"""E2: the frozen SR threshold calibration, one family per invocation.

The repository supplies no non-Gaussian SR threshold, so this is P8R's only new
calibration.  Gaussian SR keeps the frozen ``A = 520.886133602749`` and is only
re-verified on the held-out sample.

The whole procedure -- budgets, iteration counts, update rule, acceptance
tolerance, retry ladder, address classes -- is frozen in
``src/rebaseguard_p8r/calibrate.py`` and ``config.py`` and digested at the
temporal anchor.  This driver adds no policy of its own.

Usage:  run_calibration.py <family>
        run_calibration.py --merge
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import _common as C                                              # noqa: E402
from rebaseguard_p8r import SR_THRESHOLD_GAUSSIAN                # noqa: E402
from rebaseguard_p8r.addressing import (CAL_SEARCH_ARL0,         # noqa: E402
                                        CAL_VERIFY_1_ARL0,
                                        CAL_VERIFY_2_ARL0)
from rebaseguard_p8r.calibrate import (calibrate_family,         # noqa: E402
                                       declared_budget, executed_budget,
                                       _verify)
from rebaseguard_p8r.config import (CAL_TOLERANCE,               # noqa: E402
                                     CAL_VERIFY_1_BATCH, FAMILIES, RESULTS,
                                     stage_d_target_arl0)

OUT = RESULTS / "cal"
TAGS = (CAL_SEARCH_ARL0, CAL_VERIFY_1_ARL0, CAL_VERIFY_2_ARL0)


def one(fam: str) -> dict:
    target = stage_d_target_arl0()
    t0 = time.time()
    if fam == "gaussian":
        # Frozen, not recalibrated: no search happens, so there is nothing to
        # leak.  The held-out sample is still drawn, and reported, so that the
        # Gaussian anchor is measured on the same footing as the others.
        v1 = _verify(experiment=CAL_VERIFY_1_ARL0, family=fam,
                     threshold=SR_THRESHOLD_GAUSSIAN,
                     batch=CAL_VERIFY_1_BATCH, target=target)
        rec = {"family": fam, "detector": "sr", "target_arl0": target,
               "start_threshold": SR_THRESHOLD_GAUSSIAN,
               "threshold": SR_THRESHOLD_GAUSSIAN,
               "label": "FROZEN_NOT_RECALIBRATED",
               "outcome": "FROZEN_NOT_RECALIBRATED",
               "accepted_by": None,
               "search_trace": [], "retry_trace": [],
               "verify_1": v1, "verify_2": None,
               "declared_budget": declared_budget()}
        rec["executed_budget"] = executed_budget(rec)
        rec["budget_matches_declaration"] = True
    else:
        rec = calibrate_family(family=fam, target=target,
                               start=SR_THRESHOLD_GAUSSIAN)
    rec["seconds"] = time.time() - t0
    C.write(OUT / f"{fam}.json",
            C.envelope(generator="run_calibration.py",
                       schema="rebaseguard.p8r.sr-calibration-cell.v1",
                       tags=TAGS, payload=rec))
    v = rec["verify_2"] or rec["verify_1"]
    print(f"{fam:11s} outcome={rec['outcome']:24s} "
          f"A={rec['threshold'] if rec['threshold'] else float('nan'):.6f} "
          f"arl0={v['arl0']:.3f}+-{v['se']:.3f} rel={v['relative_error']:.5f} "
          f"[{rec['seconds']:.0f}s]", flush=True)
    return rec


def merge() -> None:
    rows = [C.load_payload(OUT / f"{f}.json") for f in FAMILIES]
    non_g = [r for r in rows if r["family"] != "gaussian"]
    payload = {
        "target_arl0": stage_d_target_arl0(),
        "declared_budget": declared_budget(),
        "rows": rows,
        "outcomes": {r["family"]: r["outcome"] for r in rows},
        "thresholds": {r["family"]: r["threshold"] for r in rows},
        "calibration_failed_families":
            [r["family"] for r in rows if r["outcome"] == "CALIBRATION_FAILED"],
        "used_retry_families":
            [r["family"] for r in rows if r["outcome"] == "ACCEPTED_VERIFY_2"],
        "max_relative_error_non_gaussian":
            max((r["verify_2"] or r["verify_1"])["relative_error"]
                for r in non_g),
        "gaussian_frozen_relative_error":
            rows[0]["verify_1"]["relative_error"],
        "all_budgets_match_declaration":
            bool(all(r["budget_matches_declaration"] for r in rows)),
        "tolerance": CAL_TOLERANCE,
    }
    C.write(RESULTS / "sr_calibration.json",
            C.envelope(generator="run_calibration.py",
                       schema="rebaseguard.p8r.sr-calibration.v1",
                       tags=TAGS, payload=payload))
    print(json.dumps({k: payload[k] for k in
                      ("outcomes", "calibration_failed_families",
                       "used_retry_families",
                       "max_relative_error_non_gaussian",
                       "all_budgets_match_declaration")}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "--merge":
        merge()
    else:
        one(sys.argv[1])
