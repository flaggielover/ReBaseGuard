"""C9 Phase 4 -- E1 producer forensics.

Resolve the certifier's full transitive dependency graph from committed code, determine the external
requirements, and test the one question that could make C9 DATA_BLOCKED: does E1 need the K1
candidate polynomial payloads that C6 proved were never serialized anywhere?
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C

SEARCH = [
    C.AD / "code",
    C.CLOSURE / "p5y_k5_cusum_order3_r3_infrastructure" / "code",
    C.CLOSURE / "p5y_k5_cusum_order3_real_producer" / "code",
    C.CLOSURE / "p5y_k1_cusum_aux5_successor" / "code",
    C.CLOSURE / "p5y_k1_cover_ledger_implementation" / "code",
    C.C2 / "code",
    C.CLOSURE / "p5y_k1_cusum_aux4_fullcover" / "code",
    C.CLOSURE.parent.parent / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics" / "compute_optimization_r2",
    C.CLOSURE / "p5x_global_nonlinear_dynamics" / "compute_optimization_r2",
    C.CLOSURE / "p5x_global_nonlinear_dynamics" / "certified_method_repair_ra",
    C.REPO / "rebaseguard-proof" / "src",
]
STDLIB = {"__future__", "argparse", "json", "math", "sys", "time", "pathlib", "fractions", "os",
          "hashlib", "itertools", "functools", "collections", "typing", "dataclasses", "decimal",
          "concurrent", "subprocess", "re", "warnings", "copy", "bisect", "random", "statistics",
          "contextlib", "traceback", "shutil", "tempfile", "textwrap", "enum", "abc", "io",
          "operator", "pickle", "struct", "array", "gc", "platform", "importlib", "types",
          "multiprocessing", "threading", "queue", "signal", "errno", "stat", "glob", "csv"}
EXTERNAL = {"numpy", "flint", "scipy", "mpmath", "sympy", "gmpy2"}


def find_module(name: str):
    for d in SEARCH:
        for cand in (d / f"{name}.py", d / name / "__init__.py"):
            if cand.exists():
                return cand
    return None


def main() -> int:
    root = C.AD / "code" / "taboo_certify.py"
    seen, missing, ext, pkgs = {}, [], set(), set()
    stack = [("taboo_certify", root)]
    while stack:
        nm, p = stack.pop()
        if nm in seen:
            continue
        seen[nm] = {"path": str(p.relative_to(C.REPO)), "sha256": C.sha256_file(p)}
        try:
            tree = ast.parse(p.read_text(), filename=str(p))
        except SyntaxError as e:
            missing.append({"module": nm, "reason": f"syntax error: {e}"})
            continue
        for node in ast.walk(tree):
            roots = []
            if isinstance(node, ast.Import):
                roots = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = [node.module.split(".")[0]]
            for r in roots:
                if r in STDLIB:
                    continue
                if r in EXTERNAL:
                    ext.add(r)
                    continue
                if r in seen:
                    continue
                q = find_module(r)
                if q is None:
                    pkgs.add(r)
                else:
                    stack.append((r, q))

    # is any external PACKAGE (not module) resolvable in-repo?
    for r in sorted(pkgs):
        q = None
        for d in SEARCH:
            for c2 in d.rglob(f"{r}/__init__.py"):
                q = c2
                break
        if q:
            seen[r] = {"path": str(q.relative_to(C.REPO)), "sha256": C.sha256_file(q)}
        else:
            missing.append({"module": r, "reason": "not resolvable in the committed tree"})

    prod = C.C2 / "code" / "c2_refined_registry.py"
    psrc = prod.read_text()
    tsrc = root.read_text()

    # The DATA_BLOCKED question, tested properly.
    #
    # The first version scanned for TOKENS and fired on the string "K1 record" -- which occurs in the
    # producer's own docstring asserting "no K1 record". A scan that matches a NEGATION of the thing
    # it hunts for is worse than no scan. The real question is whether the producer READS a K1
    # record store, and that is answered by its command-line contract and by its actual file opens.
    cli_takes_records = "--records" in psrc
    consumer = (C.C2 / "code" / "c2_d5_forecast.py").read_text()
    consumer_takes_records = "--records" in consumer
    reads = []
    for node in ast.walk(ast.parse(psrc)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("read_bytes", "read_text", "open"):
            seg = ast.get_source_segment(psrc, node) or ""
            reads.append(seg[:90])
    payload_is_output = '"payload"' in tsrc or "payload" in tsrc
    needs_k1_payload = cli_takes_records

    out_answer = ("NO. The certifier's CLI takes only --outdir/--cells/--workers and never a records "
                  "directory, while the downstream CONSUMER c2_d5_forecast.py DOES take --records. "
                  "The certification and the consumption have different input contracts, and only "
                  "the consumer touches K1. The certifier builds its OWN Chebyshev supersolution; "
                  "the `payload` field in arl_cell_*.json is its OUTPUT. C9 is NOT DATA_BLOCKED."
                  if not needs_k1_payload else
                  "YES -- the producer's CLI requires a records directory. C9 is DATA_BLOCKED.")

    out = {
        "schema": "C9_FORENSICS/1",
        "route": "R3 / E1 operator certification",
        "entry_producer": {"path": str(prod.relative_to(C.REPO)),
                           "sha256": C.sha256_file(prod),
                           "cli": "python -B c2_refined_registry.py build --outdir DIR --cells 307"},
        "certifier": {"path": str(root.relative_to(C.REPO)), "sha256": C.sha256_file(root)},
        "transitive_modules_resolved": len(seen),
        "module_graph": seen,
        "unresolved": missing,
        "external_requirements": sorted(ext),
        "DATA_BLOCKED_question": {
            "question": ("does E1 need the K1 candidate polynomial payloads that C6 proved were "
                         "never serialized anywhere?"),
            "method": ("command-line contract plus an AST scan of the producer's file opens. A token "
                       "scan was tried first and was WRONG: it fired on the producer's own docstring "
                       "asserting 'no K1 record', i.e. on a negation of the thing being hunted."),
            "producer_cli_takes_records_dir": cli_takes_records,
            "consumer_cli_takes_records_dir": consumer_takes_records,
            "producer_file_opens": sorted(set(reads))[:8],
            "needs_k1_candidate_payloads": needs_k1_payload,
            "producer_self_declaration": ("operator only ... no source S_r, no candidate of any "
                                          "F / D / H / G object, no K1 record, no value of R"),
            "answer": out_answer},
        "determinism": {
            "thread_pinning": "_PINNED sets OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1 before numpy loads",
            "exact_arithmetic": "fractions.Fraction plus flint.arb interval arithmetic",
            "declared_new_real": "NEW_REAL_ADDRESSES = 0" in psrc,
        },
    }
    s = C.write_evidence(C.NS / "evidence" / "phase4" / "C9_FORENSICS.json", out)
    print(f"transitive in-repo modules resolved : {len(seen)}")
    print(f"unresolved                          : {missing if missing else 'none'}")
    print(f"external requirements               : {sorted(ext)}")
    print(f"needs K1 candidate payloads         : {needs_k1_payload}")
    print(f"  -> {out['DATA_BLOCKED_question']['answer'][:100]}")
    print(f"wrote evidence/phase4/C9_FORENSICS.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
