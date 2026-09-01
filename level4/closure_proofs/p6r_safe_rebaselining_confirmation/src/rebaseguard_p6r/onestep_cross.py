"""The DECLARED cross-chain one-step statistic — added after Checkpoint A.

Recorded deviation, stated up front.  ``REPAIRED_PROTOCOL.md`` section 9 (frozen
at Checkpoint A ``fcc1355``) declared that the one-step gain would be reported
twice: on the SAW-M chain's cycles and on the ``FIXED_TUNE`` chain's cycles,
"because the two chains induce different entering laws and neither is
privileged".  The Checkpoint-A implementation
(``onestep.one_step_risk_gain`` applied to the control arm) computes something
different and weaker: the **control's own** gain over the best constant weight,
which is zero by construction for a constant policy and therefore only
calibrates the statistic.

This module computes the quantity that was actually declared: SAW-M's decision
rule applied to the **baseline chain's** cycles, so both risks are evaluated
under the baseline's entering law.  The formula is unchanged from the
declaration; only the code is new, and it is new *after* the anchor.  Nothing
here is selected or tuned — the policy, its four constants and the formula were
all fixed before the anchor.
"""
from __future__ import annotations

import numpy as np

from .onestep import one_step_risk_gain
from .stats_r import ALPHA, N_BOOT


def saw_rho_on(res, calib, k: int, rho_max: float = 0.95,
               s_floor: float = 1e-2) -> np.ndarray:
    """The weight SAW-M *would* have chosen, from a chain's own observables.

    Uses only ``tau``, ``zbar`` and ``w = min(m, tau)`` — the audited observable
    set — so it is exactly the deployed rule, evaluated counterfactually.
    """
    tau = res.post(res.tau).astype(float)
    zbar = res.post(res.zbar)
    m = res.post(res.m).astype(float)
    w = np.minimum(m, tau)
    mu = (calib.g0 + calib.g1 / np.sqrt(tau)) * zbar
    s = np.maximum(np.where(w < m, calib.s1, calib.s0), s_floor)
    v = mu * mu + s
    nu = 1.0 / float(k)
    return np.minimum(nu / (v + nu), rho_max)


def cross_chain_sums(res, calib, k: int) -> dict:
    """Per-replicate sums for SAW-M's rule applied to ``res``'s cycles."""
    nu = 1.0 / float(k)
    u2 = (res.post(res.e_start) + res.post(res.zbar)) ** 2
    rho = saw_rho_on(res, calib, k)
    risk = rho ** 2 * u2 + (1.0 - rho) ** 2 * nu
    return {"s_u2": u2.sum(axis=1), "s_risk": risk.sum(axis=1),
            "n_cyc": np.full(u2.shape[0], u2.shape[1], float), "nu": nu,
            "rho_mean": float(rho.mean())}


def cross_chain_gain(res, calib, k: int, *, seed: int = 0,
                     n_boot: int = N_BOOT, alpha: float = ALPHA) -> dict:
    """``G`` for SAW-M's rule on another policy's chain, with a cluster BCa CI."""
    sums = cross_chain_sums(res, calib, k)
    out = one_step_risk_gain(sums, seed=seed, n_boot=n_boot, alpha=alpha)
    out["rho_mean_counterfactual"] = sums["rho_mean"]
    out["note"] = ("SAW-M's rule evaluated on the cycles of a DIFFERENT policy's "
                   "chain; both risks share that chain's entering law.")
    return out
