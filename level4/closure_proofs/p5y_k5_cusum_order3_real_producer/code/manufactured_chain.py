"""Manufactured analytic CHAIN systems with exact derivatives, and a rigorous Arb backend for them.

NON-SCIENTIFIC. No detector, cell table, K1 record or CUSUM operator. The structure copies the CUSUM raw DAG so the
order-3 engine and the rung-3 residual are exercised exactly as the real producer wires them:

    K(e), J(e)       n x n rational matrix polynomials in t = e - c
    h_1(e), S_0(e)   rational vector polynomials ("closed forms")
    h_j = K h_(j-1)  (j = 2..4),   S_r = J h_r  (r = 1..4)
    F_r = (I - K)^-1 S_r,   W_(r,0) = S_r,   W_(r,j) = K W_(r,j-1)
    R_m^(n)(e) = sum_c c * X^(n)(e)[0]   (frozen coefficient table)

Exact truth: Taylor coefficients about any rational point (polynomials shift exactly; the resolvent by the exact
recursion (I - K_0) f_q = s_q + sum_(p>=1) K_p f_(q-p)). Rigorous certified inputs for the engine:

    norms      k_i, j_i = sup_cell ||K^(i)||, ||J^(i)||  by the triangle inequality on the expansion about e0
    C          1 / (1 - k_0)  (refused unless k_0 < 1)
    towers     sup_cell ||X^(n)|| for polynomial objects, the same triangle bound
    mid        EXACT midpoint errors ||Xhat - X(e0)||
    cell       ||Xhat_n - X_n(e0)|| + sum_(q>=1) ||X_(n+q)(e0)|| rho^q / q!              (polynomials: exact sum)
               ||Xhat_n - X_n(e0)|| + sum_(q=1..3) ||X_(n+q)(e0)|| rho^q/q! + rho^4/4! TF_(n+4)  (resolvent)
    residuals  the SAME rung3_residual.g_residual code as the real producer, with ball matrices for K_i(e0);
               the order-3 source-chain residuals follow aux_certifier.aux_residuals term for term

All inputs are upper bounds on the quantities the engine's proofs require; tightness is not assumed.
"""
from __future__ import annotations

from fractions import Fraction as Fr
from math import comb, factorial

LCG_MOD = (1 << 61) - 1
W_INDICES = tuple((r, j) for r in range(4) for j in range(1, 4 - r))
M_VALUES = (1, 2, 3, 5)


class Rng:
    def __init__(self, seed: int):
        self.x = (seed * 6364136223846793005 + 1442695040888963407) % LCG_MOD

    def frac(self, span: int, den: int) -> Fr:
        self.x = (self.x * 3935559000370003845 + 2691343689449507681) % LCG_MOD
        return Fr(self.x % (2 * span + 1) - span, den)


def coefficients(m: int):
    rows = [("F", r, 0, Fr(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]
    return rows


# ------------------------------------------------------------------ exact linear algebra
def zeros_v(n):
    return [Fr(0)] * n


def zeros_m(n):
    return [[Fr(0)] * n for _ in range(n)]


def vadd(u, v):
    return [a + b for a, b in zip(u, v, strict=True)]


def vsub(u, v):
    return [a - b for a, b in zip(u, v, strict=True)]


def vscale(c, v):
    return [c * a for a in v]


def madd(A, B):
    return [vadd(a, b) for a, b in zip(A, B, strict=True)]


def mscale(c, A):
    return [vscale(c, a) for a in A]


def matvec(A, v):
    return [sum((a * b for a, b in zip(row, v, strict=True)), Fr(0)) for row in A]


def matmul(A, B):
    n = len(A)
    return [[sum((A[i][k] * B[k][j] for k in range(n)), Fr(0)) for j in range(n)] for i in range(n)]


def vnorm(v) -> Fr:
    return max(abs(x) for x in v)


def mnorm(A) -> Fr:
    return max(sum((abs(x) for x in row), Fr(0)) for row in A)


def solve(M, b):
    n = len(b)
    a = [list(row) + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = next((r for r in range(col, n) if a[r][col] != 0), None)
        if piv is None:
            raise ValueError("singular resolvent matrix")
        a[col], a[piv] = a[piv], a[col]
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col], strict=True)]
    return [a[i][n] / a[i][i] for i in range(n)]


# ------------------------------------------------------------------ polynomials with matrix / vector coefficients
def shift(coeffs, t0: Fr, *, matrix: bool):
    """Coefficients of P(t0 + s) in s, exactly."""
    deg = len(coeffs) - 1
    out = []
    for q in range(deg + 1):
        acc = None
        for p in range(q, deg + 1):
            term = (mscale if matrix else vscale)(comb(p, q) * t0 ** (p - q), coeffs[p])
            acc = term if acc is None else (madd if matrix else vadd)(acc, term)
        out.append(acc)
    return out


def polymat_vec(Kc, vc):
    """(sum K_p s^p)(sum v_q s^q), full degree."""
    n = len(vc[0])
    out = [zeros_v(n) for _ in range(len(Kc) + len(vc) - 1)]
    for p, Kp in enumerate(Kc):
        for q, vq in enumerate(vc):
            out[p + q] = vadd(out[p + q], matvec(Kp, vq))
    return out


class ChainSystem:
    def __init__(self, n, A, B, a, b, centre: Fr, label: str):
        self.n, self.A, self.B, self.a, self.b, self.c, self.label = n, A, B, a, b, centre, label

    # ---- exact Taylor coefficients of every object about e (polynomials full degree; resolvent to order N)
    def expand(self, e: Fr, N: int = 8) -> dict:
        t0 = e - self.c
        Kc = shift(self.A, t0, matrix=True)
        Jc = shift(self.B, t0, matrix=True)
        h = {1: shift(self.a, t0, matrix=False)}
        for j in range(2, 5):
            h[j] = polymat_vec(Kc, h[j - 1])
        S = {0: shift(self.b, t0, matrix=False)}
        for r in range(1, 5):
            S[r] = polymat_vec(Jc, h[r])
        W = {}
        for r in range(4):
            W[(r, 0)] = S[r]
            for j in range(1, 4 - r):
                W[(r, j)] = polymat_vec(Kc, W[(r, j - 1)])
        I_K0 = [[(Fr(1) if i == j else Fr(0)) - Kc[0][i][j] for j in range(self.n)] for i in range(self.n)]
        F = {}
        for r in range(5):
            f = []
            for q in range(N + 1):
                rhs = list(S[r][q]) if q < len(S[r]) else zeros_v(self.n)
                for p in range(1, min(q, len(Kc) - 1) + 1):
                    rhs = vadd(rhs, matvec(Kc[p], f[q - p]))
                f.append(solve(I_K0, rhs))
            F[r] = f
        return {"K": Kc, "J": Jc, "h": h, "S": S, "W": W, "F": F}

    @staticmethod
    def deriv(coeffs, n: int):
        """n-th derivative at the expansion point: n! * coefficient n."""
        if n >= len(coeffs):
            return zeros_v(len(coeffs[0]))
        return vscale(factorial(n), coeffs[n])

    def truth(self, e: Fr) -> dict:
        ex = self.expand(e, 4)
        return {("F", r): [self.deriv(ex["F"][r], n) for n in range(4)] for r in range(5)} | \
               {("W", rj): [self.deriv(ex["W"][rj], n) for n in range(4)] for rj in ex["W"]} | \
               {("h", j): [self.deriv(ex["h"][j], n) for n in range(4)] for j in range(1, 5)} | \
               {("S", r): [self.deriv(ex["S"][r], n) for n in range(4)] for r in range(5)}

    def true_R(self, e: Fr, m: int, n: int, tr: dict | None = None) -> Fr:
        tr = self.truth(e) if tr is None else tr
        total = Fr(0)
        for kind, r, j, c in coefficients(m):
            v = tr[("F", r)] if kind == "F" else tr[("W", (r, j))]
            total += c * v[n][0]
        return total


# ------------------------------------------------------------------ rigorous cell bounds
def sup_deriv_poly(coeffs, n: int, rho: Fr, mat: bool = False) -> Fr:
    """sup_(|s|<=rho) ||P^(n)(e0+s)|| <= sum_(q>=n) q!/(q-n)! ||p_q|| rho^(q-n)."""
    nrm = mnorm if mat else vnorm
    return sum((Fr(factorial(q), factorial(q - n)) * nrm(coeffs[q]) * rho ** (q - n)
                for q in range(n, len(coeffs))), Fr(0))


def poly_cell_error(cand, coeffs, n: int, rho: Fr) -> Fr:
    """sup_cell ||cand - P^(n)(e)||: exact midpoint error plus the exact remaining expansion."""
    at = ChainSystem.deriv(coeffs, n)
    tail = sum((Fr(factorial(q), factorial(q - n)) * vnorm(coeffs[q]) * rho ** (q - n)
                for q in range(n + 1, len(coeffs))), Fr(0))
    return vnorm(vsub(cand, at)) + tail


class Rigorous:
    """All exact-rational certified inputs of one manufactured cell (no Arb yet)."""

    def __init__(self, sysm: ChainSystem, e0: Fr, rho: Fr, *, seed: int, noise: Fr, perturb=None):
        self.sysm, self.e0, self.rho = sysm, e0, rho
        ex = sysm.expand(e0, 8)
        self.ex = ex
        n = sysm.n
        self.k = [sup_deriv_poly(ex["K"], i, rho, mat=True) for i in range(9)]
        self.j = [sup_deriv_poly(ex["J"], i, rho, mat=True) for i in range(9)]
        if not self.k[0] < 1:
            raise ValueError("sup_cell ||K|| >= 1: no resolvent bound")
        self.C = 1 / (1 - self.k[0])
        g = Rng(seed + 7919)

        def nz(v):
            return [x + g.frac(1000, 1000) * noise for x in v] if noise else list(v)

        D = ChainSystem.deriv
        P = {}
        for j in range(1, 5):
            for q in range(4):
                P["h", j, q] = nz(D(ex["h"][j], q))
        for r in range(5):
            for q in range(4):
                P["S", r, q] = nz(D(ex["S"][r], q))
        P["Sclosed", 0, 3] = D(ex["S"][0], 3)
        for r in range(5):
            for fam, q in (("F", 0), ("D", 1), ("H", 2), ("G", 3)):
                P[fam, r, 0] = nz(D(ex["F"][r], q))
        if perturb is not None:
            # perturb one F derivative order by eta, then re-solve the higher orders EXACTLY from the perturbed
            # lower ones (as the design's manufactured.cell_inputs): the error enters only through the
            # propagation edges, so each edge's coefficient is load-bearing.
            order, eta = perturb
            Kd = [mscale(factorial(i), ex["K"][i]) if i < len(ex["K"]) else zeros_m(n) for i in range(4)]
            I_K0 = [[(Fr(1) if a == b else Fr(0)) - Kd[0][a][b] for b in range(n)] for a in range(n)]
            for r in range(5):
                cands = []
                for q in range(4):
                    if q < order:
                        v = D(ex["F"][r], q)
                    elif q == order:
                        v = [x + eta for x in D(ex["F"][r], q)]
                    else:
                        rhs = D(ex["S"][r], q) if r == 0 else list(P["S", r, q])
                        for i in range(1, q + 1):
                            rhs = vadd(rhs, vscale(comb(q, i), matvec(Kd[i], cands[q - i])))
                        v = solve(I_K0, rhs)
                    cands.append(v)
                for fam, q in (("F", 0), ("D", 1), ("H", 2), ("G", 3)):
                    P[fam, r, 0] = cands[q]
        for (r, j) in W_INDICES:
            for q in range(4):
                P["W", (r, j), q] = nz(D(ex["W"][(r, j)], q))
        for r in range(4):
            for q in range(4):
                P["W", (r, 0), q] = P["S", r, q]
        self.P = P
        self.sup = {key: vnorm(v) for key, v in P.items()}

        # towers (true objects, n <= 8)
        T = {}
        for jj in range(1, 5):
            for q in range(9):
                T["h", jj, q] = sup_deriv_poly(ex["h"][jj], q, rho)
        for r in range(5):
            for q in range(9):
                T["S", r, q] = sup_deriv_poly(ex["S"][r], q, rho)
        for rj, coeffs in ex["W"].items():
            for q in range(9):
                T["W", rj, q] = sup_deriv_poly(coeffs, q, rho)
        self.T = T
        # resolvent norm tower TF_n, n <= 8
        self.TF = {}
        for r in range(5):
            tf = []
            for q in range(9):
                acc = T["S", r, q] + sum((comb(q, i) * self.k[i] * tf[q - i] for i in range(1, q + 1)), Fr(0))
                tf.append(self.C * acc)
            self.TF[r] = tf

        mid, cell, ref = {}, {}, {}
        for jj in range(1, 5):
            for q in range(4):
                mid[f"h:{jj}:{q}"] = vnorm(vsub(P["h", jj, q], D(ex["h"][jj], q)))
                if q <= 2:
                    cell[f"h:{jj}:{q}"] = poly_cell_error(P["h", jj, q], ex["h"][jj], q, rho)
        for r in range(5):
            for q in range(4):
                mid[f"S:{r}:{q}"] = vnorm(vsub(P["S", r, q], D(ex["S"][r], q)))
                if q <= 2:
                    cell[f"S:{r}:{q}"] = poly_cell_error(P["S", r, q], ex["S"][r], q, rho)
        mid["Sclosed:3"] = Fr(0)
        for rj, coeffs in ex["W"].items():
            for q in range(4):
                mid[f"W:{rj[0]}:{rj[1]}:{q}"] = vnorm(vsub(P["W", rj, q], D(coeffs, q)))
                if q <= 2:
                    cell[f"W:{rj[0]}:{rj[1]}:{q}"] = poly_cell_error(P["W", rj, q], coeffs, q, rho)
        for r in range(5):
            for fam, q in (("F", 0), ("D", 1), ("H", 2)):
                e_mid = vnorm(vsub(P[fam, r, 0], D(ex["F"][r], q)))
                mid[f"{fam}:{r}"] = e_mid
                tail = sum((vnorm(D(ex["F"][r], q + p)) * rho ** p / factorial(p) for p in range(1, 4)), Fr(0))
                ref[f"{fam}:{r}"] = e_mid + tail + rho ** 4 / factorial(4) * self.TF[r][q + 4]
        self.mid, self.cell, self.refined = mid, cell, ref


# ------------------------------------------------------------------ Arb backend with the real residual interface
class VecBall:
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = list(v)

    def __add__(self, o):
        return VecBall([a + b for a, b in zip(self.v, o.v, strict=True)])

    def __sub__(self, o):
        return VecBall([a - b for a, b in zip(self.v, o.v, strict=True)])

    def scale(self, c):
        return VecBall([c * a for a in self.v])


class ManufacturedCert:
    """Duck-typed stand-in for the real Order3Certifier's residual surface (Arb at the ambient precision)."""

    def __init__(self, rig: Rigorous):
        from flint import arb
        from rung3_engine import exact
        self.rig = rig
        self.arb, self.exact = arb, exact
        self.z_range = arb(1)
        self.reward_allow = {3: arb(0)}
        self.P = {key: [exact(x) for x in v] for key, v in rig.P.items()}
        self.sup = {key: exact(v) for key, v in rig.sup.items()}
        self.norms = {"k": {i: exact(rig.k[i]) for i in range(9)}, "j": {i: exact(rig.j[i]) for i in range(9)}}
        D = ChainSystem.deriv
        self.Kd = {i: [[exact(x) for x in row] for row in mscale(factorial(i), rig.ex["K"][i])]
                   if i < len(rig.ex["K"]) else None for i in range(5)}
        self.Jd = {i: [[exact(x) for x in row] for row in mscale(factorial(i), rig.ex["J"][i])]
                   if i < len(rig.ex["J"]) else None for i in range(5)}
        self._D = D
        self.rho = exact(rig.rho)

    def eps_zi(self, i):
        return self.arb(0)

    def vec(self, poly):
        return VecBall(poly)

    def _apply(self, M, v):
        n = len(v.v)
        if M is None:
            return VecBall([self.arb(0)] * n)
        return VecBall([sum((a * b for a, b in zip(row, v.v)), self.arb(0)) for row in M])

    def K(self, poly, i):
        return self._apply(self.Kd[i], VecBall(poly))

    def J(self, poly, i):
        return self._apply(self.Jd[i], VecBall(poly))

    def certify(self, name, res, extra, env):
        rng = self.arb(0)
        for x in res.v:
            a = x.abs_upper()
            rng = a if a.upper() > rng.upper() else rng
        delta_mid = (rng + extra).abs_upper()
        return {"object": name, "delta_mid": delta_mid,
                "delta_cell": (delta_mid + self.rho * env.abs_upper()).abs_upper()}

    # ---- the order-3 source-chain residuals, term for term as aux_certifier.aux_residuals
    def aux_residuals(self) -> dict:
        arb, ex, k_, j_ = self.arb, self.rig.ex, self.norms["k"], self.norms["j"]
        exact, D = self.exact, self._D
        out = {}
        h1_true = VecBall([exact(x) for x in D(ex["h"][1], 3)])
        out["h_1:3"] = self.certify("h_1:3", VecBall(self.P["h", 1, 3]) - h1_true, arb(0),
                                    exact(self.rig.T["h", 1, 4]))
        s0_true = VecBall([exact(x) for x in D(ex["S"][0], 3)])
        out["S_0:3"] = self.certify("S_0:3", VecBall(self.P["S", 0, 3]) - s0_true, arb(0),
                                    exact(self.rig.T["S", 0, 4]))
        for jj in range(2, 5):
            res, env = VecBall(self.P["h", jj, 3]), arb(0)
            for i in range(4):
                res = res - self.K(self.P["h", jj - 1, 3 - i], i).scale(arb(comb(3, i)))
                env = env + arb(comb(3, i)) * k_[i + 1] * self.sup["h", jj - 1, 3 - i]
            out[f"h_{jj}:3"] = self.certify(f"h_{jj}:3", res, arb(0), env)
        for r in range(1, 5):
            res, env = VecBall(self.P["S", r, 3]), arb(0)
            for i in range(4):
                res = res - self.J(self.P["h", r, 3 - i], i).scale(arb(comb(3, i)))
                env = env + arb(comb(3, i)) * j_[i + 1] * self.sup["h", r, 3 - i]
            out[f"S_{r}:3"] = self.certify(f"S_{r}:3", res, arb(0), env)
        for (r, jj) in W_INDICES:
            res, env = VecBall(self.P["W", (r, jj), 3]), arb(0)
            for i in range(4):
                res = res - self.K(self.P["W", (r, jj - 1), 3 - i], i).scale(arb(comb(3, i)))
                env = env + arb(comb(3, i)) * k_[i + 1] * self.sup["W", (r, jj - 1), 3 - i]
            out[f"W_{r}_{jj}:3"] = self.certify(f"W_{r}_{jj}:3", res, arb(0), env)
        return out


def engine_inputs(cert: ManufacturedCert, g: dict, *, inflate: Fr = Fr(1)) -> dict:
    """The engine input dict, from rigorous manufactured bounds. `inflate` >= 1 widens every lower-order input."""
    rig, ex, arb = cert.rig, cert.exact, cert.arb
    if inflate < 1:
        raise ValueError("inflation must keep upper bounds valid")
    aux = cert.aux_residuals()
    return {
        "C": ex(rig.C), "rho": ex(rig.rho),
        "k": {i: ex(rig.k[i]) for i in range(5)}, "j": {i: ex(rig.j[i]) for i in range(5)},
        "mid": {kk: ex(v * inflate) for kk, v in rig.mid.items()},
        "cell": {kk: ex(v * inflate) for kk, v in rig.cell.items()},
        "refined": {kk: ex(v * inflate) for kk, v in rig.refined.items()},
        "aux": aux, "g": g,
        "towers": {kk: ex(v) for kk, v in rig.T.items() if kk[2] <= 4},
        "sup_S0_4": ex(rig.T["S", 0, 4]),
        "sup_hat": {(fam, r): ex(rig.sup[fam, r, 0]) for fam in ("F", "D", "H", "G") for r in range(5)},
        "origin": {("G", r): ex(rig.P["G", r, 0][0]) for r in range(5)}
        | {("W", (r, j)): ex(rig.P["W", (r, j), 3][0]) for r in range(4) for j in range(4 - r)},
    }


# ------------------------------------------------------------------ fixture families
def random_chain(seed: int, n: int, *, deg: int = 3, k0: Fr = Fr(1, 4), centre: Fr = Fr(0),
                 label: str = "random") -> ChainSystem:
    g = Rng(seed)

    def mat(scale):
        return [[g.frac(1000, 1000) * scale for _ in range(n)] for _ in range(n)]

    A = [mat(k0 / n)] + [mat(Fr(1, 8 * n * factorial(p))) for p in range(1, deg + 1)]
    B = [mat(Fr(1, 2 * n))] + [mat(Fr(1, 4 * n * factorial(p))) for p in range(1, deg + 1)]
    a = [[g.frac(1000, 1000) / factorial(p) for _ in range(n)] for p in range(deg + 1)]
    b = [[g.frac(1000, 1000) / factorial(p) for _ in range(n)] for p in range(deg + 1)]
    return ChainSystem(n, A, B, a, b, centre, label)


def ill_conditioned_chain(seed: int, *, C_target: int, deg: int = 2, centre: Fr = Fr(0)) -> ChainSystem:
    """3x3, K_0 with row sums 1 - 1/C_target (so C = C_target exactly when the cell adds no drift norm)."""
    g = Rng(seed)
    base = random_chain(seed, 3, deg=deg, centre=centre, label=f"ill_conditioned_C{C_target}")
    s = Fr(1) - Fr(1, C_target)
    K0 = [[Fr(1, 3) + g.frac(50, 1000) for _ in range(3)] for _ in range(3)]
    for row in K0:
        tot = sum(abs(x) for x in row)
        for i in range(3):
            row[i] = row[i] * s / tot
    base.A = [K0] + [mscale(Fr(1, 10 * C_target), M) for M in base.A[1:]]
    return base


def scalar_chain(K_coeffs, J_coeffs, h1_coeffs, S0_coeffs, centre: Fr, label: str) -> ChainSystem:
    return ChainSystem(1, [[[c]] for c in K_coeffs], [[[c]] for c in J_coeffs],
                       [[c] for c in h1_coeffs], [[c] for c in S0_coeffs], centre, label)


def with_target_R3_m1(sysm: ChainSystem, e0: Fr, target: Fr) -> ChainSystem:
    """Adjust the cubic coefficient of S_0 (in e - e0) so that R'''_1(e0) = F_0'''(e0)[0] = target exactly.

    Requires centre == e0 so that lower derivatives of S_0 at e0 are unchanged.
    """
    if sysm.c != e0:
        raise ValueError("centre must equal e0")
    base = sysm.true_R(e0, 1, 3)
    ex = sysm.expand(e0, 3)
    I_K0 = [[(Fr(1) if i == j else Fr(0)) - ex["K"][0][i][j] for j in range(sysm.n)] for i in range(sysm.n)]
    v = [target - base] + [Fr(0)] * (sysm.n - 1)
    delta = vscale(Fr(1, 6), matvec(I_K0, v))
    b = [list(x) for x in sysm.b] + [zeros_v(sysm.n)] * max(0, 4 - len(sysm.b))
    b[3] = vadd(b[3], delta)
    return ChainSystem(sysm.n, sysm.A, sysm.B, sysm.a, b, sysm.c, sysm.label + f"_R3m1={target}")
