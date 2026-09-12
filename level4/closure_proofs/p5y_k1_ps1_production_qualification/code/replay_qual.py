"""Fresh-process deterministic replay of Phase-4 production-path records: re-execute 6 patches of 3 qualification
cells (one per production group type) through the production per-patch function and compare every scientific leaf
with the Phase-4 records."""
import glob
import json
import sys
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_bint_p1 as BP
import opt_core as OC
import succ_t3 as S3

Q = Path(__file__).resolve().parents[1] / "evidence/qual/chunks"
PICK = {1: [(0, 0), (24, 20)], 150: [(38, 26), (8, 36)], 368: [(51, 63), (63, 54)]}


def strip(r):
    r = {k: v for k, v in r.items() if k not in ("cpu_seconds", "peak_rss_kib")}
    r["modes"]["mid"].pop("cache_hits", None), r["modes"]["mid"].pop("cache_misses", None)
    return r


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    orig = {}
    for f in glob.glob(str(Q / "rec_s*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r["successor_cell"] in PICK and tuple(r["patch"]) in PICK[r["successor_cell"]]:
                orig[(r["successor_cell"], tuple(r["patch"]))] = strip(r)
    res = {}
    with T.scientific_precision():
        for s, ps in PICK.items():
            cands, hashes, C, e0, clsha = S3.cell_inputs(s)
            for (i, j) in ps:
                with BP.p1_lagrange_factor():
                    nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache={}, mode="mid")
                o = orig[(s, (i, j))]["modes"]["mid"]
                res[f"{s}:{i},{j}"] = (nodes == o["nodes"] and geo == o["geo"])
    rep = {"identical": res, "all_identical": all(res.values()) and len(res) == 6}
    (out / "replay.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep))
    return 0 if rep["all_identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
