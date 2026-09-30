# Independent pre-freeze review R4, follow-up 4 (R4F3-C3 focused re-confirmation and the D5 exception), formal campaign p5y_k5_cell309_p309_r1
FREEZE_APPROVED
D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES

**Reviewer.** R4, the author of `reviews/REVIEW_PREFREEZE_R4_P309.md`, `…_FOLLOWUP_P309.md`, `…_FOLLOWUP_2_P309.md`
and `…_FOLLOWUP_3_P309.md` (FREEZE_BLOCKED on F4; D5 YES). R4 wrote none of the reviewed code. R4 is not R1–R3, the
incident-independence reviewer, the delta reviewer or the verifier's author. Brief:
`reviews/BRIEF_PREFREEZE_R4_FOLLOWUP_4_P309.md` (committed before issue, fd7da22f).

**State reviewed.**
* The tree is **fd7da22f**, the commit that adds the brief. The pushed tip 7c781743 adds only the checkpoint-push
  record. Against my follow-up-3 scope (8a380f19), the code changes are in `code/p309_driver.py`,
  `code/p309_guard.py`, `code/p309_static_check.py`, `code/p309_self_audit.py`, the two handoff-text tools, the
  allowance, and `tests/test_p309_d5_exception.py` and `tests/test_p309_exactly_once.py`.
* I read the "Fifth delta" (A43–A47), addendum 2 of `governance/D5_SITE_BACKSTOP_REPORT_P309.md` and addendum 5 of the
  qualification-review brief.

---

## 1. Verdict in brief

**FREEZE_APPROVED**, with the conditions below. **`D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`.**

* **F4 is closed (R4F3-C1, A43).** `run_seal_only` runs `check_host_git(ctx)` right after `check_flags()`, before its
  first git call. The only git call before it is `production_context`'s `symbolic-ref -q HEAD`, a read that runs no
  configured program under the hermetic `ENV` — the same as in `execute`.
* **The recommended items are adopted and correct:** the repeated checks in `execute` (A44), the hermetic guard git
  (A45), the controls H01–H07, V11, T10 and X01–X11 (A46), and the five narrowed allowlist entries (A47).
* **Nothing touches a ref-mutation site.** The two sites keep the owner-ratified hashes and the backstop keeps the A38
  pins (recomputed, §5).

**Runs at this tree** (`-I -S -B`):

| suite | result |
|---|---|
| D5 controls (X01–X11, my N/K/T7/T8/R mutants, M01–M15) | **166/166** |
| backstop controls | **27/27** |
| QC11 (incl. H01–H07, V10, V11) | **112/112** |
| QC12 static T1–T10 (independent) | **10/10 PASS** |
| my new T10 mutants Y01–Y07 (static only) | 3/7 rejected (§3) |

**One non-blocking finding (F5): T10 checks shape, not behaviour.** Four of my seven new static mutants pass the scan
and T1–T10: a write reached through a local alias before the post-marker check, a seal-only check shadowed by a local,
a neutered `check_host_git` body, and `ENV` made non-hermetic by a later module-level statement. The genuine tree
contains none of these (I read all three call sites, `check_host_git`'s body, `ENV` and the guard's runners). I do not
block on it. The binding concerns a host-configured program running during git calls, not the D5 sites or the
exactly-once guarantees. The frozen driver and guard hashes pin the code after the freeze, and the window between this
confirmation and the freeze is closed by a standing condition that records the binding's AST hashes (R4F4-C1).
Pinning them in the allowance, as A38 did for the backstop, is recommended but not required (R4F4-C2).

---

## 2. Task 1: R4F3-C1 (A43)

`run_seal_only` now reads:
1. `_MODE["mode"] = "seal-only"`;
2. `ctx = ctx or production_context()` — `git symbolic-ref -q HEAD` through the driver's `git()`, with the hermetic
   `ENV`;
3. `check_flags()`;
4. `check_host_git(ctx)`;
5. then the signal setup, `check_branch`, the `rev-parse` of the marker and pending ref, the emergency branch
   (`_persist_pending`), and the seal.

**Does anything in `seal-only` still reach git before the check?** Only step 2. `symbolic-ref` reads `HEAD`; it runs no
hook, and under `GIT_CONFIG_NOSYSTEM` / `GIT_CONFIG_GLOBAL=/dev/null` no system or global program. A repository-local
key such as `core.fsmonitor` affects index refreshes, which `symbolic-ref` does not do. `execute` has the same order.
Accepted.

QC11 H06 and H07 plant a hook and a disallowed key (`core.hooksPath`) on persisted, unsealed evidence. `seal-only`
refuses with nothing written, and seals once each is removed. Both pass.

---

## 3. Task 2: A44–A47, and new mutants against T10

**A44, the repeated checks in `execute`.**
* **(a) Before the first later write.** A top-level `check_host_git(ctx)` now sits after the historical control and
  `common`, before the CONTROL_FAILED seal and before the run nonce and the marker. Between the first check (right
  after `check_flags`) and this one, `execute` makes no git write. Its only git calls there are reads and a
  `status --porcelain` with `GIT_OPTIONAL_LOCKS=0`, which writes no index. A refusal here raises before the marker:
  exit 2, nothing consumed. H03 and H04 cover it.
* **(b) After the marker.** In `after_marker`, `check_host_git(ctx)` is the first statement of the try that holds the
  persist.
  * A `Refusal` is caught by the `except BaseException`, and `persist_emergency` writes the evidence. That is a Python
    file write into the git dir; its only git call is the `rev-parse` of the git dir, a read. The run then returns 4
    (UNSEALED).
  * `seal-only` then refuses until the host is clean (A43). After that, its emergency branch requires the marker and
    the grant, persists through the ratified `_persist_pending`, and seals.
  * H05 covers the whole path: a hook appears during the evaluation, the evidence goes to the emergency file with exit
    4, `seal-only` refuses while the hook exists, and seals once it is removed.
* **What remains.** Between the persist and the seal, no re-check runs. The two statements follow each other directly,
  so the window is negligible.

**A45, the hermetic guard.**
* `_git`, `_git_bytes` and `_git_ok` strip `GIT_*` and then `env.update(_HERMETIC_GIT)`, so the guard no longer reads
  the host's `~/.gitconfig`. That closes my NF6 case: a global `log.showSignature` would have corrupted check 4's
  one-commit count.
* The three runners remain hash-pinned `reviewed_functions`. My Y07 (rebinding `env` after the update) is rejected by
  the scan through that pin.

**The verifier-variant reasoning is correct.** Inside `execute`, the variant runs only in the Stage-1 jobs.
`_spawn_job` starts them with `env={**ENV, "PYTHONHASHSEED": "0"}`, and the variant's `_run_git` builds its environment
from `os.environ`, which in the job is that hermetic dict. Outside `execute`, the variant's review mode (post-execution
P10) runs reads only: `rev-list`, blob `show <rev>:<path>`, `for-each-ref`, `rev-parse`, `merge-base` and
`diff-tree --name-only`. None of these prints signatures or runs a configured program, and the variant writes no ref.
T10 checks the spawn environment (X08).

**A46, the controls.**
* H01–H07 and V11 exercise every refusal point with a planted hook, which is a plain non-executable file that git never
  runs, or a disallowed key. `check_host_git` refuses any non-`.sample` file in the hooks directory whether or not it is
  executable, which is stricter than git. All pass (§4).
* X01–X11 are counted as passing only when T10 itself fails, not merely the scanner's hash pins. All pass (§4).
* NF8 is discharged.

**A47, the narrowing.** I checked the allowance:
* `importlib` is gone from `import_policy.allowed.code`;
* `c2_d5_forecast` and `tct_rule` are gone from `allowed.tests`;
* `diff-tree` takes `--name-only`, `--no-commit-id` and `-r` only;
* `read-tree` and `archive` take no listed options (`--end-of-options` is still accepted as a terminator).

The genuine scan passes.

**New adversarial mutants against T10** (`scratchpad/r4/d5_mutants6.py`). Each was planted in a temporary copy, only
parsed, never executed, and deleted.

| id | change (in a temporary copy) | scan | static | rejected? |
|---|---|---|---|---|
| Y00 | genuine | PASS | all pass | — |
| Y01 | `run_seal_only`: `check_host_git = lambda c: None` just before the check | PASS | all pass | **no** |
| Y02 | `check_host_git`: `return` as its first statement | PASS | all pass | **no** |
| Y03 | `after_marker`: `_p = persist; _p(ctx, data)` before the try that holds the check | PASS | all pass | **no** |
| Y04 | `run_seal_only`: `_s = seal_blob; _s(...)` before the check | PASS | T10 fails (`run_seal_only_host_git_first`) | yes |
| Y05 | `production_context` given a git write | FAIL (GIT_OPTION_FORBIDDEN) | T5 | yes |
| Y06 | module-level `ENV.pop("GIT_CONFIG_GLOBAL")` after the `ENV` literal | PASS | all pass | **no** |
| Y07 | guard `_git`: `env = {**env, **os.environ}` after the hermetic update | FAIL (ENV_UNLISTED, RUNNER_UNREVIEWED, …) | T5 | yes |

**F5: T10 can be satisfied by code that still writes before a check (Y03) or that disables the check (Y01, Y02,
Y06).** Four facts explain it:
* T10 matches writers by name (`WRITERS`), so a local alias hides a write.
* It recognises the check by the exact text `check_host_git(ctx)`, so a local rebinding of the name defeats it.
* It never inspects `check_host_git`'s body.
* It reads `ENV` only from the dict literal, not from later statements.

`run_execute` and the guard's runners are protected indirectly, because the scan hash-pins them as `reviewed_functions`
(hence Y07). `run_seal_only`, `after_marker`, `check_host_git`, `ENV` and `REPO_CONFIG_ALLOWED` are not pinned.

This is the same shape-versus-behaviour limit I found in the old T8. I do not block on it:
* the genuine tree has none of these constructs;
* the binding's failure mode is a host-configured program during a git call on the owner's host, not a site or an
  exactly-once breach;
* after the freeze, the manifest and the grant pin the driver's and guard's bytes;
* the window before the freeze is closed by R4F4-C1, which records the binding's AST hashes at this tree.

R4F4-C2 recommends the mechanical fix.

---

## 4. Task 3: R4F3-C3 runs

All runs used `python3 -I -S -B` and `P309_EVIDENCE_DIR=scratchpad/r4/evidence4`. Test modules ran unchanged through
my wrapper `scratchpad/r4/r4c4_run.py`, which only redirects `SCRATCH` into `scratchpad/r4` and includes the new
`host_git_flows`. The QC11 directory `scratchpad/qc11_sandboxes` was not used. Sandboxes were light repositories with
TEST names only, and all were deleted.

| run | result | evidence |
|---|---|---|
| D5 controls: X01–X11, N01–N20, K01–K04, T7a–T7d, T8a–T8c, R01–R23, M01–M15 and the positive controls | **166/166** | `R4C5_d5.json`, `run6_d5.log` |
| backstop controls | **27/27** | `R4C5_backstop.json` |
| QC11, all seven flow groups | **112/112**: H01–H07, V01–V11 and Z pass | `R4C5_qc11.json` |
| QC12 static T1–T10 (independent) | **10/10 PASS** | `run6_static.log` |
| Y01–Y07 (static) | 3/7 rejected | `run6_ymutants.log` |
| AST hashes (sites, backstop, host-git binding) | §5 | `run6_hashes.log` |
| git verbs reachable between execute's two checks | reads only: diff-tree, for-each-ref, log, ls-tree, rev-list, rev-parse, show, status, var | `run6_writes.log` |

The counts match the coordinator's dev results (QC11 112 flows; T1–T10 pass).

---

## 5. Task 4: R4F3-C4

I recomputed the hashes at fd7da22f with `p309_scan.ast_sha`:
* **The ratified sites:** `_arm_marker` `1ee764b7…`, `_persist_pending` `13ee3ec3…`. Both are unchanged and equal the
  owner-ratified values.
* **The A38 backstop pins:** `_assert_execute_context` `c8a2fb51…`, `_site_backstop` `80d206ad…`,
  `_require_own_run_nonce` `23f3021d…`, `_SITE_CODES` `696a6102…`. All are unchanged and T8 passes.
* **The host-git binding at this tree** (recorded for R4F4-C1):

| file | object | AST sha256 |
|---|---|---|
| `code/p309_driver.py` | `check_host_git` | `4110bb9d9d864a3ada3c8e691a8ffd01f82bfebb5b5edc7cf763800669e95053` |
| `code/p309_driver.py` | `run_seal_only` | `159262fc99300d72b4edfff705b39682ea5f647691487e3e8e0141ba2ae73dbc` |
| `code/p309_driver.py` | `after_marker` | `cf36c8dd8a0fda1bf1146e79b0fb6aaa625a1af3404380415179ed4b0ecab333` |
| `code/p309_driver.py` | `run_execute` | `3eab4185400556f553c0cfd8eb395c07c60875107332bdfbd7c889bbce91a918` |
| `code/p309_driver.py` | `ENV` (statement) | `6a6a1821467cc112fcc28269c8763bf5c2da6650c6f0521015895fdd50946fa5` |
| `code/p309_driver.py` | `REPO_CONFIG_ALLOWED` (statement) | `2530ba04a0b6d3f5b37a26f19c9c1a054cfa8ab4cd6f507e1ea1048efff3c229` |
| `code/p309_guard.py` | `_HERMETIC_GIT` (statement) | `3bfe879eefdb43b977a3e87e5ef9b927acc0b6fc19e9594f18993cd14b2cdd1d` |
| `code/p309_guard.py` | `_git` | `654e71dd8ff38c63741b822aa7ae994f075469569d7d02f92312d6f6a494546d` |
| `code/p309_guard.py` | `_git_bytes` | `c8af7037024be14427f311e603d87bec54c14bc98108e758d0403926d4847668` |
| `code/p309_guard.py` | `_git_ok` | `b4341f45d6d741c5ff04c0ca51c2aae03f465af627a1eb9cc3054583a0255e05` |

The genuine driver has no other statement that mutates `ENV` and no rebinding of `check_host_git`.

---

## 6. Task 5: readiness

Nothing else blocks the freeze from my side:
* B1–B8, F1, F2, F3 and F4 are closed;
* the D5 exception is limited to the two ratified sites;
* the controls and runs pass.

The handoff texts are accurate for this code:
* The proposal's `host_git` text names A43–A45 and says what to do after a post-marker `HOST_GIT` refusal: exit 4,
  remove the hook or key, then `seal-only`.
* The D5 report's addendum 2 states that after the marker "no git write runs under a hook". That is true for the
  emergency path, which is a Python file write, and for the persist. The negligible window between persist and seal is
  the one noted in §3.

A43–A45 go to the delta reviewer as binding changes (C2, G9, H7, H8). This review does not replace that. The
execution-ledger rows of my runs are for the next independence or qualification review (H5).

---

## Conditions

* **R4F4-C1 (standing, at the freeze).**
  * The two sites keep the owner-ratified AST hashes (`_arm_marker` `1ee764b7…`, `_persist_pending` `13ee3ec3…`).
  * The backstop keeps the A38 pins (`c8a2fb51…`, `80d206ad…`, `23f3021d…`, `696a6102…`).
  * The host-git binding keeps the AST sha256 values recorded in §5 of this review, computed at fd7da22f:
    * `check_host_git` `4110bb9d9d864a3ada3c8e691a8ffd01f82bfebb5b5edc7cf763800669e95053`;
    * `run_seal_only` `159262fc99300d72b4edfff705b39682ea5f647691487e3e8e0141ba2ae73dbc`;
    * `after_marker` `cf36c8dd8a0fda1bf1146e79b0fb6aaa625a1af3404380415179ed4b0ecab333`;
    * `run_execute` `3eab4185400556f553c0cfd8eb395c07c60875107332bdfbd7c889bbce91a918`;
    * the `ENV` statement `6a6a1821467cc112fcc28269c8763bf5c2da6650c6f0521015895fdd50946fa5`;
    * the `REPO_CONFIG_ALLOWED` statement `2530ba04a0b6d3f5b37a26f19c9c1a054cfa8ab4cd6f507e1ea1048efff3c229`;
    * in the guard: the `_HERMETIC_GIT` statement `3bfe879eefdb43b977a3e87e5ef9b927acc0b6fc19e9594f18993cd14b2cdd1d`,
      `_git` `654e71dd8ff38c63741b822aa7ae994f075469569d7d02f92312d6f6a494546d`, `_git_bytes`
      `c8af7037024be14427f311e603d87bec54c14bc98108e758d0403926d4847668` and `_git_ok`
      `b4341f45d6d741c5ff04c0ca51c2aae03f465af627a1eb9cc3054583a0255e05`.
  * The qualification reviewer recomputes them with `p309_scan.ast_sha`. Any difference is a new delta under H7/H8 and
    needs a focused confirmation.
* **R4F4-C2 (recommended, not required for the freeze; F5).** Make T10 an equality check, as A38 did for T8, by
  pinning the R4F4-C1 hashes in the allowance. Alternatively, extend T10 to:
  * resolve local aliases and rebindings of `WRITERS` functions and of `check_host_git`;
  * reject any module-level mutation of `ENV`;
  * check `check_host_git`'s body.

  Then add Y01, Y02, Y03 and Y06 (`scratchpad/r4/d5_mutants6.py`) as D5 controls. If adopted before the freeze, it is
  a new delta (H8) with its own focused confirmation. R4F4-C1 already gives the same assurance at the freeze.
* **R4F4-C3 (standing).** QC12 T1–T10, the D5 controls (including X01–X11 and my N, K, T7, T8, R and M01–M15 mutants),
  the backstop controls and QC11 (including H01–H07, V10 and V11) pass at the frozen tree in the qualification run.

---

## 7. Disclosures

**Reads.**
* FNS files and git metadata.
* The fd7da22f diff against 8a380f19.
* `governance/P309_REV2C_AMENDMENTS.md` (Fifth delta).
* The `D5_SITE_BACKSTOP_REPORT` addendum 2 and the qualification-review brief addendum 5.
* `code/p309_driver.py`, `code/p309_guard.py`, `code/p309_static_check.py`, `code/make_proposed_authorization.py`,
  the allowance, and the D5 and QC11 test files.
* No consumer code, no target input and no 305–309 value. I did not open THEOREM_TCT.md.

**Indirect reads by the test code I ran.** QC11's integration flows verify the committed TEST-band decoy certificates in
review mode and compose the a2_h5 decoys with manufactured Stage-1b records. No cover-cell entry and no campaign results
file is read, and nothing was displayed.

**Executions.** All carry notes prefixed "R4 reviewer:" and `new_target_evaluations` 0, on 2026-09-30. The exact lines
are in `scratchpad/r4/evidence4/R4_FOLLOWUP4_EXEC_LEDGER.jsonl`.

| UTC | what | class |
|---|---|---|
| 11:15:55 | D5 controls, 166/166 | GOVERNANCE |
| 11:15:58 | backstop controls, 27/27 | SYNTHETIC |
| 11:16:00 | QC11, 112/112 | NONTARGET_DECOY |
| 11:16:03 | QC12 static T1–T10 (independent) | GOVERNANCE |
| 11:16:19 | Y01–Y07 mutants against T10 (static) | GOVERNANCE |
| 11:19:36 | AST hashes of the sites, the backstop and the host-git binding (read-only) | GOVERNANCE |
| 11:33:50 | git verbs reachable between execute's two host-git checks (read-only AST walk) | GOVERNANCE |

Results are in `scratchpad/r4/evidence4/R4C5_*.json` and `scratchpad/r4/run6_*.log`, where `scratchpad/r4` is
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r4`.

**How the executions were contained.**
* Sandboxes were light repositories under `scratchpad/r4`, with TEST names only, never pushed, and deleted. The fixed
  QC11 directory `scratchpad/qc11_sandboxes` was not touched.
* Mutant copies were parsed only, never imported or executed, and deleted.

**What was never done.**
* `execute`, `seal-only` and `validate-grant` were never run against this repository.
* The Y mutants were never executed.
* No ref was created, armed or consumed under `refs/p5y-k5-cell309-p309-r1/` anywhere. There are 0 such refs here and
  0 `refs/p309-test/` refs here, checked after all runs.
* The production grant path was never written.
* No git write was made.
* No kernel ran in [6/5, 13/5] or its mirror.
* Nothing was evaluated for cells 305–309.

**Writes.** This file only, plus my ledger lines through `p309_env`, and scratch files under `scratchpad/r4`.

NEW Γ309 TARGET EVALUATIONS = 0.
