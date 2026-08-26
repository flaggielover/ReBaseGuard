#!/usr/bin/env bash
# Offline terminal reproduction of the final Level-4 closure audit.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE="$ROOT/level4/final_level4_closure"
PY="$ROOT/level4/.venv/bin/python"

cd "$ROOT"
test -x "$PY"

echo "== protected historical evidence =="
"$PY" "$BASE/src/integrity.py"

echo
echo "== canonical 18-row source and mapped evidence =="
"$PY" "$BASE/src/audit.py" --check
"$PY" "$BASE/src/reports.py" --check

echo
echo "== offline byte-stable regeneration =="
"$PY" "$BASE/src/reproduction.py" --check-run

echo
echo "== focused terminal closure tests =="
"$PY" -m pytest "$BASE/tests" -q

echo
echo "== final A1-A32 adversarial suite =="
"$PY" "$BASE/src/adversarial.py" --check

echo
echo "== authoritative repository verification =="
bash "$ROOT/scripts/verify_level_1_3.sh"
bash "$ROOT/scripts/verify_level_4.sh"

echo
echo "== generator-owned final records =="
"$PY" "$BASE/src/verification.py" --check-record
"$PY" "$BASE/src/reproduction.py" --check-record
"$PY" "$BASE/src/finalize.py" --check
"$PY" "$BASE/src/integrity.py"

echo
echo "FINAL LEVEL-4 CLOSURE REPRODUCTION OK"
