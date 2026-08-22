#!/usr/bin/env bash
# Reproduce Stage C end to end.
#
# Every campaign cell is checkpointed under results/cells/, keyed by a hash of
# its configuration.  Re-running is therefore cheap: completed cells are reused
# and only missing ones are computed.  Pass --force to recompute everything.
#
#   --quick   reduced replicates/cycles; exercises every code path, produces a
#             noisier (not different) answer.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="level4/.venv/bin/python"
SRC="level4/stage_c/src"

if [ ! -x "$PY" ]; then
  echo "missing $PY -- see level4/README.md for environment setup" >&2
  exit 1
fi

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

echo "== frozen regression: Level 1-3 + Stage A + Stage B =="
bash scripts/verify_level_4.sh

echo
echo "== Stage C test suite =="
"$PY" -m pytest level4/stage_c/tests -q

echo
echo "== step 1: conditional cycle-length curve A(e) =="
if [ "$QUICK" = "1" ]; then
  "$PY" "$SRC/run_arl_curve.py" 40000 0.05
else
  "$PY" "$SRC/run_arl_curve.py"
fi

echo
echo "== step 2: dense in-control rho campaign =="
if [ "$QUICK" = "1" ]; then
  "$PY" "$SRC/run_incontrol.py" --n-replicates 20 --n-cycles 1000 \
      --burn-in 200 --tag main
else
  "$PY" "$SRC/run_incontrol.py" --tag main
fi

echo
echo "== step 3: detection delay under post-change shifts =="
if [ "$QUICK" = "1" ]; then
  "$PY" "$SRC/run_detection.py" --n-replicates 500 --burn-in 60 --tag main
else
  "$PY" "$SRC/run_detection.py" --tag main
fi

echo
echo "== step 4: adversarial checks =="
"$PY" "$SRC/adversarial_c.py"

echo
echo "== step 5: criterion C9 regression evidence =="
"$PY" "$SRC/regression_check.py"

echo
echo "== step 6: criteria, Pareto frontier, findings =="
"$PY" "$SRC/run_analysis.py"

echo
echo "== step 7: figures and report =="
"$PY" "$SRC/make_report_c.py"

echo
echo "STAGE C REPRODUCTION COMPLETE"
