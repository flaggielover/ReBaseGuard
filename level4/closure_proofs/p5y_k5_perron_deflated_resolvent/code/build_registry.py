"""Build and verify the CERTIFIED operator registry of theorem AD (operator only; no source, no K1 record, no R value).

    build   12 taboo e-blocks of width 1/100 on [0, 12/100] (degree-20 supersolution, Lemma T: C_T, tau), then for every
            frozen cover cell k in CELLS: a whole-kernel ARL supersolution uniform on the cell (Abar >= E_a[tau]) and the
            taboo objects d, d', d'' (D_lo, D1, D2 uniform on the cell), using tau and C_T of the blocks meeting the cell.
            Deterministic parameter ladders (operator-only; no record is ever read).
    verify  recompute every artifact from its stored exact payload and compare every certified field.

    python -B code/build_registry.py build --outdir DIR --workers 7
    python -B code/build_registry.py verify --outdir DIR --workers 7
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(REPO / "level4/closure_proofs/p5y_k5_order3_readiness_audit/code"))

CELLS_JSON = REPO / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json"
CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"
BLOCK_EDGES = [F(i, 100) for i in range(0, 13)]
CELLS = tuple(range(0, 149))
DEGREE = 20
TABOO_ALPHAS = (F(6, 5), F(13, 10), F(7, 5))
SCHEMA = "rebaseguard.p5y.k5.perron-deflation.operator-registry.v1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cover():
    import k5_minimality as KM
    if sha(CELLS_JSON.read_bytes()) != CELLS_SHA256:
        raise SystemExit("cells.json does not match its pin")
    cells = KM.load_cells(CELLS_JSON, "CUSUM")
    return {c["index"]: (KM.rat(c["left"]), KM.rat(c["right"]), KM.rat(c["e0"]), KM.rat(c["rho"])) for c in cells}


def full_alphas(rho: F):
    return (1 + 200 * rho + F(2, 100), 1 + 400 * rho + F(5, 100), F(5, 4), F(7, 5))


def _block(args):
    import taboo_certify as TC
    i, outdir = args
    lo, hi = BLOCK_EDGES[i], BLOCK_EDGES[i + 1]
    for a in TABOO_ALPHAS:
        art = TC.block_artifact(lo, hi, a, F(0), 2, DEGREE, False)
        if art["certified"]:
            break
    path = Path(outdir) / f"taboo_block_{i:02d}.json"
    path.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    return i, art["certified"], art["C_T"], art["tau"], sha(path.read_bytes())


def _cell(args):
    import taboo_certify as TC
    k, x_lo, x_hi, e0, rho, tau, C, outdir = args
    for a in full_alphas(rho):
        fa = TC.block_artifact(x_lo, x_hi, a, F(2), 2, 12, True)
        if fa["certified"]:
            break
    fp = Path(outdir) / f"arl_cell_{k:03d}.json"
    fp.write_text(json.dumps(fa, indent=1, sort_keys=True) + "\n")
    da = TC.cell_artifact(e0, rho, tau, C, degree=DEGREE)
    dp = Path(outdir) / f"taboo_cell_{k:03d}.json"
    dp.write_text(json.dumps(da, indent=1, sort_keys=True) + "\n")
    return {"cell": k, "e_lo": str(x_lo), "e_hi": str(x_hi), "Abar": fa["tau"], "arl_certified": fa["certified"],
            "C_T": str(C), "tau": str(tau), "D_lo": da["D_lo"], "D1": da["D1"], "D2": da["D2"],
            "D_certified": da["certified"], "arl_artifact_sha256": sha(fp.read_bytes()),
            "taboo_cell_artifact_sha256": sha(dp.read_bytes())}


def build(outdir: Path, workers: int) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    cov = cover()
    with ProcessPoolExecutor(workers) as ex:
        blocks = list(ex.map(_block, [(i, str(outdir)) for i in range(len(BLOCK_EDGES) - 1)]))
    btab = {i: {"e_lo": str(BLOCK_EDGES[i]), "e_hi": str(BLOCK_EDGES[i + 1]), "certified": ok, "C_T": c, "tau": t,
                "artifact_sha256": h} for i, ok, c, t, h in blocks}
    if not all(b["certified"] for b in btab.values()):
        raise SystemExit("a taboo block did not certify")
    jobs = []
    for k in CELLS:
        x_lo, x_hi, e0, rho = cov[k]
        hit = [b for b in btab.values() if F(b["e_lo"]) < x_hi and x_lo < F(b["e_hi"])]
        if not hit or min(F(b["e_lo"]) for b in hit) > x_lo or max(F(b["e_hi"]) for b in hit) < x_hi:
            raise SystemExit(f"cell {k} not covered by the taboo blocks")
        tau = max(F(b["tau"]) for b in hit)
        C = max(F(b["C_T"]) for b in hit)
        jobs.append((k, x_lo, x_hi, e0, rho, tau, C, str(outdir)))
    with ProcessPoolExecutor(workers) as ex:
        cells = list(ex.map(_cell, jobs))
    ok = all(c["arl_certified"] and c["D_certified"] for c in cells)
    reg = {"schema": SCHEMA, "rule": "r2", "certified": ok, "operator_only": True,
           "cells_json_sha256": CELLS_SHA256, "degree_taboo": DEGREE, "taboo_blocks": btab,
           "blocks": [{"e_lo": c["e_lo"], "e_hi": c["e_hi"], "cell": c["cell"], "Abar": c["Abar"], "C_T": c["C_T"],
                       "tau": c["tau"], "D_lo": c["D_lo"], "D1": c["D1"], "D2": c["D2"],
                       "arl_artifact_sha256": c["arl_artifact_sha256"],
                       "taboo_cell_artifact_sha256": c["taboo_cell_artifact_sha256"]} for c in cells],
           "code_sha256": {p.name: sha(p.read_bytes()) for p in (HERE, HERE.parent / "taboo_certify.py")}}
    (outdir / "REGISTRY.json").write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")
    return reg


def assemble(outdir: Path) -> dict:
    """Rebuild REGISTRY.json deterministically from the artifacts already in outdir (no computation)."""
    cov = cover()
    btab = {}
    for i in range(len(BLOCK_EDGES) - 1):
        p = outdir / f"taboo_block_{i:02d}.json"
        a = json.loads(p.read_text())
        if F(a["e_lo"]) != BLOCK_EDGES[i] or F(a["e_hi"]) != BLOCK_EDGES[i + 1] or a.get("kind") != "taboo":
            raise SystemExit(f"taboo block {i} does not match the frozen block edges")
        btab[i] = {"e_lo": a["e_lo"], "e_hi": a["e_hi"], "certified": a["certified"], "C_T": a["C_T"], "tau": a["tau"],
                   "artifact_sha256": sha(p.read_bytes())}
    blocks, ok = [], all(b["certified"] for b in btab.values())
    for k in CELLS:
        x_lo, x_hi, e0, rho = cov[k]
        hit = [b for b in btab.values() if F(b["e_lo"]) < x_hi and x_lo < F(b["e_hi"])]
        tau, C = max(F(b["tau"]) for b in hit), max(F(b["C_T"]) for b in hit)
        fp, dp = outdir / f"arl_cell_{k:03d}.json", outdir / f"taboo_cell_{k:03d}.json"
        fa, da = json.loads(fp.read_text()), json.loads(dp.read_text())
        if (F(fa["e_lo"]), F(fa["e_hi"])) != (x_lo, x_hi) or fa.get("kind") != "full":
            raise SystemExit(f"ARL artifact of cell {k} is not bound to the cell")
        if (F(da["e0"]), F(da["rho"]), F(da["tau"]), F(da["C_T"])) != (e0, rho, tau, C):
            raise SystemExit(f"taboo cell artifact {k} is not bound to the cell and its blocks")
        ok = ok and fa["certified"] and da["certified"]
        blocks.append({"e_lo": str(x_lo), "e_hi": str(x_hi), "cell": k, "Abar": fa["tau"], "C_T": str(C),
                       "tau": str(tau), "D_lo": da["D_lo"], "D1": da["D1"], "D2": da["D2"],
                       "arl_artifact_sha256": sha(fp.read_bytes()), "taboo_cell_artifact_sha256": sha(dp.read_bytes())})
    reg = {"schema": SCHEMA, "rule": "r2", "certified": ok, "operator_only": True,
           "cells_json_sha256": CELLS_SHA256, "degree_taboo": DEGREE, "taboo_blocks": btab, "blocks": blocks,
           "code_sha256": {p.name: sha(p.read_bytes()) for p in (HERE, HERE.parent / "taboo_certify.py")}}
    (outdir / "REGISTRY.json").write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")
    return reg


def _verify_one(path: str):
    import taboo_certify as TC
    art = json.loads(Path(path).read_text())
    r = TC.verify_cell(art) if art["schema"] == TC.SCHEMA_CELL else TC.verify_block(art)
    return Path(path).name, r["identical"], r["certified"]


def verify(outdir: Path, workers: int) -> dict:
    reg = json.loads((outdir / "REGISTRY.json").read_text())
    files = sorted(str(p) for p in outdir.glob("*.json") if p.name != "REGISTRY.json")
    want = {**{f"taboo_block_{int(i):02d}.json": b["artifact_sha256"] for i, b in reg["taboo_blocks"].items()},
            **{f"arl_cell_{b['cell']:03d}.json": b["arl_artifact_sha256"] for b in reg["blocks"]},
            **{f"taboo_cell_{b['cell']:03d}.json": b["taboo_cell_artifact_sha256"] for b in reg["blocks"]}}
    bad_hash = [n for n, h in want.items() if sha((outdir / n).read_bytes()) != h]
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_verify_one, files))
    return {"artifacts": len(res), "hash_mismatch": bad_hash,
            "not_identical": [n for n, same, _ in res if not same], "not_certified": [n for n, _, ok in res if not ok],
            "pass": not bad_hash and all(s and c for _, s, c in res) and len(res) == len(want)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("build", "verify", "assemble"))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    if a.cmd == "assemble":
        out = assemble(Path(a.outdir))
    else:
        out = build(Path(a.outdir), a.workers) if a.cmd == "build" else verify(Path(a.outdir), a.workers)
    print(json.dumps({k: v for k, v in out.items() if k not in ("blocks", "taboo_blocks")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
