"""HO-10 evidence: the frozen J/h Leibniz tower against the exact h_j^(n), S_r^(n) on FX_B score walks (exact).

Tower (THEOREM_TC P3 / THEOREM_TCT P3'):  T[1][n] = ||h_1^(n)|| (exact here), T[j][0] = 1,
    T[j][n] = sum_i C(n,i) k_i T[j-1][n-i],   sigma_n(r) = sum_i C(n,i) j_i T[r][n-i],
with k_i = ||K_i(e0)||, j_i = ||J_i(e0)|| (point norms).  Reports tower / true for j, r = 1..4, n = 1..4.
Negative control: the recursion with the binomial weights dropped (C(n,i) -> 1) must fall below the truth somewhere.
Cells: FX_B N in {4, 8, 12}, e0 in {0, 1/4} (declared FX_B rule).  Writes NS/validation/B307_TOWER_FIXTURE.json.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b307_lib as L  # noqa: E402
from b307_lib import X, Q, NS  # noqa: E402

Q.install_import_guard()


def jkernel(N):
    p = {+1: [F(1, 3), L.SCORE_C / 3, L.SCORE_D / 3, L.SCORE_C3 / 3], -1: [F(1, 3), -L.SCORE_C / 3, L.SCORE_D / 3, -L.SCORE_C3 / 3],
         0: [F(1, 3), F(0), -2 * L.SCORE_D / 3, F(0)]}
    n = N + 1
    jp = [[[F(0)] for _ in range(n)] for _ in range(n)]
    for x in range(n):
        for z, pz in p.items():
            if x + z <= N:
                jp[x][max(0, x + z)] = L.poly_add(jp[x][max(0, x + z)], L.poly_scale(pz, F(z)))
    return jp


def main():
    rows, nc_det, nc_tot = [], 0, 0
    for N in (4, 8, 12):
        kp, srcs, hs = L.score_walk(N)
        jp = jkernel(N)
        for e0 in (F(0), F(1, 4)):
            Q.guard_drift(e0)
            fam = X.DriftFamily(kp, [[F(0)]] * (N + 1), (e0, e0))
            famJ = X.DriftFamily(jp, [[F(0)]] * (N + 1), (e0, e0))
            k = [X.op_norm(fam.K(e0, i)) for i in range(5)]
            jn = [X.op_norm(famJ.K(e0, i)) for i in range(5)]
            ev = lambda vp, nn: [X.poly_eval(X.poly_deriv(list(q), nn), e0) for q in vp]  # noqa: E731
            true_h = {j: [X.sup_norm(ev(hs[j], nn)) for nn in range(5)] for j in range(1, 5)}
            true_S = {r: [X.sup_norm(ev(srcs[r], nn)) for nn in range(5)] for r in range(1, 5)}
            T = {1: [F(1)] + true_h[1][1:]}
            Tbad = {1: list(T[1])}
            for j in range(2, 5):
                T[j] = [F(1)] + [sum((comb(nn, i) * k[i] * T[j - 1][nn - i] for i in range(nn + 1)), F(0)) for nn in range(1, 5)]
                Tbad[j] = [F(1)] + [sum((k[i] * Tbad[j - 1][nn - i] for i in range(nn + 1)), F(0)) for nn in range(1, 5)]
            for j in range(1, 5):
                for nn in range(1, 5):
                    ok = T[j][nn] >= true_h[j][nn]
                    rows.append({"N": N, "e0": str(e0), "object": f"h_{j}", "n": nn, "true": float(true_h[j][nn]),
                                 "tower": float(T[j][nn]), "ratio": float(T[j][nn] / true_h[j][nn]) if true_h[j][nn] else None,
                                 "sound": ok})
                    if j >= 2 and nn >= 2:
                        nc_tot += 1
                        nc_det += int(Tbad[j][nn] < true_h[j][nn])
            for r in range(1, 5):
                for nn in range(1, 5):
                    sig = sum((comb(nn, i) * jn[i] * T[r][nn - i] for i in range(nn + 1)), F(0))
                    rows.append({"N": N, "e0": str(e0), "object": f"S_{r}", "n": nn, "true": float(true_S[r][nn]),
                                 "tower": float(sig), "ratio": float(sig / true_S[r][nn]) if true_S[r][nn] else None,
                                 "sound": sig >= true_S[r][nn]})
    sound = all(r["sound"] for r in rows)
    summ = {}
    for obj in ("h_2", "h_3", "h_4", "S_1", "S_2", "S_3", "S_4"):
        for nn in (3, 4):
            v = [r["ratio"] for r in rows if r["object"] == obj and r["n"] == nn and r["ratio"] is not None]
            summ[f"{obj}^({nn})"] = {"min": min(v), "max": max(v)} if v else None
    out = {"schema": "P5Y_K5_TAIL_OVERNIGHT_B307_TOWER_FIXTURE/1", "producer": "streams/B_307/code/b307_tower_fixture.py",
           "class": "SYNTHETIC_VALIDATION", "all_sound": sound,
           "negative_control_binomials_dropped": {"detected": nc_det, "of": nc_tot},
           "tower_over_true": summ, "rows": rows}
    with open(NS / "validation" / "B307_TOWER_FIXTURE.json", "w") as fh:
        json.dump(out, fh, indent=1)
    Q.log_execution("streams/B_307/code/b307_tower_fixture.py", "B307 HO-10: J/h tower vs exact on FX_B score walks",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION", notes=f"sound={sound} NC {nc_det}/{nc_tot}")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
