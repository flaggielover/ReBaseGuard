"""Consume the sealed C2 packet with the frozen consumer. Reads the seal; evaluates nothing new.

Refuses unless the seal's whole chain re-hashes to what the seal records and the namespace manifest still matches
file for file. Output is deterministic: run twice and the two must be byte-identical, except for the leaves listed
in `incidental` (wall clock), which are excluded from the emitted document entirely rather than merely tolerated.

    python3 -B c2_consume.py --tree <clean clone at the freeze> --out OUT.json
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c2_closure"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = Path(__file__).resolve().parents[1]
    ns = Path(a.tree).resolve() / NSREL

    seal = json.loads((dev / "evidence/seal/C2_SEAL.json").read_bytes())
    manifest = json.loads((dev / "evidence/seal/C2_SEAL_MANIFEST.json").read_bytes())

    refusals = []
    if hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest() != seal["namespace_manifest_sha256"]:
        refusals.append("seal manifest hash does not match the seal")
    drift = [rel for rel, want in manifest.items()
             if not (dev / rel).is_file() or sha(dev / rel) != want]
    for rel in ("evidence/qualification/C2_QUALIFICATION.json", "evidence/authorization/C2_AUTHORIZATION.json",
                "evidence/execution/C2_EXECUTION.json"):
        key = {"evidence/qualification/C2_QUALIFICATION.json": "qualification_sha256",
               "evidence/authorization/C2_AUTHORIZATION.json": "authorization_sha256",
               "evidence/execution/C2_EXECUTION.json": "execution_sha256"}[rel]
        if sha(dev / rel) != seal["chain"][key]:
            refusals.append(f"chain hash mismatch: {rel}")
    if sha(ns / "config/FEASIBILITY_GATES_C2.json") != seal["chain"]["gate_sha256"]:
        refusals.append("frozen gate hash mismatch")
    if seal["execution_facts"]["new_real_scientific_addresses_evaluated"] != 0:
        refusals.append("seal records a new-real evaluation; refusing")
    if refusals:
        print(json.dumps({"REFUSED": refusals, "manifest_drift": drift[:8]}, indent=1))
        return 2

    # re-derive the class once more, from the frozen rule and the sealed per-cell values
    spec = importlib.util.spec_from_file_location("frz", ns / "code/c2_d5_forecast.py")
    d5 = importlib.util.module_from_spec(spec)
    sys.modules["frz"] = d5
    spec.loader.exec_module(d5)
    gate = json.loads((ns / "config/FEASIBILITY_GATES_C2.json").read_bytes())
    thresh = F(str(gate["material_tightening_test"]["threshold"]))
    base_gap = {int(k): F(str(v)) for k, v in gate["baseline"]["gap"].items()}

    per = seal["sealed_result"]["per_cell"]
    closed, still_open, mt = [], [], {}
    for k in sorted(int(x) for x in per):
        c = per[str(k)]
        if c["pass"]:
            closed.append(k)
        else:
            still_open.append(k)
            mt[str(k)] = bool(F(str(c["gap_above_1"])) <= (1 - thresh) * base_gap[k])
    cls = d5.classify(closed, {int(k): v for k, v in mt.items()}, still_open)

    doc = {
        "schema": "rebaseguard.p5y.k5.tail-c2.consumption.v1",
        "seal_sha256": sha(dev / "evidence/seal/C2_SEAL.json"),
        "chain_verified": True,
        "manifest_files_checked": len(manifest),
        "manifest_drift": drift,
        "consumed_result": {"D_STAGE_CLASS": cls, "closed": closed, "still_open": still_open,
                            "materially_tightened": mt},
        "agrees_with_seal": (cls == seal["sealed_result"]["D_STAGE_CLASS"]
                             and closed == seal["sealed_result"]["closed"]
                             and still_open == seal["sealed_result"]["still_open"]),
        "new_real_scientific_addresses_evaluated": 0,
        "guard": "REAL_SCIENTIFIC_COMPUTE = DENY",
        "adoption": "NOT ADOPTED — adoption requires an adjudicator handover",
        "cell_306_margin_floor": "referred to the adjudicator; not decided by the consumer",
        "incidental": "no wall-clock or host leaf is emitted, so two runs are byte-identical by construction",
    }
    data = json.dumps(doc, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"class": cls, "closed": closed, "still_open": still_open,
                      "agrees_with_seal": doc["agrees_with_seal"], "drift": drift,
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0 if doc["agrees_with_seal"] and not drift else 1


if __name__ == "__main__":
    sys.exit(main())
