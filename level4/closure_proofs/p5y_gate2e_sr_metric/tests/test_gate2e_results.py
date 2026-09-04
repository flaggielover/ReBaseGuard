"""Post-result assertions for P5Y Gate-2E."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n="sr_metric.json"): return json.loads((R / n).read_text())


def test_gate2d_not_rewritten():
    g = json.loads((ROOT / "level4/closure_proofs/p5y_gate2d_sr_realcandidate/results/"
                    "gate2d_adjudication.json").read_text())
    assert g["governing_decision"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"
    assert load()["gate2d_remains"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"


def test_metric_is_absolute_and_proposition_derived():
    m = load()["metric"]
    assert m["type"] == "ABSOLUTE" and m["scientific_target"] == "R_MAX_LT_2"
    assert m["boundary"] == 2.0 and m["w_target"] == 0.2
    assert m["derivation_inputs_all_predate_gate2d"] is True
    assert m["scale_aware_fallback_invoked"] is False


def test_budget_ledger_sums_within_target_with_reserve():
    m = load()["metric"]
    assert abs(sum(m["ledger_absolute"].values()) - 0.19) < 1e-12
    assert abs(m["reserve_fraction"] - 0.05) < 1e-12
    assert sum(m["ledger_absolute"].values()) <= m["w_target"]
    assert abs(m["local_gate_budget"] - 0.100) < 1e-12


def test_candidate_budget_and_panel_budget_match_the_derivation():
    m = load()["metric"]
    assert abs(m["delta_candidate_max"]
               - 2 * m["ledger_absolute"]["B_candidate"]
               / (m["C_SR_quarter"] * m["E_abs_raw"])) < 1e-15
    assert abs(m["w_panel_max"]
               - m["local_gate_budget"] / (0.5 * m["C_SR_quarter"] * m["n_panels"])) < 1e-15


def test_amplification_direction_audit_passed():
    a = load()["direction_audit"]
    assert a["type"] == "UPPER" and a["PASS"] is True
    assert a["cross_check_le_certified"] is True
    assert a["monotone_decreasing_in_e"] is True


def test_execution_order_was_enforced():
    s = load()["stages_run"]
    assert s == ["direction_audit", "acceptance_precondition",
                 "representation_guard", "precision_grid"]


def test_candidate_identical_to_gate2d_not_refitted():
    c = load()["candidate_identity_vs_gate2d"]
    assert c["identical"] is True and c["refitted"] is False
    assert c["gate2d_eps_cand"] == c["this_gate_eps_cand"]


def test_acceptance_precondition_passed_by_a_wide_margin():
    a = load()["acceptance_precondition"]
    assert a["PASS"] is True
    assert a["ratio"] < 1e-3, "the candidate should be far inside its budget"


def test_all_objects_pass_the_absolute_budget():
    d = load()
    for name, cells in d["cells"].items():
        for c in cells:
            assert c["ABS_PASS"] is True, f"{name}@{c['bits']} failed the absolute metric"
            assert c["budget_ratio"] < 1.0


def test_old_relative_P2_did_not_decide_anything():
    d = load()
    h1 = d["cells"]["hhat_1"][0]
    assert h1["P2_old_DIAGNOSTIC_ONLY"] > 1e-8, "the old metric would have failed this"
    assert h1["ABS_PASS"] is True, "yet the proposition-derived metric passes it"


def test_gate2d_root_cause_confirmed_absolutely():
    a = load()["absolute_vs_relative_demonstration"]
    assert 0.1 < a["absolute_ratio_h1_over_unit"] < 10, \
        "the two candidates must be within an order of magnitude in ABSOLUTE terms"
    assert a["relative_P2_ratio_h1_over_unit"] > 1e6, \
        "while the relative metric separates them by orders of magnitude"


def test_error_decomposition_shows_approximation_limited():
    c = load()["cells"]["hhat_1"][0]
    assert c["share_candidate"] > 0.9
    assert c["share_interval"] < 1e-30, "Arb precision is not the limit"
    assert abs(c["share_candidate"] + c["share_kernel"] + c["share_interval"] - 1.0) < 1e-9


def test_failure_is_the_P1_knife_edge_not_the_candidate():
    d = load(); adj = load("gate2e_adjudication.json")
    assert d["GATE2E_DECISION"] == "SR_METRIC_FAIL_CANDIDATE"
    assert adj["failure_class"] == "IMPLEMENTATION_DEFECT"
    k = adj["the_P1_knife_edge_third_occurrence"]
    assert 0 < k["overshoot_relative"] < 1e-14, "a floating-point knife edge, not a real miss"
    for c in d["cells"]["hhat_1"]:
        assert c["P1_repaired_pass"] is False and c["ABS_PASS"] is True


def test_decision_was_not_reinterpreted_after_results():
    adj = load("gate2e_adjudication.json")
    assert adj["decision_is_mechanical_and_not_reinterpreted"] is True
    assert adj["decision_stands"] == load()["GATE2E_DECISION"]
    assert "no frozen rule maps" in adj["the_name_understates_the_cause"][
        "why_not_adjudicated_to_another_name"].lower().replace("no frozen rule maps", "no frozen rule maps")


def test_no_post_T2_mutation():
    man = json.loads((HERE / "GATE2E_SOURCE_MANIFEST.json").read_text())
    for f in ("sr_metric.py", "GATE2E_PREREGISTRATION.md"):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == man["files"][f]


def test_p1_repair_panel_count_unchanged():
    p = load()["p1_repair"]
    assert p["n_z"] == 28 and p["panel_count_unchanged"] is True


def test_representation_guard_passed():
    g = load()["representation_guard"]
    assert g["PASS"] is True and g["max_bidegree"] == 16
    assert g["score_per_composition"] <= g["budget"]


def test_cap_respected_and_no_out_of_scope_artifacts():
    rt = load()["runtime"]
    assert rt["within_cap"] is True and rt["cpu_seconds"] < 540
    assert {p.name for p in R.iterdir()} == {"sr_metric.json", "gate2e_adjudication.json"}


def test_prior_gates_intact():
    for p, key, val in (
        ("p5y_gate2a_sr_precision/results/sr_precision.json", "GATE2A_DECISION", "SR_PRECISION_PASS_256"),
        ("p5y_gate2b_sr_cover/results/sr_cover.json", "GATE2B_DECISION", "SR_COVER_PASS_MEASURED"),
        ("p5y_gate2cbis_m2_assembly_b/results/m2b_assembly.json", "GATE2CBIS_DECISION", "M2_ASSEMBLY_B_PASS")):
        assert json.loads((ROOT / "level4/closure_proofs" / p).read_text())[key] == val


def test_anchor_had_no_results_and_tree_untouched():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2E T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2e_sr_metric/results/" not in tree
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad
