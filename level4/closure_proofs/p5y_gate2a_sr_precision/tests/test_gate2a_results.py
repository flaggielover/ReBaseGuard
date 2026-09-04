"""Post-result assertions for P5Y Gate-2A."""
from __future__ import annotations
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"
CAP = 0.10


def load(n): return json.loads((R / n).read_text())


def test_grid_executed_is_exactly_the_frozen_grid():
    d = load("sr_precision.json")
    assert set(d["cells"]) == {f"{deg}@{b}" for deg in (8, 10) for b in (192, 256, 384, 512)}
    assert d["frozen"]["precisions"] == [256, 384, 512]
    assert d["frozen"]["degrees"] == [8, 10]
    assert not any("12@" in k for k in d["cells"]), "degree 12 is prohibited"


def test_panel_geometry_identical_across_every_precision():
    d = load("sr_precision.json")
    for deg in (8, 10):
        nz = {d["cells"][f"{deg}@{b}"]["n_z"] for b in (192, 256, 384, 512)}
        hz = {d["cells"][f"{deg}@{b}"]["h_z"] for b in (192, 256, 384, 512)}
        assert len(nz) == 1 and len(hz) == 1, f"geometry moved with precision at degree {deg}"


def test_safety_target_was_not_weakened():
    d = load("sr_precision.json")
    assert d["frozen"]["P2_safety_target"] == 1e-8
    for c in d["cells"].values():
        g = c["gates"]
        assert g["P2_pass"] == (g["P2_relative_half_width"] <= 1e-8)


def test_selection_is_lowest_qualifying_precision_for_degree8():
    d = load("sr_precision.json")
    sel = d["selected_precision_degree8"]
    for b in (256, 384, 512):
        q = d["cells"][f"8@{b}"]["qualifies"]
        if b < sel:
            assert not q, f"a lower precision {b} qualified but was not selected"
        if b == sel:
            assert q
    assert d["GATE2A_DECISION"] == f"SR_PRECISION_PASS_{sel}"


def test_every_inherited_gate_passes_with_nonzero_margin_at_selection():
    d = load("sr_precision.json")
    g = d["cells"][f"8@{d['selected_precision_degree8']}"]["gates"]
    assert g["P1_pass"] and g["P1_margin_relative"] > 0
    assert g["P3_pass"] and g["P3_margin_orders"] > 0
    assert g["P2_pass"] and g["P2_margin_factor"] > 1.0
    for k in ("T1_enclosure_contains_point_evals", "T2_remainder_monotone_in_H",
              "T3_split_exhaustive", "T5_moment_decay", "T6_exact_rational_e",
              "T7_uses_log1pA_not_logA"):
        assert g[k] is True


def test_p1_margin_is_precision_independent_confirming_gate1_defect():
    d = load("sr_precision.json")
    for deg in (8, 10):
        m = [d["cells"][f"{deg}@{b}"]["gates"]["P1_margin_relative"] for b in (256, 384, 512)]
        assert max(m) - min(m) < 1e-18, "P1 margin moved with precision"
        assert 0 < m[0] < 1e-14, "P1 margin should be nonzero but microscopic"


def test_interval_radii_are_monotone_and_contract():
    d = load("sr_precision.json")
    for deg in ("8", "10"):
        diag = d["diagnosis"][deg]
        assert diag["radius_monotone_in_precision"] is True
        assert diag["radius_contracts"] is True


def test_failure_class_is_precision_insufficient_not_mathematical():
    d = load("sr_precision.json")
    for deg in ("8", "10"):
        assert d["diagnosis"][deg]["classification"] == "PRECISION_INSUFFICIENT"


def test_diagnosis_used_radii_not_midpoints():
    d = load("sr_precision.json")
    for deg in ("8", "10"):
        assert "radius_by_precision" in d["diagnosis"][deg]
        assert all(isinstance(r[1], float) for r in d["diagnosis"][deg]["radius_by_precision"])


def test_reproducibility_ball_identical():
    d = load("sr_precision.json")
    r = d["reproducibility"]
    assert r["ball_identical"] is True
    assert r["cell"] == "degree 8 @ 384 bits"


def test_degree10_replacement_met_every_frozen_condition():
    d = load("sr_precision.json")
    rep = d["degree10_replacement"]
    if rep["eligible"]:
        assert rep["a_P2_target"] and rep["b_all_gates"] and rep["c_margins_not_worse"]
        assert rep["cost_ratio_10_over_8"] <= 0.80, "must be >=20% cheaper"
        assert d["recommended_backend"] == "DEGREE10_CONTINUOUS"
    else:
        assert d["recommended_backend"] == "DEGREE8_CONTINUOUS"


def test_degree10_margins_are_genuinely_not_worse():
    d = load("sr_precision.json")
    if not d["degree10_replacement"]["eligible"]:
        return
    sel = d["selected_precision_degree8"]
    g8 = d["cells"][f"8@{sel}"]["gates"]
    g10 = d["cells"][f"10@{d['degree10_replacement']['degree10_min_safe_precision']}"]["gates"]
    assert g10["P2_relative_half_width"] <= g8["P2_relative_half_width"]
    assert g10["P2_floor_precision_independent"] <= g8["P2_floor_precision_independent"]


def test_cost_model_carries_forward_the_measured_multiplier():
    c = load("cost_model_2a.json")
    assert c["m_sharing_multiplier"] == 24.5
    assert c["feasibility_ceiling"] == 30000


def test_measured_precision_scaling_is_mild():
    c = load("cost_model_2a.json")
    for deg in ("8", "10"):
        assert c["measured_precision_scaling_t_panel_relative_to_192bits"][deg]["512"] < 2.0


def test_cpu_cap_respected():
    d = load("sr_precision.json")
    assert d["runtime"]["cpu_hours"] <= CAP
    assert d["runtime"]["within_cap"] is True


def test_no_production_artifact_created():
    for n in ("sr_precision.json", "cost_model_2a.json"):
        assert load(n)["binding"] is False
    names = {p.name for p in R.iterdir()}
    assert names <= {"sr_precision.json", "cost_model_2a.json"}, f"unexpected artifacts: {names}"


def test_out_of_scope_work_absent_from_results():
    d = json.dumps(load("sr_precision.json")).lower()
    for banned in ("s_min", "second_moment", "lean", "full_cover", "h3a"):
        assert banned not in d


def test_temporal_anchor_contains_no_results():
    log = subprocess.run(["git", "log", "--format=%H %s", "-10"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    anchors = [l.split()[0] for l in log if "Gate-2A T0/T1" in l]
    assert anchors, "no Gate-2A anchor commit"
    tree = subprocess.run(["git", "ls-tree", "-r", anchors[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2a_sr_precision/results/" not in tree


def test_p5_p5x_and_gate1_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip()
           and not x.startswith("level4/closure_proofs/p5y_micropilot_gate1/")
           and not x.startswith("level4/closure_proofs/p5y_gate2a_sr_precision/")]
    assert not bad, f"protected paths modified: {bad}"
