"""Cell-308 MB campaign (r1) -- the cell-308-only exactly-once driver (B6).

ONE scientific evaluation, after freeze -> qualification -> independent review (QUALIFICATION_ACCEPTED) -> grant:
  Stage 1  (mb308_stage1) RLR block rungs on every hull B_i; the pointwise Lambda ladder at every b_i (C2b N 20/40/80,
           C1b d 8/10/12); independent verification of every certified C2b upper rung by stream VERIFY's P1 verifier
           vd_pl inside its job; C1b upper rungs with d > 6 are never admitted (NOT_INDEPENDENTLY_VERIFIED) and the C1b
           Lambda_lo serves only as the cross-implementation alarm (L_C1b <= U_C2b); admission (verified AND an
           other-implementation lower rung below U), INCONSISTENT on a refutation or an alarm; envelope (Lemma M-U);
           in a pool of spawned workers (one fresh process per job, declared CPU cap) that load every certifier from
           pinned bytes and arm the guard from git;
  compose  (mb308_supply) S_i = componentwise min of {S_I1, Dv'-M(C1), Dv'-M(C2), D14-M, G}, equal to stream F2;
  Stage 2  (mb308_consumer.stage2) TPT-B through tptb_tail on cell 308's COMMITTED TC-T inputs with the block
           triples; C5 / C6 gates; F2 bracket; Gamma_dec = g_hi + max(P_B, P_hi); CLOSED iff Gamma_dec < 0 (exact).
Before the marker, two historical controls: C-A (C2's committed record under S_I1) and C-B (tptb_tail reproduction
gates at s = rho, reproduction only). Either failing => CONTROL_FAILED, sealed, target NOT consumed.

Exactly-once mechanics: the accepted cell-307 driver's (seal from memory, marker by CAS, pending ref, emergency file,
O_EXCL|O_NOFOLLOW writes, after_marker that never raises, caps, exit codes), re-targeted to cell 308.

modes
    preflight                          read-only anywhere: bindings, governance, no prior evaluation, module identities
    rehearse --cell 305                read-only: controls C-A and C-B on cell 305's COMMITTED record (equality only)
    decoy --cell 297|316 [--first-blocks K] [--dev-ladder] --out F
                                       Stage 1 in DECOY mode on a declared decoy cover cell (outside [6/5, 13/5]) and,
                                       for 297, Stage 2 on manufactured TC-T bundles with 297's geometry (decoy_gen);
                                       writes only --out. --dev-ladder (decoy only) = a reduced ladder for timing.
    execute                            qualified worktree + grant commit only; the ONE evaluation of cell 308
    seal-only                          qualified worktree only: seal / materialize persisted evidence; never computes

exit codes: 0 sealed TARGET_EVALUATED; 2 REFUSED before the marker (nothing consumed); 3 CONTROL_FAILED sealed (target
            not consumed); 4 UNSEALED (evidence persisted; run seal-only); 5 sealed with a post-marker failure status;
            6 CONSUMED_UNRECORDED (never rerun); 7 sealed, worktree copy not materialized (run seal-only)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import multiprocessing
import os
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mb308_consumer as CON  # noqa: E402
import mb308_guard as GUARD  # noqa: E402
import mb308_pinned as PIN  # noqa: E402
import mb308_stage1 as S1M  # noqa: E402
import mb308_supply as SUP  # noqa: E402

CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell308_mb_r1"
QUALIFIED_WORKTREE = "/Users/suzhe/ReBaseGuard-c308mb"
QUALIFIED_GIT_DIR = "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mb"
QUALIFIED_COMMON_DIR = "/Users/suzhe/ReBaseGuard/.git"
QUALIFIED_BRANCH = "refs/heads/p5y-k5-cell308-mb-r1"

TARGET_CELL = 308
REHEARSAL_CELLS = (305,)
DECOY_CELLS = (297, 316)
FIELDS = ("A0", "A1", "A2")
FROZEN_DIRS = ("code", "protocol", "theory", "tests", "config", "errata", "evidence_prefreeze")
POST_FREEZE_DIRS = ("qualification", "review", "authorization", "evidence", "adjudication", "postexec")
DECOY_SEED = 20260929
DECOY_BUNDLES = (("taylor", 1, "cut"), ("midpoint", -1, "loose"), ("mixed", 1, "cut_both"))

EXEC_DIR_REL = NS_REL + "/evidence/execution"
RESULT_NAME = "MB308_CELL308_RESULT.json"
RESULT_REL = EXEC_DIR_REL + "/" + RESULT_NAME
GUARDED_PATHS = (EXEC_DIR_REL, RESULT_REL, EXEC_DIR_REL + "/MB308_CELL308_RESULT.tmp",
                 EXEC_DIR_REL + "/MB308_CELL308_RESULT.json.tmp", EXEC_DIR_REL + "/MB308_CELL308_RESULT.partial")
GRANT_REL = NS_REL + "/authorization/MB308_GRANT.json"
QUAL_DIR_REL = NS_REL + "/qualification/"
QUAL_REL = QUAL_DIR_REL + "MB308_QUALIFICATION.json"
QREVIEW_REL = NS_REL + "/review/MB308_QUALIFICATION_REVIEW.md"
MANIFEST_REL = NS_REL + "/protocol/MB308_FREEZE.json"
CONSUMED_REF = GUARD.CONSUMED_REF
PENDING_REF = "refs/p5y-k5-cell308-mb-r1/pending-result"
EMERGENCY_NAME = "mb308-cell308-emergency-result.json"
PRIOR_MARKERS = ("refs/p5y-k5-cell308-mb-r1/",)
R6_NAME = "K5_COVERAGE_MAP_R6"
WORKERS = 5                      # design D11
PRE_CAP_S = 1800                 # everything before the marker (controls included)
EVAL_CAP_S = 8 * 3600            # protocol 3.2: max(6 h, ceil(2 x projected Stage-1 wall)) from decoy runtimes only
DECOY_CAP_S = 12 * 3600
SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}
SCHEMA = "rebaseguard.p5y.k5.cell308-mb-r1.result.v1"
OUTCOMES = ("CELL308_CLOSED_UNDER_MB", "CELL308_NOT_CLOSED_UNDER_MB", "CELL308_EXECUTION_INDETERMINATE")

# helper modules of this campaign, pinned by sha256 (the grant binds this driver's own sha256). Re-pinned at freeze.
HELPER_SHA256 = {
    "mb308_guard.py": "882ce3fb86f4089081104e0fdbaf31c01b16e9a80065acd4e911f3010e6e06b1",
    "mb308_pinned.py": "5c221a0e70a708c580f13e1cd622556930f047f3c0b302227a8d9b18c52220a2",
    "mb308_a0core.py": "0873604379bb5008f385ed09c7ae2f0694a402a91881b6a9d2e45649af332de6",
    "mb308_stage1.py": "23296f837eb7520b36c32bba08d238d940c14a8753e8ce8cadb05f0990f2ec98",
    "mb308_supply.py": "af1a818b68459ada53773557e10153ae4ae3edc232d52e93fd19814e4da59b58",
    "mb308_consumer.py": "c233bdb6235cd8a44bcf187be7d6686a4684f8619bed21ade9130432c5c09188",
}
PIN.GUARD_SHA256 = HELPER_SHA256["mb308_guard.py"]
# per-job CPU caps (REVIEW_A0_CERTIFIER_R1 C3): each Stage-1 job runs in a FRESH worker process (max_tasks_per_child
# = 1) whose RLIMIT_CPU is set to exactly the declared cap; a job refuses to start if an outer hard limit would make the
# effective cap smaller than the declared one. A cap hit kills the worker: an execution failure, never a dropped rung.
# Values: protocol 3.2 (max(3 x the larger decoy wall time rounded up to 300 s, 1800 s)); C1B d4 and every VER entry
# serve only the decoy development ladder / are unused by the frozen ladder (C1b d > 6 is never verified).
RUNG_CPU_CAP_S = {"RLR": {4: 1800, 6: 4200, 8: 8700}, "C2B": {20: 1800, 40: 1800, 80: 2700},
                  "C1B": {4: 1800, 8: 1800, 10: 1800, 12: 1800},
                  "VER": {4: 1800, 6: 1800, 8: 1800, 10: 1800, 12: 1800}}
LINEAGE = [("5a94568af69f775eaabdeb895dea19b9bf664935", "D stage"), ("ae4cbc2c", "coverage map r5"),
           ("a15d083b009868e38a5bd5a808f38f19e6ab4b92", "floor r2"),
           ("3fadb422eaba97123d46e98b9e80277a62a042c8", "REPLACEMENT_FLOOR_ACCEPTED"),
           ("9c2cbf21", "CELL306_NOT_ADOPTED"), ("c5324a78", "ADJUDICATION_ACCEPTED"),
           ("d3b60795", "FREEZE_READY"), ("7f45e048c39023f4805b21a461650fd332af951f", "morning handover"),
           ("b73b9449", "CELL307_CLOSED_UNDER_RLR"),
           # the research lineage required by the coordinator (note 6, item 5)
           ("33185113", "charter"), ("bfa9ad3c", "Theorem MB r1"), ("a7014669", "stream INDEP"),
           ("0292d654", "stream INDEP_TUPLE"), ("e042c8d1", "A0 certifier review"),
           ("f42fef40", "incident-independence review"), ("8da57f89", "incident-review conditions"),
           ("58f190dc", "stream VERIFY follow-up"), ("55d3719c", "pre-freeze formal build"),
           ("fc4eeeee", "stream-A0 certificates"), ("cc249872", "protocol draft p0")]


class Refusal(Exception):
    """Fail closed BEFORE the marker: nothing is evaluated, nothing is consumed."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class IndependentCheckFailed(RuntimeError):
    """A layer disagrees with its independent reconstruction or verifier (after the marker: INDETERMINATE)."""


class Inconsistent(RuntimeError):
    """L_i > U_i at some pointwise drift: a soundness alarm (after the marker: INDETERMINATE)."""


# ------------------------------------------------------------------ plumbing
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def git(*args, env_extra=None, input_bytes=None):
    env = dict(ENV)
    if env_extra:
        env.update(env_extra)
    if input_bytes is not None:
        p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args], input=input_bytes,
                           capture_output=True, env=env)
        return subprocess.CompletedProcess(p.args, p.returncode, p.stdout.decode(errors="replace"),
                                           p.stderr.decode(errors="replace"))
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args],
                          capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def verdict_ok(text: str, expected: str) -> bool:
    lines = text.splitlines()
    return len(lines) > 1 and lines[1].strip() == expected and sum(1 for ln in lines if ln.strip() == expected) == 1


def freeze_commit() -> str:
    return git("log", "-1", "--format=%H", "--", *(f"{NS_REL}/{d}" for d in FROZEN_DIRS)).stdout.strip()


def git_dir() -> Path:
    return Path(git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())


def check_helpers() -> dict:
    out = {}
    for name, pin in HELPER_SHA256.items():
        got = sha((CODE / name).read_bytes())
        if got != pin:
            raise Refusal("HELPER_PIN_MISMATCH", name)
        out[name] = got
    return out


def jsonable(o):
    if isinstance(o, F):
        return fs(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


# ------------------------------------------------------------------ identity, flags, prior evaluation, paths
def check_flags() -> None:
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise Refusal("INTERPRETER_FLAGS", "execute and seal-only require python3.14 -I -S -B")


def check_identity() -> dict:
    here = str(REPO.resolve())
    gd = git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip()
    cd = git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    br = git("symbolic-ref", "-q", "HEAD").stdout.strip()
    if here != QUALIFIED_WORKTREE or str(Path(gd).resolve()) != QUALIFIED_GIT_DIR or \
            str(Path(cd).resolve()) != QUALIFIED_COMMON_DIR:
        raise Refusal("REPO_NOT_QUALIFIED", "not the qualified worktree / git dir / common dir")
    if br != QUALIFIED_BRANCH:
        raise Refusal("WRONG_BRANCH", br or "detached HEAD")
    return {"worktree": here, "git_dir": gd, "common_dir": cd, "branch": br}


def check_not_evaluated() -> None:
    for prefix in PRIOR_MARKERS:
        if git("for-each-ref", "--format=%(refname)", prefix).stdout.strip():
            raise Refusal("CONSUMED", f"a ref exists under {prefix}")
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    if RESULT_REL in names or os.path.lexists(REPO / RESULT_REL) or \
            git("log", "--all", "--format=%H", "--", RESULT_REL).stdout.strip():
        raise Refusal("TARGET_ARTIFACT_EXISTS", RESULT_REL)
    gd = git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip()
    if gd and os.path.lexists(Path(gd) / EMERGENCY_NAME):
        raise Refusal("TARGET_ARTIFACT_EXISTS", "emergency evidence file in the git dir")


def check_result_paths() -> None:
    for rel in GUARDED_PATHS:
        try:
            st = os.lstat(REPO / rel)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise Refusal("RESULT_PATH_OCCUPIED", f"{rel}: unreadable ({exc.__class__.__name__})")
        raise Refusal("RESULT_PATH_OCCUPIED", f"{rel} holds a {stat.filemode(st.st_mode)} object")
    cur = REPO
    for part in (NS_REL + "/evidence").split("/"):
        cur = cur / part
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            break
        if not stat.S_ISDIR(st.st_mode):
            raise Refusal("RESULT_PATH_OCCUPIED", f"{cur.relative_to(REPO)} is not a plain directory")


def check_clean() -> None:
    if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
        raise Refusal("DIRTY_TREE")
    if git("status", "--porcelain", "--ignored", "--untracked-files=all", "--", NS_REL).stdout.strip():
        raise Refusal("IGNORED_OBJECT", "an ignored or untracked object exists in the campaign namespace")
    gd, cd = git_dir(), Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    locks = [p for p in (gd / "index.lock", gd / "HEAD.lock", cd / (QUALIFIED_BRANCH + ".lock"),
                         cd / "packed-refs.lock") if os.path.lexists(p)]
    if locks:
        raise Refusal("GIT_LOCKED", str(locks[0]))


def check_seal_preconditions() -> dict:
    if git("var", "GIT_COMMITTER_IDENT").returncode or git("var", "GIT_AUTHOR_IDENT").returncode:
        raise Refusal("SEAL_PRECONDITION", "no committer/author identity")
    head = git("rev-parse", "HEAD").stdout.strip()
    probe = b"mb308 object-store write probe\n"
    w = git("hash-object", "-w", "--stdin", input_bytes=probe)
    if w.returncode or w.stdout.strip() != git_blob_id(probe):
        raise Refusal("SEAL_PRECONDITION", "the object store is not writable")
    with tempfile.TemporaryDirectory(prefix="mb308pre") as td:
        idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
        tree = git("write-tree", env_extra=idx) if not git("read-tree", head, env_extra=idx).returncode else None
        if tree is None or tree.returncode:
            raise Refusal("SEAL_PRECONDITION", "a private index cannot be built")
        trial = git("commit-tree", tree.stdout.strip(), "-p", head, "-m", "mb308 trial commit object (never referenced)")
        if trial.returncode:
            raise Refusal("SEAL_PRECONDITION", "a commit object cannot be created with the current configuration")
    if git("rev-parse", "-q", "--verify", QUALIFIED_BRANCH).returncode:
        raise Refusal("SEAL_PRECONDITION", "the branch ref does not resolve")
    if not os.access(git_dir(), os.W_OK):
        raise Refusal("SEAL_PRECONDITION", "the git dir is not writable (fallback evidence channel)")
    evd = REPO / NS_REL / "evidence"
    parent = evd if os.path.lexists(evd) else REPO / NS_REL
    if not os.access(parent, os.W_OK | os.X_OK):
        raise Refusal("SEAL_PRECONDITION", "the worktree copy's parent directory is not writable")
    return {"branch_head": head}


# ------------------------------------------------------------------ bindings and governance state
def read_pinned(key: str) -> bytes:
    try:
        return CON.read_pinned(REPO, key)
    except CON.ConsumerRefusal as exc:
        raise Refusal(exc.code, str(exc))


def check_bindings(allow_uncommitted: bool = False) -> dict:
    shas = {}
    for key, (rel, pin, blob) in CON.PINS.items():
        shas[key] = sha(read_pinned(key))
        got = git("rev-parse", f"HEAD:{rel}").stdout.strip()
        if not got.startswith(blob):
            raise Refusal("BLOB_MISMATCH", rel)
        if git("hash-object", "--", rel).stdout.strip() != got:
            raise Refusal("WORKTREE_DIFFERS_FROM_COMMIT", rel)
    try:
        for key, pin in PIN.PINS.items():
            PIN.verified_bytes(REPO, pin, check_git=True)
            shas["module:" + key] = pin[1]
        if (REPO / PIN.INDEP_PIN[0]).exists():
            PIN.verified_bytes(REPO, PIN.INDEP_PIN, check_git=True, allow_uncommitted=allow_uncommitted)
            shas["module:mb_independent"] = PIN.INDEP_PIN[1] + ("" if PIN.INDEP_PIN[2] else " (UNCOMMITTED_DEV)")
        elif not allow_uncommitted:
            raise Refusal("F2_MISSING", "the independent reconstruction (stream F2) is required for execution")
        if not (REPO / PIN.TUPLE_PIN[0]).exists():
            raise Refusal("F3_MISSING", "the independent tuple (stream F3) is required")
        PIN.verified_bytes(REPO, PIN.TUPLE_PIN, check_git=True)
        shas["module:tuple_independent"] = PIN.TUPLE_PIN[1]
    except PIN.PinError as exc:
        raise Refusal("PIN_MISMATCH", str(exc))
    for commit, word in LINEAGE:
        if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("LINEAGE", commit)
        if word not in git("log", "-1", "--format=%s", commit).stdout:
            raise Refusal("LINEAGE_ROLE", commit)
    shas["helpers"] = check_helpers()
    return shas


def check_governance_state() -> dict:
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    if any(Path(n).name.startswith(R6_NAME) for n in names):
        raise Refusal("R6_EXISTS")
    if git("log", "--all", "--format=%H", "--", f"*{R6_NAME}*").stdout.strip():
        raise Refusal("R6_IN_HISTORY")
    r5 = json.loads(read_pinned("coverage_r5"))
    if r5.get("K5_COVERAGE_COMPLETE") is not False or r5.get("union_open_ranges") != [[306, 309]]:
        raise Refusal("R5_STATE", "r5 no longer lists exactly [306, 309] open")
    m5 = {c["cell"]: c["verdict"] for c in r5["per_m"]["5"]["cells"]}
    if any(m5.get(k) == "PASS" for k in (306, 307, 308, 309)):
        raise Refusal("R5_STATE", "a cell in 306-309 is PASS")
    return {"r6": "absent", "r5_union_open_ranges": r5["union_open_ranges"]}


# ------------------------------------------------------------------ pinned modules (main process)
def load_science(allow_uncommitted: bool, with_decoy_gen: bool = False) -> dict:
    """Every pinned module the evaluation needs, loaded from verified bytes with the guard bound."""
    c1b = PIN.load_c1b(REPO, GUARD)
    c2b = PIN.load_c2b(REPO, GUARD)
    S1, IND7 = PIN.load_rlr307(REPO)
    asm = PIN.load_assembly(REPO, GUARD, with_decoy_gen=with_decoy_gen)
    indep = PIN.load_indep(REPO, allow_uncommitted=allow_uncommitted)
    if indep is None and not allow_uncommitted:
        raise Refusal("F2_MISSING", "the independent reconstruction (stream F2) is required for execution")
    f3 = PIN.load_tuple_indep(REPO, GUARD)
    if f3 is None:
        raise Refusal("F3_MISSING", "the independent tuple (stream F3, gate G-R3b) is required")
    asm["F3"] = f3
    if tuple(S1.LADDER) != S1M.LADDER_RLR:
        raise Refusal("RULES", "rlr307_stage1.LADDER differs from the frozen RLR ladder")
    cp = c1b["c1b_certpw"]
    kc = IND7.kappa_check(cp.KAPPA1, cp.KAPPA2)
    if not (kc["kappa1_ge_sqrt_2_over_pi"] and kc["kappa2_ge_4phi1"]):
        raise Refusal("KAPPA", "a certifier kappa is not a valid upper bound")
    return {"c1b": c1b, "c2b": c2b, "S1": S1, "IND7": IND7, "asm": asm, "indep": indep, "cp": cp,
            "kappa": (cp.KAPPA1, cp.KAPPA2), "kappa_check": kc,
            "identity": {"c1b": c1b["_identity"], "c2b": c2b["_identity"], "assembly": asm["_identity"],
                         "F3": f3._mb308_identity,
                         "F2": None if indep is None else {"revision": getattr(indep, "MODULE_REVISION", None),
                                                           "committed": PIN.INDEP_PIN[2] is not None}}}


def target_geometry(con: dict, sci: dict) -> list:
    """D1/D2 for cell 308, cross-checked against cells.json, REGISTRY_C2 (interval, sub-block count), the guard's
    CELL308 and the guard's own rule."""
    lo, hi, e0, rho = CON.cover_interval(con, TARGET_CELL)
    reg = [b for b in json.loads(CON.read_pinned(REPO, "registry_c2"))["blocks"] if b["cell"] == TARGET_CELL]
    if len(reg) != 1 or (F(reg[0]["e_lo"]), F(reg[0]["e_hi"])) != (lo, hi):
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from REGISTRY_C2's")
    if (lo, hi) != GUARD.CELL308 or e0 != (lo + hi) / 2 or rho != (hi - lo) / 2:
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from the guard's")
    blocks = S1M.plan(sci["S1"], GUARD, lo, hi)
    if len(blocks) != reg[0]["sub_blocks"]:
        raise Refusal("BLOCK_GEOMETRY", "sub-block count differs from REGISTRY_C2's")
    return blocks


def admitted_pairs(blocks: list, x_lo, x_hi, e0) -> list:
    s = {(F(x_lo), F(x_hi)), (F(x_lo), F(x_lo)), (F(x_hi), F(x_hi)), (F(e0), F(e0))}
    for b in blocks:
        s |= {tuple(b["tile"]), tuple(b["hull"]), (b["b"], b["b"])}
    return sorted((fs(a), fs(c)) for a, c in s)


# ------------------------------------------------------------------ Stage 1: worker pool (spawned processes)
_W: dict = {}


def check_cpu_caps() -> dict:
    """The effective RLIMIT_CPU must allow every declared per-job cap (REVIEW_A0 C3); recorded in the result."""
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    need = max(c for caps in RUNG_CPU_CAP_S.values() for c in caps.values())
    inf = resource.RLIM_INFINITY
    if (hard != inf and hard < need) or (soft != inf and soft < need):
        raise Refusal("CPU_CAP", "an outer RLIMIT_CPU is below a declared per-job cap")
    return {"declared_per_job_s": {k: {str(r): c for r, c in v.items()} for k, v in RUNG_CPU_CAP_S.items()},
            "parent_rlimit_cpu": ["unlimited" if soft == inf else soft, "unlimited" if hard == inf else hard]}


def _set_job_cap(kind: str, rung: int) -> dict:
    cap = RUNG_CPU_CAP_S[kind][rung]
    ru = resource.getrusage(resource.RUSAGE_SELF)
    used = int(ru.ru_utime + ru.ru_stime) + 1
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    want = used + cap
    if hard != resource.RLIM_INFINITY and hard < want:
        raise S1M.InfrastructureFailure("CPU_CAP_EFFECTIVE_BELOW_DECLARED")
    resource.setrlimit(resource.RLIMIT_CPU, (want, want + 30 if hard == resource.RLIM_INFINITY else hard))
    got = resource.getrlimit(resource.RLIMIT_CPU)[0] - used
    if got != cap:
        raise S1M.InfrastructureFailure("CPU_CAP_EFFECTIVE_DIFFERS_FROM_DECLARED")
    return {"declared_s": cap, "effective_s": got}


def _worker_init(mode: str, repo: str, grant_commit: str, pairs: list, driver_sha: str, latent: str,
                 allow_uncommitted: bool) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    if sha(HERE.read_bytes()) != driver_sha:
        raise RuntimeError("worker: driver bytes differ from the parent's")
    check_helpers()
    c1b = PIN.load_c1b(Path(repo), GUARD)
    c2b = PIN.load_c2b(Path(repo), GUARD)
    S1, _ = PIN.load_rlr307(Path(repo))
    vf = PIN.load_verifier(Path(repo), GUARD)
    if mode == "target":
        GUARD.arm_target(repo, grant_commit, [(F(a), F(b)) for a, b in pairs])
    elif mode != "decoy":
        raise RuntimeError(f"worker: unknown mode {mode}")
    _W.clear()
    _W.update({"c1b": c1b, "c2b": c2b, "S1": S1, "vf": vf, "guard": GUARD, "latent": latent,
               "set_flags": PIN.set_c1b_flags, "mode": mode})


def _worker_job(kind: str, block: dict, rung: int, payload=None) -> dict:
    b = {"index": block["index"], "tile": tuple(F(x) for x in block["tile"]),
         "hull": tuple(F(x) for x in block["hull"]), "b": F(block["b"])}
    cap = _set_job_cap(kind, rung)
    out = S1M.run_job(_W, kind, b, rung, payload)
    out["cpu_cap"] = cap
    return out


def _ser_block(b: dict) -> dict:
    return {"index": b["index"], "tile": [fs(x) for x in b["tile"]], "hull": [fs(x) for x in b["hull"]], "b": fs(b["b"])}


def stage1(mode: str, blocks: list, grant_commit: str, own_sha: str, sci: dict, ladder: dict, pairs: list,
           workers: int = WORKERS, which=None, allow_uncommitted: bool = False) -> dict:
    """S1a-S1d. Raises on any infrastructure failure, IndependentCheckFailed on a verifier refutation or a ladder
    disagreement, Inconsistent on L > U."""
    latent = S1M.FORMAL_LATENT if mode == "target" else "decoy certificate (never juxtapose with any tail number)"
    ser = {b["index"]: _ser_block(b) for b in blocks}
    todo = S1M.jobs(blocks, ladder, which)
    results = {}
    ex = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"),
                             max_tasks_per_child=1, initializer=_worker_init,
                             initargs=(mode, str(REPO), grant_commit, pairs, own_sha, latent, allow_uncommitted))
    try:
        pending = {ex.submit(_worker_job, k, ser[i], r): (k, i, r) for k, i, r in todo}
        while pending:
            done, _ = wait(list(pending), return_when=FIRST_COMPLETED)
            for fut in done:
                key = pending.pop(fut)
                res = fut.result()                                   # a worker failure propagates
                results[key] = res
                if key[0] == "C1B" and res.get("status") == "CERTIFIED" and res.get("cert") and \
                        key[2] <= S1M.C1B_VERIFY_MAX_D:
                    vkey = ("VER", key[1], key[2])
                    pending[ex.submit(_worker_job, "VER", ser[key[1]], key[2], res["cert"])] = vkey
    finally:
        procs = list(getattr(ex, "_processes", {}).values())
        ex.shutdown(wait=False, cancel_futures=True)
        for p in procs:
            if p.is_alive():
                p.terminate()
    S1, IND7, cp, indep = sci["S1"], sci["IND7"], sci["cp"], sci["indep"]
    out_blocks, U_list, rlr_recs, n_ver = [], [], [], 0
    for b in blocks:
        i = b["index"]
        rl = [results[("RLR", i, d)] for d in ladder["RLR"] if ("RLR", i, d) in results]
        c1 = [results[("C1B", i, d)] for d in ladder["C1B"] if ("C1B", i, d) in results]
        c2 = [results[("C2B", i, n)] for n in ladder["C2B"] if ("C2B", i, n) in results]
        vers = {d: results[("VER", i, d)]["verification"] for d in ladder["C1B"] if ("VER", i, d) in results}
        n_ver += len(vers)
        run = bool(rl or c1 or c2)
        try:
            brec = S1M.rlr_block(S1, IND7, cp, rl, sci["kappa"]) if rl else None
        except ValueError as exc:
            raise IndependentCheckFailed(f"block {i}: {exc}")
        if brec is not None:
            brec = dict(brec, _kind="RLR_BLOCK", _hull=[fs(b["hull"][0]), fs(b["hull"][1])])
        if indep is not None and rl and not SUP.f2_ladder_check(indep, [r["record"] for r in rl], brec):
            raise IndependentCheckFailed(f"block {i}: Lemma Lad differs from stream F2")
        pw = S1M.pointwise(c2, c1, vers) if run else {"status": "NOT_RUN", "U": None, "L": None}
        if pw["status"] == "INCONSISTENT":
            raise Inconsistent(f"pointwise drift of block {i}: a verifier refutation or a cross-implementation alarm")
        U_list.append(None if pw.get("U") is None else F(pw["U"]))
        rlr_recs.append(brec)
        strip = lambda r: {k: v for k, v in r.items() if k != "cert"}  # noqa: E731
        out_blocks.append({"index": i, "tile": ser[i]["tile"], "hull": ser[i]["hull"], "b": ser[i]["b"], "run": run,
                           "rlr_rungs": rl, "rlr_block": None if brec is None else jsonable(brec),
                           "c2b_rungs": c2, "c1b_rungs": [strip(r) for r in c1],
                           "c1b_certificates": {r["rung"]: r.get("cert") for r in c1 if r.get("cert")},
                           "verifications": vers, "pointwise": jsonable(pw)})
    return {"mode": mode, "ladder": {k: list(v) for k, v in ladder.items()}, "workers": workers,
            "blocks": out_blocks, "U_list": U_list, "rlr_recs": rlr_recs, "n_verifications": n_ver,
            "verifiers": {"C2B": "vd_pl.verify_pl (pinned)", "C1B": f"vd_verify.verify for d <= {S1M.C1B_VERIFY_MAX_D} "
                          "only; higher degrees NOT_INDEPENDENTLY_VERIFIED", "budget": jsonable(S1M.VERIFY_BUDGET)}}


def public_stage1(st1: dict) -> dict:
    return {k: v for k, v in st1.items() if k not in ("U_list", "rlr_recs")} | {
        "U": [None if u is None else fs(u) for u in st1["U_list"]]}


# ------------------------------------------------------------------ composition, Stage 2, decision
def compose_and_consume(sci: dict, con: dict | None, blocks: list, st1: dict, S_I1: dict, reg_sets: list,
                        bundle: dict) -> tuple:
    try:
        sup = SUP.compose(blocks, st1["U_list"], st1["rlr_recs"], S_I1, reg_sets, con, sci["IND7"], sci["cp"],
                          sci["indep"], GUARD)
    except SUP.IndependentCheckFailed as exc:
        raise IndependentCheckFailed(str(exc))
    triples = [(b["tile"][0], b["tile"][1], sup["blocks"][k]["_S"]) for k, b in enumerate(blocks)]
    try:
        st2 = CON.stage2(sci["asm"], GUARD, bundle, triples, sci["indep"])
    except CON.IndependentCheckFailed as exc:
        raise IndependentCheckFailed(str(exc))
    return jsonable(sup), st2


def decide(st2: dict) -> dict:
    """The frozen mechanical outcome (design section 5.4); Gamma = 0 does NOT close."""
    if st2["Gamma_dec_lt_0"]:
        return {"mechanical_outcome": "CELL308_CLOSED_UNDER_MB", "reason": "Gamma_dec < 0 (exact)"}
    return {"mechanical_outcome": "CELL308_NOT_CLOSED_UNDER_MB", "reason": "Gamma_dec >= 0 (exact)"}


def evaluate_target(con: dict, prep: dict) -> dict:
    """The ONE scientific evaluation (after the marker)."""
    GUARD.arm_target(str(REPO), prep["grant_commit"], [(F(a), F(b)) for a, b in prep["pairs"]])
    st1 = stage1("target", prep["blocks"], prep["grant_commit"], prep["own_sha"], prep["sci"], prep["ladder"],
                 prep["pairs"])
    sup, st2 = compose_and_consume(prep["sci"], con, prep["blocks"], st1, prep["A_I1"], prep["reg_sets"],
                                   prep["bundle"])
    return {"cell": TARGET_CELL, "stage1": public_stage1(st1), "supply": sup, "stage2": st2, "decision": decide(st2)}


# ------------------------------------------------------------------ the grant (derived chain)
def check_grant(own_sha: str) -> dict:
    head = git("rev-parse", "HEAD").stdout.strip()
    if not os.path.lexists(REPO / GRANT_REL):
        raise Refusal("GRANT_MISSING")
    if os.path.islink(REPO / GRANT_REL):
        raise Refusal("GRANT_INVALID", "the grant is a symlink")
    if git("log", "-1", "--format=%H", "--", GRANT_REL).stdout.strip() != head:
        raise Refusal("GRANT_INVALID", "HEAD is not the grant commit")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.split() != [GRANT_REL]:
        raise Refusal("GRANT_INVALID", "the grant commit changes more than the grant")
    g = json.loads((REPO / GRANT_REL).read_bytes())
    if g.get("schema") != "rebaseguard.p5y.k5.cell308-mb-r1.grant.v1" or g.get("exactly_once") is not True \
            or g.get("cell") != TARGET_CELL or g.get("route") != "MB" or g.get("closure_only") is not True:
        raise Refusal("GRANT_INVALID", "schema / cell / route / scope")
    if g.get("driver_sha256") != own_sha:
        raise Refusal("GRANT_INVALID", "driver bytes differ from the granted driver")
    fz = freeze_commit()
    review_c = git("rev-parse", "HEAD^").stdout.strip()
    qual_c = git("rev-parse", "HEAD^^").stdout.strip()
    if (g.get("freeze_commit"), g.get("qualification_commit"), g.get("qualification_review_commit")) != \
            (fz, qual_c, review_c) or git("rev-parse", "HEAD^^^").stdout.strip() != fz:
        raise Refusal("GRANT_INVALID", "the chain must be freeze -> qualification -> review -> grant, as named")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", review_c).stdout.split() != [QREVIEW_REL]:
        raise Refusal("GRANT_INVALID", "the review commit changes more than the review")
    qfiles = git("diff-tree", "--no-commit-id", "--name-only", "-r", qual_c).stdout.split()
    if not qfiles or any(not f.startswith(QUAL_DIR_REL) for f in qfiles) or QUAL_REL not in qfiles:
        raise Refusal("GRANT_INVALID", "the qualification commit is not qualification evidence only")
    q = json.loads(git("show", f"{qual_c}:{QUAL_REL}").stdout)
    if q.get("pass") is not True or q.get("review_mode") is not False or q.get("freeze_commit") != fz:
        raise Refusal("GRANT_INVALID", "the qualification report is not an official PASS at the freeze commit")
    if not verdict_ok((REPO / QREVIEW_REL).read_text(), "QUALIFICATION_ACCEPTED"):
        raise Refusal("REVIEW_VERDICT", "qualification review is not QUALIFICATION_ACCEPTED")
    if g.get("input_manifest_sha256") != sha((REPO / MANIFEST_REL).read_bytes()):
        raise Refusal("GRANT_INVALID", "the grant does not bind the frozen input manifest")
    return {"grant_commit": head, "grant_sha256": sha((REPO / GRANT_REL).read_bytes()), "freeze_commit": fz,
            "qualification_commit": qual_c, "qualification_review_commit": review_c}


# ------------------------------------------------------------------ persistence, seal and materialization
def serialize(obj: dict) -> bytes:
    body = dict(obj)
    body["sha256"] = sha(json.dumps(body, sort_keys=True).encode())
    return (json.dumps(body, indent=1, sort_keys=True) + "\n").encode()


def persist_pending(data: bytes) -> str:
    w = git("hash-object", "-w", "--stdin", input_bytes=data)
    blob = w.stdout.strip()
    if w.returncode or blob != git_blob_id(data):
        raise OSError("hash-object did not store the produced bytes")
    if git("update-ref", PENDING_REF, blob, "0" * 40).returncode:
        raise OSError("the pending-result ref could not be created")
    return blob


def persist_emergency(data: bytes) -> str:
    dfd = os.open(git_dir(), os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = os.open(EMERGENCY_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dfd)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        os.close(dfd)
    return str(git_dir() / EMERGENCY_NAME)


def seal_blob(blob: str, message: str) -> str:
    last = None
    for delay in (0.0, *SEAL_RETRY_DELAYS):
        time.sleep(delay)
        head = git("rev-parse", "HEAD").stdout.strip()
        with tempfile.TemporaryDirectory(prefix="mb308seal") as td:
            idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
            msgf = Path(td) / "msg"
            msgf.write_text(message)
            steps = [git("read-tree", head, env_extra=idx),
                     git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}", env_extra=idx)]
            tree = git("write-tree", env_extra=idx)
            if any(s.returncode for s in steps) or tree.returncode:
                last = "index"
                continue
            commit = git("commit-tree", tree.stdout.strip(), "-p", head, "-F", str(msgf))
            if commit.returncode:
                last = "commit-tree"
                continue
            cid = commit.stdout.strip()
            if git("update-ref", QUALIFIED_BRANCH, cid, head).returncode:
                last = "update-ref"
                continue
            entry = git("ls-tree", cid, "--", RESULT_REL).stdout.split()
            if entry[:3] != ["100644", "blob", blob]:
                raise OSError("the sealed entry is not the persisted blob")
            git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}")
            return cid
    raise OSError(f"seal failed at {last}")


def materialize(blob: str) -> None:
    data = subprocess.run(["/usr/bin/git", "-C", str(REPO), "cat-file", "blob", blob], capture_output=True,
                          env=dict(ENV), stdin=subprocess.DEVNULL).stdout
    if git_blob_id(data) != blob:
        raise OSError("the object store returned other bytes")
    fds = [os.open(str(REPO), os.O_RDONLY | os.O_DIRECTORY)]
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
            while chunk := os.read(rfd, 1 << 20):
                back += chunk
        finally:
            os.close(rfd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or back != data:
            raise OSError("the materialized copy is not the sealed bytes")
    finally:
        for fd in reversed(fds):
            os.close(fd)


def seal_message(status: str) -> str:
    return (f"p5y: K5 cell-308 MB r1 — SEAL of the one cell-308 MB evaluation ({status})\n\n"
            f"Committed by {NS_REL}/code/mb308_driver.py from the in-memory bytes (object store + pending ref), "
            "not from a worktree file; the result was not inspected before this commit.\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")


def fallback_bytes(common_min: dict, stage: str, exc: BaseException) -> bytes:
    rec = {"schema": SCHEMA, "status": "POST_MARKER_RECORDING_FAILED", "stage": stage,
           "error": f"{type(exc).__name__}: {exc}"[:500], "target_evaluations": 1,
           "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE", **common_min}
    try:
        return serialize(rec)
    except BaseException:
        return (json.dumps({"status": "POST_MARKER_RECORDING_FAILED", "stage": stage,
                            "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE"}) + "\n").encode()


def _eval_cap(*_):
    raise TimeoutError(f"evaluation exceeded {EVAL_CAP_S} s")


def failure_kind(exc: BaseException) -> str:
    if isinstance(exc, (IndependentCheckFailed, SUP.IndependentCheckFailed, CON.IndependentCheckFailed)):
        return "INDEPENDENT_CHECK_FAILED"
    if isinstance(exc, Inconsistent):
        return "INCONSISTENT"
    if isinstance(exc, CON.Stop) and exc.code == "C6_EMPTY_BAND":
        return "C6_REFUSED"
    return "TARGET_EVALUATION_FAILED"


def after_marker(con, prep, common: dict, evaluator, t0: float, persist=None, sealer=None, materializer=None) -> int:
    """From here the target is consumed. Nothing raises out of this function; every outcome is evidence."""
    persist = persist or persist_pending
    sealer = sealer or seal_blob
    materializer = materializer or materialize
    signal.signal(signal.SIGALRM, _eval_cap)
    common_min = {"cell": TARGET_CELL, "grant": common.get("grant"), "driver_sha256": common.get("driver_sha256"),
                  "consumed_ref": CONSUMED_REF}
    try:
        try:
            signal.alarm(EVAL_CAP_S)
            t_eval = time.time()
            tgt = evaluator(con, prep)
            signal.alarm(0)
            status = "TARGET_EVALUATED"
        except BaseException as exc:
            signal.alarm(0)
            kind = failure_kind(exc)
            tgt, status = {"error": f"{type(exc).__name__}: {exc}"[:800], "failure_kind": kind}, kind
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        common.update({"status": status, "target_evaluated": status == "TARGET_EVALUATED", "target_evaluations": 1,
                       "consumed_ref": CONSUMED_REF, "target": tgt,
                       "mechanical_outcome": (tgt.get("decision", {}).get("mechanical_outcome")
                                              if status == "TARGET_EVALUATED" else "CELL308_EXECUTION_INDETERMINATE"),
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                       "evaluation_wall_seconds": round(time.time() - t_eval, 3) if "t_eval" in locals() else None,
                       "peak_rss_bytes": usage.ru_maxrss,
                       "cpu_seconds_parent": round(usage.ru_utime + usage.ru_stime, 3),
                       "cpu_seconds_workers": round(cusage.ru_utime + cusage.ru_stime, 3)})
        data = serialize(common)
    except BaseException as exc:
        status, data = "POST_MARKER_RECORDING_FAILED", fallback_bytes(common_min, "record", exc)
    blob, channel = None, None
    try:
        blob, channel = persist(data), "pending_ref"
    except BaseException:
        try:
            persist_emergency(data)
            channel = "emergency_file"
        except BaseException:
            print("MB308 CONSUMED_UNRECORDED: the marker exists and no evidence channel worked. NEVER run execute again.")
            return 6
    if blob is None:
        print("MB308 UNSEALED: evidence persisted in the git dir; run `seal-only`. NEVER run execute again.")
        return 4
    try:
        cid = sealer(blob, seal_message(status))
    except BaseException:
        print(f"MB308 UNSEALED: evidence persisted ({channel}); run `seal-only`. NEVER run execute again.")
        return 4
    try:
        materializer(blob)
    except BaseException:
        print(f"MB308 SEALED {cid} (status {status}); worktree copy NOT materialized: run `seal-only`.")
        return 7
    print(f"MB308 SEALED {cid} (status {status}; one target evaluation; result not printed)")
    return 0 if status == "TARGET_EVALUATED" else 5


def keep_awake() -> dict:
    """Environmental only (results never depend on it): ask macOS not to idle-sleep while this process lives."""
    try:
        p = subprocess.Popen(["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"caffeinate_pid": p.pid}
    except OSError as exc:
        return {"caffeinate": f"unavailable ({type(exc).__name__})"}


# ------------------------------------------------------------------ controls and preparation (before the marker)
def controls(con: dict, sci: dict, k: int) -> dict:
    """C-A and C-B on cell k (305 rehearsal or 308 target control); equality only."""
    ca = CON.control_ca(con, k, sci["IND7"])
    bundle = CON.bundle_for(ca["_ci"], ca["_A"], ca["_committed"])
    cb = CON.control_cb(sci["asm"], GUARD, bundle, sci["indep"])
    return {"C_A": CON.public(ca), "C_B": cb, "pass": bool(ca["reproduces_C2_exactly"] and cb["reproduces_exactly"]),
            "_ca": ca, "_bundle": bundle}


def prepare_target(con: dict, ctl: dict, own_sha: str, grant: dict, sci: dict) -> dict:
    blocks = target_geometry(con, sci)
    lo, hi, e0, _ = CON.cover_interval(con, TARGET_CELL)
    pairs = admitted_pairs(blocks, lo, hi, e0)
    if frozenset((F(a), F(b)) for a, b in pairs) != GUARD.target_admitted_set():
        raise Refusal("BLOCK_GEOMETRY", "the admitted set differs from the guard's frozen set")
    return {"blocks": blocks, "pairs": pairs, "grant_commit": grant["grant_commit"], "own_sha": own_sha, "sci": sci,
            "ladder": {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N, "C1B": S1M.LADDER_C1B_D},
            "A_I1": ctl["_ca"]["_A"], "reg_sets": CON.i1_sets(REPO, TARGET_CELL), "bundle": ctl["_bundle"],
            "kappa_check": sci["kappa_check"]}


def run_execute(own_sha: str, prepare=None, evaluator=None, persist=None, sealer=None, materializer=None) -> int:
    """Injection points exist for the qualification's DECOY flow tests only; the CLI never passes them."""
    evaluator = evaluator or evaluate_target
    t0, started = time.time(), utc()
    check_flags()
    ident = check_identity()
    check_not_evaluated()
    check_result_paths()
    check_clean()
    grant = check_grant(own_sha)
    shas = check_bindings()
    state = check_governance_state()
    pre = check_seal_preconditions()
    pre["cpu_caps"] = check_cpu_caps()
    awake = keep_awake()
    try:
        con = load_consumer()
        sci = load_science(allow_uncommitted=False)
        ctl = control(con, sci, TARGET_CELL)
    except CON.ConsumerRefusal as exc:
        raise Refusal(exc.code, str(exc))
    except PIN.PinError as exc:
        raise Refusal("PIN_MISMATCH", str(exc))
    common = {"schema": SCHEMA, "cell": TARGET_CELL, "m": 5, "route": "MB", "scope": "CLOSURE_ONLY",
              "identity": ident, "grant": grant, "input_sha256": shas, "governance_state_before": state,
              "seal_preconditions": pre, "driver_sha256": own_sha, "started_utc": started,
              "controls": {k: v for k, v in ctl.items() if not k.startswith("_")}, "python": sys.version.split()[0],
              "environment": awake}
    if not ctl["pass"]:
        common.update({"status": "CONTROL_FAILED", "target_evaluated": False, "target_evaluations": 0,
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3)})
        data = serialize(common)
        try:
            blob = (persist or persist_pending)(data)
            cid = (sealer or seal_blob)(blob, seal_message("CONTROL_FAILED"))
            (materializer or materialize)(blob)
        except BaseException:
            print("MB308 CONTROL_FAILED: not fully sealed; run `seal-only`. The target was not evaluated.")
            return 4
        print(f"MB308 CONTROL_FAILED sealed {cid}; the target was not evaluated")
        return 3
    try:
        prep = (prepare or prepare_target)(con, ctl, own_sha, grant, sci)
    except CON.ConsumerRefusal as exc:
        raise Refusal(exc.code, str(exc))
    common.update({"kappa_check": prep.get("kappa_check"), "admitted_pairs": prep.get("pairs"),
                   "blocks_planned": [_ser_block(b) for b in prep.get("blocks", [])]})
    check_result_paths()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    signal.alarm(0)
    if git("update-ref", CONSUMED_REF, grant["grant_commit"], "0" * 40).returncode != 0:
        raise Refusal("CONSUMED", "the exactly-once marker could not be created: the target is never evaluated twice")
    return after_marker(con, prep, common, evaluator, t0, persist, sealer, materializer)


def load_consumer():
    return CON.load_consumer(REPO)


def control(con, sci, k):
    return controls(con, sci, k)


def run_seal_only() -> int:
    """Seal and/or materialize EXISTING evidence. Never computes, never evaluates, never touches the consumer."""
    check_flags()
    check_identity()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    marker = git("rev-parse", "-q", "--verify", CONSUMED_REF).stdout.strip()
    pending = git("rev-parse", "-q", "--verify", PENDING_REF).stdout.strip()
    emergency = git_dir() / EMERGENCY_NAME
    if not pending and os.path.lexists(emergency):
        if os.path.islink(emergency):
            raise Refusal("SEAL_ONLY", "the emergency evidence file is a symlink")
        fd = os.open(emergency, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            data = b""
            while chunk := os.read(fd, 1 << 20):
                data += chunk
        finally:
            os.close(fd)
        pending = persist_pending(data)
    if not pending:
        raise Refusal("SEAL_ONLY", "no persisted evidence (no pending ref, no emergency file)")
    data = subprocess.run(["/usr/bin/git", "-C", str(REPO), "cat-file", "blob", pending], capture_output=True,
                          env=dict(ENV), stdin=subprocess.DEVNULL).stdout
    try:
        rec = json.loads(data)
        status = rec.get("status", "UNKNOWN")
    except ValueError:
        rec, status = {}, "UNPARSEABLE_EVIDENCE"
    if status == "CONTROL_FAILED" and marker:
        raise Refusal("SEAL_ONLY", "CONTROL_FAILED evidence but the marker exists")
    if status != "CONTROL_FAILED" and not marker:
        raise Refusal("SEAL_ONLY", "post-marker evidence without a marker")
    entry = git("ls-tree", "HEAD", "--", RESULT_REL).stdout.split()
    if entry and entry[:3] != ["100644", "blob", pending]:
        raise Refusal("SEAL_ONLY", "HEAD holds a different result entry")
    cid = git("rev-parse", "HEAD").stdout.strip()
    if not entry:
        if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
            raise Refusal("DIRTY_TREE", "seal-only needs an otherwise clean tree")
        try:
            cid = seal_blob(pending, seal_message(f"{status}, sealed by seal-only"))
        except OSError as exc:
            raise Refusal("UNSEALED", str(exc))
    if not os.path.lexists(REPO / RESULT_REL):
        try:
            materialize(pending)
        except (OSError, FileExistsError) as exc:
            print(f"MB308 SEALED {cid} (status {status}); materialization refused: {type(exc).__name__}")
            return 7
    else:
        st = os.lstat(REPO / RESULT_REL)
        same = False
        if stat.S_ISREG(st.st_mode):
            fd = os.open(REPO / RESULT_REL, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                back = b""
                while chunk := os.read(fd, 1 << 20):
                    back += chunk
            finally:
                os.close(fd)
            same = back == data
        if not same:
            print(f"MB308 SEALED {cid} (status {status}); the worktree object at the result path is NOT the sealed bytes")
            return 7
    print(f"MB308 SEALED {cid} (seal-only; status {status}; nothing computed)")
    return 0


# ------------------------------------------------------------------ rehearsal and decoy (qualification only)
def rehearse(k: int) -> dict:
    """Cell 305 only: C-A (C2's committed record under S_I1) and C-B (tptb_tail reproduction gates at s = rho).
    Equality booleans only; no new-route value on 305."""
    if k not in REHEARSAL_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", str(k))
    con = load_consumer()
    sci = load_science(allow_uncommitted=True)
    ctl = controls(con, sci, k)
    ca = ctl["C_A"]
    return {"cell": k, "C_A": {"reproduces_C2_exactly": ca["reproduces_C2_exactly"],
                               "field_matches": ca["field_matches"], "provenance": ca["provenance"]},
            "C_B": ctl["C_B"], "pass": ctl["pass"], "F2_present": sci["indep"] is not None}


def decoy_cover(k: int) -> tuple:
    cells = [c for c in json.loads(CON.read_pinned(REPO, "cells_json")) if c["detector"] == "CUSUM" and c["index"] == k]
    c = cells[0] if len(cells) == 1 else None
    if c is None or any(c[x][1] != "0/1" for x in ("left", "right", "e0", "rho")):
        raise Refusal("DECOY_GEOMETRY", str(k))
    lo, hi, e0, rho = (F(c[x][0]) for x in ("left", "right", "e0", "rho"))
    if e0 - rho != lo or e0 + rho != hi:
        raise Refusal("DECOY_GEOMETRY", f"{k}: cover is not [e0 - rho, e0 + rho]")
    return lo, hi, e0, rho


def r0_order3_variant(bundle: dict) -> dict:
    """The r = 0 adopted order-3 bound made to BIND (stream F3 note: decoy_gen never does): Sclosed:0:3 + Sclosed:3 is
    set below sup_S0[3]; the decoy's own committed record no longer applies and is dropped."""
    import copy
    p = copy.deepcopy(bundle)
    s3 = F(p["meas"]["sup_S0"][3])
    p["aux"]["candidate_suprema"]["Sclosed:0:3"] = fs(s3 / 10)
    p["aux"]["midpoint_eps"]["Sclosed:3"] = fs(s3 / 1000)
    p.pop("committed", None)
    p["decoy_meta"] = dict(p["decoy_meta"], r0_order3_binds=True)
    return p


def supply_scaled_variant(bundle: dict, factor: int = 1000) -> dict:
    """The decoy supply scaled up so that the Stage-1 members (D14M, G) can BIND in the per-block minimum (decoy_gen's
    supplies are small); the decoy's committed record no longer applies and is dropped."""
    import copy
    p = copy.deepcopy(bundle)
    p["supply"] = {j: fs(F(v) * factor) for j, v in p["supply"].items()}
    p.pop("committed", None)
    p["decoy_meta"] = dict(p["decoy_meta"], supply_scaled=factor)
    return p


def decoy_bundles(sci: dict, e0: F, rho: F) -> list:
    """Manufactured TC-T bundles (stream ASSEMBLY decoy_gen, pinned) with the decoy cell's geometry; label DECOY; plus
    the r = 0 order-3-binding variant of the first one and a supply-scaled variant of the second one."""
    DG = sci["asm"]["DG"]
    saved = DG.GEOMS
    DG.GEOMS = [(e0, rho)]
    try:
        out = [DG.make_decoy(i, DECOY_SEED, regime, sign, cap, 0) for i, (regime, sign, cap) in enumerate(DECOY_BUNDLES)]
    finally:
        DG.GEOMS = saved
    return out + [r0_order3_variant(out[0]), supply_scaled_variant(out[1])]


def decoy(k: int, own_sha: str, workers: int, first_blocks, dev_ladder: bool) -> dict:
    if k not in DECOY_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", f"{k} is not a declared decoy")
    lo, hi, e0, rho = decoy_cover(k)
    GUARD.guard_drift(lo, hi)                                          # decoy mode: refuses the band
    caps = check_cpu_caps()
    sci = load_science(allow_uncommitted=True, with_decoy_gen=True)
    blocks = S1M.plan(sci["S1"], GUARD, lo, hi)
    for b in blocks:
        GUARD.guard_drift(*b["hull"])
        GUARD.guard_drift(b["b"])
    ladder = S1M.DEV_LADDER if dev_ladder else {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N,
                                                "C1B": S1M.LADDER_C1B_D}
    which = None if first_blocks is None else set(range(first_blocks))
    t0 = time.time()
    st1 = stage1("decoy", blocks, "", own_sha, sci, ladder, [], workers, which, allow_uncommitted=True)
    t1 = time.time()
    out = {"decoy_cell": k, "blocks_total": len(blocks), "blocks_run": sorted(which) if which else "all", "cpu_caps": caps,
           "dev_ladder": dev_ladder, "stage1": public_stage1(st1), "stage1_wall_seconds": round(t1 - t0, 1)}
    if k == 297:
        runs = []
        for bundle in decoy_bundles(sci, e0, rho):
            S_dec = {j: F(bundle["supply"][j]) for j in FIELDS}
            try:
                sup, st2 = compose_and_consume(sci, None, blocks, st1, S_dec, [], bundle)
                runs.append({"decoy_meta": bundle["decoy_meta"], "supply": sup, "stage2": st2,
                             "decoy_outcome": "DECOY_CLOSED" if st2["Gamma_dec_lt_0"] else "DECOY_NOT_CLOSED"})
            except (IndependentCheckFailed, CON.Stop, SUP.SupplyRefusal) as exc:
                runs.append({"decoy_meta": bundle["decoy_meta"], "stop": f"{type(exc).__name__}: {exc}"[:400]})
        out["stage2_decoys"] = runs
        out["stage2_wall_seconds"] = round(time.time() - t1, 1)
    out["latent_proxy"] = "decoy values; never juxtapose with any tail-cell number"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("preflight", "rehearse", "decoy", "execute", "seal-only"))
    ap.add_argument("--cell", type=int)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--first-blocks", type=int)
    ap.add_argument("--dev-ladder", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    own_sha = sha(HERE.read_bytes())

    def wall_cap(*_):
        raise Refusal("WALL_CAP", f"{PRE_CAP_S} s")

    signal.signal(signal.SIGALRM, wall_cap)
    signal.alarm(DECOY_CAP_S if a.mode == "decoy" else PRE_CAP_S)
    try:
        if a.mode in ("preflight", "execute", "seal-only") and a.cell is not None:
            raise Refusal("CELL_OUT_OF_SCOPE", "only rehearse / decoy take --cell; execute is cell 308 only")
        if a.mode != "decoy" and (a.dev_ladder or a.first_blocks is not None):
            raise Refusal("DEV_FLAG_REFUSED", "--dev-ladder / --first-blocks exist in decoy mode only")
        if a.mode == "preflight":
            check_not_evaluated()
            out = {"mode": "preflight", "input_sha256": check_bindings(), "governance_state": check_governance_state(),
                   "driver_sha256": own_sha}
            load_consumer()
            out["identity"] = load_science(allow_uncommitted=False)["identity"]
            print("MB308 PREFLIGHT PASS")
        elif a.mode == "rehearse":
            check_not_evaluated()
            check_bindings(allow_uncommitted=True)
            check_governance_state()
            t0 = time.time()
            out = {"mode": "rehearse", **rehearse(a.cell), "wall_seconds": round(time.time() - t0, 3),
                   "driver_sha256": own_sha, "utc": utc()}
            print(f"MB308 REHEARSE cell {a.cell}: C-A and C-B reproduce the committed record exactly = {out['pass']}")
            if not out["pass"]:
                if a.out:
                    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
                return 3
        elif a.mode == "decoy":
            if a.workers > 5 or a.workers < 1:
                raise Refusal("WORKERS", "1..5 workers")
            check_bindings(allow_uncommitted=True)
            t0 = time.time()
            out = decoy(a.cell, own_sha, a.workers, a.first_blocks, a.dev_ladder)
            cu = resource.getrusage(resource.RUSAGE_CHILDREN)
            out.update({"mode": "decoy", "driver_sha256": own_sha, "utc": utc(), "wall_seconds": round(time.time() - t0, 1),
                        "cpu_seconds_workers": round(cu.ru_utime + cu.ru_stime, 1)})
            print(f"MB308 DECOY cell {a.cell}: stage 1 in {out['stage1_wall_seconds']} s")
        elif a.mode == "execute":
            return run_execute(own_sha)
        else:
            return run_seal_only()
        if a.out:
            Path(a.out).write_text(json.dumps(jsonable(out), indent=1, sort_keys=True) + "\n")
        return 0
    except (Refusal, PIN.PinError, GUARD.QuarantineRefusal, CON.ConsumerRefusal) as e:
        print(f"MB308 REFUSED {e}")
        return 4 if getattr(e, "code", None) == "UNSEALED" else 2
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    sys.exit(main())
