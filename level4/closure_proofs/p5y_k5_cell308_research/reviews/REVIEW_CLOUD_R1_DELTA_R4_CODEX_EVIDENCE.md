# Cell308 revision 4: independent evidence and harness review

Reviewer: fresh independent final evidence/harness subagent, with no authorship of the revision-4 repairs. Date: 2026-10-15 (JST).

Reviewed repository: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Immutable HEAD: `aef3bead293759e0e4cc1af26e0c01f060bb9abc`. Initial working tree was clean. Historical baseline reviewed commit: `d423c7aacc4d1cc15f3c7d77aecb5257a0175392`.

## Dispositions

- **Historical 75-test record preservation: PASS.** `results/TEST_RUN.json` and `results/MUTANTS_RUN.json` are byte-identical to their d423c7 Git blobs. They remain explicitly described as revision-3 evidence; their 75-test / 65-mutant counts are not presented as current revision-4 runtime evidence.
- **Historical Linux replay attribution: PASS after independent adjudication.** The supplied replay records a clean baseline of 75 tests on Linux / CPython 3.12.3, followed by 64 assertion cases and M29's single required-key error. All 64 assertions have direct witnesses for the intended weakening. M29 is a valid behavioral kill of required launch-gate omission, as explained below; it is not a generic execution-error kill.
- **Current harness static and synthetic controls: PASS.** There are 103 unique test methods and exactly 73 unique mutant IDs: M=32, R=10, X=9, N=14, Y=3, P=5. Every sequential mutation anchor is unique and every resulting source parses. Baseline-first, cleaned LX_PLATFORM_DIR, strict failure classification, registry enforcement and fail-on-partial-run controls pass.
- **Current input/ledger consistency: PASS within this review's scope.** Seven permitted stream/evidence bindings in the explicit current repair line match independently recomputed SHA-256 values. The line's two governance bindings were not opened; the independent governance reviewer owns those checks.
- **Revision-4 recorded Linux runtime: PASS.** Independently assessed completed run 38636549368 at immutable aef3bead: the clean baseline ran 103 tests; all 73 mutants are complete, property-related assertion kills; there are zero errors, skips, timeouts or unapplied cases. Input hashes before and after match local bytes, every mutant digest/anchor count matches independent static construction, and every test traceback frame matches current source. This does not establish coverage of untested behaviors or imply a global fail-closed verdict.

These dispositions concern development evidence. They do not accept an amendment, ratify an open decision, or authorize an official step.

## Exposure and execution

Read the prior `reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX_EVIDENCE.md`; the current development harness, unit tests, active README, source bytes for mutation/AST/hash checks, inventory bytes for hashing, historical result records, the supplied historical Linux `validation.json` / `M29.json`, the final revision-4 Linux artifact `validation.json` / `input-commit.txt` / `full-output.json`, the narrowly requested repair ledger diff, `.github/workflows/cell308-dev-review.yml`, and `.github/scripts/cell308_dev_review.py`. Used Git to read only the same permitted historical source/test/harness/result paths and to verify HEAD/status. The ledger diff contains bookkeeping mentions of excluded material; no referenced excluded content was opened.

No forbidden audit, interruption assessment/review, coordinator exposure disclosure, MB-r1 postexecution/target-run record, or Cell309 file/branch/record was read. No full namespace listing/scan occurred. No science, candidate, decoy, target, cell, drift or qualification evaluator was executed. No lx_platform module or unit suite was imported or executed, and no full Mac or Linux suite was launched by this subagent. The only repository Python module imported was the target-free harness, which imports stdlib only and performs no suite call on import. Synthetic reports and mock run_suite/input_hashes functions exercised its classifier and final exit logic; mutation text was parsed, never executed. All generated material is under `/tmp/cell308-codex-review62`; no repository edits, commits or pushes were made.

## Current hashes and historical preservation

Paths below are relative to the development stream.

| File | Current SHA-256 |
|---|---|
| `lx_platform.py` | `d2ceb74e0eb3fae3a8349efaa18988cb56a9f03d4ff813d656eda5a082a328b5` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `tests/test_lx_platform.py` | `e1f2297dab51a87eb2fc3563c7029e27c8b5eea24205829086e79c27f722f784` |
| `tests/run_mutants.py` | `26347426ebb361c4a73232605a62dbb84dea7c45f683e00fedd42cbd5f706919` |
| `README_DEV_ONLY.md` | `0dbb30cdc28ec992992d4d8cef881c35d51015b092d3a324ccd5fe4ee010fc15` |

| Historical preserved record | SHA-256 at both commits |
|---|---|
| `results/TEST_RUN.json` | `2d1685940d855e9d1925670012b98d3445d4b18d5f840e4933205bd89d4f9e28` |
| `results/MUTANTS_RUN.json` | `e2db08c23013f03ccacb29b54d5094db47d0ba61f8b020251b7ebfb7a2b29f2c` |

The historical replay's source/test/harness hashes equal their d423c7 Git blob hashes, both before and after its run. Its standalone M29.json is exactly the M29 row in validation.json. The recorded historical interpreter is CPython 3.12.3 and kernel is 6.17.0-1022-azure. This replay corroborates that interpreter; the preserved earlier TEST_RUN's 3.11/3.13 claims were not independently replayed here.

## Historical property attribution

Independent inspection covered every complete failure/error section, its named test, observed result and corresponding test fixture. Every run reaches `Ran 75 tests`, exits 1, has no skip or timeout, and, except M29, contains assertion failures with zero unittest errors. The current strict parser accepts all 64 assertion runs and rejects M29 as ERROR until its behavior is manually adjudicated.

M29 changes `if mode in ("execute", "resume") or launched is not None:` to `if launched is not None:`. In the historical test, execute with no launch record then omits the required `launched_by_systemd` gate entirely. The traceback is solely `test_launch_record_fields_are_verified`, r3 test line 884, `self.assertEqual(g["launched_by_systemd"], L.FAIL, mode)`, with `KeyError: 'launched_by_systemd'`. This is the intended missing-gate behavior, with a clean baseline and complete test count; it is a **valid behavioral kill after explicit adjudication**. The revision-4 test now asserts required-key membership before accessing it, so the same omission becomes an assertion failure without relaxing the harness's no-error rule.

M16's crash child exits before the intended SIGKILL because writing directly to the existing target disrupts the exclusive temporary-file path. That secondary crash assertion alone would be less direct evidence. Its independent stale-temp and symlink assertions also fail (`StaleTmp not raised`, `OSError not raised`), directly detecting the same unsafe target-in-place weakening; M16 is therefore a valid kill.

The table lists a direct witness for each assertion case. All rows below are independently adjudicated VALID; full traces remain in the source artifact.

| ID | Intended weakening | Direct witness |
|---|---|---|
| M01 | failed boot-id read treated as a reboot (DEAD) | `test_failed_readings_are_unknown_never_dead` |
| M02 | unreadable /proc/<pid>/stat treated as DEAD | `test_failed_readings_are_unknown_never_dead` |
| M03 | incomplete identity record reported ALIVE | `test_unrecorded_fields` |
| M04 | zombie read as DEAD again (the withdrawn L-ID-1) | `test_zombie_is_never_proof_of_death` |
| M05 | pid reuse (other starttime) not detected | `test_positive_death_evidence` |
| M06 | no power supply exposed read as AC | `test_live_host_is_never_clean` |
| M07 | unreadable cgroup limit skipped | `test_partial_chain_never_numeric` |
| M08 | missing journal channel ignored in assess | `test_missing_channels_never_clean` |
| M09 | pause channel P removed | `test_pause_channel_is_ambiguous` |
| M10 | suspend (boottime - monotonic) ignored | `test_suspend_detected_just_above_tolerance` |
| M11 | D-MEM-FREE gate silently passes | `test_all_favourable_still_blocked` |
| M12 | attestation 'reviewed' not required | `test_forged_or_unaccepted_attestations_refused` |
| M13 | provider image updates pass without an attested token | `test_lifetime_gates_open_while_undecided` |
| M14 | update vectors other than apt ignored | `test_positive_evidence_only` |
| M15 | launched_by_systemd skips the MainPID check | `test_launched_by_systemd_requires_everything` |
| M16 | durable_write writes the target in place | `test_stale_tmp_is_a_named_state` |
| M17 | unreadable pin counts as a match | `test_unknown_interpreter_package_never_matches` |
| M18 | busy_processes uses lifetime ticks instead of the window | `test_window_not_lifetime_and_reuse_and_birth` |
| M19 | empty cmdline (failed read) hashed as a command | `test_empty_cmdline_is_a_failed_read` |
| M20 | UNKNOWN gates not reported as blocking | `test_unknowns_never_pass_and_are_reported` |
| M21 | headroom computed over levels with unreadable usage | `test_partial_chain_never_numeric` |
| M22 | namespace mismatch ignored | `test_namespace_mismatch_is_unknown` |
| M23 | unknown power-supply type skipped | `test_failed_or_unknown_supplies_are_unknown` |
| M24 | process born in the window not counted | `test_window_not_lifetime_and_reuse_and_birth` |
| M25 | attestation file sha256 not verified | `test_reference_digest_must_match_the_committed_file` |
| M26 | attestation not bound to the hardware identity | `test_forged_or_unaccepted_attestations_refused` |
| M27 | v2 root accepted as unlimited without attestation | `test_v2_root_and_memory_high` |
| M28 | effective_limit numeric without root attestation | `test_root_attestation_must_be_true` |
| M29 | execute / resume pass the launch gate without a launch record | `test_launch_record_fields_are_verified` — required-key error, explicitly adjudicated |
| M30 | mapped shared objects (libm) not pinned | `test_libm_change_with_same_glibc_string` |
| M31 | incomplete /proc view accepted | `test_no_reading_or_unsafe_inputs_fail_closed` |
| M32 | own may contain init | `test_no_reading_or_unsafe_inputs_fail_closed` |
| R01 | unreadable Battery status skipped (a failed read can yield AC) | `test_failed_or_unknown_supplies_are_unknown` |
| R02 | host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED') | `test_forged_or_unaccepted_attestations_refused` |
| R03 | durable_write never fsyncs the data | `test_fsyncs_file_then_directory` |
| R04 | suspend / pause tolerance raised from 2 s to 25 s | `test_suspend_detected_just_above_tolerance` |
| R05 | hidden name allow-list for the Cloud session controller in busy_processes | `test_no_name_or_path_allowlist` |
| R06 | package versions and glibc dropped from PIN_KEYS | `test_libm_change_with_same_glibc_string` |
| R07 | stopped (T/t) and uninterruptible (D) tasks read as DEAD | `test_live_task_states_are_alive` |
| R08 | durable_write never fsyncs the directory after the rename | `test_fsyncs_file_then_directory` |
| R09 | maximum sample spacing raised from 180 s to 390 s | `test_sample_spacing_boundary` |
| R10 | assess checks power only at start and end, not at the samples | `test_power_checked_at_every_sample` |
| X01 | /proc 'subset=' no longer refused | `test_proc_view` |
| X02 | no /proc mount line counts as a complete view | `test_proc_view` |
| X03 | unreadable livepatch counts as none applied | `test_positive_evidence_only` |
| X04 | K' monotonic-ahead-of-boottime channel removed | `test_monotonic_ahead_of_boottime_and_absent_samples` |
| X05 | durable_write read-back verification removed | `test_read_back_mismatch_is_detected` |
| X06 | absent samples no longer AMBIGUOUS | `test_monotonic_ahead_of_boottime_and_absent_samples` |
| X07 | a transient .scope accepted as the campaign unit | `test_launched_by_systemd_requires_everything` |
| X08 | v1 'unlimited' sentinel lowered to 1 GiB | `test_large_v1_limit_is_a_limit` |
| X09 | unknown interpreter package drops out of the pin | `test_unknown_interpreter_package_never_matches` |
| N01 | D-HOST-LIFETIME treated as decided | `test_lifetime_gates_open_while_undecided` |
| N02 | attestation acceptance line not required | `test_forged_or_unaccepted_attestations_refused` |
| N03 | attestation schema not checked | `test_forged_or_unaccepted_attestations_refused` |
| N04 | caller-asserted fields accepted in the attestation reference | `test_forged_or_unaccepted_attestations_refused` |
| N05 | root attestation truthy again | `test_root_attestation_must_be_true` |
| N06 | nested PID namespace view accepted | `test_proc_view` |
| N07 | boot id not validated | `test_boot_id_must_be_valid` |
| N08 | exited processes not reported | `test_exited_in_window_is_reported` |
| N09 | unreadable existing process skipped | `test_unreadable_existing_process_fails_the_snapshot` |
| N10 | campaign children exempt by pid alone | `test_reused_campaign_pid_does_not_exempt_children` |
| N11 | unrecorded namespace lets pid evidence count (revision-2 behaviour) | `test_unrecorded_namespace_never_proves_death` |
| N12 | pin without libm / libc / loader accepted | `test_required_members_and_pin_point` |
| N13 | launch record trusted on its 'pass' flag | `test_launch_record_fields_are_verified` |
| N14 | unrecognised battery status read as not discharging | `test_failed_or_unknown_supplies_are_unknown` |

## Harness controls and metadata

The baseline is the first suite subprocess. main removes inherited LX_PLATFORM_DIR and pins PYTHONDONTWRITEBYTECODE=1 before calling it. Each subprocess invokes the current interpreter with `-B -W error::ResourceWarning -m unittest discover ... -v`. Records preserve the full command, cwd, controlled environment values, stdout/stderr, elapsed time, normal/signal exit, timeout/launch error, parsed test count, summary and named failures/errors. The final record includes interpreter executable/real executable/version/implementation, host system/kernel/machine, per-mutant source digest and anchor counts, plus four input hashes before and after. Hash changes force overall failure.

KILLED requires a passing baseline, equal test count, consistent named failure tally and assertion failure summary, no errors/skips/expected failures/unexpected successes, no missing/malformed summary, no ResourceWarning/unraisable marker, and normal exit. It never automatically upgrades M29-style errors to kills. Human property attribution is still required when assessing the preserved full traces.

Synthetic classifier controls confirmed: an ordinary complete assertion failure -> KILLED; a passing complete suite -> SURVIVED; import error, missing summary, skipped test, short count, unexpected success, timeout, signal exit, ResourceWarning, unmatched names, launch error and exit/summary disagreement -> ERROR. Final main controls confirmed all 73 synthetic assertion kills -> exit 0; one short run, one survivor, failed baseline, or changed input hash -> exit 1. A failed baseline launches no mutant suite. Removing one registry ID raises ValueError; the exact expected group registry cannot silently shrink. An inherited deliberately poisoned LX_PLATFORM_DIR was absent from the synthetic baseline environment. These controls do not represent native platform runtime evidence.

## Workflow/script metadata

The active push workflow is restricted to the continuation branch and named development paths, grants contents:read, uses pinned checkout/upload action commits, and checks out the development snapshot at github.sha. It writes input-commit.txt, runs the revised run_mutants.py with a separate evidence output, retains complete stdout, and uploads evidence with always() even if the run fails. A timeout or interrupted run cannot establish success or the final before/after record. The validation-control checkout is currently unused by the active command.

The standalone `.github/scripts/cell308_dev_review.py` explains the historical replay: it records full traces and before/after hashes and clears LX_PLATFORM_DIR for baseline, but names assertion outcomes `KILLED_ASSERTION_REQUIRES_PROPERTY_REVIEW` and errors `ERROR_REQUIRES_REVIEW`. Its exit condition does not reject those human-review statuses. **NOTE:** its process success is not an adjudicated mutation verdict; the complete traces must be reviewed, as done above. The active workflow calls the repaired harness directly, so this legacy script behavior is not an active revision-4 CI defect.

## Prior finding disposition and remaining work

Prior E1 documentation/count/range/reference corrections are resolved: the current README identifies revision 4, says 103 tests / 73 mutants, describes the old result records as historical, and names amendment r4 for open decisions; the harness names N01-N14 and qualifies its optional output write. The tests identify revision 4. Prior E2's original evidence limitation is resolved for the historical baseline by complete traces and property attribution, and its harness weaknesses are repaired by the current strict baseline-first implementation. Native revision-4 confirmation is established for the supplied 103-test / 73-mutant artifact below. Separate code-review findings remain outside this evidence verdict.

New findings in this scoped subreview: BLOCKING 0; MAJOR 0; MINOR 0; NOTE 1 (legacy script's human-review statuses). No current behavioral or governance acceptance verdict is inferred from these counts.

Supporting local outputs: `static_checks.json`, `harness_controls.json`, `historical_adjudication_checks.json`, and `current_adjudication_checks.json`, beside this report.

## Final revision-4 Linux artifact assessment

Artifact directory: `/tmp/cell308-codex-review61/linux-r4-38636549368`. Input-commit.txt names `aef3bead293759e0e4cc1af26e0c01f060bb9abc`, the exact immutable reviewed HEAD. `validation.json` and `full-output.json` are byte-identical and parse to the same complete record. The record is SYNTHETIC_VALIDATION / dev_only, Linux x86_64, kernel 6.17.0-1022-azure, CPython 3.12.3 (`/usr/bin/python3`, real `/usr/bin/python3.12`), timestamp 2026-10-14T21:03:22Z, new_target_evaluations=0.

The baseline command is `/usr/bin/python3 -B -W error::ResourceWarning -m unittest discover -s <snapshot development tests> -v`; its controlled environment records LX_PLATFORM_DIR=null and PYTHONDONTWRITEBYTECODE=1. It reports Ran 103 / OK, returncode=0, no failures/errors/skips/invalid reasons, no timeout or launch error. Every mutant uses the same command/cwd with its temporary LX_PLATFORM_DIR, reports Ran 103, normal returncode=1 and one or more named assertion failures, with zero errors/skips/invalid reasons. Independent recomputation of the strict classifier yields 73 KILLED and no other status. IDs/properties exactly match the full expected registry. All 73 mutated source hashes and sequential anchor-count lists match independent local construction. Every traceback test frame's line and source statement match current test bytes.

Before/after hashes match all four local inputs in the hash table: lx_platform.py, lx_inventory.py, tests/test_lx_platform.py and tests/run_mutants.py. inputs_unchanged=true is thus independently verified. The artifact's status summary and subgroup kill counts are also correct: M32, R10, X9, N14, Y3, P5. Existing 64 assertion cases retain direct witnesses equivalent to the historical attribution table. M29 now fails at `assertIn("launched_by_systemd", g)`, directly detecting the intended omission as a strict assertion kill. The eight added semantic/regression cases are attributable as follows:

| ID | Direct property witness | Recorded observation |
|---|---|---|
| Y01 | `test_host_memtotal_caps_every_cgroup_limit` | effective_limit 3000 rather than required host cap 1000 |
| Y02 | `test_v2_root_and_memory_high` | cgroup_min_headroom 7980 rather than required minimum 2990 |
| Y03 | `test_samples_out_of_order_never_clean` | CLEAN rather than AMBIGUOUS for sample after end |
| P01 | reused-parent/exited-child/unobserved-parent tests | external child's row disappears despite no observed matching parent identity |
| P02 | `test_malformed_current_boot_never_proves_death` | DEAD rather than UNKNOWN for invalid current boot strings |
| P03 | `test_malformed_boot_readings_never_clean` | CLEAN rather than AMBIGUOUS for matching malformed boot IDs |
| P04 | `test_invalid_window_duration_is_no_reading` | empty positive reading rather than None for nan / inf window |
| P05 | `test_proc_view_rejects_malformed_nspid` | True for empty/garbage/zero/negative/decimal NSpid |

All 73 current kills are VALID ASSERTION KILLS after independent property review. M16 still has the direct stale-temp/symlink witnesses described above, independent of its crash-child exit assertion. No generic execution error is being counted as a current kill.

| Artifact file | SHA-256 |
|---|---|
| `validation.json` | `7fc04e79a9e20d0133bdd4956cc7eabcc7b9ab61d2cf495f8d583e7f8c0318da` |
| `input-commit.txt` | `98bd41b58f68ec1c8538bbe87be1061ad6344194c8ce89d9fee0b51c5f90c526` |
| `full-output.json` | `7fc04e79a9e20d0133bdd4956cc7eabcc7b9ab61d2cf495f8d583e7f8c0318da` |

Final repository check: HEAD remained the immutable reviewed commit and `git status --short` remained empty. No source change occurred during this subreview.

**Outstanding limitation:** the parent reported separate code-review concerns about intermediate clock/counter readings and malformed mount/duplicate-record cases. Those cases are not established by this 73-mutant registry. Their independent adjudication and any bounded repair/replay remain pending with the parent/code reviewer. The recorded run is verified; a complete fail-closed/code acceptance conclusion must incorporate those findings and must not be inferred solely from the passing baseline and 73 kills.
