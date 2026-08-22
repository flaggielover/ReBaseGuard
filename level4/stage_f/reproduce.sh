#!/usr/bin/env bash
# Stage F closure audit. READ-ONLY with respect to every historical scientific
# artifact: it regenerates only Stage F's own outputs.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=level4/.venv/bin/python

echo "== frozen protocol + pre-commitment hashes (must be unchanged) =="
shasum -a 256 \
  level4/stage_c/STAGE_C_PROTOCOL.md \
  level4/stage_c1/STAGE_C1_PROTOCOL.md \
  level4/stage_d/STAGE_D_PROTOCOL.md \
  level4/stage_e/STAGE_E_PROTOCOL.md \
  level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md \
  level4/stage_d/notes/D2_5_PRECOMMIT.md \
  level4/stage_d/notes/D3_REGULARITY.md

echo "== Stage F adversarial suite (F1-F18) =="
$PY -u level4/stage_f/src/adversarial_f.py

echo "== final decision, derived mechanically from the requirements table =="
$PY -u level4/stage_f/src/make_final_decision.py

echo "== Stage F tests =="
$PY -m pytest level4/stage_f/tests -q

echo
echo "Stage F reproduce complete. No historical scientific artifact was written."
