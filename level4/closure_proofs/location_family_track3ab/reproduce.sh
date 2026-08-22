#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/location_family_track3ab"
PY="$ROOT/level4/.venv/bin/python"
LEAN_PROJECT="$ROOT/rebaseguard-lean"
LEAN_DIR="$CAMPAIGN/lean"

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

echo "== immutable Track-3A/3B hashes and focused tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== retained numerical checkpoint audit =="
AUDIT_BEFORE="$(shasum -a 256 "$CAMPAIGN/results/numerical_audit.json" | awk '{print $1}')"
"$PY" "$CAMPAIGN/numerics/audit_numerical.py"
AUDIT_AFTER="$(shasum -a 256 "$CAMPAIGN/results/numerical_audit.json" | awk '{print $1}')"
if [[ "$AUDIT_BEFORE" != "$AUDIT_AFTER" ]]; then
  echo "numerical audit is not byte-stable" >&2
  exit 1
fi

echo "== historical closure-track suites =="
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1a/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/m_gt_1_track1b/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/sr_derivative/tests" -q
"$PY" -m pytest "$ROOT/level4/closure_proofs/location_family/tests" -q

echo "== Track-3B Lean compile =="
LEAN_TMP="$(mktemp -d "${TMPDIR:-/tmp}/rebaseguard-track3ab-lean.XXXXXX")"
(
  cd "$LEAN_PROJECT"
  lake env lean -R "$LEAN_DIR" -o "$LEAN_TMP/LocationFamilyTrack3AB.olean" \
    "$LEAN_DIR/LocationFamilyTrack3AB.lean"
)

echo "== theorem-by-theorem axiom audit =="
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
if rg -n '\b(sorry|admit|axiom)\b' "$LEAN_DIR/LocationFamilyTrack3AB.lean"; then
  echo "Lean bypass or project axiom token found" >&2
  exit 1
fi

echo "== authoritative repository verifier =="
bash "$ROOT/scripts/verify_level_4.sh"

echo "== final scoped decision and clean tree =="
"$PY" - <<'PY' "$CAMPAIGN"
import json
import pathlib
import sys

campaign = pathlib.Path(sys.argv[1])
decision = json.loads((campaign / "results/decision.json").read_text())
historical = json.loads(
    (campaign.parent / "location_family/results/decision.json").read_text()
)
assert decision["decision"] == "LOCATION-FAMILY-TRACK3AB-CLOSED"
assert decision["general_location_family_theorem_requirement"] == "CLOSED"
assert decision["verification"]["combined_checks"] == 929
assert decision["global_level4_reaudit_performed"] is False
assert historical["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
print("final decision and historical preservation: PASS")
PY

if ! git -C "$ROOT" diff --quiet || ! git -C "$ROOT" diff --cached --quiet; then
  echo "reproducer changed tracked files" >&2
  exit 1
fi

echo "REPRODUCED: LOCATION-FAMILY-TRACK3AB-CLOSED"
echo "general location-family theorem: CLOSED"
echo "historical Track 3: LOCATION-FAMILY-THEOREM-PARTIAL (unchanged)"
echo "checks: 929 / 929"
