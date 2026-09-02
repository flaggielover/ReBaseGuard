"""Frozen detector recurrences, reconstructed from the authoritative sources.

Nothing here is copied from P9.  Each recurrence is written from the frozen
specification and then pinned by hand-computed algebra in the focused tests.

CUSUM (frozen, ``closure/01_FROZEN_MODEL.md`` via
``level4/src/rebaseguard_level4/frozen.py``)::

    S+_t = max(0, S+_{t-1} + Z_t - k)      S+_0 = 0
    S-_t = max(0, S-_{t-1} - Z_t - k)      S-_0 = 0
    alarm iff max(S+_t, S-_t) >= h         (inclusive, tested AFTER the update)

SR, symmetric two-chart, **no headstart** (``level4/stage_d/src/stopped.py``
``_sr_update``; identically restated by P7 and by the Priority-2 Route-B
module ``log_sr.py``)::

    R+_t = (1 + R+_{t-1}) exp(Z_t - 1/2)   R+_0 = 0
    R-_t = (1 + R-_{t-1}) exp(-Z_t - 1/2)  R-_0 = 0
    alarm iff max(R+_t, R-_t) >= A         (inclusive, tested AFTER the update)

The numerically stable log-domain form stores ``y = log(1 + R)`` (so ``y_0 = 0``
encodes ``R_0 = 0``) and per step computes

    ell_t = y_{t-1} + Z_t - 1/2 = log R_t          <- the ALARM statistic
    y_t   = logaddexp(0, ell_t) = log(1 + R_t)     <- the stored state

The defect repaired here is that P9 stored ``ell`` in the slot that must hold
``y`` and started it at ``0``, i.e. it evaluated ``logaddexp(0, ell_{t-1})``
where the frozen recurrence has ``y_{t-1}``.  Because ``y_0 = 0`` and
``logaddexp(0, 0) = log 2``, the *first* update of every cycle is shifted
upward by exactly ``log 2``; after a reset the shift recurs.
"""
from __future__ import annotations

import numpy as np

from . import H_FROZEN, K_FROZEN, SR_THRESHOLD


# ---------------------------------------------------------------- CUSUM
def cusum_step(plus, minus, z, k: float = K_FROZEN, h: float = H_FROZEN):
    """One frozen CUSUM step.  Returns ``(S+, S-, crossed_up, crossed_down)``."""
    new_plus = np.maximum(0.0, plus + z - k)
    new_minus = np.maximum(0.0, minus - z - k)
    return new_plus, new_minus, new_plus >= h, new_minus >= h


def cusum_initial_state(n):
    return np.zeros(n), np.zeros(n)


# ---------------------------------------------------------------- SR
def sr_step(y_plus, y_minus, z, log_thr: float):
    """One frozen SR step in the log domain.

    ``y_*`` are the stored states ``log(1 + R_*)``.  The alarm test is applied
    to ``ell_* = log R_*``, i.e. to the *post-update raw state logarithm*,
    exactly as ``classify_alarm_logs`` does in the Priority-2 module.
    """
    ell_plus = y_plus + z - 0.5
    ell_minus = y_minus - z - 0.5
    return (np.logaddexp(0.0, ell_plus), np.logaddexp(0.0, ell_minus),
            ell_plus >= log_thr, ell_minus >= log_thr)


def sr_initial_state(n):
    """``y_0 = log(1 + R_0) = log(1 + 0) = 0`` — the no-headstart convention."""
    return np.zeros(n), np.zeros(n)


# --------------------------------------------------- the P9 defective variant
def sr_step_p9_defective(s_plus, s_minus, z, log_thr: float):
    """The **defective** P9 SR update, retained only so P9R can measure it.

    Reproduced verbatim in structure from
    ``level4/closure_proofs/p9_final_synthesis/experiments/reproduce_anchors.py``::

        lrp = np.logaddexp(0.0, lrp) + Z - 0.5
        fired = max(lrp, lrm) >= log A

    This function is never used by any P9R scientific result.  It exists so
    that ``experiments/run_sr_recurrence_check.py`` can exhibit the exact
    ``log 2`` first-step shift and so that the corrected-vs-defective
    reproduction discrepancy can be quantified instead of asserted.
    """
    new_plus = np.logaddexp(0.0, s_plus) + z - 0.5
    new_minus = np.logaddexp(0.0, s_minus) - z - 0.5
    return new_plus, new_minus, new_plus >= log_thr, new_minus >= log_thr


def sr_initial_state_p9_defective(n):
    return np.zeros(n), np.zeros(n)


# ---------------------------------------------------------------- dispatch
def make_step(detector: str, *, defective_sr: bool = False):
    """Return ``(step, init, threshold, log_threshold)`` for one detector."""
    if detector == "cusum":
        if defective_sr:
            raise ValueError("defective_sr applies to the SR detector only")

        def step(plus, minus, z):
            return cusum_step(plus, minus, z)

        return step, cusum_initial_state, H_FROZEN, None
    if detector == "sr":
        log_thr = float(np.log(SR_THRESHOLD))
        if defective_sr:
            def step(plus, minus, z):
                return sr_step_p9_defective(plus, minus, z, log_thr)
            return step, sr_initial_state_p9_defective, SR_THRESHOLD, log_thr

        def step(plus, minus, z):
            return sr_step(plus, minus, z, log_thr)

        return step, sr_initial_state, SR_THRESHOLD, log_thr
    raise ValueError(f"unknown detector {detector!r}")
