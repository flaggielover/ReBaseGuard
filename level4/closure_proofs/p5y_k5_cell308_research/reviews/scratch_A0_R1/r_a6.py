"""reviewA0 A6: independent NON-RIGOROUS estimate of Lambda(e) = E_a[tau] at one declared drift, by my own code:
  (i)  P1 Nystrom (node collocation, product integration of the P1 interpolant against phi, float), Jacobi value
       iteration to a 1e-14 update, meshes N in NLIST, Richardson O(h^2) and three-mesh ratios;
  (ii) plain Monte Carlo of the chain (random.Random(seed).gauss), with its standard error.
Compares with the A0 ladder's exact U and L at that drift (results/LADDER_e<E>_detA.json).  Writes only relative
positions and z-scores:  python3 -I -B r_a6.py E NLIST NMC
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction as F
from operator import mul
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r_common as R  # noqa: E402
from r_eval import dPhi, lin_int, K, H, C  # noqa: E402  (my own primitives)


def weights(N, base):
    """segment weights for u in [0, h] against phi(base + d h + u): (A_d, B_d) = int (1-u/h) phi, int (u/h) phi."""
    h = 1.0 / N
    D = 5 * N + 3
    WA, WB = {}, {}
    for d in range(-D, D + 1):
        t0 = base + d * h
        tot = lin_int(0.0, h, 1.0, 1.0, t0)          # int phi
        sec = lin_int(0.0, h, 0.0, 1.0, t0)          # int (u/h) phi
        WA[d], WB[d] = tot - sec, sec
    return WA, WB


def nystrom(N, e, tol=1e-14, maxit=5000):
    h = 1.0 / N
    n5 = 5 * N
    cols = [n5 + 1] + [4 * N - i + 1 for i in range(1, 4 * N + 1)] + [1] * N
    A3, B3 = weights(N, K + e)        # p-axis and interior: phi(p' - p + K + e), d = k - i
    A2, B2 = weights(N, K - e)        # m-axis: phi(m' - m + K - e), d = k - j
    D = 5 * N + 3
    # contiguous arrays indexed by d + D
    A3l = [A3[d] for d in range(-D, D + 1)]
    B3l = [B3[d] for d in range(-D, D + 1)]
    atom = {}
    for i in range(N):
        for j in range(N - i):
            atom[(i, j)] = dPhi(j * h - K + e, K - i * h + e)
    V = [[0.0] * c for c in cols]
    it = 0
    while True:
        it += 1
        f = [V[k][0] for k in range(n5 + 1)]
        g = [V[0][k] for k in range(n5 + 1)]
        S3 = []
        for i in range(n5 + 1):
            suf = [0.0] * (n5 + 1)
            acc = 0.0
            for k in range(n5 - 1, -1, -1):
                acc += f[k] * A3[k - i] + f[k + 1] * B3[k - i]
                suf[k] = acc
            S3.append(suf)
        S2 = []
        for j in range(n5 + 1):
            suf = [0.0] * (n5 + 1)
            acc = 0.0
            for k in range(n5 - 1, -1, -1):
                acc += g[k] * A2[k - j] + g[k + 1] * B2[k - j]
                suf[k] = acc
            S2.append(suf)
        diag = {}
        Vn = [[0.0] * c for c in cols]
        delta = 0.0
        for i in range(len(cols)):
            for j in range(cols[i]):
                n = i + j
                lo = max(0, n - N)
                v = 1.0 + S3[i][lo] + S2[j][lo]
                if n > N:
                    q = n - N
                    if q not in diag:
                        diag[q] = [V[k][q - k] for k in range(q + 1)]
                    a = diag[q]
                    o = -i + D                      # index of d = k - i at k = 0
                    v += sum(map(mul, a[:q], A3l[o:o + q])) + sum(map(mul, a[1:q + 1], B3l[o:o + q]))
                elif n < N:
                    v += atom[(i, j)] * V[0][0]
                Vn[i][j] = v
                dv = abs(v - V[i][j])
                if dv > delta:
                    delta = dv
        V = Vn
        if delta < tol * max(1.0, abs(V[0][0])) or it >= maxit:
            break
    return V[0][0], it, delta


def mc(e, n, seed):
    rng = random.Random(seed)
    gauss = rng.gauss
    s1 = s2 = 0.0
    for _ in range(n):
        p = m = 0.0
        t = 0
        while True:
            t += 1
            z = gauss(0.0, 1.0) - e
            if z > C - p or z < m - C:
                break
            p, m = max(0.0, p + z - K), max(0.0, m - z - K)
        s1 += t
        s2 += t * t
    mean = s1 / n
    var = (s2 - n * mean * mean) / (n - 1)
    return mean, math.sqrt(var / n)


def main(e_s, Nlist, nmc):
    e = R.rv_drift(e_s)
    tg = f"{e.numerator}" if e.denominator == 1 else f"{e.numerator}_{e.denominator}"
    lf = R.A0 / "results" / f"LADDER_e{tg}_detA.json"
    if lf.exists():
        lad = json.loads(lf.read_text())
        U, L = F(lad["U"]), F(lad["L"])
    else:                                   # no ladder run at this drift: the study's deciding rung (C2BX N=80)
        rec = json.loads((R.A0 / "results" / f"C2BX_e{tg}_N80.json").read_text())["rung"]
        U, L = F(rec["U"]), F(rec["L"])
    t0 = time.time()
    vals = {}
    for N in Nlist:
        t1 = time.time()
        lam, it, dl = nystrom(N, float(e))
        vals[N] = lam
        print(f"N={N} iters={it} last_delta={dl:.1e} secs={time.time() - t1:.1f}", flush=True)
    Ns = sorted(vals)
    rich = {f"{Ns[k]}-{Ns[k + 1]}": vals[Ns[k + 1]] + (vals[Ns[k + 1]] - vals[Ns[k]]) / 3 for k in range(len(Ns) - 1)}
    ratios = {f"{Ns[k]}/{Ns[k + 1]}/{Ns[k + 2]}": (vals[Ns[k + 1]] - vals[Ns[k]]) / (vals[Ns[k + 2]] - vals[Ns[k + 1]])
              for k in range(len(Ns) - 2)}
    best_key = list(rich)[-1]
    est = rich[best_key]
    # second-level Richardson (h^4) when three meshes are available, as an error indicator for the h^2 value
    est4 = None
    if len(Ns) >= 3:
        r1, r2 = rich[f"{Ns[-3]}-{Ns[-2]}"], rich[f"{Ns[-2]}-{Ns[-1]}"]
        est4 = r2 + (r2 - r1) / 15
    Uf, Lf = float(U), float(L)
    out = {"drift_declared": True, "meshes": Ns, "three_mesh_ratios": ratios,
           "richardson_keys": list(rich), "rel_change_last_two_richardson":
               (abs(rich[list(rich)[-1]] - rich[list(rich)[-2]]) / est) if len(rich) > 1 else None,
           "rel_h4_minus_h2": (abs(est4 - est) / est) if est4 else None,
           "U_minus_est_over_est": (Uf - est) / est, "est_minus_L_over_est": (est - Lf) / est,
           "L_le_est_le_U": Lf <= est <= Uf}
    if est4:
        out.update({"U_minus_est4_over_est": (Uf - est4) / est4, "est4_minus_L_over_est": (est4 - Lf) / est4})
    if nmc:
        t1 = time.time()
        mean, se = mc(float(e), nmc, 20260929)
        out["mc"] = {"n": nmc, "seed": 20260929, "rel_se": se / mean, "z_vs_est": (mean - est) / se,
                     "z_U": (Uf - mean) / se, "z_L": (mean - Lf) / se, "secs": round(time.time() - t1, 1)}
    out["wall_seconds"] = round(time.time() - t0, 1)
    R.dump(f"t_a6_e{tg}.json", out)
    R.rv_log("r_a6.py", f"REVIEW_A0_CERTIFIER_R1 A6: independent non-rigorous estimate (own P1 Nystrom N={Ns}, "
             f"Richardson; own MC n={nmc}) at declared drift e={e}; compared with A0 ladder U, L",
             notes="relative positions only are recorded; latent proxy stays in reviews/scratch_A0_R1")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], [int(x) for x in sys.argv[2].split(",")], int(sys.argv[3]))
