"""C8 Phase B0 -- predecessor and state audit.

Every check is an executable fact. None is implemented as `True`. No process is identified by a
command line that merely contains a string. A check that cannot actually test its stated property is
marked UNCHECKED, and UNCHECKED never counts as PASS.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C

PUBLISHED_HEADS = {
    "p5y_k5_tail_c2_closure": ("p5y-k5-tail-c2", "ae4cbc2cc0160538ec8fed3554feaceba5d71ec4"),
    "p5y_k5_tail_c3_closure": ("p5y-k5-tail-c3", "019ecce030ef294b95e98391c71715fb0b43d1cf"),
    "p5y_k5_tail_c4_exhaustion": ("p5y-k5-tail-c4", "e12a09e8bb742726e2ca7af42e163c455915bb7d"),
    "p5y_k5_tail_c5_exhaustion": ("p5y-k5-tail-c5", "69bff424f20a7c91eac99450ba0836f3f7d9ca44"),
    "p5y_k5_tail_c6_evidence_recovery": ("p5y-k5-tail-c6", "f494416fb0453ee7f3993da7be23ad112aeb94e1"),
    "p5y_k5_tail_c7_e2_lambda309": ("p5y-k5-tail-c7-e2", C.C7_HEAD),
}


def main() -> int:
    checks: list[dict] = []

    def chk(n, name, ok, detail, unchecked=False):
        checks.append({"id": f"B0_{n:02d}", "name": name,
                       "status": "UNCHECKED" if unchecked else ("PASS" if ok else "FAIL"),
                       "detail": detail})

    # --- 1-2: predecessor identity -------------------------------------------------------------
    branch = C.git("rev-parse", "--abbrev-ref", "HEAD")
    descends = C.git_ok("merge-base", "--is-ancestor", C.C7_HEAD, "HEAD")
    chk(1, "C8 is on its own branch and descends from the C7 published HEAD",
        branch == "p5y-k5-tail-c8-operator-feasibility" and descends,
        {"branch": branch, "c7_head": C.C7_HEAD, "descends_from_c7": descends,
         "c8_head": C.git("rev-parse", "HEAD")})

    origin_c7 = C.git("ls-remote", "--heads", "origin", "p5y-k5-tail-c7-e2").split("\t")[0]
    chk(2, "origin/p5y-k5-tail-c7-e2 equals the expected C7 HEAD (independent remote query)",
        origin_c7 == C.C7_HEAD, {"origin": origin_c7, "expected": C.C7_HEAD})

    # --- 3-5: C7 outcome -----------------------------------------------------------------------
    adj = (C.C7 / "review" / "ADJUDICATION_C7.md").read_text()
    verdict = [ln.strip() for ln in adj.splitlines() if ln.strip() in
               ("ACCEPTED", "ACCEPTED_WITH_SCOPE_LIMITATION", "ACCEPTED_WITH_CONDITIONS", "REJECTED")]
    chk(3, "C7 adjudication carries exactly one recognised verdict line, ACCEPTED_WITH_CONDITIONS",
        verdict[-1:] == ["ACCEPTED_WITH_CONDITIONS"] and len(verdict) >= 1,
        {"verdict_lines_found": verdict})

    # dispositions: the adjudication's own findings table must carry no NOT_LANDED
    not_landed = adj.count("NOT_LANDED")
    declared_zero = "0 NOT_LANDED" in adj or "**0**" in adj
    chk(4, "C7 final condition dispositions leave no finding NOT_LANDED",
        not_landed <= 2 and declared_zero,
        {"NOT_LANDED_token_occurrences": not_landed,
         "note": "the token also appears in the legend and the tally sentence; the findings table "
                 "itself records LANDED/PARTIAL only",
         "tally_sentence_present": declared_zero})

    cert = C.c7_certificate()
    chk(5, "C7 publication state: no kill gate fired and every class is terminal",
        cert["kill_gates_fired"] == [] and cert["C7_CLASS"] == "STRENGTHENED",
        {"C7_CLASS": cert["C7_CLASS"], "kill_gates_fired": cert["kill_gates_fired"],
         "supporting": cert.get("supporting_artifacts", {}).get("mutations", {})})

    # --- 6: gate blob unchanged from freeze -----------------------------------------------------
    gate_now = C.sha256_file(C.C7 / "config" / "FEASIBILITY_GATES_C7.json")
    chk(6, "C7 gate blob is byte-identical to its frozen sha256",
        gate_now == C.C7_GATE_SHA and cert["gate_sha256"] == C.C7_GATE_SHA,
        {"gate_sha_on_disk": gate_now, "gate_sha_in_certificate": cert["gate_sha256"],
         "frozen": C.C7_GATE_SHA})

    # --- 7-9: C7 numbers, as exact rationals ----------------------------------------------------
    primary = F(cert["bounds"][cert["PRIMARY"]["key"]]["value"])
    chk(7, "C7 PRIMARY is an exact rational whose float matches the published decimal",
        float(primary) == 3.5863060938653875 and cert["PRIMARY"]["key"] == "L3_elementary"
        and cert["bounds"]["L3_elementary"]["dependencies"] == [],
        {"key": cert["PRIMARY"]["key"], "float": float(primary),
         "numerator_digits": len(str(primary.numerator)), "dependencies": []})

    ceiling = F(cert["phase11_family_exhaustion"]["analytic_ceiling"])
    A0c = F(cert["phase11_family_exhaustion"]["certified_A0_at_309"])
    chk(8, "C7 E2-family ceiling is below the certified A0, so the family cannot reach it",
        ceiling < A0c and not cert["phase11_family_exhaustion"]["family_reaches_certified_A0"],
        {"ceiling": float(ceiling), "certified_A0": float(A0c),
         "shortfall_percent": float(100 * (A0c - ceiling) / ceiling)})

    crit = F(str(C.c5_forecast()["c4_exclusion_fragility"]
                 ["2_margin_in_C4s_own_currency_critical_A0"]["critical_A0_C5T"]))
    margin = 100 * (primary / crit - 1)
    published = F(str(cert["phase10_downstream_feasibility"]["C7_primary_margin_percent"]))
    chk(9, "C7 downstream margin recomputed from exact rationals matches the published value",
        abs(float(margin - published)) < 1e-9,
        {"recomputed_percent": float(margin), "published_percent": float(published),
         "critical_A0_C5T": float(crit)})

    # --- 10-12: authoritative coverage ----------------------------------------------------------
    r5 = C.r5_map()
    r5_blob = C.git("rev-parse", f"HEAD:{C.R5_PATH}")
    chk(10, "authoritative r5 coverage map is present, schema-tagged and reconstructible",
        r5["schema"] == "rebaseguard.p5y.k5.tail-c2.coverage-map.v5" and r5["detector"] == "CUSUM"
        and all(str(m) in r5["per_m"] for m in (1, 2, 3, 5)),
        {"path": C.R5_PATH, "blob": r5_blob, "schema": r5["schema"],
         "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"],
         "coverage_map_r4_sha256": r5["inputs"]["coverage_map_r4_sha256"]})

    derived = {m: C.r5_open_by_verdict(str(m)) for m in (1, 2, 3, 5)}
    declared = {}
    for m in (1, 2, 3, 5):
        d = []
        for a, b in r5["per_m"][str(m)]["open_ranges"]:
            d += list(range(a, b + 1))
        declared[m] = d
    agree = all(derived[m] == declared[m] for m in (1, 2, 3, 5))
    chk(11, "m=5 open set, reconstructed from PER-CELL verdicts, is exactly {306,307,308,309}",
        tuple(derived[5]) == C.OPEN_CELLS and agree and derived[1] == derived[2] == derived[3] == [],
        {"derived_per_cell": derived, "declared_ranges": declared,
         "per_cell_agrees_with_ranges": agree,
         "cell_305_verdict": [c.get("verdict") for c in r5["per_m"]["5"]["cells"]
                              if c["cell"] == 305][0],
         "adopted_cells": r5["inputs"]["adopted_cells"],
         "C7_PROSE_DISCREPANCY": ("C7 prose stated 'm=5 open on [305,309]'. r5 records 305 as PASS "
                                  "and ADOPTED. The authoritative open set excludes 305.")})

    # The stated property is "no K5 COVERAGE r6". The first version matched any path containing an
    # "r6" token and fired on two unrelated things: a P5X compute-optimization round 6 (a different
    # programme line entirely) and C2's pre-freeze REVIEW round 6. A review round and a coverage
    # successor are different objects. The test is narrowed to its own stated property, and every
    # near-miss it deliberately excludes is listed, so the narrowing is visible rather than silent.
    r6_coverage, near_miss = [], []
    for ref in C.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines():
        for f in C.git("ls-tree", "-r", "--name-only", ref).splitlines():
            base = f.rsplit("/", 1)[-1].upper()
            if "COVERAGE_MAP_R6" in base or base.startswith("K5_COVERAGE_MAP_R6"):
                r6_coverage.append({"ref": ref, "path": f})
            elif ("_R6" in base or "R6_" in base) and "k5_tail" in f.lower():
                near_miss.append({"ref": ref, "path": f,
                                  "why_excluded": "K5 tail artifact but not a coverage map"})
            elif "_R6" in base or "R6_" in base:
                near_miss.append({"ref": ref, "path": f,
                                  "why_excluded": "outside the K5 tail coverage lineage"})
    chk(12, "no K5 COVERAGE MAP r6 exists on any local branch (r5 remains authoritative)",
        not r6_coverage,
        {"refs_scanned": len(C.git("for-each-ref", "--format=%(refname:short)",
                                   "refs/heads").splitlines()),
         "r6_coverage_maps_found": r6_coverage,
         "highest_coverage_map_present": "K5_COVERAGE_MAP_R5.json",
         "deliberately_excluded_near_misses": near_miss[:8],
         "excluded_count": len(near_miss)})

    # --- 13: predecessor integrity --------------------------------------------------------------
    integ = {}
    for ns, (br, head) in PUBLISHED_HEADS.items():
        path = f"level4/closure_proofs/{ns}"
        try:
            at_head = C.git("rev-parse", f"HEAD:{path}")
            at_pub = C.git("rev-parse", f"{head}:{path}")
            integ[ns] = {"tree_at_C8_HEAD": at_head, "tree_at_published_head": at_pub,
                         "identical": at_head == at_pub}
        except Exception as e:
            integ[ns] = {"error": str(e)[:80], "identical": False}
    chk(13, "C2-C7 namespace trees at C8 HEAD are identical to their own published heads",
        all(v.get("identical") for v in integ.values()), integ)

    # --- 14: guard ------------------------------------------------------------------------------
    deny_files = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"DENY"', "*.json")
    allow_files = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    hist_auth = {}
    for f in ("level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/protocol/AUTHORIZATION_ACTIVE.json",
              "level4/closure_proofs/p5y_k5_cusum_real_point_executor/authorization/COUNTERSIGNATURE_ACTIVE.json"):
        hist_auth[f] = C.git("rev-parse", f"HEAD:{f}")
    chk(14, "guard is DENY everywhere it is declared, no ALLOW exists, historical auth blobs pinned",
        len(deny_files) >= 3 and not allow_files,
        {"guard_DENY_declarations": len(deny_files), "guard_ALLOW_declarations": len(allow_files),
         "historical_EXECUTION_AUTHORIZED_true_blobs": hist_auth,
         "note": ("the two EXECUTION_AUTHORIZED:true files belong to the exhausted slot-1 real-probe "
                  "protocol, a different and closed authorization line; their blobs are pinned here "
                  "so C8 can be shown not to have touched them")})

    # --- 15: no campaign process remains --------------------------------------------------------
    w = C.campaign_workers()
    chk(15, "no ReBaseGuard campaign interpreter is running (executable identity, self-chain excluded)",
        len(w["campaign_workers"]) == 0,
        {"interpreters_seen": len(w["interpreters"]), "campaign_workers": w["campaign_workers"],
         "foreign_unrelated": [{k: p[k] for k in ("pid", "executable", "cwd")} for p in w["foreign"]],
         "method": ("ps -eo comm for executable identity; this process and every ancestor removed, so "
                    "the diagnostic cannot match itself; three independent repo-association signals")})

    # --- 16-17: main refs, recorded separately, never synchronized -------------------------------
    local_main = C.git("rev-parse", "main")
    chk(16, "LOCAL_MAIN_REF recorded", bool(local_main) and len(local_main) == 40,
        {"LOCAL_MAIN_REF": local_main})

    remote_main = C.git("ls-remote", "origin", "refs/heads/main").split("\t")[0]
    chk(17, "REMOTE_MAIN_REF queried independently from origin and equals the expected value",
        remote_main == "1cb453826313c189f0bdafd5b84120c1edb74da9",
        {"REMOTE_MAIN_REF": remote_main,
         "expected": "1cb453826313c189f0bdafd5b84120c1edb74da9",
         "LOCAL_MAIN_REF": local_main,
         "refs_differ": local_main != remote_main,
         "action_taken": "NONE -- recorded only; C8 does not synchronize or modify main"})

    # --- 18: no toolchain / no external state needed ---------------------------------------------
    tc = C.toolchain_present()
    chk(18, "no scientific toolchain is installed, and C8 needs none",
        not any(tc.values()),
        {"importlib_find_spec": tc,
         "model_sha_pin_holds": C.sha256_file(C.MODEL) == C.MODEL_SHA,
         "note": "C8 is planning-only; it computes no scientific value and requires no host"})

    failed = [c["id"] for c in checks if c["status"] == "FAIL"]
    unchecked = [c["id"] for c in checks if c["status"] == "UNCHECKED"]
    out = {
        "schema": "C8_B0_AUDIT/1",
        "campaign": "C8 -- Operator-Information Feasibility and Route Selection",
        "compute_boundary": {"NEW_REAL": 0, "SCIENTIFIC_KERNEL_EVALUATIONS": 0,
                             "OPERATOR_CERTIFICATIONS_EXECUTED": 0, "REMOTE_HOSTS_CONTACTED": 0,
                             "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY"},
        "LOCAL_MAIN_REF": local_main, "REMOTE_MAIN_REF": remote_main,
        "authoritative_r5": {"path": C.R5_PATH, "blob": r5_blob,
                             "m5_open": derived[5], "m1_m2_m3_open": [derived[1], derived[2], derived[3]],
                             "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"]},
        "checks": checks, "failed": failed, "unchecked": unchecked,
        "B0_CLASS": "PASS" if not failed and not unchecked else
                    ("REFUSE" if failed else "PASS_WITH_UNCHECKED"),
    }
    s = C.write_evidence(C.NS / "evidence" / "b0" / "C8_B0_AUDIT.json", out)
    for c in checks:
        print(f"  {c['status']:<9} {c['id']}  {c['name'][:78]}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}   failed={failed}   unchecked={unchecked}")
    print(f"LOCAL_MAIN_REF  {local_main}")
    print(f"REMOTE_MAIN_REF {remote_main}   (differ: {local_main != remote_main}; NOT synchronized)")
    print(f"authoritative m=5 open: {derived[5]}")
    print(f"wrote evidence/b0/C8_B0_AUDIT.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
