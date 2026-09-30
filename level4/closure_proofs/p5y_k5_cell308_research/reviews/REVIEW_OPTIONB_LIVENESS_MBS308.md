# Cell-308 successor MB-S r1: narrow delta review of option B (W, N) and the liveness delta (L) at 216c465f (reviewB5)
DELTA_ACCEPTED

Reviewer: **reviewB5**, a fresh reviewer who is not a holder of any MB r1 run observation, independent of the builder
(`builder3`), the editor (`editorR3C1`) and the earlier reviewers (brief 47, recorded at research 3ac53e11, corrected text
324ba37f). Started 2026-09-30T11:20Z, finished 13:04Z. Object: successor branch `p5y-k5-cell308-mbs-r1`, three additive
commits on 191ce4a9: W `4a960e061ee78b2799f9a750e90b70a4e728e8a4`, N `b0dd8e937389d7d8f24bad8087863852b13309ae`,
L `216c465fd48d779ceef876fd13b1422773dfea31`. The worktree was clean at L throughout, so every run below exercised the
committed bytes of L (W and N were read with `git show` and, for the R3 gates, run from code copies of their bytes).
New cell-308 target evaluations by this review: **0**. I evaluated no cell in 305-309 and no drift in [6/5, 13/5] or its
mirror; I did not touch cell 309; I created no authorization, grant, marker, pending result or seal; I made no git write.

## Reading, and my own exposure

Read: brief 47 and brief 45; CONSTANTS_RATIFICATION_MBS308 (3c2a7854; unchanged at the research HEAD); the user ruling's
ledger line (5e7b8cdc); REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 (58cfe66b; header, sections 3, re-runs and verdict); the
diffs 35cabb50..191ce4a9..W..N..L of the namespace; the successor's code, tests and protocol section 4; BUILD_REPORT
section 14 (the heading list only for the rest; section 9 not opened); the research ledger's OPTION_B_RECHECK.json and
the ENOSPC folder (audit, tool, audit JSON, contaminated file, the coordinator's deletion list, the L_final_* reports);
builder3's reports and per-mutant result files (the brief's explicit exception; nothing modified); the quarantine
module's `log_event`. **Not opened:** any REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*,
REVIEW_SUCCESSOR_GOVERNANCE_308*, INCIDENT_INDEPENDENCE_REVIEW_MBS308* (T6 included), COORDINATOR_EXPOSURE_DISCLOSURE*,
anything under `p5y_k5_cell308_mb_r1/{review,adjudication,postexec,evidence}/`, BUILD_REPORT section 9, any other
session's or agent's scratchpad (builder3's evidence excepted), anything under `/Users/suzhe/.claude/`.

**Exposure disclosed.** My session began with the user's auto-loaded memory index in context (I opened no file of it).
Its lines touching MB r1 are: the outcome label of MB r1's one execution together with the successor's pre-freeze status
(the label the allowed governance texts carry), a lesson line that host sleep and thermal slowdown inflate wall times
(provenance unknown to me; it may derive from MB r1's run), and a successor-lessons line (packed-refs.lock, timing-
dependent kills, positive evidence for liveness). None carries a per-job, progress, CPU, memory, host or science figure;
I repeat none of it, and no judgment below depends on it. My `git log` of the successor worktree showed only the six
MB-S commit subjects (afba20e5..216c465f), not MB r1's. Nothing else in my context is an MB r1 run observation.

## Work log (UTC; all sandbox runs on my own `git clone --no-local --bare` base store `reviewB5/base_store.git`)

| time | step | result |
|---|---|---|
| 11:23 | own base store (clone of the successor repository, 465 MB, no alternates); 116 GiB free | - |
| 11:24-11:25 | static, launch suites | 10/10, 10/10 |
| 11:26-11:40 | state, crash suites (in parallel, separate scratches) | 46/46, 50/50 |
| 11:36-11:46 | own byte-level re-check tool `optionb_recheck_reviewB5.py`; liveness probe `liveness_probe_reviewB5.py`; TZ probe | all checks PASS; findings O-1..O-4 below |
| 11:44 | R3 gates on code copies of W and N | W: 3/3 FAIL by assertion; N: 3/3 PASS |
| 11:48-12:27 | full mutant matrix (57) | 57/57 KILLED by assertion; unmutated 51/51 PASS |
| 12:30-12:45 | own supplementary mutants (20) | 14/14 intended kills; 6 survivals explained below |

Free space on the data volume: 116 GiB before my first run, 118 GiB at the matrix start, 72 GiB at its end (its
sandboxes), 117 GiB after I deleted every sandbox of mine (the JSON reports and per-mutant result files are kept in
`.../scratchpad/reviewB5/reports`, `/mx`, `/xm`). No run of mine saw less than 72 GiB.

## 1. Option B — MET

* **(a) W restores exactly the two spans — MET.** My tool (`git show` only): `code/mbs308_launch.py` at W is byte-identical
  to 35cabb50. The driver at W differs from 191ce4a9 in exactly three places: the launcher pin (now c829b9ed…, the sha256
  of W's launcher), the editor's comment line above `EXCL_ALLOW` (removed), and the literal's tail (its last two lines,
  which carried the four names, become 35cabb50's closing line). The `EXCL_ALLOW` assignment plus the line above it is byte-identical to 35cabb50's; the rest of the driver,
  with the pin masked, is identical to 191ce4a9. W changes no other file except DRIVER_DIFF.md. Run from a copy of W's
  code, the three R3 gates FAIL by assertion (static: excl_allow old 39 / new 39; launch: 1900 when PRE_CAP_S is 1234;
  state: each of the four daemons refused HOST_PREFLIGHT), as brief 45 expected.
* **(b) EXCL_ALLOW at N = the 39 of 35cabb50 ∪ the four of item 16, nothing else — MET.** Parsed from the ratification
  text at 3c2a7854: item 16's "Provisional for tonight's build" set and "Changes requested" 2 both give
  {spotlightknowledged.updater, cloudd, BackgroundShortcutRunner, modelcatalogd}. N's literal (AST): 43 elements, 43
  unique; its first 39 are 35cabb50's in order; the four are appended in the ratification's order; nothing removed; the
  four are disjoint from the 39. The literal equals 191ce4a9's element for element; only its comment differs.
* **(c) The launcher timeout is the rule PRE_CAP_S + 100 and follows the driver without importing it — MET.** AST of N's
  launcher: `pre_launch` passes `timeout=PRE_CAP_S + 100`; module-level `PRE_CAP_S = driver_pre_cap_s()`, which parses the
  driver's bytes with `ast.parse`. The launcher imports only the standard library and `mbs308_host`; it has no `exec`,
  `eval`, `compile`, `__import__`, `importlib` or `runpy` call. The driver binds `PRE_CAP_S` exactly once anywhere in its
  AST (`PRE_CAP_S = 1800`). Loading the launcher in a separate interpreter from throw-away copies: 1800 → timeout 1900;
  a copy with 1234 → 1334; missing, bound twice, a string, or an expression → `LaunchRefused(DRIVER_PRE_CAP_S)` at load.
  No driver or science module was ever in `sys.modules`. Non-blocking note N-B1: the reader looks at top-level
  statements only, so a future driver that rebinds PRE_CAP_S inside a module-level `if`/`try` block would not be seen
  (my probe: the launcher keeps 1800). It is inert at the committed bytes (one binding in the whole AST) and the freeze
  binds the bytes; if the driver is ever edited, walking every `Store` of the name would close it.
* **(d) Byte-level comparison of N with 191ce4a9 — MET, no operational difference.** Of the namespace's 20 files, 17 are
  byte-identical. The three that differ, every difference:
  1. `code/mbs308_driver.py`: the launcher pin (38cb35a3… → 1510308a…, the sha256 of N's launcher) and the one-line
     comment above `EXCL_ALLOW` replaced by a two-line comment. Comments and a pin: not operational.
  2. `code/mbs308_launch.py`: the module docstring's sentence about the rule (reworded), `pre_launch`'s docstring (one
     clause added), and the reader: the editor's `driver_literal(name)` (first top-level `Assign` match, `RuntimeError`
     when missing, placed before `LaunchRefused`) is replaced by builder3's `driver_pre_cap_s()` (exactly one top-level
     binding, an `int` literal, else `LaunchRefused("DRIVER_PRE_CAP_S")`, placed after `LaunchRefused`), with its own
     comment. The timeout expression `PRE_CAP_S + 100` and its value at the committed driver (1900 s) are identical. The
     only behavioural difference is on a malformed driver, where N refuses to load in more cases (stricter, fail closed).
     Not an operational value.
  3. `DRIVER_DIFF.md`: the header's driver sha256, hunk 4's launcher pin, hunk 8's comment (one line → two), and 16 hunk
     headers whose new-side start moves by one line. Consequences of 1.
  The coordinator's OPTION_B_RECHECK.json (b3cc9675) reports the same three files and the same lines; I agree with it,
  from my own tool.
* **(e) Pins and DRIVER_DIFF.md — MET.** At W, N and L (and 191ce4a9 as a control) every `HELPER_SHA256` entry equals the
  sha256 of the helper in the same commit; the DRIVER_DIFF header names the driver's sha256 and MB r1's base
  (c46434a3 = 21e99cf0 bytes, 411252b2…); its 22 diff blocks equal, block for block, my own
  `difflib.SequenceMatcher(autojunk=False)` 3-line-context hunks, and applying them to the base reproduces the driver
  byte for byte. Outside the diff blocks only the header sha line changes from 191ce4a9 to N and from N to L; the
  index table and class counts (IDENTITY 1, IDENTITY + LIFECYCLE 10, LIFECYCLE 11) are consistent. builder3's scratch
  copies of DRIVER_DIFF at W/N/L are byte-identical to the committed files.
* **(f) R3 gates and M51 / M52 — MET.** static `t_r3_ratified_rules_applied`, state `t_gc10_ratified_allow_list` and
  launch `t_preflight_timeout_rule` PASS at N (code copy) and at L (full suites). In the full matrix M51 and M52 are
  KILLED by their targets' own assertions. My B1 (the timeout is `max(PRE_CAP_S, 1800) + 100`: right at 1800, does not
  follow a smaller value), B2 / B2s (one daemon misspelt) and B3s (a 44th, unratified name) are KILLED as well, so the
  gates test "follows the driver" and "exactly 39 + 4", not just the current value.

## 2. Liveness delta — MET

* **(a) Only the two named sites; the rule — MET.** L's change to `code/mbs308_state.py` is: `Lock.acquire`'s test
  `HOST.identity_alive(holder)` → `_not_dead(holder, None, None)` (plus the class docstring), and the classifier's
  CONSUMED_COMPUTING test `HOST.identity_alive(jrec.get("process"), cur_boot)` → `_not_dead(jrec.get("process"),
  cur_boot, None)` (plus a comment and the value-free why code `PROCESS_NOT_PROVABLY_DEAD`, which nothing reads). Both
  reuse N-3's `_not_dead` unchanged: a dict identity counts as alive unless `HOST.identity_state` returns DEAD; not a
  dict, or a dict whose pid is missing / None, is "no process". The other code changes of L are the state pin in the
  driver and the regenerated DRIVER_DIFF. `read_pidfile` and `check_not_evaluated` keep `identity_alive`, as the brief
  fixes and protocol section 4 states.
* **(b) The classifier and Lock.acquire tests are specific and non-vacuous — MET.** `state::t_computing_ps_failure_not_interrupted`
  plants a journal whose recorded process is a live helper with `ps` failing only for its pid, with an in-process control
  that the planted reading is UNKNOWN; no recover lock is planted, so the classifier alone decides (my run: COMPUTING,
  recover rc 8 "-> wait", resume RESUME_REFUSED, refs unchanged; then INTERRUPTED, recover rc 0, SEALED with the
  uninterrupted certified bytes, attempt 2). `crash::t_S13_lock_ps_failure_not_broken` plants no git lockfile and keeps
  the journal naming the dead crashed driver, so `Lock.acquire` alone decides (LOCKED, the lock byte for byte, nothing
  aside; then broken once, resumed, sealed, no verified checkpoint recomputed). Both kill their site's revert (M53, M54)
  and my ALIVE-only variants through `identity_state` (Y1, Y2), and both kill the gate made unconditional (NC3: a
  recorded process always computing; NC4: a lock with any holder never broken), each by assertion.
* **(c) The L12 extension tests the journal source on its own and kills X4 — MET.** `crash::t_L13_lock_sources_ps_failure_each`
  calls `git_lock_info` directly on the sandbox's own (possibly mutated) modules, with each source in turn naming the
  live, `ps`-failing helper while the other two name the dead crashed driver: my run gives `live == ["journal_process"]`,
  `["recover_lock"]`, `["pidfile"]` respectively, not stale, and `live == []`, stale, before and after the helper. My X4,
  written as the exact pre-N-3 text of the journal source (35cabb50: `identity_alive` + the pid exclusion), is KILLED by
  L13's assertion (its journal case reads `live []`, stale). The same X4 against the old L12 alone SURVIVES, which
  confirms that L13 is what closes reviewR3C1's coverage note. X4b (journal source dropped) and X6 (recover-lock source
  dropped) are KILLED, and so are NC1 / NC2 (either source listed whenever a record exists: the dead case fails; NC2 is
  non-vacuous because the crashed driver leaves its recover lock).
* **(d) No new operational number — MET.** L changes no cap, limit, timeout, threshold, allow-list entry, budget or poll.
  Test-only values: the existing `T.Helper` for 300 s / 120 s, the existing F3 crash at the 4th checkpoint, planted `ps`
  failures for the helper's pid only.
* **(e) Consequences stated in protocol section 4 — MET.** The new *Liveness of a recorded process identity* paragraph
  states the one rule for the classifier, the recover lock and the git-lockfile test, and the fail-closed consequence:
  while `ps` keeps failing for an existing recorded pid, or the boot-UUID read keeps failing at all, the run stays
  CONSUMED_COMPUTING (recover exit 8; resume, close-indeterminate, seal-only refuse) and the lock is LOCKED, with no
  timeout, until positive evidence. My probe confirms the "at all" clause (a dead pid with the boot-UUID read failing is
  still not dead). Non-blocking wording note D-1: the CONSUMED_UNRECORDED row's closing clause ("all only when the
  recorded process is positively dead") does not hold for its first five conditions (no / invalid / unbound journal,
  CLOSING, ABORTED_INTENT), which the code, following the table's "checked in this order", returns before the liveness
  test; this was already so with "not alive" at 191ce4a9, and it is safe because every action on those states then takes
  `Lock.acquire`, which applies the same rule. A clause naming the order would make the row exact.

## 3. ENOSPC incident — ruled: no evidence this review or the delta relies on was produced or invalidated by disk exhaustion

* **What I checked in builder3's evidence** (reports and every per-mutant `result.json`, independently of the audit
  tool): every JSON parses, none is zero-length (the two zero-length files are builder3's empty `MX2_alerts.*` logs);
  no ENOSPC / "No space left" / Errno 28 / "unable to write" / "invalid object" text outside the one contaminated run
  (the audit's "truncated" hits are the planted test case `t_S06_truncated_result`); MX2 (09:11-09:47Z, after the
  cleanup at 08:59:48Z): 57/57 killed, each result file `ok` false with no `error`, unmutated 51/51 PASS, no error field
  anywhere. The contaminated file in the ledger has the same sha256 as builder3's original (b79b821d…); its unmutated
  phase failed on "unable to write new index file", an "invalid object" during checkout and a missing sandbox, so its
  "6/6 killed" means nothing; it is superseded by L3 (6/6 by assertion, unmutated PASS), by MX2 and by my runs. The
  coordinator's deletion list has 126 entries, all `sbx` clones or `base_store.git` under `scratchpad/editor` or
  `scratchpad/reviewR3C1`; none touches builder3's evidence.
* **Could exhaustion have faked a result?** A disk failure shows as an exception, a failed clone or git write, a missing
  result or a failed assertion, so it can fake a kill or an unmutated failure, but not a PASS: each new test asserts
  exact refusal codes and then a successful resume and seal. The pre-cleanup suites were all PASS with no error, and the
  step-W failures carry their specific causes (39 names; 1900 at 1234; HOST_PREFLIGHT), not disk symptoms.
* **Re-established on ample disk by me**, on the committed bytes of L: static 10/10, launch 10/10, state 46/46, crash
  50/50, the full 57-mutant matrix 57/57 (unmutated 51/51), the R3 gates at W and N, and my own 20 mutants; at least
  72 GiB free throughout; every kill checked in its result file (`ok` false, no `error`, rc 1, no missing result). The
  audit's conclusion (one contaminated run, preserved and superseded; nothing else affected) is confirmed.

## 4. Safety questions

* **(a) Can a failed `ps` or boot-UUID reading be read as positive evidence that a recorded live process is dead, in the
  repaired paths? — No.** `identity_state` returns DEAD only on a recorded boot UUID that differs from a successfully
  read one, on `kill(pid, 0)` raising ProcessLookupError (the kernel, not `ps`), or on a successfully read start time or
  command that differs from a recorded field. A failed read is `None` (`_run` returns stdout only on exit 0; timeouts
  and OSError give `None`) and returns UNKNOWN; the classifier's `None` boot UUID is re-read inside `identity_state`.
  My in-process probe on L's code: a live holder is UNKNOWN / not dead with `ps` failing, with only the command read
  failing, and with the boot-UUID read failing; `Lock.acquire` then refuses LOCKED with the lock bytes unchanged in
  each case. Caveats, both outside the delta: coverage note K-1 (no test plants a boot-UUID failure or a command-only
  failure, so my Y5 / Y6 mutants, which turn those UNKNOWN branches into DEAD, survive every target; the code is right,
  a regression there would go unseen); observation O-4 (`ps -o command=` reports an unreadable argument vector as
  `(name)` with exit 0, a failed reading that looks successful; in my sampling it occurred only for processes 0-1 s from
  exec or exit, and the repaired paths compare self-recorded identities of long-running processes, so I found no path
  where it reads a live driver dead). Finding O-1 below is not a failed reading but a successful one misread.
* **(b) Is Lock.acquire safe? — Yes (for every lock carrying a recorded identity).** A live holder's lock is never broken
  under `ps`, command or boot-UUID failure (probe and S13; M54 / Y2 / NC4 killed). A dead holder (pid gone, even with
  `ps` failing for that pid), a rebooted holder and a reused pid are broken, moved aside once, and the lock taken. The
  LOCK_RACE path is unchanged by L (one line of `acquire` changed) and works as designed: simulating a second breaker
  that replaces the lock between the read and the rename, `acquire` refuses LOCK_RACE and restores that breaker's lock
  byte for byte. Two pre-existing observations, unchanged by the delta: O-2 (a lockfile caught between its O_EXCL
  creation and its identity write reads as "no recorded identity" and is breakable; a window of one write, backed by
  the journal CAS) and O-3 (after that LOCK_RACE put-back the lock has two links, which `spool_read` refuses, so every
  later `acquire` refuses LOCK_RACE and `release` cannot remove it: fail closed, but the campaign lock stays wedged until
  a manual action).
* **(c) Is the classifier / resume behaviour safe? — Yes, for the delta's subject; one pre-existing exception (O-1) is
  reported.** A live recorded driver whose identity cannot be verified is CONSUMED_COMPUTING: recover waits and resume
  refuses (the new state test; M53 / Y1 / NC3 killed; under Y1 the test shows recover resuming and sealing next to the
  live helper, which the unmutated code prevents). A positively dead driver resumes (the second half of that test, S13,
  the F-series) and a rebooted one resumes (`t_reboot`; M15 re-targeted and killed). The running `execute` also holds
  the recover lock, so a resume beside it must pass both the lock and the classifier, now under the same rule.
  **O-1:** `process_start` compares `ps -o lstart=`, which prints local time; a change of the system time zone during a
  run changes the string for the same live process, so `identity_state` returns DEAD for a live driver. My probe (a
  sleep helper, TZ changed after its identity was recorded): ALIVE → DEAD, and `identity_alive` false. This reaches the
  classifier, `Lock.acquire`, `git_lock_info` and the launcher's `wait_and_cleanup` (which would boot out a live job),
  and it was identical at 191ce4a9 and 35cabb50; it is not introduced by W, N or L. I recommend it as a required
  pre-freeze repair with its own non-holder review (a time-zone-independent start time; no operational number needed).
* **(d) Does L12/L13 test the journal-recorded process on its own? — Yes.** L13's journal case has the journal alone
  naming the live, `ps`-failing process (pidfile and recover lock name the dead crashed driver) and requires exactly
  `live == ["journal_process"]`; its end-to-end part shows recover waiting (rc 8, lockfile intact) and, after the helper
  dies, moving the lockfile aside (recorded) and sealing.
* **(e) Is reviewR3C1's X4 killed? — Yes.** My own X4 (pre-N-3 text of the journal source) is KILLED by L13's assertion;
  builder3's M55 (the same revert without the pid exclusion) is KILLED in my full matrix; X4 against L12 alone survives.
* **(f) Are the negative controls non-vacuous? — Yes.** Each new test fails when its gate is removed or made
  unconditional: M11 (classifier gate `if False`), NC3 (always computing), M54 / Y2 (lock broken on UNKNOWN), NC4 (never
  broken), X4b / X6 (a source dropped), NC1 / NC2 (a source always live): all KILLED by the target's own assertion.
* **(g) No target exposure anywhere? — Yes.** The delta touches no science and no target path; every run here used the
  synthetic evaluator in sandboxes or planted readings; the only real-driver invocations were the launch suite's
  read-only `preflight` and the static suite's `status` in sandbox copies, as in the earlier reviews. 0 target
  evaluations by the builder (section 14) and by me.

## 5. Scope and governance — MET

* **Files.** Across W, N, L the repository paths that changed are the nine namespace files of the brief: W and N touch
  only the driver, the launcher and DRIVER_DIFF.md; L touches `mbs308_state.py` (the two sites), the driver (state pin),
  DRIVER_DIFF.md, protocol section 4, the state / crash / mutant tests and BUILD_REPORT (section 14 appended; 0 lines
  removed from sections 1-13 in any of the three commits). M51 / M52's fragments occur once in N's bytes and were not
  edited. Beyond the letter of brief 45, M15 was re-targeted to `identity_state`'s boot comparison (same meaning, same
  target `t_reboot`) and its old fragment kept as M57 (`t_stale_pidfile`): this was needed because the classifier no
  longer reads `identity_alive`'s boot check (M15 survived the first matrix), and it keeps both facets covered. I accept it.
* **Operational values.** The only values of N are the ratifier's (item 16's four names; item 31's `PRE_CAP_S + 100`);
  L chooses none; the launcher's reader is a validation, not a value.
* **Builder's exposure statement.** Section 14 has it (memory-index lines, two MB r1 commit subjects, the editor's bytes
  read for step W) and discloses a size-only `du` over the project's temporary tree that traversed other sessions'
  directory metadata (no file opened, no names listed). Adequate; the `du` is a minor, disclosed deviation from the
  scratchpad rule that exposed no content.

## Findings outside the delta (none introduced by W, N or L; for the freeze preparation)

| id | where | what | direction | recommendation |
|---|---|---|---|---|
| O-1 | `mbs308_host.process_start` / `identity_state` | a system time-zone change makes a live process's `lstart` differ → DEAD | **unsafe** (resume beside a live driver; launcher boot-out of a live job) | required pre-freeze repair + review |
| O-2 | `Lock.acquire` | an empty lockfile (between O_EXCL create and write) is breakable | unsafe, one-write window; journal CAS second line | repair (e.g. create the lock with its content atomically) or rule |
| O-3 | `Lock.acquire` LOCK_RACE put-back | the restored lock has two links; `spool_read` refuses it; permanent LOCK_RACE, `release` cannot remove it | fail closed (liveness) | repair or rule before the freeze |
| O-4 | `process_command_sha256` | `ps` prints an unreadable argv as `(name)` with exit 0 | seen only at exec / exit | consider reading `(name)` as UNKNOWN |
| K-1 | tests | no test plants a boot-UUID read failure or a command-only read failure (Y5, Y6 survive) | coverage | add both cases to `t_identity_state_positive_evidence` |
| N-B1 | launcher reader | top-level bindings only | inert at the committed bytes | walk every `Store` if the driver is edited |
| D-1 | protocol §4 table | CONSUMED_UNRECORDED closing clause vs check order | wording | name the order |

## Re-runs on the committed bytes of L (counts)

| run | result |
|---|---|
| static | **10/10 PASS** |
| launch | **10/10 PASS** (synthetic payload; transient LaunchAgents `org.rebaseguard.mbs308.test.` 20260930T112527, ld20260930T112532, wc20260930T112534182751, nb20260930T112537865479; each booted out by its teardown) |
| state | **46/46 PASS** |
| crash | **50/50 PASS** |
| full mutant matrix | **57/57 KILLED**, every kill the target's own assertion (`ok` false, no `error`, rc 1, no missing result); unmutated 51/51 target tests PASS; M33 by its deterministic run only (95.6 s; the seven carried runs 5.9-6.7 s, passing); launch targets used wc20260930T115629339646, nb20260930T115626116522, wc20260930T122147253157, nb20260930T122150576084, all booted out |
| R3 gates at W / N (code copies) | W 0/3 (each FAILS by assertion, as expected); N 3/3 PASS |
| supplementary mutants (mine, 20) | unmutated 8/8 targets PASS; **KILLED** X4, X4b, X6, NC1, NC2, NC3, NC4, Y1, Y2, Y4, B1, B2, B2s, B3s (14/14 intended, all by assertion); **SURVIVED** X4_vs_L12 (expected: L12 plants only the pidfile), Y5 ×2 and Y6 ×3 (coverage note K-1) |
| option-B byte re-check (mine) | all checks PASS (report `reviewB5/reports/OPTIONB_RECHECK_reviewB5.json`, tool `optionb_recheck_reviewB5.py`, sha256 a3eb65cf…) |
| liveness probe (mine) | as in 4(a)/(b) (`reviewB5/reports/liveness_probe.json`, tool sha256 166f9d83…); TZ probe `tz_probe.json` |

## Integrity

* **Real repository:** the 144 refs are identical between my 11:47Z and 12:55Z snapshots; there is no ref under
  `refs/p5y-k5-cell308-mbs-r1/`; MB r1's marker still names afa93072; no `packed-refs.lock` and no `mbs308-spool` in
  the real git dir. Every sandbox was a `--shared` clone of my own base store (the harness asserts that the only
  alternate is that store). My only other git repository was a throw-away `git init` in my scratch for the in-process
  Lock probe (deleted by the probe).
* **Successor worktree:** clean at 216c465f before and after.
* **Launchd:** `launchctl list` shows no rebaseguard job; no plist in `~/Library/LaunchAgents` or my scratch; no stray
  mbs308 process. The tests' empty logs stay in `~/Library/Logs/ReBaseGuard/mbs308-test/`, as in the earlier reviews.
* **Research worktree:** my writes are six ledger lines (agent `reviewB5`, `new_target_evaluations` 0, no LEAK_FLAG; the
  last records this verdict) and this file. The coordinator commits them.
* **My scratch** (`.../scratchpad/reviewB5/`): the base store (458 MB), tools, JSON reports and result files; every
  sandbox deleted.

## Verdict

**Accepted** (the verdict on line 2).

| item | ruling |
|---|---|
| 1 (a) W restores exactly the two spans | **MET** |
| 1 (b) EXCL_ALLOW = 39 ∪ the four of item 16 | **MET** |
| 1 (c) timeout rule PRE_CAP_S + 100, follows the driver, no import | **MET** (note N-B1) |
| 1 (d) N vs 191ce4a9 byte-level: every difference listed, none operational | **MET** |
| 1 (e) pins and DRIVER_DIFF.md | **MET** |
| 1 (f) R3 gates pass; M51 / M52 killed | **MET** |
| 2 (a) only the two sites; alive unless DEAD; no identity = no process | **MET** |
| 2 (b) classifier and Lock.acquire tests specific, non-vacuous | **MET** |
| 2 (c) L13 tests the journal source on its own; X4 killed | **MET** |
| 2 (d) no new operational number | **MET** |
| 2 (e) fail-closed consequence stated in protocol §4 | **MET** (wording note D-1) |
| 3 ENOSPC | **ruled: no relied-on evidence affected; re-established on ample disk** |
| 4 (a) failed reading ever read as death | **no** (K-1, O-4 noted) |
| 4 (b) Lock.acquire safe | **yes** (pre-existing O-2, O-3 noted) |
| 4 (c) classifier / resume safe | **yes** for failed readings; pre-existing **O-1** reported |
| 4 (d) journal source tested on its own | **yes** |
| 4 (e) X4 killed | **yes** |
| 4 (f) negative controls non-vacuous | **yes** |
| 4 (g) no target exposure | **yes** |
| 5 scope and governance | **MET** |

Option B and the liveness delta are each independently satisfied. **The build at L (216c465f) remains
IMPLEMENTATION_ACCEPTED as a pre-freeze candidate.** Before any freeze (I choose no freeze parameter), in addition to the
items already listed by REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 and the user's instructions: **O-1** should be repaired
under its own non-holder review (I rate it required: it is the one path I found where a successful but misread
reading lets a resume start beside, or the launcher boot out, a live driver); O-2 and O-3 should be repaired or
explicitly ruled; K-1's two test cases are cheap and should be added; O-4, N-B1 and D-1 are optional.
