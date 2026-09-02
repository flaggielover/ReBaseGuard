"""SR full-cell prototype invariants.  Preserves the FAIL; nothing is rewritten."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "results" / "sr_prototype.json").read_text())
C = R["criteria"]


def test_prototype_fail_is_preserved():
    assert R["gate"] == "FAIL"
    assert set(R["failed_criteria"]) == {"P3_resolvent_bound", "P4_half_width"}


def test_resolvent_never_converged_within_the_frozen_budget():
    p = C["P3_resolvent_bound"]
    assert p["C"] is None and p["q_final"] == 1.0 and p["n_max"] == 4000


def test_tractability_established_despite_the_failure():
    t = R["tractability"]
    assert t["z_panels"] == 0 and t["softplus"] == 0
    assert t["ms_per_cell"] < 1.0 and t["full_64x64_sweep_s"] < 10


def test_science_corroborated_by_diagnostic_only_evidence():
    p = C["P6_correspondence_diagnostic_only"]
    assert p["deviation_in_standard_errors"] < 3.0
    assert "DIAGNOSTIC ONLY" in p["note"]


def test_both_blockers_recorded_with_evidence():
    ids = {b["id"]: b for b in R["blockers"]}
    assert set(ids) == {"B1", "B2"}
    assert ids["B1"]["class"] == "RESOLVENT_BOUND_NOT_OBTAINED"
    assert ids["B2"]["class"] == "INTERVAL_DEPENDENCY"
    assert ids["B2"]["evidence"]["blowup"] > 1e9


def test_stop_was_recorded_with_unfrozen_alternatives():
    s = R["stop"]
    assert "condition 8" in s["rule"]
    assert len(s["paths_B1"]) >= 2 and len(s["paths_B2"]) >= 2


def test_no_production_was_launched():
    assert "production" not in R and "full_cover" not in R


def test_anchor_is_checkpoint_i():
    assert R["checkpoint_i"] == "3fe7e0a81bb8a46640469e1b1186998ee1363df4"
