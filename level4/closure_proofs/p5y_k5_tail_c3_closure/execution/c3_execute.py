"""Execute the authorized C3 lifecycle (zero-new-real) and seal before interpretation.

Re-derives the C3 class from the FROZEN gate against the committed per-cell evidence, independent of the class the
forecast records. Refuses unless the authorization binds the freeze, the qualification is QUALIFIED, the class is
ZERO_NEW_REAL and the tree is AT the freeze commit.

    python3 -B c3_execute.py --tree <clean clone at freeze> --out-dir DIR
"""
import argparse, hashlib, importlib.util, json, os, subprocess, sys, time
from fractions import Fraction as F
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c3_closure"


def sb(b): return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True); ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    tree = Path(a.tree).resolve(); ns = tree / NSREL
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    dev = Path(__file__).resolve().parents[1]

    auth = json.loads((dev / "evidence/authorization/C3_AUTHORIZATION.json").read_bytes())
    qual = json.loads((dev / "evidence/qualification/C3_QUALIFICATION.json").read_bytes())
    frec = json.loads((dev / "evidence/freeze/C3_FREEZE_RECORD.json").read_bytes())
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(tree)).stdout.strip()

    ref = []
    if auth["bound_to"]["freeze_commit"] != frec["freeze_commit"]: ref.append("authorization does not bind the freeze")
    if qual["verdict"] != "QUALIFIED": ref.append("qualification is not QUALIFIED")
    if auth["execution_class"] != "ZERO_NEW_REAL" or auth["new_real_scientific_addresses_authorized"] != 0:
        ref.append("authorization is not ZERO_NEW_REAL")
    if head != frec["freeze_commit"]: ref.append(f"tree is at {head[:8]}, not the freeze commit")
    if ref:
        print(json.dumps({"REFUSED": ref}, indent=1)); return 2

    spec = importlib.util.spec_from_file_location("c3fc", ns / "code/c3_forecast.py")
    m = importlib.util.module_from_spec(spec); sys.modules["c3fc"] = m; spec.loader.exec_module(m)
    gate_raw = (ns / "config/FEASIBILITY_GATES_C3.json").read_bytes()
    if sb(gate_raw) != frec["gate_sha256"]:
        print(json.dumps({"REFUSED": ["frozen gate hash mismatch"]})); return 2
    gate = json.loads(gate_raw)
    fc = json.loads((ns / "evidence/forecast/C3_FORECAST.json").read_bytes())

    cls, closed, adoptable, still, mt = m.classify(gate, fc["cells"], gate["universe"]["cells"])
    agree = (cls == fc["C3_CLASS"] and closed == fc["closed"] and adoptable == fc["adoptable"]
             and still == fc["still_open"] and {str(k): v for k, v in mt.items()} == fc["materially_tightened"])

    det = {}
    for mod, art in (("c3_blocker.py", "evidence/phase_c1/C3_BLOCKER.json"),
                     ("c3_mutations.py", "evidence/preforecast/C3_MUTATIONS.json"),
                     ("c3_forecast.py", "evidence/forecast/C3_FORECAST.json")):
        dst = out / ("exec_" + Path(art).name)
        subprocess.run([sys.executable, "-B", f"code/{mod}", "--out", str(dst)], capture_output=True,
                       text=True, cwd=str(ns), env=dict(os.environ, PYTHONINTMAXSTRDIGITS="0"))
        det[mod] = dst.is_file() and dst.read_bytes() == (ns / art).read_bytes()

    rec = {"schema": "rebaseguard.p5y.k5.tail-c3.execution.v1", "execution_class": "ZERO_NEW_REAL",
           "new_real_scientific_addresses_evaluated": 0, "new_real_cpu_seconds": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY throughout", "bound_to": auth["bound_to"],
           "executor_sha256": sb(Path(__file__).read_bytes()), "executor_note": "not part of the frozen set",
           "frozen_rule_source": "code/c3_forecast.py::classify, loaded from the frozen tree",
           "rederived": {"C3_CLASS": cls, "closed": closed, "adoptable": adoptable, "still_open": still,
                         "materially_tightened": {str(k): v for k, v in mt.items()}},
           "recorded_in_forecast": {"C3_CLASS": fc["C3_CLASS"], "closed": fc["closed"],
                                    "adoptable": fc["adoptable"], "still_open": fc["still_open"],
                                    "materially_tightened": fc["materially_tightened"]},
           "rederivation_agrees": agree, "producer_determinism": det,
           "per_cell": {k: {kk: fc["cells"][k][kk] for kk in
                            ("Gamma", "closes", "requirement", "gap_above_1", "gap_fall_vs_r5", "adoption_floor")}
                        for k in fc["cells"]},
           "wall_clock_seconds": round(time.time() - t0, 1)}
    data = json.dumps(rec, sort_keys=True, indent=1) + "\n"
    (out / "C3_EXECUTION.json").write_text(data)
    print(json.dumps({"rederived_class": cls, "closed": closed, "adoptable": adoptable,
                      "agrees": agree, "producers_byte_identical": all(det.values()),
                      "new_real": 0, "sha256": sb(data.encode())}, indent=1))
    return 0 if (agree and all(det.values())) else 1


if __name__ == "__main__":
    sys.exit(main())
