"""Post-result assertions for P5Y Gate-1.  Every headline claim is checked
against a produced artifact, and the governance invariants are checked against
git rather than against the working tree (the P5X D5-D9 lesson)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"
CAP_CPU_HOURS = 5.0


def load(n):
    return json.loads((R / n).read_text())


# ------------------------------------------------------------------ M1
def test_m1_near_cell_overlaps_historical_r2_anchor():
    d = load("m1_raw_2cell.json")
    assert d["verdict"]["A1_near_overlaps_r2_anchor"] is True


def test_m1_z_control_reproduces_the_historical_r2_enclosure():
    """The control arm must land on R2's published interval, or the comparison
    is not ceteris paribus."""
    d = load("m1_raw_2cell.json")
    z = d["cells"]["A_near"]["arms"]["z_control"]
    lo, hi = d["frozen"]["r2_anchor"]
    assert abs(z["R_lower"] - lo) < 1e-12
    assert abs(z["R_upper"] - hi) < 1e-10


def test_m1_far_cell_half_width_below_frozen_threshold():
    d = load("m1_raw_2cell.json")
    assert d["cells"]["B_far"]["arms"]["raw"]["half_width"] < 1.0


def test_m1_raw_beats_z_in_the_far_field():
    d = load("m1_raw_2cell.json")
    assert d["verdict"]["far_width_reduction_vs_z_control"] > 10.0


def test_m1_uses_exactly_the_two_frozen_cells():
    d = load("m1_raw_2cell.json")
    assert set(d["cells"]) == {"A_near", "B_far"}
    assert d["frozen"]["cells"]["B_far"] == [10.5441104, 12.0]


def test_m1_subcells_tile_exactly():
    d = load("m1_raw_2cell.json")
    for c in d["cells"].values():
        assert c["tiles_exactly"] is True


def test_m1_verdict_is_mechanical():
    d = load("m1_raw_2cell.json")
    v = d["verdict"]
    expect = "PASS" if (v["A1_near_overlaps_r2_anchor"] and v["A2_far_half_width_below_1.0"]
                        and v["A4_near_half_width_below_0.05"]) else "FAIL"
    assert v["PILOT_RAW_2CELL"] == expect


# ------------------------------------------------------------------ M2
def test_m2_degree_grid_was_not_expanded():
    d = load("m2_sr_degree.json")
    assert d["frozen"]["degrees"] == [8, 10, 12]
    assert set(d["degrees"]) == {"6", "8", "10", "12"}
    assert d["degrees"]["6"]["role"] == "control_only_not_selectable"


def test_m2_selected_degree_passed_every_mathematical_gate():
    d = load("m2_sr_degree.json")
    s = str(d["selected_degree"])
    assert d["degrees"][s]["math_gates_all_pass"] is True
    assert d["degrees"][s]["cost"]["P4_pass"] is True


def test_m2_selection_is_lowest_qualifying_degree():
    d = load("m2_sr_degree.json")
    q = d["qualifying_degrees"]
    assert d["selected_degree"] == (min(q) if q else None)


def test_m2_no_degree_passed_on_cost_while_failing_maths():
    """A faster candidate that fails a mathematical gate must be FAIL."""
    d = load("m2_sr_degree.json")
    for k, g in d["degrees"].items():
        if not g.get("math_gates_all_pass", False):
            assert g["verdict"] == "FAIL", f"degree {k} passed despite failing maths"


def test_m2_cost_budget_is_the_frozen_r3_threshold():
    d = load("m2_sr_degree.json")
    assert d["frozen"]["budget"] == 0.3314531805
    assert d["frozen"]["timing_repeats"] == 5


def test_m2_higher_degrees_failed_on_conditioning_not_on_cost():
    """Recorded finding: degrees 10 and 12 are cheaper but mathematically dead."""
    d = load("m2_sr_degree.json")
    for k in ("10", "12"):
        g = d["degrees"][k]
        assert g["cost"]["P4_pass"] is True
        assert g["math_gates"]["P2_relative_half_width"] > 0.5
        assert g["verdict"] == "FAIL"


# ------------------------------------------------------------------ M3
def test_m3_backend_was_not_built_because_m2_passed():
    d = load("m3_analytic.json")
    m2 = load("m2_sr_degree.json")
    assert m2["PILOT_SR_DEGREE"] == "PASS"
    assert d["summary"]["backend_built"] is False
    assert d["decisive"] is False


def test_m3_transform_identity_verified():
    d = load("m3_analytic.json")
    assert d["checks"]["X1_transform_identity_holds"] is True
    assert d["checks"]["X1_alarm_equivalence_holds"] is True


def test_m3_panel_count_is_deterministic_and_disclosed():
    d = load("m3_analytic.json")
    p = d["checks"]["X3_panels"]
    assert p["induced_panel_count"] == p["closed_form_upper_bound"] == 127
    assert p["within_brief_default"] is False, "the 100 default must be reported as breached"
    assert p["within_frozen_threshold"] is True


def test_m3_precision_obstacle_is_recorded():
    a = load("m3_precision_addendum.json")
    assert "400+" in a["consequence_for_M3"]
    assert a["decisive"] is False


# ------------------------------------------------------- optional / general
def test_optional_checks_are_marked_non_decisive():
    d = load("optional_checks.json")
    assert d["decisive"] is False
    assert d["PILOT_SMIN_ANALYTIC"]["kind"] == "SCOPING_CHECK_NOT_A_CERTIFICATE"


def test_mshare_multiplier_correction():
    d = load("optional_checks.json")["PILOT_MSHARE"]
    assert d["no_m_specific_solve"] is True
    assert d["overcount_factor"] > 1.5


def test_farfield2_reproduces_published_L3_values():
    rows = load("optional_checks.json")["PILOT_FARFIELD2"]["rows"]
    cus12 = [r for r in rows if r["detector"] == "cusum" and r["e"] == 12.0][0]
    sr12 = [r for r in rows if r["detector"] == "sr" and r["e"] == 12.0][0]
    assert abs(cus12["B1_float"] - 5.37e-10) / 5.37e-10 < 0.01     # PROOF.md L3.4
    assert abs(sr12["B1_float"] - 8.57e-07) / 8.57e-07 < 0.01


def test_cpu_cap_was_respected():
    m1 = load("m1_raw_2cell.json")
    total = m1["runtime"]["cpu_hours_children_total"] + 0.01
    assert total < CAP_CPU_HOURS, f"CPU cap breached: {total}"


def test_no_pilot_claims_to_be_binding_or_production():
    for n in ("m1_raw_2cell.json", "m2_sr_degree.json", "m3_analytic.json",
              "optional_checks.json", "cost_model.json"):
        assert load(n)["binding"] is False


def test_no_monte_carlo_on_any_decision_path():
    for f in ("raw_certifier.py", "m1_raw_2cell.py", "m2_sr_degree.py"):
        src = (HERE / f).read_text().lower()
        for bad in ("random", "monte", "np.random", "seed"):
            assert bad not in src, f"{f} references {bad}"


def test_temporal_anchor_ordering_against_git_not_the_worktree():
    """The T0/T1 anchor commit must contain no results file.  Asserted with
    git ls-tree on the named commit, never by inspecting the working tree."""
    log = subprocess.run(["git", "log", "--format=%H %s", "-20"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    anchors = [l.split()[0] for l in log if "T1 re-freeze" in l or "T0/T1" in l]
    assert anchors, "no Gate-1 anchor commit found"
    for a in anchors:
        tree = subprocess.run(["git", "ls-tree", "-r", a, "--name-only"], cwd=ROOT,
                              capture_output=True, text=True).stdout
        assert "p5y_micropilot_gate1/results/" not in tree, \
            f"anchor {a[:8]} already contained results"


def test_protected_tree_untouched_by_this_gate():
    base = subprocess.run(["git", "rev-parse", "c123b9b"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    diff = subprocess.run(["git", "diff", "--name-only", base, "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    outside = [d for d in diff if d.strip()
               and not d.startswith("level4/closure_proofs/p5y_micropilot_gate1/")]
    assert not outside, f"P5/P5X or other protected paths modified: {outside}"
