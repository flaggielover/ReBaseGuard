#!/usr/bin/env python3
"""E2: long-run reference-state law, dispersion, alternation and mixing.

Statistical unit = independent replicate chain.  Three initial-condition groups
(e0 = 0, +6, -6) run inside every cell so that initial-condition dependence and
metastability are testable directly.  Nothing here treats a time step as an
independent replicate.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, SEED_FAMILY, P3               # noqa: E402
from rebaseguard_p5.chain import simulate_chain_raw               # noqa: E402
from rebaseguard_p5.kernel import child_rng                       # noqa: E402

M_GRID = (1, 2, 3, 5)
DETECTORS = ("cusum", "sr")
RHO_ABS = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50,
           0.60, 0.70, 0.80, 0.90, 0.95, 1.0)
RHO_OVER_RHOC = (0.5, 0.8, 1.0, 1.25, 1.5, 2.0)
N_REP_PER_GROUP = 80
N_CYCLES = 2000
BURN_IN = 400
E0_GROUPS = (0.0, 6.0, -6.0)


def acf1(x: np.ndarray) -> np.ndarray:
    """Lag-1 autocorrelation per row (replicate)."""
    xc = x - x.mean(axis=1, keepdims=True)
    num = (xc[:, :-1] * xc[:, 1:]).sum(axis=1)
    den = (xc ** 2).sum(axis=1)
    return num / np.where(den > 0, den, np.nan)


def iact(x: np.ndarray, maxlag: int = 60) -> np.ndarray:
    """Initial-positive-sequence integrated autocorrelation time per row."""
    xc = x - x.mean(axis=1, keepdims=True)
    den = (xc ** 2).sum(axis=1)
    out = np.ones(x.shape[0])
    rho_prev = np.ones(x.shape[0])
    alive = np.ones(x.shape[0], dtype=bool)
    for k in range(1, maxlag + 1):
        r = (xc[:, :-k] * xc[:, k:]).sum(axis=1) / np.where(den > 0, den, np.nan)
        alive &= (r + rho_prev) > 0
        out += np.where(alive, 2.0 * r, 0.0)
        rho_prev = r
    return np.maximum(out, 1.0)


def summarize(e: np.ndarray, tau: np.ndarray) -> dict:
    ae = np.abs(e)
    per = {
        "rms": np.sqrt((e ** 2).mean(axis=1)),
        "mad": ae.mean(axis=1),
        "q90": np.quantile(ae, 0.90, axis=1),
        "q95": np.quantile(ae, 0.95, axis=1),
        "q99": np.quantile(ae, 0.99, axis=1),
        "p_gt_1": (ae > 1.0).mean(axis=1),
        "p_gt_2": (ae > 2.0).mean(axis=1),
        "p_gt_3": (ae > 3.0).mean(axis=1),
        "mean": e.mean(axis=1),
        "acf1": acf1(e),
        "alt_rate": (np.sign(e[:, :-1]) * np.sign(e[:, 1:]) < 0).mean(axis=1),
        "arl": tau.mean(axis=1),
        "iact": iact(e),
        "kurt": ((e - e.mean(axis=1, keepdims=True)) ** 4).mean(axis=1)
                / ((e ** 2).mean(axis=1) ** 2),
    }
    z = 1.959963984540054
    out = {}
    for k, v in per.items():
        n = v.size
        mu = float(np.nanmean(v))
        se = float(np.nanstd(v, ddof=1) / np.sqrt(n))
        out[k] = mu
        out[k + "_se"] = se
        out[k + "_lo"] = mu - z * se
        out[k + "_hi"] = mu + z * se
    return out


def main(seed_family: int = SEED_FAMILY, tag: int = 20,
         out: str = "chain_sweep.json") -> None:
    t3 = json.loads((P3 / "results" / "boundary_table.json").read_text())
    rc = {(r["detector_short"].lower(), int(r["m"])): r["rho_crit"]
          for r in t3["rows"] if r["layer"].startswith("GAUSSIAN")}
    n_rep = N_REP_PER_GROUP * len(E0_GROUPS)
    e0 = np.repeat(np.array(E0_GROUPS), N_REP_PER_GROUP)
    cells, t0 = [], time.time()
    samples = {}
    for det in DETECTORS:
        for m in M_GRID:
            rhos = sorted({round(v, 6) for v in RHO_ABS}
                          | {round(f * rc[(det, m)], 6) for f in RHO_OVER_RHOC})
            for i, rho in enumerate(rhos):
                rng = child_rng(seed_family, det, tag * 100 + m, i)
                r = simulate_chain_raw(detector=det, m=m, rho=rho, n_rep=n_rep,
                                       n_cycles=N_CYCLES, burn_in=BURN_IN,
                                       rng=rng, e0=e0)
                e = r.post(r.e_start)
                tau = r.post(r.tau)
                cell = {"detector": det, "m": int(m), "rho": float(rho),
                        "rho_over_rhoc": float(rho / rc[(det, m)]),
                        "rho_crit": float(rc[(det, m)]),
                        "n_rep": n_rep, "n_cycles": N_CYCLES,
                        "burn_in": BURN_IN, "all": summarize(e, tau)}
                for g, v in enumerate(E0_GROUPS):
                    sl = slice(g * N_REP_PER_GROUP, (g + 1) * N_REP_PER_GROUP)
                    cell[f"e0_{v:+.0f}"] = summarize(e[sl], tau[sl])
                cells.append(cell)
                if m in (1, 3) and rho in (0.0, 0.2, 0.5, 0.8, 1.0):
                    samples[f"{det}_m{m}_rho{rho}"] = e[::7, ::11].ravel()
                print(f"{det} m={m} rho={rho:.4f} rms={cell['all']['rms']:.4f} "
                      f"acf1={cell['all']['acf1']:+.4f} "
                      f"arl={cell['all']['arl']:7.2f} "
                      f"({time.time()-t0:6.1f}s)", flush=True)
    (RESULTS / out).write_text(json.dumps(
        {"seed_family": seed_family, "tag": tag, "n_cycles": N_CYCLES,
         "burn_in": BURN_IN, "n_rep_per_group": N_REP_PER_GROUP,
         "e0_groups": list(E0_GROUPS), "cells": cells}, indent=1))
    np.savez_compressed(RESULTS / "chain_samples.npz", **samples)
    print("wrote", RESULTS / out)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--seed-family", type=int, default=SEED_FAMILY)
    p.add_argument("--tag", type=int, default=20)
    p.add_argument("--out", default="chain_sweep.json")
    a = p.parse_args()
    main(a.seed_family, a.tag, a.out)
