# Brief: incident-independence review of the THIRD rev. 2c delta (conditions C2, D8; delta-2 E10)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent incident-independence reviewer, author of:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`.

## Question

R4's follow-up review blocked the freeze again: `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`, FREEZE_BLOCKED, with F1,
F2, NF1 and NF2. The resolution is commit `3cb5d513`, plus `147ba3a2` (a scanner cache reset with no rule change). It
is recorded as the append-only section "Third delta" (A31–A36) of `governance/P309_REV2C_AMENDMENTS.md`, with the
report to the owner `governance/D5_SITE_BACKSTOP_REPORT_P309.md`.

Your conditions C2 and D8, and your delta-2 condition E10, require an independence review of any further rule,
parameter or binding change. The rows marked as new rules are:
* **A31**, a strengthened precondition at the two exactly-once sites (a runtime backstop);
* **A34**, the `authority` test narrowed to the proposal's own placeholder texts, and `execution_host.worktree`
  required.

A32, A33, A35 and A36 are marked as implementation or controls.

For every row A31–A36: is the change **temporally and parametrically independent** of the exposed information? Does it
move a rule toward closure in a way that could reflect target information or result chasing?

## Tasks

1. **Classify each row.** Say whether it is a rule, a parameter, a mechanism or binding, or controls only. Give its
   direction for closure and its source (an R4 finding or the owner's D5). Check that its basis is target-free.
2. **Specific attention:**
   * **A31.** In a correct run, are its conditions already guaranteed when a site is reached, so that no outcome
     changes? Does it narrow anything the owner decided in D5, or widen anything?
   * **A34.** The narrowing admits `authority` strings that were refused before, for example a quote of the owner's
     words containing `<`, `>` or `->`. Direction, and whether anything about the target could bear on it.
     `validate-grant` also reads the pinned `cells.json` entry of the target cell (compared, not displayed; ledgered).
     This is the same read as the proposal tool's, taken once at validation time on the execution host. Is that read
     necessary and correctly classified?
   * **A32 and A33.** Confirm that they add no rule on the evaluation, only rejections of code paths.
3. **New exposures.** Read `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/ZERO_TARGET_LEDGER.jsonl` from commit `a873ca83`
   onwards. Did anyone see a 305–309 value? This covers the coordinator's dev runs and R4's runs.
4. **Liabilities.** Check the liability item that `code/make_freeze_params.py` now adds for the R4 follow-up, and the
   new `grant_rules` texts (`grant_validation`, `site_backstop`, `premarker_admission`). Is anything missing, or does
   anything need to go into the conditions carried into the grant?

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

`reviews/REVIEW_DELTA3_INCIDENT_P309.md`.

Line 2 is exactly one of:
* `DELTA3_INDEPENDENCE_ACCEPTED`;
* `DELTA3_INDEPENDENCE_REJECTED`. The campaign then STOPs before the freeze.

It must also contain a section headed exactly `## Conditions`, which the freeze parameters carry verbatim.
