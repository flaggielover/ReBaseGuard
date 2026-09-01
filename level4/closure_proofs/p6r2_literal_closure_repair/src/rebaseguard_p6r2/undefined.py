"""First-class handling of mathematically undefined ratio comparisons.

Adjudication blockers G6C and G12: the generic analysis labelled ratios with an
exactly-zero denominator using finite effect verdicts, and the authoritative
JSON carried 56 such invalid favourable labels.  A downstream enumeration
artifact does not repair a false primary JSON, so the guard here runs **at the
source** of the analysis pipeline: no bootstrap is ever started for an undefined
comparison, and the emitted record carries JSON ``null`` everywhere a number
would otherwise be.
"""
from __future__ import annotations

import math

import numpy as np

STATUS_OK = "OK"
STATUS_UNDEFINED = "UNDEFINED_ZERO_DENOMINATOR"
VERDICT_NO_CLAIM = "NO_CLAIM"

#: verdict labels a defined effect may carry.  An undefined one may carry none.
FINITE_VERDICTS = ("INCONCLUSIVE", "STATISTICALLY_RESOLVED",
                   "PRACTICALLY_MATERIAL", "INSUFFICIENT_TAIL_EVENTS")
#: labels that must NEVER appear on an undefined comparison
FORBIDDEN_ON_UNDEFINED = ("PRACTICALLY_MATERIAL", "SIGNIFICANT", "FAVORABLE",
                          "UNFAVORABLE", "STATISTICALLY_RESOLVED",
                          "INCONCLUSIVE", "INSUFFICIENT_TAIL_EVENTS")


def denominator_is_zero(control) -> bool:
    """True when the control arm's mean is exactly zero, so the ratio is undefined."""
    c = np.asarray(control, float)
    return bool(c.size == 0 or float(c.mean()) == 0.0)


def undefined_record(metric: str, statistic: str, *, n_pairs: int,
                     method_mean: float | None = None,
                     control_mean: float = 0.0, reason: str = "") -> dict:
    """The one record shape an undefined comparison may take.

    Every numeric field is JSON ``null`` -- never ``NaN``, never ``Infinity``,
    never a finite placeholder.  ``verdict`` is ``NO_CLAIM``.
    """
    return {
        "metric": metric,
        "statistic": statistic,
        "status": STATUS_UNDEFINED,
        "relative_effect": None,
        "bca_interval": None,
        "normal_interval": None,
        "boot_sd": None,
        "p_value": None,
        "p_adjusted": None,
        "verdict": VERDICT_NO_CLAIM,
        "n_pairs": int(n_pairs),
        "n_boot": 0,
        "z0": None,
        "accel": None,
        "pair_corr": None,
        "tail_flag": None,
        "n_events_method": None,
        "n_events_control": None,
        "method_mean": (None if method_mean is None or not math.isfinite(method_mean)
                        else float(method_mean)),
        "control_mean": float(control_mean),
        "undefined_reason": reason or ("control arm mean is exactly zero, so the "
                                       "relative effect is mathematically undefined"),
    }


def is_undefined(rec: dict) -> bool:
    return rec.get("status") == STATUS_UNDEFINED


def sanitise_for_strict_json(obj):
    """Recursively replace non-finite floats with ``None``.

    Strict JSON has no ``NaN`` or ``Infinity`` tokens.  A *defined* record must
    never need this -- ``effects.py`` raises if one does -- so this exists to
    make the guarantee mechanical for incidental diagnostics such as a pair
    correlation that is undefined because an arm has zero variance.
    """
    if isinstance(obj, dict):
        return {k: sanitise_for_strict_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitise_for_strict_json(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        return f if math.isfinite(f) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def assert_no_nonfinite(obj, path="root"):
    """Raise if any non-finite float survives anywhere in ``obj``."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert_no_nonfinite(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            assert_no_nonfinite(v, f"{path}[{i}]")
    elif isinstance(obj, (np.floating, float)):
        f = float(obj)
        if not math.isfinite(f):
            raise ValueError(f"non-finite float at {path}: {f!r}")
