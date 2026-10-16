"""Aggregate saved-root scheduling gaps; deliberately never attests completeness."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from account_saved_qpc import read, union, overlap, clipped


def rows(path):
    with path.open(encoding="ascii", newline="") as f:
        for r in csv.DictReader(f):
            yield tuple(int(r[k]) for k in ("kind", "qpc", "cpu", "opcode", "a", "b", "c", "cpu_index_flag"))


def lifetimes(records, low, high):
    """Rundown bounds existing identity, without pretending to know creation time."""
    result = []
    active = None
    for op, when, identity in sorted(records, key=lambda x: (x[1], x[0])):
        if op in (1, 3):
            if active is not None:
                # DCStart enumerates an already running thread/process. A
                # matching snapshot after its real Start is not a new birth.
                # Keep the exact Start bound; never widen it to trace start.
                if op == 3 and not active[2] and active[1] == identity and active[0] <= when:
                    continue
                raise ValueError("overlapping start/rundown identity")
            active = (low if op == 3 else when, identity, op == 3)
        elif op in (2, 4):
            if active is None or active[1] != identity:
                raise ValueError("unmatched end/rundown identity")
            stop = high if op == 4 else when
            if active[0] > stop:
                raise ValueError("backwards lifetime")
            result.append((active[0], stop, identity, active[2]))
            active = None
    if active is not None:
        raise ValueError("unclosed lifetime")
    return result


def audit(root):
    off = root / "offline"
    h = read(off / "qpc.stdout.json")
    if any(h[k] for k in ("unknown_required_prefix", "header_events_lost", "header_buffers_lost", "process_rc", "close_rc", "output_error")):
        raise ValueError("decoder not usable")
    if h["clock_type"] != 1 or h["cpu_number_events"] or h["max_cpu"] >= h["processors"]:
        raise ValueError("clock/cpu mapping unsupported")
    path = off / "qpc-prefix.csv"
    proc, threads, flags = defaultdict(list), defaultdict(list), {}
    early_rundown, late_rundown = [], []
    for kind, stamp, cpu, op, a, b, c, index in rows(path):
        if kind == 4:
            proc[b].append((op, stamp, a))
            flags[(b, a)] = flags.get((b, a), 0) | c
        elif kind == 3:
            threads[b].append((op, stamp, a))
        if kind in (3, 4):
            if op == 3:
                early_rundown.append(stamp)
            elif op == 4:
                late_rundown.append(stamp)
    if not early_rundown or not late_rundown:
        raise ValueError("missing rundown")
    begin = max(early_rundown)
    end = begin + 60*h["qpc_frequency"]
    if min(late_rundown) < end:
        raise ValueError("no full 60 second interval between rundown boundaries")
    # Unresolvable identities are counted, never guessed or discarded as quiet.
    pmap, tmap, bad_proc, bad_thread = {}, {}, 0, 0
    for pid, events in proc.items():
        try:
            pmap[pid] = lifetimes(events, h["first_qpc"], h["last_qpc"])
        except ValueError:
            bad_proc += 1
    for tid, events in threads.items():
        try:
            tmap[tid] = lifetimes(events, h["first_qpc"], h["last_qpc"])
        except ValueError:
            bad_thread += 1

    def owner(tid, a, b):
        matches = [v for v in tmap.get(tid, []) if v[0] <= a <= b <= v[1]]
        if len(matches) != 1:
            return None
        pid = matches[0][2]
        matches = [v for v in pmap.get(pid, []) if v[0] <= a <= b <= v[1]]
        return (pid, matches[0][2]) if len(matches) == 1 else None

    last, scheduled, irq = {}, defaultdict(list), defaultdict(list)
    totals = defaultdict(int)
    unknown_intervals = discontinuities = backwards = 0
    cpu_span = defaultdict(int)
    for kind, stamp, cpu, op, incoming, outgoing, unused, index in rows(path):
        if index != 1 or not 0 <= cpu < h["processors"]:
            raise ValueError("invalid CPU row")
        if kind == 2:
            cut = clipped(incoming, stamp, begin, end)
            if cut:
                irq[cpu].append(cut)
        if kind != 1:
            continue
        if cpu in last:
            before, prev = last[cpu]
            if stamp < before:
                backwards += 1
            else:
                cut = clipped(before, stamp, begin, end)
                if cut:
                    a, b = cut
                    cpu_span[cpu] += b-a
                    if prev != outgoing:
                        discontinuities += 1
                        totals["discontinuous"] += b-a
                    elif outgoing == 0:
                        totals["idle_scheduled"] += b-a
                    else:
                        identity = owner(outgoing, a, b)
                        label = "unknown_identity" if identity is None else "protected_flag" if flags[identity] & 4 else "other_identified"
                        totals[label] += b-a
                        if identity is None:
                            unknown_intervals += 1
                        # Save non-idle intervals only, to subtract IRQ union once.
                        scheduled[cpu].append((a, b))
        last[cpu] = stamp, incoming
    complete_cpu_spans = set(cpu_span) == set(range(h["processors"])) and all(v == end-begin for v in cpu_span.values())
    irq_total = sum(b-a for spans in irq.values() for a, b in union(spans))
    irq_on_busy = sum(overlap(spans, irq[cpu]) for cpu, spans in scheduled.items())
    freq = h["qpc_frequency"]
    return dict(scope="OFFLINE_ROOT_SCHEDULED_INTERVAL_AUDIT_NOT_HOST_ADMISSION",
                window_seconds=60, window_qpc=[begin, end], processor_count=h["processors"],
                every_cpu_has_closed_60s_span=complete_cpu_spans,
                scheduled_seconds_by_class={k:v/freq for k,v in sorted(totals.items())},
                unknown_intervals=unknown_intervals, discontinuities=discontinuities, backwards=backwards,
                unresolved_process_identities=bad_proc, unresolved_thread_identities=bad_thread,
                irq_union_seconds=irq_total/freq, irq_on_nonidle_seconds=irq_on_busy/freq,
                root_busy_minus_irq_seconds=(sum(v for k,v in totals.items() if k not in ("idle_scheduled", "discontinuous"))-irq_on_busy)/freq,
                protected_process_coverage_proven=False, other_partition_coverage_proven=False,
                rundown_is_not_creation_time=True, coverage_complete=False, I1_I7="OPEN", admission="BLOCKED")


if __name__ == "__main__":
    result = audit(Path(sys.argv[1]))
    with Path(sys.argv[2]).open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))
