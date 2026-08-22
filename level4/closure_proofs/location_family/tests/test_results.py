from __future__ import annotations

import hashlib
import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def _load(name: str):
    return json.loads((CAMPAIGN / "results" / name).read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_numerical_artifacts_are_frozen_and_exact():
    manifest = _load("numerical_artifact_manifest.json")
    assert manifest["decision"] == "LOCATION-FAMILY-NUMERICAL-FAILED"
    for relative, expected in manifest["sha256"].items():
        assert _sha256(CAMPAIGN / relative) == expected, relative


def test_exact_frozen_failure_and_lean_stop_are_preserved():
    decision = _load("numerical_decision.json")
    assert decision["status"] == "LOCATION-FAMILY-NUMERICAL-FAILED"
    assert decision["declaration"] == "NUMERICAL GATE FAILED — LEAN NOT AUTHORIZED"
    assert decision["lean_authorized"] is False
    assert decision["all_regular_families_pass"] is False
    assert not (CAMPAIGN / "lean").exists()


def test_t3_has_the_only_failed_primary_predicate():
    decision = _load("numerical_decision.json")
    failed = []
    for row in decision["rows"]:
        for criterion, passed in row["criteria"].items():
            if not passed:
                failed.append((row["family"], criterion))
    assert failed == [("t3", "replication_relative_le_3pct")]
    t3 = next(row for row in decision["rows"] if row["family"] == "t3")
    assert t3["correspondence_abs_z"] == 0.15830764400154898
    assert t3["correspondence_relative"] == 0.009948503999464772
    assert t3["replication_abs_z"] == 1.3182234438470144
    assert t3["replication_relative"] == 0.04605351425844214
    assert t3["pass"] is False


def test_five_regular_families_pass_but_cannot_rescue_gate():
    decision = _load("numerical_decision.json")
    passing = [row["family"] for row in decision["rows"] if row["pass"]]
    assert passing == ["gaussian", "t10", "t5", "contam0.05", "contam0.1"]
    assert decision["all_regular_families_pass"] is False


def test_gaussian_control_reproduces_existing_theorem():
    decision = _load("numerical_decision.json")
    control = decision["gaussian_control"]
    assert control["pass"] is True
    assert control["abs_z"] < 3.0
    assert control["relative_discrepancy"] < 0.02
    gaussian = next(row for row in decision["rows"] if row["family"] == "gaussian")
    assert gaussian["gamma_f"] == 15.937502174003612
    assert gaussian["pass"] is True


def test_all_tie_operating_point_and_structural_controls_pass():
    decision = _load("numerical_decision.json")
    structural = _load("structural_controls.json")
    assert structural["pass"] is True
    for row in decision["rows"]:
        assert row["criteria"]["route_a_zero_ties"] is True
        assert row["criteria"]["route_b_zero_ties"] is True
        assert row["criteria"]["route_a_arl_within_2pct"] is True


def test_t3_estimand_resolution_preserves_historical_ambiguity():
    resolution = _load("numerical_decision.json")["t3_estimand_resolution"]
    assert resolution["new_raw_reuse_gamma_f"] == 8.710087311547682
    assert resolution["historical_gamma_psi"] == 2.5979720736709115
    assert resolution["historical_gamma_psi_over_Epsi_prime"] == 1.2989860304369447
    assert resolution["mathematical_resolution"].startswith("NEITHER")
    assert "remains AMBIGUOUS" in resolution["mathematical_resolution"]


def test_independent_retained_summary_audit_reproduces_failure():
    audit = _load("numerical_audit.json")
    assert audit["pass"] is True
    assert audit["failed_predicates"] == ["t3:replication_relative_le_3pct"]
    assert audit["recomputed_status"] == "LOCATION-FAMILY-NUMERICAL-FAILED"
    assert audit["lean_authorized"] is False

