"""C12 -- qualification verifier for the frozen cell-306 campaign. Evaluates NO target: no Gamma under any supply that
contains an I2 constant is computed anywhere in this file, in the real repository or in the sandbox.

Sections
  S  static: the driver's structure (the target evaluation is reachable only from `execute`, after the grant, the
     control and the consumed ref, in that order; no print of a computed value; no numpy/flint)
  T  temporal integrity: HEAD is the freeze commit of code/ and protocol/; no result, no consumed ref, no r6
  R  real repository, read-only: preflight PASS; the I1 control reproduces C2's committed record exactly for cell
     306 and for the non-target cell 305; the working tree is untouched by every run
  N  negative controls through the real CLI in a sparse sandbox clone at the freeze commit (planted defects must
     each be refused with their own code; the sandbox baseline must pass first so no refusal is vacuous)
  F  function-level negative controls in-process (mixed supplies, statements, classes, bindings, domain, validation,
     control mismatch, wrong cell, verdict lines)
  G  the frozen r6 generator: refuses in the real repository; on SYNTHETIC sandbox inputs it produces a map that moves
     only (5, 306) and refuses every planted defect
  L  leak scans of this namespace for the original and the independent D1/D2 values (hashed; never printed)

    python3.14 -I -S -B c12_verify.py --out FILE [--keep-sandbox]
"""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import shutil
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
NS_REL = CP + "p5y_k5_tail_c12_cell306_adoption"
DRIVER = NS / "code/c12_cell306.py"
R6GEN = NS / "code/c12_r6_from_adjudication.py"
PY = sys.executable
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": "/var/empty",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
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


def git(repo: Path, *args, env_extra=None) -> subprocess.CompletedProcess:
    env = dict(ENV)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], capture_output=True, text=True, env=env)


def rgit(*args):
    return git(REPO, *args)


def load_driver():
    spec = importlib.util.spec_from_file_location("c12drv", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["c12drv"] = mod
    spec.loader.exec_module(mod)
    return mod


def expect_refusal(fn, code: str) -> bool:
    D = sys.modules["c12drv"]
    try:
        fn()
    except D.Refusal as e:
        return e.code == code
    return False


# ------------------------------------------------------------------ S: static structure of the driver
def static_checks() -> dict:
    src = DRIVER.read_text()
    tree = ast.parse(src)
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    callers = {}
    for name, fn in fns.items():
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                callers.setdefault(node.func.id, set()).add(name)
    ex = fns["run_execute"]

    def first_line(pred):
        lines = [n.lineno for n in ast.walk(ex) if pred(n)]
        return min(lines) if lines else None

    def call_to(name):
        return lambda n: isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
    l_grant, l_control = first_line(call_to("check_grant")), first_line(call_to("control"))
    l_ctlfail = first_line(lambda n: isinstance(n, ast.Constant) and n.value == "CONTROL_FAILED")
    l_prep, l_eval = first_line(call_to("prepare_target")), first_line(call_to("evaluate_target"))
    l_consume = first_line(lambda n: isinstance(n, ast.Name) and n.id == "CONSUMED_REF")
    printed = [ast.unparse(v.value) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "print" for v in ast.walk(n) if isinstance(v, ast.FormattedValue)]
    allowed = {"a.cell", "cid", "e", "status", "ctl['reproduces_C2_exactly']"}
    leaky = sorted(set(printed) - allowed)
    imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
               for a in (n.names if isinstance(n, ast.Import) else [ast.alias(n.module or "")])}
    return {
        "evaluate_target is called only from run_execute": callers.get("evaluate_target") == {"run_execute"},
        "prepare_target is called only from run_execute": callers.get("prepare_target") == {"run_execute"},
        "run_execute order: grant < control < CONTROL_FAILED exit < prepare < consumed ref < evaluate":
            None not in (l_grant, l_control, l_ctlfail, l_prep, l_consume, l_eval)
            and l_grant < l_control < l_ctlfail < l_prep < l_consume < l_eval,
        "no print of a computed value": leaky == [],
        "no numpy/flint import": not ({"numpy", "flint"} & imports),
        "supply refuses mixed implementations before any atom constant": "MIXED_SUPPLY" in ast.unparse(fns["supply"]),
    }


# ------------------------------------------------------------------ T: temporal integrity
def temporal_checks() -> dict:
    head = rgit("rev-parse", "HEAD").stdout.strip()
    frozen_at = rgit("log", "-1", "--format=%H", "--", f"{NS_REL}/code", f"{NS_REL}/protocol").stdout.strip()
    code_dirty = rgit("status", "--porcelain", "--", f"{NS_REL}/code", f"{NS_REL}/protocol").stdout.strip()
    return {"freeze_commit": frozen_at, "HEAD": head,
            "checks": {"HEAD is the freeze commit of code/ and protocol/": head == frozen_at and not code_dirty,
                       "no consumed ref": not rgit("rev-parse", "-q", "--verify", "refs/c12/cell306-target-consumed").stdout.strip(),
                       "no result artifact anywhere": not rgit("log", "--all", "--format=%H", "--",
                                                               f"{NS_REL}/evidence/execution").stdout.strip()
                       and not (NS / "evidence/execution").exists(),
                       "no r6 anywhere": not list((REPO / CP).rglob("K5_COVERAGE_MAP_R6*"))
                       and not rgit("log", "--all", "--format=%H", "--", "*K5_COVERAGE_MAP_R6*").stdout.strip()}}


# ------------------------------------------------------------------ R: real repository, read-only
def run_driver(repo: Path, *argv, out: Path = None) -> tuple:
    cmd = [PY, "-I", "-S", "-B", str(repo / NS_REL / "code/c12_cell306.py"), *argv]
    if out is not None:
        cmd += ["--out", str(out)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"})
    return p.returncode, p.stdout.strip() + p.stderr.strip()[-300:], round(time.time() - t0, 3)


def real_runs(qdir: Path) -> dict:
    before = rgit("status", "--porcelain", "--untracked-files=all").stdout
    out = {}
    for name, argv in (("preflight", ("preflight",)), ("rehearse_306", ("rehearse", "--cell", "306")),
                       ("rehearse_305", ("rehearse", "--cell", "305"))):
        f = qdir / f"{name.upper()}.json"
        code, text, wall = run_driver(REPO, *argv, out=f)
        rec = json.loads(f.read_text()) if f.exists() else None
        out[name] = {"exit": code, "stdout": text, "wall_seconds": wall,
                     "reproduces_C2_exactly": (rec or {}).get("control", {}).get("reproduces_C2_exactly")}
    after = rgit("status", "--porcelain", "--untracked-files=all").stdout
    new = sorted(set(after.splitlines()) - set(before.splitlines()))
    out["checks"] = {
        "preflight PASS": out["preflight"]["exit"] == 0 and "PREFLIGHT PASS" in out["preflight"]["stdout"],
        "I1 control reproduces C2's committed cell-306 record exactly": out["rehearse_306"]["exit"] == 0
        and out["rehearse_306"]["reproduces_C2_exactly"] is True,
        "I1 control reproduces C2's committed cell-305 record exactly (non-target)": out["rehearse_305"]["exit"] == 0
        and out["rehearse_305"]["reproduces_C2_exactly"] is True,
        "the runs changed nothing but the qualification outputs": all(f"{NS_REL}/evidence/qualification/" in ln
                                                                     for ln in new),
    }
    return out


# ------------------------------------------------------------------ N: CLI negative controls in a sandbox
class Sandbox:
    def __init__(self, root: Path, commit: str, dry_run: bool = False):
        self.root, self.commit = root / "sb", commit
        assert str(self.root).startswith(str(root)) and REPO not in self.root.parents and self.root != REPO
        for step in (git(root, "clone", "-q", "--shared", "--no-checkout", str(REPO), str(self.root)),
                     self.g("sparse-checkout", "init", "--no-cone"),
                     self.g("sparse-checkout", "set", "--no-cone", *SPARSE),
                     self.g("checkout", "-q", "--detach", commit)):
            if step.returncode:
                raise SystemExit(f"sandbox setup failed: {step.stderr[:300]}")
        if dry_run:                      # debugging only: stand in for the freeze commit with the working-tree files
            for sub in ("code", "protocol"):
                if (NS / sub).exists():
                    shutil.copytree(NS / sub, self.p(NS_REL) / sub, dirs_exist_ok=True)
            self.commit_all("sandbox stand-in freeze (dry run)")
            self.commit = self.g("rev-parse", "HEAD").stdout.strip()

    def g(self, *args):
        assert self.root != REPO
        return git(self.root, "-c", "user.name=c12-sandbox", "-c", "user.email=sandbox@invalid", *args)

    def reset(self):
        self.g("checkout", "-q", "--detach", "--force", self.commit)
        self.g("reset", "-q", "--hard", self.commit)
        self.g("clean", "-qfdx")
        for ref in self.g("for-each-ref", "--format=%(refname)", "refs/c12").stdout.split():
            self.g("update-ref", "-d", ref)

    def p(self, rel: str) -> Path:
        return self.root / rel

    def commit_all(self, msg: str):
        self.g("add", "-A", "--sparse", ".")
        return self.g("commit", "-q", "--no-verify", "-m", msg)


def cli_controls(sb: Sandbox) -> dict:
    res = {}

    def run(name, setup, argv, want_exit, want_code):
        sb.reset()
        if setup:
            setup()
        code, text, _ = run_driver(sb.root, *argv)
        res[name] = {"argv": list(argv), "exit": code, "out": text[:240],
                     "pass": code == want_exit and (want_code is None or f"REFUSED {want_code}" in text)}

    grant_rel = f"{NS_REL}/authorization/C12_GRANT.json"
    drv_sha = sha_b((sb.p(NS_REL) / "code/c12_cell306.py").read_bytes())

    def write_grant(driver_sha=drv_sha):
        head = sb.g("rev-parse", "HEAD").stdout.strip()
        sb.p(grant_rel).parent.mkdir(parents=True, exist_ok=True)
        sb.p(grant_rel).write_text(json.dumps({"schema": "rebaseguard.p5y.k5.tail-c12.grant.v1", "exactly_once": True,
                                               "driver_sha256": driver_sha, "freeze_commit": head,
                                               "qualification_commit": head, "qualification_review_commit": head}))
        sb.commit_all("sandbox grant")

    def append(rel):
        return lambda: sb.p(rel).write_bytes(sb.p(rel).read_bytes() + b" ")

    reg1 = CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json"
    reg2 = CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"
    c11r = CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json"
    frev = CP + "p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md"
    adjr = CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md"
    result = f"{NS_REL}/evidence/execution/C12_CELL306_RESULT.json"

    def blob_swap():                       # HEAD carries altered bytes; the working tree is restored to the pinned bytes
        good = sb.p(reg1).read_bytes()
        sb.p(reg1).write_bytes(good + b"\n")
        sb.commit_all("sandbox altered registry")
        sb.p(reg1).write_bytes(good)

    def statement_file():
        d = json.loads(sb.p(c11r).read_text())
        d["result"]["per_target"]["C_T"]["statement"]["STATUS"] = "WEAKER"
        sb.p(c11r).write_text(json.dumps(d))

    def plant_result():
        sb.p(result).parent.mkdir(parents=True, exist_ok=True)
        sb.p(result).write_text("{}")

    def plant_result_history():
        plant_result()
        sb.commit_all("sandbox premature result")
        sb.g("rm", "-q", result)
        sb.commit_all("sandbox remove result")

    def plant_consumed():
        sb.g("update-ref", "refs/c12/cell306-target-consumed", "HEAD")

    def plant_r6():
        sb.p(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R6.json").write_text("{}")

    def grant_not_head():
        write_grant()
        sb.p(f"{NS_REL}/SANDBOX_EXTRA").write_text("x")
        sb.commit_all("sandbox commit after grant")

    def untracked():
        sb.p(f"{NS_REL}/UNTRACKED").write_text("x")

    run("N00 sandbox baseline: preflight passes (controls below are not vacuous)", None, ("preflight",), 0, None)
    run("N00b sandbox baseline: the I1 control rehearsal reproduces C2", None, ("rehearse", "--cell", "306"), 0, None)
    run("N01 altered input (ADOPTED_TAIL_INPUTS.json)", append(CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/"
                                                              "ADOPTED_TAIL_INPUTS.json"), ("preflight",), 2, "PIN_MISMATCH")
    run("N02 wrong cell 307 (rehearse)", None, ("rehearse", "--cell", "307"), 2, "CELL_OUT_OF_SCOPE")
    run("N02b wrong cell 308 (rehearse)", None, ("rehearse", "--cell", "308"), 2, "CELL_OUT_OF_SCOPE")
    run("N02c wrong cell 309 (rehearse)", None, ("rehearse", "--cell", "309"), 2, "CELL_OUT_OF_SCOPE")
    run("N02d a cell passed to execute", None, ("execute", "--cell", "307"), 2, "CELL_OUT_OF_SCOPE")
    run("N03 wrong bytes (REGISTRY_C1 replaced by REGISTRY_C2)",
        lambda: sb.p(reg1).write_bytes(sb.p(reg2).read_bytes()), ("preflight",), 2, "PIN_MISMATCH")
    run("N03b wrong blob at HEAD, pinned bytes in the working tree", blob_swap, ("preflight",), 2, "BLOB_MISMATCH")
    run("N04 wrong statement (C11R C_T statement WEAKER)", statement_file, ("preflight",), 2, "PIN_MISMATCH")
    run("N05 missing review (floor r2 review deleted)", lambda: sb.p(frev).unlink(), ("preflight",), 2, "INPUT_MISSING")
    run("N05b missing review (N9 adjudication review deleted)", lambda: sb.p(adjr).unlink(), ("preflight",), 2,
        "INPUT_MISSING")
    run("N05c execute with a grant but no qualification review", write_grant, ("execute",), 2, "REVIEW_MISSING")
    run("N07 premature target artifact in the working tree", plant_result, ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("N07b premature target artifact in history", plant_result_history, ("preflight",), 2, "TARGET_ARTIFACT_EXISTS")
    run("N07c consumed ref already present", plant_consumed, ("rehearse", "--cell", "306"), 2, "CONSUMED")
    run("N08 execute without a grant", None, ("execute",), 2, "GRANT_MISSING")
    run("N09 execute where HEAD is not the grant commit", grant_not_head, ("execute",), 2, "GRANT_INVALID")
    run("N10 execute with a grant for different driver bytes", lambda: write_grant("0" * 64), ("execute",), 2,
        "GRANT_INVALID")
    run("N11 execute on a dirty tree", untracked, ("execute",), 2, "DIRTY_TREE")
    run("N12 an r6 file in the working tree", plant_r6, ("preflight",), 2, "R6_EXISTS")
    sb.reset()
    return res


# ------------------------------------------------------------------ F: function-level controls (in-process)
def function_controls(D) -> dict:
    con = D.load_consumer()
    res = {}
    G = {"A0": F(3), "A1": F(3), "A2": F(3)}
    syn = {"Abar": F(9), "tau": F(2), "C_T": F(3), "D_lo": F(1, 2), "D1": F(1), "D2": F(1)}
    s_i1 = {"impl": "I1", "name": "C1", "values": dict(syn)}
    s_i2 = {"impl": "I2", "name": "I2", "values": dict(syn)}
    res["F01 mixed supply I1 + I2 refused"] = expect_refusal(lambda: D.supply(con, "I1", [s_i1, s_i2], G), "MIXED_SUPPLY")
    res["F01b I1-tagged set in an I2 supply refused"] = expect_refusal(lambda: D.supply(con, "I2", [s_i1], G), "MIXED_SUPPLY")
    res["F01c duplicate set name refused"] = expect_refusal(lambda: D.supply(con, "I1", [s_i1, dict(s_i1)], G),
                                                            "MIXED_SUPPLY")
    for label, patch in (("tau < 1", {"tau": F(1, 2)}), ("C < tau", {"C_T": F(1)}), ("D_lo <= 0", {"D_lo": F(0)}),
                         ("Abar < 1", {"Abar": F(1, 2)}), ("non-exact value", {"D1": 1.0})):
        s = {"impl": "I1", "name": "X", "values": {**syn, **patch}}
        res[f"F02 consumer validation refuses {label}"] = expect_refusal(lambda s=s: D.validate_set(s), "VALIDATION")
    c11r = json.loads(D.read_pinned("c11r_comparison"))
    c11rd = json.loads(D.read_pinned("c11rd_comparison"))
    runs = json.loads(D.read_pinned("c11rd_runs"))
    cov = con["cover"][306]

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
    ]
    for label, (a, b, c), code in cases:
        res[label] = expect_refusal(lambda a=a, b=b, c=c: D.i2_set(a, b, c, cov, con["KM"]), code)
    st = json.loads(D.read_pinned("c11r_statements"))
    res["F04 I2 domain for cell 307 refused"] = expect_refusal(
        lambda: D.i2_block_check(mut(st, ["drift_domain", "cell"], 307), cov, con["KM"]), "I2_DOMAIN")
    res["F04b I2 domain endpoint altered refused"] = expect_refusal(
        lambda: D.i2_block_check(mut(st, ["drift_domain", "e_hi"], "1789/1000"), cov, con["KM"]), "I2_DOMAIN")
    res["F04c I2 domain equals cell 306's cover cell (positive)"] = D.i2_block_check(st, cov, con["KM"]) is None
    want = copy.deepcopy(json.loads(D.read_pinned("c2_forecast"))["cells"]["306"])
    want["Gamma_exact"] = want["Gamma_exact"] + "1"
    res["F05 control mismatch is detected (perturbed expected record)"] = \
        D.control(con, 306, want=want)["reproduces_C2_exactly"] is False
    res["F06 cell 307 refused by cell_inputs"] = expect_refusal(lambda: D.cell_inputs(con, 307), "CELL_OUT_OF_SCOPE")
    res["F06b cell 309 refused by cell_inputs"] = expect_refusal(lambda: D.cell_inputs(con, 309), "CELL_OUT_OF_SCOPE")
    res["F07 verdict line: a second verdict line is refused"] = not D.verdict_ok("# t\nX_ACCEPTED\nX_ACCEPTED\n", "line2", "X_ACCEPTED")
    res["F07b verdict line: wrong line 2 is refused"] = not D.verdict_ok("# t\nX_REJECTED\n", "line2", "X_ACCEPTED")
    res["F07c verdict line: the right line 2 is accepted (positive)"] = D.verdict_ok("# t\nX_ACCEPTED\n", "line2", "X_ACCEPTED")
    return res


# ------------------------------------------------------------------ G: the r6 generator
def r6_controls(sb: Sandbox, tmp: Path) -> dict:
    res = {}
    out = tmp / "r6_real.json"
    p = subprocess.run([PY, "-I", "-S", "-B", str(R6GEN), "--out", str(out)], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"})
    res["G01 refuses in the real repository (no sealed result, no reviews)"] = p.returncode != 0 and \
        "REFUSED" in (p.stdout + p.stderr) and not out.exists()
    gen = sb.p(NS_REL) / "code/c12_r6_from_adjudication.py"
    result = f"{NS_REL}/evidence/execution/C12_CELL306_RESULT.json"

    def synthetic(adj_line="CELL306_ADOPTED", adj_set="[306]", s_i2_pass=True, with_adj_review=True):
        sb.reset()
        body = {"status": "TARGET_EVALUATED", "target_evaluations": 1, "SYNTHETIC": True,
                "control": {"reproduces_C2_exactly": True, "evaluated": {"pass": True}},
                "target": {"evaluated": {"pass": s_i2_pass}}}
        body["sha256"] = sha_b(json.dumps(body, sort_keys=True).encode())
        sb.p(result).parent.mkdir(parents=True, exist_ok=True)
        sb.p(result).write_text(json.dumps(body))
        (sb.p(NS_REL) / "review").mkdir(exist_ok=True)
        (sb.p(NS_REL) / "adjudication").mkdir(exist_ok=True)
        (sb.p(NS_REL) / "review/C12_EXECUTION_REVIEW.md").write_text("# synthetic\nEXECUTION_ACCEPTED\n")
        (sb.p(NS_REL) / "adjudication/C12_ADOPTION_ADJUDICATION.md").write_text(
            f"# synthetic\n{adj_line}\n\n## ADOPTED CELL SET\n\n{adj_set}\n")
        if with_adj_review:
            (sb.p(NS_REL) / "review/C12_ADJUDICATION_REVIEW.md").write_text("# synthetic\nADJUDICATION_ACCEPTED\n")
        sb.commit_all("sandbox synthetic chain")
        sb.g("update-ref", "refs/c12/cell306-target-consumed", "HEAD")
        o = tmp / "r6_sb.json"
        if o.exists():
            o.unlink()
        q = subprocess.run([PY, "-I", "-S", "-B", str(gen), "--out", str(o)], capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty"})
        return q, o

    q, o = synthetic()
    ok = q.returncode == 0 and o.exists()
    if ok:
        r6 = json.loads(o.read_text())
        r5 = json.loads(sb.p(CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json").read_text())
        m5a = {c["cell"]: c["verdict"] for c in r5["per_m"]["5"]["cells"]}
        m5b = {c["cell"]: c["verdict"] for c in r6["per_m"]["5"]["cells"]}
        changed = sorted(k for k in m5a if m5a[k] != m5b[k])
        other_m_same = all(r5["per_m"][m]["cells"] == r6["per_m"][m]["cells"] for m in r5["per_m"] if m != "5")
        ok = changed == [306] and m5b[306] == "PASS" and other_m_same and r6["union_open_ranges"] == [[307, 309]] \
            and r6["K5_COVERAGE_COMPLETE"] is False and r6["inputs"]["predecessor"] == "r5"
    res["G02 synthetic chain: r6 moves exactly (5, 306), keeps 307-309 open, records r5 lineage"] = ok
    for label, kw in (("G03 refuses CELL306_NOT_ADOPTED", {"adj_line": "CELL306_NOT_ADOPTED"}),
                      ("G04 refuses an adopted set other than [306]", {"adj_set": "[306, 307]"}),
                      ("G05 refuses when Gamma(S_I2) >= 0", {"s_i2_pass": False}),
                      ("G06 refuses without the adjudication review", {"with_adj_review": False})):
        q, o = synthetic(**kw)
        res[label] = q.returncode != 0 and "REFUSED" in (q.stdout + q.stderr) and not o.exists()
    sb.reset()
    return res


# ------------------------------------------------------------------ L: leak scans
def leak_scans() -> dict:
    spec = importlib.util.spec_from_file_location(
        "c12q", REPO / f"{CP}p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_qualify.py")
    Q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Q)
    runs = json.loads((REPO / f"{CP}p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/C11RD_RUNS.json").read_text())
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
    ap.add_argument("--keep-sandbox", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="debug before the freeze commit; never a qualification")
    a = ap.parse_args(argv)
    t0 = time.time()
    qdir = (Path(tempfile.mkdtemp(prefix="c12dry")) if a.dry_run else NS / "evidence/qualification")
    qdir.mkdir(parents=True, exist_ok=True)
    report = {"schema": "rebaseguard.p5y.k5.tail-c12.qualification.v1",
              "driver_sha256": sha_b(DRIVER.read_bytes()), "verifier_sha256": sha_b(HERE.read_bytes()),
              "r6_generator_sha256": sha_b(R6GEN.read_bytes()), "python": sys.version.split()[0]}
    report["S_static"] = static_checks()
    report["T_temporal"] = temporal_checks()
    report["R_real"] = real_runs(qdir)
    D = load_driver()
    tmp = Path(tempfile.mkdtemp(prefix="c12q"))
    try:
        sb = Sandbox(tmp, report["T_temporal"]["HEAD"], dry_run=a.dry_run)
        report["dry_run"] = a.dry_run
        report["N_cli_controls"] = cli_controls(sb)
        report["F_function_controls"] = function_controls(D)
        report["G_r6_generator"] = r6_controls(sb, tmp)
    finally:
        if not a.keep_sandbox:
            shutil.rmtree(tmp, ignore_errors=True)
    report["L_leak"] = leak_scans()
    flat = {**report["S_static"], **report["T_temporal"]["checks"], **report["R_real"]["checks"],
            **{k: v["pass"] for k, v in report["N_cli_controls"].items()}, **report["F_function_controls"],
            **report["G_r6_generator"], **report["L_leak"]["checks"]}
    report["failed"] = sorted(k for k, v in flat.items() if v is not True)
    report["pass"] = not report["failed"]
    report["counts"] = {"checks": len(flat), "passed": sum(v is True for v in flat.values())}
    report["wall_seconds"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(f"C12 QUALIFICATION {'PASS' if report['pass'] else 'FAIL'} ({report['counts']['passed']}/{report['counts']['checks']})")
    for k in report["failed"]:
        print("  FAIL", k)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
