"""E3: the in-control reuse ladder, for one (detector, family) cell.

The reuse grid is **P7's ladder verbatim** -- multiples of ``rho_c`` plus the
absolute practitioner anchors -- so that P7's pre-committed boundary criterion
can be applied to every innovation family without re-specification.

``rho_c(D, f, m)`` is read at run time from P8's own Gamma matrix, which is the
only place a non-Gaussian ``rho_c`` exists.

Usage:  run_chain_ladder.py <detector> <family> [--reps N] [--cycles N]
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
from rebaseguard_p8.analysis import batch_mean_se                   # noqa: E402
from rebaseguard_p8.chain import simulate_chain                     # noqa: E402
from rebaseguard_p8.config import RESULTS                           # noqa: E402
from run_gamma_matrix import threshold_for                          # noqa: E402

RHO_OVER_RHOC = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)   # P7 ladder
RHO_ABSOLUTE = (0.0, 0.25, 0.5, 0.75, 1.0)
M_CHAIN = (1, 5)
FA_HORIZON = 100


def gamma_cell(detector: str, family: str, tag: str = "E1") -> dict:
    p = RESULTS / "gamma" / f"{tag}_{detector}_{family}.json"
    return json.loads(p.read_text())


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
    # boundary criterion can be applied to the same object.  The per-replicate
    # version above is kept only because it carries a standard error.
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
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--cycles", type=int, default=70)
    ap.add_argument("--burn-in", type=int, default=20)
    ap.add_argument("--tag", default="E3")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--gamma-tag", default="E1")
    a = ap.parse_args()

    d = RESULTS / "chain"
    d.mkdir(exist_ok=True)
    dest = d / f"{a.tag}_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present; pass --force to redo)")
        return

    thr, prov = threshold_for(a.detector, a.family)
    cell = gamma_cell(a.detector, a.family, a.gamma_tag)
    experiment = f"p8_chain_{a.tag}"
    rows, t0 = [], time.time()
    for m in M_CHAIN:
        rc = rho_c_of(cell, m)
        grid = {}
        for f in RHO_OVER_RHOC:
            v = f * rc
            if 0.0 <= v <= 1.0:
                grid[round(v, 12)] = f
        for v in RHO_ABSOLUTE:
            grid.setdefault(round(float(v), 12), None)
        for rho in sorted(grid):
            r = simulate_chain(experiment=experiment, family=a.family,
                               detector=a.detector, threshold=thr, m=m,
                               rho=rho, n_rep=a.reps, n_cycles=a.cycles,
                               burn_in=a.burn_in)
            row = {"m": m, "rho": rho, "rho_over_rhoc": grid[rho],
                   "rho_c": rc, **metrics(r)}
            rows.append(row)
            print(f"  m={m} rho={rho:.5f} arl={row['arl']:.2f} "
                  f"mse={row['ref_mse']:.4f} [{time.time()-t0:.0f}s]", flush=True)
    out = {"schema": "rebaseguard.p8.chain-ladder.v1", "tag": a.tag,
           "experiment_tag": experiment, "detector": a.detector,
           "family": a.family, "threshold": thr, "threshold_provenance": prov,
           "n_replicates": a.reps, "n_cycles": a.cycles, "burn_in": a.burn_in,
           "fa_horizon": FA_HORIZON, "rho_ladder_source": "P7 EXPERIMENT_DESIGN",
           "seconds": time.time() - t0, "rows": rows}
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(f"DONE chain {a.detector}/{a.family} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
