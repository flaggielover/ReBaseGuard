"""Phases 3-4 (NON-CERTIFYING feasibility oracle) for SR cell 313, m = 1,2,3,5.

(a) TRUE scalar R_m(x0, e): float Nystrom solves (the frozen T1 NodalSystem, degree 16, 220-point quadrature) at
    e = e0 + k*delta, delta = rho/4, k = -6..6; R'', R''', R'''' by 5-point central differences; values at e0 and
    sup over the parent cell from the grid points |k| <= 4.
(b) Fourth-order NORM TOWER T[X,4] (aux3 construction, extended to the SR resolvent): norm-only bounds on the TRUE
    objects, uniform over all states and every e in the parent cell:
      h_1^(0) <= 1, h_1^(n) <= k_n;  h_j^(n) <= sum_i C(n,i) k_i h_{j-1}^(n-i)
      S_0 = (phi(U)-phi(L)) - e h_1: S_0^(n) <= 2 sup|He_n phi| + E h_1^(n) + n h_1^(n-1)
      S_r^(n) <= sum_i C(n,i) kz_i h_r^(n-i);  W_(r,j)^(n) <= sum_i C(n,i) k_i W_(r,j-1)^(n-i),  W_(r,0) = S_r
      (I-K)F_r^(n) = sum_{i>=1} C(n,i) K^(i) F_r^(n-i) + f_r^(n),  f_0 = phi(U)-phi(L),  f_r = S_r + e h_1
      F_r^(n) <= C_upper * ( sum_{i>=1} C(n,i) k_i F_r^(n-i) + f_r^(n) )
    with k_i = max_e int_{-c+e}^{c+e}|He_i|phi and two K_z variants: EXACT (max_e int|w-e||He_i(w)|phi(w)dw, the
    tightest any proved norm can be) and CERT-FORM (A_{i+1} + i A_{i-1} + E A_i, the curv_mv construction).
    Norms are evaluated numerically (diagnostic); a certified successor would need outward arb versions.
(c) Third-order Taylor cover of the frozen STYLE_1 form, with M_R2 replaced by
      M_R2_taylor = |R''(e0)| + rho |R'''(e0)| + (rho^2/2) M_R4,
    using the certified D_interval magnitude of the curvature-successor kill record.
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
CELL = 313
MS = (1, 2, 3, 5)
XG, WG = np.polynomial.legendre.leggauss(48)


def he(n):
    a, b = np.poly1d([1.0]), np.poly1d([1.0, 0.0])
    if n == 0:
        return a
    for k in range(1, n):
        a, b = b, np.poly1d([1.0, 0.0]) * b - k * a
    return b


def integ_abs(P, a, b):
    rts = [r.real for r in np.roots(P.coeffs) if abs(r.imag) < 1e-12 and a < r.real < b] if P.order > 0 else []
    pts = sorted([a, b] + rts)
    tot = 0.0
    for lo, hi in zip(pts[:-1], pts[1:]):
        ed = np.linspace(lo, hi, 25)
        for l, h in zip(ed[:-1], ed[1:]):
            x = 0.5 * (h - l) * XG + 0.5 * (h + l)
            tot += abs(float(np.sum(WG * P(x) * np.exp(-x * x / 2))) / math.sqrt(2 * math.pi) * 0.5 * (h - l))
    return tot


def objects(b, c, e):
    S = T.NodalSystem(b, c, e)
    M0, M1 = S.M[0], S.M[1]
    one = np.ones(S.A.shape[0])
    h = {1: one - M0 @ one}
    for j in range(2, 5):
        h[j] = M0 @ h[j - 1]
    Sr = {0: S.s0raw - e * h[1]}
    for r in range(1, 5):
        Sr[r] = M1 @ h[r]
    W = {}
    for r in range(4):
        W[(r, 0)] = Sr[r]
        for j in range(1, 4 - r):
            W[(r, j)] = M0 @ W[(r, j - 1)]
    F = {r: np.linalg.solve(S.A, S.s0raw if r == 0 else Sr[r] + e * h[1]) for r in range(5)}
    return F, W


def R_of(F, W, m, idx=0):
    v = sum(F[r][idx] for r in range(m)) / m
    for t in range(1, m):
        for r in range(t):
            v += (1.0 / t - 1.0 / m) * W[(r, t - r - 1)][idx]
    return v


def fd(f, k, d):
    g = lambda q: f[k + q]                                  # noqa: E731
    return {1: (-g(2) + 8 * g(1) - 8 * g(-1) + g(-2)) / (12 * d),
            2: (-g(2) + 16 * g(1) - 30 * g(0) + 16 * g(-1) - g(-2)) / (12 * d * d),
            3: (g(2) - 2 * g(1) + 2 * g(-1) - g(-2)) / (2 * d ** 3),
            4: (g(2) - 4 * g(1) + 6 * g(0) - 4 * g(-1) + g(-2)) / d ** 4}


def towers(k, kz, C, E, s0):
    Th = {(1, 0): 1.0}
    for n in range(1, 5):
        Th[1, n] = k[n]
    for j in range(2, 5):
        for n in range(5):
            Th[j, n] = sum(comb(n, i) * k[i] * Th[j - 1, n - i] for i in range(n + 1))
    TS = {}
    for n in range(5):
        TS[0, n] = s0[n] + E * Th[1, n] + (n * Th[1, n - 1] if n else 0.0)
        for r in range(1, 5):
            TS[r, n] = sum(comb(n, i) * kz[i] * Th[r, n - i] for i in range(n + 1))
    TW = {}
    for r in range(4):
        for n in range(5):
            TW[(r, 0), n] = TS[r, n]
        for j in range(1, 4 - r):
            for n in range(5):
                TW[(r, j), n] = sum(comb(n, i) * k[i] * TW[(r, j - 1), n - i] for i in range(n + 1))
    TF = {}
    for r in range(5):
        for n in range(5):
            fs = s0[n] if r == 0 else TS[r, n] + E * Th[1, n] + (n * Th[1, n - 1] if n else 0.0)
            TF[r, n] = C * (sum(comb(n, i) * k[i] * TF[r, n - i] for i in range(1, n + 1)) + fs)
    return Th, TS, TW, TF


def assemble_tower(TF, TW, m, n):
    v = sum(TF[r, n] for r in range(m)) / m
    for t in range(1, m):
        for r in range(t):
            v += (1.0 / t - 1.0 / m) * TW[(r, t - r - 1), n]
    return v


def main():
    T.check_threads()
    cell = T.frozen_cell(CELL)
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        b, c, e0 = T.nearest_double(g["b"]), T.nearest_double(g["c"]), T.nearest_double(g["e0"])
        rho = float(g["rho"].mid())
    C = float(T4.Fr(cell["C_upper"]))
    d = rho / 4
    ks = list(range(-6, 7))
    Rv = {m: {} for m in MS}
    F_nodes = {}
    for kk in ks:
        F, W = objects(b, c, e0 + kk * d)
        F_nodes[kk] = (F, W)
        for m in MS:
            Rv[m][kk] = R_of(F, W, m)
    kill = json.loads((CP / "p5y_k1_sr_o9_curvature_successor/evidence/kill/t4_c313.json").read_text())
    true = {}
    for m in MS:
        at = {kk: fd(Rv[m], kk, d) for kk in range(-4, 5)}
        true[str(m)] = {"R_e0": Rv[m][0], "R1_e0": at[0][1], "R2_e0": at[0][2], "R3_e0": at[0][3], "R4_e0": at[0][4],
                        "sup_cell_R2": max(abs(at[q][2]) for q in at), "sup_cell_R3": max(abs(at[q][3]) for q in at),
                        "sup_cell_R4": max(abs(at[q][4]) for q in at),
                        "D_mag_certified": float(T4.Fr(kill["m"][str(m)]["D_interval_mag"])),
                        "M_R2_certified": float(T4.Fr(kill["m"][str(m)]["M_R2"])),
                        "B_cover_ratio_certified": kill["B_cover_ratio"][str(m)]}
    # sup-norm (over states) third derivatives at e0 for the aux3 node form
    node3 = {}
    for r in range(5):
        v = {kk: F_nodes[kk][0][r] for kk in (-2, -1, 0, 1, 2)}
        node3[f"F:{r}"] = float(np.max(np.abs((v[2] - 2 * v[1] + 2 * v[-1] - v[-2]) / (2 * d ** 3))))
    for key in F_nodes[0][1]:
        v = {kk: F_nodes[kk][1][key] for kk in (-2, -1, 0, 1, 2)}
        node3[f"W:{key[0]},{key[1]}"] = float(np.max(np.abs((v[2] - 2 * v[1] + 2 * v[-1] - v[-2]) / (2 * d ** 3))))
    # norms over the parent cell
    lo, hi = e0 - rho, e0 + rho
    grid = np.linspace(lo, hi, 21)
    E = abs(hi) if abs(hi) > abs(lo) else abs(lo)
    kn = [max(integ_abs(he(i), -c + e, c + e) for e in grid) for i in range(6)]
    kz_exact = [max(integ_abs(np.poly1d([1.0, -e]) * he(i), -c + e, c + e) for e in grid) for i in range(5)]
    kz_cert = [kn[i + 1] + (i * kn[i - 1] if i else 0.0) + E * kn[i] for i in range(5)]
    w = np.linspace(-15, 15, 300001)
    s0 = [2 * float(np.max(np.abs(he(n)(w) * np.exp(-w * w / 2) / math.sqrt(2 * math.pi)))) for n in range(5)]
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-oracle.v1", "cell": CELL, "DIAGNOSTIC_ONLY": True,
           "geometry": {"e0": e0, "rho": rho, "C_upper": C, "fd_step": d, "E": E},
           "norms": {"k": kn, "kz_exact": kz_exact, "kz_certform": kz_cert, "sup_src0_deriv": s0},
           "true": true, "node_sup_third_derivative_e0": node3, "towers": {}, "cover": {}}
    for lab, kz in (("exact_norms", kz_exact), ("certform_norms", kz_cert)):
        Th, TS, TW, TF = towers(kn, kz, C, E, s0)
        out["towers"][lab] = {"F": {f"{r},{n}": TF[r, n] for r in range(5) for n in range(5)},
                              "W": {f"{rj[0]},{rj[1]},{n}": v for (rj, n), v in TW.items()},
                              "assembled_M_R4": {str(m): assemble_tower(TF, TW, m, 4) for m in MS},
                              "assembled_order": {str(m): [assemble_tower(TF, TW, m, n) for n in range(5)] for m in MS}}
    for m in MS:
        t = true[str(m)]
        Mmax = (0.05 - rho * t["D_mag_certified"]) / (rho * rho / 2)
        target = (Mmax - abs(t["R2_e0"])) / rho
        row = {"M_R2_max_for_ratio_1": Mmax, "target_Q": target}
        for lab, M4 in (("true_M_R4", t["sup_cell_R4"]), ("tower_exact", out["towers"]["exact_norms"]["assembled_M_R4"][str(m)]),
                        ("tower_certform", out["towers"]["certform_norms"]["assembled_M_R4"][str(m)])):
            Q = abs(t["R3_e0"]) + rho / 2 * M4
            M2 = abs(t["R2_e0"]) + rho * abs(t["R3_e0"]) + rho * rho / 2 * M4
            row[lab] = {"M_R4": M4, "Q": Q, "Q_over_target": Q / target, "M_R2_taylor": M2,
                        "B_cover_ratio": (rho * t["D_mag_certified"] + rho * rho / 2 * M2) / 0.05}
        row["ideal_true_sup_R2"] = {"B_cover_ratio": (rho * t["D_mag_certified"] + rho * rho / 2 * t["sup_cell_R2"]) / 0.05}
        out["cover"][str(m)] = row
    (NS / "evidence/phase34_oracle_c313.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for m in MS:
        t, r = true[str(m)], out["cover"][str(m)]
        print(f"m{m} R''(e0)={t['R2_e0']:.5g} R'''(e0)={t['R3_e0']:.5g} supR2={t['sup_cell_R2']:.5g} trueM_R4={t['sup_cell_R4']:.5g} "
              f"target={r['target_Q']:.4g} | " + " | ".join(f"{lab}: M4={r[lab]['M_R4']:.4g} Q={r[lab]['Q']:.4g} ratio={r[lab]['B_cover_ratio']:.4g}"
                                                         for lab in ("true_M_R4", "tower_exact", "tower_certform")))
    print("k", [round(x, 4) for x in kn], "kz_exact", [round(x, 4) for x in kz_exact], "kz_cert", [round(x, 4) for x in kz_cert])
    print("assembled tower orders m5 exact", [round(x, 3) for x in out["towers"]["exact_norms"]["assembled_order"]["5"]])


if __name__ == "__main__":
    main()
