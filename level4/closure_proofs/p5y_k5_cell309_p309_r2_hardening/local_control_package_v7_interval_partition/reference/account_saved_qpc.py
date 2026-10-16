"""Saved numeric evidence only. No live collection or admission implementation."""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def json_lines(p):
    with p.open(encoding="utf-8-sig") as f:
        for line in f:
            yield json.loads(line)


def union(intervals):
    out = []
    for a, b in sorted(intervals):
        if a < 0 or b < a:
            raise ValueError("invalid interval")
        if a == b:
            continue
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(b, out[-1][1]))
        else:
            out.append((a, b))
    return out


def overlap(left, right):
    a, b = union(left), union(right)
    i = j = total = 0
    while i < len(a) and j < len(b):
        total += max(0, min(a[i][1], b[j][1]) - max(a[i][0], b[j][0]))
        if a[i][1] <= b[j][1]:
            i += 1
        else:
            j += 1
    return total


def clipped(a, b, start, end):
    if b < a:
        raise ValueError("backwards interval")
    a, b = max(a, start), min(b, end)
    return (a, b) if a < b else None


def unique_lifetime(rows, key_index):
    starts = [r for r in rows if r[0] == 1]
    ends = [r for r in rows if r[0] == 2]
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError("nonunique lifetime")
    if starts[0][key_index] != ends[0][key_index] or starts[0][1] >= ends[0][1]:
        raise ValueError("lifetime identity/order mismatch")
    return starts[0][1], ends[0][1]


def analyze(root):
    cap, off = root / "capture", root / "offline"
    header = read(off / "qpc.stdout.json")
    previous = read(off / "CSWITCH_RAW_RESULT.json")
    for key in ("unknown_required_prefix", "header_events_lost", "header_buffers_lost", "process_rc", "close_rc", "output_error"):
        if header[key] != 0:
            raise ValueError("unusable decoder status: " + key)
    if header["clock_type"] != 1 or header["qpc_frequency"] <= 0:
        raise ValueError("not QPC")
    # A mixed CPU namespace needs a topology proof; do not silently merge it.
    if header["cpu_number_events"] or header["max_cpu"] >= header["processors"]:
        raise ValueError("CPU index mapping not homogeneous/bounded")
    if header["events"] != previous["events"] or previous["header_events_lost"]:
        raise ValueError("independent decoder count/loss differs")
    guards = [r for r in json_lines(cap / "guard.jsonl") if "job_total" in r]
    held = [r for r in guards if r["scope"] == "OWNED_WHP_COUNTER_FIXTURE_ONLY"]
    whp_rows = list(json_lines(cap / "whp-probe.stdout.jsonl"))
    counters = [r for r in whp_rows if "run_tid" in r]
    clean = [r for r in whp_rows if r.get("stage") == "whp_cleanup"]
    if len(held) != 1 or len(counters) != 1 or len(clean) != 1 or clean[0]["api_cleanup_succeeded"] is not True:
        raise ValueError("WHP evidence incomplete")
    held, vp = held[0], counters[0]
    if (held["pid"], held["creation_filetime"]) != (vp["pid"], vp["creation_filetime"]) or held["exit_code"] or held["job_active"] or held["job_total"] != 1:
        raise ValueError("held process differs/not clean")
    if vp["qpc_frequency"] != header["qpc_frequency"] or vp["run_hr"] or vp["cancel_hr"]:
        raise ValueError("WHP clock/API status differs")
    begin, end = vp["run_begin_qpc"], vp["run_end_qpc"]
    if not header["first_qpc"] <= vp["begin_qpc"] <= begin < end <= vp["end_qpc"] <= header["last_qpc"]:
        raise ValueError("WHP time bounds differ")
    pids = {r["pid"] for r in guards}
    if len(pids) != 4 or len(guards) != 4:
        raise ValueError("fixture generations ambiguous")
    proc, thread = defaultdict(list), defaultdict(list)
    last, scheduled, irqs = {}, defaultdict(list), defaultdict(list)
    kinds = Counter()
    protected = set()
    gaps = backwards = window_gaps = rows = 0
    for_row = off / "qpc-prefix.csv"
    with for_row.open(newline="", encoding="ascii") as f:
        for text in csv.DictReader(f):
            kind, qpc, cpu, op, a, b, c, cpu_kind = (int(text[k]) for k in ("kind", "qpc", "cpu", "opcode", "a", "b", "c", "cpu_index_flag"))
            rows += 1
            kinds[kind] += 1
            if cpu_kind != 1 or not 0 <= cpu < header["processors"] or qpc < 0:
                raise ValueError("invalid row CPU/clock")
            if kind == 1:
                if cpu in last:
                    start, incoming = last[cpu]
                    if qpc < start:
                        backwards += 1
                    elif incoming != b:
                        gaps += 1
                        window_gaps += bool(clipped(start, qpc, begin, end))
                    elif b == vp["run_tid"]:
                        cut = clipped(start, qpc, begin, end)
                        if cut:
                            scheduled[cpu].append(cut)
                last[cpu] = qpc, a
            elif kind == 2:
                cut = clipped(a, qpc, begin, end)
                if cut:
                    irqs[cpu].append(cut)
            elif kind == 3 and a in pids:
                thread[(a, b)].append((op, qpc, b))
            elif kind == 4:
                if c & 4:
                    protected.add((a, b))
                if b in pids:
                    proc[b].append((op, qpc, a))
            elif kind not in (3, 5):
                raise ValueError("unknown row kind")
    if rows != header["decoded"] or kinds[1] != previous["decoded_cswitch"]:
        raise ValueError("numeric row count differs")
    if backwards or window_gaps:
        raise ValueError("unreconciled switch continuity in comparison window")
    if set(last) != set(range(header["processors"])) or any(v[0] < end for v in last.values()):
        raise ValueError("comparison window has unclosed CPU tail")
    facts = []
    for held_row in guards:
        pid = held_row["pid"]
        lifetime = unique_lifetime(proc[pid], 2)
        own_threads = []
        for (thread_pid, tid), records in thread.items():
            if thread_pid == pid:
                start, stop = unique_lifetime(records, 2)
                if not lifetime[0] <= start <= stop <= lifetime[1]:
                    raise ValueError("thread outside process lifetime")
                own_threads.append(tid)
                if tid == vp["run_tid"]:
                    if pid != vp["pid"] or not start <= begin < end <= stop:
                        raise ValueError("WHP run thread lifetime differs")
        if not own_threads:
            raise ValueError("missing fixture threads")
        facts.append(dict(pid=pid, creation_filetime=held_row["creation_filetime"], process_qpc=lifetime, thread_ids=sorted(own_threads)))
    if (vp["pid"], vp["run_tid"]) not in thread:
        raise ValueError("missing WHP run thread")
    raw = sum(b-a for spans in scheduled.values() for a, b in spans)
    merged = sum(b-a for a, b in union([span for spans in scheduled.values() for span in spans]))
    if raw != merged or raw > end-begin:
        raise ValueError("run-thread CPU overlap")
    irq = sum(overlap(spans, irqs[cpu]) for cpu, spans in scheduled.items())
    freq = header["qpc_frequency"]
    delta = {}
    for stem in ("vp_total", "vp_hypervisor", "process_cpu"):
        value = vp[stem+"_after_100ns"] - vp[stem+"_before_100ns"]
        if value < 0:
            raise ValueError("counter went backwards")
        delta[stem+"_delta_100ns"] = value
    if delta["vp_hypervisor_delta_100ns"] > delta["vp_total_delta_100ns"]:
        raise ValueError("hypervisor counter exceeds total")
    return dict(scope="OFFLINE_ONE_OWNED_WHP_QPC_COMPARISON", events=header["events"], lost=0,
                trace_span_seconds=(header["last_qpc"]-header["first_qpc"])/freq,
                header_span_seconds=(header["header_end_filetime"]-header["header_start_filetime"])/10000000,
                kinds=dict(kinds), fixture_lifetimes=facts, run_tid=vp["run_tid"],
                run_wall_seconds=(end-begin)/freq, scheduled_seconds=raw/freq,
                irq_union_overlap_seconds=irq/freq, scheduled_minus_irq_seconds=(raw-irq)/freq,
                counters=delta, global_switch_continuity_gaps=gaps, comparison_window_gaps=window_gaps,
                protected_flag_generations_observed=len(protected), protected_coverage_proven=False,
                counter_window_is_wider_than_run_window=True,
                whole_process_cpu_is_not_run_thread_cpu=True,
                threaded_dpc_not_subtracted=True, full_host_guest_deduplication_proven=False,
                coverage_complete=False, I1_I7="OPEN", admission="BLOCKED")


if __name__ == "__main__":
    result = analyze(Path(sys.argv[1]))
    with Path(sys.argv[2]).open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(result, ensure_ascii=False))
