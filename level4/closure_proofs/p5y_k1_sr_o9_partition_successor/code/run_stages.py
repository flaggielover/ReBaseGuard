"""Successor stage runner for one successor cell: T3 aggregation (midpoint + mean-value cell mode) -> T4 -> T5.
Every output records the git commit it was produced at (temporal integrity: it must descend from the anchor)."""
import glob
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

import succ_cells as SC
import succ_t3_aggregate as AG
import succ_t4 as S4
import succ_t5 as S5


def main():
    s, pattern, outdir = int(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    outdir.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(SC.NS), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = SC.cell(s)
    c0 = time.process_time()
    t3 = AG.aggregate(s, glob.glob(pattern))
    (outdir / f"t3_s{s}.json").write_bytes(AG.canonical(t3))
    c1 = time.process_time()
    t4 = S4.t4(t3, rec)
    (outdir / f"t4_s{s}.json").write_bytes(S4.canonical(t4))
    ev = {"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
          "t3_file_sha256": hashlib.sha256((outdir / f"t3_s{s}.json").read_bytes()).hexdigest(),
          "t4_file_sha256": hashlib.sha256((outdir / f"t4_s{s}.json").read_bytes()).hexdigest(),
          "git_commit": head, "successor_cells_sha256": SC.table_sha256()}
    t5 = S5.obligations(t3, t4, ev, rec)
    (outdir / f"t5_s{s}.json").write_bytes(S5.canonical(t5))
    c2 = time.process_time()
    summ = {"successor_cell": s, "id": rec["id"], "git_commit": head, "T3_PASS": t3["T3_PASS"], "t3_checks": t3["checks"],
            "B_cover_ratio": t4["B_cover_ratio"], "status_m": t4["all_m_status"],
            "M_R2": {m: t4["m"][m]["M_R2"] for m in t4["m"]},
            "contraction_max": max(float(str(v["summary"]["contraction"])[1:].split(" ")[0]) for v in t4["refinement"].values()),
            "t5_status": t5["status"], "t5_pass_count": t5["pass_count"], "t5_total": t5["total"],
            "ids_equal_frozen_unit_structure": t5["obligation_ids_equal_frozen_universe"], "chain": t5["provenance_chain_verified"],
            "worst_obligation_margin": {o["identity"]["obligation_id"]: o["margin"] for o in t5["obligations"] if o["identity"]["unit_kind"] == "assembly"},
            "cpu_s": {"t3_aggregate": c1 - c0, "t4_t5": c2 - c1}, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "t5_sha256": hashlib.sha256((outdir / f"t5_s{s}.json").read_bytes()).hexdigest()}
    (outdir / f"summary_s{s}.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summ[k] for k in ("id", "T3_PASS", "B_cover_ratio", "t5_status", "t5_pass_count")}))


if __name__ == "__main__":
    main()
