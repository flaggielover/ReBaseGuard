"""P4ZB locks: scope, expansion identities, ladder freeze, closure conservation."""
import hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import pytest

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent/"p4_theory_generalization"
P4Z = NS.parent/"p4z_location_family_feasibility"
P4ZA = NS.parent/"p4za_fullscope_closure"
sys.path.insert(0, str(NS/"production"))
import p4zb_hash as sh  # noqa: E402

AUD = json.loads((NS/"results"/"p4zb_starting_audit.json").read_text())
PLAN = json.loads((NS/"production"/"p4zb_campaign_plan.json").read_text())
PROT = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
STUDY = json.loads((NS/"results"/"ladder_study.json").read_text())


def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


# --- scope lock --------------------------------------------------------------

def test_scope_is_exactly_the_four_open_cells():
    s = PLAN["scope_lock"]
    assert s["configuration"] == "frozen/cusum@5/skewnormal4"
    assert s["m"] == [1,2,3,5] and s["cells"] == 4
    assert AUD["reconciliation"]["open_cells"] == 4
    assert AUD["reconciliation"]["open_configuration"] == s["configuration"]


def test_no_configuration_outside_the_scope_lock_was_run():
    d = NS/"production"/"blocks"
    if not d.exists(): pytest.skip("no blocks yet")
    assert {p.name for p in d.iterdir()} <= {"frozen__cusum_at_5__skewnormal4"}


def test_the_other_92_cells_were_not_rerun():
    assert PLAN["scope_lock"]["cells_not_rerun"] == 92
    cov = NS/"results"/"final_coverage.json"
    if not cov.exists(): pytest.skip("coverage not built")
    c = json.loads(cov.read_text())
    assert c["authoritative_sources"].get("P4Z",0) + c["authoritative_sources"].get("P4ZA",0) == 92
    assert c["authoritative_sources"].get("P4ZB",0) == 4


# --- finite-difference identities -------------------------------------------

def test_central_difference_has_only_even_powers():
    """An even function differences to exactly zero; odd powers cannot survive."""
    even = lambda e: 3.0 + 4.0*e**2 + 5.0*e**4 + 6.0*e**6
    for h in (0.1, 0.05, 0.025):
        assert even(h) - even(-h) == pytest.approx(0.0, abs=1e-13)


def test_richardson_cancels_h2_leaving_minus_four_b_h4():
    G,a,b = 3.0, 1.5, -0.75
    D = lambda h: G + a*h*h + b*h**4
    for h in (0.05, 0.025, 0.0125):
        assert (4*D(h)-D(2*h))/3.0 == pytest.approx(G - 4*b*h**4, rel=1e-12)


def test_order_below_two_requires_opposite_signs():
    """p = log2[4(a+5b h^2)/(a+1.25 b h^2)]; p<2 iff b/a<0."""
    def p(a,b,h): return math.log2(4*(a+5*b*h*h)/(a+1.25*b*h*h))
    h = 0.05
    assert p(200.0, -6000.0, h) < 2.0        # opposite signs -> below 2
    assert p(200.0, +6000.0, h) > 2.0        # same signs     -> above 2
    assert p(200.0, 0.0, h) == pytest.approx(2.0, rel=1e-12)


def test_the_measured_coefficient_ratio_is_negative_on_every_m():
    for c in AUD["cells"]:
        assert c["three_point_fit"]["b_over_a"] < 0, c["m"]


def test_the_predicted_order_reproduces_the_observed_order():
    for c in AUD["cells"]:
        f = c["three_point_fit"]; a,b = f["a"], f["b"]; h = 0.05
        p_pred = math.log2(4*(a+5*b*h*h)/(a+1.25*b*h*h))
        assert p_pred == pytest.approx(c["p4za_empirical_order_p"], abs=5e-3), c["m"]


def test_adjacent_richardson_pairs_differ_by_fifteen_times_the_residual():
    G,a,b = 3.0, 1.5, -0.75
    D = lambda h: G + a*h*h + b*h**4
    h = 0.025
    R_fine = (4*D(h)-D(2*h))/3.0
    R_coarse = (4*D(2*h)-D(4*h))/3.0
    assert (R_coarse - R_fine) == pytest.approx(15*(R_fine-G), rel=1e-10)


def test_the_finer_neighbour_estimates_the_residual_almost_exactly():
    """|R(2h,h) - R(h,h/2)| = (15/16) * |residual of R(2h,h)|."""
    G,a,b = 3.0, 1.5, -0.75
    D = lambda h: G + a*h*h + b*h**4
    h = 0.025
    R_frozen = (4*D(h)-D(2*h))/3.0
    R_finer  = (4*D(h/2)-D(h))/3.0
    assert abs(R_frozen-R_finer) == pytest.approx(0.9375*abs(R_frozen-G), rel=1e-9)


# --- ladder freeze and its justification ------------------------------------

def test_the_ladder_is_frozen_and_justified_by_measurement():
    L = PLAN["fd_ladder"]
    assert L["rungs"] == [0.1, 0.05, 0.025, 0.0125]
    assert L["frozen_scientific_pair"] == PROT["fd_steps"] == [0.05, 0.025]
    assert "Route B remains the frozen per-batch Richardson" in L["estimator_unchanged"]
    assert "no divisor" in L["truncation_rule"]
    assert L["model_dependence"].startswith("NONE")
    assert "SNR" in L["noise_is_conservative"] or "noise" in L["noise_is_conservative"].lower()


def test_the_excluded_rung_is_excluded_on_measured_noise():
    """0.00625 was in the study and is excluded from the frozen ladder."""
    assert 0.00625 in STUDY["ladder"]
    assert 0.00625 not in PLAN["fd_ladder"]["rungs"]
    for m in ("1","2","3","5"):
        snr = STUDY["by_m"][m]["paired_differences"]["0.0125-0.00625"]["snr"]
        assert snr < 1.0, (m, snr)


def test_the_h4_model_was_validated_out_of_sample():
    for m in ("1","2","3","5"):
        t = STUDY["by_m"][m]["prediction_test"]
        assert t["D_0.0125_error_in_se"] < 3.0, (m, t["D_0.0125_error_in_se"])


def test_every_ladder_block_uses_the_frozen_rungs():
    want = {f"{h:g}" for h in PLAN["fd_ladder"]["rungs"]}
    n = 0
    for p in (NS/"production"/"blocks").rglob("fd_ladder_*.json"):
        assert set(json.loads(p.read_text())["central_difference_by_h"]) == want
        n += 1
    if n == 0: pytest.skip("no ladder blocks yet")


# --- thresholds --------------------------------------------------------------

def test_the_k7_limit_is_unchanged():
    assert PLAN["thresholds"]["fd_ladder_relative_max"] == 0.02
    assert AUD["frozen_inputs_unchanged"]["k7_limit"] == 0.02


def test_no_threshold_drift():
    t = PLAN["thresholds"]
    assert t["relative"] == PROT["gates"]["correspondence_relative_limit"] == 0.03
    assert t["z"] == PROT["gates"]["correspondence_z_limit"] == 4.0
    assert abs(1.96*math.sqrt(2)*t["r_star"] - 0.03) < 1e-8
    assert t["any_threshold_changed_by_p4zb"] is False


# --- producer, seeds, caps ---------------------------------------------------

def test_seeds_are_disjoint_from_every_prior_campaign():
    cfg = PLAN["configuration"]
    seeds = {cfg["seed_rb_score"], cfg["seed_rb_map"], cfg["seed_fd_ladder"]}
    assert len(seeds) == 3
    for src in (P4Z/"production"/"campaign_plan.json", P4ZA/"production"/"p4za_campaign_plan.json"):
        prior = {s for c in json.loads(src.read_text())["configurations"]
                 for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
        assert not seeds & prior
    assert STUDY["seed"] not in seeds
    assert not seeds & set(PROT["master_seeds"].values())


def test_head_excluded_from_producer_hash_and_tcb_holds_producers_only():
    m = sh.build_manifest()
    assert "head_informational" in m and "head" not in m
    sh.verify_manifest(dict(m, head_informational="0"*40))
    assert any(p.endswith("run_p4zb.py") for p in sh.TCB_PATHS)
    assert any(p.endswith("p4zb_campaign_plan.json") for p in sh.TCB_PATHS)
    for reader in ("adjudicate_p4zb.py","replay_p4zb.py","build_final_coverage.py",
                   "independent_closure_audit.py","build_p4zb_closure.py"):
        assert not any(p.endswith(reader) for p in sh.TCB_PATHS), reader


def test_block_and_path_caps_are_fixed():
    f = PLAN["fixed_policy"]
    assert f["blocks_per_route"] == 200 and f["ladder_blocks"] == 40
    assert f["adaptive"] is False and f["top_ups_permitted"] == 0
    assert f["path_count_may_increase_during_run"] is False
    assert f["block_paths_unchanged_from_p4za"] is True


def test_cost_cap_is_not_borrowed_and_counts_calibration():
    b = PLAN["budget"]
    assert b["borrowed_from_p4za_cap"] is False
    assert b["cost_bearing_calibration_included"] is True
    assert b["total_cpu_cap_hours"] == 4.5


# --- replay and final conservation ------------------------------------------

def test_replay_is_bit_identical():
    p = NS/"production"/"replay_p4zb.json"
    if not p.exists(): pytest.skip("replay not run")
    r = json.loads(p.read_text())
    assert r["all_scientific_hashes_identical"] is True
    assert r["any_scientific_field_mismatch"] is False
    assert r["all_producer_hashes_identical"] and r["all_runtime_hashes_identical"]


def test_final_96_cell_conservation():
    p = NS/"results"/"final_coverage.json"
    if not p.exists(): pytest.skip("coverage not built")
    c = json.loads(p.read_text())
    assert c["cells_total"] == 96 and sum(c["counts"].values()) == 96
    assert c["counts"]["UNCOVERED"] == 0
    assert c["conservation"]["conserved"] and c["conservation"]["one_source_per_cell"]
    assert c["rules"]["historical_evidence_used_as_sole_authority"] is False


def test_closed_is_only_claimed_when_everything_is_clean():
    p = NS/"results"/"p4zb_successor_closure.json"
    if not p.exists(): pytest.skip("closure not built")
    d = json.loads(p.read_text())
    c = json.loads((NS/"results"/"final_coverage.json").read_text())["counts"]
    if d["verdict"] == "P4ZB_CLOSED":
        assert c == {"COVERED_PASS":96,"COVERED_FAIL":0,"INCONCLUSIVE":0,"UNCOVERED":0}
    assert d["historical_status_unchanged"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    for claim in ("historical P4 was retroactively changed to PASS",
                  "P5Y is CLOSED","K1 is CLOSED","Level-4 is CLOSED",
                  "production readiness"):
        assert claim in d["claims_explicitly_not_made"]


# --- historical immutability -------------------------------------------------

def test_the_whole_prior_lineage_is_untouched():
    assert git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization") \
        == AUD["parent_evidence"]["p4_theorem_tree"]
    assert json.loads((P4/"results"/"closure_decision.json").read_text())["verdict"] == "PARTIAL"
    for name, key in (("production/adjudication_p4za.json","p4za_adjudication_sha256"),
                      ("results/claim_coverage.json","p4za_coverage_sha256"),
                      ("results/p4za_successor_closure.json","p4za_closure_sha256"),
                      ("production/p4za_campaign_plan.json","p4za_plan_sha256")):
        assert hashlib.sha256((P4ZA/name).read_bytes()).hexdigest() \
            == AUD["parent_evidence"][key], name


def test_p4zb_touches_no_path_outside_its_namespace():
    for p in filter(None, git("diff","--name-only","p4za-fullscope-closure","HEAD").splitlines()):
        assert p.startswith("level4/closure_proofs/p4zb_skewnormal4_k7/"), p
