#!/usr/bin/env python3
"""P4Z determinism / replay check.

Recomputes stored result-bearing blocks from their recorded seed and block
index, in a fresh process, and compares every scientific field and the
scientific hash.  CPU and wall timings are expected to differ and are excluded
from the comparison by the same allowlist the hash uses -- that is the point of
an exclusion-based hash.

Nothing is written back to the block store: a replay that disagreed would be a
finding, not a correction.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(NS / "src"))
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))

import numpy as np  # noqa: E402

import run_p4z  # noqa: E402
import runtime_contract as rc  # noqa: E402
import scientific_hash as sh  # noqa: E402


def replay_one(mod, ctx, cfg, stored: dict, m_grid, fd_steps) -> dict:
    fam = mod["REGISTRY"][cfg["family"]]
    kit = mod["FAMILY_KITS"][cfg["family"]]
    det = mod["Detector"](cfg["detector_kind"], cfg["threshold"])
    route, block = stored["route"], stored["block"]

    if route == "rb_score":
        rng = np.random.Generator(np.random.PCG64([cfg["seed_rb_score"], block]))
        values, unstopped, steps = mod["rb_score_batch"](
            family=fam, kit=kit, detector_kind=cfg["detector_kind"],
            threshold=cfg["threshold"], m_grid=m_grid,
            n_paths=cfg["block_paths"], rng=rng, max_steps=cfg["max_steps"],
            new_state=det.new_state, step_fn=det.step)
    elif route == "rb_map":
        values = mod["rb_map_derivative_batch"](
            fd_steps=fd_steps, m_grid=m_grid, family=fam, kit=kit,
            detector_kind=cfg["detector_kind"], threshold=cfg["threshold"],
            n_paths=cfg["block_paths"], seed=cfg["seed_rb_map"], batch=block,
            max_steps=cfg["max_steps"], new_state=det.new_state,
            step_fn=det.step, stream_counter=mod["stream_counter"])
        unstopped, steps = 0, 0
    else:  # fd_ladder
        from rebaseguard_p4z.rbmap import rb_map_batch  # noqa: PLC0415
        ladder = ctx["plan"]["fd_ladder_steps"]
        central = {}
        for h in ladder:
            g = rb_map_batch(
                family=fam, kit=kit, detector_kind=cfg["detector_kind"],
                threshold=cfg["threshold"], m_grid=m_grid, e_values=(h, -h),
                n_paths=cfg["block_paths"], seed=cfg["seed_fd_ladder"],
                batch=block, max_steps=cfg["max_steps"],
                new_state=det.new_state, step_fn=det.step,
                stream_counter=mod["stream_counter"])
            central[h] = {m: -(g[h][m] - g[-h][m]) / (2.0 * h) for m in m_grid}
        values = {m: central[ladder[-1]][m] for m in m_grid}
        unstopped, steps = 0, 0

    replay = {
        "block_mean": {str(m): float(values[m].mean()) for m in m_grid},
        "tail": {str(m): run_p4z.tail_stats(values[m]) for m in m_grid},
        "unstopped_paths": int(unstopped), "steps_used": int(steps),
    }
    if route == "fd_ladder":
        ladder = ctx["plan"]["fd_ladder_steps"]
        replay["central_difference_by_h"] = {
            f"{h:g}": {str(m): float(central[h][m].mean()) for m in m_grid}
            for h in ladder}
        replay["richardson_by_pair"] = {
            f"{c:g}/{f:g}": {
                str(m): float(((4.0 * central[f][m] - central[c][m]) / 3.0).mean())
                for m in m_grid}
            for c, f in zip(ladder[:-1], ladder[1:])}

    rebuilt = dict(stored)
    rebuilt.update(replay)
    rebuilt.pop("scientific_hash", None)
    rebuilt_hash = sh.scientific_hash(rebuilt)

    mismatches = []
    for key, value in replay.items():
        if stored[key] != value:
            mismatches.append(key)
    return {
        "configuration": cfg["id"], "route": route, "block": block,
        "seed": stored["seed"],
        "stored_scientific_hash": stored["scientific_hash"],
        "replay_scientific_hash": rebuilt_hash,
        "scientific_hash_identical": rebuilt_hash == stored["scientific_hash"],
        "producer_hash_identical":
            stored["producer_hash"] == ctx["manifest"]["producer_hash"],
        "runtime_hash_identical":
            stored["runtime_hash"] == ctx["contract"]["runtime_hash"],
        "mismatched_scientific_fields": mismatches,
        "stored_cpu_seconds": stored["cpu_seconds"],
        "timings_excluded_from_comparison": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-route", type=int, default=1,
                    help="blocks to replay per route on each selected configuration")
    args = ap.parse_args()

    rc.enforce_environment()
    ctx = run_p4z.preflight()
    mod = run_p4z.load_scientific_modules()
    sh.final_producer_gate(ctx["manifest"])

    plan = ctx["plan"]
    m_grid = tuple(plan["scope"]["m_grid"])
    fd_steps = tuple(plan["fd_steps"])
    targets = [c for c in plan["configurations"] if c["carries_unresolved_cells"]]

    rows = []
    for cfg in targets:
        for route in ("rb_score", "rb_map", "fd_ladder"):
            docs = run_p4z._read_blocks(cfg, route)
            for stored in docs[: args.per_route]:
                row = replay_one(mod, ctx, cfg, stored, m_grid, fd_steps)
                rows.append(row)
                flag = "OK" if (row["scientific_hash_identical"]
                                and not row["mismatched_scientific_fields"]) else "MISMATCH"
                print(f"{flag:8s} {cfg['id']:32s} {route:10s} block {stored['block']}")

    doc = {
        "schema": "rebaseguard.p4z-replay.v1",
        "result_bearing": True,
        "policy": "replay compares every scientific field and the scientific "
                  "hash; CPU and wall timings are non-scientific by the same "
                  "allowlist the hash uses",
        "blocks_replayed": len(rows),
        "all_scientific_hashes_identical":
            all(r["scientific_hash_identical"] for r in rows),
        "all_producer_hashes_identical":
            all(r["producer_hash_identical"] for r in rows),
        "all_runtime_hashes_identical":
            all(r["runtime_hash_identical"] for r in rows),
        "any_scientific_field_mismatch":
            any(r["mismatched_scientific_fields"] for r in rows),
        "rows": rows,
    }
    out = NS / "production" / "replay.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"\nreplayed {len(rows)} blocks; hashes identical: "
          f"{doc['all_scientific_hashes_identical']}; field mismatches: "
          f"{doc['any_scientific_field_mismatch']}")
    print(f"-> {out}")
    return 0 if doc["all_scientific_hashes_identical"] and not doc["any_scientific_field_mismatch"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
