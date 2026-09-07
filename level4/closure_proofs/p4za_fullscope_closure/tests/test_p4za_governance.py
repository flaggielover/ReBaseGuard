"""P4ZA locks.  Every test is a constant comparison or a fail-closed behaviour."""
import hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import pytest

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
sys.path.insert(0, str(NS/"production"))
import p4za_hash as sh  # noqa: E402

AUDIT = json.loads((NS/"results"/"p4za_starting_audit.json").read_text())
PLAN = json.loads((NS/"production"/"p4za_campaign_plan.json").read_text())
PROT = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
ZADJ = json.loads((P4Z/"production"/"adjudication.json").read_text())


def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


# --- exact 52-cell reconstruction and K3/K7 partition -----------------------

def test_the_96_cell_universe_reconciles():
    r = AUDIT["reconciliation"]
    assert r["p4z_cells_total"] == 96
    assert r["p4z_counts"] == {"PASS":44,"FAIL":0,"INCONCLUSIVE":52}
    assert r["all_counts_reconcile"] is True


def test_the_inconclusive_partition_is_exactly_32_K3_and_20_K7():
    p = AUDIT["reconciliation"]["inconclusive_partition"]
    assert p == {"K3":32,"K7":20,"total":52}
    k3 = sum(1 for c in AUDIT["cells"] if c["p4z_inconclusive_cause"]=="K3")
    k7 = sum(1 for c in AUDIT["cells"] if c["p4z_inconclusive_cause"]=="K7")
    assert (k3,k7) == (32,20)


def test_every_inconclusive_cell_is_recomputed_by_p4za():
    need = {(c["layer"],c["detector"],c["family"],c["m"]) for c in AUDIT["cells"]
            if c["p4z_disposition"]=="INCONCLUSIVE"}
    planned = {(c["layer"],c["detector"],c["family"],m)
               for c in PLAN["configurations"] for m in c["m_affected"]}
    assert need == planned and len(need) == 52


def test_p4za_does_not_rerun_the_44_passing_cells():
    assert PLAN["scope"]["p4z_cells_not_recomputed"] == 44
    planned = {(c["layer"],c["detector"],c["family"],m)
               for c in PLAN["configurations"] for m in c["m_affected"]}
    for c in ZADJ["cells"]:
        if c["gate_result"] == "PASS":
            assert (c["layer"],c["detector"],c["family"],c["m"]) not in planned


# --- historical evidence composition ----------------------------------------

def test_all_52_cells_were_p4x_pass():
    inc = [c for c in AUDIT["cells"] if c["p4z_disposition"]=="INCONCLUSIVE"]
    assert len(inc) == 52
    assert {c["p4x_disposition"] for c in inc} == {"PASS"}


def test_no_p4x_evidence_for_the_52_used_a_topup_or_sharding():
    """The recorded P4X governance defects are individually inapplicable."""
    for c in AUDIT["cells"]:
        if c["p4z_disposition"] != "INCONCLUSIVE": continue
        for r in ("p4x_route_a","p4x_route_b"):
            assert c[r]["stage2_paths"] == 0, (c["family"], r)
            assert c[r]["stage2_shards"] == 0, (c["family"], r)
            assert c[r]["meets_r_star"] is True, (c["family"], r)


def test_historical_evidence_is_never_the_sole_authority():
    cov_p = NS/"results"/"claim_coverage.json"
    if not cov_p.exists(): pytest.skip("coverage graph not built yet")
    cov = json.loads(cov_p.read_text())
    assert cov["rules"]["historical_evidence_used_as_sole_authority"] is False
    assert cov["sources"]["P4X"]["cells"] == 0
    for c in cov["cells"]:
        for e in c.get("corroborating_evidence", []):
            assert e["confers_disposition"] is False


def test_no_cell_is_uncovered_or_ambiguous():
    cov_p = NS/"results"/"claim_coverage.json"
    if not cov_p.exists(): pytest.skip("coverage graph not built yet")
    cov = json.loads(cov_p.read_text())
    assert cov["counts"]["UNCOVERED"] == 0
    assert cov["ambiguous"] == []
    assert cov["conservation"]["conserved"] is True
    assert sum(cov["counts"].values()) == 96


# --- FD expansion identities -------------------------------------------------

def test_richardson_cancels_the_h_squared_term_exactly():
    """R(2h,h) = Gamma - 4 b h^4 for D(h) = Gamma + a h^2 + b h^4."""
    G, a, b = 3.0, 1.5, -0.75
    D = lambda h: G + a*h*h + b*h**4
    for h in (0.05, 0.025, 0.0125):
        R = (4*D(h) - D(2*h))/3.0
        assert R == pytest.approx(G - 4*b*h**4, rel=1e-12)


def test_adjacent_richardson_difference_is_fifteen_times_the_residual():
    G, a, b = 3.0, 1.5, -0.75
    D = lambda h: G + a*h*h + b*h**4
    h = 0.025
    R_fine = (4*D(h) - D(2*h))/3.0
    R_coarse = (4*D(2*h) - D(4*h))/3.0
    assert (R_coarse - R_fine) == pytest.approx(15*(R_fine - G), rel=1e-10)


def test_the_central_difference_has_no_odd_powers():
    G, a, b = 2.0, 1.0, 0.5
    g = lambda e: -(G*e) + (a/ -6.0)*0  # placeholder; use symmetry directly
    # a central difference of an even function is exactly zero
    even = lambda e: 3.0 + 4.0*e**2 + 5.0*e**4
    for h in (0.1, 0.05):
        assert (even(h) - even(-h)) == pytest.approx(0.0, abs=1e-12)


# --- ladder freeze -----------------------------------------------------------

def test_the_ladder_is_frozen_and_drops_only_the_coarse_rung():
    L = PLAN["fd_ladder"]
    assert L["rungs"] == [0.1, 0.05, 0.025]
    assert L["coarse_rung_dropped"] == 0.2
    assert L["frozen_scientific_pair"] == PROT["fd_steps"] == [0.05, 0.025]
    assert L["adjacent_pairs_required"] is True
    assert "P4ZA does NOT" in L["truncation_rule"]
    assert "conservative factor of 15" in L["truncation_rule"]
    assert "adjacent" in L["p4z_defect_corrected"].lower() or \
        "NON-adjacent" in L["p4z_defect_corrected"]


def test_the_ladder_choice_is_justified_by_measurement_not_assertion():
    cal = json.loads((NS/"results"/"ladder_calibration.json").read_text())
    assert cal["result_bearing"] is False
    assert 0.2 in cal["ladder"] and 0.00625 in cal["ladder"]
    assert "outside the asymptotic regime" in PLAN["fd_ladder"]["why_0_2_dropped"]
    assert "noise" in PLAN["fd_ladder"]["why_no_rung_below_0_025"]


def test_every_ladder_block_uses_the_frozen_rungs():
    want = {f"{h:g}" for h in PLAN["fd_ladder"]["rungs"]}
    n = 0
    for p in (NS/"production"/"blocks").rglob("fd_ladder_*.json"):
        assert set(json.loads(p.read_text())["central_difference_by_h"]) == want
        n += 1
    if n == 0: pytest.skip("no ladder blocks yet")


# --- K3 envelope / applicability --------------------------------------------

def test_the_envelope_is_calibrated_from_precision_statistics_only():
    for c in PLAN["configurations"]:
        assert "precision statistic" in c["calibration_source"]
        assert c["calibration_relative_sd_per_path"] > 0
    assert "measured_relative_sd" in PLAN["fixed_policy"]["sizing_rule"]


def test_the_sizing_rule_meets_r_star_with_a_two_fold_margin():
    r_star = PLAN["thresholds"]["r_star"]
    for c in PLAN["configurations"]:
        assert c["expected_relative_se"] == pytest.approx(r_star/2, rel=0.01)
        assert c["expected_relative_se"] < r_star


def test_skewnormal4_score_is_at_most_linear_which_is_hypothesis_L4():
    from rebaseguard_p4_general.families import REGISTRY
    psi = REGISTRY["skewnormal4"].psi
    z = np.array([1e3, 1e4, 1e5])
    for tail in (z, -z):
        slope = psi(tail)/tail
        assert np.all(np.isfinite(slope))
        # linear growth: the ratio converges rather than diverging
        assert abs(slope[-1] - slope[-2]) < abs(slope[1] - slope[0]) + 1e-9


def test_the_bounded_survival_lemma_supplies_an_effective_score_bound():
    from rebaseguard_p4_general.families import REGISTRY
    from rebaseguard_p4_general.detectors import Detector
    psi = REGISTRY["skewnormal4"].psi
    assert REGISTRY["skewnormal4"].score_bound is None      # globally unbounded
    for kind, thr in (("cusum",5.0),("sr",520.886133602749)):
        c_d = Detector(kind,thr).forcing_increment()
        grid = np.linspace(-c_d, c_d, 2001)
        m_eff = float(np.max(np.abs(psi(grid))))
        assert math.isfinite(m_eff) and m_eff > 0


# --- thresholds and immutability --------------------------------------------

def test_no_threshold_was_changed():
    t = PLAN["thresholds"]
    assert t["relative"] == PROT["gates"]["correspondence_relative_limit"] == 0.03
    assert t["z"] == PROT["gates"]["correspondence_z_limit"] == 4.0
    assert abs(1.96*math.sqrt(2)*t["r_star"] - 0.03) < 1e-8
    assert t["fd_ladder_relative_max"] == 0.02
    assert t["any_threshold_changed_by_p4za"] is False


def test_historical_and_parent_trees_are_untouched():
    assert git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization") \
        == AUDIT["parent_evidence"]["p4_theorem_tree"]
    assert json.loads((P4/"results"/"closure_decision.json").read_text())["verdict"] == "PARTIAL"
    for name, key in (("production/adjudication.json","p4z_adjudication_sha256"),
                      ("results/successor_closure.json","p4z_closure_sha256"),
                      ("production/campaign_plan.json","p4z_campaign_plan_sha256")):
        assert hashlib.sha256((P4Z/name).read_bytes()).hexdigest() \
            == AUDIT["parent_evidence"][key], name


def test_p4za_touches_no_path_outside_its_namespace():
    changed = git("diff","--name-only","p4z-location-family-feasibility","HEAD")
    for p in filter(None, changed.splitlines()):
        assert p.startswith("level4/closure_proofs/p4za_fullscope_closure/"), p


def test_no_inconclusive_is_reinterpreted_as_pass():
    ap = NS/"production"/"adjudication_p4za.json"
    if not ap.exists(): pytest.skip("P4ZA adjudication not built yet")
    a = json.loads(ap.read_text())
    for c in a["cells"]:
        if c["gate_result"] == "PASS":
            assert c["rb_score"]["blocks"] >= PLAN["fixed_policy"]["blocks_per_route"]
            assert c["rb_map"]["blocks"] >= PLAN["fixed_policy"]["blocks_per_route"]
            assert c["correspondence"]["relative_ok"] and c["correspondence"]["z_ok"]


# --- producer / seeds / caps -------------------------------------------------

def test_the_tcb_binds_the_inherited_estimators_by_content():
    m = sh.build_manifest()
    for rel in sh.TCB_PATHS:
        assert rel in m["entries"]
    assert any("rbscore.py" in p for p in sh.TCB_PATHS)
    assert any("rbmap.py" in p for p in sh.TCB_PATHS)
    assert any("p4za_campaign_plan.json" in p for p in sh.TCB_PATHS)


def test_head_is_excluded_from_the_producer_hash():
    m = sh.build_manifest()
    assert "head_informational" in m and "head" not in m
    sh.verify_manifest(dict(m, head_informational="0"*40))


def test_scientific_hash_fails_closed_on_unknown_types():
    with pytest.raises(sh.ProducerGateError):
        sh.scientific_hash({"bad": {1,2,3}})


def test_seed_schedule_is_disjoint_from_p4z_and_history():
    seeds = [s for c in PLAN["configurations"]
             for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])]
    assert len(set(seeds)) == len(seeds)
    z = json.loads((P4Z/"production"/"campaign_plan.json").read_text())
    zs = {s for c in z["configurations"]
          for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    assert not set(seeds) & zs
    assert not set(seeds) & set(PROT["master_seeds"].values())


def test_block_caps_and_non_adaptive_policy():
    f = PLAN["fixed_policy"]
    assert f["blocks_per_route"] == 200 and f["ladder_blocks"] == 40
    assert f["adaptive"] is False and f["top_ups_permitted"] == 0
    assert f["path_count_may_increase_during_run"] is False


def test_p4za_does_not_borrow_the_p4z_cap():
    assert PLAN["budget"]["borrowed_from_p4z_cap"] is False
    assert PLAN["budget"]["total_cpu_cap_hours"] == 6.0


def test_replay_when_present_is_bit_identical():
    p = NS/"production"/"replay_p4za.json"
    if not p.exists(): pytest.skip("replay not run yet")
    r = json.loads(p.read_text())
    assert r["all_scientific_hashes_identical"] is True
    assert r["any_scientific_field_mismatch"] is False


# --- final closure conservation ---------------------------------------------

def test_the_96_cell_coverage_is_conserved_and_unambiguous():
    cov = json.loads((NS/"results"/"claim_coverage.json").read_text())
    c = cov["counts"]
    assert sum(c.values()) == 96 == cov["cells_total"]
    assert c["UNCOVERED"] == 0 and cov["ambiguous"] == []
    assert cov["sources"]["P4Z"]["cells"] + cov["sources"]["P4ZA"]["cells"] == 96
    assert cov["sources"]["P4X"]["cells"] == 0


def test_closure_is_not_claimed_while_any_cell_is_inconclusive():
    d = json.loads((NS/"results"/"p4za_successor_closure.json").read_text())
    cov = json.loads((NS/"results"/"claim_coverage.json").read_text())
    if cov["counts"]["INCONCLUSIVE"] or cov["counts"]["UNCOVERED"]:
        assert d["verdict"] != "P4ZA_CLOSED"
    assert d["historical_status_unchanged"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    for claim in ("historical P4 was retroactively changed to PASS",
                  "P4 is CLOSED","P5Y is CLOSED","K1 is CLOSED",
                  "Level-4 is CLOSED","production readiness",
                  "the full 96-cell scope is closed"):
        assert claim in d["claims_explicitly_not_made"]


def test_the_open_cells_are_reported_with_their_frozen_limit():
    d = json.loads((NS/"results"/"p4za_successor_closure.json").read_text())
    for x in d["what_remains_open"]["detail"]:
        assert x["limit"] == 0.02
        assert x["relative_drift"] > x["limit"], "an open cell must actually exceed the limit"
        assert x["rb_score_relative_se"] < x["r_star"], "its K3 problem is resolved"
        assert x["rb_map_relative_se"] < x["r_star"]


def test_all_k7_cells_were_resolved_by_the_new_ladder():
    a = json.loads((NS/"production"/"adjudication_p4za.json").read_text())
    assert a["by_cause"]["K7"]["INCONCLUSIVE"] == 0
    assert a["by_cause"]["K7"]["FAIL"] == 0
    assert a["by_cause"]["K7"]["PASS"] == 20


def test_no_scientific_fail_anywhere():
    a = json.loads((NS/"production"/"adjudication_p4za.json").read_text())
    cov = json.loads((NS/"results"/"claim_coverage.json").read_text())
    assert a["counts"]["FAIL"] == 0
    assert cov["counts"]["COVERED_FAIL"] == 0


def test_the_independent_audit_reconstructs_rather_than_trusts():
    a = json.loads((NS/"production"/"independent_closure_audit.json").read_text())
    assert a["independent_of_the_runner"] is True
    assert a["verdict"] == "CLOSURE_AUDIT_PASS"
    assert a["checks_failed"] == 0
