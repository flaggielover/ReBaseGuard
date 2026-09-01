"""Cell execution, calibration fixed point, and the per-replicate record schema.

Every number the campaign reports is produced here, from a ``PolicyChainResult``
and nothing else, so that a result row can always be traced to one deterministic
``(family, detector, m, policy_id, cell_tag, block)`` stream.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import metrics as M
from .calibrate import SawCalibration, fit_from_samples
from .chain import simulate_policy_chain
from .policy import ConstantPolicy
from .saw import SawPolicy
from .seeds import generator

#: Preregistered reference-tail radii (SAFETY_OBJECTIVES.md section 3.1).
TAIL_RADII = (0.2, 0.5, 1.0)
#: Preregistered FAP horizons and delay-tail thresholds.
FAP_HORIZONS = (50, 100)
DELAY_TAILS = (50, 100)


# ---------------------------------------------------------------------------
# calibration fixed point
# ---------------------------------------------------------------------------

def _collect(res, m):
    """Post-burn-in observable/latent calibration sample from a chain run."""
    e = res.post(res.e_start).ravel()
    zbar = res.post(res.zbar).ravel()
    tau = res.post(res.tau).ravel().astype(float)
    w = np.minimum(res.post(res.m), res.post(res.tau)).ravel().astype(float)
    return zbar, tau, w, e + zbar


def calibrate_saw(*, detector: str, m: int, k: int, family: str = "tune",
                  n_rep: int = 400, n_cycles: int = 250, burn_in: int = 25,
                  rho_init: float = 0.2, max_iter: int = 8, tol: float = 1e-3,
                  cell_tag: str = "calib") -> dict:
    """Fixed-point calibration of the SAW plug-in on the ``family`` seed stream.

    Returns the converged ``SawCalibration``, the separately-fitted no-tau
    coefficient, and ``v_bar`` (needed by the ``flat`` sensor ablation, which is
    exactly a fixed-rho policy).
    """
    policy = ConstantPolicy(rho=rho_init, m=m, k=k)
    calib = None
    trace = []
    converged = False
    for it in range(max_iter):
        rng = generator(family=family, detector=detector, m=m,
                        policy_id="calib", cell_tag=cell_tag)
        res = simulate_policy_chain(detector=detector, policy=policy, n_rep=n_rep,
                                    n_cycles=n_cycles, burn_in=burn_in, e0=0.0,
                                    rng=rng)
        zbar, tau, w, rbar = _collect(res, m)
        new = fit_from_samples(zbar=zbar, tau=tau, w=w, rbar=rbar,
                               detector=detector, m=m, k=k, seed_family=family,
                               iterations=it + 1)
        trace.append([new.g0, new.g1, new.s0, new.s1])
        if calib is not None:
            # Convergence is judged on (g0, g1, s0) only: ``s1`` is the residual
            # variance on truncated windows, a group mean over well under 1% of
            # cycles, so it is dominated by Monte Carlo noise and would prevent
            # the map from ever reporting a fixed point.  Common random numbers
            # across iterations make the map deterministic.
            delta = max(abs(new.g0 - calib.g0), abs(new.g1 - calib.g1),
                        abs(new.s0 - calib.s0))
            if delta < tol:
                calib = new
                converged = True
                break
        calib = new
        policy = SawPolicy(calib, k=k, mode="full")

    calib = SawCalibration(**{**calib.to_dict(), "converged": converged})

    # one more run under the converged policy, for the ablation constants
    rng = generator(family=family, detector=detector, m=m,
                    policy_id="calib_final", cell_tag=cell_tag)
    res = simulate_policy_chain(detector=detector,
                                policy=SawPolicy(calib, k=k, mode="full"),
                                n_rep=n_rep, n_cycles=n_cycles, burn_in=burn_in,
                                e0=0.0, rng=rng)
    zbar, tau, w, rbar = _collect(res, m)
    no_tau = fit_from_samples(zbar=zbar, tau=tau, w=w, rbar=rbar,
                              detector=detector, m=m, k=k, seed_family=family,
                              use_tau_feature=False)
    v = calib.v_hat(zbar, tau, w)
    nu = 1.0 / k
    v_bar = float(v.mean())
    # the exact one-step Jensen gap on this sample (THEORY.md T6-C)
    q_star = nu * v / (v + nu)
    jensen = float(nu * v_bar / (v_bar + nu) - q_star.mean())
    return {
        "calib": calib,
        "g0_no_tau": no_tau.g0,
        "s0_no_tau": no_tau.s0,
        "s1_no_tau": no_tau.s1,
        "v_bar": v_bar,
        "v_sd": float(v.std()),
        "jensen_gap": jensen,
        "jensen_gap_rel": float(jensen / (nu * v_bar / (v_bar + nu))),
        "rho_flat": float(nu / (v_bar + nu)),
        "trace": trace,
        "n_calib": int(zbar.size),
    }


# ---------------------------------------------------------------------------
# cell execution
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Cell:
    detector: str
    m: int
    policy_id: str
    policy_class: str
    family: str
    n_rep: int
    n_cycles: int
    burn_in: int
    shift: float
    shift_cycle: int
    e0: float | None
    m0: int


def run_incontrol(*, policy, detector, m, family, n_rep, n_cycles, burn_in,
                  e0=0.0, m0=5, cell_tag="ic", c_beta=None, block=0,
                  pair_tag=None):
    """One in-control cell.  Returns per-replicate metric arrays plus scalars.

    ``pair_tag`` makes every policy in a comparison consume the *same* seed
    stream, so per-replicate differences are paired (STATISTICAL_DESIGN.md
    section 2).  In this chain that is seed alignment, not path coupling: the
    realised pair correlation is measured and reported, never assumed.
    """
    rng = generator(family=family, detector=detector, m=m,
                    policy_id=pair_tag or policy.name, cell_tag=cell_tag,
                    block=block)
    res = simulate_policy_chain(detector=detector, policy=policy, n_rep=n_rep,
                                n_cycles=n_cycles, burn_in=burn_in, e0=e0, m0=m0,
                                rng=rng)
    out = {
        "Arl0": M.arl0(res),
        "Rms": M.reference_rms(res),
        "Mad": M.reference_mad(res),
        "Wbar": M.mean_weight(res),
        "Reuse": M.reused_per_alarm(res),
        "Fresh": M.fresh_per_alarm(res),
        "FracReuse": M.frac_reuse(res),
        "FreshProp": M.fresh_proportional(res),
    }
    for h in FAP_HORIZONS:
        out[f"Fap{h}"] = M.fap(res, h)
    for c in TAIL_RADII:
        out[f"Tail{c}"] = M.reference_tail(res, c)
    out["Q95e"] = np.quantile(np.abs(res.post(res.e_start)), 0.95, axis=1)
    if c_beta is not None:
        for beta, cb in c_beta.items():
            out[f"OutCal{beta}"] = M.reference_tail(res, cb)
    out["Eff"] = out["Fresh"] / np.maximum(out["Arl0"], 1e-12)
    return out, res


def run_delay(*, policy, detector, m, family, n_rep, shift, shift_cycle,
              e0=0.0, m0=5, cell_tag="oc", block=0, pair_tag=None):
    """One out-of-control cell: one delay observation per replicate."""
    rng = generator(family=family, detector=detector, m=m,
                    policy_id=pair_tag or policy.name,
                    cell_tag=f"{cell_tag}_d{shift}", block=block)
    res = simulate_policy_chain(detector=detector, policy=policy, n_rep=n_rep,
                                n_cycles=shift_cycle + 1, burn_in=shift_cycle,
                                e0=e0, m0=m0, shift=shift, shift_cycle=shift_cycle,
                                rng=rng)
    delay = res.tau[:, shift_cycle].astype(float)
    e_entering = res.e_start[:, shift_cycle]
    return {"delay": delay, "e_entering": e_entering}, res


def run_finite_cycle(*, policy, detector, m, family, n_rep, n_cycles=50,
                     e0=0.0, m0=5, cell_tag="r3", block=0, pair_tag=None):
    """R1/R2/R3: finite-cycle regimes from ``e_0``, no burn-in."""
    rng = generator(family=family, detector=detector, m=m,
                    policy_id=pair_tag or policy.name, cell_tag=cell_tag,
                    block=block)
    res = simulate_policy_chain(detector=detector, policy=policy, n_rep=n_rep,
                                n_cycles=n_cycles, burn_in=0, e0=e0, m0=m0,
                                rng=rng)
    return {
        "tau_by_cycle": res.tau.mean(axis=0),
        "rms_by_cycle": np.sqrt((res.e_start ** 2).mean(axis=0)),
        "coll": M.collapse_ratio(res),
        "tau1": res.tau[:, 0].astype(float),
        "tau2": res.tau[:, 1].astype(float),
    }, res
