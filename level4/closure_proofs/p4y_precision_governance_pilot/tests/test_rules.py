"""Allocation-rule semantics -- the P4X G1 repair.

The point of these tests is that the two acceptable terminal states are
EXHAUSTIVE for the staged rules, and that ``PRECISION_LIMITED`` means one
specific mechanical thing and nothing else.
"""

import math

import pytest

from p4y_pilot.rules import (
    ATTAINED,
    CANDIDATES,
    PRECISION_LIMITED,
    UNRESOLVED,
    Rule,
    can_end_unresolved,
    initial_blocks,
    run,
)
from p4y_pilot.stats import chi2_upper_quantile_ratio

R_STAR = 0.01
KAPPA_HEAVY = 1.0 - 1.0 / 1.47
STAGED = [r for r in CANDIDATES if not can_end_unresolved(r)]
BOUNDED = [r for r in CANDIDATES if can_end_unresolved(r)]


def converging(c: float, kappa: float):
    """relSE = c * B**-kappa -- the idealised behaviour the rule assumes."""
    return lambda b: c * b ** -kappa


def stuck(value: float):
    """A route whose precision never improves.  Only the cap can stop it."""
    return lambda b: value


@pytest.mark.parametrize("rule", STAGED, ids=lambda r: r.name)
def test_staged_rules_cannot_reach_the_third_state(rule):
    for behaviour in (converging(0.4, KAPPA_HEAVY), stuck(0.5), stuck(1e6)):
        o = run(rule, measure=behaviour, reference_blocks=12,
                reference_relative_se=0.05, r_star=R_STAR,
                kappa=KAPPA_HEAVY, cap_blocks=144, min_blocks=8)
        assert o.status in (ATTAINED, PRECISION_LIMITED)
        assert o.status != UNRESOLVED


@pytest.mark.parametrize("rule", BOUNDED, ids=lambda r: r.name)
def test_the_p4x_shaped_rules_can_reach_the_third_state(rule):
    """Pin the defect: a bounded-stage rule admits 'neither r* nor capped'."""
    o = run(rule, measure=stuck(0.02), reference_blocks=12,
            reference_relative_se=0.05, r_star=R_STAR, kappa=KAPPA_HEAVY,
            cap_blocks=10**9, min_blocks=8)
    assert o.status == UNRESOLVED
    assert o.relative_se > R_STAR
    assert o.next_stage_blocks is not None
    assert o.next_stage_blocks <= 10**9, "the cap was never reached"


def test_precision_limited_is_exactly_next_stage_crosses_the_cap():
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    o = run(rule, measure=stuck(0.05), reference_blocks=12,
            reference_relative_se=0.05, r_star=R_STAR, kappa=KAPPA_HEAVY,
            cap_blocks=100, min_blocks=8)
    assert o.status == PRECISION_LIMITED
    assert o.next_stage_blocks > 100          # the refused allocation
    assert o.blocks <= 100                    # nothing beyond the cap ran


def test_precision_limited_is_not_produced_by_repeated_attempts_alone():
    """A route may take many stages and still not be precision-limited."""
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    o = run(rule, measure=converging(0.9, 0.5), reference_blocks=12,
            reference_relative_se=0.3, r_star=R_STAR, kappa=0.5,
            cap_blocks=10**9, min_blocks=8)
    assert o.status == ATTAINED
    assert o.stages >= 1


def test_a_route_never_executes_beyond_the_cap():
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    for cap in (30, 50, 144, 1000):
        o = run(rule, measure=stuck(0.5), reference_blocks=12,
                reference_relative_se=0.5, r_star=R_STAR, kappa=KAPPA_HEAVY,
                cap_blocks=cap, min_blocks=8)
        assert o.blocks <= cap, (cap, o)


def test_continuation_depends_only_on_route_local_precision():
    """The rule has no channel for discrepancy, z, sign or pass/fail."""
    import inspect

    params = set(inspect.signature(run).parameters)
    for forbidden in ("discrepancy", "z", "sign", "gate", "passed",
                      "route_other", "family_result", "history"):
        assert forbidden not in params
    assert params == {"rule", "measure", "reference_blocks",
                      "reference_relative_se", "r_star", "kappa",
                      "cap_blocks", "min_blocks"}


def test_two_routes_with_identical_precision_get_identical_allocations():
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    kw = dict(measure=converging(0.4, 0.5), reference_blocks=12,
              reference_relative_se=0.05, r_star=R_STAR, kappa=0.5,
              cap_blocks=10**9, min_blocks=8)
    assert run(rule, **kw) == run(rule, **kw)


def test_sizing_follows_the_inherited_scaling_law():
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    b = initial_blocks(rule, 12, 0.05, R_STAR, 0.5, min_blocks=1)
    assert b == math.ceil(12 * (0.05 / R_STAR) ** 2)


def test_safety_factor_enters_as_a_target_divisor():
    plain = initial_blocks(Rule("p", math.inf, safety=1.0), 12, 0.05,
                           R_STAR, 0.5, 1)
    safe = initial_blocks(Rule("s", math.inf, safety=1.3), 12, 0.05,
                          R_STAR, 0.5, 1)
    assert safe == math.ceil(plain * 1.3 ** 2) or safe > plain
    assert safe > plain


def test_adaptive_inflation_vanishes_at_production_block_counts():
    """RULE D must not tax a large allocation."""
    small = math.sqrt(chi2_upper_quantile_ratio(24, 0.95))
    large = math.sqrt(chi2_upper_quantile_ratio(8801, 0.95))
    assert small > 1.2
    assert large < 1.02
    # the cost surcharge at the heavy-tail exponent
    assert large ** (1.0 / KAPPA_HEAVY) < 1.05


def test_min_blocks_floor_is_respected():
    """An already-precise reference never shrinks the allocation below the
    reference size, and never below the frozen floor."""
    rule = Rule("probe", max_stages=math.inf, safety=1.0)
    assert initial_blocks(rule, 12, 1e-9, R_STAR, 0.5, min_blocks=8) == 12
    assert initial_blocks(rule, 4, 1e-9, R_STAR, 0.5, min_blocks=8) == 8
    assert initial_blocks(rule, 4, 1e-9, R_STAR, 0.5, min_blocks=1) == 4


def test_every_candidate_is_uniquely_named():
    names = [r.name for r in CANDIDATES]
    assert len(names) == len(set(names))
    assert len(CANDIDATES) == 9


def test_first_crossing_matches_the_reference_definition():
    """The cost-tail phase's fast curve must equal worst_relative_se(B)."""
    import importlib.util
    import sys
    from pathlib import Path

    from p4y_pilot.blocks import BlockPool, Cell, register_cells, worst_relative_se

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("ct", root / "run_costtail.py")
    ct = importlib.util.module_from_spec(spec)
    sys.modules["ct"] = ct
    spec.loader.exec_module(ct)

    register_cells({"crossing-probe": 930})
    cell = Cell(key="crossing-probe", layer="reduced", kind="cusum",
                threshold=2.0, family="t1p5", route="route_a",
                max_steps=60_000, block_size=3_000, heavy=True)
    pool = BlockPool(cell, "identity", 0)
    pool.take(40)
    for r_star in (0.02, 0.05, 0.1, 0.5, 1e-9):
        fast = ct.first_crossing(pool, r_star)
        slow = next((b for b in range(8, 41)
                     if worst_relative_se(pool.take(b))[0] <= r_star), None)
        assert fast == slow, (r_star, fast, slow)
