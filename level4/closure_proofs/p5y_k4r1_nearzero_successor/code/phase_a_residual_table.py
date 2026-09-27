"""K4R1 Phase A: read-only forensic reconstruction of the historical K4 residual (bc4ba08e).

Reads ONLY already-existing historical evidence: the accepted frozen K4 assembly report
(p5y_k4_frozen_execution_r1/evidence/K4_ASSEMBLY_REPORT.json, sha 83cabce2...) and the CUSUM Aux5 composite export
records it consumed (manifest sha 29ad1f9b...). It re-derives, in exact rational arithmetic and with the frozen
K4 formulas, why each residual (m, cell) failed. It evaluates no successor certificate.

  python phase_a_residual_table.py --report K4_ASSEMBLY_REPORT.json --cusum-records DIR --manifest MAN --out OUT
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

REPORT_SHA = "83cabce239630d98a842bd9eec32482c7d0720fc86433ef8ee7c658833aef175"
MANIFEST_SHA = "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def iv(d):
    return F(d["lo"]), F(d["hi"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--cusum-records", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if sha(a.report) != REPORT_SHA or sha(a.manifest) != MANIFEST_SHA:
        raise SystemExit("historical evidence identity mismatch")
    rep = json.loads(Path(a.report).read_text())
    man = json.loads(Path(a.manifest).read_text())["files"]
    rows, universe = [], []
    for key, v in sorted(rep["per_Dm"].items()):
        det, m = key.split("|m=")
        for cell in v.get("too_loose_cells", []):
            universe.append({"detector": det, "m": int(m), "cell": cell})
    for u in universe:
        rel = f"k4_records/aux5_CUSUM_{u['cell']}_256.json"
        path = Path(a.cusum_records) / Path(rel).name
        if sha(path) != man[rel]:
            raise SystemExit(f"{rel}: hash differs from the export manifest")
        rec = json.loads(path.read_text())
        ent = rec["m"][str(u["m"])]
        e0, rho = F(rec["e0"][0]), F(rec["rho"][0])
        R, D, R2 = iv(ent["R_interval"]), iv(ent["D_interval"]), iv(ent["R2_interval"])
        M = F(ent["M_R2"])
        magD = max(abs(D[0]), abs(D[1]))
        rem = rho * magD + rho * rho * M / 2
        rp_hi, r_hi = D[1] + rho * M, R[1] + rem
        hist = next(c for c in rep["per_Dm"][f"{u['detector']}|m={u['m']}"]["per_cell"] if c["index"] == u["cell"])
        assert hist["Rprime_cell_hi"] == str(rp_hi) and hist["R_cell_hi"] == str(r_hi) and hist["how"] == "CERTIFICATE_TOO_LOOSE"
        rows.append({
            **u, "e_interval": [str(e0 - rho), str(e0 + rho)], "e0": str(e0), "rho": str(rho),
            "record": rel, "record_sha256": man[rel],
            "R_interval_at_e0": [str(R[0]), str(R[1])], "D_interval_at_e0": [str(D[0]), str(D[1])],
            "R2_interval_over_cell": [str(R2[0]), str(R2[1])], "M_R2": str(M),
            "M_R2_equals_R2_mag": M == max(abs(R2[0]), abs(R2[1])),
            "R2_interval_contains_zero": R2[0] <= 0 <= R2[1],
            "R2_one_sided_gain_over_M": str(M - max(R2[1], -R2[0], F(0))),
            "widening_rho_M": str(rho * M), "Rprime_cell_hi": str(rp_hi),
            "taylor_remainder_rho_magD_plus_rho2M_over_2": str(rem), "R_cell_hi": str(r_hi),
            "chain_failure": "D.hi + rho*M >= 0 although D.hi < 0" if D[1] < 0 <= rp_hi else "D.hi >= 0",
            "direct_failure": "R.hi + rem >= 0" + (" (cell contains e = 0, where R(0) = 0: the direct rule can never certify it)"
                                                    if e0 - rho == 0 else ""),
            "counterexample": R[0] > 0,
            "locality": {"R_interval": "local, at the point e0", "D_interval": "local, at the point e0",
                         "R2_interval": "local, uniform over the closed cell", "M_R2": "local, |R2_interval| over the cell"},
            "float_view": {"D": [float(D[0]), float(D[1])], "rho_M": float(rho * M), "R2": [float(R2[0]), float(R2[1])]},
        })
    out = {"schema": "rebaseguard.p5y.k4r1.residual-table.v1", "source_report_sha256": REPORT_SHA,
           "source_manifest_sha256": MANIFEST_SHA, "historical_commit": "bc4ba08ef20f3996926f319766ca253e82004f74",
           "residual_universe": universe, "rows": rows,
           "residual_e_regions": {f"CUSUM|m={m}": max((r["e_interval"][1] for r in rows if r["m"] == m), key=F)
                                  for m in sorted({r["m"] for r in rows})}}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"universe": universe, "regions": out["residual_e_regions"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
