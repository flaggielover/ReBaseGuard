"""G2: calibrate the frozen SR threshold per innovation family.

The repository supplies no non-Gaussian SR threshold; this is P8's only new
calibration and is declared in ``P8_DEFINITION_AUDIT.md`` section 7 before any
result existed.  Gaussian SR keeps the frozen ``A = 520.886133602749``
unchanged and is only re-verified.

Usage:  run_sr_calibration.py <family>     -> results/sr_cal/<family>.json
        run_sr_calibration.py --merge      -> results/sr_calibration.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8 import SR, SR_THRESHOLD_GAUSSIAN                # noqa: E402
from rebaseguard_p8.calibrate import arl0, calibrate                # noqa: E402
from rebaseguard_p8.config import (                                 # noqa: E402
    FAMILIES, RESULTS, stage_d_target_arl0)

EXPERIMENT = "p8_sr_calibration"
SEARCH_ROW_BLOCKS = 40           # 163,840 cycles per iteration
VERIFY_ROW_BLOCKS = 250          # 1,024,000 cycles; relative SE ~0.1%
OUT = RESULTS / "sr_cal"


def one(fam: str) -> dict:
    target = stage_d_target_arl0()
    t0 = time.time()
    if fam == "gaussian":
        cal = {"family": fam, "detector": SR, "target_arl0": target,
               "threshold": SR_THRESHOLD_GAUSSIAN,
               "label": "FROZEN_NOT_RECALIBRATED",
               "procedure": "read from stage_d/results/calibration_d1.json",
               "trace": [], "n_iterations": 0}
    else:
        cal = calibrate(experiment=EXPERIMENT, family=fam, detector=SR,
                        target=target, start=SR_THRESHOLD_GAUSSIAN,
                        n_row_blocks=SEARCH_ROW_BLOCKS)
    a, se, n = arl0(experiment=EXPERIMENT + "_verify", family=fam, detector=SR,
                    threshold=cal["threshold"], batch=7,
                    n_row_blocks=VERIFY_ROW_BLOCKS)
    cal.update({"verification_arl0": a, "verification_se": se,
                "verification_n": n,
                "verification_relative_error": abs(a - target) / target,
                "verification_z": (a - target) / se if se > 0 else None,
                "seconds": time.time() - t0})
    OUT.mkdir(exist_ok=True)
    (OUT / f"{fam}.json").write_text(json.dumps(cal, indent=1) + "\n")
    print(f"{fam:11s} A={cal['threshold']:.6f} arl0={a:.3f}+-{se:.3f} "
          f"rel={cal['verification_relative_error']:.5f} "
          f"iters={cal['n_iterations']} [{cal['seconds']:.0f}s]", flush=True)
    return cal


def merge() -> None:
    rows = [json.loads((OUT / f"{f}.json").read_text()) for f in FAMILIES]
    non_g = [r for r in rows if r["family"] != "gaussian"]
    out = {"schema": "rebaseguard.p8.sr-calibration.v1",
           "experiment_tag": EXPERIMENT,
           "target_arl0": stage_d_target_arl0(),
           "search_cycles_per_iteration": SEARCH_ROW_BLOCKS * 4096,
           "verification_cycles": VERIFY_ROW_BLOCKS * 4096,
           "rows": rows,
           "gates": {
               "G2_max_relative_error_non_gaussian":
                   max(r["verification_relative_error"] for r in non_g),
               "G2_pass": bool(all(r["verification_relative_error"] <= 0.005
                                   for r in non_g)),
               "gaussian_frozen_relative_error":
                   [r for r in rows if r["family"] == "gaussian"][0]
                   ["verification_relative_error"]}}
    (RESULTS / "sr_calibration.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["gates"], indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "--merge":
        merge()
    else:
        one(sys.argv[1])
