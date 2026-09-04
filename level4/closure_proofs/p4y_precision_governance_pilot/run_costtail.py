#!/usr/bin/env python3
"""AMENDMENT 1 phase: the uncensored cost tail.

The pilot's 6x cap censors every cost distribution at the cap, so a
production cap cannot be projected from the design or validation phases.  This
phase re-runs three of the rules against a 16x cap in a FRESH seed namespace
and records, per replicate:

  * the blocks each rule actually spends;
  * the ORACLE first-crossing block count -- the smallest B at which the
    realised relative SE first reaches r*.  No rule can use it (it needs
    hindsight), but it is the cost distribution a perfect rule would face and
    so bounds what any cap must cover.

Used ONLY to project a production cap and an uncensored unconditional
p_attain.  Never used to select a rule, and never to set delta or beta.
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

import numpy as np  # noqa: E402

from p4y_pilot.blocks import M_GRID, BlockPool, worst_relative_se  # noqa: E402
from p4y_pilot.config import (  # noqa: E402
    B1_NOMINAL, BETA, COSTTAIL_CAP_BLOCKS, COSTTAIL_CAP_MULTIPLIER,
    COSTTAIL_POOL_LIMIT, COSTTAIL_REPLICATES, COSTTAIL_RULES, MIN_BLOCKS,
    PILOT_CELLS, PILOT_CPU_CAP_HOURS, REFERENCE_BLOCKS, kappa_for,
)
from p4y_pilot.rules import ATTAINED, CANDIDATES, run as run_rule  # noqa: E402
from p4y_pilot.stats import clopper_pearson_lower  # noqa: E402

RULES = tuple(r for r in CANDIDATES if r.name in COSTTAIL_RULES)
COSTTAIL_BASE = 5_000


class Stop(RuntimeError):
    pass


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def first_crossing(pool: BlockPool, r_star: float) -> int | None:
    """Smallest B >= MIN_BLOCKS whose realised worst-m relative SE meets r*.

    Uses running mean and running unbiased variance from cumulative sums, so
    the whole curve costs one pass per ``m``.  ``worst_relative_se`` is the
    reference definition; ``tests`` pin these against each other.
    """
    drawn = pool.blocks_simulated
    if drawn < max(2, MIN_BLOCKS):
        return None
    b = np.arange(1, drawn + 1, dtype=float)
    worst = np.zeros(drawn)
    for m in M_GRID:
        x = np.array([pool.values[i][m] for i in range(drawn)], dtype=float)
        csum, csq = np.cumsum(x), np.cumsum(x * x)
        mean = csum / b
        with np.errstate(invalid="ignore", divide="ignore"):
            var = (csq - b * mean * mean) / (b - 1.0)
            rel = np.sqrt(np.maximum(var, 0.0) / b) / np.abs(mean)
        rel[0] = np.inf
        worst = np.maximum(worst, rel)
    hit = np.flatnonzero((worst <= r_star) & (b >= MIN_BLOCKS))
    return int(hit[0]) + 1 if hit.size else None


def quantile(xs: list[float], q: float) -> float:
    if not xs:
        return math.nan
    s = sorted(xs)
    i = min(len(s) - 1, max(0, int(math.ceil(q * len(s))) - 1))
    return s[i]


def main() -> int:
    cal = {c["cell"]: c for c in json.loads(
        (ROOT / "results" / "calibration.json").read_text())["cells"]}
    spent = json.loads((ROOT / "results" / "calibration.json").read_text()
                       )["total_cpu_seconds"] / 3600.0
    for phase in ("design", "validation"):
        p = ROOT / "results" / f"{phase}.json"
        if p.exists():
            spent += json.loads(p.read_text())["cpu_hours"]
    print(f"pilot CPU already spent: {spent:.4f} h of {PILOT_CPU_CAP_HOURS}")

    out = {"schema": "rebaseguard.p4y-pilot-costtail.v1", "binding": False,
           "amendment": 1, "purpose": "project a production cap only",
           "not_used_for": ["rule selection", "delta", "beta",
                            "the primary endpoint"],
           "replicates_per_cell": COSTTAIL_REPLICATES,
           "cap_blocks": COSTTAIL_CAP_BLOCKS,
           "cap_multiplier": COSTTAIL_CAP_MULTIPLIER,
           "b1_nominal": B1_NOMINAL, "cells": [], "stopped": None}
    t0, c0 = time.perf_counter(), cpu()
    order = sorted(PILOT_CELLS,
                   key=lambda c: cal[c.key]["calibration_cpu_seconds"])
    try:
        for cell in order:
            info = cal[cell.key]
            r_star, kappa = info["r_star_pilot"], kappa_for(cell)
            rows, cc = [], cpu()
            for i in range(COSTTAIL_REPLICATES):
                used = spent + (cpu() - c0) / 3600.0
                if used > PILOT_CPU_CAP_HOURS:
                    raise Stop(f"CPU cap: {used:.3f} > {PILOT_CPU_CAP_HOURS} h")
                ref = BlockPool(cell, "reference", COSTTAIL_BASE + i)
                ref_rel, _ = worst_relative_se(ref.take(REFERENCE_BLOCKS))
                pool = BlockPool(cell, "costtail", COSTTAIL_BASE + i)

                def measure(b: int, _pool=pool) -> float:
                    if b > COSTTAIL_POOL_LIMIT:
                        raise Stop(f"pool overrun: {b} > {COSTTAIL_POOL_LIMIT}")
                    return worst_relative_se(_pool.take(b))[0]

                outcomes = {}
                for rule in RULES:
                    o = run_rule(rule, measure=measure,
                                 reference_blocks=REFERENCE_BLOCKS,
                                 reference_relative_se=ref_rel, r_star=r_star,
                                 kappa=kappa, cap_blocks=COSTTAIL_CAP_BLOCKS,
                                 min_blocks=MIN_BLOCKS)
                    outcomes[rule.name] = {
                        "status": o.status, "blocks": o.blocks,
                        "stages": o.stages, "relative_se": o.relative_se,
                        "block_multiplier": o.blocks / B1_NOMINAL,
                    }
                # oracle first crossing, over blocks already drawn.  Computed
                # from cumulative sums so it costs no simulation and no
                # quadratic re-summarising.
                oracle = first_crossing(pool, r_star)
                rows.append({
                    "replicate": COSTTAIL_BASE + i,
                    "reference_relative_se": ref_rel,
                    "outcomes": outcomes,
                    "oracle_first_crossing_blocks": oracle,
                    "oracle_multiplier": (oracle / B1_NOMINAL
                                          if oracle else None),
                    "blocks_simulated": pool.blocks_simulated
                    + ref.blocks_simulated,
                })
            cell_cpu = cpu() - cc
            summary = []
            for rule in RULES:
                outs = [r["outcomes"][rule.name] for r in rows]
                n = len(outs)
                att = sum(o["status"] == ATTAINED for o in outs)
                mult = [o["block_multiplier"] for o in outs]
                summary.append({
                    "rule": rule.name, "replicates": n, "attained": att,
                    "p_attain_at_16x_cap": att / n if n else math.nan,
                    "lower_bound_at_16x_cap": clopper_pearson_lower(att, n, BETA),
                    "mean_multiplier": sum(mult) / n if n else math.nan,
                    "q50_multiplier": quantile(mult, 0.50),
                    "q90_multiplier": quantile(mult, 0.90),
                    "q95_multiplier": quantile(mult, 0.95),
                    "max_multiplier": max(mult) if mult else math.nan,
                })
            orc = [r["oracle_multiplier"] for r in rows
                   if r["oracle_multiplier"] is not None]
            out["cells"].append({
                "cell": cell.key, "config": cell.config, "route": cell.route,
                "heavy": cell.heavy, "r_star_pilot": r_star,
                "rules": summary,
                "oracle_resolved": len(orc), "oracle_replicates": len(rows),
                "oracle_q50": quantile(orc, 0.50),
                "oracle_q90": quantile(orc, 0.90),
                "oracle_q95": quantile(orc, 0.95),
                "oracle_max": max(orc) if orc else math.nan,
                "replicates": rows, "cpu_seconds": cell_cpu,
                "blocks_simulated": sum(r["blocks_simulated"] for r in rows),
            })
            print(f"{cell.key} {cell.config:28s} {cell.route}  "
                  f"{cell_cpu:7.1f} CPU-s  oracle q50/q90/q95/max = "
                  f"{quantile(orc,0.5):.2f}/{quantile(orc,0.9):.2f}/"
                  f"{quantile(orc,0.95):.2f}/{max(orc) if orc else float('nan'):.2f}",
                  flush=True)
            for s in summary:
                print(f"    {s['rule']:26s} att={s['attained']:3d}/{s['replicates']:<3d}"
                      f" mean={s['mean_multiplier']:6.2f}"
                      f" q90={s['q90_multiplier']:6.2f}"
                      f" q95={s['q95_multiplier']:6.2f}"
                      f" max={s['max_multiplier']:6.2f}", flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)

    out["cpu_hours"] = (cpu() - c0) / 3600.0
    out["wall_seconds"] = time.perf_counter() - t0
    out["cumulative_pilot_cpu_hours"] = spent + out["cpu_hours"]
    (ROOT / "results" / "costtail.json").write_text(json.dumps(out, indent=1))
    print(f"\ncosttail CPU = {out['cpu_hours']*3600:.1f} s; cumulative pilot "
          f"{out['cumulative_pilot_cpu_hours']:.4f} / {PILOT_CPU_CAP_HOURS} h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
