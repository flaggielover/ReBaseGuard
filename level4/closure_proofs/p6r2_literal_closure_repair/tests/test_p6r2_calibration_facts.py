"""G9: the calibration facts must be carried forward, never reinterpreted."""
import json
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
P6R = NS.parent / "p6r_safe_rebaselining_confirmation"


def _crn():
    f = NS / "results" / "p6r2_crn_fixed_path_calibration_sensitivity.json"
    if not f.exists():
        pytest.skip("CRN artifact not produced yet")
    return json.loads(f.read_text())


def _audit():
    return json.loads((P6R / "precommit" / "calibration_audit.json").read_text())


def test_nonconverged_cells_remain_reported_as_nonconverged():
    """Derived from the FROZEN audit, not from the new artifact."""
    aud = _audit()
    assert aud["summary"]["all_converged"] is False
    assert set(aud["summary"]["non_converged_cells"]) == {"cusum_m2", "sr_m3"}
    crn = _crn()
    s = crn["calibration_summary_carried_forward"]
    assert s["all_converged"] is False
    assert set(s["non_converged_cells"]) == {"cusum_m2", "sr_m3"}
    assert s["n_converged"] == 6 and s["n_cells"] == 8
    for k in ("cusum_m2", "sr_m3"):
        assert crn["cells"][k]["calibration_facts_carried_forward"]["converged"] \
            is False


def test_final_refit_is_not_claimed_to_be_a_verified_fixed_point():
    crn = _crn()
    s = crn["calibration_summary_carried_forward"]
    assert s["final_refit_is_a_verified_fixed_point"] is False
    for c in crn["cells"].values():
        f = c["calibration_facts_carried_forward"]
        assert f["final_refit_followed_by_another_fixed_point_update"] is False
    assert crn["does_not_claim"].startswith("This artifact does NOT prove")


def test_sparse_s1_and_fallback_cells_are_carried_forward_exactly():
    aud, crn = _audit(), _crn()
    for k, c in aud["cells"].items():
        f = crn["cells"][k]["calibration_facts_carried_forward"]
        assert f["n_obs_behind_s1"] == c["n_obs_behind_s1"]
        assert f["s1_sparse"] == c["s1_sparse"]
        assert f["s1_is_fallback_equal_to_s0"] == c["s1_is_fallback_equal_to_s0"]
        assert f["variance_floor_1e-2_active"] == c["variance_floor_1e-2_active"]
        assert f["rho_max_can_bind"] == c["rho_max_can_bind"]
        # tau < m event count is the s1 evidence count, reported explicitly
        assert f["n_truncated_window_events_tau_lt_m"] == c["n_obs_behind_s1"]


def test_shipped_constants_are_unchanged_by_the_sensitivity():
    aud, crn = _audit(), _crn()
    assert crn["saw_m_recalibrated"] is False
    assert crn["shipped_constants_changed"] is False
    for k, c in aud["cells"].items():
        sh = crn["cells"][k]["shipped"]
        for f in ("g0", "g1", "s0", "s1"):
            assert sh[f] == c[f], (k, f)
        assert crn["cells"][k]["variants"]["baseline"]["s1_used"] == c["s1"]


def test_paths_are_identical_across_variants_in_every_cell():
    crn = _crn()
    assert crn["all_paths_identical_across_variants"] is True
    for k, c in crn["cells"].items():
        assert all(c["cycle0_innovation_paths_identical_across_variants"].values()), k


def test_cells_with_no_truncated_window_show_exactly_zero_movement():
    """s1 cannot fire where tau >= m always: CRN must give EXACTLY zero."""
    crn = _crn()
    for k, c in crn["cells"].items():
        if c["calibration_facts_carried_forward"]["n_obs_behind_s1"] == 0:
            for mm in ("rho_mean", "rms", "arl0"):
                assert c["max_abs_relative_change"][mm] == 0.0, (k, mm)


def test_the_corrected_artifact_names_itself_as_the_replacement():
    crn = _crn()
    assert crn["artifact"] == "CORRECTED_CRN_FIXED_PATH_CALIBRATION_SENSITIVITY"
    assert "CONFOUNDED" in crn["replaces"]
    assert "s1_sensitivity.json" in crn["replaces"]
