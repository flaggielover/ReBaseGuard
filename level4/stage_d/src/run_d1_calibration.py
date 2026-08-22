"""D1.1 -- ARL0-match the SR chart to the frozen CUSUM(k=1/2, h=5).

Protocol (STAGE_D_PROTOCOL.md, frozen 925adecf...):
  * bisection on log A, tolerance 1e-3 in log-threshold, <= 30 iterations
  * calibration on its own seed family and its own N = 400,000
  * calibration uncertainty propagated and reported
  * THE THRESHOLD IS NEVER ADJUSTED AFTER SEEING ANY Gamma
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import bisect_threshold, measure_arl0        # noqa: E402
from stopped import CUSUM, SR                                # noqa: E402

SEED = 20261001                       # Stage D confirmatory seed family
N_CAL = 400_000                       # protocol-mandated calibration N
BATCH = 100_000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "calibration_d1.json"


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def main() -> None:
    t0 = time.time()
    print("D1.1  ARL0 calibration", flush=True)

    # --- 1. the frozen CUSUM target, measured on its own seed ---------------
    print("  [1/2] CUSUM(h=5) ARL0 target ...", flush=True)
    ss = np.random.SeedSequence([SEED, 10, 0])
    arl_c, se_c = measure_arl0(CUSUM, 5.0, n_paths=N_CAL, seed_seq=ss, batch=BATCH)
    print(f"        ARL0_CUSUM = {arl_c:.3f} +/- {se_c:.3f}", flush=True)

    # --- 2. bisect the SR threshold to that target --------------------------
    print("  [2/2] SR bisection on log A over A in [100, 3000] ...", flush=True)
    cal = bisect_threshold(SR, arl_c, lo=100.0, hi=3000.0, n_paths=N_CAL,
                           root_seed=SEED, tol_log=1e-3, max_iter=30, batch=BATCH)

    # relative error and its uncertainty, both propagated
    rel = cal["achieved_arl0"] / arl_c - 1.0
    rel_se = abs(cal["achieved_arl0"] / arl_c) * np.hypot(
        cal["arl0_se"] / cal["achieved_arl0"], se_c / arl_c)
    passed = abs(rel) <= 0.01

    out = {
        "gate": "D1.1",
        "criterion": "|ARL0_SR / ARL0_CUSUM - 1| <= 0.01",
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "seed_family": SEED,
        "n_paths_calibration": N_CAL,
        "cusum": {"threshold_h": 5.0, "arl0": arl_c, "arl0_se": se_c,
                  "seed": [SEED, 10, 0], "n_paths": N_CAL},
        "sr": cal,
        "relative_error": rel,
        "relative_error_se": float(rel_se),
        "criterion_met": bool(passed),
        "evidence_status": "NEW-NUMERICAL",
        "note": ("Monte Carlo calibration, not a certified quantity. The SR "
                 "threshold is expressed in NATURAL units A; the recursion "
                 "compares log R against log A."),
        "git_head": _git(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n  SR threshold A   = {cal['threshold']:.6f}", flush=True)
    print(f"  ARL0_SR          = {cal['achieved_arl0']:.3f} "
          f"+/- {cal['arl0_se']:.3f}  (N = {cal['n_paths_final']:,})", flush=True)
    print(f"  ARL0_CUSUM       = {arl_c:.3f} +/- {se_c:.3f}", flush=True)
    print(f"  relative error   = {rel:+.5f} +/- {rel_se:.5f}", flush=True)
    print(f"  D1.1 criterion   = {'MET' if passed else 'NOT MET'}", flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
