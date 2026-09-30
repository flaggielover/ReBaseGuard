# Brief: independent check of the U2 corrected proposition (formal campaign p5y_k5_cell309_p309_r1; before the freeze)

This brief is committed before it is issued (condition C5). The reviewer is the independent incident-independence
reviewer, who wrote `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md` and its condition C7. It is continued for this
check because it already holds the U2 context. It has not produced or coordinated the campaign.

## Question

The owner's U2 ruling (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`, "OWNER RULING — U2") confirms U2 = NOT_TRIGGERED
only on the corrected premise, and only if it is established from committed evidence; otherwise the campaign STOPs with
U2_UNRESOLVED. Is the corrected proposition **U2-CP** (`governance/U2_CORRECTED_PROPOSITION.md` §4) established from
committed evidence?

## Tasks

1. **Criterion (§3).** Are Q1–Q5 a faithful reading of U2's committed definition, C6 Condition 10 and the committed
   examples? Is anything missing or stretched? You may re-read C6 Condition 10 only through a masked read
   (numbers masked, as the coordinator did), and you must ledger it.
2. **Inventory (§5).** Check it against the code. Is every potentially P3-derived quantity on the Stage-2 path listed,
   with the right role (load-bearing, gate-only, present-only, absent)? Is any row mis-classified?
3. **Mechanical evidence (§6).** Check the following:
   * Is `code/u2_structure_check.py` sound?
     * Are the polynomial identities in S1 the right ones, and do they support §4.4?
     * Could the checker pass on a formula that forms a new function of adopted scalars?
     * Do S3 and S4 cover what they claim?
   * Are the planted controls meaningful?

   You may run `python3 code/u2_structure_check.py` and `python3 tests/test_u2_structure_controls.py`. Both are
   static, and both write only into `evidence/u2/`: restore those two files byte-identical afterwards, or report the
   difference.
4. **Corollary T boundary (§4.3–4.4).** Given the evidence, is the line between SRK (a consumer-level radius that
   changes only operator-side multipliers of sub-expressions the frozen TC-T already forms) and Corollary T (a re-derived
   record-level interval) now established? Or does it remain a judgement?
5. **Freeze obligations (§7).** Are F-U2-1..3 sufficient?

## Firewall

* **Allowed:**
  * all of FNS and RNS;
  * the files named in the U2 document;
  * the source of the pinned consumer files, **only** through `python3 code/code_skeleton.py py <file>`, which
    strips docstrings and comments and masks numbers;
  * the two input files **only** through `python3 code/code_skeleton.py json <file>`, which shows key types only;
  * git metadata.
* **Forbidden:**
  * raw reads of `tct_rule.py`, `tail_forecast_r2.py`, `c2_d5_forecast.py` and `tc_rule.py` beyond the skeleton;
  * any value in TCT_INPUTS_309, ADOPTED_TAIL_INPUTS or the K1 records;
  * THEOREM_TCT lines 12 and 39;
  * any cell-307 or cell-308 file beyond `code_skeleton` or AST output;
  * any evaluation for cells 305–309;
  * any kernel run in the band;
  * git writes;
  * modifying anything except your output file.
* **Executions and reads** are ledgered to a scratch file, which you name in your output.

## Output

`reviews/REVIEW_U2_CHECK_P309.md`, with line 2 exactly one of:
* `U2_CP_ESTABLISHED`, followed by any conditions;
* `U2_UNRESOLVED`, followed by the reasons. The campaign then STOPs before the freeze.
