# Brief: second focused follow-up of the r2 delta review (repair round 2)

This brief is committed before it is issued.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
* the r2 code or its repairs;
* the verifier author's changes;
* the r2 plan or its addenda;
* any earlier r2 review: the delta review (`REVIEW_R2_DELTA.md`) or the first follow-up (`REVIEW_R2_DELTA_FOLLOWUP_1.md`).

**Boundaries.** These are the same as in the earlier briefs:
* no git write of any kind (no commit, ref, stash, config, fetch or push);
* NEW Γ309 TARGET EVALUATIONS = 0: never run `p309_driver.py execute`, `seal-only` or `validate-grant`, and never
  anything that could read a target input;
* no cell-305–309 values;
* no cell-307/308 file contents and no hashes of them;
* no decoy outputs opened;
* no network;
* scratch runs only under your own scratchpad, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` pointed
  there;
* every TEST process you start is yours to kill. Give each one a random token in its argv, and before you finish,
  check that no process carrying your token is left. An earlier reviewer left two busy loops running.

**What you review.** The **committed bytes and evidence** on branch `claude/p5y-k5-cell309-p309-r2` at the commit that
adds this brief, over the range `ec34b2a3..`. That range is everything after the first follow-up review was preserved
and pushed. Two documents are guides only, never evidence:
* `governance/R2_DELTA_RESPONSE_2.md`, the coordinator's account;
* `governance/REVIEW_R2_DELTA_FOLLOWUP_1.md`, the conditions FU1–FU4 and advisories V1–V10 that you check against.

Verify from git and from the preserved evidence.

## What to assess (every item)

1. **Each of FU1–FU4 and V1–V10.** For each, say whether it is met in the bytes, deferred by the plan, or not met. FU1
   is blocking-before-owner-decisions:
   * check `governance/OWNER_DECISION_PACKET_R2.md` against FU1 (a) and (b) word by word;
   * check `R2_AWS_SESSION_INSTRUCTIONS.md`, `R2_HOST_REQUIREMENTS.md` and `P309_R2_AMENDMENTS.md` §G for the same
     facts;
   * check that the packet still decides nothing.
2. **`kill_own_descendants`** (`code/p309_host.py`). Is the traversal now complete against a descendant that forks
   during the call? Does the start-time check prevent signalling a reused pid? Does anything outside the caller's tree
   get signalled? Reproduce your own fork-race control if you can.
3. **The end-to-end abort control A01** (`tests/test_p309_host_controls.py`). Check:
   * that nothing is written in `qualification/`;
   * that the abort row in the namespace ledger is preceded by the explanatory row, and that the reason for not
     redirecting the ledger (QC12 T7) holds;
   * that the control fails if the abort does not kill the tree.
   * Does it show C5 for the worker-tier drill as the review asked?
4. **QC12 T14's V1 extension** and the new mutants T14f–T14h.
5. **The launcher's V2 refusal and V4 blocker**, and why V4 is a blocker rather than a refusal.
6. **The monitor's V5 timing** and the 45 s default, against the sampling code.
7. **FU3**: is `P309_R2_AMENDMENTS.md` §G mechanical and consistent with §D, and is the file still append-only?
8. **FU4**: is the operating procedure in §4.1 complete and safe? Does it ask anything of cell 308 beyond read-only
   facts and agreement?
9. **The re-drill and the evidence.**
   * The cloud-tier drill attempt named below: its report, its ledger rows in full (including the A01 row pair), the
     controls, and F2.
   * `governance/R2_REPIN_LIST_SUPPLEMENT_2.json`, row by row.
   * `governance/R2_EQUIVALENCE_P8_ROUND3.json`: recompute (a)–(d).
10. **No scientific change.** Confirm that nothing changed in the scientific object, the driver, the guard, the
    verifier, the generators or the scanner code in this round.
11. **Anything new.** Look for a fail-open path, a false positive that would consume the single attempt on a shared
    host, a signal to a process not owned by the caller, a leaking record, a refusal after the attempt directory, or
    an implicit owner decision.

## The re-drill

* **Evidence:** `evidence/drill/20261001T224858Z/` (attempt 8; PASS). Attempt 7 (`evidence/drill/20261001T222108Z_INTERRUPTED/`) was
  interrupted by a container restart during QC_D5 and is preserved with a coordinator-written record. Check it too.
* **Code commit:** the round-2 repairs are `8cb59c0f`. The drill's clone base is `8725f8b7`, whose code bytes are
  identical; after `8cb59c0f` only evidence and ledger records were added.
* **The coordinator's independent validation:** `governance/R2_DRILL_ATTEMPT8_VALIDATION.json` (44/44). It discloses a
  validator defect found and fixed on its first run.
* **The kept drill clone** (F′ `ed89357f`, FR′ `c9579c0d`) stays at
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_drill_cloud_8/drill_20261001T224858Z/clone`.
  You may read it with read-only git. Never write to it.
* **P8 round 3:** `governance/R2_EQUIVALENCE_P8_ROUND3.json`. It shows no change from round 2.
* **The container restarts:** two this round. Both are recorded in the validation record and in attempt 7's
  interruption record.

## Output

**`governance/REVIEW_R2_DELTA_FOLLOWUP_2.md`.** Line 2 is exactly one of:
* `R2_DELTA_FOLLOWUP_2_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
* `R2_DELTA_FOLLOWUP_2_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**. Avoid the words that
`code/p309_placeholder_check.py` flags.

**Your execution ledger** goes in your scratchpad. Do not commit.
