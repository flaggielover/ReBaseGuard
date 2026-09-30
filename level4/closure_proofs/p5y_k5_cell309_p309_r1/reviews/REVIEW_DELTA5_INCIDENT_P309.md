# Incident-independence review of the FIFTH rev. 2c delta (A43–A47; conditions C2, D8, G8, G9, H7, H8), formal campaign p5y_k5_cell309_p309_r1
DELTA5_INDEPENDENCE_ACCEPTED

**Standard.** As before, temporal and parametric independence only. The conditions are I1–I7, in the section headed
"Conditions" below. I2 and I3 must be met before the freeze.

**Reviewer.** I am the independent incident-independence reviewer. I wrote:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`, with its follow-up 1;
* `reviews/REVIEW_DELTA3_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA4_INCIDENT_P309.md`.

I did not produce or coordinate the campaign.

**Brief.** `reviews/BRIEF_DELTA5_INCIDENT_P309.md`, committed at fd7da22f before it was issued (C5 respected).

**Reviewed state.**
* The code and governance are at fd7da22f. The tip 7c781743 adds a checkpoint record.
* Four ledger-only commits landed during the review: 6ca991ae, 223a2eeb, 2823e7bf and ac34a6e3. I cover the ledgers
  through ac34a6e3.
* I read committed bytes, plus two read-only checks outside the repository (§4): the ledger file of the coordinator's
  scratch clone, and the refs and hooks of both repositories.

**Written.** 2026-09-30, 11:14–11:25Z.

**Ledger** (reads and runs):
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/delta5review/D5_LEDGER.jsonl`.

---

## 0. Verdict in brief

**ACCEPTED, on temporal and parametric independence.**

* **Sources.** Every row comes from R4 follow-up 3: F4, with R4F3-C1, NF6, NF7, NF8 and NF9. That is an independent
  reviewer's reading of the code.
* **Scope.** The rows extend A40's host-git binding to three more places: `seal-only`, `execute`'s later git writes,
  and the guard's git. They also add controls and narrow the allowlist.
  * The driver diff is three `check_host_git(ctx)` calls plus comments.
  * The guard diff is `_HERMETIC_GIT` in its three git runners.
  * Nothing touches Stage 1a, 1b or 2, a budget, a gate, a decoy, the band or the outcome table.
  * The two ratified sites and the four A38 backstop pins are unchanged. I compared the ASTs at 7884122d and fd7da22f.
* **The rule and binding changes are outcome-neutral.**
  * They depend only on the host's git state.
  * Before the marker, a refusal consumes nothing.
  * After the marker, a refusal changes only the channel through which the evidence travels, and when it is sealed.
    It never changes the record.
* **Exposures.** From bfa18252 to ac34a6e3, 165 new execution-ledger rows and no new exposure rows.
  * Every row records zero target evaluations.
  * No row touches a tail cell, or a drift in the band or its mirror.
  * The 9 lines copied from the coordinator's scratch clone match the clone's own ledger byte for byte.
  * Nobody saw a 305–309 value.
* **Result-chasing component: LOW.**
* **What must happen before the freeze.**
  * The fifth delta's rule choices must be listed as liabilities, including one side effect of A44's pre-marker
    re-check: it can mask a CONTROL_FAILED record (I2).
  * The handoff must say that a refusal there spends the grant, and must fix in advance the git environment of the
    post-execution checks (I3).

**Delta-4 conditions.**
* H2–H4 are met at 8a380f19:
  * the F3 breakdown;
  * the fourth-delta rule choices and "result-chasing LOW";
  * `host_git_allowed_keys` = `REPO_CONFIG_ALLOWED`;
  * the horizon re-evaluation text.
* H5 is discharged by §4.
* H7 and H8 bring this delta here.
* H6 stands (I5).

---

## 1. Task 1: each row

| row | kind | source | direction for closure | basis target-free? |
|---|---|---|---|---|
| **A43** `seal-only` runs `check_host_git` right after `check_flags`, before its first git call | **binding** (A40 extended to the recovery path) | R4F3-C1 (F4) | fail-closed. The recovery is refused until the host is clean, and the evidence stays where it was. The record is unchanged | yes: host git state only |
| **A44** `execute` re-checks (a) after the historical control, before its first git write; (b) after the marker, inside the persist `try`, before the persist | **rule** | R4F3-C2 NF7 | (a) fail-closed and outcome-neutral, before the marker. (b) The evidence is kept, and no git write runs under a hook. The seal is delayed, never changed (§2) | yes |
| **A45** the guard's `_git`, `_git_bytes` and `_git_ok` set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null` after the `GIT_*` strip | **binding** | R4F3-C2 NF6 | toward a conclusive outcome. It removes a host-dependent guard refusal, both in the dry admission and in the guard's checks inside the Stage-1 jobs after the marker. It favours no particular outcome | yes |
| **A46** QC11 H01–H07 and V11; QC12 T10; D5 X01–X11 | controls | R4F3-C1, NF8 | none | yes. Sandboxes, TEST names, and a plain non-executable planted hook |
| **A47** `importlib` (code), `c2_d5_forecast` and `tct_rule` (tests), `diff-tree --diff-filter=`, and the redundant `--end-of-options` entries of `read-tree` and `archive` are removed | implementation | NF9 | narrows only | yes |

**The allowlist, compared by sets (5781b6da to fd7da22f).**
* Removed: exactly the five A47 entries.
* Two `reviewed_functions` are added, both tests: `host_git_flows` and `validate_flows`, with the `gitdir_write` and
  `ref_file_write` permits for the sandbox plantings.
* Rehashed: `run_execute` and the guard's three runners, and `validate_flows` in `ref_mutation_functions`.
* The QC11 `t7_exemptions` module hash is refreshed.
* The sites, the backstop pins, `env_keys`, the forbidden imports and the module-level exemptions are unchanged.

---

## 2. Task 2: A44

### After the marker

**Can the change of channel or exit code alter any mechanical outcome or its record?** No. It only delays the seal.

* In `after_marker`, the record is complete before the re-check:
  * the evaluation;
  * the `common` update, including `mechanical_outcome`;
  * `data = serialize(common)`.
* The re-check sits inside the persist `try`. A HOST_GIT refusal is caught there, and `persist_emergency` writes
  **the same bytes** to the emergency file.
* `seal-only` then:
  1. refuses until the hook or key is gone (A43);
  2. reads those bytes;
  3. binds them to the marker's grant commit;
  4. writes them through `_persist_pending`;
  5. seals them with `seal_message(status)` taken from the record.
* The record has no channel field. The exit code (4 instead of 0 or 5) is the process status, not part of the record.

**What does not change.**
* The only new failure mode is the one every persist failure already had: if the emergency write also fails, the run
  ends CONSUMED_UNRECORDED.
* Unsealed evidence in the git dir could be left unsealed by an operator. That is visible (a marker without a seal),
  cannot produce a closure claim, and allows no second evaluation. The same holds for every earlier UNSEALED case.
* Without A44(b), the same hook would have run inside `update-ref`.

QC11 H05 (a hook during the evaluation, then the emergency file, then `seal-only` refusing and finally sealing) passes
in the committed development evidence. That evidence is QC11 112/112, at the committed driver and test file.

### Before the marker

**Is the re-check outcome-neutral?** Yes.
* It depends only on the host's git configuration and hooks at that moment.
* It runs before the nonce and the marker, so no target evaluation has happened.
* The historical control's result is not observable at that point. I checked the driver: `historical_control` and
  `run_execute` write no ledger line and print nothing before the re-check. So no one can condition the host state on
  the control's result, except by an implausible race over a few statements.

**It can hide a CONTROL_FAILED seal.** If a hook or key appears **during** the control, and the control fails:
* the run ends `P309 REFUSED HOST_GIT` (exit 2) instead of a sealed CONTROL_FAILED (exit 3);
* the control's failure is then recorded nowhere;
* the grant is spent, because `execute` is never run twice and a refused grant commit is terminal without a new owner
  decision.

Both paths evaluate no target. So this cannot move anything toward closure, and no target information bears on it.
What is lost is route-validity information, a failing historical control, and only under host tampering during the
control. It must be disclosed (I2, I3).

Printing the control's `reproduces_C2_exactly` flag with an A44(a) refusal would remove the loss. That is optional, and
R4's call. If adopted it changes `run_execute`, so it is a new delta under H8.

---

## 3. Task 3: A45 and the verifier variant

**Does leaving the variant unchanged fit its role separation?** Yes.
* The variant belongs to the independent verifier author. The coordinator must not edit it. Changes go through a
  committed brief to its author, as A42 did.
* It is technically sufficient inside `execute`. There the variant runs only in the Stage-1 jobs:
  * `_spawn_job` starts them with `{**ENV, "PYTHONHASHSEED": "0"}`;
  * the variant's `_run_git` builds `dict(os.environ, …)` (verify line 234), so it inherits `GIT_CONFIG_NOSYSTEM` and
    `GIT_CONFIG_GLOBAL`;
  * T10 checks the spawn environment.

  Its official-mode grant-history `git log`, the call R4 showed `log.showSignature` corrupts, therefore runs
  hermetically.

**Outside `execute`, there is a small residual.**
* `code/p309_postexec.py` loads the variant in-process with `mode="review"`, under the operator's environment.
* Review mode skips the official-mode checks. Its git calls are plumbing and blob reads: `rev-parse`, `for-each-ref`,
  `symbolic-ref`, `rev-list`, and `show <rev>:<path>`. The known program-running settings do not change their output.

The residual still matters for independence in one respect. If a host setting ever made P10 fail, the choice to re-run
it in another environment would be made after the result is known. Fixing the post-execution environment in the
handoff removes that discretion without touching the variant (I3).

**A45's own direction.**
* The guard's git runs in the dry admission.
* It also runs inside the Stage-1 jobs, where the `GIT_*` strip had removed the driver's hermetic keys. That covers the
  per-call checks after the marker.
* So A45 removes a host-dependent post-marker refusal cause, which would have led to EXECUTION_INDETERMINATE or a
  silent SRK loss.

That is toward a conclusive outcome, and it favours no particular outcome.

---

## 4. Task 4: new exposures (from bfa18252 on)

**Exposure ledger.** There are no new rows. The last row is still the delta-2 E4 retrospective row.

**Execution ledger, bfa18252 to ac34a6e3.**
* 165 rows, appended only, with no line removed.
* Dated 08:57:30Z to 11:17:12Z.
* By class: 129 NONTARGET_DECOY, 28 GOVERNANCE, 8 SYNTHETIC.
* This includes the 10 rows of 49bf2e95, which I already covered in delta 4.

**Sources.**
* **The coordinator's pre-freeze dry runs (FE-11 labels).**
  * Part 4: QC08 decoy Stage 1a on the declared a2_h5, which passed; QC10's decoy review, stopped by a session time
    limit; and 108 SRK certification lines on the a2_h5 decoy.
  * The start of part 5: the research tests in the archive mirror, labelled "dry run (pre-freeze, development)"; QC05 on
    12 manufactured seeds; QC12; the placeholder scan; and QC14′ on manufactured inputs.
* **R4 follow-up 3.** 17 rows, matching its committed ledger extract.
* **R4 follow-up 4.** 5 rows, the re-confirmation runs.
* **The coordinator's development runs of this delta.**
  * 9 rows in a scratch clone (static check, QC11, D5 controls, guard, backstop and allowance tests), copied here, and
    one governance line naming them.
  * The same suites on this tree, at 11:07–11:11Z.
* **My delta-4 review** wrote no execution-ledger line. Its reads and runs are in its own committed ledger.

**Checks, done mechanically; I printed no interval.**
* `new_target_evaluations`, `target_informed_optimisation` and `target_equivalent_proxies` are 0 on every row.
* No `drifts` entry meets the band or its mirror.
* Of the 176 interval pairs in the text of the 148 rows up to 7c781743, none meets the band or its mirror; the same
  holds for the 17 later rows.
* All 176 of those intervals come from the 108 SRK certification lines. Every one lies at geometry (5, 1/2), inside
  the declared a2_h5 decoy cell widened by 2^-10.
* No row touches a cell 305–309.

**The scratch clone** (`scratchpad/p309dev5`). I read only its git metadata and its execution ledger.
* Its ledger is append-only over its base commit a3f49854.
* It holds exactly 9 extra lines.
* All 9 appear verbatim and contiguously in this repository's ledger at fd7da22f.
* The only break in UTC order in the window is where those 9 lines, dated 10:13–10:41Z, follow rows dated 10:52Z. The
  governance line discloses this.
* The clone and this repository both hold 0 refs under `refs/p5y-k5-cell309-p309-r1/` or `refs/p309-test/`, and no
  hooks.

**Answer.** On the ledgers' evidence, nobody saw a 305–309 value in this window.

---

## 5. Task 5: liabilities and texts

**The R4 follow-up-3 item is accurate.** It states:
* FREEZE_BLOCKED with D5 YES;
* F4 on `seal-only`;
* that no second evaluation was at risk;
* the resolution by A43–A47.

At the freeze it must be true that the resolution holds, and R4 follow-up 4's verdict must be cited (I5).

**`host_git` texts.** The grant rules and the proposal now name A43–A45. The proposal says what to do after a
post-marker HOST_GIT refusal: exit 4, remove the hook or key, then run `seal-only`. That is accurate. Two points are
missing (I3):
* **At the A44(a) re-check.** "Nothing consumed" is true, but the grant is then spent, as with any `execute` refusal,
  and a failing historical control is then not recorded.
* **The post-execution checks.** Their git environment is not fixed. The variant is not hermetic outside `execute`.

**Missing from the liabilities** (I2):
* the fifth delta's rule choices with direction;
* the CONTROL_FAILED masking;
* the variant's non-hermetic git outside `execute`;
* "fifth delta result-chasing component LOW".

**Note for R4 follow-up 4, not a condition.** The committed D5 evidence at fd7da22f (155/155, 08:56Z) predates this
delta. Its test, static-check and allowance hashes do not match fd7da22f, and it does not contain X01–X11. The commit
message says the run at this tree is in progress. The qualification's Q-D5 re-runs it anyway.

---

## Conditions

* **I1 (wording).** The fifth delta is accepted on **temporal and parametric independence only**. C1–C8, D1–D8,
  E1–E10, G1–G9 and H1–H8 continue. H5 is discharged for the committed rows through ac34a6e3.
* **I2 (liabilities; before the freeze).** Add to `DISCLOSED_LIABILITIES`:
  * **(a) the fifth-delta rule choices, with direction:**
    * A43: fail-closed. The recovery is refused until the host is clean, and the evidence is kept.
    * A44(a): fail-closed and outcome-neutral, before the marker. A refusal there spends the grant. If a hook or key
      appears during a failing historical control, that failure goes unrecorded: the HOST_GIT refusal replaces the
      CONTROL_FAILED record.
    * A44(b): after the marker, the evidence is kept and the seal is delayed (emergency file, exit 4, then `seal-only`
      once the host is clean). The record and the mechanical outcome are unchanged.
    * A45: toward a conclusive outcome. It removes a host-dependent guard refusal in the dry admission and in the
      Stage-1 jobs.
  * **(b)** The verifier variant is unchanged, by role separation. It is hermetic inside `execute`, through the jobs'
    `ENV`. Outside `execute` (`p309_postexec.py` review mode, the verifier's own runs) its git reads the host's
    configuration; in review mode it issues only plumbing and blob reads.
  * **(c)** "fifth delta result-chasing component LOW".
* **I3 (handoff texts; before the freeze).**
  * The grant-rules and proposal `host_git` texts state that an A44(a) refusal spends the grant, as any `execute`
    refusal does, and that a failing historical control is then not recorded.
  * The proposal's post-execution step fixes the environment in advance: run `code/p309_postexec.py` with
    `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null`. The variant's `_run_git` copies the environment, and the
    guard is already hermetic. That way no post-result choice of verification environment remains.
* **I4 (later ledger lines).** The next independence or qualification review covers the execution-ledger rows after
  ac34a6e3. That includes the rest of dry run part 5, R4 follow-up 4's runs, and the D5 run at this tree.
* **I5 (standing).** At the freeze:
  * the R4 follow-up-3 item's "resolved before the freeze" is true, and cites R4 follow-up 4's verdict;
  * the two sites keep the owner-ratified AST hashes;
  * the backstop keeps the A38 pins.
* **I6 (the git environment is binding).** The following are frozen as R4 follow-up 4 confirms them:
  * the driver's `ENV` and the job environment;
  * `REPO_CONFIG_ALLOWED`;
  * `check_host_git` and its four call sites (`run_execute` first and after the control, `after_marker`,
    `run_seal_only`), plus `validate-grant`'s use of it;
  * the guard's `_HERMETIC_GIT`.

  Any change after that confirmation is a new delta under C2.
* **I7 (later changes).** Any further rule, parameter or binding change after this review is a new delta under C2.

---

## 6. Reviewer disclosures

**Exposures.** None to any 305–309 value. I saw:
* code and governance text of the formal namespace;
* R4 follow-up 3's review;
* the verifier variant's git code;
* ledger rows, summarised mechanically by class and flags, with purpose texts shown only with their rationals masked
  or in grouped form;
* the scratch clone's execution ledger, compared byte-wise and not printed;
* top-level facts of the committed development evidence.

I opened no cell-307 or cell-308 campaign file, and no THEOREM_TCT. In the scratch clone I read only its ledger file
and git metadata.

**Executions.**
* Read-only `git` and `grep`, in this repository and in the scratch clone: logs, status, `for-each-ref` counts and
  hook counts.
* An in-memory `ast.dump` comparison of six driver definitions.
* Small read-only Python summaries in scratch that printed flags and counts.
* A byte-wise ledger comparison, using copies in my scratch directory.

I ran no evaluation, no kernel run and no git write.

**Writes.** This file only, plus scratch copies under my ledger's directory.

---
