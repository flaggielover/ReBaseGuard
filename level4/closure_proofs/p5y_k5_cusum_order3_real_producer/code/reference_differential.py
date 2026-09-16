"""Differential test of the Arb engine against the FROZEN exact-rational reference kernel. NON-SCIENTIFIC.

The reference kernel is `p5y_k5_cusum_order3_producer_design/code/order3_algebra.py` (frozen at 10911e51, qualified
at 1bf31bc8), on its own manufactured systems (`manufactured.py`). Its inputs are mapped onto the engine so that the
engine's F_r:3 midpoint and cascade and W:3 cascade and Taylor rules receive EXACTLY the reference's operands:

    mid F:r / D:r / H:r      <- ref eps_mid (F, r, 0 / 1 / 2)
    refined F:r / D:r / H:r  <- ref eps_cell (F, r, 0 / 1 / 2)
    g[r].delta_mid           <- ref delta (F, r, 3)
    g[r].delta_cell          <- ref delta (F, r, 3) + rho Env_3,  Env_3 = k_1 |Fhat_3| + sum_i C(3,i) k_(i+1) |Fhat_(3-i)|
    source r = 0 / r >= 1    <- mid Sclosed:3 / S:r:3 = epsS[r][3];  sup_S0_4 / tower S:r:4 = TS[r][4]
                                (aux S cascade disabled with a huge valid bound, so the Taylor source bound is kept,
                                 which is exactly the reference's src_cell)
    W chain                  <- ref eps_mid / eps_cell / towers / delta of W, with aux delta_cell = delta + rho Env_W

Required: engine eps_mid and cascade of F:r:3, and cascade and Taylor of W:(r,j):3, equal the reference's exact
values up to Arb outward rounding (engine >= reference, relative excess <= 2^-200); the engine's F:r:3 Taylor bound,
which uses a sharper admissible tower, is <= the reference's; the engine's export interval lies inside the
reference's; and the engine export contains the exact truth at e0 and on the reference grid.
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
DESIGN = NS.parents[0] / "p5y_k5_cusum_order3_producer_design/code"
if str(DESIGN) not in sys.path:
    sys.path.append(str(DESIGN))

import manufactured as RMF  # noqa: E402
import order3_algebra as RA  # noqa: E402

import rung3_engine as E  # noqa: E402

HUGE = Fr(10) ** 40
TOL = Fr(1, 2 ** 200)


def engine_inputs_from_reference(inp: dict, out: dict) -> dict:
    ex = E.exact
    k, rho = inp["k"], inp["rho"]
    Fh, Wh, Sh = inp["Fhat"], inp["What"], inp["Shat"]
    mid, cell, ref, aux, g, T = {}, {}, {}, {}, {}, {}
    for r in range(5):
        for n, nm in ((0, "F"), (1, "D"), (2, "H")):
            mid[f"{nm}:{r}"] = ex(out["eps_mid"][("F", r, n)])
            ref[f"{nm}:{r}"] = ex(out["eps_cell"][("F", r, n)])
        env3 = k[1] * RA.norm(Fh[r][3]) + sum((comb(3, i) * k[i + 1] * RA.norm(Fh[r][3 - i]) for i in range(1, 4)),
                                              Fr(0))
        d = out["delta"][("F", r, 3)]
        g[r] = {"delta_mid": ex(d), "delta_cell": ex(d + rho * env3)}
        for n in range(5):
            T[("S", r, n)] = ex(inp["TS"][r][n])
    mid["Sclosed:3"] = ex(inp["epsS"][0][3])
    for r in range(1, 5):
        mid[f"S:{r}:3"] = ex(inp["epsS"][r][3])
        aux[f"S_{r}:3"] = {"delta_mid": ex(HUGE), "delta_cell": ex(HUGE)}
    mid["S:0:3"] = ex(inp["epsS"][0][3])
    aux["S_0:3"] = {"delta_mid": ex(HUGE), "delta_cell": ex(HUGE)}
    for j in range(1, 5):
        mid[f"h:{j}:3"] = ex(Fr(0))
        aux[f"h_{j}:3"] = {"delta_mid": ex(HUGE), "delta_cell": ex(HUGE)}
        T[("h", j, 4)] = ex(Fr(0))
        for n in range(3):
            cell[f"h:{j}:{n}"] = ex(Fr(0))
    for r in range(4):
        for n in range(4):
            mid[f"W:{r}:0:{n}"] = ex(out["eps_mid"][("W", (r, 0), n)])
            if n <= 2:
                cell[f"W:{r}:0:{n}"] = ex(out["eps_cell"][("W", (r, 0), n)])
        T[("W", (r, 0), 4)] = ex(out["tower"][("W", (r, 0), 4)])
    for (r, j) in RA.W_INDICES:
        prev = (lambda n, r=r: Sh[r][n]) if j == 1 else (lambda n, r=r, j=j: Wh[(r, j - 1)][n])
        for n in range(4):
            mid[f"W:{r}:{j}:{n}"] = ex(out["eps_mid"][("W", (r, j), n)])
            if n <= 2:
                cell[f"W:{r}:{j}:{n}"] = ex(out["eps_cell"][("W", (r, j), n)])
        envw = sum((comb(3, i) * k[i + 1] * RA.norm(prev(3 - i)) for i in range(4)), Fr(0))
        dw = out["delta"][("W", (r, j), 3)]
        aux[f"W_{r}_{j}:3"] = {"delta_mid": ex(dw), "delta_cell": ex(dw + rho * envw)}
        T[("W", (r, j), 4)] = ex(out["tower"][("W", (r, j), 4)])
    for r in range(5):
        T[("S", r, 4)] = ex(inp["TS"][r][4])
    return {
        "C": ex(inp["C"]), "rho": ex(rho), "k": {i: ex(k[i]) for i in range(5)}, "j": {i: ex(Fr(0)) for i in range(5)},
        "mid": mid, "cell": cell, "refined": ref, "aux": aux, "g": g, "towers": T, "sup_S0_4": ex(inp["TS"][0][4]),
        "sup_hat": {(nm, r): ex(RA.norm(Fh[r][n])) for r in range(5) for n, nm in enumerate(("F", "D", "H", "G"))},
        "origin": {("G", r): ex(Fh[r][3][RA.ORIGIN]) for r in range(5)}
        | {("W", (r, 0)): ex(Sh[r][3][RA.ORIGIN]) for r in range(4)}
        | {("W", rj): ex(Wh[rj][3][RA.ORIGIN]) for rj in RA.W_INDICES},
    }


def compare(trial: dict, *, bits: int = 256) -> dict:
    e0, rho = Fr(trial["e0"]), Fr(trial["rho"])
    if trial["system"] == "random":                       # exactly the design runner's build_trial
        sysm = RMF.random_system(trial["seed"], trial["n"])
    else:
        sysm = RMF.scalar_controlled(trial["system"].split(":")[1], e0)
    perturb = {"F": (trial["perturb_F"][0], Fr(trial["perturb_F"][1]))} if "perturb_F" in trial else None
    inp, _truth = RMF.cell_inputs(sysm, e0, rho, perturb=perturb, seed=trial.get("seed", 0),
                                  noise=Fr(trial.get("noise", "0")))
    out = RA.cell_order3(inp)
    with E.precision(bits):                     # inputs are injected at the certifying precision
        res = E.certify_order3(engine_inputs_from_reference(inp, out), bits=bits)
    comp = res["components"]
    problems = []

    def eq(name, eng, refv):
        e = E.upper_fraction(eng)
        if not (refv <= e <= refv + TOL * max(refv, Fr(1))):
            problems.append(f"{name}: engine {float(e):.6e} != reference {float(refv):.6e}")

    for r in range(5):
        eq(f"F:{r}:3 eps_mid", comp[f"F:{r}:3"]["eps_mid"], out["eps_mid"][("F", r, 3)])
        eq(f"F:{r}:3 cascade", comp[f"F:{r}:3"]["cascade"], out["cascade"][("F", r, 3)])
        if E.upper_fraction(comp[f"F:{r}:3"]["taylor"]) > out["taylor"][("F", r, 3)] * (1 + TOL):
            problems.append(f"F:{r}:3 taylor exceeds the reference")
    for (r, j) in RA.W_INDICES:
        eq(f"W:{r}:{j}:3 cascade", comp[f"W:{r}:{j}:3"]["cascade"], out["cascade"][("W", (r, j), 3)])
        eq(f"W:{r}:{j}:3 taylor", comp[f"W:{r}:{j}:3"]["taylor"], out["taylor"][("W", (r, j), 3)])
    contained = True
    for m in E.M_VALUES:
        L, U = res["m"][m]["R3_cell"]
        rL, rU = out["m"][m]["export"]["L"], out["m"][m]["export"]["U"]
        if not (rL - TOL <= L and U <= rU + TOL):
            problems.append(f"m={m}: engine export not inside the reference export")
        pts = [e0] + [e0 - rho + 2 * rho * Fr(gp, 16) for gp in range(17)]
        for e in pts:
            t = sysm.true_R(e, m, 3)
            if not L <= t <= U:
                contained = False
                problems.append(f"m={m} e={e}: truth outside engine export")
    return {"trial": trial["id"], "problems": problems, "truth_contained": contained, "pass": not problems}
