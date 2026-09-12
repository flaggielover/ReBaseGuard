"""Phase 1: cProfile the real PS1 midpoint certifier (t3_patch.core via succ_t3) on given patches of one successor cell."""
import cProfile
import json
import pstats
import sys
import time
from pathlib import Path

import sr_o9_candidates as T
import succ_t3 as S3

s, outdir = int(sys.argv[1]), Path(sys.argv[2])
patches = [tuple(map(int, p.split(","))) for p in sys.argv[3].split(";")]
outdir.mkdir(parents=True, exist_ok=True)
T.check_threads()
t0 = time.process_time()
pr = cProfile.Profile()
pr.enable()
with T.scientific_precision():
    inputs = S3.cell_inputs(s)
pr.disable()
t_inputs = time.process_time() - t0
res = {"cell": s, "cell_inputs_cpu_s": t_inputs, "patches": {}}
import sr_o9_bint_p1 as BP
import t3_patch as TP
cands, hashes, C, e0, clsha = inputs
for (i, j) in patches:
    cache = {}
    t1 = time.process_time()
    pr.enable()
    with T.scientific_precision():
        with BP.p1_lagrange_factor():
            nodes, geo, st = TP.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
    pr.disable()
    res["patches"][f"{i},{j}"] = {"cpu_s": time.process_time() - t1, "n_z": geo["n_z"], "contract_evaluations": geo["contract_evaluations"],
                                   "cache_misses": st["misses"], "cache_hits": st["hits"]}
pr.dump_stats(str(outdir / f"prof_s{s}.pstats"))
ps = pstats.Stats(pr)
rows = []
for (fn, ln, name), (cc, nc, tt, ct, callers) in ps.stats.items():
    rows.append({"func": f"{Path(fn).name}:{ln}:{name}", "tottime": tt, "cumtime": ct, "ncalls": nc})
rows.sort(key=lambda r: -r["tottime"])
res["top_tottime"] = rows[:45]
res["top_cumtime"] = sorted(rows, key=lambda r: -r["cumtime"])[:45]
(outdir / f"profile_s{s}.json").write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k in ("cell", "cell_inputs_cpu_s", "patches")}))
for r in res["top_tottime"][:30]:
    print(f"{r['tottime']:9.2f} {r['cumtime']:9.2f} {r['ncalls']:>9} {r['func']}")
