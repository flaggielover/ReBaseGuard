#!/usr/bin/env python3
"""P4ZA production driver -- the only result-bearing entry point.

Consumes the frozen P4ZA plan and nothing else.  Reuses the P4Z estimators
unchanged (same estimand, bound by content hash) and the P4Z Mac runtime
contract, which was verified to still match this host exactly.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, resource, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
P4Z = NS.parent / "p4z_location_family_feasibility"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P4Z / "src"))
sys.path.insert(0, str(P4Z / "production"))
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))

import numpy as np                       # noqa: E402
import p4za_hash as sh                   # noqa: E402
import runtime_contract as rc            # noqa: E402

BLOCK_DIR = NS / "production" / "blocks"
STATE = NS / "production" / "run_state.json"


def preflight() -> dict:
    rc.enforce_environment()
    head = sh.refuse_dirty_scientific_state()
    contract = rc.verify(rc.CONTRACT_PATH)
    manifest = sh.build_manifest()
    plan = json.loads((NS/"production"/"p4za_campaign_plan.json").read_text())
    prot = json.loads((NS.parent/"p4_theory_generalization"/"configs"/"P4_PROTOCOL.json").read_text())
    t = plan["thresholds"]
    if t["relative"] != prot["gates"]["correspondence_relative_limit"] != 0.03:
        raise sh.ProducerGateError("relative threshold drift")
    if t["z"] != prot["gates"]["correspondence_z_limit"] != 4.0:
        raise sh.ProducerGateError("z threshold drift")
    if abs(1.96*math.sqrt(2)*t["r_star"] - 0.03) > 1e-8:
        raise sh.ProducerGateError("r* drift")
    if plan["fd_ladder"]["frozen_scientific_pair"] != prot["fd_steps"] != [0.05,0.025]:
        raise sh.ProducerGateError("frozen FD pair drift")
    if plan["fixed_policy"]["adaptive"] or plan["fixed_policy"]["top_ups_permitted"]:
        raise sh.ProducerGateError("adaptive stopping is not permitted")
    if plan["execution"] != {"workers":1,"blas_threads":1}:
        raise sh.ProducerGateError("execution configuration drift")
    if contract["runtime_hash"] != plan["runtime_hash"]:
        raise sh.ProducerGateError("runtime hash does not match the frozen plan")
    return {"head":head,"contract":contract,"manifest":manifest,"plan":plan}


def load_modules():
    from rebaseguard_p4_general.detectors import Detector
    from rebaseguard_p4_general.families import REGISTRY
    from rebaseguard_p4_general.simulate import stream_counter
    from rebaseguard_p4z.analytic import FAMILY_KITS, alarm_bounds, alarm_integrals
    from rebaseguard_p4z.rbscore import rb_score_batch
    from rebaseguard_p4z.rbmap import rb_map_batch, rb_map_derivative_batch
    return dict(Detector=Detector, REGISTRY=REGISTRY, stream_counter=stream_counter,
                FAMILY_KITS=FAMILY_KITS, alarm_bounds=alarm_bounds,
                alarm_integrals=alarm_integrals, rb_score_batch=rb_score_batch,
                rb_map_batch=rb_map_batch, rb_map_derivative_batch=rb_map_derivative_batch)


def resume_identity(ph, rh, cid, route, seed, block) -> str:
    return hashlib.sha256(f"{ph}|{rh}|{cid}|{route}|{seed}|{block}".encode()).hexdigest()


def block_path(cfg, route, block) -> Path:
    safe = cfg["id"].replace("/","__").replace("@","_at_")
    return BLOCK_DIR/safe/f"{route}_{block:04d}.json"


def tail_stats(x) -> dict:
    x = np.asarray(x,float); dev=(x-x.mean())**2; tot=float(dev.sum())
    o=np.sort(dev)[::-1]; k=max(10,x.size//200)
    ad=np.sort(np.abs(x-x.mean()))[::-1][:k+1]
    hill=float(1.0/np.mean(np.log(ad[:k]/ad[k]))) if ad[k]>0 else float("nan")
    return {"top1_share":float(o[0]/tot) if tot>0 else 0.0,
            "top5_share":float(o[:5].sum()/tot) if tot>0 else 0.0,
            "hill_index":hill,"per_path_sd":float(x.std(ddof=1))}


def produce(mod, ctx, cfg, route, block, m_grid):
    path = block_path(cfg,route,block)
    ident = resume_identity(ctx["manifest"]["producer_hash"],
                            ctx["contract"]["runtime_hash"], cfg["id"], route,
                            cfg[f"seed_{route}"], block)
    if path.exists():
        d = json.loads(path.read_text())
        if d.get("resume_identity") == ident: return d, 0.0
        raise sh.ProducerGateError(f"resume identity mismatch for {path}")

    fam = mod["REGISTRY"][cfg["family"]]; kit = mod["FAMILY_KITS"][cfg["family"]]
    det = mod["Detector"](cfg["detector_kind"], cfg["threshold"])
    plan = ctx["plan"]; fd = tuple(plan["fd_ladder"]["frozen_scientific_pair"])
    t_cpu, t_wall = time.process_time(), time.time()
    central = None

    if route == "rb_score":
        rng = np.random.Generator(np.random.PCG64([cfg["seed_rb_score"], block]))
        values, unstopped, steps = mod["rb_score_batch"](
            family=fam, kit=kit, detector_kind=cfg["detector_kind"],
            threshold=cfg["threshold"], m_grid=m_grid, n_paths=cfg["block_paths"],
            rng=rng, max_steps=cfg["max_steps"], new_state=det.new_state,
            step_fn=det.step)
    elif route == "rb_map":
        values = mod["rb_map_derivative_batch"](
            fd_steps=fd, m_grid=m_grid, family=fam, kit=kit,
            detector_kind=cfg["detector_kind"], threshold=cfg["threshold"],
            n_paths=cfg["block_paths"], seed=cfg["seed_rb_map"], batch=block,
            max_steps=cfg["max_steps"], new_state=det.new_state,
            step_fn=det.step, stream_counter=mod["stream_counter"])
        unstopped, steps = 0, 0
    elif route == "fd_ladder":
        rungs = plan["fd_ladder"]["rungs"]; central = {}
        for h in rungs:
            g = mod["rb_map_batch"](family=fam, kit=kit,
                detector_kind=cfg["detector_kind"], threshold=cfg["threshold"],
                m_grid=m_grid, e_values=(h,-h), n_paths=cfg["block_paths"],
                seed=cfg["seed_fd_ladder"], batch=block, max_steps=cfg["max_steps"],
                new_state=det.new_state, step_fn=det.step,
                stream_counter=mod["stream_counter"])
            central[h] = {m: -(g[h][m]-g[-h][m])/(2.0*h) for m in m_grid}
        values = {m: central[rungs[-1]][m] for m in m_grid}
        unstopped, steps = 0, 0
    else:
        raise sh.ProducerGateError(f"unknown route {route!r}")

    cpu = time.process_time()-t_cpu
    doc = {"schema":"rebaseguard.p4za-block.v1","result_bearing":True,
           "configuration":cfg["id"],"route":route,"block":block,
           "seed":cfg[f"seed_{route}"],"block_paths":cfg["block_paths"],
           "m_grid":list(m_grid),"fd_steps":list(fd),"layer":cfg["layer"],
           "detector":cfg["detector"],"family":cfg["family"],
           "max_steps":cfg["max_steps"],"p4za_cause":cfg["p4za_cause"],
           "unstopped_paths":int(unstopped),"steps_used":int(steps),
           "block_mean":{str(m):float(values[m].mean()) for m in m_grid},
           "tail":{str(m):tail_stats(values[m]) for m in m_grid},
           "resume_identity":ident,
           "producer_hash":ctx["manifest"]["producer_hash"],
           "runtime_hash":ctx["contract"]["runtime_hash"],
           "head":ctx["head"],"cpu_seconds":cpu,
           "wall_seconds":time.time()-t_wall,
           "peak_rss_mb":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1<<20)}
    if route == "fd_ladder":
        rungs = plan["fd_ladder"]["rungs"]
        doc["central_difference_by_h"] = {
            f"{h:g}":{str(m):float(central[h][m].mean()) for m in m_grid} for h in rungs}
        doc["richardson_by_pair"] = {
            f"{c:g}/{f:g}":{str(m):float(((4.0*central[f][m]-central[c][m])/3.0).mean())
                            for m in m_grid}
            for c,f in zip(rungs[:-1],rungs[1:])}
    doc["scientific_hash"] = sh.scientific_hash(doc)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    return doc, cpu


def read_blocks(cfg, route):
    d = block_path(cfg,route,0).parent
    if not d.exists(): return []
    return [json.loads(p.read_text()) for p in sorted(d.glob(f"{route}_*.json"))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("a","full"), required=True)
    args = ap.parse_args()
    ctx = preflight(); mod = load_modules(); sh.final_producer_gate(ctx["manifest"])
    plan = ctx["plan"]; m_grid = (1,2,3,5)
    state = json.loads(STATE.read_text()) if STATE.exists() else {
        "schema":"rebaseguard.p4za-run-state.v1","cpu_seconds_total":0.0,
        "stage_a":{}, "configurations":{}}
    cap = plan["budget"]["total_cpu_cap_hours"]*3600
    cap_cfg = plan["budget"]["per_configuration_cpu_cap_hours"]*3600

    if args.stage == "a":
        # Stage-A exercises ONLY the new mechanisms, on the smallest
        # representative of each: a K7 light-tail cell, a bounded-score K3 cell,
        # and the unbounded-score skewnormal4 route.
        targets = ["reduced/sr@20/gaussian", "reduced/sr@20/logistic",
                   "reduced/sr@20/skewnormal4"]
        blocks = range(0, 20)
    else:
        if state.get("stage_a_verdict") != "P4ZA_STAGE_A_PASS":
            raise sh.ProducerGateError(
                f"full run requires P4ZA_STAGE_A_PASS; have {state.get('stage_a_verdict')!r}")
        targets = [c["id"] for c in plan["configurations"]]
        blocks = None

    for cfg in plan["configurations"]:
        if cfg["id"] not in targets: continue
        cfg_cpu = 0.0
        for route in ("rb_score","rb_map","fd_ladder"):
            span = (blocks if blocks is not None else
                    range(0, cfg["ladder_blocks"] if route=="fd_ladder" else cfg["blocks"]))
            if args.stage == "a" and route == "fd_ladder":
                span = range(0, min(20, cfg["ladder_blocks"]))
            for b in span:
                _, cpu = produce(mod, ctx, cfg, route, b, m_grid)
                cfg_cpu += cpu; state["cpu_seconds_total"] += cpu
                if state["cpu_seconds_total"] > cap:
                    state["verdict"]="K8_TOTAL_CPU_CAP"; STATE.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
                    raise SystemExit("K8: total CPU cap reached; STOP")
        if cfg_cpu > cap_cfg:
            state.setdefault("excluded",{})[cfg["id"]]="K4 per-configuration cap"
        state["configurations"][cfg["id"]] = {
            "cpu_seconds": state["configurations"].get(cfg["id"],{}).get("cpu_seconds",0.0)+cfg_cpu,
            "stage": args.stage}
        STATE.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
        print(f"  {cfg['id']:32s} cpu={cfg_cpu:8.1f}s total={state['cpu_seconds_total']/3600:6.3f}h")
    STATE.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
