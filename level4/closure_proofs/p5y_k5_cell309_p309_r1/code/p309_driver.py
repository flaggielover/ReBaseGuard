"""P309 formal-campaign driver (FC1, FC3-FC6; package rev. 2b section C, as amended by governance/P309_REV2C_AMENDMENTS.md).

Modes
  preflight                      read-only binding and governance checks; never reads a target input
  rehearse                       the full Stage-2 pipeline on MANUFACTURED inputs + real decoy SRK certificates (QC14')
  decoy-stage1a --decoy <name>   Stage 1a on a declared out-of-band decoy cell (QC08, QC10)
  decoy-stage1b --cell <k>       Stage 1b (RLR307 rules) on a declared out-of-band decoy cover cell (QC09)
  execute                        THE single target evaluation: only on the grant commit, after check_grant; never run
                                 before the owner's grant exists
  seal-only                      seals persisted evidence; never computes
  _job                           internal: one Stage-1a / Stage-1b job in a CPU-limited child process

Exit codes: 0 sealed / pass, 2 refused pre-marker, 3 CONTROL_FAILED (not consumed), 4 UNSEALED, 5 sealed failure
status, 6 CONSUMED_UNRECORDED, 7 sealed but not materialized.

Nothing in this file writes a grant.  The exactly-once refs are created only inside the two reviewed exactly-once
sites (_arm_marker, _persist_pending), which first assert an execute context; their names come from the guard module
(code/p309_guard.py) or, in sandbox flows (QC11), from the synthetic test context.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
FNS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import p309_env as E  # noqa: E402  (puts the research impl/verify/code on sys.path; redirects the ledgers)
import p309_guard as G  # noqa: E402

CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell309_p309_r1"
RNS_REL = CP + "p5y_k5_cell309_research_r1"
TARGET_CELL = 309  # q309: literal-ok (the single target of the granted execute mode; checked against the grant)
GEOMETRY = {"h": "5/1", "k": "1/2"}   # the adapter's and the certificates' exact string form
FIELDS = ("A0", "A1", "A2")
ARGS = ("Abar", "tau", "C_T", "D_lo", "D1", "D2")
FROZEN_DIRS = ("code", "config", "fc2", "freeze", "tests", "verify", "governance")
FREEZE_REL = NS_REL + "/freeze/P309_FREEZE.json"
MANIFEST_REL = NS_REL + "/freeze/P309_FREEZE_MANIFEST.json"
QUAL_DIR_REL = NS_REL + "/qualification/"
QUAL_REL = QUAL_DIR_REL + "P309_QUALIFICATION.json"
QREVIEW_PREFIX = NS_REL + "/reviews/REVIEW_QUALIFICATION_P309"
QREVIEW_REL = QREVIEW_PREFIX + ".md"
CHECKPOINT_LEDGER_REL = NS_REL + "/ledger/CHECKPOINT_PUSHES.jsonl"
EXEC_DIR_REL = NS_REL + "/evidence/execution"
RESULT_NAME = "P309_RESULT.json"
RESULT_REL = EXEC_DIR_REL + "/" + RESULT_NAME
GUARDED_PATHS = (EXEC_DIR_REL, RESULT_REL, RESULT_REL + ".tmp", RESULT_REL + ".partial")
EMERGENCY_NAME = "p309-emergency-result.json"
PRIOR_MARKER_PATTERNS = ("refs/p5y-k5-cell309", "refs/p309-cell309", "refs/rlr-tail/")  # q309: literal-ok (ref prefixes, refusal only)
R6_NAME = "K5_COVERAGE_MAP_R6"
WORKERS = 4
STAGE1A_LADDER = (8, 10, 12)
STAGE1A_INDICES = (1, 2, 3, 4)
STAGE1A_BUDGET_S = 48 * 3600          # start threshold (protocol 2.5)
STAGE1A_JOB_LIMIT_S = 12 * 3600       # per-job CPU limit (protocol 2.5)
STAGE1B_BUDGET_S = 21600              # protocol 3 (307 precedent)
STAGE1B_JOB_LIMIT_S = 21600           # rev. 2c: the Stage-1b per-job limit equals its total budget
VERIFIER_N, VERIFIER_DEPTH = 8, 24
PRE_CAP_S = 1800
SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)  # q309: literal-ok (seconds of delay, not drifts)
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}
SCHEMA = "rebaseguard.p5y.k5.cell309-p309-r1.result.v1"  # q309: literal-ok (result schema name)
DECOY_STAGE1A = {   # declared (research SRK_DECOY_DECLARATION_A2 cell family); the h3 cell is the FC2 TEST band
    "a2_h5": {"h": "5/1", "k": "1/2", "cell": ["1/2", "37/72"]},
}
DECOY_STAGE1B_CELLS = (297, 316)       # the RLR307 decoy cover cells (declared by the 307 pattern; outside the band)
VARIANT_REL = NS_REL + "/verify/srk_verify_indep_scoped.py"


class Refusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class IndependentCheckFailed(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------------ small helpers
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def git(*args, repo: Path | None = None, env_extra=None, input_bytes=None):
    env = dict(ENV)
    env.update(env_extra or {})
    cmd = ["/usr/bin/git", "--no-replace-objects", "-C", str(repo or REPO), *args]
    if input_bytes is not None:
        p = subprocess.run(cmd, input=input_bytes, capture_output=True, env=env)
        return subprocess.CompletedProcess(p.args, p.returncode, p.stdout.decode(errors="replace"),
                                           p.stderr.decode(errors="replace"))
    return subprocess.run(cmd, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


# ------------------------------------------------------------------------------------------------ execution contexts
class ExecContext:
    """Names and repository of one execution.  PRODUCTION: this repository and the guard's production names.
    Sandbox (QC11 only): a sandbox clone and the synthetic TEST names; never the production names."""

    def __init__(self, kind: str, repo: Path, guard_ctx, marker_ref: str, pending_ref: str, namespace: str,
                 branch_ref: str | None):
        self.kind, self.repo, self.guard_ctx = kind, Path(repo), guard_ctx
        self.marker_ref, self.pending_ref, self.namespace, self.branch_ref = marker_ref, pending_ref, namespace, branch_ref


def production_context() -> ExecContext:
    br = git("symbolic-ref", "-q", "HEAD").stdout.strip() or None
    return ExecContext("PRODUCTION", REPO, G.PRODUCTION, G.PRODUCTION.marker_ref, G.PRODUCTION.pending_ref,
                       G.PRODUCTION.ref_namespace, br)


def sandbox_context(sandbox: Path) -> ExecContext:
    tc = G.TestContext(sandbox)                    # refuses this repository, its worktrees and production refs
    br = git("symbolic-ref", "-q", "HEAD", repo=tc.repo).stdout.strip() or None
    return ExecContext("SANDBOX", tc.repo, tc, tc.marker_ref, tc.pending_ref, tc.ref_namespace, br)


def _assert_execute_context(ctx: ExecContext) -> None:
    """First statement of every exactly-once site: the context is one of the two kinds, its names are the guard's
    own names for that kind, and the process runs in execute (or seal-only) mode."""
    if _MODE.get("mode") not in ("execute", "seal-only"):
        raise Refusal("NOT_EXECUTE_MODE", "an exactly-once site outside execute / seal-only")
    if ctx.kind == "PRODUCTION":
        ok = (ctx.guard_ctx is G.PRODUCTION and ctx.marker_ref == G.PRODUCTION.marker_ref
              and ctx.pending_ref == G.PRODUCTION.pending_ref and ctx.repo == REPO)
    elif ctx.kind == "SANDBOX":
        ok = (type(ctx.guard_ctx) is G.TestContext and ctx.marker_ref == G.TEST_MARKER
              and ctx.pending_ref == G.TEST_PENDING_REF and ctx.repo != REPO)
    else:
        ok = False
    if not ok:
        raise Refusal("CONTEXT", "exactly-once names do not match the context kind")


_MODE: dict = {}


# ------------------------------------------------------------------------------------------------ frozen pins
def load_manifest(repo: Path = REPO) -> dict:
    raw = (repo / MANIFEST_REL).read_bytes()
    m = json.loads(raw)
    if m.get("schema") != "P309_FREEZE_MANIFEST/1":
        raise Refusal("MANIFEST", "not a P309 freeze manifest")
    m["_sha256"] = sha(raw)
    return m


def pin_table(m: dict) -> dict:
    out = {}
    for sec in ("code_pins", "data_pins"):
        for p in m[sec]:
            out[p["path"]] = (p["sha256"], p["git_blob"])
    return out


def read_pinned(pins: dict, rel: str, repo: Path = REPO) -> bytes:
    if rel not in pins:
        raise Refusal("NOT_PINNED", rel)
    try:
        raw = (repo / rel).read_bytes()
    except OSError:
        raise Refusal("INPUT_MISSING", rel)
    if sha(raw) != pins[rel][0] or git_blob_id(raw) != pins[rel][1]:
        raise Refusal("PIN_MISMATCH", rel)
    return raw


def data_rel(m: dict, role: str) -> str:
    for p in m["data_pins"]:
        if p.get("role") == role:
            return p["path"]
    raise Refusal("NOT_PINNED", f"data role {role}")


def check_bindings(m: dict, repo: Path = REPO) -> dict:
    """every pin: sha256 and git blob of the worktree bytes, and the committed blob at HEAD."""
    pins = pin_table(m)
    bad = []
    for rel, (s, b) in pins.items():
        try:
            raw = (repo / rel).read_bytes()
        except OSError:
            bad.append(("missing", rel))
            continue
        if sha(raw) != s or git_blob_id(raw) != b:
            bad.append(("bytes", rel))
        elif git("rev-parse", f"HEAD:{rel}", repo=repo).stdout.strip() != b:
            bad.append(("commit", rel))
    if bad:
        raise Refusal("PIN_MISMATCH", f"{len(bad)} pins: {bad[:3]}")
    rt = m["runtime"]
    import platform
    if (platform.python_version(), platform.python_implementation()) != (rt["python"], rt["implementation"]):
        raise Refusal("RUNTIME", "interpreter differs from the frozen runtime")
    return {"pins": len(pins), "manifest_sha256": m["_sha256"]}


def check_flags() -> None:
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise Refusal("INTERPRETER_FLAGS", "execute and seal-only require python3 -I -S -B")


# ------------------------------------------------------------------------------------------------ governance checks
def freeze_commit(repo: Path = REPO) -> str:
    return git("log", "-1", "--format=%H", "--", *(f"{NS_REL}/{d}" for d in FROZEN_DIRS), repo=repo).stdout.strip()


def check_not_evaluated(ctx: ExecContext) -> None:
    refs = git("for-each-ref", "--format=%(refname)", repo=ctx.repo).stdout.split()
    hits = [r for r in refs if r.startswith(ctx.namespace) or any(r.startswith(p) for p in PRIOR_MARKER_PATTERNS)]
    if hits:
        raise Refusal("CONSUMED", f"a ref exists under a marker namespace: {hits[:2]}")
    names = git("ls-tree", "-r", "--name-only", "HEAD", repo=ctx.repo).stdout.split()
    if RESULT_REL in names or os.path.lexists(ctx.repo / RESULT_REL) or git(
            "log", "--all", "--format=%H", "--", RESULT_REL, repo=ctx.repo).stdout.strip():
        raise Refusal("TARGET_ARTIFACT_EXISTS", RESULT_REL)
    if os.path.lexists(git_dir(ctx) / EMERGENCY_NAME):
        raise Refusal("TARGET_ARTIFACT_EXISTS", "emergency evidence file in the git dir")


def git_dir(ctx: ExecContext) -> Path:
    return Path(git("rev-parse", "--path-format=absolute", "--git-dir", repo=ctx.repo).stdout.strip())


def check_result_paths(ctx: ExecContext) -> None:
    for rel in GUARDED_PATHS:
        try:
            st = os.lstat(ctx.repo / rel)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise Refusal("RESULT_PATH_OCCUPIED", f"{rel}: unreadable ({exc.__class__.__name__})")
        raise Refusal("RESULT_PATH_OCCUPIED", f"{rel} holds a {stat.filemode(st.st_mode)} object")
    cur = ctx.repo
    for part in (NS_REL + "/evidence").split("/"):
        cur = cur / part
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            break
        if not stat.S_ISDIR(st.st_mode):
            raise Refusal("RESULT_PATH_OCCUPIED", f"{cur} is not a plain directory")


def check_clean(ctx: ExecContext) -> None:
    if git("status", "--porcelain", "--untracked-files=all", repo=ctx.repo).stdout.strip():
        raise Refusal("DIRTY_TREE")
    if git("status", "--porcelain", "--ignored", "--untracked-files=all", "--", NS_REL, repo=ctx.repo).stdout.strip():
        raise Refusal("IGNORED_OBJECT", "an ignored or untracked object exists in the campaign namespace")


def check_governance_state(m: dict, repo: Path = REPO) -> dict:
    names = git("ls-tree", "-r", "--name-only", "HEAD", repo=repo).stdout.split()
    if any(Path(n).name.startswith(R6_NAME) for n in names):
        raise Refusal("R6_EXISTS")
    if git("log", "--all", "--format=%H", "--", f"*{R6_NAME}*", repo=repo).stdout.strip():
        raise Refusal("R6_IN_HISTORY")
    r5 = data_rel(m, "coverage_r5")
    read_pinned(pin_table(m), r5, repo)                  # r5 byte-identical to its pin (not otherwise read)
    return {"r6": "absent", "r5": "pinned bytes unchanged"}


def verdict_ok(text: str, expected: str) -> bool:
    lines = text.splitlines()
    return len(lines) > 1 and lines[1].strip() == expected and sum(1 for ln in lines if ln.strip() == expected) == 1


def _only(commit: str, allowed, repo: Path, prefixes=()) -> list:
    """the paths a commit changes that are neither listed exactly nor under one of the prefixes (empty = OK)."""
    files = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit, repo=repo).stdout.split()
    if not files:
        return ["<no paths>"]
    return [f for f in files if f not in allowed and not any(f.startswith(p) for p in prefixes)]


def check_grant(own_sha: str, m: dict, ctx: ExecContext) -> dict:
    """rev. 2c chain: freeze F -> qualification Q -> qualification review Rv -> grant G, where between them only
    checkpoint-record commits (touching only ledger/CHECKPOINT_PUSHES.jsonl) may occur; G touches only the grant."""
    repo = ctx.repo
    gp = ctx.guard_ctx.grant_path
    head = git("rev-parse", "HEAD", repo=repo).stdout.strip()
    raw = git("show", f"HEAD:{gp}", repo=repo)
    if raw.returncode:
        raise Refusal("GRANT_MISSING")
    if os.path.islink(repo / gp):
        raise Refusal("GRANT_INVALID", "the grant is a symlink")
    if git("log", "-1", "--format=%H", "--", gp, repo=repo).stdout.strip() != head:
        raise Refusal("GRANT_INVALID", "HEAD is not the grant commit")
    if _only(head, (gp,), repo):
        raise Refusal("GRANT_INVALID", "the grant commit changes more than the grant")
    if len(git("rev-list", "--parents", "-n", "1", head, repo=repo).stdout.split()) != 2:
        raise Refusal("GRANT_INVALID", "the grant commit must have exactly one parent")
    try:
        g = json.loads(raw.stdout)
        if not isinstance(g, dict):
            raise ValueError("not an object")
    except ValueError:
        raise Refusal("GRANT_INVALID", "the grant does not parse as a JSON object") from None
    if ctx.kind == "PRODUCTION" and (g.get("schema") != "P309_GRANT/1" or g.get("cell") != TARGET_CELL or
                                     g.get("closure_only") is not True or g.get("executions_authorized") != 1):
        raise Refusal("GRANT_INVALID", "schema / cell / scope / executions")
    if g.get("driver_sha256") != own_sha:
        raise Refusal("GRANT_INVALID", "driver bytes differ from the granted driver")
    if g.get("frozen_manifest_sha256") != m["_sha256"]:
        raise Refusal("GRANT_INVALID", "the grant does not bind the frozen manifest")
    chain, c = [], head
    for _ in range(64):                                  # walk single parents back to the freeze commit
        pl = git("rev-list", "--parents", "-n", "1", c, repo=repo).stdout.split()
        if len(pl) != 2:
            raise Refusal("GRANT_INVALID", "a merge or root commit inside the chain")
        c = pl[1]
        if c == g.get("frozen_commit"):
            break
        if not _only(c, (CHECKPOINT_LEDGER_REL,), repo):
            continue                                     # a checkpoint-record commit: allowed anywhere in the chain
        chain.append(c)
        if len(chain) > 2:
            raise Refusal("GRANT_INVALID", "more than qualification and review between freeze and grant")
    else:
        raise Refusal("GRANT_INVALID", "the chain never reaches the named freeze commit")
    if len(chain) != 2:
        raise Refusal("GRANT_INVALID", "the chain must be freeze -> qualification -> review -> grant")
    review_c, qual_c = chain
    fz = freeze_commit(repo)
    if fz != g.get("frozen_commit") or (g.get("qualification_commit"), g.get("qualification_review_commit")) != (
            qual_c, review_c):
        raise Refusal("GRANT_INVALID", "the grant does not name the chain commits")
    if _only(review_c, (), repo, prefixes=(QREVIEW_PREFIX,)):
        raise Refusal("GRANT_INVALID", "the review commit changes more than the review files")
    if _only(qual_c, (NS_REL + "/ledger/ZERO_TARGET_LEDGER.jsonl", NS_REL + "/ledger/EXPOSURE_LEDGER.jsonl"), repo,
             prefixes=(QUAL_DIR_REL,)) or QUAL_REL not in git("diff-tree", "--no-commit-id", "--name-only", "-r",
                                                                qual_c, repo=repo).stdout.split():
        raise Refusal("GRANT_INVALID", "the qualification commit is not qualification evidence only")
    try:
        q = json.loads(git("show", f"{qual_c}:{QUAL_REL}", repo=repo).stdout or "{}")
    except ValueError:
        q = {}
    if q.get("pass") is not True or q.get("freeze_commit") != fz:
        raise Refusal("GRANT_INVALID", "the qualification report is not a PASS at the freeze commit")
    rv = git("show", f"{review_c}:{QREVIEW_REL}", repo=repo).stdout
    if not verdict_ok(rv, "QUALIFICATION_ACCEPTED"):
        raise Refusal("REVIEW_VERDICT", "qualification review is not QUALIFICATION_ACCEPTED")
    if git("merge-base", "--is-ancestor", fz, head, repo=repo).returncode:
        raise Refusal("GRANT_INVALID", "the freeze commit is not an ancestor")
    later = git("log", "--format=%H", f"{fz}..{head}", "--", *(f"{NS_REL}/{d}" for d in FROZEN_DIRS),
                repo=repo).stdout.split()
    if later:
        raise Refusal("GRANT_INVALID", "a frozen directory changed after the freeze")
    return {"grant_commit": head, "grant_sha256": sha(raw.stdout.encode()), "freeze_commit": fz,
            "qualification_commit": qual_c, "qualification_review_commit": review_c,
            "cell_interval": g.get("cell_interval"), "drift_hull_Ew": g.get("drift_hull_Ew")}


# ------------------------------------------------------------------------------------------------ consumer (Stage 2)
def exec_module(raw: bytes, path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


CONSUMER = {"tct_rule": CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
            "tail_forecast_r2": CP + "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
            "c2_forecast_code": CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
            "deflated_consume": CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
            "adapter": CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py"}


def load_consumer(m: dict, repo: Path = REPO) -> dict:
    """the 307 pattern: the pinned consumer loaded by bytes (no import statement), cover from the pinned cells.json.
    No record of any cell is read here."""
    pins = pin_table(m)
    tct = exec_module(read_pinned(pins, CONSUMER["tct_rule"], repo), repo / CONSUMER["tct_rule"], "tct_rule")
    fc = exec_module(read_pinned(pins, CONSUMER["tail_forecast_r2"], repo), repo / CONSUMER["tail_forecast_r2"],
                     "p309_tail_forecast_r2")
    if fc.T is not tct:
        raise Refusal("MODULE_IDENTITY", "tail_forecast_r2 did not bind the pinned tct_rule")
    c2f = exec_module(read_pinned(pins, CONSUMER["c2_forecast_code"], repo), repo / CONSUMER["c2_forecast_code"],
                      "p309_c2_d5_forecast")
    dc = exec_module(read_pinned(pins, CONSUMER["deflated_consume"], repo), repo / CONSUMER["deflated_consume"],
                     "p309_deflated_consume")
    if (dc.K1_BOUND, dc.K2_BOUND) != (c2f.K1_BOUND, c2f.K2_BOUND):
        raise Refusal("KAPPA", "consumer kappa differs from C2's local copy")
    R = tct.load_frozen("tc_rule", tct.FROZEN["tc_rule"][1])
    adapter = fc.module("adapter", "p309_fc_adapter")
    if sha((repo / fc.PINS["adapter"][0]).read_bytes()) != pins[CONSUMER["adapter"]][0]:
        raise Refusal("PIN_MISMATCH", "consumption adapter")
    comp = adapter.frozen_components(repo)
    KM = comp["loader"]
    adapter.bound_file(repo / adapter.CELLS_JSON, adapter.CELLS_SHA256, "cells.json")
    if adapter.CELLS_SHA256 != pins[data_rel(m, "cells_json")][0] or \
            adapter.MANIFEST_SHA256 != pins[data_rel(m, "record_manifest")][0]:
        raise Refusal("PIN_MISMATCH", "adapter bindings differ from the campaign's")
    cover = KM.load_cells(repo / adapter.CELLS_JSON, adapter.DETECTOR)
    return {"T": tct, "FC": fc, "C2F": c2f, "DC": dc, "R": R, "KM": KM, "adapter": adapter,
            "cover": {c["index"]: c for c in cover}}


def _ind():
    """the RLR307 independent reconstruction (pinned bytes; loaded without an import statement)."""
    return sys.modules.get("p309_rlr307_independent")


def load_rlr307(m: dict, repo: Path = REPO) -> dict:
    pins = pin_table(m)
    out = {}
    for name in ("rlr307_independent", "rlr307_stage1", "rlr307_pinned"):
        rel = CP + f"p5y_k5_cell307_rlr_r1/code/{name}.py"
        out[name] = exec_module(read_pinned(pins, rel, repo), repo / rel, f"p309_{name}")
    return out


def cell_inputs(con: dict, m: dict, k: int, repo: Path = REPO, *, _execute_only: bool = True) -> dict:
    """the 307 pattern: measurement + adopted inputs + record manifest binding for the target cell ONLY.
    Called only from the post-grant, pre-marker historical control and from Stage 2 (execute)."""
    if k != TARGET_CELL or _MODE.get("mode") != "execute":
        raise Refusal("CELL_OUT_OF_SCOPE", "target inputs are read only in execute mode, after check_grant")
    pins = pin_table(m)
    T, FC, R = con["T"], con["FC"], con["R"]
    meas = json.loads(read_pinned(pins, data_rel(m, "tct_inputs_target"), repo))
    adopted = json.loads(read_pinned(pins, data_rel(m, "adopted_inputs"), repo))
    manifest = json.loads(read_pinned(pins, data_rel(m, "record_manifest"), repo))
    a = adopted["cells"][str(k)]
    want = manifest["files"].get(f"k4_records/aux5_CUSUM_{k}_256.json")
    if meas["cell"] != k or not meas["identity_gate"]["identical"] or meas["order3_fields_present"]:
        raise Refusal("MEASUREMENT", "not a gated order-3-free replay")
    if not (want and meas["k1_record_sha256"] == a["record_sha256"] == want):
        raise Refusal("RECORD_BINDING", "measurement, adopted inputs and manifest disagree")
    if adopted["manifest_sha256"] != pins[data_rel(m, "record_manifest")][0]:
        raise Refusal("RECORD_BINDING", "adopted inputs not bound to the adopted export manifest")
    meas["C_upper"] = str(FC.rat(a["C_upper"]))
    rec_view = {"eps_cell_refined": a["eps_cell_refined"], "m": a["m"]}
    if not T.derived_identity_gate(R, meas, rec_view)["pass"]:
        raise Refusal("IDENTITY_GATE")
    kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    Gs = T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])
    if {j: Gs[j] for j in FIELDS} != _ind().lemma_g(F(meas["C_upper"]), kn[1], kn[2]):
        raise Refusal("LEMMA_G_CROSSCHECK")
    return {"meas": meas, "aux": a["auxiliary_evidence"], "ad": a["m"]["5"], "cov": con["cover"][k], "G": Gs}


def s_i1(con: dict, m: dict, k: int, ci: dict, repo: Path = REPO) -> tuple:
    pins = pin_table(m)
    sup = {"G": ci["G"]}
    for name, role in (("C1", "registry_c1"), ("C2", "registry_c2")):
        blocks = [b for b in json.loads(read_pinned(pins, data_rel(m, role), repo))["blocks"] if b["cell"] == k]
        if len(blocks) != 1 or blocks[0].get("certified") is not True:
            raise Refusal("I1_BLOCK", name)
        v = {x: F(blocks[0][x]) for x in ARGS}
        if not (v["D_lo"] > 0 and v["tau"] >= 1 and v["C_T"] >= v["tau"] and v["Abar"] >= 1):
            raise Refusal("VALIDATION", name)
        args = tuple(v[x] for x in ARGS)
        frozen = con["DC"].atom_constants_r2(*args)
        ind = _ind().dv_prime_r2(*args, con["C2F"].K1_BOUND, con["C2F"].K2_BOUND)
        if {j: frozen[j] for j in FIELDS} != con["C2F"]._atom_independent(*args) or \
                {j: frozen[j] for j in FIELDS} != ind:
            raise Refusal("ATOM_CROSSCHECK", name)
        sup[name] = frozen
    A, prov = con["C2F"].combine(sup)
    if {j: A[j] for j in FIELDS} != _ind().componentwise_min(sup):
        raise Refusal("COMBINE_CROSSCHECK")
    return A, prov, sup


class _SRKShim:
    """Injection into the pinned c2_d5_forecast.direct (U2-check U4(i)): direct is called UNCHANGED; its
    tail_enclosure call returns the SRK enclosure computed beforehand from exactly the same arguments, and its internal
    crosscheck returns the same pair (so it is vacuous for SRK).  The genuine TC-T crosscheck is performed separately,
    before, on the pinned tct_rule (evaluate_srk)."""

    def __init__(self, T, lo, hi, obj, args):
        self._T, self._lohi, self._obj, self._args = T, (lo, hi), obj, args

    def tail_enclosure(self, R, meas, aux, A, m, order3=None):
        if (R, meas, aux, A, m, order3) != self._args:
            raise IndependentCheckFailed("direct() called the enclosure with other arguments than the SRK input")
        return self._lohi[0], self._lohi[1], self._obj

    def tail_enclosure_crosscheck(self, meas, aux, A, m, order3=None):
        return self._lohi


def evaluate_srk(con: dict, ci: dict, A: dict, cell: tuple, gate_result, verifier_id: str) -> dict:
    """Stage 2 (protocol 4): TC-T enclosure with S (pinned tct_rule, with its crosscheck), the SRK adapter (exact
    reproduction gate, binding to cell/geometry/kernel/verifier), then the pinned direct clause via the shim."""
    import srk_adapter as AD
    T, R = con["T"], con["R"]
    lo, hi, obj = T.tail_enclosure(R, ci["meas"], ci["aux"], A, 5, None)
    if (lo, hi) != T.tail_enclosure_crosscheck(ci["meas"], ci["aux"], A, 5, None):
        raise IndependentCheckFailed("theorem TC-T crosscheck disagrees")
    H = AD.srk_enclosure(ci["meas"], A, 5, cell, gate_result, obj, (lo, hi), R.coefficients, verifier_id=verifier_id)
    shim = _SRKShim(T, H["lo"], H["hi"], obj, (R, ci["meas"], ci["aux"], A, 5, None))
    res = con["C2F"].direct(shim, R, ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    return {"Gamma_exact": fs(res["Gamma"]), "pass": bool(res["Gamma"] < 0), "H_SRK_exact": [fs(H["lo"]), fs(H["hi"])],
            "H_TCT_exact": [fs(lo), fs(hi)], "M_after_exact": fs(res["M"]), "A_exact": {j: fs(A[j]) for j in FIELDS},
            "per_r": {str(r): {k: (fs(v) if isinstance(v, F) else v) for k, v in d.items()}
                      for r, d in H["per_r"].items()}}


def evaluate_tct(con: dict, ci: dict, A: dict) -> dict:
    res = con["C2F"].direct(con["T"], con["R"], ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    return {"Gamma_exact": str(res["Gamma"]), "pass": bool(res["pass"]), "H_exact": [str(res["lo"]), str(res["hi"])],
            "M_after_exact": str(res["M"]), "A_exact": {j: str(A[j]) for j in FIELDS}}


def historical_control(con: dict, m: dict, cell: tuple, verifier_id: str, repo: Path = REPO) -> dict:
    """post-grant, pre-marker (protocol 4): (a) the 307-pattern control with S_I1 through the unchanged direct;
    (b) the P309 pipeline with the EMPTY GateResult and S = S_I1.  Both must reproduce C2's committed record for the
    target cell byte-identically."""
    import srk_gate as GT
    ci = cell_inputs(con, m, TARGET_CELL, repo)
    A, prov, sup = s_i1(con, m, TARGET_CELL, ci, repo)
    got = evaluate_tct(con, ci, A)
    fc = json.loads(read_pinned(pin_table(m), data_rel(m, "c2_forecast"), repo))
    want, wsup = fc["cells"][str(TARGET_CELL)], fc["supplies"][str(TARGET_CELL)]
    empty = GT.GateResult.empty(cell[0], cell[1], dict(GEOMETRY), (1, 2, 3, 4))
    pipe = evaluate_srk(con, ci, A, cell, empty, verifier_id)
    fields = {"Gamma_exact": got["Gamma_exact"] == want["Gamma_exact"], "A_exact": got["A_exact"] == want["A_exact"],
              "provenance": prov == want["provenance"], "H_exact": got["H_exact"] == want["H_exact"],
              "M_after_exact": got["M_after_exact"] == want["M_after_exact"], "pass": got["pass"] == want["pass"],
              "per_supply": sorted(wsup) == sorted(sup) and all(float(sup[n][j]) == wsup[n][j]
                                                                for n in sup for j in FIELDS),
              "pipeline_EMPTY_Gamma": F(pipe["Gamma_exact"]) == F(want["Gamma_exact"]),
              "pipeline_EMPTY_H": [F(x) for x in pipe["H_SRK_exact"]] == [F(x) for x in want["H_exact"]]}
    body = {"cell": TARGET_CELL, "fields": fields, "reproduces_C2_exactly": all(fields.values())}
    return {**body, "digest": sha(canon(body)), "_ci": ci, "_A": A, "_prov": prov}


# ------------------------------------------------------------------------------------------------ Stage 1a (SRK)
def stage1a_jobs() -> list:
    """rung-major (protocol 2.5): every sub-block at d = 8, then 10, then 12; b1..b4 in order within a rung."""
    return [(j, d) for d in STAGE1A_LADDER for j in range(4)]


def _proc_cpu(pid: int) -> float:
    try:
        f = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
        return (int(f[11]) + int(f[12])) / os.sysconf("SC_CLK_TCK")
    except (OSError, IndexError, ValueError):
        return 0.0


def run_jobs(specs: list, *, budget_s: float, job_limit_s: float, workers: int, runner=None) -> dict:
    """Start-threshold budget (protocol 2.5 / 3): jobs are started in the given order while the cumulative CPU
    (finished + running, user + system) is below budget_s; a job exceeding job_limit_s is terminated (RLIMIT_CPU) and
    its output discarded.  Never raises for budget reasons.  `runner(spec)` -> Popen (tests inject stubs)."""
    runner = runner or _spawn_job
    pending, running, done = list(enumerate(specs)), {}, {}
    cum, log = 0.0, []
    while pending or running:
        while pending and len(running) < workers:
            live = sum(_proc_cpu(p.pid) for p, _, _ in running.values())
            if cum + live >= budget_s:
                break
            idx, spec = pending.pop(0)
            out = tempfile.NamedTemporaryFile(prefix="p309job", suffix=".json", delete=False)
            out.close()
            p = runner(dict(spec, _out=out.name, _limit=job_limit_s))
            running[p.pid] = (p, idx, out.name)
            log.append({"event": "start", "job": idx, "utc": utc(), "cum_cpu_s": round(cum, 3)})
        if not running:
            break
        pid, status, ru = os.wait4(-1, 0)
        if pid not in running:
            continue
        p, idx, outp = running.pop(pid)
        cpu = ru.ru_utime + ru.ru_stime
        cum += cpu
        sig = os.WTERMSIG(status) if os.WIFSIGNALED(status) else None
        rc = os.WEXITSTATUS(status) if os.WIFEXITED(status) else None
        if sig in (signal.SIGXCPU, signal.SIGKILL) or cpu >= job_limit_s:
            done[idx] = {"kind": "TERMINATED_JOB_LIMIT", "cpu_s": round(cpu, 3), "signal": sig}
        elif rc == 0:
            try:
                done[idx] = dict(json.loads(Path(outp).read_text()), cpu_s=round(cpu, 3))
            except (OSError, ValueError) as exc:
                done[idx] = {"kind": "JOB_EXCEPTION", "error": f"unreadable job output ({type(exc).__name__})",
                             "cpu_s": round(cpu, 3)}
        else:
            done[idx] = {"kind": "JOB_EXCEPTION", "error": f"exit {rc} signal {sig}", "cpu_s": round(cpu, 3)}
        try:
            os.unlink(outp)
        except OSError:
            pass
        log.append({"event": "end", "job": idx, "utc": utc(), "kind": done[idx]["kind"], "cpu_s": round(cpu, 3)})
    not_started = [idx for idx, _ in pending]
    return {"results": done, "not_started": not_started, "cpu_s_total": round(cum, 3), "log": log,
            "budget_s": budget_s, "job_limit_s": job_limit_s}


def _spawn_job(spec: dict):
    lim = int(spec["_limit"])

    def limit():
        resource.setrlimit(resource.RLIMIT_CPU, (lim, lim + 5))
        for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
            signal.signal(s, signal.SIG_IGN)
    return subprocess.Popen([sys.executable, "-B", str(HERE), "_job", json.dumps(spec)], preexec_fn=limit,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            env={**ENV, "PYTHONHASHSEED": "0"})


def job_stage1a(spec: dict) -> dict:
    """one (sub-block, rung) job: run_block with ladder=(d,) (per-rung serialization), certificate_json per index,
    in-process verdicts of the pinned band-scoped verifier at N = 8, max_depth = 24."""
    import importlib.util
    import srk_certify as S
    import srk_gate as GT
    import srk_kernel as KX
    _check_worker_pins(load_manifest(), (S, GT, KX, sys.modules["srk_envelope"], sys.modules["srk_float"], G, E))
    mode = spec["mode"]
    if mode == "target":
        S.Q = G.producer_adapter(G.PRODUCTION)           # admission re-checked on every guarded call
    elif mode != "decoy":
        raise RuntimeError("unknown job mode")
    vs = importlib.util.spec_from_file_location("srk_verify_indep_scoped", str(REPO / VARIANT_REL))
    V = importlib.util.module_from_spec(vs)
    vs.loader.exec_module(V)
    if GT.verifier_identity(V) != spec["verifier_id"]:
        raise RuntimeError("verifier bytes differ from the pinned verifier")
    g = KX.Geom(F(spec["h"]), F(spec["k"]))
    lo, hi = F(spec["block"][0]), F(spec["block"][1])
    wb = (F(spec["weight_block"][0]), F(spec["weight_block"][1]))
    logs: list = []
    blk = S.run_block(g, lo, hi, STAGE1A_INDICES, (spec["degree"],), log=logs.append,
                      klass="TARGET_EXECUTION" if mode == "target" else "NONTARGET_DECOY", weight_block=wb)
    rung = blk["rungs"][0]
    certs = [S.certificate_json(blk, i) for i in STAGE1A_INDICES]
    certs = [c for c in certs if c.get("status") == "CERTIFIED"]
    verdicts, source = GT.verdicts_from_verifier(certs, V, None, N=VERIFIER_N, max_depth=VERIFIER_DEPTH)
    return {"kind": "JOB_RETURNED", "block": spec["block"], "degree": spec["degree"],
            "W_status": rung["W"]["status"],
            "V_status": {str(i): rung["V"][i]["status"] for i in rung["V"]},
            "certificates": certs, "verdicts": verdicts, "verdict_source": source,
            "adapter_records": list(getattr(S.Q, "records", [])), "log_digest": sha("\n".join(map(str, logs)).encode())}


def _check_worker_pins(m: dict, modules) -> None:
    """package C 'Workers re-verify the pins': every module a job runs, and this driver, match the frozen pins."""
    pins = pin_table(m)
    for mod in modules:
        rel = str(Path(mod.__file__).resolve().relative_to(REPO))
        read_pinned(pins, rel)
    read_pinned(pins, str(HERE.relative_to(REPO)))


def stage1a(mode: str, cell: tuple, geometry: dict, verifier_id: str, *, workers: int = WORKERS, runner=None,
            budget_s: float = STAGE1A_BUDGET_S) -> dict:
    """protocol 2: jobs, budget, per-rung certificates, in-process verdicts, the pinned gate.  Non-CERTIFIED, non-ACCEPT
    and budget outcomes fall back (Gamma-bar_i = None); a job exception or a gate exception raises (post-marker ->
    EXECUTION_INDETERMINATE)."""
    import srk_certify as S
    import srk_gate as GT
    wb, subs = S.cell_blocks(cell[0], cell[1])
    specs = [{"mode": mode, "h": geometry["h"], "k": geometry["k"], "block": [fs(subs[j][0]), fs(subs[j][1])],
              "weight_block": [fs(wb[0]), fs(wb[1])], "degree": d, "verifier_id": verifier_id}
             for j, d in stage1a_jobs()]
    run = run_jobs(specs, budget_s=budget_s, job_limit_s=STAGE1A_JOB_LIMIT_S, workers=workers, runner=runner)
    exc = [i for i, r in run["results"].items() if r["kind"] == "JOB_EXCEPTION"]
    if exc:
        raise RuntimeError(f"Stage-1a job exception(s) {exc}: " + run["results"][exc[0]].get("error", ""))
    certs, verdicts = [], {}
    for i in sorted(run["results"]):
        r = run["results"][i]
        if r["kind"] != "JOB_RETURNED":
            continue                                          # terminated by the job limit: discarded (fallback)
        if r["verdict_source"] != verifier_id:
            raise RuntimeError("a job's verdicts do not come from the pinned verifier")
        certs.extend(r["certificates"])
        verdicts.update(r["verdicts"])
    gr = GT.gate(cell[0], cell[1], dict(geometry), "whole", certs, verdicts, indices=STAGE1A_INDICES,
                 verdict_source=verifier_id)
    return {"gate_result": gr, "certificates": certs, "verdicts": verdicts, "run": {
        k: v for k, v in run.items() if k != "results"}, "jobs": {str(i): {k: v for k, v in r.items()
                                                                          if k not in ("certificates",)}
                                                               for i, r in run["results"].items()},
        "weight_block": [fs(wb[0]), fs(wb[1])], "sub_blocks": [[fs(a), fs(b)] for a, b in subs]}


def gate_report(gr) -> dict:
    return {"source": gr.source, "gamma": {str(i): (fs(v) if v is not None else None) for i, v in dict(gr.gamma).items()},
            "verdict_source": gr.verdict_source, "admitted": list(gr.admitted), "report": gr.report}


# ------------------------------------------------------------------------------------------------ Stage 1b (RLR307)
def job_stage1b(spec: dict) -> dict:
    m = load_manifest()
    _check_worker_pins(m, (G, E))
    rl = load_rlr307(m)
    S1, PIN = rl["rlr307_stage1"], rl["rlr307_pinned"]
    guard = G.producer_adapter(G.PRODUCTION)               # decoy drifts: NOT_BANDED; target: admission per call
    mods = PIN.load_certifier(REPO, guard, check_git=True)
    rec = S1.certify_rung(mods, F(spec["hull"][0]), F(spec["hull"][1]), spec["degree"])
    return {"kind": "JOB_RETURNED", "block": spec["block"], "degree": spec["degree"], "status": rec.get("status"),
            "record": rec, "adapter_records": list(guard.records)}


def _load_certifier_isolated(PIN, guard) -> dict:
    """The pinned RLR307 certifier, loaded without changing this process's module table.  In execute, the historical
    control and the Stage-1a gate have already imported the SRK side, which imports c1b_gauss by a plain import, and
    the pinned loader refuses a module it did not load itself.  The names are removed for the load and the previous
    table is restored afterwards: the certifier modules are held only by the returned dict (the loader's identity
    check binds them to each other), and later imports resolve as they did for the historical control."""
    names = tuple(PIN.LOAD_ORDER) + ("ov_quarantine",)
    saved = {n: sys.modules.pop(n) for n in names if n in sys.modules}
    try:
        return PIN.load_certifier(REPO, guard, check_git=True)
    finally:
        for n in names:
            sys.modules.pop(n, None)
        sys.modules.update(saved)


def stage1b(mode: str, cell: tuple, m: dict, *, workers: int = WORKERS, runner=None,
            budget_s: float = STAGE1B_BUDGET_S) -> dict:
    """protocol 3: the RLR307 Stage-1 rules verbatim; CERTIFICATION_FAILED -> fallback to S_I1; an exception or an
    independent-reconstruction mismatch raises (post-marker -> EXECUTION_INDETERMINATE)."""
    rl = load_rlr307(m)
    S1, IND = rl["rlr307_stage1"], rl["rlr307_independent"]
    mods = _load_certifier_isolated(rl["rlr307_pinned"], G.producer_adapter(G.PRODUCTION))
    cp = mods["c1b_certpw"]
    kappa = (cp.KAPPA1, cp.KAPPA2)
    kc = IND.kappa_check(*kappa)
    if not (kc["kappa1_ge_sqrt_2_over_pi"] and kc["kappa2_ge_4phi1"]):
        raise IndependentCheckFailed("a certifier kappa is not a valid upper bound")
    blocks = S1.blocks_for(cell[0], cell[1])
    hull = [(fs(b["hull_lo"]), fs(b["hull_hi"])) for b in blocks]
    order = sorted(((i, d) for i in range(len(blocks)) for d in S1.LADDER), key=lambda j: (-j[1], j[0]))
    specs = [{"mode": mode, "stage": "1b", "block": i, "hull": list(hull[i]), "degree": d} for i, d in order]
    run = run_jobs(specs, budget_s=budget_s, job_limit_s=STAGE1B_JOB_LIMIT_S, workers=workers, runner=runner)
    res = {}
    for idx, r in run["results"].items():
        if r["kind"] == "JOB_EXCEPTION":
            raise RuntimeError(f"Stage-1b job exception: {r.get('error', '')}")
        res[(specs[idx]["block"], specs[idx]["degree"])] = r
    block_recs, ind_blocks, rung_checks = [], [], []
    for i in range(len(blocks)):
        rungs = [res.get((i, d), {"kind": "NOT_STARTED"}) for d in S1.LADDER]
        cert = [r["record"] for r in rungs if r.get("kind") == "JOB_RETURNED" and r.get("status") == "CERTIFIED"]
        for r in cert:
            ind = IND.block_supply(r, *kappa)
            rung_checks.append(all(F(r[k]) == ind[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2")))
        brec = S1.ladder_compose(cp, cert)
        lad = IND.ladder(cert)
        if lad is None:
            ind_blocks.append(None)
            if brec["status"] != "NOT_CERTIFIED":
                raise IndependentCheckFailed(f"block {i}: ladder status disagrees")
        else:
            isup = IND.block_supply(lad, *kappa)
            if not (all(F(brec[k]) == lad[k] for k in IND.UPPER_KEYS + IND.LOWER_KEYS)
                    and all(F(brec[k]) == isup[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))):
                raise IndependentCheckFailed(f"block {i}: ladder or block supply disagrees")
            ind_blocks.append(isup)
        block_recs.append({"index": i, "sub_lo": fs(blocks[i]["sub_lo"]), "sub_hi": fs(blocks[i]["sub_hi"]),
                           "hull_lo": hull[i][0], "hull_hi": hull[i][1], "block": brec,
                           "rungs": [{k: v for k, v in r.items() if k != "adapter_records"} for r in rungs]})
    if not all(rung_checks):
        raise IndependentCheckFailed("a rung's assembly disagrees with the independent D14 recomputation")
    cellrec = S1.cell_compose([b["block"] for b in block_recs])
    icell = IND.cell(ind_blocks)
    if cellrec["status"] != icell["status"] or (cellrec["status"] == "CERTIFIED" and not all(
            F(cellrec[k + "_max"]) == icell[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))):
        raise IndependentCheckFailed("cell composition disagrees")
    return {"mode": mode, "ladder": list(S1.LADDER), "hull_bits": S1.HULL_BITS, "blocks": block_recs,
            "cell": cellrec, "kappa_check": kc, "run": {k: v for k, v in run.items() if k != "results"},
            "independent_checks": {"rungs": len(rung_checks), "all_equal": True}}


def compose_S(A_i1: dict, st1b: dict | None) -> dict:
    """S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)); a Stage-1b CERTIFICATION_FAILED gives S = S_I1."""
    if st1b is None or st1b["cell"]["status"] != "CERTIFIED":
        return {j: F(A_i1[j]) for j in FIELDS}
    c = st1b["cell"]
    return {"A0": F(A_i1["A0"]), "A1": min(F(A_i1["A1"]), F(c["A1_SUPPLY_max"])),
            "A2": min(F(A_i1["A2"]), F(c["A2_SUPPLY_max"]))}


# ------------------------------------------------------------------------------------------------ exactly-once sites
def _arm_marker(ctx: ExecContext, grant_commit: str) -> None:
    _assert_execute_context(ctx)
    if git("update-ref", ctx.marker_ref, grant_commit, "0" * 40, repo=ctx.repo).returncode != 0:
        raise Refusal("CONSUMED", "the exactly-once marker could not be created: the target is never evaluated twice")


def _persist_pending(ctx: ExecContext, data: bytes) -> str:
    _assert_execute_context(ctx)
    w = git("hash-object", "-w", "--stdin", repo=ctx.repo, input_bytes=data)
    blob = w.stdout.strip()
    if w.returncode or blob != git_blob_id(data):
        raise OSError("hash-object did not store the produced bytes")
    if git("update-ref", ctx.pending_ref, blob, "0" * 40, repo=ctx.repo).returncode:
        raise OSError("the pending ref could not be created")
    return blob


def persist_emergency(ctx: ExecContext, data: bytes) -> str:
    dfd = os.open(git_dir(ctx), os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = os.open(EMERGENCY_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dfd)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        os.close(dfd)
    return str(git_dir(ctx) / EMERGENCY_NAME)


def serialize(obj: dict) -> bytes:
    body = dict(obj)
    body["sha256"] = sha(json.dumps(body, sort_keys=True).encode())
    return (json.dumps(body, indent=1, sort_keys=True) + "\n").encode()


def seal_blob(ctx: ExecContext, blob: str, message: str) -> str:
    last = None
    for delay in (0, *SEAL_RETRY_DELAYS):
        time.sleep(delay)
        head = git("rev-parse", "HEAD", repo=ctx.repo).stdout.strip()
        with tempfile.TemporaryDirectory(prefix="p309seal") as td:
            idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
            msgf = Path(td) / "msg"
            msgf.write_text(message)
            steps = [git("read-tree", head, repo=ctx.repo, env_extra=idx),
                     git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}", repo=ctx.repo,
                         env_extra=idx)]
            tree = git("write-tree", repo=ctx.repo, env_extra=idx)
            if any(s.returncode for s in steps) or tree.returncode:
                last = "index"
                continue
            commit = git("commit-tree", tree.stdout.strip(), "-p", head, "-F", str(msgf), repo=ctx.repo)
            if commit.returncode:
                last = "commit-tree"
                continue
            cid = commit.stdout.strip()
            if not ctx.branch_ref or git("update-ref", ctx.branch_ref, cid, head, repo=ctx.repo).returncode:
                last = "update-ref"
                continue
            entry = git("ls-tree", cid, "--", RESULT_REL, repo=ctx.repo).stdout.split()
            if entry[:3] != ["100644", "blob", blob]:
                raise OSError("the sealed entry is not the persisted blob")
            git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}", repo=ctx.repo)
            return cid
    raise OSError(f"seal failed at {last}")


def materialize(ctx: ExecContext, blob: str) -> None:
    data = subprocess.run(["/usr/bin/git", "-C", str(ctx.repo), "cat-file", "blob", blob], capture_output=True,
                          env=dict(ENV), stdin=subprocess.DEVNULL).stdout
    if git_blob_id(data) != blob:
        raise OSError("the object store returned other bytes")
    fds = [os.open(str(ctx.repo), os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for part in (NS_REL + "/evidence").split("/"):
            try:
                os.mkdir(part, 0o755, dir_fd=fds[-1])
            except FileExistsError:
                pass
            fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        os.mkdir("execution", 0o755, dir_fd=fds[-1])
        fds.append(os.open("execution", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        fd = os.open(RESULT_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fds[-1])
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        rfd = os.open(RESULT_NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fds[-1])
        try:
            st = os.fstat(rfd)
            back = b""
            while (chunk := os.read(rfd, 1 << 20)):
                back += chunk
        finally:
            os.close(rfd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or back != data:
            raise OSError("the materialized copy is not the sealed bytes")
    finally:
        for fd in reversed(fds):
            os.close(fd)


def seal_message(status: str) -> str:
    return (f"p309 formal r1 — SEAL of the one cell-309 P309 evaluation ({status})\n\nCommitted by "  # q309: literal-ok (commit message text)
            f"{NS_REL}/code/p309_driver.py from the in-memory bytes (object store + pending ref), not from a worktree "
            "file; the result was not inspected before this commit.\n")


# ------------------------------------------------------------------------------------------------ the evaluation
def decide(st1b: dict | None, st2: dict) -> dict:
    """protocol 5: CLOSED iff Gamma < 0 (exact, strict) on a TARGET_EVALUATED run; fallbacks are not failures."""
    closed = F(st2["Gamma_exact"]) < 0
    return {"mechanical_outcome": "CELL309_CLOSED_UNDER_P309" if closed else "NOT_CLOSED",  # q309: literal-ok (label)
            "reason": "Gamma < 0 (exact, strict)" if closed else "Gamma >= 0 (exact)",
            "stage1b_fallback_to_S_I1": st1b is None or st1b["cell"]["status"] != "CERTIFIED"}


def evaluate_target(con: dict, prep: dict) -> dict:
    """post-marker: Stage 1a, Stage 1b, Stage 2.  Any exception propagates (-> EXECUTION_INDETERMINATE)."""
    cell, vid, m = prep["cell"], prep["verifier_id"], prep["manifest"]
    st1a = stage1a("target", cell, GEOMETRY, vid)
    st1b = stage1b("target", cell, m)
    A = compose_S(prep["A_I1"], st1b)
    if st1b["cell"]["status"] == "CERTIFIED" and A != _ind().consumed(prep["A_I1"], {
            "A1_SUPPLY": st1b["cell"]["A1_SUPPLY_max"], "A2_SUPPLY": st1b["cell"]["A2_SUPPLY_max"]}):
        raise IndependentCheckFailed("S disagrees with its independent reconstruction")
    st2 = evaluate_srk(con, prep["ci"], A, cell, st1a["gate_result"], vid)
    return {"cell": TARGET_CELL, "stage1a": {**{k: v for k, v in st1a.items() if k != "gate_result"},
                                             "gate": gate_report(st1a["gate_result"])},
            "stage1b": st1b, "S": {j: fs(A[j]) for j in FIELDS}, "stage2": st2, "decision": decide(st1b, st2)}


def fallback_bytes(common_min: dict, stage: str, exc: BaseException) -> bytes:
    rec = {"schema": SCHEMA, "status": "POST_MARKER_RECORDING_FAILED", "stage": stage,
           "error": f"{type(exc).__name__}: {exc}"[:400], "target_evaluations": 1, **common_min}
    try:
        return serialize(rec)
    except BaseException:  # noqa: BLE001
        return (json.dumps({"status": "POST_MARKER_RECORDING_FAILED", "stage": stage}) + "\n").encode()


def after_marker(ctx: ExecContext, con, prep, common: dict, evaluator, t0: float, persist=None, sealer=None,
                 materializer=None) -> int:
    persist = persist or _persist_pending
    sealer = sealer or seal_blob
    materializer = materializer or materialize
    common_min = {"cell": TARGET_CELL, "grant": common.get("grant"), "driver_sha256": common.get("driver_sha256")}
    try:
        try:
            t_eval = time.time()
            tgt = evaluator(con, prep)
            status = "TARGET_EVALUATED"
        except BaseException as exc:  # noqa: BLE001  (protocol 2.5 / 3: any exception -> EXECUTION_INDETERMINATE)
            kind = "INDEPENDENT_CHECK_FAILED" if isinstance(exc, IndependentCheckFailed) else "TARGET_EVALUATION_FAILED"
            tgt, status = {"error": f"{type(exc).__name__}: {exc}"[:400], "failure_kind": kind}, kind
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        common.update({"status": status, "target_evaluated": status == "TARGET_EVALUATED", "target_evaluations": 1,
                       "target": tgt,
                       "mechanical_outcome": tgt.get("decision", {}).get("mechanical_outcome")
                       if status == "TARGET_EVALUATED" else "EXECUTION_INDETERMINATE",
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                       "evaluation_wall_seconds": round(time.time() - t_eval, 3),
                       "cpu_seconds_parent": round(usage.ru_utime + usage.ru_stime, 3),
                       "cpu_seconds_children": round(cusage.ru_utime + cusage.ru_stime, 3)})
        data = serialize(common)
    except BaseException as exc:  # noqa: BLE001
        status, data = "POST_MARKER_RECORDING_FAILED", fallback_bytes(common_min, "record", exc)
    blob, channel = None, None
    try:
        blob, channel = persist(ctx, data), "pending_ref"
    except BaseException:  # noqa: BLE001
        try:
            persist_emergency(ctx, data)
            channel = "emergency_file"
        except BaseException:  # noqa: BLE001
            print("P309 CONSUMED_UNRECORDED: the marker exists and no evidence channel worked. NEVER run execute again.")
            return 6
    if blob is None:
        print("P309 UNSEALED: evidence persisted in the git dir; run `seal-only`. NEVER run execute again.")
        return 4
    try:
        cid = sealer(ctx, blob, seal_message(status))
    except BaseException:  # noqa: BLE001
        print(f"P309 UNSEALED: evidence persisted ({channel}); run `seal-only`. NEVER run execute again.")
        return 4
    try:
        materializer(ctx, blob)
    except BaseException:  # noqa: BLE001
        print(f"P309 SEALED {cid} (status {status}); worktree copy NOT materialized: run `seal-only`.")
        return 7
    print(f"P309 SEALED {cid} (status {status}; one target evaluation; result not printed)")
    return 0 if status == "TARGET_EVALUATED" else 5


def run_execute(own_sha: str, ctx: ExecContext | None = None, prepare=None, evaluator=None, persist=None,
                sealer=None, materializer=None, control=None) -> int:
    """THE execution.  Before the marker: flags, not-evaluated, result paths, clean tree, check_grant, pins,
    governance, the historical control (CONTROL_FAILED -> exit 3, not consumed).  Then the marker (CAS), then
    Stage 1a / 1b / 2 and recording from memory."""
    _MODE["mode"] = "execute"
    ctx = ctx or production_context()
    t0, started = time.time(), utc()
    if ctx.kind == "PRODUCTION":
        check_flags()
    check_not_evaluated(ctx)
    check_result_paths(ctx)
    check_clean(ctx)
    m = load_manifest(ctx.repo)
    grant = check_grant(own_sha, m, ctx)
    shas = check_bindings(m, ctx.repo) if ctx.kind == "PRODUCTION" else {"sandbox": True}
    state = check_governance_state(m, ctx.repo) if ctx.kind == "PRODUCTION" else {"sandbox": True}
    cell = tuple(F(x) for x in grant["cell_interval"])
    if ctx.kind == "PRODUCTION":
        import srk_certify as S
        wb, _ = S.cell_blocks(*cell)
        if [fs(wb[0]), fs(wb[1])] != [fs(F(x)) for x in grant["drift_hull_Ew"]]:
            raise Refusal("GRANT_INVALID", "Ew is not the outward hull of the granted cell")
    verifier_id = "sha256:" + pin_table(m)[VARIANT_REL][0]
    if ctx.kind == "PRODUCTION":
        con = load_consumer(m, ctx.repo)
        load_rlr307(m, ctx.repo)
        ctl = historical_control(con, m, cell, verifier_id, ctx.repo)
    else:
        con, ctl = None, (control or (lambda: {"reproduces_C2_exactly": True, "digest": "sandbox"}))()
    common = {"schema": SCHEMA, "cell": TARGET_CELL, "m": 5, "route": "P309", "scope": "CLOSURE_ONLY",
              "context": ctx.kind, "grant": grant, "input_sha256": shas, "governance_state_before": state,
              "driver_sha256": own_sha, "started_utc": started, "verifier_id": verifier_id,
              "historical_control": {k: v for k, v in ctl.items() if not k.startswith("_")},
              "python": sys.version.split()[0]}
    if not ctl["reproduces_C2_exactly"]:
        common.update({"status": "CONTROL_FAILED", "target_evaluated": False, "target_evaluations": 0,
                       "finished_utc": utc()})
        data = serialize(common)
        try:
            w = git("hash-object", "-w", "--stdin", repo=ctx.repo, input_bytes=data)
            cid = (sealer or seal_blob)(ctx, w.stdout.strip(), seal_message("CONTROL_FAILED"))
            (materializer or materialize)(ctx, w.stdout.strip())
        except BaseException:  # noqa: BLE001
            print("P309 CONTROL_FAILED: not fully sealed. The target was not evaluated.")
            return 4
        print(f"P309 CONTROL_FAILED sealed {cid}; the target was not evaluated")
        return 3
    prep = (prepare or (lambda: {"cell": cell, "verifier_id": verifier_id, "manifest": m, "A_I1": ctl["_A"],
                                 "ci": ctl["_ci"]}))()
    check_result_paths(ctx)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    signal.alarm(0)
    _arm_marker(ctx, grant["grant_commit"])
    return after_marker(ctx, con, prep, common, evaluator or evaluate_target, t0, persist, sealer, materializer)


def run_seal_only(ctx: ExecContext | None = None) -> int:
    _MODE["mode"] = "seal-only"
    ctx = ctx or production_context()
    if ctx.kind == "PRODUCTION":
        check_flags()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    marker = git("rev-parse", "-q", "--verify", ctx.marker_ref, repo=ctx.repo).stdout.strip()
    pending = git("rev-parse", "-q", "--verify", ctx.pending_ref, repo=ctx.repo).stdout.strip()
    emergency = git_dir(ctx) / EMERGENCY_NAME
    if not pending and os.path.lexists(emergency):
        if os.path.islink(emergency):
            raise Refusal("SEAL_ONLY", "the emergency evidence file is a symlink")
        fd = os.open(emergency, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            data = b""
            while (chunk := os.read(fd, 1 << 20)):
                data += chunk
        finally:
            os.close(fd)
        pending = _persist_pending(ctx, data)
    if not pending:
        raise Refusal("SEAL_ONLY", "no persisted evidence (no pending ref, no emergency file)")
    data = subprocess.run(["/usr/bin/git", "-C", str(ctx.repo), "cat-file", "blob", pending], capture_output=True,
                          env=dict(ENV), stdin=subprocess.DEVNULL).stdout
    try:
        status = json.loads(data).get("status", "UNKNOWN")
    except ValueError:
        status = "UNPARSEABLE_EVIDENCE"
    if status == "CONTROL_FAILED" and marker:
        raise Refusal("SEAL_ONLY", "CONTROL_FAILED evidence but the marker exists")
    if status != "CONTROL_FAILED" and not marker:
        raise Refusal("SEAL_ONLY", "post-marker evidence without a marker")
    entry = git("ls-tree", "HEAD", "--", RESULT_REL, repo=ctx.repo).stdout.split()
    if entry and entry[:3] != ["100644", "blob", pending]:
        raise Refusal("SEAL_ONLY", "HEAD holds a different result entry")
    cid = git("rev-parse", "HEAD", repo=ctx.repo).stdout.strip()
    if not entry:
        if git("status", "--porcelain", "--untracked-files=all", repo=ctx.repo).stdout.strip():
            raise Refusal("DIRTY_TREE", "seal-only needs an otherwise clean tree")
        try:
            cid = seal_blob(ctx, pending, seal_message(f"{status}, sealed by seal-only"))
        except OSError as exc:
            raise Refusal("UNSEALED", str(exc))
    if not os.path.lexists(ctx.repo / RESULT_REL):
        try:
            materialize(ctx, pending)
        except (OSError, FileExistsError) as exc:
            print(f"P309 SEALED {cid} (status {status}); materialization refused: {type(exc).__name__}")
            return 7
    else:
        st = os.lstat(ctx.repo / RESULT_REL)
        same = False
        if stat.S_ISREG(st.st_mode):
            same = (ctx.repo / RESULT_REL).read_bytes() == data
        if not same:
            print(f"P309 SEALED {cid} (status {status}); the worktree object at the result path is NOT the sealed bytes")
            return 7
    print(f"P309 SEALED {cid} (seal-only; status {status}; nothing computed)")
    return 0


# ------------------------------------------------------------------------------------------------ qualification modes
def decoy_stage1a(name: str, workers: int, verifier_id: str) -> dict:
    if name not in DECOY_STAGE1A:
        raise Refusal("CELL_OUT_OF_SCOPE", f"{name} is not a declared Stage-1a decoy")
    d = DECOY_STAGE1A[name]
    cell = (F(d["cell"][0]), F(d["cell"][1]))
    import srk_certify as S
    wb, _ = S.cell_blocks(*cell)
    G.guard_interval((F(d["h"]), F(d["k"])), wb[0], wb[1])     # raises for any band-meeting decoy
    E.log("code/p309_driver.py decoy-stage1a", f"QC08/QC10 decoy Stage 1a on declared {name}",
          klass="NONTARGET_DECOY", drifts=[[fs(wb[0]), fs(wb[1])]] if F(d["h"]) == 5 else [],
          notes="declared out-of-band decoy cell (research SRK_DECOY_DECLARATION_A2 family)")
    st = stage1a("decoy", cell, {"h": d["h"], "k": d["k"]}, verifier_id, workers=workers)
    return {**{k: v for k, v in st.items() if k != "gate_result"}, "gate": gate_report(st["gate_result"]),
            "decoy": name}


def decoy_stage1b(k: int, workers: int, m: dict) -> dict:
    if k not in DECOY_STAGE1B_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", f"{k} is not a declared Stage-1b decoy")
    cells = [c for c in json.loads(read_pinned(pin_table(m), data_rel(m, "cells_json")))
             if c["detector"] == "CUSUM" and c["index"] == k]
    if len(cells) != 1:
        raise Refusal("DECOY_GEOMETRY", str(k))
    lo, hi = F(cells[0]["left"][0], cells[0]["left"][1]), F(cells[0]["right"][0], cells[0]["right"][1])
    G.guard_interval((F(5), F(1, 2)), lo, hi)
    E.log("code/p309_driver.py decoy-stage1b", f"QC09 decoy Stage 1b (RLR307 rules) on declared cover cell {k}",
          klass="NONTARGET_DECOY", drifts=[[fs(lo), fs(hi)]], notes="the RLR307 decoy cells; outside the band")
    return stage1b("decoy", (lo, hi), m, workers=workers)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("preflight", "rehearse", "decoy-stage1a", "decoy-stage1b", "execute",
                                     "seal-only", "_job"))
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--decoy")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    own_sha = sha(HERE.read_bytes())
    _MODE["mode"] = a.mode
    if a.mode == "_job":
        spec = json.loads(a.spec)
        try:
            res = job_stage1b(spec) if spec.get("stage") == "1b" else job_stage1a(spec)
        except BaseException as exc:  # noqa: BLE001
            res = {"kind": "JOB_EXCEPTION", "error": f"{type(exc).__name__}: {exc}"[:400]}
        Path(spec["_out"]).write_text(json.dumps(res, sort_keys=True))
        return 0
    try:
        if a.mode in ("preflight", "execute", "seal-only") and (a.cell is not None or a.decoy is not None):
            raise Refusal("CELL_OUT_OF_SCOPE", "execute takes no cell: the cell comes from the grant")
        if a.mode == "execute":
            return run_execute(own_sha)
        if a.mode == "seal-only":
            return run_seal_only()
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Refusal("WALL_CAP", f"{PRE_CAP_S} s")))
        m = load_manifest()
        vid = "sha256:" + pin_table(m)[VARIANT_REL][0]
        if a.mode == "preflight":
            signal.alarm(PRE_CAP_S)
            check_not_evaluated(production_context())
            out = {"mode": "preflight", "bindings": check_bindings(m), "governance_state": check_governance_state(m),
                   "driver_sha256": own_sha}
            load_consumer(m)
            load_rlr307(m)
            print("P309 PREFLIGHT PASS")
        elif a.mode == "rehearse":
            import p309_rehearse as RH
            out = RH.rehearse(load_consumer(m), m, vid)
            print(f"P309 REHEARSE (manufactured inputs): pass = {out['pass']}")
        elif a.mode == "decoy-stage1a":
            t0 = time.time()
            out = {"mode": "decoy-stage1a", **decoy_stage1a(a.decoy, a.workers, vid), "driver_sha256": own_sha,
                   "utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                   "latent_proxy": "decoy values; never juxtapose with any tail-cell number"}
            print(f"P309 DECOY-STAGE1A {a.decoy}: gate source {out['gate']['source']}")
        else:
            t0 = time.time()
            out = {"mode": "decoy-stage1b", "decoy_cell": a.cell, **decoy_stage1b(a.cell, a.workers, m),
                   "driver_sha256": own_sha, "utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                   "latent_proxy": "decoy values; never juxtapose with any tail-cell number"}
            print(f"P309 DECOY-STAGE1B cell {a.cell}: {out['cell']['status']}")
        if a.out:
            Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
        return 0
    except (Refusal, G.QuarantineRefusal) as e:
        print(f"P309 REFUSED {e}")
        return 4 if getattr(e, "code", None) == "UNSEALED" else 2
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    sys.exit(main())
