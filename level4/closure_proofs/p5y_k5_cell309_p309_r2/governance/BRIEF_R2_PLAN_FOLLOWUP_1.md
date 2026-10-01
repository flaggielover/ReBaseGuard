# Brief: focused follow-up review of P309-r2 plan addendum 1 (P1–P5)

This brief is committed before it is issued (C5).

**Recipient:** the independent reviewer of `governance/REVIEW_R2_PLAN.md`. Your first brief's boundaries hold
unchanged: no git writes, no campaign code, git metadata only for cell-307/308, and target evaluations stay 0.

**Task.** At the commit that adds this brief, check that:
* `governance/R2_PLAN_ADDENDUM_1.md`, `governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md` and
  `governance/R2_LITERAL_DISPOSITION.json` satisfy your conditions **P1–P5** exactly;
* the dispositions of P6–P23 and the gate order (P13) are faithful to your text;
* the P1 redaction is disclosed adequately;
* the P2 table's dispositions are correct row by row. Spot-check the code, config, test and verify rows, and re-run
  the inventory if you wish.

Anything missing is a condition. No implementation starts before your acceptance.

**Output:** `governance/REVIEW_R2_PLAN_FOLLOWUP_1.md`, with line 2 exactly one of:
* `ADDENDUM_1_ACCEPTED`, with a section headed exactly `## Conditions`;
* `ADDENDUM_1_REJECTED`, with reasons.
