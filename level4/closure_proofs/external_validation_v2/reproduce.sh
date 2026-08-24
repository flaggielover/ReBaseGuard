#!/usr/bin/env bash
# Reproduce external-validation V2 from official archives and frozen config.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BASE="$ROOT/level4/closure_proofs/external_validation_v2"
PY="$ROOT/level4/.venv/bin/python"

cd "$ROOT"
test -x "$PY"

echo "== frozen protocol and protected history =="
"$PY" "$BASE/src/integrity.py"

echo
echo "== official dataset archives =="
"$PY" "$BASE/src/acquire.py"

echo
echo "== rebuild calibration, outcomes, statistics, reports, and figures =="
"$PY" "$BASE/src/reproduction.py" --check-run

echo
echo "== focused external-validation V2 tests =="
"$PY" -m pytest "$BASE/tests" -q

echo
echo "== final adversarial audit =="
"$PY" "$BASE/src/adversarial.py" --check

echo
echo "== authoritative repository verification =="
bash "$ROOT/scripts/verify_level_4.sh"

echo
echo "== final integrity and byte record =="
"$PY" "$BASE/src/integrity.py"
"$PY" "$BASE/src/reports.py" --check
"$PY" "$BASE/src/reproduction.py" --check-record

echo
echo "EXTERNAL VALIDATION V2 REPRODUCTION OK"
