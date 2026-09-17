"""R4 Strategy B on manufactured sigma-systems (R odd exactly): point run at e = 0 + local R^(5) majorant, against exact
truth. Pure: sigma_systems / manufactured_chain / graded_dag / r5_majorant / local_r5 only (no CUSUM operator code).

    point     graded_dag point interval at e0 = 0, rho = 0 (degenerate cell)                 -> I_0, point errors
    local M5  local_r5.local_tower on the hull [0, x1], anchored by point candidates + point errors -> M5
    L_B = lo(I_0) - (x1^2/2) M5,  U_B = hi(I_0) + (x1^2/2) M5
    reference: R3 Strategy A (graded whole cell) and R3 anchored M5 (first_cell.run), reported only

Checks on 17 grid points of [0, x1] (exact rational truth): I_0 contains R'''(0); L_B <= min R''' and U_B >= max R''';
every component (e, o, t) of every tower node n <= 5 and of every local anchor dominates the exact value; M5 >= max|R^(5)|.
Violation labels are typed ("tower", "anchor", "point", "strategyB", "M5") so a mutation's failure mode is attributable.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r3_infrastructure/code"),
           str(CP / "p5y_k5_cusum_order3_r2_repair/code"), str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import first_cell as FC3  # noqa: E402  (R3, frozen: exact truth helpers)
import graded_dag as G  # noqa: E402
import local_r5 as LR  # noqa: E402
import manufactured_chain as MC  # noqa: E402
import r5_majorant as R5  # noqa: E402
import rung3_engine as R1E  # noqa: E402
import sigma_systems as SS  # noqa: E402

FAM = ("F", "D", "H", "G")


def rig_key(node: str):
    parts = node.split(":")
    n = int(parts[-1])
    if parts[0] == "F":
        return (FAM[n], int(parts[1]), 0)
    if parts[0] in ("h", "S"):
        return (parts[0], int(parts[1]), n)
    if parts[0] == "W":
        return ("W", (int(parts[1]), int(parts[2])), n)
    return None


def run(spec: dict, *, r5=R5, lr=LR, bits: int = 256, reference: bool = True) -> dict:
    x1 = F(spec["x1"])
    sysm = SS.build(spec)
    noise = F(spec.get("noise", "0"))
    seed = int(spec["seed"])
    gr0 = SS.GradedRig(sysm, F(0), F(0), seed=seed, noise=noise)
    grH = SS.GradedRig(sysm, x1 / 2, x1 / 2, seed=seed, noise=noise)          # hull norms / constants only
    viol = []
    with R1E.precision(bits):
        ex = R1E.exact
        out0 = G.certify_graded(gr0.engine_inputs(), parity=True)
        pnodes = out0["mid"]["nodes"]
        cands = {}
        for node in pnodes:
            key = rig_key(node)
            if key is None or key not in gr0.P or int(node.split(":")[-1]) > 3:
                continue
            ge, go, _gt = SS.gnorm(gr0.P[key])
            cands[node] = (ex(ge), ex(go))
        hk = [MC.sup_deriv_poly(grH.rig.ex["K"], i, x1 / 2, mat=True) for i in range(7)]
        hj = [MC.sup_deriv_poly(grH.rig.ex["J"], i, x1 / 2, mat=True) for i in range(7)]
        base = {"C": ex(grH.C), "C_e0": ex(grH.C_e0), "C_o0": ex(grH.C_o0),
                "k": {i: ex(hk[i]) for i in range(7)}, "j": {i: ex(hj[i]) for i in range(7)}, "eta": ex(x1),
                "S0": {n: ex(grH.rig.T["S", 0, n]) for n in range(7)},
                "h1": {n: ex(grH.rig.T["h", 1, n]) for n in range(7)}}
        loc = lr.local_tower(base, cands, pnodes, x1=ex(x1), r5=r5)
        tw, M5 = loc["towers"], loc["M5"]
        rows = {}
        for m in G.M_VALUES:
            I0 = out0["m"][m]["R3_mid"]
            LB, UB = r5.strategy_b_bounds(I0, x1, M5[m])
            rows[m] = {"I0": I0, "L_B": LB, "U_B": UB, "M5": R1E.fraction_of(M5[m])}
        anchors = {n: (R1E.upper_fraction(v.e), R1E.upper_fraction(v.o), R1E.upper_fraction(v.t))
                   for n, v in loc["anchors"].items()}
        towers = {n: (R1E.upper_fraction(v.e), R1E.upper_fraction(v.o), R1E.upper_fraction(v.t)) for n, v in tw.items()}
    grid = [x1 * F(g, 16) for g in range(17)]
    ders = {e: FC3.true_derivs(sysm, e) for e in grid}
    for e in grid[1:]:
        if FC3.true_R(ders[e], 1, 0) != -FC3.true_R(FC3.true_derivs(sysm, -e, 0), 1, 0):
            viol.append(f"oddness: R not odd at {e}")
    for m, row in rows.items():
        vals3 = [FC3.true_R(ders[e], m, 3) for e in grid]
        vals5 = [abs(FC3.true_R(ders[e], m, 5)) for e in grid]
        if not row["I0"][0] <= vals3[0] <= row["I0"][1]:
            viol.append(f"point: m={m} I0 misses R'''(0)")
        if not (row["L_B"] <= min(vals3) and row["U_B"] >= max(vals3)):
            viol.append(f"strategyB: m={m} misses")
        if max(vals5) > row["M5"]:
            viol.append(f"M5: m={m} {float(row['M5']):.3e} < max|R5| {float(max(vals5)):.3e}")
    for label, table in (("tower", towers), ("anchor", anchors)):
        for e in grid:
            for node, (be, bo, bt) in table.items():
                ge, go, gt = SS.gnorm(ders[e][node])
                for lab, val, b in (("e", ge, be), ("o", go, bo), ("t", gt, bt)):
                    if val > b:
                        viol.append(f"{label}: {node}.{lab} at e={e}: {float(val):.3e} > {float(b):.3e}")
    rad = {}
    for m, row in rows.items():
        pen = x1 * x1 / 2 * row["M5"]
        pt = (row["I0"][1] - row["I0"][0]) / 2
        rad[str(m)] = {"radius_B_point": float(pt), "penalty_B_local": float(pen), "radius_B_local": float(pt + pen),
                       "M5_local": float(row["M5"]),
                       "true_max_abs_R5": float(max(abs(FC3.true_R(ders[e], m, 5)) for e in grid))}
    out = {"id": spec["id"], "violations": viol[:20], "violation_count": len(viol),
           "violation_kinds": sorted({v.split(":")[0] for v in viol}), "radii": rad,
           "C": float(grH.C), "C_e0": float(grH.C_e0), "C_o0": float(grH.C_o0), "x1": str(x1),
           "M5_trace_m1": [float(t) for t in loc["trace_m1"]]}
    if reference:
        r3 = FC3.run(spec)
        out["reference_R3"] = {str(m): {k: r3["radii"][m][k] for k in ("radius_A", "radius_B", "M5")} for m in r3["radii"]}
        out["reference_R3_violations"] = r3["violation_count"]
    return out
