#!/usr/bin/env bash
# Merge the per-family SR calibrations only after every polish pass has
# finished and every non-Gaussian family is inside the preregistered G2
# tolerance.  Refuses to merge otherwise, so the pipeline cannot start the SR
# Gamma cells on an out-of-tolerance threshold.
set -u
P8="$(cd "$(dirname "$0")/.." && pwd)"; cd "$P8"
PY=/Users/suzhe/ReBaseGuard/level4/.venv/bin/python
while pgrep -f "polish_sr_calibration.py" > /dev/null || \
      [ "$(ls results/sr_cal/*.json 2>/dev/null | wc -l | tr -d ' ')" -lt 6 ]; do
  sleep 20
done
$PY - <<'EOF'
import json, pathlib, sys
d = pathlib.Path("results/sr_cal")
bad = []
for p in sorted(d.glob("*.json")):
    c = json.loads(p.read_text())
    if c["family"] == "gaussian":
        continue
    if c["verification_relative_error"] > 0.005:
        bad.append((c["family"], c["verification_relative_error"]))
print("OUT_OF_TOLERANCE:", bad if bad else "none")
sys.exit(0)
EOF
$PY experiments/run_sr_calibration.py --merge
