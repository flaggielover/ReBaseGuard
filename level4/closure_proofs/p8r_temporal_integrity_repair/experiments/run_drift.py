"""E4: drift-pattern robustness -- step and ramp detection delay.

Both patterns are applied at a re-baselining instant (the Stage-D / P7
convention).  The delay of interest is the length of the first cycle that begins
after the change, measured against the same-cell in-control cycle.

Usage:  run_drift.py <detector> <family>
"""
from __future__ import annotations

import argparse
import time

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.addressing import PROD_DRIFT_E4             # noqa: E402
from rebaseguard_p8r.chain import shift_schedule, simulate_chain  # noqa: E402
from rebaseguard_p8r.config import (E4_CYCLES, E4_REPLICATES,    # noqa: E402
                                     E4_SHIFT_CYCLE, M_CHAIN, RAMP_SLOPES,
                                     RESULTS, SHIFTS, TAIL_EVENT_FLOOR)
from thresholds import CalibrationFailed, threshold_for           # noqa: E402

RHOS = (0.0, 1.0)


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
            "tail_label": ("OK" if n_tail >= TAIL_EVENT_FLOOR
                           else "INSUFFICIENT_TAIL_EVENTS"),
            "n": int(n)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("detector")
    ap.add_argument("family")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    dest = RESULTS / "drift" / f"E4_{a.detector}_{a.family}.json"
    if dest.exists() and not a.force:
        print(f"SKIP {dest.name} (already present)")
        return
    try:
        thr, prov = threshold_for(a.detector, a.family)
    except CalibrationFailed as e:
        C.write(dest, C.envelope(
            generator="run_drift.py", schema="rebaseguard.p8r.drift.v1",
            tags=[PROD_DRIFT_E4],
            payload={"detector": a.detector, "family": a.family,
                     "status": "EXCLUDED_CALIBRATION_FAILED",
                     "reason": str(e), "rows": []}))
        print(f"EXCLUDED drift {a.detector}/{a.family}: {e}")
        return

    rows, t0 = [], time.time()
    for m in M_CHAIN:
        for rho in RHOS:
            specs = [("none", 0.0, 0.0)]
            specs += [("step", s, 0.0) for s in SHIFTS]
            specs += [("ramp", 0.0, s) for s in RAMP_SLOPES]
            for pattern, size, slope in specs:
                sched = shift_schedule(E4_CYCLES, pattern, size,
                                       E4_SHIFT_CYCLE, slope)
                r = simulate_chain(experiment=PROD_DRIFT_E4, family=a.family,
                                   detector=a.detector, threshold=thr, m=m,
                                   rho=rho, n_rep=E4_REPLICATES,
                                   n_cycles=E4_CYCLES,
                                   burn_in=E4_SHIFT_CYCLE, shift=sched)
                st = delay_stats(r, E4_SHIFT_CYCLE)
                rows.append({"m": m, "rho": rho, "pattern": pattern,
                             "size": size, "slope": slope,
                             "shift_cycle": E4_SHIFT_CYCLE,
                             "pre_change_arl": float(
                                 r.tau[:, :E4_SHIFT_CYCLE].mean()),
                             "ref_mse_pre": float(
                                 (r.e_start[:, :E4_SHIFT_CYCLE] ** 2).mean()),
                             "delay": st})
                print(f"  m={m} rho={rho} {pattern}({size or slope}) "
                      f"delay={st['mean']:.2f} q95={st['q95']:.0f} "
                      f"[{time.time() - t0:.0f}s]", flush=True)
    payload = {"detector": a.detector, "family": a.family, "status": "OK",
               "threshold": thr, "threshold_provenance": prov,
               "n_replicates": E4_REPLICATES, "n_cycles": E4_CYCLES,
               "shift_cycle": E4_SHIFT_CYCLE, "tail_floor": TAIL_EVENT_FLOOR,
               "seconds": time.time() - t0, "rows": rows}
    C.write(dest, C.envelope(generator="run_drift.py",
                             schema="rebaseguard.p8r.drift.v1",
                             tags=[PROD_DRIFT_E4], payload=payload))
    print(f"DONE drift {a.detector}/{a.family} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
