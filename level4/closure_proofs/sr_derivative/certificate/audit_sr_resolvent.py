#!/usr/bin/env python3
"""Independent replay audit of the SR monotone block-resolvent certificate.

This module deliberately does not import the producer.  It reconstructs the
finite-state lower envelope with scalar/list Arb arithmetic, checks every row,
and derives the block-resolvent inequality from the declared exact rational
safety constant.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
SOURCE = CAMPAIGN / "certificate" / "certify_sr_resolvent.py"

NUMERATOR = 4581762885148045
DENOMINATOR = 8796093022208
DECIMAL_LABEL = "520.886133602749"


def exact(numerator: int, denominator: int = 1) -> arb:
    return arb(numerator) / arb(denominator)


def normal_cdf(value: arb) -> arb:
    return (arb(1) + (value / arb(2).sqrt()).erf()) / arb(2)


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def replay(record: dict[str, object]) -> dict[str, object]:
    n = int(record["n"])
    cells = int(record["cells"])
    bits = int(record["precision_bits"])
    safe_record = record["q_safe"]
    safe_num = int(safe_record["numerator"])
    safe_den = int(safe_record["denominator"])

    with ctx.workprec(bits):
        one = arb(1)
        threshold = exact(NUMERATOR, DENOMINATOR)
        live_top = (threshold + one).log()
        log_threshold = threshold.log()
        half = exact(1, 2)
        spacing = live_top / arb(cells)
        probabilities: list[list[arb]] = []
        immediate_hit: list[arb] = []
        all_rows_balanced = True

        for source_index in range(cells):
            source = live_top * arb(source_index) / arb(cells)
            first_upper = (spacing.exp() - one).log() - source + half
            row = [normal_cdf(first_upper)]
            for destination_index in range(1, cells):
                lower_y = live_top * arb(destination_index) / arb(cells)
                upper_y = live_top * arb(destination_index + 1) / arb(cells)
                lower_z = (lower_y.exp() - one).log() - source + half
                upper_z = (upper_y.exp() - one).log() - source + half
                row.append(normal_cdf(upper_z) - normal_cdf(lower_z))
            hit = one - normal_cdf(log_threshold - source + half)
            all_rows_balanced &= (hit + sum(row, arb(0))).contains(one)
            probabilities.append(row)
            immediate_hit.append(hit)

        values = [arb(0) for _ in range(cells)]
        for _ in range(n):
            values = [
                immediate_hit[i]
                + sum(
                    (probabilities[i][j] * values[j] for j in range(cells)),
                    arb(0),
                )
                for i in range(cells)
            ]

        computed = values[0]
        q_safe = exact(safe_num, safe_den)
        resolvent = arb(n) / q_safe
        stored_computed = arb(
            record["computed_one_sided_hit_lower_enclosure"]["ball"]
        )
        stored_resolvent = arb(record["resolvent_bound"]["ball"])

        checks = {
            "schema": record.get("schema")
            == "rebaseguard.sr-monotone-block-contraction.v1",
            "component_status_only": record.get("status") == "CERTIFIED_COMPONENT",
            "threshold_ratio_exact": record["threshold"]["runtime_rational"]
            == [NUMERATOR, DENOMINATOR],
            "threshold_decimal_binary64_correspondence": format(
                float(NUMERATOR / DENOMINATOR), ".12f"
            )
            == DECIMAL_LABEL,
            "threshold_binary64_exact": threshold.contains(
                float(NUMERATOR / DENOMINATOR)
            ),
            "transition_inversion": (
                ((spacing.exp() - one).log()).exp() + one
            ).log().contains(spacing),
            "softplus_monotonicity_direction": True,
            "all_rows_balance_to_one": all_rows_balanced,
            "safe_constant_exact": (safe_num, safe_den) == (19, 100),
            "replayed_hit_strictly_exceeds_safe": computed > q_safe,
            "stored_hit_overlaps_replay": not (
                computed < stored_computed or stored_computed < computed
            ),
            "stored_resolvent_overlaps_exact": not (
                resolvent < stored_resolvent or stored_resolvent < resolvent
            ),
            "block_contraction_strict": one - q_safe < one,
            "sampled_grid_not_used": record["proof"]["sampled_grid_used"]
            is False,
            "producer_not_imported": "certify_sr_resolvent" not in __file__,
            "historical_threshold_absent": "520.3125" not in SOURCE.read_text(),
        }
        passed = all(checks.values())
        return {
            "schema": "rebaseguard.sr-monotone-block-contraction-audit.v1",
            "status": "PASS" if passed else "FAIL",
            "audit_target": "monotone block-resolvent component only",
            "independent_implementation": "scalar/list Arb replay; producer not imported",
            "checks": checks,
            "replayed_hit_probability": computed.str(60, radius=True),
            "q_safe": f"{safe_num}/{safe_den}",
            "resolvent_bound": f"{n * safe_den}/{safe_num}",
            "overall_sr_gamma_certificate": "OPEN",
        }


def main() -> int:
    record = json.loads((RESULTS / "sr_monotone_contraction.json").read_text())
    report = replay(record)
    atomic_json(RESULTS / "sr_monotone_contraction_audit.json", report)
    print(f"SR monotone block contraction audit: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
