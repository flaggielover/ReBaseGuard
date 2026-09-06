"""EXPLORATORY (float, NOT a certificate) survival dynamic programme for SR.

Computes s_n(y) = P_y(tau > n) = (K_e^n 1)(y) on a grid, to locate an n where
q_n = sup_y s_n(y) drops materially below 1. Float arithmetic, bilinear
interpolation, Gauss-Legendre in z: every number produced here is an ESTIMATE
used only to choose n. The certified computation is sr_nstep.py.

Single-threaded and sized to run in a few seconds so it cannot compete with the
CUSUM campaign.
"""
from __future__ import annotations

import numpy as np

A = 4581762885148045 / 8796093022208
B_SR = np.log1p(A)
C_SR = np.log(A) + 0.5


def survival_ladder(e: float, G: int = 48, NZ: int = 40, nmax: int = 256):
    """Return (s_sup[n], cum_sup[n]) for n = 0..nmax, sup over the state grid."""
    yp = np.linspace(0.0, B_SR, G)
    ym = np.linspace(0.0, B_SR, G)
    YP, YM = np.meshgrid(yp, ym, indexing="ij")          # (G,G)
    lo = YM - C_SR                                        # l(y)
    hi = C_SR - YP                                        # u(y)
    gl_x, gl_w = np.polynomial.legendre.leggauss(NZ)
    mid = (lo + hi)[..., None] / 2.0
    half = (hi - lo)[..., None] / 2.0
    Z = mid + half * gl_x                                 # (G,G,NZ)
    W = half * gl_w
    dens = np.exp(-0.5 * (Z + e) ** 2) / np.sqrt(2 * np.pi)
    WD = W * dens                                         # quadrature weight x phi
    # successor states
    npl = np.logaddexp(0.0, YP[..., None] + Z - 0.5)
    nmi = np.logaddexp(0.0, YM[..., None] - Z - 0.5)
    npl = np.clip(npl, 0.0, B_SR)
    nmi = np.clip(nmi, 0.0, B_SR)
    # bilinear interpolation indices, precomputed once
    hgrid = B_SR / (G - 1)
    fi = np.clip(npl / hgrid, 0, G - 1 - 1e-12)
    fj = np.clip(nmi / hgrid, 0, G - 1 - 1e-12)
    i0 = fi.astype(np.int64); j0 = fj.astype(np.int64)
    ti = fi - i0; tj = fj - j0
    i1 = np.minimum(i0 + 1, G - 1); j1 = np.minimum(j0 + 1, G - 1)
    w00 = (1 - ti) * (1 - tj); w01 = (1 - ti) * tj
    w10 = ti * (1 - tj);       w11 = ti * tj

    s = np.ones((G, G))
    sup, cum = [1.0], [1.0]
    running = np.ones((G, G))
    for _ in range(1, nmax + 1):
        vals = (w00 * s[i0, j0] + w01 * s[i0, j1]
                + w10 * s[i1, j0] + w11 * s[i1, j1])
        s = np.sum(vals * WD, axis=-1)
        s = np.clip(s, 0.0, 1.0)
        running = running + s
        sup.append(float(s.max()))
        cum.append(float(running.max()))
    return np.array(sup), np.array(cum)


def table(e: float, ladder=(1, 2, 4, 8, 16, 32, 64, 128, 256), **kw):
    sup, cum = survival_ladder(e, nmax=max(ladder), **kw)
    rows = []
    for n in ladder:
        q = sup[n]
        # C_n <= ||sum_{j<n} K^j 1|| / (1 - q_n),  sum_{j<n} s_j = cum[n-1]
        Cn = cum[n - 1] / (1 - q) if q < 1 else float("inf")
        rows.append({"n": n, "q_n": q, "sum_j<n": cum[n - 1], "C_n": Cn})
    return rows


if __name__ == "__main__":
    import json
    import sys
    out = {}
    for e in (0.0, 0.25, 0.5, 1.0, 2.0):
        rows = table(e)
        out[f"e={e}"] = rows
        print(f"\n  e = {e}")
        print(f"    {'n':>5} {'q_n = sup P_y(tau>n)':>24} {'sum_j<n ||K^j 1||':>20} {'C_n':>14}")
        for r in rows:
            c = f"{r['C_n']:.4g}" if np.isfinite(r["C_n"]) else "inf"
            print(f"    {r['n']:>5} {r['q_n']:>24.12f} {r['sum_j<n']:>20.4f} {c:>14}")
    if len(sys.argv) > 1:
        open(sys.argv[1], "w").write(json.dumps(out, indent=1))
