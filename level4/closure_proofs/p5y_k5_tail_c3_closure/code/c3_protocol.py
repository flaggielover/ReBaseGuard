"""Build and check the frozen C3 protocol.

Carries the C2 lifecycle lessons from the outset rather than discovering them:
  * the protocol pins its OWN producer, so editing this file after the freeze invalidates the freeze;
  * the binding-integrity check exists BEFORE the real freeze, so binding cannot smuggle an edit;
  * `check --expect-bound` refuses while the protocol is UNBOUND;
  * every pin table tags the root its paths resolve against, so a checker never infers it.

    python3 -B c3_protocol.py build --out ../config/C3_PROTOCOL.json
    python3 -B c3_protocol.py check --protocol ../config/C3_PROTOCOL.json [--expect-bound]
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
REPO = HERE.parents[4]
C2 = CP / "p5y_k5_tail_c2_closure"
SCHEMA = "rebaseguard.p5y.k5.tail-c3.protocol.v1"
GATE_SHA = "f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7"
GATE_COMMIT = "24c038ec"
ROOTS = {"namespace": NS, "closure_proofs": CP}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pins(paths, root_name: str) -> dict:
    root = ROOTS[root_name]
    files = {}
    for rel in sorted(paths):
        p = root / rel
        if not p.is_file():
            raise SystemExit(f"protocol input missing: {p}")
        files[rel] = sha(p)
    return {"root": root_name, "files": files}


def build() -> dict:
    fc = json.loads((NS / "evidence/forecast/C3_FORECAST.json").read_bytes())
    mut = json.loads((NS / "evidence/preforecast/C3_MUTATIONS.json").read_bytes())
    code = sorted(p.name for p in (NS / "code").glob("*.py"))
    return {
        "schema": SCHEMA, "campaign": "p5y_k5_tail_c3_closure",
        "freeze": {"commit": None, "state": "UNBOUND",
                   "note": "bound by evidence/freeze/C3_FREEZE_RECORD.json after the commit introducing this file"},
        "scientific_load_bearing": {
            "result": {"C3_CLASS": fc["C3_CLASS"], "closed": fc["closed"], "adoptable": fc["adoptable"],
                       "still_open": fc["still_open"],
                       "materially_tightened": fc["materially_tightened"],
                       "Gamma": {k: fc["cells"][k]["Gamma"] for k in fc["cells"]},
                       "requirement": {k: fc["cells"][k]["requirement"] for k in fc["cells"]},
                       "gap_fall_vs_r5": {k: fc["cells"][k]["gap_fall_vs_r5"] for k in fc["cells"]},
                       "adoption_floor": {k: fc["cells"][k]["adoption_floor"] for k in fc["cells"]}},
            "evidence": pins(["evidence/forecast/C3_FORECAST.json",
                              "evidence/preforecast/C3_MUTATIONS.json",
                              "evidence/phase_c1/C3_BLOCKER.json",
                              "evidence/phase_b0/C3_B0_AUDIT.json"], "namespace"),
            "producers": pins([f"code/{n}" for n in code], "namespace"),
            "consumed_predecessor_evidence": pins([
                "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json",
                "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
                "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                "p5y_k1_cover_ledger_successor/config/cells.json",
            ] + [f"p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_{k}.json" for k in range(306, 310)],
                "closure_proofs"),
            "consumed_modules": pins([
                "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
                "p5y_k5_m5_tail_closure/code/tct_rule.py",
                "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
                "p5y_k5_lower_front_order3/code/tc_rule.py",
                "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
            ], "closure_proofs"),
            "expected_verdicts": {"mutations": {"applied": mut["applied"], "killed": mut["killed"],
                                                "proved_equivalent": mut["proved_equivalent"],
                                                "undetected": mut["undetected"], "pass": mut["pass"]}},
        },
        "governance_provenance": {
            "gate": {"commit": GATE_COMMIT, "sha256": GATE_SHA,
                     "path": "config/FEASIBILITY_GATES_C3.json", "frozen_before_any_c3_forecast": True},
            "gate_erratum": pins(["ERRATUM_C3_GATE.md"], "namespace"),
            "preforecast_review": pins(["review/REVIEW_C3_PREFORECAST.md"], "namespace"),
            "preforecast_verdict": "READY_WITH_NOTES (0 FAIL)",
            "predecessor_c2": {
                "adjudication_sha256": sha(C2 / "evidence/adjudication/C2_ADJUDICATION.md"),
                "verdict": "PARTIALLY_ADOPTED", "adopted": [305],
                "seal_sha256": sha(C2 / "evidence/seal/C2_SEAL.json")},
            "authoritative_input_coverage_map": pins(
                ["p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json",
                 "p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json"], "closure_proofs"),
            "guard": "REAL_SCIENTIFIC_COMPUTE = DENY",
            "new_real_scientific_addresses_authorized": 0,
            "proposes_for_adoption": [],
            "prohibition": ("no new real scientific address, no R-stage, no AWS. C3 does not assert deterministic "
                            "exhaustion."),
            "r6_rule": "generated only on an adopting adjudication verdict with a non-empty adopted set",
            "lifecycle_order": ["gate", "mechanism", "mutations", "preforecast_review", "forecast", "protocol",
                                "freeze", "qualification", "authorization", "execution", "seal", "consumption",
                                "adjudication"],
        },
        "incidental_runtime": {"note": "recorded, not required to reproduce"},
    }


def check(proto: dict, expect_bound: bool):
    bad = []
    if proto.get("schema") != SCHEMA:
        bad.append("schema mismatch")
    fr = proto.get("freeze", {})
    if expect_bound and (fr.get("state") != "BOUND" or not fr.get("commit")):
        bad.append("REFUSED: protocol is not bound to a freeze commit")
    for grp in ("scientific_load_bearing", "governance_provenance"):
        for key, tbl in proto.get(grp, {}).items():
            if not (isinstance(tbl, dict) and "root" in tbl and "files" in tbl):
                continue
            base = ROOTS[tbl["root"]]
            for rel, want in tbl["files"].items():
                p = base / rel
                if not p.is_file():
                    bad.append(f"missing pinned input: {rel}")
                elif sha(p) != want:
                    bad.append(f"pin mismatch: {rel}")
    if sha(NS / "config/FEASIBILITY_GATES_C3.json") != GATE_SHA:
        bad.append("frozen gate identity mismatch")
    if proto.get("governance_provenance", {}).get("new_real_scientific_addresses_authorized") != 0:
        bad.append("protocol authorizes new real addresses; refusing")
    rec = NS / "evidence/freeze/C3_FREEZE_RECORD.json"
    if expect_bound and rec.is_file():
        r = json.loads(rec.read_bytes())
        got = subprocess.run(["git", "show", f"{r['freeze_commit']}:level4/closure_proofs/"
                              "p5y_k5_tail_c3_closure/config/C3_PROTOCOL.json"],
                             capture_output=True, text=True, cwd=str(REPO))
        if got.returncode != 0:
            bad.append("cannot read the protocol at the freeze commit")
        else:
            raw = got.stdout.encode()
            if hashlib.sha256(raw).hexdigest() != r.get("protocol_sha256_unbound_at_freeze"):
                bad.append("protocol at the freeze commit does not match its recorded unbound hash")
            a_, b_ = json.loads(raw), dict(proto)
            a_.pop("freeze", None), b_.pop("freeze", None)
            if a_ != b_:
                bad.append("bound protocol differs from the frozen one outside the freeze block")
    return (not bad), bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("build", "check"))
    ap.add_argument("--out")
    ap.add_argument("--protocol")
    ap.add_argument("--expect-bound", action="store_true")
    a = ap.parse_args()
    if a.mode == "build":
        data = json.dumps(build(), sort_keys=True, indent=1) + "\n"
        Path(a.out).write_text(data)
        print(json.dumps({"written": a.out, "sha256": hashlib.sha256(data.encode()).hexdigest(),
                          "freeze_state": "UNBOUND"}))
        return 0
    proto = json.loads(Path(a.protocol).read_bytes())
    ok, bad = check(proto, a.expect_bound)
    print(json.dumps({"protocol_sha256": sha(Path(a.protocol)), "expect_bound": a.expect_bound,
                      "pass": ok, "problems": bad[:8]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
