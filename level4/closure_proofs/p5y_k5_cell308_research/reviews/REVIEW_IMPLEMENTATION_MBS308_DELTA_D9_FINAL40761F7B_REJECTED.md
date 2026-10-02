# Cell-308 MB-S final-byte matrix reviewD9: 40761f7b
DELTA_REJECTED

Reviewer: reviewD9 (fresh non-holder; no MB r1 run observation supplied)
Date: 2026-10-03

## Candidate and scope

Reviewed successor config/revision commit `40761f7b3633d47a964b96879839ef449f08334b`
(parent `9e0e98d07b0e702c6d9848abc54e8ba36ee3544a`, branch `p5y-k5-cell308-mbs-r1`).
This is a final-byte evidence review only; the earlier scoped acceptance in
`REVIEW_IMPLEMENTATION_MBS308_DELTA_D9_ACCEPTED.md` is preserved and is not overwritten.
No target evaluation, measurement, official qualification, freeze, apply, grant, marker,
pending-result or seal operation was performed by this reviewer.

## Final evidence

The supplied report files are:

- `/private/tmp/codex-cell308-builder8-final-40761f7b/reports/mutants.json`
- `/private/tmp/codex-cell308-builder8-final-40761f7b/reports/mutants.run.json`

The seven reported suites pass on AC-valid final-byte runs: static 10/10, launch 13/13,
state 56/56, qualify 29/29, disk 30/30, cases 28/28 and crash 50/50. The mutant report,
however, records 294/297 killed, `survivors: ["MB104", "MQ44", "MQ50"]`, `not_run: []`,
and `unmutated_all_pass: true`. The run report confirms `valid_ac_window: true`, AC power
before and after, return code 1, one `error_rows` entry and zero unmutated errors.

## Blocking findings

1. **MB104 is invalid rather than killed.** Its result has
`error: "INVALID MUTANT RuntimeError: MB104: the fragment occurs 0 times in mbs308_measure.py"`,
`killed: false`, `result_verified: false`, and `test_passed: true`. This is not an
assertion-killed mutant and leaves the declared matrix incomplete.

2. **MQ44 survives.** Its target is `qualify::t_qc12s_raw_text_only_match`; the result is
`error: null`, `rc: 0`, `result_verified: true`, `killed: false`, and `test_passed: true`.
The mutant therefore preserves the forbidden raw/decoded QC12 behavior.

3. **MQ50 survives.** Its target is `qualify::t_qc12s_json_escaped_figure`; the result is
`error: null`, `rc: 0`, `result_verified: true`, `killed: false`, and `test_passed: true`.
The mutant therefore preserves the forbidden outside-post-freeze decoded-scan behavior.

These are blocking because brief 58 requires the full mutant matrix, every result read for
an `error` field, and each kill to be an assertion. The report instead has one invalid
mutant and two true survivors. The earlier acceptance is therefore scoped mechanics only,
not final completion.

## Required follow-up boundary

Builder8 must repair MB104's stale mutation fragment and add/repair the necessary regression
and mutant coverage for MQ44 and MQ50 (and recheck D-1..D-5/G8/O8/T riders as applicable),
then provide a new immutable candidate and AC-valid final-byte suite/matrix reports. Until
that fresh review passes, no complete-all claim or operational step is supported. No code
or configuration was changed by this reviewer.
