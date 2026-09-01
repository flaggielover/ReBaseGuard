"""TUNE-only selection of the fixed-``rho`` baseline.

Blocking defect 1 of the independent adjudication: the original campaign's
``B2*`` was chosen as the grid member minimising the objective **on the EVAL
table itself**, and re-chosen on REPLAY.  That is selection on the evaluation
data, and it invalidates the comparison it was meant to anchor.

The repaired rule, frozen here **before any P6R EVAL run**:

```text
S1  for each cell (detector, m, k):
      grid      RHO_FINE = {0.05, 0.06, ..., 0.35}          31 points
      family    TUNE, and TUNE only
      arm       Delta = 1, shift_cycle = 15, n_rep = N_SELECT replicates
      curve     d(rho)  = TUNE estimate of Dtail(100)
      smoothing s(rho)  = centred 5-point moving average of d, edge-truncated
      choice    rho*_TUNE = argmin_rho s(rho)
      ties      smaller smoothed Dq95, then smaller rho
```

The 5-point moving average is part of the rule, not a post-hoc filter: on a
`0.01`-spaced grid the fixed-``rho`` objective is nearly flat over `[0.15, 0.30]`
and a raw argmin over 31 correlated noisy points is dominated by selection
noise.  Smoothing gives the baseline its **best** shot, which is what an honest
bar requires.  The unsmoothed argmin, the ``Arl0`` argmax and the ``Rms`` argmin
are all recorded as TUNE diagnostics so that a reviewer can see the whole curve.

A second, independently motivated control is declared here as well: the value
``rho = 0.25`` that the independent adjudication itself identified as the
TUNE-selected optimum for the primary CUSUM ``m=3, k=3`` cell.  It is carried
into confirmation as a **declared secondary control** whether or not S1 selects
it, and the headline claim must survive against whichever of the two controls is
*less favourable to SAW-M*.  That is a strictly harder bar than S1 alone, and it
is fixed before any EVAL number exists.
"""
from __future__ import annotations

import numpy as np

#: The frozen fine grid.  31 points, 0.01 spacing.
RHO_FINE = tuple(round(0.05 + 0.01 * i, 2) for i in range(31))
#: Replicates per grid point in the TUNE selection arm.
N_SELECT = 150_000
#: Shift and injection cycle for the selection arm.
SELECT_SHIFT = 1.0
SELECT_SHIFT_CYCLE = 15
#: Half-width of the centred moving average (5-point window => 2).
SMOOTH_HALFWIDTH = 2
#: The adjudication-identified secondary control for the primary cell.
ADJUDICATION_CONTROL_RHO = 0.25


def moving_average(y, halfwidth: int = SMOOTH_HALFWIDTH) -> np.ndarray:
    """Centred moving average with edge truncation (no padding, no wrap)."""
    y = np.asarray(y, float)
    n = y.size
    out = np.empty(n, float)
    for i in range(n):
        lo = max(0, i - halfwidth)
        hi = min(n, i + halfwidth + 1)
        out[i] = y[lo:hi].mean()
    return out


def select_rho(dtail100, dq95, grid=RHO_FINE,
               halfwidth: int = SMOOTH_HALFWIDTH) -> dict:
    """Apply rule S1 to a TUNE curve.  Pure function; no simulation."""
    grid = np.asarray(grid, float)
    d = np.asarray(dtail100, float)
    q = np.asarray(dq95, float)
    if not (grid.size == d.size == q.size):
        raise ValueError("grid, dtail100 and dq95 must be the same length")
    sd = moving_average(d, halfwidth)
    sq = moving_average(q, halfwidth)
    best = float(sd.min())
    cand = np.flatnonzero(sd <= best + 1e-15)
    if cand.size > 1:                                   # tie -> smoothed Dq95
        qbest = float(sq[cand].min())
        cand = cand[sq[cand] <= qbest + 1e-15]
    i = int(cand[0])                                    # then smallest rho
    return {
        "rule": "S1",
        "rho_selected": float(grid[i]),
        "index": i,
        "grid": grid.tolist(),
        "dtail100_tune": d.tolist(),
        "dtail100_smoothed": sd.tolist(),
        "dq95_tune": q.tolist(),
        "dq95_smoothed": sq.tolist(),
        "rho_argmin_unsmoothed": float(grid[int(np.argmin(d))]),
        "smoothing_halfwidth": int(halfwidth),
        "n_tied_at_optimum": int(cand.size),
    }
