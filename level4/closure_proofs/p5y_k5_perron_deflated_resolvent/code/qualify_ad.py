"""Manufactured qualification and mutation suite for theorem AD (non-scientific; exact rational arithmetic).

Every fixture is a finite state space X = {0, ..., n-1} with the atom a = 0 and a kernel family
    K_e(x, y) = B(x, y) * g_y(e),   g_y(e) = 1 + c_y e + d_y e^2 / 2      (polynomial in e, positive on the test range)
with row sums < 1 on the range. Khat_e = K_e with column 0 removed. A finite state space is a special case of B(X), so every
lemma of THEOREM_AD.md applies verbatim; the exact truth (resolvents, e-derivatives, point errors) is computed in Fraction.

Checks
  Q1  Lemma SM: (I-K)^-1 == Ghat + h (x) nu / D exactly; D == nu(h_1) > 0; sup_f |R f(a)| == tau_a / D == E_a[tau]
  Q2  Lemma Dv and Dv' (r1 and r2 constants): |[dR f](a)| <= A1 ||f||, |[d2R f](a)| <= A2 ||f|| for the extremal f
      (the sign pattern of the row / of the exact functional), at every sample drift
  Q3  Theorem AD on a manufactured DAG (true S_e analytic; candidates = truth + perturbations, including the adversarial
      constant-residual perturbation that makes the order-0 bound attained): radii >= exact point errors; H uniformly on
      the cell (at every sample drift of the cell, constants taken over the cell)
  Q4  Corollary T (tightening) on manufactured Minkowski-sum intervals: the truth stays inside, refusals fire
  Q5  refusals: nonpositive D_lo, tau < 1, C < tau, uncovered cell, a closed non-killed class (no taboo resolvent)
  Q6  mutation suite: every unsound mutant violates at least one fixture

    python3 -B code/qualify_ad.py run --out QUALIFICATION_AD.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import deflated_consume as DC  # noqa: E402


# ------------------------------------------------------------------------------------------------ exact linear algebra
def eye(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum((A[i][k] * B[k][j] for k in range(m) if A[i][k] and B[k][j]), F(0)) for j in range(p)] for i in range(n)]


def matvec(A, v):
    return [sum((a * b for a, b in zip(row, v) if a and b), F(0)) for row in A]


def sub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


def inv(A):
    n = len(A)
    M = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            raise ZeroDivisionError("singular")
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [x / piv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def norm_inf(A):
    return max(sum(abs(x) for x in row) for row in A)


def vnorm(v):
    return max(abs(x) for x in v)


# ------------------------------------------------------------------------------------------------ fixture families
class Family:
    """K_e = B o g(e) with the atom at state 0."""

    def __init__(self, name, B, c, d, e_range):
        self.name, self.B, self.c, self.d, self.e_range = name, B, c, d, e_range
        self.n = len(B)

    def g(self, y, e, k=0):
        if k == 0:
            return 1 + self.c[y] * e + self.d[y] * e * e / 2
        if k == 1:
            return self.c[y] + self.d[y] * e
        if k == 2:
            return self.d[y]
        return F(0)

    def K(self, e, k=0, hat=False):
        return [[(F(0) if (hat and y == 0) else self.B[x][y] * self.g(y, e, k)) for y in range(self.n)]
                for x in range(self.n)]

    def valid(self):
        for e in self.sample():
            K = self.K(e)
            if any(v < 0 for r in K for v in r) or any(sum(r) >= 1 for r in K):
                return False
        return True

    def sample(self, m=5):
        lo, hi = self.e_range
        return [lo + (hi - lo) * F(i, m - 1) for i in range(m)]


def make_families(seed=20260919):
    rng = random.Random(seed)
    fams = []

    def rnd(n, density=1.0, scale=F(1)):
        return [[(F(rng.randint(1, 20), 20) * scale if rng.random() < density else F(0)) for _ in range(n)]
                for _ in range(n)]

    def normalise(B, keep):
        out = []
        for x, row in enumerate(B):
            s = sum(row)
            out.append([v * keep[x] / s if s else v for v in row])
        return out
    # F1 simple positive
    n = 5
    fams.append(Family("F1_simple_positive", normalise(rnd(n), [F(3, 5)] * n), [F(1, 2)] * n, [F(0)] * n,
                       (F(0), F(1, 10))))
    # F2 near-unit Perron eigenvalue (tiny killing)
    fams.append(Family("F2_near_unit_perron", normalise(rnd(n), [F(999, 1000)] * n),
                       [F(0)] + [F(-1, 20)] * (n - 1), [F(0)] * n, (F(0), F(1, 10))))
    # F3 strongly nonnormal (feed-forward chain away from the atom, slow return)
    B = [[F(0)] * 6 for _ in range(6)]
    for x in range(6):
        B[x][min(x + 1, 5)] = F(9, 10)
        B[x][0] = F(1, 200)
    B[5][5] = F(97, 100)
    fams.append(Family("F3_nonnormal_feedforward", normalise(B, [F(99, 100)] * 5 + [F(98, 100)]),
                       [F(1, 5)] * 6, [F(0)] * 6, (F(0), F(1, 20))))
    # F4 ill-conditioned Perron vectors (one state carries almost all mass, atom rarely visited)
    B = rnd(5)
    B[1] = [F(1, 10000), F(9998, 10000), F(1, 20000), F(1, 20000), F(0)]
    fams.append(Family("F4_ill_conditioned", normalise(B, [F(19, 20), F(997, 1000), F(9, 10), F(9, 10), F(9, 10)]),
                       [F(1, 10)] * 5, [F(0)] * 5, (F(0), F(1, 50))))
    # F5 small spectral gap between Perron and the second mode
    B = [[F(0)] * 4 for _ in range(4)]
    B[0][0], B[0][1] = F(1, 2), F(49, 100)
    B[1][0], B[1][1] = F(49, 100), F(1, 2)
    B[2][2], B[2][3], B[2][0] = F(1, 2), F(485, 1000), F(1, 100)
    B[3][2], B[3][3], B[3][0] = F(485, 1000), F(1, 2), F(1, 100)
    fams.append(Family("F5_small_gap", B, [F(0), F(1, 3), F(-1, 3), F(1, 3)], [F(0)] * 4, (F(0), F(1, 20))))
    # F6 near-defective (two almost equal eigenvalues with nearly parallel eigenvectors)
    B = [[F(1, 2), F(49, 100), F(0)], [F(0), F(1, 2), F(49, 100)], [F(1, 100), F(0), F(97, 100)]]
    fams.append(Family("F6_near_defective", B, [F(1, 4), F(-1, 4), F(1, 4)], [F(1, 2), F(0), F(-1, 2)],
                       (F(0), F(1, 20))))
    # F7 exact rank-one slow mode plus small perturbation
    u = [F(1)] * 5
    v = [F(3, 10), F(1, 5), F(1, 5), F(1, 5), F(9, 100)]
    B = [[u[x] * v[y] + (F(1, 1000) if x == y else F(0)) for y in range(5)] for x in range(5)]
    fams.append(Family("F7_rank_one_slow", B, [F(0), F(2, 5), F(-2, 5), F(1, 5), F(0)], [F(0)] * 5, (F(0), F(1, 20))))
    # F8 two competing slow modes: a nearly closed class {3, 4} that rarely reaches the atom
    B = [[F(3, 10), F(3, 10), F(3, 10), F(1, 1000), F(0)],
         [F(3, 10), F(3, 10), F(3, 10), F(0), F(0)],
         [F(3, 10), F(3, 10), F(3, 10), F(0), F(0)],
         [F(1, 2000), F(0), F(0), F(1, 2), F(4985, 10000)],
         [F(0), F(0), F(0), F(4985, 10000), F(1, 2)]]
    fams.append(Family("F8_competing_slow_modes", B, [F(0), F(1, 10), F(-1, 10), F(1, 2), F(-1, 2)], [F(0)] * 5,
                       (F(0), F(1, 20))))
    # F9 strongly e-dependent eigenvectors (large c, curvature d)
    fams.append(Family("F9_e_dependent", normalise(rnd(5), [F(4, 5)] * 5), [F(3), F(-2), F(1), F(2), F(-3)],
                       [F(4), F(-4), F(2), F(0), F(1)], (F(0), F(1, 20))))
    # F10 fast-varying renewal defect (D'/D large): killing near the atom grows quickly with e
    B = normalise(rnd(4), [F(9995, 10000), F(99, 100), F(99, 100), F(99, 100)])
    fams.append(Family("F10_fast_D", B, [F(-8), F(0), F(0), F(0)], [F(0)] * 4, (F(1, 100), F(3, 100))))
    for f in fams:
        if not f.valid():
            raise SystemExit(f"fixture {f.name} invalid")
    return fams


# ------------------------------------------------------------------------------------------------ exact objects
def objects(fam, e):
    n = fam.n
    I = eye(n)
    K = fam.K(e)
    Kh = fam.K(e, hat=True)
    R = inv(sub(I, K))
    G = inv(sub(I, Kh))
    one = [F(1)] * n
    ka = [K[x][0] for x in range(n)]
    h1 = [1 - sum(K[x]) for x in range(n)]
    h = matvec(G, ka)
    D = 1 - h[0]
    tau_a = matvec(G, one)[0]
    C = max(matvec(G, one))
    K1, K2 = fam.K(e, 1), fam.K(e, 2)
    dR = matmul(matmul(R, K1), R)
    T = matmul(matmul(dR, K1), R)                      # R K' R K' R
    RK2R = matmul(matmul(R, K2), R)
    d2R = [[2 * a + b for a, b in zip(r1, r2)] for r1, r2 in zip(T, RK2R)]
    # D' and D'' exactly: D = (Ghat h_1)(a); differentiate the taboo system
    Kh1, Kh2 = fam.K(e, 1, hat=True), fam.K(e, 2, hat=True)
    dh1 = [-sum(K1[x]) for x in range(n)]
    d2h1 = [-sum(K2[x]) for x in range(n)]
    dvec = matvec(G, h1)
    d1vec = matvec(G, [a + b for a, b in zip(matvec(Kh1, dvec), dh1)])
    d2vec = matvec(G, [a + 2 * b + c for a, b, c in zip(matvec(Kh2, dvec), matvec(Kh1, d1vec), d2h1)])
    kap1 = norm_inf(K1)
    kap2 = norm_inf(K2)
    return {"R": R, "G": G, "h": h, "D": D, "tau_a": tau_a, "C": C, "ARL": matvec(R, one)[0], "dR": dR, "d2R": d2R,
            "D1": d1vec[0], "D2": d2vec[0], "Dnu": dvec[0], "kap1": kap1, "kap2": kap2, "h1": h1, "ka": ka}


def row_norm_at_atom(M):
    return sum(abs(x) for x in M[0])


# ------------------------------------------------------------------------------------------------ rules under test
def consts_over(fam, drifts, rule="r1", ob=None):
    obs = ob or [objects(fam, e) for e in drifts]
    tau = max(o["tau_a"] for o in obs)
    C = max(o["C"] for o in obs)
    Dlo = min(o["D"] for o in obs)
    D1 = max(abs(o["D1"]) for o in obs)
    D2 = max(abs(o["D2"]) for o in obs)
    k1 = max(o["kap1"] for o in obs)
    k2 = max(o["kap2"] for o in obs)
    Abar = max(o["ARL"] for o in obs)
    C = max(C, tau)
    if rule == "r2":
        return DC.atom_constants_r2(Abar, tau, C, Dlo, D1, D2, k1, k2), obs
    return DC.atom_constants(tau, C, Dlo, D1, D2, k1, k2), obs


# ------------------------------------------------------------------------------------------------ mutants
def mutant_constants(name, tau, C, Dlo, D1, D2, k1, k2, lam=None, Dhi=None):
    good = DC.atom_constants(tau, C, Dlo, D1, D2, k1, k2)
    if name == "M01_drop_perron_channel":            # use the taboo resolvent alone
        return {"A0": C, "A1": C * k1 * C, "A2": C * (2 * k1 ** 2 * C ** 2 + k2 * C)}
    if name == "M02_omit_normalization_D":           # nu without division by D
        return {"A0": tau, "A1": tau * k1 * C, "A2": tau * (2 * k1 ** 2 * C ** 2 + k2 * C)}
    if name == "M03_orthogonal_projection":          # point evaluation delta_a in place of nu = delta_a Ghat
        return {"A0": 1 / Dlo, "A1": k1 * C / Dlo + D1 / Dlo ** 2, "A2": good["A2"] / tau}
    if name == "M04_ignore_moving_projection":       # drop every D' and D'' term
        return {"A0": good["A0"], "A1": tau * k1 * C / Dlo, "A2": tau * (2 * k1 ** 2 * C ** 2 + k2 * C) / Dlo}
    if name == "M05_midpoint_eigen_as_exact":        # the largest D of the range in place of the smallest
        return DC.atom_constants(tau, C, Dhi, D1, D2, k1, k2)
    if name == "M06_gap_without_conditioning":       # 1/(1 - lambda) as the channel amplification
        g = 1 / (1 - lam)
        return {"A0": g, "A1": g * k1 * C, "A2": g * (2 * k1 ** 2 * C ** 2 + k2 * C)}
    if name == "M09_wrong_complement_norm":          # tau (a point value) in place of ||Ghat||
        return DC.atom_constants(tau, tau, Dlo, D1, D2, k1, k2) if tau <= C else good
    if name == "M11_half_second_order":              # 2 k1^2 C^2 -> k1^2 C^2 and drop 2 D1^2/D^3
        return {"A0": good["A0"], "A1": good["A1"],
                "A2": tau * (k1 ** 2 * C ** 2 + k2 * C) / Dlo + 2 * tau * k1 * C * D1 / Dlo ** 2 + tau * D2 / Dlo ** 2}
    raise KeyError(name)


CONSTANT_MUTANTS = ("M01_drop_perron_channel", "M02_omit_normalization_D", "M03_orthogonal_projection",
                    "M04_ignore_moving_projection", "M05_midpoint_eigen_as_exact", "M06_gap_without_conditioning",
                    "M09_wrong_complement_norm", "M11_half_second_order")


def perron_eigenvalue(fam, e):
    """Largest eigenvalue of K_e by the renewal root (bisection on Phi(z) = delta_a (z - Khat)^-1 k_a = 1)."""
    n = fam.n
    Kh = fam.K(e, hat=True)
    ka = [fam.K(e)[x][0] for x in range(n)]

    def phi(z):
        return matvec(inv(sub([[z * int(i == j) for j in range(n)] for i in range(n)], Kh)), ka)[0]
    lo, hi = F(0), F(1)
    for _ in range(60):
        mid = (lo + hi) / 2
        try:
            v = phi(mid)
        except ZeroDivisionError:
            lo = mid
            continue
        if v < 0 or v > 1:
            lo = mid
        else:
            hi = mid
    return hi


# ------------------------------------------------------------------------------------------------ checks
def extremal_point_error(M):
    """max over ||f|| <= 1 of |(M f)(a)| = l1 norm of row a."""
    return row_norm_at_atom(M)


def check_fixture(fam):
    out = {"family": fam.name, "violations": [], "mutant_violations": {m: 0 for m in CONSTANT_MUTANTS}}
    drifts = fam.sample()
    obs = [objects(fam, e) for e in drifts]
    for e, o in zip(drifts, obs):
        n = fam.n
        # Q1 Sherman-Morrison at the atom
        nu = o["G"][0]
        SM = [[o["G"][x][y] + o["h"][x] * nu[y] / o["D"] for y in range(n)] for x in range(n)]
        if SM != o["R"]:
            out["violations"].append(f"Q1 SM identity e={e}")
        if o["D"] != sum(nu[y] * o["h1"][y] for y in range(n)) or not o["D"] > 0:
            out["violations"].append(f"Q1 D = nu(h1) e={e}")
        if extremal_point_error(o["R"]) != o["tau_a"] / o["D"] or o["ARL"] != o["tau_a"] / o["D"]:
            out["violations"].append(f"Q1 sharpness e={e}")
    for rule in ("r1", "r2"):
        # Q2 at each drift with that drift's own constants and with the range constants
        A_rng, _ = consts_over(fam, drifts, rule, obs)
        for e, o in zip(drifts, obs):
            A_pt, _ = consts_over(fam, [e], rule, [o])
            for A, tag in ((A_pt, "point"), (A_rng, "range")):
                if extremal_point_error(o["R"]) > A["A0"]:
                    out["violations"].append(f"Q2 {rule} A0 {tag} e={e}")
                if extremal_point_error(o["dR"]) > A["A1"]:
                    out["violations"].append(f"Q2 {rule} A1 {tag} e={e}")
                if extremal_point_error(o["d2R"]) > A["A2"]:
                    out["violations"].append(f"Q2 {rule} A2 {tag} e={e}")
    # mutants against the range constants
    tau = max(o["tau_a"] for o in obs)
    C = max(max(o["C"] for o in obs), tau)
    Dlo, Dhi = min(o["D"] for o in obs), max(o["D"] for o in obs)
    D1, D2 = max(abs(o["D1"]) for o in obs), max(abs(o["D2"]) for o in obs)
    k1, k2 = max(o["kap1"] for o in obs), max(o["kap2"] for o in obs)
    lam = min(perron_eigenvalue(fam, e) for e in drifts)
    for mname in CONSTANT_MUTANTS:
        A = mutant_constants(mname, tau, C, Dlo, D1, D2, k1, k2, lam=lam, Dhi=Dhi)
        for o in obs:
            if (extremal_point_error(o["R"]) > A["A0"] or extremal_point_error(o["dR"]) > A["A1"]
                    or extremal_point_error(o["d2R"]) > A["A2"]):
                out["mutant_violations"][mname] += 1
    out["constants"] = {"tau": float(tau), "C": float(C), "Dlo": float(Dlo), "Dhi": float(Dhi), "D1": float(D1),
                        "D2": float(D2), "k1": float(k1), "k2": float(k2), "lambda_min": float(lam),
                        "ARL_max": float(max(o["ARL"] for o in obs))}
    return out


# ------------------------------------------------------------------------------------------------ Q3 DAG fixture
def dag_fixture(fam, seed, adversarial):
    """True S_e = s0 + e s1 + e^2 s2 / 2 (+ e^3 s3 / 6); F = R S, D = F', H = F''. Candidates at the midpoint."""
    rng = random.Random(seed)
    n = fam.n
    lo, hi = fam.e_range
    e0, rho = (lo + hi) / 2, (hi - lo) / 2
    s = [[F(rng.randint(-20, 20), 40) for _ in range(n)] for _ in range(4)]

    def S(e, k):
        if k == 0:
            return [s[0][x] + e * s[1][x] + e * e * s[2][x] / 2 + e ** 3 * s[3][x] / 6 for x in range(n)]
        if k == 1:
            return [s[1][x] + e * s[2][x] + e * e * s[3][x] / 2 for x in range(n)]
        return [s[2][x] + e * s[3][x] for x in range(n)]

    def truth(e):
        o = objects(fam, e)
        R, K1, K2 = o["R"], fam.K(e, 1), fam.K(e, 2)
        Fv = matvec(R, S(e, 0))
        Dv = matvec(R, [a + b for a, b in zip(matvec(K1, Fv), S(e, 1))])
        Hv = matvec(R, [a + 2 * b + c for a, b, c in zip(matvec(K2, Fv), matvec(K1, Dv), S(e, 2))])
        return Fv, Dv, Hv
    F0, D0, H0 = truth(e0)
    o0 = objects(fam, e0)
    one = [F(1)] * n
    if adversarial:          # residual = constant vector on the selected objects: the order-0 bound is attained
        eps = F(1, 10 ** 4)
        sel = {"all": "FDH", "D_only": "D", "H_only": "H"}[adversarial if isinstance(adversarial, str) else "all"]
        Ra = matvec(o0["R"], one)
        Fh = [f - (eps * a if "F" in sel else 0) for f, a in zip(F0, Ra)]
        Dh = [d - (eps * a if "D" in sel else 0) for d, a in zip(D0, Ra)]
        Hh = [h - (eps * a if "H" in sel else 0) for h, a in zip(H0, Ra)]
    else:
        Fh = [f + F(rng.randint(-100, 100), 10 ** 5) for f in F0]
        Dh = [d + F(rng.randint(-100, 100), 10 ** 5) for d in D0]
        Hh = [h + F(rng.randint(-100, 100), 10 ** 5) for h in H0]
    exact_src = isinstance(adversarial, str) and adversarial != "all"
    Sh = [x + (0 if exact_src else F(rng.randint(-5, 5), 10 ** 6)) for x in S(e0, 0)]
    S1h = [x + (0 if exact_src else F(rng.randint(-5, 5), 10 ** 6)) for x in S(e0, 1)]
    S2h = [x + (0 if exact_src else F(rng.randint(-5, 5), 10 ** 6)) for x in S(e0, 2)]

    def residuals(e):
        I = eye(n)
        K, K1, K2 = fam.K(e), fam.K(e, 1), fam.K(e, 2)
        A = sub(I, K)
        rF = [a - b for a, b in zip(matvec(A, Fh), Sh)]
        rD = [a - b - c for a, b, c in zip(matvec(A, Dh), matvec(K1, Fh), S1h)]
        rH = [a - b - 2 * c - d for a, b, c, d in zip(matvec(A, Hh), matvec(K2, Fh), matvec(K1, Dh), S2h)]
        sF = vnorm([a - b for a, b in zip(Sh, S(e, 0))])
        sD = vnorm([a - b for a, b in zip(S1h, S(e, 1))])
        sH = vnorm([a - b for a, b in zip(S2h, S(e, 2))])
        return vnorm(rF), vnorm(rD), vnorm(rH), sF, sD, sH
    cell_drifts = [e0 - rho + 2 * rho * F(i, 4) for i in range(5)]
    mid = residuals(e0)
    cell_res = [residuals(e) for e in cell_drifts]
    lam_cell = [max(r[i] for r in cell_res) for i in range(6)]
    return {"e0": e0, "rho": rho, "mid": mid, "cell": lam_cell, "Fh": Fh, "Dh": Dh, "Hh": Hh, "F0": F0, "D0": D0,
            "cell_drifts": cell_drifts, "truth": truth}


def record_like(fx):
    """A record-shaped dict (the fields deflated_radii reads) from a DAG fixture; one object r = 0 replicated."""
    lm, lc = fx["mid"], fx["cell"]
    obj = {f"{k}_{r}": {"delta_mid": str(lm[i]), "delta_cell": str(lc[i])}
           for r in range(5) for i, k in ((0, "F"), (1, "dF"), (2, "H"))}
    em = {"Sclosed:0": str(lm[3]), "Sclosed:1": str(lm[4]), "Sclosed:2": str(lm[5])}
    ec = {"Sclosed:0": str(lc[3]), "Sclosed:1": str(lc[4]), "Sclosed:2": str(lc[5])}
    for r in range(1, 5):
        for k in range(3):
            em[f"S:{r}:{k}"] = em[f"Sclosed:{k}"]
            ec[f"S:{r}:{k}"] = ec[f"Sclosed:{k}"]
    return {"objects": obj, "eps_mid": em, "eps_cell": ec}


def radii_variant(rec, A, variant=None):
    if variant is None:
        return DC.deflated_radii(rec, A)
    r = DC.deflated_radii(rec, A)
    obj, em, ec = rec["objects"], rec["eps_mid"], rec["eps_cell"]
    for k in range(5):
        fF_mid = F(obj[f"F_{k}"]["delta_mid"]) + F(em[DC.source_node(k, 0)])
        fD_mid = F(obj[f"dF_{k}"]["delta_mid"]) + F(em[DC.source_node(k, 1)])
        fF_cell = F(obj[f"F_{k}"]["delta_cell"]) + F(ec[DC.source_node(k, 0)])
        fD_cell = F(obj[f"dF_{k}"]["delta_cell"]) + F(ec[DC.source_node(k, 1)])
        fH_cell = F(obj[f"H_{k}"]["delta_cell"]) + F(ec[DC.source_node(k, 2)])
        fH_mid = F(obj[f"H_{k}"]["delta_mid"]) + F(em[DC.source_node(k, 2)])
        if variant == "M08_point_certificate_as_whole_cell":
            r[k]["H"] = A["A0"] * fH_mid + 2 * A["A1"] * fD_mid + A["A2"] * fF_mid
        elif variant == "M12_drop_source_error":
            r[k]["F"] = A["A0"] * F(obj[f"F_{k}"]["delta_mid"])
            r[k]["D"] = A["A0"] * F(obj[f"dF_{k}"]["delta_mid"]) + A["A1"] * F(obj[f"F_{k}"]["delta_mid"])
            r[k]["H"] = (A["A0"] * F(obj[f"H_{k}"]["delta_cell"]) + 2 * A["A1"] * F(obj[f"dF_{k}"]["delta_cell"])
                         + A["A2"] * F(obj[f"F_{k}"]["delta_cell"]))
        elif variant == "M13_drop_factor_two":
            r[k]["H"] = A["A0"] * fH_cell + A["A1"] * fD_cell + A["A2"] * fF_cell
        elif variant == "M14_drop_order0_in_derivative":
            r[k]["D"] = A["A1"] * fF_mid
        else:
            raise KeyError(variant)
    return r


RADII_MUTANTS = ("M08_point_certificate_as_whole_cell", "M12_drop_source_error", "M13_drop_factor_two",
                 "M14_drop_order0_in_derivative")


def check_dag(fam, seed, adversarial, rule):
    fx = dag_fixture(fam, seed, adversarial)
    cell_obs = [objects(fam, e) for e in fx["cell_drifts"]]
    A, _ = consts_over(fam, fx["cell_drifts"], rule, cell_obs)
    rec = record_like(fx)
    viol, mut = [], {m: 0 for m in RADII_MUTANTS}
    errF = abs(fx["Fh"][0] - fx["F0"][0])
    errD = abs(fx["Dh"][0] - fx["D0"][0])
    errH = max(abs(fx["Hh"][0] - fx["truth"](e)[2][0]) for e in fx["cell_drifts"])
    rad = radii_variant(rec, A)[0]
    for tag, err, r in (("F", errF, rad["F"]), ("D", errD, rad["D"]), ("H", errH, rad["H"])):
        if err > r:
            viol.append(f"Q3 {rule} {tag} err {float(err):.3e} > radius {float(r):.3e}")
    for m in RADII_MUTANTS:
        rm = radii_variant(rec, A, m)[0]
        if errF > rm["F"] or errD > rm["D"] or errH > rm["H"]:
            mut[m] += 1
    return viol, mut, {"errF": float(errF), "radF": float(rad["F"]), "errD": float(errD), "radD": float(rad["D"]),
                       "errH": float(errH), "radH": float(rad["H"])}


# ------------------------------------------------------------------------------------------------ Q4 / Q5 / consumer mutants
def tighten_variant(interval, eps_rec, eps_new, m, variant=None):
    if variant is None:
        return DC.tighten(interval, eps_rec, eps_new, m)
    lo, hi = interval
    if variant == "M10_suppress_new_radius":
        d = sum((F(1, m) * a for a in eps_rec), F(0))
    elif variant == "M15_coefficient_one":
        d = sum((max(F(0), a - b) for a, b in zip(eps_rec, eps_new)), F(0))
    else:
        raise KeyError(variant)
    return lo + d, hi - d


TIGHTEN_MUTANTS = ("M10_suppress_new_radius", "M15_coefficient_one")


def check_tighten(seed):
    rng = random.Random(seed)
    viol, mut = [], {m: 0 for m in TIGHTEN_MUTANTS}
    for _ in range(200):
        m = rng.choice([1, 2, 3, 5])
        truth = [F(rng.randint(-1000, 1000), 1000) for _ in range(m)]
        eps_rec = [F(rng.randint(1, 1000), 1000) for _ in range(m)]
        eps_new = [e * F(rng.randint(1, 1000), 1000) for e in eps_rec]
        centres = [t + F(rng.randint(-1000, 1000), 1000) * en for t, en in zip(truth, eps_new)]   # |t - c| <= eps_new
        w = F(rng.randint(-100, 100), 1000)
        wr = F(rng.randint(0, 100), 1000)
        c0 = sum((F(1, m) * c for c in centres), F(0)) + w
        half = sum((F(1, m) * e for e in eps_rec), F(0)) + wr
        lo, hi = c0 - half - F(rng.randint(0, 5), 10 ** 6), c0 + half + F(rng.randint(0, 5), 10 ** 6)
        wtrue = w + F(rng.randint(-100, 100), 100) * wr
        value = sum((F(1, m) * t for t in truth), F(0)) + wtrue
        nlo, nhi = tighten_variant((lo, hi), eps_rec, eps_new, m)
        if not (nlo <= value <= nhi):
            viol.append("Q4 truth outside the tightened interval")
        for v in TIGHTEN_MUTANTS:
            a, b = tighten_variant((lo, hi), eps_rec, eps_new, m, v)
            if not (a <= value <= b):
                mut[v] += 1
    # refusals
    refused = 0
    try:
        DC.tighten((F(0), F(1, 10)), [F(1)], [F(1, 2)], 1)
    except DC.DeflationRefusal:
        refused += 1
    return viol, mut, refused


def check_refusals():
    ok = {}

    def refuses(fn):
        try:
            fn()
        except (DC.DeflationRefusal, ZeroDivisionError):
            return True
        return False
    ok["Dlo_nonpositive"] = refuses(lambda: DC.atom_constants(F(2), F(3), F(0), F(0), F(0)))
    ok["tau_below_one"] = refuses(lambda: DC.atom_constants(F(1, 2), F(3), F(1, 10), F(0), F(0)))
    ok["C_below_tau"] = refuses(lambda: DC.atom_constants(F(4), F(3), F(1, 10), F(0), F(0)))
    ok["Abar_below_one"] = refuses(lambda: DC.atom_constants_r2(F(1, 2), F(2), F(3), F(1, 10), F(0), F(0)))
    reg = {"rule": "r2", "blocks": [{"e_lo": "0", "e_hi": "1/100", "Abar": "400", "C_T": "20", "tau": "8",
                                     "D_lo": "1/100", "D1": "1/10", "D2": "2"}]}
    ok["uncovered_cell_returns_none"] = DC.block_for(reg, F(1, 200), F(3, 200)) is None
    ok["adjacent_block_not_used_r2"] = DC.block_for(reg, F(1, 100), F(2, 100)) is None
    # a closed class that is never killed and never reaches the atom: no taboo resolvent exists
    B = [[F(1, 2), F(1, 4), F(0)], [F(0), F(1, 2), F(1, 2)], [F(0), F(1, 2), F(1, 2)]]
    fam = Family("closed_class", B, [F(0)] * 3, [F(0)] * 3, (F(0), F(0)))
    ok["closed_class_no_taboo_resolvent"] = refuses(lambda: objects(fam, F(0)))
    return ok


def run() -> dict:
    fams = make_families()
    fixtures = [check_fixture(f) for f in fams]
    dag = []
    dag_mut = {m: 0 for m in RADII_MUTANTS}
    for f in fams:
        for rule in ("r1", "r2"):
            for adv in ("all", "D_only", "H_only", False):
                v, mu, info = check_dag(f, 7, adv, rule)
                dag.append({"family": f.name, "rule": rule, "adversarial": adv, "violations": v, **info})
                for k, c in mu.items():
                    dag_mut[k] += c
    tv, tmut, tref = check_tighten(11)
    refusals = check_refusals()
    # M07: a block reused outside its certified cover (no coverage check) must be caught by the cover fixture
    reg = {"rule": "r2", "blocks": [{"e_lo": "0", "e_hi": "1/100", "Abar": "400", "C_T": "20", "tau": "8",
                                     "D_lo": "1/100", "D1": "1/10", "D2": "2"}]}
    m07 = [b for b in reg["blocks"] if F(b["e_lo"]) < F(3, 200) and F(1, 200) < F(b["e_hi"])]
    tmut["M07_block_outside_certified_cover"] = int(bool(m07) and DC.block_for(reg, F(1, 200), F(3, 200)) is None)
    # M16: the taboo value w(a) (tau) used as the whole-kernel ARL bound Abar
    m16 = 0
    for x in fixtures:
        c = x["constants"]
        if c["tau"] < c["ARL_max"]:
            m16 += 1
    tmut["M16_taboo_value_as_ARL"] = m16
    const_mut = {m: sum(x["mutant_violations"][m] for x in fixtures) for m in CONSTANT_MUTANTS}
    mutants = {**const_mut, **dag_mut, **tmut}
    violations = [v for x in fixtures for v in x["violations"]] + [v for d in dag for v in d["violations"]] + tv
    res = {"schema": "rebaseguard.p5y.k5.perron-deflation.qualification-ad.v1",
           "families": [f.name for f in fams], "fixtures": fixtures, "dag": dag,
           "tighten": {"violations": len(tv), "refusal_fired": tref},
           "refusals": refusals, "mutants_detected": mutants,
           "violations": violations,
           "Q_PASS": not violations and all(refusals.values()) and tref == 1,
           "MUTATION_PASS": all(c > 0 for c in mutants.values()),
           "consumer_code_sha256": hashlib.sha256((HERE.parent / "deflated_consume.py").read_bytes()).hexdigest(),
           "code_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest()}
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run()
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("Q_PASS", "MUTATION_PASS", "mutants_detected", "refusals")}, indent=1))
    print("violations:", res["violations"][:10])
    return 0 if res["Q_PASS"] and res["MUTATION_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
