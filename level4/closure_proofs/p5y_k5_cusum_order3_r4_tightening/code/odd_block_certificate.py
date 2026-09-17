"""R4-B: exact sigma-odd block certificate for the CUSUM kernel at drift e = 0.

Operator information only (K_0 with weight phi on bounded functions on the reachable set R). No source term, DAG
object, K1 record or R''' value.

REDUCTION (exact, at e = 0). sigma(p, m) = (m, p), H = {x in R : p >= m}, d = p - m >= 0 for x in H,
q(x, z) = ((p + z - 1/2)+, (m - z - 1/2)+), survival window z in [m - c, c - p], c = 11/2.
  (i)   q(x, z) lies in H iff z >= -d/2 (interior: q_p - q_m = d + 2z; axes and the origin atom likewise), and
        sigma q(x, z) = q(x, -d - z); z -> -d - z maps the window onto itself.
  (ii)  For sigma-odd u = (I - K_0)^-1 f and x in H:
            u(x) = f(x) + int_{z > -d/2} [phi(z) - phi(-d - z)] u(q(x, z)) dz =: f(x) + (K_o u)(x),
        the atom (0,0) and the diagonal contribute u = 0 exactly, and there is no even leakage at e = 0.
  (iii) phi(z) >= phi(-d - z) for z >= -d/2 (|z| <= d + z), so K_o is a POSITIVE operator on bounded functions on H,
        K_o <= Khat (R3), hence sum_j K_o^j 1 <= E_x[tau ^ T0] < oo and u = sum_j K_o^j f.
  (iv)  For a positive operator the sup-norm resolvent norm equals sup_H sum_j K_o^j 1. If w >= 0 on H and
        w >= 1 + K_o w on H, then sum_(j<n) K_o^j 1 <= w for all n, so for every sigma-odd f
            ||(I - K_0)^-1 f|| = sup_H |u| <= ||f|| sup_H w =: C_o0      (sigma-odd: |u(sigma x)| = |u(x)|).
  The load-bearing operator is the projected odd operator itself; nothing is bounded on the full space and then
  projected. The bound is EXACT in the limit (the minimal supersolution is the odd resolvent applied to 1).

POLYNOMIAL FORM. For w a polynomial on [0,5]^2 and w_s(y) = w(sigma y), with the frozen kernel pieces
("up" = p-axis, "both" = interior, "down" = m-axis) and mid = (m - p)/2 = -d/2:
    p + m >= 1:  K_o w = up(w)[m - 1/2, c - p] + both(w)[mid, m - 1/2] - both(w_s)[1/2 - p, mid] - down(w_s)[m - c, 1/2 - p]
    p + m <= 1:  K_o w = up(w)[1/2 - p, c - p] - down(w_s)[m - c, m - 1/2]           (origin atom: u = 0)
The second integrals are the reflected halves int_{z < -d/2} phi(z) w(sigma q(x, z)) dz of (ii).
CERTIFICATION. L := w - 1 - (K_o w)_poly - 2 Z_RANGE sup|w| eps_z (frozen phi truncation, charged for both halves);
certified by Bernstein coefficients on the H-part of the frozen reachable cover (triangle parameter t in [1/2, 1]
for r in [0,1] and [1,4]; the p-axis tail p in [4,5]) with subdivision:  min L > 0, min w >= 0, C := max w.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(CP / "p5y_k5_cusum_order3_r3_infrastructure/code"), str(CP / "p5y_k5_cusum_order3_real_producer/code"),
           str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5  # noqa: E402,F401

import numpy as np  # noqa: E402
from flint import arb  # noqa: E402

import cusum_layer1 as L1  # noqa: E402
from cusum_layer2 import Z_RANGE  # noqa: E402
import ra_certifier as RA  # noqa: E402
from fast_range import affine_to_unit_square_fast  # noqa: E402
from intervals import exact, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_scale, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import (_chebyshev_sup, _kernel_piece, _parameterize_triangle,  # noqa: E402
                                          _power_to_bernstein, _split_patch)

K_, C_ = 0.5, 5.5
HALF = F(1, 2)


def swap(poly):
    return {(j, i): c for (i, j), c in poly.items()}


def _lin(cp, cm, c0):
    out = {}
    if cp:
        out[(1, 0)] = exact(F(cp))
    if cm:
        out[(0, 1)] = exact(F(cm))
    out[(0, 0)] = exact(F(c0))
    return out


def odd_kernel(w, b0):
    """(low, high) polynomial enclosures of K_o w for x in H (low: p + m <= 1, high: p + m >= 1)."""
    ws = swap(w)
    ell, upper = _lin(0, 1, "-11/2"), _lin(-1, 0, "11/2")
    beta, alpha, mid = _lin(0, 1, "-1/2"), _lin(-1, 0, "1/2"), _lin("-1/2", "1/2", 0)
    kp = lambda poly, mode, lo, hi: _kernel_piece(poly, mode, lo, hi, b0, z_weight=0)
    low = bi_add(kp(w, "up", alpha, upper), bi_scale(kp(ws, "down", ell, beta), -arb(1)))
    high = kp(w, "up", beta, upper)
    high = bi_add(high, kp(w, "both", mid, beta))
    high = bi_add(high, bi_scale(kp(ws, "both", alpha, mid), -arb(1)))
    high = bi_add(high, bi_scale(kp(ws, "down", ell, alpha), -arb(1)))
    return low, high


# ------------------------------------------------------------------ Bernstein on the H-part of the reachable cover
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


def h_pieces(low_poly, high_poly):
    t0 = exact(HALF)
    low = affine_to_unit_square_fast(_parameterize_triangle(low_poly), arb(0), arb(1), t0, arb(1))
    high = affine_to_unit_square_fast(_parameterize_triangle(high_poly), arb(1), arb(4), t0, arb(1))
    plus = {(i, 0): c for (i, j), c in high_poly.items() if j == 0}
    return [_power_to_bernstein(low), _power_to_bernstein(high),
            _power_to_bernstein(affine_to_unit_square_fast(plus, arb(4), arb(5), arb(0), arb(1)))]


def min_max_on_h(low_poly, high_poly, depth):
    mn, mx, count = None, None, 0
    for coeffs in h_pieces(low_poly, high_poly):
        for patch in _patches(coeffs, depth):
            count += 1
            for row in patch:
                for c in row:
                    lo_c, hi_c = c.lower(), c.upper()
                    mn = lo_c if mn is None or lo_c < mn else mn
                    mx = hi_c if mx is None or hi_c > mx else mx
    return mn, mx, count


# ------------------------------------------------------------------ certification
def certify(payload: dict, *, bits: int = 256, depth: int = 2) -> dict:
    with workprec(bits):
        b0 = RA.phi_taylor_coefficients(RA.TAYLOR_N, arb(0))
        eps_z = RA.taylor_remainder(RA.TAYLOR_N, exact(F(11, 2)))
        w = chebyshev_payload_to_power(payload)
        sup_w = _chebyshev_sup(payload)
        allow = arb(2) * Z_RANGE * sup_w * eps_z
        low, high = odd_kernel(w, b0)
        shift = {(0, 0): -(arb(1) + allow)}
        L_low = bi_add(bi_add(w, bi_scale(low, -arb(1))), shift)
        L_high = bi_add(bi_add(w, bi_scale(high, -arb(1))), shift)
        Lmin, _, npatch = min_max_on_h(L_low, L_high, depth)
        wmin, wmax, _ = min_max_on_h(w, w, depth)
        ok = bool(Lmin > 0) and bool(wmin >= 0)
        return {"bits": bits, "subdivision_depth": depth, "patches": npatch, "supersolution_margin_lower_bound": Lmin,
                "w_min_lower_bound": wmin, "C_upper_bound": wmax, "allowance": allow, "certified": ok}


# ------------------------------------------------------------------ float proposal (not evidence)
def _bary(values, nodes, wts):
    d = values[:, None] - nodes[None, :]
    ex = np.abs(d) < 2e-14
    d = np.where(ex, 1.0, d)
    t = wts[None, :] / d
    t = t / t.sum(axis=1, keepdims=True)
    hit = ex.any(axis=1)
    if hit.any():
        t[hit] = ex[hit].astype(float)
    return t


def odd_matrix(quad: int = 400):
    """Float K_o on the frozen Chebyshev grid for sigma-symmetric w (w_s = w), rows at x or sigma x in H."""
    n = L1.DEGREE + 1
    x = np.cos(np.pi * np.arange(n) / L1.DEGREE)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    wts = (-1.0) ** np.arange(n)
    wts[[0, -1]] *= 0.5
    gn, gw = np.polynomial.legendre.leggauss(quad)
    M = np.zeros((n * n, n * n))
    for i, p0 in enumerate(nodes):
        for j, m0 in enumerate(nodes):
            p, m = (p0, m0) if p0 >= m0 else (m0, p0)
            ell, upper, midz = m - C_, C_ - p, (m - p) / 2
            cuts = sorted({ell, upper, midz} | {z for z in (K_ - p, m - K_) if ell < z < upper})
            row = np.zeros((n, n))
            for a, b in zip(cuts[:-1], cuts[1:]):
                if b - a < 1e-15:
                    continue
                c, r = 0.5 * (a + b), 0.5 * (b - a)
                z = c + r * gn
                qp, qm = np.maximum(0.0, p + z - K_), np.maximum(0.0, m - z - K_)
                inside = ~((qp == 0) & (qm == 0))
                dens = r * gw * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi) * inside
                sign = 1.0 if c > midz else -1.0
                row += sign * np.einsum("q,qa,qb->ab", dens, _bary(qp, nodes, wts), _bary(qm, nodes, wts))
            M[i * n + j] = row.ravel()
    return M, n


def proposal(alpha: float, beta: float):
    M, n = odd_matrix()
    g = np.linalg.solve(np.eye(n * n) - M, np.ones(n * n))
    g = 0.5 * (g + g.reshape(n, n).T.ravel())
    return L1.dyadic_candidate(alpha * g + beta, n), float(g.max())


def _q(x):
    import rung3_engine as R1E
    return R1E.fraction_of(x)


def artifact(alpha: str, beta: str, depth: int, bits: int = 256) -> dict:
    pay, gmax = proposal(float(F(alpha)), float(F(beta)))
    r = certify(pay, bits=bits, depth=depth)
    if not r["certified"]:
        raise ArithmeticError("odd block: supersolution not certified")
    return {"schema": "rebaseguard.p5y.k5.order3-r4.odd-block-certificate.v1", "name": "C_o0", "drift": "0",
            "norm": "sup norm of bounded functions on the reachable CUSUM state set (frozen reachable cover)",
            "statement": "||(I - K_0)^-1 f|| <= C ||f|| for every sigma-odd f",
            "method": ("exact sigma-odd block reduction to H = {p >= m} with the positive reflected kernel "
                       "phi(z) - phi(-d - z), z > -d/2; polynomial supersolution of sum_j K_o^j 1 with the frozen "
                       "kernel pieces; Bernstein on the H-part of the frozen reachable cover"),
            "proposal": {"alpha": alpha, "beta": beta, "float_sup_of_odd_block_resolvent_of_one": gmax},
            "precision_bits": bits, "subdivision_depth": depth, "payload": pay,
            "certified": {"supersolution_margin_lower_bound": str(_q(r["supersolution_margin_lower_bound"])),
                          "w_min_lower_bound": str(_q(r["w_min_lower_bound"])),
                          "C_upper_bound": str(_q(r["C_upper_bound"])),
                          "truncation_allowance": str(_q(r["allowance"].upper()))}}


def verify_artifact(art: dict) -> dict:
    r = certify(art["payload"], bits=art["precision_bits"], depth=art["subdivision_depth"])
    got = {"supersolution_margin_lower_bound": str(_q(r["supersolution_margin_lower_bound"])),
           "w_min_lower_bound": str(_q(r["w_min_lower_bound"])), "C_upper_bound": str(_q(r["C_upper_bound"])),
           "truncation_allowance": str(_q(r["allowance"].upper()))}
    return {"certified": r["certified"] and F(got["supersolution_margin_lower_bound"]) > 0
            and F(got["w_min_lower_bound"]) >= 0, "recomputed": got, "identical": got == art["certified"]}


if __name__ == "__main__":
    import json
    if sys.argv[1] == "artifact":
        art = artifact(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        Path(sys.argv[5]).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
        print("C_o0", art["certified"])
    elif sys.argv[1] == "verify":
        print(json.dumps(verify_artifact(json.loads(Path(sys.argv[2]).read_text())), indent=1))
    else:
        a, b = float(sys.argv[1]), float(sys.argv[2])
        depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        pay, gmax = proposal(a, b)
        r = certify(pay, depth=depth)
        print({k: (v.str(10) if hasattr(v, "str") else v) for k, v in r.items()}, "float sup", gmax, flush=True)
