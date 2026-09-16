"""Manufactured analytic systems with EXACT derivatives, for non-scientific qualification only.

    K(e)   = sum_(p=0..5) A_p (e - c)^p        (n x n rational matrices)
    S_r(e) = sum_(p=0..5) s_(r,p) (e - c)^p    (r = 0..4)
    F_r    = (I - K)^-1 S_r,   W_(r,0) = S_r,   W_(r,j) = K W_(r,j-1)

These are NOT the CUSUM operators, carry no detector, cell table or K1 record, and say nothing about R_(D,m).
True derivatives at any rational e come from exact truncated power series; norm constants on a cell come from the
triangle inequality over the monomials in (e - c), which is rigorous. Pseudo-randomness is an integer LCG, so every
trial is a pure function of its seed.
"""
from __future__ import annotations

from fractions import Fraction as Fr
from math import comb, factorial

import order3_algebra as A

DEG = 5
LCG_MOD = (1 << 61) - 1


class Rng:
    def __init__(self, seed: int):
        self.x = (seed * 6364136223846793005 + 1442695040888963407) % LCG_MOD

    def frac(self, span: int, den: int) -> Fr:
        self.x = (self.x * 3935559000370003845 + 2691343689449507681) % LCG_MOD
        return Fr(self.x % (2 * span + 1) - span, den)


def falling(p: int, i: int) -> int:
    return factorial(p) // factorial(p - i) if p >= i else 0


def matvec(M, v):
    return [sum((a * b for a, b in zip(row, v, strict=True)), Fr(0)) for row in M]


def matnorm(M) -> Fr:
    return max(sum((abs(a) for a in row), Fr(0)) for row in M)


def solve(M, b):
    """Exact Gaussian elimination with pivoting on nonzero entries."""
    n = len(b)
    a = [list(row) + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = next(r for r in range(col, n) if a[r][col] != 0)
        a[col], a[piv] = a[piv], a[col]
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col], strict=True)]
    return [a[i][n] / a[i][i] for i in range(n)]


class System:
    def __init__(self, n: int, A_: list, s: list, centre: Fr):
        self.n, self.A, self.s, self.c = n, A_, s, centre

    # ---- exact derivatives of the data at e
    def K_deriv(self, i: int, e: Fr):
        t = e - self.c
        return [[sum((falling(p, i) * self.A[p][a][b] * t ** (p - i) for p in range(i, DEG + 1)), Fr(0))
                 for b in range(self.n)] for a in range(self.n)]

    def S_deriv(self, r: int, i: int, e: Fr):
        t = e - self.c
        return [sum((falling(p, i) * self.s[r][p][a] * t ** (p - i) for p in range(i, DEG + 1)), Fr(0))
                for a in range(self.n)]

    # ---- exact true object derivatives at e, orders 0..N
    def true_objects(self, e: Fr, N: int = 3) -> dict:
        Kc = [[[x / factorial(q) for x in row] for row in self.K_deriv(q, e)] for q in range(N + 1)]
        IK0 = [[(Fr(1) if a == b else Fr(0)) - Kc[0][a][b] for b in range(self.n)] for a in range(self.n)]
        out = {}
        for r in range(5):
            sc = [[x / factorial(q) for x in self.S_deriv(r, q, e)] for q in range(N + 1)]
            f = []
            for q in range(N + 1):
                rhs = list(sc[q])
                for p in range(1, q + 1):
                    rhs = A.add(rhs, matvec(Kc[p], f[q - p]))
                f.append(solve(IK0, rhs))
            out[("F", r)] = [A.scale(factorial(q), f[q]) for q in range(N + 1)]
            out[("W", (r, 0))] = [A.scale(factorial(q), sc[q]) for q in range(N + 1)] if r < 4 else None
        for (r, j) in A.W_INDICES:
            prev = [A.scale(Fr(1, factorial(q)), v) for q, v in enumerate(out[("W", (r, j - 1))])]
            w = []
            for q in range(N + 1):
                acc = [Fr(0)] * self.n
                for p in range(q + 1):
                    acc = A.add(acc, matvec(Kc[p], prev[q - p]))
                w.append(acc)
            out[("W", (r, j))] = [A.scale(factorial(q), w[q]) for q in range(N + 1)]
        return out

    def true_R(self, e: Fr, m: int, n: int) -> Fr:
        obj = self.true_objects(e, n)
        total = Fr(0)
        for kind, r, j, c in A.coefficients(m):
            v = obj[("F", r)] if kind == "F" else obj[("W", (r, j))]
            total += c * v[n][A.ORIGIN]
        return total

    # ---- rigorous cell norm constants
    def cell_norms(self, e0: Fr, rho: Fr) -> dict:
        tmax = max(abs(e0 - rho - self.c), abs(e0 + rho - self.c))
        k = [sum((falling(p, i) * matnorm(self.A[p]) * tmax ** (p - i) for p in range(i, DEG + 1)), Fr(0))
             for i in range(DEG + 1)]
        if not k[0] < 1:
            raise ValueError("sup_cell ||K|| >= 1: Neumann bound unavailable")
        TS = [[sum((falling(p, i) * max(abs(x) for x in self.s[r][p]) * tmax ** (p - i)
                    for p in range(i, DEG + 1)), Fr(0)) for i in range(5)] for r in range(5)]
        return {"C": 1 / (1 - k[0]), "k": k, "TS": TS}


# ------------------------------------------------------------------ trial construction
def random_system(seed: int, n: int, centre: Fr = Fr(0)) -> System:
    g = Rng(seed)
    A_ = []
    for p in range(DEG + 1):
        scale_ = Fr(1, 4 * n) if p == 0 else Fr(1, 24 * n * factorial(p))
        A_.append([[g.frac(1000, 1000) * scale_ for _ in range(n)] for _ in range(n)])
    s = [[[g.frac(1000, 1000) / factorial(p) for _ in range(n)] for p in range(DEG + 1)] for _ in range(5)]
    return System(n, A_, s, centre)


def scalar_controlled(kind: str, e0: Fr) -> System:
    """Scalar systems centred at e0 where the norm constants are nearly attained.

    kind "K1": K = 3/10 + (1/5)(e-e0) + (1/20)(e-e0)^2 + (1/30)(e-e0)^3     (all coefficients positive)
    kind "K3": K = 3/10 + (1/6)(e-e0)^3 + (1/24)(e-e0)^4                    (K_1(e0) = K_2(e0) = 0)
    """
    coeffs = {"K1": [Fr(3, 10), Fr(1, 5), Fr(1, 20), Fr(1, 30), Fr(0), Fr(0)],
              "K3": [Fr(3, 10), Fr(0), Fr(0), Fr(1, 6), Fr(1, 24), Fr(0)]}[kind]
    A_ = [[[c]] for c in coeffs]
    s = [[[Fr(1 + r, p + 1) * (1 if (r + p) % 2 == 0 else -1)] for p in range(DEG + 1)] for r in range(5)]
    return System(1, A_, s, e0)


def cell_inputs(sysm: System, e0: Fr, rho: Fr, *, perturb: dict | None = None, seed: int = 0,
                noise: Fr = Fr(0)) -> tuple[dict, dict]:
    """Candidates at e0 plus certified inputs, in the shape order3_algebra.cell_order3 consumes.

    noise > 0 : every candidate is truth + independent LCG noise of that size (general soundness)
    perturb   : {"F": (order, eta)} perturbs one F order of every r by eta; the higher F orders are then re-solved
                EXACTLY from the perturbed lower ones, so the error enters only through the propagation edges
    """
    truth = sysm.true_objects(e0, 3)
    g = Rng(seed + 7919)
    nz = (lambda v: [x + g.frac(1000, 1000) * noise for x in v]) if noise else (lambda v: list(v))
    Kd = [sysm.K_deriv(i, e0) for i in range(4)]
    I_K0 = [[(Fr(1) if a == b else Fr(0)) - Kd[0][a][b] for b in range(sysm.n)] for a in range(sysm.n)]

    Shat = [[nz(sysm.S_deriv(r, q, e0)) for q in range(4)] for r in range(5)]
    Fhat = []
    for r in range(5):
        rows = []
        for q in range(4):
            if perturb and "F" in perturb:
                order, eta = perturb["F"]
                if q < order:
                    v = list(truth[("F", r)][q])
                elif q == order:
                    v = [x + eta for x in truth[("F", r)][q]]
                else:
                    rhs = list(Shat[r][q])
                    for i in range(1, q + 1):
                        rhs = A.add(rhs, A.scale(comb(q, i), matvec(Kd[i], rows[q - i])))
                    v = solve(I_K0, rhs)
            else:
                v = nz(truth[("F", r)][q])
            rows.append(v)
        Fhat.append(rows)
    What = {(r, j): [nz(truth[("W", (r, j))][q]) for q in range(4)] for (r, j) in A.W_INDICES}
    epsS = [[A.norm(A.sub(Shat[r][q], sysm.S_deriv(r, q, e0))) for q in range(4)] for r in range(5)]
    nrm = sysm.cell_norms(e0, rho)
    inp = {"rho": rho, "C": nrm["C"], "k": nrm["k"], "TS": nrm["TS"], "epsS": epsS,
           "Fhat": Fhat, "Shat": Shat, "What": What,
           "Kapply": lambda i, v: matvec(Kd[i], v)}
    return inp, truth
