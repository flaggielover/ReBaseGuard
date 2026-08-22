#!/usr/bin/env python
"""Stage C.1 — the independent confirmatory campaign.

Runs on seeds that appear nowhere else in the repository.  Every design choice
was frozen in STAGE_C1_PROTOCOL.md and results/sizing_decision.json before this
script generated a single confirmatory outcome.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from campaign_c1 import (
    RESULTS,
    RHO_EXPLORATORY,
    RHO_FRESH,
    RHO_FULL,
    SEED_ADVERSARIAL,
    SEED_CONFIRM,
    SHIFTS,
    arm,
    config_hash,
    rho_rbg,
    run_cell,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level4" / "src"))
from rebaseguard_level4 import provenance   # noqa: E402

SIZING = json.loads((RESULTS / "sizing_decision.json").read_text())["chosen"]


def policies() -> list[tuple[str, float, str]]:
    """(label, rho, role).  Roles decide what may influence the decision."""
    return [
        ("fresh", RHO_FRESH, "non-inferiority reference"),
        ("rbg", rho_rbg(), "the Stage C certificate-aware policy under test"),
        ("full", RHO_FULL, "DIAGNOSTIC ONLY -- never the reference"),
        *[(f"explore_{r:g}", r, "EXPLORATORY -- must not affect the decision")
          for r in RHO_EXPLORATORY],
    ]


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED_CONFIRM)
    ap.add_argument("--tag", default="confirmatory")
    ap.add_argument("--n-replicates", type=int, default=SIZING["N_replicates"])
    ap.add_argument("--n-events", type=int, default=SIZING["K_events"])
    ap.add_argument("--burn-in", type=int, default=SIZING["burn_in"])
    ap.add_argument("--cycles-between", type=int,
                    default=SIZING["cycles_between"])
    args = ap.parse_args(argv[1:])

    if args.seed in (20260820, 20260821, 20260822):
        raise SystemExit(f"seed {args.seed} overlaps an earlier stage; refused")

    print(f"Stage C.1 [{args.tag}] seed={args.seed}  "
          f"N={args.n_replicates} replicates x K={args.n_events} events, "
          f"burn-in {args.burn_in}, spacing {args.cycles_between}", flush=True)
    t0 = time.time()
    arms: dict[str, dict] = {}
    for label, rho, role in policies():
        for shift in (0.0,) + SHIFTS:
            key = {"stage": "c1", "tag": args.tag, "policy": label,
                   "rho": float(rho), "shift": float(shift),
                   "N": args.n_replicates, "K": args.n_events,
                   "burn_in": args.burn_in,
                   "cycles_between": args.cycles_between, "seed": args.seed}
            cell = run_cell(key, lambda rho=rho, shift=shift: arm(
                rho=rho, shift=shift, n_replicates=args.n_replicates,
                n_events=args.n_events, burn_in=args.burn_in,
                cycles_between=args.cycles_between, master_seed=args.seed),
                verbose=False)
            arms[f"{label}|{shift}"] = cell
            print(f"  {label:<12} Delta={shift:<5g} "
                  f"mean delay {cell['grand_mean_delay']:8.3f}  "
                  f"ties {cell['n_two_arm_ties']}  "
                  f"({cell['seconds']:.0f}s)", flush=True)

    payload = {
        "campaign": "stage_c1", "tag": args.tag,
        "arguments": vars(args),
        "policies": [{"label": l, "rho": r, "role": ro} for l, r, ro in policies()],
        "shifts": list(SHIFTS),
        "arms": {k: {kk: vv for kk, vv in v.items()
                     if kk not in ("per_replicate_mean_delay",
                                   "per_replicate_median_delay",
                                   "recovery_abs_e_by_offset")}
                 for k, v in arms.items()},
        "arm_cell_hashes": {k: v["config_hash"] for k, v in arms.items()},
        "seconds": time.time() - t0,
        "manifest": provenance.build_manifest(
            gate="stage-c1", stage=args.tag, config=vars(args)),
    }
    out = RESULTS / f"campaign_{args.tag}.json"
    out.write_text(json.dumps(payload, indent=2, default=float))
    print(f"\n  wrote {out}  ({payload['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
