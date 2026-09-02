"""Level-4 Priority-8 **repair** campaign (`P8R`), isolated namespace.

P8R reruns the P8 model-class robustness question under a genuinely
pre-anchored, leakage-free protocol.  It is **not** a rewrite of P8: the
original `p8_model_class_robustness/` tree, its protocol, its results, its
adjudication and its authoritative `P8 = FAIL` verdict are historical protected
artifacts and are never modified by anything in this package.

Nothing here writes outside
``level4/closure_proofs/p8r_temporal_integrity_repair/``.  The frozen CUSUM
recurrence is imported read-only from
``level4/src/rebaseguard_level4/frozen.py``; the frozen SR recurrence is
restated exactly as ``level4/stage_d/src/stopped.py`` states it.
"""
CUSUM = "cusum"
SR = "sr"

#: frozen Gaussian operating point (stage_d/results/d3_nongaussian.json).
#: Re-read at run time by ``config.stage_d_target_arl0``; this literal exists
#: only for the equality assertion in ``tests/test_frozen_inheritance.py``.
TARGET_ARL0 = 465.50394

#: frozen Gaussian thresholds, inherited unchanged
CUSUM_THRESHOLD_GAUSSIAN = 5.0                    # H_FROZEN
SR_THRESHOLD_GAUSSIAN = 520.886133602749          # stage_d calibration_d1.json

K_FROZEN = 0.5
