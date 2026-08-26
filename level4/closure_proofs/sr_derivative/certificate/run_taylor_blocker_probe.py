#!/usr/bin/env python3
"""Reproduce the cancellation-preserving SR residual blocker.

This is an OPEN proof-development probe.  It rigorously encloses the reset
point residual and one complete continuum patch, but it does not claim that
the patch is representative of the global maximum or that a global cover has
been certified.
"""

from __future__ import annotations

import json
import os
import platform
import tempfile
from pathlib import Path

import flint
from flint import arb, ctx

import validated_taylor as vt
from sr_residual_taylor import bound_residual_a_patch

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
CANDIDATE_PATH = RESULTS / "arb_candidate.json"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192


def ball_record(value: arb, digits: int = 60) -> dict[str, str]:
    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def gaussian_phi(value: arb) -> arb:
    return (-(value * value) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def gaussian_cdf(value: arb) -> arb:
    return (arb(1) + (value / arb(2).sqrt()).erf()) / arb(2)


def reset_residuals(
    candidate: dict[str, object], threshold: arb, live_max: arb
) -> tuple[arb, arb]:
    log_a = threshold.log()
    lower = -log_a - arb(1) / arb(2)
    upper = log_a + arb(1) / arb(2)

    def integrand(coefficients: list[list[int]], z_weight: bool):
        def evaluate(z: vt.Jet) -> vt.Jet:
            order = len(z) - 1
            q_plus = vt.softplus(
                vt.add(vt.constant(-arb(1) / arb(2), order), z)
            )
            q_minus = vt.softplus(
                vt.add(
                    vt.constant(-arb(1) / arb(2), order),
                    vt.scale(z, -arb(1)),
                )
            )
            value = vt.evaluate_chebyshev_candidate(
                coefficients,
                scale_bits=int(candidate["scale_bits"]),
                live_max=live_max,
                y_plus=q_plus,
                y_minus=q_minus,
            )
            if z_weight:
                value = vt.multiply(value, z)
            return vt.multiply(value, vt.gaussian_density(z))

        return evaluate

    def at_reset(coefficients: list[list[int]]) -> arb:
        return vt.evaluate_chebyshev_candidate(
            coefficients,
            scale_bits=int(candidate["scale_bits"]),
            live_max=live_max,
            y_plus=vt.constant(arb(0), 0),
            y_minus=vt.constant(arb(0), 0),
        )[0]

    k_a = vt.integrate_with_taylor_remainder(
        integrand(candidate["a"], False),
        lower,
        upper,
        partitions=32,
        order=10,
    )
    kz_a = vt.integrate_with_taylor_remainder(
        integrand(candidate["a"], True),
        lower,
        upper,
        partitions=32,
        order=10,
    )
    k_b = vt.integrate_with_taylor_remainder(
        integrand(candidate["b"], False),
        lower,
        upper,
        partitions=32,
        order=10,
    )
    phi_lower = gaussian_phi(lower)
    phi_upper = gaussian_phi(upper)
    reward_a = phi_upper - phi_lower
    reward_b = (
        gaussian_cdf(lower)
        - lower * phi_lower
        + arb(1)
        - gaussian_cdf(upper)
        + upper * phi_upper
    )
    return (
        at_reset(candidate["a"]) - k_a - reward_a,
        at_reset(candidate["b"]) - k_b - kz_a - reward_b,
    )


def main() -> int:
    candidate = json.loads(CANDIDATE_PATH.read_text())
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        log_a = threshold.log()
        reset_a, reset_b = reset_residuals(candidate, threshold, live_max)

        patch_upper = live_max / arb(64)
        patch = bound_residual_a_patch(
            candidate["a"],
            scale_bits=int(candidate["scale_bits"]),
            live_max=live_max,
            log_a=log_a,
            plus_lower=arb(0),
            plus_upper=patch_upper,
            minus_lower=arb(0),
            minus_upper=patch_upper,
            innovation_partitions=32,
            order=6,
        )

        resolvent = arb(25000) / arb(19)
        kz_bound = (arb(2) / arb.pi()).sqrt()
        gamma_candidate = vt.evaluate_chebyshev_candidate(
            candidate["b"],
            scale_bits=int(candidate["scale_bits"]),
            live_max=live_max,
            y_plus=vt.constant(arb(0), 0),
            y_minus=vt.constant(arb(0), 0),
        )[0]
        maximum_eps_a_if_eps_b_zero = (gamma_candidate - arb(2)) / (
            kz_bound * resolvent * resolvent
        )
        output = {
            "schema": "rebaseguard.sr-taylor-residual-blocker.v1",
            "status": "OPEN",
            "claim": "NO GLOBAL SR RESIDUAL SUPREMUM CERTIFIED",
            "proof_role": "RIGOROUS LOCAL PROBE; NOT A GLOBAL CERTIFICATE",
            "precision_bits": PRECISION_BITS,
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "candidate_sha256": candidate["sha256"],
            "candidate_degree": candidate["degree"],
            "candidate_scale_bits": candidate["scale_bits"],
            "reset_point": {
                "integration_order": 10,
                "innovation_partitions": 32,
                "residual_a": ball_record(reset_a),
                "residual_b": ball_record(reset_b),
            },
            "first_continuum_patch": {
                "domain": "0<=y_plus<=L/64, 0<=y_minus<=L/64",
                "taylor_order": 6,
                "innovation_partitions": 32,
                "polynomial_residual_a_upper": ball_record(patch.polynomial_a),
                "taylor_remainder_a_upper": ball_record(patch.remainder_a),
                "certified_residual_a_upper": ball_record(patch.residual_a),
            },
            "propagation_budget": {
                "resolvent": ball_record(resolvent),
                "K_z_bound": ball_record(kz_bound),
                "maximum_epsilon_a_if_epsilon_b_zero": ball_record(
                    maximum_eps_a_if_eps_b_zero
                ),
                "formula": "(b_hat(0,0)-2)/(K_z_bound*resolvent^2)",
            },
            "blocking_quantity": (
                "The certified total-degree Taylor remainder on the first "
                "continuum patch exceeds the maximum feasible global epsilon_a."
            ),
            "most_plausible_fix": (
                "Replace sparse interval high-derivative remainders with a "
                "Bernstein-bounded local composition and adaptively refine only "
                "innovation-dominant patches; retain the validated point integrator."
            ),
            "sampled_grid_used": False,
            "exact_global_patch_cover": False,
        }
    atomic_json(RESULTS / "sr_taylor_residual_blocker.json", output)
    print("SR Taylor residual probe: OPEN (global remainder not certified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
