"""Adjudicator's own crude Markov-chain (Brook-Evans style) float estimate of E_a[tau] (two-sided CUSUM, k=0.5, c=5.5,
state in [0,5)^2, X density phi(z+e)) and of tau_a = E_a[tau ^ T_a], D = 1 - p_e. Sanity only (not certified)."""
import sys, math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from scipy.special import ndtr
K, C, H = 0.5, 5.5, 5.0

def chain(e, N, NZ=4000):
    w = H / N
    grid = np.arange(N) * w                      # p = i*w (i=0 is the reset boundary)
    rows, cols, vals = [], [], []
    atom_w = np.zeros(N * N)
    for i, p in enumerate(grid):
        for j, m in enumerate(grid):
            if p > 0 and m > 0 and p + m > 4 + 1e-12:
                continue
            lo, hi = m - C, C - p
            # exact atom mass: z in [m-K, K-p]
            b, a = m - K, K - p
            am = max(0.0, ndtr(a + e) - ndtr(b + e)) if b < a else 0.0
            edges = np.linspace(lo, hi, NZ + 1)
            zc = 0.5 * (edges[1:] + edges[:-1])
            pw = ndtr(edges[1:] + e) - ndtr(edges[:-1] + e)
            if b < a:
                keep = (zc < b) | (zc > a)
                zc, pw = zc[keep], pw[keep]
            pn = np.maximum(0.0, p + zc - K); mn = np.maximum(0.0, m - zc - K)
            ii = np.minimum(N - 1, np.rint(pn / w).astype(int)); jj = np.minimum(N - 1, np.rint(mn / w).astype(int))
            src = i * N + j
            idx = ii * N + jj
            rows += [src] * len(idx); cols += list(idx); vals += list(pw)
            rows.append(src); cols.append(0); vals.append(am)
            atom_w[src] = am
    P = sp.csr_matrix((vals, (rows, cols)), shape=(N * N, N * N))
    return P, atom_w

def solve(e, N):
    P, ka = chain(e, N)
    I = sp.identity(N * N, format="csr")
    one = np.ones(N * N)
    arl = spl.spsolve((I - P).tocsc(), one)
    Ph = P.tolil(); Ph[:, 0] = Ph[:, 0].toarray().ravel() - ka[:, None].ravel() if False else Ph[:, 0]
    Ph = P.tocsr().copy()
    Ph = Ph - sp.csr_matrix((ka, (np.arange(N * N), np.zeros(N * N, int))), shape=(N * N, N * N))
    g = spl.spsolve((I - Ph).tocsc(), one)
    hvec = spl.spsolve((I - Ph).tocsc(), ka)
    return arl[0], g[0], 1 - hvec[0], g.max()

for e in [float(x) for x in sys.argv[1].split(",")]:
    for N in (50, 100):
        arl, tau, D, gmax = solve(e, N)
        print(f"e={e:.7f} N={N}: E_a[tau]={arl:.2f} tau_a={tau:.3f} D={D:.5f} tau_a/D={tau/D:.2f} max Ghat1={gmax:.2f}", flush=True)
