#!/usr/bin/env bash
# Reproduce Stage E end to end. Raw datasets are fetched, never redistributed.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=level4/.venv/bin/python
S=level4/stage_e/src
C=level4/stage_e/data/_cache
mkdir -p "$C"

echo "== protocol integrity =="
shasum -a 256 level4/stage_e/STAGE_E_PROTOCOL.md
echo "   expected 974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc"

echo "== fetch datasets (skipped if cached) =="
[ -f "$C/electricity-normalized.arff" ] || curl -sL --max-time 300 -o "$C/electricity-normalized.arff" \
  "https://api.openml.org/data/v1/download/2419/electricity-normalized.arff"
[ -f "$C/AirQualityUCI.csv" ] || { curl -sL --max-time 300 -o "$C/air_quality.zip" \
  "https://archive.ics.uci.edu/static/public/360/air+quality.zip" && unzip -oq "$C/air_quality.zip" -d "$C"; }
[ -f "$C/hour.csv" ] || { curl -sL --max-time 300 -o "$C/bike_sharing.zip" \
  "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip" && unzip -oq "$C/bike_sharing.zip" -d "$C"; }
shasum -a 256 "$C/electricity-normalized.arff" "$C/AirQualityUCI.csv" "$C/hour.csv"

echo "== confirmatory campaigns (k fixed per task by the frozen spacing rule) =="
$PY -u $S/run_task.py electricity  --k 120
$PY -u $S/run_task.py air_quality  --k 24
$PY -u $S/run_task.py bike_sharing --k 46

echo "== per-task hypothesis analysis =="
for t in electricity air_quality bike_sharing; do
  $PY -u $S/analyze_task.py task_${t}_confirmatory.json
done

echo "== figures (from results JSON only) =="
$PY -u $S/figures_e.py
echo "== adversarial suite =="
$PY -u $S/adversarial_e.py
echo "== frozen decision rule =="
$PY -u $S/make_decision_e.py
echo "== tests =="
$PY -m pytest level4/stage_e/tests -q
