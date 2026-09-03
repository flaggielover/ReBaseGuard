"""C1-C7 derivation, ledger completeness, Route-Q role, CUT-2, Gaussian
statistic, and the final verdict derivation."""

from __future__ import annotations

import math
import subprocess

import pytest


# ------------------------------------------------------------- ledger --

def test_cell_ledger_records_every_required_field(ledger):
    required = {"layer", "detector", "family", "m", "route_a", "route_b",
                "h_values", "richardson", "relative_discrepancy", "z",
                "gate_result", "precision_status"}
    per_route = {"estimate", "se", "relative_se", "paths", "blocks",
                 "block_size", "cpu_seconds", "wall_seconds", "peak_rss_mb",
                 "precision_status"}
    for c in ledger["cells"]:
        assert required <= set(c), (c["config"], c["m"])
        for route in ("route_a", "route_b"):
            assert per_route <= set(c[route]), (c["config"], route)


def test_no_failed_cell_is_hidden(ledger):
    counted = (ledger["cells_passed"] + ledger["cells_failed"]
               + ledger["cells_precision_limited"]
               + ledger.get("cells_precondition_not_met", 0))
    assert counted == ledger["cells_total"] == 96
    failed = [c for c in ledger["cells"] if c["gate_result"] == "FAIL"]
    assert len(failed) == ledger["cells_failed"]
    assert {(c["config"], c["m"]) for c in failed} == {
        (c["config"], c["m"]) for c in ledger["failed_cells"]}


def test_gate_result_is_recomputable_from_the_frozen_criterion(ledger):
    for c in ledger["cells"]:
        if c["gate_result"] in {"PRECISION_LIMITED", "PRECONDITION_NOT_MET"}:
            continue
        expected = ("PASS" if (c["relative_discrepancy"] <= 0.03
                               and c["z"] <= 4.0) else "FAIL")
        assert c["gate_result"] == expected, (c["config"], c["m"])


def test_precondition_not_met_cells_are_not_counted_as_passes(ledger):
    """Checkpoint A X6 requires a route to reach r* (or be PRECISION_LIMITED)
    BEFORE the gate is adjudicated.  A cell whose route got its one frozen
    top-up and still missed r*, without hitting a cap, satisfies neither
    branch, so its criterion value may not be read as a pass."""
    unmet = [c for c in ledger["cells"]
             if c["gate_result"] == "PRECONDITION_NOT_MET"]
    assert len(unmet) == ledger.get("cells_precondition_not_met", 0)
    for c in unmet:
        assert c["precondition_unmet"] is True, (c["config"], c["m"])
        assert "criterion_satisfied_informational" in c
        # a route below target is what makes the precondition unmet
        assert any(c[r]["precision_status"] == "BELOW_TARGET"
                   for r in ("route_a", "route_b")), (c["config"], c["m"])
    if unmet:
        assert ledger["C2"] == "INCOMPLETE"


def test_below_target_routes_are_never_silently_passed(ledger):
    for c in ledger["cells"]:
        below = any(c[r]["precision_status"] == "BELOW_TARGET"
                    for r in ("route_a", "route_b"))
        if below:
            assert c["gate_result"] != "PASS", (c["config"], c["m"])


def test_discrepancy_and_z_are_recomputable(ledger):
    for c in ledger["cells"]:
        a, b = c["route_a"], c["route_b"]
        diff = abs(a["estimate"] - b["estimate"])
        scale = max(abs(a["estimate"]), abs(b["estimate"]))
        assert c["absolute_difference"] == pytest.approx(diff, rel=1e-9)
        assert c["relative_discrepancy"] == pytest.approx(diff / scale, rel=1e-9)
        combined = math.hypot(a["se"], b["se"])
        assert c["combined_se"] == pytest.approx(combined, rel=1e-9)
        assert c["z"] == pytest.approx(diff / combined, rel=1e-9)


def test_no_cell_used_a_weakened_tolerance(ledger):
    for c in ledger["cells"]:
        assert c["gate_relative_limit"] == 0.03
        assert c["gate_z_limit"] == 4.0


# ------------------------------------------------------------- Route Q --

def test_route_q_is_cross_check_only(verdict, checkpoint):
    assert checkpoint["route_q_role"]["role"] == "INDEPENDENT_CROSS_CHECK_ONLY"
    c3 = verdict["obligations"]["C3"]
    assert c3["role"] == "INDEPENDENT_CROSS_CHECK_ONLY"
    assert c3["arbitrated_any_cell"] is False
    assert c3["rescued_any_gate"] is False
    assert c3["cross_check"] in {"CONSISTENT", "INCONSISTENT", "NOT_APPLICABLE"}


def test_route_q_did_not_enter_any_cell_decision(ledger):
    for c in ledger["cells"]:
        assert "route_q" not in c
        assert c["gate_result"] in {
            "PASS", "FAIL", "PRECISION_LIMITED", "PRECONDITION_NOT_MET"}


# --------------------------------------------------------------- CUT-2 --

def test_cut2_split_semantics(p1, checkpoint):
    c4 = p1["C4"]
    assert c4["a3_half"]["new_compute"] == "NONE"
    assert c4["first_moment_half"]["new_compute"] == "NONE"
    assert "FALSE" in c4["a3_half"]["proved_failure_mode"]
    assert "NON-EXISTENCE" in c4["first_moment_half"]["proved_failure_mode"]
    assert c4["first_moment_half"]["monte_carlo_signature_demanded"] is False
    assert checkpoint["assumption_semantics"]["necessity_claimed"] is False


def test_cut2_a3_is_discharged_by_exact_evidence(p1):
    checks = p1["C4"]["a3_half"]["checks"]
    assert checks["route_q_identity_does_not_hold"] is True
    assert checks["route_q_score_side_exactly_zero"] is True
    assert checks["arb_uniform_identity_defect_positive"] is True


# ------------------------------------------------------ Gaussian C5 --

def test_gaussian_two_sample_formula(p1):
    c5 = p1["C5"]
    assert c5["formula"] == "z_combined = |e1 - e2| / sqrt(SE1^2 + SE2^2)"
    assert c5["limit"] == 4.0
    assert c5["cells"] == 8
    assert c5["treats_either_estimate_as_exact"] is False
    for r in c5["rows"]:
        expected = abs(r["p4x_estimate"] - r["closed_estimate"]) / math.hypot(
            r["p4x_se"], r["closed_se"])
        assert r["z_combined"] == pytest.approx(expected, rel=1e-9)
        assert r["pass"] == (r["z_combined"] <= 4.0)


def test_gaussian_uses_both_published_uncertainties(p1):
    for r in p1["C5"]["rows"]:
        assert r["closed_se"] > 0
        assert r["p4x_se"] > 0


# ---------------------------------------------------------- C1-C7 ledger --

@pytest.mark.parametrize("ob", ["C1", "C2", "C3", "C4", "C5", "C6", "C7"])
def test_every_obligation_has_a_frozen_status(verdict, ob):
    assert verdict["obligations"][ob]["status"] in {"PASS", "FAIL", "INCOMPLETE"}


def test_verdict_derivation_is_mechanical(verdict):
    statuses = {k: v["status"] for k, v in verdict["obligations"].items()}
    all_pass = all(s == "PASS" for s in statuses.values())
    any_fail = any(s == "FAIL" for s in statuses.values())
    if all_pass:
        expected = "CLOSED"
    elif verdict["load_bearing_contradiction"] or verdict["integrity_failure"]:
        expected = "FAIL"
    else:
        expected = "PARTIAL"
    assert verdict["P4X_SUCCESSOR_VERDICT"] == expected
    assert verdict["P4X_SUCCESSOR_VERDICT"] in {"CLOSED", "PARTIAL", "FAIL"}
    if any_fail and not (verdict["load_bearing_contradiction"]
                         or verdict["integrity_failure"]):
        assert expected == "PARTIAL"


def test_closed_requires_all_seven(verdict):
    if verdict["P4X_SUCCESSOR_VERDICT"] == "CLOSED":
        assert all(v["status"] == "PASS"
                   for v in verdict["obligations"].values())


def test_historical_p4_is_untouched(verdict):
    assert verdict["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    assert verdict["P4_ORIGINAL_MUTATED"] == "NO"
    assert verdict["P5_P5X_MUTATED"] == "NO"


def test_scientific_line_status_follows_the_verdict(verdict):
    v, line = verdict["P4X_SUCCESSOR_VERDICT"], verdict["P4_SCIENTIFIC_LINE_STATUS"]
    if v == "CLOSED":
        assert line == "CLOSED_BY_SUCCESSOR_CAMPAIGN"
    else:
        assert line in {"PARTIALLY_REPAIRED_BY_SUCCESSOR", "UNCHANGED_PARTIAL"}


def test_novelty_and_level4_unchanged(verdict):
    assert verdict["NOVELTY_STATUS"] == "NOT_ESTABLISHED"
    assert verdict["LEVEL4_GLOBAL_CLOSURE"] == "NO"


# ----------------------------------------------------------- integrity --

def test_protected_tree_verified_before_and_after(verdict, root):
    pt = verdict["obligations"]["C7"]
    assert pt["readings"]["pre_production"] == "PASS"
    assert pt["readings"]["post_production"] == "PASS"
    assert pt["readings"]["pre_verdict"] == "PASS"
    for path, expected in pt["manifest"].items():
        got = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{path}"], cwd=root, text=True).strip()
        assert got == expected, path


def test_c6_added_no_new_lean_or_arb(c6):
    assert c6["new_lean_declarations"] == 0
    assert c6["new_arb_objects"] == 0
    assert c6["lean"]["declarations_audited"] == 19
    assert set(c6["lean"]["axioms_observed"]) <= {
        "propext", "Classical.choice", "Quot.sound"}
