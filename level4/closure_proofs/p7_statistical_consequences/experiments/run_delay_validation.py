"""E5 validation: is the delay identity E[tau | shift] = E_pi[A(e - Delta)] real?

The identity is exact under the frozen semantics (detector reset + iid
innovations, so the entering reference error is a sufficient statistic for the
cycle).  It is nevertheless CHECKED by direct simulation before P7 uses it to
populate the delay grid; if it fails the identity route is abandoned, not
patched.  The shift is applied at a re-baselining instant, the D2.5 convention.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD    # noqa: E402
from rebaseguard_p7.analysis import ResponseCurves, load_curves         # noqa: E402
from rebaseguard_p7.chain import simulate_chain                         # noqa: E402
from rebaseguard_p7.config import (                                   # noqa: E402
    DETECTOR_CODE, M_GRID, RESULTS, SEED_FAMILY, load_p3_boundaries)

SHIFT_CYCLE = 25
N_CYCLES = 27
N_REP = 40_000
CELLS = [("cusum", 1, 1.0), ("cusum", 5, 0.0), ("sr", 5, 1.0), ("sr", 2, 0.5)]


def main() -> None:
    raw = load_curves()["curves"]
    curves = {d: ResponseCurves(raw[d], M_GRID) for d in ("cusum", "sr")}
    sweep = json.loads((RESULTS / "chain_sweep.json").read_text())
    arrays = np.load(RESULTS / "chain_sweep_arrays.npz")
    index = {(c["detector"], c["m"], round(c["rho"], 10)): c
             for c in sweep["cells"]}
    boundaries = load_p3_boundaries()
    del boundaries
    rows, t0 = [], time.time()
    for det, m, rho in CELLS:
        thr = CUSUM_THRESHOLD if det == CUSUM else SR_THRESHOLD
        cell = index[(det, m, round(rho, 10))]
        e_pi = arrays[f"{cell['array_key']}__e_sample"].astype(float)
        for D in (0.5, 1.0):
            ss = np.random.SeedSequence([SEED_FAMILY, 5, DETECTOR_CODE[det], m,
                                         int(round(rho * 1e7)), int(D * 1000)])
            res = simulate_chain(detector=det, m=m, rho=rho, n_rep=N_REP,
                                 n_cycles=N_CYCLES, burn_in=SHIFT_CYCLE, e0=0.0,
                                 shift=D, shift_cycle=SHIFT_CYCLE,
                                 threshold=thr,
                                 rng=np.random.Generator(np.random.PCG64(ss)))
            direct = res.tau[:, SHIFT_CYCLE].astype(float)
            pred = float(curves[det].A(e_pi - D).mean())
            rows.append({
                "detector": det, "m": m, "rho": rho, "shift": D,
                "direct_mean": float(direct.mean()),
                "direct_se": float(direct.std(ddof=1) / np.sqrt(N_REP)),
                "identity_prediction": pred,
                "relative_gap": float(direct.mean() / pred - 1.0),
                "z": float((direct.mean() - pred) /
                           (direct.std(ddof=1) / np.sqrt(N_REP))),
                "n_rep": N_REP, "shift_cycle": SHIFT_CYCLE,
                "direct_median": float(np.median(direct)),
                "direct_q75": float(np.quantile(direct, 0.75)),
                "direct_q95": float(np.quantile(direct, 0.95)),
                "direct_p_gt_100": float((direct > 100).mean()),
                "nominal_delay": float(curves[det].A(np.array([-D]))[0]),
            })
            print(f"{det} m={m} rho={rho} D={D}: direct={direct.mean():8.3f}"
                  f"+-{rows[-1]['direct_se']:.3f} identity={pred:8.3f} "
                  f"gap={rows[-1]['relative_gap']:+.4f} z={rows[-1]['z']:+.2f} "
                  f"[{time.time()-t0:.1f}s]", flush=True)
    (RESULTS / "delay_validation.json").write_text(
        json.dumps({"cells": rows, "shift_cycle": SHIFT_CYCLE}, indent=1))
    print("wrote", RESULTS / "delay_validation.json")


if __name__ == "__main__":
    main()
