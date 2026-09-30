"""Maintain `ref_mutation_functions` in config/SCANNER_ALLOWANCE_P309.json (owner D5: every ref-moving path is reviewed
and pinned by AST hash).

  python3 code/p309_scan_pins.py --list      every function with a ref-moving git call, and whether it is listed/current
  python3 code/p309_scan_pins.py --refresh   recompute the AST sha256 of the ALREADY-LISTED functions (pre-freeze only)

It never adds an entry: a new ref-moving function is a finding (REF_MUTATION_UNLISTED) until a reviewed entry with a
reason is written by hand.  It never touches `exactly_once_sites`: the two owner-ratified sites keep the hashes the
owner ratified, and any change to them is a new decision.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_scan as S  # noqa: E402

CONFIG = FNS / "config" / "SCANNER_ALLOWANCE_P309.json"


def inventory(root: Path = FNS) -> dict:
    out = {}
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" in p.parts or p.name == "q309_guard.py":
            continue
        rel = str(p.relative_to(root))
        tree = ast.parse(p.read_text())
        own = S.owners(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and S.ref_verbs_of(n):
                o = own.get(id(n))
                key = (rel, o[0] if o else "<module>")
                out.setdefault(key, {"verbs": set(), "ast_sha256": S.ast_sha(o[1]) if o else None})
                out[key]["verbs"] |= S.ref_verbs_of(n)
    return out


if __name__ == "__main__":
    cfg = json.loads(CONFIG.read_text())
    inv = inventory()
    listed = {(r["file"], r["function"]): r for r in cfg["ref_mutation_functions"]}
    if "--refresh" in sys.argv:
        for key, r in listed.items():
            if key in inv:
                r["ast_sha256"] = inv[key]["ast_sha256"]
        CONFIG.write_text(json.dumps(cfg, indent=1) + "\n")
    sites = {(s["file"], s["function"]) for s in cfg["exactly_once_sites"]}
    for key, v in sorted(inv.items()):
        state = ("SITE" if key in sites else "control" if key[0] in cfg["planted_control_files"] else
                 "listed, current" if key in listed and listed[key]["ast_sha256"] == v["ast_sha256"] else
                 "listed, STALE HASH" if key in listed else "NOT LISTED")
        print(f"{key[0]} {key[1]} {sorted(v['verbs'])}: {state}")
    for key in sorted(set(listed) - set(inv)):
        print(f"{key[0]} {key[1]}: listed but has no ref-moving call (remove the entry)")
