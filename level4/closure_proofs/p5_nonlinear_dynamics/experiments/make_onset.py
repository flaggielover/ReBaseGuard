#!/usr/bin/env python3
"""Bimodality onset: the zero crossing of the per-replicate density contrast."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, P3                            # noqa: E402

t3 = json.loads((P3 / "results" / "boundary_table.json").read_text())
RC = {(r["detector_short"].lower(), int(r["m"])): r["rho_crit"]
      for r in t3["rows"] if r["layer"].startswith("GAUSSIAN")}

rows = []
for f in ("density.json", "density_crossover.json"):
    if (RESULTS / f).exists():
        rows += json.loads((RESULTS / f).read_text())["rows"]

out = {}
for det, m in sorted({(r["detector"], r["m"]) for r in rows}):
    r = sorted([x for x in rows if x["detector"] == det and x["m"] == m],
               key=lambda x: x["rho"])
    c = [(x["rho"], x["contrast_mean"]) for x in r]
    onset = None
    for a, b in zip(c, c[1:]):
        if a[1] < 0 <= b[1]:
            onset = a[0] + (b[0] - a[0]) * (-a[1]) / (b[1] - a[1])
    rc = RC[(det, m)]
    out[f"{det}_m{m}"] = {"onset": onset, "rho_crit": rc,
                          "over_rhoc": onset / rc if onset else None,
                          "n_rho": len(r)}
    print(f"{det:5s} m={m}: onset rho = {onset}, = "
          f"{onset/rc if onset else float('nan'):.1f} x rho_c")
(RESULTS / "bimodality_onset.json").write_text(json.dumps(out, indent=1))
print("wrote bimodality_onset.json")
