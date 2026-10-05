#!/usr/bin/env python3
"""Print a compact structural view of a JSON file: peek.py FILE [maxdepth] [maxstr]"""
import json
import sys

path = sys.argv[1]
maxd = int(sys.argv[2]) if len(sys.argv) > 2 else 3
maxs = int(sys.argv[3]) if len(sys.argv) > 3 else 160


def show(x, d=0, key="$"):
    pad = "  " * d
    if isinstance(x, dict):
        if d >= maxd:
            print(f"{pad}{key}: {{...{len(x)} keys: {list(x)[:12]}}}")
            return
        print(f"{pad}{key}: {{")
        for k, v in x.items():
            show(v, d + 1, k)
        print(f"{pad}}}")
    elif isinstance(x, list):
        if d >= maxd or (x and not isinstance(x[0], (dict, list)) and len(json.dumps(x)) < maxs):
            print(f"{pad}{key}: {json.dumps(x)[:maxs]} (len {len(x)})")
            return
        print(f"{pad}{key}: [ (len {len(x)})")
        for i, v in enumerate(x[:40]):
            show(v, d + 1, f"[{i}]")
        print(f"{pad}]")
    else:
        print(f"{pad}{key}: {json.dumps(x)[:maxs]}")


show(json.load(open(path)))
