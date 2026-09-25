"""C11RD -- the problem data: the CUSUM model, the cell, the reachable set, the bands, and the ONE
accepted premise this campaign consumes (C11R's F_H supersolution certificate).

Everything here is DATA, re-derived or read from committed, hash-bound files. No target D1/D2
value, no original certificate, no registry row and no C11R comparison is read by this module (the
statement-table file it reads carries no magnitude: CONTAINS_NO_ORIGINAL_MAGNITUDE is true).

THE MODEL (the same specification C11's independent certifier re-derived from the frozen model text;
see docs/D1_D2_STATEMENT_AUDIT.md section 2):
  state x = (p, m), p, m >= 0; reference K = 1/2; alarm threshold C = 11/2; increment z with
  z + e ~ N(0, 1) (density phi(z + e)); alarm-free window z in [m - C, C - p];
  next state x'(z) = (max(0, p + z - K), max(0, m - z - K)); atom a = (0, 0).
  R = {(p, m) in [0, 5]^2 : p + m <= 4 or p = 0 or m = 0}   (C11 / C11R state-set specification).
"""
from __future__ import annotations

import json
import pathlib
import subprocess
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CLOSURE = NS.parent
REPO = CLOSURE.parent.parent
NS_REL = "level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension"

K = F(1, 2)
H = F(5)
C = K + H                      # 11/2
ATOM = (F(0), F(0))
BANDS = (0, 1, 2, 3, 4)       # band k: k <= p + m <= k + 1; band 4 exists on the axes only
TARGET_CELL = 306

# ---- frozen inputs, bound by git blob id (verified at load) ----------------------------------
C11R_NS = "level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment"
STATEMENT_TABLE_REL = f"{C11R_NS}/evidence/table/C11R_N9_STATEMENTS.json"
STATEMENT_TABLE_BLOB = "58b4066f5cce7efd139154c1b50e8661b4b5861b"
C11R_RUNS_REL = f"{C11R_NS}/evidence/runs/C11R_RUNS.json"
C11R_RUNS_BLOB = "a53516031948cf44255d7980dc5c7af5ae8b2afd"      # sealed at 5ff4cc5b, EXECUTION_ACCEPTED
C11R_SEAL_COMMIT = "5ff4cc5b310b31bc7b61213598aade9a5188964e"
C11R_FINAL_HEAD = "7375b9cdb1d770ba836335164f205e26b445035e"


# The N9 statement semantics for D1/D2, as C11R's FROZEN schema defines them (c11r_schema.STATE_SET_R,
# QUANTITY, PROPOSITION, CONVENTION, and the route it reserved for this work,
# "independent_derivative_propagation", which necessarily consumes C_T_independent and
# tau_independent). Written here, not imported; equality with the frozen schema is validation V18.
STATE_SET_R = ("R = {(p, m) in [0,5]^2 : p + m <= 4 or p = 0 or m = 0}; "
               "atom a = (0, 0); certified over a box cover that is a superset of R")
ROUTE = "independent_derivative_propagation"
QUANTITY = {"D1": "|d'(atom)|, the first drift derivative of d",
            "D2": "|d''(atom)|, the second drift derivative of d"}
PROPOSITION = {"D1": "for every e in the block: |D_e'| <= value",
               "D2": "for every e in the block: |D_e''| <= value"}
DEPENDENCIES = ("C_T_independent", "tau_independent")
C11R_SCHEMA_REL = f"{C11R_NS}/code/c11r_schema.py"


class ModelError(Exception):
    pass


def git_blob(path: pathlib.Path) -> str:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), "hash-object",
                           "--no-filters", str(path)], capture_output=True, text=True,
                          check=True, env={"PATH": "/usr/bin:/bin", "GIT_NO_REPLACE_OBJECTS": "1"}
                          ).stdout.strip()


GIT_HARD = ("git", "--no-replace-objects", "-c", "core.commitGraph=false")
GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_NO_REPLACE_OBJECTS": "1"}


def history_commits(rels: list, repo=None) -> list:
    """Every commit reachable from ANY ref or reflog entry (all worktrees' HEADs included) that ever
    touched one of the paths, over the FULL history (--full-history: a path added on a side branch
    that was merged, or added and later deleted or reverted, is still found). Replace refs are
    ignored and a commit-graph file is not trusted. FAILS CLOSED (ModelError) when the history is
    not complete or not readable: a shallow repository, a grafts file, or any git error."""
    repo = str(repo or REPO)

    def run(*args):
        return subprocess.run([*GIT_HARD, "-C", repo, *args], capture_output=True, text=True, env=GIT_ENV)
    sh = run("rev-parse", "--is-shallow-repository")
    if sh.returncode != 0 or sh.stdout.strip() != "false":
        raise ModelError(f"history not complete: shallow check {sh.stdout.strip() or sh.stderr.strip()!r}")
    cd = run("rev-parse", "--path-format=absolute", "--git-common-dir")
    if cd.returncode != 0:
        raise ModelError(f"history not readable: {cd.stderr.strip()}")
    common = pathlib.Path(cd.stdout.strip())
    for leaf in ("info/grafts", "shallow"):
        if (common / leaf).exists():
            raise ModelError(f"history not trustworthy: {leaf} present")
    r = run("rev-list", "--all", "--reflog", "--full-history", "--", *rels)
    if r.returncode != 0:
        raise ModelError(f"history not readable: {r.stderr.strip()}")
    return r.stdout.split()


def _load_bound(rel: str, blob: str) -> dict:
    p = REPO / rel
    got = git_blob(p)
    if got != blob:
        raise ModelError(f"{rel}: blob {got} is not the frozen {blob}")
    return json.loads(p.read_text())


def cell_block(stmt: dict | None = None) -> tuple[F, F]:
    """Cell 306's drift block, exact, from C11R's frozen statement table."""
    stmt = stmt or _load_bound(STATEMENT_TABLE_REL, STATEMENT_TABLE_BLOB)
    d = stmt["drift_domain"]
    if d.get("cell") != TARGET_CELL:
        raise ModelError("the statement table is not cell 306's")
    return F(d["e_lo"]), F(d["e_hi"])


def original_d_statements(stmt: dict | None = None) -> dict:
    """The ORIGINAL D1/D2 propositions (semantics only; the table holds no magnitude)."""
    stmt = stmt or _load_bound(STATEMENT_TABLE_REL, STATEMENT_TABLE_BLOB)
    if stmt.get("CONTAINS_NO_ORIGINAL_MAGNITUDE") is not True:
        raise ModelError("statement table does not declare itself magnitude-free")
    out = {}
    for k in ("D1", "D2"):
        v = dict(stmt["original_statements"][k])
        if "value" in v or "value_float" in v:
            raise ModelError("statement table carries a value field")
        out[k] = v
    return out


def comparison_rule(stmt: dict | None = None) -> dict:
    """The factor-2 agreement rule C11R froze before any result (read, never restated)."""
    stmt = stmt or _load_bound(STATEMENT_TABLE_REL, STATEMENT_TABLE_BLOB)
    return dict(stmt["comparison_semantics_frozen_before_results"])


def c11r_fh_premise() -> dict:
    """The ACCEPTED C11R certificate F_H: for every e in cell 306's block, w >= 1 + Khat_e w on a
    cover of R, with w = A - B m. Consumed as a frozen PREMISE (never recomputed):
        Ghat_e 1 <= w on R  =>  ||Ghat_e|| <= sup_R w = A  and  (Ghat_e 1)(a) <= w(a) = A,
    because B >= 0 and m >= 0 on R."""
    runs = _load_bound(C11R_RUNS_REL, C11R_RUNS_BLOB)
    c = runs["certificates"]["F_H"]
    res = c["certifier_result"]
    lo, hi = cell_block()
    problems = []
    if c.get("certificate_id") != "F_H" or res.get("kernel") != "Khat_e" or res.get("certified") is not True:
        problems.append("F_H is not a certified Khat_e supersolution")
    if c["inputs"].get("atom_removed_argument") is not True:
        problems.append("F_H was not run with the atom removed")
    if [F(x) for x in c["inputs"]["drift_block"]] != [lo, hi]:
        problems.append("F_H's drift block is not cell 306's")
    if c.get("aggregation") != "single_certificate_whole_block":
        problems.append("F_H is not a whole-block certificate")
    if c.get("premises") != []:
        problems.append("F_H has premises")
    w = {tuple(int(t) for t in k.split(",")): F(v) for k, v in c["weight"].items()}
    if set(w) != {(0, 0), (0, 1)}:
        problems.append("F_H's weight is not of the form A - B m")
    A, B = w.get((0, 0), F(0)), -w.get((0, 1), F(0))
    if not (A > 0 and B >= 0):
        problems.append("F_H's weight does not have A > 0, B >= 0")
    if F(res["w_min_lower_bound"]) < 0 or F(res["margin_lower_bound"]) <= 0:
        problems.append("F_H's certified margin or w_min is not positive")
    if problems:
        raise ModelError("; ".join(problems))
    return {"A": A, "B": B, "C_T": A, "tau": A, "certificate_id": "F_H",
            "input_digest": c["input_digest"], "certifier": dict(c["certifier"]),
            "source": {"file": C11R_RUNS_REL, "blob": C11R_RUNS_BLOB,
                       "seal_commit": C11R_SEAL_COMMIT},
            "statement": "for every e in [680769/400000, 17885921/10000000]: w >= 1 + Khat_e w on R, "
                         "w = A - B m; hence ||Ghat_e|| <= A and (Ghat_e 1)(a) <= A"}


def kernel_norms() -> dict:
    """kappa_i >= sup_x int_window |phi^(i)(z + e)| dz, by the whole-line absolute moments:
        kappa_1 = int |phi'| = 2 phi(0),   kappa_2 = int |y^2 - 1| phi = 4 phi(1).
    Upper ends of C7's rigorous phi enclosures."""
    import c11rd_tm as T
    return {1: 2 * T.phi_point(F(0))[1], 2: 4 * T.phi_point(F(1))[1]}


def in_R(p: F, m: F) -> bool:
    return p >= 0 and m >= 0 and p <= H and m <= H and (p + m <= 4 or p == 0 or m == 0)
