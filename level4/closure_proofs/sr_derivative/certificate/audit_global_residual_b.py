#!/usr/bin/env python3
"""Independent fail-closed audit of the global SR b-residual certificate."""

from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
CERTIFICATE = CAMPAIGN / "certificate"
FINAL = RESULTS / "sr_residual_global_b.json"
CANDIDATE = RESULTS / "arb_candidate.json"
GLOBAL_A = RESULTS / "sr_residual_global_a.json"
RESET_SOURCE = RESULTS / "sr_taylor_residual_blocker.json"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 256
GRID = 64
TARGET = Fraction(5, 1_000)
EXPECTED_ALGORITHM_FILES = {
    "certify_global_residual_a.py",
    "certify_global_residual_b.py",
    "sr_adaptive_residual.py",
    "sr_bernstein.py",
    "sr_residual_taylor.py",
    "taylor_model.py",
}
KEY_PATTERN = re.compile(r"^p(?P<plus>\d{2})_m(?P<minus>\d{2})$")


def fraction_pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def independent_algorithm_digest(names: list[str]) -> str:
    digest = hashlib.sha256()
    for name in names:
        if Path(name).name != name:
            raise ValueError("algorithm file must be a basename")
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((CERTIFICATE / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def expected_keys() -> set[str]:
    return {
        f"p{plus:02d}_m{minus:02d}"
        for minus in range(GRID)
        for plus in range(minus, GRID)
        if plus + minus < 69
    }


def candidate_at_reset(candidate: dict[str, object]) -> arb:
    """Evaluate the tensor Chebyshev series at x_plus=x_minus=-1."""
    denominator = arb(1 << candidate["scale_bits"])
    numerator = sum(
        coefficient * (-1 if (i + j) % 2 else 1)
        for i, row in enumerate(candidate["b"])
        for j, coefficient in enumerate(row)
    )
    return arb(numerator) / denominator


def audit_document(document: dict[str, object]) -> dict[str, object]:
    if document.get("status") != "GLOBAL_B_CERTIFIED":
        raise ValueError("certificate status is not GLOBAL_B_CERTIFIED")
    if document.get("sampled_grid_used") is not False:
        raise ValueError("sampled-grid proof metadata is prohibited")
    if document.get("global_reachable_cover_complete") is not True:
        raise ValueError("global reachable cover is not marked complete")
    if document.get("precision_bits") != 192:
        raise ValueError("unexpected producer precision")

    gaussian = document.get("gaussian_accounting", {})
    if gaussian.get("artificial_truncation_used") is not False:
        raise ValueError("unexpected Gaussian truncation")
    if gaussian.get("omitted_tail_bound") != "0":
        raise ValueError("Gaussian tail accounting is absent or nonzero")
    if "full state-dependent continuation interval" not in gaussian.get(
        "continuation_integration", ""
    ):
        raise ValueError("full continuation integration is not documented")
    if "r_b = 1 - integral_cont z^2 phi" not in gaussian.get("alarm_region", ""):
        raise ValueError("alarm-region cancellation identity is not documented")

    algorithm_files = document.get("algorithm_files")
    if not isinstance(algorithm_files, list):
        raise ValueError("algorithm file manifest is absent")
    if set(algorithm_files) != EXPECTED_ALGORITHM_FILES:
        raise ValueError("algorithm file manifest is incomplete")
    if independent_algorithm_digest(algorithm_files) != document.get(
        "algorithm_sha256"
    ):
        raise ValueError("algorithm digest mismatch")

    candidate = json.loads(CANDIDATE.read_text())
    coefficients = candidate["b"]
    if not all(
        coefficients[i][j] == coefficients[j][i]
        for i in range(len(coefficients))
        for j in range(len(coefficients))
    ):
        raise ValueError("candidate b is not exactly symmetric")
    if document.get("candidate_sha256") != candidate.get("sha256"):
        raise ValueError("candidate identity mismatch")

    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        exp_sum_cap = (
            arb.const_e()
            * threshold
            * (threshold + arb(1))
            / (arb.const_e() * threshold - (threshold + arb(1)))
        )
        if not exp_sum_cap.log() < arb(69) * live_max / arb(64):
            raise ArithmeticError("independent reachable sum-cap check failed")

        patches = document.get("patches")
        if not isinstance(patches, dict):
            raise ValueError("patch table is absent")
        expected = expected_keys()
        if set(patches) != expected:
            missing = sorted(expected - set(patches))
            extra = sorted(set(patches) - expected)
            raise ValueError(f"patch cover mismatch: missing={missing[:3]} extra={extra[:3]}")

        target = arb(TARGET.numerator) / arb(TARGET.denominator)
        worst_key = None
        worst_bound = None
        total_intervals = 0
        maximum_depth = 0
        interval_counts = []
        for key in sorted(patches):
            match = KEY_PATTERN.fullmatch(key)
            if match is None:
                raise ValueError(f"invalid patch key: {key}")
            plus = int(match.group("plus"))
            minus = int(match.group("minus"))
            patch = patches[key]
            if patch.get("status") != "PATCH_CERTIFIED":
                raise ValueError(f"uncertified patch: {key}")
            if patch.get("exact_innovation_cover") is not True:
                raise ValueError(f"innovation cover is not exact: {key}")
            if patch.get("sampled_grid_used") is not False:
                raise ValueError(f"sampled grid used: {key}")
            if patch.get("trace_included") is not False:
                raise ValueError(f"unexpected compact-certificate trace: {key}")
            if patch.get("normalized_plus") != [
                fraction_pair(Fraction(plus, GRID)),
                fraction_pair(Fraction(plus + 1, GRID)),
            ]:
                raise ValueError(f"plus endpoints disagree with key: {key}")
            if patch.get("normalized_minus") != [
                fraction_pair(Fraction(minus, GRID)),
                fraction_pair(Fraction(minus + 1, GRID)),
            ]:
                raise ValueError(f"minus endpoints disagree with key: {key}")
            components = sum(
                (
                    arb(patch[field])
                    for field in (
                        "polynomial_bernstein",
                        "direct_remainder",
                        "reward_remainder",
                        "integration_remainder",
                    )
                ),
                arb(0),
            )
            residual = arb(patch["certified_residual_b"])
            if not components.overlaps(residual):
                raise ArithmeticError(f"component sum does not overlap residual: {key}")
            if not residual < target:
                raise ArithmeticError(f"patch exceeds engineering target: {key}")
            if worst_bound is None or residual.upper() > worst_bound.upper():
                worst_key = key
                worst_bound = residual
            count = patch.get("final_intervals")
            depth = patch.get("maximum_depth")
            if not isinstance(count, int) or not isinstance(depth, int):
                raise ValueError(f"subdivision metadata absent: {key}")
            interval_counts.append(count)
            total_intervals += count
            maximum_depth = max(maximum_depth, depth)

        if worst_key != document.get("worst_patch"):
            raise ValueError("reported worst patch disagrees with independent maximum")
        if not worst_bound.overlaps(arb(document["epsilon_b"])):
            raise ArithmeticError("reported epsilon_b disagrees with worst patch")
        statistics = document.get("subdivision_statistics", {})
        expected_statistics = {
            "maximum_innovation_depth": maximum_depth,
            "minimum_innovation_intervals": min(interval_counts),
            "maximum_innovation_intervals": max(interval_counts),
            "total_innovation_intervals": total_intervals,
        }
        for field, value in expected_statistics.items():
            if statistics.get(field) != value:
                raise ValueError(f"subdivision statistic mismatch: {field}")

        reset = document.get("reset_point", {})
        source_reset = json.loads(RESET_SOURCE.read_text())["reset_point"]["residual_b"]
        if reset.get("status") != "RESET_POINT_CERTIFIED":
            raise ValueError("reset point is not certified")
        if reset.get("residual_b") != source_reset:
            raise ValueError("reset residual disagrees with its frozen source")
        if not arb(source_reset["ball"]) < target:
            raise ArithmeticError("reset residual exceeds target")

        propagation = document.get("propagation", {})
        epsilon_a = arb(json.loads(GLOBAL_A.read_text())["epsilon_a"])
        epsilon_b = arb(document["epsilon_b"])
        resolvent = arb(25000) / arb(19)
        kz_norm = (arb(2) / arb.pi()).sqrt()
        gamma_candidate = candidate_at_reset(candidate)
        propagated_a = kz_norm * resolvent * resolvent * epsilon_a
        propagated_b = resolvent * epsilon_b
        total_error = propagated_a + propagated_b
        gamma_lower = gamma_candidate - total_error
        gamma_upper = gamma_candidate + total_error
        recomputed = {
            "gamma_candidate": gamma_candidate,
            "kz_operator_norm_bound": kz_norm,
            "epsilon_a": epsilon_a,
            "epsilon_b": epsilon_b,
            "propagated_a_error": propagated_a,
            "propagated_b_error": propagated_b,
            "total_error_radius": total_error,
            "lower_endpoint_margin_above_two": gamma_lower - arb(2),
        }
        if propagation.get("resolvent_bound") != "25000/19":
            raise ValueError("unexpected resolvent bound")
        for field, value in recomputed.items():
            if not value.overlaps(arb(propagation.get(field, "nan"))):
                raise ArithmeticError(f"propagation field disagrees: {field}")
        reported_interval = propagation.get("gamma_interval", {})
        if not isinstance(reported_interval, dict):
            raise ValueError("Gamma interval endpoint enclosures are absent")
        for field, value in (
            ("lower_endpoint_enclosure", gamma_lower),
            ("upper_endpoint_enclosure", gamma_upper),
        ):
            if not value.overlaps(arb(reported_interval.get(field, "nan"))):
                raise ArithmeticError(f"Gamma interval endpoint disagrees: {field}")
        if propagation.get("status") != "PROPAGATION_CERTIFIED":
            raise ValueError("propagation status is not certified")
        if propagation.get("strict_lower_endpoint_above_two") is not True:
            raise ValueError("strict Gamma lower-bound flag is absent")
        if not gamma_lower.lower() > arb(2):
            raise ArithmeticError("independent Gamma interval is not above two")

    return {
        "status": "AUDIT_PASS",
        "audited_patches": len(patches),
        "worst_patch": worst_key,
        "epsilon_b": document["epsilon_b"],
        "gamma_interval": propagation["gamma_interval"],
        "algorithm_sha256": document["algorithm_sha256"],
    }


def main() -> int:
    result = audit_document(json.loads(FINAL.read_text()))
    print(
        f"SR global b audit: PASS ({result['audited_patches']} patches, "
        f"epsilon_b={result['epsilon_b']}, Gamma={result['gamma_interval']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
