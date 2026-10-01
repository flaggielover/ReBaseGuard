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
T9 (R4F2-C2) validate_grant runs execute's read-only pre-marker checks under the same conditions as run_execute
T10 (R4 follow-up 3: R4F3-C1, NF6, NF7; rev. 2c A43-A45) the host-git check precedes every git write:
   * run_execute and run_seal_only: a top-level check_host_git(ctx) comes before any other call except the hooks
     refusal, production_context, check_flags and the clock;
   * run_execute: a second top-level check_host_git(ctx) lies after the historical control and before the first later
     statement that writes (the CONTROL_FAILED seal, the run nonce, the marker, after_marker);
   * after_marker: check_host_git(ctx) precedes the persist call in the body of the same try, and no earlier statement
     writes;
   * the driver's ENV sets GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL=/dev/null, and _spawn_job passes {**ENV, ...}
     with no GIT_ key (the Stage-1 jobs, and the verifier variant loaded inside them, inherit it);
   * the guard: _HERMETIC_GIT is exactly those two keys, and each of _git, _git_bytes and _git_ok applies it right
     after stripping GIT_* and stores no GIT_ key afterwards
T11 (r2 QC11 repair; plan section 4.6; review P6(e)) the sandbox base rule:
   * tests/test_p309_exactly_once.py defines sandbox_base(), which reads the real HEAD and validates a post-freeze
     history through D.recorded_freeze; its new_sandbox and the guard harness's new_sandbox take their base from it;
   * verify/scoped_sandbox.py Sandbox.__init__ takes its base from the verifier author's sandbox_base_commit();
   * in tests/ and verify/, no other call reads the real repository's HEAD ("rev-parse" + "HEAD" on REPO, str(REPO),
     own_repo() or the sandbox source) except the guard tests' report line (T11_REPORT_ONLY)
T12 (r2 addendum 2, F1) no ref in either production namespace, anywhere: both r1's and r2's namespace start with the
   driver's PRIOR_MARKER_PATTERNS[0]; both are refused by the guard's TestContext, the verifier variant's sandbox check
   (FORBIDDEN_REF_NAMESPACES), the verifier's sandbox helper (_FORBIDDEN_REF_PREFIX) and QC13 (_FORBIDDEN_NAMESPACES);
   both tokens are in the scanner's production_tokens
T13 (r2 review P6(f)) the production read path is pinned: the call closure of recorded_freeze, check_grant, walk_chain
   and check_not_evaluated (driver functions, and guard functions and classes reached through G.<name>) equals config
   production_read_path_pins, name for name and AST sha256 for AST sha256 (CPython 3.11); the pin tool never refreshes
   them
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
T7_STRING_SCOPE = ("tests/", "code/p309_qualify.py", "code/p309_rehearse.py", "verify/run_verify_all_scoped.py",
                   "code/p309_host.py", "code/p309_launch.py", "code/p309_topology_drill.py")   # r2: P4, F5
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
T11_REPORT_ONLY = {("tests/test_p309_guard.py", "<module>")}     # the guard tests' report line records git_head only
T11_BASE_FUNCS = {("tests/test_p309_exactly_once.py", "sandbox_base"), ("verify/scoped_sandbox.py", "sandbox_base_commit")}
T13_START = ("recorded_freeze", "check_grant", "walk_chain", "check_not_evaluated")
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


HOST_GIT_PRE_ALLOWED = {"any", "Refusal", "production_context", "check_flags", "time", "utc"}
WRITERS = {"git", "sealer", "seal_blob", "materializer", "materialize", "create_run_nonce", "_arm_marker",
           "after_marker", "persist", "_persist_pending", "persist_emergency"}
HERMETIC = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}


def _callees(node) -> set:
    return {c.func.id if isinstance(c.func, ast.Name) else c.func.attr for c in ast.walk(node)
            if isinstance(c, ast.Call) and isinstance(c.func, (ast.Name, ast.Attribute))}


def _is_host_check(st) -> bool:
    return isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and ast.unparse(st.value) == "check_host_git(ctx)"


def t10(dtree, gtree) -> dict:
    fns = {n.name: n for n in dtree.body if isinstance(n, ast.FunctionDef)}
    out = {}
    for name in ("run_execute", "run_seal_only"):
        body = fns[name].body if name in fns else []
        k = next((i for i, st in enumerate(body) if _is_host_check(st)), None)
        out[f"{name}_host_git_first"] = k is not None and all(
            _callees(st) <= HOST_GIT_PRE_ALLOWED for st in body[:k])
    rx = fns.get("run_execute")
    body = rx.body if rx else []
    ctl = [i for i, st in enumerate(body) if "historical_control" in _callees(st)]
    later = [i for i, st in enumerate(body) if ctl and i > ctl[-1] and _callees(st) & WRITERS]
    out["run_execute_recheck_after_control"] = bool(ctl and later) and any(
        _is_host_check(body[i]) for i in range(ctl[-1] + 1, later[0]))
    am = fns.get("after_marker")
    ok = False
    for i, st in enumerate(am.body if am else []):
        if isinstance(st, ast.Try) and any(isinstance(c, ast.Call) and ast.unparse(c.func) == "persist"
                                           for b in st.body for c in ast.walk(b)):
            j = next(j for j, b in enumerate(st.body) if any(isinstance(c, ast.Call) and ast.unparse(c.func) ==
                                                              "persist" for c in ast.walk(b)))
            ok = any(_is_host_check(b) for b in st.body[:j]) and not any(
                _callees(x) & WRITERS for x in am.body[:i])
            break
    out["after_marker_recheck_before_persist"] = ok
    env = next((n.value for n in dtree.body if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "ENV"), None)
    envd = {k.value: v.value for k, v in zip(env.keys, env.values) if isinstance(k, ast.Constant)
            and isinstance(v, ast.Constant)} if isinstance(env, ast.Dict) else {}
    out["driver_env_hermetic"] = all(envd.get(k) == v for k, v in HERMETIC.items())
    sp = fns.get("_spawn_job")
    kws = [kw.value for c in (ast.walk(sp) if sp else []) if isinstance(c, ast.Call) for kw in c.keywords
           if kw.arg == "env"]
    out["jobs_inherit_env"] = len(kws) == 1 and isinstance(kws[0], ast.Dict) and any(
        k is None and ast.unparse(v) == "ENV" for k, v in zip(kws[0].keys, kws[0].values)) and not any(
        isinstance(k, ast.Constant) and str(k.value).startswith("GIT_") for k in kws[0].keys)
    her = [n.value for n in gtree.body if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "_HERMETIC_GIT"]
    out["guard_hermetic_constant"] = len(her) == 1 and isinstance(her[0], ast.Dict) and {
        getattr(k, "value", None): getattr(v, "value", None) for k, v in zip(her[0].keys, her[0].values)} == HERMETIC
    gfns = {n.name: n for n in gtree.body if isinstance(n, ast.FunctionDef)}
    for name in ("_git", "_git_bytes", "_git_ok"):
        b = gfns[name].body if name in gfns else []
        good = len(b) >= 2 and isinstance(b[0], ast.Assign) and ast.unparse(b[0].targets[0]) == "env" and \
            "startswith('GIT_')" in ast.unparse(b[0].value) and ast.unparse(b[1]) == "env.update(_HERMETIC_GIT)"
        stores = [t for st in b[2:] for n in ast.walk(st) if isinstance(n, ast.Assign) for t in n.targets
                  if isinstance(t, ast.Subscript) and ast.unparse(t.value) == "env" and not (
                      isinstance(t.slice, ast.Constant) and t.slice.value == "LC_ALL")]
        calls = [n for n in ast.walk(gfns[name]) if isinstance(n, ast.Call) and ast.unparse(n.func) in (
            "env.update", "env.setdefault", "env.pop")] if name in gfns else []
        out[f"guard_{name}_hermetic"] = good and not stores and len(calls) == 1
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


def _consts(tree) -> dict:
    """module-level NAME = <constant or tuple of names/constants>"""
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            v = n.value
            if isinstance(v, ast.Constant):
                out[n.targets[0].id] = v.value
            elif isinstance(v, ast.Tuple):
                out[n.targets[0].id] = tuple(e.value if isinstance(e, ast.Constant) else
                                             e.id if isinstance(e, ast.Name) else None for e in v.elts)
    return out


def _func(tree, qual: str):
    """the function (or Class.method) named qual, or None"""
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == qual:
            return n
        if isinstance(n, ast.ClassDef) and qual.startswith(n.name + "."):
            for m in n.body:
                if isinstance(m, ast.FunctionDef) and m.name == qual.split(".", 1)[1]:
                    return m
    return None


def _calls_named(node, names: set) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Name) and f.id in names) or (isinstance(f, ast.Attribute) and f.attr in names):
                return True
    return False


def _owner_map(tree) -> dict:
    """id(node) -> outermost top-level function or Class.method name ("<module>" otherwise)"""
    out = {}
    for top in tree.body:
        if isinstance(top, ast.FunctionDef):
            for n in ast.walk(top):
                out[id(n)] = top.name
        elif isinstance(top, ast.ClassDef):
            for m in top.body:
                if isinstance(m, ast.FunctionDef):
                    for n in ast.walk(m):
                        out[id(n)] = f"{top.name}.{m.name}"
    return out


def t11(root: Path) -> dict:
    x = ast.parse((root / "tests" / "test_p309_exactly_once.py").read_text())
    g = ast.parse((root / "tests" / "test_p309_guard.py").read_text())
    v = ast.parse((root / "verify" / "scoped_sandbox.py").read_text())
    sb = _func(x, "sandbox_base")
    d = {"sandbox_base_defined_and_validates_through_recorded_freeze": sb is not None and _calls_named(sb, {"recorded_freeze"}),
         "qc11_new_sandbox_uses_sandbox_base": _calls_named(_func(x, "new_sandbox") or ast.Module(body=[]), {"sandbox_base"}),
         "guard_new_sandbox_uses_sandbox_base": _calls_named(_func(g, "new_sandbox") or ast.Module(body=[]), {"sandbox_base"}),
         "verifier_sandbox_uses_sandbox_base_commit": _calls_named(_func(v, "Sandbox.__init__") or ast.Module(body=[]),
                                                                   {"sandbox_base_commit"})}
    real = {"REPO", "src", "own_repo", "own"}
    stray = []
    for sub in ("tests", "verify"):
        for p in sorted((root / sub).glob("*.py")):
            rel = f"{sub}/{p.name}"
            tree = ast.parse(p.read_text())
            own = _owner_map(tree)
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call):
                    continue
                flat = []
                for a in n.args:
                    flat += a.elts if isinstance(a, (ast.List, ast.Tuple)) else [a]
                lits = [a.value for a in flat if isinstance(a, ast.Constant)]
                if "rev-parse" in lits and "HEAD" in lits and any(
                        isinstance(m, ast.Name) and m.id in real for a in flat for m in ast.walk(a)):
                    key = (rel, own.get(id(n), "<module>"))
                    if key not in T11_BASE_FUNCS and key not in T11_REPORT_ONLY:
                        stray.append(f"{rel}:{n.lineno} {key[1]}")
    d["no_other_real_head_read_in_tests_or_verify"] = not stray
    d["stray"] = stray[:10]
    return {k: v for k, v in d.items()}


def t12(root: Path) -> dict:
    dc = _consts(ast.parse((root / "code" / "p309_driver.py").read_text()))
    gt = ast.parse((root / "code" / "p309_guard.py").read_text())
    gc = _consts(gt)
    vc = _consts(ast.parse((root / "verify" / "srk_verify_indep_scoped.py").read_text()))
    sc = _consts(ast.parse((root / "verify" / "scoped_sandbox.py").read_text()))
    r1, r2 = gc.get("_PRIOR_NAMESPACE"), gc.get("_PROD_NAMESPACE")
    pfx = (dc.get("PRIOR_MARKER_PATTERNS") or (None,))[0]
    tc = _func(gt, "TestContext.__init__")
    tc_names = {n.id for n in ast.walk(tc) if isinstance(n, ast.Name)} if tc else set()
    qq = _func(ast.parse((root / "code" / "p309_qualify.py").read_text()), "qc13")
    toks = set(ALLOW["production_tokens"])
    return {"two_distinct_namespaces": bool(r1) and bool(r2) and r1 != r2
            and r1.endswith("-r1/") and r2.endswith("-r2/"),
            "both_start_with_prior_marker_pattern_0": bool(pfx) and r1.startswith(pfx) and r2.startswith(pfx),
            "guard_forbidden_namespaces_is_both": gc.get("_FORBIDDEN_NAMESPACES") == ("_PROD_NAMESPACE", "_PRIOR_NAMESPACE"),
            "guard_testcontext_refuses_both": {"_PROD_NAMESPACE", "_PRIOR_NAMESPACE"} <= tc_names,
            "variant_forbidden_namespaces_is_both": vc.get("FORBIDDEN_REF_NAMESPACES") == (
                "PRIOR_PRODUCTION_REF_NAMESPACE", "PRODUCTION_REF_NAMESPACE") and vc.get(
                "PRIOR_PRODUCTION_REF_NAMESPACE") == r1 and str(vc.get("PRODUCTION_MARKER", "")).startswith(r2),
            "verifier_sandbox_forbids_both": sc.get("_FORBIDDEN_REF_PREFIX") == (
                "_FORBIDDEN_REF_PREFIX_R1", "_FORBIDDEN_REF_PREFIX_R2") and sc.get("_FORBIDDEN_REF_PREFIX_R1") == r1
            and sc.get("_FORBIDDEN_REF_PREFIX_R2") == r2,
            "qc13_checks_both": qq is not None and "_FORBIDDEN_NAMESPACES" in ast.unparse(qq),
            "production_tokens_hold_both": bool(r1) and bool(r2) and r1.rstrip("/") in toks and r2.rstrip("/") in toks}


def production_read_closure(root: Path) -> dict:
    """name -> AST sha256 for the T13 call closure (driver functions; guard functions/classes reached as G.<name>)"""
    dt = ast.parse((root / "code" / "p309_driver.py").read_text())
    gt = ast.parse((root / "code" / "p309_guard.py").read_text())
    dtop = {n.name: n for n in dt.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    gtop = {n.name: n for n in gt.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    seen, stack = {}, [("code/p309_driver.py", n) for n in T13_START]
    while stack:
        f, name = stack.pop()
        table = dtop if f == "code/p309_driver.py" else gtop
        key = f"{f}::{name}"
        if key in seen or name not in table:
            continue
        node = table[name]
        seen[key] = hashlib.sha256(ast.dump(node).encode()).hexdigest()
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id in table:
                stack.append((f, n.id))
            elif f == "code/p309_driver.py" and isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                    and n.value.id == "G" and n.attr in gtop:
                stack.append(("code/p309_guard.py", n.attr))
    return seen


def t13(root: Path) -> dict:
    now = production_read_closure(root)
    pins = {f"{e['file']}::{e['name']}": e["ast_sha256"] for e in ALLOW.get("production_read_path_pins", {}).get(
        "entries", [])}
    return {"closure_nonempty": bool(now), "same_members": set(now) == set(pins),
            "same_hashes": bool(pins) and all(now.get(k) == v for k, v in pins.items()),
            "changed": sorted(k for k in set(now) | set(pins) if now.get(k) != pins.get(k))[:10]}


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
    d10 = t10(dtree, ast.parse((root / "code" / "p309_guard.py").read_text()))
    R["T10_host_git_checked_before_git_writes"] = {"pass": all(d10.values()), "detail": d10}
    d11 = t11(root)
    R["T11_sandbox_base_rule"] = {"pass": all(v for k, v in d11.items() if k != "stray"), "detail": d11}
    d12 = t12(root)
    R["T12_both_production_namespaces_forbidden"] = {"pass": all(d12.values()), "detail": d12}
    d13 = t13(root)
    R["T13_production_read_path_pinned"] = {"pass": d13["closure_nonempty"] and d13["same_members"]
                                            and d13["same_hashes"], "detail": d13}
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
