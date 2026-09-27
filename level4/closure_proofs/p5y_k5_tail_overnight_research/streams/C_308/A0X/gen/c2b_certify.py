"""C2b driver: proposal -> family -> fine (alpha, beta) selection -> EXACT certificate, pointwise or block-uniform.

Declared procedure (STRATEGY.md s2-s6):
  proposal  g = Nystrom value function on mesh h = 1/N at the block ends (nodal max over {e_lo, e_hi}); 'whole'
            uses V_h (ARL), 'taboo' uses t_h (taboo time).  Rounded to dyadics 2^-Q.
  family    P1 on the same mesh (rung ladder N in NS_LADDER); comparator rung F0 = affine in m (w = beta - alpha m).
  scaling   w = alpha g + beta, alpha on the fine ladder 1 + k 2^-ALPHA_BITS (k = 0..2^ALPHA_BITS), beta = smallest
            dyadic (2^-(Q+ALPHA_BITS)) satisfying the linearised per-vertex constraints; alpha chosen to minimise
            w(a) (convex in alpha: ternary search on the ladder index).  Selection is UNTRUSTED (floats).
  certify   c2b_exact.certify on the final nodal vector (exact).  If it fails, k -> k+1 (at most BUMP_MAX times).
"""
from __future__ import annotations

import time
from fractions import Fraction as F

import c2b_common as CM
import c2b_exact as EX
import c2b_float as FL

Q = 40
ALPHA_BITS = 12
BUMP_MAX = 64


def _dyadic(Wf, q=Q):
    return [[int(round(v * (1 << q))) for v in col] for col in Wf]


def prepare(S, g_int, full):
    """Per-vertex linear data: for every (cell, slab, vertex, e-offset):  alpha*u + beta*v >= 1  with
    u = (g - K g_hi - err_g) and v = (1 - K1_hi - err_1), as floats (selection only)."""
    one = [[1 << Q for _ in range(c)] for c in S.mesh.cols]
    Mg = {jj: EX.kernel_nodes(S, g_int, jj, full, upper=True) for jj in range(S.J + 1)}
    M1 = {jj: EX.kernel_nodes(S, one, jj, full, upper=True) for jj in range(S.J + 1)}
    Hg = EX.hessian_bounds(S, g_int, full)
    H1 = EX.hessian_bounds(S, one, full)
    sc = 2.0 ** -(EX.P + Q)
    cons = []
    for (rg, r1) in zip(Hg, H1):
        cell, jj, je = rg[0], rg[1], rg[2]
        eg, e1 = rg[6], r1[6]
        for v in cell[8]:
            for t in ((0, 1) if je else (0,)):
                x = jj + t
                gv = g_int[v[0]][v[1]] << EX.P
                u = (gv - Mg[x][v] - eg) * sc
                w = ((1 << (EX.P + Q)) - M1[x][v] - e1) * sc
                cons.append((u, w))
    # deduplicate nearly identical constraints cheaply
    return sorted(set(cons))


def beta_min(cons, alpha):
    lo, hi = 0.0, float("inf")
    for (u, v) in cons:
        r = 1.0 - alpha * u
        if v > 0:
            lo = max(lo, r / v)
        elif v < 0:
            hi = min(hi, r / v)
        elif r > 0:
            return None
    return lo if lo <= hi else None


def select(cons, g_atom, kmax=1 << ALPHA_BITS):
    """Ternary search over the ladder index k (alpha = 1 + k 2^-ALPHA_BITS) of f(k) = alpha g(a) + beta_min."""
    def f(k):
        a = 1.0 + k / (1 << ALPHA_BITS)
        b = beta_min(cons, a)
        return float("inf") if b is None else a * g_atom + b

    # coarse scan for a feasible index, then ternary on the (convex) sequence
    step = 64
    grid = list(range(0, kmax + 1, step))
    vals = [f(k) for k in grid]
    kbest = grid[min(range(len(grid)), key=lambda r: vals[r])]
    if vals[grid.index(kbest)] == float("inf"):
        return None
    lo, hi = max(0, kbest - step), min(kmax, kbest + step)
    while hi - lo > 2:
        m1, m2 = lo + (hi - lo) // 3, hi - (hi - lo) // 3
        if f(m1) <= f(m2):
            hi = m2
        else:
            lo = m1
    return min(range(lo, hi + 1), key=f)


def build_w(g_int, k, cons):
    a_num = (1 << ALPHA_BITS) + k
    alpha = a_num / (1 << ALPHA_BITS)
    b = beta_min(cons, alpha) or 0.0
    b_num = int(b * (1 << (Q + ALPHA_BITS))) + 1 if b > 0 else 0
    W = [[a_num * x + b_num for x in col] for col in g_int]
    return W, F(a_num, 1 << ALPHA_BITS), F(b_num, 1 << (Q + ALPHA_BITS))


def proposal(N, e_lo, e_hi, kind):
    key = "V" if kind == "whole" else "t"
    sols = [FL.FloatKernel(N, float(e)).solve_taboo() for e in sorted({F(e_lo), F(e_hi)})]
    g = [[max(s[key][i][jx] for s in sols) for jx in range(len(sols[0][key][i]))] for i in range(len(sols[0][key]))]
    return g, sols


def run(N, e_lo, e_hi=None, kind="whole", family="P1"):
    """Full pipeline.  kind in {'whole', 'taboo'}; family in {'P1', 'F0_affine_m'}."""
    e_lo = F(e_lo)
    e_hi = e_lo if e_hi is None else F(e_hi)
    CM.guard(e_lo, e_hi)
    full = kind == "whole"
    t0 = time.process_time()
    S = EX.Setup(N, e_lo, e_hi)
    t_setup = time.process_time() - t0
    g, sols = proposal(N, e_lo, e_hi, kind)
    t_prop = time.process_time() - t0 - t_setup
    if family == "F0_affine_m":
        g = [[-(j / N) for j in range(S.mesh.cols[i])] for i in range(len(S.mesh.cols))]
    g_int = _dyadic(g)
    cons = prepare(S, g_int, full)
    g_atom = g_int[0][0] / (1 << Q)
    if family == "F0_affine_m":
        k = _select_affine(cons)
    else:
        k = select(cons, g_atom)
    t_sel = time.process_time() - t0 - t_setup - t_prop
    res = None
    bumps = 0
    while k is not None and bumps <= BUMP_MAX:
        if family == "F0_affine_m":
            W, alpha, beta = _build_affine(g_int, k, cons)
        else:
            W, alpha, beta = build_w(g_int, k, cons)
        res = EX.certify(S, W, Q + ALPHA_BITS, full)
        if res["certified"]:
            break
        k += 1
        bumps += 1
    t_all = time.process_time() - t0
    float_est = {"Lambda": [s["Lambda"] for s in sols], "tau_a": [s["tau_a"] for s in sols],
                 "C_T": [s["C_T"] for s in sols]}
    return {
        "N": N, "e_lo": str(e_lo), "e_hi": str(e_hi), "kind": kind, "family": family,
        "alpha": str(alpha) if res else None, "beta": str(beta) if res else None,
        "alpha_float": float(alpha) if res else None, "beta_float": float(beta) if res else None,
        "ladder_index": k, "bumps": bumps, "certificate": res,
        "nystrom_same_mesh": float_est,
        "cpu_seconds": {"setup_gauss": t_setup, "proposal": t_prop, "selection": t_sel, "total": t_all},
    }


# ---------------------------------------------------------------- comparator rung F0: w = beta - alpha m
def _select_affine(cons, kmax=1 << 14):
    """alpha = k 2^-8 (slope B), beta = A minimal; minimise A (C11R-style selector, but exact-certified here)."""
    best, kb = float("inf"), None
    for k in range(0, 1 << 11, 4):
        a = k / 256.0
        b = beta_min(cons, a)
        if b is not None and b < best:
            best, kb = b, k
    if kb is None:
        return None
    lo, hi = max(0, kb - 4), kb + 4
    return min(range(lo, hi + 1), key=lambda k: (beta_min(cons, k / 256.0) or float("inf")))


def _build_affine(g_int, k, cons):
    alpha = k / 256.0
    b = beta_min(cons, alpha) or 0.0
    b_num = int(b * (1 << (Q + ALPHA_BITS))) + 1
    # g_int = -m 2^Q; w = alpha g + beta at scale 2^-(Q+ALPHA_BITS); alpha = k/256 -> k * 2^(ALPHA_BITS-8)
    W = [[k * (1 << (ALPHA_BITS - 8)) * x + b_num for x in col] for col in g_int]
    return W, F(k, 256), F(b_num, 1 << (Q + ALPHA_BITS))


# ---------------------------------------------------------------- declared rung ladder and stopping rule (STRATEGY s6)
NS_LADDER = (10, 20, 40, 80)
GAMMA = F(1, 400)          # stop when the certified value improves by less than 0.25 %
BUDGET_CPU = 1200.0        # per drift or block


def ladder_decision(rungs):
    """rungs: list of (N, certified_value or None, cpu_seconds) in ladder order.  Returns (stop_after_N, reason,
    best_value).  Pure function of the rung sequence: no truth, no target quantity."""
    best, prev = None, None
    for idx, (N, val, cpu) in enumerate(rungs):
        if val is not None:
            best = val if best is None else min(best, val)
        if prev is not None and val is not None and (prev - val) < GAMMA * prev:
            return N, "improvement < gamma", best
        if idx + 1 < len(NS_LADDER) and cpu * 8 > BUDGET_CPU:
            return N, "projected next-rung cost > budget", best
        prev = val if val is not None else prev
    return rungs[-1][0], "ladder exhausted or rungs not yet run", best


def run_ladder(e_lo, e_hi=None, kind="whole"):
    rungs, out = [], []
    for N in NS_LADDER:
        r = run(N, e_lo, e_hi, kind, "P1")
        c = r["certificate"]
        val = F(c["w_atom"]) if (c and c["certified"]) else None
        rungs.append((N, val, r["cpu_seconds"]["total"]))
        out.append(r)
        stop_N, reason, best = ladder_decision(rungs)
        if stop_N == N and reason != "ladder exhausted or rungs not yet run":
            break
    return {"rungs": out, "stop_after_N": stop_N, "reason": reason, "best": str(best) if best else None}
