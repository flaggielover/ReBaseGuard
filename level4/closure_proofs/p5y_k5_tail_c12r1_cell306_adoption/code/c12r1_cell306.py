"""C12-R1 -- K5 tail cell-306 adoption campaign under floor r2: the cell-306-only driver (successor of C12).

C12 (freeze b9ffc87f) was QUALIFICATION_REJECTED (2cdfa467), blocker B1: its verifier's sandbox could pass every
guard at later governance states. This successor repairs B1 in the DRIVER itself, so that no copy or sandbox can
evaluate the target, whatever builds it:
  * identity first: `execute`/`seal-only` refuse unless the process runs in the qualified worktree, with the qualified
    git dir and common dir, on the qualified branch (QUALIFIED_*), before anything else is read;
  * no prior evaluation anywhere: this campaign's and C12's markers and result paths (ref, tree, history, disk);
  * every seal precondition (clean tree and index, no git locks, committer identity, a private index can be built,
    the result directory is writable) is checked BEFORE the exactly-once marker is created;
  * after the marker exists, EVERY failure (BaseException, wall cap, crosscheck SystemExit) is recorded and sealed;
    `seal-only` completes a failed seal and never computes.
Review notes carried in: N1 (git-blob binding of every pin), N2 (the control also compares C2's per-supply records,
so the Lemma-G input is checked), N3 (above), N4 (seal-only verifies the result's self-hash and status and names the
real status), N5 (the grant's freeze/qualification/review commits are derived and checked, not trusted), N8
(independence_violations must be empty in both comparisons).

It reuses C2's frozen consumer verbatim, every module executed from pinned bytes:
    c2_d5_forecast.py      direct (the frozen K5-B direct clause), combine (the D4 rule), _atom_independent
    deflated_consume.py    atom_constants_r2 (Lemma Dv' r2)
    tct_rule.py            atom_constants_generic (Lemma G), tail_enclosure (+ crosscheck), derived_identity_gate,
                           load_frozen('tc_rule')
    tail_forecast_r2.py    the pinned module loader for the E6 adapter (frozen loader and cells.json)
C2 read C_upper, auxiliary_evidence and the m = 5 intervals from the off-host K1 record; this driver reads the same
fields from the committed ADOPTED_TAIL_INPUTS.json, bound to that record's sha256 (the adopted export manifest entry).

Supplies (floor r2, never mixed):
    S_I1 = min_componentwise{G, Dv'(REGISTRY_C1 block 306), Dv'(REGISTRY_C2 block 306)}   = C2's adopted supply
    S_I2 = min_componentwise{G, Dv'(C11R C_T, tau, Abar, D_lo + C11RD D1, D2)}

modes
    preflight                  read-only anywhere: bindings, governance state, no target artifact, no marker
    rehearse --cell 305|306    read-only anywhere: the I1 control on S_I1 must reproduce C2's committed record
                               exactly (including C2's per-supply records). Never reads an I2 constant.
    execute                    qualified worktree + grant commit only: control -> I2 checks -> marker -> ONE
                               evaluation of Gamma(5, 306; S_I2) -> write and seal. Prints status only.
    seal-only                  qualified worktree only: seal an already written result after an UNSEALED exit

exit codes: 0 ok; 2 REFUSED (fail closed, nothing evaluated); 3 CONTROL_FAILED (sealed, target never evaluated);
            4 UNSEALED (result written, seal incomplete: run seal-only; never execute again);
            5 TARGET_EVALUATION_FAILED (consumed and sealed; never rerun)

    python3.14 -I -S -B c12r1_cell306.py {preflight | rehearse --cell N | execute | seal-only}
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import tempfile
import time
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_tail_c12r1_cell306_adoption"

# the one place this campaign may consume its target (B1 repair)
QUALIFIED_WORKTREE = "/Users/suzhe/ReBaseGuard-k5c11rd"
QUALIFIED_GIT_DIR = "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd"
QUALIFIED_COMMON_DIR = "/Users/suzhe/ReBaseGuard/.git"
QUALIFIED_BRANCH = "refs/heads/p5y-k5-tail-c11rd-d1d2-extension"

TARGET_CELL = 306
REHEARSAL_CELLS = (305, 306)
FIELDS = ("A0", "A1", "A2")
ARGS = ("Abar", "tau", "C_T", "D_lo", "D1", "D2")

RESULT_REL = NS_REL + "/evidence/execution/C12R1_CELL306_RESULT.json"
GRANT_REL = NS_REL + "/authorization/C12R1_GRANT.json"
QUAL_REL = NS_REL + "/evidence/qualification/C12R1_QUALIFICATION.json"
QREVIEW_REL = NS_REL + "/review/C12R1_QUALIFICATION_REVIEW.md"
CONSUMED_REF = "refs/c12r1/cell306-target-consumed"
# evidence that the cell-306 I2 target was ever evaluated or attempted, by this campaign or its predecessor
PRIOR_MARKERS = ("refs/c12r1/", "refs/c12/")
PRIOR_RESULTS = (RESULT_REL, CP + "p5y_k5_tail_c12_cell306_adoption/evidence/execution/C12_CELL306_RESULT.json")
R6_NAME = "K5_COVERAGE_MAP_R6"
WALL_CAP_S = 900
SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}

# ------------------------------------------------------------------ bindings (sha256 of the exact bytes)
PINS = {
    # floor r2 and the N9 chain (G00, G01)
    "floor_rule": (CP + "p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json",
                  "eb2b4196dd23a8353e25093ff6bfa30d18634dd7f52968ec3c7000ea9b624238"),
    "floor_gate": (CP + "p5y_k5_tail_floor_r2/config/CELL306_ADOPTION_GATE_R2.json",
                  "747c65a8de75c9420410ec6941d3eb4a2da23e29cca24cd743c60acd436dca14"),
    "floor_review": (CP + "p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md",
                    "2b94c8e0af795e758e7334bcf7d9e76861ff503b1ed67cfbaad273e00a188c77"),
    "n9_adjudication": (CP + "p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md",
                       "4a61b0a345b539cb80a0912e2ab1f1c396f42405d5a6510496456e537a103ffc"),
    "n9_adjudication_review": (CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md",
                              "5fa25a80aad3b2d3610da5eccf946d0bc399558e01ac329b9b07edea1e701702"),
    # C2's frozen consumer path (G04, G09) -- unchanged since C2's forecast commit 5a94568a
    "c2_forecast_code": (CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
                        "bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b"),
    "tail_forecast_r2": (CP + "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
                        "5ab31ae56c0174697a7f5805e212b46334803e9e3371a77f82871d60716b96cd"),
    "tct_rule": (CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
                "f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e"),
    "deflated_consume": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                        "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"),
    "adapter": (CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
               "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"),
    "cells_json": (CP + "p5y_k1_cover_ledger_successor/config/cells.json",
                  "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"),
    "record_manifest": (CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                       "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"),
    # non-supply consumer inputs
    "adopted_inputs": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                      "485fb1254e459683f48815c239d18d29119d651d0e77876f772c3fee9d29a37d"),
    "tct_inputs_305": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305.json",
                      "e1390b427e5f7dcf2f997fe039ea3658554cba86f6e472f3c8f339ac0e93df76"),
    "tct_inputs_306": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_306.json",
                      "57ff9280ca4d3b597ce4cdd6741d3a473e9f5d63e7c414696ce42c422b709a49"),
    # I1 (G04)
    "registry_c1": (CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
                   "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3"),
    "registry_c2": (CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json",
                   "1b2b834939fcd80a81ddc8f029f46705b53cefeb46c0cc925a99c2b8e856fdd6"),
    # the control (G10)
    "c2_forecast": (CP + "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json",
                   "784f25eecd65bad3bf687727590a0c0e91a683c5d30817c3bda80d6f373fe983"),
    # I2 (G05, G06)
    "c11r_comparison": (CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json",
                       "800447adb9bc5f1b6116b61dc584d1653d8ec3c3e181ae35112a9efd1568231b"),
    "c11r_statements": (CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/table/C11R_N9_STATEMENTS.json",
                       "2e0f7dc4ceb796289d083ba09129116f128f54dc172ad31d45129a255c0487b7"),
    "c11r_execution_review": (CP + "p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_EXECUTION.md",
                             "ae2fbf7020751772feec798e73abde5bbf695a505315337ea8aef79ce90078a7"),
    "c11r_comparison_review": (CP + "p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_COMPARISON.md",
                              "09f1d42f0e85e10cc0907f4614d981d4852e160fc8cb2b9cb2649ad1fb1804ce"),
    "c11rd_comparison": (CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json",
                        "8a9637b6a11d6b7e48bc4beee6a7a8b37fce4425ba911f4b10d53b4020391b06"),
    "c11rd_runs": (CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/C11RD_RUNS.json",
                  "c28a8cea9e777c06dd082765fc8cc94f3f5e5376809c2c74fedc358658709cc0"),
    "c11rd_execution_review": (CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_EXECUTION_REVIEW.md",
                              "5d3181cb9fc83ec1e7f5ff473800d44251100100d43cd71b210a36439f1ff211"),
    "c11rd_comparison_review": (CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_COMPARISON_REVIEW.md",
                               "1c8832b4963f3da70883744cdfe0f5a91586f755ca0e26049cb4643dfc3199ff"),
    # governance state (G02)
    "coverage_r5": (CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json",
                   "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c"),
}
# git blob ids (12-hex prefixes) of the same files at the bound commits: a second, independent binding (N1)
BLOBS = {
    "floor_rule": "0ddfac300b92", "floor_gate": "89b86218116a", "floor_review": "ad73021bca35",
    "n9_adjudication": "c3e001a7c84a", "n9_adjudication_review": "3c716c70de5b", "c2_forecast_code": "18403dbec855",
    "tail_forecast_r2": "edec817e57f1", "tct_rule": "98f6eee4d867", "deflated_consume": "a0a836fa83c6",
    "adapter": "0516a15b2d83", "cells_json": "30e40fc0e721", "record_manifest": "e6e0e26e2583",
    "adopted_inputs": "0ba3c6dc876f", "tct_inputs_305": "499ccafe5cc9", "tct_inputs_306": "ad0f8039b4a1",
    "registry_c1": "f6d84bdb5ef0", "registry_c2": "1a3adfd3d893", "c2_forecast": "a191557f24c3",
    "c11r_comparison": "5269c2aaa354", "c11r_statements": "58b4066f5cce", "c11r_execution_review": "bfc1ab77c01f",
    "c11r_comparison_review": "a1d33960e262", "c11rd_comparison": "7151f57a9792", "c11rd_runs": "30e2dfd0ac87",
    "c11rd_execution_review": "7037189f61ad", "c11rd_comparison_review": "7c7cad001a72",
    "coverage_r5": "f978eeb6b411",
}
# commits every one of which must be an ancestor of HEAD, with a word its subject must contain
LINEAGE = [
    ("5a94568af69f775eaabdeb895dea19b9bf664935", "D stage"),                  # C2 forecast (the control artifact)
    ("ae4cbc2c", "coverage map r5"),                                          # r5
    ("22537709", "EXECUTION_ACCEPTED"), ("2c24a989", "comparison"), ("7375b9cd", "COMPARISON_ACCEPTED"),
    ("4547bcd4", "SEAL"), ("db1c6118", "EXECUTION_ACCEPTED"), ("8e2defab", "comparator"),
    ("90265349", "COMPARISON_ACCEPTED"),
    ("7d67989d3da6595180ca3c01d34f2bdf4543ae73", "adjudication"),
    ("fb237288a7cf481c14cd2f85c18bb363d2ebe44a", "ADJUDICATION_ACCEPTED"),
    ("a15d083b009868e38a5bd5a808f38f19e6ab4b92", "floor r2"),
    ("3fadb422eaba97123d46e98b9e80277a62a042c8", "REPLACEMENT_FLOOR_ACCEPTED"),
    ("2cdfa467", "QUALIFICATION_REJECTED"),                                   # the predecessor's rejection (B1)
]
VERDICTS = [
    ("floor_review", "line2", "REPLACEMENT_FLOOR_ACCEPTED"),
    ("n9_adjudication", "line2", "N9_CLOSED"),
    ("n9_adjudication_review", "line2", "ADJUDICATION_ACCEPTED"),
    ("c11rd_execution_review", "line2", "EXECUTION_ACCEPTED"),
    ("c11rd_comparison_review", "line2", "COMPARISON_ACCEPTED"),
    ("c11r_execution_review", "verdict_line", "VERDICT: EXECUTION_ACCEPTED"),
    ("c11r_comparison_review", "verdict_line", "VERDICT: COMPARISON_ACCEPTED"),
]
I2_FROM_C11R = {"C_T": "UPPER_BOUND", "tau": "UPPER_BOUND", "Abar": "UPPER_BOUND", "D_lo": "LOWER_BOUND"}
I2_FROM_C11RD = {"D1": "UPPER_BOUND", "D2": "UPPER_BOUND"}
ACCEPTED_CLASSES = ("AGREES", "STRONGER")
ACCEPTED_STATEMENTS = ("EQUIVALENT", "STRONGER")
ACCEPTED_DOMAINS = ("EQUAL", "SUPERSET")


class Refusal(Exception):
    """Fail closed: nothing is evaluated, nothing is decided."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


# ------------------------------------------------------------------ plumbing
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args, env_extra=None):
    env = dict(ENV)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args],
                          capture_output=True, text=True, env=env)


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def read_pinned(key: str) -> bytes:
    rel, pin = PINS[key]
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


def verdict_ok(text: str, how: str, expected: str) -> bool:
    lines = text.splitlines()
    if how == "line2":
        return len(lines) > 1 and lines[1].strip() == expected and \
            sum(1 for ln in lines if ln.strip() == expected) == 1
    return sum(1 for ln in lines if ln.strip() == expected) == 1


def freeze_commit() -> str:
    """The freeze commit is, by construction, the last commit that touched code/ or protocol/."""
    return git("log", "-1", "--format=%H", "--", f"{NS_REL}/code", f"{NS_REL}/protocol").stdout.strip()


# ------------------------------------------------------------------ B1 repair: identity and prior evaluation
def check_identity() -> dict:
    """The qualified worktree, git dir, common dir and branch -- checked before anything else in execute/seal-only."""
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
    """No marker of this campaign or of C12; no result of either, in the tree, in any history or on disk."""
    for prefix in PRIOR_MARKERS:
        if git("for-each-ref", "--format=%(refname)", prefix).stdout.strip():
            raise Refusal("CONSUMED", f"a marker exists under {prefix}")
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    for rel in PRIOR_RESULTS:
        if rel in names or (REPO / rel).exists() or git("log", "--all", "--format=%H", "--", rel).stdout.strip():
            raise Refusal("TARGET_ARTIFACT_EXISTS", rel)


def check_clean() -> None:
    if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
        raise Refusal("DIRTY_TREE")
    gd = Path(git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())
    cd = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    locks = [p for p in (gd / "index.lock", gd / "HEAD.lock", cd / (QUALIFIED_BRANCH + ".lock"),
                         cd / "packed-refs.lock") if p.exists()]
    if locks:
        raise Refusal("GIT_LOCKED", str(locks[0]))


def check_seal_preconditions() -> dict:
    """Everything the seal needs that can be checked without the target (N3/B1): before the marker exists."""
    if git("var", "GIT_COMMITTER_IDENT").returncode or git("var", "GIT_AUTHOR_IDENT").returncode:
        raise Refusal("SEAL_PRECONDITION", "no committer/author identity")
    head = git("rev-parse", "HEAD").stdout.strip()
    with tempfile.TemporaryDirectory(prefix="c12r1pre") as td:
        idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
        if git("read-tree", head, env_extra=idx).returncode or git("write-tree", env_extra=idx).returncode:
            raise Refusal("SEAL_PRECONDITION", "a private index cannot be built")
    d = (REPO / RESULT_REL).parent
    probe = d / ".c12r1_write_probe"
    try:
        d.mkdir(parents=True, exist_ok=True)
        probe.write_text("probe")
        probe.unlink()
    except OSError:
        raise Refusal("SEAL_PRECONDITION", "the result directory is not writable")
    if git("rev-parse", "-q", "--verify", QUALIFIED_BRANCH).returncode:
        raise Refusal("SEAL_PRECONDITION", "the branch ref does not resolve")
    return {"branch_head": head}


# ------------------------------------------------------------------ G00-G02, G04-G07: bindings and state
def check_bindings() -> dict:
    shas = {}
    for key in PINS:
        shas[key] = sha(read_pinned(key))
    for key, prefix in BLOBS.items():
        got = git("rev-parse", f"HEAD:{PINS[key][0]}").stdout.strip()
        if not got.startswith(prefix):
            raise Refusal("BLOB_MISMATCH", PINS[key][0])
        if git("hash-object", "--", PINS[key][0]).stdout.strip() != got:
            raise Refusal("WORKTREE_DIFFERS_FROM_COMMIT", PINS[key][0])
    for commit, word in LINEAGE:
        if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("LINEAGE", commit)
        if word not in git("log", "-1", "--format=%s", commit).stdout:
            raise Refusal("LINEAGE_ROLE", commit)
    for key, how, expected in VERDICTS:
        if not verdict_ok(read_pinned(key).decode(), how, expected):
            raise Refusal("REVIEW_VERDICT", f"{PINS[key][0]} lacks exactly one '{expected}'")
    rule = json.loads(read_pinned("floor_rule"))
    body = {k: v for k, v in rule.items() if k != "sha256"}
    if sha(json.dumps(body, sort_keys=True).encode()) != rule.get("sha256"):
        raise Refusal("FLOOR_SELF_HASH")
    gate = json.loads(read_pinned("floor_gate"))
    if [g["id"] for g in gate["items"]] != [f"G{i:02d}" for i in range(15)]:
        raise Refusal("GATE_ITEMS")
    return shas


def check_governance_state() -> dict:
    """G02: r5 authoritative and unchanged, 306-309 open, no r6 anywhere."""
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    if any(Path(n).name.startswith(R6_NAME) for n in names):
        raise Refusal("R6_EXISTS")
    if git("log", "--all", "--format=%H", "--", f"*{R6_NAME}*").stdout.strip():
        raise Refusal("R6_IN_HISTORY")
    if list((REPO / CP).rglob(f"{R6_NAME}*")):
        raise Refusal("R6_EXISTS", "an r6 file exists in the working tree")
    r5 = json.loads(read_pinned("coverage_r5"))
    if r5.get("K5_COVERAGE_COMPLETE") is not False or r5.get("union_open_ranges") != [[306, 309]]:
        raise Refusal("R5_STATE", "r5 no longer lists exactly [306, 309] open")
    m5 = {c["cell"]: c["verdict"] for c in r5["per_m"]["5"]["cells"]}
    if any(m5.get(k) == "PASS" for k in (306, 307, 308, 309)):
        raise Refusal("R5_STATE", "a cell in 306-309 is PASS")
    return {"r6": "absent", "r5_union_open_ranges": r5["union_open_ranges"]}


# ------------------------------------------------------------------ the frozen consumer, from pinned bytes
def load_consumer() -> dict:
    tct = exec_module(read_pinned("tct_rule"), REPO / PINS["tct_rule"][0], "tct_rule")
    fc = exec_module(read_pinned("tail_forecast_r2"), REPO / PINS["tail_forecast_r2"][0], "c12r1_tail_forecast_r2")
    if fc.T is not tct:
        raise Refusal("MODULE_IDENTITY", "tail_forecast_r2 did not bind the pinned tct_rule")
    c2f = exec_module(read_pinned("c2_forecast_code"), REPO / PINS["c2_forecast_code"][0], "c12r1_c2_d5_forecast")
    dc = exec_module(read_pinned("deflated_consume"), REPO / PINS["deflated_consume"][0], "c12r1_deflated_consume")
    if (dc.K1_BOUND, dc.K2_BOUND) != (c2f.K1_BOUND, c2f.K2_BOUND):
        raise Refusal("KAPPA", "consumer kappa differs from C2's local copy")
    R = tct.load_frozen("tc_rule", tct.FROZEN["tc_rule"][1])
    adapter = fc.module("adapter", "c12r1_fc_adapter")
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
    if k not in REHEARSAL_CELLS:
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
    return {"meas": meas, "aux": a["auxiliary_evidence"], "ad": a["m"]["5"], "cov": con["cover"][k],
            "G": T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])}


# ------------------------------------------------------------------ constant sets and supplies (G08, G09)
def validate_set(s: dict) -> None:
    v = {x: s["values"][x] for x in ARGS}
    if not all(type(x) is F for x in v.values()):
        raise Refusal("VALIDATION", f"{s['name']}: not exact rationals")
    if not (v["D_lo"] > 0 and v["tau"] >= 1 and v["C_T"] >= v["tau"] and v["Abar"] >= 1):
        raise Refusal("VALIDATION", f"{s['name']}: tau >= 1, C >= tau, D_lo > 0, Abar >= 1 violated")


def i1_sets(k: int) -> list:
    out = []
    for name, key in (("C1", "registry_c1"), ("C2", "registry_c2")):
        blocks = [b for b in json.loads(read_pinned(key))["blocks"] if b["cell"] == k]
        if len(blocks) != 1 or blocks[0].get("certified") is not True:
            raise Refusal("I1_BLOCK", f"{name} cell {k}")
        out.append({"impl": "I1", "name": name, "values": {x: F(blocks[0][x]) for x in ARGS}})
    return out


def i2_set(c11r: dict, c11rd: dict, runs: dict) -> dict:
    """G05/G06: the accepted six-constant evidence of I2 for cell 306, with statement/domain/class checks."""
    vals = {}
    if c11r["result"].get("independence_violations") != [] or c11rd.get("independence_violations") != []:
        raise Refusal("I2_INDEPENDENCE", "a comparison records independence violations")
    pt = c11r["result"]["per_target"]
    for x, direction in I2_FROM_C11R.items():
        t = pt[x]
        if t.get("target_status") != "CERTIFIED" or t.get("direction") != direction:
            raise Refusal("I2_STATUS", x)
        if t.get("CLASS") not in ACCEPTED_CLASSES:
            raise Refusal("I2_CLASS", x)
        st = t.get("statement") or {}
        if st.get("STATUS") not in ACCEPTED_STATEMENTS or st.get("domain") not in ACCEPTED_DOMAINS:
            raise Refusal("I2_STATEMENT", x)
        vals[x] = F(t["independent_value"])
    if c11rd.get("N9_VERDICT") != "N9_CLOSED":
        raise Refusal("I2_STATUS", "C11RD comparison verdict")
    for x, direction in I2_FROM_C11RD.items():
        t = c11rd["per_target"][x]
        if t.get("direction") != direction or t.get("CLASS") not in ACCEPTED_CLASSES:
            raise Refusal("I2_CLASS", x)
        st = t.get("statement") or {}
        if st.get("STATUS") not in ACCEPTED_STATEMENTS or st.get("domain") not in ACCEPTED_DOMAINS:
            raise Refusal("I2_STATEMENT", x)
        if t["independent_value"] != runs["targets"][x]["value"]:
            raise Refusal("I2_BINDING", f"{x}: comparison value is not the sealed run's value")
        vals[x] = F(t["independent_value"])
    if runs.get("cell") != TARGET_CELL:
        raise Refusal("I2_BINDING", "C11RD runs are not cell 306")
    return {"impl": "I2", "name": "I2", "values": vals}


def i2_block_check(c11r_statements: dict, cov: dict, KM) -> None:
    """The I2 statements' whole block must be cell 306's cover cell exactly (domain EQUAL)."""
    dd = c11r_statements.get("drift_domain") or {}
    if dd.get("cell") != TARGET_CELL or not isinstance(dd.get("e_lo"), str) or not isinstance(dd.get("e_hi"), str):
        raise Refusal("I2_DOMAIN", "C11R drift domain is not an exact cell-306 block")
    if (F(dd["e_lo"]), F(dd["e_hi"])) != (KM.rat(cov["left"]), KM.rat(cov["right"])):
        raise Refusal("I2_DOMAIN", "C11R drift domain is not cell 306's cover cell")


def atoms(con: dict, s: dict) -> dict:
    validate_set(s)
    args = tuple(s["values"][x] for x in ARGS)
    frozen = con["DC"].atom_constants_r2(*args)
    if {j: frozen[j] for j in FIELDS} != con["C2F"]._atom_independent(*args):
        raise Refusal("ATOM_CROSSCHECK", s["name"])
    return frozen


def supply(con: dict, impl: str, sets: list, G: dict) -> tuple:
    """Floor r2 S_I: componentwise minimum over Lemma G and Dv' of I's OWN sets. Never mixes implementations.
    Returns (A, provenance, per-supply atoms)."""
    if not sets or any(s["impl"] != impl for s in sets):
        raise Refusal("MIXED_SUPPLY", f"a supply for {impl} received {[s['impl'] for s in sets]}")
    sup = {"G": G}
    for s in sets:
        if s["name"] in sup:
            raise Refusal("MIXED_SUPPLY", f"duplicate set name {s['name']}")
        sup[s["name"]] = atoms(con, s)
    A, prov = con["C2F"].combine(sup)
    return A, prov, sup


def evaluate(con: dict, ci: dict, A: dict) -> dict:
    res = con["C2F"].direct(con["T"], con["R"], ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    return {"Gamma_exact": str(res["Gamma"]), "Gamma": float(res["Gamma"]), "pass": bool(res["pass"]),
            "H_exact": [str(res["lo"]), str(res["hi"])], "M_after_exact": str(res["M"]),
            "A_exact": {j: str(A[j]) for j in FIELDS}}


# ------------------------------------------------------------------ G10: the control (N2: per-supply records too)
def control(con: dict, k: int, want_cell: dict | None = None, want_supplies: dict | None = None) -> dict:
    ci = cell_inputs(con, k)
    A, prov, sup = supply(con, "I1", i1_sets(k), ci["G"])
    got = evaluate(con, ci, A)
    fc = json.loads(read_pinned("c2_forecast"))
    want = fc["cells"][str(k)] if want_cell is None else want_cell
    wsup = fc["supplies"][str(k)] if want_supplies is None else want_supplies
    fields = {"Gamma_exact": got["Gamma_exact"] == want["Gamma_exact"],
              "A_exact": got["A_exact"] == want["A_exact"],
              "provenance": prov == want["provenance"],
              "H_exact": got["H_exact"] == want["H_exact"],
              "M_after_exact": got["M_after_exact"] == want["M_after_exact"],
              "pass": got["pass"] == want["pass"],
              "per_supply_records_G_C1_C2": sorted(wsup) == sorted(sup) and all(
                  float(sup[n][j]) == wsup[n][j] for n in sup for j in FIELDS)}
    return {"cell": k, "supply": "S_I1 = min{G, C1, C2}", "reproduces_C2_exactly": all(fields.values()),
            "field_matches": fields, "provenance": prov, "evaluated": got}


# ------------------------------------------------------------------ G11: the one target evaluation
def prepare_target(con: dict) -> dict:
    """Every I2 check BEFORE the marker exists, so that only the one evaluation can follow consumption."""
    ci = cell_inputs(con, TARGET_CELL)
    c11r = json.loads(read_pinned("c11r_comparison"))
    c11rd = json.loads(read_pinned("c11rd_comparison"))
    runs = json.loads(read_pinned("c11rd_runs"))
    i2_block_check(json.loads(read_pinned("c11r_statements")), ci["cov"], con["KM"])
    A, prov, _ = supply(con, "I2", [i2_set(c11r, c11rd, runs)], ci["G"])
    return {"ci": ci, "A": A, "prov": prov}


def evaluate_target(con: dict, prep: dict) -> dict:
    got = evaluate(con, prep["ci"], prep["A"])
    return {"cell": TARGET_CELL, "supply": "S_I2 = min{G, I2}", "provenance": prep["prov"], "evaluated": got}


def decide(ctl: dict, tgt: dict) -> dict:
    """The frozen floor r2 decision table (advisory: adoption is decided by the independent adjudication)."""
    base = ctl["evaluated"]["pass"]
    f1p_d = base and tgt["evaluated"]["pass"]
    return {"base_clause_Gamma_S_I1_lt_0": base,
            "F1_prime_a_to_c": "bound before consumption (G05-G07): I1 and I2 certified, six AGREES/STRONGER, "
                               "accepted reviews, no independence violation",
            "F1_prime_d_both_supplies_lt_0": f1p_d,
            "F1_prime": f1p_d,
            "F2": "NOT_SATISFIED: C2 published F2 FAIL on S_I1 for cell 306; floor r2 does not revisit it and this "
                  "campaign does not re-evaluate it",
            "floor_r2_satisfied_mechanically": bool(base and f1p_d),
            "scientific_closure": {"S_I1": base, "S_I2": tgt["evaluated"]["pass"]},
            "note": "adoption requires this table AND G13 (independent execution review and adoption adjudication)"}


# ------------------------------------------------------------------ the grant (N5: derived, not trusted)
def check_grant(own_sha: str) -> dict:
    head = git("rev-parse", "HEAD").stdout.strip()
    if not (REPO / GRANT_REL).exists():
        raise Refusal("GRANT_MISSING")
    if git("log", "-1", "--format=%H", "--", GRANT_REL).stdout.strip() != head:
        raise Refusal("GRANT_INVALID", "HEAD is not the grant commit")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.split() != [GRANT_REL]:
        raise Refusal("GRANT_INVALID", "the grant commit changes more than the grant")
    g = json.loads((REPO / GRANT_REL).read_bytes())
    if g.get("schema") != "rebaseguard.p5y.k5.tail-c12r1.grant.v1" or g.get("exactly_once") is not True:
        raise Refusal("GRANT_INVALID", "schema")
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
    if not qfiles or any(not f.startswith(NS_REL + "/evidence/qualification/") for f in qfiles) or QUAL_REL not in qfiles:
        raise Refusal("GRANT_INVALID", "the qualification commit is not qualification evidence only")
    q = json.loads(git("show", f"{qual_c}:{QUAL_REL}").stdout)
    if q.get("pass") is not True or q.get("dry_run") is not False or q.get("freeze_commit") != fz:
        raise Refusal("GRANT_INVALID", "the qualification report is not a PASS at the freeze commit")
    if not (REPO / QREVIEW_REL).exists():
        raise Refusal("REVIEW_MISSING", QREVIEW_REL)
    if not verdict_ok((REPO / QREVIEW_REL).read_text(), "line2", "QUALIFICATION_ACCEPTED"):
        raise Refusal("REVIEW_VERDICT", "qualification review is not QUALIFICATION_ACCEPTED")
    return {"grant_commit": head, "grant_sha256": sha((REPO / GRANT_REL).read_bytes()), "freeze_commit": fz,
            "qualification_commit": qual_c, "qualification_review_commit": review_c}


# ------------------------------------------------------------------ seal
def seal(message: str) -> str:
    """Commit the result file alone on top of HEAD through a private index, with CAS on the qualified branch."""
    last = None
    for delay in (0.0, *SEAL_RETRY_DELAYS):
        time.sleep(delay)
        head = git("rev-parse", "HEAD").stdout.strip()
        with tempfile.TemporaryDirectory(prefix="c12r1seal") as td:
            idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
            msgf = Path(td) / "msg"
            msgf.write_text(message)
            steps = [git("read-tree", head, env_extra=idx),
                     git("update-index", "--add", "--", RESULT_REL, env_extra=idx)]
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
            git("update-index", "--add", "--", RESULT_REL)          # align the main index with the new HEAD
            return cid
    raise Refusal("UNSEALED", f"seal failed at {last}")


def write_result(obj: dict) -> None:
    path = REPO / RESULT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(obj)
    body["sha256"] = sha(json.dumps(body, sort_keys=True).encode())
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, path)


def seal_message(status: str) -> str:
    return (f"p5y: K5 C12-R1 — SEAL of the one cell-306 floor-r2 evaluation ({status})\n\n"
            f"Written and committed by {NS_REL}/code/c12r1_cell306.py; the result was not inspected before this "
            "commit.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")


# ------------------------------------------------------------------ modes
def run_execute(own_sha: str, prepare=None, evaluator=None, sealer=None) -> int:
    """`prepare`, `evaluator` and `sealer` are injection points for the qualification's DECOY flow tests only; the
    CLI never passes them (a static check enforces it)."""
    prepare, evaluator, sealer = prepare or prepare_target, evaluator or evaluate_target, sealer or seal
    t0, started = time.time(), utc()
    ident = check_identity()                                                  # B1: nothing is read before this
    check_not_evaluated()
    check_clean()
    grant = check_grant(own_sha)
    shas = check_bindings()
    state = check_governance_state()
    pre = check_seal_preconditions()
    con = load_consumer()
    ctl = control(con, TARGET_CELL)                                           # G10, before anything about I2
    common = {"schema": "rebaseguard.p5y.k5.tail-c12r1.cell306-result.v1", "cell": TARGET_CELL, "m": 5,
              "floor": "r2 (rule a15d083b, review 3fadb422)", "identity": ident, "grant": grant,
              "input_sha256": shas, "governance_state_before": state, "seal_preconditions": pre,
              "driver_sha256": own_sha, "started_utc": started, "control": ctl, "python": sys.version.split()[0]}
    if not ctl["reproduces_C2_exactly"]:
        common.update({"status": "CONTROL_FAILED", "target_evaluated": False, "target_evaluations": 0,
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3)})
        write_result(common)
        try:
            cid = sealer(seal_message("CONTROL_FAILED"))
        except Refusal:
            print("C12R1 CONTROL_FAILED UNSEALED: run `seal-only`; the target was not evaluated")
            return 4
        print(f"C12R1 CONTROL_FAILED sealed {cid}; the target was not evaluated")
        return 3
    prep = prepare(con)                                                       # every I2 check; no Gamma yet
    if git("update-ref", CONSUMED_REF, grant["grant_commit"], "0" * 40).returncode != 0:
        raise Refusal("CONSUMED", "the exactly-once marker could not be created: the target is never evaluated twice")
    try:                                                                      # consumed: from here, record and seal
        tgt = evaluator(con, prep)
        status, table = "TARGET_EVALUATED", decide(ctl, tgt)
    except BaseException as exc:                                              # N3: SystemExit, wall cap, anything
        tgt, status, table = {"error": f"{type(exc).__name__}: {exc}"[:500]}, "TARGET_EVALUATION_FAILED", None
    signal.alarm(0)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    common.update({"status": status, "target_evaluated": status == "TARGET_EVALUATED", "target_evaluations": 1,
                   "consumed_ref": CONSUMED_REF, "target": tgt, "floor_r2_table": table,
                   "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                   "peak_rss_bytes": usage.ru_maxrss, "cpu_seconds": round(usage.ru_utime + usage.ru_stime, 3)})
    write_result(common)
    try:
        cid = sealer(seal_message(status))
    except Refusal:
        print("C12R1 UNSEALED: the result is written; run `seal-only`. NEVER run execute again.")
        return 4
    print(f"C12R1 SEALED {cid} (status {status}; one target evaluation; result not printed)")
    return 0 if status == "TARGET_EVALUATED" else 5


def run_seal_only() -> int:
    """N4: never computes; verifies the written result's self-hash and status; the commit names the real status."""
    check_identity()
    path = REPO / RESULT_REL
    if RESULT_REL in git("ls-tree", "-r", "--name-only", "HEAD").stdout.split():
        print("C12R1 already sealed")
        return 0
    if not path.exists():
        raise Refusal("SEAL_ONLY", "no written result")
    res = json.loads(path.read_bytes())
    body = {k: v for k, v in res.items() if k != "sha256"}
    if sha(json.dumps(body, sort_keys=True).encode()) != res.get("sha256"):
        raise Refusal("SEAL_ONLY", "the written result's self-hash does not verify")
    marker = bool(git("rev-parse", "-q", "--verify", CONSUMED_REF).stdout.strip())
    status = res.get("status")
    if not ((status in ("TARGET_EVALUATED", "TARGET_EVALUATION_FAILED") and marker and res.get("target_evaluations") == 1)
            or (status == "CONTROL_FAILED" and not marker and res.get("target_evaluations") == 0)):
        raise Refusal("SEAL_ONLY", "status and marker are inconsistent")
    others = [ln for ln in git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
              if not ln.endswith(RESULT_REL)]
    if others:
        raise Refusal("DIRTY_TREE", "only the written result may be pending")
    cid = seal(seal_message(f"{status}, sealed by seal-only"))
    print(f"C12R1 SEALED {cid} (seal-only; status {status})")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("preflight", "rehearse", "execute", "seal-only"))
    ap.add_argument("--cell", type=int)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    own_sha = sha(HERE.read_bytes())

    def wall_cap(*_):
        raise Refusal("WALL_CAP", f"{WALL_CAP_S} s")

    signal.signal(signal.SIGALRM, wall_cap)
    signal.alarm(WALL_CAP_S)
    try:
        if a.mode != "rehearse" and a.cell is not None:
            raise Refusal("CELL_OUT_OF_SCOPE", "only rehearse takes --cell; execute is cell 306 only")
        if a.mode == "preflight":
            check_not_evaluated()
            out = {"mode": "preflight", "input_sha256": check_bindings(),
                   "governance_state": check_governance_state(), "driver_sha256": own_sha}
            load_consumer()
            print("C12R1 PREFLIGHT PASS")
        elif a.mode == "rehearse":
            if a.cell not in REHEARSAL_CELLS:
                raise Refusal("CELL_OUT_OF_SCOPE", str(a.cell))
            check_not_evaluated()
            check_bindings()
            check_governance_state()
            t0 = time.time()
            ctl = control(load_consumer(), a.cell)
            usage = resource.getrusage(resource.RUSAGE_SELF)
            out = {"mode": "rehearse", "control": ctl, "wall_seconds": round(time.time() - t0, 3),
                   "peak_rss_bytes": usage.ru_maxrss, "driver_sha256": own_sha, "utc": utc()}
            print(f"C12R1 REHEARSE cell {a.cell}: reproduces C2 exactly = {ctl['reproduces_C2_exactly']}")
            if not ctl["reproduces_C2_exactly"]:
                if a.out:
                    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
                return 3
        elif a.mode == "execute":
            return run_execute(own_sha)
        else:
            return run_seal_only()
        if a.out:
            Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
        return 0
    except Refusal as e:
        print(f"C12R1 REFUSED {e}")
        return 4 if e.code == "UNSEALED" else 2
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    sys.exit(main())
