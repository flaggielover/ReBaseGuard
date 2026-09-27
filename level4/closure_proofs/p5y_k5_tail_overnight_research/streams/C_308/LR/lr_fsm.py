"""Stream C1a (LR / score representation of the atom constants) -- exact finite-state validation.

SYNTHETIC ONLY. Uses NS/code/ov_fixtures.py drift families (state 0 = atom) and two hand-built toy chains
(Examples E1d/E2 of THEOREM_LR.md). No CUSUM cell, no drift in the quarantined band (guard_drift at every entry).

State-level scores (THEOREM_LR §0): s(x,y) = K1[x][y]/K0[x][y], t(x,y) = K2[x][y]/K0[x][y] - s^2 on living transitions.
Moment kernels K^{(m)}[x][y] = K0[x][y] * s(x,y)^m  (K^{(1)} = K1).

Everything is exact rational arithmetic (fractions). sqrt only enters through verified directed rational bounds.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction as F
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
import ov_fixtures as X  # noqa: E402

VALID = NS / "validation"


# ----------------------------------------------------------------------------- small exact helpers

def sqrt_up(x: F) -> F:
    """Rational r >= sqrt(x), verified exactly (x >= 0)."""
    if x <= 0:
        return F(0)
    try:
        y = F(math.sqrt(float(x))) * (1 + F(1, 2 ** 40))
    except (OverflowError, ValueError):
        y = None
    if y is None or y * y < x:
        p, q = x.numerator, x.denominator
        s = 2 ** 64
        y = F(math.isqrt(p * q * s * s) + 1, q * s)
    assert y * y >= x
    return y


def sqrt_down(x: F) -> F:
    """Rational r <= sqrt(x), verified exactly (x >= 0)."""
    if x <= 0:
        return F(0)
    try:
        y = F(math.sqrt(float(x))) * (1 - F(1, 2 ** 40))
    except (OverflowError, ValueError):
        y = None
    if y is None or y * y > x or y < 0:
        p, q = x.numerator, x.denominator
        s = 2 ** 64
        y = F(math.isqrt(p * q * s * s), q * s)
    assert y * y <= x
    return y


def dyadic(x: F, bits: int = 30) -> F:
    """A short positive rational close to x (used only for tuning parameters; never a bound)."""
    if x <= 0:
        return F(1, 2 ** bits)
    return F(round(float(x) * 2 ** bits), 2 ** bits) or F(1, 2 ** bits)


def row_mat(u: list, A: list) -> list:
    """Row vector times matrix."""
    n = len(A[0])
    return [sum((u[i] * A[i][j] for i in range(len(u))), F(0)) for j in range(n)]


def dot(u, v):
    return sum((a * b for a, b in zip(u, v)), F(0))


def had(A, B):
    return [[a * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def absm(A):
    return [[abs(a) for a in r] for r in A]


# ----------------------------------------------------------------------------- chain object

class Chain:
    """Sub-Markov chain with state-level scores at one drift point (exact)."""

    def __init__(self, K0, K1, K2, atom: int = 0, label: str = ""):
        self.n = len(K0)
        self.K0, self.K1, self.K2 = K0, K1, K2
        self.atom = atom
        self.label = label
        n = self.n
        for x in range(n):
            for y in range(n):
                if K0[x][y] == 0 and (K1[x][y] != 0 or K2[x][y] != 0):
                    raise ValueError("derivative mass on a zero-density transition: score undefined")
        self.s = [[(K1[x][y] / K0[x][y]) if K0[x][y] else F(0) for y in range(n)] for x in range(n)]
        self.t = [[(K2[x][y] / K0[x][y] - self.s[x][y] ** 2) if K0[x][y] else F(0) for y in range(n)]
                  for x in range(n)]
        self.R = X.mat_inv(X.mat_add(X.mat_id(n), K0, F(-1)))
        self.one = [F(1)] * n
        self.R1 = X.mat_vec(self.R, self.one)
        self.Lam = self.R1[atom]

    def Kw(self, i: int, j: int):
        """Kernel with weight s^i t^j (state level)."""
        return [[self.K0[x][y] * self.s[x][y] ** i * self.t[x][y] ** j for y in range(self.n)] for x in range(self.n)]

    # -- exact moment totals U_{ij}(y) = E_a sum_{n<tau} M_n^i N_n^j 1{X_n=y}
    def moment_totals(self, maxdeg: int = 4, sign: int = 1, tsign: int = 1, plant=None) -> dict:
        """Row-vector linear solves U_{ij} = [delta_a 1{ij=00} + sum_lower C C U_{i'j'} K_{s^{i-i'} t^{j-j'}}] R.

        Negative-control hooks (REVIEW_GLOBAL_INTEGRITY_R1 C-10 repair; all act INSIDE this solver):
        ``sign`` = -1 flips the first-order score; ``tsign`` = -1 flips the second-order score t;
        ``plant`` = ((i, j), eps) adds eps at the atom entry of the (i, j) right-hand side before the solve."""
        n = self.n
        cache = {}

        def Kst(i, j):
            if (i, j) not in cache:
                cache[(i, j)] = [[self.K0[x][y] * (sign * self.s[x][y]) ** i * (tsign * self.t[x][y]) ** j
                                  for y in range(n)] for x in range(n)]
            return cache[(i, j)]

        U = {}
        keys = sorted([(i, j) for i in range(maxdeg + 1) for j in range(maxdeg // 2 + 1) if i + 2 * j <= maxdeg],
                      key=lambda ij: (ij[0] + 2 * ij[1], ij))
        for (i, j) in keys:
            rhs = [F(int(y == self.atom and i == 0 and j == 0)) for y in range(n)]
            for i2 in range(i + 1):
                for j2 in range(j + 1):
                    if (i2, j2) == (i, j):
                        continue
                    coef = comb(i, i2) * comb(j, j2)
                    contrib = row_mat(U[(i2, j2)], Kst(i - i2, j - j2))
                    rhs = [r + coef * c for r, c in zip(rhs, contrib)]
            if plant is not None and plant[0] == (i, j):
                rhs = [r + (plant[1] if y == self.atom else F(0)) for y, r in enumerate(rhs)]
            U[(i, j)] = row_mat(rhs, self.R)
        return U

    # -- forward per-time moments u_{ij,n}(y) = E_a[M_n^i N_n^j ; X_n = y, n<tau]
    def forward_moments(self, H: int, maxdeg: int = 4, keys=None):
        """keys must be closed under taking (i2<=i, j2<=j); default: all i + 2j <= maxdeg."""
        n = self.n
        if keys is None:
            keys = [(i, j) for i in range(maxdeg + 1) for j in range(maxdeg // 2 + 1) if i + 2 * j <= maxdeg]
        Kc = {}
        for i in range(maxdeg + 1):
            for j in range(maxdeg // 2 + 1):
                if i + 2 * j <= maxdeg:
                    Kc[(i, j)] = self.Kw(i, j)
        u = {k: [F(int(y == self.atom and k == (0, 0))) for y in range(n)] for k in keys}
        out = [u]
        for _ in range(H):
            nu = {}
            for (i, j) in keys:
                acc = [F(0)] * n
                for i2 in range(i + 1):
                    for j2 in range(j + 1):
                        coef = comb(i, i2) * comb(j, j2)
                        contrib = row_mat(u[(i2, j2)], Kc[(i - i2, j - j2)])
                        acc = [a + coef * c for a, c in zip(acc, contrib)]
                nu[(i, j)] = acc
            u = nu
            out.append(u)
        return out


# ----------------------------------------------------------------------------- certificates (THEOREM_LR §cert)

def check_quadratic_cert(ch: Chain, a, b1, b2, c, _mutant_drop_A: bool = False) -> dict:
    """Exact check of w = a + b1 mu + b2 mu^2 >= c(x)/2 + mu^2/(2c(x)) + P w for all mu (THEOREM_LR §cert (i')).

    c: list (state-dependent) of positive rationals. Returns per-state pass flags and the worst slack."""
    n = ch.n
    K, K1, K2s = ch.K0, ch.K1, ch.Kw(2, 0)
    Kb2 = X.mat_vec(K, b2)
    Kb1 = X.mat_vec(K, b1)
    Ka = X.mat_vec(K, a)
    K1b2 = X.mat_vec(K1, b2)
    K1b1 = X.mat_vec(K1, b1)
    K2b2 = X.mat_vec(K2s, b2)
    ok_all = True
    fails = []
    for x in range(n):
        A = b2[x] - 1 / (2 * c[x]) - Kb2[x]
        B = b1[x] - Kb1[x] - 2 * K1b2[x]
        C = a[x] - c[x] / 2 - Ka[x] - K1b1[x] - K2b2[x]
        ok = (_mutant_drop_A or A >= 0) and C >= 0 and B * B <= 4 * A * C
        if not ok:
            ok_all = False
            fails.append(x)
    nonneg = all(b2[x] >= 0 and b1[x] ** 2 <= 4 * a[x] * b2[x] for x in range(n))
    return {"pass": ok_all, "failed_states": fails, "w_nonnegative": nonneg}


def cert_delta(ch: Chain, c: F, delta: F):
    """Proposition C1 (b1 = 0): minimal b = beta R1, a = R[c/2 + K2s b + (K1 b)^2/delta]."""
    beta = 1 / (2 * c) + delta
    b = [beta * v for v in ch.R1]
    K1b = X.mat_vec(ch.K1, b)
    K2b = X.mat_vec(ch.Kw(2, 0), b)
    forcing = [c / 2 + k2 + k1 * k1 / delta for k1, k2 in zip(K1b, K2b)]
    a = X.mat_vec(ch.R, forcing)
    return a, [F(0)] * ch.n, b


def cert_full(ch: Chain, cvec: list):
    """(i') exact minimal quadratic solution for a state-dependent c(x)."""
    b2 = X.mat_vec(ch.R, [1 / (2 * cx) for cx in cvec])
    b1 = X.mat_vec(ch.R, [2 * v for v in X.mat_vec(ch.K1, b2)])
    K1b1 = X.mat_vec(ch.K1, b1)
    K2b2 = X.mat_vec(ch.Kw(2, 0), b2)
    a = X.mat_vec(ch.R, [cx / 2 + p + q for cx, p, q in zip(cvec, K1b1, K2b2)])
    return a, b1, b2


# ----------------------------------------------------------------------------- per-seed analysis

A1_KEYS = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1)]
C_GRID = [F(2 ** k, 8) for k in range(7)]          # declared: multiples of c_hat
D_GRID = [F(1, 4), F(1, 2), F(1), F(2)]             # declared: multiples of 1/(2c)


def identity1_holds(U: dict, dR, a: int) -> bool:
    return U[(1, 0)] == dR[a]


def identity2_holds(U: dict, d2R, a: int) -> bool:
    return [p + q for p, q in zip(U[(2, 0)], U[(0, 1)])] == d2R[a]


def identity_checks(fam, ch: Chain, e: F) -> dict:
    """Theorem LR-1 on the fixture: U10 row == (R K1 R)[a], U20+U01 row == (d2R)[a]; independent checks."""
    Q.guard_drift(e)
    R, K1, K2 = ch.R, ch.K1, ch.K2
    dR = X.mat_mul(X.mat_mul(R, K1), R)
    d2R = X.mat_add(X.mat_scale(X.mat_mul(X.mat_mul(dR, K1), R), 2), X.mat_mul(X.mat_mul(R, K2), R))
    U = ch.moment_totals(4)
    a = ch.atom
    id1 = identity1_holds(U, dR, a)
    id2 = identity2_holds(U, d2R, a)
    # independent check 1: symmetric difference quotient of e -> R_e (exact rationals, error O(h^2))
    h = F(1, 10 ** 5)
    Rp, Rm = fam.R(e + h), fam.R(e - h)
    fd1 = [(p - q) / (2 * h) for p, q in zip(Rp[a], Rm[a])]
    fd2 = [(p - 2 * r + q) / (h * h) for p, r, q in zip(Rp[a], R[a], Rm[a])]
    err1 = max(abs(p - q) for p, q in zip(fd1, U[(1, 0)]))
    err2 = max(abs(p - q) for p, q in zip(fd2, [p + q for p, q in zip(U[(2, 0)], U[(0, 1)])]))
    # independent check 2: brute-force path enumeration over horizon Hp vs forward recursion
    Hp = 4 if ch.n <= 7 else 3
    fwd = ch.forward_moments(Hp, 2)
    enum1 = [F(0)] * ch.n
    enum2 = [F(0)] * ch.n
    paths = [((a,), F(1), F(0), F(0))]  # (path, prob, M, N)
    for step in range(Hp + 1):
        for (p, pr, M, N) in paths:
            y = p[-1]
            enum1[y] += pr * M
            enum2[y] += pr * (M * M + N)
        if step == Hp:
            break
        new = []
        for (p, pr, M, N) in paths:
            x = p[-1]
            for y in range(ch.n):
                new.append((p + (y,), pr * ch.K0[x][y], M + ch.s[x][y], N + ch.t[x][y]))
        paths = new
    rec1 = [sum((fwd[k][(1, 0)][y] for k in range(Hp + 1)), F(0)) for y in range(ch.n)]
    rec2 = [sum((fwd[k][(2, 0)][y] + fwd[k][(0, 1)][y] for k in range(Hp + 1)), F(0)) for y in range(ch.n)]
    enum_ok = (rec1 == enum1) and (rec2 == enum2)
    # negative controls, all THROUGH moment_totals and the same comparators as the real checks.
    # (the former `neg_t_flip`, a bare != on U20-U01, was class (d) and is withdrawn: REVIEW_GLOBAL_INTEGRITY_R1 C-10)
    Uneg = ch.moment_totals(2, sign=-1)
    neg1_detected = not identity1_holds(Uneg, dR, a)
    # guaranteed plant: +eps at the atom of the (0,1) rhs shifts U01 by eps*R[a,.], and R[a][a] >= 1 > 0
    Upl = ch.moment_totals(2, plant=((0, 1), F(1, 10 ** 9)))
    neg2_plant_detected = not identity2_holds(Upl, d2R, a)
    # t-sign flip inside the solver: fires iff U01 != 0 (not guaranteed; fire rate reported)
    Utf = ch.moment_totals(2, tsign=-1)
    neg2_tflip_detected = not identity2_holds(Utf, d2R, a)
    return {
        "identity1_exact": id1, "identity2_exact": id2,
        "fd_err1": float(err1), "fd_err2": float(err2), "fd_h": "1e-5",
        "fd_ok": err1 < F(1, 10 ** 6) and err2 < F(1, 10 ** 3),
        "path_enumeration_horizon": Hp, "path_enumeration_match": enum_ok,
        "neg_sign_flip_detected": neg1_detected, "neg2_plant_detected": neg2_plant_detected,
        "neg2_tflip_in_solver_detected": neg2_tflip_detected,
        "_U": U, "_dR": dR, "_d2R": d2R,
    }


def lr_bounds_A1(ch: Chain, U: dict, H_head: int, H_lb: int, fwd=None) -> dict:
    """Certified upper bounds on A1^LR (several certificates) and a rigorous lower bound."""
    n = ch.n
    Lam = ch.Lam
    S2 = sum(U[(2, 0)])
    c_hat = dyadic(sqrt_up(S2 / Lam))
    out = {"Lambda": Lam, "S2": S2}
    # (i) delta-certificate over the declared grid
    best = None
    grid_rec = []
    for cm in C_GRID:
        c = c_hat * cm
        for dm in D_GRID:
            delta = dm / (2 * c)
            a, b1, b2 = cert_delta(ch, c, delta)
            chk = check_quadratic_cert(ch, a, b1, b2, [c] * n)
            val = a[ch.atom]
            grid_rec.append((float(cm), float(dm), float(val), chk["pass"]))
            if chk["pass"] and (best is None or val < best[0]):
                best = (val, c, delta, a, b2)
    out["delta_cert"] = best[0]
    out["delta_cert_params"] = {"c": str(best[1]), "delta": str(best[2])}
    out["delta_grid_all_pass"] = all(r[3] for r in grid_rec)
    out["delta_grid_size"] = len(grid_rec)
    a_best, b_best, c_best, d_best = best[3], best[4], best[1], best[2]
    neg = {}
    # (i') full quadratic, global c = c_hat (exact minimal solution)
    a2, b12, b22 = cert_full(ch, [c_hat] * n)
    chk2 = check_quadratic_cert(ch, a2, b12, b22, [c_hat] * n)
    out["full_global"] = a2[ch.atom]
    out["full_global_pass"] = chk2["pass"]
    out["full_global_formula_match"] = a2[ch.atom] == c_hat * Lam / 2 + S2 / (2 * c_hat)
    out["sqrt_Lam_S2_lower"] = sqrt_down(Lam * S2)
    # planted linear-term perturbation must break the exact solution (B^2 <= 4AC with A = C = 0)
    b12_bad = list(b12)
    b12_bad[ch.atom] += F(1, 10 ** 6)
    neg["b1_perturbed_rejected"] = not check_quadratic_cert(ch, a2, b12_bad, b22, [c_hat] * n)["pass"]
    # (i') per-state c(y) = dyadic sqrt(U2/U0)
    U0, U2 = U[(0, 0)], U[(2, 0)]
    cvec = [dyadic(sqrt_up(U2[y] / U0[y])) if U0[y] > 0 and U2[y] > 0 else F(1) for y in range(n)]
    a3, b13, b23 = cert_full(ch, cvec)
    chk3 = check_quadratic_cert(ch, a3, b13, b23, cvec)
    formula = sum((cvec[y] * U0[y] / 2 + U2[y] / (2 * cvec[y]) for y in range(n)), F(0))
    out["full_perstate"] = a3[ch.atom]
    out["full_perstate_pass"] = chk3["pass"]
    out["full_perstate_formula_match"] = a3[ch.atom] == formula
    out["full_perstate_w_nonneg"] = chk3["w_nonnegative"]
    # (iii) finite horizon head per-(n,y) CS + certified tail with the per-state certificate
    if fwd is None:
        fwd = ch.forward_moments(max(H_head, H_lb), 4, keys=A1_KEYS)
    head = F(0)
    for k in range(H_head):
        for y in range(n):
            head += sqrt_up(fwd[k][(0, 0)][y] * fwd[k][(2, 0)][y])
    uH = fwd[H_head]
    tail = sum((a3[y] * uH[(0, 0)][y] + b13[y] * uH[(1, 0)][y] + b23[y] * uH[(2, 0)][y] for y in range(n)), F(0))
    out["horizon_cert"] = head + tail
    out["horizon_H"] = H_head
    # (iv) rigorous lower bound: per-(n,y) Holder, n < H_lb
    lb = F(0)
    for k in range(H_lb):
        for y in range(n):
            u2, u4 = fwd[k][(2, 0)][y], fwd[k][(4, 0)][y]
            if u2 > 0 and u4 > 0:
                lb += u2 * sqrt_down(u2) / sqrt_up(u4)
    out["lower_bound"] = lb
    out["lower_H"] = H_lb
    # negative controls on the checker: planted NON-supersolutions (each must be rejected)
    z = [F(0)] * n
    a_bad = [v * (1 - F(1, 1000)) for v in a_best]
    neg["a_scaled_down_rejected"] = not check_quadratic_cert(ch, a_bad, z, b_best, [c_best] * n)["pass"]
    K1b = X.mat_vec(ch.K1, b_best)
    K2b = X.mat_vec(ch.Kw(2, 0), b_best)
    a_wc = X.mat_vec(ch.R, [c_best / 4 + k2 + k1 * k1 / d_best for k1, k2 in zip(K1b, K2b)])
    neg["wrong_constant_rejected"] = not check_quadratic_cert(ch, a_wc, z, b_best, [c_best] * n)["pass"]
    # A < 0 plant (REVIEW_GLOBAL_INTEGRITY_R1 F7): b2 exact for c' = 2c (so A = 1/(4c) - 1/(2c) < 0), b1 exact from
    # b2 (B = 0), a solved with the checker's c (C = 0): ONLY the A >= 0 conjunct can reject it; w - g - Pw = A mu^2 < 0.
    cc = c_hat
    b2p = X.mat_vec(ch.R, [1 / (2 * (2 * cc))] * n)
    b1p = X.mat_vec(ch.R, [2 * v for v in X.mat_vec(ch.K1, b2p)])
    ap = X.mat_vec(ch.R, [cc / 2 + p + q for p, q in zip(X.mat_vec(ch.K1, b1p), X.mat_vec(ch.Kw(2, 0), b2p))])
    neg["A_negative_rejected"] = not check_quadratic_cert(ch, ap, b1p, b2p, [cc] * n)["pass"]
    neg["A_negative_passes_mutant_without_A_conjunct"] = check_quadratic_cert(
        ch, ap, b1p, b2p, [cc] * n, _mutant_drop_A=True)["pass"]
    if lb > 0:
        sc = lb / (2 * a_best[ch.atom])
        neg["below_lower_bound_rejected"] = not check_quadratic_cert(
            ch, [v * sc for v in a_best], z, [v * sc for v in b_best], [c_best] * n)["pass"]
    out["negative_controls_checker"] = neg
    out["best_cert"] = min(out["delta_cert"], out["full_global"], out["full_perstate"], out["horizon_cert"])
    out["_fwd"] = fwd
    return out


# ----------------------------------------------------------------------------- truth, PM, Lemma G, A2 bounds

def truth_pm_g(ch: Chain, dR, d2R) -> dict:
    a = ch.atom
    R, K1, K2 = ch.R, ch.K1, ch.K2
    one = ch.one
    C = X.op_norm(R)
    k1, k2 = X.op_norm(K1), X.op_norm(K2)
    w = ch.R1
    v = X.mat_vec(R, X.mat_vec(absm(K1), w))
    pm1 = v[a]
    pm2 = 2 * X.mat_vec(R, X.mat_vec(absm(K1), v))[a] + X.mat_vec(R, X.mat_vec(absm(K2), w))[a]
    return {
        "A0_true": ch.Lam, "A0_G": C,
        "A1_true": sum(abs(x) for x in dR[a]), "A1_PM": pm1, "A1_G": k1 * C * C,
        "A2_true": sum(abs(x) for x in d2R[a]), "A2_PM": pm2, "A2_G": k2 * C * C + 2 * k1 * k1 * C ** 3,
        "dLam": sum(dR[a]), "d2Lam": sum(d2R[a]),
    }


def lr_bounds_A2(ch: Chain, U: dict, fwd=None, H_lb: int = 0) -> dict:
    """Certified upper bounds on A2^LR: (ii-a) triangle S2 + T_N; (ii-b) per-state quartic CS (exact value)."""
    n, a = ch.n, ch.atom
    S2 = sum(U[(2, 0)])
    Kabs_t = [[ch.K0[x][y] * abs(ch.t[x][y]) for y in range(n)] for x in range(n)]
    TN = X.mat_vec(ch.R, X.mat_vec(Kabs_t, ch.R1))[a]
    U0 = U[(0, 0)]
    Q4 = [U[(4, 0)][y] + 2 * U[(2, 1)][y] + U[(0, 2)][y] for y in range(n)]
    cvec = [dyadic(sqrt_up(Q4[y] / U0[y])) if U0[y] > 0 and Q4[y] > 0 else F(1) for y in range(n)]
    quart = sum((cvec[y] * U0[y] / 2 + Q4[y] / (2 * cvec[y]) for y in range(n)), F(0))
    Lam = ch.Lam
    Q4tot = sum(Q4)
    out = {"tri": S2 + TN, "S2": S2, "T_N": TN, "quartic_perstate": quart,
           "quartic_global_lower": sqrt_down(Lam * Q4tot)}
    # rigorous lower bound on A2^LR: sum_{n<H,y} |E[M^2+N; X_n=y]| (Jensen)
    if fwd is not None and H_lb > 0:
        out["lower_bound"] = sum((abs(fwd[k][(2, 0)][y] + fwd[k][(0, 1)][y]) for k in range(H_lb) for y in range(n)),
                                 F(0))
    out["best_cert"] = min(out["tri"], out["quartic_perstate"])
    return out


def excursion(ch: Chain) -> "Chain":
    """Taboo chain: transitions into the atom removed (killed on entering a at time >= 1)."""
    a = ch.atom

    def cut(M):
        return [[(F(0) if y == a else M[x][y]) for y in range(ch.n)] for x in range(ch.n)]
    return Chain(cut(ch.K0), cut(ch.K1), cut(ch.K2), atom=a, label=ch.label + "/taboo")


def rlr_and_dv(ch: Chain, dR, d2R, H_head: int, H_lb: int) -> dict:
    """Theorem LR-3 (RLR) and Lemma Dv' with EXACT point inputs, plus the regenerative identity checks."""
    a, n = ch.atom, ch.n
    hc = excursion(ch)
    G = hc.R
    tau_a = hc.Lam
    C_T = X.op_norm(G)
    kap1, kap2 = X.op_norm(hc.K1), X.op_norm(hc.K2)
    ka = [ch.K0[x][a] for x in range(n)]
    ka1 = [ch.K1[x][a] for x in range(n)]
    ka2 = [ch.K2[x][a] for x in range(n)]
    h = X.mat_vec(G, ka)
    D = 1 - h[a]
    hp = X.mat_vec(G, X.vec_add(X.mat_vec(hc.K1, h), ka1))
    Dp = -hp[a]
    hpp = X.mat_vec(G, X.vec_add(X.vec_add(X.mat_vec(hc.K2, h), X.mat_vec(hc.K1, hp), F(2)), ka2))
    Dpp = -hpp[a]
    Lam = ch.Lam
    Uh = hc.moment_totals(4)
    nu, nu1 = Uh[(0, 0)], Uh[(1, 0)]
    nu2 = [p + q for p, q in zip(Uh[(2, 0)], Uh[(0, 1)])]
    reg1 = [p / D - q * Dp / D ** 2 for p, q in zip(nu1, nu)]
    reg2 = [p2 / D - 2 * p1 * Dp / D ** 2 + p0 * (2 * Dp ** 2 / D ** 3 - Dpp / D ** 2)
            for p0, p1, p2 in zip(nu, nu1, nu2)]
    checks = {
        "Lam_eq_tau_over_D": Lam == tau_a / D,
        "regenerative_identity1": reg1 == dR[a],
        "regenerative_identity2": reg2 == d2R[a],
        "nu1_eq_GK1G_row": nu1 == X.mat_mul(X.mat_mul(G, hc.K1), G)[a],
    }
    d1, d2 = abs(Dp) / D, abs(Dpp) / D
    A1_dv = Lam * (kap1 * C_T + d1)
    A2_dv = Lam * (2 * kap1 ** 2 * C_T ** 2 + kap2 * C_T + 2 * kap1 * C_T * d1 + 2 * d1 ** 2 + d2)
    b1 = lr_bounds_A1(hc, Uh, H_head, H_lb)
    b2 = lr_bounds_A2(hc, Uh, b1["_fwd"], H_lb)
    rho1 = b1["best_cert"] / tau_a
    rho2 = b2["best_cert"] / tau_a
    pmhat1 = X.mat_vec(G, X.mat_vec(absm(hc.K1), hc.R1))[a]
    pmhat2 = (2 * X.mat_vec(G, X.mat_vec(absm(hc.K1), X.mat_vec(G, X.mat_vec(absm(hc.K1), hc.R1))))[a]
              + X.mat_vec(G, X.mat_vec(absm(hc.K2), hc.R1))[a])
    A1_rlr = Lam * (rho1 + d1)
    A2_rlr = Lam * (rho2 + 2 * rho1 * d1 + 2 * d1 ** 2 + d2)
    # Theorem LR-3 domination for the exact-PM ratios (must hold) and for the certified ratios (may fail)
    return {
        "tau_a": tau_a, "C_T": C_T, "kappa1": kap1, "kappa2": kap2, "D": D, "Dp": Dp, "Dpp": Dpp,
        "delta1": d1, "delta2": d2,
        "A1_Dv": A1_dv, "A2_Dv": A2_dv, "A1_RLR": A1_rlr, "A2_RLR": A2_rlr,
        "rho1_cert": rho1, "rho2_cert": rho2, "rho1_Dv": kap1 * C_T,
        "rho2_Dv": 2 * kap1 ** 2 * C_T ** 2 + kap2 * C_T,
        "L1_cert": b1["best_cert"], "L1_lower": b1["lower_bound"], "L2_cert": b2["best_cert"],
        "PMhat1_ratio": pmhat1 / tau_a, "PMhat2_ratio": pmhat2 / tau_a,
        "PMhat1_le_Dv": pmhat1 / tau_a <= kap1 * C_T,
        "PMhat2_le_Dv": pmhat2 / tau_a <= 2 * kap1 ** 2 * C_T ** 2 + kap2 * C_T,
        "excursion_cert_negcontrols": b1["negative_controls_checker"],
        "excursion_cert_pass": b1["full_perstate_pass"] and b1["full_global_pass"] and b1["delta_grid_all_pass"],
        "checks": checks,
    }


# ----------------------------------------------------------------------------- per-seed driver

def fl(x):
    return float(x) if isinstance(x, (F, int)) else x


def analyse_seed(seed: int, kill: F, e: F, H_head: int, H_lb: int) -> dict:
    Q.guard_drift(e)
    n = 6 + seed % 4
    fam = X.random_family(n, seed, e_range=(F(0), F(1, 4)), kill=kill)
    Q.guard_drift(fam.e_lo, fam.e_hi)
    assert fam.check_substochastic()
    ch = Chain(fam.K(e, 0), fam.K(e, 1), fam.K(e, 2), atom=0, label=f"seed{seed}")
    t0 = time.time()
    idc = identity_checks(fam, ch, e)
    U, dR, d2R = idc.pop("_U"), idc.pop("_dR"), idc.pop("_d2R")
    tp = truth_pm_g(ch, dR, d2R)
    b1 = lr_bounds_A1(ch, U, H_head, H_lb)
    fwd = b1.pop("_fwd")
    b2 = lr_bounds_A2(ch, U, fwd, H_lb)
    rd = rlr_and_dv(ch, dR, d2R, H_head, H_lb)
    A1_best = min(b1["best_cert"], rd["A1_RLR"], rd["A1_Dv"], tp["A1_G"])
    A2_best = min(b2["best_cert"], rd["A2_RLR"], rd["A2_Dv"], tp["A2_G"])
    chain1 = {
        "true_le_LRlower": tp["A1_true"] <= b1["lower_bound"] or None,  # informative only (LB may be < true)
        "LRlower_le_LRcert": b1["lower_bound"] <= b1["best_cert"],
        "true_le_LRcert": tp["A1_true"] <= b1["best_cert"],
        "LRcert_le_PM": b1["best_cert"] <= tp["A1_PM"],
        "PM_le_G": tp["A1_PM"] <= tp["A1_G"],
        "true_le_RLR": tp["A1_true"] <= rd["A1_RLR"],
        "true_le_Dv": tp["A1_true"] <= rd["A1_Dv"],
    }
    chain2 = {
        "true_le_LRlower": tp["A2_true"] <= b2.get("lower_bound", F(0)) or None,
        "LRlower_le_LRcert": b2.get("lower_bound", F(0)) <= b2["best_cert"],
        "true_le_LRcert": tp["A2_true"] <= b2["best_cert"],
        "LRcert_le_PM": b2["best_cert"] <= tp["A2_PM"],
        "PM_le_G": tp["A2_PM"] <= tp["A2_G"],
        "true_le_RLR": tp["A2_true"] <= rd["A2_RLR"],
        "true_le_Dv": tp["A2_true"] <= rd["A2_Dv"],
    }
    rec = {
        "seed": seed, "n": n, "kill": str(kill), "e": str(e),
        "identity": idc,
        "A0": {"true": fl(tp["A0_true"]), "G": fl(tp["A0_G"])},
        "A1": {"true": fl(tp["A1_true"]), "LR_lower": fl(b1["lower_bound"]),
               "LR_delta_cert": fl(b1["delta_cert"]), "LR_full_global": fl(b1["full_global"]),
               "LR_full_perstate": fl(b1["full_perstate"]), "LR_horizon": fl(b1["horizon_cert"]),
               "LR_cert_best": fl(b1["best_cert"]), "sqrt_Lam_S2": fl(b1["sqrt_Lam_S2_lower"]),
               "PM": fl(tp["A1_PM"]), "G": fl(tp["A1_G"]), "Dv_exact_inputs": fl(rd["A1_Dv"]),
               "RLR": fl(rd["A1_RLR"]), "best_valid": fl(A1_best), "abs_dLam": fl(abs(tp["dLam"]))},
        "A2": {"true": fl(tp["A2_true"]), "LR_lower": fl(b2.get("lower_bound", F(0))),
               "LR_tri": fl(b2["tri"]), "LR_quartic_perstate": fl(b2["quartic_perstate"]),
               "LR_cert_best": fl(b2["best_cert"]), "PM": fl(tp["A2_PM"]), "G": fl(tp["A2_G"]),
               "Dv_exact_inputs": fl(rd["A2_Dv"]), "RLR": fl(rd["A2_RLR"]), "best_valid": fl(A2_best),
               "abs_d2Lam": fl(abs(tp["d2Lam"]))},
        "cert_checks": {
            "delta_grid_all_pass": b1["delta_grid_all_pass"], "delta_grid_size": b1["delta_grid_size"],
            "delta_best_params": b1["delta_cert_params"],
            "full_global_pass": b1["full_global_pass"], "full_global_formula_match": b1["full_global_formula_match"],
            "full_perstate_pass": b1["full_perstate_pass"],
            "full_perstate_formula_match": b1["full_perstate_formula_match"],
            "full_perstate_w_nonneg": b1["full_perstate_w_nonneg"],
            "negative_controls": b1["negative_controls_checker"],
            "H_head": H_head, "H_lb": H_lb,
        },
        "rlr_dv": {k: (fl(v) if isinstance(v, F) else v) for k, v in rd.items()},
        "chain_A1": chain1, "chain_A2": chain2,
        "seconds": round(time.time() - t0, 2),
    }
    return rec



# ----------------------------------------------------------------------------- summaries and main

def ratio_stats(vals):
    vals = [v for v in vals if v is not None]
    return {"min": min(vals), "max": max(vals), "median": sorted(vals)[len(vals) // 2]} if vals else None


def summarise(recs: list) -> dict:
    keys1 = ["LRlower_le_LRcert", "true_le_LRcert", "LRcert_le_PM", "PM_le_G", "true_le_RLR", "true_le_Dv"]
    out = {"seeds": len(recs)}
    for tag in ("chain_A1", "chain_A2"):
        out[tag + "_holds"] = {k: sum(1 for r in recs if r[tag][k]) for k in keys1}
    idk = ["identity1_exact", "identity2_exact", "fd_ok", "path_enumeration_match", "neg_sign_flip_detected",
           "neg2_plant_detected", "neg2_tflip_in_solver_detected"]
    out["identity_counts"] = {k: sum(1 for r in recs if r["identity"][k]) for k in idk}
    nck = ["b1_perturbed_rejected", "a_scaled_down_rejected", "wrong_constant_rejected", "below_lower_bound_rejected",
           "A_negative_rejected", "A_negative_passes_mutant_without_A_conjunct"]
    out["checker_negative_controls_detected"] = {
        k: sum(1 for r in recs if r["cert_checks"]["negative_controls"].get(k)) for k in nck}
    out["checker_negative_controls_detected_excursion"] = {
        k: sum(1 for r in recs if r["rlr_dv"]["excursion_cert_negcontrols"].get(k)) for k in nck}
    out["cert_pass_counts"] = {
        "delta_grid_all_pass": sum(1 for r in recs if r["cert_checks"]["delta_grid_all_pass"]),
        "full_global_pass": sum(1 for r in recs if r["cert_checks"]["full_global_pass"]),
        "full_perstate_pass": sum(1 for r in recs if r["cert_checks"]["full_perstate_pass"]),
        "formula_matches": sum(1 for r in recs if r["cert_checks"]["full_global_formula_match"]
                               and r["cert_checks"]["full_perstate_formula_match"]),
        "excursion_cert_pass": sum(1 for r in recs if r["rlr_dv"]["excursion_cert_pass"]),
    }
    out["regenerative_checks"] = {k: sum(1 for r in recs if r["rlr_dv"]["checks"][k])
                                  for k in recs[0]["rlr_dv"]["checks"]}
    out["PMhat_le_Dv_counts"] = {"A1": sum(1 for r in recs if r["rlr_dv"]["PMhat1_le_Dv"]),
                                 "A2": sum(1 for r in recs if r["rlr_dv"]["PMhat2_le_Dv"])}
    for A in ("A1", "A2"):
        R = {}
        for lab in ("LR_lower", "LR_cert_best", "PM", "G", "Dv_exact_inputs", "RLR", "best_valid"):
            R[lab + "/true"] = ratio_stats([r[A][lab] / r[A]["true"] for r in recs])
        R["PM/LR_cert_best"] = ratio_stats([r[A]["PM"] / r[A]["LR_cert_best"] for r in recs])
        R["LR_cert_best/LR_lower"] = ratio_stats([r[A]["LR_cert_best"] / r[A]["LR_lower"] for r in recs
                                                  if r[A]["LR_lower"] > 0])
        R["Dv/RLR"] = ratio_stats([r[A]["Dv_exact_inputs"] / r[A]["RLR"] for r in recs])
        R["Dv/best_valid"] = ratio_stats([r[A]["Dv_exact_inputs"] / r[A]["best_valid"] for r in recs])
        R["count_LRcert_lt_Dv"] = sum(1 for r in recs if r[A]["LR_cert_best"] < r[A]["Dv_exact_inputs"])
        R["count_RLR_lt_Dv"] = sum(1 for r in recs if r[A]["RLR"] < r[A]["Dv_exact_inputs"])
        R["count_LRcert_lt_RLR"] = sum(1 for r in recs if r[A]["LR_cert_best"] < r[A]["RLR"])
        out[A + "_ratios"] = R
    out["A0_G/true"] = ratio_stats([r["A0"]["G"] / r["A0"]["true"] for r in recs])
    out["Lambda_range"] = ratio_stats([r["A0"]["true"] for r in recs])
    return out


def run_sets():
    e = F(1, 8)
    Q.guard_drift(e)
    res = {"schema": "C1LR_FSM_VALIDATION/1", "producer": "streams/C_308/LR/lr_fsm.py (run_sets)",
           "declared_rule": ("V1: ov_fixtures.random_family(n=6+seed%4, seed, e_range=(0,1/4), kill=1/20), seeds 1..12;"
                             " V2: same with kill=1/5; drift e=1/8; H_head=12, H_lb=80; certificate grids "
                             "c in {2^k/8, k=0..6}*c_hat, delta in {1/4,1/2,1,2}/(2c). Declared in PROGRESS.md before"
                             " running; all seeds reported."),
           "class": "SYNTHETIC_VALIDATION", "cells_touched": []}
    for name, kill in (("V1", F(1, 20)), ("V2", F(1, 5))):
        recs = []
        for seed in range(1, 13):
            recs.append(analyse_seed(seed, kill, e, 12, 80))
            print(name, seed, recs[-1]["seconds"], flush=True)
        res[name] = {"records": recs, "summary": summarise(recs)}
    VALID.mkdir(exist_ok=True)
    (VALID / "C1LR_FSM_VALIDATION.json").write_text(json.dumps(res, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --sets", "C1a LR identity + certificate exact validation on "
                    "synthetic drift-family fixtures (V1 kill=1/20, V2 kill=1/5, seeds 1..12, e=1/8)",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    return res



# ----------------------------------------------------------------------------- Examples E1d / E2 (THEOREM_LR §5.2)

EPS_LADDER = [F(1, 10), F(1, 20), F(1, 40), F(1, 80), F(1, 160)]   # declared in PROGRESS.md before running


def fam_E1d(eps: F) -> "X.DriftFamily":
    """One-state chain with 3-point noise, lifted to 3 copies (state-level score of the lift = noise score)."""
    c = (1 - eps) / 3
    row = [[c, c], [c, -c], [c, c / 2]]
    return X.DriftFamily([row, row, row], [[F(0)], [F(0)], [F(0)]], (F(0), F(0)))


def fam_E2(eps: F) -> "X.DriftFamily":
    h = (1 - eps) / 2
    return X.DriftFamily([[[h, h], [h, -h]], [[1 - eps], [F(0)]]], [[F(0)], [F(0)]], (F(0), F(0)))


def run_examples():
    e = F(0)
    Q.guard_drift(e)
    out = {"schema": "C1LR_EXAMPLES/1", "producer": "streams/C_308/LR/lr_fsm.py (run_examples)",
           "declared_rule": "eps ladder {1/10,1/20,1/40,1/80,1/160}, e=0, lower-bound horizon H=4/eps (PROGRESS.md)",
           "class": "SYNTHETIC_VALIDATION", "cells_touched": [], "E1d": [], "E2": []}
    for eps in EPS_LADDER:
        H = int(4 / eps)
        # E1d: original one-state chain in closed form; LR_noise from the lifted chain
        fam = fam_E1d(eps)
        ch = Chain(fam.K(e, 0), fam.K(e, 1), fam.K(e, 2), atom=0, label="E1d")
        pi = sum(ch.K0[0])
        pi1 = sum(ch.K1[0])
        pi2 = sum(ch.K2[0])
        Lam = 1 / (1 - pi)
        true1 = abs(pi1) * Lam ** 2
        true2 = abs(pi2 * Lam ** 2 + 2 * pi1 ** 2 * Lam ** 3)
        D, Dp, Dpp = 1 - pi, -pi1, -pi2
        dv1 = Lam * abs(Dp) / D
        dv2 = Lam * (2 * (Dp / D) ** 2 + abs(Dpp) / D)
        U = ch.moment_totals(4)
        b1 = lr_bounds_A1(ch, U, 12, H)
        b1.pop("_fwd")
        rec = {"eps": str(eps), "Lambda": fl(Lam), "H_lb": H,
               "A1_true": fl(true1), "A1_Dv_exact": fl(dv1), "A1_LRstate_equals_true": True,
               "A1_LRnoise_lower": fl(b1["lower_bound"]), "A1_LRnoise_cert": fl(b1["best_cert"]),
               "ratio_LRnoise_lower_over_Dv": fl(b1["lower_bound"] / dv1),
               "LRnoise_lower_over_Lambda^1.5": fl(b1["lower_bound"]) / fl(Lam) ** 1.5,
               "Dv_equals_true": dv1 == true1 and dv2 == true2,
               "LB_gt_Dv": b1["lower_bound"] > dv1}
        out["E1d"].append(rec)
        print("E1d", rec["eps"], rec["ratio_LRnoise_lower_over_Dv"], flush=True)
        # E2: two-state chain, state-level scores; full analysis
        fam = fam_E2(eps)
        ch = Chain(fam.K(e, 0), fam.K(e, 1), fam.K(e, 2), atom=0, label="E2")
        idc = identity_checks(fam, ch, e)
        U, dR, d2R = idc.pop("_U"), idc.pop("_dR"), idc.pop("_d2R")
        tp = truth_pm_g(ch, dR, d2R)
        b1 = lr_bounds_A1(ch, U, 12, H)
        fwd = b1.pop("_fwd")
        rd = rlr_and_dv(ch, dR, d2R, 12, H)
        rec2 = {"eps": str(eps), "Lambda": fl(ch.Lam), "H_lb": H, "identity": idc,
                "A1_true": fl(tp["A1_true"]), "A1_LR_lower": fl(b1["lower_bound"]), "A1_LR_cert": fl(b1["best_cert"]),
                "A1_PM": fl(tp["A1_PM"]), "A1_G": fl(tp["A1_G"]), "A1_Dv_exact": fl(rd["A1_Dv"]),
                "A1_RLR": fl(rd["A1_RLR"]), "C_T": fl(rd["C_T"]), "delta1": fl(rd["delta1"]),
                "ratio_LR_lower_over_Dv": fl(b1["lower_bound"] / rd["A1_Dv"]),
                "LR_lower_over_Lambda^1.5": fl(b1["lower_bound"]) / fl(ch.Lam) ** 1.5,
                "LB_gt_Dv": b1["lower_bound"] > rd["A1_Dv"], "regenerative_checks": rd["checks"]}
        out["E2"].append(rec2)
        print("E2", rec2["eps"], rec2["ratio_LR_lower_over_Dv"], flush=True)
    VALID.mkdir(exist_ok=True)
    (VALID / "C1LR_EXAMPLES.json").write_text(json.dumps(out, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --examples", "C1a Examples E1d/E2: plain LR vs Dv' order separation "
                    "(synthetic toy chains, e=0)", cells_touched=[], klass="SYNTHETIC_VALIDATION")
    return out



def fam_E1dp(eps: F) -> "X.DriftFamily":
    """E1d' (declared after E1d's design error): D = eps(1+e), bounded delta1 = 1/(1+e)."""
    c = (1 - eps) / 3
    row = [[c, F(1, 3)], [c, F(-1, 3)], [c, -eps]]
    return X.DriftFamily([row, row, row], [[F(0)], [F(0)], [F(0)]], (F(0), F(0)))


def run_example_E1dp():
    e = F(0)
    Q.guard_drift(e)
    out = []
    for eps in EPS_LADDER:
        H = int(4 / eps)
        fam = fam_E1dp(eps)
        ch = Chain(fam.K(e, 0), fam.K(e, 1), fam.K(e, 2), atom=0, label="E1dp")
        pi, pi1, pi2 = sum(ch.K0[0]), sum(ch.K1[0]), sum(ch.K2[0])
        Lam = 1 / (1 - pi)
        true1 = abs(pi1) * Lam ** 2
        D, Dp, Dpp = 1 - pi, -pi1, -pi2
        dv1 = Lam * abs(Dp) / D
        U = ch.moment_totals(4)
        b1 = lr_bounds_A1(ch, U, 12, H)
        b1.pop("_fwd")
        rec = {"eps": str(eps), "Lambda": fl(Lam), "H_lb": H, "delta1": fl(abs(Dp) / D),
               "A1_true": fl(true1), "A1_Dv_exact": fl(dv1), "Dv_equals_true": dv1 == true1,
               "A1_LRnoise_lower": fl(b1["lower_bound"]), "A1_LRnoise_cert": fl(b1["best_cert"]),
               "ratio_LRnoise_lower_over_Dv": fl(b1["lower_bound"] / dv1),
               "LRnoise_lower_over_Lambda^1.5": fl(b1["lower_bound"]) / fl(Lam) ** 1.5,
               "LB_gt_Dv": b1["lower_bound"] > dv1,
               "checker_negative_controls": b1["negative_controls_checker"]}
        out.append(rec)
        print("E1dp", {k: rec[k] for k in rec if k != "checker_negative_controls"}, flush=True)
    path = VALID / "C1LR_EXAMPLES.json"
    doc = json.loads(path.read_text())
    doc["E1d_prime"] = out
    doc["E1d_note"] = ("E1d as declared has delta1 = |D'|/D ~ Lambda/6 (design error: O(1) killing derivative), so no "
                       "separation is expected (ratio ~ sqrt(Lambda)/delta1); preserved. E1d_prime (declared after, "
                       "before running) has delta1 = 1.")
    path.write_text(json.dumps(doc, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --example-e1dp", "C1a Example E1d': noise-level LR vs Dv' with "
                    "bounded delta1 (synthetic, e=0)", cells_touched=[], klass="SYNTHETIC_VALIDATION")
    return out



# ----------------------------------------------------------------------------- block uniformity (THEOREM_LR §6)

def ipoly(c: list, lo: F, hi: F):
    """Interval Horner enclosure of sum c_d e^d over e in [lo, hi] (exact rationals)."""
    alo = ahi = F(0)
    for coef in reversed(c):
        ps = (alo * lo, alo * hi, ahi * lo, ahi * hi)
        alo, ahi = min(ps) + coef, max(ps) + coef
    return alo, ahi


def imatvec(Mi, v):
    """Interval matrix (lo, hi pairs) times exact vector -> list of (lo, hi)."""
    out = []
    for row in Mi:
        lo = hi = F(0)
        for (ml, mh), x in zip(row, v):
            if x >= 0:
                lo += ml * x
                hi += mh * x
            else:
                lo += mh * x
                hi += ml * x
        out.append((lo, hi))
    return out


def block_enclosures(fam, lo: F, hi: F):
    Q.guard_drift(lo, hi)
    n = fam.n
    K0 = [[ipoly(p, lo, hi) for p in row] for row in fam.kp]
    K1 = [[ipoly(X.poly_deriv(p, 1), lo, hi) for p in row] for row in fam.kp]
    K2s = []
    for x in range(n):
        r = []
        for y in range(n):
            (l1, h1), (l0, h0) = K1[x][y], K0[x][y]
            assert l0 > 0
            sq_lo = F(0) if l1 <= 0 <= h1 else min(l1 * l1, h1 * h1)
            sq_hi = max(l1 * l1, h1 * h1)
            r.append((sq_lo / h0, sq_hi / l0))
        K2s.append(r)
    return K0, K1, K2s


def check_block_cert(encs, a, b1, b2, c) -> dict:
    """Checker: for every sub-interval J and state x, A_lo >= 0, C_lo >= 0, max B^2 <= 4 A_lo C_lo."""
    worst = None
    for (K0, K1, K2s) in encs:
        Kb2, Kb1, Ka = imatvec(K0, b2), imatvec(K0, b1), imatvec(K0, a)
        K1b2, K1b1, K2b2 = imatvec(K1, b2), imatvec(K1, b1), imatvec(K2s, b2)
        for x in range(len(a)):
            A_lo = b2[x] - 1 / (2 * c[x]) - Kb2[x][1]
            B_lo = b1[x] - Kb1[x][1] - 2 * K1b2[x][1]
            B_hi = b1[x] - Kb1[x][0] - 2 * K1b2[x][0]
            C_lo = a[x] - c[x] / 2 - Ka[x][1] - K1b1[x][1] - K2b2[x][1]
            Bm = max(B_lo * B_lo, B_hi * B_hi)
            ok = A_lo >= 0 and C_lo >= 0 and Bm <= 4 * A_lo * C_lo
            if not ok:
                return {"pass": False, "first_failure_state": x}
            m = 4 * A_lo * C_lo - Bm
            worst = m if worst is None or m < worst else worst
    return {"pass": True, "min_discriminant_margin": worst}


def run_block(seeds=range(1, 9), m: int = 8, eta: F = F(1, 100)):
    lo_b, hi_b = F(0), F(1, 4)
    Q.guard_drift(lo_b, hi_b)
    out = {"schema": "C1LR_BLOCK/1", "producer": "streams/C_308/LR/lr_fsm.py (run_block)",
           "declared_rule": "V1 seeds 1..8, block [0,1/4], m=8, eta=1/100, grid e=k/32 k=0..8, LB horizon 60",
           "class": "SYNTHETIC_VALIDATION", "cells_touched": [], "records": []}
    for seed in seeds:
        n = 6 + seed % 4
        fam = X.random_family(n, seed, e_range=(lo_b, hi_b), kill=F(1, 20))
        subs = [(lo_b + (hi_b - lo_b) * F(k, m), lo_b + (hi_b - lo_b) * F(k + 1, m)) for k in range(m)]
        encs = [block_enclosures(fam, l, h) for (l, h) in subs]
        Kup = [[max(encs[k][0][x][y][1] for k in range(m)) for y in range(n)] for x in range(n)]
        assert all(sum(r) < 1 for r in Kup)
        Rup = X.mat_inv(X.mat_add(X.mat_id(n), Kup, F(-1)))
        em = (lo_b + hi_b) / 2
        chm = Chain(fam.K(em, 0), fam.K(em, 1), fam.K(em, 2), atom=0)
        Um = chm.moment_totals(2)
        U0, U2 = Um[(0, 0)], Um[(2, 0)]
        c = [dyadic(sqrt_up(U2[y] / U0[y])) if U0[y] > 0 and U2[y] > 0 else F(1) for y in range(n)]
        b2 = [(1 + eta) * v for v in X.mat_vec(Rup, [1 / (2 * cx) for cx in c])]
        b1 = X.mat_vec(chm.R, [2 * v for v in X.mat_vec(chm.K1, b2)])
        slack = [F(0)] * n
        Fx = [F(0)] * n
        for (K0, K1, K2s) in encs:
            Kb2, Kb1, K1b2 = imatvec(K0, b2), imatvec(K0, b1), imatvec(K1, b2)
            K1b1, K2b2 = imatvec(K1, b1), imatvec(K2s, b2)
            for x in range(n):
                A_lo = b2[x] - 1 / (2 * c[x]) - Kb2[x][1]
                B_lo = b1[x] - Kb1[x][1] - 2 * K1b2[x][1]
                B_hi = b1[x] - Kb1[x][0] - 2 * K1b2[x][0]
                slack[x] = max(slack[x], max(B_lo * B_lo, B_hi * B_hi) / (4 * A_lo))
                Fx[x] = max(Fx[x], K1b1[x][1] + K2b2[x][1])
        a = X.mat_vec(Rup, [cx / 2 + f + sl for cx, f, sl in zip(c, Fx, slack)])
        chk = check_block_cert(encs, a, b1, b2, c)
        a0 = X.mat_vec(Rup, [cx / 2 + f for cx, f in zip(c, Fx)])
        neg = check_block_cert(encs, a0, b1, b2, c)
        # pointwise comparison on the grid: LB(e) <= block bound (must hold), and pointwise cert overhead
        grid = []
        for k in range(9):
            e = F(k, 32)
            Q.guard_drift(e)
            ch = Chain(fam.K(e, 0), fam.K(e, 1), fam.K(e, 2), atom=0)
            U = ch.moment_totals(4)
            bb = lr_bounds_A1(ch, U, 12, 60)
            bb.pop("_fwd")
            R = ch.R
            dR = X.mat_mul(X.mat_mul(R, ch.K1), R)
            grid.append({"e": str(e), "true": sum(abs(v) for v in dR[0]), "LB": bb["lower_bound"],
                         "cert": bb["best_cert"]})
        blk = a[0]
        k1_up = max(sum(max(abs(encs[k][1][x][y][0]), abs(encs[k][1][x][y][1])) for y in range(n))
                    for k in range(m) for x in range(n))
        C_up = X.op_norm(Rup)
        absK1up = [[max(max(abs(encs[k][1][x][y][0]), abs(encs[k][1][x][y][1])) for k in range(m))
                    for y in range(n)] for x in range(n)]
        pm_blk = X.mat_vec(Rup, X.mat_vec(absK1up, X.mat_vec(Rup, [F(1)] * n)))[0]
        rec = {"seed": seed, "n": n, "block_cert_pass": chk["pass"], "block_bound_A1LR": fl(blk),
               "neg_slack0_rejected": not neg["pass"],
               "max_grid_true": fl(max(g["true"] for g in grid)), "max_grid_LB": fl(max(g["LB"] for g in grid)),
               "max_grid_cert": fl(max(g["cert"] for g in grid)),
               "LB_le_block_all": all(g["LB"] <= blk for g in grid),
               "overhead_block_over_max_pointwise_cert": fl(blk / max(g["cert"] for g in grid)),
               "PM_block": fl(pm_blk), "G_block": fl(k1_up * C_up * C_up),
               "chain_block": blk <= pm_blk <= k1_up * C_up * C_up,
               "W_block_supersolution_rowsum_Kup_lt_1": True}
        out["records"].append(rec)
        print("block", rec, flush=True)
    VALID.mkdir(exist_ok=True)
    (VALID / "C1LR_BLOCK.json").write_text(json.dumps(out, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --block", "C1a block-uniform e-free LR certificate on synthetic "
                    "fixtures, block [0,1/4]", cells_touched=[], klass="SYNTHETIC_VALIDATION")
    return out



def build_block_cert(fam, lo_b: F, hi_b: F, m: int, eta: F) -> dict:
    Q.guard_drift(lo_b, hi_b)
    n = fam.n
    subs = [(lo_b + (hi_b - lo_b) * F(k, m), lo_b + (hi_b - lo_b) * F(k + 1, m)) for k in range(m)]
    encs = [block_enclosures(fam, l, h) for (l, h) in subs]
    Kup = [[max(encs[k][0][x][y][1] for k in range(m)) for y in range(n)] for x in range(n)]
    assert all(sum(r) < 1 for r in Kup)
    Rup = X.mat_inv(X.mat_add(X.mat_id(n), Kup, F(-1)))
    em = (lo_b + hi_b) / 2
    chm = Chain(fam.K(em, 0), fam.K(em, 1), fam.K(em, 2), atom=0)
    Um = chm.moment_totals(2)
    U0, U2 = Um[(0, 0)], Um[(2, 0)]
    c = [dyadic(sqrt_up(U2[y] / U0[y])) if U0[y] > 0 and U2[y] > 0 else F(1) for y in range(n)]
    b2 = [(1 + eta) * v for v in X.mat_vec(Rup, [1 / (2 * cx) for cx in c])]
    b1 = X.mat_vec(chm.R, [2 * v for v in X.mat_vec(chm.K1, b2)])
    slack = [F(0)] * n
    Fx = [None] * n
    for (K0, K1, K2s) in encs:
        Kb2, Kb1, K1b2 = imatvec(K0, b2), imatvec(K0, b1), imatvec(K1, b2)
        K1b1, K2b2 = imatvec(K1, b1), imatvec(K2s, b2)
        for x in range(n):
            A_lo = b2[x] - 1 / (2 * c[x]) - Kb2[x][1]
            B_lo = b1[x] - Kb1[x][1] - 2 * K1b2[x][1]
            B_hi = b1[x] - Kb1[x][0] - 2 * K1b2[x][0]
            slack[x] = max(slack[x], max(B_lo * B_lo, B_hi * B_hi) / (4 * A_lo))
            v = K1b1[x][1] + K2b2[x][1]
            Fx[x] = v if Fx[x] is None or v > Fx[x] else Fx[x]
    a = X.mat_vec(Rup, [cx / 2 + f + sl for cx, f, sl in zip(c, Fx, slack)])
    chk = check_block_cert(encs, a, b1, b2, c)
    a0 = X.mat_vec(Rup, [cx / 2 + f for cx, f in zip(c, Fx)])
    neg = check_block_cert(encs, a0, b1, b2, c)
    return {"value": a[0], "pass": chk["pass"], "neg_slack0_rejected": not neg["pass"],
            "Lambda_up": X.mat_vec(Rup, [F(1)] * n)[0], "eta": eta, "m": m, "encs": encs, "Rup": Rup}


def run_block_variants(seeds=range(1, 9)):
    lo_b, hi_b = F(0), F(1, 4)
    Q.guard_drift(lo_b, hi_b)
    base = json.loads((VALID / "C1LR_BLOCK.json").read_text())
    basemap = {r["seed"]: r for r in base["records"]}
    var = []
    for seed in seeds:
        n = 6 + seed % 4
        fam = X.random_family(n, seed, e_range=(lo_b, hi_b), kill=F(1, 20))
        lam_grid = []
        for k in range(9):
            e = F(k, 32)
            Q.guard_drift(e)
            lam_grid.append(fam.R(e)[0])
        max_lam = max(sum(r) for r in lam_grid)
        rows = []
        best = None
        for m in (8, 32):
            for eta in (F(1, 100), F(1, 10), F(1, 2), F(2)):
                bc = build_block_cert(fam, lo_b, hi_b, m, eta)
                rows.append({"m": m, "eta": str(eta), "value": fl(bc["value"]), "pass": bc["pass"],
                             "neg_slack0_rejected": bc["neg_slack0_rejected"]})
                if bc["pass"] and (best is None or bc["value"] < best["value"]):
                    best = bc
        # block PM / G with the best variant's m (same envelope construction)
        encs, Rup, m = best["encs"], best["Rup"], best["m"]
        absK1up = [[max(max(abs(encs[k][1][x][y][0]), abs(encs[k][1][x][y][1])) for k in range(m))
                    for y in range(n)] for x in range(n)]
        pm_blk = X.mat_vec(Rup, X.mat_vec(absK1up, X.mat_vec(Rup, [F(1)] * n)))[0]
        k1_up = max(sum(absK1up[x]) for x in range(n))
        C_up = X.op_norm(Rup)
        b = basemap.get(seed, {})
        rec = {"seed": seed, "variants": rows, "best_value": fl(best["value"]), "best_m": best["m"],
               "best_eta": str(best["eta"]), "Lambda_up": fl(best["Lambda_up"]), "max_grid_Lambda": fl(max_lam),
               "Lambda_envelope_inflation": fl(best["Lambda_up"] / max_lam),
               "max_grid_cert": b.get("max_grid_cert"), "max_grid_LB": b.get("max_grid_LB"),
               "max_grid_true": b.get("max_grid_true"),
               "overhead_best_over_max_pointwise_cert": fl(best["value"]) / b["max_grid_cert"] if b else None,
               "LB_le_best": (b.get("max_grid_LB") or 0) <= fl(best["value"]),
               "PM_block": fl(pm_blk), "G_block": fl(k1_up * C_up * C_up),
               "chain_best_le_PM_le_G": best["value"] <= pm_blk <= k1_up * C_up * C_up,
               "all_variants_pass": all(r["pass"] for r in rows),
               "all_neg_rejected": all(r["neg_slack0_rejected"] for r in rows)}
        var.append(rec)
        print("var", {k: rec[k] for k in rec if k != "variants"}, flush=True)
    base["variants_declared"] = "eta in {1/100,1/10,1/2,2} x m in {8,32}; best = min over checker-passing variants"
    base["variant_records"] = var
    (VALID / "C1LR_BLOCK.json").write_text(json.dumps(base, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --block-variants", "C1a block certificate declared parameter "
                    "variants (synthetic fixtures, block [0,1/4])", cells_touched=[], klass="SYNTHETIC_VALIDATION")



def run_block_negctl(seeds=range(1, 9)):
    lo_b, hi_b = F(0), F(1, 4)
    Q.guard_drift(lo_b, hi_b)
    doc = json.loads((VALID / "C1LR_BLOCK.json").read_text())
    vmap = {r["seed"]: r for r in doc["variant_records"]}
    out = []
    for seed in seeds:
        r = vmap[seed]
        n = 6 + seed % 4
        fam = X.random_family(n, seed, e_range=(lo_b, hi_b), kill=F(1, 20))
        bc = build_block_cert(fam, lo_b, hi_b, r["best_m"], F(r["best_eta"]))
        # rebuild the certificate vectors (build_block_cert returns only the value); re-derive by scaling check
        encs = bc["encs"]
        # reconstruct a, b1, b2 exactly as in build_block_cert
        Rup = bc["Rup"]
        em = (lo_b + hi_b) / 2
        chm = Chain(fam.K(em, 0), fam.K(em, 1), fam.K(em, 2), atom=0)
        Um = chm.moment_totals(2)
        c = [dyadic(sqrt_up(Um[(2, 0)][y] / Um[(0, 0)][y])) if Um[(0, 0)][y] > 0 and Um[(2, 0)][y] > 0 else F(1)
             for y in range(n)]
        eta = F(r["best_eta"])
        b2 = [(1 + eta) * v for v in X.mat_vec(Rup, [1 / (2 * cx) for cx in c])]
        b1 = X.mat_vec(chm.R, [2 * v for v in X.mat_vec(chm.K1, b2)])
        slack = [F(0)] * n
        Fx = [None] * n
        for (K0, K1, K2s) in encs:
            Kb2, Kb1, K1b2 = imatvec(K0, b2), imatvec(K0, b1), imatvec(K1, b2)
            K1b1, K2b2 = imatvec(K1, b1), imatvec(K2s, b2)
            for x in range(n):
                A_lo = b2[x] - 1 / (2 * c[x]) - Kb2[x][1]
                B_lo = b1[x] - Kb1[x][1] - 2 * K1b2[x][1]
                B_hi = b1[x] - Kb1[x][0] - 2 * K1b2[x][0]
                slack[x] = max(slack[x], max(B_lo * B_lo, B_hi * B_hi) / (4 * A_lo))
                v = K1b1[x][1] + K2b2[x][1]
                Fx[x] = v if Fx[x] is None or v > Fx[x] else Fx[x]
        a = X.mat_vec(Rup, [cx / 2 + f + sl for cx, f, sl in zip(c, Fx, slack)])
        same = a[0] == bc["value"] and check_block_cert(encs, a, b1, b2, c)["pass"]
        lb = F(r["max_grid_LB"])
        sc = lb / (2 * a[0])
        rej = not check_block_cert(encs, [v * sc for v in a], [v * sc for v in b1], [v * sc for v in b2], c)["pass"]
        out.append({"seed": seed, "rebuilt_matches_and_passes": same, "scale": float(sc),
                    "scaled_below_LB_rejected": rej})
        print("negctl", out[-1], flush=True)
    doc["guaranteed_invalid_controls"] = out
    (VALID / "C1LR_BLOCK.json").write_text(json.dumps(doc, indent=1, default=str))
    Q.log_execution("streams/C_308/LR/lr_fsm.py --block-negctl", "C1a block checker guaranteed-invalid negative "
                    "control (synthetic)", cells_touched=[], klass="SYNTHETIC_VALIDATION")


if __name__ == "__main__":
    if "--one" in sys.argv:
        s = int(sys.argv[sys.argv.index("--one") + 1])
        r = analyse_seed(s, F(1, 20), F(1, 8), 12, int(sys.argv[sys.argv.index("--one") + 2]))
        print(json.dumps(r, indent=1, default=str)[:6000])
    if "--examples" in sys.argv:
        out = run_examples()
        for k in ("E1d", "E2"):
            for r in out[k]:
                print(k, {kk: r[kk] for kk in r if kk not in ("identity", "regenerative_checks")})
    if "--example-e1dp" in sys.argv:
        run_example_E1dp()
    if "--block" in sys.argv:
        run_block()
    if "--block-variants" in sys.argv:
        run_block_variants()
    if "--block-negctl" in sys.argv:
        run_block_negctl()
    if "--sets" in sys.argv:
        out = run_sets()
        print(json.dumps({k: out[k]["summary"] for k in ("V1", "V2")}, indent=1, default=str)[:9000])
