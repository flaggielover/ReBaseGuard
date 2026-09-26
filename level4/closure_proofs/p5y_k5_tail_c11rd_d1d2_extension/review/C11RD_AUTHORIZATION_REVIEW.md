# C11RD-R1 authorization review
AUTHORIZATION_ACCEPTED

Reviewer: fresh, independent, read-only. Date 2026-09-26. Worktree `/Users/suzhe/ReBaseGuard-k5c11rd`,
branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD = authorization commit A =
`6bab71b95cd492956a688b062fe3547a5daf7389` (parent `e27c2ffdc55f745e372f0e896d6bedc42a57f341`).
`git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step
(later steps ran with `GIT_OPTIONAL_LOCKS=0`). `refs/c11rd/*` stayed empty, `<common>/c11rd_r1` was never
created, no grant or `config/` was created, and no `__pycache__` appeared in the namespace or in C7's code
directory. I never ran `--make-grant`, the frozen runner, the comparator's main or any C11R runner on the real
repository. Every grant, launcher and seal experiment ran in a scratch clone under my scratch directory, and
the one full launch there used a STUB runner.

## Summary

The authorization is acceptable. Suppose the grant is created exactly by the stated rule on top of the
preserved, accepted version of this review. Then a later, separately instructed execution round can launch
the ONE cell-306 D1/D2 execution safely and exactly as authorized, provided it satisfies the listed launch
preconditions, including P-10 (tmux), which is not met today.

* **Bindings.** The artifact binds the right lineage, and every value matches the freeze, the accepted
  qualification artifact and the live host. I checked each one myself:
  * freeze `ce5b8595`, qualification `e627d4ec`, accepted review `e27c2ffd`, launcher sha256 `81ccc048...`;
  * host, worktree, branch, interpreter, 227 runtime files, launch limits and caps;
  * target cell 306, D1/D2 only, `max_executions` 1.
* **The grant rule works.** I simulated the rule in a scratch clone. There I made R, ran the tool's own
  `--make-grant`, and committed G.
  * The grant bytes equal my independent `serialize(fill(template, A, blob, R, blob))`.
  * The frozen runner's `grant_problems` at G reports only the one path-bound item that a clone cannot
    satisfy (its canonical worktree). With that single field substituted by the clone's identity, it
    reports nothing.
  * At R and at A it refuses.
  * The qualified launcher's preflight at G reports only the path-bound and host-volatile items.
  * A full launch at G with a STUB runner consumed at G and sealed exactly `evidence/runs/` on top of G. A
    relaunch was then refused.
* **The A -> R -> G structure is sound, and G is necessarily the launch commit.** The frozen runner needs
  the review and the byte-identical grant at the commit it is given, so neither A nor R can work.
* **Evidence reproduces.** `--verify` gave 34/34 and `--self-test` gave 14/14. The self-test output is
  identical to the committed file, and the verify checks are identical too.
* **Leaks.** Both my own value-free scan and the frozen V18 detector find 0 hits, and their decoy controls
  work.
* **Governance is unchanged.**

I found no blocker. The non-blocking notes below concern the runbook's completeness and places where the
mechanical enforcement is weaker than the prose. The most important are:
* N-1: the identity of G is enforced by the authorization tool's checks, not by the launcher or runner;
* N-2: `--check-grant` is not a runbook step;
* N-3: the host must stay idle for the whole run, not only at launch.

## Findings per item

### 1. Bindings - PASS
* **Lineage, commits and parents.** A adds exactly the 6 files under `authorization_r1/` and nothing else.
  * `e27c2ffd` has parent `e627d4ec` and adds exactly the qualification review.
  * `e627d4ec` has parent `89330534`.
  * `ce5b8595`, `3c1eff11`, `3addf9d3`, `89330534`, `e627d4ec` and `e27c2ffd` are all ancestors of HEAD.
* **Freeze.** The JSON sha256 is `07118d30...` and the MD sha256 is `d2875e83...`, and both are
  byte-identical at `ce5b8595` and on disk.
  * `git diff ce5b8595 HEAD -- code protocol theory` is empty.
  * There are 8 code files, and every sha256 equals the freeze. So do the 8 document hashes, the 8 input
    blobs at HEAD and the C7 `c7_gaussian.py` sha256.
* **Qualification artifact.** Blob `1d79ad42` at `e627d4ec` and at HEAD, sha256 `36aa5c68...`, identical
  on disk.
  * The review has sha256 `be308335...` and is identical at `e27c2ffd`, at HEAD and on disk.
  * It has exactly one `QUALIFICATION_ACCEPTED` line and none rejected.
  * The launcher is byte-identical at `e627d4ec`, at HEAD and on disk: sha256 `81ccc048...`, blob
    `a169f1de`.
  * The qualification tool sha256 is `886679d1...`.
  * The authorization tool sha256 is `1ea8dbe6...`, as recorded.
  * The other reviews are unchanged: `dd4ccbda...`, `d95a2cb6...`, and the predecessor review.
* **Qualified bindings.** The artifact's `bindings` and `grant_template` equal the qualification artifact
  field for field:
  * host (`grant_host`), worktree, `launch_branch`, `interpreter`, `launch_limits`;
  * `science` and `resource_caps`: 43200 s, 2097152 kB, 5 workers;
  * `retry_semantics`, `seal_policy`, `attempt_semantics`;
  * the target block and its 4 sub-blocks.

  The frozen parameters equal the freeze's `frozen_parameters`. The recurrence and the D1/D2 formulas equal
  the freeze's `F_derivative_recurrence`, `P_execution_count` is 1, and the runtime binding is 227 files
  (binding sha256 `9b2a5035...`).
* **The live host.** The host and worktree identity, the interpreter (stub, running image, libpython) and
  all 227 runtime files re-hash equal. The verify rerun shows this, and so did the preflight in the clone.
* **Target and scope.** Cell 306 on `[680769/400000, 17885921/10000000]`, D1/D2 only, `max_executions`
  1. The scope and prohibitions exclude:
  * cells 307-309;
  * comparison before an execution review;
  * adoption, r6, and any change to r5.
* **Exactly one execution.** The freeze's P = 1, the grant's `max_executions` is 1, and there are the
  runner's permanent lock and R4, and the launcher's create-only consumed ref.
* **Entry.** Only the qualified launcher is permitted; the rejected launcher and direct runner invocation
  are not.
* **Launch commit.** The launch happens only at HEAD == G.
* **Launch command.** It uses the absolute framework interpreter. The qualification's `python3` form
  resolves to the same image, which L1 and the interpreter identity check.

### 2. The grant rule and the A -> R -> G structure - PASS (see N-1, N-2)
* **Template.** `grant_template_sha256` recomputes to `423a81d9...`.
  * The template contains every field of the freeze's `grant_schema_prospective`.
  * It adds `authorization`, `launcher`, `launch_branch`, `launch_rule` and `scope`. `grant_problems`
    ignores extra fields.
  * Only the four `authorization` fields are null, and the fill rule sets exactly those.
* **Simulation.** I made a scratch clone (`--shared`, the launch branch only, origin removed) and gave it a
  scratch test review at R.
  * **Refusals.**
    * `--make-grant` with R = A refused.
    * A second `--make-grant` refused: create-only, and the tree was no longer clean.
  * **The grant.**
    * `--make-grant --artifact-commit A --review-commit R` wrote the grant.
    * My independent fill produced identical bytes, with no null left.
    * I committed G.
  * **`--check-grant` at G.** Every lineage, byte and HEAD check was ok. It failed only on:
    * the frozen check's `canonical worktree differs from the grant's` (clone path);
    * the launcher `--preflight-only` items: worktree twice, plus `host not idle` (volatile).
  * **Frozen `grant_problems` in the clone.**

    | case | result |
    |---|---|
    | exact grant at G | only the worktree item |
    | worktree field substituted by the clone's identity, at G | `[]` |
    | same, at R | not byte-identical |
    | same, at A | review not present, and not byte-identical |
    | mutated in memory: cell 307, `max_executions` 2, D1 only, other freeze, rejected qualification, other host UUID | each refused with the right message |

  * **Launcher.**
    * `seal_safety_problems` at G is `[]`, and given R it is "HEAD is not the authorization review commit".
    * `load_qualified` through the grant equals the qualification artifact.
    * `commit_id_problems` is `[]`.
  * **Full launch at G (STUB runner, path-bound and volatile preflight items filtered).**
    * It consumed at G.
    * The stub ran.
    * It SEALED on the first attempt, with parent G.
    * The seal commit holds exactly the 4 files under `evidence/runs/` (lock, runs artifact, log, journal).
    * The index was refreshed and the namespace was clean.
    * A relaunch at G, and a launch at the seal commit, were refused (R4 on disk and in history, and the
      consumed ref).
    * A launch attempt at R, made before this launch, was refused before consumption.
* **Judgement.** The frozen runner requires the accepted review AND the byte-identical grant at the commit
  it is given. The grant names A and R. So G (R plus exactly the grant) is the only commit that can
  satisfy both the runner and the launcher's HEAD check. "G, not A, is the launch commit" is correct.
  * All security-relevant grant fields are fixed in the template, which this review covers.
  * The only filled-in values are A, the artifact blob at A, R and this review's blob. All four are
    deterministic.
  * The artifact is bound by blob, so everything in the artifact, including the preconditions and the
    runbook, is bound transitively.
  * Nothing important is left unbound. The one caveat is N-1.

### 3. Carried-forward launch conditions - PASS (see N-3 to N-6, N-8, N-9)
Every qualification-review condition is present:

| review note | carried as |
|---|---|
| N-1 | P-04 |
| N-2 | P-05 |
| N-3 | P-06 and runbook steps 2 and 5 |
| N-4 | P-10 and P-11 |
| N-5 | steps 6 and 7 |
| N-6 | P-14 |
| N-11 | step 8 |
| clean index, no lock | P-02 and P-03 |
| idle host, AC power, lid open | P-07 to P-09 |
| sleep prevention | P-12 |
| memory, disk, runtime | P-13 |

Each is either enforced by the qualified launcher, enforced by `--launch-preconditions`, or labelled as
operator procedure (P-06 during the run, P-11). The labels are honest.

**`--launch-preconditions`.** I read it. It is read-only.
* In the clone at G every item passed except P-10 (no tmux) and P-13 (the clone's worktree path).
* At R, P-01 and P-02/P-03 failed.
* A 12-hex id was refused.
* After the stub seal, P-01, P-02/P-03 and P-15 failed.
* On the real repository at A, P-01, P-07 (load) and P-10 failed, and all else was ok.

**Self-test.** 14/14, and my rerun is identical. The controls for line endings, other-worktree locks, the
log directory, a running git program and maintenance fire in both directions.

**Tmux positive control.** The self-test has none, so I supplied one:
* a process named `tmux` as an ancestor, with `TMUX` set, reports inside;
* either condition alone reports not inside.

**The runbook** uses the exact absolute interpreter, `-I -S -B`, and the right paths and order (cd, then
preconditions, then the launch in the same pane). N-5 (index refresh) and N-11 are covered. Gaps are in
N-2 to N-6.

### 4. Mechanical verification - PASS
* **`--verify`** into scratch: VERIFY PASS 34/34. The check keys and values are identical to the committed
  file. The differences are only:
  * HEAD: the committed run preceded A, at `e27c2ffd`;
  * the pending-file list and the pending-file seal-precondition entries;
  * the prospective-check commit prefix;
  * host-volatile load, memory and disk.
* **`--self-test`** into scratch: 14/14, byte-identical after normalisation.
* **My own checks:**
  * HEAD is A and the tree is clean.
  * The frozen hashes are unchanged (item 1).
  * `e627d4ec` and `e27c2ffd` are reachable and their artifacts are byte-identical.
  * There are no `refs/c11rd` and no `refs/replace`, the repository is not shallow, and there are no
    grafts and no stash.
  * No commit touches `evidence/runs`, `evidence/comparison`, `config`, the authorization review or the
    execution review in `log --all --reflog --full-history`, and none of those is on disk.
  * There is no live grant.
  * Local main is `c123b9bb8f15d17650545b3fce4aca8a6b61093b` and origin/main is
    `1cb453826313c189f0bdafd5b84120c1edb74da9`: distinct, and unchanged.
* **Configuration**, read in the launcher's environment (global and system configuration off):
  * no `core.autocrlf`, `core.safecrlf`, `core.eol`, `attributesFile`, `hooksPath`, `fsmonitor` or
    `sparseCheckout`;
  * no `config.worktree`;
  * no active hooks;
  * no `info/attributes`;
  * `check-attr -a` on the grant, review and seal paths is empty;
  * the global config has no maintenance section, and there is no XDG git config file.
* **Locks and processes.**
  * `<common>/c11rd_r1` is absent.
  * There is no `*.lock` in the common dir, in `refs/`, or in any of the 33 linked worktree git dirs.
  * No git process is running, and no fsmonitor daemon.
  * The ref format is `files`.
* **Ignore rules.** The grant and review paths are not ignored. The execution log matches `*.log`, which
  the seal handles with `add -f`.

### 5. The authorization tool - PASS (see N-7)
* **What it writes.**
  * In the repository it creates only the grant, and only in `--make-grant`. That mode runs after the
    lineage checks, requires HEAD == R and a clean tree, and uses `O_EXCL` after refusing an existing
    `config/`.
  * `--verify`, `--self-test`, `--compose` and `--check-grant --out` write only the output path they are
    given.
  * The self-test uses temporary repositories only.
* **What it never does.**
  * It never calls `update-ref` or `run_once`, and never starts the runner. Its only launcher call is
    `--preflight-only`, which creates nothing.
  * It computes no science. The R6 cover check is the frozen, value-free cover-completeness check that
    the launcher also runs.
  * It never opens the quarantine, the C11R comparison or REGISTRY_C2.

### 6. Leak freedom - PASS
* **My own scanner.** It uses only `c11rd_validate.ORIGINAL_PATTERN_SHA256` (17 hashes) and
  `c11rd_compare.value_patterns`/`token_prefixes`.
  * **Method.** Every numeric token and every maximal digit run is taken, including those inside hex
    identifiers. Its significant digits are placed at every decimal scale, then rendered as the plain form,
    every prefix of it, and `%.{4..9}g`. Each rendering is hashed and looked up in the frozen set.
  * **Coverage.** A's 6 files, all 67 namespace files, and the messages of every commit in
    `7375b9cd..HEAD`, A's included.
  * **Result.** 0 hits.
  * **Decoy controls.** Nine positive plants all fired: plain, scientific, per-mille, integer-coded,
    rounded, bare-point, percent, inside a hex identifier, and 6-digit. Four negatives stayed silent.
* **The frozen V18 detector.** 67 files, 0 hits, and its planted controls behaved as designed.
* **This review file.** I scanned it the same way: 0 hits.

### 7. Absence of target computation and governance - PASS
* The artifact says `target_D1_computed`, `target_D2_computed`, `target_runner_started` and
  `live_grant_exists` are all false.
* There is no consumed ref, run, seal, comparison or r6. Nothing outside the namespace changed since
  `7375b9cd`.
* In this review nothing was computed at a cell 306-309 drift. The only launches were in the scratch clone
  with a STUB.

## BLOCKERS

none

## NON-BLOCKING NOTES

**N-1. The identity of G is enforced by the authorization tool's checks, not by the launcher or runner.**
* **Evidence.** In the scratch clone I added a commit G2 after G.
  * `grant_problems(auth=G2)` returned `[]`, and the launcher's `seal_safety_problems(G2)` with HEAD = G2
    returned `[]`.
  * `--launch-preconditions` refused G2 on P-01 ("G adds exactly the grant").
* **Why it does not block.** A launch at a descendant still has every scientific and qualification
  binding re-checked (code, freeze, inputs, qualification, launcher blob at HEAD, grant bytes), so it would
  be the same execution with different provenance. It also needs the operator to skip runbook step 3.
* **Condition for the execution round.**
  * Run `--launch-preconditions` and `--check-grant` with the same G, and require both to pass
    (`--check-grant` apart from host-volatile items).
  * The execution review should verify three things: the consumed ref and the seal's parent are G; G
    adds exactly the grant; G's parent R adds exactly this review; and R's parent is A.

**N-2. `--check-grant` is named in `grant_rule.writer` but is not a runbook step.** It is the only
mechanical check before launch that:
* the grant bytes equal the rule;
* R is A's child and adds exactly the review.

Run it right after committing G, with `--out` to a file outside the repository, and keep the output.

**N-3. The host must stay idle for the whole run.** P-07 is a snapshot at launch. The run may last up to
the 12 h wall cap, and during this review other activity on this 8 GB host drove the 5-minute load above
20. Contention can push the run past the cap, which gives COMPLETED_NOT_CERTIFIED, and under this freeze
that is never retried. Step 5 should add: no other compute on the host, including other Claude sessions,
until SEALED or UNSEALED is printed.

**N-4. The seal-only recovery command the launcher prints uses a bare `python3`.**
* On this host the user's PATH resolves it to the framework 3.14, which I checked. `/usr/bin/python3` is
  3.9.6, however, and would fail.
* Run any recovery with the absolute interpreter:
  `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B <launcher> --authorization-review-commit <G> --seal-only`.

**N-5. Step 8 (QR2.N-11) has a dead end.** If the consumed ref exists after a REFUSE and there is neither
a runner log nor runs content, `--seal-only` answers "nothing to seal" (exit 5). Step 8 should then say:
stop; the execution is consumed and nothing ran; ask for a separately instructed recovery.

**N-6. The moved-branch recovery (QR2.N-5, second half) is deferred, not closed.** The runbook says to stop
and ask instead of giving exact commands. That is the conservative choice, and acceptable.

**N-7. `--check-grant` does not validate G before git sees it.**
* **Evidence.** `--authorization-commit=--output=<path>` reaches `git rev-list` and `git diff` as an
  option. In the clone I confirmed that `git rev-list ... --output=<file>` creates the file.
* **Scope.** The value is typed by the operator only; the launcher and `--launch-preconditions` do
  validate their ids.
* **Fix.** Validate the 40-hex id first.

**N-8. P-10 (tmux) is honest but unmet.**
* tmux is not installed, which I confirmed. The launch cannot proceed until it is installed.
* Install it before step 2. Homebrew's own git activity is outside the repository and outside the bound
  files.
* The check can be spoofed by a process named tmux. It is a safety aid, not a proof.
* Also keep the launcher's printed report, for example with tmux `remain-on-exit` or `pipe-pane` to a file
  outside the repository.

**N-9. Git clients and process names.**
* **Claude sessions run git.** The Claude app and Claude Code sessions run git in the main checkout
  `/Users/suzhe/ReBaseGuard`, which uses the same common dir. Per the qualification probes this is
  harmless to the private-index seal: a transient common-dir `index.lock` only makes the preflight or the
  gate refuse. It is still git activity under P-06, so idle those sessions.
* **The other-runner check matches any command line containing the runner's file name.** That includes a
  shell whose command text mentions it: my own first scratch launch was refused this way. This is safe,
  because the refusal comes before consumption, but it also blocks `--seal-only`. Avoid naming that file
  in any command running at the time.

**N-10. Wording.** MD section 3 says the launcher enforces the frozen caps through the qualification
artifact. In fact the frozen runner enforces them from the freeze file, which `grant_problems` binds; the
launcher uses only the rss cap in its accounting check. The committed VERIFY file was produced at
`e27c2ffd` with only the tool pending, as the artifact states. My rerun at A gives identical checks.

## Commands I ran
The real repository is `/Users/suzhe/ReBaseGuard-k5c11rd`. `<S>` is my scratch directory, and `P` is
`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`.
```
git status --porcelain --ignored --untracked-files=all | wc -l   (0 before/after every step); git for-each-ref refs/c11rd refs/replace
git show --stat HEAD; git log -1 --format=%B HEAD; git rev-parse HEAD HEAD^; git log --oneline -12; git worktree list
git rev-parse --is-shallow-repository / --show-ref-format / --git-dir --git-common-dir; git symbolic-ref HEAD; git stash list
git -C /Users/suzhe/ReBaseGuard rev-parse main origin/main; ls <common>/c11rd_r1 <common>/info <common>/hooks <worktree gitdir>
env -i <launcher SAFE_ENV> git config --show-origin --list; git check-attr -a -- <grant, review, seal paths>; git check-ignore -v --no-index <same>
git diff --name-only 7375b9cd HEAD (outside namespace: none); git log --all --reflog --full-history -- <lifecycle paths>
cat/sed/Read: authorization_r1/* (all), qualification review (all), launcher (all 940 lines), c11rd_runs.py (barrier, R0-R7,
  grant_problems, main), c11rd_compare.py (value_patterns, leak_hits, verify_seal), c11rd_validate.py (V18), c11rd_model.history_commits
P -I -S -B -c <compare artifact bindings with freeze and qualification artifact>
P -I -S -B <S>/hashcheck.py                      (hashes, blobs, parents, diffs, ancestry, lifecycle history)
P -I -S -B authorization_r1/code/c11rd_authorize.py --verify <S>/v.json       (VERIFY PASS 34/34; compared with committed)
TMPDIR=<S>/tmp P -I -S -B authorization_r1/code/c11rd_authorize.py --self-test <S>/s.json   (14/14; identical to committed)
P -I -S -B authorization_r1/code/c11rd_authorize.py --launch-preconditions --authorization-commit <A>   (NOT MET: P-01, P-07, P-10)
P -I -S -B authorization_r1/code/c11rd_authorize.py --check-grant --authorization-commit <A> --out <S>/cg_real.json   (FAIL, expected: no grant)
P -I -S -B qualification_r1q_r1/code/c11rd_launch.py --authorization-review-commit <A> --preflight-only | --seal-only   (REFUSE L2: no grant)
P -I -S -B <S>/my_leak_scan.py <A's files> | ns   (0 hits; decoys 9/9 fire, 4/4 silent); P -I -S -B -c <c11rd_validate.v18_no_original_values_anywhere()>
Scratch clone <S>/sim/repo (git clone --shared --single-branch --branch <launch branch>; origin removed; scratch identity):
  commit scratch R; clone's c11rd_authorize.py --make-grant (R=A refused; exact; second refused); independent fill comparison; commit G
  clone's --check-grant --authorization-commit G; --launch-preconditions at G, R, 12-hex id, and after the stub seal
  P -I -S -B <S>/sim/probe_grant.py   (grant_problems variants, launcher seal preconditions, descendant G2, then reset to G)
  bash <S>/sim/run_probe_launch.sh    (launch() with STUB runner: at R refused; at G SEALED; relaunch refused)
  fake ancestor named tmux + TMUX: tmux_state positive and negative controls; git rev-list --output probe (N-7)
ps (no git, fsmonitor, caffeinate or stray sleep processes afterwards); uptime; pmset -g batt; which -a python3
```
I never opened the C11R quarantine, `C11R_COMPARISON.json`, `REGISTRY_C2.json` or any original cell or
denominator artifact. I never recovered, echoed or passed the original values anywhere.
