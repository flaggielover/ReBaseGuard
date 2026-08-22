#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/location_family"
PY="$ROOT/level4/.venv/bin/python"

if [[ $# -ne 0 ]]; then
  echo "usage: $0" >&2
  exit 2
fi
if [[ ! -x "$PY" ]]; then
  echo "missing pinned interpreter: $PY" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"
export CAMPAIGN_PATH="$CAMPAIGN"

echo "== historical closure-track suites =="
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1a/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1b/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/sr_derivative/tests" -q

echo "== Track-3 retained artifacts and tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== retained numerical correspondence audit =="
AUDIT_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/numerical_audit.json" | awk '{print $1}')"
"$PY" "$CAMPAIGN/numerics/audit_numerical.py"
AUDIT_AFTER="$(shasum -a 256 "$CAMPAIGN/results/numerical_audit.json" | awk '{print $1}')"
if [[ "$AUDIT_BEFORE" != "$AUDIT_AFTER" ]]; then
  echo "retained numerical audit is not byte-stable" >&2
  exit 1
fi

echo "== Lean gate =="
"$PY" - <<'PY'
import json
import os
from pathlib import Path

campaign = Path(os.environ["CAMPAIGN_PATH"])
decision = json.loads((campaign / "results/numerical_decision.json").read_text())
assert decision["status"] == "LOCATION-FAMILY-NUMERICAL-FAILED"
assert decision["lean_authorized"] is False
assert not (campaign / "lean").exists()
print("Lean correctly NOT AUTHORIZED / NOT RUN")
PY

echo "== authoritative historical verifier =="
bash "$ROOT/scripts/verify_level_4.sh"

echo "REPRODUCED: LOCATION-FAMILY-THEOREM-PARTIAL"
echo "numerical gate: LOCATION-FAMILY-NUMERICAL-FAILED"
echo "Lean: NOT AUTHORIZED / NOT RUN"

