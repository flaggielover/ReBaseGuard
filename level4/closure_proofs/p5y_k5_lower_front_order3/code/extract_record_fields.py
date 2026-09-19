"""Extract, from the adopted CUSUM K1 records (manifest 29ad1f9b...), the midpoint residual fields a Taylor-cell
forecast needs. Read-only, deterministic; no model evaluation.

For every requested cell and r = 0..4 it copies (exact rational strings):
    delta_mid of F_r, dF_r, H_r;  eps_mid of the source nodes (Sclosed:k for r = 0, S:r:k otherwise), k = 0, 1, 2;
    the Aux3 order-3 source midpoint eps (auxiliary_evidence.midpoint_eps: Sclosed:3 / S:r:3);
    rho, e0, C_upper; each record's sha256 is checked against the export manifest.

    python -B extract_record_fields.py --records DIR --manifest MANIFEST.json --cells 11-44 --out FIELDS.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def src(r: int, k: int) -> str:
    return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.cells.split("-"))
    man = json.loads(Path(a.manifest).read_bytes())
    files = man["files"]
    out = {"schema": "rebaseguard.p5y.k5.lower-front-order3.record-fields.v1",
           "manifest_sha256": hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest(), "cells": {}}
    for k in range(lo, hi + 1):
        name = f"aux5_CUSUM_{k}_256.json"
        raw = (Path(a.records) / name).read_bytes()
        want = files["k4_records/" + name]
        if hashlib.sha256(raw).hexdigest() != want:
            raise SystemExit(f"record {k} does not match the manifest")
        rec = json.loads(raw)
        o, em, am = rec["objects"], rec["eps_mid"], rec["auxiliary_evidence"]["midpoint_eps"]
        row = {"record_sha256": want, "rho": rec["rho"], "e0": rec["e0"], "C_upper": rec["C_upper"], "r": {}}
        for r in range(5):
            row["r"][str(r)] = {
                "dF": o[f"F_{r}"]["delta_mid"], "dD": o[f"dF_{r}"]["delta_mid"], "dH": o[f"H_{r}"]["delta_mid"],
                "s0": em[src(r, 0)], "s1": em[src(r, 1)], "s2": em[src(r, 2)],
                "s3": am["Sclosed:3" if r == 0 else f"S:{r}:3"],
            }
        out["cells"][str(k)] = row
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print("cells", len(out["cells"]), "sha256", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
