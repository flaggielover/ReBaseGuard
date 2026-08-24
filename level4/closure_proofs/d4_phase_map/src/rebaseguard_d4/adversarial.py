"""Frozen A1-A14 adversarial audit for the isolated D4 campaign."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .common import read_json, sha256, write_json
from .config import CAMPAIGN, M_GRID, PROTOCOL_SHA256, REPO, RESULTS, RHO_GRID


def _check(identifier: str, statement: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"id": identifier, "statement": statement, "passed": bool(passed), "detail": detail}


def verify_history() -> tuple[bool, dict[str, Any]]:
    manifest = read_json(RESULTS / "historical_hashes.json")
    inherited_path = REPO / manifest["inherited_manifest"]["path"]
    mismatches = []
    if sha256(inherited_path) != manifest["inherited_manifest"]["sha256"]:
        mismatches.append(str(inherited_path.relative_to(REPO)))
    for relative, expected in manifest["files"].items():
        path = REPO / relative
        if not path.is_file() or sha256(path) != expected:
            mismatches.append(relative)
    inherited = read_json(inherited_path)
    for relative, expected in inherited["files"].items():
        path = REPO / relative
        if not path.is_file() or sha256(path) != expected:
            mismatches.append(relative)
    return not mismatches, {"n_checked": len(manifest["files"]) + len(inherited["files"]) + 1,
                            "mismatches": sorted(set(mismatches))}


def _claim_text() -> str:
    paths = [
        RESULTS / "phase_map.json",
        RESULTS / "operational_overlay.json",
        CAMPAIGN / "PHASE_MAP_REPORT.md",
        CAMPAIGN / "OPERATIONAL_BRIDGE.md",
        CAMPAIGN / "FINAL_REPORT.md",
    ]
    return "\n".join(path.read_text() for path in paths if path.exists()).lower()


def _hidden_raw_dependency() -> tuple[bool, list[str]]:
    forbidden_keys = {"raw_paths", "trajectory", "trajectories", "lags_newest"}
    offenders = []

    def walk(value: Any, where: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in forbidden_keys:
                    offenders.append(f"{where}:{key}")
                walk(child, f"{where}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{where}[{index}]")
        elif isinstance(value, str) and value.startswith("/"):
            offenders.append(f"{where}:absolute-path")

    for path in RESULTS.glob("*.json"):
        walk(read_json(path), path.name)
    return not offenders, offenders


def run(*, pre_full: bool = False) -> dict[str, Any]:
    protocol_actual = sha256(CAMPAIGN / "PROTOCOL.md")
    stage_d = read_json(REPO / "level4/stage_d/results/stage_d_decision.json")
    stage_d_by_id = {row["id"]: row["status"] for row in stage_d["criteria"]}
    d25 = read_json(REPO / "level4/stage_d/results/d2_5_verdict.json")
    track1a = read_json(REPO / "level4/closure_proofs/m_gt_1_track1a/results/decision.json")
    track1b = read_json(REPO / "level4/closure_proofs/m_gt_1_track1b/results/decision.json")
    freeze = read_json(RESULTS / "protocol_hash.json")
    direct = read_json(RESULTS / "direct_validation.json")
    phase = read_json(RESULTS / "phase_map.json")
    operational = read_json(RESULTS / "operational_overlay.json")
    figure_index = read_json(CAMPAIGN / "figures/figure_index.json")
    history_ok, history_detail = verify_history()
    claims = _claim_text()
    no_raw, raw_detail = _hidden_raw_dependency()
    figure_inputs = set(figure_index["inputs"])
    expected_figure_inputs = {
        "results/phase_map.json", "results/operational_overlay.json",
        "results/direct_validation.json",
    }
    source_text = (CAMPAIGN / "src/rebaseguard_d4/gamma_grid.py").read_text()
    verification = (
        read_json(RESULTS / "verification.json")
        if (RESULTS / "verification.json").exists()
        else {"status": "PENDING"}
    )
    checks = [
        _check("A1", "protocol hash unchanged", protocol_actual == PROTOCOL_SHA256,
               {"expected": PROTOCOL_SHA256, "actual": protocol_actual}),
        _check("A2", "Stage-D D2.3 FAIL preserved", stage_d_by_id.get("D2.3") == "FAIL",
               stage_d_by_id.get("D2.3")),
        _check("A3", "D2.5 MATHEMATICAL, NOT OPERATIONAL preserved",
               d25["verdict"] == "MATHEMATICAL, NOT OPERATIONAL",
               d25["verdict"]),
        _check("A4", "Track 1A FAIL preserved", track1a["decision"] == "MGT1-TRACK1A-FAILED",
               track1a["decision"]),
        _check("A5", "Track 1B CLOSED preserved", track1b["decision"] == "MGT1-TRACK1B-CLOSED",
               track1b["decision"]),
        _check("A6", "Stage-A dwell semantics never substituted",
               "minimum_dwell=None" in source_text and "stage_a" not in source_text.lower(),
               "Gamma simulator calls ordinary-stop Track-1B primitive with minimum_dwell=None"),
        _check("A7", "no post-outcome grid change",
               freeze["m_grid"] == M_GRID.tolist() and freeze["rho_grid"] == RHO_GRID.tolist()
               and phase["m_grid"] == M_GRID.tolist() and phase["rho_grid"] == RHO_GRID.tolist(),
               {"m_grid": phase["m_grid"], "rho_grid": phase["rho_grid"]}),
        _check("A8", "no post-outcome interpolation change",
               freeze["interpolation"] == "piecewise-linear in log(m) on raw GammaTilde_m point estimates",
               freeze["interpolation"]),
        _check("A9", "direct-map validation independent enough",
               direct["checks"]["source_separation"] and direct["valid"],
               direct["source_separation"]),
        _check("A10", "no operational phase-transition overclaim",
               "operational phase transition" not in claims and "system bifurcation map" not in claims,
               "claim artifacts scanned"),
        _check("A11", "no universal or distribution-free wording",
               "universal phase transition" not in claims and "distribution-free" not in claims,
               "claim artifacts scanned"),
        _check("A12", "figures generated from final JSON only",
               figure_index["source_policy"] == "figures generated from final JSON only"
               and figure_inputs == expected_figure_inputs,
               sorted(figure_inputs)),
        _check("A13", "no hidden raw-data dependency", no_raw, raw_detail),
        _check("A14", "full verifier green",
               verification.get("status") == "PASS" if not pre_full else False,
               "PENDING" if pre_full else verification.get("status")),
    ]
    output = {
        "schema": "rebaseguard.d4-adversarial.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "mode": "PRE-FULL-A1-A13" if pre_full else "FINAL-A1-A14",
        "checks": checks,
        "passed": sum(row["passed"] for row in checks),
        "total": len(checks),
        "history_integrity": history_detail,
        "history_integrity_passed": history_ok,
    }
    required = checks[:13] if pre_full else checks
    output["valid"] = all(row["passed"] for row in required) and history_ok
    write_json(RESULTS / ("adversarial_pre_full.json" if pre_full else "adversarial.json"), output)
    if not output["valid"]:
        failed = [row["id"] for row in required if not row["passed"]]
        raise RuntimeError(f"D4 adversarial checks failed: {failed}")
    return output
