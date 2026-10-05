"""Static check: does every mutant anchor of r2's tests/test_p309_static_controls.py occur exactly once in a
package's files?  The test module is never imported (no ledger write); its MUTANTS list is evaluated from the AST with
only its own module-level string constants in scope.

usage: anchor_check.py <package namespace dir> <out.json>
"""
import ast
import json
import sys
from pathlib import Path

ns, out = Path(sys.argv[1]), Path(sys.argv[2])
test = ns / "tests" / "test_p309_static_controls.py"
tree = ast.parse(test.read_text())
consts, mutants_node = {}, None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name == "MUTANTS":
            mutants_node = node.value
            continue
        try:
            v = ast.literal_eval(node.value)
        except Exception:
            continue
        if isinstance(v, str):
            consts[name] = v
mutants = eval(compile(ast.Expression(mutants_node), str(test), "eval"), {"__builtins__": {}}, consts)
rows = []
for name, check, rel, old, new in mutants:
    src = (ns / rel).read_text()
    rows.append({"mutant": name, "check": check, "file": rel, "anchor_count": src.count(old)})
res = {"namespace": str(ns), "mutants": rows, "all_anchors_exactly_once": all(r["anchor_count"] == 1 for r in rows)}
out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
for r in rows:
    print(f"{r['anchor_count']}  {r['mutant']}")
print("all_anchors_exactly_once:", res["all_anchors_exactly_once"])
