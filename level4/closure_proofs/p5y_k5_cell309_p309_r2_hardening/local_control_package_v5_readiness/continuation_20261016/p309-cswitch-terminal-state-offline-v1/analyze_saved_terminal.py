"""Diagnose saved unknown thread intervals without extending ownership."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).absolute().parent
SAVED = Path(r"D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\offline")
PRIVATE = SAVED / "PRIVATE_UNATTRIBUTED_INTERVAL_IDENTITIES.json"
COVERAGE = SAVED / "ROOT_COVERAGE_AUDIT_V3.json"
STAGING = HERE.parent / "p309-offline-input-integrity-staging-v1"
HELPER = STAGING / "run_verified_audit.py"
HELPER_SHA = "9eb9e1fe69e8b6d148c71714c907d0bccc5198c715ee850681064cdc2fd221b6"
AUDIT = STAGING / "audit_root_coverage.snapshot.py"
AUDIT_SHA = "3799e88d1726ba2a4e625d8e08decb3765a5bc36527bf92d8329fe81a81fa189"
ACCOUNT = STAGING / "account_saved_qpc.snapshot.py"
ACCOUNT_SHA = "d49f9ed2e49bd7aa0674f59a10a03380e46c5fb1b52839d0e5a60c157b6cd1fd"
RAW = HERE / "PRIVATE_THREAD_TERMINAL.csv"
RAW_SHA = "e1846fe314c5ac9f49b4794cf92dad4cdef0ce9b6afdc300cd1974486027ed8c"
SCHEMA = ["kind", "event_sequence", "qpc", "cpu_index_flag", "cpu_effective", "cpu_processor_index",
          "cpu_processor_number", "event_header_flags", "opcode", "version", "payload_bytes", "new_tid",
          "old_tid", "old_state_byte", "payload_pid", "payload_tid", "header_pid", "header_tid"]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_new(name, obj):
    with (HERE / name).open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2)


def load_helper():
    data = HELPER.read_bytes()
    if hashlib.sha256(data).hexdigest() != HELPER_SHA:
        raise ValueError("helper binding differs")
    module = types.ModuleType("saved_file_helper")
    module.__file__ = str(HELPER)
    exec(compile(data, str(HELPER), "exec"), module.__dict__)
    return module


def main():
    helper = load_helper()
    derivation = HERE / "DERIVATION_RESULT.json"
    summary_file = HERE / "decoder.stdout.json"
    inputs = [PRIVATE, COVERAGE, HELPER, AUDIT, ACCOUNT, RAW, derivation, summary_file, Path(__file__).absolute()]
    with helper.PinnedInputs(inputs):
        input_hashes = {str(path): digest(path) for path in inputs}
        for path, expected in ((HELPER, HELPER_SHA), (AUDIT, AUDIT_SHA), (ACCOUNT, ACCOUNT_SHA), (RAW, RAW_SHA)):
            if input_hashes[str(path)] != expected:
                raise ValueError("explicit saved input/source binding differs")
        old = json.loads(PRIVATE.read_text())
        coverage = json.loads(COVERAGE.read_text())
        summary = json.loads(summary_file.read_text())
        d = json.loads(derivation.read_text())
        if d["private_csv_sha256"] != RAW_SHA or d["input_sha256"] != "3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870" or not d["summaries_and_counts_usable"]:
            raise ValueError("fresh saved ETL derivation binding differs")
        audit = helper.load_bound_audit(AUDIT, ACCOUNT, AUDIT.read_bytes(), ACCOUNT.read_bytes())
        lifetimes = audit.__globals__["lifetimes"]
        target = {entry["tid"]: entry for entry in old}
        if len(target) != len(old):
            raise ValueError("historical private selection duplicates a TID")
        pids_zero_end_only = {tid for tid, entry in target.items() if len(entry["thread_events"]) == 1
                             and entry["thread_events"][0][0] == 4 and entry["thread_events"][0][2] == 0}
        spans = {}
        for tid, entry in target.items():
            try:
                spans[tid] = lifetimes(entry["thread_events"], summary["first_qpc"], summary["last_qpc"])
            except ValueError:
                spans[tid] = []
        begin, end = coverage["window_qpc"]
        if [begin, end] != [104557006279, 105157006279]:
            raise ValueError("historical comparison window differs")
        last = {}
        raw_threads, switchins, switchouts = defaultdict(list), defaultdict(list), defaultdict(list)
        unknown = []
        counts = Counter()
        with RAW.open("r", encoding="ascii", newline="") as stream:
            reader = csv.reader(stream)
            if next(reader) != SCHEMA:
                raise ValueError("new private schema differs")
            for row in reader:
                if len(row) != 18:
                    raise ValueError("new private row width differs")
                kind, sequence, stamp = map(int, row[:3])
                counts["rows"] += 1
                if kind == 2:
                    counts["thread"] += 1
                    op, pid, tid, header_pid, header_tid = (int(row[i]) for i in (8, 14, 15, 16, 17))
                    if tid in target:
                        raw_threads[tid].append(dict(op=op, qpc=stamp, pid=pid, tid=tid,
                                                     header_pid=header_pid, header_tid=header_tid, sequence=sequence))
                    continue
                if kind != 1:
                    raise ValueError("unexpected new numeric kind")
                counts["cswitch"] += 1
                flag, cpu, new_tid, old_tid, state = (int(row[i]) for i in (3, 4, 11, 12, 13))
                if flag != 1 or not 0 <= cpu < summary["processors"]:
                    raise ValueError("unsupported saved CPU namespace")
                if new_tid in target:
                    switchins[new_tid].append((stamp, sequence, cpu))
                if old_tid in target:
                    switchouts[old_tid].append((stamp, sequence, cpu, state))
                if cpu in last:
                    before, prior_new = last[cpu]
                    if stamp < before:
                        counts["backwards"] += 1
                    elif prior_new != old_tid:
                        counts["discontinuities"] += 1
                    else:
                        a, b = max(before, begin), min(stamp, end)
                        if a < b and old_tid in target and not any(s[0] <= a <= b <= s[1] for s in spans[old_tid]):
                            unknown.append(dict(tid=old_tid, cpu=cpu, a=a, b=b, raw_begin=before,
                                                switchout_qpc=stamp, old_state_byte=state, sequence=sequence))
                last[cpu] = stamp, new_tid
        if (counts["rows"], counts["cswitch"], counts["thread"]) != (summary["decoded_rows"], summary["cswitch_rows"], summary["thread_rows"]):
            raise ValueError("new row counts differ from fixed decoder summary")
        thread_mismatches = sum(sorted((r["op"], r["qpc"], r["pid"]) for r in raw_threads[tid])
                                != sorted(tuple(r) for r in target[tid]["thread_events"]) for tid in target)
        if thread_mismatches:
            raise ValueError("historical selected thread events differ from new dual-identity extraction")
        per_tid = Counter()
        for interval in unknown:
            per_tid[interval["tid"]] += interval["b"] - interval["a"]
        selection_matches = all(per_tid[tid] == entry["qpc_ticks"] for tid, entry in target.items())
        total_ticks = sum(per_tid.values())
        if not selection_matches or len(unknown) != 1328 or total_ticks != 4392592:
            write_new("SELECTION_MISMATCH.json", dict(intervals=len(unknown), qpc_ticks=total_ticks,
                         all_historical_per_tid_totals_match=selection_matches,
                         reason="Thread-only reconstruction must not be forced to explain process-boundary gaps", admission="BLOCKED"))
            raise ValueError("thread-bound reconstruction does not reproduce historical unknown intervals")

        groups = defaultdict(lambda: dict(intervals=0, ticks=0, states=Counter()))
        cases, end_keys = [], set()
        for interval in unknown:
            tid, a, b = interval["tid"], interval["a"], interval["b"]
            label = "PID0_DCEnd_only_unattributed" if tid in pids_zero_end_only else "other_thread_bound_gap"
            group = groups[label]
            group["intervals"] += 1;group["ticks"] += b-a;group["states"][interval["old_state_byte"]] += 1
            if tid in pids_zero_end_only:
                cases.append(dict(interval, category=label))
                continue
            ends = [r for r in raw_threads[tid] if r["op"] == 2 and r["qpc"] <= interval["switchout_qpc"]]
            if not ends:
                cases.append(dict(interval, category="no_prior_ThreadEnd"))
                continue
            ending = max(ends, key=lambda r: (r["qpc"], r["sequence"]))
            relation = "strictly_crosses_ThreadEnd" if a < ending["qpc"] < b else "starts_at_ThreadEnd" if a == ending["qpc"] < b else "fully_after_ThreadEnd" if ending["qpc"] < a else "ends_at_or_before_ThreadEnd"
            new_starts = [r for r in raw_threads[tid] if r["op"] == 1 and ending["qpc"] < r["qpc"] <= interval["switchout_qpc"]]
            reentries = [r for r in switchins[tid] if ending["qpc"] < r[0] < interval["switchout_qpc"]]
            entry = dict(interval, category=relation, thread_end_qpc=ending["qpc"],
                         end_header_payload_match=(ending["pid"], ending["tid"]) == (ending["header_pid"], ending["header_tid"]),
                         intervening_new_Starts=len(new_starts), intervening_switchins=len(reentries))
            cases.append(entry)
            end_keys.add((tid, ending["qpc"], ending["sequence"]))

        generations = []
        for tid, ending, sequence in sorted(end_keys):
            next_start = min((r["qpc"] for r in raw_threads[tid] if r["op"] == 1 and r["qpc"] > ending), default=summary["last_qpc"]+1)
            outs = [r for r in switchouts[tid] if ending <= r[0] < next_start]
            if not outs:
                generations.append(dict(tid=tid, end_qpc=ending, outgoing_csw_after_end=0))
                continue
            final = max(outs, key=lambda r: (r[0], r[1]))
            ins = [r for r in switchins[tid] if ending < r[0] < final[0]]
            starts_before_final = [r for r in raw_threads[tid] if r["op"] == 1 and ending < r["qpc"] <= final[0]]
            generations.append(dict(tid=tid, end_qpc=ending, outgoing_csw_after_end=len(outs),
                                    final_out_qpc=final[0], final_old_state_byte=final[3],
                                    switchins_strictly_between_end_and_final=len(ins),
                                    new_starts_between_end_and_final=len(starts_before_final),
                                    end_to_final_qpc_ticks=final[0]-ending,
                                    final_precedes_next_observed_Start=final[0] < next_start))
        public_groups = {name: dict(intervals=g["intervals"], qpc_ticks=g["ticks"], seconds=g["ticks"]/summary["qpc_frequency"],
                                   old_state_byte_counts=dict(sorted(g["states"].items()))) for name, g in groups.items()}
        relation_counts = Counter(case["category"] for case in cases)
        relation_states = defaultdict(Counter)
        for case in cases:
            relation_states[case["category"]][case["old_state_byte"]] += 1
        generation_state_counts = Counter(g["final_old_state_byte"] for g in generations if "final_old_state_byte" in g)
        result = dict(scope="SAVED_TRACE_UNKNOWN_THREAD_TERMINAL_TIMING_DIAGNOSTIC_ONLY",
                      utc=datetime.now(timezone.utc).isoformat(), input_sha256=input_hashes,
                      window_qpc=[begin, end], qpc_frequency=summary["qpc_frequency"],
                      selected_thread_count=len(target), reconstructed_unknown_intervals=len(unknown),
                      reconstructed_unknown_qpc_ticks=total_ticks, reconstructed_unknown_seconds=total_ticks/summary["qpc_frequency"],
                      all_selected_thread_event_tuples_match_new_extraction=True,
                      all_historical_per_tid_unknown_totals_match=True, global_backwards=counts["backwards"],
                      global_discontinuities=counts["discontinuities"], groups=public_groups,
                      interval_relation_counts=dict(sorted(relation_counts.items())),
                      old_state_byte_by_interval_relation={k: dict(sorted(value.items())) for k, value in relation_states.items()},
                      intervals_with_intervening_new_Start=sum(c.get("intervening_new_Starts", 0) > 0 for c in cases),
                      intervals_with_intervening_switchin=sum(c.get("intervening_switchins", 0) > 0 for c in cases),
                      associated_ThreadEnd_generations=len(generations),
                      final_out_old_state_byte_counts=dict(sorted(generation_state_counts.items())),
                      generations_with_no_outgoing_after_end=sum(g["outgoing_csw_after_end"] == 0 for g in generations),
                      generations_with_reentry_before_final_out=sum(g.get("switchins_strictly_between_end_and_final", 0) > 0 for g in generations),
                      total_reentries_before_final_out=sum(g.get("switchins_strictly_between_end_and_final", 0) for g in generations),
                      generations_with_new_Start_before_final=sum(g.get("new_starts_between_end_and_final", 0) > 0 for g in generations),
                      maximum_end_to_final_qpc_ticks=max((g.get("end_to_final_qpc_ticks", 0) for g in generations), default=0),
                      thread_header_payload_mismatch_by_opcode=summary["thread_header_payload_mismatch_by_opcode"],
                      raw_identity_records_private_only=True, no_pid_zero_exemption=True,
                      state_four_is_observed_terminated_byte_not_ownership_authority=True,
                      reused_TID_requires_next_Start_boundary_not_unbounded_extension=True,
                      ownership_extended=False, cpu_identity_topology_proven=False,
                      protected_process_coverage_proven=False, other_partition_coverage_proven=False,
                      original_audit_execution_binding_proven=False, coverage_complete=False,
                      I1_I7="OPEN", admission="BLOCKED")
        for path in inputs:
            if digest(path) != input_hashes[str(path)]:
                raise ValueError("pinned saved input changed")
        write_new("PRIVATE_UNKNOWN_TERMINAL_INTERVALS.json", cases)
        write_new("PRIVATE_END_GENERATIONS.json", generations)
        write_new("TERMINAL_DIAGNOSTIC_SUMMARY.json", result)
        print(json.dumps({k: result[k] for k in ("reconstructed_unknown_intervals", "reconstructed_unknown_seconds", "groups", "interval_relation_counts", "final_out_old_state_byte_counts", "generations_with_reentry_before_final_out", "total_reentries_before_final_out", "generations_with_new_Start_before_final", "admission")}))


if __name__ == "__main__":
    main()
