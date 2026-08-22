"""Stage E per-task campaign: calibrate, then run every policy under every
frozen drift condition on the SAME stream with the SAME injection grid.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate_e import calibrate                            # noqa: E402
from drift import inject, injection_grid                     # noqa: E402
from loaders import LOADERS                                  # noqa: E402
from metrics_e import (                                      # noqa: E402
    acf1, block_bootstrap_diff, block_bootstrap_mean, block_bootstrap_ratio,
    cycle_lengths, e2_reference_error, e3_alert_burden,
)
from monitor import BURN_CYCLES, M_WINDOW, run_monitor       # noqa: E402
from residuals import build_stream                           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEED_GRID = 20261101
# Settling before each onset = 3 cycles at the calibration TARGET ARL0. Derived
# from the frozen calibration target, not from any observed outcome.
WARMUP = 750

POLICIES = {"P0_fresh": 0.0, "P1_full_reuse": 1.0,
            "P2_rebaseguard": 0.029796, "P3_moderate_EXPLORATORY": 0.3}
CONDITIONS = [("STEP", 0.5), ("STEP", 1.0), ("STEP", 2.0),
              ("GRAD", 1.0), ("RECUR", 1.0)]


def run_task(task: str, *, k_events: int, pilot: bool, out_name: str) -> dict:
    t0 = time.time()
    ms = build_stream(LOADERS[task]())
    sp = ms.split
    r = ms.residual
    ev_lo, ev_hi = sp.eval.start, sp.eval.stop
    n_eval = ev_hi - ev_lo

    # reference at deployment: last m observations of the CALIBRATION block
    r0 = float(r[sp.calib.stop - M_WINDOW:sp.calib.stop].mean())

    cal = calibrate(r, lo=sp.calib.start, hi=sp.calib.stop, scale=ms.scale, r0=r0)
    h = cal["threshold_h"]
    print(f"  calibration: h = {h:.4f}  ARL0 = {cal['achieved_arl0']:.1f} "
          f"CI {[round(v,1) for v in cal['arl0_ci']]}  "
          f"(target {cal['target_arl0']}, rel err {cal['relative_error']:+.4f}, "
          f"{cal['n_cycles']} cycles)", flush=True)

    grid = injection_grid(n_eval, ev_lo, k_events, SEED_GRID)

    # ---- in-control pass: E2, E3 and the tau_0 baseline -------------------
    ic = {}
    for pol, rho in POLICIES.items():
        run = run_monitor(r, scale=ms.scale, threshold=h, rho=rho, r0=r0,
                          start=ev_lo, stop=ev_hi)
        cyc = run.post_burn(BURN_CYCLES)
        cl = cycle_lengths(cyc)
        e2 = e2_reference_error(cyc)
        ic[pol] = {
            "rho": rho, "n_cycles_total": len(run.cycles),
            "n_cycles_scored": len(cyc), "n_obs": run.n_obs,
            "E2_reference_error": block_bootstrap_mean(e2, unit="cycle"),
            "E2_reference_error_values": e2.tolist(),
            "E3_alert_burden_per_1000": e3_alert_burden(cyc, run.n_obs),
            "cycle_length": block_bootstrap_mean(cl, unit="cycle"),
            "reference_acf1": acf1([c.reference for c in cyc]),
            "direction_acf1": acf1([c.direction for c in cyc]),
            "tau0_cycle_lengths": cl.tolist(),
        }
        print(f"    IC {pol:26s} cycles={len(cyc):4d} "
              f"meanlen={cl.mean() if cl.size else float('nan'):7.1f} "
              f"E2={e2.mean() if e2.size else float('nan'):.4f} "
              f"E3={ic[pol]['E3_alert_burden_per_1000']:.3f}/1000", flush=True)

    # ---- matched in-control baseline, measured at the SAME grid points -----
    # IMPLEMENTATION CORRECTION (pilot gate, before any confirmatory outcome).
    # The numerator of E1 is a delay from a mid-cycle onset; a FULL in-control
    # cycle length is a different quantity, so their ratio is length-biased
    # (measured on the Task A pilot: E[L^2]/(2E[L]) = 217.8 vs E[L] = 174.0).
    # The matched denominator applies the identical procedure with magnitude 0
    # at the identical grid points. Both denominators are reported.
    ic_at_grid = {}
    for pol, rho in POLICIES.items():
        w_aligned = np.full(grid.size, np.nan)
        w = []
        for gi, t0i in enumerate(grid):
            start = max(ev_lo, int(t0i) - WARMUP)
            run = run_monitor(r, scale=ms.scale, threshold=h, rho=rho, r0=r0,
                              start=start, stop=ev_hi)
            hit = next((c.alarm for c in run.cycles if c.alarm >= t0i), None)
            if hit is not None:
                w.append(float(hit - t0i))
                w_aligned[gi] = float(hit - t0i)
        ic_at_grid[pol] = np.array(w)[np.isfinite(np.array(w))] if w else np.array([])
        ic[pol]["tau0_grid_matched_wait"] = ic_at_grid[pol].tolist()
        ic[pol]["tau0_grid_matched_aligned"] = w_aligned.tolist()
        ic[pol]["tau0_grid_matched_mean"] = (float(ic_at_grid[pol].mean())
                                             if ic_at_grid[pol].size else None)

    # ---- drift passes: one pass per injection event (STEP is permanent) ----
    drift: dict = {}
    for cond, mag in CONDITIONS:
        key = f"{cond}_{mag}"
        drift[key] = {}
        for pol, rho in POLICIES.items():
            delays = np.full(grid.size, np.nan)
            for gi, t0i in enumerate(grid):
                start = max(ev_lo, int(t0i) - WARMUP)
                inj = inject(r, scale=ms.scale, t0=int(t0i),
                             condition=cond, magnitude=mag)
                run = run_monitor(inj, scale=ms.scale, threshold=h, rho=rho,
                                  r0=r0, start=start, stop=ev_hi)
                hit = next((c.alarm for c in run.cycles if c.alarm >= t0i), None)
                if hit is not None:
                    delays[gi] = float(hit - t0i)
            d_aligned = delays
            d = delays[np.isfinite(delays)]
            cl0 = np.array(ic[pol]["tau0_cycle_lengths"])
            w0 = ic_at_grid[pol]
            drift[key][pol] = {
                "rho": rho, "n_events": int(d.size), "n_events_grid": int(grid.size),
                "E4_delay": block_bootstrap_mean(d, unit="injection event"),
                # PRIMARY: matched procedure, matched grid points
                "E1_R_delta": block_bootstrap_ratio(
                    d, w0, unit="event delay / matched in-control wait"),
                # SECONDARY: the length-biased cycle-length denominator
                "E1_R_delta_cyclelen_denominator": block_bootstrap_ratio(
                    d, cl0, unit="event delay / full IC cycle length"),
                "delays": d.tolist(),
                "delays_aligned_to_grid": d_aligned.tolist(),
            }
        row = drift[key]
        print(f"    {key:12s} " + "  ".join(
            f"{p.split('_')[0]}:R={row[p]['E1_R_delta']['ratio']:.3f}"
            for p in POLICIES), flush=True)

    out = {
        "stage": "E", "task": task, "pilot": pilot,
        "protocol_sha256":
            "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc",
        "n_total": int(sp.n),
        "split": {"train": [0, sp.train.stop],
                  "calib": [sp.calib.start, sp.calib.stop],
                  "eval": [ev_lo, ev_hi]},
        "model_kind": ms.model_kind, "n_features": ms.n_features,
        "residual_scale_reference_block": ms.scale,
        "r0_initial_reference": r0,
        "m_window": M_WINDOW, "burn_cycles": BURN_CYCLES,
        "calibration": cal, "threshold_h": h,
        "injection_grid": grid.tolist(), "k_events": int(k_events),
        "warmup_before_onset": WARMUP,
        "event_spacing": float(np.diff(grid).mean()) if grid.size > 1 else None,
        "block5_covers_obs": (float(5 * np.diff(grid).mean())
                              if grid.size > 1 else None),
        "block5_covers_warmup": (bool(5 * np.diff(grid).mean() >= WARMUP)
                                 if grid.size > 1 else None),
        "policies": POLICIES,
        "in_control": ic, "drift": drift,
        "evidence_status": "PILOT" if pilot else "CONFIRMATORY",
        "python": platform.python_version(), "numpy": np.__version__,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (ROOT / "results").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / out_name).write_text(json.dumps(out, indent=2) + "\n")
    print(f"  -> results/{out_name}  ({out['elapsed_s']} s)", flush=True)
    return out


if __name__ == "__main__":
    task = sys.argv[1]
    pilot = "--pilot" in sys.argv
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 8
    tag = "pilot" if pilot else "confirmatory"
    print(f"Stage E {tag}: task {task}, k_events = {k}", flush=True)
    run_task(task, k_events=k, pilot=pilot, out_name=f"task_{task}_{tag}.json")
