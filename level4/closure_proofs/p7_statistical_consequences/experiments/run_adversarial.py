"""Adversarial checks against the P7 conclusions.  Emits results/adversarial.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD    # noqa: E402
from rebaseguard_p7.chain import simulate_chain                         # noqa: E402
from rebaseguard_p7.config import (                                     # noqa: E402
    DETECTOR_CODE, DETECTORS, M_GRID, RESULTS, SEED_FAMILY,
)

ALT_SEED = 20260901          # deliberately outside the production family


def main() -> None:
    res = json.loads((RESULTS / "consequences.json").read_text())
    cells = res["cells"]
    idx = {(c["detector"], c["m"], round(c["rho"], 10)): c for c in cells}
    out = {}

    # --- A1 burn-in adequacy: late window vs the reported window ----------
    a1 = []
    for c in cells:
        ca = np.array(c["cycle_arl"])
        late = ca[30:].mean()
        rep = ca[12:].mean()
        a1.append({"key": c["array_key"], "reported_window": float(rep),
                   "late_window": float(late),
                   "relative_shift": float(late / rep - 1.0)})
    worst = max(a1, key=lambda r: abs(r["relative_shift"]))
    out["burn_in_adequacy"] = {
        "note": ("cycle-mean ARL over cycles 12-49 (reported) vs 30-49 (late). "
                 "A large shift would mean burn_in=12 is too short."),
        "worst_cell": worst,
        "max_abs_relative_shift": float(max(abs(r["relative_shift"]) for r in a1)),
        "n_cells_shifted_more_than_2pct":
            int(sum(abs(r["relative_shift"]) > 0.02 for r in a1)),
    }

    # --- A2 estimator stability: normal vs bootstrap intervals -------------
    widths = []
    for c in cells:
        nb = c["arl_normal_ci"]
        bb = c["arl_boot_ci"]
        wn, wb = nb[1] - nb[0], bb[1] - bb[0]
        widths.append(abs(wb - wn) / wn)
    out["interval_agreement"] = {
        "note": "run lengths are heavy tailed; the replicate mean need not be",
        "max_relative_width_disagreement": float(max(widths)),
        "n_cells_over_20pct": int(sum(w > 0.20 for w in widths)),
    }

    # --- A3 seed dependence: independent replication of four claims -------
    a3 = []
    for det, m, rho in [("cusum", 1, 1.0), ("cusum", 5, 0.0), ("sr", 3, 0.25),
                        ("sr", 5, 1.0), ("cusum", 1, 0.0), ("cusum", 1, 0.25)]:
        thr = CUSUM_THRESHOLD if det == CUSUM else SR_THRESHOLD
        ss = np.random.SeedSequence([ALT_SEED, 2, DETECTOR_CODE[det], m,
                                     int(round(rho * 1e7))])
        r = simulate_chain(detector=det, m=m, rho=rho, n_rep=5000, n_cycles=50,
                           burn_in=12, e0=0.0, threshold=thr,
                           rng=np.random.Generator(np.random.PCG64(ss)))
        arl = r.cycle_arl
        base = idx[(det, m, round(rho, 10))]
        se = np.sqrt((arl.std(ddof=1) / np.sqrt(arl.size)) ** 2
                     + base["arl_se"] ** 2)
        a3.append({"detector": det, "m": m, "rho": rho,
                   "production_arl": base["arl"],
                   "replication_arl": float(arl.mean()),
                   "z": float((arl.mean() - base["arl"]) / se)})
        print(f"A3 {det} m={m} rho={rho}: prod={base['arl']:.2f} "
              f"alt-seed={arl.mean():.2f} z={a3[-1]['z']:+.2f}", flush=True)
    out["seed_dependence"] = {"seed_family": ALT_SEED, "cells": a3,
                              "max_abs_z": float(max(abs(r["z"]) for r in a3))}

    # --- A4 is the ARL maximum in rho real, or noise? ----------------------
    a4 = []
    for d in DETECTORS:
        for m in M_GRID:
            rows = sorted((c for c in cells if c["detector"] == d and c["m"] == m),
                          key=lambda c: c["rho"])
            best = max(rows, key=lambda c: c["arl"])
            zero = rows[0]
            diff = best["arl"] - zero["arl"]
            se = np.sqrt(best["arl_se"] ** 2 + zero["arl_se"] ** 2)
            a4.append({"detector": d, "m": m, "argmax_rho": best["rho"],
                       "argmax_rho_over_rhoc": best["rho_over_rhoc"],
                       "gain_over_fresh": float(diff / zero["arl"]),
                       "z": float(diff / se)})
    out["non_monotonicity"] = {
        "note": ("EXPLORATORY. The in-control ARL is maximised at a strictly "
                 "positive reuse fraction, well above rho_c. Not a "
                 "pre-committed claim and not a mitigation recommendation."),
        "cells": a4, "min_z": float(min(r["z"] for r in a4))}

    # --- A5 boundary verdict robustness -----------------------------------
    bv = json.loads((RESULTS / "boundary_verdict.json").read_text())
    peaks = bv["families_peaking_at_boundary_per_metric"]
    out["boundary_robustness"] = {
        "note": ("the criterion needs >=4 of 8 families for one metric; the "
                 "observed maximum is far below, so the verdict does not turn "
                 "on the threshold"),
        "per_metric": peaks, "required": 4, "observed_max": int(max(peaks.values())),
        "verdict_would_flip_at_threshold": int(max(peaks.values())) + 1,
    }

    # --- A6 gain correspondence with the closed campaigns -----------------
    a6 = []
    for d in DETECTORS:
        s = res["curve_summary"][d]
        for m in M_GRID:
            mine = s["gamma_tilde_remeasured"][str(m)]
            se = s["gamma_tilde_remeasured_se"][str(m)]
            p3 = s["gamma_tilde_p3"][str(m)]
            a6.append({"detector": d, "m": m, "p7": mine, "p7_se": se,
                       "p3": p3, "abs_diff": abs(mine - p3),
                       "diff_in_p7_se": float((mine - p3) / se)})
    out["gain_correspondence"] = {
        "note": ("P7 re-measures GammaTilde only as a correspondence check and "
                 "does not own those numbers; a disagreement is reported, not "
                 "resolved, here"),
        "cells": a6,
        "max_abs_diff_in_p7_se": float(max(abs(r["diff_in_p7_se"]) for r in a6)),
    }

    (RESULTS / "adversarial.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items()
                      if k != "seed_dependence"}, indent=1)[:2400])


if __name__ == "__main__":
    main()
