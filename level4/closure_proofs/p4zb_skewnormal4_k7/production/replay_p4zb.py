#!/usr/bin/env python3
"""P4ZB Phase 13 -- replay.  Prespecified subset: the m with the best K7 margin
and the m with the worst, chosen from the frozen plan's ordering rule (best =
smallest T_B relative, worst = largest), plus all three routes."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
import run_p4zb as R          # noqa: E402
import p4zb_hash as sh        # noqa: E402
import runtime_contract as rc # noqa: E402


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--per-route",type=int,default=2)
    args=ap.parse_args()
    rc.enforce_environment()
    ctx=R.preflight(); mod=R.load_modules(); sh.final_producer_gate(ctx["manifest"])
    adj=json.loads((NS/"production"/"adjudication_p4zb.json").read_text())
    tb={c["m"]: c["fd_ladder"]["relative_drift"] for c in adj["cells"] if c.get("fd_ladder")}
    best=min(tb,key=tb.get); worst=max(tb,key=tb.get)
    rows=[]
    for route in ("rb_score","rb_map","fd_ladder"):
        for stored in R.read_blocks(route)[: args.per_route]:
            rebuilt=_recompute(mod,ctx,stored)
            mism=[k for k,v in rebuilt.items() if stored[k]!=v]
            body=dict(stored); body.update(rebuilt); body.pop("scientific_hash",None)
            h=sh.scientific_hash(body)
            ok=(h==stored["scientific_hash"]) and not mism
            rows.append({"route":route,"block":stored["block"],"seed":stored["seed"],
                "stored_scientific_hash":stored["scientific_hash"],
                "replay_scientific_hash":h,
                "scientific_hash_identical":h==stored["scientific_hash"],
                "producer_hash_identical":stored["producer_hash"]==ctx["manifest"]["producer_hash"],
                "runtime_hash_identical":stored["runtime_hash"]==ctx["contract"]["runtime_hash"],
                "mismatched_scientific_fields":mism})
            print(f"{'OK' if ok else 'MISMATCH':9s} {route:10s} block {stored['block']}")
    doc={"schema":"rebaseguard.p4zb-replay.v1","result_bearing":True,
        "prespecified_subset":{"best_margin_m":best,"worst_margin_m":worst,
            "note":"every block covers all four m simultaneously, so replaying a "
                   "block replays the best- and worst-margin cells together",
            "T_B_relative_by_m":tb},
        "policy":"every scientific field and the scientific hash compared; CPU "
                 "and wall timings are non-scientific by the same allowlist",
        "blocks_replayed":len(rows),
        "all_scientific_hashes_identical":all(r["scientific_hash_identical"] for r in rows),
        "all_producer_hashes_identical":all(r["producer_hash_identical"] for r in rows),
        "all_runtime_hashes_identical":all(r["runtime_hash_identical"] for r in rows),
        "any_scientific_field_mismatch":any(r["mismatched_scientific_fields"] for r in rows),
        "rows":rows}
    (NS/"production"/"replay_p4zb.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"\nreplayed {len(rows)} blocks; hashes identical: {doc['all_scientific_hashes_identical']}; "
          f"field mismatches: {doc['any_scientific_field_mismatch']}")
    print(f"best-margin m={best} (T_B rel {tb[best]:.5f}), worst-margin m={worst} (T_B rel {tb[worst]:.5f})")
    return 0 if doc["all_scientific_hashes_identical"] and not doc["any_scientific_field_mismatch"] else 1


def _recompute(mod,ctx,stored):
    plan=ctx["plan"]; cfg=plan["configuration"]; m_grid=tuple(cfg["m_grid"])
    fam=mod["REGISTRY"][cfg["family"]]; kit=mod["FAMILY_KITS"][cfg["family"]]
    det=mod["Detector"](cfg["detector_kind"],cfg["threshold"])
    fd=tuple(plan["fd_ladder"]["frozen_scientific_pair"])
    route,block=stored["route"],stored["block"]; central=None
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
