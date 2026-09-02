"""The single place P8R resolves a detector threshold for a production cell.

CUSUM thresholds are the frozen Stage-D D3 values and are never recalibrated.
SR thresholds are the frozen Gaussian value for ``gaussian`` and the accepted
P8R calibration otherwise.  A family whose calibration ended
``CALIBRATION_FAILED`` has **no** SR threshold: this raises rather than
silently substituting one, so a failed calibration can never leak into a
production cell.
"""
from __future__ import annotations

from pathlib import Path

import _common as C
from rebaseguard_p8r import SR_THRESHOLD_GAUSSIAN
from rebaseguard_p8r.config import RESULTS, stage_d_cusum_thresholds


class CalibrationFailed(RuntimeError):
    """Raised when a cell's SR threshold was never accepted on a holdout."""


def threshold_for(detector: str, family: str) -> tuple[float, str]:
    if detector == "cusum":
        return stage_d_cusum_thresholds()[family], "STAGE_D_D3_FROZEN"
    if detector != "sr":
        raise ValueError(f"unknown detector {detector!r}")
    if family == "gaussian":
        return SR_THRESHOLD_GAUSSIAN, "STAGE_D_D1_FROZEN"
    p = Path(RESULTS / "sr_calibration.json")
    if not p.exists():
        raise FileNotFoundError(
            "results/sr_calibration.json is absent: production may not start "
            "before the frozen calibration has been merged")
    cal = C.load_payload(p)
    for r in cal["rows"]:
        if r["family"] == family:
            if r["outcome"] == "CALIBRATION_FAILED" or r["threshold"] is None:
                raise CalibrationFailed(
                    f"SR/{family}: calibration failed on both frozen holdouts; "
                    "this cell is excluded by the frozen plan, not retuned")
            return float(r["threshold"]), f"P8R_CALIBRATION:{r['outcome']}"
    raise KeyError(family)
