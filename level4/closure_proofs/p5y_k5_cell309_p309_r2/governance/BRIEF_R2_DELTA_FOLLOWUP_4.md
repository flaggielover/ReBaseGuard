# Brief: fourth focused follow-up of the r2 delta review (repair round 4)

This brief is committed before it is issued.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
* the r2 code or its repairs;
* the verifier author's changes;
* the r2 plan or its addenda;
* any earlier r2 review: `REVIEW_R2_DELTA.md` or `REVIEW_R2_DELTA_FOLLOWUP_1.md`–`_3.md`.

**Boundaries.** These are the same as in the earlier briefs:
* no git write of any kind;
* NEW Γ309 TARGET EVALUATIONS = 0: never run `p309_driver.py execute`, `seal-only` or `validate-grant`, nor anything
  that could read a target input;
* no cell-305–309 values;
* no cell-307/308 file contents and no hashes of them;
* no decoy outputs opened;
* no network;
* scratch runs only under your own scratchpad, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` pointed
  there;
* every TEST process you start carries a random token, is killed by you, and none is left at the end.

This container has restarted more than once tonight. Write your execution ledger and your review file incrementally.

**What you review.** The **committed bytes and evidence** on branch `claude/p5y-k5-cell309-p309-r2` at the commit that
adds this brief, over the range `ea71e5f4..` (everything after the third follow-up review was preserved and pushed).
Two documents are guides only, never evidence:
* `governance/R2_DELTA_RESPONSE_4.md`, the coordinator's account;
* `governance/REVIEW_R2_DELTA_FOLLOWUP_3.md`, whose advisories X1–X7 you check against.

Verify from git and from the preserved evidence.

## What to assess (every item)

1. **X1–X7.** For each, say whether it is met in the bytes, deferred by the plan, or not met.
2. **X1 in depth.**
   * With the stop time taken after the monitor is reaped, the times unrounded and `parse_monitor_rows`, can Q-HOST
     still fail wrongly at the stop, or pass wrongly?
     * Consider a monitor that hangs and is SIGKILLed after 30 s.
     * Consider a torn line that is not the last.
     * Consider an empty file.
   * Is the packet's list of what ends the attempt now complete and exact?
3. **X2.** Does the `kill_own_descendants` loop now end only on a walk begun after a settled observation? Can it fail
   to end, or signal outside the caller's tree? The response reports a development run of the previous reviewer's
   slow-fork harness: 7 of 20 trials with survivors for the round-3 function, 0 of 20 for this round, with one
   disclosed measurement fix to the harness copy. Reproduce it if you can, and judge whether K02, which by the
   response's own account does not reproduce the race, is described honestly.
4. **X3, the R01 control.**
   * Does it exercise the runner's own start and stop?
   * Is moving the interval into `QHOST["interval"]` safe for the official run, and is it still 60 s there?
   * Could the control fail spuriously on the cloud tier and so fail a drill for no reason?
5. **X4–X7.** Check the bounded forkers, the repeated cleanup, U01's TEST-only bytes and the directory removal, T14's
   stated scope, and the operator texts.
6. **The re-drill and the evidence.**
   * The cloud-tier drill attempt named below: its report, its ledger rows in full, the controls, and F2.
   * `governance/R2_REPIN_LIST_SUPPLEMENT_4.json`, row by row.
   * `governance/R2_EQUIVALENCE_P8_ROUND5.json`: recompute (a)–(d).
7. **No scientific change.** Confirm that nothing changed in the scientific object, the driver, the guard, the
   verifier, the generators or the scanner code in this round.
8. **The governance texts.**
   * `OWNER_DECISION_PACKET_R2.md`: does it still decide nothing?
   * `P309_R2_AMENDMENTS.md` §I: is it append-only?
   * Check the AWS instructions as well.
   * The third follow-up's ledger is kept in `evidence/reviews/`, bound by `governance/REVIEW_R2_DELTA_FOLLOWUP_3.sha256`.
     Is that handling sound?
9. **Anything new.** Look for:
   * a fail-open path;
   * a false positive that would consume the single attempt on a shared host;
   * a signal to a process the caller does not own;
   * a leaking record;
   * a refusal after the attempt directory;
   * an implicit owner decision.

## The re-drill

* **Evidence:** `evidence/drill/20261002T052554Z/` (attempt 10; PASS).
* **Code commit:** the round-4 repairs are `2fc6c130`; the drill's clone base is `cec189d9`, the same code bytes plus
  their checkpoint record.
* **The coordinator's independent validation:** `governance/R2_DRILL_ATTEMPT10_VALIDATION.json` (44/44).
* **The kept drill clone** (F′ `170074cc`, FR′ `bd6071b2`) is at
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_drill_cloud_10/drill_20261002T052554Z/clone`.
  You may read it with read-only git. Never write to it.
* **P8 round 5:** `governance/R2_EQUIVALENCE_P8_ROUND5.json`. It shows no change from round 4.
* **The container restarted a third time** after this attempt had finished; the evidence was checked intact.

## Output

**`governance/REVIEW_R2_DELTA_FOLLOWUP_4.md`.** Line 2 is exactly one of:
* `R2_DELTA_FOLLOWUP_4_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
* `R2_DELTA_FOLLOWUP_4_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**. Avoid the words that
`code/p309_placeholder_check.py` flags.

**Your execution ledger** goes in your scratchpad. Do not commit. Avoid the flagged words in the ledger too: it is kept with the
review.
