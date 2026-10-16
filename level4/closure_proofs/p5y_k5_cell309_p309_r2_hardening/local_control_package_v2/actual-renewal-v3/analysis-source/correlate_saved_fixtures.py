import csv,json,sys,collections
from pathlib import Path
r=Path(sys.argv[1]); out=r/"offline"
fixtures={int(v["pid"]):v for v in map(json.loads,(r/"capture/guard.jsonl").read_text().splitlines()) if "job_total" in v}
candidates=json.loads((out/"PRIVATE_FIXTURE_CANDIDATES.json").read_text(encoding="utf-8"))
def number(s): return int(s.strip(),16) if s.strip().startswith("0x") else int(s.strip())
facts={}
for pid,g in fixtures.items():
    process=[]; starts={}; ends={}; images=0
    for candidate in candidates:
        row=candidate["row"]; kind=row[0].strip(); op=row[1].strip()
        if kind=="Process" and op in ("Start","End") and number(row[20])==pid:
            process.append({"opcode":op,"clock":int(row[16]),"key":row[19],"pid":pid,"parent_pid":number(row[21]),"image":row[27] if len(row)>27 else None})
        if kind=="Thread" and op in ("Start","End") and number(row[19])==pid:
            (starts if op=="Start" else ends)[number(row[20])]=int(row[16])
        if kind=="Image" and len(row)>21 and number(row[21])==pid: images+=1
    pstart=[v for v in process if v["opcode"]=="Start"]; pend=[v for v in process if v["opcode"]=="End"]
    if len(pstart)!=1 or len(pend)!=1: raise ValueError("fixture process lifetime not unique")
    if pstart[0]["key"]!=pend[0]["key"]:raise ValueError("fixture process key changed")
    facts[pid]={"pid":pid,"held_creation_filetime":g["creation_filetime"],"held_exit_filetime":g["exit_filetime"],
      "process_start_clock":pstart[0]["clock"],"process_end_clock":pend[0]["clock"],
      "process_start_delta_from_creation_100ns":pstart[0]["clock"]-g["creation_filetime"],
      "image_is_expected":pstart[0]["image"]=="EtwCapture.exe","held_exit_code":g["exit_code"],
      "job_active":g["job_active"],"job_total":g["job_total"],
      "thread_start_count":len(starts),"thread_end_count":len(ends),
      "observed_thread_ids":sorted(starts),"image_events":images,
      "held_cpu_ticks_100ns":g["cpu_ticks"],"observed_cswitch_in":0,"observed_cswitch_out":0,
      "matched_interval_ticks_100ns":0,"matched_intervals":0,
      "thread_windows":{t:(ts,ends.get(t,g["exit_filetime"])) for t,ts in starts.items()}}
lookup=collections.defaultdict(list)
for pid,f in facts.items():
    for tid,(start,end) in f["thread_windows"].items():lookup[tid].append((pid,start,end))
def owner(tid,stamp):
    matches=[pid for pid,start,end in lookup.get(tid,[]) if start<=stamp<=end]
    if len(matches)>1:raise ValueError("ambiguous fixture thread generation")
    return matches[0] if matches else None
last={}; mismatches=0; backwards=0; count=0
with (out/"cswitch-prefix.csv").open(newline="") as f:
    for row in csv.DictReader(f):
        count+=1
        t,cpu,new,old=(int(row[k]) for k in ("clock_100ns","cpu","new_tid","old_tid"))
        inc=owner(new,t); leaving=owner(old,t)
        if inc is not None:facts[inc]["observed_cswitch_in"]+=1
        if leaving is not None:facts[leaving]["observed_cswitch_out"]+=1
        if cpu in last:
            prev_t,prev_new=last[cpu]
            if t<prev_t:backwards+=1
            elif old!=prev_new:mismatches+=1
            elif leaving is not None and owner(old,prev_t)==leaving:
                facts[leaving]["matched_interval_ticks_100ns"]+=t-prev_t
                facts[leaving]["matched_intervals"]+=1
        last[cpu]=(t,new)
for v in facts.values():del v["thread_windows"]
result={"scope":"OFFLINE_THREE_OWNED_FIXTURE_CORRELATION_NOT_FULL_COVERAGE",
"fixture_facts":list(facts.values()),"cswitch_records":count,
"all_trace_per_cpu_continuity_mismatches":mismatches,"all_trace_backwards_clock":backwards,
"trace_events_lost":12027,"matched_interval_totals_are_not_complete_cpu_accounting":True,
"not_closed":["PPL","all transient processes","guest/hypervisor attribution","cross-partition deduplication","complete 60s loss-free window","independent stop"],
"admission":"BLOCKED","I1_I7":"OPEN"}
(out/"FIXTURE_CORRELATION.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
