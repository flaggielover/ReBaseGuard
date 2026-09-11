"""Phase 3/4 decisive estimate (NON-CERTIFYING): the SELF-CONSISTENT Taylor tower.

Every lower-order cell-uniform sup is bounded by Taylor from MIDPOINT sup-norms (orders <= 3, what order-3
auxiliary evidence would certify) plus the whole-cell order-4 bound, and the order-4 bound uses those lower-order
cell sups one level down. For X with midpoint sup-norms m_n = ||X^(n)(e0)||, n = 0..3, and a4 >= sup_cell||X''''||:
    a_n <= sum_{k=0}^{3-n} rho^k/k! m_{n+k} + rho^(4-n)/(4-n)! a4                 (Taylor, pointwise then sup)
    h_1: a4 <= k_4;  h_j: a4 <= sum_i C(4,i) k_i a_{4-i}(h_{j-1});  S_r: a4 <= sum_i C(4,i) kz_i a_{4-i}(h_r)
    S_0: a4 <= 2 sup|He_4 phi| + E a4(h_1) + 4 a3(h_1);  W: a4 <= sum_i C(4,i) k_i a_{4-i}(W_(r,j-1))
    F_r: a4 <= C ( sum_{i>=1} C(4,i) k_i a_{4-i}(F_r) + a4(f_r) ),  a_{4-i}(F_r) itself Taylor in a4  =>
         a4 <= C (sum_i C(4,i) k_i P_i + a4(f_r)) / (1 - C sum_i C(4,i) k_i rho^i/i!),  valid when the denominator > 0
         (a4 is a finite real number, so a4 <= c + q a4 with q < 1 gives a4 <= c/(1-q)).
Midpoint sup-norms, two variants: TRUE (max over Nystrom nodes, 5-point differences) and CERT-LIKE (for orders
<= 2: certified candidate sup sum|c_ij| + certified eps_mid; for order 3 and image nodes: TRUE times the largest
candidate-sup/true ratio seen at order 2). Norm variants: exact K_z and cert-form K_z.
"""
import json
import math
from math import comb
from pathlib import Path

import numpy as np
import sr_o9_candidates as T
import t4_cell as T4

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
CELL, MS = 313, (1, 2, 3, 5)


def objs(b, c, e):
    S = T.NodalSystem(b, c, e)
    M0, M1 = S.M[0], S.M[1]
    one = np.ones(S.A.shape[0])
    o = {"h:1": one - M0 @ one}
    for j in range(2, 5):
        o[f"h:{j}"] = M0 @ o[f"h:{j-1}"]
    o["S:0"] = S.s0raw - e * o["h:1"]
    for r in range(1, 5):
        o[f"S:{r}"] = M1 @ o[f"h:{r}"]
    for r in range(4):
        for j in range(1, 4 - r):
            o[f"W:{r},{j}"] = M0 @ (o[f"S:{r}"] if j == 1 else o[f"W:{r},{j-1}"])
    o["f:0"] = S.s0raw
    for r in range(1, 5):
        o[f"f:{r}"] = o[f"S:{r}"] + e * o["h:1"]
    for r in range(5):
        o[f"F:{r}"] = np.linalg.solve(S.A, o[f"f:{r}"])
    return o


def main():
    T.check_threads()
    orc = json.loads((NS / "evidence/phase34_oracle_c313.json").read_text())
    geo = orc["geometry"]
    e0, rho, C, E, d = geo["e0"], geo["rho"], geo["C_upper"], geo["E"], geo["fd_step"]
    cell = T.frozen_cell(CELL)
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        b, c = T.nearest_double(g["b"]), T.nearest_double(g["c"])
    V = {q: objs(b, c, e0 + q * d) for q in (-2, -1, 0, 1, 2)}
    st = {0: ([0, 0, 1, 0, 0], 1), 1: ([-1, 8, 0, -8, 1], 12), 2: ([-1, 16, -30, 16, -1], 12), 3: ([1, -2, 0, 2, -1], 2)}
    true = {}
    for name in V[0]:
        true[name] = []
        for n in range(4):
            cf, den = st[n]
            vec = sum(ci * V[q][name] for ci, q in zip(cf, (2, 1, 0, -1, -2))) / (den * d ** n)
            true[name].append(float(np.max(np.abs(vec))))
    built = T.build_cell_candidates(CELL)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    kill = json.loads((CP / "p5y_k1_sr_o9_curvature_successor/evidence/kill/t4_c313.json").read_text())
    epsm = {k: float(T4.Fr(v)) for k, v in kill["eps_mid"].items()}
    cert, ratios = {}, []
    for name in true:
        if name.startswith("f:"):
            continue
        row = []
        for n in range(3):
            cn = f"{name}:k{n}"
            if cn in mant:
                v = float(T4.Fr(str(T4.mag_fraction(T4.cand_sup(mant[cn]))))) + epsm.get(cn, 0.0)
                if n == 2 and true[name][2] > 1e-12:
                    ratios.append(v / true[name][2])
                row.append(v)
            else:
                row.append(None)
        cert[name] = row
    R = max(ratios) if ratios else 1.0
    for name in cert:
        cert[name] = [x if x is not None else true[name][n] * R for n, x in enumerate(cert[name])] + [true[name][3] * R]
    for r in range(5):
        cert[f"f:{r}"] = [x * R for x in true[f"f:{r}"]]
    k = orc["norms"]["k"]
    s0 = orc["norms"]["sup_src0_deriv"]

    def run(mids, kz):
        a = {}

        def taylor(mm, a4):
            return [sum(rho ** q / math.factorial(q) * mm[n + q] for q in range(4 - n)) + rho ** (4 - n) / math.factorial(4 - n) * a4
                    for n in range(4)] + [a4]
        a["h:1"] = taylor(mids["h:1"], k[4])
        for j in range(2, 5):
            p = a[f"h:{j-1}"]
            a[f"h:{j}"] = taylor(mids[f"h:{j}"], sum(comb(4, i) * k[i] * p[4 - i] for i in range(5)))
        a["S:0"] = taylor(mids["S:0"], s0[4] + E * a["h:1"][4] + 4 * a["h:1"][3])
        for r in range(1, 5):
            p = a[f"h:{r}"]
            a[f"S:{r}"] = taylor(mids[f"S:{r}"], sum(comb(4, i) * kz[i] * p[4 - i] for i in range(5)))
        for r in range(4):
            for j in range(1, 4 - r):
                p = a[f"S:{r}"] if j == 1 else a[f"W:{r},{j-1}"]
                a[f"W:{r},{j}"] = taylor(mids[f"W:{r},{j}"], sum(comb(4, i) * k[i] * p[4 - i] for i in range(5)))
        q_ = C * sum(comb(4, i) * k[i] * rho ** i / math.factorial(i) for i in range(1, 5))
        for r in range(5):
            f4 = s0[4] if r == 0 else a[f"S:{r}"][4] + E * a["h:1"][4] + 4 * a["h:1"][3]
            mm = mids[f"F:{r}"]
            P = {i: sum(rho ** q / math.factorial(q) * mm[4 - i + q] for q in range(i)) for i in range(1, 5)}
            a4 = C * (sum(comb(4, i) * k[i] * P[i] for i in range(1, 5)) + f4) / (1 - q_)
            a[f"F:{r}"] = taylor(mm, a4)
        out = {"contraction_q": q_}
        for m in MS:
            M4 = sum(a[f"F:{r}"][4] for r in range(m)) / m
            for t in range(1, m):
                for r in range(t):
                    M4 += (1.0 / t - 1.0 / m) * (a[f"S:{r}"][4] if t - r - 1 == 0 else a[f"W:{r},{t-r-1}"][4])
            tr, cv = orc["true"][str(m)], orc["cover"][str(m)]
            M2 = abs(tr["R2_e0"]) + rho * abs(tr["R3_e0"]) + rho * rho / 2 * M4
            out[str(m)] = {"M_R4": M4, "Q": abs(tr["R3_e0"]) + rho / 2 * M4, "target_Q": cv["target_Q"], "M_R2_taylor": M2,
                           "B_cover_ratio": (rho * tr["D_mag_certified"] + rho * rho / 2 * M2) / 0.05}
        out["a4"] = {n: v[4] for n, v in a.items()}
        return out

    res = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-consistent.v1", "cell": CELL, "DIAGNOSTIC_ONLY": True,
           "cand_sup_over_true_ratio_order2_max": R, "midpoint_true": true, "midpoint_certlike": cert, "variants": {}}
    for ml, mids in (("true_midpoint", true), ("certlike_midpoint", cert)):
        for kl, kz in (("kz_exact", orc["norms"]["kz_exact"]), ("kz_certform", orc["norms"]["kz_certform"])):
            res["variants"][f"{ml}/{kl}"] = run(mids, kz)
    (NS / "evidence/phase34_consistent_c313.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print("cand_sup/true ratio (order 2, max):", round(R, 4))
    for lab, v in res["variants"].items():
        print(f"{lab:32s} q={v['contraction_q']:.3f} " + " | ".join(
            f"m{m}: M4={v[str(m)]['M_R4']:.4g} Q={v[str(m)]['Q']:.3g}/{v[str(m)]['target_Q']:.3g} ratio={v[str(m)]['B_cover_ratio']:.3g}" for m in MS))


if __name__ == "__main__":
    main()
