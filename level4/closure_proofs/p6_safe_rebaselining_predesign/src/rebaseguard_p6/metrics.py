"""Per-replicate metric definitions (SAFETY_OBJECTIVES.md section 3).

Every function returns one value *per replicate*: the replicate is the
statistical unit (STATISTICAL_DESIGN.md section 1), so all downstream inference
is ordinary iid inference across replicates.

Metrics are tagged by layer so that a report cannot silently gate on a
surrogate (SAFETY_OBJECTIVES.md section 5, FAILURE_MODE_REGISTER.md F2):

    LATENT      -- functionals of e; may be OPTIMISED, never gated on
    OBSERVABLE  -- monitoring metrics; must be MEASURED for any claim
    COST        -- what the operator pays
"""
from __future__ import annotations

import numpy as np

LATENT, OBSERVABLE, COST = "latent", "observable", "cost"

#: metric id -> layer.  Used by report builders to refuse a latent-layer gate.
METRIC_LAYER = {
    "Rms": LATENT, "M2": LATENT, "Mad": LATENT, "Q95e": LATENT,
    "Tail": LATENT, "OutCal": LATENT,
    "Arl0": OBSERVABLE, "Fap": OBSERVABLE, "Rate": OBSERVABLE,
    "Dmean": OBSERVABLE, "Dmed": OBSERVABLE, "Dq95": OBSERVABLE,
    "Dtail": OBSERVABLE, "Coll": OBSERVABLE,
    "Reuse": COST, "Fresh": COST, "FracReuse": COST, "Wbar": COST,
}


# -- observable layer -------------------------------------------------------

def arl0(res) -> np.ndarray:
    """Mean in-control cycle length per replicate."""
    return res.post(res.tau).mean(axis=1)


def fap(res, horizon: int = 100) -> np.ndarray:
    """Fraction of post-burn-in cycles alarming within ``horizon`` observations."""
    return (res.post(res.tau) <= horizon).mean(axis=1)


def rate_per_1000(res) -> np.ndarray:
    return 1000.0 / arl0(res)


def collapse_ratio(res) -> np.ndarray:
    """``tau_2 / tau_1``: the finite-cycle collapse of ledger row S8.

    Returned per replicate; the campaign reports the ratio of the means, which
    must be bootstrapped as a ratio (STATISTICAL_DESIGN.md section 3).
    """
    if res.tau.shape[1] < 2:
        raise ValueError("collapse_ratio needs at least 2 cycles")
    return res.tau[:, 1] / res.tau[:, 0]


def delay_stats(res, quantiles=(0.5, 0.95), tails=(50, 100)) -> dict:
    """Delay summaries for the shifted cycle of each replicate.

    ``res.shift_cycle`` must name the cycle into which the shift was injected.
    """
    if res.shift == 0.0 or res.shift_cycle < 0:
        raise ValueError("delay_stats requires a shifted run")
    d = res.tau[:, res.shift_cycle].astype(float)
    out = {"Dmean": d}
    for q in quantiles:
        out[f"Dq{int(q * 100)}"] = d          # per-replicate value; quantile is
        # taken across replicates by the analysis layer, not within one cycle.
    for L in tails:
        out[f"Dtail{L}"] = (d > L).astype(float)
    return out


# -- latent layer (surrogates; never a gate) --------------------------------

def reference_rms(res) -> np.ndarray:
    return np.sqrt((res.post(res.e_start) ** 2).mean(axis=1))


def reference_mad(res) -> np.ndarray:
    return np.abs(res.post(res.e_start)).mean(axis=1)


def reference_tail(res, c: float) -> np.ndarray:
    return (np.abs(res.post(res.e_start)) > c).mean(axis=1)


def out_of_calibration(res, c_beta: float) -> np.ndarray:
    """``P(|e| > c_beta)`` with ``c_beta`` the ARL-calibrated tolerance radius.

    ``c_beta`` must be derived from P7's response curves at campaign start
    (FULL_CAMPAIGN_ENTRY_GATE.md item 14); it is not a constant of this module.
    """
    return reference_tail(res, c_beta)


# -- cost layer -------------------------------------------------------------

def reused_per_alarm(res) -> np.ndarray:
    w = np.minimum(res.post(res.m), res.post(res.tau))
    return w.mean(axis=1)


def fresh_per_alarm(res) -> np.ndarray:
    """Fresh observations per alarm: ``k_j`` iff ``rho_j < 1`` (design H5)."""
    paid = res.post(res.k) * (res.post(res.rho) < 1.0)
    return paid.mean(axis=1)


def frac_reuse(res) -> np.ndarray:
    w = np.minimum(res.post(res.m), res.post(res.tau))
    paid = res.post(res.k) * (res.post(res.rho) < 1.0)
    return (w / (w + paid)).mean(axis=1)


def mean_weight(res) -> np.ndarray:
    """Mean algebraic reuse weight.  Reporting only -- it is not a cost."""
    return res.post(res.rho).mean(axis=1)
