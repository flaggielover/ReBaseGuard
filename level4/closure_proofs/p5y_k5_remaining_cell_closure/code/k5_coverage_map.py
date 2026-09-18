"""K5 coverage map after T-EXT (descriptive; recomputed from sealed/frozen inputs only; no new scientific arithmetic).

For every CUSUM cover cell 0..309 and m in {1,2,3,5}: PASS/OPEN under the frozen K5-B with the adjudicated T-EXT
consumption C2 (sealed TEXT_RESULT cb97cabc), the route (slot-1 L1 / chain / direct), the evidence artifact and its
sha256, and, for OPEN cells, the Phase A blocker classification.

    python -B code/k5_coverage_map.py build --repo <clean checkout> --out K5_COVERAGE_MAP.json   (vultr-02, records present)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

NS_REL = "level4/closure_proofs/p5y_k5_remaining_cell_closure"
TEXT_REL = NS_REL + "/transport_extension/evidence/qualification_r1/TEXT_RESULT.json"
TEXT_SHA256 = "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"
CONS_REL = NS_REL + "/transport_extension/evidence/consumption_r1/TEXT_CONSUMPTION.json"
MAP_REL = NS_REL + "/phase_a/OPEN_CELL_MAP.json"
SCHEMA = "rebaseguard.p5y.k5.remaining-cell-closure.coverage-map.v1"


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(repo: Path, records: Path) -> dict:
    sys.path.insert(0, str(repo / NS_REL / "transport_extension/code"))
    import text_consume as TC
    text = json.loads((repo / TEXT_REL).read_bytes())
    if sha(repo / TEXT_REL) != TEXT_SHA256:
        raise SystemExit("TEXT_RESULT seal mismatch")
    per = json.loads((repo / TC.SEALED).read_bytes())["scientific"]["per_m"]
    lam, m2 = TC.text_objects(text, {m: per[m]["L1"] for m in TC.MS})
    A = TC.load_adapter(repo)
    comp = A.frozen_components(repo)
    KM, KB = comp["loader"], comp["theorem"]
    manifest = json.loads(A.bound_file(repo / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(repo / A.CELLS_JSON, A.DETECTOR)
    recs, hashes = A.read_records(KM, records, cover, manifest)
    phase_a = json.loads((repo / MAP_REL).read_bytes())
    cons = json.loads((repo / CONS_REL).read_bytes())
    e6 = json.loads((repo / "level4/closure_proofs/p5y_k5_cusum_first_real_probe_result/consumption/"
                            "E6_POSITIVE_CONSUMPTION_OUTPUT.json").read_bytes())
    from fractions import Fraction as F
    out = {}
    for m in TC.MS:
        cells = A.cells_for_m(KM, cover, recs, m, F(per[m]["L1"]))
        for k in TC.CHANNEL_CELLS:
            cells[k]["L"] = lam[m][k]
        for k in TC.CURVATURE_CELLS:
            lo, hi = cells[k]["H"]
            b = m2[m][k]
            cells[k]["H"] = (max(lo, -b), min(hi, b))
            cells[k]["M"] = min(cells[k]["M"], b)
        rows = KB.k5b_literal(cells)
        if KM.ranges([i for i, r in enumerate(rows) if r["pass"]]) != cons["consumptions"]["C2"][m]["pass_ranges"]:
            raise SystemExit("coverage recomputation differs from the committed C2 consumption")
        blockers = {r["cell"]: r for r in phase_a["per_m"][m]["open"]}
        baseline = set(KM.expand(e6["per_m"][m]["pass_ranges"]))     # adopted slot-1 + E6 pass set (before T-EXT)
        cm = []
        for i, r in enumerate(rows):
            rec_sha = hashes[str(i)]
            if r["pass"] and r["via"] == "L1":
                row = {"cell": i, "verdict": "PASS", "route": "K5-B cell-1 clause (L_1 > 0)",
                       "evidence": "slot-1 sealed record (ADOPTED)", "artifact_sha256": TC.SEALED_SHA256}
            elif r["pass"] and i not in baseline:
                row = {"cell": i, "verdict": "PASS", "route": f"K5-B {r['via']} with the T-EXT channel (new vs E6)",
                       "evidence": "T-EXT TEXT_RESULT (sealed, adjudicated ADOPTED) + K1 record",
                       "artifact_sha256": TEXT_SHA256, "k1_record_sha256": rec_sha}
            elif r["pass"] and r["via"] == "chain":
                row = {"cell": i, "verdict": "PASS", "route": "K5-B chain U_k < 0 (K1 records; also passes under E6)",
                       "evidence": "K1 CUSUM Aux5 records", "artifact_sha256": rec_sha}
            elif r["pass"]:
                row = {"cell": i, "verdict": "PASS", "route": "K5-B direct bound Gamma_k < 0",
                       "evidence": "K1 CUSUM Aux5 record", "artifact_sha256": rec_sha}
            else:
                b = blockers.get(i, {})
                row = {"cell": i, "verdict": "OPEN", "region": b.get("region"), "primary": b.get("primary"),
                       "flags": b.get("flags"), "zone": b.get("zone"), "k1_record_sha256": rec_sha}
            cm.append(row)
        out[m] = {"cells": cm, "pass_ranges": KM.ranges([c["cell"] for c in cm if c["verdict"] == "PASS"]),
                  "open_ranges": KM.ranges([c["cell"] for c in cm if c["verdict"] == "OPEN"]),
                  "open_count": sum(c["verdict"] == "OPEN" for c in cm)}
    union = sorted({c["cell"] for m in out for c in out[m]["cells"] if c["verdict"] == "OPEN"})
    return {"schema": SCHEMA, "detector": "CUSUM", "universe": [0, 309], "consumption": "T-EXT C2 (adjudicated)",
            "inputs": {"text_result_sha256": TEXT_SHA256, "consumption_sha256": sha(repo / CONS_REL),
                       "phase_a_map_sha256": sha(repo / MAP_REL), "manifest_sha256": A.MANIFEST_SHA256,
                       "records_sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()},
            "attribution_rule": "T-EXT is the evidence exactly for cells passing now but not under the adopted E6 "
                                "baseline; every other pass is attributed to slot-1 (cell 0) or to the K1 records",
            "per_m": out, "union_open_ranges": KM.ranges(union), "union_open_count": len(union),
            "K5_COVERAGE_COMPLETE": not union}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--repo", required=True)
    b.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    b.add_argument("--out", required=True)
    a = ap.parse_args()
    res = build(Path(a.repo), Path(a.records))
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print({m: v["open_ranges"] for m, v in res["per_m"].items()}, "complete:", res["K5_COVERAGE_COMPLETE"],
          "sha256", sha(Path(a.out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
