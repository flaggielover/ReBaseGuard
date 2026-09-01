"""E1: the stopped-cycle Gamma matrix for one (detector, family) cell.

Usage:  run_gamma_matrix.py <detector> <family> [--batches N] [--tag TAG]
                            [--batch0 B0] [--rowblocks R]

Writes ``results/gamma/<tag>_<detector>_<family>.json``.

Everything P8's window law, regime audit and convention contrast need is a mean
of a per-cycle functional, so one pass produces them all with batch-means
standard errors.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8 import SR_THRESHOLD_GAUSSIAN                    # noqa: E402
from rebaseguard_p8.config import (                                 # noqa: E402
    LAG_DEPTH, M_GRID, RESULTS, stage_d_cusum_thresholds)
from rebaseguard_p8.stopped import simulate_batch                   # noqa: E402


def threshold_for(detector: str, family: str) -> tuple[float, str]:
    if detector == "cusum":
        return stage_d_cusum_thresholds()[family], "STAGE_D_D3_FROZEN"
    if family == "gaussian":
        return SR_THRESHOLD_GAUSSIAN, "STAGE_D_D1_FROZEN"
    cal = json.loads((RESULTS / "sr_calibration.json").read_text())
    for r in cal["rows"]:
        if r["family"] == family:
            return float(r["threshold"]), "NEW_P8_CALIBRATION"
    raise KeyError(family)


def batch_functionals(s, m_grid, lag_depth) -> dict:
    """Every P8 estimand for one batch, as plain means over its cycles."""
    out = {"n": int(s.tau.size), "arl": float(s.tau.mean()),
           "n_ties": int(s.n_ties), "max_tau": int(s.tau.max()),
           "e_tau_sq": float((s.tau.astype(float) ** 2).mean()),
           "p_up": float(s.up.mean())}
    Psi = s.Psi
    out["gamma_A"], out["gamma_B"], out["gamma_naive"] = {}, {}, {}
    out["gamma_psipsi"], out["p_tau_lt_m"], out["R_m"] = {}, {}, {}
    for m in m_grid:
        out["gamma_A"][str(m)] = float((s.zbar(m, "A") * Psi).mean())
        out["gamma_B"][str(m)] = float((s.zbar(m, "B") * Psi).mean())
        out["gamma_naive"][str(m)] = float((s.zbar(m, "A") * s.T).mean())
        out["gamma_psipsi"][str(m)] = float((s.psibar(m, "A") * Psi).mean())
        trunc = s.tau < m
        out["p_tau_lt_m"][str(m)] = float(trunc.mean())
        rem = np.where(trunc,
                       (1.0 / np.maximum(s.tau, 1) - 1.0 / m) * s.T * Psi, 0.0)
        out["R_m"][str(m)] = float(rem.mean())
    out["gamma_lag"] = [float((s.lag_z[:, r] * s.valid[:, r] * Psi).mean())
                        for r in range(lag_depth)]
    out["p_tau_gt_r"] = [float(s.valid[:, r].mean()) for r in range(lag_depth)]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("detector")
    ap.add_argument("family")
    ap.add_argument("--batches", type=int, default=20)
    ap.add_argument("--batch0", type=int, default=0)
    ap.add_argument("--rowblocks", type=int, default=50)
    ap.add_argument("--tag", default="E1")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    d = RESULTS / "gamma"
    d.mkdir(exist_ok=True)
    dest = d / f"{a.tag}_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present; pass --force to redo)")
        return
    thr, provenance = threshold_for(a.detector, a.family)
    experiment = f"p8_gamma_{a.tag}"
    batches, t0 = [], time.time()
    for b in range(a.batch0, a.batch0 + a.batches):
        s = simulate_batch(experiment=experiment, family=a.family,
                           detector=a.detector, threshold=thr, batch=b,
                           n_row_blocks=a.rowblocks, L=LAG_DEPTH)
        batches.append(batch_functionals(s, M_GRID, LAG_DEPTH))
        print(f"  {a.detector}/{a.family} batch {b - a.batch0 + 1}/{a.batches} "
              f"[{time.time() - t0:.0f}s]", flush=True)
    out = {"schema": "rebaseguard.p8.gamma-cell.v1",
           "tag": a.tag, "experiment_tag": experiment,
           "detector": a.detector, "family": a.family,
           "threshold": thr, "threshold_provenance": provenance,
           "m_grid": list(M_GRID), "lag_depth": LAG_DEPTH,
           "batch0": a.batch0, "n_batches": a.batches,
           "row_blocks_per_batch": a.rowblocks,
           "cycles_per_batch": a.rowblocks * 4096,
           "n_cycles": a.batches * a.rowblocks * 4096,
           "seconds": time.time() - t0,
           "batches": batches}
    dest.write_text(json.dumps(out, indent=1) + "\n")
    g = np.array([bb["gamma_A"]["1"] for bb in batches])
    print(f"DONE {a.detector}/{a.family} Gamma_A(1)={g.mean():.4f}"
          f"+-{g.std(ddof=1)/np.sqrt(g.size):.4f} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
