"""Structural properties of the two candidate estimators.

These tests are *identities and invariants*, not measurements.  None of them
compares a number against a scientific threshold.
"""
import math

import numpy as np
import pytest

from rebaseguard_p4_general.detectors import Detector, K_FROZEN, H_FROZEN, A_FROZEN
from rebaseguard_p4_general.families import REGISTRY
from rebaseguard_p4_general.simulate import stream_counter
from rebaseguard_p4z.analytic import FAMILY_KITS, alarm_bounds
from rebaseguard_p4z.rbscore import rb_score_batch
from rebaseguard_p4z.rbmap import rb_map_batch

CELLS = [("gaussian", "cusum", 2.0), ("t1p5", "sr", 20.0)]


def _run_score(name, kind, thr, m_grid=(1, 2, 3, 5), n=4000, seed=99, steps=20000):
    fam, kit, det = REGISTRY[name], FAMILY_KITS[name], Detector(kind, thr)
    rng = np.random.Generator(np.random.PCG64([seed, 0]))
    return rb_score_batch(
        family=fam, kit=kit, detector_kind=kind, threshold=thr, m_grid=m_grid,
        n_paths=n, rng=rng, max_steps=steps,
        new_state=det.new_state, step_fn=det.step,
    )


@pytest.mark.parametrize("name,kind,thr", CELLS)
def test_rb_score_is_deterministic_given_the_seed(name, kind, thr):
    a, ua, _ = _run_score(name, kind, thr)
    b, ub, _ = _run_score(name, kind, thr)
    assert ua == ub
    for m in a:
        assert np.array_equal(a[m], b[m])


@pytest.mark.parametrize("name,kind,thr", CELLS)
def test_rb_score_summand_has_a_finite_second_moment_signature(name, kind, thr):
    """The historical summand's tail is the family's own; the RB summand's is not.

    Checked structurally: the share of squared deviation carried by the single
    most extreme path.  This is Pilot-4's own concentration diagnostic, applied
    here as an invariant of the construction, not as a certificate.
    """
    vals, _, _ = _run_score(name, kind, thr)
    for m, x in vals.items():
        dev = (x - x.mean()) ** 2
        assert float(dev.max() / dev.sum()) < 0.10, (name, m)


def test_survival_residuals_are_bounded_by_the_forcing_increment():
    """The bounded-survival lemma, checked against the frozen recursions.

    ``forcing_increment()`` is already the constant discharge lemma L1 uses.
    """
    for kind, thr in (("cusum", H_FROZEN), ("sr", A_FROZEN)):
        det = Detector(kind, thr)
        c_d = det.forcing_increment()
        rng = np.random.Generator(np.random.PCG64([7, 0]))
        up, down = det.new_state(2000)
        active = np.ones(2000, bool)
        fam = REGISTRY["t1p5"]
        for step in range(1, 400):
            idx = np.flatnonzero(active)
            if idx.size == 0:
                break
            lower, upper = alarm_bounds(kind, thr, up[idx], down[idx], K_FROZEN)
            assert np.all(lower < 0.0) and np.all(upper > 0.0)
            assert np.all(np.abs(lower) <= c_d + 1e-9)
            assert np.all(upper <= c_d + 1e-9)
            z = fam.sample(rng, (int(idx.size),))
            nu_, nd_, crossed = det.step(up[idx], down[idx], z, step)
            # every residual that did NOT alarm is inside the bound
            assert np.all(np.abs(z[~crossed]) < c_d)
            up[idx], down[idx] = nu_, nd_
            active[idx[crossed]] = False


def test_alarm_bounds_agree_with_the_frozen_recursion_exactly():
    """``z >= U`` or ``z <= L`` must reproduce the frozen ``crossed`` flag."""
    rng = np.random.Generator(np.random.PCG64([5, 1]))
    for kind, thr in (("cusum", 5.0), ("sr", 520.886133602749)):
        det = Detector(kind, thr)
        up, down = det.new_state(3000)
        fam = REGISTRY["laplace"]
        active = np.ones(3000, bool)
        for step in range(1, 200):
            idx = np.flatnonzero(active)
            if idx.size == 0:
                break
            lower, upper = alarm_bounds(kind, thr, up[idx], down[idx], K_FROZEN)
            z = fam.sample(rng, (int(idx.size),))
            predicted = (z >= upper) | (z <= lower)
            nu_, nd_, crossed = det.step(up[idx], down[idx], z, step)
            assert np.array_equal(predicted, crossed), (kind, step)
            up[idx], down[idx] = nu_, nd_
            active[idx[crossed]] = False


@pytest.mark.parametrize("name,kind,thr", CELLS)
def test_rb_map_is_crn_coupled_and_reproducible(name, kind, thr):
    fam, kit, det = REGISTRY[name], FAMILY_KITS[name], Detector(kind, thr)
    kw = dict(family=fam, kit=kit, detector_kind=kind, threshold=thr,
              m_grid=(1, 2), n_paths=3000, seed=42, batch=0, max_steps=20000,
              new_state=det.new_state, step_fn=det.step,
              stream_counter=stream_counter)
    a = rb_map_batch(e_values=(0.05, -0.05), **kw)
    b = rb_map_batch(e_values=(0.05, -0.05), **kw)
    for e in a:
        for m in a[e]:
            assert np.array_equal(a[e][m], b[e][m])
    # the two shifted runs are genuinely different objects, not aliases
    assert not np.array_equal(a[0.05][1], a[-0.05][1])


def test_rb_map_richardson_rejects_a_non_halved_step_pair():
    from rebaseguard_p4z.rbmap import rb_map_derivative_batch
    with pytest.raises(ValueError, match="fd_steps"):
        rb_map_derivative_batch(fd_steps=(0.05, 0.03), m_grid=(1,))
