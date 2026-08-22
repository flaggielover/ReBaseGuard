#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/m_gt_1_track1b"
LEAN_PROJECT="$ROOT/rebaseguard-lean"
LEAN_DIR="$CAMPAIGN/lean"
LEAN_OBJECT="$LEAN_DIR/MGtOneTrack1B.olean"
AXIOM_OUTPUT="$CAMPAIGN/results/axiom_audit.reproduced.txt"
PY="$ROOT/level4/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "missing Level-4 Python environment: $PY" >&2
  exit 1
fi

cleanup() {
  rm -f -- "$LEAN_OBJECT"
  rm -f -- "$AXIOM_OUTPUT"
}
trap cleanup EXIT

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== historical Track 1 and Track 1A =="
bash "$ROOT/level4/closure_proofs/m_gt_1_track1a/reproduce.sh"

echo "== Track 1B isolated tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== frozen numerical result =="
"$PY" "$CAMPAIGN/numerics/run_replication.py" --resume

echo "== Lean compile =="
(
  cd "$LEAN_PROJECT"
  lake env lean -R "$LEAN_DIR" -o "$LEAN_OBJECT" "$LEAN_DIR/MGtOneTrack1B.lean"
)

echo "== Lean axiom audit =="
(
  cd "$LEAN_PROJECT"
  lake env env TRACK1B_LEAN_DIR="$LEAN_DIR" zsh -c \
    'LEAN_PATH="$TRACK1B_LEAN_DIR:$LEAN_PATH" lean -R "$TRACK1B_LEAN_DIR" "$TRACK1B_LEAN_DIR/AxiomAudit.lean"'
) | tee "$AXIOM_OUTPUT"

if [[ "$(grep -c "depends on axioms" "$AXIOM_OUTPUT")" -ne 4 ]]; then
  echo "unexpected number of axiom declarations" >&2
  exit 1
fi
if grep -vE "depends on axioms|propext|Classical.choice|Quot.sound|^[[:space:]]*$" \
    "$AXIOM_OUTPUT" | grep -q .; then
  echo "unexpected axiom audit output" >&2
  exit 1
fi
rm -f -- "$AXIOM_OUTPUT"

if rg -n "\b(sorry|admit|axiom)\b" "$LEAN_DIR" --glob '*.lean' \
    | grep -v '#print axioms'; then
  echo "Lean bypass token found" >&2
  exit 1
fi

echo "REPRODUCED: MGT1-TRACK1B numerical and Lean evidence"
