"""Consume the sealed C3 packet with the frozen consumer. Reads the seal; evaluates nothing new.

Refuses unless the seal's manifest re-hashes, every sealed file still matches, the chain hashes match, the frozen
gate matches and the seal records zero new-real evaluations. Emits no wall-clock or host leaf, so two runs are
byte-identical by construction.

    python3 -B c3_consume.py --tree <clean clone at freeze> --out OUT.json
"""
import argparse, hashlib, importlib.util, json, sys
from fractions import Fraction as F
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c3_closure"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = Path(__file__).resolve().parents[1]; ns = Path(a.tree).resolve() / NSREL
    seal = json.loads((dev / "evidence/seal/C3_SEAL.json").read_bytes())
    man = json.loads((dev / "evidence/seal/C3_SEAL_MANIFEST.json").read_bytes())

    ref = []
    if hashlib.sha256(json.dumps(man, sort_keys=True).encode()).hexdigest() != seal["namespace_manifest_sha256"]:
        ref.append("seal manifest hash does not match the seal")
    drift = [r for r, w in man.items() if not (dev / r).is_file() or sha(dev / r) != w]
    for rel, key in (("evidence/qualification/C3_QUALIFICATION.json", "qualification_sha256"),
                     ("evidence/authorization/C3_AUTHORIZATION.json", "authorization_sha256"),
                     ("evidence/execution/C3_EXECUTION.json", "execution_sha256")):
        if sha(dev / rel) != seal["chain"][key]:
            ref.append(f"chain hash mismatch: {rel}")
    if sha(ns / "config/FEASIBILITY_GATES_C3.json") != seal["chain"]["gate_sha256"]:
        ref.append("frozen gate hash mismatch")
    if seal["execution_facts"]["new_real_scientific_addresses_evaluated"] != 0:
        ref.append("seal records a new-real evaluation")
    if ref:
        print(json.dumps({"REFUSED": ref, "manifest_drift": drift[:6]}, indent=1)); return 2

    spec = importlib.util.spec_from_file_location("c3fc", ns / "code/c3_forecast.py")
    m = importlib.util.module_from_spec(spec); sys.modules["c3fc"] = m; spec.loader.exec_module(m)
    gate = json.loads((ns / "config/FEASIBILITY_GATES_C3.json").read_bytes())
    per = seal["sealed_result"]["per_cell"]
    cls, closed, adoptable, still, mt = m.classify(gate, per, gate["universe"]["cells"])

    doc = {"schema": "rebaseguard.p5y.k5.tail-c3.consumption.v1",
           "seal_sha256": sha(dev / "evidence/seal/C3_SEAL.json"), "chain_verified": True,
           "manifest_files_checked": len(man), "manifest_drift": drift,
           "consumed_result": {"C3_CLASS": cls, "closed": closed, "adoptable": adoptable,
                               "still_open": still, "materially_tightened": {str(k): v for k, v in mt.items()}},
           "agrees_with_seal": (cls == seal["sealed_result"]["C3_CLASS"]
                                and closed == seal["sealed_result"]["closed"]
                                and adoptable == seal["sealed_result"]["adoptable"]),
           "new_real_scientific_addresses_evaluated": 0, "guard": "REAL_SCIENTIFIC_COMPUTE = DENY",
           "proposes_for_adoption": [],
           "adoption": "NOT ADOPTED - C3 proposes nothing; adoption is an adjudicator's decision",
           "deterministic_exhaustion": "NOT established by C3",
           "incidental": "no wall-clock or host leaf is emitted, so two runs are byte-identical by construction"}
    data = json.dumps(doc, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"class": cls, "closed": closed, "adoptable": adoptable,
                      "agrees_with_seal": doc["agrees_with_seal"], "drift": drift,
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0 if doc["agrees_with_seal"] and not drift else 1


if __name__ == "__main__":
    sys.exit(main())
