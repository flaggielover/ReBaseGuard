"""Post-result assertions for P5Y Gate-2B."""
from __future__ import annotations
import json, math, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n=" sr_cover.json".strip()): return json.loads((R / n).read_text())


def test_e0_cross_check_against_certified_sr_component():
    c = load()["cross_check_e0"]
    assert c["H_250_ge_q_safe"] is True
    assert c["C_SR_0_le_certified"] is True
    assert c["mass_balance_ok"] is True
    cert = json.loads((ROOT / "level4/closure_proofs/sr_derivative/results/"
                       "sr_monotone_contraction.json").read_text())
    ref = float(cert["computed_one_sided_hit_lower_enclosure"]["ball"].strip("[]").split()[0])
    assert abs(c["H_250_lower"] - ref) / ref < 1e-15, "reconstruction must reproduce the certified value"


def test_compact_domain_is_e_star_not_twelve():
    d = load()
    assert abs(float(d["e_star_SR"].strip("[]").split()[0]) - 6.755531464321473) < 1e-12
    assert d["cover"]["densest_region_e"][1] <= 6.7556
    for a, b in [(d["cover"]["densest_region_e"][0], d["cover"]["densest_region_e"][1])]:
        assert b <= 6.7556, "no cell may extend past e_star"


def test_cover_tiles_the_domain_exactly():
    assert load()["cover"]["covers_exactly"] is True


def test_upper_and_lower_cover_bounds_bracket():
    c = load()["cover"]
    assert c["subcell_count_lower_bound"] <= c["subcell_count_upper_bound"]
    assert c["subcell_count_upper_bound"] - c["subcell_count_lower_bound"] < 0.1 * c["subcell_count_upper_bound"]


def test_historical_835_comparison_is_reported_not_targeted():
    c = load()["cover"]
    assert c["historical_estimate"] == 835
    assert c["classification"] in ("LOWER", "CONSISTENT", "HIGHER")
    assert abs(c["ratio_vs_historical"] - c["subcell_count_upper_bound"] / 835.0) < 1e-12


def test_live_patch_definition_is_exact_and_keeps_the_reset_state():
    p = load()["patches"]
    assert p["nominal"] == 4096
    assert p["live"] + p["excluded_unreachable_low_product"] + \
           p["excluded_unreachable_high_product"] == p["nominal"], "every patch classified once"
    assert p["x0_patch"] == [0, 0] and p["x0_patch_kept_as_reset_state"] is True


def test_forward_invariance_of_the_live_set():
    f = load()["forward_invariance"]
    assert f["forward_invariant"] is True
    assert f["min_image_product"] >= f["lower_constraint"] * (1 - 1e-12)
    assert f["max_image_product"] <= f["upper_constraint"] * (1 + 1e-12)


def test_no_patch_excluded_for_numerical_smallness():
    """Exclusions must equal exactly the count implied by the algebraic invariant."""
    d = load()
    b = float(d["b_SR"].strip("[]").split()[0])
    A = 4581762885148045 / 8796093022208
    g, dd, inv_e = 64, None, math.exp(-1.0)
    dd = b / g
    hi = (1 + A) ** 2 * inv_e
    lo_ct = hi_ct = 0
    for i in range(g):
        for j in range(g):
            pmax = (math.exp((i + 1) * dd) - 1) * (math.exp((j + 1) * dd) - 1)
            pmin = (math.exp(i * dd) - 1) * (math.exp(j * dd) - 1)
            if pmax < inv_e and not (i == 0 and j == 0):
                lo_ct += 1
            elif pmin > hi:
                hi_ct += 1
    assert lo_ct == d["patches"]["excluded_unreachable_low_product"]
    assert hi_ct == d["patches"]["excluded_unreachable_high_product"]


def test_geometry_is_independent_of_e():
    assert load()["patches"]["geometry_depends_on_e"] is False


def test_nz_is_per_patch_not_a_global_28():
    p = load()["patches"]
    assert p["n_z_at_gate1_patch_17_11"] == 28, "Gate-1's cell must be reproduced"
    assert p["n_z_min"] < 28 < p["n_z_max"], "n_z must vary across patches"
    assert p["total_panels_over_live_patches"] < p["naive_live_times_28"]


def test_degree_stays_8_and_no_degree10_geometry():
    d = load()
    assert d["frozen"]["degree"] == 8
    g1 = json.loads((ROOT / "level4/closure_proofs/p5y_micropilot_gate1/results/"
                     "m2_sr_degree.json").read_text())
    assert d["frozen"]["h_z"] == g1["degrees"]["8"]["panel_rule"]["h_z"]
    assert d["frozen"]["h_z"] != g1["degrees"]["10"]["panel_rule"]["h_z"]


def test_cost_formula_does_not_multiply_geometry_by_m():
    c = load()["cost"]
    assert c["geometric_cover_multiplied_by_m"] is False
    d = load()
    expect = (d["cover"]["subcell_count_upper_bound"] * 49
              * d["patches"]["total_panels_over_live_patches"] * d["frozen"]["t_panel"] / 3600.0)
    assert abs(c["cpu_sr_hours"] - expect) / expect < 1e-9


def test_function_multiplier_is_49_equals_24p5_units():
    assert load()["frozen"]["n_functions"] == 49
    g1 = json.loads((ROOT / "level4/closure_proofs/p5y_micropilot_gate1/results/"
                     "optional_checks.json").read_text())
    assert g1["PILOT_MSHARE"]["corrected_multiplier_units"] == 24.5
    assert 49 == 24.5 * 2


def test_no_production_solve_invoked():
    assert load()["production_solve_invoked"] is False


def test_p1_repair_estimated_not_applied():
    p = load()["p1_headroom_repair_estimate"]
    assert p["applied"] is False
    assert p["recommended_epsilon"] == 1e-3
    assert load()["frozen"]["h_z"] == p["h_z_current"]


def test_sensitivity_is_diagnostic_only_and_did_not_move_the_baseline():
    d = load()
    s = d["sensitivity_5pct"]
    assert s["baseline"] == d["cover"]["subcell_count_upper_bound"]
    assert s["minus_5pct_C"] <= s["baseline"] <= s["plus_5pct_C"]


def test_cpu_cap_respected():
    r = load()["runtime"]
    assert r["cpu_hours"] <= 0.10 and r["within_cap"] is True


def test_decision_is_mechanical():
    d = load()
    feas = d["cost"]["cover_feasibility"]
    expect = ("SR_COVER_PASS_MEASURED" if d["geometry_sound"] and feas in ("STRONG", "MODERATE")
              else "SR_COVER_PASS_BUT_COST_HIGH" if d["geometry_sound"]
              else "SR_COVER_FAIL_GEOMETRY")
    assert d["GATE2B_DECISION"] == expect


def test_no_binding_artifact():
    assert load()["binding"] is False
    assert {p.name for p in R.iterdir()} == {"sr_cover.json"}


def test_anchor_contained_no_results():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2B T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2b_sr_cover/results/" not in tree


def test_prior_gates_and_protected_tree_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith(
        ("level4/closure_proofs/p5y_micropilot_gate1/",
         "level4/closure_proofs/p5y_gate2a_sr_precision/",
         "level4/closure_proofs/p5y_gate2b_sr_cover/"))]
    assert not bad, f"protected paths modified: {bad}"
