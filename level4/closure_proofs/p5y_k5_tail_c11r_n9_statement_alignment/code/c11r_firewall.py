"""C11R -- the original-value firewall, revision 4: a load-path dataflow HEURISTIC.

WHAT THIS IS, AND IS NOT (round 4; review round 3 N-1; erratum E29). This analysis is
DEFENSE_IN_DEPTH_HEURISTIC. It is NOT a proof that no leak path exists: the third reviewer planted
20 further leak paths (multi-argument Path, %-formatting, `python -c` children, higher-order and
aliased loaders or open, linecache, fileinput, urlopen, methods with path parameters, shell
substitution, ...) and revision 3 caught only 6. Those 20 are carried below as KNOWN-MISS probes
whose outcome is recorded, not asserted. FIREWALL_CLASS = PASS means exactly: every planted
positive control is flagged, no negative control is, and this analysis finds no violating read in
the campaign's code -- nothing more.

THE LOAD-BEARING PROTECTIONS are elsewhere, and this module does not replace them: the explicit
allowlists of production reads (common.ALLOWED_NS_INPUTS, load_allowlisted), the quarantine
architecture (two sanctioned readers), the RUNTIME open-guard in c11r_common (an audit hook that
refuses any Python-level open of a protected path outside the two readers -- exercised below), the
frozen execution contract with recomputed provenance, and the comparator refusing, before it
opens the quarantine, whenever the execution identity fails (c11r_compare.execute_comparison).

The six original magnitudes may enter this campaign at exactly two places: c11r_table.py, which
extracts them into the quarantine, and c11r_compare.py, which reads them only after the
independent outputs are sealed. Every other module must be unable to read them, or anything that
quotes them.

WHY REVISION 3 (review round 2, blocker B-2; erratum E14). Revision 2 reported PASS while the
status checker and B0 json-loaded whole directory trees that reached the quarantine and the
registry, and while the policy module parsed a review report that quotes original values. It
matched protected NAMES as substrings of literal strings, so a glob, a concatenation, an f-string,
a from-import, a function argument, a walrus, a git subprocess or a review file all went through.
The reviewer planted fourteen such paths; revision 2 caught five.

WHAT THIS SCANNER DOES. It follows every CONTENT READ -- open, read_text, read_bytes, Path.open,
C.load, C.blob_at, a git subprocess that prints content (show, cat-file, grep without -l, diff or
log without --name-only), any other subprocess or os.system command -- and resolves the PATH it
reads to a set of patterns, by constant folding (concatenation, f-strings, pathlib `/`, join,
format, containers, subscripts, module constants in other campaign modules) and by dataflow
(assignment, augmented assignment, walrus, for-loop and comprehension targets, container
append, function parameters, function returns, calls into other campaign modules by import,
from-import, importlib and getattr). A directory traversal (glob, rglob, iterdir, os.walk,
listdir, scandir) yields a wildcard pattern under its base.

Each resolved pattern is matched against the REAL file inventory (`git ls-files` of the closure
tree, names only, plus the files this campaign will create). A read is a VIOLATION when its
pattern can name:
  PROTECTED         a quarantine, registry, mixed-table, comparison or retired artifact, or any
                    review or adjudication report (common.is_protected);
  EXTERNAL          any non-Python file outside this namespace other than the declared R5 map;
  NS_OFF_ALLOWLIST  any file in this namespace outside common.ALLOWED_NS_INPUTS -- which
                    includes the runs artifact, so no pre-comparison module can read a
                    prospective cell 306 value either.
A pattern that is fully unknown matches every file and is therefore a violation: a production
module must read paths the analysis can resolve. A read whose path is a function PARAMETER is not
judged where it occurs; it is recorded in the function's summary and judged at every call site
with the argument substituted, across modules. A function that performs a PROTECTED read is a
FORBIDDEN READER (any violating read, directly or through a call); calling one from a non-reader
module is a violation.

Also flagged: traversal of any directory other than a code directory; dynamic code (exec, eval,
compile, runpy); a read of a magnitude-bearing KEY (load context only -- a store reads nothing);
a non-integer numeric literal inside the open-cell drift range [1.6208813, 2.0922830] (a
computation on cells 306-309 hard-coded in a production module); and a subprocess launch of the
comparator.

`common.content_free_id` is exempt: it asks `git hash-object` for an object id and no byte of the
file enters this process. That is the sanctioned way to verify a protected file is unchanged.

The scanner never reads a magnitude. The value-based leak check lives in c11r_table.py, the one
pre-comparison module that legitimately holds the values; this module checks artifacts
structurally (forbidden payload keys) and code by dataflow.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_schema as S

ALLOWED_READERS = frozenset({"c11r_table.py", "c11r_compare.py"})
# Calls to a sanctioned reader's functions that this analysis flags, exempted EXPLICITLY with the
# reason. c11r_chain.py drives the comparator's seal and chain checks on SYNTHETIC repositories;
# the analysis cannot see that its `repo` argument is a temporary repository, but a RUNTIME guard
# in c11r_compare (_real_repository_guard) raises unless the running program is the comparator
# itself whenever the repository is the real one, and c11r_chain exercises that guard.
EXEMPTED_CALLS = {"c11r_chain.py": ("c11r_compare.execute_comparison", "c11r_compare.verify_seal")}
# Whole functions exempted, with the reason: this module's runtime_open_guard_controls opens a
# PLANTED dummy file (written by a subprocess into a fresh temporary directory, with a protected
# NAME) precisely to prove the runtime guard refuses it; the analysis cannot see that the path is
# a temporary directory. The real quarantine is never touched.
#
# Round 5 (review round 4, N4-3): c11r_contract._pyc_matches_source reads a contract module's
# CACHED BYTECODE file and compiles the module's VERIFIED source bytes to compare the two code
# objects; the compiled object is compared, never executed. c11r_chain's IMP controls (c_IMP,
# its helpers one / forged_pyc, and _driver) launch subprocess DRIVERS from a fresh temporary
# directory that import campaign modules and call verify_loaded_modules; forged_pyc compiles a
# modified source only to WRITE a forged bytecode file into a temporary pycache prefix, which the
# driver subprocess then loads -- that is the attack the control demonstrates; stale_pyc does the
# same with a header the loader must REJECT (the no-false-refusal control IMP6b). The drivers read
# Python source only; the quarantine is never touched.
#
# Round 6 (review round 5, N5-2 and erratum E45): c11r_chain's CF controls (c_CF, _plant_file)
# write files with the PROTECTED NAME C11R_COMPARISON.json -- by a subprocess, into synthetic
# repositories and temporary directories only -- to prove that the comparator refuses a stale,
# modified, symlinked or earlier comparison file and that its writer creates the file exactly
# once; CF5b passes the comparator's PATH as an argument to a driver that simulates the reader's
# identity (the recorded residual) and writes into a temporary directory. The real comparison path
# is never touched and the comparator's main() is never launched.
EXEMPTED_FUNCTIONS = {"c11r_firewall.py": ("runtime_open_guard_controls",),
                      "c11r_contract.py": ("_pyc_matches_source",),
                      "c11r_chain.py": ("c_IMP", "one", "forged_pyc", "stale_pyc",
                                        "_driver", "c_CF", "_plant_file")}
FORBIDDEN_LAUNCH = ("c11r_compare.py",)
# Functions whose CALLS are not reads of campaign data: content_free_id hashes through a git
# subprocess (an id, never content); _pyc_matches_source reads only the cached BYTECODE of a
# module verify_loaded_modules has just shown to be a contract module at its contract path (round
# 5, N4-3), and its own body is exempted above with that reason.
EXEMPT_FUNCTIONS = frozenset({("c11r_common", "content_free_id"),
                              ("c11r_contract", "_pyc_matches_source")})
MAGNITUDE_KEYS = S.FORBIDDEN_PAYLOAD_KEYS
# the m=5 tail cells 305-309 span [1.6208813, 2.0922830] in drift. Written as integer numerators
# over 10**7 so that this checker does not itself carry a literal its own rule would flag.
OPEN_CELL_RANGE_E7 = (16208813, 20922830)
DRIFT_PRECISION_DENOMINATOR = 1000
VIOLATION_CLASSES = ("PROTECTED", "EXTERNAL", "NS_OFF_ALLOWLIST")

# files this campaign will create later; they are in no inventory yet but must be classified now
HYPOTHETICAL = (f"{C.NS_REL}/evidence/comparison/C11R_COMPARISON.json",
                f"{C.NS_REL}/config/C11R_CONTRACT.json",
                f"{C.NS_REL}/evidence/chain/C11R_CHAIN_CONTROLS.json",
                f"{C.NS_REL}/evidence/procs/C11R_PROCESS_DETECTOR.json",
                f"{C.NS_REL}/evidence/runs/C11R_RUNS.json",
                f"{C.NS_REL}/review/REVIEW_C11R_PREFREEZE_R3.md",
                f"{C.NS_REL}/review/REVIEW_C11R_PREFREEZE_R5.md",
                f"{C.NS_REL}/review/ADJUDICATION_C11R.md",
                f"{C.NS_REL}/config/C11R_AUTHORIZATION.json",
                f"{C.NS_REL}/config/C11R_EXECUTION_PERMISSION.json",
                f"{C.NS_REL}/evidence/qualification/C11R_QUALIFICATION.json")

W = ("W",)                     # a wildcard: any string

MAXPAT = 48
SAFE_COMMANDS = frozenset({"ps", "lsof", "sysctl", "uname", "hostname", "sw_vers", "nproc",
                           "uptime", "date", "whoami", "id"})
GIT_CONTENT = frozenset({"show", "cat-file", "grep", "diff", "log", "blame", "archive",
                         "format-patch", "stash"})
GIT_NAME_ONLY_FLAGS = frozenset({"--name-only", "--name-status", "--stat", "--numstat", "-l",
                                 "-L", "-c", "--count", "--files-with-matches",
                                 "--files-without-match", "-q", "--quiet", "--exit-code"})
TRAVERSAL_ATTRS = frozenset({"glob", "rglob", "iterdir", "walk"})
TRAVERSAL_FUNCS = {("os", "walk"), ("os", "listdir"), ("os", "scandir"), ("glob", "glob"),
                   ("glob", "iglob")}
SUBPROCESS_FUNCS = frozenset({"run", "Popen", "check_output", "call", "check_call",
                              "getoutput", "getstatusoutput"})


def P(name):
    return ("P", name)


def _is_item_str(x):
    return isinstance(x, str)


def _norm(p: tuple) -> tuple:
    out = []
    for x in p:
        if isinstance(x, tuple) and len(x) == 2 and x[0] == "SFX":
            # Path.with_suffix(s): replace the last suffix of the preceding literal, if resolved
            if out and isinstance(out[-1], str):
                head, sep, tail = out[-1].rpartition("/")
                if "." in tail:
                    tail = tail.rsplit(".", 1)[0]
                out[-1] = head + sep + tail + x[1]
                continue
            if out and isinstance(out[-1], tuple) and out[-1] and out[-1][0] == "P":
                out.append(x)                            # resolved after substitution
                continue
            out.append(x[1])                             # after a wildcard: W + suffix
            continue
        if isinstance(x, str):
            if x == "":
                continue
            if out and isinstance(out[-1], str):
                out[-1] = out[-1] + x
                continue
        elif x == W and out and out[-1] == W:
            continue
        out.append(x)
    return tuple(out)


def _uniq(ps):
    seen, out = set(), []
    for p in ps:
        p = _norm(p)
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out if len(out) <= MAXPAT else [(W,)]


def _cat(a, b, sep=""):
    out = []
    for x in a:
        for y in b:
            out.append(x + ((sep,) if sep else ()) + y)
    return _uniq(out)


def _params_in(p) -> set[str]:
    return {x[1] for x in p if isinstance(x, tuple) and x[0] == "P"}


def _subst(p: tuple, binding: dict[str, list]) -> list[tuple]:
    """Replace parameter markers by the argument patterns bound at a call site."""
    outs = [()]
    for x in p:
        if isinstance(x, tuple) and x[0] == "P":
            alts = binding.get(x[1], [(W,)])
            outs = [o + a for o in outs for a in alts]
        else:
            outs = [o + (x,) for o in outs]
        if len(outs) > MAXPAT:
            return [(W,)]
    return _uniq(outs)


def _render(p: tuple) -> str:
    return "".join(x if isinstance(x, str) else (x[1] if isinstance(x, tuple) and len(x) == 2
                                                  and x[0] == "SFX" else "\x00") for x in p)


# ---------------------------------------------------------------------------------------------
# the file inventory, classified. Names only: `git ls-files` never returns content.
# ---------------------------------------------------------------------------------------------
def classify_file(rel: str) -> str:
    if C.is_protected(rel):
        return "PROTECTED"
    if rel.endswith(".py"):
        return "CODE"
    if rel in C.DECLARED_EXTERNAL_INPUTS:
        return "DECLARED_EXTERNAL"
    if rel.startswith(C.NS_REL + "/"):
        return "ALLOWLISTED" if rel[len(C.NS_REL) + 1:] in C.ALLOWED_NS_INPUTS \
            else "NS_OFF_ALLOWLIST"
    return "EXTERNAL"


_INVENTORY: dict[str, str] | None = None


def inventory() -> dict[str, str]:
    global _INVENTORY
    if _INVENTORY is None:
        names = set(C.git("ls-files", "level4/closure_proofs").splitlines())
        names |= set(C.git("ls-files", "--others", "--exclude-standard", C.NS_REL).splitlines())
        # every name this namespace EVER held (names only), so a blob read of a deleted artifact --
        # the revision-1 mixed table, the retired screen -- is still classified
        # --full-history -m: no merge simplification (review 4, R4-1), so a name that existed
        # only on a merged side branch is still listed
        names |= set(C.git("log", "--all", "--full-history", "-m", "--name-only",
                           "--pretty=format:", "--", C.NS_REL).splitlines())
        names |= set(HYPOTHETICAL)
        _INVENTORY = {n: classify_file(n) for n in names if n and "__pycache__" not in n}
    return _INVENTORY


_MATCH_CACHE: dict[str, dict] = {}


def _canon(s: str) -> str:
    s = s.replace("<NS>", C.NS_REL).replace("<CLOSURE>", "level4/closure_proofs")
    s = s.replace("<REPO>/", "").replace("<REPO>", "")
    # a git revision prefix "HEAD:path" or "<sha>:path" names the path
    m = re.match(r"^[^/:]*:(?!\()(.*)$", s)
    if m and not s.startswith(":"):
        s = m.group(1)
    # a leading wildcard DIRECTORY (an unknown repository root: `repo / NS_REL / rel`) stands for
    # any prefix, including none; the match is anchored at a path boundary anyway (erratum E31 --
    # without this, repository-parameterised reads resolved to no file and passed vacuously)
    while s.startswith("\x00/"):
        s = s[2:]
    return s


def classify_pattern(p: tuple) -> dict:
    """Which inventory files can this read-path pattern name, by class."""
    s = _canon(_render(p))
    if s in _MATCH_CACHE:
        return _MATCH_CACHE[s]
    rx = re.compile("(?:^|/)" + "".join(".*" if ch == "\x00" else re.escape(ch) for ch in s)
                    + "$", re.S)
    by: dict[str, list[str]] = {}
    for rel, cls in inventory().items():
        if rx.search(rel):
            by.setdefault(cls, []).append(rel)
    bad = [c for c in VIOLATION_CLASSES if c in by]
    r = {"pattern": s.replace("\x00", "*"), "classes": {k: len(v) for k, v in sorted(by.items())},
         "examples": {k: sorted(v)[:3] for k, v in sorted(by.items()) if k in VIOLATION_CLASSES},
         "violation": bad}
    _MATCH_CACHE[s] = r
    return r


# ---------------------------------------------------------------------------------------------
# per-module analysis
# ---------------------------------------------------------------------------------------------
ROOT_MARKERS = {("c11r_common", "HERE"): "<NS>/code", ("c11r_common", "NS"): "<NS>",
                ("c11r_common", "CLOSURE"): "<CLOSURE>", ("c11r_common", "REPO"): "<REPO>"}


class Module:
    def __init__(self, stem: str, src: str, world: "World", selfpath: str | None = None):
        self.stem, self.world = stem, world
        self.tree = ast.parse(src)
        self.selfpath = selfpath or f"<NS>/code/{stem}.py"
        self.aliases: dict[str, str] = {}        # local name -> module stem
        self.from_imports: dict[str, tuple[str, str]] = {}
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.aliases[a.asname or a.name.split(".")[0]] = a.name.split(".")[0]
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                for a in n.names:
                    self.from_imports[a.asname or a.name] = (n.module.split(".")[0], a.name)
        # importlib / __import__ aliases: K = importlib.import_module("m")
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                mod = self._dynamic_import(n.value)
                if mod:
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            self.aliases[t.id] = mod
        self.funcs = {n.name: n for n in self.tree.body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.nested = {n.name: n for n in ast.walk(self.tree)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        # the enclosing function of each nested function, for closure variables
        self.parent_fn: dict[int, ast.AST] = {}
        for outer in ast.walk(self.tree):
            if isinstance(outer, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(outer):
                    if inner is not outer and isinstance(inner, (ast.FunctionDef,
                                                                 ast.AsyncFunctionDef)):
                        cur = self.parent_fn.get(id(inner))
                        # keep the NEAREST enclosing function
                        if cur is None or any(x is outer for x in ast.walk(cur)):
                            self.parent_fn[id(inner)] = outer
        self.module_env: dict[str, list] = {}
        self.module_assign = {t.id: st.value for st in self.tree.body if isinstance(st, ast.Assign)
                              for t in st.targets if isinstance(t, ast.Name)}
        # summaries: func -> {"sinks": [(kind, payload)], "returns": [patterns], "params": [...]}
        self.summary: dict[str, dict] = {}

    # -- import helpers -----------------------------------------------------------------------
    @staticmethod
    def _dynamic_import(call: ast.Call) -> str | None:
        f = call.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
        if name in ("import_module", "__import__") and call.args and isinstance(
                call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
            return call.args[0].value.split(".")[0]
        return None

    def callee(self, call: ast.Call) -> tuple[str, str] | None:
        """(module stem, function name) for a call into a campaign or local function."""
        f = call.func
        if isinstance(f, ast.Name):
            if f.id in self.nested:
                return (self.stem, f.id)
            if f.id in self.from_imports:
                return self.from_imports[f.id]
            return None
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and \
                f.value.id in self.aliases:
            return (self.aliases[f.value.id], f.attr)
        if isinstance(f, ast.Call) and isinstance(f.func, ast.Name) and f.func.id == "getattr" \
                and len(f.args) >= 2 and isinstance(f.args[0], ast.Name) and \
                f.args[0].id in self.aliases and isinstance(f.args[1], ast.Constant):
            return (self.aliases[f.args[0].id], str(f.args[1].value))
        return None

    # -- folding ------------------------------------------------------------------------------
    def is_seq(self, n) -> bool:
        """Is this expression a sequence (tuple, list), so that `+` concatenates SEQUENCES?"""
        if isinstance(n, (ast.Tuple, ast.List, ast.ListComp)):
            return True
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            return self.is_seq(n.left) or self.is_seq(n.right)
        if isinstance(n, ast.Name):
            v = self.module_assign.get(n.id)
            return v is not None and self.is_seq(v)
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and \
                n.value.id in self.aliases:
            other = self.world.mods.get(self.aliases[n.value.id])
            v = other.module_assign.get(n.attr) if other else None
            return v is not None and other.is_seq(v)
        return False

    def fold(self, n, env) -> list[tuple]:
        if n is None:
            return [(W,)]
        if isinstance(n, ast.Constant):
            if isinstance(n.value, str):
                return [(n.value,)]
            return [] if n.value is None else [(W,)]
        if isinstance(n, ast.JoinedStr):
            outs = [()]
            for v in n.values:
                alts = self.fold(v.value, env) if isinstance(v, ast.FormattedValue) else \
                    self.fold(v, env)
                if isinstance(v, ast.FormattedValue) and v.format_spec is not None:
                    alts = [(W,)]
                outs = _cat(outs, alts)
            return outs
        if isinstance(n, ast.BinOp):
            a, b = self.fold(n.left, env), self.fold(n.right, env)
            if isinstance(n.op, ast.Div):
                return _cat(a, b, "/")
            if isinstance(n.op, ast.Add):
                if self.is_seq(n.left) or self.is_seq(n.right):
                    return _uniq(a + b)                  # tuple + tuple: the union of elements
                return _cat(a, b)
            if isinstance(n.op, ast.Mod):
                return _cat(a, [(W,)])
            return [(W,)]
        if isinstance(n, ast.Name):
            if n.id == "__file__":
                return [(self.selfpath,)]
            if n.id in env:
                return env[n.id]
            if n.id in self.module_env:
                return self.module_env[n.id]
            if n.id in self.from_imports:
                mod, attr = self.from_imports[n.id]
                return self.world.module_constant(mod, attr)
            return [(W,)]
        if isinstance(n, ast.Attribute):
            if isinstance(n.value, ast.Name) and n.value.id in self.aliases:
                return self.world.module_constant(self.aliases[n.value.id], n.attr)
            base = self.fold(n.value, env)
            if n.attr == "parent":
                return _uniq([_parent(p) for p in base])
            if n.attr in ("name", "stem", "suffix"):
                return [(W,)]
            return base
        if isinstance(n, (ast.List, ast.Tuple, ast.Set)):
            out = []
            for e in n.elts:
                out += self.fold(e.value if isinstance(e, ast.Starred) else e, env)
            return _uniq(out) if out else [(W,)]
        if isinstance(n, ast.Dict):
            out = []
            for v in n.values:
                out += self.fold(v, env)
            return _uniq(out) if out else [(W,)]
        if isinstance(n, ast.Subscript):
            return self.fold(n.value, env)
        if isinstance(n, ast.IfExp):
            return _uniq(self.fold(n.body, env) + self.fold(n.orelse, env))
        if isinstance(n, ast.BoolOp):
            out = []
            for v in n.values:
                out += self.fold(v, env)
            return _uniq(out)
        if isinstance(n, ast.NamedExpr):
            return self.fold(n.value, env)
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            env2 = dict(env)
            for g in n.generators:
                self.bind_target(g.target, self.iter_elems(g.iter, env2), env2)
            return self.fold(n.elt, env2)
        if isinstance(n, ast.Call):
            return self.fold_call(n, env)
        return [(W,)]

    def fold_call(self, n: ast.Call, env) -> list[tuple]:
        f = n.func
        attr = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
        if attr in ("Path", "PurePath", "PurePosixPath", "str", "fspath", "sorted", "list",
                    "tuple", "set", "reversed", "frozenset") and n.args:
            return self.fold(n.args[0], env)
        if attr == "join" and isinstance(f, ast.Attribute):
            recv = f.value
            if isinstance(recv, ast.Attribute) and recv.attr == "path":        # os.path.join
                outs = self.fold(n.args[0], env) if n.args else [(W,)]
                for a in n.args[1:]:
                    outs = _cat(outs, self.fold(a, env), "/")
                return outs
            if isinstance(recv, ast.Constant) and isinstance(recv.value, str) and n.args:
                arg = n.args[0]
                if isinstance(arg, (ast.List, ast.Tuple)):
                    outs = [()]
                    for i, e in enumerate(arg.elts):
                        outs = _cat(outs, self.fold(e, env), recv.value if i else "")
                    return outs
                return _cat(self.fold(arg, env), [(W,)])
        if attr == "joinpath" and isinstance(f, ast.Attribute):
            outs = self.fold(f.value, env)
            for a in n.args:
                outs = _cat(outs, self.fold(a, env), "/")
            return outs
        if attr in ("resolve", "absolute", "expanduser", "relative_to", "as_posix") and \
                isinstance(f, ast.Attribute):
            return self.fold(f.value, env)
        if attr == "format" and isinstance(f, ast.Attribute):
            return [_norm(tuple(x if not isinstance(x, str) else x for x in _fmt(p)))
                    for p in self.fold(f.value, env)]
        if attr in ("pop", "values", "copy") and isinstance(f, ast.Attribute):
            return self.fold(f.value, env)
        if attr == "with_suffix" and isinstance(f, ast.Attribute) and n.args and isinstance(
                n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            return _uniq([p + (("SFX", n.args[0].value),) for p in self.fold(f.value, env)])
        if attr == "with_suffix" and isinstance(f, ast.Attribute):
            return _cat([_strip_suffix(p) for p in self.fold(f.value, env)], [(W,)])
        if attr in TRAVERSAL_ATTRS and isinstance(f, ast.Attribute) and not (
                isinstance(f.value, ast.Name) and f.value.id in self.aliases):
            return self.traversal_children(self.fold(f.value, env), n, attr)
        cal = self.callee(n)
        if cal is not None:
            summ = self.world.summary_of(*cal)
            if summ is not None and summ["returns"]:
                return _uniq([q for p in summ["returns"]
                              for q in _subst(p, self.bind_args(summ, n, env))])
        return [(W,)]

    def traversal_children(self, base, n: ast.Call, attr: str) -> list[tuple]:
        pat = n.args[0].value if n.args and isinstance(n.args[0], ast.Constant) and \
            isinstance(n.args[0].value, str) else "*"
        tail = tuple(x if x != "*" else W for x in re.split(r"(\*)", pat.replace("**/", "*"))
                     if x) if attr in ("glob", "rglob") else (W,)
        mid = ("/", W) if attr == "rglob" else ("/",)
        return _uniq([b + mid + tail for b in base])

    def iter_elems(self, it, env) -> list[tuple]:
        if isinstance(it, ast.Call):
            f = it.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nm in ("enumerate", "zip", "items"):
                return [(W,)]
        return self.fold(it, env)

    def bind_target(self, t, pats, env, replace=False):
        if isinstance(t, ast.Name):
            env[t.id] = _uniq(pats) if replace else _uniq(env.get(t.id, []) + pats)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self.bind_target(e, [(W,)], env, replace)
        elif isinstance(t, ast.Starred):
            self.bind_target(t.value, pats, env, replace)

    def bind_args(self, summ: dict, call: ast.Call, env) -> dict[str, list]:
        b: dict[str, list] = dict(summ.get("defaults", {}))       # an omitted argument
        params, vararg = summ["params"], summ["vararg"]
        pos = [a for a in call.args if not isinstance(a, ast.Starred)]
        for i, a in enumerate(pos):
            if i < len(params):
                b[params[i]] = self.fold(a, env)
        if vararg:
            b[vararg] = [(W,)]
        for k in call.keywords:
            if k.arg:
                b[k.arg] = self.fold(k.value, env)
        return b

    def varargs_of(self, summ: dict, call: ast.Call, env) -> list[list[tuple]]:
        n = len(summ["params"])
        rest = [a for a in call.args if not isinstance(a, ast.Starred)][n:]
        return [self.fold(a, env) for a in rest]

    # -- environments -------------------------------------------------------------------------
    def fn_env(self, fn, penv: dict[str, list]) -> dict:
        """A function's environment: its enclosing function's (closure variables; the enclosing
        function's own parameters are unknown here, so W), then its own bindings."""
        parent = self.parent_fn.get(id(fn))
        base = {}
        if parent is not None:
            a = parent.args
            pparams = {x.arg: [(W,)] for x in a.posonlyargs + a.args + a.kwonlyargs}
            base = self.fn_env(parent, pparams)
        return self.build_env(fn, penv, base=base)

    def build_env(self, body_owner, params: dict[str, list] | None = None,
                  base: dict | None = None) -> dict:
        env: dict[str, list] = dict(base or {})
        env.update(params or {})
        for _ in range(6):
            before = {k: list(v) for k, v in env.items()}
            for n in ast.walk(body_owner):
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, (ast.Tuple, ast.List)) and isinstance(
                                n.value, (ast.Tuple, ast.List)) and len(t.elts) == len(
                                n.value.elts):
                            for te, ve in zip(t.elts, n.value.elts):     # a, b = x, y
                                self.bind_target(te, self.fold(ve, env), env)
                        else:
                            self.bind_target(t, self.fold(n.value, env), env)
                elif isinstance(n, ast.AnnAssign) and n.value is not None:
                    self.bind_target(n.target, self.fold(n.value, env), env)
                elif isinstance(n, ast.AugAssign):
                    self.bind_target(n.target, _cat(self.fold(n.target, env) if isinstance(
                        n.target, ast.Name) and n.target.id in env else [(W,)],
                        self.fold(n.value, env)), env)
                elif isinstance(n, ast.NamedExpr):
                    self.bind_target(n.target, self.fold(n.value, env), env)
                elif isinstance(n, (ast.For, ast.AsyncFor)):
                    self.bind_target(n.target, self.iter_elems(n.iter, env), env)
                elif isinstance(n, (ast.With, ast.AsyncWith)):
                    for it in n.items:
                        if it.optional_vars is not None:
                            self.bind_target(it.optional_vars, [(W,)], env)
                elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and \
                        n.func.attr in ("append", "add", "extend", "insert", "update") and \
                        isinstance(n.func.value, ast.Name):
                    arg = n.args[-1] if n.args else None
                    self.bind_target(n.func.value, self.fold(arg, env), env)
            if {k: list(v) for k, v in env.items()} == before:
                break
        return env

    # -- sinks --------------------------------------------------------------------------------
    def sinks_in(self, owner, env) -> list[dict]:
        """Every content read, traversal, launch and call-with-summary inside `owner`."""
        out = []

        def visit(node, env_):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue                          # analysed as its own function
                if isinstance(child, (ast.ListComp, ast.SetComp, ast.GeneratorExp,
                                      ast.DictComp)):
                    # a comprehension has its own scope: bind its targets in a child env
                    env2 = dict(env_)
                    for g in child.generators:
                        visit_expr(g.iter, env2)
                        # the target SHADOWS any same-named variable outside
                        self.bind_target(g.target, self.iter_elems(g.iter, env2), env2,
                                         replace=True)
                        for cond in g.ifs:
                            visit_expr(cond, env2)
                    for part in ((child.key, child.value) if isinstance(child, ast.DictComp)
                                 else (child.elt,)):
                        visit_expr(part, env2)
                    continue
                visit_expr(child, env_)

        def visit_expr(node, env_):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                holder = ast.Expr(value=node)
                visit(holder, env_)
                return
            if isinstance(node, ast.Call):
                out.extend(self.sinks_of_call(node, env_))
            visit(node, env_)
        visit(owner, env)
        return out

    def sinks_of_call(self, n: ast.Call, env) -> list[dict]:
        f = n.func
        line = n.lineno
        src = ast.unparse(n)[:140]
        base = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None
        base_mod = self.aliases.get(base) if base else None
        attr = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
        if isinstance(f, ast.Name) and f.id in self.from_imports and \
                self.from_imports[f.id][0] not in self.world.mods:
            base_mod, attr = self.from_imports[f.id]      # `from subprocess import run`
        out = []
        cal = self.callee(n)
        if cal in EXEMPT_FUNCTIONS:
            return []
        if (attr in ("exec", "eval", "compile") and isinstance(f, ast.Name)
                and base_mod is None) or base_mod == "runpy":
            out.append({"kind": "dynamic_code", "line": line, "call": src})
            return out
        if isinstance(f, ast.Name) and attr == "open" and base_mod is None:
            out.append({"kind": "read", "line": line, "call": src,
                        "patterns": self.fold(n.args[0] if n.args else None, env)})
        elif isinstance(f, ast.Attribute) and attr in ("read_text", "read_bytes"):
            out.append({"kind": "read", "line": line, "call": src,
                        "patterns": self.fold(f.value, env)})
        elif isinstance(f, ast.Attribute) and attr == "open":
            if base_mod in ("io", "codecs", "os", "gzip", "bz2", "lzma", "tarfile", "zipfile"):
                pats = self.fold(n.args[0] if n.args else None, env)
            else:
                pats = self.fold(f.value, env)
            out.append({"kind": "read", "line": line, "call": src, "patterns": pats})
        elif base_mod in ("numpy", "np", "shutil") and attr in ("load", "loadtxt", "genfromtxt",
                                                                 "copy", "copyfile", "copy2"):
            out.append({"kind": "read", "line": line, "call": src,
                        "patterns": self.fold(n.args[0] if n.args else None, env)})
        elif base_mod == "subprocess" and attr in SUBPROCESS_FUNCS or \
                (base_mod == "os" and attr in ("system", "popen")):
            out.append({"kind": "argv", "line": line, "call": src,
                        "argv": self.fold_argv(n.args[0] if n.args else None, env)})
        elif (base_mod, attr) in TRAVERSAL_FUNCS:
            out.append({"kind": "traversal", "line": line, "call": src,
                        "patterns": self.fold(n.args[0] if n.args else None, env)})
        elif isinstance(f, ast.Attribute) and attr in TRAVERSAL_ATTRS and base_mod is None:
            out.append({"kind": "traversal", "line": line, "call": src,
                        "patterns": self.fold(f.value, env)})
        if cal is not None and cal != (self.stem, None):
            summ = self.world.summary_of(*cal)
            if summ is not None:
                out.append({"kind": "call", "line": line, "call": src, "callee": cal,
                            "binding": self.bind_args(summ, n, env),
                            "varargs": self.varargs_of(summ, n, env)})
        return out

    def fold_argv(self, a, env) -> list[list[tuple]]:
        if isinstance(a, (ast.List, ast.Tuple)):
            argv = []
            for e in a.elts:
                if isinstance(e, ast.Starred):
                    pats = self.fold(e.value, env)
                    if any(_params_in(q) for q in pats):
                        argv.append([("STAR", tuple(pats))])     # *args, expanded at call sites
                    else:
                        argv.append(pats)
                else:
                    argv.append(self.fold(e, env))
            return argv
        # a shell string: split on spaces where the constant parts allow it
        pats = self.fold(a, env)
        argv = []
        for p in pats[:1]:
            cur = []
            for x in p:
                if isinstance(x, str):
                    parts = x.split(" ")
                    for i, s in enumerate(parts):
                        if i:
                            argv.append([_norm(tuple(cur))] if cur else [(W,)])
                            cur = []
                        if s:
                            cur.append(s)
                else:
                    cur.append(x)
            if cur:
                argv.append([_norm(tuple(cur))])
        return argv or [[(W,)]]


def _is_star(p) -> bool:
    return isinstance(p, tuple) and len(p) == 2 and p[0] == "STAR"


def _strip_suffix(p: tuple) -> tuple:
    """Path.with_suffix drops the last suffix of the last literal; a trailing wildcard stays."""
    if p and isinstance(p[-1], str):
        head, sep, tail = p[-1].rpartition("/")
        if "." in tail:
            tail = tail.rsplit(".", 1)[0]
        return p[:-1] + ((head + sep + tail),)
    return p


def _fmt(p: tuple) -> tuple:
    out = []
    for x in p:
        if isinstance(x, str):
            for i, s in enumerate(re.split(r"\{[^{}]*\}", x)):
                if i:
                    out.append(W)
                out.append(s)
        else:
            out.append(x)
    return tuple(out)


def _parent(p: tuple) -> tuple:
    if p and isinstance(p[-1], str) and "/" in p[-1]:
        head = p[-1].rsplit("/", 1)[0]
        return p[:-1] + ((head,) if head else ())
    if p == ("<NS>",):
        return ("<CLOSURE>",)
    if p == ("<NS>/code",):
        return ("<NS>",)
    return p[:-1] + (W,) if p else (W,)


# ---------------------------------------------------------------------------------------------
# the world: every module in scope, their constants, their function summaries
# ---------------------------------------------------------------------------------------------
class World:
    def __init__(self):
        self.mods: dict[str, Module] = {}
        self._const_cache: dict[tuple, list] = {}

    def add(self, stem, src, selfpath=None):
        m = Module(stem, src, self, selfpath)
        self.mods[stem] = m
        return m

    def module_constant(self, mod: str, attr: str) -> list[tuple]:
        if (mod, attr) in ROOT_MARKERS:
            return [(ROOT_MARKERS[(mod, attr)],)]
        m = self.mods.get(mod)
        if m is None:
            return [(W,)]
        if attr == "__file__":
            return [(m.selfpath,)]                    # another campaign module's own source
        if attr in m.module_env:
            return m.module_env[attr]
        return [(W,)]

    def summary_of(self, mod: str, fn: str) -> dict | None:
        if (mod, fn) in EXEMPT_FUNCTIONS:
            return None
        m = self.mods.get(mod)
        if m is None or fn not in m.nested:
            return None
        return m.summary.get(fn)

    def solve(self, rounds: int = 8):
        for m in self.mods.values():
            m.module_env = {}
        for _ in range(3):
            for m in self.mods.values():
                m.module_env = m.build_env(ast.Module(body=[s for s in m.tree.body if not
                                                            isinstance(s, (ast.FunctionDef,
                                                                           ast.AsyncFunctionDef,
                                                                           ast.ClassDef))],
                                                      type_ignores=[]))
        for m in self.mods.values():
            for name, fn in m.nested.items():
                a = fn.args
                params = [x.arg for x in a.posonlyargs + a.args] + [x.arg for x in a.kwonlyargs]
                m.summary[name] = {"params": params,
                                   "vararg": a.vararg.arg if a.vararg else None,
                                   "defaults": _defaults(m, fn),
                                   "sinks": [], "returns": [], "loader": False}
        for _ in range(rounds):
            changed = False
            for m in self.mods.values():
                for name, fn in m.nested.items():
                    summ = m.summary[name]
                    penv = {p: [(P(p),)] for p in summ["params"]}
                    if summ["vararg"]:
                        penv[summ["vararg"]] = [(P(summ["vararg"]),)]
                    env = m.fn_env(fn, penv)
                    rets = []
                    for n in ast.walk(fn):
                        if isinstance(n, ast.Return) and n.value is not None:
                            rets += m.fold(n.value, env)
                    rets = _uniq(rets) if rets else []
                    sinks = m.sinks_in(fn, env)
                    judged = judge(self, m, sinks)
                    param_sinks = [j for j in judged if j.get("deferred")]
                    loader = _is_loader([j for j in judged if not _exempted(
                        m.stem + ".py", {"function": name, "why": j.get("violation", []),
                                         "call": j.get("call", "")})])
                    new = {"returns": rets, "param_sinks": param_sinks, "loader": loader}
                    old = {k: summ.get(k) for k in new}
                    if repr(new) != repr(old):
                        summ.update(new)
                        changed = True
            if not changed:
                break


def _defaults(m: "Module", fn) -> dict[str, list]:
    """Patterns of parameter DEFAULTS, bound at a call site that omits the argument."""
    a = fn.args
    pos = a.posonlyargs + a.args
    out = {}
    for arg, d in zip(pos[len(pos) - len(a.defaults):], a.defaults):
        out[arg.arg] = m.fold(d, m.module_env)
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        if d is not None:
            out[arg.arg] = m.fold(d, m.module_env)
    return out


def _code_dir(p: tuple) -> bool:
    s = _canon(_render(p))
    return "\x00" not in s and (s.endswith("/code") or s == "code")


def _classify_argv(argv: list[list[tuple]]) -> dict:
    """Judge one subprocess argv (each element a list of alternative patterns)."""
    def lit(i):
        if i >= len(argv):
            return None
        alts = argv[i]
        if len(alts) == 1 and len(alts[0]) == 1 and isinstance(alts[0][0], str):
            return alts[0][0]
        return None

    def may_launch_comparator() -> bool:
        # any ALTERNATIVE of any argument that can end in the comparator's file name
        for alts in argv[1:]:
            for p in alts:
                if _is_star(p):
                    return True               # an unknown *args could name the comparator
                if not p:
                    continue
                tail = p[-1]
                if not isinstance(tail, str):
                    continue
                if any(tail.endswith(t) for t in FORBIDDEN_LAUNCH):
                    return True
        return False

    prog = lit(0)
    if prog is None:
        # sys.executable or unknown program: look for a launched script
        scripts = [lit(i) for i in range(1, len(argv))]
        if may_launch_comparator():
            return {"violation": ["LAUNCHES_COMPARATOR"], "reads": []}
        if any(s and s.endswith(".py") for s in scripts):
            return {"violation": [], "reads": [], "launch": [s for s in scripts if s]}
        return {"violation": [], "reads": [a for alts in argv[1:] for a in alts]}
    prog_name = prog.rsplit("/", 1)[-1]
    if prog_name in SAFE_COMMANDS:
        return {"violation": [], "reads": []}
    if prog_name.startswith("python"):
        if may_launch_comparator():
            return {"violation": ["LAUNCHES_COMPARATOR"], "reads": []}
        return {"violation": [], "reads": []}
    if prog_name == "git":
        return _classify_git([lit(i) for i in range(1, len(argv))], argv[1:])
    return {"violation": [], "reads": [a for alts in argv[1:] for a in alts]}


def _classify_git(lits: list, alts: list) -> dict:
    i = 0
    while i < len(lits) and lits[i] in ("-C", "-c", "--git-dir", "--work-tree",
                                        "--no-replace-objects", "--no-pager"):
        i += 1 if lits[i] in ("--no-replace-objects", "--no-pager") else 2
    if i >= len(lits):
        return {"violation": [], "reads": [], "unresolved_git": True}
    sub = lits[i]
    if sub is None:
        return {"violation": [], "reads": [p for a in alts[i:] for p in a],
                "unresolved_git": True}
    if sub not in GIT_CONTENT:
        return {"violation": [], "reads": []}
    rest_l, rest_a = lits[i + 1:], alts[i + 1:]
    if any(x in GIT_NAME_ONLY_FLAGS for x in rest_l if x):
        return {"violation": [], "reads": []}
    # `git log --format=...` prints only what the format names: hashes and dates are names;
    # %B, %s, %b and friends print commit MESSAGES, which are content
    if sub == "log" and "-p" not in rest_l and "--patch" not in rest_l:
        fmts = [x.split("=", 1)[1] for x in rest_l if x and (x.startswith("--format=")
                                                            or x.startswith("--pretty="))]
        if fmts and all(re.fullmatch(r"(%(H|h|T|t|P|p|ct|ci|cI|at|ai|aI)|[^%])*", f)
                        for f in fmts):
            return {"violation": [], "reads": []}
        return {"violation": ["READS_COMMIT_MESSAGES"], "reads": []}
    reads = []
    for x, a in zip(rest_l, rest_a):
        if x is not None and (x.startswith("-") or x.startswith(":!") or
                              x.startswith(":(exclude)") or x.startswith(":^")):
            continue
        reads += a
    # a git BLOB of a data artifact is a HISTORICAL version: the leak check scans only the current
    # one (revision 2 of the errata restated original values), so any blob read of a non-code
    # file in this namespace is refused, whatever the commit
    return {"violation": [], "reads": reads, "blob": sub in ("show", "cat-file")}


def judge(world: World, m: Module, sinks: list[dict]) -> list[dict]:
    """Resolve each sink. Returns rows with `violation` (list) or `deferred` (param sink)."""
    rows = []
    for s in sinks:
        k = s["kind"]
        if k == "dynamic_code":
            rows.append({**s, "violation": ["DYNAMIC_CODE"]})
        elif k == "traversal":
            bad = [p for p in s["patterns"] if not _code_dir(p) and not _params_in(p)]
            deferred = [p for p in s["patterns"] if _params_in(p)]
            rows.append({**s, "violation": ["TRAVERSAL_OF_NON_CODE_DIR"] if bad else [],
                         "deferred": bool(deferred), "sink_patterns": deferred,
                         "resolved": [_canon(_render(p)).replace("\x00", "*") for p in
                                      s["patterns"]]})
        elif k == "read":
            rows.append(judge_reads(s, s["patterns"]))
        elif k == "argv":
            star = [p for alts in s["argv"] for p in alts if _is_star(p)]
            has_param = any(_params_in(p) for alts in s["argv"] for p in alts if not _is_star(p))
            if star or has_param:
                rows.append({**s, "violation": [], "deferred": True, "argv_template": s["argv"]})
                continue
            c = _classify_argv(s["argv"])
            r = judge_reads(s, c["reads"]) if c["reads"] else {**s, "violation": []}
            r["violation"] = sorted(set(r.get("violation", [])) | set(c["violation"])
                                    | _blob_violation(c, r))
            rows.append(r)
        elif k == "call":
            summ = world.summary_of(*s["callee"])
            if summ is None:
                continue
            viol = ["CALLS_A_FORBIDDEN_READER"] if summ.get("loader") else []
            details = []
            for ps in summ.get("param_sinks", []):
                if ps["kind"] in ("read", "traversal"):
                    pats = [q for p in ps.get("sink_patterns", []) for q in
                            _subst(p, s["binding"])]
                    if ps["kind"] == "traversal":
                        bad = [p for p in pats if not _code_dir(p) and not _params_in(p)]
                        if bad:
                            viol.append("TRAVERSAL_OF_NON_CODE_DIR")
                        if any(_params_in(p) for p in pats):
                            details.append({"deferred_patterns": [p for p in pats
                                                                  if _params_in(p)]})
                        continue
                    r = judge_reads({"kind": "read"}, pats)
                    viol += r["violation"]
                    if r.get("deferred"):
                        details.append({"deferred_patterns": r["sink_patterns"]})
                    details.append({"via": s["callee"], "classified": r.get("classified", [])})
                elif ps["kind"] == "argv":
                    argv = []
                    for alts in ps["argv_template"]:
                        if alts and _is_star(alts[0]):
                            # a *args parameter expanded at this call site
                            argv += s["varargs"]
                        else:
                            argv.append(_uniq([q for p in alts for q in _subst(p, s["binding"])]))
                    has_param = any(_params_in(p) for alts in argv for p in alts)
                    if has_param:
                        details.append({"deferred_argv": argv})
                        continue
                    c = _classify_argv(argv)
                    viol += c["violation"]
                    if c["reads"]:
                        r = judge_reads({"kind": "read"}, c["reads"])
                        viol += r["violation"] + sorted(_blob_violation(c, r))
                        details.append({"via": s["callee"], "classified": r.get("classified", [])})
            row = {**s, "violation": sorted(set(viol)), "details": details}
            row.pop("binding", None)
            row.pop("varargs", None)
            deferred_pats = [p for d in details for p in d.get("deferred_patterns", [])]
            deferred_argv = [d["deferred_argv"] for d in details if "deferred_argv" in d]
            if deferred_pats:
                row["deferred"] = True
                row["kind"] = "read_via_call"
                row["sink_patterns"] = deferred_pats
            if deferred_argv:
                row["deferred"] = True
                row["kind"] = "argv_via_call"
                row["argv_template"] = deferred_argv[0]
            rows.append(row)
    # normalise deferred rows into summary-sink form
    for r in rows:
        if r.get("deferred"):
            if r["kind"] in ("read", "read_via_call"):
                r["kind"] = "read"
            elif r["kind"] in ("argv", "argv_via_call"):
                r["kind"] = "argv"
    return rows


def _blob_violation(c: dict, r: dict) -> set[str]:
    if not c.get("blob"):
        return set()
    hit = any(x["classes"].get("ALLOWLISTED") for x in r.get("classified", []))
    return {"BLOB_OF_A_DATA_ARTIFACT"} if hit else set()


FORBIDDEN_READ_CLASSES = frozenset(VIOLATION_CLASSES) | {
    "CALLS_A_FORBIDDEN_READER", "BLOB_OF_A_DATA_ARTIFACT", "READS_COMMIT_MESSAGES"}


def _is_loader(judged: list[dict]) -> bool:
    """A FORBIDDEN READER: a function whose body performs any read a pre-comparison module may
    not -- a protected file, a non-code external file, the runs artifact or any other file off
    the allowlist, a historical data blob, commit messages -- directly or through a call. Calling
    one from a pre-comparison module is a violation even when the function lives in a sanctioned
    reader: c11r_compare.verify_seal reads the runs artifact, so no other module may call it."""
    return any(set(j.get("violation", [])) & FORBIDDEN_READ_CLASSES for j in judged)


def judge_reads(s: dict, pats: list[tuple]) -> dict:
    deferred = [p for p in pats if _params_in(p)]
    concrete = [p for p in pats if not _params_in(p)]
    viol, classified = set(), []
    for p in concrete:
        c = classify_pattern(p)
        classified.append(c)
        viol |= set(c["violation"])
    r = {**s, "violation": sorted(viol), "classified": classified}
    r.pop("patterns", None)
    if deferred:
        r["deferred"] = True
        r["sink_patterns"] = deferred
    return r


# ---------------------------------------------------------------------------------------------
# other per-module checks
# ---------------------------------------------------------------------------------------------
def magnitude_key_reads(tree) -> list[dict]:
    out = []
    for n in ast.walk(tree):
        key = None
        # only a LOAD reads a value; `x["magnitudes"] = ...` stores into a dict the module built
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(
                n.ctx, ast.Load):
            key = n.slice.value
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and \
                n.func.attr in ("get", "pop", "setdefault") and n.args and isinstance(
                n.args[0], ast.Constant):
            key = n.args[0].value
        if key in MAGNITUDE_KEYS:
            out.append({"line": n.lineno, "expr": ast.unparse(n)[:100]})
    return out


def open_cell_literals(tree) -> list[dict]:
    """A HEURISTIC complement to the dataflow analysis, not a proof.

    Flags a numeric literal inside the open-cell drift span written to drift precision: a Fraction
    whose reduced denominator is at least 1000, or a float with at least four decimals. Every drift
    endpoint in this programme is given to at least four decimals; small-denominator values in the
    span (2.0, 7/4, 19/10) are ubiquitous quadrature weights, test abscissae and cost constants,
    and are not flagged. A drift written as F(18355, 10000) -- the revision-2 qualifier's cell 307
    point -- is.
    """
    from fractions import Fraction
    lo, hi = (Fraction(x, 10 ** 7) for x in OPEN_CELL_RANGE_E7)
    out = []
    for n in ast.walk(tree):
        v = None
        if isinstance(n, ast.Constant) and isinstance(n.value, float):
            frac = repr(n.value).split(".")[-1] if "." in repr(n.value) else ""
            if len(frac) >= 4:
                v = Fraction(repr(n.value))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                "F", "Fraction") and len(n.args) == 2 and all(
                isinstance(a, ast.Constant) and isinstance(a.value, int) for a in n.args) and \
                n.args[1].value:
            v = Fraction(n.args[0].value, n.args[1].value)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                "F", "Fraction") and len(n.args) == 1 and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            try:
                v = Fraction(n.args[0].value)
            except (ValueError, ZeroDivisionError):
                v = None
        if v is not None and v.denominator >= DRIFT_PRECISION_DENOMINATOR and lo <= v <= hi:
            out.append({"line": n.lineno, "expr": ast.unparse(n)[:80]})
    return out


def analyse(world: World, m: Module) -> dict:
    env = m.module_env
    top = judge(world, m, m.sinks_in(m.tree, env))
    fn_rows = []
    for name, fn in m.nested.items():
        summ = m.summary[name]
        penv = {p: [(P(p),)] for p in summ["params"]}
        if summ["vararg"]:
            penv[summ["vararg"]] = [(P(summ["vararg"]),)]
        fenv = m.fn_env(fn, penv)
        for r in judge(world, m, m.sinks_in(fn, fenv)):
            fn_rows.append({**r, "function": name})
    rows = top + fn_rows
    violations = [r for r in rows if r.get("violation")]
    return {"module": m.stem,
            "sinks": len(rows),
            "deferred_param_sinks": sum(1 for r in rows if r.get("deferred")),
            "violations": [{"line": r["line"], "function": r.get("function"),
                            "kind": r["kind"], "why": r["violation"], "call": r["call"]}
                           for r in violations],
            "loader_functions": sorted(n for n, s in m.summary.items() if s.get("loader")),
            "magnitude_key_reads": magnitude_key_reads(m.tree),
            "open_cell_literals": open_cell_literals(m.tree)}


def module_violations(r: dict) -> list[str]:
    v = sorted({w for x in r["violations"] for w in x["why"]})
    if r["magnitude_key_reads"]:
        v.append("MAGNITUDE_KEY_READ")
    if r["open_cell_literals"]:
        v.append("OPEN_CELL_LITERAL")
    return v


# ---------------------------------------------------------------------------------------------
# the real world: every module in the campaign code closure
# ---------------------------------------------------------------------------------------------
def real_world() -> tuple[World, dict[str, str]]:
    scope = {}
    for m in sorted(C.HERE.glob("c11r_*.py")):
        for rel in C.code_closure(m):
            scope[rel] = C.REPO / rel
    world = World()
    for rel, path in sorted(scope.items()):
        rp = "<REPO>/" + rel
        world.add(path.stem, C.read_code(rel), selfpath=rp)
    world.solve()
    return world, {path.stem: rel for rel, path in scope.items()}


def control_world(src: str, name: str) -> tuple[World, Module]:
    """A planted source analysed INSIDE the real world, so its imports resolve for real."""
    world, _ = real_world_cached()
    w = World()
    w.mods = dict(world.mods)
    mod = w.add(name, src)
    # re-solve only the planted module against the frozen summaries of the real ones
    mod.module_env = mod.build_env(ast.Module(body=[s for s in mod.tree.body if not isinstance(
        s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))], type_ignores=[]))
    for nm, fn in mod.nested.items():
        a = fn.args
        mod.summary[nm] = {"params": [x.arg for x in a.posonlyargs + a.args] +
                           [x.arg for x in a.kwonlyargs],
                           "vararg": a.vararg.arg if a.vararg else None,
                           "defaults": _defaults(mod, fn),
                           "sinks": [], "returns": [], "loader": False, "param_sinks": []}
    for _ in range(6):
        changed = False
        for nm, fn in mod.nested.items():
            summ = mod.summary[nm]
            penv = {p: [(P(p),)] for p in summ["params"]}
            env = mod.fn_env(fn, penv)
            rets = _uniq([q for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value
                          for q in mod.fold(n.value, env)]) if any(
                isinstance(n, ast.Return) and n.value for n in ast.walk(fn)) else []
            judged = judge(w, mod, mod.sinks_in(fn, env))
            new = {"returns": rets, "param_sinks": [j for j in judged if j.get("deferred")],
                   "loader": _is_loader(judged)}
            if repr(new) != repr({k: summ.get(k) for k in new}):
                summ.update(new)
                changed = True
        if not changed:
            break
    mod.module_env = mod.build_env(ast.Module(body=[s for s in mod.tree.body if not isinstance(
        s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))], type_ignores=[]))
    return w, mod


_RW = None


def real_world_cached():
    global _RW
    if _RW is None:
        _RW = real_world()
    return _RW


# ---------------------------------------------------------------------------------------------
# planted controls. POSITIVES must all be flagged; NEGATIVES must all be clean. L1-L14 are the
# second reviewer's fourteen leak paths (review round 2, B-2), verbatim in substance.
# ---------------------------------------------------------------------------------------------
_Q = 'C.NS/"evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"'
POSITIVE = {
    "L1_glob_loads_quarantine":
        'import json, c11r_common as C\nfor p in (C.NS/"evidence").rglob("*.json"):\n'
        '    o = json.loads(p.read_text())\n',
    "L2_string_concat_name":
        'import c11r_common as C\n'
        'x = C.load(C.C2/"evidence"/"registry_c2"/("REGISTRY_" + "C2.json"))\n',
    "L3_fstring_name":
        'import c11r_common as C\nk="C2"\nx = C.load(C.C2/"evidence"/"registry_c2"/f"REGISTRY_{k}.json")\n',
    "L4_from_import_loader":
        'from c11r_compare import load_original_magnitudes\nm = load_original_magnitudes({})\n',
    "L5_for_loop_taint":
        f'import c11r_common as C\nfor p in [{_Q}]:\n    x = C.load(p)\n',
    "L6_git_show_helper":
        'import c11r_common as C\nx = C.git("show", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure/'
        'evidence/registry_c2/REGISTRY_C2.json")\n',
    "L7_walrus":
        f'import c11r_common as C\nif (p := {_Q}):\n    x = C.load(p)\n',
    "L8_function_arg":
        f'import c11r_common as C\ndef g(p):\n    return C.load(p)\ng({_Q})\n',
    "L9_getattr_import":
        'import importlib\nK = importlib.import_module("c11r_compare")\n'
        'm = getattr(K, "load_original_magnitudes")({})\n',
    "L10_review_md_with_values":
        'import c11r_common as C\nt = (C.NS/"review"/"REVIEW_C11R_PREFREEZE.md").read_text()\n',
    "L12_subprocess_cat":
        'import subprocess\nsubprocess.run(["cat", "evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"],'
        ' capture_output=True)\n',
    "L13_with_open":
        'with open("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json") as f:\n    x = f.read()\n',
    "L14_direct_quarantine_load":
        f'import c11r_common as C\nx = C.load({_Q})\n',
    # beyond the reviewer's set
    "P15_module_constant_in_common":
        'import c11r_common as C\nx = C.load(C.NS / C.QUARANTINE_REL)\n',
    "P16_helper_in_common_with_parameter":
        'import c11r_common as C\nx = C.load_allowlisted("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json")\n',
    "P17_helper_returns_the_path":
        'import c11r_common as C\ndef where():\n    return C.NS / "evidence" / "quarantine"\n'
        'x = C.load(where() / "C11R_ORIGINAL_MAGNITUDES.json")\n',
    "P18_path_through_a_dict":
        'import c11r_common as C\nd = {"p": C.QUARANTINE_REL}\nx = C.load(C.NS / d["p"])\n',
    "P19_git_grep_prints_content":
        'import c11r_common as C\nx = C.git("grep", "-n", "tau", "HEAD", "--", '
        '"level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json")\n',
    "P20_blob_of_predecessor_result":
        'import c11r_common as C\nb = C.blob_at("440bcd91", "level4/closure_proofs/'
        'p5y_k5_tail_c11_n9_independent_certifier/evidence/n9/C11_N9_RESULT.json")\n',
    "P21_external_non_code_via_module_path":
        'import c11r_common as C\nx = C.load(C.C11 / "evidence" / "crosscheck" / "C11_CROSSCHECK.json")\n',
    "P22_traversal_of_evidence_without_a_read":
        'import c11r_common as C\nnames = [p.name for p in (C.NS / "evidence").iterdir()]\n',
    "P23_os_system_shell_string":
        'import os\nos.system("head -c 200 evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json")\n',
    "P24_read_the_prospective_runs_artifact":
        'import c11r_common as C\nr = C.load(C.NS / "evidence" / "runs" / "C11R_RUNS.json")\n',
    "P25_unresolvable_path":
        'import c11r_common as C, sys\nx = C.load(sys.argv[1])\n',
    "P26_launch_the_comparator":
        'import subprocess, sys\nsubprocess.run([sys.executable, "code/c11r_compare.py"])\n',
    "P26b_launch_the_comparator_from_a_list":
        'import subprocess, sys, pathlib\nH = pathlib.Path("code")\n'
        'for m in ("c11r_b0.py", "c11r_compare.py"):\n'
        '    subprocess.run([sys.executable, str(H / m)])\n',
    "P27_read_a_magnitude_key":
        'import c11r_common as C\nt = C.load(C.NS / "evidence/table/C11R_N9_STATEMENTS.json")\n'
        'v = t["constants"]["tau"]["value_float"]\n',
    "P28_open_cell_literal":
        'from fractions import Fraction as F\ne = F(18355, 10000)\n',
    "P28b_cell_306_endpoint_as_a_float":
        'e = 1.7885921\n',
    "P32_historical_blob_of_an_allowlisted_artifact":
        'import c11r_common as C\nb = C.blob_at("9801276c", "level4/closure_proofs/'
        'p5y_k5_tail_c11r_n9_statement_alignment/evidence/errata/C11R_ERRATA.json")\n',
    "P33_omitted_argument_takes_a_protected_default":
        f'import c11r_common as C\ndef f(p={_Q}):\n    return C.load(p)\nx = f()\n',
    "P29_dynamic_code":
        'src = "x = 1"\nexec(src)\n',
    "P30_old_mixed_table_via_blob":
        'import c11r_common as C\nb = C.blob_at("38f59993", "level4/closure_proofs/'
        'p5y_k5_tail_c11r_n9_statement_alignment/evidence/table/C11R_N9_TABLE.json")\n',
    "P31_retired_screen_via_blob":
        'import c11r_common as C\nb = C.blob_at("38f59993", str((C.NS / "evidence" / "screen" / '
        '"C11R_SCREEN.json").relative_to(C.REPO)))\n',
}
NEGATIVE = {
    "L11_errata_json_is_value_free":
        'import c11r_common as C\nt = C.load(C.NS/"evidence"/"errata"/"C11R_ERRATA.json")\n',
    "N1_docstring_mention":
        '"""This module never reads REGISTRY_C2.json; only the comparator does."""\nx = 1\n',
    "N2_print_mention":
        'print("the registry REGISTRY_C2.json is read only at comparison time")\n',
    "N3_semantic_label":
        'SOURCE = {"source": "REGISTRY_C2.json", "role": "label only"}\n',
    "N4_load_the_statement_table":
        'import c11r_common as C\nt = C.load(C.NS / "evidence/table/C11R_N9_STATEMENTS.json")\n'
        'k = t["constants"]["tau"]["kernel"]\n',
    "N5_launch_the_extractor":
        'import subprocess, sys\nsubprocess.run([sys.executable, "code/c11r_table.py"])\n',
    "N6_store_a_magnitude_key_into_a_local_dict":
        'planted = {}\nplanted["magnitudes"] = {"tau": "planted"}\nplanted["value_float"] = 0\n',
    "N7_content_free_id_of_the_quarantine":
        f'import c11r_common as C\ni = C.content_free_id({_Q})\n',
    "N8_git_grep_names_only_with_exclusions":
        'import c11r_common as C\nx = C.git("grep", "-l", "-E", "guard", "HEAD", "--", "*.json", '
        '":(exclude,literal)level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/'
        'REGISTRY_C2.json")\n',
    "N9_glob_the_code_directory":
        'import c11r_common as C\nfor m in sorted(C.HERE.glob("c11r_*.py")):\n    s = m.read_text()\n',
    "N10_git_names_only":
        'import c11r_common as C\nx = C.git("ls-files", "level4/closure_proofs").splitlines()\n',
    "N11_allowlisted_helper":
        'import c11r_common as C\np = C.load_allowlisted("config/C11R_POLICY.json")\n',
    "N12_declared_r5_map":
        'import c11r_common as C\nm = C.r5_open_by_verdict("5")\n',
    "N13_existence_check_of_the_runs_path":
        'import c11r_common as C\nx = (C.NS / "evidence" / "runs").exists()\n',
    "N14_block_width_literal_outside_the_open_cells":
        'from fractions import Fraction as F\nw = F(108337, 1250000)\nnt = F(5, 2)\n',
    "N15_small_denominator_constants_inside_the_span":
        'from fractions import Fraction as F\nweights = (4.0, 2.0)\nz = F(7, 4)\nc = F(19, 10)\n',
}
# The third reviewer's twenty leak paths (review round 3, N-1), verbatim in substance. Their
# outcomes are RECORDED, not asserted: this analysis is a heuristic, and several are known misses.
KNOWN_MISS_PROBES = {
    "R1_pathlib_Path_multi_arg":
        'import c11r_common as C, pathlib\nx = C.load(pathlib.Path(C.NS, "evidence", "quarantine", '
        '"C11R_ORIGINAL_MAGNITUDES.json"))\n',
    "R2_percent_format":
        'import c11r_common as C\nx = C.load("%s/evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json" '
        '% C.NS)\n',
    "R3_python_dash_c_subprocess":
        'import subprocess, sys\nsubprocess.run([sys.executable, "-c", "print(open(\'evidence/'
        'quarantine/C11R_ORIGINAL_MAGNITUDES.json\').read())"])\n',
    "R4_python3_literal_dash_c":
        'import subprocess\nsubprocess.run(["python3", "-c", "import json; print(json.load(open('
        '\'evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json\')))"])\n',
    "R5_function_via_dict_dispatch":
        f'import c11r_common as C\ndef f(p):\n    return C.load(p)\nT = {{"a": f}}\nx = T["a"]({_Q})\n',
    "R6_aliased_loader": f'import c11r_common as C\nL = C.load\nx = L({_Q})\n',
    "R7_aliased_open":
        'o = open\nx = o("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json").read()\n',
    "R8_linecache":
        'import linecache\nx = linecache.getlines("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json")\n',
    "R9_fileinput":
        'import fileinput\nx = list(fileinput.input("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"))\n',
    "R10_urlopen_file_url":
        'import urllib.request\nx = urllib.request.urlopen("file:///x/evidence/quarantine/'
        'C11R_ORIGINAL_MAGNITUDES.json").read()\n',
    "R11_map_over_paths": f'import c11r_common as C\nxs = list(map(C.load, [{_Q}]))\n',
    "R12_functools_partial":
        f'import c11r_common as C, functools\ng = functools.partial(C.load, {_Q})\nx = g()\n',
    "R13_os_open_os_read":
        'import os\nfd = os.open("evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json", os.O_RDONLY)\n'
        'x = os.read(fd, 9999)\n',
    "R14_method_on_class_instance_with_param":
        f'import c11r_common as C\nclass R:\n    def get(self, p):\n        return C.load(p)\n'
        f'x = R().get({_Q})\n',
    "R15_lambda_param": f'import c11r_common as C\ng = lambda p: C.load(p)\nx = g({_Q})\n',
    "R16_str_replace":
        'import c11r_common as C\nx = C.load(C.NS / "evidence/table/C11R_N9_STATEMENTS.json".replace('
        '"table/C11R_N9_STATEMENTS", "quarantine/C11R_ORIGINAL_MAGNITUDES"))\n',
    "R17_git_show_via_subprocess_pipe_shell":
        'import subprocess\nsubprocess.run("git show HEAD:$(git ls-files | grep MAGNITUDES)", '
        'shell=True)\n',
    "R18_varargs_loader":
        f'import c11r_common as C\ndef g(*ps):\n    return [C.load(p) for p in ps]\nx = g({_Q})\n',
    "R19_sorted_listdir_of_quarantine_names_then_load":
        'import c11r_common as C, os\nfor n in os.listdir(str(C.NS / "evidence" / "quarantine")):\n'
        '    x = C.load(C.NS / "evidence" / "quarantine" / n)\n',
    "R20_blob_at_via_rev_parse_path":
        'import c11r_common as C\nb = C.blob_at("HEAD", C.NS_REL + "/" + C.QUARANTINE_REL)\n',
}

CONTROL_NOTES = {
    "L11_errata_json_is_value_free": (
        "the reviewer planted this as a leak because revision 2 of the errata restated original "
        "values. Revision 3 of the errata restates none (erratum E14/C, and the leak check scans "
        "the errata artifact for every original's decimal and rational forms). It is now an "
        "allowlisted, value-free input, so loading it must NOT be flagged."),
    "L4_from_import_loader": "argument added so the call matches the loader's real signature",
    "L9_getattr_import": "argument added so the call matches the loader's real signature",
}


def run_controls() -> dict:
    def one(name, src):
        w, m = control_world(src, name)
        return module_violations(analyse(w, m))
    pos = {k: one(k, s) for k, s in POSITIVE.items()}
    neg = {k: one(k, s) for k, s in NEGATIVE.items()}
    probes = {}
    for k, s in KNOWN_MISS_PROBES.items():
        try:
            probes[k] = one(k, s)
        except Exception as e:                       # the analyser failing is a recorded miss
            probes[k] = []
            probes[k + "_analyser_error"] = [f"{type(e).__name__}"]
    known = {k: {"flagged": bool(v), "why": v} for k, v in probes.items()
             if not k.endswith("_analyser_error")}
    return {"positive": {k: {"flagged": bool(v), "why": v} for k, v in pos.items()},
            "negative": {k: {"flagged": bool(v), "why": v} for k, v in neg.items()},
            "known_miss_probes": {"cases": known,
                                  "flagged": sum(1 for v in known.values() if v["flagged"]),
                                  "missed": sum(1 for v in known.values() if not v["flagged"]),
                                  "asserted": False,
                                  "note": ("the third reviewer's 20 paths; recorded, not "
                                           "asserted -- this analysis is a heuristic")},
            "notes": CONTROL_NOTES,
            "all_positives_flagged": all(pos.values()),
            "no_negative_flagged": not any(neg.values())}


def runtime_open_guard_controls() -> dict:
    """The RUNTIME layer, exercised on PLANTED dummy files with protected names -- the real
    quarantine is never touched. The files are created by a subprocess, because this process may
    not open them even to write. Revision 2 (review round 4, N4-2): symlink, chdir + bare name, a
    faked program name, an impostor file named c11r_compare.py, and the sanctioned context outside
    a reader are all exercised; the one residual bypass (code that rewrites __main__.__file__ AND
    enters the sanctioned context) is DEMONSTRATED and recorded, not hidden."""
    import os
    import subprocess
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp(prefix="c11r_guard_"))
    (d / "quarantine").mkdir()
    planted = d / "quarantine" / "C11R_ORIGINAL_MAGNITUDES.json"
    innocent_in_protected_dir = d / "quarantine" / "innocent_name.json"
    for f in (planted, innocent_in_protected_dir, d / "ordinary.json"):
        subprocess.run(["/bin/sh", "-c", 'printf "{}" > "$0"', str(f)], check=True)
    plain = d / "ordinary.json"
    link = d / "innocent_link.json"
    link.symlink_to(planted)
    res, residual = {}, {}

    def refused(fn):
        try:
            fn()
            return False
        except PermissionError:
            return True

    def sanctioned_read(p):
        with C.sanctioned_protected_access("guard control"):
            return pathlib.Path(p).read_text()
    res["open_refused"] = refused(lambda: open(planted).read())
    res["read_text_refused"] = refused(lambda: planted.read_text())
    res["os_open_refused"] = refused(lambda: os.open(str(planted), os.O_RDONLY))
    res["common_load_refused"] = refused(lambda: C.load(planted))
    res["ordinary_file_allowed"] = not refused(lambda: plain.read_text())
    res["symlink_with_innocent_name_refused"] = refused(lambda: link.read_text())
    cwd = os.getcwd()
    try:
        os.chdir(d / "quarantine")
        res["chdir_then_bare_name_refused"] = refused(lambda: open("innocent_name.json").read())
    finally:
        os.chdir(cwd)
    res["sanctioned_context_outside_a_reader_refused"] = refused(lambda: sanctioned_read(planted))
    saved = sys.argv[0]
    try:
        sys.argv[0] = str(C.HERE / "c11r_table.py")         # a FAKED program name
        res["faked_program_name_refused"] = refused(lambda: planted.read_text())
        res["faked_program_name_in_the_sanctioned_context_refused"] = refused(
            lambda: sanctioned_read(planted))
    finally:
        sys.argv[0] = saved
    imp = d / "impostor"
    imp.mkdir()
    (imp / "c11r_compare.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, sys.argv[1])\nimport c11r_common as C\n"
        "try:\n    with C.sanctioned_protected_access('impostor'):\n"
        "        pathlib.Path(sys.argv[2]).read_text()\n    print('OPENED')\n"
        "except PermissionError:\n    print('REFUSED')\n")
    r = subprocess.run([sys.executable, str(imp / "c11r_compare.py"), str(C.HERE), str(planted)],
                       capture_output=True, text=True)
    res["impostor_file_named_c11r_compare_refused"] = r.stdout.strip().endswith("REFUSED")
    main = sys.modules["__main__"]
    had = hasattr(main, "__file__")
    saved_file = getattr(main, "__file__", None)
    try:
        main.__file__ = str(C.HERE / "c11r_table.py")      # the reader identity, simulated
        res["reader_in_the_sanctioned_context_allowed"] = not refused(
            lambda: sanctioned_read(planted))
        res["reader_outside_the_sanctioned_context_refused"] = refused(
            lambda: planted.read_text())
        residual["rewriting___main__.__file___and_entering_the_context_opens"] = \
            res["reader_in_the_sanctioned_context_allowed"]
    finally:
        if had:
            main.__file__ = saved_file
        else:
            del main.__file__
    # revision 3 (review round 5, N5-10): PathLike arguments, hard links and renames. The planted
    # files' inodes are registered exactly as production registers the quarantine and registry.
    import io
    res["io_FileIO_of_a_Path_refused"] = refused(lambda: io.FileIO(planted).read())
    C.protect_inode(planted)
    hard = d / "innocent_hardlink.json"
    os.link(planted, hard)                                # os.link raises no "open" event
    res["hard_link_with_innocent_name_refused"] = refused(lambda: hard.read_text())
    moved_src = d / "quarantine" / "C11R_ORIGINAL_MAGNITUDES_2.json"
    subprocess.run(["/bin/sh", "-c", 'printf "{}" > "$0"', str(moved_src)], check=True)
    C.protect_inode(moved_src)
    moved = d / "renamed_innocent.json"
    os.replace(moved_src, moved)
    res["rename_then_open_refused"] = refused(lambda: moved.read_text())
    plain_dir = d / "plain_dir"
    plain_dir.mkdir()
    os.link(planted, plain_dir / "innocent.json")
    dfd = os.open(str(plain_dir), os.O_RDONLY)
    try:
        fd = os.open("innocent.json", os.O_RDONLY, dir_fd=dfd)
        os.close(fd)
        residual["dir_fd_relative_open_of_a_hard_link_opens"] = True
    except PermissionError:
        residual["dir_fd_relative_open_of_a_hard_link_opens"] = False
    finally:
        os.close(dfd)
    subprocess.run(["rm", "-rf", str(d)], check=True)
    res["ALL_PASS"] = all(res.values())
    res["residual_bypass_demonstrated"] = residual
    res["scope"] = ("DEFENSE IN DEPTH. Python-level opens in any process importing c11r_common, "
                    "judged on the path as given (a PathLike through os.fspath), absolute and "
                    "realpath, and -- for the two magnitude-bearing files, the quarantine and the "
                    "registry -- by INODE, so a hard link or a rename of either is refused; a "
                    "reader is identified by the realpath of __main__.__file__. NOT covered: "
                    "subprocess reads (git, cat, a python child that does not import it), "
                    "descriptors opened elsewhere, an open relative to a directory descriptor "
                    "(dir_fd; demonstrated above), hard links or renames of the other protected "
                    "files (review prose: name and directory only), a magnitude-bearing file "
                    "replaced by a new inode after the process started, and in-process code that "
                    "rewrites __main__.__file__ and enters the sanctioned context (demonstrated "
                    "above). The load-bearing protection is the execution chain, which refuses "
                    "before the comparator's loader runs.")
    return res


def scan_structural_artifacts() -> list[dict]:
    """Every allowlisted pre-result artifact produced BEFORE this one carries no forbidden payload
    key. The five produced after it (this artifact, the chain controls, the mutations, the leak
    check and the status report) are not read here -- reading them would make this artifact depend on its own
    consumers -- and the status report, which runs last, scans every artifact's keys."""
    rows = []
    later = ("evidence/firewall/C11R_FIREWALL.json", "evidence/chain/C11R_CHAIN_CONTROLS.json",
             "evidence/mutations/C11R_MUTATIONS.json", "evidence/leakcheck/C11R_LEAKCHECK.json",
             "evidence/status/C11R_STATUS.json")
    for rel in C.PRE_RESULT_ARTIFACTS:
        if rel in later:
            continue
        if not (C.NS / rel).exists():
            rows.append({"artifact": rel, "exists": False, "forbidden_keys": []})
            continue
        rows.append({"artifact": rel, "exists": True,
                     "forbidden_keys": S.forbidden_payload(C.load_allowlisted(rel))})
    return rows


def _exempted(module: str, row: dict) -> bool:
    """An explicit exemption (EXEMPTED_CALLS / EXEMPTED_FUNCTIONS), with its reason recorded."""
    calls = EXEMPTED_CALLS.get(module, ())
    funcs = EXEMPTED_FUNCTIONS.get(module, ())
    if row.get("function") in funcs:
        return True
    why = set(row.get("why") or [])
    return bool(why) and why <= {"CALLS_A_FORBIDDEN_READER", "NS_OFF_ALLOWLIST"} and (
        any(c.split(".")[1] + "(" in row.get("call", "") for c in calls)
        or any(f + "(" in row.get("call", "") for f in funcs))


def main() -> int:
    world, stems = real_world_cached()
    results, offenders, exemptions = {}, [], []
    for stem, m in sorted(world.mods.items()):
        r = analyse(world, m)
        allowed = stem + ".py" in ALLOWED_READERS
        kept = []
        for row in r["violations"]:
            if _exempted(stem + ".py", row):
                exemptions.append({"module": stem + ".py", "line": row["line"],
                                   "call": row["call"][:100]})
            else:
                kept.append(row)
        r["violations"] = kept
        v = module_violations(r)
        r["allowed_reader"] = allowed
        r["module_violations"] = v
        results[stems[stem]] = r
        if v and not allowed:
            offenders.append({"module": stems[stem], "violations": v})
    real_unmatched = sorted({c["pattern"] for c in _MATCH_CACHE.values() if not c["classes"]})
    ctl = run_controls()
    guard = runtime_open_guard_controls()
    struct = scan_structural_artifacts()
    struct_bad = [r for r in struct if r["forbidden_keys"]]
    missing = [r["artifact"] for r in struct if not r["exists"]]
    inv = inventory()
    ok = (ctl["all_positives_flagged"] and ctl["no_negative_flagged"] and not offenders
          and not struct_bad and guard["ALL_PASS"])
    out = {"schema": "C11R_FIREWALL/4",
           "CLAIM": "DEFENSE_IN_DEPTH_HEURISTIC",
           "what_PASS_means": ("every planted positive is flagged, no negative is, this analysis "
                               "finds no violating read in the campaign's code, and the runtime "
                               "open-guard refuses a planted protected open"),
           "what_it_does_not_prove": ("that no leak path exists: the analysis is a heuristic "
                                      "with known misses (known_miss_probes), and the runtime "
                                      "guard does not see subprocess reads"),
           "load_bearing_protections": ["explicit production allowlists",
                                        "the quarantine architecture: two sanctioned readers",
                                        "the frozen execution contract, recomputed at every "
                                        "boundary, over COMPLETE reachable history (round 5, "
                                        "R4-1)",
                                        "the comparator's twelve verification steps, all "
                                        "before the magnitude loader (round 5, N4-5; exercised "
                                        "by the chain controls' loader spy)"],
           "defence_in_depth": ["this static analysis (a heuristic)",
                                "the runtime open-guard (c11r_common), with the residual bypass "
                                "recorded in runtime_open_guard_controls"],
           "runtime_open_guard_controls": guard,
           "exempted_calls": {"rules": {k: list(v) for k, v in EXEMPTED_CALLS.items()},
                              "functions": {k: list(v) for k, v in EXEMPTED_FUNCTIONS.items()},
                              "applied": exemptions},
           "principle": ("original magnitudes may enter only at c11r_table.py (extraction into "
                         "quarantine) and c11r_compare.py (after seal); every other module's "
                         "content reads must resolve to allowlisted inputs, Python source or the "
                         "declared R5 map"),
           "method": ("load-path dataflow: constant folding + taint through assignment, walrus, "
                      "loops, comprehensions, containers, parameters and returns, across "
                      "modules; resolved patterns matched against the git file inventory"),
           "allowed_readers": sorted(ALLOWED_READERS),
           "allowed_ns_inputs": list(C.ALLOWED_NS_INPUTS),
           "declared_external_inputs": list(C.DECLARED_EXTERNAL_INPUTS),
           "exempt_functions": [".".join(x) for x in sorted(EXEMPT_FUNCTIONS)],
           "inventory": {"files": len(inv),
                         "by_class": {c: sum(1 for v in inv.values() if v == c)
                                      for c in sorted(set(inv.values()))}},
           "controls": ctl,
           "modules_scanned": len(results),
           "per_module": results,
           "offenders": offenders,
           "structural_artifact_scan": struct,
           "structural_offenders": struct_bad,
           "artifacts_not_yet_written": missing,
           "read_patterns_resolving_to_no_file": {
               "patterns": real_unmatched,
               "scope": "the real campaign code only (control sources are analysed afterwards)",
               "note": ("recorded so that a vacuous resolution is visible (erratum E23). Expected "
                        "here: argument tokens that the subprocess rule treats as candidate paths "
                        "(flags, revisions, planted control words), and code-shaped paths of a "
                        "fallback branch. A data-artifact path in this list would be a defect.")},
           "FIREWALL_CLASS": "PASS" if ok else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "firewall" / "C11R_FIREWALL.json", out,
                         producer=__file__)
    print("controls:")
    for k, v in ctl["positive"].items():
        print(f"  {'caught ' if v['flagged'] else 'MISSED '} {k:48s} {v['why']}")
    for k, v in ctl["negative"].items():
        print(f"  {'FALSE+ ' if v['flagged'] else 'clean  '} {k:48s} {v['why']}")
    print(f"\nmodules scanned: {len(results)}  (inventory {len(inv)} files)")
    for rel, r in sorted(results.items()):
        tag = "ALLOWED" if r["allowed_reader"] else ("VIOLATE" if r["module_violations"]
                                                     else "clean  ")
        print(f"  {tag}  {rel.split('/')[-1]:24s} sinks={r['sinks']:3d} "
              f"deferred={r['deferred_param_sinks']:2d} {r['module_violations']}")
        if r["module_violations"]:
            for x in r["violations"][:12]:
                print(f"           L{x['line']} {x.get('function')}: {x['why']} {x['call'][:90]}")
            for x in r["open_cell_literals"]:
                print(f"           L{x['line']} open-cell literal {x['expr']}")
            for x in r["magnitude_key_reads"]:
                print(f"           L{x['line']} magnitude key {x['expr']}")
    print(f"\nknown-miss probes (recorded, not asserted): "
          f"{ctl['known_miss_probes']['flagged']} flagged, "
          f"{ctl['known_miss_probes']['missed']} missed")
    print(f"runtime open-guard controls: {guard}")
    print(f"exempted calls: {exemptions}")
    print(f"read patterns resolving to no file (real code): {len(real_unmatched)}")
    print(f"offending modules: {[o['module'].split('/')[-1] for o in offenders]}")
    print(f"structural offenders: {[r['artifact'] for r in struct_bad]}")
    print(f"\nFIREWALL_CLASS = {out['FIREWALL_CLASS']}")
    print(f"wrote evidence/firewall/C11R_FIREWALL.json sha256 {s[:16]}...")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
