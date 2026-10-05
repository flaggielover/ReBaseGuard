"""Byte and AST identity of every top-level node of a Python module between two versions.

usage: ast_full.py --old OLD_FILE --new NEW_FILE --pinned-json ALLOWANCE_JSON --rel code/NAME.py --out OUT.json
          [--intended a,b,c]

For every top-level function and class: AST sha256 (ast.dump) and source-bytes sha256 (exact source segment incl.
decorators) in both versions.  Module-level statements that are not functions or classes are compared in order as
one AST list and also listed individually.  Pinned = the scanner allowance's process_policy.reviewed_functions for
--rel.  With --intended, every changed/added/removed name must be in that set.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path


def h(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def nodes(src: str):
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    defs, other = {}, []
    for n in tree.body:
        start = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
        seg = "".join(lines[start - 1:n.end_lineno])
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[n.name] = {"ast": h(ast.dump(n)), "bytes": h(seg), "kind": type(n).__name__}
        else:
            other.append({"ast": h(ast.dump(n)), "bytes": h(seg), "line": n.lineno, "src": seg[:120]})
    return defs, other


ap = argparse.ArgumentParser()
for k in ("--old", "--new", "--pinned-json", "--rel", "--out"):
    ap.add_argument(k, required=True)
ap.add_argument("--intended", default="")
a = ap.parse_args()
old_src, new_src = Path(a.old).read_text(), Path(a.new).read_text()
do, oo = nodes(old_src)
dn, on = nodes(new_src)
allow = json.loads(Path(a.pinned_json).read_text())
pinned = sorted({e["function"] for e in allow["process_policy"]["reviewed_functions"] if e.get("file") == a.rel})
common = sorted(set(do) & set(dn))
changed_ast = [f for f in common if do[f]["ast"] != dn[f]["ast"]]
changed_bytes = [f for f in common if do[f]["bytes"] != dn[f]["bytes"]]
added, removed = sorted(set(dn) - set(do)), sorted(set(do) - set(dn))
intended = set(x for x in a.intended.split(",") if x)
res = {
    "old": a.old, "new": a.new, "old_sha256": h(old_src), "new_sha256": h(new_src),
    "defs_old": len(do), "defs_new": len(dn),
    "added": added, "removed": removed,
    "changed_ast": changed_ast, "changed_bytes_only": sorted(set(changed_bytes) - set(changed_ast)),
    "unchanged_byte_identical": sorted(f for f in common if f not in changed_bytes),
    "module_level_statements_old": len(oo), "module_level_statements_new": len(on),
    "module_level_ast_identical": [x["ast"] for x in oo] == [x["ast"] for x in on],
    "module_level_bytes_identical": [x["bytes"] for x in oo] == [x["bytes"] for x in on],
    "module_level_old_only": [x["src"] for x in oo if x["ast"] not in {y["ast"] for y in on}],
    "module_level_new_only": [x["src"] for x in on if x["ast"] not in {y["ast"] for y in oo}],
    "pinned": pinned,
    "pinned_status": {f: ("missing" if f not in dn else
                          "byte_identical" if do.get(f, {}).get("bytes") == dn[f]["bytes"] else
                          "ast_identical" if do.get(f, {}).get("ast") == dn[f]["ast"] else "CHANGED") for f in pinned},
}
res["pinned_all_byte_identical"] = all(v == "byte_identical" for v in res["pinned_status"].values())
if intended:
    touched = set(added) | set(removed) | set(changed_ast) | set(changed_bytes)
    res["intended"] = sorted(intended)
    res["unintended_touched"] = sorted(touched - intended)
    res["intended_untouched"] = sorted(intended - touched)
Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in res.items() if k not in ("unchanged_byte_identical",)}, indent=1, sort_keys=True))
