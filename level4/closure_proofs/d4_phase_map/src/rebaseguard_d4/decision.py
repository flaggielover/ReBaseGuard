"""Derive the scoped D4 decision mechanically from structured artifacts."""

from __future__ import annotations

from .adversarial import verify_history
from .common import read_json, write_json
from .config import CAMPAIGN, PROTOCOL_SHA256, REPO, RESULTS


def build() -> dict:
    gamma = read_json(RESULTS / "gamma_grid.json")
    direct = read_json(RESULTS / "direct_validation.json")
    phase = read_json(RESULTS / "phase_map.json")
    operational = read_json(RESULTS / "operational_overlay.json")
    adversarial = read_json(RESULTS / "adversarial.json")
    verification = read_json(RESULTS / "verification.json")
    figure_index = read_json(CAMPAIGN / "figures/figure_index.json")
    track1b = read_json(REPO / "level4/closure_proofs/m_gt_1_track1b/results/decision.json")
    d25 = read_json(REPO / "level4/stage_d/results/d2_5_verdict.json")
    history_ok, history_detail = verify_history()
    criteria = {
        "D4.1": track1b["decision"] == "MGT1-TRACK1B-CLOSED",
        "D4.2": gamma["valid"] and len(gamma["rows"]) == 17,
        "D4.3": phase["valid"] and phase["checks"]["formula_recomputed"],
        "D4.4": direct["valid"] and len(direct["rows"]) == 6,
        "D4.5": phase["valid"] and figure_index["valid"],
        "D4.6": adversarial["checks"][5]["passed"],
        "D4.7": operational["valid"] and adversarial["checks"][9]["passed"],
        "D4.8": d25["verdict"] == "MATHEMATICAL, NOT OPERATIONAL",
        "D4.9": adversarial["valid"] and adversarial["passed"] == 14,
        "D4.10": verification["status"] == "PASS",
    }
    if all(criteria.values()) and history_ok:
        verdict = "D4-PHASE-MAP-CLOSED"
        requirement = "CLOSED"
    elif history_ok and gamma["valid"] and phase["valid"]:
        verdict = "D4-PHASE-MAP-PARTIAL"
        requirement = "PARTIAL"
    else:
        verdict = "D4-PHASE-MAP-FAILED"
        requirement = "UNMET"
    output = {
        "schema": "rebaseguard.d4-decision.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "decision": verdict,
        "original_global_d4_requirement": requirement,
        "criteria": criteria,
        "derivative_formula": phase["derivative_formula"],
        "gamma_definition": phase["gamma_definition"],
        "gamma_equals_2_crossings": phase["crossings_gamma_equals_2"],
        "gamma_rows": phase["gamma_rows"],
        "rho_c_rows": phase["boundary_rows"],
        "direct_validation": direct["rows"],
        "operational_overlay": operational,
        "historical_d2_3": "FAILED",
        "historical_d2_5": d25["verdict"],
        "historical_stage_f": "LEVEL-4-PARTIAL",
        "current_post_closure_global_verdict": "LEVEL-4-PARTIAL",
        "global_level4_reaudit_performed": False,
        "historical_integrity": history_detail,
        "historical_integrity_passed": history_ok,
        "remaining_global_blockers_after_scoped_d4_closure": [
            {"name": "Semi-real external validation", "type": "SCIENTIFIC"},
            {"name": "Prior-art and novelty verification", "type": "DOCUMENTATION_PROVENANCE"},
        ] if requirement == "CLOSED" else [
            {"name": "m-rho phase map (D4)", "type": "SCIENTIFIC"}
        ],
        "verification": verification,
        "adversarial": {"passed": adversarial["passed"], "total": adversarial["total"]},
        "claim": (
            "The closed m>1 derivative theorem induces a protocol-specific local "
            "stability boundary rho_c(m), mapped across the frozen CUSUM reuse protocol."
        ),
    }
    write_json(RESULTS / "decision.json", output)
    return output
