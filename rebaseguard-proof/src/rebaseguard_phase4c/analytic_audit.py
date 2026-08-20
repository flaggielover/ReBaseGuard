"""Arb audit of SR geometry, derivative bounds, and two-dimensionality."""

from __future__ import annotations

from flint import arb

from rebaseguard_certify.arb_backend import ball_record, rational, workprec


def _sigmoid(value: arb) -> arb:
    return arb(1) / (arb(1) + (-value).exp())


def audit_analytic_structure(*, bits: int = 192) -> dict[str, object]:
    with workprec(bits):
        one = arb(1)
        half = rational(1, 2)
        a = rational(8325, 16)
        log_a = a.log()
        live_max = (one + a).log()
        denominator = one - (a + one) / (arb.const_e() * a)
        exp_sum_cap = (a + one) / denominator
        sum_cap = exp_sum_cap.log()
        product_min = (-one).exp()
        product_max = exp_sum_cap / arb.const_e()
        coordinate_min = (one + product_min / a).log()
        continuation_width = arb(2) * log_a + one - sum_cap
        fixed_point_image = (
            (one + a) * (one + (sum_cap - one).exp() / a)
        ).log()

        t_min = -log_a - one
        t_max = log_a
        sigmoid_min = _sigmoid(t_min)
        sigmoid_max = _sigmoid(t_max)

        z1 = one
        z2 = arb(0)
        first_plus = (one + (z1 - half).exp()).log()
        first_minus = (one + (-z1 - half).exp()).log()
        s1_plus = _sigmoid(z1 - half)
        s1_minus = _sigmoid(-z1 - half)
        s2_plus = _sigmoid(first_plus + z2 - half)
        s2_minus = _sigmoid(first_minus - z2 - half)
        two_step_jacobian = s2_plus * s2_minus * (s1_minus - s1_plus)

        checks = {
            "invariant_denominator_positive": denominator > 0,
            "sum_cap_fixed_point": (fixed_point_image - sum_cap).contains(0),
            "sum_cap_less_than_naive_square": sum_cap < arb(2) * live_max,
            "product_cap_less_than_A_squared": product_max < a * a,
            "continuation_width_gt_6_79": continuation_width > rational(679, 100),
            "coordinate_floor_positive": coordinate_min > 0,
            "two_step_jacobian_nonzero": two_step_jacobian < 0,
            "softplus_slope_strictly_between_zero_and_one": (
                sigmoid_min > 0 and sigmoid_max < 1
            ),
        }
        if not all(checks.values()):
            raise ArithmeticError("analytic SR structure audit failed")
        return {
            "schema": "rebaseguard.phase4c.analytic-structure.v1",
            "proof_role": "RIGOROUS ARB FEASIBILITY LEMMAS; NOT FINAL GAMMA CERTIFICATE",
            "precision_bits": bits,
            "constants": {
                "A": ball_record(a),
                "log_A": ball_record(log_a),
                "live_y_max_log_1_plus_A": ball_record(live_max),
                "sum_cap": ball_record(sum_cap),
                "product_min": ball_record(product_min),
                "product_max": ball_record(product_max),
                "coordinate_min": ball_record(coordinate_min),
                "minimum_continuation_width": ball_record(continuation_width),
            },
            "transition_derivatives": {
                "softplus_slope_min": ball_record(sigmoid_min),
                "softplus_slope_max": ball_record(sigmoid_max),
                "softplus_second_derivative_global_upper": "1/4 exact",
                "source_coordinate_lipschitz": "1 in each active source coordinate",
                "innovation_lipschitz": "1 in each target coordinate",
                "convexity": "softplus is globally convex in its affine argument",
            },
            "two_step_jacobian_determinant_at_z1_1_z2_0": ball_record(
                two_step_jacobian
            ),
            "checks": checks,
            "reachable_enclosure": {
                "reset": "(0,0) added separately",
                "nonreset_constraints": [
                    "0<Y_plus,Y_minus<=log(1+A)",
                    "exp(-1)<=R_plus*R_minus<=product_max",
                    "Y_plus+Y_minus<=sum_cap",
                ],
                "invariant_identity": "R'_plus*R'_minus=exp(Y_plus+Y_minus-1)",
                "least_cap_iteration": (
                    "C_{j+1}=log((1+A)(1+exp(C_j-1)/A)), C_0=0"
                ),
            },
        }
