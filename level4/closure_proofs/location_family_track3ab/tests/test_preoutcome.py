from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import numpy as np

from rebaseguard_location_family_track3ab.frozen import (
    BATCHES,
    HISTORICAL_DERIVATIVE_SCALE,
    HISTORICAL_ROUTE_A_PATH_SD,
    HISTORICAL_ROUTE_B_PATH_SD_UPPER,
    H_STEPS,
    MASTER_SEED,
    PRIMARY_H,
    REPLICATIONS,
    ROUTE_A_PATHS_PER_BATCH,
    ROUTE_B_PATHS_PER_BATCH,
    THRESHOLD,
)
from rebaseguard_location_family_track3ab.route_a import t3_location_score
from rebaseguard_location_family_track3ab.statistics import (
    combined_z,
    mean_se,
    symmetric_relative_difference,
)


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def test_historical_track3_decision_is_immutable() -> None:
    decision = json.loads(
        (REPO / "level4/closure_proofs/location_family/results/decision.json").read_text()
    )
    numerical = json.loads(
        (REPO / "level4/closure_proofs/location_family/results/numerical_decision.json").read_text()
    )
    assert decision["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
    assert numerical["status"] == "LOCATION-FAMILY-NUMERICAL-FAILED"
    assert numerical["lean_authorized"] is False


def test_historical_manifest_hashes() -> None:
    path = CAMPAIGN / "results/historical_manifest.json"
    if not path.exists():
        return
    manifest = json.loads(path.read_text())
    assert all(digest(REPO / rel) == expected for rel, expected in manifest["sha256"].items())


def test_protocol_hash() -> None:
    path = CAMPAIGN / "results/protocol_hash.json"
    if not path.exists():
        return
    frozen = json.loads(path.read_text())
    assert digest(CAMPAIGN / "PROTOCOL.md") == frozen["sha256"]
    assert frozen["confirmatory_outcomes_existed_at_freeze"] is False


def test_fresh_seed_design_is_pairwise_disjoint() -> None:
    keys = [
        (MASTER_SEED, route, rep, batch)
        for route in (10, 20)
        for rep in range(1, REPLICATIONS + 1)
        for batch in range(BATCHES)
    ]
    assert MASTER_SEED != 2026082307
    assert len(keys) == len(set(keys))


def test_t3_score_formula_and_bound() -> None:
    z = np.linspace(-100.0, 100.0, 200_001)
    assert np.array_equal(t3_location_score(z), 4.0 * z / (1.0 + z * z))
    assert np.max(np.abs(t3_location_score(z))) <= 2.0 + 1e-14


def test_gaussian_specialization() -> None:
    z = np.array([-4.0, -0.5, 0.0, 0.5, 4.0])
    log_density_derivative = -z
    psi = -log_density_derivative
    assert np.array_equal(psi, z)


def test_route_sources_are_separate() -> None:
    a = CAMPAIGN / "src/rebaseguard_location_family_track3ab/route_a.py"
    b = CAMPAIGN / "src/rebaseguard_location_family_track3ab/route_b.py"
    assert not any("route_b" in name for name in imported_modules(a))
    assert not any("route_a" in name for name in imported_modules(b))
    b_text = b.read_text().lower()
    assert all(
        token not in b_text
        for token in ("location_score", "score_sum", "gamma_f", "stopped_gain")
    )


def test_h_ladder_and_operating_point() -> None:
    assert H_STEPS == (0.05, 0.025, 0.0125)
    assert PRIMARY_H == 0.0125
    assert THRESHOLD == 6.337011391962933


def test_variance_aware_sizing_rule() -> None:
    n_a = BATCHES * ROUTE_A_PATHS_PER_BATCH
    n_b = BATCHES * ROUTE_B_PATHS_PER_BATCH
    relative_se = np.hypot(
        HISTORICAL_ROUTE_A_PATH_SD / np.sqrt(n_a),
        HISTORICAL_ROUTE_B_PATH_SD_UPPER / np.sqrt(n_b),
    ) / HISTORICAL_DERIVATIVE_SCALE
    assert relative_se <= 0.01


def test_batch_statistics_and_relative_definition() -> None:
    mean, se = mean_se(np.array([1.0, 2.0, 3.0, 4.0]))
    assert mean == 2.5
    assert np.isclose(se, np.std([1.0, 2.0, 3.0, 4.0], ddof=1) / 2.0)
    assert np.isclose(symmetric_relative_difference(-7.0, -7.21), 0.21 / 7.105)
    assert combined_z(2.0, 3.0, 2.0, 4.0) == 0.0


def test_variance_diagnosis_replayed_historical_batches() -> None:
    diagnosis = json.loads(
        (CAMPAIGN / "results/historical_variance_diagnosis.json").read_text()
    )
    assert diagnosis["historical_seed_replay_only"] is True
    assert diagnosis["fresh_campaign_outcomes_generated"] is False
    assert diagnosis["route_a"]["replay_max_abs_error"] == 0.0
    assert max(
        rep["replay_max_abs_error"] for rep in diagnosis["route_b"]["replications"]
    ) < 1e-12
    assert np.isclose(
        diagnosis["route_b"]["primary_replication_comparison"][
            "symmetric_relative_difference"
        ],
        0.0460535142584416,
    )


def test_no_confirmatory_outcome_before_freeze() -> None:
    protocol_hash = CAMPAIGN / "results/protocol_hash.json"
    checkpoints = CAMPAIGN / "results/checkpoints"
    if checkpoints.exists() and any(checkpoints.rglob("*.json")):
        assert protocol_hash.exists()
