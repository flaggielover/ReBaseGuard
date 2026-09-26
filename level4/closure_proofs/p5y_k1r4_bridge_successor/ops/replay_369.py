"""369-cell equivalence replay through the GENERATED K1R4 bridge stages (REPLAY mode).

Uses existing historical evidence only: the sealed patch files are decompressed into a
scratch directory and re-aggregated; t4 and t5 are recomputed from that t3. No patch is
solved. The sealed evidence is only ever read.
"""
import gzip
import hashlib
import json
import os
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
          "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"


def setup():
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    sys.path[:0] = [str(NS / "driver")] + [str(PROD / r) for r in auth["pythonpath_rel"]] + [str(PS1 / "driver")]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def replay_cell(s: int) -> dict:
    setup()
    import k1r4_bridge_cells as SC
    SC.set_mode("REPLAY")
    import k1r4_bridge_t3_aggregate as AG
    import k1r4_bridge_t4 as S4
    import k1r4_bridge_t5 as S5
    import sr_o9_candidates as T
    import multihost as M
    sealed = json.loads((PS1 / f"production/cells/{s:04d}.json").read_text())
    ev = sealed["evidence"]
    h3 = json.loads(Path(ev["t3"]["path"]).read_text())
    h4 = json.loads(Path(ev["t4"]["path"]).read_text())
    h5_bytes = Path(ev["t5"]["path"]).read_bytes()
    t0 = time.process_time()
    with tempfile.TemporaryDirectory(prefix=f"k1r4replay{s:04d}-") as td:
        f = Path(td) / f"patches_{s:04d}.jsonl"
        with gzip.open(ev["patches_gz"]["path"], "rb") as z:
            f.write_bytes(z.read())
        with T.scientific_precision():
            rec = SC.cell(s)
            t3 = AG.aggregate(s, [str(f)])
            t4 = S4.t4(t3, rec)
            evd = {"t3_record_sha256": t3["t3_record_sha256"],
                   "t4_record_sha256": t4["t4_record_sha256"],
                   "t3_file_sha256": sha(AG.canonical(t3)), "t4_file_sha256": sha(S4.canonical(t4)),
                   "successor_cells_sha256": SC.table_sha256(), "task_id": sealed["task_id"]}
            t5 = S5.obligations(t3, t4, evd, rec)
    t5_bytes = S5.canonical(t5)
    sch = hashlib.sha256(M.canonical({
        "t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
        "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}) + b"\n").hexdigest()
    diffs = []
    if t3["t3_record_sha256"] != h3["t3_record_sha256"]:
        diffs.append("t3_record_sha256")
    if t4["t4_record_sha256"] != h4["t4_record_sha256"]:
        diffs.append("t4_record_sha256")
    hc = [o["certificate_hash"] for o in json.loads(h5_bytes)["obligations"]]
    rc = [o["certificate_hash"] for o in t5["obligations"]]
    diffs += [f"t5_certificate_hash[{i}]" for i, (a, b) in enumerate(zip(hc, rc)) if a != b]
    if len(hc) != len(rc):
        diffs.append("t5_obligation_count")
    if sch != sealed["scientific_content_hash"]:
        diffs.append("scientific_content_hash")
    return {"cell": s, "leaf_differences": diffs, "t5_bytes_identical": t5_bytes == h5_bytes,
            "t3_file_identical": sha(AG.canonical(t3)) == ev["t3"]["sha256"],
            "t4_file_identical": sha(S4.canonical(t4)) == ev["t4"]["sha256"],
            "scientific_content_hash_match": sch == sealed["scientific_content_hash"],
            "cpu_s": round(time.process_time() - t0, 2)}


def main(argv) -> int:
    cells = list(range(369)) if not argv else [int(x) for x in argv[0].split(",")]
    procs = int(os.environ.get("K1R4_REPLAY_PROCS", "24"))
    t0 = time.time()
    with Pool(procs) as pool:
        res = pool.map(replay_cell, cells, chunksize=1)
    bad = [r for r in res if r["leaf_differences"]]
    out = {"schema": "rebaseguard.p5y.k1r4.historical-replay.v1", "cells_replayed": len(res),
           "cells_equivalent": len(res) - len(bad),
           "scientific_leaf_differences": sum(len(r["leaf_differences"]) for r in res),
           "t5_bytes_identical": sum(r["t5_bytes_identical"] for r in res),
           "t3_files_identical": sum(r["t3_file_identical"] for r in res),
           "t4_files_identical": sum(r["t4_file_identical"] for r in res),
           "scientific_content_hash_matches": sum(r["scientific_content_hash_match"] for r in res),
           "cpu_s_total": round(sum(r["cpu_s"] for r in res), 1),
           "wall_s": round(time.time() - t0, 1), "patch_solves": 0,
           "mismatching_cells": [(r["cell"], r["leaf_differences"][:4]) for r in bad][:20],
           "per_cell": res}
    name = "REPLAY_369.json" if len(cells) == 369 else f"REPLAY_TRIAL_{'_'.join(map(str,cells[:4]))}.json"
    (NS / "evidence" / name).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_cell"}, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
