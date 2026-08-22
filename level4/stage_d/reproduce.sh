#!/usr/bin/env bash
# Reproduce Stage D end to end. Order matters: the SR threshold is fixed by
# D1.1 and is never revisited once any Gamma has been seen.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=level4/.venv/bin/python
S=level4/stage_d/src

echo "== protocol integrity =="
shasum -a 256 level4/stage_d/STAGE_D_PROTOCOL.md
echo "   expected 925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"

echo "== tests =="
$PY -m pytest level4/stage_d/tests/ -q

echo "== D1.1 ARL0 calibration (~4 min) =="
$PY -u $S/run_d1_calibration.py
echo "== D1.2 / D1.3 (~2 min) =="
$PY -u $S/run_d1_gamma.py
echo "== D2 Gamma_m (~1 min) =="
$PY -u $S/run_d2_gamma_m.py
echo "== D1.4 SR induced map (~1 min) =="
$PY -u $S/run_d1_4_sr_map.py
echo "== D2.3 derivative correspondence (~1 min) =="
$PY -u $S/run_d2_3_derivative.py
echo "== m=1 slope consistency check (~2 min) =="
$PY -u $S/run_d1_map_slope_check.py
echo "== D2.5 monitoring bridge (~50 min) =="
$PY -u $S/run_d2_5_bridge.py
echo "== D3 non-Gaussian (~50 min) =="
$PY -u $S/run_d3_nongaussian.py
echo "== adversarial suite (~3 min) =="
$PY -u $S/adversarial_d.py
echo "== figures =="
$PY -u $S/figures.py
echo "== decision =="
$PY -u $S/make_decision.py
