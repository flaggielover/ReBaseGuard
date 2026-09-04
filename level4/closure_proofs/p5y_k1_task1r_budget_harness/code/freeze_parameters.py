"""T1R: run the frozen deterministic selection and emit the frozen parameters.

Result-independent: it touches no candidate and no predecessor residual.
Its output is committed BEFORE any genuine certificate is computed.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
import harness as H                                                  # noqa: E402
import integrity                                                     # noqa: E402
from rebaseguard_certify.arb_backend import workprec                 # noqa: E402


def main() -> int:
    t0 = time.process_time()
    iv = integrity.verify()
    if not iv["PASS"]:
        print(json.dumps({"FAIL": "CHECKPOINT_INTEGRITY_FAILURE", "integrity": iv},
                         indent=1))
        return 2
    sc = integrity.frozen_scope_unchanged(H)
    if not sc["PASS"]:
        print(json.dumps({"FAIL": "CHECKPOINT_INTEGRITY_FAILURE", "scope": sc}, indent=1))
        return 2
    sys.path.insert(0, str(H.K1 / "task1"))
    from task1_f0 import resolvent_upper_bound
    amp = resolvent_upper_bound(H.E_NUM, H.E_DEN)
    with workprec(H.PROD_BITS):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        sel = H.select_parameters(g, p1, amp["C_at_e"])
    out = {"schema": "rebaseguard.p5y.k1.task1r.frozen_parameters.v1",
           "binding": True, "result_bearing": False,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "integrity": iv, "frozen_scope": sc,
           "amplification": amp, "p1": p1,
           "budget_partition": H.budget(),
           "selection": sel,
           "selection_rule": (
               "minimal Z on the frozen ascending grid meeting B_tail, then "
               "minimal D on the frozen ascending grid meeting B_trunc and the "
               "joint-consistency relation; a-priori scale from the resolvent "
               "theorem only; no candidate and no predecessor residual is read"),
           "Z_GRID": list(H.Z_GRID), "D_GRID": list(H.D_GRID),
           "cpu_seconds": time.process_time() - t0}
    (NS / "config").mkdir(exist_ok=True)
    (NS / "config" / "frozen_parameters.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("selection", "budget_partition")}, indent=1))
    print("Z_selected =", sel.get("Z_selected"), " D_selected =", sel.get("D_selected"),
          " FAIL =", sel.get("FAIL"))
    print("cpu_seconds =", round(out["cpu_seconds"], 2))
    return 0 if sel.get("FAIL") is None else 3


if __name__ == "__main__":
    raise SystemExit(main())
