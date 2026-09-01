"""The observability audit, enforced rather than documented."""
import dataclasses

import numpy as np
import pytest

from rebaseguard_p6 import IMPLEMENTABLE, ORACLE
from rebaseguard_p6.chain import simulate_policy_chain
from rebaseguard_p6.policy import (
    AUDITED_OBSERVABLE_FIELDS, ConstantPolicy, CycleObservation, OracleObservation,
    OracleResetPolicy, PooledDisplacementPolicy, TauThresholdWindowPolicy,
    ZbarThresholdPolicy,
)

IMPLEMENTABLE_REGISTRY = [
    ConstantPolicy(rho=0.2, m=3),
    TauThresholdWindowPolicy(rho=0.2, m_short=1, m_long=5, tau_split=20),
    ZbarThresholdPolicy(m=3, rho_lo=0.0, rho_hi=0.5, q=0.5),
    PooledDisplacementPolicy(m=3, rho_lo=0.0, rho_hi=0.5, c=0.3),
]


def test_observation_field_set_matches_the_audit():
    got = tuple(f.name for f in dataclasses.fields(CycleObservation))
    assert got == AUDITED_OBSERVABLE_FIELDS


def test_no_latent_field_reachable_from_an_implementable_observation():
    """Latent quantities must be absent by NAME, not merely undocumented."""
    forbidden = {"e", "e_current", "e_start", "raw", "rbar", "r_bar", "shift",
                 "delta", "theta", "e_origin", "e_prev", "e_next"}
    names = {f.name.lower() for f in dataclasses.fields(CycleObservation)}
    assert not (names & forbidden), sorted(names & forbidden)
    # and none of them is reachable as an attribute either
    for bad in forbidden:
        assert not hasattr(CycleObservation, bad)


@pytest.mark.parametrize("policy", IMPLEMENTABLE_REGISTRY, ids=lambda p: p.name)
def test_registered_implementable_policies_declare_no_oracle(policy):
    assert policy.policy_class == IMPLEMENTABLE
    assert policy.requires_oracle is False


def test_oracle_policy_is_labelled_and_refuses_a_plain_observation():
    pol = OracleResetPolicy(m=3, c=0.5)
    assert pol.policy_class == ORACLE and pol.requires_oracle is True
    n = 4
    obs = CycleObservation(
        rep=np.arange(n), cycle=0, tau=np.full(n, 7), direction=np.ones(n, np.int8),
        stat_plus=np.zeros(n), stat_minus=np.zeros(n), overshoot=np.zeros(n),
        window=np.zeros((n, 3)), window_valid=np.ones((n, 3), bool),
        displacement=np.zeros(n), last_move=np.zeros(n),
        prev_tau=np.zeros(n, np.int64), prev_zbar=np.zeros(n),
        prev_rho=np.zeros(n), prev_m=np.full(n, 3), prev_k=np.full(n, 3),
    )
    with pytest.raises(TypeError):
        pol.decide(obs)
    assert isinstance(OracleObservation(e_current=np.zeros(n), shift=0.0,
                                        **{f.name: getattr(obs, f.name)
                                           for f in dataclasses.fields(obs)}),
                      CycleObservation)


def test_result_record_carries_the_policy_class():
    res = simulate_policy_chain(
        detector="cusum", policy=ConstantPolicy(rho=0.2, m=3), n_rep=8,
        n_cycles=6, burn_in=0, e0=0.0, rng=np.random.default_rng(3))
    assert res.policy_class == IMPLEMENTABLE


def test_history_channel_is_withheld_when_e0_is_known():
    """With a KNOWN e_0, displacement would equal the latent state exactly."""
    with pytest.raises(ValueError, match="leaks the latent state"):
        simulate_policy_chain(
            detector="cusum",
            policy=PooledDisplacementPolicy(m=3, rho_lo=0.0, rho_hi=0.5, c=0.3),
            n_rep=8, n_cycles=6, burn_in=0, e0=0.0,
            rng=np.random.default_rng(3))


def test_history_channel_is_available_when_e0_is_drawn_from_its_prior():
    res = simulate_policy_chain(
        detector="cusum",
        policy=PooledDisplacementPolicy(m=3, rho_lo=0.0, rho_hi=0.5, c=0.3),
        n_rep=16, n_cycles=8, burn_in=0, e0=None, m0=5,
        rng=np.random.default_rng(3))
    assert res.tau.shape == (16, 8)
    assert np.isfinite(res.e_start).all()
