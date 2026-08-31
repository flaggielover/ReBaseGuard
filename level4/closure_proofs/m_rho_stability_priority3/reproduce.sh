#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/m_rho_stability_priority3"
PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== provenance, map, figures and report from the closed P1/P2 artifacts =="
"$PY" "$CAMPAIGN/scripts/build_map.py"

echo "== rigorous finite-support Arb certification of the map boundaries =="
"$PY" "$CAMPAIGN/arb/run_certificate.py"

echo "== focused Priority-3 tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q

echo "== Lean synthesis spine and axiom audit =="
"$PY" "$CAMPAIGN/run_lean.py"

echo "== repository regression suites and historical diagnostics =="
"$PY" "$CAMPAIGN/run_repository_verification.py"

echo "== mechanical Priority-3 closure decision =="
"$PY" "$CAMPAIGN/derive_closure.py"
"$PY" - "$CAMPAIGN/results/closure_decision.json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["verdict"] == "CLOSED", d["verdict"]
assert d["all_required_gates_pass"]
assert not d["frozen_infinite_horizon_gaussian_gains_interval_certified"]
assert not d["global_or_nonlinear_stability_claimed"]
assert not d["detector_universal_stability_claimed"]
print("Level-4 Priority 3 -- CLOSED; Gaussian gains remain empirical")
PYEOF
