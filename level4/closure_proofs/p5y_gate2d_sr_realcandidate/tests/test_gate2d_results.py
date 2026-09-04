"""Post-result assertions for P5Y Gate-2D."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n="sr_realcandidate.json"): return json.loads((R / n).read_text())


def test_candidate_is_genuine_not_unit_candidate():
    g = load()["genuine_candidate"]
    assert g["is_unit_candidate"] is False
    assert g["represents"].startswith("h_1^SR")
    assert load()["candidate_is_unit_candidate"] is False


def test_candidate_bidegree_and_dyadic_format():
    g = load()["genuine_candidate"]
    assert g["bidegree"] == [16, 16]
    assert g["exact_dyadic_denominator_bits"] == 50
    assert g["nonzero_coefficients"] == 33, "separable: 1 + 16 + 16"


def test_residual_is_whole_domain_and_three_termed():
    g = load()["genuine_candidate"]
    assert g["fit_domain"].startswith("full state square")
    for k in ("A", "B"):
        tot, tail, interp, rnd = g["eps_detail_A_B"][k]
        assert abs(tot - (tail + interp + rnd)) < 1e-18 * max(1.0, tot)
        assert interp < 1e-25 and rnd < 1e-12


def test_complexity_guard_and_p1_repair_passed():
    d = load()
    assert d["complexity_guard"]["PASS"] is True
    assert d["complexity_guard"]["score_per_composition"] <= d["complexity_guard"]["budget"]
    assert d["p1_repair"]["PASS"] is True
    assert d["p1_repair"]["n_z"] == 28 == d["p1_repair"]["n_z_gate2a_gate2b"]
    assert d["p1_repair"]["panel_count_unchanged"] is True


def test_precision_grid_is_exactly_the_frozen_one():
    d = load()
    assert [c["bits"] for c in d["cells_genuine"]] == [256, 384, 512]
    assert d["frozen"]["precisions"] == [256, 384, 512]


def test_failure_is_not_precision_driven():
    """P2 equals its precision-independent floor at every precision."""
    cells = load()["cells_genuine"]
    # the precision-dependent part of P2 is (P2 - floor); assert it is negligible
    # AND that it shrinks with precision, which is the substantive claim.
    share = [(c["P2"] - c["P2_floor"]) / c["P2"] for c in cells]
    assert max(share) < 1e-6, f"precision contributes {max(share):.2e} of P2"
    assert share == sorted(share, reverse=True), "precision share must shrink with bits"
    rad = [c["acc_radius"] for c in cells]
    assert rad == sorted(rad, reverse=True), "radius must still contract with precision"
    assert rad[-1] < 1e-100, "radius is utterly negligible at 512 bits"


def test_conditioning_is_better_than_the_control_in_the_same_run():
    d = load()
    g = d["cells_genuine"][0]["digits_lost"]
    u = d["cells_unit_control"][0]["digits_lost"]
    assert g < u, "the genuine candidate must be compared to a same-run control"
    assert d["digit_loss"]["delta_digits_vs_gate2a"] < 0


def test_conditioning_class_severity_comes_from_the_second_clause():
    """SEVERE here means 'no safe precision', NOT delta_digits > +30."""
    d = load()
    assert d["digit_loss"]["conditioning_class"] == "SEVERE"
    assert d["digit_loss"]["delta_digits_vs_gate2a"] <= 5, \
        "on the delta_digits clause alone this would be STABLE"
    assert d["selected_safe_precision"] is None


def test_failure_class_is_candidate_residual_dominant():
    assert load()["failure_class"] == "CANDIDATE_RESIDUAL_DOMINANT"


def test_acceptance_precondition_was_measured_and_failed():
    a = load()["acceptance_precondition"]
    assert a["eps_cand_finite"] is True
    assert a["P2_target_reachable"] is False
    assert a["eps_cand_times_N0_over_acc"] > 1e-8


def test_governing_decision_is_fail_representation_per_the_frozen_rule():
    adj = load("gate2d_adjudication.json")
    assert adj["governing_decision"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"
    assert adj["artifact_field"] == "SR_REALCANDIDATE_FAIL_WITHIN_GRID"
    assert "section 7" in adj["why"]["frozen_rule"]


def test_implementation_defect_recorded_not_patched():
    adj = load("gate2d_adjudication.json")
    assert "not_patched_because" in adj["implementation_defect_recorded_not_patched"]
    man = json.loads((HERE / "GATE2D_SOURCE_MANIFEST.json").read_text())
    now = hashlib.sha256((HERE / "sr_realcandidate.py").read_bytes()).hexdigest()
    assert now == man["files"]["sr_realcandidate.py"], "module mutated after T1"


def test_root_cause_is_scale_not_separability():
    adj = load("gate2d_adjudication.json")
    ev = adj["root_cause"]["scale_evidence"]
    assert ev["unit_candidate_acc"] > 1.0 > ev["genuine_h1_acc"]
    assert ev["nonseparable_h2_probe_acc"] > ev["genuine_h1_acc"]
    d = load()
    probe = d["nonseparable_probe"]
    assert probe["decisive"] is False and probe["certifies_nothing"] is True
    assert probe["cells"][0]["P2"] > 1e-8, "the non-separable probe fails the same way"


def test_probe_never_entered_the_decision():
    d = load()
    assert d["nonseparable_probe"]["decisive"] is False
    assert d["selected_safe_precision"] is None
    assert d["GATE2D_DECISION"].startswith("SR_REALCANDIDATE_FAIL")


def test_reproducibility_ball_identical():
    r = load()["reproducibility"]
    assert r["ball_identical"] is True and r["bits"] == 384


def test_cap_respected():
    rt = load()["runtime"]
    assert rt["cap_cpu_seconds"] == 540 and rt["within_cap"] is True
    assert rt["cpu_seconds"] < 540


def test_no_out_of_scope_artifacts():
    assert load()["second_moment_object_created"] is False
    assert load()["other_patch_used"] is False
    assert {p.name for p in R.iterdir()} == {"sr_realcandidate.json", "gate2d_adjudication.json"}


def test_prior_gates_intact():
    for p, key, val in (
        ("p5y_gate2a_sr_precision/results/sr_precision.json", "GATE2A_DECISION", "SR_PRECISION_PASS_256"),
        ("p5y_gate2b_sr_cover/results/sr_cover.json", "GATE2B_DECISION", "SR_COVER_PASS_MEASURED"),
        ("p5y_gate2c_m2_assembly/results/m2_assembly_abort.json", "GATE2C_DECISION", "M2_ASSEMBLY_INCOMPLETE_EXTERNAL"),
        ("p5y_gate2cbis_m2_assembly_b/results/m2b_assembly.json", "GATE2CBIS_DECISION", "M2_ASSEMBLY_B_PASS")):
        assert json.loads((ROOT / "level4/closure_proofs" / p).read_text())[key] == val


def test_anchor_had_no_results_and_tree_untouched():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2D T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2d_sr_realcandidate/results/" not in tree
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad, f"protected paths modified: {bad}"
