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
LIT = ALLOW["marker_literal"]
CONST = ALLOW["constant_name"]
NSPACE = ALLOW["production_ref_namespace"]
VERBS = set(ALLOW["mutating_git_verbs"])
GRANT_MARKS = tuple(ALLOW["production_grant_markers"]) + ("_PROD_GRANT_PATH",)
WRITE_FUNCS = {"write_text", "write_bytes", "writelines"}
GIT_WRITE_VERBS = {"add", "commit", "commit-tree", "hash-object", "update-index", "mv", "checkout", "apply", "am",
                   "stash", "merge", "cherry-pick", "revert", "reset", "restore"}
FORMAL_KINDS = {"MARKER_MUTATION", "MARKER_ALIAS", "MARKER_REBIND", "GRANT_WRITE"}


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
    return any(a == CONST or a == "_PROD_NAMESPACE" or (isinstance(a, str) and (LIT in a or NSPACE in a))
               for a in atoms)


def _literal_nodes(tree) -> list:
    return [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and LIT in n.value]


def allowance_check(tree) -> list:
    """Reasons the allowance does NOT apply (empty list = conditions (a)-(d) hold)."""
    why = []
    lits = _literal_nodes(tree)
    if len(lits) != 1:
        why.append(f"(a) the literal occurs {len(lits)} times")
    mod_assign = [n for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                  and isinstance(n.value, ast.Constant) and n.value.value == LIT]
    ok_b = (len(mod_assign) == 1 and lits and mod_assign[0].value is lits[0]
            and ((isinstance(mod_assign[0], ast.Assign) and len(mod_assign[0].targets) == 1
                  and isinstance(mod_assign[0].targets[0], ast.Name) and mod_assign[0].targets[0].id == CONST)
                 or (isinstance(mod_assign[0], ast.AnnAssign) and isinstance(mod_assign[0].target, ast.Name)
                     and mod_assign[0].target.id == CONST)))
    if not ok_b:
        why.append("(b) the literal is not the value of the single module-level PRODUCTION_MARKER assignment")
    stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == CONST
              and isinstance(n.ctx, (ast.Store, ast.Del))]
    stores += [n for n in ast.walk(tree) if isinstance(n, (ast.Global, ast.Nonlocal)) and CONST in n.names]
    stores += [n for n in ast.walk(tree) if isinstance(n, ast.arg) and n.arg == CONST]
    stores += [n for n in ast.walk(tree) if isinstance(n, ast.alias) and (n.asname or n.name) == CONST]
    if len(stores) != 1:
        why.append(f"(c) PRODUCTION_MARKER is bound {len(stores)} times")
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            a = _atoms(n)
            if a & VERBS and _mentions_marker(a):
                why.append(f"(d) a ref-mutating call names the marker (line {n.lineno})")
                break
    return why


def formal_rules(tree, rel: str) -> list:
    listed = rel in ALLOW["files"]
    out = []

    def rec(node, kind, what):
        out.append({"file": rel, "line": getattr(node, "lineno", 0), "kind": kind, "what": str(what)[:100]})

    class_attr_ok = set()
    if listed:
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for st in cls.body:
                if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                        and st.targets[0].id == "marker_ref" and isinstance(st.value, ast.Name)
                        and st.value.id == CONST):
                    class_attr_ok.add(id(st))
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            a = _atoms(n)
            if a & VERBS and _mentions_marker(a):
                rec(n, "MARKER_MUTATION", sorted(a & VERBS))
            fname = n.func.attr if isinstance(n.func, ast.Attribute) else (
                n.func.id if isinstance(n.func, ast.Name) else "")
            writes = fname in WRITE_FUNCS or (fname == "open" and any(
                isinstance(x, ast.Constant) and isinstance(x.value, str) and set(x.value) & set("wax")
                for x in list(n.args[1:2]) + [k.value for k in n.keywords if k.arg == "mode"])) or bool(
                a & GIT_WRITE_VERBS)
            if writes and any(isinstance(x, str) and any(g in x for g in GRANT_MARKS) for x in a):
                rec(n, "GRANT_WRITE", fname or "call")
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            val = n.value
            if val is None:
                continue
            is_alias = (isinstance(val, ast.Name) and val.id == CONST) or (
                isinstance(val, ast.Attribute) and val.attr == CONST)
            if is_alias and id(n) not in class_attr_ok:
                rec(n, "MARKER_ALIAS", ast.unparse(n)[:100])
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tgts:
                for tt in ast.walk(t):
                    if isinstance(tt, ast.Attribute) and tt.attr == CONST and isinstance(tt.ctx, ast.Store):
                        rec(n, "MARKER_REBIND", ast.unparse(n)[:100])
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and LIT in n.value and not listed:
            rec(n, "MARKER_ALIAS", "marker literal outside the listed files")
    return out


def scan(root: Path = FNS) -> dict:
    Q.NS = root
    r = Q.scan(root)
    findings, allowed = [], []
    for f in r["findings"]:
        if f["kind"] == "TARGET_PATH" and f["what"] == LIT and f["file"] in ALLOW["files"]:
            why = allowance_check(ast.parse((root / f["file"]).read_text()))
            if not why:
                allowed.append(dict(f, allowance="SCANNER_ALLOWANCE_P309 (a)-(e) hold"))
                continue
            f = dict(f, allowance_refused=why)
        findings.append(f)
    for f in r["sanctioned_refusal_test_findings"]:
        if f["kind"] == "TARGET_PATH" and LIT in f.get("what", ""):
            findings.append(dict(f, note="marker literal in a refusal-test file: not covered by the allowance"))
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
        fs = formal_rules(tree, rel)
        if Q.CONTROL_MARK in src[:400]:
            formal_controls.append({"file": rel, "fired": sorted({x["kind"] for x in fs})})
            continue
        findings.extend(fs)
    formal_ok = any(FORMAL_KINDS <= set(c["fired"]) for c in formal_controls)
    verdict = "PASS" if (not findings and r["control_fires_all_kinds"] and formal_ok) else "FAIL"
    return {"files_scanned": r["files_scanned"], "findings": findings, "allowed_marker_name": allowed,
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
