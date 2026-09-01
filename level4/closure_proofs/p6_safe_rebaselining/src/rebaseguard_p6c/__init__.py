"""P6 campaign harness — safe re-baselining over the FROZEN detector core.

This package is the *campaign* superset of the P6 pre-design harness
(``p6_safe_rebaselining_predesign/src/rebaseguard_p6``).  ``chain.py``,
``policy.py`` (baseline/oracle part), ``seeds.py``, ``metrics.py`` and
``stats.py`` are carried over so that the three structural disciplines of the
pre-design survive verbatim:

1.  the frozen detector semantics are never touched — a constant policy
    reproduces ``rebaseguard_p7.chain.simulate_chain`` with bit-identical
    ``tau`` (``tests/test_correspondence.py``);
2.  an *implementable* policy cannot read the latent reference error, because
    the object it is handed has no such field (``policy.py``);
3.  tuning, evaluation and replay seeds cannot collide (``seeds.py``).

What the campaign adds: ``saw.py`` (the selection-aware weighting family and
its ablations), ``calibrate.py`` (the offline design-time calibration and the
ARL-calibrated tolerance radius), ``runner.py`` (cell execution and the
per-replicate record schema) and ``analysis.py``.
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
