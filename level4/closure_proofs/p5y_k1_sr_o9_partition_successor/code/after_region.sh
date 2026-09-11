#!/bin/sh
# Post-run helper (orchestration only; no science): finalize one region (T3 aggregation, T4, T5 for every child),
# report whether every child is 28/28, then compress the raw patch records deterministically (gzip -n) for commit.
# Verification later: gunzip -k chunks/rec_*.jsonl.gz and rerun `run_region.sh finalize PARENT`; the t3/t4/t5
# record hashes must reproduce.
set -eu
N=$(cd "$(dirname "$0")/.." && pwd); PARENT=$1
OUT=$N/evidence/certified/parent_$PARENT
test -z "$(ls $OUT/chunks/ | grep -v -e '^rec_' -e '^log_' -e '^patches_')" || { echo "unexpected files"; exit 1; }
$N/code/run_region.sh finalize $PARENT
python3 - "$OUT" <<'EOF'
import glob, json, sys
s = [json.load(open(f)) for f in sorted(glob.glob(sys.argv[1] + "/summary_s*.json"))]
print("children", len(s), "all_28_of_28", all(x["t5_status"] == "T5_28_OF_28_PASS" for x in s))
for x in s:
    print(x["id"], x["t5_status"], x["t5_pass_count"], {m: round(v, 4) for m, v in x["B_cover_ratio"].items()})
EOF
for f in $OUT/chunks/rec_*.jsonl; do gzip -n -9 "$f"; done
du -sh $OUT/chunks
