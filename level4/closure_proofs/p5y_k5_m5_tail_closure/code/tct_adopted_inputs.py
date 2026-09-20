"""Copy, verbatim, the ADOPTED K1 record fields the tail arithmetic consumes, so that this namespace can be
re-derived from its own committed evidence (review r1 note N2). Pure extraction: no computation, no model quantity.

Every record is checked against the adopted composite export manifest before anything is read from it, and the
emitted fields are exactly those `code/tail_forecast_r2.py` and `code/tct_rule.py` consume:

    C_upper, e0, rho, left, right                      (also in the frozen cover, repeated here for convenience)
    auxiliary_evidence.candidate_suprema['S:r:3'|'Sclosed:0:3'|'h:j:3']    premise (P3') order-3 candidate suprema
    auxiliary_evidence.midpoint_eps['S:r:3'|'Sclosed:3'|'h:j:3']           premise (P3') certified midpoint errors
    eps_cell_refined['H:r']                                               the derived identity gate
    m[1|2|3|5].{R_interval, D_interval, R2_interval, M_R2}                the adopted state at the tail

    python3 -B tct_adopted_inputs.py --records DIR --manifest MANIFEST.json --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

TAIL = (305, 306, 307, 308, 309)
MS = ("1", "2", "3", "5")
SCHEMA = "rebaseguard.p5y.k5.m5-tail.adopted-inputs.v1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    man_raw = Path(a.manifest).read_bytes()
    files = json.loads(man_raw)["files"]
    out = {"schema": SCHEMA, "manifest_sha256": sha(man_raw), "cells": {}}
    for k in TAIL:
        name = f"aux5_CUSUM_{k}_256.json"
        raw = (Path(a.records) / name).read_bytes()
        want = files["k4_records/" + name]
        if sha(raw) != want:
            raise SystemExit(f"record {k} does not match the adopted export manifest")
        rec = json.loads(raw)
        if rec.get("cell_index") != k or rec.get("detector") != "CUSUM":
            raise SystemExit(f"record {k} does not identify itself as this CUSUM cell")
        ae = rec["auxiliary_evidence"]
        cs, me = ae["candidate_suprema"], ae["midpoint_eps"]
        out["cells"][str(k)] = {
            "record_sha256": want,
            "C_upper": rec["C_upper"], "e0": rec["e0"], "rho": rec["rho"],
            "auxiliary_evidence": {
                "candidate_suprema": {key: cs[key] for key in
                                      ["Sclosed:0:3"] + [f"S:{r}:3" for r in range(1, 5)]
                                      + [f"h:{j}:3" for j in range(1, 5)]},
                "midpoint_eps": {key: me[key] for key in
                                 ["Sclosed:3"] + [f"S:{r}:3" for r in range(1, 5)]
                                 + [f"h:{j}:3" for j in range(1, 5)]},
            },
            "eps_cell_refined": {f"H:{r}": rec["eps_cell_refined"][f"H:{r}"] for r in range(5)},
            "m": {m: {"R_interval": {t: rec["m"][m]["R_interval"][t] for t in ("lo", "hi")},
                      "D_interval": {t: rec["m"][m]["D_interval"][t] for t in ("lo", "hi")},
                      "R2_interval": {t: rec["m"][m]["R2_interval"][t] for t in ("lo", "hi")},
                      "M_R2": rec["m"][m]["M_R2"]} for m in MS},
        }
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"cells": len(out["cells"]), "sha256": sha(data)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
