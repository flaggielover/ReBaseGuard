# C11RD-R1 qualification review
QUALIFICATION_REJECTED

Reviewer: fresh, independent, read-only. Date 2026-09-26. Worktree `/Users/suzhe/ReBaseGuard-k5c11rd`,
branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD = qualification commit
`3addf9d3c72d9274813fb5e06486b633a50a133c` (parent `3c1eff11`, grandparent `ce5b8595`).
`git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step.
`refs/c11rd/*` stayed empty and no `.git/c11rd_r1/` directory was created.

In short: the freeze, the scientific object, the validation (29/29), leak freedom, host binding, history
hardening and the note dispositions all hold. I reproduced the qualification key for key, apart from
host-volatile fields. One defect in the new launcher blocks acceptance (B-1). Its automatic "immediate
seal" can fail after the one execution has run and been consumed. It fails on ordinary repository
states that the preflight does not check, and the result is then left unsealed. In one of these cases
the launcher reports it with the same `REFUSE:` prefix it uses when nothing ran.
The repair touches only the launcher and the qualification tool: no frozen file and no new freeze.

## Scope and what I ran

Read in full:
* the accepted R1 review `3c1eff11:review/C11RD_R1_PRE_EXECUTION_REVIEW.md`;
* `docs/C11RD_R1_QUALIFICATION.md`, the artifact, the checks JSON, `POST_WRITE_LEAK_SCAN.json`, the
  validation log and JSON;
* `qualification_r1/code/c11rd_launch.py` and `c11rd_qualify.py`, both in full;
* the frozen `code/c11rd_runs.py` in full;
* the frozen `code/c11rd_compare.py`: docstring, `verify_seal`, `run_once_problems` and `main`;
* `c11rd_kernel.Box`, `c11rd_certify.initial_boxes`, and the `point_box`/`kernel_at` call sites in
  `c11rd_validate.py`;
* the governance sections of `protocol/C11RD_FREEZE_R1.json`, and the repository and global git
  configuration.

Executed (outputs only under `<SCRATCH>` = `.../scratchpad/c11rd_review_q`):
* **Frozen validation** (`code/c11rd_validate.py`): 29/29 PASS.
* **Qualification tool**, with both disclosed values on stdin and `--write-artifact`: 10/10 PASS. The
  composed artifact equals the committed one key by key, except for host-volatile fields (see item 4).
* **My own broad leak scan**, with the values on stdin and 14/14 planted positive controls.
* **V18 hash-set equality check.**
* **The launcher on the real repository**, in `--preflight-only` mode with 40 zeros, under four
  environments.
* **Scratch-repository launcher probes** T1-T4, T9, T11, T12 and T14. They use the qualification tool's
  own sandbox and STUB runner.
* **A spawn/accounting probe and a UTF-8 probe** under the launcher's exact sanitized environment.
* **Host fact checks.**

What I did not do:
* compute anything at a cell 306-309 drift;
* run `c11rd_runs.py` in any mode, or the launcher without `--preflight-only` on the real repository;
* run the comparator's main, create a grant, a consumed ref or a commit in the real repository, or
  start any C11R runner;
* open the C11R quarantine, `C11R_COMPARISON.json`, `REGISTRY_C2.json` or any original cell or
  denominator artifact.

## Findings per item

### 1. Freeze identity — PASS
* The sha256 of `protocol/C11RD_FREEZE_R1.json` is `07118d30…`, and of the `.md` file `d2875e83…`.
  Both files have the same blobs at `ce5b8595`, `3c1eff11` and HEAD (`770b378d` and `63f4d71b`).
* All 8 code files equal the freeze's `code_sha256` and the artifact's `frozen_code_sha256`. `code/`
  holds exactly those 8 files.
* The 8 `document_sha256` entries are equal.
* All 8 input blobs are equal at HEAD and at `ce5b8595`. C7's `c7_gaussian.py` sha256 and blob equal
  the freeze.
* `git diff ce5b8595 3addf9d3` over `code/`, `protocol/`, `theory/`, the bound documents and the
  calibration file is empty.
* `3addf9d3` adds only 8 files. All of them are under `qualification_r1/`, `evidence/qualification_r1/`
  or `docs/C11RD_R1_QUALIFICATION.md`.

### 2. The accepted R1 review — PASS
* The review has blob `f568f9af` at both `3c1eff11` and HEAD, and sha256 `dd4ccbda…`.
* Its only verdict line is `READY_TO_QUALIFY` (line 2).
* `3c1eff11` added only that file, on top of `ce5b8595`.

### 3. Scientific identity — PASS
My reading of the freeze and of `c11rd_runs.certify_block`, plus the Q03 rerun, confirm every item:
* target cell 306 only, on [680769/400000, 17885921/10000000];
* the four sub-blocks tile the block exactly;
* 168 initial boxes;
* refinement: tolerances 1/100000, 1/20000 and 1/2000, `max_depth` 2, and the frozen splits;
* Taylor order 6 and 34 moment terms;
* the frozen float proposal;
* the recurrence and the D1/D2 formula texts, with `propagate` and `atom_values` equal to the formulas
  on 50 random rational instances;
* maximum aggregation (AST: two `max` calls, no `min`);
* the factor-2 rule;
* caps of 43,200 s, 2,097,152 KiB and 5 workers;
* the upper-closed band convention;
* the quarantine is blob-bound and read only after U0-U4 (AST order);
* V29 identity against `71495747`.

The artifact's `science` and `target` blocks are copied from the freeze. The new code lives outside
`code/`, so the frozen runner's barrier is unaffected.

### 4. Validation — PASS (29/29 reproduced)
* My run took 2 min 2 s. It differs from the committed `evidence/qualification_r1/validation` only in:
  * V18 `files_scanned`: 51 now against 46, because qualification evidence was written after that run;
  * V28's timing-dependent fields.
* `drifts_used` is [0, 1, 5/2, NT block], and `target_values_used` is false.
* My rerun of the qualification tool matches the committed artifact except for fields that change with
  each run, which is expected:
  * host-volatile values: disk, load, memory, `ps` seconds and clock drift;
  * the checks-file hash;
  * the validation output hash, which covers timings;
  * the file count of the broad scan (51 against 48).

### 5. Leak freedom — PASS
* **V18.** `value_patterns` of the two disclosed values, hashed, equals V18's 17-element set. V18 now
  scans 51 files with 0 hits.
* **Post-write scan.** `POST_WRITE_LEAK_SCAN.json` covers 50 files plus itself, which is the whole
  current namespace.
* **Q10 rerun.** 51 files and 7,985 rationals, 0 hits.
* **My own scan** covered the 51 files and the commit messages of all 5 namespace commits. It checked
  every plain, bare-point, scientific, integer-mantissa and rational token, also scaled by 10^-3 to
  10^3, for values within 1e-3 relative. It also checked leading significant-digit substrings of 4 or
  more digits, truncated and rounded, inside any digit run. All 14 planted positive controls fired.
  * There are no hits in any qualification-round file or commit message.
  * The only hits are in the two frozen non-target rehearsal JSONs, and they are identical in both.
    Both kinds sit inside long dyadic numerators of the non-target candidate coefficients:
    * one scaled near-match that agrees in fewer than 4 significant digits;
    * digit substrings that occur strictly inside long numerators, never at their start.
  * These are coincidences below the 4-significant-digit rendering rule, not renderings. The R1 review
    already reported the same kind. I give no positions, so that they cannot serve as a locator.
* Q10 as written is weaker than it claims; see N-4.

### 6. Host / runtime — PASS (authorization conditions in N-10 and N-15)
* **Identity.** The recorded identity equals the live host:
  * hostname `suzhedeMacBook.local` and IOPlatformUUID `57559A2E-…8AF0`;
  * `darwin`, Python 3.14.5, interpreter realpath `…/3.14/bin/python3.14` with sha256 `bd349815…`;
  * worktree `/Users/suzhe/ReBaseGuard-k5c11rd` with git common dir `/Users/suzhe/ReBaseGuard/.git`;
  * macOS 26.5.2 (25F84), arm64, 6 cores, 8 GiB;
  * git 2.50.1, and AC power now.
* **Q06 rerun.** 5 isolated workers, 500/500 `ps` reads, and the caffeinate assertion verified.
* **My probe under the launcher's exact environment** (`PATH`, `HOME`, `LANG=C`,
  `GIT_NO_REPLACE_OBJECTS`):
  * spawn gives 5 isolated workers, and `memory_status` is OK over 8 tree PIDs;
  * UTF-8 mode is on (`LC_CTYPE=C.UTF-8`), so the runner's `read_text()` calls are safe.
* **Idle host and sleep prevention** (the predecessor's N-7, the R1 review's N-11). They are enforced
  mechanically only in part: the launcher checks load ≤ 2.0 and the `caffeinate -i` assertion. Mains
  power and an open lid are prose only. During this review the 1-min load was 2.4-4.1, so an actual
  launch must wait for true idleness.

### 7. Git/history hardening — PASS
* **Real repository.**
  * No replace refs, no `refs/c11rd`, no grafts or shallow file, and it is not shallow.
  * No lifecycle path (runs, comparison, config, execution/authorization/qualification review) is on
    any ref, reflog or full history, or on disk.
  * The only namespace commits are `71495747`, `663f8fe7`, `ce5b8595`, `3c1eff11` and `3addf9d3`.
  * Nothing outside the namespace changed since `7375b9cd`. main is `c123b9bb` and origin/main
    `1cb45382`. There is no stash.
  * Hooks are samples only; `user.name` and `user.email` are repo-local; there is no `gpgsign`.
* **Q07 rerun.** PASS. Its corrupted commit-graph case does not discriminate (N-6).
* **Launcher L1.** I ran the preflight on the real repository:
  * with a hostile environment (`GIT_DIR`, `GIT_WORK_TREE`, `PYTHONPATH`, `GIT_CONFIG_*`, poisoned
    `PATH`): it reached `REFUSE L2: no grant`;
  * with a preset marker plus an extra variable: `REFUSE L1`.

### 8. Upper-closed convention binding — PASS
* It is bound by `E.band_ownership`, the frozen `c11rd_certify.py` hash (`owner_band`, `verify_cover`),
  the theory hash and runner guard R6.
* Q03's `owner_band` spot checks, `verify_cover` and V24 all pass.
* The erratum for the JSON `FORBIDDEN` list is accurate: the band clause is in the `.md` file only, at
  line 72.

### 9. Resource caps — PASS
* The frozen caps are unchanged.
* The launcher adds governance launch limits only (load, disk, available memory) and never touches the
  caps.
* RAM equals 4× the memory cap.

### 10. One-execution semantics and attempt semantics — PASS (see N-13)
* **The runner** checks, in order: grant, clean namespace, loaded modules, the `O_EXCL` permanent lock,
  the certifier, then the atomic write. R4 checks history, and nothing removes the lock.
* **The launcher** runs a preflight that creates nothing, then caffeinate, then the create-only ref,
  then exactly one run.
  * T12: a second `update-ref` on the ref is refused.
  * Q08: a second launch is refused.
  * Two concurrent launchers cannot both create the ref.
* **Attempt semantics** were verified by Q08, and by my own tests:
  * T3: SIGINT to the launcher gives CONSUMED_NO_RESULT, sealed, runner exit -2;
  * T9: SIGINT to the whole process group, as a terminal Ctrl-C sends it, gives the same.
* T14: a foreign process whose command line names `c11rd_runs.py` blocks the launch without consuming
  it.

### 11. Immediate seal — FAIL (B-1)
The seal path itself is correct in the normal case:
* it commits only `evidence/runs/`;
* the seal's parent is checked to be the start HEAD;
* it reads no value;
* the commit message carries the outcome class and exit code only;
* the frozen comparator's U1 accepts the extra log file.

It is not robust: see B-1.

### 12. Qualification path binding — PASS, with conditions
* T1 builds a grant whose qualification `review_path` points to an alternate file saying
  `QUALIFICATION_ACCEPTED`, while the canonical review says `QUALIFICATION_REJECTED`. The frozen
  `grant_problems` returns `[]`, which confirms the R1 review's N-8. The launcher refuses ("the grant's
  qualification paths are not the canonical ones").
* T4 uses another commit carrying the byte-identical freeze. The frozen check again returns `[]`, and
  the launcher refuses.
* Is the launcher-only rule adequate? Yes, as a two-layer defence:
  * the launcher refuses these grants;
  * an independent authorization review must accept the byte-identical grant.
* The frozen runner cannot know about the launcher, so direct invocation is excluded only by rule. That
  is adequate only if the authorization review explicitly checks the paths, the exact `freeze_commit`
  `ce5b8595`, and the launcher's hash at the authorization commit. Nothing checks commits made after
  the authorization review (N-1).
* Q08 never tests this path check (N-3).

### 13. Note dispositions — honest; none requires a new freeze

| note | class | my judgement |
|---|---|---|
| N-1 | QUALIFIED | Correct. Q09 does not instrument V07's 3 `kernel_at` calls, but V07 uses `global_cand` at band-0 points, so the claim holds; "every call ... 151 calls" overstates the evidence (N-5). |
| N-2 | HARDENED | Adequate. There are 36 rows at orders 0-2 on the lines s = 2, 3, 4. |
| N-3 | HARDENED | Adequate. The worst width/residual ratio is 7.2e-4. |
| N-4 | ACCEPTED_LIMITATION + rule | Honest. The governed path is unaffected. |
| N-5 | HARDENED | Adequate for the launcher path. Residuals: `HOME` passthrough (N-7) and direct invocation. |
| N-6 | HARDENED | The consumed ref is correct. The "automatic immediate seal" part is **not** adequate until B-1 is repaired. |
| N-7 | ACCEPTED_LIMITATION | Honest (inherent). |
| N-8 | HARDENED | Correct in code (T1/T4). Untested in Q08 (N-3). |
| N-9 | ACCEPTED_LIMITATION | Honest: wording only, and the errata are accurate. |
| N-10 | QUALIFIED | The namespace is clean (item 5). The tool's own control is vacuous (N-4). |
| N-11 | QUALIFIED | Honest. Fail-closed is kept. |
| N-12 | HARDENED | Adequate. The matrix passes. |
| N-13 | QUALIFIED | Adequate: each per-sub-block list is complete and geometrically identical. |

### 14. Absence of target computation — PASS
* There is no `evidence/runs`, lock, seal, comparison, `config/`, consumed ref or `.git/c11rd_r1`, on
  disk or in any history.
* Q09's N-13 check and runner guard R6 build `Box` objects on the target sub-blocks. Each is geometry
  plus affine s/θ/e Taylor models only, with no candidate, kernel, residual or magnitude. This is the
  same as R6, which the R1 review accepted.
* Everything I ran used drift 0, 1, 5/2 or the NT block, or a STUB runner.

### 15. Absence of authorization/grant — PASS
* There is no grant or authorization review on disk or in history.
* `c11rd_launch.py --authorization-review-commit 000…0 --preflight-only` prints
  `REFUSE L2: no grant at config/C11RD_GRANT.json` and exits 2.

## The launcher, adversarially

* **Environment (L1).** The re-exec keeps only `PATH`, `HOME`, `LANG` and `GIT_NO_REPLACE_OBJECTS`, and
  `launch()` replaces `os.environ`. The runner child gets `safe_env()`. Q08 shows the child sees only
  the safe keys plus `LC_CTYPE` and `__CF_USER_TEXT_ENCODING`. Gaps:
  * `HOME` passes through (N-7).
  * A preset marker skips the re-exec. The `-I -S -B` flags are then first checked only after the
    frozen import (N-2).
* **Preflight completeness.** The preflight covers host, interpreter, worktree, the frozen grant check,
  the exact freeze commit, the canonical paths, the runner hash, load, disk, memory, the process table,
  other runners, the consumed ref and a clean namespace. It does not cover:
  * the preconditions of its own seal (B-1);
  * its own identity, or HEAD = authorization commit (N-1);
  * AC power (N-10);
  * the runner's R0/R1 (other 7 files, C7) and R4 guards. A predictable runner refusal therefore
    consumes the authorization (N-9).
* **Signals.** SIGINT, SIGTERM and SIGHUP are forwarded while the runner lives (T3, T9, Q08). The
  handlers are restored before the seal (N-8).
* **Consumed-ref ordering.** It is correct: nothing is consumed on any preflight refusal, and every
  started run is consumed.
* **Seal correctness.** Correct when it succeeds; fragile otherwise (B-1).
* **Tests.** Q08 drives `launch()`, not `main()`, with a stub. It tests none of the following:
  * any seal failure;
  * the canonical-path refusal;
  * the disk, memory, process-table or no-grant refusals;
  * the L1 re-exec. I exercised L1 myself on the real repository.

## BLOCKERS

**B-1. The automatic seal can fail after the one execution has run and been consumed, and the preflight does not check the preconditions of its own seal.**

*Where.*
* `qualification_r1/code/c11rd_launch.py:158-206`: `preflight` checks `git status -- <namespace>` only
  (`:204`). It checks neither the repository-wide index nor the worktree's `index.lock`.
* `:293-298`: the launcher consumes the ref and runs before any seal precondition is known.
* `:264-284`, the seal:
  * `git add -f` at `:273` with `check=True` raises, through `git()` at `:101-102`, the message
    "REFUSE: git add -f failed: …";
  * a staged path outside `evidence/runs/` makes `:275-276` raise "SEAL REFUSED: unexpected staged
    paths".
* The frozen runner's R3 (`code/c11rd_runs.py:291-294`) also checks the namespace only.

*Evidence.* Scratch repositories, using the qualification tool's own `_launch_in_sandbox` and STUB
runner:
* **T2: one file staged outside the namespace before the launch.**
  * The preflight passes, the ref is consumed, and the stub runs as CERTIFIED.
  * The launcher reports "SEAL REFUSED: unexpected staged paths ['elsewhere/note.txt', …/C11RD_RUNS.json, …]".
  * The runs files are left staged but uncommitted.
* **T11: a stale `.git/index.lock` present at launch.**
  * The preflight passes, the ref is consumed, and the stub runs.
  * The launcher reports "REFUSE: git add -f failed: fatal: Unable to create '…/index.lock': File exists."
  * The artifact, lock and log are left untracked on disk.
* The real runner would also run in both states, because its R3 is namespace-only.

*Why it blocks authorization.*
* It is an enumerated blocker class: a target execution that leaves an unsealed result.
* It is reachable from ordinary, non-deliberate states that the preflight could detect before
  consuming:
  * a stray `git add`;
  * a lock left by a crashed git process (this repository's configuration carries VS Code and
    GitKraken traces: `vscode-merge-base` keys and `.git/gk`).
* The qualification presents the automatic immediate seal as the hardening of R1 note N-6. Its
  attempt-semantics table and artifact list every outcome as sealed, yet Q08 never exercises a seal
  failure.
* The failure after a completed, consumed, up-to-12-hour execution is reported with the same `REFUSE:`
  prefix as a preflight no-op. An operator could therefore believe nothing ran, and read or discard
  the unsealed artifact.

*Repair.* Only the launcher and the qualification tool change: no frozen file and no new freeze.
1. The preflight refuses unless:
   * the repository-wide index equals HEAD (`git diff --cached --quiet`);
   * no `index.lock` exists in the worktree's git dir;
   * (recommended) HEAD equals the authorization review commit.
2. The seal retries for a bounded time on `index.lock` contention.
3. Every failure after consumption prints one unambiguous message ("EXECUTION CONSUMED — RESULT
   UNSEALED — manual seal of exactly evidence/runs/ and nothing else") and never the preflight prefix.
   It leaves the index as it found it.
4. Q08 gains tests for these states.
5. The qualification is re-run, which records the new launcher hash, and a fresh qualification review
   follows.

## NON-BLOCKING NOTES

**N-1. No launcher self-check and no check of HEAD against the authorization commit.**
* Both the frozen runner and the launcher accept any commits after the authorization review commit.
* The launcher never compares its own sha256 with the artifact's `qualification_code_sha256`.
* So a launcher modified and committed after authorization would run unqualified.
* Fix: add both checks (fold into the B-1 repair).

**N-2. The L1 guard can be bypassed by a preset marker.** With `C11RD_LAUNCH_SANITIZED=1` preset and
only the safe keys, the re-exec is skipped and a non-isolated interpreter proceeds. I ran this; it
stopped at "no grant".
* `preflight()` imports the frozen runner before checking the `-I -S -B` flags.
* Without `-B`, that import would write `code/__pycache__` before the R0 barrier refuses, polluting the
  frozen directory. This is a deliberate path only.
* Fix: check `sys.flags` in `main()` before anything else.

**N-3. Q08 coverage gaps.** Q08 calls `launch()`, not `main()`: the re-exec, `load_qualified` and the
real command construction are untested. It has no tests of:
* the canonical-path refusal (the N-8 hardening; my T1 and T4 cover it);
* the no-grant, symlinked-grant, disk, memory or process-table refusals.

**N-4. Q10 is weaker than described.**
* Its "positive control" is arithmetic only (`c11rd_qualify.py:930-931`). It never runs the scanner on
  planted text.
* Its 1e-4 relative threshold is tighter than the 4-significant-digit rule. In general a 4-digit
  truncation can differ from the value by more than 1e-4 relative (up to 1e-3 over the leading digit).
* My scan (1e-3, prefixes, real controls) is clean. Fix the tool before reusing it.

**N-5. The N-1 evidence overstates its coverage.** Q09 instruments 7 tests but not V07. The claim
still holds by inspection.

**N-6. The Q07 commit-graph case does not discriminate.** Plain git with the corrupted graph also
returned both commits (return code 0, with a warning). So the test cannot fail and does not show that
the graph is "not consulted". The property rests on `core.commitGraph=false` in the code.

**N-7. `HOME` passes through the sanitizer.**
* `$HOME/.gitconfig` and `~/.config/git/*` apply to the launcher's, the runner's and the seal's git
  calls. Hooks, fsmonitor and signing all come from config.
* The current global config is benign.
* Consider `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`: the repo-local identity is
  enough.

**N-8. Signal and death windows.**
* The handlers are restored before `seal()`, so a second Ctrl-C or SIGTERM can interrupt the seal
  midway. Keep forwarding or ignoring signals through the seal.
* If the launcher dies (SIGKILL, jetsam, power loss), the runner keeps running with no seal and no sleep
  assertion.
* Document the recovery: a manual seal of exactly `evidence/runs/`, and nothing else first.

**N-9. The preflight does not pre-run the runner's R0/R1 (the other 7 files, the C7 directory) or R4
(lock/runs on disk or in history).** A foreseeable runner refusal then consumes the authorization
(fail-closed, but wasteful). Adding these calls is cheap.

**N-10. Mains power and an open lid are not enforced.**
* `pmset -g batt` gives a cheap AC check.
* `caffeinate -i` does not prevent a lid-close sleep. The cap clock `time.time()` keeps running
  through sleep, so a closed lid can turn the run into RESOURCE_CAP_WALL.

**N-11. The interpreter binding is weak.**
* The recorded interpreter sha256 is of the framework launcher stub `bin/python3.14` (about 136 KB).
  The interpreter itself (`Versions/3.14/Python`, about 14 MB) is unbound.
* The standard-library hashes are recorded but not re-checked at launch.
* Only deliberate tampering could exploit this.

**N-12. "N-7" names two different notes in the same artifact.**
* `authorization_requirements[2]` and doc section 3 mean the predecessor review's N-7, which is the R1
  review's N-11 (idle host and caffeinate).
* `note_dispositions` N-7 is "reachable history".
* Disambiguate before the authorization.

**N-13. The freeze's retry path is now closed.** Sealing the lock into history makes R4 refuse every
later run under this freeze, so the freeze's O host-fault retry path is closed. "A new execution needs
a new, independently reviewed authorization" should also say "and a new freeze or namespace".
This is the fail-closed direction.

**N-14. `load_qualified` passes an unvalidated commit id to git.** It runs `git show
<grant.qualification.commit>:<path>` before validating that id (`c11rd_launch.py:150-152`). A value
starting with `--` is parsed as a git option. Validate 40 hex characters first. This needs a
deliberately crafted grant.

**N-15. Conditions for a future authorization, after a repaired qualification.** The authorization
review should require all of the following:
* the grant has the canonical paths and `freeze_commit` = `ce5b8595` exactly;
* the launcher's sha256 at the authorization commit equals the artifact's;
* launch happens at HEAD = the authorization commit, with a clean index and no `index.lock`;
* no IDE or git client is attached to the repository;
* the host is idle, on AC power, with the lid open;
* the exact launch command:
  `python3 -I -S -B qualification_r1/code/c11rd_launch.py --authorization-review-commit <sha>`;
* any launcher exit without a printed RESULT JSON after the ref exists means: do nothing except a
  manual seal.

## Commands I ran

All commands ran from the worktree or `<SCRATCH>`. Writes went only to `<SCRATCH>`. The disclosed values
are shown as `<REDACTED>`.
```
git status; git rev-parse HEAD; git log --oneline -8; git show --stat 3addf9d3
git diff --stat 3c1eff11 3addf9d3; git diff --stat ce5b8595 3c1eff11; git diff --name-status ce5b8595 3addf9d3
git diff --stat ce5b8595 3addf9d3 -- <ns>/code <ns>/protocol <ns>/theory <bound docs> <ns>/evidence/calibration   (empty)
find <ns> -type f; cat -n <ns>/qualification_r1/code/c11rd_launch.py; cat -n <ns>/code/c11rd_runs.py
Read: review/C11RD_R1_PRE_EXECUTION_REVIEW.md, docs/C11RD_R1_QUALIFICATION.md, qualification_r1/code/c11rd_qualify.py (all)
sed/grep: c11rd_compare.py (docstring, verify_seal, run_once_problems, main), c11rd_kernel.Box, c11rd_certify.initial_boxes,
          c11rd_validate.py point_box/kernel_at call sites and V07; protocol/C11RD_FREEZE_R1.md (qualif/forbidden)
cat evidence/qualification_r1/*.json validation log; python3 -I -S -B -c <print checks JSON details / freeze governance sections>
shasum -a 256 qualification_r1/code/*.py evidence/qualification_r1/*.json evidence/qualification_r1/validation/* protocol/C11RD_FREEZE_R1.* review/*.md code/*.py
python3 -I -S -B - <freeze code/doc hashes; input blobs at HEAD and ce5b8595; C7 sha256; blob ids of freeze/review files at ce5b8595, 3c1eff11, HEAD>
python3 -I -S -B - <sanitized git: rev-list --all --reflog --full-history (namespace; lifecycle paths), for-each-ref refs/c11rd refs/replace,
                    rev-parse --is-shallow-repository / main origin/main HEAD, stash list, worktree list, branch --contains; grafts/shallow files>
cat /Users/suzhe/ReBaseGuard/.git/config ~/.gitconfig <CLT gitconfig>; ls .git/hooks .git; cat .gitignore; find -name .gitattributes
cd code && python3 -I -S -B c11rd_validate.py --out <SCRATCH>/review_validation.json          (29/29 PASS)
python3 -I -S -B - <compare with evidence/qualification_r1/validation/C11RD_VALIDATION.json modulo timings>
printf '<REDACTED>' | python3 -I -S -B qualification_r1/code/c11rd_qualify.py --out-dir <SCRATCH>/q --leak-values-from-stdin --write-artifact   (10/10 PASS)
python3 -I -S -B - <key-by-key diff of <SCRATCH>/q/C11RD_R1_QUALIFICATION.json vs the committed artifact>
printf '<REDACTED>' | python3 -I -S -B <SCRATCH>/my_leak_scan.py ; printf '<REDACTED>' | python3 -I -S -B <SCRATCH>/my_leak_detail.py <SCRATCH>/my_leak_scan.py
cd code && printf '<REDACTED>' | python3 -I -S -B -c <value_patterns hash set == V.ORIGINAL_PATTERN_SHA256; V.v18 rerun>
python3 -I -S -B qualification_r1/code/c11rd_launch.py --authorization-review-commit 000…0 --preflight-only                      (REFUSE L2: no grant; exit 2)
  - same under a hostile env (GIT_DIR, GIT_WORK_TREE, PYTHONPATH, GIT_CONFIG_*, poisoned PATH): first attempt resolved /usr/bin/python3 (3.9)
    and died at def time on `int | None` before doing anything; rerun with the framework python3: REFUSE L2: no grant
  - env C11RD_LAUNCH_SANITIZED=1 FOO=bar ...                                                                                     (REFUSE L1)
  - env -i C11RD_LAUNCH_SANITIZED=1 PATH HOME LANG=C <framework python3 without -I -S -B> ...                                    (REFUSE L2: no grant)
env -i PATH=/usr/bin:/bin HOME LANG=C GIT_NO_REPLACE_OBJECTS=1 python3 -I -S -B -c <utf8_mode, locale, read_text of freeze/artifact>
env -i PATH=/usr/bin:/bin HOME LANG=C GIT_NO_REPLACE_OBJECTS=1 python3 -I -S -B <SCRATCH>/spawn_probe.py   (5 isolated spawn workers; memory_status OK)
python3 -I -S -B <SCRATCH>/launcher_probe.py <SCRATCH>    (T1 non-canonical review path; T4 other freeze commit; T12 double consume;
                                                           T2 staged path outside namespace; T11 stale index.lock; T3 SIGINT; T9 SIGINT to process group;
                                                           T14 decoy process) -- scratch repos under <SCRATCH>, STUB runner only
hostname; ioreg -rd1 -c IOPlatformExpertDevice; sw_vers; sysctl -n hw.memsize hw.physicalcpu; git --version; pmset -g batt; uptime;
shasum -a 256 <framework>/bin/python3.14; ls -la <framework binaries>
git status --porcelain --ignored --untracked-files=all | wc -l   (0 after every step); git for-each-ref refs/c11rd | wc -l (0); ls .git/c11rd_r1 (absent)
grep -rlE '<REDACTED prefixes>' <SCRATCH>   (after redacting my own run log: no file)
printf '<REDACTED>' | python3 -I -S -B <SCRATCH>/scan_review.py ... <SCRATCH>/C11RD_R1_QUALIFICATION_REVIEW.md ; c11rd_compare.leak_hits on this review   (0 hits)
```

My scratch run log of the qualification tool at first echoed the `printf` command line through the
shell's `time` output; I redacted it. The same echo exists in the harness's background-task output
file, which lives under the session's tasks directory and not in the repository.
