#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/m_gt_1_priority1"
LEAN_PROJECT="$ROOT/rebaseguard-lean"
PY="$ROOT/level4/.venv/bin/python"
WORK="$(mktemp -d)"

cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== independent frozen-CUSUM correspondence =="
"$PY" "$CAMPAIGN/numerics/run_correspondence.py"

echo "== exact finite-support Arb certificate =="
"$PY" "$CAMPAIGN/certificates/run_certificate.py"

echo "== focused campaign tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== independent Lean proof spine =="
(
  cd "$LEAN_PROJECT"
  lake env lean -R "$CAMPAIGN/lean" -o "$WORK/MGtOneClosure.olean" \
    "$CAMPAIGN/lean/MGtOneClosure.lean"
)

echo "== Lean axiom audit =="
(
  cd "$LEAN_PROJECT"
  LEAN_PATH="$WORK:$CAMPAIGN/lean:${LEAN_PATH:-}" \
    lake env lean -R "$CAMPAIGN/lean" "$CAMPAIGN/lean/AxiomAudit.lean"
) > "$WORK/axioms.txt"
"$PY" - "$WORK/axioms.txt" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
flat = " ".join(text.split())
reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
assert len(reports) == 5, reports
allowed = {"propext", "Classical.choice", "Quot.sound"}
for _, raw in reports:
    assert {x.strip() for x in raw.split(",") if x.strip()} <= allowed
assert "sorryAx" not in text
print("5 declarations; standard Mathlib axioms only")
PY

if rg -n '\b(sorry|admit|axiom)\b' "$CAMPAIGN/lean" --glob '*.lean' \
    | grep -v '#print axioms'; then
  echo "Lean bypass token found" >&2
  exit 1
fi

echo "== mechanical closure decision =="
"$PY" "$CAMPAIGN/derive_closure.py"
"$PY" - "$CAMPAIGN/results/closure_decision.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["verdict"] == "CLOSED"
assert d["all_required_gates_pass"]
assert not d["frozen_gaussian_m_gt_1_interval_certified"]
print("CLOSED: Priority-1 two-tier package; frozen Gaussian m>1 intervals excluded")
PY
