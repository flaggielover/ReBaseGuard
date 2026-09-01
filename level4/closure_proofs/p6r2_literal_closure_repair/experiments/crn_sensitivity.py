"""Corrected CRN / fixed-path calibration sensitivity (G9).

Replaces the CONFOUNDED P6R artifact, in which the variants used different
``policy_id`` values and therefore different RNG streams.  Here every variant is
applied to the **identical stochastic paths**: the innovations of cycle ``j`` of
replicate ``r`` are seeded by ``(cell, j)`` alone, never by the policy.

SAW-M is **not** recalibrated and **no shipped constant changes**.  The declared
variants perturb only ``s1``:  ``s1 x 0.5``, ``s1 x 2.0``, ``s1 := s0``.

This artifact does **not** claim to prove calibration convergence.  The
convergence facts are carried forward from the frozen P6R audit unchanged and
are not reinterpreted.

    python experiments/crn_sensitivity.py
"""
from __future__ import annotations

import json
import time

import numpy as np

import _p6r2_paths as P                                              # noqa: F401
from _p6r2_paths import P6R, RESULTS

from rebaseguard_p6r2.fixedpath import (DEFAULT_TAPE_LEN,            # noqa: E402
                                        saw_decider, simulate_fixed_path)

N_REP, N_CYCLES, BURN_IN = 1500, 60, 15
VARIANTS = ("baseline", "s1_x0.5", "s1_x2.0", "s1_eq_s0")


def variant_s1(name: str, s0: float, s1: float) -> float:
    return {"baseline": s1, "s1_x0.5": 0.5 * s1, "s1_x2.0": 2.0 * s1,
            "s1_eq_s0": s0}[name]


def main():
    t0 = time.time()
    aud = json.loads((P6R / "precommit" / "calibration_audit.json").read_text())
    out = {
        "artifact": "CORRECTED_CRN_FIXED_PATH_CALIBRATION_SENSITIVITY",
        "replaces": ("p6r_safe_rebaselining_confirmation/precommit/"
                     "s1_sensitivity.json, which was CONFOUNDED: its variants "
                     "used different policy_id values and therefore different "
                     "RNG streams"),
        "method": ("every variant is applied to IDENTICAL stochastic paths. The "
                   "innovations of cycle j of replicate r are seeded by (cell, j) "
                   "alone -- never by the policy -- so the only thing that can "
                   "differ between variants is the reuse weight the perturbed "
                   "constant produces."),
        "does_not_claim": ("This artifact does NOT prove calibration convergence. "
                           "It answers only: given the frozen shipped policy "
                           "constants and identical stochastic paths, how much do "
                           "aggregate outcomes move under the declared s1 "
                           "perturbations?"),
        "saw_m_recalibrated": False,
        "shipped_constants_changed": False,
        "n_rep": N_REP, "n_cycles": N_CYCLES, "burn_in": BURN_IN,
        "tape_len": DEFAULT_TAPE_LEN, "variants": list(VARIANTS),
        "cells": {},
    }

    for key, c in aud["cells"].items():
        det, m, k = c["detector"], int(c["m"]), int(c["k"])
        rows, paths = {}, {}
        for v in VARIANTS:
            s1 = variant_s1(v, c["s0"], c["s1"])
            res = simulate_fixed_path(
                detector=det,
                decide=saw_decider(c["g0"], c["g1"], c["s0"], s1, m, k),
                m=m, k=k, n_rep=N_REP, n_cycles=N_CYCLES, burn_in=BURN_IN,
                cell_tag=key)
            rows[v] = {"s1_used": float(s1), "rho_mean": res["rho_mean"],
                       "rms": res["rms"], "arl0": res["arl0"],
                       "n_overflow_draws": res["n_overflow_draws"]}
            # the first cycle's entering state is e0 = 0 for every variant, so
            # cycle-0 innovations are a direct path-identity check
            paths[v] = res["zbar"][:, 0].copy()
        base = rows["baseline"]
        ident = {v: bool(np.array_equal(paths[v], paths["baseline"]))
                 for v in VARIANTS}
        out["cells"][key] = {
            "detector": det, "m": m, "k": k,
            "shipped": {kk: c[kk] for kk in ("g0", "g1", "s0", "s1")},
            "variants": rows,
            "absolute_change_vs_baseline": {
                v: {"rho_mean": rows[v]["rho_mean"] - base["rho_mean"],
                    "rms": rows[v]["rms"] - base["rms"],
                    "arl0": rows[v]["arl0"] - base["arl0"]} for v in VARIANTS},
            "relative_change_vs_baseline": {
                v: {"rho_mean": rows[v]["rho_mean"] / base["rho_mean"] - 1.0,
                    "rms": rows[v]["rms"] / base["rms"] - 1.0,
                    "arl0": rows[v]["arl0"] / base["arl0"] - 1.0} for v in VARIANTS},
            "max_abs_relative_change": {
                mm: max(abs(rows[v][mm] / base[mm] - 1.0) for v in VARIANTS)
                for mm in ("rho_mean", "rms", "arl0")},
            "cycle0_innovation_paths_identical_across_variants": ident,
            # carried forward from the frozen audit, unchanged, not reinterpreted
            "calibration_facts_carried_forward": {
                "converged": c["converged"],
                "iterations_reached": c["iterations_reached"],
                "n_obs_behind_s1": c["n_obs_behind_s1"],
                "s1_is_fallback_equal_to_s0": c["s1_is_fallback_equal_to_s0"],
                "s1_sparse": c["s1_sparse"],
                "frac_truncated_windows_tau_lt_m": c["frac_truncated_windows"],
                "n_truncated_window_events_tau_lt_m": c["n_obs_behind_s1"],
                "variance_floor_1e-2_active": c["variance_floor_1e-2_active"],
                "rho_max_can_bind": c["rho_max_can_bind"],
                "final_refit_followed_by_another_fixed_point_update":
                    c["final_refit_followed_by_another_fixed_point_update"],
                "drift_fixed_point_to_final": c["drift_fixed_point_to_final"],
            },
        }
        print(f"CRN {key}: rho_mean {base['rho_mean']:.4f} | max|rel| "
              f"rho {100*out['cells'][key]['max_abs_relative_change']['rho_mean']:.3f}% "
              f"rms {100*out['cells'][key]['max_abs_relative_change']['rms']:.3f}% "
              f"arl0 {100*out['cells'][key]['max_abs_relative_change']['arl0']:.3f}% "
              f"| paths identical {all(ident.values())} "
              f"[{time.time()-t0:.0f}s]", flush=True)

    s = aud["summary"]
    out["calibration_summary_carried_forward"] = {
        "n_cells": s["n_cells"], "n_converged": s["n_converged"],
        "all_converged": s["all_converged"],
        "non_converged_cells": s["non_converged_cells"],
        "s1_sparse_cells": s["s1_sparse_cells"],
        "s1_fallback_cells": s["s1_fallback_cells"],
        "variance_floor_active_anywhere": s["variance_floor_active_anywhere"],
        "rho_max_can_bind_anywhere": s["rho_max_can_bind_anywhere"],
        "final_refit_is_a_verified_fixed_point":
            s["final_refit_is_a_verified_fixed_point"],
        "note": s["note"],
    }
    out["all_paths_identical_across_variants"] = all(
        all(v["cycle0_innovation_paths_identical_across_variants"].values())
        for v in out["cells"].values())
    out["seconds"] = time.time() - t0
    (RESULTS / "p6r2_crn_fixed_path_calibration_sensitivity.json").write_text(
        json.dumps(out, indent=1, allow_nan=False))
    print(f"wrote p6r2_crn_fixed_path_calibration_sensitivity.json "
          f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
