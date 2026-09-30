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
REF_VERBS = set(ALLOW["ref_mutation_verbs"])
GIT_RUNNERS = set(ALLOW["git_runner_names"])
REF_FUNCS = ALLOW["ref_mutation_functions"]
CONTROL_FILES = set(ALLOW["planted_control_files"])
TOKEN_DEFS = ALLOW["token_definitions"]
FS_WRITE_FUNCS = {"mkdir", "makedirs", "rename", "replace", "renames", "link", "symlink", "unlink", "remove", "rmtree",
                  "copy", "copy2", "copyfile", "copytree", "move", "touch", "write_text", "write_bytes", "writelines"}
WRITE_FUNCS = {"write_text", "write_bytes", "writelines"}
GIT_WRITE_VERBS = {"add", "commit", "commit-tree", "hash-object", "update-index", "mv", "checkout", "apply", "am",
                   "stash", "merge", "cherry-pick", "revert", "reset", "restore"}
FORMAL_KINDS = {"MARKER_MUTATION", "MARKER_ALIAS", "MARKER_REBIND", "GRANT_WRITE", "REF_MUTATION_UNLISTED",
                "MARKER_TOKEN", "REF_FILE_WRITE"}


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


def ast_sha(fn) -> str:
    import hashlib
    return hashlib.sha256(ast.dump(fn).encode()).hexdigest()


def _unique_module_def(tree, fn) -> bool:
    """fn is a module-level def and the only def of that name anywhere in the file"""
    same = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fn.name]
    return fn in tree.body and len(same) == 1


def _site_ok(tree, rel: str, fn) -> bool:
    if fn is None or not _unique_module_def(tree, fn):
        return False
    return any(s["file"] == rel and s["function"] == fn.name and s["ast_sha256"] == ast_sha(fn) for s in SITES)


def owners(tree) -> dict:
    """node id -> (qualified name, node) of the OUTERMOST enclosing function: `func` at module level, or
    `Class.method` for a method of a module-level class.  Nested functions and lambdas belong to their owner, whose
    AST hash covers them."""
    out = {}

    def walk(n, owner, cls):
        for ch in ast.iter_child_nodes(n):
            o = owner
            if owner is None and isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                o = (f"{cls}.{ch.name}" if cls else ch.name, ch)
            out[id(ch)] = o
            walk(ch, o, ch.name if (owner is None and cls is None and isinstance(ch, ast.ClassDef)) else cls)
    walk(tree, None, None)
    return out


def _ref_func_ok(tree, rel: str, owner) -> bool:
    if owner is None:
        return False
    qual, node = owner
    same = [o for o in owners(tree).values() if o is not None and o[0] == qual and o[1] is not node]
    if same:
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


def ref_verbs_of(n: ast.Call) -> set:
    """the ref-moving git verbs of a git-runner call (positional arguments only; `errors="replace"` is not a verb)"""
    if _callee(n) not in GIT_RUNNERS:
        return set()
    pos = _positional_strings(n)
    if _callee(n) in ("run", "Popen", "check_output", "check_call", "call") and not any(
            x == "git" or x.endswith("/git") for x in pos):
        return set()
    return set(pos) & REF_VERBS


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


def taint(tree, seeds: set, lit_test) -> set:
    """flow-insensitive alias closure over VALUES (R4 NB1): a name becomes marker-bearing when it is bound -- directly,
    element-wise through tuples, as a loop/with/walrus target, as the parameter receiving an in-module call argument,
    or as a function whose return value is such a value -- to a value-like expression built from a seed name, an
    already marker-bearing name, or a literal accepted by lit_test.  Objects that merely CONTAIN such a value (an
    execution context, a constructor result) are not marker-bearing; their marker attributes are seeds themselves."""
    tainted = set(seeds)
    funcs = {f.name: f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def hot(expr) -> bool:
        names = _value_names(expr)
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


def git_write_verbs_of(n: ast.Call) -> set:
    """object/index-writing git verbs of a git-runner call (positional arguments only)"""
    if _callee(n) not in GIT_RUNNERS:
        return set()
    pos = _positional_strings(n)
    if _callee(n) in ("run", "Popen", "check_output", "check_call", "call") and not any(
            x == "git" or x.endswith("/git") for x in pos):
        return set()
    return set(pos) & (GIT_WRITE_VERBS | REF_VERBS)


def write_target_atoms(n: ast.Call) -> set:
    """the atoms of the PATH a write call writes (not of the bytes written): the receiver of a Path method, the first
    argument of open / os.* / shutil.* (both paths for rename, replace, link, copy, move); for a git write, the call."""
    fname = _callee(n)
    if git_write_verbs_of(n):
        return _atoms(n)
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


def fs_write_of(n: ast.Call, atoms: set) -> bool:
    fname = _callee(n)
    if fname in FS_WRITE_FUNCS:
        return True
    if fname == "open" and isinstance(n.func, ast.Name):      # builtin open with a writing mode
        return any(isinstance(x, ast.Constant) and isinstance(x.value, str) and set(x.value) & set("wax+")
                   for x in list(n.args[1:2]) + [k.value for k in n.keywords if k.arg == "mode"])
    if fname == "open":                                        # os.open with creating/writing flags
        return bool({"O_CREAT", "O_WRONLY", "O_RDWR", "O_APPEND", "O_TRUNC"} & atoms)
    return False


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


def formal_rules(tree, rel: str, sanctioned: list | None = None) -> list:
    listed = any(rel in n["files"] for n in NAMES)
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
            direct = bool(a & VERBS) and _mentions_marker(a)
            aliased = bool(ref_verbs_of(n)) and bool(a & marker_names)
            verbs = (a & VERBS) | ref_verbs_of(n)
            if direct or aliased:
                if _site_ok(tree, rel, fn):
                    sanctioned.append({"file": rel, "line": n.lineno, "function": fn.name,
                                       "kind": "EXACTLY_ONCE_SITE", "verbs": sorted(verbs)})
                else:
                    rec(n, "MARKER_MUTATION", sorted(verbs))
            rv = ref_verbs_of(n)
            if rv and not _site_ok(tree, rel, fn) and not _ref_func_ok(tree, rel, own.get(id(n))):
                rec(n, "REF_MUTATION_UNLISTED", f"{(own.get(id(n)) or ('<module>',))[0]}: {sorted(rv)}")
            fname = _callee(n)
            fs_write = fs_write_of(n, a)
            writes = fs_write or bool(git_write_verbs_of(n))
            ta = write_target_atoms(n) if writes else set()
            if writes and (any(isinstance(x, str) and any(g in x for g in GRANT_MARKS) for x in ta) or ta & grant_names):
                rec(n, "GRANT_WRITE", fname or "call")
            if fs_write and any(isinstance(x, str) and (x in ("refs", "packed-refs") or "refs/" in x
                                                        or x.startswith("logs/refs")) for x in ta):
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
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            for nm in NAMES:
                if nm["literal"] in n.value and rel not in nm["files"]:
                    rec(n, "MARKER_ALIAS", f"{nm['constant']} literal outside its listed files")
            if id(n) not in allowed_defs and any(t in n.value for t in TOKENS):
                rec(n, "MARKER_TOKEN", "a production ref-name token outside the reviewed definitions")
    return out


def scan(root: Path = FNS) -> dict:
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
    for p in sorted(root.rglob("*.py")):
        if p.name == "q309_guard.py":
            continue
        rel = str(p.relative_to(root))
        src = p.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            findings.append({"file": rel, "line": 0, "kind": "UNPARSEABLE"})
            continue
        site_hits: list = []
        fs = formal_rules(tree, rel, site_hits)
        if Q.CONTROL_MARK in src:
            if rel not in CONTROL_FILES or Q.CONTROL_MARK not in src[:400]:
                findings.append({"file": rel, "line": 0, "kind": "CONTROL_MARK_UNLISTED",
                                 "what": "a planted-control mark in a file that is not a listed planted control"})
                continue
            formal_controls.append({"file": rel, "fired": sorted({x["kind"] for x in fs})})
            continue
        findings.extend(fs)
        sanctioned.extend(site_hits)
    formal_ok = any(FORMAL_KINDS <= set(c["fired"]) for c in formal_controls)
    verdict = "PASS" if (not findings and r["control_fires_all_kinds"] and formal_ok) else "FAIL"
    return {"files_scanned": r["files_scanned"], "findings": findings, "allowed_marker_name": allowed,
            "sanctioned_exactly_once_sites": sanctioned,
            "suppressed_listed": r["suppressed_listed"],
            "sanctioned_refusal_test_findings": r["sanctioned_refusal_test_findings"],
            "planted_controls": r["planted_controls"], "control_fires_all_kinds": r["control_fires_all_kinds"],
            "formal_planted_controls": formal_controls, "formal_controls_fire_all_kinds": formal_ok,
            "allowance_config_sha256": __import__("hashlib").sha256(
                (FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_bytes()).hexdigest(),
            "verdict": verdict}


if __name__ == "__main__":
    res = scan(FNS)
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
