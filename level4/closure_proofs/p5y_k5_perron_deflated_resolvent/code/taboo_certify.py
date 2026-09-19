"""Certified OPERATOR-ONLY constants for theorem AD (THEOREM_AD.md section 8).

No source S_r, no candidate of any F / D / H object, no K1 record and no value of R is formed. The objects are the kernel
K_e itself, its atom split K_e = Khat_e + k_a (x) delta_a (the frozen "origin" piece of _kernel_polynomials), the one-step
alarm probability h_1 = 1 - K_e 1 and its e-derivatives (closed forms of the operator), and

    w     polynomial supersolution  w >= 1 + Khat_e w  on X, uniformly on an e-block     (Lemma T: C_T, tau_a)
    d     = Ghat h_1       (D = d(a) = P_a(tau < T_a))
    d'    = Ghat (Khat' d + h_1')          (D' = d'(a))
    d''   = Ghat (Khat'' d + 2 Khat' d' + h_1'')   (D'' = d''(a))

Arithmetic: Arb at 256 bits with the frozen Pair kernel (_kernel_polynomials, order-120 phi series), the frozen truncation
allowances Z_RANGE * sup * (N+1)^i * eps_z (doubled for the removed origin piece, as in the adopted R3 C_o0 certificate),
the frozen closed forms and allowances of cusum_layer2, and the frozen Bernstein range bound on the reachable cover.
Candidates are degree-12 exact-dyadic Chebyshev payloads (frozen L1.dyadic_candidate) from a float proposal; the float
is never trusted.

    python -B code/taboo_certify.py block --lo NUM/DEN --hi NUM/DEN --alpha 27/20 --out B.json
    python -B code/taboo_certify.py cell --index K --tau T --C C --out CELL.json
    python -B code/taboo_certify.py verify-block B.json | verify-cell CELL.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = NS.parents[0]
R3 = CP / "p5y_k5_cusum_order3_r3_infrastructure/code"
for _p in (str(R3), str(CP / "p5y_k5_cusum_order3_real_producer/code"), str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5  # noqa: E402,F401  (frozen science import bootstrap)

import numpy as np  # noqa: E402
from flint import arb  # noqa: E402

import cusum_layer1 as L1  # noqa: E402
from cusum_layer2 import REWARD_RADIUS, Z_RANGE  # noqa: E402  (sets the RA path, as in R3)
import opnorms  # noqa: E402
import ra_certifier as RA  # noqa: E402
from fast_range import max_abs_on_reachable_fast  # noqa: E402
from intervals import exact, tight_upper, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_eval, bi_mul, bi_scale, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_piece, _kernel_polynomials  # noqa: E402
import resolvent_certificate as R3C  # noqa: E402  (frozen R3: bary_rows, min_max_on_reachable)

K_, C_ = 0.5, 5.5
BITS = 256
ORDER = RA.TAYLOR_N
SCHEMA_BLOCK = "rebaseguard.p5y.k5.perron-deflation.taboo-block-certificate.v1"
SCHEMA_CELL = "rebaseguard.p5y.k5.perron-deflation.taboo-cell-certificate.v1"


def _beta_alpha():
    beta = bi_add({(0, 1): arb(1)}, {(0, 0): -arb(1) / arb(2)})           # m - 1/2
    alpha = bi_add({(1, 0): -arb(1)}, {(0, 0): arb(1) / arb(2)})           # 1/2 - p
    return beta, alpha


def _q(x) -> F:
    q = x.fmpq() if hasattr(x, "fmpq") else x
    return F(int(q.p), int(q.q))


def upper(x: arb) -> F:
    return _q(x.upper())


def lower(x: arb) -> F:
    return _q(x.lower())


# ------------------------------------------------------------------------------------------------ float proposals
def float_taboo_kernels(drift: float, orders=(0, 1, 2), degree: int = 12):
    """Khat_i on a tensor Chebyshev grid of the given degree (R3 cut points; atom window removed), weights
    phi^(i)(z+e). Float proposal only."""
    n = degree + 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    w = (-1.0) ** np.arange(n)
    w[[0, -1]] *= 0.5
    gn, gw = np.polynomial.legendre.leggauss(L1.QUADRATURE)
    mats = {i: np.zeros((n * n, n * n)) for i in orders}
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            ell, upp = m - C_, C_ - p
            beta, alpha = m - K_, K_ - p
            cuts = sorted({ell, upp} | ({beta, alpha} if beta < alpha else set()))
            rows = {o: np.zeros((n, n)) for o in orders}
            for a, b in zip(cuts[:-1], cuts[1:]):
                if beta < alpha and a >= beta - 1e-15 and b <= alpha + 1e-15:
                    continue
                mid, rad = 0.5 * (a + b), 0.5 * (b - a)
                z = mid + rad * gn
                y = z + drift
                phi = np.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)
                wp = R3C.bary_rows(np.maximum(0.0, p + z - K_), nodes, w)
                wm = R3C.bary_rows(np.maximum(0.0, m - z - K_), nodes, w)
                for o in orders:
                    he = {0: 1.0, 1: -y, 2: y * y - 1.0}[o]           # phi^(o)(y) = (-1)^o He_o(y) phi(y)
                    rows[o] += np.einsum("q,qa,qb->ab", rad * gw * phi * he, wp, wm)
            for o in orders:
                mats[o][i * n + j] = rows[o].ravel()
    return mats, nodes, n


def float_h1(drift: float, nodes):
    """h_1, h_1' = -S_0, h_1'' = -S_0' at the grid nodes (closed forms)."""
    Phi = lambda t: 0.5 * (1.0 + math.erf(t / math.sqrt(2.0)))
    ph = lambda t: math.exp(-0.5 * t * t) / math.sqrt(2 * math.pi)
    n = len(nodes)
    h = {k: np.zeros(n * n) for k in range(3)}
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            au, al = C_ - p + drift, m - C_ + drift
            h[0][i * n + j] = 1.0 - Phi(au) + Phi(al)
            s0 = ph(au) - ph(al)
            s1 = -au * ph(au) + al * ph(al)
            h[1][i * n + j] = -s0
            h[2][i * n + j] = -s1
    return h


# ------------------------------------------------------------------------------------------------ Khat enclosures
class Ops:
    """Frozen Pair enclosures of Khat_i f at the exact drift e, i = 0, 1, 2 (origin piece removed from the low branch)."""

    def __init__(self, e: F):
        self.e = exact(e)
        self.b = [RA.phi_taylor_coefficients(ORDER, self.e)]
        for _ in range(3):
            self.b.append(RA.derivative_coefficients(self.b[-1]))
        self.eps_z = RA.taylor_remainder(ORDER, exact(F(11, 2)))
        self.beta, self.alpha = _beta_alpha()
        self.calls = 0

    def eps_zi(self, i: int) -> arb:
        return (arb(ORDER + 1) ** i) * self.eps_z

    def khat(self, poly, i: int, full: bool = False):
        """Khat_i (origin piece removed) or, with full=True, the frozen K_i itself."""
        self.calls += 1
        lo, hi = _kernel_polynomials(poly, self.b[i], z_weight=0)
        if full:
            return lo, hi
        origin = _kernel_piece(poly, "origin", self.beta, self.alpha, self.b[i], z_weight=0)
        return bi_add(lo, bi_scale(origin, -arb(1))), hi

    def trunc(self, sup: arb, i: int) -> arb:
        """Allowance of one Khat_i application: the Pair kernel's own plus the removed origin piece's (R3 rule).
        Also used, conservatively, for the full K_i."""
        return arb(2) * Z_RANGE * sup * self.eps_zi(i)


def pair_sub(a, b):
    return bi_add(a[0], bi_scale(b[0], -arb(1))), bi_add(a[1], bi_scale(b[1], -arb(1)))


def pair_scale(a, c):
    return bi_scale(a[0], c), bi_scale(a[1], c)


def pair_const(poly):
    return poly, poly


# ------------------------------------------------------------------------------------------------ block supersolution
def float_full_kernel(drift: float, degree: int = 12):
    """K_e on the grid with the same cut points, atom window INCLUDED (float proposal only)."""
    mats, nodes, n = float_taboo_kernels(drift, orders=(0,), degree=degree)
    ka = np.zeros(n * n)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            beta, alpha = m - K_, K_ - p
            if beta < alpha:
                ka[i * n + j] = 0.5 * (math.erf((alpha + drift) / math.sqrt(2)) - math.erf((beta + drift) / math.sqrt(2)))
    K = mats[0].copy()
    K[:, 0] += ka                                   # node (0,0) is index 0: K = Khat + k_a (x) delta_a
    return K, n


def block_proposal(ec: float, alpha_s: float, beta_s: float, degree: int = 12, full: bool = False):
    if full:
        M, n = float_full_kernel(ec, degree)
    else:
        mats, nodes, n = float_taboo_kernels(ec, orders=(0,), degree=degree)
        M = mats[0]
    g = np.linalg.solve(np.eye(n * n) - M, np.ones(n * n))
    return L1.dyadic_candidate(alpha_s * g + beta_s, n), float(g.max())


def certify_block(e_lo: F, e_hi: F, payload: dict, *, depth: int = 2, full: bool = False) -> dict:
    """Lemma T on E = [e_lo, e_hi] with the affine-in-(e - ec) expansion checked at both ends.
    full=False: w >= 1 + Khat_e w (taboo: C_T = sup w, tau = w(a)).
    full=True:  w >= 1 + K_e w (whole kernel: E_x[tau] <= w(x); Abar = w(a) bounds the ARL at the atom)."""
    if not (F(0) <= e_lo < e_hi):
        raise ValueError("block must satisfy 0 <= e_lo < e_hi")
    ec, delta = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
    t0 = time.process_time()
    with workprec(BITS):
        ops = Ops(ec)
        w = chebyshev_payload_to_power(payload)
        sup_w = _chebyshev_sup(payload)
        k0 = ops.khat(w, 0, full)
        k1 = ops.khat(w, 1, full)
        d = exact(delta)
        kappa2 = opnorms.kernel_norm(2)
        allow = (ops.trunc(sup_w, 0) + d * ops.trunc(sup_w, 1)
                 + d * d / arb(2) * kappa2 * sup_w)
        one = {(0, 0): arb(1) + allow}
        mins = {}
        for s in (1, -1):
            L = pair_sub(pair_sub(pair_const(w), k0), pair_scale(k1, arb(s) * d))
            L = pair_sub(L, pair_const(one))
            mn, _, npatch = R3C.min_max_on_reachable(L[0], L[1], depth)
            mins[s] = mn
        wmin, wmax, _ = R3C.min_max_on_reachable(w, w, depth)
        wa = bi_eval(w, arb(0), arb(0))
        margin = mins[1] if mins[1] < mins[-1] else mins[-1]
        ok = bool(margin > 0) and bool(wmin >= 0)
        return {"schema": SCHEMA_BLOCK, "kind": "full" if full else "taboo",
                "e_lo": str(e_lo), "e_hi": str(e_hi), "ec": str(ec), "delta": str(delta),
                "depth": depth, "bits": BITS, "patches": npatch, "certified": ok,
                "margin_lower_bound": str(_q(margin)), "w_min_lower_bound": str(_q(wmin)),
                "C_T": str(upper(wmax)), "tau": str(upper(wa)), "allowance_upper": str(upper(allow)),
                "sup_w_chebyshev": str(upper(sup_w)), "kernel_calls": ops.calls,
                "cpu_seconds": time.process_time() - t0,
                "statement": ("for every e in [e_lo, e_hi]: w >= 1 + K_e w on X, hence E_x[tau] <= w(x); "
                              "Abar := tau field = w(a) >= E_a[tau]" if full else
                              "for every e in [e_lo, e_hi]: w >= 1 + Khat_e w on X, hence ||Ghat_e|| <= C_T and "
                              "(Ghat_e 1)(a) <= tau (Lemma T)")}


def block_artifact(e_lo: F, e_hi: F, alpha_s: F, beta_s: F, depth: int, degree: int = 12,
                   full: bool = False) -> dict:
    ec = float((e_lo + e_hi) / 2)
    payload, gmax = block_proposal(ec, float(alpha_s), float(beta_s), degree, full)
    cert = certify_block(e_lo, e_hi, payload, depth=depth, full=full)
    cert.update({"proposal": {"alpha": str(alpha_s), "beta": str(beta_s), "float_sup_taboo_grid": gmax},
                 "payload": payload})
    return cert


def verify_block(art: dict) -> dict:
    r = certify_block(F(art["e_lo"]), F(art["e_hi"]), art["payload"], depth=art["depth"],
                      full=art.get("kind") == "full")
    keys = ("certified", "margin_lower_bound", "w_min_lower_bound", "C_T", "tau", "allowance_upper")
    return {"identical": all(r[k] == art[k] for k in keys), "certified": r["certified"],
            "recomputed": {k: r[k] for k in keys}}


# ------------------------------------------------------------------------------------------------ taboo objects d, d', d''
def closed_h1(ops: Ops, e: F, e_max: F):
    """h_1^(k) closed forms (cusum_layer2._closed_forms) and their truncation allowances."""
    eps_r = RA.taylor_remainder(ORDER, exact(REWARD_RADIUS))
    (phi_u, cdf_u), (phi_l, cdf_l), arg_u, arg_l = RA._recentred_sites(ORDER, ops.e)
    one = {(0, 0): arb(1)}
    s0 = bi_add(phi_u, bi_scale(phi_l, -arb(1)))
    s1 = bi_add(bi_scale(bi_mul(arg_u, phi_u), -arb(1)), bi_mul(arg_l, phi_l))
    h1 = bi_add(one, bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))
    A = arb(11) / arb(2) + exact(e_max)
    allow = {0: arb(2) * exact(REWARD_RADIUS) * eps_r, 1: arb(2) * eps_r, 2: arb(2) * A * eps_r}
    return {0: h1, 1: bi_scale(s0, -arb(1)), 2: bi_scale(s1, -arb(1))}, allow


def taboo_proposals(e0: float, degree: int = 12):
    mats, nodes, n = float_taboo_kernels(e0, orders=(0, 1, 2), degree=degree)
    h = float_h1(e0, nodes)
    A = np.eye(n * n) - mats[0]
    d0 = np.linalg.solve(A, h[0])
    d1 = np.linalg.solve(A, mats[1] @ d0 + h[1])
    d2 = np.linalg.solve(A, mats[2] @ d0 + 2 * mats[1] @ d1 + h[2])
    return {k: L1.dyadic_candidate(v, n) for k, v in (("d0", d0), ("d1", d1), ("d2", d2))}


def certify_cell(e0: F, rho: F, tau: F, C: F, payloads: dict, *, depth: int = 0) -> dict:
    """Point values of D, D' at e0 and uniform bounds of D, D', D'' on [e0 - rho, e0 + rho] (tame taboo propagation)."""
    t0 = time.process_time()
    with workprec(BITS):
        ops = Ops(e0)
        e_max = abs(e0) + rho
        hk, hallow = closed_h1(ops, e0, e_max)
        kap = {i: opnorms.kernel_norm(i) for i in range(4)}
        sup_h = {k: opnorms.sup_source_derivative(k - 1) if k >= 1 else arb(1) for k in range(4)}
        P = {k: chebyshev_payload_to_power(payloads[k]) for k in ("d0", "d1", "d2")}
        S = {k: _chebyshev_sup(payloads[k]) for k in ("d0", "d1", "d2")}

        def rng(pair):
            v, _ = max_abs_on_reachable_fast(pair[0], pair[1], subdivision_depth=depth)
            return tight_upper(v)

        # d:   d - Khat d - h_1
        r0 = pair_sub(pair_sub(pair_const(P["d0"]), ops.khat(P["d0"], 0)), pair_const(hk[0]))
        x0 = ops.trunc(S["d0"], 0) + hallow[0]
        env0 = kap[1] * S["d0"] + sup_h[1]
        # d':  d' - Khat d' - Khat' d - h_1'
        r1 = pair_sub(pair_sub(pair_sub(pair_const(P["d1"]), ops.khat(P["d1"], 0)), ops.khat(P["d0"], 1)),
                      pair_const(hk[1]))
        x1 = ops.trunc(S["d1"], 0) + ops.trunc(S["d0"], 1) + hallow[1]
        env1 = kap[1] * S["d1"] + kap[2] * S["d0"] + sup_h[2]
        # d'': d'' - Khat d'' - 2 Khat' d' - Khat'' d - h_1''
        r2 = pair_sub(pair_sub(pair_sub(pair_sub(pair_const(P["d2"]), ops.khat(P["d2"], 0)),
                                        pair_scale(ops.khat(P["d1"], 1), arb(2))), ops.khat(P["d0"], 2)),
                      pair_const(hk[2]))
        x2 = ops.trunc(S["d2"], 0) + arb(2) * ops.trunc(S["d1"], 1) + ops.trunc(S["d0"], 2) + hallow[2]
        env2 = kap[1] * S["d2"] + arb(2) * kap[2] * S["d1"] + kap[3] * S["d0"] + sup_h[3]
        lam_mid = {0: tight_upper(rng(r0) + x0), 1: tight_upper(rng(r1) + x1), 2: tight_upper(rng(r2) + x2)}
        r_ = exact(rho)
        lam_cell = {0: tight_upper(lam_mid[0] + r_ * env0), 1: tight_upper(lam_mid[1] + r_ * env1),
                    2: tight_upper(lam_mid[2] + r_ * env2)}
        T, Cc = exact(tau), exact(C)

        def prop(lam):
            n0 = Cc * lam[0]
            p0 = T * lam[0]
            n1 = Cc * (lam[1] + kap[1] * n0)
            p1 = T * (lam[1] + kap[1] * n0)
            p2 = T * (lam[2] + arb(2) * kap[1] * n1 + kap[2] * n0)
            return p0, p1, p2
        pm = prop(lam_mid)
        pc = prop(lam_cell)
        dv = {k: bi_eval(P[k], arb(0), arb(0)) for k in ("d0", "d1", "d2")}
        D_mid_lo = dv["d0"] - pm[0]
        D1_mid = dv["d1"].abs_upper() + pm[1]
        D2_cell = dv["d2"].abs_upper() + pc[2]
        D1_cell_a = dv["d1"].abs_upper() + pc[1]
        D1_cell_b = D1_mid + r_ * D2_cell
        D1_cell = D1_cell_a if D1_cell_a.upper() < D1_cell_b.upper() else D1_cell_b
        D_lo_cell = D_mid_lo - r_ * D1_cell
        return {"schema": SCHEMA_CELL, "e0": str(e0), "rho": str(rho), "tau": str(tau), "C_T": str(C),
                "depth": depth, "bits": BITS,
                "lambda_mid": {str(k): str(upper(v)) for k, v in lam_mid.items()},
                "lambda_cell": {str(k): str(upper(v)) for k, v in lam_cell.items()},
                "candidate_at_atom": {k: [str(lower(v)), str(upper(v))] for k, v in dv.items()},
                "D_lo": str(lower(D_lo_cell)), "D1": str(upper(D1_cell)), "D2": str(upper(D2_cell)),
                "D_mid": [str(lower(D_mid_lo)), str(upper(dv["d0"] + pm[0]))],
                "D1_mid_abs_upper": str(upper(D1_mid)),
                "certified": bool(D_lo_cell > 0),
                "kernel_calls": ops.calls, "cpu_seconds": time.process_time() - t0,
                "statement": "for every e in [e0 - rho, e0 + rho]: D_e >= D_lo, |D_e'| <= D1, |D_e''| <= D2 "
                             "(given ||Ghat_e|| <= C_T and (Ghat_e 1)(a) <= tau on the same set)"}


def cell_artifact(e0: F, rho: F, tau: F, C: F, depth: int = 0, degree: int = 12) -> dict:
    payloads = taboo_proposals(float(e0), degree)
    cert = certify_cell(e0, rho, tau, C, payloads, depth=depth)
    cert["payloads"] = payloads
    return cert


def verify_cell(art: dict) -> dict:
    r = certify_cell(F(art["e0"]), F(art["rho"]), F(art["tau"]), F(art["C_T"]), art["payloads"], depth=art["depth"])
    keys = ("certified", "D_lo", "D1", "D2", "D_mid", "lambda_mid", "lambda_cell")
    return {"identical": all(r[k] == art[k] for k in keys), "certified": r["certified"],
            "recomputed": {k: r[k] for k in keys}}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("block")
    b.add_argument("--lo", required=True)
    b.add_argument("--hi", required=True)
    b.add_argument("--alpha", default="27/20")
    b.add_argument("--beta", default="0")
    b.add_argument("--depth", type=int, default=2)
    b.add_argument("--degree", type=int, default=12)
    b.add_argument("--full", action="store_true")
    b.add_argument("--out", required=True)
    c = sub.add_parser("cell")
    c.add_argument("--e0", required=True)
    c.add_argument("--rho", required=True)
    c.add_argument("--tau", required=True)
    c.add_argument("--C", required=True)
    c.add_argument("--degree", type=int, default=12)
    c.add_argument("--out", required=True)
    for name in ("verify-block", "verify-cell"):
        v = sub.add_parser(name)
        v.add_argument("path")
    a = ap.parse_args()
    if a.cmd == "block":
        art = block_artifact(F(a.lo), F(a.hi), F(a.alpha), F(a.beta), a.depth, a.degree, a.full)
        Path(a.out).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
        print(json.dumps({k: art[k] for k in ("e_lo", "e_hi", "certified", "margin_lower_bound", "C_T", "tau",
                                              "cpu_seconds")}))
    elif a.cmd == "cell":
        art = cell_artifact(F(a.e0), F(a.rho), F(a.tau), F(a.C), degree=a.degree)
        Path(a.out).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
        print(json.dumps({k: art[k] for k in ("e0", "certified", "D_lo", "D1", "D2", "D_mid", "lambda_mid",
                                              "lambda_cell", "cpu_seconds")}))
    elif a.cmd == "verify-block":
        print(json.dumps(verify_block(json.loads(Path(a.path).read_text())), indent=1))
    else:
        print(json.dumps(verify_cell(json.loads(Path(a.path).read_text())), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
