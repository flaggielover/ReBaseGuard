"""Proof that the post-T2 harness fix is OUTCOME-PRESERVING.

Classification (brief section 23): implementation bug in the harness, found
after T2, semantics-preserving.

WHAT WAS WRONG.  ``trace`` bounded its loop by ``pool_limit = B_ref + largest
frozen cap`` and, when the sizing law computed a NEXT stage beyond that bound,
flagged ``pool_exhausted`` -- which the runner raised on, aborting the phase.
But the computed next stage is a NUMBER, not a draw: in the observed case the
replicate had drawn 48 blocks against a pool limit of 624.  No replicate ever
requested more than the pool limit, so the frozen STOP rule 2 never fired in
substance.

WHY THE FIX CHANGES NO RESULT.  ``terminate`` never reads ``pool_exhausted``;
it walks the stage list.  The stage list is identical either way, because the
old loop appended the stage BEFORE noticing the bound.  The fix simply returns
at that point instead of iterating once more and flagging.  The frozen
specification already said this was the intent: "the rule can always run to
the point where the largest cap would refuse it, and never one block further".

These tests prove the equivalence over randomised trajectories rather than
asserting it.
"""

import math
import random

import pytest

from p4y_pilot2.rule import (
    ATTAINED, PRECISION_LIMITED, Precision, Stage, Trajectory,
    next_allocation, terminate, trace,
)
from p4y_pilot2.strata import CAP_MULTIPLIERS, KAPPA_A, KAPPA_B, STRATA, cap_blocks


def old_trace(*, measure, b1, target, kappa, pool_limit):
    """The pre-fix implementation, verbatim, kept only to be compared against."""
    stages = []
    blocks = b1
    if b1 > pool_limit:
        return Trajectory((), target, kappa, False, False, b1)
    while True:
        if blocks > pool_limit:
            return Trajectory(tuple(stages), target, kappa, False, True, b1)
        achieved = measure(blocks)
        here = Precision(blocks, achieved)
        if achieved <= target:
            stages.append(Stage(len(stages) + 1, blocks, achieved, None))
            return Trajectory(tuple(stages), target, kappa, True, False, b1)
        nxt = next_allocation(here, target, kappa)
        stages.append(Stage(len(stages) + 1, blocks, achieved, nxt))
        blocks = nxt


@pytest.mark.parametrize("stratum", STRATA, ids=lambda s: s.key)
@pytest.mark.parametrize("kappa", [KAPPA_A, KAPPA_B], ids=["kA", "kB"])
def test_the_fix_gives_identical_outcomes_at_every_frozen_cap(stratum, kappa):
    rng = random.Random(20260904)
    max_cap = cap_blocks(stratum, max(CAP_MULTIPLIERS))
    pool = stratum.b_ref + max_cap
    target = 0.03
    for _ in range(60):
        c = math.exp(rng.uniform(math.log(0.05), math.log(6.0)))
        noise = [rng.uniform(0.7, 1.4) for _ in range(64)]
        counter = {"i": 0}

        def measure(b, c=c, noise=noise, counter=counter):
            v = c * b ** -0.5 * noise[counter["i"] % len(noise)]
            counter["i"] += 1
            return v

        counter["i"] = 0
        new = trace(measure=measure, b1=stratum.b1, target=target,
                    kappa=kappa, max_cap=max_cap)
        counter["i"] = 0
        old = old_trace(measure=measure, b1=stratum.b1, target=target,
                        kappa=kappa, pool_limit=pool)

        # The new stage list is a PREFIX of the old one.  Where they differ,
        # the old code had drawn one further stage whose block count already
        # exceeded the largest frozen cap -- simulation that no cap in the
        # grid could ever consume.  The fix removes that wasted draw and
        # nothing else.
        assert list(new.stages) == list(old.stages)[:len(new.stages)]
        assert new.planned_b1 == old.planned_b1
        if len(old.stages) > len(new.stages):
            assert old.stages[len(new.stages)].blocks > max_cap

        # What actually matters: every frozen cap yields the identical outcome.
        for mult in CAP_MULTIPLIERS:
            cb = cap_blocks(stratum, mult)
            a, b = terminate(new, cb), terminate(old, cb)
            assert a == b, (stratum.key, kappa, mult, a, b)


@pytest.mark.parametrize("stratum", STRATA, ids=lambda s: s.key)
def test_measure_is_never_called_beyond_the_largest_frozen_cap(stratum):
    """This is what actually bounds the pilot's cost."""
    max_cap = cap_blocks(stratum, max(CAP_MULTIPLIERS))
    seen = []

    def measure(b):
        seen.append(b)
        return 5.0                     # never reaches target: worst case

    trace(measure=measure, b1=stratum.b1, target=1e-6, kappa=KAPPA_A,
          max_cap=max_cap)
    assert seen, "the rule must draw at least stage 1"
    assert max(seen) <= max_cap
    assert max(seen) + stratum.b_ref <= stratum.b_ref + max_cap


@pytest.mark.parametrize("stratum", STRATA, ids=lambda s: s.key)
def test_the_fixed_trace_never_flags_pool_exhaustion(stratum):
    max_cap = cap_blocks(stratum, max(CAP_MULTIPLIERS))
    for c in (0.001, 0.05, 0.5, 5.0, 500.0):
        t = trace(measure=lambda b, c=c: c * b ** -0.5, b1=stratum.b1,
                  target=0.03, kappa=KAPPA_A, max_cap=max_cap)
        assert not t.pool_exhausted
        for mult in CAP_MULTIPLIERS:
            o = terminate(t, cap_blocks(stratum, mult))
            assert o.status in (ATTAINED, PRECISION_LIMITED)


def test_the_observed_failing_case_now_terminates_normally():
    """The exact shape that aborted the first design run."""
    t1 = STRATA[0]
    max_cap = cap_blocks(t1, 12.0)
    t = trace(measure=lambda b: 1.2 * b ** -0.5, b1=48, target=0.06171,
              kappa=KAPPA_A, max_cap=max_cap)
    assert not t.pool_exhausted
    assert [s.blocks for s in t.stages] == [48]
    assert t.stages[0].next_blocks == 1211
    for mult in CAP_MULTIPLIERS:
        o = terminate(t, cap_blocks(t1, mult))
        assert o.status == PRECISION_LIMITED
        assert o.blocks == 48
        assert o.next_stage_blocks == 1211
