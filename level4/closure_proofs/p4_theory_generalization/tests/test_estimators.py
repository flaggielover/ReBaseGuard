"""The estimator layer: batch statistics and the Richardson combination."""

from __future__ import annotations

import math

import numpy as np
import pytest

from rebaseguard_p4_general.detectors import Detector
from rebaseguard_p4_general.estimators import (
    correspondence, route_a, route_b, summarise,
)
from rebaseguard_p4_general.families import REGISTRY


def test_summarise_uses_the_spread_of_batch_means():
    values = [1.0, 2.0, 3.0, 4.0]
    estimate = summarise(values)
    assert estimate.mean == pytest.approx(2.5)
    assert estimate.se == pytest.approx(np.std(values, ddof=1) / 2.0)
    assert estimate.batches == 4


def test_route_b_requires_a_halving_step_pair():
    with pytest.raises(ValueError):
        route_b(
            family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
            m_grid=(1,), batches=1, paths=100, seed=1,
            fd_steps=(0.05, 0.03), max_steps=1000,
        )


def test_route_b_reports_richardson_and_both_raw_steps():
    result = route_b(
        family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
        m_grid=(1,), batches=6, paths=4000, seed=2,
        fd_steps=(0.05, 0.025), max_steps=5000,
    )
    per_step = result["by_m"]["1"]["per_step"]
    assert set(per_step) == {"0.05", "0.025"}
    coarse = per_step["0.05"]["gamma"]["mean"]
    fine = per_step["0.025"]["gamma"]["mean"]
    combined = result["by_m"]["1"]["gamma"]["mean"]
    # the reported value is the Richardson combination of the batch means
    assert combined == pytest.approx((4.0 * fine - coarse) / 3.0, rel=1e-9)
    assert result["primary_estimator"] == "richardson"


def test_route_a_reproduces_the_pathwise_decomposition_in_expectation():
    result = route_a(
        family=REGISTRY["laplace"], detector=Detector("cusum", 2.0),
        m_grid=(1, 5), batches=6, paths=8000, seed=4, max_steps=5000,
    )
    for m in (1, 5):
        block = result["by_m"][str(m)]
        assert block["gamma"]["mean"] == pytest.approx(
            block["fixed_gain"]["mean"] + block["short_correction"]["mean"],
            rel=1e-9, abs=1e-12,
        )
    assert result["by_m"]["1"]["short_correction"]["mean"] == 0.0
    assert result["unstopped_paths"] == 0


def test_gaussian_form_gain_equals_the_score_gain_only_for_the_gaussian():
    for name, same in (("gaussian", True), ("laplace", False), ("t3", False)):
        result = route_a(
            family=REGISTRY[name], detector=Detector("cusum", 2.0),
            m_grid=(1,), batches=4, paths=6000, seed=12, max_steps=5000,
        )
        block = result["by_m"]["1"]
        equal = block["gamma"]["mean"] == pytest.approx(
            block["gaussian_gain"]["mean"], rel=1e-12
        )
        assert equal is same, name


def test_correspondence_reports_both_relative_and_z():
    row = correspondence({"mean": 10.0, "se": 0.1}, {"mean": 10.3, "se": 0.2})
    assert row["relative_discrepancy"] == pytest.approx(0.3 / 10.3)
    assert row["z"] == pytest.approx(0.3 / math.hypot(0.1, 0.2))


def test_two_routes_agree_on_a_cheap_cell():
    """A small end-to-end agreement check that does not depend on the frozen
    campaign artifacts existing."""
    detector = Detector("cusum", 2.0)
    a = route_a(family=REGISTRY["logistic"], detector=detector, m_grid=(1,),
                batches=8, paths=40000, seed=21, max_steps=5000)
    b = route_b(family=REGISTRY["logistic"], detector=detector, m_grid=(1,),
                batches=8, paths=40000, seed=22, fd_steps=(0.05, 0.025),
                max_steps=5000)
    row = correspondence(a["by_m"]["1"]["gamma"], b["by_m"]["1"]["gamma"])
    assert row["relative_discrepancy"] < 0.03


def test_non_selective_stopping_collapses_the_map_to_zero():
    """Corollary G2(a): with a deterministic stopping rule the conditional-mean
    reuse map is identically zero, so E_e[A_m] = -e exactly."""
    from rebaseguard_p4_general.simulate import simulate_group
    for name in ("gaussian", "laplace", "t3", "skewnormal4"):
        for e in (0.0, 0.25, -0.4):
            (run,) = simulate_group(
                family=REGISTRY[name], detector=Detector("deterministic", 3),
                e_values=(e,), n_paths=200000, seed=77, batch=0, m_max=3,
                mode="compact", max_steps=6,
            )
            assert (run.tau == 3).all()
            for m in (1, 2, 3):
                assert float(run.window_mean(m).mean()) == pytest.approx(
                    -e, abs=0.02
                ), (name, e, m)
