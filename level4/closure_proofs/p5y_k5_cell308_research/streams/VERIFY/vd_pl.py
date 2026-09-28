"""Stream D, D6: independent rigorous verifier for P1 (triangle-piecewise-linear) nodal certificates.

W is given by nodal values w[i][j] at (i h, j h), h = 1/N, on the mesh of R: the triangles
    L(i,j) = conv{(i,j), (i+1,j), (i,j+1)}          (i + j <= 4N - 1)
    U(i,j) = conv{(i+1,j), (i,j+1), (i+1,j+1)}      (i + j <= 4N - 2)
(the anti-diagonal split of each square) and the axis segments [(i,0),(i+1,0)], [(0,j),(0,j+1)] for i, j >= 4N; W is
linear on every cell (data layout as in stream A0's stored certificates; nothing else is taken from any certifier).

Kernel application (derived here).  Fix x and put u = z + e, a_p = p - K - e, a_m = m - K + e.  Along the window
u in [u_L, u_H] = [m - C + e, C - p + e] the path value g(u) = W(T(x, u - e)) is CONTINUOUS and piecewise linear:
the image runs down the m-axis (m' = a_m - u), then (t >= 1) along the line p' + m' = t - 1 or (t <= 1) sits in the
atom (value W(a)), then along the p-axis (p' = a_p + u).  With Phi' = phi and Psi(u) = u Phi(u) + phi(u) (Psi' = Phi),
integrating by parts twice:
    int_{u_L}^{u_H} g phi du = g(u_H) Phi(u_H) - g(u_L) Phi(u_L) - s_last Psi(u_H) + s_first Psi(u_L)
                               + sum_k (s_k^+ - s_k^-) Psi(u_k)
over the kinks u_k of g (slopes s in u).  Every kink is a mesh crossing of the path: p' = i h at
u = pU(i) = i h + K + e - p, or m' = j h at u = mU(j) = m + e - K - j h; the kink coefficients are exact rationals
fixed by the nodal values and by the t-band of x only:
  t <= 1:          p-side  i = 0: (C_1 - C_0)/h,  i >= 1: second differences of C_i = w[i][0] (over h)
                   m-side  j = 0: (A_1 - A_0)/h,  j >= 1: second differences of A_j = w[0][j]
  t - 1 in [b h, (b+1) h]:
                   p-side  i = 0: (w[1][b] - w[0][b])/h;  1 <= i <= b: D(i, b-i) - D(i-1, b-i);  i > b: d2 C_i
                   m-side  j = 0: (w[b][1] - w[b][0])/h;  1 <= j <= b: D(b-j, j-1) - D(b-j, j);  j > b: d2 A_j
  with D(i, j) = (w[i+1][j] - w[i][j+1]) / h (the slope along p' + m' = const on L(i,j) and U(i,j)),
  and the window ends: p-side  C_5N Phi(u_H) - s_C,last Psi(u_H);  m-side  -A_5N Phi(u_L) + s_A,first Psi(u_L).
Hence on every mesh cell (one t-band, one linear piece of W) the residual is SEPARABLE:
    F(p, m) = alpha + beta p + gamma m - 1 - P_band(p) - M_band(m),
with P, M finite sums of Psi, Phi at affine arguments.  Per cell (and sub-cell after midpoint subdivision):
    F(x) >= F(c) + min_{vertices v} grad F(c).(v - c) - (1/2)(max|P''| r_p^2 + max|M''| r_m^2),
c the centroid (in R), gradient at c with thin intervals, P'', M'' enclosed over the cell's p- and m-ranges; exact
dyadic-rational interval arithmetic (vd_verify primitives, outward rounding).  A centroid with residual upper bound
< 0 is a rigorous witness.  W >= 0 on R iff every nodal value is >= 0 (P1).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_verify as V  # noqa: E402  (own interval arithmetic and special functions)

Q = V.Q
K, C = V.KQ, V.CQ
ifr, iadd, isub, ineg, imul, imaxabs, ONE, PREC = V.ifr, V.iadd, V.isub, V.ineg, V.imul, V.imaxabs, V.ONE, V.PREC


def _cols(N: int) -> list:
    return [5 * N + 1] + [4 * N - i + 1 for i in range(1, 4 * N + 1)] + [1] * N


class PLW:
    """P1 nodal function on the mesh of R (h = 1/N); w[i][j] exact Fractions."""

    def __init__(self, N: int, w: list, meta=None):
        self.N = int(N)
        self.h = F(1, self.N)
        cols = _cols(self.N)
        if len(w) != len(cols) or any(len(w[i]) != c for i, c in enumerate(cols)):
            raise ValueError("nodal array shape does not match the mesh of R")
        self.w = [[F(x) for x in col] for col in w]
        self.meta = meta or {}

    # ------------------------------------------------------------------ exact evaluation
    def at_atom(self) -> F:
        return self.w[0][0]

    def tri_lin(self, kind: str, i: int, j: int) -> tuple:
        """(alpha, beta, gamma) with W = alpha + beta p + gamma m on the cell."""
        h, w = self.h, self.w
        if kind == "L":
            b = (w[i + 1][j] - w[i][j]) / h
            g = (w[i][j + 1] - w[i][j]) / h
            return w[i][j] - b * i * h - g * j * h, b, g
        if kind == "U":
            b = (w[i + 1][j + 1] - w[i][j + 1]) / h
            g = (w[i + 1][j + 1] - w[i + 1][j]) / h
            return w[i + 1][j + 1] - b * (i + 1) * h - g * (j + 1) * h, b, g
        if kind == "AXP":
            b = (w[i + 1][0] - w[i][0]) / h
            return w[i][0] - b * i * h, b, F(0)
        if kind == "AXM":
            g = (w[0][j + 1] - w[0][j]) / h
            return w[0][j] - g * j * h, F(0), g
        raise ValueError(kind)

    def locate(self, p: F, m: F) -> tuple:
        """a cell (kind, i, j) containing the point (p, m) of R."""
        p, m, h, N = F(p), F(m), self.h, self.N
        if not V.in_R(p, m):
            raise ValueError("point outside R")
        if p + m > 4:
            if m == 0:
                return ("AXP", min(int(p / h), 5 * N - 1), 0)
            return ("AXM", 0, min(int(m / h), 5 * N - 1))
        i0, j0 = int(p / h), int(m / h)
        for di in (0, -1):
            for dj in (0, -1):
                i, j = i0 + di, j0 + dj
                if i < 0 or j < 0:
                    continue
                if i + j <= 4 * N - 1 and p >= i * h and m >= j * h and p + m <= (i + j + 1) * h:
                    return ("L", i, j)
                if i + j <= 4 * N - 2 and p <= (i + 1) * h and m <= (j + 1) * h and p + m >= (i + j + 1) * h:
                    return ("U", i, j)
        raise ValueError(f"no cell found for {(p, m)}")

    def value(self, p, m) -> F:
        a, b, g = self.tri_lin(*self.locate(F(p), F(m)))
        return a + b * F(p) + g * F(m)

    def min_node(self) -> F:
        return min(min(col) for col in self.w)

    def scaled(self, s) -> "PLW":
        s = F(s)
        return PLW(self.N, [[x * s for x in col] for col in self.w], dict(self.meta))

    def with_node(self, i: int, j: int, v) -> "PLW":
        w = [list(col) for col in self.w]
        w[i][j] = F(v)
        return PLW(self.N, w, dict(self.meta))

    def to_json(self) -> dict:
        return {"format": "VD_PL_NODAL/1", "N": self.N,
                "w": [[f"{x.numerator}/{x.denominator}" for x in col] for col in self.w]}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    @staticmethod
    def from_json(obj: dict) -> "PLW":
        return PLW(int(obj["N"]), [[F(x) for x in col] for col in obj["w"]])

    # ------------------------------------------------------------------ kernel coefficients
    def band_of(self, kind: str, i: int, j: int):
        k = {"L": i + j, "U": i + j + 1, "AXP": i, "AXM": j}[kind]
        return "low" if k <= self.N - 1 else k - self.N

    def coeffs(self, band, omit_atom: bool = False) -> dict:
        """exact kink coefficients: {'psiP': {i: c}, 'phiP': {i: c}, 'psiM': {j: c}, 'phiM': {j: c}, 'tail': t0}
        where the band-independent second-difference tail i, j in [t0, 5N-1] is NOT included (added by suffix sums)."""
        N, h, w = self.N, self.h, self.w
        n5 = 5 * N
        Cc = [w[i][0] for i in range(n5 + 1)]
        Aa = [w[0][j] for j in range(n5 + 1)]
        psiP, psiM = {}, {}
        phiP = {n5: Cc[n5]}
        phiM = {n5: -Aa[n5]}
        psiP[n5] = -(Cc[n5] - Cc[n5 - 1]) / h
        psiM[n5] = -(Aa[n5] - Aa[n5 - 1]) / h

        def D(i, j):
            return (w[i + 1][j] - w[i][j + 1]) / h

        if band == "low":
            psiP[0] = (Cc[1] - Cc[0]) / h
            psiM[0] = (Aa[1] - Aa[0]) / h
            t0 = 1
            if omit_atom:
                phiP[0] = phiP.get(0, F(0)) - w[0][0]
                phiM[0] = phiM.get(0, F(0)) + w[0][0]
        else:
            b = int(band)
            psiP[0] = (w[1][b] - w[0][b]) / h
            psiM[0] = (w[b][1] - w[b][0]) / h
            for i in range(1, b + 1):
                psiP[i] = D(i, b - i) - D(i - 1, b - i)
            for j in range(1, b + 1):
                psiM[j] = D(b - j, j - 1) - D(b - j, j)
            t0 = b + 1
        return {"psiP": psiP, "phiP": phiP, "psiM": psiM, "phiM": phiM, "tail": t0}

    def d2_tails(self) -> tuple:
        N, h, w = self.N, self.h, self.w
        n5 = 5 * N
        d2C = [F(0)] * (n5 + 1)
        d2A = [F(0)] * (n5 + 1)
        for i in range(1, n5):
            d2C[i] = (w[i + 1][0] - 2 * w[i][0] + w[i - 1][0]) / h
            d2A[i] = (w[0][i + 1] - 2 * w[0][i] + w[0][i - 1]) / h
        return d2C, d2A


def from_a0_cert(cert: dict) -> PLW:
    """Adapter for stream A0's stored C2b / C2bx certificates (layout only): W = int / 2^Qbits per node, columns i of
    heights _cols(N); W_sha256 = sha256(json.dumps([[str(x) ...] ...], sort_keys=True, separators=(',', ':')))."""
    N, Qb = int(cert["N"]), int(cert["Qbits"])
    raw = [[str(x) for x in col] for col in cert["W"]]
    sha = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if sha != cert["W_sha256"]:
        raise ValueError("W_SHA256_MISMATCH")
    ints = [[int(x) for x in col] for col in raw]
    return PLW(N, [[F(x, 1 << Qb) for x in col] for col in ints],
               {"certifier": cert.get("certifier"), "claim_w_atom": cert.get("claim_w_atom"), "drift": cert["drift"],
                "kind": cert.get("kind"), "selection": cert.get("selection")})


# ================================================================================================ per-process state
class Engine:
    """per-process caches: 1-D jets of P_band on p-intervals and M_band on m-intervals."""

    def __init__(self, W: PLW, e: F, omit_atom: bool = False, direction: str = "super"):
        Q.guard_drift(e)
        self.W, self.e, self.omit_atom, self.dir = W, F(e), omit_atom, direction
        self.N, self.h = W.N, W.h
        self.n5 = 5 * W.N
        d2C, d2A = W.d2_tails()
        self.d2C = [ifr(x) for x in d2C]
        self.d2A = [ifr(x) for x in d2A]
        self.cp = [F(i, self.N) + K + self.e for i in range(self.n5 + 1)]      # pU(i) = cp[i] - p
        self.cm = [self.e - K - F(j, self.N) for j in range(self.n5 + 1)]      # mU(j) = m + cm[j]
        self._coef = {}
        self._base = {}
        self._jet = {}

    def coef(self, band) -> dict:
        if band not in self._coef:
            c = self.W.coeffs(band, self.omit_atom)
            self._coef[band] = {k: ({i: ifr(x) for i, x in v.items()} if isinstance(v, dict) else v)
                                for k, v in c.items()}
        return self._coef[band]

    def base(self, side: str, lo: F, hi: F, c: F) -> dict:
        """per-index jets on the interval [lo, hi] with expansion point c, plus suffix sums of the d2 tail."""
        key = (side, lo, hi, c)
        if key in self._base:
            return self._base[key]
        n5 = self.n5
        sgn = -1 if side == "p" else 1
        consts = self.cp if side == "p" else self.cm
        Psi, Phi, phi, phiU, uphiU = [], [], [], [], []
        for k in range(n5 + 1):
            if side == "p":
                uc = consts[k] - c
                U = (ifr(consts[k] - hi)[0], ifr(consts[k] - lo)[1])
            else:
                uc = c + consts[k]
                U = (ifr(lo + consts[k])[0], ifr(hi + consts[k])[1])
            ui = ifr(uc)
            Pc = V.Phi_iv(ui)
            pc = V.phi_iv(ui)
            Psi.append(iadd(imul(ui, Pc), pc))
            Phi.append(Pc)
            phi.append(pc)
            pU = V.phi_iv(U)
            phiU.append(pU)
            uphiU.append(imul(U, pU))
        d2 = self.d2C if side == "p" else self.d2A
        # suffix sums over k in [t, n5 - 1] of d2[k] * (Psi, d1, d2) jets
        Sv = [(0, 0)] * (n5 + 1)
        S1 = [(0, 0)] * (n5 + 1)
        S2 = [(0, 0)] * (n5 + 1)
        acc_v = acc_1 = acc_2 = (0, 0)
        for k in range(n5 - 1, 0, -1):
            acc_v = iadd(acc_v, imul(d2[k], Psi[k]))
            acc_1 = iadd(acc_1, imul(d2[k], Phi[k]))
            acc_2 = iadd(acc_2, imul(d2[k], phiU[k]))
            Sv[k], S1[k], S2[k] = acc_v, acc_1, acc_2
        out = {"Psi": Psi, "Phi": Phi, "phi": phi, "phiU": phiU, "uphiU": uphiU, "Sv": Sv, "S1": S1, "S2": S2,
               "sgn": sgn}
        self._base[key] = out
        return out

    def jet(self, side: str, lo: F, hi: F, c: F, band) -> tuple:
        """(value at c, first derivative at c, second-derivative enclosure over [lo, hi]) of P_band (side 'p') or
        M_band (side 'm')."""
        key = (side, lo, hi, c, band)
        if key in self._jet:
            return self._jet[key]
        B = self.base(side, lo, hi, c)
        cf = self.coef(band)
        psi = cf["psiP"] if side == "p" else cf["psiM"]
        phc = cf["phiP"] if side == "p" else cf["phiM"]
        t0 = cf["tail"]
        val, d1, d2 = B["Sv"][t0], B["S1"][t0], B["S2"][t0]
        for k, a in psi.items():
            val = iadd(val, imul(a, B["Psi"][k]))
            d1 = iadd(d1, imul(a, B["Phi"][k]))
            d2 = iadd(d2, imul(a, B["phiU"][k]))
        for k, a in phc.items():
            val = iadd(val, imul(a, B["Phi"][k]))
            d1 = iadd(d1, imul(a, B["phi"][k]))
            d2 = isub(d2, imul(a, B["uphiU"][k]))
        if B["sgn"] < 0:          # d/dp of f(c_k - p) = -f'(u); second derivative sign unchanged
            d1 = ineg(d1)
        out = (val, d1, d2)
        self._jet[key] = out
        return out

    # ------------------------------------------------------------------ cell bound
    def cell_bound(self, verts: tuple, band, lin: tuple) -> tuple:
        """(lower bound of the residual over the cell, residual enclosure at the centroid, centroid)."""
        alpha, beta, gamma = lin
        ps = [v[0] for v in verts]
        ms = [v[1] for v in verts]
        p0, p1, m0, m1 = min(ps), max(ps), min(ms), max(ms)
        pc, mc = sum(ps) / len(ps), sum(ms) / len(ms)
        Pv, P1, P2 = self.jet("p", p0, p1, pc, band)
        Mv, M1, M2 = self.jet("m", m0, m1, mc, band)
        Wc = alpha + beta * pc + gamma * mc
        Fc = isub(isub(ifr(Wc - 1), Pv), Mv)
        gp = isub(ifr(beta), P1)
        gm = isub(ifr(gamma), M1)
        if self.dir == "sub":                    # check 1 + K W - W >= 0 instead
            Fc, gp, gm = ineg(Fc), ineg(gp), ineg(gm)
        lin_lo = None
        for (vp, vm) in verts:
            t = iadd(imul(gp, ifr(vp - pc)), imul(gm, ifr(vm - mc)))
            lin_lo = t[0] if lin_lo is None else min(lin_lo, t[0])
        rp = ifr(max(abs(v - pc) for v in ps))[1]
        rm = ifr(max(abs(v - mc) for v in ms))[1]
        q = imaxabs(P2) * rp * rp + imaxabs(M2) * rm * rm
        quad = -((-q) >> (2 * PREC + 1))
        lb = Fc[0] + lin_lo - quad
        return lb, Fc, (pc, mc)

    def point_residual(self, p: F, m: F) -> tuple:
        """rigorous enclosure of W - 1 - K_e W at an exact point of R (its own cell formula)."""
        kind, i, j = self.W.locate(p, m)
        band = self.W.band_of(kind, i, j)
        if kind in ("L", "U") and self.W.band_of(kind, i, j) != band:
            raise AssertionError
        a, b, g = self.W.tri_lin(kind, i, j)
        Pv = self.jet("p", F(p), F(p), F(p), band)[0]
        Mv = self.jet("m", F(m), F(m), F(m), band)[0]
        r = isub(isub(ifr(a + b * F(p) + g * F(m) - 1), Pv), Mv)
        return V.to_frac_lo(r), V.to_frac_hi(r)


def point_band_check(W: PLW, p: F, m: F):
    """the band of a point is the band of any cell containing it only in the interior; at a band boundary both
    formulas agree (continuity), which vd_crosscheck_pl tests."""
    return W.band_of(*W.locate(p, m))


# ================================================================================================ branch and bound
def base_cells(W: PLW) -> list:
    N, h = W.N, W.h
    out = []
    for i in range(4 * N):
        for j in range(4 * N - i):
            out.append(("L", i, j))
            if i + j + 2 <= 4 * N:
                out.append(("U", i, j))
    for i in range(4 * N, 5 * N):
        out.append(("AXP", i, 0))
    for j in range(4 * N, 5 * N):
        out.append(("AXM", 0, j))
    return out


def cell_verts(W: PLW, kind: str, i: int, j: int) -> tuple:
    h = W.h
    if kind == "L":
        return ((i * h, j * h), ((i + 1) * h, j * h), (i * h, (j + 1) * h))
    if kind == "U":
        return (((i + 1) * h, j * h), (i * h, (j + 1) * h), ((i + 1) * h, (j + 1) * h))
    if kind == "AXP":
        return ((i * h, F(0)), ((i + 1) * h, F(0)))
    return ((F(0), j * h), (F(0), (j + 1) * h))


def subdivide(verts: tuple) -> list:
    if len(verts) == 2:
        a, b = verts
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return [(a, mid), (mid, b)]
    a, b, c = verts
    mab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    mbc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
    mca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
    return [(a, mab, mca), (mab, b, mbc), (mca, mbc, c), (mab, mbc, mca)]


_ENG = None


def _init_worker(W_json, e_str, omit_atom, direction):
    global _ENG
    _ENG = Engine(PLW.from_json(W_json), F(e_str), omit_atom, direction)


def bb_cells(args) -> dict:
    cells, max_depth, max_boxes = args
    E = _ENG
    W = E.W
    n = 0
    min_lb = None
    min_ub, min_ub_at = None, None
    undecided = 0
    for (kind, i, j) in cells:
        band = W.band_of(kind, i, j)
        lin = W.tri_lin(kind, i, j)
        stack = [(cell_verts(W, kind, i, j), 0)]
        while stack:
            verts, depth = stack.pop()
            n += 1
            lb, Fc, (pc, mc) = E.cell_bound(verts, band, lin)
            if min_ub is None or Fc[1] < min_ub:
                min_ub, min_ub_at = Fc[1], (pc, mc)
            if Fc[1] < 0:
                return {"status": "REFUTED", "boxes": n, "witness": {
                    "p": f"{pc.numerator}/{pc.denominator}", "m": f"{mc.numerator}/{mc.denominator}",
                    "cell": [kind, i, j], "band": str(band), "value_hi": F(Fc[1], ONE), "value_lo": F(Fc[0], ONE)}}
            if lb >= 0:
                min_lb = lb if min_lb is None else min(min_lb, lb)
                continue
            if depth >= max_depth or n >= max_boxes:
                undecided += 1
                min_lb = lb if min_lb is None else min(min_lb, lb)
                continue
            for ch in subdivide(verts):
                stack.append((ch, depth + 1))
    return {"status": "CERTIFIED" if not undecided else "UNDECIDED", "boxes": n, "n_undecided": undecided,
            "min_lb": None if min_lb is None else F(min_lb, ONE), "min_ub": None if min_ub is None else F(min_ub, ONE),
            "min_ub_at": None if min_ub_at is None else [str(min_ub_at[0]), str(min_ub_at[1])]}


def verify_pl(W: PLW, e, *, direction: str = "super", omit_atom: bool = False, workers: int = 3,
              max_depth: int = 12, max_boxes: int = 10 ** 6, claim=None) -> dict:
    """Rigorously decide W >= 1 + K_e W (direction 'super'; plus W >= 0) or W <= 1 + K_e W ('sub') on all of R."""
    e = F(e)
    Q.guard_drift(e)
    t0 = time.time()
    cells = base_cells(W)
    by_col: dict = {}
    for c in cells:
        key = c[1] if c[0] != "AXM" else -1
        by_col.setdefault(key, []).append(c)
    jobs = [(v, max_depth, max_boxes) for _, v in sorted(by_col.items(), key=lambda kv: -len(kv[1]))]
    Wj = W.to_json()
    res, early = [], False
    if workers <= 1:
        _init_worker(Wj, str(e), omit_atom, direction)
        for j in jobs:
            res.append(bb_cells(j))
            if res[-1]["status"] == "REFUTED":
                early = True
                break
    else:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(min(3, workers), initializer=_init_worker,
                                          initargs=(Wj, str(e), omit_atom, direction)) as pool:
            for r in pool.imap_unordered(bb_cells, jobs, chunksize=1):
                res.append(r)
                if r["status"] == "REFUTED":
                    early = True
                    break
    refuted = [r for r in res if r["status"] == "REFUTED"]
    und = [r for r in res if r["status"] == "UNDECIDED"]
    status = "REFUTED" if refuted else ("UNDECIDED" if und else "CERTIFIED")
    wmin = W.min_node()
    nonneg_ok = wmin >= 0 if direction == "super" else True
    certified = status == "CERTIFIED" and nonneg_ok
    witness = None
    if refuted:
        witness = {"kind": "RESIDUAL_NEGATIVE" if direction == "super" else "SUB_RESIDUAL_NEGATIVE",
                   **min(refuted, key=lambda r: r["witness"]["value_hi"])["witness"]}
    elif not nonneg_ok:
        for i, col in enumerate(W.w):
            for j, x in enumerate(col):
                if x == wmin and witness is None:
                    witness = {"kind": "W_NEGATIVE_AT_NODE", "i": i, "j": j, "p": str(F(i, W.N)),
                               "m": str(F(j, W.N)), "value": x}
    lbs = [r["min_lb"] for r in res if r.get("min_lb") is not None]
    ubs = [r for r in res if r.get("min_ub") is not None]
    best = min(ubs, key=lambda r: r["min_ub"]) if ubs else None
    out = {"certified": certified,
           "verdict": "PASS" if certified else ("FAIL" if witness else "UNDECIDED"),
           "direction": direction, "drift": e, "N": W.N, "omit_atom": omit_atom,
           "min_margin_lower_bound": min(lbs) if (lbs and status == "CERTIFIED") else None,
           "min_residual_upper_bound": best["min_ub"] if best else None,
           "min_residual_upper_bound_at": best.get("min_ub_at") if best else None,
           "W_min_node": wmin, "W_at_atom": W.at_atom(), "witness_if_refuted": witness,
           "cells": len(cells), "boxes": sum(r["boxes"] for r in res), "jobs": len(jobs),
           "jobs_processed": len(res), "early_exit_on_witness": early,
           "n_undecided": sum(r.get("n_undecided", 0) for r in res), "sha256_W": W.sha256(),
           "seconds": round(time.time() - t0, 1)}
    if claim is not None:
        out["claim_w_atom"] = F(claim)
        out["W_at_atom_equals_claim"] = W.at_atom() == F(claim)
        if not out["W_at_atom_equals_claim"]:
            out["certified"] = False
            out["verdict"] = "FAIL"
            out["claim_mismatch"] = True
    return out


def load_a0(path) -> tuple:
    Q.guard_path(path)
    cert = json.loads(Path(path).read_text())
    return from_a0_cert(cert), cert


if __name__ == "__main__":
    for pth in sys.argv[1:]:
        W, cert = load_a0(pth)
        d = "super" if cert["certifier"] == "C2B_P1_SUPER" else "sub"
        r = verify_pl(W, F(cert["drift"]), direction=d, claim=cert["claim_w_atom"])
        print(json.dumps(V.jsonable({k: r[k] for k in ("verdict", "direction", "N", "boxes", "seconds",
                                                        "W_at_atom_equals_claim", "min_margin_lower_bound")})))
