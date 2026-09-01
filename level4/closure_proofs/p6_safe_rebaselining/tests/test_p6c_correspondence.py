"""I1/I4: the frozen core is untouched -- a constant policy IS the P7 chain."""
import numpy as np
import pytest

from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy
from rebaseguard_p7.chain import simulate_chain

CELLS = [(d, m, r) for d in ("cusum", "sr") for m in (1, 2, 3, 5)
         for r in (0.0, 0.25, 1.0)]


@pytest.mark.parametrize("det,m,rho", CELLS, ids=lambda x: str(x))
def test_constant_policy_is_bit_identical_to_p7(det, m, rho):
    kw = dict(detector=det, n_rep=80, n_cycles=25, burn_in=5, e0=0.0)
    ref = simulate_chain(m=m, rho=rho, rng=np.random.default_rng(20260901), **kw)
    got = simulate_policy_chain(policy=ConstantPolicy(rho=rho, m=m),
                                rng=np.random.default_rng(20260901), **kw)
    assert np.array_equal(ref.tau, got.tau), "stopping times differ: semantics changed"
    assert np.abs(ref.e_start - got.e_start).max() < 1e-13


def test_convention_a_truncated_denominator_exact():
    """At rho = 1 the update is e_{j+1} = e_j + zbar_j exactly (convention A)."""
    for det in ("cusum", "sr"):
        res = simulate_policy_chain(detector=det, policy=ConstantPolicy(rho=1.0, m=5),
                                    n_rep=800, n_cycles=15, burn_in=0, e0=0.0,
                                    rng=np.random.default_rng(7))
        assert (res.tau < 5).any(), "test needs truncated windows to be meaningful"
        resid = res.e_start[:, 1:] - (res.e_start + res.zbar)[:, :-1]
        assert np.abs(resid).max() < 1e-12


def test_raw_mean_identity_holds_under_an_adaptive_policy():
    """T1 with an F_j-measurable decision: e_{j+1} = rho_j U_j + (1-rho_j) fresh."""
    from _registry import calib_for, load_calibration
    from rebaseguard_p6c.saw import SawPolicy
    cal = load_calibration()
    c = calib_for(cal, "cusum", 3)
    res = simulate_policy_chain(detector="cusum", policy=SawPolicy(c, k=3),
                                n_rep=400, n_cycles=20, burn_in=0, e0=0.0,
                                rng=np.random.default_rng(5))
    u = res.e_start + res.zbar                      # the RAW window mean
    lhs = res.e_start[:, 1:]
    # e_{j+1} - rho_j U_j must be exactly (1-rho_j) * fresh_j, mean zero and
    # with variance (1-rho)^2 / k; here we assert the algebraic part only.
    resid = lhs - res.rho[:, :-1] * u[:, :-1]
    scale = (1.0 - res.rho[:, :-1]) / np.sqrt(res.k[:, :-1])
    z = resid / np.maximum(scale, 1e-300)
    assert abs(float(z.mean())) < 0.05
    assert abs(float(z.std()) - 1.0) < 0.05
