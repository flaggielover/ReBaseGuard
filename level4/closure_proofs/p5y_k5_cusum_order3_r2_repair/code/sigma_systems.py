"""Manufactured sigma-SYMMETRIC chain systems with exact truth, and exact graded residuals. NON-SCIENTIFIC.

State dimension n = 3, involution sigma = swap of components 1 and 2, fixed point x0 = component 0. Centre e = 0:

    K(e) = sum_p A_p e^p,  sigma A_p sigma = (-1)^p A_p        J(e) = sum_p B_p e^p,  sigma B_p sigma = (-1)^(p+1) B_p
    h_1(e) = sum_p a_p e^p, sigma a_p = (-1)^p a_p              S_0(e) = sum_p b_p e^p, sigma b_p = (-1)^(p+1) b_p

so K_i(0) has parity (-1)^i and J_i(0) parity (-1)^(i+1), exactly the CUSUM structure at e = 0. A_0 is a scaled
sigma-commuting row-stochastic matrix with a Perron (even) eigenvalue 1 - delta and an odd eigenvalue
(1 - delta)(1 - d - 2c): large C_e0, moderate C_o0, as in the CUSUM e = 0 operator estimate.

Everything exact (Fractions): truth from the R1 ChainSystem expansion, candidates from the R1 Rigorous class (truth +
LCG noise, optional parity-pure perturbations re-solved exactly), residuals of every DAG equation at e0, cell
envelopes, C, C_e0, C_o0, cell and hull norms. The Arb conversion happens in `engine_inputs`.
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from math import comb, factorial
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R1_CODE = NS.parents[0] / "p5y_k5_cusum_order3_real_producer/code"
if str(R1_CODE) not in sys.path:
    sys.path.append(str(R1_CODE))

import manufactured_chain as MC  # noqa: E402  (R1, frozen)

N_DIM = 3


def sig_v(v):
    return [v[0], v[2], v[1]]


def sig_m(A):
    P = [0, 2, 1]
    return [[A[P[i]][P[j]] for j in range(3)] for i in range(3)]


def proj_v(v, s):
    w = sig_v(v)
    return [(a + s * b) / 2 for a, b in zip(v, w)]


def proj_m(A, s):
    B = sig_m(A)
    return [[(A[i][j] + s * B[i][j]) / 2 for j in range(3)] for i in range(3)]


def build(spec: dict) -> MC.ChainSystem:
    g = MC.Rng(int(spec["seed"]))
    Ct = Fr(spec["C_target"])
    delta = Fr(1001, 1000) / Ct
    b, d, c = Fr(spec.get("b", "1/5")), Fr(spec.get("d", "1/10")), Fr(spec.get("c", "1/10"))
    stoch = [[1 - 2 * b, b, b], [d, 1 - d - c, c], [d, c, 1 - d - c]]
    A0 = MC.mscale(1 - delta, stoch)
    deg = int(spec.get("deg", 2))
    kscale = Fr(spec.get("k_scale", "1/2"))

    def rnd_m(scale):
        return [[g.frac(1000, 1000) * scale for _ in range(3)] for _ in range(3)]

    def rnd_v(scale):
        return [g.frac(1000, 1000) * scale for _ in range(3)]

    A = [A0] + [proj_m(rnd_m(kscale / factorial(p)), (-1) ** p) for p in range(1, deg + 1)]
    B = [proj_m(rnd_m(Fr(1, 2) / factorial(p)), (-1) ** (p + 1)) for p in range(deg + 1)]
    a = [proj_v(rnd_v(Fr(1, factorial(p))), (-1) ** p) for p in range(deg + 1)]
    bb = [proj_v(rnd_v(Fr(1, factorial(p))), (-1) ** (p + 1)) for p in range(deg + 1)]
    return MC.ChainSystem(3, A, B, a, bb, Fr(0), f"sigma_{spec['id']}")


def _inv(M):
    n = len(M)
    cols = [MC.solve(M, [Fr(1) if i == j else Fr(0) for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def parity_resolvents(sysm: MC.ChainSystem) -> tuple[Fr, Fr, Fr]:
    """||A0^-1||, ||A0^-1 P_e||, ||A0^-1 P_o|| (infinity norm) at e = 0: valid bounds on the restrictions."""
    A0 = [[(Fr(1) if i == j else Fr(0)) - sysm.A[0][i][j] for j in range(3)] for i in range(3)]
    Ai = _inv(A0)
    Sg = [[Fr(1), Fr(0), Fr(0)], [Fr(0), Fr(0), Fr(1)], [Fr(0), Fr(1), Fr(0)]]          # the permutation sigma
    Pe = [[(Fr(int(i == j)) + Sg[i][j]) / 2 for j in range(3)] for i in range(3)]
    Po = [[(Fr(int(i == j)) - Sg[i][j]) / 2 for j in range(3)] for i in range(3)]
    mul = lambda X, Y: [[sum(X[i][k] * Y[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return MC.mnorm(Ai), MC.mnorm(mul(Ai, Pe)), MC.mnorm(mul(Ai, Po))


def gnorm(v):
    """(||P_e v||, ||P_o v||, ||v||)."""
    return MC.vnorm(proj_v(v, 1)), MC.vnorm(proj_v(v, -1)), MC.vnorm(v)


class GradedRig:
    def __init__(self, sysm: MC.ChainSystem, e0: Fr, rho: Fr, *, seed: int, noise: Fr, perturb=None):
        self.sysm, self.e0, self.rho = sysm, e0, rho
        rig = MC.Rigorous(sysm, e0, rho, seed=seed, noise=noise)
        self.rig = rig
        ex = rig.ex
        D = MC.ChainSystem.deriv
        P = rig.P
        Kd = [MC.mscale(factorial(i), ex["K"][i]) if i < len(ex["K"]) else MC.zeros_m(3) for i in range(5)]
        Jd = [MC.mscale(factorial(i), ex["J"][i]) if i < len(ex["J"]) else MC.zeros_m(3) for i in range(5)]
        I_K0 = [[(Fr(1) if a == b else Fr(0)) - Kd[0][a][b] for b in range(3)] for a in range(3)]
        if perturb is not None:
            # parity-pure perturbation of one F order (vector), higher orders re-solved EXACTLY from it, so the
            # error reaches the higher orders only through the graded propagation edges
            order, vec = perturb
            for r in range(5):
                cands = []
                for q in range(4):
                    if q < order:
                        v = D(ex["F"][r], q)
                    elif q == order:
                        v = MC.vadd(D(ex["F"][r], q), vec)
                    else:
                        rhs = D(ex["S"][0], q) if r == 0 else list(P["S", r, q])
                        for i in range(1, q + 1):
                            rhs = MC.vadd(rhs, MC.vscale(comb(q, i), MC.matvec(Kd[i], cands[q - i])))
                        v = MC.solve(I_K0, rhs)
                    cands.append(v)
                for fam, q in (("F", 0), ("D", 1), ("H", 2), ("G", 3)):
                    P[fam, r, 0] = cands[q]
        self.P = P
        self.sup = {key: MC.vnorm(v) for key, v in P.items()}
        self.k, self.j, self.C = rig.k, rig.j, rig.C
        left, right = e0 - rho, e0 + rho
        lo, hi = min(Fr(0), left), max(Fr(0), right)
        hc, hr = (lo + hi) / 2, (hi - lo) / 2
        exh = sysm.expand(hc, 1)
        self.k_hull = [MC.sup_deriv_poly(exh["K"], i, hr, mat=True) for i in range(6)]
        self.j_hull = [MC.sup_deriv_poly(exh["J"], i, hr, mat=True) for i in range(6)]
        self.eta_mid, self.eta_cell = abs(e0), max(abs(left), abs(right))
        self.C_full0, self.C_e0, self.C_o0 = parity_resolvents(sysm)
        T = rig.T
        k_, j_ = self.k, self.j
        self.R = {}
        self._ar = None

    def _graded_residuals(self, G=None):
        """Exact graded residuals; the cell envelope uses graded_dag.graded_env / graded_true_sup in Arb."""
        if G is None:
            import graded_dag as G
        import rung3_engine as R1E
        ex = R1E.exact
        rig, P, rho, D = self.rig, self.P, self.rho, MC.ChainSystem.deriv
        exr, T = rig.ex, rig.T
        Kd = [MC.mscale(factorial(i), exr["K"][i]) if i < len(exr["K"]) else MC.zeros_m(3) for i in range(5)]
        Jd = [MC.mscale(factorial(i), exr["J"][i]) if i < len(exr["J"]) else MC.zeros_m(3) for i in range(5)]
        kA = {i: ex(self.k[i]) for i in range(6)}
        jA = {i: ex(self.j[i]) for i in range(6)}
        khA = {i: ex(self.k_hull[i]) for i in range(6)}
        jhA = {i: ex(self.j_hull[i]) for i in range(6)}
        eta = ex(self.eta_cell)
        rhoA = ex(rho)

        def sv(v):
            ge, go, gt = gnorm(v)
            return G.V(ex(ge), ex(go), ex(gt))

        R = {}

        def res(name, vec, env: "G.V"):
            m = sv(vec)
            R[name] = {"mid": (m.e, m.o, m.t), "cell": (m.e + rhoA * env.e, m.o + rhoA * env.o, m.t + rhoA * env.t)}

        for kk in range(4):
            # h_1 even (derivative k parity (-1)^k); S_0 odd (parity (-1)^(k+1)); envelope = sup of the next derivative
            res(f"h_1:{kk}", MC.vsub(P["h", 1, kk], D(exr["h"][1], kk)),
                G.graded_true_sup((-1) ** (kk + 1), ex(T["h", 1, kk + 1]), ex(T["h", 1, kk + 2]), eta))
            envS = G.graded_true_sup((-1) ** kk, ex(T["S", 0, kk + 1]), ex(T["S", 0, kk + 2]), eta)
            res(f"S_0:{kk}", MC.vsub(P["S", 0, kk], D(exr["S"][0], kk)), envS)
            R[f"Sclosed_{kk}"] = {"mid": (ex(0), ex(0), ex(0)), "cell": (rhoA * envS.e, rhoA * envS.o, rhoA * envS.t)}
        for jj in range(2, 5):
            for kk in range(4):
                v, terms = list(P["h", jj, kk]), []
                for i in range(kk + 1):
                    v = MC.vsub(v, MC.vscale(comb(kk, i), MC.matvec(Kd[i], P["h", jj - 1, kk - i])))
                    terms.append((comb(kk, i), "K", i + 1, sv(P["h", jj - 1, kk - i])))
                res(f"h_{jj}:{kk}", v, G.graded_env(terms, kA, jA, khA, jhA, eta))
        for r in range(1, 5):
            for kk in range(4):
                v, terms = list(P["S", r, kk]), []
                for i in range(kk + 1):
                    v = MC.vsub(v, MC.vscale(comb(kk, i), MC.matvec(Jd[i], P["h", r, kk - i])))
                    terms.append((comb(kk, i), "J", i + 1, sv(P["h", r, kk - i])))
                res(f"S_{r}:{kk}", v, G.graded_env(terms, kA, jA, khA, jhA, eta))
        fams = ("F", "D", "H", "G")
        for r in range(5):
            for n in range(4):
                X = P[fams[n], r, 0]
                v = MC.vsub(X, MC.matvec(Kd[0], X))
                terms = [(1, "K", 1, sv(X))]
                for i in range(1, n + 1):
                    v = MC.vsub(v, MC.vscale(comb(n, i), MC.matvec(Kd[i], P[fams[n - i], r, 0])))
                    terms.append((comb(n, i), "K", i + 1, sv(P[fams[n - i], r, 0])))
                src = D(exr["S"][0], n) if r == 0 else P["S", r, n]
                res(f"F_{r}:{n}", MC.vsub(v, src), G.graded_env(terms, kA, jA, khA, jhA, eta))
        for (r, jj) in MC.W_INDICES:
            for kk in range(4):
                v, terms = list(P["W", (r, jj), kk]), []
                for i in range(kk + 1):
                    v = MC.vsub(v, MC.vscale(comb(kk, i), MC.matvec(Kd[i], P["W", (r, jj - 1), kk - i])))
                    terms.append((comb(kk, i), "K", i + 1, sv(P["W", (r, jj - 1), kk - i])))
                res(f"W_{r}_{jj}:{kk}", v, G.graded_env(terms, kA, jA, khA, jhA, eta))
        return R

    def engine_inputs(self, *, origin: bool = True, graded=None) -> dict:
        """Must be called inside the certifying precision context."""
        import rung3_engine as R1E
        ex = R1E.exact
        inp = {"C": ex(self.C), "C_e0": ex(self.C_e0), "C_o0": ex(self.C_o0),
               "k": {i: ex(self.k[i]) for i in range(6)}, "j": {i: ex(self.j[i]) for i in range(6)},
               "k_hull": {i: ex(self.k_hull[i]) for i in range(6)}, "j_hull": {i: ex(self.j_hull[i]) for i in range(6)},
               "eta_mid": ex(self.eta_mid), "eta_cell": ex(self.eta_cell), "x0_sigma_fixed": True,
               "res": self._graded_residuals(graded)}
        if origin:
            inp["origin"] = {("G", r): ex(self.P["G", r, 0][0]) for r in range(5)} | \
                            {("W", (r, jj)): ex(self.P["W", (r, jj), 3][0]) for r in range(4) for jj in range(4 - r)}
        return inp


def graded_violations(gr: GradedRig, out: dict, *, parity: bool, grid: int = 16) -> list[str]:
    """Exact containment of every (e, o, t) node bound (midpoint at e0, cell on the grid) and of the export."""
    import rung3_engine as R1E
    sysm, P, e0, rho = gr.sysm, gr.P, gr.e0, gr.rho
    up = R1E.upper_fraction
    viol = []
    fams = ("F", "D", "H", "G")

    def candidates_and_truth(tr, e):
        exe = sysm.expand(e, 4)
        D = MC.ChainSystem.deriv
        rows = []
        for kk in range(4):
            rows.append((f"h:1:{kk}", P["h", 1, kk], tr[("h", 1)][kk]))
            rows.append((f"S:0:{kk}", P["S", 0, kk], tr[("S", 0)][kk]))
            rows.append((f"Sclosed:{kk}", D(gr.rig.ex["S"][0], kk), D(exe["S"][0], kk)))
        for jj in range(2, 5):
            for kk in range(4):
                rows.append((f"h:{jj}:{kk}", P["h", jj, kk], tr[("h", jj)][kk]))
        for r in range(1, 5):
            for kk in range(4):
                rows.append((f"S:{r}:{kk}", P["S", r, kk], tr[("S", r)][kk]))
        for r in range(5):
            for n in range(4):
                rows.append((f"F:{r}:{n}", P[fams[n], r, 0], tr[("F", r)][n]))
        for (r, jj) in MC.W_INDICES:
            for kk in range(4):
                rows.append((f"W:{r}:{jj}:{kk}", P["W", (r, jj), kk], tr[("W", (r, jj))][kk]))
        return rows

    def check(nodes, tr, e, tag):
        for name, cand, truth in candidates_and_truth(tr, e):
            ge, go, gt = gnorm(MC.vsub(cand, truth))
            v = nodes[name]
            for lab, val, bnd in (("e", ge, v.e), ("o", go, v.o), ("t", gt, v.t)):
                if val > up(bnd):
                    viol.append(f"{tag} {name}.{lab}: {float(val):.3e} > {float(up(bnd)):.3e}")

    tr0 = sysm.truth(e0)
    check(out["mid"]["nodes"], tr0, e0, "mid")
    pts = [e0 - rho + 2 * rho * Fr(g, grid) for g in range(grid + 1)]
    for e in pts:
        tr = sysm.truth(e)
        check(out["cell"]["nodes"], tr, e, f"cell e={e}")
        for m, v in out["m"].items():
            t = sysm.true_R(e, m, 3, tr)
            L, U = v["R3_cell"]
            if not L <= t <= U:
                viol.append(f"export e={e} m={m}")
    for m, v in out["m"].items():
        t = sysm.true_R(e0, m, 3, tr0)
        if not v["R3_mid"][0] <= t <= v["R3_mid"][1]:
            viol.append(f"export mid m={m}")
    return viol
