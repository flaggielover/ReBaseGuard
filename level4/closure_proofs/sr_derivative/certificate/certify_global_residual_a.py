#!/usr/bin/env python3
"""Resumable rigorous global continuum certificate for the SR a-residual."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from sr_adaptive_residual import certify_adaptive_patch_a

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
CHECKPOINT = RESULTS / "sr_residual_global_a_checkpoint.json"
FINAL = RESULTS / "sr_residual_global_a.json"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192
GRID = 64
SAFE_SUM_CAP_NUMERATOR = 69
SAFE_SUM_CAP_DENOMINATOR = 64
EXPECTED_FUNDAMENTAL_CELLS = 1210
ALGORITHM_FILES = (
    "certify_global_residual_a.py",
    "sr_adaptive_residual.py",
    "sr_bernstein.py",
    "sr_residual_taylor.py",
    "taylor_model.py",
)

_candidate: dict[str, object] | None = None
_live_max: arb | None = None
_log_a: arb | None = None


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def algorithm_digest() -> str:
    digest = hashlib.sha256()
    certificate = CAMPAIGN / "certificate"
    for name in ALGORITHM_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((certificate / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def cells() -> list[tuple[int, int]]:
    """Symmetry-reduced cells meeting the rational sum-cap superset."""

    return [
        (plus, minus)
        for plus in range(GRID)
        for minus in range(plus + 1)
        if plus + minus <= SAFE_SUM_CAP_NUMERATOR - 1
    ]


def cell_key(cell: tuple[int, int]) -> str:
    return f"p{cell[0]:02d}_m{cell[1]:02d}"


def initialize_worker() -> None:
    global _candidate, _live_max, _log_a
    _candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    ctx.prec = PRECISION_BITS
    threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
    _live_max = (arb(1) + threshold).log()
    _log_a = threshold.log()


def certify_cell(cell: tuple[int, int]) -> tuple[str, dict[str, object]]:
    if _candidate is None or _live_max is None or _log_a is None:
        raise RuntimeError("worker was not initialized")
    plus, minus = cell
    result = certify_adaptive_patch_a(
        _candidate["a"],
        scale_bits=_candidate["scale_bits"],
        live_max=_live_max,
        log_a=_log_a,
        normalized_plus=(Fraction(plus, GRID), Fraction(plus + 1, GRID)),
        normalized_minus=(Fraction(minus, GRID), Fraction(minus + 1, GRID)),
        include_trace=False,
    )
    return cell_key(cell), result


def geometry_and_algebra_checks(candidate: dict[str, object]) -> dict[str, bool]:
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        denominator = arb(1) - (threshold + arb(1)) / (
            arb.const_e() * threshold
        )
        sum_cap = ((threshold + arb(1)) / denominator).log()
        rational_cap = (
            arb(SAFE_SUM_CAP_NUMERATOR)
            / arb(SAFE_SUM_CAP_DENOMINATOR)
            * live_max
        )
    coefficient_a = candidate["a"]
    antisymmetric = all(
        coefficient_a[i][j] == -coefficient_a[j][i]
        for i in range(len(coefficient_a))
        for j in range(len(coefficient_a))
    )
    enumerated = cells()
    return {
        "candidate_a_exactly_antisymmetric": antisymmetric,
        "reachable_sum_cap_below_69_over_64_live_max": sum_cap < rational_cap,
        "fundamental_cell_count_is_1210": len(enumerated)
        == EXPECTED_FUNDAMENTAL_CELLS,
        "all_cells_in_fundamental_half": all(i >= j for i, j in enumerated),
        "all_cells_meet_integer_sum_cap": all(
            i + j <= SAFE_SUM_CAP_NUMERATOR - 1 for i, j in enumerated
        ),
        "cell_keys_unique": len({cell_key(cell) for cell in enumerated})
        == len(enumerated),
    }


def new_checkpoint(candidate: dict[str, object]) -> dict[str, object]:
    checks = geometry_and_algebra_checks(candidate)
    if not all(checks.values()):
        raise ArithmeticError("global cover geometry or symmetry check failed")
    return {
        "schema": "rebaseguard.sr-global-residual-a-checkpoint.v1",
        "status": "GLOBAL_A_IN_PROGRESS",
        "proof_role": "RESUMABLE PRODUCER CHECKPOINT; NOT A COMPLETE CERTIFICATE",
        "precision_bits": PRECISION_BITS,
        "candidate_sha256": candidate["sha256"],
        "grid": GRID,
        "safe_normalized_sum_cap": [
            SAFE_SUM_CAP_NUMERATOR,
            SAFE_SUM_CAP_DENOMINATOR,
        ],
        "expected_fundamental_cells": EXPECTED_FUNDAMENTAL_CELLS,
        "cover_checks": checks,
        "patches": {},
    }


def load_checkpoint(candidate: dict[str, object]) -> dict[str, object]:
    if not CHECKPOINT.exists():
        return new_checkpoint(candidate)
    checkpoint = json.loads(CHECKPOINT.read_text())
    expected = new_checkpoint(candidate)
    for field in (
        "schema",
        "precision_bits",
        "candidate_sha256",
        "grid",
        "safe_normalized_sum_cap",
        "expected_fundamental_cells",
        "cover_checks",
    ):
        if checkpoint.get(field) != expected[field]:
            raise ValueError(f"incompatible global checkpoint field: {field}")
    allowed = {cell_key(cell) for cell in cells()}
    if not set(checkpoint["patches"]) <= allowed:
        raise ValueError("checkpoint contains an out-of-cover patch")
    return checkpoint


def finalize(checkpoint: dict[str, object]) -> dict[str, object] | None:
    patches = checkpoint["patches"]
    if len(patches) != EXPECTED_FUNDAMENTAL_CELLS:
        return None
    if not all(patch["status"] == "PATCH_CERTIFIED" for patch in patches.values()):
        checkpoint["status"] = "GLOBAL_A_BLOCKED"
        atomic_json(CHECKPOINT, checkpoint)
        return None
    worst_key = max(
        patches,
        key=lambda key: float(arb(patches[key]["certified_residual_a"]).upper()),
    )
    reset = json.loads((RESULTS / "sr_taylor_residual_blocker.json").read_text())[
        "reset_point"
    ]["residual_a"]
    maximum_depth = max(patch["maximum_depth"] for patch in patches.values())
    interval_counts = [patch["final_intervals"] for patch in patches.values()]
    component_fields = (
        "polynomial_bernstein",
        "direct_remainder",
        "reward_remainder",
        "integration_remainder",
    )
    component_maxima = {}
    for field in component_fields:
        key = max(
            patches,
            key=lambda patch_key: float(arb(patches[patch_key][field]).upper()),
        )
        component_maxima[field] = {"patch": key, "bound": patches[key][field]}
    result = dict(checkpoint)
    result.update(
        {
            "schema": "rebaseguard.sr-global-residual-a.v1",
            "status": "GLOBAL_A_CERTIFIED",
            "proof_role": "RIGOROUS GLOBAL CONTINUUM a-RESIDUAL PRODUCER CERTIFICATE",
            "completed_fundamental_cells": len(patches),
            "worst_patch": worst_key,
            "epsilon_a": patches[worst_key]["certified_residual_a"],
            "reset_point": {
                "status": "RESET_POINT_CERTIFIED",
                "residual_a": reset,
                "source": "results/sr_taylor_residual_blocker.json",
            },
            "subdivision_statistics": {
                "maximum_innovation_depth": maximum_depth,
                "minimum_innovation_intervals": min(interval_counts),
                "maximum_innovation_intervals": max(interval_counts),
                "total_innovation_intervals": sum(interval_counts),
                "component_maxima": component_maxima,
            },
            "gaussian_accounting": {
                "artificial_truncation_used": False,
                "omitted_tail_bound": "0",
                "continuation_integration": (
                    "exact t in [-1,1] affine image of the full state-dependent "
                    "continuation interval"
                ),
                "alarm_region": "included analytically in reward_a",
            },
            "candidate_degree": json.loads(
                (RESULTS / "arb_candidate.json").read_text()
            )["degree"],
            "algorithm_files": list(ALGORITHM_FILES),
            "algorithm_sha256": algorithm_digest(),
            "global_reachable_cover_complete": True,
            "sampled_grid_used": False,
        }
    )
    atomic_json(FINAL, result)
    checkpoint["status"] = "GLOBAL_A_COMPLETE"
    atomic_json(CHECKPOINT, checkpoint)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument(
        "--limit",
        type=int,
        help="certify at most this many new cells; leaves an OPEN checkpoint",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    checkpoint = load_checkpoint(candidate)
    remaining = [
        cell for cell in cells() if cell_key(cell) not in checkpoint["patches"]
    ]
    if args.limit is not None:
        remaining = remaining[: args.limit]
    if remaining and args.workers == 1:
        initialize_worker()
        for cell in remaining:
            key, result = certify_cell(cell)
            checkpoint["patches"][key] = result
            atomic_json(CHECKPOINT, checkpoint)
            print(
                f"{len(checkpoint['patches'])}/{EXPECTED_FUNDAMENTAL_CELLS} "
                f"{key} {result['status']} {result['certified_residual_a']}",
                flush=True,
            )
    elif remaining:
        with ProcessPoolExecutor(
            max_workers=args.workers, initializer=initialize_worker
        ) as executor:
            futures = {executor.submit(certify_cell, cell): cell for cell in remaining}
            for future in as_completed(futures):
                key, result = future.result()
                checkpoint["patches"][key] = result
                atomic_json(CHECKPOINT, checkpoint)
                print(
                    f"{len(checkpoint['patches'])}/{EXPECTED_FUNDAMENTAL_CELLS} "
                    f"{key} {result['status']} {result['certified_residual_a']}",
                    flush=True,
                )
    final = finalize(checkpoint)
    if final is None:
        print(
            f"SR global a residual: OPEN checkpoint "
            f"{len(checkpoint['patches'])}/{EXPECTED_FUNDAMENTAL_CELLS}"
        )
    else:
        print(f"SR global a residual: CERTIFIED {final['epsilon_a']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
