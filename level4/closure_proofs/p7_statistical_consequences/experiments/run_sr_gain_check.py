"""Focused higher-precision re-measurement of the frozen Gaussian SR gain.

P7's correspondence check found the P7 estimate of GammaTilde^SR below P3's at
every m, with the same sign and magnitude.  P7 does not own those numbers, so
this script only sharpens the observation for independent adjudication: it
re-measures at 2,000,000 cycles (P3's own sample size) with batch-means standard
errors, and reports the comparison.  Nothing upstream is edited.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD   # noqa: E402
from rebaseguard_p7.config import (                                   # noqa: E402
    DETECTOR_CODE, M_GRID, RESULTS, SEED_FAMILY, load_p3_boundaries)
from rebaseguard_p7.cycles import simulate_cycles                     # noqa: E402

N_BATCH = 20
PER_BATCH = 100_000


def main() -> None:
    b = load_p3_boundaries()
    out = {"n_batches": N_BATCH, "paths_per_batch": PER_BATCH, "rows": []}
    print("SR threshold hex:", float.hex(SR_THRESHOLD))
    for det, thr in ((SR, SR_THRESHOLD), (CUSUM, CUSUM_THRESHOLD)):
        batches = {m: [] for m in M_GRID}
        arls, t0 = [], time.time()
        for k in range(N_BATCH):
            ss = np.random.SeedSequence([SEED_FAMILY, 7, DETECTOR_CODE[det], k])
            cs = simulate_cycles(detector=det, e=0.0, n_paths=PER_BATCH,
                                 m_grid=M_GRID,
                                 rng=np.random.Generator(np.random.PCG64(ss)),
                                 threshold=thr)
            arls.append(float(cs.tau.mean()))
            for m in M_GRID:
                batches[m].append(float((cs.zbar_for(m) * cs.T).mean()))
            print(f"  {det} batch {k+1}/{N_BATCH} [{time.time()-t0:.0f}s]",
                  flush=True)
        for m in M_GRID:
            v = np.array(batches[m])
            est = float(v.mean())
            se = float(v.std(ddof=1) / np.sqrt(N_BATCH))
            p3 = b[(det, m)]["gamma_tilde"]
            p3_se = b[(det, m)]["gamma_tilde_se"]
            comb = float(np.sqrt(se ** 2 + p3_se ** 2))
            out["rows"].append({
                "detector": det, "m": m, "p7_gamma": est,
                "p7_batch_se": se, "p3_gamma": p3, "p3_se": p3_se,
                "combined_se": comb, "z_combined": (est - p3) / comb,
                "p7_rho_c": 1.0 / (est - 1.0),
                "p3_rho_c": b[(det, m)]["rho_crit"],
                "rho_c_relative_shift": (1.0 / (est - 1.0)) /
                                        b[(det, m)]["rho_crit"] - 1.0,
            })
            print(f"{det} m={m}: P7 {est:.4f}+-{se:.4f}  P3 {p3:.4f}+-{p3_se:.4f} "
                  f" z={out['rows'][-1]['z_combined']:+.2f}  "
                  f"rho_c shift {100*out['rows'][-1]['rho_c_relative_shift']:+.2f}%",
                  flush=True)
        out[f"arl0_{det}"] = {"est": float(np.mean(arls)),
                              "se": float(np.std(arls, ddof=1) / np.sqrt(N_BATCH))}
    (RESULTS / "sr_gain_check.json").write_text(json.dumps(out, indent=1))
    print("wrote", RESULTS / "sr_gain_check.json")


if __name__ == "__main__":
    main()
