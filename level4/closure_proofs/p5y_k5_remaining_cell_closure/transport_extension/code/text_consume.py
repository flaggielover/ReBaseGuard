"""T-EXT consumption: frozen K5-B (k5b_literal) with a per-cell order-3 channel (additive successor of the E6 adapter;
it does not amend the slot-1 result or its E6 output).

Composition only. The accepted E6 adapter (fbad7d33) is loaded from its pinned bytes and its OWN frozen functions are
used for loading: frozen_components (k5_minimality 3a54f0fb, k5b_check ddd54dc4), bound_file (cells.json 341eb5e9,
manifest 29ad1f9b), load_cells, read_records (manifest-bound records) and cells_for_m. Two frozen consumptions:
  C1  channel only: cell 0 keeps the adopted sealed L1; cells 1..40 get Lambda(k) from TEXT_RESULT; others None.
  C2  C1 plus curvature tightening on cells 0..40 with the T-EXT hull bound M2(x_hi(k)) >= sup_[0,x_hi(k)] |R''|:
      H'_k = [max(H.lo, -M2), min(H.hi, M2)], M'_k = min(M_R2, M2)   (valid enclosures, so K5-B applies unchanged).
C2 dominates C1 (K5-B is monotone in tighter valid enclosures); both are reported, C2 is the T-EXT result.

    python -B code/text_consume.py consume --text TEXT_RESULT.json --text-sha256 <sha> --out TEXT_CONSUMPTION.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
CP = "level4/closure_proofs/"
ADAPTER = CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py"
ADAPTER_SHA256 = "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"
SEALED = CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json"
SEALED_SHA256 = "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"
CHANNEL_CELLS = tuple(range(1, 41))
CURVATURE_CELLS = tuple(range(0, 41))
MS = ("1", "2", "3", "5")
SCHEMA = "rebaseguard.p5y.k5.remaining-cell-closure.text-consumption.v2"


class ConsumeRefusal(RuntimeError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def load_adapter(repo: Path):
    path = repo / ADAPTER
    if sha256_bytes(path.read_bytes()) != ADAPTER_SHA256:
        raise ConsumeRefusal("E6 adapter does not match its pin")
    spec = importlib.util.spec_from_file_location("e6_adapter_for_text", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def text_objects(text: dict, sealed_L1: dict) -> tuple[dict, dict]:
    """(Lambda {m: {k: F}}, M2 {m: {k: F}}) from TEXT_RESULT, re-deriving Lambda exactly; refuses anything else."""
    rows = {r["cell"]: r for r in text["rows"]}
    if sorted(rows) != [0] + list(CHANNEL_CELLS) or text.get("channel_cells") != list(CHANNEL_CELLS):
        raise ConsumeRefusal("TEXT_RESULT rows are not exactly the frozen hulls 0..40")
    if text["sealed_record_sha256"] != SEALED_SHA256 or text["sealed_L1"] != sealed_L1:
        raise ConsumeRefusal("TEXT_RESULT is not bound to the adopted slot-1 record")
    for k in range(1, 41):
        if F(rows[k]["x_lo"]) != F(rows[k - 1]["x_hi"]):
            raise ConsumeRefusal("TEXT_RESULT hulls are not contiguous")
    lam, m2 = {}, {}
    for m in MS:
        L0 = F(text["L0"][m])
        lam[m], m2[m] = {}, {}
        for k in CHANNEL_CELLS:
            X = F(rows[k]["x_hi"])
            B = sum((F(rows[j]["M"]["5"][m]) * ((X - F(rows[j]["x_lo"])) ** 2 - (X - F(rows[j]["x_hi"])) ** 2) / 2
                     for j in range(0, k + 1)), F(0))
            want = max(L0 - B, -F(rows[k]["M"]["3"][m]))
            if F(rows[k]["Lambda"][m]) != want:
                raise ConsumeRefusal(f"TEXT_RESULT Lambda mismatch cell {k} m {m}")
            lam[m][k] = want
        for k in CURVATURE_CELLS:
            v = F(rows[k]["M"]["2"][m])
            if v <= 0:
                raise ConsumeRefusal("non-positive M2")
            m2[m][k] = v
    return lam, m2


def consume(text_path: Path, text_sha256: str, records_dir: Path, repo: Path = REPO) -> dict:
    raw = Path(text_path).read_bytes()
    if sha256_bytes(raw) != text_sha256:
        raise ConsumeRefusal("TEXT_RESULT does not match the committed seal")
    text = json.loads(raw)
    sraw = (repo / SEALED).read_bytes()
    if sha256_bytes(sraw) != SEALED_SHA256:
        raise ConsumeRefusal("sealed slot-1 record hash mismatch")
    per = json.loads(sraw)["scientific"]["per_m"]
    L1 = {m: F(per[m]["L1"]) for m in MS}
    lam, m2 = text_objects(text, {m: per[m]["L1"] for m in MS})
    A = load_adapter(repo)
    comp = A.frozen_components(repo)
    KM, KB = comp["loader"], comp["theorem"]
    A.bound_file(repo / A.CELLS_JSON, A.CELLS_SHA256, "cells.json")
    manifest = json.loads(A.bound_file(repo / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(repo / A.CELLS_JSON, A.DETECTOR)
    if [c["index"] for c in cover] != list(range(0, 310)):
        raise ConsumeRefusal("cover universe mismatch")
    records, hashes = A.read_records(KM, Path(records_dir), cover, manifest)
    out = {"C1": {}, "C2": {}}
    for m in A.MS:
        for variant in ("C1", "C2"):
            cells = A.cells_for_m(KM, cover, records, m, L1[m])
            for k in CHANNEL_CELLS:
                if cells[k]["L"] is not None or cover[k]["index"] != k:
                    raise ConsumeRefusal("unexpected order-3 channel before T-EXT assignment")
                cells[k]["L"] = lam[m][k]
            if variant == "C2":
                for k in CURVATURE_CELLS:
                    b = m2[m][k]
                    lo, hi = cells[k]["H"]
                    if max(lo, -b) > min(hi, b):
                        raise ConsumeRefusal(f"empty curvature enclosure cell {k} m {m}: K1 and T-EXT disagree")
                    cells[k]["H"] = (max(lo, -b), min(hi, b))
                    cells[k]["M"] = min(cells[k]["M"], b)
            rows = KB.k5b_literal(cells)
            passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
            opened = [k for k in range(310) if k not in set(passed)]
            out[variant][m] = {
                "pass_ranges": KM.ranges(passed), "pass_count": len(passed), "open_ranges": KM.ranges(opened),
                "open_count": len(opened), "rows_sha256": sha256_bytes(canonical(A.row_json(rows))),
                "via": {str(i): rows[i]["via"] for i in range(0, 42)},
                "L_used": {str(i): (None if cells[i]["L"] is None else str(cells[i]["L"])) for i in range(0, 42)},
                "H_lo_used": {str(i): str(cells[i]["H"][0]) for i in range(0, 42)},
                "M_used": {str(i): str(cells[i]["M"]) for i in range(0, 42)}}
    return {"schema": SCHEMA, "text_result_sha256": text_sha256, "sealed_record_sha256": SEALED_SHA256,
            "adapter_sha256": ADAPTER_SHA256, "components": comp["sha256"], "channel_cells": list(CHANNEL_CELLS),
            "curvature_cells": list(CURVATURE_CELLS),
            "inputs": {"manifest_sha256": A.MANIFEST_SHA256, "cells_json_sha256": A.CELLS_SHA256,
                       "records_sha256": sha256_bytes(canonical(hashes)), "record_count": len(hashes)},
            "consumptions": out, "result": "C2", "code_sha256": sha256_bytes(HERE.read_bytes())}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("consume")
    c.add_argument("--text", required=True)
    c.add_argument("--text-sha256", required=True)
    c.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    res = consume(Path(a.text), a.text_sha256, Path(a.records))
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({v: {m: x["open_ranges"] for m, x in res["consumptions"][v].items()} for v in ("C1", "C2")}),
          "sha256", sha256_bytes(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
