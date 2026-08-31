"""Frozen detector recurrences, restated once for both P7 simulators.

CUSUM comes from the frozen module by import (never re-implemented).
SR is the two-chart log-domain softplus recursion of
``level4/stage_d/src/stopped.py::_sr_update``, restated verbatim so that the P7
chain does not have to import a Stage-D private helper.
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

from . import CUSUM, SR, SR_THRESHOLD                # noqa: E402


def sr_update(yp, ym, z, log_thr):
    """One frozen SR step in the log domain; identical to Stage D's helper."""
    log_r_plus = yp + z - 0.5
    log_r_minus = ym - z - 0.5
    return (np.logaddexp(0.0, log_r_plus), np.logaddexp(0.0, log_r_minus),
            log_r_plus >= log_thr, log_r_minus >= log_thr)


def make_step(detector: str, threshold: float | None = None):
    """Return ``(step, threshold, log_thr)`` for the requested frozen detector.

    ``step(plus, minus, z) -> (plus', minus', crossed_up, crossed_down)`` with
    the inclusive post-update alarm test of the frozen model.
    """
    if detector == CUSUM:
        thr = H_FROZEN if threshold is None else float(threshold)

        def step(plus, minus, z):
            return cusum_update(plus, minus, z, K_FROZEN, thr)

        return step, thr, None
    if detector == SR:
        thr = SR_THRESHOLD if threshold is None else float(threshold)
        if thr <= 1.0:
            raise ValueError("SR threshold A must exceed 1; pass NATURAL units")
        log_thr = float(np.log(thr))

        def step(plus, minus, z):
            return sr_update(plus, minus, z, log_thr)

        return step, thr, log_thr
    raise ValueError(f"unknown detector {detector!r}")
