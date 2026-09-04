"""Post-result assertions for P5Y Gate-2F."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n="sr_metric_b.json"): return json.loads((R / n).read_text())


def test_prior_failures_remain_failures():
    d = load()
    assert d["gate2d_remains"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"
    assert d["gate2e_remains"] == "SR_METRIC_FAIL_CANDIDATE"
    e = json.loads((ROOT / "level4/closure_proofs/p5y_gate2e_sr_metric/results/"
                    "sr_metric.json").read_text())
    assert e["GATE2E_DECISION"] == "SR_METRIC_FAIL_CANDIDATE"


def test_inheritance_audit_passed():
    a = load()["inheritance_audit"]
    assert a["PASS"] is True
    assert a["checks"]["run_cell_is_gate2e_function"] is True
    assert a["thresholds_distinct"] is True


def test_metric_remains_absolute_and_unchanged():
    d = load()
    assert d["metric_type"] == "ABSOLUTE"
    a = d["inheritance_audit"]["checks"]
    for k in ("metric_type_absolute", "target_R_max_lt_2", "slack_R", "alpha",
              "w_target", "ledger", "w_panel_max", "delta_candidate_max"):
        assert a[k] is True


def test_the_only_change_is_the_p1_threshold_pair():
    c = load()["the_only_change"]
    assert c["P1_RULE_TARGET"] < c["P1_CHECK_THRESHOLD"]
    assert abs(c["eps_P1"] - 1e-3) < 1e-15
    assert c["min_headroom_rel"] == 1e-6
    assert "SAME value" in c["gate2e_behaviour"]


def test_p1_headroom_is_robust_not_a_knife_edge():
    p = load()["p1_structural"]
    assert p["thresholds_distinct"] is True and p["P1_PASS"] is True
    assert p["headroom_rel"] >= 1e-6
    assert abs(p["headroom_rel"] - 1e-3) < 1e-9
    assert p["headroom_rel"] / 1e-6 > 900


def test_negative_control_reproduces_the_gate2e_knife_edge():
    n = load()["negative_control"]
    assert n["old_symmetric"]["knife_edge"] is True
    assert n["old_symmetric"]["P1_PASS"] is False
    assert abs(n["old_symmetric"]["headroom_rel"]) < 1e-6
    assert n["new_asymmetric"]["robust"] is True and n["PASS"] is True
    assert n["new_asymmetric"]["headroom_rel"] / abs(n["old_symmetric"]["headroom_rel"]) > 1e10


def test_gate2e_symmetric_boolean_is_demonstrably_untrustworthy():
    d = load()
    here = [c["P1_PASS_gate2e_symmetric"] for c in d["cells"]["hhat_1"]]
    there = json.loads((ROOT / "level4/closure_proofs/p5y_gate2e_sr_metric/results/"
                        "sr_metric.json").read_text())
    gate2e = [c["P1_repaired_pass"] for c in there["cells"]["hhat_1"]]
    assert all(here) and not any(gate2e), \
        "the same symmetric check flips between runs -- it was never a real gate"


def test_execution_order_enforced():
    assert load()["stages_run"] == [
        "inheritance_audit", "amplification_consistency", "p1_structural",
        "candidate_precondition", "representation_guard", "precision_grid"]


def test_candidate_identical_across_2d_2e_2f():
    c = load()["candidate_identity"]
    assert c["identical_across_all_three"] is True and c["refitted"] is False


def test_all_objects_pass_the_absolute_metric_and_p1():
    for name, cells in load()["cells"].items():
        for c in cells:
            assert c["ABS_PASS"] is True and c["P1_PASS_new"] is True
            assert c["CELL_PASS"] is True and c["budget_ratio"] < 1.0


def test_absolute_metric_matches_gate2e_to_one_ulp():
    for k, v in load()["absolute_metric_unchanged_vs_gate2e"].items():
        rel = abs(v["gate2e"] - v["gate2f"]) / v["gate2e"]
        assert rel < 1e-14, f"{k} moved by {rel:.2e}, more than a rounding artefact"


def test_panel_count_unchanged():
    p = load()["p1_geometry"]
    assert p["n_z"] == 28 and p["panel_count_unchanged"] is True


def test_old_P2_did_not_decide_anything():
    h = load()["cells"]["hhat_1"][0]
    assert h["P2_old_DIAGNOSTIC_ONLY"] > 1e-8 and h["CELL_PASS"] is True


def test_lowest_passing_precision_selected():
    d = load()
    assert d["selected_safe_precision"] == 256
    assert d["GATE2F_DECISION"] == "SR_METRIC_B_PASS_256"


def test_reproducibility_passed():
    assert load()["reproducibility"]["PASS"] is True


def test_guard_and_direction_audit_passed():
    d = load()
    assert d["representation_guard"]["PASS"] is True
    assert d["direction_audit"]["PASS"] is True and d["direction_audit"]["type"] == "UPPER"


def test_failure_class_none_and_decision_mechanical():
    d = load()
    assert d["failure_class"] == "NONE"
    assert d["GATE2F_DECISION"] == f"SR_METRIC_B_PASS_{d['selected_safe_precision']}"


def test_cap_respected_and_no_post_T2_mutation():
    rt = load()["runtime"]
    assert rt["within_cap"] is True and rt["cpu_seconds"] < 180
    man = json.loads((HERE / "GATE2F_SOURCE_MANIFEST.json").read_text())
    for f in ("sr_metric_b.py", "GATE2F_PREREGISTRATION.md"):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == man["files"][f]


def test_prior_successful_gates_intact():
    for p, key, val in (
        ("p5y_gate2a_sr_precision/results/sr_precision.json", "GATE2A_DECISION", "SR_PRECISION_PASS_256"),
        ("p5y_gate2b_sr_cover/results/sr_cover.json", "GATE2B_DECISION", "SR_COVER_PASS_MEASURED"),
        ("p5y_gate2cbis_m2_assembly_b/results/m2b_assembly.json", "GATE2CBIS_DECISION", "M2_ASSEMBLY_B_PASS")):
        assert json.loads((ROOT / "level4/closure_proofs" / p).read_text())[key] == val


def test_anchor_had_no_results_and_tree_untouched():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2F T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2f_sr_metric_b/results/" not in tree
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad
