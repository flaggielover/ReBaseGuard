# Bounded R1 fixture-repair review before native R2

**Verdict: no concrete material issue found in the three reviewed test-file repairs.** The changes preserve direct property witnesses and assertion strength, use genuine distinct subtest identities, and isolate temporary Git activity without suppressing cleanup failures. This is a static review plus inspection of the supplied targeted evidence, not native R2 validation, full-suite success, host acceptance, scientific acceptance, or execution authority.

## Exact binding and scope

Worktree: `/Users/suzhe/.codex/worktrees/cell308-claude-r5-sync/ReBaseGuard`. Baseline: `7eb9bbd999a1ec07d31a15f0b391fcc32ffa4d6b`. Under `level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV/tests/`, the exact reviewed hashes are:

| File | SHA-256 |
| --- | --- |
| `test_lx_platform.py` | `d961b25be1d6a64d0d7b4f40ba3bc137641ad1ed2402eace91720f082eb2fd54` |
| `test_lx_verified.py` | `4d096c43c07d9523fd464a1191dadb207f41d271bdcfe915235c880f5990e887` |
| `test_sync_boundaries.py` | `4487ce763b2a93d76c72c700cc7d005c42f4eb98272d9c6d8adc933af21bd00e` |

The observer filename is `test_lx_verified.py`; bounded directory-name metadata confirmed no `test_lx_verified_observer.py`. All three hashes match the requested freeze and were unchanged after review. Exact baseline diffs and baseline hashes are saved alongside `SOURCE_BINDINGS.json`. The supplied `three-tests.patch`, `source-freeze.json`, and `targeted-seven-mutations.json` are hash-bound in `EVIDENCE_BINDINGS.json`.

## Repair assessment

- At `test_sync_boundaries.py:188–195`, list-type and exact-length assertions precede birth/exit indexing. They strengthen the expected result shape and preserve the existing PID, birth/exit marker, and ownership assertions. Empty/missing results now fail a direct property assertion instead of leaking an indexing error. The separate unchanged process birth/exited witnesses also remain.
- At `test_sync_boundaries.py:473–488`, both unit and update observations are still computed under the same synthetic supervisor/activity mocks. The same expected identity comparisons remain, now split into `evidence="unit"` and `evidence="updates"` subtests. This allows both direct property failures to be recorded independently without weakening either check. No arbitrary exception is converted to a pass.
- At `test_lx_verified.py:272–278`, enumeration adds a stable case index to the subtest identity. The six fixture cases and `assert_unverified` call are unchanged. The same-path missing-verdict and extra-verdict cases are genuine different inputs; indices 4 and 5 identify them distinctly instead of giving two different witnesses the same label.
- At `test_lx_platform.py:1069–1074`, malformed-reference checks explicitly name a new temporary repository. The rejection assertions and input forms remain; the verifier no longer defaults to the actual project repository for that fixture loop.
- The new `fixture_git`/`git_init` helpers at `test_lx_platform.py:938–960` use checked subprocesses, disable automatic GC/maintenance, hooks, and filesystem monitoring for fixture commands, and persist those settings locally for the platform's read-only Git calls within each fixture. Existing commit-order, digest, committed-byte, and malformed-reference assertions remain unchanged. All affected repositories remain ordinary `TemporaryDirectory()` contexts. There is no cleanup-error suppression, `ignore_cleanup_errors`, catch-and-ignore cleanup path, or weakened Git return-code handling in these repairs. These flags reduce incidental background behavior; they do not prove the earlier native cleanup error's cause, which the supplied evidence correctly keeps **UNPROVEN**.

## Counts and targeted evidence

Static AST inspection confirms the method inventory is unchanged and unique: **89 platform + 35 observer + 42 boundary + 25 unchanged harness tests = 191 methods**. The unchanged `run_mutants.py` catalog is byte-identical to the baseline (`5d0e3b2b93441d438d574ce68fcc652337c16cb3209a98a3d0765d76f6e481cc`) and contains **133 unique mutant IDs**. No catalog or harness behavior was changed or executed by this review. See `COUNT_ID_CHECKS.json`.

The explicitly authorized targeted artifact records a clean **12-test baseline** and seven **KILLED** rows (`M24`, `N04`, `N06`, `N08`, `P04`, `Q07`, `CDEX16`). Every row has zero errors, no invalid reasons, unique recorded event IDs, and actual `builtins.AssertionError` identities with frames in the relevant property assertions. In particular, P04's observer failures have distinct case indices 4/5; Q07/CDEX16's unit/update failures have distinct evidence labels. Inputs before/after the targeted run are identical and new target evaluations are zero. The compact extraction is `TARGETED_SEVEN_SUMMARY.json`.

This is evidence for that local twelve-test/seven-mutation subset only. It does not establish all 191 runtime tests or all 133 mutant outcomes, native R2 success, or the cause/resolution of the prior cleanup failure. The requested native R2 run remains the next independent validation step.

## Review limits and preservation

I performed one bounded read-only review. I did not import or run the active tests/product/harness, launch any full suite, execute new mutants, run actual-host queries, or execute science/candidate/evaluator/qualification/campaign/target code. The only Git use was read-only retrieval of the explicitly named baseline file blobs. I did not change product, tests, harness, workflow, or prior reports.

Reads were limited to the three active test files and their exact baseline diffs, their needed fixture/witness context, the named targeted evidence, and static counts/byte equality for the two unchanged harness files. No prohibited interruption/incident/exposure/postexec/Cell309 records, broad namespace inventory, or actual repository recursive veto evidence were read. The four earlier independent reports remain byte-identical (`PRIOR_REPORT_PRESERVATION.json`). This additive report preserves all their original bindings and scope limits.
