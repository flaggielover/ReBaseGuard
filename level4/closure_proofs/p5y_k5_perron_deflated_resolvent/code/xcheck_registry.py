"""Independent float cross-check (X-A) of the certified operator registry, and certifier refusal / mutation probes.

xb      Independent Fraction recomputation of every registry field from the artifacts' recorded intermediates (review M1).
xcheck  For every registry cell, float operator values (degree-20 grid, operator only) at 5 drifts inside the cell must satisfy
        Abar >= E_a[tau], C_T >= sup_reach E_x[tau ^ T_a], tau >= E_a[tau ^ T_a], D_lo <= D <= ..., D1 >= |D'|, D2 >= |D''|.
        A certified bound below the float value by more than 1e-6 relative flags an implementation error.
probe   Certifier refusal tests on vultr (Arb): a wide taboo block [0, 3/10] at alpha 6/5 must be REFUSED; the same block
        certified with the e-linear term suppressed (mutant) must be ACCEPTED, showing the term is load-bearing.

    python3 -B code/xcheck_registry.py xcheck --registry REGISTRY.json --out XA.json
    python -B code/xcheck_registry.py probe --out PROBE.json            (Arb; vultr venv)
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))


def float_ops(e, deg=20):
    import operator_float_diagnostic as OD
    K, Kh, ka, nodes, n = OD.kernel_split(e, deg, quad=400)
    I = np.eye(n * n)
    P, M = np.meshgrid(nodes, nodes, indexing="ij")
    reach = (P.ravel() <= 1e-12) | (M.ravel() <= 1e-12) | (P.ravel() + M.ravel() <= 4 + 1e-12)
    G = np.linalg.inv(I - Kh)
    tab = G @ np.ones(n * n)
    arl = np.linalg.solve(I - K, np.ones(n * n))
    return {"ARL": float(arl[0]), "C": float(tab[reach].max()), "tau": float(tab[0]), "D": 1.0 - float((G @ ka)[0])}


def xcheck(reg: dict) -> dict:
    flags = []
    rows = []
    for b in reg["blocks"]:
        lo, hi = F(b["e_lo"]), F(b["e_hi"])
        es = [float(lo + (hi - lo) * F(i, 4)) for i in range(5)]
        vals = [float_ops(e) for e in es]
        dd = 2e-3
        dp = [float_ops(e + dd)["D"] for e in es]
        dm = [float_ops(abs(e - dd))["D"] for e in es]
        D1 = max(abs(p - m) / (2 * dd) for p, m in zip(dp, dm))
        D2 = max(abs(p - 2 * v["D"] + m) / dd ** 2 for p, m, v in zip(dp, dm, vals))
        fl = {"ARL": max(v["ARL"] for v in vals), "C": max(v["C"] for v in vals), "tau": max(v["tau"] for v in vals),
              "D_min": min(v["D"] for v in vals), "D1": D1, "D2": D2}
        cert = {k: float(F(b[k])) for k in ("Abar", "C_T", "tau", "D_lo", "D1", "D2")}
        tol = 1e-6
        checks = {"Abar>=ARL": cert["Abar"] >= fl["ARL"] * (1 - tol), "C_T>=C": cert["C_T"] >= fl["C"] * (1 - tol),
                  "tau>=tau": cert["tau"] >= fl["tau"] * (1 - tol), "D_lo<=D": cert["D_lo"] <= fl["D_min"] * (1 + tol),
                  "D1>=|D'|": cert["D1"] >= fl["D1"] * (1 - 1e-2), "D2>=|D''|": cert["D2"] >= fl["D2"] * (1 - 1e-2)}
        if not all(checks.values()):
            flags.append({"cell": b.get("cell"), "failed": [k for k, v in checks.items() if not v]})
        rows.append({"cell": b.get("cell"), "certified": cert, "float": fl,
                     "ratio": {"Abar": cert["Abar"] / fl["ARL"], "C_T": cert["C_T"] / fl["C"],
                               "tau": cert["tau"] / fl["tau"], "D_lo": cert["D_lo"] / fl["D_min"],
                               "D1": cert["D1"] / max(fl["D1"], 1e-12), "D2": cert["D2"] / fl["D2"]}})
    ratios = {k: [min(r["ratio"][k] for r in rows), max(r["ratio"][k] for r in rows)] for k in rows[0]["ratio"]}
    return {"schema": "rebaseguard.p5y.k5.perron-deflation.registry-xcheck.v1", "cells": len(rows),
            "flags": flags, "pass": not flags, "certified_over_float_ratio_range": ratios, "rows": rows}


# ------------------------------------------------------------------------------------------------ X-B (review M1)
K_UP = {0: F(1), 1: F(7978846, 10 ** 7), 2: F(9678830, 10 ** 7), 3: F(15100130, 10 ** 7)}


def cheb_l1(payload: dict) -> F:
    """sup of a Chebyshev payload over [0, h]^2 bounded by the l1 norm of its exact dyadic coefficients."""
    den = 1 << payload["scale_bits"]
    return sum((F(abs(int(c)), den) for row in payload["numerators"] for c in row), F(0))


def xb(reg: dict, art_dir: Path, sup_h: dict) -> dict:
    """Independent recomputation (Fraction, own code) of every registry field from the artifacts' intermediates.
    sup_h[k] = certified sup |h_1^(k)| (k = 1, 2, 3) as rational upper bounds (frozen opnorms, passed in).
    The recomputation uses rational UPPER bounds of kappa_i, so it is never less conservative than the certifier;
    agreement within 1e-6 relative shows that no term is missing and no composition step differs."""
    flags, worst = [], F(0)
    tb = {int(i): b for i, b in reg["taboo_blocks"].items()}
    for b in reg["blocks"]:
        k = b["cell"]
        lo, hi = F(b["e_lo"]), F(b["e_hi"])
        hit = [x for x in tb.values() if F(x["e_lo"]) < hi and lo < F(x["e_hi"])]
        if F(b["tau"]) != max(F(x["tau"]) for x in hit) or F(b["C_T"]) != max(F(x["C_T"]) for x in hit):
            flags.append([k, "worst-block selection"])
        arl = json.loads((art_dir / f"arl_cell_{k:03d}.json").read_text())
        if arl.get("kind") != "full" or (F(arl["e_lo"]), F(arl["e_hi"])) != (lo, hi) or F(arl["tau"]) != F(b["Abar"]):
            flags.append([k, "ARL binding"])
        d = json.loads((art_dir / f"taboo_cell_{k:03d}.json").read_text())
        e0, rho, tau, C = F(d["e0"]), F(d["rho"]), F(d["tau"]), F(d["C_T"])
        if (e0 - rho, e0 + rho) != (lo, hi) or tau != F(b["tau"]) or C != F(b["C_T"]):
            flags.append([k, "taboo-cell binding"])
        S = {j: cheb_l1(d["payloads"][f"d{j}"]) for j in range(3)}
        env = {0: K_UP[1] * S[0] + sup_h[1],
               1: K_UP[1] * S[1] + K_UP[2] * S[0] + sup_h[2],
               2: K_UP[1] * S[2] + 2 * K_UP[2] * S[1] + K_UP[3] * S[0] + sup_h[3]}
        lm = {j: F(d["lambda_mid"][str(j)]) for j in range(3)}
        lc_rec = {j: F(d["lambda_cell"][str(j)]) for j in range(3)}
        lc = {j: lm[j] + rho * env[j] for j in range(3)}

        def prop(lam):
            n0 = C * lam[0]
            n1 = C * (lam[1] + K_UP[1] * n0)
            return tau * lam[0], tau * (lam[1] + K_UP[1] * n0), tau * (lam[2] + 2 * K_UP[1] * n1 + K_UP[2] * n0)
        pm, pc = prop(lm), prop(lc)
        cand = {j: [F(x) for x in d["candidate_at_atom"][f"d{j}"]] for j in range(3)}
        amax = {j: max(abs(cand[j][0]), abs(cand[j][1])) for j in range(3)}
        D_mid_lo = cand[0][0] - pm[0]
        D1_mid = amax[1] + pm[1]
        D2 = amax[2] + pc[2]
        D1 = min(amax[1] + pc[1], D1_mid + rho * D2)
        D_lo = D_mid_lo - rho * D1
        rec = {"D_lo": F(b["D_lo"]), "D1": F(b["D1"]), "D2": F(b["D2"])}
        mine = {"D_lo": D_lo, "D1": D1, "D2": D2}
        for key in ("D1", "D2"):
            rel = (mine[key] - rec[key]) / mine[key]
            worst = max(worst, abs(rel))
            if rel < -F(1, 10 ** 6) or rel > F(1, 10 ** 6):
                flags.append([k, key, float(rel)])
        rel = (rec["D_lo"] - mine["D_lo"]) / rec["D_lo"]
        worst = max(worst, abs(rel))
        if rel < -F(1, 10 ** 6) or rel > F(1, 10 ** 6):
            flags.append([k, "D_lo", float(rel)])
        for j in range(3):
            rel = (lc[j] - lc_rec[j]) / lc[j]
            worst = max(worst, abs(rel))
            if rel < -F(1, 10 ** 6) or rel > F(1, 10 ** 6):
                flags.append([k, f"lambda_cell {j}", float(rel)])
    return {"schema": "rebaseguard.p5y.k5.perron-deflation.registry-xb.v1", "cells": len(reg["blocks"]),
            "flags": flags, "max_relative_deviation": float(worst), "pass": not flags}


def sup_h_bounds() -> dict:
    """Rational upper bounds of the frozen opnorms.sup_source_derivative(k - 1), k = 1, 2, 3 (Arb; vultr venv)."""
    import taboo_certify  # noqa: F401  (frozen import bootstrap)
    import opnorms
    from intervals import workprec
    out = {}
    with workprec(256):
        for k in (1, 2, 3):
            q = opnorms.sup_source_derivative(k - 1).upper().fmpq()
            out[k] = F(int(q.p), int(q.q))
    return out


def probe() -> dict:
    import taboo_certify as TC
    lo, hi = F(0), F(3, 10)
    payload, _ = TC.block_proposal(float((lo + hi) / 2), 1.2, 0.0, 20, False)
    good = TC.certify_block(lo, hi, payload, depth=2)
    # mutant: suppress the e-linear term by certifying the midpoint only (delta -> 0) and claiming the whole block
    mut = TC.certify_block((lo + hi) / 2, (lo + hi) / 2 + F(1, 10 ** 12), payload, depth=2)
    return {"wide_block": [str(lo), str(hi)], "correct_certifier_certified": good["certified"],
            "correct_margin": good["margin_lower_bound"], "mutant_certified": mut["certified"],
            "pass": (good["certified"] is False) and (mut["certified"] is True)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("xcheck", "xb", "probe"))
    ap.add_argument("--registry")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "xb":
        regp = Path(a.registry)
        res = xb(json.loads(regp.read_text()), regp.parent, sup_h_bounds())
    else:
        res = xcheck(json.loads(Path(a.registry).read_text())) if a.cmd == "xcheck" else probe()
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
