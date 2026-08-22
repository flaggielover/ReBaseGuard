"""The certified G' bracket must contain the true derivative.

The derivative is obtained from the differentiated operator equation (Lemma
L6), never from a finite difference.  The finite difference is used here only
as an INDEPENDENT reference to check containment.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from backends import ArbBackend, FloatBackend
from bellman_solver import Grid, build as bs_build
from derivative import DerivativeIterator, interval_mul
from domain import build_partition
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from transitions import build_transitions

E_STAR = 1.0367242887184211


def reference_G(e: float, n_solver: int = 200) -> float:
    g = Grid(n_solver)
    K, rG, _, _, _ = bs_build(g, e)
    n = g.n
    return float(spla.splu((sp.eye(n, format="csc") - K).tocsc())
                 .solve(rG)[g.idx[(0, 0)]])


def reference_Gprime(e: float, delta: float = 1e-4, n_solver: int = 200) -> float:
    return (reference_G(e + delta, n_solver)
            - reference_G(e - delta, n_solver)) / (2 * delta)


def run_pair(e, *, n_axis=80, n_tri=16, backend=None):
    backend = backend or FloatBackend()
    part = build_partition(n_axis=n_axis, axis_power=2.0, n_tri=n_tri)
    struct = build_transitions(part, backend, e, e)
    kill = best_killing_bound(e, e)
    m = a_priori_bound(abs(e), kill["arl_upper_bound"])
    br = Iterator(struct).run(m, max_iter=250)
    di = DerivativeIterator(struct, backend, br.lower, br.upper,
                            kill["resolvent_upper_bound"], 12.0)
    return br, di.run(max_iter=250), kill


def test_interval_mul_handles_sign_changes():
    lo, hi = interval_mul(np.array([-2.0]), np.array([3.0]),
                          np.array([-1.0]), np.array([4.0]))
    assert lo[0] == pytest.approx(-8.0)
    assert hi[0] == pytest.approx(12.0)
    lo, hi = interval_mul(np.array([-3.0]), np.array([-1.0]),
                          np.array([-2.0]), np.array([-0.5]))
    assert lo[0] == pytest.approx(0.5)
    assert hi[0] == pytest.approx(6.0)


def test_derivative_bracket_contains_the_finite_difference_reference():
    _, db, _ = run_pair(E_STAR)
    ref = reference_Gprime(E_STAR)
    assert db.atom_lower <= ref <= db.atom_upper, (db.atom_lower, ref,
                                                   db.atom_upper)


@pytest.mark.parametrize("e", [0.5, 1.0367242887184211, 1.6])
def test_derivative_bracket_contains_reference_across_e(e):
    _, db, _ = run_pair(e, n_axis=60, n_tri=14)
    ref = reference_Gprime(e, 1e-4, 150)
    assert db.atom_lower <= ref <= db.atom_upper, (e, db.atom_lower, ref,
                                                   db.atom_upper)


def test_F1_prime_bracket_contains_the_stage_a_branch_value():
    """Claude Science reports F_1'(e*) = 0.5915457 at rho = 1."""
    _, db, _ = run_pair(E_STAR, n_axis=120, n_tri=20)
    lo, hi = 1.0 + db.atom_lower, 1.0 + db.atom_upper
    assert lo <= 0.5915457061865803 <= hi


def test_derivative_refinement_shrinks_and_keeps_containment():
    ref = reference_Gprime(E_STAR)
    widths = []
    for n_axis, n_tri in [(40, 10), (80, 16), (160, 26)]:
        _, db, _ = run_pair(E_STAR, n_axis=n_axis, n_tri=n_tri)
        assert db.atom_lower <= ref <= db.atom_upper
        widths.append(db.atom_width)
    assert widths[0] > widths[1] > widths[2]


def test_derivative_uses_the_G_bracket_and_widens_with_it():
    """A wider G bracket must give a wider G' bracket, never a narrower one."""
    part = build_partition(n_axis=60, axis_power=2.0, n_tri=14)
    struct = build_transitions(part, FloatBackend(), E_STAR, E_STAR)
    kill = best_killing_bound(E_STAR, E_STAR)
    m = a_priori_bound(abs(E_STAR), kill["arl_upper_bound"])
    br = Iterator(struct).run(m, max_iter=250)
    tight = DerivativeIterator(struct, FloatBackend(), br.lower, br.upper,
                               kill["resolvent_upper_bound"], 12.0).run()
    loose = DerivativeIterator(struct, FloatBackend(), br.lower - 0.05,
                               br.upper + 0.05,
                               kill["resolvent_upper_bound"], 12.0).run()
    assert loose.atom_width > tight.atom_width
    assert loose.atom_lower <= tight.atom_lower
    assert loose.atom_upper >= tight.atom_upper


def test_arb_derivative_encloses_the_float_derivative():
    _, da, _ = run_pair(E_STAR, n_axis=40, n_tri=10, backend=ArbBackend(bits=96))
    _, df, _ = run_pair(E_STAR, n_axis=40, n_tri=10, backend=FloatBackend())
    assert da.atom_lower <= df.atom_lower + 1e-8
    assert da.atom_upper >= df.atom_upper - 1e-8


def test_derivative_weights_match_a_finite_difference_of_the_mass():
    """dw = d(mass)/de and dr = d(zmom)/de, checked numerically."""
    fb = FloatBackend()
    a = np.array([-2.0, -0.3, 1.1]); b = np.array([-1.0, 0.4, 2.0])
    e, d = 1.0367, 1e-6
    dw, _, dr, _, _ = fb.derivative_integrals(a, b, e, e)
    m1, _, z1, _ = fb.segment_integrals(a, b, e + d, e + d)
    m0, _, z0, _ = fb.segment_integrals(a, b, e - d, e - d)
    assert np.allclose(dw, (m1 - m0) / (2 * d), atol=1e-7)
    assert np.allclose(dr, (z1 - z0) / (2 * d), atol=1e-7)


def test_tail_derivative_matches_a_finite_difference():
    fb = FloatBackend()
    A = np.array([-5.5, -4.0]); B = np.array([4.4, 3.0])
    e, d = 1.0367, 1e-6
    dlo, _ = fb.tail_derivative(A, B, e, e)
    t1, _ = fb.tail_moment(A, B, e + d, e + d)
    t0, _ = fb.tail_moment(A, B, e - d, e - d)
    assert np.allclose(dlo, (t1 - t0) / (2 * d), atol=1e-7)
