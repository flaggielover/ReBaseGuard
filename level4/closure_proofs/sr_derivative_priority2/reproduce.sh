#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/sr_derivative_priority2"
PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== dual immutable SR history manifests =="
"$PY" "$CAMPAIGN/history/generate_manifests.py"

echo "== independent frozen-Gaussian SR correspondence =="
"$PY" "$CAMPAIGN/numerics/run_correspondence.py"

echo "== exact finite-support SR Arb certificate =="
"$PY" "$CAMPAIGN/certificates/run_certificate.py"

echo "== focused Priority-2 tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== Lean proof spine and axiom audit =="
"$PY" "$CAMPAIGN/run_lean.py"

echo "== repository regression suites and historical diagnostics =="
"$PY" "$CAMPAIGN/run_repository_verification.py"

echo "== mechanical Priority-2 closure decision =="
"$PY" "$CAMPAIGN/derive_closure.py"
"$PY" - "$CAMPAIGN/results/closure_decision.json" <<'PY'
import json, sys
d=json.load(open(sys.argv[1]))
assert d["verdict"] == "CLOSED"
assert d["all_required_gates_pass"]
assert not d["frozen_infinite_horizon_gaussian_sr_m_gt_1_interval_certified"]
print("Level-4 Priority 2 -- CLOSED; frozen Gaussian SR intervals excluded")
PY
