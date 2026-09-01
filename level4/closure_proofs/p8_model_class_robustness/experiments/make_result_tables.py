"""Flatten every P8 primary table into one machine-readable artifact.

``results/result_tables.json`` is the single file an independent replayer needs
to compare against: every headline number, keyed by cell, with its standard
error and its provenance.  It is derived, never authored.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.config import (                                 # noqa: E402
    DETECTORS, FAMILIES, MOMENT_MARGINAL, RESULTS)


def load(n):
    p = RESULTS / n
    return json.loads(p.read_text()) if p.exists() else None


def main() -> None:
    mat = load("gamma_matrix_E1.json")
    mat5 = load("gamma_matrix_E5.json")
    dec = load("closure_decision.json")
    cal = load("sr_calibration.json")
    xp = load("cross_priority_consistency.json")
    idx5 = {(c["detector"], c["family"]): c for c in mat5["cells"]} if mat5 else {}

    gamma = []
    for c in mat["cells"]:
        for m, r in c["per_m"].items():
            row = {"detector": c["detector"], "family": c["family"], "m": int(m),
                   "threshold": c["threshold"],
                   "threshold_provenance": c["threshold_provenance"],
                   "arl0_measured": c["arl0"], "n_cycles": c["n_cycles"],
                   "moment_marginal": c["moment_marginal"],
                   "extrapolation_beyond_p3": r["extrapolation_beyond_p3"],
                   **{k: r[k] for k in (
                       "gamma_A", "gamma_A_se", "gamma_A_ci95", "gamma_B",
                       "gamma_B_se", "gamma_naive_wrong_score",
                       "gamma_psipsi_stage_d_estimand", "R_m", "p_tau_lt_m",
                       "rho_c", "rho_c_interval", "regime",
                       "lower_bound_exceeds_2", "K", "K_se", "K_ci95")}}
            k5 = idx5.get((c["detector"], c["family"]))
            if k5:
                row["gamma_A_seed_family_E5"] = k5["per_m"][m]["gamma_A"]
                row["gamma_A_seed_family_E5_se"] = k5["per_m"][m]["gamma_A_se"]
            gamma.append(row)

    lag = [{"detector": c["detector"], "family": c["family"],
            "gamma_lag": c["gamma_lag"], "gamma_lag_se": c["gamma_lag_se"],
            "lag_profile_w": c["lag_profile_w"],
            "lag_profile_w_se": c["lag_profile_w_se"],
            "p_tau_gt_r": c["p_tau_gt_r"]} for c in mat["cells"]]

    chain = []
    for d in DETECTORS:
        for f in FAMILIES:
            p = RESULTS / "chain" / f"E3_{d}_{f}.json"
            if p.exists():
                c = json.loads(p.read_text())
                for r in c["rows"]:
                    chain.append({"detector": d, "family": f, **r})
    drift = []
    for d in DETECTORS:
        for f in FAMILIES:
            p = RESULTS / "drift" / f"E4_{d}_{f}.json"
            if p.exists():
                c = json.loads(p.read_text())
                for r in c["rows"]:
                    drift.append({"detector": d, "family": f,
                                  **{k: r[k] for k in
                                     ("m", "rho", "pattern", "size", "slope",
                                      "pre_change_arl", "ref_mse_pre")},
                                  **{f"delay_{k}": v
                                     for k, v in r["delay"].items()}})

    out = {"schema": "rebaseguard.p8.result-tables.v1",
           "anchor_commit": "ffe23a63181e2ff11380768d3c73980de80f94fb",
           "moment_marginal_families": list(MOMENT_MARGINAL),
           "verdict": dec["verdict"] if dec else None,
           "gate_results": dec["gate_results"] if dec else None,
           "sr_calibration": [{k: r.get(k) for k in
                               ("family", "threshold", "label",
                                "verification_arl0", "verification_se",
                                "verification_relative_error",
                                "n_iterations", "n_polish_iterations")}
                              for r in cal["rows"]] if cal else None,
           "gamma_matrix": gamma,
           "lag_profiles": lag,
           "chain_ladder": chain,
           "drift": drift,
           "cross_priority_consistency": xp["rows"] if xp else None}
    (RESULTS / "result_tables.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"gamma rows={len(gamma)} lag={len(lag)} chain={len(chain)} "
          f"drift={len(drift)}")


if __name__ == "__main__":
    main()
