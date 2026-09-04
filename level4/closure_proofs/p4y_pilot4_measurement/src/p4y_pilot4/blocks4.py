"""Base blocks, and exact aggregation to larger logical block sizes.

THE IDENTITY THIS RESTS ON.  Every frozen per-block statistic is a PLAIN
AVERAGE of per-path contributions:

    Route A   gamma_m = mean_paths( A_m * sum psi(Z) )
    Route B   Richardson = (4 D(h/2) - D(h))/3, and each D is itself
              mean_paths( -(A_m(+h) - A_m(-h)) / 2h ); the combination is
              linear, so the block value is linear in the path averages.

Therefore the block value over ``k*n`` paths equals the mean of ``k``
independent block values over ``n`` paths, EXACTLY -- not approximately.
`tests/test_aggregation_identity.py` verifies this bit-for-bit by splitting a
simulated block's own paths, so the property is checked rather than assumed.

Two consequences, both load-bearing for Pilot-4:

  * a 4 000 000-path logical block costs ~1.2 GB if simulated in one piece;
    built from 80 base blocks of 50 000 it costs 2 MB.  The probe measured
    318 MB for a single 1 000 000-path block, so the direct route does not
    scale to the frozen grid;
  * one base pool serves EVERY block size in the grid, which is what makes
    the three-block-size sweep affordable.  Analyses at different block sizes
    then share paths; that is disclosed, and it makes the comparison ACROSS
    block sizes a common-random-number comparison rather than a noisy one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_P1 = Path(__file__).resolve().parents[3] / "p4y_precision_governance_pilot"
if str(_P1 / "src") not in sys.path:
    sys.path.insert(0, str(_P1 / "src"))

from p4y_pilot.blocks import Cell, block_value  # noqa: E402

#: Every logical block size in the frozen grid is a multiple of this.
BASE_BLOCK_PATHS = 50_000
M_PRIMARY = 1


def base_series(cell: Cell, stream_seed: int, n_base: int, m: int = M_PRIMARY,
                cache: dict | None = None) -> np.ndarray:
    """``n_base`` base-block values for one logical stream, at window ``m``."""
    out = np.empty(n_base, dtype=float)
    for i in range(n_base):
        if cache is not None and i in cache:
            out[i] = cache[i]
            continue
        v = block_value(cell, stream_seed, i)[m]
        if cache is not None:
            cache[i] = v
        out[i] = v
    return out


def aggregate(base: np.ndarray, factor: int) -> np.ndarray:
    """Exact logical block means at ``factor * BASE_BLOCK_PATHS`` paths.

    Trailing base blocks that do not fill a whole logical block are dropped,
    so every returned value is an average over exactly the same path count.
    """
    if factor < 1:
        raise ValueError("factor must be >= 1")
    usable = (base.size // factor) * factor
    if usable == 0:
        return np.empty(0, dtype=float)
    return base[:usable].reshape(-1, factor).mean(axis=1)


def factor_for(block_paths: int) -> int:
    if block_paths % BASE_BLOCK_PATHS:
        raise ValueError(f"{block_paths} is not a multiple of {BASE_BLOCK_PATHS}")
    return block_paths // BASE_BLOCK_PATHS


def base_blocks_needed(block_paths: int, n_logical: int) -> int:
    return factor_for(block_paths) * n_logical
