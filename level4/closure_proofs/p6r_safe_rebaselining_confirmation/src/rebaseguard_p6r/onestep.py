"""Direct realized one-step risk -- the repaired Jensen evidence.

The independent adjudication accepted T6-C only under narrower assumptions, and
separately observed that the original campaign's empirical Jensen diagnostic was
``sigma(V_hat)``-restricted: the reference conditional second moment was
estimated by binning on the plug-in itself, so it measured the plug-in's
*calibration* rather than the achievable gap.

This module implements the stronger, direct statistic, **precommitted here
before execution**.  It uses the realized raw terminal-window mean ``U`` and no
binning, no conditional-expectation estimate and no plug-in reference at all.

Definition (fixed ``k``, hence fixed ``nu = 1/k``).  On the post-burn-in cycles
of one chain, with ``U_{r,j} = e_{r,j} + zbar_{r,j}`` the realized raw window
mean (exact, by T1) and ``rho_hat_{r,j}`` the weight the policy actually chose:

```text
    M2       = mean_{r,j} [ U^2 ]                          (realized second moment)
    R_const(rho0) = rho0^2 M2 + (1-rho0)^2 nu              (any CONSTANT weight)
    R_star   = min_{rho0} R_const = nu M2 / (M2 + nu)      at rho0* = nu/(M2+nu)
    R_adapt  = mean_{r,j} [ rho_hat^2 U^2 + (1-rho_hat)^2 nu ]
    G        = 1 - R_adapt / R_star                        (the realized gain)
```

Both risks are evaluated on the **same cycles**, i.e. under a common entering
law, which is exactly the setting in which the fixed-``k`` T6-C statement is
exact.  ``R_star`` is the *best constant weight on this very sample*, so the
comparison is against the strongest constant-policy opponent available, not
against a grid member.

Two statements this does NOT make, and which must not be inferred from it:

* ``R_adapt`` uses the **plug-in** ``rho_hat``.  It is therefore an upper bound
  on the risk of the ``F``-measurable optimizer, and ``G`` is a **lower bound**
  on the achievable adaptive gap.  The plug-in is not claimed to be the oracle
  ``F``-measurable optimizer.
* ``G`` is a one-step, latent-layer quantity.  No monitoring consequence follows
  from it; the monitoring metrics are measured separately.

Uncertainty: the resampling unit is the **replicate cluster**, because cycles
within a replicate are dependent.  Each replicate contributes its cycle sums.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm

from .stats_r import ALPHA, N_BOOT, _bca_from_parts, _boot_indices


def per_replicate_sums(res, *, nu: float) -> dict:
    """Per-replicate cycle sums for the one-step risk statistic.

    ``res`` is a ``rebaseguard_p6c.chain.PolicyChainResult``.  Only post-burn-in
    cycles are used.  ``U = e_start + zbar`` is exact by the raw-mean identity.
    """
    e = res.post(res.e_start)
    zb = res.post(res.zbar)
    rho = res.post(res.rho)
    u2 = (e + zb) ** 2
    risk = rho ** 2 * u2 + (1.0 - rho) ** 2 * nu
    return {"s_u2": u2.sum(axis=1), "s_risk": risk.sum(axis=1),
            "n_cyc": np.full(u2.shape[0], u2.shape[1], float),
            "nu": float(nu)}


def _gain_from_sums(s_u2, s_risk, n_cyc, nu):
    m2 = s_u2.sum(axis=-1) / n_cyc.sum(axis=-1)
    r_adapt = s_risk.sum(axis=-1) / n_cyc.sum(axis=-1)
    r_star = nu * m2 / (m2 + nu)
    return 1.0 - r_adapt / r_star, m2, r_adapt, r_star


def one_step_risk_gain(sums: dict, *, seed: int = 0, n_boot: int = N_BOOT,
                       alpha: float = ALPHA) -> dict:
    """``G = 1 - R_adapt/R_star`` with a replicate-cluster BCa interval."""
    s_u2 = np.asarray(sums["s_u2"], float)
    s_risk = np.asarray(sums["s_risk"], float)
    n_cyc = np.asarray(sums["n_cyc"], float)
    nu = float(sums["nu"])
    n = s_u2.size

    g_hat, m2, r_adapt, r_star = _gain_from_sums(s_u2, s_risk, n_cyc, nu)
    g_hat = float(g_hat)

    rng = np.random.default_rng(seed)
    parts = []
    for idx in _boot_indices(rng, n, n_boot):
        g, *_ = _gain_from_sums(s_u2[idx], s_risk[idx], n_cyc[idx], nu)
        parts.append(g)
    boot = np.concatenate(parts)

    tot_u2, tot_risk, tot_n = s_u2.sum(), s_risk.sum(), n_cyc.sum()
    j_m2 = (tot_u2 - s_u2) / (tot_n - n_cyc)
    j_ad = (tot_risk - s_risk) / (tot_n - n_cyc)
    jack = 1.0 - j_ad / (nu * j_m2 / (j_m2 + nu))

    lo, hi, z0, accel = _bca_from_parts(g_hat, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    rho_star_const = float(nu / (float(m2) + nu))
    return {
        "G": g_hat, "bca_lo": lo, "bca_hi": hi,
        "normal_lo": g_hat - z * sd, "normal_hi": g_hat + z * sd,
        "boot_sd": sd, "n_clusters": int(n), "n_cycles": int(tot_n),
        "n_boot": int(boot.size), "z0": z0, "accel": accel,
        "M2_realized": float(m2), "nu": nu,
        "R_star": float(r_star), "R_adapt": float(r_adapt),
        "rho_star_constant_on_this_sample": rho_star_const,
        "resolved": bool(lo > 0.0 or hi < 0.0),
    }


def constant_policy_risk_curve(sums: dict, rho_grid) -> dict:
    """``R_const(rho0)`` over a grid -- the curve the adaptive risk is beaten against."""
    m2 = float(np.asarray(sums["s_u2"]).sum() / np.asarray(sums["n_cyc"]).sum())
    nu = float(sums["nu"])
    g = np.asarray(rho_grid, float)
    return {"rho": g.tolist(),
            "R_const": (g ** 2 * m2 + (1.0 - g) ** 2 * nu).tolist(),
            "M2": m2, "nu": nu}
