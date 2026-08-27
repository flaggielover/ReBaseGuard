#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/sr_derivative"
PROOF_PY="$ROOT/rebaseguard-proof/.venv/bin/python"
TRACK_PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"
export PYTHONPATH="$CAMPAIGN/certificate"

artifacts=(
  sr_monotone_contraction.json
  sr_monotone_contraction_audit.json
  sr_residual_global_a_checkpoint.json
  sr_residual_global_a.json
  sr_residual_global_b_checkpoint.json
  sr_residual_global_b.json
)

before="$(mktemp "${TMPDIR:-/tmp}/rebaseguard-sr-closed-before.XXXXXX")"
after="$(mktemp "${TMPDIR:-/tmp}/rebaseguard-sr-closed-after.XXXXXX")"
trap 'rm -f "$before" "$after"' EXIT

for artifact in "${artifacts[@]}"; do
  shasum -a 256 "$CAMPAIGN/results/$artifact" >> "$before"
done

"$PROOF_PY" "$CAMPAIGN/certificate/certify_sr_resolvent.py"
"$PROOF_PY" "$CAMPAIGN/certificate/audit_sr_resolvent.py"
"$PROOF_PY" "$CAMPAIGN/certificate/certify_global_residual_a.py" --workers 1
"$PROOF_PY" "$CAMPAIGN/certificate/audit_global_residual_a.py"
"$PROOF_PY" "$CAMPAIGN/certificate/certify_global_residual_b.py" --workers 1
"$PROOF_PY" "$CAMPAIGN/certificate/audit_global_residual_b.py"

for artifact in "${artifacts[@]}"; do
  shasum -a 256 "$CAMPAIGN/results/$artifact" >> "$after"
done
if ! diff -u "$before" "$after"; then
  echo "closed SR Arb artifacts are not byte-stable" >&2
  exit 1
fi

"$TRACK_PY" -m pytest \
  "$CAMPAIGN/tests/test_sr_resolvent_certificate.py" \
  "$CAMPAIGN/tests/test_sr_adaptive_residual.py" -q

echo "OPTIONAL SR ARB UPGRADE: CLOSED"
echo "rigorous SR local-instability certificate: SR-GAMMA-CERTIFIED"
