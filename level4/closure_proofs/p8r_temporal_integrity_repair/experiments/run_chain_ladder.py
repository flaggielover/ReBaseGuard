"""E3: the in-control reuse ladder for one ``(detector, family)`` cell.

The reuse grid is **P7's ladder verbatim** -- multiples of ``rho_c`` plus the
absolute practitioner anchors -- so that P7's pre-committed boundary criterion
can be applied to every innovation family without re-specification.

``rho_c(D, f, m)`` is read at run time from P8R's own E1 Gamma matrix, which is
the only place a non-Gaussian ``rho_c`` exists inside this campaign.

Usage:  run_chain_ladder.py <detector> <family>
"""
from __future__ import annotations

import argparse
import time

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.addressing import PROD_CHAIN_E3             # noqa: E402
from rebaseguard_p8r.analysis import batch_mean_se               # noqa: E402
from rebaseguard_p8r.chain import simulate_chain                 # noqa: E402
from rebaseguard_p8r.config import (E3_BURN_IN, E3_CYCLES,       # noqa: E402
                                     E3_REPLICATES, M_CHAIN, RESULTS,
                                     RHO_ABSOLUTE, RHO_MULTIPLIERS)
from thresholds import CalibrationFailed, threshold_for           # noqa: E402

FA_HORIZON = 100


def rho_c_of(cell: dict, m: int) -> float:
    g = np.array([b["gamma_A"][str(m)] for b in cell["batches"]]).mean()
    return float(1.0 / abs(1.0 - g))


def metrics(r) -> dict:
    arl = r.per_replicate_arl
    mse = r.per_replicate_ref_mse
    fap = r.per_replicate_fap(FA_HORIZON)
    acf = r.per_replicate_acf1
    out = {}
    for name, v in (("arl", arl), ("ref_mse", mse), ("fap100", fap),
                    ("e_acf1", acf)):
        mu, se, n = batch_mean_se(v)
        out[name] = mu
        out[name + "_se"] = se
    out["n_replicates"] = int(arl.size)
    out["ref_rms"] = float(np.sqrt(mse.mean()))
    # P7 defines e_acf1 as the POOLED correlation over all replicate pairs
    # (p7/experiments/run_chain_sweep.py); restated exactly so that P7's
    # boundary criterion applies to the same object.  The per-replicate version
    # above is kept only because it carries a standard error.
    post_e = r.post(r.e_start)
    a, b = post_e[:, :-1].ravel(), post_e[:, 1:].ravel()
    out["e_acf1_per_replicate_mean"] = out["e_acf1"]
    out["e_acf1"] = float(np.corrcoef(a, b)[0, 1])
    out["max_block_index"] = r.max_block_index
    out["n_overflow_draws"] = r.n_overflow_draws
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("detector")
    ap.add_argument("family")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    dest = RESULTS / "chain" / f"E3_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present)")
        return
    try:
        thr, prov = threshold_for(a.detector, a.family)
    except CalibrationFailed as e:
        C.write(dest, C.envelope(
            generator="run_chain_ladder.py",
            schema="rebaseguard.p8r.chain-ladder.v1", tags=[PROD_CHAIN_E3],
            payload={"detector": a.detector, "family": a.family,
                     "status": "EXCLUDED_CALIBRATION_FAILED",
                     "reason": str(e), "rows": []}))
        print(f"EXCLUDED chain {a.detector}/{a.family}: {e}")
        return

    cell = C.load_payload(RESULTS / "gamma" / f"E1_{a.detector}_{a.family}.json")
    rows, t0 = [], time.time()
    for m in M_CHAIN:
        rc = rho_c_of(cell, m)
        grid = {}
        for f in RHO_MULTIPLIERS:
            v = f * rc
            if 0.0 <= v <= 1.0:
                grid[round(v, 12)] = f
        for v in RHO_ABSOLUTE:
            grid.setdefault(round(float(v), 12), None)
        for rho in sorted(grid):
            r = simulate_chain(experiment=PROD_CHAIN_E3, family=a.family,
                               detector=a.detector, threshold=thr, m=m,
                               rho=rho, n_rep=E3_REPLICATES,
                               n_cycles=E3_CYCLES, burn_in=E3_BURN_IN)
            row = {"m": m, "rho": rho, "rho_over_rhoc": grid[rho],
                   "rho_c": rc, **metrics(r)}
            rows.append(row)
            print(f"  m={m} rho={rho:.5f} arl={row['arl']:.2f} "
                  f"mse={row['ref_mse']:.4f} [{time.time() - t0:.0f}s]",
                  flush=True)
    payload = {"detector": a.detector, "family": a.family, "status": "OK",
               "threshold": thr, "threshold_provenance": prov,
               "n_replicates": E3_REPLICATES, "n_cycles": E3_CYCLES,
               "burn_in": E3_BURN_IN, "fa_horizon": FA_HORIZON,
               "rho_ladder_source": "P7 EXPERIMENT_DESIGN, verbatim",
               "seconds": time.time() - t0, "rows": rows}
    C.write(dest, C.envelope(generator="run_chain_ladder.py",
                             schema="rebaseguard.p8r.chain-ladder.v1",
                             tags=[PROD_CHAIN_E3], payload=payload))
    print(f"DONE chain {a.detector}/{a.family} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
