#!/usr/bin/env python3
"""Run or replay the frozen D4 numerical campaign."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_d4.direct_map import run as run_direct  # noqa: E402
from rebaseguard_d4.gamma_grid import run as run_gamma  # noqa: E402
from rebaseguard_d4.operational import run as run_operational  # noqa: E402
from rebaseguard_d4.phase_map import build as build_phase_map  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=("gamma", "direct", "phase-map", "operational", "through-map", "all"),
    )
    parser.add_argument("--recompute", action="store_true")
    args = parser.parse_args()
    resume = not args.recompute
    if args.stage in {"gamma", "through-map", "all"}:
        run_gamma(resume=resume)
    if args.stage in {"direct", "through-map", "all"}:
        run_direct(resume=resume)
    if args.stage in {"phase-map", "through-map", "all"}:
        build_phase_map()
    if args.stage in {"operational", "all"}:
        run_operational(resume=resume)


if __name__ == "__main__":
    main()
