#!/usr/bin/env python
"""Stage C step 3 — detection delay under controlled post-change mean shifts.

Design notes that matter for reading the numbers:

* `tau` is extremely heavy-tailed (in control at rho = 0: mean 78, median 16,
  sd 173).  100 change events would give ~22% relative error on the mean, far
  too coarse for the C6 criterion, so detection uses thousands of independent
  change events rather than the 100 replicates of the in-control sweep.
* Delay must never be read alone.  A more dispersed reference detects FASTER
  (A is decreasing in |e|) while also false-alarming more, so the honest object
  is the pair (in-control ARL, detection delay).  That pairing is what the
  Pareto section reports.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

from campaign import RESULTS, full_rho_grid, run_cell
from detection import DetectionConfig, simulate_detection
from rebaseguard_level4 import metrics, provenance

SHIFTS = (0.0, 0.25, 0.5, 1.0, 1.5)     # 0.0 is the in-control control arm


def detection_cell(*, rho: float, shift: float, n_replicates: int,
                   burn_in: int, n_cycles_after: int, master_seed: int,
                   n_bootstrap: int) -> dict:
    cfg = DetectionConfig(n_replicates=n_replicates, burn_in=burn_in,
                          n_cycles_after=n_cycles_after, rho=float(rho),
                          shift=float(shift), master_seed=master_seed,
                          n_changes=1)
    res = simulate_detection(cfg)
    delays = res.detection_delays()[:, 0].astype(float)
    e_prev = res.by_replicate("e_prev")
    tau = res.by_replicate("tau").astype(float)
    total = res.total_cycles
    change_col = burn_in

    # reference contamination: |e| right after the change is detected
    e_after = res.by_replicate("e_next")[:, change_col]
    # recovery: cycles until |e| falls back inside the in-control 90% band
    post = res.by_replicate("e_prev")[:, change_col:]

    est = {}
    for i, (name, values) in enumerate([
        ("detection_delay", delays),
        ("log_detection_delay", np.log(delays)),
        ("e_at_change", e_prev[:, change_col]),
        ("abs_e_at_change", np.abs(e_prev[:, change_col])),
        ("e_after_first_realarm", e_after),
        ("abs_e_after_first_realarm", np.abs(e_after)),
    ]):
        est[name] = metrics.bootstrap_estimate(
            values, metric=name, master_seed=master_seed, metric_index=i,
            n_bootstrap=n_bootstrap).as_dict()

    return {
        "config": cfg.as_dict(),
        "statistical_unit": "replicate (one independent change event each)",
        "n_two_arm_ties": res.n_ties,
        "estimates": est,
        "delay_mean": float(delays.mean()),
        "delay_se": float(delays.std(ddof=1) / np.sqrt(delays.size)),
        "delay_median": float(np.median(delays)),
        "delay_q90": float(np.quantile(delays, 0.90)),
        "delay_sd": float(delays.std(ddof=1)),
        "per_replicate_delay": delays.tolist(),
        "post_change_abs_e_by_cycle": np.abs(post).mean(axis=0).tolist(),
        "post_change_tau_by_cycle": tau[:, change_col:].mean(axis=0).tolist(),
    }


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-replicates", type=int, default=4000)
    ap.add_argument("--burn-in", type=int, default=300)
    ap.add_argument("--n-cycles-after", type=int, default=6)
    ap.add_argument("--master-seed", type=int, default=20260821)
    ap.add_argument("--n-bootstrap", type=int, default=4000)
    ap.add_argument("--rho", type=float, nargs="*", default=None)
    ap.add_argument("--shifts", type=float, nargs="*", default=list(SHIFTS))
    ap.add_argument("--tag", default="main")
    args = ap.parse_args(argv[1:])

    grid = tuple(args.rho) if args.rho else full_rho_grid()
    print(f"Stage C detection [{args.tag}]: {len(grid)} rho x "
          f"{len(args.shifts)} shifts, {args.n_replicates} change events each",
          flush=True)
    t0 = time.time()
    rows = []
    for shift in args.shifts:
        for rho in grid:
            key = {"rho": float(rho), "shift": float(shift),
                   "n_replicates": args.n_replicates, "burn_in": args.burn_in,
                   "n_cycles_after": args.n_cycles_after,
                   "master_seed": args.master_seed, "m": 1}
            cell = run_cell("detect", key,
                            lambda rho=rho, shift=shift: detection_cell(
                                rho=rho, shift=shift,
                                n_replicates=args.n_replicates,
                                burn_in=args.burn_in,
                                n_cycles_after=args.n_cycles_after,
                                master_seed=args.master_seed,
                                n_bootstrap=args.n_bootstrap),
                            verbose=False)
            e = cell["estimates"]
            rows.append({
                "rho": float(rho), "shift": float(shift),
                "delay_mean": cell["delay_mean"], "delay_se": cell["delay_se"],
                "delay_ci": [e["detection_delay"]["ci_low"],
                             e["detection_delay"]["ci_high"]],
                "delay_median": cell["delay_median"],
                "delay_q90": cell["delay_q90"],
                "abs_e_at_change": e["abs_e_at_change"]["point"],
                "abs_e_after_first_realarm": e["abs_e_after_first_realarm"]["point"],
                "cell_hash": cell["config_hash"][:16],
            })
            print(f"  shift={shift:<5g} rho={rho:<9.6g} "
                  f"delay={cell['delay_mean']:8.3f} +/- {cell['delay_se']:6.3f} "
                  f"median={cell['delay_median']:6.1f} "
                  f"|e| at change={e['abs_e_at_change']['point']:.4f}",
                  flush=True)

    payload = {"campaign": "stage_c_detection", "tag": args.tag,
               "arguments": vars(args), "rows": rows,
               "seconds": time.time() - t0,
               "manifest": provenance.build_manifest(
                   gate="stage-c", stage=f"detection-{args.tag}",
                   config=vars(args))}
    out = RESULTS / f"detection_{args.tag}.json"
    out.write_text(json.dumps(payload, indent=2, default=float))
    print(f"\n  wrote {out}  ({payload['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
