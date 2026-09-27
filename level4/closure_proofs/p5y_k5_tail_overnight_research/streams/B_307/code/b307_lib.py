"""Stream B_307 shared exact library (stdlib ``fractions`` only; no historical module is imported).

Everything here acts on synthetic finite-state drift families (``ov_fixtures.DriftFamily``) or on committed
non-target numbers passed in by the caller.  Nothing here knows about CUSUM m=5 cells; every public entry point
that takes a drift calls ``ov_quarantine.guard_drift``.

Contents
  * two fixture generators (declared in VALIDATION_DECLARATION_B307.json before any run):
      generic_family   -- rows = random probability vectors scaled by (1 - kill_x); the e-dependence is a
                          row-sum-zero redistribution (score-like part) plus a small kill-changing part;
      score_walk       -- one-sided discrete CUSUM-like walk on {0..N} with reflection at 0 (the atom) and killing
                          (alarm) above N; increment law p_z(e) with sum_z p_z^(i)(e) = 0 for i >= 1;
                          sources S_0, h_j, S_r = J h_r built exactly as polynomial vectors;
  * exact resolvent-derivative operators at a point: R, dR = R K1 R, d2R, d3R;
  * atom split (Lemma K analogue), taboo resolvent, tau_a, C_T, D, D', D'' (exact);
  * the atom-constant ladders (Lemma G, Lemma Dv' r2, collapse level, positive majorant, true functional norms);
  * certified cell-uniform bounds (k_i, sigma_n, C) from the exact polynomial Taylor structure;
  * an INDEPENDENT re-implementation of the theorem-TC arithmetic (Env4, p0/p1/p2, radius).
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_fixtures as X  # noqa: E402
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

ATOM = 0


# ----------------------------------------------------------------------------------------------- small helpers

def absm(A):
    return [[abs(a) for a in r] for r in A]


def row_l1(A, a: int = ATOM) -> F:
    """Norm of the functional f -> (A f)(a) on (R^n, sup): sum_j |A[a][j]| (exact)."""
    return sum((abs(x) for x in A[a]), F(0))


def mm(*Ms):
    out = Ms[0]
    for M in Ms[1:]:
        out = X.mat_mul(out, M)
    return out


def madd(*Ms):
    out = Ms[0]
    for M in Ms[1:]:
        out = X.mat_add(out, M)
    return out


def vsub(u, v):
    return [a - b for a, b in zip(u, v)]


def vadd(*vs):
    out = list(vs[0])
    for v in vs[1:]:
        out = [a + b for a, b in zip(out, v)]
    return out


def vscale(v, s):
    return [s * a for a in v]


def ones(n):
    return [F(1)] * n


def poly_mul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                out[i + j] += a * b
    return out


def poly_add(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else F(0)) + (q[i] if i < len(q) else F(0)) for i in range(n)]


def poly_scale(p, s):
    return [s * a for a in p]


def polymat_vec(kp, vp):
    """(K v) as polynomial vector: sum_j kp[x][j] * vp[j]."""
    out = []
    for row in kp:
        acc = [F(0)]
        for kxy, vy in zip(row, vp):
            if any(kxy) and any(vy):
                acc = poly_add(acc, poly_mul(kxy, vy))
        out.append(acc)
    return out


def taylor_abs_bound_poly(p, e0: F, rho: F, i: int) -> F:
    """Certified sup_{|t|<=rho} |p^(i)(e0 + t)| <= sum_j |p^(i+j)(e0)| rho^j / j!  (exact for polynomials)."""
    D = len(p) - 1
    tot = F(0)
    for j in range(0, D - i + 1):
        tot += abs(X.poly_eval(X.poly_deriv(list(p), i + j), e0)) * rho ** j / factorial(j)
    return tot


def compositions(n: int):
    """all ordered tuples of positive integers summing to n (n = 0 -> the empty composition)."""
    if n == 0:
        return [()]
    out = []
    for first in range(1, n + 1):
        for rest in compositions(n - first):
            out.append((first,) + rest)
    return out


def row_times(v, M):
    return [sum((a * M[x][y] for x, a in enumerate(v) if a), F(0)) for y in range(len(M[0]))]


def generic_dnR_bound(n: int, k, C) -> F:
    """||d^n R|| <= sum over compositions n!/prod(i!) C^(p+1) prod k_i  (Lemma-G type, cell-uniform if k, C are)."""
    tot = F(0)
    for comp in compositions(n):
        c = F(factorial(n))
        for i in comp:
            c = c / factorial(i) * k[i]
        tot += c * C ** (len(comp) + 1)
    return tot


# ----------------------------------------------------------------------------------------------- generators

def generic_family(n: int, seed: int, kill_scale: F, deg: int = 4, e_range=(F(0), F(1, 4))):
    """FX_A generator.  Row x: base_j = w_j / sum w * (1 - kill_x), kill_x = kill_scale * (1 + U{0..10}/10).
    Drift coefficients for degree d = 1..deg:
        c_{xj,d} = base_j * (u_{j,d} - ubar_d) / 4        (row-sum-zero redistribution, u ~ U{-10..10}/10)
                 + base_j * kill_x * v_d / 10              (kill-changing part, v ~ U{-10..10}/10)
    Positivity and row sums < 1 are verified EXACTLY on e_range by the worst-case coefficient bound."""
    rng = random.Random(7919 * seed + 104729 * n + int(1 / kill_scale))
    kp = []
    emax = max(abs(F(e_range[0])), abs(F(e_range[1])))
    for x in range(n):
        w = [F(rng.randint(1, 20)) for _ in range(n)]
        s = sum(w)
        kill = kill_scale * (1 + F(rng.randint(0, 10), 10))
        base = [wj / s * (1 - kill) for wj in w]
        row = [[b] for b in base]
        for d in range(1, deg + 1):
            u = [F(rng.randint(-10, 10), 10) for _ in range(n)]
            ubar = sum(bj * uj for bj, uj in zip(base, u)) / sum(base)
            v = F(rng.randint(-10, 10), 10)
            for j in range(n):
                row[j].append(base[j] * (u[j] - ubar) / 4 + base[j] * kill * v / 10)
        kp.append(row)
    # exact admissibility on the e-range
    for row in kp:
        tot = F(0)
        for c in row:
            drift = sum((abs(c[d]) * emax ** d for d in range(1, len(c))), F(0))
            if c[0] - drift <= 0:
                raise ValueError("entry may become non-positive")
            tot += c[0] + drift
        if tot >= 1:
            # row-sum-zero part cancels exactly in the row sum; bound the row sum sharply instead
            rs = [F(0)] * (deg + 1)
            for c in row:
                for d in range(len(c)):
                    rs[d] += c[d]
            if rs[0] + sum((abs(rs[d]) * emax ** d for d in range(1, deg + 1)), F(0)) >= 1:
                raise ValueError("row may reach 1")
    return kp


def generic_sources(n: int, seed: int, count: int, deg: int = 5):
    rng = random.Random(15485863 + 31 * seed + n)
    return [[[F(rng.randint(-10, 10), 10) for _ in range(deg + 1)] for _ in range(n)] for _ in range(count)]


SCORE_C, SCORE_D, SCORE_C3 = F(1, 2), F(1, 8), F(1, 16)


def score_walk(N: int, c: F = SCORE_C, d: F = SCORE_D, c3: F = SCORE_C3, r_max: int = 4):
    """FX_B generator: states 0..N, x -> max(0, x+z), alarm iff x+z > N.
    Returns (kp, sources) with sources [S_0, S_1, ..., S_rmax] as polynomial vectors, plus h list."""
    p = {+1: [F(1, 3), c / 3, d / 3, c3 / 3], -1: [F(1, 3), -c / 3, d / 3, -c3 / 3], 0: [F(1, 3), F(0), -2 * d / 3, F(0)]}
    n = N + 1
    kp = [[[F(0)] for _ in range(n)] for _ in range(n)]
    h1 = [[F(0)] for _ in range(n)]
    S0 = [[F(0)] for _ in range(n)]
    for x in range(n):
        for z, pz in p.items():
            if x + z > N:
                h1[x] = poly_add(h1[x], pz)
                S0[x] = poly_add(S0[x], poly_scale(pz, F(z)))
            else:
                y = max(0, x + z)
                kp[x][y] = poly_add(kp[x][y], pz)
    # J kernel: (J g)(x) = sum_z z p_z(e) g(T(x,z)) 1{no alarm}
    jp = [[[F(0)] for _ in range(n)] for _ in range(n)]
    for x in range(n):
        for z, pz in p.items():
            if x + z <= N:
                y = max(0, x + z)
                jp[x][y] = poly_add(jp[x][y], poly_scale(pz, F(z)))
    hs = [None, h1]
    for j in range(2, r_max + 1):
        hs.append(polymat_vec(kp, hs[-1]))
    sources = [S0] + [polymat_vec(jp, hs[r]) for r in range(1, r_max + 1)]
    return kp, sources, hs


def score_walk_admissible(e_lo: F, e_hi: F, c: F = SCORE_C, d: F = SCORE_D, c3: F = SCORE_C3) -> bool:
    em = max(abs(e_lo), abs(e_hi))
    return (1 - c * em - c3 * em ** 3 > 0) and (1 - 2 * d * em ** 2 > 0)


# ----------------------------------------------------------------------------------------------- point objects

class Point:
    """All exact point objects of a kernel family at drift e (atom = state 0)."""

    def __init__(self, kp, e: F, need_d3: bool = True):
        Q.guard_drift(e)
        self.e = F(e)
        fam = X.DriftFamily(kp, [[F(0)]] * len(kp), (e, e))
        self.n = len(kp)
        self.K = [fam.K(self.e, i) for i in range(5)]
        n = self.n
        I = X.mat_id(n)
        self.R = X.mat_inv(X.mat_add(I, self.K[0], F(-1)))
        R, K1, K2, K3 = self.R, self.K[1], self.K[2], self.K[3]
        self.dR = mm(R, K1, R)
        RK1R = self.dR
        self.d2R = madd(X.mat_scale(mm(RK1R, K1, R), F(2)), mm(R, K2, R))
        if need_d3:
            self.d3R = madd(X.mat_scale(mm(RK1R, K1, RK1R), F(6)),
                            X.mat_scale(mm(R, K2, RK1R), F(3)),
                            X.mat_scale(mm(RK1R, K2, R), F(3)),
                            mm(R, K3, R))
        self.Lam = sum(self.R[ATOM], F(0))                      # E_a[tau] = (R 1)(a)
        self.C = X.op_norm(self.R)                                 # ||R|| = sup_x E_x[tau]
        self.k = [X.op_norm(Ki) for Ki in self.K]

    # ------------------------------------------------------------------ atom rows of d^n R (compositions)
    def atom_rows(self, nmax: int = 4):
        """[delta_a d^n R for n = 0..nmax] as row vectors, from
        d^n R = sum over compositions (i_1..i_p) of n of  n!/(i_1!...i_p!)  R K_{i_1} R K_{i_2} R ... K_{i_p} R."""
        rows = []
        for nn in range(nmax + 1):
            acc = [F(0)] * self.n
            for comp in compositions(nn):
                v = list(self.R[ATOM])
                for i in comp:
                    v = row_times(row_times(v, self.K[i]), self.R)
                c = F(factorial(nn))
                for i in comp:
                    c /= factorial(i)
                acc = [x + c * y for x, y in zip(acc, v)]
            rows.append(acc)
        return rows

    # ------------------------------------------------------------------ atom split (Lemma K / T / SM analogues)
    def taboo(self):
        n, a = self.n, ATOM
        Kh = [[(F(0) if j == a else x) for j, x in enumerate(r)] for r in self.K[0]]
        Kh1 = [[(F(0) if j == a else x) for j, x in enumerate(r)] for r in self.K[1]]
        Kh2 = [[(F(0) if j == a else x) for j, x in enumerate(r)] for r in self.K[2]]
        ka = [r[a] for r in self.K[0]]
        ka1 = [r[a] for r in self.K[1]]
        ka2 = [r[a] for r in self.K[2]]
        G = X.mat_inv(X.mat_add(X.mat_id(n), Kh, F(-1)))
        G1 = mm(G, Kh1, G)
        G2 = madd(X.mat_scale(mm(G1, Kh1, G), F(2)), mm(G, Kh2, G))
        tau_a = sum(G[a], F(0))
        C_T = X.op_norm(G)
        Dv = 1 - X.mat_vec(G, ka)[a]
        D1 = -(X.mat_vec(G1, ka)[a] + X.mat_vec(G, ka1)[a])
        D2 = -(X.mat_vec(G2, ka)[a] + 2 * X.mat_vec(G1, ka1)[a] + X.mat_vec(G, ka2)[a])
        h1 = [1 - s for s in X.mat_vec(self.K[0], ones(n))]
        D_via_h1 = X.mat_vec(G, h1)[a]
        kap = [X.op_norm(Kh1), X.op_norm(Kh2)]
        return {"tau_a": tau_a, "C_T": C_T, "D": Dv, "D1": D1, "D2": D2, "D_via_h1": D_via_h1,
                "kappa1": kap[0], "kappa2": kap[1]}

    # ------------------------------------------------------------------ atom-constant ladders
    def ladders(self):
        R, K1, K2, K3 = self.R, self.K[1], self.K[2], self.K[3]
        Lam, C, k = self.Lam, self.C, self.k
        one = ones(self.n)
        w = X.mat_vec(R, one)
        aK1, aK2, aK3 = absm(K1), absm(K2), absm(K3)
        v1 = X.mat_vec(R, X.mat_vec(aK1, w))              # R|K1|R1
        v2 = X.mat_vec(R, X.mat_vec(aK2, w))              # R|K2|R1
        v11 = X.mat_vec(R, X.mat_vec(aK1, v1))            # R|K1|R|K1|R1
        pm1 = v1[ATOM]
        pm2 = 2 * v11[ATOM] + v2[ATOM]
        pm3 = (6 * X.mat_vec(R, X.mat_vec(aK1, v11))[ATOM] + 3 * X.mat_vec(R, X.mat_vec(aK2, v1))[ATOM]
               + 3 * X.mat_vec(R, X.mat_vec(aK1, v2))[ATOM] + X.mat_vec(R, X.mat_vec(aK3, w))[ATOM])
        tb = self.taboo()
        CT, D, kap1, kap2 = tb["C_T"], tb["D"], tb["kappa1"], tb["kappa2"]
        d1, d2 = abs(tb["D1"]) / D, abs(tb["D2"]) / D
        out = {
            "Lambda": Lam, "C": C, "k1": k[1], "k2": k[2], "k3": k[3], "C_T": CT, "tau_a": tb["tau_a"], "D": D,
            "delta1": d1, "delta2": d2,
            "A0": {"true": Lam, "G": C, "Dv2": min(Lam, tb["tau_a"] / D)},
            "A1": {"true": row_l1(self.dR), "PM": pm1, "collapse": Lam * k[1] * C, "G": k[1] * C * C,
                    "Dv2": Lam * (kap1 * CT + d1)},
            "A2": {"true": row_l1(self.d2R), "PM": pm2, "collapse": Lam * (2 * k[1] ** 2 * C ** 2 + k[2] * C),
                    "G": k[2] * C * C + 2 * k[1] ** 2 * C ** 3,
                    "Dv2": Lam * (2 * kap1 ** 2 * CT ** 2 + kap2 * CT + 2 * kap1 * CT * d1 + 2 * d1 ** 2 + d2)},
        }
        if hasattr(self, "d3R"):
            out["A3"] = {"true": row_l1(self.d3R), "PM": pm3,
                         "collapse": Lam * (6 * k[1] ** 3 * C ** 3 + 6 * k[1] * k[2] * C ** 2 + k[3] * C),
                         "G": 6 * k[1] ** 3 * C ** 4 + 6 * k[1] * k[2] * C ** 3 + k[3] * C ** 2}
        return out


# ----------------------------------------------------------------------------------------------- cell bounds

def cell_bounds(kp, sources, e0: F, rho: F, s_orders: int = 5):
    """Certified cell-uniform bounds on [e0 - rho, e0 + rho] from the exact polynomial Taylor structure.
    k[i]   >= sup ||K_i(e)||      (entrywise sum_j |K_{i+j}(e0)| rho^j / j!, then max row sum)
    C      >= sup ||R_e||         (Neumann: ||R0|| / (1 - ||R0|| * Delta), Delta >= sup ||K_e - K_e0||)
    sig[r][n] >= sup ||S_r^(n)(e)||."""
    Q.guard_drift(e0 - rho, e0 + rho)
    n = len(kp)
    k = []
    for i in range(5):
        k.append(max(sum(taylor_abs_bound_poly(p, e0, rho, i) for p in row) for row in kp))
    # Delta: sum_{j>=1} |K_j(e0)| rho^j/j!
    delta = F(0)
    for row in kp:
        tot = F(0)
        for p in row:
            for j in range(1, len(p)):
                tot += abs(X.poly_eval(X.poly_deriv(list(p), j), e0)) * rho ** j / factorial(j)
        delta = max(delta, tot)
    fam = X.DriftFamily(kp, [[F(0)]] * n, (e0, e0))
    R0n = X.op_norm(X.mat_inv(X.mat_add(X.mat_id(n), fam.K(e0), F(-1))))
    if R0n * delta >= 1:
        raise ValueError("Neumann bound fails on this cell")
    C = R0n / (1 - R0n * delta)
    sig = []
    for sp in sources:
        sig.append([max(taylor_abs_bound_poly(p, e0, rho, m) for p in sp) for m in range(s_orders)])
    return {"k": k, "C": C, "Delta": delta, "sigma": sig}


def cover_rule_rho(kp, sources, e0: F, cap: F):
    """rho = min(cap, 1/(4 k1(e0) C(e0))), then shrunk once to <= 1/(4 k1_cell C_cell) (monotone, so valid)."""
    P = Point(kp, e0, need_d3=False)
    rho0 = min(cap, 1 / (4 * P.k[1] * P.C))
    b = cell_bounds(kp, sources, e0, rho0)
    rho1 = min(rho0, 1 / (4 * b["k"][1] * b["C"]))
    # make it a short rational (round DOWN), keeps validity (bounds are monotone in rho)
    den = 10 ** 6
    rho1 = F(int(rho1 * den), den)
    return rho1


# ----------------------------------------------------------------------------------------------- theorem TC arithmetic

def env4(sF, sD, sH, sG, k, sigma4, rho):
    return (sigma4 + 4 * k[1] * sG + 6 * k[2] * (sH + rho * sG) + 4 * k[3] * (sD + rho * sH + rho ** 2 * sG / 2)
            + k[4] * (sF + rho * sD + rho ** 2 * sH / 2 + rho ** 3 * sG / 6))


def env4_sG_part(sG, k, rho):
    return sG * (4 * k[1] + 6 * k[2] * rho + 2 * k[3] * rho ** 2 + k[4] * rho ** 3 / 6)


def taylor_p(fF, fD, fH, fG, e4, s):
    p0 = fF + s * fD + s ** 2 * fH / 2 + s ** 3 * fG / 6 + s ** 4 * e4 / 24
    p1 = fD + s * fH + s ** 2 * fG / 2 + s ** 3 * e4 / 6
    p2 = fH + s * fG + s ** 2 * e4 / 2
    return p0, p1, p2


def radius(A0, A1, A2, p):
    p0, p1, p2 = p
    return A0 * p2 + 2 * A1 * p1 + A2 * p0


def radius_terms(A0, A1, A2, fF, fD, fH, fG, e4, rho):
    """The 15 exact monomials of rad = A0 p2 + 2 A1 p1 + A2 p0 (bookkeeping identity)."""
    t = {
        "A0*fH": A0 * fH, "A0*rho*fG": A0 * rho * fG, "A0*rho^2*Env4/2": A0 * rho ** 2 * e4 / 2,
        "2A1*fD": 2 * A1 * fD, "2A1*rho*fH": 2 * A1 * rho * fH, "A1*rho^2*fG": A1 * rho ** 2 * fG,
        "A1*rho^3*Env4/3": A1 * rho ** 3 * e4 / 3,
        "A2*fF": A2 * fF, "A2*rho*fD": A2 * rho * fD, "A2*rho^2*fH/2": A2 * rho ** 2 * fH / 2,
        "A2*rho^3*fG/6": A2 * rho ** 3 * fG / 6, "A2*rho^4*Env4/24": A2 * rho ** 4 * e4 / 24,
    }
    return t


def selftest():
    kp = generic_family(5, 1, F(1, 5))
    P = Point(kp, F(1, 8))
    L = P.ladders()
    assert L["A1"]["true"] <= L["A1"]["PM"] <= L["A1"]["collapse"] <= L["A1"]["G"]
    kpb, src, hs = score_walk(4)
    Pb = Point(kpb, F(0))
    tb = Pb.taboo()
    assert tb["tau_a"] / tb["D"] == Pb.Lam
    print("b307_lib selftest PASS")


if __name__ == "__main__":
    selftest()
