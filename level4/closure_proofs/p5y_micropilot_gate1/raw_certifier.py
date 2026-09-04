"""P5Y Gate-1 M1 pilot: RAW-VARIABLE certified enclosure of R_{CUSUM,m=1}(e).

NOT production.  NOT a certificate of record.  A falsification pilot only.

Every equation-building object is IMPORTED UNMODIFIED from the historical P5X
R-A' / R2 modules: the kernel assembly `_kernel_polynomials`, the recentred
Hermite coefficients, the reachable-set Bernstein range bound, the resolvent
minorant, the candidate solver's collocation geometry, the state square, the
precision, the Taylor order and the candidate degree.

Exactly two things change, and only these (GATE1_PREREGISTRATION.md section 2.3):

  (1) the UNKNOWN and its SOURCE.  The historical certifier solves for
      ghat = R - e with source rho_1,e; this pilot solves for F = E_x[raw_tau]
      with source rho_1^raw = phi(u+e) - phi(l+e), using the exact identity
      rho_1,e + e h_1 = phi(u+e) - phi(l+e).  R(e) = F(x_0) directly, with no
      external '+ e' cancellation term.

  (2) the bootstrap constant c_2, which in the raw representation is the
      e-FREE constant 2 max|(x^2-1) phi(x)| = 2 phi(0) instead of the
      e-GROWING 1.13788 + b|e|.

The operator K_e, the estimand R_{CUSUM,1}(e), the state space, the stopping
convention and the detector semantics are untouched.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from flint import arb
from scipy.special import ndtr

_ROOT = Path(__file__).resolve().parents[3]
_P5X = _ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
_PROOF_SRC = _ROOT / "rebaseguard-proof" / "src"
for _p in (str(_PROOF_SRC), str(_P5X / "certified_method_repair_ra"),
           str(_P5X / "compute_optimization_r1"), str(_P5X / "compute_optimization_r2")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
from rebaseguard_certify.polynomial import (                                  # noqa: E402
    BiPoly, bi_add, bi_eval, bi_mul, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_polynomials  # noqa: E402
from rebaseguard_certify.spectral_candidate import (                          # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis,
)
import ra_certifier as RA                                                     # noqa: E402
from fast_range import max_abs_on_reachable_fast                              # noqa: E402

K_FROZEN = RA.K_FROZEN
H_FROZEN = RA.H_FROZEN
C_CUSUM = RA.C_CUSUM
DEPTH_LADDER = (0, 1, 2, 3)          # frozen, inherited from R2
DEPTH_BUDGET = arb(1) / arb(20)      # frozen 0.05, inherited from R2


# --------------------------------------------------------------------------
# Raw-variable rewards.  Both are pure boundary-density expressions: the entire
# e-linear and e-quadratic content of the z-variable rewards has cancelled.
# --------------------------------------------------------------------------
def reward_rho1_raw(order: int, e: arb) -> BiPoly:
    """rho_1^raw = phi(u+e) - phi(l+e).   (no cdf terms, no e multiplier)"""
    (phi_u, _), (phi_l, _), _, _ = RA._recentred_sites(order, e)
    return bi_add(phi_u, bi_scale(phi_l, -arb(1)))


def reward_drho1_raw(order: int, e: arb) -> BiPoly:
    """d_e rho_1^raw = phi'(u+e) - phi'(l+e) = -(u+e)phi(u+e) + (l+e)phi(l+e)."""
    (phi_u, _), (phi_l, _), arg_u, arg_l = RA._recentred_sites(order, e)
    out = bi_scale(bi_mul(arg_u, phi_u), -arb(1))
    return bi_add(out, bi_mul(arg_l, phi_l))


# --------------------------------------------------------------------------
# Candidate solve.  Geometry, nodes, quadrature and kernel are RA's; only the
# two right-hand sides change.
# --------------------------------------------------------------------------
def _collocation_raw(drift: float, degree: int, quadrature_order: int):
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    nodes = 0.5 * H_FROZEN * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quadrature_order)
    dim = count * count
    kernel = np.zeros((dim, dim))
    kernel_dphi = np.zeros((dim, dim))
    reward = np.zeros(dim)
    dreward = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * count + j
            ell = m - C_CUSUM
            upper = C_CUSUM - p
            mid = 0.5 * (ell + upper)
            rad = 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / norm
                wp = _basis(max(0.0, p + z - K_FROZEN), nodes, bary)
                wm = _basis(max(0.0, m - z - K_FROZEN), nodes, bary)
                interp = np.outer(wp, wm).ravel()
                kernel[row] += dens * interp
                kernel_dphi[row] += (-y) * dens * interp
            au = upper + drift
            al = ell + drift
            pu = math.exp(-0.5 * au * au) / norm
            pl = math.exp(-0.5 * al * al) / norm
            reward[row] = pu - pl                       # RAW: no  - drift*brack
            dreward[row] = -au * pu + al * pl           # RAW: no  -brack + drift*(pu-pl)
    return nodes, kernel, kernel_dphi, reward, dreward, count


def solve_candidates_raw(drift: float, degree: int = RA.DEGREE,
                         quadrature_order: int = RA.QUADRATURE):
    _, kernel, kernel_dphi, reward, dreward, count = _collocation_raw(
        drift, degree, quadrature_order)
    dim = count * count
    operator = np.eye(dim) - kernel
    f = np.linalg.solve(operator, reward)
    df = np.linalg.solve(operator, kernel_dphi @ f + dreward)
    return (SpectralCandidate(f.reshape(count, count), H_FROZEN),
            SpectralCandidate(df.reshape(count, count), H_FROZEN))


# --------------------------------------------------------------------------
# Certified residuals at one exact rational drift, raw representation.
# --------------------------------------------------------------------------
def certify_raw_at_exact_drift(e_num: int, e_den: int, *, resolvent: arb,
                               order: int = RA.TAYLOR_N, degree: int = RA.DEGREE,
                               quadrature_order: int = RA.QUADRATURE,
                               scale_bits: int = RA.SCALE_BITS,
                               bits: int = RA.BITS,
                               e_hi_for_allowance: float = 0.26) -> dict:
    drift = e_num / e_den
    cand_f, cand_df = solve_candidates_raw(drift, degree, quadrature_order)
    pay_f = cand_f.to_chebyshev_dyadic(scale_bits=scale_bits)
    pay_df = cand_df.to_chebyshev_dyadic(scale_bits=scale_bits)

    with workprec(bits):
        e = rational(e_num, e_den)
        b = RA.phi_taylor_coefficients(order, e)
        db = RA.derivative_coefficients(b)
        f_hat = chebyshev_payload_to_power(pay_f)
        df_hat = chebyshev_payload_to_power(pay_df)

        kf_low, kf_high = _kernel_polynomials(f_hat, b, z_weight=0)
        rho1 = reward_rho1_raw(order, e)
        res_f_low = bi_add(bi_add(f_hat, bi_scale(kf_low, -arb(1))), bi_scale(rho1, -arb(1)))
        res_f_high = bi_add(bi_add(f_hat, bi_scale(kf_high, -arb(1))), bi_scale(rho1, -arb(1)))

        kdf_low, kdf_high = _kernel_polynomials(df_hat, b, z_weight=0)
        dkf_low, dkf_high = _kernel_polynomials(f_hat, db, z_weight=0)
        drho1 = reward_drho1_raw(order, e)
        res_d_low = bi_add(bi_add(df_hat, bi_scale(kdf_low, -arb(1))),
                           bi_add(bi_scale(dkf_low, -arb(1)), bi_scale(drho1, -arb(1))))
        res_d_high = bi_add(bi_add(df_hat, bi_scale(kdf_high, -arb(1))),
                            bi_add(bi_scale(dkf_high, -arb(1)), bi_scale(drho1, -arb(1))))

        eps_z = RA.taylor_remainder(order, rational(11, 2))
        eps_reward = RA.taylor_remainder(order, rational(5, 2))
        eps_dz = arb(order + 1) * eps_z
        sup_f = _chebyshev_sup(pay_f)
        sup_df = _chebyshev_sup(pay_df)
        e_hi = arb(rational(round(e_hi_for_allowance * 10 ** 6), 10 ** 6))
        # RAW allowance: the two-phi-site part of the frozen R-A' allowance.
        # The e-dependent cdf part is absent because the raw reward has no cdf term.
        reward_allow = arb(2) * eps_reward * (arb(1) + rational(5, 2))

        chosen = None
        for d in DEPTH_LADDER:
            poly_f, coverage = max_abs_on_reachable_fast(
                res_f_low, res_f_high, subdivision_depth=d)
            delta = poly_f + arb(11) * sup_f * eps_z + reward_allow
            if resolvent * delta <= DEPTH_BUDGET:
                chosen = (d, poly_f, delta, coverage)
                break
        if chosen is None:
            raise ArithmeticError("frozen depth ladder exhausted")
        depth, poly_f, delta, coverage = chosen

        poly_d, _ = max_abs_on_reachable_fast(res_d_low, res_d_high, subdivision_depth=depth)
        delta_d = (poly_d + arb(11) * sup_df * eps_z + arb(11) * sup_f * eps_dz
                   + reward_allow * (arb(1) + rational(11, 2) + e_hi))
        if not delta > 0 or not delta_d > 0:
            raise ArithmeticError("invalid residual bounds")

        return {
            "e_rational": f"{e_num}/{e_den}", "e_float": drift,
            "representation": "raw", "subdivision_depth_used": depth,
            "polynomial_residual_value": ball_record(poly_f),
            "polynomial_residual_derivative": ball_record(poly_d),
            "delta": ball_record(delta), "delta_derivative": ball_record(delta_d),
            "sup_chebyshev_F": ball_record(sup_f), "sup_chebyshev_dF": ball_record(sup_df),
            "Fhat_origin": ball_record(bi_eval(f_hat, arb(0), arb(0))),
            "dFhat_origin": ball_record(bi_eval(df_hat, arb(0), arb(0))),
            "coverage": coverage,
        }


# --------------------------------------------------------------------------
# The two e-free raw bootstrap constants, with their rigorous justification.
# --------------------------------------------------------------------------
def raw_bootstrap_constants() -> tuple[arb, arb]:
    """(c_1^raw, c_2^raw) = (2 max|x phi(x)|, 2 max|(x^2-1) phi(x)|) = (2 phi(1), 2 phi(0)).

    d_e rho_1^raw = phi'(u+e) - phi'(l+e) and d_e^2 rho_1^raw = phi''(u+e) - phi''(l+e),
    so each is bounded by twice the global sup of |phi'| resp. |phi''|.
    |phi'(x)| = |x| phi(x) peaks at |x| = 1.  |phi''(x)| = |x^2-1| phi(x) has
    critical points 0 and +/- sqrt 3, with |phi''(0)| = phi(0) > 2 phi(sqrt 3).
    Both are INDEPENDENT OF e -- this is the entire content of the repair.
    """
    two_pi = arb(2) * arb.pi()
    phi0 = arb(1) / two_pi.sqrt()
    phi1 = (-arb(1) / arb(2)).exp() / two_pi.sqrt()
    return arb(2) * phi1, arb(2) * phi0
