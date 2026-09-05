#!/usr/bin/env bash
# Single-shot progress summary. No polling loop; run it when you want a status.
set -euo pipefail
: "${WORKDIR:=$HOME/rebaseguard}"
: "${RUN_ID:?set RUN_ID}"
cd "$WORKDIR"
RUN=level4/closure_proofs/p5y_k1_production_driver/runs/$RUN_ID
./level4/.venv/bin/python - "$RUN" <<'PY'
import json,sys,pathlib
run=pathlib.Path(sys.argv[1]); tot=12255
st={"COMPLETE":0,"FAILED":0,"NOT_RUN":0,"NOT_IMPLEMENTED":0}; cpu=0.0
for f in run.glob("cells_shard*.jsonl"):
    for line in f.read_text().splitlines():
        if not line.strip(): continue
        try: r=json.loads(line)
        except Exception: continue
        st[r.get("status","NOT_RUN")]=st.get(r.get("status","NOT_RUN"),0)+1
        cpu+=r.get("cpu_seconds") or 0.0
done=st["COMPLETE"]
print(f"phase      : {'assembly' if (run/'assembly.json').exists() else 'production'}")
print(f"units      : {done}/{tot} complete  ({100*done/tot:.2f}%)")
print(f"failures   : {st['FAILED']}   not-implemented: {st['NOT_IMPLEMENTED']}")
print(f"CPU-hours  : {cpu/3600:.2f} of a 1126 cap")
if done: print(f"remaining  : ~{cpu/3600*(tot-done)/done:.1f} CPU-h")
PY
