"""P5 focused tests: frozen-semantics correspondence and audit identities."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parents[0] / "p7_statistical_consequences" / "src"))

from rebaseguard_p5 import RESULTS, P3                       # noqa: E402
from rebaseguard_p5.chain import simulate_chain_raw          # noqa: E402
from rebaseguard_p5.kernel import simulate_raw_cycles        # noqa: E402
from rebaseguard_p7.chain import simulate_chain as p7_chain  # noqa: E402
from rebaseguard_p7.cycles import simulate_cycles as p7_cycles  # noqa: E402

CASES = [(d, m, r) for d in ("cusum", "sr") for m in (1, 3, 5)
         for r in (0.5, 1.0)]


@pytest.mark.parametrize("det,m,rho", CASES)
def test_raw_mean_identity_matches_frozen_chain(det, m, rho):
    """AUDIT-1: e_{j+1} = rho*Rbar + (1-rho)*fresh reproduces the frozen chain."""
    kw = dict(detector=det, m=m, rho=rho, n_rep=200, n_cycles=60, burn_in=0)
    a = p7_chain(rng=np.random.Generator(np.random.PCG64(7)), **kw)
    b = simulate_chain_raw(rng=np.random.Generator(np.random.PCG64(7)), **kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.abs(a.e_start - b.e_start).max() < 1e-13


@pytest.mark.parametrize("det", ["cusum", "sr"])
@pytest.mark.parametrize("e", [0.0, 0.4, -1.3])
def test_cycle_identity_matches_frozen_cycles(det, e):
    """Rbar_w == e + zbar_m on the frozen P7 cycle object, path by path."""
    m_grid = (1, 2, 3, 5)
    a = p7_cycles(detector=det, e=e, n_paths=4000, m_grid=m_grid,
                  rng=np.random.Generator(np.random.PCG64(11)))
    b = simulate_raw_cycles(detector=det, e=e, n_paths=4000, m_grid=m_grid,
                            rng=np.random.Generator(np.random.PCG64(11)))
    assert np.array_equal(a.tau, b.tau)
    assert np.abs((a.zbar + e) - b.rbar).max() < 1e-12


@pytest.mark.parametrize("det", ["cusum", "sr"])
def test_window_denominator_is_truncated(det):
    """w = min(m, tau) with denominator w: for tau=1 every m gives Rbar=raw_tau."""
    s = simulate_raw_cycles(detector=det, e=7.0, n_paths=20000,
                            m_grid=(1, 2, 3, 5),
                            rng=np.random.Generator(np.random.PCG64(3)))
    one = s.tau == 1
    assert one.sum() > 100
    for j in range(1, 4):
        assert np.abs(s.rbar[j, one] - s.rbar[0, one]).max() < 1e-12


def test_slope_at_zero_matches_p3_boundary_table():
    """AUDIT/§6: R'(0) reproduces the frozen P3 1 - GammaTilde within 3%."""
    a = json.loads((RESULTS / "map_analysis.json").read_text())
    for c in a["cells"]:
        assert c["rel_err_vs_p3"] < 0.03, (c["detector"], c["m"],
                                           c["rel_err_vs_p3"])


def test_p3_boundary_table_untouched():
    t = json.loads((P3 / "results" / "boundary_table.json").read_text())
    got = {(r["detector_short"], int(r["m"])): round(r["rho_crit"], 4)
           for r in t["rows"] if r["layer"].startswith("GAUSSIAN")}
    assert got == {("CUSUM", 1): 0.067, ("CUSUM", 2): 0.0815,
                   ("CUSUM", 3): 0.0913, ("CUSUM", 5): 0.1084,
                   ("SR", 1): 0.0608, ("SR", 2): 0.0741,
                   ("SR", 3): 0.0835, ("SR", 5): 0.0995}
