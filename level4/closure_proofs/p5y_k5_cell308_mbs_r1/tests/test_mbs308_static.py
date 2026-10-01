"""MB-S r1: static checks (RC1 science boundary, the guard diff, the science pins, the test-only fault hook, the
launcher requirement). No computation, no sandbox refs; reads files and the committed MB r1 bytes only.

    python3.14 -I -S -B test_mbs308_static.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import ast
import difflib
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

NSF_CODE = T.REPO / T.NSF_REL / "code"
BASE = T.BASE
FREEZE_R3 = "c46434a399eca18a709616a4a4d51918d1a30298"
# RC1: every science-glue function carried over from MB r1's driver, text-identical
SCIENCE_GLUE = ("controls", "compose_and_consume", "decide", "target_geometry", "admitted_pairs", "prepare_target",
                "stage1", "public_stage1", "load_science", "_worker_job", "_worker_init", "_set_job_cap", "_ser_block",
                "evaluate_target", "check_cpu_caps", "failure_kind", "rehearse", "decoy_cover", "r0_order3_variant",
                "supply_scaled_variant", "decoy_bundles", "decoy", "jsonable", "fs", "load_consumer", "control",
                "check_bindings", "check_governance_state", "read_pinned", "check_helpers", "_eval_cap",
                "Refusal", "IndependentCheckFailed", "Inconsistent")


def code(name: str) -> Path:
    return T.code_dir() / name


def segs(src: str) -> dict:
    tree = ast.parse(src)
    return {n.name: ast.get_source_segment(src, n) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def git_show(rev: str, rel: str) -> bytes:
    return subprocess.run(["/usr/bin/git", "-C", str(T.REPO), "show", f"{rev}:{rel}"], capture_output=True,
                          env=T.GENV).stdout


def t_rc1_science_glue_text_identical():
    """The functions of RC1 are TEXT-IDENTICAL (ast source segments) to MB r1's driver at c46434a3 (== 21e99cf0)."""
    mb = git_show(FREEZE_R3, T.NSF_REL + "/code/mb308_driver.py").decode()
    same_bytes = mb.encode() == git_show(BASE, T.NSF_REL + "/code/mb308_driver.py")
    a, b = segs(mb), segs(code("mbs308_driver.py").read_text())
    diff = [n for n in SCIENCE_GLUE if a.get(n) is None or a.get(n) != b.get(n)]
    return {"ok": same_bytes and not diff, "compared": len(SCIENCE_GLUE), "differing": diff,
            "driver_c46434a3_equals_21e99cf0": same_bytes}


# MBS-9 (i): module-level names referenced by the carried functions whose binding is NOT text-identical to MB r1's,
# each with its reason (anything else must be text-identical: same def, same import, same assignment source)
ALLOWED_BINDING_DIFFS = {
    "GUARD": "mbs308_guard: MB r1's guard with the successor's marker ref only (t_rc1_guard_diff_only_marker)",
    "HOST": "mbs308_host: MB r1's host module plus additions; require_ac / snapshot / Sampler / provenance used by carried "
            "code are MB r1's (snapshot / sample record three more keys)",
    "PIN": "MB r1's mb308_pinned, executed from its pinned bytes (SCIENCE_PINS) instead of imported",
    "S1M": "MB r1's mb308_stage1, executed from its pinned bytes (SCIENCE_PINS) instead of imported",
    "SUP": "MB r1's mb308_supply, executed from its pinned bytes (SCIENCE_PINS) instead of imported",
    "CON": "MB r1's mb308_consumer, executed from its pinned bytes (SCIENCE_PINS) instead of imported",
    "ProcessPoolExecutor": "lifecycle: bound to mbs308_state.CheckpointingPool (checkpoints, RSS record, memory watchdog)",
    "wait": "lifecycle: bound to mbs308_state.checkpointing_wait (one durable checkpoint per completed job)",
    "HELPER_SHA256": "identity: the successor's helper modules (the science modules are pinned by SCIENCE_PINS)",
    "LINEAGE": "identity: MB r1's lineage plus MB r1's own chain (c46434a3, 7eb057bb, 47bb37c7, afa93072, 21e99cf0)",
}


def _globals_used(fn: ast.AST) -> set:
    bound = set()
    for n in ast.walk(fn):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            a = n.args
            for x in a.posonlyargs + a.args + a.kwonlyargs + ([a.vararg] if a.vararg else []) + \
                    ([a.kwarg] if a.kwarg else []):
                bound.add(x.arg)
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            bound.add(n.id)
        if isinstance(n, ast.ExceptHandler) and n.name:
            bound.add(n.name)
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for al in n.names:
                bound.add(al.asname or al.name.split(".")[0])
    used = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    import builtins
    return {u for u in used - bound if not hasattr(builtins, u)}


def _bindings(src: str) -> dict:
    tree = ast.parse(src)
    b = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            b[n.name] = ("def", ast.get_source_segment(src, n))
        elif isinstance(n, ast.Import):
            for al in n.names:
                b[al.asname or al.name.split(".")[0]] = ("import", f"{al.name} as {al.asname}")
        elif isinstance(n, ast.ImportFrom):
            for al in n.names:
                b[al.asname or al.name] = ("import", f"from {n.module} import {al.name} as {al.asname}")
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tg:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        b[x.id] = ("assign", ast.get_source_segment(src, n))
    return b


def t_mbs9_referenced_module_names():
    """MBS-9 (i): every module-level name a carried function references (constants, helper functions, imports) is
    bound identically in MB-S (same def text, same import, same assignment source), or is a listed, reasoned
    exception. Functions referenced must themselves be carried identically."""
    mb = git_show(FREEZE_R3, T.NSF_REL + "/code/mb308_driver.py").decode()
    ms = code("mbs308_driver.py").read_text()
    tmb = ast.parse(mb)
    fns = {n.name: n for n in tmb.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    bmb, bms = _bindings(mb), _bindings(ms)
    report, bad = {}, []
    todo, seen = list(SCIENCE_GLUE), set()
    while todo:
        name = todo.pop()
        if name in seen or name not in fns:
            continue
        seen.add(name)
        for g in sorted(_globals_used(fns[name])):
            if g in report:
                continue
            a, b = bmb.get(g), bms.get(g)
            if g in ALLOWED_BINDING_DIFFS:
                report[g] = "ALLOWED: " + ALLOWED_BINDING_DIFFS[g]
            elif a is None or b is None:
                report[g] = "MISSING"
                bad.append(g)
            elif a == b:
                report[g] = "IDENTICAL " + a[0]
                if a[0] == "def":
                    todo.append(g)
            else:
                report[g] = "DIFFERS " + a[0]
                bad.append(g)
    return {"ok": not bad, "differing": bad, "names_checked": len(report), "functions_closed_over": len(seen),
            "report": report}


def t_mbs12_static_carryovers():
    """MBS-12: no successor file reads C3_KNOCKOUT_RECONSTRUCTION.json; the decoy cells stay 297 and 316 (none nearer
    the band); the decision rule (MB r1 section 5.4, `decide`) is carried verbatim (see RC1)."""
    hits = []
    for p in list(T.code_dir().glob("*.py")) + list((T.NSS / "tests").glob("*.py")):
        if p.name != "test_mbs308_static.py" and "C3_KNOCKOUT_RECONSTRUCTION" in p.read_text():
            hits.append(p.name)
    src = code("mbs308_driver.py").read_text()
    decoys = re.search(r"^DECOY_CELLS = \((\d+), (\d+)\)$", src, re.M)
    return {"ok": not hits and decoys is not None and decoys.groups() == ("297", "316"),
            "files_naming_c3_knockout": hits, "decoy_cells": decoys and decoys.groups()}


def t_rc1_guard_diff_only_marker():
    """mbs308_guard differs from MB r1's mb308_guard ONLY in the marker-ref constant line."""
    old = git_show(BASE, T.NSF_REL + "/code/mb308_guard.py").decode().splitlines()
    new = code("mbs308_guard.py").read_text().splitlines()
    changed = [ln for ln in difflib.unified_diff(old, new, lineterm="", n=0)
               if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    return {"ok": changed == ['-CONSUMED_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"',
                              '+CONSUMED_REF = "refs/p5y-k5-cell308-mbs-r1/target-consumed"'], "changed_lines": changed}


def t_science_pins_equal_mbr1_bytes():
    """SCIENCE_PINS: sha256 and git blob of each science module equal MB r1's committed bytes at 21e99cf0, and the
    namespace carries no copy of any of them."""
    src = code("mbs308_driver.py").read_text()
    pins = {m[0]: (m[1], m[2]) for m in re.findall(r'"(mb308_\w+)": \("([0-9a-f]{64})",\s*"([0-9a-f]{40})"\)', src)}
    out, ok = {}, len(pins) == 5
    for name, (s, b) in pins.items():
        raw = git_show(BASE, f"{T.NSF_REL}/code/{name}.py")
        blob = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
        out[name] = hashlib.sha256(raw).hexdigest() == s and blob == b
        ok = ok and out[name]
    copies = [p.name for p in T.code_dir().iterdir() if p.name.startswith("mb308_")]
    return {"ok": ok and not copies, "modules": out, "copies_in_namespace": copies}


def t_fault_hook_test_only():
    """The fault hook is inert in production: FAULT is only ever assigned None in code/, every fault() call names F1-F12,
    and the CLI refuses to run any mode when a test hook is present (checked by running the CLI)."""
    assigns, points = [], set()
    for p in T.code_dir().glob("*.py"):
        tree = ast.parse(p.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign):
                for tg in n.targets:
                    name = tg.attr if isinstance(tg, ast.Attribute) else getattr(tg, "id", None)
                    if name == "FAULT":
                        assigns.append((p.name, ast.unparse(n.value)))
            if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) == "fault" and n.args:
                if isinstance(n.args[0], ast.Constant):
                    points.add(n.args[0].value)
    drv = ast.parse(code("mbs308_driver.py").read_text())
    main = next(n for n in drv.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    body_src = [ast.unparse(s) for s in main.body]
    i_hooks = next((i for i, s in enumerate(body_src) if "test_hooks_present" in s), None)
    i_dispatch = next((i for i, s in enumerate(body_src) if s.startswith("try:")), None)
    sb = T.Sandbox(T.SCRATCH / "t_static")                 # the CLI runs from a sandbox copy of the code under test
    env = dict(T.GENV, MBS308_TEST_ANY="1")
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(sb.driver), "status"], capture_output=True,
                       text=True, env=env, stdin=subprocess.DEVNULL)
    clean = subprocess.run([T.PY, "-I", "-S", "-B", str(sb.driver), "status"], capture_output=True,
                           text=True, env=dict(T.GENV), stdin=subprocess.DEVNULL)
    return {"ok": assigns == [("mbs308_state.py", "None")] and points == {f"F{i}" for i in range(1, 13)}
            and i_hooks is not None and i_dispatch is not None and i_hooks < i_dispatch and p.returncode == 2
            and "TEST_HOOKS_PRESENT" in p.stdout and clean.returncode == 0 and "TEST_HOOKS" not in clean.stdout,
            "assignments": assigns, "points": sorted(points), "cli": [p.returncode, p.stdout.strip()[-80:]],
            "cli_without_hooks": [clean.returncode, clean.stdout.strip()[-40:]]}


def t_execute_and_resume_require_launcher_and_pins():
    """execute and resume both pass through pre_marker_common, which calls check_launched (launchd), check_platform
    (RC2) and host_preflight; the classifier takes the platform readings (DR2)."""
    tree = ast.parse(code("mbs308_driver.py").read_text())
    fns = {n.name: ast.unparse(n) for n in tree.body if isinstance(n, ast.FunctionDef)}
    pmc = fns["pre_marker_common"]
    ok = all(x in pmc for x in ("check_launched()", "check_platform()", "host_preflight(", "check_mbr1_state()",
                                "check_science_modules()")) and \
        "pre_marker_common(" in fns["run_execute"] and "pre_marker_common(" in fns["run_resume"] and \
        all("platform=platform_readings()" in fns[f] for f in ("run_status", "run_recover", "run_resume",
                                                                "run_seal_only", "run_close_indeterminate"))
    return {"ok": ok}


def t_no_mbr1_driver_mode_invoked():
    """No file of the namespace executes MB r1's driver: its path appears only as a read in the RC1 comparison."""
    hits = []
    for p in list(T.code_dir().glob("*.py")) + list((T.NSS / "tests").glob("*.py")):
        for i, ln in enumerate(p.read_text().splitlines(), 1):
            if "mb308_driver" in ln and p.name != "test_mbs308_static.py" and \
                    any(x in ln for x in ("import ", "subprocess", "exec(", "Popen", "run(", "spawn")):
                hits.append(f"{p.name}:{i}")
    return {"ok": not hits, "hits": hits}


def t_launcher_plist_contract():
    """The launcher's plist: pinned interpreter with -I -S -B, RunAtLoad true, KeepAlive false, AbandonProcessGroup
    true, logs outside /private/tmp, the label in MBS308_LAUNCH_LABEL."""
    sys.path.insert(0, str(T.code_dir()))
    import mbs308_launch as L
    pl = L.make_plist("org.rebaseguard.mbs308.execute.X", L.driver_cmd("execute"), T.REPO, L.LOG_DIR)
    ok = pl["ProgramArguments"][:4] == [L.PYTHON, "-I", "-S", "-B"] and pl["RunAtLoad"] is True and \
        pl["KeepAlive"] is False and pl["AbandonProcessGroup"] is True and \
        not pl["StandardOutPath"].startswith("/private/tmp") and \
        pl["EnvironmentVariables"]["MBS308_LAUNCH_LABEL"] == pl["Label"] and \
        str(L.LOG_DIR).endswith("Library/Logs/ReBaseGuard/mbs308")
    return {"ok": ok}


RATIFICATION_COMMIT = "3c2a78544899c5772ea95b7b228b1059f056e3fd"
RATIFICATION_REL = "level4/closure_proofs/p5y_k5_cell308_research/governance/CONSTANTS_RATIFICATION_MBS308.md"
RATIFIED_EXCL_ADDITIONS = {"spotlightknowledged.updater", "cloudd", "BackgroundShortcutRunner", "modelcatalogd"}
PRE_R3_BUILD = "35cabb507c70686e0545c3036dacc452dc7fe6ff"      # the build the implementation delta review rejected


def _norm(s: str) -> str:
    return " ".join(s.split())


def _driver_set(src: str, name: str):
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == [name]:
            v = n.value
            return set(ast.literal_eval(v.args[0] if isinstance(v, ast.Call) else v))
    return None


def t_r3_ratified_rules_applied():
    """R3 (REVIEW_IMPLEMENTATION_MBS308_DELTA condition 1): the protocol draft's section 8 carries the ratification's
    written rules R-MEM, R-FREE (with its attainability clause), R-EXCL-PCT and R-ALLOW (with its exclusions) VERBATIM
    (whitespace-normalised), read from the committed ratification 3c2a7854; the superseded memory rule is no longer
    stated as the frozen rule; section 7 states the launcher's preflight timeout as PRE_CAP_S + 100; and EXCL_ALLOW is
    exactly the 39 names of the rejected build 35cabb50 plus the four ratified OS daemons."""
    rat = git_show(RATIFICATION_COMMIT, RATIFICATION_REL).decode()
    sec = rat.split("## Written rules", 1)[1].split("\n## Evidence", 1)[0] if "## Written rules" in rat else ""
    paras = [p for p in sec.split("\n\n") if p.strip()]
    starts = ("**R-MEM (MEM_CAP).**", "**R-FREE (FREE_MEM_MIN).**", "*Attainability.*", "**R-EXCL-PCT (EXCL_CPU_PCT).**",
              "**R-ALLOW (EXCL_ALLOW).**", "Never added:")
    rules = {s: next((p for p in paras if p.strip().startswith(s)), None) for s in starts}
    proto = (T.NSS / "protocol/MBS308_PROTOCOL_DRAFT.md").read_text()
    s8 = proto.split("\n## 8.", 1)[1].split("\n## 9.", 1)[0]
    s7 = proto.split("\n## 7.", 1)[1].split("\n## 8.", 1)[0]
    verbatim = {s: p is not None and _norm(p) in _norm(s8) for s, p in rules.items()}
    superseded = "the frozen rule is max(3 × the largest official decoy per-job peak RSS, 1 GiB)"
    old = _driver_set(git_show(PRE_R3_BUILD, T.NS_REL + "/code/mbs308_driver.py").decode(), "EXCL_ALLOW")
    new = _driver_set(code("mbs308_driver.py").read_text(), "EXCL_ALLOW")
    # brief 54 (section 11.2 option (a)): until the apply step the driver carries the PROVISIONAL item-16 list (the 39
    # names plus the four ratified daemons, exactly); after it EXCL_ALLOW is R-ALLOW's output, which by the rule keeps
    # the 39 names and holds the two ratified daemons whose H3 readings (70.3, 52.2) exceed every possible EXCL_CPU_PCT
    # (case R_RULES_OFFICIAL compares the output itself). The protocol's rule-output table says which state this is.
    provisional = "| PROVISIONAL (pre-freeze build; not a rule output) |" in s8
    allow_ok = old is not None and len(old) == 39 and not (old & RATIFIED_EXCL_ADDITIONS) and new is not None and (
        new == old | RATIFIED_EXCL_ADDITIONS if provisional else
        old | {"spotlightknowledged.updater", "BackgroundShortcutRunner"} <= new)
    timeout_rule = "PRE_CAP_S + 100" in _norm(s7)
    ok = all(verbatim.values()) and _norm(superseded) not in _norm(s8) and timeout_rule and allow_ok
    return {"ok": ok, "verbatim": verbatim, "superseded_absent": _norm(superseded) not in _norm(s8),
            "timeout_rule_in_s7": timeout_rule, "excl_allow": {"old": len(old or ()), "new": len(new or ()),
                                                              "ok": allow_ok, "provisional": provisional}}


if __name__ == "__main__":
    T.cli(globals())
