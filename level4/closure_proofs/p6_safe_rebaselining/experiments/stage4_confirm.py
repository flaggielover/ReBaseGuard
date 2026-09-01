"""Stage 4 -- confirmation on EVAL seeds, with frozen policies and parameters.

The freeze point is ``results/calibration.json`` (TUNE, Delta = 0 only) plus
``EXPERIMENT_PROTOCOL.md``.  Nothing is tuned here.  Policies dropped at Stage 2
are listed in ``DROPPED`` with the reason, and are not silently absent.

    python experiments/stage4_confirm.py [family]      family in {eval, replay}
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from _registry import (RESULTS, RHO_GRID, baselines, load_calibration,  # noqa: E402
                       oracles, saw_family, shift_oracle)

from rebaseguard_p6c.runner import run_delay, run_incontrol            # noqa: E402
from rebaseguard_p6c import stats as S                                 # noqa: E402

DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
PRIMARY = ("cusum", 3, 1.0)
N_REP_IC, N_CYCLES_IC, BURN_IN = 8000, 100, 15
N_REP_D, SHIFT_CYCLE = 60000, 15
SHIFTS_ALL = (1.0,)
SHIFTS_REDUCED = (0.5, 2.0)
PAIR = "confirm_paired"

#: dropped at Stage 2 by ES2 (strict domination at matched cost on TUNE)
DROPPED = {
    "B7_overshoot": "ES2 strict domination: worse than B2_rho0.2 on Arl0 AND Rms at identical Fresh, in all 8 families (TUNE)",
    "B8_window_disp": "ES2 strict domination: same, and its sensor (window sample variance) estimates the innovation variance, which is 1 by construction",
    "B10_capped": "ES2 strict domination: same; the consecutive-reuse cap forces periodic full refreshes that cost Arl0 without buying Rms",
}
#: the reduced set carried to the secondary shifts
REDUCED = ("B0_fresh_only", "B3_full_reuse", "B2_rho0.15", "B2_rho0.2",
           "B2_rho0.25", "SAW_M", "SAW_T", "SAW_A_flat", "B6_zbar_two_level",
           "Z1_oracle_saw")


def build(cal, det, m, q_zbar):
    pols = baselines(det, m, q_zbar)
    for k in DROPPED:
        pols.pop(k, None)
    pols.update(saw_family(cal, det, m))
    pols.update(oracles(cal, det, m))
    return pols


def delay_summary(d):
    d = np.asarray(d, float)
    return {
        "Dmean": float(d.mean()),
        "Dmed": float(np.median(d)),
        "Dq75": float(np.quantile(d, 0.75)),
        "Dq95": float(np.quantile(d, 0.95)),
        "Dq99": float(np.quantile(d, 0.99)),
        "Dtail50": float((d > 50).mean()),
        "Dtail100": float((d > 100).mean()),
        "n_events_50": int((d > 50).sum()),
        "n_events_100": int((d > 100).sum()),
        "n": int(d.size),
        "se_mean": float(d.std(ddof=1) / np.sqrt(d.size)),
    }


def main(family="eval"):
    t0 = time.time()
    cal = load_calibration()
    screen = json.loads((RESULTS / "screen.json").read_text())
    corr = json.loads((RESULTS / "correspondence.json").read_text())

    ic, delay = {}, {}
    for det in DETECTORS:
        cb = {b: corr["c_beta"][det][b]["c"] for b in ("0.75", "0.5", "0.25", "0.1")}
        for m in M_GRID:
            key = f"{det}_m{m}"
            q = screen[key]["q_zbar"]
            pols = build(cal, det, m, q)

            # ---- in control -------------------------------------------
            rows, per = {}, {}
            for pid, pol in pols.items():
                out, res = run_incontrol(policy=pol, detector=det, m=m,
                                         family=family, n_rep=N_REP_IC,
                                         n_cycles=N_CYCLES_IC, burn_in=BURN_IN,
                                         e0=0.0, c_beta=cb, pair_tag=PAIR)
                rows[pid] = {k: float(np.mean(v)) for k, v in out.items()}
                rows[pid].update(
                    policy_class=pol.policy_class, policy_name=pol.name,
                    n_rep=int(N_REP_IC),
                    tau1=float(res.tau[:, 0].mean()),
                    tau2=float(res.tau[:, 1].mean()),
                    Coll=float(res.tau[:, 1].mean() / res.tau[:, 0].mean()),
                    rho_mean=float(res.post(res.rho).mean()),
                    rho_p05=float(np.quantile(res.post(res.rho), 0.05)),
                    rho_p95=float(np.quantile(res.post(res.rho), 0.95)),
                    tau_by_cycle=res.tau.mean(axis=0).round(3).tolist(),
                )
                per[pid] = {kk: np.asarray(vv, np.float64)
                            for kk, vv in out.items()}
                per[pid]["Coll_num"] = res.tau[:, 1].astype(float)
                per[pid]["Coll_den"] = res.tau[:, 0].astype(float)
            ic[key] = rows
            np.savez_compressed(RESULTS / f"confirm_ic_{family}_{key}.npz",
                                **{f"{p}|{k}": v for p, d_ in per.items()
                                   for k, v in d_.items()})

            # ---- delays -----------------------------------------------
            for shift in SHIFTS_ALL + SHIFTS_REDUCED:
                sel = pols if shift in SHIFTS_ALL else \
                    {k: v for k, v in pols.items() if k in REDUCED}
                if shift in SHIFTS_ALL:
                    sel = {**sel, **shift_oracle(m)}
                drows, dper = {}, {}
                for pid, pol in sel.items():
                    out, _ = run_delay(policy=pol, detector=det, m=m,
                                       family=family, n_rep=N_REP_D, shift=shift,
                                       shift_cycle=SHIFT_CYCLE, pair_tag=PAIR)
                    drows[pid] = delay_summary(out["delay"])
                    drows[pid]["policy_class"] = pol.policy_class
                    drows[pid]["blind_spot_mass"] = float(
                        (np.abs(out["e_entering"] - 0.0) < 0.2).mean())
                    dper[pid] = out["delay"].astype(np.float32)
                delay[f"{key}_d{shift}"] = drows
                if (det, m, shift) == PRIMARY:
                    np.savez_compressed(
                        RESULTS / f"confirm_delay_primary_{family}.npz", **dper)
            print(f"{key} done ({time.time()-t0:.0f}s)", flush=True)

    (RESULTS / f"confirm_ic_{family}.json").write_text(json.dumps(
        {"dropped": DROPPED, "cells": ic,
         "params": {"n_rep": N_REP_IC, "n_cycles": N_CYCLES_IC,
                    "burn_in": BURN_IN, "family": family}}, indent=1))
    (RESULTS / f"confirm_delay_{family}.json").write_text(json.dumps(
        {"cells": delay,
         "params": {"n_rep": N_REP_D, "shift_cycle": SHIFT_CYCLE,
                    "family": family}}, indent=1))
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval")
