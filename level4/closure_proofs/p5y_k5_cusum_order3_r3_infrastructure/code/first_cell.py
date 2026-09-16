"""R3 Part F on manufactured sigma-systems (R odd exactly): Strategy A vs Strategy B, certified, against exact truth.

    Strategy A  graded_dag whole-cell interval on [0, x1]                              -> (L_A, U_A)
    Strategy B  graded_dag point interval at e0 = 0, rho = 0 (degenerate cell)         -> I_0
                + r5_majorant tower on the hull [0, x1], anchored at orders <= 3 on the Strategy-A candidates
                (graded candidate sup + graded whole-cell error)                        -> M5
                L_B = lo(I_0) - (x1^2/2) M5,  U_B = hi(I_0) + (x1^2/2) M5

Checks (exact truth on 17 grid points of [0, x1] plus e = 0): R odd at the grid; I_0 contains R'''(0); L_A, L_B <=
min R'''; U_A, U_B >= max R'''; every tower component (e, o, t) of every true object for n <= 5 dominates the exact
value; M5 >= max |R^(5)|. Reported: radius_A = (U_A - L_A)/2 and radius_B = (hi - lo)(I_0)/2 + penalty.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from math import factorial
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r2_repair/code"),
           str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import graded_dag as G  # noqa: E402
import manufactured_chain as MC  # noqa: E402
import r5_majorant as R5  # noqa: E402
import rung3_engine as R1E  # noqa: E402
import sigma_systems as SS  # noqa: E402


def true_derivs(sysm, e: F, nmax: int = 5) -> dict:
    ex = sysm.expand(e, nmax + 1)
    D = MC.ChainSystem.deriv
    out = {}
    for j in range(1, 5):
        out.update({f"h:{j}:{n}": D(ex["h"][j], n) for n in range(nmax + 1)})
    for r in range(5):
        out.update({f"S:{r}:{n}": D(ex["S"][r], n) for n in range(nmax + 1)})
        out.update({f"F:{r}:{n}": D(ex["F"][r], n) for n in range(nmax + 1)})
    for rj, coeffs in ex["W"].items():
        out.update({f"W:{rj[0]}:{rj[1]}:{n}": D(coeffs, n) for n in range(nmax + 1)})
    return out


def true_R(der: dict, m: int, n: int) -> F:
    return sum((c * (der[f"F:{r}:{n}"] if kind == "F" else der[f"W:{r}:{j}:{n}"])[0]
                for kind, r, j, c in R1E.coefficients(m)), F(0))


FAM = ("F", "D", "H", "G")


def run(spec: dict, *, r5=R5, anchors_with_error: bool = True, bits: int = 256) -> dict:
    x1 = F(spec["x1"])
    sysm = SS.build(spec)
    noise = F(spec.get("noise", "0"))
    seed = int(spec["seed"])
    grA = SS.GradedRig(sysm, x1 / 2, x1 / 2, seed=seed, noise=noise)
    gr0 = SS.GradedRig(sysm, F(0), F(0), seed=seed, noise=noise)
    viol = []
    with R1E.precision(bits):
        outA = G.certify_graded(grA.engine_inputs(), parity=True)
        out0 = G.certify_graded(gr0.engine_inputs(), parity=True)
        ex = R1E.exact
        anchors = {}
        cellN = outA["cell"]["nodes"]
        for node, v in cellN.items():
            parts = node.split(":")
            n = int(parts[-1])
            if parts[0] == "F":
                key = (FAM[n], int(parts[1]), 0)
            elif parts[0] == "h":
                key = ("h", int(parts[1]), n)
            elif parts[0] == "S":
                key = ("S", int(parts[1]), n)
            elif parts[0] == "W":
                key = ("W", (int(parts[1]), int(parts[2])), n)
            else:
                continue
            if key not in grA.P:
                continue
            ge, go, gt = SS.gnorm(grA.P[key])
            if anchors_with_error:
                anchors[node] = G.V(ex(ge) + v.e, ex(go) + v.o, ex(gt) + v.t)
            else:
                anchors[node] = G.V(ex(ge), ex(go), ex(gt))
        hk = [MC.sup_deriv_poly(grA.rig.ex["K"], i, x1 / 2, mat=True) for i in range(7)]
        hj = [MC.sup_deriv_poly(grA.rig.ex["J"], i, x1 / 2, mat=True) for i in range(7)]
        tin = {"C": ex(grA.C), "C_e0": ex(grA.C_e0), "C_o0": ex(grA.C_o0),
               "k": {i: ex(hk[i]) for i in range(7)}, "j": {i: ex(hj[i]) for i in range(7)}, "eta": ex(x1),
               "S0": {n: ex(grA.rig.T["S", 0, n]) for n in range(7)},
               "h1": {n: ex(grA.rig.T["h", 1, n]) for n in range(7)}, "anchors": anchors}
        tw = r5.true_tower(tin, parity=True)
        M5 = r5.m5(tw["towers"], parity=True)
        rows = {}
        for m in G.M_VALUES:
            I0 = out0["m"][m]["R3_mid"]
            LB, UB = r5.strategy_b_bounds(I0, x1, M5[m])
            LA, UA = outA["m"][m]["R3_cell"]
            rows[m] = {"L_A": LA, "U_A": UA, "I0": I0, "L_B": LB, "U_B": UB, "M5": R1E.fraction_of(M5[m])}
    grid = [x1 * F(g, 16) for g in range(17)]
    ders = {e: true_derivs(sysm, e) for e in grid}
    for e in grid[1:]:
        if true_R(ders[e], 1, 0) != -true_R(true_derivs(sysm, -e, 0), 1, 0):
            viol.append(f"R not odd at {e}")
    for m, row in rows.items():
        vals3 = [true_R(ders[e], m, 3) for e in grid]
        vals5 = [abs(true_R(ders[e], m, 5)) for e in grid]
        t0 = vals3[0]
        if not row["I0"][0] <= t0 <= row["I0"][1]:
            viol.append(f"m={m} point interval misses R'''(0)")
        if not (row["L_A"] <= min(vals3) and row["U_A"] >= max(vals3)):
            viol.append(f"m={m} strategy A misses")
        if not (row["L_B"] <= min(vals3) and row["U_B"] >= max(vals3)):
            viol.append(f"m={m} strategy B misses")
        if max(vals5) > row["M5"]:
            viol.append(f"m={m} M5 {float(row['M5']):.3e} < max|R5| {float(max(vals5)):.3e}")
    for e in grid:
        for node, v in tw["towers"].items():
            ge, go, gt = SS.gnorm(ders[e][node])
            for lab, val, b in (("e", ge, v.e), ("o", go, v.o), ("t", gt, v.t)):
                if val > R1E.upper_fraction(b):
                    viol.append(f"tower {node}.{lab} at e={e}: {float(val):.3e} > {float(R1E.upper_fraction(b)):.3e}")
    rad = {}
    for m, row in rows.items():
        pen = x1 * x1 / 2 * row["M5"]
        rad[m] = {"radius_A": float((row["U_A"] - row["L_A"]) / 2), "radius_B_point": float((row["I0"][1] - row["I0"][0]) / 2),
                  "penalty_B": float(pen), "radius_B": float((row["I0"][1] - row["I0"][0]) / 2 + pen),
                  "M5": float(row["M5"]), "true_max_abs_R5": float(max(abs(true_R(ders[e], m, 5)) for e in grid))}
    return {"id": spec["id"], "violations": viol[:20], "violation_count": len(viol), "radii": rad,
            "C": float(grA.C), "C_e0": float(grA.C_e0), "C_o0": float(grA.C_o0), "tower_mode": tw["resolvent_mode"],
            "x1": str(x1)}


def evenness_lemma_check(seed: int) -> dict:
    """Independent exact check of the transport inequality on random odd polynomials (and its failure for a
    non-odd control, showing R''''(0) = 0 is load-bearing)."""
    g = MC.Rng(seed)
    out = {}
    for label, odd in (("odd", True), ("control_not_odd", False)):
        coeffs = [F(0)] * 10
        for p in range(10):
            if (p % 2 == 1) or not odd:
                coeffs[p] = g.frac(1000, 100) / factorial(p)
        if not odd:
            coeffs[4] = F(-50)                                   # R''''(0) = -1200: R''' must drop linearly
        d = lambda n, e: sum((F(factorial(p), factorial(p - n)) * coeffs[p] * e ** (p - n)
                              for p in range(n, 10)), F(0))
        x1 = F(1, 5)
        sup5 = sum((F(factorial(p), factorial(p - 5)) * abs(coeffs[p]) * x1 ** (p - 5) for p in range(5, 10)), F(0))
        fails = [e for e in (x1 * F(i, 40) for i in range(41)) if d(3, e) < d(3, F(0)) - e * e / 2 * sup5]
        out[label] = {"holds_on_grid": not fails, "first_failure": None if not fails else str(fails[0])}
    out["pass"] = out["odd"]["holds_on_grid"] and not out["control_not_odd"]["holds_on_grid"]
    return out
