"""Compare the frozen core (t3_patch.core) and the generated opt core (opt_core.core) on real PS1 cells/patches:
every node record and the geometry must be identical; also report CPU of both."""
import hashlib
import json
import sys
import time
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import t3_patch as TP
import opt_core as OC
import succ_t3 as S3


def h(nodes, geo):
    return hashlib.sha256(json.dumps({"nodes": nodes, "geo": geo}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


cells = [int(x) for x in sys.argv[1].split(",")]
patches = [tuple(map(int, p.split(","))) for p in sys.argv[2].split(";")]
out = Path(sys.argv[3])
T.check_threads()
rows = []
with T.scientific_precision():
    inp = {s: S3.cell_inputs(s) for s in cells}
    for (i, j) in patches:
        for impl, fn in (("frozen", TP.core), ("opt", OC.core)):
            cache = {}
            for s in cells:
                cands, hashes, C, e0, _ = inp[s]
                t = time.process_time()
                with BP.p1_lagrange_factor():
                    nodes, geo, st = fn(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                rows.append({"impl": impl, "cell": s, "patch": [i, j], "cpu_s": time.process_time() - t, "sci": h(nodes, geo)})
res = {"rows": rows}
pairs = {}
for r in rows:
    pairs.setdefault((r["cell"], tuple(r["patch"])), {})[r["impl"]] = r
res["identical"] = all(v["frozen"]["sci"] == v["opt"]["sci"] for v in pairs.values())
res["cpu_frozen"] = sum(r["cpu_s"] for r in rows if r["impl"] == "frozen")
res["cpu_opt"] = sum(r["cpu_s"] for r in rows if r["impl"] == "opt")
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: res[k] for k in ("identical", "cpu_frozen", "cpu_opt")}))
