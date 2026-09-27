"""C2b UNTRUSTED float proposal / NON-CERTIFIED truth: product-integration (Nystrom) value iteration on the P1 grid.

Grid (mesh h = 1/N): triangle nodes (i, j), i, j >= 0, i + j <= 4N, plus axis nodes (i, 0), (0, j) up to 5N.
The operator is K_h = K_e o I_h, I_h = P1 interpolation on the anti-diagonal triangulation.  Because every next
state lies on an axis or on the anti-diagonal s' = s - 1 (a grid line when s is a grid level), K_h at a node is an
EXACT finite sum of nodal values times Gaussian segment weights.  The same weights, in rigorous arithmetic, are the
certificate's vertex evaluator (c2b_exact.py); here they are floats.

Solves (taboo)  t = 1 + Khat t,  d = h1 + Khat d  by Jacobi iteration with a convergence check, then the
regenerative identities  Lambda_h = t(a)/d(a),  V_h = t + (1 - d) Lambda_h  (exact for the discrete chain).
NOTHING here is certified.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

import c2b_common as CM


class Grid:
    def __init__(self, N: int):
        self.N = N
        self.h = 1.0 / N
        self.cols = []                      # cols[i] = number of j values at column i
        for i in range(5 * N + 1):
            if i == 0:
                self.cols.append(5 * N + 1)
            elif i <= 4 * N:
                self.cols.append(4 * N - i + 1)
            else:
                self.cols.append(1)
        self.nodes = [(i, j) for i in range(5 * N + 1) for j in range(self.cols[i])]

    def zeros(self):
        return [[0.0] * c for c in self.cols]

    def const(self, v):
        return [[float(v)] * c for c in self.cols]


def seg_weights_float(c: float, h: float, dmin: int, dmax: int):
    """A(d), B(d) for the segment [t_d, t_{d+1}], t_d = c + d h: weights of the left/right nodal values of the P1
    hat pieces against phi(t) dt; plus Phi(t_d)."""
    Phi = {d: CM.Phi_float(c + d * h) for d in range(dmin, dmax + 2)}
    phi = {d: CM.phi_float(c + d * h) for d in range(dmin, dmax + 2)}

    def mass(d):
        a, b = c + d * h, c + (d + 1) * h
        if a >= 0:   # upper tails for accuracy
            return 0.5 * (math.erfc(a / math.sqrt(2)) - math.erfc(b / math.sqrt(2)))
        return Phi[d + 1] - Phi[d]

    A, B = {}, {}
    for d in range(dmin, dmax + 1):
        M0 = mass(d)
        M1 = phi[d] - phi[d + 1]
        t0, t1 = c + d * h, c + (d + 1) * h
        A[d] = (t1 * M0 - M1) / h
        B[d] = (M1 - t0 * M0) / h
    return A, B, Phi


class FloatKernel:
    def __init__(self, N: int, e: float):
        self.g = Grid(N)
        self.N, self.e = N, float(e)
        h = self.g.h
        D = 5 * N + 2
        Kf = 0.5
        self.Ap, self.Bp, self.Phip = seg_weights_float(Kf + self.e, h, -D, D)
        self.Am, self.Bm, self.Phim = seg_weights_float(Kf - self.e, h, -D, D)
        # window mass at each node: Phi(C - p + e) - Phi(m - C + e)
        C = 5.5
        self.mass = self.g.zeros()
        self.katom = self.g.zeros()
        for (i, j) in self.g.nodes:
            p, m = i * h, j * h
            self.mass[i][j] = CM.Phi_float(C - p + self.e) - CM.Phi_float(m - C + self.e)
            if i + j < N:
                self.katom[i][j] = CM.Phi_float(Kf + self.e - p) - CM.Phi_float(m - Kf + self.e)

    def apply(self, W, full: bool):
        """(K_h W)(node) for all nodes; full=False drops the atom piece (taboo kernel Khat)."""
        g, N = self.g, self.N
        n5 = 5 * N
        a = [W[k][0] for k in range(n5 + 1)]
        b = [W[0][k] for k in range(n5 + 1)]
        Ap, Bp, Am, Bm = self.Ap, self.Bp, self.Am, self.Bm
        # suffix sums over segments k >= A for each shift index
        S3 = []
        for i in range(n5 + 1):
            suf = [0.0] * (n5 + 1)
            acc = 0.0
            for k in range(n5 - 1, -1, -1):
                acc += Ap[k - i] * a[k] + Bp[k - i] * a[k + 1]
                suf[k] = acc
            S3.append(suf)
        S2 = []
        for j in range(n5 + 1):
            suf = [0.0] * (n5 + 1)
            acc = 0.0
            for k in range(n5 - 1, -1, -1):
                acc += Am[k - j] * b[k] + Bm[k - j] * b[k + 1]
                suf[k] = acc
            S2.append(suf)
        out = g.zeros()
        w0 = W[0][0]
        for (i, j) in g.nodes:
            n = i + j
            A = max(0, n - N)
            v = S3[i][A] + S2[j][A]
            if n > N:
                q = n - N
                v += sum(Ap[k - i] * W[k][q - k] + Bp[k - i] * W[k + 1][q - k - 1] for k in range(q))
            elif n < N and full:
                v += w0 * self.katom[i][j]
            out[i][j] = v
        return out

    def solve_taboo(self, tol=1e-13, maxit=20000):
        g = self.g
        t = g.zeros()
        d = g.zeros()
        h1 = [[1.0 - self.mass[i][j] for j in range(g.cols[i])] for i in range(len(g.cols))]
        it = 0
        while True:
            it += 1
            Kt = self.apply(t, full=False)
            Kd = self.apply(d, full=False)
            tn = [[1.0 + Kt[i][j] for j in range(g.cols[i])] for i in range(len(g.cols))]
            dn = [[h1[i][j] + Kd[i][j] for j in range(g.cols[i])] for i in range(len(g.cols))]
            dt = max(abs(tn[i][j] - t[i][j]) for (i, j) in g.nodes)
            dd = max(abs(dn[i][j] - d[i][j]) for (i, j) in g.nodes)
            t, d = tn, dn
            if (dt <= tol * max(1.0, t[0][0]) and dd <= tol) or it >= maxit:
                break
        Lam = t[0][0] / d[0][0]
        V = [[t[i][j] + (1.0 - d[i][j]) * Lam for j in range(g.cols[i])] for i in range(len(g.cols))]
        return {"t": t, "d": d, "V": V, "Lambda": Lam, "tau_a": t[0][0], "D": d[0][0],
                "C_T": max(t[i][j] for (i, j) in g.nodes), "iterations": it, "last_dt": dt, "last_dd": dd}

    def residual(self, W, full: bool, rhs=1.0):
        """max |W - rhs - K_h W| over nodes (float consistency check)."""
        KW = self.apply(W, full)
        return max(abs(W[i][j] - rhs - KW[i][j]) for (i, j) in self.g.nodes)


def truth(e, Ns=(10, 20, 40)):
    """NON-CERTIFIED truth: Nystrom Lambda_h, tau_h, C_T,h at several meshes + Richardson (assumes O(h^2))."""
    CM.guard(e)
    rows = []
    for N in Ns:
        fk = FloatKernel(N, float(e))
        s = fk.solve_taboo()
        s["N"] = N
        s["residual_whole"] = fk.residual(s["V"], full=True)
        s["residual_taboo"] = fk.residual(s["t"], full=False)
        rows.append(s)
    out = {"e": str(F(e)), "meshes": []}
    for s in rows:
        out["meshes"].append({k: s[k] for k in ("N", "Lambda", "tau_a", "D", "C_T", "iterations", "last_dt",
                                                "last_dd", "residual_whole", "residual_taboo")})
    for key in ("Lambda", "tau_a", "C_T"):
        rich = []
        for s0, s1 in zip(rows, rows[1:]):
            r = s1["N"] / s0["N"]
            rich.append((r * r * s1[key] - s0[key]) / (r * r - 1))
        out[key + "_richardson"] = rich
    return out, rows


def robust(N, e_list, tol=1e-10, maxit=20000):
    """NON-CERTIFIED robust (adversarial time-varying drift) ARL on the drift grid e_list:
    W* = 1 + max_e K_{e,h} W*.  Any block-uniform supersolution w satisfies w >= W* (induction), so W*(a) is the
    intrinsic floor of a common-supersolution A0 on that grid.  Started from max_e V_e (a subsolution), the Jacobi
    iterates increase monotonically; stop when the sup increment < tol * W(a); remaining error ~ increment * Lambda."""
    for e in e_list:
        CM.guard(e)
    kernels = [FloatKernel(N, float(e)) for e in e_list]
    sols = [k.solve_taboo() for k in kernels]
    g = kernels[0].g
    W = [[max(s["V"][i][j] for s in sols) for j in range(g.cols[i])] for i in range(len(g.cols))]
    it = 0
    while True:
        it += 1
        KW = [k.apply(W, True) for k in kernels]
        Wn = [[1.0 + max(kw[i][j] for kw in KW) for j in range(g.cols[i])] for i in range(len(g.cols))]
        inc = max(Wn[i][j] - W[i][j] for (i, j) in g.nodes)
        W = Wn
        if inc < tol * W[0][0] or it >= maxit:
            break
    argmax = {}
    for (i, j) in g.nodes:
        r = max(range(len(KW)), key=lambda q: KW[q][i][j])
        argmax[r] = argmax.get(r, 0) + 1
    return {"W_atom": W[0][0], "Lambdas": [s["Lambda"] for s in sols], "iterations": it, "last_increment": inc,
            "argmax_counts": {str(e_list[r]): c for r, c in argmax.items()}}
