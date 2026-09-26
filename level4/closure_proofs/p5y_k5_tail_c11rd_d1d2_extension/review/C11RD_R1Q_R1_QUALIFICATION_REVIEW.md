# C11RD-R1Q-R1 qualification review
QUALIFICATION_ACCEPTED

Reviewer: fresh, independent, read-only. Date 2026-09-26. Worktree `/Users/suzhe/ReBaseGuard-k5c11rd`,
branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD = repair commit `e627d4ecf402f6d7b827d8ab734b55f4ae41e0e6`
(parent `89330534`). `git status --porcelain --ignored --untracked-files=all` printed 0 lines before and
after every step. `refs/c11rd/*` stayed empty, `.git/c11rd_r1/` was never created, and no `__pycache__`
appeared in the namespace. Every launcher experiment ran in scratch repositories with a STUB runner.

## Summary

The repaired qualification is acceptable as the qualification of freeze `ce5b8595`. A future,
separately reviewed authorization can use THIS launcher
(`qualification_r1q_r1/code/c11rd_launch.py`, sha256 `81ccc048…`) for the one cell-306 D1/D2 execution,
subject to the authorization conditions listed under the non-blocking notes.

* **The freeze is untouched.** The freeze, the scientific object, the frozen hashes, the historical r1
  files and the rejection review are all byte-identical to their commits. `e627d4ec` adds exactly 8 new
  files, all under this round's paths.
* **B-1 is repaired.**
  * T2 and T11 now refuse before consumption: no consumed ref, no runner start, HEAD and index as found.
    The tool shows this and so do my own probes.
  * The rejected launcher still exhibits B-1 in the same states.
  * The new seal no longer depends on the shared index. It uses a private index and a compare-and-swap
    ref update.
  * Every post-consumption seal failure I could provoke ends in the distinct, correctly reported state
    `EXECUTION CONSUMED — RESULT UNSEALED` (exit 4), never under `REFUSE`. Where a result existed, the
    seal-only recovery sealed it on the start commit without starting the runner.
* **Reproductions.** I reproduced the qualification tool (14/14 PASS) and the frozen validation (29/29,
  run twice). Both match the committed evidence apart from host-volatile fields.
* **The interpreter binding (QR1.N-11) is correct.** I checked it with dyld, `lsof` and `ps`.
* **The namespace is leak-free.** My own value-free scan found 0 hits, with working decoy controls.

I found no blocker. I did find two post-consumption seal-failure states that the preflight does not
check (N-1, N-2 below). Both need a deliberate, non-ordinary change to the repository or to file
permissions. Neither exists now. Both end in the correct UNSEALED state. They show that the document's
sentence "Nothing checkable before consumption is deferred past it" is slightly overstated. They do not
make an authorized execution unsafe, and the authorization review can close both with a check.

## Scope and what I ran

Read in full:
* the rejection review at `89330534`;
* the new document `docs/C11RD_R1Q_R1_QUALIFICATION.md`;
* the repaired launcher, all 940 lines;
* the qualification tool: every check, the sandbox, the stub, the driver and the leak scanner;
* the committed artifact, the checks JSON and `POST_WRITE_LEAK_SCAN.json`;
* in the frozen runner, the pre-import barrier, R0-R7, `grant_problems`, `take_lock` and `main`;
* in the frozen comparator, `value_patterns`, `leak_hits`, `verify_seal` and the start of `main`;
* in the frozen validation, `_hashed_leak_scan` and V18.

Executed:
* **Qualification tool:** a full run into my scratch directory.
* **Frozen validation:** a standalone run.
* **Hash and lineage verification script.**
* **Independent value-free leak scanner.**
* **Three probe programs.** They cover 27 launcher scenarios in scratch repositories with a STUB runner.
* **Interpreter checks:** dyld, `lsof` and `ps`.
* **The launcher on the real repository:** refusal paths only.
* **Read-only git queries.**

## Findings per item

### 1. Freeze identity and immutability — PASS
* **Code.** All 8 `code/` files equal the freeze's `code_sha256`, on disk and at `ce5b8595`. `code/`
  holds exactly those 8 files.
* **Documents and inputs.**
  * All 8 `document_sha256` entries are equal.
  * All 8 input blobs are equal at HEAD and at `ce5b8595`.
  * I looked up the two comparison-only inputs by blob id only and never opened them.
  * C7's `c7_gaussian.py` sha256 equals the freeze.
* **Freeze files.** `protocol/C11RD_FREEZE_R1.json` (blob `770b378d`, sha256 `07118d30…`) and `.md`
  (`63f4d71b`, `d2875e83…`) are identical at `ce5b8595` and HEAD. So are the predecessor freeze files.
* **Diffs since the freeze and since the rejection.**
  * `git diff ce5b8595 HEAD -- code protocol theory` is empty.
  * The only additions since the freeze are the R1 review, the r1 qualification, its review and this
    round's files.
  * Since `89330534`, nothing outside the namespace changed.
* **Historical files.**
  * All 8 historical r1 files have the same blobs at `3addf9d3` and HEAD. The rejected launcher is
    still `67714472…`.
  * The rejection review is blob `92984aba`, sha256 `d95a2cb6…`, identical at `89330534` and HEAD, with
    exactly one verdict line (line 2, rejected).
  * The R1 review is blob `f568f9af`, `dd4ccbda…`, READY_TO_QUALIFY.
* **The new artifact** has `schema` `c11rd.qualification.r1q_r1` and `freeze_commit` `ce5b8595…`.
  * `successor_of` names `3addf9d3`, its artifact blob `a4544187`, the review `89330534` (`d95a2cb6…`),
    blocker QR1.B-1, and the superseded launcher as "HISTORICAL -- NOT a permitted entry".
  * `requires_new_freeze` is `[]`.
  * `qualification_code_sha256` equals the files on disk: launcher `81ccc048…`, tool `886679d1…`.

### 2. B-1: reproduction, repair and other states — PASS (see N-1, N-2)
**The repaired launcher, my own probes.**
* **T2** (file staged outside the namespace): `REFUSE L2: the index differs from HEAD …`. No consumed
  ref, stub not started, HEAD and index unchanged, no runs files.
* **T11** (stale `worktrees/wt/index.lock`): `REFUSE L2: git lock files present …`, with the same
  observations.

**The rejected launcher, same states.**
* **T2:** consumed, the stub ran, `SEAL REFUSED: unexpected staged paths`, runs files left on disk.
* **T11:** consumed, the stub ran, `REFUSE: git add -f failed: … index.lock …`, which is the misleading
  prefix.
* So B-1 is still reproducible on the historical launcher.

**The tool's Q11 rerun** agrees on all points:
* the 2 historical reproductions;
* 18 of 18 states refuse before consumption;
* defense in depth 2 of 2: with the preconditions monkeypatched off, T2 and T11 still seal correctly;
* the AST ordering check.

**Ordering.** I read `launch()`. The order is preflight (L1 environment, commit ids, host, interpreter,
runtime files, worktree, own hash, freeze, canonical paths, runner hash, frozen grant check, runner guards
R0/R1/R4/R5/R6-R7, seal preconditions, power, lid, load, disk, memory, process table, no other runner, no
consumed ref) → `caffeinate` → signal guard → final gate → create-only consumed ref → one run → seal. The
final gate re-checks the seal preconditions, the consumed ref, the runs paths, the log path and the
signals received. Every runner refusal that can be decided in advance is decided in advance. The one
exception is the writability of the launcher log directory (N-2).

**Other states I probed.**

| state | expected | observed |
|---|---|---|
| repo-local `commit.gpgSign=true`, missing `gpg.program` | seal | sealed (`commit-tree --no-gpg-sign`) |
| failing `reference-transaction` hook via repo-local `core.hooksPath` | seal | sealed (`-c core.hooksPath=/dev/null` wins for both consume and seal) |
| `info/attributes` `* text=auto eol=crlf`; repo-local `core.attributesFile` | refuse | refused before consumption |
| `sparseCheckout` in `config.worktree` | refuse | refused before consumption |
| stale `index.lock` of another linked worktree | seal | sealed (irrelevant to the private-index seal) |
| branch only in `packed-refs`; empty `evidence/runs/` pre-existing | seal | sealed |
| `packed-refs.lock` or the main worktree's `index.lock` appearing during the run | seal | sealed |
| `HEAD.lock` appearing during the run and persisting | UNSEALED, then recovery | 7 attempts, UNSEALED (exit 4); after removal, `--seal-only` sealed on the start HEAD, stub not rerun |
| `feature.manyFiles`, `core.splitIndex`, `untrackedCache`+`fsmonitor`, `user.useConfigOnly`, `logAllRefUpdates=always` | seal | all sealed |
| **repo-local `core.autocrlf=true` + `core.safecrlf=true`** | — | **passes preflight and gate; after consumption `git add` fails ("LF would be replaced by CRLF"); 7 attempts; UNSEALED; recoverable** (N-1) |
| **launcher log directory present but not writable** | — | **passes preflight and gate; consumed; runner NOT started; UNSEALED (UNKNOWN); `--seal-only` refuses "nothing to seal"** (N-2) |
| `autocrlf=true` alone; `autocrlf=input`+`safecrlf=true`; `eol=crlf`+`safecrlf=true` | seal | all sealed |

The real repository has none of the N-1 or N-2 conditions:
* its repo-local configuration has no `autocrlf`, `safecrlf`, `eol`, `attributesFile`, `hooksPath`,
  `fsmonitor` or `sparseCheckout`, and there is no `config.worktree`;
* `check-attr -a` on the seal paths is empty;
* the ref format is `files`;
* HEAD is the launch branch;
* the identity resolves under the launcher's environment;
* `.git/c11rd_r1` does not exist.

### 3. Post-consumption behaviour and the private-index seal — PASS
* **Retry policy.** The seal is retried only inside `seal()`: 1 + 6 attempts with delays of 1, 2, 4, 8,
  16 and 32 s. Nothing re-enters `run_once`.
  * The tool's P6 rerun measured UNSEALED 65.0 s after the runner exited.
  * A moved branch, or HEAD leaving the branch, is permanent. It gives UNSEALED after one attempt (P3).
  * Every other failed git step is treated as transient. A permanent configuration error such as N-1 is
    therefore retried 7 times. That is harmless.
* **Terminal states.**
  * Every failure after consumption becomes `ConsumedUnsealed`: exit 4, banner, `UNSEALED_REPORT`
    printed on both stdout and stderr, and `C11RD_UNSEALED_<head>.json` written.
  * The `except BaseException` in `launch()` and `execute()` guarantees that no `REFUSE` text is printed
    once `STATE["consumed"]` is set.
  * `LaunchRefusal` is raised only before `consume` succeeds.
* **Seal-only recovery.**
  * It requires the consumed ref at the start commit, HEAD equal to that commit on the launch branch,
    `evidence/runs/` not yet in HEAD, and no `c11rd_runs.py` process alive.
  * It has no `run_once`, no `Popen` and no runner command (the AST check, and my reading).
  * A refused recovery prints `SEAL-ONLY REFUSED` (exit 5) and changes nothing. A relaunch after
    recovery is refused.
  * The message says in plain words that a seal-only recovery never permits a new D1/D2 execution.
* **The private-index seal** runs `read-tree <start>` → `add -f -- evidence/runs` → `diff-index --cached
  --name-only <start>` (every path must be under `evidence/runs/`) → `write-tree` → `commit-tree
  --no-gpg-sign -p <start>` → `update-ref <branch> <seal> <start>` (compare-and-swap).
  * Then `_verify_landed` checks that HEAD is the seal and that the seal's only parent is the start
    commit.
  * The shared index is touched only afterwards, by `reset -q -- evidence/runs`.
  * The outcome class comes from file presence only. The launcher never reads the runs artifact or the
    runner log. The runner's own log lines carry progress and status, not values.
  * The frozen comparator's `verify_seal` compares only the runs artifact's bytes, so the extra journal
    and log files are compatible with U1.
  * I judge the seal correct: exactly `evidence/runs/`, parent = start HEAD, no other ref or index
    touched, no value read.

### 4. Signals, sanitized state, HOME, commit ids, runner guards, power, self-hash — PASS (see N-4)
* **Signals (QR1.N-8).**
  * From the gate to the end of `launch()`, INT, TERM, HUP and QUIT are recorded and forwarded only to a
    live runner. TSTP is recorded and ignored.
  * git and `caffeinate` children run in their own sessions (Q13 S2 shows a different process group).
  * S1-S6 pass in my rerun.
  * SIGKILL of the launcher leads to the seal-only recovery, and Q12 tests that.
* **Sanitized state and marker (QR1.N-2).** `main()` evaluates `sanitized_state_problems()` before any
  argument parsing, git call or frozen import. A preset marker without the exact state refuses (Q14 E2,
  E3).
* **HOME and global configuration (QR1.N-7).**
  * `SAFE_ENV` sets `HOME=/var/empty`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`,
    `GIT_ATTR_NOSYSTEM=1` and `GIT_OPTIONAL_LOCKS=0`. It applies to the launcher's git, to the runner
    (Q08 env stub) and to the seal.
  * Q07's control shows that a hostile HOME configures plain git but not the launcher's.
* **Commit ids (QR1.N-14).** Commit ids are validated as 40 hex characters:
  * the CLI argument;
  * the grant's `freeze_commit`, `qualification.commit` and `review_commit`;
  * `qc` in `load_qualified`.

  I confirmed that `--authorization-review-commit=--help` is refused on the real repository.
* **Runner guards in advance (QR1.N-9).** R0, R1, R4 (disk and history), R5 and R6/R7 are called through
  the frozen functions. R2 is covered by `grant_problems` and R3 by the namespace check.
* **Power and lid (QR1.N-10).** AC power comes from `pmset -g batt` and the lid state from
  `AppleClamshellState`. Both are required. `caffeinate -i -s` asserts both PreventUserIdleSystemSleep
  and PreventSystemSleep.
* **Self-hash and HEAD (QR1.N-1).**
  * The preflight compares the launcher's sha256 with the artifact.
  * `main()` compares the launcher's blob at HEAD, its canonical path and `FREEZE_COMMIT`.
  * HEAD must equal the authorization commit.

### 5. The interpreter actually running (QR1.N-11) — PASS, checked mechanically
I started a `-I -S -B` process through `…/3.14/bin/python3.14` under the launcher's exact environment,
and another through the `python3` symlink.
* In both, dyld image 0 is `…/3.14/Resources/Python.app/Contents/MacOS/Python`, and libpython
  `…/3.14/Python` is loaded.
* A sleeping probe confirmed this independently:
  * `ps -o comm=` shows the Python.app path;
  * `lsof` txt mappings list `Python.app/…/Python`, `Versions/3.14/Python`, `libcrypto.3.dylib` and the
    `lib-dynload` extensions.
* My shasum of the stub (`bd349815…`), the running image (`2c8c1048…`) and libpython (`34463f1b…`)
  equals the artifact's `interpreter` block.
* **The binding.**
  * My tool rerun reproduced an identical 227-file `runtime_files_sha256` (binding sha256
    `9b2a5035…`): 92 `.pyc`, 107 `.py`, 24 `.so`, the two Mach-O images and two dylibs.
  * At launch, `runtime_problems` re-hashes every bound file and refuses any file loaded but not
    bound.
  * In-process: under the plain flags, `runtime_problems` of the committed artifact is empty. Under
    `-O` it refuses, because unbound `.opt-1.pyc` files are loaded.
  * Q08 shows that a changed hash refuses.

### 6. Leak scans (QR1.N-4) — PASS
* **Design.** The value-free design is sound. It hashes renderings of every numeric token at 7 decimal
  scales and 4-10 significant digits, and compares them with the frozen 17-element
  `ORIGINAL_PATTERN_SHA256`. The decoy positives and negatives go through the same code path, and the
  decoy set is checked to be disjoint from the frozen set.
* **My rerun of Q10.** 60 files and the commit messages, 0 hits; decoys 22 of 22 fired and 8 of 8
  stayed silent.
* **The committed post-write scan** covers all 60 current files, the second pass including itself.
* **My own scanner**, written separately. The only frozen parts it uses are
  `ORIGINAL_PATTERN_SHA256` and `value_patterns`.
  * It covered:
    * all 60 namespace files;
    * the messages of all 7 namespace commits;
    * all commit messages in `7375b9cd..HEAD`.
  * It used the tool's token forms plus plain integers of 4 or more digits: 24,535 tokens, 7,050
    distinct values.
  * Each value was scaled by 10^-3 to 10^3. At each scale I took every leading-digit prefix with 4 or
    more significant digits, the roundings to 4-12 digits (half-up, half-even, down; plain and with
    trailing zeros stripped), `%.{4..17}g` and `repr`.
  * A broad tier took every maximal digit run anywhere, identifiers and hex included: 60,480 runs.
  * Result: 0 hits in both tiers. 12 of 12 decoy positive plants fired and 4 of 4 negatives stayed
    silent. No ≥ 4-significant-digit rendering of either original value is in any namespace file or
    commit message.
* **Q10's remaining gap:** it does not scan plain integers (N-7). My scan did.

### 7. Reproduction of the evidence — PASS
* **Frozen validation.** I ran it standalone: 29/29 PASS, `drifts_used` [0, 1, 5/2, NT block],
  `target_values_used` false.
* **Qualification tool.** It ran in 413 s with 14/14 PASS, and it reran the validation as Q05: 29/29.
* **Key-by-key comparison with the committed artifact and checks JSON.** They differ only in:
  * host-volatile fields: disk, load, memory, drift and `ps` seconds;
  * per-check seconds;
  * the checks-file and validation-output hashes, which change with timings;
  * Q01's recorded HEAD (`89330534`: the recorded run preceded the commit, as expected);
  * leak-scan file and token counts (60 against 56 files, because the four evidence and document files
    were written after that run);
  * one temporary-directory path in the T11 message.
* **Identical** are the interpreter block, the 227-file binding and every check verdict.

### 8. Absence of target computation, grant, authorization, run, seal, comparison and r6; governance — PASS
* `git log --all --reflog --full-history` finds no commit touching `evidence/runs`,
  `evidence/comparison`, `config`, the execution, authorization or R1Q-R1 qualification review. None of
  them is on disk.
* There are no `refs/c11rd/*` and no `refs/replace`, the repository is not shallow, and there are no
  grafts, no stash and no `.git/c11rd_r1`.
* Local main is `c123b9bb8f15d17650545b3fce4aca8a6b61093b` and origin/main is
  `1cb453826313c189f0bdafd5b84120c1edb74da9`, both unchanged.
* The artifact says `target_D1_computed`/`target_D2_computed` false. The tool's science runs only at
  drift 0, 1 or 5/2, on the NT block, or with a stub. Everything I ran did the same.

### 9. Note dispositions — honest; nothing requires a new freeze
* **QR1.B-1** is repaired in the launcher only.
* **Hardened, and I checked the code and tests:** QR1.N-1, N-2, N-3, N-5, N-6, N-7, N-9, N-10, N-11,
  N-12 and N-14.
* **QR1.N-4** is hardened. The plain-integer gap is covered by my scan.
* **QR1.N-8** is hardened, with an honest residual for SIGKILL and power loss. N-4 below adds the
  terminal-stop case.
* **QR1.N-13 is correctly an ACCEPTED_LIMITATION.** It is the fail-closed direction: a new execution
  needs a new freeze or namespace.
* **QR1.N-15** is carried and partly enforced mechanically.
* **The R1R dispositions** are unchanged from the accepted round, with Q09 now covering V07.
* Everything I found (N-1 to N-11 below) is launcher- or governance-level. None of it touches the frozen
  scientific object.

## BLOCKERS

none

## NON-BLOCKING NOTES

**N-1. A repository configuration that breaks the seal after consumption is not in the preflight:
`core.autocrlf=true` with `core.safecrlf=true`.**
* **Where.** `seal_safety_problems` checks git attributes on the seal paths (`check-attr -a`) but not
  their configuration equivalents. `GIT_PREFIX` does not pin `core.autocrlf` or `core.safecrlf`.
* **Evidence.** In a scratch repository with both keys set repo-locally:
  * preflight and gate pass, and the execution is consumed and run;
  * the private-index `git add` fails "LF would be replaced by CRLF";
  * after 7 attempts the result is UNSEALED (exit 4);
  * `--seal-only` stays UNSEALED while the keys are set, and seals correctly on the start commit after
    `git config --unset core.safecrlf`, without rerunning the stub.
* **Why it does not block.**
  * It needs a deliberate two-key configuration change. Neither key is set in the real repository, and
    global and system configuration are disabled.
  * The failure lands in the designed, correctly labelled UNSEALED state, and the recovery works.
  * It does falsify the prose invariant "Nothing checkable before consumption is deferred past it".
* **Authorization condition.** The authorization review verifies that the repo-local and worktree
  configuration has no `core.autocrlf`, `core.safecrlf` or `core.eol` (in the launcher's environment:
  `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git config --show-origin --list`).
* **Future hardening.** Add `-c core.autocrlf=false -c core.safecrlf=false` to the seal's git calls, or
  refuse them in the preflight.

**N-2. An unwritable launcher log directory consumes the execution without starting the runner.**
* **Where.**
  * `Journal.event` swallows write failures, so the `preflight_pass` event cannot detect the condition.
  * The execution log is first created by `run_once` (`open(…, "x")`), after `consume()`.
  * `seal_only` treats "no log and no runs content" as "nothing to seal".
* **Evidence.** With a pre-existing, mode-555 log directory:
  * consumed, stub not started;
  * `EXECUTION CONSUMED — RESULT UNSEALED`, outcome UNKNOWN, permission error on the log;
  * `--seal-only` answers `SEAL-ONLY REFUSED … nothing to seal`.
* **Why it does not block.**
  * `<common>/c11rd_r1` does not exist, and the launcher creates it with the user's permissions. The
    state therefore needs deliberate interference.
  * It is fail-closed: nothing ran and nothing can be run again, because of the consumed ref.
  * The one execution would be wasted, and no history record would exist beyond the consumed ref.
* **Condition and hardening.** The authorization review confirms that `.git/c11rd_r1` is absent, or is
  a writable directory owned by the user. A future launcher should create the execution log, or at
  least test the directory's writability, in the final gate, and should let the seal-only recovery seal
  the journal alone as CONSUMED_RUNNER_NOT_STARTED.

**N-3. The common dir is shared by 33 linked worktrees (one of them prunable) and the main checkout.** At 15e70072 (detached),
the main checkout is likely to be used by other sessions. Git activity in any of them:
* creates transient `*.lock` files under the common dir and `refs/`, which makes the preflight or gate
  refuse (safe: retry);
* can contend on shared ref locks during the seal.

A persistent `HEAD.lock` or branch lock gives UNSEALED, and the seal-only recovery then works (my
probes). Authorization requirement 4 ("no IDE or git client attached") should name the whole common dir:
no commits, gc, `pack-refs` or maintenance in ANY worktree of `/Users/suzhe/ReBaseGuard/.git` during the
run.

**N-4. Terminal job control and hangup.**
* **SIGTSTP.** "SIGTSTP is recorded and ignored" is true of the launcher only. The runner and its spawn
  workers share the launcher's foreground process group with default dispositions. A terminal Ctrl-Z
  therefore stops them while the launcher keeps waiting; the wall clock keeps running, and SIGCONT
  resumes them.
  * I could not reproduce this in the sandbox: SIGTSTP to a new-session group is discarded, because the
    group is orphaned. This is POSIX semantics, and it is also why Q13 S1 only signals the launcher.
* **Hangup.** A terminal hangup kills the runner, giving CONSUMED_NO_RESULT, sealed (fail-closed).
* **Condition.** The authorization should require a terminal that stays open for up to 12 h, or a
  tmux/screen session, and no Ctrl-Z.
* **Minor.** The handlers are restored in `launch()`'s `finally`, before `main()` prints the report. The
  "until the report is printed" wording is slightly optimistic. A signal in that window only loses the
  printed text; the seal, journal and UNSEALED file are unaffected.

**N-5. Two recoveries lack instructions.**
* **Index refresh.** When `index_refreshed` is false, which Q12 P4 shows with a stale `index.lock`, the
  SEALED text gives no instruction. The namespace then shows staged deletions of the sealed files plus
  untracked copies until `git reset -q -- <ns>/evidence/runs` runs.
* **Moved branch.** For a moved branch (P3), the UNSEALED text says only "clear the blocking condition".
  The seal-only recovery needs HEAD back at the start commit on the launch branch. The authorization
  packet should give the exact commands, keeping the foreign commit on another ref.

**N-6. The L1 predicate does not check `sys.flags.optimize` or `-X` options.** An exactly sanitized
`python3 -I -S -B -O` passes L1. The runtime binding then refuses it, because it loads unbound
`.opt-1.pyc` files (I verified this in-process). The runner is always started with exactly `-I -S -B`.
The gap has no effect.

**N-7. Q10 does not scan plain integers without a point or exponent.** For example, a thousandfold
rendering written as an integer would be missed. My scan covers them (0 hits). The tool's module
docstring still says the leak scans "need the two disclosed original values on stdin". That is stale:
the code reads no stdin.

**N-8. Runtime-binding residual.** Launch re-hashes all 227 bound files, but only the launcher's own
loaded set is checked for completeness. The runner's set is bound from the runner-like probe and its
workers, and the frozen code's lazy imports (`re`, `socket`, `multiprocessing`, `c11rd_tm`) are covered
there. Only deliberate tampering could exploit the difference.

**N-9. `main()`'s success path is never exercised end to end.** Q14 covers refusals; the sandbox drives
`launch()`. It cannot be exercised without a sandbox that holds the real frozen runner. Every defect
there would be a pre-consumption refusal (fail-closed).

**N-10. Disclosure about the original values.** The document discloses (§8) that the author tried to
recover the two original values from the session transcript for the old stdin interface, and that the
permission policy refused it. Nothing leaked (item 6). The value-free redesign removes any need for the
values. The authorization and execution rounds should keep the rule that nobody recovers, echoes or
pipes them.

**N-11. Theoretical: an unreported consumption.** If `git update-ref` created the consumed ref but still
returned non-zero, `consume()` would report `REFUSE L4 … consumed nothing`. A cheap re-read of the ref on
failure would close this. I could not produce the state.

**Authorization conditions carried forward (QR1.N-15 as carried by the artifact, plus N-1 to N-4).**
* The grant has the qualified values:
  * `freeze_commit` = `ce5b8595` exactly;
  * qualification commit = `e627d4ec` (the commit of this artifact);
  * qualification review = the commit preserving this review;
  * the canonical r1q_r1 paths.
* The launcher's sha256 at the authorization commit is `81ccc048…`. The r1 launcher and direct runner
  invocation are not permitted.
* The launch uses the exact `launch_command` at HEAD = the authorization review commit.
* The repository has:
  * a clean index;
  * no lock file;
  * no `core.autocrlf`, `core.safecrlf` or `core.eol` in repo-local or worktree configuration (N-1);
  * no or a writable `.git/c11rd_r1` (N-2).
* No git activity in any worktree of the common dir (N-3).
* An idle host, AC power, the lid open, a terminal that stays open, and no Ctrl-Z (N-4).
* After exit 4 or a launcher death, nothing but `--seal-only`.

## Commands I ran

Everything ran from the worktree or from `<SCRATCH>` = `…/scratchpad/c11rd_review_q2`. Writes went only
to `<SCRATCH>`. `P` = `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`.
```
git status --porcelain --ignored --untracked-files=all | wc -l   (0 before/after every step); git for-each-ref refs/c11rd | wc -l (0)
git rev-parse HEAD; git log --oneline -8; git diff --stat 89330534 e627d4ec; git diff --name-status ce5b8595 HEAD
git diff --stat ce5b8595 HEAD -- <ns>/code <ns>/protocol <ns>/theory   (empty); git diff --stat 3addf9d3 HEAD -- <r1 paths> (empty)
git diff --stat 89330534 HEAD -- <ns>/review (empty); git diff --name-only 89330534 HEAD | grep -v <ns>/ (none); git log -1 --format=%B e627d4ec
cat <ns>/review/C11RD_R1_QUALIFICATION_REVIEW.md; Read docs/C11RD_R1Q_R1_QUALIFICATION.md; cat -n qualification_r1q_r1/code/c11rd_launch.py (all)
sed -n on qualification_r1q_r1/code/c11rd_qualify.py (header, Q05-Q14, sandbox, STUB, DRIVER, leak scanner, run, main)
sed/grep on code/c11rd_runs.py (barrier, R0-R7, grant_problems, take_lock, main, log calls), code/c11rd_compare.py (value_patterns,
    leak_hits, verify_seal, main start), code/c11rd_validate.py (_hashed_leak_scan, V18)
P -I -S -B <SCRATCH>/hashcheck.py        (code/doc/input/freeze hashes; blobs at ce5b8595/3addf9d3/89330534/3c1eff11/HEAD; verdict lines)
P -I -S -B -c <print artifact keys and blocks>; shasum of the two new code files
cd qualification_r1q_r1/code && /usr/bin/time -p P -I -S -B c11rd_qualify.py --out-dir <SCRATCH>/q --write-artifact   (14/14 PASS, 412.8 s)
P -I -S -B <SCRATCH>/cmp.py <SCRATCH>    (key-by-key diff vs committed artifact and checks JSON); P -I -S -B - <validation JSON diff>
cd code && P -I -S -B c11rd_validate.py --out <SCRATCH>/standalone_validation.json   (29/29 PASS)
env -i <SAFE_ENV> P -I -S -B <SCRATCH>/dyld_probe.py ; .../bin/python3 -I -S -B <SCRATCH>/dyld_probe.py ; ps -o comm= ; lsof -p <pid> (txt) ;
    shasum -a 256 <stub> <Python.app image> <libpython>; otool -L <Python.app image>
env -i ... P -I -S -B [-O | -X frozen_modules=off] -c <LA.runtime_problems(committed artifact)>
P -I -S -B <SCRATCH>/my_leak_scan.py      (value-free; frozen hash set only; decoy controls)
P -I -S -B <SCRATCH>/my_probes.py <SCRATCH>   (A/B repaired T2/T11; C1/C2 rejected T2/T11; D1-D10)   -- scratch repos, STUB only
P -I -S -B <SCRATCH>/my_probes2.py <SCRATCH>  (CRLF configurations; seal-only before/after unsetting)
P -I -S -B <SCRATCH>/my_probes3.py <SCRATCH>  (manyFiles, splitIndex, untrackedCache+fsmonitor, useConfigOnly, logAllRefUpdates)
P -I -S -B -c <SIGTSTP to a new-session group: discarded (orphaned group)>
Real repository, refusal paths only:
  python3 -I -S -B <launcher> --authorization-review-commit 000…0 --preflight-only           -> REFUSE L2: no grant (exit 2)
  env GIT_DIR=… GIT_WORK_TREE=… PYTHONPATH=… HOME=/tmp FOO=bar python3 <launcher> … --seal-only -> REFUSE L2: no grant (exit 2)
  env -i <SAFE_ENV> C11RD_LAUNCH_SANITIZED=1 python3 -I -S -B -O <launcher> … --preflight-only  -> REFUSE L2: no grant (exit 2)
  python3 -I -S -B <launcher> --authorization-review-commit=--help                            -> REFUSE L2: … 40-hex (exit 2)
Read-only git: rev-parse main origin/main; for-each-ref refs/replace refs/c11rd; rev-parse --is-shallow-repository; stash list; worktree list;
  log --all --reflog --full-history -- <lifecycle paths>; config --show-origin --list (launcher env); check-attr -a -- <seal paths>;
  rev-parse --show-ref-format; symbolic-ref HEAD; var GIT_COMMITTER_IDENT; ls .git/info .git/worktrees/ReBaseGuard-k5c11rd
uptime; pmset -g batt; ps -A (no c11rd_runs.py, no stray caffeinate after the runs)
P -I -S -B <SCRATCH>/my_leak_scan.py <this review>   (0 hits)
```
I never opened the C11R quarantine, `C11R_COMPARISON.json`, `REGISTRY_C2.json` or any original cell or
denominator artifact. I never recovered or used the original values. Nothing was computed at a cell
306-309 drift.
