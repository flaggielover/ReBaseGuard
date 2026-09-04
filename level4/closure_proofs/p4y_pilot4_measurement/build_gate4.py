#!/usr/bin/env python3
"""Apply the frozen Pilot-4 feasibility criterion.

No threshold, band, grid or ordering is chosen here; all are frozen in
PILOT4_PREREGISTRATION.md and `src/p4y_pilot4/design4.py`.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))

from p4y_pilot4.design4 import (  # noqa: E402
    ACCURACY_FACTOR, BETA, BLOCK_SIZES, CONTROL_KEYS, HEAVY_KEYS,
    MAX_PRODUCTION_REFERENCE_HOURS, TARGET_PROBABILITY,
)

R = ROOT / "results"


def load(n):
    p = R / f"{n}.json"
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    master, ref = load("master"), load("reference")
    if master is None:
        raise SystemExit("run master first")
    by = {s["stratum"]: s for s in master["strata"]}

    # ---------------------------------------------------------- benchmark
    bench = {}
    for b in BLOCK_SIZES:
        heavy_here = [k for k in HEAVY_KEYS if str(b) in by[k]["by_block_size"]]
        ctrl_here = [k for k in CONTROL_KEYS if str(b) in by[k]["by_block_size"]]
        rows = {k: by[k]["by_block_size"][str(b)] for k in heavy_here + ctrl_here}
        bench[b] = {
            "heavy_strata": heavy_here, "control_strata": ctrl_here,
            "admissible_heavy": all(rows[k]["benchmark_admissible"]
                                    for k in heavy_here),
            "admissible_control": all(rows[k]["benchmark_admissible"]
                                      for k in ctrl_here) if ctrl_here else None,
            "per_stratum": {k: {
                "theta_benchmark": rows[k]["theta_benchmark"],
                "split": rows[k]["independent_pool_spread"],
                "prefix": rows[k]["prefix_full_over_half"],
                "top1": rows[k]["concentration"]["top1"],
                "top5": rows[k]["concentration"]["top5"],
                "checks": rows[k]["admissible_checks"],
                "admissible": rows[k]["benchmark_admissible"]} for k in rows},
        }
    out = {"schema": "rebaseguard.p4y-pilot4-gate.v1", "binding": False,
           "accuracy_factor": ACCURACY_FACTOR,
           "target_probability": TARGET_PROBABILITY, "beta": BETA,
           "benchmark": bench,
           "any_admissible_block_size": any(v["admissible_heavy"]
                                            for v in bench.values()),
           "master_stopped": master["stopped"]}

    print("BENCHMARK ADMISSIBILITY (frozen: split<=1.25, prefix in "
          "[0.870,1.150], top1<=0.10, top5<=0.30)")
    for b in BLOCK_SIZES:
        print(f"  b = {b:>9d}   heavy admissible: "
              f"{bench[b]['admissible_heavy']}")
        for k, v in bench[b]["per_stratum"].items():
            bad = [n for n, ok in v["checks"].items() if not ok]
            print(f"    {k:4s} theta={v['theta_benchmark']:.5f} "
                  f"split={v['split']:6.3f} prefix={v['prefix']:6.3f} "
                  f"top1={v['top1']:6.3f} top5={v['top5']:6.3f} "
                  f"-> {'ADMISSIBLE' if v['admissible'] else 'REJECTED ' + str(bad)}")

    # ---------------------------------------------------------- accuracy
    if ref:
        cand = {}
        for s in ref["strata"]:
            for c in s["candidates"]:
                cand.setdefault((c["block_paths"], c["bref"]), {})[s["stratum"]] = c
        rows = []
        for (b, bref), per in sorted(cand.items()):
            heavy = {k: v for k, v in per.items() if k in HEAVY_KEYS}
            ctrl = {k: v for k, v in per.items() if k in CONTROL_KEYS}
            min_lb = min((v["lower_bound"] for v in heavy.values()),
                         default=math.nan)
            ok = {
                "A_benchmark_admissible": bench[b]["admissible_heavy"],
                "D_lower_bound": min_lb >= TARGET_PROBABILITY,
                "E_affordable": all(v["affordable"] for v in heavy.values()),
            }
            rows.append({
                "block_paths": b, "bref": bref,
                "reference_paths": b * bref,
                "production_reference_hours":
                    next(iter(heavy.values()))["production_reference_hours"],
                "min_heavy_lower_bound": min_lb,
                "min_heavy_success_rate": min((v["success_rate"]
                                               for v in heavy.values()),
                                              default=math.nan),
                "worst_heavy_underestimation": max(
                    (v["underestimation_frequency"] for v in heavy.values()),
                    default=math.nan),
                "control_lower_bound": (next(iter(ctrl.values()))["lower_bound"]
                                        if ctrl else None),
                "criteria": ok, "selectable": all(ok.values()),
                "per_stratum": {k: {
                    "success_rate": v["success_rate"],
                    "lower_bound": v["lower_bound"],
                    "median": v["ratio_median"], "q05": v["ratio_q05"],
                    "q95": v["ratio_q95"],
                    "under": v["underestimation_frequency"],
                    "secondary_rate": v["secondary_rate"]} for k, v in per.items()},
            })
        out["candidates"] = rows
        sel = [r for r in rows if r["selectable"]]
        sel.sort(key=lambda r: (r["reference_paths"], r["block_paths"]))
        out["selected"] = ({k: sel[0][k] for k in
                            ("block_paths", "bref", "min_heavy_lower_bound",
                             "production_reference_hours")} if sel else None)
        out["reference_stopped"] = ref["stopped"]
        out["cumulative_cpu_hours"] = ref.get("cumulative_cpu_hours")

        print()
        print("CANDIDATE ACCURACY (frozen: c=1.25, p>=0.90, CP lower bound, R=29)")
        print(f"  {'b':>9s} {'B_ref':>6s} {'ref paths':>11s} {'prod h':>7s} "
              f"{'minHeavyRate':>12s} {'minLB':>7s} {'under':>6s} "
              f"{'ctrlLB':>7s}  selectable")
        for r in rows:
            print(f"  {r['block_paths']:9d} {r['bref']:6d} "
                  f"{r['reference_paths']:11.3g} "
                  f"{r['production_reference_hours']:7.2f} "
                  f"{r['min_heavy_success_rate']:12.4f} "
                  f"{r['min_heavy_lower_bound']:7.4f} "
                  f"{r['worst_heavy_underestimation']:6.2f} "
                  f"{(r['control_lower_bound'] if r['control_lower_bound'] is not None else float('nan')):7.4f}"
                  f"  {'YES' if r['selectable'] else 'no'}")
        print()
        print("SELECTED:", out["selected"] or "NONE")

    (R / "gate.json").write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
