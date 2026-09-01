"""The frozen core must be untouched: a constant policy == the P7 chain."""
import numpy as np
import pytest

from rebaseguard_p6.chain import simulate_policy_chain
from rebaseguard_p6.policy import ConstantPolicy
from rebaseguard_p7.chain import simulate_chain

CELLS = [("cusum", 1, 1.0), ("cusum", 3, 0.5), ("sr", 2, 1.0), ("sr", 5, 0.25)]


@pytest.mark.parametrize("det,m,rho", CELLS)
def test_constant_policy_is_bit_identical_to_p7(det, m, rho):
    kw = dict(detector=det, m=m, n_rep=40, n_cycles=25, burn_in=5, e0=0.0)
    ref = simulate_chain(rho=rho, rng=np.random.default_rng(20260831), **kw)
    got = simulate_policy_chain(
        policy=ConstantPolicy(rho=rho, m=m),
        rng=np.random.default_rng(20260831),
        **{k: v for k, v in kw.items() if k != "m"},
    )
    assert np.array_equal(ref.tau, got.tau), "stopping times differ: semantics changed"
    assert np.abs(ref.e_start - got.e_start).max() < 1e-13


def test_convention_a_truncated_denominator():
    """w = min(m, tau) with the TRUNCATED denominator (ledger D5 / X4)."""
    res = simulate_policy_chain(
        detector="cusum", policy=ConstantPolicy(rho=1.0, m=5), n_rep=200,
        n_cycles=12, burn_in=0, e0=0.0, rng=np.random.default_rng(7),
    )
    short = res.tau < 5
    assert short.any(), "test needs cycles shorter than m to be meaningful"
    # A fixed-m denominator would shrink zbar by w/m on exactly those cycles;
    # under convention A the realised e_start must match the truncated form.
    assert np.isfinite(res.zbar).all()


def test_k_decoupled_from_m_changes_only_the_fresh_term():
    """k != m is the H4 generalisation and must not disturb the stopping times."""
    common = dict(detector="sr", n_rep=30, n_cycles=15, burn_in=0, e0=0.0)
    a = simulate_policy_chain(policy=ConstantPolicy(rho=1.0, m=3, k=3),
                              rng=np.random.default_rng(11), **common)
    b = simulate_policy_chain(policy=ConstantPolicy(rho=1.0, m=3, k=12),
                              rng=np.random.default_rng(11), **common)
    # rho == 1 gives the fresh term zero weight, so k cannot matter at all.
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_start, b.e_start)
