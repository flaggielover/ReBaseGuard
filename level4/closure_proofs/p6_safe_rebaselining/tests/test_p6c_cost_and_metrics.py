"""Cost accounting, metric definitions, determinism, and seed separation."""
import numpy as np
import pytest

from rebaseguard_p6c import metrics as M
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy
from rebaseguard_p6c.saw import SawPolicy
from rebaseguard_p6c.seeds import assert_disjoint, generator, seed_sequence
from _registry import calib_for, load_calibration

CAL = calib_for(load_calibration(), "cusum", 3)


def _run(policy, **kw):
    base = dict(detector="cusum", n_rep=200, n_cycles=30, burn_in=5, e0=0.0,
                rng=np.random.default_rng(1))
    base.update(kw)
    return simulate_policy_chain(policy=policy, **base)


def test_primary_cost_is_k_when_any_fresh_baseline_is_collected():
    """C_fresh = k_j * 1{rho_j < 1}: the approved primary model."""
    res = _run(ConstantPolicy(rho=0.2, m=3, k=7))
    assert np.allclose(M.fresh_per_alarm(res), 7.0)
    res1 = _run(ConstantPolicy(rho=1.0, m=3, k=7))
    assert np.allclose(M.fresh_per_alarm(res1), 0.0)


def test_full_reuse_is_free_in_samples_and_saw_is_not():
    assert float(M.fresh_per_alarm(_run(ConstantPolicy(rho=1.0, m=3))).mean()) == 0.0
    assert float(M.fresh_per_alarm(_run(SawPolicy(CAL, k=3))).mean()) == 3.0


def test_proportional_cost_is_the_declared_sensitivity_not_the_primary():
    res = _run(ConstantPolicy(rho=0.25, m=4, k=4))
    assert np.allclose(M.fresh_per_alarm(res), 4.0)
    assert np.allclose(M.fresh_proportional(res), 3.0)


def test_reuse_uses_convention_a_truncated_window():
    res = _run(ConstantPolicy(rho=0.5, m=5), n_rep=500)
    w = np.minimum(res.post(res.m), res.post(res.tau))
    assert np.allclose(M.reused_per_alarm(res), w.mean(axis=1))
    assert (w <= 5).all()


def test_metric_layers_forbid_gating_on_a_surrogate():
    assert M.METRIC_LAYER["Rms"] == M.LATENT
    assert M.METRIC_LAYER["OutCal"] == M.LATENT
    assert M.METRIC_LAYER["Arl0"] == M.OBSERVABLE
    assert M.METRIC_LAYER["Dtail"] == M.OBSERVABLE
    assert M.METRIC_LAYER["Fresh"] == M.COST


def test_arl0_and_fap_definitions():
    res = _run(ConstantPolicy(rho=0.2, m=3))
    assert np.allclose(M.arl0(res), res.tau[:, 5:].mean(axis=1))
    assert np.allclose(M.fap(res, 100), (res.tau[:, 5:] <= 100).mean(axis=1))
    assert np.allclose(M.rate_per_1000(res), 1000.0 / M.arl0(res))


def test_collapse_ratio_is_cycle2_over_cycle1():
    res = _run(ConstantPolicy(rho=1.0, m=3))
    assert np.allclose(M.collapse_ratio(res), res.tau[:, 1] / res.tau[:, 0])


def test_determinism_of_a_stateful_policy_and_of_saw():
    from rebaseguard_p6c.policy import CappedReusePolicy
    for pol_factory in (lambda: SawPolicy(CAL, k=3),
                        lambda: CappedReusePolicy(m=3, rho=0.5, n_max=3)):
        a = _run(pol_factory(), rng=np.random.default_rng(31))
        b = _run(pol_factory(), rng=np.random.default_rng(31))
        assert np.array_equal(a.tau, b.tau)
        assert np.array_equal(a.rho, b.rho)
        assert np.array_equal(a.e_start, b.e_start)


def test_stateful_policy_resets_between_runs():
    from rebaseguard_p6c.policy import CappedReusePolicy
    p = CappedReusePolicy(m=3, rho=0.5, n_max=2)
    a = _run(p, rng=np.random.default_rng(41))
    b = _run(p, rng=np.random.default_rng(41))       # same object, re-used
    assert np.array_equal(a.rho, b.rho), "policy state leaked across runs"


def test_seed_families_are_disjoint():
    assert_disjoint(detector="cusum", m=3, policy_id="p", cell_tag="c")
    for f in ("tune", "eval", "replay"):
        s1 = seed_sequence(family=f, detector="cusum", m=3, policy_id="p")
        s2 = seed_sequence(family=f, detector="cusum", m=3, policy_id="p")
        assert s1.entropy == s2.entropy
    with pytest.raises(ValueError):
        seed_sequence(family="nope", detector="cusum", m=3, policy_id="p")


def test_seed_streams_differ_across_cells_and_blocks():
    heads = set()
    for cell in ("a", "b"):
        for block in (0, 1):
            g = generator(family="eval", detector="sr", m=2, policy_id="p",
                          cell_tag=cell, block=block)
            heads.add(tuple(g.standard_normal(4).round(12).tolist()))
    assert len(heads) == 4
