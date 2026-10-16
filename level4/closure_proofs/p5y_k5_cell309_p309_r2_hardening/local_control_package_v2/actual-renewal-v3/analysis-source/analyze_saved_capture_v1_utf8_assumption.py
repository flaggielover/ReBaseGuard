import csv, json, hashlib, sys, platform
from collections import Counter
from pathlib import Path
root=Path(sys.argv[1])
out=root/"offline"
fixtures={int(r["pid"]):r for r in map(json.loads,(root/"capture"/"guard.jsonl").read_text(encoding="utf-8-sig").splitlines()) if "job_total" in r}
csv_path=out/"events.csv"
with csv_path.open("rb") as f: prefix=f.read(4)
encoding="utf-16" if prefix.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig"
counts=Counter(); samples={}; related=[]; first=None; last=None; total=0
with csv_path.open("r",encoding=encoding,newline="") as f:
    reader=csv.reader(f,skipinitialspace=True)
    header=next(reader)
    for row in reader:
        total+=1
        if len(row)<19: raise ValueError(f"short event row {total}")
        key="|".join(row[i].strip() for i in (0,1,3))
        counts[key]+=1
        if key not in samples: samples[key]=row
        stamp=int(row[16].strip())
        first=stamp if first is None else min(first,stamp)
        last=stamp if last is None else max(last,stamp)
        # Preserve candidate lifecycle records only. Never infer process ownership
        # from an arbitrary PID-shaped token; inspect schema in the next pass.
        if row[0].strip() in ("Process","Thread","Image"):
            vals={v.strip() for v in row[19:25]}
            hits=[pid for pid in fixtures if str(pid) in vals or f"0x{pid:08X}" in vals or f"0x{pid:X}" in vals]
            if hits: related.append({"candidate_pids":hits,"row":row})
summary={"scope":"OFFLINE_TRACERPT_CSV_STRUCTURE_ONLY_NOT_ADMISSION","python":sys.version,
"python_executable":sys.executable,"platform":platform.platform(),"private_cpython_substitution":False,
"analysis_runtime_only":True,"csv_encoding":encoding,"events":total,"first_clock":first,"last_clock":last,
"clock_span_100ns":last-first,"counts":dict(sorted(counts.items())),
"fixture_pids":list(fixtures),"candidate_lifecycle_records":len(related),"admission":"BLOCKED"}
(out/"EVENT_STRUCTURE_ANALYSIS.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(out/"PRIVATE_SCHEMA_SAMPLES.json").write_text(json.dumps(samples,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(out/"PRIVATE_FIXTURE_CANDIDATES.json").write_text(json.dumps(related,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))
