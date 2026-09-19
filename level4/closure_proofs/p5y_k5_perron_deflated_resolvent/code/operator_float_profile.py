"""NON-CERTIFIED operator-only float profile of the atom-deflation constants on e in [0, 0.13] (FORECAST INPUT ONLY).

tau_a(e) = E_a[tau ^ T_a], C_T(e) = sup over reachable nodes of E_x[tau ^ T_a], D(e) = P_a(tau < T_a),
D'(e), D''(e) by central differences of D on the same grid. No source, no candidate, no R value.
"""
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import operator_float_diagnostic as OD  # noqa: E402


def taboo_data(e, deg):
    K, Kh, ka, nodes, n = OD.kernel_split(e, deg, quad=500)
    dim = n * n
    I = np.eye(dim)
    P, M = np.meshgrid(nodes, nodes, indexing="ij")
    P, M = P.ravel(), M.ravel()
    reach = (P <= 1e-12) | (M <= 1e-12) | (P + M <= 4 + 1e-12)
    tab = np.linalg.solve(I - Kh, np.ones(dim))
    h = np.linalg.solve(I - Kh, ka)
    return float(tab[0]), float(tab[reach].max()), 1.0 - float(h[0])


def main():
    deg = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    es = [float(x) for x in np.round(np.linspace(0.0, 0.13, 27), 6)]
    d = 2e-3
    rows = []
    for e in es:
        tau, ct, D0 = taboo_data(e, deg)
        Dp = taboo_data(e + d, deg)[2]
        Dm = taboo_data(abs(e - d), deg)[2]          # D is even in e
        rows.append({"e": e, "tau_a": tau, "C_T": ct, "D": D0,
                     "D1": (Dp - Dm) / (2 * d), "D2": (Dp - 2 * D0 + Dm) / d ** 2})
    json.dump({"schema": "rebaseguard.p5y.k5.perron-deflation.operator-float-profile.v1", "certified": False,
               "degree": deg, "use": "FORECAST INPUT ONLY (operator only)", "rows": rows}, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
