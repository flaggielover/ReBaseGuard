# Brief: incident-independence review of the SECOND rev. 2c delta (condition C2 / R4-C1; formal campaign p5y_k5_cell309_p309_r1)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent incident-independence reviewer, author of:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`.

## Question

The pre-freeze review R4 blocked the freeze (`reviews/REVIEW_PREFREEZE_R4_P309.md`, B1–B8). The owner then ratified the
D5 extensions (`governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`). The resolution is the append-only section "Second
delta" of `governance/P309_REV2C_AMENDMENTS.md` (A20–A30), together with formal erratum FE-9.

Your condition C2 and your D8 require a new independence review of any further rule, parameter or binding change. R4's
condition R4-C1 names two: the minimum grant horizon (A21) and the amended grant window (A23). The table also marks
these as new rules: A22 (the job-end mapping), A24 (the freeze record) and A27 (no-retry qualification).

For every row A20–A30: is the change **temporally and parametrically independent** of the exposed information, and
does it move a rule toward closure in a way that could reflect target information or result chasing?

## Tasks

1. **Classify each row.** Say whether it is a rule, a parameter, a mechanism or binding, or qualification only. Give
   its direction for closure and its source (R4 finding, owner decision, implementation). Check that its basis is
   target-free.
2. **Specific attention:**
   * **A21, the 14-day horizon.** Is 14 days a choice that could favour an outcome? Is the pre-marker dry admission
     outcome-neutral?
   * **A22, the job-end mapping.** SIGKILL below the per-job limit is now INDETERMINATE instead of a fallback. Direction
     and basis.
   * **A23, A24 and A27:** the grant window, the freeze record, and no retry.
   * **A20, the cell from `cells.json`.** Also FE-9's structural read. The coordinator evaluated every cover cell's
     endpoints in memory to prove the reader equal to the canonical loader; only the boolean and cells 0/1 were
     displayed (exposure ledger). Is that read necessary, and is it correctly classified?
   * **A29, the D5 implementation.** It adds no rule. Confirm that it neither narrows nor widens anything the owner
     did not decide.
3. **New exposures.** Read `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/ZERO_TARGET_LEDGER.jsonl` from commit `e53a678c`
   onwards. Did anyone see a 305–309 value? The ledgers include R4's runs, the verifier author's runs and the
   coordinator's dev runs.
4. **Liabilities.** Check the liabilities that `code/make_freeze_params.py` now freezes: R4 FREEZE_BLOCKED and its
   resolution, FE-9, and D5. Do the added items suffice? Does anything need to go into the conditions carried into the
   grant?

## Firewall

The same as your earlier briefs:
* Allowed: all of FNS and RNS; the overnight incident files; git metadata.
* Never reproduce a 305–309 value.
* Forbidden:
  * THEOREM_TCT lines 12 and 39;
  * any cell-307 or cell-308 campaign file other than git metadata, masked `code/code_skeleton.py` output, or AST
    output;
  * any evaluation for cells 305–309;
  * any in-band kernel run;
  * git writes;
  * modifying anything except your output file.
* Ledger your reads and runs to a scratch file, and name it in your output.

## Output

`reviews/REVIEW_DELTA2_INCIDENT_P309.md`.

Line 2 is exactly one of:
* `DELTA2_INDEPENDENCE_ACCEPTED`;
* `DELTA2_INDEPENDENCE_REJECTED`. The campaign then STOPs before the freeze.

It must also contain a section headed exactly `## Conditions`, which the freeze parameters carry verbatim.
