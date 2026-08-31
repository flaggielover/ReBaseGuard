#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/p7_statistical_consequences"
PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== E3/E4 response curves A(x), g_m(x)  (~5 min) =="
"$PY" "$CAMPAIGN/experiments/run_response_curves.py"
"$PY" "$CAMPAIGN/experiments/run_response_tail.py"

echo "== E2/E6 chain sweep, 104 cells  (~7 min) =="
"$PY" "$CAMPAIGN/experiments/run_chain_sweep.py"

echo "== analysis =="
"$PY" "$CAMPAIGN/experiments/analyze.py"

echo "== E5 delay-identity validation =="
"$PY" "$CAMPAIGN/experiments/run_delay_validation.py"

echo "== adversarial checks =="
"$PY" "$CAMPAIGN/experiments/run_adversarial.py"

echo "== gain correspondence check against the closed campaigns =="
"$PY" "$CAMPAIGN/experiments/run_sr_gain_check.py"

echo "== report and figures =="
"$PY" "$CAMPAIGN/experiments/make_report.py"
"$PY" "$CAMPAIGN/experiments/make_figures.py"

echo "== focused P7 tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q
