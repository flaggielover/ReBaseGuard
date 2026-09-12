#!/usr/bin/env python3
"""Derive the RNG manifest of every campaign in the P4Z line, from artifacts.

Nothing here is hand-copied.  Production stream blocks are read from the stored
*block* files, so the manifest records the addresses a campaign actually
consumed rather than the ones its plan authorised.  Calibration stream blocks
are parsed out of the frozen diagnostic scripts and cross-checked against the
stored diagnostic JSON wherever that JSON records the seed.

Every constant this script extracts is asserted, so an edit to a frozen
historical script makes the build fail loudly instead of silently changing the
disclosure.

NOT RESULT BEARING.  Reads only; writes only into the P4ZR namespace.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
P4Z = CP / "p4z_location_family_feasibility"
P4ZA = CP / "p4za_fullscope_closure"
P4ZB = CP / "p4zb_skewnormal4_k7"

#: route -> bit generator, fixed by the frozen runners.  ``rb_score`` builds
#: ``np.random.Generator(np.random.PCG64([seed, block]))``; ``rb_map`` and
#: ``fd_ladder`` call ``rb_map_batch(seed=..., batch=block)``, which keys
#: ``np.random.Philox``.
ROUTE_GENERATOR = {"rb_score": "PCG64", "rb_map": "PHILOX", "fd_ladder": "PHILOX"}


def module_constants(path: Path, names: set[str]) -> dict:
    """Literal module-level constants of a frozen script, by AST, no import."""
    tree = ast.parse(path.read_text())
    out: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    out[t.id] = ast.literal_eval(node.value)
    return out


def argparse_default(path: Path, option: str):
    """The literal default of an ``add_argument`` option in a frozen script."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == option):
            for kw in node.keywords:
                if kw.arg == "default":
                    return ast.literal_eval(kw.value)
    raise AssertionError(f"no default for {option} in {path.name}")


def local_assignment(path: Path, func: str, names: tuple[str, ...]) -> dict:
    """Literal tuple assignment inside a function, e.g. ``a, b, c = 1, 2, 3``."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func:
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Tuple)):
                    ids = tuple(e.id for e in stmt.targets[0].elts
                                if isinstance(e, ast.Name))
                    if ids == names:
                        return dict(zip(ids, ast.literal_eval(stmt.value)))
    raise AssertionError(f"no {names} assignment in {func}() of {path.name}")


def rb_map_seed_offset(path: Path) -> int:
    """The ``seed + k`` offset the script passes to the Philox-keyed route."""
    src = path.read_text()
    m = re.search(r"seed\s*=\s*seed\s*\+\s*(\d+)", src)
    if m:
        return int(m.group(1))
    assert re.search(r"seed\s*=\s*(SEED|seed)\s*,", src), \
        f"cannot determine the rb_map seed expression in {path.name}"
    return 0


def consumed_production_streams(campaign_dir: Path, plan: dict) -> list[dict]:
    """Production stream blocks, read from the stored block files."""
    blocks_dir = campaign_dir / "production" / "blocks"
    assert blocks_dir.is_dir(), f"no stored blocks under {blocks_dir}"
    seen: dict[tuple[str, str], list[int]] = {}
    for cfg_dir in sorted(blocks_dir.iterdir()):
        if not cfg_dir.is_dir():
            continue
        for f in sorted(cfg_dir.glob("*.json")):
            route = re.sub(r"_\d+\.json$", "", f.name)
            doc = json.loads(f.read_text())
            key = (doc["configuration"], route)
            seen.setdefault(key, []).append(int(doc["block"]))
            # the block records its own seed; assert it matches the plan
            assert int(doc["seed"]) == plan_seed(plan, doc["configuration"], route), (
                f"block {f} seed {doc['seed']} disagrees with the frozen plan")
    out = []
    for (cid, route), batches in sorted(seen.items()):
        out.append({
            "generator": ROUTE_GENERATOR[route],
            "key": plan_seed(plan, cid, route),
            "batch_lo": min(batches), "batch_hi": max(batches),
            "configuration": cid, "route": route,
            "blocks_consumed": len(batches),
        })
    return out


def plan_configs(plan: dict) -> list[dict]:
    cfg = plan.get("configurations")
    if cfg is None:                      # P4ZB freezes a single configuration
        cfg = [plan["configuration"]]
    return cfg


def plan_seed(plan: dict, configuration: str, route: str) -> int:
    for c in plan_configs(plan):
        if c["id"] == configuration:
            return int(c[f"seed_{route}"])
    raise AssertionError(f"{configuration} not in the frozen plan")


# ---------------------------------------------------------------------------
# per-campaign calibration declarations, parsed from the frozen scripts
# ---------------------------------------------------------------------------

def p4z_calibration() -> list[dict]:
    mp = P4Z / "micropilots" / "run_micropilots.py"
    fd = P4Z / "micropilots" / "run_fd_ladder.py"

    mp_seed = argparse_default(mp, "--seed")
    mp_batches = argparse_default(mp, "--batches")
    mp_offset = rb_map_seed_offset(mp)
    stored = json.loads((P4Z / "micropilots" / "diagnostics" / "micropilot.json").read_text())
    assert stored["seed"] == mp_seed and stored["batches"] == mp_batches, (
        "run_micropilots.py defaults disagree with the stored diagnostic")
    assert stored["result_bearing"] is False
    # Candidate B runs max(2, batches // 2) blocks.
    mp_map_batches = max(2, mp_batches // 2)

    fd_local = local_assignment(fd, "main", ("batches", "paths", "seed"))
    fd_seed, fd_batches = fd_local["seed"], fd_local["batches"]
    fd_offset = rb_map_seed_offset(fd)
    fd_stored = json.loads((P4Z / "micropilots" / "diagnostics" / "fd_ladder.json").read_text())
    assert fd_stored["result_bearing"] is False

    return [
        {"label": "micropilots/run_micropilots.py :: RB-SCORE candidate",
         "streams": [{"generator": "PCG64", "key": mp_seed,
                      "batch_lo": 0, "batch_hi": mp_batches - 1,
                      "configuration": "5 diagnostic cells (not a production id)",
                      "route": "rb_score-kernel"}]},
        {"label": "micropilots/run_micropilots.py :: historical Route-A tail check",
         "streams": [{"generator": "PCG64", "key": mp_seed,
                      "batch_lo": 0, "batch_hi": 0,
                      "configuration": "5 diagnostic cells (not a production id)",
                      "route": "simulate_group(mode='compact')"}]},
        {"label": "micropilots/run_micropilots.py :: RB-MAP candidate",
         "streams": [{"generator": "PHILOX", "key": mp_seed + mp_offset,
                      "batch_lo": 0, "batch_hi": mp_map_batches - 1,
                      "configuration": "5 diagnostic cells (not a production id)",
                      "route": "rb_map-kernel"}]},
        {"label": "micropilots/run_fd_ladder.py :: RB-SCORE reference",
         "streams": [{"generator": "PCG64", "key": fd_seed,
                      "batch_lo": 0, "batch_hi": fd_batches - 1,
                      "configuration": "2 diagnostic cells (not a production id)",
                      "route": "rb_score-kernel"}]},
        {"label": "micropilots/run_fd_ladder.py :: FD ladder",
         "streams": [{"generator": "PHILOX", "key": fd_seed + fd_offset,
                      "batch_lo": 0, "batch_hi": fd_batches - 1,
                      "configuration": "2 diagnostic cells (not a production id)",
                      "route": "rb_map-kernel"}]},
    ]


def p4za_calibration() -> list[dict]:
    cal = P4ZA / "audit" / "calibrate_ladder.py"
    c = module_constants(cal, {"SEED", "BLOCKS"})
    stored = json.loads((P4ZA / "results" / "ladder_calibration.json").read_text())
    assert stored["seed"] == c["SEED"] and stored["blocks"] == c["BLOCKS"], (
        "calibrate_ladder.py constants disagree with the stored calibration")
    assert stored["result_bearing"] is False
    return [
        {"label": "audit/calibrate_ladder.py :: FD ladder micro-calibration",
         "streams": [{"generator": "PHILOX", "key": c["SEED"],
                      "batch_lo": 0, "batch_hi": c["BLOCKS"] - 1,
                      "configuration": "4 calibration cells (not a production id)",
                      "route": "rb_map-kernel"}]},
    ]


def p4zb_calibration() -> list[dict]:
    st = P4ZB / "audit" / "ladder_study.py"
    c = module_constants(st, {"SEED", "BLOCKS"})
    stored = json.loads((P4ZB / "results" / "ladder_study.json").read_text())
    assert stored["seed"] == c["SEED"] and stored["blocks"] == c["BLOCKS"], (
        "ladder_study.py constants disagree with the stored study")
    assert stored["result_bearing"] is False
    return [
        {"label": "audit/ladder_study.py :: out-of-sample ladder study",
         "streams": [{"generator": "PHILOX", "key": c["SEED"],
                      "batch_lo": 0, "batch_hi": c["BLOCKS"] - 1,
                      "configuration": "frozen/cusum@5/skewnormal4 (study only)",
                      "route": "rb_map-kernel"}]},
    ]


CAMPAIGNS = {
    "P4Z": (P4Z, "production/campaign_plan.json", p4z_calibration),
    "P4ZA": (P4ZA, "production/p4za_campaign_plan.json", p4za_calibration),
    "P4ZB": (P4ZB, "production/p4zb_campaign_plan.json", p4zb_calibration),
}


def build(name: str) -> dict:
    campaign_dir, plan_rel, cal_fn = CAMPAIGNS[name]
    plan = json.loads((campaign_dir / plan_rel).read_text())
    programs = [dict(p, **{"class": "calibration", "result_bearing": False})
                for p in cal_fn()]
    programs.append({
        "label": f"{name} production runner",
        "class": "production", "result_bearing": True,
        "streams": consumed_production_streams(campaign_dir, plan),
    })
    return {
        "schema": "rebaseguard.campaign-rng-manifest.v1",
        "campaign": name,
        "derived_from": {
            "plan": plan_rel,
            "production_streams": "read from the stored production block files",
            "calibration_streams": "parsed from the frozen diagnostic scripts "
                                   "and cross-checked against the stored "
                                   "diagnostic JSON",
        },
        "result_bearing": False,
        "programs": programs,
    }


def main() -> int:
    out_dir = NS / "results" / "rng_manifests"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in CAMPAIGNS:
        doc = build(name)
        p = out_dir / f"{name.lower()}_rng_manifest.json"
        p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        print(f"{name}: {sum(len(x['streams']) for x in doc['programs'])} "
              f"stream blocks -> {p.relative_to(NS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
