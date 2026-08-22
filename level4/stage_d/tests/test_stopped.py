"""Stage D core tests: frozen correspondence, conventions, detector semantics."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level4" / "src"))

from stopped import CUSUM, SR, simulate_stopped, run_batches   # noqa: E402
from rebaseguard_level4.frozen import H_FROZEN, K_FROZEN       # noqa: E402


def _rng(*key):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key))))


# --------------------------------------------------------------- frozen model
def test_frozen_constants_unchanged():
    assert K_FROZEN == 0.5 and H_FROZEN == 5.0


def test_cusum_arl0_matches_frozen_level13_value():
    """The frozen CUSUM(k=1/2, h=5) in-control ARL0 is ~465; a drift here means
    Stage D is no longer simulating the frozen detector."""
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=200_000, L=2, m_grid=np.array([1]),
                         rng=_rng(20261031, 0))
    assert abs(s.arl - 465.0) < 5.0, s.arl


def test_gamma_1_matches_frozen_certified_enclosure():
    """Gamma at m=1 must land inside the Level 1-3 certified Arb enclosure."""
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=200_000, L=2, m_grid=np.array([1]),
                         rng=_rng(20261031, 0))
    g = s.gamma_m("A")[0]
    assert 3.9243482 < g < 27.8493821, g


def test_wald_second_identity():
    """Sum_i gamma_i = E[T_tau^2] = ARL0 for the frozen zero-drift CUSUM."""
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=200_000, L=600, m_grid=np.array([1]),
                         rng=_rng(20261031, 1))
    assert abs(s.E_T_sq / s.arl - 1.0) < 0.02, (s.E_T_sq, s.arl)


# ------------------------------------------------------- window conventions
def test_conventions_agree_at_m_equals_1():
    """w = min(1, tau) = 1 = m whenever tau >= 1, so A and B coincide at m=1."""
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=20_000, L=4, m_grid=np.array([1, 2, 5]),
                         rng=_rng(20261031, 2))
    a, b = s.gamma_m("A"), s.gamma_m("B")
    assert a[0] == pytest.approx(b[0], rel=1e-12)


def test_conventions_diverge_once_m_can_exceed_tau():
    """A and B are genuinely different statistics; B <= A because B keeps the
    larger denominator m on the P(tau < m) paths."""
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=100_000, L=300, m_grid=np.array([1, 50, 250]),
                         rng=_rng(20261031, 3))
    a, b = s.gamma_m("A"), s.gamma_m("B")
    assert b[2] < a[2], (a[2], b[2])


def test_convention_B_equals_lag_average_by_construction():
    """Gamma_m^B = (1/m) sum_{i<m} gamma_i is an algebraic identity for B."""
    m = 40
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=50_000, L=m, m_grid=np.array([m]),
                         rng=_rng(20261031, 4))
    assert s.gamma_m("B")[0] == pytest.approx(s.gamma_lag[:m].mean(), rel=1e-10)


def test_convention_A_is_not_the_lag_average():
    """The blueprint's closed form does NOT hold for the frozen convention A.
    This test pins the refutation so it cannot be quietly reversed."""
    m = 250
    s = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.0,
                         n_paths=100_000, L=m, m_grid=np.array([m]),
                         rng=_rng(20261031, 5))
    a = s.gamma_m("A")[0]
    lag_avg = s.gamma_lag[:m].mean()
    se = s.gamma_m_se("A")[0]
    assert abs(a - lag_avg) > 20.0 * se, (a, lag_avg, se)


# --------------------------------------------------------- detector semantics
def test_sr_threshold_is_natural_units_not_log():
    """REGRESSION: `_sr_update` compares against log(A). A caller passing A was
    silently getting threshold e^A, so no path ever alarmed. The threshold is
    now logged exactly once, inside `simulate_stopped`."""
    s = simulate_stopped(detector=SR, threshold=520.3125, e=0.0,
                         n_paths=20_000, L=2, m_grid=np.array([1]),
                         rng=_rng(20261031, 6))
    assert 350.0 < s.arl < 650.0, s.arl


def test_sr_rejects_a_degenerate_threshold():
    """The units guard catches A <= 1, i.e. a log-scale value for any A < e.

    LIMITATION, stated rather than papered over: no numeric guard can separate
    A = 6.25 from log(520.3) = 6.25, because both are legal SR thresholds. The
    real protection is that `threshold` is documented as natural units and is
    logged exactly once inside `simulate_stopped`, and that
    `test_sr_threshold_is_natural_units_not_log` pins the resulting ARL0."""
    with pytest.raises(ValueError, match="NATURAL units"):
        simulate_stopped(detector=SR, threshold=0.5, e=0.0, n_paths=10,
                         L=2, m_grid=np.array([1]), rng=_rng(20261031, 7))


def test_sr_arl0_increases_with_threshold():
    arls = [simulate_stopped(detector=SR, threshold=A, e=0.0, n_paths=20_000,
                             L=2, m_grid=np.array([1]), rng=_rng(20261031, 8)).arl
            for A in (100.0, 520.3125, 2000.0)]
    assert arls[0] < arls[1] < arls[2], arls


# ------------------------------------------------------------- reproducibility
def test_batching_is_deterministic_given_the_seed():
    kw = dict(detector=CUSUM, threshold=H_FROZEN, e=0.0, n_paths=40_000,
              L=8, m_grid=np.array([1, 5]))
    a = run_batches(batch=10_000, seed_seq=np.random.SeedSequence([20261031, 9]), **kw)
    b = run_batches(batch=10_000, seed_seq=np.random.SeedSequence([20261031, 9]), **kw)
    assert a.arl == b.arl
    assert np.array_equal(a.gamma_m("A"), b.gamma_m("A"))


def test_batch_size_does_not_change_the_estimand():
    """Different batch sizes give different draws, but the same estimand to
    within Monte Carlo error -- this catches accumulator bugs in `combine`."""
    kw = dict(detector=CUSUM, threshold=H_FROZEN, e=0.0, n_paths=200_000,
              L=8, m_grid=np.array([1, 5]))
    a = run_batches(batch=20_000, seed_seq=np.random.SeedSequence([20261031, 10]), **kw)
    b = run_batches(batch=200_000, seed_seq=np.random.SeedSequence([20261031, 11]), **kw)
    assert a.n == b.n == 200_000
    se = np.hypot(a.gamma_m_se("A"), b.gamma_m_se("A"))
    assert np.all(np.abs(a.gamma_m("A") - b.gamma_m("A")) < 4.0 * se)


def test_odd_symmetry_of_arl_in_e():
    """The frozen two-sided detector is symmetric: ARL(e) = ARL(-e)."""
    p = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=0.6, n_paths=100_000,
                         L=2, m_grid=np.array([1]), rng=_rng(20261031, 12))
    n = simulate_stopped(detector=CUSUM, threshold=H_FROZEN, e=-0.6, n_paths=100_000,
                         L=2, m_grid=np.array([1]), rng=_rng(20261031, 13))
    assert abs(p.arl - n.arl) / p.arl < 0.05, (p.arl, n.arl)


def test_score_hook_identity_reproduces_gamma_bit_for_bit():
    """The D3 score hook must be inert for the Gaussian: with psi = identity,
    gamma_psi equals gamma_m exactly, and the raw path is untouched."""
    mg = np.array([1, 5, 20])
    kw = dict(detector=CUSUM, threshold=H_FROZEN, e=0.0, n_paths=50_000,
              L=20, m_grid=mg)
    a = simulate_stopped(rng=_rng(20261031, 40), **kw)
    b = simulate_stopped(rng=_rng(20261031, 40), score=lambda x: x, **kw)
    assert np.array_equal(a.gamma_m("A"), b.gamma_psi())
    assert np.array_equal(a.gamma_m("A"), b.gamma_m("A"))


def test_score_hook_changes_the_estimand_for_a_nonlinear_score():
    mg = np.array([1])
    kw = dict(detector=CUSUM, threshold=H_FROZEN, e=0.0, n_paths=50_000,
              L=2, m_grid=mg)
    b = simulate_stopped(rng=_rng(20261031, 41),
                         score=lambda x: np.tanh(x), **kw)
    assert not np.allclose(b.gamma_psi(), b.gamma_m("A"))
