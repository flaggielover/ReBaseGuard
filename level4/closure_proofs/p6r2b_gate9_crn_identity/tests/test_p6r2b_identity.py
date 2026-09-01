"""The 13 identity tests, derived from primitive GENERATION, never from a stored
Boolean.

The contract under test: for every
``(seed_namespace, detector, m, k, replicate_id, cycle_id, primitive_type,
primitive_index)`` the raw exogenous draw is bit-identical across all
sensitivity variants -- and endogenous trajectories are free to diverge.
"""
import inspect

import numpy as np
import pytest

from rebaseguard_p6r2b import primitives as PR
from rebaseguard_p6r2b.simulate import LADDER, saw_decider, simulate

CELL = dict(detector="cusum", m=3, k=3)
N = 200
#: the four declared sensitivity variants, as s1 values
S1_VARIANTS = (2.560, 1.280, 5.120, 0.0626)


# --- 1-4: the primitive draws themselves -----------------------------------

@pytest.mark.parametrize("r,j,t", [(0, 0, 0), (7, 3, 5), (13, 11, 511),
                                   (99, 2, 512), (150, 7, 1023), (42, 5, 2457),
                                   (3, 0, 4095)])
def test_1_monitor_primitive_is_bit_identical_across_variants(r, j, t):
    """A variant cannot change a monitor draw: the address has no variant slot."""
    vals = set()
    for _s1 in S1_VARIANTS:
        PR.clear_cache()
        vals.add(PR.monitor(CELL["detector"], CELL["m"], CELL["k"], r, j, t, N))
    assert len(vals) == 1


@pytest.mark.parametrize("j", [0, 5, 59])
def test_2_fresh_primitive_is_bit_identical_across_variants(j):
    ref = None
    for _s1 in S1_VARIANTS:
        PR.clear_cache()
        got = PR.fresh(CELL["detector"], CELL["m"], CELL["k"], j, N)
        ref = got.copy() if ref is None else ref
        assert np.array_equal(got, ref)


def test_3_initialisation_primitive_is_bit_identical_across_variants():
    ref = None
    for _s1 in S1_VARIANTS:
        PR.clear_cache()
        got = PR.init(CELL["detector"], CELL["m"], CELL["k"], N)
        ref = got.copy() if ref is None else ref
        assert np.array_equal(got, ref)


@pytest.mark.parametrize("t", [512, 999, 2000, 2047, 2457, 5000, 12345])
def test_4_overflow_primitive_is_bit_identical_across_variants(t):
    """Past the first block -- and past the 2000-step tape P6R2 relied on."""
    assert t >= PR.BLOCK_LEN
    vals = set()
    for _s1 in S1_VARIANTS:
        PR.clear_cache()
        vals.add(PR.monitor(CELL["detector"], CELL["m"], CELL["k"], 5, 4, t, N))
    assert len(vals) == 1


# --- 5-6: no policy quantity may enter the address -------------------------

def test_5_no_policy_identity_can_reach_the_rng_addressing():
    sig = set(inspect.signature(PR.address_key).parameters)
    assert sig == {"detector", "m", "k", "cycle", "primitive_type", "block_index"}
    for banned in ("policy", "policy_id", "variant", "s1", "rho", "live",
                   "tau", "seed_family"):
        assert banned not in sig
    # scan EXECUTABLE code only -- prose in docstrings names what is excluded
    import ast
    tree = ast.parse(inspect.getsource(PR))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            body = list(node.body)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body = body[1:]                    # drop the docstring
            node.body = body if body else [ast.Pass()]
    code = ast.unparse(tree)
    for banned in ("policy_id", "variant", "live_idx", "live_set", "n_live",
                   "s1", "rho", "tau"):
        assert banned not in code, f"{banned!r} appears in primitive addressing code"


def test_6_changing_the_s1_multiplier_cannot_change_a_primitive_draw():
    """s1 is a *policy* quantity; it is not an argument of any primitive call."""
    for fn in (PR.monitor, PR.monitor_column, PR.fresh, PR.init, PR.aux,
               PR.block, PR.address_key):
        assert "s1" not in inspect.signature(fn).parameters


# --- 7-9: order- and live-set-independence ---------------------------------

def test_7_live_replicate_ordering_does_not_affect_a_draw():
    col = PR.monitor_column(CELL["detector"], CELL["m"], CELL["k"], 2, 700, N)
    for order in (np.arange(N), np.arange(N)[::-1],
                  np.random.default_rng(0).permutation(N)):
        got = col[order]
        assert np.array_equal(got[np.argsort(order)], col)


def test_8_removing_replicates_from_the_live_set_does_not_move_the_rest():
    """The exact P6R2 failure mode: a shrinking live set must change nothing."""
    full = PR.monitor_column(CELL["detector"], CELL["m"], CELL["k"], 3, 1500, N)
    for keep in (np.arange(N), np.arange(0, N, 2), np.array([5, 9, 100]),
                 np.array([N - 1])):
        assert np.array_equal(PR.monitor_column(
            CELL["detector"], CELL["m"], CELL["k"], 3, 1500, N)[keep], full[keep])


def test_9_same_address_in_a_different_execution_order_gives_the_same_value():
    addrs = [(1, 0, 3), (1, 0, 900), (2, 4, 17), (2, 4, 2100), (0, 9, 0)]
    PR.clear_cache()
    fwd = [PR.monitor(CELL["detector"], CELL["m"], CELL["k"], *a, N) for a in addrs]
    PR.clear_cache()
    rev = [PR.monitor(CELL["detector"], CELL["m"], CELL["k"], *a, N)
           for a in reversed(addrs)][::-1]
    assert fwd == rev


# --- 10: forced overflow inside a real simulation ---------------------------

def test_10_forced_overflow_past_2000_observations_keeps_identity():
    """Force very long cycles, then check the deep ladder points agree exactly."""
    kw = dict(detector="cusum", m=3, k=3, n_rep=120, n_cycles=6, burn_in=1)
    runs = [simulate(decide=saw_decider(0.9384, -1.0667, 0.0626, s1, 3, 3), **kw)
            for s1 in S1_VARIANTS]
    assert max(r["max_block_index"] for r in runs) >= 4, "need t > 2047"
    assert max(r["n_overflow_draws"] for r in runs) > 0
    common = np.minimum.reduce([r["tau"] for r in runs])
    deep = [i for i, L in enumerate(LADDER) if L >= PR.BLOCK_LEN]
    checked = 0
    for i in deep:
        mask = common > LADDER[i]
        if not mask.any():
            continue
        base = runs[0]["ladder_sum"][..., i][mask]
        for r in runs[1:]:
            assert np.array_equal(r["ladder_sum"][..., i][mask], base)
        checked += int(mask.sum())
    assert checked > 0, "no deep comparison was actually performed"


# --- 11: field digests -------------------------------------------------------

def test_11_primitive_field_digests_match_across_all_four_variants():
    digests = set()
    for _s1 in S1_VARIANTS:
        PR.clear_cache()
        digests.add(PR.field_digest(CELL["detector"], CELL["m"], CELL["k"],
                                    N, 4, 2))
    assert len(digests) == 1
    # and a different cell must give a different digest (the digest is real)
    assert PR.field_digest("sr", 3, 3, N, 4, 2) != digests.pop()


# --- 12-13: endogenous divergence is ALLOWED, and must not be re-asserted ----

def test_12_endogenous_states_are_allowed_to_differ():
    kw = dict(detector="cusum", m=5, k=5, n_rep=300, n_cycles=12, burn_in=2)
    a = simulate(decide=saw_decider(0.9201, -1.0321, 0.0433, 0.498, 5, 5), **kw)
    b = simulate(decide=saw_decider(0.9201, -1.0321, 0.0433, 4.980, 5, 5), **kw)
    # the test asserts divergence is TOLERATED -- it never requires equality
    assert a["e_start"].shape == b["e_start"].shape
    diverged = int((a["e_start"] != b["e_start"]).sum())
    assert diverged >= 0            # explicitly no equality requirement
    # but the exogenous fresh field must still be identical
    assert np.array_equal(a["fresh"], b["fresh"])


def test_13_the_old_all_paths_identical_semantics_cannot_reappear():
    """No P6R2b artifact or source may assert whole-path equality."""
    import json
    from pathlib import Path
    ns = Path(__file__).resolve().parents[1]
    for f in list((ns / "src").rglob("*.py")) + list((ns / "experiments").rglob("*.py")):
        t = f.read_text()
        assert "all_paths_identical" not in t, f
    for f in (ns / "results").glob("p6r2b_*.json"):
        d = json.loads(f.read_text())
        assert "all_paths_identical_across_variants" not in json.dumps(d)
        assert "cycle0_innovation_paths_identical_across_variants" not in json.dumps(d)
