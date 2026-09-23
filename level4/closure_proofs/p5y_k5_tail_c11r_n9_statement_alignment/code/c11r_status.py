"""C11R Repair E -- evidence freshness, cross-artifact consistency, and the generated status report.

WHY (errata E4 and E5). The first freeze carried a mutation artifact produced by older code than
the validation artifact beside it: validation said V6 had 0 mismatches, mutations said 9, and the
class was REFUSE. Nothing recorded which code produced either, so it went unnoticed -- and the
author's status report, typed from memory, said something else again.

WHAT THIS MODULE DOES
  1  FRESHNESS. For every artifact under evidence/ and config/, recompute the sha256 of its
     producer, of every module in its recorded code closure, and of every input it read, and
     compare with what the artifact recorded. Any difference is STALE. An artifact whose own
     sha256 no longer matches its body is CORRUPT. One without provenance is UNBOUND.
  2  PROPAGATION. An artifact is FRESH only if every campaign artifact it read is FRESH.
  3  CONTRADICTIONS. Cross-artifact claims are checked against each other -- a validation reporting
     0 scalar-collapse mismatches beside a mutation record citing any other number is REFUSE.
  4  PRE-RESULT STATE. No evidence/runs/, no authorization with guard ALLOW, no comparison.
  5  The status report is GENERATED from the artifacts. Nothing in it is typed by hand.

Planted controls show the checker refusing a stale producer, a stale input, a corrupted body, and
the exact contradiction that slipped through revision 1.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_firewall as FW

SELF_OUT = C.NS / "evidence" / "status" / "C11R_STATUS.json"


def _artifacts() -> list[pathlib.Path]:
    out = sorted((C.NS / "evidence").rglob("*.json")) + sorted((C.NS / "config").glob("*.json"))
    return [p for p in out if p.resolve() != SELF_OUT.resolve()]


def freshness(obj: dict, now_sha) -> dict:
    """now_sha(relpath) -> current sha256 or None if absent. Pure given that function."""
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
    stmt, pol = A.get("statements"), A.get("policy")
    if stmt and pol and pol.get("statements_sha256") != stmt.get("sha256"):
        out.append("the policy was frozen against a different statement table")
    gate = A.get("gate")
    if gate and pol and gate.get("policy_sha256") != pol.get("sha256"):
        out.append("the gate is bound to a different policy")
    if gate and stmt and gate.get("statements_sha256") != stmt.get("sha256"):
        out.append("the gate is bound to a different statement table")
    if stmt and stmt.get("CONTAINS_NO_ORIGINAL_MAGNITUDE") is not True:
        out.append("the statement table does not declare itself magnitude-free")
    if pol and pol.get("references_original_magnitudes") is not False:
        out.append("the policy does not declare itself free of original magnitudes")
    return out


def _controls(A: dict) -> dict:
    """Planted defects the checker must refuse; and one clean case it must accept."""
    res = {}
    if "validation" in A and "mutations" in A:
        planted = copy.deepcopy(A)
        planted["mutations"]["mutants"] = list(planted["mutations"]["mutants"]) + [
            {"id": "PLANTED", "cites_v6_mismatch_count": 9}]
        res["validation_0_vs_mutation_9"] = bool(contradictions(planted))
        res["clean_pair_accepted"] = not contradictions(A)
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
    def now_sha(rel: str):
        p = C.REPO / rel
        return C.sha256_file(p) if p.exists() else None

    arts, rows = {}, {}
    for p in _artifacts():
        obj = json.loads(p.read_text())
        rel = str(p.relative_to(C.REPO))
        arts[rel] = obj
        rows[rel] = freshness(obj, now_sha)
    # propagation: FRESH only if every campaign artifact it read is FRESH
    changed = True
    while changed:
        changed = False
        for rel, r in rows.items():
            if r["state"] != "FRESH":
                continue
            bad = [i for i in r.get("inputs", []) if i in rows and rows[i]["state"] != "FRESH"]
            if bad:
                r["state"] = "STALE"
                r["why"] = [f"reads non-fresh input {b.split('/')[-1]}" for b in bad]
                changed = True

    def pick(suffix):
        for rel, o in arts.items():
            if rel.endswith(suffix):
                return o
        return None
    A = {"validation": pick("validation/C11R_VALIDATION.json"),
         "mutations": pick("mutations/C11R_MUTATIONS.json"),
         "statements": pick("table/C11R_N9_STATEMENTS.json"),
         "policy": pick("config/C11R_POLICY.json"),
         "gate": pick("config/N9R_GATE_C11R.json"),
         "firewall": pick("firewall/C11R_FIREWALL.json"),
         "equivalence": pick("equivalence/C11R_EQUIVALENCE.json"),
         "errata": pick("errata/C11R_ERRATA.json"),
         "b0": pick("b0/C11R_B0.json")}
    A = {k: v for k, v in A.items() if v is not None}
    contra = contradictions(A)
    ctl = _controls(A)

    # the firewall's STRUCTURAL scan re-run here, over the FINAL artifact set (the firewall
    # producer runs before the mutation suite, so this is the scan that sees every artifact)
    struct = [r for r in FW.scan_structural_artifacts() if r["magnitude_keys"]]
    if struct:
        contra.append(f"magnitude-bearing keys in pre-result artifacts: {struct}")

    runs_dir = C.NS / "evidence" / "runs"
    auth = C.NS / "config" / "C11R_AUTHORIZATION.json"
    auth_allow = auth.exists() and json.loads(auth.read_text()).get("guard") == "ALLOW"
    def same_as(commit, path):
        rel = str(path.relative_to(C.REPO))
        return C.sha256_bytes(C.blob_at(commit, rel)) == C.sha256_file(path)
    reviewed_machinery = {
        # G5/G6 assert the drift layer is the one the first pre-freeze review found sound (it
        # reviewed 49b17ab4); checked here, not asserted
        "c11r_idrift_identical_to_first_reviewed_commit_49b17ab4":
            same_as("49b17ab4", C.HERE / "c11r_idrift.py"),
        "c11_certifier_identical_to_C11_HEAD": same_as(C.C11_HEAD,
                                                       C.C11 / "code" / "c11_certifier.py"),
        "c7_gaussian_identical_to_C11_HEAD": same_as(C.C11_HEAD, C.C7 / "code" / "c7_gaussian.py"),
    }
    if not all(reviewed_machinery.values()):
        contra.append(f"reviewed machinery changed: {reviewed_machinery}")

    pre_result = {
        "evidence_runs_absent": not runs_dir.exists(),
        "no_runs_artifact_in_any_commit": not C.git("log", "--all", "--format=%H", "--",
                                                    "*C11R_RUNS.json"),
        "no_authorization_with_guard_ALLOW": not auth_allow,
        "no_comparison_artifact": not (C.NS / "evidence" / "comparison").exists(),
    }
    classes = {
        "B0": A.get("b0", {}).get("B0_CLASS"),
        "TABLE": A.get("statements", {}).get("TABLE_CLASS"),
        "EQUIVALENCE": A.get("equivalence", {}).get("EQUIV_CLASS"),
        "VALIDATION": A.get("validation", {}).get("VALIDATION_CLASS"),
        "FIREWALL": A.get("firewall", {}).get("FIREWALL_CLASS"),
        "MUTATIONS": A.get("mutations", {}).get("MUTATION_CLASS"),
        "GATE_RESULT_LANGUAGE_HITS": A.get("gate", {}).get("result_language_scan", {})
        .get("hits_in_this_gate"),
    }
    required = {"B0": "PASS", "TABLE": "RESOLVED", "EQUIVALENCE": "READY",
                "VALIDATION": "PASS", "FIREWALL": "PASS", "MUTATIONS": "PASS",
                "GATE_RESULT_LANGUAGE_HITS": 0}
    class_fail = {k: v for k, v in classes.items() if v != required[k]}
    not_fresh = {r.split("/")[-1]: x for r, x in rows.items() if x["state"] != "FRESH"}
    ok = (not not_fresh and not contra and not class_fail and all(pre_result.values())
          and all(ctl.values()))

    out = {"schema": "C11R_STATUS/1",
           "generated_from": "the committed artifacts; no line of this report is typed by hand",
           "artifacts": {r.split("closure_proofs/")[-1]: x for r, x in rows.items()},
           "not_fresh": not_fresh,
           "contradictions": contra,
           "classes": classes, "classes_required": required, "class_failures": class_fail,
           "pre_result_state": pre_result,
           "reviewed_machinery_unchanged": reviewed_machinery,
           "controls": ctl,
           "STATUS_CLASS": "CONSISTENT" if ok else "REFUSE"}
    s = C.write_evidence(SELF_OUT, out, producer=__file__)
    print(f"artifacts checked: {len(rows)}")
    for r, x in sorted(rows.items()):
        print(f"  {x['state']:8s} {r.split('/')[-1]:34s} {'; '.join(x['why'])[:90]}")
    print(f"\nclasses: {classes}")
    print(f"class failures: {class_fail}")
    print(f"contradictions: {contra}")
    print(f"pre-result state: {pre_result}")
    print(f"reviewed machinery unchanged: {reviewed_machinery}")
    print(f"controls: {ctl}")
    print(f"\nSTATUS_CLASS = {out['STATUS_CLASS']}")
    print(f"wrote evidence/status/C11R_STATUS.json sha256 {s[:16]}...")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
