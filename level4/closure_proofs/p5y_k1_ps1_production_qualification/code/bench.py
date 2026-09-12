"""Phase 3 benchmark: the real PS1 midpoint certifier, patch-outer / cells-inner with one shared per-patch cache
(the committed architecture of succ_t3.run_chunk), for a given batch of successor cells and patches. Records, per
(cell, patch): CPU seconds and the sha256 of the canonical SCIENTIFIC record (runtime fields removed), so every
configuration can be compared leaf-for-leaf with every other and with the committed certified records."""
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import t3_patch as TP
import succ_t3 as S3


def sci_hash(nodes, geo):
    return hashlib.sha256(json.dumps({"nodes": nodes, "geo": geo}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    cells = [int(x) for x in sys.argv[1].split(",")]
    patches = [tuple(map(int, p.split(","))) for p in sys.argv[2].split(";")]
    out = Path(sys.argv[3])
    T.check_threads()
    w0, c0 = time.perf_counter(), time.process_time()
    rows = []
    with T.scientific_precision():
        inputs = {s: S3.cell_inputs(s) for s in cells}
        c_in = time.process_time() - c0
        for (i, j) in patches:
            cache = {}
            for s in cells:
                cands, hashes, C, e0, _ = inputs[s]
                t = time.process_time()
                with BP.p1_lagrange_factor():
                    nodes, geo, st = TP.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                rows.append({"cell": s, "patch": [i, j], "cpu_s": time.process_time() - t, "n_z": geo["n_z"],
                             "hits": st["hits"], "misses": st["misses"], "sci_sha256": sci_hash(nodes, geo)})
    res = {"cells": cells, "patches": [list(p) for p in patches], "cell_inputs_cpu_s": c_in,
           "cpu_s": time.process_time() - c0, "wall_s": time.perf_counter() - w0,
           "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, "rows": rows}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("cells", "cpu_s", "wall_s", "peak_rss_mib")}))


if __name__ == "__main__":
    main()
