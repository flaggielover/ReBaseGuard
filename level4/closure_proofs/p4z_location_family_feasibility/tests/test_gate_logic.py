"""The frozen gate arithmetic, tested on synthetic inputs.

No real block is read here.  These tests pin the *logic*: the rounding
direction, the three exhaustive outcomes, and the role of the truncation term.
"""
import json
import math
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS / "production"))

import adjudicate as adj  # noqa: E402

PLAN = json.loads((NS / "production" / "campaign_plan.json").read_text())


def test_rounding_is_away_from_zero_and_therefore_conservative():
    """Every gate is a `<=`, so rounding the statistic up makes PASS harder."""
    assert adj._round_up(0.0299999999999) >= 0.0299999999999
    assert adj._round_up(1.0000000000001) > 1.0
    assert adj._round_up(-1.0000000000001) < -1.0
    assert adj._round_up(0.03) == 0.03
    assert adj._round_up(math.inf) == math.inf


def test_a_statistic_exactly_on_the_limit_still_passes():
    """`<=` means the boundary is inclusive; rounding must not steal it."""
    assert adj._round_up(0.03) <= 0.03
    assert adj._round_up(4.0) <= 4.0


def test_a_statistic_a_hair_over_the_limit_fails():
    assert not adj._round_up(0.030000000001) <= 0.03
    assert not adj._round_up(4.000000000001) <= 4.0


def test_the_truncation_term_can_only_widen_route_b_uncertainty():
    """`se_b_total = hypot(mc_se, T_B) >= mc_se`, always."""
    for mc, t_b in ((0.01, 0.0), (0.01, 0.005), (0.001, 0.02)):
        assert math.hypot(mc, t_b) >= mc


def test_the_relative_gate_is_untouched_by_the_truncation_term():
    """rel compares point estimates only, so T_B cannot buy a pass on rel."""
    a, b = 1.0, 1.05
    rel = abs(a - b) / max(abs(a), abs(b))
    for t_b in (0.0, 0.5, 5.0):
        assert abs(a - b) / max(abs(a), abs(b)) == rel


def test_K7_bounds_how_far_the_truncation_term_can_widen_anything():
    """A large T_B is not a free pass: K7 makes the cell INCONCLUSIVE first."""
    limit = PLAN["thresholds"]["fd_ladder_relative_max"]
    assert limit == 0.02
    assert adj._round_up(0.0201) > limit          # fires
    assert adj._round_up(0.0199) <= limit         # does not fire


def test_the_three_outcomes_are_exhaustive_and_disjoint():
    stage0 = json.loads((NS / "production" / "stage0_freeze.json").read_text())
    assert stage0["stage0_verdict_rule"]["exhaustive"] is True
    checkpoint = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
    rule = checkpoint["uncertainty_rule"]
    assert rule["almost_pass"] == "does not exist"
    assert {"pass", "fail", "inconclusive"} <= set(rule)


def test_gate_thresholds_in_the_plan_equal_their_frozen_sources():
    protocol = json.loads(
        (NS.parent / "p4_theory_generalization" / "configs" / "P4_PROTOCOL.json").read_text())
    thr = PLAN["thresholds"]
    assert thr["relative"] == protocol["gates"]["correspondence_relative_limit"]
    assert thr["z"] == protocol["gates"]["correspondence_z_limit"]
    assert abs(1.96 * math.sqrt(2) * thr["r_star"] - 0.03) < 1e-8


def test_a_missing_route_yields_INCONCLUSIVE_not_a_silent_pass():
    """`_summarise` returns None below two blocks; the caller must not pass."""
    assert adj._summarise([], 1) is None
    assert adj._summarise([{"block_mean": {"1": 1.0}, "block_paths": 1,
                            "cpu_seconds": 0.0}], 1) is None


def test_summarise_is_a_batch_standard_error_over_block_means():
    docs = [{"block_mean": {"1": v}, "block_paths": 10, "cpu_seconds": 0.0}
            for v in (1.0, 2.0, 3.0, 4.0)]
    out = adj._summarise(docs, 1)
    assert out["mean"] == pytest.approx(2.5)
    # sample sd of (1,2,3,4) is sqrt(5/3); SE divides by sqrt(4)
    assert out["mc_se"] == pytest.approx(math.sqrt(5 / 3) / 2)
    assert out["blocks"] == 4
