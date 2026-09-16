"""R3 Part H: cell-0 first-cell forecast from COMMITTED K1 magnitudes + CERTIFIED operator constants. No R''' value.

Inputs
    committed Aux5 cell-0 record (hash-bound copy): residual magnitudes (objects, auxiliary_evidence), candidate suprema
    (D_at_e0 - eps_mid, H_at_e0 - eps_mid, F envelope / k_1, order-3 candidate_suprema), C_upper, geometry
    certified: C_o0, C_e0 (config/OPERATOR_CERTIFICATES_R3.json), norms k_0..6, j_0..6 (frozen + He_6 extension),
    sup |S_0^(n)| n <= 6 (frozen + extension + reviewed)
Conventions (conservative): a scalar committed magnitude is assigned to BOTH parity components; the G_r residual
(never committed) is swept x{1, 10, 100} of the largest committed H_r residual (R2 convention).

    STRATEGY A   graded whole-cell radius on cell 0 (graded_dag, eta = x_1)
    STRATEGY B   point radius at e = 0 (eta = 0) + (x_1^2/2) M5
                 point radius, assumption A1 (binding): a point run at e = 0 has residual magnitudes equal to the
                   committed e0 magnitudes;  conservative proxy: residual(0) <= residual(e0) + e0 * envelope
                 M5 from r5_majorant.true_tower on [0, x_1] with the certified constants, anchored at orders 0..3
                   where a committed candidate supremum exists (+ the Strategy-A graded whole-cell error)
CLASSIFICATION (predeclared, config/FEASIBILITY_CRITERION_R3.json): reference scale S* = max_r sup|Hhat_r| (committed)
    PROMISING radius <= S*;  MARGINAL S* < radius <= 100 S*;  UNINFORMATIVE radius > 100 S*;
    STRUCTURALLY_BLOCKED if the strategy has no finite certified bound (e.g. a missing certified object).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r2_repair/code"),
           str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cell0_forecast as R2F  # noqa: E402  (R2, frozen: committed-magnitude input construction)
import hermite6_ext as H6  # noqa: E402
import graded_dag as G  # noqa: E402
import r5_majorant as R5  # noqa: E402
import rung3_engine as R1E  # noqa: E402

RECORD = CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json"
FAM_N = {"F": 0, "D": 1, "H": 2}


def certified_constants() -> dict:
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R3.json").read_text())
    return {e["name"]: F(e["value_upper"]) for e in reg["certificates"]}


def _inputs(rec, consts, *, g, eta_mode, C_o0=None, C_e0=None, res_scale=F(1), leak=True):
    ex = R1E.exact
    inp = R2F.inputs(rec, C_o0=ex(consts["C_o0"] if C_o0 is None else C_o0), g_res_factor=g, eta_mode=eta_mode)
    inp["C_e0"] = ex(consts["C_e0"] if C_e0 is None else C_e0)
    cell = R2F.rec_cell(rec)
    t = H6.norm_table(F(cell["left"]), F(cell["right"]))
    inp["k"], inp["j"], inp["k_hull"], inp["j_hull"] = t["k"], t["j"], t["k"], t["j"]
    if res_scale != 1:
        s = ex(res_scale)
        inp["res"] = {n: {w: tuple(s * x for x in v[w]) for w in ("mid", "cell")} for n, v in inp["res"].items()}
    if not leak:
        inp["eta_mid"], inp["eta_cell"] = ex(0), ex(0)
    return inp


def _rad(d, m=1):
    return float(R1E.fraction_of(d[m]))


def m5_forecast(rec, consts, outA, *, anchored=True, C_e0=None, C_o0=None) -> dict:
    ex = R1E.exact
    cell = R2F.rec_cell(rec)
    left, x1 = F(cell["left"]), F(cell["right"])
    t = H6.norm_table(left, x1)
    anchors = {}
    if anchored:
        cellN = outA["cell"]["nodes"]
        k1 = R1E.fraction_of(t["k"][1].abs_upper())
        for r in range(5):
            so = rec["whole_cell_refinement"][str(r)]["second_order"]
            sups = {"F": F(rec["objects"][f"F_{r}"]["envelope"]) / k1,
                    "D": F(so["D_at_e0"]) - F(rec["eps_mid"][f"D:{r}"]),
                    "H": F(so["H_at_e0"]) - F(rec["eps_mid"][f"H:{r}"])}
            for fam, n in FAM_N.items():
                v = cellN[f"F:{r}:{n}"]
                s = ex(sups[fam])
                anchors[f"F:{r}:{n}"] = G.V(s + v.e, s + v.o, s + v.t)
        cs = rec["auxiliary_evidence"]["candidate_suprema"]
        for key, val in cs.items():
            if key.startswith("h:") and not key.startswith("hclosed"):
                node = key
            elif key.startswith("S:"):
                node = key
            elif key.startswith("W:("):
                r, jj = key[3:key.index(")")].split(", ")
                node = f"W:{r}:{jj}:3"
            else:
                continue
            if node in cellN:
                v = cellN[node]
                s = ex(F(val))
                anchors[node] = G.V(s + v.e, s + v.o, s + v.t)
    tin = {"C": ex(F(rec["C_upper"])), "C_e0": ex(consts["C_e0"] if C_e0 is None else C_e0),
           "C_o0": ex(consts["C_o0"] if C_o0 is None else C_o0), "k": t["k"], "j": t["j"], "eta": ex(x1),
           "S0": {n: H6.sup_S0_on(n, left, x1) for n in range(7)}, "anchors": anchors}
    tw = R5.true_tower(tin, parity=True)
    M5 = R5.m5(tw["towers"], parity=True)
    pen = {m: float(x1 * x1 / 2 * R1E.fraction_of(v)) for m, v in M5.items()}
    return {"M5": {m: float(R1E.fraction_of(v)) for m, v in M5.items()}, "penalty": pen,
            "x1_squared_over_2": str(x1 * x1 / 2), "anchor_count": len(anchors), "tower_mode": tw["resolvent_mode"]}


def classify(radius: float, s_star: float, finite: bool = True) -> str:
    if not finite:
        return "STRUCTURALLY_BLOCKED"
    if radius <= s_star:
        return "PROMISING"
    if radius <= 100 * s_star:
        return "MARGINAL"
    return "UNINFORMATIVE"


def compute() -> dict:
    rec = json.loads(RECORD.read_text())
    consts = certified_constants()
    s_star = max(float(F(rec["whole_cell_refinement"][str(r)]["second_order"]["H_at_e0"]) - F(rec["eps_mid"][f"H:{r}"]))
                 for r in range(5))
    out = {"schema": "rebaseguard.p5y.k5.order3-r3.cell0-forecast.v1", "no_R3_value_computed": True,
           "certified_constants": {k: str(v) for k, v in consts.items()}, "S_star": s_star, "sweep": {}}
    with R1E.precision(256):
        for g in (1, 10, 100):
            A = G.certify_graded(_inputs(rec, consts, g=g, eta_mode="mid"), parity=True)
            P1 = G.certify_graded(dict(_inputs(rec, consts, g=g, eta_mode="mid"), eta_mid=R1E.exact(0)), parity=True)
            Pp = G.certify_graded(_inputs(rec, consts, g=g, eta_mode="point0"), parity=True)
            S = G.certify_graded(_inputs(rec, consts, g=g, eta_mode="mid"), parity=False)
            m5a = m5_forecast(rec, consts, A, anchored=True)
            row = {}
            for m in G.M_VALUES:
                ra, rp, rpp = _rad(A["rad_cell"], m), _rad(P1["rad_mid"], m), _rad(Pp["rad_mid"], m)
                rb = rp + m5a["penalty"][m]
                row[str(m)] = {"R1_scalar_cell_radius": _rad(S["rad_cell"], m),
                               "strategy_A_radius": ra, "strategy_A_class": classify(ra, s_star),
                               "strategy_B_point_radius_A1": rp, "strategy_B_point_radius_proxy": rpp,
                               "strategy_B_penalty": m5a["penalty"][m], "M5": m5a["M5"][m],
                               "strategy_B_radius": rb, "strategy_B_class": classify(rb, s_star),
                               "strategy_B_radius_proxy": rpp + m5a["penalty"][m],
                               "strategy_B_class_proxy": classify(rpp + m5a["penalty"][m], s_star),
                               "midpoint_radius_e0": _rad(A["rad_mid"], m)}
            out["sweep"][str(g)] = {"m": row, "x1_squared_over_2": m5a["x1_squared_over_2"],
                                    "anchors": m5a["anchor_count"], "tower_mode": m5a["tower_mode"],
                                    "resolvent_mode": [A["mid"]["resolvent"]["mode"], A["cell"]["resolvent"]["mode"]]}
        # diagnostic attribution at g = 1, m = 1 (not certified where noted)
        base = _rad(G.certify_graded(_inputs(rec, consts, g=1, eta_mode="mid"), parity=True)["rad_cell"])
        diag = {"baseline_certified_A_cell": base}
        variants = {
            "C_o0_float_estimate_4.68_(non-certified)": dict(C_o0=F(468, 100)),
            "C_e0_replaced_by_C_upper": dict(C_e0=F(rec["C_upper"])),
            "no_parity_leakage_(invalid_diagnostic)": dict(leak=False),
            "base_residuals_x0.1_(hypothetical)": dict(res_scale=F(1, 10)),
        }
        for name, kw in variants.items():
            diag[name] = _rad(G.certify_graded(_inputs(rec, consts, g=1, eta_mode="mid", **kw), parity=True)["rad_cell"])
        diag["cell_drift_midpoint_vs_cell"] = {"mid": _rad(G.certify_graded(_inputs(rec, consts, g=1, eta_mode="mid"),
                                                                         parity=True)["rad_mid"]), "cell": base}
        A1 = G.certify_graded(_inputs(rec, consts, g=1, eta_mode="mid"), parity=True)
        diag["M5_unanchored_tower"] = m5_forecast(rec, consts, A1, anchored=False)["M5"][1]
        diag["M5_anchored_tower"] = m5_forecast(rec, consts, A1, anchored=True)["M5"][1]
        diag["M5_with_float_C_o0_(non-certified)"] = m5_forecast(rec, consts, A1, anchored=True, C_o0=F(468, 100))["M5"][1]
        # best case with the NON-CERTIFIED operator estimate (next-step rule input only; never a certified number)
        Af = G.certify_graded(_inputs(rec, consts, g=1, eta_mode="mid", C_o0=F(468, 100)), parity=True)
        Pf = G.certify_graded(dict(_inputs(rec, consts, g=1, eta_mode="mid", C_o0=F(468, 100)), eta_mid=R1E.exact(0)),
                              parity=True)
        m5f = m5_forecast(rec, consts, Af, anchored=True, C_o0=F(468, 100))
        rbf = _rad(Pf["rad_mid"]) + m5f["penalty"][1]
        diag["best_case_non_certified_C_o0"] = {"strategy_A_radius": _rad(Af["rad_cell"]),
                                                "strategy_A_class": classify(_rad(Af["rad_cell"]), s_star),
                                                "strategy_B_point_radius": _rad(Pf["rad_mid"]),
                                                "strategy_B_penalty": m5f["penalty"][1], "strategy_B_radius": rbf,
                                                "strategy_B_class": classify(rbf, s_star)}
        out["diagnostics_g1_m1"] = diag
    return out


if __name__ == "__main__":
    print(json.dumps(compute(), indent=1))
