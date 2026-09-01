"""Corrected Gate-9 calibration sensitivity under addressable primitive CRN.

Reruns ONLY the Gate-9 sensitivity.  No recalibration, no TUNE, no primary EVAL,
no REPLAY, no replication, no delta scope, no finite-reference run, no change to
the main statistical analysis.

Produces:
    results/p6r2b_crn_identity.json      direct primitive-identity evidence
    results/p6r2b_crn_sensitivity.json   the corrected 8-cell sensitivity
"""
from __future__ import annotations

import json
import time

import numpy as np

import _p6r2b_paths as P                                            # noqa: F401
from _p6r2b_paths import P6R, RESULTS

from rebaseguard_p6r2b import primitives as PR                      # noqa: E402
from rebaseguard_p6r2b.simulate import (LADDER, saw_decider,        # noqa: E402
                                        simulate)

N_REP, N_CYCLES, BURN_IN = 1500, 60, 15          # unchanged from P6R2
VARIANTS = ("baseline", "s1_x0.5", "s1_x2.0", "s1_eq_s0")


def variant_s1(name, s0, s1):
    return {"baseline": s1, "s1_x0.5": 0.5 * s1, "s1_x2.0": 2.0 * s1,
            "s1_eq_s0": s0}[name]


def identity_evidence(runs: dict, detector, m, k) -> dict:
    """Direct evidence that the PRIMITIVE field was identical across variants."""
    base = runs["baseline"]
    tau = {v: r["tau"] for v, r in runs.items()}
    common = np.minimum.reduce([tau[v] for v in VARIANTS])

    n_mon_cmp = 0
    worst_mon = 0.0
    per_ladder = []
    for i, L in enumerate(LADDER):
        mask = common > L
        n = int(mask.sum())
        if n == 0:
            per_ladder.append({"observation_index": L, "n_comparisons": 0,
                               "max_abs_diff": None,
                               "past_first_block": bool(L >= PR.BLOCK_LEN)})
            continue
        d = 0.0
        for v in VARIANTS[1:]:
            d = max(d, float(np.abs(runs[v]["ladder_sum"][..., i][mask]
                                    - base["ladder_sum"][..., i][mask]).max()))
        n_mon_cmp += n * (len(VARIANTS) - 1)
        worst_mon = max(worst_mon, d)
        per_ladder.append({"observation_index": L, "n_comparisons": n,
                           "max_abs_diff": d,
                           "past_first_block": bool(L >= PR.BLOCK_LEN)})

    worst_fresh = max(float(np.abs(runs[v]["fresh"] - base["fresh"]).max())
                      for v in VARIANTS[1:])
    n_fresh_cmp = int(base["fresh"].size) * (len(VARIANTS) - 1)

    ovf_common = np.minimum.reduce([runs[v]["ovf_count"] for v in VARIANTS])
    deep = [p for p in per_ladder if p["past_first_block"] and p["n_comparisons"]]
    n_ovf_cmp = sum(p["n_comparisons"] * (len(VARIANTS) - 1) for p in deep)
    worst_ovf = max([p["max_abs_diff"] for p in deep], default=None)

    max_block = max(r["max_block_index"] for r in runs.values())
    hashes = {v: PR.field_digest(detector, m, k, N_REP, N_CYCLES, max_block)
              for v in VARIANTS}
    hashes_match = len(set(hashes.values())) == 1

    tau_div = {v: int((tau[v] != tau["baseline"]).sum()) for v in VARIANTS}
    state_div = {v: int((runs[v]["e_start"] != base["e_start"]).sum())
                 for v in VARIANTS}

    return {
        "primitive_stream_identity": bool(
            worst_mon == 0.0 and worst_fresh == 0.0
            and (worst_ovf in (None, 0.0)) and hashes_match),
        "endogenous_path_identity": "NOT_REQUIRED",
        "statement": ("All sensitivity variants consume the same addressable "
                      "exogenous primitive random field; endogenous trajectories "
                      "may diverge as a consequence of the parameter "
                      "perturbation."),
        "n_primitive_monitor_draws_compared": n_mon_cmp,
        "n_fresh_draws_compared": n_fresh_cmp,
        "n_overflow_draws_compared": n_ovf_cmp,
        "max_abs_difference_monitor": worst_mon,
        "max_abs_difference_fresh": worst_fresh,
        "max_abs_difference_overflow": worst_ovf,
        "ladder_checkpoints": per_ladder,
        "block_len": PR.BLOCK_LEN, "max_block_index_touched": max_block,
        "deepest_observation_index_compared": max(
            (p["observation_index"] for p in per_ladder if p["n_comparisons"]),
            default=None),
        "monitor_draws_consumed_per_variant": {
            v: int(r["n_monitor_draws"]) for v, r in runs.items()},
        "overflow_draws_consumed_per_variant": {
            v: int(r["n_overflow_draws"]) for v, r in runs.items()},
        "min_common_overflow_draws": int(ovf_common.sum()),
        "primitive_field_digest_per_variant": hashes,
        "primitive_field_digest_offsets": list(PR.DIGEST_OFFSETS),
        "primitive_field_digests_match": hashes_match,
        "endogenous_tau_divergences_vs_baseline": tau_div,
        "endogenous_entering_state_divergences_vs_baseline": state_div,
    }


def main():
    t0 = time.time()
    aud = json.loads((P6R / "precommit" / "calibration_audit.json").read_text())
    ident = {"artifact": "P6R2B_CRN_PRIMITIVE_IDENTITY",
             "contract": ("for every (seed_namespace, detector, m, k, "
                          "replicate_id, cycle_id, primitive_type, "
                          "primitive_index) the raw exogenous draw is "
                          "bit-identical across all variants"),
             "address_excludes": ["policy_id", "sensitivity_variant",
                                  "s1_multiplier", "live_set_position",
                                  "stopping_time", "branch_order",
                                  "n_previously_consumed_draws"],
             "block_len": PR.BLOCK_LEN, "ladder": list(LADDER),
             "n_rep": N_REP, "n_cycles": N_CYCLES, "burn_in": BURN_IN,
             "variants": list(VARIANTS), "cells": {}}
    sens = {"artifact": "P6R2B_CORRECTED_CRN_CALIBRATION_SENSITIVITY",
            "replaces": ("p6r2_literal_closure_repair/results/"
                         "p6r2_crn_fixed_path_calibration_sensitivity.json, "
                         "whose CRN identity was FAIL: overflow draws came from "
                         "a shared vector RNG indexed by the current live set"),
            "saw_m_recalibrated": False, "shipped_constants_changed": False,
            "does_not_claim": ("This experiment does NOT prove calibration "
                               "convergence.  It measures only the empirical "
                               "sensitivity of aggregate outcomes to the "
                               "declared s1 perturbations under shared exogenous "
                               "randomness."),
            "n_rep": N_REP, "n_cycles": N_CYCLES, "burn_in": BURN_IN,
            "variants": list(VARIANTS), "cells": {}}

    for key, c in aud["cells"].items():
        det, m, k = c["detector"], int(c["m"]), int(c["k"])
        runs = {}
        for v in VARIANTS:
            s1 = variant_s1(v, c["s0"], c["s1"])
            runs[v] = simulate(detector=det,
                               decide=saw_decider(c["g0"], c["g1"], c["s0"], s1,
                                                  m, k),
                               m=m, k=k, n_rep=N_REP, n_cycles=N_CYCLES,
                               burn_in=BURN_IN)
            runs[v]["s1_used"] = float(s1)
        ident["cells"][key] = identity_evidence(runs, det, m, k)

        base = runs["baseline"]
        s1_fires = int((runs["baseline"]["tau"] < m).sum())
        rows = {v: {"s1_used": runs[v]["s1_used"],
                    "rho_mean": runs[v]["rho_mean"], "rms": runs[v]["rms"],
                    "arl0": runs[v]["arl0"]} for v in VARIANTS}
        sens["cells"][key] = {
            "detector": det, "m": m, "k": k,
            "shipped": {kk: c[kk] for kk in ("g0", "g1", "s0", "s1")},
            "variants": rows,
            "absolute_change_vs_baseline": {
                v: {mm: rows[v][mm] - rows["baseline"][mm]
                    for mm in ("rho_mean", "rms", "arl0")} for v in VARIANTS},
            "relative_change_vs_baseline": {
                v: {mm: rows[v][mm] / rows["baseline"][mm] - 1.0
                    for mm in ("rho_mean", "rms", "arl0")} for v in VARIANTS},
            "max_abs_relative_change": {
                mm: max(abs(rows[v][mm] / rows["baseline"][mm] - 1.0)
                        for v in VARIANTS) for mm in ("rho_mean", "rms", "arl0")},
            "n_cycles_where_s1_can_fire_tau_lt_m": s1_fires,
            "s1_can_fire_under_observed_trajectories": bool(s1_fires > 0),
            "why_if_not": (None if s1_fires else
                           "no cycle had tau < m, so the truncated-window branch "
                           "that s1 governs was never taken; the s1 perturbation "
                           "is therefore inert by construction, not by accident"),
            "calibration_facts_carried_forward": {
                "converged": c["converged"],
                "iterations_reached": c["iterations_reached"],
                "n_obs_behind_s1": c["n_obs_behind_s1"],
                "s1_is_fallback_equal_to_s0": c["s1_is_fallback_equal_to_s0"],
                "s1_sparse": c["s1_sparse"],
                "variance_floor_1e-2_active": c["variance_floor_1e-2_active"],
                "rho_max_can_bind": c["rho_max_can_bind"],
                "final_refit_followed_by_another_fixed_point_update":
                    c["final_refit_followed_by_another_fixed_point_update"],
                "drift_fixed_point_to_final": c["drift_fixed_point_to_final"],
            },
        }
        e = ident["cells"][key]
        print(f"{key}: primitive_identity={e['primitive_stream_identity']} "
              f"mon={e['n_primitive_monitor_draws_compared']} "
              f"ovf={e['n_overflow_draws_compared']} "
              f"maxdiff={e['max_abs_difference_monitor']} "
              f"deepest_t={e['deepest_observation_index_compared']} | "
              f"s1_fires={s1_fires} maxrel rho/rms/arl0 "
              f"{100*sens['cells'][key]['max_abs_relative_change']['rho_mean']:.3f}/"
              f"{100*sens['cells'][key]['max_abs_relative_change']['rms']:.3f}/"
              f"{100*sens['cells'][key]['max_abs_relative_change']['arl0']:.3f}% "
              f"[{time.time()-t0:.0f}s]", flush=True)
        PR.clear_cache()

    ident["all_cells_primitive_identity"] = all(
        v["primitive_stream_identity"] for v in ident["cells"].values())
    s = aud["summary"]
    sens["calibration_summary_carried_forward"] = {
        kk: s[kk] for kk in ("n_cells", "n_converged", "all_converged",
                             "non_converged_cells", "s1_sparse_cells",
                             "s1_fallback_cells", "variance_floor_active_anywhere",
                             "rho_max_can_bind_anywhere",
                             "final_refit_is_a_verified_fixed_point", "note")}
    ident["seconds"] = sens["seconds"] = time.time() - t0
    (RESULTS / "p6r2b_crn_identity.json").write_text(
        json.dumps(ident, indent=1, allow_nan=False))
    (RESULTS / "p6r2b_crn_sensitivity.json").write_text(
        json.dumps(sens, indent=1, allow_nan=False))
    print(f"all cells primitive identity: {ident['all_cells_primitive_identity']} "
          f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
