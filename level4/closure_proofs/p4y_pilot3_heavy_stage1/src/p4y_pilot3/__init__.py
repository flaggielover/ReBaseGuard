"""P4Y PILOT-3 -- heavy-tail Stage-1 sizing closure pilot.

NON-BINDING.  Not P4Y production, not a binding checkpoint, not permission to
run the 96-cell scientific campaign.

Pilot-2 (commit 7797368) left exactly ONE unresolved design question, and this
pilot answers only that question:

    how to size the INITIAL production allocation for heavy-tail strata
    without systematically underestimating the precision requirement.

Pilot-2's measured failure mechanism: at the historical heavy-tail reference
of ~4 blocks, relSE_ref fell BELOW its true value in 95-100 % of fresh draws
with a median of 34-41 % of truth; Stage-1 raises that to the power 1/kappa,
so it bought a median 11-17 % of the true requirement.

Inherited unchanged and imported read-only:
  * the staged continuation rule and its auditor   (p4y_pilot2.rule, .audit)
  * the exact shard partition                      (p4y_pilot.shard)
  * per-block evaluation of the frozen estimators  (p4y_pilot.blocks)
  * Clopper-Pearson bounds                         (p4y_pilot.stats)
"""

__all__ = ["addressing3", "strata3", "ucb", "sizing"]
