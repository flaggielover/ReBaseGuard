#!/usr/bin/env python3
"""Pilot-3 execution: benchmark, design, validation.

Executes PILOT3_PREREGISTRATION.md.  Nothing here is a decision: the cells,
strata, Bmin grid, UCB constructions and their frozen level, kappa pair, cap
grid, replicate counts, thresholds, budget and STOP rules are all frozen in
that document and in `src/p4y_pilot3/strata3.py`.

Usage:
    run_phase3.py benchmark
    run_phase3.py design
    run_phase3.py validation
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_pilot2_final_prefreeze" / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))

from p4y_pilot.blocks import block_value, summarise  # noqa: E402
from p4y_pilot.stats import hill_alpha  # noqa: E402
from p4y_pilot2 import rule as R2  # noqa: E402  (staged rule, unchanged)
from p4y_pilot2.audit import audit  # noqa: E402  (auditor, unchanged)
from p4y_pilot3.addressing3 import audit_reachable_domain, seed  # noqa: E402
from p4y_pilot3.sizing import coverage, size_stage1  # noqa: E402
from p4y_pilot3.ucb import UCB_BASELINE, UCB_LEVEL, UCB_METHODS, evaluate  # noqa: E402
from p4y_pilot3.strata3 import (  # noqa: E402
    BENCHMARK_BLOCKS, BENCHMARK_BLOCKS_ROBUSTNESS, BETA, BMIN_CANDIDATES,
    CAP_MULTIPLIERS, CELL_STRATA, CELLS, DELTA, DESIGN_BASE,
    KAPPA_CANDIDATES, MAX_CAP_MULTIPLIER, MIN_BLOCK_MEAN_ALPHA,
    PILOT3_CPU_CAP_HOURS, PRIMARY_CELLS, R_DESIGN, R_DESIGN_ROBUSTNESS,
    R_VALIDATION, R_VALIDATION_ROBUSTNESS, STRATA, VALIDATION_BASE,
    abs_ceiling, reachable_addresses, reference_blocks, stratum as get_stratum,
)

MIN_BLOCKS = 8
MAX_BMIN = max(BMIN_CANDIDATES)
#: Fixed offset so the bootstrap stream is deterministic in the logical
#: address and can never coincide with a block stream.
BOOTSTRAP_OFFSET = 777_000_000


class Stop(RuntimeError):
    pass


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def spent_hours(exclude: str) -> float:
    total = 0.0
    for name in ("benchmark", "design", "validation"):
        if name == exclude:
            continue
        p = ROOT / "results" / f"{name}.json"
        if p.exists():
            total += json.loads(p.read_text())["cpu_hours"]
    return total


class Pool:
    __slots__ = ("cell", "seed", "values", "blocks", "paths")

    def __init__(self, cell, stream_seed: int):
        self.cell, self.seed = cell, stream_seed
        self.values: dict[int, dict[int, float]] = {}
        self.blocks = self.paths = 0

    def take(self, n: int) -> list[dict[int, float]]:
        for bid in range(n):
            if bid not in self.values:
                self.values[bid] = block_value(self.cell, self.seed, bid)
                self.blocks += 1
                self.paths += self.cell.block_size
        return [self.values[i] for i in range(n)]


def worst_m_relse(blocks: list[dict[int, float]]) -> float:
    worst = -math.inf
    for m in (1, 2, 3, 5):
        worst = max(worst, summarise([b[m] for b in blocks])["relative_se"])
    return worst


def worst_m_series(blocks: list[dict[int, float]]) -> np.ndarray:
    """Block means of the m that carries the worst relative SE."""
    best, arg = -math.inf, 1
    for m in (1, 2, 3, 5):
        r = summarise([b[m] for b in blocks])["relative_se"]
        if r > best:
            best, arg = r, m
    return np.array([b[arg] for b in blocks], dtype=float)


# ---------------------------------------------------------------- benchmark
def run_benchmark() -> int:
    out = {"schema": "rebaseguard.p4y-pilot3-benchmark.v1", "binding": False,
           "ucb_level": UCB_LEVEL, "cells": [], "stopped": None}
    c0 = cpu()
    try:
        for name, cell in CELLS.items():
            n = (BENCHMARK_BLOCKS if name in PRIMARY_CELLS
                 else BENCHMARK_BLOCKS_ROBUSTNESS)
            s = seed(name, CELL_STRATA[name][0], "benchmark", 0)
            vals = [block_value(cell, s, i) for i in range(n)]
            per_m = {}
            for m in (1, 2, 3, 5):
                xs = [v[m] for v in vals]
                st = summarise(xs)
                per_m[m] = {"mean": st["mean"], "block_sd": st["sd"],
                            "hill_alpha_block_means": hill_alpha(xs)}
            alpha = min(per_m[m]["hill_alpha_block_means"] for m in per_m)
            if alpha <= MIN_BLOCK_MEAN_ALPHA:
                raise Stop(f"cell {name}: block-mean Hill alpha {alpha:.2f} "
                           f"<= {MIN_BLOCK_MEAN_ALPHA}")
            # the m that governs, at each stratum's requirement
            targets, true_ref = {}, {}
            for sk in CELL_STRATA[name]:
                st_ = get_stratum(sk)
                worst = max((per_m[m]["block_sd"]
                             / (math.sqrt(st_.b_req) * abs(per_m[m]["mean"])), m)
                            for m in per_m)
                targets[sk] = {"target": worst[0], "worst_m": worst[1],
                               "b_req": st_.b_req}
                bm = per_m[worst[1]]
                true_ref[sk] = {
                    str(b): bm["block_sd"] / (math.sqrt(b) * abs(bm["mean"]))
                    for b in (list(BMIN_CANDIDATES) + [st_.b_ref] if st_.b_ref
                              else BMIN_CANDIDATES)}
            out["cells"].append({
                "cell": name, "config": cell.config, "route": cell.route,
                "block_size": cell.block_size, "benchmark_blocks": n,
                "min_block_mean_alpha": alpha,
                "benchmark_relative_uncertainty_of_sd":
                    1.0 / math.sqrt(2 * (n - 1)),
                "by_m": {str(m): per_m[m] for m in per_m},
                "targets": targets, "true_reference_relse": true_ref,
            })
            print(f"{name} {cell.config:26s} {cell.route}  n={n}  "
                  f"alpha={alpha:6.2f}  sd(s)/s={1/math.sqrt(2*(n-1)):.4%}  "
                  + " ".join(f"{k}:{v['target']:.5g}" for k, v in targets.items()),
                  flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)
    out["cpu_hours"] = (cpu() - c0) / 3600.0
    (ROOT / "results" / "benchmark.json").write_text(json.dumps(out, indent=1))
    print(f"\nbenchmark CPU = {out['cpu_hours']*3600:.1f} s")
    return 0


# --------------------------------------------------------- design/validation
def replicate(cell, st, namespace, gid, target, true_ref) -> dict:
    heavy = st.heavy
    n_ref = MAX_BMIN if heavy else st.b_ref
    ref = Pool(cell, seed(cell.key, st.key, "reference", gid))
    ref_blocks = ref.take(n_ref)
    ceiling = abs_ceiling(st)
    pool = Pool(cell, seed(cell.key, st.key, namespace, gid))
    boot_rng = np.random.default_rng(
        seed(cell.key, st.key, "reference", gid) + BOOTSTRAP_OFFSET)

    def measure(b: int) -> float:
        if b > ceiling:
            raise Stop(f"trace exceeded the absolute ceiling {ceiling}")
        return worst_m_relse(pool.take(b))

    bmins = BMIN_CANDIDATES if heavy else (st.b_ref,)
    methods = tuple(UCB_METHODS) if heavy else (UCB_BASELINE,)
    row = {"replicate": gid, "heavy": heavy, "b_req": st.b_req,
           "candidates": {}}
    for bmin in bmins:
        series = worst_m_series(ref_blocks[:bmin])
        point_est = evaluate(UCB_BASELINE, series, rng=boot_rng)
        row.setdefault("reference", {})[str(bmin)] = {
            "relse_point": point_est,
            "true_relse": true_ref[str(bmin)],
            "ratio_to_truth": (point_est / true_ref[str(bmin)]
                               if true_ref[str(bmin)] else math.inf),
            "below_truth": point_est < true_ref[str(bmin)],
        }
        for meth in methods:
            u = evaluate(meth, series, rng=boot_rng)
            row["reference"][str(bmin)].setdefault("ucb", {})[meth] = {
                "u": u,
                "covers_truth": u >= true_ref[str(bmin)],
                "ratio_to_truth": (u / true_ref[str(bmin)]
                                   if true_ref[str(bmin)] else math.inf)}
            for kname, kappa in KAPPA_CANDIDATES.items():
                s1 = size_stage1(b_ref=bmin, relse_point=point_est,
                                 relse_upper=u, target=target, kappa=kappa,
                                 min_blocks=MIN_BLOCKS, abs_ceiling=ceiling)
                key = f"{bmin}|{meth}|{kname}"
                entry = {"bmin": bmin, "ucb": meth, "kappa": kname,
                         "b1": s1.b1, "b1_point": s1.b1_point,
                         "inflation": s1.inflation,
                         "stage1_covers_requirement": coverage(s1.b1, st.b_req),
                         "stage1_point_covers_requirement":
                             coverage(s1.b1_point, st.b_req),
                         "b1_over_requirement": s1.b1 / st.b_req,
                         "b1_point_over_requirement": s1.b1_point / st.b_req,
                         "refused": s1.refused, "caps": {}}
                if s1.refused:
                    for mult in CAP_MULTIPLIERS:
                        entry["caps"][f"{mult:g}"] = {
                            "cap_blocks": math.ceil(mult * s1.b1),
                            "status": "REFUSED_ABOVE_CEILING", "blocks": 0,
                            "valid": False,
                            "reasons": ["stage-1 allocation above the frozen "
                                        "absolute ceiling"],
                            "block_multiplier": math.inf}
                else:
                    max_cap = math.ceil(MAX_CAP_MULTIPLIER * s1.b1)
                    traj = R2.trace(measure=measure, b1=s1.b1, target=target,
                                    kappa=kappa, max_cap=min(max_cap, ceiling))
                    entry["stage_blocks"] = [x.blocks for x in traj.stages]
                    for mult in CAP_MULTIPLIERS:
                        cb = math.ceil(mult * s1.b1)
                        o = R2.terminate(traj, cb)
                        a = audit(o, traj, cap_blocks=cb)
                        entry["caps"][f"{mult:g}"] = {
                            "cap_blocks": cb, "status": o.status,
                            "blocks": o.blocks, "stages": o.stages,
                            "relative_se": o.relative_se,
                            "next_stage_blocks": o.next_stage_blocks,
                            "valid": a.valid, "reasons": list(a.reasons),
                            "block_multiplier": o.blocks / st.b_req}
                row["candidates"][key] = entry
    row["blocks_simulated"] = pool.blocks + ref.blocks
    row["paths_simulated"] = pool.paths + ref.paths
    return row


def run_phase(phase: str) -> int:
    bpath = ROOT / "results" / "benchmark.json"
    if not bpath.exists():
        raise SystemExit("run benchmark first")
    bench = json.loads(bpath.read_text())
    if bench["stopped"]:
        raise SystemExit(f"benchmark STOPPED: {bench['stopped']}")
    binfo = {c["cell"]: c for c in bench["cells"]}

    inj = audit_reachable_domain(reachable_addresses())
    if not inj["collision_free"]:
        raise SystemExit(f"ADDRESS COLLISION: refusing to execute -- {inj}")

    base = DESIGN_BASE if phase == "design" else VALIDATION_BASE
    out = {"schema": f"rebaseguard.p4y-pilot3-{phase}.v1", "binding": False,
           "phase": phase, "delta": DELTA, "beta": BETA,
           "ucb_level": UCB_LEVEL, "bmin_candidates": list(BMIN_CANDIDATES),
           "cap_multipliers": list(CAP_MULTIPLIERS),
           "kappa_candidates": KAPPA_CANDIDATES,
           "address_audit": {k: inj[k] for k in
                             ("addresses", "unique_seeds", "collision_free")},
           "cells": [], "stopped": None}
    c0 = cpu()
    budget = spent_hours(exclude=phase)

    order = [(n, sk) for n in CELLS for sk in CELL_STRATA[n]]
    order.sort(key=lambda x: get_stratum(x[1]).b_req * CELLS[x[0]].block_size)
    try:
        for name, sk in order:
            cell, st = CELLS[name], get_stratum(sk)
            target = binfo[name]["targets"][sk]["target"]
            true_ref = binfo[name]["true_reference_relse"][sk]
            primary = name in PRIMARY_CELLS
            reps = ((R_DESIGN if primary else R_DESIGN_ROBUSTNESS)
                    if phase == "design"
                    else (R_VALIDATION if primary else R_VALIDATION_ROBUSTNESS))
            rows, cc = [], cpu()
            for i in range(reps):
                used = budget + (cpu() - c0) / 3600.0
                if used > PILOT3_CPU_CAP_HOURS:
                    raise Stop(f"CPU cap: {used:.3f} > {PILOT3_CPU_CAP_HOURS} h")
                rows.append(replicate(cell, st, phase, base + i, target,
                                      true_ref))
            out["cells"].append({
                "cell": name, "stratum": sk, "primary": primary,
                "heavy": st.heavy, "weight": st.weight, "b_req": st.b_req,
                "b_ref_ordinary": st.b_ref, "config": cell.config,
                "route": cell.route, "block_size": cell.block_size,
                "target": target, "replicates": rows,
                "cpu_seconds": cpu() - cc,
                "blocks_simulated": sum(r["blocks_simulated"] for r in rows)})
            print(f"{name}/{sk:6s} {cell.config:24s} {cell.route} "
                  f"B_req={st.b_req:5d} heavy={st.heavy}  {cpu()-cc:7.1f} CPU-s "
                  f"{sum(r['blocks_simulated'] for r in rows):8d} blocks",
                  flush=True)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)

    out["cpu_hours"] = (cpu() - c0) / 3600.0
    out["cumulative_cpu_hours"] = budget + out["cpu_hours"]
    (ROOT / "results" / f"{phase}.json").write_text(json.dumps(out, indent=1))
    print(f"\n{phase} CPU = {out['cpu_hours']*3600:.1f} s; cumulative "
          f"{out['cumulative_cpu_hours']:.4f} / {PILOT3_CPU_CAP_HOURS} h")
    return 0


def main(phase: str) -> int:
    if phase == "benchmark":
        return run_benchmark()
    if phase in ("design", "validation"):
        return run_phase(phase)
    raise SystemExit("phase must be benchmark, design or validation")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "benchmark"))
