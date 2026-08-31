"""Level-4 Priority-7 statistical-consequence campaign (isolated namespace).

Nothing in this package is imported by P1, P2, P3 or P4.  It imports the frozen
CUSUM recurrence from ``level4/src/rebaseguard_level4/frozen.py`` read-only and
restates the frozen SR recurrence exactly as ``level4/stage_d/src/stopped.py``
does, so that P7 measures the same monitoring object the closed derivative
theorems are about.
"""
CUSUM = "cusum"
SR = "sr"
SR_THRESHOLD = 520.886133602749   # level4/stage_d/results/calibration_d1.json
CUSUM_THRESHOLD = 5.0             # H_FROZEN
