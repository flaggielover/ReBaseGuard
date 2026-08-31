#!/usr/bin/env bash
# Deterministic P5 reproduction.  Total wall time ~55 min single-core.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
C="$ROOT/level4/closure_proofs/p5_nonlinear_dynamics"
PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

echo "== E1  conditional-mean map R(e), primary seed family 20260501  (~6 min) =="
"$PY" "$C/experiments/run_nonlinear_map.py"
echo "== E1b far tail |e| in [5.5, 24]  (~1 min) =="
"$PY" "$C/experiments/run_map_tail.py"
echo "== E1r independent replication, seed family 20261119  (~6 min) =="
"$PY" "$C/experiments/run_nonlinear_map.py" --seed-family 20261119 --tag 2 \
      --out nonlinear_map_rep.json

echo "== analysis of the map and of the conditional-theorem hypotheses =="
"$PY" "$C/experiments/analyze_map.py"
"$PY" "$C/experiments/analyze_map.py" nonlinear_map_rep.json map_analysis_rep.json
"$PY" "$C/experiments/audit_hypotheses.py"

echo "== E3  deterministic skeleton scan, 199 rho x 84 initial conditions (~1 min) =="
"$PY" "$C/experiments/run_skeleton.py"

echo "== E2  chain sweep, 176 cells x 240 replicates x 2000 cycles  (~32 min) =="
"$PY" "$C/experiments/run_chain.py"

echo "== E5  runaway stress test  (~3 min) =="
"$PY" "$C/experiments/run_stress.py"

echo "== E6  stationary density and bimodality onset  (~7 min) =="
"$PY" "$C/experiments/run_density.py"
"$PY" "$C/experiments/run_density.py" --crossover --tag 55 --out density_crossover.json

echo "== analysis, onset, figures =="
"$PY" "$C/experiments/analyze_chain.py"
"$PY" "$C/experiments/make_onset.py"
"$PY" "$C/experiments/make_figures.py"

echo "== Lean skeleton spine + axiom audit  (~3 min) =="
"$PY" "$C/run_lean.py"

echo "== independent adjudication replay (~10 sec) =="
"$PY" "$C/experiments/independent_adjudication.py"

echo "== provenance =="
"$PY" "$C/experiments/make_provenance.py"

echo "== focused tests =="
"$PY" -m pytest "$C/tests" -q
