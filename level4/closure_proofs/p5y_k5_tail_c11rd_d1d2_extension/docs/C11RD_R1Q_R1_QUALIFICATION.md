# C11RD-R1Q-R1 — repaired qualification of the C11RD-R1 freeze

Scope: a QUALIFICATION-GOVERNANCE REPAIR only. Freeze `ce5b85959a1693525f9e001e7c191516a4ee7d76`
(pre-execution review preserved at `3c1eff11…`, READY_TO_QUALIFY) is unchanged. The rejected
qualification `3addf9d3c72d9274813fb5e06486b633a50a133c` and its review, preserved verbatim at
`8933053406b33cb4cc852dfd5b2231f507a552b3` (QUALIFICATION_REJECTED, blocker B-1), are immutable
historical evidence and were not edited. No authorization, no grant, no target execution, no
comparison. No cell-306 D1/D2 magnitude has been computed. Nothing under `code/`, `protocol/`,
`theory/` or any hash-bound document or input changed, and there is no scientific successor freeze.

Note identifiers are unique in this document and in the artifact (review QR1.N-12):
`R1R.N-k` = the C11RD-R1 pre-execution review (3c1eff11); `QR1.B-1`, `QR1.N-k` = the qualification
review of 3addf9d3 (89330534); `PRED.N-7` = the predecessor review (663f8fe7) note on an idle host,
which is the same requirement as `R1R.N-11`. (The rejected artifact's `authorization_requirements[2]`
and its doc section 3 say "N-7" meaning PRED.N-7; its `note_dispositions` "N-7" is R1R.N-7.)

## 1. Lineage and what changed

| commit | what | status |
|---|---|---|
| `ce5b8595` | C11RD-R1 scientific freeze | unchanged |
| `3c1eff11` | R1 pre-execution review, READY_TO_QUALIFY | unchanged |
| `3addf9d3` | qualification (qualification_r1/, evidence/qualification_r1/, docs/C11RD_R1_QUALIFICATION.md) | REJECTED, historical, unchanged |
| `89330534` | its review, QUALIFICATION_REJECTED (B-1) | unchanged |
| this round | qualification_r1q_r1/, evidence/qualification_r1q_r1/, this document | successor |

| new path | role |
|---|---|
| `qualification_r1q_r1/code/c11rd_launch.py` | the repaired launcher — the ONLY permitted entry of the one execution |
| `qualification_r1q_r1/code/c11rd_qualify.py` | checks Q01–Q14, the artifact writer, the post-write leak scan |
| `evidence/qualification_r1q_r1/C11RD_R1Q_R1_QUALIFICATION_CHECKS.json` | every check with its evidence |
| `evidence/qualification_r1q_r1/validation/` | the frozen validation suite, re-run (29/29) |
| `evidence/qualification_r1q_r1/C11RD_R1Q_R1_QUALIFICATION.json` | the qualification artifact (successor of 3addf9d3's) |
| `evidence/qualification_r1q_r1/POST_WRITE_LEAK_SCAN.json` | leak scan after every file was written |

The rejected launcher `qualification_r1/code/c11rd_launch.py` (sha256 `67714472…`) stays in the tree
as history and is NOT a permitted entry; its canonical qualification review is the REJECTED one, so
the frozen runner's own grant check refuses any grant built on it.

## 2. B-1 as found, and reproduced

The rejected launcher's preflight checked `git status` of the namespace only. Two ordinary states
passed it: a file staged elsewhere (reviewer T2) and a stale `.git/index.lock` (T11). In both the
launcher consumed the one execution, ran the runner and then failed to seal (T2: "SEAL REFUSED:
unexpected staged paths"; T11: "REFUSE: git add -f failed …" — under the preflight's own REFUSE
prefix). The result was left unsealed on disk. I reproduced both before preserving the review, and
Q11 now reproduces them mechanically against the rejected launcher (scratch repositories, stub
runner) in every qualification run.

## 3. The repair (launcher only)

Invariant: **complete preflight → sleep prevention → final gate → consume once → run once →
immediate seal**. Nothing checkable before consumption is deferred past it.

* **Seal preconditions refuse before consumption** (preflight AND a final gate immediately before
  the consumed ref is created): HEAD is exactly the authorization review commit, on the qualified
  launch branch; the index equals HEAD (`diff-index --cached`), no unmerged entry; the worktree and
  the namespace are clean; no `*.lock` in the worktree's git dir, the common dir or under `refs/`
  (index.lock of either worktree, HEAD.lock, packed-refs.lock, the branch-ref and consumed-ref
  locks); no merge, cherry-pick, revert, rebase, bisect or sequencer in progress; files ref backend;
  an explicit repo-local `user.name`/`user.email`; no sparse checkout; no git attribute on the seal
  paths; writable object store, refs and git dir.
* **A seal that cannot be broken by the shared index**: on a PRIVATE index file the launcher reads
  the start HEAD's tree, adds `evidence/runs/`, writes the tree, creates the commit with parent =
  start HEAD, and moves the branch by a compare-and-swap `update-ref <branch> <seal> <start HEAD>`.
  Hooks cannot run (`core.hooksPath=/dev/null`). Only then is the worktree index refreshed for
  `evidence/runs/`. A stale index.lock or a file staged elsewhere during the run no longer affects
  the seal (Q11 defense-in-depth, Q12 P4/P5).
* **Bounded retry of the seal only**: 7 attempts, delays 1, 2, 4, 8, 16, 32 s (63 s). Transient =
  lock contention or a failed git step while the branch still equals the start HEAD. Permanent (not
  retried) = the branch moved, HEAD left it, or unexpected staged paths. The runner is never started
  again.
* **A distinct terminal state**: `EXECUTION CONSUMED — RESULT UNSEALED`, exit code 4, never the
  REFUSE prefix; the report says the execution is consumed, lists the attempts and the last failure,
  leaves `evidence/runs/` exactly as found, writes `C11RD_UNSEALED_<head>.json` next to the journal
  and names the only continuation.
* **Seal-only recovery** (`--seal-only`): requires the consumed ref at the start commit, HEAD at it
  on the launch branch, `evidence/runs/` not yet in HEAD and no runner process alive; it runs the
  same seal and never starts the runner (Q12 AST check). A refused recovery prints `SEAL-ONLY
  REFUSED` (exit 5) and changes nothing.

## 4. What can and cannot be retried after consumption (QR1.N-13)

* Before consumption: any `REFUSE …` (exit 2) consumed nothing and ran nothing; fix the cause and
  launch again.
* After consumption, the science: NEVER under freeze `ce5b8595`. The consumed ref, the runner's
  permanent lock and its history guard R4, and `max_executions = 1` all refuse. A new execution
  needs a new freeze or namespace AND a new, independently reviewed qualification and authorization.
* After consumption, the seal: automatically within the same launcher process (the bounded policy
  above), and afterwards only by the seal-only recovery. A seal-only recovery never permits a new
  D1/D2 execution, never resets the consumed ref and never changes what the runner produced; the
  sealed result goes to the execution review.

## 5. Signals and launcher death (QR1.N-8)

From the final gate until the report is printed, SIGINT, SIGTERM, SIGHUP and SIGQUIT are recorded
and forwarded to the runner while it lives; SIGTSTP is recorded and ignored; nothing interrupts the
seal. A signal before consumption refuses (nothing consumed); a signal between consumption and the
runner start means the runner is not started (`CONSUMED_RUNNER_NOT_STARTED`, sealed). git children
and caffeinate run in their own sessions, so a terminal Ctrl-C (SIGINT to the process group) does
not reach them. SIGKILL or power loss of the launcher cannot be intercepted: the runner may finish
with no seal and sleep prevention ends with the launcher. Recovery: do nothing else, wait until no
`c11rd_runs.py` process remains, then `--seal-only` (tested in Q12 with a SIGKILLed launcher).

## 6. The interpreter actually used (QR1.N-11) — mechanically verified

`sys.executable` (`…/3.14/bin/python3.14`, about 136 KB) is a framework stub. dyld image 0 of every
`-I -S -B` process it starts — the launcher, a runner-like probe and its five spawn workers — is
`…/3.14/Resources/Python.app/Contents/MacOS/Python`, linked to libpython `…/3.14/Python` (about
14 MB). The artifact binds the stub, the running image and libpython in `interpreter`, and binds in
`runtime_files_sha256` every interpreter file those processes loaded: the Mach-O images, the
framework dylibs, every extension module, and every standard-library source AND cached bytecode
(`-B` stops writing `.pyc`, not reading them). The launcher re-hashes all of them at launch and
refuses any file it has loaded that is not bound (Q08).

## 7. Other notes folded in

* QR1.N-1 launcher self-hash against the artifact (and its blob at HEAD in `main()`); HEAD must be
  the authorization review commit.
* QR1.N-2 `main()` first evaluates a sanitized-state predicate (flags, no pycache prefix, exact
  environment); a preset marker without that state refuses before any frozen import.
* QR1.N-3 Q08 now covers no grant, symlinked grant, disk, memory, process table, AC power, lid,
  T1 (canonical paths), T4 (another freeze commit), T14 (decoy runner) and the runner guards; Q14
  drives `main()`.
* QR1.N-4 Q10 rebuilt value-free (section 8).
* QR1.N-5 Q09 instruments V07 too.
* QR1.N-6 a lying commit-graph makes the Q07 test discriminating.
* QR1.N-7 HOME=/var/empty, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, GIT_ATTR_NOSYSTEM=1 in
  the launcher, the runner and the seal; Q07 shows a hostile HOME configures plain git but not the
  launcher's.
* QR1.N-9 the preflight runs the frozen runner's R0, R1, R4, R5, R6/R7 in advance.
* QR1.N-10 AC power and an open lid are required at launch; caffeinate `-i -s`.
* QR1.N-14 every commit id is validated as 40 hex before it reaches git.

## 8. The leak scans (QR1.N-4)

The rejected Q10 compared tokens with the disclosed values (read from stdin) within 1e-4 and its
"control" was arithmetic. This round's Q10 needs no value at all. Every decimal, bare-point,
scientific (point or integer mantissa), JSON-float and rational token of every namespace file and of
the namespace's commit messages is shifted by 10^j (j = −3…3) and rendered with 4–10 significant
digits (truncated, rounded half up, and `%.{k}g`); each rendering's sha256 is compared with the
frozen set `c11rd_validate.ORIGINAL_PATTERN_SHA256` (17 renderings of the two disclosed values, built
by `c11rd_compare.value_patterns`). A hit is exactly a ≥ 4-significant-digit rendering at any of
seven scales. The same scanner, given the hash set of two DECOY constants (checked disjoint from the
frozen set), fires on 22 planted renderings (plain truncated/rounded, 9 digits, scientific, integer
mantissa, JSON, rational, percent, bare point, thousandfold, negative sign) and stays silent on 8
non-renderings (3 digits, 2e-3 off, digits inside a long integer or a hex digest); the plants live in
a temporary directory outside the repository. The post-write scan adds the frozen detectors (V18
and `_hashed_leak_scan`) over every file after all evidence was written, then again including
itself.

(While preparing this round I tried to recover the two values from the session transcript to pipe
them to the old stdin interface; the session's permission policy refused that. The value-free design
removes the need for them.)

## 9. Checks Q01–Q14 (all `python3 -I -S -B`)

The recorded evidence is ONE complete run from an empty evidence directory: **14/14 PASS** (397 s).

| check | result | what it covers |
|---|---|---|
| Q01 entry identity | PASS (14 items) | freeze commit and files; R1 review `dd4ccbda…` READY_TO_QUALIFY; `3addf9d3` and `89330534` ancestors; the rejection review byte-identical (`d95a2cb6…`) with exactly one verdict, QUALIFICATION_REJECTED; the historical r1 files unchanged (rejected launcher still `67714472…`); since `89330534` only this round's paths changed, nothing outside the namespace |
| Q02 history | PASS (15) | no run, lock, seal, comparison, grant or authorization path in any ref, reflog or full history (own reader and the frozen reader) or on disk; this round's review not yet written; no `refs/c11rd`, no launcher log dir; not shallow, no grafts, no replace refs; C11R byte-identical; r5 unchanged, no r6; LOCAL_MAIN_REF, cached REMOTE_MAIN_REF |
| Q03 scientific object | PASS (21) | cell 306 only on [680769/400000, 17885921/10000000]; 4-sub-block exact tiling; 168 boxes; tolerances 1/100000, 1/20000, 1/2000, depth 2; Taylor order 6; 34 moment terms; float proposal; recurrence and D1/D2 texts; `propagate`/`atom_values` exact on 50 random instances; max aggregation (AST); factor 2; one execution; caps 43,200 s / 2 GiB / 5 workers; upper-closed convention; cover; quarantine blob and read order; V29 |
| Q04 hashes | PASS (5) | 8 frozen code files (and only those), C7, 8 input blobs, 8 document hashes |
| Q05 validation | PASS | frozen suite **29/29** (output sha256 `db53abe5ebe7…`) |
| Q06 host / runtime | PASS (17) | section 10; interpreter binding of 227 files (QR1.N-11) |
| Q07 git hardening | PASS (17) | artifact committed then deleted is found; a LYING commit-graph fools plain git but not the frozen reader or the launcher (QR1.N-6); replace ref; 15 hostile variables; failing repository hooks run for plain git, not for the launcher's; a hostile HOME configures plain git, not the launcher's (QR1.N-7); grafts/shallow fail closed; detached linked worktree; path alias; real repository clean |
| Q08 lifecycle | PASS (9) | runner real-mode order; predecessor matrix 15/15 through the frozen grant check; production runner on the NT block: accounting failure, memory cap, wall cap → NOT_CERTIFIED; launcher outcomes 8/8 (certified, second launch refused, NOT_CERTIFIED, crash, SIGTERM, runner refusal, hostile environment, preflight refusals); **23/23 preflight refusal cases** (host, interpreter, runtime file, worktree, freeze, launcher hash, idle, disk, memory, process table, AC power, lid, runner hash, runner R0/R1/R4, consumed, dirty namespace, no grant, symlinked grant, T1, T4, T14) each with its expected reason, no ref, no runner, index as found |
| Q09 R1R notes | PASS (4) | 8 validation tests instrumented incl. V07 (154 point_box, 153 kernel_at calls); 36 kernel-level rows; worst width/residual 7.2e-04; per-sub-block covers |
| Q10 leak scan | PASS | 56 files + the namespace's commit messages, 10,338 tokens (3,663 distinct values), 0 hits; decoy controls 22/22 fired, 8/8 silent; decoy set disjoint from the frozen set |
| Q11 B-1 | PASS (4) | the REJECTED launcher reproduces T2 and T11 (consumed, ran, not sealed; T11 under REFUSE); the repaired one refuses **18/18** states before consumption (T2, T11, common-dir index.lock, branch-ref lock, packed-refs.lock, HEAD.lock, consumed-ref lock, merge, cherry-pick, rebase, detached HEAD, HEAD after the authorization commit, unmerged entry, no user.email, sparse checkout, attribute on the seal paths, unstaged and untracked files elsewhere); defense in depth 2/2 (with the preconditions monkeypatched off, T2 and T11 still seal correctly); ordering invariant (AST) |
| Q12 post-consumption | PASS (3) | 12/12 cases: transient lock → retried, sealed, runner once; persistent lock → 7 attempts → UNSEALED (exit 4, not REFUSE), runs left as found, index untouched; seal-only while blocked → still UNSEALED; seal-only after clearing → sealed on the start HEAD, runner not started again; second seal-only → SEAL-ONLY REFUSED; relaunch refused; seal-only on an unconsumed lineage refused; branch moved → UNSEALED after ONE attempt; index.lock during the run → sealed, refresh reported pending; file staged elsewhere during the run → seal holds only evidence/runs/; **production policy: 7 attempts, UNSEALED 65 s after the runner exited**; launcher SIGKILL mid-run → seal-only refused while the runner lives, then sealed (RECOVERED_ARTIFACT_AND_LOCK); AST: `seal_only` and `seal` cannot start the runner or read the artifact |
| Q13 signals | PASS (6) | INT/TERM/HUP/QUIT/TSTP at the seal's ref update deferred; process-group SIGINT during the seal (git children in their own group); SIGINT after consumption → runner not started; SIGTERM in the gate → REFUSE; terminal Ctrl-C during the run; forwarded-then-deferred |
| Q14 entry point | PASS (12) | on the REAL repository, refusal paths only: hostile environment → one re-exec → REFUSE no grant; preset marker + extra variable → REFUSE L1; preset marker without `-I -S -B` → REFUSE L1 (QR1.N-2); exact sanitized state → proceeds; option-shaped CLI id refused (QR1.N-14); `--seal-only` without grant refused; option-shaped grant ids and a symbolic authorization id refused in sandboxes; the real repository unchanged; `main()` builds exactly the runner command |

## 10. Host and runtime (bound in the artifact)

Hostname `suzhedeMacBook.local`, IOPlatformUUID `57559A2E-B526-5AE7-9701-A8BEB8908AF0`, platform
`darwin`, Python 3.14.5; macOS 26.5.2 (25F84), arm64, 6 cores (Apple A18 Pro), 8 GiB;
canonical worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, git common dir `/Users/suzhe/ReBaseGuard/.git`, launch
branch `refs/heads/p5y-k5-tail-c11rd-d1d2-extension`; git version 2.50.1 (Apple Git-155).

Interpreter: stub `…/3.14/bin/python3.14` (sha256 `bd349815…`), running image
`…/3.14/Resources/Python.app/Contents/MacOS/Python` (`2c8c1048…`), libpython `…/3.14/Python` (`34463f1b…`);
227 runtime files bound (binding sha256 `9b2a50359ac5…`).

Under the launcher's exact environment (HOME=/var/empty, global and system git config off): 5 isolated spawn
workers, memory accounting OK, the frozen history reader and cover work, the seal identity is repo-local.
`/bin/ps` read 500 times, 0 failures; wall/monotonic drift
over 2 s 3e-06 s; caffeinate `-i -s` assertions verified; power now
AC, lid open; pmset sleep 1 min.

Launch limits (governance, not science): 1-min load ≤ 2.0, free disk ≥ 2 GiB, available memory ≥ 1 GiB, AC
power, lid open. At qualification the 1-min load was 1.84; the launcher enforces the
limits at launch.

## 11. Note dispositions (unique identifiers)

| note | class | disposition |
|---|---|---|
| R1R.N-1 | QUALIFIED | validation helper point_box reads bands lower-closed; Q09 instruments point_box and kernel_at over 8 validation tests INCLUDING V07 (QR1.N-5): every call uses a globally continuous candidate or none and no interior point with s >= 4; c11rd_validate.py is frozen and not edited (erratum recorded) |
| R1R.N-2 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q09: kernel-level exclusion of the reversed convention, Khat orders 0-2, s = 2, 3, 4 |
| R1R.N-3 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q09: sharp endpoint containment, width < 1e-3 of the residual at u_e = -1, +1 |
| R1R.N-4 | ACCEPTED_LIMITATION | nontarget mode trusts the on-disk freeze (changing it needs a new freeze); rule: no rehearsal after this qualification except on explicit instruction, from a clean tree with the committed freeze; the governed target path binds the freeze at the freeze commit (R2) |
| R1R.N-5 | HARDENED_OUTSIDE_FROZEN_SCIENCE | the qualified launcher is the only permitted entry; the sanitized state now also fixes HOME=/var/empty, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM, GIT_ATTR_NOSYSTEM, core.hooksPath=/dev/null (Q06-Q08, Q14); residual ACCEPTED_LIMITATION: deliberate forgery by a trusted operator, and interpreter start-up before any program check when the launcher is started without -I -S -B |
| R1R.N-6 | HARDENED_OUTSIDE_FROZEN_SCIENCE | consumed ref in the COMMON git dir before the run, and an immediate seal that no longer depends on the shared index (private index + compare-and-swap ref update, bounded retry, distinct UNSEALED state, seal-only recovery): QR1.B-1 repaired (Q11-Q13) |
| R1R.N-7 | ACCEPTED_LIMITATION | reachable history only (inherent; the freeze says 'reachable history') |
| R1R.N-8 | HARDENED_OUTSIDE_FROZEN_SCIENCE | canonical qualification paths and the exact freeze commit enforced by the launcher; Q08 now tests it (reviewer T1 and T4: the frozen check alone accepts, the launcher refuses) |
| R1R.N-9 | ACCEPTED_LIMITATION | stale 'R0-R6' wording and the JSON FORBIDDEN list without the band clause cannot be edited without a new freeze; errata carried; the convention is immutable through the frozen hashes and guard R6 |
| R1R.N-10 | QUALIFIED | Q10 repaired (QR1.N-4): value-free hashed rendering scan at seven scales, 4-10 digits, with decoy positive/negative controls through the same code path: clean |
| R1R.N-11 | QUALIFIED | fail-closed kept: a failed process-table read ends the run NOT_CERTIFIED and consumes it; Q06 500/500 reads; the launcher pre-checks the table and requires an idle host, AC power, open lid and verified sleep prevention (= PRED.N-7) |
| R1R.N-12 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q08 single-field deviation matrix (platform, input_bindings, git_common_dir, QUALIFICATION_REJECTED, ancestor freeze commit with a different freeze file): all refused |
| R1R.N-13 | QUALIFIED | Q09: each per-sub-block box list is complete (verify_cover) and identical in geometry to the NT list |
| QR1.B-1 | HARDENED_OUTSIDE_FROZEN_SCIENCE | REPAIRED in the launcher only. Before consumption the preflight AND a final gate refuse unless HEAD is the authorization commit on the qualified branch, the index equals HEAD with no unmerged entry, the worktree and namespace are clean, no *.lock exists in the worktree git dir, the common dir or refs/, no merge/rebase/cherry-pick/revert/bisect is in progress, the ref backend is files, an explicit repo-local identity exists, sparse checkout is off, no attribute applies to the seal paths and the object store is writable. The seal itself uses a private index and a compare-and-swap ref update, retries transient failures under a bounded policy (1+6 attempts in 63 s, seal steps only), and otherwise ends in 'EXECUTION CONSUMED — RESULT UNSEALED' (exit 4, never REFUSE) whose only continuation is --seal-only. Q11: the rejected launcher reproduces T2/T11, the repaired one refuses both and 16 more states before consumption; Q12/Q13: post-consumption failure, retry, UNSEALED, recovery, signals, launcher death |
| QR1.N-1 | HARDENED_OUTSIDE_FROZEN_SCIENCE | the launcher checks its own sha256 against this artifact and, in main(), its blob at HEAD; HEAD must equal the authorization review commit (Q08, Q11) |
| QR1.N-2 | HARDENED_OUTSIDE_FROZEN_SCIENCE | main() first evaluates the sanitized-state predicate (flags, pycache prefix, exact environment); a preset marker without that state refuses (Q14 E2, E3; no __pycache__ written) |
| QR1.N-3 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q08 now tests no grant, symlinked grant, disk, memory, process table, AC power, lid, canonical paths (T1), another freeze commit (T4), a decoy runner (T14), runner guards; every sandbox launch loads the qualification through load_qualified; Q14 drives main() (L1 re-exec, refusals) |
| QR1.N-4 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q10 rebuilt: value-free, >= 4-digit renderings at seven scales against the frozen hash set; 22 planted decoy renderings fire and 8 decoy non-renderings stay silent through the same scanner |
| QR1.N-5 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q09 instruments V07 as well and reports the instrumented tests and call counts |
| QR1.N-6 | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q07: a LYING commit-graph (c3's parent recorded as c1): plain git follows the lie, the frozen reader and the launcher's git return the truth -- the test can fail |
| QR1.N-7 | HARDENED_OUTSIDE_FROZEN_SCIENCE | HOME=/var/empty, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, GIT_ATTR_NOSYSTEM=1 in the launcher, the runner and the seal; Q07 control shows a hostile HOME configures plain git and not the launcher's; Q08 hostile environment reaches neither |
| QR1.N-8 | HARDENED_OUTSIDE_FROZEN_SCIENCE | signals are recorded (and forwarded only while the runner lives) from the final gate to the printed report; git children and caffeinate run in their own sessions; Q13 S1-S6. Residual ACCEPTED_LIMITATION: SIGKILL/power loss of the launcher cannot be intercepted -> the runner may finish unsealed, sleep prevention ends; recovery = --seal-only after no runner process remains (Q12 launcher-death test) |
| QR1.N-9 | HARDENED_OUTSIDE_FROZEN_SCIENCE | the preflight runs the frozen runner's R0 (loaded modules), R1 (code, C7), R4 (disk and history), R5 (premise), R6/R7 (target, cover, accounting) in advance; the runner re-runs all of them |
| QR1.N-10 | HARDENED_OUTSIDE_FROZEN_SCIENCE | the preflight requires AC power and an open lid; caffeinate -i -s. Residual ACCEPTED_LIMITATION: a lid closed DURING the run cannot be prevented; the wall-clock cap then ends the run NOT_CERTIFIED (fail-closed) |
| QR1.N-11 | HARDENED_OUTSIDE_FROZEN_SCIENCE | MECHANICALLY VERIFIED (Q06): sys.executable bin/python3.14 is a stub; the running image (dyld image 0) is Resources/Python.app/Contents/MacOS/Python, linked to Versions/3.14/Python; both, every extension module and dylib, and every stdlib source and cached bytecode loaded by the launcher, a runner-like probe and its 5 spawn workers are bound (runtime_files_sha256) and re-hashed at launch; a mismatch refuses (Q08) |
| QR1.N-12 | HARDENED_OUTSIDE_FROZEN_SCIENCE | every note here carries its source prefix (R1R, QR1, PRED); PRED.N-7 = R1R.N-11 recorded; the historical artifact and review are not edited |
| QR1.N-13 | ACCEPTED_LIMITATION | fail-closed direction kept: after consumption the science can never be rerun under freeze ce5b8595 (consumed ref, runner lock and history R4, max_executions 1); a new execution needs a new freeze or namespace AND a new independently reviewed qualification and authorization. Only the SEAL may be retried (see retry_semantics) |
| QR1.N-14 | HARDENED_OUTSIDE_FROZEN_SCIENCE | every commit id reaching git is validated as 40 hex first: the CLI argument, the grant's freeze, qualification and qualification-review commits (Q14 E5, E7-E9) |
| QR1.N-15 | QUALIFIED | carried into authorization_requirements, several now enforced mechanically by the launcher |

No note requires a new freeze.

## 12. Authorization requirements (QR1.N-15, for a future, separately instructed round)

1. the grant equals the qualified values: host (grant_host), worktree, freeze_commit = ce5b8595 exactly, qualification commit = the commit of this artifact, qualification review = the R1Q-R1 review commit (QUALIFICATION_ACCEPTED), the canonical r1q_r1 paths, the frozen code and input hashes, target 306 [D1, D2], max_executions 1
2. the launcher's sha256 at the authorization commit equals this artifact's; the rejected r1 launcher is not permitted; direct runner invocation is not permitted
3. the launch is the exact launch_command at HEAD = the authorization review commit, clean index, no lock file (the launcher enforces these)
4. no IDE or git client attached to the repository during the run (not mechanically enforceable; the seal survives index contention and retries ref-lock contention)
5. an otherwise idle host, AC power, lid open, sleep prevention verified (the launcher enforces all four at launch; PRED.N-7 = R1R.N-11)
6. after exit 4 or a launcher death: nothing but the seal-only recovery

Exact launch command: `python3 -I -S -B level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_launch.py --authorization-review-commit <authorization review commit>`.

## 13. Run history of this round

* The rejected qualification's own history (three full runs, two tool defects) is in
  `docs/C11RD_R1_QUALIFICATION.md` §6; its review (`89330534`) is the reason for this round.
* Before preserving that review I reproduced B-1 (T2, T11) in scratch sandboxes with the rejected
  launcher; this round's Q11 repeats that reproduction mechanically in every run.
* During development the checks were exercised one at a time from a scratch harness (outside the
  repository; not evidence). Defects found and fixed before the recorded run:
  1. Q07's QR1.N-7 control read `user.name`, which the repository's own config overrides, so it
     could not show HOME's effect; it now uses keys only a global config sets (`gpg.program`,
     global attributes).
  2. Q11's attribute case planted a root-relative pattern that matched no seal path, so the
     launcher (correctly) sealed instead of refusing; the plant now matches the seal paths.
  3. Q10 was redesigned value-free (section 8) after the attempt to recover the disclosed values for
     the old stdin interface was refused by the session's permission policy.
  4. Hard-coded claims replaced by measurements: decoy/frozen-set disjointness (Q10) and "historical
     files unchanged" (from Q01).
  5. Launcher hardening from self-review before the recorded run: journal writes can no longer
     raise; `run_once` never returns while the runner lives; a refused recovery is `SEAL-ONLY
     REFUSED` (exit 5), never REFUSE; every unexpected post-consumption error ends UNSEALED with a
     report.
  6. The scratch harness itself lacked a `__main__` guard, so the NT attempt-semantics workers
     re-imported it (harness only; the tool is guarded).
* Recorded evidence: ONE complete run from an empty `evidence/qualification_r1q_r1/`, 14/14 PASS,
  validation 29/29, launcher sha256 `81ccc0482994ba0a4febb8aa5d6ee551f84bb3e66957e06e821250180e11fb48`,
  tool sha256 `886679d16d22f6734bf7748dbeaa08452250ecb7685f5ef9d0869f0c99ea0a0d` (both
  unchanged between the start and the end of the run). No `__pycache__` anywhere; no `refs/c11rd`, no
  launcher log dir and no grant in the real repository afterwards.

## 14. Errata (hash-bound documents and historical artifacts are not edited)

Carried from the rejected qualification's doc §7 (still valid): "R0–R6" in
`docs/C11RD_ARCHITECTURE.md` and the freeze JSON's `K_success_failure` omit R7; the freeze JSON's
`FORBIDDEN` list lacks the band-convention clause stated in `protocol/C11RD_FREEZE_R1.md`;
`c11rd_validate.point_box`'s docstring says "the band that owns (p, m)" but selects bands
lower-closed (validation helper only); the freeze JSON's `entry_head` is the campaign entry
`7375b9cd`, the R1 round's entry was `663f8fe7`.

New, about the rejected qualification's files: its artifact's `attempt_semantics` and
`immediate_seal_rule` describe every outcome as sealed, which B-1 showed false; its "N-7" names two
different notes (see the identifier map above); its Q10 "positive control" was arithmetic only and
its Q07 commit-graph case could not fail. These statements are superseded by this document and the
successor artifact.
