#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/sr_derivative"
PROOF_PY="$ROOT/rebaseguard-proof/.venv/bin/python"
TRACK_PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"
export PYTHONPATH="$CAMPAIGN/certificate"

CONTRACTION_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/sr_monotone_contraction.json" | awk '{print $1}')"
AUDIT_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/sr_monotone_contraction_audit.json" | awk '{print $1}')"
TAYLOR_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/sr_taylor_residual_blocker.json" | awk '{print $1}')"

"$PROOF_PY" "$CAMPAIGN/certificate/certify_sr_resolvent.py"
"$PROOF_PY" "$CAMPAIGN/certificate/audit_sr_resolvent.py"
"$PROOF_PY" "$CAMPAIGN/certificate/run_taylor_blocker_probe.py"

CONTRACTION_AFTER="$(shasum -a 256 "$CAMPAIGN/results/sr_monotone_contraction.json" | awk '{print $1}')"
AUDIT_AFTER="$(shasum -a 256 "$CAMPAIGN/results/sr_monotone_contraction_audit.json" | awk '{print $1}')"
TAYLOR_AFTER="$(shasum -a 256 "$CAMPAIGN/results/sr_taylor_residual_blocker.json" | awk '{print $1}')"
if [[ "$CONTRACTION_BEFORE" != "$CONTRACTION_AFTER" || \
      "$AUDIT_BEFORE" != "$AUDIT_AFTER" || \
      "$TAYLOR_BEFORE" != "$TAYLOR_AFTER" ]]; then
  echo "optional SR Arb artifacts are not byte-stable" >&2
  exit 1
fi

"$TRACK_PY" -m pytest \
  "$CAMPAIGN/tests/test_sr_resolvent_certificate.py" \
  "$CAMPAIGN/tests/test_sr_taylor_probe.py" -q

echo "OPTIONAL SR ARB UPGRADE: OPEN"
echo "strongest component: monotone block resolvent CERTIFIED"
echo "blocking component: global Taylor/Bernstein residual supremum OPEN"
