"""Metric definitions and the estimand arithmetic."""
import numpy as np
import pytest

from rebaseguard_p8.analysis import (Z95, bh_fdr, cochran_q, combined_z,
                                     p7_boundary_rates, rho_c_from_gamma,
                                     spread)
from rebaseguard_p8.chain import simulate_chain
from rebaseguard_p8.stopped import simulate_row_block

EXP = "unit_test"


def test_rho_c_formula_and_regimes():
    r = rho_c_from_gamma(15.9165, 0.0599)
    assert abs(r["rho_c"] - 1.0 / (15.9165 - 1.0)) < 1e-12
    assert r["regime"] == "GAMMA_GT_2"
    assert r["accessible_in_admissible_domain"] and r["lower_bound_exceeds_2"]
    assert rho_c_from_gamma(1.5, 0.01)["regime"] == "GAMMA_BETWEEN_1_AND_2"
    assert rho_c_from_gamma(0.5, 0.01)["regime"] == "GAMMA_BETWEEN_0_AND_1"
    assert rho_c_from_gamma(-1.0, 0.01)["regime"] == "GAMMA_LT_0"
    assert rho_c_from_gamma(2.0, 0.01)["regime"] == "GAMMA_EQ_2"


def test_rho_c_uses_the_absolute_value_form_not_the_gt1_shortcut():
    """P3 THEOREM section 5: rho_c = 1/|1-Gamma| in every regime."""
    for g in (-2.0, 0.0, 0.4, 1.7, 3.0, 20.0):
        r = rho_c_from_gamma(g, 1e-9)
        assert abs(r["rho_c"] - 1.0 / abs(1.0 - g)) < 1e-6


def test_rho_c_interval_is_the_exact_monotone_image():
    r = rho_c_from_gamma(1.02, 0.05)          # CI straddles Gamma = 1
    assert r["rho_c_interval"][1] is None     # d can be 0 -> rho_c unbounded


def test_p3_exact_witness_values_round_trip():
    """P3's EXACT_SYMBOLIC finite-support witnesses, as a regression anchor."""
    for gamma, rho_c in ((7.5, 2 / 13), (4.0, 1 / 3), (3.0, 0.5),
                         (8 / 3, 0.6), (12 / 5, 5 / 7)):
        assert abs(rho_c_from_gamma(gamma, 0.0)["rho_c"] - rho_c) < 1e-12


def test_combined_z_and_spread():
    assert combined_z(1.0, 0.0, 1.0, 0.0) == float("inf")
    assert abs(combined_z(2.0, 0.3, 1.0, 0.4) - 1.0 / 0.5) < 1e-12
    assert abs(spread([1.0, 1.1]) - 0.1) < 1e-12
    assert spread([0.0, 1.0]) == float("inf")


def test_p7_boundary_rate_matches_the_frozen_definition():
    """Restated verbatim from p7/experiments/make_report.py::boundary_verdict."""
    ladder = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)
    ys = np.array([100.0, 90.0, 80.0, 20.0, 19.0, 18.0, 17.0, 16.0])
    out = p7_boundary_rates(ladder, ys, "arl")
    assert out["peaks_at_boundary"] is True
    assert out["argmax_bracket"] == "0.8-1.0"
    xs = np.log(np.array(ladder))
    expected = abs(np.diff(np.log(np.abs(ys)))[2] / np.diff(xs)[2])
    assert abs(out["boundary_rate"] - expected) < 1e-12


def test_p7_boundary_rate_requires_the_boundary_brackets():
    with pytest.raises(ValueError):
        p7_boundary_rates((0.25, 0.5, 2.0), [1.0, 2.0, 3.0], "arl")


def test_cochran_q_is_zero_for_identical_values():
    q = cochran_q(np.array([2.0, 2.0, 2.0]), np.array([0.1, 0.2, 0.3]))
    assert q["Q"] == 0.0 and q["df"] == 2 and q["I2"] == 0.0


def test_bh_fdr():
    assert bh_fdr([0.001, 0.5, 0.9], 0.10).tolist() == [True, False, False]
    assert bh_fdr([0.9, 0.9, 0.9], 0.10).tolist() == [False, False, False]


def test_gamma_A_at_m1_equals_the_lag0_estimand():
    s = simulate_row_block(experiment=EXP, family="t10", detector="cusum",
                           threshold=5.234517732360302, batch=0, row_block=0,
                           n_paths=2048)
    assert np.allclose((s.zbar(1) * s.Psi), (s.lag_z[:, 0] * s.Psi))


def test_lag_decomposition_identity_holds_pathwise():
    """P8-L1(b): Gamma_A(m) = mean_r gamma_r + R_m, exactly, per sample."""
    s = simulate_row_block(experiment=EXP, family="contam0.05", detector="cusum",
                           threshold=7.671712168173407, batch=1, row_block=0,
                           n_paths=4096)
    for m in (1, 2, 3, 5, 10, 20):
        gA = float((s.zbar(m, "A") * s.Psi).mean())
        lag = np.mean([float((s.lag_z[:, r] * s.valid[:, r] * s.Psi).mean())
                       for r in range(m)])
        trunc = s.tau < m
        Rm = float(np.where(trunc, (1.0 / np.maximum(s.tau, 1) - 1.0 / m)
                            * s.T * s.Psi, 0.0).mean())
        assert abs(gA - lag - Rm) < 1e-9 * max(1.0, abs(gA))


def test_convention_difference_equals_the_truncation_remainder():
    s = simulate_row_block(experiment=EXP, family="gaussian", detector="cusum",
                           threshold=5.0, batch=1, row_block=0, n_paths=4096)
    for m in (1, 5, 20):
        gA = float((s.zbar(m, "A") * s.Psi).mean())
        gB = float((s.zbar(m, "B") * s.Psi).mean())
        trunc = s.tau < m
        Rm = float(np.where(trunc, (1.0 / np.maximum(s.tau, 1) - 1.0 / m)
                            * s.T * s.Psi, 0.0).mean())
        assert abs((gA - gB) - Rm) < 1e-12


def test_chain_metric_definitions():
    r = simulate_chain(experiment=EXP, family="gaussian", detector="cusum",
                       threshold=5.0, m=1, rho=0.5, n_rep=64, n_cycles=10,
                       burn_in=3)
    assert np.allclose(r.per_replicate_arl, r.tau[:, 3:].mean(axis=1))
    assert np.allclose(r.per_replicate_ref_mse, (r.e_start[:, 3:] ** 2).mean(axis=1))
    assert np.allclose(r.per_replicate_fap(100), (r.tau[:, 3:] <= 100).mean(axis=1))
    assert r.per_replicate_acf1.shape == (64,)
    assert np.all(np.abs(r.per_replicate_acf1) <= 1.0 + 1e-12)


def test_burn_in_is_actually_dropped():
    r = simulate_chain(experiment=EXP, family="gaussian", detector="cusum",
                       threshold=5.0, m=1, rho=0.0, n_rep=8, n_cycles=6,
                       burn_in=4)
    assert r.post(r.tau).shape == (8, 2)


def test_z95_constant():
    from scipy import stats
    assert abs(Z95 - stats.norm.ppf(0.975)) < 1e-12


# --- exact anchors for the estimator itself -------------------------------
@pytest.mark.parametrize("name", ["gaussian", "t10", "t5", "contam0.05",
                                  "contam0.1"])
def test_degenerate_detector_recovers_the_exact_unit_diagonal(name):
    """A detector with threshold 0 alarms at tau = 1 on every path.

    Then ``zbar^A_m = z_1`` for every ``m``, so
    ``Gamma_A(m) = E[z psi(z)] = 1`` EXACTLY for every family and every window
    (P8-L1(a)).  This anchors the whole estimator -- score evaluation, lag
    buffer, window extraction, accumulation -- against a value known in closed
    form, with no reference to any historical artifact.
    """
    s = simulate_row_block(experiment=EXP, family=name, detector="cusum",
                           threshold=0.0, batch=4, row_block=0, n_paths=4096)
    assert (s.tau == 1).all()
    for m in (1, 3, 20):
        g = float((s.zbar(m, "A") * s.Psi).mean())
        se = float((s.zbar(m, "A") * s.Psi).std(ddof=1) / np.sqrt(s.tau.size))
        assert abs(g - 1.0) < 5.0 * se + 1e-9


@pytest.mark.parametrize("m", [2, 5, 20])
def test_degenerate_detector_gives_the_exact_truncation_remainder(m):
    """With tau = 1 always, R_m = (1 - 1/m) E[z psi(z)] and Gamma_B = Gamma_A/m."""
    s = simulate_row_block(experiment=EXP, family="t5", detector="cusum",
                           threshold=0.0, batch=4, row_block=0, n_paths=4096)
    gA = float((s.zbar(m, "A") * s.Psi).mean())
    gB = float((s.zbar(m, "B") * s.Psi).mean())
    assert abs(gB - gA / m) < 1e-12
    Rm = float(np.where(s.tau < m, (1.0 / np.maximum(s.tau, 1) - 1.0 / m)
                        * s.T * s.Psi, 0.0).mean())
    assert abs((gA - gB) - Rm) < 1e-12
    assert abs(Rm - (1.0 - 1.0 / m) * gA) < 1e-12
