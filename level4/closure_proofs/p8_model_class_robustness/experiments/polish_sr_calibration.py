"""Refine a P8 SR threshold until it meets the preregistered G2 tolerance.

The search phase uses 163,840-cycle evaluations, whose own relative standard
error is about 0.25%; that is not enough resolution to land inside the 0.5%
gate reliably.  This phase does the obvious thing: evaluate at the large
verification sample (whose relative SE is ~0.15%), apply the same proportional
correction, and repeat.  ``ARL_0`` is asymptotically linear in the SR natural
threshold, so one or two steps suffice.

This changes the **procedure** by which a threshold is found.  It does not
change gate `G2`, whose 0.5% tolerance and 1,024,000-cycle verification sample
are unchanged, and it does not touch any frozen CUSUM threshold.

Usage:  polish_sr_calibration.py <family>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8 import SR                                       # noqa: E402
from rebaseguard_p8.calibrate import arl0                           # noqa: E402
from rebaseguard_p8.config import RESULTS, stage_d_target_arl0      # noqa: E402

EXPERIMENT = "p8_sr_calibration"
POLISH_ROW_BLOCKS = 150          # 614,400 cycles; relative SE ~0.15%
VERIFY_ROW_BLOCKS = 250          # 1,024,000 cycles, as declared for G2
ACCEPT = 0.0025                  # stop polishing once inside 0.25%
MAX_POLISH = 4
OUT = RESULTS / "sr_cal"


def main() -> None:
    fam = sys.argv[1]
    target = stage_d_target_arl0()
    cal = json.loads((OUT / f"{fam}.json").read_text())
    if fam == "gaussian":
        print("gaussian threshold is frozen; nothing to polish")
        return
    thr = float(cal["threshold"])
    trace, t0 = list(cal.get("polish_trace", [])), time.time()
    for it in range(MAX_POLISH):
        a, se, n = arl0(experiment=EXPERIMENT + "_polish", family=fam,
                        detector=SR, threshold=thr, batch=2_000 + it,
                        n_row_blocks=POLISH_ROW_BLOCKS)
        rel = abs(a - target) / target
        trace.append({"iter": it, "threshold": thr, "arl0": a, "se": se,
                      "n": n, "batch": 2_000 + it, "relative_error": rel})
        print(f"  polish {it}: A={thr:.4f} arl0={a:.2f}+-{se:.2f} rel={rel:.5f}",
              flush=True)
        if rel <= ACCEPT:
            break
        thr = thr * (target / a)
    cal["threshold"] = thr
    cal["polish_trace"] = trace
    cal["n_polish_iterations"] = len(trace)
    cal["polish_cycles_per_iteration"] = POLISH_ROW_BLOCKS * 4096
    cal["procedure"] = (cal["procedure"] + "; then refined at "
                        f"{POLISH_ROW_BLOCKS * 4096} cycles per step with the "
                        "same proportional correction until within 0.25%")
    a, se, n = arl0(experiment=EXPERIMENT + "_verify", family=fam, detector=SR,
                    threshold=thr, batch=7, n_row_blocks=VERIFY_ROW_BLOCKS)
    cal.update({"verification_arl0": a, "verification_se": se,
                "verification_n": n,
                "verification_relative_error": abs(a - target) / target,
                "verification_z": (a - target) / se if se > 0 else None,
                "polish_seconds": time.time() - t0})
    (OUT / f"{fam}.json").write_text(json.dumps(cal, indent=1) + "\n")
    print(f"{fam:11s} A={thr:.6f} arl0={a:.3f}+-{se:.3f} "
          f"rel={cal['verification_relative_error']:.5f}", flush=True)


if __name__ == "__main__":
    main()
