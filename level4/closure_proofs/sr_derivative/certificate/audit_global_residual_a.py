#!/usr/bin/env python3
"""Independent fail-closed audit of the global SR a-residual certificate."""

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
FINAL = RESULTS / "sr_residual_global_a.json"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 256
GRID = 64
TARGET = Fraction(5, 1_000_000)
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
    result = set()
    for minus in range(GRID):
        for plus in range(minus, GRID):
            if plus + minus < 69:
                result.add(f"p{plus:02d}_m{minus:02d}")
    return result


def audit_document(document: dict[str, object]) -> dict[str, object]:
    if document.get("status") != "GLOBAL_A_CERTIFIED":
        raise ValueError("certificate status is not GLOBAL_A_CERTIFIED")
    if document.get("sampled_grid_used") is not False:
        raise ValueError("sampled-grid proof metadata is prohibited")
    if document.get("global_reachable_cover_complete") is not True:
        raise ValueError("global reachable cover is not marked complete")
    if document.get("precision_bits") != 192:
        raise ValueError("unexpected producer precision")
    if document.get("candidate_degree") != 16:
        raise ValueError("unexpected candidate degree")

    gaussian = document.get("gaussian_accounting", {})
    if gaussian.get("artificial_truncation_used") is not False:
        raise ValueError("unexpected Gaussian truncation")
    if gaussian.get("omitted_tail_bound") != "0":
        raise ValueError("Gaussian tail accounting is absent or nonzero")
    if "full state-dependent continuation interval" not in gaussian.get(
        "continuation_integration", ""
    ):
        raise ValueError("full continuation integration is not documented")

    algorithm_files = document.get("algorithm_files")
    if not isinstance(algorithm_files, list) or not algorithm_files:
        raise ValueError("algorithm file manifest is absent")
    if independent_algorithm_digest(algorithm_files) != document.get(
        "algorithm_sha256"
    ):
        raise ValueError("algorithm digest mismatch")

    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        exp_sum_cap = (
            arb.const_e()
            * threshold
            * (threshold + arb(1))
            / (arb.const_e() * threshold - (threshold + arb(1)))
        )
        sum_cap = exp_sum_cap.log()
        safe_cap = arb(69) * live_max / arb(64)
        if not sum_cap < safe_cap:
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
            residual = arb(patch["certified_residual_a"])
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
        if not worst_bound.overlaps(arb(document["epsilon_a"])):
            raise ArithmeticError("reported epsilon_a disagrees with worst patch")
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
        reset_residual = reset.get("residual_a", {})
        if reset.get("status") != "RESET_POINT_CERTIFIED":
            raise ValueError("reset point is not certified")
        if not arb(reset_residual.get("upper_enclosure", "nan")) < target:
            raise ArithmeticError("reset residual exceeds target")

    return {
        "status": "AUDIT_PASS",
        "audited_patches": len(patches),
        "worst_patch": worst_key,
        "epsilon_a": document["epsilon_a"],
        "algorithm_sha256": document["algorithm_sha256"],
    }


def main() -> int:
    result = audit_document(json.loads(FINAL.read_text()))
    print(
        f"SR global a audit: PASS ({result['audited_patches']} patches, "
        f"epsilon_a={result['epsilon_a']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
