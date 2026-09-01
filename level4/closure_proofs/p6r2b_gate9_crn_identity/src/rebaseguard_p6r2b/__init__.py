"""P6R2b -- ultra-narrow Gate-9 repair: addressable primitive CRN identity.

The only defect repaired here is the one the independent delta adjudication
found:

    CRN_PATH_IDENTITY = FAIL

The previous P6R2 CRN driver removed policy-dependent *seeds*, but it still drew
overflow observations from a shared sequential generator indexed by the
**current live-replicate set**.  Variants with different stopping behaviour have
different live sets, so overflow consumption -- and therefore the mapping of raw
values to replicates -- became variant-dependent.  ``cusum_m5`` overflow counts
differed materially across variants.

What is required is **identical primitive exogenous randomness**, not identical
endogenous trajectories.  Endogenous divergence is the *expected* consequence of
perturbing a policy parameter and is neither prevented nor tested for here.
"""
from __future__ import annotations

SOURCE_HEAD = "c57e1930303738eef7a600d6bf047d7a708aaff8"
IDENTITY_CONTRACT = (
    "For every (seed_namespace, detector, m, k, replicate_id, cycle_id, "
    "primitive_type, primitive_index) the raw exogenous draw is bit-identical "
    "across all sensitivity variants.  The address contains no policy_id, no "
    "variant label, no s1 multiplier, no live-set position, no stopping time, "
    "no branch order and no count of previously consumed draws."
)

__all__ = ["SOURCE_HEAD", "IDENTITY_CONTRACT"]
