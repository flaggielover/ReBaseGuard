"""Phase 10: derive the NEW PS1 global cap from MEASURED Phase-4 cost (never from the historical 1,126/4,500 caps).

  P      = measured campaign projection, worst-group based (the slowest measured production group per cell x 368 + the
           measured terminal single cell), plus 10% measurement margin
  R      = per-cell reservation = ceil_0.5(1.25 x slowest measured per-cell cost)
  INFL   = 16 x R                (in-flight reservations of a full pool at the last admission)
  RETRY  = 0.03 x 369 x R        (up to ~3% of cells torn once, re-run in full)
  OVH    = governed operational overhead = 0.02 x P (supervisor, launcher, probes, idle pool, shadow lag)
  CAP    = ceil_50( 1.15 x (P + INFL + RETRY + OVH) )    1.15 = the frozen lifecycle invariant factor
The frozen invariant 1.15 x (committed + open + torn + shadow + requested + overhead) <= CAP is then satisfiable to the
end of the campaign with margin, and CAP >= 1.15 x P > measured projection."""
import json
import math
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
Q = NS.parent / "p5y_k1_ps1_production_qualification/evidence"


def main():
    s = json.loads((Q / "qual_summary.json").read_text())
    probe = json.loads((Q / "runtime_probe_aws.json").read_text())
    P = s["projection_cpu_h"]["worst_plus_10pct"]
    R = math.ceil(1.25 * s["per_cell_cpu_h_stats"]["max"] * 2) / 2
    INFL, RETRY, OVH = 16 * R, 0.03 * 369 * R, 0.02 * P
    CAP = math.ceil(1.15 * (P + INFL + RETRY + OVH) / 50) * 50
    c = {"GLOBAL_CPU_CAP": float(CAP), "GOVERNED_OVERHEAD_CPU_H": round(OVH, 3), "TOTAL_CELLS": 369,
         "TOTAL_SR_OBLIGATIONS": 369 * 28 + 1,
         "derivation": {"P_projection_worst_plus_10pct": P, "R_per_cell_reservation": R, "INFL": INFL, "RETRY": RETRY,
                        "OVH": OVH, "factor": 1.15, "measured_mean_projection": s["projection_cpu_h"]["mean_based"],
                        "source": "p5y_k1_ps1_production_qualification/evidence/qual_summary.json"},
         "ROLES": {"AWS": {"sys_vendor": "Amazon EC2", "runtime_contract_hash": probe["runtime"]["sha256"], "workers": 16,
                           "core_assignment": list(range(16)), "per_cell_reservation_cpu_h": R},
                   "VULTR": {"sys_vendor": "Vultr", "runtime_contract_hash": "NOT_QUALIFIED_FOR_PS1", "workers": 0,
                             "core_assignment": [], "per_cell_reservation_cpu_h": R}}}
    (NS / "config/PS1_CONSTANTS.json").write_text(json.dumps(c, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: c[k] for k in ("GLOBAL_CPU_CAP", "GOVERNED_OVERHEAD_CPU_H")}), json.dumps(c["derivation"]))


if __name__ == "__main__":
    main()
