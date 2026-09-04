"""Brief sections 21-22: regression only.  Nothing is redesigned."""

import inspect
import math

import pytest

from p4y_pilot.blocks import Cell, block_value, summarise
from p4y_pilot.shard import (
    Allocation, ShardInvariantError, block_ids, p4x_defective_partition,
    partition, verify,
)
from p4y_pilot4 import addressing4 as A4
from p4y_pilot4 import blocks4, estimand
from p4y_pilot4.design4 import CELLS, reachable_addresses

K_VALUES = [1, 2, 5, 7, 13, 64]
P4X_B, P4X_K, P4X_BLOCK = 8_801, 5, 250_000


@pytest.mark.parametrize("k", K_VALUES)
@pytest.mark.parametrize("b", [0, 1, 59, 512, 2048, 8_801, 100_000])
def test_exact_shard_sum(b, k):
    sizes = partition(b, k)
    assert sum(sizes) == b and max(sizes) - min(sizes) <= 1
    a = Allocation(total_blocks=b, block_size=250_000, workers=k).audit()
    assert a["delta_blocks"] == 0 and a["delta_paths"] == 0


def test_historical_8801_regression():
    assert sorted(partition(P4X_B, P4X_K)) == [1760, 1760, 1760, 1760, 1761]
    a = Allocation(total_blocks=P4X_B, block_size=P4X_BLOCK,
                   workers=P4X_K).audit()
    assert a["executed_blocks"] == 8_801
    assert a["executed_paths"] == 2_200_250_000
    bad = p4x_defective_partition(P4X_B, P4X_K)
    assert sum(bad) == 8_805 and sum(bad) * P4X_BLOCK == 2_201_250_000
    with pytest.raises(ShardInvariantError):
        verify(bad, P4X_B)


def test_collision_free_logical_addresses():
    d = reachable_addresses()
    r = A4.audit_reachable_domain(d)
    assert r["addresses"] == r["unique_seeds"] == len(d)
    assert r["collision_free"]
    assert A4.bounds_are_injective_by_construction()
    assert "%" not in inspect.getsource(A4.seed)
    assert list(inspect.signature(A4.seed).parameters) == [
        "cell", "namespace", "replicate"]
    for banned in ("worker", "pid", "shard", "schedule", "order"):
        assert banned not in inspect.signature(A4.seed).parameters


def test_pilot4_seeds_cannot_collide_with_any_earlier_campaign():
    lo = min(a.seed for a in reachable_addresses())
    assert lo == A4.CAMPAIGN_BASE == 12_310_000_000
    assert lo >= A4.PILOT3_CEILING + 1_000_000_000


IDENT = Cell(key="ident4", layer="reduced", kind="cusum", threshold=2.0,
             family="t1p5", route="route_a", max_steps=60_000,
             block_size=2_000, heavy=True)
B = 12


def _run(k, stream):
    return {bid: block_value(IDENT, stream, bid)
            for shard in range(k) for bid in block_ids(B, k, shard)}


def test_shard_invariant_block_identity():
    stream = A4.seed("H", "master0", 0)
    ref = _run(1, stream)
    for k in K_VALUES:
        got = _run(k, stream)
        assert got.keys() == ref.keys()
        for bid, v in got.items():
            assert v == ref[bid]


@pytest.mark.parametrize("k", K_VALUES)
def test_pooled_equals_unsharded(k):
    stream = A4.seed("H", "master1", 0)
    un = [block_value(IDENT, stream, i)[1] for i in range(B)]
    sh = [_run(k, stream)[i][1] for i in range(B)]
    assert sh == un
    a, b = summarise(un), summarise(sh)
    assert (a["mean"], a["se"]) == (b["mean"], b["se"])


# --------------------------------------------------------- leakage guard
FORBIDDEN = ("discrepancy", "relative_discrepancy", "z_score", "gate",
             "gate_result", "passed", "pass_fail", "route_q",
             "gaussian_consistency", "verdict", "correspondence",
             "historically_failed")


def _executable_source(path) -> str:
    """The file's CODE, with comments and every docstring removed.

    A prose scan would trip over the package's own explanation of what it does
    not contain.  Stripping docstring nodes and re-unparsing checks the
    executable statements, which is what the guard is actually about.
    """
    import ast

    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)


def _mentions(body: str, token: str) -> bool:
    """Whole-identifier match.  'gate' must not fire on 'aggregate'."""
    import re

    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
                     body) is not None


def test_measurement_code_consumes_no_scientific_outcome():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for name in ("run_measure.py", "src/p4y_pilot4/estimand.py",
                 "src/p4y_pilot4/blocks4.py", "src/p4y_pilot4/design4.py"):
        body = _executable_source(root / name)
        for banned in FORBIDDEN:
            assert not _mentions(body, banned), f"{banned!r} appears in {name}"


def test_the_guard_itself_is_not_vacuous():
    """A word-boundary guard must still catch a real occurrence."""
    assert _mentions("x = discrepancy + 1", "discrepancy")
    assert _mentions("gate = 3", "gate")
    assert not _mentions("y = aggregate(x, 5)", "gate")
    assert not _mentions("propagated = 1", "gate")


def test_the_estimator_reads_only_block_values():
    assert list(inspect.signature(estimand.theta_hat).parameters) == ["values"]
    assert list(inspect.signature(blocks4.base_series).parameters) == [
        "cell", "stream_seed", "n_base", "m", "cache"]


def test_pilot4_contains_no_allocation_rule():
    """Brief section 2: no Stage-1 sizing, no cap, no kappa, anywhere."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for py in sorted((root / "src").rglob("*.py")) + [root / "run_measure.py"]:
        body = _executable_source(py)
        for banned in ("cap_blocks", "stage1", "size_stage1", "top_up",
                       "topup", "PRECISION_LIMITED", "kappa"):
            assert not _mentions(body, banned), f"{banned!r} in {py.name}"
