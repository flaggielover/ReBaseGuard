"""The enclosure must actually contain the true value.

These are the tests that matter: a bracket that is fast, tight and wrong is
worse than no bracket.  Each one checks containment against a reference the
Stage B pipeline does not share code with.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from backends import ArbBackend, FloatBackend
from bellman_solver import Grid, build as bs_build
from domain import ATOM, build_partition, destination_cells
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from transitions import SEG_CONT, SEG_MIXED, build_transitions

E_STAR = 1.0367242887184211


def reference_G(e: float, n_solver: int = 200) -> float:
    """Independent value from the Stage A Claude Science Bellman solver."""
    g = Grid(n_solver)
    K, rG, _, _, _ = bs_build(g, e)
    n = g.n
    G = spla.splu((sp.eye(n, format="csc") - K).tocsc()).solve(rG)
    return float(G[g.idx[(0, 0)]])


def run_bracket(e, *, n_axis=80, n_tri=16, backend=None, max_iter=250):
    backend = backend or FloatBackend()
    part = build_partition(n_axis=n_axis, axis_power=2.0, n_tri=n_tri)
    struct = build_transitions(part, backend, e, e)
    kill = best_killing_bound(e, e)
    m = a_priori_bound(abs(e), kill["arl_upper_bound"])
    it = Iterator(struct)
    return it.run(m, max_iter=max_iter), struct, part


# ------------------------------------------------------------- containment --

def test_bracket_contains_the_independent_solver_value():
    br, _, _ = run_bracket(E_STAR)
    ref = reference_G(E_STAR)
    assert br.atom_lower <= ref <= br.atom_upper
    assert br.atom_width < 0.25


@pytest.mark.parametrize("e", [0.0, 0.5, 1.0367242887184211, 2.0])
def test_bracket_contains_the_solver_value_across_e(e):
    br, _, _ = run_bracket(e, n_axis=60, n_tri=14)
    ref = reference_G(e, 150)
    assert br.atom_lower <= ref <= br.atom_upper, (e, br.atom_lower, ref,
                                                   br.atom_upper)


def test_bracket_contains_a_monte_carlo_estimate():
    """Fully independent route: Stage A's Gate 4.2 conditional simulator.

    Stage A estimates F_1(e) = E[e + Z_tau]; Stage B encloses G(e) = E[Z_tau].
    """
    from rebaseguard_level4.conditional import simulate_cycle_batch
    from rebaseguard_level4.streams import ScalarStream

    e = E_STAR
    batch = simulate_cycle_batch(
        e=e, n_paths=200_000, m=1,
        stream=ScalarStream(20260821, 3, 0, 0),
        fresh_stream=ScalarStream(20260821, 1, 3, 0, 0))
    g_mc = float((batch.mu_reuse - e).mean())
    se = float((batch.mu_reuse - e).std(ddof=1) / np.sqrt(batch.mu_reuse.size))
    br, _, _ = run_bracket(e)
    assert br.atom_lower - 5 * se <= g_mc <= br.atom_upper + 5 * se


def test_every_iterate_is_already_a_valid_bracket():
    """Monotonicity claim: validity does not wait for convergence."""
    part = build_partition(n_axis=50, axis_power=2.0, n_tri=12)
    struct = build_transitions(part, FloatBackend(), E_STAR, E_STAR)
    kill = best_killing_bound(E_STAR, E_STAR)
    m = a_priori_bound(abs(E_STAR), kill["arl_upper_bound"])
    it = Iterator(struct)
    lower = np.full(struct.n_cells, -m)
    upper = np.full(struct.n_cells, m)
    ref = reference_G(E_STAR, 150)
    widths = []
    for _ in range(60):
        lower, upper = it.step(lower, upper)
        assert lower[ATOM] <= ref <= upper[ATOM]
        widths.append(upper[ATOM] - lower[ATOM])
    assert widths[-1] < widths[0]
    assert all(widths[i + 1] <= widths[i] + 1e-9 for i in range(len(widths) - 1))


def test_refinement_shrinks_the_bracket_and_keeps_containment():
    ref = reference_G(E_STAR)
    widths = []
    for n_axis, n_tri in [(40, 10), (80, 16), (160, 26)]:
        br, _, _ = run_bracket(E_STAR, n_axis=n_axis, n_tri=n_tri)
        assert br.atom_lower <= ref <= br.atom_upper
        widths.append(br.atom_width)
    assert widths[0] > widths[1] > widths[2]


# ------------------------------------------------------------ backend agreement --

def test_arb_bracket_contains_the_float_bracket_result():
    ba, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10, backend=ArbBackend(bits=96))
    bf, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10, backend=FloatBackend())
    assert ba.atom_lower <= bf.atom_lower + 1e-9
    assert ba.atom_upper >= bf.atom_upper - 1e-9


@pytest.mark.parametrize("bits", [64, 96, 160])
def test_arb_precision_does_not_move_the_answer(bits):
    ref = ArbBackend(bits=96)
    br_ref, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10, backend=ref)
    br, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10, backend=ArbBackend(bits=bits))
    assert abs(br.atom_lower - br_ref.atom_lower) < 1e-8
    assert abs(br.atom_upper - br_ref.atom_upper) < 1e-8


# ------------------------------------------------------- structural invariants --

def test_total_continuation_mass_never_exceeds_one_at_thin_e():
    _, struct, _ = run_bracket(E_STAR, n_axis=60, n_tri=14)
    total = np.bincount(struct.seg_src, struct.mass_hi,
                        minlength=struct.n_cells)
    assert total.max() <= 1.0 + 1e-9


def test_every_continuation_segment_has_a_destination_inside_the_live_region():
    """Lemma L1 is checked on the actual grid, not assumed."""
    _, struct, part = run_bracket(E_STAR, n_axis=40, n_tri=10)
    assert struct.member_counts[struct.seg_type != 0].min() >= 1
    assert struct.members.max() < part.n_cells


def test_destination_lookup_returns_a_superset():
    part = build_partition(n_axis=40, axis_power=2.0, n_tri=10)
    cells = destination_cells(part, 0.4, 0.9, 0.0, 0.0)
    edges = part.axis_p_edges
    for idx in cells:
        assert part.kind[idx] in (0, 1)
    covered_lo = min(part.p_lo[i] for i in cells if part.kind[i] == 1)
    covered_hi = max(part.p_hi[i] for i in cells if part.kind[i] == 1)
    assert covered_lo <= 0.4 and covered_hi >= 0.9


def test_z_cut_must_exceed_the_alarm_reach():
    part = build_partition(n_axis=20, axis_power=2.0, n_tri=6)
    with pytest.raises(ValueError, match="z_cut"):
        build_transitions(part, FloatBackend(), E_STAR, E_STAR, z_cut=5.0)


def test_alarm_reward_lives_only_in_the_two_outer_tails():
    _, struct, part = run_bracket(E_STAR, n_axis=40, n_tri=10)
    assert set(np.unique(struct.seg_type)) <= {SEG_CONT, SEG_MIXED}
    assert struct.tail_lo.size == part.n_cells
    assert np.all(struct.tail_lo <= struct.tail_hi)


def test_bracket_is_reproducible():
    a, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10)
    b, _, _ = run_bracket(E_STAR, n_axis=40, n_tri=10)
    assert (a.atom_lower, a.atom_upper) == (b.atom_lower, b.atom_upper)


# ------------------------------------------------------------- warm starts --

def test_warm_start_agrees_with_a_cold_start():
    """A warm start may only save iterations, never change the answer.

    Soundness rests on the inflation covering |G(e2) - G(e1)| <= ||G'|| |e2-e1|;
    if it did not, the warm run would converge to something tighter than the
    truth, which this test would catch as a disagreement.
    """
    part = build_partition(n_axis=60, axis_power=2.0, n_tri=14)
    kill = best_killing_bound(E_STAR, E_STAR)
    m = a_priori_bound(abs(E_STAR), kill["arl_upper_bound"])
    st = build_transitions(part, FloatBackend(), E_STAR, E_STAR)
    cold = Iterator(st).run(m, max_iter=300)

    st0 = build_transitions(part, FloatBackend(), E_STAR - 0.001, E_STAR - 0.001)
    prev = Iterator(st0).run(m, max_iter=300)
    inflate = 0.5
    warm = Iterator(st).run(m, max_iter=300,
                            warm=(prev.lower - inflate, prev.upper + inflate))
    assert warm.atom_lower == pytest.approx(cold.atom_lower, abs=1e-9)
    assert warm.atom_upper == pytest.approx(cold.atom_upper, abs=1e-9)
    assert warm.iterations <= cold.iterations


def test_warm_start_inflation_covers_the_change_in_G():
    """The inflation must dominate the true movement of G between mesh points."""
    a = reference_G(E_STAR - 0.001, 150)
    b = reference_G(E_STAR, 150)
    kill = best_killing_bound(E_STAR, E_STAR)
    m = a_priori_bound(abs(E_STAR), kill["arl_upper_bound"])
    from mesh_certificate import INT_ABS_PHI1
    crude = kill["resolvent_upper_bound"] * (
        INT_ABS_PHI1 * m + 1.0 + abs(E_STAR) * INT_ABS_PHI1)
    assert abs(b - a) < crude * 0.001
