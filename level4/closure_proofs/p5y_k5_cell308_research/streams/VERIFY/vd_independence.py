"""Stream D, D2: measured independence of the verifier from the original certifiers.

(1) static: AST import list of every verifier-side module; any import whose last component starts with c1b_, c2b_,
    c7_ (or is ov_quarantine, or any module living in the certifier directories) is a finding; planted control.
(2) runtime: import the verifier-side modules, run a small verification, then list sys.modules: no certifier module
    may be loaded; planted control (a subprocess that imports c1b_gauss must be detected).
(3) textual overlap: identical normalised source lines (length >= 25 after whitespace collapse) and shared
    top-level function names between each verifier-side file and each original certifier file.
Output: results/D2_INDEPENDENCE.json.  The producer vd_produce.py is reported separately (it is the one sanctioned
importer of C1b and is not part of the verifier).
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
OV = NS.parent / "p5y_k5_tail_overnight_research"
ORIG_DIRS = [OV / "streams" / "C_308" / "LR" / "cusum", OV / "streams" / "C_308" / "A0X" / "gen",
             NS / "streams" / "A0"]          # stream A0 (stored-format reader read for layout; its certifier code)
VERIFIER_SIDE = ["vd_verify.py", "vd_point.py", "vd_adapt.py", "vd_float.py", "vd_controls.py",
                 "vd_d3_verify_all.py", "vd_d5.py", "vd_mc.py", "vd_crosscheck.py", "vd_independence.py",
                 "vd_pl.py", "vd_d6_verify_pl.py", "vd_pl_controls.py", "vd_pl_crosscheck.py", "vd_d7_cost.py"]
BAD = re.compile(r"^(c1b_|c2b_|c7_|a0_|ov_quarantine$|r2_)")


def imports_of(path: Path) -> list:
    tree = ast.parse(path.read_text())
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            out.append(n.module or "")
        elif isinstance(n, ast.Call):
            f = n.func
            nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            if nm in ("__import__", "import_module") and n.args and isinstance(n.args[0], ast.Constant):
                out.append(str(n.args[0].value))
    return sorted(set(out))


def bad_imports(mods: list) -> list:
    return [m for m in mods if BAD.search(m.rsplit(".", 1)[-1])]


def norm_lines(path: Path) -> set:
    s = set()
    for line in path.read_text().splitlines():
        t = " ".join(line.split())
        if len(t) >= 25 and not t.startswith("#"):
            s.add(t)
    return s


def top_funcs(path: Path) -> set:
    tree = ast.parse(path.read_text())
    return {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def main() -> dict:
    res = {"verifier_side_files": VERIFIER_SIDE}
    static = {}
    for f in VERIFIER_SIDE:
        mods = imports_of(HERE / f)
        static[f] = {"imports": mods, "certifier_imports": bad_imports(mods)}
    res["static_imports"] = static
    res["static_clean"] = all(not v["certifier_imports"] for v in static.values())
    with tempfile.TemporaryDirectory() as td:
        pl = Path(td) / "planted.py"
        pl.write_text("import c1b_pw\nfrom c2b_exact import Mesh\nimport importlib\nimportlib.import_module('c7_gaussian')\n"
                      "import a0_c2b\n")
        pm = imports_of(pl)
        res["static_planted_control"] = {"imports": pm, "flagged": bad_imports(pm),
                                         "detected": sorted(bad_imports(pm)) == ["a0_c2b", "c1b_pw", "c2b_exact",
                                                                                 "c7_gaussian"]}
    res["producer_imports"] = imports_of(HERE / "vd_produce.py")
    # runtime
    code = ("import sys; sys.path.insert(0, %r)\n"
            "import vd_verify as V, vd_point as P, vd_adapt as A, vd_float as FL, vd_pl as PL\n"
            "from fractions import Fraction as F\n"
            "W = V.StripPW([0, 5], [{(0, 0): F(100)}])\n"
            "pre = V.Prep(W, F(3)); V.residual_point(pre, F(1, 3), F(1, 5)); P.residual(P.PW(W.to_json()), 3, 0, 0)\n"
            "V.bb_box(('k', W.to_json(), '3', False, (F(0), F(1, 4), F(0), F(1, 4)), 'res', {}))\n"
            "PW = PL.PLW(2, [[F(10)] * c for c in PL._cols(2)])\n"
            "PL.verify_pl(PW, F(3), workers=1); P.residual(P.make(PW.to_json()), 3, F(1, 3), F(1, 5))\n"
            "print('\\n'.join(sorted(sys.modules)))\n") % str(HERE)
    r = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, timeout=600)
    loaded = r.stdout.split()
    res["runtime_modules_loaded_count"] = len(loaded)
    res["runtime_certifier_modules"] = [m for m in loaded if BAD.search(m.rsplit(".", 1)[-1])]
    res["runtime_nonstdlib_modules"] = [m for m in loaded if m.startswith(("vd_", "c308"))]
    res["runtime_ok"] = r.returncode == 0 and not res["runtime_certifier_modules"]
    ctrl = ("import sys; sys.path.insert(0, %r); import c1b_gauss\nprint('\\n'.join(sorted(sys.modules)))\n"
            % str(ORIG_DIRS[0]))
    r2 = subprocess.run([sys.executable, "-I", "-B", "-c", ctrl], capture_output=True, text=True, timeout=120)
    res["runtime_planted_control_detected"] = any(BAD.search(m) for m in r2.stdout.split())
    # textual overlap
    orig_files = sorted(p for d in ORIG_DIRS for p in d.glob("*.py"))
    overlap = {}
    tot_lines = 0
    for f in VERIFIER_SIDE:
        mine = norm_lines(HERE / f)
        tot_lines += len(mine)
        mf = top_funcs(HERE / f)
        hits = {}
        for o in orig_files:
            common = mine & norm_lines(o)
            names = mf & top_funcs(o)
            if common or names:
                hits[o.name] = {"identical_lines": len(common), "examples": sorted(common)[:4],
                                "shared_top_level_names": sorted(names)}
        overlap[f] = {"normalised_lines": len(mine), "overlaps": hits,
                      "identical_lines_total": len(set().union(*[mine & norm_lines(o) for o in orig_files]))}
    res["textual_overlap"] = overlap
    res["original_files_compared"] = [str(p.relative_to(NS.parent)) for p in orig_files]
    return res


if __name__ == "__main__":
    out = main()
    (HERE / "results" / "D2_INDEPENDENCE.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("static_clean", "runtime_ok", "runtime_certifier_modules",
                                          "runtime_planted_control_detected")}, indent=1))
    print(json.dumps(out["static_planted_control"]))
    for f, v in out["textual_overlap"].items():
        print(f, v["normalised_lines"], v["identical_lines_total"],
              {k: (x["identical_lines"], x["shared_top_level_names"]) for k, x in v["overlaps"].items()})
