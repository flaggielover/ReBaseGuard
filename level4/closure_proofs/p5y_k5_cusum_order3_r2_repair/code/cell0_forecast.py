"""Cell-0 (and cell-309 contrast) R''' RADIUS forecast from COMMITTED K1 magnitudes. No R''' value, no centre, no sign.

Inputs, all pre-existing:
    committed, hash-bound Aux5 records (premise-binding copies of cells 0 and 309):
        objects[*].delta_mid / delta_cell      order 0..2 certified residual magnitudes
        auxiliary_evidence.objects[*]          order-3 source-chain residual magnitudes and envelopes
        auxiliary_evidence.midpoint_eps["Sclosed:3"]
        m[*] / eps_mid / whole_cell_refinement  (only for the reconstruction check and candidate sups)
    geometry-only certified functions: sharp_norms.table(left, right) (k_i, j_i), order2.sup_source_derivative_on
    the NON-CERTIFIED e = 0 operator estimate (C_o0 ~ 4.68), used only as one point of a predeclared sweep

Not committed, therefore swept (predeclared): the G_r residual (never computed in R1) as a multiple of the largest
committed order-2 resolvent residual, and the candidate sup of G_r as a multiple of sup|Hhat_r|.

Conservative convention: a scalar committed residual or envelope is assigned to BOTH parity components (valid, since
||P_x v|| <= ||v||). Modes:
    R1_SCALAR      graded_dag with parity=False on the same inputs (reproduces the frozen scalar cascade)
    R2_MID         graded, eta = e0                         (midpoint R'''(e0) radius)
    R2_POINT0      graded, eta = 0, residual(0) <= residual(e0) + e0 * envelope   (point R'''(0) radius)
    R2_CELL        graded, eta = x_1, cell residuals = committed delta_cell (scalar envelope, both components)
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for p in (str(NS / "code"), str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if p not in sys.path:
        sys.path.insert(0, p)

import ancestry5  # noqa: E402,F401

from flint import arb  # noqa: E402

import order2  # noqa: E402
import sharp_norms  # noqa: E402
import graded_dag as G  # noqa: E402
import rung3_engine as R1E  # noqa: E402

RECORDS = CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records"
W_IDX = [(r, j) for r in range(4) for j in range(1, 4 - r)]


def inputs(rec: dict, *, C_o0, g_res_factor, eta_mode: str) -> dict:
    ex = R1E.exact
    left, right = F(rec_cell(rec)["left"]), F(rec_cell(rec)["right"])
    e0, rho = F(rec["e0"][0]), F(rec["rho"][0])
    norms = sharp_norms.table(left, right)
    k = {i: norms["k"][i] for i in range(5)}
    j = {i: norms["j"][i] for i in range(5)}
    k[5], j[5] = k[4], j[4]                     # never read on these paths (graded_env is not used here)
    C = ex(F(rec["C_upper"]))
    obj = rec["objects"]
    aux = rec["auxiliary_evidence"]["objects"]
    rhoA, e0A = ex(rho), ex(e0)

    def val(d, key):
        return ex(F(d[key]))

    def entry(dm, dc, env):
        if eta_mode == "point0":
            m = dm + e0A * env
            return {"mid": (m, m, m), "cell": (dc, dc, dc)}
        return {"mid": (dm, dm, dm), "cell": (dc, dc, dc)}

    res = {}
    for name, o in obj.items():
        env = val(o, "envelope")
        res[name] = entry(val(o, "delta_mid"), val(o, "delta_cell"), env)
    ren = {}
    for r in range(5):
        ren[f"F_{r}:0"], ren[f"F_{r}:1"], ren[f"F_{r}:2"] = res.pop(f"F_{r}"), res.pop(f"dF_{r}"), res.pop(f"H_{r}")
    res.update(ren)
    for kk in range(3):
        res[f"Sclosed_{kk}"] = res.pop(f"Sclosed_{kk}")
    for name, o in aux.items():
        dm, env = val(o, "delta_mid"), val(o, "envelope")
        res[name] = entry(dm, dm + rhoA * env, env)
    alw = ex(F(rec["auxiliary_evidence"]["midpoint_eps"]["Sclosed:3"]))
    s04 = order2.sup_source_derivative_on(4, left, right)
    res["Sclosed_3"] = entry(alw, alw + rhoA * s04, s04)
    # G_r residual: not committed -> predeclared sweep multiple of the largest committed order-2 resolvent residual
    base = max((F(obj[f"H_{r}"]["delta_mid"]) for r in range(5)))
    for r in range(5):
        sH = F(rec["whole_cell_refinement"][str(r)]["second_order"]["H_at_e0"]) - F(rec["eps_mid"][f"H:{r}"])
        sD = F(rec["whole_cell_refinement"][str(r)]["second_order"]["D_at_e0"]) - F(rec["eps_mid"][f"D:{r}"])
        sF = F(obj[f"F_{r}"]["envelope"]) / F(str(norm_up(k[1])))
        sG = sH * g_res_factor
        envG = (ex(sG) * k[1] + k[4] * ex(sF) + arb(3) * k[3] * ex(sD) + arb(3) * k[2] * ex(sH))
        dm = ex(base * g_res_factor)
        res[f"F_{r}:3"] = entry(dm, dm + rhoA * envG, envG)
    eta_mid = ex(0) if eta_mode == "point0" else e0A
    return {"C": C, "C_e0": C, "C_o0": C_o0, "k": k, "j": j, "k_hull": k, "j_hull": j,
            "eta_mid": eta_mid, "eta_cell": ex(right), "x0_sigma_fixed": True, "res": res}


def norm_up(x):
    return R1E.fraction_of(x.abs_upper())


def rec_cell(rec):
    cells = json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_text())
    c = next(x for x in cells if x["detector"] == "CUSUM" and x["index"] == rec["cell_index"])
    return {"left": c["left"][0], "right": c["right"][0]}


def budget(rec: dict, k1, k2, k3, g_res) -> dict:
    """Exact term shares of the R1 scalar midpoint cascade F -> D -> H -> G for r = 0 (committed magnitudes)."""
    C = F(rec["C_upper"])
    o, a = rec["objects"], rec["auxiliary_evidence"]
    q = lambda x: F(x)
    dF, dD, dH = q(o["F_0"]["delta_mid"]), q(o["dF_0"]["delta_mid"]), q(o["H_0"]["delta_mid"])
    s0, s1, s2 = (q(o[f"Sclosed_{i}"]["delta_mid"]) for i in range(3))
    s3 = q(a["midpoint_eps"]["Sclosed:3"])
    eF = C * (dF + s0)
    eD = C * (dD + k1 * eF + s1)
    eH = C * (dH + k2 * eF + 2 * k1 * eD + s2)
    eG = C * (g_res + k3 * eF + 3 * k2 * eD + 3 * k1 * eH + s3)
    share = lambda parts, tot: {kk: float(v / tot) for kk, v in parts.items()}
    return {"C": float(C), "k1": float(k1), "k2": float(k2), "k3": float(k3),
            "eps_F": float(eF), "eps_D": float(eD), "eps_H": float(eH), "eps_G_lower_rule": float(eG),
            "shares_F": share({"C*delta_F": C * dF, "C*source": C * s0}, eF),
            "shares_D": share({"C*delta_D": C * dD, "C*k1*eps_F": C * k1 * eF, "C*source": C * s1}, eD),
            "shares_H": share({"C*delta_H": C * dH, "C*k2*eps_F": C * k2 * eF, "C*2k1*eps_D": C * 2 * k1 * eD,
                               "C*source": C * s2}, eH),
            "shares_G": share({"C*delta_G(assumed)": C * g_res, "C*k3*eps_F": C * k3 * eF, "C*3k2*eps_D": C * 3 * k2 * eD,
                               "C*3k1*eps_H": C * 3 * k1 * eH, "C*source": C * s3}, eG),
            "power_of_C_attribution": {"eps_F/delta": float(eF / (dF + s0)),
                                       "C^4*6k1^3*(delta_F+s0)": float(C ** 4 * 6 * k1 ** 3 * (dF + s0)),
                                       "raw_residuals": {"delta_F": float(dF), "delta_D": float(dD), "delta_H": float(dH),
                                                         "Sclosed_0..3": [float(s0), float(s1), float(s2), float(s3)]}},
            "candidate_sup_vs_error": {"sup_Dhat": float(q(rec["whole_cell_refinement"]["0"]["second_order"]["D_at_e0"])
                                                         - q(rec["eps_mid"]["D:0"])),
                                       "eps_D_mid": float(q(rec["eps_mid"]["D:0"])),
                                       "sup_Hhat": float(q(rec["whole_cell_refinement"]["0"]["second_order"]["H_at_e0"])
                                                         - q(rec["eps_mid"]["H:0"])),
                                       "eps_H_mid": float(q(rec["eps_mid"]["H:0"]))}}


def compute() -> dict:
    out = {"schema": "rebaseguard.p5y.k5.order3-r2.cell0-forecast.v1", "certified_inputs_only_except": "C_o0 and C_e0 sweeps",
           "no_R3_value_computed": True, "cells": {}, "budget_cell0": None}
    est = json.loads((NS / "evidence/e0_operator_estimate/E0_OPERATOR_ESTIMATE.json").read_text())
    sweep_Co = [("float_estimate_4.68", est["resolvent_odd_inf"]), ("10", 10), ("50", 50), ("466", 466), ("C_upper", None)]
    sweep_Ce = [("C_upper", None), ("float_full_466", est["resolvent_inf"]),
                ("hypothetical_deflated_11.2", est["even_resolvent_after_perron_deflation_inf"])]
    sweep_g = [1, 10, 100]
    fl = lambda d: {str(m): float(R1E.fraction_of(v)) for m, v in d.items()}
    for idx in (0, 309):
        rec = json.loads((RECORDS / f"aux5_CUSUM_{idx}_256.json").read_text())
        rows = []
        with R1E.precision(256):
            if idx == 0:
                left, right = F(rec_cell(rec)["left"]), F(rec_cell(rec)["right"])
                nm = sharp_norms.table(left, right)
                kf = lambda i: R1E.fraction_of(nm["k"][i].abs_upper())
                base = max(F(rec["objects"][f"H_{r}"]["delta_mid"]) for r in range(5))
                out["budget_cell0"] = budget(rec, kf(1), kf(2), kf(3), base)
            for gl in sweep_g:
                base_inp = inputs(rec, C_o0=R1E.exact(F(rec["C_upper"])), g_res_factor=gl, eta_mode="mid")
                scal = G.certify_graded(base_inp, parity=False)
                recon = {n: float(R1E.fraction_of(scal["mid"]["nodes"][n].t)) for n in ("F:0:0", "F:0:1", "F:0:2")}
                committed = {n: float(F(rec["eps_mid"][c])) for n, c in (("F:0:0", "F:0"), ("F:0:1", "D:0"),
                                                                           ("F:0:2", "H:0"))}
                for ce_label, ce in sweep_Ce:
                    for label, co in sweep_Co:
                        if ce is not None and label not in ("float_estimate_4.68",):
                            continue
                        coA = R1E.exact(F(rec["C_upper"])) if co is None else R1E.exact(F(str(co)))
                        rows_inp = {}
                        for mode in ("mid", "point0"):
                            inp = inputs(rec, C_o0=coA, g_res_factor=gl, eta_mode=mode)
                            if ce is not None:
                                inp["C_e0"] = R1E.exact(F(str(ce)))
                            rows_inp[mode] = G.certify_graded(inp, parity=True)
                        mid, pt0 = rows_inp["mid"], rows_inp["point0"]
                        nodes = {n: {"e": float(R1E.fraction_of(mid["mid"]["nodes"][n].e)),
                                     "o": float(R1E.fraction_of(mid["mid"]["nodes"][n].o)),
                                     "t": float(R1E.fraction_of(mid["mid"]["nodes"][n].t))}
                                 for n in ("F:0:0", "F:0:1", "F:0:2", "F:0:3")}
                        rows.append({"g_residual_factor": gl, "C_e0": ce_label, "C_o0": label,
                                     "R1_scalar_mid": fl(scal["rad_mid"]), "R1_scalar_cell": fl(scal["rad_cell"]),
                                     "R2_mid": fl(mid["rad_mid"]), "R2_point0_conservative_proxy": fl(pt0["rad_mid"]),
                                     "R2_cell": fl(mid["rad_cell"]), "R2_mid_nodes_r0": nodes,
                                     "resolvent_mode": [mid["mid"]["resolvent"]["mode"], mid["cell"]["resolvent"]["mode"]],
                                     "scalar_reconstruction_of_committed_eps_mid": {"recomputed": recon,
                                                                                    "committed": committed,
                                                                                    "equal": recon == committed}})
        out["cells"][str(idx)] = rows
    return out


def main():
    json.dump(compute(), sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
