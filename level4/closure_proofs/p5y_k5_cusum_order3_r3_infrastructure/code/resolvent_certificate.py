"""R3 Part A/B: certified sigma-odd and whole-space resolvent bounds of the CUSUM kernel at drift e = 0.

Operator information only: K_0 (weight phi) on bounded functions on the reachable CUSUM state set R. No source term,
DAG object, K1 record or R''' value.

THEOREM (odd). Let T0 = first t >= 1 with X_t = (0,0), tau the alarm time. For every sigma-odd bounded f and x in R,
    |((I - K_0)^-1 f)(x)| <= ||f|| * E_x[tau ^ T0].
Proof: u = (I-K_0)^-1 f = E_x sum_(t<tau) f(X_t) is sigma-odd (sigma commutes with K_0), hence u(0,0) = 0 since (0,0)
is sigma-fixed; the strong Markov property at T0 gives u(x) = E_x sum_(t < tau ^ T0) f(X_t) + E_x[u(0,0); T0 < tau].

THEOREM (supersolution). Let Khat = K_0 with (0,0) absorbing (the "origin" atom of the frozen kernel removed). If a
bounded w >= 0 on R satisfies w >= 1 + Khat w on R, then E_x[tau ^ T0] = sum_j Khat^j 1 <= w (induction:
sum_(j<n) Khat^j 1 <= w for all n, since Khat is positive). Hence C_o0 := sup_R w. The same with K_0 (no atom
removal) gives C_e0 := sup_R w_e >= sup_x E_x[tau] = ||(I - K_0)^-1||, a bound for EVERY function, in particular even.

CERTIFICATION. w is an exact dyadic degree-12 Chebyshev polynomial (float proposal). On R, with the frozen Pair kernel
enclosures at e = 0 (order-120 phi series, frozen truncation allowance Z_RANGE * sup|w| * eps_z):
    L := w - 1 - (Khat w)_poly - allowance   (low branch minus the frozen "origin" piece w(0,0) * int_beta^alpha phi)
    certified min_R L >= 0 and min_R w >= 0 (Bernstein coefficients on the frozen reachable cover, subdivision),
    C := certified max_R w (Bernstein).
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_real_producer/code"),
           str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5  # noqa: E402,F401

import numpy as np  # noqa: E402
from flint import arb  # noqa: E402

import cusum_layer1 as L1  # noqa: E402
from cusum_layer2 import Z_RANGE  # noqa: E402  (sets the RA path)
import ra_certifier as RA  # noqa: E402
from fast_range import affine_to_unit_square_fast  # noqa: E402
from intervals import exact, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_scale, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import (_chebyshev_sup, _kernel_piece, _kernel_polynomials,  # noqa: E402
                                          _parameterize_triangle, _power_to_bernstein, _split_patch)

K_, C_ = 0.5, 5.5


# ------------------------------------------------------------------ certified Bernstein min / max on the reachable cover
def _patches(coeffs, depth):
    patches = [coeffs]
    for _ in range(depth):
        nxt = []
        for patch in patches:
            left, right = _split_patch(patch, 0)
            for half in (left, right):
                bottom, top = _split_patch(half, 1)
                nxt.extend((bottom, top))
        patches = nxt
    return patches


def reachable_pieces(lo_poly, hi_poly):
    low = affine_to_unit_square_fast(_parameterize_triangle(lo_poly), arb(0), arb(1), arb(0), arb(1))
    high = affine_to_unit_square_fast(_parameterize_triangle(hi_poly), arb(1), arb(4), arb(0), arb(1))
    plus = {(i, 0): c for (i, j), c in hi_poly.items() if j == 0}
    minus = {(0, j): c for (i, j), c in hi_poly.items() if i == 0}
    return [_power_to_bernstein(low), _power_to_bernstein(high),
            _power_to_bernstein(affine_to_unit_square_fast(plus, arb(4), arb(5), arb(0), arb(1))),
            _power_to_bernstein(affine_to_unit_square_fast(minus, arb(0), arb(1), arb(4), arb(5)))]


def min_max_on_reachable(lo_poly, hi_poly, depth):
    """Certified [lower bound of min, upper bound of max] of the Pair function on R (Bernstein enclosure)."""
    mn, mx, count = None, None, 0
    for coeffs in reachable_pieces(lo_poly, hi_poly):
        for patch in _patches(coeffs, depth):
            count += 1
            for row in patch:
                for c in row:
                    lo_c, hi_c = c.lower(), c.upper()
                    mn = lo_c if mn is None or lo_c < mn else mn
                    mx = hi_c if mx is None or hi_c > mx else mx
    return mn, mx, count


# ------------------------------------------------------------------ float proposal on the frozen grid
def bary_rows(values, nodes, w):
    d = values[:, None] - nodes[None, :]
    ex = np.abs(d) < 2e-14
    d = np.where(ex, 1.0, d)
    t = w[None, :] / d
    t = t / t.sum(axis=1, keepdims=True)
    hit = ex.any(axis=1)
    if hit.any():
        t[hit] = ex[hit].astype(float)
    return t


def kernel_matrices():
    n = L1.DEGREE + 1
    x = np.cos(np.pi * np.arange(n) / L1.DEGREE)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    w = (-1.0) ** np.arange(n)
    w[[0, -1]] *= 0.5
    gn, gw = np.polynomial.legendre.leggauss(L1.QUADRATURE)
    K = np.zeros((n * n, n * n))
    Khat = np.zeros((n * n, n * n))
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            ell, upper = m - C_, C_ - p
            beta, alpha = m - K_, K_ - p
            cuts = sorted({ell, upper} | ({beta, alpha} if beta < alpha else set()))
            rowK = np.zeros((n, n))
            rowH = np.zeros((n, n))
            for a, b in zip(cuts[:-1], cuts[1:]):
                mid, rad = 0.5 * (a + b), 0.5 * (b - a)
                z = mid + rad * gn
                dens = rad * gw * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
                wp = bary_rows(np.maximum(0.0, p + z - K_), nodes, w)
                wm = bary_rows(np.maximum(0.0, m - z - K_), nodes, w)
                piece = np.einsum("q,qa,qb->ab", dens, wp, wm)
                rowK += piece
                if not (beta < alpha and a >= beta - 1e-15 and b <= alpha + 1e-15):
                    rowH += piece
            K[i * n + j] = rowK.ravel()
            Khat[i * n + j] = rowH.ravel()
    return K, Khat, n


def proposal(kind: str, alpha: float, beta: float):
    K, Khat, n = kernel_matrices()
    M = Khat if kind == "odd" else K
    g = np.linalg.solve(np.eye(n * n) - M, np.ones(n * n))
    return L1.dyadic_candidate(alpha * g + beta, n), float(g.max())


# ------------------------------------------------------------------ certification
def certify(kind: str, payload: dict, *, bits: int = 256, depth: int = 2) -> dict:
    if kind not in ("odd", "whole"):
        raise ValueError(kind)
    with workprec(bits):
        e = arb(0)
        b0 = RA.phi_taylor_coefficients(RA.TAYLOR_N, e)
        eps_z = RA.taylor_remainder(RA.TAYLOR_N, exact(F(11, 2)))
        w = chebyshev_payload_to_power(payload)
        sup_w = _chebyshev_sup(payload)
        lo, hi = _kernel_polynomials(w, b0, z_weight=0)
        allow = Z_RANGE * sup_w * eps_z
        if kind == "odd":
            m = {(0, 1): arb(1)}
            p = {(1, 0): arb(1)}
            beta = bi_add(m, {(0, 0): -arb(1) / arb(2)})
            alpha = bi_add(bi_scale(p, -arb(1)), {(0, 0): arb(1) / arb(2)})
            origin = _kernel_piece(w, "origin", beta, alpha, b0, z_weight=0)
            lo = bi_add(lo, bi_scale(origin, -arb(1)))
            allow = allow + Z_RANGE * sup_w * eps_z            # the removed piece carries its own truncation error
        one = {(0, 0): arb(1)}
        L_lo = bi_add(bi_add(w, bi_scale(lo, -arb(1))), bi_scale(one, -(arb(1) + allow)))
        L_hi = bi_add(bi_add(w, bi_scale(hi, -arb(1))), bi_scale(one, -(arb(1) + allow)))
        Lmin, _, npatch = min_max_on_reachable(L_lo, L_hi, depth)
        wmin, wmax, _ = min_max_on_reachable(w, w, depth)
        ok = bool(Lmin > 0) and bool(wmin >= 0)
        return {"kind": kind, "bits": bits, "subdivision_depth": depth, "patches": npatch,
                "supersolution_margin_lower_bound": Lmin, "w_min_lower_bound": wmin, "C_upper_bound": wmax,
                "allowance": allow, "certified": ok}


def _q(x):
    import rung3_engine as R1E
    return R1E.fraction_of(x)


def artifact(kind: str, alpha: str, beta: str, depth: int, bits: int = 256) -> dict:
    """Build the frozen certificate artifact (float proposal -> exact payload -> certified bounds)."""
    pay, gmax = proposal(kind, float(F(alpha)), float(F(beta)))
    r = certify(kind, pay, bits=bits, depth=depth)
    if not r["certified"]:
        raise ArithmeticError(f"{kind}: supersolution not certified")
    return {"schema": "rebaseguard.p5y.k5.order3-r3.resolvent-certificate.v1",
            "name": "C_o0" if kind == "odd" else "C_e0", "kind": kind, "drift": "0",
            "norm": "sup norm of bounded functions on the reachable CUSUM state set (frozen reachable cover)",
            "statement": ("||(I - K_0)^-1 f|| <= C ||f|| for every sigma-odd f" if kind == "odd"
                          else "||(I - K_0)^-1 f|| <= C ||f|| for every f (in particular sigma-even f)"),
            "method": ("strong Markov at T0 = hit of the sigma-fixed atom (0,0) + polynomial supersolution of "
                       "E_x[tau ^ T0] with the frozen Pair kernel minus the frozen origin piece"
                       if kind == "odd" else "polynomial supersolution of E_x[tau] with the frozen Pair kernel"),
            "proposal": {"alpha": alpha, "beta": beta, "float_sup_of_expected_run_length": gmax},
            "precision_bits": bits, "subdivision_depth": depth, "payload": pay,
            "certified": {"supersolution_margin_lower_bound": str(_q(r["supersolution_margin_lower_bound"])),
                          "w_min_lower_bound": str(_q(r["w_min_lower_bound"])),
                          "C_upper_bound": str(_q(r["C_upper_bound"])),
                          "truncation_allowance": str(_q(r["allowance"].upper()))}}


def verify_artifact(art: dict) -> dict:
    """Recompute every certified number from the stored exact payload (no float step)."""
    r = certify(art["kind"], art["payload"], bits=art["precision_bits"], depth=art["subdivision_depth"])
    got = {"supersolution_margin_lower_bound": str(_q(r["supersolution_margin_lower_bound"])),
           "w_min_lower_bound": str(_q(r["w_min_lower_bound"])), "C_upper_bound": str(_q(r["C_upper_bound"])),
           "truncation_allowance": str(_q(r["allowance"].upper()))}
    return {"certified": r["certified"] and F(got["supersolution_margin_lower_bound"]) > 0
            and F(got["w_min_lower_bound"]) >= 0, "recomputed": got, "identical": got == art["certified"]}


if __name__ == "__main__":
    import json
    if sys.argv[1] == "artifact":
        kind, alpha, beta, depth, out = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
        art = artifact(kind, alpha, beta, depth)
        Path(out).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
        print(art["name"], art["certified"])
    elif sys.argv[1] == "verify":
        print(json.dumps(verify_artifact(json.loads(Path(sys.argv[2]).read_text())), indent=1))
    else:
        kind = sys.argv[1]
        a, b = float(sys.argv[2]), float(sys.argv[3])
        depth = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        pay, gmax = proposal(kind, a, b)
        r = certify(kind, pay, depth=depth)
        print({k: (v.str(12) if hasattr(v, "str") else v) for k, v in r.items()}, "float gmax", gmax)
