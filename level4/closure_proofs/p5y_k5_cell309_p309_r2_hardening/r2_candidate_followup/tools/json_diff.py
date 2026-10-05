"""Structural diff of two JSON files: every leaf path whose value differs (plus added / removed paths).

usage: json_diff.py OLD NEW OUT
"""
import hashlib
import json
import sys
from pathlib import Path


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


old_b, new_b = Path(sys.argv[1]).read_bytes(), Path(sys.argv[2]).read_bytes()
o, n = dict(leaves(json.loads(old_b))), dict(leaves(json.loads(new_b)))
res = {"old_sha256": hashlib.sha256(old_b).hexdigest(), "new_sha256": hashlib.sha256(new_b).hexdigest(),
       "leaves_old": len(o), "leaves_new": len(n),
       "changed": [{"path": k, "old": o[k], "new": n[k]} for k in o if k in n and o[k] != n[k]],
       "added": sorted(set(n) - set(o)), "removed": sorted(set(o) - set(n))}
old_lines, new_lines = old_b.decode().splitlines(), new_b.decode().splitlines()
res["text_lines_changed"] = sum(1 for a, b in zip(old_lines, new_lines) if a != b) + abs(len(old_lines) - len(new_lines))
Path(sys.argv[3]).write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
