# Independent observer test-only addendum

**Scoped verdict: the narrow observer-test change enforces the specific malformed-reference no-exception contract without weakening assertions. All 35 observer tests pass, and no new code correctness blocker was found.** The repaired product verdict remains the separate immutable delta review's bounded verdict. No formal/governance, route, host, science, campaign, target, or execution acceptance follows. Operational readiness remains false and A1/A2/A5 remain unmet.

## Final four-input binding

A new private combined snapshot is at `/tmp/cell308-claude-sync-20261015/independent-code-observer-test-addendum/combined-input/`. All source and copied hashes were independently checked before imports and rechecked after the runs:

| Input relative to `combined-input/` | SHA-256 |
| --- | --- |
| `lx_platform.py` | `2f0489d376a7129ce4416004c37d1cf66f2bcfbede5a653ed068e382919fae15` |
| `lx_verified.py` | `b78756eb377e91c4877b5bf0f96557257da64d4ac464ae339080e9f9e0ca29a9` |
| `tests/test_sync_boundaries.py` | `e305c7f847c2dd1a807c4e14eb1bfd965259753ab9655b486d96a168818e4451` |
| `tests/test_lx_verified.py` | `e1214c519c0cfb2fa8fedb890da54208f2c206c0cfe3ae696974170a731811c2` |

Only the observer-test hash changes from the previous four-file binding (`041b8dcf15fe5c998f140f9a9126676f301ea52401fc08eeb77069a738a4c781`). Platform, wrapper, and final boundary-test bytes are unchanged. `SOURCE_BINDINGS.json` records source, copied snapshot, and repository paths. The coordinator must separately match these hashes to final committed bytes; this report does not claim that binding.

## Exact change and contract analysis

`OBSERVER_TEST_DELTA.diff` shows one change inside `TestVerifiedObservation.test_invalid_reference_paths_are_refused_without_exceptions` (`test_lx_verified.py:196`). For the same two planted paths (embedded NUL and invalid surrogate), the unchanged `self.assert_unverified(dict(valid, path=path))` call is placed in a `try` block. The only handler catches `(ValueError, UnicodeError)` and unconditionally calls:

```python
self.fail(f"Malformed reference must be refused without leaking {type(escaped).__name__}")
```

The public observer is expected to return an unverified, nonready result with reasons for those malformed references. A leaked malformed-argument/encoding exception is a direct violation of that advertised boundary property, so an explicit unittest failure is justified. It is not treated as successful verification or a passing test.

Normal-return assertions are preserved in `assert_unverified`: unverified attestation, no root authority, nonempty refusal reasons, raw/withheld memory quantities, false readiness, and unmet A1/A2/A5. There is no `pass`, blanket `except Exception`, `else`, or `finally` that could turn a failure into success. Unrelated exception types continue to propagate. No harness classification logic was reviewed or changed by this addendum, and this report supplies no credit for arbitrary runtime exceptions.

Independent AST comparison confirms exactly one method changes, the original assertion call is identical, all other AST nodes are unchanged, and the test-method inventory remains **35**. `SEMANTIC_TEST_DELTA.json` records the specific handler classes and unconditional failure call.

## Synthetic tests and fresh probes

`run_observer_tests.py` ran only the copied final observer-test file against the unchanged reviewed platform/wrapper: **35 tests, zero failures/errors/skips**, Python 3.14.5. The run is recorded in `supplied_tests.log` and `supplied_tests.json`.

A fresh independent probe produced **27 checked result cases**:

- Thirteen malformed/absent path forms, including embedded NUL at different positions, high/low surrogates, wrong types, empty and missing paths, return unverified/nonready results with reasons and no escaped exception.
- Seven other malformed-reference forms return the same safe refusal shape.
- A valid committed UTF-8 pathname still verifies while retaining raw quantities, false operational readiness, and unmet conditions.
- Six fault-injected handler controls demonstrate the test's exact behavior without changing product/test source: ValueError, UnicodeError, and UnicodeEncodeError become explicit AssertionError test failures with the specific malformed-reference message; unrelated TypeError and RuntimeError propagate unchanged; an existing AssertionError remains the same assertion failure. No exception is swallowed.

See `probe_malformed_reference_contract.py` and `malformed_reference_probes.json`. These are public-boundary and handler semantics probes, not mutations or a claim about arbitrary exception-based mutation outcomes.

The prior final-boundary addendum ran **42 tests** against the identical final boundary hash and the identical product hashes. This addendum supplies the separate final **35-test observer run**. I did not rerun a combined 77-test invocation or full native CI here. The original 77-test run retains its original older test-file bindings; no earlier report is relabeled.

## Safeguards, preservation, and limits

All four combined files were hashed and inspected via top-level AST before controlled imports (`AST_IMPORT_PRECHECK.json`). `LX_PLATFORM_DIR` selects the new combined snapshot, imports resolve to that snapshot, and bytecode writes are disabled.

Raw host readers are denied unless replaced with explicit synthetic fixtures. Audit hooks reject `/proc`, `/sys`, relevant identity/OS/systemd paths and non-Git subprocesses; stat/readlink are guarded; Git runs only in controlled temporary fixture repositories. Both completed runs record **zero unexpected host-access attempts**. Actual host inventory/systemctl, process signals/probes, pin point, candidate/science, evaluator, qualification, campaign, target execution, and governance acceptance were not accessed or run.

Only the named immutable observer-test addition, earlier reviewed immutable inputs, and my own review artifacts were read. No mutable working sources, harness changes, mutant results, prohibited interruption/incident/exposure records, target-run artifacts, Cell309 material, broad namespace inventory, quarantine CLI, or actual repository recursive veto evidence were inspected. No product/test-source edits, commits, or pushes were made. All prior reports and snapshots remain unchanged; `PRIOR_REPORT_PRESERVATION.json` rechecks the three previous report hashes. This verdict establishes only the stated code/test correctness observations, not host facts, scientific validity, reviewer independence, or operational authority.
