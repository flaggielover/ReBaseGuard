#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/m_gt_1_track1a"
PY="$ROOT/level4/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "missing Level-4 Python environment: $PY" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

"$PY" -m pytest "$CAMPAIGN/tests" -q

TRACK1A_TMP="$(mktemp -d)"
trap 'rm -r -- "$TRACK1A_TMP"' EXIT
bash "$ROOT/level4/closure_proofs/m_gt_1/reproduce.sh" \
  --resume --output "$TRACK1A_TMP/previous.json"

set +e
"$PY" "$CAMPAIGN/numerics/run_replication.py" --resume
RUN_STATUS=$?
set -e

NUMERICAL_DECISION="$($PY -c 'import json, pathlib; p=pathlib.Path("'"$CAMPAIGN"'/results/replication.json"); print(json.loads(p.read_text())["verdict"]["decision"])')"
TRACK_DECISION="$($PY -c 'import json, pathlib; p=pathlib.Path("'"$CAMPAIGN"'/results/decision.json"); print(json.loads(p.read_text())["decision"])')"

if [[ "$RUN_STATUS" -eq 2 && "$NUMERICAL_DECISION" == "FAIL" \
      && "$TRACK_DECISION" == "MGT1-TRACK1A-FAILED" ]]; then
  echo "REPRODUCED: distinction PASS; frozen independent decomposition FAIL; MGT1-TRACK1A-FAILED"
  exit 0
fi

echo "unexpected reproduction status: runner=$RUN_STATUS numerical=$NUMERICAL_DECISION track=$TRACK_DECISION" >&2
exit 1

