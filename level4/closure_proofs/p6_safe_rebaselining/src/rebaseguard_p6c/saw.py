"""Selection-aware weighting (SAW): the P6 candidate method and its ablations.

Mechanism, in one line: **the reuse weight is the inverse-variance weight
between the reused terminal-window mean and the fresh baseline, evaluated
cycle-by-cycle from an observable estimate of how strongly this particular
alarm selected its window.**

Derivation (exact, from T1/T2, which the P5 adjudication licenses for the
frozen constant-policy Gaussian convention-A model and which extend verbatim to
an ``F_j``-measurable decision because the policy acts only between cycles):

    e_{j+1} = rho_j Rbar_j + (1 - rho_j) fresh_j ,   fresh_j ~ N(0, 1/k_j) indep.

so for any ``F_j``-measurable ``rho_j``,

    E[e_{j+1}^2 | F_j] = rho_j^2 V_j + (1 - rho_j)^2 nu ,
    V_j = E[Rbar_j^2 | F_j] ,   nu = 1/k_j ,

a strictly convex quadratic minimised at

    rho*_j = nu / (V_j + nu) ,      giving   Q*(V_j) = nu V_j / (V_j + nu) .

``Q*`` is strictly concave, so by Jensen the achievable one-step risk under the
adaptive rule is strictly below the best constant-``rho`` risk whenever ``V_j``
is non-degenerate -- **fixed-rho tuning is exactly the ``V_j = const`` member of
this family.**  See ``THEORY.md`` T6-C.

``V_j`` is latent.  ``SawPolicy`` substitutes the design-time plug-in of
``calibrate.SawCalibration``; ``OracleSawPolicy`` substitutes the realised
``Rbar_j^2`` and is the ceiling for the rule shape.
"""
from __future__ import annotations

import numpy as np

from . import IMPLEMENTABLE, ORACLE
from .calibrate import RHO_MAX, S_FLOOR, SawCalibration
from .policy import BasePolicy, CycleObservation, Decision, OracleObservation


def _rho_from_v(v, nu, rho_max=RHO_MAX):
    return np.minimum(nu / (np.maximum(v, S_FLOOR) + nu), rho_max)


# --- the tail-targeted variant's inner minimisation -------------------------

#: Grid over rho used by SAW-T.  Structural (a numerical quadrature), not tuned.
_RHO_GRID = np.linspace(0.0, RHO_MAX, 96)


def _tail_optimal_rho(mu, s, nu, c, rho_grid=_RHO_GRID):
    """argmin_rho P(|N(rho mu, rho^2 s + (1-rho)^2 nu)| > c), vectorised.

    The Gaussian form is an approximation to the true one-step law of
    ``Rbar | F_j`` (which is a selected raw-window mean, not exactly normal);
    it is declared as such in ``METHOD.md`` and is the reason SAW-T is reported
    as an *approximate* one-step tail rule rather than a derived optimum.
    """
    from scipy.stats import norm
    mu = np.asarray(mu, float)[:, None]
    s = np.asarray(s, float)[:, None]
    r = rho_grid[None, :]
    sd = np.sqrt(r * r * s + (1.0 - r) ** 2 * nu)
    sd = np.maximum(sd, 1e-12)
    m = r * mu
    p = norm.sf((c - m) / sd) + norm.cdf((-c - m) / sd)
    return rho_grid[np.argmin(p, axis=1)]


# ---------------------------------------------------------------------------
# implementable
# ---------------------------------------------------------------------------

class SawPolicy(BasePolicy):
    """SAW-M: the derived second-moment rule with the design-time plug-in.

    Information set: ``tau_j`` (F01), the terminal window (F05/F06) through
    ``zbar_j`` and ``w_j = min(m, tau_j)``.  Nothing else -- **memoryless**, so
    the closed-loop chain stays a time-homogeneous Markov chain and
    ``THEORY.md`` T6-B applies.  No latent quantity, no future information, no
    knowledge of ``Delta``.

    ``mode``:
      * ``"full"``    -- the calibrated plug-in (the proposed method)
      * ``"no_tau"``  -- ablation: drop the stopping-geometry feature (g1 = 0)
      * ``"naive"``   -- ablation: the naive magnitude proxy V = zbar^2
      * ``"flat"``    -- ablation: remove the sensor entirely, V = E[V];
                         this is *exactly* a fixed-rho policy and is the null
    """

    policy_class = IMPLEMENTABLE
    uses_history = False

    def __init__(self, calib: SawCalibration, *, k: int | None = None,
                 mode: str = "full", v_bar: float | None = None,
                 rho_max: float = RHO_MAX, name: str | None = None) -> None:
        if mode not in ("full", "no_tau", "naive", "flat"):
            raise ValueError(f"unknown SAW mode {mode!r}")
        self.calib = calib
        self.m = int(calib.m)
        self.k = int(calib.k if k is None else k)
        self.nu = 1.0 / self.k
        self.mode = mode
        self.rho_max = float(rho_max)
        self.v_bar = v_bar
        if mode == "flat" and v_bar is None:
            raise ValueError("mode='flat' needs v_bar (the calibrated mean of V)")
        self.max_m = self.m
        self.name = name or f"saw_m[{mode}](m={self.m},k={self.k})"
        super().__init__()

    # -- the plug-in -------------------------------------------------------
    def v_of(self, obs: CycleObservation):
        zbar = obs.zbar(self.m)
        tau = obs.tau.astype(float)
        w = np.minimum(self.m, obs.tau).astype(float)
        if self.mode == "flat":
            return np.full(zbar.shape, float(self.v_bar)), zbar
        if self.mode == "naive":
            return zbar * zbar, zbar
        c = self.calib
        g1 = 0.0 if self.mode == "no_tau" else c.g1
        g0 = c.g0 if self.mode != "no_tau" else self._g0_no_tau()
        mu = (g0 + g1 / np.sqrt(tau)) * zbar
        s = np.maximum(np.where(w < float(self.m), c.s1, c.s0), S_FLOOR)
        return mu * mu + s, zbar

    def _g0_no_tau(self):
        # The no-tau ablation must not silently inherit a coefficient fitted in
        # the presence of the dropped feature; the campaign fits it separately
        # and injects it here.
        return getattr(self, "_g0_alt", self.calib.g0)

    def decide(self, obs: CycleObservation) -> Decision:
        v, _ = self.v_of(obs)
        rho = _rho_from_v(v, self.nu, self.rho_max)
        return self._full(obs, rho, self.m, self.k)


class SawTailPolicy(SawPolicy):
    """SAW-T: the same plug-in, minimising an approximate one-step tail risk.

    ``c`` is the ARL-calibrated tolerance radius ``c_beta``
    (``calibrate.c_beta``), i.e. the largest reference error whose conditional
    in-control ARL still retains a fraction ``beta`` of nominal.  It is derived
    from P7's closed response curve, not tuned.
    """

    def __init__(self, calib: SawCalibration, c: float, **kw) -> None:
        self.c = float(c)
        kw.setdefault("name", None)
        super().__init__(calib, **kw)
        if kw.get("name") is None:
            self.name = f"saw_t[{self.mode}](m={self.m},k={self.k},c={self.c:g})"

    def decide(self, obs: CycleObservation) -> Decision:
        zbar = obs.zbar(self.m)
        tau = obs.tau.astype(float)
        w = np.minimum(self.m, obs.tau).astype(float)
        c = self.calib
        g1 = 0.0 if self.mode == "no_tau" else c.g1
        mu = (c.g0 + g1 / np.sqrt(tau)) * zbar
        s = np.maximum(np.where(w < float(self.m), c.s1, c.s0), S_FLOOR)
        rho = _tail_optimal_rho(mu, s, self.nu, self.c)
        rho = np.minimum(rho, self.rho_max)
        return self._full(obs, rho, self.m, self.k)


# ---------------------------------------------------------------------------
# oracle ceiling for the SAW rule shape
# ---------------------------------------------------------------------------

class OracleSawPolicy(SawPolicy):
    """Z1: the same rule with the *realised* ``Rbar_j^2`` in place of ``V_hat``.

    This is the ceiling of the SAW information ladder: it answers "how much of
    SAW's shortfall is the plug-in, and how much is the rule shape?"  Reads F14.
    NEVER deployable.
    """

    policy_class = ORACLE

    def __init__(self, calib: SawCalibration, **kw) -> None:
        kw.setdefault("name", f"oracle_saw(m={calib.m},k={kw.get('k', calib.k)})")
        super().__init__(calib, **kw)

    def decide(self, obs: CycleObservation) -> Decision:
        if not isinstance(obs, OracleObservation):
            raise TypeError("OracleSawPolicy requires an OracleObservation")
        rbar = obs.e_current + obs.zbar(self.m)
        rho = _rho_from_v(rbar * rbar, self.nu, self.rho_max)
        return self._full(obs, rho, self.m, self.k)


class OracleTailSawPolicy(SawPolicy):
    """Z2: one-step tail oracle -- knows ``e_j``, minimises P(|e_{j+1}|>c|e_j)."""

    policy_class = ORACLE

    def __init__(self, calib: SawCalibration, c: float, **kw) -> None:
        self.c = float(c)
        kw.setdefault("name", f"oracle_saw_tail(m={calib.m},c={c:g})")
        super().__init__(calib, **kw)

    def decide(self, obs: CycleObservation) -> Decision:
        if not isinstance(obs, OracleObservation):
            raise TypeError("OracleTailSawPolicy requires an OracleObservation")
        rbar = obs.e_current + obs.zbar(self.m)
        # Rbar is known exactly, so the only randomness left is the fresh draw.
        rho = _tail_optimal_rho(rbar, np.zeros_like(rbar), self.nu, self.c)
        return self._full(obs, np.minimum(rho, self.rho_max), self.m, self.k)
