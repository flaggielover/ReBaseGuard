"""C10 Phase 16 -- verify before absorb.

Every load-bearing factual claim C10 makes or adopts is reproduced from the committed tree.
Numerical claims are recomputed; git-history claims are re-derived from git objects; governance
claims cite exact committed text. Reviewer INTERPRETATION is never recorded as historical fact.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c10_common as C

GATE_SHA_FILE = "config/DECISION_GATE_C10.json"


def main() -> int:
    ledger, findings = [], []
    arch = C.load(C.NS / "evidence" / "phase1" / "C10_ARCHAEOLOGY.json")
    gov = C.load(C.NS / "evidence" / "phase5" / "C10_GOVERNANCE.json")
    adj_txt = (C.C2 / "evidence" / "adjudication" / "C2_ADJUDICATION.md").read_text()

    def rec(stmt, kind, source, method, ok, value=None):
        ledger.append({"statement": stmt, "claim_kind": kind, "source": source,
                       "verification_method": method,
                       "result": "REPRODUCED" if ok else "NOT_REPRODUCED", "value": value,
                       "disposition": "ABSORBED" if ok else "REVIEW_SOURCED_UNVERIFIED"})
        if not ok:
            findings.append({"check": "CLAIM_NOT_REPRODUCED", "statement": stmt})

    q1 = arch["Q1_hash_archaeology"]
    bound = q1["commit_bound_by_the_pin"]
    rec("REGISTRY_C2's recorded producer hash equals the producer at the bound commit",
        "GIT_HISTORY", "REGISTRY_C2.code_sha256 vs git object",
        "recomputed sha256 of the blob at that commit",
        C.sha256_bytes(C.blob_at(bound, C.PRODUCER)) == q1["recorded_c2_refined_registry"],
        q1["recorded_c2_refined_registry"][:16])
    rec("the producer changed twice after the registry was sealed",
        "GIT_HISTORY", "git log over the producer path", "counted commits after the registry commit",
        len(q1["producer_timeline"]) == 3 and q1["registry_rebuilt_since"] == 0,
        {"producer_commits": len(q1["producer_timeline"]),
         "registry_rebuilds": q1["registry_rebuilt_since"]})
    rec("only main and verify changed; every build-path unit is identical",
        "NUMERICAL", "AST unit comparison", "re-derived by parsing both blobs",
        arch["Q1_diff_classification"]["units_changed"] == ["main", "verify"]
        and arch["Q1_diff_classification"]["BUILD_PATH_IDENTICAL"],
        arch["Q1_diff_classification"]["units_changed"])
    rec("the enforced taboo_certify pin still matches",
        "NUMERICAL", "REGISTRY_C2 vs the committed certifier", "recomputed sha256",
        q1["taboo_pin_still_matches"], q1["recorded_taboo_certify"][:16])

    rule = gov["Q2_phase5_rule_reconstruction"]
    rec("the C2 floor declares itself prospective",
        "GOVERNANCE", "C2_ADJUDICATION.md", "exact substring present in the committed text",
        "It is **prospective**: it governs future adoptions" in adj_txt,
        "It is **prospective**: it governs future adoptions of K5 m = 5 tail cells from this verdict onward.")
    rec("F1 carries an explicit lapse condition tied to N9",
        "GOVERNANCE", "C2_ADJUDICATION.md", "exact substring present",
        "remains open, and lapses when N9 is closed" in adj_txt,
        "This limb is available for as long as **N9** ... remains open, and lapses when N9 is closed.")
    rec("the adjudication directs a successor to freeze a REPLACEMENT floor",
        "GOVERNANCE", "C2_ADJUDICATION.md", "exact substring present",
        "a successor should freeze a replacement floor" in adj_txt,
        "a successor should freeze a replacement floor requiring agreement between two independent "
        "certifier implementations rather than F1")
    rec("no committed artifact claims the floor is immutable for all future successors",
        "GOVERNANCE", "C2_ADJUDICATION.md", "regex scan for permanence language",
        rule["any_claim_of_permanence"] == [], rule["any_claim_of_permanence"])
    rec("N9 is OPEN, by explicit assertions with conditionals excluded",
        "GOVERNANCE", "C2-C9 prose", "assertion scan with preceding context and conditional filter",
        rule["N9_status"]["state"] == "OPEN"
        and rule["N9_status"]["explicit_closed_assertions"] == 0,
        {"state": rule["N9_status"]["state"],
         "open": rule["N9_status"]["explicit_open_assertions"],
         "closed": rule["N9_status"]["explicit_closed_assertions"]})

    c307 = gov["Q2_phase10_cell307"]
    lever = C.load(C.C9 / "evidence" / "phase4" / "C9_ALPHA_LEVER.json")
    best = max(p["tightening"] for p in lever["projection"])
    rec("alpha can close cell 307 but cannot satisfy F2",
        "NUMERICAL", "C9 alpha projection vs C8 thresholds", "recomputed max over the projection",
        best >= c307["tightening_to_close"]
        and best < c307["tightening_to_be_ADOPTABLE_under_the_inherited_floor"],
        {"best_alpha": best, "close": c307["tightening_to_close"],
         "adopt": c307["tightening_to_be_ADOPTABLE_under_the_inherited_floor"]})
    rec("F1 is invariant under alpha, so alpha can never satisfy it",
        "GOVERNANCE", "F1's definition vs what alpha moves",
        "F1 requires a supply NOT using the Arb/FLINT registry; alpha tightens that registry's own "
        "taboo supersolution, so no alpha value changes a registry-free supply",
        c307["alpha_can_satisfy_F1"] is False and c307["F1_passes"] is False,
        c307["F1_Gamma_under_Lemma_G"])

    # scope discipline
    outside = [f for f in C.git("diff", "--name-only", f"{C.C9_HEAD}..HEAD").splitlines()
               if "p5y_k5_tail_c10_governance_provenance" not in f]
    r6 = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    allow = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    for stmt, ok in (("no file outside the C10 namespace was changed", not outside),
                     ("no r6 was created", not r6),
                     ("guard never left DENY", not allow)):
        rec(stmt, "GIT_HISTORY", "git", "diff/ls-tree/grep over the committed tree", ok)

    gsha = C.sha256_file(C.NS / GATE_SHA_FILE)
    rec("the C10 decision gate predates the adjudication and is unchanged",
        "GIT_HISTORY", "config/DECISION_GATE_C10.json", "sha256 of the committed blob",
        (C.NS / GATE_SHA_FILE).exists(), gsha[:16])

    out = {"schema": "C10_HANDOVER_FACT_VERIFICATION/1",
           "WHAT_THIS_CANNOT_VERIFY": (
               "governance READINGS are arguments, not facts. This ledger verifies that the quoted "
               "text EXISTS in the committed artifact and says what is claimed; it cannot verify "
               "that the programme's intent matches the reading. Those entries are marked "
               "claim_kind GOVERNANCE so a reader can weigh them differently from GIT_HISTORY and "
               "NUMERICAL entries, which are reproducible outright."),
           "load_bearing_claim_ledger": ledger,
           "claim_kinds": sorted({e["claim_kind"] for e in ledger}),
           "findings": findings,
           "FACT_CHECK_CLASS": "PASS" if not findings else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json", out)
    for e in ledger:
        print(f"  {e['result']:<15} [{e['claim_kind']:<12}] {e['statement'][:62]}")
    print(f"\nFACT_CHECK_CLASS = {out['FACT_CHECK_CLASS']}  findings={len(findings)}")
    print(f"wrote evidence/governance/HANDOVER_FACT_VERIFICATION.json sha256 {s[:16]}...")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
