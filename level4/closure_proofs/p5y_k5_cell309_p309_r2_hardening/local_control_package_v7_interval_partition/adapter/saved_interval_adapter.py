"""Two-pass saved numeric adapter; imports must be bound by the offline driver.

Never captures events or attests coverage. Public rows/read hooks permit the
same-handle, same-byte driver to supply both passes and immutable summaries.
"""
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
from account_saved_qpc import read, clipped
from interval_partition import partition_interval


def rows(path):
    with path.open(encoding="ascii", newline="") as stream:
        reader = csv.reader(stream)
        if next(reader) != ["kind", "qpc", "cpu", "opcode", "a", "b", "c", "cpu_index_flag"]:
            raise ValueError("unexpected numeric schema")
        for row in reader:
            if len(row) != 8:
                raise ValueError("unexpected row width")
            yield tuple(map(int, row))


# Exact v4 lifetimes body; renamed only. Historical comparator NEVER feeds KNOWN.
# Source SHA256 3799e88d1726ba2a4e625d8e08decb3765a5bc36527bf92d8329fe81a81fa189
def historical_lifetimes(records, low, high):
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


def historical_maps(events, low, high):
    grouped = defaultdict(list)
    for op, qpc, numeric_id, identity, flags, ordinal in events:
        grouped[numeric_id].append((op, qpc, identity))
    result = {}
    for numeric_id, records in grouped.items():
        try:
            result[numeric_id] = historical_lifetimes(records, low, high)
        except ValueError:
            pass  # Exact v4 omission for unresolved lifetimes, comparison only.
    return result


def historical_owner(tid, a, b, tmap, pmap):
    matches = [v for v in tmap.get(tid, []) if v[0] <= a <= b <= v[1]]
    if len(matches) != 1:
        return None
    pid = matches[0][2]
    matches = [v for v in pmap.get(pid, []) if v[0] <= a <= b <= v[1]]
    return (pid, matches[0][2]) if len(matches) == 1 else None


def compare_span(decision, historical_identity):
    old = "old_unknown" if historical_identity is None else "old_known"
    return {old+"_new_known": decision["known_ticks"],
            old+"_new_unknown": decision["unknown_ticks"]}


def integer(value):
    return type(value) is int and value >= 0


def build_generations(events, low, high):
    """events=(opcode,qpc,numeric_id,identity,flags,CSV_data_row_ordinal).

    Any invalid lifecycle invalidates the ENTIRE ID, including earlier otherwise
    valid generations. No conflict filtering, implicit end or traceLow birth.
    """
    if not integer(low) or not integer(high) or high < low:
        raise ValueError("invalid trace bounds")
    by_id = defaultdict(list)
    ordinals = set()
    for event in events:
        if len(event) != 6 or not all(integer(v) for v in event):
            raise ValueError("invalid lifecycle row")
        op, qpc, numeric_id, identity, flags, ordinal = event
        if op not in (1, 2, 3, 4) or not low <= qpc <= high or ordinal in ordinals:
            raise ValueError("invalid opcode, trace timestamp or duplicate CSV row")
        ordinals.add(ordinal)
        by_id[numeric_id].append(tuple(event))
    generations, evidence, flags_by_generation, unresolved = {}, {}, {}, {}
    for numeric_id, raw in by_id.items():
        ordered = sorted(raw, key=lambda e: (e[1], e[5]))
        built, proofs, observed_flags = [], {}, {}
        active = None
        problem = None
        if len({e[1] for e in ordered}) != len(ordered):
            problem = "SAME_QPC_LIFECYCLE_ORDER_UNPROVEN"
        elif [e[1] for e in sorted(raw, key=lambda e: e[5])] != [e[1] for e in ordered]:
            problem = "BACKWARDS_LIFECYCLE_EVENT_ORDER"
        if problem is None:
            for op, qpc, _, identity, flags, ordinal in ordered:
                if op in (1, 3):
                    if active is not None:
                        if op == 3 and active["start_kind"] == "START" and not active["dcstart"] and active["identity"] == identity:
                            active["dcstart"] = True
                            active["rows"].append(ordinal)
                            active["flags"].append(dict(row_ordinal=ordinal, opcode=op, qpc=qpc, flags=flags))
                            continue
                        problem = "DUPLICATE_OR_OVERLAPPING_START"
                        break
                    active = dict(start=low if op == 3 else qpc,
                                  anchor=qpc, start_kind="RUNDOWN" if op == 3 else "START",
                                  identity=identity, dcstart=op == 3, rows=[ordinal],
                                  flags=[dict(row_ordinal=ordinal, opcode=op, qpc=qpc, flags=flags)])
                else:
                    if active is None or active["identity"] != identity:
                        problem = "UNMATCHED_END_OR_IDENTITY_CONFLICT"
                        break
                    index = len(built)
                    built.append((active["start"], high if op == 4 else qpc, identity,
                                  active["start_kind"] == "RUNDOWN"))
                    proofs[index] = dict(start_kind=active["start_kind"], start_anchor=active["anchor"],
                                         end_kind="RUNDOWN" if op == 4 else "END", end_anchor=qpc,
                                         source_row_ordinals=active["rows"]+[ordinal])
                    observations = active["flags"]+[dict(row_ordinal=ordinal, opcode=op, qpc=qpc, flags=flags)]
                    values = {r["flags"] for r in observations}
                    observed_flags[index] = dict(observations=observations,
                                                  consistent=len(values) == 1,
                                                  value=next(iter(values)) if len(values) == 1 else None)
                    active = None
        if problem is None and active is not None:
            problem = "UNCLOSED_LIFECYCLE_NO_REAL_END_ANCHOR"
        if problem is None and any(left[1] >= right[0] for left, right in zip(built, built[1:])):
            problem = "OVERLAPPING_OR_SAME_QPC_DERIVED_GENERATIONS"
        if problem is not None:
            unresolved[numeric_id] = dict(reason=problem, events=ordered)
        else:
            generations[numeric_id], evidence[numeric_id] = built, proofs
            flags_by_generation[numeric_id] = observed_flags
    return dict(generations=generations, evidence=evidence,
                flags=flags_by_generation, unresolved=unresolved, events_by_id=dict(by_id))


def partition_switch_span(tid, original_span, thread_index, process_index, window):
    """Pass the ORIGINAL CSwitch endpoints, never its clipped overlap."""
    # Subset IDs only; never filter/reindex generations within an ID.
    trows = thread_index["generations"].get(tid, [])
    parent_ids = {r[2] for r in trows}
    result = partition_interval(tid, original_span, {tid: trows},
                                {pid: process_index["generations"].get(pid, []) for pid in parent_ids}, window,
                                thread_evidence=thread_index["evidence"],
                                process_evidence=process_index["evidence"])
    result["unresolved_thread"] = thread_index["unresolved"].get(tid)
    pids = {r[3] for r in result["unresolved_thread"]["events"]} if result["unresolved_thread"] else set()
    pids.update(r[2] for r in thread_index["generations"].get(tid, []))
    result["unresolved_processes"] = {pid: process_index["unresolved"][pid]
                                      for pid in pids if pid in process_index["unresolved"]}
    result["bound_source_events"] = {}
    for label, bound, source in (("thread", result["bound_thread"], thread_index),
                                  ("process", result["bound_process"], process_index)):
        if bound is not None:
            numeric_id, ordinal = bound["numeric_id"], bound["ordinal"]
            metadata = source["evidence"][numeric_id][ordinal]
            row_ids = set(metadata["source_row_ordinals"])
            result["bound_source_events"][label] = dict(metadata=metadata, events=[
                list(e) for e in source["events_by_id"][numeric_id] if e[5] in row_ids])
    for piece in result["slices"]:
        if piece["state"] == "KNOWN":
            owner = piece["identity"]
            piece["process_flags"] = process_index["flags"][owner["pid"]][owner["process_ordinal"]]
    return result


def _row(row, header):
    if len(row) != 8 or not all(integer(v) for v in row):
        raise ValueError("invalid numeric row")
    kind, qpc, cpu, op, a, b, c, index = row
    if (kind not in (1, 2, 3, 4, 5) or index != 1 or cpu >= header["processors"] or
            not header["first_qpc"] <= qpc <= header["last_qpc"]):
        raise ValueError("unsupported row namespace or bounds")
    supported = {1: (36,), 2: (50, 67, 68, 69), 3: (1, 2, 3, 4),
                 4: (1, 2, 3, 4), 5: (66,)}
    if op not in supported[kind]:
        raise ValueError("unsupported kind/opcode pair")
    return kind, qpc, cpu, op, a, b, c, index


def audit(root, private_decisions=None):
    """Two rows(path) passes. No live query or original audit modification.

    Caller MUST bind modules, summary bytes and identical CSV bytes/row counts
    across both passes. This standalone entry does not claim such custody.
    """
    off = Path(root)/"offline"
    header = read(off/"qpc.stdout.json")
    for key in ("unknown_required_prefix", "header_events_lost", "header_buffers_lost",
                "process_rc", "close_rc", "output_error"):
        if header[key] != 0:
            raise ValueError("unusable decoder status: "+key)
    if (header["clock_type"] != 1 or header["cpu_number_events"] != 0 or
            not integer(header["qpc_frequency"]) or header["qpc_frequency"] == 0 or
            not integer(header["processors"]) or header["processors"] == 0 or
            header["max_cpu"] >= header["processors"]):
        raise ValueError("unsupported clock or CPU namespace")
    path = off/"qpc-prefix.csv"
    threads, processes, starts, ends = [], [], [], []
    first_count = 0
    for ordinal, raw in enumerate(rows(path), 1):
        kind, qpc, cpu, op, a, b, c, index = _row(raw, header)
        first_count = ordinal
        if kind in (3, 4):
            (threads if kind == 3 else processes).append((op, qpc, b, a, c, ordinal))
            if op == 3:
                starts.append(qpc)
            if op == 4:
                ends.append(qpc)
    if first_count != header["decoded"] or not starts or not ends:
        raise ValueError("row count or rundown missing")
    begin = max(starts)
    finish = begin+60*header["qpc_frequency"]
    if min(ends) < finish:
        raise ValueError("no closed 60-second interior window")
    thread_index = build_generations(threads, header["first_qpc"], header["last_qpc"])
    process_index = build_generations(processes, header["first_qpc"], header["last_qpc"])
    historical_threads = historical_maps(threads, header["first_qpc"], header["last_qpc"])
    historical_processes = historical_maps(processes, header["first_qpc"], header["last_qpc"])
    last, spans, ticks, reasons = {}, Counter(), Counter(), Counter()
    comparison, geometry = Counter(), Counter()
    backwards = discontinuities = decision_count = second_count = 0
    sink = None
    try:
        if private_decisions is not None:
            sink = Path(private_decisions).open("x", encoding="utf-8")
        for ordinal, raw in enumerate(rows(path), 1):
            kind, qpc, cpu, op, incoming, outgoing, c, index = _row(raw, header)
            second_count = ordinal
            if kind != 1:
                continue
            if cpu in last:
                before, prior_new, before_row = last[cpu]
                if qpc < before:
                    raise ValueError("backwards CSwitch QPC on CPU %d at CSV row %d" % (cpu, ordinal))
                else:
                    if prior_new != outgoing:
                        discontinuities += 1
                    cut = clipped(before, qpc, begin, finish)
                    if cut:
                        duration = cut[1]-cut[0]
                        spans[cpu] += duration
                        if prior_new != outgoing:
                            ticks["discontinuous_unknown"] += duration
                        elif outgoing == 0:
                            ticks["historical_idle_unproven"] += duration
                        if prior_new != outgoing or outgoing == 0:
                            decision_count += 1
                            if sink is not None:
                                sink.write(json.dumps(dict(cpu=cpu, cswitch_source_rows=[before_row, ordinal],
                                    source_interval=[before, qpc], clipped_interval=list(cut), ticks=duration,
                                    state="UNKNOWN", reason="CSWITCH_DISCONTINUITY" if prior_new != outgoing
                                    else "TID_ZERO_IDLE_UNPROVEN", tid=outgoing), sort_keys=True)+"\n")
                        else:
                            geometry["touching_original_ticks"] += qpc-before
                            geometry["inside_window_ticks"] += duration
                            geometry["outside_window_ticks"] += qpc-before-duration
                            # Deliberately do not pass cut as the source span.
                            decision = partition_switch_span(outgoing, (before, qpc), thread_index,
                                                             process_index, (begin, finish))
                            old_identity = historical_owner(outgoing, cut[0], cut[1], historical_threads,
                                                            historical_processes)
                            comparison.update(compare_span(decision, old_identity))
                            decision["historical_comparator_identity"] = old_identity
                            decision["historical_comparator_not_evidence"] = True
                            for piece in decision["slices"]:
                                if piece["state"] == "UNKNOWN":
                                    label = "unknown_identity"
                                    reasons[piece["reason"]] += piece["ticks"]
                                elif not piece["process_flags"]["consistent"]:
                                    label = "known_identity_flags_unknown"
                                else:
                                    label = "known_protected_flag" if piece["process_flags"]["value"] & 4 else "known_other"
                                ticks[label] += piece["ticks"]
                            if old_identity is None or decision["unknown_ticks"] or len(decision["slices"]) > 1:
                                decision_count += 1
                                if sink is not None:
                                    sink.write(json.dumps(dict(cpu=cpu, cswitch_source_rows=[before_row, ordinal],
                                                               decision=decision), sort_keys=True)+"\n")
            last[cpu] = (qpc, incoming, ordinal)
        if second_count != first_count:
            raise ValueError("second pass row count differs")
        if sum(comparison.values()) != geometry["inside_window_ticks"]:
            raise AssertionError("historical comparison conservation failed")
        if geometry["inside_window_ticks"]+geometry["outside_window_ticks"] != geometry["touching_original_ticks"]:
            raise AssertionError("original/window conservation failed")
        if sum(ticks.values()) != sum(spans.values()):
            raise AssertionError("adapter tick conservation failed")
    finally:
        if sink is not None:
            sink.close()
    return dict(scope="OFFLINE_BOUNDARY_PARTITION_DIAGNOSTIC_NOT_ADMISSION", window_qpc=[begin, finish],
                qpc_frequency=header["qpc_frequency"], row_counts=[first_count, second_count],
                ticks_by_class=dict(ticks), unknown_ticks_by_reason=dict(reasons),
                historical_comparison_ticks=dict(comparison),
                historical_unknown_ticks=comparison["old_unknown_new_known"]+comparison["old_unknown_new_unknown"],
                recoverable_old_unknown_prefix_ticks=comparison["old_unknown_new_known"],
                remaining_new_unknown_ticks=comparison["old_unknown_new_unknown"]+comparison["old_known_new_unknown"],
                original_span_geometry=dict(geometry),
                geometry_scope="POSITIVE_CONTINUOUS_NON_TID0_SPANS_WITH_POSITIVE_WINDOW_OVERLAP_ONLY",
                historical_comparator_source_sha256="3799e88d1726ba2a4e625d8e08decb3765a5bc36527bf92d8329fe81a81fa189",
                unknown_identity_seconds=ticks["unknown_identity"]/header["qpc_frequency"],
                every_cpu_has_closed_60s_span=(discontinuities == 0 and set(spans) == set(range(header["processors"])) and
                                               all(n == finish-begin for n in spans.values())),
                backwards=backwards, discontinuities=discontinuities,
                unresolved_thread_ids=len(thread_index["unresolved"]),
                unresolved_process_ids=len(process_index["unresolved"]),
                private_decision_count=decision_count, tid_zero_idle_proven=False,
                original_source_binding_proven=False, actual_runtime_validation=False,
                coverage_complete=False, admission="BLOCKED", I1_I7="OPEN")
