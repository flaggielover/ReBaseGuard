"""P5X R8: rigorous one-sided SR resolvent bound C_SR (B1).

Implements R8_BINDING_SPEC.md section 1 exactly.  The minus chart evolves
autonomously, so tau <= tau^- pathwise (B1-L1) and E_x[tau] <= E_{y^-}[tau^-].
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "compute_optimization_r4_xi_reformulation",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
from xi_kernel import sr_constants                                  # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational  # noqa: E402

G1, Z1, N_MAX, Q_TARGET, ZMAX, BITS = 1024, 1024, 4000, 0.5, 8, 256
SWEEP_INFLATE = 1.0 + 2.0 ** -40


def _masses(za, zb, e_lo, e_hi, zmax):
    """Arb upper bounds on int_{za}^{zb} phi(z+e) dz, valid for all e in cell.

    d/de of the integral is phi(zb+e) - phi(za+e), zero exactly at
    e* = -(za+zb)/2 and a maximum there, so the sup over the e-cell is at
    clip(e*, e_lo, e_hi).  Exact and tight -- not an interval hull.
    """
    out = np.empty(len(za))
    for s in range(len(za)):
        estar = min(max(-(za[s] + zb[s]) / 2.0, e_lo), e_hi)
        eb = arb(estar) + arb(0, 2.0 ** -50)
        m = gaussian_cdf(arb(zb[s]) + eb) - gaussian_cdf(arb(za[s]) + eb)
        out[s] = max(float(m.upper()), 0.0)
    tb = arb(e_hi) + arb(0, 2.0 ** -50)
    tail = float((arb(1) - gaussian_cdf(arb(zmax) + tb)).upper())
    return out, max(tail, 0.0)


def resolvent(e_lo: float, e_hi: float, grid=G1, zpart=Z1, n_max=N_MAX,
              q_target=Q_TARGET, zmax=ZMAX, bits=BITS):
    ctx.prec = bits
    A, b_SR, c_SR = sr_constants()
    b = float(b_SR.upper())
    c = float(c_SR.upper())
    d = b / grid
    ylo = np.arange(grid) * d
    yhi = ylo + d
    zg = np.linspace(-c, zmax, zpart + 1)
    za, zb = zg[:-1], zg[1:]
    mass, tail = _masses(za, zb, e_lo, e_hi, zmax)

    def sp(x):
        return np.log1p(np.exp(np.clip(x, -700, 700)))

    # y' = softplus(y - z - 1/2): increasing in y, decreasing in z.  Outward
    # cell-index rounding with a one-cell margin absorbs float error in sp().
    a_i = np.clip(np.floor(sp(ylo[:, None] - zb[None, :] - 0.5) / d).astype(np.int64) - 1, 0, grid - 1)
    b_i = np.clip(np.ceil(sp(yhi[:, None] - za[None, :] - 0.5) / d).astype(np.int64) + 1, 0, grid - 1)
    b_i = np.maximum(b_i, a_i)
    # tail z > zmax: y' in [0, softplus(y_hi - zmax - 1/2)]
    t_hi = np.clip(np.ceil(sp(yhi - zmax - 0.5) / d).astype(np.int64) + 1, 0, grid - 1)
    live = zb[None, :] > (ylo[:, None] - c)          # widest continuation per cell
    wm = mass[None, :] * live

    V = np.ones(grid)
    lev = int(np.ceil(np.log2(grid))) + 1
    for n in range(1, n_max + 1):
        st = [V]
        for k in range(1, lev):
            p = st[-1]
            s = 1 << (k - 1)
            cur = p.copy()
            cur[:grid - s] = np.maximum(p[:grid - s], p[s:])
            st.append(cur)
        ln = b_i - a_i + 1
        kk = np.minimum(np.floor(np.log2(np.maximum(ln, 1))).astype(np.int64), lev - 1)
        W = np.empty((grid, zpart))
        for q_ in range(lev):
            sel = kk == q_
            if not sel.any():
                continue
            s = 1 << q_
            ii, ss = np.nonzero(sel)
            lo = a_i[ii, ss]
            hi = np.maximum(b_i[ii, ss] - s + 1, lo)
            W[ii, ss] = np.maximum(st[q_][lo], st[q_][hi])
        tl = np.array([st[min(int(np.floor(np.log2(max(t + 1, 1)))), lev - 1)][0] for t in t_hi])
        tl = np.maximum(tl, np.array([V[:t + 1].max() for t in t_hi]))
        Vn = ((W * wm).sum(axis=1) + tail * tl) * SWEEP_INFLATE
        V = np.minimum(V, Vn)
        q = float(V.max())
        if q <= q_target:
            return {"C": n / (1.0 - q), "n0": n, "q": q, "grid": grid,
                    "zpart": zpart, "bits": bits, "converged": True}
    return {"C": None, "n0": n_max, "q": float(V.max()), "grid": grid,
            "zpart": zpart, "bits": bits, "converged": False}
