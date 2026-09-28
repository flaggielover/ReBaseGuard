"""Stream D, D7: cost of the C1b-format verifier (vd_verify) at degrees 8, 10, 12 (e = 1 and e = 3 only).

Certificates are produced by vd_produce.py (C1b certify_degree, the one sanctioned C1b import) into certs/; this
script verifies them with vd_d3_verify_all.main (adapter + exact A_bar check + vd_verify.verify, 3 workers) and records
wall time, main-process CPU, boxes and margins.  Output: results/D7_COST.json.  The machine is shared: wall times are
indicative only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_d3_verify_all as D3  # noqa: E402
import vd_verify as V  # noqa: E402

Q = V.Q

if __name__ == "__main__":
    args = list(sys.argv[1:])
    workers = 3
    if "--workers" in args:
        k = args.index("--workers")
        workers = int(args[k + 1])
        del args[k:k + 2]
    degs = [int(x) for x in args] or [8, 10, 12]
    paths = [str(p) for e in ("3_1", "1_1") for d in degs
             for p in [HERE / "certs" / f"CERT_e{e}_d{d}.json"] if p.exists()]
    # per-initial-box budget: beyond it the verdict is UNDECIDED (reported as such, never as PASS)
    budget = {"max_boxes": 40000}
    Q.log_event("streams/VERIFY/vd_d7_cost.py", f"D7 cost of the independent C1b-format verifier at degrees {degs}, "
                "declared drifts 1 and 3", klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    t0 = time.time()
    rows = D3.main(paths, workers=workers, opts_extra=budget)
    doc = {"schema": "VD_D7/1", "degrees": degs, "workers": workers, "budget_per_initial_box": budget, "rows": rows, "all_pass": all(r["control_pass"] for r in rows),
           "missing": [f"e{e}_d{d}" for d in degs for e in ("1_1", "3_1")
                       if not (HERE / "certs" / f"CERT_e{e}_d{d}.json").exists()],
           "seconds": round(time.time() - t0, 1)}
    (HERE / "results" / "D7_COST.json").write_text(json.dumps(V.jsonable(doc), indent=1, sort_keys=True) + "\n")
    print("ALL_PASS", doc["all_pass"], "missing", doc["missing"])
