# Conservative saved-interval partition, v7

Pure supplied-data API:

`partition_interval(tid, (start, end), thread_generations, process_generations, (window_start, window_end))`

Maps are compatible with v4 `lifetimes()` output: numeric TID or PID maps to a list of `(start_qpc, end_qpc, identity, rundown_bool)`. Thread identity is PID; process identity is ProcessKey. The caller provides already derived generations. This module does not import v4, alter its lifetime rules, read ETL/CSV, infer missing rundown, or attest provenance/coverage.

All times are exact integer QPC and half-open intervals. Collect all touching thread generation and related PID process boundaries, clip to the requested window, then classify every positive-duration piece. Exactly one thread row and exactly one matching process row are necessary for KNOWN. Duplicate rows remain ambiguous even if their identities agree. Zero TID/PID/ProcessKey remains UNKNOWN; no idle exemption or terminal-tail extension. A zero-duration generation contributes a boundary but no CPU ticks. Adjacent end/start at the same QPC divides duration without claiming event ordering or identity at the zero-duration instant. Conflicting overlapping positive duration remains UNKNOWN.

Output includes original interval/window, clipped interval, every boundary with its source row/edge, piece-to-boundary indexes, all covering candidate rows, identity and reason. Generation ordinals identify rows in the supplied per-ID list, not global or authenticated generation IDs. KNOWN is only a local evidence classification, not a formal claim. Tick totals conserve clipped duration and retain duration outside the window separately. Inputs are not mutated. Malformed inputs raise ValueError rather than inventing an UNKNOWN row over invalid geometry.

The actual cross-ThreadEnd defect can recover only prefixes for which BOTH thread and process ownership are unique. The saved 0.1247455-second thread-only subtotal is not pre-subtracted. No actual saved numeric input was processed by preparing this module. The reported 0.4392592 seconds remains unchanged.

Integration must separately establish same-byte input binding, schema, clock/CPU namespace, CSwitch continuity, loss, complete generations and endpoint semantics. A real collector also needs generation identity and same-QPC ambiguity handling before supplying these intervals. This reference API validates whole input maps per invocation; a future indexed adapter should reuse validated immutable maps for large traces and must preserve these semantics. No live observer or production admission consumer is implemented here.

Tests are small supplied-data regressions for the actual boundary bug and its process-boundary counterexample, TID/PID reuse, duplicate/overlap ambiguity, same-QPC/zero duration, clipping/conservation, zero IDs and exact large timestamps. They are not host evidence. Intended interpreter: existing Windows Python 3.12.14, OFFLINE_ANALYSIS_TOOL only, not P309 private CPython 3.11.15 qualification.

No threshold changes. I1-I7 OPEN; formal admission BLOCKED. No host query, trace, UAC, VM, service, key or workload code. Historical v4/v5 files are untouched. Independent review and fixed binding precede any actual saved audit.
