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
import math
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
LADDER_DET_DRIFTS = ("3", "11/10")
# Q1: the NSF copy of THEOREM_MB r1 must be byte-identical to the research file as committed at bfa9ad3c
THEORY_REL = D.NS_REL + "/theory/THEOREM_MB.md"
THEORY_RESEARCH = (RS + "theory/THEOREM_MB.md", "bfa9ad3c",
                   "f1c767dccc0bb3738fcae350530d4dda13c8b9db482ffb25528376502f4d0d25",
                   "2ee1a41bccd26c32f2bb150b5f2ad6df856ff3a9")
# Q12 (protocol 3.2): the cell-308 Stage-1 job set and the projection's scheduling model
Q12_BLOCKS, Q12_WORKERS = 11, D.WORKERS
Q12_KEYS = (("RLR", 4), ("RLR", 6), ("RLR", 8), ("C2B", 20), ("C2B", 40), ("C2B", 80), ("C1B", 8), ("C1B", 10),
            ("C1B", 12))         # REVIEW_A0 C4: one dyadic (with d = 8), one non-dyadic declared drift
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
    ns_text = "".join(p.read_text(errors="replace") for p in NS.rglob("*") if p.is_file() and p.suffix == ".py"
                      and "__pycache__" not in p.parts)   # code only: prose may STATE the prohibition (protocol s5)
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


MANIFEST_REL = D.NS_REL + "/protocol/MB308_FREEZE.json"
GUARD_REL = D.NS_REL + "/code/mb308_guard.py"
GUARD_FIELD = ("guard", "cell308_cover")          # the manifest's guard-geometry field (the guard's CELL308 constant)


def qc12_leak(record_scan: bool) -> dict:
    """(a) the tail-figure text scan over EVERY file of this namespace (0 hits), with a planted control built at run
    time from the pattern file in neutral wording; (b) when `record_scan` (official and review runs, or --record-scan
    in dev): tokens (>= 6 significant digits) of the committed cell-308 records, as the 307 QC12 (counts and file
    names only, never a value). r2 repair: the tokens derived from cell 308's cells.json GEOMETRY (left, right, e0,
    rho) are exempt ONLY where the design puts that geometry: inside the freeze manifest's guard-geometry field
    guard.cell308_cover (every occurrence of the token in the file must lie in that field) and in the guard source;
    every exempted occurrence is reported (file, field, count; never the value); any other hit fails. Planted
    controls, through the same per-file function on a temporary copy of the manifest text: a NON-geometry record
    token must fire, and a geometry token placed outside the guard field must fire."""
    pats, rx = _tail_regex()
    files = sorted(p for p in NS.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    hits, timing_ex = {}, []
    for p in files:
        rel = str(p.relative_to(REPO))
        n, ex = _tail_hits(rel, p.read_text(errors="replace"), rx)
        if n:
            hits[rel] = n
        if ex:
            timing_ex.append({"file": rel, "field": "timing keys " + "/".join(sorted(TIMING_KEYS)), "occurrences": ex})
    planted = " and ".join(re.sub(r"\\b|\\", "", pat) for pat in pats[:3])   # built at run time only, neutral
    ctl = len(rx.findall("row " + planted + " end")) >= 3
    one = re.sub(r"\\b|\\", "", pats[0])
    rec_rel = D.NS_REL + "/qualification/PLANTED.json"
    c_nontiming = _tail_hits(rec_rel, json.dumps({"record": {"value": one, "seconds": 1.0}}), rx)[0] > 0
    c_timing = _tail_hits(rec_rel, json.dumps({"record": {"value": "x", "seconds": {"S": one}}}), rx) == (0, 1)
    out = {"files_scanned": len(files), "patterns": len(pats), "tail_figure_hits": hits,
           "timing_field_exemptions": timing_ex, "planted_control_fires": ctl,
           "planted_tail_value_in_nontiming_field_of_evidence_fires": c_nontiming,
           "planted_tail_value_in_timing_field_of_evidence_exempt_and_counted": c_timing}
    ctl = ctl and c_nontiming and c_timing
    if not record_scan:
        out["record_token_scan"] = "not run (official and review runs, or --record-scan in dev mode)"
        out["pass"] = not hits and ctl and len(pats) > 20
        return out
    toks, geom = _record_tokens(), _geometry_tokens()
    if not geom:
        out.update({"pass": False, "reason": "no geometry tokens derived"})
        return out
    th, exempt = {}, []
    for p in files:
        rel = str(p.relative_to(REPO))
        bad, ex = _token_hits(rel, p.read_text(errors="replace"), toks, geom)
        if bad:
            th[rel] = bad
        exempt += ex
    c_rec = c_geo = False
    if (REPO / MANIFEST_REL).exists():
        mtext = (REPO / MANIFEST_REL).read_text()
        non_geo = sorted(toks - geom)
        planted_rec = mtext.replace("\n", "\n" + json.dumps(non_geo[len(non_geo) // 2]) + "\n", 1)
        c_rec = _token_hits(MANIFEST_REL, planted_rec, toks, geom)[0] > 0
        planted_geo = mtext.replace("\n", "\n" + json.dumps(sorted(geom)[0]) + "\n", 1)
        c_geo = _token_hits(MANIFEST_REL, planted_geo, toks, geom)[0] > 0
    out.update({"record_tokens": len(toks), "geometry_tokens": len(geom),
                "record_token_hit_files": sorted(th), "record_token_hits": sum(th.values()),
                "geometry_exemptions": exempt,
                "planted_non_geometry_token_in_manifest_copy_fires": c_rec,
                "planted_geometry_token_outside_guard_field_fires": c_geo})
    out["pass"] = not hits and ctl and not th and c_rec and c_geo and len(toks) > 20
    return out


def _tail_hits(rel: str, text: str, rx) -> tuple:
    """(non-exempt tail-pattern matches, matches exempted as timing fields). r2: in machine-written JSON evidence under
    the post-freeze directories (qualification/, incl. r1_failed/), a match located ONLY inside a timing key
    (TIMING_KEYS, at any depth, with everything below it: runtimes in seconds) is exempt and reported; every other
    match fails. Every other file is scanned as text, without exemption."""
    n = len(rx.findall(text))
    parts = Path(rel).relative_to(D.NS_REL).parts if rel.startswith(D.NS_REL + "/") else ()
    if not n or not parts or parts[0] not in D.POST_FREEZE_DIRS or not rel.endswith(".json"):
        return n, 0
    try:
        obj = json.loads(text)
    except ValueError:
        return n, 0
    kept = len(rx.findall(json.dumps(_strip_timing(obj), sort_keys=True)))
    full = len(rx.findall(json.dumps(obj, sort_keys=True)))
    return kept + max(0, n - full), max(0, full - kept)      # a raw-text-only match is never exempt


def _token_hits(rel: str, text: str, toks: set, geom: set) -> tuple:
    """(number of NON-exempt token occurrences, [exemption records]) for one file's text."""
    counts = {t: text.count(t) for t in toks | geom if t in text}
    if not counts:
        return 0, []
    field_counts = {}
    if rel == MANIFEST_REL:
        try:
            man = json.loads(text)
            vals = man.get(GUARD_FIELD[0], {}).get(GUARD_FIELD[1], [])
        except (ValueError, AttributeError):
            vals = []
        field_counts = {t: sum(str(v).count(t) for v in vals) for t in counts}
    bad, n_ex = 0, 0
    for t, n in counts.items():
        if t in geom and rel == GUARD_REL:
            n_ex += n
        elif t in geom and rel == MANIFEST_REL and field_counts.get(t, 0) == n:
            n_ex += n
        else:
            bad += n
    ex = [] if not n_ex else [{"file": rel, "field": ".".join(GUARD_FIELD) if rel == MANIFEST_REL else "source",
                               "occurrences": n_ex}]
    return bad, ex


def _tok(o, acc: set) -> None:
    if isinstance(o, dict):
        for v in o.values():
            _tok(v, acc)
    elif isinstance(o, list):
        for v in o:
            _tok(v, acc)
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


def _record_tokens() -> set:
    """Tokens of the committed cell-308 records (C2 forecast cell and supplies, REGISTRY_C1/C2 rows, TCT_INPUTS_308)."""
    acc = set()
    fc = json.loads(D.read_pinned("c2_forecast"))
    _tok(fc["cells"]["308"], acc)
    _tok(fc["supplies"]["308"], acc)
    for key in ("registry_c1", "registry_c2"):
        _tok([b for b in json.loads(D.read_pinned(key))["blocks"] if b["cell"] == 308], acc)
    _tok(json.loads(D.read_pinned("tct_inputs_308")), acc)
    return acc


def _geometry_tokens() -> set:
    """Tokens of cell 308's cells.json geometry (left, right, e0, rho): exact rational strings and their
    6-significant-digit renderings (the same tokenisation as the record tokens)."""
    cells = [c for c in json.loads(D.read_pinned("cells_json")) if c["detector"] == "CUSUM" and c["index"] == 308]
    acc = set()
    if len(cells) == 1:
        _tok({k: cells[0][k][0] for k in ("left", "right", "e0", "rho")}, acc)
    return acc


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
    """The freeze manifest lists EVERY namespace file (manifest and post-freeze directories excluded) and EVERY pinned
    external file, each with sha256 and git blob; all must match the bytes and the blobs at HEAD."""
    import mb308_manifest as MF
    mp = MF.OUT
    if not mp.exists():
        return {"pass": False, "reason": "no freeze manifest"}
    man = json.loads(mp.read_bytes())
    bad = [rel for rel, v in man["frozen_files"].items()
           if not (REPO / rel).exists() or sha((REPO / rel).read_bytes()) != v["sha256"]
           or git("rev-parse", f"HEAD:{rel}") != v["git_blob"]]
    listed = set(man["frozen_files"])
    on_disk = {str(p.relative_to(REPO)) for p in MF.namespace_files()}
    want_ext = MF.external_pins()
    ext = man.get("external_files", {})
    bad_ext = [k for k, (rel, pin) in want_ext.items()
               if k not in ext or ext[k]["path"] != rel or sha((REPO / rel).read_bytes()) != ext[k]["sha256"]
               or (pin is not None and pin != ext[k]["sha256"]) or git("rev-parse", f"HEAD:{rel}") != ext[k]["git_blob"]]
    required = [D.NS_REL + "/" + r for r in ("protocol/MB308_PROTOCOL.md", "theory/THEOREM_MB.md",
                                             "evidence_prefreeze/DECOY_TIMING_PREFREEZE.json",
                                             "errata/C2B_ERRATA.md", "config/QUALIFICATION_CASES.json")]
    drv_ok = man["driver"]["sha256"] == sha((CODE / "mb308_driver.py").read_bytes())
    try:
        D.check_bindings()
        bind = True
    except (D.Refusal, PIN.PinError):
        bind = False
    return {"manifest_sha256": sha(mp.read_bytes()), "frozen_files": len(listed), "mismatches": bad,
            "unlisted_files": sorted(on_disk - listed), "listed_but_absent": sorted(listed - on_disk),
            "external_files": len(ext), "external_mismatches": bad_ext,
            "required_files_listed": all(r in listed for r in required), "driver_sha_ok": drv_ok,
            "bindings_ok": bind,
            "pass": not bad and on_disk == listed and not bad_ext and len(ext) == len(want_ext) and drv_ok and bind
            and all(r in listed for r in required)}


# ------------------------------------------------------------------ Q1 theory copy
def q1_theory() -> dict:
    raw = (REPO / THEORY_REL).read_bytes() if (REPO / THEORY_REL).exists() else b""
    rel, commit, pin_sha, pin_blob = THEORY_RESEARCH
    out = {"nsf_copy": THEORY_REL, "research": f"{rel}@{commit}",
           "research_blob_at_commit_ok": git("rev-parse", f"{commit}:{rel}") == pin_blob,
           "nsf_sha256_ok": sha(raw) == pin_sha, "nsf_blob_ok": PIN.blob_id(raw) == pin_blob}
    out["pass"] = all(out[k] for k in ("research_blob_at_commit_ok", "nsf_sha256_ok", "nsf_blob_ok"))
    return out


# ------------------------------------------------------------------ Q12 cap rule on the official decoy runtimes
def _decoy_jobs(dec: dict) -> tuple:
    """(jobs, problems) from an official decoy record: runtime and status ONLY (incident review C7(b))."""
    jobs, bad = [], []
    for b in dec["stage1"]["blocks"]:
        if not b.get("run"):
            continue
        for r in b["rlr_rungs"]:
            jobs.append({"kind": "RLR", "rung": r["rung"], "wall": r["wall_seconds"], "ok": r.get("status") == "CERTIFIED"})
        for r in b["c2b_rungs"]:
            v = r.get("verification") or {}
            jobs.append({"kind": "C2B", "rung": r["rung"], "wall": r["wall_seconds"],
                         "ver_seconds": v.get("seconds") or 0.0,
                         "ok": r.get("status_U") == "CERTIFIED" and r.get("status_L") == "CERTIFIED"
                         and v.get("verdict") == "VERIFIED" and v.get("accepted") is True})
        for r in b["c1b_rungs"]:
            jobs.append({"kind": "C1B", "rung": r["rung"], "wall": r["wall_seconds"], "ok": r.get("status") == "CERTIFIED"})
        pw = b["pointwise"]
        c2b_up = [u for u in pw.get("uppers", []) if u["impl"] == "C2B"]
        if pw.get("status") != "CERTIFIED" or pw.get("alarms") or pw.get("refuted_rungs") or \
                pw.get("alarm_unavailable") or not c2b_up or any("alarm_sensitivity" not in u for u in c2b_up):
            bad.append(b["index"])
    return jobs, bad


def lpt_makespan(durations: list, workers: int) -> float:
    """Longest-first list scheduling on `workers` identical workers (protocol 3.2)."""
    loads = [0.0] * workers
    for d in sorted(durations, reverse=True):
        i = loads.index(min(loads))
        loads[i] += d
    return max(loads)


def q12_caps(dec297: dict | None, dec316: dict | None) -> dict:
    """Protocol 3.2 re-derived from the OFFICIAL QC02 (297, all blocks) and QC03 (316, blocks 0-2) runtimes:
    projection = longest-first makespan of 11 blocks x the 9 frozen jobs at 5 workers, each job taking the larger
    official wall time of its kind and rung (C2b: job wall + its recorded in-job verification seconds, the
    protocol table's conservative convention; the job wall already contains the verification). Requires
    EVAL_CAP_S >= ceil(1.5 x projection), every per-job cap >= 2 x the official max wall of its kind and rung,
    every job CERTIFIED (C2b VERIFIED and admitted) and no alarm. Runtime and status only."""
    if not dec297 or not dec316:
        return {"pass": False, "missing": [k for k, v in (("QC02", dec297), ("QC03", dec316)) if not v]}
    j297, bad297 = _decoy_jobs(dec297)
    j316, bad316 = _decoy_jobs(dec316)
    mx = {}
    for j in j297 + j316:
        w = j["wall"] + (j.get("ver_seconds") or 0.0)
        key = (j["kind"], j["rung"])
        mx[key] = max(mx.get(key, 0.0), w)
    missing = [f"{k}:{r}" for k, r in Q12_KEYS if (k, r) not in mx]
    if missing:
        return {"pass": False, "missing_job_kinds": missing}
    durations = [mx[k] for _ in range(Q12_BLOCKS) for k in Q12_KEYS]
    proj = lpt_makespan(durations, Q12_WORKERS)
    need_eval = math.ceil(1.5 * proj)
    caps = {f"{k}:{r}": {"cap_s": D.RUNG_CPU_CAP_S[k][r], "official_max_wall_s": round(mx[(k, r)], 1),
                         "cap_ge_2x": D.RUNG_CPU_CAP_S[k][r] >= 2 * mx[(k, r)]} for k, r in Q12_KEYS}
    out = {"jobs_297": len(j297), "jobs_316": len(j316), "all_jobs_certified": all(j["ok"] for j in j297 + j316),
           "blocks_with_alarm_or_unadmitted_c2b": {"297": bad297, "316": bad316},
           "projection_jobs": len(durations), "projection_job_seconds": round(sum(durations), 1),
           "projection_makespan_s": round(proj, 1), "eval_cap_s": D.EVAL_CAP_S, "eval_cap_required_s": need_eval,
           "eval_cap_ok": D.EVAL_CAP_S >= need_eval, "per_job_caps": caps,
           "stage1_wall_s": {"297": dec297.get("stage1_wall_seconds"), "316": dec316.get("stage1_wall_seconds")},
           "note": "runtime and status only (incident review C7(b))"}
    out["pass"] = out["all_jobs_certified"] and not bad297 and not bad316 and out["eval_cap_ok"] and \
        all(c["cap_ge_2x"] for c in caps.values()) and len(j297) > 0 and len(j316) > 0
    return out


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


TIMING_KEYS = frozenset({"seconds", "wall_seconds", "cpu_seconds"})     # QC04 r2: stripped at EVERY depth, nothing else


def _strip_timing(o):
    if isinstance(o, dict):
        return {k: _strip_timing(v) for k, v in o.items() if k not in TIMING_KEYS}
    if isinstance(o, list):
        return [_strip_timing(v) for v in o]
    return o


def _leaves(o, path=()) -> list:
    if isinstance(o, dict):
        return [lf for k in sorted(o) for lf in _leaves(o[k], path + (k,))]
    if isinstance(o, list):
        return [lf for i, v in enumerate(o) for lf in _leaves(v, path + (i,))]
    return [path]


def _serial_view(job: dict) -> dict:
    """The compared scope of a serial / pooled Stage-1 job (as in r1: the status fields and the record), after the
    driver's own publication projection D.jsonable (it drops the in-memory "_"-prefixed fields such as _cpu_seconds,
    _log_sha256, which no published record carries; the r1 serial child wrote its file without that projection) and
    the recursive timing strip."""
    j = D.jsonable(job)
    keep = {x: j[x] for x in ("status", "status_U", "status_L") if x in j}
    keep["record"] = j.get("record", {})
    return _strip_timing(keep)


def _ladder_view(job: dict) -> dict:
    """The compared scope of a ladder-determinism job (as in r1: the whole job minus cpu_cap at the job level)."""
    j = D.jsonable(job)
    j.pop("cpu_cap", None)
    return _strip_timing(j)


def _compare(a: dict, b: dict, view) -> dict:
    va, vb = view(a), view(b)
    return {"equal": va == vb, "compared_leaves": len(_leaves(va))}


def _planted(a: dict, b: dict, view) -> bool:
    """Mutate ONE non-timing leaf (the middle one of the compared view) in a deep copy of `a`; the SAME comparison
    must report a difference."""
    import copy
    paths = _leaves(view(a))
    if not paths:
        return False
    path = paths[len(paths) // 2]
    m = copy.deepcopy(a)
    node = m
    for k in path[:-1]:
        node = node[k]
    v = node[path[-1]]
    node[path[-1]] = (not v) if isinstance(v, bool) else (v + 1 if isinstance(v, (int, float)) else
                                                           ("planted" if v is None else str(v) + "#planted"))
    return not _compare(m, b, view)["equal"]


def qc04_eval(dec: dict | None, serial: dict | None, det_a: dict | None, det_b: dict | None) -> dict:
    """QC04 r2: (a) block 0 of decoy 297, serial vs pooled; (b) the REVIEW_A0 C4 ladder pair. Every compared pair:
    exactly the timing keys {seconds, wall_seconds, cpu_seconds} are stripped at every depth (and cpu_cap at the job
    level); the comparison must be non-vacuous (> 0 compared leaves per job) and a planted one-leaf mutation of a
    deep copy must be detected by the same comparison."""
    out = {"stripped_keys": sorted(TIMING_KEYS) + ["cpu_cap (job level)"]}
    if dec and serial:
        b0 = dec["stage1"]["blocks"][0]
        pooled = {f"RLR:{r['rung']}": r for r in b0["rlr_rungs"]} | {f"C2B:{r['rung']}": r for r in b0["c2b_rungs"]} | \
            {f"C1B:{r['rung']}": r for r in b0["c1b_rungs"]}
        rows = {}
        for k, r in serial["results"].items():
            if k.startswith("VER"):
                continue
            p = pooled.get(k)
            if p is None:
                rows[k] = {"equal": False, "compared_leaves": 0, "missing_pooled": True, "control_detected": False}
                continue
            rows[k] = _compare(r, p, _serial_view) | {"control_detected": _planted(r, p, _serial_view)}
        out["serial_vs_pooled"] = rows
        out["serial_ok"] = bool(rows) and len(rows) == len(pooled) and all(
            v["equal"] and v["compared_leaves"] > 0 and v["control_detected"] for v in rows.values())
    else:
        out["serial_ok"] = False
    if det_a and det_b:
        ka, kb = det_a.get("results", {}), det_b.get("results", {})
        rows = {}
        for k in sorted(set(ka) | set(kb)):
            if k not in ka or k not in kb:
                rows[k] = {"equal": False, "compared_leaves": 0, "control_detected": False, "missing_one_side": True}
                continue
            rows[k] = _compare(ka[k], kb[k], _ladder_view) | {"control_detected": _planted(kb[k], ka[k], _ladder_view)}
        out["ladder_pair"] = rows
        out["ladder_drifts"] = [det_a.get("drifts"), det_b.get("drifts")]
        out["ladder_pair_identical"] = bool(rows) and all(
            v["equal"] and v["compared_leaves"] > 0 and v["control_detected"] for v in rows.values())
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
    ap.add_argument("--records", help="review / dev without --heavy: directory of the committed heavy-case records "
                                      "(default: qualification/)")
    ap.add_argument("--record-scan", action="store_true", help="dev only: run QC12's committed-record token scan")
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
    if mode == "official" and (a.records or a.record_scan):
        print("QUALIFY REFUSED: --records / --record-scan are review / dev options (official recomputes everything)")
        return 2
    if a.record_scan and mode != "dev":
        print("QUALIFY REFUSED: --record-scan is a dev option (review runs always scan)")
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
    if mode != "official" and not heavy:                     # re-verify the committed heavy records (read only)
        rdir = Path(a.records).resolve() if a.records else QDIR
        for k in ("decoy297", "decoy316", "serial", "det_a", "det_b", "mc"):
            paths[k] = rdir / OUTS[k]
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
        cases["QC12"] = qc12_leak(mode in ("official", "review") or a.record_scan)
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
        if heavy and paths["decoy297"].exists():
            subprocess.run([PY, *FLAGS, str(HERE), "--_child", "mc", "--_decoy", str(paths["decoy297"]), "--out",
                            str(paths["mc"])], env=ENV, cwd=str(REPO))
        cases["QC08"] = load("mc") or {"pass": False, "missing": "decoy 297 record"}
    if "QC13" in sel:
        cases["QC13"] = qc13(pre)
    if mode != "dev":
        cases["Q8"] = q8_manifest()
    cases["Q1_theory"] = q1_theory()
    if mode != "dev" or {"QC02", "QC03"} <= sel:
        cases["Q12_caps"] = q12_caps(load("decoy297"), load("decoy316"))
    missing_pass = sorted(k for k, v in cases.items() if not isinstance(v, dict) or not isinstance(v.get("pass"), bool))
    P = lambda *ks: all(cases.get(k, {}).get("pass") is True for k in ks)    # noqa: E731
    theory = (REPO / RS / "theory/THEOREM_MB.md").exists()
    gates = {"Q1": {"pass": P("QC05", "Q1_theory") and theory}, "Q2": {"pass": P("QC01", "QC06", "QC11", "Q8")},
             "Q3": {"pass": P("QC04")}, "Q4": {"pass": P("QC05", "QC06")}, "Q5": {"pass": P("QC05", "QC07")},
             "Q6": {"pass": P("QC02", "QC03", "QC08")}, "Q7": {"pass": P("QC05")}, "Q8": {"pass": P("Q8")},
             "Q9": {"pass": P("QC09", "QC12")}, "Q10": {"pass": P("QC13")},
             "Q11": {"pass": pre.get("incident_review_accepted_before_freeze") is True},
             "Q12": {"pass": P("QC10", "QC11", "Q12_caps")}}
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
