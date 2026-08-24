#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BASE="$ROOT/level4/closure_proofs/l4r06_policy"
PY="$ROOT/level4/.venv/bin/python"
cd "$ROOT"

if [ "${1:-}" = "--recompute" ]; then
  "$PY" "$BASE/src/campaign.py" --workers "${L4R06_WORKERS:-4}" --force
  "$PY" "$BASE/src/analysis.py"
  "$PY" "$BASE/src/figures.py"
  "$PY" "$BASE/src/reproduction_check.py"
fi

"$PY" "$BASE/src/integrity.py"
"$PY" - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "level4/closure_proofs/l4r06_policy/src")
from policy import policy_table
rows = policy_table()
assert [round(row["rho"], 6) for row in rows] == [0.053642, 0.245418, 0.781994, 1.0]
print("L4R-06 P3 reconstruction: PASS")
PY
"$PY" "$BASE/src/analysis.py" --check
"$PY" "$BASE/src/figures.py" --check
"$PY" -m pytest "$BASE/tests" -q
"$PY" "$BASE/src/reproduction_check.py" --check
"$PY" "$BASE/src/adversarial.py" --check-final
bash scripts/verify_level_4.sh
"$PY" "$BASE/src/decision.py" --check
"$PY" - <<'PY'
import json
from pathlib import Path
s = json.loads(Path("level4/stage_c/results/findings.json").read_text())
assert s["decision"] == "STAGE-C-PARTIAL"
assert "C6" in s["decision_basis"]["failed"]
print("historical Stage C/C6: unchanged (STAGE-C-PARTIAL; C6 FAILED)")
PY

echo "L4R-06 REPRODUCTION OK"
