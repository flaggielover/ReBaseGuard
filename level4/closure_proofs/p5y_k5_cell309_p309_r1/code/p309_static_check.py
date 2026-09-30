"""QC12: static structure of the P309 driver (package rev. 2b QC12 / FC4, as amended by rev. 2c A16).  Exit 0 iff PASS.

  python3 code/p309_static_check.py      -> evidence/fc6/STATIC_CHECK.json

T1 no path from a qualification mode (preflight, rehearse, decoy-stage1a, decoy-stage1b, _job) to a target function
   (run_execute, after_marker, evaluate_target, historical_control, cell_inputs, check_grant, _arm_marker,
   _persist_pending, run_seal_only), over the static call-and-reference graph of the driver and the rehearsal
T2 FC4: no `_TOKEN`, no `object.__setattr__`, no direct `GateResult(` construction (the module's own classmethod
   `GateResult.empty` is allowed), no store to `_REAL_GEOMETRY_ITEMS` / `REAL_GEOMETRY`, no geometry or kernel
   override passed to the adapter, and every `verdicts_from_verifier` call passes N=VERIFIER_N, max_depth=VERIFIER_DEPTH
T3 `cell_inputs` is referenced only by `historical_control`, which is referenced only by `run_execute`
T4 the exactly-once sites `_arm_marker` and `_persist_pending` begin with `_assert_execute_context(ctx)` and are
   referenced only by `run_execute`, `after_marker` and `run_seal_only`
T5 the formal quarantine scan (code/p309_scan.py) passes
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
FILES = {"p309_driver": FNS / "code" / "p309_driver.py", "p309_rehearse": FNS / "code" / "p309_rehearse.py"}
TARGET_FUNCS = {"run_execute", "after_marker", "evaluate_target", "historical_control", "cell_inputs", "check_grant",
                "_arm_marker", "_persist_pending", "run_seal_only"}
MODE_ENTRIES = {"preflight": {"check_not_evaluated", "check_bindings", "check_governance_state", "load_consumer",
                              "load_rlr307", "production_context", "load_manifest", "pin_table"},
                "rehearse": {"rehearse", "load_consumer", "load_manifest", "pin_table"},
                "decoy-stage1a": {"decoy_stage1a", "load_manifest", "pin_table"},
                "decoy-stage1b": {"decoy_stage1b", "load_manifest", "pin_table"},
                "_job": {"job_stage1a", "job_stage1b"}}
SITES = ("_arm_marker", "_persist_pending")
SITE_CALLERS = {"run_execute", "after_marker", "run_seal_only"}


def graph() -> tuple:
    """function -> set of function names it references (Name, or attribute of the driver alias D / module RH)."""
    defs, edges = {}, {}
    for key, path in FILES.items():
        tree = ast.parse(path.read_text())
        for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            name = fn.name if key == "p309_driver" else f"{fn.name}" if fn.name not in defs else f"rh.{fn.name}"
            defs[name] = fn
            refs = set()
            for n in ast.walk(fn):
                if isinstance(n, ast.Name):
                    refs.add(n.id)
                elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in ("D", "RH"):
                    refs.add(n.attr)
            edges[name] = refs
    return defs, edges


def reachable(start: set, edges: dict) -> set:
    seen, stack = set(), list(start)
    while stack:
        f = stack.pop()
        if f in seen or f not in edges:
            continue
        seen.add(f)
        stack.extend(edges[f] - seen)
    return seen


def main_mode_calls(tree) -> dict:
    """the names referenced inside each `a.mode == <m>` branch of main()."""
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    out = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and isinstance(n.test.comparators[0], ast.Constant):
            left = ast.unparse(n.test.left)
            if left == "a.mode" and isinstance(n.test.ops[0], ast.Eq):
                names = {x.id for b in n.body for x in ast.walk(b) if isinstance(x, ast.Name)} | {
                    x.attr for b in n.body for x in ast.walk(b) if isinstance(x, ast.Attribute)}
                out[n.test.comparators[0].value] = names
    return out


def run() -> dict:
    R = {}
    defs, edges = graph()
    dtree = ast.parse(FILES["p309_driver"].read_text())
    branches = main_mode_calls(dtree)
    t1 = {}
    for mode, entries in MODE_ENTRIES.items():
        refs = (branches.get(mode, set()) | entries) & set(defs)
        hit = sorted(reachable(refs, edges) & TARGET_FUNCS)
        t1[mode] = hit
    job = next(n for n in ast.walk(dtree) if isinstance(n, ast.If) and "_job" in ast.unparse(n.test))
    jobrefs = {x.id for b in job.body for x in ast.walk(b) if isinstance(x, ast.Name)} & set(defs)
    t1["_job"] = sorted(reachable(jobrefs | MODE_ENTRIES["_job"], edges) & TARGET_FUNCS)
    R["T1_no_path_from_qualification_modes_to_target"] = {"pass": not any(t1.values()), "detail": t1}
    bad = []
    for key, path in FILES.items():
        tree = ast.parse(path.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and n.id == "_TOKEN" or isinstance(n, ast.Attribute) and n.attr == "_TOKEN":
                bad.append(f"{key}:{n.lineno}:_TOKEN")
            if isinstance(n, ast.Attribute) and n.attr == "__setattr__" and isinstance(n.value, ast.Name) and \
                    n.value.id == "object":
                bad.append(f"{key}:{n.lineno}:object.__setattr__")
            if isinstance(n, ast.Call) and ((isinstance(n.func, ast.Name) and n.func.id == "GateResult") or (
                    isinstance(n.func, ast.Attribute) and n.func.attr == "GateResult")):
                bad.append(f"{key}:{n.lineno}:GateResult(")
            if isinstance(n, (ast.Name, ast.Attribute)) and getattr(n, "ctx", None).__class__ is ast.Store and (
                    getattr(n, "id", None) in ("_REAL_GEOMETRY_ITEMS", "REAL_GEOMETRY") or
                    getattr(n, "attr", None) in ("_REAL_GEOMETRY_ITEMS", "REAL_GEOMETRY")):
                bad.append(f"{key}:{n.lineno}:geometry rebinding")
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "srk_enclosure":
                kws = {k.arg for k in n.keywords}
                if kws - {"verifier_id"}:
                    bad.append(f"{key}:{n.lineno}:adapter override {sorted(kws)}")
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "verdicts_from_verifier":
                kw = {k.arg: ast.unparse(k.value) for k in n.keywords}
                if kw.get("N") not in ("VERIFIER_N", "D.VERIFIER_N") or kw.get("max_depth") not in (
                        "VERIFIER_DEPTH", "D.VERIFIER_DEPTH"):
                    bad.append(f"{key}:{n.lineno}:verdicts_from_verifier without the pinned N/max_depth")
    R["T2_fc4_static_items"] = {"pass": not bad, "detail": bad}
    referrers = {f: {g for g, refs in edges.items() if f in refs and g != f} for f in ("cell_inputs",
                                                                                       "historical_control")}
    R["T3_target_inputs_only_via_the_control"] = {
        "pass": referrers["cell_inputs"] == {"historical_control"} and referrers["historical_control"] == {
            "run_execute"}, "detail": {k: sorted(v) for k, v in referrers.items()}}
    t4 = {}
    for s in SITES:
        fn = defs[s]
        first = fn.body[0]
        starts = (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call) and
                  ast.unparse(first.value) == "_assert_execute_context(ctx)")
        callers = {g for g, refs in edges.items() if s in refs and g != s}
        t4[s] = {"starts_with_assert": starts, "referrers": sorted(callers), "ok": starts and callers <= SITE_CALLERS}
    R["T4_exactly_once_sites"] = {"pass": all(v["ok"] for v in t4.values()), "detail": t4}
    sc = subprocess.run([sys.executable, str(FNS / "code" / "p309_scan.py")], capture_output=True, text=True)
    try:
        verdict = json.loads(sc.stdout)["verdict"]
    except ValueError:
        verdict = "UNREADABLE"
    R["T5_formal_scan"] = {"pass": verdict == "PASS", "detail": verdict}
    return R


if __name__ == "__main__":
    sys.path.insert(0, str(FNS / "code"))
    import p309_env as E
    E.log("code/p309_static_check.py", "QC12 static structure (AST)", klass="GOVERNANCE", notes="static only")
    r = run()
    ok = all(v["pass"] for v in r.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": ok,
           "driver_sha256": hashlib.sha256(FILES["p309_driver"].read_bytes()).hexdigest(),
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": r}
    (E.evidence_dir("fc6") / "STATIC_CHECK.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in r.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}  {'' if v['pass'] else v['detail']}")
    sys.exit(0 if ok else 1)
