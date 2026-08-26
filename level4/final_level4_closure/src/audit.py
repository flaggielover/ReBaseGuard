#!/usr/bin/env python3
"""Validate closure evidence and generate the canonical terminal 18-row ledger."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from config import BASE, PREVIOUS, RESULTS, ROOT, SOURCE, STARTING_HEAD, canonical_json, load
from decision_engine import derive
from integrity import verify as verify_integrity


CAMPAIGNS: dict[str, dict[str, Any]] = {
    "L4R-06": {
        "campaign": "L4R06-POLICY-CLOSED",
        "decision_path": "level4/closure_proofs/l4r06_policy/results/decision.json",
        "reason": "The frozen D4-driven P3 campaign closes the original stability-aware policy requirement while preserving historical Stage C/C6.",
        "extra_evidence": [
            "level4/closure_proofs/l4r06_policy/PROTOCOL.md",
            "level4/closure_proofs/l4r06_policy/results/scientific_findings.json",
            "level4/closure_proofs/l4r06_policy/FAILURE_DIAGNOSES.md",
            "level4/closure_proofs/l4r06_policy/results/decision.json",
        ],
    },
    "L4R-09": {
        "campaign": "MGT1-TRACK1B-CLOSED",
        "decision_path": "level4/closure_proofs/m_gt_1_track1b/results/decision.json",
        "reason": "Track 1B independently closes the scoped m>1 derivative theorem.",
        "extra_evidence": [],
    },
    "L4R-10": {
        "campaign": "SR-DERIVATIVE-CLOSED",
        "decision_path": "level4/closure_proofs/sr_derivative/results/decision.json",
        "reason": "Track 2 closes the SR derivative theorem while leaving the SR Arb certificate open.",
        "extra_evidence": [],
    },
    "L4R-11": {
        "campaign": "D4-PHASE-MAP-CLOSED",
        "decision_path": "level4/closure_proofs/d4_phase_map/results/decision.json",
        "reason": "The independently frozen D4 campaign closes the protocol-specific local phase-map requirement.",
        "extra_evidence": [],
    },
    "L4R-12": {
        "campaign": "L4R12-CLOSED-NEGATIVE-RESULT",
        "decision_path": "level4/closure_proofs/l4r12_operational_crossing/results/decision.json",
        "reason": "The original investigational question is completed by a sufficiently strong frozen negative result; the scientific result remains negative.",
        "extra_evidence": [
            "level4/closure_proofs/l4r12_operational_crossing/REQUIREMENT_SEMANTICS_AUDIT.md",
            "level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json",
            "level4/closure_proofs/l4r12_operational_crossing/results/decision.json",
        ],
    },
    "L4R-14": {
        "campaign": "LOCATION-FAMILY-TRACK3AB-CLOSED",
        "decision_path": "level4/closure_proofs/location_family_track3ab/results/decision.json",
        "reason": "Track 3A/3B closes the regular location-family theorem under explicit assumptions.",
        "extra_evidence": [],
    },
    "L4R-15": {
        "campaign": "EXTERNAL-VALIDATION-V3-CLOSED",
        "decision_path": "level4/closure_proofs/external_validation_v3/results/decision.json",
        "reason": "The frozen cross-campaign rule closes semi-real validation with three supporting tasks against two required.",
        "extra_evidence": [],
    },
    "L4R-16": {
        "campaign": "NOVELTY-VERIFICATION-CLOSED",
        "decision_path": "level4/closure_proofs/novelty_verification/results/decision.json",
        "reason": "The scoped documented search closes the hygiene requirement at N2 with claims narrowed.",
        "extra_evidence": [],
    },
}

OPEN_NONBLOCKERS = [
    {
        "id": "SR-ARB-CERTIFICATE",
        "status": "OPEN",
        "classification": "OPTIONAL_RIGOR_UPGRADE_OUTSIDE_ORIGINAL_18_ROWS",
        "reason": "L4R-10 requires the derivative theorem, not an Arb-certified Gamma_SR inequality.",
        "evidence_paths": [
            "level4/closure_proofs/sr_derivative/results/decision.json",
            "level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md",
        ],
    }
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_authority() -> tuple[dict[str, Any], dict[str, Any]]:
    source = load(SOURCE)
    previous = load(PREVIOUS)
    original = load(ROOT / source["original_source"]["path"])
    require(sha256(SOURCE) == "f802e3f83d1af3ca5517895ccfca18e8e9401571ed53c2561227fb8152d19245",
            "authoritative Final Global requirement source changed")
    require(sha256(PREVIOUS) == "3806c6e0519f4ba6f33848bdc6f1b8b4b84bf1c4b6105a78c20d835c992cdbe5",
            "previous Final Global decision changed")
    require(len(source["requirements"]) == len(original["requirements"]) == 18,
            "original requirement count changed")
    require([row["id"] for row in source["requirements"]] == [f"L4R-{i:02d}" for i in range(1, 19)],
            "requirement IDs/order changed")
    require(sum(row["classification"] == "MANDATORY" for row in source["requirements"]) == 16,
            "mandatory classification count changed")
    original_by = {row["id"]: row for row in original["requirements"]}
    for row in source["requirements"]:
        prior = original_by[row["id"]]
        require(row["requirement"] == prior["requirement"], f"{row['id']}: wording changed")
        require(row["classification"] == prior["classification"], f"{row['id']}: class changed")
        require(row["stage_f"] == prior["stage_f"], f"{row['id']}: Stage-F status changed")
    require(source["taxonomy"]["closed_rule"] == "ALL_MANDATORY_ROWS_PASS",
            "closure rule changed")
    require(source["taxonomy"]["mandatory_satisfying_statuses"] == ["PASS"],
            "mandatory acceptance status changed")
    require(source["taxonomy"]["closed_with_limitations_independently_authorized"] is False,
            "CLOSED-WITH-LIMITATIONS was newly authorized")
    require(previous["current_verdict"] == "LEVEL-4-PARTIAL", "previous Final Global verdict changed")
    require(previous["current_counts"] == {"PASS": 15, "PARTIAL": 3, "FAIL": 0, "OPEN": 0},
            "previous Final Global counts changed")
    require(previous["mandatory_counts"] == {"PASS": 14, "PARTIAL": 2, "FAIL": 0, "OPEN": 0},
            "previous mandatory counts changed")
    return source, previous


def _campaign(campaign: str, target: str, checks: dict[str, bool], paths: list[str],
              limitations: list[str]) -> dict[str, Any]:
    return {
        "campaign": campaign,
        "target_requirement": target,
        "status": "PASS" if checks and all(checks.values()) else "FAIL",
        "checks": checks,
        "evidence_paths": paths,
        "surviving_limitations": limitations,
    }


def audit_evidence() -> dict[str, Any]:
    campaigns: list[dict[str, Any]] = []

    l06 = load(ROOT / CAMPAIGNS["L4R-06"]["decision_path"])
    science = load(ROOT / "level4/closure_proofs/l4r06_policy/results/scientific_findings.json")
    l06_failures = (ROOT / "level4/closure_proofs/l4r06_policy/FAILURE_DIAGNOSES.md").read_text()
    campaigns.append(_campaign("L4R06-POLICY-CLOSED", "L4R-06", {
        "scoped_verdict": l06["scoped_verdict"] == "L4R06-POLICY-CLOSED",
        "same_requirement_mapping": l06["same_requirement_mapping"] is True,
        "original_row_pass": l06["original_L4R06_current_status"] == "PASS",
        "historical_C6_preserved": l06["historical_C6_preserved"] is True
            and l06["historical_stage_c_verdict"] == "STAGE-C-PARTIAL",
        "all_H6_pass": all(value == "PASS" for value in l06["H6"].values()),
        "frozen_policy_formula": science["H6-1"]["status"] == "PASS"
            and all(row["formula_reconstruction_pass"] for row in science["H6-1"]["rows"]),
        "verification_and_reproduction": l06["verification"]["status"] == "PASS"
            and l06["reproduction"]["status"] == "PASS",
        "unfavorable_findings_visible": "Descriptive P2 advantages" in l06_failures
            and science["saturated_m100_identity"] is True
            and len(science["secondary_epsilon_0.05_failures"]) == 2,
    }, CAMPAIGNS["L4R-06"]["extra_evidence"], [
        "Historical Stage C remains PARTIAL and C6 remains failed.",
        "P2 has descriptive advantages at m=70 and m=100; P3=P1 at saturated m=100.",
        "Two secondary epsilon=0.05 conditions fail; the frozen primary epsilon=0.10 family passes.",
    ]))

    t1 = load(ROOT / CAMPAIGNS["L4R-09"]["decision_path"])
    campaigns.append(_campaign("MGT1-TRACK1B-CLOSED", "L4R-09", {
        "decision": t1["decision"] == "MGT1-TRACK1B-CLOSED",
        "original_requirement": t1["m_gt_1_derivative_theorem_requirement"] == "CLOSED",
        "criteria": all(t1["criteria"].values()),
        "failures_preserved": t1["historical_track1a"] == "MGT1-TRACK1A-FAILED"
            and t1["historical_d2_3"] == "FAILED",
    }, [CAMPAIGNS["L4R-09"]["decision_path"]], [
        "Historical D2.3 and Track 1A remain failed; the theorem has explicit scope and assumptions."
    ]))

    sr = load(ROOT / CAMPAIGNS["L4R-10"]["decision_path"])
    campaigns.append(_campaign("SR-DERIVATIVE-CLOSED", "L4R-10", {
        "decision": sr["decision"] == "SR-DERIVATIVE-CLOSED",
        "theorem_closed": sr["status_boundary"]["derivative_theorem"] == "CLOSED",
        "closure_conditions": all(str(value).startswith("PASS") for value in sr["closure_conditions"].values()),
        "Gamma_numerical": sr["status_boundary"]["Gamma_SR_gt_2"] == "CONFIRMATORY NUMERICAL",
        "arb_open": sr["arb"]["status"] == "OPEN"
            and sr["status_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN",
    }, [CAMPAIGNS["L4R-10"]["decision_path"],
        "level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md"], [
        "Gamma_SR > 2 remains confirmatory numerical; SR-GAMMA-CERTIFIED is not awarded."
    ]))

    d4 = load(ROOT / CAMPAIGNS["L4R-11"]["decision_path"])
    campaigns.append(_campaign("D4-PHASE-MAP-CLOSED", "L4R-11", {
        "decision": d4["decision"] == "D4-PHASE-MAP-CLOSED",
        "criteria": all(d4["criteria"].values()),
        "local_claim": "local stability boundary" in d4["claim"],
        "D2_5_preserved": d4["historical_d2_5"] == "MATHEMATICAL, NOT OPERATIONAL",
    }, [CAMPAIGNS["L4R-11"]["decision_path"],
        "level4/closure_proofs/d4_phase_map/OPERATIONAL_BRIDGE.md"], [
        "The D4 boundary is local and deterministic, not an operational phase-transition proof."
    ]))

    l12 = load(ROOT / CAMPAIGNS["L4R-12"]["decision_path"])
    l12_evidence = load(ROOT / "level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json")
    campaigns.append(_campaign("L4R12-CLOSED-NEGATIVE-RESULT", "L4R-12", {
        "scoped_verdict": l12["scoped_verdict"] == "L4R12-CLOSED-NEGATIVE-RESULT",
        "same_requirement_mapping": l12["same_requirement_mapping"] is True,
        "original_row_pass": l12["original_L4R12_current_status"] == "PASS",
        "investigational_semantics": l12["semantics"] == "INVESTIGATIONAL"
            and l12["negative_result_closure_allowed"] is True,
        "valid_negative_answer": l12["negative_result_class"]
            == "C_COMPLETED_RESEARCH_QUESTION_WITH_VALID_NEGATIVE_ANSWER"
            and l12["evidence_sufficient"] is True,
        "historical_D2_5_preserved": l12["historical_D2_5_preserved"] is True
            and l12_evidence["historical_verdict"] == "MATHEMATICAL, NOT OPERATIONAL",
        "no_new_science": l12["new_science_run"] is False,
        "frozen_metrics": l12_evidence["operational_result"]["metrics_peaking_at_crossing"] == 0
            and l12_evidence["operational_result"]["metrics_monotone_in_log_m"] == 4,
        "crossing_values": l12_evidence["crossing"]["stage_d_bracket"] == [50, 75]
            and abs(l12_evidence["crossing"]["stage_d_interpolated"] - 72.18925933962045) < 1e-12
            and l12_evidence["crossing"]["D4_bracket"] == [70, 72]
            and abs(l12_evidence["crossing"]["D4_interpolated"] - 71.41938616943077) < 1e-12,
        "adequate_power": l12_evidence["operational_design"]["n_replicates"] == 20_000
            and l12_evidence["N12"][8]["status"] == "PASS",
        "scoped_negative_claim": "under the frozen monitoring metrics and protocol" in l12["claim_safe"]
            and "in general" in l12["claim_forbidden"],
    }, CAMPAIGNS["L4R-12"]["extra_evidence"], [
        "The scientific result remains negative: no crossing-localized transition under the frozen protocol.",
        "No universal no-effect claim is supported."
    ]))

    t3 = load(ROOT / CAMPAIGNS["L4R-14"]["decision_path"])
    campaigns.append(_campaign("LOCATION-FAMILY-TRACK3AB-CLOSED", "L4R-14", {
        "decision": t3["decision"] == "LOCATION-FAMILY-TRACK3AB-CLOSED",
        "original_requirement": t3["general_location_family_theorem_requirement"] == "CLOSED",
        "criteria": all(t3["criteria"].values()),
        "historical_partial": t3["historical_track_3"]["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
            and t3["historical_track_3"]["numerical_gate"] == "FAILED",
    }, [CAMPAIGNS["L4R-14"]["decision_path"]], [
        "Historical Track 3 remains partial/failed; the theorem is scoped to explicit regularity assumptions."
    ]))

    v3 = load(ROOT / CAMPAIGNS["L4R-15"]["decision_path"])
    v3_results = (ROOT / "level4/closure_proofs/external_validation_v3/RESULTS.md").read_text()
    campaigns.append(_campaign("EXTERNAL-VALIDATION-V3-CLOSED", "L4R-15", {
        "decision": v3["final_campaign_verdict"] == "EXTERNAL-VALIDATION-V3-CLOSED",
        "original_requirement": v3["original_external_validation_requirement"] == "CLOSED",
        "closure_gates": all(v3["closure_gates"].values()),
        "support": v3["cross_campaign_success_count"] == 3 and v3["cross_campaign_required"] == 2,
        "history": v3["historical_stage_e"] == "STAGE-E-PARTIAL"
            and v3["historical_v2"] == "EXTERNAL-VALIDATION-V2-PARTIAL",
        "route_B_unfavorable": "Route B result is unfavorable" in v3_results,
    }, [CAMPAIGNS["L4R-15"]["decision_path"],
        "level4/closure_proofs/external_validation_v3/RESULTS.md",
        "level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md"], [
        "Stage E remains 0/3 and V2 remains 1/3; V3 Route B is unfavorable on both tasks.",
        "P2 external safety is regime-dependent rather than universal."
    ]))

    novelty = load(ROOT / CAMPAIGNS["L4R-16"]["decision_path"])
    campaigns.append(_campaign("NOVELTY-VERIFICATION-CLOSED", "L4R-16", {
        "decision": novelty["decision"] == "NOVELTY-VERIFICATION-CLOSED",
        "original_requirement": novelty["original_global_requirement"] == "CLOSED",
        "criteria": all(novelty["criteria"].values()),
        "N2": novelty["novelty_position"] == "N2"
            and novelty["novelty_position_label"] == "PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED",
        "claim_narrowing": novelty["claim_narrowing_required"] is True,
    }, [CAMPAIGNS["L4R-16"]["decision_path"],
        "level4/closure_proofs/novelty_verification/FINAL_REPORT.md"], [
        "N2 is a scoped partial-overlap finding, not absolute novelty or priority."
    ]))

    stage_c = load(ROOT / "level4/stage_c/results/findings.json")
    stage_d = load(ROOT / "level4/stage_d/results/stage_d_decision.json")
    stage_e = load(ROOT / "level4/stage_e/results/stage_e_decision.json")
    v2 = load(ROOT / "level4/closure_proofs/external_validation_v2/results/decision.json")
    track1a = load(ROOT / "level4/closure_proofs/m_gt_1_track1a/results/decision.json")
    negative_history = {
        "stage_c": stage_c["decision"],
        "stage_c_C6": "FAILED" if "C6" in stage_c["decision_basis"]["failed"] else "MISSING",
        "stage_d": stage_d["decision"],
        "stage_d_D2_3": next(row["status"] for row in stage_d["criteria"] if row["id"] == "D2.3"),
        "stage_d_D2_5": next(row["status"] for row in stage_d["criteria"] if row["id"] == "D2.5"),
        "track_1A": track1a["decision"],
        "historical_track_3": t3["historical_track_3"]["decision"],
        "stage_e": stage_e["decision"],
        "stage_e_support": f"{stage_e['n_tasks_supporting_H_E5']}/3",
        "external_validation_v2": v2["decision"],
        "external_validation_v2_support": f"{sum(v2['task_support'].values())}/3",
        "novelty_position": novelty["novelty_position"],
        "L4R13": "PARTIAL",
    }
    expected_map = {data["campaign"]: rid for rid, data in CAMPAIGNS.items()}
    return {
        "schema": "rebaseguard.final-level4-closure-evidence.v1",
        "mode": "AUDIT_ONLY_NO_NEW_SCIENCE",
        "campaign_requirement_map": expected_map,
        "campaigns": campaigns,
        "all_campaigns_pass": all(row["status"] == "PASS" for row in campaigns),
        "negative_and_unfavorable_history": negative_history,
    }


def build_canonical() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source, previous = validate_authority()
    integrity = verify_integrity()
    require(integrity["status"] == "INTACT", f"protected history broken: {integrity['errors']}")
    evidence = audit_evidence()
    require(evidence["all_campaigns_pass"], "one or more mapped campaigns failed evidence audit")
    prior_by = {row["id"]: row for row in previous["requirements"]}
    campaign_by = {row["target_requirement"]: row for row in evidence["campaigns"]}
    rows = []
    for original in source["requirements"]:
        rid = original["id"]
        prior = prior_by[rid]
        campaign = campaign_by.get(rid)
        current = "PASS" if campaign else prior["current_status"]
        evidence_paths = list(dict.fromkeys(
            list(original["evidence_paths"])
            + ([] if not campaign else campaign["evidence_paths"])
        ))
        transition = CAMPAIGNS.get(rid)
        row = {
            "id": rid,
            "requirement": original["requirement"],
            "class": original["classification"],
            "classification": original["classification"],
            "mandatory": original["classification"] == "MANDATORY",
            "stage_f_status": original["stage_f"],
            "previous_final_audit_status": prior["current_status"],
            "current_status": current,
            "evidence_paths": evidence_paths,
            "transition_campaign": transition["campaign"] if transition else None,
            "transition_reason": transition["reason"] if transition else original["reason"],
            "historical_limitations": original.get("limitations", []),
            "surviving_limitations": campaign["surviving_limitations"] if campaign else original.get("limitations", []),
            "current_blocking": original["classification"] == "MANDATORY" and current != "PASS",
            "changed_since_stage_f": current != original["stage_f"]["status"],
            "changed_since_previous_final_audit": current != prior["current_status"],
        }
        rows.append(row)
    canonical = {
        "schema": "rebaseguard.final-level4-canonical-requirements.v1",
        "generator_owned": True,
        "mode": "AUDIT_DERIVATION_ONLY_NO_NEW_SCIENCE",
        "audit_start_head": STARTING_HEAD,
        "authoritative_source": {
            "path": "level4/final_global_reaudit/requirements.json",
            "sha256": sha256(SOURCE),
        },
        "previous_final_global_decision": {
            "path": "level4/final_global_reaudit/results/final_decision.json",
            "verdict": previous["current_verdict"],
            "counts": previous["current_counts"],
            "mandatory_counts": previous["mandatory_counts"],
        },
        "historical_verdicts": integrity["historical_global_statuses"],
        "taxonomy": source["taxonomy"],
        "open_nonblockers": OPEN_NONBLOCKERS,
        "requirements": rows,
    }
    ledger_closed = derive(rows, integrity_ok=True, engineering_ok=True)
    pending = derive(rows, integrity_ok=True, engineering_ok=False)
    transitions = [row for row in rows if row["changed_since_stage_f"]]
    ledger = {
        "schema": "rebaseguard.final-level4-ledger-derivation.v1",
        "counts": ledger_closed["current_counts"],
        "mandatory_counts": ledger_closed["mandatory_counts"],
        "mandatory_blocker_ids": ledger_closed["mandatory_blocker_ids"],
        "ledger_candidate_verdict": ledger_closed["current_verdict"],
        "pre_final_engineering_verdict": pending["current_verdict"],
        "final_verdict_pending_engineering": True,
        "status_transition_ids": [row["id"] for row in transitions],
        "nonmandatory_partial_ids": [
            row["id"] for row in rows if not row["mandatory"] and row["current_status"] == "PARTIAL"
        ],
        "mechanical_trace": [
            f"canonical rows -> {len(rows)}",
            f"mandatory rows -> {sum(row['mandatory'] for row in rows)}",
            f"mandatory non-PASS rows -> {len(ledger_closed['mandatory_blocker_ids'])}",
            "only PASS satisfies a mandatory row",
            "CLOSED-WITH-LIMITATIONS remains unauthorized",
            f"ledger candidate -> {ledger_closed['current_verdict']}",
            "final verdict remains gated on integrity, A1-A32, reproduction, and both authoritative verifiers",
        ],
    }
    return canonical, evidence, ledger


def outputs() -> dict[Path, str]:
    canonical, evidence, ledger = build_canonical()
    return {
        BASE / "requirements.json": canonical_json(canonical),
        RESULTS / "evidence_audit.json": canonical_json(evidence),
        RESULTS / "ledger_derivation.json": canonical_json(ledger),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    generated = outputs()
    for path, content in generated.items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("terminal audit artifacts stale: " + ", ".join(stale))
        return 1
    ledger = load(RESULTS / "ledger_derivation.json") if args.check else load(RESULTS / "ledger_derivation.json")
    print(
        f"terminal ledger: {ledger['counts']} mandatory={ledger['mandatory_counts']} "
        f"candidate={ledger['ledger_candidate_verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
