"""Stream D, D7 probe: where the C1b-format verifier spends its time at high degree (e = 3 only).

For each certificate: mean wall time of one second-order box bound on 12 sample boxes, then the local branch and
bound on every initial box with a small per-box budget (max_boxes), recording how many initial boxes certify within
the budget and the total boxes.  Single process.  Output: results/D7_PROBE.json.  Diagnostic only (no verdict).
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_verify as V  # noqa: E402
import vd_adapt as AD  # noqa: E402

Q = V.Q

if __name__ == "__main__":
    degs = [int(x) for x in sys.argv[1:]] or [8]
    budget = 200
    Q.log_event("streams/VERIFY/vd_d7_probe.py", f"D7 cost probe of the C1b-format verifier at e=3, degrees {degs}",
                klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    out = {"schema": "VD_D7_PROBE/1", "budget_boxes_per_initial_box": budget, "rows": []}
    for d in [4, 6] + degs:
        path = HERE / "certs" / f"CERT_e3_1_d{d}.json"
        W = AD.from_c1b_raw(json.loads(path.read_text())["c1b_raw"])
        pre = V.Prep(W, F(3))
        boxes = V.initial_boxes()
        t0 = time.time()
        for b in boxes[:: max(1, len(boxes) // 12)][:12]:
            V._box_bound(pre, b, V.residual_region, 2)
        per_box = (time.time() - t0) / 12
        key = (W.sha256(), "3", False)
        V._PREP_CACHE.clear()
        t1 = time.time()
        done = und = tot = 0
        hard = []
        for b in boxes:
            r = V.bb_box((key, W.to_json(), "3", False, b, "res", {"max_boxes": budget}))
            tot += r["boxes"]
            if r["status"] == "CERTIFIED":
                done += 1
            else:
                und += 1
                hard.append([str(x) for x in b])
        row = {"degree": d, "ms_per_box_bound": round(1000 * per_box, 1), "initial_boxes": len(boxes),
               "certified_within_budget": done, "not_within_budget": und, "boxes_used": tot,
               "hard_initial_boxes": hard[:10], "seconds": round(time.time() - t1, 1)}
        out["rows"].append(row)
        print(json.dumps(row), flush=True)
        (HERE / "results" / "D7_PROBE.json").write_text(json.dumps(out, indent=1) + "\n")
