#!/usr/bin/env python3
"""Resumable global SR b-residual certificate and coupled propagation."""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from certify_global_residual_a import (
    A_DENOMINATOR,
    A_NUMERATOR,
    EXPECTED_FUNDAMENTAL_CELLS,
    PRECISION_BITS,
    atomic_json,
    cell_key,
    cells,
    geometry_and_algebra_checks,
)
from sr_adaptive_residual import certify_adaptive_patch_b
from taylor_model import Model, evaluate_candidate

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
CHECKPOINT = RESULTS / "sr_residual_global_b_checkpoint.json"
FINAL = RESULTS / "sr_residual_global_b.json"
PATCH_TARGET = Fraction(5, 1_000)
ALGORITHM_FILES = (
    "certify_global_residual_a.py",
    "certify_global_residual_b.py",
    "sr_adaptive_residual.py",
    "sr_bernstein.py",
    "sr_residual_taylor.py",
    "taylor_model.py",
)

_candidate: dict[str, object] | None = None
_live_max: arb | None = None
_log_a: arb | None = None


def algorithm_digest() -> str:
    digest = hashlib.sha256()
    certificate = CAMPAIGN / "certificate"
    for name in ALGORITHM_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((certificate / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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
    result = certify_adaptive_patch_b(
        _candidate["a"],
        _candidate["b"],
        scale_bits=_candidate["scale_bits"],
        live_max=_live_max,
        log_a=_log_a,
        normalized_plus=(Fraction(plus, 64), Fraction(plus + 1, 64)),
        normalized_minus=(Fraction(minus, 64), Fraction(minus + 1, 64)),
        include_trace=False,
    )
    return cell_key(cell), result


def cover_checks(candidate: dict[str, object]) -> dict[str, bool]:
    checks = geometry_and_algebra_checks(candidate)
    coefficient_b = candidate["b"]
    checks["candidate_b_exactly_symmetric"] = all(
        coefficient_b[i][j] == coefficient_b[j][i]
        for i in range(len(coefficient_b))
        for j in range(len(coefficient_b))
    )
    return checks


def new_checkpoint(candidate: dict[str, object]) -> dict[str, object]:
    checks = cover_checks(candidate)
    if not all(checks.values()):
        raise ArithmeticError("global b cover geometry or symmetry check failed")
    return {
        "schema": "rebaseguard.sr-global-residual-b-checkpoint.v1",
        "status": "GLOBAL_B_IN_PROGRESS",
        "proof_role": "RESUMABLE PRODUCER CHECKPOINT; NOT A COMPLETE CERTIFICATE",
        "precision_bits": PRECISION_BITS,
        "candidate_sha256": candidate["sha256"],
        "grid": 64,
        "safe_normalized_sum_cap": [69, 64],
        "patch_target": [PATCH_TARGET.numerator, PATCH_TARGET.denominator],
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
        "patch_target",
        "expected_fundamental_cells",
        "cover_checks",
    ):
        if checkpoint.get(field) != expected[field]:
            raise ValueError(f"incompatible global b checkpoint field: {field}")
    allowed = {cell_key(cell) for cell in cells()}
    if not set(checkpoint["patches"]) <= allowed:
        raise ValueError("global b checkpoint contains an out-of-cover patch")
    return checkpoint


def propagation(epsilon_b: arb, candidate: dict[str, object]) -> dict[str, object]:
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        gamma_candidate = evaluate_candidate(
            candidate["b"],
            candidate["scale_bits"],
            live_max,
            Model.constant(arb(0), 2, 0),
            Model.constant(arb(0), 2, 0),
        ).constant_term
        epsilon_a = arb(
            json.loads((RESULTS / "sr_residual_global_a.json").read_text())[
                "epsilon_a"
            ]
        )
        resolvent = arb(25000) / arb(19)
        kz_norm = (arb(2) / arb.pi()).sqrt()
        propagated_a = kz_norm * resolvent * resolvent * epsilon_a
        propagated_b = resolvent * epsilon_b
        total = propagated_a + propagated_b
        radius = total.upper()
        gamma_interval = (gamma_candidate - radius).union(gamma_candidate + radius)
        return {
            "status": (
                "PROPAGATION_CERTIFIED"
                if gamma_interval.lower() > arb(2)
                else "PROPAGATION_BLOCKED"
            ),
            "gamma_candidate": gamma_candidate.str(60, radius=True),
            "resolvent_bound": "25000/19",
            "kz_operator_norm_bound": kz_norm.str(60, radius=True),
            "epsilon_a": epsilon_a.str(60, radius=True),
            "epsilon_b": epsilon_b.str(60, radius=True),
            "propagated_a_error": propagated_a.str(60, radius=True),
            "propagated_b_error": propagated_b.str(60, radius=True),
            "total_error_radius": total.str(60, radius=True),
            "gamma_interval": gamma_interval.str(60, radius=True),
            "strict_lower_endpoint_above_two": gamma_interval.lower() > arb(2),
            "lower_endpoint_margin_above_two": (
                gamma_interval.lower() - arb(2)
            ).str(60, radius=True),
        }


def finalize(
    checkpoint: dict[str, object], candidate: dict[str, object]
) -> dict[str, object] | None:
    patches = checkpoint["patches"]
    if len(patches) != EXPECTED_FUNDAMENTAL_CELLS:
        return None
    if not all(patch["status"] == "PATCH_CERTIFIED" for patch in patches.values()):
        checkpoint["status"] = "GLOBAL_B_BLOCKED"
        atomic_json(CHECKPOINT, checkpoint)
        return None
    worst_key = max(
        patches,
        key=lambda key: float(arb(patches[key]["certified_residual_b"]).upper()),
    )
    epsilon_b = arb(patches[worst_key]["certified_residual_b"])
    reset = json.loads((RESULTS / "sr_taylor_residual_blocker.json").read_text())[
        "reset_point"
    ]["residual_b"]
    counts = [patch["final_intervals"] for patch in patches.values()]
    result = dict(checkpoint)
    result.update(
        {
            "schema": "rebaseguard.sr-global-residual-b.v1",
            "status": "GLOBAL_B_CERTIFIED",
            "proof_role": (
                "RIGOROUS GLOBAL CONTINUUM b-RESIDUAL AND COUPLED PROPAGATION "
                "PRODUCER CERTIFICATE"
            ),
            "completed_fundamental_cells": len(patches),
            "worst_patch": worst_key,
            "epsilon_b": patches[worst_key]["certified_residual_b"],
            "reset_point": {
                "status": "RESET_POINT_CERTIFIED",
                "residual_b": reset,
                "source": "results/sr_taylor_residual_blocker.json",
            },
            "subdivision_statistics": {
                "maximum_innovation_depth": max(
                    patch["maximum_depth"] for patch in patches.values()
                ),
                "minimum_innovation_intervals": min(counts),
                "maximum_innovation_intervals": max(counts),
                "total_innovation_intervals": sum(counts),
            },
            "gaussian_accounting": {
                "artificial_truncation_used": False,
                "omitted_tail_bound": "0",
                "continuation_integration": (
                    "exact t in [-1,1] affine image of the full state-dependent "
                    "continuation interval"
                ),
                "alarm_region": (
                    "included by the exact identity r_b = 1 - integral_cont z^2 phi"
                ),
            },
            "algorithm_files": list(ALGORITHM_FILES),
            "algorithm_sha256": algorithm_digest(),
            "global_reachable_cover_complete": True,
            "sampled_grid_used": False,
            "propagation": propagation(epsilon_b, candidate),
        }
    )
    atomic_json(FINAL, result)
    checkpoint["status"] = "GLOBAL_B_COMPLETE"
    atomic_json(CHECKPOINT, checkpoint)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--limit", type=int)
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
                f"{key} {result['status']} {result['certified_residual_b']}",
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
                    f"{key} {result['status']} {result['certified_residual_b']}",
                    flush=True,
                )
    final = finalize(checkpoint, candidate)
    if final is None:
        print(
            f"SR global b residual: OPEN checkpoint "
            f"{len(checkpoint['patches'])}/{EXPECTED_FUNDAMENTAL_CELLS}"
        )
    else:
        print(
            f"SR global b residual: CERTIFIED {final['epsilon_b']} "
            f"({final['propagation']['status']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
