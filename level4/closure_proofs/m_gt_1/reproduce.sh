#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/m_gt_1"
PY="$ROOT/level4/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "missing Level-4 Python environment: $PY" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

"$PY" -m pytest "$CAMPAIGN/tests" -q

set +e
"$PY" "$CAMPAIGN/numerics/run_correspondence.py" "$@"
RUN_STATUS=$?
set -e

if [[ " $* " == *" --quick "* ]]; then
  exit "$RUN_STATUS"
fi

DECISION="$($PY -c 'import json, pathlib; p=pathlib.Path("'"$CAMPAIGN"'/results/correspondence.json"); print(json.loads(p.read_text())["verdict"]["decision"])')"
if [[ "$RUN_STATUS" -eq 2 && "$DECISION" == "FAIL" ]]; then
  echo "REPRODUCED: frozen numerical gate FAIL; proof-track decision MGT1-THEOREM-PARTIAL"
  exit 0
fi

echo "unexpected reproduction status: command=$RUN_STATUS decision=$DECISION" >&2
exit 1
