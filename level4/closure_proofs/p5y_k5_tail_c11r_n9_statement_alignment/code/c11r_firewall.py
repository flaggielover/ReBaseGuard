"""C11R Repair C -- the original-value firewall, proved by AST.

The six original magnitudes may enter this campaign at exactly two places: c11r_table.py, which
extracts them into a quarantine artifact, and c11r_compare.py, which reads them only after the
independent outputs are sealed. Every other module -- anything that can influence candidate
selection, depth selection, qualification, certification or gate logic -- must be unable to load
them.

Revision 1 had two defects here. Its M03 detector fired on the literal "REGISTRY_C2.json" inside a
call, so c11r_screen.py read the original constants through the Phase 1 table undetected and
printed them (erratum E8). And a substring check cannot tell a docstring that MENTIONS the
registry from code that LOADS it. This scanner distinguishes three things:

  PROSE     a string in a docstring, a print, or any value that never reaches a loader;
  SEMANTIC  a string naming an artifact, used as a label or schema reference, never loaded;
  LOAD      a loader call -- load, read_text, read_bytes, open, json.load, blob_at -- whose
            argument or receiver carries a protected artifact name, directly or through a
            variable assignment (taint propagated to a fixpoint), or a call to a function that
            itself performs such a load, in this module or in another campaign module.

It never loads a magnitude itself. The value-based leak check lives in c11r_table.py, the one
module that legitimately holds the values; this scanner checks the statement table structurally.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

PROTECTED = ("REGISTRY_C2.json", "C11R_ORIGINAL_MAGNITUDES.json", "C11R_N9_TABLE.json",
             "C11R_COMPARISON.json")
ALLOWED_READERS = frozenset({"c11r_table.py", "c11r_compare.py"})
# Subprocess launch of a magnitude-aware module. The extractor prints no magnitude and its values
# never reach the caller, so launching it is permitted; launching the comparator is not.
FORBIDDEN_SUBPROCESS_TARGETS = ("c11r_compare.py",)
LOADER_ATTRS = frozenset({"load", "read_text", "read_bytes", "open", "blob_at", "loads_file"})
MAGNITUDE_KEYS = frozenset({"magnitudes", "value_float"})


def _is_protected_const(n) -> bool:
    return isinstance(n, ast.Constant) and isinstance(n.value, str) and any(
        p in n.value for p in PROTECTED)


def _names_in(node) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _carries_protected(node, tainted: set[str]) -> bool:
    return any(_is_protected_const(n) for n in ast.walk(node)) or bool(
        _names_in(node) & tainted)


def _docstring_nodes(tree) -> set[int]:
    ids = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(
                    getattr(n.body[0], "value", None), ast.Constant):
                ids.add(id(n.body[0].value))
    return ids


def _call_name(call: ast.Call) -> tuple[str | None, str | None]:
    """(receiver-module alias or None, function/attribute name)."""
    f = call.func
    if isinstance(f, ast.Name):
        return None, f.id
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else None
        return base, f.attr
    return None, None


def analyse_source(src: str, name: str, *, foreign_loaders: dict[str, set[str]] | None = None
                   ) -> dict:
    """Classify every protected reference in one module's source."""
    tree = ast.parse(src)
    doc_ids = _docstring_nodes(tree)
    foreign_loaders = foreign_loaders or {}

    # module aliases: `import c11r_compare as K` -> {"K": "c11r_compare"}
    aliases = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                aliases[a.asname or a.name.split(".")[0]] = a.name.split(".")[0]

    # taint: names assigned from anything carrying a protected artifact name
    tainted: set[str] = set()
    changed = True
    while changed:
        changed = False
        for n in ast.walk(tree):
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                val = n.value
                if val is None or not _carries_protected(val, tainted):
                    continue
                tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in tgts:
                    for nm in _names_in(t):
                        if nm not in tainted:
                            tainted.add(nm)
                            changed = True

    loads, subprocess_hits, magnitude_key_reads = [], [], []
    local_loader_funcs: set[str] = set()

    # which local functions perform a protected load (to a fixpoint through local calls)
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef,
                                                                ast.AsyncFunctionDef))}

    def direct_loads(node) -> list[ast.Call]:
        out = []
        for c in ast.walk(node):
            if not isinstance(c, ast.Call):
                continue
            base, attr = _call_name(c)
            if attr in LOADER_ATTRS or (base == "json" and attr == "load"):
                recv = c.func.value if isinstance(c.func, ast.Attribute) else None
                if any(_carries_protected(a, tainted) for a in c.args) or any(
                        _carries_protected(k.value, tainted) for k in c.keywords) or (
                        recv is not None and _carries_protected(recv, tainted)):
                    out.append(c)
        return out

    for fname, fnode in funcs.items():
        if direct_loads(fnode):
            local_loader_funcs.add(fname)
    changed = True
    while changed:
        changed = False
        for fname, fnode in funcs.items():
            if fname in local_loader_funcs:
                continue
            for c in ast.walk(fnode):
                if isinstance(c, ast.Call) and _call_name(c)[0] is None and \
                        _call_name(c)[1] in local_loader_funcs:
                    local_loader_funcs.add(fname)
                    changed = True
                    break

    for c in direct_loads(tree):
        loads.append({"kind": "direct", "line": c.lineno, "call": ast.unparse(c)[:120]})
    for c in ast.walk(tree):
        if not isinstance(c, ast.Call):
            continue
        base, attr = _call_name(c)
        if base is not None and base in aliases:
            mod = aliases[base]
            if attr in foreign_loaders.get(mod, set()):
                loads.append({"kind": "via_other_module", "line": c.lineno,
                              "call": ast.unparse(c)[:120], "module": mod})
        if base == "subprocess" or attr in ("run", "Popen", "check_output", "call"):
            for sub in ast.walk(c):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and any(
                        t in sub.value for t in FORBIDDEN_SUBPROCESS_TARGETS):
                    subprocess_hits.append({"line": c.lineno, "call": ast.unparse(c)[:120]})
    for n in ast.walk(tree):
        key = None
        # only a LOAD reads a value. `x["magnitudes"] = ...` is a store into a dict the module
        # built itself and reads nothing; flagging it was a false positive (it fired on the
        # mutation suite PLANTING a key into a synthetic policy). Writing a magnitude into an
        # artifact would first require reading one, and the structural scan checks every
        # artifact's keys, so a store cannot hide a leak.
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(
                n.ctx, ast.Load):
            key = n.slice.value
        elif isinstance(n, ast.Call) and _call_name(n)[1] == "get" and n.args and isinstance(
                n.args[0], ast.Constant):
            key = n.args[0].value
        if key in MAGNITUDE_KEYS:
            magnitude_key_reads.append({"line": n.lineno, "expr": ast.unparse(n)[:100]})

    prose, semantic = 0, 0
    load_const_ids = {id(s) for c in direct_loads(tree) for s in ast.walk(c)}
    for n in ast.walk(tree):
        if _is_protected_const(n) and id(n) not in load_const_ids:
            if id(n) in doc_ids:
                prose += 1
            else:
                semantic += 1

    return {"module": name, "loads": loads, "subprocess_compare": subprocess_hits,
            "magnitude_key_reads": magnitude_key_reads,
            "exports_loader_functions": sorted(local_loader_funcs),
            "prose_mentions": prose, "semantic_references": semantic,
            "tainted_names": sorted(tainted)}


def violations(r: dict) -> list[str]:
    v = []
    if r["loads"]:
        v.append(f"{len(r['loads'])} protected load(s)")
    if r["subprocess_compare"]:
        v.append("launches the comparator")
    if r["magnitude_key_reads"]:
        v.append(f"{len(r['magnitude_key_reads'])} magnitude-key read(s)")
    return v


# ---------------------------------------------------------------------------------------------
# planted controls -- the scanner must flag every positive and none of the negatives
# ---------------------------------------------------------------------------------------------
POSITIVE = {
    "P1_direct_registry_load":
        'import c11r_common as C\nx = C.load(C.C2 / "evidence" / "registry_c2" / '
        '"REGISTRY_C2.json")\n',
    "P2_load_through_a_variable":
        'import c11r_common as C\np = C.NS / "evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"'
        '\nq = p\nx = C.load(q)\n',
    "P3_load_through_the_receiver":
        'import pathlib\nx = pathlib.Path("e/quarantine/C11R_ORIGINAL_MAGNITUDES.json")'
        '.read_text()\n',
    "P4_git_blob_of_the_old_mixed_table":
        'import c11r_common as C\nb = C.blob_at("38f59993", "evidence/table/C11R_N9_TABLE.json")'
        '\n',
    "P5_via_a_loader_function_in_another_module":
        'import c11r_compare as K\nm = K.load_original_magnitudes()\n',
    "P6_launch_the_comparator":
        'import subprocess, sys\nsubprocess.run([sys.executable, "code/c11r_compare.py"])\n',
    "P7_read_a_magnitude_key":
        'import c11r_common as C\nt = C.load(C.NS / "evidence/table/C11R_N9_STATEMENTS.json")\n'
        'v = t["constants"]["tau"]["value_float"]\n',
    "P8_loader_hidden_in_a_local_helper":
        'import c11r_common as C\ndef _g():\n    return C.load("x/REGISTRY_C2.json")\n'
        'def f():\n    return _g()\nf()\n',
}
NEGATIVE = {
    "N1_docstring_mention":
        '"""This module never reads REGISTRY_C2.json; only the comparator does."""\nx = 1\n',
    "N2_print_mention":
        'print("the registry REGISTRY_C2.json is read only at comparison time")\n',
    "N3_semantic_label":
        'SOURCE = {"source": "REGISTRY_C2.json", "role": "label only"}\n',
    "N4_load_the_statement_table":
        'import c11r_common as C\nt = C.load(C.NS / "evidence/table/C11R_N9_STATEMENTS.json")\n'
        'k = t["constants"]["tau"]["kernel"]\n',
    "N6_store_a_magnitude_key_into_a_local_dict":
        'planted = {}\nplanted["magnitudes"] = {"tau": "planted"}\nplanted["value_float"] = 0\n',
    "N5_launch_the_extractor":
        'import subprocess, sys\nsubprocess.run([sys.executable, "code/c11r_table.py"])\n',
}


def run_controls() -> dict:
    fl = {"c11r_compare": {"load_original_magnitudes"}}
    pos = {k: violations(analyse_source(s, k, foreign_loaders=fl)) for k, s in POSITIVE.items()}
    neg = {k: violations(analyse_source(s, k, foreign_loaders=fl)) for k, s in NEGATIVE.items()}
    return {"positive": {k: {"flagged": bool(v), "why": v} for k, v in pos.items()},
            "negative": {k: {"flagged": bool(v), "why": v} for k, v in neg.items()},
            "all_positives_flagged": all(pos.values()),
            "no_negative_flagged": not any(neg.values())}


def scan_structural_artifacts() -> list[dict]:
    """Pre-result artifacts must carry no magnitude-bearing key. Structural: loads no value."""
    rows = []
    skip = {"C11R_ORIGINAL_MAGNITUDES.json", "C11R_COMPARISON.json"}
    for f in sorted((C.NS / "evidence").rglob("*.json")) + sorted((C.NS / "config").glob("*.json")):
        if f.name in skip:
            continue
        found = []

        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in MAGNITUDE_KEYS:
                        found.append(f"{path}.{k}")
                    walk(v, f"{path}.{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}]")
        walk(json.loads(f.read_text()), "$")
        rows.append({"artifact": str(f.relative_to(C.NS)), "magnitude_keys": found})
    return rows


def main() -> int:
    ctl = run_controls()

    # scope: every C11R module, plus the transitive campaign closure they import
    c11r_mods = sorted(C.HERE.glob("c11r_*.py"))
    scope = {}
    for m in c11r_mods:
        for rel in C.code_closure(m):
            scope[rel] = C.REPO / rel

    # pass 1: which ALLOWED modules export loader functions (so proxy calls can be caught)
    foreign = {}
    for rel, path in scope.items():
        r = analyse_source(path.read_text(), path.name)
        if path.name in ALLOWED_READERS:
            foreign[path.stem] = set(r["exports_loader_functions"])

    results, offenders = {}, []
    for rel, path in sorted(scope.items()):
        r = analyse_source(path.read_text(), path.name, foreign_loaders=foreign)
        v = violations(r)
        allowed = path.name in ALLOWED_READERS
        r["allowed_reader"] = allowed
        r["violations"] = v
        results[rel] = r
        if v and not allowed:
            offenders.append({"module": rel, "violations": v})

    stmt = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    struct = scan_structural_artifacts()
    struct_bad = [r for r in struct if r["magnitude_keys"]]
    stmt_ok = (stmt.get("CONTAINS_NO_ORIGINAL_MAGNITUDE") is True
               and stmt.get("leak_check", {}).get("magnitudes_found") == 0)

    ok = (ctl["all_positives_flagged"] and ctl["no_negative_flagged"] and not offenders
          and not struct_bad and stmt_ok)
    out = {"schema": "C11R_FIREWALL/1",
           "principle": ("original magnitudes may enter only at c11r_table.py (extraction into "
                         "quarantine) and c11r_compare.py (after seal)"),
           "protected_artifacts": list(PROTECTED),
           "allowed_readers": sorted(ALLOWED_READERS),
           "controls": ctl,
           "modules_scanned": len(results),
           "per_module": results,
           "offenders": offenders,
           "structural_artifact_scan": struct,
           "structural_offenders": struct_bad,
           "statement_table_declares_no_magnitude": stmt_ok,
           "FIREWALL_CLASS": "PASS" if ok else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "firewall" / "C11R_FIREWALL.json", out,
                         producer=__file__)
    print("controls:")
    for k, v in ctl["positive"].items():
        print(f"  {'caught ' if v['flagged'] else 'MISSED '} {k:44s} {v['why']}")
    for k, v in ctl["negative"].items():
        print(f"  {'FALSE+ ' if v['flagged'] else 'clean  '} {k:44s} {v['why']}")
    print(f"\nmodules scanned: {len(results)}")
    for rel, r in sorted(results.items()):
        tag = "ALLOWED" if r["allowed_reader"] else ("VIOLATE" if r["violations"] else "clean  ")
        print(f"  {tag}  {rel.split('/')[-1]:24s} loads={len(r['loads'])} "
              f"prose={r['prose_mentions']} semantic={r['semantic_references']}")
    print(f"\noffending modules: {offenders}")
    print(f"structural offenders: {[r['artifact'] for r in struct_bad]}")
    print(f"statement table declares no magnitude: {stmt_ok}")
    print(f"\nFIREWALL_CLASS = {out['FIREWALL_CLASS']}")
    print(f"wrote evidence/firewall/C11R_FIREWALL.json sha256 {s[:16]}...")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
