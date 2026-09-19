"""K5 coverage map r4 (descriptive composition; no new arithmetic): the adopted map r3 (6d598dc5, Perron-deflated
successor) plus the SEALED, adjudicated theorem-TC consumption. Cells that pass now but were OPEN in r3 are attributed
to the TC successor; every other cell keeps its r3 entry. Refuses if any r3 PASS cell is not PASS now.

Lives under evidence/tc_r1/ because the rest of the namespace is frozen.

    python3 -B coverage_map_r4.py --result TC_CONSUMPTION.json --result-sha256 SHA --out K5_COVERAGE_MAP_R4.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[6]
R3 = REPO / ("level4/closure_proofs/p5y_k5_perron_deflated_resolvent/evidence/successor_r1/K5_COVERAGE_MAP_R3.json")
R3_SHA256 = "6d598dc53293f91cdffb99f8fb3a0080542d8d0ca75c3110cc5fcc4db97a544d"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def expand(rs):
    return {k for lo, hi in rs for k in range(lo, hi + 1)}


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def build(result_path: Path, result_sha256: str) -> dict:
    raw = result_path.read_bytes()
    if sha(raw) != result_sha256:
        raise SystemExit("sealed result hash mismatch")
    r3raw = R3.read_bytes()
    if sha(r3raw) != R3_SHA256:
        raise SystemExit("adopted map r3 hash mismatch")
    res, r3 = json.loads(raw), json.loads(r3raw)
    out = {"schema": "rebaseguard.p5y.k5.lower-front-order3.coverage-map.v4", "detector": "CUSUM",
           "inputs": {"coverage_map_r3_sha256": R3_SHA256, "tc_consumption_sha256": result_sha256,
                      "protocol_sha256": res.get("protocol_sha256"), "freeze_commit": res.get("freeze_commit"),
                      "tc_index_sha256": (res.get("verified") or {}).get("tc_index_sha256")},
           "attribution_rule": "cells passing now but OPEN in r3 are attributed to the theorem-TC successor (Taylor-cell "
                               "whole-cell R'' enclosure with order-3 midpoint candidates, sealed consumption); every "
                               "other cell keeps its r3 attribution", "per_m": {}}
    union_open = set()
    for m, x in res["consumptions"].items():
        now = expand(x["pass_ranges"])
        was = expand(r3["per_m"][m]["pass_ranges"])
        if not was <= now:
            raise SystemExit(f"m={m}: cells {sorted(was - now)[:5]} passed in r3 but not now (impossible)")
        cells = []
        for c in r3["per_m"][m]["cells"]:
            k = c["cell"]
            if k in now and k not in was:
                c = {"cell": k, "verdict": "PASS", "route": f"theorem_TC:{x['via'].get(str(k))}",
                     "evidence": "p5y_k5_lower_front_order3 sealed TC consumption", "evidence_sha256": result_sha256,
                     "k1_record_sha256": c.get("k1_record_sha256")}
            cells.append(c)
        opened = sorted(set(range(310)) - now)
        union_open |= set(opened)
        out["per_m"][m] = {"pass_ranges": ranges(now), "open_ranges": ranges(opened), "open_count": len(opened),
                           "newly_passing": ranges(now - was), "newly_passing_count": len(now - was), "cells": cells}
    out["union_open_ranges"] = ranges(union_open)
    out["union_open_count"] = len(union_open)
    out["K5_COVERAGE_COMPLETE"] = not union_open
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--result-sha256", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = build(Path(a.result), a.result_sha256)
    data = json.dumps(out, indent=1, sort_keys=True) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({m: {k: v for k, v in x.items() if k != "cells"} for m, x in out["per_m"].items()}, indent=1),
          out["union_open_ranges"], sha(data.encode()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
