#!/usr/bin/env python3
"""P4ZA Phase 17 -- determinism / replay.

Recomputes stored blocks from their recorded seed and block index in a fresh
process and compares every scientific field and the scientific hash.  Timings
are expected to differ and are excluded by the same allowlist the hash uses.
Nothing is written back to the block store.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
import run_p4za as R           # noqa: E402
import p4za_hash as sh         # noqa: E402
import runtime_contract as rc  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-route", type=int, default=1)
    args = ap.parse_args()
    rc.enforce_environment()
    ctx = R.preflight(); mod = R.load_modules(); sh.final_producer_gate(ctx["manifest"])
    plan = ctx["plan"]; m_grid = (1,2,3,5)
    # a prespecified representative subset: one K7 configuration, one
    # bounded-score K3 configuration, and the skewnormal4 route.
    want = ["frozen/sr@520.886/gaussian", "reduced/sr@20/logistic",
            "frozen/sr@520.886/skewnormal4"]
    rows = []
    for cfg in plan["configurations"]:
        if cfg["id"] not in want: continue
        for route in ("rb_score","rb_map","fd_ladder"):
            for stored in R.read_blocks(cfg, route)[: args.per_route]:
                rebuilt = _recompute(mod, ctx, cfg, stored, m_grid)
                mism = [k for k, v in rebuilt.items() if stored[k] != v]
                body = dict(stored); body.update(rebuilt); body.pop("scientific_hash", None)
                h = sh.scientific_hash(body)
                ok = (h == stored["scientific_hash"]) and not mism
                rows.append({"configuration":cfg["id"],"route":route,
                    "block":stored["block"],"seed":stored["seed"],
                    "stored_scientific_hash":stored["scientific_hash"],
                    "replay_scientific_hash":h,
                    "scientific_hash_identical":h==stored["scientific_hash"],
                    "producer_hash_identical":stored["producer_hash"]==ctx["manifest"]["producer_hash"],
                    "runtime_hash_identical":stored["runtime_hash"]==ctx["contract"]["runtime_hash"],
                    "mismatched_scientific_fields":mism,
                    "timings_excluded_from_comparison":True})
                print(f"{'OK' if ok else 'MISMATCH':9s} {cfg['id']:32s} {route:10s} block {stored['block']}")
    doc = {"schema":"rebaseguard.p4za-replay.v1","result_bearing":True,
        "policy":"every scientific field and the scientific hash compared; "
                 "CPU and wall timings are non-scientific by the same allowlist "
                 "the hash uses",
        "prespecified_subset":want,
        "blocks_replayed":len(rows),
        "all_scientific_hashes_identical":all(r["scientific_hash_identical"] for r in rows),
        "all_producer_hashes_identical":all(r["producer_hash_identical"] for r in rows),
        "all_runtime_hashes_identical":all(r["runtime_hash_identical"] for r in rows),
        "any_scientific_field_mismatch":any(r["mismatched_scientific_fields"] for r in rows),
        "rows":rows}
    (NS/"production"/"replay_p4za.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"\nreplayed {len(rows)} blocks; hashes identical: "
          f"{doc['all_scientific_hashes_identical']}; field mismatches: "
          f"{doc['any_scientific_field_mismatch']}")
    return 0 if doc["all_scientific_hashes_identical"] and not doc["any_scientific_field_mismatch"] else 1


def _recompute(mod, ctx, cfg, stored, m_grid):
    fam=mod["REGISTRY"][cfg["family"]]; kit=mod["FAMILY_KITS"][cfg["family"]]
    det=mod["Detector"](cfg["detector_kind"], cfg["threshold"])
    plan=ctx["plan"]; fd=tuple(plan["fd_ladder"]["frozen_scientific_pair"])
    route, block = stored["route"], stored["block"]
    central=None
    if route=="rb_score":
        rng=np.random.Generator(np.random.PCG64([cfg["seed_rb_score"],block]))
        values,uns,steps=mod["rb_score_batch"](family=fam,kit=kit,
            detector_kind=cfg["detector_kind"],threshold=cfg["threshold"],
            m_grid=m_grid,n_paths=cfg["block_paths"],rng=rng,
            max_steps=cfg["max_steps"],new_state=det.new_state,step_fn=det.step)
    elif route=="rb_map":
        values=mod["rb_map_derivative_batch"](fd_steps=fd,m_grid=m_grid,family=fam,
            kit=kit,detector_kind=cfg["detector_kind"],threshold=cfg["threshold"],
            n_paths=cfg["block_paths"],seed=cfg["seed_rb_map"],batch=block,
            max_steps=cfg["max_steps"],new_state=det.new_state,step_fn=det.step,
            stream_counter=mod["stream_counter"]); uns,steps=0,0
    else:
        rungs=plan["fd_ladder"]["rungs"]; central={}
        for h in rungs:
            g=mod["rb_map_batch"](family=fam,kit=kit,detector_kind=cfg["detector_kind"],
                threshold=cfg["threshold"],m_grid=m_grid,e_values=(h,-h),
                n_paths=cfg["block_paths"],seed=cfg["seed_fd_ladder"],batch=block,
                max_steps=cfg["max_steps"],new_state=det.new_state,step_fn=det.step,
                stream_counter=mod["stream_counter"])
            central[h]={m:-(g[h][m]-g[-h][m])/(2.0*h) for m in m_grid}
        values={m:central[rungs[-1]][m] for m in m_grid}; uns,steps=0,0
    out={"block_mean":{str(m):float(values[m].mean()) for m in m_grid},
         "tail":{str(m):R.tail_stats(values[m]) for m in m_grid},
         "unstopped_paths":int(uns),"steps_used":int(steps)}
    if route=="fd_ladder":
        rungs=plan["fd_ladder"]["rungs"]
        out["central_difference_by_h"]={f"{h:g}":{str(m):float(central[h][m].mean()) for m in m_grid} for h in rungs}
        out["richardson_by_pair"]={f"{c:g}/{f:g}":{str(m):float(((4.0*central[f][m]-central[c][m])/3.0).mean()) for m in m_grid}
                                   for c,f in zip(rungs[:-1],rungs[1:])}
    return out


if __name__ == "__main__":
    raise SystemExit(main())
