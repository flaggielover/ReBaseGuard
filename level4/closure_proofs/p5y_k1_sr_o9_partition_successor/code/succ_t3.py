"""Successor T3 midpoint producer: the frozen T2-closed per-patch certifier (t3_patch.core, unchanged) evaluated at
the EXACT successor-cell midpoint e0 only. The whole-cell mode is supplied by the governed mean-value successor in
succ_t3_aggregate (delta_cell = delta_mid + rho*Env), so the interval-e cell mode is not run.
"""
import argparse
import hashlib
import json
import resource
import time
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import t3_patch as TP
import succ_cells as SC
import succ_t1 as S1

SCHEMA = "rebaseguard.p5y.k1.sr.partition-successor.t3-patch-mid.v1"


def cell_inputs(s):
    rec = SC.cell(s)
    built = S1.build(rec)["scientific"]
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
    g = SC.geometry(rec)
    return cands, hashes, Fr(rec["C_upper"]), g["e0"], hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest()


def run_chunk(indices, patches, out_path):
    done, p = set(), Path(out_path)
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
                done.add((r["successor_cell"], tuple(r["patch"])))
            except json.JSONDecodeError:
                break
    with T.scientific_precision():
        inputs = {s: cell_inputs(s) for s in indices}
        with open(p, "a") as fh:
            for (i, j) in patches:
                cache = {}
                for s in indices:
                    if (s, (i, j)) in done:
                        continue
                    cands, hashes, C, e0, clsha = inputs[s]
                    t0 = time.process_time()
                    rec = {"schema": SCHEMA, "successor_cell": s, "successor_cells_sha256": SC.table_sha256(), "patch": [i, j],
                           "candidate_identity_list_sha256": clsha, "modes": {}}
                    with BP.p1_lagrange_factor():
                        nodes, geo, st = TP.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                    rec["modes"]["mid"] = {"nodes": nodes, "geo": geo, "cache_hits": st["hits"], "cache_misses": st["misses"]}
                    rec["cpu_seconds"] = time.process_time() - t0
                    rec["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                    fh.flush()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True, help="comma-separated successor cell indices")
    ap.add_argument("--patches", required=True, help="file with 'i j' lines")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    T.check_threads()
    run_chunk([int(x) for x in a.cells.split(",")],
              [tuple(map(int, l.split())) for l in Path(a.patches).read_text().splitlines() if l.strip()], a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
