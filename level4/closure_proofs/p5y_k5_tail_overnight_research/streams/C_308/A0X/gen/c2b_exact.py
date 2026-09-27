"""C2b exact certifier for P1 (piecewise-linear) supersolutions on the uniform anti-diagonal triangulation.

WHAT IS PROVED (for a nodal vector W >= 0, mesh h = 1/N, drift block E = [e_lo, e_hi], e_hi - e_lo in h*Z):
  let w = I_h W (P1 interpolant on the cells below).  If for every cell T and every e-slab S of E
        min_{vertices v of T x S} [ w(v) - 1 - (K_e w)(v)_upper ]  >=  err(T, S)
  then w >= 1 + K_e w on R for every e in E (kernel='whole'), hence E_x[tau] <= w(x); with kernel='taboo' the same
  with Khat_e, hence (Ghat_e 1)(x) <= w(x) and ||Ghat_e|| <= max W.

INGREDIENTS
  (1) Drift-position lemma: (K_e w)(p,m) = Psi_w(s, y), s = p+m, y = p-K-e.  Every Gaussian argument that occurs at
      a vertex of a lattice-aligned slab is on one of two lattices  t = K+e_lo+d h  or  t = K-e_lo+d h.
  (2) Vertex values: exact finite sums  W_k * (segment weight)  with rigorous interval weights built from c7
      enclosures of Phi and phi at lattice points, held as integers at scale 2^-P_BITS (no rounding in the sums).
  (3) Interpolation error: on a cell, w is affine, so w - 1 - I(Psi) is affine on each simplex of the P1 split of
      T x S and its minimum is at vertices; |Psi - I Psi| <= (r_s^2 |Psi_ss| + 2 r_s r_y |Psi_sy| + r_y^2 |Psi_yy|)/8
      (variance bound sum_i lambda_i d_i^2 <= range^2/4), with closed-form bounds on the second derivatives of
      Psi_w for P1 w derived in STRATEGY.md s5 (integration by parts; jump sums over P1 kinks).
"""
from __future__ import annotations

from fractions import Fraction as F

import c2b_common as CM

K, H = CM.K, CM.H
P = CM.P_BITS
ONE = CM.ONE_P


# ------------------------------------------------------------------------------------------------ geometry
class Mesh:
    def __init__(self, N: int):
        self.N = N
        self.h = F(1, N)
        self.cols = [5 * N + 1] + [4 * N - i + 1 for i in range(1, 4 * N + 1)] + [1] * N
        self.nodes = [(i, j) for i in range(5 * N + 1) for j in range(self.cols[i])]

    def has(self, i, j):
        return 0 <= i <= 5 * self.N and 0 <= j < self.cols[i]

    def cells(self):
        """(kind, i, j, n_s, i_lo, i_hi, j_lo, j_hi, vertices)."""
        N = self.N
        out = []
        for i in range(4 * N):
            for j in range(4 * N - i):
                out.append(("L", i, j, i + j, i, i + 1, j, j + 1, ((i, j), (i + 1, j), (i, j + 1))))
                if i + j + 2 <= 4 * N:
                    out.append(("U", i, j, i + j + 1, i, i + 1, j, j + 1,
                                ((i + 1, j), (i, j + 1), (i + 1, j + 1))))
        for i in range(4 * N, 5 * N):
            out.append(("AXP", i, 0, i, i, i + 1, 0, 0, ((i, 0), (i + 1, 0))))
        for j in range(4 * N, 5 * N):
            out.append(("AXM", 0, j, j, 0, 0, j, j + 1, ((0, j), (0, j + 1))))
        return out


# ------------------------------------------------------------------------------------------------ lattices
class Setup:
    """Mesh + both Gaussian lattices for a drift block [e_lo, e_lo + J h]."""

    def __init__(self, N: int, e_lo, e_hi=None):
        e_lo = F(e_lo)
        e_hi = e_lo if e_hi is None else F(e_hi)
        CM.guard(e_lo, e_hi)
        self.mesh = Mesh(N)
        self.N, self.h, self.e_lo, self.e_hi = N, F(1, N), e_lo, e_hi
        J = (e_hi - e_lo) * N
        if J.denominator != 1 or J < 0:
            raise ValueError("block width must be a non-negative multiple of h")
        self.J = int(J)
        D = 5 * N + self.J + 3
        self.Lp = CM.Lattice(K + e_lo, self.h, -D, D)
        self.Lm = CM.Lattice(K - e_lo, self.h, -D, D)
        self.phi0_hi = CM.ceil_scaled(CM.phi_iv(F(0)).hi)
        self.phi1_hi = CM.ceil_scaled(CM.phi_iv(F(1)).hi)
        self.Wp = self._seg(self.Lp, -D, D - 1)
        self.Wm = self._seg(self.Lm, -D, D - 1)
        self.tphi_p = self._tphi(self.Lp)
        self.tphi_m = self._tphi(self.Lm)

    def _seg(self, L, d0, d1):
        """rigorous (A_lo, A_hi, B_lo, B_hi) per segment d, scale 2^-P; A, B >= 0 mathematically."""
        N = self.N
        out = {}
        for d in range(d0, d1 + 1):
            M0lo = L.Phi_lo[d + 1] - L.Phi_hi[d]
            M0hi = L.Phi_hi[d + 1] - L.Phi_lo[d]
            M1lo = L.phi_lo[d] - L.phi_hi[d + 1]
            M1hi = L.phi_hi[d] - L.phi_lo[d + 1]
            t0, t1 = L.t(d), L.t(d + 1)
            # A = N (t1 M0 - M1),  B = N (M1 - t0 M0)
            c1 = sorted((t1 * M0lo, t1 * M0hi))
            c0 = sorted((t0 * M0lo, t0 * M0hi))
            Alo = N * (c1[0] - M1hi)
            Ahi = N * (c1[1] - M1lo)
            Blo = N * (M1lo - c0[1])
            Bhi = N * (M1hi - c0[0])
            out[d] = (max(0, _fl(Alo)), _ce(Ahi), max(0, _fl(Blo)), _ce(Bhi))
        return out

    def _tphi(self, L):
        return {d: _ce(abs(L.t(d)) * L.phi_hi[d]) for d in L.phi_hi}

    # upper bounds of phi and |t| phi on lattice-aligned intervals [t_d1, t_d2]
    def phimax(self, L, d1, d2):
        t1, t2 = L.t(d1), L.t(d2)
        if t1 <= 0 <= t2:
            return self.phi0_hi
        return L.phi_hi[d1] if t1 > 0 else L.phi_hi[d2]

    def tphimax(self, L, tp, d1, d2):
        t1, t2 = L.t(d1), L.t(d2)
        if (t1 <= 1 <= t2) or (t1 <= -1 <= t2):
            return self.phi1_hi
        return max(tp[d1], tp[d2])


def _fl(x: F) -> int:
    return x.numerator // x.denominator if isinstance(x, F) else int(x)


def _ce(x: F) -> int:
    return -((-x.numerator) // x.denominator) if isinstance(x, F) else int(x)


# ------------------------------------------------------------------------------------------------ vertex values
def kernel_nodes(S: Setup, Wint, jj: int, full: bool, upper: bool = True):
    """Rigorous bound (upper if upper else lower) of (K_e w)(node) at e = e_lo + jj h for all nodes; w = Wint * 2^-Q.
    Returned integers are at scale 2^-(P+Q) (same Q as Wint)."""
    N, mesh = S.N, S.mesh
    n5 = 5 * N

    def pick(Wv, lo, hi):
        if upper:
            return hi if Wv >= 0 else lo
        return lo if Wv >= 0 else hi

    Wp, Wm, Lp, Lm = S.Wp, S.Wm, S.Lp, S.Lm
    a = [Wint[k][0] for k in range(n5 + 1)]
    b = [Wint[0][k] for k in range(n5 + 1)]

    def suffix(vals, W, shift):
        suf = [0] * (n5 + 1)
        acc = 0
        for k in range(n5 - 1, -1, -1):
            Alo, Ahi, Blo, Bhi = W[k - shift]
            acc += vals[k] * pick(vals[k], Alo, Ahi) + vals[k + 1] * pick(vals[k + 1], Blo, Bhi)
            suf[k] = acc
        return suf

    S3 = {i: suffix(a, Wp, i - jj) for i in range(n5 + 1)}
    S2 = {j: suffix(b, Wm, j + jj) for j in range(n5 + 1)}
    w0 = Wint[0][0]
    out = {}
    for (i, j) in mesh.nodes:
        n = i + j
        A = max(0, n - N)
        v = S3[i][A] + S2[j][A]
        if n > N:
            q = n - N
            sh = i - jj
            acc = 0
            for k in range(q):
                Alo, Ahi, Blo, Bhi = Wp[k - sh]
                x0, x1 = Wint[k][q - k], Wint[k + 1][q - k - 1]
                acc += x0 * pick(x0, Alo, Ahi) + x1 * pick(x1, Blo, Bhi)
            v += acc
        elif n < N and full:
            # atom window mass Phi(K + e - p) - 1 + Phi(K - e - m)
            dp, dm = jj - i, -j - jj
            klo = Lp.Phi_lo[dp] + Lm.Phi_lo[dm] - ONE
            khi = Lp.Phi_hi[dp] + Lm.Phi_hi[dm] - ONE
            klo = max(0, klo)
            v += w0 * pick(w0, klo, khi)
        out[(i, j)] = v
    return out


def margins(S: Setup, Wint, Q: int, full: bool):
    """Lower bounds (scale 2^-(P+Q)) of w - 1 - K_e w at every node, for every e-offset jj = 0..J."""
    one = 1 << (P + Q)
    res = {}
    for jj in range(S.J + 1):
        Kw = kernel_nodes(S, Wint, jj, full, upper=True)
        res[jj] = {x: (Wint[x[0]][x[1]] << P) - one - Kw[x] for x in Kw}
    return res


# ------------------------------------------------------------------------------------------------ Hessian bounds
class _PM:
    """Fast upper bounds of phi and |t|phi on lattice-aligned index ranges [d1, d2] (precomputed signs)."""

    def __init__(self, S, L, tp):
        self.phi = L.phi_hi
        self.tp = tp
        self.phi0, self.phi1 = S.phi0_hi, S.phi1_hi
        self.sg = {d: (1 if L.t(d) > 0 else (-1 if L.t(d) < 0 else 0)) for d in L.phi_hi}
        self.s1 = {d: (1 if L.t(d) > 1 else (-1 if L.t(d) < 1 else 0)) for d in L.phi_hi}
        self.sm1 = {d: (1 if L.t(d) > -1 else (-1 if L.t(d) < -1 else 0)) for d in L.phi_hi}

    def pm(self, d1, d2):
        if self.sg[d1] <= 0 <= self.sg[d2]:
            return self.phi0
        return self.phi[d1] if self.sg[d1] > 0 else self.phi[d2]

    def tpm(self, d1, d2):
        if (self.s1[d1] <= 0 <= self.s1[d2]) or (self.sm1[d1] <= 0 <= self.sm1[d2]):
            return self.phi1
        return max(self.tp[d1], self.tp[d2])


def hessian_bounds(S: Setup, Wint, full: bool):
    """For every cell and e-slab: upper bounds (Hss, Hsy, Hyy) of |Psi_ss|, |Psi_sy|, |Psi_yy| over the cell's
    (s, y) rectangle, as integers at scale 2^-(P+Q), and err = ceil((Hss + 2 ry Hsy + ry^2 Hyy)/(8 N^2)).
    Derivation: STRATEGY.md s5 (integration by parts against the P1 kinks)."""
    N, mesh = S.N, S.mesh
    n5 = 5 * N
    Pp, Pm = _PM(S, S.Lp, S.tphi_p), _PM(S, S.Lm, S.tphi_m)
    W = Wint
    a = [W[k][0] for k in range(n5 + 1)]
    b = [W[0][k] for k in range(n5 + 1)]
    sa = [(a[k + 1] - a[k]) * N for k in range(n5)]
    sb = [(b[k + 1] - b[k]) * N for k in range(n5)]
    da = [0] + [abs(sa[k] - sa[k - 1]) for k in range(1, n5)]      # da[k] = |jump of a' at node k|
    db = [0] + [abs(sb[k] - sb[k - 1]) for k in range(1, n5)]
    aH, bH, w0 = abs(a[n5]), abs(b[n5]), abs(W[0][0])

    # suffix sums  SA[(off, wd)][k0] = sum_{k>=k0, k<=n5-1} da[k] * pm(k+off-wd', k+off+..)
    # Lp ranges for node u=k h: (k - ihi + jj, k - ilo + jj + je) = (k + off - wp, k + off + je), off = jj - ilo,
    # wp = ihi - ilo.  Lm ranges: (k - jhi - jj - je, k - jlo - jj) = (k + offm - wm - je, k + offm), offm = -jlo-jj.
    cacheA, cacheB = {}, {}

    def sufA(off, wp, je):
        key = (off, wp, je)
        if key not in cacheA:
            suf = [0] * (n5 + 1)
            acc = 0
            for k in range(n5 - 1, 0, -1):
                acc += da[k] * Pp.pm(k + off - wp, k + off + je)
                suf[k] = acc
            cacheA[key] = suf
        return cacheA[key]

    def sufB(offm, wm, je):
        key = (offm, wm, je)
        if key not in cacheB:
            suf = [0] * (n5 + 1)
            acc = 0
            for k in range(n5 - 1, 0, -1):
                acc += db[k] * Pm.pm(k + offm - wm - je, k + offm)
                suf[k] = acc
            cacheB[key] = suf
        return cacheB[key]

    def slopes(kind, i, j):
        if kind == "L":
            return (W[i + 1][j] - W[i][j]) * N, (W[i][j + 1] - W[i][j]) * N
        return (W[i + 1][j + 1] - W[i][j + 1]) * N, (W[i + 1][j + 1] - W[i + 1][j]) * N

    diag = {}

    def diag_data(q):
        if q in diag:
            return diag[q]
        pieces = []
        for k in range(q + 1):
            pieces.append(("L", k, q - k))
            if k < q:
                pieces.append(("U", k, q - k - 1))
        sl = [slopes(*pc) for pc in pieces]
        breaks = []
        for r in range(len(pieces) - 1):
            (gp0, gm0), (gp1, gm1) = sl[r], sl[r + 1]
            dc = abs((gp1 - gm1) - (gp0 - gm0))
            dg = abs(gm1 - gm0)
            k = pieces[r][1]
            if pieces[r][0] == "L":      # horizontal crossing, moving in [k h, (k+1) h]
                breaks.append((True, k, k + 1, dc, dg))
            else:                        # vertical crossing at u = (k+1) h
                breaks.append((False, k + 1, k + 1, dc, dg))
        diag[q] = (breaks, sl[0], sl[-1])
        return diag[q]

    out = []
    slabs = [(0, 0)] if S.J == 0 else [(jj, 1) for jj in range(S.J)]
    for cell in mesh.cells():
        kind, i, j, ns, ilo, ihi, jlo, jhi, verts = cell
        wp, wm = ihi - ilo, jhi - jlo
        for (jj, je) in slabs:
            off, offm = jj - ilo, -jlo - jj
            rp = lambda k0, k1: (k0 + off - wp, k1 + off + je)          # noqa: E731  u in [k0 h, k1 h]
            rm = lambda k0, k1: (k0 + offm - wm - je, k1 + offm)        # noqa: E731
            common_b = bH * Pm.tpm(*rm(n5, n5)) + abs(sb[n5 - 1]) * Pm.pm(*rm(n5, n5))
            Hyy = aH * Pp.tpm(*rp(n5, n5)) + abs(sa[n5 - 1]) * Pp.pm(*rp(n5, n5)) + common_b
            if ns >= N:
                q = ns - N
                breaks, (gpf, gmf), (gpl, gml) = diag_data(q)
                t_last = abs(gml) * Pp.pm(*rp(q, q + 1))
                Hyy += t_last + abs(gpf) * Pp.pm(*rp(0, 0))
                jb = sufB(offm, wm, je)[q + 1] if q + 1 <= n5 - 1 else 0
                ja = sufA(off, wp, je)[q + 1] if q + 1 <= n5 - 1 else 0
                Hyy += ja + jb
                sy = t_last + common_b + jb
                ss = t_last + common_b + jb
                for (moving, k0, k1, dc, dg) in breaks:
                    pmv = Pp.pm(*rp(k0, k1))
                    Hyy += dc * pmv
                    sy += dg * pmv
                    if moving:
                        ss += dg * pmv
                Hsy, Hss = sy, ss
            else:
                jb = sufB(offm, wm, je)[1]
                ja = sufA(off, wp, je)[1]
                Hyy += abs(sa[0]) * Pp.pm(*rp(0, 0)) + abs(sb[0]) * Pm.pm(*rm(0, 0)) + ja + jb
                Hsy = Hss = common_b + abs(sb[0]) * Pm.pm(*rm(0, 0)) + jb
                if not full:   # taboo: the atom piece is absent, its cancellations with T2/T3 are lost
                    ty, te = Pp.tpm(*rp(0, 0)), Pm.tpm(*rm(0, 0))
                    Hyy += w0 * (ty + te)
                    Hsy += w0 * te
                    Hss += w0 * te
            ry = wp + je
            err = Hss + 2 * ry * Hsy + ry * ry * Hyy
            err = -((-err) // (8 * N * N))
            out.append((cell, jj, je, Hss, Hsy, Hyy, err))
    return out


# ------------------------------------------------------------------------------------------------ certificate
def certify(S: Setup, Wint, Q: int, full: bool, want_detail: bool = False):
    """Exact certificate for w = Wint * 2^-Q (P1).  Returns dict with 'certified', exact slack, value at the atom."""
    if any(Wint[i][j] < 0 for (i, j) in S.mesh.nodes):
        return {"certified": False, "reason": "negative nodal value"}
    M = margins(S, Wint, Q, full)
    Hb = hessian_bounds(S, Wint, full)
    worst = None
    worst_cell = None
    fails = 0
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        verts = cell[8]
        vmin = min(M[jj + t][v] for v in verts for t in ((0, 1) if je else (0,)))
        slack = vmin - err
        if slack <= 0:
            fails += 1
        if worst is None or slack < worst:
            worst, worst_cell = slack, (cell[:4], jj, float(F(vmin, 1 << (P + Q))), float(F(err, 1 << (P + Q))))
    scale = F(1, 1 << (P + Q))
    res = {
        "certified": fails == 0,
        "failing_cells": fails,
        "cells_checked": len(Hb),
        "min_slack": str(worst * scale), "min_slack_float": float(worst * scale),
        "worst_cell": worst_cell,
        "w_atom": str(F(Wint[0][0], 1 << Q)), "w_atom_float": Wint[0][0] / 2 ** Q,
        "w_max": str(F(max(Wint[i][j] for (i, j) in S.mesh.nodes), 1 << Q)),
        "min_vertex_margin_float": float(min(min(v.values()) for v in M.values()) * scale),
        "max_err_float": float(max(r[6] for r in Hb) * scale),
    }
    if want_detail:
        res["_M"], res["_Hb"] = M, Hb
    return res
