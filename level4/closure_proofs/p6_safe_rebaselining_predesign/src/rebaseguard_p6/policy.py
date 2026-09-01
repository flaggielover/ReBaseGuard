"""Policy interface, with the observability audit enforced structurally.

The design rule of OBSERVABILITY_AUDIT.md is that an *implementable* policy
must not be able to read the latent reference error ``e_j``.  This module makes
that impossible rather than merely forbidden: the object handed to an
implementable policy has no field containing it, so there is nothing to leak.

Latent quantities are exposed only through :class:`OracleObservation`, which the
chain constructs only for a policy that declares ``policy_class == ORACLE`` (or
``DIAGNOSTIC``).  Every result record carries the class, so an oracle cannot be
silently presented as a recommendation.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Protocol

import numpy as np

from . import DIAGNOSTIC, IMPLEMENTABLE, ORACLE, POLICY_CLASSES

#: The exact audited observable set (OBSERVABILITY_AUDIT.md section 2, F01-F13).
#: tests/test_observability.py asserts CycleObservation matches this list.
AUDITED_OBSERVABLE_FIELDS = (
    "rep",              # simulation bookkeeping: which replicate each row is.
                        # Carries no information about the process; it exists so
                        # a stateful policy can address its own per-stream state.
    "cycle",            # F12  index of the cycle that just ended
    "tau",              # F01  cycle length
    "direction",        # F02  alarm arm, +1 / -1
    "stat_plus",        # F03  detector statistic, upper arm, after the update
    "stat_minus",       # F03  detector statistic, lower arm, after the update
    "overshoot",        # F04  excess of the crossing statistic over threshold
    "window",           # F05  the last L innovations z, most recent first
    "window_valid",     # F05  which window slots hold data from this cycle
    "displacement",     # F09/F10  d_j = mu_j - mu_0 = e_j - e_0, exactly known
    "last_move",        # F09  mu_j - mu_{j-1} = e_j - e_{j-1}
    "prev_tau",         # F11  previous cycle length (0 in the first cycle)
    "prev_zbar",        # F11  previous realised zbar
    "prev_rho",         # F13  the policy's own previous decisions
    "prev_m",
    "prev_k",
)

#: Latent fields, available to ORACLE / DIAGNOSTIC policies only (F14-F19).
ORACLE_ONLY_FIELDS = ("e_current", "shift")


@dataclass(frozen=True, slots=True)
class CycleObservation:
    """Everything an implementable policy may legally see at an alarm.

    Every field is an array over live replicates.  ``window`` is
    ``(n_live, L)`` with column ``r`` holding ``z_{tau - r}``; ``window_valid``
    marks the columns that belong to the cycle that just ended (a cycle shorter
    than ``L`` does not fill the buffer).

    There is deliberately no field carrying ``e``, ``raw``, ``Rbar`` or the
    shift: see FAILURE_MODE_REGISTER.md F1.
    """
    rep: np.ndarray
    cycle: int
    tau: np.ndarray
    direction: np.ndarray
    stat_plus: np.ndarray
    stat_minus: np.ndarray
    overshoot: np.ndarray
    window: np.ndarray
    window_valid: np.ndarray
    displacement: np.ndarray
    last_move: np.ndarray
    prev_tau: np.ndarray
    prev_zbar: np.ndarray
    prev_rho: np.ndarray
    prev_m: np.ndarray
    prev_k: np.ndarray

    @property
    def n(self) -> int:
        return int(self.tau.size)

    def zbar(self, m: np.ndarray | int) -> np.ndarray:
        """Observable window mean at candidate window length ``m`` (F06).

        Convention A: ``w = min(m, tau)``, truncated denominator.  Selecting
        ``m`` *after* inspecting this across candidates is legal but hazardous
        (OBSERVABILITY_AUDIT.md section 6).
        """
        m_arr = np.broadcast_to(np.asarray(m, dtype=np.int64), self.tau.shape)
        w = np.minimum(m_arr, self.tau)
        cols = np.arange(self.window.shape[1])[None, :]
        take = (cols < w[:, None]) & self.window_valid
        return np.where(take, self.window, 0.0).sum(axis=1) / w


@dataclass(frozen=True, slots=True)
class OracleObservation(CycleObservation):
    """``CycleObservation`` plus the latent state.  NEVER deployable."""
    e_current: np.ndarray = None      # F14  the true entering reference error
    shift: float = 0.0                # F18  the true shift


@dataclass(frozen=True, slots=True)
class Decision:
    """The only thing a policy may change: the reference-update line.

    ``rho`` in [0, 1]; ``m`` >= 1 is the reuse window; ``k`` >= 1 is the number
    of fresh post-alarm observations backing ``fresh ~ N(0, 1/k)``.  ``k == m``
    recovers the frozen model exactly.
    """
    rho: np.ndarray
    m: np.ndarray
    k: np.ndarray


class Policy(Protocol):
    """Structural interface.  Implementations need not subclass anything."""
    name: str
    policy_class: str
    max_m: int
    #: True if the policy reads ``displacement`` / ``last_move``.  Such a policy
    #: may only run with an unknown ``e_0`` (chain.simulate_policy_chain e0=None);
    #: see OBSERVABILITY_AUDIT.md section 4a.
    uses_history: bool

    def reset(self, n_rep: int) -> None: ...
    def decide(self, obs: CycleObservation) -> Decision: ...


class BasePolicy:
    """Convenience base: validates the class label and the decision it returns."""

    name = "base"
    policy_class = IMPLEMENTABLE
    max_m = 1
    uses_history = False

    def __init__(self) -> None:
        if self.policy_class not in POLICY_CLASSES:
            raise ValueError(f"{self.name}: bad policy_class {self.policy_class!r}")

    @property
    def requires_oracle(self) -> bool:
        return self.policy_class in (ORACLE, DIAGNOSTIC)

    def reset(self, n_rep: int) -> None:            # noqa: D102
        return None

    def decide(self, obs: CycleObservation) -> Decision:  # pragma: no cover
        raise NotImplementedError

    # -- helpers -----------------------------------------------------------
    def _full(self, obs: CycleObservation, rho, m, k) -> Decision:
        n = obs.n
        return Decision(
            rho=np.broadcast_to(np.asarray(rho, float), (n,)).astype(float),
            m=np.broadcast_to(np.asarray(m, np.int64), (n,)).astype(np.int64),
            k=np.broadcast_to(np.asarray(k, np.int64), (n,)).astype(np.int64),
        )


def validate_decision(d: Decision, n: int, max_m: int) -> None:
    """Raise unless the decision is inside the declared, frozen-compatible box."""
    for nm, a in (("rho", d.rho), ("m", d.m), ("k", d.k)):
        if a.shape != (n,):
            raise ValueError(f"decision.{nm} has shape {a.shape}, expected {(n,)}")
    if np.any(d.rho < 0.0) or np.any(d.rho > 1.0):
        raise ValueError("decision.rho outside [0, 1]")
    if np.any(d.m < 1) or np.any(d.m > max_m):
        raise ValueError(f"decision.m outside [1, {max_m}]")
    if np.any(d.k < 1):
        raise ValueError("decision.k must be >= 1")


# ---------------------------------------------------------------------------
# Baselines (P6_METHOD_CANDIDATES.md section 1).  None of these is proposed as
# a method; they are the set any method must beat.
# ---------------------------------------------------------------------------

class ConstantPolicy(BasePolicy):
    """B0-B4: fixed ``(rho, m, k)``.  The frozen model when ``k == m``."""

    policy_class = IMPLEMENTABLE

    def __init__(self, rho: float, m: int, k: int | None = None,
                 name: str | None = None) -> None:
        self.rho = float(rho)
        self.m = int(m)
        self.k = int(m if k is None else k)
        self.max_m = self.m
        self.name = name or f"const(rho={self.rho:g},m={self.m},k={self.k})"
        super().__init__()

    def decide(self, obs: CycleObservation) -> Decision:
        return self._full(obs, self.rho, self.m, self.k)


class TauThresholdWindowPolicy(BasePolicy):
    """B5: adaptive ``m`` from ``tau`` alone (F01) -- the cheapest adaptivity."""

    policy_class = IMPLEMENTABLE

    def __init__(self, rho: float, m_short: int, m_long: int, tau_split: int) -> None:
        self.rho = float(rho)
        self.m_short, self.m_long = int(m_short), int(m_long)
        self.tau_split = int(tau_split)
        self.max_m = max(self.m_short, self.m_long)
        self.name = (f"tau_window(rho={self.rho:g},m={self.m_short}/{self.m_long}"
                     f",split={self.tau_split})")
        super().__init__()

    def decide(self, obs: CycleObservation) -> Decision:
        m = np.where(obs.tau <= self.tau_split, self.m_short, self.m_long)
        return self._full(obs, self.rho, m, m)


class ZbarThresholdPolicy(BasePolicy):
    """B6: two-level ``rho`` from ``|zbar|`` alone (F08).

    This is the null that Family A must beat: it uses the high-gain sensor of
    OBSERVABILITY_AUDIT.md section 3.1 in the crudest possible way.
    """

    policy_class = IMPLEMENTABLE

    def __init__(self, m: int, rho_lo: float, rho_hi: float, q: float,
                 k: int | None = None) -> None:
        self.m = int(m)
        self.k = int(m if k is None else k)
        self.rho_lo, self.rho_hi, self.q = float(rho_lo), float(rho_hi), float(q)
        self.max_m = self.m
        self.name = (f"zbar_thresh(m={self.m},rho={self.rho_hi:g}/{self.rho_lo:g}"
                     f",q={self.q:g})")
        super().__init__()

    def decide(self, obs: CycleObservation) -> Decision:
        zbar = obs.zbar(self.m)
        rho = np.where(np.abs(zbar) <= self.q, self.rho_hi, self.rho_lo)
        return self._full(obs, rho, self.m, self.k)


# ---------------------------------------------------------------------------
# Oracles (P6_METHOD_CANDIDATES.md section 4).  Ceilings only; NEVER deployable.
# ---------------------------------------------------------------------------

class OracleResetPolicy(BasePolicy):
    """Z3: reset iff the TRUE ``|e_j|`` exceeds ``c``.  Reads F14."""

    policy_class = ORACLE

    def __init__(self, m: int, c: float, k_fresh: int | None = None) -> None:
        self.m = int(m)
        self.c = float(c)
        self.k_fresh = int(m if k_fresh is None else k_fresh)
        self.max_m = self.m
        self.name = f"oracle_reset(m={self.m},c={self.c:g},k={self.k_fresh})"
        super().__init__()

    def decide(self, obs: CycleObservation) -> Decision:
        if not isinstance(obs, OracleObservation):
            raise TypeError("OracleResetPolicy requires an OracleObservation")
        big = np.abs(obs.e_current) > self.c
        rho = np.where(big, 0.0, 1.0)
        k = np.where(big, self.k_fresh, self.m)
        return self._full(obs, rho, self.m, k)


class PooledDisplacementPolicy(BasePolicy):
    """Family E sketch: pool the aligned readouts of section 4 of the audit.

    ``zbar_i + d_i`` is a readout of the single unknown ``-e_0`` for every ``i``,
    so an EWMA over it estimates ``-e_0`` and ``ehat_j = d_j + ewma`` estimates
    ``e_j``.  The estimate is *biased* by ``R(e)``, which is of order one -- this
    is a feasibility sketch for the harness, NOT the proposed method.

    Requires an unknown ``e_0``: with ``e0`` fixed and known the same arithmetic
    would reconstruct the latent state exactly (audit section 4a).
    """

    policy_class = IMPLEMENTABLE
    uses_history = True

    def __init__(self, m: int, rho_lo: float, rho_hi: float, c: float,
                 alpha: float = 0.3, k: int | None = None) -> None:
        self.m = int(m)
        self.k = int(m if k is None else k)
        self.rho_lo, self.rho_hi, self.c = float(rho_lo), float(rho_hi), float(c)
        self.alpha = float(alpha)
        self.max_m = self.m
        self.name = (f"pooled_disp(m={self.m},rho={self.rho_hi:g}/{self.rho_lo:g}"
                     f",c={self.c:g},alpha={self.alpha:g})")
        self._ewma = None
        super().__init__()

    def reset(self, n_rep: int) -> None:
        self._ewma = np.zeros(n_rep)
        self._seen = np.zeros(n_rep, dtype=bool)

    def decide(self, obs: CycleObservation) -> Decision:
        zbar = obs.zbar(self.m)
        reading = -(zbar + obs.displacement)          # a readout of e_0
        # NOTE: indices here are over live replicates only; the harness passes a
        # contiguous slice, so the sketch keeps a full-length state and updates
        # the rows it saw.  A campaign-grade version must carry the live index.
        r = obs.rep
        prev, seen = self._ewma[r], self._seen[r]
        self._ewma[r] = np.where(seen, (1 - self.alpha) * prev + self.alpha * reading,
                                 reading)
        self._seen[r] = True
        ehat = obs.displacement - self._ewma[r]
        rho = np.where(np.abs(ehat) <= self.c, self.rho_hi, self.rho_lo)
        return self._full(obs, rho, self.m, self.k)
