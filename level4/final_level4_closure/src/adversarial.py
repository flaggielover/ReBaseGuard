#!/usr/bin/env python3
"""Run the exact A1-A32 terminal closure audit attacks."""
from __future__ import annotations

import argparse
import copy
import re
import subprocess
from typing import Any

from config import BASE, PREVIOUS, PY, RESULTS, ROOT, SOURCE, canonical_json, load
from decision_engine import derive
from integrity import verify as verify_integrity


def add(checks: list[dict[str, Any]], check_id: str, name: str,
        passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "name": name, "passed": bool(passed), "detail": detail})


def focused_tests() -> tuple[bool, str]:
    result = subprocess.run(
        [str(PY), "-m", "pytest", str(BASE / "tests"), "-q"], cwd=ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    match = re.search(r"(\d+) passed", result.stdout)
    count = int(match.group(1)) if match else 0
    return result.returncode == 0 and count > 0, f"focused tests={count} returncode={result.returncode}"


def run() -> dict[str, Any]:
    canonical = load(BASE / "requirements.json")
    source = load(SOURCE)
    previous = load(PREVIOUS)
    evidence = load(RESULTS / "evidence_audit.json")
    ledger = load(RESULTS / "ledger_derivation.json")
    integrity = verify_integrity()
    rows = canonical["requirements"]
    by_id = {row["id"]: row for row in rows}
    campaigns = {row["target_requirement"]: row for row in evidence["campaigns"]}
    history = evidence["negative_and_unfavorable_history"]
    allowed_claims = (BASE / "CLAIM_FIREWALL.md").read_text().split("## Prohibited", 1)[0]
    transition_text = (BASE / "STATUS_TRANSITIONS.md").read_text()
    checks: list[dict[str, Any]] = []

    add(checks, "A1", "historical Stage F remains PARTIAL",
        canonical["historical_verdicts"]["historical_stage_f"] == "LEVEL-4-PARTIAL",
        "protected Stage F is LEVEL-4-PARTIAL")
    add(checks, "A2", "previous Final Global Re-audit remains PARTIAL",
        canonical["historical_verdicts"]["previous_final_global"] == "LEVEL-4-PARTIAL"
        and previous["current_verdict"] == "LEVEL-4-PARTIAL",
        "historical Final Global verdict is LEVEL-4-PARTIAL")
    add(checks, "A3", "L4R-06 historical C6 failure preserved",
        history["stage_c"] == "STAGE-C-PARTIAL" and history["stage_c_C6"] == "FAILED"
        and campaigns["L4R-06"]["checks"]["historical_C6_preserved"],
        "Stage C remains PARTIAL and C6 remains FAILED")
    add(checks, "A4", "L4R-06 later same-requirement mapping verified",
        by_id["L4R-06"]["current_status"] == "PASS"
        and campaigns["L4R-06"]["checks"]["same_requirement_mapping"],
        "L4R06-POLICY-CLOSED maps only to original L4R-06")
    add(checks, "A5", "L4R-12 D2.5 negative result preserved",
        history["stage_d_D2_5"] == "MATHEMATICAL, NOT OPERATIONAL"
        and campaigns["L4R-12"]["checks"]["historical_D2_5_preserved"],
        "negative scientific result remains historical fact")
    add(checks, "A6", "L4R-12 semantics verified investigational",
        campaigns["L4R-12"]["checks"]["investigational_semantics"],
        "frozen semantics permit a sufficiently supported negative answer")
    add(checks, "A7", "no positive-transition rewriting",
        "scientific result remains negative" in transition_text
        and "no corresponding operational transition was found" in
        load(ROOT / "level4/closure_proofs/l4r12_operational_crossing/results/decision.json")["claim_safe"],
        "requirement PASS is separated from the negative scientific outcome")
    add(checks, "A8", "L4R-13 remains PARTIAL",
        by_id["L4R-13"]["current_status"] == "PARTIAL", "L4R-13 is unchanged")
    add(checks, "A9", "L4R-13 confirmed nonmandatory",
        not by_id["L4R-13"]["mandatory"] and not by_id["L4R-13"]["current_blocking"],
        "STRONG_EXTENSION is nonblocking under the original rule")
    add(checks, "A10", "SR Arb remains OPEN",
        canonical["open_nonblockers"][0]["id"] == "SR-ARB-CERTIFICATE"
        and canonical["open_nonblockers"][0]["status"] == "OPEN",
        "optional Arb certificate remains explicit")
    add(checks, "A11", "no SR certificate inflation",
        campaigns["L4R-10"]["checks"]["Gamma_numerical"]
        and campaigns["L4R-10"]["checks"]["arb_open"]
        and "Gamma_SR is not" in allowed_claims,
        "Gamma_SR > 2 is numerical and not Arb-certified")
    add(checks, "A12", "novelty remains N2",
        history["novelty_position"] == "N2" and campaigns["L4R-16"]["checks"]["N2"],
        "N2 partial-overlap/claims-narrowed finding retained")
    add(checks, "A13", "no absolute novelty wording",
        "absolute novelty" not in allowed_claims.lower()
        and not re.search(r"\b(first-ever|unprecedented|previously unknown)\b", allowed_claims, re.I),
        "allowed claims contain no absolute novelty or priority assertion")
    add(checks, "A14", "V2 remains PARTIAL",
        history["external_validation_v2"] == "EXTERNAL-VALIDATION-V2-PARTIAL"
        and history["external_validation_v2_support"] == "1/3",
        "V2 remains PARTIAL with 1/3 support")
    add(checks, "A15", "Stage E remains 0/3",
        history["stage_e"] == "STAGE-E-PARTIAL" and history["stage_e_support"] == "0/3",
        "Stage E remains PARTIAL with 0/3 support")
    add(checks, "A16", "V3 closure preserved without universality claim",
        campaigns["L4R-15"]["status"] == "PASS"
        and "universal external validation" not in allowed_claims.lower(),
        "V3 satisfies its frozen 3-versus-2 scoped rule")
    add(checks, "A17", "no P2 universal-safety claim",
        "universally safe" not in allowed_claims.lower() and "regime-dependent" in allowed_claims,
        "P2 safety remains regime-dependent")
    add(checks, "A18", "D4 remains local/deterministic",
        campaigns["L4R-11"]["checks"]["local_claim"]
        and "deterministic local-stability map" in allowed_claims,
        "D4 is not promoted to an operational theorem")
    add(checks, "A19", "D2.5 remains MATHEMATICAL, NOT OPERATIONAL",
        history["stage_d_D2_5"] == "MATHEMATICAL, NOT OPERATIONAL",
        "historical D2.5 label is exact")
    add(checks, "A20", "original 18-row count unchanged",
        len(rows) == len(source["requirements"]) == 18,
        "canonical and authoritative sources both contain 18 rows")
    add(checks, "A21", "original 16 mandatory rows unchanged",
        sum(row["mandatory"] for row in rows) == 16,
        "exactly 16 authoritative rows are mandatory")
    source_by = {row["id"]: row for row in source["requirements"]}
    add(checks, "A22", "no manually altered classifications",
        all(row["classification"] == source_by[row["id"]]["classification"]
            for row in rows), "all classifications match the protected source")
    transitions = [row for row in rows if row["changed_since_stage_f"]]
    add(checks, "A23", "all status transitions have evidence paths",
        len(transitions) == 8 and all(row["evidence_paths"] and
        all((ROOT / path).exists() for path in row["evidence_paths"]) for row in transitions),
        "all eight Stage-F-to-current transitions have existing evidence")
    derived = derive(rows, integrity_ok=True, engineering_ok=True)
    add(checks, "A24", "counts generated mechanically",
        ledger["counts"] == derived["current_counts"]
        and ledger["mandatory_counts"] == derived["mandatory_counts"],
        f"counts={derived['current_counts']} mandatory={derived['mandatory_counts']}")
    add(checks, "A25", "verdict generated mechanically",
        ledger["ledger_candidate_verdict"] == derived["current_verdict"] == "LEVEL-4-CLOSED",
        f"ledger candidate={derived['current_verdict']}")
    mandatory_partial = copy.deepcopy(rows)
    mandatory_partial[0]["current_status"] = "PARTIAL"
    add(checks, "A26", "synthetic mandatory PARTIAL forces global PARTIAL",
        derive(mandatory_partial, True, True)["current_verdict"] == "LEVEL-4-PARTIAL",
        "counterfactual mandatory non-PASS cannot close")
    nonmandatory_partial = copy.deepcopy(rows)
    by_copy = {row["id"]: row for row in nonmandatory_partial}
    by_copy["L4R-13"]["current_status"] = "PARTIAL"
    add(checks, "A27", "synthetic nonmandatory PARTIAL does not block closure",
        derive(nonmandatory_partial, True, True)["current_verdict"] == "LEVEL-4-CLOSED",
        "original rule quantifies over mandatory rows only")
    add(checks, "A28", "protected historical hashes unchanged",
        integrity["status"] == "INTACT" and not integrity["errors"],
        f"{integrity['trees_verified']} trees and {integrity['files_verified']} files intact")
    reproduction_path = RESULTS / "reproduction.json"
    reproduction = load(reproduction_path) if reproduction_path.exists() else {}
    add(checks, "A29", "generated artifacts byte-stable",
        reproduction.get("status") == "PASS" and reproduction.get("byte_stable") is True,
        "record missing/not final" if not reproduction else f"digest={reproduction.get('digest')}")
    # The detector's own forbidden-token literals are not executable network use.
    offline_files = [
        BASE / "reproduce.sh", BASE / "src/audit.py", BASE / "src/integrity.py",
        BASE / "src/reports.py", BASE / "src/reproduction.py", BASE / "src/finalize.py",
        BASE / "src/verification.py", BASE / "src/decision_engine.py",
    ]
    offline_text = "\n".join(path.read_text().lower() for path in offline_files if path.exists())
    add(checks, "A30", "reproducer offline",
        all(token not in offline_text for token in ("curl ", "wget ", "requests.", "urlopen", "http://", "https://")),
        "terminal audit uses committed local evidence only")
    tests_ok, tests_detail = focused_tests()
    add(checks, "A31", "focused tests green", tests_ok, tests_detail)
    verification_path = RESULTS / "verification.json"
    verification = load(verification_path) if verification_path.exists() else {}
    add(checks, "A32", "authoritative repository verifier green",
        verification.get("status") == "PASS"
        and verification.get("level_1_3_status") == "PASS"
        and verification.get("level_4_status") == "PASS"
        and verification.get("required_checks_skipped") is False,
        "record missing/not final" if not verification else
        f"status={verification.get('status')} checks={verification.get('current_distinct_checks')}")

    passed = sum(row["passed"] for row in checks)
    return {
        "schema": "rebaseguard.final-level4-closure-adversarial.v1",
        "passed": passed,
        "total": 32,
        "status": "PASS" if passed == 32 else "FAIL",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = BASE / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(canonical_json(result))
    print(f"terminal adversarial: {result['passed']}/{result['total']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['name']} — {row['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
