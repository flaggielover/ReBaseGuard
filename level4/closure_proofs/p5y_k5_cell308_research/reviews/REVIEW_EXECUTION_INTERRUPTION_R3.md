# R3 re-check of erratum E1 to addendum A1 (reviewer reviewINT, resumed; repairs R1 and R2 only)
DELTA_ACCEPTED

Erratum E1 carries repairs R1 and R2 exactly. It quotes the two replaced passages of A1 exactly, changes nothing else
and adds no new claim. A1 and the original assessment are byte-unchanged. I re-verified the post-reboot object
accounting by id and type.

**Consequence.** The recovery assessment is now accepted: the original (`8b64d989`) as corrected by addendum A1
(`e681d16f`) and erratum E1 (`c5f7c857`). In the terms of my first review, the corrected record is
RECOVERY_ASSESSMENT_ACCEPTED, and conditions C4–C6 bind the next steps.

## 0. Basis

* **Documents read.**
  * E1: `audit/EXECUTION_INTERRUPTION_ASSESSMENT_ADDENDUM_A1_ERRATUM_E1.md`, research commit `c5f7c857`.
  * A1, the original assessment, and my delta review (`0b9020af`).
* **Read-only.**
  * Git reads in the formal worktree ran with `GIT_OPTIONAL_LOCKS=0`, and nothing was written there.
  * No ref, index or object was written, and no driver mode was run.
  * I read no content of any post-marker object.
* **No target computation.** Nothing was computed for cells 305–309 or the band.

## 1. The quotes are exact: PASS

The text was compared after whitespace normalisation, to allow for line wrapping.

* **R1.** The quoted sentence "A SIGTERM-class termination of the app's subprocesses therefore killed `caffeinate`
  and left the driver and the workers running." occurs in A1 exactly once.
* **R2.** The quoted passage "**After the reboot:** the only objects written are those of the research commit
  `8b64d989` that carried the assessment (12 objects; type- and size-accounted by the review). None of them is a
  result object." occurs in A1 exactly once.

## 2. The replacements equal R1 and R2: PASS

After the same normalisation, both replacement texts are identical to the wording given in the delta review's §5.

## 3. Nothing else changed, and no new claim: PASS WITH NOTE

* **E1's other sentences are procedural or already verified.**
  * A1 and the original assessment stay unchanged.
  * A1 as corrected prevails.
  * No fixed count is given.
  * "No object was written between the marker and the reboot" is unchanged. It is re-verified in §5.
  * The "Unchanged" list matches the accepted A1: A–E, INDETERMINATE, count 1, the status lines, and the C3 ledger
    line.
  * The delta review is cited as `0b9020af` with sha256 `3c48babf…b5a220`. That matches the committed bytes and the
    worktree bytes.
* **The commit touches nothing else in the record.** Commit `c5f7c857` adds only E1, brief 26 and one row of the
  brief index. It modifies no existing audit, review or ledger file.
* **Note N1.** "E1 replaces exactly two sentences of A1" is imprecise: R2 replaces a two-sentence bullet, so E1
  replaces three sentences in two places. The quoted passages are exact, so this has no effect.

## 4. A1 and the original assessment are byte-unchanged: PASS

Each file has one blob id at `e681d16f`, `0b9020af` and `c5f7c857`, and the worktree file equals it:

* the original assessment: `7e9a0a82…`;
* A1: `ae5ace43…`.

The only commits that ever touched the two files are `8b64d989` and `e681d16f`.

## 5. Object accounting: PASS

* **Between the marker (20:58:01) and the reboot (00:00:15):** no object was written. The only objects of the
  launch minute are the two pre-marker probes of 20:58:00, `a1995184…` and `501388e2…`.
* **After the reboot:** 53 loose objects were written, and no pack or info file.
  * They are exactly the set `git rev-list --objects c6c7cbe4..c5f7c857`:
    * `8b64d989`, 12 objects;
    * `ef29bc2b`, 9 objects;
    * `e681d16f`, 12 objects;
    * `0b9020af`, 9 objects;
    * `c5f7c857`, 11 objects.
  * By type: 5 commits, 33 trees and 15 blobs.
  * Every path lies under `level4/closure_proofs/p5y_k5_cell308_research/`. None is an `evidence/execution` path, a
    `MB308_CELL308_RESULT*` name or an emergency file, so none is a result object.
  * E1's formulation ("… `8b64d989`, `ef29bc2b`, `e681d16f`, and any later research commit") covers `0b9020af` and
    `c5f7c857`.
* **Formal state, re-verified.**
  * The marker still points to `afa93072`.
  * The formal tree is clean, including ignored files.
  * There is no pending ref, no emergency file and no `evidence/`.
  * No MB308 or `caffeinate` process is alive.

## 6. Conditions that bind the next steps (C4–C6, restated)

**C4. The formal `postexec/` record** is now permitted, and only as review §8a allows.
* **Form.**
  * One additive commit under `NSF/postexec/`, a direct child of `afa93072`.
  * It never touches `refs/p5y-k5-cell308-mb-r1/*`.
  * It never creates `evidence/` or any `GUARDED_PATHS` name.
  * It changes no frozen, qualification, review or authorization file.
* **What it states.**
  * The launch time (11:57:58Z) and the marker time (11:58:01Z).
  * The post-reboot state, with the object statement in E1/R2 form.
  * The host facts: the Force Quit at 23:29:00 JST, both caffeinate `ClientDied` entries, the qualitative pool-load
    continuation until at least 23:40:48, the last log entries, and the PMU forced reset at 00:00:15.
  * "Driver death most probably after 23:29:00, at the latest 00:00:15", and the hang's cause as unknown.
  * The launcher readings, labelled coordinator-reported.
  * TARGET_EVALUATION_COUNT 1.
  * "State equivalent to CONSUMED_UNRECORDED; the driver never returned".
  * The §8 row verbatim: CELL308_EXECUTION_INDETERMINATE (target consumed; no rerun).
  * The status lines.
* **What it must not contain.**
  * No target, bound, Γ or partial quantity.
  * No job-level information.
  * No seal, sealed status or exit code.
  * No result schema or result-like file name.
  * No resume or rerun mechanism.
  * No causal claim beyond the evidence.
  * No decoy, validation or qualification value next to any cell-308 quantity.
* **A checks script, if any,** uses stdlib and read-only git plumbing only, imports no `mb308_*` module or pinned
  certifier, and does not arm the guard.

**C5. Protocol §10 steps 6–8** run on the postexec record, each by a fresh reviewer, unless the user records a
different decision before the adjudication.
* **Step 6, the execution review.** It checks the record against the repository and logs. Items that presuppose a
  seal are reported as "not available: unsealed". It discloses the host events and E1/E2 compliance.
* **Step 7, the adjudication.** It applies §8 verbatim and carries G3's text.
* **Step 8, the adjudication review.**
* Whatever the verdicts, there is no rerun.

**C6. Standing prohibitions.**
* No `execute`, and no `seal-only` (there is nothing to seal).
* No change to, and never a deletion of, any ref under `refs/p5y-k5-cell308-mb-r1/`.
* No new grant, rerun, resumption or recomputation for cell 308 under route MB r1 without a new independent
  governance process and a new user decision (E7).
* No proxy or reconstruction of any target quantity.
* r5 stays authoritative, with no r6. K5 is PARTIAL and P5Y is unchanged.
* Read-only audits of the formal worktree use `GIT_OPTIONAL_LOCKS=0`.

## NOTES

* **N1.** The wording note in §3.
* **N2.** The delta review's wording notes still apply to the postexec record. It should write "for the incident
  window" after "no panic, watchdog or jetsam report", and "Stage-1 pool load continued" rather than a core count.
  These are notes, not repairs.
