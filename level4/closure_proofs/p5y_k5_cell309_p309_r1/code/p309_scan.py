"""Static quarantine scan of the formal namespace (p5y_k5_cell309_p309_r1).  Exit 0 iff PASS.

  python3 code/p309_scan.py

Three layers:
1. The research campaign's pinned scanner (q309_guard.scan), rooted here, unchanged.  Its planted controls must fire.
2. The owner-authorized NARROW allowance (owner rulings 2, "QUARANTINE SCANNER"; spec fc2/FC2_SPEC_R2.md section 7;
   config/SCANNER_ALLOWANCE_P309.json).  A TARGET_PATH finding for exactly the production marker NAME is allowed only
   in a listed file, and only when all of these hold:
   (a) the literal occurs exactly once among the file's string constants;
   (b) that occurrence is the value of a module-level assignment to the single name PRODUCTION_MARKER;
   (c) PRODUCTION_MARKER is bound exactly once in the file;
   (d) no call passes PRODUCTION_MARKER, the literal or the production ref namespace together with a ref-mutating
       git verb;
   (e) the file is listed.
   Allowed findings are LISTED in the output, never silently dropped.  A refusal-test mark does not cover the literal.
3. Formal rules on every .py file of the namespace (no allowance in this stage):
   MARKER_MUTATION   a call combining a ref-mutating git verb with PRODUCTION_MARKER, the literal or the namespace;
   MARKER_ALIAS      binding another name to PRODUCTION_MARKER (only the class attribute `marker_ref` of a listed
                     file is allowed), or any use of the literal outside the listed files;
   MARKER_REBIND     an attribute store to PRODUCTION_MARKER (e.g. monkeypatching it in a test);
   GRANT_WRITE       a write call (write_text/write_bytes/open/writelines, or a git write verb) naming the production
                     grant path.
   A planted control (tests/planted_control_p309_formal.py) must fire all four.
4. Owner D5 (governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md): the ratified production mutation sites may EXIST;
   everything else that could move a ref is rejected.
   * Aliases are tracked (R4 NB1): a name bound, directly or through a tuple, a function return or an in-module call
     argument, to a marker/pending/namespace/grant-path name is itself such a name (MARKER_MUTATION, GRANT_WRITE).
   * A sanctioned site is the unique module-level function of that name in its listed file, with the listed AST hash.
   REF_MUTATION_UNLISTED  a git call with a ref-moving verb (config `ref_mutation_verbs`, as a positional argument of a
                          git-runner call) in a function that is not listed in config `ref_mutation_functions` with
                          its current AST sha256 (and a reason) -- so a dynamically constructed ref name, however it is
                          built, is caught wherever it is not already reviewed and pinned
   MARKER_TOKEN           a string constant carrying a production ref-name token (config `production_tokens`) other
                          than the reviewed definitions (the listed constants' own assignments)
   REF_FILE_WRITE         a filesystem mutation (open for writing, os.open O_CREAT/O_WRONLY, write_*, mkdir, rename,
                          replace, link, symlink, unlink, remove, copy, move) naming a refs path
   CONTROL_MARK_UNLISTED  a planted-control mark in a file not listed in config `planted_control_files`
   A planted control must fire every formal kind.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
RNS = FNS.parent / "p5y_k5_cell309_research_r1"
sys.path.insert(0, str(RNS / "code"))
import q309_guard as Q  # noqa: E402

ALLOW = json.loads((FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_text())
NAMES = ALLOW["names"]                                  # [{literal, constant, files}]
LIT = NAMES[0]["literal"]                               # the production marker NAME
CONST = NAMES[0]["constant"]
LITS = tuple(n["literal"] for n in NAMES)
CONSTS = tuple(n["constant"] for n in NAMES)
MENTION = set(ALLOW["mention_names"])
NSPACE = ALLOW["production_ref_namespace"]
SITES = ALLOW["exactly_once_sites"]
VERBS = set(ALLOW["mutating_git_verbs"])
GRANT_MARKS = tuple(ALLOW["production_grant_markers"]) + ("_PROD_GRANT_PATH",)
GRANT_NAMES = {"grant_path", "_PROD_GRANT_PATH"}
TOKENS = tuple(ALLOW["production_tokens"])
REF_FUNCS = ALLOW["ref_mutation_functions"]
CONTROL_FILES = set(ALLOW["planted_control_files"])
TOKEN_DEFS = ALLOW["token_definitions"]
FS_WRITE_FUNCS = {"mkdir", "makedirs", "rename", "replace", "renames", "link", "symlink", "unlink", "remove", "rmtree",
                  "copy", "copy2", "copyfile", "copytree", "move", "touch", "write_text", "write_bytes", "writelines"}
WRITE_FUNCS = {"write_text", "write_bytes", "writelines"}
FORMAL_KINDS = {"MARKER_MUTATION", "MARKER_ALIAS", "MARKER_REBIND", "GRANT_WRITE", "REF_MUTATION_UNLISTED",
                "MARKER_TOKEN", "REF_FILE_WRITE"}
PROCESS_KINDS = {"PROCESS_FORBIDDEN", "PROCESS_SHELL", "PROCESS_UNLISTED", "PROCESS_ALIAS", "RUNNER_ALIAS",
                 "DYNAMIC_IMPORT", "DYNAMIC_EXEC", "GIT_OPTION_FORBIDDEN", "GIT_CALL_OPAQUE", "GIT_WRITE_UNLISTED",
                 "GITDIR_WRITE", "IMPORT_UNLISTED", "INTROSPECTION", "ENV_UNLISTED"}


def _atoms(node) -> set:
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.add(n.value)
        elif isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def _mentions_marker(atoms: set) -> bool:
    return any(a in MENTION or (isinstance(a, str) and (any(l in a for l in LITS) or NSPACE in a)) for a in atoms)


def _literal_nodes(tree, lit=None) -> list:
    lit = LIT if lit is None else lit
    return [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and lit in n.value]


def _func_of(tree) -> dict:
    """node id -> the innermost enclosing function NODE (None at module level)."""
    out = {}

    def walk(n, fn):
        for ch in ast.iter_child_nodes(n):
            f = ch if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
            out[id(ch)] = f
            walk(ch, f)
    walk(tree, None)
    return out


_SHA_CACHE: dict = {}


def clear_caches() -> None:
    """the per-tree caches hold their trees; each scan (and each static-check T7 pass) starts empty, so that repeated
    scans of planted copies (QC_D5) do not accumulate every parsed tree"""
    for c in (_SHA_CACHE, _OWNERS_CACHE, _DEFS_CACHE, _QUAL_CACHE, _IMPORTS_CACHE, _MODULE_FILES):
        c.clear()


def ast_sha(fn) -> str:
    hit = _SHA_CACHE.get(id(fn))
    if hit is None or hit[0] is not fn:
        hit = (fn, hashlib.sha256(ast.dump(fn).encode()).hexdigest())
        _SHA_CACHE[id(fn)] = hit
    return hit[1]


_DEFS_CACHE: dict = {}


def _defs_by_name(tree) -> dict:
    hit = _DEFS_CACHE.get(id(tree))
    if hit is None or hit[0] is not tree:
        d = {}
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d.setdefault(n.name, []).append(n)
        hit = (tree, d)
        _DEFS_CACHE[id(tree)] = hit
    return hit[1]


def _unique_module_def(tree, fn) -> bool:
    """fn is a module-level def and the only def of that name anywhere in the file"""
    return fn in tree.body and len(_defs_by_name(tree).get(fn.name, [])) == 1


def _site_ok(tree, rel: str, fn) -> bool:
    if fn is None or not _unique_module_def(tree, fn):
        return False
    return any(s["file"] == rel and s["function"] == fn.name and s["ast_sha256"] == ast_sha(fn) for s in SITES)


_OWNERS_CACHE: dict = {}


def owners(tree) -> dict:
    """node id -> (qualified name, node) of the OUTERMOST enclosing function: `func` at module level, or
    `Class.method` for a method of a module-level class.  Nested functions and lambdas belong to their owner, whose
    AST hash covers them."""
    hit = _OWNERS_CACHE.get(id(tree))
    if hit is not None and hit[0] is tree:
        return hit[1]
    out = {}
    _OWNERS_CACHE[id(tree)] = (tree, out)

    def walk(n, owner, cls):
        for ch in ast.iter_child_nodes(n):
            o = owner
            if owner is None and isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                o = (f"{cls}.{ch.name}" if cls else ch.name, ch)
            out[id(ch)] = o
            walk(ch, o, ch.name if (owner is None and cls is None and isinstance(ch, ast.ClassDef)) else cls)
    walk(tree, None, None)
    return out


_QUAL_CACHE: dict = {}


def _unique_owner(tree, owner) -> bool:
    """no other outermost function of the file has the same qualified name"""
    hit = _QUAL_CACHE.get(id(tree))
    if hit is None or hit[0] is not tree:
        q = {}
        for o in owners(tree).values():
            if o is not None:
                q.setdefault(o[0], {})[id(o[1])] = o[1]
        hit = (tree, q)
        _QUAL_CACHE[id(tree)] = hit
    return len(hit[1].get(owner[0], {})) == 1


def _ref_func_ok(tree, rel: str, owner) -> bool:
    if owner is None:
        return False
    qual, node = owner
    if not _unique_owner(tree, owner):
        return False
    return any(r["file"] == rel and r["function"] == qual and r["ast_sha256"] == ast_sha(node) and r.get("reason")
               for r in REF_FUNCS)


def _callee(n: ast.Call) -> str:
    return n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else "")


def _positional_strings(n: ast.Call) -> list:
    out = []
    for a in n.args:
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            out.append(a.value)
        elif isinstance(a, (ast.List, ast.Tuple)):
            out += [x.value for x in a.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)]
    return out


STR_METHODS = {"join", "format", "replace", "strip", "lstrip", "rstrip", "lower", "upper", "removeprefix",
               "removesuffix", "encode", "decode", "__add__", "format_map", "casefold"}


def _value_names(expr) -> set | None:
    """the names and string constants a VALUE expression is built from, or None if it is not value-like.  Value-like:
    names, attributes, string constants, f-strings, + / % concatenation, conditional and boolean forms, subscripts
    and string-method calls.  An arbitrary call (for example a constructor returning an object) is not a value."""
    if isinstance(expr, ast.Name):
        return {expr.id}
    if isinstance(expr, ast.Attribute):
        inner = _value_names(expr.value)
        return {expr.attr} | (inner or set())
    if isinstance(expr, ast.Constant):
        return {expr.value} if isinstance(expr.value, str) else set()
    if isinstance(expr, ast.JoinedStr):
        out = set()
        for v in expr.values:
            got = _value_names(v.value if isinstance(v, ast.FormattedValue) else v)
            out |= got or set()
        return out
    if isinstance(expr, ast.FormattedValue):
        return _value_names(expr.value)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Mod)):
        return (_value_names(expr.left) or set()) | (_value_names(expr.right) or set())
    if isinstance(expr, ast.IfExp):
        return (_value_names(expr.body) or set()) | (_value_names(expr.orelse) or set())
    if isinstance(expr, ast.BoolOp):
        return set().union(*[(_value_names(v) or set()) for v in expr.values])
    if isinstance(expr, ast.Subscript):
        return _value_names(expr.value)
    if isinstance(expr, (ast.Tuple, ast.List)):
        return set().union(*[(_value_names(v) or set()) for v in expr.elts]) if expr.elts else set()
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr in STR_METHODS:
        out = _value_names(expr.func.value) or set()
        for a in expr.args:
            out |= _value_names(a) or set()
        return out
    if isinstance(expr, ast.Call):                   # the value returned by a (possibly marker-bearing) function
        return {_callee(expr)} - {""}
    return None


def _targets(t) -> list:
    """the bound names of an assignment target (Name ids and Attribute attrs), element-wise for tuples"""
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, ast.Attribute):
        return [t.attr]
    if isinstance(t, ast.Starred):
        return _targets(t.value)
    if isinstance(t, (ast.Tuple, ast.List)):
        return [x for e in t.elts for x in _targets(e)]
    return []


PATH_CALLS = {"Path", "PurePath", "str", "fspath", "join", "joinpath", "realpath", "abspath", "resolve", "open",
              "dirname", "with_name", "with_suffix", "expanduser"}


def _path_value_names(expr) -> set | None:
    """like _value_names, and a path-building call (Path(), str(), os.path.join(), os.open(dir) ...) carries the
    names of its receiver and arguments (a git-directory path stays a git-directory path)"""
    if isinstance(expr, ast.Call) and _callee(expr) in PATH_CALLS:
        out = set()
        if isinstance(expr.func, ast.Attribute):
            out |= _path_value_names(expr.func.value) or set()
        for a in expr.args:
            out |= _path_value_names(a) or set()
        return out
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
        return (_path_value_names(expr.left) or set()) | (_path_value_names(expr.right) or set())
    if isinstance(expr, ast.Attribute):
        return {expr.attr} | (_path_value_names(expr.value) or set())
    return _value_names(expr)


def taint(tree, seeds: set, lit_test, broad: bool = False, values=None) -> set:
    """flow-insensitive alias closure over VALUES (R4 NB1): a name becomes marker-bearing when it is bound -- directly,
    element-wise through tuples, as a loop/with/walrus target, as the parameter receiving an in-module call argument,
    or as a function whose return value is such a value -- to a value-like expression built from a seed name, an
    already marker-bearing name, or a literal accepted by lit_test.  Objects that merely CONTAIN such a value (an
    execution context, a constructor result) are not marker-bearing; their marker attributes are seeds themselves."""
    tainted = set(seeds)
    funcs = {f.name: f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def hot(expr) -> bool:
        names = _atoms(expr) if broad else (values or _value_names)(expr)
        return bool(names) and any(a in tainted or (isinstance(a, str) and lit_test(a)) for a in names)
    for _ in range(12):
        before = len(tainted)
        for n in ast.walk(tree):
            pairs = []
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, (ast.Tuple, ast.List)) and isinstance(n.value, (ast.Tuple, ast.List)) and \
                            len(t.elts) == len(n.value.elts):
                        pairs += list(zip(t.elts, n.value.elts))
                    else:
                        pairs.append((t, n.value))
            elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
                pairs.append((n.target, n.value))
            elif isinstance(n, ast.NamedExpr):
                pairs.append((n.target, n.value))
            elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)):
                pairs.append((n.target, n.iter))
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                pairs += [(i.optional_vars, i.context_expr) for i in n.items if i.optional_vars is not None]
            elif isinstance(n, ast.Call) and _callee(n) in funcs:
                f = funcs[_callee(n)]
                params = [a.arg for a in f.args.posonlyargs + f.args.args]
                if isinstance(n.func, ast.Attribute) and params[:1] == ["self"]:
                    params = params[1:]
                for k, a in enumerate(n.args):
                    if k < len(params) and hot(a):
                        tainted.add(params[k])
                for kw in n.keywords:
                    if kw.arg and hot(kw.value):
                        tainted.add(kw.arg)
            for t, v in pairs:
                if hot(v):
                    tainted.update(_targets(t))
        for f in funcs.values():
            if any(isinstance(r, ast.Return) and r.value is not None and hot(r.value) for r in ast.walk(f)):
                tainted.add(f.name)
        if len(tainted) == before:
            break
    return tainted


def write_target_atoms(n: ast.Call) -> set:
    """the atoms of the PATH a write call writes (not of the bytes written): the receiver of a Path method, the first
    argument of open / os.* / shutil.* (both paths for rename, replace, link, copy, move); for a git write, the call."""
    fname = _callee(n)
    two = {"rename", "replace", "renames", "link", "symlink", "copy", "copy2", "copyfile", "copytree", "move"}
    if isinstance(n.func, ast.Attribute) and fname in {"write_text", "write_bytes", "touch", "symlink_to",
                                                         "hardlink_to"} | ({"mkdir", "unlink", "rename", "replace"}
                                                                           if not n.args or fname in two else set()):
        return _atoms(n.func.value) | (_atoms(n.args[0]) if n.args and fname in two else set())
    args = n.args[:2] if fname in two else n.args[:1]
    out = set()
    for x in args:
        out |= _atoms(x)
    return out


def fs_write_of(n: ast.Call, atoms: set, fc=None) -> bool:
    fname = _callee(n)
    if fname in ("replace", "rename") and isinstance(n.func, ast.Attribute) and len(n.args) >= 2:
        base = n.func.value                     # os.replace(a, b) / shutil.move: a module; str.replace(a, b): not
        mods = fc.mod_alias if fc is not None else {"os": "os", "shutil": "shutil"}
        return isinstance(base, ast.Name) and mods.get(base.id) in ("os", "shutil", "posix")
    if fname in FS_WRITE_FUNCS:
        return True
    if fname == "open" and isinstance(n.func, ast.Name):      # builtin open with a writing mode
        return any(isinstance(x, ast.Constant) and isinstance(x.value, str) and set(x.value) & set("wax+")
                   for x in list(n.args[1:2]) + [k.value for k in n.keywords if k.arg == "mode"])
    if fname == "open":                                        # os.open with creating/writing flags
        return bool({"O_CREAT", "O_WRONLY", "O_RDWR", "O_APPEND", "O_TRUNC"} & atoms)
    return False


# ------------------------------------------------------------------------------------------------------------------
# Layer 5 (R4 follow-up F1(b)): an ALLOWLIST for process execution.  Every call that can start a process or run git
# is a finding unless it lies in an exactly-once site or a reviewed function (config `process_policy`
# `reviewed_functions`, AST-pinned, with the permits it needs), or it is a literal git call whose verb is in the
# read-only allowlist.  Unknown git verbs count as ref-moving.
# ------------------------------------------------------------------------------------------------------------------
PROC = ALLOW["process_policy"]
REVIEWED = PROC["reviewed_functions"]            # [{file, function, ast_sha256, permits, reason}]
RUNNERS = PROC["git_runners"]                    # [{file, function, leading, list?, kind: git|argv, reason}]
READ_VERBS = set(PROC["git_read_verbs"])
OBJECT_VERBS = set(PROC["git_object_verbs"])
GLOBAL_OPTS_1 = set(PROC["git_global_options_with_operand"])     # e.g. -C <path>
GLOBAL_OPTS_0 = set(PROC["git_global_options_flag"])
FORBIDDEN_OPTS_EXACT = set(PROC["git_forbidden_options_exact"])
FORBIDDEN_OPTS_PREFIX = tuple(PROC["git_forbidden_option_prefixes"])
PY_ARGV0 = set(PROC["python_argv0"])
VERB_OPTIONS = PROC["git_verb_options"]
SUFFIXES = set(PROC["file_suffixes"])
PROC_MODULES = {"subprocess", "os", "pty", "asyncio", "importlib", "builtins", "posix"}
OS_PROC = {"system", "popen", "startfile", "fork", "forkpty"}
OS_PROC_PREFIX = ("exec", "spawn", "posix_spawn")
SUBPROCESS_RUN = {"run", "Popen", "call", "check_call", "check_output"}
SUBPROCESS_DATA = {"DEVNULL", "PIPE", "STDOUT", "CalledProcessError", "TimeoutExpired", "CompletedProcess",
                   "SubprocessError"}
GITDIR_NAMES = {"git_dir", "git_dir_of", "_git_dir", "gitdir", "GIT_DIR", "common_dir", "_common_dir"}
GITDIR_OPTS = {"--git-dir", "--git-common-dir", "--absolute-git-dir", "--git-path"}
REF_LAST = {"packed-refs", "HEAD", "ORIG_HEAD", "FETCH_HEAD", "MERGE_HEAD", "config"}
REF_ANY = {"refs", "hooks"}
X = "\x00"                                        # an unknown piece of a folded string


def _fmt_fold(fmt: str) -> str:
    """a %-format string with placeholders for its conversions (for parsing a `python -c` code string)"""
    import re
    return re.sub(r"%(\([^)]*\))?[-#0 +]*\d*(\.\d+)?[rsdifxXa%]",
                  lambda m: "%" if m.group(0) == "%%" else ("'_'" if m.group(0).endswith("r") else "_"), fmt)


ROOT = "\x01"                                     # the repository root in a loose path fold
STR_FOLDS = {"lower": str.lower, "upper": str.upper, "strip": str.strip, "lstrip": str.lstrip, "rstrip": str.rstrip,
             "decode": lambda x: x, "casefold": str.casefold}


def fold(expr, consts=None, loose=False):
    """the string value of an expression built from literals: + and / concatenation, f-strings, %-formatting of a
    literal, str()/Path()/os.path.join()/joinpath(), chr(<int>), '<sep>'.join([...]), .decode(), .lower() and
    friends, .replace(<lit>, <lit>); bytes literals count as strings (R4F2-C1(f)).  Exact mode returns None when any
    piece is unknown; loose mode puts X for each unknown piece, and ROOT for the repository root (REPO)."""
    consts = consts or {}

    def lit(e):
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            return e.value
        if isinstance(e, ast.Constant) and isinstance(e.value, bytes):
            return e.value.decode("latin-1")
        return None

    def f(e, g):
        v = lit(e)
        if v is not None:
            return v
        if isinstance(e, ast.Name) and e.id in consts:
            return g(consts[e.id])
        if loose and (isinstance(e, ast.Name) and e.id == "REPO" or isinstance(e, ast.Attribute) and e.attr == "REPO"):
            return ROOT
        if isinstance(e, ast.JoinedStr):
            parts = [g(v.value) if isinstance(v, ast.FormattedValue) else g(v) for v in e.values]
            return None if None in parts else "".join(parts)
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Add, ast.Div)):
            a, b = g(e.left), g(e.right)
            if a is None or b is None:
                return None
            return a + b if isinstance(e.op, ast.Add) else a + "/" + b
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Mod):
            a = g(e.left)
            return None if a is None else _fmt_fold(a)
        if isinstance(e, ast.Call):
            c = _callee(e)
            if c == "chr" and isinstance(e.func, ast.Name) and len(e.args) == 1 and isinstance(e.args[0], ast.Constant) \
                    and type(e.args[0].value) is int and 0 <= e.args[0].value < 0x110000:
                return chr(e.args[0].value)
            if c in ("str", "Path", "PurePath", "fspath", "realpath", "abspath", "resolve", "bytes") and \
                    len(e.args) == 1:
                return g(e.args[0])
            if c == "joinpath" or (c == "join" and ast.unparse(e.func).endswith("path.join")):
                parts = ([g(e.func.value)] if c == "joinpath" else []) + [g(a) for a in e.args]
                return None if None in parts else "/".join(parts)
            if c == "join" and isinstance(e.func, ast.Attribute) and lit(e.func.value) is not None and \
                    len(e.args) == 1 and isinstance(e.args[0], (ast.List, ast.Tuple)):
                parts = [g(a) for a in e.args[0].elts]
                return None if None in parts else lit(e.func.value).join(parts)
            if c in STR_FOLDS and isinstance(e.func, ast.Attribute) and not e.args:
                r = g(e.func.value)
                return None if r is None else STR_FOLDS[c](r)
            if c == "replace" and isinstance(e.func, ast.Attribute) and len(e.args) == 2 and \
                    all(lit(a) is not None for a in e.args):
                r = g(e.func.value)
                return None if r is None else r.replace(lit(e.args[0]), lit(e.args[1]))
        return None
    if not loose:
        def exact(e):
            return f(e, exact)
        return exact(expr)

    def lz(e):
        r = f(e, lz)
        return X if r is None else r
    return lz(expr)


def single_constants(tree) -> dict:
    """names bound exactly once in the file, by a plain assignment of a foldable value"""
    binds = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            binds[n.id] = binds.get(n.id, 0) + 1
        elif isinstance(n, ast.arg):
            binds[n.arg] = binds.get(n.arg, 0) + 1
        elif isinstance(n, ast.alias):
            k = (n.asname or n.name).split(".")[0]
            binds[k] = binds.get(k, 0) + 1
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            binds[n.name] = binds.get(n.name, 0) + 1
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and \
                binds.get(n.targets[0].id) == 1:
            out[n.targets[0].id] = n.value
    return out


def target_folds(n: ast.Call, fc, owner_node, depth: int = 3) -> tuple:
    """(full, parts): loose folds of a write call's whole target -- following a plain name to the values its function
    (or the module) binds to it, and a call of a function of this file to its return values (R4F M07: the path is
    built into a local, or returned by a helper, first) -- and loose folds of the names / helper calls INSIDE the
    target, where only a refs / hooks component counts (their last component is not the written file)"""
    full, parts = [], []
    tops = {f.name: f for f in fc.tree.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def bound(scope, name):
        out = []
        for m in ast.walk(scope):
            vals = []
            if isinstance(m, ast.Assign):
                vals = [(t, m.value) for t in m.targets]
            elif isinstance(m, (ast.AnnAssign, ast.NamedExpr)) and m.value is not None:
                vals = [(m.target, m.value)]
            elif isinstance(m, (ast.With, ast.AsyncWith)):
                vals = [(it.optional_vars, it.context_expr) for it in m.items if it.optional_vars is not None]
            out += [v for t, v in vals if isinstance(t, ast.Name) and t.id == name]
        return out

    def returns(fn):
        return [r.value for r in ast.walk(fn) if isinstance(r, ast.Return) and r.value is not None]

    def links(e, scope):
        if isinstance(e, ast.Name):
            return [(v, scope) for v in bound(scope, e.id)]
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in tops:
            return [(r, tops[e.func.id]) for r in returns(tops[e.func.id])]
        return []

    def walk(e, scope, d, whole):
        (full if whole else parts).append(fold(e, fc.consts, loose=True))
        if d == 0:
            return
        for v, sc in links(e, scope):
            walk(v, sc, d - 1, whole)
        for sub in ast.walk(e):
            if sub is not e and isinstance(sub, (ast.Name, ast.Call)):
                for v, sc in links(sub, scope):
                    walk(v, sc, d - 1, False)
    for x in _write_target_exprs(n):
        walk(x, owner_node if owner_node is not None else fc.tree, depth, True)
    return full, parts


def _path_part_bad(sfold: str) -> bool:
    comps = [c for c in sfold.replace("\\", "/").split("/") if c]
    return bool(set(comps) & REF_ANY) or any(comps[i] == "logs" and comps[i + 1] in ("refs", "HEAD")
                                              for i in range(len(comps) - 1))


def _path_bad(sfold: str) -> str | None:
    comps = [c for c in sfold.replace("\\", "/").split("/") if c]
    if not comps:
        return None
    if set(comps) & REF_ANY or comps[-1] in REF_LAST:
        return "refs"
    if any(comps[i] == "logs" and comps[i + 1] in ("refs", "HEAD") for i in range(len(comps) - 1)):
        return "refs"
    return None


def _has_gitdir_component(sfold: str) -> bool:
    return ".git" in [c for c in sfold.replace("\\", "/").split("/")]


class FileCtx:
    """per-file resolution: module aliases (import X as Y), runner definitions, single-binding constants"""

    def __init__(self, tree, rel: str):
        self.tree, self.rel = tree, rel
        self.mod_alias = {}                               # local name -> module name
        self.from_names = {}                              # local name -> (module, name)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.mod_alias[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    self.from_names[a.asname or a.name] = (n.module, a.name)
        self.defs = {f.name for f in tree.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.consts = single_constants(tree)

    def module_of_expr(self, e, root: Path | None = None, depth: int = 0):
        """the module an expression denotes: an import alias, a name bound (anywhere in the file) to a module-valued
        expression, an attribute of a scanned project module that is itself a module there (P.D, D.G), or a module
        lookup (sys.modules[...], import_module(...)) -> '*'.  None if it is not module-valued."""
        if depth > 6:
            return None
        if isinstance(e, ast.Name):
            if e.id in self.mod_alias:
                return self.mod_alias[e.id]
            vals = self.bindings().get(e.id, [])
            for v in vals:
                m = self.module_of_expr(v, root, depth + 1)
                if m is not None:
                    return m
            return None
        if isinstance(e, ast.Subscript) and ast.unparse(e.value) == "sys.modules":
            return "*"
        if isinstance(e, ast.Call) and _callee(e) in ("import_module", "__import__"):
            return "*"
        if isinstance(e, ast.Call) and _callee(e) == "get" and isinstance(e.func, ast.Attribute) and \
                ast.unparse(e.func.value) == "sys.modules":
            return "*"
        if isinstance(e, ast.Attribute):
            base = self.module_of_expr(e.value, root, depth + 1)
            if base is None or base == "*" or root is None:
                return "*" if base == "*" else None
            mf = module_file(root, base.split(".")[-1])
            nxt = _module_imports_of(root, mf).get(e.attr) if mf else None
            return nxt
        return None

    def bindings(self) -> dict:
        if getattr(self, "_bindings", None) is None:
            out = {}
            for n in ast.walk(self.tree):
                pairs = []
                if isinstance(n, ast.Assign):
                    pairs = [(t, n.value) for t in n.targets]
                elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)) and n.value is not None:
                    pairs = [(n.target, n.value)]
                elif isinstance(n, (ast.With, ast.AsyncWith)):
                    pairs = [(i.optional_vars, i.context_expr) for i in n.items if i.optional_vars is not None]
                for t, v in pairs:
                    if isinstance(t, ast.Name):
                        out.setdefault(t.id, []).append(v)
            self._bindings = out
        return self._bindings

    def is_mod(self, node, mod: str) -> bool:
        return isinstance(node, ast.Name) and self.mod_alias.get(node.id) == mod

    def module_of(self, node) -> str | None:
        """the module name a Name / Attribute chain denotes (import aliases, and one hop through a module's own
        imports is not followed: `D.G` resolves only when this file imports the guard itself)"""
        if isinstance(node, ast.Name):
            return self.mod_alias.get(node.id)
        return None


_MODULE_FILES: dict = {}


def module_file(root: Path, mod: str) -> str | None:
    """the scanned file of a module name (code/, tests/, verify/, start_state/ of the scanned root)"""
    key = (str(root), mod)
    if key not in _MODULE_FILES:
        hit = None
        for d in ("code", "tests", "verify", "start_state"):
            if (root / d / f"{mod}.py").exists():
                hit = f"{d}/{mod}.py"
                break
        _MODULE_FILES[key] = hit
    return _MODULE_FILES[key]


_IMPORTS_CACHE: dict = {}


def _module_imports_of(root: Path, rel: str) -> dict:
    key = (str(root), rel)
    if key not in _IMPORTS_CACHE:
        _IMPORTS_CACHE[key] = _module_imports_uncached(root, rel)
    return _IMPORTS_CACHE[key]


def _module_imports_uncached(root: Path, rel: str) -> dict:
    try:
        t = ast.parse((root / rel).read_text())
    except (OSError, SyntaxError):
        return {}
    out = {}
    for n in ast.walk(t):
        if isinstance(n, ast.Import):
            for a in n.names:
                out[a.asname or a.name.split(".")[0]] = a.name
    return out


def runner_of(call: ast.Call, fc: FileCtx, root: Path) -> dict | None:
    """the registered runner a call invokes: a def of this file, a name imported from a scanned module, or an
    attribute of a module alias (followed through one module's own import aliases, e.g. D.G._git)"""
    return runner_ref(call.func, fc, root)


def runner_ref(fn, fc: FileCtx, root: Path) -> dict | None:
    """the registered runner a Name / Attribute expression denotes (None if it denotes none)"""
    if isinstance(fn, ast.Name):
        if fn.id in fc.defs:
            return next((r for r in RUNNERS if r["file"] == fc.rel and r["function"] == fn.id), None)
        if fn.id in fc.from_names:
            mod, name = fc.from_names[fn.id]
            mf = module_file(root, mod.split(".")[-1])
            return next((r for r in RUNNERS if r["file"] == mf and r["function"] == name), None)
        return None
    if isinstance(fn, ast.Attribute):
        chain, v = [fn.attr], fn.value
        while isinstance(v, ast.Attribute):
            chain.append(v.attr)
            v = v.value
        if not isinstance(v, ast.Name) or v.id not in fc.mod_alias:
            return None
        mod = fc.mod_alias[v.id]
        mf = module_file(root, mod.split(".")[-1])
        for attr in reversed(chain[1:]):                # follow module aliases (D.G -> the guard)
            if mf is None:
                return None
            nxt = _module_imports_of(root, mf).get(attr)
            mf = module_file(root, nxt.split(".")[-1]) if nxt else None
        return next((r for r in RUNNERS if r["file"] == mf and r["function"] == fn.attr), None) if mf else None
    return None


def classify_git(args: list, consts: dict) -> dict:
    """R4F F1(b): the verb class of a git argument list: read | object | ref | opaque | forbidden.  Unknown verbs are
    ref-moving; any starred or non-literal element at or before the verb is opaque."""
    i = 0
    while i < len(args):
        a = args[i]
        if isinstance(a, ast.Starred):
            return {"cls": "opaque", "why": "a starred argument at or before the verb"}
        s = fold(a, consts)
        if s is None:
            return {"cls": "opaque", "why": "a non-literal verb"}
        if s in GLOBAL_OPTS_1:
            i += 2
            continue
        if s in GLOBAL_OPTS_0:
            i += 1
            continue
        if s.startswith("-"):
            return {"cls": "forbidden", "why": f"git global option {s!r} is not allowlisted"}
        verb, rest = s, args[i + 1:]
        break
    else:
        return {"cls": "opaque", "why": "no verb"}
    lits, starred = [], False
    for k, a in enumerate(rest):
        if isinstance(a, ast.Starred):
            starred = True
            continue
        v = fold(a, consts)
        if v in ("--", "--end-of-options"):              # the terminators: everything after is an operand / pathspec
            rest = rest[:k]
            break
        if v is not None:
            lits.append(v)
            if v in FORBIDDEN_OPTS_EXACT or v.startswith(FORBIDDEN_OPTS_PREFIX):
                return {"cls": "forbidden", "verb": verb, "why": f"git option {v!r} is forbidden"}
    allowed_opts = VERB_OPTIONS.get(verb, [])
    for v in lits:                                        # R4F2-C1(e): each verb has its own option allowlist
        if v.startswith("-") and not (v in allowed_opts or any(o.endswith("=") and v.startswith(o)
                                                              for o in allowed_opts)):
            return {"cls": "forbidden", "verb": verb, "why": f"git {verb} option {v!r} is not allowlisted"}
    ops = [x for x in rest if isinstance(x, ast.Starred) or fold(x, consts) is None or
           not fold(x, consts).startswith("-")]
    cls = None
    if verb in READ_VERBS:
        cls = "read"
    elif verb == "symbolic-ref":
        cls = "read" if (not starred and len(ops) == 1 and set(lits) - {fold(o, consts) for o in ops}
                         <= {"-q", "--quiet", "--short"}) else "ref"
    elif verb == "config":
        cls = "read" if set(lits) & {"--get", "--get-all", "--get-regexp", "--list", "-l"} and not starred else "ref"
    elif verb == "branch":
        cls = "read" if not starred and lits and set(lits) <= {"--show-current", "--list"} and len(lits) == len(rest) \
            else "ref"
    elif verb == "remote":
        cls = "read" if not rest else "ref"
    elif verb in ("worktree", "sparse-checkout", "stash"):
        cls = "read" if lits[:1] == ["list"] and len(rest) == 1 else "ref"
    elif verb in OBJECT_VERBS:
        cls = "object"
    else:
        cls = "ref"
    if starred and cls == "read":
        return {"cls": "opaque", "verb": verb, "why": "starred operands"}
    return {"cls": cls, "verb": verb, "starred": starred}


def _python_argv(elts: list, consts: dict) -> dict:
    """a python interpreter argv: -c <literal code> (parsed and scanned), -m <literal module>, or a script whose
    path folds to a .py file"""
    i = 1
    while i < len(elts):
        a = elts[i]
        if isinstance(a, ast.Starred):
            return {"ok": False, "why": "a starred python argument before the script"}
        s = fold(a, consts)
        if s == "-c":
            code = fold(elts[i + 1], consts) if i + 1 < len(elts) and not isinstance(elts[i + 1], ast.Starred) \
                else None
            return {"ok": code is not None, "code": code, "control": elts[:i + 2],
                    "why": None if code is not None else "python -c with non-literal code"}
        if s == "-m":
            mod = fold(elts[i + 1], consts) if i + 1 < len(elts) else None
            return {"ok": mod is not None, "control": elts[:i + 2],
                    "why": None if mod else "python -m with a non-literal module"}
        if s is not None and s.startswith("-") and s in ("-I", "-S", "-B", "-u", "-E", "-s", "-O", "-X", "-W"):
            i += 2 if s in ("-X", "-W") else 1
            continue
        script = fold(a, consts, loose=True)
        return {"ok": script.endswith(".py") and not script.startswith(X + X), "control": elts[:i + 1],
                "why": None if script.endswith(".py") else "python script path does not fold to a .py file"}
    return {"ok": False, "why": "python without a script", "control": elts}


def process_info(n: ast.Call, fc: FileCtx, root: Path) -> dict | None:
    """None if the call starts no process; else {kind, git?, python?, why?}"""
    fn = n.func
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
        mod = fc.mod_alias.get(fn.value.id)
        if mod in ("os", "posix") and (fn.attr in OS_PROC or fn.attr.startswith(OS_PROC_PREFIX)):
            return {"kind": "PROCESS_FORBIDDEN", "why": f"os.{fn.attr}"}
        if mod == "pty" and fn.attr == "spawn" or mod == "asyncio" and fn.attr.startswith("create_subprocess"):
            return {"kind": "PROCESS_FORBIDDEN", "why": f"{mod}.{fn.attr}"}
        if mod == "subprocess":
            if fn.attr in SUBPROCESS_DATA:
                return None                                   # a result / exception object, not a process
            if fn.attr not in SUBPROCESS_RUN:
                return {"kind": "PROCESS_FORBIDDEN", "why": f"subprocess.{fn.attr}"}
            return _argv_info(n, fc, root, n.args[0] if n.args else next(
                (k.value for k in n.keywords if k.arg == "args"), None))
    r = runner_of(n, fc, root)
    if r is not None:
        lead = r.get("leading", 0)
        if r.get("kind") == "script":                 # a python-script runner: the caller names the script literally
            sc = fold(n.args[lead], fc.consts) if len(n.args) > lead else None
            ok = sc is not None and sc.endswith(".py")
            return {"kind": "python", "python": {"ok": ok, "why": None if ok else "the script of a script runner is "
                                                  "not a literal .py path"}, "control": n.args[:lead + 1]}
        if r.get("kind") == "argv":
            return _argv_info(n, fc, root, n.args[lead] if len(n.args) > lead else None, runner=r)
        if r.get("list"):
            lst = n.args[lead] if len(n.args) > lead else None
            if not isinstance(lst, (ast.List, ast.Tuple)):
                return {"kind": "git", "runner": r["function"], "git": {"cls": "opaque", "why": "the git argument "
                                                                          "list is not a literal list"}}
            gargs = list(lst.elts)
        else:
            gargs = list(n.args[lead:])
        return {"kind": "git", "runner": r["function"], "git": classify_git(gargs, fc.consts)}
    return None


def _argv_info(n: ast.Call, fc: FileCtx, root: Path, argv, runner=None) -> dict:
    if any(k.arg == "shell" and not (isinstance(k.value, ast.Constant) and k.value.value is False)
           for k in n.keywords):
        return {"kind": "PROCESS_SHELL", "why": "shell=True"}
    if not isinstance(argv, (ast.List, ast.Tuple)) or not argv.elts:
        return {"kind": "argv", "opaque": "the argv is not a literal list"}
    elts = argv.elts
    if isinstance(elts[0], ast.Starred):
        return {"kind": "argv", "opaque": "starred program"}
    if any(isinstance(e, ast.Starred) for e in elts[1:]) and not (ast.unparse(elts[0]) in PY_ARGV0 or fold(
            elts[0], fc.consts) in PY_ARGV0 | {"git", "/usr/bin/git"}):
        return {"kind": "argv", "opaque": "starred arguments"}
    prog = fold(elts[0], fc.consts)
    if ast.unparse(elts[0]) in PY_ARGV0 or prog in PY_ARGV0:
        py = _python_argv(elts, fc.consts)
        return {"kind": "python", "python": py, "control": py.get("control", elts)}
    if prog in ("git", "/usr/bin/git"):
        if any(isinstance(e, ast.Starred) for e in elts[1:]):
            return {"kind": "git", "git": {"cls": "opaque", "why": "starred git arguments"}, "raw": True}
        return {"kind": "git", "git": classify_git(elts[1:], fc.consts), "raw": True}
    return {"kind": "argv", "opaque": f"program {ast.unparse(elts[0])[:40]} is not git or python"}


def reviewed(rel: str, owner, permit: str, tree=None) -> bool:
    if owner is None or (tree is not None and not _unique_owner(tree, owner)):
        return False
    qual, node = owner
    return any(r["file"] == rel and r["function"] == qual and r["ast_sha256"] == ast_sha(node) and r.get("reason")
               and permit in r.get("permits", []) for r in REVIEWED)


def process_rules(tree, rel: str, root: Path, recurse=None) -> list:
    """layer 5 findings for one file (or one parsed `python -c` code string)"""
    fc = FileCtx(tree, rel)
    own = owners(tree)
    fn_of = _func_of(tree)
    out = []

    def rec(node, kind, what):
        out.append({"file": rel, "line": getattr(node, "lineno", 0), "kind": kind, "what": str(what)[:120]})
    call_funcs = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    attr_values = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    gitdir = taint(tree, set(GITDIR_NAMES), lambda a: _has_gitdir_component(a) or a in GITDIR_OPTS,
                   values=_path_value_names)
    for n in ast.walk(tree):
        o = own.get(id(n))
        site = _site_ok(tree, rel, fn_of.get(id(n)))
        if isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] in PROC_MODULES:
            names = {a.name for a in n.names}
            m0 = n.module.split(".")[0]
            if m0 in ("subprocess", "pty", "importlib", "builtins") or (m0 in ("os", "posix") and any(
                    x == "*" or x in OS_PROC or x.startswith(OS_PROC_PREFIX) for x in names)):
                rec(n, "PROCESS_ALIAS", f"from {n.module} import {sorted(names)}")
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and id(n) not in call_funcs:
            mod = fc.mod_alias.get(n.value.id)
            if (mod == "subprocess" and n.attr not in SUBPROCESS_DATA) or (
                    mod in ("os", "posix") and (n.attr in OS_PROC or n.attr.startswith(OS_PROC_PREFIX)
                                                 or n.attr == "__dict__")) or (mod == "pty" and n.attr == "spawn"):
                rec(n, "PROCESS_ALIAS", f"{mod}.{n.attr} used as a value")
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and id(n) not in attr_values and \
                fc.mod_alias.get(n.id) in ("subprocess", "pty"):
            rec(n, "PROCESS_ALIAS", f"the {fc.mod_alias[n.id]} module used as a value")
        if isinstance(n, (ast.Name, ast.Attribute)) and isinstance(n.ctx, ast.Load) and id(n) not in call_funcs \
                and id(n) not in attr_values and runner_ref(n, fc, root) is not None and not reviewed(
                rel, o, "runner_alias", tree):
            rec(n, "RUNNER_ALIAS", f"the git runner {ast.unparse(n)} used as a value")
        if not isinstance(n, ast.Call):
            continue
        c = _callee(n)
        if isinstance(n.func, ast.Name) and c in ("getattr", "setattr", "vars", "delattr", "hasattr") and n.args and \
                isinstance(n.args[0], ast.Name) and fc.mod_alias.get(n.args[0].id) in PROC_MODULES:
            rec(n, "PROCESS_ALIAS", f"{c} on the {fc.mod_alias[n.args[0].id]} module")
        if isinstance(n.func, ast.Name) and c in ("__import__",) or (
                c == "import_module" and isinstance(n.func, ast.Attribute)):
            mod = fold(n.args[0], fc.consts) if n.args else None
            if mod is None:
                rec(n, "DYNAMIC_IMPORT", f"{c} with a non-literal module")
            elif mod.split(".")[0] in PROC_MODULES:
                rec(n, "PROCESS_ALIAS", f"{c}({mod!r})")
        if isinstance(n.func, ast.Name) and c in ("exec", "eval", "compile") and n.args:
            code = fold(n.args[0], fc.consts)
            if code is None:
                if not (site or reviewed(rel, o, "dynamic_exec", tree)):
                    rec(n, "DYNAMIC_EXEC", f"{c} with non-literal code")
            elif recurse is not None:
                out.extend(recurse(code, f"{rel}:{n.lineno}:{c}"))
        info = process_info(n, fc, root)
        if info is None:
            continue
        k = info["kind"]
        opaque = (k == "argv" or (k == "python" and not info["python"]["ok"])
                  or (k == "git" and info["git"]["cls"] == "opaque"))
        if opaque and o is not None and _forwards_params(o[1], info.get("control", n.args[:2])) and not any(
                r["file"] == rel and r["function"] == o[0] for r in RUNNERS) and not reviewed(
                rel, o, "forwards_operands", tree):
            rec(n, "RUNNER_UNREGISTERED", f"{o[0]} forwards its parameters into a process call")
        if k in ("PROCESS_FORBIDDEN", "PROCESS_SHELL"):
            rec(n, k, info["why"])
            continue
        if k == "argv":
            if not (site or reviewed(rel, o, "process", tree)):
                rec(n, "PROCESS_UNLISTED", info["opaque"])
            continue
        if k == "python":
            py = info["python"]
            if not py["ok"] and not (site or reviewed(rel, o, "process", tree)):
                rec(n, "PROCESS_UNLISTED", py["why"])
            if py.get("code") is not None and recurse is not None:
                out.extend(recurse(py["code"], f"{rel}:{n.lineno}:-c"))
            continue
        g = info["git"]
        if g["cls"] == "read":
            continue
        if g["cls"] == "forbidden":
            rec(n, "GIT_OPTION_FORBIDDEN", g["why"])
            continue
        if g["cls"] == "opaque":
            if not (site or reviewed(rel, o, "process", tree)):
                rec(n, "GIT_CALL_OPAQUE", g["why"])
            continue
        if g["cls"] == "object" and not (site or reviewed(rel, o, "git_write", tree) or _ref_func_ok(tree, rel, o)):
            rec(n, "GIT_WRITE_UNLISTED", f"{(o or ('<module>',))[0]}: {g['verb']}")
        # ref-class verbs: REF_MUTATION_UNLISTED in formal_rules (it uses the same classifier)
    # git-dir writes: a filesystem write whose target is built from a git directory
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and fs_write_of(n, _atoms(n), fc):
            tex = _write_target_exprs(n)
            ta = write_target_atoms(n).union(*(_atoms(e) for e in tex))
            tf, tparts = target_folds(n, fc, (own.get(id(n)) or (None, None))[1])
            if (ta & gitdir or any(_has_gitdir_component(x) for x in tf + tparts)) and not (
                    _site_ok(tree, rel, fn_of.get(id(n))) or reviewed(rel, own.get(id(n)), "gitdir_write", tree)):
                rec(n, "GITDIR_WRITE", _callee(n))
    # reviewed runners: every registered runner of this file is itself reviewed with the process permit
    for r in RUNNERS:
        if r["file"] == rel:
            node = next((f for f in tree.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and f.name == r["function"]), None)
            if node is None or not reviewed(rel, (r["function"], node), "process") or not r.get("reason"):
                rec(node or tree, "RUNNER_UNREVIEWED", r["function"])
    return out


def _forwards_params(fn, exprs: list) -> bool:
    """the call's program / argv / git-argument expressions depend on a parameter of fn (directly or through a local
    bound from one): the function is then a runner and its callers must be checked"""
    a = fn.args
    params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs} | ({a.vararg.arg} if a.vararg else set()) | (
        {a.kwarg.arg} if a.kwarg else set())
    params -= {"self"}
    if not params:
        return False
    hot = taint(fn, params, lambda _: False, broad=True)
    return any(isinstance(x, ast.Name) and x.id in hot for e in exprs for x in ast.walk(e))


def _write_target_exprs(n: ast.Call) -> list:
    fname = _callee(n)
    two = {"rename", "replace", "renames", "link", "symlink", "copy", "copy2", "copyfile", "copytree", "move"}
    if isinstance(n.func, ast.Attribute) and fname in {"write_text", "write_bytes", "touch", "symlink_to",
                                                         "hardlink_to", "mkdir", "unlink"} and not n.args:
        return [n.func.value]
    if isinstance(n.func, ast.Attribute) and fname in {"write_text", "write_bytes", "touch"}:
        return [n.func.value]
    return list(n.args[:2] if fname in two else n.args[:1]) + [k.value for k in n.keywords
                                                                 if k.arg in ("dst", "file", "path", "dir_fd",
                                                                              "src_dir_fd", "dst_dir_fd")]


def git_class_of(n: ast.Call, fc: "FileCtx", root: Path) -> str | None:
    info = process_info(n, fc, root)
    if info is None or info["kind"] != "git":
        return None
    return info["git"]["cls"]


# ------------------------------------------------------------------------------------------------------------------
# Layer 6 (R4 follow-up 2, R4F2-C1): closed-world rules
# ------------------------------------------------------------------------------------------------------------------
IMPORTS = ALLOW["import_policy"]
INTROSPECTION_CALLS = {"vars", "globals", "locals", "dir", "__import__"}
INTROSPECTION_ATTRS = {"__dict__", "__getattribute__", "__builtins__", "__globals__", "__code__", "f_globals",
                       "f_locals", "__setattr__", "__delattr__", "_getframe"}
EXEC_NAMES = {"exec", "eval", "compile"}
ENV_KEYS = set(PROC["env_keys"])
GIT_INTERNAL = (".git", "refs", "packed-refs", "HEAD", "hooks", "config", "logs")


def _pinned_nodes(tree, rel: str) -> set:
    """ids of the nodes inside the pinned backstop functions and pinned statements of this file whose AST hashes are
    current (R4F2-C1(g)); introspection there is reviewed and pinned like the sites"""
    out = set()
    for pin in ALLOW.get("backstop_pins", []):
        if pin["file"] != rel:
            continue
        for st in tree.body:
            name = st.name if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) else (
                st.targets[0].id if isinstance(st, ast.Assign) and len(st.targets) == 1 and
                isinstance(st.targets[0], ast.Name) else None)
            if name == pin["name"] and ast_sha(st) == pin["ast_sha256"]:
                out |= {id(x) for x in ast.walk(st)}
    return out


def _import_ok(rel: str, mod: str, owner, tree) -> str | None:
    """None if importing `mod` is allowed in this file, else the reason"""
    top = mod.split(".")[0]
    forb = next((f for f in IMPORTS["forbidden"] if mod == f or mod.startswith(f + ".")), None)
    if forb is not None:
        if reviewed(rel, owner, "import:" + forb, tree):
            return None
        if any(x["file"] == rel and x["module"] == forb and x.get("reason") and x["ast_sha256"] == ast_sha(tree)
               for x in IMPORTS["module_level_exemptions"]):
            return None
        return f"{mod} is forbidden (R4F2-C1(a)) outside a reviewed function"
    d = rel.split("/")[0]
    if top not in IMPORTS["allowed"].get(d, []):
        return f"{top} is not on the import allowlist of {d}/"
    return None


def _env_ok(e, fc, scope, depth: int = 0) -> bool:
    """an env / env_extra value outside a reviewed runner: None, a fixed module-level environment, dict(<fixed>) or a
    dict literal (optionally unpacking a fixed environment) with allowlisted literal keys, or a local bound only to
    such values (R4F2-C1(d))"""
    if depth > 4:
        return False
    if isinstance(e, ast.Constant) and e.value is None:
        return True
    fixed = {n.targets[0].id for n in fc.tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and len(fc.bindings().get(n.targets[0].id, [])) == 1
             and (isinstance(n.value, ast.Dict) or (isinstance(n.value, ast.Call) and _callee(n.value) == "dict"))}
    if isinstance(e, ast.Name):
        if e.id in fixed:
            return True
        vals = [v for m in ast.walk(scope) if isinstance(m, ast.Assign) for t in m.targets
                if isinstance(t, ast.Name) and t.id == e.id for v in [m.value]]
        if vals:
            return all(_env_ok(v, fc, scope, depth + 1) for v in vals)
        # a parameter of the enclosing function: every call of that function in this file passes an allowed value
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = [a.arg for a in scope.args.posonlyargs + scope.args.args]
            if e.id in params:
                pos = params.index(e.id) - (1 if params[:1] == ["self"] else 0)
                own = owners(fc.tree)
                calls = [c for c in ast.walk(fc.tree) if isinstance(c, ast.Call) and _callee(c) == scope.name]
                got = []
                for c in calls:
                    arg = c.args[pos] if 0 <= pos < len(c.args) else next(
                        (k.value for k in c.keywords if k.arg == e.id), None)
                    if arg is not None:
                        got.append(_env_ok(arg, fc, (own.get(id(c)) or (None, fc.tree))[1], depth + 1))
                return bool(got) and all(got)
        return False
    if isinstance(e, ast.Dict):
        for k, v in zip(e.keys, e.values):
            if k is None:
                if not (isinstance(v, ast.Name) and v.id in fixed):
                    return False
            elif not (isinstance(k, ast.Constant) and k.value in ENV_KEYS):
                return False
        return True
    if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "dict":
        return all(isinstance(a, ast.Name) and a.id in fixed for a in e.args) and all(
            k.arg in ENV_KEYS for k in e.keywords)
    return False


def _forward_findings(tree, rel: str, root: Path, fc) -> list:
    """forwarded operands of reviewed `forwards_operands` functions are validated (R4F2-C1(e)): preceded by a literal
    --end-of-options, passed as the argument of a literal option, or passed literally by every caller"""
    out = []
    own = owners(tree)
    for r in REVIEWED:
        if r["file"] != rel or "forwards_operands" not in r.get("permits", []):
            continue
        node = next((o[1] for o in own.values() if o is not None and o[0] == r["function"]), None)
        if node is None:
            continue
        for param, spec in (r.get("forwarded") or {}).items():
            hows = spec["how"] if isinstance(spec["how"], list) else [spec["how"]]
            how = "+".join(hows)
            hot = taint(node, {param}, lambda _: False, broad=True)
            ok = True
            if set(hows) <= {"end_of_options", "option_argument"}:
                for lst in [x for x in ast.walk(node) if isinstance(x, (ast.List, ast.Tuple))]:
                    eoo = [k for k, el in enumerate(lst.elts) if fold(el, fc.consts) == "--end-of-options"]
                    for k, el in enumerate(lst.elts):
                        if any(isinstance(y, ast.Name) and y.id in hot for y in ast.walk(el)):
                            prev = fold(lst.elts[k - 1], fc.consts) if k else None
                            if not (("end_of_options" in hows and eoo and min(eoo) < k) or
                                    ("option_argument" in hows and prev and prev in spec.get("options", []))):
                                ok = False
            elif hows == ["literal_callers"]:
                fn = node
                pos = [a.arg for a in fn.args.posonlyargs + fn.args.args].index(param)
                allowed = set(spec.get("options", []))
                for q in ast.walk(tree):
                    if isinstance(q, ast.Call) and _callee(q) == r["function"].split(".")[-1]:
                        arg = q.args[pos] if len(q.args) > pos else next(
                            (k.value for k in q.keywords if k.arg == param), None)
                        if arg is None:
                            continue
                        elts = arg.elts if isinstance(arg, (ast.List, ast.Tuple)) else [arg]
                        for x in elts:
                            v = fold(x, fc.consts)
                            if v is None or not (v in allowed or any(o.endswith("=") and v.startswith(o)
                                                                     for o in allowed)):
                                ok = False
            else:
                ok = False
            if not ok:
                out.append({"file": rel, "line": node.lineno, "kind": "FORWARD_UNVALIDATED",
                            "what": f"{r['function']}: {param} ({how})"})
        if not (r.get("forwarded") or {}):
            out.append({"file": rel, "line": node.lineno, "kind": "FORWARD_UNVALIDATED",
                        "what": f"{r['function']}: forwards_operands without a validation spec"})
    return out


def closed_world_rules(tree, rel: str, root: Path) -> list:
    """layer 6 findings for one file (or one parsed `python -c` code string)"""
    fc = FileCtx(tree, rel)
    own = owners(tree)
    pinned = _pinned_nodes(tree, rel.split(":")[0])
    out = []

    def rec(node, kind, what):
        out.append({"file": rel, "line": getattr(node, "lineno", 0), "kind": kind, "what": str(what)[:140]})
    call_funcs = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for n in ast.walk(tree):
        o = own.get(id(n))
        ok_intro = id(n) in pinned or reviewed(rel, o, "introspection", tree)
        # (a) imports
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in n.names] if isinstance(n, ast.Import) else (
                [n.module] + [f"{n.module}.{a.name}" for a in n.names] if n.module and not n.level else
                ["." * n.level + (n.module or "")])
            for mod in mods:
                if mod.startswith("."):
                    rec(n, "IMPORT_UNLISTED", f"relative import {mod}")
                    continue
                why = _import_ok(rel.split(":")[0], mod, o, tree)
                if why and (isinstance(n, ast.Import) or mod == mods[0] or any(
                        mod == f or mod.startswith(f + ".") for f in IMPORTS["forbidden"])):
                    rec(n, "IMPORT_UNLISTED", why)
        # (b) introspection
        if isinstance(n, ast.Attribute) and n.attr in INTROSPECTION_ATTRS and not ok_intro:
            rec(n, "INTROSPECTION", ast.unparse(n)[:60])
        if isinstance(n, ast.Attribute) and n.attr == "modules" and isinstance(n.value, ast.Name) and \
                fc.mod_alias.get(n.value.id) == "sys" and not ok_intro:
            rec(n, "INTROSPECTION", "sys.modules")
        if isinstance(n, ast.Name) and n.id == "__builtins__" and not ok_intro:
            rec(n, "INTROSPECTION", "__builtins__")
        if isinstance(n, ast.Name) and n.id in EXEC_NAMES and isinstance(n.ctx, ast.Load) and not ok_intro and \
                not reviewed(rel, o, "dynamic_exec", tree):
            rec(n, "INTROSPECTION", f"{n.id} referenced")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and not ok_intro:
            c = n.func.id
            if c in INTROSPECTION_CALLS:
                rec(n, "INTROSPECTION", f"{c}()")
            elif c in ("getattr", "setattr", "delattr", "hasattr") and n.args:
                name_lit = len(n.args) > 1 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str)
                on_mod = fc.module_of_expr(n.args[0], root) is not None
                if not name_lit or on_mod:
                    rec(n, "INTROSPECTION", f"{c} with a {'computed name' if not name_lit else 'module target'}")
        # (d) environment
        if isinstance(n, ast.Call):
            info = process_info(n, fc, root)
            if info is not None and not reviewed(rel, o, "process", tree):
                for k in n.keywords:
                    if k.arg in ("env", "env_extra") and not _env_ok(k.value, fc, o[1] if o else tree):
                        rec(n, "ENV_UNLISTED", f"{k.arg}={ast.unparse(k.value)[:60]}")
            txt = ast.unparse(n.func)
            if txt in ("os.putenv", "os.unsetenv") or (isinstance(n.func, ast.Attribute) and
                                                       ast.unparse(n.func.value) == "os.environ" and
                                                       n.func.attr in ("update", "setdefault", "pop", "clear",
                                                                       "popitem", "__setitem__", "__delitem__")):
                rec(n, "ENV_UNLISTED", f"environment mutation {txt}")
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)) and \
                ast.unparse(n.value) == "os.environ":
            rec(n, "ENV_UNLISTED", "os.environ store")
    out += _forward_findings(tree, rel, root, fc) if ":" not in rel else []
    return out


def _unresolved_bad(sfold: str) -> bool:
    """R4F2-C1(f): an unresolved piece directly under the repository root, or a partially resolved piece whose known
    part could complete a git-internal name (e.g. X + 'git', X + 'efs')"""
    comps = [c for c in sfold.split("/") if c]
    for k, c in enumerate(comps):
        if X in c:
            if k and comps[k - 1] == ROOT:
                return True
            known = c.replace(X, "")
            if known and any(known in g for g in GIT_INTERNAL):
                return True
    return False


def file_rules(root: Path) -> list:
    """non-Python files, executable bits, and modules that would shadow a research module (R4F M01, M15)"""
    out = []
    shadow = set()
    for d in ("impl", "verify", "code"):
        shadow |= {p.stem for p in (RNS / d).glob("*.py")}
    for p in sorted(root.rglob("*")):
        if "__pycache__" in p.parts or not p.is_file():
            continue
        rel = str(p.relative_to(root))
        if p.suffix not in SUFFIXES:
            out.append({"file": rel, "line": 0, "kind": "NONPY_FILE", "what": f"suffix {p.suffix!r} not allowed"})
        if p.stat().st_mode & 0o111:
            out.append({"file": rel, "line": 0, "kind": "EXEC_BIT", "what": "an executable file"})
        if p.suffix == ".py" and p.stem in shadow:
            out.append({"file": rel, "line": 0, "kind": "SHADOW_MODULE",
                        "what": f"{p.name} would shadow a research module on sys.path"})
    return out


def allowance_check(tree, lit=None, const=None) -> list:
    """Reasons the allowance does NOT apply (empty list = conditions (a)-(d) hold)."""
    lit = LIT if lit is None else lit
    const = CONST if const is None else const
    why = []
    lits = _literal_nodes(tree, lit)
    if len(lits) != 1:
        why.append(f"(a) the literal occurs {len(lits)} times")
    mod_assign = [n for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                  and isinstance(n.value, ast.Constant) and n.value.value == lit]
    ok_b = (len(mod_assign) == 1 and lits and mod_assign[0].value is lits[0]
            and ((isinstance(mod_assign[0], ast.Assign) and len(mod_assign[0].targets) == 1
                  and isinstance(mod_assign[0].targets[0], ast.Name) and mod_assign[0].targets[0].id == const)
                 or (isinstance(mod_assign[0], ast.AnnAssign) and isinstance(mod_assign[0].target, ast.Name)
                     and mod_assign[0].target.id == const)))
    if not ok_b:
        why.append(f"(b) the literal is not the value of the single module-level {const} assignment")
    stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == const
              and isinstance(n.ctx, (ast.Store, ast.Del))]
    stores += [n for n in ast.walk(tree) if isinstance(n, (ast.Global, ast.Nonlocal)) and const in n.names]
    stores += [n for n in ast.walk(tree) if isinstance(n, ast.arg) and n.arg == const]
    stores += [n for n in ast.walk(tree) if isinstance(n, ast.alias) and (n.asname or n.name) == const]
    if len(stores) != 1:
        why.append(f"(c) {const} is bound {len(stores)} times")
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            a = _atoms(n)
            if a & VERBS and _mentions_marker(a):
                why.append(f"(d) a ref-mutating call names the marker (line {n.lineno})")
                break
    return why


def formal_rules(tree, rel: str, sanctioned: list | None = None, root: Path = FNS) -> list:
    listed = any(rel in n["files"] for n in NAMES)
    fc = FileCtx(tree, rel)
    sanctioned = [] if sanctioned is None else sanctioned
    out = []

    def rec(node, kind, what):
        out.append({"file": rel, "line": getattr(node, "lineno", 0), "kind": kind, "what": str(what)[:100]})

    class_attr_ok = set()
    if listed:
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for st in cls.body:
                if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                        and st.targets[0].id in ("marker_ref", "pending_ref") and isinstance(st.value, ast.Name)
                        and st.value.id in CONSTS):
                    class_attr_ok.add(id(st))
    marker_names = taint(tree, set(MENTION) | set(CONSTS), lambda a: any(l in a for l in LITS) or NSPACE in a)
    grant_names = taint(tree, set(GRANT_NAMES), lambda a: any(g in a for g in GRANT_MARKS))
    fn_of = _func_of(tree)
    own = owners(tree)
    allowed_defs = set()                      # the reviewed definitions of the listed constants (the only token homes)
    homes = {"PRODUCTION_MARKER", "PENDING_REF", "_PROD_NAMESPACE"} if listed else set()
    homes |= {d["constant"] for d in TOKEN_DEFS if d["file"] == rel and d.get("reason")}
    for st in tree.body:
        if isinstance(st, (ast.Assign, ast.AnnAssign)) and isinstance(st.value, ast.Constant) and any(
                t in _targets(x) for x in (st.targets if isinstance(st, ast.Assign) else [st.target]) for t in homes):
            allowed_defs.add(id(st.value))
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            a = _atoms(n)
            fn = fn_of.get(id(n))
            info = process_info(n, fc, root)
            g = info["git"] if info and info["kind"] == "git" else None
            gcls = g["cls"] if g else None
            gverb = {g.get("verb")} - {None} if g else set()
            direct = bool(a & VERBS) and _mentions_marker(a)
            aliased = gcls in ("ref", "opaque", "forbidden") and bool(a & marker_names)
            verbs = (a & VERBS) | (gverb if gcls == "ref" else set())
            if direct or aliased:
                if _site_ok(tree, rel, fn):
                    sanctioned.append({"file": rel, "line": n.lineno, "function": fn.name,
                                       "kind": "EXACTLY_ONCE_SITE", "verbs": sorted(verbs)})
                else:
                    rec(n, "MARKER_MUTATION", sorted(verbs) or gcls)
            if gcls == "ref" and not _site_ok(tree, rel, fn) and not _ref_func_ok(tree, rel, own.get(id(n))):
                rec(n, "REF_MUTATION_UNLISTED", f"{(own.get(id(n)) or ('<module>',))[0]}: {sorted(gverb)}")
            fname = _callee(n)
            fs_write = fs_write_of(n, a, fc)
            writes = fs_write or gcls in ("object", "ref", "opaque")
            ta = (a if gcls in ("object", "ref", "opaque") else write_target_atoms(n)) if writes else set()
            tf, tparts = target_folds(n, fc, (own.get(id(n)) or (None, None))[1]) if fs_write else ([], [])
            if writes and (any(isinstance(x, str) and any(g_ in x for g_ in GRANT_MARKS) for x in list(ta) + tf)
                           or ta & grant_names):
                rec(n, "GRANT_WRITE", fname or "call")
            if fs_write and (any(isinstance(x, str) and (x in ("refs", "packed-refs") or "refs/" in x
                                                          or x.startswith("logs/refs")) for x in ta)
                             or any(_path_bad(x) for x in tf) or any(_path_part_bad(x) for x in tparts)
                             or any(_unresolved_bad(x) for x in tf)) \
                    and not reviewed(rel, own.get(id(n)),
                                                                                "ref_file_write", tree):
                rec(n, "REF_FILE_WRITE", fname)
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            val = n.value
            if val is None:
                continue
            is_alias = (isinstance(val, ast.Name) and val.id in CONSTS) or (
                isinstance(val, ast.Attribute) and val.attr in CONSTS)
            if is_alias and id(n) not in class_attr_ok:
                rec(n, "MARKER_ALIAS", ast.unparse(n)[:100])
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tgts:
                for tt in ast.walk(t):
                    if isinstance(tt, ast.Attribute) and tt.attr in CONSTS and isinstance(tt.ctx, ast.Store):
                        rec(n, "MARKER_REBIND", ast.unparse(n)[:100])
        elif isinstance(n, ast.Constant) and isinstance(n.value, (str, bytes)):
            sval = n.value if isinstance(n.value, str) else n.value.decode("latin-1")   # R4F2-C1(f): bytes too
            for nm in NAMES:
                if nm["literal"] in sval and rel not in nm["files"]:
                    rec(n, "MARKER_ALIAS", f"{nm['constant']} literal outside its listed files")
            if id(n) not in allowed_defs and any(t in sval for t in TOKENS):
                rec(n, "MARKER_TOKEN", "a production ref-name token outside the reviewed definitions")
    return out


def scan(root: Path = FNS) -> dict:
    clear_caches()
    Q.NS = root
    r = Q.scan(root)
    findings, allowed, sanctioned = [], [], []
    for f in r["findings"]:
        nm = next((n for n in NAMES if f["kind"] == "TARGET_PATH" and f["what"] == n["literal"]), None)
        if nm is not None and f["file"] in nm["files"]:
            why = allowance_check(ast.parse((root / f["file"]).read_text()), nm["literal"], nm["constant"])
            if not why:
                allowed.append(dict(f, allowance=f"SCANNER_ALLOWANCE_P309 (a)-(e) hold for {nm['constant']}"))
                continue
            f = dict(f, allowance_refused=why)
        findings.append(f)
    for f in r["sanctioned_refusal_test_findings"]:
        if f["kind"] == "TARGET_PATH" and any(l in f.get("what", "") for l in LITS):
            findings.append(dict(f, note="exactly-once ref literal in a refusal-test file: not covered by the allowance"))
    formal_controls = []
    findings.extend(file_rules(root))

    def recurse(code: str, label: str, depth=[0]) -> list:            # a `python -c` / exec code string
        if depth[0] > 3:
            return [{"file": label, "line": 0, "kind": "UNPARSEABLE_CODE", "what": "nesting too deep"}]
        try:
            t = ast.parse(code)
        except SyntaxError:
            return [{"file": label, "line": 0, "kind": "UNPARSEABLE_CODE", "what": code[:80]}]
        depth[0] += 1
        try:
            return (formal_rules(t, label, [], root) + process_rules(t, label, root, recurse)
                    + closed_world_rules(t, label, root))
        finally:
            depth[0] -= 1
    for p in sorted(root.rglob("*.py")):                 # R4F M01: no file is skipped by its name
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(root))
        src = p.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            findings.append({"file": rel, "line": 0, "kind": "UNPARSEABLE"})
            continue
        site_hits: list = []
        fs = (formal_rules(tree, rel, site_hits, root) + process_rules(tree, rel, root, recurse)
              + closed_world_rules(tree, rel, root))
        if Q.CONTROL_MARK in src:
            if rel not in CONTROL_FILES or Q.CONTROL_MARK not in src[:400]:
                findings.append({"file": rel, "line": 0, "kind": "CONTROL_MARK_UNLISTED",
                                 "what": "a planted-control mark in a file that is not a listed planted control"})
                continue
            formal_controls.append({"file": rel, "fired": sorted({x["kind"] for x in fs})})
            continue
        findings.extend(fs)
        sanctioned.extend(site_hits)
    formal_ok = any(FORMAL_KINDS <= set(c["fired"]) for c in formal_controls) and any(
        PROCESS_KINDS <= set(c["fired"]) for c in formal_controls)
    verdict = "PASS" if (not findings and r["control_fires_all_kinds"] and formal_ok) else "FAIL"
    return {"files_scanned": r["files_scanned"], "findings": findings, "allowed_marker_name": allowed,
            "sanctioned_exactly_once_sites": sanctioned,
            "suppressed_listed": r["suppressed_listed"],
            "sanctioned_refusal_test_findings": r["sanctioned_refusal_test_findings"],
            "planted_controls": r["planted_controls"], "control_fires_all_kinds": r["control_fires_all_kinds"],
            "formal_planted_controls": formal_controls, "formal_controls_fire_all_kinds": formal_ok,
            "allowance_config_sha256": hashlib.sha256(
                (FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_bytes()).hexdigest(),
            "verdict": verdict}


if __name__ == "__main__":
    res = scan(FNS)
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
