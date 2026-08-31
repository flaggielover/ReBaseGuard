"""P7 analysis: turns the two result files into the reported evidence.

Deterministic given `results/response_curves.json`, `results/chain_sweep.json`
and `results/chain_sweep_arrays.npz`.  Emits `results/consequences.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7.analysis import (                                  # noqa: E402
    ResponseCurves, beta_r, bootstrap_ci, gamma_eff, gamma_eff_from_h, h_sup,
    load_curves, ratio_ci, verdict,
)
from rebaseguard_p7.config import (                                    # noqa: E402
    DETECTORS, M_GRID, RESULTS, SHIFTS, load_p3_boundaries,
)

BOUND_RADII = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35)


def repulsion_bound(cv: ResponseCurves, m: int, rho: float,
                    V: float, m4: float) -> dict | None:
    """Conditional P7-C/D Monte Carlo plug-in diagnostic.

    Write ``b(e) = -e h(e) >= 0`` (the selection bias always opposes the sign of
    the reference error).  Stationarity gives ``|ACF1| <= 1`` and
    ``ACF1 = -rho E[b(e)]/V``, hence ``E[b(e)] <= V/rho``.  With
    ``beta_r = inf_{0<|e|<=r} (-h(e)/e)`` we have ``b(e) >= beta_r e^2`` on
    ``|e| <= r`` and ``b >= 0`` everywhere, so

        V/rho >= beta_r (V - E[e^2; |e|>r])
        =>  E[e^2; |e|>r] / V  >=  1 - 1/(rho beta_r)              (mass escape)

    whenever ``rho beta_r > 1``.  That condition is exactly the P3 repulsion
    condition ``rho > rho_c`` in the limit ``r -> 0``, because
    ``beta_r -> GammaTilde - 1 = 1/rho_c``.  Cauchy-Schwarz on the same tail
    gives ``E[e^2; |e|>r] <= sqrt(E[e^4] P(|e|>r))``, so

        P(|e| > r)  >=  [ V (1 - 1/(rho beta_r)) ]^2 / E[e^4],

    and since ``A`` is even and non-increasing in ``|e|``,

        ARL_chain = E[A(e)] <= A(0) - (A(0) - A(r)) P(|e| > r).

    The algebra assumes stationarity, a global sign condition for ``h``, a
    finite fourth moment, and monotonicity of ``A``.  All numerical inputs are
    Monte Carlo point estimates without uncertainty propagation, so the result
    is not a certified bound.

    Returns the grid radius maximising the plug-in deficit, or ``None`` when
    no admissible radius exists.
    """
    if rho <= 0:
        return None
    A0 = float(cv.arl[0])
    best = None
    for r in BOUND_RADII:
        b_r = beta_r(cv, m, r)
        if rho * b_r <= 1.0:
            continue
        mass = 1.0 - 1.0 / (rho * b_r)
        p_lo = float(min((V * mass) ** 2 / m4, 1.0))
        Ar = float(cv.A(r))
        deficit = (A0 - Ar) * p_lo
        cand = {"r": r, "beta_r": b_r, "rho_beta_r": rho * b_r,
                "tail_second_moment_share_lower": mass,
                "plug_in_p_tail_lower": p_lo, "A_r": Ar,
                "plug_in_arl_upper_bound": A0 - deficit,
                "plug_in_relative_deficit": deficit / A0}
        if best is None or deficit > (A0 - best["plug_in_arl_upper_bound"]):
            best = cand
    return best


def main() -> None:
    cv = ResponseCurves(load_curves()["curves"]["cusum"], M_GRID)
    curves = {d: ResponseCurves(load_curves()["curves"][d], M_GRID)
              for d in DETECTORS}
    del cv
    sweep = json.loads((RESULTS / "chain_sweep.json").read_text())
    arrays = np.load(RESULTS / "chain_sweep_arrays.npz")
    boundaries = load_p3_boundaries()

    fresh = {(c["detector"], c["m"]): c for c in sweep["cells"] if c["rho"] == 0.0}
    out = {"cells": [], "curve_summary": {}}

    for d in DETECTORS:
        c = curves[d]
        c2, app = c.arl_curvature()
        out["curve_summary"][d] = {
            "A0": float(c.arl[0]), "A0_se": float(c.arl_se[0]),
            "arl_quadratic_c2": c2, "arl_second_derivative_at_0": app,
            "gamma_tilde_remeasured": c.gamma_tilde,
            "gamma_tilde_remeasured_se": c.gamma_tilde_se,
            "gamma_tilde_p3": {m: boundaries[(d, m)]["gamma_tilde"]
                               for m in M_GRID},
            "linearisation_radius": {m: c.linearisation_radius(m) for m in M_GRID},
            "g_sup": {m: c.g_sup(m) for m in M_GRID},
            "selection_bias_sup": {m: h_sup(c, m) for m in M_GRID},
            "beta_r": {m: {str(r): beta_r(c, m, r) for r in BOUND_RADII}
                       for m in M_GRID},
            "rho_c_from_beta": {m: 1.0 / beta_r(c, m, 0.05) for m in M_GRID},
            "A_at": {str(x): float(a) for x, a in zip(c.x, c.arl)},
        }

    for cell in sweep["cells"]:
        d, m, rho = cell["detector"], cell["m"], cell["rho"]
        c = curves[d]
        key = cell["array_key"]
        per_rep = arrays[f"{key}__per_rep_arl"]
        e = arrays[f"{key}__e_sample"].astype(float)
        A0 = float(c.arl[0])
        fr = fresh[(d, m)]
        fr_per_rep = arrays[f"{fr['array_key']}__per_rep_arl"]

        lo, hi = bootstrap_ci(per_rep)
        # distortion against the two controls
        rel_nom = cell["arl"] / A0 - 1.0
        rel_nom_ci = (lo / A0 - 1.0, hi / A0 - 1.0)
        rlo, rhi = ratio_ci(per_rep, fr["arl"], fr["arl_se"])
        rel_fresh = cell["arl"] / fr["arl"] - 1.0
        rel_fresh_ci = (rlo - 1.0, rhi - 1.0)

        ge = gamma_eff(c, m, e) if np.mean(e ** 2) > 0 else float("nan")
        ge_h = gamma_eff_from_h(c, m, e) if np.mean(e ** 2) > 0 else float("nan")
        acf_pred = rho * (1.0 - ge)

        delay = {}
        for D in SHIFTS:
            vals = c.A(e - D)
            ref = float(c.A(np.array([-D]))[0])
            delay[str(D)] = {
                "delay_chain": float(vals.mean()),
                "delay_nominal": ref,
                "relative": float(vals.mean() / ref - 1.0),
                "R_delta": float(vals.mean() / cell["arl"]),
                "out_of_grid_fraction": c.out_of_grid_fraction(e - D),
                # The entering reference was built before the shift. A blind
                # spot occurs when it happens to lie near the post-change mean.
                "p_blind_spot": float(np.mean(np.abs(e - D) < 0.2)),
                "p_delay_exceeds_half_nominal_arl":
                    float(np.mean(vals > 0.5 * float(c.arl[0]))),
                "delay_conditional_median_proxy":
                    float(np.median(vals)),
            }

        out["cells"].append({
            **{k: v for k, v in cell.items() if k != "e_sample"},
            "arl_boot_ci": [lo, hi],
            "arl_normal_ci": [cell["arl"] - 1.959963984540054 * cell["arl_se"],
                              cell["arl"] + 1.959963984540054 * cell["arl_se"]],
            "rel_vs_nominal": rel_nom,
            "rel_vs_nominal_ci": list(rel_nom_ci),
            "rel_vs_nominal_verdict": verdict(rel_nom, *rel_nom_ci),
            "rel_vs_fresh": rel_fresh,
            "rel_vs_fresh_ci": list(rel_fresh_ci),
            "rel_vs_fresh_verdict": verdict(rel_fresh, *rel_fresh_ci),
            "far_per_1000": 1000.0 / cell["arl"],
            "far_per_1000_nominal": 1000.0 / A0,
            "gamma_eff": ge,
            "gamma_eff_via_h": ge_h,
            "variance_floor_fresh": (1.0 - rho) ** 2 / m,
            "gamma_tilde_p3": cell["gamma_tilde_p3"],
            "acf1_predicted_from_gamma_eff": acf_pred,
            "acf1_measured": cell["e_acf1"],
            "acf1_predicted_from_p3_lambda": cell["lambda_p3"],
            "linearisation_radius": c.linearisation_radius(m),
            "ref_rms": float(np.sqrt(cell["ref_mse"])),
            "dispersion_over_lin_radius":
                float(np.sqrt(cell["ref_mse"]) / c.linearisation_radius(m))
                if c.linearisation_radius(m) > 0 else float("inf"),
            "e_out_of_grid_fraction": c.out_of_grid_fraction(e),
            "delay": delay,
            "repulsion_bound": repulsion_bound(c, m, rho, cell["ref_mse"],
                                               cell["ref_m4"]),
            "rb_arl_estimate": float(c.A(e).mean()),
        })

    (RESULTS / "consequences.json").write_text(json.dumps(out, indent=1))
    print("wrote", RESULTS / "consequences.json", len(out["cells"]), "cells")


if __name__ == "__main__":
    main()
