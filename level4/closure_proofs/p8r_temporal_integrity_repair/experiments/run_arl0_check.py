"""S3: measured in-control ARL at the frozen thresholds, all cells.

This is a *diagnostic* measurement, never a tuning input: the CUSUM thresholds
are Stage-D D3's and are not recalibrated by P8R, and the SR thresholds were
already fixed by the frozen calibration and accepted on their holdout before
this ran.  It is therefore drawn from ``PRODUCTION`` addresses, which are
disjoint from every calibration class.

Usage:  run_arl0_check.py
"""
from __future__ import annotations

import time

import _common as C                                              # noqa: E402
from rebaseguard_p8r.addressing import PROD_ARL0_CHECK           # noqa: E402
from rebaseguard_p8r.calibrate import arl0                       # noqa: E402
from rebaseguard_p8r.config import (ARL0_CHECK_ROW_BLOCKS,       # noqa: E402
                                     DETECTORS, FAMILIES, RESULTS,
                                     ROWS_PER_BLOCK, S3_ARL0_REL_MAX,
                                     stage_d_target_arl0)
from thresholds import CalibrationFailed, threshold_for           # noqa: E402


def main() -> None:
    target = stage_d_target_arl0()
    rows, t0 = [], time.time()
    for det in DETECTORS:
        for fam in FAMILIES:
            try:
                thr, prov = threshold_for(det, fam)
            except CalibrationFailed as e:
                rows.append({"detector": det, "family": fam,
                             "status": "EXCLUDED_CALIBRATION_FAILED",
                             "reason": str(e)})
                continue
            a, se, n = arl0(experiment=PROD_ARL0_CHECK, family=fam,
                            detector=det, threshold=thr, batch=0,
                            n_row_blocks=ARL0_CHECK_ROW_BLOCKS)
            rel = abs(a - target) / target
            rows.append({"detector": det, "family": fam, "status": "OK",
                         "threshold": thr, "threshold_provenance": prov,
                         "arl0": a, "se": se, "n": int(n),
                         "relative_error": rel,
                         "z": (a - target) / se if se > 0 else None,
                         "within_1pct": bool(rel <= S3_ARL0_REL_MAX)})
            print(f"  {det}/{fam:11s} arl0={a:.3f}+-{se:.3f} rel={rel:.5f} "
                  f"[{time.time() - t0:.0f}s]", flush=True)
    payload = {"target_arl0": target,
               "row_blocks": ARL0_CHECK_ROW_BLOCKS,
               "cycles_per_cell": ARL0_CHECK_ROW_BLOCKS * ROWS_PER_BLOCK,
               "tolerance": S3_ARL0_REL_MAX,
               "seconds": time.time() - t0, "rows": rows}
    C.write(RESULTS / "arl0_check.json",
            C.envelope(generator="run_arl0_check.py",
                       schema="rebaseguard.p8r.arl0-check.v1",
                       tags=[PROD_ARL0_CHECK], payload=payload))
    print("DONE arl0_check")


if __name__ == "__main__":
    main()
