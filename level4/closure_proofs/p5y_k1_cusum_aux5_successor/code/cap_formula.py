"""The FROZEN CUSUM successor production cost-cap formula (config/COST_CAP_FORMULA.json). Non-certifying.

    P      = 1.10 * N * c_max_cpu_h                 10% measurement margin
    R      = ceil_0.5(1.25 * c_max_cpu_h)           per-cell reservation
    INFL   = W * R                                  full pool in flight at the last admission
    RETRY  = 0.03 * N * R                           ~3% of cells torn once and re-run
    OVH    = 0.02 * P                               supervisor/launcher/probe overhead
    CAP    = ceil_50(1.15 * (P + INFL + RETRY + OVH))   1.15 = frozen lifecycle invariant factor

Source methodology: p5y_k1_ps1_production/code/make_constants.py (PS1). Exact rational arithmetic.
"""
from __future__ import annotations

import math
from fractions import Fraction as F


def ceil_to(x: F, step: F) -> F:
    return F(math.ceil(x / step)) * step


def cap(*, c_max_cpu_seconds, n_cells: int = 326, workers: int = 4) -> dict:
    c = F(str(c_max_cpu_seconds)) / 3600
    P = F(11, 10) * n_cells * c
    R = ceil_to(F(5, 4) * c, F(1, 2))
    INFL = workers * R
    RETRY = F(3, 100) * n_cells * R
    OVH = F(2, 100) * P
    CAP = ceil_to(F(115, 100) * (P + INFL + RETRY + OVH), F(50))
    return {"c_max_cpu_h": float(c), "P": float(P), "R": float(R), "INFL": float(INFL), "RETRY": float(RETRY),
            "OVH": float(OVH), "CAP_cpu_h": int(CAP), "N": n_cells, "W": workers,
            "exact": {"P": str(P), "R": str(R), "CAP": str(CAP)}}
