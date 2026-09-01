"""The object under confirmation is the object that was adjudicated.

T6-B is `EXACT_VALID` for a memoryless policy with ``rho < rho_max``; these
tests assert SAW-M still satisfies the theorem's hypotheses field by field, and
that the frozen detector semantics are untouched.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from rebaseguard_p6c.calibrate import RHO_MAX, S_FLOOR, SawCalibration
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy, CycleObservation
from rebaseguard_p6c.saw import SawPolicy
from rebaseguard_p7.chain import simulate_chain

CAL_PATH = (Path(__file__).resolve().parents[2] / "p6_safe_rebaselining"
            / "results" / "calibration.json")
#: THEOREM_SCOPE.md section 1: the eight fields a T6-B policy may NOT read.
EXCLUDED_FIELDS = ("cycle", "prev_tau", "prev_zbar", "prev_rho", "prev_m",
                   "prev_k", "displacement", "last_move")


def _cal(det, m):
    d = json.loads(CAL_PATH.read_text())[f"{det}_m{m}"]["final"]
    return SawCalibration(**d)


@pytest.mark.parametrize("det,m,rho", [(d, m, r) for d in ("cusum", "sr")
                                       for m in (1, 3) for r in (0.0, 0.25, 1.0)])
def test_frozen_detector_semantics_are_untouched(det, m, rho):
    kw = dict(detector=det, n_rep=60, n_cycles=20, burn_in=5, e0=0.0)
    ref = simulate_chain(m=m, rho=rho, rng=np.random.default_rng(20260901), **kw)
    got = simulate_policy_chain(policy=ConstantPolicy(rho=rho, m=m),
                                rng=np.random.default_rng(20260901), **kw)
    assert np.array_equal(ref.tau, got.tau)
    assert np.abs(ref.e_start - got.e_start).max() < 1e-13


@pytest.mark.parametrize("det,m", [(d, m) for d in ("cusum", "sr")
                                   for m in (1, 2, 3, 5)])
def test_saw_is_memoryless_in_the_sense_T6B_requires(det, m):
    """Perturb each excluded field; no SAW-M decision may move."""
    p = SawPolicy(_cal(det, m), k=m, mode="full")
    assert p.uses_history is False
    n = 6
    rng = np.random.default_rng(0)
    base = dict(rep=np.arange(n), cycle=0, tau=rng.integers(1, 60, n),
                direction=np.ones(n, np.int8), stat_plus=rng.normal(size=n),
                stat_minus=rng.normal(size=n), overshoot=rng.normal(size=n),
                window=rng.normal(size=(n, m)),
                window_valid=np.ones((n, m), bool),
                displacement=rng.normal(size=n), last_move=rng.normal(size=n),
                prev_tau=rng.integers(1, 60, n), prev_zbar=rng.normal(size=n),
                prev_rho=rng.random(n), prev_m=np.full(n, m, np.int64),
                prev_k=np.full(n, m, np.int64))
    d0 = p.decide(CycleObservation(**base))
    for field in EXCLUDED_FIELDS:
        pert = dict(base)
        v = base[field]
        pert[field] = (v + 11.0 if isinstance(v, np.ndarray) and v.dtype.kind == "f"
                       else (v * 0 + 5 if isinstance(v, np.ndarray) else 7))
        assert np.array_equal(d0.rho, p.decide(CycleObservation(**pert)).rho), field


@pytest.mark.parametrize("det,m", [(d, m) for d in ("cusum", "sr")
                                   for m in (1, 2, 3, 5)])
def test_rho_is_bounded_away_from_one_as_T6B_requires(det, m):
    res = simulate_policy_chain(detector=det, policy=SawPolicy(_cal(det, m), k=m),
                                n_rep=300, n_cycles=30, burn_in=0, e0=0.0,
                                rng=np.random.default_rng(4))
    assert res.rho.max() < RHO_MAX - 1e-6      # the cap is non-binding
    assert res.rho.min() > 0.0
    assert res.rho.max() < 1.0                 # the T6-B hypothesis itself


def test_saw_is_sign_equivariant():
    p = SawPolicy(_cal("cusum", 3), k=3)
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


def test_fixed_k_throughout_so_T6C_applies():
    """T6-C is exact only for FIXED k; every headline cell must use one."""
    for det in ("cusum", "sr"):
        for m in (1, 2, 3, 5):
            res = simulate_policy_chain(
                detector=det, policy=SawPolicy(_cal(det, m), k=m),
                n_rep=120, n_cycles=20, burn_in=0, e0=0.0,
                rng=np.random.default_rng(8))
            assert len(np.unique(res.k)) == 1, (det, m)
            assert int(res.k[0, 0]) == m


def test_calibration_constants_are_the_frozen_p6_ones():
    """P6R must not re-derive the method's constants."""
    d = json.loads(CAL_PATH.read_text())["cusum_m3"]["final"]
    assert abs(d["g0"] - 0.93840) < 1e-4
    assert abs(d["g1"] + 1.06668) < 1e-4
    assert abs(d["s0"] - 0.06263) < 1e-4
    assert d["s1"] > 0 and d["s0"] > S_FLOOR
