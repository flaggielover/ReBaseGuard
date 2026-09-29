# Cell-308 successor MB-S r1: independent implementation review of the pre-freeze build afba20e5 (reviewIMPL)
IMPLEMENTATION_REJECTED

Reviewer: reviewIMPL (fresh; wrote and reviewed none of the build). Started 2026-09-29T21:09:18Z.
Object under review: successor worktree `/Users/suzhe/ReBaseGuard-c308mbs`, branch `p5y-k5-cell308-mbs-r1`, commit
`afba20e5f05b5615c2c0f42b7bdf8b239ea07a02`, namespace NSS = `level4/closure_proofs/p5y_k5_cell308_mbs_r1`.
New cell-308 target evaluations by this review: 0. No MB r1 driver mode run. No CUSUM m=5 cell 305-309 evaluated.

## Work log (incremental)

* 21:09Z start; read BUILD_REPORT, architecture + A1, conditions register, governance + A1 + E1, route A1 + E1 + E2,
  incident review MB308 C2-C9 (lines 336-392). Did not open any MBS-2 excluded file.
* 21:12Z own base store: `git clone --bare --no-local` of the successor worktree into reviewIMPL scratch
  (`base_store.git`, 466 MB, no alternates); every sandbox of this review borrows from it only (env
  `MBS308_BASE_STORE`, `MBS308_SCRATCH` = reviewIMPL scratch).
* 21:13Z static suite re-run: 9/9 PASS. 21:14Z-21:19Z state suite re-run: 34/34 PASS.
* MB r1 bytes: tree `012e0c29` of NSF identical at 21e99cf0 and afba20e5; `git diff 21e99cf0 afba20e5` touches
  nothing outside NSS; worktree clean (also `--ignored`) for NSF and NSS.
* Science pins: the five science modules, guard and host of MB r1 have the same sha256 at c46434a3, 21e99cf0 and on
  disk, and the same blob at c46434a3 and afba20e5; `SCIENCE_PINS` equals them.
* DRIVER_DIFF completeness: applying the 22 hunks of DRIVER_DIFF.md with `patch` to MB r1's driver at c46434a3
  (sha256 411252b2...) yields exactly `code/mbs308_driver.py` (sha256 7bc2a619...): the diff is complete.
* Independent AST check (own script): 46 top-level defs text-identical; changed: check_not_evaluated,
  check_seal_preconditions, check_grant, serialize, persist_pending, seal_blob, materialize, seal_message,
  fallback_bytes, after_marker, keep_awake, close_host, run_execute, run_seal_only, main; removed persist_emergency;
  24 added. None of the changed defs is science glue. Module-level names used by the identical defs whose binding
  differs: CON, GUARD, HOST, PIN, S1M, SUP, ProcessPoolExecutor, wait, HELPER_SHA256, LINEAGE (the builder's reasoned
  list) plus GUARDED_PATHS, NS_REL, QUALIFIED_BRANCH/GIT_DIR/WORKTREE, used only by identity functions
  (check_identity, check_clean, check_result_paths, freeze_commit), not by science glue.
* Guard: `diff` of mb308_guard.py and mbs308_guard.py is exactly line 40 (CONSUMED_REF); GUARD_DIFF.md is correct.
* 21:19Z-21:26Z crash suite re-run: 36/36 PASS (F1-F12 x exit/kill, S01-S12).
* 21:26Z own experiment `exp_lock.py` (sandbox): stale git ref lockfiles (see DEF-1). 21:27Z launch suite re-run with
  review labels `org.rebaseguard.mbs308.review.20260929T212712` and `...review.20260929T212717Z` (plists and logs in
  reviewIMPL scratch; the wrapper only rewrites the label, the harness path and the harness log dir): 6/6 PASS; both
  jobs booted out, plists removed, `launchctl list` shows no rebaseguard job afterwards.
* 21:28Z mutant matrix re-run started (own base store). 21:31Z own experiment `exp_pins.py` (sandbox): behavioural
  platform / research-pin / science-pin gates.
* 21:30Z object-store scan of the real repository (read-only; loose objects by st_birthtime / st_mtime; packs).

## 1. Scope and boundary (RC1, S11, MBS-9(i)) — PASS

* MB r1 bytes unchanged: PASS (tree `012e0c29` at 21e99cf0 and at afba20e5; nothing outside NSS changed; the worktree
  holds no modified, untracked or ignored object under NSF or NSS).
* Science loaded from MB r1 paths by sha256 and blob, not copied: PASS. `load_science_module` executes the committed
  bytes at `NSF/code/<name>.py` after checking sha256, the git blob of the bytes and the blob at HEAD; `check_science_modules`
  re-checks them (and the loaded module's own pin) at preflight / execute / every resume. NSS carries no copy. Verified
  behaviourally: a one-line change to `mb308_supply.py` in a sandbox makes the driver stop at import with
  `SciencePinError` (nothing runs); restored, `recover` resumes and seals.
* Carried science functions text-identical, with module-level names: PASS (builder's AST tests re-run, and my own
  independent AST script agrees; see the work log). The rebinding of `ProcessPoolExecutor` / `wait` is the one
  lifecycle entry into MB r1's `stage1`; I read `CheckpointingPool` / `checkpointing_wait`: with no context they are
  the originals plus `run_measured` (returns the job's own object unchanged plus ru_maxrss) and the watchdog thread;
  served checkpoints are decoded by a lossless tagged JSON (Fraction, float.hex, tuple, dict pairs in insertion order;
  unknown types refuse at encode, so such a job is simply recomputed). The aggregation in `stage1` indexes `results`
  by (kind, block, rung) in ladder order, so completion order cannot change the output.
* Guard diff: PASS (exactly `CONSUMED_REF`; `log_execution` still refuses; nothing writes into NSF).
* DRIVER_DIFF.md: PASS — complete (patch reproduces the MB-S driver byte for byte) and correctly classified: no hunk
  touches a science-glue function; hunk 10 (`serialize`) is correctly LIFECYCLE (D9, ruled below).

## 2. State machine and recovery — PASS WITH NOTE

* All eight states are produced and classified from refs, spool, journal, process identity (pid + `ps lstart` +
  command sha256 + boot UUID), boot UUID and the current platform readings; `status` prints the name only; the
  classifier is read-only (GIT_OPTIONAL_LOCKS=0, spool opened O_RDONLY, no mkdir, tree listing only). Re-run: state
  34/34, crash 36/36.
* `recover` dispatches exactly `ACTIONS[state]`; `resume` / `close-indeterminate` / `seal-only` re-classify under the
  O_EXCL lock and refuse outside their state (t_no_abandonment, t_computing_then_interrupted).
* Checkpoints are never results: different schema, no `complete`, never read by the classifier, `verify_result`
  requires the result schema + complete + terminal status + cell + grant + driver.
* Mandatory continuation, budget (attempt >= 4 dead -> UNRECORDED), deadline (7 d from marker / intent time),
  two-consecutive-failures: implemented and tested (t_budget_real_resumes drives execute + 3 real resumes).
* `close-indeterminate` is value-free: schema, status, cell, grant commit, driver sha, target_evaluations 1,
  mechanical outcome, classification reason codes, journal seq/attempt/n_ckpt, time, `value_free: true`; spool
  result files are renamed aside unread.
* NOTE (see DEF-1): a stale git ref lockfile produces a state the table does not name (resume refuses, close refuses).
* NOTE: a torn worktree copy (crash inside `materialize`, which writes the final name directly as the design says)
  leaves SEALED with `recover` returning 7 for ever; the sealed blob is safe, but the fix (move the torn copy aside)
  is not a frozen action.

## 3. Persistence (section 3) — PASS

O_CREAT|O_EXCL|O_NOFOLLOW tmp (0600) in `<git dir>/mbs308-spool/`; full write; fsync + F_FULLFSYNC; rename; directory
fsync + F_FULLFSYNC; read-back byte equality + canonical layout + self sha256; journal RESULT_DURABLE (sha only);
`hash-object -w` under `core.fsync=loose-object,reference` with the id verified; pending ref by CAS from zero (or from a
classified stale value, D6); private-index seal commit + branch CAS, entry re-verified; materialization
O_EXCL|O_NOFOLLOW + fsync + read-back. A partial or corrupt file can never be taken as a result: `result.json.tmp` is
never read (`spool_read` raises), `result.json` must be a regular single-link file whose bytes are exactly
`serialize(record)` with a matching self sha256, the result schema, complete, a terminal status, cell 308 and the
marker's grant and granted driver; the pending blob is re-verified by id and content. Tests re-run:
t_persistence_contract (syscall order via wrapped os.open/fsync/rename/fcntl), t_verify_result_units, F5-F7, S05-S09.

## 4. Crash injection (F1-F12 and the simulations) — PASS, but coverage gap (DEF-1)

Re-run 36/36. I read every assertion: each F-case asserts the process really died (signal 9 or exit 86), the
classified state and the recover action against a fixed table, the final state SEALED, the sealed certified bytes
equal to an uninterrupted baseline (the synthetic Stage 2 is an order-sensitive digest of every record, so a lost,
duplicated or reordered record changes it), exactly one marker naming the grant, no recomputation of any job whose
checkpoint existed before `recover` (per-job execution log written by the worker itself), zero new jobs where the
result was already complete (F4-F12), and a renamed-aside tmp for F5-F7. These are not vacuous: the mutant matrix
(section 5) shows the gates they exercise are load-bearing. S01 (7 worker deaths), S02 reboot, S03 stale lock, S04
stale pidfile, S05 corrupt tmp, S06/S07 truncated / wrong-hash result, S08/S09 stale pending, S10 concurrent recover,
S11 memory watchdog, S12 awake-time cap: all meaningful and passing.

**Gap.** Every fault point lies BETWEEN git commands. None interrupts the host inside a `git update-ref` (a reset or
power loss during a ref write, the MB r1 failure class), which can leave `<ref>.lock`. My sandbox experiment
(`exp_lock.py`) shows what follows (DEF-1): with one stale `refs/p5y-k5-cell308-mbs-r1/ckpt.lock`, each of the three
`recover` -> `resume` attempts ends `LOST OWNERSHIP` (rc 9) at its first checkpoint write, nothing new is persisted,
and after the third the state is CONSUMED_UNRECORDED (RESUME_BUDGET_EXHAUSTED) -> INDETERMINATE, although no other
process ever owned the run. With a stale `journal.lock`, `recover` -> resume refuses `RESUME_REFUSED` and
`close-indeterminate` refuses `NO_DISCRETIONARY_ABANDONMENT`: the run is wedged in CONSUMED_INTERRUPTED with no frozen
action (after 7 days it becomes UNRECORDED, but `close-indeterminate` then needs the same journal CAS and fails too).

## 5. Mutants — PASS (with the gap of DEF-4)

Re-run 21:28Z-21:47Z against my own base store: the unmutated code passes all 30 target tests; **33/33 mutants
killed**; I checked every kill in the per-mutant result files: each is an assertion failure of the gate's own test
with specific evidence (e.g. M04-M10: the planted bad checkpoint was accepted, `rejected: []`; M15: a changed boot
UUID still CONSUMED_COMPUTING; M20: the CLI ran with a hook present; M25: an extra MB r1 ref accepted; M26: a
platform mismatch resumed), none by an exception, a timeout or a pin check (the runner re-pins HELPER_SHA256 to the
mutated bytes and refuses a mutant that does not parse or whose fragment is not unique). The MBS-9(iii) set is
complete: job A served as B (M09), wrong grant (M04), wrong driver sha (M05), wrong / future seq (M07), another
attempt (M08), another platform pin (M06), skipped resume-time pin check (M26), checkpoints read after a terminal
state (M28). Supplementary mutants of my own (X2, X3 gap probes; X5, X6 controls): see the work log at the end.

## 6. Detachment (section 5) — PASS WITH NOTE; DEF-2

* Proven by test, not by PPID = 1: the launcher's proof requires not-a-descendant of the launcher's ancestry, a
  different SID and `launchctl print` naming the pid running; `t_ppid1_is_not_detachment` shows an orphan with PPID 1
  in the launcher's session is NOT detached (and M13 is killed). Re-run with my label: job pid = pgid, SID 1, PPID 1,
  XPC_SERVICE_NAME = label, `launched_by_launchd.pass` true.
* Survives the death of the launching process group and session: the test SIGKILLs the launching shell's process
  group and every member of its session; the job's heartbeat keeps advancing and launchd still names it (re-run PASS);
  `t_launcher_death_while_waiting` PASS. (A real Force Quit of the hosting app is not reproducible here; the test is
  the stated analogue.)
* Caffeinate re-spawned: the job's `caffeinate -i -m -s -w <job pid>` killed by SIGKILL is re-spawned with the same
  flags and watched pid; deaths / respawns recorded (re-run PASS; M14 killed).
* Stale pidfile detected: LIVE while the job runs, STALE after it exits (identity = pid + start time + boot UUID +
  command sha256; M22 killed).
* The driver side is strong: `execute` / `resume` require XPC_SERVICE_NAME == label, PPID 1 and `launchctl print`
  naming this pid (D11; M31 killed; `t_execute_refuses_outside_launchd` runs the real check).
* **DEF-2.** `mbs308_launch.wait_and_cleanup` (the default `--wait` path) loops `while launchd_job_pid(label) is not
  None` and then calls `bootout`. `launchd_job_pid` returns None on ANY failed or timed-out (30 s) `launchctl print`
  or an unparsed state, so one transient read failure makes the launcher boot out a live post-marker job (launchd
  SIGTERMs it, the driver ignores SIGTERM, then SIGKILL): an avoidable, launcher-induced interruption that consumes a
  resume. Likewise `launch()` boots the job out on any exception after the bootstrap (including KeyboardInterrupt in
  the launcher). Bootout must require the recorded job identity to be dead (HOST.identity_alive false) and never act
  on a single negative reading; the launcher must never kill a job it cannot prove is still pre-marker.
* NOTE: `mbs308_launch._run` does not catch `subprocess.TimeoutExpired` (preflight timeout 1900 s): the launcher then
  dies with a traceback instead of `LAUNCH REFUSED` (nothing is launched, so harmless).

## 7. Host contract (section 6, S17, GC-10, DR2) — PASS WITH NOTE

* Section 6 gates (AC, lowpowermode 0, thermal 0, disk >= 2 GiB, memory pressure normal, boot UUID, no live campaign
  pidfile, launched by launchd) and DR2(c) (AutomaticallyInstallMacOSUpdates / CriticalUpdateInstall enabled or
  missing refuses): unit-tested on planted readings, each failing reading fails exactly its gate (re-run PASS). Real
  host tonight: all four SoftwareUpdate keys = 1, so `execute` would refuse (the launcher test saw PREFLIGHT_FAILED).
* GC-10 driver gates (free memory >= 2 GiB from vm_stat; exclusivity: no process > 25 % CPU outside this process and
  its direct children and the allow-list): I unit-checked the parsers with planted text (correct; a missing vm_stat key
  fails closed), but NO test or mutant covers them, and every sandbox run stubs the driver's `host_preflight`. Note
  also that "this process tree" is one level deep (grandchildren count as busy; harmless at preflight, when no
  workers exist).
* RC2 platform pin at execute and every resume: behaviourally confirmed by me (planted OS build at `execute` ->
  PLATFORM_PIN_MISMATCH before any ref; a changed pinned research input at resume -> PIN_MISMATCH, attempt not
  moved); at resume via the classifier (t_platform_mismatch_at_resume, M26). The pins equal this host's readings
  (interpreter bd349815..., libpython 34463f1b..., 3.14.5, 25F84, arm64). Only the classifier path has a behavioural
  test; the execute / resume `check_platform`, `check_bindings` and `check_science_modules` refusals are asserted only
  statically (presence of the call).
* Memory watchdog -> recorded execution failure: PASS (S11: a 400 MB job under a 200 MB cap is SIGKILLed, the kill is
  recorded, the attempt seals TARGET_EVALUATION_FAILED -> INDETERMINATE; M27 killed).
* Host provenance never changes the outcome: PASS by reading. After the marker, host readings are only recorded
  (snapshot, sampler, caffeinate record, host log); no branch depends on them. Before the marker and at resume
  (before the attempt counter moves) the gates only refuse. Host conditions can therefore change completion (a
  refused resume ages toward the 7-day deadline; a watchdog or EVAL_CAP hit is INDETERMINATE), never a status of a
  completed evaluation or Γ.

## 8. MBS-3, MBS-12, S15 / GC-8 — PASS WITH NOTE

* MBS-3: `t_no_in_run_observation` captures stdout and stderr of an interrupted execute + its recover and allows only
  the fixed lifecycle lines (SEALED / RECOVER state / UNSEALED / NOTHING DURABLE / RESUME STOPPED / LOST OWNERSHIP);
  no job name may appear on stderr; the host log holds caffeinate events only; the journal chain stays <= 8 entries
  (M29 killed). The science modules contain no print / warnings / logging. NOTE: the journal's resume entry records
  `n_ckpt`, `ckpt_verified`, `ckpt_rejected` and `ckpt_failures` keyed by job name, and the ckpt ref's tree listing is
  readable in-run by design: these are attempt-start progress facts; the no-observation rule (L6) must name the ckpt
  ref, the journal and loose-object times, and the names in `ckpt_failures` should be hashed (builder gap 7).
* MBS-4: `verified_records` refuses after SEALED / INDETERMINATE_SEALED / CLOSING or a sealed record (M28 killed);
  checkpoints are never deleted; the close record carries counts only.
* MBS-12: C2 — no successor file names C3_KNOCKOUT_RECONSTRUCTION (asserted; my grep agrees); C7(a) — `rehearse` /
  `controls` text-identical, rehearse not run; C7(b) — DECOY_CELLS = (297, 316) asserted, `decoy` refuses others and
  guards the band; C8 — no scanner exists yet (future QC12 must build planted strings at run time; protocol draft
  s11 says so); C9 — `decide` text-identical, nothing but R-MB on 308 (evaluate_target / controls text-identical),
  one marker by CAS. PASS (C8 deferred to qualification).
* S15 / GC-8: `check_mbr1_state` asserts exactly `[[marker, afa93072]]` under `refs/p5y-k5-cell308-mb-r1/`, no
  emergency file in MB r1's git dir, this git dir or the common dir, no NSF/evidence in the worktree, at HEAD or on MB
  r1's branch; called by preflight, execute and every resume. Planted extra ref, pending ref, moved marker, emergency
  file and evidence directory each refuse MBR1_STATE; the unplanted chain runs (re-run PASS; M25 killed). The real
  repository satisfies it now (read-only check: one MB r1 ref, afa93072; no MB-S ref). NOTE: the evidence path at HEAD
  / on MB r1's branch is not planted by the test.

## 9. Object-store hygiene — PASS WITH NOTE

Read-only scan of `/Users/suzhe/ReBaseGuard/.git/objects` (loose objects, `st_birthtime` and `st_mtime`, since
2026-09-29 18:00Z; packs): 327 loose objects were born in the window; the only ones containing MB-S lifecycle or
sandbox markers are six blobs born 21:05:13Z, each a source file of the build commit afba20e5 itself
(BUILD_REPORT.md, DRIVER_DIFF.md, mbs308_driver.py, mbs308_state.py, the protocol draft, mbs308_testlib.py). No
journal, checkpoint, result, probe, trial-commit or sandbox-commit object exists in the real store. Exactly one
object was freshened (born before, mtime inside): `a1995184cdbcf51f5e1885873958a5168fbd5f69`, MB r1's probe blob,
born before the build session, mtime 19:12:46Z — exactly as the builder disclosed (BUILD_REPORT s6). No pack changed. The successor
probe now carries a 32-hex nonce (distinct bytes; D17) and every sandbox borrows from a separate `--no-local` base
store whose constructor refuses alternates to the real store. NOTE: the builder's freshening changed the mtime of an
MB r1 object; any MB r1 audit must window by birthtime (as the builder says). My own review wrote nothing to the real
store (my base store is a `--no-local` clone; re-scan at the end).

## 10. T6 non-dependence: itemised provenance trace (M1) — PASS WITH DEFECT (DEF-3)

I did not read the MB r1 postexec record; per the builder's description it holds a chronology, launch-time host
readings, caffeinate pids, probe / trial ids and a qualitative pool-load
fact, and no per-job runtime. Sources: (a) MB r1 frozen value — MB r1 driver `mb308_driver.py` sha256 411252b2…,
MB r1 host `mb308_host.py` sha256 6702a9be…, MB r1 protocol `MB308_PROTOCOL.md` sha256 09ac4884…; (b) decoy /
synthetic run tonight; (c) host reading tonight; (d) UNTRACEABLE to (a)-(c). "Γ?" = can it affect Γ (value) or only
completion (whether / how far the one evaluation runs).

| # | constant (file) | value / rule | source | Γ? |
|---|---|---|---|---|
| 1 | WORKERS (driver) | 5 | (a) MB r1 driver l.100 (D11) | completion only |
| 2 | PRE_CAP_S (driver) | 1800 s before the marker | (a) MB r1 driver l.101 | completion only |
| 3 | EVAL_CAP_S (driver) | 8 h | (a) MB r1 driver l.102 (protocol 3.2) | completion only |
| 4 | EVAL_CAP application (state AwakeCap) | per attempt, CLOCK_UPTIME_RAW, from marker / resume start | (d) rule set in architecture 8a4a02b4 s8 (coordinator; MBS-8 user decision) | completion only |
| 5 | AwakeCap poll | min(5 s, cap/20) | (d) a priori | completion only (hit latency) |
| 6 | DECOY_CAP_S (driver) | 12 h | (a) MB r1 driver l.103 | decoys only |
| 7 | SEAL_RETRY_DELAYS (driver) | 0.5, 1, 2, 4 s | (a) MB r1 driver l.104 | completion only |
| 8 | RUNG_CPU_CAP_S (driver) | RLR 1800/4200/8700; C2B 1800/1800/2700; C1B 1800 x4; VER 1800 x5 | (a) MB r1 driver l.126 (protocol 3.2) | completion only (a hit is a failure, never a dropped rung) |
| 9 | DECOY_CELLS / REHEARSAL_CELLS / DECOY_SEED / DECOY_BUNDLES | (297, 316) / (305,) / 20260929 / 3 bundles | (a) MB r1 driver l.77-83 | non-target |
| 10 | MEM_CAP_BYTES (driver) | 3 GiB (provisional) | (d) — not the output of the builder's own rule on tonight's dev decoy (max(3 x 88 MB, 1 GiB) = 1 GiB); no source cited | completion only (a kill = INDETERMINATE) |
| 11 | memory-cap freeze rule (protocol s8) | max(3 x largest official decoy per-job peak RSS, 1 GiB) | factor 3 and floor 1 GiB: (d) a priori; input: official decoys (b, future) | completion only |
| 12 | dev-decoy per-kind peak RSS (protocol s8) | RLR 72 MB, C1B 70 MB, C2B 88 MB, VER 40 MB | (b) dev decoy 297 block 0 tonight (recorded, used by no constant) | none |
| 13 | MEM_POLL_S (driver) / Ctx default | 2.0 s | (d) a priori | completion only |
| 14 | FREE_MEM_MIN_BYTES (driver) | 2 GiB (vm_stat free+inactive+speculative+purgeable) | (d) a priori (not a host reading) | start gate only |
| 15 | EXCL_CPU_PCT (driver) | 25 % | (d) a priori | start gate only |
| 16 | EXCL_ALLOW (driver) | 41 macOS process names | (d) a priori list (builder gap 8: heuristic; no recorded reading cited) | start gate only |
| 17 | PLATFORM_PINS (driver) | interpreter bd349815…, libpython 34463f1b…, 3.14.5 + sys.version, 25F84, arm64 | (c) host readings tonight (re-verified by me) | guards determinism; mismatch refuses / UNRECORDED; no Γ effect |
| 18 | MAX_RESUMES (state) | 3 (attempt <= 4) | (d) architecture 8a4a02b4 s4(b) | completion only |
| 19 | DEADLINE_S (state) | 7 days after the marker | (d) architecture s4(c) | completion only |
| 20 | CKPT_FAIL_LIMIT (state) | 2 consecutive failures of one job | (d) architecture s4(a) | completion only |
| 21 | Lock retries (state) | 4 | (d) a priori | lifecycle only |
| 22 | worker parent-death watch (state) | 1 s | (d) a priori | lifecycle only |
| 23 | MIN_FREE_DISK (host) | 2 GiB | (d) architecture s6 | start gate only |
| 24 | MEMORY_PRESSURE_NORMAL (host) | level 1 required | (d) architecture s6 ("normal"); 1 = the OS meaning of normal | start gate only |
| 25 | lowpowermode gate (host) | 0 | (d) architecture s6 | start gate only |
| 26 | AC gate, thermal-pressure 0 gate (host) | AC Power; level 0 | (a) MB r1 protocol s14 l.269, l.309 | start gate only |
| 27 | SU_GATING_KEYS (host) | AutomaticallyInstallMacOSUpdates, CriticalUpdateInstall (missing = enabled) | (d) builder's key choice (D15) under DR2(c) | start gate only |
| 28 | caffeinate supervisor poll / backoff / respawn delay / stop join / terminate wait (host) | 0.2 s / 0.5 s / 0.05 s / 10 s / 5 s | (d) a priori | completion only (sleep prevention) |
| 29 | CAFFEINATE_FLAGS, SLEEP_GAP_TOL_NS, SAMPLE_EVERY_S, MAX_SAMPLE_GAP_S (host) | -i -m -s; 2 s; 60 s; 180 s | (a) MB r1 host l.42-47 | provenance only |
| 30 | launchctl print timeout (host) | 30 s | (d) a priori | launch / wait (DEF-2) |
| 31 | launcher bootstrap wait / wait poll / preflight timeout (launch) | 15 s / 2 s / 1900 s | (d) a priori | launch only |
| 32 | test-only timings (tests) | eval_cap 2 s, job_sleep 0.3-3 s, alloc 400 MB vs cap 200 MB, 60-90 s bounds | (b) synthetic, tests only | none |

**Finding.** No constant, cap, limit, timing or threshold traces to an observation of the MB r1 target run: every
value that bounds the science's run (WORKERS, the CPU caps, EVAL_CAP's value, PRE_CAP, SEAL delays) is MB r1's
frozen value, the platform pins are tonight's host readings, and nothing can affect Γ. **But** items 4, 5, 10, 11,
13-16, 18-25, 27, 28, 30, 31 have no source in (a)-(c): they are a priori values set by the builder (an exposed
agent, T6) or by the coordinator's architecture (a holder, E1″). None is plausibly derived from the postexec
record's content as described (it has no per-job runtime or memory figure), and all are completion-only, but M1 is
mechanical: **DEF-3**, re-derive or ratify them by a non-holder. The two that most deserve a derivation rule rather
than ratification are MEM_CAP (10/11) and the start gates FREE_MEM_MIN / EXCL_CPU_PCT / EXCL_ALLOW (14-16), which
decide whether the evaluation can start and, for MEM_CAP, whether it can finish.

## 11. Deviations D1-D17 (BUILD_REPORT s8): rulings

* **D1 (durable ARMING intent before the marker) — ACCEPTED.** It closes a real window of the design (marker written,
  no journal => CONSUMED_UNRECORDED, the evaluation lost for nothing). Exactly-once still rests on the marker CAS
  alone; the intent is bound to grant, driver, process identity and platform before the marker, so ARMING + marker +
  dead process is correctly CONSUMED_INTERRUPTED (deadline measured from the intent time), ARMING + marker + live is
  COMPUTING, ARMING without marker is taken over only if its process is dead, and a failed marker CAS closes the intent
  ABORTED_INTENT (M32 killed). Residual (DEF-5, part of R1): a marker CAS that fails for a non-conflict reason (e.g. a
  stale `target-consumed.lock` after a reset during the marker write) leaves ABORTED_INTENT without a marker; status
  says NO_TARGET_CONSUMED but every later `execute` refuses CONSUMED — a pre-marker wedge with no frozen action.
* **D2 — ACCEPTED** (MBS-3). **D3 — ACCEPTED** (needed for MBS-9 iii; M06-M08 killed).
* **D4 — ACCEPTED WITH NOTE.** The reading "journal whose checkpoints fail verification" = the tree recorded at the
  last attempt start is no longer contained in the ckpt ref, plus s4(a) literally, is a sound reconciliation (the
  classifier may not read content). Note: a bad checkpoint that is not rewritten before the next interruption counts
  twice and makes the run UNRECORDED although no new failure occurred; this follows the design's letter.
* **D5 (worker death = execution failure) — ACCEPTED WITH NOTE.** It is MB r1 s4's rule, it is what S17 asks
  ("exhaustion becomes a recorded INDETERMINATE"), the design's state table defines INTERRUPTED by the DRIVER's
  identity, and an OS jetsam kill, the memory-watchdog kill and a CPU-cap kill are all SIGKILL and cannot be told
  apart reliably. Making worker deaths resumable would let a cap hit be retried, i.e. would change a frozen cap into a
  budget. The trade (one transient jetsam kill costs the evaluation) should be shown to the user with MBS-6/MBS-8.
* **D6, D7, D8 — ACCEPTED** (a stale pending ref must be classified STALE first; rejected spool files are renamed aside
  and never read; an existing plain `execution/` directory is reused, a symlink still refuses).
* **D9 (`serialize` round-trips once before hashing) — ACCEPTED.** Confirmed: MB r1's self sha256 is not
  re-verifiable for int-keyed dicts (numeric vs lexical key order). The change is in the persistence layer only: the
  record's values are identical, only the key order inside int-keyed dicts and the self-hash definition differ from
  MB r1's layout (never produced for the target). MBR1_REPRO compares parsed leaves, so it is unaffected.
* **D10 (EVAL_CAP per attempt on CLOCK_UPTIME_RAW) — ACCEPTED WITH NOTES** (independent review of the MBS-8 rule as
  implemented). The watchdog starts after the marker (or the resume's journal advance), stops when the evaluator
  returns or raises, and on expiry raises MB r1's SIGALRM -> TimeoutError -> TARGET_EVALUATION_FAILED ->
  INDETERMINATE (S12 re-run; `eval_cap.clock` recorded). UPTIME_RAW does not advance in sleep, which is exactly the K
  channel MB r1 already uses (MONOTONIC_RAW - UPTIME_RAW), so no after-the-fact subtraction is needed; DarkWake
  counts as awake. A resumed attempt only recomputes jobs without a verified checkpoint, so the per-attempt cap never
  fails a resumed evaluation that would have passed uninterrupted. Notes: (i) the total awake budget becomes up to
  4 x 8 h within the 7-day window — completion only, never Γ, but the user's MBS-8 decision must name this
  semantics explicitly; (ii) the sleep exclusion is not exercised by a test (this host has not slept since boot:
  MONOTONIC_RAW - UPTIME_RAW = 0), it rests on the clock's documented semantics; (iii) as in MB r1, a cap firing in the
  instant between the evaluator's return and `SIG_IGN` records a failure.
* **D11 — ACCEPTED** (the hosting app exports XPC_SERVICE_NAME=0; equality + PPID 1 + launchctl pid is the right
  test). **D12 — ACCEPTED** (S1 made mechanical; MBS-13 will add more). **D13 — ACCEPTED** (DR2).
* **D14 (RESUME_CONTROL_FAILED) — ACCEPTED.** Stage 2 needs the controls' A_I1 and bundle; re-running MB r1's
  controls at resume is the only way to rebuild them without persisting them; on the pinned platform they are
  deterministic reproductions, so a failure signals non-determinism and INDETERMINATE is correct. It is not a new
  computation on 308 beyond what MB r1 ran before its marker.
* **D15 (update gate keys) — ACCEPTED WITH NOTE.** The two gating keys are the ones whose automatic installation can
  change the OS build; the resume-time platform pin backs them up (a change becomes UNRECORDED, never a mixed
  resume). Note: managed preferences (/Library/Managed Preferences) are not read; widening the gate to all four keys
  costs nothing and is recommended.
* **D16, D17 — ACCEPTED** (findings 2-4 reproduced in spirit by S01 and the hard exit; the nonce probe is distinct).

## 12. Anything else; freeze readiness

* The fault hook is inert in production (FAULT assigned only `None` in code/, every `fault()` names F1-F12, the CLI
  refuses when FAULT is set or any MBS308_TEST* variable exists; M20 killed).
* `check_not_evaluated`, `check_result_paths`, `check_clean` run at `execute` only; `resume` relies on the grant chain
  at HEAD, the research / science / helper pins and the classifier. Acceptable (the evaluation reads only pinned
  bytes), noted.
* Builder's own known gaps stand (s10): no qualification verifier, manifest writer or leak scanner; provisional pins
  and values; the real driver never launched by launchd; full MBR1_REPRO and QS-RESUME-DECOY not run; Q12 not
  re-measured under the launcher.
* **Freeze-ready apart from the user decisions (S16(c), MBS-6, MBS-7, MBS-8, S1)? NO.** DEF-1 and DEF-2 need code
  repairs, DEF-3 needs a non-holder derivation / ratification, DEF-4 needs tests, and the builder's own gaps (above)
  remain.
* 21:38Z own experiment `exp_lock2.py` (sandbox): `execute` stopped at F8 (the complete result durable in the spool),
  then a stale `journal.lock` planted: `recover` -> `seal-only` ends `LOST OWNERSHIP` (rc 9) twice, the state stays
  RESULT_DURABLE_UNSEALED and the durable result is never sealed; after the lock is removed by hand, `recover` seals.
  The journal is advisory in `seal-only` ("the artifacts, not the journal, decide"), yet `_journal` turns its failed
  CAS into LostOwnership. (Part of DEF-1.)

## Defects

* **DEF-1 (blocking; persistence / recovery; demonstrated in sandboxes).** `Store.cas_ref` returns False for ANY
  `git update-ref` failure, and every caller reads False as "another process moved the ref": `Checkpointer.write`
  raises JournalConflict -> `checkpointing_wait` raises LostOwnership; `Journal.advance` raises JournalConflict ->
  `_journal` raises LostOwnership, `run_resume` refuses RESUME_REFUSED, `run_close_indeterminate` refuses; the marker
  CAS failure closes the intent ABORTED_INTENT. A stale `<ref>.lock` (what a host reset or power loss inside a ref
  write leaves: the MB r1 failure class this campaign exists to survive) is never classified and no frozen action
  clears it, and no fault point lies inside a git write. Demonstrated: (a) stale `ckpt.lock` -> three resumes end LOST
  OWNERSHIP with nothing persisted -> RESUME_BUDGET_EXHAUSTED -> INDETERMINATE; (b) stale `journal.lock` -> resume and
  close-indeterminate both refuse: wedged in CONSUMED_INTERRUPTED; (c) stale `journal.lock` with a complete durable
  result -> `seal-only` ends LOST OWNERSHIP every time: the result is never sealed. (d) By reading: a stale
  `target-consumed.lock` makes the next `execute` close its intent ABORTED_INTENT; afterwards `status` says
  NO_TARGET_CONSUMED but every `execute` refuses CONSUMED (pre-marker wedge). Removing the lock by hand is outside the
  frozen actions (MBS-5: a deviation, INDETERMINATE).
* **DEF-2 (blocking; launcher).** `wait_and_cleanup` boots out the job after a single `launchctl print` that fails,
  times out or does not parse; `launch()` boots it out on any exception after the bootstrap. Either can kill a live
  post-marker job (launcher-induced interruption, a resume consumed).
* **DEF-3 (M1).** The untraceable constants of s10 (items 4, 5, 10, 11, 13-16, 18-25, 27, 28, 30, 31): completion-only,
  none traces to the MB r1 target run, but none traces to (a)-(c) either; M1 requires non-holder re-derivation or
  ratification.
* **DEF-4 (tests).** No behavioural test or mutant covers the driver's GC-10 start gates (free memory, exclusivity; the
  driver's `host_preflight` is stubbed in every sandbox run), the execute-time `check_platform` comparison, the
  resume-time `check_bindings` / `check_science_modules` refusals, or the GC-8 evidence path at HEAD / on MB r1's
  branch; they are asserted only by the presence of the call. I confirmed the unmutated behaviour by hand (s7), and
  the supplementary mutants X2 / X3 below show the gap.

## CONDITIONS (before the freeze; a bounded delta review checks R1-R4 only)

* **R1 (DEF-1).** (i) Distinguish a CAS conflict from other ref-write failures: after a failed `update-ref`, re-read
  the ref; only "the ref no longer holds the expected old value" is a conflict (LostOwnership / JournalConflict);
  anything else is a recorded, retried infrastructure failure. (ii) In `seal-only` (and in `_journal` generally
  after the durable artifacts exist) a failed journal advance must never stop the seal: the artifacts decide.
  (iii) Classify stale git lockfiles of the campaign (`refs/p5y-k5-cell308-mbs-r1/*.lock`, the branch lock,
  `packed-refs.lock`) when no live campaign process holds the O_EXCL lock / pidfile, and give `recover` a frozen,
  recorded, value-free action for them (move aside, never delete), before resume / seal / close. (iv) Add fault
  points / planted locks for the marker, journal, ckpt, pending and branch refs to the crash suite, each asserting the
  frozen final state, plus mutants that undo (i)-(iii).
* **R2 (DEF-2).** The launcher boots a job out only when the recorded job identity (pid, start time, boot UUID,
  command sha256) is dead, never on one negative `launchctl print`; `launch()` must not boot out a job that may have
  passed the marker (e.g. make the driver wait for the launcher's detachment record before arming, or never boot out
  after the bootstrap and leave refusal to the driver's own launchd check). Add a test with a planted failing
  `launchctl print` and a mutant.
* **R3 (DEF-3, M1).** A non-holder re-derives or ratifies, from decoy / synthetic / host evidence only, every
  untraceable item of the s10 table; MEM_CAP and the start gates (FREE_MEM_MIN, EXCL_CPU_PCT, EXCL_ALLOW) by a written
  rule from official decoy and host readings; the architecture values (3 resumes, 7 days, 2 failures, 2 GiB disk,
  lowpowermode 0, memory pressure normal, the per-attempt awake-time EVAL_CAP rule) are ratified or re-derived.
* **R4 (DEF-4).** Behavioural tests + mutants for the driver's GC-10 start gates on planted readings, the
  execute-time and resume-time platform / research / science pin refusals, and GC-8 with an evidence path at HEAD and
  on MB r1's branch.
* **Qualification (unchanged from the builder's own gaps).** Build the verifier, manifest writer and leak scanner
  (ckpt tree by counts and tree hash only, names included in the quarantine; planted strings built at run time, C8);
  re-pin HELPER_SHA256 and PLATFORM_PINS at the freeze; run the real driver's `decoy` under the launchd launcher
  (Q12 re-measured under it, RC6); full MBR1_REPRO (QC02, QC03, QC04 pair) and QS-RESUME-DECOY; the user disables
  AutomaticallyInstallMacOSUpdates and CriticalUpdateInstall before `execute` (tonight all four keys are 1).
* **User decisions (unchanged):** S1, S16(c), MBS-6, MBS-7, MBS-8 — the MBS-8 text must state the per-attempt,
  awake-time EVAL_CAP semantics (up to 4 x 8 h awake within 7 days) and should show the D5 trade.

## NOTES

1. D4: a bad checkpoint not rewritten before the next interruption counts twice (UNRECORDED without a new failure).
2. A torn worktree copy (crash inside `materialize`) leaves SEALED with `recover` returning 7; no frozen action.
3. `ckpt_failures` in the journal is keyed by job name; hash the names (builder gap 7); the L6 no-observation rule
   must name the ckpt ref's listing, the journal counts and loose-object times.
4. `busy_processes` treats only direct children as "this process tree".
5. `mbs308_launch._run` does not catch TimeoutExpired.
6. D15: read all four keys as gating and consider /Library/Managed Preferences.
7. Process start time is read with `ps -o lstart` in the local time zone (HOST.ENV has no TZ): a time-zone change
   between the journal write and a classification would make a live driver look dead (JST has no DST; set TZ=UTC0).
8. The builder freshened the mtime of MB r1's probe blob a1995184 (disclosed); any MB r1 audit windows by birthtime.
9. `check_not_evaluated`, `check_result_paths` and `check_clean` run at `execute` only, not at `resume`.
10. This host would refuse `execute` tonight (all SoftwareUpdate keys 1; free memory ~1.57 GiB at 21:34Z).

## Work log (continued)

* 21:47Z mutant matrix complete: unmutated 30/30 PASS; 33/33 killed, all by assertion (per-mutant result files
  checked).
* 21:47Z-21:50Z supplementary mutants (same runner, own base store): X2 (driver exclusivity gate forced true) ->
  launch::t_preflight_gates_planted: **SURVIVED**; X3 (`check_platform` compares nothing) ->
  state::t_platform_mismatch_at_resume: **SURVIVED**; controls X5 (classifier ignores the recorded ckpt tree) ->
  t_ckpt_tree_inconsistent: KILLED; X6 (a live lock is broken) -> t_S03_stale_lock: KILLED. Unmutated targets 4/4
  PASS. X2 / X3 are the DEF-4 gap: the execute-time platform comparison and the GC-10 start gates have no test.
* 21:31Z also verified the protocol draft's s2 list: 45 rows (path, sha256, blob) all equal at 21e99cf0, at afba20e5
  and on disk.
* 21:48Z-21:53Z dev decoy re-run (`test_mbs308_decoy.py`; exactly `decoy --cell 297 --first-blocks 1 --dev-ladder
  --workers 2`, three times: uninterrupted, SIGKILLed after 2 checkpoints, resumed): 2/2 PASS — served C1B.0.4 and
  C2B.0.20, computed 2; Stage 1 (643 leaves) and 5 Stage-2 decoy bundles (883 leaves) equal to the uninterrupted run;
  MBR1_REPRO tiny: RLR d4 (192 leaves), C2B N20 (43 leaves) and geometry equal to MB r1's committed QC02 records. Only
  booleans and leaf counts were read; no decoy value was inspected. Host CLEAN.
* 21:53Z final hygiene: no `org.rebaseguard` launchd job; no stray caffeinate / python process; successor worktree
  clean (also `--ignored`), HEAD afba20e5; real refs: only `refs/p5y-k5-cell308-mb-r1/target-consumed` -> afa93072,
  no MB-S ref, no spool in the successor git dir; real object store since 21:09Z: nothing freshened, no pack changed,
  no loose object carrying any MB-S lifecycle / sandbox marker (57 loose objects were born meanwhile, none of them
  mine or the build's). 11 ledger lines appended (class REVIEW, agent reviewIMPL, 0 target evaluations, no
  LEAK_FLAG).

## Verdict

**IMPLEMENTATION_REJECTED** (repairable; bounded delta). The science boundary (RC1, S11, MBS-9(i)), the guard, the
state machine's states and actions, the persistence chain, checkpoints and resume (MBS-9(ii)/(iii)), MBS-3, MBS-4,
MBS-12, GC-8, the detachment proof, the caffeinate supervisor, the memory watchdog, the awake-time EVAL_CAP and the
object-store hygiene all PASS on re-run (static 9/9, state 34/34, crash 36/36, launch 6/6, decoy 2/2, mutants 33/33
killed), and no constant traces to the MB r1 target run. The rejection rests on DEF-1 (a stale git ref lock, the
footprint of the very host reset MB-S exists to survive, burns every resume to INDETERMINATE, wedges the run, or
keeps a complete durable result from ever being sealed — demonstrated), DEF-2 (the launcher can boot out a live
post-marker job on one failed `launchctl print`), DEF-3 (M1: untraceable a-priori constants need non-holder
re-derivation or ratification) and DEF-4 (untested execute-time platform and GC-10 start gates; X2 / X3 survive).
A delta review limited to R1-R4 and their tests / mutants suffices; nothing else needs re-review.
