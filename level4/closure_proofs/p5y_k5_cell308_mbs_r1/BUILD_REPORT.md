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
