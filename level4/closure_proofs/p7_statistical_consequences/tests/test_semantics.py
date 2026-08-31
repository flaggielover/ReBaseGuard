"""Frozen semantics that P7's conclusions depend on."""
import numpy as np
import pytest

from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD
from rebaseguard_p7.cycles import simulate_cycles


def _rng(seed):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))


@pytest.mark.parametrize("det,thr", [(CUSUM, CUSUM_THRESHOLD),
                                     (SR, SR_THRESHOLD)])
def test_shift_and_reference_error_are_the_same_code_path(det, thr):
    """A process shift +D is exactly the reference-error offset -D."""
    a = simulate_cycles(detector=det, e=0.0, delta=0.7, n_paths=3000,
                        m_grid=(1,), rng=_rng(55), threshold=thr)
    b = simulate_cycles(detector=det, e=-0.7, delta=0.0, n_paths=3000,
                        m_grid=(1,), rng=_rng(55), threshold=thr)
    assert np.array_equal(a.tau, b.tau)
    assert np.allclose(a.zbar, b.zbar)


@pytest.mark.parametrize("det,thr", [(CUSUM, CUSUM_THRESHOLD),
                                     (SR, SR_THRESHOLD)])
def test_no_censoring(det, thr):
    """Every cycle alarms; max_steps is an error, never a silent truncation."""
    with pytest.raises(RuntimeError):
        simulate_cycles(detector=det, e=0.0, n_paths=200, m_grid=(1,),
                        rng=_rng(9), threshold=thr, max_steps=3)


@pytest.mark.parametrize("det,thr", [(CUSUM, CUSUM_THRESHOLD),
                                     (SR, SR_THRESHOLD)])
def test_alarm_is_inclusive_and_post_update(det, thr):
    cs = simulate_cycles(detector=det, e=0.0, n_paths=500, m_grid=(1,),
                         rng=_rng(3), threshold=thr)
    assert (cs.tau >= 1).all()
    # the terminal increment is included: zbar at m=1 is exactly z_tau, so the
    # stopped sum of a tau=1 path equals its window mean
    one = cs.tau == 1
    if one.any():
        assert np.allclose(cs.zbar[0][one], cs.T[one])


def test_symmetry_of_the_response_functions():
    """A is even and g_m is odd, to Monte Carlo error (theorem-level symmetry)."""
    n = 120_000
    pos = simulate_cycles(detector=CUSUM, e=0.25, n_paths=n, m_grid=(1, 5),
                          rng=_rng(101), threshold=CUSUM_THRESHOLD)
    neg = simulate_cycles(detector=CUSUM, e=-0.25, n_paths=n, m_grid=(1, 5),
                          rng=_rng(202), threshold=CUSUM_THRESHOLD)
    se = np.sqrt(pos.tau.var(ddof=1) / n + neg.tau.var(ddof=1) / n)
    assert abs(pos.tau.mean() - neg.tau.mean()) < 4 * se
    for j in (0, 1):
        s = np.sqrt(pos.zbar[j].var(ddof=1) / n + neg.zbar[j].var(ddof=1) / n)
        assert abs(pos.zbar[j].mean() + neg.zbar[j].mean()) < 4 * s
