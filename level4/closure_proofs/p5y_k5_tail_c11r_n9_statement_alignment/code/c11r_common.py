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


# ---------------------------------------------------------------------------------------------
# EVERY git call of this campaign goes through git_run (review round 5, N5-4; erratum E42).
#   * `--no-replace-objects` and GIT_NO_REPLACE_OBJECTS=1: a repository-local replace ref
#     (`git replace`, `git replace --graft`) cannot substitute the objects or the parentage being
#     verified -- the REAL graph is read;
#   * no inherited GIT_* variable (GIT_DIR, GIT_WORK_TREE, GIT_OBJECT_DIRECTORY,
#     GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_GRAFT_FILE, GIT_REPLACE_REF_BASE, GIT_INDEX_FILE,
#     GIT_NAMESPACE, GIT_CONFIG_*, ...) can redirect or rewrite what is read;
#   * a legacy grafts file is NOT disabled by --no-replace-objects (measured), and a shallow
#     repository has no history beyond its boundary: history_integrity() REFUSES both, and every
#     history verifier calls it;
#   * the COMMIT-GRAPH file is NOT read (core.commitGraph=false, set through git_env's
#     GIT_CONFIG_* variables; review 6, N6-6). It is a cache git TRUSTS: a forged graph that
#     drops a merge's second parent made `git rev-list HEAD` and `rev-list --all` omit the side
#     commit and `log -1 %P` report one parent (measured, git 2.50.1), while range walks happened
#     to re-parse the commit. The real commit objects are now read by construction, not by
#     observation. The object database itself (loose objects, packs, their indexes) and the
#     repository configuration beyond these settings are trusted: forging object storage is
#     arbitrary tampering with the repository, out of scope like in-memory patching.
# Every wrapper below spells the same literal argv prefix (git --no-replace-objects -C <repo>) and
# the same env=git_env(); the chain controls parse every campaign module and require that each git
# subprocess call is one of these, with exactly that prefix and environment.
# ---------------------------------------------------------------------------------------------


def git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.commitGraph",
               GIT_CONFIG_VALUE_0="false")          # the real commits, never the graph cache
    return env


def git_run(repo, *a: str, input=None, text: bool = True, check: bool = True):
    """The ONE git entry point: sanitized environment, replace objects disabled."""
    return subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *a], input=input,
                          capture_output=True, text=text, check=check, env=git_env())


def git(*a: str) -> str:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), *a],
                          capture_output=True, text=True, check=True, env=git_env()).stdout.strip()


def git_ok(*a: str) -> bool:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), *a],
                          capture_output=True, text=True, env=git_env()).returncode == 0


def git_in(repo, *a: str) -> str:
    """git in an explicit repository root (the real one, or a synthetic rehearsal repository)."""
    return subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *a],
                          capture_output=True, text=True, check=True, env=git_env()).stdout.strip()


def git_ok_in(repo, *a: str) -> bool:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *a],
                          capture_output=True, text=True, env=git_env()).returncode == 0


def history_integrity(repo) -> dict:
    """What would make git's view of history differ from the objects: refused (grafts, shallow)
    or neutralised (replace refs, ignored by every campaign git call and reported here)."""
    p = []
    if git_in(repo, "rev-parse", "--is-shallow-repository") == "true":
        p.append("history integrity: the repository is shallow -- history beyond its boundary "
                 "is missing")
    grafts = pathlib.Path(git_in(repo, "rev-parse", "--git-path", "info/grafts"))
    if not grafts.is_absolute():
        grafts = pathlib.Path(repo) / grafts
    if grafts.exists():
        p.append("history integrity: a grafts file rewrites commit parentage (not disabled by "
                 "--no-replace-objects)")
    replace = [x for x in git_in(repo, "for-each-ref", "--format=%(refname)",
                                 "refs/replace/").splitlines() if x]
    return {"problems": p, "replace_refs_ignored": len(replace)}


def git_grep(pattern: str, *paths: str) -> list[str]:
    r = subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), "grep", "-l", "-E",
                        pattern, "HEAD", "--", *paths], capture_output=True, text=True,
                       env=git_env())
    if r.returncode > 1:
        raise RuntimeError(f"git grep failed: {r.stderr[:200]}")
    return [x for x in r.stdout.strip().splitlines() if x]


def blob_at(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), "show",
                           f"{commit}:{path}"], capture_output=True, check=True,
                          env=git_env()).stdout


def blob_at_in(repo, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(repo), "show",
                           f"{commit}:{path}"], capture_output=True, check=True,
                          env=git_env()).stdout


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
# pre-result artifacts, and the three post-freeze inputs the chain itself needs (the
# authorization, the execution-permission record, the qualification). The runs artifact is
# deliberately absent: it carries prospective cell 306 values and only the comparator reads it.
ALLOWED_NS_INPUTS = PRE_RESULT_ARTIFACTS + ("config/C11R_AUTHORIZATION.json",
                                            "config/C11R_EXECUTION_PERMISSION.json",
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
# THE RUNTIME OPEN-GUARD. DEFENSE IN DEPTH, not a proof and not the trust boundary: the load-
# bearing protection is the execution chain (c11r_contract / c11r_compare), which refuses before
# the quarantine is opened. A CPython audit hook, installed in every process importing this
# module, refuses a Python-level `open` (open, io.open, os.open, Path.read_*, linecache, ...) of a
# PROTECTED path unless BOTH hold: the code is inside `sanctioned_protected_access(...)` -- used
# only by the extractor's and the comparator's loaders -- AND the running program is one of the
# two readers. REVISION 2 (review round 4, N4-2): the path is judged as given, as an absolute
# path and as its REALPATH, so a symlink with an innocent name, or chdir + a bare name, no longer
# bypasses it; and the program NAME no longer identifies a reader: the running program is a
# reader only when the __main__ module's file RESOLVES to this directory's c11r_table.py or
# c11r_compare.py, so neither a faked sys.argv[0] nor another file named c11r_compare.py is one.
# REVISION 3 (review round 5, N5-10; erratum E47): a PathLike argument (io.FileIO(Path(...)))
# is judged like a string (os.fspath), and the two MAGNITUDE-BEARING files -- the quarantine and
# the registry -- are also recognised by INODE, so a hard link to either, or either file itself
# renamed, under an innocent name is refused too. A COPY is a new inode with an innocent name and
# is NOT refused (review 6, N6-7: the round-6 wording "a renamed copy" overstated this).
# What it still does not see: a COPY of a protected file under an innocent name (made, for
# instance, by a subprocess), content read by a subprocess (git show, cat, a python child that
# does not import this module), a file descriptor opened elsewhere, an open relative to a
# directory descriptor (dir_fd), hard links or renames of the OTHER protected files (review
# prose, recognised by name and directory only), a magnitude-bearing file replaced by a new inode
# after this process started, and code that deliberately rewrites __main__.__file__ AND enters
# the sanctioned context -- deliberately malicious code in the process, which no in-process guard
# can stop. It is DEFENCE IN DEPTH: the load-bearing protection is the execution chain, which
# refuses before the comparator's loader runs.
# ---------------------------------------------------------------------------------------------
READER_PROGRAMS = frozenset({"c11r_table.py", "c11r_compare.py"})
_SANCTIONED = {"depth": 0}
_PROTECTED_INODES: set[tuple[int, int]] = set()


def protect_inode(path) -> bool:
    """Register a file's (device, inode): a hard link to it, or the file renamed, is then judged
    protected like the file itself. Production registers the quarantine and the registry."""
    try:
        st = os.stat(path)
    except OSError:
        return False
    _PROTECTED_INODES.add((st.st_dev, st.st_ino))
    return True


def running_program() -> str:
    """For messages only: the program name as invoked."""
    return pathlib.PurePath(sys.argv[0]).name if sys.argv and sys.argv[0] else ""


def running_reader() -> str | None:
    """The reader this process IS, by the realpath of its __main__ module's file -- or None."""
    main_file = getattr(sys.modules.get("__main__"), "__file__", None)
    if not main_file:
        return None
    real = os.path.realpath(main_file)
    for name in sorted(READER_PROGRAMS):
        if real == os.path.realpath(HERE / name):
            return name
    return None


class sanctioned_protected_access:
    """The only context in which a protected file may be opened, and only by a reader program."""

    def __init__(self, reason: str):
        self.reason = reason

    def __enter__(self):
        if running_reader() is None:
            raise PermissionError(f"C11R runtime open-guard: {running_program() or 'this process'}"
                                  f" is not a sanctioned reader ({self.reason})")
        _SANCTIONED["depth"] += 1
        return self

    def __exit__(self, *exc):
        _SANCTIONED["depth"] -= 1
        return False


def guard_judges_protected(path: str) -> bool:
    """The path as given, as an absolute path, as its realpath (symlinks resolved), and -- for the
    magnitude-bearing files -- by the inode it names (hard links, renames)."""
    absolute = os.path.abspath(path)
    if any(is_protected(x) for x in (path, absolute, os.path.realpath(absolute))):
        return True
    if _PROTECTED_INODES:
        try:
            st = os.stat(path)
        except OSError:
            return False
        return (st.st_dev, st.st_ino) in _PROTECTED_INODES
    return False


def _open_guard(event, args):
    if event != "open" or not args:
        return
    path = args[0]
    if hasattr(path, "__fspath__"):
        path = os.fspath(path)                    # io.FileIO(pathlib.Path(...)) (N5-10)
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, str):
        return                                    # a file descriptor, not a path
    if guard_judges_protected(path) and not (
            _SANCTIONED["depth"] > 0 and running_reader() is not None):
        raise PermissionError(f"C11R runtime open-guard: {running_program() or 'this process'} "
                              f"may not open protected file {pathlib.PurePath(path).name}")


if not getattr(sys, "_c11r_open_guard_installed", False):
    protect_inode(NS / QUARANTINE_REL)                                   # the magnitude-bearing
    protect_inode(C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")  # files, by inode
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
    # --no-filters: the id of the RAW bytes (no clean filter or attribute can mask a change)
    r = subprocess.run(["git", "--no-replace-objects", "-C", str(path.parent), "hash-object",
                        "--no-filters", "--", str(path.resolve())], capture_output=True, text=True,
                       env=git_env())
    return "gitobj:" + r.stdout.strip() if r.returncode == 0 else None


def _rel(p: pathlib.Path) -> str:
    """Repository-relative name of a path: LEXICALLY first (a symlink inside the repository keeps
    its own name even when it resolves outside -- review 6, N6-5: resolving first raised
    ValueError inside verify_contract instead of producing a typed refusal), then resolved."""
    absolute = pathlib.Path(os.path.abspath(p))
    try:
        return str(absolute.relative_to(REPO))
    except ValueError:
        return str(absolute.resolve().relative_to(REPO))


# The kind of a directory entry, from lstat -- never following it (review 6, N6-5). Every
# load-bearing path check names one of these instead of raising.
PATH_KINDS = ("ABSENT", "FILE", "DIRECTORY", "SYMLINK_INSIDE", "SYMLINK_OUTSIDE",
              "SYMLINK_DANGLING", "SYMLINK_LOOP", "OTHER")


def path_kind(path, *, inside=None) -> str:
    """lstat-based kind of `path`. A symlink is classified by where it resolves: inside `inside`
    (default: the repository), outside it, dangling, or a loop."""
    import stat as _stat
    path = os.path.abspath(path)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return "ABSENT"
    except OSError:
        return "OTHER"
    if _stat.S_ISLNK(st.st_mode):
        try:
            os.stat(path)
        except FileNotFoundError:
            return "SYMLINK_DANGLING"
        except OSError:
            return "SYMLINK_LOOP"
        base = os.path.realpath(inside if inside is not None else REPO)
        real = os.path.realpath(path)
        return "SYMLINK_INSIDE" if real == base or real.startswith(base + os.sep) \
            else "SYMLINK_OUTSIDE"
    if _stat.S_ISREG(st.st_mode):
        return "FILE"
    if _stat.S_ISDIR(st.st_mode):
        return "DIRECTORY"
    return "OTHER"


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
    r = subprocess.run(["git", "--no-replace-objects", "-C", str(repo or REPO), "rev-parse",
                        "--verify", "--quiet", f"{commit}:{rel}"], capture_output=True, text=True,
                       env=git_env())
    return "gitobj:" + r.stdout.strip() if r.returncode == 0 else None


def _resolve_module(name: str) -> pathlib.Path | None:
    for d in CODE_DIRS:
        cand = d / f"{name}.py"
        if cand.is_file():                      # a directory named x.py is not source (N6-5)
            return cand
    return None


def code_closure(producer: pathlib.Path) -> dict[str, str]:
    """sha256 of the producer and of every campaign module it imports, transitively."""
    import ast
    seen: dict[str, str] = {}
    # lexical paths (review 6, N6-5): a module file that is a symlink keeps its in-repository name
    # here; the code-directory checks refuse the symlink itself, with a typed reason
    stack = [pathlib.Path(producer).absolute()]
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
                    stack.append(r.absolute())
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
