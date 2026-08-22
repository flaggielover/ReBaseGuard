from __future__ import annotations

import math

import numpy as np

from rebaseguard_sr_derivative import AUTHORITATIVE_A
from rebaseguard_sr_derivative.log_sr import (
    DOWN,
    TIE,
    UP,
    classify_alarm_logs,
    run_log_path,
    simulate_paired_log_batch,
)
from rebaseguard_sr_derivative.raw_sr import run_raw_path


def test_independent_raw_and_log_paths_correspond():
    paths = [
        np.array([0.1, -0.2, 0.4, 7.0]),
        np.array([-0.1, 0.3, -0.5, -7.0]),
        np.array([0.3, -0.1, 0.2, -0.4, 0.5]),
    ]
    for path in paths:
        raw = run_raw_path(path, threshold=AUTHORITATIVE_A)
        log = run_log_path(path, threshold=AUTHORITATIVE_A)
        assert raw.tau == log.tau
        assert raw.direction == log.direction
        assert raw.terminal_z == log.terminal_z
        assert raw.stopped_sum == log.stopped_sum
        np.testing.assert_allclose(math.log1p(raw.r_plus), log.y_plus, rtol=2e-15)
        np.testing.assert_allclose(math.log1p(raw.r_minus), log.y_minus, rtol=2e-15)


def test_log_reflection_swaps_charts_and_terminal_signs():
    path = np.array([0.2, -0.3, 0.1, 0.8, 8.0])
    forward = run_log_path(path, threshold=AUTHORITATIVE_A)
    reflected = run_log_path(-path, threshold=AUTHORITATIVE_A)
    assert forward.tau == reflected.tau
    assert forward.direction == UP
    assert reflected.direction == DOWN
    assert forward.terminal_z == -reflected.terminal_z
    assert forward.stopped_sum == -reflected.stopped_sum
    assert forward.y_plus == reflected.y_minus
    assert forward.y_minus == reflected.y_plus


def test_log_alarm_classifier_has_explicit_tie_status():
    log_a = math.log(AUTHORITATIVE_A)
    crossed, direction, simultaneous, exact_tie = classify_alarm_logs(
        np.array([log_a + 1.0, log_a + 0.2, log_a + 0.5]),
        np.array([log_a + 0.2, log_a + 1.0, log_a + 0.5]),
        log_a,
    )
    np.testing.assert_array_equal(crossed, [True, True, True])
    np.testing.assert_array_equal(direction, [UP, DOWN, TIE])
    np.testing.assert_array_equal(simultaneous, [True, True, True])
    np.testing.assert_array_equal(exact_tie, [False, False, True])


def test_paired_log_batch_reuses_one_path_time_stream_for_all_conditions():
    h_grid = np.array([0.1, 0.05, 0.025, 0.0125])
    seed = np.random.SeedSequence([2026082227, 91, 2])
    first = simulate_paired_log_batch(
        n_paths=128,
        threshold=40.0,
        h_grid=h_grid,
        rng=np.random.default_rng(seed),
    )
    second = simulate_paired_log_batch(
        n_paths=128,
        threshold=40.0,
        h_grid=h_grid,
        rng=np.random.default_rng(np.random.SeedSequence([2026082227, 91, 2])),
    )
    np.testing.assert_array_equal(first.map_output, second.map_output)
    np.testing.assert_array_equal(first.tau, second.tau)
    np.testing.assert_array_equal(first.derivatives, second.derivatives)
    assert first.map_output.shape == (4, 2, 128)
    assert np.count_nonzero(first.exact_tie) == 0


def test_rho_scaling_and_affine_endpoints_are_pathwise():
    reuse_error = np.array([-2.0, 0.0, 3.0])
    fresh = np.array([0.5, -0.5, 1.0])
    rho = 0.37
    mixed = rho * reuse_error + (1.0 - rho) * fresh
    np.testing.assert_array_equal(0.0 * reuse_error + fresh, fresh)
    np.testing.assert_array_equal(1.0 * reuse_error + 0.0 * fresh, reuse_error)
    np.testing.assert_allclose(mixed - (1.0 - rho) * fresh, rho * reuse_error)

