"""Metric correctness and replicate-level inference (Gate 4.1)."""

from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_level4 import metrics
from rebaseguard_level4.metrics import (
    autocorrelation,
    bootstrap_estimate,
    burn_in_diagnostic,
    replicate_statistics,
    summarise,
)
from rebaseguard_level4.multicycle import MultiCycleConfig, simulate_multicycle


def test_autocorrelation_of_perfect_alternation():
    x = np.array([1.0, -1.0] * 50)
    acf = autocorrelation(x, [1, 2, 3, 4])
    assert acf[0] == pytest.approx(-0.99, abs=0.02)
    assert acf[1] == pytest.approx(0.98, abs=0.02)
    assert acf[2] == pytest.approx(-0.97, abs=0.03)
    assert acf[3] == pytest.approx(0.96, abs=0.03)


def test_autocorrelation_matches_explicit_formula():
    rng = np.random.default_rng(3)
    x = rng.normal(size=400)
    xc = x - x.mean()
    denom = np.dot(xc, xc)
    for lag in (1, 5, 20):
        want = np.dot(xc[:-lag], xc[lag:]) / denom
        assert autocorrelation(x, [lag])[0] == pytest.approx(want)


def test_autocorrelation_of_white_noise_is_near_zero():
    rng = np.random.default_rng(11)
    acf = autocorrelation(rng.normal(size=200_000), [1, 2, 3])
    assert np.all(np.abs(acf) < 0.01)


def test_autocorrelation_edge_cases():
    x = np.arange(5.0)
    assert np.isnan(autocorrelation(x, [0])[0])
    assert np.isnan(autocorrelation(x, [5])[0])
    assert np.isnan(autocorrelation(np.ones(10), [1])[0])


def test_replicate_statistics_shapes_and_definitions():
    cfg = MultiCycleConfig(n_replicates=6, n_cycles=50, burn_in=10, rho=1.0, m=1,
                           master_seed=4)
    table = simulate_multicycle(cfg)
    stats = replicate_statistics(table)
    for name, values in stats.items():
        assert values.shape == (6,), name
    e = table.post_burn_in().by_replicate("e_next")
    assert stats["mean_reference_error"] == pytest.approx(e.mean(axis=1))
    assert stats["rmse_reference_error"] == pytest.approx(
        np.sqrt((e ** 2).mean(axis=1))
    )
    tau = table.post_burn_in().by_replicate("tau").astype(float)
    assert stats["cycle_arl"] == pytest.approx(tau.mean(axis=1))
    assert stats["median_tau"] == pytest.approx(np.median(tau, axis=1))
    d = table.post_burn_in().by_replicate("direction").astype(float)
    assert stats["alternation_rate"] == pytest.approx(
        (d[:, 1:] != d[:, :-1]).mean(axis=1)
    )


def test_post_burn_in_drops_exactly_the_burn_in_cycles():
    cfg = MultiCycleConfig(n_replicates=4, n_cycles=30, burn_in=7, rho=0.5, m=1,
                           master_seed=5)
    table = simulate_multicycle(cfg)
    retained = table.post_burn_in()
    assert retained.e_next.size == 4 * 30
    assert retained.cycle_index.min() == 7
    assert not retained.in_burn_in.any()


def test_bootstrap_is_reproducible_and_seed_recorded():
    values = np.random.default_rng(0).normal(5.0, 2.0, 60)
    a = bootstrap_estimate(values, metric="x", master_seed=7, metric_index=3)
    b = bootstrap_estimate(values, metric="x", master_seed=7, metric_index=3)
    assert (a.ci_low, a.ci_high) == (b.ci_low, b.ci_high)
    c = bootstrap_estimate(values, metric="x", master_seed=8, metric_index=3)
    assert (a.ci_low, a.ci_high) != (c.ci_low, c.ci_high)
    assert a.bootstrap_seed_key == [7, metrics.STREAM_BOOTSTRAP, 3]
    assert a.as_dict()["statistical_unit"] == "replicate"


def test_bootstrap_interval_brackets_the_point_estimate():
    values = np.random.default_rng(1).normal(-3.0, 1.0, 80)
    est = bootstrap_estimate(values, metric="x", master_seed=1, metric_index=0)
    assert est.ci_low < est.point < est.ci_high
    assert est.standard_error == pytest.approx(est.replicate_sd / np.sqrt(80),
                                               rel=0.15)


def test_bootstrap_coverage_is_approximately_nominal():
    """95% intervals should cover the truth about 95% of the time."""
    truth = 2.5
    covered = 0
    trials = 300
    rng = np.random.default_rng(99)
    for i in range(trials):
        sample = rng.normal(truth, 1.0, 100)
        est = bootstrap_estimate(sample, metric="x", master_seed=i,
                                 metric_index=0, n_bootstrap=600)
        covered += est.ci_low <= truth <= est.ci_high
    assert 0.90 <= covered / trials <= 0.99


def test_bootstrap_rejects_empty_input():
    with pytest.raises(ValueError):
        bootstrap_estimate(np.array([np.nan]), metric="x", master_seed=1,
                           metric_index=0)


def test_summarise_reports_unit_and_all_headline_metrics():
    cfg = MultiCycleConfig(n_replicates=5, n_cycles=60, burn_in=10, rho=1.0, m=1,
                           master_seed=6)
    out = summarise(simulate_multicycle(cfg), n_bootstrap=200)
    assert out["statistical_unit"] == "replicate"
    assert out["n_two_arm_ties"] == 0
    for name in ("mean_reference_error", "var_reference_error",
                 "rmse_reference_error", "cycle_arl", "median_tau",
                 "alarm_up_proportion", "alternation_rate",
                 "acf_e_lag1", "acf_direction_lag1", "e_quantile_0.5"):
        est = out["estimates"][name]
        assert est["ci_method"] == "percentile-bootstrap-over-replicates"
        assert est["ci_level"] == 0.95
        assert est["n_replicates"] == 5
    assert out["pooled_empirical_distribution"]["n"] == 5 * 60


def test_burn_in_diagnostic_covers_the_whole_run():
    cfg = MultiCycleConfig(n_replicates=4, n_cycles=80, burn_in=20, rho=1.0, m=1,
                           master_seed=8)
    diag = burn_in_diagnostic(simulate_multicycle(cfg), n_blocks=5)
    assert diag["burn_in_cycles"] == 20
    assert diag["blocks"][0]["contains_burn_in"] is True
    assert diag["blocks"][-1]["contains_burn_in"] is False
    assert diag["blocks"][-1]["cycle_range"][1] == 100


def test_fresh_control_shows_no_alternation_and_reuse_does():
    """The headline contrast, at smoke size: a sanity guard, not a result."""
    fresh = summarise(simulate_multicycle(MultiCycleConfig(
        n_replicates=8, n_cycles=400, burn_in=50, rho=0.0, m=1,
        master_seed=1234)), n_bootstrap=200)
    reuse = summarise(simulate_multicycle(MultiCycleConfig(
        n_replicates=8, n_cycles=400, burn_in=50, rho=1.0, m=1,
        master_seed=1234)), n_bootstrap=200)
    assert fresh["estimates"]["alternation_rate"]["point"] == pytest.approx(0.5,
                                                                           abs=0.03)
    assert reuse["estimates"]["alternation_rate"]["point"] > 0.8
    assert abs(fresh["estimates"]["acf_e_lag1"]["point"]) < 0.05
    assert reuse["estimates"]["acf_e_lag1"]["point"] < -0.3
