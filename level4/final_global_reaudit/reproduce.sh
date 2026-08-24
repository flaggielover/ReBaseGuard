#!/usr/bin/env bash
# Offline terminal reproduction of the final global Level-4 re-audit.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE="$ROOT/level4/final_global_reaudit"
PY="$ROOT/level4/.venv/bin/python"

cd "$ROOT"
test -x "$PY"

echo "== protected historical evidence =="
"$PY" "$BASE/src/integrity.py"

echo
echo "== canonical 18-row derivation and evidence map =="
"$PY" "$BASE/src/audit.py" --check

echo
echo "== offline byte-stable audit rebuild =="
"$PY" "$BASE/src/reproduction.py" --check-run

echo
echo "== focused final-global re-audit tests =="
"$PY" -m pytest "$BASE/tests" -q

echo
echo "== final adversarial audit =="
"$PY" "$BASE/src/adversarial.py" --check

echo
echo "== required authoritative verification =="
bash "$ROOT/scripts/verify_level_1_3.sh"
bash "$ROOT/scripts/verify_level_4.sh"

echo
echo "== final generator-owned records and reports =="
"$PY" "$BASE/src/verification.py" --check-record
"$PY" "$BASE/src/reproduction.py" --check-record
"$PY" "$BASE/src/finalize.py" --check
"$PY" "$BASE/src/integrity.py"

echo
echo "FINAL GLOBAL LEVEL-4 RE-AUDIT REPRODUCTION OK"
