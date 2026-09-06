"""P4Z -- estimator redesign and feasibility adjudication for the P4 general
location-family truncated-window derivative.

This package contains NO scientific result artifacts.  It contains the
candidate estimators, their analytic contracts, and the micro-pilot harness
used to falsify them.  The frozen P4 theorem, thresholds and conventions are
inherited unchanged from
``level4/closure_proofs/p4_theory_generalization/``.
"""

from .analytic import (
    FAMILY_KITS,
    FamilyKit,
    alarm_bounds,
    alarm_integrals,
    whole_line_integrals,
)
from .rbscore import rb_score_batch
from .rbmap import rb_map_batch, rb_map_derivative_batch

__all__ = [
    "FAMILY_KITS",
    "FamilyKit",
    "alarm_bounds",
    "alarm_integrals",
    "whole_line_integrals",
    "rb_score_batch",
    "rb_map_batch",
    "rb_map_derivative_batch",
]
