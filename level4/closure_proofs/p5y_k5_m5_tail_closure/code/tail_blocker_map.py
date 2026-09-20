"""Campaign B, Phase A: the m = 5 tail blocker map (cells 305-309), from the adopted K1 records only.

Runs where the adopted records live (rebaseguard-vultr-02). Every record is checked against the adopted export
manifest. For each tail cell and each m it records the frozen K5-B direct-test quantities

    g(e0) enclosure = R_interval - e0 * D_interval,   penalty = rho * x_hi * M_R2,   Gamma = hi(g(e0)) + penalty

plus the whole-cell R'' enclosure, the refined per-object eps that set M_R2, the certified C_upper, the midpoint and
whole-cell residuals of F_r, dF_r, H_r and the candidate envelopes (the inputs any tightening route would use), and the
exact margin a closure needs. It computes no model quantity.

    python -B tail_blocker_map.py --records DIR --manifest MANIFEST.json --cells-json CELLS --out MAP.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

MS = ("1", "2", "3", "5")
CELLS = list(range(300, 310))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def fl(x) -> float:
    return float(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--cells-json", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    man = json.loads(Path(a.manifest).read_bytes())
    files = man["files"]
    cover = {c["index"]: c for c in json.loads(Path(a.cells_json).read_bytes()) if c["detector"] == "CUSUM"}
    out = {"schema": "rebaseguard.p5y.k5.m5-tail.blocker-map.v1",
           "manifest_sha256": sha(Path(a.manifest).read_bytes()),
           "cells_json_sha256": sha(Path(a.cells_json).read_bytes()), "rows": [], "records": {}}
    for k in CELLS:
        name = f"aux5_CUSUM_{k}_256.json"
        raw = (Path(a.records) / name).read_bytes()
        want = files["k4_records/" + name]
        if sha(raw) != want:
            raise SystemExit(f"record {k} does not match the manifest")
        out["records"][str(k)] = want
        rec = json.loads(raw)
        g = cover[k]
        x_lo, x_hi, rho, e0 = (rat(g[t]) for t in ("left", "right", "rho", "e0"))
        o = rec["objects"]
        for m in MS:
            r = rec["m"][m]
            R = [F(r["R_interval"]["lo"]), F(r["R_interval"]["hi"])]
            D = [F(r["D_interval"]["lo"]), F(r["D_interval"]["hi"])]
            H = [F(r["R2_interval"]["lo"]), F(r["R2_interval"]["hi"])]
            M = F(r["M_R2"])
            g_lo, g_hi = R[0] - e0 * D[1], R[1] - e0 * D[0]
            pen = rho * x_hi * M
            Gamma = g_hi + pen
            need_M = (-g_hi) / (rho * x_hi) if g_hi < 0 else None
            out["rows"].append({
                "cell": k, "m": int(m), "e_lo": fl(x_lo), "e_hi": fl(x_hi), "e0": fl(e0), "rho": fl(rho),
                "g_e0_interval": [fl(g_lo), fl(g_hi)], "penalty_rho_xhi_M": fl(pen), "Gamma": fl(Gamma),
                "passes_direct": bool(Gamma < 0), "R2_cell": [fl(H[0]), fl(H[1])], "M_R2": fl(M),
                "C_upper": fl(rat(rec["C_upper"])),
                "R_halfwidth": fl((R[1] - R[0]) / 2), "D_halfwidth": fl((D[1] - D[0]) / 2),
                "eps_cell_refined_H": {f"H:{i}": fl(F(rec["eps_cell_refined"][f"H:{i}"])) for i in range(int(m))},
                "residuals": {n: {t: fl(F(o[n][t])) for t in ("delta_mid", "delta_cell", "envelope")}
                              for n in [f"{fam}_{i}" for fam in ("F", "dF", "H") for i in range(int(m))]},
                "M_needed_for_direct_pass": (fl(need_M) if need_M is not None else None),
                "M_reduction_factor_needed": (fl(M / need_M) if need_M else None),
                "target_gate_status": r.get("target_gate", {}).get("status"),
            })
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    open_rows = [r for r in out["rows"] if not r["passes_direct"]]
    print(json.dumps({"rows": len(out["rows"]), "direct_fail": [(r["cell"], r["m"]) for r in open_rows],
                      "sha256": sha(data)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
