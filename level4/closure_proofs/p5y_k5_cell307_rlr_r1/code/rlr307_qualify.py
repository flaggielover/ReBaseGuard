"""Cell-307 RLR campaign (r1) -- the qualification verifier (protocol section 9; cases in config/QUALIFICATION_CASES.json).

It can NEVER evaluate cell 307, 306, 308 or 309:
* every certifier call is on a declared decoy outside [6/5, 13/5], and the campaign guard refuses everything else;
* the consumer runs only on cell 305's committed record (rehearse);
* the exactly-once flows run in a `git clone --shared` sandbox with stubbed control and evaluator.

Official run: HEAD must be the freeze commit and no review, grant, marker or result may exist. It writes
qualification/RLR307_QUALIFICATION.json plus the heavy case records next to it, and nothing else in the repository.
The ledger lines of the qualification are carried inside the report (`ledger_entries`), because the qualification
commit may hold qualification files only.

Review run (`--review`): HEAD may be the freeze commit or the qualification commit on it. It writes only --out,
outside the repository. The heavy cases (QC01-QC03) are re-verified from the committed records unless --heavy is given.

    python3.14 -I -S -B rlr307_qualify.py                      (official)
    python3.14 -I -S -B rlr307_qualify.py --review --out FILE  [--heavy]
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
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
import rlr307_driver as D  # noqa: E402
import rlr307_guard as GUARD  # noqa: E402
import rlr307_independent as IND  # noqa: E402
import rlr307_pinned as PIN  # noqa: E402
import rlr307_stage1 as S1  # noqa: E402

PY = sys.executable
FLAGS = ["-I", "-S", "-B"]
QDIR = NS / "qualification"
DECOY_CELL = 297
OUTS = {"report": "RLR307_QUALIFICATION.json", "decoy": "RLR307_DECOY_STAGE1_297.json",
        "serial": "RLR307_QC03_SERIAL_297_B0.json", "qc01": "RLR307_QC01_BLOCK_REPRO.json",
        "rehearse": "RLR307_REHEARSE_305.json", "mc": "RLR307_QC04_MC.json"}
COMMITTED_BLOCK = REPO / (D.CP + "p5y_k5_tail_overnight_research/validation/C1B_R2_PW_BLOCK_1_2__17_32_d4.json")
PRE_GRANT_CLASSES = {"START_STATE_READ", "HISTORICAL_READ", "NONTARGET_DECOY", "SYNTHETIC", "GOVERNANCE", "DISCLOSURE"}
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": os.environ.get("HOME", "/var/empty")}


def git(*args) -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *args], capture_output=True, text=True, env=ENV,
                          stdin=subprocess.DEVNULL).stdout.strip()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decoy_cover(k: int) -> tuple:
    c = [c for c in json.loads(D.read_pinned("cells_json")) if c["detector"] == "CUSUM" and c["index"] == k][0]
    return F(c["left"][0]), F(c["right"][0])


# ------------------------------------------------------------------ barrier: preconditions
def preconditions(review: bool) -> dict:
    fz, head = D.freeze_commit(), git("rev-parse", "HEAD")
    out = {"freeze_commit": fz, "head": head}
    if not review:
        ok_head = head == fz
    else:
        added = git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").split()
        ok_head = head == fz or (git("rev-parse", "HEAD^") == fz and added
                                 and all(a.startswith(D.QUAL_DIR_REL) for a in added))
    out["head_ok"] = bool(ok_head)
    forbidden = [D.QREVIEW_REL, D.GRANT_REL, D.RESULT_REL, D.NS_REL + "/adjudication"]
    out["no_review_grant_result"] = not any(os.path.lexists(REPO / p) or git("log", "--all", "--format=%H", "--", p)
                                            for p in forbidden)
    out["no_marker_refs"] = not any(git("for-each-ref", "--format=%(refname)", p) for p in D.PRIOR_MARKERS)
    gd = Path(git("rev-parse", "--path-format=absolute", "--git-dir"))
    out["no_emergency_file"] = not os.path.lexists(gd / D.EMERGENCY_NAME)
    tracked_dirty = git("status", "--porcelain", "--untracked-files=no")
    out["tracked_clean"] = tracked_dirty == ""
    if not review:
        extra = [ln for ln in git("status", "--porcelain", "--ignored", "--untracked-files=all", "--", D.NS_REL)
                 .splitlines()]
        out["namespace_clean_including_ignored"] = extra == []
    rv = D.NS_REL + "/review/INCIDENT_INDEPENDENCE_REVIEW.md"
    rc = git("log", "-1", "--format=%H", "--", rv)
    lines = (REPO / rv).read_text().splitlines()
    out["incident_review_accepted_before_freeze"] = bool(rc) and lines[1].strip() == "INCIDENT_AUDIT_ACCEPTED" and \
        subprocess.run(["/usr/bin/git", "-C", str(REPO), "merge-base", "--is-ancestor", rc, fz], env=ENV).returncode == 0
    out["pass"] = all(v for k, v in out.items() if k not in ("freeze_commit", "head"))
    return out


# ------------------------------------------------------------------ children (fresh processes)
def child_qc01(out: Path) -> None:
    mods = PIN.load_certifier(REPO, GUARD)
    t0 = time.time()
    rec = S1.certify_rung(mods, F(1, 2), F(17, 32), 4)
    committed = json.loads(COMMITTED_BLOCK.read_bytes())
    crec, clad = committed["records"][0], committed["ladder_min"]
    keys = sorted(k for k, v in crec.items() if isinstance(v, dict) and "exact" in v)
    eq = {k: rec.get(k) == crec[k]["exact"] for k in keys}
    lad = S1.ladder_compose(mods["c1b_certpw"], [rec])
    lkeys = sorted(k for k, v in clad.items() if isinstance(v, dict) and "exact" in v)
    leq = {k: lad.get(k) == clad[k]["exact"] for k in lkeys}
    res = {"status": rec["status"], "committed_status": crec["status"], "exact_fields_compared": len(keys),
           "exact_fields_equal": sum(eq.values()), "unequal": [k for k, v in eq.items() if not v],
           "ladder_fields_compared": len(lkeys), "ladder_fields_equal": sum(leq.values()),
           "wall_seconds": round(time.time() - t0, 1), "identity": mods["_identity"]}
    res["pass"] = bool(rec["status"] == crec["status"] == "CERTIFIED" and all(eq.values()) and all(leq.values())
                       and keys and lkeys)
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")


def child_serial(out: Path) -> None:
    mods = PIN.load_certifier(REPO, GUARD)
    lo, hi = decoy_cover(DECOY_CELL)
    GUARD.guard_drift(lo, hi)
    b = S1.blocks_for(lo, hi)[0]
    t0 = time.time()
    rungs = [S1.certify_rung(mods, b["hull_lo"], b["hull_hi"], d) for d in S1.LADDER]
    lad = S1.ladder_compose(mods["c1b_certpw"], [r for r in rungs if r.get("status") == "CERTIFIED"])
    out.write_text(json.dumps({"decoy_cell": DECOY_CELL, "block": 0, "hull": [S1.fs(b["hull_lo"]), S1.fs(b["hull_hi"])],
                               "rungs": rungs, "block_record": lad, "wall_seconds": round(time.time() - t0, 1),
                               "latent_proxy": "decoy values; never juxtapose with any tail-cell number"},
                              indent=1, sort_keys=True) + "\n")


# ------------------------------------------------------------------ QC03 comparison
def qc03_compare(decoy: dict, serial: dict) -> dict:
    b0 = decoy["stage1"]["blocks"][0]
    pooled = {r["degree"]: r for r in b0["rungs"]}
    per = {}
    for r in serial["rungs"]:
        p = pooled.get(r["degree"], {})
        prec = p.get("record", {})
        keys = [k for k in S1.EXACT_RECORD_KEYS if k in r or k in prec]
        per[r["degree"]] = {"status_equal": r.get("status") == p.get("status"),
                            "exact_equal": all(r.get(k) == prec.get(k) for k in keys), "keys": len(keys)}
    blk_equal = serial["block_record"] == b0["block"]
    return {"per_degree": per, "block_record_identical": blk_equal,
            "hull_identical": serial["hull"] == [b0["hull_lo"], b0["hull_hi"]],
            "pass": blk_equal and all(v["status_equal"] and v["exact_equal"] for v in per.values())
            and len(per) == len(S1.LADDER)}


def qc03_cross_run(decoy: dict | None) -> dict:
    """r2 addition (stricter only): this run's decoy Stage 1 must equal the preserved r1 run's records exactly
    (block records, and every exact rung field), a cross-run determinism check at the same pinned code."""
    r1 = QDIR / "r1_failed" / OUTS["decoy"]
    if not r1.exists():
        return {"pass": True, "note": "no r1 record present (not applicable)"}
    if not decoy:
        return {"pass": False, "missing": "decoy"}
    a, b = json.loads(r1.read_text())["stage1"], decoy["stage1"]
    same_blocks = [x["block"] == y["block"] for x, y in zip(a["blocks"], b["blocks"])]
    same_rungs = []
    for x, y in zip(a["blocks"], b["blocks"]):
        rx = {r["degree"]: r.get("record", {}) for r in x["rungs"]}
        ry = {r["degree"]: r.get("record", {}) for r in y["rungs"]}
        same_rungs.append(all(rx[d].get(k) == ry[d].get(k) for d in rx for k in S1.EXACT_RECORD_KEYS))
    return {"blocks_identical": sum(same_blocks), "rungs_identical_blocks": sum(same_rungs), "blocks": len(b["blocks"]),
            "cell_identical": a["cell"] == b["cell"],
            "pass": len(a["blocks"]) == len(b["blocks"]) and all(same_blocks) and all(same_rungs) and a["cell"] == b["cell"]}


# ------------------------------------------------------------------ QC06 kappa
def qc06() -> dict:
    mods = PIN.load_certifier(REPO, GUARD)
    cp = mods["c1b_certpw"]
    c2 = D.exec_module(D.read_pinned("c2_forecast_code"), REPO / D.PINS["c2_forecast_code"][0], "qual_c2f")
    a = IND.kappa_check(cp.KAPPA1, cp.KAPPA2)
    b = IND.kappa_check(c2.K1_BOUND, c2.K2_BOUND)
    ctl = IND.kappa_check(F(7978845608, 10 ** 10), cp.KAPPA2 - F(1, 10 ** 40))
    return {"certifier": a, "consumer": b, "control_below_true": ctl,
            "pass": a["kappa1_ge_sqrt_2_over_pi"] and a["kappa2_ge_4phi1"] and b["kappa1_ge_sqrt_2_over_pi"]
            and b["kappa2_ge_4phi1"] and not ctl["kappa1_ge_sqrt_2_over_pi"] and not ctl["kappa2_ge_4phi1"]}


# ------------------------------------------------------------------ QC07 guard (in-process part)
def qc07_guard() -> dict:
    def refused(lo, hi):
        try:
            GUARD.guard_drift(lo, hi)
            return False
        except GUARD.QuarantineRefusal:
            return True

    cells = {c["index"]: c for c in json.loads(D.read_pinned("cells_json")) if c["detector"] == "CUSUM"}
    hull307 = [(b["hull_lo"], b["hull_hi"]) for b in S1.blocks_for(*GUARD.CELL307)]
    r = {"cell307_hull_blocks_refused": all(refused(*h) for h in hull307) and len(hull307) == 10,
         "tail_cover_cells_refused": all(refused(F(cells[k]["left"][0]), F(cells[k]["right"][0]))
                                         for k in (305, 306, 307, 308, 309)),
         "band_ends_and_mirror_refused": all(refused(a, b) for a, b in ((F(6, 5), F(6, 5)), (F(13, 5), F(13, 5)),
                                                                        (F(-2), F(-3, 2)), (F(1), F(7, 5)))),
         "decoys_accepted": not any(refused(a, b) for a, b in ((F(1, 2), F(17, 32)), (F(3), F(31, 10)),
                                                               (F(-1, 2), F(-1, 4)), *[(x["hull_lo"], x["hull_hi"])
                                                               for x in S1.blocks_for(*decoy_cover(DECOY_CELL))]))}
    try:
        GUARD.arm_target(str(REPO), git("rev-parse", "HEAD"), hull307)
        r["arm_without_marker_refused"] = False
    except GUARD.QuarantineRefusal:
        r["arm_without_marker_refused"] = True
    mods = PIN.load_certifier(REPO, GUARD)
    t0 = time.time()
    try:
        S1.certify_rung(mods, F(5, 2), F(5, 2) + F(1, 1024), 4)
        r["certifier_path_refuses_band_unarmed"] = False
    except GUARD.QuarantineRefusal:
        r["certifier_path_refuses_band_unarmed"] = time.time() - t0 < 5
    r["pass"] = all(r.values())
    return r


# ------------------------------------------------------------------ QC11 static structure
def qc11_static() -> dict:
    src = (CODE / "rlr307_driver.py").read_text()
    tree = ast.parse(src)
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    def calls_in(fn, name):
        return [c for c in ast.walk(funcs[fn]) if isinstance(c, ast.Call) and
                ((isinstance(c.func, ast.Name) and c.func.id == name) or
                 (isinstance(c.func, ast.Attribute) and c.func.attr == name))]

    r = {}
    main_calls = calls_in("main", "run_execute")
    r["cli_passes_no_injection"] = len(main_calls) == 1 and len(main_calls[0].args) == 1 and not main_calls[0].keywords
    ctl = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "control"]
    tgt_ctl = [c for c in ctl if any(isinstance(a, ast.Name) and a.id == "TARGET_CELL" for a in c.args)]
    grant_line = min(c.lineno for c in calls_in("run_execute", "check_grant"))
    r["target_control_only_in_run_execute_after_grant"] = len(tgt_ctl) == 1 and \
        any(x is tgt_ctl[0] for x in ast.walk(funcs["run_execute"])) and tgt_ctl[0].lineno > grant_line
    st = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "stage1"]
    tgt_st = [c for c in st if c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value == "target"]
    r["stage1_target_only_in_evaluate_target"] = len(tgt_st) == 1 and any(x is tgt_st[0] for x in
                                                                           ast.walk(funcs["evaluate_target"]))
    refs = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "evaluate_target"]
    r["evaluate_target_referenced_only_in_run_execute"] = len(refs) == 1 and any(
        x is refs[0] for x in ast.walk(funcs["run_execute"]))
    upd = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "git"
           and len(c.args) >= 2 and isinstance(c.args[0], ast.Constant) and c.args[0].value == "update-ref"
           and isinstance(c.args[1], ast.Name) and c.args[1].id == "CONSUMED_REF"]
    r["exactly_one_marker_update_ref_in_run_execute"] = len(upd) == 1 and any(x is upd[0] for x in
                                                                              ast.walk(funcs["run_execute"]))
    write_names = {"open", "write_text", "write_bytes", "write", "mkdir", "rename", "replace", "unlink"}
    no_write = {}
    for fn in ("stage1", "evaluate_target", "prepare_target", "_worker_job", "_worker_init", "s_rlr", "decide",
               "control", "evaluate", "cell_inputs", "s_i1", "target_blocks", "after_marker"):
        bad = [c for c in ast.walk(funcs[fn]) if isinstance(c, ast.Call) and
               ((isinstance(c.func, ast.Name) and c.func.id in write_names) or
                (isinstance(c.func, ast.Attribute) and c.func.attr in write_names))]
        no_write[fn] = not bad
    r["no_file_write_in_target_path"] = all(no_write.values())
    r["no_file_write_detail"] = no_write
    allowed = {"cid", "status", "channel"}
    prints = calls_in("after_marker", "print")
    ok_prints = True
    for c in prints:
        for a in c.args:
            if isinstance(a, ast.JoinedStr):
                for v in a.values:
                    if isinstance(v, ast.FormattedValue) and not (isinstance(v.value, ast.Name) and v.value.id in allowed):
                        ok_prints = False
            elif not isinstance(a, ast.Constant):
                ok_prints = False
    r["after_marker_prints_status_only"] = ok_prints and len(prints) >= 1
    s1 = ast.parse((CODE / "rlr307_stage1.py").read_text())
    r["stage1_module_prints_and_writes_nothing"] = not any(
        isinstance(c, ast.Call) and ((isinstance(c.func, ast.Name) and c.func.id in {"print", "open"}) or
                                     (isinstance(c.func, ast.Attribute) and c.func.attr in write_names))
        for c in ast.walk(s1))
    r["pass"] = all(v for k, v in r.items() if k != "no_file_write_detail")
    return r


# ------------------------------------------------------------------ QC12 leak scan
def _tokens_of(obj, acc: set) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _tokens_of(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _tokens_of(v, acc)
    elif isinstance(obj, str) and "/" in obj:
        try:
            x = F(obj)
        except (ValueError, ZeroDivisionError):
            return
        if len(obj) >= 8:
            acc.add(obj)
        _float_token(float(x), acc)
    elif isinstance(obj, float):
        _float_token(obj, acc)


def _float_token(x: float, acc: set) -> None:
    s = f"{abs(x):.12g}"
    digits = s.replace(".", "").lstrip("0")
    if "e" in s or len(digits) < 6:
        return
    # the first six significant digits, written as the number is written (with its decimal point)
    out, n = "", 0
    for ch in s:
        out += ch
        if ch.isdigit() and (n > 0 or ch != "0"):
            n += 1
        if n == 6:
            break
    acc.add(out)


def leak_tokens() -> set:
    acc = set()
    fc = json.loads(D.read_pinned("c2_forecast"))
    _tokens_of(fc["cells"]["307"], acc)
    _tokens_of(fc["supplies"]["307"], acc)
    for key in ("registry_c1", "registry_c2"):
        _tokens_of([b for b in json.loads(D.read_pinned(key))["blocks"] if b["cell"] == 307], acc)
    _tokens_of(json.loads(D.read_pinned("tct_inputs_307")), acc)
    geom = set()
    cell = [c for c in json.loads(D.read_pinned("cells_json")) if c["detector"] == "CUSUM" and c["index"] == 307][0]
    _tokens_of({k: cell[k][0] if isinstance(cell[k], list) else cell[k] for k in ("left", "right", "e0", "rho")}, geom)
    return acc - geom


def scan(texts: dict, tokens: set) -> dict:
    hits = {}
    for name, t in texts.items():
        n = sum(t.count(tok) for tok in tokens)
        if n:
            hits[name] = n
    return hits


def qc12_leak() -> dict:
    tokens = leak_tokens()
    files = git("ls-files", D.NS_REL).splitlines()
    texts = {}
    for f in files:
        try:
            texts[f] = (REPO / f).read_text(errors="replace")
        except OSError:
            pass
    hits = scan(texts, tokens)
    control = scan({"planted": "a line with " + sorted(tokens)[len(tokens) // 2] + " in it"}, tokens)
    return {"tokens": len(tokens), "files_scanned": len(texts), "hit_files": sorted(hits), "hits": sum(hits.values()),
            "planted_control_detected": control.get("planted", 0) >= 1,
            "pass": not hits and control.get("planted", 0) >= 1 and len(tokens) > 20}


# ------------------------------------------------------------------ QC13 temporal / governance
def qc13(pre: dict) -> dict:
    rows = [json.loads(ln) for ln in (NS / "ledger/ZERO_TARGET_LEDGER_307.jsonl").read_text().splitlines() if ln.strip()]
    classes = {r["class"] for r in rows}
    gov = D.check_governance_state()
    r = {"preconditions": pre["pass"], "ledger_pre_grant_classes_only": classes <= PRE_GRANT_CLASSES,
         "ledger_zero_target": all(r["new_target_evaluations"] == 0 and r["target_equivalent_proxies"] == 0
                                   for r in rows), "ledger_lines": len(rows), "governance": gov}
    r["pass"] = r["preconditions"] and r["ledger_pre_grant_classes_only"] and r["ledger_zero_target"]
    return r


# ------------------------------------------------------------------ Q8 manifest
def q8_manifest() -> dict:
    mp = NS / "protocol/RLR307_FREEZE.json"
    man = json.loads(mp.read_bytes())
    bad = []
    for rel, v in man["frozen_files"].items():
        raw = (REPO / rel).read_bytes()
        if sha(raw) != v["sha256"] or git("rev-parse", f"HEAD:{rel}") != v["git_blob"]:
            bad.append(rel)
    listed = set(man["frozen_files"])
    on_disk = {str(p.relative_to(REPO)) for d in D.FROZEN_DIRS for p in (NS / d).rglob("*")
               if p.is_file() and p != mp and "__pycache__" not in p.parts}
    drv_ok = man["driver"]["sha256"] == sha((CODE / "rlr307_driver.py").read_bytes())
    try:
        shas = D.check_bindings()
        bind = True
    except (D.Refusal, PIN.PinError) as e:
        shas, bind = str(e), False
    return {"manifest_sha256": sha(mp.read_bytes()), "frozen_files": len(listed), "mismatches": bad,
            "unlisted_files": sorted(on_disk - listed), "driver_sha_ok": drv_ok, "bindings_ok": bind,
            "pass": not bad and on_disk == listed and drv_ok and bind}


# ------------------------------------------------------------------ main
def spawn(args: list, log: Path) -> subprocess.Popen:
    return subprocess.Popen([PY, *FLAGS, *args], stdout=log.open("w"), stderr=subprocess.STDOUT, env=ENV,
                            stdin=subprocess.DEVNULL, cwd=str(REPO))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--heavy", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--_child", choices=("qc01", "serial"))
    a = ap.parse_args(argv)
    if a._child:
        (child_qc01 if a._child == "qc01" else child_serial)(Path(a.out))
        return 0
    t0, started = time.time(), utc()
    pre = preconditions(a.review)
    if not pre["pass"]:
        print(f"QUALIFY REFUSED: preconditions {json.dumps(pre)}")
        return 2
    official = not a.review
    heavy = official or a.heavy
    work = Path(tempfile.mkdtemp(prefix="rlr307q"))
    odir = QDIR if official else work
    if official:
        odir.mkdir(exist_ok=True)
    paths = {k: odir / v for k, v in OUTS.items()}
    procs = {}
    if heavy:
        procs["decoy"] = spawn([str(CODE / "rlr307_driver.py"), "decoy-stage1", "--cell", str(DECOY_CELL), "--out",
                                str(paths["decoy"])], work / "decoy.log")
        procs["serial"] = spawn([str(HERE), "--_child", "serial", "--out", str(paths["serial"])], work / "serial.log")
        procs["qc01"] = spawn([str(HERE), "--_child", "qc01", "--out", str(paths["qc01"])], work / "qc01.log")
    else:
        for k in ("decoy", "serial", "qc01"):
            paths[k] = QDIR / OUTS[k]                                   # the committed records
    reh = subprocess.run([PY, *FLAGS, str(CODE / "rlr307_driver.py"), "rehearse", "--cell", "305", "--out",
                          str(paths["rehearse"])], capture_output=True, text=True, env=ENV, cwd=str(REPO))
    cases = {}
    cases["QC06"] = qc06()
    cases["QC07_inprocess"] = qc07_guard()
    cases["QC11"] = qc11_static()
    cases["QC12"] = qc12_leak()
    cases["Q8"] = q8_manifest()
    import test_rlr307_flows as TF  # noqa: E402
    flows = TF.run_flows(pre["freeze_commit"], work / "flows")
    cases["QC10"] = {k: v for k, v in flows.items() if k != "flows"}
    cases["QC10"]["flows"] = {k: {"ok": v["ok"], "run": v.get("run")} for k, v in flows["flows"].items()}
    cases["QC10"]["pass"] = bool(flows["all_ok"]) and not flows["failed"]      # r2 repair: r1 lacked this key
    cases["QC07"] = {"in_process": cases.pop("QC07_inprocess"), "sandbox_arming": flows["flows"].get("QC07_arming")}
    cases["QC07"]["pass"] = cases["QC07"]["in_process"]["pass"] and bool(cases["QC07"]["sandbox_arming"]
                                                                          and cases["QC07"]["sandbox_arming"]["ok"])
    rh = json.loads(paths["rehearse"].read_text()) if paths["rehearse"].exists() else {}
    cases["QC08"] = {"exit": reh.returncode, "control": rh.get("control", {}).get("field_matches"),
                     "neutral_substitution": rh.get("neutral_substitution"),
                     "pass": reh.returncode == 0 and rh.get("control", {}).get("reproduces_C2_exactly") is True
                     and all((rh.get("neutral_substitution") or {"x": False}).values())}
    for k, p in procs.items():
        p.wait()
    rcs = {k: p.returncode for k, p in procs.items()}
    decoy = json.loads(paths["decoy"].read_text()) if paths["decoy"].exists() else None
    serial = json.loads(paths["serial"].read_text()) if paths["serial"].exists() else None
    q1 = json.loads(paths["qc01"].read_text()) if paths["qc01"].exists() else {"pass": False}
    cases["QC01"] = q1
    st = (decoy or {}).get("stage1", {})
    walls = {}
    for b in st.get("blocks", []):
        for r in b["rungs"]:
            walls[r["degree"]] = max(walls.get(r["degree"], 0), r["wall_seconds"])
    proj = 2 * sum(walls.values()) if walls else None                  # 10 blocks, 5 workers: two rounds per degree
    cases["QC02"] = {"exit": rcs.get("decoy", "committed"), "cell_status": st.get("cell", {}).get("status"),
                     "independent_checks": st.get("independent_checks"), "ladder": st.get("ladder"),
                     "blocks": len(st.get("blocks", [])),
                     "rung_status": {f"b{b['index']}d{r['degree']}": r.get("status", r.get("kind"))
                                     for b in st.get("blocks", []) for r in b["rungs"]},
                     "max_rung_wall_by_degree": walls, "projected_cell307_wall_s": proj,
                     "pass": bool(decoy) and st.get("cell", {}).get("status") == "CERTIFIED"
                     and (st.get("independent_checks") or {}).get("all_equal") is True
                     and st.get("ladder") == list(S1.LADDER) and len(st.get("blocks", [])) == 5}
    cases["QC03"] = qc03_compare(decoy, serial) if decoy and serial else {"pass": False, "missing": True}
    cases["QC03_cross_run"] = qc03_cross_run(decoy)
    import test_rlr307_mc as TM  # noqa: E402
    import test_rlr307_twosided as TT  # noqa: E402
    if decoy:
        mc = TM.run(st)
        if official:
            paths["mc"].write_text(json.dumps(mc, indent=1, sort_keys=True) + "\n")
        cases["QC04"] = {k: v for k, v in mc.items() if k != "rows"} | {"rows_all_hold": all(r.get("all_hold")
                                                                                        for r in mc["rows"])}
        mods = PIN.load_certifier(REPO, GUARD)
        cases["QC05"] = TT.assembly_test(mods["c1b_certpw"], IND, st)
        cases["QC09"] = TT.composition_test(mods["c1b_certpw"], IND, S1, D, st)
    else:
        cases["QC04"] = cases["QC05"] = cases["QC09"] = {"pass": False, "missing": "decoy stage 1"}
    cases["QC13"] = qc13(pre)
    cap_ok = proj is not None and proj <= D.EVAL_CAP_S / 2 and proj <= 4 * 3600
    missing_pass = sorted(k for k, v in cases.items() if not isinstance(v.get("pass"), bool))   # r2: fail loudly
    P = lambda *ks: all(cases[k].get("pass") is True for k in ks)       # noqa: E731
    gates = {
        "Q1": {"pass": P("QC05") and (NS / "theory/THEOREM_RLR307.md").exists(),
               "note": "automated: theorem formulas = independent module = pinned assembly; proof checked by the reviewer"},
        "Q2": {"pass": P("QC01", "QC08", "QC11", "Q8")},
        "Q3": {"pass": P("QC01", "QC03", "QC03_cross_run")},
        "Q4": {"pass": P("QC05", "QC06") and cases["QC05"].get("float_reaching_exact_layer_raises") is True},
        "Q5": {"pass": P("QC05") and cases["QC05"].get("historical_mutants_rejected") == "6/6"},
        "Q6": {"pass": P("QC02", "QC04")},
        "Q7": {"pass": P("QC05", "QC09")},
        "Q8": {"pass": P("Q8", "QC06")},
        "Q9": {"pass": P("QC07", "QC12") and cases["QC13"]["ledger_pre_grant_classes_only"]},
        "Q10": {"pass": P("QC13")},
        "Q11": {"pass": pre["incident_review_accepted_before_freeze"]},
        "Q12": {"pass": P("QC10", "QC11") and cap_ok, "projected_cell307_wall_s": proj, "eval_cap_s": D.EVAL_CAP_S},
    }
    ok = all(g["pass"] for g in gates.values()) and not missing_pass
    report = {"schema": "rebaseguard.p5y.k5.cell307-rlr-r1.qualification.v1", "freeze_commit": pre["freeze_commit"],
              "head": pre["head"], "review_mode": not official, "heavy_recomputed": heavy, "preconditions": pre,
              "cases": cases, "gates": gates, "pass": ok, "cases_missing_pass": missing_pass, "started_utc": started, "finished_utc": utc(),
              "wall_seconds": round(time.time() - t0, 1), "verifier_sha256": sha(HERE.read_bytes()),
              "python": sys.version.split()[0],
              "record_sha256": {k: sha(p.read_bytes()) for k, p in paths.items() if k != "report" and p.exists()},
              "ledger_entries": [
                  {"class": "NONTARGET_DECOY", "what": f"QC01 committed block [1/2,17/32] d4; QC02/QC03/QC04 decoy cover "
                   f"cell {DECOY_CELL} (5 blocks, ladder {list(S1.LADDER)})", "recomputed": heavy},
                  {"class": "HISTORICAL_READ", "what": "QC08 rehearse cell 305 (committed-record reproduction only); QC12 "
                   "committed cell-307 records read to form leak-scan tokens (never printed)"},
                  {"class": "SYNTHETIC", "what": "QC05/QC09 synthetic and planted sets; QC10 sandbox flows with stubs"}],
              "target_evaluations": 0}
    out = Path(a.out) if a.out else paths["report"]
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(f"QUALIFICATION {'PASS' if ok else 'FAIL'}: " + " ".join(f"{k}={'P' if v['pass'] else 'F'}"
                                                              for k, v in gates.items()))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
