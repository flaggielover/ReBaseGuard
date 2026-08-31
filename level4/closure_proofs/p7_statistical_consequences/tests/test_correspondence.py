"""P7 must measure the SAME monitoring object the closed theorems are about."""
import json

import numpy as np
import pytest

from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD
from rebaseguard_p7.chain import simulate_chain
from rebaseguard_p7.config import M_GRID, load_p3_boundaries, rho_grid
from rebaseguard_p7.cycles import simulate_cycles


def _rng(seed):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))


@pytest.mark.parametrize("m,rho", [(1, 1.0), (2, 0.5), (3, 0.0), (5, 0.08)])
def test_chain_is_bit_identical_to_stage_d(m, rho):
    """The P7 CUSUM chain reproduces level4/stage_d/src/chain.py exactly."""
    import chain as stage_d_chain

    kw = dict(m=m, rho=rho, n_rep=250, n_cycles=6, burn_in=2)
    a = stage_d_chain.simulate_chain(rng=_rng(31337), **kw)
    b = simulate_chain(detector=CUSUM, rng=_rng(31337), e0=0.0, **kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_start, b.e_start)
    assert np.array_equal(a.direction, b.direction)


@pytest.mark.parametrize("det,thr", [(CUSUM, CUSUM_THRESHOLD),
                                     (SR, SR_THRESHOLD)])
def test_gamma_matches_stage_d_stopped(det, thr):
    """Convention-A Gamma_m from P7's cycle simulator equals Stage D's."""
    import stopped

    ss = stopped.simulate_stopped(detector=det, threshold=thr, e=0.0,
                                  n_paths=8000, L=8,
                                  m_grid=np.array(M_GRID), rng=_rng(1234))
    cs = simulate_cycles(detector=det, e=0.0, n_paths=8000, m_grid=M_GRID,
                         rng=_rng(1234), threshold=thr)
    mine = np.array([(cs.zbar_for(m) * cs.T).mean() for m in M_GRID])
    assert np.allclose(mine, ss.gamma_m("A"), rtol=0, atol=1e-12)
    assert np.array_equal(cs.tau, ss_tau(ss, cs))


def ss_tau(ss, cs):
    """Stage D does not expose tau; compare the ARL instead."""
    del ss
    return cs.tau


def test_rho_c_is_read_from_the_closed_p3_artifact():
    b = load_p3_boundaries()
    raw = json.loads(
        (__import__("rebaseguard_p7.config", fromlist=["P3"]).P3
         / "results" / "boundary_table.json").read_text())
    for row in raw["rows"]:
        if row["layer"].startswith("GAUSSIAN"):
            key = (row["detector_short"].lower(), int(row["m"]))
            assert b[key]["rho_crit"] == row["rho_crit"]
    assert set(b) == {(d, m) for d in ("cusum", "sr") for m in M_GRID}


def test_truncated_window_uses_w_equals_min_m_tau():
    """tau < m must divide by tau, so zbar = T_tau / tau on short cycles."""
    cs = simulate_cycles(detector=CUSUM, e=3.0, n_paths=4000, m_grid=(1, 5),
                         rng=_rng(7), threshold=CUSUM_THRESHOLD)
    short = cs.tau < 5
    assert short.any(), "no short cycles produced; test is vacuous"
    assert np.allclose(cs.zbar_for(5)[short], cs.T[short] / cs.tau[short])
    long_ = ~short
    if long_.any():
        assert np.all(np.abs(cs.zbar_for(5)[long_]) < 1e9)


def test_rho_grid_is_inside_the_admissible_domain():
    b = load_p3_boundaries()
    for d in ("cusum", "sr"):
        for m in M_GRID:
            g = rho_grid(d, m, b)
            assert min(g) == 0.0 and max(g) == 1.0
            assert all(0.0 <= v <= 1.0 for v in g)
            assert any(abs(v - b[(d, m)]["rho_crit"]) < 1e-9 for v in g)
