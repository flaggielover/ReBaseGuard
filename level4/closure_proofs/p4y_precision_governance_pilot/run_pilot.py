#!/usr/bin/env python3
"""P4Y pre-freeze pilot -- design and validation phases.

Executes PILOT_PREREGISTRATION.md.  Nothing here is a design decision: the
cells, the rules, the replicate counts, the split, the caps, the statistical
framework and the selection criterion are all fixed in that document and in
``src/p4y_pilot/config.py``.

NON-BINDING.  No checkpoint, no production, no verdict on the P4 scientific
line.

Usage:
    run_pilot.py design
    run_pilot.py validation
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

from p4y_pilot.blocks import BlockPool, worst_relative_se  # noqa: E402
from p4y_pilot.config import (  # noqa: E402
    B1_NOMINAL, BETA, CAP_MULTIPLIER, DELTA, DESIGN_BASE, MIN_BLOCKS,
    PILOT_CELLS, PILOT_CPU_CAP_HOURS, POOL_HARD_LIMIT, R_DESIGN, R_VALIDATION,
    REFERENCE_BLOCKS, VALIDATION_BASE, kappa_for,
)
from p4y_pilot.rules import (  # noqa: E402
    ATTAINED, CANDIDATES, PRECISION_LIMITED, UNRESOLVED, can_end_unresolved,
    run as run_rule,
)
from p4y_pilot.stats import (  # noqa: E402
    clopper_pearson_lower, hill_alpha, wilson_interval,
)

CAP_BLOCKS = CAP_MULTIPLIER * B1_NOMINAL
#: Block counts the free scale-robustness diagnostic is evaluated at.  These
#: reuse blocks the rules already drew; they cost nothing extra.
SCALE_GRID = (12, 24, 48, 96)


class Stop(RuntimeError):
    """A predeclared STOP rule fired."""


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def calibration() -> dict:
    path = ROOT / "results" / "calibration.json"
    if not path.exists():
        raise SystemExit("run_calibration.py first: r*_pilot is not frozen")
    data = json.loads(path.read_text())
    return {c["cell"]: c for c in data["cells"]}


def replicate(cell, global_id: int, namespace: str, r_star: float,
              kappa: float, spent_hours: float) -> dict:
    """One independent repetition of every candidate rule on one cell."""
    ref = BlockPool(cell, "reference", global_id)
    ref_rel, ref_m = worst_relative_se(ref.take(REFERENCE_BLOCKS))
    pool = BlockPool(cell, namespace, global_id)

    def measure(blocks: int) -> float:
        if blocks > POOL_HARD_LIMIT:
            raise Stop(f"pool overrun: {blocks} > {POOL_HARD_LIMIT} blocks")
        return worst_relative_se(pool.take(blocks))[0]

    outcomes = {}
    for rule in CANDIDATES:
        o = run_rule(rule, measure=measure, reference_blocks=REFERENCE_BLOCKS,
                     reference_relative_se=ref_rel, r_star=r_star,
                     kappa=kappa, cap_blocks=CAP_BLOCKS,
                     min_blocks=MIN_BLOCKS)
        outcomes[rule.name] = {
            "status": o.status, "blocks": o.blocks, "stages": o.stages,
            "relative_se": o.relative_se,
            "block_multiplier": o.blocks / B1_NOMINAL,
            "stage_blocks": list(o.stage_blocks),
            "stage_relative_se": list(o.stage_relative_se),
            "next_stage_blocks": o.next_stage_blocks,
        }

    # Free diagnostic: realised relative SE at fixed block counts, from blocks
    # the rules already paid for.  Nothing is simulated for this.
    scale = {}
    for b in SCALE_GRID:
        if b <= pool.blocks_simulated:
            scale[str(b)] = worst_relative_se(pool.take(b))[0]

    return {
        "replicate": global_id, "namespace": namespace,
        "reference_relative_se": ref_rel, "reference_worst_m": ref_m,
        "outcomes": outcomes,
        "scale_diagnostic": scale,
        "blocks_simulated": pool.blocks_simulated + ref.blocks_simulated,
        "paths_simulated": pool.paths_simulated + ref.paths_simulated,
        "cpu_seconds": pool.cpu_seconds + ref.cpu_seconds,
        "block_mean_hill_alpha": hill_alpha(
            [v[1] for v in pool.values.values()]),
    }


def summarise_rule(rows: list[dict], name: str) -> dict:
    outs = [r["outcomes"][name] for r in rows]
    n = len(outs)
    att = sum(o["status"] == ATTAINED for o in outs)
    lim = sum(o["status"] == PRECISION_LIMITED for o in outs)
    unres = sum(o["status"] == UNRESOLVED for o in outs)
    mult = [o["block_multiplier"] for o in outs]
    # p_attain conditions on the cap not having refused the purchase: a
    # PRECISION_LIMITED route is a declared, legal outcome, not a failure of
    # the precision rule.  Both readings are reported.
    resolvable = n - lim
    return {
        "rule": name, "replicates": n,
        "attained": att, "precision_limited": lim, "unresolved": unres,
        "third_state_possible": can_end_unresolved(
            next(r for r in CANDIDATES if r.name == name)),
        "p_attain_all": att / n if n else math.nan,
        "p_attain_within_cap": att / resolvable if resolvable else math.nan,
        "lower_bound_all": clopper_pearson_lower(att, n, BETA),
        "lower_bound_within_cap": clopper_pearson_lower(att, resolvable, BETA)
        if resolvable else 0.0,
        "wilson_all": list(wilson_interval(att, n, BETA)),
        "mean_block_multiplier": sum(mult) / n if n else math.nan,
        "max_block_multiplier": max(mult) if mult else math.nan,
        "median_stages": sorted(o["stages"] for o in outs)[n // 2] if n else 0,
        "max_stages_used": max(o["stages"] for o in outs) if n else 0,
    }


def main(phase: str) -> int:
    if phase not in ("design", "validation"):
        raise SystemExit("phase must be 'design' or 'validation'")
    reps = R_DESIGN if phase == "design" else R_VALIDATION
    base = DESIGN_BASE if phase == "design" else VALIDATION_BASE
    cal = calibration()
    spent0 = json.loads((ROOT / "results" / "calibration.json").read_text())
    budget_used = spent0["total_cpu_seconds"] / 3600.0
    prior = ROOT / "results" / "design.json"
    if phase == "validation" and prior.exists():
        budget_used += json.loads(prior.read_text())["cpu_hours"]

    out = {"schema": f"rebaseguard.p4y-pilot-{phase}.v1", "binding": False,
           "phase": phase, "replicates_per_cell": reps,
           "b1_nominal": B1_NOMINAL, "cap_blocks": CAP_BLOCKS,
           "delta": DELTA, "beta": BETA,
           "reference_blocks": REFERENCE_BLOCKS,
           "cells": [], "stopped": None}
    t0, c0 = time.perf_counter(), cpu()

    # cheapest-first, so a STOP leaves the maximum surviving evidence
    order = sorted(PILOT_CELLS,
                   key=lambda c: cal[c.key]["calibration_cpu_seconds"])
    try:
        for cell in order:
            info = cal[cell.key]
            r_star, kappa = info["r_star_pilot"], kappa_for(cell)
            rows, cc = [], cpu()
            for i in range(reps):
                used = budget_used + (cpu() - c0) / 3600.0
                if used > PILOT_CPU_CAP_HOURS:
                    raise Stop(f"CPU cap: {used:.3f} > {PILOT_CPU_CAP_HOURS} h")
                rows.append(replicate(cell, base + i, phase, r_star, kappa,
                                      used))
            cell_cpu = cpu() - cc
            out["cells"].append({
                "cell": cell.key, "config": cell.config, "route": cell.route,
                "block_size": cell.block_size, "heavy": cell.heavy,
                "kappa": kappa, "r_star_pilot": r_star,
                "rules": [summarise_rule(rows, r.name) for r in CANDIDATES],
                "replicates": rows,
                "cpu_seconds": cell_cpu,
                "blocks_simulated": sum(r["blocks_simulated"] for r in rows),
                "paths_simulated": sum(r["paths_simulated"] for r in rows),
            })
            print(f"{cell.key} {cell.config:28s} {cell.route}  "
                  f"{cell_cpu:7.1f} CPU-s  "
                  f"{sum(r['blocks_simulated'] for r in rows):6d} blocks",
                  flush=True)
            for r in CANDIDATES:
                s = out["cells"][-1]["rules"][
                    [x.name for x in CANDIDATES].index(r.name)]
                print(f"    {s['rule']:26s} att={s['attained']:3d}/{s['replicates']:<3d}"
                      f" PL={s['precision_limited']:<3d} UNRES={s['unresolved']:<3d}"
                      f" mean_mult={s['mean_block_multiplier']:6.2f}"
                      f" max_mult={s['max_block_multiplier']:7.2f}", flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)

    out["cpu_hours"] = (cpu() - c0) / 3600.0
    out["wall_seconds"] = time.perf_counter() - t0
    out["cumulative_pilot_cpu_hours"] = budget_used + out["cpu_hours"]
    (ROOT / "results" / f"{phase}.json").write_text(json.dumps(out, indent=1))
    print(f"\n{phase} CPU = {out['cpu_hours']*3600:.1f} s "
          f"({out['cpu_hours']:.4f} h); cumulative pilot "
          f"{out['cumulative_pilot_cpu_hours']:.4f} / {PILOT_CPU_CAP_HOURS} h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "design"))
