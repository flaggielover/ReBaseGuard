"""P6R2 — narrow literal closure repair over FROZEN P6R evidence.

Post-adjudication.  Not preregistered before the original P6R EVAL and not
presented as such.  Repairs exactly three adjudicated blockers and touches
nothing else:

    G6A  literal F3 family                       -> families.py
    G6B  two-block BCa acceleration for Rdelta   -> twoblock.py
    G6C  first-class zero-denominator handling   -> undefined.py, effects.py
    G12  the same, at the SOURCE of the pipeline -> undefined.py, effects.py
    G9   confounded calibration sensitivity      -> fixedpath.py

The scientific object is untouched: SAW-M, its constants, the frozen
TUNE-selected rho values, the S1 rule, the estimand, the thresholds, the twelve
gates, T6-B and T6-C are all imported or quoted, never modified.
"""
from __future__ import annotations

SOURCE_P6R_HEAD = "73ecad84620e71b68db60612a7001707a2cbd741"
CHECKPOINT_A = "fcc1355715426531c431e9390c9f12d1bad9b97c"
CHECKPOINT_B = "185bda0f63da57162309111b0ff02215f6e805d1"

__all__ = ["SOURCE_P6R_HEAD", "CHECKPOINT_A", "CHECKPOINT_B"]
