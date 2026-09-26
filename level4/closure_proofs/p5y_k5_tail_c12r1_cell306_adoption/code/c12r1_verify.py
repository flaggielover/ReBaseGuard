"""C12-R1 -- qualification verifier. It can NEVER evaluate Gamma(5, 306; S_I2) (the B1 repair, three independent barriers):

  (1) it refuses to run at all unless HEAD is the freeze commit (official mode) or the qualification-evidence commit
      directly on top of it (--review), and unless NO qualification review, grant, adjudication, execution result or
      exactly-once marker exists anywhere (tree, disk, any history, any ref) -- of this campaign or of C12;
  (2) every sandbox is built at the FREEZE commit (derived from git, never HEAD). Sandbox A (real inputs) is used only
      for baselines and input-tampering refusals and never receives a grant or review; every governance-state and
      exactly-once test runs in sandbox B, whose I2 inputs are replaced by minimal SYNTHETIC decoys (no real I2 or
      original D1/D2 value exists in its working tree), so a failed guard there could only ever evaluate a decoy;
  (3) the driver itself refuses `execute` outside the qualified worktree / git dir / common dir / branch.

Sections: P preconditions | S static | T temporal | R real read-only (incl. a real `execute` refused GRANT_MISSING)
          | A sandbox A (real inputs) | B sandbox B CLI state tests + the verifier refusing inside B
          | X exactly-once flow tests on decoy targets (in-process, identity pointed at sandbox B)
          | F function-level controls | G r6 generator | L leak scans

    python3.14 -I -S -B c12r1_verify.py --out FILE              (official: HEAD = freeze commit; writes evidence/qualification/)
    python3.14 -I -S -B c12r1_verify.py --review --out FILE     (HEAD = freeze or qualification commit; writes nothing in the repo)
"""
import argparse
import ast
import contextlib
import io
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_tail_c12r1_cell306_adoption"
DRIVER = NS / "code/c12r1_cell306.py"
R6GEN = NS / "code/c12r1_r6_from_adjudication.py"
PY = sys.executable
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": "/var/empty",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
FORBIDDEN_DIRS = ("review", "authorization", "adjudication", "evidence/execution", "evidence/coverage")
C11R_CMP = CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json"
C11RD_CMP = CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json"
C11RD_RUNS = CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/C11RD_RUNS.json"
DECOY = {"Abar": "9", "tau": "2", "C_T": "3", "D_lo": "1/2", "D1": "1", "D2": "1"}   # synthetic, valid, not real
SPARSE = [f"/{NS_REL}/", f"/{CP}p5y_k5_tail_floor_r2/",
          f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/adjudication/", f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/review/",
          f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/",
          f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/",
          f"/{CP}p5y_k5_tail_c2_closure/code/", f"/{CP}p5y_k5_tail_c2_closure/evidence/phase_d5/",
          f"/{CP}p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json",
          f"/{CP}p5y_k5_tail_c2_closure/evidence/coverage/",
          f"/{CP}p5y_k5_m5_tail_closure/code/", f"/{CP}p5y_k5_m5_tail_closure/evidence/measurement_r1/",
          f"/{CP}p5y_k5_perron_deflated_resolvent/code/", f"/{CP}p5y_k5b_consumption_adapter/code/",
          f"/{CP}p5y_k1_cover_ledger_successor/config/",
          f"/{CP}p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
          f"/{CP}p5y_k5_tail_operator_registry/evidence/registry_c1/",
          f"/{CP}p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/",
          f"/{CP}p5y_k5_tail_c11r_n9_statement_alignment/evidence/table/",
          f"/{CP}p5y_k5_tail_c11r_n9_statement_alignment/review/",
          f"/{CP}p5y_k5_lower_front_order3/code/", f"/{CP}p5y_k5_order3_readiness_audit/code/",
          f"/{CP}p5y_k5b_independent_countersignature/code/"]


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(repo, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], capture_output=True, text=True, env=dict(ENV))


def rgit(*args):
    return git(REPO, *args)


def load_driver(name: str, path: Path = DRIVER):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def expect_refusal(D, fn, code: str) -> bool:
    try:
        fn()
    except D.Refusal as e:
        return e.code == code
    return False


class Refused(Exception):
    pass


# ------------------------------------------------------------------ P: preconditions (barrier 1)
def preconditions(review: bool) -> dict:
    D = load_driver("c12r1_pre")
    fz = D.freeze_commit()
    head = rgit("rev-parse", "HEAD").stdout.strip()
    if not fz:
        raise Refused("no freeze commit")
    q_state = rgit("rev-parse", "HEAD^").stdout.strip() == fz and all(
        f.startswith(NS_REL + "/evidence/qualification/")
        for f in rgit("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.split())
    if not (head == fz or (review and q_state)):
        raise Refused("HEAD is neither the freeze commit nor (in --review) the qualification-evidence commit on it")
    for sub in FORBIDDEN_DIRS:
        rel = f"{NS_REL}/{sub}"
        if (REPO / rel).exists() or rgit("log", "--all", "--format=%H", "--", rel).stdout.strip():
            raise Refused(f"{rel} exists (tree, disk or history): a later governance state")
    for prefix in ("refs/c12r1/", "refs/c12/"):
        if rgit("for-each-ref", "--format=%(refname)", prefix).stdout.strip():
            raise Refused(f"a marker exists under {prefix}")
    try:
        D.check_not_evaluated()
    except D.Refusal as e:
        raise Refused(f"prior evaluation evidence: {e}")
    if not review and rgit("status", "--porcelain", "--untracked-files=all").stdout.strip():
        raise Refused("the official run needs a clean tree at the freeze commit")
    return {"freeze_commit": fz, "HEAD": head, "state": "freeze" if head == fz else "qualification"}


# ------------------------------------------------------------------ S: static structure of the driver
def static_checks() -> dict:
    tree = ast.parse(DRIVER.read_text())
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def names_in(fn):
        return {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    refs = {name: {f for f, fn in fns.items() if name in names_in(fn)} for name in ("evaluate_target", "prepare_target")}
    ex = fns["run_execute"]

    def first(pred):
        ls = [n.lineno for n in ast.walk(ex) if pred(n)]
        return min(ls) if ls else None

    def call(name):
        return lambda n: isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
    order = [first(call(c)) for c in ("check_identity", "check_not_evaluated", "check_clean", "check_grant",
                                      "check_bindings", "check_governance_state", "check_seal_preconditions",
                                      "load_consumer", "control")]
    order += [first(lambda n: isinstance(n, ast.Constant) and n.value == "CONTROL_FAILED"),
              first(call("prepare")), first(lambda n: isinstance(n, ast.Name) and n.id == "CONSUMED_REF"),
              first(call("evaluator"))]
    so = fns["run_seal_only"]
    so_calls = [n.func.id for n in ast.walk(so) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    main_calls = [n for n in ast.walk(fns["main"]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                  and n.func.id == "run_execute"]
    printed = {ast.unparse(v.value) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "print" for v in ast.walk(n) if isinstance(v, ast.FormattedValue)}
    handlers = [h for n in ast.walk(ex) if isinstance(n, ast.Try) for h in n.handlers]
    return {
        "evaluate_target / prepare_target are referenced only by run_execute":
            refs["evaluate_target"] == {"run_execute"} and refs["prepare_target"] == {"run_execute"},
        "run_execute order: identity < not-evaluated < clean < grant < bindings < state < seal preconditions < "
        "consumer < control < CONTROL_FAILED exit < prepare < marker < evaluation":
            None not in order and order == sorted(order) and len(set(order)) == len(order),
        "seal-only checks identity first and never computes": so_calls[:1] == ["check_identity"]
            and not {"evaluate_target", "prepare_target", "control", "evaluate", "load_consumer"} & set(so_calls),
        "the CLI calls run_execute(own_sha) with no injection": len(main_calls) == 1 and len(main_calls[0].args) == 1
            and not main_calls[0].keywords,
        "after the marker every exception is recorded (except BaseException)":
            any(isinstance(h.type, ast.Name) and h.type.id == "BaseException" for h in handlers),
        "no print of a computed value": printed <= {"a.cell", "cid", "e", "status", "ctl['reproduces_C2_exactly']"},
        "no numpy/flint import": not ({"numpy", "flint"} & {a.name.split(".")[0] for n in ast.walk(tree)
                                                               if isinstance(n, ast.Import) for a in n.names}),
    }


# ------------------------------------------------------------------ R: real repository, read-only
def run_cli(repo: Path, script: str, *argv, out: Path = None, home="/var/empty") -> tuple:
    cmd = [PY, "-I", "-S", "-B", str(repo / NS_REL / "code" / script), *argv]
    if out is not None:
        cmd += ["--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": home})
    return p.returncode, (p.stdout + p.stderr)[-400:]


def real_runs(qdir: Path) -> dict:
    out = {}
    code, text = run_cli(REPO, "c12r1_cell306.py", "execute", home=os.environ.get("HOME", "/var/empty"))
    out["execute_in_the_real_worktree"] = {"exit": code, "out": text}
    for name, argv in (("preflight", ("preflight",)), ("rehearse_306", ("rehearse", "--cell", "306")),
                       ("rehearse_305", ("rehearse", "--cell", "305"))):
        f = qdir / f"{name.upper()}.json"
        code, text = run_cli(REPO, "c12r1_cell306.py", *argv, out=f)
        rec = json.loads(f.read_text()) if f.exists() else {}
        out[name] = {"exit": code, "out": text, "reproduces_C2_exactly": rec.get("control", {}).get("reproduces_C2_exactly"),
                     "field_matches": rec.get("control", {}).get("field_matches")}
    marker = rgit("for-each-ref", "refs/c12r1").stdout.strip()
    out["checks"] = {
        "a real execute at this state refuses GRANT_MISSING (identity, no-prior-evaluation and clean tree pass first)":
            out["execute_in_the_real_worktree"]["exit"] == 2 and "REFUSED GRANT_MISSING" in out["execute_in_the_real_worktree"]["out"],
        "preflight PASS": out["preflight"]["exit"] == 0 and "PREFLIGHT PASS" in out["preflight"]["out"],
        "I1 control reproduces C2 exactly for 306, including C2's per-supply records (N2)":
            out["rehearse_306"]["exit"] == 0 and out["rehearse_306"]["reproduces_C2_exactly"] is True
            and (out["rehearse_306"]["field_matches"] or {}).get("per_supply_records_G_C1_C2") is True,
        "I1 control reproduces C2 exactly for the non-target 305": out["rehearse_305"]["exit"] == 0
            and out["rehearse_305"]["reproduces_C2_exactly"] is True,
        "no marker was created in the real repository": marker == "",
        "no result exists in the real repository": not (REPO / f"{NS_REL}/evidence/execution").exists(),
    }
    return out


# ------------------------------------------------------------------ sandboxes (barrier 2)
class Sandbox:
    def __init__(self, root: Path, name: str, commit: str):
        self.root = (root / name).resolve()
        assert REPO.resolve() not in self.root.parents and self.root != REPO.resolve()
        for step in (git(root, "clone", "-q", "--shared", "--no-checkout", str(REPO), str(self.root)),
                     self.g("sparse-checkout", "init", "--no-cone"),
                     self.g("sparse-checkout", "set", "--no-cone", *SPARSE),
                     self.g("checkout", "-q", "-B", "campaign", commit)):
            if step.returncode:
                raise SystemExit(f"sandbox setup failed: {step.stderr[:300]}")
        self.base = commit

    def g(self, *args):
        assert self.root != REPO.resolve()
        return git(self.root, "-c", "user.name=c12r1-sandbox", "-c", "user.email=sandbox@invalid", *args)

    def p(self, rel: str) -> Path:
        return self.root / rel

    def head(self) -> str:
        return self.g("rev-parse", "HEAD").stdout.strip()

    def commit_all(self, msg: str) -> str:
        self.g("add", "-A", "--sparse", ".")
        self.g("commit", "-q", "--no-verify", "-m", msg)
        return self.head()

    def reset(self):
        self.g("checkout", "-q", "-f", "-B", "campaign", self.base)
        self.g("reset", "-q", "--hard", self.base)
        self.g("clean", "-qfdx")
        for ref in self.g("for-each-ref", "--format=%(refname)", "refs/c12r1", "refs/c12").stdout.split():
            self.g("update-ref", "-d", ref)
        for lock in (self.root / ".git/index.lock",):
            if lock.exists():
                lock.unlink()


def make_decoy_sandbox(root: Path, freeze: str) -> tuple:
    """Sandbox B: the freeze commit plus ONE sandbox commit replacing the three I2 inputs by minimal synthetic decoys
    (and marking protocol/, so that the sandbox's own freeze commit is this decoy commit)."""
    sb = Sandbox(root, "sbB", freeze)
    stmt = {"STATUS": "EQUIVALENT", "domain": "EQUAL", "premises": "SAME"}
    c11r = {"DECOY": True, "result": {"independence_violations": [], "per_target": {
        x: {"target_status": "CERTIFIED", "direction": d, "CLASS": "AGREES", "statement": dict(stmt),
            "independent_value": DECOY[x], "original_value": DECOY[x]}
        for x, d in (("C_T", "UPPER_BOUND"), ("tau", "UPPER_BOUND"), ("Abar", "UPPER_BOUND"), ("D_lo", "LOWER_BOUND"))}}}
    c11rd = {"DECOY": True, "N9_VERDICT": "N9_CLOSED", "independence_violations": [], "per_target": {
        x: {"direction": "UPPER_BOUND", "CLASS": "STRONGER", "statement": dict(stmt), "independent_value": DECOY[x],
            "original_value": DECOY[x]} for x in ("D1", "D2")}}
    runs = {"DECOY": True, "cell": 306, "targets": {x: {"value": DECOY[x]} for x in ("D1", "D2")}}
    for rel, obj in ((C11R_CMP, c11r), (C11RD_CMP, c11rd), (C11RD_RUNS, runs)):
        sb.p(rel).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    sb.p(f"{NS_REL}/protocol").mkdir(parents=True, exist_ok=True)
    sb.p(f"{NS_REL}/protocol/SANDBOX_DECOY.md").write_text("sandbox-only decoy freeze; not part of the campaign\n")
    sb.base = sb.commit_all("sandbox decoy freeze: synthetic I2 inputs")
    pins = {k: (rel, sha_b(sb.p(rel).read_bytes())) for k, rel in
            (("c11r_comparison", C11R_CMP), ("c11rd_comparison", C11RD_CMP), ("c11rd_runs", C11RD_RUNS))}
    blobs = {k: sb.g("rev-parse", f"HEAD:{rel}").stdout.strip()[:12] for k, (rel, _) in pins.items()}
    return sb, pins, blobs


def build_state(sb: Sandbox, upto: str, drv_sha: str, grant_patch: dict = None, review_line: str = "QUALIFICATION_ACCEPTED"):
    """Synthetic governance chain on sandbox B: Q (qualification evidence) -> R (review) -> G (grant)."""
    D = sys.modules["c12r1_pre"]
    fz = sb.head()
    q = sb.p(D.QUAL_REL)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps({"pass": True, "dry_run": False, "freeze_commit": fz, "SYNTHETIC": True}))
    qc = sb.commit_all("sandbox synthetic qualification")
    if upto == "Q":
        return
    r = sb.p(D.QREVIEW_REL)
    r.parent.mkdir(parents=True, exist_ok=True)
    r.write_text(f"# synthetic\n{review_line}\n")
    rc = sb.commit_all("sandbox synthetic review")
    if upto == "R":
        return
    g = {"schema": "rebaseguard.p5y.k5.tail-c12r1.grant.v1", "exactly_once": True, "driver_sha256": drv_sha,
         "freeze_commit": fz, "qualification_commit": qc, "qualification_review_commit": rc, "SYNTHETIC": True}
    g.update(grant_patch or {})
    gp = sb.p(D.GRANT_REL)
    gp.parent.mkdir(parents=True, exist_ok=True)
    gp.write_text(json.dumps(g))
    sb.commit_all("sandbox synthetic grant")


def sandbox_a_controls(sbA: Sandbox) -> dict:
    res = {}

    def snapshot():
        d = sbA.p(f"{NS_REL}/evidence/execution")
        return {str(f): f.read_bytes() for f in sorted(d.rglob("*")) if f.is_file()} if d.exists() else {}

    def run(name, setup, argv, want_exit, want_code):
        sbA.reset()
        if setup:
            setup()
        before = snapshot()
        code, text = run_cli(sbA.root, "c12r1_cell306.py", *argv)
        res[name] = {"argv": list(argv), "exit": code, "out": text[-240:],
                     "pass": code == want_exit and (want_code is None or f"REFUSED {want_code}" in text)
                     and snapshot() == before}

    reg1 = CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json"
    reg2 = CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"
    D = sys.modules["c12r1_pre"]

    def blob_swap():
        good = sbA.p(reg1).read_bytes()
        sbA.p(reg1).write_bytes(good + b"\n")
        sbA.commit_all("sandbox altered registry")
        sbA.p(reg1).write_bytes(good)

    def statement_file():
        d = json.loads(sbA.p(C11R_CMP).read_text())
        d["result"]["per_target"]["C_T"]["statement"]["STATUS"] = "WEAKER"
        sbA.p(C11R_CMP).write_text(json.dumps(d))

    def plant(rel, history=False):
        def f():
            sbA.p(rel).parent.mkdir(parents=True, exist_ok=True)
            sbA.p(rel).write_text("{}")
            if history:
                sbA.commit_all("sandbox premature result")
                sbA.g("rm", "-q", rel)
                sbA.commit_all("sandbox remove result")
        return f

    run("A00 freeze-commit sandbox: preflight PASS (not vacuous)", None, ("preflight",), 0, None)
    run("A00b freeze-commit sandbox: the I1 control rehearsal PASS", None, ("rehearse", "--cell", "306"), 0, None)
    run("A01 altered input", lambda: sbA.p(CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json")
        .write_bytes(sbA.p(CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes() + b" "),
        ("preflight",), 2, "PIN_MISMATCH")
    for c in (307, 308, 309):
        run(f"A02 wrong cell {c} (rehearse)", None, ("rehearse", "--cell", str(c)), 2, "CELL_OUT_OF_SCOPE")
    run("A02b a cell passed to execute", None, ("execute", "--cell", "307"), 2, "CELL_OUT_OF_SCOPE")
    run("A03 wrong bytes (REGISTRY_C1 := REGISTRY_C2)", lambda: sbA.p(reg1).write_bytes(sbA.p(reg2).read_bytes()),
        ("preflight",), 2, "PIN_MISMATCH")
    run("A03b wrong blob at HEAD, pinned bytes on disk", blob_swap, ("preflight",), 2, "BLOB_MISMATCH")
    run("A04 wrong statement file", statement_file, ("preflight",), 2, "PIN_MISMATCH")
    run("A05 missing review (floor r2)", lambda: sbA.p(CP + "p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md").unlink(),
        ("preflight",), 2, "INPUT_MISSING")
    run("A05b missing review (N9 adjudication review)",
        lambda: sbA.p(CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md").unlink(),
        ("preflight",), 2, "INPUT_MISSING")
    run("A07 planted result (working tree)", plant(D.RESULT_REL), ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("A07b planted result (history)", plant(D.RESULT_REL, True), ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("A07c planted predecessor C12 result", plant(D.PRIOR_RESULTS[1]), ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("A07d planted marker (refs/c12r1)", lambda: sbA.g("update-ref", D.CONSUMED_REF, "HEAD"),
        ("rehearse", "--cell", "306"), 2, "CONSUMED")
    run("A07e planted predecessor marker (refs/c12)", lambda: sbA.g("update-ref", "refs/c12/cell306-target-consumed", "HEAD"),
        ("preflight",), 2, "CONSUMED")
    run("A12 an r6 file in the working tree", plant(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R6.json"),
        ("preflight",), 2, "R6_EXISTS")
    run("A20 freeze-commit sandbox (real inputs) cannot execute: identity refused first", None, ("execute",), 2,
        "REPO_NOT_QUALIFIED")
    sbA.reset()
    return res


def sandbox_b_cli(sbB: Sandbox, drv_sha: str, tmp: Path) -> dict:
    """Governance-state sandboxes through the REAL CLI: all must refuse, write no result and create no marker."""
    res = {}
    D = sys.modules["c12r1_pre"]

    def check(name, argv=("execute",), repo=None, script="c12r1_cell306.py", want="REFUSED REPO_NOT_QUALIFIED", exit_=2):
        r = repo or sbB.root
        before = git(r, "for-each-ref", "refs/c12r1").stdout
        code, text = run_cli(r, script, *argv, home=os.environ.get("HOME", "/var/empty"))
        after = git(r, "for-each-ref", "refs/c12r1").stdout
        res[name] = {"exit": code, "out": text[-240:],
                     "pass": code == exit_ and want in text and not (r / D.RESULT_REL).exists() and before == after}

    sbB.reset(); build_state(sbB, "Q", drv_sha)
    check("B01 qualification-commit sandbox cannot target-evaluate")
    sbB.reset(); build_state(sbB, "R", drv_sha)
    check("B02 accepted-review-state sandbox cannot target-evaluate")
    check("B02v the verifier refuses to run in an accepted-review state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r1_verify.py", want="VERIFY REFUSED")
    sbB.reset(); build_state(sbB, "G", drv_sha)
    check("B03 grant-state sandbox cannot target-evaluate")
    check("B03s grant-state sandbox cannot seal-only", argv=("seal-only",))
    check("B03v the verifier refuses to run in a grant state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r1_verify.py", want="VERIFY REFUSED")
    cp = tmp / "copied_repository"
    shutil.copytree(sbB.root, cp, symlinks=True)
    check("B05 a copied repository (grant state) cannot target-evaluate", repo=cp)
    shutil.rmtree(cp, ignore_errors=True)
    sbB.g("update-ref", D.CONSUMED_REF, "HEAD")
    check("B04 consumed-state sandbox cannot target-evaluate")
    check("B04v the verifier refuses to run in a consumed state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r1_verify.py", want="VERIFY REFUSED")
    sbB.reset(); build_state(sbB, "G", drv_sha)
    sbB.p(D.RESULT_REL).parent.mkdir(parents=True, exist_ok=True)
    sbB.p(D.RESULT_REL).write_text("{}")
    code, text = run_cli(sbB.root, "c12r1_verify.py", "--review", "--out", str(tmp / "v.json"))
    res["B06v the verifier refuses to run with a planted result"] = {"exit": code, "out": text[-240:],
                                                                     "pass": code == 2 and "VERIFY REFUSED" in text}
    # barrier 1 at the freeze state itself (HEAD = the sandbox's freeze commit): planted review / marker / result
    for label, plant in (("B07v planted qualification review file", lambda: (sbB.p(D.QREVIEW_REL).parent.mkdir(parents=True, exist_ok=True),
                                                                           sbB.p(D.QREVIEW_REL).write_text("# x\nQUALIFICATION_ACCEPTED\n"))),
                         ("B08v planted exactly-once marker", lambda: sbB.g("update-ref", D.CONSUMED_REF, "HEAD")),
                         ("B09v planted predecessor C12 result", lambda: (sbB.p(D.PRIOR_RESULTS[1]).parent.mkdir(parents=True, exist_ok=True),
                                                                          sbB.p(D.PRIOR_RESULTS[1]).write_text("{}")))):
        sbB.reset()
        plant()
        code, text = run_cli(sbB.root, "c12r1_verify.py", "--review", "--out", str(tmp / "v.json"))
        res[f"{label}: the verifier refuses at the freeze state"] = {"exit": code, "out": text[-240:],
                                                                     "pass": code == 2 and "VERIFY REFUSED" in text}
    sbB.reset()
    return res


# ------------------------------------------------------------------ X: exactly-once flows on DECOY targets
def flow_tests(sbB: Sandbox, pins: dict, blobs: dict, drv_sha: str) -> dict:
    res = {}
    decoy_base = sbB.base

    def fresh(upto="G", **kw):
        sbB.reset()
        if upto:
            build_state(sbB, upto, drv_sha, **kw)
        D = load_driver(f"c12r1_flow_{len(res)}")
        D.REPO = sbB.root
        D.QUALIFIED_WORKTREE = str(sbB.root)
        D.QUALIFIED_GIT_DIR = str((sbB.root / ".git").resolve())
        D.QUALIFIED_COMMON_DIR = str((sbB.root / ".git").resolve())
        D.QUALIFIED_BRANCH = "refs/heads/campaign"
        D.PINS = {**D.PINS, **pins}
        D.BLOBS = {**D.BLOBS, **blobs}
        calls = {"control": 0, "prepare": 0, "evaluate": 0}
        orig_control, orig_prep, orig_eval = D.control, D.prepare_target, D.evaluate_target

        def ctl(*a, **k):
            calls["control"] += 1
            return orig_control(*a, **k)

        def prep(con):
            calls["prepare"] += 1
            return orig_prep(con)

        def ev(con, p):
            calls["evaluate"] += 1
            return orig_eval(con, p)
        D.control = ctl
        return D, calls, prep, ev

    def marker():
        return bool(sbB.g("for-each-ref", "refs/c12r1").stdout.strip())

    def refused(D, fn, code):
        try:
            fn()
        except D.Refusal as e:
            return e.code == code
        return False

    # X01 wrong worktree, X02 wrong branch
    D, calls, prep, ev = fresh()
    D.QUALIFIED_WORKTREE = "/nonexistent/qualified/worktree"
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "REPO_NOT_QUALIFIED")
    res["X01 wrong worktree cannot consume"] = ok and not marker() and calls == {"control": 0, "prepare": 0, "evaluate": 0}
    D, calls, prep, ev = fresh()
    sbB.g("checkout", "-q", "--detach")
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "WRONG_BRANCH")
    res["X02 wrong branch (detached) cannot consume"] = ok and not marker() and calls["evaluate"] == 0
    D, calls, prep, ev = fresh()
    sbB.g("checkout", "-q", "-b", "other")
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "WRONG_BRANCH")
    res["X02b wrong branch (another branch) cannot consume"] = ok and not marker() and calls["evaluate"] == 0
    # X03 copied repository: identity names the sandbox, the process runs in a copy
    D, calls, prep, ev = fresh()
    cp = sbB.root.parent / "copy_for_X03"
    shutil.copytree(sbB.root, cp, symlinks=True)
    D.REPO = cp
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "REPO_NOT_QUALIFIED")
    res["X03 a copy of the qualified repository cannot consume"] = ok and calls["evaluate"] == 0 and \
        not git(cp, "for-each-ref", "refs/c12r1").stdout.strip()
    shutil.rmtree(cp, ignore_errors=True)
    # X04 states before the grant
    for st in ("Q", "R"):
        D, calls, prep, ev = fresh(st)
        ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_MISSING")
        res[f"X04 {st}-state cannot consume (GRANT_MISSING)"] = ok and not marker() and calls["evaluate"] == 0
    # X05 full DECOY execution at a grant state: the pipeline works, exactly once, on synthetic I2 values only
    D, calls, prep, ev = fresh()
    code = D.run_execute(drv_sha, prep, ev)
    rel = D.RESULT_REL
    in_head = rel in sbB.g("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    r = json.loads(sbB.p(rel).read_text()) if sbB.p(rel).exists() else {}
    decoy_bound = r.get("input_sha256", {}).get("c11r_comparison") == pins["c11r_comparison"][1]
    res["X05 grant-state DECOY run: one evaluation, sealed, on decoy I2 inputs only"] = code == 0 and in_head and marker() \
        and r.get("status") == "TARGET_EVALUATED" and r.get("target_evaluations") == 1 and decoy_bound \
        and r["control"]["reproduces_C2_exactly"] and calls == {"control": 1, "prepare": 1, "evaluate": 1}
    # X06 a second execute after the sealed run
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")
    res["X06 a second execute after a sealed run is refused before anything"] = ok and calls["evaluate"] == 1 \
        and calls["control"] == 1
    # X07 planted result (working tree, then history)
    D, calls, prep, ev = fresh()
    sbB.p(D.RESULT_REL).parent.mkdir(parents=True, exist_ok=True)
    sbB.p(D.RESULT_REL).write_text("{}")
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "TARGET_ARTIFACT_EXISTS")
    res["X07 a planted result cannot cause an evaluation"] = ok and not marker() and calls["evaluate"] == 0
    D, calls, prep, ev = fresh()
    sbB.p(D.PRIOR_RESULTS[1]).parent.mkdir(parents=True, exist_ok=True)
    sbB.p(D.PRIOR_RESULTS[1]).write_text("{}")
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "TARGET_ARTIFACT_EXISTS")
    res["X07b a planted predecessor (C12) result cannot cause an evaluation"] = ok and calls["evaluate"] == 0
    # X08 consumed state
    D, calls, prep, ev = fresh()
    sbB.g("update-ref", D.CONSUMED_REF, "HEAD")
    ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")
    res["X08 consumed state: refused before control, prepare or evaluation"] = ok and \
        calls == {"control": 0, "prepare": 0, "evaluate": 0}
    # X09 seal failure: exactly one evaluation, never a second; seal-only completes without computing
    D, calls, prep, ev = fresh()

    def failing_seal(msg):
        raise D.Refusal("UNSEALED", "injected seal failure")
    code = D.run_execute(drv_sha, prep, ev, failing_seal)
    written = sbB.p(D.RESULT_REL).exists()
    ok2 = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")
    so = D.run_seal_only()
    sealed = D.RESULT_REL in sbB.g("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    so2 = D.run_seal_only()
    res["X09 seal failure: UNSEALED, no second evaluation, seal-only seals without computing"] = code == 4 and written \
        and marker() and ok2 and so == 0 and sealed and so2 == 0 and calls["evaluate"] == 1
    # X10 a failure after consumption (SystemExit, as C2's crosscheck raises) is recorded and sealed
    D, calls, prep, ev = fresh()

    def exploding(con, p):
        calls["evaluate"] += 1
        raise SystemExit("injected crosscheck failure")
    code = D.run_execute(drv_sha, prep, exploding)
    r = json.loads(sbB.p(D.RESULT_REL).read_text()) if sbB.p(D.RESULT_REL).exists() else {}
    ok2 = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")
    res["X10 SystemExit after consumption is sealed as TARGET_EVALUATION_FAILED; never rerun"] = code == 5 and \
        r.get("status") == "TARGET_EVALUATION_FAILED" and D.RESULT_REL in sbB.g("ls-tree", "-r", "--name-only", "HEAD").stdout \
        and ok2 and calls["evaluate"] == 1
    # X11 control mismatch at a grant state: CONTROL_FAILED sealed, no marker, the target never touched
    D, calls, prep, ev = fresh()
    fc_rel = D.PINS["c2_forecast"][0]
    fc = json.loads(sbB.p(fc_rel).read_text())
    fc["cells"]["306"]["Gamma_exact"] += "1"
    sbB.reset()
    sbB.p(fc_rel).write_text(json.dumps(fc))
    marker_file = sbB.p(f"{NS_REL}/protocol/SANDBOX_DECOY.md")
    marker_file.write_text(marker_file.read_text() + "perturbed control artifact (X11)\n")
    sbB.base = sbB.commit_all("sandbox perturbed control artifact")
    build_state(sbB, "G", drv_sha)
    D.PINS = {**D.PINS, "c2_forecast": (fc_rel, sha_b(sbB.p(fc_rel).read_bytes()))}
    D.BLOBS = {**D.BLOBS, "c2_forecast": sbB.g("rev-parse", f"HEAD:{fc_rel}").stdout.strip()[:12]}
    code = D.run_execute(drv_sha, prep, ev)
    r = json.loads(sbB.p(D.RESULT_REL).read_text()) if sbB.p(D.RESULT_REL).exists() else {}
    res["X11 control mismatch: CONTROL_FAILED sealed, no marker, no I2 preparation or evaluation"] = code == 3 and \
        r.get("status") == "CONTROL_FAILED" and not marker() and calls["prepare"] == 0 and calls["evaluate"] == 0
    sbB.base = decoy_base                                            # back to the decoy freeze
    # X12 grant variants
    variants = [("schema", {"schema": "wrong"}, "GRANT_INVALID"), ("exactly_once false", {"exactly_once": False}, "GRANT_INVALID"),
                ("driver sha", {"driver_sha256": "0" * 64}, "GRANT_INVALID"),
                ("freeze commit named wrong", {"freeze_commit": "0" * 40}, "GRANT_INVALID")]
    for label, patch, code_ in variants:
        D, calls, prep, ev = fresh("G", grant_patch=patch)
        res[f"X12 grant variant refused: {label}"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), code_) \
            and not marker() and calls["evaluate"] == 0
    D, calls, prep, ev = fresh("G", review_line="QUALIFICATION_REJECTED")
    res["X12b a REJECTED review cannot be granted"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "REVIEW_VERDICT") \
        and calls["evaluate"] == 0
    D, calls, prep, ev = fresh("G")
    sbB.p(D.GRANT_REL).write_text(sbB.p(D.GRANT_REL).read_text())
    sbB.p(f"{NS_REL}/authorization/EXTRA").write_text("x")
    sbB.g("add", "-A", "--sparse", ".")
    sbB.g("commit", "-q", "--amend", "--no-edit")
    res["X12c a grant commit carrying another file is refused"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_INVALID") \
        and calls["evaluate"] == 0
    D, calls, prep, ev = fresh("G")
    sbB.p(f"{NS_REL}/NOTE").write_text("x")
    sbB.commit_all("sandbox commit after the grant")
    res["X12d HEAD not the grant commit is refused"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_INVALID") \
        and calls["evaluate"] == 0
    # X13 dirty tree, git lock, unwritable result directory: all before the marker
    D, calls, prep, ev = fresh()
    sbB.p(f"{NS_REL}/UNTRACKED").write_text("x")
    res["X13 dirty tree refused before the marker"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "DIRTY_TREE") \
        and not marker()
    D, calls, prep, ev = fresh()
    (sbB.root / ".git/index.lock").write_text("")
    res["X13b a git lock is refused before the marker"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GIT_LOCKED") \
        and not marker()
    (sbB.root / ".git/index.lock").unlink()
    D, calls, prep, ev = fresh()
    ev_dir = sbB.p(f"{NS_REL}/evidence")
    ev_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(ev_dir, stat.S_IRUSR | stat.S_IXUSR)
    try:
        ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "SEAL_PRECONDITION")
    finally:
        os.chmod(ev_dir, stat.S_IRWXU)
    res["X13c an unwritable result directory is refused before the marker"] = ok and not marker() and calls["evaluate"] == 0
    sbB.reset()
    return res


# ------------------------------------------------------------------ F: function-level controls (real repo, no Gamma under I2)
def function_controls() -> dict:
    D = load_driver("c12r1_fn")
    con = D.load_consumer()
    res = {}
    G = {"A0": F(3), "A1": F(3), "A2": F(3)}
    syn = {k: F(v) for k, v in DECOY.items()}
    s_i1 = {"impl": "I1", "name": "C1", "values": dict(syn)}
    s_i2 = {"impl": "I2", "name": "I2", "values": dict(syn)}
    res["F01 mixed supply I1 + I2 refused"] = expect_refusal(D, lambda: D.supply(con, "I1", [s_i1, s_i2], G), "MIXED_SUPPLY")
    res["F01b I1-tagged set in an I2 supply refused"] = expect_refusal(D, lambda: D.supply(con, "I2", [s_i1], G), "MIXED_SUPPLY")
    res["F01c duplicate set name refused"] = expect_refusal(D, lambda: D.supply(con, "I1", [s_i1, dict(s_i1)], G), "MIXED_SUPPLY")
    for label, patch in (("tau < 1", {"tau": F(1, 2)}), ("C < tau", {"C_T": F(1)}), ("D_lo <= 0", {"D_lo": F(0)}),
                         ("Abar < 1", {"Abar": F(1, 2)}), ("non-exact value", {"D1": 1.0})):
        s = {"impl": "I1", "name": "X", "values": {**syn, **patch}}
        res[f"F02 consumer validation refuses {label}"] = expect_refusal(D, lambda s=s: D.validate_set(s), "VALIDATION")
    c11r = json.loads(D.read_pinned("c11r_comparison"))
    c11rd = json.loads(D.read_pinned("c11rd_comparison"))
    runs = json.loads(D.read_pinned("c11rd_runs"))

    def mut(obj, path, value):
        o = copy.deepcopy(obj)
        cur = o
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value
        return o
    cases = [
        ("F03 C11R class INSUFFICIENT", (mut(c11r, ["result", "per_target", "C_T", "CLASS"], "INSUFFICIENT"), c11rd, runs), "I2_CLASS"),
        ("F03b C11R statement WEAKER", (mut(c11r, ["result", "per_target", "tau", "statement", "STATUS"], "WEAKER"), c11rd, runs), "I2_STATEMENT"),
        ("F03c C11R domain SUBSET", (mut(c11r, ["result", "per_target", "Abar", "statement", "domain"], "SUBSET"), c11rd, runs), "I2_STATEMENT"),
        ("F03d C11R target not certified", (mut(c11r, ["result", "per_target", "D_lo", "target_status"], "NOT_IMPLEMENTED"), c11rd, runs), "I2_STATUS"),
        ("F03e C11R D_lo direction flipped", (mut(c11r, ["result", "per_target", "D_lo", "direction"], "UPPER_BOUND"), c11rd, runs), "I2_STATUS"),
        ("F03f C11RD N9 verdict not CLOSED", (c11r, mut(c11rd, ["N9_VERDICT"], "N9_REMAINS_OPEN"), runs), "I2_STATUS"),
        ("F03g C11RD class INSUFFICIENT", (c11r, mut(c11rd, ["per_target", "D2", "CLASS"], "INSUFFICIENT"), runs), "I2_CLASS"),
        ("F03h C11RD statement WEAKER", (c11r, mut(c11rd, ["per_target", "D1", "statement", "STATUS"], "WEAKER"), runs), "I2_STATEMENT"),
        ("F03i C11RD value not the sealed run's", (c11r, mut(c11rd, ["per_target", "D1", "independent_value"], "1"), runs), "I2_BINDING"),
        ("F03j C11RD runs for another cell", (c11r, c11rd, mut(runs, ["cell"], 307)), "I2_BINDING"),
        ("F03k independence violation recorded (N8)", (mut(c11r, ["result", "independence_violations"], ["x"]), c11rd, runs), "I2_INDEPENDENCE"),
    ]
    for label, (a, b, c), code in cases:
        res[label] = expect_refusal(D, lambda a=a, b=b, c=c: D.i2_set(a, b, c), code)
    st = json.loads(D.read_pinned("c11r_statements"))
    cov = con["cover"][306]
    res["F04 I2 domain for cell 307 refused"] = expect_refusal(D, lambda: D.i2_block_check(mut(st, ["drift_domain", "cell"], 307), cov, con["KM"]), "I2_DOMAIN")
    res["F04b I2 domain endpoint altered refused"] = expect_refusal(D, lambda: D.i2_block_check(mut(st, ["drift_domain", "e_hi"], "1789/1000"), cov, con["KM"]), "I2_DOMAIN")
    res["F04c I2 domain equals cell 306's cover cell (positive)"] = D.i2_block_check(st, cov, con["KM"]) is None
    fc = json.loads(D.read_pinned("c2_forecast"))
    w = copy.deepcopy(fc["cells"]["306"])
    w["Gamma_exact"] += "1"
    res["F05 control mismatch detected (perturbed expected cell record)"] = D.control(con, 306, want_cell=w)["reproduces_C2_exactly"] is False
    ws = copy.deepcopy(fc["supplies"]["306"])
    ws["G"]["A0"] = ws["G"]["A0"] * 2
    res["F05b control mismatch detected (perturbed Lemma-G supply record, N2)"] = D.control(con, 306, want_supplies=ws)["reproduces_C2_exactly"] is False
    res["F06 cell 307 refused by cell_inputs"] = expect_refusal(D, lambda: D.cell_inputs(con, 307), "CELL_OUT_OF_SCOPE")
    res["F06b cell 309 refused by cell_inputs"] = expect_refusal(D, lambda: D.cell_inputs(con, 309), "CELL_OUT_OF_SCOPE")
    res["F07 verdict line: a second verdict line is refused"] = not D.verdict_ok("# t\nX_ACCEPTED\nX_ACCEPTED\n", "line2", "X_ACCEPTED")
    res["F07b verdict line: wrong line 2 is refused"] = not D.verdict_ok("# t\nX_REJECTED\n", "line2", "X_ACCEPTED")
    res["F07c verdict line: the right line 2 is accepted (positive)"] = D.verdict_ok("# t\nX_ACCEPTED\n", "line2", "X_ACCEPTED")
    return res


# ------------------------------------------------------------------ G: the r6 generator (synthetic chain in sandbox B)
def r6_controls(sbB: Sandbox, tmp: Path) -> dict:
    res = {}
    out = tmp / "K5_COVERAGE_MAP_R6.json"
    p = subprocess.run([PY, "-I", "-S", "-B", str(R6GEN), "--out", str(out)], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"})
    res["G01 refuses in the real repository"] = p.returncode != 0 and "REFUSED" in (p.stdout + p.stderr) and not out.exists()
    D = sys.modules["c12r1_pre"]
    gen = sbB.p(NS_REL) / "code/c12r1_r6_from_adjudication.py"
    exec_rev, adj, adj_rev = (f"{NS_REL}/review/C12R1_EXECUTION_REVIEW.md", f"{NS_REL}/adjudication/C12R1_ADOPTION_ADJUDICATION.md",
                              f"{NS_REL}/review/C12R1_ADJUDICATION_REVIEW.md")
    target_out = sbB.p(f"{NS_REL}/evidence/coverage/K5_COVERAGE_MAP_R6.json")

    def chain(adj_line="CELL306_ADOPTED", adj_set="[306]", s_i2=True, with_adj_rev=True, with_exec_rev=True,
              bad_hash=False, marker=True, after=None, out_path=None):
        sbB.reset()
        body = {"status": "TARGET_EVALUATED", "target_evaluations": 1, "SYNTHETIC": True,
                "control": {"reproduces_C2_exactly": True, "evaluated": {"pass": True}},
                "target": {"evaluated": {"pass": s_i2}}}
        body["sha256"] = "0" * 64 if bad_hash else sha_b(json.dumps(body, sort_keys=True).encode())
        for rel, text in ((D.RESULT_REL, json.dumps(body)),
                          (exec_rev, "# synthetic\nEXECUTION_ACCEPTED\n" if with_exec_rev else None),
                          (adj, f"# synthetic\n{adj_line}\n\n## ADOPTED CELL SET\n\n{adj_set}\n"),
                          (adj_rev, "# synthetic\nADJUDICATION_ACCEPTED\n" if with_adj_rev else None)):
            if text is not None:
                sbB.p(rel).parent.mkdir(parents=True, exist_ok=True)
                sbB.p(rel).write_text(text)
        sbB.commit_all("sandbox synthetic chain")
        if marker:
            sbB.g("update-ref", D.CONSUMED_REF, "HEAD")
        if after:
            after()
        o = Path(out_path) if out_path else target_out
        q = subprocess.run([PY, "-I", "-S", "-B", str(gen), "--out", str(o)], capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"})
        return q, o

    q, o = chain()
    ok = q.returncode == 0 and o.exists()
    if ok:
        r6 = json.loads(o.read_text())
        r5 = json.loads(sbB.p(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json").read_text())
        a5 = {c["cell"]: c["verdict"] for c in r5["per_m"]["5"]["cells"]}
        b5 = {c["cell"]: c["verdict"] for c in r6["per_m"]["5"]["cells"]}
        ok = sorted(k for k in a5 if a5[k] != b5[k]) == [306] and b5[306] == "PASS" and \
            all(r5["per_m"][m]["cells"] == r6["per_m"][m]["cells"] for m in r5["per_m"] if m != "5") and \
            r6["union_open_ranges"] == [[307, 309]] and r6["K5_COVERAGE_COMPLETE"] is False and r6["inputs"]["predecessor"] == "r5"
    res["G02 synthetic chain: r6 moves exactly (5, 306), keeps 307-309 open, records r5 lineage"] = ok
    r5_path = sbB.p(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json")
    for label, kw in (("G03 CELL306_NOT_ADOPTED", {"adj_line": "CELL306_NOT_ADOPTED"}),
                      ("G04 adopted set other than [306]", {"adj_set": "[306, 307]"}),
                      ("G05 Gamma(S_I2) >= 0", {"s_i2": False}),
                      ("G06 no adjudication review", {"with_adj_rev": False}),
                      ("G07 no execution review", {"with_exec_rev": False}),
                      ("G08 result self-hash mismatch", {"bad_hash": True}),
                      ("G09 no exactly-once marker", {"marker": False}),
                      ("G10 working bytes differ from the committed bytes (dirty)",
                       {"after": lambda: sbB.p(adj_rev).write_text("# synthetic\nADJUDICATION_ACCEPTED\n\n")}),
                      ("G11 --out is r5", {"out_path": str(r5_path)}),
                      ("G12 --out wrongly named", {"out_path": str(sbB.p(f"{NS_REL}/evidence/coverage/other.json"))})):
        r5_before = r5_path.read_bytes()
        q, o = chain(**kw)
        created = o.exists() and o != r5_path
        res[f"{label}: refused"] = q.returncode != 0 and "REFUSED" in (q.stdout + q.stderr) and not created \
            and r5_path.read_bytes() == r5_before
    sbB.reset()
    return res


# ------------------------------------------------------------------ L: leak scans
def leak_scans() -> dict:
    spec = importlib.util.spec_from_file_location(
        "c12r1q", REPO / f"{CP}p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_qualify.py")
    Q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Q)
    runs = json.loads((REPO / C11RD_RUNS).read_text())
    ind = frozenset(hashlib.sha256(x.encode()).hexdigest() for k in ("D1", "D2")
                    for x in Q.CM.value_patterns(format(float(F(runs["targets"][k]["value"])), ".12f")))
    texts = {str(f.relative_to(NS)): f.read_text() for f in sorted(NS.rglob("*")) if f.is_file()}
    decoy = frozenset(hashlib.sha256(x.encode()).hexdigest() for x in Q.CM.value_patterns("0.123456789012"))
    return {"files_scanned": sorted(texts),
            "checks": {"no rendering of the original D1/D2 values": not Q._broad_hashed_scan(texts, Q.V.ORIGINAL_PATTERN_SHA256)["hits"],
                       "no rendering of the independent D1/D2 values": not Q._broad_hashed_scan(texts, ind)["hits"],
                       "the scanner detects a planted decoy (not vacuous)":
                           bool(Q._broad_hashed_scan({"x": "v 0.1234567890 w"}, decoy)["hits"])}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--review", action="store_true", help="read-only re-run by a reviewer; writes nothing in the repo")
    a = ap.parse_args(argv)
    t0 = time.time()
    try:
        pre = preconditions(a.review)
    except Refused as e:
        print(f"C12R1 VERIFY REFUSED {e}")
        return 2
    qdir = Path(tempfile.mkdtemp(prefix="c12r1rev")) if a.review else NS / "evidence/qualification"
    qdir.mkdir(parents=True, exist_ok=True)
    drv_sha = sha_b(DRIVER.read_bytes())
    report = {"schema": "rebaseguard.p5y.k5.tail-c12r1.qualification.v1", "dry_run": False, "review_mode": a.review,
              "freeze_commit": pre["freeze_commit"], "HEAD": pre["HEAD"], "state": pre["state"],
              "driver_sha256": drv_sha, "verifier_sha256": sha_b(HERE.read_bytes()),
              "r6_generator_sha256": sha_b(R6GEN.read_bytes()),
              "grant_generator_sha256": sha_b((NS / "code/c12r1_grant.py").read_bytes()), "python": sys.version.split()[0]}
    report["S_static"] = static_checks()
    report["R_real"] = real_runs(qdir)
    tmp = Path(tempfile.mkdtemp(prefix="c12r1q"))
    try:
        sbA = Sandbox(tmp, "sbA", pre["freeze_commit"])
        sbB, pins, blobs = make_decoy_sandbox(tmp, pre["freeze_commit"])
        report["sandboxes"] = {"A_commit": sbA.base, "B_parent": sbB.g("rev-parse", f"{sbB.base}^").stdout.strip(),
                               "both_from_the_freeze_commit": sbA.base == pre["freeze_commit"] ==
                               sbB.g("rev-parse", f"{sbB.base}^").stdout.strip(),
                               "B_contains_no_real_I2_file": all(
                                   json.loads(sbB.p(r).read_text()).get("DECOY") is True for r in (C11R_CMP, C11RD_CMP, C11RD_RUNS))}
        report["A_sandbox"] = sandbox_a_controls(sbA)
        report["B_sandbox_cli"] = sandbox_b_cli(sbB, drv_sha, tmp)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):                         # the decoy runs' own status lines
            report["X_flows_decoy"] = flow_tests(sbB, pins, blobs, drv_sha)
        report["X_flows_decoy_stdout"] = buf.getvalue().splitlines()
        report["G_r6_generator"] = r6_controls(sbB, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    report["F_function_controls"] = function_controls()
    report["L_leak"] = leak_scans()
    flat = {**report["S_static"], **report["R_real"]["checks"],
            "sandboxes built from the freeze commit": report["sandboxes"]["both_from_the_freeze_commit"],
            "sandbox B holds only decoy I2 inputs": report["sandboxes"]["B_contains_no_real_I2_file"],
            **{k: v["pass"] for k, v in report["A_sandbox"].items()},
            **{k: v["pass"] for k, v in report["B_sandbox_cli"].items()},
            **report["X_flows_decoy"], **report["G_r6_generator"], **report["F_function_controls"],
            **report["L_leak"]["checks"]}
    report["failed"] = sorted(k for k, v in flat.items() if v is not True)
    report["pass"] = not report["failed"]
    report["counts"] = {"checks": len(flat), "passed": sum(v is True for v in flat.values())}
    report["wall_seconds"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(f"C12R1 QUALIFICATION {'PASS' if report['pass'] else 'FAIL'} ({report['counts']['passed']}/{report['counts']['checks']})")
    for k in report["failed"]:
        print("  FAIL", k)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
