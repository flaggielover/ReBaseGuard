"""Exact restatement of the frozen Level 1-3 CUSUM semantics.

Every convention here is traced to ``closure/01_FROZEN_MODEL.md`` and to the
frozen implementation ``rebaseguard_certify.model``.  Regression tests in
``level4/tests/test_frozen_correspondence.py`` assert bit-level agreement with
that frozen implementation; this module must never be "improved" away from it.

Conventions (frozen, do not change)
-----------------------------------
k = 1/2, h = 5                                    01_FROZEN_MODEL.md Sec. 2
S+_t = max(0, S+_{t-1} + Z_t - k)                 01_FROZEN_MODEL.md Sec. 3
S-_t = max(0, S-_{t-1} - Z_t - k)                 (same shared innovation Z_t)
alarm iff max(S+_t, S-_t) >= h   (inclusive)      01_FROZEN_MODEL.md Sec. 4
alarm tested *after* the update                   model.py:step
tau = inf{ t >= 1 : ... }                         model.py:run_path (start=1)
T_t = sum_{s=1}^{t} Z_s, includes Z_tau           model.py:oracle_step
alarm direction: plus arm has priority on ties    model.py:step (if/elif)

Level 4 additions (fixed by the repository, not invented here)
--------------------------------------------------------------
Physical/residual split   Z_t = X_t - e, X_t iid N(0,1)
                          proofs/phase4b/convention_matrix.md line 5
Reuse statistic           mu_reuse = (1/m) sum_{r=0}^{m-1} X_{tau-r}
                          (last m raw observations, alarm observation INCLUDED)
                          rebaseguard_phase2b.md:32
Minimum dwell for m >= 2  tau_m = inf{ t >= m : max(S+,S-) >= h }
                          rebaseguard_phase2c.md:25  (convention "A")
Fresh statistic           mu_fresh = (1/m) sum_{r=1}^{m} Y_r, Y iid N(0,1),
                          independent of the stopping event
                          rebaseguard_phase2b.md:124
Mixed re-baselining       e_{j+1} = rho*mu_reuse + (1-rho)*mu_fresh
                          rebaseguard_phase2b.md:14
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Frozen detector constants.  These are the only values for which any Level 1-3
# claim is made.  They are module-level constants, never defaults to be tuned.
# --------------------------------------------------------------------------
K_FROZEN = 0.5
H_FROZEN = 5.0

ALARM_NONE = 0
ALARM_UP = 1
ALARM_DOWN = -1


def step_scalar(
    plus: float, minus: float, z: float, k: float = K_FROZEN, h: float = H_FROZEN
) -> tuple[float, float, int]:
    """One frozen CUSUM step.  Mirrors ``rebaseguard_certify.model.step`` exactly.

    Returns ``(S+, S-, alarm)`` with the alarm tested *after* the update and the
    boundary inclusive.  The plus arm takes priority on an exact tie, matching
    the ``if plus >= h: ... if minus >= h: ...`` order of the frozen source.
    """
    new_plus = max(0.0, plus + z - k)
    new_minus = max(0.0, minus - z - k)
    if new_plus >= h:
        return new_plus, new_minus, ALARM_UP
    if new_minus >= h:
        return new_plus, new_minus, ALARM_DOWN
    return new_plus, new_minus, ALARM_NONE


def cusum_update(
    plus: np.ndarray, minus: np.ndarray, z: np.ndarray, k: float, h: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Vectorised frozen CUSUM step.

    Returns ``(S+, S-, crossed_up, crossed_down)`` where the crossing flags use
    the inclusive ``>=`` boundary on the post-update state.  Note that *both*
    flags are returned untouched by any dwell constraint; applying the minimum
    dwell is the caller's responsibility so that the detector recursion itself
    stays literally the frozen one.
    """
    new_plus = np.maximum(0.0, plus + z - k)
    new_minus = np.maximum(0.0, minus - z - k)
    return new_plus, new_minus, new_plus >= h, new_minus >= h


def alarm_direction(crossed_up: np.ndarray, crossed_down: np.ndarray) -> np.ndarray:
    """Frozen alarm direction: plus-arm priority, matching ``model.step``.

    For the frozen two-sided CUSUM a simultaneous crossing is unreachable (from
    any reachable state ``p + m < h - 2k``, one step gives ``p' + m' < h``, so
    both arms cannot reach ``h`` together), but the priority rule is implemented
    literally rather than assumed vacuous, and ``count_ties`` records it.
    """
    return np.where(crossed_up, np.int8(ALARM_UP), np.int8(ALARM_DOWN))


def count_ties(crossed_up: np.ndarray, crossed_down: np.ndarray) -> int:
    """Number of simultaneous two-arm crossings (expected to be exactly 0)."""
    return int(np.count_nonzero(crossed_up & crossed_down))


def fresh_statistic_scale(m: int) -> float:
    """Standard deviation of ``mu_fresh = (1/m) sum_{r=1}^m Y_r``.

    ``mu_fresh`` is used only through its distribution (it is independent of the
    stopping event by construction), so a single ``N(0, 1/m)`` draw is
    distributionally identical to averaging ``m`` standard normals and is what
    the simulators actually draw.  This is an implementation note, not a change
    of convention: no pathwise coupling to the reuse block exists to preserve.
    """
    if m < 1:
        raise ValueError("m must be a positive integer")
    return 1.0 / np.sqrt(m)


def rebaseline(
    mu_reuse: np.ndarray, mu_fresh: np.ndarray, rho: float
) -> np.ndarray:
    """Mixed re-baselining rule ``e_next = rho*mu_reuse + (1-rho)*mu_fresh``.

    ``rho = 0`` is the *fresh* policy (matched-information control) and
    ``rho = 1`` is *full reuse*; both are exactly the endpoints of this one
    expression, so no separate code path can drift away from them.
    """
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0, 1]")
    return rho * mu_reuse + (1.0 - rho) * mu_fresh
