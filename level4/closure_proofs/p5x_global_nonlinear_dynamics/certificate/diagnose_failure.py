"""Attribute the single-cell stop-gate outcome.  Diagnostics, not a certificate.

Collapsing the e-ball to its midpoint (`diagnostic_radius = 0`) isolates the
drift-dependence of the enclosure from the *continuum-in-e* handling, which is
the only thing that differs between a point evaluation and a cell.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
from drift_certificate import certify_cell            # noqa: E402

CELL = (0.24, 0.26)


def main() -> None:
    rows = []
    for radius in (0.0, 1e-8):
        t = time.time()
        rec = certify_cell(e_lo=CELL[0], e_hi=CELL[1], diagnostic_radius=radius)
        rows.append({
            "e_ball_radius": radius,
            "polynomial_residual": rec["polynomial_residual"]["ball"],
            "delta": rec["delta"]["ball"],
            "resolvent_bound": rec["resolvent"]["bound"]["ball"],
            "R_enclosure": rec["R_enclosure"]["ball"],
            "half_width": rec["achieved_half_width"],
            "wall_seconds": time.time() - t,
        })
        print(json.dumps(rows[-1], indent=1), flush=True)
    out = {
        "schema": "rebaseguard.p5x.stop-gate-diagnosis.v1",
        "role": "DIAGNOSTIC ONLY; a point e is not a certified cell enclosure",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cell": list(CELL),
        "rows": rows,
    }
    (NS / "results" / "stop_gate_diagnosis.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
