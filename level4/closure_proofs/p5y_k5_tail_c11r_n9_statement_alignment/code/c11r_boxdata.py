"""C11R Repair A/F -- candidate-independent box data, the frozen selectors, and the D_lo route.

NOTHING IN THIS MODULE CHOOSES A CANDIDATE BY HAND, AND NOTHING READS AN ORIGINAL MAGNITUDE.

1. THE UPPER FAMILY IS LINEAR IN ITS PARAMETERS. For w = A - B*m with B >= 0, the reviewed box
   bound c11r_idrift.kernel_box_upper_iv evaluates, per u-panel k, max(0, A - B*m_lo_k) times the
   panel's mass upper bound. On the cover, w >= 0 forces A >= 5B, and m_lo_k <= 5 - step, so every
   max(0, .) is inactive and the box bound is exactly
        (K w).hi  =  A * S0  -  B * S1,     S0 = sum_k mass_hi_k,   S1 = sum_k m_lo_k * mass_hi_k,
   and the box margin is
        L_lo(A, B)  =  (A - B*d) - 1 - (A*S0 - B*S1)  =  A(1 - S0) + B(S1 - d) - 1.
   S0, S1 and d are properties of the BOX, the drift block and the panel count -- not of any
   candidate. One pass over the cover therefore gives the box constraints for the whole family.
   `box_upper_coeffs` replicates kernel_box_upper_iv's panel loop exactly (same u0, u1, z-range,
   image bounds and atom test); validation V11 checks the factored form against the reviewed
   function. The reviewed module is not edited.

2. THE SELECTOR (`select_upper`). Minimise A over a frozen rational grid of B, subject to every box
   constraint and A >= 5B. A_req(B) = max_boxes (1 + mu - B(S1 - d)) / (1 - S0) is a maximum of
   affine functions of B, hence convex, so an exact integer ternary search finds the grid optimum.
   The objective is the tightest certifiable bound -- the campaign's own natural objective. It
   references no original value and no comparison threshold. The selected member is then
   certified by the REVIEWED supersolution_margin_iv; the selector only chooses.

3. THE D_lo ROUTE (erratum-free, new in revision 2). D_e = d_e(atom) where d = Ghat_e h_1 is the
   MINIMAL non-negative solution of d = h_1 + Khat_e d. If u >= 0 is bounded and satisfies
        u <= h_1 + Khat_e u      on R, for every e in the block,
   then iterating gives u <= sum_{k<n} Khat^k h_1 + Khat^n u, and Khat^n u -> 0 because
   Khat_e 1 <= K_e 1 = 1 - h_1 <= 1 - h_min with h_min > 0 certified in the same pass. So u <= d,
   and D_e >= u(atom). This needs NO C_T and NO tau: the statement is UNCONDITIONAL, where the
   original's is conditional on C_T and tau. It needs one new rigorous routine, a box LOWER bound
   for Khat_e u, built as the mirror of the upper one:
     * the INTERSECTION of the alarm-free windows over the box and the drift block, in u-coordinates
       [d - C + e_hi, C - b + e_lo], so every kept panel lies inside every state's window;
     * the UNION of the atom windows over the box, [c - K, K - a], removed conservatively -- any
       panel meeting it is dropped, which can only lower a sum of non-negative terms;
     * each kept panel contributes u(m_lo) times the panel's mass LOWER bound, u being
       non-decreasing in m and non-negative.
   The family is u = alpha + beta*m, alpha, beta >= 0: the simplest non-negative, non-decreasing
   family, chosen because d is driven by the m-arm under positive drift. Richer families would
   give tighter lower bounds; that is out of scope here and recorded as such.
"""
from __future__ import annotations

import functools
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_idrift as I

X, G = I.X, I.G
K, CC = I.K, I.CC
M_MAX = F(5)          # sup of m over the cover; w = A - B m >= 0 on the cover iff A >= 5B


# ---------------------------------------------------------------------------------------------
# a Phi cache. G.Phi is a pure function of an exact rational, so memoising it cannot change a
# single bit of any result -- validation V15 checks that. It exists because adjacent u-panels share
# an endpoint, and because the certification pass revisits every endpoint the data pass computed.
# ---------------------------------------------------------------------------------------------
class PhiCache:
    def __init__(self):
        self._orig = None

    def __enter__(self):
        self._orig = G.Phi
        G.Phi = functools.lru_cache(maxsize=None)(self._orig)
        return self

    def __exit__(self, *exc):
        G.Phi = self._orig
        return False


# ---------------------------------------------------------------------------------------------
# 1. upper box coefficients -- an exact replication of kernel_box_upper_iv's panel loop
# ---------------------------------------------------------------------------------------------
def box_upper_coeffs(a: F, b: F, c: F, d: F, E: I.Blk, panels: int) -> dict:
    """S0, S1 for K_e (all panels) and for Khat_e (atom panels skipped) on one box."""
    lo_z, hi_z = c - CC, CC - a
    out = {"a": a, "b": b, "c": c, "d": d,
           "K": {"S0": F(0), "S1": F(0), "mlo_max": F(0)},
           "H": {"S0": F(0), "S1": F(0), "mlo_max": F(0), "skipped": 0}}
    if hi_z <= lo_z:
        return out
    u0_all, u1_all = lo_z + E.lo, hi_z + E.hi
    step = (u1_all - u0_all) / panels
    at_lo, at_hi = d - K, K - b
    for k in range(panels):
        u0, u1 = u0_all + step * k, u0_all + step * (k + 1)
        z_lo, z_hi = u0 - E.hi, u1 - E.lo
        m_lo = max(F(0), c - z_hi - K)
        mass = I._moments_pair(u0, u0, u1, u1, 0)[0]
        mh = mass.hi if mass.hi > 0 else F(0)
        for key in ("K", "H"):
            if key == "H" and at_lo < at_hi and z_lo >= at_lo and z_hi <= at_hi:
                out["H"]["skipped"] += 1
                continue
            out[key]["S0"] += mh
            out[key]["S1"] += m_lo * mh
            if m_lo > out[key]["mlo_max"]:
                out[key]["mlo_max"] = m_lo
    return out


def factored_upper_margin(row: dict, key: str, A: F, B: F) -> F:
    """The exact box margin A(1 - S0) + B(S1 - d) - 1 for w = A - B m."""
    r = row[key]
    return A * (1 - r["S0"]) + B * (r["S1"] - row["d"]) - 1


def select_upper(rows: list[dict], key: str, *, grid: int, b_max: F, mu: F) -> dict:
    """Minimal A on the frozen grid, over B in {0, 1/grid, ..., b_max}, meeting every box."""
    J = int(b_max * grid)

    def a_req(j: int):
        B = F(j, grid)
        best = M_MAX * B                        # w >= 0 on the cover
        for row in rows:
            r = row[key]
            den = 1 - r["S0"]
            if den <= 0:
                return None
            need = (1 + mu - B * (r["S1"] - row["d"])) / den
            if need > best:
                best = need
        return best

    lo, hi = 0, J
    while hi - lo > 2:
        m1, m2 = lo + (hi - lo) // 3, hi - (hi - lo) // 3
        f1, f2 = a_req(m1), a_req(m2)
        if f1 is None or f2 is None:
            return {"feasible": False, "reason": "a box has 1 - S0 <= 0"}
        if f1 <= f2:
            hi = m2
        else:
            lo = m1
    cands = [(a_req(j), j) for j in range(lo, hi + 1)]
    cands = [(v, j) for v, j in cands if v is not None]
    if not cands:
        return {"feasible": False, "reason": "no finite A on the grid"}
    v, j = min(cands)                            # ties -> smallest B
    A = F(-((-v * grid).__floor__()), grid)      # round A UP onto the grid
    B = F(j, grid)
    worst = min(factored_upper_margin(r, key, A, B) for r in rows)
    return {"feasible": worst >= mu, "A": A, "B": B, "A_req_exact": v,
            "min_factored_margin": worst, "grid": grid, "b_max": b_max,
            "ternary_evaluations": "integer ternary search on a convex function"}


# ---------------------------------------------------------------------------------------------
# 2. lower box coefficients and the sub-solution certificate (the D_lo route)
# ---------------------------------------------------------------------------------------------
def h1_box_lower(a: F, b: F, c: F, d: F, E: I.Blk) -> F:
    """A rigorous lower bound of h_1 = 1 - Phi(C - p + e) + Phi(m - C + e) over box and block.

    The escape probability is smallest where the alarm-free window is widest: p = a, m = c, and
    the drift pushing each end outward (e_hi at the upper end, e_lo at the lower end).
    """
    return F(1) - G.Phi(CC - a + E.hi).hi + G.Phi(c - CC + E.lo).lo


def _lower_panels(a: F, b: F, c: F, d: F, E: I.Blk, panels: int):
    """Yield (u0, u1, m_lo, kept) over the intersection window, dropping the atom union."""
    u0_all, u1_all = d - CC + E.hi, CC - b + E.lo
    if u1_all <= u0_all:
        return
    step = (u1_all - u0_all) / panels
    union_lo, union_hi = c - K, K - a            # union of [m - K, K - p] over the box
    for k in range(panels):
        u0, u1 = u0_all + step * k, u0_all + step * (k + 1)
        z_lo, z_hi = u0 - E.hi, u1 - E.lo
        meets_atom = union_lo < union_hi and z_lo < union_hi and z_hi > union_lo
        yield u0, u1, max(F(0), c - z_hi - K), not meets_atom


def box_lower_coeffs(a: F, b: F, c: F, d: F, E: I.Blk, panels: int) -> dict:
    M0, M1, dropped = F(0), F(0), 0
    for u0, u1, m_lo, kept in _lower_panels(a, b, c, d, E, panels):
        if not kept:
            dropped += 1
            continue
        mass = I._moments_pair(u0, u0, u1, u1, 0)[0]
        ml = mass.lo if mass.lo > 0 else F(0)
        M0 += ml
        M1 += m_lo * ml
    return {"a": a, "b": b, "c": c, "d": d, "M0": M0, "M1": M1,
            "h1lo": h1_box_lower(a, b, c, d, E), "dropped_atom_panels": dropped}


def kernel_box_lower_iv(u: dict, a: F, b: F, c: F, d: F, E: I.Blk, panels: int) -> F:
    """A rigorous LOWER bound of (Khat_e u)(p, m) over the box and the block, for u >= 0."""
    acc = F(0)
    for u0, u1, m_lo, kept in _lower_panels(a, b, c, d, E, panels):
        if not kept:
            continue
        z_lo, z_hi = u0 - E.hi, u1 - E.lo
        p_lo = max(F(0), a + z_lo - K)
        p_hi = max(F(0), b + z_hi - K)
        m_hi = max(F(0), d - z_lo - K)
        uv = X.poly_eval_iv(u, G.Iv(p_lo, p_hi), G.Iv(m_lo, m_hi))
        mass = I._moments_pair(u0, u0, u1, u1, 0)[0]
        if uv.lo >= 0:
            acc += uv.lo * (mass.lo if mass.lo > 0 else F(0))
        else:
            acc += uv.lo * mass.hi              # negative contribution: take the larger mass
    return acc


def subsolution_margin_iv(u: dict, E: I.Blk, depth: int, panels: int) -> dict:
    """Rigorous certificate that u <= h_1 + Khat_e u on R for every e in the block.

    Also certifies the two side conditions the sub-solution argument needs: u >= 0 on the state
    range (so that dropping panels only lowers the bound), and h_min = min h_1 > 0 (so that
    Khat_e^n u -> 0).
    """
    nonneg = X.poly_eval_iv(u, G.Iv(0, M_MAX), G.Iv(0, M_MAX)).lo >= 0
    boxes = X.cover(depth)
    mn, h_min = None, None
    for (a, b, c, d) in boxes:
        h = h1_box_lower(a, b, c, d, E)
        kl = kernel_box_lower_iv(u, a, b, c, d, E, panels)
        uh = X.poly_eval_iv(u, G.Iv(a, b), G.Iv(c, d)).hi
        m = h + kl - uh
        mn = m if mn is None or m < mn else mn
        h_min = h if h_min is None or h < h_min else h_min
    # the certifier reports its OWN kernel, as the reviewed supersolution certifier does: the lower
    # bound removes the atom union, so what this function certifies is always about Khat_e
    return {"margin_lower_bound": mn, "h_min_lower_bound": h_min, "u_nonnegative": nonneg,
            "boxes": len(boxes), "kernel": "Khat_e",
            "certified": bool(mn is not None and mn > 0 and nonneg and h_min > 0)}


def factored_lower_margin(row: dict, alpha: F, beta: F) -> F:
    """h1lo + alpha*M0 + beta*M1 - (alpha + beta*d), the box margin for u = alpha + beta m."""
    return row["h1lo"] + alpha * row["M0"] + beta * row["M1"] - (alpha + beta * row["d"])


def select_lower(rows: list[dict], *, grid: int, beta_max: F, mu: F) -> dict:
    """Maximal alpha on the frozen grid, over beta in {0, ..., beta_max}, meeting every box."""
    J = int(beta_max * grid)

    def a_max(j: int):
        beta = F(j, grid)
        best = None
        for r in rows:
            den = 1 - r["M0"]
            if den <= 0:
                return None
            v = (r["h1lo"] - mu + beta * (r["M1"] - r["d"])) / den
            best = v if best is None or v < best else best
        return best

    lo, hi = 0, J
    while hi - lo > 2:
        m1, m2 = lo + (hi - lo) // 3, hi - (hi - lo) // 3
        f1, f2 = a_max(m1), a_max(m2)
        if f1 is None or f2 is None:
            return {"feasible": False, "reason": "a box has 1 - M0 <= 0"}
        if f1 >= f2:
            hi = m2
        else:
            lo = m1
    cands = [(a_max(j), -j) for j in range(lo, hi + 1)]
    cands = [(v, nj) for v, nj in cands if v is not None]
    if not cands:
        return {"feasible": False, "reason": "no finite alpha on the grid"}
    v, nj = max(cands)                           # ties -> smallest beta
    alpha = F((v * grid).__floor__(), grid)      # round alpha DOWN onto the grid
    beta = F(-nj, grid)
    worst = min(factored_lower_margin(r, alpha, beta) for r in rows) if rows else None
    return {"feasible": bool(alpha > 0 and worst is not None and worst >= mu),
            "alpha": alpha, "beta": beta, "alpha_max_exact": v,
            "min_factored_margin": worst, "grid": grid, "beta_max": beta_max,
            "reason": None if alpha > 0 else "no positive lower bound in the family"}


# ---------------------------------------------------------------------------------------------
# 3. the pointwise stage (G10): per-state coefficients, and the per-candidate necessary check
# ---------------------------------------------------------------------------------------------
def pointwise_grid(n: int = 15) -> list[tuple[F, F]]:
    ax = [F(5 * i, n - 1) for i in range(n)]
    return [(p, m) for p in ax for m in ax if (p + m <= 4) or p == 0 or m == 0]


def pointwise_coeffs(p: F, m: F, E: I.Blk) -> dict:
    one, mm = {(0, 0): F(1)}, {(0, 1): F(1)}
    K1 = I.kernel_apply_iv(one, p, m, E)
    Km = I.kernel_apply_iv(mm, p, m, E)
    at = I.atom_contribution_iv(one, p, m, E)   # the atom piece of K_e 1; of K_e m' it is 0,
    h1 = I.alarm_prob_iv(p, m, E)               # because m' = 0 on the atom window
    return {"p": p, "m": m, "K1": (K1.lo, K1.hi), "Km": (Km.lo, Km.hi),
            "atom1": (at.lo, at.hi), "h1": (h1.lo, h1.hi)}


def pointwise_upper_hi(c: dict, key: str, A: F, B: F) -> F:
    """An UPPER bound of L = w - 1 - K w at one state, for w = A - B m. Negative refutes w."""
    k1lo = c["K1"][0] - (c["atom1"][1] if key == "H" else 0)
    return A * (1 - k1lo) + B * (c["Km"][1] - c["m"]) - 1


def pointwise_lower_hi(c: dict, alpha: F, beta: F) -> F:
    """An UPPER bound of h_1 + Khat u - u at one state. Negative refutes u as a sub-solution."""
    khat1_hi = c["K1"][1] - c["atom1"][0]
    return c["h1"][1] + alpha * khat1_hi + beta * c["Km"][1] - (alpha + beta * c["m"])
