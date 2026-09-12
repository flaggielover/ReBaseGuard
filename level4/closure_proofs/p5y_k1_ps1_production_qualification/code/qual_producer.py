"""Phase 4 cost qualification producer: the PRODUCTION unit. For each deterministic cell GROUP (up to 4 consecutive
successor cells), patch-outer / cells-inner with one shared per-patch panel cache (drift-independent PanelShared
reuse), using the production per-patch function (generated opt_core.core), over one chunk of the frozen live patches.
Groups are processed one after another. Record schema = succ_t3 records."""
import json
import resource
import sys
import time
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import opt_core as OC
import succ_t3 as S3
import succ_cells as SC


def main():
    groups = [[int(x) for x in g.split(",")] for g in sys.argv[1].split(";")]
    pfile = Path(sys.argv[2])
    patches = [tuple(map(int, l.split())) for l in pfile.read_text().splitlines() if l.strip()]
    outdir = Path(sys.argv[3])
    T.check_threads()
    with T.scientific_precision():
        for grp in groups:
            t_in = time.process_time()
            inp = {s: S3.cell_inputs(s) for s in grp}
            t_in = time.process_time() - t_in
            fhs = {s: open(outdir / f"rec_s{s}_{pfile.name}.jsonl", "w") for s in grp}
            for (i, j) in patches:
                cache = {}
                for s in grp:
                    cands, hashes, C, e0, clsha = inp[s]
                    t0 = time.process_time()
                    rec = {"schema": S3.SCHEMA, "successor_cell": s, "successor_cells_sha256": SC.table_sha256(), "patch": [i, j],
                           "candidate_identity_list_sha256": clsha, "modes": {}}
                    with BP.p1_lagrange_factor():
                        nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                    rec["modes"]["mid"] = {"nodes": nodes, "geo": geo, "cache_hits": st["hits"], "cache_misses": st["misses"]}
                    rec["cpu_seconds"] = time.process_time() - t0
                    rec["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    fhs[s].write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                    fhs[s].flush()
            for fh in fhs.values():
                fh.close()
            (outdir / f"inputs_g{grp[0]}_{pfile.name}.json").write_text(json.dumps({"group": grp, "cell_inputs_cpu_s": t_in}))


if __name__ == "__main__":
    main()
