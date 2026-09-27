"""Exact synthetic fixtures for non-target validation (stdlib ``fractions`` only).

A *finite-state drift family* is a sub-Markov kernel K(e) on n states whose entries are
polynomials in the drift parameter e.  Everything the K5 tail theorems talk about is then an
exact rational object:

    R_e      = (I - K(e))^{-1}                      (resolvent)
    K_i(e)   = d^i/de^i K(e)                        (exact polynomial derivatives)
    dR       = R K_1 R,   d2R = 2 R K_1 R K_1 R + R K_2 R
    F(e)     = R_e S(e),  F', F'', F''' by the Leibniz identities
    atom     = state 0

so every bound (operator constants, Taylor-cell enclosures, transport clauses, residual-specific
majorants) can be checked against the exact truth.  None of these fixtures is a CUSUM cell; they
carry no target information.
"""
from __future__ import annotations

import random
from fractions import Fraction as F
from math import comb

Vec = list
Mat = list


# ----------------------------------------------------------------------------- linear algebra

def mat_zero(n: int, m: int | None = None) -> Mat:
    return [[F(0)] * (n if m is None else m) for _ in range(n)]


def mat_id(n: int) -> Mat:
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def mat_add(A: Mat, B: Mat, s: F = F(1)) -> Mat:
    return [[a + s * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_scale(A: Mat, s) -> Mat:
    return [[s * a for a in r] for r in A]


def mat_mul(A: Mat, B: Mat) -> Mat:
    Bt = list(zip(*B))
    return [[sum((a * b for a, b in zip(r, c)), F(0)) for c in Bt] for r in A]


def mat_vec(A: Mat, v: Vec) -> Vec:
    return [sum((a * x for a, x in zip(r, v)), F(0)) for r in A]


def vec_add(u: Vec, v: Vec, s: F = F(1)) -> Vec:
    return [a + s * b for a, b in zip(u, v)]


def sup_norm(v: Vec) -> F:
    return max(abs(x) for x in v)


def op_norm(A: Mat) -> F:
    """Operator norm on (R^n, sup): max absolute row sum (exact)."""
    return max(sum(abs(a) for a in r) for r in A)


def mat_inv(A: Mat) -> Mat:
    n = len(A)
    M = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [x / piv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]


# ----------------------------------------------------------------------------- polynomial entries

def poly_eval(c: list, x: F) -> F:
    acc = F(0)
    for a in reversed(c):
        acc = acc * x + a
    return acc


def poly_deriv(c: list, k: int = 1) -> list:
    for _ in range(k):
        c = [i * c[i] for i in range(1, len(c))] or [F(0)]
    return c


class DriftFamily:
    """K(e)[i][j] = poly_{ij}(e), S(e)[i] = spoly_i(e); atom = state 0."""

    def __init__(self, kpolys: list, spolys: list, e_range: tuple):
        self.kp = kpolys
        self.sp = spolys
        self.n = len(kpolys)
        self.e_lo, self.e_hi = F(e_range[0]), F(e_range[1])

    def K(self, e: F, i: int = 0) -> Mat:
        return [[poly_eval(poly_deriv(p, i), e) for p in row] for row in self.kp]

    def S(self, e: F, i: int = 0) -> Vec:
        return [poly_eval(poly_deriv(p, i), e) for p in self.sp]

    def R(self, e: F) -> Mat:
        return mat_inv(mat_add(mat_id(self.n), self.K(e), F(-1)))

    def F_derivs(self, e: F, upto: int = 4) -> list:
        """[F, F', ..., F^(upto)] at e, exactly, from (I-K)F = S and Leibniz."""
        R = self.R(e)
        Ks = [self.K(e, i) for i in range(upto + 1)]
        out: list = []
        for n in range(upto + 1):
            rhs = self.S(e, n)
            for i in range(1, n + 1):
                rhs = vec_add(rhs, mat_vec(Ks[i], out[n - i]), F(comb(n, i)))
            out.append(mat_vec(R, rhs))
        return out

    def check_substochastic(self, samples: int = 9) -> bool:
        for t in range(samples):
            e = self.e_lo + (self.e_hi - self.e_lo) * F(t, samples - 1)
            Ke = self.K(e)
            if any(a < 0 for r in Ke for a in r):
                return False
            if any(sum(r) >= 1 for r in Ke):
                return False
        return True


def random_family(n: int, seed: int, *, e_range=(F(0), F(1, 4)), deg: int = 2,
                  kill: F = F(1, 5)) -> DriftFamily:
    """A random sub-Markov drift family (deterministic from the seed).

    Base kernel rows are random probability vectors scaled by (1 - kill_i); each entry gets small
    random polynomial drift terms bounded so that entries stay positive and rows stay < 1 on the
    e-range (verified by sampling AND by an exact worst-case bound below).
    """
    rng = random.Random(seed)
    kp = []
    for i in range(n):
        w = [F(rng.randint(1, 20)) for _ in range(n)]
        s = sum(w)
        k_i = kill + (F(1) - kill) * F(rng.randint(0, 10), 40)
        base = [x / s * (1 - k_i) for x in w]
        row = []
        for j in range(n):
            c = [base[j]]
            for d in range(1, deg + 1):
                c.append(base[j] * F(rng.randint(-10, 10), 40))
            row.append(c)
        kp.append(row)
    sp = [[F(rng.randint(-10, 10), 10) for _ in range(deg + 2)] for _ in range(n)]
    fam = DriftFamily(kp, sp, e_range)
    # exact worst case: |sum_d c_d e^d| <= sum_d |c_d| e_max^d
    em = max(abs(fam.e_lo), abs(fam.e_hi))
    for row in kp:
        tot = F(0)
        for c in row:
            drift = sum(abs(c[d]) * em ** d for d in range(1, len(c)))
            if c[0] - drift <= 0:
                raise ValueError("entry may become non-positive; shrink drift")
            tot += c[0] + drift
        if tot >= 1:
            raise ValueError("row may reach 1; increase kill")
    return fam


def _selftest() -> None:
    fam = random_family(5, seed=1)
    assert fam.check_substochastic()
    e = F(1, 8)
    R = fam.R(e)
    I = mat_mul(mat_add(mat_id(5), fam.K(e), F(-1)), R)
    assert I == mat_id(5)
    # dR = R K1 R against an exact symmetric difference quotient limit check (polynomial in h)
    Fd = fam.F_derivs(e, 3)
    h = F(1, 10 ** 6)
    Fp = fam.F_derivs(e + h, 0)[0]
    Fm = fam.F_derivs(e - h, 0)[0]
    approx = [(a - b) / (2 * h) for a, b in zip(Fp, Fm)]
    err = max(abs(a - b) for a, b in zip(approx, Fd[1]))
    assert err < F(1, 10 ** 8), float(err)
    print("ov_fixtures selftest PASS", float(err))


if __name__ == "__main__":
    _selftest()
