"""Enumerate ratio effects whose DENOMINATOR is exactly zero.  Post-anchor.

Two reference arms have structurally zero denominators for some metrics:

    B3 (full reuse) has C_acq = C_prop = C_quad = 0  -- it acquires nothing
    B0 (fresh-only) has Wbar = 0                     -- it reuses nothing

A relative effect against a zero denominator is **undefined**, and the
Checkpoint-A code labels it from its (non-finite) bootstrap like any other
effect, which produces a meaningless verdict.  Rather than edit anchored code
after seeing results, this pass ENUMERATES every such entry into its own
artifact.  A test then asserts (a) the enumeration is complete, and (b) no
enumerated entry appears in any BH family or supports any claim in the report.

    python experiments/enumerate_undefined.py
"""
from __future__ import annotations

import json
import math

import _p6r_paths as P                                              # noqa: F401
from _p6r_paths import RESULTS

FIELDS = ("rel", "bca_lo", "bca_hi", "normal_lo", "normal_hi", "boot_sd")


def _nonfinite(e):
    return any(e[f] is None or (isinstance(e[f], float) and not math.isfinite(e[f]))
               for f in FIELDS)


def main():
    out = {"note": ("Ratio effects with an exactly-zero denominator.  These are "
                    "UNDEFINED, not material: B3 acquires no fresh samples so its "
                    "cost denominators are 0, and B0 reuses nothing so its Wbar "
                    "denominator is 0.  The verdict recorded for them in the "
                    "analysis JSON comes from a non-finite bootstrap and must be "
                    "read as UNDEFINED_ZERO_DENOMINATOR.  None of them enters a BH "
                    "family and none supports any claim in CONFIRMATION_REPORT.md."),
           "label": "UNDEFINED_ZERO_DENOMINATOR", "families": {}}
    for fam in ("eval", "replay"):
        f = RESULTS / f"p6r_analysis_{fam}.json"
        if not f.exists():
            continue
        a = json.loads(f.read_text())
        rows = []
        for tag, row in a["cells"].items():
            for blk, comps in row["comparisons"].items():
                for m, e in comps.items():
                    if _nonfinite(e):
                        rows.append({"cell": tag, "comparison": blk, "metric": m,
                                     "recorded_verdict": e["verdict"],
                                     "control_arm": blk.split("@")[0]
                                                       .replace("vs_", "")})
        out["families"][fam] = {
            "n_undefined": len(rows),
            "controls_involved": sorted({r["control_arm"] for r in rows}),
            "metrics_involved": sorted({r["metric"] for r in rows}),
            "entries": rows,
        }
        print(f"{fam}: {len(rows)} undefined ratio effects, controls "
              f"{sorted({r['control_arm'] for r in rows})}")
    (RESULTS / "p6r_undefined_ratios.json").write_text(json.dumps(out, indent=1))
    print("wrote p6r_undefined_ratios.json")


if __name__ == "__main__":
    main()
