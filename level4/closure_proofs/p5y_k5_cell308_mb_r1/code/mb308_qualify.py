"""Cell-308 MB campaign (r1) -- the qualification verifier (B8; cases in config/QUALIFICATION_CASES.json, gates Q1-Q12).

It can NEVER evaluate cell 308 (or 306, 307, 309):
* every certifier call is on a declared decoy / validation drift outside [6/5, 13/5] (the guard refuses the rest);
* the consumer runs on cell 305's COMMITTED record only, in reproduction-only mode (rehearse);
* the exactly-once flows run in a `git clone --shared` sandbox with stubbed controls and evaluator.

Modes
  official   HEAD must be the freeze commit; no review / grant / marker / result may exist. Writes
             qualification/MB308_QUALIFICATION.json and the heavy case records next to it, nothing else in the repo.
  --review   HEAD = freeze or the qualification commit on it; writes only --out (outside the repository); the heavy
             cases are re-verified from the committed records unless --heavy.
  --dev      BUILDER development only (never evidence): any HEAD, only the cases named by --only, writes only --out
             (outside the repository). Its report carries dev_mode = true and pass = false by construction of the gate
             aggregation (a dev report can never be an official PASS).
Every case summary carries a boolean `pass`; the aggregator fails loudly on a missing or non-boolean `pass`.

    python3.14 -I -S -B mb308_qualify.py                           (official)
    python3.14 -I -S -B mb308_qualify.py --review --out FILE [--heavy]
    python3.14 -I -S -B mb308_qualify.py --dev --only QC05,QC09 --out FILE
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
sys.path.insert(1, str(NS / "tests"))
import mb308_a0core as A0C  # noqa: E402
import mb308_driver as D  # noqa: E402
import mb308_guard as GUARD  # noqa: E402
import mb308_pinned as PIN  # noqa: E402
import mb308_stage1 as S1M  # noqa: E402
import mb308_supply as SUP  # noqa: E402

PY = sys.executable
FLAGS = ["-I", "-S", "-B"]
QDIR = NS / "qualification"
OUTS = {"report": "MB308_QUALIFICATION.json", "rehearse": "MB308_QC01_REHEARSE_305.json",
        "decoy297": "MB308_QC02_DECOY_297.json", "decoy316": "MB308_QC03_DECOY_316_B3.json",
        "serial": "MB308_QC04_SERIAL_297_B0.json", "det_a": "MB308_QC04_LADDER_DET_A.json",
        "det_b": "MB308_QC04_LADDER_DET_B.json", "mc": "MB308_QC08_MC.json", "asm_controls": "MB308_QC07_E4.json"}
HEAVY = ("QC02", "QC03", "QC04", "QC08")
ALL_CASES = ("QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13")
PRE_GRANT_CLASSES = {"HISTORICAL_READ", "HISTORICAL_RECONSTRUCTION", "PRUNING_FROM_COMMITTED", "INFRASTRUCTURE",
                     "SYNTHETIC_VALIDATION", "NONTARGET_DRIFT_VALIDATION", "NONTARGET_REAL_VALIDATION", "THEORY",
                     "REVIEW"}
RS = "level4/closure_proofs/p5y_k5_cell308_research/"
# the independent incident-independence review of route R-MB (INCIDENT_AUDIT_ACCEPTED with conditions C1-C9), and
# the files its conditions C1-C8 require to exist (checked by path at HEAD); C4 (the user's CLOSURE_ONLY ruling) is
# checked at the grant, not here
INCIDENT_REVIEW_REL = RS + "reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md"
INCIDENT_CONDITION_FILES = (RS + "audit/INCIDENT_AUDIT_MB308_ADDENDUM_A1.md", RS + "config/QUARANTINE_AMENDMENT_308_1.json",
                            RS + "ledger/briefs/BRIEF_CHECK.json", RS + "registry/ROUTE_REGISTRY.md")
# the sanctioned tail-figure pattern file of the research scanner r2 (incident review C8): read at run time only
PATTERNS_PIN = (RS + "ledger/TAIL_FIGURE_PATTERNS.json",
                "0dc2addcd6ac667c6866736ab913a2513b6ec848636d2fbb04051d02ab49cbf5", "ab0104c6b534")
MC_PIN = ("level4/closure_proofs/p5y_k5_cell307_rlr_r1/tests/test_rlr307_mc.py",
          "811c929acabbdde16ce181f22e66cd7ce9f840c7777add71c632140f7eb348fb", "b486a5f69588")
E4_PIN = (RS + "streams/ASSEMBLY/controls.py", "801fb5ab3450407dd478ef26331f964a8cd27abee3c00768c3fc8a0c95946519",
          "4c42c56af95c")
LADDER_DET_DRIFTS = ("3", "11/10")         # REVIEW_A0 C4: one dyadic (with d = 8), one non-dyadic declared drift
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": os.environ.get("HOME", "/var/empty")}


def git(*args) -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *args], capture_output=True, text=True, env=ENV,
                          stdin=subprocess.DEVNULL).stdout.strip()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def spawn(args: list, log: Path) -> subprocess.Popen:
    return subprocess.Popen([PY, *FLAGS, *args], stdout=log.open("w"), stderr=subprocess.STDOUT, env=ENV,
                            stdin=subprocess.DEVNULL, cwd=str(REPO))


# ------------------------------------------------------------------ preconditions
def preconditions(mode: str) -> dict:
    fz, head = D.freeze_commit(), git("rev-parse", "HEAD")
    out = {"freeze_commit": fz, "head": head, "mode": mode}
    if mode == "official":
        ok_head = bool(fz) and head == fz
    elif mode == "review":
        added = git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").split()
        ok_head = bool(fz) and (head == fz or (git("rev-parse", "HEAD^") == fz and added
                                               and all(a.startswith(D.QUAL_DIR_REL) for a in added)))
    else:
        ok_head = True
    out["head_ok"] = bool(ok_head)
    forbidden = [D.QREVIEW_REL, D.GRANT_REL, D.RESULT_REL, D.NS_REL + "/adjudication", D.NS_REL + "/authorization",
                 D.EXEC_DIR_REL]
    out["no_review_grant_result"] = not any(os.path.lexists(REPO / p) or git("log", "--all", "--format=%H", "--", p)
                                            for p in forbidden)
    out["no_marker_refs"] = not any(git("for-each-ref", "--format=%(refname)", p) for p in D.PRIOR_MARKERS)
    gd = Path(git("rev-parse", "--path-format=absolute", "--git-dir"))
    out["no_emergency_file"] = not os.path.lexists(gd / D.EMERGENCY_NAME)
    if mode != "dev":
        out["tracked_clean"] = git("status", "--porcelain", "--untracked-files=no") == ""
    if mode == "official":
        out["namespace_clean_including_ignored"] = git("status", "--porcelain", "--ignored", "--untracked-files=all",
                                                       "--", D.NS_REL) == ""
    out["incident_review_accepted_before_freeze"] = incident_review(fz)["pass"]
    keys = [k for k in out if k not in ("freeze_commit", "head", "mode")]
    if mode == "dev":
        keys = [k for k in keys if k != "incident_review_accepted_before_freeze"]
    out["pass"] = all(out[k] for k in keys)
    return out


def incident_review(fz: str) -> dict:
    """The verdict line (the first non-empty line after the title) is exactly INCIDENT_AUDIT_ACCEPTED, and it occurs
    once as a standalone line; the review is committed and an ancestor of the freeze; the condition files exist at
    HEAD; the route registry carries revision r2."""
    rc = git("log", "-1", "--format=%H", "--", INCIDENT_REVIEW_REL)
    text = (REPO / INCIDENT_REVIEW_REL).read_text() if (REPO / INCIDENT_REVIEW_REL).exists() else ""
    body = [ln.strip() for ln in text.splitlines()[1:] if ln.strip()]
    verdict = bool(body) and body[0] == "INCIDENT_AUDIT_ACCEPTED" and \
        sum(1 for ln in text.splitlines() if ln.strip() == "INCIDENT_AUDIT_ACCEPTED") == 1
    before = bool(rc) and bool(fz) and subprocess.run(["/usr/bin/git", "-C", str(REPO), "merge-base", "--is-ancestor",
                                                       rc, fz], env=ENV).returncode == 0
    files = {f: bool(git("rev-parse", "-q", "--verify", f"HEAD:{f}")) for f in INCIDENT_CONDITION_FILES}
    reg = (REPO / INCIDENT_CONDITION_FILES[-1]).read_text() if (REPO / INCIDENT_CONDITION_FILES[-1]).exists() else ""
    out = {"review": INCIDENT_REVIEW_REL, "verdict_line": verdict, "committed_before_freeze": before,
           "condition_files_at_HEAD": files, "registry_revision_r2": "**Revision r2**" in reg}
    out["pass"] = verdict and before and all(files.values()) and out["registry_revision_r2"]
    return out


# ------------------------------------------------------------------ children (fresh processes)
def _decoy_ctx() -> dict:
    """The Stage-1 worker context of DECOY mode, in this process (serial children only)."""
    D._worker_init("decoy", str(REPO), "", [], sha((CODE / "mb308_driver.py").read_bytes()), "decoy", True)
    return D._W


def child_serial(out: Path) -> None:
    """QC04(a): block 0 of decoy 297, every job run serially in THIS process (no pool; per-job caps not applied)."""
    ctx = _decoy_ctx()
    lo, hi, _, _ = D.decoy_cover(297)
    b = S1M.plan(ctx["S1"], GUARD, lo, hi)[0]
    ladder = {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N, "C1B": S1M.LADDER_C1B_D}
    t0 = time.time()
    res = {}
    for kind, i, r in S1M.jobs([b], ladder):
        res[f"{kind}:{r}"] = S1M.run_job(ctx, kind, b, r)
    for d in ladder["C1B"]:
        c = res.get(f"C1B:{d}", {})
        if c.get("status") == "CERTIFIED" and c.get("cert") and d <= S1M.C1B_VERIFY_MAX_D:
            res[f"VER:{d}"] = S1M.run_job(ctx, "VER", b, d, c["cert"])
    out.write_text(json.dumps({"block": 0, "results": res, "wall_seconds": round(time.time() - t0, 1)},
                              indent=1, sort_keys=True, default=str) + "\n")


def child_ladder(out: Path, drifts: str) -> None:
    """QC04(b) (REVIEW_A0 C4): the pointwise ladder of the frozen driver's job code at the declared drifts (one dyadic,
    with the C1b rungs d = 8, 10, 12; one non-dyadic, C2b only: the formal ladder uses dyadic b_i by rule D2),
    serially in this process; every certificate is reduced to its canonical sha256."""
    ctx = _decoy_ctx()
    t0 = time.time()
    res = {}
    for ds in drifts.split(","):
        e = F(ds)
        GUARD.guard_drift(e)
        b = {"index": 0, "tile": (e, e), "hull": (e, e), "b": e}
        dyadic = (e.denominator & (e.denominator - 1)) == 0
        for n in S1M.LADDER_C2B_N:
            res[f"{ds}:C2B:{n}"] = S1M.run_job(ctx, "C2B", b, n)
        for d in (S1M.LADDER_C1B_D if dyadic else ()):
            r = S1M.run_job(ctx, "C1B", b, d)
            if r.get("cert"):
                r["cert_sha256"] = A0C.sha256_bytes(A0C.canon(r.pop("cert")))
            res[f"{ds}:C1B:{d}"] = r
    out.write_text(json.dumps({"drifts": drifts, "results": res, "wall_seconds": round(time.time() - t0, 1)},
                              indent=1, sort_keys=True, default=str) + "\n")


def child_e4(out: Path) -> None:
    """QC07(a): stream ASSEMBLY's E4 negative controls (29), regenerated through the research path in this fresh
    process; main() is NOT called (it writes into the research namespace), only its control loop."""
    import types
    raw = PIN.verified_bytes(REPO, E4_PIN, check_git=True)
    path = REPO / E4_PIN[0]
    mod = types.ModuleType("mb308_e4_controls")
    mod.__file__ = str(path)
    sys.modules["mb308_e4_controls"] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    t0 = time.time()
    rows = [mod.run_control(*c) for c in mod.controls(mod.DG.decoy_set())]
    res = {"controls": len(rows), "detected": sum(1 for r in rows if r["DETECTED"]),
           "not_detected": [r["control"] for r in rows if not r["DETECTED"]],
           "valid_halves_ok": all(r["valid_status"] == "OK" for r in rows), "wall_seconds": round(time.time() - t0, 1)}
    res["pass"] = res["controls"] == 29 and not res["not_detected"] and res["valid_halves_ok"]
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")


def child_mc(out: Path, decoy_path: Path) -> None:
    """QC08: independent Monte Carlo (the cell-307 campaign's pinned simulator, test_rlr307_mc.py) at decoy 297's
    drifts: every RLR block record is checked as in the 307 campaign, and at every b_i U_i >= Lambda_MC - 5 se and
    L_i <= Lambda_MC + 5 se; planted wrong bounds must be flagged."""
    MC = PIN.exec_pinned(REPO, "mb308_rlr307_mc", MC_PIN)
    dec = json.loads(decoy_path.read_text())
    blocks = dec["stage1"]["blocks"]
    rows, ctl = [], {}
    for b in blocks:
        if not b.get("run"):
            continue
        e = float(F(b["b"]))
        est = MC.estimate(e, 971 + 10 * b["index"])
        lam, se = est["Lambda"]
        pw = b["pointwise"]
        row = {"block": b["index"], "U_ok": pw.get("U") is None or float(F(pw["U"])) >= lam - MC.Z * se,
               "L_ok": pw.get("L") is None or float(F(pw["L"])) <= lam + MC.Z * se}
        if b.get("rlr_block"):
            row["rlr_block"] = MC.check(est, b["rlr_block"])["all_hold"]
        rows.append(row)
        if not ctl and pw.get("U") is not None:
            ctl = {"U := Lambda_hat/2 flagged": not (lam / 2 >= lam - MC.Z * se),
                   "L := 2 Lambda_hat flagged": not (2 * lam <= lam + MC.Z * se)}
    res = {"rows": rows, "controls": ctl, "n": len(rows),
           "pass": bool(rows) and all(r["U_ok"] and r["L_ok"] and r.get("rlr_block", True) for r in rows)
           and bool(ctl) and all(ctl.values()), "latent_proxy": "decoy estimates only"}
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")


# ------------------------------------------------------------------ QC11 static structure (AST)
def _funcs(tree) -> dict:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _calls(node, name) -> list:
    return [c for c in ast.walk(node) if isinstance(c, ast.Call) and
            ((isinstance(c.func, ast.Name) and c.func.id == name) or
             (isinstance(c.func, ast.Attribute) and c.func.attr == name))]


def _names(node) -> set:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | \
        {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}


def qc11_static() -> dict:
    r = {}
    drv = ast.parse((CODE / "mb308_driver.py").read_text())
    fd = _funcs(drv)
    main_calls = _calls(fd["main"], "run_execute")
    r["cli_passes_no_injection"] = len(main_calls) == 1 and len(main_calls[0].args) == 1 and not main_calls[0].keywords
    ctl = [c for c in _calls(drv, "control") if any(isinstance(a, ast.Name) and a.id == "TARGET_CELL" for a in c.args)]
    grant_line = min(c.lineno for c in _calls(fd["run_execute"], "check_grant"))
    r["target_control_only_in_run_execute_after_grant"] = len(ctl) == 1 and \
        any(x is ctl[0] for x in ast.walk(fd["run_execute"])) and ctl[0].lineno > grant_line
    st = [c for c in _calls(drv, "stage1") if c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value == "target"]
    r["stage1_target_only_in_evaluate_target"] = len(st) == 1 and any(x is st[0] for x in ast.walk(fd["evaluate_target"]))
    refs = [n for n in ast.walk(drv) if isinstance(n, ast.Name) and n.id == "evaluate_target"]
    r["evaluate_target_referenced_only_in_run_execute"] = len(refs) == 1 and any(
        x is refs[0] for x in ast.walk(fd["run_execute"]))
    arms = _calls(drv, "arm_target")
    r["arm_target_only_in_evaluate_target_and_worker_init"] = len(arms) == 2 and all(
        any(x is c for x in ast.walk(fd["evaluate_target"])) or any(x is c for x in ast.walk(fd["_worker_init"]))
        for c in arms)
    upd = [c for c in _calls(drv, "git") if len(c.args) >= 2 and isinstance(c.args[0], ast.Constant)
           and c.args[0].value == "update-ref" and isinstance(c.args[1], ast.Name) and c.args[1].id == "CONSUMED_REF"]
    r["exactly_one_marker_update_ref_in_run_execute"] = len(upd) == 1 and any(
        x is upd[0] for x in ast.walk(fd["run_execute"]))
    write_names = {"open", "write_text", "write_bytes", "write", "mkdir", "rename", "replace", "unlink"}
    no_write = {}
    for fn in ("stage1", "evaluate_target", "prepare_target", "_worker_job", "_worker_init", "decide", "controls",
               "compose_and_consume", "target_geometry", "after_marker", "load_science"):
        no_write[fn] = not [c for c in ast.walk(fd[fn]) if isinstance(c, ast.Call) and
                            ((isinstance(c.func, ast.Name) and c.func.id in write_names) or
                             (isinstance(c.func, ast.Attribute) and c.func.attr in write_names))]
    r["no_file_write_in_target_path"] = all(no_write.values())
    allowed = {"cid", "status", "channel"}
    ok_prints = True
    prints = _calls(fd["after_marker"], "print")
    for c in prints:
        for a in c.args:
            if isinstance(a, ast.JoinedStr):
                ok_prints &= all(not isinstance(v, ast.FormattedValue) or (isinstance(v.value, ast.Name)
                                                                         and v.value.id in allowed) for v in a.values)
            elif not isinstance(a, ast.Constant):
                ok_prints = False
    r["after_marker_prints_status_only"] = ok_prints and len(prints) >= 1
    con = ast.parse((CODE / "mb308_consumer.py").read_text())
    fc = _funcs(con)
    forbidden_route = {"penalty_closed", "penalty_c5t", "penalty_riemann", "penalty_riemann_lower",
                       "evaluate_bundle", "p5_c5t_closed_form", "tpt_endpoint_only", "_mutant"}
    r["control_path_names_no_penalty"] = not ((_names(fc["_repro_core"]) | _names(fc["control_cb"]) |
                                               _names(fc["gr3b_cell"])) & (forbidden_route | {"penalty_blocked", "tptb"}))
    r["stage2_names_no_other_route"] = not (_names(fc["_stage2"]) & forbidden_route)
    rbg = [k for c in ast.walk(con) if isinstance(c, ast.Call) for k in c.keywords if k.arg == "research_band_guard"]
    r["F2_band_guard_only_from_formal_guard"] = bool(rbg) and all(isinstance(k.value, ast.Name) and
                                                                  k.value.id == "band_guard" for k in rbg) and \
        "f2_band_guard" in _names(fc["_stage2"])
    sup = ast.parse((CODE / "mb308_supply.py").read_text())
    rbs = [k for c in ast.walk(sup) if isinstance(c, ast.Call) for k in c.keywords if k.arg == "research_band_guard"]
    r["supply_band_guard_only_from_formal_guard"] = bool(rbs) and all(isinstance(k.value, ast.Name) and
                                                                      k.value.id == "band_guard" for k in rbs)
    for f in ("mb308_driver.py", "mb308_consumer.py", "mb308_supply.py", "mb308_stage1.py", "mb308_a0core.py"):
        t = ast.parse((CODE / f).read_text())
        r[f"no_private_F2_hooks_{f}"] = "_mutant" not in _names(t) and "tpt_endpoint_only" not in _names(t)
    s1 = ast.parse((CODE / "mb308_stage1.py").read_text())
    a0 = ast.parse((CODE / "mb308_a0core.py").read_text())
    r["stage1_and_a0core_print_and_write_nothing"] = not any(
        isinstance(c, ast.Call) and ((isinstance(c.func, ast.Name) and c.func.id in {"print", "open"}) or
                                     (isinstance(c.func, ast.Attribute) and c.func.attr in write_names))
        for t in (s1, a0) for c in ast.walk(t))
    ind = ast.parse((REPO / PIN.INDEP_PIN[0]).read_text())
    imps = {a.name.split(".")[0] for n in ast.walk(ind) if isinstance(n, ast.Import) for a in n.names} | \
        {(n.module or "").split(".")[0] for n in ast.walk(ind) if isinstance(n, ast.ImportFrom)}
    r["F2_imports_stdlib_only"] = imps <= {"__future__", "fractions", "re"}
    t3 = ast.parse((REPO / PIN.TUPLE_PIN[0]).read_text())
    imps3 = {a.name.split(".")[0] for n in ast.walk(t3) if isinstance(n, ast.Import) for a in n.names} | \
        {(n.module or "").split(".")[0] for n in ast.walk(t3) if isinstance(n, ast.ImportFrom)}
    ns_text = "".join(p.read_text(errors="replace") for p in NS.rglob("*") if p.is_file() and p.suffix in
                      (".py", ".json", ".md") and "__pycache__" not in p.parts)
    forbidden = ("history" + "/" + "recon", "KNOCK" + "OUT_RECON")      # incident review C2 (built, not written)
    r["no_reference_to_the_research_reconstructions"] = not any(f in ns_text for f in forbidden)
    r["F3_imports_stdlib_only"] = imps3 <= {"__future__", "fractions", "hashlib", "json", "math", "random", "copy",
                                            "sys"}
    r["pass"] = all(v is True for v in r.values())
    return r


# ------------------------------------------------------------------ QC12 leak scans
def _tail_regex():
    """The tail-figure patterns, read at RUN TIME from the pinned sanctioned file (incident review C8); nothing of
    them is written into this namespace. Compiled exactly as the research scanner r2 compiles them."""
    raw = PIN.verified_bytes(REPO, PATTERNS_PIN, check_git=True)
    pats = json.loads(raw)["patterns"]
    return pats, re.compile("|".join("(?<![0-9])" + p for p in pats))


def qc12_leak(official: bool) -> dict:
    """(a) the tail-figure text scan over EVERY file of this namespace (0 hits), with a planted control built at run
    time from the pattern file in neutral wording; (b) official runs only: tokens (>= 6 significant digits) of the
    committed cell-308 records, as the 307 QC12 (counts and file names only, never a value)."""
    pats, rx = _tail_regex()
    files = sorted(p for p in NS.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    hits = {}
    for p in files:
        n = len(rx.findall(p.read_text(errors="replace")))
        if n:
            hits[str(p.relative_to(REPO))] = n
    planted = " and ".join(re.sub(r"\\b|\\", "", pat) for pat in pats[:3])   # built at run time only, neutral
    ctl = len(rx.findall("row " + planted + " end")) >= 3
    out = {"files_scanned": len(files), "patterns": len(pats), "tail_figure_hits": hits,
           "planted_control_fires": ctl}
    if official:
        toks = _record_tokens()
        th = {str(p.relative_to(REPO)): sum(p.read_text(errors="replace").count(t) for t in toks) for p in files}
        th = {k: v for k, v in th.items() if v}
        c2 = sum(("line " + sorted(toks)[len(toks) // 2]).count(t) for t in toks) >= 1
        out.update({"record_tokens": len(toks), "record_token_hit_files": sorted(th), "record_planted_fires": c2})
        out["pass"] = not hits and ctl and not th and c2 and len(toks) > 20
    else:
        out["record_token_scan"] = "not run (official qualification only; it reads committed cell-308 records)"
        out["pass"] = not hits and ctl and len(pats) > 20
    return out


def _record_tokens() -> set:
    acc = set()

    def tok(o):
        if isinstance(o, dict):
            for v in o.values():
                tok(v)
        elif isinstance(o, list):
            for v in o:
                tok(v)
        elif isinstance(o, str) and "/" in o:
            try:
                x = F(o)
            except (ValueError, ZeroDivisionError):
                return
            if len(o) >= 8:
                acc.add(o)
            s = f"{abs(float(x)):.12g}"
            if "e" not in s and len(s.replace(".", "").lstrip("0")) >= 6:
                out, n = "", 0
                for ch in s:
                    out += ch
                    if ch.isdigit() and (n > 0 or ch != "0"):
                        n += 1
                    if n == 6:
                        break
                acc.add(out)
    fc = json.loads(D.read_pinned("c2_forecast"))
    tok(fc["cells"]["308"])
    tok(fc["supplies"]["308"])
    for key in ("registry_c1", "registry_c2"):
        tok([b for b in json.loads(D.read_pinned(key))["blocks"] if b["cell"] == 308])
    tok(json.loads(D.read_pinned("tct_inputs_308")))
    geom = set()
    return acc - geom


# ------------------------------------------------------------------ QC13 temporal / governance
def qc13(pre: dict) -> dict:
    rows = []
    led = REPO / RS / "ledger/TARGET_INTEGRITY_LEDGER.jsonl"
    for ln in led.read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            if r.get("agent") in ("builder", "mb308_qualification"):
                rows.append(r)
    gov = D.check_governance_state()
    out = {"preconditions": pre["pass"], "builder_ledger_lines": len(rows),
           "builder_ledger_pre_grant_classes_only": all(r["class"] in PRE_GRANT_CLASSES for r in rows),
           "builder_ledger_zero_target": all(r["new_target_evaluations"] == 0 and r["target_equivalent_proxies"] == 0
                                             and not r.get("LEAK_FLAG") for r in rows), "governance": gov}
    out["incident_review"] = incident_review(pre["freeze_commit"])
    out["pass"] = out["preconditions"] and out["builder_ledger_pre_grant_classes_only"] and \
        out["builder_ledger_zero_target"] and (pre["mode"] == "dev" or out["incident_review"]["pass"])
    return out


# ------------------------------------------------------------------ Q8 manifest
def q8_manifest() -> dict:
    mp = NS / "protocol" / "MB308_FREEZE.json"
    if not mp.exists():
        return {"pass": False, "reason": "no freeze manifest"}
    man = json.loads(mp.read_bytes())
    bad = [rel for rel, v in man["frozen_files"].items()
           if sha((REPO / rel).read_bytes()) != v["sha256"] or git("rev-parse", f"HEAD:{rel}") != v["git_blob"]]
    listed = set(man["frozen_files"])
    on_disk = {str(p.relative_to(REPO)) for d in D.FROZEN_DIRS if (NS / d).is_dir() for p in (NS / d).rglob("*")
               if p.is_file() and p != mp and "__pycache__" not in p.parts}
    drv_ok = man["driver"]["sha256"] == sha((CODE / "mb308_driver.py").read_bytes())
    try:
        D.check_bindings()
        bind = True
    except (D.Refusal, PIN.PinError):
        bind = False
    return {"manifest_sha256": sha(mp.read_bytes()), "frozen_files": len(listed), "mismatches": bad,
            "unlisted_files": sorted(on_disk - listed), "driver_sha_ok": drv_ok, "bindings_ok": bind,
            "pass": not bad and on_disk == listed and drv_ok and bind}


# ------------------------------------------------------------------ comparisons of the heavy records
def qc02_eval(dec: dict | None) -> dict:
    if not dec:
        return {"pass": False, "missing": "decoy 297 record"}
    st = dec["stage1"]
    blocks = st["blocks"]
    s2 = dec.get("stage2_decoys") or []
    ok_s2 = bool(s2) and all("stage2" in r and all(g.get("pass") is True for g in r["stage2"]["gates"].values())
                             and r["supply"]["independent"]["status"] == "EQUAL" for r in s2)
    return {"blocks": len(blocks), "all_run": all(b["run"] for b in blocks),
            "rlr_blocks_certified": sum(1 for b in blocks if b.get("rlr_block")),
            "pointwise_status": [b["pointwise"]["status"] for b in blocks],
            "verifications": st.get("n_verifications"), "stage2_decoys": len(s2), "stage2_all_gates_pass": ok_s2,
            "r0_order3_variant_present": any(r.get("decoy_meta", {}).get("r0_order3_binds") for r in s2),
            "ladder_full": st["ladder"] == {"RLR": list(S1M.LADDER_RLR), "C2B": list(S1M.LADDER_C2B_N),
                                            "C1B": list(S1M.LADDER_C1B_D)},
            "pass": dec.get("blocks_run") == "all" and all(b["run"] for b in blocks) and ok_s2
            and all(b["pointwise"]["status"] in ("CERTIFIED", "ALARM_UNAVAILABLE", "NOT_CERTIFIED") for b in blocks)
            and st["ladder"] == {"RLR": list(S1M.LADDER_RLR), "C2B": list(S1M.LADDER_C2B_N),
                                 "C1B": list(S1M.LADDER_C1B_D)}}


def qc04_eval(dec: dict | None, serial: dict | None, det_a: dict | None, det_b: dict | None) -> dict:
    out = {}
    if dec and serial:
        b0 = dec["stage1"]["blocks"][0]
        pooled = {f"RLR:{r['rung']}": r for r in b0["rlr_rungs"]} | {f"C2B:{r['rung']}": r for r in b0["c2b_rungs"]} | \
            {f"C1B:{r['rung']}": r for r in b0["c1b_rungs"]}
        same = {}
        for k, r in serial["results"].items():
            if k.startswith("VER"):
                continue
            p = pooled.get(k, {})
            keys = [x for x in ("status", "status_U", "status_L") if x in r] + ["record"]
            rec_s = {x: v for x, v in r.get("record", {}).items() if not x.startswith("_") and x != "cpu_seconds"}
            rec_p = {x: v for x, v in p.get("record", {}).items() if not x.startswith("_") and x != "cpu_seconds"}
            same[k] = all(r.get(x) == p.get(x) for x in keys if x != "record") and rec_s == rec_p
        out["serial_vs_pooled"] = same
        out["serial_ok"] = bool(same) and all(same.values())
    else:
        out["serial_ok"] = False
    if det_a and det_b:
        def proj(d):
            return {k: {x: y for x, y in v.items() if x not in ("wall_seconds", "cpu_cap")} |
                    {"record": {x: y for x, y in v.get("record", {}).items() if x not in ("cpu_seconds",)}}
                    for k, v in d["results"].items()}
        out["ladder_pair_identical"] = proj(det_a) == proj(det_b)
        out["ladder_drifts"] = [det_a.get("drifts"), det_b.get("drifts")]
    else:
        out["ladder_pair_identical"] = False
    out["pass"] = out["serial_ok"] and out["ladder_pair_identical"]
    return out


# ------------------------------------------------------------------ main
def main(argv=None) -> int:  # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--heavy", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=D.WORKERS)
    ap.add_argument("--work", help="base directory for work files and the flow sandbox (required with --dev)")
    ap.add_argument("--_child", choices=("serial", "ladder", "e4", "mc"))
    ap.add_argument("--_drift")
    ap.add_argument("--_decoy")
    a = ap.parse_args(argv)
    if a._child:
        {"serial": lambda: child_serial(Path(a.out)), "ladder": lambda: child_ladder(Path(a.out), a._drift),
         "e4": lambda: child_e4(Path(a.out)), "mc": lambda: child_mc(Path(a.out), Path(a._decoy))}[a._child]()
        return 0
    mode = "dev" if a.dev else ("review" if a.review else "official")
    if mode != "official" and not a.out:
        print("QUALIFY REFUSED: --review / --dev write only --out")
        return 2
    if mode == "dev" and not a.work:
        print("QUALIFY REFUSED: --dev needs --work (the builder's sandboxes live in the session scratchpad)")
        return 2
    if a.work and Path(a.work).resolve().is_relative_to(REPO.resolve()):
        print("QUALIFY REFUSED: --work must lie outside the repository")
        return 2
    if a.out and Path(a.out).resolve().is_relative_to(REPO.resolve()):
        print("QUALIFY REFUSED: --out must lie outside the repository")
        return 2
    t0, started = time.time(), utc()
    pre = preconditions(mode)
    if not pre["pass"]:
        print(f"QUALIFY REFUSED: preconditions {json.dumps(pre)}")
        return 2
    sel = set(ALL_CASES) if mode != "dev" else set((a.only or "").split(",")) & set(ALL_CASES)
    heavy = mode == "official" or a.heavy
    work = Path(tempfile.mkdtemp(prefix="mb308q", dir=a.work))
    odir = QDIR if mode == "official" else work
    if mode == "official":
        odir.mkdir(exist_ok=True)
    paths = {k: odir / v for k, v in OUTS.items()}
    drv = str(CODE / "mb308_driver.py")
    procs = {}
    if heavy and "QC02" in sel:
        procs["decoy297"] = spawn([drv, "decoy", "--cell", "297", "--workers", str(a.workers), "--out",
                                   str(paths["decoy297"])], work / "decoy297.log")
    if heavy and "QC03" in sel:
        procs["decoy316"] = spawn([drv, "decoy", "--cell", "316", "--first-blocks", "3", "--workers", "1", "--out",
                                   str(paths["decoy316"])], work / "decoy316.log")
    if heavy and "QC04" in sel:
        procs["serial"] = spawn([str(HERE), "--_child", "serial", "--out", str(paths["serial"])], work / "serial.log")
        for tag in ("det_a", "det_b"):
            procs[tag] = spawn([str(HERE), "--_child", "ladder", "--_drift", ",".join(LADDER_DET_DRIFTS), "--out",
                                str(paths[tag])], work / f"{tag}.log")
    if "QC07" in sel:
        procs["e4"] = spawn([str(HERE), "--_child", "e4", "--out", str(paths["asm_controls"])], work / "e4.log")
    cases = {}
    if "QC01" in sel:
        reh = subprocess.run([PY, *FLAGS, drv, "rehearse", "--cell", "305", "--out", str(paths["rehearse"])],
                             capture_output=True, text=True, env=ENV, cwd=str(REPO))
        rh = json.loads(paths["rehearse"].read_text()) if paths["rehearse"].exists() else {}
        cases["QC01"] = {"exit": reh.returncode, "C_A": rh.get("C_A", {}).get("field_matches"),
                         "C_B_failed": rh.get("C_B", {}).get("failed"),
                         "pass": reh.returncode == 0 and rh.get("pass") is True}
    need_sci = sel & {"QC05", "QC06", "QC07", "QC09"}
    if need_sci:
        con = D.load_consumer()
        sci = D.load_science(allow_uncommitted=(mode == "dev"), with_decoy_gen=True)
        vf = PIN.load_verifier(REPO, GUARD)
    if "QC05" in sel:
        import test_mb308_twosided as TT
        cases["QC05"] = TT.composition_test(SUP, S1M, sci["S1"], sci["indep"], sci["IND7"], sci["cp"], con, GUARD)
    if "QC06" in sel:
        import test_mb308_a0 as TA
        cases["QC06"] = TA.run(PIN, A0C, sci["c1b"], sci["c2b"], GUARD, S1M=S1M, vf=vf)
    if "QC07" in sel:
        import test_mb308_tptb as TP
        cases["QC07_formal"] = TP.run(D.CON, sci["asm"], GUARD, sci["indep"], sci["asm"]["DG"])
    if "QC09" in sel:
        import test_mb308_guard as TG
        mods = {"c1b": sci["c1b"], "c2b": sci["c2b"], "S1": sci["S1"], "A0C": A0C, "vd": vf["vd"],
                "TPT": sci["asm"]["TPT"], "indep": sci["indep"], "set_flags": PIN.set_c1b_flags}
        cases["QC09_inprocess"] = TG.run(D.CON.read_pinned, mods)
    if "QC10" in sel or "QC09" in sel:
        import test_mb308_flows as TF
        fz = pre["freeze_commit"] if mode != "dev" else None
        flows = TF.run_flows(work / "flows", freeze=fz)
        cases["QC10"] = {"n": flows["n"], "failed": flows["failed"], "freeze": flows["freeze"],
                         "flows": {k: {"ok": v["ok"], "run": v.get("run")} for k, v in flows["flows"].items()},
                         "pass": bool(flows["all_ok"]) and not flows["failed"]}
        if "QC09" in sel:
            arm = flows["flows"].get("QC09_arming")
            cases["QC09"] = {"in_process": cases.pop("QC09_inprocess"), "sandbox_arming": arm}
            cases["QC09"]["pass"] = cases["QC09"]["in_process"]["pass"] is True and bool(arm and arm["ok"])
        if "QC10" not in sel:
            cases.pop("QC10")
    if "QC11" in sel:
        cases["QC11"] = qc11_static()
    if "QC12" in sel:
        cases["QC12"] = qc12_leak(mode == "official")
    for k, p in procs.items():
        p.wait()
    rcs = {k: p.returncode for k, p in procs.items()}
    load = lambda k: json.loads(paths[k].read_text()) if paths[k].exists() else None   # noqa: E731
    if "QC07" in sel:
        e4 = load("asm_controls") or {"pass": False, "missing": True}
        cases["QC07"] = {"assembly_E4": e4, "formal": cases.pop("QC07_formal"),
                         "pass": e4.get("pass") is True and cases.get("QC07_formal", {}).get("pass", True) is True}
        cases["QC07"]["pass"] = e4.get("pass") is True and cases["QC07"]["formal"]["pass"] is True
    if "QC02" in sel:
        cases["QC02"] = qc02_eval(load("decoy297")) | {"exit": rcs.get("decoy297", "committed")}
    if "QC03" in sel:
        d3 = load("decoy316")
        cases["QC03"] = {"exit": rcs.get("decoy316", "committed"), "pass": bool(d3) and all(
            b["run"] for b in d3["stage1"]["blocks"][:3])}
    if "QC04" in sel:
        cases["QC04"] = qc04_eval(load("decoy297"), load("serial"), load("det_a"), load("det_b"))
    if "QC08" in sel:
        if paths["decoy297"].exists():
            subprocess.run([PY, *FLAGS, str(HERE), "--_child", "mc", "--_decoy", str(paths["decoy297"]), "--out",
                            str(paths["mc"])], env=ENV, cwd=str(REPO))
        cases["QC08"] = load("mc") or {"pass": False, "missing": "decoy 297 record"}
    if "QC13" in sel:
        cases["QC13"] = qc13(pre)
    if mode != "dev":
        cases["Q8"] = q8_manifest()
    missing_pass = sorted(k for k, v in cases.items() if not isinstance(v, dict) or not isinstance(v.get("pass"), bool))
    P = lambda *ks: all(cases.get(k, {}).get("pass") is True for k in ks)    # noqa: E731
    theory = (REPO / RS / "theory/THEOREM_MB.md").exists()
    gates = {"Q1": {"pass": P("QC05") and theory}, "Q2": {"pass": P("QC01", "QC06", "QC11", "Q8")},
             "Q3": {"pass": P("QC04")}, "Q4": {"pass": P("QC05", "QC06")}, "Q5": {"pass": P("QC05", "QC07")},
             "Q6": {"pass": P("QC02", "QC03", "QC08")}, "Q7": {"pass": P("QC05")}, "Q8": {"pass": P("Q8")},
             "Q9": {"pass": P("QC09", "QC12")}, "Q10": {"pass": P("QC13")},
             "Q11": {"pass": pre.get("incident_review_accepted_before_freeze") is True},
             "Q12": {"pass": P("QC10", "QC11")}}
    ok = mode != "dev" and all(g["pass"] for g in gates.values()) and not missing_pass
    report = {"schema": "rebaseguard.p5y.k5.cell308-mb-r1.qualification.v1", "freeze_commit": pre["freeze_commit"],
              "head": pre["head"], "review_mode": mode != "official", "dev_mode": mode == "dev",
              "cases_selected": sorted(sel), "heavy_recomputed": heavy, "preconditions": pre, "cases": cases,
              "gates": gates, "cases_missing_pass": missing_pass, "pass": ok, "started_utc": started,
              "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 1), "verifier_sha256": sha(HERE.read_bytes()),
              "python": sys.version.split()[0], "child_exit_codes": rcs,
              "record_sha256": {k: sha(p.read_bytes()) for k, p in paths.items() if k != "report" and p.exists()},
              "ledger_entries": [
                  {"class": "HISTORICAL_RECONSTRUCTION", "what": "QC01 rehearse cell 305 (C-A, C-B reproduction only)"},
                  {"class": "NONTARGET_DRIFT_VALIDATION", "what": "QC02-QC04, QC06, QC08 decoy cells 297 / 316 and "
                   "validation drifts 3, 27/10, 11/10"},
                  {"class": "SYNTHETIC_VALIDATION", "what": "QC05, QC07, QC10 synthetic sets, decoy bundles, sandbox"}],
              "target_evaluations": 0}
    out = Path(a.out) if a.out else paths["report"]
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(f"QUALIFICATION {'PASS' if ok else ('DEV' if mode == 'dev' else 'FAIL')}: " +
          " ".join(f"{k}={'P' if cases[k].get('pass') else 'F'}" for k in sorted(cases)))
    return 0 if ok or mode == "dev" else 1


if __name__ == "__main__":
    sys.exit(main())
