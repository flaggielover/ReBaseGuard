"""Design-time calibration for the selection-aware weighting (SAW) family.

Two independent objects live here.

**1. The ARL-calibrated tolerance radius** ``c_beta`` of
``SAFETY_OBJECTIVES.md`` section 3.1, re-derived from P7's *closed* response
curves (`S2`) rather than quoted from the pre-design's indicative values.

**2. The SAW plug-in calibration.**  The policy needs an estimate of

    V_j := E[ Rbar_j^2 | F_j ] ,      Rbar_j = e_j + zbar_j ,

where ``F_j`` is the observable sigma-field at the alarm (F01-F13).  ``Rbar_j``
is latent, so ``V_j`` cannot be evaluated online; but it is a *functional of the
frozen model*, so it can be estimated **offline, at design time**, exactly like
the ``A(.)`` / ``P(tau|e)`` tables that ``OBSERVABILITY_AUDIT.md`` F21 declares
legal.  Nothing about that estimation enters the deployed policy except four
scalars.

Functional form (fixed before any campaign data; see ``METHOD.md`` section 4):

    mu_hat(F) = ( g0 + g1 / sqrt(tau) ) * zbar             (conditional mean)
    s_hat(F)  = max( s_long  if w == m  else  s_short , s_floor )
    V_hat     = mu_hat^2 + s_hat

Oddness of the frozen model in ``e`` (T3) forces ``E[Rbar | F]`` to be an odd
function of the readout, so a linear-through-origin model is the natural
first-order form; the ``1/sqrt(tau)`` interaction is kept because the stopping
geometry carries real gain information (a short cycle is one large observation,
a long cycle is an accumulation).  A cubic term was measured and discarded
(it reduced the residual variance by under 2%).

The conditional variance is split by the *truncation indicator* ``w < m``
rather than modelled as ``s0 + s1/w``.  Truncated cycles are rare (0.02%-5% of
cycles over the design grid) but their residual variance is 30x-70x the
untruncated one, not the ``m/w`` factor a naive averaging argument predicts, so
a smooth ``1/w`` model both extrapolates badly and is ill-conditioned when
``w`` is nearly constant.  Two group means are exact, stable and need no
extrapolation.

The four scalars are obtained by **ordinary least squares**, not by search: the
policy has no tuned hyperparameter beyond the design choice ``(m, k)``.
Because the law of ``e`` depends on the policy, calibration is run to a **fixed
point**: calibrate under the current policy, rebuild the policy, repeat.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

_P7_RESULTS = (Path(__file__).resolve().parents[3]
               / "p7_statistical_consequences" / "results")

#: Lower clamp on the estimated conditional variance.  Structural, not tuned:
#: it keeps ``V_hat`` strictly positive so ``rho < 1`` strictly, which is a
#: hypothesis of THEORY.md T6-B.
S_FLOOR = 1e-2

#: Structural cap on the reuse weight, required by T6-B's minorisation.  It is
#: not a tuning knob: the calibrated ``V_hat`` keeps ``rho`` well below it in
#: every measured cell (the cap is reported as non-binding in RESULTS.md).
RHO_MAX = 0.95


# ---------------------------------------------------------------------------
# 1. the ARL-calibrated tolerance radius
# ---------------------------------------------------------------------------

def response_curve(detector: str) -> tuple[np.ndarray, np.ndarray]:
    """``(|x|, A(|x|))`` from P7's frozen response curves (ledger S2)."""
    d = json.loads((_P7_RESULTS / "response_curves.json").read_text())
    rows = d["curves"][detector]
    # The published grid carries a few negative ``x`` entries as symmetry
    # checks; ``A`` is even (S2), so the curve is taken on ``x >= 0`` only.
    x = np.array([r["x"] for r in rows], float)
    a = np.array([r["arl"] for r in rows], float)
    keep = x >= 0.0
    x, a = x[keep], a[keep]
    o = np.argsort(x)
    return x[o], a[o]


def c_beta(detector: str, beta: float) -> dict:
    """``sup{ c >= 0 : A(c) >= beta A(0) }`` with a linear-interpolation budget.

    The measured curve is monotone decreasing on the grid; the radius is found
    by linear interpolation between the two bracketing grid points, and the
    error budget reported is the full width of that bracket -- an honest upper
    bound on the interpolation error, since ``A`` is monotone there.
    """
    x, a = response_curve(detector)
    target = beta * a[0]
    below = np.flatnonzero(a < target)
    if below.size == 0:
        return {"beta": beta, "c": float(x[-1]), "bracket": 0.0,
                "note": "curve never falls below the target on the measured grid"}
    i = int(below[0])
    if i == 0:
        return {"beta": beta, "c": 0.0, "bracket": 0.0, "note": "target above A(0)"}
    x0, x1, a0, a1 = x[i - 1], x[i], a[i - 1], a[i]
    c = x0 + (a0 - target) * (x1 - x0) / (a0 - a1)
    return {"beta": float(beta), "c": float(c), "bracket": float(x1 - x0),
            "a_lo": float(a1), "a_hi": float(a0), "a0": float(a[0])}


# ---------------------------------------------------------------------------
# 2. the SAW plug-in calibration
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SawCalibration:
    """Four scalars plus the provenance needed to replay their derivation."""
    detector: str
    m: int
    k: int
    g0: float
    g1: float
    s0: float          # E[resid^2 | w == m]   (untruncated window)
    s1: float          # E[resid^2 | w <  m]   (truncated window)
    n_obs: int
    iterations: int
    converged: bool
    seed_family: str
    resid_var: float          # Var(Rbar - mu_hat), diagnostic
    r2: float                 # 1 - resid_var / Var(Rbar), diagnostic

    def features(self, zbar, tau, w):
        """``(mu_hat, s_hat)`` from observables only."""
        zbar = np.asarray(zbar, float)
        tau = np.asarray(tau, float)
        w = np.asarray(w, float)
        mu = (self.g0 + self.g1 / np.sqrt(tau)) * zbar
        s = np.maximum(np.where(w < float(self.m), self.s1, self.s0), S_FLOOR)
        return mu, s

    def v_hat(self, zbar, tau, w):
        mu, s = self.features(zbar, tau, w)
        return mu * mu + s

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "SawCalibration":
        return SawCalibration(**{k: d[k] for k in SawCalibration.__slots__})


def fit_from_samples(*, zbar, tau, w, rbar, detector, m, k, seed_family,
                     iterations=0, converged=False, use_tau_feature=True,
                     ) -> SawCalibration:
    """Least-squares fit of the four scalars from one calibration sample."""
    zbar = np.asarray(zbar, float).ravel()
    tau = np.asarray(tau, float).ravel()
    w = np.asarray(w, float).ravel()
    rbar = np.asarray(rbar, float).ravel()

    cols = [zbar] + ([zbar / np.sqrt(tau)] if use_tau_feature else [])
    X = np.column_stack(cols)
    coef, *_ = np.linalg.lstsq(X, rbar, rcond=None)
    g0 = float(coef[0])
    g1 = float(coef[1]) if use_tau_feature else 0.0
    resid = rbar - X @ coef

    y = resid ** 2
    trunc = w < float(m)
    s0 = float(y[~trunc].mean()) if (~trunc).any() else float(y.mean())
    s1 = float(y[trunc].mean()) if trunc.any() else s0

    var_r = float(rbar.var())
    rv = float(resid.var())
    return SawCalibration(
        detector=detector, m=int(m), k=int(k), g0=g0, g1=g1, s0=s0, s1=s1,
        n_obs=int(zbar.size), iterations=int(iterations), converged=bool(converged),
        seed_family=seed_family, resid_var=rv,
        r2=float(1.0 - rv / var_r) if var_r > 0 else float("nan"),
    )
