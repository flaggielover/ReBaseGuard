# Independent review of the MB308 execution-interruption recovery assessment (reviewer reviewINT)
RECOVERY_ASSESSMENT_REJECTED

Rejected **as submitted**, on the factual record only. Every operative answer of the assessment (A–E) is
independently confirmed: the target is consumed, no evidence was persisted, `seal-only` has nothing to seal,
re-execution is forbidden, and the frozen outcome is CELL308_EXECUTION_INDETERMINATE with cell 308 OPEN. The
rejection is about the timeline. The logs establish a user **Force Quit of the Claude desktop app at 23:29:00 JST**,
which killed the launcher's and the driver's own `caffeinate` processes and left the run orphaned. The assessment
omits this event, says that interval "is not established", misdates the last power-log entry, and carries the gap
into its title, its ledger line and the proposed formal `postexec/` record. A corrected addendum and a short delta
review (conditions C1–C6) are enough; nothing about the outcome needs to change.

## 0. Basis and method

* Documents reviewed:
  * the assessment `audit/EXECUTION_INTERRUPTION_ASSESSMENT.md`, blob `7e9a0a82…`, research commit `8b64d989`;
  * its ledger line (utc 2026-09-29T15:22:45Z);
  * brief 24;
  * the frozen protocol r3 §4, §7, §8, §10 and §14;
  * the driver `mb308_driver.py` (sha256 `411252b2…`): its docstring and exit codes, `run_execute`, `after_marker`,
    `persist_pending`, `persist_emergency`, `seal_blob`, `materialize`, `run_seal_only`, `check_seal_preconditions`,
    `check_not_evaluated`, `check_governance_state`, `keep_awake`, `close_host` and `main`;
  * `mb308_host.py`;
  * the grant `MB308_GRANT.json`;
  * the qualification review (E1–E8, N1–N8);
  * the r5 file that `check_governance_state` reads.
* **Read-only throughout.**
  * No driver mode was run, and no ref, index or object was written.
  * Every git status in the formal worktree used `GIT_OPTIONAL_LOCKS=0 --no-optional-locks`.
  * Nothing was written in `/Users/suzhe/ReBaseGuard-c308mb`.
* **Object contents.** The only objects created after the marker are the 12 objects of the research commit that
  carries the assessment (§2). For those I report type and size only. The two pre-marker probe objects were verified
  by **recomputing their ids**, never by reading them.
* **System sources, all read-only.**
  * `sysctl kern.boottime`, `ps`.
  * `/usr/bin/log show`. Note: in zsh the bare word `log` is a shell builtin; the brief's command only works as
    `/usr/bin/log`.
  * `pmset -g log`.
  * `/Library/Logs/DiagnosticReports`.
  * The system powerlog database `/private/var/db/powerlog/Library/BatteryLife/CurrentPowerlog.PLSQL`, opened with
    stdlib `sqlite3` in `mode=ro&immutable=1`. Only per-coalition CPU time and boolean existence queries were run.
* **Nothing computed for cells 305–309, and no drift evaluated.**
  * The only data about the run's computation that I read is aggregate CPU seconds per 20–60 s interval for the
    app coalition that contained the run.
  * I read no job timings, job names, statuses or values.
* **Timezones.** Times are JST (+0900), with UTC in brackets where it matters. `log show --style syslog` printed
  +0900 for ordinary entries and +0000 for early-boot kernel entries; every timestamp carries its offset, so nothing
  is ambiguous.

## 1. Marker, HEAD, namespace, chain, frozen hashes: PASS

* **The marker.**
  * `refs/p5y-k5-cell308-mb-r1/target-consumed` is a loose ref (41 bytes).
  * It points to `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` (a commit, the grant).
  * mtime and birth 2026-09-29 20:58:01.004 JST (epoch 1790683081.004).
  * It is the **only** ref under `refs/p5y-k5-cell308-mb-r1/`. `packed-refs` has no entry for the prefix, and its
    mtime is 2026-09-29 01:10.
  * There is no reflog for the prefix.
* **Formal worktree.**
  * HEAD is `afa93072…` on `refs/heads/p5y-k5-cell308-mb-r1`.
  * `status --porcelain --ignored --untracked-files=all` is empty, both for the whole tree and for the namespace.
  * The namespace directory's mtime is 20:47:08, the grant commit's time. So `evidence/` was never created and
    removed after the grant.
* **The chain is unchanged.**
  * `HEAD^` = `47bb37c7` changes only the review. `HEAD^^` = `7eb057bb` changes only qualification files.
    `HEAD^^^` = `c46434a3`, which is also the last commit touching the frozen directories.
  * The grant binds this chain, the driver sha256 `411252b2…` and the manifest sha256 `8799cdac…`. Both match the
    bytes on disk.
* **The frozen hashes still match.**
  * All 21 `frozen_files` of `MB308_FREEZE.json` match.
  * All 54 `external_files` match.
  * The driver and all 7 helpers match.
  * The frozen directories hold no file outside the manifest except the manifest itself.
  * `main` is unchanged at `c123b9bb`.

## 2. No persisted evidence; object store; probe objects: PASS WITH NOTE

* **No persisted evidence.**
  * `refs/p5y-k5-cell308-mb-r1/pending-result` is absent.
  * `mb308-cell308-emergency-result.json` is absent from the worktree git dir. A filesystem-wide `find` for that name
    returned nothing.
  * `evidence/` is absent, so there is no result file.
* **Object store.** Every file under `.git/objects` newer than 20:45 JST:
  * 7 objects at 20:47:08 (the grant commit) and 7 at 20:48:42 (research `c6c7cbe4`), all before launch;
  * the two probe objects at 20:58:00;
  * 12 objects at 2026-09-30 00:24:05. These are exactly the set
    `git rev-list --objects c6c7cbe4..8b64d989`, i.e. the research commit carrying this assessment: 1 commit
    (725 B), 7 trees (241–7869 B) and 4 blobs (3198, 5882, 9314 and 105501 B). The 105501 B blob is the ledger,
    whose size equals the worktree file.
  * **No object was written between the marker (20:58:01) and the reboot.** No pack was written after 2026-09-29
    01:10. There are no `tmp_obj_*` or `incoming-*` files and no alternates.
* **The two 20:58:00 objects.**
  * `a1995184cdbcf51f5e1885873958a5168fbd5f69` (blob, 31 B, birth 20:58:00.589). Its id equals
    `git_blob_id(b"mb308 object-store write probe\n")` recomputed from `check_seal_preconditions`: the 31-byte
    frozen probe.
  * `501388e2a1c285bc4a71524be79e36ddc1a1a8c5` (commit, 253 B, birth 20:58:00.632). I reconstructed its id without
    reading it, from these inputs:
    * tree = `afa93072^{tree}`;
    * parent `afa93072`;
    * the configured author and committer identity;
    * time 1790683080 +0900;
    * the frozen message "mb308 trial commit object (never referenced)".

    The recomputed sha1 matches exactly, at 253 bytes. It is the driver's pre-marker trial commit.
  * Both objects precede the marker by 0.42 s and 0.37 s. That matches the driver's order: probe, trial commit, …,
    marker.
* **Note N1.** The assessment's sentence "the only objects written after launch are the two pre-marker probes" was
  true when written, but it is no longer literally true: its own commit added 12 objects at 00:24:05. The
  successor text should say "apart from the research commit carrying this assessment".
* **Note N2.** The formal worktree git dir changed its directory mtime at 2026-09-30 00:16:57. No entry was added:
  its eight entries are all older than the launch, and the index mtime is still 20:49:30. This is the signature of a
  transient `index.lock` from a post-reboot `git status` run without `--no-optional-locks`. It is harmless, but it
  is a write in the git dir of the qualified worktree. Future read-only audits there should use
  `GIT_OPTIONAL_LOCKS=0`.

## 3. No MB308 process alive: PASS

* `ps -axo` shows no `mb308`, `python3.14 … mb308_driver`, multiprocessing, `resource_tracker` or `caffeinate`
  process.
* The only Python processes are post-boot, unrelated daemons:
  * a `hermes-agent` gateway (00:01:13);
  * the two rebaseguard MCP servers (00:04:07, 00:10:24).
* `kern.boottime` is 1790694015 = 2026-09-30 00:00:15 JST (15:00:15Z).

## 4. The reset, and what the logs show before it: PASS on the reset; FAIL on the account of 23:10–23:41

### 4a. The reset itself (confirmed)

* **Boot.** `kern.boottime` is 00:00:15 JST.
* **PMU fault.** The kernel boot log reads, at 15:00:26.340842Z: `(AppleSPMIPMU) pmu fault log: rst
  btn_rst,btn_seq_reset`. The next line reads `pmu o2ws: 34 00 ( gcb_wakeup auto_wakeup gcb_crash_wakeup)`. I do
  not interpret that second line, and the assessment does not mention it. The fault string is consistent with a
  forced reset by a long press of the power button.
* **No orderly event.** Between the launch and the boot, `pmset -g log` has only `Assertions` entries. There is no
  Sleep, Wake, DarkWake, Shutdown or Restart entry. The first non-assertion entry is `2026-09-30 00:00:42 Start
  powerd process is started`.
* **No crash report.** `/Library/Logs/DiagnosticReports` has no panic, watchdog or jetsam report for 2026-09-29
  after 19:34.
* **Last unified-log entry.** 23:41:09.965 JST (14:41:09Z), from `corebrightnessd`. This matches the assessment.
* **Last power-log entry.** **23:40:35 JST** (`cloudd Released SystemIsActive`), after entries at 23:39:06 and
  23:40:29. It is **not** 23:38:46 as the assessment states: 23:38:46 is only the last periodic `Summary` block.
* **Lid and power.** The powerd `com.apple.powermanagement.lidopen` assertion had been held for 09:56:43 at 23:38:46.
  So the lid was open continuously from about 13:42 until at least 23:38. The power log shows no transition to
  battery.
* **Pre-marker conditions proven by the marker.** The marker exists, and `run_execute` creates it only after the
  following have passed: `require_ac`, `check_clean`, `check_grant`, the pins, the governance state,
  `check_seal_preconditions`, and both controls (a failing control gives a sealed CONTROL_FAILED and no marker). So
  AC at launch, a clean tree and passing controls are established by the marker, independently of the lost launcher
  record.
* **Thermal pressure.** The OS thermal-pressure context was 0 from 20:53:58 until 20:58:03 (then 1). That is
  consistent with the lost launcher record of level 0 at launch.

### 4b. What the assessment missed: a Force Quit at 23:29:00 JST (14:29:00Z)

These are verbatim log facts, and all of them are reproducible with `/usr/bin/log show --start '2026-09-29 23:28:40'
--end '2026-09-29 23:29:20'` and `pmset -g log`.

* **The Force Quit.**
  * 23:29:00.047495, `loginwindow`: `Forcequit confirmed, quitting app(s)`, then `-[Application
    terminateAppAndSubprocesses] | enter`.
  * 23:29:00.050119: `Claude [97329] force quit (caller responsible for termination)`.
  * This is the user's Force Quit dialog acting on the Claude desktop app. The app hosted the Claude Code session
    that ran the one-shot launcher.
* **The app and its helpers die.**
  * 23:29:00.211257, `launchd`: the Claude desktop app `[97329] exited due to SIGTERM | sent by loginwindow[402]`.
  * Its helpers and its process-scoped `Virtualization.VirtualMachine` service exit at the same moment.
  * A Claude Code process logs "Entering exit handler" at 23:29:00.107.
* **Both caffeinate processes of the run die.**
  * 23:29:00.097 / .098: `caffeinate` **56680** "termination reported by proc_exit" and powerd `ClientDied
    PreventUserIdleSystemSleep … age:02:31:01`. It had been created at 20:57:59, the same second as the driver (the
    assessment's driver pid is 56681). It is the launcher's `caffeinate -i` wrapper.
  * 23:29:00.160 / .165: `caffeinate` **56814** "termination reported by proc_exit" and powerd `ClientDied` for
    `PreventUserIdleSystemSleep`, `PreventSystemSleep` and `PreventDiskIdle`, `age:02:30:59`. It was created
    20:58:00, i.e. it is the driver's own `keep_awake()` (`caffeinate -i -m -s -w <driver pid>`).
  * **From 23:29:00 the run had no sleep prevention at all, and its launcher and parent session were gone.**
* **The computation continued after the Force Quit.** Evidence from the system powerlog, per-coalition CPU time:
  * The Claude desktop app's coalition (LaunchdCoalitionId 44227) carried the whole run, about 4.5–4.8 cores
    throughout (about 290 CPU-s per 60 s).
  * It **kept the same load after 23:29:00**: 4.2–4.8 cores in every interval from 23:29:14 to the last recorded
    interval (23:39:54–23:40:48, 4.77 cores). The only exceptions are two short intervals at 2.9 and 4.0.
  * Over 23:29–23:40 the coalition used 3069 CPU-s, against 192 for WindowServer.
  * The OS thermal-pressure context stayed at level 2 from 20:59:17 with **no transition until the reboot**. On that
    day, transitions down from 2 are otherwise logged within minutes of a load ending.
  * A steady load of more than 4 cores is Stage-1 pool workers. Stage 2 and the seal run in the single driver
    process.
  * This is consistent with the frozen code. After the marker the driver ignores SIGINT, SIGTERM, SIGHUP and SIGQUIT
    (`run_execute`), and so does every worker (`_worker_init`). A SIGTERM-class termination of the app's subprocesses
    therefore kills `caffeinate`, which does not ignore it, and leaves the driver and the workers running.
* **Assessment of the evidence.**
  * Established:
    * the Force Quit and the deaths of both `caffeinate` processes at 23:29:00;
    * Stage-1 pool load continuing until at least 23:40:48.
  * Most probable, but not proven: the driver itself survived as an orphan until the host stopped responding
    (about 23:41) and was reset at 00:00:15. The powerlog's per-process tables end at 23:12:25, so no process-level
    record exists for 23:29–00:00. And orphaned workers could in principle finish their current jobs without a live
    parent.
  * Either way, the Stage-1 computation was still in progress at 23:40:48. That supports the assessment's
    "mid-Stage-1". It also excludes an earlier exit of the driver through `after_marker`, which would have written a
    pending blob, an emergency file, or printed CONSUMED_UNRECORDED and stopped the load.
* **Other recorded host facts in the window.** Recorded only; I do not claim any of them as a cause.
  * `ReportMemoryException` ran from about 23:27:44 to 23:28:48. I did not identify its subject.
  * A system memory-pressure **warning** (not critical) was broadcast at 23:33:31.
  * Heavy Bluetooth and audio-accessory activity began at 23:40 (31 043 log lines in that minute, 10 674 of them
    from bluetoothd).
  * Before the silence, the last logs show the display awake and a user present: an `apsd` policy with
    `clamshelled: NO, inFullWake: YES`, and brightness updates.
  * The cause of the unresponsiveness after 23:41:09 is **not established**. The assessment is right about that,
    and I add nothing to it.

### 4c. Consequence for the assessment

* **What stands.** The reset is correctly evidenced, and it is the most probable **final** terminator of the driver.
* **What is wrong.**
  * §1's timeline jumps from "23:10 … the same process tree alive" to "23:41:09 last entry" without the Force Quit.
    That Force Quit ended the run's sleep prevention, its launcher and its parent session 31 minutes before the
    reset.
  * §6's "What happened between 23:10 and 23:41 … is not established" is therefore **partly wrong**: the Force Quit
    and its effects are established from the logs.
  * §2's "caffeinate … all gone" is true, but for the caffeinates the cause is the Force Quit, not the reset.
  * The power-log end time is misstated.
* **Why it matters even though the outcome does not change.** Under E3 and protocol §14, host events never change the
  status or the outcome, and the outcome does not change here. But E6 obliges disclosure of `caffeinate_pid` and of
  the host record. With no sealed record, that disclosure can only come from the recovery record. That record may
  not omit a logged event that removed the run's sleep prevention and orphaned it.
* **Honest attribution.** The honest description is: "the one granted evaluation was orphaned by a user Force Quit
  of the hosting Claude desktop app at 23:29:00 JST (its caffeinate processes died; Stage-1 load continued at least
  until 23:40:48); the host stopped logging at 23:41:09 and was force-reset by the power button at 00:00:15; no
  evidence was ever persisted". "Interrupted by a host hard reset", alone, is incomplete.

## 5. Frozen semantics: PASS WITH NOTE

* **CELL308_EXECUTION_INDETERMINATE is entailed.**
  * Protocol §8's third row reads: "INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6 refusal, TARGET_EVALUATION_FAILED,
    POST_MARKER_RECORDING_FAILED, unsealable | any post-marker failure | CELL308_EXECUTION_INDETERMINATE (target
    consumed; no rerun)".
  * The marker exists (the target is consumed), and no sealed status exists or can exist ("unsealable").
  * §4 classes "worker death … and signals" as execution failures (INDETERMINATE). §14 and E3 say that host events
    never change the status, the outcome or exactly-once.
  * This holds whatever the terminator was: the Force Quit, the reset, or both.
* **`seal-only` is inapplicable, and it never computes.** `run_seal_only` proceeds as follows:
  * it checks the flags and the identity;
  * it reads `PENDING_REF`, which is absent, and `git_dir()/EMERGENCY_NAME`, which is absent;
  * `if not pending: raise Refusal("SEAL_ONLY", "no persisted evidence (no pending ref, no emergency file)")`;
  * `main` maps that to `MB308 REFUSED`, exit 2.

  It computes nothing, but it has nothing to seal. Not running it is correct.
* **Re-execution is forbidden and mechanically refused.**
  * `run_execute` → `check_not_evaluated` refuses with `CONSUMED` as soon as any ref exists under
    `refs/p5y-k5-cell308-mb-r1/`. This happens before any evaluation, and the marker CAS (`update-ref … 0{40}`) would
    fail as well.
  * `preflight` and `rehearse` also refuse with `CONSUMED`.
  * `decoy` accepts only 297 and 316 and guards the band.
  * The grant ("No re-run"), §8 ("no rerun"), the docstring ("NEVER run execute again") and E7 all forbid it.
* **No resume or recovery path exists in the frozen code.**
  * Stage-1 results live only in the driver's memory (`results` in `stage1`).
  * The formal guard's `log_execution` refuses unconditionally, so no pinned module writes a file. The only file
    writer in the pinned C1b code, `c1b_certpw.run_point`, is not on the formal path (D3 uses `certify_degree`).
  * `mb308_host` writes nothing.
  * The only persistence channels are `persist_pending` and `persist_emergency`, both inside `after_marker` after
    `evaluator()` returns or raises. Neither was reached.
  * No checkpoint, cache or partial record exists to resume from. None was found on disk.
* **Note N3: CONSUMED_UNRECORDED is the driver's exit code 6.** The driver prints it only when both channels fail
  inside `after_marker`, and it never got there: it was killed. No exit code exists. The label may be used for the
  **state** ("marker present, no evidence channel holds anything"), and the assessment does so. The formal record
  should say "state equivalent to CONSUMED_UNRECORDED; the driver never returned" and must not record "exit 6".
* **Note N4: answer C's inference.** "No persisted object ⇒ died before the boundary" leaves open, on its own, that
  the boundary was reached and both channels failed. The coalition-CPU evidence of §4b closes that gap: Stage-1 load
  continued to 23:40:48.

## 6. Status claims and the ledger line: PASS WITH NOTE

* **Cell 308 is OPEN.** No sealed status, no Γ and no mechanical outcome other than the frozen INDETERMINATE exist.
  INDETERMINATE is neither CLOSED nor NOT_CLOSED. There is no scientific positive or negative conclusion.
* **r5 is unchanged.** The pinned `K5_COVERAGE_MAP_R5.json` has sha256 `e2197051…` and blob `f978eeb6b411…` at HEAD.
  In it:
  * `K5_COVERAGE_COMPLETE` is false;
  * `union_open_ranges` is `[[306, 309]]`;
  * none of 306–309 is PASS.

  That is exactly `check_governance_state`'s test.
* **No r6 exists.** There is no `K5_COVERAGE_MAP_R6` in either HEAD tree, in `git log --all`, or on disk in the three
  worktrees.
* **K5 and P5Y are unaffected.** K5 stays PARTIAL, and `main` is unchanged.
* **TARGET_EVALUATION_COUNT = 1 is correct.** The one granted evaluation began after the marker, was consumed and was
  never recorded.
* **The ledger line.**
  * Class `INCIDENT` is a valid `KNOWN_CLASSES` member. The research quarantine has no TARGET_EXECUTION class; the
    307 formal ledger does use `TARGET_EXECUTION`, as the note says.
  * `new_target_evaluations` is 1.
  * `cells_touched` is `[{"cell": 308, "detector": "CUSUM", "m": 5}]`.
  * `LEAK_FLAG` true is automatic (`log_event` sets it whenever target_evaluations > 0), and the note explains it
    honestly.
  * **Defect.** Its `purpose` states the interruption as "a host forced power-button reset … before any evidence was
    persisted" and omits the 23:29:00 Force Quit. The ledger is append-only, so this must be corrected by a new
    supplementary line (C3), never by editing.

## 7. Timeline, losses and unknowns: FAIL

* **Accurate.**
  * Launch 20:57:58 and driver start 20:57:59. The caffeinate wrapper was also created at 20:57:59.
  * Probes 20:58:00, marker 20:58:01, last unified-log entry 23:41:09.
  * Boot 00:00:15 with the PMU `btn_rst,btn_seq_reset`, and no orderly sleep, shutdown or restart.
  * EVAL_CAP (8 h) not reached.
  * "Mid-Stage-1" is consistent. §4b's evidence strengthens it: pool load at 23:40:48.
  * The projection of 17 546 s is Q12's official re-derivation (qualification review N7). The frozen §3.2 projection
    is 13 110.8 s. Both place the run inside Stage 1, and EVAL_CAP is unaffected.
* **Losses confirmed.**
  * `/private/tmp` was recreated at boot (birth 00:00:36). No entry under it predates the boot.
  * So the launcher log, the execution log and the host-readings file are gone.
  * The launcher's host readings now exist only in the coordinator's session transcript. I could not verify them,
    and the record must label them "coordinator-reported". AC at launch and passing pre-marker checks are, however,
    proven by the marker (§4a).
* **Inaccurate or incomplete.**
  * (i) The 23:29:00 Force Quit, with the deaths of both caffeinates and the orphaning of the run, is missing
    (§4b).
  * (ii) The power log's last entry is 23:40:35, not 23:38:46.
  * (iii) "What happened between 23:10 and 23:41 … is not established" is overstated. The Force Quit and its effects
    are established. Only the cause of the unresponsiveness after 23:41:09, and the exact moment the driver died,
    remain unknown.
  * (iv) The title and §1 present the reset as the interruption. The record should say the run was first orphaned
    (23:29:00) and then ended at the latest by the reset.
* **Not overstated.** The assessment does not claim to know the cause of the hang, and it says the E2 conditions
  change nothing (E3). Both are correct.

## 8. Ruling on the §7 proposal (formal `postexec/` record; §10 steps 6–8)

### 8a. The postexec record

The postexec record is **approved in principle, after C1–C2**. It must follow the cell-307 precedent: an additive
`postexec/` directory holding a launch time, a stdout record, a checks JSON and a checks script. `postexec` is one of
the driver's `POST_FREEZE_DIRS`.

**Form of the commit.**
* One commit on `p5y-k5-cell308-mb-r1`, a direct child of `afa93072`.
* It adds files only under `level4/closure_proofs/p5y_k5_cell308_mb_r1/postexec/`.
* It changes nothing in `code/`, `protocol/`, `theory/`, `tests/`, `config/`, `errata/`, `evidence_prefreeze/`,
  `qualification/`, `review/` or `authorization/`.
* It never creates `evidence/`, `evidence/execution/` or anything at a `GUARDED_PATHS` name.
* It never touches `refs/p5y-k5-cell308-mb-r1/*`. The marker stays at the grant; only the branch head moves.

**It MAY contain:**
* the launch UTC 2026-09-29T11:57:58Z and the marker time 11:58:01Z (ref-file birth);
* the post-reboot state:
  * the marker ref and its target;
  * the absence of the pending ref, the emergency file, `evidence/` and the result;
  * the object-store statement "no object between the marker and the reboot", with the two probe ids, their
    types and sizes, and the recomputations;
* the host facts of this review's §4:
  * boot time and PMU string;
  * no sleep, shutdown or restart entry;
  * last log entries;
  * the Force Quit and the two caffeinate `ClientDied` entries;
  * a **qualitative** statement that the pool load continued until at least 23:40:48 (no per-interval series is
    needed);
* the loss of the `/private/tmp` logs, with the launcher readings marked "coordinator-reported, unverifiable";
* references (path, commit, sha256) to the assessment, its addendum, this review, the delta review, and their
  ledger lines;
* TARGET_EVALUATION_COUNT 1;
* the frozen outcome CELL308_EXECUTION_INDETERMINATE, with the §8 row quoted verbatim and "no sealed status exists
  (unsealable); state equivalent to CONSUMED_UNRECORDED; the driver never returned";
* the status lines: cell 308 OPEN; r5 authoritative and unchanged; no r6; K5 PARTIAL; P5Y unchanged; route MB r1's
  single authorization exhausted.

**It MAY NOT contain:**
* any target value, bound, U, Γ, P or S, or any partial, estimated or reconstructed quantity;
* any job-level information about the target run: job names, rungs, statuses, counts, timings, progress fractions,
  or which blocks had finished;
* any decoy, validation-drift or qualification value next to a cell-308 quantity (E8);
* any claim of a seal, a sealed status or an exit code;
* the driver's result schema string, or a file named like `MB308_CELL308_RESULT*`;
* any proposal or mechanism to resume, re-run, re-grant or recompute;
* any causal claim beyond the evidence. In particular, the cause of the 23:41 unresponsiveness is "unknown", and the
  moment of the driver's death is "after 23:29:00 (most probably) and at the latest 00:00:15";
* any unverified launcher reading presented as a fact.

**A checks script, if one is included:**
* it uses stdlib and git plumbing only, read-only;
* it does **not** import any campaign module (`mb308_*`) or pinned certifier, and it does not arm the guard (E7);
* it writes only its own JSON.

### 8b. Protocol §10 steps 6–8: they must run

**Ruling.** §10 steps 6–8 **should run** on that record, in adapted form. The reviewed assessment does not suffice.

**Why.**
* §8's conclusions are defined as "applied verbatim **by the adjudication**".
* §10 has no exception for an unsealed execution.
* Skipping steps 6–8 would silently narrow a frozen gate. Running them costs little and changes nothing in the
  outcome.

**Step 6: execution review, on the postexec record and the repository state.**
* EXECUTION_ACCEPTED means only that the record is accurate and complete, and that the state is as recorded.
* E4 and E6 items that presuppose a sealed record are reported as "not available: unsealed". Instead, the review
  discloses:
  * the host events: the Force Quit, the loss of caffeinate, and the reset;
  * E1 and E2 compliance as far as it can be assessed, including the other applications active during the run. For
    example, the Claude desktop app's own process-scoped virtual machine ran until 23:29.
* REJECTED ⇒ STOP, and there is still no rerun.

**Step 7: adjudication.** It writes the §8 row verbatim: CELL308_EXECUTION_INDETERMINATE (target consumed; no
rerun). It carries G3's text (grant condition G5) and states no scientific conclusion.

**Step 8: adjudication review.**

Each of these steps needs a fresh reviewer. The user may still decide otherwise, but that decision must be recorded
before the adjudication.

## 9. Other findings

* **Pre-marker checks proven by the marker (strengthens the assessment).** The marker proves that every pre-marker
  refusal passed, including AC, and that both controls passed. So no CONTROL_FAILED path applies.
* **E1 and E2 during the run** (for the execution review).
  * Other interactive and agent applications were active: ChatGPT, Codex, Chrome, Safari, Perplexity and a second
    Claude app coalition. Their CPU was small next to the run's (for example 23:29–23:40: WindowServer 192 CPU-s,
    Codex 30 CPU-s, against 3069 for the run's coalition).
  * The coordinator ran a read-only audit at 23:10, during the evaluation (as the assessment reports; not
    otherwise verifiable).
  * The hosting app hung or was force-quit by the user.
  * By E3 none of this changes the outcome. It must be disclosed, not judged.
* **Operational lesson (not a defect of the frozen design).**
  * A multi-hour exactly-once run was launched as a subprocess of an interactive desktop app. A user Force Quit of
    that app killed the launcher and every `caffeinate`.
  * The driver's post-marker signal immunity (SIG_IGN for INT/TERM/HUP/QUIT) most probably kept the computation
    alive, but it could not keep its sleep prevention or its launcher alive.
  * Any successor campaign should launch detached from any GUI app (for example under a `launchd` job or `nohup`
    + `setsid` from a terminal session), with the logs outside `/private/tmp`, so that neither a Force Quit nor a
    reboot erases them.
* **Brief errata** (for the record, no effect).
  * `log` is a zsh builtin, so `/usr/bin/log` is required.
  * `log show --style syslog` prints the local offset (+0900) for ordinary entries, not UTC.
* **Scratch files.** This review's scratch files (log extracts, power-log text, boolean or aggregate powerlog
  queries) contain no target quantity.

## CONDITIONS

* **C1. Addendum A1 to the assessment.** It goes in the research branch. The assessment file stays byte-unchanged,
  following the `INCIDENT_AUDIT_MB308_ADDENDUM_A1` pattern. A1 corrects:
  * (a) The timeline gains the 23:29:00 JST Force Quit: loginwindow `Forcequit confirmed` /
    `terminateAppAndSubprocesses`, Claude [97329] exited on SIGTERM. It also gains the `ClientDied` of caffeinate
    56680 (launcher) and 56814 (driver `keep_awake`), and the qualitative fact that the Stage-1 pool load continued
    until at least 23:40:48.
  * (b) The power log's last entry is 23:40:35, not 23:38:46.
  * (c) The phrase "23:10–23:41 not established" is replaced by the actual unknowns: the exact moment the driver
    died (after 23:29:00, most probably; at the latest 00:00:15) and the cause of the unresponsiveness after
    23:41:09.
  * (d) The title and §1 are restated: the run was orphaned at 23:29:00 and ended at the latest by the forced reset.
  * (e) The object-store sentence gets N1's qualifier.
  * (f) CONSUMED_UNRECORDED is described as a state, not an exit code (N3).
  * (g) The launcher readings are labelled "coordinator-reported".

  A1 changes none of the answers A–E, the outcome or the status lines.
* **C2. A delta review of A1 only**, before any formal commit. This reviewer, resumed, or a fresh one. Line 2 must be
  DELTA_ACCEPTED or DELTA_REJECTED. No formal `postexec/` commit before DELTA_ACCEPTED.
* **C3. One supplementary research-ledger line.** It uses class INCIDENT, **`new_target_evaluations` 0** (the count
  stays 1, carried by the 15:22:45Z line) and `cells_touched` empty. Its notes carry the corrected account
  (C1(a)–(d)) and cross-reference the 15:22:45Z line. The existing line is never edited.
* **C4. The formal `postexec/` record** is exactly as §8a allows: its shape, what it may contain and what it may not.
* **C5. §10 steps 6–8 run on the postexec record** as §8b rules, each with a fresh reviewer, unless the user records
  a different decision before the adjudication. Whatever their verdicts, there is no rerun.
* **C6. Standing prohibitions**, repeated because they bind every next step:
  * no `execute`, and no `seal-only` (there is nothing to seal);
  * no change to, and never a deletion of, any ref under `refs/p5y-k5-cell308-mb-r1/`;
  * no new grant, rerun, resumption or recomputation of cell 308 under route MB r1. Lost information is recomputed
    only through a new independent governance process and a new user decision (E7);
  * no proxy or reconstruction of any target quantity;
  * r5 stays authoritative, with no r6;
  * read-only audits of the formal worktree use `GIT_OPTIONAL_LOCKS=0`.

## NOTES

* **N1** (§2). The assessment's commit wrote 12 objects after the marker. They are type- and size-accounted, and none
  is a result object.
* **N2** (§2). There was a post-reboot transient lock in the formal worktree git dir (dir mtime 00:16:57). No lasting
  change.
* **N3** (§5). CONSUMED_UNRECORDED is a state label here. The driver never returned an exit code.
* **N4** (§5). Answer C's inference is completed by the coalition-CPU evidence.
* **N5** (§4a). The PMU line `o2ws: 34 00 (gcb_wakeup auto_wakeup gcb_crash_wakeup)` is recorded but not
  interpreted. No panic or watchdog report exists.
* **N6** (§4b, §9). A ReportMemoryException (about 23:27:44–23:28:48, subject unidentified) and a memory-pressure
  warning (23:33:31) are recorded, not claimed as causes.
* **N7** (§9). E1 and E2 cannot be fully assessed without the sealed host record. The execution review must disclose
  the other applications active during the run, the coordinator's 23:10 audit, and the Force Quit.
* **N8** (§9). For any successor, launch detached from GUI apps and keep the logs off `/private/tmp`.
* **N9** (§0, §9). Brief errata: `/usr/bin/log`, and the local-offset printing.

## Verdict and reason

**RECOVERY_ASSESSMENT_REJECTED, as submitted.**

**What I confirm independently.** Every operative conclusion stands, and I verify each one myself:
* the marker names the grant, and nothing else exists under the prefix;
* the chain and the 21 + 54 frozen hashes are intact;
* no pending ref, no emergency file, no `evidence/`, and no object written between the marker and the reboot;
* the two probe objects are the driver's, by recomputed ids;
* no process survives;
* the forced power-button reset is confirmed by `kern.boottime` and the PMU fault log, with no orderly sleep,
  shutdown or restart;
* the frozen protocol and driver entail CELL308_EXECUTION_INDETERMINATE. `seal-only` would refuse. Re-execution is
  refused mechanically and forbidden by the grant, §8, the docstring and E7. No resume path exists;
* cell 308 stays OPEN, r5 is unchanged, there is no r6, K5 and P5Y are unaffected, and the count is 1.

**Why the record cannot be accepted as it stands.** Its factual account is materially incomplete.
* It omits a logged user Force Quit of the hosting Claude desktop app at 23:29:00 JST. That Force Quit killed the
  launcher's `caffeinate` and the driver's own `keep_awake` `caffeinate`, and orphaned the run, which kept computing
  until at least 23:40:48.
* It misdates the power log's end.
* It calls the 23:10–23:41 interval unestablished.
* It carries these gaps into its title, its ledger line and the proposed formal record.

**The remedy.** A recovery record must disclose every logged event that affected the one exactly-once run. E6
requires that disclosure, and there is no sealed record to carry it. The fix is bounded: addendum A1, a delta
review, a supplementary ledger line, then the postexec record, and §10 steps 6–8 as ruled in §8.
