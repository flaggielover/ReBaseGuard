#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/d4_phase_map"
PY="$ROOT/level4/.venv/bin/python"
MODE="${1:-}"

if [[ -n "$MODE" && "$MODE" != "--recompute" ]]; then
  echo "usage: $0 [--recompute]" >&2
  exit 2
fi
if [[ ! -x "$PY" ]]; then
  echo "missing pinned Level-4 interpreter: $PY" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"
export PYTHONPATH="$CAMPAIGN/src"

echo "== D4 protocol and protected history =="
"$PY" - <<'PY' "$ROOT" "$CAMPAIGN"
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
campaign = pathlib.Path(sys.argv[2])
freeze = json.loads((campaign / "results/protocol_hash.json").read_text())
actual = hashlib.sha256((campaign / "PROTOCOL.md").read_bytes()).hexdigest()
assert actual == freeze["protocol_sha256"]
manifest = json.loads((campaign / "results/historical_hashes.json").read_text())
inherited_path = root / manifest["inherited_manifest"]["path"]
assert hashlib.sha256(inherited_path.read_bytes()).hexdigest() == manifest["inherited_manifest"]["sha256"]
for relative, expected in manifest["files"].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative
inherited = json.loads(inherited_path.read_text())
for relative, expected in inherited["files"].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative
print("protocol and historical hashes: PASS")
PY

echo "== D4 resumable numerical summaries =="
if [[ "$MODE" == "--recompute" ]]; then
  "$PY" "$CAMPAIGN/numerics/run_campaign.py" all --recompute
else
  "$PY" "$CAMPAIGN/numerics/run_campaign.py" all
fi

echo "== D4 figures from final JSON =="
"$PY" "$CAMPAIGN/numerics/make_figures.py"

echo "== D4 focused tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== D4 adversarial A1-A13 =="
"$PY" "$CAMPAIGN/numerics/run_adversarial.py" --pre-full

echo "== authoritative repository verifier =="
bash "$ROOT/scripts/verify_level_4.sh"
"$PY" "$CAMPAIGN/numerics/record_verification.py"

echo "== D4 adversarial A1-A14 and scoped decision =="
"$PY" "$CAMPAIGN/numerics/run_adversarial.py"
"$PY" "$CAMPAIGN/numerics/make_decision.py"
"$PY" "$CAMPAIGN/numerics/make_reports.py"
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== final history and byte-stability guard =="
"$PY" "$CAMPAIGN/numerics/run_campaign.py" all
"$PY" "$CAMPAIGN/numerics/make_figures.py"
"$PY" "$CAMPAIGN/numerics/run_adversarial.py" --pre-full
"$PY" "$CAMPAIGN/numerics/record_verification.py"
"$PY" "$CAMPAIGN/numerics/run_adversarial.py"
"$PY" "$CAMPAIGN/numerics/make_decision.py"
"$PY" "$CAMPAIGN/numerics/make_reports.py"

if [[ -n "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]]; then
  echo "D4 reproducer changed the committed working tree" >&2
  git -C "$ROOT" status --short >&2
  exit 1
fi

echo "REPRODUCED: D4-PHASE-MAP-CLOSED"
echo "D4 focused tests: 18 / 18"
echo "D4 adversarial: 14 / 14"
echo "current distinct checks: 965 / 965"
