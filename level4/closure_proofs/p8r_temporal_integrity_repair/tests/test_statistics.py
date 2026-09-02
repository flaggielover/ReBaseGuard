"""The frozen statistical plan is the one the analysis actually followed."""
import numpy as np
import pytest

from rebaseguard_p8r.analysis import (Z95, batch_mean_se, cochran_q,
                                      rho_c_from_gamma, spread)
from conftest import payload_or_skip


def test_paired_ratio_uses_the_covariance_not_an_independent_formula():
    """Two strongly correlated batch vectors: the paired SE must be much
    smaller than the naive independent SE.  Reusing the independent formula for
    a CRN-paired ratio is exactly what the P8 adjudication had to correct by
    hand."""
    from derive_resolution import paired_ratio
    rng = np.random.default_rng(7)
    common = rng.normal(10.0, 1.0, 20)
    a = common + rng.normal(0, 0.02, 20)
    b = common * 0.9 + rng.normal(0, 0.02, 20)
    r = paired_ratio(a, b)
    assert r["batch_correlation"] > 0.9
    assert r["se"] < 0.25 * r["naive_unpaired_se"]


def test_paired_ratio_reduces_to_the_ordinary_ratio_of_means():
    from derive_resolution import paired_ratio
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([2.0, 2.0, 2.0, 2.0, 2.0])
    assert abs(paired_ratio(a, b)["ratio"] - a.mean() / b.mean()) < 1e-12


def test_rho_c_interval_is_the_exact_monotone_image():
    d = rho_c_from_gamma(15.0, 0.5)
    lo, hi = d["gamma_ci95"]
    assert abs(d["rho_c"] - 1.0 / 14.0) < 1e-12
    assert abs(d["rho_c_interval"][0] - 1.0 / (hi - 1.0)) < 1e-12
    assert abs(d["rho_c_interval"][1] - 1.0 / (lo - 1.0)) < 1e-12


def test_rho_c_interval_is_unbounded_when_the_ci_straddles_one():
    d = rho_c_from_gamma(1.0, 0.5)
    assert d["rho_c_interval"][1] is None


def test_batch_mean_se_is_the_batch_means_estimator():
    v = np.array([1.0, 2.0, 3.0, 4.0])
    m, se, n = batch_mean_se(v)
    assert n == 4 and abs(m - 2.5) < 1e-12
    assert abs(se - v.std(ddof=1) / 2.0) < 1e-12


def test_cochran_q_is_labelled_descriptive_only():
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    assert "cochran_q_DESCRIPTIVE_ONLY" in by_q["S13"]["detail"]


def test_multiple_comparison_companion_is_never_part_of_a_gate():
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    comp = by_q["S10"]["detail"]["uncertainty_companion"]
    assert "DESCRIPTIVE ONLY" in comp["note"]
    # the gate statistic must not mention the companion
    assert "bh" not in str(by_q["S10"]["statistic"]).lower()


def test_heavy_tail_family_is_excluded_from_the_regime_gate_but_reported():
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    d = by_q["S6"]["detail"]
    assert d["moment_marginal_reported"], "t3 cells must still be reported"
    assert all(r["family"] != "t3" for r in d["eligible"])


def test_insufficient_tail_cells_are_labelled_not_dropped():
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    rows = by_q["S14"]["detail"]["rows"]
    for r in rows:
        if "tail_label" in r:
            assert r["tail_label"] in ("OK", "INSUFFICIENT_TAIL_EVENTS")
            assert r["q95"] is not None


def test_spread_statistic_is_max_over_min_minus_one():
    assert abs(spread([1.0, 1.1]) - 0.1) < 1e-12
    assert spread([1.0, -1.0]) == float("inf")


def test_seed_families_are_independent_not_paired(p8r):
    """E1 and E5 use different production tags, so their fields are disjoint
    and a combined (unpaired) SE is the correct comparison."""
    from rebaseguard_p8r.addressing import PROD_GAMMA_E1, PROD_GAMMA_E5
    from rebaseguard_p8r.addressing import tag_digest
    assert tag_digest(PROD_GAMMA_E1) != tag_digest(PROD_GAMMA_E5)
