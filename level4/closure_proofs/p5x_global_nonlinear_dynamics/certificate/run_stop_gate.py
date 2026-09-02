"""Run the P5X single-cell certified stop-gate exactly as STOP_GATE_SPEC.md declares."""
from __future__ import annotations

import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))

from drift_certificate import certify_cell            # noqa: E402

# Frozen in STOP_GATE_SPEC.md before the run; do not edit after a result exists.
CELL = (0.24, 0.26)
THRESHOLD = 0.2


def main() -> None:
    import flint
    t0 = time.time()
    c0 = time.process_time()
    payload = certify_cell(e_lo=CELL[0], e_hi=CELL[1])
    wall = time.time() - t0
    cpu = time.process_time() - c0
    usage = resource.getrusage(resource.RUSAGE_SELF)
    half = payload["achieved_half_width"]
    payload.update({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "runtime": {
            "wall_seconds": wall,
            "cpu_seconds": cpu,
            "peak_rss_bytes": usage.ru_maxrss,
            "peak_rss_mib": usage.ru_maxrss / (1024 * 1024),
        },
        "stop_gate": {
            "frozen_threshold": THRESHOLD,
            "achieved_half_width": half,
            "verdict": "PASS" if half <= THRESHOLD else "FAIL",
            "rule": "STOP_GATE_SPEC.md section 6; not reinterpretable",
        },
    })
    out = NS / "results" / "stop_gate_cell.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("target", "e_cell", "R_enclosure", "interval_width",
                       "achieved_half_width", "polynomial_residual", "delta",
                       "resolvent", "runtime", "stop_gate")}, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
