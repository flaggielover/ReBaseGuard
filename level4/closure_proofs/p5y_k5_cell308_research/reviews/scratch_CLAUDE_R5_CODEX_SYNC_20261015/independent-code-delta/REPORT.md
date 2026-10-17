# Independent immutable delta review — repaired selective integration

**Bounded code correctness verdict: no remaining blocker found in the reviewed repair delta. Original findings F1–F4 are repaired for the tested contracts. No new substantive regression was found.** This verdict is limited to synthetic evidence and the exact source bytes below. It grants no formal/governance, route, host, campaign, science, target, or execution acceptance. A1/A2/A5 remain unmet, and operational readiness remains false.

I authored none of the four reviewed snapshots and made no product/test-source edits, commits, or pushes. The original review/report is preserved verbatim and retains its original verdict for its original bytes.

## Immutable source binding

All hashes were independently calculated before imports, matched against the supplied delta `SOURCE_BINDINGS.json`, and rechecked after probes:

| Snapshot under `code-review-delta-input/` | SHA-256 |
| --- | --- |
| `lx_platform.py` | `2f0489d376a7129ce4416004c37d1cf66f2bcfbede5a653ed068e382919fae15` |
| `lx_verified.py` | `b78756eb377e91c4877b5bf0f96557257da64d4ac464ae339080e9f9e0ca29a9` |
| `tests/test_sync_boundaries.py` | `3af0af36dfa7078e3f246b196c58d08eb976d1bdd8ae8d81cb326e035e55e082` |
| `tests/test_lx_verified.py` | `041b8dcf15fe5c998f140f9a9126676f301ea52401fc08eeb77069a738a4c781` |

The wrapper and its supplied tests are byte-identical to the original review inputs. `SOURCE_BINDINGS.json` includes repository-relative paths and observed equality; the coordinator must separately verify equality with final committed bytes. This report does not assert that final binding.

Original report: `/tmp/cell308-claude-sync-20261015/independent-code/REPORT.md`, SHA-256 `d76387f9a556873ee87bef4a97a7c3e417c6ae61ed324120f6d21cfc0c044033`; unchanged after delta review, recorded in `ORIGINAL_REPORT_PRESERVATION.json`.

## Repair verification

### F1 — formerly P2, quoted review paths bypassed vetoes: repaired

`lx_platform.py:1176–1186` now parses complete NUL-delimited byte records with strict UTF-8 decoding. Both direct and recursive listings at `1198–1199` request `-z`; blob reads use the resulting complete paths. A readable committed veto under each original ASCII, Unicode, space, tab, and newline filename now rejects the attestation. The positive accepting controls still verify before the veto is added. Fresh controls also rename the valid direct acceptance itself to UTF-8/tab/newline names; all remain valid, so the repair preserves positive pathname support rather than merely refusing those files.

Malformed/unterminated/NUL-empty/non-UTF-8 listing controls refuse explicitly. A real synthetic Git tree containing a non-UTF-8 pathname also refuses explicitly. The latter tree was constructed from a planted blob and Git index entry inside the temporary fixture repository; no host path was read.

Evidence: `acceptance_probes.json`, `delta_adjacent_probes.json`, and the corresponding scripts. All original case semantics are retained, with explicit updated refusal assertions in `assert_delta_expectations.py`.

### F2 — formerly P2, unreadable veto evidence became no veto: repaired

`lx_platform.py:1200–1210` now refuses verification when a required listing or blob is unavailable/malformed/non-UTF-8. It returns no acceptances and an explicit `UNAVAILABLE` sentinel. `1218–1219` also refuses inconsistent direct/recursive accepting evidence. The record cache means the verdict decision uses the same blob text already included in the veto scan.

The exact original recursive-listing and veto-blob fault cases now return `verified=False` with explicit reasons, whereas the readable veto control continues to reject. Additional fresh probes cover direct-list failure, malformed direct/recursive listing data, missing accepting-file membership, unavailable accepting blob, and binary accepting blob. All refuse, and all positive acceptance controls still verify.

### F3 — formerly P2, unknown PID 1 could imply disabled units: repaired

`lx_platform.py:850–866` now distinguishes strict `True`, strict `False`, and other supervisor results. Only strict `False` reaches the non-systemd fallback. Unknown/nonboolean supervisor values return `None`, while the systemd branch still requires recognized inactive/failed activity before disabled/not-found can count as disabled.

The unchanged original probe matrix now returns unknown for `systemd_is_pid1=None`; the composed `auto_update_settings` reports `guest_updates_shown_disabled=False`, with unknown unit readings counted as enabled-or-unknown. Fresh controls include `None`, integer 0/1, a string, and a list; none becomes a disabled-unit assertion. Positive non-systemd and recognized activity controls remain intact.

### F4 — formerly P3, malformed numeric readers raised: repaired

The bounded `_nint` parser at `lx_platform.py:299–309` requires string input, an ASCII decimal token, an explicit 4300-digit bound, and guarded integer conversion. `suspend_success_count` at `312–314` and `_cg_val` at `469–473` use it. The cgroup `max` token remains a separate recognized string.

Every original superscript/Unicode-digit/bytes/integer/bool malformed reading now returns `None`, including at the canonical mocked `_read` boundary. Additional controls verify signs, empty/malformed tokens, a digit string over the explicit bound, and a temporarily tighter configured interpreter digit limit. No conversion exception escapes those completed probes. Valid zero, leading-zero, and whitespace-trimmed ASCII readings retain their values.

Thermal zone/trip numerics at `445–452` use the signed form. Negative and nonnegative ASCII temperatures parse correctly; plus-prefixed, double-minus, superscript, fullwidth/Arabic digits, bytes, integers/bools, absence, and overlong values produce `None`. Zone and trip controls agree.

## Adjacent integration checks and conservative limits

The 77 supplied synthetic tests and original independent probes continue to exercise strict identity schemas, positive death evidence, exact observed-parent ownership, duplicate PID/counter/numeric refusal, full interval clocks/counters/order, strict proc-view checks, malformed Git arguments/absence, direct review membership/single verdict/commit ordering, initial namespace plus D-HOST-LIFETIME root provenance, and fresh launch/preflight composition.

The repaired delta leaves those implementation paths unchanged except the specific repaired readers. The observer continues to bind canonical repository/current-machine verification, distinguish a record's root claim from the root contract, withhold effective limit/headroom, label memory raw, expose no caller-selected trust seams, keep the other-campaign detector unknown, and return `operational_ready=False` with A1/A2/A5 unmet. Empty `DECIDED`, all 21 decision IDs, false journal-reader status, undefined fixed science module list, and static pin-point refusal remain intact. No pin point was invoked.

One conservative availability restriction is recorded, not treated as an acceptance bypass or operational blocker: a direct **directory** named `REVIEW_HOST_ATTESTATION_*.md` is listed by the direct tree scan but absent from recursive file records, so `1218–1219` returns explicit `UNAVAILABLE` even when another valid acceptance exists. Non-UTF-8 review paths or contents likewise refuse verification rather than being skipped. These behaviors can deny verification; they do not establish authority from incomplete evidence. The numeric probes cover the repaired suspend/cgroup/thermal boundaries, not an assertion that every other parser in this large development module accepts no malformed input.

## Synthetic execution evidence and limits

Before controlled imports, all four delta files were hashed and their top-level AST inspected. `AST_IMPORT_PRECHECK.json` records the nodes; the new helpers are definitions, not top-level reads. Imports resolve precisely to the immutable delta snapshot with bytecode writing disabled and `LX_PLATFORM_DIR` set to that snapshot.

- The two supplied copied test files ran once as a complete suite: **77 tests, zero failures/errors/skips**, Python 3.14.5. See `supplied_tests.log` and `supplied_tests.json`.
- The original independent scripts reran the same **13 acceptance, 56 composition, and 32 numeric/order cases**. `assert_delta_expectations.py` explicitly validates all **101** case results, retains original cases/inputs, and changes only the expected repaired refusal outcomes. Comparisons normalize only the planted fixture process PID because each run uses its own Python process.
- Fresh adjacent scripts produced **102 asserted result rows** covering NUL transport, ASCII/digit-bound/type refusals, signed thermal values, supervisor schemas, actual temporary Git fixtures, required-evidence faults, and conservative refusal limits. These are result/assertion counts, not 203 additional unittest methods. All completed assertions pass.

Raw reader functions are denied unless replaced with specific synthetic fixtures. Audit hooks forbid `/proc`, `/sys`, relevant host identity/OS/systemd paths and non-Git subprocesses; guarded stat/readlink provide additional checks. Git subprocesses are restricted to controlled temporary fixture repositories. Every completed run records **zero unexpected host-access attempts**. Actual systemctl, process signal/probe, host inventory, candidate/science, evaluator, qualification, campaign, target steps, and pin-point execution were neither needed nor performed.

The adjacent probe fixture was corrected during development for a missing local helper constant and for macOS rejecting an invalid-UTF-8 working filename; the final invalid-path control uses a synthetic Git blob/index entry without creating that filename in the filesystem. These were probe-scaffolding issues, not product failures, and do not alter the completed 77-test result.

I did not read mutable working product/test/harness changes or mutant results. No prohibited interruption/incident/exposure records, target-run material, Cell309 files, broad namespace inventory, quarantine CLI, actual repository recursive veto scan, real-host queries, science/evaluator/candidate runs, or governance acceptance actions were performed. All original review inputs/artifacts remain unchanged. No real-host facts, reviewer independence, scientific validity, or operational authorization follow from this bounded delta verdict.
