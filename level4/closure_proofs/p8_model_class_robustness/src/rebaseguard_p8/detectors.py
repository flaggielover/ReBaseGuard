"""Frozen detector recurrences.

Both detector statistics are **frozen exactly as designed for the Gaussian
model** and are applied unchanged to every innovation family.  Only the
threshold is recalibrated per family, which is the Stage-D D3 convention
(``stage_d/src/run_d3_nongaussian.py``) and the operationally realistic
scenario: a practitioner deploys the standard chart and tunes its limit.

CUSUM is imported from the frozen module and never re-implemented.  SR is the
two-chart log-domain softplus recursion of ``level4/stage_d/src/stopped.py``,
restated exactly as ``p7/detectors.py`` restates it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(_ROOT / "level4" / "src"))
from rebaseguard_level4.frozen import (            # noqa: E402
    H_FROZEN, K_FROZEN, cusum_update,
)

from . import CUSUM, SR, SR_THRESHOLD_GAUSSIAN     # noqa: E402


def sr_update(yp, ym, z, log_thr):
    """One frozen SR step in the log domain; identical to Stage D's helper."""
    log_r_plus = yp + z - 0.5
    log_r_minus = ym - z - 0.5
    return (np.logaddexp(0.0, log_r_plus), np.logaddexp(0.0, log_r_minus),
            log_r_plus >= log_thr, log_r_minus >= log_thr)


def make_step(detector: str, threshold: float | None = None):
    """Return ``(step, threshold)`` for the requested frozen detector.

    ``step(plus, minus, z) -> (plus', minus', crossed_up, crossed_down)`` with
    the inclusive post-update alarm test of the frozen model.  ``threshold`` is
    in NATURAL units for both detectors (``h`` for CUSUM, ``A`` for SR).
    """
    if detector == CUSUM:
        thr = H_FROZEN if threshold is None else float(threshold)

        def step(plus, minus, z):
            return cusum_update(plus, minus, z, K_FROZEN, thr)

        return step, thr
    if detector == SR:
        thr = SR_THRESHOLD_GAUSSIAN if threshold is None else float(threshold)
        if thr <= 1.0:
            raise ValueError("SR threshold A must exceed 1; pass NATURAL units")
        log_thr = float(np.log(thr))

        def step(plus, minus, z):
            return sr_update(plus, minus, z, log_thr)

        return step, thr
    raise ValueError(f"unknown detector {detector!r}")
