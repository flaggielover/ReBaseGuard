#!/usr/bin/env python
"""Stage C step 2 — the dense in-control rho campaign.

Uses the FROZEN Stage A multi-cycle simulator for every cell; Stage C adds no
detector code to the in-control path.  Each rho is checkpointed, so an
interrupted run resumes without recomputation.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

from arl_curve import ACurve
from campaign import EXTRA_RHO, PROTOCOL_RHO, RESULTS, full_rho_grid, in_control_cell, run_cell
from rebaseguard_level4 import provenance

DEFAULTS = dict(n_replicates=100, n_cycles=10_000, burn_in=1_000,
                master_seed=20260821, n_bootstrap=10_000)


def load_curves():
    d = json.loads((RESULTS / "arl_curve.json").read_text())
    recs = d["records"]
    e = np.array([r["e"] for r in recs])
    se = np.array([r["A_se"] for r in recs])
    curve = ACurve.from_records(recs)
    batches = [ACurve(e, np.array([r["A_batch_means"][b] for r in recs]), se)
               for b in range(d["batches"])]
    return curve, batches


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-replicates", type=int, default=DEFAULTS["n_replicates"])
    ap.add_argument("--n-cycles", type=int, default=DEFAULTS["n_cycles"])
    ap.add_argument("--burn-in", type=int, default=DEFAULTS["burn_in"])
    ap.add_argument("--master-seed", type=int, default=DEFAULTS["master_seed"])
    ap.add_argument("--n-bootstrap", type=int, default=DEFAULTS["n_bootstrap"])
    ap.add_argument("--rho", type=float, nargs="*", default=None)
    ap.add_argument("--tag", default="main")
    args = ap.parse_args(argv[1:])

    curve, batches = load_curves()
    grid = tuple(args.rho) if args.rho else full_rho_grid()
    print(f"Stage C in-control campaign [{args.tag}]: {len(grid)} rho cells, "
          f"{args.n_replicates} replicates x {args.n_cycles} cycles "
          f"(burn-in {args.burn_in}), seed {args.master_seed}", flush=True)

    t0 = time.time()
    rows = []
    for rho in grid:
        key = {"rho": float(rho), "n_replicates": args.n_replicates,
               "n_cycles": args.n_cycles, "burn_in": args.burn_in,
               "master_seed": args.master_seed, "m": 1,
               "n_bootstrap": args.n_bootstrap, "acurve": "arl_curve.json"}
        cell = run_cell(
            "incontrol", key,
            lambda rho=rho: in_control_cell(
                rho=rho, n_replicates=args.n_replicates,
                n_cycles=args.n_cycles, burn_in=args.burn_in,
                master_seed=args.master_seed, n_bootstrap=args.n_bootstrap,
                acurve=curve, a_batches=batches))
        est = cell["estimates"]
        rows.append({
            "rho": float(rho),
            "in_protocol_grid": float(rho) in PROTOCOL_RHO,
            "added_point": float(rho) in EXTRA_RHO,
            "reference_mse": est["reference_mse"]["point"],
            "reference_mse_ci": [est["reference_mse"]["ci_low"],
                                 est["reference_mse"]["ci_high"]],
            "cycle_arl": est["cycle_arl"]["point"],
            "cycle_arl_ci": [est["cycle_arl"]["ci_low"],
                             est["cycle_arl"]["ci_high"]],
            "arl_decomposition": est.get("arl_decomposition", {}).get("point"),
            "arl_paired_gap": est.get("arl_paired_gap", {}).get("point"),
            "arl_paired_gap_ci": [est.get("arl_paired_gap", {}).get("ci_low"),
                                  est.get("arl_paired_gap", {}).get("ci_high")],
            "arl_decomp_se_from_A": cell["decomposition"].get("arl_decomp_se_from_A"),
            "reference_sd": est["reference_sd"]["point"],
            "reference_mean": est["reference_mean"]["point"],
            "alternation_rate": est["alternation_rate"]["point"],
            "acf_e_lag1": est["acf_e_lag1"]["point"],
            "acf_e_lag2": est["acf_e_lag2"]["point"],
            "acf_e_lag3": est["acf_e_lag3"]["point"],
            "central_mass_0p5": est["central_mass_0p5"]["point"],
            "offcenter_mass_1p0": est["offcenter_mass_1p0"]["point"],
            "offcenter_mass_1p5": est["offcenter_mass_1p5"]["point"],
            "median_tau": est["median_tau"]["point"],
            "cell_file": str(cell.get("config_hash", ""))[:16],
        })
        r = rows[-1]
        print(f"  rho={rho:<9.6g} MSE={r['reference_mse']:.5f} "
              f"ARL={r['cycle_arl']:8.3f} decomp={r['arl_decomposition']:8.3f} "
              f"gap={r['arl_paired_gap']:+7.3f} "
              f"alt={r['alternation_rate']:.4f}", flush=True)

    payload = {
        "campaign": "stage_c_incontrol", "tag": args.tag,
        "arguments": vars(args), "rows": rows,
        "protocol_grid": list(PROTOCOL_RHO), "added_points": list(EXTRA_RHO),
        "seconds": time.time() - t0,
        "manifest": provenance.build_manifest(
            gate="stage-c", stage=f"incontrol-{args.tag}", config=vars(args)),
    }
    out = RESULTS / f"incontrol_{args.tag}.json"
    out.write_text(json.dumps(payload, indent=2, default=float))
    print(f"\n  wrote {out}  ({payload['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
