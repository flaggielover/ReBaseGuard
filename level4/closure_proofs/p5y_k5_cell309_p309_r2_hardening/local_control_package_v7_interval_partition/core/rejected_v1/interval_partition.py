"""Pure integer-QPC partitioning, compatible with v4 lifetimes() rows.

Rows are (start, end, identity, rundown): TID -> PID and PID -> ProcessKey.
No file IO, host API, collector, clock, threshold or admission implementation.
KNOWN means unique in supplied evidence, never complete host coverage.
"""
from collections.abc import Mapping


def _integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(name + " must be a nonnegative integer")
    return value


def _span(value, name):
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(name + " must contain two QPC integers")
    start, end = (_integer(v, name) for v in value)
    if end < start:
        raise ValueError(name + " runs backwards")
    return start, end


def _generations(mapping, name):
    if not isinstance(mapping, Mapping):
        raise ValueError(name + " must be a mapping")
    result = {}
    for numeric_id, records in mapping.items():
        _integer(numeric_id, name + " numeric id")
        if not isinstance(records, (list, tuple)):
            raise ValueError(name + " generations must be a list or tuple")
        normalized = []
        for ordinal, record in enumerate(records):
            if not isinstance(record, (list, tuple)) or len(record) != 4:
                raise ValueError(name + " generation must have four fields")
            start, end = _span(record[:2], name + " generation")
            identity = _integer(record[2], name + " identity")
            if type(record[3]) is not bool:
                raise ValueError(name + " rundown must be boolean")
            normalized.append(dict(numeric_id=numeric_id, ordinal=ordinal,
                                   start=start, end=end, identity=identity,
                                   rundown=record[3]))
        result[numeric_id] = normalized
    return result


def partition_interval(tid, interval, thread_generations, process_generations, window):
    """Partition one supplied closed-by-CSwitch span, using half-open intervals.

    No ordering is inferred between events at equal QPC. Zero-duration rows
    create boundaries but own no ticks. Duplicate/overlapping rows stay separate
    candidates, even with equal identities. No ThreadEnd extension, PID0/idle
    exemption or duration tolerance. Invalid types/bounds raise ValueError.
    The caller remains responsible for loss, continuity, identity and provenance.
    """
    _integer(tid, "tid")
    start, end = _span(interval, "interval")
    low, high = _span(window, "window")
    threads = _generations(thread_generations, "thread")
    processes = _generations(process_generations, "process")
    begin, finish = max(start, low), min(end, high)
    result = dict(scope="OFFLINE_SUPPLIED_INTERVAL_PARTITION_ONLY", tid=tid,
                  interval=[start, end], window=[low, high], clipped_interval=None,
                  interval_convention="HALF_OPEN_INTEGER_QPC",
                  same_qpc_policy="NO_EVENT_ORDER_INFERRED; ZERO_DURATION_OWNS_NO_TICKS",
                  boundaries=[], slices=[], known_ticks=0, unknown_ticks=0,
                  clipped_ticks=0, outside_window_ticks=end-start,
                  conservation_verified=True, coverage_complete=False,
                  admission="BLOCKED", I1_I7="OPEN")
    if begin >= finish:
        return result
    result["clipped_interval"] = [begin, finish]
    result["clipped_ticks"] = finish-begin
    result["outside_window_ticks"] = end-start-(finish-begin)
    bounds = {begin: [], finish: []}

    def boundary(when, evidence):
        if begin <= when <= finish:
            bounds.setdefault(when, []).append(evidence)

    for label, a, b in (("interval", start, end), ("window", low, high)):
        boundary(a, dict(source=label, edge="start"))
        boundary(b, dict(source=label, edge="end"))

    def touches(record):
        return record["start"] <= finish and begin <= record["end"]

    candidates = [r for r in threads.get(tid, []) if touches(r)]
    relevant_pids = {r["identity"] for r in candidates}
    relevant_processes = [r for pid in sorted(relevant_pids)
                          for r in processes.get(pid, []) if touches(r)]
    for kind, records in (("thread", candidates), ("process", relevant_processes)):
        for record in records:
            for edge in ("start", "end"):
                boundary(record[edge], dict(source=kind, edge=edge,
                                            generation=dict(record)))
    times = sorted(bounds)
    result["boundaries"] = [dict(qpc=t, evidence=bounds[t]) for t in times]

    def covers(record, a, b):
        return record["start"] <= a < b <= record["end"]

    for position, (a, b) in enumerate(zip(times, times[1:])):
        thread_matches = [r for r in candidates if covers(r, a, b)]
        matching_pids = {r["identity"] for r in thread_matches}
        process_matches = [r for r in relevant_processes
                           if r["numeric_id"] in matching_pids and covers(r, a, b)]
        identity = None
        if tid == 0:
            reason = "ZERO_TID_NOT_PROVEN_IDLE"
        elif not thread_matches:
            reason = "NO_THREAD_GENERATION"
        elif len(thread_matches) != 1:
            reason = "AMBIGUOUS_THREAD_GENERATION"
        elif thread_matches[0]["identity"] == 0:
            reason = "PID_ZERO_NOT_PROVEN_IDLE"
        elif not process_matches:
            reason = "NO_PROCESS_GENERATION"
        elif len(process_matches) != 1:
            reason = "AMBIGUOUS_PROCESS_GENERATION"
        elif process_matches[0]["identity"] == 0:
            reason = "ZERO_PROCESS_KEY_UNPROVEN"
        else:
            reason = "UNIQUE_SUPPLIED_THREAD_AND_PROCESS_GENERATIONS"
            identity = dict(tid=tid, pid=thread_matches[0]["identity"],
                            process_key=process_matches[0]["identity"],
                            thread_ordinal=thread_matches[0]["ordinal"],
                            process_ordinal=process_matches[0]["ordinal"])
        state = "KNOWN" if identity is not None else "UNKNOWN"
        result["slices"].append(dict(start=a, end=b, ticks=b-a, state=state,
                                     reason=reason, identity=identity,
                                     source_interval=[start, end],
                                     thread_candidates=[dict(r) for r in thread_matches],
                                     process_candidates=[dict(r) for r in process_matches],
                                     start_boundary=position, end_boundary=position+1))
        result["known_ticks" if state == "KNOWN" else "unknown_ticks"] += b-a
    if (sum(s["ticks"] for s in result["slices"]) != finish-begin or
            result["known_ticks"]+result["unknown_ticks"] != finish-begin or
            result["clipped_ticks"]+result["outside_window_ticks"] != end-start):
        raise AssertionError("partition conservation failed")
    return result
