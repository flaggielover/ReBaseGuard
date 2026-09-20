"""Campaign C1: build and verify the CERTIFIED OPERATOR-ONLY registry extension over the CUSUM m = 5 tail.

Operator only, exactly in the sense of theorem AD section 8: no source S_r, no candidate of any F / D / H / G object,
no K1 record, no value of R. The only machinery used is the frozen, adopted `taboo_certify` of
`p5y_k5_perron_deflated_resolvent`, executed from its pinned bytes, on the tail domain instead of [0, 0.12].
**NEW_REAL_ADDRESSES = 0**: nothing here is a scientific address, and the guard stays DENY.

Per tail cell k the extension certifies, uniformly on the cell's own e-interval [left, right]:

    taboo block   w >= 1 + Khat_e w      ->  C_T >= sup ||Ghat_e||,  tau >= sup E_a[tau ^ T_a]      (Lemma T)
    ARL block     W >= 1 + K_e W         ->  Abar >= sup E_a[tau]                   (whole-kernel supersolution)
    cell artifact d, d', d''             ->  D_lo <= inf D_e,  D1 >= sup |D'|,  D2 >= sup |D''|     (Lemma SM)

which are the six constants theorem AD section 8 requires, and which `deflated_consume.atom_constants_r2` turns into
the Lemma Dv' atom constants A0, A1, A2 that theorem TC-T consumes in place of Lemma G's generic ones.

One block per tail cell, equal to that cell's own interval, so the adopted `block_for` resolves each cell to exactly
one block with exact coverage. The alpha ladders are deterministic and pre-registered; the first alpha that certifies
is taken, and a cell that certifies at no alpha is reported uncertified rather than patched.

    python -B c1_tail_registry.py build  --outdir DIR [--cells 305,306,307,308,309] [--workers 5]
    python -B c1_tail_registry.py verify --outdir DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
if "numpy" not in sys.modules:
    os.environ.update(_PINNED)
    os.environ["K1_THREADS_PINNED"] = "1"

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
AD = CP / "p5y_k5_perron_deflated_resolvent"
CELLS_JSON = CP / "p5y_k1_cover_ledger_successor/config/cells.json"
CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"
TABOO_SHA256 = None            # filled from the C1 protocol when one exists; None = record, do not enforce
TAIL = (305, 306, 307, 308, 309)
DEGREE_TABOO = 20
DEGREE_ARL = 12
SCHEMA = "rebaseguard.p5y.k5.tail-operator-registry.registry.v1"

# deterministic, pre-registered alpha ladders (the frozen build_registry ladders, extended upward for the tail)
TABOO_ALPHAS = (F(6, 5), F(13, 10), F(7, 5), F(3, 2), F(2), F(3))
ARL_ALPHAS = (F(5, 4), F(7, 5), F(3, 2), F(2), F(3), F(5))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _import():
    for p in (str(AD / "code"), str(CP / "p5y_k5_order3_readiness_audit/code")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import taboo_certify as TC
    import k5_minimality as KM
    return TC, KM


def cover():
    TC, KM = _import()
    if sha(CELLS_JSON.read_bytes()) != CELLS_SHA256:
        raise SystemExit("cells.json does not match its pin")
    cells = KM.load_cells(CELLS_JSON, "CUSUM")          # NOTE: index collides across detectors; filter first
    return {c["index"]: tuple(KM.rat(c[t]) for t in ("left", "right", "e0", "rho")) for c in cells}


def _one(args):
    k, x_lo, x_hi, e0, rho, outdir = args
    TC, _ = _import()
    out = {"cell": k, "e_lo": str(x_lo), "e_hi": str(x_hi), "e0": str(e0), "rho": str(rho)}
    t0 = time.process_time()

    taboo = None
    for a in TABOO_ALPHAS:
        art = TC.block_artifact(x_lo, x_hi, a, F(0), 2, DEGREE_TABOO, False)
        if art["certified"]:
            taboo, out["taboo_alpha"] = art, str(a)
            break
    if taboo is None:
        out["certified"] = False
        out["reason"] = "no taboo supersolution certified on the cell interval at any pre-registered alpha"
        out["cpu_seconds"] = time.process_time() - t0
        return out
    tp = Path(outdir) / f"taboo_block_{k:03d}.json"
    tp.write_text(json.dumps(taboo, indent=1, sort_keys=True) + "\n")
    out["C_T"], out["tau"] = taboo["C_T"], taboo["tau"]
    out["taboo_artifact_sha256"] = sha(tp.read_bytes())

    arl = None
    for a in ARL_ALPHAS:
        art = TC.block_artifact(x_lo, x_hi, a, F(2), 2, DEGREE_ARL, True)
        if art["certified"]:
            arl, out["arl_alpha"] = art, str(a)
            break
    if arl is None:
        out["certified"] = False
        out["reason"] = "no whole-kernel ARL supersolution certified on the cell interval at any pre-registered alpha"
        out["cpu_seconds"] = time.process_time() - t0
        return out
    ap = Path(outdir) / f"arl_cell_{k:03d}.json"
    ap.write_text(json.dumps(arl, indent=1, sort_keys=True) + "\n")
    out["Abar"] = arl["tau"]                      # the whole-kernel supersolution's value at the atom
    out["arl_artifact_sha256"] = sha(ap.read_bytes())

    da = TC.cell_artifact(e0, rho, F(out["tau"]), F(out["C_T"]), degree=DEGREE_TABOO)
    dp = Path(outdir) / f"taboo_cell_{k:03d}.json"
    dp.write_text(json.dumps(da, indent=1, sort_keys=True) + "\n")
    out["D_lo"], out["D1"], out["D2"] = da["D_lo"], da["D1"], da["D2"]
    out["taboo_cell_artifact_sha256"] = sha(dp.read_bytes())
    out["certified"] = bool(da["certified"])
    if not out["certified"]:
        out["reason"] = "the taboo cell artifact (d, d', d'') did not certify"
    out["cpu_seconds"] = time.process_time() - t0
    return out


def build(outdir: Path, cells, workers: int) -> dict:
    cov = cover()
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(k, *cov[k], str(outdir)) for k in cells]
    rows = []
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_one, jobs))
    else:
        rows = [_one(j) for j in jobs]
    rows.sort(key=lambda r: r["cell"])
    reg = {"schema": SCHEMA, "rule": "r2", "operator_only": True,
           "certified": all(r.get("certified") for r in rows),
           "degree_taboo": DEGREE_TABOO, "degree_arl": DEGREE_ARL,
           "taboo_alphas": [str(a) for a in TABOO_ALPHAS], "arl_alphas": [str(a) for a in ARL_ALPHAS],
           "cells_json_sha256": CELLS_SHA256,
           "code_sha256": {"taboo_certify": sha((AD / "code/taboo_certify.py").read_bytes()),
                           "c1_tail_registry": sha(HERE.read_bytes())},
           "blocks": rows,
           "cpu_seconds_total": sum(r.get("cpu_seconds", 0.0) for r in rows)}
    return reg


def verify(outdir: Path, reg: dict) -> dict:
    """Recompute every stored artifact from its own exact payload and compare every certified field."""
    TC, _ = _import()
    bad = []
    for r in reg["blocks"]:
        k = r["cell"]
        if not r.get("certified"):
            continue
        for name, fn, fields in (("taboo_block", TC.verify_block, ("C_T", "tau")),
                                 ("arl_cell", TC.verify_block, ("tau",)),
                                 ("taboo_cell", TC.verify_cell, ("D_lo", "D1", "D2"))):
            p = outdir / f"{name}_{k:03d}.json"
            art = json.loads(p.read_bytes())
            got = fn(art)
            if got.get("certified") is not True:
                bad.append(f"{name} {k}: recomputation does not certify")
            for fld in fields:
                mine = r["Abar"] if (name == "arl_cell" and fld == "tau") else r[fld]
                if str(got.get(fld)) != str(mine):
                    bad.append(f"{name} {k}: {fld} differs")
        want = {"taboo_block": "taboo_artifact_sha256", "arl_cell": "arl_artifact_sha256",
                "taboo_cell": "taboo_cell_artifact_sha256"}
        for name, key in want.items():
            if sha((outdir / f"{name}_{k:03d}.json").read_bytes()) != r[key]:
                bad.append(f"{name} {k}: artifact sha differs")
    return {"pass": not bad, "problems": bad[:10], "blocks_checked": len(reg["blocks"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("build", "verify"))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--cells", default=",".join(str(k) for k in TAIL))
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    outdir = Path(a.outdir)
    cells = [int(x) for x in a.cells.split(",") if x]
    if any(k not in TAIL for k in cells):
        raise SystemExit(f"cells outside the frozen C1 universe {TAIL}")
    if a.mode == "build":
        reg = build(outdir, cells, a.workers)
        data = json.dumps(reg, sort_keys=True, indent=1).encode() + b"\n"
        (outdir / "REGISTRY_C1.json").write_bytes(data)
        print(json.dumps({"certified": reg["certified"], "cells": len(reg["blocks"]),
                          "cpu_seconds_total": round(reg["cpu_seconds_total"], 1),
                          "sha256": sha(data),
                          "per_cell": {str(r["cell"]): {"certified": r.get("certified"),
                                                        "C_T": (float(F(r["C_T"])) if r.get("C_T") else None),
                                                        "tau": (float(F(r["tau"])) if r.get("tau") else None),
                                                        "Abar": (float(F(r["Abar"])) if r.get("Abar") else None),
                                                        "D_lo": (float(F(r["D_lo"])) if r.get("D_lo") else None),
                                                        "D1": (float(F(r["D1"])) if r.get("D1") else None),
                                                        "D2": (float(F(r["D2"])) if r.get("D2") else None),
                                                        "reason": r.get("reason")}
                                       for r in reg["blocks"]}}, indent=1))
        return 0 if reg["certified"] else 1
    reg = json.loads((outdir / "REGISTRY_C1.json").read_bytes())
    res = verify(outdir, reg)
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
