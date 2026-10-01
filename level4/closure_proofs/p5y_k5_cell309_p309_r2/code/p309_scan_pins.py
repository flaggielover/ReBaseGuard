"""Maintain the AST-pinned lists of config/SCANNER_ALLOWANCE_P309.json (owner D5; R4 follow-up F1(b)/(c)):
`ref_mutation_functions`, `process_policy.reviewed_functions` and `t7_exemptions`.

  python3 code/p309_scan_pins.py --list      every function with a ref-moving git call, and the state of every
                                             listed entry (current / STALE HASH / missing)
  python3 code/p309_scan_pins.py --refresh   recompute the AST sha256 of the ALREADY-LISTED entries (pre-freeze only)

It never adds an entry: an unlisted function is a scanner finding until a reviewed entry with a reason is written by
hand.  It never touches `exactly_once_sites`: the two owner-ratified sites keep the hashes the owner ratified, and any
change to them is a new decision.  No file is skipped by its name (R4F M01).
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


def _files(root: Path):
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" not in p.parts:
            yield str(p.relative_to(root)), p


def inventory(root: Path = FNS) -> dict:
    """(file, function) -> {verbs, ast_sha256} for every function with a ref-class git call"""
    out = {}
    for rel, p in _files(root):
        tree = ast.parse(p.read_text())
        fc = S.FileCtx(tree, rel)
        own = S.owners(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                info = S.process_info(n, fc, root)
                if info and info["kind"] == "git" and info["git"]["cls"] == "ref":
                    o = own.get(id(n))
                    key = (rel, o[0] if o else "<module>")
                    out.setdefault(key, {"verbs": set(), "ast_sha256": S.ast_sha(o[1]) if o else None})
                    out[key]["verbs"].add(info["git"].get("verb"))
    return out


def owner_hash(root: Path, rel: str, qual: str) -> str | None:
    """the AST sha256 of the unique outermost function `qual` of a file (None if absent or not unique)"""
    p = root / rel
    if not p.exists():
        return None
    tree = ast.parse(p.read_text())
    hits = {id(o[1]): o[1] for o in S.owners(tree).values() if o is not None and o[0] == qual}
    return S.ast_sha(next(iter(hits.values()))) if len(hits) == 1 else None


def module_hash(root: Path, rel: str) -> str | None:
    p = root / rel
    return S.ast_sha(ast.parse(p.read_text())) if p.exists() else None


def entries(cfg: dict):
    """(list name, entry, current hash) for every AST-pinned entry except the owner-ratified sites"""
    for r in cfg["ref_mutation_functions"]:
        yield "ref_mutation_functions", r, owner_hash(FNS, r["file"], r["function"])
    for r in cfg["process_policy"]["reviewed_functions"]:
        yield "reviewed_functions", r, owner_hash(FNS, r["file"], r["function"])
    for r in cfg.get("t7_exemptions", []):
        yield "t7_exemptions", r, module_hash(FNS, r["file"])
    for r in cfg.get("import_policy", {}).get("module_level_exemptions", []):
        yield "module_level_exemptions", r, module_hash(FNS, r["file"])


if __name__ == "__main__":
    cfg = json.loads(CONFIG.read_text())
    if "--refresh" in sys.argv:
        changed = []
        for name, r, h in entries(cfg):
            if h is not None and r.get("ast_sha256") != h:
                changed.append(f"{name}: {r['file']} {r.get('function', '<module>')}")
                r["ast_sha256"] = h
        CONFIG.write_text(json.dumps(cfg, indent=1, ensure_ascii=False) + "\n")
        print("refreshed:", json.dumps(changed, indent=1))
    listed = {(r["file"], r["function"]) for r in cfg["ref_mutation_functions"]}
    sites = {(s["file"], s["function"]) for s in cfg["exactly_once_sites"]}
    bad = []
    inv = inventory(FNS)
    for key, v in sorted(inv.items()):
        state = ("SITE" if key in sites else "control" if key[0] in cfg["planted_control_files"] else
                 "listed" if key in listed else "NOT LISTED")
        line = f"ref-class: {key[0]} {key[1]} {sorted(x for x in v['verbs'] if x)}: {state}"
        print(line)
        bad += [line] if state == "NOT LISTED" else []
    for name, r, h in entries(cfg):
        state = "missing" if h is None else "current" if r.get("ast_sha256") == h else "STALE HASH"
        if name == "ref_mutation_functions" and (r["file"], r["function"]) not in inv:
            state += ", but it has no ref-class git call (remove the entry)"
        line = f"{name}: {r['file']} {r.get('function', '<module>')}: {state}"
        print(line)
        bad += [line] if state != "current" else []
    print(f"P309 SCAN PINS: {'all current' if not bad else str(len(bad)) + ' NOT CURRENT'}")
    sys.exit(1 if bad and "--refresh" not in sys.argv else 0)
