"""Level-4 Priority-8 model-class robustness campaign (isolated namespace).

P8 owns the detector-family / distribution-family / drift-pattern robustness
matrix handed over by P7 (``p7/CLOSURE_REPORT.md`` section 6, ``p7/README.md``
section Scope, ``p7/EXPERIMENT_DESIGN.md`` section 1) and by the P6 pre-design
exclusion ``X5``.

Nothing in this package writes outside
``level4/closure_proofs/p8_model_class_robustness/``.  It imports the frozen
CUSUM recurrence read-only from ``level4/src/rebaseguard_level4/frozen.py`` and
restates the frozen SR recurrence exactly as ``level4/stage_d/src/stopped.py``
and ``p7/detectors.py`` do.
"""
CUSUM = "cusum"
SR = "sr"

#: frozen Gaussian operating point (stage_d/results/d3_nongaussian.json)
TARGET_ARL0 = 465.50394

#: frozen Gaussian thresholds
CUSUM_THRESHOLD_GAUSSIAN = 5.0                    # H_FROZEN
SR_THRESHOLD_GAUSSIAN = 520.886133602749          # stage_d calibration_d1.json

K_FROZEN = 0.5
