"""R2 optimized certifier: R1's equation, R2's range bound.

Every equation-building object is IMPORTED UNMODIFIED from `ra_certifier`
(candidates, Hermite coefficients, rewards, kernel assembly, remainders,
constants).  Only the Bernstein range bound is replaced: candidate C2 supplies
the fast affine substitution, candidate C1 supplies the depth by frozen ladder.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS / "certified_method_repair_ra"))

from flint import arb                                                       # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
from rebaseguard_certify.polynomial import (                                # noqa: E402
    bi_add, bi_eval, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_polynomials  # noqa: E402
import ra_certifier as RA                                                    # noqa: E402
from fast_range import max_abs_on_reachable_fast                             # noqa: E402

DEPTH_LADDER = (0, 1, 2, 3)      # frozen, R2_FROZEN_SPEC section 1 C1
DEPTH_BUDGET = arb(1) / arb(20)  # frozen 0.05


def certify_at_exact_drift_r2(e_num: int, e_den: int, *, resolvent: arb,
                              order: int = RA.TAYLOR_N, degree: int = RA.DEGREE,
                              quadrature_order: int = RA.QUADRATURE,
                              scale_bits: int = RA.SCALE_BITS,
                              bits: int = RA.BITS,
                              e_hi_for_allowance: float = 0.26) -> dict:
    drift = e_num / e_den
    cand_g, cand_dg = RA.solve_candidates(drift, degree, quadrature_order)
    pay_g = cand_g.to_chebyshev_dyadic(scale_bits=scale_bits)
    pay_dg = cand_dg.to_chebyshev_dyadic(scale_bits=scale_bits)

    with workprec(bits):
        e = rational(e_num, e_den)
        b = RA.phi_taylor_coefficients(order, e)
        db = RA.derivative_coefficients(b)
        g_hat = chebyshev_payload_to_power(pay_g)
        dg_hat = chebyshev_payload_to_power(pay_dg)

        kg_low, kg_high = _kernel_polynomials(g_hat, b, z_weight=0)
        rho1 = RA.reward_rho1(order, e)
        res_g_low = bi_add(bi_add(g_hat, bi_scale(kg_low, -arb(1))), bi_scale(rho1, -arb(1)))
        res_g_high = bi_add(bi_add(g_hat, bi_scale(kg_high, -arb(1))), bi_scale(rho1, -arb(1)))

        kdg_low, kdg_high = _kernel_polynomials(dg_hat, b, z_weight=0)
        dkg_low, dkg_high = _kernel_polynomials(g_hat, db, z_weight=0)
        drho1 = RA.reward_drho1(order, e)
        res_d_low = bi_add(bi_add(dg_hat, bi_scale(kdg_low, -arb(1))),
                           bi_add(bi_scale(dkg_low, -arb(1)), bi_scale(drho1, -arb(1))))
        res_d_high = bi_add(bi_add(dg_hat, bi_scale(kdg_high, -arb(1))),
                            bi_add(bi_scale(dkg_high, -arb(1)), bi_scale(drho1, -arb(1))))

        eps_z = RA.taylor_remainder(order, rational(11, 2))
        eps_reward = RA.taylor_remainder(order, rational(5, 2))
        eps_dz = arb(order + 1) * eps_z
        sup_g = _chebyshev_sup(pay_g)
        sup_dg = _chebyshev_sup(pay_dg)
        e_hi = arb(rational(round(e_hi_for_allowance * 10 ** 6), 10 ** 6))
        reward_allow = (arb(2) + arb(2) * e_hi * (rational(11, 2) + e_hi)) * (
            eps_reward * (arb(1) + rational(5, 2)))

        chosen = None
        for d in DEPTH_LADDER:
            poly_g, coverage = max_abs_on_reachable_fast(
                res_g_low, res_g_high, subdivision_depth=d)
            delta = poly_g + arb(11) * sup_g * eps_z + reward_allow
            if resolvent * delta <= DEPTH_BUDGET:
                chosen = (d, poly_g, delta, coverage)
                break
        if chosen is None:
            raise ArithmeticError("frozen depth ladder exhausted; abort per spec section 7")
        depth, poly_g, delta, coverage = chosen

        poly_d, _ = max_abs_on_reachable_fast(res_d_low, res_d_high, subdivision_depth=depth)
        delta_d = (poly_d + arb(11) * sup_dg * eps_z + arb(11) * sup_g * eps_dz
                   + reward_allow * (arb(1) + rational(11, 2) + e_hi))
        if not delta > 0 or not delta_d > 0:
            raise ArithmeticError("invalid residual bounds")

        return {
            "e_rational": f"{e_num}/{e_den}", "e_float": drift,
            "subdivision_depth_used": depth,
            "polynomial_residual_value": ball_record(poly_g),
            "polynomial_residual_derivative": ball_record(poly_d),
            "delta": ball_record(delta), "delta_derivative": ball_record(delta_d),
            "sup_chebyshev_g": ball_record(sup_g), "sup_chebyshev_dg": ball_record(sup_dg),
            "ghat_origin": ball_record(bi_eval(g_hat, arb(0), arb(0))),
            "dghat_origin": ball_record(bi_eval(dg_hat, arb(0), arb(0))),
            "coverage": coverage,
        }
