#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BASE="$ROOT/level4/closure_proofs/l4r12_operational_crossing"
PY="$ROOT/level4/.venv/bin/python"
cd "$ROOT"

"$PY" "$BASE/src/integrity.py"
"$PY" "$BASE/src/audit.py" --check
"$PY" -m pytest "$BASE/tests" -q
"$PY" "$BASE/src/reproduction_check.py" --check
"$PY" "$BASE/src/adversarial.py" --check-final
bash scripts/verify_level_4.sh
"$PY" "$BASE/src/decision.py" --check
"$PY" "$BASE/src/reports.py" --check
"$PY" - <<'PY'
import json
from pathlib import Path

d25 = json.loads(Path("level4/stage_d/results/d2_5_verdict.json").read_text())
d4 = json.loads(Path("level4/closure_proofs/d4_phase_map/results/decision.json").read_text())
stage_f = json.loads(Path("level4/stage_f/results/final_decision.json").read_text())
final_global = json.loads(Path("level4/final_global_reaudit/results/final_decision.json").read_text())
assert d25["verdict"] == "MATHEMATICAL, NOT OPERATIONAL"
assert d4["decision"] == "D4-PHASE-MAP-CLOSED"
assert stage_f["decision"] == "LEVEL-4-PARTIAL"
assert final_global["current_verdict"] == "LEVEL-4-PARTIAL"
print("historical D2.5, D4, Stage F, and Final Global Re-audit: unchanged")
PY

echo "L4R-12 REPRODUCTION OK"

