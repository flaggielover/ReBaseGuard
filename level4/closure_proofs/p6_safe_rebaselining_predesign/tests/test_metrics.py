"""Metric definitions, layer tagging, and the paired-effect utility."""
import numpy as np

from rebaseguard_p6.chain import simulate_policy_chain
from rebaseguard_p6.metrics import (
    METRIC_LAYER, OBSERVABLE, arl0, collapse_ratio, fap, frac_reuse,
    fresh_per_alarm, mean_weight, reference_rms, reused_per_alarm,
)
from rebaseguard_p6.policy import ConstantPolicy
from rebaseguard_p6.stats import (
    INSUFFICIENT_TAIL_EVENTS, batch_means, paired_effect, tail_event_check,
)


def _run(rho, m, k=None, seed=101, n_rep=64, n_cycles=40):
    return simulate_policy_chain(
        detector="cusum", policy=ConstantPolicy(rho=rho, m=m, k=k), n_rep=n_rep,
        n_cycles=n_cycles, burn_in=8, e0=0.0, rng=np.random.default_rng(seed))


def test_full_reuse_costs_in_control_arl_and_reference_accuracy():
    """The direction of ledger rows S3/S15 must be reproduced by the harness."""
    fresh, full = _run(0.0, 3), _run(1.0, 3)
    assert arl0(full).mean() < arl0(fresh).mean()
    assert reference_rms(full).mean() > reference_rms(fresh).mean()


def test_cost_model_charges_fresh_samples_only_when_rho_below_one():
    assert fresh_per_alarm(_run(1.0, 3)).mean() == 0.0
    assert fresh_per_alarm(_run(0.5, 3, k=7)).mean() == 7.0
    assert mean_weight(_run(0.5, 3)).mean() == 0.5


def test_reuse_count_respects_the_truncated_window():
    res = _run(0.5, 5)
    assert reused_per_alarm(res).max() <= 5.0
    assert 0.0 < frac_reuse(res).mean() < 1.0


def test_fap_and_collapse_are_well_formed():
    res = _run(1.0, 3)
    f = fap(res, horizon=100)
    assert ((f >= 0) & (f <= 1)).all()
    assert np.isfinite(collapse_ratio(res)).all()


def test_metric_layers_are_tagged():
    assert METRIC_LAYER["Arl0"] == OBSERVABLE
    assert METRIC_LAYER["Rms"] == "latent"


def test_paired_effect_reports_correlation_and_a_verdict():
    a, b = arl0(_run(0.2, 3)), arl0(_run(1.0, 3))
    eff = paired_effect(a, b, materiality=5.0, n_boot=2000,
                        rng=np.random.default_rng(0))
    assert eff.n_pairs == a.size
    assert eff.lo <= eff.estimate <= eff.hi
    assert eff.verdict in {"INCONCLUSIVE", "STATISTICALLY_RESOLVED",
                           "PRACTICALLY_MATERIAL"}


def test_tail_event_check_flags_under_powered_cells():
    assert tail_event_check(12) == INSUFFICIENT_TAIL_EVENTS
    assert tail_event_check(500) is None


def test_batch_means_returns_a_mean_and_a_standard_error():
    m, se = batch_means(np.random.default_rng(1).standard_normal(400))
    assert abs(m) < 0.5 and se > 0
