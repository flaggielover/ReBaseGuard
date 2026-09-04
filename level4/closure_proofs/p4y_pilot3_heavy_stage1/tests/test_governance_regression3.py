"""Brief sections 19, 21, 22: regression only, nothing redesigned.

The shard partition, the logical RNG addressing architecture, the staged
termination semantics and the leakage guard are INHERITED.  These tests
re-run them in the Pilot-3 namespace so a checkpoint drafted from Pilot-3
carries its own evidence, and so any regression STOPs the pilot.
"""

import inspect
import math

import pytest

from p4y_pilot.blocks import Cell, block_value, summarise
from p4y_pilot.shard import (
    Allocation, ShardInvariantError, block_ids, p4x_defective_partition,
    partition, verify,
)
from p4y_pilot2 import rule as R2
from p4y_pilot2.audit import audit
from p4y_pilot3 import addressing3 as A3
from p4y_pilot3.strata3 import (
    CELL_STRATA, CELLS, HEAVY_FAMILY, N_HEAVY_STRATA, N_ORDINARY_STRATA,
    N_STRATA_TOTAL, STRATA, reachable_addresses,
)

K_VALUES = [1, 2, 5, 7, 13, 64]
P4X_B, P4X_K, P4X_BLOCK = 8_801, 5, 250_000


# ------------------------------------------------------ exact shard sum
@pytest.mark.parametrize("k", K_VALUES)
@pytest.mark.parametrize("b", [0, 1, 59, 151, 215, 1784, 8_801, 100_000])
def test_exact_shard_sum(b, k):
    sizes = partition(b, k)
    assert sum(sizes) == b
    assert max(sizes) - min(sizes) <= 1
    a = Allocation(total_blocks=b, block_size=250_000, workers=k).audit()
    assert a["delta_blocks"] == 0 and a["delta_paths"] == 0


def test_historical_8801_regression():
    sizes = partition(P4X_B, P4X_K)
    assert sum(sizes) == 8_801 != 8_805
    assert sorted(sizes) == [1760, 1760, 1760, 1760, 1761]
    a = Allocation(total_blocks=P4X_B, block_size=P4X_BLOCK,
                   workers=P4X_K).audit()
    assert a["executed_blocks"] == 8_801
    assert a["executed_paths"] == 2_200_250_000
    bad = p4x_defective_partition(P4X_B, P4X_K)
    assert sum(bad) == 8_805 and sum(bad) * P4X_BLOCK == 2_201_250_000
    with pytest.raises(ShardInvariantError):
        verify(bad, P4X_B)


def test_no_per_shard_rounding():
    for b, k in ((8_801, 5), (1784, 5), (215, 7), (59, 13)):
        assert sum(partition(b, k)) == b
        if b % k:
            assert sum([math.ceil(b / k)] * k) > b


# --------------------------------------------------------- RNG addressing
def test_frozen_domain_is_collision_free():
    d = reachable_addresses()
    r = A3.audit_reachable_domain(d)
    assert r["addresses"] == r["unique_seeds"] == len(d)
    assert r["collision_free"] and r["addresses"] > 500


def test_addressing_is_keyed_by_logical_identity_only():
    params = list(inspect.signature(A3.seed).parameters)
    assert params == ["cell", "stratum", "namespace", "replicate"]
    for banned in ("worker", "pid", "process", "shard", "schedule", "order"):
        assert banned not in params
    assert "%" not in inspect.getsource(A3.seed)
    assert A3.bounds_are_injective_by_construction()


def test_pilot3_seeds_cannot_collide_with_any_earlier_campaign():
    lo = min(a.seed for a in reachable_addresses())
    assert lo == A3.CAMPAIGN_BASE == 9_310_000_000
    assert lo >= A3.PILOT2_CEILING + 1_000_000_000


# ------------------------------------------- shard-invariant block identity
IDENT = Cell(key="ident3", layer="reduced", kind="cusum", threshold=2.0,
             family="t1p5", route="route_a", max_steps=60_000,
             block_size=2_000, heavy=True)
B = 12


def _run(k, stream):
    return {bid: block_value(IDENT, stream, bid)
            for shard in range(k) for bid in block_ids(B, k, shard)}


def test_block_identity_is_invariant_under_k():
    stream = A3.seed("H", "S59", "validation", 0)
    ref = _run(1, stream)
    for k in K_VALUES:
        got = _run(k, stream)
        assert got.keys() == ref.keys()
        for bid, v in got.items():
            assert v == ref[bid]


@pytest.mark.parametrize("k", K_VALUES)
def test_pooled_equals_unsharded(k):
    stream = A3.seed("H", "S59", "validation", 1)
    un = [block_value(IDENT, stream, i)[1] for i in range(B)]
    sh = [_run(k, stream)[i][1] for i in range(B)]
    assert sh == un
    a, b = summarise(un), summarise(sh)
    assert (a["mean"], a["se"]) == (b["mean"], b["se"])


# ------------------------------------------------------- leakage guard
def test_allocation_reads_precision_only():
    assert set(inspect.signature(R2.trace).parameters) == {
        "measure", "b1", "target", "kappa", "max_cap"}
    assert R2.Precision.__slots__ == R2.PRECISION_FIELDS == ("blocks",
                                                             "relative_se")
    from p4y_pilot3 import sizing
    assert set(inspect.signature(sizing.size_stage1).parameters) == {
        "b_ref", "relse_point", "relse_upper", "target", "kappa",
        "min_blocks", "abs_ceiling"}


@pytest.mark.parametrize("field", R2.FORBIDDEN_FIELDS)
def test_forbidden_fields_are_rejected(field):
    traj = R2.trace(measure=lambda b: 0.005, b1=48, target=0.01, kappa=0.5,
                    max_cap=1000)
    o = R2.terminate(traj, 576)
    assert audit(o, traj, cap_blocks=576).valid
    assert not audit(o, traj, cap_blocks=576,
                     measure_inputs_seen=(field,)).valid


def test_the_runner_never_hands_a_scientific_field_to_the_allocation():
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "run_phase3.py").read_text()
    body = src[src.index("def replicate("):src.index("def run_phase(")]
    for banned in ("discrepancy", "gate", "verdict", "pass_fail",
                   "correspondence", "route_q", "z_score"):
        assert banned not in body


# ------------------------------------------- frozen production mixture
def test_the_production_mixture_is_the_verified_one():
    assert (N_STRATA_TOTAL, N_HEAVY_STRATA, N_ORDINARY_STRATA) == (48, 8, 40)
    assert sum(s.weight for s in STRATA) == 48
    assert sum(s.weight for s in STRATA if s.heavy) == 8
    assert sum(s.weight for s in STRATA if not s.heavy) == 40
    assert HEAVY_FAMILY == "t1p5"


def test_the_heavy_class_comes_from_frozen_family_metadata():
    """Not from an observed Pilot-3 failure -- brief section 19."""
    import json
    from pathlib import Path

    cp = json.loads(Path(
        "/Users/suzhe/ReBaseGuard-p4x/level4/closure_proofs/"
        "p4x_generalization_boundary/checkpoint_a/results/checkpoint_a.json"
    ).read_text())
    pol = cp["heavy_tail_policy"]
    assert pol["only_family_requiring_alpha_below_2"] == HEAVY_FAMILY
    assert pol["measured_alpha_min_other_families"] > 2.0
    seen = {}
    for p in cp["production_plan"]:
        for r in ("route_a", "route_b"):
            seen.setdefault((p["config"], r), (p["heavy_tailed"], p["family"]))
    heavy = [k for k, v in seen.items() if v[0]]
    assert len(seen) == 48 and len(heavy) == 8
    assert {seen[k][1] for k in heavy} == {HEAVY_FAMILY}


def test_the_heavy_rule_does_not_touch_ordinary_strata():
    from p4y_pilot3.strata3 import reference_blocks, stratum

    ordinary = stratum("ORD")
    for bmin in (4, 16, 32, 64, 128):
        assert reference_blocks(ordinary, bmin) == ordinary.b_ref == 160
    heavy = stratum("S215")
    for bmin in (16, 32, 64, 128):
        assert reference_blocks(heavy, bmin) == bmin
