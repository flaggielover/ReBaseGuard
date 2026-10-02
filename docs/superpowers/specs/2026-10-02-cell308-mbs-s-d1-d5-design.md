# Cell-308 MB-S D-1–D-5 bounded repair design

## Scope

This successor starts at clean commit `d4734231` on `p5y-k5-cell308-mbs-r1`. It repairs only the five bounded implementation defects identified by reviewF8. It does not alter scientific functions, operational constants, accepted owner records, accepted R-rules, historical reviewF8, or cell membership. It does not run designation, apply, freeze, qualification, grant, or any cell-308/cell-309 target evaluation.

## Design

D-1 makes series history authoritative in a fixed campaign ledger independent of `--work`. A series is recorded when it starts and its terminal status is appended in the same fixed location. Designation, derivation, and official R-rule evaluation refuse when any earlier series carries `STEP1_RERUN_REQUIRED`; no alternate worktree or later clean series can hide that event. The existing accepted owner supplement and designation rule remain the source of semantics.

D-2 adds a narrowly named verifier exception for the committed research-ledger line 418. Admission requires the exact line digest and all zero-exposure conditions: zero target evaluations, zero proxies, zero target-informed optimization, and no `LEAK_FLAG`. Any changed byte, second INCIDENT line, nonzero count, or leak flag fails closed. The historical ledger remains append-only and unchanged.

D-3 validates all recorded R-MEM peak values (job, driver, and watchdog when present) as positive integers before they enter the aggregate. Non-positive, non-integer, or malformed values produce a named invalid-input reason.

D-4 requires the official measurement series hosting-app paths to equal the designated evidence paths byte-for-byte. A missing or mismatched path fails closed before R-rule derivation.

D-5 extends QS-RESUME-DECOY so the failed decoy's watchdog outcome is read and propagated into the aggregate as `QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`.

## Verification

Each repair gets a regression case and, where applicable, a mutant that the assertion kills. On final committed bytes, run the affected static, launch, state, crash, qualification, disk, case, and decoy suites plus the complete mutant matrix. Read every mutant result's `error` field and require assertion-based kills. Re-run the governance-record check against the real committed research ledger. A fresh non-holder delta review must compare only against reviewF8's findings.

## Safety gates

All work is target-free. Tests may use only synthetic payloads and the existing permitted dev decoy. The work stops at `HOST_PREPARATION_REQUIRED` if host readiness is the only remaining blocker; no host settings or owner applications are changed. Cell309 remains out of scope.
