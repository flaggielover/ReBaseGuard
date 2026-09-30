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
T6 (owner D5: no mutation reachable without a valid owner grant) dominance in the driver:
   * run_execute: its first statement refuses test hooks outside a sandbox (R4 NB4); check_grant, then the dry
     admission (premarker_admission), then the run nonce, then the single _arm_marker call, then after_marker, each in
     a top-level statement (or the body of a top-level try), in that order;
   * run_seal_only: the single _persist_pending call is preceded, in its block, by the three refusals (no marker; the
     marker names no grant commit; the evidence is bound to another commit);
   * after_marker is referenced only by run_execute
T7 (owner D5: no qualification or test path can mutate the production refs) outside the driver and the post-execution
   tool: no reference to production_context, _arm_marker, _persist_pending, after_marker, reverify_production, _MODE,
   _assert_execute_context, _site_backstop, _SITE_CODES or _require_own_run_nonce; no ExecContext construction; every
   run_execute / run_seal_only call passes an explicit, non-None context; no subprocess call runs the driver in
   `execute` or `seal-only` mode.  R4 follow-up F1(c): also no `from p309_driver import` of those names (or of G or *),
   no `from p309_guard import PRODUCTION` (or *); no __dict__ / getattr / setattr / delattr / hasattr / vars on the
   driver or guard module, no sys.modules / import_module / __import__ access to them; no attribute store or delete on
   the driver module (except the QC11 stub point `persist_emergency`) or on the guard module; no reference to the
   guard's PRODUCTION context; in tests and the qualification tools, no string constant naming a forbidden name; and
   every `python -c` code string is parsed and checked by the same rules.  A file listed in config `t7_exemptions`
   (module AST sha256, the exempted rules, a reason) is exempt from exactly those rules.
T8 (R4 follow-up F1(a)) the runtime backstop: _assert_execute_context ends by refusing any caller that is not one of the
   two sites (NOT_A_SITE, through _SITE_CODES of their code objects) and then calls _site_backstop; _site_backstop's
   arm branch requires execute mode, G.premarker_check and the run nonce of this process; its pending branch requires
   the marker and the grant path at the marker; _SITE_CODES maps exactly the two sites' code objects and is the only
   module-level reference to them
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
T7_EXEMPT = {"code/p309_driver.py"}          # R4F2-C1(h): p309_postexec.py has a rule-specific, hash-bound exemption
T7_FORBIDDEN = {"production_context", "_arm_marker", "_persist_pending", "after_marker", "reverify_production", "_MODE",
                "_assert_execute_context", "_site_backstop", "_SITE_CODES", "_require_own_run_nonce"}
T7_STRING_SCOPE = ("tests/", "code/p309_qualify.py", "code/p309_rehearse.py", "verify/run_verify_all_scoped.py")
ALLOW = json.loads((FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_text())
TARGET_FUNCS = {"run_execute", "after_marker", "evaluate_target", "historical_control", "cell_inputs", "check_grant",
                "_arm_marker", "_persist_pending", "run_seal_only"}
MODE_ENTRIES = {"preflight": {"check_not_evaluated", "check_bindings", "check_governance_state", "load_consumer",
                              "load_rlr307", "production_context", "load_manifest", "pin_table"},
                "rehearse": {"rehearse", "load_consumer", "load_manifest", "pin_table"},
                "decoy-stage1a": {"decoy_stage1a", "load_manifest", "pin_table"},
                "decoy-stage1b": {"decoy_stage1b", "load_manifest", "pin_table"},
                "validate-grant": {"validate_grant", "check_flags", "check_branch", "check_not_evaluated",
                                   "check_result_paths", "check_clean", "check_bindings", "check_governance_state",
                                   "check_host_git"},
                "_job": {"job_stage1a", "job_stage1b"}}
SITES = ("_arm_marker", "_persist_pending")
SITE_CALLERS = {"run_execute", "after_marker", "run_seal_only"}


def graph(files=None) -> tuple:
    """function -> set of function names it references (Name, or attribute of the driver alias D / module RH)."""
    defs, edges = {}, {}
    for key, path in (files or FILES).items():
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


def _chain_ok(fn, target) -> bool:
    """the call node `target` lies in a top-level statement of fn, or in the body of a top-level try (no branch,
    loop, with or handler on the way)"""
    for st in fn.body:
        if target in list(ast.walk(st)):
            if isinstance(st, ast.Try):
                return any(target in list(ast.walk(b)) for b in st.body) and not any(
                    target in list(ast.walk(h)) for h in st.handlers + st.finalbody + st.orelse) and not any(
                    isinstance(x, (ast.If, ast.For, ast.While, ast.With, ast.Try)) and target in list(ast.walk(x))
                    for b in st.body for x in ast.walk(b))
            return not any(isinstance(x, (ast.If, ast.For, ast.While, ast.With, ast.Try))
                           and target in list(ast.walk(x)) for x in ast.walk(st))
    return False


def _top_index(fn, target) -> int:
    return next(i for i, st in enumerate(fn.body) if target in list(ast.walk(st)))


def _calls(fn, name) -> list:
    return [n for n in ast.walk(fn) if isinstance(n, ast.Call) and (
        (isinstance(n.func, ast.Name) and n.func.id == name) or (isinstance(n.func, ast.Attribute) and n.func.attr == name))]


def t6(dtree, edges) -> dict:
    fns = {n.name: n for n in dtree.body if isinstance(n, ast.FunctionDef)}
    out = {}
    rx = fns["run_execute"]
    first = rx.body[1] if isinstance(rx.body[0], ast.Expr) and isinstance(rx.body[0].value, ast.Constant) else rx.body[0]
    out["hooks_refused_first"] = (isinstance(first, ast.If) and isinstance(first.body[0], ast.Raise)
                                  and "HOOKS" in ast.unparse(first.body[0]) and "SANDBOX" in ast.unparse(first.test))
    order, idx = ["check_grant", "premarker_admission", "create_run_nonce", "_arm_marker", "after_marker"], []
    for name in order:
        cs = _calls(rx, name)
        ok = len(cs) == 1 and _chain_ok(rx, cs[0])
        out[f"{name}_single_top_level"] = ok
        idx.append(_top_index(rx, cs[0]) if cs else -1)
    out["order"] = idx == sorted(idx) and len(set(idx[:4])) == 4 and -1 not in idx
    so = fns["run_seal_only"]
    ps = _calls(so, "_persist_pending")
    blk = None
    if len(ps) == 1:
        for n in ast.walk(so):
            for body in (getattr(n, "body", None), getattr(n, "orelse", None)):
                if isinstance(body, list) and any(ps[0] in list(ast.walk(st)) for st in body) and any(
                        isinstance(st, ast.Assign) and ps[0] in list(ast.walk(st)) for st in body):
                    blk = body
    guards = []
    if blk:
        k = next(i for i, st in enumerate(blk) if ps[0] in list(ast.walk(st)))
        for st in blk[:k]:
            if isinstance(st, ast.If) and isinstance(st.body[0], ast.Raise):
                guards.append(ast.unparse(st.test))
    out["seal_only_persist_guarded"] = (len(ps) == 1 and any(g.strip() == "not marker" for g in guards)
                                        and any("grant_path" in g for g in guards)
                                        and any("bound" in g and "marker" in g for g in guards))
    out["after_marker_only_from_run_execute"] = {g for g, r in edges.items() if "after_marker" in r and
                                                 g != "after_marker"} == {"run_execute"}
    return out


def _t7_aliases(tree) -> tuple:
    drv, grd = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "p309_driver":
                    drv.add(a.asname or a.name)
                elif a.name == "p309_guard":
                    grd.add(a.asname or a.name)
    return drv, grd


_FC = {}


def _is_mod(node, names: set, drv: set) -> bool:
    """node denotes the driver (names is drv) or the guard (otherwise), however the module was obtained: an import
    alias, a local alias, an attribute of another project module (P.D, D.G), a sys.modules / import_module lookup
    (R4F2-C1(c); the scanner's FileCtx.module_of_expr)"""
    fc, root = _FC.get("fc"), _FC.get("root")
    if fc is None:
        return isinstance(node, ast.Name) and node.id in names
    m = fc.module_of_expr(node, root)
    want = "p309_driver" if names is drv else "p309_guard"
    return m == want or m == "*"


def _ident_in(text: str, names: set) -> list:
    import re
    return [nm for nm in names if re.search(r"(?<![A-Za-z0-9_])" + re.escape(nm) + r"(?![A-Za-z0-9_])", text)]


def t7_tree(tree, rel: str, root: Path, depth: int = 0) -> list:
    """[(rule, message)] for one file (or one parsed `python -c` code string)"""
    import p309_scan as SC                                 # on sys.path (t7)
    bad = []
    fc = SC.FileCtx(tree, rel)
    _FC.update(fc=fc, root=root)
    drv, grd = _t7_aliases(tree)
    both = drv | grd
    strings = rel.startswith(T7_STRING_SCOPE) or depth > 0
    for n in ast.walk(tree):
        ln = getattr(n, "lineno", 0)
        if isinstance(n, ast.Name) and n.id in T7_FORBIDDEN or isinstance(n, ast.Attribute) and n.attr in T7_FORBIDDEN:
            bad.append(("FORBIDDEN_NAME", f"{rel}:{ln}: reference to {getattr(n, 'id', getattr(n, 'attr', ''))}"))
        if isinstance(n, ast.ImportFrom) and n.module in ("p309_driver", "p309_guard"):
            names = {a.name for a in n.names}
            hit = names & (T7_FORBIDDEN | {"*", "G"}) if n.module == "p309_driver" else names & {"PRODUCTION", "*"}
            if hit:
                bad.append(("IMPORT_FROM", f"{rel}:{ln}: from {n.module} import {sorted(hit)}"))
        if isinstance(n, ast.Attribute) and n.attr in ("__dict__", "__getattribute__") and (
                _is_mod(n.value, drv, drv) or _is_mod(n.value, grd, drv)):
            bad.append(("DYNAMIC_ACCESS", f"{rel}:{ln}: {ast.unparse(n)}"))
        if isinstance(n, ast.Attribute) and n.attr == "PRODUCTION" and _is_mod(n.value, grd, drv):
            bad.append(("PRODUCTION_REFERENCE", f"{rel}:{ln}: {ast.unparse(n)}"))
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)) and \
                fc.module_of_expr(n.value, root) is not None:          # any module, however obtained
            bad.append(("MODULE_ATTRIBUTE_STORE", f"{rel}:{ln}: {ast.unparse(n)}"))
        if isinstance(n, ast.Subscript) and ast.unparse(n.value) in ("sys.modules",) and any(
                isinstance(x, ast.Constant) and isinstance(x.value, str) and x.value in ("p309_driver", "p309_guard")
                for x in ast.walk(n.slice)):
            bad.append(("DYNAMIC_ACCESS", f"{rel}:{ln}: {ast.unparse(n)}"))
        if strings and isinstance(n, ast.Constant) and isinstance(n.value, str):
            hit = _ident_in(n.value, T7_FORBIDDEN)
            if hit:
                bad.append(("STRING_NAME", f"{rel}:{ln}: a string naming {sorted(hit)}"))
        if not isinstance(n, ast.Call):
            continue
        callee = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
        if callee in ("getattr", "setattr", "delattr", "hasattr", "vars") and n.args and (
                _is_mod(n.args[0], drv, drv) or _is_mod(n.args[0], grd, drv)):
            bad.append(("DYNAMIC_ACCESS", f"{rel}:{ln}: {callee} on the driver / guard module"))
        if callee in ("import_module", "__import__", "get") and any(
                isinstance(x, ast.Constant) and isinstance(x.value, str) and x.value.split(".")[-1] in (
                    "p309_driver", "p309_guard") for x in n.args[:1]) and (callee != "get" or ast.unparse(
                        n.func.value) == "sys.modules"):
            bad.append(("DYNAMIC_ACCESS", f"{rel}:{ln}: {callee}({ast.unparse(n.args[0])})"))
        if callee == "ExecContext":
            bad.append(("EXEC_CONTEXT", f"{rel}:{ln}: ExecContext construction"))
        if callee in ("run_execute", "run_seal_only"):
            ctxs = [k.value for k in n.keywords if k.arg == "ctx"] + (n.args[:1] if callee == "run_seal_only"
                                                                      else n.args[1:2])
            if not ctxs or any(isinstance(c, ast.Constant) and c.value is None for c in ctxs):
                bad.append(("NO_CONTEXT", f"{rel}:{ln}: {callee} without an explicit context"))
        strs = [x.value for a in n.args for x in ([a] + list(getattr(a, "elts", [])))
                if isinstance(x, ast.Constant) and isinstance(x.value, str)]
        if any("p309_driver" in x for x in strs) and {"execute", "seal-only"} & set(strs):
            bad.append(("DRIVER_EXECUTE", f"{rel}:{ln}: the driver run in execute / seal-only mode"))
        if any(isinstance(a, (ast.List, ast.Tuple)) and any(
                isinstance(x, (ast.Attribute, ast.Name, ast.BinOp, ast.Call)) and "p309_driver" in ast.unparse(x)
                for x in a.elts) for a in n.args) and {"execute", "seal-only"} & set(strs):
            bad.append(("DRIVER_EXECUTE", f"{rel}:{ln}: the driver run in execute / seal-only mode"))
        if depth < 3:                                      # a `python -c` code string: the same rules
            info = SC.process_info(n, fc, root)
            code = (info or {}).get("python", {}).get("code") if info and info["kind"] == "python" else None
            if code is not None:
                try:
                    bad += t7_tree(ast.parse(code), f"{rel}:{ln}:-c", root, depth + 1)
                except SyntaxError:
                    bad.append(("UNPARSEABLE", f"{rel}:{ln}: unparseable -c code"))
    return bad


def _never_runs(tree) -> bool:
    body = [st for st in tree.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
    return bool(body) and isinstance(body[0], ast.Raise) and "SystemExit" in ast.unparse(body[0])


def t7(root: Path) -> list:
    import hashlib as _h
    sys.path.insert(0, str(FNS / "code"))
    import p309_scan as SC
    SC.clear_caches()
    ex = {e["file"]: e for e in ALLOW.get("t7_exemptions", []) if e.get("reason")}
    bad = []
    for p in sorted(root.rglob("*.py")):                   # R4F M01: no file is skipped by its name
        rel = str(p.relative_to(root))
        if "__pycache__" in p.parts or rel in T7_EXEMPT:
            continue
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            bad.append(f"{rel}: unparseable")
            continue
        if rel in ALLOW["planted_control_files"] and _never_runs(tree):
            continue                                        # a planted control raises at import: it never runs
        e = ex.get(rel)
        current = e is not None and e.get("ast_sha256") == _h.sha256(ast.dump(tree).encode()).hexdigest()
        for rule, msg in t7_tree(tree, rel, root):          # a `-c` string's findings belong to its file
            if not (current and rule in e.get("rules", [])):
                bad.append(f"[{rule}] {msg}")
    return bad


def t9(dtree) -> dict:
    """R4F2-C2: validate_grant runs execute's read-only pre-marker checks, under the same condition as run_execute
    (check_bindings / check_governance_state only in the PRODUCTION context; the others unconditionally)"""
    fns = {n.name: n for n in dtree.body if isinstance(n, ast.FunctionDef)}
    vg, rx = fns.get("validate_grant"), fns.get("run_execute")
    out = {}

    def cond_of(fn, name):
        for n in ast.walk(fn):
            if isinstance(n, ast.IfExp) and any(isinstance(c, ast.Name) and c.id == name for c in ast.walk(n.body)):
                return ast.unparse(n.test)
        return None

    def called(fn, name):
        return any(isinstance(c, ast.Name) and c.id == name for c in ast.walk(fn))
    for name in ("check_flags", "check_branch", "check_not_evaluated", "check_result_paths", "check_clean",
                 "check_host_git"):
        out[f"{name}_in_both"] = bool(vg and rx) and called(vg, name) and called(rx, name) and \
            cond_of(vg, name) is None and cond_of(rx, name) is None
    for name in ("check_bindings", "check_governance_state"):
        out[f"{name}_same_condition"] = bool(vg and rx) and cond_of(vg, name) == cond_of(rx, name) == \
            "ctx.kind == 'PRODUCTION'"
    return out


def t8(dtree) -> dict:
    fns = {n.name: n for n in dtree.body if isinstance(n, ast.FunctionDef)}
    out = {}
    sys.path.insert(0, str(FNS / "code"))
    import p309_scan as SC
    for pin in ALLOW["backstop_pins"]:                     # R4F2-C1(g): equality with the pinned AST hashes
        st = next((x for x in dtree.body if (isinstance(x, ast.FunctionDef) and x.name == pin["name"]) or (
            isinstance(x, ast.Assign) and len(x.targets) == 1 and isinstance(x.targets[0], ast.Name)
            and x.targets[0].id == pin["name"])), None)
        out[f"pinned_{pin['name']}"] = st is not None and SC.ast_sha(st) == pin["ast_sha256"]
    ae = fns.get("_assert_execute_context")
    body = [st for st in (ae.body if ae else []) if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
    out["assert_ends_with_site_check_and_backstop"] = (
        len(body) >= 3 and ast.unparse(body[-3]) == "site = _SITE_CODES.get(sys._getframe(1).f_code)"
        and isinstance(body[-2], ast.If) and ast.unparse(body[-2].test) == "site is None"
        and isinstance(body[-2].body[0], ast.Raise) and "NOT_A_SITE" in ast.unparse(body[-2].body[0])
        and ast.unparse(body[-1]) == "_site_backstop(ctx, site)")
    sb = fns.get("_site_backstop")
    src = ast.unparse(sb) if sb else ""
    arm = next((st for st in (sb.body if sb else []) if isinstance(st, ast.If) and ast.unparse(st.test) ==
                "site == 'arm'"), None)
    arm_src = ast.unparse(arm) if arm else ""
    out["arm_requires_execute_grant_and_nonce"] = bool(arm) and all(x in arm_src for x in (
        "_MODE.get('mode') != 'execute'", "G.premarker_check(ctx.guard_ctx)", "_require_own_run_nonce(ctx)")) and \
        isinstance(arm.body[-1], ast.Return)
    rest = ast.unparse(ast.Module(body=[st for st in (sb.body if sb else []) if st is not arm], type_ignores=[]))
    out["pending_requires_marker_and_grant"] = all(x in rest for x in (
        "if not marker:", "ctx.guard_ctx.grant_path", "_require_own_run_nonce(ctx)"))
    nonce = fns.get("_require_own_run_nonce")
    out["nonce_names_this_process"] = bool(nonce) and "os.getpid()" in ast.unparse(nonce)
    mod_refs = [st for st in dtree.body if not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and any(isinstance(x, ast.Name) and x.id in SITES for x in ast.walk(st))]
    out["site_codes_is_the_only_module_reference"] = (
        len(mod_refs) == 1 and ast.unparse(mod_refs[0]) ==
        "_SITE_CODES = types.MappingProxyType({_arm_marker.__code__: 'arm', _persist_pending.__code__: 'pending'})")
    out["site_backstop_referenced_only_by_assert"] = {
        f.name for f in fns.values() if f.name != "_site_backstop" and any(
            isinstance(x, ast.Name) and x.id == "_site_backstop" for x in ast.walk(f))} == {"_assert_execute_context"}
    return out


def run(root: Path = FNS) -> dict:
    R = {}
    files = {"p309_driver": root / "code" / "p309_driver.py", "p309_rehearse": root / "code" / "p309_rehearse.py"}
    defs, edges = graph(files)
    dtree = ast.parse(files["p309_driver"].read_text())
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
    for key, path in files.items():
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
    if root == FNS:
        sc = subprocess.run([sys.executable, str(FNS / "code" / "p309_scan.py")], capture_output=True, text=True)
        try:
            verdict = json.loads(sc.stdout)["verdict"]
        except ValueError:
            verdict = "UNREADABLE"
    else:
        sys.path.insert(0, str(FNS / "code"))
        import p309_scan as SC
        verdict = SC.scan(root)["verdict"]
    R["T5_formal_scan"] = {"pass": verdict == "PASS", "detail": verdict}
    d6 = t6(dtree, edges)
    R["T6_mutation_dominated_by_the_grant"] = {"pass": all(d6.values()), "detail": d6}
    d7 = t7(root)
    R["T7_no_production_execution_from_tests_or_qualification"] = {"pass": not d7, "detail": d7[:20]}
    d8 = t8(dtree)
    R["T8_runtime_backstop_at_the_sites"] = {"pass": all(d8.values()), "detail": d8}
    d9 = t9(dtree)
    R["T9_validate_grant_runs_execute_prechecks"] = {"pass": all(d9.values()), "detail": d9}
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
