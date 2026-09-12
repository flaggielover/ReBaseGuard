"""Run the generated opt core (patch-outer, cells-inner, one shared per-patch cache) on real PS1 cells and compare
every (cell, patch) scientific record (nodes + geometry) against the COMMITTED certified record of that cell."""
import glob
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import opt_core as OC
import succ_t3 as S3

CERT = Path(S3.SC.NS) / "evidence/certified"
PARENT = {360: 313, 361: 313, 362: 313, 363: 313, 150: 150, 275: 275, 368: 315}


def h(nodes, geo):
    return hashlib.sha256(json.dumps({"nodes": nodes, "geo": geo}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    cells = [int(x) for x in sys.argv[1].split(",")]
    patches = [tuple(map(int, p.split(","))) for p in sys.argv[2].split(";")]
    out = Path(sys.argv[3])
    want = set(patches)
    committed = {}
    for s in cells:
        for f in glob.glob(str(CERT / f"parent_{PARENT[s]}/chunks/rec_*.jsonl.gz")):
            for line in gzip.open(f, "rt"):
                r = json.loads(line)
                if r["successor_cell"] == s and tuple(r["patch"]) in want:
                    committed[(s, tuple(r["patch"]))] = h(r["modes"]["mid"]["nodes"], r["modes"]["mid"]["geo"])
    T.check_threads()
    rows = []
    c0 = time.process_time()
    with T.scientific_precision():
        inp = {s: S3.cell_inputs(s) for s in cells}
        for (i, j) in patches:
            cache = {}
            for s in cells:
                cands, hashes, C, e0, _ = inp[s]
                t = time.process_time()
                with BP.p1_lagrange_factor():
                    nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                rows.append({"cell": s, "patch": [i, j], "cpu_s": time.process_time() - t, "n_z": geo["n_z"],
                             "match_committed": h(nodes, geo) == committed[(s, (i, j))]})
    res = {"cells": cells, "n": len(rows), "all_match": all(r["match_committed"] for r in rows), "cpu_s": time.process_time() - c0, "rows": rows}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("cells", "n", "all_match", "cpu_s")}))


if __name__ == "__main__":
    main()
