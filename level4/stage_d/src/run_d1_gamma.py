"""D1.2 / D1.3 -- Gamma_SR at m=1 and the ARL0-matched SR-vs-CUSUM excess.

The SR threshold is read from calibration_d1.json and is NEVER recomputed or
adjusted here: this module sees Gamma, so by protocol it may not touch the
threshold.
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
from stopped import CUSUM, SR, simulate_stopped              # noqa: E402

SEED = 20261001
N_TOTAL = 2_000_000
N_BATCHES = 20
BATCH = N_TOTAL // N_BATCHES
ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "results" / "calibration_d1.json"
OUT = ROOT / "results" / "d1_gamma.json"
Z = 1.959964


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def run(detector: str, threshold: float, key: int) -> dict:
    ss = np.random.SeedSequence([SEED, key, 0])
    stats, batch_g, batch_arl = None, [], []
    t0 = time.time()
    for b, child in enumerate(ss.spawn(N_BATCHES)):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=detector, threshold=threshold, e=0.0,
                             n_paths=BATCH, L=2, m_grid=np.array([1]), rng=rng)
        batch_g.append(float(s.gamma_m("A")[0]))
        batch_arl.append(s.arl)
        stats = s if stats is None else stats.combine(s)
        print(f"  {detector:5s} batch {b + 1:2d}/{N_BATCHES}  "
              f"G={batch_g[-1]:7.4f}  ({time.time() - t0:5.1f}s)", flush=True)
    g = float(stats.gamma_m("A")[0])
    se = float(stats.gamma_m_se("A")[0])
    bg = np.array(batch_g)
    se_batch = float(bg.std(ddof=1) / np.sqrt(N_BATCHES))
    return {"detector": detector, "threshold": threshold, "seed": [SEED, key, 0],
            "n_cycles": int(stats.n), "arl0": float(stats.arl),
            "gamma": g, "se": se, "se_batch_means": se_batch,
            "ci_normal": [g - Z * se, g + Z * se],
            "ci_batch": [g - Z * se_batch, g + Z * se_batch],
            "batch_means": batch_g, "batch_arl": batch_arl}


def main() -> None:
    t0 = time.time()
    cal = json.loads(CAL.read_text())
    A = cal["sr"]["threshold"]
    print(f"D1.2/D1.3  Gamma at m=1.  SR threshold A = {A:.6f} "
          f"(frozen by D1.1, not revisited)", flush=True)

    sr = run(SR, A, 30)
    cu = run(CUSUM, 5.0, 31)

    # D1.2 -- lower 95% bound of Gamma_SR strictly above 2
    d12_pass = sr["ci_normal"][0] > 2.0 and sr["ci_batch"][0] > 2.0

    # D1.3 -- independent samples, so the difference SE adds in quadrature
    diff = sr["gamma"] - cu["gamma"]
    diff_se = float(np.hypot(sr["se"], cu["se"]))
    diff_ci = [diff - Z * diff_se, diff + Z * diff_se]
    d13_pass = diff_ci[0] > 0.0 or diff_ci[1] < 0.0

    out = {
        "gate": "D1.2/D1.3",
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "sr_threshold_from_calibration": A,
        "sr": sr, "cusum": cu,
        "d1_2": {"criterion": "lower 95% bound of Gamma_SR strictly > 2",
                 "lower_bound_normal": sr["ci_normal"][0],
                 "lower_bound_batch": sr["ci_batch"][0],
                 "criterion_met": bool(d12_pass),
                 "gamma_sr_exceeds_4": bool(sr["ci_normal"][0] > 4.0),
                 "d1_4_gate": ("D1.4 runs" if d12_pass and sr["ci_normal"][0] > 4.0
                               else "D1.4 NOT run")},
        "d1_3": {"criterion": "95% CI for Gamma_SR - Gamma_CUSUM excludes 0",
                 "difference": diff, "se": diff_se, "ci": diff_ci,
                 "pairing": ("INDEPENDENT samples, unpaired difference. CRN "
                             "pairing is carried as an adversarial variant, not "
                             "as the primary estimator."),
                 "criterion_met": bool(d13_pass)},
        "arl0_match_check": {
            "arl0_sr": sr["arl0"], "arl0_cusum": cu["arl0"],
            "ratio": sr["arl0"] / cu["arl0"]},
        "evidence_status": "NEW-NUMERICAL",
        "note": ("Monte Carlo. Not certified. Two detectors agreeing is "
                 "two-detector replication, NOT detector-independence."),
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n  Gamma_SR    = {sr['gamma']:.4f} +/- {sr['se']:.4f}  "
          f"95% CI [{sr['ci_normal'][0]:.4f}, {sr['ci_normal'][1]:.4f}]", flush=True)
    print(f"  Gamma_CUSUM = {cu['gamma']:.4f} +/- {cu['se']:.4f}", flush=True)
    print(f"  ARL0: SR {sr['arl0']:.2f} vs CUSUM {cu['arl0']:.2f}", flush=True)
    print(f"  D1.2 (lower bound > 2): {'MET' if d12_pass else 'NOT MET'}", flush=True)
    print(f"  D1.3 difference = {diff:+.4f} +/- {diff_se:.4f}  "
          f"CI [{diff_ci[0]:+.4f}, {diff_ci[1]:+.4f}]: "
          f"{'MET' if d13_pass else 'NOT MET'}", flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
