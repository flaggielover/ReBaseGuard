"""The recurrence repair, re-derived independently of the experiment program.

Nothing here imports ``run_sr_recurrence_check.py``.  The expected numbers are
written out from the frozen specification by hand, so a bug shared between the
module and its generator cannot hide.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from rebaseguard_p9r import SR_THRESHOLD
from rebaseguard_p9r.detectors import (
    sr_initial_state, sr_initial_state_p9_defective, sr_step,
    sr_step_p9_defective,
)

LOG_A = math.log(SR_THRESHOLD)


def one(z, step, init):
    yp, ym = init(1)
    return step(yp, ym, np.array([float(z)]), LOG_A)


def test_no_headstart_initial_state_is_zero():
    yp, ym = sr_initial_state(1)
    # y = log(1 + R) and R_0 = 0, so y_0 must be exactly 0.0
    assert yp[0] == 0.0 and ym[0] == 0.0


def test_first_step_equals_hand_computed_log_R1():
    z = 0.25
    yp, ym = sr_initial_state(1)
    ell = float(yp[0] + z - 0.5)
    assert ell == pytest.approx(z - 0.5, abs=0.0)
    # and the raw state matches the non-log recurrence exactly
    assert math.exp(ell) == pytest.approx((1.0 + 0.0) * math.exp(z - 0.5), rel=0, abs=1e-15)


def test_first_two_steps_match_the_direct_recurrence():
    zs = [0.25, -0.75]
    rp = 0.0
    yp, ym = sr_initial_state(1)
    for z in zs:
        ell = float(yp[0] + z - 0.5)
        rp = (1.0 + rp) * math.exp(z - 0.5)
        assert ell == pytest.approx(math.log(rp), abs=1e-12)
        yp, ym, _, _ = sr_step(yp, ym, np.array([float(z)]), LOG_A)


def test_reset_first_step_is_the_same_as_the_very_first_step():
    """A cycle reset restores y_0 = 0, so the first post-reset update is
    identical to the first update of cycle one."""
    z = 0.1
    yp, ym = sr_initial_state(1)
    first = float(yp[0] + z - 0.5)
    # simulate a few steps, then reset
    for zz in (1.5, -0.4, 2.0):
        yp, ym, _, _ = sr_step(yp, ym, np.array([zz]), LOG_A)
    assert yp[0] > 0.0                      # state really moved
    yp, ym = sr_initial_state(1)            # the reset
    after_reset = float(yp[0] + z - 0.5)
    assert after_reset == first


def test_absence_of_log2_shift_in_the_repaired_form():
    """The repaired first step must NOT contain log 2."""
    z = 0.25
    yp, _ = sr_initial_state(1)
    ell = float(yp[0] + z - 0.5)
    assert abs(ell - (z - 0.5)) == 0.0
    assert abs(ell - (z - 0.5 + math.log(2.0))) == pytest.approx(math.log(2.0))


def test_p9_form_is_shifted_by_exactly_log2_on_the_first_step():
    z = 0.25
    yp, _ = sr_initial_state(1)
    gp, _ = sr_initial_state_p9_defective(1)
    frozen = float(yp[0] + z - 0.5)
    p9 = float(np.logaddexp(0.0, gp[0]) + z - 0.5)
    assert p9 - frozen == math.log(2.0)


def test_log2_shift_changes_the_alarm_decision():
    z = LOG_A + 0.5 - 0.5 * math.log(2.0)
    _, _, cu_f, _ = one(z, sr_step, sr_initial_state)
    _, _, cu_9, _ = one(z, sr_step_p9_defective, sr_initial_state_p9_defective)
    assert not bool(cu_f[0])
    assert bool(cu_9[0])


def test_eight_step_path_matches_direct_recurrence_and_alarms():
    zs = [0.25, -0.75, 1.5, 0.1, -0.4, 2.0, -1.25, 0.6]
    rp = rm = 0.0
    yp, ym = sr_initial_state(1)
    for z in zs:
        ell_p = float(yp[0] + z - 0.5)
        ell_m = float(ym[0] - z - 0.5)
        rp = (1.0 + rp) * math.exp(z - 0.5)
        rm = (1.0 + rm) * math.exp(-z - 0.5)
        assert ell_p == pytest.approx(math.log(rp), abs=1e-12)
        assert ell_m == pytest.approx(math.log(rm), abs=1e-12)
        assert (ell_p >= LOG_A) == (rp >= SR_THRESHOLD)
        assert (ell_m >= LOG_A) == (rm >= SR_THRESHOLD)
        yp, ym, _, _ = sr_step(yp, ym, np.array([float(z)]), LOG_A)


def test_experiment_artifact_agrees_when_present(sr_check):
    assert sr_check["all_pass"] is True
    assert sr_check["C5_log2_shift"]["first_step_shift"] == math.log(2.0)
    assert sr_check["C6_alarm_witness"]["decisions_differ"] is True
