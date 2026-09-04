"""Gate-2A cost re-projection using MEASURED precision multipliers."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
d = json.loads((HERE / "results" / "sr_precision.json").read_text())
g1 = json.loads((ROOT / "level4/closure_proofs/p5y_micropilot_gate1/results/cost_model.json").read_text())

SR_PATCHES, SR_SUBCELLS = 1210, 835
MULT = 24.5                      # carried forward from Gate-1 MSHARE, unchanged
CUSUM_UNIT = g1["derived"]["cusum_cpu_hours_per_unit"]
C3, OVERHEAD = 0.17, 0.15

def sr_unit(deg, bits):
    c = d["cells"][f"{deg}@{bits}"]
    return 2 * SR_SUBCELLS * SR_PATCHES * c["n_z"] * c["timing"]["t_panel_median"] / 3600.0

def total(deg, bits, m_mult=1.0, cover_mult=1.0):
    return (sr_unit(deg, bits) * cover_mult + CUSUM_UNIT) * MULT * m_mult * (1 + C3) * (1 + OVERHEAD)

scal = {}
for deg in (8, 10):
    base = d["cells"][f"{deg}@192"]["timing"]["t_panel_median"]
    scal[deg] = {b: d["cells"][f"{deg}@{b}"]["timing"]["t_panel_median"] / base
                 for b in (192, 256, 384, 512)}

bands = {
 "optimistic":   {"config": "degree 10 @ 256 (frozen-rule winner)", "cpu_hours": total(10, 256),
                  "assumption": "m>1 per-function cost equals m=1; cover as estimated"},
 "central":      {"config": "degree 8 @ 256 (precision-saturated, safer backend)",
                  "cpu_hours": total(8, 256),
                  "assumption": "m>1 per-function cost equals m=1; cover as estimated"},
 "conservative": {"config": "degree 8 @ 256", "cpu_hours": total(8, 256, 1.5, 1.25),
                  "assumption": "m>1 functions 1.5x; SR cover 1.25x the estimate"},
 "worst":        {"config": "degree 8 @ 384", "cpu_hours": total(8, 384, 2.0, 1.5),
                  "assumption": "real production candidate needs 384 bits; m>1 2x; cover 1.5x"},
}
for v in bands.values():
    for cores, eff in ((16, 0.95), (64, 0.90), (128, 0.80)):
        v[f"wall_hours_{cores}_cores"] = v["cpu_hours"] / (cores * eff)

central = bands["central"]["cpu_hours"]
sel = d["selected_precision_degree8"]
feas = ("STRONG" if sel <= 256 and central <= 5000 else
        "MODERATE" if sel <= 384 and central <= 10000 else
        "WEAK" if sel == 512 or (10000 < central <= 30000) else "NOT_FEASIBLE")

out = {"schema": "rebaseguard.p5y.gate2a.costmodel.v1", "binding": False,
       "measured_precision_scaling_t_panel_relative_to_192bits": scal,
       "sr_unit_cpu_hours": {f"deg{deg}@{b}": sr_unit(deg, b)
                             for deg in (8, 10) for b in (256, 384, 512)},
       "cusum_unit_cpu_hours": CUSUM_UNIT, "m_sharing_multiplier": MULT,
       "bands": bands, "selected_precision_degree8": sel,
       "central_cpu_hours": central, "feasibility_ceiling": 30000,
       "sr_production_feasibility": feas,
       "gate1_bands_for_comparison": {k: v["cpu_hours"] for k, v in g1["bands"].items()},
       "gate1_assumed_precision_multipliers": {k: v["precision_mult"] for k, v in g1["bands"].items()},
       "note": "Gate-1 assumed precision multipliers of 1.0/1.5/3.0/5.0. MEASURED "
               "multipliers are 1.03 (256), 1.17-1.20 (384), 1.32-1.41 (512). "
               "Gate-1's conservative and worst bands were over-pessimistic on precision."}
(HERE / "results" / "cost_model_2a.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"precision_scaling": scal,
                  "sr_unit": {k: round(v, 2) for k, v in out["sr_unit_cpu_hours"].items()},
                  "bands": {k: {"config": v["config"], "cpu": round(v["cpu_hours"]),
                                "w16": round(v["wall_hours_16_cores"]),
                                "w64": round(v["wall_hours_64_cores"]),
                                "w128": round(v["wall_hours_128_cores"])}
                            for k, v in bands.items()},
                  "feasibility": feas, "gate1_bands": out["gate1_bands_for_comparison"]}, indent=1))
