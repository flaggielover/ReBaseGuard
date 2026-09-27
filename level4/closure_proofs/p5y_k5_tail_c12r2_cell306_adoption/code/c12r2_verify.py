"""C12-R2 -- qualification verifier. It can NEVER evaluate Gamma(5, 306; S_I2) with real I2 constants.

Barriers kept from C12-R1 (whose review found them sound):
  (1) it refuses to run unless HEAD is the freeze commit (official) or, with --review, the qualification-evidence commit
      directly on it; and unless no qualification review, grant, adjudication, execution/coverage output, marker,
      pending-result ref or emergency evidence exists anywhere (tree, disk, any history, any ref) for C12-R2, C12-R1 or
      C12. With --review it also requires a clean tree and code/ + protocol/ byte-identical to the freeze (N3), and it
      keeps no output inside or outside the repository except --out (N13);
  (2) every sandbox is built at the FREEZE commit. Sandbox A (real inputs) is used only for baselines and
      input-tampering refusals and never receives a grant or review. Every governance-state, exactly-once and
      filesystem-attack test runs in sandbox B, whose I2 SUPPLY INPUT FILES (C11R_COMPARISON.json,
      C11RD_COMPARISON.json, C11RD_RUNS.json), C11R_RUNS.json and the I2 soundness documents are synthetic decoys and
      whose C11RD run logs are removed (N1: other pinned documents, e.g. the floor rule, are unchanged; they are never
      read as supply inputs);
  (3) the driver refuses execute/seal-only outside the qualified worktree / git dir / common dir / branch and without
      -I -S -B (N8).
New in C12-R2 (the C12-R1 blocker): section T = filesystem attacks on the result paths before the marker (directory,
symlink out of the repository, broken symlink, FIFO, socket, ignored regular *.tmp, planted final result, symlinked
execution directory or parent component), and section P = every post-marker failure (evaluation exception, SystemExit,
KeyboardInterrupt, evaluation wall cap, serialization failure, primary / both persistence channels failing, seal
failure, permission failure, unexpected filesystem state), each proving at most one decoy evaluation, a persisting
consumed state, a refused retry and a recovery that never recomputes. Section N classifies review notes N1-N13.

    python3.14 -I -S -B c12r2_verify.py --out FILE              (official: HEAD = freeze commit; writes evidence/qualification/)
    python3.14 -I -S -B c12r2_verify.py --review --out FILE     (HEAD = freeze or qualification commit; writes only FILE)
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
import signal
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
NS_REL = CP + "p5y_k5_tail_c12r2_cell306_adoption"
DRIVER = NS / "code/c12r2_cell306.py"
R6GEN = NS / "code/c12r2_r6_from_adjudication.py"
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
          f"/{CP}p5y_k5b_independent_countersignature/code/",
          f"/{CP}p5y_k5_tail_c11r_n9_statement_alignment/evidence/runs/C11R_RUNS.json",
          f"/{CP}p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md",
          f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/theory/D1_D2_DERIVATION.md",
          f"/{CP}p5y_k5_tail_c11rd_d1d2_extension/docs/C11RD_INDEPENDENCE_AUDIT.md",
          f"/{CP}p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md"]
C11R_RUNS = CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/runs/C11R_RUNS.json"
C11RD_THEORY = CP + "p5y_k5_tail_c11rd_d1d2_extension/theory/D1_D2_DERIVATION.md"
C11RD_AUDIT = CP + "p5y_k5_tail_c11rd_d1d2_extension/docs/C11RD_INDEPENDENCE_AUDIT.md"


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(repo, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], capture_output=True, text=True, env=dict(ENV),
                          stdin=subprocess.DEVNULL, timeout=300)


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
    D = load_driver("c12r2_pre")
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
    for prefix in ("refs/c12r2/", "refs/c12r1/", "refs/c12/"):
        if rgit("for-each-ref", "--format=%(refname)", prefix).stdout.strip():
            raise Refused(f"a marker or pending ref exists under {prefix}")
    try:
        D.check_not_evaluated()
        D.check_result_paths()
    except D.Refusal as e:
        raise Refused(f"prior evaluation evidence or an occupied result path: {e}")
    if rgit("status", "--porcelain", "--ignored", "--untracked-files=all").stdout.strip():
        raise Refused("the verifier needs a clean tree (tracked, untracked and ignored)")
    if rgit("diff", "--name-only", fz, "HEAD", "--", f"{NS_REL}/code", f"{NS_REL}/protocol").stdout.strip():
        raise Refused("code/ or protocol/ differ from the freeze commit (N3)")
    return {"freeze_commit": fz, "HEAD": head, "state": "freeze" if head == fz else "qualification"}


# ------------------------------------------------------------------ S: static structure of the driver
def static_checks() -> dict:
    tree = ast.parse(DRIVER.read_text())
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def names_in(fn):
        return {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    refs = {name: {f for f, fn in fns.items() if name in names_in(fn)}
            for name in ("evaluate_target", "prepare_target", "after_marker")}
    ex = fns["run_execute"]

    def first(fn, pred):
        ls = [n.lineno for n in ast.walk(fn) if pred(n)]
        return min(ls) if ls else None

    def call(name):
        return lambda n: isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
    order = [first(ex, call(c)) for c in ("check_flags", "check_identity", "check_not_evaluated", "check_result_paths",
                                          "check_clean", "check_grant", "check_bindings", "check_governance_state",
                                          "check_seal_preconditions", "load_consumer", "control")]
    order += [first(ex, lambda n: isinstance(n, ast.Constant) and n.value == "CONTROL_FAILED"),
              first(ex, call("prepare")),
              first(ex, lambda n: isinstance(n, ast.Attribute) and n.attr == "SIG_IGN"),
              first(ex, lambda n: isinstance(n, ast.Name) and n.id == "CONSUMED_REF"),
              first(ex, call("after_marker"))]
    am = fns["after_marker"]
    am_top = [st for st in am.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
    risky = [st for st in am_top if not isinstance(st, (ast.Try, ast.Return, ast.Assign, ast.If))
             and not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)
                      and ast.unparse(st.value.func) in ("signal.signal", "print"))]
    trys = [st for st in am_top if isinstance(st, ast.Try)]
    base_handled = all(any(isinstance(h.type, ast.Name) and h.type.id == "BaseException" for h in t.handlers) for t in trys)
    am_calls = [(n.lineno, n.func.id) for n in ast.walk(am) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    line = {name: min([ln for ln, f in am_calls if f == name] or [None]) for name in ("evaluator", "persist", "sealer", "materializer")}
    so = fns["run_seal_only"]
    so_calls = [n.func.id for n in ast.walk(so) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    main_calls = [n for n in ast.walk(fns["main"]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                  and n.func.id == "run_execute"]
    printed = {ast.unparse(v.value) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "print" for v in ast.walk(n) if isinstance(v, ast.FormattedValue)}
    src = DRIVER.read_text()
    return {
        "evaluate_target / prepare_target referenced only by run_execute; after_marker only by run_execute":
            refs["evaluate_target"] == {"run_execute"} and refs["prepare_target"] == {"run_execute"}
            and refs["after_marker"] == {"run_execute"},
        "run_execute order: flags < identity < not-evaluated < result paths < clean (incl. ignored) < grant < bindings < "
        "state < seal preconditions < consumer < control < CONTROL_FAILED exit < prepare < signals ignored < marker < "
        "after_marker": None not in order and order == sorted(order) and len(set(order)) == len(order),
        "after_marker: every top-level statement is a try with an `except BaseException`, an assignment, a guarded "
        "branch or a return (nothing escapes)": risky == [] and trys != [] and base_handled,
        "after_marker order: evaluation < persistence < seal < materialization":
            None not in line.values() and line["evaluator"] < line["persist"] < line["sealer"] < line["materializer"],
        "the result is never written through the filesystem before the seal (no write_result, sealed via --cacheinfo)":
            "def write_result" not in src and "--cacheinfo" in ast.unparse(fns["seal_blob"])
            and "O_EXCL" in ast.unparse(fns["materialize"]) and "O_NOFOLLOW" in ast.unparse(fns["materialize"]),
        "seal-only: flags and identity first, never computes": so_calls[:2] == ["check_flags", "check_identity"]
            and not {"evaluate_target", "prepare_target", "control", "evaluate", "load_consumer", "after_marker"} & set(so_calls),
        "the CLI calls run_execute(own_sha) with no injection": len(main_calls) == 1 and len(main_calls[0].args) == 1
            and not main_calls[0].keywords,
        "no print of a computed value": printed <= {"a.cell", "cid", "e", "status", "channel",
                                                    "ctl['reproduces_C2_exactly']", "type(exc).__name__"},
        "no numpy/flint import": not ({"numpy", "flint"} & {a.name.split(".")[0] for n in ast.walk(tree)
                                                               if isinstance(n, ast.Import) for a in n.names}),
        "the grant generator requires QUAL_REL and commits through the driver's sanitized git (N9)":
            "D.QUAL_REL not in qfiles" in (NS / "code/c12r2_grant.py").read_text()
            and 'D.git("-c", "core.hooksPath=/dev/null", "commit"' in (NS / "code/c12r2_grant.py").read_text(),
        "the G07 soundness evidence is pinned by sha256 and blob (N10)": all(
            k in src and f'"{k}": "' in src for k in ("soundness_c11r_runs", "soundness_c2_cell306_adoption",
                                                      "soundness_c11rd_theory", "soundness_c11rd_independence_audit",
                                                      "soundness_c2_adjudication")),
        "review mode removes its temporary output (N13)": "shutil.rmtree(review_tmp" in HERE.read_text(),
    }


# ------------------------------------------------------------------ R: real repository, read-only
def run_cli(repo: Path, script: str, *argv, out: Path = None, home="/var/empty") -> tuple:
    cmd = [PY, "-I", "-S", "-B", str(repo / NS_REL / "code" / script), *argv]
    if out is not None:
        cmd += ["--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": home},
                       stdin=subprocess.DEVNULL, timeout=900)
    return p.returncode, (p.stdout + p.stderr)[-400:]


def real_runs(qdir: Path) -> dict:
    out = {}
    code, text = run_cli(REPO, "c12r2_cell306.py", "execute", home=os.environ.get("HOME", "/var/empty"))
    out["execute_in_the_real_worktree"] = {"exit": code, "out": text}
    for name, argv in (("preflight", ("preflight",)), ("rehearse_306", ("rehearse", "--cell", "306")),
                       ("rehearse_305", ("rehearse", "--cell", "305"))):
        f = qdir / f"{name.upper()}.json"
        code, text = run_cli(REPO, "c12r2_cell306.py", *argv, out=f)
        rec = json.loads(f.read_text()) if f.exists() else {}
        out[name] = {"exit": code, "out": text, "reproduces_C2_exactly": rec.get("control", {}).get("reproduces_C2_exactly"),
                     "field_matches": rec.get("control", {}).get("field_matches")}
    marker = rgit("for-each-ref", "refs/c12r2", "refs/c12r1", "refs/c12").stdout.strip()
    out["checks"] = {
        "a real execute at this state refuses GRANT_MISSING (identity, no-prior-evaluation and clean tree pass first)":
            out["execute_in_the_real_worktree"]["exit"] == 2 and "REFUSED GRANT_MISSING" in out["execute_in_the_real_worktree"]["out"],
        "preflight PASS": out["preflight"]["exit"] == 0 and "PREFLIGHT PASS" in out["preflight"]["out"],
        "I1 control reproduces C2 exactly for 306, including C2's per-supply records (N2)":
            out["rehearse_306"]["exit"] == 0 and out["rehearse_306"]["reproduces_C2_exactly"] is True
            and (out["rehearse_306"]["field_matches"] or {}).get("per_supply_records_G_C1_C2") is True,
        "I1 control reproduces C2 exactly for the non-target 305": out["rehearse_305"]["exit"] == 0
            and out["rehearse_305"]["reproduces_C2_exactly"] is True,
        "no marker or pending ref exists in the real repository": marker == "",
        "no result path object exists in the real repository (lexists)": not os.path.lexists(REPO / f"{NS_REL}/evidence/execution"),
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
        return git(self.root, "-c", "user.name=c12r2-sandbox", "-c", "user.email=sandbox@invalid", *args)

    def p(self, rel: str) -> Path:
        return self.root / rel

    def head(self) -> str:
        return self.g("rev-parse", "HEAD").stdout.strip()

    def commit_all(self, msg: str) -> str:
        self.g("add", "-A", "--sparse", ".")
        self.g("commit", "-q", "--no-verify", "-m", msg)
        return self.head()

    def reset(self):
        ns = self.p(NS_REL)
        for d in [ns, *ns.rglob("*")] if ns.exists() else []:            # undo chmod tests (never follows links)
            if not d.is_symlink() and d.is_dir():
                os.chmod(d, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        for rel in (f"{NS_REL}/evidence/execution", f"{NS_REL}/evidence"):
            q = self.p(rel)
            if q.is_symlink() or (os.path.lexists(q) and not q.is_dir()):
                q.unlink()
            elif rel.endswith("execution") and q.is_dir():
                shutil.rmtree(q)
        em = self.root / ".git" / "c12r2-cell306-emergency-result.json"
        if os.path.lexists(em):
            em.unlink()
        self.g("checkout", "-q", "-f", "-B", "campaign", self.base)
        self.g("reset", "-q", "--hard", self.base)
        self.g("clean", "-qfdx")
        for ref in self.g("for-each-ref", "--format=%(refname)", "refs/c12r2", "refs/c12r1", "refs/c12").stdout.split():
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
    c11r_runs = {"DECOY": True, "cell": 306, "note": "synthetic stand-in for C11R_RUNS.json"}
    for rel, obj in ((C11R_CMP, c11r), (C11RD_CMP, c11rd), (C11RD_RUNS, runs), (C11R_RUNS, c11r_runs)):
        sb.p(rel).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    for rel in (C11RD_THEORY, C11RD_AUDIT):
        sb.p(rel).write_text("# DECOY placeholder for a soundness document (sandbox only)\n")
    for f in sorted(sb.p(C11RD_RUNS).parent.iterdir()):                  # N1: run logs removed from sandbox B
        if f.name != Path(C11RD_RUNS).name:
            f.unlink()
    sb.p(f"{NS_REL}/protocol").mkdir(parents=True, exist_ok=True)
    sb.p(f"{NS_REL}/protocol/SANDBOX_DECOY.md").write_text("sandbox-only decoy freeze; not part of the campaign\n")
    sb.base = sb.commit_all("sandbox decoy freeze: synthetic I2 inputs and soundness documents")
    pins = {k: (rel, sha_b(sb.p(rel).read_bytes())) for k, rel in
            (("c11r_comparison", C11R_CMP), ("c11rd_comparison", C11RD_CMP), ("c11rd_runs", C11RD_RUNS),
             ("soundness_c11r_runs", C11R_RUNS), ("soundness_c11rd_theory", C11RD_THEORY),
             ("soundness_c11rd_independence_audit", C11RD_AUDIT))}
    blobs = {k: sb.g("rev-parse", f"HEAD:{rel}").stdout.strip()[:12] for k, (rel, _) in pins.items()}
    return sb, pins, blobs


def build_state(sb: Sandbox, upto: str, drv_sha: str, grant_patch: dict = None, review_line: str = "QUALIFICATION_ACCEPTED"):
    """Synthetic governance chain on sandbox B: Q (qualification evidence) -> R (review) -> G (grant)."""
    D = sys.modules["c12r2_pre"]
    fz = sb.head()
    q = sb.p(D.QUAL_REL)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps({"pass": True, "review_mode": False, "freeze_commit": fz, "SYNTHETIC": True}))
    qc = sb.commit_all("sandbox synthetic qualification")
    if upto == "Q":
        return
    r = sb.p(D.QREVIEW_REL)
    r.parent.mkdir(parents=True, exist_ok=True)
    r.write_text(f"# synthetic\n{review_line}\n")
    rc = sb.commit_all("sandbox synthetic review")
    if upto == "R":
        return
    g = {"schema": "rebaseguard.p5y.k5.tail-c12r2.grant.v1", "exactly_once": True, "driver_sha256": drv_sha,
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
        code, text = run_cli(sbA.root, "c12r2_cell306.py", *argv)
        res[name] = {"argv": list(argv), "exit": code, "out": text[-240:],
                     "pass": code == want_exit and (want_code is None or f"REFUSED {want_code}" in text)
                     and snapshot() == before}

    reg1 = CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json"
    reg2 = CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"
    D = sys.modules["c12r2_pre"]

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
    run("A07c planted predecessor C12-R1 result", plant(D.PRIOR_RESULTS[1]), ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("A07c2 planted predecessor C12 result", plant(D.PRIOR_RESULTS[2]), ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("A07f planted predecessor marker (refs/c12r1)", lambda: sbA.g("update-ref", "refs/c12r1/cell306-target-consumed", "HEAD"),
        ("preflight",), 2, "CONSUMED")
    run("A07g planted pending-result ref (refs/c12r2)", lambda: sbA.g("update-ref", D.PENDING_REF, "HEAD"),
        ("preflight",), 2, "CONSUMED")
    run("A07d planted marker (refs/c12r2)", lambda: sbA.g("update-ref", D.CONSUMED_REF, "HEAD"),
        ("rehearse", "--cell", "306"), 2, "CONSUMED")
    run("A07e planted predecessor marker (refs/c12)", lambda: sbA.g("update-ref", "refs/c12/cell306-target-consumed", "HEAD"),
        ("preflight",), 2, "CONSUMED")
    run("A12 an r6 file in the working tree", plant(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R6.json"),
        ("preflight",), 2, "R6_EXISTS")
    sbA.reset()
    q = subprocess.run([PY, "-S", "-B", str(sbA.p(NS_REL) / "code/c12r2_cell306.py"), "execute"], capture_output=True,
                       text=True, env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"}, stdin=subprocess.DEVNULL, timeout=900)
    res["A21 execute without -I is refused before anything (N8)"] = {"exit": q.returncode, "out": q.stdout[-200:],
                                                                    "pass": q.returncode == 2 and "REFUSED INTERPRETER_FLAGS" in q.stdout}
    run("A20 freeze-commit sandbox (real inputs) cannot execute: identity refused first", None, ("execute",), 2,
        "REPO_NOT_QUALIFIED")
    sbA.reset()
    return res


def sandbox_b_cli(sbB: Sandbox, drv_sha: str, tmp: Path) -> dict:
    """Governance-state sandboxes through the REAL CLI: all must refuse, write no result and create no marker."""
    res = {}
    D = sys.modules["c12r2_pre"]

    def check(name, argv=("execute",), repo=None, script="c12r2_cell306.py", want="REFUSED REPO_NOT_QUALIFIED", exit_=2):
        r = repo or sbB.root
        before = git(r, "for-each-ref", "refs/c12r2").stdout
        code, text = run_cli(r, script, *argv, home=os.environ.get("HOME", "/var/empty"))
        after = git(r, "for-each-ref", "refs/c12r2").stdout
        res[name] = {"exit": code, "out": text[-240:],
                     "pass": code == exit_ and want in text and not (r / D.RESULT_REL).exists() and before == after}

    sbB.reset(); build_state(sbB, "Q", drv_sha)
    check("B01 qualification-commit sandbox cannot target-evaluate")
    sbB.reset(); build_state(sbB, "R", drv_sha)
    check("B02 accepted-review-state sandbox cannot target-evaluate")
    check("B02v the verifier refuses to run in an accepted-review state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r2_verify.py", want="VERIFY REFUSED")
    sbB.reset(); build_state(sbB, "G", drv_sha)
    check("B03 grant-state sandbox cannot target-evaluate")
    check("B03s grant-state sandbox cannot seal-only", argv=("seal-only",))
    check("B03v the verifier refuses to run in a grant state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r2_verify.py", want="VERIFY REFUSED")
    cp = tmp / "copied_repository"
    shutil.copytree(sbB.root, cp, symlinks=True)
    check("B05 a copied repository (grant state) cannot target-evaluate", repo=cp)
    shutil.rmtree(cp, ignore_errors=True)
    sbB.g("update-ref", D.CONSUMED_REF, "HEAD")
    check("B04 consumed-state sandbox cannot target-evaluate")
    check("B04v the verifier refuses to run in a consumed state", argv=("--review", "--out", str(tmp / "v.json")),
          script="c12r2_verify.py", want="VERIFY REFUSED")
    sbB.reset(); build_state(sbB, "G", drv_sha)
    sbB.p(D.RESULT_REL).parent.mkdir(parents=True, exist_ok=True)
    sbB.p(D.RESULT_REL).write_text("{}")
    code, text = run_cli(sbB.root, "c12r2_verify.py", "--review", "--out", str(tmp / "v.json"))
    res["B06v the verifier refuses to run at a grant state with a planted result (refused by the HEAD test)"] = {"exit": code, "out": text[-240:],
                                                                     "pass": code == 2 and "VERIFY REFUSED" in text}
    # barrier 1 at the freeze state itself (HEAD = the sandbox's freeze commit): planted review / marker / result
    for label, plant in (("B07v planted qualification review file", lambda: (sbB.p(D.QREVIEW_REL).parent.mkdir(parents=True, exist_ok=True),
                                                                           sbB.p(D.QREVIEW_REL).write_text("# x\nQUALIFICATION_ACCEPTED\n"))),
                         ("B08v planted exactly-once marker", lambda: sbB.g("update-ref", D.CONSUMED_REF, "HEAD")),
                         ("B09v planted predecessor C12-R1 result", lambda: (sbB.p(D.PRIOR_RESULTS[1]).parent.mkdir(parents=True, exist_ok=True),
                                                                          sbB.p(D.PRIOR_RESULTS[1]).write_text("{}"))),
                         ("B10v this campaign's own result planted at the freeze state (N2)",
                          lambda: (sbB.p(D.RESULT_REL).parent.mkdir(parents=True, exist_ok=True), sbB.p(D.RESULT_REL).write_text("{}"))),
                         ("B11v an ignored *.tmp object planted in the namespace at the freeze state",
                          lambda: sbB.p(f"{NS_REL}/code/stray.tmp").write_text("x")),
                         ("B12v --review with modified code at the freeze state (N3)",
                          lambda: sbB.p(f"{NS_REL}/code/c12r2_cell306.py").write_text(
                              sbB.p(f"{NS_REL}/code/c12r2_cell306.py").read_text() + "\n# modified\n"))):
        sbB.reset()
        plant()
        code, text = run_cli(sbB.root, "c12r2_verify.py", "--review", "--out", str(tmp / "v.json"))
        res[f"{label}: the verifier refuses at the freeze state"] = {"exit": code, "out": text[-240:],
                                                                     "pass": code == 2 and "VERIFY REFUSED" in text}
    sbB.reset()
    return res


# ------------------------------------------------------------------ X: exactly-once flows on DECOY targets
def flow_tests(sbB: Sandbox, pins: dict, blobs: dict, drv_sha: str, tmp: Path) -> dict:
    """X: exactly-once governance flows; T: filesystem attacks on the result paths (the C12-R1 blocker) before the
    marker; P: every post-marker failure. All on DECOY I2 inputs, in-process, identity pointed at sandbox B."""
    res = {}
    decoy_base = sbB.base
    sigs = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGALRM)
    saved = {sg: signal.getsignal(sg) for sg in sigs}

    def restore_signals():
        signal.alarm(0)
        for sg, h in saved.items():
            signal.signal(sg, h)

    def fresh(upto="G", **kw):
        restore_signals()
        sbB.reset()
        if upto:
            build_state(sbB, upto, drv_sha, **kw)
        D = load_driver(f"c12r2_flow_{len(res)}_{time.time_ns()}")
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
        D._orig_eval = orig_eval
        return D, calls, prep, ev

    def consumed(D):
        return bool(sbB.g("rev-parse", "-q", "--verify", D.CONSUMED_REF).stdout.strip())

    def pending(D):
        return sbB.g("rev-parse", "-q", "--verify", D.PENDING_REF).stdout.strip()

    def in_head(D):
        return D.RESULT_REL in sbB.g("ls-tree", "-r", "--name-only", "HEAD").stdout.split()

    def head_blob(D):
        return sbB.g("rev-parse", f"HEAD:{D.RESULT_REL}").stdout.strip()

    def refused(D, fn, code):
        try:
            fn()
        except D.Refusal as e:
            return e.code == code
        return False

    def untouched(D, calls):
        return not consumed(D) and not pending(D) and calls["evaluate"] == 0 and calls["prepare"] == 0 and not in_head(D)

    def quiet(fn):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = fn()
        return out, buf.getvalue()

    # ---- X: governance flows
    D, calls, prep, ev = fresh()
    D.QUALIFIED_WORKTREE = "/nonexistent/qualified/worktree"
    res["X01 wrong worktree cannot consume"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "REPO_NOT_QUALIFIED") \
        and untouched(D, calls) and calls["control"] == 0
    D, calls, prep, ev = fresh()
    sbB.g("checkout", "-q", "--detach")
    res["X02 wrong branch (detached) cannot consume"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "WRONG_BRANCH") \
        and untouched(D, calls)
    D, calls, prep, ev = fresh()
    sbB.g("checkout", "-q", "-b", "other")
    res["X02b wrong branch (another branch) cannot consume"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "WRONG_BRANCH") \
        and untouched(D, calls)
    D, calls, prep, ev = fresh()
    cp = tmp / "copy_for_X03"
    shutil.copytree(sbB.root, cp, symlinks=True)
    D.REPO = cp
    res["X03 a copy of the qualified repository cannot consume"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev),
                                                                            "REPO_NOT_QUALIFIED") and calls["evaluate"] == 0 \
        and not git(cp, "for-each-ref", "refs/c12r2").stdout.strip()
    shutil.rmtree(cp, ignore_errors=True)
    for st in ("Q", "R"):
        D, calls, prep, ev = fresh(st)
        res[f"X04 {st}-state cannot consume (GRANT_MISSING)"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev),
                                                                        "GRANT_MISSING") and untouched(D, calls)
    # X05 the full DECOY pipeline, exactly once, sealed from memory, materialized exclusively
    D, calls, prep, ev = fresh()
    code, _ = quiet(lambda: D.run_execute(drv_sha, prep, ev))
    f = sbB.p(D.RESULT_REL)
    st = os.lstat(f) if os.path.lexists(f) else None
    data = f.read_bytes() if st and stat.S_ISREG(st.st_mode) else b""
    r = json.loads(data) if data else {}
    body = {k: v for k, v in r.items() if k != "sha256"}
    mode = sbB.g("ls-tree", "HEAD", "--", D.RESULT_REL).stdout.split()[:1]
    res["X05 grant-state DECOY run: one evaluation; sealed bytes = pending blob = produced bytes = worktree copy"] = \
        code == 0 and in_head(D) and consumed(D) and pending(D) == head_blob(D) == D.git_blob_id(data) \
        and mode == ["100644"] and st is not None and stat.S_ISREG(st.st_mode) \
        and sha_b(json.dumps(body, sort_keys=True).encode()) == r.get("sha256") and r.get("status") == "TARGET_EVALUATED" \
        and r.get("target_evaluations") == 1 and r["input_sha256"]["c11r_comparison"] == pins["c11r_comparison"][1] \
        and r["control"]["reproduces_C2_exactly"] and calls == {"control": 1, "prepare": 1, "evaluate": 1}
    res["X06 a second execute after a sealed run is refused before anything"] = \
        refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED") and calls == {"control": 1, "prepare": 1, "evaluate": 1}
    code, out = quiet(D.run_seal_only)
    res["X06b seal-only after a complete run changes nothing and computes nothing"] = code == 0 and "nothing computed" in out \
        and calls["evaluate"] == 1
    for label, rel in (("X07 own result", None), ("X07b predecessor C12-R1 result", 1), ("X07c predecessor C12 result", 2)):
        D, calls, prep, ev = fresh()
        target = sbB.p(D.RESULT_REL if rel is None else D.PRIOR_RESULTS[rel])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}")
        res[f"{label} planted: refused before anything"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev),
                                                                   "TARGET_ARTIFACT_EXISTS") and untouched(D, calls)
    D, calls, prep, ev = fresh()
    sbB.g("update-ref", D.CONSUMED_REF, "HEAD")
    res["X08 consumed state: refused before control, prepare or evaluation"] = \
        refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED") and calls == {"control": 0, "prepare": 0, "evaluate": 0}
    D, calls, prep, ev = fresh()
    sbB.g("update-ref", D.PENDING_REF, "HEAD")
    res["X08b a pending-result ref: refused before anything"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED") \
        and calls["evaluate"] == 0
    D, calls, prep, ev = fresh()
    (sbB.root / ".git" / D.EMERGENCY_NAME).write_text("{}")
    res["X08c an emergency evidence file: refused before anything"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev),
                                                                               "TARGET_ARTIFACT_EXISTS") and untouched(D, calls)
    # X11 control mismatch: CONTROL_FAILED sealed, no marker, no I2 preparation or evaluation; the campaign is spent
    D, calls, prep, ev = fresh(None)
    fc_rel = D.PINS["c2_forecast"][0]
    fc = json.loads(sbB.p(fc_rel).read_text())
    fc["cells"]["306"]["Gamma_exact"] += "1"
    sbB.p(fc_rel).write_text(json.dumps(fc))
    mk = sbB.p(f"{NS_REL}/protocol/SANDBOX_DECOY.md")
    mk.write_text(mk.read_text() + "perturbed control artifact (X11)\n")
    sbB.base = sbB.commit_all("sandbox perturbed control artifact")
    build_state(sbB, "G", drv_sha)
    D.PINS = {**D.PINS, "c2_forecast": (fc_rel, sha_b(sbB.p(fc_rel).read_bytes()))}
    D.BLOBS = {**D.BLOBS, "c2_forecast": sbB.g("rev-parse", f"HEAD:{fc_rel}").stdout.strip()[:12]}
    code, _ = quiet(lambda: D.run_execute(drv_sha, prep, ev))
    r = json.loads(sbB.p(D.RESULT_REL).read_text()) if sbB.p(D.RESULT_REL).is_file() else {}
    res["X11 control mismatch: CONTROL_FAILED sealed, no marker, no I2 preparation or evaluation; retry refused"] = code == 3 \
        and r.get("status") == "CONTROL_FAILED" and not consumed(D) and pending(D) == head_blob(D) \
        and calls["prepare"] == 0 and calls["evaluate"] == 0 and refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")
    sbB.base = decoy_base
    # X12 grant variants (N5/N6)
    for label, patch in (("schema", {"schema": "wrong"}), ("exactly_once false", {"exactly_once": False}),
                         ("driver sha", {"driver_sha256": "0" * 64}), ("freeze commit named wrong", {"freeze_commit": "0" * 40}),
                         ("qualification commit named wrong", {"qualification_commit": "1" * 40}),
                         ("review commit named wrong", {"qualification_review_commit": "2" * 40})):
        D, calls, prep, ev = fresh("G", grant_patch=patch)
        res[f"X12 grant variant refused: {label}"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_INVALID") \
            and untouched(D, calls)
    D, calls, prep, ev = fresh("G", review_line="QUALIFICATION_REJECTED")
    res["X12b a REJECTED review cannot be granted"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "REVIEW_VERDICT") \
        and untouched(D, calls)
    D, calls, prep, ev = fresh("G")
    sbB.p(f"{NS_REL}/authorization/EXTRA").write_text("x")
    sbB.g("add", "-A", "--sparse", ".")
    sbB.g("commit", "-q", "--amend", "--no-edit")
    res["X12c a grant commit carrying another file is refused"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev),
                                                                          "GRANT_INVALID") and untouched(D, calls)
    D, calls, prep, ev = fresh("G")
    sbB.p(f"{NS_REL}/NOTE").write_text("x")
    sbB.commit_all("sandbox commit after the grant")
    res["X12d HEAD not the grant commit is refused"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_INVALID") \
        and untouched(D, calls)
    D, calls, prep, ev = fresh(None)
    old_fz = sbB.head()
    sbB.p(f"{NS_REL}/code/ADDED_AFTER_FREEZE.py").write_text("# x\n")
    sbB.commit_all("sandbox code change after the freeze")
    build_state(sbB, "G", drv_sha, grant_patch={"freeze_commit": old_fz})
    res["X12e code changed after the freeze: the grant naming the old freeze is refused (N6)"] = \
        refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GRANT_INVALID") and untouched(D, calls)
    # X13 pre-marker environment
    D, calls, prep, ev = fresh()
    sbB.p(f"{NS_REL}/UNTRACKED").write_text("x")
    res["X13 dirty tree refused before the marker"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "DIRTY_TREE") \
        and untouched(D, calls)
    D, calls, prep, ev = fresh()
    (sbB.root / ".git/index.lock").write_text("")
    res["X13b a git lock is refused before the marker"] = refused(D, lambda: D.run_execute(drv_sha, prep, ev), "GIT_LOCKED") \
        and untouched(D, calls)
    (sbB.root / ".git/index.lock").unlink()
    D, calls, prep, ev = fresh()
    os.chmod(sbB.p(f"{NS_REL}/evidence"), stat.S_IRUSR | stat.S_IXUSR)
    res["X13c an unwritable result parent is refused before the marker"] = \
        refused(D, lambda: D.run_execute(drv_sha, prep, ev), "SEAL_PRECONDITION") and untouched(D, calls)

    # ---- T: the C12-R1 blocker -- every planted object at the result paths, before the marker
    tmp_rel = f"{NS_REL}/evidence/execution/C12R2_CELL306_RESULT.tmp"
    sentinel = tmp / "outside_sentinel.json"

    def attack(label, plant, code="RESULT_PATH_OCCUPIED", status_blind=False):
        D, calls, prep, ev = fresh()
        sentinel.write_text("OUTSIDE-SENTINEL\n")
        before = (sentinel.read_bytes(), os.lstat(sentinel).st_mtime_ns)
        plant(D)
        blind = sbB.g("status", "--porcelain", "--untracked-files=all").stdout.strip() == ""
        ok = refused(D, lambda: D.run_execute(drv_sha, prep, ev), code) and untouched(D, calls)
        ok = ok and (sentinel.read_bytes(), os.lstat(sentinel).st_mtime_ns) == before
        if status_blind:
            ok = ok and blind                                  # proves the default `git status` could not see it
        res[label] = ok

    def mk(rel):
        sbB.p(rel).parent.mkdir(parents=True, exist_ok=True)
        return sbB.p(rel)

    attack("T1 directory at the temporary-result path (ignored *.tmp): refused, 0 evaluations, no marker, no result",
           lambda D: mk(tmp_rel).mkdir(), status_blind=True)
    attack("T2 symlink at the temporary-result path to a file outside the repository: refused, outside unchanged",
           lambda D: os.symlink(sentinel, mk(tmp_rel)), status_blind=True)
    attack("T3 broken symlink at the temporary-result path: refused",
           lambda D: os.symlink(tmp / "does_not_exist", mk(tmp_rel)), status_blind=True)
    attack("T4 regular file at the final result path: refused", lambda D: mk(D.RESULT_REL).write_text("{}"),
           code="TARGET_ARTIFACT_EXISTS")
    attack("T4b symlink at the final result path to outside: refused, outside unchanged",
           lambda D: os.symlink(sentinel, mk(D.RESULT_REL)), code="TARGET_ARTIFACT_EXISTS")
    attack("T4c directory at the final result path: refused", lambda D: mk(D.RESULT_REL).mkdir(), code="TARGET_ARTIFACT_EXISTS")
    attack("T4d broken symlink at the final result path: refused",
           lambda D: os.symlink(tmp / "does_not_exist", mk(D.RESULT_REL)), code="TARGET_ARTIFACT_EXISTS")
    attack("T5 ignored regular *.tmp file at the temporary-result path: refused although `git status` is blind to it",
           lambda D: mk(tmp_rel).write_text("x"), status_blind=True)
    attack("T5b ignored *.tmp file elsewhere in the namespace: refused (R2, ignored-aware cleanliness)",
           lambda D: mk(f"{NS_REL}/code/stray.tmp").write_text("x"), code="IGNORED_OBJECT", status_blind=True)
    attack("T6 FIFO at the temporary-result path: refused", lambda D: os.mkfifo(mk(tmp_rel)), status_blind=True)

    def sock(D):
        import socket
        d = mk(tmp_rel).parent
        here = os.getcwd()
        s = socket.socket(socket.AF_UNIX)
        try:
            os.chdir(d)
            s.bind(Path(tmp_rel).name)
        finally:
            os.chdir(here)
            s.close()
    attack("T7 socket at the temporary-result path: refused", sock, status_blind=True)
    outside_dir = tmp / "outside_dir"

    def exec_dir_link(D):
        outside_dir.mkdir(exist_ok=True)
        mk(f"{NS_REL}/evidence/execution")
        os.symlink(outside_dir, sbB.p(f"{NS_REL}/evidence/execution"))
    attack("T8 the execution directory is a symlink to outside: refused", exec_dir_link)

    def parent_link(D):
        ev_dir = sbB.p(f"{NS_REL}/evidence")
        moved = tmp / "moved_evidence"
        shutil.rmtree(moved, ignore_errors=True)
        shutil.move(str(ev_dir), str(moved))
        os.symlink(moved, ev_dir)
    attack("T9 a symlinked parent component (evidence/): refused", parent_link)
    shutil.rmtree(tmp / "moved_evidence", ignore_errors=True)

    # ---- P: every post-marker failure is recorded and sealed (or recoverable), never recomputed
    def post(label, evaluator_fn=None, persist=None, sealer=None, emergency_fail=False, want_exit=5, want_status=None,
             recover=True, after=None, recover_exit=0, cap=None):
        D, calls, prep, ev = fresh()
        if cap:
            D.EVAL_CAP_S = cap
        if emergency_fail:
            def no_emergency(data):
                raise OSError("injected: emergency channel unavailable")
            D.persist_emergency = no_emergency

        def evaluator(con, p):
            calls["evaluate"] += 1
            return evaluator_fn(D, con, p) if evaluator_fn else D._orig_eval(con, p)
        code, out = quiet(lambda: D.run_execute(drv_sha, prep, evaluator, persist, sealer))
        ok = code == want_exit and consumed(D) and calls["evaluate"] == 1
        if want_status:
            blob = pending(D) or (head_blob(D) if in_head(D) else "")
            data = sbB.g("cat-file", "blob", blob).stdout if blob else ""
            if not data and (sbB.root / ".git" / D.EMERGENCY_NAME).exists():
                data = (sbB.root / ".git" / D.EMERGENCY_NAME).read_text()
            ok = ok and bool(data) and json.loads(data).get("status") == want_status
        ok = ok and refused(D, lambda: D.run_execute(drv_sha, prep, ev), "CONSUMED")      # retry refused
        if after:
            after(D)
        if recover:
            restore_signals()
            try:
                rc, _ = quiet(D.run_seal_only)
            except D.Refusal as e:
                rc = f"REFUSED {e.code}"
            ok = ok and rc == recover_exit and calls["evaluate"] == 1                        # recovery never recomputes
            if recover_exit == 0:
                ok = ok and in_head(D) and head_blob(D) == pending(D)
        res[label] = bool(ok)

    def boom(exc):
        def f(D, con, p):
            raise exc
        return f
    post("P01 evaluation exception: sealed TARGET_EVALUATION_FAILED; retry refused; seal-only computes nothing",
         boom(ValueError("injected")), want_status="TARGET_EVALUATION_FAILED")
    post("P02 SystemExit in the evaluation (as C2's crosscheck raises): sealed, retry refused",
         boom(SystemExit("injected crosscheck failure")), want_status="TARGET_EVALUATION_FAILED")
    post("P03 KeyboardInterrupt in the evaluation: sealed, retry refused", boom(KeyboardInterrupt()),
         want_status="TARGET_EVALUATION_FAILED")

    def slow(D, con, p):
        time.sleep(3)
        return D._orig_eval(con, p)
    post("P04 evaluation wall cap fires: sealed TARGET_EVALUATION_FAILED, retry refused", slow, cap=1,
         want_status="TARGET_EVALUATION_FAILED")

    def unserializable(D, con, p):
        t = D._orig_eval(con, p)
        t["evaluated"]["unserializable"] = {1, 2}
        return t
    post("P05 serialization failure after the evaluation: sealed POST_MARKER_RECORDING_FAILED, retry refused",
         unserializable, want_status="POST_MARKER_RECORDING_FAILED")

    def primary_fails(data):
        raise OSError("injected: object store unavailable")
    post("P06 primary persistence fails: emergency channel used, UNSEALED, retry refused, seal-only seals it without "
         "computing", persist=primary_fails, want_exit=4, want_status="TARGET_EVALUATED")
    post("P07 both persistence channels fail: CONSUMED_UNRECORDED, retry refused, seal-only refuses, nothing recomputed",
         persist=primary_fails, emergency_fail=True, want_exit=6, recover_exit="REFUSED SEAL_ONLY")

    def seal_fails(blob, message):
        raise OSError("injected: commit-tree failed")
    post("P08 seal failure (non-Refusal error): UNSEALED, pending evidence kept, retry refused, seal-only seals it",
         sealer=seal_fails, want_exit=4, want_status="TARGET_EVALUATED")

    def lock_parent(D, con, p):
        t = D._orig_eval(con, p)
        os.chmod(sbB.p(f"{NS_REL}/evidence"), stat.S_IRUSR | stat.S_IXUSR)
        return t
    post("P09 permission failure after the marker: sealed, worktree copy refused (exit 7), retry refused, seal-only "
         "materializes after the permission is restored", lock_parent, want_exit=7, want_status="TARGET_EVALUATED",
         after=lambda D: os.chmod(sbB.p(f"{NS_REL}/evidence"), stat.S_IRWXU))

    def plant_exec_dir(D, con, p):
        t = D._orig_eval(con, p)
        sbB.p(f"{NS_REL}/evidence/execution").mkdir(parents=True)
        return t
    post("P10 unexpected filesystem state after the marker (directory planted): sealed, never materialized over it, "
         "seal-only refuses to materialize (7), nothing recomputed", plant_exec_dir, want_exit=7,
         want_status="TARGET_EVALUATED", recover_exit=7)
    outside_dir2 = tmp / "outside_dir2"

    def plant_exec_link(D, con, p):
        t = D._orig_eval(con, p)
        outside_dir2.mkdir(exist_ok=True)
        os.symlink(outside_dir2, sbB.p(f"{NS_REL}/evidence/execution"))
        return t
    post("P11 symlink planted at the execution directory after the marker: sealed, nothing written outside",
         plant_exec_link, want_exit=7, want_status="TARGET_EVALUATED", recover_exit=7)
    res["P11b nothing was written through the planted symlink"] = not any(outside_dir2.iterdir()) if outside_dir2.exists() else True
    restore_signals()
    sbB.reset()
    return res


# ------------------------------------------------------------------ F: function-level controls (real repo, no Gamma under I2)
def function_controls() -> dict:
    D = load_driver("c12r2_fn")
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
    C, k1, k2 = F(123457, 1000), F(7978846, 10 ** 7), F(9678830, 10 ** 7)
    res["F08 Lemma G: the frozen tct_rule and the independent re-derivation agree exactly (N11)"] = \
        {j: con["T"].atom_constants_generic(C, k1, k2)[j] for j in D.FIELDS} == D.lemma_g_independent(C, k1, k2)
    real_lg = D.lemma_g_independent
    D.lemma_g_independent = lambda C, k1, k2: {**real_lg(C, k1, k2), "A2": real_lg(C, k1, k2)["A2"] + 1}
    res["F08b Lemma G: a perturbed re-derivation is refused by cell_inputs (N11 guard is live)"] = \
        expect_refusal(D, lambda: D.cell_inputs(con, 306), "LEMMA_G_CROSSCHECK")
    D.lemma_g_independent = real_lg
    res["F08c Lemma G exact at 306 and 305 from the record-bound C_upper (positive)"] = \
        all(D.cell_inputs(con, k)["G"] is not None for k in (305, 306))
    return res


# ------------------------------------------------------------------ G: the r6 generator (synthetic chain in sandbox B)
def r6_controls(sbB: Sandbox, tmp: Path) -> dict:
    res = {}
    out = tmp / "K5_COVERAGE_MAP_R6.json"
    p = subprocess.run([PY, "-I", "-S", "-B", str(R6GEN), "--out", str(out)], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"}, stdin=subprocess.DEVNULL, timeout=900)
    res["G01 refuses in the real repository"] = p.returncode != 0 and "REFUSED" in (p.stdout + p.stderr) and not out.exists()
    D = sys.modules["c12r2_pre"]
    gen = sbB.p(NS_REL) / "code/c12r2_r6_from_adjudication.py"
    exec_rev, adj, adj_rev = (f"{NS_REL}/review/C12R2_EXECUTION_REVIEW.md", f"{NS_REL}/adjudication/C12R2_ADOPTION_ADJUDICATION.md",
                              f"{NS_REL}/review/C12R2_ADJUDICATION_REVIEW.md")
    target_out = sbB.p(f"{NS_REL}/evidence/coverage/K5_COVERAGE_MAP_R6.json")

    def chain(adj_line="CELL306_ADOPTED", adj_set="[306]", s_i2=True, with_adj_rev=True, with_exec_rev=True,
              bad_hash=False, marker=True, after=None, out_path=None, cell=306, marker_at_grant=True, pending_ok=True):
        sbB.reset()
        grant_c = sbB.head()
        body = {"status": "TARGET_EVALUATED", "target_evaluations": 1, "SYNTHETIC": True, "cell": cell,
                "grant": {"grant_commit": grant_c},
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
            sbB.g("update-ref", D.CONSUMED_REF, grant_c if marker_at_grant else "HEAD")
        blob = sbB.g("rev-parse", f"HEAD:{D.RESULT_REL}").stdout.strip()
        sbB.g("update-ref", D.PENDING_REF, blob if pending_ok else sbB.g("rev-parse", f"HEAD:{adj}").stdout.strip())
        if after:
            after()
        o = Path(out_path) if out_path else target_out
        q = subprocess.run([PY, "-I", "-S", "-B", str(gen), "--out", str(o)], capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"}, stdin=subprocess.DEVNULL, timeout=900)
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
                      ("G12 --out wrongly named", {"out_path": str(sbB.p(f"{NS_REL}/evidence/coverage/other.json"))}),
                      ("G13 result for another cell (N7)", {"cell": 307}),
                      ("G14 marker not at the result's grant commit (N7)", {"marker_at_grant": False}),
                      ("G15 committed result is not the pending blob", {"pending_ok": False}),
                      ("G16 --out outside evidence/coverage/ (N7)", {"out_path": str(tmp / "K5_COVERAGE_MAP_R6.json")}),
                      ("G17 the result is not committed at HEAD (N6)",
                       {"after": lambda: (sbB.g("rm", "-q", sys.modules["c12r2_pre"].RESULT_REL),
                                          sbB.commit_all("sandbox remove the result"))})):
        r5_before = r5_path.read_bytes()
        q, o = chain(**kw)
        created = o.exists() and o != r5_path
        res[f"{label}: refused"] = q.returncode != 0 and "REFUSED" in (q.stdout + q.stderr) and not created \
            and r5_path.read_bytes() == r5_before
    sbB.reset()
    return res


# ------------------------------------------------------------------ N: C12-R1 review notes N1-N13, each classified
N_NOTES = {
    "N1": {"note": "protocol overstatements: the verifier's C12 coverage; 'no real I2 value' in sandbox B",
           "classification": "repaired",
           "how": "C12-R2 protocol states exactly what is checked for C12, C12-R1 and C12-R2; sandbox B also decoys C11R_RUNS.json "
                  "and the I2 soundness documents and removes the C11RD run logs, and the claim is narrowed to those files",
           "evidence": ["sandbox B holds only decoy I2 inputs", "A07c2", "A07f", "B09v"]},
    "N2": {"note": "B06v refused for a different reason than its label", "classification": "repaired",
           "how": "B06v relabelled; B10v plants this campaign's own result at the freeze state", "evidence": ["B06v", "B10v"]},
    "N3": {"note": "--review did not bind its own code", "classification": "repaired",
           "how": "--review requires a clean tree (incl. ignored) and code/ + protocol/ identical to the freeze", "evidence": ["B12v"]},
    "N4": {"note": "post-marker residuals: signal window, non-Refusal sealer errors, object store / gpgsign not probed",
           "classification": "repaired",
           "how": "signals ignored before the marker, the wall cap scoped to the evaluation, every post-marker exception handled, "
                  "an object-store write probe and a trial commit object before the marker",
           "evidence": ["run_execute order", "after_marker: every top-level", "P04", "P08", "X13c"]},
    "N5": {"note": "exactly-once is local to the common ref store", "classification": "not applicable (inherent), mitigated",
           "how": "deleting the marker is forbidden by protocol; the identity barrier stops copies, and the pending ref and the "
                  "emergency file are further prior-evaluation evidence the driver refuses on",
           "evidence": ["X03", "B05", "X08", "X08b", "X08c"]},
    "N6": {"note": "missing tests: grant naming a wrong qualification/review commit, code changed after the freeze, r6 with "
                   "the result not at HEAD", "classification": "repaired", "evidence": ["X12 grant variant refused: qualification",
                                                                                         "X12 grant variant refused: review", "X12e", "G17"]},
    "N7": {"note": "r6 --out not confined; no cell / marker-target check", "classification": "repaired",
           "evidence": ["G13", "G14", "G15", "G16"]},
    "N8": {"note": "interpreter flags not enforced", "classification": "repaired", "evidence": ["A21"]},
    "N9": {"note": "grant generator: QUAL_REL not required; inherited environment", "classification": "repaired",
           "evidence": ["the grant generator requires QUAL_REL"]},
    "N10": {"note": "G07 soundness evidence not pinned", "classification": "repaired",
            "how": "C11R_RUNS.json, CELL_306_ADOPTION.md, the C11RD theory and independence audit and the C2 adjudication are "
                   "pinned by sha256 and blob, for the adjudicator to verify", "evidence": ["the G07 soundness evidence is pinned", "preflight PASS"]},
    "N11": {"note": "the Lemma-G check was float-level", "classification": "repaired to the precision the committed evidence permits",
            "how": "C2 recorded G only as floats, so an exact comparison with C2 is impossible; the driver now re-derives Lemma G "
                   "exactly from its statement and refuses any disagreement, and C_upper is bound to the K1 record hash",
            "evidence": ["F08", "F08b", "F08c", "I1 control reproduces C2 exactly for 306"]},
    "N12": {"note": "S_I2 atoms exist in memory before the marker", "classification": "not applicable (by design)",
            "how": "every I2 check must precede consumption (R4); the atoms are never output", "evidence": ["run_execute order"]},
    "N13": {"note": "--review left a temp directory", "classification": "repaired",
            "evidence": ["review mode removes its temporary output"]},
}


# ------------------------------------------------------------------ L: leak scans
def leak_scans() -> dict:
    spec = importlib.util.spec_from_file_location(
        "c12r2q", REPO / f"{CP}p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_qualify.py")
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
        print(f"C12R2 VERIFY REFUSED {e}")
        return 2
    review_tmp = Path(tempfile.mkdtemp(prefix="c12r2rev")) if a.review else None     # N13: removed at the end
    qdir = review_tmp if a.review else NS / "evidence/qualification"
    qdir.mkdir(parents=True, exist_ok=True)
    drv_sha = sha_b(DRIVER.read_bytes())
    report = {"schema": "rebaseguard.p5y.k5.tail-c12r2.qualification.v1", "dry_run": False, "review_mode": a.review,
              "freeze_commit": pre["freeze_commit"], "HEAD": pre["HEAD"], "state": pre["state"],
              "driver_sha256": drv_sha, "verifier_sha256": sha_b(HERE.read_bytes()),
              "r6_generator_sha256": sha_b(R6GEN.read_bytes()),
              "grant_generator_sha256": sha_b((NS / "code/c12r2_grant.py").read_bytes()), "python": sys.version.split()[0]}
    report["S_static"] = static_checks()
    report["R_real"] = real_runs(qdir)
    tmp = Path(tempfile.mkdtemp(prefix="c12r2q"))
    try:
        sbA = Sandbox(tmp, "sbA", pre["freeze_commit"])
        sbB, pins, blobs = make_decoy_sandbox(tmp, pre["freeze_commit"])
        report["sandboxes"] = {"A_commit": sbA.base, "B_parent": sbB.g("rev-parse", f"{sbB.base}^").stdout.strip(),
                               "both_from_the_freeze_commit": sbA.base == pre["freeze_commit"] ==
                               sbB.g("rev-parse", f"{sbB.base}^").stdout.strip(),
                               "B_contains_no_real_I2_file": all(
                                   json.loads(sbB.p(r).read_text()).get("DECOY") is True for r in (C11R_CMP, C11RD_CMP, C11RD_RUNS, C11R_RUNS))
                               and all("DECOY" in sbB.p(r).read_text() for r in (C11RD_THEORY, C11RD_AUDIT))
                               and [f.name for f in sbB.p(C11RD_RUNS).parent.iterdir()] == [Path(C11RD_RUNS).name],
                               "B_scope_note": "the I2 supply inputs, C11R_RUNS.json and the I2 soundness documents are decoys and "
                                               "the C11RD run logs are removed; other pinned documents (e.g. the floor rule) are "
                                               "unchanged and are never read as supply inputs (N1)"}
        report["A_sandbox"] = sandbox_a_controls(sbA)
        report["B_sandbox_cli"] = sandbox_b_cli(sbB, drv_sha, tmp)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):                         # the decoy runs' own status lines
            report["X_flows_decoy"] = flow_tests(sbB, pins, blobs, drv_sha, tmp)
        report["X_flows_decoy_stdout"] = buf.getvalue().splitlines()
        report["G_r6_generator"] = r6_controls(sbB, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    report["F_function_controls"] = function_controls()
    report["L_leak"] = leak_scans()
    if review_tmp is not None:
        shutil.rmtree(review_tmp, ignore_errors=True)
        report["review_tmp_removed"] = not review_tmp.exists()
    D0 = sys.modules["c12r2_pre"]
    report["repository_identity"] = {
        "worktree": str(REPO.resolve()),
        "git_dir": rgit("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip(),
        "common_dir": rgit("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip(),
        "branch": rgit("symbolic-ref", "-q", "HEAD").stdout.strip(),
        "equals_the_driver_qualified_identity": [str(REPO.resolve()), D0.QUALIFIED_GIT_DIR, D0.QUALIFIED_COMMON_DIR,
                                                 D0.QUALIFIED_BRANCH] == [
            str(REPO.resolve()), str(Path(rgit("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip()).resolve()),
            str(Path(rgit("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()).resolve()),
            rgit("symbolic-ref", "-q", "HEAD").stdout.strip()]}
    r5 = json.loads(D0.read_pinned("coverage_r5"))
    report["exactly_once_state"] = {
        "real_target_evaluations": 0,
        "evidence": "no ref under refs/c12r2, refs/c12r1 or refs/c12; no result of C12-R2, C12-R1 or C12 in any tree, history or "
                    "disk; no emergency file; no grant (checked by the preconditions before anything ran, and again below)",
        "markers_and_pending_refs": rgit("for-each-ref", "--format=%(refname)", "refs/c12r2", "refs/c12r1", "refs/c12").stdout.split(),
        "result_path_objects": [r for r in D0.GUARDED_PATHS if os.path.lexists(REPO / r)],
        "grant_exists": os.path.lexists(REPO / D0.GRANT_REL), "seal_exists": bool(rgit("log", "--all", "--format=%H", "--", D0.RESULT_REL).stdout.strip())}
    report["coverage_state"] = {"r5_blob": rgit("rev-parse", f"HEAD:{D0.PINS['coverage_r5'][0]}").stdout.strip(),
                                "r5_union_open_ranges": r5["union_open_ranges"], "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"],
                                "r6_exists": bool(list((REPO / CP).rglob("K5_COVERAGE_MAP_R6*")))}
    report["N_notes"] = N_NOTES
    flat = {**report["S_static"], **report["R_real"]["checks"],
            "sandboxes built from the freeze commit": report["sandboxes"]["both_from_the_freeze_commit"],
            "sandbox B holds only decoy I2 inputs": report["sandboxes"]["B_contains_no_real_I2_file"],
            **{k: v["pass"] for k, v in report["A_sandbox"].items()},
            **{k: v["pass"] for k, v in report["B_sandbox_cli"].items()},
            **report["X_flows_decoy"], **report["G_r6_generator"], **report["F_function_controls"],
            **report["L_leak"]["checks"],
            "the run left the real repository's exactly-once state untouched (no ref, no result object, no grant, no seal)":
                not report["exactly_once_state"]["markers_and_pending_refs"] and not report["exactly_once_state"]["result_path_objects"]
                and not report["exactly_once_state"]["grant_exists"] and not report["exactly_once_state"]["seal_exists"],
            "r5 unchanged (blob f978eeb6) and no r6": report["coverage_state"]["r5_blob"].startswith("f978eeb6")
                and not report["coverage_state"]["r6_exists"],
            "the qualified identity is this worktree": report["repository_identity"]["equals_the_driver_qualified_identity"]}
    for n, rec in N_NOTES.items():
        cited = [k for ev in rec["evidence"] for k in flat if k.startswith(ev)]
        flat[f"{n} classified ({rec['classification']}) and every cited test exists and passed"] = \
            bool(cited) and len({ev for ev in rec["evidence"] if any(k.startswith(ev) for k in flat)}) == len(rec["evidence"]) \
            and all(flat[k] is True for k in cited)
    report["failed"] = sorted(k for k, v in flat.items() if v is not True)
    report["pass"] = not report["failed"]
    report["counts"] = {"checks": len(flat), "passed": sum(v is True for v in flat.values())}
    report["wall_seconds"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(f"C12R2 QUALIFICATION {'PASS' if report['pass'] else 'FAIL'} ({report['counts']['passed']}/{report['counts']['checks']})")
    for k in report["failed"]:
        print("  FAIL", k)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
