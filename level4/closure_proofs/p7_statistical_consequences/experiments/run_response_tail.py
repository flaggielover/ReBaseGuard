"""Extends the response-curve grid into the far tail.

The delay identity evaluates ``A(e - Delta)`` and the heaviest cells (m=1,
rho=1, where the next reference is essentially the alarm-triggering observation)
put a few percent of mass beyond |x| = 3.  Clamping there biased the identity
upward by up to 6%.  The tail points are cheap -- the run length is 2 to 3 steps
-- so the grid is extended rather than the bias tolerated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD   # noqa: E402
from rebaseguard_p7.config import (                                   # noqa: E402
    DETECTOR_CODE, M_GRID, RESULTS, SEED_FAMILY)
from rebaseguard_p7.cycles import run_cycle_batches                   # noqa: E402

TAIL = [3.5, 4.0, 5.0, 6.0, 8.0, 12.0]
N = 200_000


def main() -> None:
    path = RESULTS / "response_curves.json"
    out = json.loads(path.read_text())
    have = {round(r["x"], 6) for r in out["curves"]["cusum"]}
    for det, thr in ((CUSUM, CUSUM_THRESHOLD), (SR, SR_THRESHOLD)):
        for x in TAIL:
            if round(x, 6) in have and det == CUSUM:
                continue
            ss = np.random.SeedSequence([SEED_FAMILY, 3, DETECTOR_CODE[det], 0,
                                         int(round(abs(x) * 1e6))])
            cs = run_cycle_batches(detector=det, e=x, n_paths=N,
                                   m_grid=M_GRID, seed_seq=ss, threshold=thr)
            tau = cs.tau.astype(float)
            row = {"x": x, "n": N, "arl": float(tau.mean()),
                   "arl_se": float(tau.std(ddof=1) / np.sqrt(N)),
                   "arl_median": float(np.median(tau)),
                   "p_up": float(cs.up.mean()), "g": {}, "g_se": {},
                   "var_zbar": {}, "symmetry_check": False}
            for m in M_GRID:
                zb = cs.zbar_for(m)
                row["g"][str(m)] = float(zb.mean())
                row["g_se"][str(m)] = float(zb.std(ddof=1) / np.sqrt(N))
                row["var_zbar"][str(m)] = float(zb.var(ddof=1))
            out["curves"][det].append(row)
            print(f"{det} x={x:5.1f} ARL={row['arl']:7.3f} "
                  f"g1={row['g']['1']:+.4f} h1={row['g']['1']+x:+.4f}", flush=True)
    out["tail_extension"] = {"x": TAIL, "n": N}
    path.write_text(json.dumps(out, indent=1))
    print("extended", path)


if __name__ == "__main__":
    main()
