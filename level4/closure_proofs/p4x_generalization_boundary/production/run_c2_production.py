#!/usr/bin/env python3
"""P4X production C2 -- attainable-precision numerical correspondence.

Executes the FROZEN Checkpoint-A specification.  Nothing here is a design
decision: the estimator, the sample-size rule, the block-size rule, the caps and
the gate all come from `checkpoint_a/results/checkpoint_a.json`.

Cost is charged per (configuration, route) because the four windows share paths.
Per-job CPU is measured inside each worker and persisted, so accounting never
depends on an unreaped RUSAGE_CHILDREN.

Usage:
    run_c2_production.py stage1
    run_c2_production.py stage2
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
BOUNDARY = PROD.parent
CLOSURE = BOUNDARY.parent
P4 = CLOSURE / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.estimators import route_a, route_b  # noqa: E402

CHECKPOINT = json.loads(
    (BOUNDARY / "checkpoint_a" / "results" / "checkpoint_a.json").read_text())
PROTOCOL = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())

R_STAR = CHECKPOINT["precision_rule"]["r_star"]
FD_STEPS = tuple(CHECKPOINT["estimator_plan"]["fd_steps"])
M_GRID = tuple(PROTOCOL["m_grid"])
TOTAL_CAP_H = CHECKPOINT["cost_envelope"]["TOTAL_CPU_CAP_HOURS"]
PER_CONFIG_CAP_H = CHECKPOINT["cost_envelope"]["PER_CONFIGURATION_CPU_CAP_HOURS"]
MIN_BLOCK_HEAVY = CHECKPOINT["heavy_tail_policy"]["minimum_block_paths_heavy_tail"]
MIN_BLOCK_DEFAULT = CHECKPOINT["heavy_tail_policy"]["minimum_block_paths_default"]
KAPPA_TOPUP_HEAVY = CHECKPOINT["heavy_tail_policy"]["kappa_t1p5"]
MIN_BLOCKS = 24

#: Measured cost at the PRODUCTION block sizes, s per 1e6 paths.  R0 calibrated
#: at 40k/100k blocks; the heavy-tail rule mandates 250k blocks, where the
#: straggler overhead is larger.  This changes the COST PROJECTION only -- the
#: frozen sample sizes are untouched.
MEASURED_S_PER_1E6 = {"frozen/sr@520.886/t1p5": 25.7,
                      "frozen/cusum@5/t1p5": 19.8}
HEAVY_COST_INFLATION = 1.8      # applied to R0 cost for other 250k-block jobs

#: Fresh production seed namespace.  The frozen campaign used 401xxxx and the
#: R0 pilot 411xxxx; production uses 421xxxx, so no production block can
#: coincide with either.
SEED_BASE = 4210000
WORKERS = 5


def worker_cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def config_key(layer: str, detector: str, family: str) -> str:
    return f"{layer}/{detector}/{family}"


def seed_for(layer: str, kind: str, family: str, route: str) -> int:
    """Deterministic, collision-free production seed."""
    import hashlib
    h = hashlib.sha256(f"{layer}|{kind}|{family}|{route}".encode()).digest()
    return SEED_BASE + int.from_bytes(h[:3], "big") % 9973


def plan_rows_by_config() -> dict:
    rows: dict[str, list] = {}
    for row in CHECKPOINT["production_plan"]:
        rows.setdefault(row["config"], []).append(row)
    return rows


def block_size_for(heavy: bool) -> int:
    return MIN_BLOCK_HEAVY if heavy else MIN_BLOCK_DEFAULT


def allocate(n_required: float, heavy: bool) -> tuple[int, int]:
    """Frozen allocation: block size from the heavy-tail rule, blocks from N."""
    bs = block_size_for(heavy)
    blocks = max(MIN_BLOCKS, math.ceil(n_required / bs))
    return blocks, bs


def job(spec: dict) -> dict:
    """Run one (configuration, route) allocation.  Executed in a worker."""
    c0, w0 = worker_cpu(), time.perf_counter()
    family = REGISTRY[spec["family"]]
    detector = Detector(spec["kind"], spec["threshold"])
    common = dict(family=family, detector=detector, m_grid=M_GRID,
                  batches=spec["blocks"], paths=spec["block_size"],
                  seed=spec["seed"], max_steps=spec["max_steps"])
    if spec["route"] == "route_a":
        out = route_a(**common)
    else:
        out = route_b(**common, fd_steps=FD_STEPS)
    by_m = {str(m): out["by_m"][str(m)]["gamma"] for m in M_GRID}
    return {
        **{k: spec[k] for k in ("config", "layer", "detector", "family",
                                "route", "stage", "blocks", "block_size",
                                "seed", "heavy")},
        "paths": spec["blocks"] * spec["block_size"],
        "by_m": by_m,
        "cpu_seconds": worker_cpu() - c0,
        "wall_seconds": time.perf_counter() - w0,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20),
        "pid": os.getpid(),
    }


def pooled(groups: list[dict]) -> dict:
    """Pool block-mean summaries from one or more independent runs of the SAME
    estimator at the SAME block size.

    Blocks are i.i.d., so pooling shards is pooling blocks: the pooled mean is
    the block-count-weighted mean and the pooled standard error follows from
    the pooled block-to-block variance about that mean.  Sharding a job across
    workers with distinct Philox seeds is therefore a parallelisation choice
    only -- it changes no estimator, no sample size and no block size.
    """
    groups = [g for g in groups if g]
    if len(groups) == 1:
        return dict(groups[0])
    n = sum(g["batches"] for g in groups)
    mean = sum(g["batches"] * g["mean"] for g in groups) / n
    ss = 0.0
    for g in groups:
        ni, mi, si = g["batches"], g["mean"], g["se"]
        var_block_i = (si ** 2) * ni          # sd_i^2
        ss += (ni - 1) * var_block_i + ni * (mi - mean) ** 2
    var_block = ss / (n - 1)
    return {"mean": mean, "se": math.sqrt(var_block / n), "batches": n,
            "paths_per_batch": groups[0]["paths_per_batch"],
            "paths": sum(g["paths"] for g in groups)}


def build_stage1_specs() -> list[dict]:
    specs = []
    by_config = plan_rows_by_config()
    for cfg, rows in sorted(by_config.items()):
        layer, detector, family = rows[0]["layer"], rows[0]["detector"], rows[0]["family"]
        heavy = rows[0]["heavy_tailed"]
        kind = "cusum" if detector.startswith("cusum") else "sr"
        threshold = dict(PROTOCOL["layers"][layer]["detectors"])[kind]
        max_steps = PROTOCOL["layers"][layer]["max_steps"]
        for route in ("route_a", "route_b"):
            n_req = max(r[route]["stage1_paths"] for r in rows)
            blocks, bs = allocate(n_req, heavy)
            specs.append({
                "config": cfg, "layer": layer, "detector": detector,
                "family": family, "kind": kind, "threshold": threshold,
                "max_steps": max_steps, "route": route, "stage": 1,
                "heavy": heavy, "required_paths": n_req,
                "blocks": blocks, "block_size": bs,
                "projected_cpu_hours_checkpoint": max(
                    r[route]["stage1_cpu_hours"] for r in rows),
                "projected_cpu_hours": _measured_projection(
                    cfg, route, rows, heavy, blocks * bs),
                "seed": seed_for(layer, kind, family, route + "_s1"),
            })
    return specs


def run_specs(specs: list[dict], label: str) -> list[dict]:
    print(f"\n=== {label}: {len(specs)} jobs on {WORKERS} workers ===", flush=True)
    # longest-first (LPT) minimises wall-clock makespan.  Ordering is a
    # scheduling choice only: every job is independent and its result does not
    # depend on when it runs.
    ordered = sorted(specs, key=lambda s: -s["projected_cpu_hours"])
    results = []
    with mp.Pool(WORKERS) as pool:
        for res in pool.imap_unordered(job, ordered):
            results.append(res)
            g = res["by_m"]["1"]
            rel = abs(g["se"] / g["mean"]) if g["mean"] else float("inf")
            print(f"  {res['config']:34s} {res['route']:8s} "
                  f"N={res['paths']:>12,d} m1={g['mean']:9.4f} "
                  f"relSE={rel:.5f} cpu={res['cpu_seconds']:8.1f}s", flush=True)
    return results


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "stage1"
    out_path = PROD / "results" / f"c2_{mode}.json"

    if mode == "stage1":
        specs = build_stage1_specs()
        projected = sum(s["projected_cpu_hours"] for s in specs)
        print(f"stage-1 projected CPU {projected:.3f} h against a {TOTAL_CAP_H} h cap")
        if projected > TOTAL_CAP_H:
            raise SystemExit("STOP: stage-1 projection exceeds the total cap")
        t0 = time.perf_counter()
        results = run_specs(specs, "STAGE 1")
        payload = {
            "schema": "rebaseguard.p4x-production-c2-stage1.v1",
            "stage": 1, "seed_base": SEED_BASE, "workers": WORKERS,
            "r_star": R_STAR, "fd_steps": list(FD_STEPS),
            "projected_cpu_hours": projected,
            "specs": specs, "results": results,
            "cpu_seconds_sum_of_jobs": sum(r["cpu_seconds"] for r in results),
            "wall_seconds": time.perf_counter() - t0,
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"\nstage-1 job CPU {payload['cpu_seconds_sum_of_jobs'] / 3600:.4f} h, "
              f"wall {payload['wall_seconds'] / 3600:.4f} h -> {out_path}")
        return

    raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()
