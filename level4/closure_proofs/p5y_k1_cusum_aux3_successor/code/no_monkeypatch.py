"""PHASE 2/13: a static detector for runtime module patching.

WHAT IT LOOKS FOR
-----------------
Patterns that redirect behaviour by mutating something imported, rather than by
passing it:

  1. `module.attr = value`      assignment to an attribute of an imported module
  2. `setattr(module, ...)`     the same thing spelled dynamically
  3. `sys.modules[...] = ...`   replacing a module in the import table
  4. `globals()[...] = ...`     and `vars(module)[...] = ...`

"Imported module" is decided per file from its own import statements, so
`self.x = y` and `record["k"] = v` are never flagged, and a name that is a local
variable rather than a module is not flagged either.

WHY STATIC
----------
The defect being prevented is exactly the kind that a passing test suite hides:
the predecessor's suite was green while `propagate.refine` was being reassigned
at import time. A source-level check cannot be satisfied by luck of import order.

This module is NOT part of the certifying set: it inspects code, it does not
produce certificates.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import ancestry

PATTERNS = {
    "module_attribute_assignment": "`module.attr = ...` on an imported module",
    "setattr_on_module": "`setattr(module, ...)` on an imported module",
    "sys_modules_assignment": "`sys.modules[...] = ...`",
    "globals_assignment": "`globals()[...] = ...` or `vars(x)[...] = ...`",
}


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # `from x import y` binds y; y may itself be a module
            for a in node.names:
                names.add(a.asname or a.name)
    return names


def scan_source(source: str, where: str) -> list[dict]:
    tree = ast.parse(source)
    modules = _imported_names(tree)
    found: list[dict] = []

    def flag(kind, node, detail):
        found.append({"pattern": kind, "file": where, "line": node.lineno,
                      "detail": detail})

    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                        and t.value.id in modules):
                    flag("module_attribute_assignment", node,
                         f"{t.value.id}.{t.attr}")
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute):
                    v = t.value
                    if (isinstance(v.value, ast.Name) and v.value.id == "sys"
                            and v.attr == "modules"):
                        flag("sys_modules_assignment", node, "sys.modules[...]")
                if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Call)
                        and isinstance(t.value.func, ast.Name)
                        and t.value.func.id in ("globals", "vars")):
                    flag("globals_assignment", node, f"{t.value.func.id}()[...]")
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "setattr" and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id in modules):
            flag("setattr_on_module", node, f"setattr({node.args[0].id}, ...)")
    return found


def scan_path(path: Path) -> list[dict]:
    root = Path(path)
    files = sorted(root.rglob("*.py")) if root.is_dir() else [root]
    out: list[dict] = []
    for f in files:
        rel = str(f.resolve().relative_to(ancestry.ROOT))
        out.extend(scan_source(f.read_text(), rel))
    return out


def scan_namespace() -> dict:
    """This namespace must be clean."""
    findings = scan_path(ancestry.NS)
    return {"namespace": str(ancestry.NS.relative_to(ancestry.ROOT)),
            "clean": not findings, "findings": findings,
            "patterns_checked": PATTERNS}


def scan_predecessor() -> dict:
    """The predecessor must NOT be clean: this is the reproduction control."""
    findings = scan_path(ancestry.CUSUM_NS / "code")
    return {"namespace": str(ancestry.CUSUM_NS.relative_to(ancestry.ROOT)),
            "clean": not findings, "findings": findings}


def main() -> None:
    report = {"schema": "k1.cusum-aux3.monkeypatch-scan.v1",
              "this_namespace": scan_namespace(),
              "predecessor_control": scan_predecessor()}
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["this_namespace"]["clean"] else 1)


if __name__ == "__main__":
    main()
