"""P5X R8: binding SR certification -- B2 dual-representation cell certifier.

FAST KERNEL   : R6 monomial grouped closed form (unchanged, used for the exact
                cell-centre value).
CERTIFICATION : exact monomial->Bernstein, exact degree elevation 16->32 for the
                derivative hulls, exact de Casteljau cell restriction for ghat's
                hull, closed-form kernel weights, mean-value range enclosure.

K_e is NEVER applied to a Bernstein basis image (that route was measured at
1.9324e6 in the B2 audit and is rejected).
"""
from __future__ import annotations

import sys
from math import comb
from pathlib import Path

from flint import arb

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "sr_full_cell_prototype", _NS / "compute_optimization_r6_minimal_evaluator",
           _NS / "compute_optimization_r4_xi_reformulation", _NS / "b2_basis_feasibility_audit",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import bernstein as BB                                            # noqa: E402
import sr_prototype as SP                                         # noqa: E402
from minimal_evaluator import COUNTERS, I_k, live_limits, sr_constants  # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational      # noqa: E402

DEGREE, ELEVATED, GRID = 16, 32, 256


def elevate1d(b, n, N):
    return [sum((b[i] * arb(comb(n, i)) * arb(comb(N - n, k - i)) / arb(comb(N, k))
                 for i in range(max(0, k - (N - n)), min(n, k) + 1)), arb(0))
            for k in range(N + 1)]


def elevate2d(bt, n, N):
    r = [elevate1d([bt[i][j] for i in range(n + 1)], n, N) for j in range(n + 1)]
    cN = [elevate1d([r[j][i] for j in range(n + 1)], n, N) for i in range(N + 1)]
    return [[cN[i][j] for j in range(N + 1)] for i in range(N + 1)]


def precompute(coef):
    """Candidate-global: Bernstein form, elevated derivative hulls, |ghat|max."""
    n = len(coef) - 1
    beta = BB.mono_to_bern_2d(coef)
    bN = elevate2d(beta, n, ELEVATED)
    N = ELEVATED
    Mx = max(abs(float(v.mid())) + float(v.rad())
             for i in range(N) for j in range(N + 1)
             for v in [arb(N) * (bN[i + 1][j] - bN[i][j])])
    My = max(abs(float(v.mid())) + float(v.rad())
             for i in range(N + 1) for j in range(N)
             for v in [arb(N) * (bN[i][j + 1] - bN[i][j])])
    glo = min(float(x.lower()) for r in beta for x in r)
    ghi = max(float(x.upper()) for r in beta for x in r)
    return {"beta": beta, "Mx": Mx, "My": My, "gmax": max(abs(glo), abs(ghi)),
            "hull": (glo, ghi), "coef": coef}


def certify_cell(pre, i: int, j: int, e: arb, A: arb, grid: int = GRID):
    """Rigorous enclosure of sup |r| over cell (i,j).  Returns (bound, parts)."""
    x0, x1 = arb(i) / arb(grid), arb(i + 1) / arb(grid)
    y0, y1 = arb(j) / arb(grid), arb(j + 1) / arb(grid)
    zp = (x0 + x1) / arb(2) + ((x1 - x0) / arb(2)) * arb(0, 1)
    zm = (y0 + y1) / arb(2) + ((y1 - y0) / arb(2)) * arb(0, 1)
    xc, yc = (x0 + x1) / arb(2), (y0 + y1) / arb(2)
    h = (x1 - x0) / arb(2)

    l, u = live_limits(zp, zm, A)
    wp, wm = arb(1) / A + zp, arb(1) / A + zm
    TP = (arb(2) * arb.pi()).sqrt()

    # exact centre residual, via the unchanged R6 fast kernel
    rc = SP.residual_on_cell(pre["coef"], xc, yc, e, A)
    # ghat oscillation on the cell: exact de Casteljau hull (sharp)
    sub = BB.restrict_cell(pre["beta"], x0, x1, y0, y1)
    glo, ghi = BB.hull_range(sub)
    # rho_1 oscillation, bounded by its enclosure width
    r1 = SP.rho1_arb(l, u, e)
    # K_e ghat oscillation, mean-value with Bernstein-hull derivative bounds
    IEp = (-e).exp() * (gaussian_cdf(u + e - arb(1)) - gaussian_cdf(l + e - arb(1)))
    IEm = (e).exp() * (gaussian_cdf(u + e + arb(1)) - gaussian_cdf(l + e + arb(1)))
    Gm = arb(pre["gmax"])
    gx = arb(pre["Mx"]) * IEp + Gm * (-(u + e) * (u + e) / arb(2)).exp() / TP / wp
    gy = arb(pre["My"]) * IEm + Gm * (-(l + e) * (l + e) / arb(2)).exp() / TP / wm
    Kw = 2.0 * float(h) * (float(gx.upper()) + float(gy.upper()))

    bound = (abs(float(rc.mid())) + float(rc.rad())
             + (ghi - glo) + 2.0 * float(r1.rad()) + Kw)
    return bound, {"centre": abs(float(rc.mid())), "ghat_osc": ghi - glo,
                   "rho1_osc": 2.0 * float(r1.rad()), "Ke_osc": Kw,
                   "gx": float(gx.upper()), "gy": float(gy.upper())}
