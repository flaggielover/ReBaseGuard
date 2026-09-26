# C11RD-R1 authorization of the one cell-306 D1/D2 execution

Scope: AUTHORIZATION ONLY. Nothing was executed: no target runner, no D1/D2, no comparator, no cells
307–309, no adoption, no r6; r5 unchanged. No frozen scientific file and no historical qualification
or review artifact changed. This document and `C11RD_AUTHORIZATION.json` contain no target magnitude.
The live grant does NOT exist yet: it is created only after a fresh review accepts this artifact.

## 1. Lineage bound

| what | commit | identity |
|---|---|---|
| scientific freeze | `ce5b85959a1693525f9e001e7c191516a4ee7d76` | freeze JSON sha256 `07118d30…` |
| R1 pre-execution review | `3c1eff11562638727156f09a9c58b8dc704548a5` | READY_TO_QUALIFY, `dd4ccbda…` |
| rejected qualification / review | `3addf9d3…` / `8933053406b33cb4cc852dfd5b2231f507a552b3` | QUALIFICATION_REJECTED, `d95a2cb6…` (historical) |
| accepted qualification | `e627d4ecf402f6d7b827d8ab734b55f4ae41e0e6` | artifact blob `1d79ad42…`, sha256 `36aa5c68…` |
| accepted qualification review | `e27c2ffdc55f745e372f0e896d6bedc42a57f341` | QUALIFICATION_ACCEPTED, `be308335…` |
| qualified launcher | (at `e627d4ec`) | sha256 `81ccc0482994ba0a4febb8aa5d6ee551f84bb3e66957e06e821250180e11fb48` |

## 2. The authorization lineage and the launch commit

The frozen runner fixes the grant path (`config/C11RD_GRANT.json`) and the authorization review path
(`review/C11RD_AUTHORIZATION_REVIEW.md`), and requires that the commit given as
`--authorization-review-commit` hold BOTH the accepted review (exactly one `AUTHORIZATION_ACCEPTED`
line) and the byte-identical grant. The qualified launcher additionally refuses unless HEAD equals
that commit. Because the grant is created only after the review, the lineage is:

* **A** — this commit: the tool, the verification and self-test evidence, this document and the
  artifact, which freezes PROSPECTIVELY the exact grant (`grant_template`, sha256
  `423a81d9a99c5d14…`, plus the fill and serialization rule) and every launch precondition.
* **R** — parent A; adds exactly the fresh reviewer's file at `review/C11RD_AUTHORIZATION_REVIEW.md`,
  byte for byte, holding exactly one `AUTHORIZATION_ACCEPTED` line and no `AUTHORIZATION_REJECTED` line.
* **G** — parent R; adds exactly `config/C11RD_GRANT.json` whose bytes are
  `serialize(fill(grant_template, A, blob(artifact at A), R, blob(review at R)))`, written create-only by
  `--make-grant`. **G is the authorization commit the launch binds to: HEAD == G at launch, enforced by
  the launcher before consumption; the frozen runner re-checks the review and the grant at G.**
  Nothing may be committed after G before the launch.

The grant binds A and R by commit and blob. It cannot name G (a file cannot name the commit that contains
it); G is fixed by the launch command, the launcher's HEAD check and the frozen byte-identity check.

## 3. What the grant binds

Freeze `ce5b8595` and the freeze file's sha256; the 8 frozen code hashes and the 8 input bindings; the
qualified host (hostname, IOPlatformUUID, platform, Python 3.14.5) and canonical worktree (path, git common
dir); the accepted qualification (commit `e627d4ec`, canonical artifact path and blob, review commit
`e27c2ffd` at the canonical review path); the launcher path and sha256; the launch branch; target cell 306 on
`[680769/400000, 17885921/10000000]`, constants D1 and D2 only; `max_executions` 1; the authorization
artifact (A, path, blob) and review (R, path, blob); the launch rule and the scope. Through the qualification
artifact the launcher enforces the qualified interpreter (stub, running image, libpython), the 227 runtime files,
the launch limits and the frozen caps (43,200 s, 2 GiB, 5 workers); the runner enforces the frozen
scientific parameters through its code hashes.

## 4. Launch preconditions (explicit; every one must hold)

| id | condition | enforced by |
|---|---|---|
| P-01 | HEAD == G, the grant commit (the launch commit), on the qualified launch branch; nothing committed after G | qualified launcher (seal preconditions) + frozen runner R2 + --launch-preconditions |
| P-02 | clean index (== HEAD), no unmerged entry, clean worktree and namespace (ignored files included) | qualified launcher + --launch-preconditions |
| P-03 | no git lock file in this worktree's git dir, the common dir, refs/ or ANY other worktree's git dir; no merge, rebase, cherry-pick, revert, bisect or sequencer in progress | qualified launcher (own dirs) + --launch-preconditions (all worktrees) |
| P-04 | no repository-local or worktree core.autocrlf, core.safecrlf or core.eol (review QR2.N-1), no config.worktree, no git attribute on the seal paths | --launch-preconditions (+ the launcher checks attributes) |
| P-05 | the launcher log directory <git common dir>/c11rd_r1 is absent, or a writable directory owned by the user holding no execution log (QR2.N-2) | --launch-preconditions |
| P-06 | no git activity from any worktree of the common dir, any git client, IDE or fsmonitor daemon during the execution and the seal: no running git process at launch, no scheduled git maintenance (QR2.N-3) | --launch-preconditions (snapshot at launch) + operator: start no git command anywhere until SEALED or UNSEALED is printed |
| P-07 | the host is otherwise idle: 1-min load <= 2.0, no other runner process | qualified launcher + --launch-preconditions |
| P-08 | AC power connected | qualified launcher + --launch-preconditions |
| P-09 | lid open | qualified launcher + --launch-preconditions |
| P-10 | the launch runs inside tmux (the process is a descendant of the tmux server and TMUX is set) (QR2.N-4) | --launch-preconditions |
| P-11 | no Ctrl-Z / job-control suspension and no Ctrl-C of the pane while the launcher runs; the terminal is not closed (QR2.N-4) | operator procedure (not mechanically enforceable) |
| P-12 | qualified sleep prevention active: caffeinate -i -s verified (PreventUserIdleSystemSleep and PreventSystemSleep) before consumption | qualified launcher L3 |
| P-13 | qualified memory (>= 1 GiB available), disk (>= 2 GiB free), readable process table, interpreter and 227 runtime files re-hashed, host and worktree identity | qualified launcher + --launch-preconditions |
| P-14 | the exact launch command with the absolute framework interpreter and -I -S -B only (no -O, no -X) (QR2.N-6) | runbook + qualified launcher L1 |
| P-15 | no consumed ref, no runs artifact or lock, no execution log | qualified launcher + --launch-preconditions |

`--launch-preconditions` is read-only and consumes nothing; run it in the tmux pane immediately before
the launch command. Its checks are shown able to fail by `--self-test` (14/14: line-ending keys,
another worktree's lock, a non-writable log directory, an existing execution log, a running git program,
scheduled maintenance, each against a clean control).

**Known unmet precondition at authorization time: P-10.** tmux is not installed on this host. The launch
cannot proceed until it is installed and the launch runs inside it.

## 5. Runbook (for a later, separately instructed execution round)

1. Install tmux if it is absent (it is absent at authorization time); this is outside the authorization.
2. Open a NEW tmux session on this host; cd /Users/suzhe/ReBaseGuard-k5c11rd; close every IDE or git client attached to any worktree of /Users/suzhe/ReBaseGuard/.git and stop any other session's git activity.
3. In the tmux pane: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/authorization_r1/code/c11rd_authorize.py --launch-preconditions --authorization-commit <G>  -> must print LAUNCH PRECONDITIONS PASS (exit 0); otherwise stop and fix the cause (nothing is consumed).
4. Immediately, in the same pane: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_launch.py --authorization-review-commit <G>
5. Do not press Ctrl-Z or Ctrl-C, do not close the pane, do not run git anywhere, keep AC power and the lid open, until the launcher prints SEALED ... or EXECUTION CONSUMED — RESULT UNSEALED (it may take up to 12 h).
6. SEALED with index_refreshed false: after the blocking lock is gone, run only `git reset -q -- level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/evidence/runs` (QR2.N-5).
7. EXECUTION CONSUMED — RESULT UNSEALED (exit 4) or a launcher death: do nothing else; clear the blocking condition; wait until no c11rd_runs.py process remains; then only the seal-only recovery printed by the launcher. If the launch branch moved (permanent failure), stop and ask for a separately instructed recovery (QR2.N-5).
8. Any REFUSE (exit 2): nothing ran. Before retrying, check `git rev-parse --verify -q refs/c11rd/r1-execution-consumed`; if it exists, the execution IS consumed: only the seal-only recovery (QR2.N-11).
9. After SEALED: read no value; the next step is a separately instructed execution review, then the comparison.

## 6. Verification at authorization time

`C11RD_AUTHORIZATION_VERIFY.json`: **34/34 PASS**, entry HEAD `e27c2ffd`. It covers the lineage and byte
identities, the frozen object, the absence of any run, lock, log, seal, comparison, grant, authorization
review and consumed ref (disk and every history), the local/remote main refs (recorded separately, not
synchronized), no line-ending configuration, the log directory absent, no lock file in any of the 34
worktrees' git dirs or the common dir, no scheduled maintenance, the qualified host, worktree, branch,
interpreter and 227 runtime files, the runner's R0/R1/R4/R5/R6-R7 guards run in advance, and the grant
prospectively: the frozen runner's own grant check, given the template at HEAD, reports ONLY the two items
that exist later (the authorization review and the grant at the launch commit).

Housekeeping before the verification: an orphaned `git fsmonitor--daemon`, left by the qualification
reviewer's scratch probe (it watched a scratch worktree under this session's scratchpad, never the
repository), was stopped with `fsmonitor--daemon stop`. At launch P-06 refuses any running git program.

## 7. Governance

Target D1 computed: NO. Target D2 computed: NO. Target runner started: NO. Live grant: NO (until the
review is accepted). Cells 307–309 executed: NO. Adoption: NO. r6: NO. N9 OPEN. K5 PARTIAL. r5
authoritative. LOCAL_MAIN_REF `c123b9bb8f15d17650545b3fce4aca8a6b61093b`; REMOTE_MAIN_REF
`1cb453826313c189f0bdafd5b84120c1edb74da9`.
