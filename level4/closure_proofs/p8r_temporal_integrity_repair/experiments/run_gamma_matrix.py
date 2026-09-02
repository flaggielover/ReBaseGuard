"""E1 / E5: the stopped-cycle Gamma matrix for one ``(detector, family)`` cell.

Every P8R window-law, regime-audit and convention estimand is a mean of a
per-cycle functional, so one pass over the frozen cycle budget produces them all
with batch-means standard errors over the 20 addressable batches.

E1 and E5 differ **only** in their batch region (``0..19`` vs ``100..119``) and
their production tag, so E5 is an independent seed realisation of the identical
estimand -- that is what the seed-sensitivity question S13 compares.

Usage:  run_gamma_matrix.py <detector> <family> [--tag E1|E5]
"""
from __future__ import annotations

import argparse
import sys
import time

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.addressing import (PROD_GAMMA_E1,           # noqa: E402
                                        PROD_GAMMA_E5)
from rebaseguard_p8r.config import (E1_BATCH0, E1_BATCHES,       # noqa: E402
                                     E1_ROW_BLOCKS, E5_BATCH0, E5_BATCHES,
                                     E5_ROW_BLOCKS, LAG_DEPTH, M_GRID, RESULTS)
from rebaseguard_p8r.stopped import simulate_batch                # noqa: E402
from thresholds import CalibrationFailed, threshold_for           # noqa: E402

PLAN = {"E1": (PROD_GAMMA_E1, E1_BATCH0, E1_BATCHES, E1_ROW_BLOCKS),
        "E5": (PROD_GAMMA_E5, E5_BATCH0, E5_BATCHES, E5_ROW_BLOCKS)}


def batch_functionals(s, m_grid, lag_depth) -> dict:
    """Every P8R stopped-cycle estimand for one batch, as plain means."""
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
    ap.add_argument("--tag", default="E1", choices=sorted(PLAN))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    dest = RESULTS / "gamma" / f"{a.tag}_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present)")
        return
    experiment, batch0, batches, row_blocks = PLAN[a.tag]
    try:
        thr, prov = threshold_for(a.detector, a.family)
    except CalibrationFailed as e:
        C.write(dest, C.envelope(
            generator="run_gamma_matrix.py",
            schema="rebaseguard.p8r.gamma-cell.v1", tags=[experiment],
            payload={"tag": a.tag, "detector": a.detector, "family": a.family,
                     "status": "EXCLUDED_CALIBRATION_FAILED", "reason": str(e),
                     "batches": []}))
        print(f"EXCLUDED {a.detector}/{a.family}: {e}")
        return

    t0, batches_out = time.time(), []
    for b in range(batch0, batch0 + batches):
        s = simulate_batch(experiment=experiment, family=a.family,
                           detector=a.detector, threshold=thr, batch=b,
                           n_row_blocks=row_blocks, L=LAG_DEPTH)
        batches_out.append(batch_functionals(s, M_GRID, LAG_DEPTH))
        print(f"  {a.detector}/{a.family} batch {b - batch0 + 1}/{batches} "
              f"[{time.time() - t0:.0f}s]", flush=True)

    payload = {"tag": a.tag, "detector": a.detector, "family": a.family,
               "status": "OK", "threshold": thr, "threshold_provenance": prov,
               "m_grid": list(M_GRID), "lag_depth": LAG_DEPTH,
               "batch0": batch0, "n_batches": batches,
               "row_blocks_per_batch": row_blocks,
               "cycles_per_batch": row_blocks * 4096,
               "n_cycles": batches * row_blocks * 4096,
               "seconds": time.time() - t0, "batches": batches_out}
    C.write(dest, C.envelope(generator="run_gamma_matrix.py",
                             schema="rebaseguard.p8r.gamma-cell.v1",
                             tags=[experiment], payload=payload))
    g = np.array([bb["gamma_A"]["1"] for bb in batches_out])
    print(f"DONE {a.tag} {a.detector}/{a.family} Gamma_A(1)={g.mean():.4f}"
          f"+-{g.std(ddof=1) / np.sqrt(g.size):.4f} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
