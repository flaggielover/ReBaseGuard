"""C11R -- evidence freshness, cross-artifact consistency, and the generated status report. Rev. 2.

WHY (errata E4 and E5). The first freeze carried a mutation artifact produced by older code than
the validation artifact beside it: validation said V6 had 0 mismatches, mutations said 9, and the
class was REFUSE. Nothing recorded which code produced either, so it went unnoticed -- and the
author's status report, typed from memory, said something else again.

REVISION 2 (review round 2, B-2; erratum E14). Revision 1 json-loaded every file under evidence/
and config/ by directory glob -- the quarantine included -- and compared historical blobs by
reading them. It now reads ONLY the explicit allowlist (common.PRE_RESULT_ARTIFACTS). A protected
file is checked by CONTENT-FREE identity: `git hash-object` of the file against the id recorded
for it, and `git rev-parse <commit>:<path>` for a historical version. No byte of the quarantine, a
review report or a predecessor's artifact enters this process.

WHAT THIS MODULE DOES
  1  FRESHNESS. For every allowlisted artifact, recompute the sha256 of its producer, of every
     module in its recorded code closure, and of every input it read (a protected input by its
     content-free id), and compare with what the artifact recorded. Any difference is STALE; a
     body that no longer hashes to its sha256 is CORRUPT; one without provenance is UNBOUND.
  2  PROPAGATION. An artifact is FRESH only if every campaign artifact it read is FRESH.
  3  CONTRADICTIONS. Cross-artifact claims are checked against each other.
  4  INVENTORY. Every file under evidence/ and config/ (names only, `git ls-files`) must be an
     allowlisted artifact or the quarantine; the retired artifacts must be absent.
  5  PRE-RESULT STATE. No evidence/runs/, no authorization, no comparison, in the tree or in any
     commit.
  6  The report and the handover counts are GENERATED from the artifacts.
"""
from __future__ import annotations

import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_contract as CT
import c11r_qualify as Q

SELF_REL = "evidence/status/C11R_STATUS.json"
VERIFY_ONLY = sys.argv[1:] == ["--verify-only"]
PRESERVED_REVIEWS = {"review/REVIEW_C11R_PREFREEZE.md": "6d7cd546",
                     "review/REVIEW_C11R_PREFREEZE_R2.md": "6ae05833",
                     "review/REVIEW_C11R_PREFREEZE_R3.md": "f6c737c3",
                     "review/REVIEW_C11R_PREFREEZE_R4.md": "5c5203c1",
                     "review/REVIEW_C11R_PREFREEZE_R5.md": "ebf08c0f"}
REVIEWED_MACHINERY = {f"{C.NS_REL}/code/c11r_idrift.py": "49b17ab4",
                      "level4/closure_proofs/p5y_k5_tail_c11_n9_independent_certifier/code/"
                      "c11_certifier.py": C.C11_HEAD,
                      "level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py":
                          C.C11_HEAD}


def freshness(obj: dict, now_sha) -> dict:
    """now_sha(relpath) -> current id or None if absent. Pure given that function."""
    body = {k: v for k, v in obj.items() if k != "sha256"}
    if C.sha256_obj(body) != obj.get("sha256"):
        return {"state": "CORRUPT", "why": ["the body no longer hashes to its recorded sha256"]}
    prov = obj.get("provenance")
    if not prov:
        return {"state": "UNBOUND", "why": ["no provenance: the producing code is unknowable"]}
    why = []
    cur = now_sha(prov["producer"])
    if cur is None:
        why.append(f"producer {prov['producer']} no longer exists")
    elif cur != prov["producer_sha256"]:
        why.append(f"producer {prov['producer'].split('/')[-1]} changed since this was written")
    for rel, sha in prov.get("code_closure", {}).items():
        c = now_sha(rel)
        if c != sha:
            why.append(f"closure module {rel.split('/')[-1]} "
                       f"{'is missing' if c is None else 'changed'}")
    for rel, sha in prov.get("inputs", {}).items():
        c = now_sha(rel)
        if c != sha:
            why.append(f"input {rel.split('/')[-1]} {'is missing' if c is None else 'changed'}")
    return {"state": "STALE" if why else "FRESH", "why": why,
            "inputs": sorted(prov.get("inputs", {}))}


def contradictions(A: dict) -> list[str]:
    """Cross-artifact claims checked against each other. A maps short name -> artifact."""
    out = []
    val, mut = A.get("validation"), A.get("mutations")
    if val and mut:
        v6 = next((c for c in val["checks"] if c["id"] == "V6"), None)
        n_val = v6["detail"]["mismatch_count"] if v6 else None
        for m in mut.get("mutants", []):
            cited = m.get("cites_v6_mismatch_count")
            if cited is not None and cited != n_val:
                out.append(f"mutation {m['id']} cites {cited} scalar-collapse mismatches; "
                           f"validation reports {n_val}")
        if v6 and v6["pass"] is False and mut.get("MUTATION_CLASS") == "PASS":
            out.append("mutations PASS while validation V6 FAILS")
    stmt, pol, gate = A.get("statements"), A.get("policy"), A.get("gate")
    if stmt and pol and pol.get("statements_sha256") != stmt.get("sha256"):
        out.append("the policy was frozen against a different statement table")
    if gate and pol and gate.get("policy_sha256") != pol.get("sha256"):
        out.append("the gate is bound to a different policy")
    if gate and stmt and gate.get("statements_sha256") != stmt.get("sha256"):
        out.append("the gate is bound to a different statement table")
    if stmt and stmt.get("CONTAINS_NO_ORIGINAL_MAGNITUDE") is not True:
        out.append("the statement table does not declare itself magnitude-free")
    if pol and pol.get("references_original_magnitudes") is not False:
        out.append("the policy does not declare itself free of original magnitudes")
    cost = A.get("cost")
    if pol and cost and pol["configuration"]["cost_model"]["source_artifact_sha256"] != \
            cost.get("sha256"):
        out.append("the policy was frozen against a different cost artifact")
    err = A.get("errata")
    if err and err.get("CONTAINS_NO_ORIGINAL_MAGNITUDE") is not True:
        out.append("the errata do not declare themselves free of original magnitudes")
    return out


def _controls(A: dict) -> dict:
    """Planted defects the checker must refuse; and clean cases it must accept."""
    res = {}
    if "validation" in A and "mutations" in A:
        planted = copy.deepcopy(A)
        planted["mutations"]["mutants"] = list(planted["mutations"]["mutants"]) + [
            {"id": "PLANTED", "cites_v6_mismatch_count": 9}]
        res["validation_0_vs_mutation_9"] = bool(contradictions(planted))
        res["clean_pair_accepted"] = not contradictions(A)
    if "policy" in A and "cost" in A:
        planted = copy.deepcopy(A)
        planted["cost"]["sha256"] = "0" * 64
        res["policy_against_other_cost_artifact"] = bool(contradictions(planted))
    base = {"x": 1}
    base["sha256"] = C.sha256_obj(base)
    corrupt = dict(base, x=2)
    res["corrupt_body_detected"] = freshness(corrupt, lambda r: None)["state"] == "CORRUPT"
    stale = {"x": 1, "provenance": {"producer": "p.py", "producer_sha256": "a",
                                    "code_closure": {}, "inputs": {"i.json": "b"}}}
    stale["sha256"] = C.sha256_obj({k: v for k, v in stale.items() if k != "sha256"})
    res["stale_producer_detected"] = freshness(stale, lambda r: {"p.py": "CHANGED",
                                                                 "i.json": "b"}.get(r))["state"] \
        == "STALE"
    res["stale_input_detected"] = freshness(stale, lambda r: {"p.py": "a",
                                                              "i.json": "CHANGED"}.get(r))[
        "state"] == "STALE"
    res["fresh_accepted"] = freshness(stale, lambda r: {"p.py": "a", "i.json": "b"}.get(r))[
        "state"] == "FRESH"
    res["unbound_detected"] = freshness(base, lambda r: None)["state"] == "UNBOUND"
    return res


def main() -> int:
    # current identities, from STATIC lists only: allowlisted artifacts by sha256 of their bytes
    current = {f"{C.NS_REL}/{rel}": C.sha256_file(C.NS / rel)
               for rel in C.ALLOWED_NS_INPUTS if (C.NS / rel).exists()}

    def now_sha(rel: str):
        if rel.endswith(".py"):
            return C.sha256_code(rel) if (C.REPO / rel).exists() else None
        if C.is_protected(rel):
            return C.content_free_id(C.REPO / rel)             # an id; no content is read
        return current.get(rel, "UNVERIFIABLE: not an allowlisted input")

    # the analysis that proves this module's reads is flow-insensitive, so every load-path
    # variable here has a single purpose and a name used for nothing else
    arts, rows = {}, {}
    for art in C.PRE_RESULT_ARTIFACTS:
        if art == SELF_REL:
            continue
        if not (C.NS / art).exists():
            rows[f"{C.NS_REL}/{art}"] = {"state": "MISSING", "why": ["not written"]}
            continue
        obj = C.load_allowlisted(art)
        arts[art] = obj
        rows[f"{C.NS_REL}/{art}"] = freshness(obj, now_sha)
    changed = True
    while changed:
        changed = False
        for key, row in rows.items():
            if row["state"] != "FRESH":
                continue
            bad = [i for i in row.get("inputs", []) if i in rows and rows[i]["state"] != "FRESH"]
            if bad:
                row["state"] = "STALE"
                row["why"] = [f"reads non-fresh input {b.split('/')[-1]}" for b in bad]
                changed = True

    A = {"b0": arts.get("evidence/b0/C11R_B0.json"),
         "errata": arts.get("evidence/errata/C11R_ERRATA.json"),
         "statements": arts.get("evidence/table/C11R_N9_STATEMENTS.json"),
         "equivalence": arts.get("evidence/equivalence/C11R_EQUIVALENCE.json"),
         "validation": arts.get("evidence/validation/C11R_VALIDATION.json"),
         "cost": arts.get("evidence/cost/C11R_COST.json"),
         "policy": arts.get("config/C11R_POLICY.json"),
         "policy_evidence": arts.get("evidence/policy/C11R_POLICY_EVIDENCE.json"),
         "gate": arts.get("config/N9R_GATE_C11R.json"),
         "firewall": arts.get("evidence/firewall/C11R_FIREWALL.json"),
         "mutations": arts.get("evidence/mutations/C11R_MUTATIONS.json"),
         "leakcheck": arts.get("evidence/leakcheck/C11R_LEAKCHECK.json"),
         "contract": arts.get("config/C11R_CONTRACT.json"),
         "chain": arts.get("evidence/chain/C11R_CHAIN_CONTROLS.json"),
         "procs": arts.get("evidence/procs/C11R_PROCESS_DETECTOR.json")}
    A = {k: v for k, v in A.items() if v is not None}
    contra = contradictions(A)
    ctl = _controls(A)
    from c11r_schema import forbidden_payload
    payload = {art: forbidden_payload(obj) for art, obj in arts.items() if forbidden_payload(obj)}
    if payload:
        contra.append(f"forbidden payload keys in pre-result artifacts: {payload}")

    # the quarantine: by content-free id only, against the id the statement table recorded
    q_now = C.content_free_id(C.NS / C.QUARANTINE_REL)
    q_rec = A.get("statements", {}).get("quarantine", {}).get("content_free_id")
    quarantine_ok = q_now is not None and q_now == q_rec
    if not quarantine_ok:
        contra.append("the quarantine is not the file the statement table recorded")

    # the leak check covered the CURRENT bytes of every file it scanned
    leak = A.get("leakcheck", {})
    leak_stale = []
    for r in leak.get("files", []):
        f = r["file"]
        if "git_object" in r:
            ok = C.git_object_at("HEAD", f) == "gitobj:" + r["git_object"]
        elif f.endswith(".py"):
            ok = C.sha256_code(f) == r["sha256"]
        else:
            ok = current.get(f) == r["sha256"]
        if not ok:
            leak_stale.append(f.split("/")[-1])
    if leak_stale:
        contra.append(f"the leak check scanned other bytes than the current: {leak_stale}")

    # the execution contract and the gate, RECOMPUTED from bytes (round 4, R3-1)
    gate = A.get("gate", {})
    roots = CT.chain_roots(C.REPO)
    contract_problems = list(roots["problems"])
    cfg = (roots.get("contract") or {}).get("configuration", {})
    ch = A.get("policy", {}).get("configuration", {}).get("chosen", {})
    if (cfg.get("depth"), cfg.get("panels")) != (ch.get("depth"), ch.get("panels")):
        contract_problems.append("the policy's selected configuration is not the contract's")
    if contract_problems:
        contra.append(f"the execution contract or gate does not verify: {contract_problems}")
    fwa = A.get("firewall", {})
    if fwa.get("CLAIM") != "DEFENSE_IN_DEPTH_HEURISTIC":
        contra.append("the firewall artifact does not scope its claim as a heuristic")

    # inventory: names only
    listed = C.git("ls-files", "--cached", "--others", "--exclude-standard", "--",
                   f"{C.NS_REL}/evidence", f"{C.NS_REL}/config").splitlines()
    expected = {f"{C.NS_REL}/{r}" for r in C.PRE_RESULT_ARTIFACTS} | {
        f"{C.NS_REL}/{C.QUARANTINE_REL}"}
    unexpected = sorted(x for x in listed if x and x not in expected)
    retired_present = sorted(x for x in listed if x.split("/")[-1] in C.RETIRED_FILES
                             or x.split("/")[-1] == "C11R_N9_TABLE.json")
    if unexpected:
        contra.append(f"unexpected artifacts in evidence/ or config/: {unexpected}")

    # historical and reviewed files, by object id only
    reviewed_machinery = {rel.split("/")[-1]: C.content_free_id(C.REPO / rel)
                          == C.git_object_at(commit, rel)
                          for rel, commit in REVIEWED_MACHINERY.items()}
    if not all(reviewed_machinery.values()):
        contra.append(f"reviewed machinery changed: {reviewed_machinery}")
    reviews = {rel: C.content_free_id(C.NS / rel) == C.git_object_at(commit, f"{C.NS_REL}/{rel}")
               for rel, commit in PRESERVED_REVIEWS.items()}
    if not all(reviews.values()):
        contra.append(f"a preserved review was edited: {reviews}")

    qs = Q.self_test()
    # complete history, not `git log --all -- <glob>` (review 4, R4-1: that simplifies merges)
    anywhere = CT.protocol_artifacts_anywhere(C.REPO)
    pre_result = {
        "evidence_runs_absent": not (C.NS / "evidence" / "runs").exists(),
        "no_runs_artifact_in_any_commit": not anywhere["holders"]["runs"],
        "no_authorization_artifact": not (C.NS / "config" / "C11R_AUTHORIZATION.json").exists(),
        "no_authorization_in_any_commit": not anywhere["holders"]["authorization"],
        "no_execution_permission_artifact": not (C.NS / "config" /
                                                 "C11R_EXECUTION_PERMISSION.json").exists(),
        "no_execution_permission_in_any_commit": not anywhere["holders"]["permission"],
        "no_protocol_directory_in_any_commit": not any(
            v for k, v in anywhere["holders"].items() if k.startswith("dir:")),
        "history_integrity": not anywhere["history_integrity"]["problems"],
        "no_comparison_artifact": not (C.NS / "evidence" / "comparison").exists(),
        "no_comparison_in_any_commit": not anywhere["holders"]["comparison"],
        "no_qualification_artifact": not (C.NS / "evidence" / "qualification").exists(),
        "no_qualification_in_any_commit": not anywhere["holders"]["qualification"],
        "gate_guard_DENY": gate.get("guard") == "DENY",
    }
    classes = {
        "B0": A.get("b0", {}).get("B0_CLASS"),
        "TABLE": A.get("statements", {}).get("TABLE_CLASS"),
        "EQUIVALENCE": A.get("equivalence", {}).get("EQUIV_CLASS"),
        "VALIDATION": A.get("validation", {}).get("VALIDATION_CLASS"),
        "FIREWALL": A.get("firewall", {}).get("FIREWALL_CLASS"),
        "MUTATIONS": A.get("mutations", {}).get("MUTATION_CLASS"),
        "LEAK": leak.get("LEAK_CLASS"),
        "CHAIN_CONTROLS": A.get("chain", {}).get("CHAIN_CLASS"),
        "PROCESS_DETECTOR": A.get("procs", {}).get("DETECTOR_CLASS"),
        "CONTRACT_AND_GATE_VERIFY": not contract_problems,
        "GATE_RESULT_LANGUAGE_HITS": gate.get("result_language_scan", {}).get("hits_in_this_gate"),
        "QUALIFIER_SELF_TEST": qs["ALL_PASS"],
    }
    required = {"B0": "PASS", "TABLE": "RESOLVED", "EQUIVALENCE": "READY",
                "VALIDATION": "PASS", "FIREWALL": "PASS", "MUTATIONS": "PASS", "LEAK": "PASS",
                "CHAIN_CONTROLS": "PASS", "PROCESS_DETECTOR": "PASS",
                "CONTRACT_AND_GATE_VERIFY": True,
                "GATE_RESULT_LANGUAGE_HITS": 0, "QUALIFIER_SELF_TEST": True}
    class_fail = {k: v for k, v in classes.items() if v != required[k]}
    not_fresh = {r.split("/")[-1]: x for r, x in rows.items() if x["state"] != "FRESH"}

    # handover counts, generated from the artifacts
    mut = A.get("mutations", {})
    fw = A.get("firewall", {})
    counts = {
        "errata_entries": A.get("errata", {}).get("count"),
        "b0_checks": len(A.get("b0", {}).get("checks", [])),
        "validation_checks": len(A.get("validation", {}).get("checks", [])),
        "mutants": len(mut.get("mutants", [])),
        "mutants_detected": sum(1 for m in mut.get("mutants", []) if m["outcome"] == "DETECTED"),
        "adversarial_certificate_controls": len(mut.get("adversarial_controls", [])),
        "adversarial_controls_caught": sum(1 for m in mut.get("adversarial_controls", [])
                                           if m.get("caught")),
        "firewall_positive_controls": len(fw.get("controls", {}).get("positive", {})),
        "firewall_negative_controls": len(fw.get("controls", {}).get("negative", {})),
        "firewall_modules_scanned": fw.get("modules_scanned"),
        "leak_files_scanned": leak.get("files_scanned"),
        "gate_predicates": len(gate.get("predicates", {})),
        "artifacts_checked": len(rows),
        "chain_controls": len(A.get("chain", {}).get("controls", [])),
        "chain_controls_passed": sum(1 for r in A.get("chain", {}).get("controls", [])
                                     if r.get("pass")),
        "chain_control_groups": A.get("chain", {}).get("groups"),
        "chain_loader_ordering_holds": A.get("chain", {}).get("quarantine_access_ordering", {})
        .get("loader_never_called_on_a_refused_chain"),
        "qualification_schema_items": len(CT.QUAL_ITEMS),
        "detector_planted_controls": len(A.get("procs", {}).get("planted_controls", {})
                                         .get("cases", {})),
        "firewall_known_miss_probes": {k: fw.get("controls", {}).get("known_miss_probes", {})
                                       .get(k) for k in ("flagged", "missed")},
        "mutation_detector_kinds": mut.get("detector_kinds"),
        "contract_code_files": len((roots.get("contract") or {}).get("code", {})),
    }
    ok = (not not_fresh and not contra and not class_fail and all(pre_result.values())
          and all(ctl.values()) and not retired_present)

    out = {"schema": "C11R_STATUS/2",
           "generated_from": "the allowlisted artifacts; no line of this report is typed by hand",
           "reads": "common.PRE_RESULT_ARTIFACTS only; protected files by content-free id",
           "artifacts": {r.split("closure_proofs/")[-1]: x for r, x in rows.items()},
           "not_fresh": not_fresh,
           "contradictions": contra,
           "classes": classes, "classes_required": required, "class_failures": class_fail,
           "quarantine_matches_recorded_id": quarantine_ok,
           "leak_check_covers_current_bytes": not leak_stale,
           "execution_contract_verification": {"problems": contract_problems,
                                               "digest": roots.get("contract_digest"),
                                               "gate_digest": roots.get("gate_digest")},
           "inventory": {"files_listed": len(listed), "unexpected": unexpected,
                         "retired_present": retired_present},
           "reviewed_machinery_unchanged": reviewed_machinery,
           "preserved_reviews_unedited": reviews,
           "qualifier_self_test": qs,
           "pre_result_state": pre_result,
           "pre_result_history_commits_checked": anywhere["commits_checked"],
           "controls": ctl,
           "handover_counts": counts,
           "structural_scan_of_every_artifact": {"forbidden_payload_keys": payload,
                                                 "artifacts_scanned": len(arts)},
           "not_scanned_by_the_leak_check": ("this status artifact: it carries classes, booleans, "
                                             "file names, hashes and counts only, and its keys "
                                             "pass the structural scan below"),
           "STATUS_CLASS": "CONSISTENT" if ok else "REFUSE"}
    if forbidden_payload(out):
        out["STATUS_CLASS"] = "REFUSE"
        out["contradictions"].append("the status report itself carries a forbidden payload key")
    if VERIFY_ONLY:
        # read-only verification against a commit: recompute everything, write nothing, and check
        # the committed status report itself is fresh
        self_state = freshness(C.load_allowlisted(SELF_REL), now_sha)["state"] \
            if (C.NS / SELF_REL).exists() else "MISSING"
        verdict = out["STATUS_CLASS"] if self_state == "FRESH" else "REFUSE"
        print(f"VERIFY-ONLY: artifacts {len(rows)}, not fresh {sorted(not_fresh)}, "
              f"contradictions {contra}, class failures {class_fail}, "
              f"committed status report {self_state}")
        print(f"VERIFY-ONLY STATUS_CLASS = {verdict}")
        return 0 if verdict == "CONSISTENT" else 1
    s = C.write_evidence(C.NS / SELF_REL, out, producer=__file__)
    print(f"artifacts checked: {len(rows)}")
    for r, x in sorted(rows.items()):
        print(f"  {x['state']:8s} {r.split('/')[-1]:34s} {'; '.join(x['why'])[:90]}")
    print(f"\nclasses: {classes}")
    print(f"class failures: {class_fail}")
    print(f"contradictions: {contra}")
    print(f"quarantine id matches: {quarantine_ok}; leak check current: {not leak_stale}")
    print(f"inventory unexpected: {unexpected}; retired present: {retired_present}")
    print(f"reviewed machinery unchanged: {reviewed_machinery}")
    print(f"preserved reviews unedited: {reviews}")
    print(f"qualifier self-test: {qs['ALL_PASS']}")
    print(f"pre-result state: {pre_result}")
    print(f"controls: {ctl}")
    print(f"handover counts: {counts}")
    print(f"\nSTATUS_CLASS = {out['STATUS_CLASS']}")
    print(f"wrote evidence/status/C11R_STATUS.json sha256 {s[:16]}...")
    return 0 if out["STATUS_CLASS"] == "CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
