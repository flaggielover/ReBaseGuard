"""A(e) curve, checkpointing, paired inference, and Pareto machinery."""

from __future__ import annotations

import json

import numpy as np
import pytest

from analyze import classify_regime, paired_bootstrap, pareto_front
from arl_curve import ACurve, default_grid, estimate_A
from campaign import EXTRA_RHO, PROTOCOL_RHO, cell_path, config_hash, full_rho_grid, run_cell


# ------------------------------------------------------------------ A(e) --

def test_default_grid_is_symmetric_and_covers_stationary_mass():
    g = default_grid()
    assert np.allclose(g, -g[::-1])
    assert g.min() <= -5.0 and g.max() >= 5.0
    # Stage A's widest stationary sd is 1.371 at rho = 1; +/-5 is well beyond
    assert g.max() / 1.371 > 3.5


def test_A_matches_the_frozen_in_control_arl_at_zero():
    out = estimate_A([0.0], n_paths=60_000, master_seed=4242)
    a = out["records"][0]
    assert a["A"] == pytest.approx(465.0, rel=0.02)
    assert abs(a["A"] - 465.0) < 4 * a["A_se"] + 5.0


def test_A_decreases_with_displacement():
    out = estimate_A([0.0, 0.5, 1.0, 2.0], n_paths=20_000, master_seed=7)
    vals = [r["A"] for r in out["records"]]
    assert vals[0] > vals[1] > vals[2] > vals[3]


def test_A_is_symmetric_within_error():
    out = estimate_A([-0.6, 0.6], n_paths=60_000, master_seed=13)
    a, b = out["records"]
    assert abs(a["A"] - b["A"]) < 4 * np.hypot(a["A_se"], b["A_se"])


def test_curve_interpolates_in_log_space_and_clamps():
    e = np.array([-1.0, 0.0, 1.0])
    curve = ACurve(e, np.array([10.0, 400.0, 10.0]), np.array([0.1, 1.0, 0.1]))
    mid = curve(np.array([0.5]))[0]
    assert 10.0 < mid < 400.0
    # log-linear interpolation sits below the arithmetic midpoint on a steep decay
    assert mid < 205.0
    assert curve(np.array([-9.0]))[0] == pytest.approx(10.0)
    assert curve.out_of_range_fraction(np.array([-9.0, 0.0])) == 0.5


def test_monotonicity_diagnostic_flags_a_real_increase():
    e = np.array([0.0, 0.5, 1.0, 1.5])
    good = ACurve(e, np.array([400.0, 40.0, 10.0, 5.0]), np.full(4, 0.01))
    assert good.monotonicity_diagnostics()["monotone_decreasing_in_abs_e"]
    bad = ACurve(e, np.array([400.0, 40.0, 90.0, 5.0]), np.full(4, 0.01))
    diag = bad.monotonicity_diagnostics()
    assert not diag["monotone_decreasing_in_abs_e"]
    assert diag["n_significantly_increasing"] == 1


# -------------------------------------------------------------- grid rules --

def test_protocol_grid_is_preserved_and_additions_are_recorded():
    grid = full_rho_grid()
    for rho in PROTOCOL_RHO:
        assert rho in grid, f"protocol point {rho} was dropped"
    for rho in EXTRA_RHO:
        assert rho in grid
    assert len(grid) == len(set(PROTOCOL_RHO) | set(EXTRA_RHO))


def test_added_points_are_the_policy_values():
    import policy
    assert policy.rho_safe(0.2, variant=policy.CONSERVATIVE).rho == \
        pytest.approx(EXTRA_RHO[0], abs=1e-6)
    assert policy.rho_safe(0.2, variant=policy.POINT).rho == \
        pytest.approx(EXTRA_RHO[1], abs=1e-6)


# ----------------------------------------------------------- checkpointing --

def test_checkpoint_is_reused_and_config_sensitive(tmp_path, monkeypatch):
    import campaign
    monkeypatch.setattr(campaign, "CELLS", tmp_path)
    calls = []

    def compute():
        calls.append(1)
        return {"value": 42}

    key = {"rho": 0.5, "n": 10}
    campaign.run_cell("t", key, compute, verbose=False)
    campaign.run_cell("t", key, compute, verbose=False)
    assert len(calls) == 1, "checkpoint was not reused"
    campaign.run_cell("t", {"rho": 0.5, "n": 11}, compute, verbose=False)
    assert len(calls) == 2, "a changed config silently reused a stale cell"
    campaign.run_cell("t", key, compute, verbose=False, force=True)
    assert len(calls) == 3, "force did not recompute"


def test_config_hash_is_order_independent():
    assert config_hash({"a": 1, "b": 2}) == config_hash({"b": 2, "a": 1})
    assert config_hash({"a": 1}) != config_hash({"a": 2})


# ------------------------------------------------------- paired inference --

def test_paired_bootstrap_detects_a_shared_offset_that_unpaired_would_miss():
    """The whole point of pairing: a small consistent difference under big
    common variation must still be resolvable."""
    rng = np.random.default_rng(0)
    common = rng.normal(0.0, 10.0, 200)
    a = common + 0.5
    b = common
    paired = paired_bootstrap(a, b, seed=1, index=0, n_boot=2000)
    assert paired["ci_low"] > 0.0
    assert paired["point"] == pytest.approx(0.5, abs=0.01)
    # unpaired treatment of the same data cannot resolve it
    unpaired_se = np.hypot(a.std(ddof=1), b.std(ddof=1)) / np.sqrt(200)
    assert unpaired_se > paired["se"] * 5


def test_paired_bootstrap_ratio_and_reproducibility():
    a = np.full(50, 2.0)
    b = np.full(50, 1.0)
    r = paired_bootstrap(a, b, seed=3, index=1, statistic="ratio", n_boot=500)
    assert r["point"] == pytest.approx(2.0)
    again = paired_bootstrap(a, b, seed=3, index=1, statistic="ratio", n_boot=500)
    assert (r["ci_low"], r["ci_high"]) == (again["ci_low"], again["ci_high"])


def test_paired_bootstrap_rejects_misaligned_inputs():
    with pytest.raises(ValueError, match="same shape"):
        paired_bootstrap(np.zeros(5), np.zeros(6), seed=1, index=0)


# ------------------------------------------------------------------ Pareto --

def test_pareto_front_keeps_only_non_dominated_points():
    pts = [(1.0, 5.0), (2.0, 4.0), (3.0, 6.0), (4.0, 1.0), (2.5, 4.5)]
    front = pareto_front(pts)
    assert 2 not in front and 4 not in front
    assert set(front) == {0, 1, 3}


def test_regime_classification_keeps_the_undetermined_band_visible():
    cert = (0.037245, 0.341957)
    assert classify_regime(0.01, 0.067178, cert) == "certified-stable"
    assert classify_regime(0.5, 0.067178, cert) == "certified-unstable"
    mid_low = classify_regime(0.05, 0.067178, cert)
    mid_high = classify_regime(0.2, 0.067178, cert)
    assert "undetermined-by-certificate" in mid_low
    assert "undetermined-by-certificate" in mid_high
    assert mid_low.endswith("point-stable") and mid_high.endswith("point-unstable")
