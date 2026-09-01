"""Closure condition 12: every documented claim must agree with the artifacts.

Each number quoted in CONFIRMATION_REPORT.md is re-derived here from
``results/*.json`` and ``precommit/*.json``.  These tests read artifacts; they
run no simulation.
"""
import json
from pathlib import Path

import numpy as np
import pytest

NS = Path(__file__).resolve().parents[1]
RES = NS / "results"
PRE = NS / "precommit"
CELLS8 = ("P", "RC1_sr_m3", "RC2_cusum_m1", "RC2_cusum_m2", "RC2_cusum_m5",
          "RC2_sr_m1", "RC2_sr_m2", "RC2_sr_m5")


def _j(p):
    if not p.exists():
        pytest.skip(f"{p.name} not produced yet")
    return json.loads(p.read_text())


def _eval():
    return _j(RES / "p6r_analysis_eval.json")


# --- the anchor (closure condition 10) -------------------------------------

def test_anchor_exists_is_pushed_and_matches_the_remote():
    a = _j(RES / "precommit_anchor.json")
    assert a["commit_sha"] == "fcc1355715426531c431e9390c9f12d1bad9b97c"
    assert a["pushed"] is True
    assert a["remote_matches_local"] is True
    assert a["checkpoint"] == "A"


def test_every_analysis_records_the_anchor_it_ran_after():
    for fam in ("eval", "replay"):
        a = _j(RES / f"p6r_analysis_{fam}.json")
        assert a["precommit_anchor"]["commit_sha"].startswith("fcc1355")


# --- the statistical procedure (closure condition 6) ------------------------

def test_reported_analysis_used_ten_thousand_resamples_everywhere():
    a = _eval()
    assert a["n_boot"] == 10_000 and a["bh_q"] == 0.10
    assert a["tail_event_floor"] == 200
    undef = {(r["cell"], r["comparison"], r["metric"])
             for r in _j(RES / "p6r_undefined_ratios.json")["families"]["eval"]["entries"]}
    seen = 0
    for tag, row in a["cells"].items():
        for bname, block in row["comparisons"].items():
            for eff in block.values():
                assert eff["n_boot"] == 10_000, eff["metric"]
                if (tag, bname, eff["metric"]) in undef:
                    continue          # zero denominator: undefined, carries no claim
                assert np.isfinite(eff["normal_lo"]) and np.isfinite(eff["normal_hi"])
                assert np.isfinite(eff["bca_lo"]) and np.isfinite(eff["bca_hi"])
                seen += 1
    assert seen > 300


def test_undefined_zero_denominator_effects_are_enumerated_and_claim_free():
    """Ratios against B3 (zero acquisition cost) and B0 (zero reuse) are undefined."""
    u = _j(RES / "p6r_undefined_ratios.json")
    a = _eval()
    for fam in ("eval", "replay"):
        blk = u["families"][fam]
        assert set(blk["controls_involved"]) <= {"B3_full_reuse", "B0_fresh_only"}
        assert set(blk["metrics_involved"]) <= {
            "C_acq_fresh_acquisition_count",
            "C_prop_proportional_fresh_contribution",
            "C_quad_effective_squared_weight_contribution",
            "Wbar_mean_algebraic_reuse_weight"}
    # none of them is inside any BH family
    fam_keys = set(a["cells"]["P"]["bh"]["F1_primary_cell_metrics"]["family"])
    fam_keys |= set(a["bh_F2_replication"]["family"])
    fam_keys |= set(a["bh_F4_finite_reference"]["family"])
    # F1 is keyed by metric, F2/F4 by cell; neither can name a B3/B0 comparison
    assert not any(k.startswith("vs_B3") or k.startswith("vs_B0") for k in fam_keys)
    # and every claimed cost comparison in the report uses a NON-degenerate control
    for tag in CELLS8:
        c = a["cells"][tag]["comparisons"]["vs_FIXED_TUNE@1.0"]
        assert np.isfinite(c["C_prop_proportional_fresh_contribution"]["rel"])


def test_bca_acceleration_is_nonzero_somewhere_ie_a_real_jackknife_ran():
    a = _eval()
    accels = [eff["accel"] for row in a["cells"].values()
              for block in row["comparisons"].values() for eff in block.values()]
    assert any(abs(x) > 1e-9 for x in accels)


def test_bh_families_are_emitted_with_adjusted_p_values():
    a = _eval()
    f1 = a["cells"]["P"]["bh"]["F1_primary_cell_metrics"]
    assert f1["n_tests"] == 14 and f1["q"] == 0.10
    assert sum(f1["reject"].values()) == 12
    assert set(k for k, v in f1["reject"].items() if not v) == {"Dmed", "Coll"}
    assert a["bh_F2_replication"]["n_tests"] == 8
    assert all(a["bh_F2_replication"]["reject"].values())
    assert a["bh_F4_finite_reference"]["n_tests"] == 3
    assert all(a["bh_F4_finite_reference"]["reject"].values())


# --- the tail floor (closure condition 7) ----------------------------------

def test_delta_2_tail_is_gated_and_excluded_from_its_family():
    a = _eval()
    d = a["cells"]["P"]["comparisons"]["vs_FIXED_TUNE@2.0"]["Dtail100"]
    assert d["verdict"] == "INSUFFICIENT_TAIL_EVENTS"
    assert d["tail_flag"] == "INSUFFICIENT_TAIL_EVENTS"
    assert min(d["n_events_method"], d["n_events_control"]) < 200
    f3 = a["cells"]["P"]["bh"]["F3_delta_scope"]
    assert "Dtail100@2.0" in f3["excluded_insufficient_tail"]
    assert not any(f3["reject"].values())


def test_every_claimed_tail_effect_clears_the_floor():
    a = _eval()
    for tag in CELLS8:
        d = a["cells"][tag]["comparisons"]["vs_FIXED_TUNE@1.0"]["Dtail100"]
        assert d["verdict"] != "INSUFFICIENT_TAIL_EVENTS", tag
        assert d["bca_hi"] < 0.0, tag


# --- TUNE-only selection (closure condition 4) -----------------------------

def test_selection_is_tune_only_and_matches_the_reported_values():
    s = _j(PRE / "baseline_selection.json")
    assert s["family"] == "tune"
    want = {"cusum_m1": 0.24, "cusum_m2": 0.19, "cusum_m3": 0.20,
            "cusum_m5": 0.17, "sr_m1": 0.22, "sr_m2": 0.21, "sr_m3": 0.23,
            "sr_m5": 0.19}
    for k, v in want.items():
        assert abs(s["cells"][k]["rho_selected"] - v) < 1e-9, k
        assert s["cells"][k]["family"] == "tune"
    assert s["adjudication_control_rho"] == 0.25


def test_confirmation_used_the_frozen_tune_rho_and_never_reselected():
    s = _j(PRE / "baseline_selection.json")
    for fam in ("eval", "replay"):
        m = _j(RES / f"p6r_confirm_manifest_{fam}.json")
        for cell in m["cells"]:
            key = f"{cell['detector']}_m{cell['m']}"
            assert cell["rho_tune"] == s["cells"][key]["rho_selected"], cell["tag"]


# --- the primary result (closure condition 5) ------------------------------

def test_primary_cell_headline_numbers():
    a = _eval()
    P = a["cells"]["P"]
    assert P["control_tune"] == "FIXED_TUNE_rho0.2"
    assert P["control_adj"] == "FIXED_ADJ_rho0.25"
    t = P["comparisons"]["vs_FIXED_TUNE@1.0"]
    assert abs(t["Dtail100"]["rel"] + 0.1292) < 5e-4
    assert t["Dtail100"]["bca_hi"] < -0.09
    assert t["Dtail100"]["verdict"] == "PRACTICALLY_MATERIAL"
    assert abs(t["Arl0"]["rel"] - 0.0443) < 5e-4 and t["Arl0"]["bca_lo"] > 0
    assert abs(t["Rms"]["rel"] + 0.0439) < 5e-4 and t["Rms"]["bca_hi"] < 0
    assert abs(t["Dq95"]["rel"] + 0.1497) < 1e-3
    # the ADJ control gives a LARGER effect, so the quoted one is the weaker
    j = P["comparisons"]["vs_FIXED_ADJ@1.0"]
    assert j["Dtail100"]["rel"] < t["Dtail100"]["rel"]


def test_replication_holds_in_all_eight_cells():
    a = _eval()
    for tag in CELLS8:
        c = a["cells"][tag]["comparisons"]["vs_FIXED_TUNE@1.0"]
        assert c["Arl0"]["bca_lo"] > 0, tag
        assert c["Rms"]["bca_hi"] < 0, tag
        assert c["Dtail100"]["bca_hi"] < 0, tag


def test_replay_reproduces_the_primary_effect():
    r = _j(RES / "p6r_analysis_replay.json")
    c = r["cells"]["P_replay"]["comparisons"]["vs_FIXED_TUNE@1.0"]
    assert abs(c["Dtail100"]["rel"] + 0.1047) < 1e-3
    assert c["Dtail100"]["bca_hi"] < 0
    assert c["Arl0"]["bca_lo"] > 0 and c["Rms"]["bca_hi"] < 0
    f1 = r["cells"]["P_replay"]["bh"]["F1_primary_cell_metrics"]
    assert sum(f1["reject"].values()) == 12


# --- cost (repairs Q2) -----------------------------------------------------

def test_acquisition_cost_is_identical_in_every_cell():
    a = _eval()
    for tag in CELLS8:
        c = a["cells"][tag]["comparisons"]["vs_FIXED_TUNE@1.0"]
        assert c["C_acq_fresh_acquisition_count"]["rel"] == 0.0, tag


def test_the_forbidden_cost_claims_are_not_supportable_against_both_controls():
    """The report must NOT say 'SAW is cheaper' or 'SAW reuses more'."""
    a = _eval()
    P = a["cells"]["P"]
    t = P["comparisons"]["vs_FIXED_TUNE@1.0"]
    j = P["comparisons"]["vs_FIXED_ADJ@1.0"]
    # against rho = 0.20 SAW is cheaper and reuses more ...
    assert t["C_prop_proportional_fresh_contribution"]["rel"] < 0
    assert t["Wbar_mean_algebraic_reuse_weight"]["rel"] > 0
    # ... and against rho = 0.25 it is NOT, which is why no general claim is made
    assert j["C_prop_proportional_fresh_contribution"]["rel"] > 0
    assert j["C_quad_effective_squared_weight_contribution"]["rel"] > 0
    assert j["Wbar_mean_algebraic_reuse_weight"]["rel"] < 0
    txt = (NS / "CONFIRMATION_REPORT.md").read_text().lower()
    for banned in ("saw reuses more,", "saw is cheaper,"):
        assert banned not in txt


# --- the one-step evidence (repairs Q8) ------------------------------------

def test_one_step_gain_and_its_null_calibration():
    a = _eval()
    g = a["cells"]["P"]["onestep"]["on_SAW_chain"]
    assert abs(g["G"] - 0.09089) < 5e-4
    assert g["bca_lo"] > 0 and g["n_boot"] == 10_000
    assert g["n_clusters"] == 8000
    # the constant policy's own gain must be non-positive by construction
    n = a["cells"]["P"]["onestep"]["on_FIXED_TUNE_chain"]
    assert n["G"] <= 0.0


def test_cross_chain_statistic_is_recorded_as_post_anchor():
    x = _j(RES / "p6r_onestep_cross.json")
    assert "AFTER the Checkpoint A anchor" in x["note"]
    tune = [k for k in x["blocks"] if k.startswith("FIXED_TUNE")][0]
    cross = x["blocks"][tune]["SAW_M_rule_gain_on_this_chain"]
    own = x["blocks"][tune]["own_policy_gain_over_best_constant"]
    assert abs(cross["G"] - 0.0933) < 5e-4
    assert own["G"] <= 0.0
    assert cross["bca_lo"] > 0


# --- calibration audit (repairs Q3) ----------------------------------------

def test_calibration_audit_reports_the_defects_without_softening():
    aud = _j(PRE / "calibration_audit.json")
    s = aud["summary"]
    assert s["all_converged"] is False
    assert set(s["non_converged_cells"]) == {"cusum_m2", "sr_m3"}
    assert s["variance_floor_active_anywhere"] is False
    assert s["rho_max_can_bind_anywhere"] is False
    assert s["final_refit_is_a_verified_fixed_point"] is False
    assert aud["cells"]["cusum_m3"]["n_obs_behind_s1"] == 262
    assert aud["cells"]["cusum_m2"]["n_obs_behind_s1"] == 3


def test_s1_sensitivity_was_run_for_every_cell_not_only_sparse_ones():
    s = _j(PRE / "s1_sensitivity.json")
    assert len(s["cells"]) == 8
    worst = max(v["max_abs_rel_change_arl0"] for v in s["cells"].values())
    assert worst < 0.05
    assert abs(worst - 0.0373) < 2e-3


# --- delta scope (repairs Q4) ----------------------------------------------

def test_delta_half_is_inconclusive_and_reported_as_a_limitation():
    a = _eval()
    d = a["cells"]["P"]["comparisons"]["vs_FIXED_TUNE@0.5"]
    for k in ("Dtail100", "Dq95", "Dmean"):
        assert d[k]["verdict"] == "INCONCLUSIVE", k
        assert d[k]["bca_lo"] < 0 < d[k]["bca_hi"], k


def test_finite_reference_holds_at_every_m0():
    a = _eval()
    for tag in ("RC4_m020", "RC4_m050", "RC4_m0100"):
        c = a["cells"][tag]["comparisons"]["vs_FIXED_TUNE@1.0"]
        assert c["Dtail100"]["bca_hi"] < 0, tag
        assert c["Arl0"]["bca_lo"] > 0, tag


# --- language constraints (repairs Q6, Q7, Q9) -----------------------------

def test_report_language_obeys_the_precommitted_constraints():
    txt = (NS / "CONFIRMATION_REPORT.md").read_text()
    low = txt.lower()
    # the forbidden phrases may appear ONLY inside an explicit negation
    for banned in ("detector transfer", "full initialization robustness"):
        for line in low.splitlines():
            if banned in line:
                assert f'not "{banned}"' in line, f"unqualified use of {banned!r}"
    assert "separately calibrated" in low
    assert "post-burn-in robustness to alternative initialization" in low
    for line in ("Algorithmic novelty  = NOT ESTABLISHED",
                 "Theoretical novelty  = NOT ESTABLISHED",
                 "Formulation novelty  = PLAUSIBLE",
                 "Integration novelty  = PLAUSIBLE"):
        assert line in txt
