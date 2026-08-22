"""Stage D multi-cycle chain."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chain import simulate_chain                             # noqa: E402


def _rng(*k):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(k))))


def test_fresh_policy_has_no_stopped_selection():
    """At rho = 0 the reference is a fresh estimate of m observations, so
    e ~ N(0, 1/m) INDEPENDENT of the stopping event.

    Note the ARL is NOT 465 here: e is not zero, it is N(0, 1/m), and the ARL
    falls with |e|. What rho = 0 guarantees is the absence of stopped
    selection -- no serial correlation in e, no alarm alternation.
    """
    m = 10
    r = simulate_chain(m=m, rho=0.0, n_rep=3000, n_cycles=40, burn_in=10,
                       rng=_rng(20261031, 20))
    e = r.e_start[:, 10:]
    assert abs(e.mean()) < 0.01, e.mean()
    assert e.var() == pytest.approx(1.0 / m, rel=0.08), e.var()
    assert abs(r.e_acf1.mean()) < 0.05, r.e_acf1.mean()
    assert abs(r.direction_acf1.mean()) < 0.10, r.direction_acf1.mean()


def test_fresh_beats_full_reuse_on_in_control_arl():
    """The stopped-selection penalty: at the same m, full reuse gives shorter
    in-control cycles than the fresh policy."""
    kw = dict(m=10, n_rep=3000, n_cycles=40, burn_in=10)
    fresh = simulate_chain(rho=0.0, rng=_rng(20261031, 28), **kw)
    reuse = simulate_chain(rho=1.0, rng=_rng(20261031, 29), **kw)
    assert reuse.cycle_arl.mean() < fresh.cycle_arl.mean()


def test_fresh_policy_approaches_465_as_m_grows():
    """As m -> inf the fresh estimate concentrates at e = 0 and the cycle ARL
    approaches the frozen in-control value."""
    a = simulate_chain(m=10, rho=0.0, n_rep=2000, n_cycles=30, burn_in=5,
                       rng=_rng(20261031, 30))
    b = simulate_chain(m=400, rho=0.0, n_rep=2000, n_cycles=30, burn_in=5,
                       rng=_rng(20261031, 31))
    assert b.cycle_arl.mean() > a.cycle_arl.mean()
    assert abs(b.cycle_arl.mean() - 465.0) < 60.0, b.cycle_arl.mean()


def test_full_reuse_shortens_cycles_and_alternates():
    """At rho = 1 with small m, stopped selection biases the reference and the
    chain alternates -- the Level 1-3 phenomenon, in chain form."""
    r = simulate_chain(m=10, rho=1.0, n_rep=3000, n_cycles=40, burn_in=10,
                       rng=_rng(20261031, 21))
    assert r.cycle_arl.mean() < 250.0, r.cycle_arl.mean()
    assert r.direction_acf1.mean() < -0.5, r.direction_acf1.mean()


def test_larger_m_moves_toward_the_fresh_limit():
    a = simulate_chain(m=10, rho=1.0, n_rep=3000, n_cycles=40, burn_in=10,
                       rng=_rng(20261031, 22))
    b = simulate_chain(m=100, rho=1.0, n_rep=3000, n_cycles=40, burn_in=10,
                       rng=_rng(20261031, 23))
    assert b.cycle_arl.mean() > a.cycle_arl.mean()
    assert b.reference_mse.mean() < a.reference_mse.mean()
    assert b.direction_acf1.mean() > a.direction_acf1.mean()


def test_shift_is_applied_at_the_declared_cycle():
    sc = 12
    r = simulate_chain(m=10, rho=1.0, n_rep=4000, n_cycles=sc + 1, burn_in=5,
                       rng=_rng(20261031, 24), shift=1.5, shift_cycle=sc)
    pre = r.e_start[:, sc - 1].mean()
    at = r.e_start[:, sc].mean()
    assert at < pre - 1.0, (pre, at)
    assert r.tau[:, sc].mean() < r.tau[:, sc - 1].mean()


def test_no_shift_leaves_shift_cycle_unavailable():
    r = simulate_chain(m=5, rho=1.0, n_rep=200, n_cycles=6, burn_in=1,
                       rng=_rng(20261031, 25))
    with pytest.raises(ValueError):
        _ = r.tau_at_shift


def test_chain_is_deterministic_given_the_seed():
    kw = dict(m=10, rho=1.0, n_rep=800, n_cycles=15, burn_in=3)
    a = simulate_chain(rng=_rng(20261031, 26), **kw)
    b = simulate_chain(rng=_rng(20261031, 26), **kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_start, b.e_start)


def test_every_cycle_records_a_positive_tau():
    r = simulate_chain(m=20, rho=1.0, n_rep=500, n_cycles=12, burn_in=2,
                       rng=_rng(20261031, 27))
    assert (r.tau > 0).all()
    assert set(np.unique(r.direction)) <= {-1, 1}
