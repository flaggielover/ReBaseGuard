#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/sr_derivative"
LEAN_PROJECT="$ROOT/rebaseguard-lean"
LEAN_DIR="$CAMPAIGN/lean"
PY="$ROOT/level4/.venv/bin/python"
PROOF_PY="$ROOT/rebaseguard-proof/.venv/bin/python"
RUN_FULL=false

if [[ "${1:-}" == "--full" ]]; then
  RUN_FULL=true
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--full]" >&2
  exit 2
fi

for interpreter in "$PY" "$PROOF_PY"; do
  if [[ ! -x "$interpreter" ]]; then
    echo "missing interpreter: $interpreter" >&2
    exit 1
  fi
done

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== isolated historical closure-track suites =="
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1a/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1b/tests" -q

echo "== Track-2 retained artifacts and scoped tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== Arb OPEN-attempt independent audit =="
ARB_AUDIT_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/arb_attempt_audit.json" | awk '{print $1}')"
"$PROOF_PY" "$CAMPAIGN/certificate/audit_arb_attempt.py"
ARB_AUDIT_AFTER="$(shasum -a 256 "$CAMPAIGN/results/arb_attempt_audit.json" | awk '{print $1}')"
if [[ "$ARB_AUDIT_BEFORE" != "$ARB_AUDIT_AFTER" ]]; then
  echo "Arb OPEN-attempt audit is not byte-stable" >&2
  exit 1
fi

echo "== Lean compile =="
LEAN_TMP="$(mktemp -d "${TMPDIR:-/tmp}/rebaseguard-sr-lean.XXXXXX")"
(
  cd "$LEAN_PROJECT"
  lake env lean -R "$LEAN_DIR" -o "$LEAN_TMP/SRDerivative.olean" \
    "$LEAN_DIR/SRDerivative.lean"
)

echo "== Lean axiom audit =="
AXIOM_OUTPUT="$( (
  cd "$LEAN_PROJECT"
  LEAN_PATH="$LEAN_TMP:${LEAN_PATH:-}" lake env lean -R "$LEAN_DIR" \
    "$LEAN_DIR/AxiomAudit.lean"
) 2>&1)"
printf '%s\n' "$AXIOM_OUTPUT"
if ! diff -u "$CAMPAIGN/results/axiom_audit.txt" \
    <(printf '%s\n' "$AXIOM_OUTPUT"); then
  echo "Lean axiom audit changed" >&2
  exit 1
fi
if rg -n '\b(sorry|admit|axiom)\b' "$LEAN_DIR/SRDerivative.lean"; then
  echo "Lean bypass token found" >&2
  exit 1
fi

if [[ "$RUN_FULL" == true ]]; then
  echo "== authoritative full repository verifier =="
  bash "$ROOT/scripts/verify_level_4.sh"
fi

echo "REPRODUCED: SR derivative theorem evidence"
echo "Gamma_SR > 2: CONFIRMATORY NUMERICAL ONLY"
echo "rigorous SR local-instability certificate: OPEN"
