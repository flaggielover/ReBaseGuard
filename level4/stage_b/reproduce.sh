#!/usr/bin/env bash
# Reproduce the Stage B period-2 certificate end to end.
#
# Runtime is dominated by the certified Arb mesh run (~45 min on the machine
# this was developed on).  Pass --quick to run the reduced-grid version, which
# exercises every code path but produces a wider (and therefore weaker, not
# wrong) certificate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="level4/.venv/bin/python"
SRC="level4/stage_b/src"

if [ ! -x "$PY" ]; then
  echo "missing $PY -- see level4/README.md for environment setup" >&2
  exit 1
fi

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

echo "== Stage B test suite =="
"$PY" -m pytest level4/stage_b/tests -q

echo
echo "== frozen Level 1-3 regression =="
( cd rebaseguard-proof && ".venv/bin/python" -m pytest -q )

echo
if [ "$QUICK" = "1" ]; then
  echo "== certified mesh certificate (QUICK: reduced grid) =="
  "$PY" "$SRC/run_stage_b.py" --backend arb --bits 96 \
      --n-axis 160 --n-tri 26 --radius 0.020 --spacing 0.002 --tag quick
else
  echo "== certified mesh certificate (primary) =="
  "$PY" "$SRC/run_stage_b.py" --backend arb --bits 96 \
      --n-axis 400 --n-tri 60 --radius 0.012 --spacing 0.001 --tag primary
fi

echo
echo "== B8 independent cross-checks =="
"$PY" "$SRC/cross_check.py"

echo
echo "== B9 adversarial falsification attempts =="
"$PY" "$SRC/adversarial.py"

echo
echo "== assemble certificate and report =="
"$PY" "$SRC/make_certificate.py"

echo
echo "STAGE B REPRODUCTION COMPLETE"
