"""Consistency check raised by the D1.4 scan, not a protocol gate.

The D1.4 coarse scan found the SR and CUSUM induced maps agreeing to <= 3 SE at
every e >= 0.4, while D1.3 found Gamma_SR - Gamma_CUSUM = +1.47 (37 SE). Those
are only compatible if the two maps separate near e = 0 -- since
F'(0) = 1 - Gamma -- and have merged by e = 0.4.

This measures F'(0) for both detectors directly and compares each against its
own 1 - Gamma. Steps and the Richardson-as-diagnostic rule follow
notes/D2_3_STEP_PRECOMMIT.md.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopped import CUSUM, SR, simulate_stopped              # noqa: E402

SEED = 20261001
N_POINT = 500_000
BATCH = 250_000
STEPS = [0.025, 0.05]
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d1_map_slope_check.json"
M1 = np.array([1], dtype=np.int64)
Z = 1.959964


def F_at(detector, threshold, e, key):
    ss = np.random.SeedSequence(key)
    stats = None
    for child in ss.spawn(N_POINT // BATCH):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=detector, threshold=threshold, e=e,
                             n_paths=BATCH, L=2, m_grid=M1, rng=rng)
        stats = s if stats is None else stats.combine(s)
    return float(stats.induced_map(e)[0]), float(stats.induced_map_se()[0])


def slope(detector, threshold, tag):
    out = {}
    for si, h in enumerate(STEPS):
        fp, sp = F_at(detector, threshold, +h, [SEED, 60, tag, si, 0])
        fm, sm = F_at(detector, threshold, -h, [SEED, 60, tag, si, 1])
        out[h] = ((fp - fm) / (2 * h), float(np.hypot(sp, sm)) / (2 * h))
        print(f"    {detector:5s} h={h:<6} F'(0)={out[h][0]:9.4f} "
              f"+/- {out[h][1]:.4f}", flush=True)
    d1, s1 = out[0.025]
    d2, s2 = out[0.05]
    rich = (4 * d1 - d2) / 3
    rich_se = float(np.hypot((4 / 3) * s1, (1 / 3) * s2))
    return {"by_step": {str(h): {"deriv": out[h][0], "se": out[h][1]}
                        for h in STEPS},
            "richardson": rich, "richardson_se": rich_se}


def main():
    t0 = time.time()
    d1 = json.loads((ROOT / "results" / "d1_gamma.json").read_text())
    A = d1["sr_threshold_from_calibration"]
    print("Consistency check: F'(0) vs 1 - Gamma, per detector", flush=True)

    res = {}
    for det, thr, tag, key in ((SR, A, 0, "sr"), (CUSUM, 5.0, 1, "cusum")):
        sl = slope(det, thr, tag)
        g, gse = d1[key]["gamma"], d1[key]["se"]
        target = 1.0 - g
        disc = sl["richardson"] - target
        comb = float(np.hypot(sl["richardson_se"], gse))
        res[key] = {**sl, "gamma": g, "gamma_se": gse,
                    "target_1_minus_gamma": target,
                    "richardson_discrepancy": disc,
                    "combined_se": comb, "n_combined_se": disc / comb,
                    "agrees_within_3se": bool(abs(disc) <= 3 * comb)}

    sep = res["cusum"]["richardson"] - res["sr"]["richardson"]
    sep_se = float(np.hypot(res["cusum"]["richardson_se"],
                            res["sr"]["richardson_se"]))
    gap = d1["d1_3"]["difference"]
    gap_se = d1["d1_3"]["se"]
    agree = abs(sep - gap) <= 3 * float(np.hypot(sep_se, gap_se))

    out = {"check": "induced-map slope at 0 vs 1 - Gamma, per detector",
           "role": "CONSISTENCY CHECK, not a protocol gate",
           "n_cycles_per_point": N_POINT, "steps": STEPS, "seed_family": SEED,
           "sr": res["sr"], "cusum": res["cusum"],
           "slope_separation": {
               "F0_cusum_minus_F0_sr": sep, "se": sep_se,
               "gamma_sr_minus_gamma_cusum": gap, "gamma_gap_se": gap_se,
               "these_should_be_equal_because": "F'(0) = 1 - Gamma",
               "agrees_within_3se": bool(agree)},
           "richardson_note": ("Richardson is used here because D2.3 established "
                               "the raw central difference carries O(h^2) bias; "
                               "it remains a diagnostic, not a certified value."),
           "evidence_status": "NEW-NUMERICAL",
           "python": platform.python_version(), "numpy": np.__version__,
           "elapsed_s": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    for k in ("sr", "cusum"):
        r = res[k]
        print(f"\n  {k.upper():5s} F'(0) [Richardson] = {r['richardson']:9.4f} "
              f"+/- {r['richardson_se']:.4f}")
        print(f"        1 - Gamma          = {r['target_1_minus_gamma']:9.4f} "
              f"+/- {r['gamma_se']:.4f}")
        print(f"        discrepancy        = {r['richardson_discrepancy']:+9.4f} "
              f"({r['n_combined_se']:+.2f} SE)  "
              f"{'OK' if r['agrees_within_3se'] else 'MISMATCH'}")
    print(f"\n  slope separation  F'_cusum(0) - F'_sr(0) = {sep:+.4f} +/- {sep_se:.4f}")
    print(f"  Gamma gap         Gamma_sr - Gamma_cusum  = {gap:+.4f} +/- {gap_se:.4f}")
    print(f"  consistent: {agree}")
    print(f"  -> {OUT}  ({out['elapsed_s']} s)")


if __name__ == "__main__":
    main()
