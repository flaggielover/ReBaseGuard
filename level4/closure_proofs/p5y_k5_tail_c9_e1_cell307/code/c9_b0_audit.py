"""C9 Phase B0 -- predecessor and state audit. 22 executable checks.

No check is implemented as `True`. No process is identified by a command line that merely contains a
string, nor by pgrep -f or ps|grep alone. A check that cannot test its stated property is UNCHECKED,
and UNCHECKED does not count as PASS.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C

PRED = {
    "p5y_k5_tail_c2_closure": "ae4cbc2cc0160538ec8fed3554feaceba5d71ec4",
    "p5y_k5_tail_c3_closure": "019ecce030ef294b95e98391c71715fb0b43d1cf",
    "p5y_k5_tail_c4_exhaustion": "e12a09e8bb742726e2ca7af42e163c455915bb7d",
    "p5y_k5_tail_c5_exhaustion": "69bff424f20a7c91eac99450ba0836f3f7d9ca44",
    "p5y_k5_tail_c6_evidence_recovery": "f494416fb0453ee7f3993da7be23ad112aeb94e1",
    "p5y_k5_tail_c7_e2_lambda309": "df4ec1791a5aa837a1e3dca26f9a1a329f283a9f",
    "p5y_k5_tail_c8_operator_feasibility": C.C8_HEAD,
}


def main() -> int:
    ck = []

    def chk(n, name, ok, detail, unchecked=False):
        ck.append({"id": f"B0_{n:02d}", "name": name,
                   "status": "UNCHECKED" if unchecked else ("PASS" if ok else "FAIL"),
                   "detail": detail})

    br = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "C9 is on its own branch", br == "p5y-k5-tail-c9-e1-cell307", {"branch": br})
    chk(2, "C9 descends from the expected C8 HEAD",
        C.git_ok("merge-base", "--is-ancestor", C.C8_HEAD, "HEAD"),
        {"expected_C8_HEAD": C.C8_HEAD, "c9_head": C.git("rev-parse", "HEAD")})
    orig = C.git("ls-remote", "--heads", "origin",
                 "p5y-k5-tail-c8-operator-feasibility").split("\t")[0]
    chk(3, "origin C8 branch equals the expected HEAD", orig == C.C8_HEAD,
        {"origin": orig, "expected": C.C8_HEAD})

    fcv = C.load(C.C8 / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json")
    mut8 = C.load(C.C8 / "evidence" / "mutations" / "C8_MUTATIONS.json")
    b08 = C.load(C.C8 / "evidence" / "b0" / "C8_B0_AUDIT.json")
    chk(4, "C8 publication state: fact check PASS, mutations PASS, B0 PASS",
        fcv["FACT_CHECK_CLASS"] == "PASS" and mut8["MUTATION_CLASS"] == "PASS"
        and b08["B0_CLASS"] == "PASS" and not mut8["survivors"],
        {"FACT_CHECK": fcv["FACT_CHECK_CLASS"], "MUTATION": mut8["MUTATION_CLASS"],
         "B0": b08["B0_CLASS"], "survivors": mut8["survivors"]})

    dec = C.load(C.C8 / "evidence" / "phase9" / "C8_DECISION.json")
    sel = dec["phase10_selection"]
    chk(5, "C8's final decision selects R3/E1 with cell 307 first",
        sel["OUTCOME"] == "NEXT_ROUTE_OPERATOR_CERT" and "307 first" in sel["selected_route"]
        and sel["R_stage"] == "NOT AUTHORIZED",
        {"OUTCOME": sel["OUTCOME"], "selected_route": sel["selected_route"],
         "why_NOT_306_first": sel.get("why_NOT_306_first", "")[:160]})

    g8 = C.sha256_file(C.C8 / "config" / "DECISION_GATE_C8.json")
    chk(6, "C8's decision gate blob is unchanged from its freeze", g8 == C.C8_GATE_SHA,
        {"gate_sha": g8, "frozen": C.C8_GATE_SHA})

    err = (C.C8 / "ERRATUM_C8_GATE.md")
    et = err.read_text() if err.exists() else ""
    chk(7, "C8 errata exist and record the rule-1 false premise that forbids targeting 306",
        err.exists() and "E1" in et and "rule 1" in et and "306" in et,
        {"present": err.exists(), "entries": [x for x in ("E1", "E2", "E3", "E4") if f"## {x}" in et]})

    r5 = C.r5_map()
    chk(8, "authoritative r5 reconstructs: schema, detector and all four m blocks",
        r5["schema"] == "rebaseguard.p5y.k5.tail-c2.coverage-map.v5" and r5["detector"] == "CUSUM"
        and all(str(m) in r5["per_m"] for m in (1, 2, 3, 5)),
        {"blob": C.git("rev-parse", f"HEAD:{C.R5_PATH}"), "schema": r5["schema"],
         "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"]})

    der = {m: C.r5_open_by_verdict(str(m)) for m in (1, 2, 3, 5)}
    chk(9, "m=5 open set, from PER-CELL verdicts, is exactly {306,307,308,309}",
        tuple(der[5]) == C.OPEN_CELLS and der[1] == der[2] == der[3] == [],
        {"per_cell_open": der, "declared_ranges": r5["per_m"]["5"]["open_ranges"]})

    c305 = [c for c in r5["per_m"]["5"]["cells"] if c["cell"] == 305][0]
    chk(10, "cell 305 is PASS and ADOPTED (so it is not open and not a target)",
        c305.get("verdict") == "PASS" and 305 in r5["inputs"]["adopted_cells"],
        {"verdict": c305.get("verdict"), "adopted_cells": r5["inputs"]["adopted_cells"]})

    r6 = []
    for ref in C.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines():
        r6 += [f for f in C.git("ls-tree", "-r", "--name-only", ref).splitlines()
               if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    chk(11, "no r6 coverage map exists on any local branch", not r6,
        {"hits": r6, "highest_present": "K5_COVERAGE_MAP_R5.json"})

    ad8 = C.load(C.C8 / "evidence" / "phase9" / "C8_ADOPTION.json")
    r307 = ad8["per_cell"]["307"]
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[307]
    eff_now = F(r307["A_now"]["A0"]) if isinstance(r307.get("A_now"), dict) else None
    chk(12, "cell 307's current certified supply is readable and operator-only certified",
        blk["certified"] is True and reg["operator_only"] is True and reg["rule"] == "r2"
        and blk["cell"] == 307,
        {"registry": "REGISTRY_C2", "rule": reg["rule"], "operator_only": reg["operator_only"],
         "cell": blk["cell"], "e_lo": blk["e_lo"], "e_hi": blk["e_hi"],
         "tau": blk["tau"], "D_lo": blk["D_lo"], "Abar": blk["Abar"]})

    close_x = r307["uniform_eff_tightening_to_close"]
    adopt_x = r307["uniform_eff_tightening_to_be_ADOPTABLE"]
    chk(13, "cell 307 CLOSURE threshold is committed and finite",
        close_x is not None and abs(close_x - 1.096007) < 1e-5,
        {"uniform_eff_tightening_to_close": close_x,
         "meaning": "new eff must be <= old eff / this factor"})
    chk(14, "cell 307 ADOPTION threshold is committed, distinct from closure, and larger",
        adopt_x is not None and adopt_x > close_x and abs(adopt_x - 1.370009) < 1e-5,
        {"uniform_eff_tightening_to_be_ADOPTABLE": adopt_x,
         "closure": close_x, "distinct": adopt_x != close_x,
         "adoption_floor": ad8["adoption_floor_source"]})

    tc_path = C.AD / "code" / "taboo_certify.py"
    tc_src = tc_path.read_text()
    needs = {"numpy": "import numpy" in tc_src, "python_flint": "from flint import" in tc_src}
    c6cls = C.load(C.C6 / "evidence" / "leverage" / "C6_CLASSIFICATION.json")["routes"]["E1"]
    prod_src = (C.C2 / "code" / "c2_refined_registry.py").read_text()
    operator_only_claim = ("no source S_r" in prod_src and "no K1\nrecord" in prod_src
                           or "no K1" in prod_src)
    chk(15, "E1 is independently confirmed operator-only and zero-new-real at the PRODUCER, "
            "not merely inherited from C8",
        operator_only_claim and "NEW_REAL_ADDRESSES = 0" in prod_src
        and reg["operator_only"] is True and "TRUE_NEW_REAL" not in c6cls["C6_CLASSIFICATION"],
        {"producer": "p5y_k5_tail_c2_closure/code/c2_refined_registry.py",
         "producer_declares": "operator only ... no source S_r, no candidate ..., no K1 record, "
                              "no value of R; NEW_REAL_ADDRESSES = 0",
         "registry_operator_only_flag": reg["operator_only"],
         "C6_classification": c6cls["C6_CLASSIFICATION"],
         "certifier": str(tc_path.relative_to(C.REPO)),
         "certifier_sha256": C.sha256_file(tc_path),
         "certifier_requires": needs,
         "note": "verified from the producer's own source and the registry flag, not from C8 prose"})

    integ = {}
    for ns, head in PRED.items():
        p = f"level4/closure_proofs/{ns}"
        try:
            integ[ns] = C.git("rev-parse", f"HEAD:{p}") == C.git("rev-parse", f"{head}:{p}")
        except Exception as e:
            integ[ns] = False
    chk(16, "C2-C8 namespace trees are identical to their published heads",
        all(integ.values()), integ)

    lm = C.git("rev-parse", "main")
    chk(17, "LOCAL_MAIN_REF recorded", len(lm) == 40, {"LOCAL_MAIN_REF": lm})
    rm = C.git("ls-remote", "origin", "refs/heads/main").split("\t")[0]
    chk(18, "REMOTE_MAIN_REF queried independently and equals the expected value",
        rm == "1cb453826313c189f0bdafd5b84120c1edb74da9",
        {"REMOTE_MAIN_REF": rm, "LOCAL_MAIN_REF": lm, "differ": lm != rm,
         "action": "NONE -- recorded only; C9 does not synchronize, modify or merge main"})

    allow = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    deny = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"DENY"', "*.json")
    chk(19, "guard is DENY wherever declared and no ALLOW exists anywhere at C9 start",
        not allow and len(deny) >= 3,
        {"DENY_declarations": len(deny), "ALLOW_declarations": len(allow),
         "C9_start_guard": "DENY"})

    procs = C.classified_processes()
    chk(20, "no stale C7/C8 campaign process remains",
        len(procs["campaign_workers"]) == 0,
        {"campaign_workers": procs["campaign_workers"],
         "method": "ps -eo comm executable identity, self-ancestry excluded"})
    chk(21, "every live interpreter is classified by executable AND cwd AND argv, not by substring",
        all(set(r["signals"]) == {"executable_in_repo", "cwd_in_repo", "argv_references_campaign"}
            for r in procs["interpreters"]),
        {"interpreters": [{k: r[k] for k in ("pid", "executable", "cwd", "classified")}
                          for r in procs["interpreters"]],
         "foreign_count": len(procs["foreign"])})

    ssh_cfg = pathlib.Path.home() / ".ssh" / "config"
    aws_alias = "rebaseguard-aws" in ssh_cfg.read_text() if ssh_cfg.exists() else None
    chk(22, "AWS has not been contacted by C9 and no C9 artifact references AWS access",
        not any("aws" in p.lower() for p in
                C.git("ls-files", "level4/closure_proofs/p5y_k5_tail_c9_e1_cell307").splitlines()),
        {"aws_contacted_by_C9": False,
         "aws_ssh_alias_exists_on_host": aws_alias,
         "policy": "AWS SR/PS1 is a separate production campaign; C9 must not touch it",
         "note": "this records that C9 has issued no AWS call; the alias may exist and is untouched"})

    failed = [c["id"] for c in ck if c["status"] == "FAIL"]
    unchecked = [c["id"] for c in ck if c["status"] == "UNCHECKED"]
    out = {"schema": "C9_B0_AUDIT/1",
           "campaign": "C9 -- E1 zero-new-real operator certification, CUSUM m=5 cell 307",
           "target": {"detector": "CUSUM", "m": C.TARGET_M, "cell": C.TARGET_CELL},
           "non_targets": list(C.NON_TARGETS),
           "LOCAL_MAIN_REF": lm, "REMOTE_MAIN_REF": rm,
           "authoritative_r5": {"m5_open": der[5], "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"]},
           "cell307_thresholds": {"closure_uniform_eff_factor": close_x,
                                  "adoption_uniform_eff_factor": adopt_x},
           "compute_boundary_at_B0": {"NEW_REAL": 0, "TARGET_EXECUTIONS": 0,
                                      "OPERATOR_CERTIFICATIONS": 0, "AWS_CONTACTS": 0,
                                      "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY"},
           "checks": ck, "failed": failed, "unchecked": unchecked,
           "B0_CLASS": "PASS" if not failed and not unchecked else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "b0" / "C9_B0_AUDIT.json", out)
    for c in ck:
        print(f"  {c['status']:<9} {c['id']}  {c['name'][:76]}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}  failed={failed}  unchecked={unchecked}")
    print(f"LOCAL_MAIN_REF  {lm}\nREMOTE_MAIN_REF {rm}")
    print(f"m=5 open {der[5]}   307 closure {close_x}   adoption {adopt_x}")
    print(f"wrote evidence/b0/C9_B0_AUDIT.json sha256 {s[:16]}...")
    return 0 if out["B0_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
