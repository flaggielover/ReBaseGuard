"""C11R shared helpers. Narrow repair successor to C11: can the independent certifier prove THE
SAME STATEMENT N9 requires, for cell 306, over the frozen drift block. No adoption, no
coverage change, no r6, no alpha, no C2 floor replacement.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CLOSURE = NS.parent
REPO = CLOSURE.parent.parent

C2 = CLOSURE / "p5y_k5_tail_c2_closure"
C7 = CLOSURE / "p5y_k5_tail_c7_e2_lambda309"
C9 = CLOSURE / "p5y_k5_tail_c9_e1_cell307"
C10 = CLOSURE / "p5y_k5_tail_c10_governance_provenance"
C11 = CLOSURE / "p5y_k5_tail_c11_n9_independent_certifier"
AD = CLOSURE / "p5y_k5_perron_deflated_resolvent"

C11_HEAD = "440bcd9183f4f883428cba41d47aa7780fd681c4"
REMOTE_MAIN_EXPECTED = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
ORIGINAL_CERTIFIER = "level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/taboo_certify.py"
OPEN_CELLS = (306, 307, 308, 309)
TARGET_CELL = 306
SIX_CONSTANTS = ("C_T", "tau", "Abar", "D_lo", "D1", "D2")


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True,
                          check=True).stdout.strip()


def git_ok(*a: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).returncode == 0


def git_in(repo, *a: str) -> str:
    """git in an explicit repository root (the real one, or a synthetic rehearsal repository)."""
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True,
                          check=True).stdout.strip()


def git_ok_in(repo, *a: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                          text=True).returncode == 0


def git_grep(pattern: str, *paths: str) -> list[str]:
    r = subprocess.run(["git", "-C", str(REPO), "grep", "-l", "-E", pattern, "HEAD", "--", *paths],
                       capture_output=True, text=True)
    if r.returncode > 1:
        raise RuntimeError(f"git grep failed: {r.stderr[:200]}")
    return [x for x in r.stdout.strip().splitlines() if x]


def blob_at(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def blob_at_in(repo, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_obj(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ---------------------------------------------------------------------------------------------
# PROVENANCE (repair E, erratum E4). The first freeze carried a mutation artifact produced by
# older code than the validation artifact beside it, and nothing recorded which code produced
# either, so the contradiction could not be traced from the evidence. Every artifact now binds:
#   * the sha256 of its producer module,
#   * the sha256 of every campaign module the producer imports, transitively,
#   * the sha256 of every artifact it read through load().
# code/c11r_status.py recomputes all of them and refuses on any mismatch.
# ---------------------------------------------------------------------------------------------
CODE_DIRS = (HERE, C11 / "code", C7 / "code")
_READS: dict[str, str] = {}

# ---------------------------------------------------------------------------------------------
# WHAT IS PROTECTED (round 3, blocker B-2). One definition, imported by the firewall, the status
# checker, B0 and the leak check. A PROTECTED artifact carries original cell 306 magnitudes, or
# is historical review prose that quotes them. No pre-comparison module may load one.
# ---------------------------------------------------------------------------------------------
PROTECTED_FILES = ("REGISTRY_C2.json", "C11R_ORIGINAL_MAGNITUDES.json", "C11R_N9_TABLE.json",
                   "C11R_COMPARISON.json", "C11R_SCREEN.json")
# Review and adjudication reports are untrusted prose, and several quote original values. No
# production module parses one, in this campaign or in any predecessor's.
PROTECTED_PREFIXES = ("REVIEW_", "ADJUDICATION_")
PROTECTED_DIR_SEGMENTS = ("quarantine", "review")
RETIRED_FILES = ("C11R_SCREEN.json",)
QUARANTINE_REL = "evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"
NS_REL = "level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment"

# THE EXPLICIT ALLOWLIST of pre-result artifacts (relative to NS). It replaces every directory
# glob: the round-2 status checker and B0 json-loaded whole directory trees, which reached the
# quarantine and the registry. A checker walks THIS list and nothing else.
PRE_RESULT_ARTIFACTS = (
    "evidence/procs/C11R_PROCESS_DETECTOR.json",
    "evidence/b0/C11R_B0.json",
    "evidence/errata/C11R_ERRATA.json",
    "evidence/table/C11R_N9_STATEMENTS.json",
    "evidence/equivalence/C11R_EQUIVALENCE.json",
    "evidence/validation/C11R_VALIDATION.json",
    "evidence/cost/C11R_COST.json",
    "config/C11R_POLICY.json",
    "evidence/policy/C11R_POLICY_EVIDENCE.json",
    "config/C11R_CONTRACT.json",
    "config/N9R_GATE_C11R.json",
    "evidence/firewall/C11R_FIREWALL.json",
    "evidence/chain/C11R_CHAIN_CONTROLS.json",
    "evidence/mutations/C11R_MUTATIONS.json",
    "evidence/leakcheck/C11R_LEAKCHECK.json",
    "evidence/status/C11R_STATUS.json",
)
# What a module that runs BEFORE the comparison may content-read inside this namespace: the
# pre-result artifacts, and the two post-freeze inputs the runner itself needs. The runs artifact
# is deliberately absent: it carries prospective cell 306 values and only the comparator reads it.
ALLOWED_NS_INPUTS = PRE_RESULT_ARTIFACTS + ("config/C11R_AUTHORIZATION.json",
                                            "evidence/qualification/C11R_QUALIFICATION.json")
# What such a module may content-read OUTSIDE this namespace, besides Python source. Each entry is
# value-scanned for every original magnitude by the leak check (c11r_table.py --leak-check).
DECLARED_EXTERNAL_INPUTS = (R5_PATH,)


def is_protected(rel: str) -> bool:
    """By name and path segment, so it applies to relative and absolute paths alike."""
    name = pathlib.PurePosixPath(rel).name
    parts = pathlib.PurePosixPath(rel).parts
    return (name in PROTECTED_FILES or any(name.startswith(x) for x in PROTECTED_PREFIXES)
            or any(seg in parts for seg in PROTECTED_DIR_SEGMENTS))


# ---------------------------------------------------------------------------------------------
# THE RUNTIME OPEN-GUARD (round 4, review round 3 N-1). DEFENSE IN DEPTH, not a proof.
# The static firewall is a heuristic (it missed 14 of 20 paths the third reviewer planted). This
# guard is enforced at RUNTIME in every process that imports this module: a CPython audit hook
# refuses any Python-level `open` (open, io.open, os.open, Path.read_text/read_bytes, json.load of
# an opened file, linecache, fileinput, ...) of a PROTECTED path unless the running program is one
# of the two sanctioned readers. It does NOT see content read by a subprocess (git show, cat, a
# `python -c` child that does not import this module); the static analysis and the allowlists
# cover those. The refusal fires on the open event, before any byte is read.
# ---------------------------------------------------------------------------------------------
READER_PROGRAMS = frozenset({"c11r_table.py", "c11r_compare.py"})


def running_program() -> str:
    return pathlib.PurePath(sys.argv[0]).name if sys.argv and sys.argv[0] else ""


def _open_guard(event, args):
    if event != "open" or not args:
        return
    path = args[0]
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, str):
        return                                    # a file descriptor, not a path
    if is_protected(path) and running_program() not in READER_PROGRAMS:
        raise PermissionError(f"C11R runtime open-guard: {running_program() or 'this process'} "
                              f"may not open protected file {pathlib.PurePath(path).name}")


if not getattr(sys, "_c11r_open_guard_installed", False):
    sys.addaudithook(_open_guard)
    sys._c11r_open_guard_installed = True


def content_free_id(path) -> str | None:
    """Identity of a file WITHOUT its content entering this process.

    `git hash-object` reads the file in a git subprocess and returns only its object id. This is
    how a pre-comparison module checks that a PROTECTED file is unchanged: it compares ids, never
    bytes. It is the only sanctioned way for such a module to refer to a protected file.
    """
    path = pathlib.Path(path)
    if not path.exists():
        return None
    r = subprocess.run(["git", "hash-object", "--", str(path)], capture_output=True, text=True)
    return "gitobj:" + r.stdout.strip() if r.returncode == 0 else None


def _rel(p: pathlib.Path) -> str:
    return str(pathlib.Path(p).resolve().relative_to(REPO))


def load(p: pathlib.Path):
    """Load a JSON artifact, and record what was read so the writer can bind it.

    A PROTECTED input is recorded by its content-free id, so that verifying the record later never
    requires reading the protected content. Only the two sanctioned readers ever call this on a
    protected path; the firewall proves it.
    """
    p = pathlib.Path(p)
    raw = p.read_bytes()
    rel = _rel(p)
    _READS[rel] = content_free_id(p) if is_protected(rel) else sha256_bytes(raw)
    return json.loads(raw)


def load_allowlisted(rel: str):
    """Load a pre-result artifact by its allowlist entry. Refuses anything off the list."""
    if rel not in PRE_RESULT_ARTIFACTS:
        raise ValueError(f"{rel!r} is not an allowlisted pre-result artifact")
    return load(NS / rel)


def read_code(rel: str) -> str:
    """Source of a module by repo-relative path. Python source only, by construction: the path is
    forced to end in .py, so the firewall can see that no data artifact is read through here."""
    if not rel.endswith(".py"):
        raise ValueError(f"read_code reads Python source only, not {rel!r}")
    return (REPO / rel).with_suffix(".py").read_text()


def sha256_code(rel: str) -> str:
    """sha256 of a module's bytes, by repo-relative path; Python source only, as read_code."""
    if not rel.endswith(".py"):
        raise ValueError(f"sha256_code hashes Python source only, not {rel!r}")
    return sha256_bytes((REPO / rel).with_suffix(".py").read_bytes())


def git_object_at(commit: str, rel: str, repo=None) -> str | None:
    """The git object id of a path at a commit: `rev-parse`, which prints an id, never content."""
    r = subprocess.run(["git", "-C", str(repo or REPO), "rev-parse", f"{commit}:{rel}"],
                       capture_output=True, text=True)
    return "gitobj:" + r.stdout.strip() if r.returncode == 0 else None


def _resolve_module(name: str) -> pathlib.Path | None:
    for d in CODE_DIRS:
        cand = d / f"{name}.py"
        if cand.exists():
            return cand
    return None


def code_closure(producer: pathlib.Path) -> dict[str, str]:
    """sha256 of the producer and of every campaign module it imports, transitively."""
    import ast
    seen: dict[str, str] = {}
    stack = [pathlib.Path(producer).resolve()]
    while stack:
        f = stack.pop()
        rel = _rel(f)
        if rel in seen:
            continue
        seen[rel] = sha256_file(f)
        for n in ast.walk(ast.parse(f.read_text())):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names = [n.module.split(".")[0]]
            for nm in names:
                r = _resolve_module(nm)
                if r is not None:
                    stack.append(r.resolve())
    return dict(sorted(seen.items()))


def provenance(producer) -> dict:
    prod = pathlib.Path(producer).resolve()
    return {"producer": _rel(prod),
            "producer_sha256": sha256_file(prod),
            "code_closure": code_closure(prod),
            "inputs": dict(sorted(_READS.items()))}


def write_evidence(p: pathlib.Path, obj: dict, *, producer) -> str:
    """Write an artifact bound to the code and inputs that produced it.

    `producer` is MANDATORY. An artifact that cannot say which code made it is exactly the kind
    that let a REFUSE mutation record sit unnoticed beside a PASS validation (erratum E4).
    """
    body = evidence_body(obj, producer=producer)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    return body["sha256"]


def evidence_body(obj: dict, *, producer) -> dict:
    """Exactly what write_evidence writes: the body, its provenance and its sha256."""
    if not producer:
        raise ValueError("write_evidence requires the producer module path")
    body = {k: v for k, v in obj.items() if k not in ("sha256", "provenance")}
    body["provenance"] = provenance(producer)
    body["sha256"] = sha256_obj(body)
    return body


def r5_map() -> dict:
    return json.loads(git("show", f"HEAD:{R5_PATH}"))


def r5_open_by_verdict(m: str = "5") -> list[int]:
    return sorted(c["cell"] for c in r5_map()["per_m"][m]["cells"] if c.get("verdict") == "OPEN")


# The revision-1 process detector (classified_processes) lived here. It was blind to the framework
# build of Python on the recorded host (errata E26, E27) and is removed; code/c11r_procs.py
# replaces it.


def toolchain_present() -> dict:
    import importlib.util as u
    return {m: (u.find_spec(m) is not None) for m in
            ("numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2")}
