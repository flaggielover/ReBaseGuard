#!/usr/bin/env python3
"""Validate evidence and derive the terminal 18-row Level-4 audit."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from config import BASE, RESULTS, ROOT, SOURCE, load
from integrity import verify as verify_integrity


ALLOWED_STATUSES = {"PASS", "PARTIAL", "FAIL", "OPEN"}
ALLOWED_CLASSES = {"MANDATORY", "OPTIONAL", "STRONG_EXTENSION", "STRETCH", "AMBIGUOUS"}
EXPECTED_MAP = {
    "MGT1-TRACK1B-CLOSED": "L4R-09",
    "SR-DERIVATIVE-CLOSED": "L4R-10",
    "D4-PHASE-MAP-CLOSED": "L4R-11",
    "LOCATION-FAMILY-TRACK3AB-CLOSED": "L4R-14",
    "EXTERNAL-VALIDATION-V3-CLOSED": "L4R-15",
    "NOVELTY-VERIFICATION-CLOSED": "L4R-16",
}
CORE_GENERATED = {
    BASE / "results/evidence_audit.json": None,
    BASE / "results/derived_decision.json": None,
    BASE / "REQUIREMENT_LEDGER.md": None,
    BASE / "EVIDENCE_MAP.md": None,
    BASE / "CLAIM_FIREWALL.md": None,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_source(source: dict[str, Any]) -> None:
    original_meta = source["original_source"]
    previous_meta = source["previous_decision"]
    stage_f_meta = source["historical_stage_f"]
    original_path = ROOT / original_meta["path"]
    previous_path = ROOT / previous_meta["path"]
    stage_f_path = ROOT / stage_f_meta["path"]
    stage_f_generator = ROOT / "level4/stage_f/src/make_final_decision.py"
    require(sha256(original_path) == original_meta["sha256"], "original requirement source changed")
    require(sha256(previous_path) == previous_meta["sha256"], "previous re-audit decision changed")
    require(sha256(stage_f_path) == stage_f_meta["sha256"], "historical Stage-F decision changed")
    require(sha256(stage_f_generator) == stage_f_meta["generator_sha256"], "Stage-F taxonomy generator changed")

    original = load(original_path)
    previous = load(previous_path)
    stage_f = load(stage_f_path)
    rows = source["requirements"]
    require(len(rows) == len(original["requirements"]) == 18, "original requirement count must remain 18")
    require(len({row["id"] for row in rows}) == 18, "requirement IDs must be unique")
    require([row["id"] for row in rows] == [f"L4R-{i:02d}" for i in range(1, 19)],
            "requirement IDs/order changed")
    require(sum(row["classification"] == "MANDATORY" for row in rows) == 16,
            "mandatory classification count changed")
    require(source["campaign_requirement_map"] == EXPECTED_MAP, "campaign mapping changed")
    require(source["taxonomy"]["closed_rule"] == "ALL_MANDATORY_ROWS_PASS",
            "frozen closure rule changed")
    require(source["taxonomy"]["mandatory_satisfying_statuses"] == ["PASS"],
            "mandatory acceptance status changed")
    require(source["taxonomy"]["closed_with_limitations_independently_authorized"] is False,
            "CLOSED-WITH-LIMITATIONS was post-hoc authorized")
    require(stage_f["decision"] == stage_f_meta["verdict"] == "LEVEL-4-PARTIAL",
            "historical Stage-F verdict changed")
    require(previous["current_status"] == previous_meta["verdict"] == "LEVEL-4-PARTIAL",
            "previous post-closure verdict changed")

    original_by = {row["id"]: row for row in original["requirements"]}
    previous_by = {row["id"]: row for row in previous["requirements"]}
    for row in rows:
        prior = original_by[row["id"]]
        require(row["requirement"] == prior["requirement"], f"{row['id']}: description changed")
        require(row["classification"] == prior["classification"], f"{row['id']}: classification changed")
        require(row["classification"] in ALLOWED_CLASSES, f"{row['id']}: unknown classification")
        require(row["stage_f"] == prior["stage_f"], f"{row['id']}: Stage-F status changed")
        require(row["previous_reaudit_status"] == previous_by[row["id"]]["current_status"],
                f"{row['id']}: previous re-audit status changed")
        require(row["previous_reaudit_status"] in ALLOWED_STATUSES,
                f"{row['id']}: invalid previous status")
        for evidence in row["evidence_paths"]:
            require((ROOT / evidence).exists(), f"{row['id']}: missing evidence {evidence}")
        closure = row.get("later_closure")
        if closure:
            require(EXPECTED_MAP.get(closure["campaign"]) == row["id"],
                    f"{row['id']}: later campaign closes wrong requirement")
            require(closure["status"] == "PASS", f"{row['id']}: closure status must be PASS")
            require((ROOT / closure["decision_path"]).exists(),
                    f"{row['id']}: missing decision path")


def campaign_result(name: str, target: str, checks: dict[str, bool], paths: list[str],
                    limitations: list[str]) -> dict[str, Any]:
    return {
        "campaign": name,
        "target_requirement": target,
        "status": "PASS" if checks and all(checks.values()) else "FAIL",
        "checks": checks,
        "evidence_paths": paths,
        "surviving_limitations": limitations,
    }


def audit_evidence() -> dict[str, Any]:
    campaigns: list[dict[str, Any]] = []

    t1 = load(ROOT / "level4/closure_proofs/m_gt_1_track1b/results/decision.json")
    t1_hash = load(ROOT / "level4/closure_proofs/m_gt_1_track1b/results/protocol_hash.json")
    campaigns.append(campaign_result("MGT1-TRACK1B-CLOSED", "L4R-09", {
        "decision_closes_campaign": t1["decision"] == "MGT1-TRACK1B-CLOSED",
        "decision_closes_original_requirement": t1["m_gt_1_derivative_theorem_requirement"] == "CLOSED",
        "protocol_frozen_before_outcomes": t1_hash["frozen_before_confirmatory_numerics"] is True,
        "protocol_hash_matches": t1["protocol_sha256"] == t1_hash["sha256"],
        "all_closure_criteria_pass": all(t1["criteria"].values()),
        "historical_failures_preserved": t1["historical_track1a"] == "MGT1-TRACK1A-FAILED" and t1["historical_d2_3"] == "FAILED",
    }, ["level4/closure_proofs/m_gt_1_track1b/PROTOCOL.md",
        "level4/closure_proofs/m_gt_1_track1b/results/decision.json"],
       ["Historical D2.3 and Track 1A remain failed; the Lean spine is conditional."]))

    sr = load(ROOT / "level4/closure_proofs/sr_derivative/results/decision.json")
    sr_hash = load(ROOT / "level4/closure_proofs/sr_derivative/results/protocol_hash.json")
    campaigns.append(campaign_result("SR-DERIVATIVE-CLOSED", "L4R-10", {
        "decision_closes_campaign": sr["decision"] == "SR-DERIVATIVE-CLOSED",
        "derivative_theorem_closed": sr["status_boundary"]["derivative_theorem"] == "CLOSED",
        "protocol_frozen_before_outcomes": sr_hash["frozen_before_confirmatory_numerics"] is True,
        "protocol_hash_matches": sr["protocol"]["sha256"] == sr_hash["sha256"],
        "closure_conditions_pass": all(str(value).startswith("PASS") for value in sr["closure_conditions"].values()),
        "numerical_not_upgraded": sr["status_boundary"]["Gamma_SR_gt_2"] == "CONFIRMATORY NUMERICAL",
        "arb_open_preserved": sr["arb"]["status"] == "OPEN" and sr["status_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN",
    }, ["level4/closure_proofs/sr_derivative/PROTOCOL.md",
        "level4/closure_proofs/sr_derivative/results/decision.json",
        "level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md"],
       ["Level 4 closure would not imply SR-GAMMA-CERTIFIED; the Arb certificate is OPEN."]))

    t3 = load(ROOT / "level4/closure_proofs/location_family_track3ab/results/decision.json")
    t3_hash = load(ROOT / "level4/closure_proofs/location_family_track3ab/results/protocol_hash.json")
    campaigns.append(campaign_result("LOCATION-FAMILY-TRACK3AB-CLOSED", "L4R-14", {
        "decision_closes_campaign": t3["decision"] == "LOCATION-FAMILY-TRACK3AB-CLOSED",
        "decision_closes_original_requirement": t3["general_location_family_theorem_requirement"] == "CLOSED",
        "protocol_frozen_before_outcomes": t3_hash["frozen_before_confirmatory_outcomes"] is True,
        "protocol_hash_matches": t3["protocol_sha256"] == t3_hash["sha256"],
        "all_closure_criteria_pass": all(t3["criteria"].values()),
        "historical_track3_preserved": t3["historical_track_3"]["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL" and t3["historical_track_3"]["unchanged"] is True,
        "lean_no_sorry_or_admit": t3["lean"]["sorry_or_admit"] is False,
    }, ["level4/closure_proofs/location_family_track3ab/PROTOCOL.md",
        "level4/closure_proofs/location_family_track3ab/results/decision.json"],
       ["Historical Track 3 remains partial; the Lean theorem spine is conditional on explicit analytic hypotheses."]))

    d4 = load(ROOT / "level4/closure_proofs/d4_phase_map/results/decision.json")
    d4_hash = load(ROOT / "level4/closure_proofs/d4_phase_map/results/protocol_hash.json")
    d4_verify = load(ROOT / "level4/closure_proofs/d4_phase_map/results/verification.json")
    campaigns.append(campaign_result("D4-PHASE-MAP-CLOSED", "L4R-11", {
        "decision_closes_campaign": d4["decision"] == "D4-PHASE-MAP-CLOSED",
        "protocol_frozen_before_outcomes": d4_hash["new_campaign_outcomes_inspected_before_freeze"] is False,
        "protocol_hash_matches": d4_verify["protocol_sha256"] == d4_hash["protocol_sha256"],
        "all_closure_criteria_pass": all(d4["criteria"].values()),
        "adversarial_pass": d4["adversarial"] == {"passed": 14, "total": 14},
        "verification_pass": d4_verify["status"] == "PASS",
        "formula_matches": d4["derivative_formula"] == "F'_{rho,m}(0) = rho(1-GammaTilde_m)",
        "historical_operational_boundary_preserved": "local stability boundary" in d4["claim"].lower(),
    }, ["level4/closure_proofs/d4_phase_map/PROTOCOL.md",
        "level4/closure_proofs/d4_phase_map/results/decision.json",
        "level4/closure_proofs/d4_phase_map/results/verification.json"],
       ["The phase map is mathematical/local and does not prove an abrupt stochastic operational transition."]))

    novelty = load(ROOT / "level4/closure_proofs/novelty_verification/results/decision.json")
    novelty_hash = load(ROOT / "level4/closure_proofs/novelty_verification/results/protocol_hash.json")
    novelty_verify = load(ROOT / "level4/closure_proofs/novelty_verification/results/verification.json")
    novelty_adv = load(ROOT / "level4/closure_proofs/novelty_verification/results/adversarial_final.json")
    campaigns.append(campaign_result("NOVELTY-VERIFICATION-CLOSED", "L4R-16", {
        "decision_closes_campaign": novelty["decision"] == "NOVELTY-VERIFICATION-CLOSED",
        "decision_closes_original_requirement": novelty["original_global_requirement"] == "CLOSED",
        "protocol_frozen": novelty_hash["status"] == "FROZEN",
        "all_closure_criteria_pass": all(novelty["criteria"].values()),
        "verification_pass": novelty_verify["status"] == "PASS",
        "adversarial_pass": novelty_adv["status"] == "PASS" and novelty_adv["passed"] == 18,
        "n2_claim_narrowing_preserved": novelty["novelty_position"] == "N2" and novelty["claim_narrowing_required"] is True,
    }, ["level4/closure_proofs/novelty_verification/PROTOCOL.md",
        "level4/closure_proofs/novelty_verification/results/decision.json",
        "level4/closure_proofs/novelty_verification/FINAL_REPORT.md"],
       ["The result is a scoped N2 search conclusion, not absolute novelty or priority."]))

    v3 = load(ROOT / "level4/closure_proofs/external_validation_v3/results/decision.json")
    v3_hash = load(ROOT / "level4/closure_proofs/external_validation_v3/results/protocol_hash.json")
    v3_verify = load(ROOT / "level4/closure_proofs/external_validation_v3/results/verification.json")
    v3_repro = load(ROOT / "level4/closure_proofs/external_validation_v3/results/reproduction.json")
    stage_e = load(ROOT / "level4/stage_e/results/stage_e_decision.json")
    v2 = load(ROOT / "level4/closure_proofs/external_validation_v2/results/decision.json")
    analyses = [load(ROOT / f"level4/closure_proofs/external_validation_v3/results/task_{task}_analysis.json")
                for task in ("metropt", "retail")]
    campaigns.append(campaign_result("EXTERNAL-VALIDATION-V3-CLOSED", "L4R-15", {
        "decision_closes_campaign": v3["final_campaign_verdict"] == "EXTERNAL-VALIDATION-V3-CLOSED",
        "decision_closes_original_requirement": v3["original_external_validation_requirement"] == "CLOSED",
        "protocol_frozen_before_outcomes": v3_hash["confirmatory_outcomes_existed_when_frozen"] is False,
        "all_closure_gates_pass": all(v3["closure_gates"].values()),
        "v3_two_of_two": v3["v3_joint_support"] == "2/2",
        "cross_campaign_threshold_pass": v3["cross_campaign_success_count"] == 3 and v3["cross_campaign_required"] == 2,
        "verification_pass": v3_verify["status"] == "PASS",
        "reproduction_pass": v3_repro["status"] == "PASS" and v3_repro["byte_stable"] is True,
        "historical_stage_e_preserved": stage_e["decision"] == "STAGE-E-PARTIAL" and stage_e["n_tasks_supporting_H_E5"] == 0,
        "historical_v2_preserved": v2["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL" and sum(v2["task_support"].values()) == 1,
        "unfavorable_route_b_preserved": all(row["H3_2"]["route_B_medium_response"] is False for row in analyses),
    }, ["level4/closure_proofs/external_validation_v3/PROTOCOL.md",
        "level4/closure_proofs/external_validation_v3/results/decision.json",
        "level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md"],
       ["Stage E remains 0/3, V2 remains 1/3, V3 Route B is unfavorable, and P2 remains regime-dependent."]))

    by_name = {row["campaign"]: row for row in campaigns}
    return {
        "schema": "rebaseguard.level4-final-global-evidence-audit.v1",
        "campaigns": campaigns,
        "all_campaigns_pass": all(row["status"] == "PASS" for row in campaigns),
        "campaign_requirement_map": {name: row["target_requirement"] for name, row in by_name.items()},
    }


def derive(source: dict[str, Any], evidence: dict[str, Any], integrity: dict[str, Any],
           overrides: dict[str, str] | None = None) -> dict[str, Any]:
    overrides = overrides or {}
    evidence_by = {row["campaign"]: row for row in evidence["campaigns"]}
    resolved = []
    for source_row in source["requirements"]:
        row = copy.deepcopy(source_row)
        closure = row.get("later_closure")
        if closure:
            campaign = evidence_by[closure["campaign"]]
            require(campaign["status"] == "PASS", f"{row['id']}: closure campaign failed audit")
            current = closure["status"]
        else:
            current = row["previous_reaudit_status"]
        current = overrides.get(row["id"], current)
        require(current in ALLOWED_STATUSES, f"{row['id']}: invalid current status")
        row.update({
            "current_status": current,
            "changed_since_stage_f": current != row["stage_f"]["status"],
            "changed_since_previous_reaudit": current != row["previous_reaudit_status"],
            "change_campaign": closure["campaign"] if closure and current != row["previous_reaudit_status"] else None,
            "blocks_closure": row["classification"] == "MANDATORY" and current != "PASS",
        })
        resolved.append(row)

    counts = Counter(row["current_status"] for row in resolved)
    mandatory = [row for row in resolved if row["classification"] == "MANDATORY"]
    mandatory_counts = Counter(row["current_status"] for row in mandatory)
    blockers = [row for row in mandatory if row["current_status"] != "PASS"]
    fail_open = [row for row in blockers if row["current_status"] in {"FAIL", "OPEN"}]
    integrity_ok = integrity["status"] == "INTACT"
    if not integrity_ok:
        verdict = "LEVEL-4-FAILED"
    elif blockers:
        verdict = "LEVEL-4-PARTIAL"
    else:
        verdict = "LEVEL-4-CLOSED"
    require(verdict in source["taxonomy"]["allowed_labels"], "derived verdict outside taxonomy")

    def compact(row: dict[str, Any]) -> dict[str, Any]:
        return {key: row.get(key) for key in
                ("id", "requirement", "classification", "current_status", "blocker_type",
                 "reason", "evidence_paths", "limitations")}

    partial_assessment = {
        "L4R-06": {
            "scientific_category": "A_MANDATORY_BLOCKER_REQUIRING_PASS",
            "taxonomy_effect": "BLOCKS_LEVEL_4_CLOSED",
            "reason": "Stage C is PARTIAL, C6 remains failed, and no same-requirement closure exists."
        },
        "L4R-12": {
            "scientific_category": "B_VALID_NEGATIVE_RESULT",
            "taxonomy_effect": "BLOCKS_LEVEL_4_CLOSED_AS_MANDATORY_NONPASS",
            "reason": "The negative answer is scientifically valid, but the frozen fallback normalized NEGATIVE as a mandatory non-PASS row."
        },
        "L4R-13": {
            "scientific_category": "C_NONMANDATORY_PARTIAL_PERMITTED",
            "taxonomy_effect": "DOES_NOT_BLOCK_LEVEL_4_CLOSED",
            "reason": "The row is a STRONG_EXTENSION rather than MANDATORY."
        },
    }
    claims = {
        "strongest_rigorous_result": "The Lean-checked stopped-likelihood differentiation spine, outward-rounded Gamma_CUSUM enclosure above two, and certified deterministic-skeleton period-2 orbit.",
        "strongest_general_theorem": "For regular one-dimensional location families under explicit stopped change-of-measure, tail, integrability, and domination hypotheses, F'_rho(0)=rho(1-Gamma_f).",
        "strongest_cross_detector_result": "CUSUM and the authoritative symmetric two-chart SR detector both support the stopped-score derivative identity; Gamma_SR > 2 remains confirmatory numerical evidence.",
        "most_important_negative_result": "The Gamma_m crossing is mathematical, not operational: zero of four monitoring metrics peaked at m* and all four were monotone in log m.",
        "publication_safe_summary": "ReBaseGuard has a rigorous CUSUM core and independently verified scoped derivative, phase-map, regular-location-family, novelty-hygiene, and semi-real-validation closure campaigns. The current global Level-4 status remains partial because two original mandatory rows retain non-PASS partial/negative outcomes.",
        "resume_safe_summary": "Built and verified a reproducible sequential-monitoring research stack spanning Lean-checked theorem spines, Arb-certified CUSUM bounds, deterministic stability analysis, scoped cross-detector and location-family results, and outcome-blind semi-real validation; a terminal audit preserved historical failures and identified two remaining mandatory limitations.",
    }
    return {
        "schema": "rebaseguard.level4-final-global-derived-decision.v1",
        "audit_metadata": {"audit_date": source["audit_date"], "audited_commit": source["audit_start_head"],
                           "mode": "AUDIT_DERIVATION_ONLY_NO_NEW_SCIENCE"},
        "historical_stage_f_verdict": "LEVEL-4-PARTIAL",
        "previous_post_closure_verdict": source["previous_decision"]["verdict"],
        "current_verdict": verdict,
        "taxonomy": source["taxonomy"],
        "original_requirement_count": len(resolved),
        "mandatory_requirement_count": len(mandatory),
        "current_counts": {status: counts[status] for status in ("PASS", "PARTIAL", "FAIL", "OPEN")},
        "mandatory_counts": {status: mandatory_counts[status] for status in ("PASS", "PARTIAL", "FAIL", "OPEN")},
        "mandatory_blockers": [compact(row) for row in blockers],
        "mandatory_fail_open": [compact(row) for row in fail_open],
        "remaining_open_nonblockers": source["open_nonblockers"],
        "rows_changed_since_previous_reaudit": [compact(row) | {"campaign": row["change_campaign"]}
                                                  for row in resolved if row["changed_since_previous_reaudit"]],
        "rows_changed_since_stage_f": [compact(row) for row in resolved if row["changed_since_stage_f"]],
        "remaining_partial_negative_assessment": partial_assessment,
        "later_closure_campaigns_used": list(source["campaign_requirement_map"]),
        "evidence_audit_status": "PASS" if evidence["all_campaigns_pass"] else "FAIL",
        "protected_history": integrity,
        "requirements": resolved,
        "sr_boundary": {
            "derivative_theorem": "CLOSED",
            "Gamma_SR_gt_2": "CONFIRMATORY NUMERICAL",
            "rigorous_SR_local_instability_certificate": "OPEN",
            "global_effect": "NONBLOCKING_OPTIONAL_RIGOR_UPGRADE_OUTSIDE_ORIGINAL_L4R_10"
        },
        "historical_statuses_preserved": {
            "stage_f": "LEVEL-4-PARTIAL", "previous_post_closure": "LEVEL-4-PARTIAL",
            "stage_c": "STAGE-C-PARTIAL", "stage_d": "STAGE-D-PARTIAL",
            "stage_d_D2_3": "FAILED", "stage_d_D2_5": "MATHEMATICAL, NOT OPERATIONAL",
            "stage_e": "STAGE-E-PARTIAL", "stage_e_H_E5": "0/3",
            "track_1a": "MGT1-TRACK1A-FAILED", "historical_track_3": "LOCATION-FAMILY-THEOREM-PARTIAL",
            "external_validation_v2": "EXTERNAL-VALIDATION-V2-PARTIAL", "external_validation_v2_support": "1/3"
        },
        "claims": claims,
        "decision_rule_trace": [
            "historical Stage-F and previous post-closure verdicts remain immutable LEVEL-4-PARTIAL",
            f"protected history -> {integrity['status']}",
            f"later evidence campaigns -> {'PASS' if evidence['all_campaigns_pass'] else 'FAIL'}",
            f"mandatory non-PASS rows -> {len(blockers)}",
            "CLOSED requires every mandatory row PASS; PARTIAL/NEGATIVE does not satisfy that frozen rule",
            "CLOSED-WITH-LIMITATIONS is not independently authorized",
            f"fallback taxonomy -> {verdict}",
        ],
    }


def requirement_ledger(decision: dict[str, Any]) -> str:
    lines = [
        "# Authoritative final requirement ledger",
        "",
        "Generated from `requirements.json`; counts and verdict are not manually duplicated.",
        "",
        f"Current tally: **{decision['current_counts']['PASS']} PASS · "
        f"{decision['current_counts']['PARTIAL']} PARTIAL/NEGATIVE · "
        f"{decision['current_counts']['FAIL']} FAIL · {decision['current_counts']['OPEN']} OPEN**.",
        "",
        "| ID | Requirement | Class | Stage F | Previous | Later closure | Current | Changed now | Blocks closure | Evidence | Surviving limitation |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in decision["requirements"]:
        closure = row.get("later_closure")
        campaign = closure["campaign"] if closure else "—"
        evidence = "<br>".join(f"`{path}`" for path in row["evidence_paths"])
        limitation = "<br>".join(row["limitations"]) if row["limitations"] else "—"
        lines.append(
            f"| {row['id']} | {row['requirement']} | {row['classification']} | "
            f"{row['stage_f']['label']} | {row['previous_reaudit_status']} | {campaign} | "
            f"**{row['current_status']}** | {'YES' if row['changed_since_previous_reaudit'] else 'NO'} | "
            f"{'YES' if row['blocks_closure'] else 'NO'} | {evidence} | {limitation} |"
        )
    return "\n".join(lines) + "\n"


def evidence_map(evidence: dict[str, Any]) -> str:
    lines = [
        "# Later closure evidence map", "",
        "Only explicitly targeted, frozen, verified same-requirement campaigns may change a row.", "",
        "| Campaign | Original row | Audit | Evidence chain | Surviving limitations |",
        "|---|---|---|---|---|",
    ]
    for row in evidence["campaigns"]:
        paths = "<br>".join(f"`{path}`" for path in row["evidence_paths"])
        limits = "<br>".join(row["surviving_limitations"])
        lines.append(f"| {row['campaign']} | {row['target_requirement']} | **{row['status']}** | {paths} | {limits} |")
    return "\n".join(lines) + "\n"


def claim_firewall(decision: dict[str, Any]) -> str:
    claims = decision["claims"]
    return f"""# Final scientific claim firewall

## Theorem-safe claims

- The scoped m>1 derivative theorem is closed by Track 1B while historical
  D2.3 and Track 1A remain failed.
- The symmetric two-chart SR derivative identity is closed under its explicit
  analytic hypotheses.
- The regular one-dimensional location-family stopped-score theorem is closed
  under its documented assumptions; its Lean spine is conditional.

## Certificate-safe claims

- Gamma_CUSUM has the stored outward-rounded Arb enclosure with lower endpoint
  above two.
- Stage B certifies a period-2 orbit of the deterministic conditional-mean
  skeleton, not the stochastic long-run process.
- Level 4 closure does not imply SR-GAMMA-CERTIFIED. The rigorous SR
  local-instability certificate remains OPEN.

## Numerical-evidence-safe claims

- Gamma_SR > 2 is confirmatory numerical evidence only.
- D4 maps a frozen protocol-specific deterministic local-stability boundary;
  it is not an abrupt operational phase-transition proof.
- The historical Gamma_m operational-crossing experiment is a negative result:
  0/4 metrics peaked and 4/4 were monotone in log m.

## External-validation-safe claims

- The frozen later-evidence rule closes L4R-15 with V2 Household and two V3
  tasks, three successes against a requirement of two.
- Stage E remains 0/3, V2 remains 1/3, V3 Route B remains unfavorable on both
  tasks, and P2 is regime-dependent rather than universally safe.

## Novelty-safe claims

Within the documented search scope, no work was identified that combines the
same alarm-stopped next-reference mechanism with the reported derivative and
stability results. The position is N2: partial overlap found and claims
narrowed. This is not absolute novelty or priority.

## Publication-safe summary

{claims['publication_safe_summary']}

## Resume-safe summary

{claims['resume_safe_summary']}

## Prohibited claims

- PROHIBITED: “ReBaseGuard is novel.”
- PROHIBITED: “first-ever”, “unprecedented”, “first analysis”, or “previously unknown”.
- PROHIBITED: production validation, deployment readiness, universal P2 safety,
  detector independence, distribution-free validity, or operational phase
  transition from the D4 boundary.
- PROHIBITED: all research questions are solved, or historical failed/partial
  campaigns were retrospectively successful.

## Remaining limitations and open problems

- L4R-06 remains mandatory PARTIAL because Stage C C6 failed.
- L4R-12 remains a mandatory scientifically valid NEGATIVE/PARTIAL result and
  therefore a non-PASS row under the frozen fallback rule.
- L4R-13 remains a nonmandatory partial non-Gaussian extension.
- The SR rigorous local-instability Arb certificate remains OPEN outside the
  original derivative-theorem closure requirement.
"""


def build() -> dict[Path, str]:
    source = load(SOURCE)
    validate_source(source)
    integrity = verify_integrity()
    require(integrity["status"] == "INTACT", "protected history is not intact")
    evidence = audit_evidence()
    require(evidence["all_campaigns_pass"], "one or more closure campaigns failed audit")
    decision = derive(source, evidence, integrity)
    return {
        BASE / "results/evidence_audit.json": json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        BASE / "results/derived_decision.json": json.dumps(decision, indent=2, sort_keys=True) + "\n",
        BASE / "REQUIREMENT_LEDGER.md": requirement_ledger(decision),
        BASE / "EVIDENCE_MAP.md": evidence_map(evidence),
        BASE / "CLAIM_FIREWALL.md": claim_firewall(decision),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build()
    stale = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("stale final-audit artifacts: " + ", ".join(stale))
        return 1
    decision = json.loads(outputs[BASE / "results/derived_decision.json"])
    print(f"final audit core: {decision['current_verdict']} "
          f"{decision['current_counts']}" + (" byte-stable" if args.check else " generated"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
