"""PHASE 5: where the width in cells 318-324 actually comes from.

Reads the committed f8e6f758 records (no recomputation) and decomposes each
failing `(cell, m)` obligation's B_cover into its certified constituents, then
ranks the width sources so the tightening in Phase 6 is aimed rather than
guessed.

    B_cover = rho * mag(D_interval)  +  rho^2 * M_R2 / 2

and `M_R2 = mag(R2_interval)` where, by the frozen all-m assembly,

    R2_interval = (1/m) sum_(r<m) H_r  +  sum_(t,r) c_(m,t) W''_(r,t-r-1)

with `H_r` enclosed by `Hhat_r(x0) +- epsH_r^cell` and `W''` by
`What''(x0) +- epsW''^cell`. Each eps is itself
`C * (delta^cell + norm-weighted upstream eps)`, and each `delta^cell` splits as

    delta^cell = delta^mid  +  rho * Env        (the mean-value envelope)

so the question the table answers is: how much of the final curvature width is
`delta^mid` (irreducible residual), how much is `rho * Env` (the mean-value
extension), and which upstream object dominates.
"""
from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path

import ancestry                                                 # noqa: F401

import spec                                                     # noqa: E402

CELLS = {c["index"]: c for c in spec.CELLS if c["detector"] == "CUSUM"}
BLOCK = tuple(range(318, 325))
CONTROL = 325

ORDER2_RESIDUALS = ([f"h_{j}:2" for j in range(1, 5)]
                    + [f"S_{r}:2" for r in range(5)]
                    + ["Sclosed_2"]
                    + [f"H_{r}" for r in range(5)])


def _f(x) -> float:
    return float(F(x))


def records(directory: Path) -> dict:
    out = {}
    for p in sorted(Path(directory).glob("sharp_CUSUM_*_256.json")):
        r = json.loads(p.read_text())
        out[r["cell_index"]] = r
    return out


def cover_split(rec: dict, m: str) -> dict:
    """The two frozen cover terms and their children, exactly as recorded."""
    L = rec["m"][m]
    ch = L["cover"]["children"]
    rho = F(rec["rho"][0])
    first = F(ch["nominal_first_order"]) + F(ch["derivative_uncertainty"])
    curv = F(ch["curvature"])
    total = F(L["cover"]["usage"])
    return {
        "m": m, "rho": float(rho), "M_R2": _f(L["M_R2"]),
        "B_cover": _f(total),
        "utilization_pct": L["cover"]["utilization"] * 100,
        "first_order_total": float(first),
        "curvature_total": float(curv),
        "curvature_share": float(curv / total) if total else 0.0,
        "status": L["status"],
        "R2_lo": _f(L["R2_interval"]["lo"]), "R2_hi": _f(L["R2_interval"]["hi"]),
    }


def order2_width_sources(rec: dict) -> list[dict]:
    """Rank the order-2 objects by how much of their cell bound is rho*Env."""
    rho = F(rec["rho"][0])
    rows = []
    for name in ORDER2_RESIDUALS + [f"W_{r}_{j}:2" for r in range(4)
                                    for j in range(1, 4 - r)]:
        o = rec["objects"].get(name)
        if o is None:
            continue
        mid, cell, env = F(o["delta_mid"]), F(o["delta_cell"]), F(o["envelope"])
        mv = rho * env
        rows.append({
            "object": name,
            "delta_mid": float(mid),
            "envelope": float(env),
            "rho_times_envelope": float(mv),
            "delta_cell": float(cell),
            "mean_value_share": float(mv / cell) if cell else 0.0,
        })
    rows.sort(key=lambda r: -r["rho_times_envelope"])
    return rows


def eps_ranking(rec: dict) -> list[dict]:
    """The order-2 eps nodes that feed R2_interval, largest first."""
    out = []
    for node, val in rec.get("eps_cell", {}).items():
        if node.endswith(":2") or node.startswith("H:"):
            out.append({"node": node, "eps_cell": _f(val)})
    refined = rec.get("eps_cell_refined", {})
    for node, val in refined.items():
        if node.startswith("H:"):
            for row in out:
                if row["node"] == node:
                    row["eps_cell_refined"] = _f(val)
    out.sort(key=lambda r: -r.get("eps_cell_refined", r["eps_cell"]))
    return out


def report(directory: Path) -> dict:
    recs = records(directory)
    cells = {}
    for idx in BLOCK + (CONTROL,):
        rec = recs.get(idx)
        if rec is None:
            continue
        c = CELLS[idx]
        per_m = {m: cover_split(rec, m) for m in ("1", "2", "3", "5")}
        needed = {}
        for m, v in per_m.items():
            # M_R2 headroom: the largest M_R2 that would still fit .050
            cap = F(spec.TOP_BUDGETS["B_cover"])
            room = cap - F(str(v["first_order_total"]))
            rho = F(c["rho"][0])
            needed[m] = {
                "M_R2_now": v["M_R2"],
                "M_R2_max_allowed": float(2 * room / (rho * rho)),
                "tightening_factor_required":
                    v["M_R2"] / float(2 * room / (rho * rho)),
            }
        cells[idx] = {
            "rho": float(F(c["rho"][0])),
            "C_upper": float(F(c["C_upper"])),
            "e_left": float(F(c["left"][0])),
            "per_m": per_m,
            "requirement": needed,
            "order2_width_sources": order2_width_sources(rec)[:8],
            "eps_ranking": eps_ranking(rec)[:8],
        }
    worst = max((v["requirement"]["5"]["tightening_factor_required"]
                 for k, v in cells.items() if k in BLOCK), default=None)
    return {
        "schema": "k1.cusum-successor.decomposition.v1",
        "block": list(BLOCK), "control": CONTROL,
        "cells": cells,
        "worst_tightening_factor_required_m5": worst,
        "classification": "CERTIFICATE_TOO_LOOSE (inherited, adjudicated)",
        "result_bearing": False,
    }
