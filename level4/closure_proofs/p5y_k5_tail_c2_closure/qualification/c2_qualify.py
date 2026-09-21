"""Qualify the frozen C2 D-stage successor, running against a clean tree checked out at the freeze commit.

This file is deliberately NOT part of the frozen set. It audits the freeze; it is not one of the producers the
protocol pins, and it is committed after the freeze so that adding it cannot alter what was frozen. Its own sha256
is recorded in the qualification artifact.

It refuses to certify anything it did not run: every check reports PASS, FAIL or SKIPPED, and the verdict is
QUALIFIED only when no check failed and no load-bearing check was skipped.

    python3 -B c2_qualify.py --tree /path/to/clean/clone --binding-commit <sha> --out OUT.json
                             [--with-registry] [--with-recert]

`--with-registry` re-certifies all 105 registry artifacts (~2.7 h) and `--with-recert` re-runs cell 306's eighteen
artifacts at both precisions (~40 min); both need numpy/python-flint. Without them those two rows are SKIPPED and
the verdict cannot be QUALIFIED.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NSREL = "level4/closure_proofs/p5y_k5_tail_c2_closure"
GATE_SHA = "098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f"
R4_SHA = "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"
EXPECT = {"class": "D_PARTIAL", "closed": [305, 306], "open": [307, 308, 309],
          "gap": {"307": 0.462851835, "308": 0.245930994, "309": 0.183898411},
          "gamma": {"305": -0.088029069, "306": -0.030469258}}
LOAD_BEARING = {"protocol_pins", "gate_identity", "predecessor_B0", "result_classification",
                "producer_determinism", "mutation_suite", "registry_certification",
                "recertify_306", "refusal_tampered_pin", "refusal_unbound", "no_new_real", "guard_deny"}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd, env=None):
    import os
    e = dict(os.environ, PYTHONINTMAXSTRDIGITS="0")
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), env=e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--binding-commit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--with-registry", action="store_true")
    ap.add_argument("--with-recert", action="store_true")
    a = ap.parse_args()

    tree = Path(a.tree).resolve()
    ns = tree / NSREL
    rows = {}

    def rec(name, ok, detail, skipped=False):
        rows[name] = {"verdict": "SKIPPED" if skipped else ("PASS" if ok else "FAIL"), "detail": detail}

    head = run(["git", "rev-parse", "HEAD"], tree).stdout.strip()
    dirty = run(["git", "status", "--porcelain"], tree).stdout.strip()
    rec("clean_tree_at_freeze", dirty == "", {"head": head, "dirty": dirty})

    # --- the frozen tree carries the UNBOUND protocol; the binding lives in a later commit -------------------
    proto_raw = (ns / "config/C2_PROTOCOL.json").read_bytes()
    proto = json.loads(proto_raw)
    frec_raw = run(["git", "show", f"{a.binding_commit}:{NSREL}/evidence/freeze/C2_FREEZE_RECORD.json"],
                   tree).stdout.encode()
    frec = json.loads(frec_raw)
    rec("freeze_record_binds_this_tree",
        frec["freeze_commit"] == head and frec["protocol_sha256_unbound_at_freeze"] == sha_bytes(proto_raw),
        {"freeze_commit": frec["freeze_commit"], "unbound_sha_matches": True})

    bound_raw = run(["git", "show", f"{a.binding_commit}:{NSREL}/config/C2_PROTOCOL.json"], tree).stdout.encode()
    bound = json.loads(bound_raw)
    x, y = dict(bound), dict(proto)
    x.pop("freeze"), y.pop("freeze")
    rec("binding_changed_only_freeze_block",
        x == y and sha_bytes(bound_raw) == frec["protocol_sha256_bound"] and bound["freeze"]["state"] == "BOUND",
        {"bound_sha": frec["protocol_sha256_bound"][:16]})

    # --- protocol pins over the frozen tree --------------------------------------------------------------
    bad = []
    roots = {"namespace": ns, "closure_proofs": tree / "level4/closure_proofs"}
    npins = 0
    for grp in ("scientific_load_bearing", "governance_provenance"):
        for key, tbl in proto[grp].items():
            if not (isinstance(tbl, dict) and "files" in tbl):
                continue
            for rel, want in tbl["files"].items():
                npins += 1
                p = roots[tbl["root"]] / rel
                if not p.is_file():
                    bad.append(f"missing {rel}")
                elif sha_bytes(p.read_bytes()) != want:
                    bad.append(f"mismatch {rel}")
    rec("protocol_pins", not bad, {"pins_checked": npins, "problems": bad[:8]})

    rec("gate_identity",
        sha_bytes((ns / "config/FEASIBILITY_GATES_C2.json").read_bytes()) == GATE_SHA
        and len(run(["git", "log", "--format=%h", "--all", "--", f"{NSREL}/config/FEASIBILITY_GATES_C2.json"],
                    tree).stdout.split()) == 1,
        {"sha256": GATE_SHA[:16], "commits_in_history": 1})

    r4 = tree / "level4/closure_proofs/p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json"
    r5 = list((tree / "level4").rglob("*COVERAGE_MAP_R5*"))
    rec("input_map_r4_intact_no_r5", sha_bytes(r4.read_bytes()) == R4_SHA and not r5,
        {"r4_sha256": R4_SHA[:16], "r5_found": [str(p) for p in r5]})

    # --- producers, re-run inside the frozen tree ----------------------------------------------------------
    out = Path(a.out).parent
    out.mkdir(parents=True, exist_ok=True)
    det, mut = {}, None
    for mod, art in (("c2_d1_blocker.py", "evidence/phase_d1/C2_D1_BLOCKER.json"),
                     ("c2_mutations.py", "evidence/prefreeze/C2_MUTATIONS.json"),
                     ("c2_critical_ratio.py", "evidence/phase_d5/C2_CRITICAL_RATIOS.json")):
        dst = out / ("qual_" + Path(art).name)
        p = run([a.python, "-B", f"code/{mod}", "--out", str(dst)], ns)
        same = dst.is_file() and dst.read_bytes() == (ns / art).read_bytes()
        det[mod] = {"byte_identical": same, "rc": p.returncode}
        if mod == "c2_mutations.py" and dst.is_file():
            mut = json.loads(dst.read_bytes())
    rec("producer_determinism", all(v["byte_identical"] for v in det.values()), det)
    rec("mutation_suite", bool(mut) and mut["pass"] and not mut["undetected"],
        {} if not mut else {"applied": mut["applied"], "detected": mut["detected"],
                            "undetected": mut["undetected"], "pass": mut["pass"]})

    b0dst = out / "qual_B0.json"
    run([a.python, "-B", "code/c2_b0_verify.py", "--out", str(b0dst)], ns)
    b0 = json.loads(b0dst.read_bytes()) if b0dst.is_file() else {}
    rec("predecessor_B0", bool(b0.get("ALL_PASS")), {k: v for k, v in b0.items() if k.startswith("B")})

    # --- the frozen result -------------------------------------------------------------------------------
    f = json.loads((ns / "evidence/phase_d5/C2_D5_FORECAST.json").read_bytes())
    cells = f["cells"]
    ok = (f["D_STAGE_CLASS"] == EXPECT["class"] and f["closed"] == EXPECT["closed"]
          and f["still_open"] == EXPECT["open"]
          and all(round(cells[k]["gap_fall_fraction"], 9) == v for k, v in EXPECT["gap"].items())
          and all(round(cells[k]["Gamma"], 9) == v for k, v in EXPECT["gamma"].items()))
    rec("result_classification", ok,
        {"class": f["D_STAGE_CLASS"], "closed": f["closed"], "open": f["still_open"],
         "gap_fall": {k: cells[k]["gap_fall_fraction"] for k in EXPECT["gap"]},
         "Gamma": {k: cells[k]["Gamma"] for k in EXPECT["gamma"]},
         "gate_sha256_pinned_in_forecast": f["gate_sha256"] == GATE_SHA})

    # --- refusals -----------------------------------------------------------------------------------------
    p = run([a.python, "-B", "code/c2_protocol.py", "check", "--protocol", "config/C2_PROTOCOL.json",
             "--expect-bound"], ns)
    rec("refusal_unbound", p.returncode != 0 and "REFUSED" in p.stdout, {"rc": p.returncode})

    tam = out / "qual_tampered_protocol.json"
    d = json.loads(proto_raw)
    d["scientific_load_bearing"]["evidence"]["files"]["evidence/phase_d5/C2_D5_FORECAST.json"] = "0" * 64
    tam.write_text(json.dumps(d, sort_keys=True, indent=1) + "\n")
    p = run([a.python, "-B", "code/c2_protocol.py", "check", "--protocol", str(tam)], ns)
    rec("refusal_tampered_pin", p.returncode != 0 and "pin mismatch" in p.stdout, {"rc": p.returncode})

    src = (ns / "code/c2_d5_forecast.py").read_text()
    rec("consumer_refuses_order3_fields", 'order3_fields_present' in src and "raise SystemExit" in src,
        {"guard_present": True})

    gov = proto["governance_provenance"]
    rec("no_new_real", gov["new_real_scientific_addresses_authorized"] == 0,
        {"authorized": gov["new_real_scientific_addresses_authorized"]})
    rec("guard_deny", "DENY" in gov["guard"], {"guard": gov["guard"]})

    # --- the two long, toolchain-dependent checks ---------------------------------------------------------
    if a.with_registry:
        dst = out / "qual_REGISTRY_VERIFY.json"
        p = run([a.python, "-B", "code/c2_refined_registry.py", "verify", "--outdir", "evidence/registry_c2",
                 "--out", str(dst)], ns)
        r = json.loads(dst.read_bytes()) if dst.is_file() else {}
        rec("registry_certification", bool(r.get("pass")) and not r.get("problems"),
            {"pass": r.get("pass"), "artifacts_rechecked": r.get("artifacts_rechecked"),
             "cells_checked": r.get("cells_checked"), "problems": (r.get("problems") or [])[:5]})
    else:
        rec("registry_certification", False, {"reason": "not run: --with-registry not given"}, skipped=True)

    if a.with_recert:
        dst = out / "qual_RECERTIFY_306.json"
        p = run([a.python, "-B", "code/c2_recertify_306.py", "--out", str(dst)], ns)
        r = json.loads(dst.read_bytes()) if dst.is_file() else {}
        rec("recertify_306", r.get("verdict") == "BOTH_PASSES_OK",
            {"verdict": r.get("verdict"),
             "passes": {k: v["all_ok"] for k, v in (r.get("passes") or {}).items()}})
    else:
        rec("recertify_306", False, {"reason": "not run: --with-recert not given"}, skipped=True)

    failed = [k for k, v in rows.items() if v["verdict"] == "FAIL"]
    skipped_lb = [k for k, v in rows.items() if v["verdict"] == "SKIPPED" and k in LOAD_BEARING]
    verdict = "QUALIFIED" if not failed and not skipped_lb else ("FAILED" if failed else "INCOMPLETE")

    res = {"schema": "rebaseguard.p5y.k5.tail-c2.qualification.v1",
           "verdict": verdict, "failed": failed, "skipped_load_bearing": skipped_lb,
           "freeze_commit": head, "binding_commit": a.binding_commit,
           "protocol_sha256_unbound_at_freeze": sha_bytes(proto_raw),
           "qualifier_sha256": sha_bytes(Path(__file__).read_bytes()),
           "qualifier_note": "not part of the frozen set; audits it",
           "tree": str(tree), "checks": rows}
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"verdict": verdict, "failed": failed, "skipped_load_bearing": skipped_lb,
                      "checks": {k: v["verdict"] for k, v in rows.items()}}, indent=1))
    return 0 if verdict == "QUALIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
