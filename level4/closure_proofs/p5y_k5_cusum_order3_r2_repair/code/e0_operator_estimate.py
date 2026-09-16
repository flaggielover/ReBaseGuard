"""NON-CERTIFIED float estimate of parity-restricted resolvent norms of the CUSUM kernel at drift e = 0.

FORECAST INPUT ONLY. Operator information only: it builds K_0 (weight phi) on the frozen collocation grid at drift 0.
No source term (h_1, S_0, reward), no DAG object, no candidate solve, no K1 record, and no R_(D,m) value of any order
is formed. Nothing here is certified; the certified odd-subspace resolvent bound is a separate, unbuilt operator
certificate (see ../R2_DESIGN.md section 5).

    sigma : (p, m) -> (m, p)   index (i, j) -> (j, i) on the tensor Chebyshev grid
    P_e = (I + S)/2, P_o = (I - S)/2
    reported: ||A^-1||_inf, ||A^-1 P_e||_inf, ||A^-1 P_o||_inf, A = I - K_0; top eigenvalues of K_0 on each parity
    subspace; the even-subspace norm after deflating the Perron mode; the commutation defect ||K S - S K||.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

K_FROZEN, H_FROZEN, C_CUSUM, DEGREE, QUAD = 0.5, 5.0, 5.5, 12, 400


def bary_rows(values, nodes, w):
    d = values[:, None] - nodes[None, :]
    exact = np.abs(d) < 2e-14
    d = np.where(exact, 1.0, d)
    t = w[None, :] / d
    t = t / t.sum(axis=1, keepdims=True)
    hit = exact.any(axis=1)
    if hit.any():
        t[hit] = exact[hit].astype(float)
    return t


def kernel_matrix(drift: float) -> np.ndarray:
    n = DEGREE + 1
    x = np.cos(np.pi * np.arange(n) / DEGREE)
    nodes = 0.5 * H_FROZEN * (1.0 - x)
    w = (-1.0) ** np.arange(n)
    w[[0, -1]] *= 0.5
    gn, gw = np.polynomial.legendre.leggauss(QUAD)
    K = np.zeros((n * n, n * n))
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            ell, upper = m - C_CUSUM, C_CUSUM - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            z = mid + rad * gn
            y = z + drift
            dens = rad * gw * np.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)
            wp = bary_rows(np.maximum(0.0, p + z - K_FROZEN), nodes, w)
            wm = bary_rows(np.maximum(0.0, m - z - K_FROZEN), nodes, w)
            K[i * n + j] = np.einsum("q,qa,qb->ab", dens, wp, wm).ravel()
    return K


def main():
    n = DEGREE + 1
    K = kernel_matrix(0.0)
    S = np.zeros_like(K)
    for i in range(n):
        for j in range(n):
            S[i * n + j, j * n + i] = 1.0
    I = np.eye(n * n)
    Pe, Po = (I + S) / 2, (I - S) / 2
    Ainv = np.linalg.inv(I - K)
    inf = lambda M: float(np.abs(M).sum(axis=1).max())
    ev = np.linalg.eigvals(K)
    # parity of eigenvectors
    vals, vecs = np.linalg.eig(K)
    order = np.argsort(-np.abs(vals))
    tops = []
    for idx in order[:8]:
        v = vecs[:, idx]
        par = float(np.linalg.norm(S @ v - v) / np.linalg.norm(v))
        tops.append({"eigenvalue": float(vals[idx].real), "imag": float(vals[idx].imag),
                     "parity": "even" if par < 1e-6 else ("odd" if abs(par - 2) < 1e-6 else f"mixed:{par:.3g}")})
    # Perron deflation on the even subspace
    lvals, lvecs = np.linalg.eig(K.T)
    li = int(np.argmax(lvals.real))
    ri = int(np.argmax(vals.real))
    psi, ell = np.real(vecs[:, ri]), np.real(lvecs[:, li])
    lam = float(vals[ri].real)
    proj = np.outer(psi, ell) / float(ell @ psi)
    defl = Ainv @ (I - proj) @ Pe
    out = {"schema": "rebaseguard.p5y.k5.order3-r2.e0-operator-estimate.v1", "certified": False,
           "use": "FORECAST INPUT ONLY", "drift": 0.0, "grid": "frozen degree-12 tensor Chebyshev, 400-node Gauss-Legendre",
           "commutation_defect_inf": inf(K @ S - S @ K), "norm_K_inf": inf(K),
           "resolvent_inf": inf(Ainv), "resolvent_even_inf": inf(Ainv @ Pe), "resolvent_odd_inf": inf(Ainv @ Po),
           "perron_eigenvalue": lam, "one_over_one_minus_perron": 1 / (1 - lam),
           "even_resolvent_after_perron_deflation_inf": inf(defl),
           "top_eigenvalues": tops}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
