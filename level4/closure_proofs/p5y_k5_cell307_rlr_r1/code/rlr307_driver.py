"""Cell-307 RLR campaign (r1) -- the cell-307-only exactly-once driver.

ONE scientific evaluation, after freeze -> independent qualification review (QUALIFICATION_ACCEPTED) -> grant:
  Stage 1  block-uniform RLR certification of A1, A2 over cell 307's cover interval (rlr307_stage1 rules P1-P5), by the
           pinned overnight certifier executed from its pinned bytes, in a pool of spawned worker processes;
  Stage 2  S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell)) consumed by C2's frozen consumer path (TC-T and
           the K5-B direct clause, from pinned bytes), giving Gamma(5, 307; S_RLR) and the consumer's `pass` (Gamma < 0).
Every composition layer is recomputed by rlr307_independent and must agree exactly.

Exactly-once mechanics are C12-R2's validated design (seal from memory), re-targeted:
  * before the marker: identity (qualified worktree, git dir, common dir, branch), interpreter flags -I -S -B, no prior
    evaluation (no marker / pending ref / result anywhere / emergency file), no filesystem object at any guarded result
    path (lstat), clean tree including ignored files in the namespace, the derived grant chain freeze -> qualification
    -> review -> grant, every pinned input (sha256 + git blob), the governance state (r5 as expected, no r6), every seal
    precondition (object-store write probe, trial commit object, writable git dir), the helper-module pins, and the
    CONTROL: cell 307 under C2's committed supply S_I1 must reproduce C2's committed record exactly (no new target
    information: every field is compared for equality with the committed record);
  * the marker `refs/p5y-k5-cell307-rlr-r1/target-consumed` -> the grant commit is created by CAS immediately before
    Stage 1; from then on the target is consumed, even if anything fails;
  * after the marker nothing escapes (`after_marker`): signals are ignored, the evaluation has its own wall cap, every
    failure becomes sealed evidence; the result is serialized in memory, written to the object store (blob id checked),
    recorded under a pending ref (second channel: an O_EXCL|O_NOFOLLOW file in the git dir), committed through a
    private index with --cacheinfo, and only then materialized in the worktree (O_EXCL|O_NOFOLLOW, read back);
  * `seal-only` seals / materializes existing evidence only and never computes.

modes
    preflight                      read-only anywhere: bindings, governance, no prior evaluation, module identities
    rehearse --cell 305            read-only: C2's committed cell-305 record reproduced exactly under S_I1, and the
                                   Stage-2 path with a NEUTRAL cell record (S_RLR == S_I1) reproducing it too
    decoy-stage1 --cell 297|316    Stage 1 in DECOY mode on a declared decoy cover cell (outside [6/5, 13/5]); writes
                                   only --out (qualification evidence)
    execute                        qualified worktree + grant commit only; the ONE evaluation of cell 307
    seal-only                      qualified worktree only: seal / materialize persisted evidence; never computes

exit codes: 0 sealed TARGET_EVALUATED; 2 REFUSED before the marker (nothing consumed); 3 CONTROL_FAILED sealed (target
            not consumed); 4 UNSEALED (evidence persisted; run seal-only); 5 sealed with a post-marker failure status;
            6 CONSUMED_UNRECORDED (never rerun); 7 sealed, worktree copy not materialized (run seal-only)

    python3.14 -I -S -B rlr307_driver.py {preflight | rehearse --cell 305 | decoy-stage1 --cell 297 --out F |
                                          execute | seal-only}
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
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import rlr307_guard as GUARD  # noqa: E402
import rlr307_independent as IND  # noqa: E402
import rlr307_pinned as PIN  # noqa: E402
import rlr307_stage1 as S1  # noqa: E402

CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell307_rlr_r1"
QUALIFIED_WORKTREE = "/Users/suzhe/ReBaseGuard-c307"
QUALIFIED_GIT_DIR = "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c307"
QUALIFIED_COMMON_DIR = "/Users/suzhe/ReBaseGuard/.git"
QUALIFIED_BRANCH = "refs/heads/p5y-k5-cell307-rlr-r1"

TARGET_CELL = 307
REHEARSAL_CELLS = (305,)
DECOY_STAGE1_CELLS = (297, 316)
FIELDS = ("A0", "A1", "A2")
ARGS = ("Abar", "tau", "C_T", "D_lo", "D1", "D2")
FROZEN_DIRS = ("code", "protocol", "theory", "tests", "config")

EXEC_DIR_REL = NS_REL + "/evidence/execution"
RESULT_NAME = "RLR307_CELL307_RESULT.json"
RESULT_REL = EXEC_DIR_REL + "/" + RESULT_NAME
GUARDED_PATHS = (EXEC_DIR_REL, RESULT_REL, EXEC_DIR_REL + "/RLR307_CELL307_RESULT.tmp",
                 EXEC_DIR_REL + "/RLR307_CELL307_RESULT.json.tmp", EXEC_DIR_REL + "/RLR307_CELL307_RESULT.partial")
GRANT_REL = NS_REL + "/authorization/RLR307_GRANT.json"
QUAL_DIR_REL = NS_REL + "/qualification/"
QUAL_REL = QUAL_DIR_REL + "RLR307_QUALIFICATION.json"
QREVIEW_REL = NS_REL + "/review/RLR307_QUALIFICATION_REVIEW.md"
CONSUMED_REF = GUARD.CONSUMED_REF
PENDING_REF = "refs/p5y-k5-cell307-rlr-r1/pending-result"
EMERGENCY_NAME = "rlr307-cell307-emergency-result.json"
PRIOR_MARKERS = ("refs/p5y-k5-cell307-rlr-r1/", "refs/rlr-tail/")
R6_NAME = "K5_COVERAGE_MAP_R6"
WORKERS = 5
PRE_CAP_S = 1800                 # everything before the marker (control included)
EVAL_CAP_S = 6 * 3600            # Stage 1 + Stage 2 after the marker (protocol section 5; set from decoy measurements)
DECOY_CAP_S = 6 * 3600
SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}
SCHEMA = "rebaseguard.p5y.k5.cell307-rlr-r1.result.v1"

# helper modules of this campaign, pinned by sha256 (the grant binds this driver's own sha256)
HELPER_SHA256 = {
    "rlr307_guard.py": "ef5542ae84549503205c39e6d6ff62dc5fa59fbb30ea072a056d438109bade25",
    "rlr307_pinned.py": "a5746d9c6d044c40a149fa18e0cd35e1070cc09c996a80d4a5dfbfe0f3350176",
    "rlr307_stage1.py": "6fa9f69168d619a194c1e508e9bb264c01715998dc755e8bd481846758cf685f",
    "rlr307_independent.py": "91a75ea8f4c5a6183efc0eeec4eff3315abaafd92c4a4c8bc5d94c6d44cf94f4",
}

# ------------------------------------------------------------------ bindings (sha256 of the exact bytes, git blob)
PINS = {
    # C2's frozen consumer path (the adoption quantity of floor r2; unchanged since C2's forecast commit 5a94568a)
    "c2_forecast_code": (CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
                         "bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b", "18403dbec855"),
    "tail_forecast_r2": (CP + "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
                         "5ab31ae56c0174697a7f5805e212b46334803e9e3371a77f82871d60716b96cd", "edec817e57f1"),
    "tct_rule": (CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
                 "f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e", "98f6eee4d867"),
    "deflated_consume": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                         "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72", "a0a836fa83c6"),
    "adapter": (CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d", "0516a15b2d83"),
    "cells_json": (CP + "p5y_k1_cover_ledger_successor/config/cells.json",
                   "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f", "30e40fc0e721"),
    "record_manifest": (CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                        "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334", "e6e0e26e2583"),
    "adopted_inputs": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                       "485fb1254e459683f48815c239d18d29119d651d0e77876f772c3fee9d29a37d", "0ba3c6dc876f"),
    "tct_inputs_305": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305.json",
                       "e1390b427e5f7dcf2f997fe039ea3658554cba86f6e472f3c8f339ac0e93df76", "499ccafe5cc9"),
    "tct_inputs_307": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_307.json",
                       "8212a2633d098757bb3ab36dc116b1ceea8bfe42eab3e22876311bd2817d9578", "dafc78755f39"),
    "registry_c1": (CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
                    "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3", "f6d84bdb5ef0"),
    "registry_c2": (CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json",
                    "1b2b834939fcd80a81ddc8f029f46705b53cefeb46c0cc925a99c2b8e856fdd6", "1a3adfd3d893"),
    "c2_forecast": (CP + "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json",
                    "784f25eecd65bad3bf687727590a0c0e91a683c5d30817c3bda80d6f373fe983", "a191557f24c3"),
    "coverage_r5": (CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json",
                    "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c", "f978eeb6b411"),
    "floor_rule": (CP + "p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json",
                   "eb2b4196dd23a8353e25093ff6bfa30d18634dd7f52968ec3c7000ea9b624238", "0ddfac300b92"),
}
LINEAGE = [("5a94568af69f775eaabdeb895dea19b9bf664935", "D stage"), ("ae4cbc2c", "coverage map r5"),
           ("a15d083b009868e38a5bd5a808f38f19e6ab4b92", "floor r2"),
           ("3fadb422eaba97123d46e98b9e80277a62a042c8", "REPLACEMENT_FLOOR_ACCEPTED"),
           ("9c2cbf21", "CELL306_NOT_ADOPTED"), ("c5324a78", "ADJUDICATION_ACCEPTED"),
           ("d3b60795", "FREEZE_READY"), ("7f45e048c39023f4805b21a461650fd332af951f", "morning handover")]


class Refusal(Exception):
    """Fail closed BEFORE the marker: nothing is evaluated, nothing is consumed."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class IndependentCheckFailed(RuntimeError):
    """A composition layer disagrees with its independent reconstruction (after the marker: an execution failure)."""


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


def read_pinned(key: str) -> bytes:
    rel, pin, _ = PINS[key]
    try:
        raw = (REPO / rel).read_bytes()
    except OSError:
        raise Refusal("INPUT_MISSING", rel)
    if sha(raw) != pin:
        raise Refusal("PIN_MISMATCH", rel)
    return raw


def exec_module(raw: bytes, path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


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
    probe = b"rlr307 object-store write probe\n"
    w = git("hash-object", "-w", "--stdin", input_bytes=probe)
    if w.returncode or w.stdout.strip() != git_blob_id(probe):
        raise Refusal("SEAL_PRECONDITION", "the object store is not writable")
    with tempfile.TemporaryDirectory(prefix="rlr307pre") as td:
        idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
        tree = git("write-tree", env_extra=idx) if not git("read-tree", head, env_extra=idx).returncode else None
        if tree is None or tree.returncode:
            raise Refusal("SEAL_PRECONDITION", "a private index cannot be built")
        trial = git("commit-tree", tree.stdout.strip(), "-p", head, "-m", "rlr307 trial commit object (never referenced)")
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
def check_bindings() -> dict:
    shas = {}
    for key, (rel, _, blob) in PINS.items():
        shas[key] = sha(read_pinned(key))
        got = git("rev-parse", f"HEAD:{rel}").stdout.strip()
        if not got.startswith(blob):
            raise Refusal("BLOB_MISMATCH", rel)
        if git("hash-object", "--", rel).stdout.strip() != got:
            raise Refusal("WORKTREE_DIFFERS_FROM_COMMIT", rel)
    for name in PIN.LOAD_ORDER:
        PIN.pinned_bytes(REPO, name, check_git=True)                  # raises PinError
    for commit, word in LINEAGE:
        if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("LINEAGE", commit)
        if word not in git("log", "-1", "--format=%s", commit).stdout:
            raise Refusal("LINEAGE_ROLE", commit)
    shas["helpers"] = check_helpers()
    shas["certifier"] = {n: PIN.PINNED[n][0] for n in PIN.LOAD_ORDER}
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


# ------------------------------------------------------------------ the frozen consumer, from pinned bytes (C12-R2)
def load_consumer() -> dict:
    tct = exec_module(read_pinned("tct_rule"), REPO / PINS["tct_rule"][0], "tct_rule")
    fc = exec_module(read_pinned("tail_forecast_r2"), REPO / PINS["tail_forecast_r2"][0], "rlr307_tail_forecast_r2")
    if fc.T is not tct:
        raise Refusal("MODULE_IDENTITY", "tail_forecast_r2 did not bind the pinned tct_rule")
    c2f = exec_module(read_pinned("c2_forecast_code"), REPO / PINS["c2_forecast_code"][0], "rlr307_c2_d5_forecast")
    dc = exec_module(read_pinned("deflated_consume"), REPO / PINS["deflated_consume"][0], "rlr307_deflated_consume")
    if (dc.K1_BOUND, dc.K2_BOUND) != (c2f.K1_BOUND, c2f.K2_BOUND):
        raise Refusal("KAPPA", "consumer kappa differs from C2's local copy")
    R = tct.load_frozen("tc_rule", tct.FROZEN["tc_rule"][1])
    adapter = fc.module("adapter", "rlr307_fc_adapter")
    if sha((REPO / fc.PINS["adapter"][0]).read_bytes()) != PINS["adapter"][1]:
        raise Refusal("PIN_MISMATCH", "adapter")
    comp = adapter.frozen_components(REPO)
    KM = comp["loader"]
    adapter.bound_file(REPO / adapter.CELLS_JSON, adapter.CELLS_SHA256, "cells.json")
    if adapter.CELLS_SHA256 != PINS["cells_json"][1] or adapter.MANIFEST_SHA256 != PINS["record_manifest"][1]:
        raise Refusal("PIN_MISMATCH", "adapter bindings differ from the campaign's")
    cover = KM.load_cells(REPO / adapter.CELLS_JSON, adapter.DETECTOR)
    if [c["index"] for c in cover] != list(range(310)):
        raise Refusal("COVER_UNIVERSE")
    return {"T": tct, "FC": fc, "C2F": c2f, "DC": dc, "R": R, "KM": KM, "adapter": adapter,
            "cover": {c["index"]: c for c in cover}}


def cell_inputs(con: dict, k: int) -> dict:
    if k not in REHEARSAL_CELLS + (TARGET_CELL,):
        raise Refusal("CELL_OUT_OF_SCOPE", str(k))
    T, FC, R = con["T"], con["FC"], con["R"]
    meas = json.loads(read_pinned(f"tct_inputs_{k}"))
    adopted = json.loads(read_pinned("adopted_inputs"))
    manifest = json.loads(read_pinned("record_manifest"))
    a = adopted["cells"][str(k)]
    want = manifest["files"].get(f"k4_records/aux5_CUSUM_{k}_256.json")
    if meas["cell"] != k or not meas["identity_gate"]["identical"] or meas["order3_fields_present"]:
        raise Refusal("MEASUREMENT", f"cell {k} is not a gated order-3-free replay")
    if not (want and meas["k1_record_sha256"] == a["record_sha256"] == want):
        raise Refusal("RECORD_BINDING", f"cell {k}: measurement, adopted inputs and manifest disagree")
    if adopted["manifest_sha256"] != PINS["record_manifest"][1]:
        raise Refusal("RECORD_BINDING", "adopted inputs not bound to the adopted export manifest")
    meas["C_upper"] = str(FC.rat(a["C_upper"]))
    rec_view = {"eps_cell_refined": a["eps_cell_refined"], "m": a["m"]}
    if not T.derived_identity_gate(R, meas, rec_view)["pass"]:
        raise Refusal("IDENTITY_GATE", f"cell {k}")
    kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    G = T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])
    if {j: G[j] for j in FIELDS} != IND.lemma_g(F(meas["C_upper"]), kn[1], kn[2]):
        raise Refusal("LEMMA_G_CROSSCHECK", f"cell {k}")
    return {"meas": meas, "aux": a["auxiliary_evidence"], "ad": a["m"]["5"], "cov": con["cover"][k], "G": G,
            "k1": kn[1], "k2": kn[2]}


def i1_sets(k: int) -> list:
    out = []
    for name, key in (("C1", "registry_c1"), ("C2", "registry_c2")):
        blocks = [b for b in json.loads(read_pinned(key))["blocks"] if b["cell"] == k]
        if len(blocks) != 1 or blocks[0].get("certified") is not True:
            raise Refusal("I1_BLOCK", f"{name} cell {k}")
        out.append({"name": name, "values": {x: F(blocks[0][x]) for x in ARGS}})
    return out


def s_i1(con: dict, k: int, ci: dict) -> tuple:
    """C2's adopted supply for cell k: componentwise min of {G, Dv'(C1), Dv'(C2)} (frozen consumer's combine), with
    Lemma Dv' r2 computed by the frozen consumer AND by C2's independent path AND by rlr307_independent."""
    sup = {"G": ci["G"]}
    for s in i1_sets(k):
        v = s["values"]
        if not (v["D_lo"] > 0 and v["tau"] >= 1 and v["C_T"] >= v["tau"] and v["Abar"] >= 1):
            raise Refusal("VALIDATION", s["name"])
        args = tuple(v[x] for x in ARGS)
        frozen = con["DC"].atom_constants_r2(*args)
        ind = IND.dv_prime_r2(*args, con["C2F"].K1_BOUND, con["C2F"].K2_BOUND)
        if {j: frozen[j] for j in FIELDS} != con["C2F"]._atom_independent(*args) or \
                {j: frozen[j] for j in FIELDS} != ind:
            raise Refusal("ATOM_CROSSCHECK", s["name"])
        sup[s["name"]] = frozen
    A, prov = con["C2F"].combine(sup)
    if {j: A[j] for j in FIELDS} != IND.componentwise_min(sup):
        raise Refusal("COMBINE_CROSSCHECK", str(k))
    return A, prov, sup


def evaluate(con: dict, ci: dict, A: dict) -> dict:
    res = con["C2F"].direct(con["T"], con["R"], ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    return {"Gamma_exact": str(res["Gamma"]), "pass": bool(res["pass"]), "H_exact": [str(res["lo"]), str(res["hi"])],
            "M_after_exact": str(res["M"]), "A_exact": {j: str(A[j]) for j in FIELDS}}


def control(con: dict, k: int) -> dict:
    """C2's committed record for cell k reproduced exactly under S_I1 (every field compared for equality)."""
    ci = cell_inputs(con, k)
    A, prov, sup = s_i1(con, k, ci)
    got = evaluate(con, ci, A)
    fc = json.loads(read_pinned("c2_forecast"))
    want, wsup = fc["cells"][str(k)], fc["supplies"][str(k)]
    fields = {"Gamma_exact": got["Gamma_exact"] == want["Gamma_exact"], "A_exact": got["A_exact"] == want["A_exact"],
              "provenance": prov == want["provenance"], "H_exact": got["H_exact"] == want["H_exact"],
              "M_after_exact": got["M_after_exact"] == want["M_after_exact"], "pass": got["pass"] == want["pass"],
              "per_supply_records_G_C1_C2": sorted(wsup) == sorted(sup) and all(
                  float(sup[n][j]) == wsup[n][j] for n in sup for j in FIELDS)}
    return {"cell": k, "supply": "S_I1 = min{G, Dv'(C1), Dv'(C2)} (C2's adopted supply)",
            "reproduces_C2_exactly": all(fields.values()), "field_matches": fields, "provenance": prov,
            "evaluated": got, "_ci": ci, "_A": A}


def cover_interval(con: dict, k: int) -> tuple:
    cov = con["cover"][k]
    lo, hi = con["KM"].rat(cov["left"]), con["KM"].rat(cov["right"])
    return F(lo), F(hi)


def target_blocks(con: dict) -> list:
    """P1/P2 for cell 307, cross-checked against C2's registry (same interval, same sub-block count)."""
    lo, hi = cover_interval(con, TARGET_CELL)
    reg = [b for b in json.loads(read_pinned("registry_c2"))["blocks"] if b["cell"] == TARGET_CELL]
    if len(reg) != 1 or (F(reg[0]["e_lo"]), F(reg[0]["e_hi"])) != (lo, hi):
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from REGISTRY_C2's")
    if (lo, hi) != GUARD.CELL307:
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from the guard's")
    blocks = S1.blocks_for(lo, hi)
    if len(blocks) != reg[0]["sub_blocks"]:
        raise Refusal("BLOCK_GEOMETRY", "sub-block count differs from REGISTRY_C2's")
    if blocks[0]["sub_lo"] != lo or blocks[-1]["sub_hi"] != hi or any(
            blocks[i]["sub_hi"] != blocks[i + 1]["sub_lo"] for i in range(len(blocks) - 1)):
        raise Refusal("BLOCK_GEOMETRY", "the sub-blocks do not tile the cell")
    return blocks


# ------------------------------------------------------------------ Stage 1: worker pool (spawned processes)
_W: dict = {}


def _worker_init(mode: str, repo: str, grant_commit: str, hull_blocks: list, driver_sha: str) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    if sha(HERE.read_bytes()) != driver_sha:
        raise RuntimeError("worker: driver bytes differ from the parent's")
    check_helpers()
    mods = PIN.load_certifier(Path(repo), GUARD, check_git=True)
    if mode == "target":
        GUARD.arm_target(repo, grant_commit, [(F(a), F(b)) for a, b in hull_blocks])
    elif mode != "decoy":
        raise RuntimeError(f"worker: unknown mode {mode}")
    _W.clear()
    _W.update({"mods": mods, "mode": mode})


def _worker_job(block: int, hull_lo: str, hull_hi: str, d: int) -> dict:
    t0 = time.time()
    try:
        rec = S1.certify_rung(_W["mods"], F(hull_lo), F(hull_hi), d)
    except (MemoryError, OSError):
        raise                                                        # infrastructure: an execution failure
    except Exception as exc:                                         # the frozen certifier raised: rung not certified
        return {"block": block, "degree": d, "kind": "RUNG_EXCEPTION", "error": f"{type(exc).__name__}: {exc}"[:400],
                "wall_seconds": round(time.time() - t0, 1)}
    return {"block": block, "degree": d, "kind": "RUNG_RETURNED", "status": rec.get("status"), "record": rec,
            "wall_seconds": round(time.time() - t0, 1)}


def stage1(mode: str, blocks: list, grant_commit: str, own_sha: str, cp, kappa: tuple, workers: int = WORKERS) -> dict:
    """P3-P5 with the independent reconstruction of every composition layer. Raises on any infrastructure failure."""
    hull = [(fs(b["hull_lo"]), fs(b["hull_hi"])) for b in blocks]
    jobs = sorted(((i, lo, hi, d) for i, (lo, hi) in enumerate(hull) for d in S1.LADDER), key=lambda j: (-j[3], j[0]))
    results = {}
    ex = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=_worker_init, initargs=(mode, str(REPO), grant_commit, hull, own_sha))
    try:
        futs = {ex.submit(_worker_job, *j): (j[0], j[3]) for j in jobs}
        for fut in as_completed(futs):
            results[futs[fut]] = fut.result()                        # a worker failure propagates
    finally:
        procs = list(getattr(ex, "_processes", {}).values())
        ex.shutdown(wait=False, cancel_futures=True)
        for p in procs:
            if p.is_alive():
                p.terminate()
    block_recs, ind_blocks, rung_checks = [], [], []
    for i in range(len(blocks)):
        rungs = [results[(i, d)] for d in S1.LADDER]
        cert = [r["record"] for r in rungs if r["kind"] == "RUNG_RETURNED" and r["status"] == "CERTIFIED"]
        for r in cert:                                               # each rung's own assembly vs the independent one
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
            same = all(F(brec[k]) == lad[k] for k in IND.UPPER_KEYS + IND.LOWER_KEYS) and \
                all(F(brec[k]) == isup[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))
            if not same:
                raise IndependentCheckFailed(f"block {i}: ladder or block supply disagrees")
            ind_blocks.append(isup)
        block_recs.append({"index": i, "sub_lo": fs(blocks[i]["sub_lo"]), "sub_hi": fs(blocks[i]["sub_hi"]),
                           "hull_lo": hull[i][0], "hull_hi": hull[i][1], "block": brec,
                           "rungs": [{k: v for k, v in r.items()} for r in rungs]})
    if not all(rung_checks):
        raise IndependentCheckFailed("a rung's assembly disagrees with the independent D14 recomputation")
    cell = S1.cell_compose([b["block"] for b in block_recs])
    icell = IND.cell(ind_blocks)
    if cell["status"] != icell["status"] or (cell["status"] == "CERTIFIED" and not all(
            F(cell[k + "_max"]) == icell[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))):
        raise IndependentCheckFailed("cell composition disagrees")
    return {"mode": mode, "ladder": list(S1.LADDER), "hull_bits": S1.HULL_BITS, "workers": workers,
            "blocks": block_recs, "cell": cell, "independent_checks": {"rungs": len(rung_checks), "all_equal": True}}


# ------------------------------------------------------------------ Stage 2 and the decision
def s_rlr(A_i1: dict, cell: dict) -> dict:
    return {"A0": A_i1["A0"], "A1": min(A_i1["A1"], F(cell["A1_SUPPLY_max"])),
            "A2": min(A_i1["A2"], F(cell["A2_SUPPLY_max"]))}


def decide(st1: dict, st2: dict | None) -> dict:
    """The frozen mechanical outcome (protocol section 8); the adjudication applies the same table."""
    if st1["cell"]["status"] != "CERTIFIED":
        return {"mechanical_outcome": "CELL307_NOT_CLOSED_UNDER_RLR", "reason": "RLR_CERTIFICATION_FAILED",
                "Gamma_S_RLR_evaluated": False}
    if st2["evaluated"]["pass"]:
        return {"mechanical_outcome": "CELL307_CLOSED_UNDER_RLR", "reason": "Gamma(5,307;S_RLR) < 0 (exact)",
                "Gamma_S_RLR_evaluated": True}
    return {"mechanical_outcome": "CELL307_NOT_CLOSED_UNDER_RLR", "reason": "Gamma(5,307;S_RLR) >= 0 (exact)",
            "Gamma_S_RLR_evaluated": True}


def evaluate_target(con: dict, prep: dict) -> dict:
    """The ONE scientific evaluation (after the marker)."""
    st1 = stage1("target", prep["blocks"], prep["grant_commit"], prep["own_sha"], prep["cp"], prep["kappa"])
    st2 = None
    if st1["cell"]["status"] == "CERTIFIED":
        A = s_rlr(prep["A_I1"], st1["cell"])
        if A != IND.consumed(prep["A_I1"], {"A1_SUPPLY": st1["cell"]["A1_SUPPLY_max"],
                                            "A2_SUPPLY": st1["cell"]["A2_SUPPLY_max"]}):
            raise IndependentCheckFailed("S_RLR disagrees with its independent reconstruction")
        st2 = {"supply": "S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell))",
               "provenance": {j: ("I1" if A[j] == prep["A_I1"][j] else "RLR") for j in FIELDS},
               "evaluated": evaluate(con, prep["ci"], A)}
    return {"cell": TARGET_CELL, "stage1": st1, "stage2": st2, "decision": decide(st1, st2)}


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
    if g.get("schema") != "rebaseguard.p5y.k5.cell307-rlr-r1.grant.v1" or g.get("exactly_once") is not True \
            or g.get("cell") != TARGET_CELL or g.get("route") != "RLR" or g.get("closure_only") is not True:
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
    manifest = g.get("input_manifest_sha256")
    if manifest != sha((REPO / NS_REL / "protocol/RLR307_FREEZE.json").read_bytes()):
        raise Refusal("GRANT_INVALID", "the grant does not bind the frozen input manifest")
    return {"grant_commit": head, "grant_sha256": sha((REPO / GRANT_REL).read_bytes()), "freeze_commit": fz,
            "qualification_commit": qual_c, "qualification_review_commit": review_c}


# ------------------------------------------------------------------ persistence, seal and materialization (C12-R2 R3)
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
        with tempfile.TemporaryDirectory(prefix="rlr307seal") as td:
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
    return (f"p5y: K5 cell-307 RLR r1 — SEAL of the one cell-307 RLR evaluation ({status})\n\n"
            f"Committed by {NS_REL}/code/rlr307_driver.py from the in-memory bytes (object store + pending ref), "
            "not from a worktree file; the result was not inspected before this commit.\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")


def fallback_bytes(common_min: dict, stage: str, exc: BaseException) -> bytes:
    rec = {"schema": SCHEMA, "status": "POST_MARKER_RECORDING_FAILED", "stage": stage,
           "error": f"{type(exc).__name__}: {exc}"[:500], "target_evaluations": 1, **common_min}
    try:
        return serialize(rec)
    except BaseException:
        return (json.dumps({"status": "POST_MARKER_RECORDING_FAILED", "stage": stage}) + "\n").encode()


def _eval_cap(*_):
    raise TimeoutError(f"evaluation exceeded {EVAL_CAP_S} s")


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
            kind = "INDEPENDENT_CHECK_FAILED" if isinstance(exc, IndependentCheckFailed) else "TARGET_EVALUATION_FAILED"
            tgt, status = {"error": f"{type(exc).__name__}: {exc}"[:800], "failure_kind": kind}, kind
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        common.update({"status": status, "target_evaluated": status == "TARGET_EVALUATED", "target_evaluations": 1,
                       "consumed_ref": CONSUMED_REF, "target": tgt,
                       "mechanical_outcome": (tgt.get("decision", {}).get("mechanical_outcome")
                                              if status == "TARGET_EVALUATED" else "CELL307_EXECUTION_INDETERMINATE"),
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
            print("RLR307 CONSUMED_UNRECORDED: the marker exists and no evidence channel worked. NEVER run execute again.")
            return 6
    if blob is None:
        print("RLR307 UNSEALED: evidence persisted in the git dir; run `seal-only`. NEVER run execute again.")
        return 4
    try:
        cid = sealer(blob, seal_message(status))
    except BaseException:
        print(f"RLR307 UNSEALED: evidence persisted ({channel}); run `seal-only`. NEVER run execute again.")
        return 4
    try:
        materializer(blob)
    except BaseException:
        print(f"RLR307 SEALED {cid} (status {status}); worktree copy NOT materialized: run `seal-only`.")
        return 7
    print(f"RLR307 SEALED {cid} (status {status}; one target evaluation; result not printed)")
    return 0 if status == "TARGET_EVALUATED" else 5


def keep_awake() -> dict:
    """Environmental only (results never depend on it): ask macOS not to idle-sleep while this process lives."""
    try:
        p = subprocess.Popen(["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"caffeinate_pid": p.pid}
    except OSError as exc:
        return {"caffeinate": f"unavailable ({type(exc).__name__})"}


def prepare_target(con: dict, ctl: dict, own_sha: str, grant: dict, mods: dict) -> dict:
    blocks = target_blocks(con)
    cp = mods["c1b_certpw"]
    kappa = (cp.KAPPA1, cp.KAPPA2)
    kc = IND.kappa_check(*kappa)
    if not (kc["kappa1_ge_sqrt_2_over_pi"] and kc["kappa2_ge_4phi1"]):
        raise Refusal("KAPPA", "a certifier kappa is not a valid upper bound")
    return {"blocks": blocks, "grant_commit": grant["grant_commit"], "own_sha": own_sha, "cp": cp, "kappa": kappa,
            "kappa_check": kc, "A_I1": ctl["_A"], "ci": ctl["_ci"]}


def public_control(ctl: dict) -> dict:
    return {k: v for k, v in ctl.items() if not k.startswith("_")}


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
    awake = keep_awake()
    con = load_consumer()
    mods = PIN.load_certifier(REPO, GUARD, check_git=True)
    ctl = control(con, TARGET_CELL)
    common = {"schema": SCHEMA, "cell": TARGET_CELL, "m": 5, "route": "RLR", "scope": "CLOSURE_ONLY",
              "identity": ident, "grant": grant, "input_sha256": shas, "governance_state_before": state,
              "seal_preconditions": pre, "driver_sha256": own_sha, "started_utc": started,
              "control": public_control(ctl), "python": sys.version.split()[0], "environment": awake}
    if not ctl["reproduces_C2_exactly"]:
        common.update({"status": "CONTROL_FAILED", "target_evaluated": False, "target_evaluations": 0,
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3)})
        data = serialize(common)
        try:
            blob = (persist or persist_pending)(data)
            cid = (sealer or seal_blob)(blob, seal_message("CONTROL_FAILED"))
            (materializer or materialize)(blob)
        except BaseException:
            print("RLR307 CONTROL_FAILED: not fully sealed; run `seal-only`. The target was not evaluated.")
            return 4
        print(f"RLR307 CONTROL_FAILED sealed {cid}; the target was not evaluated")
        return 3
    prep = (prepare or prepare_target)(con, ctl, own_sha, grant, mods)
    common.update({"kappa_check": prep.get("kappa_check"),
                   "blocks_planned": [{k: fs(v) if isinstance(v, F) else v for k, v in b.items()}
                                      for b in prep.get("blocks", [])]})
    check_result_paths()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    signal.alarm(0)
    if git("update-ref", CONSUMED_REF, grant["grant_commit"], "0" * 40).returncode != 0:
        raise Refusal("CONSUMED", "the exactly-once marker could not be created: the target is never evaluated twice")
    return after_marker(con, prep, common, evaluator, t0, persist, sealer, materializer)


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
            print(f"RLR307 SEALED {cid} (status {status}); materialization refused: {type(exc).__name__}")
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
            print(f"RLR307 SEALED {cid} (status {status}); the worktree object at the result path is NOT the sealed bytes")
            return 7
    print(f"RLR307 SEALED {cid} (seal-only; status {status}; nothing computed)")
    return 0


# ------------------------------------------------------------------ rehearsal and decoy Stage 1 (qualification only)
def rehearse(con: dict, k: int) -> dict:
    """Cell 305 only: the control, and the Stage-2 path with a NEUTRAL cell record (every A_cell above S_I1, so
    S_RLR == S_I1 and the committed record must be reproduced again). No new supply value enters any Gamma."""
    if k not in REHEARSAL_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", str(k))
    ctl = control(con, k)
    A = ctl["_A"]
    neutral = {"A1_SUPPLY_max": fs(A["A1"] * 2 + 1), "A2_SUPPLY_max": fs(A["A2"] * 2 + 1)}
    A2 = s_rlr(A, neutral)
    again = evaluate(con, ctl["_ci"], A2)
    return {"control": public_control(ctl), "neutral_substitution": {
        "S_RLR_equals_S_I1": A2 == {j: A[j] for j in FIELDS},
        "reproduces_committed_again": again == ctl["evaluated"]}}


def decoy_stage1(k: int, own_sha: str, workers: int) -> dict:
    if k not in DECOY_STAGE1_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", f"{k} is not a declared decoy")
    cells = [c for c in json.loads(read_pinned("cells_json")) if c["detector"] == "CUSUM" and c["index"] == k]
    if len(cells) != 1 or cells[0]["left"][1] != "0/1" or cells[0]["right"][1] != "0/1":
        raise Refusal("DECOY_GEOMETRY", str(k))
    lo, hi = F(cells[0]["left"][0]), F(cells[0]["right"][0])
    GUARD.guard_drift(lo, hi)                                          # decoy mode: refuses the band
    blocks = S1.blocks_for(lo, hi)
    for b in blocks:
        GUARD.guard_drift(b["hull_lo"], b["hull_hi"])
    mods = PIN.load_certifier(REPO, GUARD, check_git=True)
    cp = mods["c1b_certpw"]
    return stage1("decoy", blocks, "", own_sha, cp, (cp.KAPPA1, cp.KAPPA2), workers)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("preflight", "rehearse", "decoy-stage1", "execute", "seal-only"))
    ap.add_argument("--cell", type=int)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    own_sha = sha(HERE.read_bytes())

    def wall_cap(*_):
        raise Refusal("WALL_CAP", f"{PRE_CAP_S} s")

    signal.signal(signal.SIGALRM, wall_cap)
    signal.alarm(DECOY_CAP_S if a.mode == "decoy-stage1" else PRE_CAP_S)
    try:
        if a.mode in ("preflight", "execute", "seal-only") and a.cell is not None:
            raise Refusal("CELL_OUT_OF_SCOPE", "only rehearse / decoy-stage1 take --cell; execute is cell 307 only")
        if a.mode == "preflight":
            check_not_evaluated()
            out = {"mode": "preflight", "input_sha256": check_bindings(), "governance_state": check_governance_state(),
                   "driver_sha256": own_sha}
            load_consumer()
            out["certifier_identity"] = PIN.load_certifier(REPO, GUARD, check_git=True)["_identity"]
            print("RLR307 PREFLIGHT PASS")
        elif a.mode == "rehearse":
            check_not_evaluated()
            check_bindings()
            check_governance_state()
            t0 = time.time()
            out = {"mode": "rehearse", **rehearse(load_consumer(), a.cell), "wall_seconds": round(time.time() - t0, 3),
                   "driver_sha256": own_sha, "utc": utc()}
            ok = out["control"]["reproduces_C2_exactly"] and all(out["neutral_substitution"].values())
            print(f"RLR307 REHEARSE cell {a.cell}: control and neutral substitution reproduce C2 exactly = {ok}")
            if not ok:
                if a.out:
                    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
                return 3
        elif a.mode == "decoy-stage1":
            check_bindings()
            t0 = time.time()
            st = decoy_stage1(a.cell, own_sha, a.workers)
            cu = resource.getrusage(resource.RUSAGE_CHILDREN)
            out = {"mode": "decoy-stage1", "decoy_cell": a.cell, "stage1": st, "driver_sha256": own_sha, "utc": utc(),
                   "wall_seconds": round(time.time() - t0, 1),
                   "cpu_seconds_workers": round(cu.ru_utime + cu.ru_stime, 1),
                   "latent_proxy": "decoy values; never juxtapose with any tail-cell number"}
            print(f"RLR307 DECOY-STAGE1 cell {a.cell}: {st['cell']['status']} in {out['wall_seconds']} s")
        elif a.mode == "execute":
            return run_execute(own_sha)
        else:
            return run_seal_only()
        if a.out:
            Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
        return 0
    except (Refusal, PIN.PinError, GUARD.QuarantineRefusal) as e:
        print(f"RLR307 REFUSED {e}")
        return 4 if getattr(e, "code", None) == "UNSEALED" else 2
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    sys.exit(main())
