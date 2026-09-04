"""Post-result assertions for P5Y Gate-2C-bis."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n="m2b_assembly.json"): return json.loads((R / n).read_text())


def test_representation_guard_passed_statically_and_at_runtime():
    d = load(); g = d["complexity_guard"]
    assert g["PASS"] is True
    assert g["max_bidegree"] == 12 and d["runtime_max_bidegree"] == 12
    assert g["complexity_score_m2_increment"] <= g["budget"]
    assert d["runtime_complexity_score"] == g["complexity_score_m2_increment"], \
        "the static precheck must predict the runtime score exactly"


def test_every_runtime_kernel_argument_was_degree_12():
    for k in load()["runtime_kernel_log"]:
        assert k["deg_p"] <= 12 and k["deg_m"] <= 12


def test_guard_would_have_caught_the_gate2c_defect():
    g = load()["complexity_guard"]
    assert g["gate2c_defective_path_score"] > g["budget"]
    assert g["gate2c_would_have_been_rejected_by"] > 10


def test_candidate_residual_does_not_dominate():
    a = load()["assembly"]
    assert a["candidate_residual_share_PASS"] is True
    assert a["candidate_residual_share"] <= 0.50
    assert a["candidate_residual_share"] < 0.05, "recorded: it is far from dominant"


def test_candidate_degree_is_12_and_was_not_raised():
    d = load()
    assert d["frozen"]["candidate_degree"] == 12
    man = json.loads((HERE / "GATE2CBIS_SOURCE_MANIFEST.json").read_text())
    now = hashlib.sha256((HERE / "m2b_certifier.py").read_bytes()).hexdigest()
    assert now == man["files"]["m2b_certifier.py"], "certifier mutated after T1"


def test_exact_candidate_inclusion_holds():
    e = load()["exact_candidate_inclusion"]
    assert e["all_included"] is True and len(e["points"]) == 5


def test_assembly_formula_and_m1_consistency():
    d = load()
    assert d["assembly"]["formula_m2"] == "R_2 = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]"
    assert d["m1_vs_gate1"]["overlaps"] is True


def test_correspondence_passed_under_the_frozen_rule():
    c = load()["correspondence"]
    assert c["enclosure_intersects_ci"] is True
    assert c["centre_within_tolerance"] is True and c["PASS"] is True
    assert c["tolerance"] == max(4 * c["mc_se"], 5e-3), "tolerance not weakened"


def test_monte_carlo_is_the_frozen_design():
    m = load()["monte_carlo"]
    assert m["n_cycles"] == 1_000_000 and m["seed"] == 20260904


def test_sharing_unchanged_and_no_duplicate_solve():
    s = load()["sharing"]
    assert s["m1_unique_resolvent_solves"] == 2
    assert s["m2_additional_resolvent_solves"] == 2
    assert s["shared_resolvent_fraction"] == 0.5
    assert s["duplicate_m1_solve_created"] is False
    assert s["hhat1_is_source_not_resolvent"] is True
    assert s["new_solve_architecture_required"] is False


def test_cost_ratios_and_class_are_mechanical():
    c = load()["cost"]
    assert abs(c["ratio_incremental"] - c["T_incr_seconds"] / c["T_m1_seconds"]) < 1e-12
    assert abs(c["ratio_cold"] - (1 + c["ratio_incremental"])) < 1e-12
    assert abs(c["ratio_per_unit_used_by_production_model"] - c["ratio_incremental"] / 2) < 1e-12
    r = c["ratio_incremental"]
    exp = ("STRONG" if r <= 1.15 else "MODERATE" if r <= 1.50
           else "WEAK" if r <= 2.00 else "HIGH")
    assert c["cost_class_on_ratio_incremental"] == exp


def test_cost_bands_are_non_degenerate_with_named_assumptions():
    b = load("cost_model_2cbis.json")["bands"]
    vals = [b[k]["cpu_hours"] for k in ("optimistic", "central", "conservative", "worst")]
    assert vals == sorted(vals) and len(set(round(v) for v in vals)) == 4, \
        "the Gate-2B optimistic==central defect must be repaired"
    for k, v in b.items():
        assert v["named_assumptions"], f"band {k} has no named assumption"
    txt = json.dumps(b)
    assert "1.5x" not in txt and "2.0x" not in txt


def test_cap_respected_and_watchdog_used():
    r = load()["runtime"]
    assert r["cap_cpu_seconds"] == 1260 and r["within_cap"] is True
    assert r["cpu_seconds"] < 1260


def test_no_second_moment_no_sr_no_cover_executed():
    d = load()
    assert d["second_moment_object_created"] is False
    assert d["sr_executed"] is False and d["cover_executed"] is False
    assert d["degree121_in_kernel_path"] is False


def test_gate2c_failure_still_recorded_as_incomplete():
    p = ROOT / "level4/closure_proofs/p5y_gate2c_m2_assembly/results/m2_assembly_abort.json"
    assert json.loads(p.read_text())["GATE2C_DECISION"] == "M2_ASSEMBLY_INCOMPLETE_EXTERNAL"


def test_decision_is_mechanical():
    d = load()
    rep = (d["complexity_guard"]["PASS"] and d["runtime_max_bidegree"] <= 12
           and d["assembly"]["candidate_residual_share_PASS"]
           and d["sharing"]["new_solve_architecture_required"] is False)
    corr = d["correspondence"]["PASS"]
    r = d["cost"]["ratio_incremental"]
    exp = ("M2_ASSEMBLY_B_FAIL_REPRESENTATION" if not rep else
           "M2_ASSEMBLY_B_FAIL_CORRESPONDENCE" if not corr else
           "M2_ASSEMBLY_B_PASS_COST_HIGH" if r > 2.0 else "M2_ASSEMBLY_B_PASS")
    assert d["GATE2CBIS_DECISION"] == exp


def test_anchor_contained_no_results_and_tree_untouched():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2C-bis T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2cbis_m2_assembly_b/results/" not in tree
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad, f"protected paths modified: {bad}"
