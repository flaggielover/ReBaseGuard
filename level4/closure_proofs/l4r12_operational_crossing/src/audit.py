#!/usr/bin/env python3
"""Deterministically replay the L4R-12 semantics and historical evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

from config import (
    BASE,
    NEGATIVE_VERDICT,
    ORIGINAL_CLASS,
    ORIGINAL_WORDING,
    PRECOMMIT_SHA256,
    PRIMARY_METRICS,
    PROTOCOL_SHA256,
    RESULTS,
    ROOT,
    canonical_json,
)
from integrity import sha256, verify as verify_integrity


def _json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text())


def _matching_line(relative: str, needle: str) -> str:
    for line in (ROOT / relative).read_text().splitlines():
        if needle in line:
            return line
    raise ValueError(f"{needle!r} not found in {relative}")


def _claim_scan(audited_commit: str) -> dict[str, Any]:
    pattern = (
        r"(has|shows|establishes|demonstrates|is) (an? )?(observable )?"
        r"operational (counterpart|transition|phase transition)"
    )
    proc = subprocess.run(
        ["git", "grep", "-I", "-n", "-E", pattern, audited_commit, "--", "*.md", "*.json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr)
    candidates = proc.stdout.splitlines()
    conclusions = []
    for line in candidates:
        lower = line.lower()
        negative_context = any(token in lower for token in (
            "failed / negative", "mathematical, not operational",
            "no observed operational transition", "forbidden", "refutes",
        ))
        if not negative_context:
            conclusions.append(line)
    return {
        "audited_commit": audited_commit,
        "pattern": pattern,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "contradictory_positive_conclusions": conclusions,
    }


def build_sources() -> dict[str, Any]:
    requirements = _json("level4/final_global_reaudit/requirements.json")
    rows = requirements["requirements"] if isinstance(requirements, dict) else requirements
    matches = [row for row in rows if row.get("id") == "L4R-12"]
    if len(matches) != 1:
        raise ValueError(f"expected one L4R-12 row, found {len(matches)}")
    row = matches[0]
    protocol_line = _matching_line("level4/stage_d/STAGE_D_PROTOCOL.md", "| D2.5 |")
    reconstruction_line = _matching_line(
        "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md",
        "Operational consequence of the `Gamma_m` crossing",
    )
    precommit = (ROOT / "level4/stage_d/notes/D2_5_PRECOMMIT.md").read_text()
    return {
        "schema": "rebaseguard.l4r12-source-extraction.v1",
        "authoritative_scope": "repository-only",
        "source_precedence": [
            "pre-outcome Stage-D protocol",
            "pre-outcome D2.5 precommit",
            "original reconstructed 18-row requirement wording and class",
            "blueprint/ranking/kill-gate context",
            "later Stage-F and global-audit status normalization",
        ],
        "requirement": {
            "id": row["id"],
            "wording": row["requirement"],
            "classification": row["classification"],
            "stage_f": row["stage_f"],
            "previous_reaudit_status": row["previous_reaudit_status"],
            "later_closure": row["later_closure"],
            "reason": row["reason"],
            "limitations": row["limitations"],
        },
        "frozen_acceptance_condition": {
            "source": "level4/stage_d/STAGE_D_PROTOCOL.md",
            "sha256": sha256(ROOT / "level4/stage_d/STAGE_D_PROTOCOL.md"),
            "exact_row": protocol_line,
        },
        "frozen_precommit": {
            "source": "level4/stage_d/notes/D2_5_PRECOMMIT.md",
            "sha256": sha256(ROOT / "level4/stage_d/notes/D2_5_PRECOMMIT.md"),
            "written_before_data": "BEFORE any D2.5 data was generated" in precommit,
            "negative_rule_present": (
                "smooth monotone variation with no feature near `m*`" in precommit
                and "mathematical, not operational" in precommit
            ),
            "no_posthoc_metric_selection": "no metric will be selected after the fact" in precommit,
        },
        "later_reconstruction": {
            "source": "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md",
            "sha256": sha256(ROOT / "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md"),
            "exact_row": reconstruction_line,
        },
    }


def build_semantics(sources: dict[str, Any]) -> dict[str, Any]:
    protocol_row = sources["frozen_acceptance_condition"]["exact_row"]
    precommit = sources["frozen_precommit"]
    exact_source = (
        sources["requirement"]["wording"] == ORIGINAL_WORDING
        and sources["requirement"]["classification"] == ORIGINAL_CLASS
        and sources["frozen_acceptance_condition"]["sha256"] == PROTOCOL_SHA256
        and sources["frozen_precommit"]["sha256"] == PRECOMMIT_SHA256
    )
    negative_allowed = (
        "if none changes materially" in protocol_row
        and "mathematical, not operational" in protocol_row.lower()
        and precommit["written_before_data"]
        and precommit["negative_rule_present"]
        and precommit["no_posthoc_metric_selection"]
    )
    conflicts: list[str] = []
    if not exact_source:
        conflicts.append("authoritative source wording, class, or hash mismatch")
    if not negative_allowed:
        conflicts.append("pre-outcome sources do not consistently authorize the negative path")
    semantics = "INVESTIGATIONAL" if negative_allowed and not conflicts else "AMBIGUOUS"
    return {
        "schema": "rebaseguard.l4r12-semantics.v1",
        "generator_owned": True,
        "original_wording": sources["requirement"]["wording"],
        "original_requirement_class": sources["requirement"]["classification"],
        "semantics": semantics,
        "existential_positive_transition_required": False if semantics == "INVESTIGATIONAL" else None,
        "negative_result_closure_allowed": semantics == "INVESTIGATIONAL",
        "frozen_acceptance_condition": (
            "Measure the preselected operational metrics on both sides of m*; "
            "if none changes materially, report the boundary as mathematical, not operational."
        ),
        "taxonomy_audit": {
            "pre_outcome_special_negative_status": False,
            "completion_status_available": "PASS",
            "later_observational_label": "NEGATIVE RESULT",
            "later_normalized_status": "PARTIAL",
            "pass_for_completed_negative_answer": True,
            "reason": (
                "The frozen source defines completion by conducting and reporting the two-sided "
                "investigation. It does not require a positive transition. PASS is the original "
                "completion state; NEGATIVE RESULT/PARTIAL was later normalization, not a "
                "pre-outcome acceptance condition."
            ),
        },
        "post_outcome_positive_requirement_would_rewrite_rubric": semantics == "INVESTIGATIONAL",
        "source_conflicts": conflicts,
        "classification_basis": [
            "D2.5 is phrased as testing whether the crossing predicts an operational change.",
            "The frozen protocol explicitly prescribes the report when no metric changes materially.",
            "The precommit explicitly commits smooth monotone behavior to the negative conclusion.",
            "No repository source frozen before D2.5 outcomes requires observing a positive transition.",
        ],
    }


def _monotone(values: list[float]) -> bool:
    return all(b >= a for a, b in zip(values, values[1:])) or all(
        b <= a for a, b in zip(values, values[1:])
    )


def build_evidence(sources: dict[str, Any], semantics: dict[str, Any]) -> dict[str, Any]:
    d2 = _json("level4/stage_d/results/d2_gamma_m.json")
    bridge = _json("level4/stage_d/results/d2_5_bridge.json")
    verdict = _json("level4/stage_d/results/d2_5_verdict.json")
    stage_d_adv = _json("level4/stage_d/results/adversarial_d.json")
    d4 = _json("level4/closure_proofs/d4_phase_map/results/decision.json")
    d4_adv = _json("level4/closure_proofs/d4_phase_map/results/adversarial.json")
    final_global = _json("level4/final_global_reaudit/results/final_decision.json")
    integrity = verify_integrity()
    bracket = d2["d2_2_bracket"]
    crossing = d4["gamma_equals_2_crossings"]
    rows = bridge["rows"]
    below = [row["m"] for row in rows if row["m"] < bridge["m_star_interp"]]
    above = [row["m"] for row in rows if row["m"] > bridge["m_star_interp"]]
    raw_monotone = {
        metric: _monotone([float(row[metric]["mean"]) for row in rows])
        for metric in PRIMARY_METRICS
    }
    adjacent_z: dict[str, float] = {}
    below_row = next(row for row in rows if row["m"] == 65)
    above_row = next(row for row in rows if row["m"] == 75)
    for metric in PRIMARY_METRICS:
        x, y = below_row[metric], above_row[metric]
        adjacent_z[metric] = abs(float(y["mean"]) - float(x["mean"])) / math.sqrt(
            float(x["se"]) ** 2 + float(y["se"]) ** 2
        )
    a6 = next(row for row in stage_d_adv["checks"] if row["id"] == "A6")
    claim_scan = _claim_scan(integrity["audited_commit"])
    original_final_row = next(
        row for row in final_global["requirements"] if row["id"] == "L4R-12"
    )

    checks: dict[str, tuple[bool, str, Any]] = {
        "N12.1": (
            bracket["gamma_lo"] > 2 > bracket["gamma_hi"]
            and abs(bracket["z_lo"]) > 3 and abs(bracket["z_hi"]) > 3,
            "Stage-D crossing bracket is on opposite sides of 2 by more than 3 SE",
            bracket,
        ),
        "N12.2": (
            len(crossing) == 1 and crossing[0]["bracket"] == [70, 72]
            and crossing[0]["gamma_at_bracket"][0] > 2
            and crossing[0]["gamma_at_bracket"][1] < 2
            and all(d4["criteria"].values()),
            "D4 independently refines and supports the crossing",
            crossing,
        ),
        "N12.3": (
            bridge["protocol_sha256"] == PROTOCOL_SHA256
            and bridge["precommit_sha256"] == PRECOMMIT_SHA256
            and sources["frozen_precommit"]["no_posthoc_metric_selection"],
            "operational metrics and the negative reading were frozen before outcomes",
            {"protocol_sha256": bridge["protocol_sha256"], "precommit_sha256": bridge["precommit_sha256"]},
        ),
        "N12.4": (
            below == [10, 20, 50, 65] and above == [75, 90, 100],
            "the complete seven-point operational grid covers both sides",
            {"below": below, "above": above},
        ),
        "N12.5": (
            verdict["n_metrics_peaking_at_m_star"] == 0
            and verdict["n_metrics_monotone"] == 4
            and all(not row["peaks_at_m_star"] and row["monotone"]
                    for row in verdict["per_metric_localisation"].values()),
            "no preselected primary metric localizes its steepest change at the crossing",
            verdict["per_metric_localisation"],
        ),
        "N12.6": (
            all(raw_monotone.values()) and a6["passed"],
            "monotonicity holds on raw tabulated means and crossing interpolation A6 passed",
            {"raw_monotone": raw_monotone, "interpolation_check": a6},
        ),
        "N12.7": (
            stage_d_adv["n_passed"] == stage_d_adv["n_checks"] == 12
            and d4_adv["passed"] == d4_adv["total"] == 14
            and d4_adv["history_integrity_passed"],
            "Stage-D replay checks and the later independently structured D4 audit both pass",
            {"stage_d": "12/12", "D4": "14/14"},
        ),
        "N12.8": (
            not claim_scan["contradictory_positive_conclusions"]
            and d4["operational_overlay"]["interpretation"].endswith(
                "These cells cannot overturn historical D2.5."
            ),
            "no contradictory operational conclusion exists in the audited repository",
            claim_scan,
        ),
        "N12.9": (
            bridge["n_replicates"] == 20000
            and min(adjacent_z.values()) > 3
            and "scientifically valid negative result" in original_final_row["reason"],
            "the curves resolve smooth neighbor changes; the result is not a low-power significance failure",
            {"n_replicates": bridge["n_replicates"], "m65_vs_m75_combined_separation": adjacent_z},
        ),
        "N12.10": (
            verdict["verdict"] == NEGATIVE_VERDICT
            and "DETERMINISTIC skeleton" in verdict["interpretation"],
            "the claim is limited to the frozen protocol and monitored metrics",
            {"historical_verdict": verdict["verdict"], "claim_scope": "frozen Gaussian CUSUM, rho=1, Stage-D convention, grid, shifts, and metrics"},
        ),
    }
    check_rows = [
        {"id": cid, "status": "PASS" if passed else "FAIL", "statement": statement, "evidence": evidence}
        for cid, (passed, statement, evidence) in checks.items()
    ]
    all_pass = all(passed for passed, _, _ in checks.values())
    evidence_sufficient = all_pass and integrity["status"] == "PASS"
    return {
        "schema": "rebaseguard.l4r12-evidence-assessment.v1",
        "generator_owned": True,
        "mode": "AUDIT_REPLAY_ONLY_NO_NEW_SCIENCE",
        "N12": check_rows,
        "n_passed": sum(row["status"] == "PASS" for row in check_rows),
        "n_total": 10,
        "evidence_sufficient": evidence_sufficient,
        "negative_result_class": (
            "C_COMPLETED_RESEARCH_QUESTION_WITH_VALID_NEGATIVE_ANSWER"
            if evidence_sufficient and semantics["negative_result_closure_allowed"]
            else "B_LOW_POWER_NON_DEMONSTRATION"
        ),
        "positive_hypothesis_status": "FALSIFIED_BY_PRECOMMITTED_TEST",
        "historical_verdict": verdict["verdict"],
        "crossing": {
            "stage_d_bracket": [bracket["m_lo"], bracket["m_hi"]],
            "stage_d_interpolated": bracket["m_star_interp"],
            "stage_d_endpoint_z": [bracket["z_lo"], -bracket["z_hi"]],
            "D4_bracket": crossing[0]["bracket"],
            "D4_interpolated": crossing[0]["m_crossing_log_linear"],
            "D4_gamma_at_bracket": crossing[0]["gamma_at_bracket"],
        },
        "operational_design": {
            "rho": bridge["rho"],
            "m_values": bridge["m_values"],
            "n_replicates": bridge["n_replicates"],
            "n_cycles": bridge["n_cycles"],
            "burn_in": bridge["burn_in"],
            "shifts": bridge["shifts"],
            "statistical_unit": bridge["statistical_unit"],
            "primary_metrics": list(PRIMARY_METRICS),
            "R_delta_reported": True,
        },
        "operational_result": {
            "metrics_peaking_at_crossing": verdict["n_metrics_peaking_at_m_star"],
            "metrics_monotone_in_log_m": verdict["n_metrics_monotone"],
            "nearest_pair_across_crossing": verdict["nearest_pair_across_m_star"],
            "m65_vs_m75_combined_separation": adjacent_z,
            "alternation_persists_above_crossing": verdict["alternation_persists_above_m_star"],
        },
        "same_requirement_mapping_candidate": (
            sources["requirement"]["id"] == "L4R-12"
            and sources["frozen_acceptance_condition"]["source"] == "level4/stage_d/STAGE_D_PROTOCOL.md"
            and semantics["negative_result_closure_allowed"]
            and evidence_sufficient
        ),
        "claim_safe": (
            "The Gamma_m=2 crossing is mathematically well-defined, but under the frozen "
            "monitoring metrics and protocol no corresponding operational transition was found; "
            "this negative result answers the pre-specified operational-consequence question."
        ),
        "claim_forbidden": "The crossing has no operational consequence in general.",
        "historical_D2_5_preserved": integrity["historical_D2_5_preserved"],
        "D4_preserved": integrity["D4_preserved"],
        "integrity": integrity,
    }


def build_all() -> dict[str, dict[str, Any]]:
    sources = build_sources()
    semantics = build_semantics(sources)
    evidence = build_evidence(sources, semantics)
    return {
        "source_extraction.json": sources,
        "semantic_classification.json": semantics,
        "evidence_assessment.json": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = build_all()
    mismatches = []
    for name, value in generated.items():
        path = RESULTS / name
        text = canonical_json(value)
        if args.check:
            if not path.exists() or path.read_text() != text:
                mismatches.append(name)
        else:
            path.write_text(text)
    if mismatches:
        print("L4R-12 audit artifacts are not byte-stable:", ", ".join(mismatches))
        return 1
    evidence = generated["evidence_assessment.json"]
    print(
        "L4R-12 audit replay: "
        f"{generated['semantic_classification.json']['semantics']}; "
        f"N12 {evidence['n_passed']}/{evidence['n_total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

