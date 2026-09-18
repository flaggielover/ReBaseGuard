"""T-EXT mutation testing (qualification part QM). Each mutant is one exact textual replacement in the frozen
text_transport.py or text_consume.py, loaded from a temporary directory with the namespace path pinned (the R4 pattern;
no sys.modules assignment). A mutant is DETECTED when its output differs from the frozen, independently cross-checked
result (transport: any row field; consumption: the independent X-B check reports a problem) or when it refuses.
An unmodified copy loaded the same way (sham control) must reproduce the frozen result exactly.

    python -B code/text_mutants.py --text TEXT_RESULT.json --text-sha256 <sha> --out MUTATIONS.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
X1 = "F(5083, 10000000)"
TRANSPORT_MUTANTS = [
    ("TM01_ETA_FIXED_AT_X1", '"eta": ex(eta), "S0"', f'"eta": ex({X1}), "S0"'),
    ("TM02_K_J_NORMS_ON_CELL0", "t = H6.norm_table(F(0), eta)", f"t = H6.norm_table(F(0), {X1})"),
    ("TM03_S0_ON_CELL0", "H6.sup_S0_on(n, F(0), eta)", f"H6.sup_S0_on(n, F(0), {X1})"),
    ("TM04_C_MIN_NOT_MAX", 'C = max(F(c["C_upper"]) for c in cells[:k + 1])', 'C = min(F(c["C_upper"]) for c in cells[:k + 1])'),
    ("TM05_ANCHOR_DRIFT_X1", "drift = R1E.exact(eta)", f"drift = R1E.exact({X1})"),
    ("TM06_TRANSPORT_TO_LEFT_END", 'X = F(cells[k]["right"][0])', 'X = F(cells[k]["left"][0])'),
    ("TM07_L_FROM_U0", 'L0 = {m: F(s["per_m"][m]["L0"]) for m in MS}', 'L0 = {m: F(s["per_m"][m]["U0"]) for m in MS}'),
    ("TM08_M_OF_M1_FOR_ALL_M", "order=n)[int(m)]", "order=n)[1]"),
    ("TM09_HULL_ENDS_AT_LEFT", 'eta = F(cells[k]["right"][0])', 'eta = F(cells[k]["left"][0])'),
    ("TM10_POINT_ERRORS_DROPPED", "G.V(ex(F(e)), ex(F(o)), ex(F(t)))", "G.V(ex(F(0)), ex(F(0)), ex(F(0)))"),
    ("TM11_PIECEWISE_USES_OWN_HULL", "M5[j][m] * ((X", "M5[k][m] * ((X"),
    ("TM12_PIECEWISE_PREVIOUS_HULL", "M5[j][m] * ((X", "M5[max(j - 1, 0)][m] * ((X"),
    ("TM13_M3_FLOOR_SIGN", "max(L0[m] - B, -M3[k][m])", "max(L0[m] - B, M3[k][m])"),
    ("TM14_M_EXPORT_WRONG_ORDER", "order=n)[int(m)]", "order=min(n + 1, 5))[int(m)]"),
]
CONSUME_MUTANTS = [
    ("CM01_PREVIOUS_CELL_L", 'cells[k]["L"] = lam[m][k]', 'cells[k]["L"] = lam[m][max(k - 1, 1)]'),
    ("CM02_M1_CHANNEL_FOR_ALL_M", 'cells[k]["L"] = lam[m][k]', 'cells[k]["L"] = lam["1"][k]'),
    ("CM03_SEALED_L1_DROPPED", "cells = A.cells_for_m(KM, cover, records, m, L1[m])",
     "cells = A.cells_for_m(KM, cover, records, m, None)"),
    ("CM04_M2_PREVIOUS_HULL", "b = m2[m][k]", "b = m2[m][max(k - 1, 0)]"),
    ("CM05_H_FLOOR_TOO_HIGH", 'cells[k]["H"] = (max(lo, -b), min(hi, b))', 'cells[k]["H"] = (max(lo, b / 2), min(hi, b))'),
]


def load_variant(path: Path, old: str | None, new: str | None, name: str, tmp: Path):
    src = path.read_text()
    if old is not None:
        if src.count(old) != 1:
            raise RuntimeError(f"{name}: mutation site not unique ({src.count(old)})")
        src = src.replace(old, new)
    pin = "HERE = Path(__file__).resolve()"
    if src.count(pin) != 1:
        raise RuntimeError(f"{name}: cannot pin the namespace path")
    src = src.replace(pin, f"HERE = Path({str(path)!r})")
    f = tmp / f"{name}.py"
    f.write_text(src)
    spec = importlib.util.spec_from_file_location(f"text_variant_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(text_path: Path, text_sha256: str, records: Path) -> dict:
    sys.path.insert(0, str(CODE))
    import text_crosscheck as X
    frozen = json.loads(text_path.read_text())
    tmp = Path(tempfile.mkdtemp(prefix="text-mutants-", dir="/var/tmp"))
    key = lambda rows: [(r["cell"], r["M"], r.get("Lambda"), r.get("L_simple"), r["resolvent_mode"], r["hull_norms"])
                        for r in rows]
    out = {"transport": {}, "consumption": {}}
    for name, old, new in [("SHAM_TRANSPORT", None, None)] + TRANSPORT_MUTANTS:
        try:
            res = load_variant(CODE / "text_transport.py", old, new, name, tmp).evaluate()
            same = key(res["rows"]) == key(frozen["rows"]) and res["L0"] == frozen["L0"]
            out["transport"][name] = {"detected": not same, "how": "output differs" if not same else None}
        except Exception as exc:
            out["transport"][name] = {"detected": True, "how": f"refused: {type(exc).__name__}: {str(exc)[:160]}"}
    for name, old, new in [("SHAM_CONSUME", None, None)] + CONSUME_MUTANTS:
        try:
            res = load_variant(CODE / "text_consume.py", old, new, name, tmp).consume(text_path, text_sha256, records)
            p = tmp / f"{name}.json"
            p.write_text(json.dumps(res))
            xb = X.consumption(text_path, p, records)
            out["consumption"][name] = {"detected": not xb["pass"], "how": xb["problems"][:3]}
        except Exception as exc:
            out["consumption"][name] = {"detected": True, "how": f"refused: {type(exc).__name__}: {str(exc)[:160]}"}
    shams_ok = (not out["transport"]["SHAM_TRANSPORT"]["detected"]) and (not out["consumption"]["SHAM_CONSUME"]["detected"])
    muts = {**{k: v for k, v in out["transport"].items() if not k.startswith("SHAM")},
            **{k: v for k, v in out["consumption"].items() if not k.startswith("SHAM")}}
    return {"schema": "rebaseguard.p5y.k5.remaining-cell-closure.text-mutations.v1", "results": out,
            "shams_reproduce": shams_ok, "detected": sum(v["detected"] for v in muts.values()), "total": len(muts),
            "pass": shams_ok and all(v["detected"] for v in muts.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--text-sha256", required=True)
    ap.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run(Path(a.text), a.text_sha256, Path(a.records))
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print("mutants detected", res["detected"], "/", res["total"], "shams reproduce", res["shams_reproduce"],
          "PASS" if res["pass"] else "FAIL")
    return 0 if res["pass"] else 6


if __name__ == "__main__":
    sys.exit(main())
