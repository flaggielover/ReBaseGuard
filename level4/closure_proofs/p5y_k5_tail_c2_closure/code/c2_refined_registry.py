"""Campaign C2, Phases D2 and D3: the REFINED certified operator-only registry over the CUSUM m = 5 tail.

Operator only, in the sense of theorem AD section 8: no source S_r, no candidate of any F / D / H / G object, no K1
record, no value of R. The machinery is the frozen, adopted `taboo_certify`, executed from its pinned bytes.
**NEW_REAL_ADDRESSES = 0**; the guard stays DENY.

Two changes from Campaign C1, both fixed by the C2 gate BEFORE any certification ran:

  D2  partition   each tail cell's e-interval is split into N_k = ceil(2*rho_k / (1/100)) equal sub-blocks, i.e.
                  sub-blocks no wider than 1/100 - the geometry of the ADOPTED registry r1, not a width tuned to the
                  tail. C1 used one block of width 2*rho per cell.
  D3  denominator the taboo cell artifact (d, d', d'') is certified PER SUB-BLOCK rather than once per cell, and the
                  cell takes D_lo = min, D1 = max, D2 = max over its sub-blocks. A narrower sub-cell admits a tighter
                  bound, and the worst over a cover of the cell is a valid whole-cell bound.

The whole-kernel ARL supersolution (Abar) stays per cell: Phase D1 showed Abar is inert on the tail
(Abar_eff = tau/D_lo on all five cells), so subdividing it would spend a third of the budget on a quantity that
feeds nothing. It is still certified, per cell, so that C2's chain is self-contained.

    python -B c2_refined_registry.py build  --outdir DIR [--cells 305,...] [--workers 7]
    python -B c2_refined_registry.py verify --outdir DIR
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
from math import ceil
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
TABOO_SHA256 = "ced9422ca07981a9ad053acd79b72ef0d5007e93e49c16f2501f31c593fd0daa"
TAIL = (305, 306, 307, 308, 309)
SUB_BLOCK_MAX_WIDTH = F(1, 100)                 # the adopted registry r1 geometry, fixed by the C2 gate
DEGREE_TABOO = 20
DEGREE_ARL = 12
TABOO_ALPHAS = (F(6, 5), F(13, 10), F(7, 5), F(3, 2), F(2), F(3))
ARL_ALPHAS = (F(5, 4), F(7, 5), F(3, 2), F(2), F(3), F(5))
SCHEMA = "rebaseguard.p5y.k5.tail-c2.refined-registry.v1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _import():
    if sha((AD / "code/taboo_certify.py").read_bytes()) != TABOO_SHA256:
        raise SystemExit("the adopted taboo certifier does not match its pin")
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
    cells = KM.load_cells(CELLS_JSON, "CUSUM")      # index collides across detectors; the loader filters first
    return {c["index"]: tuple(KM.rat(c[t]) for t in ("left", "right", "e0", "rho")) for c in cells}


def sub_blocks(x_lo: F, x_hi: F) -> list:
    """N = ceil(width / (1/100)) equal sub-blocks, exactly as the frozen gate specifies."""
    n = max(1, ceil((x_hi - x_lo) / SUB_BLOCK_MAX_WIDTH))
    w = (x_hi - x_lo) / n
    return [(x_lo + i * w, x_lo + (i + 1) * w) for i in range(n)]


def _sub(args):
    """One sub-block: the taboo supersolution (C_T, tau) and then the denominator artifact (D_lo, D1, D2) on it."""
    k, i, lo, hi, outdir = args
    TC, _ = _import()
    t0 = time.process_time()
    out = {"cell": k, "sub": i, "e_lo": str(lo), "e_hi": str(hi)}
    taboo = None
    for a in TABOO_ALPHAS:
        art = TC.block_artifact(lo, hi, a, F(0), 2, DEGREE_TABOO, False)
        if art["certified"]:
            taboo, out["taboo_alpha"] = art, str(a)
            break
    if taboo is None:
        out.update({"certified": False, "reason": "no taboo supersolution at any pre-registered alpha",
                    "cpu_seconds": time.process_time() - t0})
        return out
    tp = Path(outdir) / f"taboo_block_{k:03d}_{i:02d}.json"
    tp.write_text(json.dumps(taboo, indent=1, sort_keys=True) + "\n")
    out["C_T"], out["tau"] = taboo["C_T"], taboo["tau"]
    out["taboo_artifact_sha256"] = sha(tp.read_bytes())
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    da = TC.cell_artifact(mid, half, F(out["tau"]), F(out["C_T"]), degree=DEGREE_TABOO)
    dp = Path(outdir) / f"taboo_cell_{k:03d}_{i:02d}.json"
    dp.write_text(json.dumps(da, indent=1, sort_keys=True) + "\n")
    out["D_lo"], out["D1"], out["D2"] = da["D_lo"], da["D1"], da["D2"]
    out["denominator_artifact_sha256"] = sha(dp.read_bytes())
    out["certified"] = bool(da["certified"])
    if not out["certified"]:
        out["reason"] = "the denominator artifact (d, d', d'') did not certify on this sub-block"
    out["cpu_seconds"] = time.process_time() - t0
    return out


def _arl(args):
    """The whole-kernel ARL supersolution, once per cell (Abar is inert on the tail; see the module docstring)."""
    k, x_lo, x_hi, outdir = args
    TC, _ = _import()
    t0 = time.process_time()
    for a in ARL_ALPHAS:
        art = TC.block_artifact(x_lo, x_hi, a, F(2), 2, DEGREE_ARL, True)
        if art["certified"]:
            p = Path(outdir) / f"arl_cell_{k:03d}.json"
            p.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
            return {"cell": k, "certified": True, "Abar": art["tau"], "arl_alpha": str(a),
                    "arl_artifact_sha256": sha(p.read_bytes()), "cpu_seconds": time.process_time() - t0}
    return {"cell": k, "certified": False, "reason": "no ARL supersolution at any pre-registered alpha",
            "cpu_seconds": time.process_time() - t0}


def build(outdir: Path, cells, workers: int) -> dict:
    cov = cover()
    outdir.mkdir(parents=True, exist_ok=True)
    subs, jobs = {}, []
    for k in cells:
        x_lo, x_hi, _, _ = cov[k]
        subs[k] = sub_blocks(x_lo, x_hi)
        jobs += [(k, i, lo, hi, str(outdir)) for i, (lo, hi) in enumerate(subs[k])]
    arl_jobs = [(k, cov[k][0], cov[k][1], str(outdir)) for k in cells]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        sub_rows = list(pool.map(_sub, jobs))
        arl_rows = list(pool.map(_arl, arl_jobs))
    arl = {r["cell"]: r for r in arl_rows}

    blocks = []
    for k in cells:
        rows = sorted([r for r in sub_rows if r["cell"] == k], key=lambda r: r["sub"])
        ok = all(r.get("certified") for r in rows) and arl[k].get("certified")
        row = {"cell": k, "e_lo": str(cov[k][0]), "e_hi": str(cov[k][1]),
               "e0": str(cov[k][2]), "rho": str(cov[k][3]),
               "sub_blocks": len(rows), "certified": bool(ok),
               "sub_rows": rows, "arl": arl[k]}
        if ok:
            # the cell takes the worst of its sub-blocks: an upper bound is the max, a lower bound the min
            row["C_T"] = str(max(F(r["C_T"]) for r in rows))
            row["tau"] = str(max(F(r["tau"]) for r in rows))
            row["D_lo"] = str(min(F(r["D_lo"]) for r in rows))
            row["D1"] = str(max(F(r["D1"]) for r in rows))
            row["D2"] = str(max(F(r["D2"]) for r in rows))
            row["Abar"] = arl[k]["Abar"]
        else:
            row["reason"] = next((r.get("reason") for r in rows if r.get("reason")), arl[k].get("reason"))
        blocks.append(row)
    cpu = sum(r.get("cpu_seconds", 0.0) for r in sub_rows) + sum(r.get("cpu_seconds", 0.0) for r in arl_rows)
    return {"schema": SCHEMA, "rule": "r2", "operator_only": True,
            "certified": all(b["certified"] for b in blocks),
            "sub_block_max_width": str(SUB_BLOCK_MAX_WIDTH),
            "degree_taboo": DEGREE_TABOO, "degree_arl": DEGREE_ARL,
            "taboo_alphas": [str(a) for a in TABOO_ALPHAS], "arl_alphas": [str(a) for a in ARL_ALPHAS],
            "cells_json_sha256": CELLS_SHA256,
            "code_sha256": {"taboo_certify": TABOO_SHA256, "c2_refined_registry": sha(HERE.read_bytes())},
            "blocks": blocks, "cpu_seconds_total": cpu}


def verify(outdir: Path, reg: dict) -> dict:
    TC, _ = _import()
    bad = []
    for b in reg["blocks"]:
        if not b.get("certified"):
            continue
        k = b["cell"]
        for r in b["sub_rows"]:
            i = r["sub"]
            for name, fn, fields, key in (("taboo_block", TC.verify_block, ("C_T", "tau"), "taboo_artifact_sha256"),
                                          ("taboo_cell", TC.verify_cell, ("D_lo", "D1", "D2"),
                                           "denominator_artifact_sha256")):
                p = outdir / f"{name}_{k:03d}_{i:02d}.json"
                got = fn(json.loads(p.read_bytes()))
                if got.get("certified") is not True:
                    bad.append(f"{name} {k}.{i}: recomputation does not certify")
                # The recomputed constants live under `recomputed`, not at the top level of verify_block /
                # verify_cell's return. Reading them from the top level yielded None for every field, so every
                # comparison failed and this verifier could never pass -- which is why no run of it was ever
                # committed. Found by running it, as the pre-freeze review (row 79) asked for.
                rec = got.get("recomputed", {})
                for fld in fields:
                    if F(str(rec[fld])) != F(str(r[fld])):
                        bad.append(f"{name} {k}.{i}: {fld} differs")
                if sha(p.read_bytes()) != r[key]:
                    bad.append(f"{name} {k}.{i}: artifact sha differs")
        p = outdir / f"arl_cell_{k:03d}.json"
        got = TC.verify_block(json.loads(p.read_bytes()))
        if got.get("certified") is not True or F(str(got.get("recomputed", {})["tau"])) != F(str(b["Abar"])):
            bad.append(f"arl_cell {k}: recomputation differs")
        if sha(p.read_bytes()) != b["arl"]["arl_artifact_sha256"]:
            bad.append(f"arl_cell {k}: artifact sha differs")
        # the worst-over-sub-blocks composition is itself re-derived
        for fld, agg in (("C_T", max), ("tau", max), ("D1", max), ("D2", max)):
            if F(b[fld]) != agg(F(r[fld]) for r in b["sub_rows"]):
                bad.append(f"cell {k}: {fld} is not the max over its sub-blocks")
        if F(b["D_lo"]) != min(F(r["D_lo"]) for r in b["sub_rows"]):
            bad.append(f"cell {k}: D_lo is not the min over its sub-blocks")
    return {"pass": not bad, "problems": bad[:10], "cells_checked": len(reg["blocks"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("build", "verify"))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--cells", default=",".join(str(k) for k in TAIL))
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--out", help="verify mode: write the result, with host and toolchain, as an evidence artifact")
    a = ap.parse_args()
    outdir = Path(a.outdir)
    cells = [int(x) for x in a.cells.split(",") if x]
    if any(k not in TAIL for k in cells):
        raise SystemExit(f"cells outside the frozen C2 universe {TAIL}")
    if a.mode == "build":
        reg = build(outdir, cells, a.workers)
        data = json.dumps(reg, sort_keys=True, indent=1).encode() + b"\n"
        (outdir / "REGISTRY_C2.json").write_bytes(data)
        print(json.dumps({"certified": reg["certified"], "cells": len(reg["blocks"]),
                          "sub_blocks": sum(b["sub_blocks"] for b in reg["blocks"]),
                          "cpu_seconds_total": round(reg["cpu_seconds_total"], 1), "sha256": sha(data),
                          "per_cell": {str(b["cell"]): {"n": b["sub_blocks"], "certified": b["certified"],
                                                        "C_T": (float(F(b["C_T"])) if b.get("C_T") else None),
                                                        "tau": (float(F(b["tau"])) if b.get("tau") else None),
                                                        "D_lo": (float(F(b["D_lo"])) if b.get("D_lo") else None),
                                                        "D1": (float(F(b["D1"])) if b.get("D1") else None),
                                                        "D2": (float(F(b["D2"])) if b.get("D2") else None),
                                                        "Abar": (float(F(b["Abar"])) if b.get("Abar") else None)}
                                       for b in reg["blocks"]}}, indent=1))
        return 0 if reg["certified"] else 1
    reg = json.loads((outdir / "REGISTRY_C2.json").read_bytes())
    res = verify(outdir, reg)
    if a.out:
        import platform
        try:
            import flint
            import numpy
            tool = {"python_flint": flint.__version__, "numpy": numpy.__version__}
        except Exception:                                   # pragma: no cover - only if the stack is absent
            tool = {}
        res = dict(res, host={"platform": platform.platform(), "machine": platform.machine(),
                              "python": sys.version.split()[0], **tool},
                   artifacts_rechecked=sum(2 * len(b["sub_rows"]) + 1 for b in reg["blocks"]),
                   registry_sha256=sha((outdir / "REGISTRY_C2.json").read_bytes()))
        Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
