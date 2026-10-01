"""Firewalled structure reader for pinned consumer code and data (formal campaign p5y_k5_cell309_p309_r1; U2 dependency graph).

  python3 code/code_skeleton.py py   <file.py> [function ...]   -> code skeleton of the named top-level functions (all if none)
  python3 code/code_skeleton.py json <file.json>                -> JSON key paths with value TYPES only

It is used to map which inputs the frozen Stage-2 path reads, without displaying any number of the tail cells:
* Python: docstrings and comments are removed (the AST drops comments; docstring expressions are deleted).
  Every string constant that looks numeric is masked, every float is masked, every numeric argument of a call is
  masked (so no F(a, b) / Fraction("a/b") literal survives), and every int outside 0..24 is masked.  Small integer
  arithmetic coefficients (e.g. the 3, 6, 4 of theorem TC's formulas) are kept: they are formula structure, not data.
* JSON: only key paths and the type of each leaf are printed (list lengths are printed; list items are collapsed to
  the first item's structure).  No value is printed.
Nothing is evaluated or imported from the read file.
"""
from __future__ import annotations

import ast
import json
import re
import sys

NUMERIC_STR = re.compile(r"^\s*[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?(\s*/\s*[-+]?\d+)?\s*$")
MASK = "<num>"


class _Mask(ast.NodeTransformer):
    def __init__(self):
        self.in_call_args = 0

    def visit_Call(self, node):
        node.func = self.visit(node.func)
        self.in_call_args += 1
        node.args = [self.visit(a) for a in node.args]
        node.keywords = [self.visit(k) for k in node.keywords]
        self.in_call_args -= 1
        return node

    def visit_Constant(self, node):
        v = node.value
        if isinstance(v, bool) or v is None:
            return node
        if isinstance(v, str):
            return ast.Name(id=MASK, ctx=ast.Load()) if NUMERIC_STR.match(v) else node
        if isinstance(v, float) or isinstance(v, complex):
            return ast.Name(id=MASK, ctx=ast.Load())
        if isinstance(v, int):
            if self.in_call_args or not (0 <= v <= 24):
                return ast.Name(id=MASK, ctx=ast.Load())
        return node


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree


def py_skeleton(path: str, names: list[str]) -> str:
    tree = _strip_docstrings(ast.parse(open(path, encoding="utf-8").read()))
    tree = _Mask().visit(tree)
    out = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            out.append(ast.unparse(node))
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not names or node.name in names:
                out.append(ast.unparse(node))
            else:
                out.append(f"# def/class {node.name} (not shown)")
        elif isinstance(node, ast.Assign):
            tg = ", ".join(ast.unparse(t) for t in node.targets)
            out.append(f"{tg} = ..." if names else ast.unparse(node))
    return "\n\n".join(out)


def _shape(x, path, out):
    if isinstance(x, dict):
        for k, v in x.items():
            ks = str(k)
            if NUMERIC_STR.match(ks) and not (ks.isdigit() and int(ks) <= 24):
                ks = "<numkey>"          # a numeric key (e.g. a cell index or a drift) is masked
            _shape(v, f"{path}.{ks}" if path else ks, out)
    elif isinstance(x, list):
        out.append(f"{path}: list[{len(x)}]")
        if x:
            _shape(x[0], path + "[0]", out)
    else:
        out.append(f"{path}: {type(x).__name__}")


def json_shape(path: str) -> str:
    out: list[str] = []
    _shape(json.load(open(path, encoding="utf-8")), "", out)
    return "\n".join(out)


if __name__ == "__main__":
    kind, path, *names = sys.argv[1:]
    print(py_skeleton(path, names) if kind == "py" else json_shape(path))
