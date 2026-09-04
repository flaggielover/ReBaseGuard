"""P5Y Gate-1 cost re-projection from PILOT-MEASURED timings only.

No optimistic historical estimate is reused.  Every input is either measured in
this gate or is an already-published measured constant, and each is labelled.
"""
from __future__ import annotations
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
m1 = json.loads((HERE / "results" / "m1_raw_2cell.json").read_text())
m2 = json.loads((HERE / "results" / "m2_sr_degree.json").read_text())
opt = json.loads((HERE / "results" / "optional_checks.json").read_text())

SR_PATCHES = 1210      # R3 measured, incumbent Gamma_SR geometry
SR_SUBCELLS = 835      # R3 frozen cover-size figure for SR over [0,12]
CUSUM_SUBCELLS = 334   # R1 measured optimized cover over [0,12]
MULT = opt["PILOT_MSHARE"]["corrected_multiplier_units"]     # 24.5, measured structurally
HIST_MULT = opt["PILOT_MSHARE"]["historical_multiplier_units"]

d8 = m2["degrees"]["8"]
t_panel = d8["cost"]["t_panel"]; n_z = d8["cost"]["n_z"]
t_panel_full = d8["timing"]["t_panel_full_median_incl_moments"]

cellA = m1["cells"]["A_near"]
raw_s = cellA["arms"]["raw"]["cpu_seconds"] / cellA["n_sub"]
z_s = cellA["arms"]["z_control"]["cpu_seconds"] / cellA["n_sub"]

sr_fn = SR_SUBCELLS * SR_PATCHES * n_z * t_panel_full / 3600.0     # one certified function
sr_unit = 2 * sr_fn                                                # value + derivative
cusum_unit = CUSUM_SUBCELLS * raw_s / 3600.0

C3 = 0.17          # H2/H3a derivative-ladder rung on [0,2], as a fraction of total
OVERHEAD = 0.15    # assembly, resolvent, auditor replay, artifact IO

def total(precision_mult, m_gt1_mult):
    sr = sr_unit * MULT * precision_mult * m_gt1_mult
    cu = cusum_unit * MULT * m_gt1_mult
    return (sr + cu) * (1 + C3) * (1 + OVERHEAD)

bands = {"optimistic":   {"precision_mult": 1.0, "m_gt1_mult": 1.0, "note": "degree 8 at 192 bits as measured; m>1 per-function cost equals m=1"},
         "central":      {"precision_mult": 1.5, "m_gt1_mult": 1.0, "note": "256 bits on SR to restore the P2 conditioning margin"},
         "conservative": {"precision_mult": 3.0, "m_gt1_mult": 1.5, "note": "384 bits on SR; m>1 functions 1.5x the m=1 cost"},
         "worst":        {"precision_mult": 5.0, "m_gt1_mult": 2.0, "note": "512 bits on SR; m>1 functions 2x the m=1 cost"}}
for k, v in bands.items():
    v["cpu_hours"] = total(v["precision_mult"], v["m_gt1_mult"])
    for cores, eff in ((1, 1.0), (16, 0.95), (64, 0.90), (128, 0.80)):
        v[f"wall_hours_{cores}_cores"] = v["cpu_hours"] / (cores * eff)

out = {"schema": "rebaseguard.p5y.gate1.costmodel.v1", "binding": False,
       "measured_inputs": {
         "sr_t_panel_seconds_degree8": t_panel,
         "sr_t_panel_incl_moments_seconds": t_panel_full,
         "sr_n_z_degree8": n_z,
         "cusum_raw_cpu_seconds_per_subcell": raw_s,
         "cusum_z_cpu_seconds_per_subcell": z_s,
         "raw_vs_z_speed_ratio": z_s / raw_s,
         "m_sharing_multiplier_measured": MULT,
         "m_sharing_multiplier_historical": HIST_MULT},
       "derived": {"sr_cpu_hours_per_certified_function": sr_fn,
                   "sr_cpu_hours_per_unit": sr_unit,
                   "cusum_cpu_hours_per_unit": cusum_unit,
                   "C3_fraction": C3, "overhead_fraction": OVERHEAD},
       "bands": bands,
       "dominant_uncertainty": "SR working precision. Degree 8 passed P2 with only "
                               "1.34x margin and its composed contraction already lost "
                               "~17 digits at 192 bits; degrees 10 and 12 were destroyed. "
                               "Precision, not panel count, now sets the SR cost.",
       "comparison": {"pre_gate_audit_central_cpu_hours": 6000,
                      "r3_projected_sr_cpu_hours": 12084,
                      "note": "the R3 projection used the dyadic n_z = 128, t_panel = 3.911 ms "
                              "and the 43x multiplier; this model uses the measured continuous "
                              "n_z = 28, t_panel(incl. moments) and the 24.5x structural multiplier"}}
(HERE / "results" / "cost_model.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"measured": out["measured_inputs"], "derived": out["derived"],
                  "bands": {k: {"cpu_hours": round(v["cpu_hours"]),
                                "wall_16": round(v["wall_hours_16_cores"]),
                                "wall_64": round(v["wall_hours_64_cores"]),
                                "wall_128": round(v["wall_hours_128_cores"])}
                            for k, v in bands.items()}}, indent=1))
