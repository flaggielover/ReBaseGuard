"""P4Y FINAL PRE-FREEZE PILOT (PILOT-2) -- precision/execution governance only.

NON-BINDING.  Not P4Y production.  Not a P4Y Checkpoint A.  Not permission to
re-run the 96-cell scientific campaign.

Pilot-1 (branch p4y-prefreeze-pilot, commit cefc03d) returned
NEEDS_ONE_MORE_PRE-FREEZE_PILOT for exactly two reasons:

  1. its primary endpoint was ambiguous, and was amended after design results
     were visible;
  2. it could not freeze a trustworthy production cap, because it measured the
     cost tail at B1 = 24 blocks while production runs at 48-1784.

Pilot-2 fixes both by construction: the endpoint is frozen mechanically before
any result-bearing byte exists, and every stratum is an ACTUAL P4X stage-1
block count.

Inherited unchanged from Pilot-1 and imported read-only:
  * the exact shard partition and its invariants   (p4y_pilot.shard)
  * per-block evaluation of the frozen estimators  (p4y_pilot.blocks)
  * Clopper-Pearson bounds                         (p4y_pilot.stats)
"""

__all__ = ["addressing", "strata", "rule", "audit", "project"]
