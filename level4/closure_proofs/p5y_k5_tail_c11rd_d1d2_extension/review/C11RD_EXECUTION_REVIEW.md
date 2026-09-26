# C11RD-R1 execution review
EXECUTION_ACCEPTED

Reviewer: a fresh, independent, read-only execution reviewer. Scope: integrity, authorization, exactly-once
semantics, runtime and memory caps, seal correctness, evidence completeness, and preservation of the frozen
scientific object. I did not read, derive, restate or compare any target D1/D2 magnitude. I parsed the runs
artifact with a whitelist script that prints only non-magnitude fields: identities, statuses, value presence,
timings, cover counts and resource accounting. This file contains no D1/D2 magnitude and no number derived from one.

## Summary

The one cell-306 D1/D2 execution under freeze `ce5b8595` ran once, completed and was sealed correctly.

* **Authorization chain.** A `6bab71b9` -> R `e320d8f5` -> G `4b716d43` -> seal `4547bcd4` is linear. Each
  commit adds exactly what the authorization artifact prescribes.
* **Grant.** The grant is byte-identical to `serialize(fill(grant_template, A, R))`.
* **Launch.** The qualified launcher (sha256 `81ccc048…`) was launched at HEAD == G from inside tmux, after
  `--launch-preconditions` printed PASS.
* **Consumption.** It consumed `refs/c11rd/r1-execution-consumed` -> G at 11:29:21Z.
* **Runner.** The frozen runner started once at 11:29:21Z and exited once with code 0 at 11:55:01Z. Its status
  is CERTIFIED: 4/4 sub-blocks, 1,540.4 s against the 43,200 s cap, and a peak sampled process-tree RSS of
  193,984 KiB (189.4 MiB) against the 2 GiB cap.
* **Seal.** The seal landed on attempt 1 at 11:55:02Z, one second after the runner exited. The seal commit's
  only parent is G, and it adds exactly the four `evidence/runs/` files. They are byte-identical on disk.
* **Evidence.** The journals, the runner log, the lock and the runs artifact agree with each other and with
  the grant and the freeze.
* **No other activity.** No git object, ref, reflog or index was written anywhere in the common dir between G
  and the seal, except by the consumption and the seal.
* **Frozen object.** Unchanged: the frozen code, protocol and theory are identical to the freeze. Local main
  and origin/main are unchanged. Cells 307-309, the comparator, adoption and r6 were not touched.
* **Watcher false trigger.** The first watcher's false trigger was a read-only `grep` matching the echoed
  command text. It had no causal path to the execution or the seal.

No blocker.

## Mechanical checks

| check | result | evidence |
|---|---|---|
| HEAD | PASS | `4547bcd428cea7219eb59ec793c0949e87a6524d`, on `refs/heads/p5y-k5-tail-c11rd-d1d2-extension` |
| seal parents | PASS | `git rev-list --parents -n1 HEAD` shows only `4b716d43ce8c48fb52dd320b91c33d2379cce410` (G); `rev-list --count G..HEAD` = 1 |
| seal content | PASS | `diff-tree` G..HEAD = exactly 4 `A` entries: `evidence/runs/C11RD_EXECUTION.lock`, `C11RD_EXECUTION.log`, `C11RD_LAUNCH_JOURNAL.jsonl`, `C11RD_RUNS.json`; no `.partial` |
| disk = sealed | PASS | `git hash-object` of each disk file equals `HEAD:<path>` (see the table below) |
| consumed ref | PASS | `refs/c11rd/r1-execution-consumed` = G (loose ref, file mtime 11:29:21Z; not packed) |
| runner starts / exits | PASS | exactly 1 start and 1 exit (see the runner-count row below) |
| runner exit code | PASS | 0: journal `runner_exited` has `runner_exit: 0`; the SEALED report has `runner_exit: 0`; the seal message says "runner exit 0" |
| launcher / chain exit code | PASS | the pane shows `C11RD_CHAIN_EXIT=0` after SEALED. This is the launcher's exit, because the `&&` left side printed PASS and the launcher ran. 0 = `EXIT_SEALED` |
| seal attempts | PASS | 1: journal `seal_attempt` has `attempt: 1`; no `seal_attempt_failed`; `sealed` has `attempts: 1`; SEALED `attempt_log` = [{attempt 1, ok}] |
| leftover processes | PASS | none (see the leftover-process row below) |
| frozen code | PASS | 8/8 `code/` sha256 on disk and at `ce5b8595` equal the freeze's `code_sha256`; C7 `c7_gaussian.py` sha256 matches |
| frozen protocol, theory, grant | PASS | see the frozen-protocol row below |
| input bindings | PASS | all 8 `input_bindings` blobs at HEAD equal the freeze's |
| authorization-bound documents | PASS | all 8 `document_sha256` entries match |
| main refs | PASS | local `refs/heads/main` = `c123b9bb8f15d17650545b3fce4aca8a6b61093b` (last reflog entry: an old fast-forward); `refs/remotes/origin/main` = `1cb453826313c189f0bdafd5b84120c1edb74da9` (last reflog entry: an old push); HEAD is in neither; no remote c11rd ref |
| cells 307-309, comparator, adoption, r6 | PASS | see the cells row below |
| worktree cleanliness | PASS | `git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step; no `__pycache__` or `.pyc` in the C11RD or C7 code directories |

Rows too long for the table:

* **Runner starts and exits (exactly 1 each).**
  * The launch journal has exactly one `runner_starting` and one `runner_exited`, under a single launch id
    `86632-1790422160.967846`.
  * The runner log has exactly one "C11RD execution started" line and one "runs artifact written" line.
  * There is exactly one lock.
* **Leftover processes (none).**
  * `ps` finds no `c11rd_runs.py`, `c11rd_launch.py`, `c11rd_authorize.py`, multiprocessing worker,
    caffeinate or git process.
  * pid 86632 is gone, and there is no caffeinate power assertion.
  * The only remaining processes are the tmux server (85800), its `zsh -f` (85801) and the pipe-pane
    `cat` (85805).
* **Frozen protocol, theory and grant (unchanged).**
  * `git diff ce5b8595 HEAD` over `code/ protocol/ theory/` is empty.
  * The namespace diff since the freeze has only `A` entries: the qualification, authorization, review,
    grant and runs files. Nothing present at the freeze was modified.
  * Nothing changed outside the namespace since the freeze.
  * `protocol/C11RD_FREEZE_R1.json` is byte-identical at `ce5b8595` and has sha256 `07118d30…`, which equals
    the grant's `freeze_sha256` and the authorization binding.
  * The grant on disk equals the grant at G and at HEAD.
* **Cells 307-309, comparator, adoption, r6 (none).**
  * The grant, the lock and the runs artifact name cell 306 only.
  * Nothing in the tree since the freeze matches compar/r6/adopt/coverage/307-309.
  * No runs or comparison directory exists in any other worktree of the common dir.
  * `code/c11rd_compare.py` is unchanged.

Sealed files (disk blob = committed blob):

| file | blob | size |
|---|---|---|
| C11RD_RUNS.json | `30e2dfd0ac87aad74f8a9490fee99623cbdf151d` | 173,199 |
| C11RD_EXECUTION.lock | `2d83c17d9d52546609300a60159a2e750ae462ea` | 447 (mode 0444, mtime 11:29:21Z) |
| C11RD_EXECUTION.log | `bdefdf2820fb3eca3494016738d6784aa0d3d31c` | 2,719 |
| C11RD_LAUNCH_JOURNAL.jsonl | `a9eabae2827881dab0d7a65daa5ac53bdfaf11c6` | 1,006 |

## Findings per item

### 1. Authorization chain A -> R -> G -> seal - PASS

* **A `6bab71b9`.** Parent `e27c2ffd`, the accepted qualification review. It adds exactly the six
  `authorization_r1/` files.
  * The artifact on disk equals the artifact at A.
  * `authorization_tool_sha256` matches the tool.
* **R `e320d8f5`.** Only parent A. It adds exactly `review/C11RD_AUTHORIZATION_REVIEW.md`, which holds
  exactly one AUTHORIZATION_ACCEPTED line and no AUTHORIZATION_REJECTED line. The disk copy equals the copy
  at R.
* **G `4b716d43`.** Only parent R. It adds exactly `config/C11RD_GRANT.json`.
  * The grant bytes equal `json.dumps(fill(grant_template, A, blob(artifact@A), R, blob(review@R)), indent=1,
    sort_keys=True)+"\n"`, recomputed independently.
  * The grant is sha256 `f968f2cf…`, with `decision` ALLOW and `max_executions` 1.
  * Target: cell 306, D1/D2, on `[680769/400000, 17885921/10000000]`.
  * Host and worktree are the qualified ones, and the launcher is bound by sha256 `81ccc048…`.
* **Seal `4547bcd4`.** Only parent G.
* **Consumed ref.** Points to G.
* **Ancestry.** freeze <= qualification `e627d4ec` <= its review `e27c2ffd` <= A.
* **Qualification.** The qualification review holds exactly one QUALIFICATION_ACCEPTED line. The
  qualification artifact blob `1d79ad42…` is the same at `e627d4ec` and at HEAD. It binds the launcher sha256,
  the frozen runner sha256, the caps (43,200 s, 2,097,152 KiB, 5 workers) and the launch limits.
* **Launcher.** Its blob at HEAD equals its blob at `e627d4ec` (`a169f1de…`).
* **Authorization review N-1 condition.** Every item it asks for holds: the consumed ref and the seal's parent
  are G; G adds exactly the grant; R adds exactly the review; R's parent is A.
* **N-2 (`--check-grant` run and kept).** `exec_check_grant.json` (11:28:03Z) holds 8/8 checks true. It
  records an empty `frozen_grant_problems`, the launcher `--preflight-only` result rc 0 "PREFLIGHT PASS", and
  the same grant sha256 `f968f2cf…`.

### 2. Launch preconditions at execution start - PASS

* **`--launch-preconditions` in the pane.** It printed `ok` for P-01, P-02/P-03, P-03, P-04, P-05, P-06,
  P-07, P-08, P-09, P-10, P-13 and P-15, then `LAUNCH PRECONDITIONS PASS`. It is the left side of `&&`, so
  the launcher ran only because it passed.
* **P-10 (inside tmux).** The pane's shell is `/bin/zsh -f` (85801), a child of the tmux server (85800). The
  server was started as `tmux new-session -d -s c11rd … -c /Users/suzhe/ReBaseGuard-k5c11rd /bin/zsh -f` at
  11:27:23Z, with `TMUX` set. tmux 3.7c is installed in the Homebrew Cellar, whose directory mtime is
  11:25Z.
* **P-14 (exact command).**
  * The pane shows the launcher run with the absolute framework interpreter and `-I -S -B` only.
  * The journal's `runner_starting.cmd` is exactly
    `[/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14, -I, -S, -B, <ns>/code/c11rd_runs.py, --mode, real, --authorization-review-commit, G]`.
* **The launcher's own preflight and gate.**
  * The journal starts with `preflight_pass` (11:29:20Z). The launcher writes it only after `preflight()`
    returns no problem. That covers the host, interpreter and runtime files, worktree, launcher sha256, the
    frozen grant check, runner guards R0/R1/R4/R5/R6-R7, the seal-safety preconditions, AC power, lid, load,
    disk, memory, the process table, no other runner and no consumed ref.
  * The journal then has `consumed` at 11:29:21Z and no `gate_refused` event. In the launcher's code,
    `consume()` is reached only after `start_sleep_prevention()` has verified both assertions and
    `final_gate_problems()` is empty.
* **Load at start.** The lock's `loadavg_at_start` is [1.2861328125, 2.6611328125, 3.60205078125]. The 1-min
  value is within the qualified maximum of 2.0, and only the 1-min value is gated. The operator reported
  waiting for a 1-min load of 1.49. That value is not recorded anywhere I could read, but the 1.29 in the lock
  one second later is consistent with it.
* **Caffeinate (P-12).**
  * `pmset -g log` shows caffeinate pid 86682 creating PreventSystemSleep at 11:29:20Z.
  * Both PreventUserIdleSystemSleep and PreventSystemSleep are held in the 15-min summaries (11:30:05Z and
    11:45:05Z).
  * Both end with ClientDied at 11:55:02Z, after 25:41 held, which is the launcher's exit.
  * No Sleep, Wake or DarkWake event appears between 11:20Z and 12:09Z; the only power-log entries in that
    window are Assertions.
* **Runner guard R3.** The runner started, took the lock and wrote a CERTIFIED artifact, so it passed its own
  guards R0-R7 at start.

### 3. Exactly-once semantics - PASS

* One launch id appears in the external journal (`86632-…`) and no other journal, UNSEALED report or leftover
  seal index exists in `<common>/c11rd_r1/`.
* **Consumption.** The consumed ref was created once, create-only, at 11:29:21Z by the ref file's mtime and
  the `consumed` event.
* **Lock.** The lock was created once and exclusively (0444, 11:29:21Z) and is now in history. Runner guard
  R4 and the consumed ref now refuse any further run, and the grant binds `max_executions` 1.
* **Counts.** One `runner_starting`, one `runner_exited`, one "execution started" log line and one seal
  commit.
* **No retries.** No REFUSE or retry is visible in the pane.
* **Worker count.** The per-sub-block `distinct_pids_seen` (20/19/19/19) equals 1 runner + 5 workers +
  1 multiprocessing resource tracker + one `ps` per memory sample (13/12/12/12). That is consistent with
  exactly 5 workers and no worker replacement.

### 4. Runtime - PASS

`execution.seconds` = 1,540.4 s. The journal gives 11:29:21Z -> 11:55:01Z = 1,540 s, and the runner log's
last progress line says "1540s". Both are well below the frozen 43,200 s wall cap (about 3.6%). The runner's
own in-loop cap check would have ended the run with RESOURCE_CAP_WALL and NOT_CERTIFIED; the status is
CERTIFIED.

### 5. Peak process-tree RSS - PASS

* `max_tree_rss_kb` per sub-block: 180,000, 187,648, 193,984 and 177,968. The maximum is 193,984 KiB
  (189.4 MiB), which is about 9.3% of the 2,097,152 KiB cap.
* 49 samples were taken in total (13/12/12/12), one about every 30 s as frozen. Each sample covers the runner
  and all its live descendants.
* No RESOURCE_CAP_MEMORY or RESOURCE_ACCOUNTING_FAILED occurred.

### 6. Four sub-blocks and the expected structure - PASS

* **Sub-blocks.** `execution.sub_blocks` has 4 entries. Their `e_lo`/`e_hi` equal the freeze's
  `D_sub_block_partition` and the authorization's `target.sub_blocks` exactly, tiling
  `[680769/400000, 17885921/10000000]`.
* **Cover counts.** Each sub-block has `initial_boxes` 168 (the authorization's `initial_boxes` 168),
  `boxes_evaluated` 172 and `leaves` 171.
* **Log.** The runner log shows the same sequence for each of the 4 sub-blocks: proposal, cover, 9 progress
  lines, and "168/168, boxes evaluated 172".
* **Status.** Top-level `status`, `execution.status` and both `targets[k].status` are CERTIFIED, and both
  `targets[k].value` are present. I checked presence only.
* **Keys.** The artifact keys are exactly those `c11rd_runs.main` writes. Both statements have aggregation
  `max_over_sub_blocks` over 4 sub-blocks, drift domain = the frozen block, and producer `file_sha256` = the
  frozen runner's `5cbd8916…`.
* **Premise keys.** `A, B, C_T, certificate_id, certifier, input_digest, source, statement, tau` (keys
  only).

### 7. Seal immediately after the runner exit, attempt 1 - PASS

* **Timeline.** `runner_exited` at 11:55:01Z, then `seal_attempt` 1 at 11:55:01Z, then `sealed` at 11:55:02Z.
  The commit and committer time is 1790423702 (11:55:02Z).
* **Refs.** The branch reflog and the worktree HEAD reflog hold one entry "C11RD-R1: immediate seal", G ->
  `4547bcd4`, at the same second.
* **SEALED report.**
  * `outcome` COMPLETED_CERTIFIED, `seal_attempts` 1, `index_refreshed` true.
  * `namespace_clean_after_seal` true, `signals_deferred` [], `start_head` G.
  * `sealed_paths` = the 4 files.
* **Objects.** The seal wrote exactly 4 blobs, the 6 trees on the path from the root to `evidence/runs`, and
  1 commit, all at 11:55:02Z.

### 8. Internal consistency and completeness of the artifacts - PASS

* **Lock and runs artifact agree.**
  * `head` = G (both), `freeze_commit` = `ce5b8595` (both, and the grant).
  * `started_utc` 11:29:21Z (both), `grant_sha256` `f968f2cf…` (both, and the grant file and `exec_check_grant.json`).
  * `host` = the grant's host (both; the runs artifact adds the same `loadavg_at_start` as the lock).
* **Runs artifact identities.** `worktree` = the grant's worktree, and `authorization_review_commit` = G.
  `code_sha256` equals the freeze's, the grant's and the authorization's frozen code hashes.
* **Runner log.** The sealed runner log is byte-identical to the external runner log
  `<common>/c11rd_r1/C11RD_EXECUTION_4b716d43ce8c.log` (sha256 `dd657960…`). It carries progress counters and
  timings only.
* **Launch journal.** The sealed launch journal (5 events, through `seal_attempt` 1) is an exact byte prefix
  of the external journal. The external journal adds only the final `sealed` event, because the launcher
  copies the journal into `evidence/runs/` before the seal commit exists.
* **Files.** The artifact, lock, log and journal are all present; there is no `.partial` and no
  unexpected file.
* **Times.** The runner log shows local time (JST, UTC+9) and the journal and lock show UTC. They are
  consistent.

### 9. No post-G commit preceded the automatic seal - PASS

* **Reflogs.** Across every reflog in the common dir and every worktree, the only entries at or after G's
  time are G itself (11:17:27Z) and the seal (11:55:02Z), on the branch and in the worktree HEAD reflog.
* **Parents.** The seal's only parent is G.
* **Objects.** The only loose objects with mtime after G are G's own (11:17:27Z) and the seal's
  (11:55:02Z), and there is no new pack.
* **Refs.** The only refs modified after G are the consumed ref (11:29:21Z) and the branch (11:55:02Z).
* **Git dirs.** Between G and 12:07Z, no file or directory in the common dir or any worktree's git dir
  changed except these:
  * the launcher's log directory (created 11:29:20Z);
  * the consumed ref;
  * the seal's branch ref, reflogs and the worktree index refresh (11:55:02Z).

  In particular, no `index.lock` churn occurred in any other worktree or in the main checkout's git dir during
  the execution. This supports the operator's statement that it ran no git command between the launch and
  the SEALED report.

### 10. The first watcher's false trigger had no causal effect - PASS

* **Mechanism.**
  * The raw pane log holds the substring `C11RD_CHAIN_EXIT=` at byte offset 1102, inside the echoed command
    line `…; echo "C11RD_CHAIN_EXIT=$?"`.
  * That offset is before `LAUNCH PRECONDITIONS PASS` (offset 1831) and `SEALED {` (offset 2242).
  * The real `C11RD_CHAIN_EXIT=0` is at offset 3028.
  * So `grep -aq "C11RD_CHAIN_EXIT="` matched the command text as soon as it was echoed. The 11:30:23Z exit
    is fully explained.
* **Capability.**
  * The watcher only ran `grep`, `sleep`, `date`, `tr` and `cut` on the pane log, in the operator's own
    shell and not in the tmux pane.
  * It sent no keys, no signals and no git command, and wrote nothing to the repository or the pane.
  * Reading the pipe-pane output file cannot affect tmux, the launcher or the runner.
  * The later read-only check and the second watcher are also reads: python reading the journal, `tail`,
    `ps`, `uptime`, and `grep` plus `ps -p` on the journal.
* **Evidence of no effect.**
  * `signals_deferred` is [] in the SEALED report, so no SIGINT, SIGTERM, SIGHUP, SIGQUIT or SIGTSTP reached
    the launcher between the gate and the report.
  * The journal is continuous: `preflight_pass`, `consumed`, `runner_starting`, `runner_exited`,
    `seal_attempt`, `sealed`. It has no `runner_not_started`, `runner_start_failed`, `seal_attempt_failed`
    or `unsealed` event.
  * The runner log is continuous across 11:30:23Z: progress lines at 20:30:09 and 20:30:54 JST, with the
    usual about-45 s spacing and no restart.
  * The runner exited 0 once, the seal landed on attempt 1, and no git write occurred in the window (item 9).
  * The second watcher's end at 11:55:51Z is consistent with its 60 s poll after `sealed` at 11:55:02Z.

## BLOCKERS

none

## NON-BLOCKING NOTES

* **NB-1. The operator account says ONE command line was sent in the pane; the pane shows two.** The first
  was a diagnostic `echo "TMUX=${TMUX:+set} pwd=$(pwd)"; ps -o pid=,ppid=,comm= -p $$ -p $PPID`. It is
  read-only, has no git, and finished before the launch line. It has no effect, but the account is
  imprecise.
* **NB-2. The launch time 11:29:19Z cannot be verified to the second.** The pane log has no timestamps.
  The launch id (Journal init after preflight) is 11:29:20.97Z. Consistent.
* **NB-3. An unexplained caffeinate assertion before the launch.** A separate caffeinate (pid 86123) created
  and dropped an assertion at 11:28:03Z, the same second `exec_check_grant.json` was written. It lived 0 s,
  before the launch, and has no bearing on P-12, which caffeinate 86682 satisfied.
* **NB-4. The host was not demonstrably idle for the whole run** (authorization review N-3).
  * At start, the 5-min and 15-min loads (2.66, 3.60) were above the 1-min gate value. Only the 1-min load
    is gated.
  * The clawd-on-desk Electron app ran throughout (started 2026-09-20). It is not known to run git, and no
    git write occurred in the window.
  * The run used about 3.6% of the wall cap, so contention had no cap consequence. Timing cannot change a
    certified interval result.
* **NB-5. The consumed ref has no reflog.** `refs/c11rd/*` is outside git's default reflog namespaces. Its
  creation time is evidenced by the ref file's mtime (11:29:21Z) and the journal.
* **NB-6. The sealed journal copy ends at `seal_attempt` 1, by design.** The `sealed` event exists only in
  the external journal, which should be kept alongside the review.
* **NB-7. Memory is sampled, not continuous.** Accounting is at about 30 s intervals, per the freeze. A
  transient peak between samples is unobserved; the observed peak is about 9% of the cap.
* **NB-8. My own `git status` touched the worktree git dir after the seal.** My first
  `git status --porcelain --ignored --untracked-files=all`, at 12:07:15Z, created and removed an optional
  `index.lock` in `.git/worktrees/ReBaseGuard-k5c11rd`. That directory's mtime is 12:07:15Z, the same second my
  scratch directory was created. It was after the seal, and it changed no content: the index mtime stays
  11:55:02Z and status is 0 lines. All later status calls used `GIT_OPTIONAL_LOCKS=0`.
* **NB-9. The atime of comparison-only files was not used as evidence.** I stat'ed (did not open) the C11R
  quarantine, the C11R comparison and `c11rd_compare.py`. APFS access-time updates are relaxed, so atime
  proves nothing either way.

## Commands I ran

Setup: `P` = `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B`,
`<ns>` = `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension`, cwd = `/Users/suzhe/ReBaseGuard-k5c11rd`
unless stated, `<S>` = my scratch directory.

Repository state:

* `git status --porcelain --ignored --untracked-files=all | wc -l`. Printed 0, before and after; later runs
  used `GIT_OPTIONAL_LOCKS=0`.
* `git rev-parse HEAD`
* `git log --format='%H %P …' -5`
* `git rev-parse --abbrev-ref HEAD`
* `git rev-parse --git-common-dir`

The seal:

* `git rev-list --parents -n1 HEAD`
* `git diff-tree --no-commit-id -r --name-status -M HEAD`
* `git cat-file -p HEAD`
* For each of the 4 runs files: `git hash-object <file>` vs `git rev-parse HEAD:<file>`, and `wc -c`
* `git show-ref | grep c11rd`
* `git for-each-ref refs/c11rd`
* `git ls-tree -r --name-only HEAD <ns>`
* `ls -la` of `authorization_r1/`, `config/`, `evidence/runs/`

Frozen files and evidence, read directly:

* `wc -l` and `shasum -a 256` of the launcher, the runner and the authorize tool
* Read `authorization_r1/C11RD_AUTHORIZATION.md`.
* Structural dump of `C11RD_AUTHORIZATION.json` with `P -c` (the artifact holds no target magnitude).
* Read `qualification_r1q_r1/code/c11rd_launch.py` and `code/c11rd_runs.py` in full, and `c11rd_authorize.py`
  lines 560-700.
* `cat` of the sealed lock, journal and runner log.
* `ls -la@` and `cat` of `/Users/suzhe/ReBaseGuard/.git/c11rd_r1/`.
* `cmp` and `shasum` of the external vs sealed runner log.
* `head -c <n> | cmp`: the sealed journal is a prefix of the external journal.
* `stat` of the c11rd_r1 files.

Pane log and tmux:

* The pane log stripped of escape codes with a `P -c` regex script into `<S>/pane_stripped.txt`, then
  `cat -v`.
* `cat <scratch>/r1qr1/exec_check_grant.json`
* `tmux ls` and `tmux capture-pane -p -S - -t c11rd`, read only; no keys sent.

Processes:

* `ps -A -o pid=,ppid=,lstart=,etime=,command=` filtered for c11rd, caffeinate, multiprocessing, python and
  git.
* `ps -p 86632`
* `ps` of the tmux tree
* `uptime`
* `date -u`
* `pmset -g assertions | grep caffeinate`

Whitelisted runs-artifact parse:

* `P <S>/whitelist_runs.py`, which printed only: schema, campaign, cell, mode, status, started/finished,
  head, freeze_commit, code_sha256, grant_sha256, authorization_review_commit, worktree, host identity and
  loadavg, premise keys, execution status and seconds, per sub-block e_lo/e_hi, resource_accounting and
  cover counts, and target status and value presence.

Identity and hash checks:

* `P <S>/hashes.py`: freeze file identity, the 8 code hashes on disk and at the freeze, C7 hash, input binding
  blobs, bound documents, grant = fill(template, A, R), grant sha256 vs lock and runs artifact, A/R disk
  identity, review verdict line counts, tool, launcher and qualification bindings, and lock vs runs artifact
  vs grant fields. It printed booleans and identities only.
* `P -c` printing freeze sections P, M, N, O, K, R, S, T, V, D, `runner_guards` and FORBIDDEN.
* `git diff --name-status ce5b8595 HEAD -- <ns>`, and the same for everything outside `<ns>`.
* `git diff --quiet ce5b8595 HEAD -- <ns>/code <ns>/protocol <ns>/theory`

History, refs and objects:

* `cat`/`tail` of the branch reflog, the worktree HEAD reflog and the (absent) consumed-ref reflog.
* `cat` of the consumed ref file, and `grep packed-refs`.
* `stat` of the git-dir files.
* awk scan of every reflog in the common dir and the worktrees for entries at or after G's time.
* `find <common>/objects -newermt '2026-09-26 20:17:00'` with `git cat-file -t`.
* `git ls-tree HEAD <ns>/evidence/runs`
* `git rev-parse` of the seal's tree path
* `git rev-parse refs/heads/main refs/remotes/origin/main`, and `tail` of their reflogs.
* `git merge-base --is-ancestor` checks (HEAD vs main and origin/main; freeze <= qualification <= review <= A;
  G <= HEAD).
* `git rev-list --count G..HEAD`
* `git for-each-ref` of refs dated after G.
* `git diff-tree` of G, R and A.
* `git rev-list --parents -n1` of the seal, G, R and A.
* `find <common>/refs -newermt …`
* `find <common> -newermt '2026-09-26 20:17:28' -not -path objects`
* `git worktree list --porcelain`, used to look for runs or comparison directories in other checkouts.
* `find <common> -name '*.lock'`
* `stat` of my scratch directory (for NB-8).

Host:

* `pmset -g log` filtered for caffeinate, and for event types in 20:20-21:09 JST.
* `grep` of the authorize tool for caffeinate and pmset.
* Read the authorization review's non-blocking notes (lines 261-335).
* `tmux -V` and the Cellar `ls`/`stat`.
* `ps` for IDE, git-client and clawd processes.
* `launchctl list | grep git`
* `stat -f %Sa` (atime; not opened) of the C11R quarantine, the C11R comparison and `c11rd_compare.py`. Not
  relied upon (NB-9).

Final checks:

* `GIT_OPTIONAL_LOCKS=0 git status … | wc -l`, which printed 0.
* `find` for `__pycache__`/`.pyc` in the C11RD and C7 code directories, which found 0.
* `grep -c` of the runner log's structure lines.

I did not run the runner, the launcher (any mode), `--make-grant`, the comparator or any C11R runner. I did
not open the C11R quarantine, the C11R comparison, REGISTRY_C2 or any original cell artifact, and I read no
session transcript or task output file. I made no commit, ref, stash, checkout or config change, and used no
network.
