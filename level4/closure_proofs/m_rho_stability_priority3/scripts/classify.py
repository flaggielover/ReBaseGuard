#!/usr/bin/env python3
"""Priority-3 stability classifier command line.

Usage:
    classify.py --detector CUSUM --m 5 --rho 0.10
    classify.py --detector SR-witness --m 3 --rho 0.6
    classify.py --gamma 9.0 --rho 0.2            # ad hoc gain, no provenance

With ``--detector`` the gain, its evidence class and (for empirical layers) its
95% interval are taken from ``results/provenance.json``, so the answer carries
the same evidence bookkeeping as the stored map.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_p3_map.classifier import boundary_as_dict, boundary, classify_cell  # noqa: E402
from rebaseguard_p3_map.common import read_json  # noqa: E402
from rebaseguard_p3_map.config import RESULTS  # noqa: E402


def _layers() -> dict:
    prov = read_json(RESULTS / "provenance.json")
    return {layer["detector_short"]: layer for layer in prov["layers"]}


def main() -> None:
    layers = _layers()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--detector", choices=sorted(layers))
    parser.add_argument("--m", type=int)
    parser.add_argument("--gamma", type=float)
    parser.add_argument("--gamma-se", type=float)
    parser.add_argument("--rho", type=float, required=True)
    args = parser.parse_args()

    if args.detector is not None:
        if args.m is None:
            parser.error("--detector requires --m")
        layer = layers[args.detector]
        row = next((r for r in layer["rows"] if r["m"] == args.m), None)
        if row is None:
            parser.error(f"m={args.m} is not supported for {args.detector}; "
                         f"supported: {[r['m'] for r in layer['rows']]}")
        gamma = row["gamma_tilde"]
        interval = tuple(row["gamma_tilde_ci95"]) if row["gamma_tilde_ci95"] else None
        cell = classify_cell(
            args.rho, gamma,
            cell_evidence_class=row["cell_evidence_class"],
            gamma_evidence_class=row["gamma_evidence_class"],
            gamma_se=row["gamma_tilde_se"], gamma_interval=interval,
            gamma_exact=row["gamma_tilde_exact"],
        )
        cell["detector"] = args.detector
        cell["detector_family"] = layer["detector_family"]
        cell["m"] = args.m
        cell["boundary"] = row["boundary"]
    else:
        if args.gamma is None:
            parser.error("supply either --detector/--m or --gamma")
        interval = None
        if args.gamma_se is not None:
            from rebaseguard_p3_map.classifier import normal_interval
            interval = normal_interval(args.gamma, args.gamma_se)
        cell = classify_cell(
            args.rho, args.gamma,
            cell_evidence_class=("THEOREM_PLUS_EMPIRICAL_ESTIMATE"
                                 if interval else "THEOREM_PLUS_SUPPLIED_INPUT"),
            gamma_evidence_class="EMPIRICAL_ONLY" if interval else "SUPPLIED",
            gamma_se=args.gamma_se, gamma_interval=interval,
        )
        cell["detector"] = "ad-hoc"
        cell["boundary"] = boundary_as_dict(
            boundary(args.gamma, args.gamma_se, interval))

    print(json.dumps(cell, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
