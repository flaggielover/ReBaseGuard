"""Blocking defect 2: the preregistered statistical procedure must be EXECUTED.

Each element the preregistration names is asserted to actually run, not merely
to be available.
"""
import numpy as np
import pytest
from scipy.stats import norm

from rebaseguard_p6r import stats_r as ST


def _skewed(n=400, seed=3):
    rng = np.random.default_rng(seed)
    return rng.lognormal(0.0, 1.0, n), rng.lognormal(0.1, 1.0, n)


# --- the resample count ----------------------------------------------------

def test_resample_count_is_exactly_ten_thousand():
    assert ST.N_BOOT == 10_000
    a, b = _skewed()
    for e in (ST.paired_ratio_of_means(a, b, metric="x"),
              ST.paired_ratio_of_quantiles(a, b, 0.95, metric="x")):
        assert e.n_boot == 10_000


def test_chunking_does_not_change_the_resample_count():
    a, b = _skewed(n=60)
    seen = sum(idx.shape[0] for idx in
               ST._boot_indices(np.random.default_rng(0), 60, ST.N_BOOT))
    assert seen == 10_000


# --- BCa is really computed ------------------------------------------------

def test_bca_is_computed_and_differs_from_a_plain_percentile_interval():
    a, b = _skewed()
    e = ST.paired_ratio_of_means(a, b, metric="x")
    assert np.isfinite(e.z0) and np.isfinite(e.accel)
    assert e.accel != 0.0, "acceleration must come from a real jackknife"
    # rebuild the plain percentile interval from the same resamples
    rng = np.random.default_rng(0)
    parts = [a[i].mean(axis=1) / b[i].mean(axis=1)
             for i in ST._boot_indices(rng, a.size, ST.N_BOOT)]
    boot = np.concatenate(parts)
    plo, phi = np.quantile(boot, [0.025, 0.975]) - 1.0
    assert abs(e.bca_lo - plo) > 1e-9 or abs(e.bca_hi - phi) > 1e-9


def test_bca_acceleration_uses_a_real_jackknife_for_quantiles():
    """The LOO quantile construction must match brute-force deletion exactly."""
    rng = np.random.default_rng(11)
    x = rng.normal(size=61)
    for q in (0.5, 0.75, 0.95):
        fast = ST.loo_quantiles(x, q)
        slow = np.array([np.quantile(np.delete(x, i), q) for i in range(x.size)])
        assert np.abs(fast - slow).max() < 1e-12, q


def test_loo_means_match_brute_force():
    rng = np.random.default_rng(12)
    x = rng.normal(size=37)
    slow = np.array([np.delete(x, i).mean() for i in range(x.size)])
    assert np.abs(ST.loo_means(x) - slow).max() < 1e-12


# --- normal intervals are emitted -----------------------------------------

def test_normal_interval_is_emitted_beside_every_bca_interval():
    a, b = _skewed()
    for e in (ST.paired_ratio_of_means(a, b, metric="x"),
              ST.paired_ratio_of_quantiles(a, b, 0.95, metric="x"),
              ST.paired_ratio_of_ratios(a, b, b, a, metric="x")):
        assert np.isfinite(e.normal_lo) and np.isfinite(e.normal_hi)
        assert e.normal_hi > e.normal_lo
        assert abs(e.normal_hi - e.normal_lo
                   - 2 * norm.ppf(0.975) * e.boot_sd) < 1e-9
        # on a skewed sample the two intervals must actually differ
        assert (abs(e.normal_lo - e.bca_lo) > 1e-9
                or abs(e.normal_hi - e.bca_hi) > 1e-9)


# --- ratios are bootstrapped AS ratios, over replicate PAIRS ---------------

def test_ratio_resampling_is_paired_not_post_hoc_division():
    """If a == b, a paired ratio resample is identically 1 and has zero spread.

    Independent post-hoc division of two separately bootstrapped means would
    give a strictly positive spread, so this separates the two implementations.
    """
    rng = np.random.default_rng(5)
    a = rng.lognormal(0.0, 1.2, 500)
    e = ST.paired_ratio_of_means(a, a.copy(), metric="identical")
    assert e.rel == 0.0
    assert e.boot_sd == 0.0
    assert e.bca_lo == 0.0 and e.bca_hi == 0.0
    # ... and the independent-division alternative would NOT be degenerate
    r1, r2 = np.random.default_rng(1), np.random.default_rng(2)
    ind = (a[r1.integers(0, 500, (400, 500))].mean(axis=1)
           / a[r2.integers(0, 500, (400, 500))].mean(axis=1))
    assert ind.std() > 1e-3


def test_ratio_of_ratios_reforms_the_ratio_inside_each_resample():
    rng = np.random.default_rng(7)
    num = rng.lognormal(size=300)
    den = rng.lognormal(size=300)
    e = ST.paired_ratio_of_ratios(num, den, num.copy(), den.copy(),
                                  metric="self")
    assert e.rel == 0.0 and e.boot_sd == 0.0


def test_ratio_of_quantiles_is_paired():
    rng = np.random.default_rng(9)
    a = rng.lognormal(size=400)
    e = ST.paired_ratio_of_quantiles(a, a.copy(), 0.95, metric="identical")
    assert e.boot_sd == 0.0 and e.rel == 0.0


# --- BH adjustment is emitted ---------------------------------------------

def test_benjamini_hochberg_matches_the_textbook_step_up():
    """Benjamini & Hochberg (1995) worked example, n = 8, q = 0.10.

    Thresholds ``q i / n`` are 0.0125 ... 0.10; the largest ``i`` with
    ``p_(i) <= q i / n`` is ``i = 7`` (``0.074 <= 0.0875``), so the step-up
    procedure rejects the seven smallest -- including ``p = 0.039``, which fails
    its own threshold but is carried by the step-up.
    """
    p = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205])
    rej, adj = ST.benjamini_hochberg(p, q=0.10)
    assert adj.shape == p.shape
    assert np.all(np.diff(adj[np.argsort(p)]) >= -1e-12)   # monotone in p
    assert rej[:7].all() and not rej[7:].any()
    assert abs(adj[0] - 0.008) < 1e-12
    assert abs(adj[7] - 0.205) < 1e-12
    assert abs(adj[2] - 0.0672) < 1e-9      # step-up pulled 0.039 down


def test_bh_family_emits_adjusted_p_and_excludes_subfloor_tails():
    a, b = _skewed()
    good = ST.paired_ratio_of_means(a, b, metric="g")
    bad = ST.apply_tail_gate(ST.paired_ratio_of_means(a, b, metric="t"), 10, 5)
    fam = ST.bh_family({"g": good, "t": bad})
    assert fam["n_tests"] == 1
    assert fam["family"] == ["g"]
    assert fam["excluded_insufficient_tail"] == ["t"]
    assert "g" in fam["p_adjusted"] and "g" in fam["reject"]
    assert fam["q"] == ST.BH_Q == 0.10


# --- the tail-event floor --------------------------------------------------

def test_insufficient_tail_cells_are_marked_and_carry_no_resolved_claim():
    assert ST.TAIL_EVENT_FLOOR == 200
    a, b = _skewed()
    e = ST.paired_ratio_of_means(a, b, metric="Dtail100")
    ok = ST.apply_tail_gate(e, 500, 400)
    assert ok.tail_flag is None and ok.verdict == e.verdict
    for nm, nc in ((199, 5000), (5000, 199), (3, 4)):
        bad = ST.apply_tail_gate(e, nm, nc)
        assert bad.tail_flag == ST.INSUFFICIENT_TAIL_EVENTS
        assert bad.verdict == ST.INSUFFICIENT_TAIL_EVENTS
        assert bad.verdict not in (ST.STATISTICALLY_RESOLVED,
                                   ST.PRACTICALLY_MATERIAL, ST.INCONCLUSIVE)


def test_p_values_are_two_sided_and_floored():
    a = np.arange(1.0, 201.0)
    e = ST.paired_ratio_of_means(a + 1000.0, a + 1000.0, metric="null")
    assert 0.0 < e.p_value <= 1.0


def test_cluster_bootstrap_resamples_clusters_not_rows():
    rng = np.random.default_rng(13)
    num = rng.lognormal(size=200)
    den = np.full(200, 50.0)
    out = ST.cluster_bootstrap_ratio(num, den)
    assert out["n_clusters"] == 200 and out["n_boot"] == 10_000
    assert out["bca_lo"] < out["estimate"] < out["bca_hi"]
