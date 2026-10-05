#!/usr/bin/env python3
"""Which top-level functions of a module changed between two versions (by AST), and which of them r2's scanner pins.

  python3 r2h_ast_diff.py --repo REPO --old-commit C --path REL --new-file FILE --allowance REL_TO_ALLOWANCE --out F

Reports: functions added, removed and changed (ast.dump sha256), and for each changed function whether r2's scanner
allowance pins it (process_policy.reviewed_functions).  A hardening must change no pinned function.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


def funcs(src: str) -> dict:
    return {n.name: hashlib.sha256(ast.dump(n).encode()).hexdigest() for n in ast.parse(src).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("--repo", "--old-commit", "--path", "--new-file", "--allowance", "--out"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    old = subprocess.run(["git", "-C", a.repo, "show", f"{a.old_commit}:{a.path}"], capture_output=True, text=True,
                         check=True).stdout
    new = Path(a.new_file).read_text()
    fo, fn = funcs(old), funcs(new)
    allow = json.loads(subprocess.run(["git", "-C", a.repo, "show", f"{a.old_commit}:{a.allowance}"],
                                      capture_output=True, text=True, check=True).stdout)
    rel = "code/" + Path(a.path).name
    pinned = {e["function"] for e in allow["process_policy"]["reviewed_functions"] if e.get("file") == rel}
    changed = sorted(f for f in fo if f in fn and fo[f] != fn[f])
    res = {"schema": "P309_R2H_AST_DIFF/1", "old": f"{a.old_commit}:{a.path}",
           "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
           "added": sorted(set(fn) - set(fo)), "removed": sorted(set(fo) - set(fn)), "changed": changed,
           "pinned_functions": sorted(pinned), "pinned_and_changed": sorted(set(changed) & pinned),
           "pinned_unchanged": sorted(f for f in pinned if fo.get(f) == fn.get(f))}
    res["ok"] = not res["removed"] and not res["pinned_and_changed"]
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
