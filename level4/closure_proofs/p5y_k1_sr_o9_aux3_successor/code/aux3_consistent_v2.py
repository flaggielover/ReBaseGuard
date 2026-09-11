"""Phase 3/4 decisive estimate v2 (NON-CERTIFYING). Supersedes the v1 'certlike' variant, whose multiplicative
cand-sup/true scaling blew up on the near-zero object F_4'' (ratio ~1e7) and is meaningless.

Self-consistent Taylor tower of order N (midpoint evidence at orders < N, whole-cell remainder of order N):
    a_n <= sum_{k=0}^{N-1-n} rho^k/k! m_{n+k} + rho^(N-n)/(N-n)! a_N           (n < N)
    h_1: a_N <= k_N;  h_j: a_N <= sum_i C(N,i) k_i a_{N-i}(h_{j-1});  S_r: a_N <= sum_i C(N,i) kz_i a_{N-i}(h_r)
    S_0: a_N <= 2 sup|He_N phi| + E a_N(h_1) + N a_{N-1}(h_1);  W: a_N <= sum_i C(N,i) k_i a_{N-i}(W_prev)
    F_r: a_N <= C (sum_{i>=1} C(N,i) k_i P_i + a_N(f_r)) / (1 - q_N),  q_N = C sum_{i>=1} C(N,i) k_i rho^i/i!
         (no bound when q_N >= 1)
    M_R2 <= sum_{k=0}^{N-3} rho^k/k! |R^(k+2)(x0,e0)| + rho^(N-2)/(N-2)! M_RN
N = 4 is exactly the order-3 auxiliary architecture of this round; N = 5, 6 would add order-4 (and order-5)
midpoint candidates. Midpoint derivatives: exact interpolation through 7 Nystrom solves at e0 + q*rho/4, q=-3..3.
Midpoint sup-norm variants: TRUE (ideal evidence) and CERT-ADDITIVE (orders <= 2 with a candidate: certified
candidate sup sum|c_ij| + certified eps_mid; other orders and image nodes: TRUE + that object's largest excess,
or the median excess when the object has no candidate).
"""
import json
import math
from math import comb
from pathlib import Path

import numpy as np
import sr_o9_candidates as T
import t4_cell as T4
import aux3_consistent as V1

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
CELL, MS, QS = 313, (1, 2, 3, 5), (-3, -2, -1, 0, 1, 2, 3)


def main():
    T.check_threads()
    orc = json.loads((NS / "evidence/phase34_oracle_c313.json").read_text())
    ext = json.loads((NS / "evidence/phase34_tower_ext_c313.json").read_text())
    geo = orc["geometry"]
    e0, rho, C, E, d = geo["e0"], geo["rho"], geo["C_upper"], geo["E"], geo["fd_step"]
    cell = T.frozen_cell(CELL)
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        b, c = T.nearest_double(g["b"]), T.nearest_double(g["c"])
    Vq = {q: V1.objs(b, c, e0 + q * d) for q in QS}
    A = np.array([[(q * d) ** p for p in range(len(QS))] for q in QS])
    Ainv = np.linalg.inv(A)

    def derivs(vals):
        X = np.array([vals[q] for q in QS])
        return [math.factorial(n) * (Ainv[n] @ X) for n in range(6)]
    true = {name: [float(np.max(np.abs(v))) for v in derivs({q: Vq[q][name] for q in QS})] for name in Vq[0]}
    Rd = {}
    for m in MS:
        def Rm(o, m=m):
            v = sum(o[f"F:{r}"][0] for r in range(m)) / m
            for t in range(1, m):
                for r in range(t):
                    key = f"S:{r}" if t - r - 1 == 0 else f"W:{r},{t-r-1}"
                    v += (1.0 / t - 1.0 / m) * o[key][0]
            return v
        Rd[m] = [float(x) for x in derivs({q: np.array(Rm(Vq[q])) for q in QS})]
    built = T.build_cell_candidates(CELL)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    kill = json.loads((CP / "p5y_k1_sr_o9_curvature_successor/evidence/kill/t4_c313.json").read_text())
    epsm = {k: float(T4.Fr(v)) for k, v in kill["eps_mid"].items()}
    excess, certv = {}, {}
    for name in true:
        for n in range(3):
            cn = f"{name}:k{n}"
            if cn in mant:
                v = float(T4.Fr(str(T4.mag_fraction(T4.cand_sup(mant[cn]))))) + epsm.get(cn, 0.0)
                certv[name, n] = v
                excess[name] = max(excess.get(name, 0.0), v - true[name][n])
    med = float(np.median(list(excess.values())))
    cert = {name: [certv.get((name, n), true[name][n] + excess.get(name, med)) for n in range(6)] for name in true}
    kn, kze, s0 = ext["norms_to_order"]["k"], ext["norms_to_order"]["kz_exact"], ext["norms_to_order"]["src0"]
    kzc = [kn[i + 1] + (i * kn[i - 1] if i else 0.0) + E * kn[i] for i in range(len(kn) - 1)]

    def run(mids, kz, NN):
        def taylor(mm, aN):
            return [sum(rho ** q / math.factorial(q) * mm[n + q] for q in range(NN - n))
                    + rho ** (NN - n) / math.factorial(NN - n) * aN for n in range(NN)] + [aN]
        a = {"h:1": taylor(mids["h:1"], kn[NN])}
        for j in range(2, 5):
            p = a[f"h:{j-1}"]
            a[f"h:{j}"] = taylor(mids[f"h:{j}"], sum(comb(NN, i) * kn[i] * p[NN - i] for i in range(NN + 1)))
        a["S:0"] = taylor(mids["S:0"], s0[NN] + E * a["h:1"][NN] + NN * a["h:1"][NN - 1])
        for r in range(1, 5):
            p = a[f"h:{r}"]
            a[f"S:{r}"] = taylor(mids[f"S:{r}"], sum(comb(NN, i) * kz[i] * p[NN - i] for i in range(NN + 1)))
        for r in range(4):
            for j in range(1, 4 - r):
                p = a[f"S:{r}"] if j == 1 else a[f"W:{r},{j-1}"]
                a[f"W:{r},{j}"] = taylor(mids[f"W:{r},{j}"], sum(comb(NN, i) * kn[i] * p[NN - i] for i in range(NN + 1)))
        qN = C * sum(comb(NN, i) * kn[i] * rho ** i / math.factorial(i) for i in range(1, NN + 1))
        out = {"contraction_qN": qN}
        if qN >= 1:
            out["no_bound"] = "resolvent self-consistency fails (q_N >= 1)"
            return out
        for r in range(5):
            fN = s0[NN] if r == 0 else a[f"S:{r}"][NN] + E * a["h:1"][NN] + NN * a["h:1"][NN - 1]
            mm = mids[f"F:{r}"]
            P = {i: sum(rho ** q / math.factorial(q) * mm[NN - i + q] for q in range(i)) for i in range(1, NN + 1)}
            aN = C * (sum(comb(NN, i) * kn[i] * P[i] for i in range(1, NN + 1)) + fN) / (1 - qN)
            a[f"F:{r}"] = taylor(mm, aN)
        for m in MS:
            MN = sum(a[f"F:{r}"][NN] for r in range(m)) / m
            for t in range(1, m):
                for r in range(t):
                    MN += (1.0 / t - 1.0 / m) * (a[f"S:{r}"][NN] if t - r - 1 == 0 else a[f"W:{r},{t-r-1}"][NN])
            mid = sum(rho ** q / math.factorial(q) * abs(Rd[m][q + 2]) for q in range(NN - 2))
            M2 = mid + rho ** (NN - 2) / math.factorial(NN - 2) * MN
            Dm = orc["true"][str(m)]["D_mag_certified"]
            out[str(m)] = {"M_RN": MN, "M_R2_bound": M2, "M_R2_max": orc["cover"][str(m)]["M_R2_max_for_ratio_1"],
                           "B_cover_ratio": (rho * Dm + rho * rho / 2 * M2) / 0.05}
        return out

    res = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-consistent.v2", "cell": CELL, "DIAGNOSTIC_ONLY": True,
           "supersedes": "aux3_consistent.py certlike variant (multiplicative scaling artifact)",
           "R_derivs_x0_e0": {str(m): Rd[m] for m in MS}, "midpoint_true": true, "midpoint_cert_additive": cert,
           "median_excess": med, "variants": {}}
    for ml, mids in (("true_midpoint", true), ("cert_additive_midpoint", cert)):
        for kl, kz in (("kz_exact", kze), ("kz_certform", kzc)):
            for NN in (4, 5, 6):
                res["variants"][f"N{NN}/{ml}/{kl}"] = run(mids, kz, NN)
    (NS / "evidence/phase34_consistent_v2_c313.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print("R derivs m5 (orders 0..5):", [round(x, 5) for x in Rd[5]], "median excess", round(med, 6))
    for lab, v in res["variants"].items():
        if "no_bound" in v:
            print(f"{lab:40s} q={v['contraction_qN']:.3f} NO BOUND")
        else:
            print(f"{lab:40s} q={v['contraction_qN']:.3f} " + " | ".join(
                f"m{m}: M_RN={v[str(m)]['M_RN']:.4g} ratio={v[str(m)]['B_cover_ratio']:.3g}" for m in MS))


if __name__ == "__main__":
    main()
