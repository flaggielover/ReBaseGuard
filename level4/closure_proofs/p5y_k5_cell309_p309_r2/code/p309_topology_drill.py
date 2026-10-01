"""P309-r2 post-freeze topology drill (R2-I5; plan section 5; review P5; addenda 1-2).  q309: literal-ok (ref names)

  python3 -B code/p309_topology_drill.py --tier cloud [--keep]    development tier: the items one by one, no systemd
  python3 -B code/p309_topology_drill.py --tier worker [--keep]   worker tier: started by code/p309_launch.py --mode drill

Development evidence, never qualification evidence.  The runner gains no drill mode: each drill runs the runner bytes
that are later frozen, from a clone of the committed branch.

1. A scratch clone of the P309 repository's committed branch under <P309_SCRATCH_ROOT>/drill_<utc>/clone.  The
   drill refuses unless all of these hold: the P309 namespace's working tree is clean (the drill imports the host
   package from it; A4); the clone lies under the drill root; its git common dir differs from the P309 repository's;
   it has no remote, no push URL and no remote.pushDefault.
2. In the clone only:
   * the unmodified generators and the placeholder check make a synthetic freeze F';
   * its record-only child FR' records F' (ledger/FREEZE_RECORD.json);
   * one checkpoint-style record commit follows, as after a real push.
3. Every clone script runs as a subprocess of the clone's own files: argv paths and cwd are in the clone; the
   environment has no PYTHONPATH and its own P309_SCRATCH_ROOT under the drill root.  This tool imports nothing from
   the runner, the driver, the guard, the generators or the tests (F2).
4. Topology witness (F2):
   * the clone's recorded_freeze returns F';
   * F' has exactly one record child;
   * F''s history holds 0 record commits;
   * one QC11 sandbox (F02_grant_not_at_head) holds exactly one record commit and descends from F'.
5. Items:
   * cloud tier: every item except QC06, QC08, QC09 and QC10, each in its own subprocess through the runner's
     items_table() and run_item() (F3);
   * worker tier: the runner's main() through the launch unit (P14).  If Q-HOST aborts the runner (exit 3, or
     QHOST_FAIL.json in the attempt), the runner has already SIGKILLed its own tree and the drill stops at once: no
     witness, host function or control runs after it (review C5).  The report embeds the (redacted) launch record and
     the unit's effective properties.
   After each runner call, the changes it left (against the clone's HEAD at the call) must lie in qualification/ and
   the execution and exposure ledgers (F5).
6. Host functions (F3): the clone's p309_host.py provenance (twice, then continuity) and preflight, and the
   clone's tests/test_p309_host.py (the host package's and launcher's decision tests), tests/test_p309_host_controls.py
   (the P9-P11 controls on the real /proc, the launcher and the runner's Q-HOST refusals; review C11) and
   tests/test_p309_static_controls.py (QC12 T11-T14 negative controls; review C10).  The preflight is expected to FAIL
   on the cloud tier and to PASS on the worker tier.  The r1-tree check runs as well.
7. Controls, each of which must fail as stated:
   * R2-M01a: the r1 base (HEAD) with the pre- and postconditions removed; QC11 fails with the uncaught refusal
     line `p309_driver.Refusal: FREEZE_RECORD` (A2);
   * R2-M01b: the r1 base (HEAD) with the conditions kept; the harness raises "QC11 harness" (fail loud);
   * a planted second freeze-record commit: recorded_freeze refuses (FREEZE_RECORD);
   * the TEST-only prior ref refs/p5y-k5-cell309-TEST-ONLY-prior/x: check_not_evaluated refuses (CONSUMED).  No ref
     in either production namespace is ever created (F1);
   * a repository with a push URL, and the P309 repository itself: the drill's own guard refuses.
   The mutants exist only in the clone and are never committed.
8. Before and after: the P309 repository's HEAD, refs and status are identical, or the drill fails (F2).
9. Export (F4):
   * into FNS2 evidence/drill/<utc>/: the drill ledger's rows in full with their sha256, the counters (target
     evaluations 0), the band check, the witnesses, the controls and the item verdicts.  No decoy output and no
     qualification output file is copied;
   * one GOVERNANCE row in the official FNS2 ledger.
   The drill root is then deleted (unless --keep).

The ledger verdict also requires completeness (A3): one RUN START row, and rows from every script the items and host
functions must log.

Exit 0 iff every step, witness and control holds.  NEW Γ309 TARGET EVALUATIONS = 0 by construction: nothing here
reads a target input or evaluates a quarantined cell.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
NS_REL = FNS.relative_to(REPO).as_posix()
BRANCH = "claude/p5y-k5-cell309-p309-r2"  # q309: literal-ok (branch name, not a cell reference)
sys.path.insert(0, str(FNS / "code"))
import p309_host as H  # noqa: E402

RECORD_REL = NS_REL + "/ledger/FREEZE_RECORD.json"
CHECKPOINT_REL = NS_REL + "/ledger/CHECKPOINT_PUSHES.jsonl"
LEDGER_RELS = (NS_REL + "/ledger/ZERO_TARGET_LEDGER.jsonl", NS_REL + "/ledger/EXPOSURE_LEDGER.jsonl")
QUAL_PREFIX = NS_REL + "/qualification/"
R1_REL = "level4/closure_proofs/p5y_k5_cell309_p309_r1"
R1_TREE = "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b"
CLOUD_ITEMS = ("QC01", "QC02", "QC03", "QC04", "QC05", "QC07", "QC11", "QC12", "QC13", "QC14", "QC15", "QC16",
               "QC17", "QC_U2", "QC_D5")
TEST_PRIOR_REF = "refs/p5y-k5-cell309-TEST-ONLY-prior/x"  # q309: literal-ok (TEST-only prefix control; in neither namespace)
WITNESS_SANDBOX = "F02_grant_not_at_head"
BAND = (Fraction(6, 5), Fraction(13, 5))   # q309: literal-ok (the quarantine band definition, used only to classify)
GIT_ENV = {"LC_ALL": "C", "GIT_PAGER": "cat", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_OPTIONAL_LOCKS": "0", "PATH": "/usr/bin:/bin",
           "GIT_AUTHOR_NAME": "p309-r2-drill", "GIT_AUTHOR_EMAIL": "p309-r2-drill@invalid",
           "GIT_COMMITTER_NAME": "p309-r2-drill", "GIT_COMMITTER_EMAIL": "p309-r2-drill@invalid"}
INHERIT = ("P309_LAUNCH_RECORD", "P309_HOST_CONFIG", "INVOCATION_ID", "P309_FOREIGN_ROOTS", "LC_ALL", "PATH", "HOME")
LEDGER_REQUIRED = ("code/p309_qualify.py", "code/p309_static_check.py", "code/p309_rehearse.py",
                   "tests/test_p309_exactly_once.py", "tests/test_p309_guard.py", "verify/run_verify_all_scoped.py",
                   "tests/test_p309_host.py", "tests/test_p309_host_controls.py", "tests/test_p309_static_controls.py")

# the python -c programs run in the clone (literal: the scanner parses and checks them)
ITEM_CODE = """
import json, os, sys
sys.path[:0] = [os.environ["P309_DRILL_CODE"]]
import p309_qualify as QQ
assert str(QQ.REPO) == os.environ["P309_DRILL_CLONE"], "the runner resolved another repository"
freeze = QQ.D.recorded_freeze()
QQ.ATT["dir"] = QQ.QDIR / "attempt_drill"
if not QQ.ATT["dir"].exists():
    QQ.E.log("code/p309_qualify.py", QQ.RUN_START + " attempt_drill at the recorded freeze " + freeze[:12]
             + " (topology drill: development only, in the drill clone)", klass="GOVERNANCE", notes="topology drill")
QQ.ATT["dir"].mkdir(parents=True, exist_ok=True)
(QQ.ATT["dir"] / "evidence").mkdir(exist_ok=True)
m = QQ.mirror(freeze)
k = os.environ["P309_DRILL_ITEM"]
res = QQ.run_item(k, QQ.items_table(m, freeze, 4)[k], freeze)
print("DRILL_ITEM_RESULT " + json.dumps({"qc": k, "pass": bool(res.get("pass")), "wall_s": res.get("wall_s")}))
"""
FREEZE_CODE = """
import json, os, sys
sys.path[:0] = [os.environ["P309_DRILL_CODE"]]
import p309_driver as D
assert str(D.REPO) == os.environ["P309_DRILL_CLONE"], "the driver resolved another repository"
try:
    print("DRILL_FREEZE " + json.dumps({"recorded": D.recorded_freeze()}))
except D.Refusal as exc:
    print("DRILL_FREEZE " + json.dumps({"refused": exc.code, "detail": str(exc)}))
"""
PRIOR_REF_CODE = """
import json, os, sys, types
from pathlib import Path
sys.path[:0] = [os.environ["P309_DRILL_CODE"]]
import p309_driver as D
assert str(D.REPO) == os.environ["P309_DRILL_CLONE"], "the driver resolved another repository"
probe = types.SimpleNamespace(repo=Path(os.environ["P309_DRILL_CLONE"]), namespace=D.G._TEST_NAMESPACE,
                              result_rel=D.SANDBOX_RESULT_REL)
try:
    D.check_not_evaluated(probe)
    print("DRILL_PRIOR " + json.dumps({"refused": None}))
except D.Refusal as exc:
    print("DRILL_PRIOR " + json.dumps({"refused": exc.code, "detail": str(exc)}))
"""


class DrillError(Exception):
    pass


# ------------------------------------------------------------------------------------------------- runners
def git(repo, *args, check=True) -> str:
    """git -C <repo> <args> with a fixed hermetic environment (a registered git runner: callers' verbs are classified)"""
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=GIT_ENV, timeout=3600,
                       stdin=subprocess.DEVNULL)
    if check and p.returncode != 0:
        raise DrillError(f"git {args[0]} failed: {p.stderr.strip()[-300:]}")
    return p.stdout.strip()


def run_py(argv: list, clone: Path, scratch: Path, item: str = "", timeout: int = 6 * 3600) -> dict:
    """a python argv of the clone's own files (a registered argv runner): cwd in the clone's namespace; the environment
    is built here, with no PYTHONPATH, the drill's own scratch root and TMPDIR, and only the INHERIT keys"""
    env = {k: os.environ[k] for k in INHERIT if k in os.environ}
    env.update({"P309_SCRATCH_ROOT": str(scratch), "TMPDIR": str(scratch / "tmp"), "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONNOUSERSITE": "1", "P309_DRILL_CODE": str(clone / NS_REL / "code"),
                "P309_DRILL_CLONE": str(clone), "P309_DRILL_ITEM": item})
    t0 = time.time()
    p = subprocess.run(argv, cwd=str(clone / NS_REL), capture_output=True, text=True, env=env, timeout=timeout,
                       stdin=subprocess.DEVNULL)
    return {"rc": p.returncode, "wall_s": round(time.time() - t0, 1), "stdout": p.stdout, "stderr": p.stderr}


def tagged(out: str, tag: str) -> dict:
    for line in out.splitlines():
        if line.startswith(tag + " "):
            return json.loads(line[len(tag) + 1:])
    return {}


# --------------------------------------------------------------------------------------------- the guards
def guard_clone(clone: Path, drill_root: Path) -> dict:
    """P5: the clone lies under the drill root, has its own git common dir, and has no remote or push URL"""
    common = Path(git(clone, "rev-parse", "--path-format=absolute", "--git-common-dir", check=False) or "/")
    p309_common = Path(git(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    conf = git(clone, "config", "--list", "--show-scope", check=False).splitlines()
    checks = {"under_drill_root": H.under(str(clone), [str(drill_root)]) and H.real(str(clone)) != H.real(str(drill_root)),
              "own_common_dir": H.real(str(common)) != H.real(str(p309_common)),
              "no_remote_or_push_url": not [c for c in conf if re.search(r"\tremote\.|\tbranch\..*\.remote=", c)
                                            or "pushdefault" in c.lower()]}
    return {"checks": checks, "pass": all(checks.values())}


def p309_state() -> dict:
    return {"head": H.git_read(str(REPO), "rev-parse", "HEAD"),
            "refs_sha256": H.sha(H.git_read(str(REPO), "for-each-ref", "--format=%(objectname) %(refname)") or ""),
            "status_sha256": H.sha(H.git_read(str(REPO), "status", "--porcelain", "--untracked-files=all") or "")}


def leftover(clone: Path) -> list:
    """uncommitted paths in the clone (porcelain, untracked included)"""
    out = []
    for line in git(clone, "status", "--porcelain", "--untracked-files=all").splitlines():
        m = re.match(r"^\s*\S{1,2}\s+(.*)$", line)       # the runner strips the output's first leading space
        if m:
            out.append(m.group(1))
    return out


def confined(paths: list) -> bool:
    return all(p.startswith(QUAL_PREFIX) or p in LEDGER_RELS for p in paths)


# ------------------------------------------------------------------------------------------- the topology
def make_topology(clone: Path, scratch: Path) -> dict:
    """F' (unmodified generators + placeholder check), FR' (record only), then one checkpoint record commit"""
    code = clone / NS_REL / "code"
    gen = [run_py([sys.executable, "-B", str(code / "make_freeze_manifest.py")], clone, scratch),
           run_py([sys.executable, "-B", str(code / "make_freeze_params.py")], clone, scratch),
           run_py([sys.executable, "-B", str(code / "p309_placeholder_check.py")], clone, scratch)]
    if any(g["rc"] != 0 for g in gen):
        raise DrillError("generators/placeholder check failed in the clone: " + " | ".join(
            (g["stdout"] + g["stderr"])[-300:] for g in gen if g["rc"] != 0))
    git(clone, "add", NS_REL)
    git(clone, "commit", "-q", "-m", "drill: synthetic freeze F' (unmodified generators; never pushed)")
    f = git(clone, "rev-parse", "HEAD")
    (clone / RECORD_REL).write_text(json.dumps({"freeze_commit": f, "recorded_utc": H.utc(),
                                                "rule": "drill: F's record-only child"}, indent=1) + "\n")
    git(clone, "add", RECORD_REL)
    git(clone, "commit", "-q", "-m", "drill: freeze record FR' (record only)")
    fr = git(clone, "rev-parse", "HEAD")
    with open(clone / CHECKPOINT_REL, "a") as fh:
        fh.write(json.dumps({"utc": H.utc(), "drill": True, "content_head": fr}) + "\n")
    git(clone, "add", CHECKPOINT_REL)
    git(clone, "commit", "-q", "-m", "drill: checkpoint-style record commit")
    return {"F": f, "FR": fr, "tip": git(clone, "rev-parse", "HEAD"), "generators": [g["rc"] for g in gen]}


def witness(clone: Path, scratch: Path, topo: dict) -> dict:
    fz = tagged(run_py([sys.executable, "-B", "-c", FREEZE_CODE], clone, scratch)["stdout"], "DRILL_FREEZE")
    children = git(clone, "log", "--format=%H", "--", RECORD_REL).split()
    base_hist = git(clone, "log", "--format=%H", topo["F"], "--", RECORD_REL).split()
    w = {"recorded_freeze_is_F": fz.get("recorded") == topo["F"], "one_record_commit": children == [topo["FR"]],
         "F_history_holds_no_record": not base_hist}
    sb = scratch / "qc11_sandboxes" / WITNESS_SANDBOX
    if (sb / ".git").exists():
        w["qc11_sandbox_one_record"] = len(git(sb, "log", "--format=%H", "--", RECORD_REL).split()) == 1
        w["qc11_sandbox_descends_from_F"] = git(sb, "merge-base", topo["F"], "HEAD", check=False) == topo["F"]
    return w


# --------------------------------------------------------------------------------------------- the items
def run_items(clone: Path, scratch: Path, tier: str) -> dict:
    out = {}
    code = clone / NS_REL / "code"
    if tier == "worker":
        head = git(clone, "rev-parse", "HEAD")
        r = run_py([sys.executable, "-B", str(code / "p309_qualify.py"), "--workers", "4"], clone, scratch,
                   timeout=12 * 3600)
        left = leftover(clone)
        summary = clone / NS_REL / "qualification" / "P309_QUALIFICATION.json"
        s = json.loads(summary.read_text()) if summary.exists() else {}
        out["main"] = {"rc": r["rc"], "wall_s": r["wall_s"], "pass": bool(s.get("pass")), "gates": s.get("gates"),
                       "head_unchanged": git(clone, "rev-parse", "HEAD") == head, "confined": confined(left)}
        if r["rc"] == 3 or (clone / NS_REL / "qualification" / "attempt_1" / "QHOST_FAIL.json").exists():
            raise DrillError("Q-HOST aborted the runner; the drill stops at once (review C5): " + json.dumps(out["main"]))
        return out
    for k in CLOUD_ITEMS:
        head = git(clone, "rev-parse", "HEAD")
        r = run_py([sys.executable, "-B", "-c", ITEM_CODE], clone, scratch, item=k)
        res = tagged(r["stdout"], "DRILL_ITEM_RESULT")
        left = leftover(clone)
        out[k] = {"rc": r["rc"], "pass": bool(res.get("pass")), "wall_s": res.get("wall_s", r["wall_s"]),
                  "head_unchanged": git(clone, "rev-parse", "HEAD") == head, "confined": confined(left),
                  "tail": "" if res.get("pass") else (r["stdout"] + r["stderr"])[-600:]}
        print(f"[drill {'PASS' if out[k]['pass'] else 'FAIL'}] {k} ({out[k]['wall_s']} s)", flush=True)
    return out


# ------------------------------------------------------------------------------------------- the controls
def mutant(clone: Path, which: str) -> Path:
    """R2-M01a/b: the QC11 harness with r1's base rule restored (outside FNS2's history: the clone only)"""
    src = (clone / NS_REL / "tests" / "test_p309_exactly_once.py").read_text()
    new_base = '    head, _mode = sandbox_base()                 # r2 P6: F after the freeze, HEAD before it (never "HEAD" blindly)\n'
    old_base = ('    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,\n'
                '                          check=True).stdout.strip()\n')
    if src.count(new_base) != 1:
        raise DrillError("mutant: the harness's base line was not found exactly once")
    src = src.replace(new_base, old_base)
    if which == "a":
        for old, new in (("    if have != want:\n", "    if False:\n"),
                         ("    man = manifest_bytes()                       # r2 P6(a)\n",
                          "    man = (REPO / D.MANIFEST_REL).read_bytes()\n")):
            if src.count(old) < 1:
                raise DrillError("mutant a: a condition line was not found")
            src = src.replace(old, new)
    p = clone / NS_REL / "tests" / f"drill_mutant_M01{which}.py"
    p.write_text(src)
    return p


def controls(clone: Path, scratch: Path, drill_root: Path, topo: dict) -> dict:
    c = {}
    tests = clone / NS_REL / "tests"
    pa = mutant(clone, "a")
    ra = run_py([sys.executable, "-B", str(tests / "drill_mutant_M01a.py")], clone, scratch, timeout=4 * 3600)
    pa.unlink()
    pb = mutant(clone, "b")
    rb = run_py([sys.executable, "-B", str(tests / "drill_mutant_M01b.py")], clone, scratch, timeout=4 * 3600)
    pb.unlink()
    ta, tb = ra["stdout"] + ra["stderr"], rb["stdout"] + rb["stderr"]
    c["R2_M01a"] = {"rc": ra["rc"], "caught": ra["rc"] != 0 and "\np309_driver.Refusal: FREEZE_RECORD: " in ta,
                    "tail": ta[-400:]}
    c["R2_M01b"] = {"rc": rb["rc"], "caught": rb["rc"] != 0 and "QC11 harness" in tb, "tail": tb[-400:]}
    tip = git(clone, "rev-parse", "HEAD")
    record_bytes = (clone / RECORD_REL).read_bytes()
    ledgers_before = {rel: (clone / rel).read_bytes() for rel in LEDGER_RELS if (clone / rel).exists()}
    (clone / RECORD_REL).write_text(json.dumps({"freeze_commit": topo["F"], "planted": "second record"}) + "\n")
    git(clone, "add", RECORD_REL)
    git(clone, "commit", "-q", "-m", "drill control: a planted second freeze-record commit")
    fz = tagged(run_py([sys.executable, "-B", "-c", FREEZE_CODE], clone, scratch)["stdout"], "DRILL_FREEZE")
    c["second_freeze_record"] = {"caught": fz.get("refused") == "FREEZE_RECORD", "got": fz}
    # back to the tip without touching the working tree's uncommitted ledger rows (F4): move the branch and the index
    # only, then restore the record file's committed bytes
    git(clone, "reset", "-q", "--mixed", tip)
    (clone / RECORD_REL).write_bytes(record_bytes)
    c["ledger_rows_kept_across_reset"] = all((clone / rel).read_bytes().startswith(b) for rel, b in ledgers_before.items())
    git(clone, "update-ref", TEST_PRIOR_REF, tip)
    pr = tagged(run_py([sys.executable, "-B", "-c", PRIOR_REF_CODE], clone, scratch)["stdout"], "DRILL_PRIOR")
    git(clone, "update-ref", "-d", TEST_PRIOR_REF)
    c["test_only_prior_ref"] = {"caught": pr.get("refused") == "CONSUMED", "got": pr}
    ctl = drill_root / "ctl_push"
    git(drill_root, "init", "-q", str(ctl))
    git(ctl, "remote", "add", "origin", "https://example.invalid/p309-drill-control.git")
    c["push_url_refused"] = {"caught": not guard_clone(ctl, drill_root)["pass"]}
    c["p309_repository_refused"] = {"caught": not guard_clone(REPO, drill_root)["pass"]}
    c["after_reset_tip"] = git(clone, "rev-parse", "HEAD") == tip
    ns_prefix = "refs/p5y-k5-cell309-p309-r"  # q309: literal-ok (both production namespaces' common prefix; refusal check)
    c["no_production_namespace_ref"] = not [r for r in git(clone, "for-each-ref", "--format=%(refname)").split()
                                            if r.startswith(ns_prefix)]
    return c


# --------------------------------------------------------------------------------------------- host + ledger
def host_functions(clone: Path, scratch: Path, tier: str) -> dict:
    code = clone / NS_REL / "code"
    a = run_py([sys.executable, "-B", str(code / "p309_host.py"), "provenance"], clone, scratch)
    b = run_py([sys.executable, "-B", str(code / "p309_host.py"), "provenance"], clone, scratch)
    pcfg = {"p309_repo": str(clone), "p309_roots": [str(clone)]}
    if tier == "worker":                       # the worker's real host configuration file, as the launch record binds it
        rec = json.loads(Path(os.environ["P309_LAUNCH_RECORD"]).read_text())
        if H.file_sha256(os.environ["P309_HOST_CONFIG"]) != rec["host_config_file_sha256"]:
            raise DrillError("the host configuration file differs from the one the launch record binds")
        pcfg = H.load_launch_config(os.environ["P309_HOST_CONFIG"], str(clone), False)[0]
    pf = run_py([sys.executable, "-B", str(code / "p309_host.py"), "preflight", "--config-json", json.dumps(pcfg)],
                clone, scratch)
    ht = run_py([sys.executable, "-I", "-S", "-B", str(clone / NS_REL / "tests" / "test_p309_host.py")], clone, scratch)
    hc = run_py([sys.executable, "-I", "-S", "-B", str(clone / NS_REL / "tests" / "test_p309_host_controls.py")], clone,
                scratch)
    sc = run_py([sys.executable, "-I", "-S", "-B", str(clone / NS_REL / "tests" / "test_p309_static_controls.py")], clone,
                scratch)
    cfg = H.load_config([])
    cont = H.continuity(json.loads(a["stdout"]), json.loads(b["stdout"]), cfg) if a["rc"] == 0 and b["rc"] == 0 else {
        "pass": False}
    return {"provenance_rc": [a["rc"], b["rc"]], "continuity_pass": cont["pass"], "preflight_rc": pf["rc"],
            "preflight_as_expected": (pf["rc"] != 0) if tier == "cloud" else (pf["rc"] == 0),
            "r1_tree_unchanged": git(clone, "rev-parse", f"HEAD:{R1_REL}") == R1_TREE,
            "host_package_tests_rc": ht["rc"], "host_package_tests_pass_lines": ht["stdout"].count("[PASS]"),
            "host_controls_rc": hc["rc"], "host_controls_pass_lines": hc["stdout"].count("[PASS]"),
            "host_controls_tail": "" if hc["rc"] == 0 else (hc["stdout"] + hc["stderr"])[-600:],
            "static_controls_rc": sc["rc"], "static_controls_pass_lines": sc["stdout"].count("[PASS]"),
            "static_controls_tail": "" if sc["rc"] == 0 else (sc["stdout"] + sc["stderr"])[-600:]}


def meets_band(d) -> bool:
    lo, hi = Fraction(d[0]), Fraction(d[-1])
    lo, hi = min(lo, hi), max(lo, hi)
    return not (hi < BAND[0] or lo > BAND[1]) or not (hi < -BAND[1] or lo > -BAND[0])


def drill_rows(clone: Path, base_commit: str) -> dict:
    """the ledger rows the drill added in the clone, after the cloned commit's committed ledgers"""
    out = {}
    for rel in LEDGER_RELS:
        base = git(clone, "show", f"{base_commit}:{rel}", check=False).splitlines()
        rows = (clone / rel).read_text().splitlines() if (clone / rel).exists() else []
        if rows[:len(base)] != base[:len(rows)]:
            raise DrillError(f"the clone's ledger is not an extension of the committed one: {rel}")
        out[rel] = rows[len(base):]
    return out


# ------------------------------------------------------------------------------------------------- main
def main() -> int:
    argv = sys.argv[1:]
    tier = argv[argv.index("--tier") + 1] if "--tier" in argv else None
    if tier not in ("cloud", "worker"):
        print(__doc__)
        return 2
    scratch_root = Path(H.scratch_root(dict(os.environ), str(REPO), {"foreign_roots": []}))
    dirty = H.git_read(str(REPO), "status", "--porcelain", "--untracked-files=all", "--", NS_REL)
    if dirty is None or dirty:
        print(json.dumps({"pass": False, "refused": "the P309 namespace's working tree is not clean (A4)"}))
        return 2
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    drill_root = scratch_root / f"drill_{stamp}"
    drill_root.mkdir()                                            # exclusive
    clone, scratch = drill_root / "clone", drill_root / "scratch"
    (scratch / "tmp").mkdir(parents=True)
    rep = {"schema": "P309_R2_DRILL/1", "tier": tier, "utc_start": H.utc(), "drill_root": str(drill_root)}
    if tier == "worker":                        # the start evidence, embedded (the launch record is redacted; C9)
        rep["launch_record"] = json.loads(Path(os.environ.get("P309_LAUNCH_RECORD") or "/nonexistent").read_text()) \
            if Path(os.environ.get("P309_LAUNCH_RECORD") or "/nonexistent").is_file() else None
        rep["unit_properties"] = H.unit_properties()
    before = p309_state()
    rep["p309_before"] = before
    ok = False
    try:
        git(drill_root, "clone", "-q", "--single-branch", "--branch", BRANCH, str(REPO), str(clone))
        git(clone, "remote", "remove", "origin")
        g = guard_clone(clone, drill_root)
        rep["guard"] = g
        if not g["pass"]:
            raise DrillError(f"the drill clone failed its guard: {g['checks']}")
        rep["clone_base"] = git(clone, "rev-parse", "HEAD")
        topo = make_topology(clone, scratch)
        rep["topology"] = topo
        rep["witness_before_items"] = witness(clone, scratch, topo)
        rep["items"] = run_items(clone, scratch, tier)
        rep["witness_after_items"] = witness(clone, scratch, topo)
        rep["host"] = host_functions(clone, scratch, tier)
        rep["controls"] = controls(clone, scratch, drill_root, topo)
        rows = drill_rows(clone, rep["clone_base"])
        zt = [json.loads(l) for l in rows[LEDGER_RELS[0]] if l.strip()]
        rep["ledger"] = {"rows": rows, "sha256": {k: H.sha("\n".join(v)) for k, v in rows.items()},
                         "counters": {k: sum(int(r.get(k, 0)) for r in zt) for k in (
                             "new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")},
                         "cells_touched": sum(len(r.get("cells_touched") or []) for r in zt),
                         "band_hits": [d for r in zt for d in r.get("drifts", []) if meets_band(d)]}
        items_ok = all(v["pass"] and v["head_unchanged"] and v["confined"] for v in rep["items"].values())
        wit_ok = all(rep["witness_before_items"].values()) and all(rep["witness_after_items"].values()) and \
            "qc11_sandbox_one_record" in rep["witness_after_items"]
        ctl_ok = all((v["caught"] if isinstance(v, dict) else v) for v in rep["controls"].values())
        host_ok = all(rep["host"]["provenance_rc"][i] == 0 for i in (0, 1)) and rep["host"]["continuity_pass"] and \
            rep["host"]["preflight_as_expected"] and rep["host"]["r1_tree_unchanged"] and \
            rep["host"]["host_package_tests_rc"] == 0 and rep["host"]["host_controls_rc"] == 0 and \
            rep["host"]["static_controls_rc"] == 0
        scripts = {r.get("script", "").split(" ")[0] for r in zt}
        rep["ledger"]["completeness"] = {
            "run_start_rows": sum(1 for r in zt if " RUN START " in " " + r.get("purpose", "") + " "),
            "missing_scripts": [x for x in LEDGER_REQUIRED if x not in scripts]}
        led_ok = not any(rep["ledger"]["counters"].values()) and not rep["ledger"]["cells_touched"] and \
            not rep["ledger"]["band_hits"] and rep["ledger"]["completeness"]["run_start_rows"] == 1 and \
            not rep["ledger"]["completeness"]["missing_scripts"]
        rep["verdicts"] = {"items": items_ok, "witness": wit_ok, "controls": ctl_ok, "host": host_ok, "ledger": led_ok}
        ok = all(rep["verdicts"].values())
    except (DrillError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        rep["error"] = f"{type(exc).__name__}: {exc}"[:800]
    after = p309_state()
    rep["p309_after"] = after
    rep["p309_unchanged"] = after == before
    ok = ok and rep["p309_unchanged"]
    rep["pass"] = ok
    rep["utc_end"] = H.utc()
    rep["statement"] = "development evidence only; no target input read; no quarantined cell evaluated; " \
                       "NEW Γ309 TARGET EVALUATIONS = 0"
    out = FNS / "evidence" / "drill" / stamp
    out.mkdir(parents=True)
    rows = (rep.get("ledger") or {}).get("rows", {})
    for rel, lines in rows.items():
        (out / ("DRILL_" + Path(rel).name)).write_text("".join(l + "\n" for l in lines))
    (out / "DRILL_REPORT.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    import p309_env as E
    E.log("code/p309_topology_drill.py", f"topology drill ({tier} tier) {stamp}: {'PASS' if ok else 'FAIL'}",
          klass="GOVERNANCE", notes=f"development only; evidence/drill/{stamp}; report sha256 "
          f"{hashlib.sha256((out / 'DRILL_REPORT.json').read_bytes()).hexdigest()}")
    if "--keep" not in argv and H.under(str(drill_root), [str(scratch_root)]) and drill_root.name == f"drill_{stamp}":
        shutil.rmtree(drill_root)
    print(json.dumps({"pass": ok, "verdicts": rep.get("verdicts"), "error": rep.get("error"), "evidence": str(out)},
                     indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
