"""Cost and memory model for the new 17,978-obligation universe.

PRODUCTION IS OFF. This measures a small representative set and projects the
full campaign; it never executes the cover.

Obligation classes and how their CPU is attributed, per cell:

  object            19  h_1..h_4 (order 0), S_0..S_4 (order 0), F_0..F_4, dF_0..dF_4
  dependency_bundle  1  h_j'(order 1), S_r'(order 1), and the finite-power
                        chain W_(r,j) at orders 0 and 1
  curvature          4  order-2 chain h_j'', S_r'', H_r, W_(r,j)''.
                        The m=5 unit OWNS these shared uniform-cell jets; the
                        m=1,2,3 units only assemble from hash-linked inputs and
                        carry the residual assembly cost only.
  assembly           4  certified all-m interval assembly, ledger and gates
  far_field          2  detector far-field certificates -- NOT IMPLEMENTED

Per-cell setup (collocation, candidate construction, recentred sites) is a
shared cell overhead and is reported as its own line rather than being hidden
inside a class or amortised away.

The frozen cap of 1126 CPU-hours is read from the frozen cost model and is
never increased here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import spec

NS = Path(__file__).resolve().parents[1]

OBJECT_RESIDUALS = ([f"h_{j}:0" for j in range(1, 5)]
                    + [f"S_{r}:0" for r in range(5)]
                    + [f"F_{r}" for r in range(5)]
                    + [f"dF_{r}" for r in range(5)])


def classify(name: str) -> str:
    if name in OBJECT_RESIDUALS:
        return "object"
    if name.startswith("Sclosed_"):
        return {"0": "object", "1": "dependency_bundle",
                "2": "curvature"}[name.rsplit("_", 1)[1]]
    if re.fullmatch(r"(h_\d|S_\d):1", name) or re.fullmatch(r"W_\d_\d:[01]", name):
        return "dependency_bundle"
    if re.fullmatch(r"(h_\d|S_\d):2", name) or re.fullmatch(r"H_\d", name) \
            or re.fullmatch(r"W_\d_\d:2", name):
        return "curvature"
    raise ValueError(f"unclassified residual {name}")


def per_cell_costs(record: dict) -> dict:
    """CPU seconds by obligation class for one measured cell."""
    by_class = {"object": 0.0, "dependency_bundle": 0.0, "curvature": 0.0}
    for name, meta in record["objects"].items():
        by_class[classify(name)] += float(meta.get("cpu_seconds", 0.0))
    total = float(record["cpu_seconds_including_dependencies"])
    prepare = float(record["cpu_seconds_prepare"])
    accounted = sum(by_class.values()) + prepare
    by_class["assembly"] = max(total - accounted, 0.0)
    by_class["cell_setup"] = prepare
    by_class["total"] = total
    by_class["unattributed"] = total - (sum(by_class[k] for k in
                                            ("object", "dependency_bundle",
                                             "curvature", "assembly", "cell_setup")))
    return by_class


def aggregate(records: list[dict]) -> dict:
    per = [per_cell_costs(r) for r in records]
    keys = ("object", "dependency_bundle", "curvature", "assembly", "cell_setup", "total")
    out = {}
    for k in keys:
        vals = sorted(c[k] for c in per)
        out[k] = {"mean_s": sum(vals) / len(vals), "min_s": vals[0], "max_s": vals[-1]}
    out["cells_measured"] = len(per)
    out["peak_rss_mib"] = max(float(r["peak_rss_kib"]) / 1024 for r in records)
    out["per_cell"] = {str(r["cell_index"]): per_cell_costs(r) for r in records}
    return out


def project(agg: dict, *, sr_extrapolation: bool = True) -> dict:
    """Full-campaign projection. SR is an extrapolation, never a measurement."""
    n_cusum, n_sr = spec.COUNTS["CUSUM"], spec.COUNTS["SR"]
    mean = agg["total"]["mean_s"]
    worst = agg["total"]["max_s"]
    cusum_central = mean * n_cusum / 3600
    cusum_conservative = worst * n_cusum / 3600

    # CUSUM completeness ratio: complete work / base-object work.
    obj = agg["object"]["mean_s"]
    ratio = mean / obj if obj else None

    cost = spec.COST_MODEL
    sr_base_central = cost["base_raw_sr_cpu_h"]
    sr_base_scaled = {
        "central": cost["base_only_central_cpu_h"] - cost["base_raw_cusum_cpu_h"],
        "conservative": cost["base_only_conservative_cpu_h"] - cost["base_raw_cusum_cpu_h"],
        "worst_plausible": cost["base_only_worst_plausible_cpu_h"] - cost["base_raw_cusum_cpu_h"],
    }
    out = {
        "frozen_hard_cap_cpu_h": spec.HARD_CAP_CPU_H,
        "cap_increased": False,
        "governed_work_units": spec.TOTAL_UNITS,
        "CUSUM": {
            "cells": n_cusum,
            "measured_complete_cpu_h_central": cusum_central,
            "measured_complete_cpu_h_conservative": cusum_conservative,
            "frozen_base_only_cpu_h": cost["base_raw_cusum_cpu_h"],
            "complete_over_base_object_ratio": ratio,
            "status": "MEASURED",
        },
        "SR": {
            "cells": n_sr,
            "measured": False,
            "status": "NOT_MEASURABLE",
            "reason": ("no raw-variable SR DAG exists: Task1R certified the F_0 "
                       "class only, on one patch at one drift, in a different "
                       "formulation. The SR dependency, curvature and all-m "
                       "interval-assembly kernels are unimplemented, so their "
                       "cost cannot be measured, only guessed."),
            "frozen_base_only_cpu_h": sr_base_scaled,
            "frozen_raw_sr_component_cpu_h": sr_base_central,
        },
    }
    if sr_extrapolation and ratio:
        out["SR"]["indicative_extrapolation"] = {
            "method": ("frozen SR base-only projection multiplied by the CUSUM "
                       "complete/base-object ratio; NOT a measurement of SR and "
                       "NOT admissible as cost qualification"),
            "ratio_applied": ratio,
            "central_cpu_h": sr_base_scaled["central"] * ratio,
            "conservative_cpu_h": sr_base_scaled["conservative"] * ratio,
            "worst_plausible_cpu_h": sr_base_scaled["worst_plausible"] * ratio,
        }
        tot_c = cusum_central + sr_base_scaled["central"] * ratio
        tot_w = cusum_conservative + sr_base_scaled["worst_plausible"] * ratio
        out["campaign_indicative"] = {
            "central_cpu_h": tot_c,
            "conservative_cpu_h": tot_w,
            "over_cap_central": tot_c > spec.HARD_CAP_CPU_H,
            "over_cap_conservative": tot_w > spec.HARD_CAP_CPU_H,
        }
        out["COST_CAP_STATUS"] = (
            "FAIL_BUDGET" if tot_c > spec.HARD_CAP_CPU_H else "NOT_ESTABLISHED")
        out["cost_cap_reason"] = (
            "the SR half of the campaign is an extrapolation from a different "
            "backend, and the two far-field obligations are unmeasured; an "
            "extrapolated number cannot establish cap adequacy"
            if tot_c <= spec.HARD_CAP_CPU_H else
            "even the indicative central projection exceeds the frozen cap")
    else:
        out["COST_CAP_STATUS"] = "NOT_ESTABLISHED"

    workers = spec.WORKER_CEILING
    out["memory"] = {
        "measured_peak_rss_mib_per_worker": agg["peak_rss_mib"],
        "frozen_per_worker_budget_mib": spec.PER_WORKER_BUDGET_MIB,
        "fits_frozen_per_worker_envelope":
            agg["peak_rss_mib"] <= spec.PER_WORKER_BUDGET_MIB,
        "worker_ceiling": workers,
        "projected_total_gib_at_ceiling": agg["peak_rss_mib"] * workers / 1024,
        "oversubscription_allowed": False,
    }
    if "campaign_indicative" in out:
        base = out["campaign_indicative"]["central_cpu_h"]
        out["wall_hours_indicative"] = {str(w): base / w for w in (1, 8, 16, 32, 64)}
        out["wall_time_note"] = (
            "8 workers is the measured host concurrency (8 vCPU); 32 and 64 "
            "worker wall times assume the frozen no-oversubscription rule and a "
            "host that actually has that many cores. They are arithmetic "
            "divisions of an already-extrapolated CPU total, not measurements.")
    return out


def load(directory: str | Path) -> list[dict]:
    out = []
    for p in sorted(Path(directory).glob("CUSUM_*_256.json")):
        rec = json.loads(p.read_text())
        if "objects" in rec:
            out.append(rec)
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    records = load(args.records)
    if not records:
        raise SystemExit("no representative records found")
    agg = aggregate(records)
    report = {"schema": "k1.cover-ledger.cost-model.v1",
              "production_run": False, "result_bearing": False,
              "host": {"vcpu": 8, "note": "AWS node used for these measurements"},
              "aggregate_cpu_seconds": agg, "projection": project(agg)}
    Path(args.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report["projection"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
