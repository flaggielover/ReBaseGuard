# Cell-308 successor MB-S r1: implementation delta review of R3 + C-1 (+ N-2 / N-3) at 191ce4a9 (reviewR3C1)
DELTA_ACCEPTED

Reviewer: **reviewR3C1**, a fresh reviewer who is not a holder (brief 44 + practical notes 44-N; research c8fbb1cb / 0700f8f8).
Started 2026-09-30T04:33Z. Object: successor branch `p5y-k5-cell308-mbs-r1`, repair commit
`191ce4a965d822284f42afa172bb898ab168b324`, diffed against its parent `35cabb50`. The worktree was clean at 191ce4a9 throughout, so
every run below exercised the committed bytes. New cell-308 target evaluations by this review: **0**. I evaluated no
cell in 305-309 and no drift in [6/5, 13/5] or its mirror. I did not touch cell 309. I created no authorization, grant,
marker, pending result or seal. I made no git write.

## Reading, and my own exposure (disclosed as brief 44 requires)

* **Read:** the diff 35cabb50..191ce4a9 in full (code, protocol draft, tests, mutant runner, BUILD_REPORT section 13 as
  a claim to check); REVIEW_IMPLEMENTATION_MBS308_DELTA (99185dcb); CONSTANTS_RATIFICATION_MBS308 (3c2a7854; the
  worktree copy is byte-identical to the commit); briefs 40, 42, 44 and 44-N and the brief index; governance erratum E1
  section D3 and the conditions-register rows that mention holders; the research ledger's recent lines; MB r1's
  `mb308_driver.py` at c46434a3 (to regenerate DRIVER_DIFF.md) and `mb308_stage1.jobs` (the job order); CPython 3.14.5's
  `concurrent/futures/process.py` and `multiprocessing/util.py`.
* **Not opened:** any MBS-2 file (REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*,
  REVIEW_SUCCESSOR_GOVERNANCE_308*, INCIDENT_INDEPENDENCE_REVIEW_MBS308* including T6, COORDINATOR_EXPOSURE_DISCLOSURE*);
  anything under `p5y_k5_cell308_mb_r1/{review,adjudication,postexec,evidence}/`; BUILD_REPORT section 9; any other
  session's scratchpad, including the editor's; anything under `/Users/suzhe/.claude/`.
* **My exposure: MB r1 observations I hold that did not come from an allowed file.**
  1. My session began with an auto-loaded memory index in my context; I did not open any file of it. Three index lines
     touch MB r1:
     * an outcome label of its one execution, which also appears in the allowed governance texts;
     * a qualitative lesson line about host sleep and thermal slowdown inflating wall times, whose provenance I do not
       know;
     * a successor-lessons line: never move `packed-refs.lock` aside, timing-dependent mutant kills are not kills,
       liveness needs positive evidence. These are the conclusions of reviewIMPL's committed C-1, M33 and N-3, which I
       re-derived from the allowed files and my own runs.
  2. A routine `git log --oneline -5` in the successor worktree showed me the one-line subjects of MB r1's grant
     commit (afa93072) and postexec commit (21e99cf0). The postexec subject carries a qualitative chronology with two
     clock times. This is the same inadvertent exposure the ratifier disclosed.

  None of this contains a per-job, progress, CPU, memory, host or science figure. I do not repeat it. No ruling below
  uses it, and I chose no operational value.

## Work log (UTC; all runs on my own `git clone --no-local --bare` base store `reviewR3C1/base_store.git`, sandboxes only)

* 04:36Z ledger (reading); 04:38Z snapshot of the real repository: 144 refs, only `refs/heads/p5y-k5-cell308-mbs-r1`
  (-> 191ce4a9) under the successor name, MB r1's marker -> afa93072, no `refs/p5y-k5-cell308-mbs-r1/`, no
  `packed-refs.lock`, no `mbs308-spool`; `launchctl list` shows no rebaseguard job.
* 04:38-05:01Z stream A (sequential): launch, static, state, crash. 04:38:55-05:20:29Z stream B: the full mutant matrix
  (started after the launch suite finished, so no two launchd tests overlapped). 05:00-05:13Z stream C (sequential,
  after the crash suite): M33 standalone x2, then supplementary mutants X1-X5. Probes (sandbox, synthetic): the C-1
  pre-marker refusal, and the M33 mechanism (unmutated vs M33 code).
* **Launchd disclosure.** I ran the launch tests as committed, which the brief permits. Four transient LaunchAgents with
  the SYNTHETIC payload were bootstrapped under the TEST prefix: `org.rebaseguard.mbs308.test.20260930T043834`,
  `...ld20260930T043839`, `...wc20260930T043841841456`, `...nb20260930T043845540541`. The matrix added four more under the same prefix for
  its launch targets (`...wc20260930T044654968345`, `...nb20260930T044651671558`, `...wc20260930T051634361008`,
  `...nb20260930T051637688251`). Each was booted out by its test's teardown, and the plists
  (in my scratch) were deleted by the tests. `launchctl list` shows no rebaseguard job, and no plist is left. The empty
  stdout / stderr logs landed in `~/Library/Logs/ReBaseGuard/mbs308-test/` and are left in place, as in the previous
  review.

## 1. R3

### (a) EXCL_ALLOW — MET
AST comparison of the `EXCL_ALLOW` literal: 35cabb50 has 39 names, 191ce4a9 has 43. The diff is exactly
+{`spotlightknowledged.updater`, `cloudd`, `BackgroundShortcutRunner`, `modelcatalogd`}, with nothing removed. The 39
names are identical to the set the ratifier read: afba20e5, whose driver is 7bc2a619… and whose helper hashes match the
ratification header. Tests:
* `state::t_gc10_ratified_allow_list` (each daemon alone and all four together pass; an unlisted OS daemon refuses
  `host_exclusive`) and the static check both PASS.
* M51 (all four removed) is KILLED, and so is my X5 (only `cloudd` removed).

### (b) preflight timeout = PRE_CAP_S + 100 — MET
* `pre_launch` passes `timeout=PRE_CAP_S + 100`. The launcher reads `PRE_CAP_S` from the driver's own bytes: an
  `ast.literal_eval` of the module-level assignment, with no import of the driver and so no science loaded. It refuses
  to import if the literal is missing (fail closed).
* The driver has exactly one `PRE_CAP_S = 1800`, and it is the value the driver's own alarm and WALL_CAP refusal use.
  The value is therefore still 1900 s.
* `launch::t_preflight_timeout_rule` shows the timeout follows a copy whose PRE_CAP_S is 1234 (1334). M52 (the literal
  restored) is KILLED.

### (c) protocol section 8 carries the four rules verbatim — MET
* I extracted R-MEM (steps 1-6), R-FREE (with *Attainability*), R-EXCL-PCT and R-ALLOW (with *Never added*) from the
  ratification committed at 3c2a7854. Each block is a byte-exact substring of section 8 at 191ce4a9 (1376 / 560 / 506 /
  704 characters), with no whitespace normalisation. The dev-input illustration and the optional recommendation are
  excluded, as they should be.
* Section 8 states that MEM_CAP_BYTES, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT and EXCL_ALLOW are frozen as the rules'
  outputs, computed from the official qualification evidence, never from any target run, with inputs recorded.
* The superseded draft memory rule is no longer stated as the frozen rule anywhere in the draft. It appears once, only
  as "replaced by the stricter R-MEM".
* The provisional values are unchanged: 3 GiB, 2 GiB and 25. The ratification rules both 3 GiB and 2 GiB provisional
  for the pre-freeze build.

### (d) no other operational change — MET
* **Constants.** Every module-level assignment in the five code files was compared by AST between 35cabb50 and
  191ce4a9. Only `EXCL_ALLOW` changed, plus `HELPER_SHA256` (driver) and the new derived `PRE_CAP_S` (launcher).
* **Digit scan.** A `git diff -U0` digit scan of `code/` finds only comments, the three re-pinned hashes and the timeout
  expression.
* **Driver definitions.** No driver function or class changed between 35cabb50 and 191ce4a9. The 46 carried
  definitions (`check_clean` included) are still text-identical to MB r1's.
* **Behaviour changes.** The only behavioural code changes are:
  * C-1: `git_lockfiles`;
  * N-3: `_not_dead` and `git_lock_info`;
  * N-2: `identity_state`;
  * the launcher's `driver_literal`.

  None introduces a cap, limit, timeout, threshold, allow-list entry, budget or poll value. Launcher 15 s / 2 s,
  WORKERS, caps, MAX_RESUMES, DEADLINE, CKPT_FAIL_LIMIT, lock retries, the caffeinate timings and all poll intervals
  are unchanged.
* **Test-only values.** Values that never reach the campaign: `job_sleep` 90, which is builder2's proposal as
  reviewIMPL measured it; the new run's harness timeout of 150 s, the editor's test value, needed so that an unreleased
  run ends past the 90 s sleep and fails by assertion; helper sleeps 60 / 120 s; planted readings; PRE_CAP_S 1234 in
  the follow test. These are outside the operational set, as in reviewIMPL's M4 check.

### (e) HELPER_SHA256 and DRIVER_DIFF.md — MET
* **Pins.** The sha256 of the committed `mbs308_host.py`, `mbs308_state.py` and `mbs308_launch.py` equal the new pins;
  the guard is unchanged (48903487…).
* **DRIVER_DIFF.md, regenerated myself.** I used `difflib.SequenceMatcher(autojunk=False)`, 3 lines of context, on MB
  r1's `mb308_driver.py` (c46434a3, byte-identical at 21e99cf0, sha 411252b2) against `mbs308_driver.py` (d13688d1).
  * The result has 22 hunks, and all 22 hunk bodies are byte-identical to the committed file's.
  * Applying the committed hunks to MB r1's driver reproduces `mbs308_driver.py` byte for byte.
  * The top-level definitions each hunk touches, mapped by my own AST line ranges, equal the committed hunk index for
    all 22.
  * Both sha256 values in the header are correct.
  * Against 35cabb50's DRIVER_DIFF.md only the header's new sha and hunks 4 and 8 change content. The rest are line
    numbers. The same checks also pass on 35cabb50's file.
  * Note: difflib's default `autojunk=True` aligns hunks 1, 10, 15 and 18 differently (same patch result), so the
    stated `autojunk=False` matters and is correct.
  * The IDENTITY / LIFECYCLE class labels are unchanged; no hunk touches a carried definition.

### (f) SEAL_RETRY_DELAYS reuse listed — MET
Protocol section 8's closing paragraph and BUILD_REPORT section 13 (row "33 (review)") list it. The code agrees:
`store()` passes the driver's `SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)`, identical to MB r1's line 104. No new number.

### (g) deterministic M33 — MET
* **The test.** `t_S01_worker_death` now starts with `{"worker_die": "RLR.0.6", "job_sleep": 90}`, harness timeout
  150 s, under the unchanged `< 60 s` bound. The seven carried runs are unchanged (same keys, 90 s harness timeout).
* **Per-run results: three independent M33 runs, each KILLED by the target's assertion (error None), and each time
  ONLY by the new run.**

  | M33 run | new run (RLR.0.6+sleep90) | seven carried runs | status |
  |---|---|---|---|
  | matrix | 97.0 s (fails the 60 s bound) | 6.5-7.2 s, all pass | rc 5 |
  | standalone 1 | 101.7 s (fails) | 9.6-12.1 s, all pass | rc 5 |
  | standalone 2 | 99.0 s (fails) | 8.6-11.0 s, all pass | rc 5 |

  In every run the status was otherwise correct (TARGET_EVALUATION_FAILED, INDETERMINATE). Because the seven carried
  runs passed under M33 all three times, the kill cannot have come from the old, lucky path.
* **Unmutated.** The new run took 10.0 s (crash suite), 12.6 s and 10.9 s (the standalone runs' unmutated phases) and
  9.5 s (probe), against the 60 s bound.
* **Mechanism probe (mine).** The same spec was run once on the unmutated code and once on the M33 code, and the sealed
  records were read:

  | code | elapsed | release event | synthetic jobs completed |
  |---|---|---|---|
  | unmutated | 9.5 s | exactly one `broken_pool_worker_killed`, about 2 s after the start (one 2 s poll) | none (the surviving worker was killed mid-sleep) |
  | M33 | 99.0 s | none | the surviving worker completed its full 90 s job `RLR.1.6` before the pool shutdown returned |

* **The editor's argument is correct, and slightly stronger than stated.**
  * **Job order.** `jobs` sorts by (−weight, −rung, block), so `RLR.0.6` is first and `RLR.1.6` second. The die check
    in `synth_job` precedes the sleep.
  * **Lock hold.** CPython 3.14.5's `terminate_broken` holds `shutdown_lock`, and the manager's `shutdown_lock` *is*
    `executor._shutdown_lock` (process.py line 290). While holding it, `_join_executor_internals(broken=True)` joins
    every worker. Stage 1's `ex.shutdown(wait=False)` enters `CheckpointingPool.shutdown`, whose `super().shutdown`
    takes the same lock (line 857), so the main thread blocks until every worker has exited.
  * **Why no worker leaves early.** The workers cannot die of SIGTERM at any point:
    * the driver sets SIG_IGN before the evaluation;
    * `synth_init` is a no-op, so the ignore is inherited rather than installed;
    * multiprocessing's spawn uses `_posixsubprocess.fork_exec` with `restore_signals=False`, and a SIG_IGN
      disposition survives exec.

    There is therefore no bootstrap window in which the survivor could die early.
  * **The survivor's two cases.** The survivor either holds a 90 s job, then exits (`max_tasks_per_child=1`), or blocks
    forever on the call queue, whose pipe it holds both ends of.
  * **Conclusion.** In both cases, only `_MemWatch._release_broken`'s SIGKILL ends the run inside 60 s.
  * **Failure mode.** `T.child` kills the child on its timeout without raising. An unreleased run therefore fails the
    bound by assertion, as claimed.

**R3: MET** on all of (a)-(g).

## 2. C-1 — MET

* **The lock set.** `git_lockfiles` lists only `refs/p5y-k5-cell308-mbs-r1/*.lock` and the branch lock. Stale-lock
  detection (`git_lock_info`), the move-aside action (`move_stale_git_locks`), the classifier, `recover`, and every
  post-marker GIT_LOCKED refusal (`resume`, `seal-only`, `close-indeterminate`, all reading `cls['git_locks']`) take
  their set from it. So does the pre-marker `check_not_evaluated`.
* **Nothing else touches it.** A search of `code/` finds `packed-refs.lock` only in MB r1's carried, text-identical
  `check_clean` and in a docstring. The campaign never deletes a ref. It seals with `commit-tree` plus `update-ref`,
  never with porcelain `commit`, so it cannot trigger auto-gc / pack-refs itself.
* **`check_clean` still refuses it before the marker.** `check_clean` is called only in `run_execute`, before the
  marker. My probe planted the lock before `execute`. It refused with check_clean's path-form detail
  (`GIT_LOCKED: <sandbox>/.git/packed-refs.lock`), not the campaign-lockfile message. The state stayed
  NO_TARGET_CONSUMED, no MB-S ref existed, and the file was intact.
* **Tests adjusted.**
  * L09 became `t_L09_packed_refs_lock_never_moved`. My re-run passed all four cases:
    * (a) after a crash: not listed, recover resumes and seals;
    * (b) planted at the 4th checkpoint and (c) planted at F8: the lock was present during the run, which sealed with
      no ref-write or checkpoint-write failure and the baseline's certified bytes;
    * (d) before execute: GIT_LOCKED, nothing consumed, recover does nothing, and execute seals once git's lock is gone.

    In every case the file stayed in place byte for byte, `git-locks-aside` stayed empty and no recover action named it.
  * L11 was re-targeted to the campaign's own ckpt lock held open.
  * M38 was re-targeted to L11 and is KILLED.
  * M48 (packed-refs.lock restored to the lock set) is KILLED by L09's assertion.
* **Fails closed, defers to git.** Before the marker the campaign refuses and git releases its own lock. After the
  marker the lock does not block the campaign's creates and updates (git 2.50.1: L09 b/c). Any ref-write failure takes
  the recorded `RefWriteError` path. No code works around the lock.
* **Protocol.** Section 4 states the new lock set and the reason.
* **Test-harness note.** The test library's `wipe_state` still unlinks a planted `packed-refs.lock` inside the
  sandbox. That is harness code, never campaign code, and I accept it.

## 3. Bounded R2 hardening N-2 / N-3 (optional; ruled separately)

* **N-2 — MET.**
  * **Logic.** `identity_state` compares a recorded field only if it was recorded, and returns ALIVE only when
    boot_uuid, start_time and command_sha256 were all recorded and all match. A missing field therefore can neither
    prove death nor complete a match. A live pid with an incomplete record is UNKNOWN. A gone pid is DEAD (positive
    evidence from `kill(pid, 0)`). A complete record behaves exactly as at 35cabb50.
  * **Test.** `launch::t_identity_state_positive_evidence` covers each missing field (alive: UNKNOWN; dead: DEAD), a
    complete live record (ALIVE), a failing `ps` (UNKNOWN) and a reused pid (DEAD). It PASSES.
  * **Mutants.** M49 (the start-time facet) is KILLED. My X1 (the command facet reverted) and X2 (a partial record reads
    ALIVE) are both KILLED by the same test, so each facet of N-2 is covered.
* **N-3 — MET, with one coverage note.**
  * **Logic.** `_not_dead` treats a recorded campaign identity as holding the lockfiles unless `identity_state` is
    DEAD. A failed `ps` or boot-UUID read keeps them held: recover exits 8, nothing is done. This is the positive-evidence
    direction reviewIMPL asked for.
  * **Test.** `crash::t_L12_lock_ps_failure_not_stale` PASSES: first recover exits 8 with the lock held; after the
    helper dies, recover moves the lock and seals.
  * **Mutants.** M50 is KILLED, and my X3 (only the pidfile source reverted) is KILLED.
  * **Coverage note.** My X4 (only the journal-process source reverted to `identity_alive`) SURVIVES. L12 plants only
    the pidfile, so the journal and recover-lock sources are covered only through the shared `_not_dead`, which M50
    exercises. A one-case extension of L12 (the journal's recorded process with `ps` failing) would close this. It is
    not gating.
  * **Edge note.** A recorded identity dict without a `pid` reads "no process" in `classify` (exclude_pid None) but
    UNKNOWN under `move_stale_git_locks` (exclude_pid = self). `recover` then refuses at the move with
    GIT_LOCKS_NOT_STALE, which fails closed. `HOST.identity()` always records a pid, so this arises only from a corrupt
    file. Not gating.
* **Leaving the other `identity_alive` sites and N-1 — reasonable, and documented** in BUILD_REPORT section 13. The four
  remaining sites (the classifier's CONSUMED_COMPUTING test, `Lock.acquire`, `read_pidfile`, and
  `check_not_evaluated`'s stale-intent takeover) are named, with their second line of defence. Changing them changes
  the frozen state table of protocol section 4, which is beyond a bounded delta. N-1 is safe-direction.
* **Recommendation.** The two post-marker sites (the CONSUMED_COMPUTING test and `Lock.acquire`) should get their own
  reviewed delta **before the freeze**. A failing `ps` on a live computing driver could otherwise let a resume start
  alongside it, with only the journal CAS / LostOwnership as the stop. That would be an avoidable concurrent attempt.

## 4. Governance point (T6 M4 as stated in briefs 40 / 42) — substantively satisfied; the formal point needs the user's ruling

* **What the editor discloses (BUILD_REPORT section 13).** Its session's auto-loaded memory, written by the coordinator
  (a holder), carries a qualitative chronology of MB r1's execution with clock times, and no figure. I did not seek
  out that material.
* **What I can establish without it.**
  1. **Requested.** Every repair in 191ce4a9 was requested or recommended by the non-holder reviewIMPL (99185dcb):
     R3 application, C-1 and the M33 run are its verdict items 1-3; N-2 / N-3 are "recommended in the same pass". M4's
     first clause, which allows repairs by an exposed party only at a non-holder's request, is satisfied.
  2. **No value chosen.** No operational value in the diff was chosen by the editor. The four daemon names and the
     rule PRE_CAP_S + 100 are the non-holder ratifier's rulings (items 16 and 31, 3c2a7854). I verified the
     transcription is exact and that nothing else operational changed (1 d). So nothing an exposed party knows could
     have entered an operational value, which is M4's evident purpose.
  3. **The stricter wording.** Brief 40 states M4 as an exposed repairer must "never touch" an allow-list value. Brief
     42 routed exactly this application to the non-holder ratifier because "only a non-holder may change operational
     numbers". The editor, who is at least exposed by its own disclosure, edited the `EXCL_ALLOW` literal. Read
     literally, as the briefs word it, that is the act brief 42 reserved to a non-holder.
  4. **Identity question.** The research ledger attributes the recording of brief 44 and my launch to agent
     `editorR3C1`, so the editing session also acted as coordinator. The disclosure does not say whether the editor is
     itself a holder or only exposed through memory.
  5. **Precedent.** The ratifier's inadvertent exposure to a one-line chronology was ledgered, and it was still treated
     as a non-holder entitled to change numbers (brief 42).
* **Why I cannot rule.** Parity with the ratifier would need a comparison with material I must not read, the T6 text
  and the editor's holder status.
* **Recommended options for the user.**
  * **(A)** Rule that a verified mechanical transcription of a non-holder's values satisfies M4. This review is the
    non-holder verification; nothing changes.
  * **(B)** Have a non-holder re-apply the four names and the timeout expression. The result must be set-identical,
    and a mechanical re-check (static test, M51 / M52, and this review's AST and set comparison) would suffice.

  My technical verdict does not depend on which option the user takes.

## Re-runs on the committed bytes (counts)

| suite | result |
|---|---|
| static | **10/10 PASS** |
| launch | **10/10 PASS** (synthetic payload; see disclosure) |
| state | **45/45 PASS** |
| crash | **48/48 PASS** (F1-F12 x exit/kill, S01-S12, L01-L12) |
| mutant matrix | **52/52 KILLED** (unmutated: every target test PASS; every kill checked in its per-mutant result file: the target's own assertion, no error, timeout or missing result) |
| M33 standalone | **2/2 KILLED** (+ the matrix run = 3/3, each by the deterministic run only) |
| C-1 regression | L09 PASS (a-d); M48 KILLED; pre-marker probe: check_clean refuses, nothing consumed |
| supplementary (mine) | X1, X2, X3, X5 KILLED; X4 SURVIVED (coverage note above) |

## Integrity

* **Real repository** (checked at 05:21Z against my 04:38Z snapshot): the 144 refs are byte-identical; there is no ref
  under `refs/p5y-k5-cell308-mbs-r1/`; MB r1's marker still names afa93072; there is no `packed-refs.lock` and no
  `mbs308-spool` in the real git dir.
* **Real object store:** 0 files newer than my snapshot marker. The positive control, a file touched after the marker in
  my scratch, is found.
* **Successor worktree:** clean at 191ce4a9 before and after.
* **Launchd:** no launchd job of the campaign or the tests; no plist in my scratch or in `~/Library/LaunchAgents`; no
  stray mbs308 process.
* **Logs:** 16 empty log files (the 8 test labels above) in `~/Library/Logs/ReBaseGuard/mbs308-test/`, left in place.
* **Research worktree:** my only writes are 12 ledger lines (the last one records this verdict), all with
  `new_target_evaluations` 0 and no LEAK_FLAG, and
  this file. The coordinator commits them.
* **My scratch:** `.../scratchpad/reviewR3C1/` holds the base store, per-run JSON reports, my probes and my
  regenerated DRIVER_DIFF hunks.

## Verdict

**Accepted** (the verdict on line 2).

| condition | ruling |
|---|---|
| R3 (a) EXCL_ALLOW = the 39 plus the 4 | **MET** |
| R3 (b) preflight timeout = PRE_CAP_S + 100 (follows the driver) | **MET** |
| R3 (c) protocol section 8 carries R-MEM / R-FREE / R-EXCL-PCT / R-ALLOW verbatim; the four constants frozen as rule outputs | **MET** |
| R3 (d) no other operational change | **MET** |
| R3 (e) HELPER_SHA256 re-pinned; DRIVER_DIFF.md faithful (regenerated) | **MET** |
| R3 (f) SEAL_RETRY_DELAYS reuse listed | **MET** |
| R3 (g) deterministic M33 (3/3 killed by the new run alone; mechanism confirmed) | **MET** |
| C-1 | **MET** |
| N-2 (optional) | **MET** |
| N-3 (optional) | **MET** (coverage note: X4) |
| other `identity_alive` sites and N-1 left for a later delta | reasonable, documented |
| governance (M4) | substantively satisfied; **the formal point needs the user's ruling** (A or B above) |

**IMPLEMENTATION_ACCEPTED as a pre-freeze candidate.** reviewIMPL's conditions R1, R2 and R4 were met at 35cabb50 and
are unchanged here. R3 and C-1 are now met. This acceptance is subject to the user's ruling on the governance point
before the freeze.

**Remaining before any freeze** (I choose no freeze parameter):
* **Governance.** The user's ruling on the M4 point above.
* **Recommended deltas** (each with its own non-holder review):
  * positive-evidence liveness at the classifier's CONSUMED_COMPUTING test and at `Lock.acquire`;
  * optionally, N-1;
  * the L12 journal-source case.
* **Tooling.** The qualification verifier, manifest writer and leak scanner.
* **Official decoys.** Run under the launchd launcher, with the R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW inputs recorded as
  the rules require: at least 10 prepared-state readings 30 s apart, the attainability of FREE_MEM_MIN, and the
  path-class check for every R-ALLOW addition. The four constants are then frozen as the rules' outputs. Protocol
  section 11 should list these qualification records.
* **Re-pins.** HELPER_SHA256 and PLATFORM_PINS at the freeze.
* **Reproduction.** Full MBR1_REPRO and QS-RESUME-DECOY.
* **User action.** Disabling automatic macOS / critical-update installation.
* **User decisions.** S1, S16(c), MBS-6, MBS-7 and MBS-8, with MBS-8 stating the per-attempt awake-time EVAL_CAP.
