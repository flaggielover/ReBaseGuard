#!/usr/bin/env python3
"""Pilot-2 execution: calibration, design, validation.

Executes PILOT2_PREREGISTRATION.md.  Nothing here is a decision: the cells,
strata, kappa candidates, cap grid, replicate counts, endpoint, statistical
method, selection criteria, budget and STOP rules are all frozen there and in
`src/p4y_pilot2/strata.py`.

Usage:
    run_phase.py calibration
    run_phase.py design
    run_phase.py validation
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
_P1 = ROOT.parent / "p4y_precision_governance_pilot"
sys.path.insert(0, str(_P1 / "src"))

from p4y_pilot.blocks import block_value, summarise, worst_relative_se  # noqa: E402
from p4y_pilot.stats import clopper_pearson_lower, hill_alpha  # noqa: E402
from p4y_pilot2.addressing import audit_reachable_domain, seed  # noqa: E402
from p4y_pilot2.audit import audit, summarise as summarise_audits  # noqa: E402
from p4y_pilot2 import rule as R  # noqa: E402
from p4y_pilot2.strata import (  # noqa: E402
    BETA, CALIBRATION_BLOCKS, CAP_MULTIPLIERS, CELL_STRATA, CELLS, DELTA,
    KAPPA_CANDIDATES, KAPPA_STAGE1, MIN_BLOCKS, MIN_BLOCK_MEAN_ALPHA,
    PILOT2_CPU_CAP_HOURS, PRIMARY_CELLS, R_DESIGN, R_DESIGN_ROBUSTNESS,
    R_VALIDATION, R_VALIDATION_ROBUSTNESS, STRATA, VALIDATION_BASE,
    cap_blocks, pool_limit, reachable_addresses,
)


class Stop(RuntimeError):
    """A predeclared STOP rule fired."""


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def spent_hours(exclude: str) -> float:
    total = 0.0
    for name in ("calibration", "design", "validation"):
        if name == exclude:
            continue
        p = ROOT / "results" / f"{name}.json"
        if p.exists():
            total += json.loads(p.read_text())["cpu_hours"]
    return total


class Pool:
    """Lazily evaluated, permanently cached blocks for one logical stream."""

    __slots__ = ("cell", "seed", "values", "blocks", "paths", "cpu_seconds")

    def __init__(self, cell, stream_seed: int):
        self.cell = cell
        self.seed = stream_seed
        self.values: dict[int, dict[int, float]] = {}
        self.blocks = 0
        self.paths = 0
        self.cpu_seconds = 0.0

    def take(self, n: int) -> list[dict[int, float]]:
        for block_id in range(n):
            if block_id in self.values:
                continue
            c0 = cpu()
            self.values[block_id] = block_value(self.cell, self.seed, block_id)
            self.cpu_seconds += cpu() - c0
            self.blocks += 1
            self.paths += self.cell.block_size
        return [self.values[i] for i in range(n)]


def round4(x: float) -> float:
    return float(f"{x:.4g}")


# --------------------------------------------------------------- calibration
def run_calibration() -> int:
    out = {"schema": "rebaseguard.p4y-pilot2-calibration.v1", "binding": False,
           "calibration_blocks": CALIBRATION_BLOCKS,
           "min_block_mean_alpha": MIN_BLOCK_MEAN_ALPHA,
           "cells": [], "stopped": None}
    c0 = cpu()
    try:
        for name, cell in CELLS.items():
            s = seed(name, CELL_STRATA[name][0], "calibration", 0)
            vals = [block_value(cell, s, i) for i in range(CALIBRATION_BLOCKS)]
            per_m = {}
            for m in (1, 2, 3, 5):
                xs = [v[m] for v in vals]
                st = summarise(xs)
                per_m[m] = {"mean": st["mean"], "block_sd": st["sd"],
                            "hill_alpha_block_means": hill_alpha(xs)}
            alpha = min(per_m[m]["hill_alpha_block_means"] for m in per_m)
            if alpha <= MIN_BLOCK_MEAN_ALPHA:
                raise Stop(f"cell {name}: block-mean Hill alpha {alpha:.2f} "
                           f"<= {MIN_BLOCK_MEAN_ALPHA}; the block-count regime "
                           "would not be faithful")
            targets = {}
            for sk in CELL_STRATA[name]:
                st_ = next(x for x in STRATA if x.key == sk)
                worst = max((per_m[m]["block_sd"]
                             / (math.sqrt(st_.b1) * abs(per_m[m]["mean"])), m)
                            for m in per_m)
                targets[sk] = {"r_star_pilot": round4(worst[0]),
                               "raw": worst[0], "worst_m": worst[1],
                               "b1_nominal": st_.b1, "b_ref": st_.b_ref}
            out["cells"].append({
                "cell": name, "config": cell.config, "route": cell.route,
                "block_size": cell.block_size, "heavy": cell.heavy,
                "min_block_mean_alpha": alpha,
                "by_m": {str(m): per_m[m] for m in per_m},
                "targets": targets,
            })
            print(f"{name} {cell.config:26s} {cell.route}  bs={cell.block_size:6d}  "
                  f"min alpha={alpha:6.2f}  "
                  + "  ".join(f"{k}:{v['r_star_pilot']:.4g}"
                              for k, v in targets.items()), flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)
    out["cpu_hours"] = (cpu() - c0) / 3600.0
    (ROOT / "results" / "calibration.json").write_text(json.dumps(out, indent=1))
    print(f"\ncalibration CPU = {out['cpu_hours']*3600:.1f} s")
    return 0


# --------------------------------------------------------- design/validation
def replicate(cell, stratum, namespace: str, gid: int, target: float) -> dict:
    ref = Pool(cell, seed(cell.key, stratum.key, "reference", gid))
    ref_rel, ref_m = worst_relative_se(ref.take(stratum.b_ref))
    b1 = max(MIN_BLOCKS,
             math.ceil(stratum.b_ref * (ref_rel / target) ** (1.0 / KAPPA_STAGE1)))
    limit = pool_limit(stratum)
    max_cap = cap_blocks(stratum, MAX_CAP_MULTIPLIER)
    pool = Pool(cell, seed(cell.key, stratum.key, namespace, gid))

    def measure(blocks: int) -> float:
        if blocks > limit:
            raise Stop(f"pool overrun: {blocks} > {limit}")
        return worst_relative_se(pool.take(blocks))[0]

    row = {"replicate": gid, "reference_relative_se": ref_rel,
           "reference_worst_m": ref_m, "b1_realised": b1,
           "b1_nominal": stratum.b1, "kappas": {}}
    for kname, kappa in KAPPA_CANDIDATES.items():
        traj = R.trace(measure=measure, b1=b1, target=target, kappa=kappa,
                       max_cap=max_cap)
        if traj.pool_exhausted:                       # defensive; unreachable
            raise Stop(f"trajectory exhausted the pool limit {limit}")
        caps = {}
        for mult in CAP_MULTIPLIERS:
            cb = cap_blocks(stratum, mult)
            o = R.terminate(traj, cb)
            a = audit(o, traj, cap_blocks=cb)
            caps[f"{mult:g}"] = {
                "cap_blocks": cb, "status": o.status, "blocks": o.blocks,
                "stages": o.stages, "relative_se": o.relative_se,
                "next_stage_blocks": o.next_stage_blocks,
                "valid": a.valid, "reasons": list(a.reasons),
                "block_multiplier": o.blocks / stratum.b1,
            }
        row["kappas"][kname] = {
            "stage_blocks": [s.blocks for s in traj.stages],
            "stage_relative_se": [s.relative_se for s in traj.stages],
            "reached_target": traj.reached_target,
            "planned_b1": traj.planned_b1,
            "caps": caps,
        }
    row["blocks_simulated"] = pool.blocks + ref.blocks
    row["paths_simulated"] = pool.paths + ref.paths
    return row


def run_phase(phase: str) -> int:
    cal = ROOT / "results" / "calibration.json"
    if not cal.exists():
        raise SystemExit("run calibration first")
    calib = json.loads(cal.read_text())
    if calib["stopped"]:
        raise SystemExit(f"calibration STOPPED: {calib['stopped']}")
    targets = {c["cell"]: c["targets"] for c in calib["cells"]}

    inj = audit_reachable_domain(reachable_addresses())
    if not inj["collision_free"]:
        raise SystemExit(f"ADDRESS COLLISION: refusing to execute -- {inj}")

    base = 0 if phase == "design" else VALIDATION_BASE
    out = {"schema": f"rebaseguard.p4y-pilot2-{phase}.v1", "binding": False,
           "phase": phase, "delta": DELTA, "beta": BETA,
           "kappa_candidates": KAPPA_CANDIDATES,
           "cap_multipliers": list(CAP_MULTIPLIERS),
           "kappa_stage1": KAPPA_STAGE1,
           "address_audit": {k: inj[k] for k in
                             ("addresses", "unique_seeds", "collision_free",
                              "min_seed", "max_seed")},
           "cells": [], "stopped": None}
    c0 = cpu()
    budget_used = spent_hours(exclude=phase)

    order = [(n, s) for n in CELLS for s in CELL_STRATA[n]]
    order.sort(key=lambda ns: pool_limit(next(x for x in STRATA if x.key == ns[1]))
               * CELLS[ns[0]].block_size)
    try:
        for name, sk in order:
            cell = CELLS[name]
            stratum = next(x for x in STRATA if x.key == sk)
            target = targets[name][sk]["r_star_pilot"]
            primary = name in PRIMARY_CELLS
            reps = ((R_DESIGN if primary else R_DESIGN_ROBUSTNESS)
                    if phase == "design"
                    else (R_VALIDATION if primary else R_VALIDATION_ROBUSTNESS))
            rows, cc = [], cpu()
            for i in range(reps):
                used = budget_used + (cpu() - c0) / 3600.0
                if used > PILOT2_CPU_CAP_HOURS:
                    raise Stop(f"CPU cap: {used:.3f} > {PILOT2_CPU_CAP_HOURS} h")
                rows.append(replicate(cell, stratum, phase, base + i, target))
            out["cells"].append({
                "cell": name, "stratum": sk, "primary": primary,
                "config": cell.config, "route": cell.route,
                "block_size": cell.block_size, "heavy": cell.heavy,
                "b1_nominal": stratum.b1, "b_ref": stratum.b_ref,
                "regime": stratum.regime, "r_star_pilot": target,
                "replicates": rows, "cpu_seconds": cpu() - cc,
                "blocks_simulated": sum(r["blocks_simulated"] for r in rows),
            })
            print(f"{name}/{sk} {cell.config:24s} {cell.route} "
                  f"B1={stratum.b1:5d} B_ref={stratum.b_ref:4d}  "
                  f"{cpu()-cc:7.1f} CPU-s  "
                  f"{sum(r['blocks_simulated'] for r in rows):8d} blocks",
                  flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)

    out["cpu_hours"] = (cpu() - c0) / 3600.0
    out["cumulative_cpu_hours"] = budget_used + out["cpu_hours"]
    (ROOT / "results" / f"{phase}.json").write_text(json.dumps(out, indent=1))
    print(f"\n{phase} CPU = {out['cpu_hours']*3600:.1f} s; cumulative "
          f"{out['cumulative_cpu_hours']:.4f} / {PILOT2_CPU_CAP_HOURS} h")
    return 0


def main(phase: str) -> int:
    if phase == "calibration":
        return run_calibration()
    if phase in ("design", "validation"):
        return run_phase(phase)
    raise SystemExit("phase must be calibration, design or validation")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "calibration"))
