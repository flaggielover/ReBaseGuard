"""The three precommitted cost accountings for P6R.

The independent adjudication required that the original campaign's cost
language be repaired.  The PRIMARY metric is unchanged in definition and only
renamed, so the repaired numbers remain comparable with the original ones:

    fresh-sample ACQUISITION cost      C_acq(j)  = k_j * 1{rho_j < 1}

This counts **newly acquired observations per update**.  It is the operational
quantity: whenever any fresh baseline is used at all, ``k_j`` new observations
must be collected, and their number does not depend on the weight they are
subsequently given.

Two declared sensitivities, reported beside it and never replacing it:

    proportional fresh contribution    C_prop(j) = (1 - rho_j) * k_j
    quadratic / effective contribution C_quad(j) = (1 - rho_j)^2 * k_j

``C_prop`` weights the acquired sample by the linear weight the update gives it.
``C_quad`` weights it by the SQUARE of that weight, which is the share in which
the fresh term enters the update's second moment (the fresh component
contributes ``(1-rho)^2 / k`` to ``Var(e_{j+1} | .)``).  Neither is an
acquisition count and neither may be described as one.

**Permitted claim, and only this one, on the primary metric:** SAW-M and the
comparison fixed-``rho`` baseline require the *same number of newly acquired
fresh samples per update* under the frozen acquisition-cost definition,
whenever both use the same ``k`` and both keep ``rho < 1``.

**Forbidden unless the measured sensitivity actually supports it in the cell
being reported:** "SAW reuses more", "SAW is cheaper", "SAW has a lower
effective fresh contribution cost".  Against a TUNE-selected baseline these may
be false, and ``report_costs`` returns the signed comparison so that the
direction is read off the data rather than assumed.
"""
from __future__ import annotations

import numpy as np

ACQUISITION = "C_acq_fresh_acquisition_count"
PROPORTIONAL = "C_prop_proportional_fresh_contribution"
QUADRATIC = "C_quad_effective_squared_weight_contribution"

COST_LABELS = {
    ACQUISITION: "fresh-sample acquisition cost, k_j * 1{rho_j < 1} (PRIMARY)",
    PROPORTIONAL: "proportional fresh contribution, (1 - rho_j) * k_j (sensitivity)",
    QUADRATIC: "quadratic/effective fresh contribution, (1 - rho_j)^2 * k_j (sensitivity)",
}


def per_replicate_costs(res) -> dict:
    """All three cost accountings, per replicate, over post-burn-in cycles."""
    rho = res.post(res.rho)
    k = res.post(res.k).astype(float)
    return {
        ACQUISITION: (k * (rho < 1.0)).mean(axis=1),
        PROPORTIONAL: ((1.0 - rho) * k).mean(axis=1),
        QUADRATIC: ((1.0 - rho) ** 2 * k).mean(axis=1),
        "Wbar_mean_algebraic_reuse_weight": rho.mean(axis=1),
    }


def report_costs(method_res, control_res) -> dict:
    """Signed comparison on all three accountings, with the direction stated."""
    a = per_replicate_costs(method_res)
    b = per_replicate_costs(control_res)
    out = {}
    for key in (ACQUISITION, PROPORTIONAL, QUADRATIC,
                "Wbar_mean_algebraic_reuse_weight"):
        ma, mb = float(a[key].mean()), float(b[key].mean())
        diff = ma - mb
        out[key] = {
            "label": COST_LABELS.get(key, key),
            "method": ma, "control": mb, "difference": diff,
            "relative": (ma / mb - 1.0) if mb != 0 else float("nan"),
            "direction": ("identical" if abs(diff) < 1e-12
                          else "method_higher" if diff > 0 else "method_lower"),
        }
    return out
