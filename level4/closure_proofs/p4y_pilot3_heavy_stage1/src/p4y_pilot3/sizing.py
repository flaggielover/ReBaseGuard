"""Stage-1 sizing: the one thing Pilot-3 changes.

    U   = UCB(reference block means)          one-sided upper bound at UCB_LEVEL
    N1  = N_ref * (U / r*) ** (1/kappa)
    B1  = ceil(N1 / block_size)               rounded ONCE, at the logical
                                              total-block level

Brief section 10: all rounding happens exactly once, at the logical total, and
never per shard.  Working directly in blocks -- ``B1 = ceil(B_ref * (U/r*) **
(1/kappa))`` -- is the same statement, since ``N = B * block_size`` with one
frozen block size per stratum.

Everything after Stage 1 is Pilot-2's staged rule, imported unchanged.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stage1:
    b_ref: int
    relse_point: float          # the Pilot-2 quantity, reported for contrast
    relse_upper: float          # what this rule actually sizes from
    b1: int
    b1_point: int               # what the Pilot-2 rule would have allocated
    inflation: float            # U / point estimate
    refused: bool               # B1 above the frozen absolute ceiling


def size_stage1(*, b_ref: int, relse_point: float, relse_upper: float,
                target: float, kappa: float, min_blocks: int,
                abs_ceiling: int) -> Stage1:
    """Size Stage 1 from the UPPER bound, and record what the point estimate
    would have bought, so the two can be compared replicate by replicate."""

    def allocate(u: float) -> int:
        if not math.isfinite(u) or u <= 0:
            return abs_ceiling + 1
        return max(min_blocks, math.ceil(b_ref * (u / target) ** (1.0 / kappa)))

    b1 = allocate(relse_upper)
    b1_point = allocate(relse_point)
    inflation = (relse_upper / relse_point
                 if relse_point > 0 and math.isfinite(relse_point) else math.inf)
    return Stage1(b_ref, relse_point, relse_upper, b1, b1_point, inflation,
                  b1 > abs_ceiling)


def coverage(b1: int, b_required: int) -> bool:
    """Did Stage 1 alone already buy the true requirement?

    This is the quantity Pilot-2's failure was measured in: its point-estimate
    rule bought a median 11-17 % of it on the heavy strata.
    """
    return b1 >= b_required
