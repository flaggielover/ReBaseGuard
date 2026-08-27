#!/usr/bin/env python3
"""Certify representative coupled SR b-residual continuum patches."""

from __future__ import annotations

import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from sr_adaptive_residual import certify_adaptive_patch_b

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192
PATCHES = (
    ("easy_interior", (6, 7), (6, 7)),
    ("difficult_plus_boundary", (62, 63), (4, 5)),
)


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def certify_one(specification: tuple[str, tuple[int, int], tuple[int, int]]):
    name, plus, minus = specification
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        result = certify_adaptive_patch_b(
            candidate["a"],
            candidate["b"],
            scale_bits=candidate["scale_bits"],
            live_max=(arb(1) + threshold).log(),
            log_a=threshold.log(),
            normalized_plus=(Fraction(plus[0], 64), Fraction(plus[1], 64)),
            normalized_minus=(Fraction(minus[0], 64), Fraction(minus[1], 64)),
        )
    return name, result


def main() -> int:
    with ProcessPoolExecutor(max_workers=2) as executor:
        certified = dict(executor.map(certify_one, PATCHES))
    checks = {
        "all_patches_below_5e_minus_3": all(
            patch["status"] == "PATCH_CERTIFIED" for patch in certified.values()
        ),
        "all_innovation_covers_exact": all(
            patch["exact_innovation_cover"] for patch in certified.values()
        ),
        "sampled_grid_not_used": all(
            patch["sampled_grid_used"] is False for patch in certified.values()
        ),
    }
    if not all(checks.values()):
        raise ArithmeticError("adaptive b patch pilot failed")
    output = {
        "schema": "rebaseguard.sr-adaptive-b-pilots.v1",
        "status": "B_PILOT_GATES_PASS",
        "proof_role": "RIGOROUS LOCAL b-RESIDUAL PATCHES; NOT A GLOBAL CERTIFICATE",
        "precision_bits": PRECISION_BITS,
        "patch_target": [5, 1_000],
        "patches": certified,
        "checks": checks,
        "global_reachable_cover_complete": False,
    }
    atomic_json(RESULTS / "sr_residual_adaptive_b_pilots.json", output)
    print("SR adaptive b patch pilots: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
