# Brief: independent review of the P309-r2 plan (before implementation)

This brief is committed before it is issued (condition C5, carried over to r2).

**Reviewer.** A new independent reviewer who wrote none of the P309 code and none of the r2 plan, and is not the
coordinator.

## Authority and boundaries (read first)

r2 is a fresh successor campaign for cell 309, after r1 ended at QUALIFICATION_FAILED. The owner's instructions of
2026-10-01 set:
* the scope: qualification infrastructure and execution-host durability;
* no scientific change unless an independent review shows one is necessary;
* r1 is never mutated;
* the shared AWS worker, with exclusive heavy compute and no interference with cell 308;
* no use of the retired Vultr worker;
* bulk data never through the owner's Mac.

NEW Γ309 TARGET EVALUATIONS must stay 0.
* No grant, marker or pending ref.
* Never run `execute`, `seal-only` or `validate-grant`.
* No value for cells 305–309; no cell-307 or cell-308 campaign file beyond git metadata.
* No git writes. Write only your output file.

## What to review

* `level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/R2_PLAN.md` on branch `claude/p5y-k5-cell309-p309-r2`,
  at the commit that adds this brief.
* r1's postmortem and its independent review, under `p5y_k5_cell309_p309_r1/handoff/` and `reviews/`.
* r1's governance (`governance/`: A24, A27, the owner decisions, the D5 ratification).
* The r1 code the plan names.

## Questions

1. **Scope.** Is every change in §3 truly infrastructure, or correctly flagged as a binding or owner item? Does
   anything in the plan risk changing a scientific output? Is the byte-for-byte equivalence proof in §2 sufficient?
2. **QC11 repair (§4).**
   * Is the root cause right?
   * Is basing sandboxes on the recorded freeze commit F correct and minimal?
   * Are the invariant, mutant R2-M01 and static assertion enough to stop a regression?
   * Is the production path unchanged?
   * Should the guard and verifier sandboxes follow the same rule now?
3. **Post-freeze rehearsal (§5).** Does it reproduce the post-freeze topology faithfully enough to catch the r1 class
   of defect (pre-freeze PASS, post-freeze harness failure)? What could still slip through? Is the cloud tier versus
   worker tier split sound?
4. **Shared host and isolation (§6).** Are the isolation proof and the cross-campaign exclusion gate sufficient and
   read-only towards cell 308? Is Q-HOST (§7) a sound fail-closed rule? Is "no retry" correctly kept?
5. **Requirements (§8).** Are the minimum resources and the durability window justified by r1's evidence?
6. **Owner decisions (§8A).** Are OD-R2-1 to OD-R2-3 the right stop points? Is anything owner-reserved missing?
7. **Gate order (§9).** Is anything missing before the r2 freeze?

## Output

`level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/REVIEW_R2_PLAN.md`, with line 2 exactly one of:
* `R2_PLAN_ACCEPTED`, with conditions P1…;
* `R2_PLAN_REJECTED`, with reasons.

Include a section headed exactly `## Conditions`, and a disclosure section.
