"""Phase L: measure cells-outer overhead AND prove per-patch scientific identity.

Runs the SAME patches for the SAME cells under both orderings through the SAME frozen
opt_core.core, then compares the stripped (scientific) records byte-for-byte.
"""
import json, os, sys, time, hashlib, resource
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import opt_core as OC
import succ_t3 as S3
import succ_cells as SC
from flint import ctx

CELLS = [0, 1, 2, 3]
NPATCH = int(os.environ.get("NPATCH", "12"))
LIVE = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
            "p5y_k1_sr_o9_t345_successor/config/live_patches.txt")


def strip(r):
    r = json.loads(json.dumps(r))
    r.pop("cpu_seconds", None); r.pop("peak_rss_kib", None)
    r["modes"]["mid"].pop("cache_hits", None); r["modes"]["mid"].pop("cache_misses", None)
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def one(i, j, s, cands, hashes, C, e0, clsha, cache):
    rec = {"schema": S3.SCHEMA, "successor_cell": s, "successor_cells_sha256": SC.table_sha256(),
           "patch": [i, j], "candidate_identity_list_sha256": clsha, "modes": {}}
    with BP.p1_lagrange_factor():
        nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C,
                                 shared_cache=cache, mode="mid")
    rec["modes"]["mid"] = {"nodes": nodes, "geo": geo,
                           "cache_hits": st["hits"], "cache_misses": st["misses"]}
    return rec, st


def main():
    live = [tuple(map(int, l.split())) for l in LIVE.read_text().splitlines() if l.strip()][:NPATCH]
    with T.scientific_precision():
        assert ctx.prec == 256, ctx.prec
        inp = {s: S3.cell_inputs(s) for s in CELLS}

        # ---- PREDECESSOR: patch-outer / cells-inner, cache shared across the 4 cells
        t0 = time.process_time(); A = {}; hits_a = miss_a = 0
        for (i, j) in live:
            cache = {}
            for s in CELLS:
                cands, hashes, C, e0, clsha = inp[s]
                rec, st = one(i, j, s, cands, hashes, C, e0, clsha, cache)
                A[(s, i, j)] = strip(rec); hits_a += st["hits"]; miss_a += st["misses"]
        cpu_a = time.process_time() - t0

        # ---- SUCCESSOR: cells-outer / patch-inner, cache per (cell, patch)
        t0 = time.process_time(); B = {}; hits_b = miss_b = 0
        for s in CELLS:
            cands, hashes, C, e0, clsha = inp[s]
            for (i, j) in live:
                cache = {}
                rec, st = one(i, j, s, cands, hashes, C, e0, clsha, cache)
                B[(s, i, j)] = strip(rec); hits_b += st["hits"]; miss_b += st["misses"]
        cpu_b = time.process_time() - t0

    same = sum(1 for k in A if A[k] == B[k])
    ha = hashlib.sha256("".join(A[k] for k in sorted(A)).encode()).hexdigest()
    hb = hashlib.sha256("".join(B[k] for k in sorted(B)).encode()).hexdigest()
    print(f"  patches/cell        : {NPATCH}   cells: {CELLS}   records: {len(A)}")
    print()
    print(f"  PREDECESSOR patch-outer : {cpu_a:8.2f} CPU-s   cache hits {hits_a:6d} misses {miss_a:6d}")
    print(f"  SUCCESSOR  cells-outer  : {cpu_b:8.2f} CPU-s   cache hits {hits_b:6d} misses {miss_b:6d}")
    print(f"  overhead                : {cpu_b/cpu_a:.4f}x  ({100*(cpu_b/cpu_a-1):+.1f}%)")
    print()
    print(f"  stripped records identical : {same}/{len(A)}")
    print(f"  predecessor bundle sha256  : {ha}")
    print(f"  successor   bundle sha256  : {hb}")
    print(f"  SCIENTIFIC IDENTITY        : {'BIT-IDENTICAL' if ha == hb else 'DIVERGENT - HARD STOP'}")
    print(json.dumps({"npatch": NPATCH, "cells": CELLS, "cpu_predecessor_s": cpu_a,
                      "cpu_successor_s": cpu_b, "overhead_ratio": cpu_b / cpu_a,
                      "cache_hits_predecessor": hits_a, "cache_hits_successor": hits_b,
                      "records": len(A), "identical": same,
                      "bundle_sha256_predecessor": ha, "bundle_sha256_successor": hb,
                      "identity": ha == hb},
                     indent=1), file=open(os.environ.get("OUT", "/dev/null"), "w"))
    return 0 if ha == hb else 1


if __name__ == "__main__":
    sys.exit(main())
