"""E2/E6: the main repeated-cycle sweep.

For every (detector, m, rho) cell one chain is started from the EXACT reference
e_0 = 0 -- the frozen / safe-reference condition -- and run for n_cycles cycles.
That single run yields both

  * the finite-cycle degradation curve  (cycle index j = 0, 1, 2, ...), and
  * the quasi-stationary metrics        (cycles after burn_in).

Statistical unit is the REPLICATE (Stage-D protocol section 6), so every standard
error is an across-replicate standard error and serial dependence inside a
replicate is absorbed rather than ignored.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD    # noqa: E402
from rebaseguard_p7.chain import simulate_chain                         # noqa: E402
from rebaseguard_p7.config import (                                     # noqa: E402
    DETECTOR_CODE, DETECTORS, FA_HORIZONS, M_GRID, RESULTS, SEED_FAMILY,
    load_p3_boundaries, rho_grid,
)

N_REP = 5000
N_CYCLES = 50
BURN_IN = 12
E_SUBSAMPLE = 40_000


def summarise(res, boundaries) -> dict:
    tau = res.tau.astype(float)
    e = res.e_start
    post_tau = tau[:, BURN_IN:]
    post_e = e[:, BURN_IN:]
    per_rep_arl = post_tau.mean(axis=1)
    per_rep_mse = (post_e ** 2).mean(axis=1)
    n = per_rep_arl.size

    a, b = post_e[:, :-1], post_e[:, 1:]
    acf1 = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    d = res.direction[:, BURN_IN:].astype(float)
    dacf1 = float(np.corrcoef(d[:, :-1].ravel(), d[:, 1:].ravel())[0, 1])

    # per-replicate false-alarm probabilities: P(tau <= N) inside one cycle
    fap = {}
    for N in FA_HORIZONS:
        per_rep = (post_tau <= N).mean(axis=1)
        fap[str(N)] = {"est": float(per_rep.mean()),
                       "se": float(per_rep.std(ddof=1) / np.sqrt(n))}

    flat_e = post_e.ravel()
    if flat_e.size > E_SUBSAMPLE:
        step = flat_e.size // E_SUBSAMPLE
        flat_e = flat_e[::step][:E_SUBSAMPLE]

    return ({
        "detector": res.detector, "m": res.m, "rho": res.rho,
        "n_rep": n, "n_cycles": N_CYCLES, "burn_in": BURN_IN,
        "arl": float(per_rep_arl.mean()),
        "arl_se": float(per_rep_arl.std(ddof=1) / np.sqrt(n)),
        "arl_median_cycle": float(np.median(post_tau)),
        "ref_mse": float(per_rep_mse.mean()),
        "ref_mse_se": float(per_rep_mse.std(ddof=1) / np.sqrt(n)),
        "ref_m4": float((post_e ** 4).mean()),
        "ref_abs": float(np.abs(post_e).mean()),
        "e_acf1": acf1, "direction_acf1": dacf1,
        "fap": fap,
        "cycle_arl": [float(v) for v in tau.mean(axis=0)],
        "cycle_arl_se": [float(v) for v in tau.std(axis=0, ddof=1) / np.sqrt(n)],
        "cycle_mse": [float(v) for v in (e ** 2).mean(axis=0)],
        "e_quantiles": {str(q): float(np.quantile(np.abs(post_e), q))
                        for q in (0.5, 0.75, 0.9, 0.95, 0.99)},
    }, {"per_rep_arl": per_rep_arl.astype(np.float64),
        "per_rep_mse": per_rep_mse.astype(np.float64),
        "per_rep_fap100": (post_tau <= 100).mean(axis=1),
        "e_sample": flat_e.astype(np.float32)})


def main() -> None:
    boundaries = load_p3_boundaries()
    cells, raw, t0 = [], {}, time.time()
    for det in DETECTORS:
        thr = CUSUM_THRESHOLD if det == CUSUM else SR_THRESHOLD
        for m in M_GRID:
            for rho in rho_grid(det, m, boundaries):
                ss = np.random.SeedSequence(
                    [SEED_FAMILY, 2, DETECTOR_CODE[det], m, int(round(rho * 1e7))])
                res = simulate_chain(
                    detector=det, m=m, rho=rho, n_rep=N_REP, n_cycles=N_CYCLES,
                    burn_in=BURN_IN, e0=0.0, threshold=thr,
                    rng=np.random.Generator(np.random.PCG64(ss)))
                row, arrays = summarise(res, boundaries)
                row["rho_c"] = boundaries[(det, m)]["rho_crit"]
                row["rho_over_rhoc"] = rho / row["rho_c"]
                row["gamma_tilde_p3"] = boundaries[(det, m)]["gamma_tilde"]
                row["lambda_p3"] = rho * (1.0 - row["gamma_tilde_p3"])
                key = f"{det}_m{m}_r{int(round(rho*1e7)):09d}"
                row["array_key"] = key
                for name, arr in arrays.items():
                    raw[f"{key}__{name}"] = arr
                cells.append(row)
                print(f"{det} m={m} rho={rho:.4f} (r/rc={row['rho_over_rhoc']:5.2f}) "
                      f"ARL={row['arl']:8.2f}+-{row['arl_se']:.2f} "
                      f"MSE={row['ref_mse']:.4f} acf1={row['e_acf1']:+.3f} "
                      f"[{time.time()-t0:6.1f}s]", flush=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "chain_sweep.json").write_text(json.dumps(
        {"seed_family": SEED_FAMILY, "n_rep": N_REP, "n_cycles": N_CYCLES,
         "burn_in": BURN_IN, "cells": cells}, indent=1))
    np.savez_compressed(RESULTS / "chain_sweep_arrays.npz", **raw)
    print("wrote", RESULTS / "chain_sweep.json", "and chain_sweep_arrays.npz")


if __name__ == "__main__":
    main()
