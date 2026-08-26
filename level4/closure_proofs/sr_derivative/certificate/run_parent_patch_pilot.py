#!/usr/bin/env python3
"""Test width-1/32 state cells for a scalable SR residual cover."""

from __future__ import annotations

import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from sr_adaptive_residual import certify_adaptive_patch_a

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192

PATCHES = (
    ("easy_interior_parent", (6, 8), (6, 8)),
    ("difficult_plus_boundary_parent", (62, 64), (4, 6)),
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
        live_max = (arb(1) + threshold).log()
        result = certify_adaptive_patch_a(
            candidate["a"],
            scale_bits=candidate["scale_bits"],
            live_max=live_max,
            log_a=threshold.log(),
            normalized_plus=(Fraction(plus[0], 64), Fraction(plus[1], 64)),
            normalized_minus=(Fraction(minus[0], 64), Fraction(minus[1], 64)),
            integration_target=Fraction(35, 10_000_000),
        )
    return name, result


def main() -> int:
    with ProcessPoolExecutor(max_workers=2) as executor:
        certified = dict(executor.map(certify_one, PATCHES))
    checks = {
        "all_innovation_covers_exact": all(
            result["exact_innovation_cover"] for result in certified.values()
        ),
        "sampled_grid_not_used": all(
            result["sampled_grid_used"] is False for result in certified.values()
        ),
    }
    if not all(checks.values()):
        raise ArithmeticError("parent-patch coverage invariant failed")
    parents_pass = all(
        result["status"] == "PATCH_CERTIFIED" for result in certified.values()
    )
    output = {
        "schema": "rebaseguard.sr-parent-patch-pilot.v1",
        "status": "PARENT_PATCHES_PASS" if parents_pass else "PARENT_PATCH_BLOCKED",
        "proof_role": "RIGOROUS SCALING PILOT; NOT A GLOBAL CERTIFICATE",
        "precision_bits": PRECISION_BITS,
        "parallel_workers": 2,
        "integration_target": [35, 10_000_000],
        "patches": certified,
        "checks": checks,
        "global_reachable_cover_complete": False,
    }
    atomic_json(RESULTS / "sr_residual_parent_patch_pilot.json", output)
    print(f"SR parent-patch pilot: {output['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
