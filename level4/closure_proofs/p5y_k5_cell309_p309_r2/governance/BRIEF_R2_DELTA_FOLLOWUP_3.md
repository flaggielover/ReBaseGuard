# Brief: third focused follow-up of the r2 delta review (repair round 3)

This brief is committed before it is issued.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
* the r2 code or its repairs;
* the verifier author's changes;
* the r2 plan or its addenda;
* any earlier r2 review: `REVIEW_R2_DELTA.md`, `REVIEW_R2_DELTA_FOLLOWUP_1.md` or `REVIEW_R2_DELTA_FOLLOWUP_2.md`.

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
adds this brief, over the range `9dcd9d53..` (everything after the second follow-up review was preserved and pushed).
Two documents are guides only, never evidence:
* `governance/R2_DELTA_RESPONSE_3.md`, the coordinator's account;
* `governance/REVIEW_R2_DELTA_FOLLOWUP_2.md`, whose conditions SF1–SF2 and advisories W1–W8 you check against.

Verify from git and from the preserved evidence.

## What to assess (every item)

1. **SF1–SF2 and W1–W8.** For each, say whether it is met in the bytes, deferred by the plan, or not met.
2. **SF1 in depth.**
   * Do `MonitorIO`, `qhost_monitor`, `start_qhost_monitor`, `stop_qhost_monitor` and `monitor_liveness` together bound
     every gap as claimed, for every stop time and every sample duration the code allows?
   * Is the monotonic clock truly shared between the runner and its monitor child?
   * Do MV01–MV05 drive the committed loop, and would they catch a regression?
   * Is anything about Q-HOST weaker than before? For example: a monitor that stops writing result rows but keeps
     writing start rows; or a sample whose result row never arrives.
3. **SF2.** Can every command in `R2_AWS_SESSION_INSTRUCTIONS.md` §3 and §4.1 and in `R2_BOOTSTRAP.md` 8c run as
   written on the §3.1 file? Is the check directory kept apart from every run's scratch root?
4. **`kill_own_descendants` (W1).** Check the stop-confirmation walk and the start-time checks. Can the loop fail to
   end, or signal a process outside the caller's tree?
5. **T14 (W5)** and the mutants T14i–k.
6. **The in-unit controls U01–U03 (W6).** They run only on the worker tier, so they cannot be run here. Review their
   logic by reading: would each reach the refusal it names inside a correct unit, and are their TEST copies confined
   to the launch's scratch root?
7. **The re-drill and the evidence.**
   * The cloud-tier drill attempt named below: its report, its ledger rows in full, the controls, and F2.
   * `governance/R2_REPIN_LIST_SUPPLEMENT_3.json`, row by row.
   * `governance/R2_EQUIVALENCE_P8_ROUND4.json`: recompute (a)–(d).
8. **No scientific change.** Confirm that nothing changed in the scientific object, the driver, the guard, the
   verifier, the generators or the scanner code in this round.
9. **The governance texts.** `OWNER_DECISION_PACKET_R2.md`: does it still decide nothing, and does it now state the
   gap rule exactly? Also check `P309_R2_AMENDMENTS.md` §H (append-only), the AWS instructions, the host requirements
   and the bootstrap.
10. **Anything new.** Look for:
    * a fail-open path;
    * a false positive that would consume the single attempt on a shared host;
    * a signal to a process the caller does not own;
    * a leaking record;
    * a refusal after the attempt directory;
    * an implicit owner decision.

## The re-drill

* **Evidence:** `evidence/drill/20261002T025624Z/` (attempt 9; PASS).
* **Code commit:** the round-3 repairs are `8c2aa69f`; the drill's clone base is `86706ca3`, the same code bytes plus
  their checkpoint record.
* **The coordinator's independent validation:** `governance/R2_DRILL_ATTEMPT9_VALIDATION.json` (44/44).
* **The kept drill clone** (F′ `2d8849c9`, FR′ `e582ab00`) is at
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_drill_cloud_9/drill_20261002T025624Z/clone`.
  You may read it with read-only git. Never write to it.
* **P8 round 4:** `governance/R2_EQUIVALENCE_P8_ROUND4.json`. It shows no change from round 3.

## Output

**`governance/REVIEW_R2_DELTA_FOLLOWUP_3.md`.** Line 2 is exactly one of:
* `R2_DELTA_FOLLOWUP_3_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
* `R2_DELTA_FOLLOWUP_3_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**. Avoid the words that
`code/p309_placeholder_check.py` flags.

**Your execution ledger** goes in your scratchpad. Do not commit.
