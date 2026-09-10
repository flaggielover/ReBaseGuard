"""CLI for the T2 closure runs.

case : one (cell, patch) in a fresh process, fresh recomputation (no shared cache)
tile : tile-major -- one patch, several cells, ONE process, PanelShared reused across cells
       through the committed contract_all shared_cache; records tensor accounting.
"""
import argparse
import json
import resource
import time
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES
import sr_o9_bint_p1 as BP
import t2_final_certifier as FC
from flint import arb, arb_mat, arb_poly

# arb_struct is 48 bytes; a 256-bit midpoint needs 4 limbs, held on the heap once it exceeds the
# 2 inline limbs (32 bytes).  ESTIMATE used only for reporting; RSS is measured separately.
BYTES_PER_ARB_256 = 80


def arb_entries(obj, seen):
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    if isinstance(obj, arb):
        return 1
    if isinstance(obj, arb_mat):
        return obj.nrows() * obj.ncols()
    if isinstance(obj, arb_poly):
        return len(obj)
    if isinstance(obj, (list, tuple)):
        return sum(arb_entries(x, seen) for x in obj)
    if isinstance(obj, dict):
        return sum(arb_entries(x, seen) for x in obj.values())
    n = 0
    for name in getattr(type(obj), "__slots__", ()):
        if hasattr(obj, name):
            n += arb_entries(getattr(obj, name), seen)
    for v in getattr(obj, "__dict__", {}).values():
        n += arb_entries(v, seen)
    return n


def case(cell, i, j, out):
    r = FC.run_case(cell, i, j)
    Path(out).write_bytes(T.canonical(r))
    print(json.dumps({**FC.summary(r), "cpu_certify": r["run"]["cpu_seconds_certify"], "rss_kib": r["run"]["peak_rss_kib"]}))


def tile(i, j, cells, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache, rows = {}, []
    t0 = time.process_time()
    for c in cells:
        built = FC.cell_inputs(c)
        r = FC.run_case(c, i, j, shared_cache=cache, built=built)
        (out_dir / f"c{c}_p{i}_{j}.json").write_bytes(T.canonical(r))
        rows.append({"cell": c, "cpu_seconds_certify": r["run"]["cpu_seconds_certify"], "cache": {"hits": r["run"]["cache_hits"], "misses": r["run"]["cache_misses"]},
                     "rss_kib_after": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     "scientific_hash": r["scientific_hash"]})
    total = time.process_time() - t0
    with T.scientific_precision():
        seen = set()
        shared = sum(arb_entries(v, seen) for v in cache.values())
        built = FC.cell_inputs(cells[0])
        cands = [T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]]
        cand_entries = sum(arb_entries(cm, set()) for cm in cands)
        e = T.cell_geometry(T.frozen_cell(cells[0]))["e0"]
        g = PC.patch_geometry(i, j, e)
        pan = PC.panelisation(i, j, g)
        h = pan["h"]
        z_lo = g["L_c"]
        z_hi = z_lo + arb(2) * h
        z_c = (z_lo + z_hi) / arb(2)
        sh = next(iter(cache.values()))
        N = PC.H.panel_moments(z_lo, z_hi, z_c, e, PC.KMAX, h)
        excl = {id(sh)}
        drift = arb_entries(PC.OB.PanelDrift(sh, N), set(excl)) + sum(
            arb_entries(ES.FixedRawShiftDrift(sh, N, s, z_c, h), set(excl)) for s in (1, 2, 3))
        with BP.p1_lagrange_factor():
            strips = arb_entries([ES.StripSide(g, g["L_c"], "L", [0, 1, 2, 3]),
                                  ES.StripSide(g, g["U_c"], "U", [0, 1, 2, 3])], set())
    summ = {"patch": [i, j], "cells": cells, "n_z": pan["n_z"], "per_cell": rows, "process_cpu_seconds": total,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "tensor_accounting": {
                "bytes_per_arb_estimate": BYTES_PER_ARB_256,
                "shared_PanelShared_objects": len(cache), "shared_arb_entries": shared,
                "shared_bytes_estimate": shared * BYTES_PER_ARB_256,
                "per_cell_drift_arb_entries_per_panel": drift,
                "per_cell_drift_bytes_estimate_per_patch": drift * pan["n_z"] * BYTES_PER_ARB_256,
                "per_cell_strip_pair_arb_entries": strips,
                "per_cell_strip_pair_bytes_estimate": strips * BYTES_PER_ARB_256,
                "candidate_arb_entries": cand_entries, "candidate_bytes_estimate": cand_entries * BYTES_PER_ARB_256,
                "candidate_count": len(cands)}}
    (out_dir / f"tile_p{i}_{j}_summary.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summ[k] for k in ("patch", "n_z", "process_cpu_seconds", "peak_rss_kib")}))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("case", "tile"))
    ap.add_argument("--cell", type=int)
    ap.add_argument("--cells", default="0,150,250,275,313,315")
    ap.add_argument("--patch", type=int, nargs=2, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    T.check_threads()
    if a.cmd == "case":
        case(a.cell, *a.patch, a.out)
    else:
        tile(*a.patch, [int(x) for x in a.cells.split(",")], a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
