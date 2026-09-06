#!/usr/bin/env python3
"""Worker/thread probe -- NOT RESULT BEARING.

Measures CPU efficiency, wall throughput and RSS at 1, 2 and 4 workers on this
host, so the worker count can be frozen BEFORE Stage-0.  It runs the real
RB-SCORE kernel on a light cell so the measurement reflects the production
code path, but its outputs are timings only: no estimate is recorded.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS / "src"))
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))

import numpy as np  # noqa: E402

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4z.analytic import FAMILY_KITS  # noqa: E402
from rebaseguard_p4z.rbscore import rb_score_batch  # noqa: E402

PROBE_PATHS = 120_000
PROBE_BLOCKS = 12


def _one_block(args):
    seed, block = args
    fam, kit = REGISTRY["t1p5"], FAMILY_KITS["t1p5"]
    det = Detector("cusum", 5.0)
    t0 = time.process_time()
    rng = np.random.Generator(np.random.PCG64([seed, block]))
    rb_score_batch(family=fam, kit=kit, detector_kind="cusum", threshold=5.0,
                   m_grid=(1, 2, 3, 5), n_paths=PROBE_PATHS, rng=rng,
                   max_steps=200_000, new_state=det.new_state, step_fn=det.step)
    return time.process_time() - t0, resource.getrusage(
        resource.RUSAGE_SELF).ru_maxrss


def run(workers: int) -> dict[str, float]:
    jobs = [(7_777_001, b) for b in range(PROBE_BLOCKS)]
    t_wall = time.time()
    if workers == 1:
        results = [_one_block(j) for j in jobs]
        parent_cpu = sum(r[0] for r in results)
        rss = max(r[1] for r in results)
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(workers) as pool:
            results = pool.map(_one_block, jobs)
        parent_cpu = sum(r[0] for r in results)
        rss = max(r[1] for r in results)
    wall = time.time() - t_wall
    return {
        "workers": workers,
        "blocks": PROBE_BLOCKS,
        "paths_per_block": PROBE_PATHS,
        "worker_cpu_seconds_sum": parent_cpu,
        "wall_seconds": wall,
        "cpu_to_wall_ratio": parent_cpu / wall,
        "blocks_per_wall_second": PROBE_BLOCKS / wall,
        "peak_rss_mb": rss / (1024 * 1024) if rss > 1 << 22 else rss / 1024,
    }


def main() -> int:
    from runtime_contract import enforce_environment  # noqa: PLC0415
    enforce_environment()
    doc = {"schema": "rebaseguard.p4z-worker-probe.v1", "result_bearing": False,
           "purpose": "freeze the worker/thread configuration before Stage-0",
           "host_cores": {"performance": 2, "efficiency": 4},
           "runs": []}
    for workers in (1, 2, 4):
        row = run(workers)
        doc["runs"].append(row)
        print(f"workers={row['workers']}  wall={row['wall_seconds']:6.2f}s  "
              f"cpu={row['worker_cpu_seconds_sum']:6.2f}s  "
              f"cpu/wall={row['cpu_to_wall_ratio']:5.2f}  "
              f"blocks/s={row['blocks_per_wall_second']:5.3f}  "
              f"rss={row['peak_rss_mb']:6.1f}MB")
    base = doc["runs"][0]["blocks_per_wall_second"]
    for row in doc["runs"]:
        row["speedup_vs_1_worker"] = row["blocks_per_wall_second"] / base
        row["parallel_efficiency"] = row["speedup_vs_1_worker"] / row["workers"]
    out = NS / "production" / "worker_probe.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
