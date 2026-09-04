"""Staged rule semantics and the independent disposition auditor.

Brief section 7: the terminal state space is exactly {ATTAINED,
PRECISION_LIMITED}, and PRECISION_LIMITED is valid ONLY when the next
predeclared stage would exceed the frozen cap.
"""

import math

import pytest

from p4y_pilot2.audit import audit
from p4y_pilot2.rule import (
    ATTAINED, PRECISION_LIMITED, Outcome, Precision, Trajectory,
    next_allocation, terminate, trace,
)
from p4y_pilot2.strata import KAPPA_A, KAPPA_B

TARGET = 0.01
KAPPAS = (KAPPA_A, KAPPA_B)


def law(c, exponent=0.5):
    return lambda b: c * b ** -exponent


def stuck(v):
    return lambda b: v


@pytest.mark.parametrize("kappa", KAPPAS)
@pytest.mark.parametrize("measure", [law(0.15), law(0.6), stuck(0.5),
                                     stuck(1e6), law(0.02)],
                         ids=["mild", "large", "stuck", "hopeless", "already"])
def test_terminal_state_space_is_exactly_two(kappa, measure):
    traj = trace(measure=measure, b1=48, target=TARGET, kappa=kappa,
                 max_cap=10 ** 6)
    for cap in (48, 72, 144, 576, 5000, 10 ** 6):
        o = terminate(traj, cap)
        assert o.status in (ATTAINED, PRECISION_LIMITED), o
        assert audit(o, traj, cap_blocks=cap).valid, audit(o, traj, cap_blocks=cap)


@pytest.mark.parametrize("kappa", KAPPAS)
def test_nothing_ever_executes_beyond_the_cap(kappa):
    traj = trace(measure=stuck(0.5), b1=48, target=TARGET, kappa=kappa,
                 max_cap=10 ** 6)
    for cap in (48, 100, 576, 4000):
        assert terminate(traj, cap).blocks <= cap


def test_precision_limited_requires_the_next_stage_to_cross_the_cap():
    traj = trace(measure=stuck(0.05), b1=48, target=TARGET, kappa=KAPPA_B,
                 max_cap=10 ** 6)
    o = terminate(traj, 100)
    assert o.status == PRECISION_LIMITED
    assert o.next_stage_blocks > 100
    assert o.blocks <= 100
    assert audit(o, traj, cap_blocks=100).valid


def test_precision_limited_before_stage_one_executes_nothing():
    """A route whose projected stage 1 already exceeds the cap draws no block."""
    traj = trace(measure=law(0.15), b1=5000, target=TARGET, kappa=KAPPA_B,
                 max_cap=624)
    assert traj.stages == ()
    assert traj.planned_b1 == 5000
    o = terminate(traj, 576)
    assert o.status == PRECISION_LIMITED
    assert o.blocks == 0
    assert o.next_stage_blocks == 5000
    assert audit(o, traj, cap_blocks=576).valid


def test_a_generous_cap_always_attains_when_the_route_converges():
    for kappa in KAPPAS:
        traj = trace(measure=law(0.6), b1=48, target=TARGET, kappa=kappa,
                     max_cap=10 ** 7)
        o = terminate(traj, 10 ** 7)
        assert o.status == ATTAINED
        assert o.relative_se <= TARGET


def test_the_auditor_catches_a_mislabelled_attainment():
    traj = trace(measure=stuck(0.5), b1=48, target=TARGET, kappa=KAPPA_B,
                 max_cap=10 ** 6)
    forged = Outcome(ATTAINED, 48, 1, 0.5, TARGET, KAPPA_B, 576, None, (48,))
    a = audit(forged, traj, cap_blocks=576)
    assert not a.valid
    assert any("ATTAINED" in r for r in a.reasons)


def test_the_auditor_catches_execution_past_the_cap():
    traj = trace(measure=law(0.15), b1=48, target=TARGET, kappa=KAPPA_B,
                 max_cap=10 ** 6)
    forged = Outcome(ATTAINED, 9000, 2, 0.001, TARGET, KAPPA_B, 576, None,
                     (48, 9000))
    a = audit(forged, traj, cap_blocks=576)
    assert not a.valid
    assert any("beyond the cap" in r for r in a.reasons)


def test_the_auditor_catches_a_premature_precision_limited():
    traj = trace(measure=stuck(0.5), b1=48, target=TARGET, kappa=KAPPA_B,
                 max_cap=10 ** 6)
    forged = Outcome(PRECISION_LIMITED, 48, 1, 0.5, TARGET, KAPPA_B,
                     10 ** 6, 120000, (48,))
    a = audit(forged, traj, cap_blocks=10 ** 6)
    assert not a.valid
    assert any("does not exceed the cap" in r for r in a.reasons)


def test_the_auditor_catches_a_foreign_trajectory():
    traj = trace(measure=law(0.15), b1=48, target=TARGET, kappa=KAPPA_B,
                 max_cap=10 ** 6)
    o = terminate(traj, 576)
    other = Trajectory(traj.stages, TARGET * 2, traj.kappa, True, False, 48)
    assert not audit(o, other, cap_blocks=576).valid


def test_terminate_agrees_with_a_rule_run_under_that_cap():
    """Deriving every cap from one trajectory must equal running each cap."""
    for kappa in KAPPAS:
        for c in (0.05, 0.15, 0.4):
            m = law(c)
            traj = trace(measure=m, b1=48, target=TARGET, kappa=kappa,
                         max_cap=10 ** 6)
            for cap in (48, 60, 100, 300, 1000, 10 ** 6):
                derived = terminate(traj, cap)
                # an independent re-run that stops itself at the cap
                blocks, stages, status, nxt, rel = 48, 0, None, None, math.inf
                while True:
                    if blocks > cap:
                        status, blocks = PRECISION_LIMITED, prev_blocks
                        break
                    rel = m(blocks)
                    stages += 1
                    prev_blocks = blocks
                    if rel <= TARGET:
                        status, nxt = ATTAINED, None
                        break
                    nxt = next_allocation(Precision(blocks, rel), TARGET, kappa)
                    if nxt > cap:
                        status = PRECISION_LIMITED
                        break
                    blocks = nxt
                assert derived.status == status, (kappa, c, cap)
                assert derived.blocks == blocks, (kappa, c, cap)


def test_sizing_law_is_the_inherited_one():
    p = Precision(100, 0.05)
    assert next_allocation(p, 0.01, 0.5) == math.ceil(100 * 5.0 ** 2)
    assert next_allocation(p, 0.01, KAPPA_A) == math.ceil(100 * 5.0 ** (1 / KAPPA_A))
    assert next_allocation(Precision(100, 0.005), 0.01, 0.5) == 100


def test_kappa_a_always_buys_at_least_as_much_as_kappa_b():
    """1/kappa_A = 3.128 > 2 = 1/kappa_B, so A over-buys whenever short."""
    for rel in (0.011, 0.02, 0.1, 1.0):
        a = next_allocation(Precision(100, rel), 0.01, KAPPA_A)
        b = next_allocation(Precision(100, rel), 0.01, KAPPA_B)
        assert a >= b
