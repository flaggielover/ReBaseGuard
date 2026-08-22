"""Regression protection: Level 4 must reproduce the frozen single-cycle semantics.

Every test here compares against ``rebaseguard_certify.model`` -- the frozen
Level 1-3 implementation -- or against the naive scalar reference.  A failure
means the Level 4 code has drifted from the immutable model, not that the model
needs updating.
"""

from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_certify import model as frozen_model
from rebaseguard_level4.frozen import (
    ALARM_DOWN,
    ALARM_NONE,
    ALARM_UP,
    H_FROZEN,
    K_FROZEN,
    alarm_direction,
    count_ties,
    cusum_update,
    fresh_statistic_scale,
    rebaseline,
    step_scalar,
)
from rebaseguard_level4.multicycle import MultiCycleConfig, simulate_multicycle
from rebaseguard_level4.reference import replay_replicate_scalar
from rebaseguard_level4.streams import STREAM_OBS, PerRowStream, generator

ALARM_MAP = {
    frozen_model.Alarm.CONTINUE: ALARM_NONE,
    frozen_model.Alarm.UP: ALARM_UP,
    frozen_model.Alarm.DOWN: ALARM_DOWN,
}


# ---------------------------------------------------------------- constants --

def test_frozen_constants_match_closure_document():
    assert K_FROZEN == 0.5
    assert H_FROZEN == 5.0


# ------------------------------------------------------- detector recurrence --

@pytest.mark.parametrize("plus", [0.0, 0.3, 1.7, 4.4, 4.999])
@pytest.mark.parametrize("minus", [0.0, 0.9, 3.2, 4.999])
@pytest.mark.parametrize("z", [-6.0, -1.25, -0.5, 0.0, 0.5, 1.25, 5.5, 6.0])
def test_step_scalar_matches_frozen_model_step(plus, minus, z):
    got = step_scalar(plus, minus, z)
    want = frozen_model.step(frozen_model.State(plus, minus), z, K_FROZEN, H_FROZEN)
    assert got[0] == want.state.plus
    assert got[1] == want.state.minus
    assert got[2] == ALARM_MAP[want.alarm]


def test_vectorised_update_matches_scalar_step():
    rng = np.random.default_rng(20260820)
    plus = rng.uniform(0.0, 4.99, 5000)
    minus = rng.uniform(0.0, 4.99, 5000)
    z = rng.normal(0.0, 3.0, 5000)
    vp, vm, up, down = cusum_update(plus, minus, z, K_FROZEN, H_FROZEN)
    for i in range(5000):
        sp, sm, alarm = step_scalar(plus[i], minus[i], z[i])
        assert vp[i] == sp and vm[i] == sm
        expected = ALARM_UP if up[i] else (ALARM_DOWN if down[i] else ALARM_NONE)
        assert expected == alarm


def test_shared_innovation_drives_both_arms():
    """The two arms must see the same Z_t with opposite sign, not two draws."""
    plus, minus, _ = step_scalar(0.0, 0.0, 2.0)
    assert plus == pytest.approx(1.5)
    assert minus == 0.0
    plus, minus, _ = step_scalar(0.0, 0.0, -2.0)
    assert plus == 0.0
    assert minus == pytest.approx(1.5)


# ----------------------------------------------------- boundary / timing case --

def test_threshold_equality_is_an_alarm():
    """Exactly reaching h fires: the boundary is inclusive (>=, not >)."""
    # from (0,0) a single z = h + k lands S+ exactly on h
    plus, _, alarm = step_scalar(0.0, 0.0, H_FROZEN + K_FROZEN)
    assert plus == pytest.approx(H_FROZEN)
    assert alarm == ALARM_UP
    _, minus, alarm = step_scalar(0.0, 0.0, -(H_FROZEN + K_FROZEN))
    assert minus == pytest.approx(H_FROZEN)
    assert alarm == ALARM_DOWN


def test_just_below_threshold_does_not_alarm():
    plus, _, alarm = step_scalar(0.0, 0.0, H_FROZEN + K_FROZEN - 1e-12)
    assert plus < H_FROZEN
    assert alarm == ALARM_NONE


def test_alarm_is_tested_after_the_update_not_before():
    """A pre-update state at h does not alarm if the update pushes it below h."""
    # start just under h on the plus arm, then a large negative step
    plus, _, alarm = step_scalar(4.9, 0.0, -10.0)
    assert alarm != ALARM_UP
    # and a state already at h only fires because the *post*-update value is >= h
    plus, _, alarm = step_scalar(4.9, 0.0, 0.6)
    assert plus == pytest.approx(5.0)
    assert alarm == ALARM_UP


def test_tau_starts_at_one():
    path = frozen_model.run_path([H_FROZEN + K_FROZEN])
    assert path.tau == 1


def test_terminal_increment_is_included_in_t_tau():
    z = H_FROZEN + K_FROZEN
    path = frozen_model.run_path([0.4, 0.4, z])
    assert path.tau == 3
    assert path.z_tau == pytest.approx(z)
    assert path.t_sum == pytest.approx(0.4 + 0.4 + z)


def test_plus_arm_priority_on_tie():
    """Frozen order is `if plus>=h ... elif minus>=h`; assert the tie rule."""
    up = np.array([True]);  down = np.array([True])
    assert alarm_direction(up, down)[0] == ALARM_UP
    assert count_ties(up, down) == 1


# --------------------------------------------------------- re-baselining rule --

def test_rho_endpoints_are_exact():
    reuse = np.array([1.5, -2.0]);  fresh = np.array([0.25, 0.75])
    assert np.array_equal(rebaseline(reuse, fresh, 0.0), fresh)
    assert np.array_equal(rebaseline(reuse, fresh, 1.0), reuse)
    mid = rebaseline(reuse, fresh, 0.25)
    assert mid == pytest.approx(0.25 * reuse + 0.75 * fresh)


@pytest.mark.parametrize("bad", [-1e-9, 1.0 + 1e-9, 2.0])
def test_rho_out_of_range_rejected(bad):
    with pytest.raises(ValueError):
        rebaseline(np.zeros(1), np.zeros(1), bad)


@pytest.mark.parametrize("m", [1, 5, 10, 20, 50])
def test_fresh_statistic_scale(m):
    assert fresh_statistic_scale(m) == pytest.approx(1.0 / np.sqrt(m))


# ------------------------------------------------------------ RNG determinism --

def test_per_row_stream_reproduces_isolated_row_generators():
    stream = PerRowStream(4242, STREAM_OBS, 6, chunk=16)
    rows = np.arange(6)
    drawn = np.array([stream.draw(rows) for _ in range(40)]).T
    for r in range(6):
        want = generator(4242, STREAM_OBS, r).standard_normal(40)
        assert np.array_equal(drawn[r], want)


def test_per_row_stream_is_independent_of_ragged_consumption():
    stream = PerRowStream(7, STREAM_OBS, 4, chunk=8)
    seen: dict[int, list[float]] = {r: [] for r in range(4)}
    for i in range(25):
        rows = np.arange(max(1, 4 - i // 7))
        values = stream.draw(rows)
        for j, r in enumerate(rows):
            seen[int(r)].append(float(values[j]))
    for r, values in seen.items():
        want = generator(7, STREAM_OBS, r).standard_normal(len(values))
        assert np.allclose(values, want, rtol=0, atol=0)


def test_simulation_is_bit_reproducible():
    cfg = MultiCycleConfig(n_replicates=8, n_cycles=20, burn_in=5, rho=0.5, m=3,
                           master_seed=99)
    a = simulate_multicycle(cfg)
    b = simulate_multicycle(cfg)
    for name, col in a.columns().items():
        assert np.array_equal(col, b.columns()[name]), name


# ----------------------------------------- multi-cycle vs frozen single cycle --

def test_first_cycle_equals_frozen_run_path():
    """With e0=0 and m=1, cycle 0 is literally a frozen Level 1-3 path."""
    cfg = MultiCycleConfig(n_replicates=64, n_cycles=1, burn_in=0, rho=1.0, m=1,
                           master_seed=1729)
    table = simulate_multicycle(cfg)
    for r in range(cfg.n_replicates):
        innovations = generator(1729, STREAM_OBS, r).standard_normal(200_000)
        want = frozen_model.run_path(innovations.tolist())
        assert table.tau[r] == want.tau
        assert table.z_tau[r] == pytest.approx(want.z_tau, abs=0, rel=0)
        assert table.t_tau[r] == pytest.approx(want.t_sum, rel=1e-12)
        assert table.direction[r] == ALARM_MAP[want.alarm]
        assert table.s_plus_terminal[r] == want.terminal_state.plus
        assert table.s_minus_terminal[r] == want.terminal_state.minus
        # m = 1: the reuse statistic is exactly the alarm-causing observation
        assert table.mu_reuse[r] == pytest.approx(want.z_tau, rel=1e-12)


@pytest.mark.parametrize("m,rho", [(1, 1.0), (1, 0.0), (5, 0.25), (20, 0.5)])
def test_vectorised_matches_scalar_replay(m, rho):
    cfg = MultiCycleConfig(n_replicates=6, n_cycles=12, burn_in=4, rho=rho, m=m,
                           master_seed=31337)
    table = simulate_multicycle(cfg)
    total = cfg.burn_in + cfg.n_cycles
    for r in range(cfg.n_replicates):
        rows = replay_replicate_scalar(
            master_seed=cfg.master_seed, replicate=r, n_cycles_total=total,
            m=m, rho=rho, draw_budget=2_000_000,
        )
        for j, row in enumerate(rows):
            idx = r * total + j
            assert table.tau[idx] == row["tau"]
            assert table.direction[idx] == row["direction"]
            assert table.z_tau[idx] == pytest.approx(row["z_tau"], rel=1e-12)
            assert table.t_tau[idx] == pytest.approx(row["t_tau"], rel=1e-10)
            assert table.window_sum[idx] == pytest.approx(row["window_sum"], rel=1e-10)
            assert table.mu_reuse[idx] == pytest.approx(row["mu_reuse"], rel=1e-10)
            assert table.mu_fresh[idx] == pytest.approx(row["mu_fresh"], rel=1e-12)
            assert table.e_next[idx] == pytest.approx(row["e_next"], rel=1e-10)


# ---------------------------------------------------------------- m semantics --

@pytest.mark.parametrize("m", [1, 2, 5, 20])
def test_minimum_dwell_is_respected(m):
    cfg = MultiCycleConfig(n_replicates=32, n_cycles=30, burn_in=0, rho=1.0, m=m,
                           master_seed=5150)
    table = simulate_multicycle(cfg)
    assert table.tau.min() >= m


def test_window_sum_is_the_last_m_residuals_including_the_alarm():
    m = 7
    cfg = MultiCycleConfig(n_replicates=4, n_cycles=6, burn_in=0, rho=1.0, m=m,
                           master_seed=8080)
    table = simulate_multicycle(cfg)
    total = cfg.n_cycles
    for r in range(cfg.n_replicates):
        draws = iter(generator(8080, STREAM_OBS, r).standard_normal(2_000_000).tolist())
        e = 0.0
        for j in range(total):
            idx = r * total + j
            tau = int(table.tau[idx])
            zs = [next(draws) - e for _ in range(tau)]
            assert zs[-1] == pytest.approx(table.z_tau[idx], rel=1e-12)
            assert sum(zs[-m:]) == pytest.approx(table.window_sum[idx], rel=1e-10)
            e = float(table.e_next[idx])


def test_fresh_policy_ignores_the_stopping_selected_data():
    cfg = MultiCycleConfig(n_replicates=16, n_cycles=40, burn_in=0, rho=0.0, m=5,
                           master_seed=606)
    table = simulate_multicycle(cfg)
    assert np.allclose(table.e_next, table.mu_fresh, rtol=0, atol=0)


def test_full_reuse_policy_uses_only_the_selected_statistic():
    cfg = MultiCycleConfig(n_replicates=16, n_cycles=40, burn_in=0, rho=1.0, m=5,
                           master_seed=607)
    table = simulate_multicycle(cfg)
    assert np.allclose(table.e_next, table.mu_reuse, rtol=0, atol=0)


def test_no_simultaneous_two_arm_crossings_occur():
    """Unreachable for the frozen CUSUM; recorded rather than assumed."""
    cfg = MultiCycleConfig(n_replicates=32, n_cycles=200, burn_in=0, rho=1.0, m=1,
                           master_seed=90210)
    assert simulate_multicycle(cfg).n_ties == 0


def test_config_validation_rejects_non_frozen_detector_constants():
    with pytest.raises(ValueError):
        MultiCycleConfig(n_replicates=2, n_cycles=2, burn_in=0, rho=0.5, m=1,
                         master_seed=1, k=0.6).validate()
    with pytest.raises(ValueError):
        MultiCycleConfig(n_replicates=2, n_cycles=2, burn_in=0, rho=0.5, m=1,
                         master_seed=1, h=4.0).validate()
