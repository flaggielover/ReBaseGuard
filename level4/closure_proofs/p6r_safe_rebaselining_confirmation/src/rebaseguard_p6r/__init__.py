"""P6R -- the repaired confirmation campaign for ReBaseGuard Priority 6.

This package adds ONLY protocol, selection, statistics and analysis.  The
method, the chain and the frozen detector are imported unchanged from the
adjudicated P6 campaign package ``rebaseguard_p6c``, which is itself a thin
policy layer over the frozen P7 core.  Nothing in the scientific object under
test is re-implemented here, so ``T6-B`` and the fixed-``k`` ``T6-C`` continue
to describe exactly the object being confirmed.

Modules
-------
``select``    TUNE-only fixed-``rho`` selection (adjudication blocking defect 1)
``stats_r``   the repaired statistical procedure (blocking defect 2)
``onestep``   the direct realized one-step risk statistic (Jensen evidence)
``costs``     the three precommitted cost accountings
``audit``     calibration diagnostics

Status
------
``ORIGINAL_P6_VERDICT   = PARTIAL`` (independent adjudication; closure rejected)
``T6_B                  = EXACT_VALID``
``T6_C                  = VALID_WITH_NARROWER_ASSUMPTIONS`` (fixed ``k`` only)
``NOVELTY``             see ``NOVELTY_SCOPE.md``; nothing is upgraded here.
"""
from __future__ import annotations

ORIGINAL_P6_VERDICT = "PARTIAL"
T6_B_STATUS = "EXACT_VALID"
T6_C_STATUS = "VALID_WITH_NARROWER_ASSUMPTIONS"

__all__ = ["ORIGINAL_P6_VERDICT", "T6_B_STATUS", "T6_C_STATUS"]
