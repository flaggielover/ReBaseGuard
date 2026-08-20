"""Build the quantitative Phase-4C feasibility error budget."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

from rebaseguard_phase4c.interval_prototype import fit_dyadic_candidate


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4c" / "error_budget.json"


def propagated_error(resolvent: float, kz_norm: float, eps_a: float, eps_b: float) -> dict[str, float]:
    a_solution_error = resolvent * eps_a
    b_from_a = resolvent * kz_norm * a_solution_error
    b_direct = resolvent * eps_b
    return {
        "a_solution_error": a_solution_error,
        "b_error_induced_by_a": b_from_a,
        "b_error_direct": b_direct,
        "total_b_error": b_from_a + b_direct,
    }


def main() -> None:
    candidate = fit_dyadic_candidate()
    signed_sum = sum(
        coefficient * (-1 if (i + j) % 2 else 1)
        for i, row in enumerate(candidate.b)
        for j, coefficient in enumerate(row)
    )
    gamma_fraction = Fraction(signed_sum, 1 << candidate.scale_bits)
    gamma_center = float(gamma_fraction)
    resolvent = 139.0 / 0.11
    kz_norm = math.sqrt(2.0 / math.pi)
    nominal = propagated_error(
        resolvent,
        kz_norm,
        candidate.diagnostic_residual_a,
        candidate.diagnostic_residual_b,
    )
    inflation = []
    for factor in (1, 5, 10, 15, 20):
        errors = propagated_error(
            resolvent,
            kz_norm,
            factor * candidate.diagnostic_residual_a,
            factor * candidate.diagnostic_residual_b,
        )
        inflation.append(
            {
                "diagnostic_residual_inflation_factor": factor,
                **errors,
                "candidate_lower_after_propagation": gamma_center
                - errors["total_b_error"],
            }
        )
    target_eps_a = 5e-6
    target_eps_b = 1.5e-3
    engineering_reserve = 0.5
    target = propagated_error(resolvent, kz_norm, target_eps_a, target_eps_b)
    expected_lower = gamma_center - target["total_b_error"] - engineering_reserve
    allowable_eps_a = (
        gamma_center
        - 2.0
        - resolvent * target_eps_b
        - engineering_reserve
    ) / (resolvent * resolvent * kz_norm)
    allowable_eps_b = (
        gamma_center
        - 2.0
        - resolvent * resolvent * kz_norm * target_eps_a
        - engineering_reserve
    ) / resolvent
    payload = {
        "schema": "rebaseguard.phase4c.error-budget.v1",
        "proof_role": "PESSIMISTIC FEASIBILITY BUDGET; NOT A CERTIFIED ENCLOSURE",
        "candidate": {
            "degree": candidate.degree,
            "scale_bits": candidate.scale_bits,
            "sha256": candidate.digest(),
            "exact_dyadic_gamma_numerator": gamma_fraction.numerator,
            "exact_dyadic_gamma_denominator": gamma_fraction.denominator,
            "gamma_center": gamma_center,
            "diagnostic_residual_a": candidate.diagnostic_residual_a,
            "diagnostic_residual_b": candidate.diagnostic_residual_b,
        },
        "operator_bounds": {
            "resolvent": resolvent,
            "K_z_sup_norm_upper": kz_norm,
            "K_z_derivation": "integral |z| phi(z) dz=sqrt(2/pi)",
        },
        "propagation_formula": (
            "||a-a_hat||<=R eps_a; ||b-b_hat||<=R eps_b+R^2 ||K_z|| eps_a"
        ),
        "nominal_diagnostic_propagation": nominal,
        "residual_inflation_study": inflation,
        "pessimistic_target_budget": {
            "target_global_residual_a": target_eps_a,
            "target_global_residual_b": target_eps_b,
            **target,
            "extra_engineering_reserve": engineering_reserve,
            "expected_lower_bound": expected_lower,
        },
        "failure_boundary_with_other_target_fixed": {
            "maximum_eps_a_for_lower_gt_2": allowable_eps_a,
            "maximum_eps_b_for_lower_gt_2": allowable_eps_b,
        },
        "interpretation": (
            "A final global residual may be roughly ten times the diagnostic a-residual "
            "and over one hundred times the diagnostic b-residual while retaining a "
            "pessimistic lower bound above eight."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
