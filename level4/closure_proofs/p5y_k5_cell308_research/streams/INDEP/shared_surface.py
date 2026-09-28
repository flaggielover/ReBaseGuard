"""shared_surface.py -- Stream F2: measure the code surface mb_independent.py shares with the primary / reference code.

Stdlib only. Four measurements, written to results/SHARED_SURFACE.json:
 S1 static imports of mb_independent.py (AST): must be stdlib only;
 S2 runtime: modules newly loaded by `import mb_independent` in a fresh isolated interpreter (-I -B): must all be
    stdlib (sys.stdlib_module_names) apart from mb_independent itself;
 S3 textual: identical normalized code lines (>= 24 chars after whitespace collapse, comments and docstrings
    dropped) and identifier 6-gram Jaccard between mb_independent.py and every reference file;
 S4 provenance: sha256 of mb_independent.py now vs the hash ledgered BEFORE any primary file was read.
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
CP = NS.parent
MOD = HERE / "mb_independent.py"
PRE_READ_SHA256 = "32aa83a866005ad737424225ff8bfcb3898ebb79b3598e37d80a1e89a16ca4c0"

REFERENCES = [
    NS / "streams" / "ASSEMBLY" / "tptb_tail.py", NS / "streams" / "ASSEMBLY" / "decoy_gen.py",
    NS / "streams" / "ASSEMBLY" / "frozen_path_loader.py", NS / "streams" / "ASSEMBLY" / "lower_front_tptb.py",
    NS / "streams" / "ASSEMBLY" / "controls.py", NS / "streams" / "ASSEMBLY" / "validate_decoys.py",
    CP / "p5y_k5_tail_overnight_research" / "streams" / "E_assembly" / "tpt.py",
    CP / "p5y_k5_cell307_rlr_r1" / "code" / "rlr307_independent.py",
    CP / "p5y_k5_cell307_rlr_r1" / "code" / "rlr307_stage1.py",
    CP / "p5y_k5_perron_deflated_resolvent" / "code" / "deflated_consume.py",
    CP / "p5y_k5_tail_c2_closure" / "code" / "c2_d5_forecast.py",
    CP / "p5y_k5_m5_tail_closure" / "code" / "tct_rule.py",
    CP / "p5y_k5_lower_front_order3" / "code" / "tc_rule.py",
] + sorted((NS / "streams" / "A0").glob("a0_*.py")) + sorted((NS / "streams" / "VERIFY").glob("vd_*.py")) + sorted(
    (CP / "p5y_k5_tail_overnight_research").rglob("c1b_*.py")) + sorted(
    (CP / "p5y_k5_tail_overnight_research").rglob("c2b_*.py"))


def code_lines(src: str) -> list[str]:
    """Normalized code lines: docstrings and comments removed, whitespace collapsed."""
    tree = ast.parse(src)
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                doc_lines.update(range(first.lineno, first.end_lineno + 1))
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in doc_lines:
            continue
        line = re.sub(r"#.*$", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if len(line) >= 24:
            out.append(line)
    return out


def ident_ngrams(src: str, n: int = 6) -> set:
    toks = [t.string for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type in (tokenize.NAME, tokenize.OP, tokenize.NUMBER)]
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def main() -> int:
    src = MOD.read_text()
    res = {"schema": "F2_SHARED_SURFACE/1", "module": str(MOD.relative_to(NS))}
    # S1
    imps = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            imps += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imps.append(node.module)
    std = set(sys.stdlib_module_names) | {"__future__"}
    res["S1_static_imports"] = {"imports": sorted(set(imps)),
                                "non_stdlib": sorted(i for i in set(imps) if i.split(".")[0] not in std)}
    # S2
    probe = ("import sys, json; sys.path.insert(0, %r); b = set(sys.modules); import mb_independent; "
             "print(json.dumps(sorted(set(sys.modules) - b)))" % str(HERE))
    new = json.loads(subprocess.run([sys.executable, "-I", "-B", "-c", probe], capture_output=True, text=True,
                                    check=True).stdout)
    res["S2_runtime_new_modules"] = {"modules": new, "non_stdlib": [m for m in new if m.split(".")[0] not in std
                                                                    and m != "mb_independent"]}
    # S3
    mine_lines = set(code_lines(src))
    mine_ng = ident_ngrams(src)
    rows = []
    for p in REFERENCES:
        if not p.exists():
            rows.append({"file": str(p.relative_to(CP)), "missing": True})
            continue
        rsrc = p.read_text()
        common = sorted(mine_lines & set(code_lines(rsrc)))
        rng = ident_ngrams(rsrc)
        jac = len(mine_ng & rng) / max(1, len(mine_ng | rng))
        rows.append({"file": str(p.relative_to(CP)), "identical_code_lines": len(common), "lines": common,
                     "ident_6gram_jaccard": round(jac, 4), "shared_6grams": len(mine_ng & rng)})
    res["S3_textual"] = {"mine_code_lines": len(mine_lines), "mine_6grams": len(mine_ng), "per_file": rows,
                         "total_identical_lines": len({ln for r in rows for ln in r.get("lines", [])})}
    # S4
    now = hashlib.sha256(MOD.read_bytes()).hexdigest()
    res["S4_provenance"] = {"sha256_now": now, "sha256_pre_read": PRE_READ_SHA256, "unchanged_since_pre_read":
                            now == PRE_READ_SHA256}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "SHARED_SURFACE.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({"S1": res["S1_static_imports"], "S2_non_stdlib": res["S2_runtime_new_modules"]["non_stdlib"],
                      "S3_total_identical_lines": res["S3_textual"]["total_identical_lines"],
                      "S3_max_jaccard": max(r.get("ident_6gram_jaccard", 0) for r in rows),
                      "S4": res["S4_provenance"]["unchanged_since_pre_read"]}, indent=1))
    for r in rows:
        if r.get("identical_code_lines"):
            print(r["file"], r["identical_code_lines"], r["ident_6gram_jaccard"])
            for ln in r["lines"]:
                print("    ", ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
