#!/usr/bin/env bash
# Reproduce external-validation V3 from official archives and frozen config.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BASE="$ROOT/level4/closure_proofs/external_validation_v3"
PY="$ROOT/level4/.venv/bin/python"

cd "$ROOT"
test -x "$PY"

echo "== frozen protocol and protected history =="
"$PY" "$BASE/src/integrity.py"

echo
echo "== official dataset archives =="
"$PY" "$BASE/src/acquire.py"

echo
echo "== rebuild and byte-check scientific artifacts =="
"$PY" "$BASE/src/reproduction.py" --check-run

echo
echo "== focused external-validation V3 tests =="
"$PY" -m pytest "$BASE/tests" -q

echo
echo "== final adversarial audit =="
"$PY" "$BASE/src/adversarial.py" --check

echo
echo "== authoritative repository verification =="
bash "$ROOT/scripts/verify_level_4.sh"

echo
echo "== final records and human-readable mirrors =="
"$PY" "$BASE/src/integrity.py"
"$PY" "$BASE/src/verification.py" --check-record
"$PY" "$BASE/src/reproduction.py" --check-record
"$PY" "$BASE/src/finalize.py" --check
"$PY" "$BASE/src/reports.py" --check

echo
echo "EXTERNAL VALIDATION V3 REPRODUCTION OK"
