# MB-S r1 (cell-308 successor): BUILD REPORT (builder; Phases 4–8; NOT frozen)

**Outcome of this build session: COMPLETE (not a blocker stop).** The namespace, its code, its tests, the mutant matrix, the protocol draft and the diffs are built and tested. **New cell-308 target evaluations: 0.** No MB r1 driver mode was run; no CUSUM m = 5 cell 305–309 was evaluated; no drift in [6/5, 13/5] or its mirror was computed; no ref was created, moved or deleted in the real repository; nothing was committed, staged or reset in any real worktree. Cell 309 was not touched. Nothing here authorizes a target evaluation: governance S1 (USER_RULING_REQUIRED at the grant) stands.

**Operational note (not a build blocker): this host would REFUSE `execute` tonight.** Read-only readings at build time: memory pressure level 2 (warn), thermal-pressure level 1, automatic macOS / critical-update installation ENABLED (with 26.6.x, 26.7.x and 27.0.x offered; the platform pin is 25F84 / 26.5.2), and a user app above the 25 % CPU exclusivity threshold. The preflight gates refuse on each; disabling automatic installation is the user's action (never changed by the driver).

## 1. What was built

| file | sha256 | role |
|---|---|---|
| `DRIVER_DIFF.md` | `ee965cd175e98781…` | full driver diff, every hunk classified |
| `GUARD_DIFF.md` | `6e6b2c4619df0dff…` | the one-line guard diff |
| `code/mbs308_driver.py` | `7bc2a6192b1877ae…` | the exactly-once driver: MB r1's text-identical science glue + the successor lifecycle / identity / modes |
| `code/mbs308_guard.py` | `48903487f648e9d3…` | MB r1's guard, one line changed (the marker ref) |
| `code/mbs308_host.py` | `21b82c3f96ce54dc…` | MB r1's host module + boot UUID, disk, memory pressure, low-power mode, update settings, process identity, caffeinate supervisor, launchd check, preflight gates |
| `code/mbs308_launch.py` | `a3310ed87c92dac5…` | the launchd launcher (transient LaunchAgent, detachment proof, bootout) |
| `code/mbs308_state.py` | `6a09062c29a57619…` | journal, spool persistence, checkpoints, classifier, lock, pidfile, awake-time cap, checkpointing pool + memory / broken-pool watchdog, test-only fault hook |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | `9a4490aeab744282…` | protocol draft (NOT frozen) |
| `tests/mbs308_child.py` | `dd95ef9302f366d3…` | child harness: one driver action in a sandbox with the synthetic evaluator and a fault point |
| `tests/mbs308_launch_harness.py` | `a5885f2a52ea69f7…` | the launching side of the launchd test |
| `tests/mbs308_payload.py` | `82061abb152963cb…` | the synthetic launchd payload |
| `tests/mbs308_synth.py` | `8e64193aadaf872a…` | the synthetic evaluator (fake job keys through MB r1's unchanged stage1; stub Stage 2) |
| `tests/mbs308_testlib.py` | `9fb5bce16ec0f421…` | sandboxes (from a separate no-local base store), grant chains, child harness, runner |
| `tests/test_mbs308_crash.py` | `7f85d71bfc095535…` | F1–F12 by os._exit and SIGKILL + simulations |
| `tests/test_mbs308_decoy.py` | `88503206a1391d8b…` | dev-decoy resume equivalence + MBR1_REPRO tiny form |
| `tests/test_mbs308_launch.py` | `8a3a697e4bd8de21…` | launchd integration + host unit tests |
| `tests/test_mbs308_mutants.py` | `36f0cefa2255ed19…` | the mutant runner |
| `tests/test_mbs308_state.py` | `00c9ef38fe70413d…` | every state and recover action; resume rules; checkpoint bindings; GC-8; persistence contract |
| `tests/test_mbs308_static.py` | `56373e82c761e6a7…` | RC1 / MBS-9 / MBS-12 / fault-hook / launcher static checks |

Helper pins (`HELPER_SHA256`) are re-pinned by a dev tool after every edit; the freeze re-pins. The science modules are NOT copied: `mbs308_driver.load_science_module` executes MB r1's committed bytes at MB r1's paths, each checked against its sha256 and git blob at 21e99cf0 and at HEAD (`SCIENCE_PINS`), registered under its own name.

## 2. How the design is implemented (architecture §1–§8)

* **§1 identity**: NSS, branch, worktree, refs `refs/p5y-k5-cell308-mbs-r1/{target-consumed,journal,ckpt,pending-result}`; MB r1 cited as history; MB r1's refs read only by the GC-8 assertion, never for arming, never written.
* **§2 state machine**: `mbs308_state.classify` (read-only; artifacts first, then the journal, the process identity, the boot UUID and — DR2 — the platform); `status` prints the state name only; `recover` dispatches exactly `ACTIONS[state]`. All eight states are reachable and tested.
* **§3 persistence**: `Store.spool_write_result` (O_EXCL|O_NOFOLLOW tmp, fsync + F_FULLFSYNC, rename, dir fsync + F_FULLFSYNC, read-back verify) → journal RESULT_DURABLE → `hash-object -w` with `core.fsync=loose-object,reference` + pending ref by CAS → private-index seal by CAS → materialize O_EXCL|O_NOFOLLOW. Fault points F4–F12 sit at these steps.
* **§4 checkpoints + resume**: MB r1's `stage1` is unchanged; `ProcessPoolExecutor` / `wait` are bound to `CheckpointingPool` / `checkpointing_wait`, which serve verified checkpoints as completed futures and write one checkpoint per completed job. `resume` arms the guard, verifies every checkpoint (job identity, grant, driver, platform, attempt + attempt seq, record hash), recomputes exactly the rest, and runs MB r1's aggregation, Stage 2, the decision and §3. Budget 3 resumes, deadline 7 days, two-consecutive-failures rule, no discretionary abandonment.
* **§5 launch**: `mbs308_launch.py` (transient LaunchAgent, `launchctl bootstrap gui/<uid>`, detachment proved by test); `execute` / `resume` refuse unless XPC_SERVICE_NAME equals the label, PPID is 1 and launchd names this pid; supervised caffeinate; stale pidfile never trusted; O_EXCL lock + CAS.
* **§6 host contract**: preflight gates (+ GC-10 headroom / exclusivity, RC2 platform, DR2 update settings) refuse before the marker; everything else is recorded only; a reboot (boot UUID change) is CONSUMED_INTERRUPTED.
* **§7 crash injection and mutants**: `tests/`; the fault hook is inert in production (the CLI refuses when it is set or any MBS308_TEST* variable is present; static check).
* **§8 what stays**: criterion, D5, controls, guard semantics, the 37 admitted pairs, caps, case families; EVAL_CAP per attempt on awake time (CLOCK_UPTIME_RAW watchdog).

## 3. Tests (final run, this code)

All state-changing tests run in `git clone --shared` sandboxes of a separate `git clone --no-local --bare` base store (never of the real object store), with the synthetic evaluator, driven in child processes so that fault points are real `os._exit` / SIGKILL. Durable reports: `~/Library/Logs/ReBaseGuard/mbs308-test/final/*.json`.

**`tests/test_mbs308_static.py`: 9/9 PASS** (5.2 s)

| test | result | s |
|---|---|---|
| `t_execute_and_resume_require_launcher_and_pins` | PASS | 0.0 |
| `t_fault_hook_test_only` | PASS | 4.8 |
| `t_launcher_plist_contract` | PASS | 0.0 |
| `t_mbs12_static_carryovers` | PASS | 0.0 |
| `t_mbs9_referenced_module_names` | PASS | 0.1 |
| `t_no_mbr1_driver_mode_invoked` | PASS | 0.0 |
| `t_rc1_guard_diff_only_marker` | PASS | 0.0 |
| `t_rc1_science_glue_text_identical` | PASS | 0.1 |
| `t_science_pins_equal_mbr1_bytes` | PASS | 0.0 |

**`tests/test_mbs308_state.py`: 34/34 PASS** (220.6 s)

| test | result | s |
|---|---|---|
| `t_budget_exhausted` | PASS | 1.9 |
| `t_budget_real_resumes` | PASS | 19.5 |
| `t_ckpt_future_seq` | PASS | 10.2 |
| `t_ckpt_job_swap` | PASS | 10.3 |
| `t_ckpt_never_read_after_terminal` | PASS | 5.9 |
| `t_ckpt_other_attempt` | PASS | 10.5 |
| `t_ckpt_tree_inconsistent` | PASS | 8.6 |
| `t_ckpt_wrong_driver` | PASS | 10.2 |
| `t_ckpt_wrong_grant` | PASS | 10.0 |
| `t_ckpt_wrong_platform` | PASS | 10.4 |
| `t_ckpt_wrong_record_hash` | PASS | 10.2 |
| `t_computing_then_interrupted` | PASS | 8.6 |
| `t_control_failed` | PASS | 2.9 |
| `t_deadline` | PASS | 1.9 |
| `t_enc_dec_lossless` | PASS | 0.0 |
| `t_execute_refuses_outside_launchd` | PASS | 2.2 |
| `t_gc8_mbr1_state` | PASS | 8.6 |
| `t_indeterminate_after_worker_death` | PASS | 5.7 |
| `t_journal_cas` | PASS | 0.4 |
| `t_marker_cas` | PASS | 2.8 |
| `t_no_abandonment` | PASS | 5.8 |
| `t_no_in_run_observation` | PASS | 10.2 |
| `t_no_target_consumed` | PASS | 10.7 |
| `t_pending_result` | PASS | 8.3 |
| `t_persistence_contract` | PASS | 0.4 |
| `t_platform_mismatch_at_resume` | PASS | 10.2 |
| `t_reboot` | PASS | 7.1 |
| `t_result_durable_unsealed` | PASS | 8.2 |
| `t_sealed_materialize` | PASS | 6.7 |
| `t_stale_pidfile` | PASS | 1.0 |
| `t_two_consecutive_failures` | PASS | 8.4 |
| `t_unrecorded_journal_invalid` | PASS | 0.6 |
| `t_unrecorded_no_journal_then_indeterminate` | PASS | 2.2 |
| `t_verify_result_units` | PASS | 0.0 |

**`tests/test_mbs308_crash.py`: 36/36 PASS** (416.7 s)

| test | result | s |
|---|---|---|
| `t_F10_exit` | PASS | 8.6 |
| `t_F10_kill` | PASS | 8.4 |
| `t_F11_exit` | PASS | 8.5 |
| `t_F11_kill` | PASS | 8.6 |
| `t_F12_exit` | PASS | 8.4 |
| `t_F12_kill` | PASS | 8.5 |
| `t_F1_exit` | PASS | 21.8 |
| `t_F1_kill` | PASS | 10.2 |
| `t_F2_exit` | PASS | 10.3 |
| `t_F2_kill` | PASS | 10.1 |
| `t_F3_exit` | PASS | 10.4 |
| `t_F3_kill` | PASS | 10.4 |
| `t_F4_exit` | PASS | 12.7 |
| `t_F4_kill` | PASS | 12.7 |
| `t_F5_exit` | PASS | 13.0 |
| `t_F5_kill` | PASS | 12.8 |
| `t_F6_exit` | PASS | 12.7 |
| `t_F6_kill` | PASS | 12.8 |
| `t_F7_exit` | PASS | 12.9 |
| `t_F7_kill` | PASS | 12.9 |
| `t_F8_exit` | PASS | 8.5 |
| `t_F8_kill` | PASS | 8.4 |
| `t_F9_exit` | PASS | 8.4 |
| `t_F9_kill` | PASS | 8.4 |
| `t_S01_worker_death` | PASS | 44.6 |
| `t_S02_reboot_after_crash` | PASS | 10.9 |
| `t_S03_stale_lock` | PASS | 11.3 |
| `t_S04_stale_pidfile` | PASS | 10.3 |
| `t_S05_corrupt_tmp` | PASS | 10.5 |
| `t_S06_truncated_result` | PASS | 13.1 |
| `t_S07_wrong_result_hash` | PASS | 14.2 |
| `t_S08_stale_pending_missing_blob` | PASS | 8.6 |
| `t_S09_stale_pending_wrong_blob` | PASS | 8.7 |
| `t_S10_concurrent_recover` | PASS | 12.1 |
| `t_S11_memory_watchdog` | PASS | 5.2 |
| `t_S12_eval_cap_awake_time` | PASS | 6.8 |

**`tests/test_mbs308_launch.py`: 6/6 PASS** (8.9 s)

| test | result | s |
|---|---|---|
| `t_launchd_integration` | PASS | 5.2 |
| `t_launcher_death_while_waiting` | PASS | 1.8 |
| `t_launcher_refuses_execute_when_preflight_fails` | PASS | 1.5 |
| `t_ppid1_is_not_detachment` | PASS | 0.0 |
| `t_preflight_gates_planted` | PASS | 0.0 |
| `t_supervisor_respawns_in_process` | PASS | 0.4 |

**`tests/test_mbs308_decoy.py`: 2/2 PASS** (284.4 s)

| test | result | s |
|---|---|---|
| `t_dev_decoy_resume_equivalence` | PASS | 284.4 |
| `t_mbr1_repro_tiny` | PASS | 0.0 |

Dev decoy (297, block 0, dev ladder, 2 workers): killed after ['C1B.0.4', 'C2B.0.20'], resumed: served ['C1B.0.4', 'C2B.0.20'], computed 2; Stage 1 (643 leaves) equal = True, Stage 2 (883 leaves over 5 decoy bundles) equal = True; per-kind peak RSS (bytes) {'C1B': 70336512, 'C2B': 87474176, 'RLR': 72253440, 'VER': 40271872}; baseline Stage-1 wall 121.0 s; host CLEAN. MBR1_REPRO tiny: RLR d4 equal = True (192 leaves), C2B N20 equal = True (43 leaves), geometry equal = True.

## 4. Mutant kill matrix

**33/33 mutants killed; unmutated code passes every target test: True.**

| id | file | what the mutant breaks | target test | killed |
|---|---|---|---|---|
| M01 | `mbs308_state.py` | skip the fsync of the tmp file | `state::t_persistence_contract` | KILLED |
| M02 | `mbs308_state.py` | skip the self-hash check | `state::t_verify_result_units` | KILLED |
| M03 | `mbs308_state.py` | accept a .tmp file as the result | `crash::t_F7_exit` | KILLED |
| M04 | `mbs308_state.py` | accept a checkpoint bound to a wrong grant | `state::t_ckpt_wrong_grant` | KILLED |
| M05 | `mbs308_state.py` | accept a checkpoint bound to a wrong driver sha | `state::t_ckpt_wrong_driver` | KILLED |
| M06 | `mbs308_state.py` | accept a checkpoint written under another platform pin | `state::t_ckpt_wrong_platform` | KILLED |
| M07 | `mbs308_state.py` | accept a checkpoint with a wrong / future journal seq | `state::t_ckpt_future_seq` | KILLED |
| M08 | `mbs308_state.py` | accept a checkpoint from another attempt | `state::t_ckpt_other_attempt` | KILLED |
| M09 | `mbs308_state.py` | serve the checkpoint of job A as job B | `state::t_ckpt_job_swap` | KILLED |
| M10 | `mbs308_state.py` | skip the checkpoint record hash | `state::t_ckpt_wrong_record_hash` | KILLED |
| M11 | `mbs308_state.py` | resume on a live process | `state::t_computing_then_interrupted` | KILLED |
| M12 | `mbs308_driver.py` | allow abandonment | `state::t_no_abandonment` | KILLED |
| M13 | `mbs308_launch.py` | treat PPID = 1 as detachment | `launch::t_ppid1_is_not_detachment` | KILLED |
| M14 | `mbs308_host.py` | no caffeinate re-spawn | `launch::t_supervisor_respawns_in_process` | KILLED |
| M15 | `mbs308_host.py` | ignore the boot UUID (a reboot is not an interruption) | `state::t_reboot` | KILLED |
| M16 | `mbs308_state.py` | journal update without compare-and-swap | `state::t_journal_cas` | KILLED |
| M17 | `mbs308_driver.py` | marker without compare-and-swap | `state::t_marker_cas` | KILLED |
| M18 | `mbs308_state.py` | a fourth resume | `state::t_budget_exhausted` | KILLED |
| M19 | `mbs308_state.py` | no 7-day deadline | `state::t_deadline` | KILLED |
| M20 | `mbs308_driver.py` | production accepts the test hook | `static::t_fault_hook_test_only` | KILLED |
| M21 | `mbs308_driver.py` | no two-consecutive-failures rule | `state::t_two_consecutive_failures` | KILLED |
| M22 | `mbs308_host.py` | trust a pidfile whose start time differs | `state::t_stale_pidfile` | KILLED |
| M23 | `mbs308_state.py` | skip the read-back verification | `state::t_persistence_contract` | KILLED |
| M24 | `mbs308_state.py` | accept a result bound to another grant | `state::t_verify_result_units` | KILLED |
| M25 | `mbs308_driver.py` | MB r1 state checked as a prefix wildcard (GC-8) | `state::t_gc8_mbr1_state` | KILLED |
| M26 | `mbs308_state.py` | skip the resume-time platform pin check (DR2) | `state::t_platform_mismatch_at_resume` | KILLED |
| M27 | `mbs308_state.py` | the memory watchdog never kills | `crash::t_S11_memory_watchdog` | KILLED |
| M28 | `mbs308_state.py` | read checkpoints after a terminal state (MBS-4) | `state::t_ckpt_never_read_after_terminal` | KILLED |
| M29 | `mbs308_state.py` | per-job progress in the journal (MBS-3) | `state::t_no_in_run_observation` | KILLED |
| M30 | `mbs308_driver.py` | resume does not set a rejected spool result aside | `crash::t_S06_truncated_result` | KILLED |
| M31 | `mbs308_driver.py` | execute without the launchd launcher | `state::t_execute_refuses_outside_launchd` | KILLED |
| M32 | `mbs308_driver.py` | a refused intent makes an unrecorded run look resumable | `state::t_marker_cas` | KILLED |
| M33 | `mbs308_state.py` | a broken pool is not released (the driver hangs until EVAL_CAP) | `crash::t_S01_worker_death` | KILLED |

Unmutated target tests:

* `crash::t_F7_exit`: PASS
* `crash::t_S01_worker_death`: PASS
* `crash::t_S06_truncated_result`: PASS
* `crash::t_S11_memory_watchdog`: PASS
* `launch::t_ppid1_is_not_detachment`: PASS
* `launch::t_supervisor_respawns_in_process`: PASS
* `state::t_budget_exhausted`: PASS
* `state::t_ckpt_future_seq`: PASS
* `state::t_ckpt_job_swap`: PASS
* `state::t_ckpt_never_read_after_terminal`: PASS
* `state::t_ckpt_other_attempt`: PASS
* `state::t_ckpt_wrong_driver`: PASS
* `state::t_ckpt_wrong_grant`: PASS
* `state::t_ckpt_wrong_platform`: PASS
* `state::t_ckpt_wrong_record_hash`: PASS
* `state::t_computing_then_interrupted`: PASS
* `state::t_deadline`: PASS
* `state::t_execute_refuses_outside_launchd`: PASS
* `state::t_gc8_mbr1_state`: PASS
* `state::t_journal_cas`: PASS
* `state::t_marker_cas`: PASS
* `state::t_no_abandonment`: PASS
* `state::t_no_in_run_observation`: PASS
* `state::t_persistence_contract`: PASS
* `state::t_platform_mismatch_at_resume`: PASS
* `state::t_reboot`: PASS
* `state::t_stale_pidfile`: PASS
* `state::t_two_consecutive_failures`: PASS
* `state::t_verify_result_units`: PASS
* `static::t_fault_hook_test_only`: PASS

Each mutant replaces one exact fragment (occurring once), must still parse, and the driver's helper pins are re-pinned to the mutated bytes, so a kill is always the gate's own test failing, never a pin check.

## 5. Review conditions RC1/RC2/RC6/GC-6/GC-8/GC-10 (and DR2, MBS-2/3/4/9/12)

* **RC1 (science boundary).** Every science-glue function carried from MB r1's driver is text-identical to MB r1's at
  `c46434a3` (whose bytes equal `21e99cf0`): 34 functions / classes compared by AST source segment
  (`t_rc1_science_glue_text_identical`). **MBS-9 (i)**: `t_mbs9_referenced_module_names` closes over every module-level
  name those functions reference (61 names across 36 functions): all defs, imports and assignments are text-identical
  except a listed, reasoned set: `GUARD`, `HOST`, `PIN`, `S1M`, `SUP`, `CON` (executed from MB r1's pinned bytes, or the
  one-line guard), `ProcessPoolExecutor` / `wait` (the checkpointing lifecycle), `HELPER_SHA256`, `LINEAGE`. The guard
  differs only in the marker constant (`t_rc1_guard_diff_only_marker`; GUARD_DIFF.md). The unchanged science is listed by
  path + sha256 + git blob in the protocol draft section 2 (45 files). The Stage-1 refactor the brief allowed was NOT
  needed: stage1's text is unchanged; resume enters through the pool / wait names, and is proven byte-equivalent on the
  synthetic evaluator and on the dev decoy.
* **RC2 (platform).** `PLATFORM_PINS` (interpreter realpath + sha256, libpython + sha256, `python_version`,
  `sys.version`, OS build 25F84, arch arm64) are re-verified by `check_platform` in preflight, `execute`, every `resume`
  (`pre_marker_common`) and the computing modes decoy / rehearse (DR2 a). MBR1_REPRO is designed (protocol section 11) and
  was run only in its tiny form (block 0 of 297, dev ladder) by comparing the successor's job records with MB r1's
  COMMITTED r3 QC02 records. MB r1's driver was never run (the brief's absolute rule), so the coordinator's "dev-ladder
  equivalent produced with MB r1's code" was replaced by the committed full-ladder records, which contain the RLR d4 and
  C2B N20 jobs of block 0.
* **RC6.** Checkpoints + mandatory resume are kept; the reason is stated in advance in protocol section 6; Q12 must be
  re-measured under the launchd launcher at qualification (noted, not run).
* **GC-6 / MBS-2 (exposure).** Section 9 states plainly what I opened.
* **GC-8.** `check_mbr1_state` (preflight, execute, resume): exactly one ref under `refs/p5y-k5-cell308-mb-r1/`, the
  marker -> `afa930727d084a5b70e6b85d30ca8f34c0e8ae74`; no MB r1 pending ref; no `mb308-cell308-emergency-result.json` in
  MB r1's git dir, this git dir or the common dir; no `NSF/evidence` in the worktree, at HEAD or on MB r1's branch. A named
  exception, never a prefix wildcard (mutant M25). `t_gc8_mbr1_state` plants an extra MB r1 ref, an MB r1 pending ref, a
  moved marker, an emergency file and an evidence path: each refuses `MBR1_STATE`; the unplanted state runs.
* **GC-10.** Per-job peak RSS is recorded (the worker's `ru_maxrss`, via a wrapper around the unchanged job function; dev
  decoy: RLR d4 ~72 MB, C1B d4 ~70 MB, C2B N20 ~88 MB, VER d4 ~40 MB). A per-worker RSS watchdog SIGKILLs a worker above
  the cap and records it; the pool breaks and the attempt is sealed TARGET_EVALUATION_FAILED (INDETERMINATE), never a
  silent drop (S11, mutant M27). The cap is provisional (3 GiB); the rule to freeze is max(3 x the largest official decoy
  per-job peak RSS, 1 GiB), from official decoy runs only. Preflight headroom: memory pressure normal and free memory
  >= 2 GiB; exclusivity: no process above 25 % CPU besides this process tree and a documented OS / UI allow-list
  (`EXCL_ALLOW` in the driver). Both are recorded and refuse start.
* **DR2.** (a) the full platform pin at execute, every resume and every computing mode; (b) a platform mismatch at resume
  classifies CONSUMED_UNRECORDED (`PLATFORM_PIN_MISMATCH`) -> `close-indeterminate`, never a mixed-platform resume
  (`t_platform_mismatch_at_resume`, planted OS build `25Z999`; mutant M26); checkpoints also carry the platform digest
  (mutant M06); (c) preflight reads, read-only, `com.apple.SoftwareUpdate` AutomaticallyInstallMacOSUpdates /
  AutomaticDownload / CriticalUpdateInstall / ConfigDataInstall (a missing key = enabled) and refuses `execute` when
  AutomaticallyInstallMacOSUpdates or CriticalUpdateInstall is enabled (the two that can change the OS build); the other
  two are recorded. Tonight all four are 1.
* **MBS-3.** `execute` / `resume` print nothing per job (only the final SEALED / UNSEALED / RECOVER lines);
  `host-events.jsonl` carries caffeinate events only; the journal is advanced only at state transitions, never per job
  (after a crash + resume it holds <= 8 entries whatever the number of jobs): `t_no_in_run_observation`, mutant M29. All
  git-writing tests use the no-local base store.
* **MBS-4.** `Checkpointer.verified_records` refuses once the journal is SEALED / INDETERMINATE_SEALED / CLOSING or a
  record is sealed on the branch; checkpoints are never deleted and are recorded by count and tree hash only
  (`t_ckpt_never_read_after_terminal`, mutant M28).
* **MBS-9.** (i) above; (ii) resumed == uninterrupted: synthetic (every F-case compares the sealed target bytes, and the
  synthetic Stage 2 is an order-sensitive digest of every record) and the dev decoy (every certified leaf); the full-cell
  case QS-RESUME-DECOY is designed (protocol section 11); (iii) mutants M04-M10 (wrong grant, wrong driver, wrong platform,
  future seq, another attempt, job A served as B, record hash) are all killed; (iv) platform + research pins at execute
  and every resume (`pre_marker_common` -> `check_bindings`, `check_science_modules`, `check_platform`).
* **MBS-12.** No successor file names C3_KNOCKOUT_RECONSTRUCTION (asserted); DECOY_CELLS = (297, 316) (asserted);
  `decide` (MB r1 section 5.4) is text-identical; C-A and `rehearse` are carried verbatim (rehearse was not run by the
  builder: it computes on cell 305); the future QC12 scanner must build its planted strings at run time (protocol
  section 11); no scanner was written in this build.

## 6. Object-store side effects (coordinator note N3)

* **Freshened in the real object store: exactly one object**, blob `a1995184cdbcf51f5e1885873958a5168fbd5f69` (MB r1's
  pre-marker probe blob, 31 bytes; birth 2026-09-29 20:58:00 JST). My early sandboxes were `--shared` clones of the real
  repository, and the successor's seal-precondition probe then used MB r1's probe bytes; `git hash-object -w` found the
  object through the alternates and bumped its **mtime** (last to 04:12:46 JST). Nothing else: a scan of every loose
  object with mtime >= 03:30 JST and birth < 03:30 JST finds only this blob, and no pack file mtime changed (all packs
  predate the session); the final re-scan is below. **No object was created in the real store by any sandbox**
  (sandbox writes go to the sandbox's own store), no ref was created, and the successor worktree's index was never
  rewritten (mtime 03:21, before the session). Sandboxes that used the real store through alternates:
  `builderMBS/sbx_smoke`, `sbx_smoke2`, `t_state` (its first run only), `decoy/sbx` (the first three dev-decoy runs).
* **Changes.** (1) The probe is now `b"mbs308 object-store write probe " + 32-hex nonce + b"\n"` (the trial commit
  message carries a nonce too): it can never equal an existing object. (2) Since 04:20 JST every sandbox is a `--shared`
  clone of a separate `git clone --no-local --bare` base store (`builderMBS/base_store.git`, 466 MB, no alternates; the
  sandbox constructor asserts that its only alternate is the base store), so no sandbox can reach the real store.
  (3) Sandboxes still `git add` namespace files; the objects go to the sandbox's own store, and an existing object can be
  freshened only in the base store. (4) Successor audit / postexec tooling must window objects by `st_birthtime`, never by
  mtime (none exists yet in this namespace).

## 7. Findings (defects found while building; fixed in MB-S; MB r1 untouched)

1. **MB r1's `serialize` self-hash is not re-verifiable from the bytes** when a record holds an int-keyed dict (json
   sorts int keys numerically before and lexically after a round trip). MB r1 never re-verified it; MB-S verifies it on
   read-back and in the classifier, so it serializes after one JSON round trip.
2. **A worker death could hang MB r1's driver until EVAL_CAP.** The driver sets SIG_IGN for SIGTERM before the marker
   and MB r1's `_worker_init` ignores it too; the spawned workers inherit it, so concurrent.futures' `terminate_broken`
   (SIGTERM, then `join` while holding the executor's shutdown lock) waits forever for a live worker, and the main thread
   blocks in `submit` or `shutdown`. Reproduced intermittently (1 in 14 synthetic runs). MB-S releases a broken pool by
   SIGKILL from the pool watch thread and SIGKILLs an abandoned pool's workers at `shutdown(wait=False)` (stage1's own
   `p.terminate()` cannot stop them); S01 now runs 7 worker deaths in about 6 s each; mutant M33.
3. **Exit-time hang after an EVAL_CAP hit**: interpreter exit joins concurrent.futures' manager thread, which can wait
   forever for a pool abandoned by the alarm exception (observed: 300 s until the harness killed it, after the record was
   sealed). MB-S's CLI hard-exits (`os._exit`) once `main()` has returned (everything durable is fsync'd by then).
4. **Orphaned workers could block forever**: a worker that starts after its driver was killed already sees PPID 1 and
   blocks on the call queue (it holds both pipe ends). The parent-death watch now takes the driver's pid explicitly.
5. **`XPC_SERVICE_NAME` is `0` in the hosting app's environment**: the design's "XPC_SERVICE_NAME / the label is
   present" would pass trivially; MB-S requires equality with the launcher's label, PPID 1 and launchd naming this pid.
6. **The design's F2 window** (marker written, journal not yet) would classify CONSUMED_UNRECORDED and lose the
   evaluation; MB-S writes a durable journal intent (ARMING) before the marker (deviation D1).
7. **A refused execute could make an unrecorded run look resumable** (intent written, marker CAS failed): the intent is
   now closed as ABORTED_INTENT, which classifies CONSUMED_UNRECORDED (mutant M32).
8. **Lossy checkpoint round trip**: a sorted canonical JSON loses dict insertion order; the order-sensitive synthetic
   Stage 2 exposed it. Checkpoints now encode every dict as ordered pairs.
9. **Stale-lock break race** (two recovers breaking one stale lock): now a clean refusal (LOCKED / LOCK_RACE), a moved
   fresh lock is restored by `link`, and the journal CAS remains the second line of defence.

## 8. Deviations from the architecture (each with its reason)

| # | design | as built | reason |
|---|---|---|---|
| D1 | journal written after the marker | durable ARMING intent (CAS) before the marker; ARMING + marker classifies like COMPUTING; a stale no-marker intent is taken over by the next `execute`; a failed marker CAS closes the intent ABORTED_INTENT | the F2 window (finding 6); exactly-once is unchanged (the marker CAS decides) |
| D2 | journal records "the ids of the checkpoint tree" | recorded at each attempt start (resume), not per checkpoint | MBS-3 (no per-job progress in durable logs); the ckpt ref is the per-job record |
| D3 | checkpoint carries "the journal sequence number" | the seq of the journal entry that STARTED the attempt, plus the attempt number and the platform digest | MBS-9 iii (another attempt, future seq, platform) |
| D4 | "a journal whose checkpoints fail verification" -> UNRECORDED | the tree recorded at the last attempt start must be contained in the ckpt ref (else UNRECORDED); a single failing checkpoint is recomputed (rule a); the same job failing twice in a row -> UNRECORDED | reconciles section 2 with section 4 (a) |
| D5 | worker death listed among the simulations | a worker death stays MB r1's execution failure (sealed TARGET_EVALUATION_FAILED -> INDETERMINATE), not a resumable interruption | MB r1 section 4; a CPU-cap kill must stay a failure. **Reviewers may prefer resumable jetsam kills: flagged** |
| D6 | pending ref by CAS from zero | from zero, or from a classified STALE value (missing or failing blob) | a stale pending ref would otherwise block the seal forever |
| D7 | (unspecified) | rejected spool files (`result.json`, `.tmp`) are renamed aside (never read) before a new write | the O_EXCL write needs the name free |
| D8 | materialize O_EXCL | also accepts an existing plain `execution` directory | re-materialization in SEALED |
| D9 | `serialize` (sorted keys, self sha256) | one JSON round trip first | finding 1 |
| D10 | EVAL_CAP "never across a sleep classified by K/S/L" | a watchdog on CLOCK_UPTIME_RAW (the K channel's non-sleeping clock) raises MB r1's SIGALRM | awake time per attempt, without after-the-fact sleep subtraction |
| D11 | launcher check "XPC_SERVICE_NAME / the label is present" | equality with the label + PPID 1 + launchctl pid | finding 5 |
| D12 | (unspecified) | the grant must carry the S1 ruling verbatim (`user_ruling_s1`: verbatim, sha256, reaffirms_c4) | governance S1 made mechanical |
| D13 | (unspecified) | the classifier takes the current platform readings; the journal records the marker attempt's platform | DR2 |
| D14 | (unspecified) | `RESUME_CONTROL_FAILED` (controls re-run at resume; a failure is a post-marker failure) | resume must rebuild the Stage-2 bundle, which the controls produce |
| D15 | (DR2 c) | the update gate uses AutomaticallyInstallMacOSUpdates and CriticalUpdateInstall only | the two that can change the OS build; the others recorded (review may widen) |
| D16 | (unspecified) | hard exit after `main()`; broken-pool release; shutdown SIGKILL; explicit parent pid in workers | findings 2-4 |
| D17 | (N3) | nonce-carrying seal-precondition probe | no collision with MB r1's probe or any existing object |

Points where I think the design is wrong or under-specified: D1 (the F2 window), D4 (section 2 vs section 4 (a)), D5
(worker death), D11 (a presence check), and the design's silence on the pool's SIGTERM behaviour (finding 2), which MB r1
shares.

## 9. Exposure disclosure (GC-6 / MBS-2), stated plainly

Before the GC-6 instruction arrived I had opened:
* **`NSF/postexec/MB308_RECOVERY_RECORD.md`, read in full** (76 lines). It holds the MB r1 target run's chronology (launch
  20:57:58 JST, marker 20:58:01, the 23:29:00 Force Quit, "Stage-1 pool load continued 23:29:00-23:40:48", last log
  entries 23:40:35 / 23:41:09, forced reset / boot 00:00:15), the host readings at launch (thermal level 0 on three reads,
  AC, lid open, lowpowermode 0), the two caffeinate PIDs, and the probe blob / trial commit ids. I also listed the file
  names of `NSF/postexec/` with line counts (`wc -l`), without reading the other files.
* `research/reviews/REVIEW_SUCCESSOR_GOVERNANCE_308.md` and `REVIEW_SUCCESSOR_ROUTE_308.md` **as they then stood** (22
  and 15 lines: headers and in-progress work logs; no run observations in them at that time). I did not open them again,
  nor any delta.
* The last three lines of the research ledger (one describes reviewEXEC's checks and names "powerlog per-coalition CPU
  aggregates", no values); the file-name listings of `research/reviews/` and `research/audit/`; the governance
  determination section 4.3 and the architecture (which say that runtime observations exist and mention the Force Quit).
* I did **not** open `research/reviews/REVIEW_EXECUTION_INTERRUPTION*.md`, `research/audit/EXECUTION_INTERRUPTION_*.md`,
  `NSF/review/MB308_EXECUTION_REVIEW.md`, `research/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`, or any adjudication /
  adjudication-review file.
* **Nothing of it entered a successor cap, limit, timing or threshold**: the CPU caps and EVAL_CAP are MB r1's frozen
  values; the memory cap, headroom and exclusivity thresholds come from tonight's dev decoy and host readings only; the
  crash tests use synthetic timings.

## 10. Known gaps

1. No qualification verifier, manifest writer or leak scanner was built (next phase); the protocol draft lists the cases.
2. Provisional values to freeze from the qualification host / official decoys: `PLATFORM_PINS`, `MEM_CAP_BYTES`,
   `FREE_MEM_MIN_BYTES`, `EXCL_CPU_PCT`, `EXCL_ALLOW`. Peak RSS for the frozen-ladder kinds (RLR d6/d8, C2B N40/N80,
   C1B d8-12) is unmeasured.
3. The real driver was never launched by launchd (by rule); the launcher and the driver's launchd check are proven with
   the synthetic payload (the check passes inside the launchd job) and in sandboxes (it refuses outside).
4. The full-cell QS-RESUME-DECOY and the full MBR1_REPRO were not run (dev / tiny forms only); `rehearse --cell 305` was
   not run; the controls' re-run at resume is exercised with stubs only.
5. The stale-lock break keeps a narrow residual race (a clean LOCK_RACE refusal; the journal CAS protects).
6. A SIGKILLed driver leaves a multiprocessing resource-tracker warning about leaked semaphores (cosmetic).
7. The resume's journal entry records checkpoint failure counts by job name (a transition record, not progress);
   reviewers may want the names hashed.
8. The exclusivity allow-list is heuristic; the hosting app is not on it.


## 11. Research-ledger lines (agent `builder2`, via `c308_quarantine.log_event`; target_evaluations 0 on every line)

| utc | class | script | purpose (abridged) |
|---|---|---|---|
| 2026-09-29T19:07:22Z | NONTARGET_DRIFT_VALIDATION | mbs308_driver.py decoy (sandbox clone --shared) | MB-S r1 build: dev decoy baseline: decoy --cell 297 --first-blocks 1 --dev-ladder --workers 2 (production decoy mode of the successor driver; MB r1 sc |
| 2026-09-29T19:07:46Z | SYNTHETIC_VALIDATION | scratch smoke.py / smoke2.py (sandbox clone --shared) | MB-S r1 build: synthetic-evaluator smoke runs of execute / recover / resume / seal-only / close-indeterminate with fault points F1-F5, F7, F9, F11, F1 |
| 2026-09-29T19:11:23Z | NONTARGET_DRIFT_VALIDATION | mbs308_child.py decoy-ckpt (sandbox) | MB-S r1 build: dev decoy 297 block 0 dev ladder, 2 workers, through the checkpoint path, SIGKILLed after 2 checkpoints (fault F3; test hook in a sandb |
| 2026-09-29T19:11:23Z | NONTARGET_DRIFT_VALIDATION | mbs308_child.py decoy-ckpt --resume (sandbox) | MB-S r1 build: resumed dev decoy 297 block 0 from 2 verified checkpoints (2 served, 2 computed); Stage 1 (643 leaves) and 5 Stage-2 decoy bundles (883 |
| 2026-09-29T20:25:03Z | SYNTHETIC_VALIDATION | tests/test_mbs308_state.py (runs r1-r3 + single-test reruns) | MB-S r1 build: state-machine tests (every state, every recover action, resume budget / deadline / checkpoint rules, GC-8, persistence contract) with t |
| 2026-09-29T20:25:03Z | SYNTHETIC_VALIDATION | tests/test_mbs308_crash.py (runs r1, r2 + single-test reruns) | MB-S r1 build: fault points F1-F12 by os._exit and SIGKILL + simulations (worker death, reboot, stale lock / pidfile, corrupt tmp, truncated / wrong-h |
| 2026-09-29T20:25:03Z | SYNTHETIC_VALIDATION | tests/test_mbs308_launch.py (run r1) | MB-S r1 build: launchd integration with a SYNTHETIC payload (labels org.rebaseguard.mbs308.test.20260929T193913 and a launcher-death label; plists in  |
| 2026-09-29T20:25:03Z | SYNTHETIC_VALIDATION | scratch debug scripts dbg1 / dbg_wd / dbg_cap / repro/ppe_hang.py | MB-S r1 build: debugging of the resume and worker-death paths with the synthetic evaluator (faulthandler stack dumps) and a plain ProcessPoolExecutor  |
| 2026-09-29T20:25:03Z | SYNTHETIC_VALIDATION | tests/test_mbs308_static.py + tests/test_mbs308_mutants.py (trial subs | MB-S r1 build: static RC1 / MBS-9 / MBS-12 checks and trial mutant runs (M02, M13, M14, M20, M24) |
| 2026-09-29T20:25:03Z | NONTARGET_DRIFT_VALIDATION | tests/test_mbs308_decoy.py (run r2: 3 dev-decoy runs) | MB-S r1 build: dev decoy 297 block 0 dev ladder 2 workers: uninterrupted baseline, SIGKILL after 2 checkpoints, resumed from 2 verified checkpoints; S |
| 2026-09-29T21:01:44Z | SYNTHETIC_VALIDATION | final run: tests/test_mbs308_static.py, _launch.py, _state.py, _crash. | MB-S r1 build, final code: static 9/9, launch 6/6 (real launchd job with a synthetic payload, booted out), state 34/34, crash 36/36 (F1-F12 x os._exit |
| 2026-09-29T21:01:44Z | SYNTHETIC_VALIDATION | final run: tests/test_mbs308_mutants.py | MB-S r1 build, final code: 33 planted mutants, 33 killed; the unmutated code passes all 30 target tests |
| 2026-09-29T21:01:44Z | NONTARGET_DRIFT_VALIDATION | final run: tests/test_mbs308_decoy.py (3 dev-decoy runs) | MB-S r1 build, final code: dev decoy 297 block 0 dev ladder 2 workers: uninterrupted, SIGKILLed after 2 checkpoints, resumed; every certified leaf of  |

13 lines; LEAK_FLAG on none: True.


## 12. Repairs R1/R2/R4 (implementation review REVIEW_IMPLEMENTATION_MBS308, IMPLEMENTATION_REJECTED, commit 6d3a44cd, sha256 abecfbb2…; T6 ruling M4: repairs at a non-holder reviewer's request only)

Read for this repair: the review's sections "Defects" and "CONDITIONS" only (plus the code and tests I wrote). R3 (DEF-3) is not a builder repair (it needs a non-holder's re-derivation / ratification) and was not touched. **No operational number was changed or added**: no cap, limit, timeout, threshold, allow-list or budget value. One point for the reviewer: the R1 (i) retry of a failed ref write reuses MB r1's frozen `SEAL_RETRY_DELAYS` schedule (0.5, 1, 2, 4 s; previously used only for the branch update in the seal) — a reuse of an existing frozen value in a new place, not a new number; ratify or rule otherwise. R2 removed the launcher's `timeout_s` early boot-out (its only use was `cleanup`'s `timeout_s=0`). Working tree only; nothing committed; base afba20e5.

### Diff summary (against afba20e5)

```
.../p5y_k5_cell308_mbs_r1/DRIVER_DIFF.md           | 204 +++++++++++++--------
 .../p5y_k5_cell308_mbs_r1/code/mbs308_driver.py    | 115 +++++++++---
 .../p5y_k5_cell308_mbs_r1/code/mbs308_host.py      |  30 +++
 .../p5y_k5_cell308_mbs_r1/code/mbs308_launch.py    |  67 ++++---
 .../p5y_k5_cell308_mbs_r1/code/mbs308_state.py     | 178 +++++++++++++++++-
 .../protocol/MBS308_PROTOCOL_DRAFT.md              |  26 +++
 .../p5y_k5_cell308_mbs_r1/tests/mbs308_child.py    |  17 ++
 .../p5y_k5_cell308_mbs_r1/tests/mbs308_testlib.py  |  32 +++-
 .../tests/test_mbs308_crash.py                     | 202 +++++++++++++++++++-
 .../tests/test_mbs308_launch.py                    |  89 +++++++++
 .../tests/test_mbs308_mutants.py                   |  41 ++++-
 .../tests/test_mbs308_state.py                     | 204 +++++++++++++++++++++
 12 files changed, 1069 insertions(+), 136 deletions(-)
```

* **R1 (i) — `mbs308_state.Store.cas_ref`.** After a failed `update-ref` the ref is re-read (`read_ref`: readable / absent / unreadable). Only "the ref no longer holds the expected old value" returns False (a conflict). Anything else (stale lockfile, I/O error, unreadable ref) is appended to `REF_WRITE_FAILURES` (value-free: ref, try, rc, lock present) and retried on the store's `retry_delays` (the driver passes `SEAL_RETRY_DELAYS`), then raises `RefWriteError` (an OSError; never a conflict). Callers: checkpoint write → recorded, evaluation continues; journal intent → `JOURNAL_WRITE_FAILED` (nothing consumed); marker → `MARKER_WRITE_FAILED` (the marker provably absent; intent closed ABORTED_INTENT); resume's attempt advance → `JOURNAL_WRITE_FAILED` (attempt not consumed); close → `JOURNAL_WRITE_FAILED`; pending / branch → UNSEALED (exit 4; the durable spool / pending decide). `check_not_evaluated` now also takes over an ABORTED_INTENT journal (no marker, process dead): this removes the DEF-1 (d) pre-marker wedge.
* **R1 (ii) — `mbs308_driver._journal(durable=...)`.** Every journal advance made once the durable artifacts exist (after the spool write, the pending ref or the seal; in `persist_and_seal` and every `seal-only` path) is `durable=True`: a failed advance — a genuine conflict included — is recorded in `JOURNAL_FAILURES` and never stops the seal. Before the artifacts exist a genuine conflict still means LostOwnership.
* **R1 (iii) — stale campaign git lockfiles.** `git_lockfiles` (refs/p5y-k5-cell308-mbs-r1/*.lock, the branch lock, packed-refs.lock in the common dir); `git_lock_info` (read-only, in every classification): stale only when no live campaign process exists (O_EXCL recover-lock holder, pidfile, journal process) and `lsof` shows no process holding any of them open (a live git command elsewhere in the shared repository); `move_stale_git_locks`: `recover`'s frozen action, before resume / seal / close and in every state except CONSUMED_COMPUTING — under the O_EXCL lock, re-verify, move each lockfile into `<spool>/git-locks-aside/` (never deleted; never renamed inside refs/, where it would read as a ref), fsync, and append a value-free record to `<spool>/recover-actions.jsonl` (also copied into the sealed record's lifecycle). Held lockfiles: recover does nothing (exit 8). `execute` / `resume` / `seal-only` / `close-indeterminate` refuse `GIT_LOCKED` while any campaign lockfile exists.
* **R1 (iv) — fault points / planted locks.** The test-only fault hook gained two in-place actions (`plant`: a lockfile appears at that fault point; `bump_journal`: another writer advances the journal there); the production CLI still refuses when any hook is set. Crash tests L01–L11 plant locks for the marker, journal, ckpt, pending and branch refs and packed-refs, before a run and mid-run, and assert the frozen final state (SEALED with the uninterrupted bytes, no second marker, no verified checkpoint recomputed).
* **R2 — `mbs308_launch.py`.** `launch()` never boots out after `launchctl bootstrap` (any failure after the bootstrap propagates; the record carries `observed`, the job identity and the detachment proof when launchd reported the job; the driver's own launchd check refuses a job not properly launched). `wait_and_cleanup` and `cleanup <label>` boot out only when `mbs308_host.identity_state(recorded identity)` is `DEAD` (positive evidence: the pid is gone, belongs to another process, or the boot UUID changed); `UNKNOWN` (a failed `ps` or boot-UUID read) is never dead; a failing, timed-out or unparseable `launchctl print` decides nothing; no recorded identity → never booted out automatically.
* **R4 — behavioural tests on planted readings.** `host_preflight(launched, texts=...)` accepts planted vm_stat / ps / host / update readings (production passes none); the child harness can plant a pin value (`pin_override`), change a pinned file after the driver loaded it (`tamper_after_import`), or skip the clean-tree check to isolate a later refusal (`skip_clean`).

### New tests (all PASS in the repair run)

| module | test | result |
|---|---|---|
| crash | `t_L01_marker_lock` | PASS |
| crash | `t_L02_journal_lock_after_crash` | PASS |
| crash | `t_L03_journal_lock_during_seal` | PASS |
| crash | `t_L04_journal_conflict_during_seal` | PASS |
| crash | `t_L05_ckpt_lock_midrun` | PASS |
| crash | `t_L06_ckpt_lock_after_crash` | PASS |
| crash | `t_L07_pending_lock` | PASS |
| crash | `t_L08_branch_lock` | PASS |
| crash | `t_L09_packed_refs_lock_stale` | PASS |
| crash | `t_L10_lock_with_live_campaign_process` | PASS |
| crash | `t_L11_packed_refs_lock_open` | PASS |
| launch | `t_wait_cleanup_ignores_failing_print` | PASS |
| launch | `t_launch_never_boots_out_after_bootstrap` | PASS |
| state | `t_gc10_start_gates` | PASS |
| state | `t_pins_execute_platform` | PASS |
| state | `t_pins_resume_platform` | PASS |
| state | `t_pins_execute_research` | PASS |
| state | `t_pins_resume_research` | PASS |
| state | `t_pins_execute_science` | PASS |
| state | `t_pins_resume_science` | PASS |
| state | `t_pins_science_fresh_process` | PASS |
| state | `t_gc8_evidence_at_head_and_mbr1_branch` | PASS |
| state | `t_cas_ref_conflict_vs_infrastructure` | PASS |

### New mutants

| id | file | what the mutant breaks | target test | result |
|---|---|---|---|---|
| M34 | `mbs308_state.py` | R1 (i) undone: every ref-write failure read as a CAS conflict | `crash::t_L05_ckpt_lock_midrun` | KILLED |
| M35 | `mbs308_driver.py` | R1 (ii) undone: a journal conflict after the durable result stops the seal | `crash::t_L04_journal_conflict_during_seal` | KILLED |
| M36 | `mbs308_driver.py` | R1 (iii) undone: recover never moves stale git lockfiles aside | `crash::t_L02_journal_lock_after_crash` | KILLED |
| M37 | `mbs308_state.py` | R1 (iii) guard undone: a lock is 'stale' although a live campaign process holds the pidfile | `crash::t_L10_lock_with_live_campaign_process` | KILLED |
| M38 | `mbs308_state.py` | R1 (iii) guard undone: a lockfile held open by a live process is moved aside | `crash::t_L11_packed_refs_lock_open` | KILLED |
| M39 | `mbs308_driver.py` | R1 (d wedge) undone: an aborted intent (marker write failed) blocks every later execute | `crash::t_L01_marker_lock` | KILLED |
| M40 | `mbs308_launch.py` | R2 undone: the launcher boots out on one negative `launchctl print` | `launch::t_wait_cleanup_ignores_failing_print` | KILLED |
| M41 | `mbs308_launch.py` | R2 undone: launch() boots out after the bootstrap | `launch::t_launch_never_boots_out_after_bootstrap` | KILLED |
| M42 | `mbs308_driver.py` | GC-10 free-memory start gate ignored (R4) | `state::t_gc10_start_gates` | KILLED |
| M43 | `mbs308_driver.py` | GC-10 exclusivity start gate ignored (R4) | `state::t_gc10_start_gates` | KILLED |
| M44 | `mbs308_driver.py` | platform pin never compared (execute / resume) (R4) | `state::t_pins_resume_platform` | KILLED |
| M45 | `mbs308_driver.py` | research pins not re-verified at execute / resume (R4) | `state::t_pins_resume_research` | KILLED |
| M46 | `mbs308_driver.py` | science pins not re-verified at execute / resume (R4) | `state::t_pins_resume_science` | KILLED |
| M47 | `mbs308_driver.py` | GC-8 evidence path at HEAD / on MB r1's branch ignored (R4) | `state::t_gc8_evidence_at_head_and_mbr1_branch` | KILLED |
| M17 | `mbs308_driver.py` | marker without compare-and-swap | `state::t_marker_cas` | KILLED |

M17 (marker without compare-and-swap) was re-targeted to the restructured marker write; its meaning is unchanged. Every other mutant M01–M33 is unchanged.

### Repair run (full suite + full matrix; reports in ~/Library/Logs/ReBaseGuard/mbs308-test/repair/)

* `test_mbs308_static.py`: **9/9 PASS**
* `test_mbs308_launch.py`: **8/8 PASS**
* `test_mbs308_state.py`: **44/44 PASS**
* `test_mbs308_crash.py`: **47/47 PASS**
* `test_mbs308_decoy.py`: **2/2 PASS**
* Mutant matrix: **46/47 killed**; unmutated code passes every target test: True; survivors ['M33'].

**The one survivor, M33, is PRE-EXISTING (not a repair mutant), and its earlier kill was luck.** M33 removes the broken-pool release from the pool watch thread. When a worker dies, concurrent.futures' `terminate_broken` holds the executor's shutdown lock while it `join`s the other workers. They ignore SIGTERM, so the join waits until each busy sibling finishes its current job; meanwhile the driver's `submit` / `shutdown` blocks. With short synthetic jobs the join ends at once, so `t_S01_worker_death` kills M33 only when a sibling happens to be mid-job: the previous matrix did (232 s), this run did not. A scratch probe (existing knobs only; no repository file changed; spec worker_die=RLR.0.6, job_sleep=90) confirms the defect and the release: unmutated, the failure is sealed in 9.7 s; with M33, 97.5 s (in production the sibling job can run for hours, until EVAL_CAP). **Proposed deterministic test (NOT applied: T6 M4 allows repairs only at a non-holder's request):** add to `t_S01_worker_death` one run with `{"worker_die": "RLR.0.6", "job_sleep": 90}` under the existing 60 s bound. For the reviewer to rule on.

The repair run used only sandboxes cloned from the separate no-local base store, the synthetic evaluator, the synthetic launchd payload and the dev decoy (297, block 0, dev ladder, 2 workers); 0 target evaluations; no ref, commit or staging in the real repository.


## 13. Repairs R3 + C-1, and the bounded hardening N-2 / N-3 (implementation delta review REVIEW_IMPLEMENTATION_MBS308_DELTA, DELTA_REJECTED, research 99185dcb; editor `editorR3C1`)

**Scope.** Only the delta review's remaining conditions: R3 (apply the non-holder ratification
`governance/CONSTANTS_RATIFICATION_MBS308.md`, research 3c2a7854, CONSTANTS_RATIFIED_WITH_CHANGES, exactly; the
deterministic M33 run) and C-1 (`packed-refs.lock` out of the campaign's lock handling), plus the reviewer's
recommended N-2 and N-3 (a failed `ps` is never evidence of death). **No operational value was chosen by the
editor:** every changed constant is a ratified ruling, and every test-only value is the builder's proposal as the
reviewer checked it. The science, the guard, the 46 carried driver definitions and MB r1's bytes are unchanged.
Base 35cabb50; working tree only until the repair commit.

**Read for this repair.** The delta review (99185dcb) and the ratification (3c2a7854); BUILD_REPORT sections 1-8 and
10-12 (section 9 was not opened); the successor's code, tests and protocol draft; MB r1's `mb308_driver.py` at freeze r3
c46434a3 (only to regenerate DRIVER_DIFF.md) and `mb308_stage1.jobs` (job order, for the M33 argument); CPython 3.14's
`concurrent/futures/process.py`; in the research namespace, briefs 42, 43 and 43-E1, the brief index, the ledger's
format, governance erratum E1 section D3 and the conditions register's holder rows. No MBS-2 file and nothing under MB r1's
review, adjudication, postexec or evidence directories was opened.

**Exposure disclosure (for the reviewer's ruling under the T6 ruling's M4).** This editing session's auto-loaded
memory, written earlier by the coordinator (a holder), carries a qualitative chronology of MB r1's one execution,
including clock times. It carries no per-job, progress, CPU, memory, host or science figure. It is not repeated
anywhere in this build, and no edit here depends on it: every operational value applied is the ratifier's, and the
M33 test values are builder2's proposal as reviewIMPL measured it.

### R3: the ratified constants, applied exactly

| ratification item | where | before (35cabb50) | after |
|---|---|---|---|
| 16 EXCL_ALLOW | `code/mbs308_driver.py` | the 39 names | the same 39 ∪ {`spotlightknowledged.updater`, `cloudd`, `BackgroundShortcutRunner`, `modelcatalogd`} (provisional; R-ALLOW at the freeze) |
| 31 launcher preflight timeout | `code/mbs308_launch.py` `pre_launch` | `timeout=1900` | `timeout=PRE_CAP_S + 100`, with `PRE_CAP_S = driver_literal("PRE_CAP_S")` read from the driver's own bytes (the launcher never imports the driver, which would load the science); the value is still 1900 s at PRE_CAP_S 1800, and it follows any change of PRE_CAP_S |
| 10 / 11 MEM_CAP | driver comment; protocol s8 | comment stated the superseded rule | value unchanged (3 GiB, provisional); the comment and protocol s8 state R-MEM |
| 14 FREE_MEM_MIN | driver comment; protocol s8 | "free memory >= 2 GiB" | value unchanged (2 GiB, provisional); R-FREE |
| 15 EXCL_CPU_PCT | driver comment; protocol s8 | 25 | value unchanged (25); R-EXCL-PCT (its single exception is a freeze-time rule, so no code) |
| rules | protocol s8 | none | R-MEM, R-FREE (with its attainability clause), R-EXCL-PCT and R-ALLOW (with its exclusions), copied programmatically from the committed ratification; the four constants frozen as rule outputs from official evidence; the superseded memory rule removed; the optional builder recommendation (a path test for R-ALLOW (b)) not taken, so (b) is checked and recorded per addition at the freeze |
| 33 (review) | protocol s8; here | not listed | the ref-write retry of repair R1 (i) reuses MB r1's frozen `SEAL_RETRY_DELAYS` = 0.5, 1, 2, 4 s (source (a); completion only; no new number) |
| launcher rule text | protocol s7; launcher docstring | none | the preflight timeout stated as the rule PRE_CAP_S + 100 s |

The sixteen items ratified as they stand are unchanged.

**Pins.** `HELPER_SHA256` re-pinned for the three edited helpers (guard unchanged):
`mbs308_host.py` `26ac9538071ee1803b900c96390fbbba12f1ca6841ca7cf3cbb7d9533763d08d`, `mbs308_state.py` `aaf76e86a059d07d24f868a2f136333af210a4ac8632f0aa757d4233e5cd5aff`, `mbs308_launch.py` `38cb35a31a80f174b9f84837840c8f6cabdb9982d8d7a668fdb76993f01ba1cb`. Driver sha256 `d13688d120fb7efb64e5c08169ea6481a93fb8b110f0f442e2030092ac8c4aa4`.
PLATFORM_PINS and SCIENCE_PINS unchanged. **DRIVER_DIFF.md** regenerated: 22 hunks, the same classes and the same
touched definitions per hunk; only hunks 4 (the MEM_CAP comment and the helper pins) and 8 (the GC-10 comment and
EXCL_ALLOW) change content, the rest shift line numbers. The generator (Python `difflib.SequenceMatcher`,
`autojunk=False`, 3 lines of context, labels carried) first reproduced the committed 35cabb50 DRIVER_DIFF.md byte for
byte; it lives in the editor's scratch and is not part of the namespace.

**M33, deterministic.** `t_S01_worker_death` now starts with the run `{"worker_die": "RLR.0.6", "job_sleep": 90}`
under the unchanged 60 s bound (harness timeout 150 s, so an unreleased run fails the bound by assertion, never by an
exception); the seven existing runs follow unchanged. Why it cannot depend on timing: every synthetic job sleeps 90 s;
RLR.0.6 is the first job of MB r1's order (`jobs` sorts by kind weight, then rung, then block) and dies at once; the
other worker has either taken the next job (a 90 s sleep) or is blocked reading the call queue. It ignores SIGTERM,
and CPython 3.14's `terminate_broken` holds the executor's shutdown lock while it joins every worker, so the driver's
`shutdown` blocks until that worker exits by itself (at least 90 s) unless `_MemWatch._release_broken` SIGKILLs it
within one 2 s poll. M33 removes exactly that release.

### C-1: `packed-refs.lock` is never the campaign's

* `mbs308_state.git_lockfiles` lists only `refs/p5y-k5-cell308-mbs-r1/*.lock` and the branch lock. Since
  `move_stale_git_locks`, `git_lock_info`, the classifier, `recover` and every post-marker `GIT_LOCKED` refusal
  (`check_not_evaluated`, `resume`, `seal-only`, `close-indeterminate`) take their set from it, `packed-refs.lock` is
  no longer detected, refused on after the marker, moved aside or recorded. Nothing else in the campaign code names
  it except MB r1's carried, text-identical `check_clean`, which still refuses it before the marker (nothing
  consumed). After the marker it does not block the campaign's ref creates and updates; a ref write that fails for
  any reason takes the recorded `RefWriteError` path (fail closed). No replacement mechanism touches it.
* Protocol s4: the lock set, and a paragraph stating why `packed-refs.lock` is never a campaign lockfile.
* Tests: `t_L09_packed_refs_lock_stale` is replaced by `t_L09_packed_refs_lock_never_moved` (planted after a crash,
  mid-run at the 4th checkpoint, at F8, and before execute; each time the file stays in place byte for byte,
  git-locks-aside stays empty, no recover action names it; the runs seal with no failed ref write; before execute the
  refusal is `GIT_LOCKED` with nothing consumed and execute seals once git's lock is gone).
  `t_L11_packed_refs_lock_open` becomes `t_L11_campaign_lock_open` (the open-handle guard, now on the campaign's
  ckpt lock). M38 re-targeted to it; new M48 restores `packed-refs.lock` to the lock set.
* The test library's sandbox reset (`wipe_state`) still unlinks a planted `packed-refs.lock` in the SANDBOX: test
  harness only, never campaign code.

### N-2 / N-3 (bounded R2 hardening)

* **N-2**, `mbs308_host.identity_state`: a recorded field that is missing (an identity recorded while `ps` or the
  boot-UUID read failed) is never compared. While the pid exists such an identity is UNKNOWN (the launcher keeps
  waiting and never boots it out); once the pid is gone it is DEAD. A complete record behaves as before.
  Test `launch::t_identity_state_positive_evidence`; mutant M49.
* **N-3**, `mbs308_state.git_lock_info`: a recorded campaign identity (journal process, pidfile, recover-lock holder)
  holds the campaign lockfiles unless `identity_state` is DEAD; a failed `ps` (UNKNOWN) keeps them held (recover exits
  8, nothing done). Test `crash::t_L12_lock_ps_failure_not_stale` (child-harness knob `ps_fail_pids`, a planted
  reading failure); mutant M50; M37's fragment re-targeted to the rewritten pidfile line (same meaning).
* **Left for a separate reviewed delta (documented, not changed):** the other `identity_alive` users, where a failed
  `ps` still reads as "not alive": the classifier's CONSUMED_COMPUTING test (M11's line: a live computing driver whose
  `ps` fails would classify CONSUMED_INTERRUPTED, and a resume would race it; only the journal CAS / LostOwnership
  protects), `Lock.acquire` (a live holder's recover lock could be broken; the journal CAS is the second line),
  `read_pidfile` (preflight's other-job gate; pre-marker, the marker CAS decides) and `check_not_evaluated`'s
  stale-intent takeover (pre-marker, the marker CAS decides). Changing them changes the frozen state table (protocol
  s4), which is beyond this delta. N-1 (`cur == new` as success) is also not applied.
* Test infrastructure: the mutant runner forwards `MBS308_BASE_STORE` to its target tests, so a matrix run uses its
  own base store rather than the library default.

### Tests and mutants (this code; reports in the editor's scratch)

* `test_mbs308_static.py`: **10/10 PASS** (the 9 carried + `t_r3_ratified_rules_applied`). Negative controls on a
  scratch copy: a one-token change of R-MEM, a dropped daemon, a missing timeout rule and the superseded rule restored
  each make it FAIL; the unedited copy passes.
* `test_mbs308_launch.py`: **10/10 PASS** (the 8 carried + `t_identity_state_positive_evidence`,
  `t_preflight_timeout_rule`: timeout 1900 at PRE_CAP_S 1800, 1334 when a copy's PRE_CAP_S is 1234). Real launchd jobs
  with the synthetic payload under the test prefix, all booted out, no plist left;
  `t_launcher_refuses_execute_when_preflight_fails` ran the real driver's read-only `preflight` (PREFLIGHT_FAILED on
  this host).
* `test_mbs308_state.py`: **45/45 PASS** (the 44 carried + `t_gc10_ratified_allow_list`).
* `test_mbs308_crash.py`: **48/48 PASS** (L09 replaced, L11 renamed, + L12), twice (the second run on the final
  test bytes, after the L09 fix below). The deterministic S01 run, unmutated: 10.7 s and 7.3 s (bound 60 s).
* `test_mbs308_decoy.py`: not re-run. It computes a real dev decoy (cell 297) through paths this repair does not
  touch (checkpointing pool, checkpointer, stage 1); nothing it exercises changed.
* **Mutant matrix: 52/52 KILLED; the unmutated code passes every target test.** M01-M47 as before (M37's fragment
  and M38's target re-targeted, meanings unchanged) + M48 (C-1), M49 (N-2), M50 (N-3), M51 (the four daemons), M52 (the
  timeout literal). Every per-mutant result file was checked: each kill is the target test's own assertion, with no
  error, timeout or missing result. **One correction:** in the full matrix M48's first "kill" was an exception in
  L09's own clean-up (`lk.unlink()` after the mutant had moved the file aside). L09 now removes the planted file with
  `missing_ok=True` after its assertions; re-run: unmutated L09 PASS, M48 KILLED by assertion (the lock was listed
  and moved aside in sub-cases (a) and (d)).
* **M33, three independent runs (the matrix and two `--only M33` runs):** KILLED each time by the deterministic run
  alone (95.6 s, 96.6 s, 96.3 s against the 60 s bound; status otherwise correct, rc 5), while the seven carried runs
  passed under M33 in two of the three (in the third one carried run also happened to hang, 100.7 s: the old,
  timing-dependent kill). Unmutated, the deterministic run took 7.4 s and 8.1 s in those runs' unmutated phases.

### Integrity

* **New cell-308 target evaluations: 0.** Every state-changing test used the synthetic evaluator in sandboxes cloned
  from the editor's own `git clone --no-local --bare` base store; the only real-driver invocations were the read-only
  `preflight` (launch test) and `status` in a sandbox copy (static test). Cells 305-309 and cell 309's campaign were
  not touched.
* Real repository, checked before the repair commit: the 144 refs are byte-identical to the pre-edit snapshot
  (2026-09-30T02:30:03Z); **no ref under `refs/p5y-k5-cell308-mbs-r1/`**; MB r1's marker still names
  `afa930727d084a5b70e6b85d30ca8f34c0e8ae74`; no `mbs308-spool` in the real git dir; no `packed-refs.lock`; no object
  created or modified in the real object store since the snapshot (checked with a positive control). No launchd job or
  plist of the campaign is left.
* MB r1's bytes, the guard, the science pins, PLATFORM_PINS and the historical reviews are unchanged.

## 14. Option B: items 16 and 31 withdrawn and re-applied by a non-holder (steps W, N), and the liveness delta (step L) (builder `builder3`, brief 45, research 5e7b8cdc)

**Scope.** The user ruled on the T6 ruling's M4 with option B: the four ratified allow-list names and the preflight
timeout expression must be applied by a genuine non-holder, not by the exposed editor (`editorR3C1`) who applied them at
191ce4a9. The same instruction asks for the liveness delta that the non-holder reviewer reviewR3C1 recommended
(REVIEW_IMPLEMENTATION_MBS308_DELTA_R3, research 58cfe66b, section 3 and coverage note X4). I am `builder3`, a fresh
builder who holds no MB r1 run observation (the exposure statement at the end of this section says exactly what my
context holds). I chose no operational number: the two values of step N are the ratifier's (CONSTANTS_RATIFICATION_MBS308,
research 3c2a7854, items 16 and 31 and its requested changes 2 and 3), and step L changes no number at all. Sections 1-13
are unchanged; this section is additive.

**Read.** Brief 45 (research ledger/briefs/45_builder3_optionB_liveness.txt); CONSTANTS_RATIFICATION_MBS308 (3c2a7854, in
full); REVIEW_IMPLEMENTATION_MBS308_DELTA (99185dcb) and REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 (58cfe66b), both in full;
the successor's code, tests, protocol draft and this report's sections 12 and 13; MB r1's `mb308_driver.py` at c46434a3
(only to regenerate DRIVER_DIFF.md); the diffs 35cabb50..191ce4a9 of the driver and the launcher (step W needs them); the
research quarantine module's `log_event` and the ledger's last lines (format). **Not opened:** any MBS-2 file
(REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*, REVIEW_SUCCESSOR_GOVERNANCE_308*,
INCIDENT_INDEPENDENCE_REVIEW_MBS308* including T6, COORDINATOR_EXPOSURE_DISCLOSURE*), anything under
`p5y_k5_cell308_mb_r1/{review,adjudication,postexec,evidence}/`, this report's section 9 (a `grep '^## '` listing of the
headings showed its title line only), any other session's or agent's scratchpad, anything under `/Users/suzhe/.claude/`.

### Step W — withdrawal of the editor's application (committed by the coordinator as 4a960e06)

Mechanical; no value chosen.
* `code/mbs308_launch.py`: the whole file restored to its bytes at 35cabb50 (sha256 c829b9ed…; `git diff 35cabb50`
  empty).
* `code/mbs308_driver.py`: the `EXCL_ALLOW` assignment (39 names) and the absence of a comment line above it restored to
  35cabb50 (the assignment's AST source segment byte-identical); the launcher pin re-pinned to c829b9ed…. Nothing else
  touched: the editor's comments for items 10/11/14/15 and the host / state pins stay as at 191ce4a9.
* DRIVER_DIFF.md regenerated. The generator (Python `difflib.SequenceMatcher(autojunk=False)`, 3 lines of context,
  unified-diff hunk headers; each hunk's touched top-level definitions from the AST line ranges of the CHANGED lines of
  both files; class labels and header text carried from the committed file) first reproduced both the 191ce4a9 and the
  35cabb50 committed DRIVER_DIFF.md byte for byte. It lives in my scratch, not in the namespace. Applying the regenerated
  hunks to MB r1's c46434a3 driver reproduces the successor driver byte for byte (checked at W, N and L).
* Expected and observed: static 9/10, only `t_r3_ratified_rules_applied` FAILS and only on `excl_allow` (old 39, new
  39; its verbatim-rules, superseded-rule and section-7 checks pass); `launch::t_preflight_timeout_rule` FAILS (1900
  when a copy's PRE_CAP_S is 1234); `state::t_gc10_ratified_allow_list` FAILS (each ratified daemon refused
  HOST_PREFLIGHT). All by assertion (no error).

### Step N — items 16 and 31 re-applied from the ratification text (committed by the coordinator as b0dd8e93)

* **Item 16** (`code/mbs308_driver.py`): the `EXCL_ALLOW` literal continues after "UserEventAgent" with
  `"spotlightknowledged.updater", "cloudd", "BackgroundShortcutRunner", "modelcatalogd"` (the ratification's order, filled
  to the file's 120-column width), under a two-line comment naming item 16 and R-ALLOW. By AST: 39 → 43, exactly those
  four added, nothing removed. Provisional; R-ALLOW decides the frozen list at the freeze.
* **Item 31** (`code/mbs308_launch.py`): `pre_launch` runs the preflight with `timeout=PRE_CAP_S + 100`. `PRE_CAP_S`
  is the driver's own: `driver_pre_cap_s()` parses the driver's BYTES (`ast.parse`; the launcher never imports the
  driver, which would load the science) and requires exactly one module-level binding `PRE_CAP_S = <int literal>`;
  anything else (missing, bound twice, augmented later, annotated, not an int literal) raises
  `LaunchRefused("DRIVER_PRE_CAP_S")` at import, so the launcher refuses to load. The module and `pre_launch` docstrings
  state the rule. A scratch probe on copies (the driver never run): 1900 as the files stand, 1334 at PRE_CAP_S 1234, and
  a refusal for each malformed variant.
* Against 191ce4a9: the `EXCL_ALLOW` literal is byte-identical (only its comment differs); the timeout expression and
  its value (1900 s) are identical. My reader is stricter than the editor's `driver_literal` (which took the first match
  and raised RuntimeError only when the name was missing). The M51 / M52 fragments occur exactly once in my bytes and
  were not changed.
* Results: static 10/10, launch 10/10, `state::t_gc10_ratified_allow_list` PASS; M51 and M52 KILLED by their targets'
  own assertions. The coordinator's byte-level re-check of N was PASS (research b3cc9675; I did not read that file).

### Step L — the liveness delta (REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 section 3; coverage note X4)

**Code (the two sites only), `code/mbs308_state.py`.**
* The classifier's CONSUMED_COMPUTING test (the line M11 targets): `if _not_dead(jrec.get("process"), cur_boot, None):`
  instead of `HOST.identity_alive(...)`. The why code is now `PROCESS_NOT_PROVABLY_DEAD` (it was
  `PROCESS_ALIVE_SAME_BOOT`; no test or code reads it).
* `Lock.acquire`: `if _not_dead(holder, None, None):` instead of `HOST.identity_alive(holder)`; the class docstring
  states the rule.
* Both reuse the N-3 function `_not_dead` unchanged, so the rule is literally the one N-3 already applies to the
  git-lockfile sources: a RECORDED identity counts as alive unless `HOST.identity_state` says DEAD (a failed `ps` or
  boot-UUID reading is UNKNOWN, never evidence of death); no recorded identity (not a record, or a record naming no pid)
  means no process. With `exclude_pid` None, the reviewer's edge note (a record without a pid) now reads "no process" at
  all three sites that pass None, and UNKNOWN only in `move_stale_git_locks`' own re-check, which fails closed.
* Not changed (outside this delta, as the brief fixes): `read_pidfile` (the preflight's other-job gate) and
  `check_not_evaluated`'s stale pre-marker intent takeover keep the all-fields-match `identity_alive`.
* No number, cap, timeout or poll changed. Re-pinned: `mbs308_state.py` 81788fa8…; driver a75bafd3…; DRIVER_DIFF.md
  regenerated (22 hunks, index unchanged; only the header sha and hunk 4's state pin change).

**Protocol draft section 4.** The CONSUMED_UNRECORDED / COMPUTING / INTERRUPTED rows now say "positively dead" /
"not positively dead (ALIVE or UNKNOWN)", and a new paragraph *Liveness of a recorded process identity* states the one
rule for the classifier, the O_EXCL recover lock and the git-lockfile staleness test, and the **fail-closed
consequence**: while `ps` keeps failing for a recorded pid that still exists, or the boot-UUID read keeps failing at all,
the run stays CONSUMED_COMPUTING (recover waits, exit 8; resume, close-indeterminate and seal-only refuse) and a recover
lock naming that identity is never broken (LOCKED); there is no timeout; it ends only on positive evidence (the boot UUID
reads again and differs, or the pid is gone or belongs to another process), after which the table applies as written (a
deadline passed meanwhile gives CONSUMED_UNRECORDED and close-indeterminate).

**Tests (new; test-only values: the existing `T.Helper` sleep helper for 300 s / 120 s, the existing F3 crash at the
4th checkpoint, planted `ps` failures for the helper's pid only).**

| suite | test | what it asserts |
|---|---|---|
| state | `t_computing_ps_failure_not_interrupted` | (a) the journal's recorded process is a live helper whose `ps` fails (child knob `ps_fail_pids`; an in-process control shows the planted reading is UNKNOWN): CONSUMED_COMPUTING, recover waits (exit 8, "-> wait"), resume refuses RESUME_REFUSED, no ref moved; helper gone: CONSUMED_INTERRUPTED, recover resumes (attempt 2) and seals the uninterrupted certified bytes, one marker |
| crash | `t_S13_lock_ps_failure_not_broken` | (b) after an F3 crash the recover lock names a live helper whose `ps` fails: recover refuses LOCKED, the state stays CONSUMED_INTERRUPTED, the lock stays byte for byte, nothing moved aside; helper gone: the stale lock is moved aside (one `recover.lock.rejected-stale-lock-*`), recover resumes and seals the uninterrupted bytes, no verified checkpoint recomputed |
| crash | `t_L13_lock_sources_ps_failure_each` | (c) after an F3 crash, with the campaign's ckpt lockfile planted, `git_lock_info` read DIRECTLY (the classifier's change would mask the journal source end to end) with `ps` failing in-process for a live helper: each source alone — the journal's recorded process, the recover lock's holder, the pidfile — holds the lockfile (`live == [that source]`, not stale); no source live: stale (before, and after the helper dies). End to end: the journal naming the live helper → recover exits 8, lockfile intact; helper gone → recover moves it aside (recorded) and seals the uninterrupted bytes |

**Mutants (new; M11 re-targeted).**

| id | fragment (in `mbs308_state.py`) | target | result |
|---|---|---|---|
| M11 | (re-targeted, same meaning: resume on a live process) the new classifier line → `if False:` | `state::t_computing_then_interrupted` | KILLED |
| M53 | classifier site reverted to `HOST.identity_alive(jrec.get("process"), cur_boot)` | `state::t_computing_ps_failure_not_interrupted` | KILLED |
| M54 | `Lock.acquire` reverted to `HOST.identity_alive(holder)` | `crash::t_S13_lock_ps_failure_not_broken` | KILLED |
| M55 | reviewR3C1's X4: only the journal source of `git_lock_info` reverted to `HOST.identity_alive(jrec.get("process"), boot_uuid)` | `crash::t_L13_lock_sources_ps_failure_each` | KILLED |
| M56 | only the recover-lock source of `git_lock_info` reverted to `HOST.identity_alive(holder, boot_uuid)` | `crash::t_L13_lock_sources_ps_failure_each` | KILLED |
| M15 | (re-targeted, same meaning: ignore the boot UUID, so a reboot is not an interruption) `identity_state`'s boot comparison → `if False:` | `state::t_reboot` | KILLED |
| M57 | M15's former fragment: `identity_alive` ignores the boot UUID | `state::t_stale_pidfile` | KILLED |

Each kill is the target test's own assertion (every per-mutant result file checked: `ok` false, no `error`): M53 reads
CONSUMED_INTERRUPTED where COMPUTING is required; M54 resumes where LOCKED is required; M55's journal case reads
`live []`, stale; M56's recover-lock case likewise. M50 (N-3's `_not_dead` body) now also reaches the two new sites and
is still KILLED by L12.

**M15 re-targeted (found by the full matrix).** The first full matrix on the final code gave 55/56: M15 SURVIVED. Its
fragment removed the boot comparison from `HOST.identity_alive`, which the classifier no longer calls, so `t_reboot`
(a simulated reboot: the recorded process is alive, the classifier's boot UUID differs) passed under it. The classifier's
reboot detection now lives in `HOST.identity_state` (`if ident.get("boot_uuid") and ident["boot_uuid"] != cur_boot:
return "DEAD"`), so M15 is re-targeted there with the same meaning and the same target; it is KILLED (under it the
rebooted classification reads CONSUMED_COMPUTING and recover waits). M15's former fragment is kept as the new M57, whose
target `t_stale_pidfile` already asserts that a pidfile recorded under another boot reads STALE (the `wrong_boot` case);
it is KILLED (that case reads LIVE). Both were first run on the unchanged final code (`--only M15,M57`; unmutated `t_reboot`
and `t_stale_pidfile` PASS), then the whole 57-mutant matrix was re-run as one run (below).

### Results on the final code (my own `git clone --no-local --bare` base store; sandboxes only)

| run | result |
|---|---|
| `test_mbs308_static.py` | **10/10 PASS** |
| `test_mbs308_launch.py` | **10/10 PASS** (real LaunchAgents with the SYNTHETIC payload under the test prefix; see below) |
| `test_mbs308_state.py` | **46/46 PASS** (45 + `t_computing_ps_failure_not_interrupted`) |
| `test_mbs308_crash.py` | **50/50 PASS** (48 + `t_S13_lock_ps_failure_not_broken`, `t_L13_lock_sources_ps_failure_each`) |
| **full mutant matrix (57), the reported run** | **57/57 KILLED**; unmutated: all 51 target tests PASS (one run, 09:11Z-09:48Z, after the coordinator freed disk: 98-111 GiB free at my checks) |
| earlier full matrix (56, before M15's re-target) | 55/56 KILLED, survivor M15 (above); unmutated 51/51 PASS |
| `--only M15,M57` | 2/2 KILLED, unmutated targets PASS |

Every per-mutant result file of the reported run was checked: each kill is the target test's own assertion (`ok`
false, no `error`), with no timeout and no missing result, and no report or result file contains an ENOSPC / "No space
left" symptom. M33 was killed by the deterministic run (`RLR.0.6+sleep90`, 95.3 s against the 60 s bound); in this run
one carried run also happened to hang (`C2B.2.20#1`, 96.6 s; the old timing-dependent path), the other six carried runs
took 5.1-6.0 s and passed; in the earlier full matrix the deterministic run alone killed it (96.0 s; the seven carried
runs 6.5-7.4 s). Earlier runs this step (same code): the new tests alone (state 2/2, crash 4/4 with L12 and S03), and
the six liveness mutants M11, M50, M53-M56 alone (6/6 KILLED, unmutated PASS).

**Disk check (the coordinator's request).** The static, launch, state and crash suites and the earlier matrices ran
while the data volume was nearly full. I checked every step-L report and every per-mutant result file for ENOSPC / "No
space left" / truncated-file symptoms and for `error` fields: none, apart from the one invalid run below; every suite
test PASSED (a disk failure shows as a failure, never as a pass). The kills, which a disk failure could in principle
fake as an assertion failure, were all re-established by the 57-mutant re-run on ample disk. My sandboxes were deleted
afterwards; only the JSON reports and per-mutant result files remain in my scratch (plus my 458 MB base store).

**One invalid run, disclosed.** The host's data volume filled up during this step (ENOSPC; 394 MiB free at the lowest,
the space taken outside my scratch). To stay within it I deleted my own finished step-W/N sandboxes (my scratch only;
their JSON reports kept) and ran the mutant matrices with a small cleaner of my own that deletes a mutant's sandbox once
its result file exists. Its first version had a glob-count bug and deleted the UNMUTATED sandboxes while they were in
use, so the first run of the six liveness mutants (ledger line 07:12:12Z) is INVALID (its unmutated targets errored on
missing sandbox files). I fixed the cleaner and re-ran; every result above comes from the fixed cleaner. Nothing outside my scratch was
touched. To diagnose the full disk I ran a size-only `du` over the project's temporary tree, which traversed other
sessions' directories' metadata; I opened no file there and listed no names.

**Launchd.** LaunchAgents with the SYNTHETIC payload were bootstrapped under the TEST prefix
`org.rebaseguard.mbs308.test.`: step N `20260930T062221`, `ld20260930T062226`, `wc20260930T062227803790`,
`nb20260930T062231170629`; step L's launch suite `20260930T072429`, `ld20260930T072434`, `wc20260930T072436687728`,
`nb20260930T072440458628`; the matrices' launch targets `wc20260930T075438102052`, `nb20260930T075434852520`,
`wc20260930T082305889954`, `nb20260930T082309230665` (earlier matrix), `wc20260930T091858365939`,
`nb20260930T091855376530`, `wc20260930T094316745243`, `nb20260930T094320053923` (reported matrix). Each was booted out by its test's teardown; `launchctl list` shows
no rebaseguard job and no plist is left (my scratch or `~/Library/LaunchAgents`). Their empty logs stay in
`~/Library/Logs/ReBaseGuard/mbs308-test/`, as in the previous reviews.

**Integrity.** New cell-308 target evaluations: **0**. No cell in 305-309 and no drift in [6/5, 13/5] or its mirror was
evaluated; cell 309 not touched; no authorization, grant, marker, pending result or seal created. The only real-driver
invocations were the launch suite's read-only `preflight` and the static suite's `status` in a sandbox copy. Real
repository: the 144 refs are identical to my snapshot except the two branch heads the coordinator moved
(`p5y-k5-cell308-mbs-r1` → 4a960e06 → b0dd8e93; the research branch); no ref under `refs/p5y-k5-cell308-mbs-r1/`; MB
r1's marker still names afa93072; no `packed-refs.lock` and no `mbs308-spool` in the real git dir. I made no git write:
every step is left in the successor worktree for the coordinator to commit. Pins at the end of step L:
`mbs308_host.py` 26ac9538…, `mbs308_state.py` 81788fa8…, `mbs308_launch.py` 1510308a…, guard 48903487… (unchanged);
driver a75bafd3…; PLATFORM_PINS and SCIENCE_PINS unchanged; MB r1's bytes unchanged.

**Research-ledger lines** (agent `builder3`, `c308_quarantine.log_event`, classes INFRASTRUCTURE / SYNTHETIC_VALIDATION,
target_evaluations 0 on every line, no LEAK_FLAG): step W 05:58:57Z, 06:05:07Z, 06:07:43Z; step N 06:21:50Z, 06:28:02Z;
step L 07:06:25Z (new tests), 07:12:12Z (the invalid run), 07:16:41Z (its re-run; that line's note misdates the invalid
run as 06:5xZ, corrected here and in my last line), 07:24:20Z (full suites), 07:45:55Z (full matrix), 08:37:32Z (M15 /
M57), 09:05:21Z (this section, first version), 09:11:17Z (the reported matrix re-run), and a last line.

**Left open (not in this delta).** `read_pidfile` and `check_not_evaluated`'s stale-intent takeover keep
`identity_alive` (the brief fixes the two sites); N-1 is not applied; the other freeze prerequisites listed by
REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 are unchanged.

### Exposure statement (builder3)

I read no MB r1 run record, review, adjudication, postexec or evidence file. What my context holds about MB r1 that did
not come from an allowed file, disclosed as brief 45 requires:
1. **Auto-loaded memory index.** My session began with the user's memory index in context (I opened no file of it).
   Lines touching MB r1: an outcome label of its one execution (the same label the allowed governance texts carry), with
   the successor's pre-freeze status; a lesson line on host sleep and thermal slowdown inflating wall times (provenance
   unknown to me); a successor-lessons line (never move `packed-refs.lock` aside; timing-dependent mutant kills are not
   kills; liveness needs positive evidence), which are the conclusions of reviewIMPL's committed C-1, M33 and N-3 and of
   reviewR3C1's recommendation, all re-read in the allowed reviews.
2. **Two commit subjects.** My first `git log --oneline -5` in the successor worktree showed the one-line subjects of MB
   r1's grant commit (afa93072) and postexec commit (21e99cf0). The postexec subject carries a qualitative chronology of
   the execution with clock times. This is the same inadvertent exposure the ratifier and reviewR3C1 disclosed.
3. **The editor's bytes.** Step W required reading the editor's 191ce4a9 application (the diffs of the driver and the
   launcher against 35cabb50) before I re-applied items 16 and 31 in step N. Every value of step N comes from the
   ratification's text; my launcher code is my own.

None of this contains a per-job, progress, CPU, memory, host or science figure; I repeat none of it; no edit or value
here depends on it.


## 15. The qualification framework, decision-independent parts (non-holder builder4, research brief 46 at e2d2b026, integrated under brief 49 at 8c45f256; NOT frozen)

**Scope.** Briefs 46 and 49 only: the successor's qualification FRAMEWORK and every case that is the same under every
option of the user's pending decisions S16(c), MBS-6, MBS-7 and MBS-8; the option-dependent cases are declared and fail
closed. Built in builder4's own scratch copy of the namespace (`git archive b0dd8e93`), then integrated on the
coordinator's INTEGRATE (brief 49) onto successor `216c465f` (builder3's step L, DELTA_ACCEPTED at research 2308651e).
Nothing here authorises a freeze, a qualification run or any target step. **New cell-308 target evaluations: 0.** No
science computation, no decoy, no cell 305-309, no drift in [6/5, 13/5] or its mirror; cell 309 not touched. No
operational number of the campaign was changed or chosen (caps, limits, timeouts, thresholds, allow-list, budgets,
polls): the rule functions carry the ratification's numbers, and every test value is planted. No freeze manifest was
written in the worktree; no official qualification run; no git write.

**Read.** Briefs 46 and 49; MB r1's `code/mb308_qualify.py`, `code/mb308_manifest.py`, `config/QUALIFICATION_CASES.json`
and protocol sections 3.2, 9 and 10 (at b0dd8e93); this namespace's protocol draft sections 1 and 3-11 (section 2 not
needed), code, tests, BUILD_REPORT sections 1-8 and 10-13 (section 9 NOT opened; builder3's section 14 not needed and not
read beyond its heading); builder3's diff b0dd8e93..216c465f of the mutant runner, the driver pin, DRIVER_DIFF.md and
protocol section 4; research `governance/CONSTANTS_RATIFICATION_MBS308.md` (3c2a7854),
`governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` sections A and G (G only for the T6 record's commit, path, sha256 and
verdict line), `governance/SUCCESSOR_CONDITIONS_REGISTER_308.md`, brief 45's lines naming the T6/M4 ruling, the ledger's
agent names and classes, and `code/c308_quarantine.py`'s `log_event`. File NAMES only (never contents) of `reviews/`,
`audit/` and of the commits the register cites (`git diff-tree --name-only`), to fill QC13-S's record table; for the
record added at integration (REVIEW_OPTIONB_LIVENESS_MBS308.md, research 2308651e) the verifier's own `check_record`
was run once against the real repository, printing only its status (OK). No MBS-2 file was opened; nothing under MB
r1's review, adjudication, postexec or evidence directories was read; no other agent's scratchpad; nothing under
~/.claude/.

### 15.1 Built (integrated bytes at 216c465f + this section)

| file | sha256 (prefix) | role |
|---|---|---|
| `code/mbs308_qualify.py` | `7d679dd2a422f104…` | the verifier framework: modes official / --review / --dev (MB r1's); preconditions; aggregator; the BUILT cases; the declared cases |
| `code/mbs308_manifest.py` | `1a0698d17a40cbd7…` | the Q8 freeze-manifest writer (`--freeze` only, or `--out` outside the repository) |
| `code/mbs308_rrules.py` | `688347d3a00e0317…` | R-MEM, R-FREE (attainability), R-EXCL-PCT, R-ALLOW as pure functions; every number the ratification's |
| `config/MBS308_QUALIFICATION_CASES.json` | `a3df97e2d66d17c0…` | case -> gates -> status; suites; commit pins; QC13-S governance records (12); the ledger agents; the ratification's H3 readings |
| `tests/test_mbs308_qualify.py` | `cc8de09884596360…` | 22 target-free tests |
| `tests/test_mbs308_mutants.py` | (changed) | + MQ01-MQ34 appended after builder3's M57 (one per new gate); M01-M57 byte-identical |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | (changed) | + sections 11.1 (plan), 11.2 (the sequencing question), 11.3 (readings of the rule text), before section 12 |

**Cases BUILT** (each summary carries a boolean `pass`): QS-STATIC, QS-STATE, QS-CRASH, QS-LAUNCH, QS-QUALIFY
(suites run in a fresh process with `MBS308_SCRATCH` / `MBS308_BASE_STORE` under `--work`, i.e. sandboxes on a separate
`--no-local` base store; counts recorded; pass iff > 0 tests, all ok, exit 0), QS-MUTANTS (pass iff the unmutated code
passes, the matrix holds exactly the declared mutants and every one is killed BY ASSERTION: an error, a timeout or an
invalid mutant is not a kill), QC09-S (the one-line guard diff against MB r1's pinned guard bytes, the driver's binding
and pin, DECOY refusals in a fresh process importing only the guard, and the arming sequence in a throw-away repository:
no marker, MB r1's marker at HEAD, a marker naming another commit, a grant not at HEAD, a dropped pair and an extra
band pair are refused; the successor marker with exactly the frozen set arms), QC11-S (18 structure checks of the
successor driver that QS-STATIC does not cover, plus MB r1's science-byte checks re-run on the pinned bytes; the list of
what QS-STATIC already covers is in the case output), QC12-S (MB r1's scans re-targeted: the pinned pattern file read at
run time, the timing-key exemption only for JSON under the post-freeze directories, the record-token scan with the
exemption only in the guard source and the manifest's `guard.cell308_cover`; planted controls built at run time;
counts and file names only), QC13-S (preconditions, r5 / no r6, the successor agents' ledger lines, 12 governance
records by commit and path), Q8-S (every namespace file, 49 external pins at HEAD, 5 commit pins, the driver sha256,
the recorded constants / pins / guard field, the driver's `check_bindings`), R_RULES_CONTROLS (37 planted controls
through the four rules, and the ratification's H3 evidence reproducing the item-16 list).

**Cases DECLARED, failing closed** (`pass: false`, `status: PENDING_USER_DECISION`, `depends_on`): QC01-QC08,
Q1_theory, QC09-SCI (MB r1's in-process guard test through the science paths), MBR1_REPRO, QS-RESUME-DECOY (MBS-7;
QC02 / QC03 / QC08 also MBS-8), Q12_caps and R_RULES_OFFICIAL (MBS-8 and the sequencing question of protocol 11.2).
QC13-S is BUILT but fails closed while two records are un-named: the implementation review accepting the frozen build,
and the user's freeze decision record (S16(c), MBS-6/7/8). No qualification can pass today.

### 15.2 Integration onto 216c465f (brief 49): merge notes

* Base: successor `216c465fd48d779ceef876fd13b1422773dfea31` (parent b0dd8e93, builder3's step L). builder3's bytes
  are unchanged: the worktree diff against 216c465f has no deleted line in any tracked file.
* New files added as built, with two updates the new base requires: `config/MBS308_QUALIFICATION_CASES.json` gains the
  governance record LIVENESS_DELTA_ACCEPTED (research 2308651e, `reviews/REVIEW_OPTIONB_LIVENESS_MBS308.md`, verdict
  DELTA_ACCEPTED on line 2, on the research branch; 12 records) and revision r1; `tests/test_mbs308_qualify.py`'s
  QS-MUTANTS check expects the declared matrix to contain exactly M01-M57 and MQ01-MQ34 (91, later additions allowed).
* `tests/test_mbs308_mutants.py`: MQ01-MQ34 appended after M57; M01-M57 (including builder3's re-targeted M11 / M15
  and new M53-M57) unchanged. Protocol: sections 11.1-11.3 inserted before section 12 (builder3's section 4 text
  untouched). BUILD_REPORT: this section after builder3's section 14.
* No helper is pinned by the driver for the new files (HELPER_SHA256 still covers the four lifecycle helpers), so the
  driver, its pin table and DRIVER_DIFF.md are unchanged by the integration. The manifest writer lists the new files as
  frozen namespace files (Q8-S).

### 15.3 Results

**Scratch (brief 46; copy of b0dd8e93).** `tests/test_mbs308_qualify.py` 22/22 PASS; MQ01-MQ34 34/34 KILLED, every
kill by assertion (unmutated targets 16/16); 9 static checks in a sparse sandbox 9/9.

**Integrated tree (brief 49; 216c465f + the integration; builder4's own `--no-local` base store; every sandbox a
`--shared` clone of it; reports in builder4's scratch).**

| suite | result |
|---|---|
| `tests/test_mbs308_static.py` | 10/10 PASS (including `t_fault_hook_test_only`, full sandbox) |
| `tests/test_mbs308_launch.py` | 10/10 PASS (synthetic payload; every job booted out; no plist left) |
| `tests/test_mbs308_state.py` | 46/46 PASS |
| `tests/test_mbs308_crash.py` | 50/50 PASS on the re-run (see the note) |
| `tests/test_mbs308_qualify.py` | 22/22 PASS (declared matrix 91; 12 governance records; sparse sandbox: 25 frozen files, 49 external files, 5 commit pins; QC12-S 70 patterns, 26 files, 0 hits; QC13-S fails on exactly the two un-named records, passes once they are named) |
| `tests/test_mbs308_mutants.py`, full matrix | **91/91 KILLED, every kill by the target's own assertion** (no error, timeout, invalid mutant or missing result); unmutated code passes all 67 target runs; 5 chunks of at most 20 (M01-M20, M21-M40, M41-M57 + MQ01-MQ03, MQ04-MQ23, MQ24-MQ34), `sbx` sandboxes deleted after every chunk, every result JSON kept; free disk checked before each chunk (>= 112 GiB throughout) |

* **Crash-suite note (environmental, recorded).** The first crash run (from 13:58Z) lost its last 12 tests (L02-L13)
  when the host entered clamshell sleep on battery at 14:07Z (`pmset -g log`): the synthetic executions then refused
  with HOST_NOT_ON_AC, and the rest ran during dark wakes. The host was back on AC by 14:28Z; the whole suite was re-run
  on AC and passed 50/50. No mutant chunk started unless the host read AC power, and `pmset -g log` shows no sleep and
  no battery event during the matrix (14:44Z-15:30Z).
* `tests/test_mbs308_decoy.py` was not run: it computes with the real science on decoy cells, which briefs 46 and 49
  exclude (brief 49 lists static, launch, state, crash and qualify).

### 15.4 Open questions (for the coordinator / a reviewer; none decided here)

1. **Sequencing** (protocol 11.2): the R-rules and MBS-8 option (ii) take official decoy runs as inputs while the frozen
   code must already carry the values; options (a)-(d) are stated there.
2. **R-MEM's D and g**: the driver's decoy record carries per-job `ru_maxrss` and the run's watchdog peak, but not the
   driver's own peak RSS and no <= 0.5 s growth sampler; the measurement harness (pending) must provide them.
3. **Readings of the rule text** READING-1 ... READING-5 (protocol 11.3), e.g. per-run peaks in R-MEM step 3, AC as part
   of a valid prepared-state reading: for the ratifier or a reviewer to confirm.
4. **QC13-S record table**: every commit and path came from the register, the decision brief, brief 49 and
   `git diff-tree` names. The expected token `EXECUTION_ACCEPTED` for MB r1's execution review (a40211cc) is inferred
   from the register's "S14 met"; builder4 never read those files (MBS-2), and the verifier reads their line 2 at run
   time (a mismatch fails closed). Only LIVENESS_DELTA_ACCEPTED was checked (status only, OK). The implementation-review
   and freeze-decision records must be named at the freeze preparation.
5. **QC11-S named exception**: QS-STATIC's `t_mbs12_static_carryovers` names the research reconstruction file in order
   to assert its absence elsewhere; QC11-S exempts exactly the occurrences inside that function. Building that string
   at run time in the static test would remove the exception (not builder4's file to change).
6. **Host**: an official QS run needs several GB under `--work` (the crash, state and static sandboxes held about 2.5 GB
   together here) and must keep the host on AC and awake: a lid close on battery invalidates the suites that execute
   the synthetic lifecycle (see the crash-suite note).

### 15.5 Exposure statement (MBS-2; T6 ruling M4)

builder4 held no MB r1 run observation at the start. Two items reached its context, disclosed plainly:
(i) the session's auto-loaded memory index (written earlier by a holder) states MB r1's recorded outcome
(CELL308_EXECUTION_INDETERMINATE, consumed, not rerun) and qualitative lessons; the memory files themselves were not
opened; (ii) a `git log -1 --format='%H %s' 21e99cf0` displayed the one-line subject of MB r1's postexec commit, which
carries a qualitative chronology with clock times (no per-job, runtime, memory, host or science figure). Neither is
repeated or used anywhere in this build: every number in the rule functions is the ratification's, every other value is
a planted test value, and the case table comes from the briefs, the register and the ratification. MB r1's protocol
section 3.2 (pre-freeze decoy costs, not an observation of the consumed run) and the ratification's evidence Q (MB r1's
pre-grant qualification decoy resources) were read as listed above. Nothing new of this kind reached builder4 during the
integration.

Ledger (agent `builder4`, via `c308_quarantine.log_event`, target_evaluations 0 on every line): INFRASTRUCTURE
2026-09-30T07:08:57Z (scratch and base store); SYNTHETIC_VALIDATION 08:22:12Z (scratch test runs);
SYNTHETIC_VALIDATION 08:32:01Z (scratch MQ matrix); SYNTHETIC_VALIDATION 08:45:25Z (final scratch run);
INFRASTRUCTURE 14:33:19Z (brief 49 integration edits); SYNTHETIC_VALIDATION 15:31:49Z (brief 49 suites and the full
matrix).

## 16. Disk-safety and scratch-lifecycle gate, liveness robustness, re-pin tooling, R-MEM inputs, QS-RESUME-DECOY, host readiness (non-holder builder5, research brief 50 at b71cb9ea; NOT frozen)

**Scope.** Brief 50 only, target-free, on successor cc723527 (builder4's integrated framework). Nothing here
authorises a freeze, a qualification run or any target step. **New cell-308 target evaluations: 0.** No cell 305-309,
no drift in [6/5, 13/5] or its mirror; cell 309 untouched; the only science run is the dev decoy on cell 297 block 0
(ledgered NONTARGET_DRIFT_VALIDATION). No authorization, grant, marker, pending result, seal, freeze manifest in the
worktree or official qualification run; no system setting changed; no git write (everything is left in the worktree
for the coordinator). **No ratified operational number changed**: the one new number, QUAL_MIN_FREE_BYTES (7 GiB), is
derived below from measurements; the execution threshold stays the ratified 2 GiB (no amendment proposed).

**Read.** Brief 50 (as sent); the protocol draft in full; this report's sections 1-5, 7, 8 and 10-15 (sections 6 and 9
not opened: a `grep '^## '` of the headings only); research `ledger/enospc_2026-09-30/ENOSPC_AUDIT.md` and the first 30
lines of its deletion list; `governance/CONSTANTS_RATIFICATION_MBS308.md` (3c2a7854) in full;
`reviews/REVIEW_OPTIONB_LIVENESS_MBS308.md` (2308651e): its reading/exposure paragraph, sections 4 and "Findings outside
the delta", the re-run table and the verdict; `governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` section A only (for the
MBS-7 / MBS-8 options); `code/c308_quarantine.py`'s `log_event` and the ledger's last lines (format); the successor's
code, tests and config; MB r1's `mb308_driver.py` at c46434a3 only through the generator (`git show` of the file's
bytes). **Not opened:** any MBS-2 file (REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*,
REVIEW_SUCCESSOR_GOVERNANCE_308*, INCIDENT_INDEPENDENCE_REVIEW_MBS308* incl. T6, COORDINATOR_EXPOSURE_DISCLOSURE*),
research `governance/SUCCESSOR_GOVERNANCE_308.md`, anything under `p5y_k5_cell308_mb_r1/{review,adjudication,postexec,
evidence}/`, any other session's or agent's scratchpad, anything under `/Users/suzhe/.claude/`. No `git log` was run in
the successor worktree or on MB r1's branch.

### 16.1 Built

| file | sha256 (prefix) | role |
|---|---|---|
| `code/mbs308_scratch.py` | `cb69ac682a54c34e…` | NEW: the disk-safety and scratch-lifecycle gate (probe, lifecycle, classes, cleanup, run_gated, meter; QUAL_MIN_FREE_BYTES) |
| `code/mbs308_repin.py` | `5b955784c083c7c0…` | NEW: re-pin tooling (helpers, platform, the validated DRIVER_DIFF.md generator); dry-run by default |
| `code/mbs308_host.py` | `6650ceebd7297dd4…` | O-1 (UTC start time), O-4 (`(name)` is a failed reading); pinned helper |
| `code/mbs308_state.py` | `e2b6b8e1bb35c295…` | O-2 (staged + linked lock record), O-3 (one name after a put-back; `lock_read`), RssSampler (task 3); pinned helper |
| `code/mbs308_driver.py` | `66b6cfd68e76f988…` | main()'s decoy branch records R-MEM's D, the 0.5 s sampler and the run configuration; helper pins re-pinned |
| `code/mbs308_qualify.py` | `b93e12ffaae692ce…` | disk gate at the start and before each heavy phase; per-phase cleanup; QS-DISK; QS-RESUME-DECOY BUILT; --host-report |
| `config/MBS308_QUALIFICATION_CASES.json` | `9afe0840fd8db207…` | r2: QS-DISK, QS-RESUME-DECOY BUILT, builder5 among the ledger agents |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | `45cb343a581dbab1…` | s4 robustness paragraph; s8.1 checklist; s8.2 disk gate and thresholds; s11 cases, READING-6 |
| `DRIVER_DIFF.md` | `27d395f498d0fd7e…` | regenerated by the tool (22 hunks; classes carried) |
| `tests/test_mbs308_disk.py` | `488dd783ec52acff…` | NEW suite QS-DISK (17 tests) |
| `tests/mbs308_resume_decoy.py` | `d4ffabc8e7b50ddc…` | NEW: QS-RESUME-DECOY case runner (official / dev forms; value-free record) |
| `tests/test_mbs308_mutants.py` | `7ee0956449464217…` | per-mutant cleanup, disk gate (run_gated), meter; + M58-M66, MD01-MD27, MR01-MR04, MM01-MM03, MQ35-MQ36 |
| `tests/mbs308_testlib.py` | `ec2aec9496239814…` | lifecycle records for every suite process (the namespace's own scratch module, private name) |
| `tests/test_mbs308_launch.py` | `6ce0cc744c64c62f…` | K-1 cases; t_identity_state_time_zone_independent (O-1); t_identity_command_unreadable_unknown (O-4) |
| `tests/test_mbs308_state.py` | `a0fafd4080e74325…` | O-2 / O-3 lock tests; t_decoy_records_rmem_inputs (task 3) |
| `tests/test_mbs308_qualify.py` | `96c1baaab4bfe6cc…` | t_qs_resume_decoy_summary |
| `tests/test_mbs308_decoy.py` | `4f4857727f8c16a5…` | t_qs_resume_decoy_dev (the case runner's dev form) |
| `tests/mbs308_child.py` | `65c0683c1568d442…` | decoy-ckpt parametrised (cell, workers, first_blocks, dev_ladder); decoy-main-synth |
| `tests/mbs308_synth.py` | `29c0f02c7574d8ef…` | synth_decoy; host_texts knob (the real start gates on planted readings) |

### 16.2 Task 0: liveness robustness (reviewB5's O-1..O-4, K-1); no number changed

* **O-1 (required) REPAIRED.** `mbs308_host.process_start` now reads `ps -o lstart=` through `_run_ps`, whose
  environment fixes `TZ=UTC0` (a POSIX zone: no tz database, no DST). The recorded start time and every later reading
  come from the same function, so both are UTC whatever the system zone or the caller's TZ; `identity`, `identity_state`,
  `identity_alive`, the pidfile, the lock, the journal identity and the launcher's record all use it. Every
  positive-evidence property is kept (a failed reading is still None, UNKNOWN; nothing else in `identity_state`
  changed). Test `launch::t_identity_state_time_zone_independent`: a live helper's identity RECORDED under one planted
  zone and CHECKED under another (planted through the environment `ps` inherits its zone from, `mbs308_host.ENV`, as a
  system-zone change would act); a non-vacuous control shows that a raw `ps -o lstart=` prints two different strings
  under the two zones; with the repair the state stays ALIVE (and `identity_alive` true), DEAD once the helper is gone.
  Mutant M62 (the zone override removed) is killed (ALIVE -> DEAD, reviewB5's probe outcome).
* **O-2 REPAIRED.** `Lock.acquire` writes and fsyncs its record under a private staged name
  (`recover.lock.staged-<pid>-<nonce>`) and LINKS it to the lock name (`link(2)` fails when the name exists: O_EXCL
  semantics); the staged name is unlinked (directory fsync) whether the lock was taken or not. The lock name therefore
  never exists without its complete record. Test `state::t_lock_record_complete_before_name`: every write of acquirer A
  is intercepted (the module's own `_write_all`); whenever the lock NAME exists during A's writes, a second acquirer B
  runs at that very moment. Required: the name is never seen empty or partial, exactly one of A and B holds the lock,
  nothing is set aside as stale, no staged file is left. Mutant M64 (the old O_EXCL-create-then-write restored) is
  killed: B breaks A's empty lock and both hold it.
* **O-3 REPAIRED.** After a LOCK_RACE put-back (`link(aside, lock)`), the set-aside name is unlinked, so the lock keeps
  ONE name and its owner can release it. A new reader `lock_read` (O_NOFOLLOW, a regular file owned by this user, any
  link count) is used for the lock by `acquire`, `release` and `git_lock_info`, so a crash inside either two-name window
  (acquire's link -> unlink, the put-back's link -> unlink) cannot wedge later acquires. Tests
  `state::t_lock_race_put_back_one_name` (a second breaker takes the lock between A's read and A's rename, planted by
  intercepting A's rename: A refuses LOCK_RACE, the lock holds B's bytes with link count 1, only B's set-aside copy of
  the stale lock remains, byte for byte, B's release removes the lock, a later acquire takes it) and
  `state::t_lock_second_name_not_wedged` (a two-name lock of a dead holder is broken once and taken; of a live holder is
  LOCKED, intact). Mutants M65 (the unlink after the put-back removed) and M66 (`lock_read` requires one link) killed.
* **K-1 ADDED.** `launch::t_identity_state_positive_evidence` now also plants a failed boot-UUID read ALONE and a failed
  command read ALONE (the start-time read still works) and requires UNKNOWN. My own equivalents of reviewB5's Y5 / Y6
  (their exact bytes are in reviewB5's scratch, which I did not read): M58 / M59 (boot read failure -> DEAD; the check
  removed) and M60 / M61 (command read failure -> DEAD; the check removed), all killed.
* **O-4 REPAIRED.** `process_command_sha256` treats an output of the form `(name)` (whole reading in parentheses) as a
  failed reading (None): never recorded, never compared (N-2), UNKNOWN. A zombie's `<defunct>` (probed: exit 0,
  `<defunct>`) and a real command that merely contains parentheses (`/usr/libexec/UserEventAgent (System)`) stay
  readings. This also protects the launcher, which records the job's identity right after launchd reports its pid, that
  is 0-1 s from exec. Test `launch::t_identity_command_unreadable_unknown`; mutant M63 killed.
* Protocol section 4: a paragraph "Robustness of the readings and of the lock" states the five points. N-B1 and D-1
  (optional) were not taken.

### 16.3 Task 1: the disk-safety and scratch-lifecycle gate

* **`code/mbs308_scratch.py`** (test / qualification infrastructure; the driver never imports it): the free-space probe
  and `check_free` / `require_free` (fail closed; a test may plant a reading that can only lower or fail the real one);
  the lifecycle records; the three classes; `cleanup` (dry-run default); `run_gated` (the heavy-phase runner the verifier
  and the mutant runner share); `TreeMeter` / `measure` (the threshold inputs); CLI `free | status | cleanup |
  measure`. Its host module is loaded under a private name, never as `mbs308_host`, so loading it never substitutes a
  host copy for the one a test or a mutant imports. The rules are protocol section 8.2 (verbatim there).
* **Wiring.** The test library writes an ACTIVE record for every suite process in its scratch root and FINISHED at the
  end. The mutant runner: `run_matrix` through `run_gated`: the disk check (QUAL_MIN_FREE_BYTES on its scratch volume)
  before the start and before every target run (a failure stops: nothing more runs; `not_run`, `disk_refusal` in the
  report; exit 1); each phase writes its own record around the target run and, once the result file is written and
  VERIFIED (it parses and carries the test's boolean `ok`), deletes that phase's sandboxes through `cleanup`; a
  `TreeMeter` records the matrix's peak scratch. The verifier: the disk check (QUAL_MIN_FREE_BYTES on `--work`,
  MIN_FREE_DISK on the repository volume) in every mode right after the argument checks, before the preconditions and
  before anything is written (`QUALIFY REFUSED: DISK`); its own record in its work directory; the heavy phases (the six
  suites, QS-MUTANTS, QS-RESUME-DECOY) through `run_gated` with the same check before each and the suites' scratch
  cleaned after each verified record; a phase not run is `DISK_REFUSED` (pass false); the report carries `disk`
  (thresholds, the start check, every check, every cleanup, the refusal).
* **(d) The driver's `free_disk` gate already failed closed** (`free_disk_bytes` returns None on OSError; the gate
  requires an int >= MIN_FREE_DISK); nothing to fix; now tested at the gate and end to end. **Found in passing, not
  changed (outside the brief's disk scope, for the reviewer):** `mbs308_driver.busy_processes` reads a FAILED `ps`
  (`HOST._run` returns None) as "no busy process", so the exclusivity start gate fails OPEN on a failed reading; a
  fail-closed fix would be `host_exclusive = text is not None and not busy` (no number).
* **Tests** (`tests/test_mbs308_disk.py`, suite QS-DISK, gate Q12) and mutants, each killed by the target's assertion:

| property (brief 50, 1 f) | test | mutants |
|---|---|---|
| a probe failure never reads as sufficient space | `t_free_probe_fails_closed`, `t_driver_disk_gate_fails_closed` | MD01, MD02, MD04, MD05, MD06 |
| insufficient disk fails closed before irreversible work: the driver's execute and resume preflight | `t_execute_resume_refuse_on_disk` (real gates on planted readings; no ref, no spool result, no seal; the attempt counter unmoved; controls seal) | MD03 |
| ... the verifier's official start (and dev) | `t_verifier_disk_gate` (nothing written, before the preconditions) | MD26 |
| ... the mutant runner's start | `t_mutant_runner_disk_gate_and_cleanup` (the real runner, planted reading) | (runner code in tests/: exercised end to end) |
| before each heavy phase | `t_run_gated_phases`, `t_verifier_heavy_phase_gated_and_cleaned` | MD22, MD23, MD24, MD25 |
| cleanup cannot target active scratch | `t_lifecycle_classes`, `t_cleanup_refuses_active_scratch` | MD07, MD08, MD09, MD14, MD15 |
| cannot target evidence (JSON, reports, ledgers, manifests, verdicts) | `t_cleanup_only_disposable` (every other file byte-identical; look-alikes kept; dry-run deletes nothing) | MD10, MD11, MD12, MD13 |
| symlinks / escape from the root | `t_cleanup_symlinks_and_escape` | MD16, MD17, MD18 |
| cannot target refs, the marker, pending, spool, seals, worktrees | `t_cleanup_never_touches_repository` (a planted repository; the real one read-only, dry-run, refused before any walk) | MD19, MD20, MD21 |
| the per-mutant cleanup works and keeps the peak small | `t_mutant_runner_disk_gate_and_cleanup` (M11 through the real runner: both phases' sandboxes deleted after their verified results) | - |
| the thresholds are the derivation, in code and protocol alike | `t_thresholds_derived` | MD27 |

### 16.4 Thresholds (protocol section 8.2 is the binding text)

Inputs measured target-free on this host, 2026-09-30 (peak allocated bytes of each run's scratch tree, sampled every 2
s by `mbs308_scratch.py measure`; base store outside the trees):

| input | measured |
|---|---|
| one sandbox: a `--shared` clone checked out at 21e99cf0 (9185 files) with its `.git` | 0.835 GiB (the runner's per-phase deletions: 0.835 GiB each) |
| the base store (`git clone --bare --no-local` of the repository, 2026-09-30) | 458.4 MiB (0.448 GiB); grows with the repository |
| QS-STATIC / QS-LAUNCH / QS-QUALIFY | 0.835 / 0.001 / 0.007 GiB |
| QS-STATE / QS-CRASH | 0.844 / 0.850 GiB |
| **QS-DISK (P_max)**: its own full sandbox, plus a nested verifier with its own base store and a full sandbox | **2.119 GiB** |
| one mutant phase (the real runner, `--only M11`, per-mutant cleanup) | 0.836 GiB |
| QS-RESUME-DECOY, dev form (one sandbox; decoy outputs MB-scale) | 0.835 GiB |
| a synthetic sealed run (18 checkpoints, journal, pending, seal): git-dir growth / spool; sealed record | 0.27 MB (0.29 MB after an F3 crash + resume) / 33-37 KB; 25 KB |
| real-science scale (dev decoy 297 block 0): 4 checkpoint blobs / its Stage-1 record / the whole decoy output | 39 KB / 54 KB / 131 KB |
| MB r1's full 5-block decoy record (ratification evidence Q) | 1.6 MB |
| macOS swap growth (ratification item 23) | 1 GiB swapfile steps |

**QUAL_MIN_FREE_BYTES = roundup_GiB(2 × (P_max + B) + 1 GiB) = roundup_GiB(2 × (2171 + 459) MiB + 1 GiB) = 7 GiB**
(P_max: QS-DISK's peak, the heaviest heavy phase; B: the verifier's persisting base store; 1 GiB: item 23's swap step;
factor 2: the written margin for the base store's growth with the repository, run-to-run variation, the phase's records
and other host activity until the phase ends). **MIN_FREE_DISK (2 GiB) checked, no amendment**: the execution's own
writes are MB-scale (a synthetic sealed run < 0.3 MB of git dir and < 40 KB of spool; at real scale < 15 MB for four
attempts, < 150 MB for a record ten times a decoy's), so 2 GiB = one swap step + > 6 × the generous bound. The
ENOSPC-type risk during an execution is other processes filling the volume; the checklist (8.1) makes "no concurrent
sandbox-heavy work from the marker to the seal" a recorded user / coordinator action. Nothing here is PENDING_USER_DECISION:
the heaviest phase (QS-DISK) and the per-case sizes (one sandbox) are the same under MBS-7 / MBS-8; the official
decoy cases of QC02 / QC03 (pending) each hold one sandbox, like QS-RESUME-DECOY, so they are within P_max.

### 16.5 Task 2: re-pin tooling (`code/mbs308_repin.py`; dry-run by default; never imports the driver)

* `helpers`: HELPER_SHA256 recomputed mechanically; `--write` rewrites exactly the stale `"name": "sha"` pairs inside
  the table's own source segment (every other byte unchanged; re-parsed and checked).
* `platform`: the readings the driver's `platform_readings()` takes (same commands, same host helper, this interpreter)
  against PLATFORM_PINS; `--write-platform` (and only that flag) rewrites the differing pins, refused when a reading
  fails. **PLATFORM_PINS were NOT re-pinned** (they equal this host's readings anyway).
* `driver-diff`: the DRIVER_DIFF.md generator (difflib.SequenceMatcher(autojunk=False), 3 lines of context, unified hunk
  headers, touched top-level definitions from the AST line ranges of the changed lines of both files, classes and header
  text carried). It FIRST regenerates the committed DRIVER_DIFF.md from the committed driver (HEAD cc723527) and
  requires byte equality (else GENERATOR_NOT_VALIDATED); it did reproduce it byte for byte on its first run. Classes are
  carried from the committed hunk with the same touched set (i-th to i-th); a hunk without a counterpart needs
  `--classes`; a hunk touching a carried definition is SCIENCE-GLUE (MUST NOT OCCUR) and fails. For this build: 22
  hunks, all carried (my decoy-branch change falls in hunk 21, `main`, LIFECYCLE; hunk 4 carries the new helper pins).
* Tests `disk::t_repin_helpers_and_platform`, `disk::t_repin_driver_diff` (copies and a sandbox; the real repository
  read only); mutants MR01-MR04 killed.

### 16.6 Tasks 3 and 4: R-MEM inputs and QS-RESUME-DECOY

* **R-MEM inputs (task 3).** In `main()`'s decoy branch only (no carried function changed; RC1 / MBS-9 static tests
  pass): `lifecycle.driver_maxrss_bytes` (ru_maxrss of RUSAGE_SELF: R-MEM's D), `lifecycle.rss_sampler` (new
  `mbs308_state.RssSampler`: a fixed-rate 0.5 s `ps -A -o pid=,ppid=,rss=` reading of the driver and its descendants:
  samples, failed reads, largest spacing, driver and worker peaks, `max_growth_bytes_per_s`: step 6's g) and
  `lifecycle.rmem_run` (workers, ladder, mem_cap_bytes, mem_poll_s, first_blocks, launched_by_launchd: step 1).
  Recorded fields only (a daemon thread reading `ps`; it never signals and never touches the computation). Test
  `state::t_decoy_records_rmem_inputs`: main()'s real decoy branch in a sandbox child with the SYNTHETIC evaluator
  standing in for `decoy()` (MB r1's unchanged stage1 over fake jobs, 64 MB held 1 s each): D = 51.4 MiB, 21 readings, 0 failed, largest spacing 0.505 s, driver peak 51.2 MiB, worker peak 97.5 MiB, g = 192.2 MiB/s; the record
  passes R-MEM step 1's field checks except exactly this synthetic run's own `NOT_UNDER_LAUNCHD_LAUNCHER`,
  `WORKERS_NOT_5`. Mutants MM01-MM03 killed. On real (decoy) science, the dev decoy's record: D = 57.7 MiB; 299 readings, 0 failed, largest spacing 0.51 s, driver peak 57.5 MiB, worker peak 82.3 MiB, g = 61.9 MiB/s. The
  spacing can exceed 0.5 s by the scheduling jitter: READING-6 (protocol 11.3) leaves "nominal or observed" to the
  ratifier; no other interval was chosen. Re-pinned; DRIVER_DIFF.md regenerated (hunk 21).
* **QS-RESUME-DECOY (task 4): BUILT.** I agree it is decision-independent: its definition compares a decoy run of the
  FROZEN driver with the same run SIGKILLed and resumed, and my implementation reads the job set, n, k = n // 2 and the
  output keys from the runs (nothing hard-coded about the science; the comparison covers every key of the decoy output
  except named provenance keys, timing stripped at every depth), so it is the same case under MBS-7 (i) and (ii) (under
  (ii) the added members' jobs are simply more jobs); only its RESULT depends on the frozen code, and the official form
  runs only in the official qualification (its record is value-free). MBS-8 changes only the caps the runs carry (a cap hit fails the case, fail closed, under either option), and the case feeds no constant, so the sequencing question of protocol 11.2 does not reach it. The one maintenance dependency: if option (ii) changed the signature of the carried `decoy()`, the child harness's call (`tests/mbs308_child.py` decoy-ckpt) would need the same change; the case's definition would not.
  Case runner `tests/mbs308_resume_decoy.py` (official: 297, every block, the frozen ladder, WORKERS, timeout
  DECOY_CAP_S, both read from the driver's text; dev: 297 block 0, dev ladder, 2 workers); verifier case (official /
  review --heavy: official form; --dev: dev form, never evidence: the summary passes only an official-form record);
  config status BUILT; protocol 11 updated. Tests `decoy::t_qs_resume_decoy_dev` (NONTARGET_DRIFT_VALIDATION) and
  `qualify::t_qs_resume_decoy_summary`; mutants MQ35, MQ36 killed. Dev result: PASS: n = 4 jobs, k = 2, SIGKILL (signal 9) after 2 checkpoints (C1B.0.4, C2B.0.20), resumed: served 2, computed 2, rejected 0; Stage 1 (643 leaves) and the five Stage-2 decoy bundles (883 leaves) equal, 1548 certified leaves in all, canonical bytes equal; host assessment of the uninterrupted run CLEAN. MBR1_REPRO, QC01-QC08,
  Q12_caps and R_RULES_OFFICIAL are untouched (still PENDING_USER_DECISION).

### 16.7 Task 5: host readiness

Protocol section 8.1: a checklist of what must hold before the official qualification and before any execution (update
installation disabled: user action; automatic restart: recorded; AC; sleep prevention and the lid: caffeinate cannot
stop lid-close sleep, user action; thermal 0; low-power 0; the disk thresholds; memory pressure and free memory; boot
identity; platform pins (re-pinned at the freeze with the repin tool); exclusivity; no other campaign job; no concurrent
sandbox-heavy work), each with how it is checked. A READ-ONLY report: `code/mbs308_qualify.py --host-report [--work
DIR] [--out FILE]` (queries only; `read_only` true, `changes_made` false); test `disk::t_verifier_host_report_read_only`
(every item present, the settings it reads unchanged after it ran, its own code holds only the two query command
vectors `pmset -g` and `ioreg -r` and no write call, refused with another mode). The report is not a gate (no mutant).
Tonight's reading on this host: 9 of 14 items READY or RECORDED; not ready: automatic_os_installation_disabled (USER_ACTION), free_memory (NOT_READY), host_exclusive (USER_ACTION), memory_pressure_normal (NOT_READY), thermal_level_0 (NOT_READY) — this host needs the user's preparation before an official run.

### 16.8 Results on the final code (own `--no-local` base store; sandboxes only; on AC throughout)

Run of 2026-10-01 11:15-12:35Z, after the resumption, on the final bytes; AC power throughout and no Sleep / Wake / DarkWake entry of the power log in the window; >= 113 GiB free.

| run | result | peak scratch | wall |
|---|---|---|---|
| `tests/test_mbs308_static.py` | **10/10 PASS** | 0.835 GiB | 6 s |
| `tests/test_mbs308_launch.py` | **12/12 PASS** | 0.001 GiB | 17 s |
| `tests/test_mbs308_qualify.py` | **23/23 PASS** | 0.007 GiB | 22 s |
| `tests/test_mbs308_disk.py` | **17/17 PASS** | 2.119 GiB | 143 s |
| `tests/test_mbs308_state.py` | **50/50 PASS** | 0.844 GiB | 400 s |
| `tests/test_mbs308_crash.py` | **50/50 PASS** | 0.850 GiB | 837 s |
| `tests/test_mbs308_decoy.py t_qs_resume_decoy_dev` (dev decoy 297 block 0) | **PASS** | 0.835 GiB | 336 s |
| `tests/test_mbs308_mutants.py`, the full matrix, ONE run, per-mutant cleanup | **136/136 KILLED, 136 by the target's own assertion**; unmutated 87/87 target runs PASS | **0.907 GiB** | 3018 s |

Matrix (M01-M66, MQ01-MQ36, MD01-MD27, MR01-MR04, MM01-MM03): no survivor, none not run, no error, timeout, invalid mutant or missing result (every kill: `test_passed` false, no `error`, exit code 1, result file verified); 224 disk checks (the start and every phase), all passing against 7 GiB; every one of the 223 phases was cleaned after its verified result: 140 sandboxes deleted, 95.2 GiB in total, while the tree never held more than 0.907 GiB (about 40 GB per full run before this gate, ENOSPC audit). The only units the cleanup refused were the disk suite's own PLANTED roots (reasons ['ROOT_ACTIVE']), which is the gate working. M33 was killed by its deterministic run (158.3 s for its target).

**Earlier runs are PRE-FINAL and superseded, disclosed.** (i) 2026-09-30 17:22-18:37Z: every suite passed and the matrix gave 136/136 killed with all 87 unmutated targets passing, but MD11 was killed by an EXCEPTION, not by the assertion: under the mutant, `cleanup` read the alternates file of the planted non-clone `sbx` that the mutant had admitted and raised FileNotFoundError. `cleanup` now treats an unreadable alternates file as no recorded borrower (a defensive read; no rule and no number changed); MD10-MD13 were re-checked alone (all by assertion). (ii) 2026-09-30 18:40-19:50Z: a full re-run on those bytes completed, but my session was cut off by an API connection error while it ran and resumed about 16 hours later; on the coordinator's instruction every run made before the resumption is PRE-FINAL. The table above is the run made AFTER the resumption on the final bytes (code, tests, config and protocol unchanged since before run (ii); after it only this section's result figures were filled in, and `tests/test_mbs308_qualify.py`, whose leak scan reads this file, was run once more: qualify 23/23 PASS, static 10/10 PASS; both were run once more after this sentence itself was written, and that last result is in builder5's handback). The pre-final reports stay in builder5's scratch.

### 16.9 For the reviewer (none decided here)

1. `busy_processes` fails OPEN on a failed `ps` (16.3 (d)); a one-line fail-closed fix is proposed, not applied.
2. READING-6: the 0.5 s sampler's nominal interval vs its observed spacing (up to 0.555 (largest over all runs; 0.51 in the final run) s).
3. QUAL_MIN_FREE_BYTES is not in the freeze manifest's recorded constants (the manifest writer was not changed); Q8-S
   covers `code/mbs308_scratch.py` by hash.
4. Roots made before this gate have no lifecycle record and stay ACTIVE for the tool (by design; deleted by hand).
5. The O-2 staged file of a process killed between its staging and its link remains in the spool (never read; harmless).
6. O-4 reads a whole-output `(...)` as a failed reading; a real process whose command line itself is parenthesised would
   read UNKNOWN (fail closed), never DEAD.

### 16.10 Integrity, ledger, exposure

* **New cell-308 target evaluations: 0.** Every state-changing run used the synthetic evaluator (or the synthetic
  launchd payload) in sandboxes cloned `--shared` from builder5's own `git clone --bare --no-local` base store; the only
  science was the dev decoy on cell 297 block 0 (four runs of `t_qs_resume_decoy_dev`: three pre-final and the final
  one, each uninterrupted + killed + resumed; the second pre-final one is covered by the "final run 2" ledger line); its decoy values stay in builder5's scratch and are never juxtaposed with any
  tail-cell number. The real driver ran only the launch suite's read-only `preflight` and, in sandbox copies,
  `status` / `decoy`. Cells 305-309, any drift in [6/5, 13/5] or its mirror, and cell 309's campaign were not touched.
* Real repository (read-only checks at the end): the 144 refs equal my snapshot at the start except the research
  branch head, which moved during my build by someone else's commit (two new review files; I did not open them); no ref
  under `refs/p5y-k5-cell308-mbs-r1/`; MB r1's marker still names afa93072; no `mbs308-spool` in the real git dirs; no
  `packed-refs.lock`. No git write of mine anywhere. No system setting changed; no caffeinate spawned outside the
  tests' own sandboxes and launch jobs; the launch suite's transient LaunchAgents (synthetic payload, test prefix) were
  booted out by their teardowns: `launchctl list` shows no rebaseguard job and no plist is left.
* Disk: every heavy run was preceded by an AC and free-space check (>= 112 GiB free throughout); my sandboxes were
  deleted after each run with the new tool (`cleanup --execute` on my own finished roots; the planted ACTIVE test roots,
  which the tool refuses by design, by hand); the base store and the JSON reports stay in my scratch.
* Ledger (agent `builder5`, `c308_quarantine.log_event`, target_evaluations 0, no LEAK_FLAG): INFRASTRUCTURE 2026-09-30T15:58:45Z; NONTARGET_DRIFT_VALIDATION 2026-09-30T16:50:05Z; SYNTHETIC_VALIDATION 2026-09-30T16:59:38Z; SYNTHETIC_VALIDATION 2026-09-30T17:22:50Z; SYNTHETIC_VALIDATION 2026-09-30T17:28:44Z; NONTARGET_DRIFT_VALIDATION 2026-09-30T17:28:44Z; SYNTHETIC_VALIDATION 2026-09-30T18:40:11Z; SYNTHETIC_VALIDATION 2026-10-01T11:15:16Z; NONTARGET_DRIFT_VALIDATION 2026-10-01T11:15:16Z; INFRASTRUCTURE 2026-10-01T12:37:02Z (10 lines).

**Exposure statement (builder5).** I read no MB r1 run record, review, adjudication, postexec or evidence file. What my
context holds about MB r1 that did not come from an allowed file: my session began with the user's auto-loaded memory
index (I opened none of its files). Its lines touching MB r1 are the outcome label of MB r1's one execution with the
successor's pre-freeze status (the label the allowed texts carry), a lesson line that host sleep and fanless thermal
slowdown inflate wall times (provenance unknown to me) and a successor-lessons line (packed-refs.lock, timing-dependent
kills, positive evidence for liveness) — the same lines builder3, builder4 and reviewB5 disclosed. At the resumption the
index was loaded again with those lines updated (the same outcome label; that owner decisions were recorded; the
lessons); the coordinator also told me that the user's owner decisions exist in two research ledger files, which I did
not open and did not act on (every PENDING_USER_DECISION case is unchanged except QS-RESUME-DECOY, section 16.6). None carries a
per-job, progress, CPU, memory, host or science figure; I repeat none of it and no value or edit here depends on it. No
commit subject of MB r1 was displayed (no `git log` was run). The ratification's evidence Q (MB r1's pre-grant
qualification decoy file size 1.6 MB, not an observation of the consumed run) is used in 16.4.


## 17. The decision-dependent cases, section 11.2 option (a), and the grant's owner records (non-holder builder6, research brief 54 at 5e425c27, with the coordinator's addition 54-A and owner supplement 2; NOT frozen)

**Scope.** Brief 54 (its recorded file, sha256 b0f2838c…, verified before anything else), the coordinator's addition
54-A (the second ratifier's readings, research ca66e367) and the user's owner supplement 2 (research 74f386a5),
target-free, on successor 555f4cbf (builder5's commit on builder4's framework). Three parts: (A) the qualification
cases that depended on the user's decisions, built under the recorded owner decisions MBS-6 (i), MBS-7 (i), MBS-8 (i);
(B) the user's section-11.2 ruling, option (a), with the ratifier's readings and the supplement-2 fail-closed
semantics; (C) the grant's binding of ALL the complete owner records (three), and the final-preflight mapping. The
work was interrupted once by a session usage limit and resumed on the same uncommitted bytes (17.10 says exactly what
was in before the interruption). Nothing
here freezes, measures officially, qualifies, authorises or grants anything. **New cell-308 target evaluations: 0.** No
cell 305-309 was evaluated, no drift in [6/5, 13/5] or its mirror was computed, cell 309 was not touched. The only
science run is decoy cover cell 297, block 0, at the development ladder (ledgered NONTARGET_DRIFT_VALIDATION). **The
STOP POINTS were kept: no full-length decoy, no designated measurement, no dress rehearsal and no apply step was run in
the worktree.** No authorization, grant, marker, pending result, seal or freeze manifest exists in the worktree; nothing
was written under `evidence_prefreeze/`; no system setting was changed; **no operational number was changed by hand**
(the five provisional rule constants and every cap are the committed values; the one number this build CHOSE is the
RSS sampler's configured interval, 0.5 s to 0.25 s, a recorded-field setting the ratifier and the owner left to the
builder and to the review: 17.4). No git write: every edit is left in the worktree for the coordinator.

**Read.** Brief 54 in full; this report's sections 1-5, 7, 8 and 10-16 (sections 6 and 9 NOT opened: a `grep '^#'` of
the headings only); the protocol draft's sections 8, 10 and 11 in full and the head of section 1;
`config/MBS308_QUALIFICATION_CASES.json`; `code/mbs308_qualify.py`, `mbs308_rrules.py`, `mbs308_repin.py`,
`mbs308_launch.py`, `mbs308_manifest.py` in full; `code/mbs308_driver.py`, `mbs308_host.py`, `mbs308_state.py`,
`mbs308_scratch.py` in the parts this section names; `tests/test_mbs308_qualify.py`, `mbs308_testlib.py`,
`mbs308_resume_decoy.py`, `test_mbs308_decoy.py`, `mbs308_child.py`, `mbs308_synth.py`, the mutant runner. The user's
rulings, every digest verified: `ledger/USER_RULING_MBS308_OWNER_DECISIONS.txt` (5c2394ba, sha256 34eb1d41…) sections
2-4, 10, 11, 13 and 14; `ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_1.txt` (8fc2b038, sha256 3f7d477b…) parts I and II;
`ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt` (74f386a5, sha256 4ba4a666…, from the file and from the git blob) in
full. The second ratifier's `governance/CONSTANTS_RATIFICATION_MBS308_READINGS_R1.md` (ca66e367, sha256 b638e1b3…,
verified): "Rulings at a glance", items 2, 4, 5 and 6 and the final table.
`reviews/REVIEW_SEQUENCING_DETERMINATION_MBS308.md` sections 1.2 and 2(a);
`reviews/REVIEW_OWNER_DECISION_CONFORMANCE_MBS308.md` sections 1.2 and 1.3;
`governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` lines 28-37 (the wording of the MBS-6 options);
`code/c308_quarantine.py`'s `log_event` and the ledger's last two lines (format). MB r1's frozen implementation
(read-only, in MB r1's worktree): `code/mb308_qualify.py` in full, the decoy branch of `code/mb308_driver.py`, the loader
functions of `code/mb308_pinned.py`, the ladders / jobs / run_job of `code/mb308_stage1.py`, `tests/test_mb308_guard.py`
in full and the entry functions of `test_mb308_twosided.py`, `_a0.py`, `_tptb.py`, protocol sections 3.2, 9 and 14, and
the KEY STRUCTURE (names and types only; no value printed) of the committed `qualification/` records with the pass flags
of `MB308_QUALIFICATION.json`. **Not opened:** any MBS-2 file (REVIEW_EXECUTION_INTERRUPTION*,
audit/EXECUTION_INTERRUPTION_*, REVIEW_SUCCESSOR_GOVERNANCE_308*, INCIDENT_INDEPENDENCE_REVIEW_MB308* and _MBS308*
including T6, COORDINATOR_EXPOSURE_DISCLOSURE*, USER_TEXTS_SUCCESSOR_308.md, governance/SUCCESSOR_GOVERNANCE_308.md,
history/), anything under MB r1's `review`, `adjudication`, `postexec` or `evidence` directories, any other session's or
agent's scratchpad, anything under `/Users/suzhe/.claude/`. No `git log` was run on any branch.

### 17.1 Built

| file | sha256 (prefix) | role |
|---|---|---|
| `code/mbs308_driver.py` | `e56d02d29042` | `S1_OWNER_RECORDS` (three records), `check_s1_ruling`, `s1_index_sha256`; the failed-decoy record of `main()`'s decoy branch (V16); comments on the five rule constants; `HELPER_SHA256` re-pinned for the state helper. No carried function, no cap, no rule constant changed |
| `code/mbs308_state.py` | `3793e0b111e8` | `RssSampler` only: configured interval 0.25 s; `max_spacing_ns` recorded (pinned helper) |
| `code/mbs308_rrules.py` | `54d13db2add7` | `r_mem`: the series parameters (cap, poll, `official`), F-6 as corrected, the re-run's step-5 bound, step 6's three cases; `sampler_reasons`; `cap_events`; the three fail-closed status names. No rule number changed |
| `code/mbs308_derive.py` | `821b481316ec` | NEW: the derivation tool, the adapters shared with the official qualification, `form_reasons` (canonical forms), `stop_statuses`, the exact comparison, the exact reader of a driver's constants |
| `code/mbs308_measure.py` | `28bcb581756b` | NEW: the designated pre-freeze measurement tool (B1) and the measurement functions the official qualification shares; the designation-rule proposal |
| `code/mbs308_repin.py` | `2cd8bb5cc4f9` | the `apply` subcommand (dry-run by default); canonical outputs only |
| `code/mbs308_manifest.py` | `033af87e5e48` | `s1_owner_records` bound and checked in git |
| `code/mbs308_qualify.py` | `202c2744a126` | the thirteen decision-dependent cases, Q12 on fixed caps, the section-4 values check, R_RULES_OFFICIAL, the fail-closed statuses (cases and aggregator), the planted R-rule controls, owner section 14, the qualified-worktree interlock |
| `config/MBS308_QUALIFICATION_CASES.json` | `4948f7bc89b2` | revision r4: every case BUILT with `decided_by`; the three owner records and the ratifier's readings named; `owner_decisions`; `official_decoys`; ledger agents |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | `e29d1076ed92` | the owner decisions; S1's three-record table; section 8 (caps, rule-output table, 8.3); section 10 (MBS-6); section 11 (cases BUILT; 11.2 the ruling chain, the rulings as implemented, the designation-rule proposal; 11.3 the readings) |
| `DRIVER_DIFF.md` | `421e3d50af3e` | regenerated by the validated generator (23 hunks) |
| `tests/test_mbs308_cases.py` | `923986079a18` | NEW suite QS-CASES (25 tests) |
| `tests/mbs308_decoy_payload.py` | `7fbcb6d9dcec` | NEW: the synthetic launchd payload (never the driver) |
| `tests/test_mbs308_state.py` | `faa519212831` | the three-record grant test (26 planted controls); the failed-decoy record test; value-agnostic start-gate and allow-list tests; the sampler fields |
| `tests/test_mbs308_qualify.py` | `eef716031884` | PENDING mechanism on planted cases; QC13-S with three planted owner records; the sparse sandbox |
| `tests/test_mbs308_static.py` | `b016b228c88d` | the allow-list test conditional on the table's status |
| `tests/test_mbs308_disk.py` | `d66d85b6ee7d` | value-agnostic planted free memory; the host report's scheduled power events |
| `tests/test_mbs308_decoy.py` | `cd4605897d25` | `t_science_cases_dev` |
| `tests/mbs308_testlib.py` | `554965ceee6c` | the owner-record helpers and `grant_chain(ruling=...)` |
| `tests/test_mbs308_mutants.py` | `28f895aad7bc` | 245 declared mutants (MB01-MB109 are this build's; M51 re-expressed) |
| `BUILD_REPORT.md` | (this file) | section 17 |

One helper changed: `code/mbs308_state.py` (`RssSampler` only: the configured interval 0.25 s and the recorded field
`max_spacing_ns`; no lifecycle function touched), so its entry of `HELPER_SHA256` was re-pinned with builder5's tool
(`mbs308_repin.py helpers --write`); guard, host and launch are unchanged. The driver changed in LIFECYCLE / IDENTITY
hunks only: the S1 check and its three rows, comments, and `main()`'s decoy branch, which now writes the run's record
also when the decoy FAILS (V16 below). `DRIVER_DIFF.md` was regenerated by builder5's validated generator: 23 hunks;
no hunk touches a carried definition; the two hunks without a committed counterpart were given their class by
`--classes` (hunk 9, the two new S1 functions: IDENTITY, the class the committed file gives the S1 check in
`check_grant`; hunk 11, the tail of `check_grant` merged with the persistence helpers: IDENTITY + LIFECYCLE). The class
names are the builder's proposal for the reviewer. Before the coordinator's commit `mbs308_repin.py check` refuses in
the worktree (`HUNK_WITHOUT_CLASS`: those two hunks have no committed counterpart yet) and `disk::t_repin_driver_diff`
fails there for the same reason; both pass on the committed bytes (17.7 ran every suite in a committed sandbox clone).

### 17.2 Part A: the decision-dependent cases

**A1 (MBS-6 (i)).** Protocol section 10: an INDETERMINATE-class outcome of MB-S is final for route MB on cell 308; no
further route-MB cell-308 evaluation is authorized after it (the decision brief's option (i) wording and the owner
record's); the earlier S7 sentence (a further successor through a further governance process) is replaced, there and in
the outcome table; the reach of MBS-7's "do not reopen the changed-science branch" is stated with owner supplement 1,
section 9. QC13-S: the configuration names the three owner records by path, commit and sha256 (`USER_FREEZE_DECISION`:
the original record: S16(c), MBS-6 / 7 / 8; `USER_OWNER_SUPPLEMENT_1`: the section-11.2 ruling and the S1 supplement;
`USER_OWNER_SUPPLEMENT_2`: the fail-closed semantics) and the second ratifier's readings
(`CONSTANTS_RATIFICATION_READINGS_R1`, presence and sha256: no verdict line is read). An
altered record (another sha256), a record missing at its commit, a record not named and a record off the research
branch each fail closed (planted controls through the same check, on the real research branch in the base store and end
to end in the sparse sandbox). `IMPLEMENTATION_REVIEW_ACCEPTED` is still un-named, so QC13-S still fails closed today.

**A2 (MBS-7 (i)): the science family, carried.** QC01, QC02, QC03, QC04, QC05, QC06, QC07, QC08, Q1_theory, QC09-SCI
and MBR1_REPRO (full form) are BUILT, each with `decided_by` = the owner record. MB r1's verifier functions are carried
in `code/mbs308_qualify.py` (`qc02_eval`, the QC03 criterion, `qc04_eval` with its views, comparison and planted-leaf
control, the serial / ladder / E4 / Monte-Carlo children, Q1, and Q12: `_decoy_jobs`, `lpt_makespan`, `_host_verdict`,
`_q12_core`, the fixture, `_synthetic_host`, `_synthetic_decoy`, the controls). MB r1's qualification TEST MODULES are
not copied: `load_mbr1_test` executes `tests/test_mb308_twosided.py`, `_a0.py`, `_tptb.py` and `_guard.py` from MB r1's
COMMITTED bytes at MB r1's paths (sha256 and blob at 21e99cf0, checked at HEAD) through MB r1's own pinned loader, as the
driver executes the science modules. MB r1's committed official r3 records, the Monte-Carlo module, the E4 controls, the
A0 evaluator, the five A0 certificates and both copies of the theorem are external pins of the manifest (Q8-S).
**QS-RESUME-DECOY** was already built by builder5; its definition is the MBS-7 (i) one (it compares a complete decoy
cell of the frozen driver, uninterrupted against killed and resumed, with the job set read from the run: under MBS-7
(i) that set is MB r1's RLR / C2b / C1b ladder); confirmed, unchanged.

**Deviations from MB r1's code (each required by the successor architecture or by the brief; nothing else differs):**

| # | MB r1 | MB-S | reason |
|---|---|---|---|
| V1 | QC02 / QC03 decoys are child processes of the verifier | each is a transient LaunchAgent bootstrapped by the launcher's own `launch` (detachment proved), waited for by its recorded identity, booted out | R-MEM step 1 and RC6: the real driver's `decoy` under the launchd launcher |
| V2 | decoy 316 runs at 1 worker | at WORKERS 5 | R-MEM step 1 ("WORKERS 5"); brief A2 |
| V3 | decoy 297, decoy 316, the serial child, the two ladder children and E4 are spawned together | the prepared-host readings first, then decoy 297, then decoy 316, each ALONE and before every other heavy phase (the verifier's gated heavy phases); then the serial, ladder and E4 children together; then the Monte Carlo | the successor verifier runs heavy phases one at a time behind the disk gate (builder5); the official configuration is the execution's (5 workers alone on the host: R-MEM step 5's memory model and R-EXCL-PCT's "official-decoy worker reading (about 99)"); the readings need the idle prepared host. **For the reviewer: the texts do not state this order word for word, and it changes the concurrency under which Q12's walls are measured (MB r1 measured its walls with every child running)** |
| V4 | decoys run with the driver's caps | the same; the memory cap and poll are the frozen driver's (no measurement configuration) | owner supplement 1, section 3 |
| V5 | QC02 / QC03 pass on MB r1's criterion | MB r1's criterion AND the official configuration (launched, detached and finished as a launchd job; WORKERS; frozen ladder; the planned blocks) | brief A2 |
| V6 | Q12 reads `D.EVAL_CAP_S`, `D.RUNG_CPU_CAP_S`, `mb308_host` | the same values read from the driver's TEXT and the successor's host module, passed in | the verifier does not import the driver for cases that need only text (builder4's rule) |
| V7 | Q12's record carries `eval_cap_required_s` | not recorded (the threshold is compared, never stated) | brief A3: Q12 never derives, proposes or prints a candidate cap |
| V8 | Q12: caps and timing provenance | plus the run configuration (the launchd launcher, WORKERS, frozen ladder), failing closed, with three planted controls beside MB r1's fourteen | RC6 |
| V9 | the in-process cases import the test modules from the namespace's `tests/` | executed from MB r1's pinned bytes; the guard test's name `mb308_guard` is bound to the successor's guard while it loads | the successor copies no science-side file; the guard differs in the marker line only (QC09-S) |
| V10 | Q1: the namespace's own copy of THEOREM_MB against the research file | MB r1's NSF copy at MB r1's path (the successor has no copy), also checked at HEAD, the research file's presence folded into the case | MBS-7 (i): the theorem is MB r1's |
| V11 | the comparison views call `D.jsonable` | a local projection that drops `_`-prefixed keys (identical on JSON data) | the evaluation is importable without the driver (planted-record tests, mutants) |
| V12 | `--dev` runs every selected case | the decoy cases compute only on decoy 297 block 0 at the dev ladder (the children take `--_dev`; the ladder child uses block 0's own pointwise drift); QC01 is never run in dev; QC05, QC06, QC07, QC09-SCI are loader checks (pinned bytes, entry signature) | brief: the only science a test may run |
| V13 | MB r1's QC09 sandbox arming and QC10 flows | not carried here | QC09-S (builder4) and QS-STATE / QS-CRASH cover the successor's own lifecycle |
| V14 | (none) | official and review runs EXECUTE science only in the campaign's qualified worktree (17.5) | a sandbox must never be able to launch the real driver |
| V15 | (none) | MBR1_REPRO, R_RULES_OFFICIAL, the section-4 values check | RC2; section 11.2; brief A3 |
| V16 | a decoy that fails leaves no record (MB r1 and the successor up to 555f4cbf: the exception leaves `main()` before `--out` is written) | `main()`'s decoy branch writes the run's record also when `decoy()` raises: `decoy_failed` (the exception's class name), no stage 1, and the same lifecycle fields (watchdog events and peak, sampler, driver peak RSS, run configuration, host provenance); the exception is then re-raised unchanged (same exit behaviour) | owner supplement 2, sections 1 and 6: a memory-watchdog event must be "mechanically detectable" and "the failed qualification evidence" preserved. Before this change a watchdog kill broke the pool, the decoy raised and NO record existed: neither `STEP1_RERUN_REQUIRED` nor the official fail-closed status could ever have fired on a real event. Recorded fields only; no carried function changed. **For the reviewer: a driver change in the decoy branch** |

QC02 / QC03's records carry, per run, every R-MEM input (each job's `ru_maxrss`, the watchdog's peak and events, the
driver's own peak RSS, builder5's RSS sampler with its largest observed spacing, the run configuration) and the host provenance Q12 needs (K / S / L,
power at every sample, thermal level and ThermalEvent entries); no carried (text-identical) science function was
changed (static RC1 / MBS-9 tests pass). The compact rule inputs of both runs and the qualification's own prepared-host
readings are written to `qualification/MBS308_RRULES_OFFICIAL_INPUTS.json`.

**MBR1_REPRO, full form.** The successor's official QC02 / QC03 / QC04 records against MB r1's committed official r3
records (pinned): each decoy record's identity (cell, blocks) and every certified part (Stage 1: every block, job,
certificate digest, verification and pointwise record; every Stage-2 decoy bundle), the serial block-0 jobs and both
ladder records, with exactly the timing keys and `cpu_cap` stripped at every depth; each comparison must be non-vacuous
and detect a planted one-leaf mutation. Not compared: provenance (host, lifecycle, driver sha256, utc, walls, the
cpu-caps record) and `stage1.workers` (V2). No extra run: the comparison inputs are the official records themselves.

**A3 (MBS-8 (i)).** `Q12_caps` = MB r1's Q12 on the FIXED caps: EVAL_CAP_S >= ceil(1.5 x projection) and every per-job
cap >= 2 x the official maximum wall of its kind and rung (MB r1 protocol 3.2: the 11-block, 9-job longest-first
projection at WORKERS, C2b with its verification seconds once more), MB r1 r3's host-provenance fail-closed conditions
(re-assessed raw readings, the stored assessment never trusted, the interval covering the walls) and its fourteen
planted controls through the successor's own decision function, plus three for the launcher, WORKERS and the ladder.
`section4_values` checks mechanically that the driver carries exactly the user's section-4 values (EVAL_CAP 28 800 s,
started once per attempt in `after_marker` and counted on CLOCK_UPTIME_RAW and no other clock; RLR 1800 / 4200 / 8700 s;
C2b 1800 / 1800 / 2700 s; every C1b and VER cap 1800 s; PRE_CAP 1800 s; WORKERS 5); the configuration's values are
checked against the owner record's own lines; nine planted mismatches (driver text, state text, configuration) each
fail it, and with it the Q12 case.

### 17.3 Part C: the grant binds every complete owner record (three); the final preflight

**C1.** The driver names the three records in fixed order (`S1_OWNER_RECORDS`: record, research path, research commit,
byte length, sha256: `original` 5c2394ba 17 291 bytes 34eb1d41…; `supplement_1` 8fc2b038 18 797 bytes 3f7d477b…;
`supplement_2` 74f386a5 12 941 bytes 4ba4a666…). Supplement 2 itself says "two-owner-record grant binding" in its
section 9 and "both complete owner records and supplements" in its section 12; the coordinator's instruction is the
three records, which satisfies both wordings; that is what is built (for the reviewer). `check_s1_ruling` (called by
`check_grant`) requires `user_ruling_s1` to be exactly `{"records": [original, supplement_1, supplement_2],
"index_sha256", "reaffirms_c4": true}`, each record exactly `{"record", "path", "commit", "bytes",
"sha256", "verbatim"}` with the COMPLETE verbatim text, and refuses unless (a) each text re-hashes to the digest and
length its entry states, (b) each entry equals the driver's row, in order, and (c) the index digest (sha256 of the
canonical JSON of the rows) matches. No other key is admitted (no room for a paraphrase). The manifest writer records
`s1_owner_records` and refuses unless git holds those bytes at those commits; Q8-S compares; the protocol's section 1
states the table. The three texts are valid UTF-8 and round-trip through JSON byte for byte. Planted controls (26),
through the real `check_grant` at `execute` in a sandbox, each refused with nothing consumed: one byte changed in each
of the three texts (with the entry's digest left as it was, and again with the entry made self-consistent), each record
missing in turn (including the two-record index that was complete before supplement 2), each record alone, the records
reversed, rotated and with the supplements swapped, supplement 1 twice in place of supplement 2, a fourth record, a
section-only excerpt of the original (section 5, and sections 5-6: exactly the ranges R2 and R3 of the conformance
review, checked by their lengths and digests) and an excerpt of supplement 2, the old single-text field, a paraphrase
key in the field and in a record, `reaffirms_c4` false, a wrong index digest, no ruling. The three complete records
are accepted and the run seals. The test library's synthetic grants carry the three real records (read from the base
store at their commits; the grant around them is a sandbox stand-in).

**C2.** Owner decisions section 14 lists seventeen items. `OWNER_SECTION14` (verifier), the host report's
`owner_section14` field and protocol section 8.3 map each, in the record's order and wording, to what covers it:
fifteen are existing gates or mechanisms of the driver (named; a test checks that every name exists in the code);
"required lid/sleep state" and "restart hazards controlled" are READ-ONLY recorded readings plus an operator line,
because no accepted text makes them a gate (protocol 8.1 already says the lid is a user action). The lid, the sleep
timers and `autorestart` were already read by builder5's `--host-report`; ADDED: the scheduled power events
(`pmset -g sched`, by type only: a scheduled restart / shutdown / sleep is reported as a hazard). "Git configuration
safety" is mapped to `check_seal_preconditions`, `check_clean`, `check_not_evaluated` and the driver's fixed git
environment; no accepted text names a further git setting, so nothing was added there (for the reviewer).

### 17.4 Part B: section 11.2 option (a), with the second ratifier's readings and owner supplement 2

* **B1, the designated measurement tool** (`code/mbs308_measure.py designate`; built and tested on planted readings and
  a synthetic launchd payload; NOT run). The prepared-host readings (10, at least 30 s apart: the rule's own numbers;
  AC; the driver's own `free_memory_bytes`, executed from its text; wired-down pages; every process the rules can use
  with its executable path and %cpu text), then the planned decoys one at a time through `run_decoy`, the function the
  official qualification uses for QC02 / QC03. Compact evidence: the commit, the driver sha256, the platform readings,
  the boot UUID, the host provenance of the whole measurement and of each run, every rule input, the sha256 of the full
  decoy outputs (kept under `--work`). It refuses outside the qualified worktree, off the committed bytes, with a
  campaign ref, on battery, with thermal level not 0 at the start, with a platform mismatch, without the sleep
  channels, on short disk, and when designated evidence already exists (`ALREADY_DESIGNATED`); it marks the evidence
  invalid (written under `--work` only) on a reading not on AC, a run whose host provenance is not CLEAN, a
  ThermalEvent entry in a run, a host that is not prepared (basename and path class reported; no threshold raised; no
  decoy launched), a run outside the official configuration, a sampler record that is not a valid step-6 input, a
  failed decoy, and any memory-watchdog event (`STEP1_RERUN_REQUIRED`: the tool stops, launches nothing more, and
  records the rule's one re-run cap and its step-5 bound; no cap-override facility exists anywhere).
* **B2, the derivation tool** (`code/mbs308_derive.py derive`) applies the existing rule functions and writes the five
  canonical outputs, each checked to be in the canonical form the rule text fixes (`form_reasons`), with every built-in
  check recorded. Its status is `OK`, or it stops with no output at all: `STEP1_RERUN_REQUIRED`,
  `MEM_POLL_S_NONCANONICAL_BRANCH` (`stop_before_freeze` true; the raw evidence and the branch in `poll`), or
  `NOT_DERIVED`. **The apply step** (`code/mbs308_repin.py apply`, dry-run by default) writes A into the driver's five
  constants and the protocol's rule-output table and regenerates DRIVER_DIFF.md; it refuses a derivation that is not
  designated, not OK (a stop status is named as it is), with a failing check, with an output not in its canonical form
  (MEM_POLL_S is only ever written as `2.0` or `0.5`), not reproduced from the committed evidence, or for other driver
  bytes; every other top-level statement of the driver is checked identical. `mbs308_rrules.r_mem` gained three keyword
  parameters (the cap and the poll the measured runs must have been made with, defaults = step 1's 3 GiB and 2 s; and
  `official`, the series); no rule text and no rule number changed.
* **B3, R_RULES_OFFICIAL**: BUILT (17.1; protocol 11.2): B == A == the frozen driver's constants, exactly, for each of
  the five; set equality for EXCL_ALLOW; no tolerance. `REQUIRED_FILES` holds the two evidence files, so Q8-S (and
  therefore any qualification) fails until the designated evidence and its derivation are committed.

**The rulings of 54-A (second ratifier, research ca66e367) and of owner supplement 2 (research 74f386a5), as built.**

| ruling | where | behaviour | status / reason |
|---|---|---|---|
| READING-6 corrected: the bound binds the OBSERVED spacing | `rrules.sampler_reasons` (used by `r_mem` step 6, by `measure.run_reasons` for each run of either series, and by the derivation's checks) | the largest observed spacing of any run must be ≤ 0.5 s (exactly 0.5 s is within) and must be stated; otherwise invalid input: no g, no MEM_POLL_S, R-MEM not OK | `SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S`, `SAMPLER_OBSERVED_SPACING_UNRECORDED` |
| READING-7 confirmed; supplement 2 §4 | `state.RssSampler.sample` | first-observation semantics NOT changed | none |
| F-6 corrected; supplement 2 §6 | `rrules.r_mem` | an event run is cured only by a VALID re-run of it at the doubled provisional cap; a clean duplicate of the cell cures nothing; until then no rule is applied | `RERUN_REQUIRED` (never OK / INCOMPLETE_INPUT) |
| designated series, supplement 2 §§2, 7 | `measure.measure`, `derive.derivation` | an event at the provisional 3 GiB: stop and report the rule's one re-run cap (6 GiB) and whether it is within the step-5 bound from the valid runs' P and D; no re-run limit, no further doubling (a second event names the same 6 GiB), nothing inferred; NO cap-override facility | `STEP1_RERUN_REQUIRED`; `rerun_step5_bound.within` false carries "STOP AND REPORT BEFORE FREEZE"; no valid run: `defined` false with the owner's open point named |
| official series, supplement 2 §1 | `rrules.r_mem(official=True)`, `qualify.decoy_failure` (QC02 / QC03), `qualify.r_rules_official`, `qualify.aggregate` | ANY memory-watchdog event in an official decoy fails the cases and the qualification closed; no re-run exists (a run claiming to be one is invalid), no doubled cap, no cure by a clean duplicate; the later official decoys and MB r1's children are not launched; the aggregator lifts the status to the qualification record (`fail_closed_statuses`) and a case carrying it can never pass | `QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP` |
| MEM_POLL_S, supplement 2 §§2, 3; readings item 6 | `rrules.r_mem` step 6, `derive.canonical`, `derive.derivation`, `repin.poll_literal`, `qualify.r_rules_official` | canonical only on case (i) (the re-checked value, unchanged) and case (ii) (the clip to exactly 0.5 s); on case (iii) no value is produced anywhere: the exact quotient is reported as `unrounded_quotient_not_an_output` with g, MEM_CAP, the re-checked value and the branch; the derivation stops before the freeze; the apply step can write only `2.0` or `0.5`; in the official series B's MEM_POLL_S is None and no comparison value is made | `MEM_POLL_S_NONCANONICAL_BRANCH` |
| canonical forms, readings item 6 | `derive.form_reasons` (derivation, apply step, R_RULES_OFFICIAL's B) | MEM_CAP: int, multiple of 256 MiB, ≥ 1 GiB; MEM_POLL_S: "2" or "1/2"; FREE_MEM_MIN: int, multiple of 256 MiB, ≥ 2 GiB; EXCL_CPU_PCT: 25, 35, 40, 45 or 50; EXCL_ALLOW: sorted distinct basenames | `<OUTPUT>_NOT_CANONICAL` |
| EXCL_ALLOW, supplement 2 §8 | `derive.compare` | set equality of exact strings, A, B and the driver; no tolerance, subset, union, intersection or sticky list | (comparison) |

**The sampler's configured interval: 0.25 s (the builder's choice; dev evidence only; for the independent review).**
On a fixed-rate schedule the spacing of two readings is the interval plus the scheduling jitter and the `ps` latency,
so a configured 0.5 s can never satisfy the bound: every observation at 0.5 s was above it (builder5: 0.505, 0.51 and
0.555 s; this build's dev decoy under a concurrent agent's load: 0.871 s). Evidence for 0.25 s, all DEV or synthetic,
on a host other agents were loading at the time (worse than a prepared host):
* a synthetic probe (five CPU-bound child processes that also allocate; the real `RssSampler` watching them; no
  science), 300 s windows: set 0.25 s gave a largest spacing of 0.278 s (load average 13) and 0.320 s (load 15.7);
  set 0.125 s gave 0.290 s (load 28); set 0.1 s gave 0.727 s (load 18.7): a shorter interval does not help once the
  host stalls a `ps`, and costs more (one `ps -A` is about 20 ms). 45 s windows: set 0.5 s gave 0.509 s, 0.25 s gave
  0.267 s, 0.2 s gave 0.212 s, 0.1 s gave 0.113 s;
* the driver's real decoy branch with the synthetic evaluator (`state::t_decoy_records_rmem_inputs`, final bytes):
  41 samples, no failed read, largest spacing 0.261 s;
* the dev decoy (decoy 297, block 0, dev ladder, 2 workers; `decoy::t_qs_resume_decoy_dev`, final bytes):
  501 samples, no failed read, largest spacing 0.263 s, and a highest growth
  rate g = 95.6 MiB/s, against 61.9 MiB/s (builder5) and 74.2 MiB/s (this build) for
  the same dev decoy with the sampler set to 0.5 s.

No official-configuration run exists (5 workers, the frozen ladder): the choice rests on the figures above only.
The largest spacing is recorded as `max_spacing_ns` (integer nanoseconds, rounded up; the largest difference of the
time stamps of two consecutive successful readings: a failed reading leaves the gap open) and the rule functions check
that integer. **Two things the reviewer should weigh, neither softened here:** (1) the time stamp of a reading is
taken immediately before its `ps` call, as it always was, so the spacing is that of the time stamps the growth rate is
computed over; (2) **g depends on the configured interval**: a shorter interval reads a fresh worker earlier in its
rise and divides by a shorter time, so the highest growth rate is larger (figures above), which moves step 6 towards
the otherwise-branch. The ratifier lists the set interval among "inputs the text does not fix"; the owner allows a
shorter interval "provided this does not alter the scientific rule beyond implementing the already-accepted
observed-spacing requirement". Whether 0.25 s meets that proviso is the review's.

**The designation rule: a PROPOSAL, flagged (protocol 11.2, step 1; the tool's docstring).** The ratifier ruled that
whether a decoy with an invalid sampler record may be measured again "must be fixed in the designation of the
pre-freeze series before the runs"; no accepted text fixes it. Proposed and implemented fail-closed: the unit is the
whole series of one invocation; an invalid invocation designates nothing, its record is kept under `--work` as
`INVALID_<n>_<utc>_…`, never overwritten, and listed in every later record; a later invocation measures the WHOLE
series again (never one decoy into an existing series, never a selection among runs); once designated evidence exists
the tool refuses (`ALREADY_DESIGNATED`); a memory-watchdog event is not a re-measurement case; no limit on invalid
series is set (no text sets one). **This is the builder's proposal, not accepted text: the owner or the review must
accept, change or reject it before any designated run.**

**READING-15 (builder6; protocol 11.3; for the reviewer).** The driver's watchdog record holds two kinds of entry: a
kill of a worker above the cap, and the release of an already-broken pool (`broken_pool_worker_killed`). Only the
first is read as a "memory-watchdog event" (`rrules.cap_events`); a run with only the second is an invalid input (a
failed decoy) but not an event run: no re-run at a doubled cap is called for, and the official fail-closed status is
not raised by it (the failed decoy fails the qualification anyway). An entry of an unknown kind counts as an event.

**B4. Is exact canonical-output agreement between two independent measurement series well-defined? (Analysis only:
nothing below is softened, resolved or worked around in the code. The second ratifier's canonical forms are taken as
given and do not replace this analysis.)**

Common to all five: the two series are taken at different times (the designated one before the freeze, the official
one at the qualification), each from ONE run of decoy 297 and ONE of decoy 316 and one series of readings. The rule
text says "≥ 10 readings"; both tools take exactly 10 (the rule's minimum; the ratifier notes the text does not fix
the number), since a longer series changes every maximum and every set below. The two series differ by construction
in the cap and the poll the decoys run with (3 GiB and 2 s against the frozen values), as the ratifier notes.

1. **MEM_CAP_BYTES.** Rule: "P = max over every job of every valid official decoy of max(`job_maxrss_bytes` [ru_maxrss
   of the job's fresh worker], `worker_peak_rss_bytes` [watchdog ps])"; "s = max over each (kind, rung) that appears in
   two or more valid runs of (largest peak / smallest peak)"; "MEM_CAP = roundup_256MiB(max(k × P, 1 GiB)), k = max(3,
   2s)". Agreement is well-defined (equality of integers). It depends on host variation through: (i) P, a maximum of
   measured peak RSS values, which differs from run to run; (ii) the 256 MiB rounding boundary: while k × P stays at or
   below the 1 GiB floor both series give 1 GiB, above it two series agree only if both k × P fall in the same 256 MiB
   step, and a change of P by δ moves k × P by at least 3δ; (iii) s, a ratio of two measured peaks, which enters k once
   it exceeds 3/2; (iv) the watchdog's ps peak is sampled at MEM_POLL_S, and the official decoys run with the frozen
   MEM_POLL_S, which may differ from the 2 s of the designated runs; (v) in the official series the frozen cap is the
   kill line: a peak above it cannot be recorded as a larger P, it is an event and fails the qualification closed
   (supplement 2, section 1). At dev scale (decoy 297 block 0, dev ladder) the per-job peaks were 39-88 MiB in every
   run, far below the floor; the frozen-ladder kinds (RLR d6 / d8, C2b N40 / N80, C1b d8-12) are unmeasured.
2. **MEM_POLL_S.** Rule: "g = the highest RSS growth rate seen by a ≤ 0.5 s qualification sampler. Require g ×
   MEM_POLL_S ≤ 0.1 × MEM_CAP; otherwise MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g)." As ruled, an output exists only
   on two branches. With c = 0.1 × MEM_CAP: **designated series** (the re-checked value is step 1's 2 s): A = 2 iff
   g_A ≤ c / 2; A = 1/2 iff g_A ≥ 2c; and for c / 2 < g_A < 2c the derivation STOPS BEFORE FREEZE
   (`MEM_POLL_S_NONCANONICAL_BRANCH`). **Official series** (the re-checked value is the frozen one): if A = 1/2, B is
   1/2 whatever g_B is (the re-check holds for g_B ≤ 2c, and above that the quotient is below 0.5 s and the rule clips):
   agreement does not depend on the host. If A = 2, B = 2 iff g_B ≤ c / 2; for c / 2 < g_B < 2c the qualification
   FAILS CLOSED (non-canonical branch); for g_B ≥ 2c, B = 1/2 ≠ A and the comparison fails. So exact agreement is
   well-defined whenever both sides are on a canonical branch, and it depends on run-to-run variation only when A = 2,
   through one inequality on g_B, an extreme-value statistic (the maximum over thousands of finite differences of RSS).
   **What the dev evidence says about the designated series (not softened): with MEM_CAP at the 1 GiB floor, c / 2 =
   51.2 MiB/s and 2c = 204.8 MiB/s. The dev decoys of this campaign (decoy 297 block 0, dev ladder, 2 workers) gave
   g = 61.9 MiB/s (builder5, 16.6) and 74.2 MiB/s (this build) with the sampler set to 0.5 s, and the figure reported
   above with it set to 0.25 s: on dev figures the designated derivation lands in the STOP band or on the clip, not on
   "unchanged 2 s". The official ladder's g is unmeasured.** If the designated measurement reaches the stop band the
   campaign stops before the freeze as the owner ruled; this build does nothing to avoid it.
3. **FREE_MEM_MIN_BYTES.** Rule: "FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS − 1) × P + D))".
   Well-defined (equality of integers). It inherits every dependence of MEM_CAP and adds D (the driver's own peak RSS)
   and 4 × P, with the same 256 MiB boundary above the 2 GiB floor (at dev scale the sum is about 1.4 GiB: floor). Its
   attainability clause ("At least 3 consecutive readings must reach FREE_MEM_MIN") is a check, not part of the value,
   but it must hold in BOTH series and depends on the host's free memory at ten instants.
4. **EXCL_CPU_PCT.** Rule: "EXCL_CPU_PCT = 25. There is exactly one exception. If the hosting app that runs the
   launcher, which cannot be quit, exceeds 25 in any prepared-state reading, then EXCL_CPU_PCT = min(50, roundup_5(1.25
   × its maximum reading))." Well-defined (an integer in {25, 35, 40, 45, 50}). It depends on the hosting app's
   MAXIMUM instantaneous %cpu over ten readings: one reading at 25.1 instead of 24.9 moves the output from 25 to 35;
   above 25 the two series agree only if both maxima fall in the same bin (25 < max ≤ 28 gives 35, 28 < max ≤ 32
   gives 40, 32 < max ≤ 36 gives 45, above 36 gives 50). The hosting app is the application that runs the agent
   driving the measurement, so it is active by construction. Both series must also identify the same hosting app
   (READING-12).
5. **EXCL_ALLOW (owner supplement 2, section 8).** Rule: "The frozen list = the current 39 names ∪ the basename … of
   every process that meets both conditions: (a) it exceeds EXCL_CPU_PCT in any prepared-state qualification reading
   (≥ 10, 30 s apart) or in this ratification's H3 readings; (b) its executable path lies under `/System/`,
   `/usr/libexec/`, `/usr/sbin/`, `/sbin/` or `/Library/Apple/`", never an excluded class.
   **Is exact equality between an independent designated series and an independent qualification series
   well-defined? Yes.** Each series gives one set: a union of three parts, each fixed by the text: the 39 names (the
   same in both); the H3 daemons whose ratified reading exceeds that series' EXCL_CPU_PCT (a function of item 4 only:
   at 25 all four names; at 35, 40, 45 or 50 only `spotlightknowledged.updater` and `BackgroundShortcutRunner`, whose
   readings 70.3 and 52.2 exceed every possible threshold); and the basenames (`comm.rsplit('/')[-1]`, exact strings,
   no normalisation) of the processes of THAT series' readings that meet (a) and (b). Equality of two such sets is the
   ordinary equality of sets; the rule supplies every semantic the comparison needs, and the ratifier's item 6 says
   the same. It is implemented exactly (A, B and the driver's constant, as sets of exact strings) and tested (one name
   more, one name fewer, a superset, a subset, a duplicate, the driver differing: each fails).
   **What in the rule makes the outcome depend on run-to-run host variation.** Condition (a) is an existential over
   ten instantaneous `ps` %cpu readings of EVERY process on a SIP-protected OS path. Two series give the same set iff
   the SIP-path basenames outside the 39 and outside the H3 part that are seen above the threshold at one of the ten
   instants are the same in both, and both have the same EXCL_CPU_PCT. OS daemons (indexing, sync, analysis, update)
   run in bursts the operator can neither quit nor provoke; they are admitted by (b), so they do not make the host
   "not prepared". One such daemon above the threshold at one instant of one series and at no instant of the other
   breaks equality. The dependence is asymmetric in its effect: a name the designated series adds is frozen into the
   driver's list, and the official series then agrees only if that same daemon exceeds the threshold again within its
   own ten readings; the gate's own tolerance of the daemon (it is in the frozen list) plays no part in B, because B is
   the rule applied to the official readings over the 39 names, never over the frozen list (that would be the sticky
   list the owner excludes).
   **Is there a genuine ambiguity or an undefined comparison? None was found in the comparison itself.** Two inputs of
   it are not fixed by the text and are fixed by the tools, for the review: the number of readings (exactly 10 in both
   series) and the identification of the hosting app (READING-12). The smallest exact question the analysis leaves,
   which is one of consequence and not of definition: *when both series satisfy the rule and differ only because an
   OS daemon admitted by (b) was above the threshold in a reading of one series and in no reading of the other, the
   exact comparison fails the qualification; is that failure the intended outcome?* Owner supplement 2, section 8
   already answers that the comparison is not weakened; so no STOP BEFORE FREEZE follows from this analysis, and none
   was implemented. It is stated so that the owner knows the exposure before the designated measurement.

In short: agreement is DEFINED for all five. MEM_POLL_S and (through the watchdog) MEM_CAP now have ruled fail-closed
branches; EXCL_ALLOW is governed by run-to-run host variation with no margin whenever any OS daemon outside the 39
names is busy in one series only; the other three are boundary-sensitive (the 256 MiB steps, the 25 % threshold and
the bins of the hosting app's maximum).

### 17.5 A safety interlock: real science executes only in the qualified worktree

With the science cases built, an official or review run that passed its preconditions inside a test sandbox (for
instance under a mutant of a precondition) would have launched the real driver's full decoys. `science_phase` therefore
executes (official decoys, MB r1's children, the rehearsal, the in-process cases) only when the driver's own
`check_identity` holds (the qualified worktree, git dir and branch); elsewhere those cases fail closed
(`NOT_THE_QUALIFIED_WORKTREE`) and a plain review only re-evaluates committed records. `mbs308_measure.designate`
(both forms) refuses outside the qualified worktree and branch in the same way. Tests: a child process in a sparse
sandbox with every executing function replaced by a recorder (none is called); the measuring function replaced by a
recorder in a mini repository (not called). No test invokes the measurement CLI or an official verifier run on the real
worktree. A reviewer's `--review --heavy` re-run of the official decoys is therefore possible only in the qualified
worktree (for the reviewer: say if another arrangement is wanted).

### 17.6 The apply step changes five constants: existing tests and one mutant made independent of the provisional values

The official qualification runs the suites and the matrix on the FROZEN bytes, i.e. after the apply step. Four
existing tests and one mutant assumed the provisional values and would have failed there:
`state::t_decoy_records_rmem_inputs` (3 GiB and the default step-1 check), `state::t_gc10_start_gates` and the disk
suite's planted free memory (8 GiB fixed), `state::t_gc10_ratified_allow_list` and `static::t_r3_ratified_rules_applied`
(the four ratified daemons, exactly), and M51 (its fragment was the literal text of the list). They now read the
constants the driver under test carries; the two allow-list tests assert the provisional item-16 list while the
protocol's table says PROVISIONAL and, after the apply step, what R-ALLOW guarantees whatever the measurements (the 39
names, and the two ratified daemons whose H3 readings exceed every possible threshold); M51 mutates the gate's use of
the list, with the same meaning and target. **Sandbox rehearsal (synthetic; not the apply step in the worktree):** in a
`--shared` clone of my base store with this worktree's namespace committed, PLANTED designated evidence gave planted
canonical outputs chosen to move everything (MEM_CAP 1 GiB, MEM_POLL_S 1/2 by the clip, FREE_MEM_MIN unchanged at its
floor, EXCL_CPU_PCT 40, 41 names: `cloudd` and `modelcatalogd` dropped, their H3 readings no longer above the
threshold);
`apply --write` changed exactly the driver's constants, the protocol table and DRIVER_DIFF.md, and `check` was clean;
the suites were then run from the sandbox's own tests on the applied bytes:
static 10 / 10; launch 12 / 12; qualify 23 / 23; disk 17 / 17; cases 25 / 25; state 52 / 52; crash 50 / 50; the full mutant matrix 245 / 245 killed (110 unmutated targets pass; per-mutant `error` fields: none). A second `apply --write` was a no-op.

### 17.7 Tests and mutants (final bytes; my own `--no-local` base store; sandboxes only; on AC throughout)

All runs below are on the FINAL code bytes, in a committed sandbox clone (`git clone --shared` of my own `--bare
--no-local` base store; branch checked out at 555f4cbf, this worktree's namespace copied over it and committed there as
`7bd6d6d507c3`; the real repository was never written), because `repin check` and `disk::t_repin_driver_diff` need the
two new DRIVER_DIFF hunks committed (17.1). The worktree differs from that sandbox commit only in this report's
section 17 (the results below were filled in afterwards); `static` and `qualify`, the only suites that read the
report (the leak scan), were then run again on the filled report: see the last row. The host was on AC power at the
start of every phase (10 readings). No timing-sensitive test failed, so no test was re-run.

| suite | result | seconds |
|---|---|---|
| `static` (QS-STATIC) | 10 / 10 | 5 |
| `launch` (QS-LAUNCH; synthetic payloads under launchd, test labels) | 12 / 12 | 14 |
| `qualify` (QS-QUALIFY) | 23 / 23 | 23 |
| `disk` (QS-DISK) | 17 / 17 | 118 |
| `cases` (QS-CASES, new) | 25 / 25 | 113 |
| `state` (QS-STATE) | 52 / 52 | 416 |
| `crash` (QS-CRASH) | 50 / 50 | 750 |
| `decoy` (dev forms: decoy 297, block 0, dev ladder, 2 workers) | 4 / 4 | 874 |
| mutant matrix | 245 / 245 killed; 110 unmutated target tests pass; survivors none; not run none | 3719 |
| `static`, `qualify` again on the filled report (sandbox commit on top of the one above; run once more after this row was written) | 10 / 10 and 23 / 23, both times | |

**Every per-mutant result was read for an `error` field:** none of the 245 carries one, every mutant's target
run ended with a written, parsed result whose boolean `ok` is false (rc 1: a failed assertion, never an exception or a
missing result), and none of the 110 unmutated target runs carries one. The suites' own result files
were read the same way (no `error` field).

**Tests for this build's parts** (suite `cases` unless said): A1 `t_protocol_owner_decisions_text`,
`t_qc13s_owner_records_fail_closed`, `qualify::t_integration_sparse_sandbox`; A2 `t_science_case_summaries`,
`t_mbr1_carried_modules_and_pins`, `t_qc04_determinism_planted`, `t_mbr1_repro_planted`,
`t_official_science_only_in_the_qualified_worktree`, `decoy::t_science_cases_dev`; A3
`t_q12_decision_and_planted_controls` (MB r1's fourteen controls and three more), `t_q12_never_states_a_candidate_cap`,
`t_section4_values_and_planted_mismatches`; B1 `t_measure_readings_and_hosting_app`, `t_measure_run_validity`,
`t_measure_synthetic_payload_under_launchd`, `t_measure_refuses_and_invalidates`; B2 `t_driver_constants_exact`,
`t_derive_adapters_and_planned_runs`, `t_derivation_outputs_and_checks`, `t_apply_literals_and_constants`,
`t_apply_step_in_a_sandbox`, `t_protocol_table_is_the_drivers_constants`; B3 `t_compare_is_exact_no_tolerance`,
`t_r_rules_official_exact_agreement` (23 rows); the rule functions `qualify::t_rrules_planted_controls` (50 planted
controls); C1 `state::t_grant_binds_every_owner_record` (26 planted controls), `t_owner_records_named_and_bound`; C2
`t_final_preflight_owner_section14`; the failed-decoy record `state::t_decoy_failure_record_on_watchdog_event` (the
driver's real decoy branch, a real watchdog kill of a synthetic job); the sampler fields
`state::t_decoy_records_rmem_inputs`.

**Mutants of this build: MB01-MB109** (each a planted failure of one check, killed by its target's assertion): the grant
index (MB01-MB07, MB109: a record's text not re-hashed, other bytes, the index digest, fewer records, paraphrase keys,
`reaffirms_c4`, supplement 2 dropped); the manifest (MB08); Q12 and section 4 (MB09-MB20); the carried cases
(MB21-MB36, MB100, MB101); the derivation and its adapters (MB37-MB47, MB86-MB92); R_RULES_OFFICIAL and the aggregator
(MB48-MB56, MB96-MB99); the apply step (MB57-MB63, MB75, MB93-MB95); the measurement tool (MB64-MB71, MB102-MB105);
the qualified-worktree interlock (MB72); the final preflight (MB73, MB74); the rulings in the rule functions
(MB76-MB85: observed spacing not enforced or not required, a clean duplicate cures an event run, the official series
re-runs, the non-canonical branch gives a value or does not stop, a broken-pool release counted as an event, the
re-run bound with the undoubled cap, a silent clip); the driver's failed-decoy record (MB106); the sampler (MB107,
MB108).

### 17.8 What remains PENDING, and points for the reviewer (none decided here)

1. **Never executed by me (by the brief's rules), so unproven end to end:** the official forms of QC01 (cell 305's
   committed record), QC05, QC06, QC07 (formal part and the E4 child) and QC09-SCI; the real driver's `decoy` under
   launchd; a full-ladder decoy; QC02 / QC03 / QC04 / QC08 / MBR1_REPRO / Q12 / R_RULES_OFFICIAL on real official
   records; the designated measurement; the apply step in the worktree. Their code is covered by planted records, the
   synthetic launchd payload, the dev forms on decoy 297 block 0 and static signature checks of the carried modules.
   A dress rehearsal by the coordinator is the first real execution.
2. **The sampler's configured interval, 0.25 s** (17.4): the builder's choice on dev evidence; g depends on it; for
   the independent review before the freeze (owner supplement 2, section 5).
3. **The designation rule is a PROPOSAL** (17.4; protocol 11.2 step 1): to be accepted, changed or rejected before
   any designated run.
4. **MEM_POLL_S on dev figures** (17.4, B4 item 2): the dev decoys' g lies in the band where the designated
   derivation stops with `MEM_POLL_S_NONCANONICAL_BRANCH`, or on the clip. Nothing was done to avoid it.
5. **EXCL_ALLOW** (17.4, B4 item 5): exact set equality is defined and implemented; its exposure to OS daemons'
   bursts is stated for the owner.
6. **Still the owner's, reported and not resolved:** which P and D stand in the step-5 bound of the re-run when no
   other valid run exists (`OPEN_RERUN_BOUND`; the tools report `defined: false`). And the means of a 6 GiB re-run:
   no cap-override facility exists; on `STEP1_RERUN_REQUIRED` the campaign stops and reports.
7. **V16**: the driver's failed-decoy record (a change in `main()`'s decoy branch; recorded fields only).
8. **READING-11 to READING-15** (protocol 11.3): W_idle = the largest wired-down reading; the hosting app from the
   process ancestry; a "thermal event" is a ThermalEvent power-log entry (the thermal-pressure level gates only the
   start); which processes a reading keeps (a rejected process makes the series not prepared); a memory-watchdog
   event is a kill at the cap, not the release of a broken pool. And exactly ten readings in both series.
9. **V3**: the official decoys one at a time against MB r1's concurrency.
10. **Three records in the grant** (17.3): supplement 2's own wording says "two-owner-record" (section 9) and "both
    complete owner records and supplements" (section 12); three are bound.
11. The class names of the two new DRIVER_DIFF hunks (17.1); `repin check` and `disk::t_repin_driver_diff` pass only
    on the committed bytes.
12. "Git configuration safety" (17.3): mapped to existing gates only.
13. Any platform re-pin must precede the designated measurement: afterwards the frozen driver must equal the measured
    driver with exactly the five outputs applied (R_RULES_OFFICIAL checks it).
14. builder5's open point 16.9 item 1 (`busy_processes` fails open on a failed `ps`) is untouched.
15. The leak scan (QC12-S) covers `evidence_prefreeze/*.json` without a timing exemption; it was exercised on planted
    evidence only.
16. **The freeze writer does not itself read the derivation's status.** "STOP BEFORE FREEZE" is enforced by the tools
    in three places: the derivation's status and `stop_before_freeze`, the apply step's refusal (so the reviewed step
    can never write outputs from a stopped derivation), and, after a freeze made against the stop, Q8-S /
    R_RULES_OFFICIAL failing the qualification. `mbs308_manifest.py --freeze` was not given a check of its own (no
    instruction; it would change builder4's writer and its tests): for the reviewer.
17. **Not repaired here, by instruction:** the findings of the review that returned DELTA_REJECTED on cc723527 +
    555f4cbf (two QC13-S records expecting a status name where the named file's line 2 differs; the scratch cleanup
    that can delete a base store borrowed from another root). Another builder repairs them on top of this delta.

### 17.9 Integrity, ledger, exposure

* **New cell-308 target evaluations: 0.** Every state-changing run used the synthetic evaluator, the synthetic launchd
  payloads or planted records, in sandboxes cloned `--shared` from builder6's own `git clone --bare --no-local` base
  store. The only science: decoy cover cell 297, block 0, development ladder (before the interruption `decoy::t_science_cases_dev` (ledgered 13:51:25Z); on the final bytes the dev decoy suite's four tests once, in sandboxes (ledgered 16:54:11Z and 18:42:30Z)). Its decoy values stay in
  builder6's scratch and are never juxtaposed with any tail-cell number. Cells 305-309, any drift in the band or its
  mirror, and cell 309's campaign were not touched. QC01's rehearsal was never run.
* Real repository: no git write of mine anywhere; `git for-each-ref refs/p5y-k5-cell308-mbs-r1/` is empty; the worktree's HEAD is still 555f4cbf; no `evidence_prefreeze/`, no `qualification/` and no freeze manifest exists in the worktree. Outside the worktree and my scratch I wrote only: my ledger lines, appended to the research worktree's ledger file (uncommitted, for the coordinator), and a local `git fetch` of the repository's branches into my own scratch base store (needed for owner supplement 2's commit).
* Launchd: transient LaunchAgents with SYNTHETIC payloads only, under the test prefix
  `org.rebaseguard.mbs308.test.` (the launch suite's own labels, and `…test.decoy297.<utc>` / `…test.decoy316.<utc>` of
  the cases suite); each was booted out by the code under test and its plist removed; `launchctl list` shows no
  rebaseguard job and no plist is left. The real driver was never launched by launchd.
* Ledger (agent `builder6`, `c308_quarantine.log_event`, target_evaluations 0 on every line, no LEAK_FLAG):
  2026-10-01T13:51:25Z INFRASTRUCTURE; 2026-10-01T13:51:25Z SYNTHETIC_VALIDATION; 2026-10-01T13:51:25Z NONTARGET_DRIFT_VALIDATION; 2026-10-01T14:06:24Z SYNTHETIC_VALIDATION; 2026-10-01T14:58:35Z SYNTHETIC_VALIDATION; 2026-10-01T16:54:11Z INFRASTRUCTURE; 2026-10-01T16:54:11Z SYNTHETIC_VALIDATION; 2026-10-01T16:54:11Z NONTARGET_DRIFT_VALIDATION; 2026-10-01T18:42:30Z NONTARGET_DRIFT_VALIDATION. The 14:58:35Z line announced a final run that the session usage limit cut before it started (no run corresponds to it); the 18:42:30Z line says so and names the four dev decoy tests of the final run.

**Exposure statement (builder6).** I read no MB r1 run record, review, adjudication, postexec or evidence file, and
ran no `git log` on any branch of the real repository (only `git log -1 --format=%H` on my own sandbox commits). After
the interruption my context was rebuilt from a summary of my own earlier work in this session and the same memory
index; the coordinator's two later messages (54-A and the resume message) and owner supplement 2 carry no MB r1 run
observation beyond the outcome label. What my context holds about MB r1 that did not come from an allowed file: my session began with the
user's auto-loaded memory index (I opened none of its files; it is not a source). **It does carry MB r1 run
observations, qualitatively:** the outcome label of MB r1's one execution (consumed once, INDETERMINATE, never rerun),
with the successor's pre-freeze status and that owner decisions are recorded; a lesson line that lid-close sleep and
fanless thermal slowdown inflate wall times and contaminate runtime gates; and successor-lesson lines (never move
`packed-refs.lock` aside; timing kills are not kills; positive-evidence liveness). It carries no per-job, progress,
CPU, memory, host or science figure of the consumed run. From allowed files I also read MB r1 protocol section 14 (the
pre-grant r2 qualification failure: sleep times and a slowdown figure of a QUALIFICATION run, not of the consumed
execution) and section 3.2 (pre-freeze decoy walls). None of it is used: every cap is the user's section-4 value, every
rule number is the ratification's, every other value is planted or measured here on decoy 297 block 0, and no
threshold, timeout or tolerance was chosen from it. The one number chosen in this build, the sampler's configured
interval, rests on the dev and synthetic figures of 17.4 only.

### 17.10 What of 54-A was already in before the interruption (asked by the coordinator and by owner supplement 2, section 9)

The session was cut by a usage limit while the 54-A rework was under way. The 54-A message HAD reached me and I had
read the ratifier file's named parts. State of the uncommitted bytes at the interruption, item by item:

| 54-A item | before the interruption | completed after the resume |
|---|---|---|
| 3. validity by series (designated 3 GiB / 2 s; official = the frozen values) | IN: `r_mem(measurement_cap_bytes, measurement_poll_s)` and its callers, built before 54-A arrived | the `official` parameter (no re-run in the official series) |
| 2. F-6 corrected | IN in `rrules.r_mem` only (cured only by a valid re-run chain; `RERUN_REQUIRED` before any other status; the re-run's step-5 bound) | planted controls, mutants, the derivation and measurement statuses |
| 1. READING-6 corrected | PARTLY: `r_mem` checked `max_spacing_ns`; `RssSampler.stop()` recorded it (so the helper pin was stale) | the configured interval (0.25 s) and its evidence; `derive.sampler_input`; `measure.run_reasons`; the planted controls; the tests and the synthetic payload; the helper re-pin; DRIVER_DIFF; the protocol; the designation-rule proposal |
| 4. canonical forms | only `r_mem`'s poll `case` / `canonical` labels | `derive.form_reasons` and its use in the derivation, the apply step and R_RULES_OFFICIAL; `poll_literal` restricted to 2.0 / 0.5; tests on canonical values |
| 5. owner's open points as fail-closed STOP statuses | only three message constants in `rrules` and the re-run bound report | superseded by owner supplement 2: the three ruled statuses in rrules, derive, measure, qualify, the aggregator; the driver's failed-decoy record that makes an event detectable |
| 6. READING-3, 7 and 1, 2, 4, 5 confirmed | nothing to change | the protocol states READING-7 as confirmed |
| configuration: `reviewQ6`, `ratifier2` in the ledger agents; my READING-7..10 renumbered | NOT in | in (READING-11..14, and READING-15 new) |

At the interruption the worktree was therefore in an inconsistent intermediate state (stale helper pin; the planted
R-rule controls and the cases suite would have failed). Every result in 17.7 is from the final bytes; every run made
before the last code change is treated as pre-final and is not reported as a result.


## 18. The bounded repairs of reviewQ6's DELTA_REJECTED: R1-R7, F-4 and the coverage gaps G-1, G-2, G-5 to G-11 (non-holder builder7, research brief 56 at 563886f3; NOT frozen)

**Updated by a follow-up: subsections 18.h to 18.j (four further items asked by the coordinator after the first
handback). Where they differ from 18.a to 18.g, they are current; the stale places below are marked.**

**Scope.** Brief 56 only (its recorded file, sha256 1a6d800a…, verified before anything else), on successor 78a172cf
(builder6's commit), target-free. The rejection that is repaired is preserved and untouched: research
`reviews/REVIEW_PREFREEZE_TOOLING_MBS308.md` (reviewQ6, DELTA_REJECTED, research 82d59cc2). Nothing here freezes,
measures officially, qualifies, authorises or grants anything. **New cell-308 target evaluations: 0.** No cell 305-309
was evaluated, no drift in [6/5, 13/5] or its mirror was computed, cell 309 was not touched. **No science was run at
all**: no decoy, not even the dev decoy on cell 297 (the decoy suite is not in the brief's re-run list and no mutant
targets it). No authorization, grant, marker, pending result, seal or freeze manifest exists in the worktree; no
designated measurement, no official qualification run; no system setting was changed. **No operational number was
changed** (caps, limits, timeouts, thresholds, allow-list, polls, the five rule constants, QUAL_MIN_FREE_BYTES and its
recorded inputs are the committed values). No science function, no carried function and no rule text was changed. No
git write: every edit is left in the worktree for the coordinator.

**Read.** Brief 56 in full; the rejection in full (sections 1 (e), 3, 7 and 8 as instructed, the rest for the wording
of the findings); research `ledger/QC13S_RECORD_CHECK_T2.md`; `governance/CONSTANTS_RATIFICATION_MBS308_READINGS_R1.md`:
"Rulings at a glance", item 1 (READING-3) and the section "READING-1, 2, 4, 5" with its G-10 paragraph; this report's
sections 15, 16 and 17 (sections 6 and 9 NOT opened: a `grep '^## '` of the headings only); the protocol draft's
sections 8, 8.1, 8.2, 8.3, 11, 11.1-11.3; the successor's `code/mbs308_scratch.py` and `mbs308_repin.py` in full, the
parts of `mbs308_qualify.py`, `mbs308_driver.py`, `mbs308_host.py`, `mbs308_state.py`, `mbs308_rrules.py` and
`mbs308_measure.py` this section names; the tests and the test library; the configuration; the first 60 lines of
`DRIVER_DIFF.md`; research `code/c308_quarantine.py`'s `log_event` and the ledger's last two lines (format). **Not
opened:** any MBS-2 file (REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*,
REVIEW_SUCCESSOR_GOVERNANCE_308*, INCIDENT_INDEPENDENCE_REVIEW_MB308* and _MBS308* including T6,
COORDINATOR_EXPOSURE_DISCLOSURE*, USER_TEXTS_SUCCESSOR_308.md, governance/SUCCESSOR_GOVERNANCE_308.md, history/),
anything under MB r1's `review`, `adjudication`, `postexec` or `evidence` directories, the owner records
(USER_RULING_MBS308_*: not needed), any other session's or agent's scratchpad, anything under `/Users/suzhe/.claude/`.
No `git log` was run on any branch. In particular the two files whose expected token R1 corrects were NOT opened: the
correction rests on the coordinator's recorded status check alone.

### 18.a Changed files (all inside the successor namespace)

| file | sha256 (prefix) | what changed |
|---|---|---|
| `code/mbs308_scratch.py` | `75555ba91422` | R2: the borrower register and the base-store rule; R3: the record before the deletion; R4: the `file:` form of the planted reading |
| `code/mbs308_qualify.py` | `75da4b5ec514` | R5: `config_consistency`, `aggregate`; R7: the host report's statuses (`recorded_status`, `exclusive_status`, `pidfile_status`) |
| `code/mbs308_driver.py` | `a84bc9703adf` | R6 only: `busy_processes`, `host_preflight` (the exact diff is below) |
| `code/mbs308_repin.py` | `9cec13e25fb7` | F-4: the SCIENCE-GLUE set includes the carried list of the committed header |
| `config/MBS308_QUALIFICATION_CASES.json` | `8e18a649715f` | revision r5: R1 (two expected tokens, two notes); `builder7`, `reviewF8` in the ledger agents |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | `a83a30fc5c45` | 8.1: the statuses sentence and the two gate rows; 8.2: the planted reading, the record before the deletion, the base-store rule (no rule text of section 8 changed) |
| `DRIVER_DIFF.md` | `ee89ba3d7909` | regenerated by the validated generator (23 hunks, every class carried) |
| `tests/mbs308_testlib.py` | `1a50e7019fec` | the borrower record of every suite process (`borrow_begin`, `borrow_clone`, `borrow_finish`) |
| `tests/mbs308_child.py` | `1ec716bc3f10` | planting knobs `ps_list_fails`, `dev_ladder`, `report_rusage` |
| `tests/test_mbs308_disk.py` | `c7ae35dd066b` | + 12 tests; the planted layout carries a borrower register; one assertion added to `t_cleanup_only_disposable` |
| `tests/test_mbs308_qualify.py` | `313036412c5a` | + 5 tests; `sparse_sandbox` names its clone in the base store |
| `tests/test_mbs308_state.py` | `faadf440efd3` | + 3 tests |
| `tests/test_mbs308_launch.py` | `963b2937f6db` | + 1 test |
| `tests/test_mbs308_mutants.py` | `d27c31b367ab` | + 37 mutants (MD28-MD40, MQ37-MQ48, M67-M73, MM04, MM05, MR05-MR07); M43 re-expressed |
| `BUILD_REPORT.md` | (this file) | this section |

No helper changed (`mbs308_guard.py`, `mbs308_host.py`, `mbs308_state.py`, `mbs308_launch.py` are byte-identical to
78a172cf), so `HELPER_SHA256` is unchanged (`mbs308_repin.py helpers`: nothing stale). The driver changed in two
functions that hunk 8 of `DRIVER_DIFF.md` already touched (`busy_processes`, `host_preflight`; 18.b, R6), so the hunk
count (23), every hunk's touched set and every class are as committed; `DRIVER_DIFF.md` was regenerated by the
validated generator (`mbs308_repin.py driver-diff --write`: validated against HEAD, every class carried, no
`--classes`), never by hand. Because no hunk is new, `mbs308_repin.py check` and `disk::t_repin_driver_diff` pass in
the uncommitted worktree as well as on the committed bytes (the case builder6 reported does not arise here).

### 18.b The repairs: what, test, mutant

Every mutant below was killed by its target's own assertion in the final matrix (18.e).

**R1 (F-1): QC13-S's two delta-review records.** Configuration revision r5: the records `GOVERNANCE_ACCEPTED` (research
00a432df, `…_GOVERNANCE_308_DELTA.md`) and `ROUTE_ACCEPTED` (research 87d0b2b9, `…_ROUTE_308_R3.md`) now expect
`DELTA_ACCEPTED`, the token `ledger/QC13S_RECORD_CHECK_T2.md` records as line 2 of each named file (the delta review's
own token); each keeps its id, commit, path and ref, and a `note` states what the id means (the governance acceptance of
the conditions register, S16 a; the route acceptance) and where the correction comes from. I did not open either
file: **the coordinator must re-run `check_record` on these bytes for every record** (the brief says so; nothing in
this section claims the statuses of the real records). Test `qualify::t_qc13s_delta_review_tokens`: the two configured
records (kind, expected token, commit, path, note) and, through the verifier's own `check_record` on PLANTED files in
a throw-away repository, each configured record pointed at a planted delta review (line 2 `DELTA_ACCEPTED`, the status
name only inside a sentence) is OK, and pointed at a file whose line 2 is its status name it is VERDICT_MISMATCH.
Mutant: none of its own (the repair is in the configuration, which the mutant runner does not mutate; the line-2 rule
itself has MQ27). Shown to fail without the repair: 18.e, negative control N1.

**R2 (F-2, G-3): "a store still borrowed is kept" is now true; the exact rule is in protocol 8.2.** In
`code/mbs308_scratch.py`: a borrower register INSIDE each base store (`<store>/mbs308-borrowers/<pid>-<nonce>.json`;
`begin_borrow`, `borrow_clone`, `finish_borrow`, `store_borrowers`). `cleanup` deletes a bare base store only when
(1) it is a disposable unit of a FINISHED root, (2) it has a register with at least one record (a store without one
is kept: `BASE_STORE_BORROWERS_UNRECORDED`: "refuse what cannot be protected"), (3) every record is valid, FINISHED and
its owner positively dead (`identity_state`; UNKNOWN is never dead), (4) no clone the pass keeps under the cleaned root
and no clone path a record names, under any root, still borrows from it (`BASE_STORE_IN_USE`); all four are checked
again just before the deletion. The test library (`tests/mbs308_testlib.py`) records every suite process inside the
base store on its first use of it (`base_store()` -> `borrow_begin`), names each sandbox before cloning it
(`Sandbox`, and `sparse_sandbox` of the qualify suite) and marks the record FINISHED at exit; it is NOT best effort: a
store in which the record cannot be written is not used. The wired uses are unchanged in effect: the verifier and the
mutant runner clean scratch roots that hold no base store. Tests: `disk::t_base_store_borrowed_in_root_kept` (the
in-root rule: a nested ACTIVE root's clone, which the register does not name, keeps the outer store; control: both
clones gone, then the store), `disk::t_base_store_borrowed_cross_root_kept` (the reviewer's case and eight more: a
sandbox in ANOTHER root borrows the store; kept, and that sandbox still reads its HEAD, with no register, an empty
register, an ACTIVE or a FINISHED record of a live process, a live process whose `ps` fails, an ACTIVE record of a
dead process, an invalid record, a symlinked record, and a finished dead record naming the other root's clone;
control: nothing borrows, the store goes and the deletion is recorded), `disk::t_borrower_records_and_library` (the
record functions, their refusals, and the library's own wiring and refusal). Mutants MD28 (in-root rule off: the
reviewer's YD4), MD29 (the register's clones ignored), MD30 (a store without a register counts as unborrowed: the
reviewed defect), MD31 (recorded borrowers ignored), MD32 (UNKNOWN counts as dead), MD33 (an ACTIVE record of a dead
process counts as finished), MD34 (an invalid record ignored). The library's wiring lives in `tests/`, which the
runner does not mutate: negative controls N2a-N2c (18.e).

**R3 (F-3): no unrecorded deletion.** `cleanup` writes and fsyncs each deletion's record BEFORE the deletion (so the
log is opened before the first one); a log that cannot be opened or written (a symlink, a directory, a non-regular
file, a write error) stops the pass with `DELETIONS_LOG_UNWRITABLE` and nothing (more) is deleted; the partial report
travels with the refusal (`.report`). A record therefore means that a deletion was STARTED (stated in the module and
in 8.2). Test `disk::t_cleanup_records_before_deleting` (the reviewer's symlink probe and a directory: nothing
deleted, every byte unchanged, nothing written through the symlink; each record on disk before its unit goes; a log
that fails at the second record leaves the second unit). Mutant MD35 (the old order).

**R4 (G-4): the reading falls after the start.** A test facility was added to the planted reading:
`MBS308_TEST_DISK_FREE=file:<path>` takes the reading from a file at every probe (it can still only lower the real
reading or fail it; an unreadable file is a failed probe): `disk::t_planted_reading_from_a_file`, mutant MD37. With
it: `disk::t_verifier_phase_gate_reading_falls` (the verifier's OWN per-phase gate, a real dev --heavy run of
QS-STATIC and QS-LAUNCH in a sparse sandbox: the reading drops once QS-STATIC has begun; QS-STATIC runs and passes,
QS-LAUNCH never runs and fails closed, DISK_REFUSED) with mutants MD38 (the reviewer's YD9: the gate replaced by a
constant pass) and MD39 (YD11: a refused phase passes); `disk::t_mutant_runner_reading_falls` (the REAL runner,
`--only M11`: the reading drops once the first phase has begun; the unmutated target runs, M11 does not, exit 1). The
runner lives in `tests/` (no mutant): negative control N3 (18.e).

**R5 (F-5): a case naming no gate is not ignored.** `config_consistency` names it (`cases_without_gates`, fails) and
`aggregate` fails on it by itself (`cases_without_gate`, printed), whether the case fails, is pending or passes; a
`gates` value of null is now a gate-less case instead of a TypeError. Test `qualify::t_case_without_gate_not_ignored`
(empty list, no key, null, only an unknown gate; the aggregate's own check in isolation, with the consistency verdict
planted to pass; control with a gate). Mutants MQ37 (consistency) and MQ38 (aggregate).

**R6 (ruling (a)): the two start gates fail closed on no reading. The exact driver diff** (`code/mbs308_driver.py`;
nothing else in the driver changed; no number):

```diff
-def busy_processes(text: str | None = None) -> list:
-    """Processes above EXCL_CPU_PCT (ps %cpu) other than this process tree and the documented OS/UI allow-list."""
+def busy_processes(text: str | None = None) -> list | None:
+    """Processes above EXCL_CPU_PCT (ps %cpu) other than this process tree and the documented OS/UI allow-list.
+    None when there is NO READING: `ps` failed, or its output holds no process row (`ps -A` always lists at least this
+    process). The exclusivity gate then fails closed: host_exclusive is never true on no reading."""
     text = HOST._run(["/bin/ps", "-A", "-o", "pid=,ppid=,pcpu=,comm="]) if text is None else text
+    if text is None:
+        return None
     mine = {os.getpid(), os.getppid()}
-    out = []
-    for ln in (text or "").splitlines():
+    out, rows = [], 0
+    for ln in text.splitlines():
 (...)
             continue
+        rows += 1
         if pid in mine or ppid == os.getpid() or pcpu <= EXCL_CPU_PCT:
 (...)
-    return out
+    return out if rows else None
 (host_preflight)
     pid_rec, pid_state = STATE.read_pidfile(store())
-    g = HOST.preflight_gates(REPO, other_job_running=pid_state == "LIVE", launched=launched, texts=t.get("host"),
-                             su_texts=t.get("su"))
+    if pid_state == "STALE" and HOST.identity_state(pid_rec["identity"]) != "DEAD":
+        pid_state = "UNKNOWN"                   # a recorded driver is STALE only on POSITIVE evidence of its death: a
+    #                                             failed `ps` or boot-UUID reading is UNKNOWN, never DEAD (it refuses)
+    g = HOST.preflight_gates(REPO, other_job_running=pid_state in ("LIVE", "UNKNOWN"), launched=launched,
+                             texts=t.get("host"), su_texts=t.get("su"))
 (...)
-    g["gates"]["host_exclusive"] = not busy
+    g["gates"]["host_exclusive"] = busy is not None and not busy     # no `ps` reading: the gate fails closed
```

Semantics, exactly: `host_exclusive` now also refuses when there is NO reading (a failed `ps`, an empty output, an
output without one process row); with a reading it decides as before. `no_other_campaign_job` now also refuses when
the pidfile records a process that is not POSITIVELY dead (`identity_state` not DEAD: a failed `ps` or boot-UUID
reading, or a recorded identity that cannot be compared); a LIVE pidfile refuses as before; an absent pidfile and a
positively dead one (pid gone, pid reused, another boot) pass as before. **Not changed, for the reviewer:** an
INVALID pidfile (not readable as a regular file of this user, not JSON, no identity) still passes the gate, as
before (it records no process; the brief asks only for the failed-reading case); `read_pidfile` itself and the helper
`mbs308_state.py` are untouched; the recorded reading `pidfile` can now be `UNKNOWN` and `busy_processes` can be null.
Protocol 8.1 states both behaviours in the two rows' "how it is checked" (no rule text changed). Test
`state::t_start_gates_fail_closed_on_no_reading` (the driver's real `host_preflight` in a sandbox child on planted
readings: a failed `ps -A`, an empty output, an output without a row, a quiet listing, a busy process; a pidfile of a
live process, of a live process whose `ps` fails, of a dead process, of a reused pid, none). Mutants M67 (a failed
`ps` reads as "no busy process"), M68 (an output without a row reads quiet), M69 (the pre-repair gate line), M70 (a
live recorded driver whose `ps` fails reads STALE), M71 (UNKNOWN does not refuse). **M43 was re-expressed** (its
fragment was the old gate line; same meaning, same target, as builder6 did for M51).

**R7 (F-7): the host report.** `automatic_restart` is RECORDED only when both `pmset -g` and `pmset -g sched` were
read (`pmset -g` does not list `autorestart` on this host, so the status follows the readability of the output, not
the presence of that key); `host_exclusive` is READY only on a `ps` reading without a busy process (no reading:
UNKNOWN); `no_other_campaign_job` is READY only for no pidfile or a positively dead recorded process (LIVE: NOT_READY;
anything else, an INVALID pidfile included: UNKNOWN). Protocol 8.1 says so. Test
`disk::t_host_report_unreadable_never_ready` (the verifier's own `host_report()` in a sparse sandbox, ten planted
scenarios). Mutants MQ39-MQ42. **(Superseded: done in the follow-up, 18.h item 1.)** **Not done, and said plainly:** the second half of the reviewer's ruling (e) -- that
the official qualification record should embed the host report, and that the place where the user's actions (lid,
quitting apps, no concurrent heavy work) are recorded should be named -- is not in brief 56's R7 and was not built:
it changes the official record and names a procedure, which is the coordinator's or the owner's to instruct.

**F-4: the generator's SCIENCE-GLUE refusal can now fire for a function-body change** (repaired, not withdrawn). The
carried set against which hunks are classed is the list the COMMITTED `DRIVER_DIFF.md` header states (validated
against the committed driver by the generator's own first step) together with the definitions text-identical in the
working driver; a change inside a carried function is therefore still SCIENCE-GLUE: `SCIENCE_GLUE_HUNK`, exit 2, and
`--classes` cannot reclassify it (the class is decided before the override is read). The header's own list is still
rendered from the working driver. Test `disk::t_repin_science_glue_refused` (a comment planted in the body of `stage1`
and of `fs`, with and without `--classes` and `--write`; control: the same change in `host_preflight`, not carried).
Mutants MR05 (the pre-repair set) and MR06 (the reviewer's YRP3: a SCIENCE-GLUE hunk does not fail).

**Coverage gaps (the code was right; a test and a mutant each).**

| gap | test | mutant(s) |
|---|---|---|
| G-1 an empty `ps -o command=` reading is hashed | `launch::t_identity_command_empty_reading_unknown` (planted at the reading itself: empty output, blank line, failed `ps`; the live process is UNKNOWN, never DEAD) | M72 |
| G-2 a dev-ladder decoy recorded as "frozen"; D from the children | `state::t_decoy_record_ladder_and_driver_peak` (main()'s real decoy branch with `--dev-ladder`, synthetic evaluator, jobs holding 256 MB: the record says "dev" and is never a step-1 input; D is at most the driver's own peak read after the run and below the children's) | MM04, MM05 |
| G-3 | under R2 | MD28 |
| G-4 | under R4 | MD38, MD39 |
| G-5 no re-verification before the deletion | `disk::t_cleanup_reverifies_before_deleting` (the state changes right after the first verification: the root becomes ACTIVE; a borrower appears in the store) | MD36 |
| G-6 the repository volume | `disk::t_verifier_checks_repository_volume` (readings planted per path: the repository one byte short, or unreadable, fails although `--work` has plenty) | MD40 |
| G-7 `lock_read` follows a symlink | `state::t_lock_read_never_follows_symlink` (a symlinked lock name reads None; `Lock.acquire` takes and breaks nothing) | M73 |
| G-8 Q8-S and a commit-pin mismatch | `qualify::t_q8_commit_pin_mismatch` (seven planted mismatches) | MQ43 |
| G-9 a raw-text-only match in post-freeze JSON | `qualify::t_qc12s_raw_text_only_match` (a duplicated key, whose first value the parser drops) | MQ44 |
| G-10 four details of R-MEM, with the second ratifier's confirmations | `qualify::t_rmem_formula_details` (D is the largest driver peak; READING-2: the per-run watchdog peak is part of P; READING-3: a rung's per-run peak is its largest job, and two blocks in one run are no spread; step 5 sums four workers for WORKERS 5, exactly at and one byte beyond the bound) | MQ45, MQ46, MQ47, MQ48 |
| G-11 PLATFORM_PINS after a failed reading; a SCIENCE-GLUE hunk | `disk::t_repin_platform_failed_reading_refused`; under F-4 | MR07; MR06 |

**Housekeeping.** The configuration's ledger agents now hold `builder7` and the next reviewer `reviewF8`.

### 18.c What builder6 had already done (verified, not redone)

`builder6`, `reviewQ6` and `ratifier2` were already in the configuration's ledger agents at 78a172cf (verified in the
committed file; `cases::t_qc13s_owner_records_fail_closed` asserts them). Nothing else of brief 56's list had been
done: builder6's own section 17.8 says so for `busy_processes` (item 14) and for the two QC13-S records and the base
store (item 17), and I found the code at 78a172cf as the review describes it for R2-R7, F-4 and every gap.

### 18.d For the reviewer (stated, none softened)

1. **R2 is a new mechanism, not a one-line fix.** Its costs: a base store without a register is never deleted by the
   tool (every store made before this change; delete by hand); a suite process that is killed leaves an ACTIVE record
   and the store is then kept until a human removes it; the register grows by one small file per suite process (a
   full mutant matrix leaves several hundred in the runner's base store; nothing prunes them); a store's deletion
   reads `ps` once per record of a living pid. Its limit is stated in 8.2: a hand-made clone outside the cleaned root
   is seen only while the store has no register.
2. **R4 added a test facility to the gate's module** (the `file:` form of the planted reading). It can only lower or
   fail the reading, as the plain form.
3. **Existing tests changed** (two places, both in `tests/test_mbs308_disk.py`): the planted `layout()` now gives its
   base store, and the non-bare look-alike, a finished borrower register (as the library leaves a store); and
   `t_cleanup_only_disposable` also requires that no look-alike is LISTED as a unit (without that, MD12 would have
   survived behind the new register rule). **One existing mutant changed**: M43 (R6).
4. **(Superseded: the test now exists, 18.h item 2.)** **The verifier's science-phase gate** (before the official / dev decoys) has no falling-reading test: the reading
   would have to fall between the verifier's start and its first phase, and a test that runs a decoy is science. Its
   wiring is the same `run_gated` call; only the suites' gate is covered by R4's test and mutants.
5. **The reviewer's non-blocking observations of section 3** (the nearest recorded root governs while the cleaned root
   is ACTIVE; a record's `root` field is not compared; a store is judged by shape) are untouched.
6. **Found in passing, not changed (outside brief 56):** **((a) and (b) are repaired in the follow-up: 18.h, items 3
   and 4; (c) stands.)**
   (a) R-MEM's D. In `main()`'s decoy branch the driver reads its `ru_maxrss` BEFORE `HOST.provenance(...)`, whose
   power-log read is large: one `log_events` call raised a fresh process's peak RSS from about 23 MiB to about 104 MiB
   here, and in G-2's synthetic run the recorded D was about 52 MiB while the same process read about 106 MiB
   after `main()` returned. The recorded D is therefore the driver's peak while the workers ran, not its peak over the whole run.
   Whether that is "the driver's own peak RSS in those runs" is the ratifier's reading, not mine.
   (b) QC12-S reads raw text first: a figure written with a JSON escape inside a post-freeze JSON file has no
   raw-text match, so `tail_hits` returns no hit although the parsed value carries it (checked on the neutral planted
   patterns only). The campaign's own writers never escape a digit or a point.
   (c) The gate `no_other_campaign_job` still passes on an INVALID pidfile (R6 above).
7. Counts that moved: launch 13 tests (12 + 1), qualify 28 (23 + 5), disk 29 (17 + 12), state 55 (52 + 3); 282
   declared mutants (245 + 37).

### 18.e Results on the final bytes

All runs are on the FINAL code, test, configuration and protocol bytes (the fourteen files of the table above), in
committed sandbox clones in my scratch (`git clone --shared` of my own `git clone --bare --no-local` base store,
which holds 78a172cf; the branch checked out at 78a172cf, this worktree's namespace copied over it and committed
there; no real repository was written). Every sandbox of every test is a `--shared` clone of that same base store.
The host was on AC power at the start of every phase; free disk never read below 98 GiB.

**The mutant matrix (ONE run, 2026-10-01 21:36-22:54Z, sandbox commit `3b8eff67` on 78a172cf; per-mutant cleanup).**
282 declared, **282 killed, every one by its target's own assertion**: each of the 282 per-mutant entries of the
matrix report was read (the runner copies into it the result file's verdict, exit code and `error` field and whether
the file was written and verified): `test_passed` false, exit code 1, result verified, and NO `error` field in any of
the 282; the unmutated code passes all 128 target tests (no `error` field there either); no survivor, none not run,
no invalid mutant, no timeout. (The per-mutant result files themselves went with the matrix's scratch when I cleared
it; the matrix report is kept.)
411 disk checks (the start and every phase), all passing against 7 GiB; all 410 phases cleaned after their verified
result: 173 sandboxes deleted, 123.7 GiB in total; peak scratch of the matrix 1.490 GiB (it was about 0.9 GiB before:
the phases of R4's verifier test hold a nested base store and a full sandbox at once); what the per-phase cleanups
refused were only the disk tests' own PLANTED units (reasons ROOT_ACTIVE, BASE_STORE_IN_USE,
BASE_STORE_BORROWERS_UNRECORDED: the gate working). M33 was killed by its deterministic run (156 s). The matrix does
not read this report (no target reads it), so its result holds for the bytes with the report as filled.

**The suites.** First run, in the same sandbox commit (22:54-23:19Z), with this section still a draft: static 10 / 10,
launch 13 / 13, disk 29 / 29, cases 25 / 25, state 55 / 55, crash 50 / 50, and **qualify 27 / 28**:
`t_integration_sparse_sandbox` failed because QC12-S's leak scan (the real pinned pattern file) matched my draft's own
SUBSECTION NUMBER, the second one, twice (a heading and a cross-reference; a four-character match, located by line
number only). The scan was right to fire; the code was not at fault. The subsections of this section are therefore
lettered (18.a-18.g), and all seven suites were run again on the report as filled:

| suite (second sandbox commit: the same thirteen code / test / config / protocol files and DRIVER_DIFF.md, this report as filled) | result | peak scratch | seconds |
|---|---|---|---|
| `static` (QS-STATIC) | 10 / 10 | 0.835 GiB | 5 |
| `launch` (QS-LAUNCH; synthetic payloads under launchd, test labels) | 13 / 13 | 0.001 GiB | 15 |
| `qualify` (QS-QUALIFY) | 28 / 28 | 0.011 GiB | 22 |
| `disk` (QS-DISK) | 29 / 29 | 2.104 GiB | 188 |
| `cases` (QS-CASES) | 25 / 25 | 0.844 GiB | 106 |
| `state` (QS-STATE) | 55 / 55 | 0.847 GiB | 391 |
| `crash` (QS-CRASH) | 50 / 50 | 0.851 GiB | 740 |
| `static` and `qualify` once more after the rows above were written (third sandbox commit, this report as it now stands) | in builder7's handback | | |

No timing-sensitive test failed in any run, so none was repeated for that reason. The suites' own result files were
read for an `error` field: none.

**Negative controls (the repairs that live outside `code/`, which the mutant runner does not mutate).** In throw-away
clones of the first sandbox commit the pre-repair state was planted and the repair's test run; each FAILED by its own
assertion (`ok` false, no `error`, exit 1):

| control | planted | test | rows that failed |
|---|---|---|---|
| N1 (R1) | the configuration's two expected tokens as they were (the status names) | `qualify::t_qc13s_delta_review_tokens` | both records: configured, the planted delta review OK, the status-name file a mismatch |
| N2a (R2) | the test library records no borrower and names no clone | `disk::t_borrower_records_and_library` | the four library rows |
| N2b (R2) | the library records the process but does not name its sandboxes | same | `library_names_its_sandboxes` |
| N2c (R2) | the record is best effort (a store that cannot record its borrower is used anyway) | same | `library_refuses_a_store_it_cannot_record_in` |
| N3 (R4) | the mutant runner checks the disk at its start only | `disk::t_mutant_runner_reading_falls` | the test's single verdict (M11 ran) |

### 18.f P_max and B re-measured on the final bytes

Measured with the namespace's own meter (`mbs308_scratch.py measure`: allocated bytes of the suite's scratch tree,
sampled every 2 s; the base store lies outside the trees).

| input | recorded in code and protocol (builder5, 2026-09-30) | re-measured on the final bytes |
|---|---|---|
| P_max: QS-DISK's peak (now 29 tests) | 2171 MiB (2.119 GiB) | 2185 MiB (2.133 GiB) in the first run, 2155 MiB (2.104 GiB) in the second (a 2 s sampler) |
| B: the base store (`git clone --bare --no-local`, 2026-10-01) | 459 MiB (458.4 MiB measured) | 459.0 MiB by the same meter (`du -sk`: 465 MiB), borrower register included |
| the other suites: static / launch / qualify / cases / state / crash | 0.835 / 0.001 / 0.007 / - / 0.844 / 0.850 GiB | 0.835 / 0.001 / 0.011 / 0.844 / 0.847 / 0.851 GiB |

**The 7 GiB derivation still holds:** roundup_GiB(2 x (P_max + B) + 1 GiB) with the re-measured inputs is
roundup_GiB(2 x (2185 + 459) MiB + 1024 MiB) = roundup_GiB(6312 MiB) = 7 GiB (with the larger P_max of the two runs;
with `du`'s 465 MiB for B: 6324 MiB, 7 GiB);
the output would change only above 3072 MiB for P_max + B. **Nothing was edited**: QUAL_MIN_FREE_BYTES and its four
recorded inputs are the committed values (`disk::t_thresholds_derived` passes unchanged). For the reviewer: the
recorded P_max (2171 MiB) is now 14 MiB below the re-measured peak (reviewQ6 measured 2179 MiB); the factor 2 is the
written margin for exactly that, and the heaviest phase is still QS-DISK (its peak is the nested verifier's base store
plus two full sandboxes, as before; the new tests add no larger moment).

### 18.g Integrity, ledger, exposure

* **New cell-308 target evaluations: 0.** No science of any kind was run: no decoy, no rehearsal, no cell. Every
  state-changing run used the synthetic evaluator, the synthetic launchd payloads or planted readings and records, in
  sandboxes cloned `--shared` from builder7's own base store. Cells 305-309, any drift in the band or its mirror, and
  cell 309's campaign were not touched.
* **Real repositories: no git write.** In the successor worktree only read-only git commands ran (`status`, `diff`,
  `rev-parse`, `for-each-ref`, and the re-pin tool's `git show` of HEAD's driver and DRIVER_DIFF.md); HEAD is still
  78a172cf, fifteen files are modified, all inside the namespace, none added or deleted;
  `git for-each-ref refs/p5y-k5-cell308-mbs-r1/` is empty; no `evidence_prefreeze/`, `qualification/`, freeze
  manifest, grant, marker or seal exists in the worktree. In the research worktree: `status --porcelain` (five lines)
  and `rev-parse` once; the names of five untracked certificate files appeared in that output (not opened). Outside
  the successor worktree and my scratch I wrote only my six ledger lines (the research worktree's ledger file,
  uncommitted, for the coordinator). My base store was made by `git clone --bare --no-local` of the repository on
  this machine (no network); my sandbox commits exist only in my scratch.
* **Launchd.** Transient LaunchAgents with SYNTHETIC payloads only, under the test prefix; each was booted out by the
  code under test; `launchctl list` shows no rebaseguard job and no plist is left. The real driver was never launched
  by launchd; in the launch suite it ran its read-only `preflight` (which refuses), in sandbox children `status`,
  `host_gates` and the synthetic `decoy` branch.
* **Host.** AC power at the start of every phase; the lid read open at the end; the power log, read by entry TYPE only
  for 2026-10-01 19:30-23:30Z (my whole window and the hour before it), holds no Sleep, Wake or DarkWake entry. No
  system setting was changed. The read-only host report inside the disk suite read, on this unprepared host:
  automatic OS installation USER_ACTION, exclusivity USER_ACTION, thermal, memory pressure and free memory NOT_READY
  (as the earlier builders and the reviewer found).
* **Scratch.** After each suite its sandboxes were deleted with the namespace's tool (`cleanup --execute` on my own
  finished roots); what the tool refused by design (the disk suite's planted roots) and my sandbox clones and base
  store were deleted by hand at the end. The JSON reports, the logs, my edit scripts and the negative-control script
  stay in `scratchpad/builder7/{reports,logs}` and `scratchpad/builder7`.
* **Pre-final runs, disclosed.** Before the final run I ran, on the then-current bytes in the worktree: the new tests
  one by one; static, qualify, cases and launch; disk, state and crash; and a subset of 89 mutants (all killed by
  assertion). One change followed them (the base-store register reads the caller's identity once per scan instead of
  once per record: the same decisions, fewer `ps` calls), so every one of those runs is pre-final and none is reported
  as a result.
* **Ledger** (agent `builder7`, `c308_quarantine.log_event`, target_evaluations 0 on every line, no LEAK_FLAG):
  2026-10-01T20:35:12Z INFRASTRUCTURE; 21:00:11Z INFRASTRUCTURE; 21:00:11Z SYNTHETIC_VALIDATION; 21:36:43Z
  SYNTHETIC_VALIDATION; 23:22:34Z SYNTHETIC_VALIDATION; 23:22:34Z INFRASTRUCTURE (6 lines; no
  NONTARGET_DRIFT_VALIDATION line, because no decoy was run).

**Exposure statement (builder7).** I read no MB r1 run record, review, adjudication, postexec or evidence file, and ran
no `git log` on any branch. From the files I opened, what I know about MB r1's run is its outcome label only (as the
allowed texts and the earlier builders' statements carry it). My starting context held the host tool's memory index
(MEMORY.md; not a source; I opened none of its files). **It does carry MB r1 run material, qualitatively:** the outcome
label of MB r1's one execution (consumed once, INDETERMINATE, never rerun) with the successor's pre-freeze status; a
lesson line that lid-close sleep and fanless thermal slowdown inflate wall times; and a successor-lessons line
(packed-refs.lock, timing-dependent kills, positive-evidence liveness, that subagents see the index). It carries no
per-job, progress, CPU, memory, host or science figure of the consumed run and no clock time. **It also carries, and I
say so because the earlier statements did not: one-line summaries of OTHER tail-cell campaigns of this project
(cells 306, 307 and 309), some with numeric figures of those campaigns.** None concerns cell 308's run; I repeat none
of them here or anywhere, and nothing in this build uses them: no number was chosen in this build at all (every
threshold, cap, constant and recorded input is the committed value; every other value is planted in a test or
measured on my own synthetic runs).

### 18.h Follow-up to brief 56: the coordinator's four items (same rules; received after the first handback)

After my first handback (sections 18.a to 18.g, which describe the bytes of the third sandbox commit named in 18.e) the
coordinator asked for four bounded items; the worktree was untouched in between (HEAD 78a172cf, uncommitted). **New
cell-308 target evaluations: still 0; still no science of any kind** (no decoy was run: where a decoy would run, a
recorder stands in its place). No git write. No operational number changed; no carried or science function changed;
no rule text changed. Where 18.a to 18.g and this subsection differ, this subsection is current: R7's "not done"
(18.b) is now done (item 1); the missing science-phase test (18.d, 4) now exists (item 2); the two findings of 18.d, 6
(a) and (b) are now repaired (items 3 and 4); the counts of 18.d, 7 and the hashes of 18.a are replaced by 18.i.

**Item 1 (reviewQ6 section 5, note (e), second half): the host report is embedded, and the operator's actions have a
named place.**
* `code/mbs308_derive.py` (the module the measurement tool, the verifier and the apply step share; it never imports
  the driver): `HOST_REPORT_SCHEMA`, `HOST_REPORT_ITEMS` (the fourteen checklist items), `OPERATOR_ACTIONS` (the
  reference to the place) and `host_report_reasons`, a STRUCTURE check: the report is there, it is the read-only
  report, every checklist item is in it once with a known status and how it is checked, it has a time, and it
  references the place. It judges no status and holds no number. `evidence_reasons` now includes it.
* `code/mbs308_qualify.py`: the report carries `operator_actions`; `host_report_record` (a report that cannot be taken
  is recorded as such, and the structure check then fails); `official_inputs`; an official run takes the report at its
  start (after the preconditions, before the readings and the decoys) and embeds it in its record (`host_report` of
  MBS308_QUALIFICATION.json) and in its rule-input record (`host_report` of MBS308_RRULES_OFFICIAL_INPUTS.json); a
  review --heavy run takes its own before its readings; a plain review reports the one its committed record embeds.
  `r_rules_official` requires it of the rule-input record (`official_host_report_reasons`) and, through the
  derivation, of the designated evidence.
* `code/mbs308_measure.py`: `host_report_of` takes the verifier's report in a FRESH verifier process (the measurement
  tool still never imports the driver) before the readings; `measure` embeds what it is given and a measurement
  without a well-formed one is invalid (never designated).
* Protocol 8.1: a paragraph stating the embedding and naming the place: the research ledger
  (`…/p5y_k5_cell308_research/ledger/TARGET_INTEGRITY_LEDGER.jsonl` on `p5y-k5-cell308-research`, the ledger QC13-S
  reads), one line for the run written with `code/c308_quarantine.py` `log_event` by the operator / coordinator,
  quoting the user's statement and its time; every embedded report references it.
* Tests: `cases::t_host_report_structure_check` (fifteen planted defects each with its reason; statuses not judged;
  the reference equals the configuration's ledger; the verifier's OWN report, taken read-only through `host_report_of`
  in a sparse sandbox, passes; protocol 8.1 names the place), `cases::t_records_without_the_host_report_fail`
  (evidence without it or with a malformed one: NOT_DERIVED, and R_RULES_OFFICIAL fails; a rule-input record without
  it: R_RULES_OFFICIAL fails although all five outputs agree; with both: passes whatever the statuses; the
  measurement embeds the report as given and is invalid without one), `cases::t_official_run_embeds_the_host_report`
  (the verifier's wiring, in a child with recorders). Mutants MB110 to MB118. The planted evidence and rule-input
  helpers of the cases suite now carry a planted report (every existing R-rule test runs with it).
* **Said plainly:** (i) "not a new gate" holds for the report's CONTENT (no status is judged anywhere); its PRESENCE
  is now required: designated evidence or an official rule-input record without the report fails, as the instruction
  asks. (ii) The place is the coordinator's instruction for this follow-up, not an accepted governance text: for the
  reviewer and the owner. (iii) Two call sites run only in the qualified worktree and were therefore not executed by
  me, like the rest of the official path (17.8, 1): the top-level `host_report` field written by the verifier's
  `main`, and `designate`'s call of `host_report_of`. `host_report_of` itself, the verifier's official branch (with
  recorders) and both structure checks were executed.

**Item 2: the verifier's science-phase disk gate with a falling reading.** `disk::t_verifier_science_gate_reading_falls`
(the `file:` facility of R4; a child in a sparse sandbox in which "this is the qualified worktree" is PLANTED, every
function that would execute science is a recorder and the real launch paths beneath them refuse): the reading drops
while the first official decoy "runs": the checks before the start and before decoy 297 pass, the check before decoy
316 fails, decoy 316 is never launched and both decoy cases fail closed (DISK_REFUSED); control: both launched; dev:
the reading drops after the verifier's start check and the dev decoy is never run. Mutants MD41 (the gate replaced by
a constant pass), MD42 (a refused decoy case passes), MD43 (the dev decoy runs although its check failed).

**Item 3: R-MEM's D is read last. A NEW bounded defect, found by builder7, OUTSIDE the rejection 82d59cc2: for the
reviewer to rule on.** Up to 78a172cf (builder5's task 3) `main()`'s decoy branch read `ru_maxrss` of RUSAGE_SELF
BEFORE `HOST.provenance(...)`, whose power-log read alone raised a fresh process's peak RSS from about 23 MiB to about
104 MiB here; the recorded D was therefore the driver's peak while the workers ran, not its peak in the run. **My
reading of the rule text, and why I changed the code rather than report only:** R-MEM step 2 says "D = the driver's
own peak RSS in those runs (the qualification records ru_maxrss of RUSAGE_SELF)". "Those runs" are the valid official
decoys of the sentence before it; the provenance collection is part of the driver's run (it happens in the decoy mode,
before the run's record exists); and the measurement the text names, ru_maxrss, is the process's maximum up to the
moment it is read. So the text decides the question: D is the maximum over the run, and a reading taken before a later
and larger peak is not it. What the text does NOT decide, and I did not touch: whether step 5's sum should count a
peak the driver reaches after its workers have ended (the ratification's reason for the sum, table item 14, is a
simultaneous one); that is the ratifier's, and it is a question about the rule, not about which value D is. The change
is recorded-field only, in `main` (not a carried function), and changes no number:

```diff
             out["lifecycle"] = {"stage1_context": ctx.summary(), "rss_sampler": rss_rec,
-                                "driver_maxrss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                 "rmem_run": {"workers": a.workers, "ladder": "dev" if a.dev_ladder else "frozen",
 (...)
             out["host"] = HOST.provenance(h0, smp.stop(), HOST.snapshot())
             cu = resource.getrusage(resource.RUSAGE_CHILDREN)
             out.update({"mode": "decoy", "driver_sha256": own_sha, "utc": utc(), "wall_seconds": round(time.time() - t0, 1),
                         "cpu_seconds_workers": round(cu.ru_utime + cu.ru_stime, 1)})
+            # D = "the driver's own peak RSS in those runs" (R-MEM step 2: ru_maxrss of RUSAGE_SELF, bytes on macOS),
+            # read LAST: after the host-provenance collection above, whose power-log read raises the driver's peak,
+            # and immediately before the record is serialised (below, for a failed and for a completed decoy alike).
+            out["lifecycle"]["driver_maxrss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
             if failed is not None:
```

(plus the comment above the `lifecycle` literal, reworded). It is the last statement before either serialisation (the
failed-decoy record and the completed one); the serialisation itself cannot be inside the value it writes. Effect on
this host, synthetic evaluator: D was about 52 MiB before and is about 120 MiB now for the same run (the power-log
read). Direction: a larger D raises R-FREE's sum and step 5's left side; nothing is loosened.
`DRIVER_DIFF.md` regenerated by the tool: 23 hunks, every class carried, `main` only. Test
`state::t_decoy_record_driver_peak_read_last` (the provenance collection is planted to hold 300 MB resident and the
peak is read inside it: the recorded D is at least that reading and at most the peak after `main()` returned; the
same for a decoy that fails). Mutant MM06 (D read before the provenance collection). MM01 and MM05 re-expressed (their
fragment was the old line; same meaning, same targets). Protocol 11.2's fact paragraph says where D is read.

**Item 4: QC12-S also scans the decoded record.** `tail_hits` scans every file as raw text and every JSON file ALSO
as the parser decodes it (keys, string values and numbers, wherever the file lies), so a figure written with a JSON
escape, which has no raw-text match, is counted: in post-freeze evidence it is a non-exempt hit unless it lies only in
a timing key (the unchanged exemption); in JSON elsewhere it is a hit (no exemption). A new run-time control of the
case, built from the pinned patterns like its other controls (the first character of a planted figure written as a
JSON escape), must fire, else the case fails. Test `qualify::t_qc12s_json_escaped_figure` (neutral planted patterns
only: the point escaped, a digit escaped; value, key, timing key, outside the post-freeze directories; not JSON and
unparseable JSON stay raw-text scans; unescaped counts unchanged). Mutants MQ49 (the old early return) and MQ50 (JSON
outside the post-freeze directories raw only); MQ24 re-expressed (the same condition in its new place). Limit, stated:
a file that is not JSON, or JSON that does not parse, is scanned as raw text only.

**Left as they are, for the reviewer to rule (listed once more, by instruction).**
1. The start gate `no_other_campaign_job` still PASSES on an INVALID pidfile (not readable as this user's regular
   file, not JSON, or without an identity), as before R6; the host report shows UNKNOWN for it.
2. R2 is a new mechanism: a base store without a borrower register is never deleted by the tool; a killed suite
   process leaves an ACTIVE record and its store is then kept until a human removes it; the register grows by one
   small file per suite process and nothing prunes it; a hand-made clone outside the cleaned root is seen only while
   the store has no register.
3. Unchanged from 18.d: the `file:` test facility in the gate's module (R4); the two changed existing tests and the
   re-expressed M43; the reviewer's non-blocking observations of its section 3.

### 18.i Results on the final bytes of the follow-up

All runs are on the FINAL code, test, configuration and protocol bytes of the follow-up, in committed sandbox clones in
my scratch (a `--shared` clone of my own rebuilt `git clone --bare --no-local` base store, which holds 78a172cf; the
branch at 78a172cf, this worktree's namespace copied over it and committed there; no real repository was written).

| file | sha256 (prefix) | changed in the follow-up |
|---|---|---|
| `code/mbs308_derive.py` | `b6c4ca87f7d8` | item 1: the host-report constants, `host_report_reasons`, `evidence_reasons` |
| `code/mbs308_qualify.py` | `ea624080a7fe` | item 1: `host_report_record`, `official_inputs`, the science phase, `r_rules_official`, the record's `host_report`; item 4: `tail_hits` and its run-time control |
| `code/mbs308_measure.py` | `edbc26c0dd3a` | item 1: `host_report_of`; `measure` embeds the report and requires it |
| `code/mbs308_driver.py` | `febf742746d6` | item 3 only (the diff of 18.h), on top of R6 |
| `protocol/MBS308_PROTOCOL_DRAFT.md` | `740e56ba9cbb` | 8.1 (the embedding; the named place), 11.1 (the decoded scan), 11.2 (where D is read) |
| `DRIVER_DIFF.md` | `c1dfd95e597e` | regenerated by the validated generator (23 hunks, every class carried) |
| `tests/mbs308_child.py` | `39a5071c54b7` | the planting knob `provenance_alloc_mb` |
| `tests/test_mbs308_cases.py` | `a7ab89166ed8` | + 3 tests; the planted evidence and rule-input helpers carry a planted report |
| `tests/test_mbs308_disk.py` | `9763a4a197ed` | + 1 test |
| `tests/test_mbs308_qualify.py` | `8f4ecd1101fc` | + 1 test |
| `tests/test_mbs308_state.py` | `9b51122d7009` | + 1 test |
| `tests/test_mbs308_mutants.py` | `edea22bda2a6` | + 15 mutants (MB110-MB118, MD41-MD43, MM06, MQ49, MQ50); MM01, MM05, MQ24 re-expressed |

Unchanged since the first handback (18.a): `code/mbs308_scratch.py`, `code/mbs308_repin.py`, the configuration,
`tests/mbs308_testlib.py`, `tests/test_mbs308_launch.py`. No helper changed (`mbs308_repin.py helpers`: nothing
stale); `mbs308_repin.py check` passes in the uncommitted worktree (no new hunk). Counts now: launch 13, qualify 29,
disk 30, cases 28, state 56, static 10, crash 50; 297 declared mutants (282 + 15).

**The suites.** First on the follow-up's sandbox commit `b31ee3a0` (2026-10-02 00:21-00:46Z, on AC throughout, these
subsections still a draft): static 10 / 10, launch 13 / 13, qualify 29 / 29, disk 30 / 30, cases 28 / 28, state
56 / 56, crash 50 / 50. Then all seven again on this report as filled (a second sandbox commit; on AC):

| suite | result | peak scratch | seconds |
|---|---|---|---|
| `static` (QS-STATIC) | 10 / 10 | 0.837 GiB | 6 |
| `launch` (QS-LAUNCH; synthetic payloads under launchd, test labels) | 13 / 13 | 0.001 GiB | 15 |
| `qualify` (QS-QUALIFY) | 29 / 29 | 0.011 GiB | 26 |
| `disk` (QS-DISK) | 30 / 30 | 2.132 GiB | 224 |
| `cases` (QS-CASES) | 28 / 28 | 0.845 GiB | 167 |
| `state` (QS-STATE) | 56 / 56 | 0.847 GiB | 488 |
| `crash` (QS-CRASH) | 50 / 50 | 0.851 GiB | 851 |
| `static` and `qualify` once more after the rows above were written (third sandbox commit, this report as it stands) | in builder7's handback | | |

No test failed in any of these runs; the suites' result files carry no `error` field.

**The mutant matrix: 297 declared, every one killed by its target's own assertion, on AC power; but in TWO runs, and
why is stated in full.** Run 1 (sandbox commit `b31ee3a0`, 00:46:41-02:09:33Z): the unmutated code passed all 134
target tests (00:46-01:17Z), then the mutants ran. **At 02:03:51Z the host went onto battery** (the power log's first
battery entry; its last AC entry before that is 01:55:22Z; AC returned at 02:26:52Z; an external event, not mine: the
lid stayed open and the log has no Sleep, Wake or DarkWake entry). On battery the synthetic executions refuse
(HOST_NOT_ON_AC) and a measurement's host provenance is not CLEAN, so a target can fail for that reason alone. Run 1
shows it: five mutants (M68, M69, M70, M71, M73) were "killed" by an ERROR (their baseline execution refused), and the
kills after the switch cannot be trusted even where no `error` field shows. **I therefore discarded from run 1 every
mutant whose result was written at or after 01:55:00Z, 93 mutants, without looking at which of them "passed", and
kept the 204 written before**, each killed by assertion (`test_passed` false, exit 1, result verified, no `error`
field). Run 2 (the same sandbox commit, 02:27:22-02:49:40Z, on AC from start to end by the power log and by a reading
at both ends): the 93 discarded mutants again, with their 39 unmutated targets: **93 / 93 killed by assertion**, no
`error` field, 39 / 39 unmutated targets pass. Together 297 / 297 by assertion; no survivor, none not run, no invalid
mutant, no timeout. Disk checks: 432 / 432 (run 1) and 133 / 133 (run 2) pass against 7 GiB; every phase was cleaned
after its verified result; peak scratch 1.439 GiB (run 1), 0.994 GiB (run 2). The per-mutant result files of both
runs are kept with the two matrix reports. The suites above were all run before the switch (first set) or after AC
had returned (the other two), none on battery.

**Negative controls** (18.e) run again on the follow-up's sandbox commit, on AC: N1, N2a, N2b, N2c and N3 each fail
their test by assertion, as before.

**P_max and B on the follow-up bytes** (the same meter): QS-DISK's peak 2110 MiB (2.060 GiB) in the first run and
2183 MiB (2.132 GiB) in the second (it was 2185 and 2155 MiB in 18.f; the new test adds a sparse sandbox, no larger moment); the
rebuilt base store 459 MiB. roundup_GiB(2 x (2185 + 459) MiB + 1024 MiB) = 7 GiB still holds with the largest
figures; nothing edited.

### 18.j Integrity, ledger and exposure of the follow-up

* **New cell-308 target evaluations: 0. No science of any kind.** The new science-phase tests run recorders in the
  place of every decoy, in a child process in which the qualified-worktree check is planted and the real launch
  paths (`official_decoy`, the measurement tool's `run_decoy` and `run_under_launchd`) are replaced by functions that
  refuse; the reports show that none of them was reached. Cells 305-309, the band and its mirror, cell 309: untouched.
* **Real repositories: no git write.** HEAD is still 78a172cf; eighteen files are modified, all inside the namespace,
  none added or deleted (the three more than in 18.g: `code/mbs308_derive.py`, `code/mbs308_measure.py`,
  `tests/test_mbs308_cases.py`); no ref under `refs/p5y-k5-cell308-mbs-r1/`; no `evidence_prefreeze/`,
  `qualification/`, manifest, grant, marker or seal. Sections 1 to 17 of this report are byte-identical to 78a172cf's.
  Outside the worktree and my scratch I wrote only my ledger lines.
* **Host.** The battery interval 02:03:51-02:26:52Z is described in 18.i; apart from it the host was on AC at every
  reading and every power-log entry of my follow-up window (00:15-02:50Z and the last runs after it), the lid open, no
  Sleep / Wake / DarkWake entry; no system setting changed. The power log was read by entry type and power source
  only, for 2026-10-02 00:15-03:30Z. Launchd: synthetic payloads under the test prefix only, each booted out; no
  rebaseguard job and no plist left.
* **Pre-final runs of the follow-up, disclosed:** the new and the affected tests (qualify, static and cases in full;
  the new disk and state tests) and 20 mutants ran in the worktree before the final clone was made; no code changed
  after them. They are not reported as results.
* **Ledger** (agent `builder7`, target_evaluations 0, no LEAK_FLAG): the six lines of 18.g and, for the follow-up,
  2026-10-02T00:20:55Z INFRASTRUCTURE and 00:20:55Z SYNTHETIC_VALIDATION, and a closing INFRASTRUCTURE line written
  with this subsection (its time is in builder7's handback).
* **Exposure.** Unchanged from 18.g: nothing new reached me in the follow-up. The coordinator's follow-up message
  carried no MB r1 run observation; I opened no MBS-2 file, no owner record and ran no `git log`. The research
  ledger file was only appended to through `log_event` and its `builder7` lines read back.
* **Scratch.** My sandbox clones, scratch trees and base store are deleted at the end; the JSON reports (both matrix
  reports included), logs, edit scripts and the negative-control script stay in `scratchpad/builder7`.
