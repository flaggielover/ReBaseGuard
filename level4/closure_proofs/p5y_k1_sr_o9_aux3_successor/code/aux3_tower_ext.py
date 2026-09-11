"""Phase 3/4 extension (NON-CERTIFYING): how far is any norm-based fourth-order remainder from sufficient?

(1) ONE-LEVEL hybrid order-4 bound: the norm recursion is applied at the top level only, with every lower-order
    cell-uniform sup (over states and the parent cell) replaced by its TRUE value from dense Nystrom solves:
        ||F_r''''|| <= C ( sum_{i>=1} C(4,i) k_i ||F_r^(4-i)||_true + ||f_r''''||_true )
        ||W_(r,j)''''|| <= sum_i C(4,i) k_i ||W_(r,j-1)^(4-i)||_true           (W_(r,0) = S_r: true)
    This is the floor of any "analytic remainder from lower-order evidence" of the aux3 type.
(2) Pure norm towers to order 8 and the Taylor order n at which the remainder alone fits:
        M_R2 <= sum_{k=0}^{n-3} rho^k/k! |R^(k+2)(e0)| + rho^(n-2)/(n-2)! * T_n
    (midpoint derivatives taken as their TRUE values, i.e. ideal midpoint evidence for orders 3..n-1).
"""
import json
import math
from math import comb
from pathlib import Path

import numpy as np
import sr_o9_candidates as T
import aux3_oracle as O

NS = Path(__file__).resolve().parents[1]
CELL, MS, NMAX = 313, (2, 3, 5), 8


def fdv(v, d, order):
    st = {1: ([-1, 8, 0, -8, 1], 12), 2: ([-1, 16, -30, 16, -1], 12), 3: ([1, -2, 0, 2, -1], 2), 4: ([1, -4, 6, -4, 1], 1)}
    c, den = st[order]
    return sum(ci * v[q] for ci, q in zip(c, (2, 1, 0, -1, -2))) / (den * d ** order)


def main():
    T.check_threads()
    oracle = json.loads((NS / "evidence/phase34_oracle_c313.json").read_text())
    geo = oracle["geometry"]
    e0, rho, C, E, d = geo["e0"], geo["rho"], geo["C_upper"], geo["E"], geo["fd_step"]
    cell = T.frozen_cell(CELL)
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        b, c = T.nearest_double(g["b"]), T.nearest_double(g["c"])
    ks = list(range(-6, 7))
    sol = {}
    for kk in ks:
        S = T.NodalSystem(b, c, e0 + kk * d)
        one = np.ones(S.A.shape[0])
        h = {1: one - S.M[0] @ one}
        for j in range(2, 5):
            h[j] = S.M[0] @ h[j - 1]
        Sr = {0: S.s0raw - (e0 + kk * d) * h[1]}
        for r in range(1, 5):
            Sr[r] = S.M[1] @ h[r]
        f = {0: S.s0raw}
        for r in range(1, 5):
            f[r] = Sr[r] + (e0 + kk * d) * h[1]
        F = {r: np.linalg.solve(S.A, f[r]) for r in range(5)}
        W = {}
        for r in range(4):
            W[(r, 0)] = Sr[r]
            for j in range(1, 4 - r):
                W[(r, j)] = S.M[0] @ W[(r, j - 1)]
        sol[kk] = {"F": F, "f": f, "W": W}
    cellpts = range(-4, 5)

    def true_sup(get, n):
        if n == 0:
            return max(float(np.max(np.abs(get(q)))) for q in cellpts)
        return max(float(np.max(np.abs(fdv({s: get(q + s) for s in (-2, -1, 0, 1, 2)}, d, n)))) for q in cellpts)

    k = oracle["norms"]["k"]
    hyb = {}
    for r in range(5):
        sF = [true_sup(lambda q, r=r: sol[q]["F"][r], n) for n in range(4)]
        sf4 = true_sup(lambda q, r=r: sol[q]["f"][r], 4)
        hyb["F", r] = C * (sum(comb(4, i) * k[i] * sF[4 - i] for i in range(1, 5)) + sf4)
    for (r, j) in sol[0]["W"]:
        if j == 0:
            hyb["W", (r, 0)] = true_sup(lambda q, r=r: sol[q]["W"][(r, 0)], 4)
        else:
            sW = [true_sup(lambda q, r=r, j=j: sol[q]["W"][(r, j - 1)], n) for n in range(5)]
            hyb["W", (r, j)] = sum(comb(4, i) * k[i] * sW[4 - i] for i in range(5))
    res = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-tower-ext.v1", "cell": CELL, "DIAGNOSTIC_ONLY": True,
           "one_level_hybrid": {}, "pure_tower_orders": {}, "minimal_taylor_order": {}}
    for m in MS:
        M4 = sum(hyb["F", r] for r in range(m)) / m
        for t in range(1, m):
            for r in range(t):
                M4 += (1.0 / t - 1.0 / m) * hyb["W", (r, t - r - 1)]
        tr = oracle["true"][str(m)]
        Mmax = oracle["cover"][str(m)]["M_R2_max_for_ratio_1"]
        M2 = abs(tr["R2_e0"]) + rho * abs(tr["R3_e0"]) + rho * rho / 2 * M4
        res["one_level_hybrid"][str(m)] = {"M_R4": M4, "Q": abs(tr["R3_e0"]) + rho / 2 * M4,
                                           "target_Q": oracle["cover"][str(m)]["target_Q"],
                                           "B_cover_ratio": (rho * tr["D_mag_certified"] + rho * rho / 2 * M2) / 0.05}
    # pure towers to order NMAX with exact norms
    grid = np.linspace(e0 - rho, e0 + rho, 21)
    kn = [max(O.integ_abs(O.he(i), -c + e, c + e) for e in grid) for i in range(NMAX + 1)]
    kz = [max(O.integ_abs(np.poly1d([1.0, -e]) * O.he(i), -c + e, c + e) for e in grid) for i in range(NMAX + 1)]
    w = np.linspace(-15, 15, 300001)
    s0 = [2 * float(np.max(np.abs(O.he(n)(w) * np.exp(-w * w / 2) / math.sqrt(2 * math.pi)))) for n in range(NMAX + 1)]
    Th = {(1, 0): 1.0}
    for n in range(1, NMAX + 1):
        Th[1, n] = kn[n]
    for j in range(2, 5):
        for n in range(NMAX + 1):
            Th[j, n] = sum(comb(n, i) * kn[i] * Th[j - 1, n - i] for i in range(n + 1))
    TS, TW, TF = {}, {}, {}
    for n in range(NMAX + 1):
        TS[0, n] = s0[n] + E * Th[1, n] + (n * Th[1, n - 1] if n else 0.0)
        for r in range(1, 5):
            TS[r, n] = sum(comb(n, i) * kz[i] * Th[r, n - i] for i in range(n + 1))
    for r in range(4):
        for n in range(NMAX + 1):
            TW[(r, 0), n] = TS[r, n]
        for j in range(1, 4 - r):
            for n in range(NMAX + 1):
                TW[(r, j), n] = sum(comb(n, i) * kn[i] * TW[(r, j - 1), n - i] for i in range(n + 1))
    for r in range(5):
        for n in range(NMAX + 1):
            fs = s0[n] if r == 0 else TS[r, n] + E * Th[1, n] + (n * Th[1, n - 1] if n else 0.0)
            TF[r, n] = C * (sum(comb(n, i) * kn[i] * TF[r, n - i] for i in range(1, n + 1)) + fs)
    for m in MS:
        tow = []
        for n in range(NMAX + 1):
            v = sum(TF[r, n] for r in range(m)) / m
            for t in range(1, m):
                for r in range(t):
                    v += (1.0 / t - 1.0 / m) * TW[(r, t - r - 1), n]
            tow.append(v)
        tr = oracle["true"][str(m)]
        Mmax = oracle["cover"][str(m)]["M_R2_max_for_ratio_1"]
        mids = [abs(tr["R2_e0"]), abs(tr["R3_e0"]), abs(tr["R4_e0"])]
        rows = []
        for n in range(4, NMAX + 1):
            mid = sum(rho ** kk / math.factorial(kk) * (mids[kk] if kk < 3 else tr["sup_cell_R4"]) for kk in range(n - 2))
            rem = rho ** (n - 2) / math.factorial(n - 2) * tow[n]
            rows.append({"taylor_order_n": n, "midpoint_orders_needed": list(range(3, n)), "tower_T_n": tow[n],
                         "remainder": rem, "M_R2_bound": mid + rem, "M_R2_max": Mmax,
                         "B_cover_ratio": (rho * tr["D_mag_certified"] + rho * rho / 2 * (mid + rem)) / 0.05})
        res["pure_tower_orders"][str(m)] = rows
        ok = [r["taylor_order_n"] for r in rows if r["B_cover_ratio"] < 1]
        res["minimal_taylor_order"][str(m)] = ok[0] if ok else None
    res["norms_to_order"] = {"k": kn, "kz_exact": kz, "src0": s0}
    (NS / "evidence/phase34_tower_ext_c313.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    for m in MS:
        h_ = res["one_level_hybrid"][str(m)]
        print(f"m{m} one-level hybrid M_R4={h_['M_R4']:.4g} Q={h_['Q']:.4g} target={h_['target_Q']:.4g} ratio={h_['B_cover_ratio']:.4g}")
        print("   pure tower by Taylor order:", [(r["taylor_order_n"], round(r["tower_T_n"], 1), round(r["B_cover_ratio"], 3))
                                                 for r in res["pure_tower_orders"][str(m)]], "minimal n:", res["minimal_taylor_order"][str(m)])


if __name__ == "__main__":
    main()
