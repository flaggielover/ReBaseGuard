"""Execute the authorized C2 lifecycle: zero-new-real deterministic consumption, then seal.

Authorized scope is narrow and enforced here rather than assumed: this re-derives the D-stage classification from
the FROZEN gate and the committed per-cell evidence, using the frozen `c2_d5_forecast.classify()`, and compares the
result against the class the forecast records. It never evaluates a scientific address, and it refuses to run if the
authorization does not bind to the freeze, the protocol and a QUALIFIED qualification.

Like the qualifier, this file is not part of the frozen set; its sha256 is recorded in the execution record.

    python3 -B c2_execute.py --tree <clean clone at the freeze> --binding-commit <sha> --out-dir DIR
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c2_closure"


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--binding-commit", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    ns = tree / NSREL
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    dev = Path(__file__).resolve().parents[1]
    auth = json.loads((dev / "evidence/authorization/C2_AUTHORIZATION.json").read_bytes())
    qual = json.loads((dev / "evidence/qualification/C2_QUALIFICATION.json").read_bytes())
    frec = json.loads((dev / "evidence/freeze/C2_FREEZE_RECORD.json").read_bytes())

    refusals = []
    if auth["bound_to"]["freeze_commit"] != frec["freeze_commit"]:
        refusals.append("authorization does not bind the freeze commit")
    if auth["bound_to"]["qualification_verdict"] != "QUALIFIED" or qual["verdict"] != "QUALIFIED":
        refusals.append("qualification is not QUALIFIED")
    if auth["new_real_scientific_addresses_authorized"] != 0 or auth["execution_class"] != "ZERO_NEW_REAL":
        refusals.append("authorization is not ZERO_NEW_REAL; refusing")
    frozen_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                 cwd=str(tree)).stdout.strip()
    if frozen_head != frec["freeze_commit"]:
        refusals.append(f"tree is at {frozen_head[:8]}, not the freeze commit")
    if refusals:
        print(json.dumps({"REFUSED": refusals}, indent=1))
        return 2

    # --- load the FROZEN decision rule out of the frozen tree ------------------------------------------------
    spec = importlib.util.spec_from_file_location("frozen_d5", ns / "code/c2_d5_forecast.py")
    d5 = importlib.util.module_from_spec(spec)
    sys.modules["frozen_d5"] = d5
    spec.loader.exec_module(d5)

    gate_raw = (ns / "config/FEASIBILITY_GATES_C2.json").read_bytes()
    if sha_b(gate_raw) != frec["gate_sha256"]:
        print(json.dumps({"REFUSED": ["frozen gate hash mismatch"]}))
        return 2
    gate = json.loads(gate_raw)
    thresh = F(str(gate["material_tightening_test"]["threshold"]))
    base_gap = {int(k): F(str(v)) for k, v in gate["baseline"]["gap"].items()}

    fc = json.loads((ns / "evidence/phase_d5/C2_D5_FORECAST.json").read_bytes())
    cells = fc["cells"]

    # --- re-derive closure and material tightening from the evidence, not from the recorded verdict ----------
    closed, still_open, mt = [], [], {}
    for k in sorted(int(x) for x in cells):
        c = cells[str(k)]
        if c["pass"]:
            closed.append(k)
        else:
            still_open.append(k)
            gap = F(str(c["gap_above_1"]))
            mt[k] = bool(gap <= (1 - thresh) * base_gap[k])
    derived_class = d5.classify(closed, mt, still_open)

    agree = (derived_class == fc["D_STAGE_CLASS"] and closed == fc["closed"]
             and still_open == fc["still_open"]
             and {str(k): v for k, v in mt.items()} == fc["materially_tightened"])

    # --- determinism of the frozen producers, inside the frozen tree -----------------------------------------
    env = dict(os.environ, PYTHONINTMAXSTRDIGITS="0")
    det = {}
    for mod, art in (("c2_d1_blocker.py", "evidence/phase_d1/C2_D1_BLOCKER.json"),
                     ("c2_mutations.py", "evidence/prefreeze/C2_MUTATIONS.json"),
                     ("c2_critical_ratio.py", "evidence/phase_d5/C2_CRITICAL_RATIOS.json")):
        dst = out / ("exec_" + Path(art).name)
        subprocess.run([sys.executable, "-B", f"code/{mod}", "--out", str(dst)],
                       capture_output=True, text=True, cwd=str(ns), env=env)
        det[mod] = dst.is_file() and dst.read_bytes() == (ns / art).read_bytes()

    rec = {
        "schema": "rebaseguard.p5y.k5.tail-c2.execution.v1",
        "execution_class": "ZERO_NEW_REAL",
        "new_real_scientific_addresses_evaluated": 0,
        "new_real_cpu_seconds": 0,
        "guard": "REAL_SCIENTIFIC_COMPUTE = DENY throughout",
        "bound_to": auth["bound_to"],
        "executor_sha256": sha_b(Path(__file__).read_bytes()),
        "executor_note": "not part of the frozen set",
        "frozen_rule_source": "code/c2_d5_forecast.py::classify, loaded from the frozen tree",
        "gate_threshold": str(thresh),
        "rederived": {"D_STAGE_CLASS": derived_class, "closed": closed, "still_open": still_open,
                      "materially_tightened": {str(k): v for k, v in mt.items()}},
        "recorded_in_forecast": {"D_STAGE_CLASS": fc["D_STAGE_CLASS"], "closed": fc["closed"],
                                 "still_open": fc["still_open"],
                                 "materially_tightened": fc["materially_tightened"]},
        "rederivation_agrees": agree,
        "per_cell": {str(k): {"Gamma": cells[str(k)]["Gamma"], "pass": cells[str(k)]["pass"],
                              "gap_above_1": cells[str(k)]["gap_above_1"],
                              "gap_fall_fraction": cells[str(k)]["gap_fall_fraction"]}
                     for k in sorted(int(x) for x in cells)},
        "producer_determinism": det,
        "wall_clock_seconds": round(time.time() - t0, 1),
    }
    data = json.dumps(rec, sort_keys=True, indent=1) + "\n"
    (out / "C2_EXECUTION.json").write_text(data)
    print(json.dumps({"rederived_class": derived_class, "closed": closed, "still_open": still_open,
                      "agrees_with_forecast": agree, "producers_byte_identical": all(det.values()),
                      "new_real_addresses": 0, "execution_sha256": sha_b(data.encode())}, indent=1))
    return 0 if (agree and all(det.values())) else 1


if __name__ == "__main__":
    sys.exit(main())
