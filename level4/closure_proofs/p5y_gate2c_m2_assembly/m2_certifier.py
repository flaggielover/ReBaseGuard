"""P5Y Gate-2C: raw-variable m=2 first-moment assembly for CUSUM.

Imports the Gate-1 raw certifier and the historical P5X machinery UNMODIFIED.
The only new content is the m=2 source chain:

    h_1     = 1 - Phi(u+e) + Phi(l+e)          closed form, no solve
    d_e h_1 = -S_0^raw                          exact
    S_1^raw = K_{z,e} h_1 + e K_e h_1           2 kernel applications
    F_1     = (I - K_e)^{-1} S_1^raw            ONE new resolvent solve

and the finite assembly  R_2 = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ].

No second-moment object, no SR object and no other m is constructed anywhere.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from flint import arb
from scipy.special import ndtr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5X = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
G1 = ROOT / "level4" / "closure_proofs" / "p5y_micropilot_gate1"
for p in (str(ROOT / "rebaseguard-proof" / "src"), str(G1),
          str(P5X / "certified_method_repair_ra"), str(P5X / "compute_optimization_r1"),
          str(P5X / "compute_optimization_r2")):
    if p not in sys.path:
        sys.path.insert(0, p)

from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
from rebaseguard_certify.polynomial import (                                  # noqa: E402
    bi_add, bi_eval, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_polynomials  # noqa: E402
from rebaseguard_certify.spectral_candidate import (                          # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis,
)
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402
from fast_range import max_abs_on_reachable_fast                              # noqa: E402

K_F, H_F, C_F = RA.K_FROZEN, RA.H_FROZEN, RA.C_CUSUM
NORM = math.sqrt(2.0 * math.pi)


# --------------------------------------------------------------------------
# Symbolic objects
# --------------------------------------------------------------------------
def h1_bipoly(order: int, e: arb):
    """h_1 = 1 - Phi(u+e) + Phi(l+e), the frozen `bracket` of RA.reward_rho1."""
    (_, cdf_u), (_, cdf_l), _, _ = RA._recentred_sites(order, e)
    return bi_add({(0, 0): arb(1)}, bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))


def s1_raw_bipoly(order: int, e: arb, b, db):
    """S_1^raw = K_{z,e} h_1 + e K_e h_1, and d_e S_1^raw.  Returns (lo, hi) pairs."""
    h1 = h1_bipoly(order, e)
    dh1 = bi_scale(RAW.reward_rho1_raw(order, e), -arb(1))       # d_e h_1 = -S_0^raw
    kz_lo, kz_hi = _kernel_polynomials(h1, b, z_weight=1)
    k0_lo, k0_hi = _kernel_polynomials(h1, b, z_weight=0)
    s1_lo = bi_add(kz_lo, bi_scale(k0_lo, e))
    s1_hi = bi_add(kz_hi, bi_scale(k0_hi, e))
    # d_e S_1^raw = K_e h_1 + [K_{z,e} + e K_e](d_e h_1) + [K_{z,db} + e K_db] h_1
    dz_lo, dz_hi = _kernel_polynomials(dh1, b, z_weight=1)
    d0_lo, d0_hi = _kernel_polynomials(dh1, b, z_weight=0)
    pz_lo, pz_hi = _kernel_polynomials(h1, db, z_weight=1)
    p0_lo, p0_hi = _kernel_polynomials(h1, db, z_weight=0)
    ds1_lo = bi_add(k0_lo, bi_add(bi_add(dz_lo, bi_scale(d0_lo, e)),
                                  bi_add(pz_lo, bi_scale(p0_lo, e))))
    ds1_hi = bi_add(k0_hi, bi_add(bi_add(dz_hi, bi_scale(d0_hi, e)),
                                  bi_add(pz_hi, bi_scale(p0_hi, e))))
    return (s1_lo, s1_hi), (ds1_lo, ds1_hi), h1, dh1


# --------------------------------------------------------------------------
# Candidate solve for F_1 (float; candidate only, never proof evidence)
# --------------------------------------------------------------------------
def collocation_m2(drift: float, degree: int, quadrature_order: int):
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    nodes = 0.5 * H_F * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quadrature_order)
    dim = count * count
    kernel = np.zeros((dim, dim)); kernel_dphi = np.zeros((dim, dim))
    r1 = np.zeros(dim); dr1 = np.zeros(dim)          # S_1^raw and d_e S_1^raw
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * count + j
            ell, upper = m - C_F, C_F - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / NORM
                wp_s = max(0.0, p + z - K_F); wm_s = max(0.0, m - z - K_F)
                wp = _basis(wp_s, nodes, bary); wm = _basis(wm_s, nodes, bary)
                interp = np.outer(wp, wm).ravel()
                kernel[row] += dens * interp
                kernel_dphi[row] += (-y) * dens * interp
                au = C_F - wp_s + drift; al = wm_s - C_F + drift
                h1v = 1.0 - ndtr(au) + ndtr(al)
                dh1v = -(math.exp(-0.5 * au * au) - math.exp(-0.5 * al * al)) / NORM
                r1[row] += dens * y * h1v
                dr1[row] += dens * (h1v + y * dh1v - y * y * h1v)
    return nodes, kernel, kernel_dphi, r1, dr1, count


def solve_F1(drift: float, degree: int = RA.DEGREE, quadrature_order: int = RA.QUADRATURE):
    _, kernel, kernel_dphi, r1, dr1, count = collocation_m2(drift, degree, quadrature_order)
    op = np.eye(count * count) - kernel
    f1 = np.linalg.solve(op, r1)
    df1 = np.linalg.solve(op, kernel_dphi @ f1 + dr1)
    return (SpectralCandidate(f1.reshape(count, count), H_F),
            SpectralCandidate(df1.reshape(count, count), H_F))


# --------------------------------------------------------------------------
# Certified residual for F_1, mirroring raw_certifier exactly
# --------------------------------------------------------------------------
def certify_F1(e_num: int, e_den: int, *, resolvent: arb, order: int = RA.TAYLOR_N,
               degree: int = RA.DEGREE, bits: int = RA.BITS,
               e_hi_for_allowance: float = 0.26) -> dict:
    drift = e_num / e_den
    cf, cdf = solve_F1(drift, degree, RA.QUADRATURE)
    pay_f = cf.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    pay_df = cdf.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    with workprec(bits):
        e = rational(e_num, e_den)
        b = RA.phi_taylor_coefficients(order, e)
        db = RA.derivative_coefficients(b)
        (s1_lo, s1_hi), (ds1_lo, ds1_hi), h1, dh1 = s1_raw_bipoly(order, e, b, db)
        f_hat = chebyshev_payload_to_power(pay_f)
        df_hat = chebyshev_payload_to_power(pay_df)

        kf_lo, kf_hi = _kernel_polynomials(f_hat, b, z_weight=0)
        res_lo = bi_add(bi_add(f_hat, bi_scale(kf_hi, -arb(1))), bi_scale(s1_hi, -arb(1)))
        res_hi = bi_add(bi_add(f_hat, bi_scale(kf_lo, -arb(1))), bi_scale(s1_lo, -arb(1)))
        poly_f, coverage = max_abs_on_reachable_fast(res_lo, res_hi, subdivision_depth=0)

        kdf_lo, kdf_hi = _kernel_polynomials(df_hat, b, z_weight=0)
        dkf_lo, dkf_hi = _kernel_polynomials(f_hat, db, z_weight=0)
        rd_lo = bi_add(bi_add(df_hat, bi_scale(kdf_hi, -arb(1))),
                       bi_add(bi_scale(dkf_hi, -arb(1)), bi_scale(ds1_hi, -arb(1))))
        rd_hi = bi_add(bi_add(df_hat, bi_scale(kdf_lo, -arb(1))),
                       bi_add(bi_scale(dkf_lo, -arb(1)), bi_scale(ds1_lo, -arb(1))))
        poly_d, _ = max_abs_on_reachable_fast(rd_lo, rd_hi, subdivision_depth=0)

        eps_z = RA.taylor_remainder(order, rational(11, 2))
        eps_reward = RA.taylor_remainder(order, rational(5, 2))
        eps_dz = arb(order + 1) * eps_z
        sup_f = _chebyshev_sup(pay_f); sup_df = _chebyshev_sup(pay_df)
        e_hi = arb(rational(round(e_hi_for_allowance * 10 ** 6), 10 ** 6))
        # allowance: the h_1 source carries two phi sites AND two cdf sites, each
        # transported through one kernel application over a range of length <= 11
        allow = arb(11) * (arb(2) + arb(2) * rational(5, 2)) * eps_reward * (
            arb(1) + rational(5, 2))
        delta = poly_f + arb(11) * sup_f * eps_z + allow * (arb(1) + e_hi)
        delta_d = (poly_d + arb(11) * sup_df * eps_z + arb(11) * sup_f * eps_dz
                   + allow * (arb(1) + rational(11, 2) + e_hi) * (arb(1) + e_hi))
        if not delta > 0 or not delta_d > 0:
            raise ArithmeticError("invalid residual bounds")
        return {
            "e_rational": f"{e_num}/{e_den}", "representation": "raw", "object": "F_1",
            "polynomial_residual_value": ball_record(poly_f),
            "polynomial_residual_derivative": ball_record(poly_d),
            "delta": ball_record(delta), "delta_derivative": ball_record(delta_d),
            "sup_chebyshev_F1": ball_record(sup_f), "sup_chebyshev_dF1": ball_record(sup_df),
            "F1hat_origin": ball_record(bi_eval(f_hat, arb(0), arb(0))),
            "dF1hat_origin": ball_record(bi_eval(df_hat, arb(0), arb(0))),
            "h1_origin": ball_record(bi_eval(h1, arb(0), arb(0))),
            "S0raw_origin": ball_record(bi_eval(
                RAW.reward_rho1_raw(order, e), arb(0), arb(0))),
            "_F1": bi_eval(f_hat, arb(0), arb(0)), "_delta": delta,
            "_h1": bi_eval(h1, arb(0), arb(0)),
            "_S0raw": bi_eval(RAW.reward_rho1_raw(order, e), arb(0), arb(0)),
            "coverage": coverage,
        }
