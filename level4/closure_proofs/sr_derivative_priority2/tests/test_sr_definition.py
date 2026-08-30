from __future__ import annotations

import math
import numpy as np

from rebaseguard_sr_priority2.direct_sr import log_step, run_path as run_log
from rebaseguard_sr_priority2.score_sr import raw_step, run_path as run_raw


def test_raw_and_log_recurrences_correspond_on_hand_path() -> None:
    path = np.array([0.25, -0.5, 1.0])
    rp = rm = yp = ym = 0.0
    for z in path:
        rp, rm = raw_step(rp, rm, z)
        yp, ym, ep, em = log_step(yp, ym, z)
        assert np.isclose(math.exp(yp) - 1.0, rp)
        assert np.isclose(math.exp(ym) - 1.0, rm)
        assert np.isclose(math.exp(ep), rp)
        assert np.isclose(math.exp(em), rm)


def test_witness_stopping_and_reflection() -> None:
    paths = ([2.0], [-2.0], [0.0] * 5 + [2.0], [0.0] * 5 + [-2.0])
    expected = (1, 1, 6, 6)
    for path, tau in zip(paths, expected):
        raw = run_raw(np.array(path), 2.0)
        log = run_log(np.array(path), 2.0)
        assert raw["tau"] == log["tau"] == tau
        assert np.isclose(raw["T"], log["T"])
    plus = run_raw(np.array(paths[2]), 2.0)
    minus = run_raw(np.array(paths[3]), 2.0)
    assert np.isclose(plus["plus"], minus["minus"])
    assert np.isclose(plus["minus"], minus["plus"])


def test_inclusive_post_update_threshold_and_terminal_inclusion() -> None:
    z = math.log(2.0) + 0.5
    threshold = math.exp(z - 0.5)
    record = run_raw(np.array([z, -100.0]), threshold)
    assert record["tau"] == 1
    assert record["increments"] == [z]
    assert record["T"] == z


def test_reset_state_and_no_headstart() -> None:
    rp, rm = raw_step(0.0, 0.0, 0.0)
    assert np.isclose(rp, math.exp(-0.5))
    assert np.isclose(rm, math.exp(-0.5))
