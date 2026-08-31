#!/usr/bin/env python3
"""E1b: far-tail extension of R(e), to test the saturation claim R(e) -> 0."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, SEED_FAMILY                  # noqa: E402
from rebaseguard_p5.kernel import raw_map_point                  # noqa: E402

MAGS = (5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 10.0, 12.0, 16.0, 24.0)
M_GRID = (1, 2, 3, 5)

rows = []
for det in ("cusum", "sr"):
    for i, mag in enumerate(MAGS):
        for s in (1.0, -1.0):
            e = s * mag
            r = raw_map_point(detector=det, e=e, m_grid=M_GRID,
                              n_paths=400_000, n_batches=8,
                              seed_family=SEED_FAMILY, tag=7000 + 2 * i + int(s < 0))
            rows.append(r)
            print(f"{det} e={e:+7.2f} A={r['tau_mean']:6.3f} "
                  f"p(tau=1)={r['p_tau1']:.4f} R1={r['per_m'][0]['R']:+.5f}"
                  f" +/-{1.96*r['per_m'][0]['R_se']:.5f}", flush=True)
(RESULTS / "map_tail.json").write_text(json.dumps(
    {"seed_family": SEED_FAMILY, "m_grid": list(M_GRID), "rows": rows}, indent=1))
print("wrote map_tail.json")
