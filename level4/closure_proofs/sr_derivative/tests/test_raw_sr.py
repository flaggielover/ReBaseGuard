from __future__ import annotations

import math

import numpy as np

from rebaseguard_sr_derivative import AUTHORITATIVE_A
from rebaseguard_sr_derivative.raw_sr import (
    DOWN,
    TIE,
    UP,
    classify_alarm,
    raw_step,
    run_raw_path,
    simulate_raw_paths,
)


def test_forcing_bound_is_sufficient_in_raw_route():
    bound = math.log(AUTHORITATIVE_A) + 0.5
    live = np.array([0.0, 0.1, 17.0, np.nextafter(AUTHORITATIVE_A, 0.0)])
    plus, _ = raw_step(live, live[::-1], np.full(live.size, bound))
    _, minus = raw_step(live, live[::-1], np.full(live.size, -bound))
    assert np.all(plus >= AUTHORITATIVE_A)
    assert np.all(minus >= AUTHORITATIVE_A)


def test_raw_reflection_swaps_direction_and_terminal_statistics():
    path = np.array([0.2, -0.3, 0.1, 0.8, 8.0])
    forward = run_raw_path(path, threshold=AUTHORITATIVE_A)
    reflected = run_raw_path(-path, threshold=AUTHORITATIVE_A)
    assert forward.tau == reflected.tau
    assert forward.direction == UP
    assert reflected.direction == DOWN
    assert forward.terminal_z == -reflected.terminal_z
    assert forward.stopped_sum == -reflected.stopped_sum
    assert forward.r_plus == reflected.r_minus
    assert forward.r_minus == reflected.r_plus


def test_raw_alarm_classifier_distinguishes_unequal_and_exact_ties():
    crossed, direction, simultaneous, exact_tie = classify_alarm(
        np.array([700.0, 600.0, 700.0]),
        np.array([600.0, 700.0, 700.0]),
        AUTHORITATIVE_A,
    )
    np.testing.assert_array_equal(crossed, [True, True, True])
    np.testing.assert_array_equal(direction, [UP, DOWN, TIE])
    np.testing.assert_array_equal(simultaneous, [True, True, True])
    np.testing.assert_array_equal(exact_tie, [False, False, True])


def test_raw_batch_accumulates_terminal_innovation_and_score_product():
    batch = simulate_raw_paths(
        n_paths=256,
        threshold=40.0,
        rng=np.random.default_rng(np.random.SeedSequence([2026082227, 90, 1])),
    )
    assert np.all(batch.tau >= 1)
    np.testing.assert_array_equal(
        batch.product, batch.terminal_z * batch.stopped_sum
    )
    assert np.count_nonzero(batch.exact_tie) == 0
    assert set(np.unique(batch.direction)).issubset({int(UP), int(DOWN)})


def test_natural_threshold_and_log_threshold_are_not_interchangeable():
    path = np.full(20, 0.8)
    natural = run_raw_path(path, threshold=AUTHORITATIVE_A)
    mistaken_log = run_raw_path(path, threshold=math.log(AUTHORITATIVE_A))
    assert mistaken_log.tau is not None
    assert natural.tau != mistaken_log.tau

