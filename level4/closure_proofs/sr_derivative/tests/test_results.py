from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"


def load(name: str):
    return json.loads((RESULTS / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_numerical_artifact_hashes_are_frozen():
    manifest = load("numerical_artifact_manifest.json")
    assert manifest["decision"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    assert {
        path: sha(CAMPAIGN / path) for path in manifest["files"]
    } == manifest["files"]


def test_calibration_checks_pass_in_distinct_roles():
    data = load("calibration.json")
    assert data["passed"] is True
    assert data["criteria"] == {
        "candidate_within_2_percent": True,
        "fixed_arl_ratio_within_1_percent": True,
    }
    assert data["bisection"]["candidate"] == 522.6191238793916
    assert data["bisection"]["candidate_relative_error"] < 0.02
    assert abs(data["fixed_operating_point"]["ratio"] - 1.0) < 0.01
    assert data["bisection"]["candidate"] != 520.886133602749


def test_route_a_score_prediction_and_tie_guard_pass():
    data = load("route_a.json")
    assert data["passed"] is True
    assert data["summary"]["gamma"]["mean"] == 17.291320922042853
    assert data["summary"]["predicted_derivative"]["mean"] == (
        1.0 - data["summary"]["gamma"]["mean"]
    )
    assert abs(data["summary"]["historical_combined_z"]) <= 4.0
    assert data["summary"]["batch_t_lower_99"] > 2.0
    assert data["summary"]["lower_bound_status"] == "CONFIRMATORY NUMERICAL ONLY"
    assert data["summary"]["exact_ties"] == 0


def test_route_b_se_is_recomputed_from_paired_batch_derivatives():
    data = load("route_b.json")
    rows = data["batches"]
    assert len(rows) == 128
    derivatives = np.asarray([row["paired_derivative"] for row in rows])
    plus = np.asarray([row["map_plus"] for row in rows])
    minus = np.asarray([row["map_minus"] for row in rows])
    h = np.asarray(data["design"]["h_grid"])
    np.testing.assert_allclose(derivatives, (plus - minus) / (2.0 * h), rtol=1e-14)
    pooled = derivatives.mean(axis=0)
    pooled_se = derivatives.std(axis=0, ddof=1) / np.sqrt(derivatives.shape[0])
    np.testing.assert_allclose(
        pooled, [row["pooled"]["mean"] for row in data["summaries"]], rtol=1e-15
    )
    np.testing.assert_allclose(
        pooled_se, [row["pooled"]["se"] for row in data["summaries"]], rtol=1e-15
    )


def test_route_b_frozen_primary_and_replication_criteria_pass():
    data = load("route_b.json")
    assert data["passed"] is True
    assert data["design"]["primary_h"] == 0.0125
    assert data["primary"]["pooled"]["mean"] == -16.195009584908167
    assert abs(data["primary"]["pooled_z_vs_route_a"]) <= 3.0
    assert all(abs(value) <= 4.0 for value in data["primary"]["replication_z_vs_route_a"])
    assert abs(data["primary"]["replication_agreement_z"]) <= 3.0
    assert data["primary"]["relative_discrepancy"] <= 0.02
    assert data["exact_ties"] == 0
    assert data["secondary_diagnostics"]["controls_verdict"] == (
        "DIAGNOSTIC ONLY; CANNOT FAIL OR RESCUE PRIMARY"
    )


def test_numerical_gate_authorizes_lean_but_not_rigorous_instability():
    decision = load("numerical_decision.json")
    assert decision["passed"] is True
    assert decision["decision"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    assert all(decision["criteria"].values())
    assert decision["gamma_inequality_status"] == "CONFIRMATORY NUMERICAL ONLY"
    assert decision["rigorous_sr_local_instability_certificate"] == "OPEN"

