#!/usr/bin/env python3
"""P4Z production driver -- the only result-bearing entry point.

Consumes the frozen checkpoint, the frozen campaign plan and the frozen Stage-0
design, and nothing else.  Makes no interactive scientific decision, never tops
up, never increases a path count, and never chooses a threshold.  Every failure
mode is fail-closed: a missing artifact, a dirty TCB, a runtime drift, an
unknown scientific field or a module resolved outside the manifest aborts the
run rather than degrading it.

Resumability is by block: each (configuration, route, block) is written as its
own JSON file keyed by a resume identity derived from the producer hash, the
runtime hash, the configuration, the route, the seed and the block index.  A
block whose key does not match is discarded, not adapted.

Usage:
  run_p4z.py --stage 0            Stage-0 pilot, blocks 0..19
  run_p4z.py --stage 1            full qualification, blocks 20..199
  run_p4z.py --adjudicate         evaluate gates over completed blocks
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(NS / "src"))
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))

import numpy as np  # noqa: E402

import runtime_contract as rc  # noqa: E402
import scientific_hash as sh  # noqa: E402

BLOCK_DIR = NS / "production" / "blocks"
STATE_PATH = NS / "production" / "run_state.json"


# --------------------------------------------------------------------------
# fail-closed preflight
# --------------------------------------------------------------------------

def preflight() -> dict[str, object]:
    rc.enforce_environment()
    head = sh.refuse_dirty_scientific_state()
    contract = rc.verify(rc.CONTRACT_PATH)
    manifest = sh.build_manifest()

    plan = json.loads((NS / "production" / "campaign_plan.json").read_text())
    checkpoint = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
    stage0 = json.loads((NS / "production" / "stage0_freeze.json").read_text())
    protocol = json.loads(
        (NS.parent / "p4_theory_generalization" / "configs" / "P4_PROTOCOL.json").read_text())

    # threshold locks: the plan may not have drifted from the frozen sources
    gates = protocol["gates"]
    if plan["thresholds"]["relative"] != gates["correspondence_relative_limit"] != 0.03:
        raise sh.ProducerGateError("relative threshold drift")
    if plan["thresholds"]["z"] != gates["correspondence_z_limit"] != 4.0:
        raise sh.ProducerGateError("z threshold drift")
    if plan["thresholds"]["r_star"] != checkpoint["gate_thresholds_unchanged"]["r_star"]:
        raise sh.ProducerGateError("r* drift")
    if plan["fd_steps"] != protocol["fd_steps"] != [0.05, 0.025]:
        raise sh.ProducerGateError("finite-difference convention drift")
    if plan["fixed_policy"]["blocks_per_route_full"] != 200:
        raise sh.ProducerGateError("block policy drift")
    if plan["fixed_policy"]["adaptive"] or plan["fixed_policy"]["top_ups_permitted"]:
        raise sh.ProducerGateError("adaptive stopping is not permitted")
    if checkpoint["estimators"]["primary"]["name"] != "RB-SCORE":
        raise sh.ProducerGateError("primary estimator is not RB-SCORE")
    if checkpoint["estimators"]["fallback"]["name"] != "RB-MAP":
        raise sh.ProducerGateError("companion route is not RB-MAP")
    if plan["execution"] != {"workers": 1, "blas_threads": 1}:
        raise sh.ProducerGateError("execution configuration drift")

    return {"head": head, "contract": contract, "manifest": manifest,
            "plan": plan, "checkpoint": checkpoint, "stage0": stage0,
            "protocol": protocol}


def load_scientific_modules():
    """Import every scientific module BEFORE the final producer gate."""
    from rebaseguard_p4_general.detectors import Detector, K_FROZEN  # noqa: PLC0415
    from rebaseguard_p4_general.families import REGISTRY  # noqa: PLC0415
    from rebaseguard_p4_general.simulate import stream_counter  # noqa: PLC0415
    from rebaseguard_p4z.analytic import (  # noqa: PLC0415
        FAMILY_KITS, alarm_bounds, alarm_integrals,
    )
    from rebaseguard_p4z.rbscore import rb_score_batch  # noqa: PLC0415
    from rebaseguard_p4z.rbmap import rb_map_derivative_batch  # noqa: PLC0415
    return dict(Detector=Detector, K_FROZEN=K_FROZEN, REGISTRY=REGISTRY,
                stream_counter=stream_counter, FAMILY_KITS=FAMILY_KITS,
                alarm_bounds=alarm_bounds, alarm_integrals=alarm_integrals,
                rb_score_batch=rb_score_batch,
                rb_map_derivative_batch=rb_map_derivative_batch)


# --------------------------------------------------------------------------
# kill gates K1 and K2 -- trusted computing base, before any block
# --------------------------------------------------------------------------

def gate_k1(mod, plan, tol: float) -> dict[str, object]:
    """Every family's four alarm-set integrals, against adaptive quadrature."""
    from scipy.integrate import quad  # noqa: PLC0415
    families = plan["scope"]["families_theorem_supported"]
    alarm_sets = [(-3.0, 2.5), (-5.5, 5.5), (-1.2, 0.9), (-7.0, 3.3), (-0.6, 0.4)]
    worst, rows = 0.0, []
    for name in families:
        kit = mod["FAMILY_KITS"][name]
        psi = mod["REGISTRY"][name].psi
        for lower, upper in alarm_sets:
            def tails(g):
                return (quad(g, -np.inf, lower, limit=500)[0]
                        + quad(g, upper, np.inf, limit=500)[0])
            want = (tails(kit.pdf),
                    tails(lambda t: t * kit.pdf(t)),
                    tails(lambda t: t * float(psi(np.array([t]))[0]) * kit.pdf(t)),
                    tails(lambda t: float(psi(np.array([t]))[0]) * kit.pdf(t)))
            got = mod["alarm_integrals"](kit, np.array([lower]), np.array([upper]))
            err = max(abs(float(np.ravel(g)[0]) - w) for g, w in zip(got, want))
            worst = max(worst, err)
            rows.append({"family": name, "lower": lower, "upper": upper,
                         "max_abs_error": err})
    return {"gate": "K1", "worst_abs_error": worst, "tolerance": tol,
            "fired": worst > tol, "rows": rows}


def gate_k2(mod, plan, n_probe: int) -> dict[str, object]:
    """alarm_bounds must reproduce the frozen Detector.step crossing flag."""
    rng = np.random.Generator(np.random.PCG64([4090004, 0]))
    checked, mismatches = 0, 0
    for layer in ("reduced", "frozen"):
        for cfg in plan["configurations"]:
            if cfg["layer"] != layer or cfg["family"] != "laplace":
                continue
            det = mod["Detector"](cfg["detector_kind"], cfg["threshold"])
            fam = mod["REGISTRY"]["laplace"]
            n = 4000
            up, down = det.new_state(n)
            active = np.ones(n, bool)
            for step in range(1, 400):
                idx = np.flatnonzero(active)
                if idx.size == 0 or checked >= n_probe:
                    break
                lower, upper = mod["alarm_bounds"](
                    cfg["detector_kind"], cfg["threshold"], up[idx], down[idx],
                    mod["K_FROZEN"])
                z = fam.sample(rng, (int(idx.size),))
                predicted = (z >= upper) | (z <= lower)
                nu_, nd_, crossed = det.step(up[idx], down[idx], z, step)
                mismatches += int(np.count_nonzero(predicted != crossed))
                checked += int(idx.size)
                up[idx], down[idx] = nu_, nd_
                active[idx[crossed]] = False
    return {"gate": "K2", "residuals_checked": checked,
            "mismatches": mismatches, "fired": mismatches > 0}


# --------------------------------------------------------------------------
# block production
# --------------------------------------------------------------------------

def resume_identity(producer_hash, runtime_hash_, cfg_id, route, seed, block) -> str:
    return hashlib.sha256(
        f"{producer_hash}|{runtime_hash_}|{cfg_id}|{route}|{seed}|{block}".encode()
    ).hexdigest()


def block_path(cfg, route, block) -> Path:
    safe = cfg["id"].replace("/", "__").replace("@", "_at_")
    return BLOCK_DIR / safe / f"{route}_{block:04d}.json"


def tail_stats(x: np.ndarray) -> dict[str, float]:
    x = np.asarray(x, float)
    dev = (x - x.mean()) ** 2
    total = float(dev.sum())
    order = np.sort(dev)[::-1]
    k = max(10, x.size // 200)
    absdev = np.sort(np.abs(x - x.mean()))[::-1][: k + 1]
    hill = (float(1.0 / np.mean(np.log(absdev[:k] / absdev[k])))
            if absdev[k] > 0 else float("nan"))
    return {"top1_share": float(order[0] / total) if total > 0 else 0.0,
            "top5_share": float(order[:5].sum() / total) if total > 0 else 0.0,
            "hill_index": hill, "per_path_sd": float(x.std(ddof=1))}


def produce_block(mod, ctx, cfg, route, block, fd_steps, m_grid):
    path = block_path(cfg, route, block)
    ident = resume_identity(ctx["manifest"]["producer_hash"],
                            ctx["contract"]["runtime_hash"], cfg["id"], route,
                            cfg[f"seed_{route}"], block)
    if path.exists():
        existing = json.loads(path.read_text())
        if existing.get("resume_identity") == ident:
            return existing, 0.0
        raise sh.ProducerGateError(
            f"resume identity mismatch for {path}: a block produced under a "
            "different producer, runtime, seed or configuration cannot be pooled")

    fam = mod["REGISTRY"][cfg["family"]]
    kit = mod["FAMILY_KITS"][cfg["family"]]
    det = mod["Detector"](cfg["detector_kind"], cfg["threshold"])
    t_cpu, t_wall = time.process_time(), time.time()

    if route == "rb_score":
        rng = np.random.Generator(np.random.PCG64([cfg["seed_rb_score"], block]))
        values, unstopped, steps = mod["rb_score_batch"](
            family=fam, kit=kit, detector_kind=cfg["detector_kind"],
            threshold=cfg["threshold"], m_grid=m_grid,
            n_paths=cfg["block_paths"], rng=rng, max_steps=cfg["max_steps"],
            new_state=det.new_state, step_fn=det.step)
    elif route == "fd_ladder":
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
    elif route == "rb_map":
        values = mod["rb_map_derivative_batch"](
            fd_steps=fd_steps, m_grid=m_grid, family=fam, kit=kit,
            detector_kind=cfg["detector_kind"], threshold=cfg["threshold"],
            n_paths=cfg["block_paths"], seed=cfg["seed_rb_map"], batch=block,
            max_steps=cfg["max_steps"], new_state=det.new_state,
            step_fn=det.step, stream_counter=mod["stream_counter"])
        unstopped, steps = 0, 0
    else:
        raise sh.ProducerGateError(f"unknown route {route!r}")

    cpu = time.process_time() - t_cpu
    doc = {
        "schema": "rebaseguard.p4z-block.v1",
        "result_bearing": True,
        "configuration": cfg["id"], "route": route, "block": block,
        "seed": cfg[f"seed_{route}"], "block_paths": cfg["block_paths"],
        "m_grid": list(m_grid), "fd_steps": list(fd_steps),
        "layer": cfg["layer"], "detector": cfg["detector"],
        "family": cfg["family"], "max_steps": cfg["max_steps"],
        "unstopped_paths": int(unstopped), "steps_used": int(steps),
        "block_mean": {str(m): float(values[m].mean()) for m in m_grid},
        "tail": {str(m): tail_stats(values[m]) for m in m_grid},
        "resume_identity": ident,
        "producer_hash": ctx["manifest"]["producer_hash"],
        "runtime_hash": ctx["contract"]["runtime_hash"],
        "head": ctx["head"],
        "cpu_seconds": cpu,
        "wall_seconds": time.time() - t_wall,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20),
    }
    if route == "fd_ladder":
        doc["central_difference_by_h"] = {
            f"{h:g}": {str(m): float(central[h][m].mean()) for m in m_grid}
            for h in ctx["plan"]["fd_ladder_steps"]}
        ladder = ctx["plan"]["fd_ladder_steps"]
        doc["richardson_by_pair"] = {
            f"{c:g}/{f:g}": {
                str(m): float(((4.0 * central[f][m] - central[c][m]) / 3.0).mean())
                for m in m_grid}
            for c, f in zip(ladder[:-1], ladder[1:])}
    doc["scientific_hash"] = sh.scientific_hash(doc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return doc, cpu


# --------------------------------------------------------------------------
# stages
# --------------------------------------------------------------------------

def load_state() -> dict[str, object]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"schema": "rebaseguard.p4z-run-state.v1",
            "cpu_seconds_total": 0.0, "stages": {}, "excluded": {},
            "killed": {}}


def save_state(state) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def run_stage(stage: int) -> int:
    ctx = preflight()
    mod = load_scientific_modules()
    sh.final_producer_gate(ctx["manifest"])          # AFTER all scientific imports

    plan, stage0 = ctx["plan"], ctx["stage0"]
    m_grid = tuple(plan["scope"]["m_grid"])
    fd_steps = tuple(plan["fd_steps"])
    params = stage0["kill_gate_parameters"]
    state = load_state()

    cap_total = plan["budget"]["total_cpu_cap_hours"] * 3600.0
    cap_config = plan["budget"]["per_configuration_cpu_cap_hours"] * 3600.0

    if stage == 0:
        k1 = gate_k1(mod, plan, params["K1_quadrature_tolerance"])
        k2 = gate_k2(mod, plan, params["K2_probe_residuals"])
        state["stages"]["0_tcb_gates"] = {
            "K1": {k: v for k, v in k1.items() if k != "rows"}, "K2": k2}
        save_state(state)
        print(f"K1 worst |error| {k1['worst_abs_error']:.3e} "
              f"(tol {k1['tolerance']:.0e})  fired={k1['fired']}")
        print(f"K2 residuals {k2['residuals_checked']:,} mismatches "
              f"{k2['mismatches']}  fired={k2['fired']}")
        if k1["fired"] or k2["fired"]:
            state["verdict"] = "STAGE0_KILLED"
            save_state(state)
            raise SystemExit("STAGE0_KILLED: a trusted-computing-base gate fired")
        blocks = range(0, plan["fixed_policy"]["blocks_per_route_stage0"])
    else:
        if state.get("stage0_verdict") != "STAGE0_PASS":
            raise sh.ProducerGateError(
                "stage 1 requires STAGE0_PASS; current stage-0 verdict is "
                f"{state.get('stage0_verdict')!r}")
        blocks = range(plan["fixed_policy"]["blocks_per_route_stage0"],
                       plan["fixed_policy"]["blocks_per_route_full"])

    envelopes = json.loads(
        (NS / "results" / "estimator_feasibility.json").read_text())["regime_envelopes"]

    for cfg in plan["configurations"]:
        if cfg["id"] in state.get("excluded", {}) or cfg["id"] in state.get("killed", {}):
            print(f"skip {cfg['id']} ({state.get('excluded', {}).get(cfg['id']) or state['killed'][cfg['id']]})")
            continue
        cfg_cpu = 0.0
        routes = (("rb_score", "rb_map", "fd_ladder") if stage == 0
                  else ("rb_score", "rb_map"))
        for route in routes:
            span = (range(0, plan["fd_ladder_blocks"])
                    if route == "fd_ladder" else blocks)
            for block in span:
                doc, cpu = produce_block(mod, ctx, cfg, route, block,
                                         fd_steps, m_grid)
                cfg_cpu += cpu
                state["cpu_seconds_total"] += cpu
                if state["cpu_seconds_total"] > cap_total:
                    state["verdict"] = "K8_TOTAL_CPU_CAP"
                    save_state(state)
                    raise SystemExit("K8: total CPU cap reached; STOP")
        # K3 / K4 are Stage-0 gates only, and read cost and variance only
        if stage == 0:
            env = envelopes[cfg["regime"]]
            measured = _measured_relative_sd(cfg, m_grid)
            k3_limit = math.sqrt(params["K3_variance_safety_factor"]) * max(
                env["rb_score_relative_sd_per_path"],
                env["rb_map_relative_sd_per_path"])
            projected = _project_cpu(cfg, cfg_cpu, plan)
            row = {"measured_relative_sd_per_path": measured,
                   "K3_limit": k3_limit, "K3_fired": measured > k3_limit,
                   "stage0_cpu_seconds": cfg_cpu,
                   "projected_full_cpu_seconds": projected,
                   "K4_limit_seconds": cap_config,
                   "K4_fired": projected > cap_config}
            state.setdefault("stage0_configurations", {})[cfg["id"]] = row
            if row["K3_fired"]:
                state.setdefault("killed", {})[cfg["id"]] = "K3 variance model exceeded"
            if row["K4_fired"]:
                state.setdefault("excluded", {})[cfg["id"]] = "K4 budget excluded"
            flag = ("K3" if row["K3_fired"] else "") + ("K4" if row["K4_fired"] else "")
            print(f"  {cfg['id']:32s} relsd={measured:6.3f}/{k3_limit:6.3f} "
                  f"cpu={cfg_cpu:7.1f}s proj={projected/3600:6.3f}h "
                  f"{'** ' + flag if flag else 'ok'}")
        else:
            print(f"  {cfg['id']:32s} cpu={cfg_cpu:8.1f}s "
                  f"total={state['cpu_seconds_total']/3600:6.3f}h")
        save_state(state)

    if stage == 0:
        state["stage0_verdict"] = _stage0_verdict(state, plan)
        print(f"\nSTAGE-0 VERDICT = {state['stage0_verdict']}")
    save_state(state)
    return 0


def _measured_relative_sd(cfg, m_grid) -> float:
    """Worst per-path relative sd over m and route, from the produced blocks."""
    worst = 0.0
    for route in ("rb_score", "rb_map"):
        docs = _read_blocks(cfg, route)
        if not docs:
            continue
        for m in m_grid:
            means = np.array([d["block_mean"][str(m)] for d in docs])
            sds = np.array([d["tail"][str(m)]["per_path_sd"] for d in docs])
            mu = float(means.mean())
            if mu != 0:
                worst = max(worst, float(sds.mean()) / abs(mu))
    return worst


def _project_cpu(cfg, stage0_cpu, plan) -> float:
    done = plan["fixed_policy"]["blocks_per_route_stage0"]
    total = plan["fixed_policy"]["blocks_per_route_full"]
    return stage0_cpu * total / done


def _stage0_verdict(state, plan) -> str:
    residue = {c["id"] for c in plan["configurations"]
               if c["carries_unresolved_cells"]}
    blocked = set(state.get("killed", {})) | set(state.get("excluded", {}))
    if residue & blocked:
        return "STAGE0_INCONCLUSIVE"
    return "STAGE0_PASS"


def _read_blocks(cfg, route) -> list[dict]:
    directory = block_path(cfg, route, 0).parent
    if not directory.exists():
        return []
    return [json.loads(p.read_text())
            for p in sorted(directory.glob(f"{route}_*.json"))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=(0, 1))
    ap.add_argument("--adjudicate", action="store_true")
    args = ap.parse_args()
    if args.adjudicate:
        import adjudicate  # noqa: PLC0415
        return adjudicate.main()
    if args.stage is None:
        ap.error("one of --stage or --adjudicate is required")
    return run_stage(args.stage)


if __name__ == "__main__":
    raise SystemExit(main())
