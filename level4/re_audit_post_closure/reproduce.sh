#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT="$ROOT/level4/re_audit_post_closure"
PY="$ROOT/level4/.venv/bin/python"

if [[ $# -ne 0 ]]; then
  echo "usage: $0" >&2
  exit 2
fi
if [[ ! -x "$PY" ]]; then
  echo "missing pinned Level-4 interpreter: $PY" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

STATUS_BEFORE="$(git -C "$ROOT" status --porcelain=v1)"

echo "== generated decision and reports are byte-stable =="
"$PY" "$AUDIT/src/generate_audit.py" --check

echo "== adversarial result is byte-stable and 18/18 =="
"$PY" "$AUDIT/src/adversarial.py" --check

echo "== isolated post-closure suite =="
"$PY" -m pytest "$AUDIT/tests" -q

echo "== full Level 1-3 verifier =="
bash "$ROOT/scripts/verify_level_1_3.sh"

echo "== full authoritative Level-4 verifier =="
bash "$ROOT/scripts/verify_level_4.sh"

echo "== final byte-stability and protected-history checks =="
"$PY" "$AUDIT/src/generate_audit.py" --check
"$PY" "$AUDIT/src/adversarial.py" --check

STATUS_AFTER="$(git -C "$ROOT" status --porcelain=v1)"
if [[ "$STATUS_BEFORE" != "$STATUS_AFTER" ]]; then
  echo "reproducer changed tracked or untracked repository state" >&2
  diff -u <(printf '%s\n' "$STATUS_BEFORE") <(printf '%s\n' "$STATUS_AFTER") || true
  exit 1
fi

echo "REPRODUCED: LEVEL-4-PARTIAL (post-closure derived verdict)"
echo "historical Stage F: LEVEL-4-PARTIAL (unchanged)"
echo "adversarial: 18 / 18"
echo "distinct checks: 947 / 947"
