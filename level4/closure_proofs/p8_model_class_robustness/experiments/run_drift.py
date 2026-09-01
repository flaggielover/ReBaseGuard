"""E4: drift-pattern robustness -- step and ramp detection delay.

Both patterns are applied at a re-baselining instant (the Stage-D / P7
convention).  The delay of interest is the length of the first cycle that
begins after the change, measured against the same-cell in-control cycle.

Usage:  run_drift.py <detector> <family>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.chain import shift_schedule, simulate_chain     # noqa: E402
from rebaseguard_p8.config import RESULTS                           # noqa: E402
from run_gamma_matrix import threshold_for                          # noqa: E402

M_DRIFT = (1, 5)
RHOS = (0.0, 1.0)
STEPS = (0.5, 1.0, 2.0)
RAMPS = (0.02, 0.05)
SHIFT_CYCLE = 20            # == burn_in: the change lands at a re-baselining
TAIL_FLOOR = 200            # preregistered minimum tail events per arm


def delay_stats(r, shift_cycle: int) -> dict:
    d = r.tau[:, shift_cycle].astype(float)
    n = d.size
    n_tail = int((d > 100).sum())
    return {"mean": float(d.mean()),
            "se": float(d.std(ddof=1) / np.sqrt(n)),
            "q50": float(np.quantile(d, 0.5)),
            "q95": float(np.quantile(d, 0.95)),
            "p_gt_100": float((d > 100).mean()),
            "n_tail_events": n_tail,
            "tail_label": ("OK" if n_tail >= TAIL_FLOOR
                           else "INSUFFICIENT_TAIL_EVENTS"),
            "n": int(n)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("detector")
    ap.add_argument("family")
    ap.add_argument("--reps", type=int, default=6000)
    ap.add_argument("--cycles", type=int, default=24)
    ap.add_argument("--tag", default="E4")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    d = RESULTS / "drift"
    d.mkdir(exist_ok=True)
    dest = d / f"{a.tag}_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present; pass --force to redo)")
        return
    thr, prov = threshold_for(a.detector, a.family)
    experiment = f"p8_drift_{a.tag}"
    rows, t0 = [], time.time()
    for m in M_DRIFT:
        for rho in RHOS:
            specs = [("none", 0.0, 0.0)]
            specs += [("step", s, 0.0) for s in STEPS]
            specs += [("ramp", 0.0, s) for s in RAMPS]
            for pattern, size, slope in specs:
                sched = shift_schedule(a.cycles, pattern, size, SHIFT_CYCLE,
                                       slope)
                r = simulate_chain(experiment=experiment, family=a.family,
                                   detector=a.detector, threshold=thr, m=m,
                                   rho=rho, n_rep=a.reps, n_cycles=a.cycles,
                                   burn_in=SHIFT_CYCLE, shift=sched)
                st = delay_stats(r, SHIFT_CYCLE)
                rows.append({"m": m, "rho": rho, "pattern": pattern,
                             "size": size, "slope": slope,
                             "shift_cycle": SHIFT_CYCLE,
                             "pre_change_arl": float(
                                 r.tau[:, :SHIFT_CYCLE].mean()),
                             "ref_mse_pre": float(
                                 (r.e_start[:, :SHIFT_CYCLE] ** 2).mean()),
                             "delay": st})
                print(f"  m={m} rho={rho} {pattern}({size or slope}) "
                      f"delay={st['mean']:.2f} q95={st['q95']:.0f} "
                      f"[{time.time()-t0:.0f}s]", flush=True)
    out = {"schema": "rebaseguard.p8.drift.v1", "tag": a.tag,
           "experiment_tag": experiment, "detector": a.detector,
           "family": a.family, "threshold": thr, "threshold_provenance": prov,
           "n_replicates": a.reps, "n_cycles": a.cycles,
           "shift_cycle": SHIFT_CYCLE, "tail_floor": TAIL_FLOOR,
           "seconds": time.time() - t0, "rows": rows}
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(f"DONE drift {a.detector}/{a.family} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
