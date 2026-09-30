# Brief: incident-independence review of the rev. 2c delta (condition C2; formal campaign p5y_k5_cell309_p309_r1)

This brief is committed before it is issued (condition C5). The recipient is the independent incident-independence
reviewer (the author of `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md` and `reviews/REVIEW_U2_CHECK_P309.md`).

## Question

Your condition C2 reads: "Any change to a rule or parameter after this review needs a new incident-independence review
of the delta." Are the changes from rev. 2b listed in `governance/P309_REV2C_AMENDMENTS.md` (A1–A19) and in
`fc2/FC2_SPEC_R2_ERRATUM_1.md` (E1-1..E1-5) **temporally and parametrically independent** of the exposed information?
Does any of them move a rule or parameter toward closure in a way that could reflect target information or result
chasing?

## Tasks

1. **Each change.** Classify it as a rule change, a parameter change, a mechanism/binding change, or a qualification-only
   change. Give its direction for closure (toward, against or neutral) and its source (owner ruling, independent review,
   implementation constraint). Check that its basis is target-free, using git commit order, the formal exposure ledger
   and the formal execution ledger.
2. **New exposures.** Read `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/ZERO_TARGET_LEDGER.jsonl` from commit 39ed662c
   on. Did the coordinator, the FC2 authors or any tool see a 305–309 value? The masked reads are listed there; you may
   spot-check the tools that produced them (`code/code_skeleton.py`, the masked grep).
3. **Specific attention:**
   * A6 (no post-marker wall-clock cap);
   * A5 (the Stage-1b per-job limit);
   * A4 (the Stage-1b guard);
   * A1/A3 (the QC14 and QC08 changes);
   * A10 (the pending-ref NAME allowance and the exactly-once sites; an extension of the owner's marker-name
     allowance);
   * A14 (the proposed execution host);
   * E1-1 (the strict-descendant reading, which prevents a silent refusal of every in-band certificate).
4. **Liabilities.** Do any of the changes need to be added to `disclosed_liabilities`, or to the conditions C1–C8
   carried into the grant?

## Firewall

The same as `reviews/BRIEF_INCIDENT_INDEPENDENCE_P309.md`:
* Allowed: all of FNS and RNS; the overnight incident files; git metadata.
* Never reproduce a 305–309 value.
* Forbidden:
  * THEOREM_TCT lines 12 and 39;
  * any cell-307 or cell-308 campaign file other than git metadata, the masked `code/code_skeleton.py` output, or AST
    output;
  * any evaluation for cells 305–309;
  * any in-band kernel run;
  * git writes;
  * modifying anything except your output file.
* Ledger your reads and runs to a scratch file, and name it in your output.

## Output

`reviews/REVIEW_DELTA_INCIDENT_P309.md`, with line 2 exactly one of:
* `DELTA_INDEPENDENCE_ACCEPTED`, followed by any conditions;
* `DELTA_INDEPENDENCE_REJECTED`, followed by the reasons. The campaign then STOPs before the freeze.
