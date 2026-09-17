"""R4 feasibility forecast for CUSUM cell 0 from COMMITTED magnitudes + CERTIFIED constants. No R''' or R^(5) value.

Inputs (all pre-existing): committed Aux5 cell-0 record magnitudes (R3 input construction, unchanged: a scalar committed
magnitude is assigned to both parity components; G factor sweep x{1, 10, 100}); certified C_o0 (R4) and C_e0 (R3) from
constants_r4.load_certificates(); frozen + He_6 norms on the hull [0, x1] (cell 0 has left endpoint 0).

BINDING (G factor 1, m = 1):
  POINT_RADIUS_FORECAST   graded point radius at e = 0 under assumption A1 (R3): point-run residual magnitudes equal the
                          committed e0 magnitudes
  CERTIFIED_M5_R4         local_r5.local_tower anchored by the committed candidate suprema (both components) + the graded
                          point errors of that point run; no whole-cell run
  TRANSPORT_PENALTY_R4    (x1^2 / 2) M5;  STRATEGY_B_TOTAL_RADIUS_R4 = point + penalty
CLASSES (config/FEASIBILITY_CRITERION_R4.json, frozen): overall class on the frozen R3 scale S*; C_o0 and transport
engineering labels; sensitivity grid (hypothetical rows marked); dominant-blocker rule.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r3_infrastructure/code"),
           str(CP / "p5y_k5_cusum_order3_r2_repair/code"), str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cell0_forecast_r3 as FR  # noqa: E402  (R3, frozen input construction)
import constants_r4 as K4  # noqa: E402
import graded_dag as G  # noqa: E402
import hermite6_ext as H6  # noqa: E402
import local_r5 as LR  # noqa: E402
import rung3_engine as R1E  # noqa: E402

CRITERION = json.loads((NS / "config/FEASIBILITY_CRITERION_R4.json").read_text())


def s_star(rec) -> float:
    return max(float(F(rec["whole_cell_refinement"][str(r)]["second_order"]["H_at_e0"]) - F(rec["eps_mid"][f"H:{r}"]))
               for r in range(5))


def candidate_sups(rec, k1: F) -> dict:
    s = {}
    for r in range(5):
        so = rec["whole_cell_refinement"][str(r)]["second_order"]
        s[f"F:{r}:0"] = F(rec["objects"][f"F_{r}"]["envelope"]) / k1
        s[f"F:{r}:1"] = F(so["D_at_e0"]) - F(rec["eps_mid"][f"D:{r}"])
        s[f"F:{r}:2"] = F(so["H_at_e0"]) - F(rec["eps_mid"][f"H:{r}"])
    for key, val in rec["auxiliary_evidence"]["candidate_suprema"].items():
        if key.startswith("hclosed") or key.startswith("Sclosed"):
            continue
        if key.startswith("h:") or key.startswith("S:"):
            s[key] = F(val)
        elif key.startswith("W:("):
            r, jj = key[3:key.index(")")].split(", ")
            s[f"W:{r}:{jj}:3"] = F(val)
    return s


def strategy_b(rec, consts: dict, *, C_o0: F, g: int = 1) -> dict:
    ex = R1E.exact
    cell = FR.R2F.rec_cell(rec)
    left, x1 = F(cell["left"]), F(cell["right"])
    if left != 0:
        raise K4.R4Refusal("local first-cell forecast needs a cell with left endpoint 0")
    inp = dict(FR._inputs(rec, consts, g=g, eta_mode="mid", C_o0=C_o0), eta_mid=ex(0))
    P = G.certify_graded(inp, parity=True)
    t = H6.norm_table(left, x1)
    k1 = R1E.fraction_of(t["k"][1].abs_upper())
    cands = {n: (ex(s), ex(s)) for n, s in candidate_sups(rec, k1).items() if n in P["mid"]["nodes"]}
    base = {"C": ex(F(rec["C_upper"])), "C_e0": ex(consts["C_e0"]), "C_o0": ex(C_o0), "k": t["k"], "j": t["j"],
            "eta": ex(x1), "S0": {n: H6.sup_S0_on(n, left, x1) for n in range(7)}}
    loc = LR.local_tower(base, cands, P["mid"]["nodes"], x1=ex(x1))
    out = {}
    for m in G.M_VALUES:
        pt = R1E.fraction_of(P["rad_mid"][m])
        M5 = R1E.fraction_of(loc["M5"][m].abs_upper())
        pen = x1 * x1 / 2 * M5
        out[m] = {"point_radius": pt, "M5": M5, "penalty": pen, "total": pt + pen}
    return {"m": out, "anchors": len(cands), "trace_m1": [float(v) for v in loc["trace_m1"]], "x1": x1,
            "strategy_A_cell_radius": R1E.fraction_of(
                G.certify_graded(FR._inputs(rec, consts, g=g, eta_mode="mid", C_o0=C_o0), parity=True)["rad_cell"][1])}


def overall_class(radius: float, S: float) -> str:
    if radius <= S:
        return "PROMISING"
    if radius <= 100 * S:
        return "MARGINAL"
    return "UNINFORMATIVE"


def labelled(value: float, table: list) -> str:
    for label, lo, hi in table:
        if (lo is None or value >= lo) and (hi is None or value < hi):
            return label
    raise ValueError(value)


def dominant(point: float, penalty: float, total: float, S: float) -> str:
    rule = CRITERION["dominant_blocker_rule"]
    if total <= S:
        return "NEITHER_INFRASTRUCTURE_READY"
    if penalty >= rule["ratio"] * point:
        return "R5_DOMINANT"
    if point >= rule["ratio"] * penalty:
        return "C_O0_DOMINANT"
    return "BOTH_COMPARABLE"


def compute(consts: dict | None = None) -> dict:
    rec = json.loads(FR.RECORD.read_text())
    consts = K4.load_certificates() if consts is None else consts
    S = s_star(rec)
    if abs(S - CRITERION["S_star"]) > 1e-9:
        raise K4.R4Refusal("S* differs from the frozen value")
    crit = CRITERION
    out = {"schema": "rebaseguard.p5y.k5.order3-r4.cell0-forecast.v1", "no_R3_or_R5_value_computed": True,
           "certified_constants": {k: str(v) for k, v in consts.items()}, "S_star": S}
    with R1E.precision(256):
        sweep = {}
        for g in (1, 10, 100):
            b = strategy_b(rec, consts, C_o0=consts["C_o0"], g=g)
            sweep[str(g)] = {str(m): {k: float(v) for k, v in row.items()} for m, row in b["m"].items()}
            if g == 1:
                binding = b
        row = binding["m"][1]
        x1 = binding["x1"]
        pt, M5, pen, tot = (float(row[k]) for k in ("point_radius", "M5", "penalty", "total"))
        c_o0 = float(consts["C_o0"])
        out["binding_g1_m1"] = {
            "CERTIFIED_C_o0_R4": str(consts["C_o0"]), "CERTIFIED_C_e0": str(consts["C_e0"]),
            "CERTIFIED_M5_R4": str(row["M5"]), "POINT_RADIUS_FORECAST": pt, "TRANSPORT_PENALTY_R4": pen,
            "STRATEGY_B_TOTAL_RADIUS_R4": tot, "X1_SQUARED_OVER_2": str(x1 * x1 / 2),
            "C_o0_improvement_factor": float(F(crit["C_o0_R3"]) / consts["C_o0"]),
            "M5_improvement_factor": float(F(crit["M5_R3"]) / row["M5"]),
            "C_o0_class": labelled(c_o0, [(c["label"], c["min"], c["max"]) for c in crit["C_o0_classes"]]),
            "transport_class": labelled(pen, [(c["label"], c["min"], c["max"]) for c in crit["transport_classes"]]),
            "strategy_B_class": overall_class(tot, S), "dominant_blocker": dominant(pt, pen, tot, S),
            "strategy_A_cell_radius_with_R4_C_o0": float(binding["strategy_A_cell_radius"]),
            "M5_iteration_trace": binding["trace_m1"], "local_anchors": binding["anchors"]}
        out["g_sweep"] = sweep
        grid = {}
        for label, co in (("certified_R4", consts["C_o0"]),) + tuple((str(v), F(v)) for v in crit["grid"]["C_o0_hypothetical"]):
            b = binding if label == "certified_R4" else strategy_b(rec, consts, C_o0=co)
            r1 = b["m"][1]
            cols = {"model_M5_at_this_C_o0": float(r1["M5"])}
            cols.update({f"M5={v:g}": float(v) for v in crit["grid"]["M5_hypothetical"]})
            grid[label] = {"hypothetical": label != "certified_R4", "C_o0": float(co),
                           "point_radius": float(r1["point_radius"]),
                           "rows": {name: {"M5": m5, "hypothetical": label != "certified_R4" or name != "model_M5_at_this_C_o0",
                                           "total_radius": float(r1["point_radius"]) + float(x1 * x1 / 2) * m5,
                                           "class": overall_class(float(r1["point_radius"]) + float(x1 * x1 / 2) * m5, S)}
                                    for name, m5 in cols.items()}}
        out["sensitivity_grid_g1_m1"] = grid
        best = min(r["total_radius"] for gl in grid.values() for r in gl["rows"].values())
        out["best_grid_total_radius"] = best
        out["best_grid_class"] = overall_class(best, S)
    return json.loads(json.dumps(out, default=str))


if __name__ == "__main__":
    print(json.dumps(compute(), indent=1))
