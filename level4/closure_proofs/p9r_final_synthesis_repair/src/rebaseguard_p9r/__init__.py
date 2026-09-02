"""Level-4 Priority-9 **repair** campaign (P9R) — isolated namespace.

P9R exists to repair the defects that the authoritative independent
adjudication of Priority 9 recorded at commit
``a3e3cabc30c4508b866736aeede54db17e5e1fcc``.  It does **not** rewrite P9.
``level4/closure_proofs/p9_final_synthesis/`` is protected historical
evidence and every P9R integrity gate asserts its bytes are unchanged.

This package imports nothing from P1-P9.  The frozen detector recurrences are
*reconstructed* here from the authoritative specifications
(``level4/src/rebaseguard_level4/frozen.py`` for CUSUM semantics,
``level4/stage_d/src/stopped.py::_sr_update`` and
``level4/closure_proofs/sr_derivative/src/rebaseguard_sr_derivative/log_sr.py``
for the symmetric two-chart SR recurrence) and are checked against
hand-computed algebra in ``tests/test_sr_recurrence.py``.

The single most important difference from P9: the SR state variable stored
between steps is ``y = log(1 + R)`` with ``y_0 = 0`` (no headstart, ``R_0 = 0``),
and the alarm test is applied to ``ell = y + z - 1/2 = log R``.  P9 stored
``ell`` but initialised it to ``0`` and then applied ``logaddexp(0, .)`` *before*
adding the increment, which shifts the first update of every cycle upward by
exactly ``log 2``.
"""

CUSUM = "cusum"
SR = "sr"

#: frozen CUSUM constants (level4/src/rebaseguard_level4/frozen.py)
K_FROZEN = 0.5
H_FROZEN = 5.0

#: frozen SR threshold in NATURAL units
#: (level4/closure_proofs/p7_statistical_consequences/src/rebaseguard_p7/__init__.py,
#:  itself read from level4/stage_d/results/calibration_d1.json)
SR_THRESHOLD = 520.886133602749

DETECTORS = (CUSUM, SR)

__all__ = [
    "CUSUM", "SR", "DETECTORS",
    "K_FROZEN", "H_FROZEN", "SR_THRESHOLD",
]
