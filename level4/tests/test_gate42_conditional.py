"""Conditional-map estimator and its analysis layer (Gate 4.2)."""

from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_certify import model as frozen_model
from rebaseguard_level4 import analysis
from rebaseguard_level4.conditional import (
    ConditionalConfig,
    estimate_conditional_map,
    lr_map,
    score_gamma,
    simulate_cycle_batch,
)
from rebaseguard_level4.frozen import rebaseline
from rebaseguard_level4.streams import STREAM_CONDITIONAL, STREAM_FRESH, ScalarStream

GAMMA_CERT_LOW = 3.9243482005828971
GAMMA_CERT_HIGH = 27.849382127546703


def _batch(e, n, m, key=(STREAM_CONDITIONAL, 0, 0, 0), seed=777):
    return simulate_cycle_batch(
        e=e, n_paths=n, m=m,
        stream=ScalarStream(seed, *key),
        fresh_stream=ScalarStream(seed, STREAM_FRESH, *key),
    )


# ---------------------------------------------- frozen semantics, one cycle --

def test_single_path_batch_equals_frozen_run_path():
    """With one path the stream is consumed in order, so compare directly."""
    key = (STREAM_CONDITIONAL, 0, 0, 0)
    batch = _batch(0.0, 1, 1, key)
    innovations = ScalarStream(777, *key).draw(200_000)
    want = frozen_model.run_path(innovations.tolist())
    assert batch.tau[0] == want.tau
    assert batch.z_tau[0] == want.z_tau
    assert batch.t_tau[0] == pytest.approx(want.t_sum, rel=1e-12)
    assert batch.s_plus_terminal[0] == want.terminal_state.plus
    assert batch.s_minus_terminal[0] == want.terminal_state.minus


def test_reference_offset_sign_convention():
    """Z_t = X_t - e: a positive e biases the DOWN arm, so alarms skew down."""
    up_at_zero = (_batch(0.0, 4000, 1).direction > 0).mean()
    up_at_plus = (_batch(0.8, 4000, 1).direction > 0).mean()
    assert up_at_zero == pytest.approx(0.5, abs=0.03)
    assert up_at_plus < 0.1


@pytest.mark.parametrize("m", [1, 2, 5, 20])
def test_conditional_batch_respects_minimum_dwell(m):
    assert _batch(0.0, 500, m).tau.min() >= m


def test_conditional_batch_window_is_the_last_m_residuals():
    m = 4
    key = (STREAM_CONDITIONAL, 0, 0, 0)
    batch = _batch(0.3, 1, m, key)
    innovations = ScalarStream(777, *key).draw(200_000) - 0.3
    tau = int(batch.tau[0])
    assert batch.window_sum[0] == pytest.approx(innovations[tau - m:tau].sum(),
                                                rel=1e-10)
    assert batch.mu_reuse[0] == pytest.approx(0.3 + batch.window_sum[0] / m,
                                              rel=1e-12)


def test_conditional_batch_has_no_two_arm_ties():
    assert _batch(0.0, 20_000, 1).n_ties == 0


def test_conditional_batch_is_reproducible():
    a, b = _batch(0.25, 2000, 3), _batch(0.25, 2000, 3)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.mu_reuse, b.mu_reuse)
    assert np.array_equal(a.mu_fresh, b.mu_fresh)


# --------------------------------------------------------- the map estimator --

def test_map_estimator_applies_the_rebaselining_rule_pathwise():
    cfg = ConditionalConfig(e_values=(0.1,), n_paths_per_e=4000, m=1,
                            master_seed=5, n_batches=4,
                            rho_values=(0.0, 0.3, 1.0))
    rec = estimate_conditional_map(cfg)["records"][0]
    assert rec["F_rho_1"] == pytest.approx(rec["F1"], rel=1e-12)
    # rho = 0 discards the selected data entirely
    assert abs(rec["F_rho_0"]) < 5.0 * rec["F_rho_0_se"] + 1e-12


def test_rho_linearity_holds_within_monte_carlo_error():
    """F_rho = rho*F_1 is an elementary Level-2 identity; check the estimator."""
    cfg = ConditionalConfig(e_values=(-0.4, 0.4), n_paths_per_e=40_000, m=1,
                            master_seed=17, n_batches=8,
                            rho_values=(0.25, 0.5, 1.0))
    for rec in estimate_conditional_map(cfg)["records"]:
        for rho in (0.25, 0.5):
            predicted = rho * rec["F1"]
            observed = rec[f"F_rho_{rho:g}"]
            se = np.hypot(rec[f"F_rho_{rho:g}_se"], rho * rec["F1_se"])
            assert abs(observed - predicted) < 4.0 * se


def test_common_random_numbers_flag_controls_the_seed_key():
    shared = ConditionalConfig(e_values=(-0.1, 0.1), n_paths_per_e=100, m=1,
                               master_seed=1, n_batches=1,
                               common_random_numbers=True)
    keys = [r["seed_keys"] for r in estimate_conditional_map(shared)["records"]]
    assert keys[0] == keys[1]
    split = ConditionalConfig(e_values=(-0.1, 0.1), n_paths_per_e=100, m=1,
                              master_seed=1, n_batches=1,
                              common_random_numbers=False)
    keys = [r["seed_keys"] for r in estimate_conditional_map(split)["records"]]
    assert keys[0] != keys[1]


def test_map_estimate_is_odd_within_error():
    cfg = ConditionalConfig(e_values=(-0.3, 0.3), n_paths_per_e=60_000, m=1,
                            master_seed=23, n_batches=10,
                            common_random_numbers=False)
    a, b = estimate_conditional_map(cfg)["records"]
    asym = a["F1"] + b["F1"]
    assert abs(asym) < 4.0 * np.hypot(a["F1_se"], b["F1_se"])


def test_config_validation():
    with pytest.raises(ValueError):
        ConditionalConfig(e_values=(0.0,), n_paths_per_e=10, m=1, master_seed=1,
                          n_batches=3).validate()
    with pytest.raises(ValueError):
        ConditionalConfig(e_values=(0.0,), n_paths_per_e=10, m=1, master_seed=1,
                          n_batches=1, rho_values=(1.5,)).validate()
    with pytest.raises(ValueError):
        ConditionalConfig(e_values=(0.0,), n_paths_per_e=10, m=1, master_seed=1,
                          n_batches=1, k=0.4).validate()


# -------------------------------------------------------- score / LR routes --

def test_score_gamma_lands_inside_the_certified_enclosure():
    out = score_gamma(n_paths=120_000, m=1, master_seed=2026, n_batches=12)
    assert GAMMA_CERT_LOW < out["gamma"] < GAMMA_CERT_HIGH
    assert out["F1_prime_0"] == pytest.approx(1.0 - out["gamma"])
    # frozen diagnostic scale is ~15.8; ARL_0 is ~465
    assert out["gamma"] == pytest.approx(15.8, abs=0.6)
    assert out["arl_0"] == pytest.approx(465.0, rel=0.05)


def test_score_gamma_wald_second_identity():
    """E[T_tau^2] = E[tau] for the frozen driftless walk (Wald's 2nd identity)."""
    out = score_gamma(n_paths=120_000, m=1, master_seed=99, n_batches=12)
    assert abs(out["wald_second_gap"]) < 0.05 * out["arl_0"]


def test_score_gamma_independent_seeds_agree():
    a = score_gamma(n_paths=100_000, m=1, master_seed=11, n_batches=10,
                    seed_replicate=0)
    b = score_gamma(n_paths=100_000, m=1, master_seed=11, n_batches=10,
                    seed_replicate=1)
    assert a["gamma"] != b["gamma"]
    assert abs(a["gamma"] - b["gamma"]) < 4.0 * np.hypot(a["gamma_se"],
                                                         b["gamma_se"])


def test_lr_map_agrees_with_direct_simulation_near_zero():
    e_values = (-0.05, 0.0, 0.05)
    lr = lr_map(e_values, n_paths=120_000, m=1, master_seed=31, n_batches=12)
    direct = estimate_conditional_map(ConditionalConfig(
        e_values=e_values, n_paths_per_e=120_000, m=1, master_seed=32,
        n_batches=12, common_random_numbers=False))
    for a, b in zip(lr["records"], direct["records"]):
        assert a["e"] == b["e"]
        se = np.hypot(a["F1_lr_se"], b["F1_se"])
        assert abs(a["F1_lr"] - b["F1"]) < 4.0 * se
    assert lr["records"][1]["ess_fraction"] == pytest.approx(1.0)


# ---------------------------------------------------------- analysis layer --

def test_odd_polynomial_fit_recovers_known_coefficients():
    e = np.linspace(-0.1, 0.1, 21)
    e = e[np.abs(e) > 1e-12]
    truth = -14.0 * e + 300.0 * e ** 3
    se = np.full(e.size, 1e-4)
    rng = np.random.default_rng(4)
    fit = analysis.odd_polynomial_fit(e, truth + rng.normal(0, 1e-4, e.size), se,
                                      max_abs_e=0.1, n_terms=3)
    assert fit["derivative_at_zero"] == pytest.approx(-14.0, abs=0.05)
    assert fit["coefficients"][1] == pytest.approx(300.0, rel=0.15)
    assert fit["chi2_per_dof"] < 3.0


def test_odd_polynomial_fit_needs_enough_points():
    e = np.array([-0.1, 0.1])
    with pytest.raises(ValueError):
        analysis.odd_polynomial_fit(e, e, np.ones(2), max_abs_e=0.2, n_terms=3)


def test_central_difference_scan_exhibits_the_delta_squared_law():
    a1, a3 = -14.0, 300.0
    deltas = [0.2, 0.1, 0.05]
    e = np.array([-d for d in deltas] + [0.0] + deltas)
    f = a1 * e + a3 * e ** 3
    scan = analysis.central_difference_scan(e, f, np.zeros(e.size), deltas)
    for row in scan:
        assert row["D"] == pytest.approx(a1 + a3 * row["delta"] ** 2, rel=1e-9)


def test_local_derivative_is_exact_on_a_quadratic():
    """The local model IS a quadratic, so recovery must be exact there."""
    e = np.linspace(-1.0, 1.0, 41)
    f = 3.0 - 2.0 * e + 5.0 * e ** 2
    out = analysis.local_derivative(e, f, np.full(e.size, 1e-6), half_window=3)
    good = np.isfinite(out["derivative"])
    assert np.allclose(out["derivative"][good], -2.0 + 10.0 * out["e"][good],
                       atol=1e-8)


def test_local_derivative_truncation_shrinks_with_the_window():
    """On a non-quadratic function the local fit carries an O(h^2) bias.

    This is expected, not a defect: the test pins the *scaling* so that any
    reported derivative can be checked against its own window size.
    """
    e = np.linspace(-1.0, 1.0, 201)
    f = np.sin(2.0 * e)
    truth = 2.0 * np.cos(2.0 * e)
    errors = []
    for half_window in (12, 6, 3):
        out = analysis.local_derivative(e, f, np.full(e.size, 1e-6),
                                        half_window=half_window)
        mid = np.abs(out["e"]) < 0.5
        errors.append(np.max(np.abs(out["derivative"][mid] - truth[mid])))
    assert errors[0] > errors[1] > errors[2]
    assert errors[2] < 1e-3
    # halving the window should cut the error by roughly four
    assert 2.5 < errors[0] / errors[1] < 6.0


def test_symmetry_diagnostics_flags_a_broken_symmetry():
    e = np.array([-0.5, -0.25, 0.25, 0.5])
    odd = np.array([1.0, 0.5, -0.5, -1.0])
    se = np.full(4, 0.01)
    clean = analysis.symmetry_diagnostics(e, odd, se)
    assert clean["n_pairs"] == 2
    assert clean["max_abs_z"] == pytest.approx(0.0)
    broken = analysis.symmetry_diagnostics(e, odd + np.array([0, 0, 0.2, 0]), se)
    assert broken["max_abs_z"] > 10.0


def test_find_h_roots_locates_a_known_crossing():
    """H(e) = F(e) + e with F(e) = -2e + e^3 has roots at 0 and +/-1."""
    e = np.linspace(-2.0, 2.0, 81)
    f = -2.0 * e + e ** 3
    roots = analysis.find_h_roots(e, f, np.full(e.size, 1e-9), rho=1.0)
    assert len(roots) == 1
    assert roots[0].e_star == pytest.approx(1.0, abs=0.01)


def test_find_h_roots_returns_nothing_when_the_fixed_point_is_stable():
    e = np.linspace(-2.0, 2.0, 81)
    f = -0.5 * e            # |F'| < 1, H = 0.5e has no nonzero root
    assert analysis.find_h_roots(e, f, np.full(e.size, 1e-9), rho=1.0) == []


def test_two_cycle_multiplier_is_the_squared_slope():
    e = np.linspace(-2.0, 2.0, 161)
    f = -2.0 * e + e ** 3
    deriv = analysis.local_derivative(e, f, np.full(e.size, 1e-9), half_window=3)
    root = analysis.find_h_roots(e, f, np.full(e.size, 1e-9), rho=1.0,
                                 derivative=deriv)[0]
    # F'(1) = -2 + 3 = 1  ->  multiplier = 1
    assert root.derivative == pytest.approx(1.0, abs=0.02)
    assert root.multiplier == pytest.approx(root.derivative ** 2)


def test_classify_candidate_labels():
    base = analysis.RootCandidate(
        rho=1.0, e_star=0.5, e_star_se=0.002, bracket=(0.49, 0.51),
        h_residual=0.0, h_residual_se=0.001, derivative=-0.3,
        derivative_se=0.01, multiplier=0.09, multiplier_se=0.006,
        classification="UNCLASSIFIED", notes=[])
    strong = analysis.classify_candidate(
        base, h_residual_direct=0.0004, h_residual_direct_se=0.001,
        symmetry_z=0.4, grid_sensitivity=0.001, mc_sensitivity=0.001,
        seed_replication_delta=0.002)
    assert strong.classification == "STRONG-CANDIDATE"
    weak = analysis.classify_candidate(
        base, h_residual_direct=0.0004, h_residual_direct_se=0.001,
        symmetry_z=0.4, grid_sensitivity=0.001, mc_sensitivity=None,
        seed_replication_delta=0.002)
    assert weak.classification == "WEAK-CANDIDATE"
    bad = analysis.classify_candidate(
        base, h_residual_direct=0.02, h_residual_direct_se=0.001,
        symmetry_z=0.4, grid_sensitivity=0.001, mc_sensitivity=0.001,
        seed_replication_delta=0.002)
    assert bad.classification == "NUMERICALLY-INCONSISTENT"
    unsymmetric = analysis.classify_candidate(
        base, h_residual_direct=0.0, h_residual_direct_se=0.001,
        symmetry_z=9.0, grid_sensitivity=0.001, mc_sensitivity=0.001,
        seed_replication_delta=0.001)
    assert unsymmetric.classification == "NUMERICALLY-INCONSISTENT"


def test_critical_rho_arithmetic():
    out = analysis.critical_rho(-14.7545, 0.0896)
    assert out["rho_c"] == pytest.approx(1.0 / 14.7545)
    assert out["rho_c_se"] == pytest.approx(0.0896 / 14.7545 ** 2)
    assert out["rho_c_ci95"][0] < out["rho_c"] < out["rho_c_ci95"][1]


def test_rho_c_from_certified_gamma_interval():
    out = analysis.rho_c_from_gamma_interval(GAMMA_CERT_LOW, GAMMA_CERT_HIGH)
    lo, hi = out["rho_c_enclosure"]
    assert lo == pytest.approx(1.0 / (GAMMA_CERT_HIGH - 1.0))
    assert hi == pytest.approx(1.0 / (GAMMA_CERT_LOW - 1.0))
    assert 0.0 < lo < hi < 1.0
    with pytest.raises(ValueError):
        analysis.rho_c_from_gamma_interval(0.5, 2.0)


# ------------------------------------------------- H-crossing significance --

def test_noise_only_sign_change_near_zero_is_screened_out():
    """For rho below rho_c, H_rho(e) ~ (1-rho|F'|)e is tiny near 0.

    Monte Carlo noise then manufactures sign changes there.  The screen must
    reject them, because accepting one would invent a period-2 candidate in
    exactly the regime where theory says the fixed point is locally stable.
    """
    e = np.linspace(-0.3, 0.3, 25)
    rng = np.random.default_rng(2)
    se = np.full(e.size, 0.05)
    f = -0.5 * e + rng.normal(0.0, 0.05, e.size)   # H = 0.5e, no true root
    screened = analysis.find_h_crossings(e, f, se, rho=1.0)
    assert screened["accepted"] == []
    for entry in screened["rejected"]:
        assert "need 3.0z" in entry["reason"]
        assert entry["left_support_z"] < 3.0 or entry["right_support_z"] < 3.0


def test_genuine_crossing_survives_the_screen_with_the_same_noise():
    e = np.linspace(-2.0, 2.0, 41)
    rng = np.random.default_rng(2)
    se = np.full(e.size, 0.05)
    f = -2.0 * e + e ** 3 + rng.normal(0.0, 0.05, e.size)
    accepted = analysis.find_h_crossings(e, f, se, rho=1.0)["accepted"]
    assert len(accepted) == 1
    assert accepted[0].e_star == pytest.approx(1.0, abs=0.05)


def test_screen_reports_rejections_rather_than_dropping_them():
    e = np.array([-0.3, -0.2, -0.1, 0.1, 0.2, 0.3])
    h = np.array([-0.05, 0.05, -0.05, 0.05, -0.05, 0.05])   # sign flips, tiny
    out = analysis.find_h_crossings(e, h - e, np.full(6, 1.0), rho=1.0)
    assert out["accepted"] == []
    assert len(out["rejected"]) >= 1
    assert "reason" in out["rejected"][0]
    assert out["rejected"][0]["left_support_z"] < 3.0


def test_min_z_threshold_is_honoured():
    e = np.linspace(-2.0, 2.0, 41)
    f = -2.0 * e + e ** 3
    # |H| peaks at only ~0.385 on the inner branch, so the error bar has to be
    # small enough for that branch to carry support at all.
    se = np.full(e.size, 0.05)
    assert analysis.find_h_crossings(e, f, se, rho=1.0, min_z=3.0)["accepted"]
    assert not analysis.find_h_crossings(e, f, se, rho=1.0,
                                         min_z=1e6)["accepted"]


def test_grid_point_landing_exactly_on_the_root_is_handled():
    e = np.linspace(-2.0, 2.0, 81)               # contains e = 1.0 exactly
    f = -2.0 * e + e ** 3
    assert np.any(np.isclose(e, 1.0))
    accepted = analysis.find_h_crossings(e, f, np.full(e.size, 1e-9),
                                         rho=1.0)["accepted"]
    assert len(accepted) == 1
    assert accepted[0].e_star == pytest.approx(1.0, abs=1e-6)


# ------------------------------------- batch-level fitting / order selection --

def _synthetic_batches(a1=-14.8, a3=330.0, a5=-4600.0, n_batches=20,
                       noise=2e-4, seed=5):
    e = np.array(sorted({0.0, *[0.0125 * i for i in range(1, 13)],
                         *[-0.0125 * i for i in range(1, 13)]}))
    truth = a1 * e + a3 * e ** 3 + a5 * e ** 5
    rng = np.random.default_rng(seed)
    batches = truth + rng.normal(0.0, noise, (n_batches, e.size))
    se = np.full(e.size, noise / np.sqrt(n_batches))
    return e, batches, se, truth


def test_batched_fit_recovers_the_slope_and_its_own_uncertainty():
    e, batches, se, _ = _synthetic_batches()
    fit = analysis.odd_polynomial_fit_batched(e, batches, max_abs_e=0.15,
                                              n_terms=3)
    assert fit["derivative_at_zero"] == pytest.approx(-14.8, abs=0.05)
    assert fit["n_batches"] == 20
    assert len(fit["per_batch_a1"]) == 20
    lo, hi = fit["derivative_at_zero_ci95"]
    assert lo < -14.8 < hi


def test_batched_fit_uncertainty_shrinks_with_more_batches():
    _, _, _, _ = _synthetic_batches()
    small = analysis.odd_polynomial_fit_batched(
        *_synthetic_batches(n_batches=10)[:2], max_abs_e=0.15, n_terms=3)
    large = analysis.odd_polynomial_fit_batched(
        *_synthetic_batches(n_batches=160)[:2], max_abs_e=0.15, n_terms=3)
    assert large["derivative_at_zero_se"] < small["derivative_at_zero_se"]


def test_batched_fit_rejects_ill_conditioned_designs():
    e, batches, _, _ = _synthetic_batches()
    with pytest.raises((ValueError, np.linalg.LinAlgError)):
        analysis.odd_polynomial_fit_batched(e, batches, max_abs_e=0.03,
                                            n_terms=6)


def test_order_selection_rejects_an_underspecified_order():
    """A degree-5 truth must not be fitted with only two odd terms."""
    e, batches, se, _ = _synthetic_batches(noise=5e-5)
    out = analysis.select_derivative_fit(e, batches, se,
                                         windows=[0.1, 0.125, 0.15])
    assert out["selected"] is not None
    assert out["selected"]["n_terms"] >= 3
    assert out["selected"]["derivative_at_zero"] == pytest.approx(-14.8, abs=0.1)
    two_term_wide = [f for f in out["scan"]
                     if f["n_terms"] == 2 and f["max_abs_e"] == 0.15]
    assert two_term_wide and not two_term_wide[0]["converged"]


def test_order_selection_reports_every_fit_it_considered():
    e, batches, se, _ = _synthetic_batches()
    out = analysis.select_derivative_fit(e, batches, se, windows=[0.1, 0.15],
                                         max_terms=4)
    assert len(out["scan"]) >= 4
    for fit in out["scan"]:
        assert {"max_abs_e", "n_terms", "derivative_at_zero",
                "derivative_at_zero_se", "converged"} <= set(fit)
    assert "rule" in out and str(out["max_terms"]) in "12345"


def test_order_selection_returns_none_when_nothing_converges():
    e, batches, se, _ = _synthetic_batches(noise=1e-9)
    out = analysis.select_derivative_fit(e, batches, se, windows=[0.15],
                                         max_terms=4, tolerance_se=0.0)
    assert out["selected"] is None
    assert out["n_converged"] == 0


def test_batched_and_pooled_fits_agree_on_the_point_estimate():
    """They differ in how uncertainty is computed, not in what they estimate."""
    e, batches, se, _ = _synthetic_batches()
    batched = analysis.odd_polynomial_fit_batched(e, batches, max_abs_e=0.15,
                                                  n_terms=3)
    pooled = analysis.odd_polynomial_fit(e, batches.mean(axis=0), se,
                                         max_abs_e=0.15, n_terms=3)
    assert batched["derivative_at_zero"] == pytest.approx(
        pooled["derivative_at_zero"], abs=0.01)


def test_fresh_statistic_is_mean_zero_and_uncorrelated_with_selection():
    """The assumption underneath the Level-2 identity F_rho = rho*F_1.

    ``F_rho = rho F_1`` holds because ``mu_fresh`` has mean zero and is
    independent of the stopping event.  The rho-scan in the Gate 4.2 report
    cannot test this — the odd polynomial basis annihilates the e-independent
    fresh term identically — so it is tested here instead.
    """
    for e in (0.0, 0.25, 1.0):
        batch = _batch(e, 200_000, 1, seed=4242)
        n = batch.mu_fresh.size
        mean_se = float(batch.mu_fresh.std(ddof=1) / np.sqrt(n))
        assert abs(batch.mu_fresh.mean()) < 4.0 * mean_se
        # independence of the stopping event: no correlation with anything the
        # stopping rule selected
        for name, selected in (("mu_reuse", batch.mu_reuse),
                               ("tau", batch.tau.astype(float)),
                               ("direction", batch.direction.astype(float)),
                               ("t_tau", batch.t_tau)):
            if selected.std() == 0.0:
                # Degenerate, not a failure: at e = 1 the reference offset is
                # large enough that every alarm fires on the down arm, so the
                # direction series is constant and has no correlation to test.
                continue
            r = float(np.corrcoef(batch.mu_fresh, selected)[0, 1])
            assert abs(r) < 5.0 / np.sqrt(n), (e, name, r)


def test_fresh_statistic_variance_matches_the_m_convention():
    """mu_fresh must have variance 1/m, the matched-information variance."""
    for m in (1, 5, 20):
        batch = _batch(0.0, 100_000, m, seed=99)
        assert batch.mu_fresh.std(ddof=1) == pytest.approx(1.0 / np.sqrt(m),
                                                           rel=0.02)
