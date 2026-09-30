# Cell-308 successor MB-S r1: implementation delta review of repairs R1-R4 at 35cabb50 (reviewIMPL, resumed)
DELTA_REJECTED

Reviewer: reviewIMPL (the non-holder reviewer of `REVIEW_IMPLEMENTATION_MBS308.md`, 6d3a44cd). Brief 43 + erratum E1
(research 3d08f981). Started 2026-09-29T23:39:55Z. Object: successor branch `p5y-k5-cell308-mbs-r1` at
`35cabb50` (builder2's repairs R1, R2, R4, diffed against afba20e5); the ratification
`governance/CONSTANTS_RATIFICATION_MBS308.md` (3c2a7854) for R3. No commit exists after 35cabb50 (erratum E1; the
worktree is clean at 35cabb50). New cell-308 target evaluations by this review: 0. No MBS-2 file opened.

## Work log

* 23:40Z read the 35cabb50 diff (code, protocol draft, tests, mutants, BUILD_REPORT s12) and the ratification.
* Scope re-verified at 35cabb50: nothing outside NSS changed; NSF unchanged; the guard unchanged; DRIVER_DIFF.md's 22
  hunks applied to MB r1's driver (c46434a3) reproduce `mbs308_driver.py` byte for byte; my AST check: the 46 carried
  definitions are still text-identical to MB r1's.
* 23:44Z-: re-runs on my own `--no-local` base store (sandboxes only), sequential suites in one stream and the full
  mutant matrix in a second stream (modest parallelism, 2 workers per sandbox run).
* 23:44Z-23:47Z static 9/9 PASS; launch 8/8 PASS with review labels `org.rebaseguard.mbs308.review.{20260929T234448,
  ld20260929T234453, wc20260929T234455730053, nb20260929T234459213254}` (plists and logs in my scratch; every job booted
  out, no plist left, `launchctl list` shows no rebaseguard job).
* 23:47Z own probes (read-only / scratch only): (1) a scratch git repository (git 2.50.1): a stale `packed-refs.lock`
  does NOT block creating or updating a ref, only deleting one; the campaign's code never deletes a ref. (2)
  `HOST.identity_state` on this process with one recorded field missing: `start_time None` -> DEAD, `command_sha256
  None` -> DEAD (see N-2). (3) M33 determinism probe (below).

## R1 (DEF-1: CAS vs infrastructure, stale locks, seal, pre-marker wedge) — MET (with correction C-1 and notes)

* (i) `Store.cas_ref` re-reads the ref after a failed `update-ref`: only "readable and no longer the expected old
  value" is a conflict (False); a persisting non-conflict failure is recorded (`REF_WRITE_FAILURES`, value-free) and
  retried on MB r1's `SEAL_RETRY_DELAYS`, then raised as `RefWriteError`. Callers: a checkpoint write failing so is
  recorded and the evaluation continues (L05: 4 recorded failures with `lock_present`, sealed bytes equal the
  baseline); before the marker the intent / marker failure refuses with nothing consumed (JOURNAL_WRITE_FAILED /
  MARKER_WRITE_FAILED); at resume the attempt counter does not move; close refuses cleanly.
* (ii) `_journal(durable=True)` on every advance made after the spool result, the pending ref or the seal (in
  `persist_and_seal` and every `seal-only` path): a conflict or an infrastructure failure is recorded
  (`JOURNAL_FAILURES`, sealed in `lifecycle`) and never stops the seal (L03 lock at F8: the run seals itself, the
  journal lags, `recover` catches it up; L04 a genuine conflict at F8: sealed). Before any durable artifact a genuine
  conflict still raises LostOwnership (checkpoint path unchanged; M34 / M35 cover both directions).
* (iii) `git_lockfiles` / `git_lock_info` in every classification (value-free, read-only; the state itself is
  unchanged); stale only if no live campaign process (journal process, pidfile, recover-lock holder) and `lsof` finds
  no open handle; `recover` (every state except CONSUMED_COMPUTING, before resume / seal / close) moves each stale
  lockfile under the O_EXCL campaign lock into `<spool>/git-locks-aside/`, never deletes it, fsyncs both
  directories and appends a value-free record to `recover-actions.jsonl` (sealed in `lifecycle`); held locks: exit 8,
  nothing done; `execute` / `resume` / `seal-only` / `close-indeterminate` refuse GIT_LOCKED. Tests L01-L11 assert
  the frozen final states (SEALED with the baseline's certified bytes, one marker, no recomputation of verified
  checkpoints, the lock moved and recorded, or the refusal with nothing done) — I read every assertion; they are
  specific, not vacuous.
* (d) pre-marker wedge fixed: an ABORTED_INTENT journal without a marker and with a dead process is taken over by the
  next `execute` (L01 b: MARKER_WRITE_FAILED -> NO_TARGET_CONSUMED -> recover moves the lock -> execute seals; M39).
* **C-1 (my own condition was too wide; required before the freeze, checkable in the R3 delta).** I listed
  `packed-refs.lock` in R1 (iii) and the builder followed it. My probe shows a stale `packed-refs.lock` never blocks the
  campaign's ref writes (creates / updates; the campaign never deletes a ref), so the campaign never owns that lock:
  whenever it exists it belongs to some other git process of the SHARED repository (gc / pack-refs / a ref deletion
  in any worktree). A live git holder is invisible to `lsof`: my probe (scratch repository, `git update-ref --stdin`
  with `start / delete / update / prepare`) held `packed-refs.lock` and a ref lock with NO open descriptor (lsof rc
  1 on both; L11 holds the file open with Python, which a real git process does not), and the "live campaign process" test is irrelevant
  to a foreign holder. Moving it aside can therefore break the lock protocol of a live foreign `pack-refs` and lose
  refs of the shared repository. Correction: drop `packed-refs.lock` from `git_lockfiles` (the campaign's move-aside
  set and its GIT_LOCKED refusals after the marker); MB r1's carried `check_clean` keeps refusing it before the marker
  (nothing consumed). Adjust L09 / L11 and M38 accordingly.
* N-1: `cas_ref` treats "the ref now holds `new`" (our own write landed but update-ref reported failure) as a
  conflict. Safe direction (at worst an evaluation classified UNRECORDED / an attempt ending LostOwnership), but
  `cur == new` should count as success.
* N-3: `git_lock_info` uses `identity_alive` (a failed `ps` reads as dead); the positive-evidence `identity_state`
  added for R2 would be the consistent choice.

## R2 (DEF-2: launcher boot-out) — MET (with note N-2)

* `launch()` never boots out after `launchctl bootstrap` (its `except BaseException` only re-raises; only a failed
  bootstrap removes the plist). The launcher's detachment proof is still computed and recorded, and the driver's own
  check (XPC_SERVICE_NAME = label, PPID 1, `launchctl print` names this pid) remains the gate.
* `wait_and_cleanup` and the new `cleanup <label>` boot out only when `HOST.identity_state(recorded identity)` is
  DEAD (boot UUID changed, pid gone, or pid reused with another start time / command); a failing, timed-out or
  unparsed `launchctl print` decides nothing; without a recorded identity nothing is booted out.
* Tests (re-run PASS with my labels): `t_wait_cleanup_ignores_failing_print` (planted `launchd_job_pid -> None`:
  `cleanup` refuses STILL_RUNNING, `wait_and_cleanup` keeps waiting while the identity is ALIVE, boots out only after
  the job stops); `t_launch_never_boots_out_after_bootstrap` (planted failure after the bootstrap: the job lives).
  Mutants M40 / M41 (results below).
* **N-2 (recommended before the freeze).** `identity_state` compares against the recorded fields without checking that
  they were recorded: an identity recorded while `ps` failed (`start_time` or `command_sha256` None) reads DEAD for a
  live process (my probe). In practice this fires at the launcher's first poll, seconds after the launch, while the
  driver is still in its pre-marker checks and controls (so nothing is consumed), i.e. it is fail-safe by timing, not
  by design. Fix: return UNKNOWN when any recorded field is missing (or refuse to record a partial identity).

## R4 (DEF-4: gate tests) — MET

* New behavioural tests (read; re-run results below): `t_gc10_start_gates` (the DRIVER's `host_preflight` on planted
  vm_stat / ps readings: low memory and an unreadable vm_stat fail exactly `free_memory_ge_min`; a busy foreign process
  fails exactly `host_exclusive`; an allow-listed and an own-child busy process pass); `t_pins_execute_platform` /
  `t_pins_resume_platform` (a planted pin: execute refuses with nothing consumed; resume refuses before the attempt
  counter moves, state stays CONSUMED_INTERRUPTED, restored -> resume seals); the same pair for a pinned research input
  (REGISTRY_C2) and for a science module changed after import, plus a science module changed before start
  (SciencePinError at import); `t_gc8_evidence_at_head_and_mbr1_branch` (an NSF/evidence path committed at HEAD but
  absent from the worktree, and one on MB r1's branch, each refuse MBR1_STATE with the specific reason).
* Mutants M42 (free-memory gate), M43 (exclusivity gate; identical to my X2), M44 (`check_platform` compares nothing;
  identical to my X3), M45 (research pins not re-verified), M46 (science pins not re-verified), M47 (GC-8 evidence at
  HEAD / MB r1's branch ignored).

## R3 (DEF-3 / M1: untraceable constants) — PARTLY MET (ratification complete; application open) => NOT MET

* **Coverage: complete.** `CONSTANTS_RATIFICATION_MBS308.md` (3c2a7854, CONSTANTS_RATIFIED_WITH_CHANGES, ratifierMBS,
  non-holder statement and one disclosed inadvertent subject-line exposure) rules on exactly the 20 items my s10 marked
  (d): 4, 5, 10, 11, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 30, 31. Sixteen are ratified as they
  stand, each with a written rationale from tonight's host readings (H1-H4), the ratifier's own dev decoy (D1), the
  builder's dev decoy figures (D0), MB r1's pre-grant official qualification decoys' resource fields (Q) or code
  reading; none rests on the MB r1 target run, and none can affect Γ.
* **Changed rulings, NOT applied** (erratum E1; verified at 35cabb50): items 10/11 (MEM_CAP by rule R-MEM at the
  freeze; the provisional 3 GiB ratified for the pre-freeze build only), 14 (FREE_MEM_MIN by R-FREE; provisional 2 GiB
  ratified), 15 (25 % with the single R-EXCL-PCT exception), 16 (EXCL_ALLOW by R-ALLOW; provisional list = the 39
  names ∪ {spotlightknowledged.updater, cloudd, BackgroundShortcutRunner, modelcatalogd}), 31 (the launcher's 1900 s
  recorded as the rule PRE_CAP_S + 100). At 35cabb50: EXCL_ALLOW still holds the 39 names; `pre_launch` still passes
  the literal 1900; the protocol draft's s8 carries none of R-MEM / R-FREE / R-EXCL-PCT / R-ALLOW. Tonight the gate as
  built would refuse on the four OS daemons (ratifier H3).
* **My erratum:** my s10 row 16 said "41 macOS process names"; the set holds **39** (the ratifier is right).
* **New operational role since the ratifier's read (35cabb50):** the ref-write retry schedule (R1 i) reuses MB r1's
  `SEAL_RETRY_DELAYS` = 0.5, 1, 2, 4 s (source (a): MB r1 driver l.104; completion only). It is traceable, so M1 is
  not engaged, but the ratification should list it (item 33).
* **M33 determinism (in R3's scope per brief 43 / E1): open.** The matrix's `t_S01_worker_death` kills M33 only when a
  sibling worker happens to be mid-job. My probe with the builder's proposed spec (`worker_die RLR.0.6`, `job_sleep
  90`, synthetic, sleep only): unmutated sealed TARGET_EVALUATION_FAILED in 9.6 s; with M33, 98.4 s. Under S01's
  existing 60 s bound that run kills M33 deterministically, but it is not in the test yet.
* Ruling: **R3 NOT MET** (partly met: coverage and rulings complete; the changed rulings, the protocol text and the
  deterministic M33 run are unapplied). A bounded R3 application + an R3-only delta suffices (plus C-1, below).

## M4 (builder2's diff changed no operational number) — PASS

Every changed code line with a digit at 35cabb50 vs afba20e5 (`git diff -U0`, code/ only) is: the three re-pinned
helper sha256s; exit code 8 re-used for "held locks, nothing done" (its existing meaning, wait); file modes 0o700 /
0o600 and `token_hex(3)` as used elsewhere; the fault hook's test-only `plant` / `bump_journal` actions. The
launcher's 15 s / 2 s / 1900 s, WORKERS, the caps, MEM / FREE / EXCL values, MAX_RESUMES, DEADLINE_S, CKPT_FAIL_LIMIT,
lock retries and all poll intervals are unchanged. The only new timing is the reuse of `SEAL_RETRY_DELAYS` above. One
number was REMOVED: `wait_and_cleanup`'s `timeout_s` (the waiting launcher now waits for the recorded identity's death
without a bound; the job is detached, so this is benign). Test-only values (`retry_delays=(0.8,)`, planted readings,
8 GiB / 0.5 GiB) are outside the operational set.

## Work log (continued)

* 23:51Z state suite: **44/44 PASS**.
* 23:50Z M33 probe (own script, sandbox, synthetic, sleep-only jobs): unmutated 9.6 s -> sealed TARGET_EVALUATION_FAILED
  (BrokenProcessPool); M33 98.4 s -> same status. The proposed spec kills M33 deterministically under S01's 60 s bound.
* **Rule deviation, disclosed (mine).** My first full-matrix stream called the builder's runner unwrapped. Its
  unmutated phase ran two NEW launch tests directly, so two synthetic-payload LaunchAgents were bootstrapped under the
  BUILDER'S label prefix, not my review prefix: `org.rebaseguard.mbs308.test.nb20260929T234837593188` and
  `org.rebaseguard.mbs308.test.wc20260929T234840555396` (plists in my scratch; each booted out by the test's
  teardown; the tests passed). Their empty (0-byte) stdout / stderr logs landed in
  `~/Library/Logs/ReBaseGuard/mbs308-test/` (left in place, not deleted). No other effect: synthetic payload only, no
  launchd job remains, no repository write. At 00:03Z I stopped that stream after M10 (M01-M10 KILLED, 43 unmutated
  targets PASS) and restarted M11-M47 with a driver that routes every `launch::` target through my review-label wrapper
  (plists and logs in my scratch), re-running the unmutated launch targets under review labels first.
* 00:04Z crash suite: **47/47 PASS** (F1-F12 x exit/kill, S01-S12, L01-L11).
* 00:03Z-00:14Z mutants M11-M47 (launch targets under review labels; the unmutated launch targets re-run first under
  review labels: 4/4 PASS).

## Mutant matrix (re-run in full, 47 mutants) — 46/47 killed; M33 survives (R3 scope)

* Unmutated: every target test PASS (43 in stream 1; the 4 launch targets again under review labels).
* Killed: M01-M32 and M34-M47, each by an assertion of its own target test (per-mutant result files checked: no kill
  by exception, timeout or missing result). The repair mutants: M34 (every ref-write failure a conflict), M35 (a
  conflict after the durable result stops the seal), M36 (recover never moves stale locks), M37 (pidfile liveness
  ignored), M38 (open-handle guard ignored), M39 (aborted intent blocks execute), M40 (boot-out on one negative
  `launchctl print`), M41 (boot-out after the bootstrap), M42-M47 (R4 gates): all KILLED. **My earlier X2 and X3 are
  M43 and M44 verbatim: both now die** (t_gc10_start_gates; t_pins_resume_platform).
* **M33 SURVIVED** (55.3 s < the 60 s bound: no busy sibling this time), exactly as builder2 disclosed. My original
  review's M33 kill (143.7 s) was the same luck. The deterministic run is part of the unapplied R3 work (see R3).

## Verdict

**DELTA_REJECTED**, ruled per condition so that the next step is bounded:

| condition | ruling |
|---|---|
| R1 (DEF-1) | **MET** — plus correction **C-1** (drop `packed-refs.lock` from the campaign's lock set; verify in the next delta) |
| R2 (DEF-2) | **MET** — note N-2 (partial identity reads DEAD) recommended before the freeze |
| R4 (DEF-4) | **MET** — X2 / X3 (= M43 / M44) now killed |
| R3 (DEF-3 / M1) | **NOT MET** (partly met): the ratification covers all 20 untraceable items and none affects Γ, but its changed rulings, the protocol s8 rules and the deterministic M33 run are unapplied |
| M4 | **PASS** — builder2 changed no operational number |

Re-runs at 35cabb50: static 9/9, launch 8/8, state 44/44, crash 47/47, mutants 46/47 (M33). Scope unchanged (NSF
bytes, guard, 46 carried science definitions, DRIVER_DIFF complete). Real repository: no ref created or moved (only
MB r1's marker -> afa93072 under either prefix), worktree clean at 35cabb50, no spool, real object store since 23:39Z:
nothing freshened, no pack changed, no MB-S / sandbox object; no launchd job and no stray process left.

**Not IMPLEMENTATION_ACCEPTED yet.** After a bounded application of R3 and C-1, the build becomes
IMPLEMENTATION_ACCEPTED as a pre-freeze candidate if an **R3-only delta** (which also checks C-1) confirms:
1. EXCL_ALLOW = the 39 names ∪ {spotlightknowledged.updater, cloudd, BackgroundShortcutRunner, modelcatalogd}
   (provisional; R-ALLOW at the freeze); the launcher's preflight timeout written as PRE_CAP_S + 100; the protocol
   draft's s8 carrying R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW verbatim, with MEM_CAP / FREE_MEM_MIN / EXCL_CPU_PCT /
   EXCL_ALLOW frozen as rule outputs from official evidence; no other operational change;
2. `t_S01_worker_death` gains the run `{"worker_die": "RLR.0.6", "job_sleep": 90}` under its 60 s bound, and M33 is
   killed by it (run the mutant at least twice);
3. C-1 applied (L09 / L11 / M38 adjusted); the ratification (or its application record) lists the ref-write retry
   schedule's reuse of SEAL_RETRY_DELAYS.
Recommended in the same pass (not gating): N-1 (`cur == new` is success), N-2 (partial identity -> UNKNOWN), N-3
(positive-evidence liveness for lock staleness).

**Still before any freeze (unchanged):** the qualification verifier, manifest writer and leak scanner; re-pinning
HELPER_SHA256 and PLATFORM_PINS; the official decoys under the launchd launcher (Q12 re-measured; the R-MEM / R-FREE /
R-ALLOW inputs); full MBR1_REPRO and QS-RESUME-DECOY; automatic macOS / critical-update installation disabled by the
user; and the user decisions S1, S16(c), MBS-6, MBS-7, MBS-8 (MBS-8 stating the per-attempt awake-time EVAL_CAP).
