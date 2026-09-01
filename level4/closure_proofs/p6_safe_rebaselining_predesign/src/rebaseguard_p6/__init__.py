"""P6 pre-design harness — policy-driven re-baselining over the FROZEN core.

This package exists to make three things structural rather than aspirational:

1.  the frozen detector semantics are never touched (``chain.py`` reuses the
    frozen ``cusum_update`` and the verbatim Stage-D SR recursion through the
    P7 package, and a constant policy reproduces ``rebaseguard_p7`` bit-for-bit);
2.  an *implementable* policy cannot read the latent reference error, because
    the object it is handed does not contain it (``policy.py``);
3.  tuning and evaluation seeds cannot collide (``seeds.py``).

Nothing here runs a campaign.  See ``FULL_CAMPAIGN_ENTRY_GATE.md``:

    FULL_P6_CAMPAIGN = BLOCKED_WAITING_FOR_P5_ADJUDICATION
"""
from __future__ import annotations

CUSUM = "cusum"
SR = "sr"

#: Seed families.  ``TUNE`` fits, ``EVAL`` reports, ``REPLAY`` adjudicates.
TUNE, EVAL, REPLAY = "tune", "eval", "replay"
SEED_FAMILIES = (TUNE, EVAL, REPLAY)

#: Policy classes (OBSERVABILITY_AUDIT.md section 7).  Only ``IMPLEMENTABLE``
#: policies may ever appear in a recommendation.
IMPLEMENTABLE, ORACLE, DIAGNOSTIC = "implementable", "oracle", "diagnostic"
POLICY_CLASSES = (IMPLEMENTABLE, ORACLE, DIAGNOSTIC)

__all__ = [
    "CUSUM", "SR", "TUNE", "EVAL", "REPLAY", "SEED_FAMILIES",
    "IMPLEMENTABLE", "ORACLE", "DIAGNOSTIC", "POLICY_CLASSES",
]
