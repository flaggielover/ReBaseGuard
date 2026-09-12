#!/usr/bin/env python3
"""Strict-gate reconstruction of the 96 authoritative cells.

Bounds the scientific exposure of the P4Z RNG address overlap, and of every
other successor-added uncertainty convention, by re-deciding each cell under the
**frozen P4 gate alone**:

    relative discrepancy <= 0.03   AND   |z| <= 4.0
    z computed on Monte Carlo error only:  |e_A - e_B| / hypot(SE_A, SE_B_mc)

The successor line adds a finite-difference truncation term ``T_B`` into
``SE_B = hypot(SE_B_mc, T_B)``.  That term *inflates* the denominator of ``z``
and therefore makes the frozen ``|z| <= 4`` gate easier.  Removing it entirely
is the strictest reading available from the stored artifacts, and it is the
reading under which the exposure of any convention dispute — the K7 instrument
lineage included — can be bounded without rerunning anything.

Each cell is taken from the campaign that `final_coverage.json` records as its
sole authoritative source, so the reconstruction covers exactly the 96 cells and
composes nothing.

NOT RESULT BEARING.  Recomputes from stored adjudication artifacts; produces no
new scientific measurement and re-decides no governed disposition.  It does NOT
constitute the outstanding independent adjudication of the K7 instrument
lineage (B1) — it only bounds what that adjudication can be about.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
SOURCES = {
    "P4Z": CP / "p4z_location_family_feasibility" / "production" / "adjudication.json",
    "P4ZA": CP / "p4za_fullscope_closure" / "production" / "adjudication_p4za.json",
    "P4ZB": CP / "p4zb_skewnormal4_k7" / "production" / "adjudication_p4zb.json",
}
COVERAGE = CP / "p4zb_skewnormal4_k7" / "results" / "final_coverage.json"

FROZEN_RELATIVE_LIMIT = 0.03
FROZEN_Z_LIMIT = 4.0


def cell_key(c: dict) -> tuple:
    return (c["layer"], c["detector"], c["family"], int(c["m"]))


def load_adjudicated() -> dict[str, dict[tuple, dict]]:
    out: dict[str, dict[tuple, dict]] = {}
    for name, path in SOURCES.items():
        doc = json.loads(path.read_text())
        out[name] = {cell_key(c): c for c in doc["cells"] if "correspondence" in c}
    return out


def main() -> int:
    cov = json.loads(COVERAGE.read_text())
    adj = load_adjudicated()

    rows, missing = [], []
    for c in cov["cells"]:
        key, src = cell_key(c), c["authoritative_source"]
        rec = adj.get(src, {}).get(key)
        if rec is None:
            missing.append({"cell": list(key), "source": src})
            continue
        co = rec["correspondence"]
        se_mc = math.hypot(co["se_a"], co["se_b_mc"])
        z_mc = co["absolute_difference"] / se_mc
        rows.append({
            "layer": key[0], "detector": key[1], "family": key[2], "m": key[3],
            "authoritative_source": src,
            "relative_discrepancy": co["relative_discrepancy"],
            "z_as_adjudicated": co["z"],
            "z_monte_carlo_error_only": z_mc,
            "T_B_over_se_b_mc": co["T_B"] / co["se_b_mc"],
            "strict_gate_pass": (co["relative_discrepancy"] <= FROZEN_RELATIVE_LIMIT
                                 and z_mc <= FROZEN_Z_LIMIT),
        })

    assert not missing, f"cells missing an adjudication record: {missing}"
    assert len(rows) == 96, f"expected 96 cells, reconstructed {len(rows)}"

    worst_z = max(rows, key=lambda r: r["z_monte_carlo_error_only"])
    worst_rel = max(rows, key=lambda r: r["relative_discrepancy"])
    doc = {
        "schema": "rebaseguard.p4zr-strict-gate-reconstruction.v1",
        "result_bearing": False,
        "purpose": "bound the scientific exposure of successor-added uncertainty "
                   "conventions, including the RNG address overlap disclosed in "
                   "RNG_ADDRESS_SEPARATION.md",
        "does_not_perform": [
            "the independent adjudication of the K7 instrument lineage (B1)",
            "any re-decision of a governed cell disposition",
            "any new scientific measurement",
        ],
        "gate": {
            "relative_limit": FROZEN_RELATIVE_LIMIT,
            "z_limit": FROZEN_Z_LIMIT,
            "z_statistic": "|e_A - e_B| / hypot(SE_A, SE_B_mc); "
                           "the successor T_B truncation term is excluded",
            "why_stricter": "T_B enters SE_B as hypot(SE_B_mc, T_B) and so "
                            "inflates the z denominator; excluding it can only "
                            "raise |z|",
        },
        "cells_total": len(rows),
        "cells_passing_the_strict_gate": sum(r["strict_gate_pass"] for r in rows),
        "worst_z_monte_carlo_error_only": {
            "value": worst_z["z_monte_carlo_error_only"],
            "cell": f"{worst_z['layer']}/{worst_z['detector']}/{worst_z['family']} m={worst_z['m']}",
            "authoritative_source": worst_z["authoritative_source"],
            "limit": FROZEN_Z_LIMIT,
        },
        "worst_relative_discrepancy": {
            "value": worst_rel["relative_discrepancy"],
            "cell": f"{worst_rel['layer']}/{worst_rel['detector']}/{worst_rel['family']} m={worst_rel['m']}",
            "authoritative_source": worst_rel["authoritative_source"],
            "limit": FROZEN_RELATIVE_LIMIT,
        },
        "cells": sorted(rows, key=lambda r: -r["z_monte_carlo_error_only"]),
    }
    out = NS / "results" / "strict_gate_reconstruction.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"{doc['cells_passing_the_strict_gate']}/{doc['cells_total']} cells pass "
          f"the strict frozen gate")
    print(f"  worst |z| (Monte Carlo error only) = "
          f"{doc['worst_z_monte_carlo_error_only']['value']:.3f}  limit {FROZEN_Z_LIMIT}")
    print(f"  worst relative discrepancy         = "
          f"{doc['worst_relative_discrepancy']['value']:.4f}  limit {FROZEN_RELATIVE_LIMIT}")
    print(f"-> {out.relative_to(NS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
