"""Rigorous SR resolvent bound C = sup_{x,e} E_{x,e}[tau].

Implements exactly PROTOTYPE_PROTOCOL.md section 2.  The geometry (which grid
cells an image box covers) is FIXED across sweeps and is precomputed once; only
V_n changes, so each sweep is a max-plus reduction over precomputed indices.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

_R4 = Path(__file__).resolve().parents[1] / "compute_optimization_r4_xi_reformulation"
_PROOF = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
for _p in (_R4, _PROOF):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
from xi_kernel import sr_constants                              # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational  # noqa: E402

G_GRID, Z_PART, N_MAX, Q_TARGET = 64, 256, 4000, 0.5
SWEEP_INFLATE = 1.0 + 2.0 ** -40


def _sparse_table(V: np.ndarray, axis: int, levels: int):
    """ST[k] gives the max over 2^k consecutive entries along `axis`."""
    st = [V]
    for k in range(1, levels):
        prev, step = st[-1], 1 << (k - 1)
        sl_a = [slice(None)] * V.ndim
        sl_b = [slice(None)] * V.ndim
        sl_a[axis] = slice(0, V.shape[axis] - step)
        sl_b[axis] = slice(step, V.shape[axis])
        cur = np.full_like(V, -np.inf)
        sl_c = [slice(None)] * V.ndim
        sl_c[axis] = slice(0, V.shape[axis] - step)
        cur[tuple(sl_c)] = np.maximum(prev[tuple(sl_a)], prev[tuple(sl_b)])
        tail = [slice(None)] * V.ndim
        tail[axis] = slice(V.shape[axis] - step, V.shape[axis])
        cur[tuple(tail)] = prev[tuple(tail)]
        st.append(cur)
    return st


def _range_max(st, lo, hi, axis, levels):
    """Max over [lo, hi] inclusive, using the sparse table; O(1) per query."""
    length = hi - lo + 1
    k = np.minimum(np.floor(np.log2(np.maximum(length, 1))).astype(np.int64), levels - 1)
    out = np.full(lo.shape, -np.inf)
    for kk in range(levels):
        sel = k == kk
        if not sel.any():
            continue
        step = 1 << kk
        a = lo[sel]
        b = np.maximum(hi[sel] - step + 1, a)
        if axis == 0:
            out[sel] = np.maximum(st[kk][a, ...][np.arange(a.size), ...],
                                  st[kk][b, ...][np.arange(b.size), ...])
        else:
            raise NotImplementedError
    return out


def build_geometry(e_lo: str, e_hi: str, grid: int = G_GRID, zpart: int = Z_PART,
                   bits: int = 192):
    """Precompute the fixed cell-cover geometry and the Arb-rigorous z masses."""
    ctx.prec = bits
    A, b_SR, c_SR = sr_constants()
    b = float(b_SR.upper())            # outward: a slightly LARGER square is safe
    c = float(c_SR.lower())            # outward: a slightly NARROWER c_SR widens
    d = b / grid                       # cell side in y

    # z partition over [-c_SR, c_SR]
    zg = np.linspace(-float(c_SR.upper()), float(c_SR.upper()), zpart + 1)
    za, zb = zg[:-1], zg[1:]

    # Arb-rigorous upper bound on int_{za}^{zb} phi(z+e) dz, valid for ALL e in
    # the cell: evaluate with e as an interval ball and take the upper endpoint.
    en, ed = e_lo.split("/"), e_hi.split("/")
    elo = rational(int(en[0]), int(en[1]))
    ehi = rational(int(ed[0]), int(ed[1]))
    e_ball = (elo + ehi) / arb(2) + ((ehi - elo) / arb(2)) * arb(0, 1)
    # int_{za}^{zb} phi(z+e) dz has d/de = phi(zb+e) - phi(za+e), which vanishes
    # exactly at e* = -(za+zb)/2 and is a maximum there.  So the supremum over
    # the e-cell is attained at clip(e*, e_lo, e_hi) -- an EXACT, tight bound,
    # not an interval hull (whose sum over a partition exceeds 1 and would pin
    # the iteration at q = 1 forever).
    flo, fhi = float(elo.lower()), float(ehi.upper())
    mass = np.empty(zpart)
    for s in range(zpart):
        estar = min(max(-(za[s] + zb[s]) / 2.0, flo), fhi)
        eb = arb(estar) + arb(0, 2.0 ** -50)      # outward slack on the float e*
        m = gaussian_cdf(arb(zb[s]) + eb) - gaussian_cdf(arb(za[s]) + eb)
        mass[s] = max(float(m.upper()), 0.0)

    yp_lo = np.arange(grid) * d
    yp_hi = (np.arange(grid) + 1) * d

    def sp(x):
        return np.log1p(np.exp(np.clip(x, -700, 700)))

    def cells(v_lo, v_hi):
        a = np.clip(np.floor(v_lo / d).astype(np.int64) - 1, 0, grid - 1)
        bb = np.clip(np.ceil(v_hi / d).astype(np.int64) + 1, 0, grid - 1)
        return a, np.maximum(bb, a)

    # plus chart: yp' increasing in z and in yp   -> depends on (i, s)
    a1, b1 = cells(sp(yp_lo[:, None] + za[None, :] - 0.5),
                   sp(yp_hi[:, None] + zb[None, :] - 0.5))
    # minus chart: ym' decreasing in z, increasing in ym -> depends on (j, s)
    a2, b2 = cells(sp(yp_lo[:, None] - zb[None, :] - 0.5),
                   sp(yp_hi[:, None] - za[None, :] - 0.5))

    # live-region mask: include any sub-interval that MEETS (l_P, u_P), with its
    # full mass -- conservative for an upper bound on P(tau > n+1).
    u_P = c - yp_lo                      # depends on i (uses yp_lo: widest)
    l_P = yp_lo - c                      # depends on j
    live = (za[None, None, :] < u_P[:, None, None]) & (zb[None, None, :] > l_P[None, :, None])
    return {"A": A, "b_SR": b_SR, "c_SR": c_SR, "d": d, "grid": grid, "zpart": zpart,
            "mass": mass, "a1": a1, "b1": b1, "a2": a2, "b2": b2, "live": live,
            "e_ball": e_ball}


def resolvent_bound(geo, n_max: int = N_MAX, q_target: float = Q_TARGET,
                    progress_every: int = 0):
    """Value iteration -> (C, n_0, q, history).  C = n_0/(1-q)."""
    G, Z = geo["grid"], geo["zpart"]
    a1, b1, a2, b2 = geo["a1"], geo["b1"], geo["a2"], geo["b2"]
    mass, live = geo["mass"], geo["live"]
    lev = int(np.ceil(np.log2(G))) + 1
    wmass = (mass[None, None, :] * live)            # (G,G,Z) masses, zeroed off-live

    V = np.ones((G, G))
    hist = []
    for n in range(1, n_max + 1):
        # step 1: reduce over the minus-chart (column) range -> B[p, j, s]
        stq = _sparse_table(V, axis=1, levels=lev)
        lenq = b2 - a2 + 1                                    # (G,Z)
        kq = np.minimum(np.floor(np.log2(np.maximum(lenq, 1))).astype(np.int64), lev - 1)
        B = np.empty((G, G, Z))
        for kk in range(lev):
            sel = kq == kk
            if not sel.any():
                continue
            step = 1 << kk
            jj, ss = np.nonzero(sel)
            lo = a2[jj, ss]
            hi = np.maximum(b2[jj, ss] - step + 1, lo)
            B[:, jj, ss] = np.maximum(stq[kk][:, lo], stq[kk][:, hi])
        # step 2: reduce over the plus-chart (row) range -> W[i, j, s]
        stp = _sparse_table(B, axis=0, levels=lev)
        lenp = b1 - a1 + 1                                    # (G,Z)
        kp = np.minimum(np.floor(np.log2(np.maximum(lenp, 1))).astype(np.int64), lev - 1)
        W = np.empty((G, G, Z))
        for kk in range(lev):
            sel = kp == kk
            if not sel.any():
                continue
            step = 1 << kk
            ii, ss = np.nonzero(sel)
            lo = a1[ii, ss]
            hi = np.maximum(b1[ii, ss] - step + 1, lo)
            W[ii, :, ss] = np.maximum(stp[kk][lo, :, ss], stp[kk][hi, :, ss])
        Vn = (W * wmass).sum(axis=2) * SWEEP_INFLATE
        V = np.minimum(V, Vn)                                 # P(tau>n) non-increasing
        q = float(V.max())
        hist.append(q)
        if progress_every and n % progress_every == 0:
            print(f"    n={n:5d}  q={q:.6e}", flush=True)
        if q <= q_target:
            return n / (1.0 - q), n, q, hist
    return None, n_max, float(V.max()), hist
