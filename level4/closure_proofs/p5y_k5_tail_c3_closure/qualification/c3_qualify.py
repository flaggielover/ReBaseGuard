"""Qualify the frozen C3 successor against a clean tree checked out at the C3 freeze commit.

Not part of the frozen set: it audits the freeze and is committed after it. Its sha256 is recorded in the artifact.
Reports PASS / FAIL / SKIPPED per check and is QUALIFIED only when nothing failed and no load-bearing check was
skipped.

    python3 -B c3_qualify.py --tree <clean clone at the C3 freeze> --binding-commit <sha> --out OUT.json
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c3_closure"
C2REL = "level4/closure_proofs/p5y_k5_tail_c2_closure"
GATE_SHA = "f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7"
R5_SHA = "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c"
R4_SHA = "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"
EXPECT = {"C3_CLASS": "PARTIAL", "closed": [306], "adoptable": [], "still_open": [307, 308, 309],
          "Gamma": {"306": -0.03619778, "307": 0.026354631, "308": 0.094564145, "309": 0.153019689}}
LOAD_BEARING = {"protocol_pins", "gate_identity", "gate_frozen_before_forecast", "r5_r4_intact_no_r6",
                "forecast_reproduction", "producer_determinism", "mutation_suite", "selector_refusals",
                "adoption_floor_reproduction", "class_reproduction", "no_new_real", "guard_deny",
                "refusal_unbound", "refusal_tampered_pin", "c2_untouched"}


def sb(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd),
                          env=dict(os.environ, PYTHONINTMAXSTRDIGITS="0"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--binding-commit", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    ns = tree / NSREL
    rows = {}

    def rec(n, ok, det, skipped=False):
        rows[n] = {"verdict": "SKIPPED" if skipped else ("PASS" if ok else "FAIL"), "detail": det}

    head = run(["git", "rev-parse", "HEAD"], tree).stdout.strip()
    rec("clean_tree_at_freeze", run(["git", "status", "--porcelain"], tree).stdout.strip() == "",
        {"head": head})

    proto_raw = (ns / "config/C3_PROTOCOL.json").read_bytes()
    proto = json.loads(proto_raw)
    frec = json.loads(run(["git", "show", f"{a.binding_commit}:{NSREL}/evidence/freeze/C3_FREEZE_RECORD.json"],
                          tree).stdout.encode())
    rec("freeze_record_binds_this_tree",
        frec["freeze_commit"] == head and frec["protocol_sha256_unbound_at_freeze"] == sb(proto_raw),
        {"freeze_commit": frec["freeze_commit"][:8]})
    bound_raw = run(["git", "show", f"{a.binding_commit}:{NSREL}/config/C3_PROTOCOL.json"], tree).stdout.encode()
    x, y = json.loads(bound_raw), dict(proto)
    x.pop("freeze"), y.pop("freeze")
    rec("binding_changed_only_freeze_block", x == y and sb(bound_raw) == frec["protocol_sha256_bound"], {})

    roots = {"namespace": ns, "closure_proofs": tree / "level4/closure_proofs"}
    bad, n = [], 0
    for grp in ("scientific_load_bearing", "governance_provenance"):
        for key, tbl in proto[grp].items():
            if not (isinstance(tbl, dict) and "files" in tbl):
                continue
            for rel, want in tbl["files"].items():
                n += 1
                p = roots[tbl["root"]] / rel
                if not p.is_file():
                    bad.append(f"missing {rel}")
                elif sb(p.read_bytes()) != want:
                    bad.append(f"mismatch {rel}")
    rec("protocol_pins", not bad, {"pins_checked": n, "problems": bad[:6]})

    rec("gate_identity", sb((ns / "config/FEASIBILITY_GATES_C3.json").read_bytes()) == GATE_SHA,
        {"sha256": GATE_SHA[:16]})

    # the gate commit must contain NO forecast artifact
    gate_commit = proto["governance_provenance"]["gate"]["commit"]
    tree_at_gate = run(["git", "ls-tree", "-r", "--name-only", gate_commit, "--", NSREL], tree).stdout
    rec("gate_frozen_before_forecast",
        "C3_FORECAST" not in tree_at_gate and len(run(
            ["git", "log", "--format=%h", "--all", "--", f"{NSREL}/config/FEASIBILITY_GATES_C3.json"],
            tree).stdout.split()) == 1,
        {"gate_commit": gate_commit, "forecast_present_at_gate": "C3_FORECAST" in tree_at_gate})

    r5 = tree / C2REL / "evidence/coverage/K5_COVERAGE_MAP_R5.json"
    r4 = tree / "level4/closure_proofs/p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json"
    r6 = list((tree / "level4").rglob("*COVERAGE_MAP_R6*"))
    rec("r5_r4_intact_no_r6", sb(r5.read_bytes()) == R5_SHA and sb(r4.read_bytes()) == R4_SHA and not r6,
        {"r5": R5_SHA[:16], "r4": R4_SHA[:16], "r6_found": len(r6)})

    c2diff = run(["git", "diff", "--name-only", "ae4cbc2c", head, "--", C2REL], tree).stdout.strip()
    rec("c2_untouched", c2diff == "", {"changed_in_c2_namespace": c2diff.splitlines()[:5]})

    out = Path(a.out).parent
    out.mkdir(parents=True, exist_ok=True)
    det = {}
    for mod, art in (("c3_blocker.py", "evidence/phase_c1/C3_BLOCKER.json"),
                     ("c3_mutations.py", "evidence/preforecast/C3_MUTATIONS.json"),
                     ("c3_forecast.py", "evidence/forecast/C3_FORECAST.json")):
        dst = out / ("qual_" + Path(art).name)
        p = run([sys.executable, "-B", f"code/{mod}", "--out", str(dst)], ns)
        det[mod] = {"byte_identical": dst.is_file() and dst.read_bytes() == (ns / art).read_bytes(),
                    "rc": p.returncode}
    rec("producer_determinism", all(v["byte_identical"] for v in det.values()), det)

    mut = json.loads((out / "qual_C3_MUTATIONS.json").read_bytes()) if (out / "qual_C3_MUTATIONS.json").is_file() else {}
    rec("mutation_suite", bool(mut) and mut.get("pass") and not mut.get("undetected"),
        {k: mut.get(k) for k in ("applied", "killed", "proved_equivalent", "undetected", "pass")})

    fc = json.loads((ns / "evidence/forecast/C3_FORECAST.json").read_bytes())
    rec("forecast_reproduction", det["c3_forecast.py"]["byte_identical"], {})
    rec("class_reproduction",
        fc["C3_CLASS"] == EXPECT["C3_CLASS"] and fc["closed"] == EXPECT["closed"]
        and fc["adoptable"] == EXPECT["adoptable"] and fc["still_open"] == EXPECT["still_open"],
        {"C3_CLASS": fc["C3_CLASS"], "closed": fc["closed"], "adoptable": fc["adoptable"],
         "still_open": fc["still_open"], "materially_tightened": fc["materially_tightened"]})
    rec("adoption_floor_reproduction",
        all(not fc["cells"][k]["adoption_floor"]["meets_floor"] for k in fc["cells"]),
        {k: fc["cells"][k]["adoption_floor"] for k in fc["cells"]})

    p = run([sys.executable, "-B", "code/c3_protocol.py", "check", "--protocol", "config/C3_PROTOCOL.json",
             "--expect-bound"], ns)
    rec("refusal_unbound", p.returncode != 0 and "REFUSED" in p.stdout, {"rc": p.returncode})
    tam = out / "qual_tampered.json"
    d = json.loads(proto_raw)
    d["scientific_load_bearing"]["evidence"]["files"]["evidence/forecast/C3_FORECAST.json"] = "0" * 64
    tam.write_text(json.dumps(d, sort_keys=True, indent=1) + "\n")
    p = run([sys.executable, "-B", "code/c3_protocol.py", "check", "--protocol", str(tam)], ns)
    rec("refusal_tampered_pin", p.returncode != 0 and "pin mismatch" in p.stdout, {"rc": p.returncode})

    src = (ns / "code/c3_selector.py").read_text()
    rec("selector_refusals",
        "whole_cell_ok" in src and "violates a Lemma Dv' premise" in src and "GATE_SHA" in src, {})

    gov = proto["governance_provenance"]
    rec("no_new_real", gov["new_real_scientific_addresses_authorized"] == 0
        and fc["new_real_scientific_addresses_evaluated"] == 0, {"authorized": 0, "evaluated": 0})
    rec("guard_deny", "DENY" in gov["guard"], {"guard": gov["guard"]})
    rec("proposes_nothing", gov["proposes_for_adoption"] == [] and fc["adoptable"] == [], {})

    failed = [k for k, v in rows.items() if v["verdict"] == "FAIL"]
    skipped_lb = [k for k, v in rows.items() if v["verdict"] == "SKIPPED" and k in LOAD_BEARING]
    verdict = "QUALIFIED" if not failed and not skipped_lb else ("FAILED" if failed else "INCOMPLETE")
    res = {"schema": "rebaseguard.p5y.k5.tail-c3.qualification.v1", "verdict": verdict,
           "failed": failed, "skipped_load_bearing": skipped_lb,
           "freeze_commit": head, "binding_commit": a.binding_commit,
           "qualifier_sha256": sb(Path(__file__).read_bytes()),
           "qualifier_note": "not part of the frozen set; audits it", "checks": rows}
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"verdict": verdict, "failed": failed, "skipped": skipped_lb,
                      "checks": {k: v["verdict"] for k, v in rows.items()}}, indent=1))
    return 0 if verdict == "QUALIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
