"""Detector, window, stopping and update semantics against the frozen model."""
import numpy as np
import pytest

from rebaseguard_p8 import CUSUM, SR, SR_THRESHOLD_GAUSSIAN, K_FROZEN
from rebaseguard_p8.chain import shift_schedule, simulate_chain
from rebaseguard_p8.detectors import make_step, sr_update
from rebaseguard_p8.stopped import simulate_row_block

EXP = "unit_test"


def test_cusum_step_is_the_frozen_recurrence():
    step, thr = make_step(CUSUM)
    assert thr == 5.0 and K_FROZEN == 0.5
    p = np.array([0.0, 1.0, 4.9])
    m = np.array([0.0, 0.0, 0.0])
    z = np.array([0.2, 0.3, 0.6])
    np_, nm_, cu, cd = step(p, m, z)
    assert np.allclose(np_, np.maximum(0.0, p + z - 0.5))
    assert np.allclose(nm_, np.maximum(0.0, m - z - 0.5))
    assert cu.tolist() == [False, False, True]      # inclusive, POST update


def test_cusum_alarm_test_is_inclusive():
    step, _ = make_step(CUSUM, 5.0)
    _, _, cu, _ = step(np.array([4.5]), np.array([0.0]), np.array([1.0]))
    assert bool(cu[0]) is True                       # 5.0 >= 5.0 alarms


def test_sr_step_matches_stage_d_helper():
    log_thr = float(np.log(SR_THRESHOLD_GAUSSIAN))
    step, thr = make_step(SR)
    assert thr == SR_THRESHOLD_GAUSSIAN
    yp, ym, z = np.array([0.3]), np.array([0.1]), np.array([0.7])
    assert all(np.allclose(a, b) for a, b in
               zip(step(yp, ym, z), sr_update(yp, ym, z, log_thr)))


def test_sr_rejects_a_log_domain_threshold():
    with pytest.raises(ValueError):
        make_step(SR, 0.9)


def test_tau_starts_at_one_and_includes_the_terminal_increment():
    s = simulate_row_block(experiment=EXP, family="gaussian", detector=CUSUM,
                           threshold=5.0, batch=0, row_block=0, n_paths=512)
    assert s.tau.min() >= 1
    # T is the sum of all tau increments: rebuild it for the shortest paths
    short = np.flatnonzero(s.tau <= s.L)
    rebuilt = np.where(s.valid[short], s.lag_z[short], 0.0).sum(axis=1)
    assert np.allclose(rebuilt, s.T[short], atol=1e-12)


def test_convention_A_and_B_differ_exactly_by_the_truncation_set():
    s = simulate_row_block(experiment=EXP, family="gaussian", detector=CUSUM,
                           threshold=5.0, batch=0, row_block=0, n_paths=2048)
    for m in (1, 2, 5, 20):
        a, b = s.zbar(m, "A"), s.zbar(m, "B")
        same = s.tau >= m
        assert np.allclose(a[same], b[same], atol=0, rtol=0)
        assert np.allclose(a[~same] * np.minimum(m, s.tau[~same]),
                           b[~same] * m)


def test_window_is_the_truncated_newest_first_window():
    s = simulate_row_block(experiment=EXP, family="t5", detector=CUSUM,
                           threshold=5.669498491821448, batch=0, row_block=0,
                           n_paths=512)
    # lag 0 is the terminal (alarm-causing) increment
    assert np.allclose(s.zbar(1, "A"), s.lag_z[:, 0])
    w = np.minimum(3, s.tau)
    manual = np.where(s.valid[:, :3], s.lag_z[:, :3], 0.0).sum(axis=1) / w
    assert np.allclose(s.zbar(3, "A"), manual)


def test_m1_gamma_reduces_to_the_p4_raw_reuse_estimand():
    s = simulate_row_block(experiment=EXP, family="t5", detector=CUSUM,
                           threshold=5.669498491821448, batch=0, row_block=0,
                           n_paths=1024)
    assert np.allclose(s.zbar(1, "A") * s.Psi, s.lag_z[:, 0] * s.Psi)


def test_gaussian_psi_sum_equals_T():
    s = simulate_row_block(experiment=EXP, family="gaussian", detector=CUSUM,
                           threshold=5.0, batch=0, row_block=0, n_paths=1024)
    assert np.allclose(s.Psi, s.T, atol=1e-9)


def test_chain_reference_update_is_the_frozen_line():
    r = simulate_chain(experiment=EXP, family="gaussian", detector=CUSUM,
                       threshold=5.0, m=2, rho=0.6, n_rep=64, n_cycles=4,
                       burn_in=0)
    from rebaseguard_p8 import primitives as PR
    for j in range(3):
        fresh = PR.chain_fresh(EXP, "gaussian", CUSUM, 2, j, 64)
        expect = 0.6 * (r.e_start[:, j] + r.zbar[:, j]) + 0.4 * fresh
        assert np.allclose(r.e_start[:, j + 1], expect, atol=1e-12)


def test_rho_zero_chain_has_reference_variance_one_over_m():
    for m in (1, 5):
        r = simulate_chain(experiment=EXP, family="gaussian", detector=CUSUM,
                           threshold=5.0, m=m, rho=0.0, n_rep=3000,
                           n_cycles=12, burn_in=2)
        assert abs(r.per_replicate_ref_mse.mean() - 1.0 / m) < 0.06 / m


def test_shift_schedule_semantics():
    assert shift_schedule(5, "none").tolist() == [0, 0, 0, 0, 0]
    assert shift_schedule(5, "step", 1.0, 2).tolist() == [0, 0, 1, 1, 1]
    assert shift_schedule(5, "ramp", 0.0, 2, 0.5).tolist() == [0, 0, .5, 1., 1.5]
    with pytest.raises(ValueError):
        shift_schedule(3, "sawtooth")


def test_step_shift_enters_as_a_one_time_reference_offset():
    """P7's convention: a permanent process-mean shift is a ONE-TIME offset of
    the reference error, because the reference re-centres on the new mean at the
    next update.  Only the first post-change cycle sees it at ``rho = 0``."""
    sched = shift_schedule(6, "step", 1.0, 3)
    r = simulate_chain(experiment=EXP, family="gaussian", detector=CUSUM,
                       threshold=5.0, m=1, rho=0.0, n_rep=4000, n_cycles=6,
                       burn_in=0, shift=sched)
    assert abs(r.e_start[:, 1].mean()) < 0.06            # pre-change, centred
    assert abs(r.e_start[:, 3].mean() + 1.0) < 0.06      # the change lands here
    assert abs(r.e_start[:, 4].mean()) < 0.06            # reference re-centred


def test_ramp_shift_is_a_persistent_per_cycle_increment():
    sched = shift_schedule(8, "ramp", 0.0, 2, 0.5)
    r = simulate_chain(experiment=EXP, family="gaussian", detector=CUSUM,
                       threshold=5.0, m=1, rho=0.0, n_rep=4000, n_cycles=8,
                       burn_in=0, shift=sched)
    for j in (3, 5, 7):
        assert abs(r.e_start[:, j].mean() + 0.5) < 0.06
