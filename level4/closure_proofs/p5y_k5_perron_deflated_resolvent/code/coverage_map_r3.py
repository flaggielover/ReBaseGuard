"""K5 coverage map r3 (descriptive composition; no new arithmetic): the adopted map r2 (ec5c3926) plus the SEALED,
adjudicated Perron-deflated consumption. Cells that pass now but were OPEN in r2 are attributed to the successor; every
other cell keeps its r2 entry. Refuses if any r2 PASS cell is not PASS now (the successor is monotone by construction).

    python3 -B code/coverage_map_r3.py --result SEALED.json --result-sha256 SHA --out K5_COVERAGE_MAP_R3.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
R2 = REPO / "level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_COVERAGE_MAP.json"
R2_SHA256 = "ec5c3926a09b8c8a3df4c09359c9ebb80a2083bb457c0b7f5cee4ceea0064e01"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def expand(ranges):
    return {k for lo, hi in ranges for k in range(lo, hi + 1)}


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
    r2raw = R2.read_bytes()
    if sha(r2raw) != R2_SHA256:
        raise SystemExit("adopted map r2 hash mismatch")
    res, r2 = json.loads(raw), json.loads(r2raw)
    out = {"schema": "rebaseguard.p5y.k5.perron-deflation.coverage-map.v3", "detector": "CUSUM",
           "inputs": {"coverage_map_r2_sha256": R2_SHA256, "deflated_consumption_sha256": result_sha256,
                      "protocol_sha256": res.get("protocol_sha256"), "freeze_commit": res.get("freeze_commit"),
                      "evaluation_head": res.get("evaluation_head")},
           "attribution_rule": "cells passing now but OPEN in r2 are attributed to the Perron-deflated successor (theorem "
                               "AD, sealed consumption); every other cell keeps its r2 attribution", "per_m": {}}
    union_open = set()
    for m, x in res["consumptions"].items():
        now = expand(x["pass_ranges"])
        was = expand(r2["per_m"][m]["pass_ranges"])
        if not was <= now:
            raise SystemExit(f"m={m}: cells {sorted(was - now)[:5]} passed in r2 but not now (impossible)")
        cells = []
        for c in r2["per_m"][m]["cells"]:
            k = c["cell"]
            if k in now and k not in was:
                c = {"cell": k, "verdict": "PASS", "route": f"deflated_AD:{x['via'].get(str(k))}",
                     "evidence": "p5y_k5_perron_deflated_resolvent sealed consumption", "evidence_sha256": result_sha256,
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
