"""Gate-2C-bis cost update: replace the assumed m>1 factor with the measured one."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
d = json.loads((HERE / "results" / "m2b_assembly.json").read_text())
cov = json.loads((ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover/results/sr_cover.json").read_text())

CPU_SR = 2227.792819637778            # Gate-2B measured
CUSUM_TOTAL = 70.13078166378472       # Gate-2B
OVER = 1.17 * 1.15                    # C3 rung + assembly/audit overhead
r_unit = d["cost"]["ratio_per_unit_used_by_production_model"]
cover_lo = cov["cover"]["subcell_count_lower_bound"] / cov["cover"]["subcell_count_upper_bound"]
PREC_384 = 1.2017975241648267         # Gate-2A measured t_panel multiplier, 256 -> 384 bits

bands = {
 "optimistic": {"cpu_hours": (CPU_SR * r_unit * cover_lo + CUSUM_TOTAL * r_unit) * OVER,
   "named_assumptions": [
     f"measured ratio_per_unit = {r_unit:.4f} (Gate-2C-bis, m=2) applied to all m",
     f"SR cover at the walk's LOWER bound ({cov['cover']['subcell_count_lower_bound']} sub-cells)"]},
 "central": {"cpu_hours": (CPU_SR + CUSUM_TOTAL) * OVER,
   "named_assumptions": [
     "ratio_per_unit = 1.0 RETAINED: the m=2 measurement shows 1.0 is conservative, but a "
     "single m=2 datum is not extrapolated to m in {3,5}, whose solve/source mix differs",
     "SR cover at the walk's upper bound (322 sub-cells), degree 8 @ 256 bits"]},
 "conservative": {"cpu_hours": (CPU_SR * PREC_384 + CUSUM_TOTAL) * OVER,
   "named_assumptions": [
     "ratio_per_unit = 1.0",
     f"the PRODUCTION SR candidate needs 384 bits, not 256: Gate-2A measured t_panel x{PREC_384:.3f}. "
     "Gate-2A used a representative candidate, so its conditioning is unmeasured for production"]},
 "worst": {"cpu_hours": (CPU_SR * PREC_384 * 1.25 + CUSUM_TOTAL) * OVER,
   "named_assumptions": [
     "ratio_per_unit = 1.0", "384-bit SR as above",
     "SR cover x1.25: the walk used a monotone step envelope, so a production certifier may "
     "need finer cells near e = 0 than the envelope implies"]},
}
for v in bands.values():
    for cores, eff in ((16, 0.95), (64, 0.90), (128, 0.80)):
        v[f"wall_hours_{cores}_cores"] = v["cpu_hours"] / (cores * eff)

out = {"schema": "rebaseguard.p5y.gate2cbis.costmodel.v1", "binding": False,
       "measured_inputs": {
         "ratio_incremental": d["cost"]["ratio_incremental"],
         "ratio_per_unit": r_unit, "ratio_cold": d["cost"]["ratio_cold"],
         "T_m1_seconds_in_process": d["cost"]["T_m1_seconds"],
         "T_incr_seconds": d["cost"]["T_incr_seconds"],
         "gate1_T_m1_per_subcell_in_pool": 30.85,
         "note_on_T_m1": "the in-process m=1 call costs 17.53 CPU-s; Gate-1's 30.85 CPU-s per "
                         "sub-cell was measured inside a 5-worker pool and carries per-worker "
                         "startup. Gate-1's larger figure is RETAINED in the CUSUM unit as the "
                         "conservative choice, since production also runs in a pool."},
       "bands": bands,
       "superseded_assumption": "Gate-2B hedged the m>1 per-function cost at 1.5x and 2.0x; "
                                "those arbitrary multipliers are now removed and replaced by "
                                "named, measured or explicitly-sourced uncertainties.",
       "gate2b_bands_for_comparison": {k: v["cpu_hours"] for k, v in cov["cost"]["bands"].items()}}
central = bands["central"]["cpu_hours"]
out["central_cpu_hours"] = central
out["feasibility"] = ("STRONG" if central <= 5000 else "MODERATE" if central <= 10000
                      else "WEAK" if central <= 30000 else "NOT_FEASIBLE")
(HERE / "results" / "cost_model_2cbis.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"measured": out["measured_inputs"],
                  "bands": {k: {"cpu": round(v["cpu_hours"]),
                                "w16": round(v["wall_hours_16_cores"]),
                                "w64": round(v["wall_hours_64_cores"]),
                                "w128": round(v["wall_hours_128_cores"])}
                            for k, v in bands.items()},
                  "feasibility": out["feasibility"],
                  "gate2b": out["gate2b_bands_for_comparison"]}, indent=1))
