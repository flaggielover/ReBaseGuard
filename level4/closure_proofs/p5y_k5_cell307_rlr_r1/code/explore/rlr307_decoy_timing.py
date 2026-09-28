"""PRE-FREEZE EXPLORATION (not qualification evidence): cost of one pinned RLR block rung on a DECOY sub-block.

Purpose: size the degree ladder and the wall caps of the protocol before it is frozen. Decoys are real cover cells
outside the quarantined band [6/5, 13/5] and its mirror (297 below it, 316 above it); cells 305-309 are refused.
Only runtime, memory and the certification status are reported by the summary; the exact record is kept in the
output file as decoy evidence (a latent-proxy class: never to be juxtaposed with any tail-cell number).

    python3.14 -I -S -B rlr307_decoy_timing.py --cell 297 --block 0 --degree 4 --out FILE
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parents[1]
REPO = HERE.parents[5]
sys.path.insert(0, str(CODE))
import rlr307_guard as guard  # noqa: E402
import rlr307_pinned as pinned  # noqa: E402
import rlr307_stage1 as S1  # noqa: E402
import rlr307_ledger as L  # noqa: E402

CELLS_JSON = REPO / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json"
DECOY_CELLS = (297, 316)


def cover(k: int) -> tuple:
    for c in json.loads(CELLS_JSON.read_bytes()):
        if c["detector"] == "CUSUM" and c["index"] == k:
            assert c["left"][1] == "0/1" and c["right"][1] == "0/1"
            return F(c["left"][0]), F(c["right"][0])
    raise KeyError(k)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--block", type=int, required=True)
    ap.add_argument("--degree", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cell not in DECOY_CELLS:
        raise SystemExit(f"cell {a.cell} is not a declared decoy")
    lo, hi = cover(a.cell)
    guard.guard_drift(lo, hi)                                   # refuses anything meeting the band
    b = S1.blocks_for(lo, hi)[a.block]
    mods = pinned.load_certifier(REPO, guard)
    L.log("code/explore/rlr307_decoy_timing.py", "NONTARGET_DECOY",
          f"pre-freeze cost exploration: decoy cell {a.cell} sub-block {a.block} degree {a.degree}",
          drifts=[[S1.fs(b["hull_lo"]), S1.fs(b["hull_hi"])]], notes="outside [6/5,13/5] and mirror; guard passed")
    t0 = time.time()
    rec = S1.certify_rung(mods, b["hull_lo"], b["hull_hi"], a.degree)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    out = {"schema": "rebaseguard.p5y.k5.cell307-rlr-r1.explore-timing.v1", "decoy_cell": a.cell,
           "block": {k: S1.fs(v) if isinstance(v, F) else v for k, v in b.items()}, "degree": a.degree,
           "status": rec.get("status"), "wall_seconds": round(time.time() - t0, 1), "cpu_seconds": rec["_cpu_seconds"],
           "peak_rss_bytes": ru.ru_maxrss, "log_sha256": S1.log_digest(rec["_log"]), "log_lines": len(rec["_log"]),
           "record": {k: v for k, v in rec.items() if not k.startswith("_")}, "identity": mods["_identity"],
           "latent_proxy": "decoy values; never juxtapose with any tail-cell number"}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"decoy cell {a.cell} block {a.block} d={a.degree}: {out['status']} wall {out['wall_seconds']} s "
          f"rss {out['peak_rss_bytes'] >> 20} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
