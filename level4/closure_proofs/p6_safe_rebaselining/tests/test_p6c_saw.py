"""The method itself: the derivation, the ladder, the theory's own identities."""
import numpy as np
import pytest

from rebaseguard_p6c.calibrate import RHO_MAX, S_FLOOR, SawCalibration
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy
from rebaseguard_p6c.saw import OracleSawPolicy, SawPolicy, _rho_from_v
from _registry import calib_for, load_calibration

CAL_ALL = load_calibration()


def test_rho_star_is_the_exact_minimiser_of_the_one_step_quadratic():
    """Lemma 3.1: h(rho) = rho^2 V + (1-rho)^2 nu is minimised at nu/(V+nu)."""
    rng = np.random.default_rng(0)
    for _ in range(200):
        v = float(rng.uniform(0.01, 10))
        nu = float(rng.uniform(0.05, 2))
        rho = nu / (v + nu)
        grid = np.linspace(0, 1, 20001)
        h = grid ** 2 * v + (1 - grid) ** 2 * nu
        assert abs(grid[h.argmin()] - rho) < 1e-3
        assert abs(h.min() - nu * v / (v + nu)) < 1e-8


def test_excess_risk_identity():
    """h(rho) - h(rho*) = (V + nu)(rho - rho*)^2, exactly."""
    rng = np.random.default_rng(1)
    v, nu = rng.uniform(0.01, 5, 500), rng.uniform(0.05, 2, 500)
    rho = rng.random(500)
    rs = nu / (v + nu)
    lhs = (rho ** 2 * v + (1 - rho) ** 2 * nu) - nu * v / (v + nu)
    rhs = (v + nu) * (rho - rs) ** 2
    assert np.abs(lhs - rhs).max() < 1e-12


def test_q_star_is_strictly_concave_so_the_jensen_gap_is_positive():
    """T6-C(ii): E[Q*(V)] < Q*(E V) for any non-degenerate V."""
    rng = np.random.default_rng(2)
    for nu in (0.2, 1.0, 2.0):
        v = rng.chisquare(1, 200_000) * 1.7 + 0.1
        q = nu * v / (v + nu)
        vbar = v.mean()
        assert q.mean() < nu * vbar / (vbar + nu)


def test_flat_mode_is_exactly_a_fixed_rho_policy():
    """The sensor ablation must land exactly on the incumbent method."""
    c = calib_for(CAL_ALL, "cusum", 3)
    vbar = CAL_ALL["cusum_m3"]["v_bar"]
    flat = SawPolicy(c, k=3, mode="flat", v_bar=vbar)
    rho = float(_rho_from_v(np.array([vbar]), 1.0 / 3)[0])
    const = ConstantPolicy(rho=rho, m=3, k=3)
    kw = dict(detector="cusum", n_rep=60, n_cycles=12, burn_in=0, e0=0.0)
    a = simulate_policy_chain(policy=flat, rng=np.random.default_rng(9), **kw)
    b = simulate_policy_chain(policy=const, rng=np.random.default_rng(9), **kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.abs(a.e_start - b.e_start).max() < 1e-12


@pytest.mark.parametrize("det,m", [(d, m) for d in ("cusum", "sr")
                                   for m in (1, 2, 3, 5)])
def test_saw_rho_is_bounded_away_from_one_as_T6B_requires(det, m):
    c = calib_for(CAL_ALL, det, m)
    res = simulate_policy_chain(detector=det, policy=SawPolicy(c, k=m),
                                n_rep=300, n_cycles=30, burn_in=0, e0=0.0,
                                rng=np.random.default_rng(4))
    assert res.rho.max() <= RHO_MAX + 1e-12
    # the structural cap must be non-binding: the plug-in itself keeps rho < 1
    assert res.rho.max() < RHO_MAX - 1e-6
    assert res.rho.min() > 0.0


def test_saw_is_sign_equivariant():
    """T6-B(g): the decision depends on zbar only through zbar^2."""
    from rebaseguard_p6c.policy import CycleObservation
    c = calib_for(CAL_ALL, "cusum", 3)
    p = SawPolicy(c, k=3)
    n = 5
    rng = np.random.default_rng(3)
    w = rng.normal(size=(n, 3))
    kw = dict(rep=np.arange(n), cycle=0, tau=np.array([2, 7, 15, 40, 3]),
              stat_plus=np.zeros(n), stat_minus=np.zeros(n),
              overshoot=np.zeros(n), window_valid=np.ones((n, 3), bool),
              displacement=np.zeros(n), last_move=np.zeros(n),
              prev_tau=np.zeros(n, np.int64), prev_zbar=np.zeros(n),
              prev_rho=np.zeros(n), prev_m=np.full(n, 3, np.int64),
              prev_k=np.full(n, 3, np.int64))
    a = p.decide(CycleObservation(window=w, direction=np.ones(n, np.int8), **kw))
    b = p.decide(CycleObservation(window=-w, direction=-np.ones(n, np.int8), **kw))
    assert np.allclose(a.rho, b.rho)


def test_calibration_reproduces_its_own_regression():
    """The stored constants must be the least-squares fit they claim to be."""
    from rebaseguard_p6c.runner import _collect
    c = calib_for(CAL_ALL, "cusum", 3)
    res = simulate_policy_chain(detector="cusum", policy=SawPolicy(c, k=3),
                                n_rep=800, n_cycles=80, burn_in=15, e0=0.0,
                                rng=np.random.default_rng(77))
    zb, tau, w, rbar = _collect(res, 3)
    X = np.column_stack([zb, zb / np.sqrt(tau)])
    coef = np.linalg.lstsq(X, rbar, rcond=None)[0]
    assert abs(coef[0] - c.g0) < 0.02
    assert abs(coef[1] - c.g1) < 0.06
    mu, s = c.features(zb, tau, w)
    assert (s >= S_FLOOR).all()
    assert float(np.corrcoef(rbar, mu)[0, 1]) > 0.9


def test_oracle_saw_dominates_saw_on_the_one_step_criterion():
    """Z1 is the ceiling of the ladder: it uses the realised U_j^2."""
    c = calib_for(CAL_ALL, "cusum", 3)
    kw = dict(detector="cusum", n_rep=3000, n_cycles=60, burn_in=15, e0=0.0)
    a = simulate_policy_chain(policy=SawPolicy(c, k=3),
                              rng=np.random.default_rng(21), **kw)
    b = simulate_policy_chain(policy=OracleSawPolicy(c, k=3),
                              rng=np.random.default_rng(21), **kw)
    assert (b.post(b.e_start) ** 2).mean() < (a.post(a.e_start) ** 2).mean()
