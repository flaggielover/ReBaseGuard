#!/usr/bin/env bash
# Reproduce Stage C.1 end to end.
#
# Cells are checkpointed by config hash, so a rerun reuses completed work.
# --quick runs a reduced version that exercises every code path.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="level4/.venv/bin/python"
SRC="level4/stage_c1/src"

[ -x "$PY" ] || { echo "missing $PY -- see level4/README.md" >&2; exit 1; }

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

echo "== frozen regression: Level 1-3 + Stage A + Stage B + Stage C =="
bash scripts/verify_level_4.sh

echo
echo "== Stage C.1 test suite (includes the protocol-hash check) =="
"$PY" -m pytest level4/stage_c1/tests -q

echo
echo "== step 1: confirmatory campaign (seed 20260901) =="
if [ "$QUICK" = "1" ]; then
  "$PY" "$SRC/run_confirmatory.py" --n-replicates 100 --n-events 40 --tag quick
  "$PY" "$SRC/run_analysis_c1.py" --tag quick
else
  "$PY" "$SRC/run_confirmatory.py"
  echo
  echo "== step 2: adversarial checks =="
  "$PY" "$SRC/adversarial_c1.py"
  echo
  echo "== step 3: analysis and decision =="
  "$PY" "$SRC/run_analysis_c1.py"
  echo
  echo "== step 4: figures, ledger and report =="
  "$PY" "$SRC/make_report_c1.py"
fi

echo
echo "STAGE C.1 REPRODUCTION COMPLETE"
