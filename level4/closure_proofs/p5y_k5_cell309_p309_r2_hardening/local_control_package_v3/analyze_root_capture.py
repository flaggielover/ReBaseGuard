"""Offline saved-file projection only. Never certifies coverage or admission.

Input directory: capture/{guard.jsonl,RESULT.json,hypervisor-raw.jsonl,...},
offline/{events.csv,cswitch-prefix.csv,CSWITCH_RAW_RESULT.json}.
CSV is produced by the pinned system tracerpt (observed ACP936); no live API.
Output must be a fresh path. Malformed/unknown input raises, never fabricates PASS.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def read_json(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def lines(p):
    with p.open(encoding="utf-8-sig") as f:
        for line in f:
            yield json.loads(line)


def number(s):
    value = s.strip()
    return int(value, 16) if value.startswith("0x") else int(value)


def analyze(root):
    cap, off = root / "capture", root / "offline"
    verdict, decoded = read_json(cap / "RESULT.json"), read_json(off / "CSWITCH_RAW_RESULT.json")
    guard = list(lines(cap / "guard.jsonl"))
    fixtures = [r for r in guard if "job_total" in r]
    pids = [r["pid"] for r in fixtures]
    if len(pids) != len(set(pids)):
        raise ValueError("reused fixture PID requires additional generation analysis")
    process = defaultdict(list)
    threads = defaultdict(list)
    schemas = Counter()
    total = 0
    low = high = None
    csv_path = off / "events.csv"
    with csv_path.open("rb") as f:
        prefix = f.read(2)
    encoding = "utf-16" if prefix in (b"\xff\xfe", b"\xfe\xff") else "cp936"
    with csv_path.open(encoding=encoding, newline="") as f:
        reader = csv.reader(f, skipinitialspace=True)
        next(reader)
        for row in reader:
            if len(row) < 19:
                raise ValueError("short event")
            total += 1
            name, op, version = (row[i].strip() for i in (0, 1, 3))
            schemas[(name, op, version)] += 1
            stamp = number(row[16])
            low = stamp if low is None else min(low, stamp)
            high = stamp if high is None else max(high, stamp)
            if name == "Process" and op in ("Start", "End"):
                if version != "4" or len(row) < 28:
                    raise ValueError("unsupported process schema")
                pid = number(row[20])
                if pid in pids:
                    process[pid].append((op, stamp, row[19].strip(), row[27].strip()))
            elif name == "Thread" and op in ("Start", "End"):
                if version != "3" or len(row) < 21:
                    raise ValueError("unsupported thread schema")
                pid = number(row[19])
                if pid in pids:
                    threads[pid].append((op, stamp, number(row[20])))
    facts = {}
    lookup = defaultdict(list)
    for held in fixtures:
        pid = held["pid"]
        starts = [v for v in process[pid] if v[0] == "Start"]
        ends = [v for v in process[pid] if v[0] == "End"]
        if len(starts) != 1 or len(ends) != 1 or starts[0][2] != ends[0][2] or ends[0][1] < starts[0][1]:
            raise ValueError("missing/ambiguous fixture process lifetime")
        tstarts = defaultdict(list)
        tends = defaultdict(list)
        for op, stamp, tid in threads[pid]:
            (tstarts if op == "Start" else tends)[tid].append(stamp)
        if set(tstarts) != set(tends):
            raise ValueError("unclosed fixture thread lifetime")
        for tid, values in tstarts.items():
            if len(values) != 1 or len(tends[tid]) != 1 or tends[tid][0] < values[0]:
                raise ValueError("ambiguous fixture thread generation")
            lookup[tid].append((pid, values[0], tends[tid][0]))
        expected = "WhpCounterProbe.exe" if held["scope"] == "OWNED_WHP_COUNTER_FIXTURE_ONLY" else "EtwCapture.exe"
        facts[pid] = dict(held)
        facts[pid].update(expected_image_match=starts[0][3] == expected,
                          process_start_delta_from_creation_100ns=starts[0][1]-held["creation_filetime"],
                          thread_ids=sorted(tstarts), observed_intervals=0,
                          observed_interval_sum_100ns=0, observed_switch_in=0, observed_switch_out=0)

    def owner(tid, stamp):
        found = [p for p, begin, end in lookup.get(tid, []) if begin <= stamp <= end]
        if len(found) > 1:
            raise ValueError("overlapping fixture thread identities")
        return found[0] if found else None

    last = {}
    gaps = backwards = switches = 0
    with (off / "cswitch-prefix.csv").open(newline="", encoding="ascii") as f:
        for row in csv.DictReader(f):
            switches += 1
            stamp, cpu, new, old = (int(row[k]) for k in ("clock_100ns", "cpu", "new_tid", "old_tid"))
            incoming, outgoing = owner(new, stamp), owner(old, stamp)
            if incoming is not None:
                facts[incoming]["observed_switch_in"] += 1
            if outgoing is not None:
                facts[outgoing]["observed_switch_out"] += 1
            if cpu in last:
                before, previous = last[cpu]
                if stamp < before:
                    backwards += 1
                elif old != previous:
                    gaps += 1
                elif outgoing is not None and owner(old, before) == outgoing:
                    facts[outgoing]["observed_intervals"] += 1
                    facts[outgoing]["observed_interval_sum_100ns"] += stamp-before
            last[cpu] = stamp, new

    if total != decoded["events"] or switches != decoded["decoded_cswitch"]:
        raise ValueError("decoder output count mismatch")
    sample_count = empty_samples = 0
    for row in lines(cap / "hypervisor-raw.jsonl"):
        if "sample" in row:
            sample = json.loads(row["sample"]) if isinstance(row["sample"], str) else row["sample"]
            sample_count += 1
            empty_samples += not sample["rows"]
    whp = None
    whp_path = cap / "whp-probe.stdout.jsonl"
    if whp_path.exists():
        whp_records = list(lines(whp_path))
        counter = [v for v in whp_records if "vp_total_after_100ns" in v]
        if len(counter) != 1:
            raise ValueError("WHP counter record missing/ambiguous")
        whp = counter[0]
        held = facts.get(whp["pid"])
        if not held or held["creation_filetime"] != whp["creation_filetime"] or whp["run_tid"] not in held["thread_ids"]:
            raise ValueError("WHP held process/thread binding differs")
        whp = dict(whp)
        whp["vp_total_delta_100ns"] = whp["vp_total_after_100ns"]-whp["vp_total_before_100ns"]
        whp["vp_hypervisor_delta_100ns"] = whp["vp_hypervisor_after_100ns"]-whp["vp_hypervisor_before_100ns"]
        whp["process_cpu_delta_100ns"] = whp["process_cpu_after_100ns"]-whp["process_cpu_before_100ns"]
        whp["comparable_or_deduplicated_cpu_proven"] = False
    return dict(scope="OFFLINE_SAVED_FIXTURE_PROJECTION_NO_ADMISSION",
                python=sys.version, analysis_runtime_only=True,
                raw_result=verdict, events=total, lost=decoded["header_events_lost"],
                event_span_100ns=None if low is None else high-low,
                unknown_cswitch=decoded["unknown_cswitch"],
                decoder_processors=decoded["processors"],
                processor_number_overflow_possible=decoded["processors"] > 255,
                processor_group_mapping_verified=False,
                native_decoder_note="ProcessorNumber prefix only; no multi-group certification",
                fixtures=list(facts.values()), whp=whp,
                sample_records=sample_count, samples_with_empty_counter_rows=empty_samples,
                cswitch_continuity_gaps=gaps, backwards_timestamps=backwards,
                interval_sums_are_not_complete_cpu_accounting=True,
                coverage_complete=False, I1_I7="OPEN", admission="BLOCKED")


if __name__ == "__main__":
    result = analyze(Path(sys.argv[1]))
    with Path(sys.argv[2]).open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"admission": "BLOCKED", "lost": result["lost"],
                      "events": result["events"], "fixtures": len(result["fixtures"])}))
