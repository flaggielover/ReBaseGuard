"""The observability audit, enforced rather than documented (I2, I3, C3)."""
import dataclasses

import numpy as np
import pytest

from rebaseguard_p6c import IMPLEMENTABLE, ORACLE
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import (
    AUDITED_OBSERVABLE_FIELDS, CappedReusePolicy, ConfidenceGatedPolicy,
    ConstantPolicy, CycleObservation, OracleObservation, OracleResetPolicy,
    OracleShiftAwarePolicy, OvershootPolicy, TauThresholdWindowPolicy,
    WindowDispersionPolicy, ZbarThresholdPolicy,
)
from rebaseguard_p6c.saw import (
    OracleSawPolicy, OracleTailSawPolicy, SawPolicy, SawTailPolicy,
)
from _registry import calib_for, load_calibration

CAL = calib_for(load_calibration(), "cusum", 3)

IMPLEMENTABLE_REGISTRY = [
    ConstantPolicy(rho=0.2, m=3),
    TauThresholdWindowPolicy(rho=0.2, m_short=1, m_long=5, tau_split=20),
    ZbarThresholdPolicy(m=3, rho_lo=0.05, rho_hi=0.5, q=1.4),
    OvershootPolicy(m=3, rho_hi=0.5, a=1.0),
    WindowDispersionPolicy(m=3, rho_hi=0.5, a=1.0),
    CappedReusePolicy(m=3, rho=0.5, n_max=3),
    ConfidenceGatedPolicy(m=3, rho_hi=0.5, q=1.4),
    SawPolicy(CAL, k=3, mode="full"),
    SawPolicy(CAL, k=3, mode="naive"),
    SawPolicy(CAL, k=3, mode="flat", v_bar=1.3),
    SawTailPolicy(CAL, 0.28, k=3),
]
ORACLE_REGISTRY = [
    OracleResetPolicy(m=3, c=0.3),
    OracleShiftAwarePolicy(m=3, rho=0.2, guard=0.3),
    OracleSawPolicy(CAL, k=3),
    OracleTailSawPolicy(CAL, 0.28, k=3),
]


def test_observation_field_set_matches_the_audit():
    got = tuple(f.name for f in dataclasses.fields(CycleObservation))
    assert got == AUDITED_OBSERVABLE_FIELDS


def test_no_latent_field_reachable_from_an_implementable_observation():
    forbidden = {"e", "e_current", "e_start", "raw", "rbar", "r_bar", "shift",
                 "delta", "theta", "e_origin", "e_prev", "e_next", "u", "u_raw"}
    names = {f.name.lower() for f in dataclasses.fields(CycleObservation)}
    assert not (names & forbidden), sorted(names & forbidden)
    for bad in forbidden:
        assert not hasattr(CycleObservation, bad)


@pytest.mark.parametrize("policy", IMPLEMENTABLE_REGISTRY, ids=lambda p: p.name)
def test_registered_implementable_policies_declare_no_oracle(policy):
    assert policy.policy_class == IMPLEMENTABLE
    assert policy.requires_oracle is False


@pytest.mark.parametrize("policy", ORACLE_REGISTRY, ids=lambda p: p.name)
def test_oracle_policies_declare_themselves_and_refuse_plain_observations(policy):
    assert policy.policy_class == ORACLE
    assert policy.requires_oracle is True
    n = 4
    obs = CycleObservation(
        rep=np.arange(n), cycle=0, tau=np.full(n, 5), direction=np.ones(n, np.int8),
        stat_plus=np.zeros(n), stat_minus=np.zeros(n), overshoot=np.zeros(n),
        window=np.zeros((n, policy.max_m)), window_valid=np.ones((n, policy.max_m), bool),
        displacement=np.zeros(n), last_move=np.zeros(n), prev_tau=np.zeros(n, np.int64),
        prev_zbar=np.zeros(n), prev_rho=np.zeros(n), prev_m=np.full(n, 3, np.int64),
        prev_k=np.full(n, 3, np.int64))
    with pytest.raises(TypeError):
        policy.decide(obs)


def test_saw_never_touches_the_history_channel():
    """SAW is memoryless, so it must be legal in BOTH e_0 regimes (audit 4a)."""
    p = SawPolicy(CAL, k=3, mode="full")
    assert p.uses_history is False
    for e0, m0 in ((0.0, 1), (None, 50)):
        simulate_policy_chain(detector="cusum", policy=p, n_rep=40, n_cycles=6,
                              burn_in=0, e0=e0, m0=m0,
                              rng=np.random.default_rng(2))


def test_saw_decision_depends_only_on_the_audited_observables():
    """Perturbing a latent-carrying field must not change any SAW decision."""
    p = SawPolicy(CAL, k=3, mode="full")
    n = 6
    rng = np.random.default_rng(0)
    base = dict(rep=np.arange(n), cycle=0, tau=rng.integers(1, 40, n),
                direction=np.ones(n, np.int8), stat_plus=rng.normal(size=n),
                stat_minus=rng.normal(size=n), overshoot=rng.normal(size=n),
                window=rng.normal(size=(n, 3)), window_valid=np.ones((n, 3), bool),
                displacement=rng.normal(size=n), last_move=rng.normal(size=n),
                prev_tau=rng.integers(1, 40, n), prev_zbar=rng.normal(size=n),
                prev_rho=rng.random(n), prev_m=np.full(n, 3, np.int64),
                prev_k=np.full(n, 3, np.int64))
    d0 = p.decide(CycleObservation(**base))
    for field in ("displacement", "last_move", "prev_tau", "prev_zbar",
                  "prev_rho", "stat_plus", "stat_minus", "overshoot", "direction"):
        pert = dict(base)
        pert[field] = base[field] + 7.0 if base[field].dtype.kind == "f" \
            else base[field] * 0 + 3
        d1 = p.decide(CycleObservation(**pert))
        assert np.array_equal(d0.rho, d1.rho), f"SAW reacted to {field}"
