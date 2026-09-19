"""Phase B: quantitative route forecasts against the frozen gates (config/FEASIBILITY_GATES_A.json).

FORECAST ONLY (non-certified). Inputs: the adopted sealed deflated consumption (per-cell R, R', R'', M and the
theorem-AD constants A0, A1, A2 per cell), the adopted T-EXT result (M2..M5 per hull), the sealed slot-1 record
(L0, candidate suprema at e = 0), the adopted K1 record midpoint fields (evidence/forecast_r1/RECORD_FIELDS_0_50.json,
extracted with code/extract_record_fields.py). No model quantity is evaluated. Every route is scored by running the
frozen K5-B (k5b_literal) on the adopted inputs plus the route's forecast enclosures; the gate class follows the frozen
rules mechanically.

Routes:
  D   atom-deflated order-5 tower + evenness transport (T-EXT channel with a better M5), zero new real addresses
  G   theorem-AD midpoint R'' corollary on the adopted records + best certified M3 (T-EXT), zero new real addresses
  H   sparse positive-e R''' anchors + local M4 transport (new real addresses)
  TC  Taylor-cell deflated whole-cell R'' enclosure with order-3 midpoint candidates (new real addresses, 34 cells)

    python3 -B code/route_forecast.py --out evidence/forecast_r1/ROUTE_FORECAST.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lower_front_blocker_map as BM  # noqa: E402  (pinned loaders and the frozen K5-B)

NS = BM.NS
FIELDS = NS / "evidence/forecast_r1/RECORD_FIELDS_0_50.json"
FIELDS_SHA256 = "bd6530c17101e9564a658e14ef8f61c501902142255df9807bc3bed959082a1d"
MS = BM.MS
KMAX = {"1": 35, "2": 41, "3": 42, "5": 44}
FRONT = range(11, 45)
# whole-line Gaussian moments E|He_i(Y)| (upper bounds of the drift-aware norms ||K_i(e)||); float forecast values
KAPPA = {1: 0.7978846, 2: 0.9678830, 3: 1.5100131, 4: 2.8005834}
SCEN = {"NOMINAL": 1.0, "CONSERVATIVE": 4.0}
COST_PER_CELL_CPU_S = 3 + 550 + 170 + 170 + 50 + 10        # prepare, K1 residuals, Aux3, rung-3 candidates, G, DAG


def fl(x):
    return float(x)


def load_state():
    deflated = json.loads(BM.pinned_bytes(BM.DEFLATED))
    cover = sorted((c for c in json.loads(BM.pinned_bytes(BM.CELLS)) if c["detector"] == "CUSUM"),
                   key=lambda c: c["index"])
    text = json.loads(BM.pinned_bytes(BM.TEXT_RESULT))
    sealed_all = json.loads(BM.pinned_bytes(BM.SEALED))["scientific"]
    sealed = sealed_all["per_m"]
    TC = BM.load_module(BM.TEXT_CONSUME, "text_consume_fc")
    KB = BM.load_module(BM.K5B, "k5b_check_fc")
    lam, _ = TC.text_objects(text, {m: sealed[m]["L1"] for m in MS})
    raw = FIELDS.read_bytes()
    if BM.sha(raw) != FIELDS_SHA256:
        raise SystemExit("record fields do not match their pin")
    fields = json.loads(raw)["cells"]
    return deflated, cover, text, sealed_all, lam, KB, fields


def base_cells(deflated, cover, sealed, lam, m):
    cons = deflated["consumptions"][m]
    cells = []
    for k in range(BM.N_REPLAY):
        c, g = cons["cells"][str(k)], cover[k]
        L = F(sealed[m]["L1"]) if k == 0 else (lam[m][k] if k in lam[m] else None)
        cells.append({"x_lo": BM.rat(g["left"]), "x_hi": BM.rat(g["right"]), "rho": BM.rat(g["rho"]),
                      "e0": BM.rat(g["e0"]), "R": tuple(F(v) for v in c["R"]), "D": tuple(F(v) for v in c["D"]),
                      "H": tuple(F(v) for v in c["H"]), "M": F(c["M"]), "L": L})
    return cells


def closed_pairs(KB, cells, m):
    rows = KB.k5b_literal(cells)
    return [k for k in range(11, KMAX[m] + 1) if rows[k]["pass"]], rows


def with_H(cells, newH: dict):
    out = [dict(c) for c in cells]
    for k, (lo, hi) in newH.items():
        a, b = max(out[k]["H"][0], lo), min(out[k]["H"][1], hi)
        if a > b:
            raise SystemExit(f"empty forecast intersection at cell {k}")
        out[k]["H"] = (a, b)
        out[k]["M"] = min(out[k]["M"], max(abs(a), abs(b)))
    return out


def with_L(cells, newL: dict):
    out = [dict(c) for c in cells]
    for k, L in newL.items():
        out[k]["L"] = L if out[k]["L"] is None else max(out[k]["L"], L)
    return out


# ------------------------------------------------------------------ route D
def route_D(state):
    deflated, cover, text, sealed_all, lam, KB, fields = state
    sealed = sealed_all["per_m"]
    rows = {r["cell"]: r for r in text["rows"]}
    res = {}
    for m in MS:
        cells = base_cells(deflated, cover, sealed, lam, m)
        L0 = F(sealed[m]["L0"])

        def closes(M5):
            newL = {k: L0 - M5 * cells[k]["x_hi"] ** 2 / 2 for k in range(1, 45)}
            return closed_pairs(KB, with_L(cells, newL), m)[0]
        lo, hi = F(10) ** 3, F(10) ** 10                     # bisection for the largest uniform M5 closing all
        if len(closes(lo)) != KMAX[m] - 10:
            raise SystemExit("route D: even M5 = 1e3 does not close the front (unexpected)")
        for _ in range(60):
            mid = (lo + hi) / 2
            if len(closes(mid)) == KMAX[m] - 10:
                lo = mid
            else:
                hi = mid
        m5_hull0 = F(rows[0]["M"]["5"][m])
        scen = {}
        for s, f in SCEN.items():
            M5 = m5_hull0 * F(f)          # NOMINAL: a deflated tower with NO hull growth at the hull-0 floor
            scen[s] = {"M5_assumed": fl(M5), "closed": len(closes(M5))}
        res[m] = {"M5_required_uniform_float": fl(lo), "M5_TEXT_hull0": fl(m5_hull0),
                  "M5_TEXT_hull10": fl(F(rows[10]["M"]["5"][m])), "M5_TEXT_hull40": fl(F(rows[40]["M"]["5"][m])),
                  "improvement_needed_vs_hull0": fl(m5_hull0 / lo),
                  "improvement_needed_vs_certified_hull_at_Km": fl(F(rows[min(KMAX[m], 40)]["M"]["5"][m]) / lo),
                  "scenarios": scen}
    return res


# ------------------------------------------------------------------ theorem-AD midpoint R'' error from records
def mid_err(fields, A, k, r):
    f = fields[str(k)]["r"][str(r)]
    fF = F(f["dF"]) + F(f["s0"])
    fD = F(f["dD"]) + F(f["s1"])
    fH = F(f["dH"]) + F(f["s2"])
    return A["A0"] * fH + 2 * A["A1"] * fD + A["A2"] * fF, (fF, fD, fH, F(f["s3"]))


def consts(deflated, k):
    a = deflated["consumptions"]["5"]["audit"][str(k)]
    return {j: F(a[j]) for j in ("A0", "A1", "A2")}


# ------------------------------------------------------------------ route G
def route_G(state):
    deflated, cover, text, sealed_all, lam, KB, fields = state
    sealed = sealed_all["per_m"]
    rows = {r["cell"]: r for r in text["rows"]}
    res = {}
    for m in MS:
        cells = base_cells(deflated, cover, sealed, lam, m)
        mi = int(m)
        scen = {}
        for s, f in SCEN.items():
            newH, detail = {}, {}
            for k in FRONT:
                if k > 40:                               # no certified M3 exists beyond hull 40
                    continue
                A = consts(deflated, k)
                err = sum((F(1, mi) * mid_err(fields, A, k, r)[0] for r in range(mi)), F(0)) + F(1, 100)
                c = (cells[k]["H"][0] + cells[k]["H"][1]) / 2
                M3 = F(rows[k]["M"]["3"][m])
                lo = c - err - cells[k]["rho"] * M3
                newH[k] = (lo, cells[k]["H"][1])
                detail[k] = {"centre": fl(c), "mid_err": fl(err), "rho_M3": fl(cells[k]["rho"] * M3), "lo": fl(lo)}
            closed = closed_pairs(KB, with_H(cells, newH), m)[0]
            scen[s] = {"closed": len(closed), "cells": {str(k): v for k, v in detail.items() if k in (11, 20, 30, 40)}}
        res[m] = scen
    return res


# ------------------------------------------------------------------ route H
def route_H(state):
    deflated, cover, text, sealed_all, lam, KB, fields = state
    rows = {r["cell"]: r for r in text["rows"]}
    sealed = sealed_all["per_m"]
    res = {}
    for m in MS:
        L0 = F(sealed[m]["L0"])
        out = {}
        for k in (11, 20, 30, 40):
            M4 = F(rows[k]["M"]["4"][m])
            radius = L0 / M4
            out[str(k)] = {"M4_TEXT_hull": fl(M4), "anchor_radius_optimistic": fl(radius),
                           "cell_half_width": fl(BM.rat(cover[k]["rho"]))}
        rho11 = BM.rat(cover[11]["rho"])
        out["anchors_needed_per_cell_at_11"] = fl(rho11 / (L0 / F(rows[11]["M"]["4"][m])))
        res[m] = {"detail": out, "scenarios": {"NOMINAL": {"closed": 0}, "CONSERVATIVE": {"closed": 0}},
                  "reason": "an anchor with the best certified local M4 transports R''' over a radius far below one "
                            "cell half-width (M4 is the T-EXT hull value; no sharper certified M4 exists at e != 0); "
                            "a sparse anchor set closes no pair; the dense limit (one order-3 object per cell) is "
                            "route TC"}
    return res


# ------------------------------------------------------------------ route TC
def route_TC(state):
    deflated, cover, text, sealed_all, lam, KB, fields = state
    sealed = sealed_all["per_m"]
    sups = sealed_all["intermediates"]["candidate_graded_sups"]
    s_at0 = {r: {fam: max(F(x) for x in sups[f"F:{r}:{n}"]) for fam, n in (("F", 0), ("D", 1), ("H", 2), ("G", 3))}
             for r in range(5)}
    kap = {i: F(str(v)) for i, v in KAPPA.items()}
    res = {"estimates_NOMINAL": {"candidate_sups": "slot-1 candidate_graded_sups at e = 0 (max of parity parts)",
                                 "abs_G_at_a": "<= sup of the G candidate", "delta_G_plus_src3": "0.02",
                                 "sup_S4": "10", "W_cell_radius": "0.01", "k_i": "whole-line E|He_i|"},
           "per_m": {}}
    for m in MS:
        cells = base_cells(deflated, cover, sealed, lam, m)
        mi = int(m)
        scen = {}
        for s, f in SCEN.items():
            f = F(f)
            newH, detail = {}, {}
            for k in FRONT:
                A = consts(deflated, k)
                rho = cells[k]["rho"]
                half = F(0)
                for r in range(mi):
                    _, (fF, fD, fH, s3) = mid_err(fields, A, k, r)
                    fG = F(2, 100) * f + s3
                    sF, sD, sH, sG = (s_at0[r][x] * f for x in ("F", "D", "H", "G"))
                    env4 = (F(10) * f + 4 * kap[1] * sG + 6 * kap[2] * (sH + rho * sG)
                            + 4 * kap[3] * (sD + rho * sH + rho ** 2 / 2 * sG)
                            + kap[4] * (sF + rho * sD + rho ** 2 / 2 * sH + rho ** 3 / 6 * sG))
                    p0 = fF + rho * fD + rho ** 2 / 2 * fH + rho ** 3 / 6 * fG + rho ** 4 / 24 * env4
                    p1 = fD + rho * fH + rho ** 2 / 2 * fG + rho ** 3 / 6 * env4
                    p2 = fH + rho * fG + rho ** 2 / 2 * env4
                    rad = A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0
                    half += F(1, mi) * (rho * sG + rad)
                half += F(1, 100) * f
                c = (cells[k]["H"][0] + cells[k]["H"][1]) / 2
                newH[k] = (c - half, c + half)
                detail[k] = {"centre": fl(c), "half_width": fl(half), "lo": fl(c - half)}
            closed = closed_pairs(KB, with_H(cells, newH), m)[0]
            mins = min(detail.values(), key=lambda d: d["lo"] / d["half_width"])
            scen[s] = {"closed": len(closed), "open_after": [k for k in range(11, KMAX[m] + 1) if k not in closed],
                       "min_lo": min(d["lo"] for d in detail.values()),
                       "min_lo_over_half": min(d["lo"] / d["half_width"] for d in detail.values()),
                       "cells": {str(k): v for k, v in detail.items() if k in (11, 12, 20, 30, 44)}}
        res["per_m"][m] = scen
    res["cost"] = {"cells": len(FRONT), "cpu_s_per_cell": COST_PER_CELL_CPU_S,
                   "cpu_hours": COST_PER_CELL_CPU_S * len(FRONT) / 3600,
                   "with_two_cell_reproduction": COST_PER_CELL_CPU_S * (len(FRONT) + 2) / 3600,
                   "basis": "adopted K1 record timings at cell 11: 63 residual certificates 550 CPU-s, Aux3 order-3 "
                            "sources 170 CPU-s, prepare 3 CPU-s; rung-3 candidates about 170 CPU-s (order-3 producer "
                            "DESIGN_REAL.md); 5 G residual certificates about 10 CPU-s each; whole-cell refine2 "
                            "(about 1330 CPU-s) is NOT run"}
    return res


def classify(scen):
    total = 122
    cons = scen["CONSERVATIVE"]["closed"]
    nom = scen["NOMINAL"]["closed"]
    if cons == total:
        return "STRONG"
    if cons >= 61 or nom == total:
        return "USEFUL"
    if nom >= 1:
        return "MARGINAL"
    return "INFEASIBLE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    st = load_state()
    D, G, H, TC = route_D(st), route_G(st), route_H(st), route_TC(st)

    def tot(per_m, getter):
        return {s: {"closed": sum(getter(per_m[m])[s]["closed"] for m in MS)} for s in SCEN}
    totals = {"D": tot(D, lambda x: x["scenarios"]), "G": tot(G, lambda x: x),
              "H": tot(H, lambda x: x["scenarios"]), "TC": tot(TC["per_m"], lambda x: x)}
    classes = {r: classify(t) for r, t in totals.items()}
    out = {"schema": "rebaseguard.p5y.k5.lower-front-order3.route-forecast.v1", "label": "FORECAST (non-certified)",
           "gates": "config/FEASIBILITY_GATES_A.json", "routes": {"D": D, "G": G, "H": H, "TC": TC},
           "totals": totals, "classes": classes}
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"totals": totals, "classes": classes}), "sha256", BM.sha(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
