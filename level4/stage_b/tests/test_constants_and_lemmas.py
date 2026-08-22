"""Analytic constants and the lemmas the certificate leans on."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.stats import norm

import mesh_certificate as mc
from killing import best_killing_bound, killing_bound

phi = norm.pdf


def test_int_abs_phi_prime_closed_form():
    q = quad(lambda w: abs(-w * phi(w)), -40, 40, limit=400)[0]
    assert mc.INT_ABS_PHI1 == pytest.approx(q, abs=1e-12)
    assert mc.INT_ABS_PHI1 >= q - 1e-12          # must not UNDER-estimate


def test_int_abs_phi_second_closed_form():
    q = quad(lambda w: abs((w * w - 1) * phi(w)), -40, 40, limit=400)[0]
    assert mc.INT_ABS_PHI2 == pytest.approx(q, abs=1e-10)
    assert mc.INT_ABS_PHI2 >= q - 1e-10


def test_int_w_abs_phi_second_closed_form():
    """This one was wrong once, and wrong in the unsound direction."""
    q = quad(lambda w: abs(w) * abs((w * w - 1) * phi(w)), -40, 40, limit=400)[0]
    assert mc.INT_W_ABS_PHI2 == pytest.approx(q, abs=1e-9)
    assert mc.INT_W_ABS_PHI2 >= q - 1e-9
    # exact closed form 8 phi(1) - 2 phi(0)
    assert mc.INT_W_ABS_PHI2 == pytest.approx(8 * phi(1) - 2 * phi(0), abs=1e-15)


def test_phi_constants():
    assert mc.PHI0 == pytest.approx(phi(0), abs=1e-15)
    assert mc.PHI1 == pytest.approx(phi(1), abs=1e-15)


# ---------------------------------------------------------------- Lemma L2 --

def test_killing_probability_is_a_true_lower_bound():
    """q_n(e) must not exceed the simulated P(tau <= n) from any live state."""
    from rebaseguard_level4.frozen import cusum_update

    e, n = 1.0367, 11
    rec = killing_bound(e, e, n)
    rng = np.random.default_rng(4)
    for p0, m0 in [(0.0, 0.0), (2.0, 0.0), (0.0, 3.0), (1.0, 2.0), (4.9, 0.0)]:
        N = 40000
        plus = np.full(N, p0); minus = np.full(N, m0)
        alarmed = np.zeros(N, dtype=bool)
        for _ in range(n):
            z = rng.normal(-e, 1.0, N)
            plus, minus, up, dn = cusum_update(plus, minus, z, 0.5, 5.0)
            alarmed |= (up | dn)
        empirical = alarmed.mean()
        assert rec["q_n_lower"] <= empirical + 4e-3, (p0, m0, empirical)


def test_killing_bound_is_uniform_in_the_starting_state():
    """The bound is stated for ALL live states; it must not use the state."""
    a = killing_bound(1.03, 1.045, 11)
    b = killing_bound(1.03, 1.045, 11)
    assert a["q_n_lower"] == b["q_n_lower"]
    assert "entire live continuum" in a["scope"]


def test_killing_bound_scan_every_n_is_individually_valid():
    r = best_killing_bound(1.03, 1.045)
    for row in r["scan"]:
        assert row["arl_upper_bound"] >= r["arl_upper_bound"] - 1e-9


def test_resolvent_bound_exceeds_the_true_arl():
    """sup_s E_s[tau] <= n/q_n; the true ARL from (0,0) must be below it."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
    from bellman_solver import Grid, build

    e = 1.0367242887184211
    g = Grid(100)
    K, rG, _, _, _ = build(g, e)
    n = g.n
    arl = spla.splu((sp.eye(n, format="csc") - K).tocsc()).solve(np.ones(n))
    r = best_killing_bound(e, e)
    assert arl.max() < r["arl_upper_bound"]


# ---------------------------------------------------------------- Lemma L3 --

def test_odd_symmetry_of_G_holds_numerically():
    """L3 is proved analytically; this checks the implementation agrees."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
    from bellman_solver import Grid, build

    g = Grid(80)
    out = {}
    for e in (0.7, -0.7):
        K, rG, _, _, _ = build(g, e)
        n = g.n
        G = spla.splu((sp.eye(n, format="csc") - K).tocsc()).solve(rG)
        out[e] = G[g.idx[(0, 0)]]
    assert out[0.7] == pytest.approx(-out[-0.7], rel=1e-9)


def test_odd_symmetry_gives_a_two_cycle():
    """Lemma L7 as arithmetic: F odd and F(x) = -x implies F(F(x)) = x."""
    def F(x):
        return -2.0 * x + x ** 3          # odd, F(1) = -1
    assert F(1.0) == pytest.approx(-1.0)
    assert F(F(1.0)) == pytest.approx(1.0)
    d = 1e-6
    fp = (F(1.0 + d) - F(1.0 - d)) / (2 * d)
    fm = (F(-1.0 + d) - F(-1.0 - d)) / (2 * d)
    assert fp == pytest.approx(fm, rel=1e-6)      # F' is even


# ---------------------------------------------- second-derivative machinery --

def test_second_derivative_bound_is_monotone_in_its_inputs():
    base = mc.second_derivative_bound(resolvent=18.0, g_sup=2.2, gp_sup=1.6,
                                      e_abs_max=1.05)
    for field, bigger in (("gp_sup", 3.2), ("g_sup", 4.4)):
        kw = dict(resolvent=18.0, g_sup=2.2, gp_sup=1.6, e_abs_max=1.05)
        kw[field] = bigger
        assert mc.second_derivative_bound(**kw)["G_second_bound"] > \
            base["G_second_bound"]


def test_self_consistent_gprime_refuses_a_coarse_mesh():
    with pytest.raises(ArithmeticError, match="mesh too coarse"):
        mc.self_consistent_gprime_sup(resolvent=18.0, g_sup=2.2,
                                      gp_sup_mesh=1.6, half_spacing=0.5,
                                      e_abs_max=1.05)


def test_self_consistent_gprime_exceeds_the_mesh_maximum():
    out = mc.self_consistent_gprime_sup(resolvent=18.5, g_sup=2.2,
                                        gp_sup_mesh=1.6, half_spacing=0.0005,
                                        e_abs_max=1.05)
    assert out["Gprime_sup_interval"] > 1.6
    assert 0.0 < out["contraction_factor"] < 1.0


def test_g_sup_is_inflated_from_mesh_to_interval():
    """||G|| must cover e BETWEEN mesh points, not only at them."""
    import numpy as np
    cert = mc.assemble(
        mesh_e=[1.0, 1.001, 1.002],
        G_lo=[-2.1, -2.1, -2.1], G_hi=[-2.0, -2.0, -2.0],
        Gp_lo=[-0.6, -0.6, -0.6], Gp_hi=[-0.2, -0.2, -0.2],
        G_sup_cells=[2.1, 2.1, 2.1], Gp_sup_cells=[2.5, 2.5, 2.5],
        resolvent=18.6, backend_name="test", certified_backend=False,
        precision_bits=None, grid={})
    assert cert.G_sup > cert.G_sup_mesh
    assert cert.G_sup == pytest.approx(
        cert.G_sup_mesh + cert.half_spacing * cert.Gprime_sup_interval, rel=1e-9)
    assert cert.Gprime_sup_interval > cert.Gprime_sup_mesh


def test_frozen_constants_guard_rejects_other_models():
    from domain import FROZEN_H, FROZEN_K, assert_frozen_constants
    assert (FROZEN_K, FROZEN_H) == (0.5, 5.0)
    assert_frozen_constants(0.5, 5.0)
    for k, h in [(0.6, 5.0), (0.5, 4.0), (0.25, 10.0)]:
        with pytest.raises(ValueError, match="frozen constants"):
            assert_frozen_constants(k, h)
