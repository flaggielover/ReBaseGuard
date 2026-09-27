"""Residual-specific order-0 (RSO) route and its derivative extensions -- exact-truth validation on synthetic FSM families.

Target-free (no CUSUM cell, no committed tail value, no drift in the quarantined band).

Theorem RSO-0 (see RESIDUAL_SPECIFIC_309.md): if psi >= |phi_e| on X and v >= 0 with v >= psi + K_e v on X for every e in
the cell, then |(R_e phi_e)(a)| <= (R_e psi)(a) <= v(a) for every e in the cell.
Theorem RSO-PM (derivatives, positive majorant): with v0 as above, v1 >= |K_1(e)| v0 + K_e v1 and
v2 >= 2|K_1(e)| v1 + |K_2(e)| v0 + K_e v2, |((dR_e) f)(a)| <= v1(a) and |((d2R_e) f)(a)| <= v2(a) for all |f| <= psi.
Theorem RSO-LR (derivative, score form, one drift): on a likelihood-ratio family, ((dR) f)(a) = E_a[sum_{n<tau} f(X_n) M_n]
and E_a[sum psi(X_n)|M_n|] <= alpha(a) for the quadratic-in-mu supersolution V = alpha + beta mu^2.

Parts (declared rule DECLARED_RULE, fixed before the first run):
  R1  certificates: v built as lambda R_{e0} b + eta R_{e0} 1 on a fixed ladder, VERIFIED uniformly on the cell by two
      independent rigorous polynomial checks (Taylor-form bisection; grid + derivative Lipschitz bound);
  R2  soundness vs exact truth on a 17-point drift grid: (R_e a)(a), (R_e|K1|R_e a)(a), and the signed |(dR f)(a)|,
      |(d2R f)(a)| for f = +-a with random signs;
  R3  shape-factor classes: generic TC residuals; FAVOURABLE (mass on the least-occupied states); ADVERSARIAL (mass on
      the most-occupied state; constant psi);
  R4  theorem-TC assembly: radius with RSO-C4 (A0 f_H only), RSO-P (all terms, pointwise profile incl. the composite
      order-3 function), RSO-P on box classes g = 1, 2, n, checked POINTWISE against the exact F_r''(t)(a);
  R5  RSO-LR on discrete likelihood-ratio families: kernel identity K^S = K_1 (exact), signed LR identity by path
      enumeration, exact truncated lower bound <= certificate alpha(a), comparison with the PM and norm bounds;
  NC  (a) planted psi below |phi| at one state -> majorant check fails; (b) planted v := (9/10) v_cert -> the
      certificate check fails; (c) planted LR certificate alpha(a) := truncated lower bound * 9/10 -> soundness fails
      (harness control); (d) planted wrong score S(z) := z -> the kernel identity K^S = K_1 fails (structural control).
Writes validation/D309_RSO_FSM.json.
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_core as D  # noqa: E402

Q, X = D.Q, D.X

DECLARED_RULE = (
    "R1-R4 generic: seeds 1..12, n = 4 + seed % 4, kernel degree 4, e0 = 1/8, rho = (1/64, 1/32, 1/16)[seed % 3], "
    "pert = (1e-6, 1e-4, 1e-2)[(seed // 3) % 3], source degree (2, 5)[seed % 2], one source per fixture, G^ := 0. "
    "R3 favourable/adversarial: same families; FAVOURABLE a = 1 on states whose exact occupation at e0 is below the "
    "median, 1/100 elsewhere; ADVERSARIAL-ATOM a = 1 on the most occupied state, 1/100 elsewhere; ADVERSARIAL-CONST "
    "a = 1. Certificate ladder lambda in {1, 1+2^-10, 1+2^-8, 1+2^-6, 1+2^-4, 1+2^-2, 2}, eta/||b|| in {2^-12, "
    "2^-8, 2^-5, 2^-3, 2^-1, 1, 4}. Box classes: consecutive index groups of size g in {1, 2, n}. Drift grid 17 points. "
    "R5: discrete LR families on states 0..L-1 (L in {4, 5, 6}), z in {-1, 0, 1}, p_e(z) = p0(z)(1 + e z + e^2 c "
    "(z^2 - m2)), p0 = (1/4, 1/2, 1/4), c = 1/2, e in {1/8, 1/4}, e-independent killing 1/4, x' = max(0, x + z), alarm "
    "iff x + z >= L; psi = (1/100 + x/L) and psi = indicator of the top state; ladder c in 2^{-4..4}, delta in 2^{-8..2}; "
    "path enumeration N = 60. Fixed before the first run.")

LAMBDAS = [F(1), F(1) + F(1, 2 ** 10), F(1) + F(1, 2 ** 8), F(1) + F(1, 2 ** 6), F(1) + F(1, 2 ** 4),
           F(1) + F(1, 4), F(2)]
ETAS = [F(1, 2 ** 12), F(1, 2 ** 8), F(1, 2 ** 5), F(1, 2 ** 3), F(1, 2), F(1), F(4)]


# --------------------------------------------------------------------------------------------- certificates


def abs_sup_matrix(fam: X.DriftFamily, i: int, lo: F, hi: F) -> list:
    """entrywise rigorous sup_{e in [lo,hi]} |K_i(e)_{xy}|."""
    return [[D.sup_abs_on(D.p_deriv(p, i), lo, hi)[0] for p in row] for row in fam.kp]


def margin_poly(fam: X.DriftFamily, v: list, x: int) -> list:
    """v_x - sum_y K_xy(e) v_y as a polynomial in e."""
    acc = [v[x]]
    for y in range(fam.n):
        acc = D.p_add(acc, D.p_scale(fam.kp[x][y], v[y]), F(-1))
    return acc


def check_cert_taylor(fam, lo, hi, v, b) -> F:
    """RIGOROUS lower bound of min_x min_e [v_x - (K_e v)_x - b_x] (Taylor-form bisection)."""
    return min(D.min_on(margin_poly(fam, v, x), lo, hi) - b[x] for x in range(fam.n))


def check_cert_grid(fam, lo, hi, v, b, N: int = 256) -> F:
    """Independent RIGOROUS lower bound: grid minimum minus (h/2) * sup|q'| with a crude coefficient bound."""
    emax = max(abs(lo), abs(hi))
    best = None
    for x in range(fam.n):
        q = margin_poly(fam, v, x)
        dq = D.p_deriv(q, 1)
        lip = sum((abs(c) * emax ** k for k, c in enumerate(dq)), F(0))
        h = (hi - lo) / N
        gmin = min(D.p_eval(q, lo + h * j) for j in range(N + 1))
        val = gmin - h / 2 * lip - b[x]
        best = val if best is None else min(best, val)
    return best


def certify(fam, e0, rho, b: list) -> dict:
    """v >= b + K_e v on the cell, v = lam R_{e0} b + eta ||b|| R_{e0} 1 (first ladder pair with the smallest v(a))."""
    lo, hi = e0 - rho, e0 + rho
    D.guard_interval(lo, hi)
    R0 = fam.R(e0)
    u = D.mv(R0, b)
    w1 = D.mv(R0, [F(1)] * fam.n)
    nb = max(D.vnorm(b), F(1, 10 ** 30))
    cands = sorted(((lam * u[0] + eta * nb * w1[0], lam, eta) for lam in LAMBDAS for eta in ETAS),
                   key=lambda t: t[0])
    for va, lam, eta in cands:
        v = [lam * ui + eta * nb * wi for ui, wi in zip(u, w1)]
        if min(v) < 0:
            continue
        m1 = check_cert_taylor(fam, lo, hi, v, b)
        if m1 >= 0:
            m2 = check_cert_grid(fam, lo, hi, v, b)
            if m2 >= 0:  # accept only a pair that BOTH independent rigorous checks certify
                return {"v": v, "va": va, "lam": lam, "eta": eta, "margin_taylor": m1, "margin_grid": m2,
                        "verified_twice": True}
    raise RuntimeError("no ladder pair certifies")


def cert_chain(fam, e0, rho, a: list, K1abs: list, K2abs: list) -> dict:
    c0 = certify(fam, e0, rho, a)
    b1 = D.mv(K1abs, c0["v"])
    c1 = certify(fam, e0, rho, b1)
    b2 = D.vadd((F(2), D.mv(K1abs, c1["v"])), (F(1), D.mv(K2abs, c0["v"])))
    c2 = certify(fam, e0, rho, b2)
    return {"N0": c0, "N1": c1, "N2": c2}


# --------------------------------------------------------------------------------------------- truth


def truth_grid(fam, e0, rho, a: list, rng: random.Random, pts: int = 17) -> dict:
    lo = e0 - rho
    worst = {"R": F(0), "PM1": F(0), "PM2": F(0), "signed1": F(0), "signed2": F(0), "Lam": F(0)}
    signs = [F(rng.choice((-1, 1))) for _ in a]
    f = [s * x for s, x in zip(signs, a)]
    for j in range(pts):
        e = lo + 2 * rho * F(j, pts - 1)
        D.guard_interval(e, e)
        R = fam.R(e)
        K1, K2 = fam.K(e, 1), fam.K(e, 2)
        K1a = [[abs(x) for x in r] for r in K1]
        K2a = [[abs(x) for x in r] for r in K2]
        Ra = D.mv(R, a)
        pm1 = D.mv(R, D.mv(K1a, Ra))
        pm2 = D.mv(R, D.vadd((F(2), D.mv(K1a, pm1)), (F(1), D.mv(K2a, Ra))))
        Rf = D.mv(R, f)
        dRf = D.mv(R, D.mv(K1, Rf))
        d2Rf = D.vadd((F(2), D.mv(R, D.mv(K1, dRf))), (F(1), D.mv(R, D.mv(K2, Rf))))
        worst["R"] = max(worst["R"], Ra[0])
        worst["PM1"] = max(worst["PM1"], pm1[0])
        worst["PM2"] = max(worst["PM2"], pm2[0])
        worst["signed1"] = max(worst["signed1"], abs(dRf[0]))
        worst["signed2"] = max(worst["signed2"], abs(d2Rf[0]))
        worst["Lam"] = max(worst["Lam"], sum(R[0]))
    return worst


def occupation(fam, e0) -> list:
    R = fam.R(e0)
    lam = sum(R[0])
    return [x / lam for x in R[0]]


# --------------------------------------------------------------------------------------------- R1-R3


def r123(seed: int) -> list:
    n = 4 + seed % 4
    e0 = F(1, 8)
    rho = (F(1, 64), F(1, 32), F(1, 16))[seed % 3]
    pert = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 2))[(seed // 3) % 3]
    sdeg = (2, 5)[seed % 2]
    fam = D.make_family(n, seed, e0 + rho, deg=4)
    sp = D.make_sources(n, 1, seed, deg=sdeg)[0]
    lo, hi = e0 - rho, e0 + rho
    k = [D.k_cell(fam, i, lo, hi) for i in range(3)]
    C = D.C_cell(fam, e0, rho)
    A0, A1, A2 = D.lemma_g(k, C)
    K1abs, K2abs = abs_sup_matrix(fam, 1, lo, hi), abs_sup_matrix(fam, 2, lo, hi)
    occ = occupation(fam, e0)
    med = sorted(occ)[len(occ) // 2]
    famr = X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
    rng = random.Random(5000 + seed)
    Fd = famr.F_derivs(e0, 2)
    cand = {"F": D.perturbed(Fd[0], pert, rng), "D": D.perturbed(Fd[1], pert, rng), "H": D.perturbed(Fd[2], pert, rng)}
    fx = D.TCFixture(fam, sp, e0, rho, cand)
    classes = {
        "generic_phiH": D.vabs(fx.phi_leibniz(2)),
        "favourable": [F(1) if o < med else F(1, 100) for o in occ],
        "adversarial_atom": [F(1) if x == max(range(n), key=lambda y: occ[y]) else F(1, 100) for x in range(n)],
        "adversarial_const": [F(1)] * n,
    }
    rows = []
    for cname, a in classes.items():
        ch = cert_chain(fam, e0, rho, a, K1abs, K2abs)
        tr = truth_grid(fam, e0, rho, a, random.Random(77 + seed))
        na = D.vnorm(a)
        # negative control (b): planted v := 9/10 v_cert must fail the certificate check
        vbad = [x * F(9, 10) for x in ch["N0"]["v"]]
        nc_b = check_cert_taylor(fam, lo, hi, vbad, a) < 0
        # negative control (a): planted psi below |phi| at the argmax state must fail the majorant check
        psi_bad = list(a)
        xm = max(range(n), key=lambda y: a[y])
        psi_bad[xm] = a[xm] / 2
        nc_a = not all(p >= q for p, q in zip(psi_bad, a))
        rows.append({
            "seed": seed, "class": cname, "n": n, "rho": str(rho),
            "certs_verified_twice": all(ch[kk]["verified_twice"] for kk in ("N0", "N1", "N2")),
            "sound": {"N0_ge_truth": ch["N0"]["va"] >= tr["R"], "N1_ge_PM1_truth": ch["N1"]["va"] >= tr["PM1"],
                      "N2_ge_PM2_truth": ch["N2"]["va"] >= tr["PM2"],
                      "N1_ge_signed": ch["N1"]["va"] >= tr["signed1"], "N2_ge_signed": ch["N2"]["va"] >= tr["signed2"]},
            "shape_factor_mu_a_over_sup": float(sum(o * x for o, x in zip(occ, a)) / na),
            "N0_over_A0norm": float(ch["N0"]["va"] / (A0 * na)),
            "N0_over_Lambda_norm": float(ch["N0"]["va"] / (tr["Lam"] * na)),
            "truth_R_over_Lambda_norm": float(tr["R"] / (tr["Lam"] * na)),
            "N1_over_A1norm": float(ch["N1"]["va"] / (A1 * na)),
            "N2_over_A2norm": float(ch["N2"]["va"] / (A2 * na)),
            "signed1_over_N1": float(tr["signed1"] / ch["N1"]["va"]),
            "cert_overhead_N0_over_truth": float(ch["N0"]["va"] / tr["R"]),
            "nc_a_detected": nc_a, "nc_b_detected": nc_b,
        })
    return rows


# --------------------------------------------------------------------------------------------- R4: TC assembly


def group_max(a: list, g: int) -> list:
    out = []
    for s in range(0, len(a), g):
        mx = max(a[s:s + g])
        out.extend([mx] * len(a[s:s + g]))
    return out


def r4(seed: int) -> list:
    n = 4 + seed % 4
    e0 = F(1, 8)
    rho = (F(1, 64), F(1, 32), F(1, 16))[seed % 3]
    pert = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 2))[(seed // 3) % 3]
    sdeg = (2, 5)[seed % 2]
    fam = D.make_family(n, seed, e0 + rho, deg=4)
    sp = D.make_sources(n, 1, seed, deg=sdeg)[0]
    lo, hi = e0 - rho, e0 + rho
    k = [D.k_cell(fam, i, lo, hi) for i in range(5)]
    C = D.C_cell(fam, e0, rho)
    A = D.lemma_g(k, C)
    K1abs, K2abs = abs_sup_matrix(fam, 1, lo, hi), abs_sup_matrix(fam, 2, lo, hi)
    famr = X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
    rng = random.Random(5000 + seed)
    Fd = famr.F_derivs(e0, 2)
    cand = {"F": D.perturbed(Fd[0], pert, rng), "D": D.perturbed(Fd[1], pert, rng), "H": D.perturbed(Fd[2], pert, rng)}
    fx = D.TCFixture(fam, sp, e0, rho, cand)
    a = [D.vabs(fx.phi_leibniz(j)) for j in range(4)]
    a4 = [D.sup_abs_on(D.p_deriv(c, 4), -rho, rho)[0] for c in fx.phi_poly()]
    a.append(a4)
    sH, sD, sF = D.vnorm(fx.Hh), D.vnorm(fx.Dh), D.vnorm(fx.Fh)
    sig3 = D.vnorm(fx.S[3])
    sig4 = D.sigma_cell(sp, 4, lo, hi)
    fG_sur = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + sig3
    E0 = sig4 + 6 * k[2] * sH + 4 * k[3] * (sD + rho * sH) + k[4] * (sF + rho * sD + rho ** 2 * sH / 2)
    fnorm = {"F": D.vnorm(a[0]), "D": D.vnorm(a[1]), "H": D.vnorm(a[2])}
    base = D.tc_rad_poly(A, dict(fnorm, G=fG_sur, Env4=E0))
    ones = [F(1)] * n

    def Nset(vecs):
        return [cert_chain(fam, e0, rho, v, K1abs, K2abs) for v in vecs]

    def rso_poly(comp_vecs):
        """rad(s) = sum over the Taylor profile of the pointwise components (theorem RSO-P)."""
        ch = Nset(comp_vecs)
        N0 = [c["N0"]["va"] for c in ch]
        N1 = [c["N1"]["va"] for c in ch]
        N2 = [c["N2"]["va"] for c in ch]
        p_N0 = [N0[2], N0[3], N0[4] / 2]
        p_N1 = [N1[1], N1[2], N1[3] / 2, N1[4] / 6]
        p_N2 = [N2[0], N2[1], N2[2] / 2, N2[3] / 6, N2[4] / 24]
        return D.p_add(D.p_add(p_N0, D.p_scale(p_N1, F(2))), p_N2), all(
            c[kk]["verified_twice"] for c in ch for kk in ("N0", "N1", "N2"))
    variants = {}
    # RSO-C4 (C4 section 7.1 as narrowed by ROUTE_AUDIT_R1): only the A0 f_H part is replaced
    c_H = cert_chain(fam, e0, rho, a[2], K1abs, K2abs)
    variants["RSO_C4"] = D.p_add(base, [c_H["N0"]["va"] - A[0] * fnorm["H"]])
    # RSO-P with norm-only order-3/4 premises (RSO without the composite route)
    variants["RSO_P_normonly34"], ok1 = rso_poly([a[0], a[1], a[2], [fG_sur] * n, [E0] * n])
    for g in (1, 2, n):
        variants[f"RSO_P_box{g if g < n else 'n'}"], okg = rso_poly([group_max(v, g) for v in a])
    rows = []
    checks = {}
    for kname, poly in [("TCT_base", base)] + list(variants.items()):
        viol, worst = 0, F(0)
        for j in range(33):
            t = lo + 2 * rho * F(j, 32)
            dev = abs(fx.Fpp_at_atom(t) - fx.Hh[0])
            r = D.p_eval(poly, abs(t - e0))
            viol += dev > r
            worst = max(worst, dev / r)
        checks[kname] = {"violations": viol, "worst_dev_over_rad": float(worst),
                         "rad_rho_over_base": float(D.p_eval(poly, rho) / D.p_eval(base, rho))}
    rows.append({"seed": seed, "n": n, "rho": str(rho), "pert": str(pert), "source_degree": sdeg,
                 "checks": checks, "occupation_at_e0": [float(o) for o in occupation(fam, e0)]})
    return rows


# --------------------------------------------------------------------------------------------- R5: LR (score) form


class LRFamily:
    """Discrete likelihood-ratio walk: x' = max(0, x+z), alarm iff x+z >= L, z in {-1,0,1}, killing kappa (e-free)."""

    def __init__(self, L: int, c: F = F(1, 2), kappa: F = F(1, 4)):
        self.L, self.c, self.kappa = L, c, kappa
        self.Z = (-1, 0, 1)
        self.p0 = {-1: F(1, 4), 0: F(1, 2), 1: F(1, 4)}
        self.m2 = sum(self.p0[z] * z * z for z in self.Z)

    def pz(self, z: int, e: F, der: int = 0) -> F:
        a1, a2 = F(z), self.c * (z * z - self.m2)
        poly = [F(1), a1, a2]
        return self.p0[z] * D.p_eval(D.p_deriv(poly, der), e)

    def score(self, z: int, e: F) -> F:
        return self.pz(z, e, 1) / self.pz(z, e)

    def nxt(self, x: int, z: int):
        y = x + z
        return None if y >= self.L else max(0, y)

    def kernel(self, e: F, weight=None) -> list:
        L = self.L
        K = [[F(0)] * L for _ in range(L)]
        for x in range(L):
            for z in self.Z:
                y = self.nxt(x, z)
                if y is None:
                    continue
                w = self.pz(z, e) * (1 - self.kappa)
                if weight is not None:
                    w *= weight(z)
                K[x][y] += w
        return K

    def kernel_deriv(self, e: F, der: int) -> list:
        L = self.L
        K = [[F(0)] * L for _ in range(L)]
        for x in range(L):
            for z in self.Z:
                y = self.nxt(x, z)
                if y is not None:
                    K[x][y] += self.pz(z, e, der) * (1 - self.kappa)
        return K


def lr_certificate(fam: LRFamily, e: F, psi: list) -> dict:
    Q.guard_drift(e)
    L = fam.L
    Kc = fam.kernel(e)
    KS = fam.kernel(e, lambda z: fam.score(z, e))
    KS2 = fam.kernel(e, lambda z: fam.score(z, e) ** 2)
    R = X.mat_inv(D.I_minus(Kc))
    best = None
    for kc in range(-4, 5):
        cc = F(2) ** kc
        for kd in range(-8, 3):
            dd = F(2) ** kd
            beta = D.mv(R, [p / (2 * cc) + dd for p in psi])
            ksb = D.mv(KS, beta)
            src = [p * cc / 2 + q + r * r / dd for p, q, r in zip(psi, D.mv(KS2, beta), ksb)]
            alpha = D.mv(R, src)
            if best is None or alpha[0] < best[0]:
                best = (alpha[0], cc, dd, min(alpha), min(beta))
    return {"alpha_a": best[0], "c": best[1], "delta": best[2], "alpha_min": best[3], "beta_min": best[4]}


def lr_paths(fam: LRFamily, e: F, psi: list, f: list, N: int) -> dict:
    """Exact truncated sums over n <= N: E_a[sum psi(X_n)|M_n|] (lower bound) and E_a[sum f(X_n) M_n]."""
    Q.guard_drift(e)
    S = {z: fam.score(z, e) for z in fam.Z}
    P = {z: fam.pz(z, e) * (1 - fam.kappa) for z in fam.Z}
    dist = {(0, F(0)): F(1)}
    lb, sg, mass = F(0), F(0), F(1)
    for n in range(N + 1):
        for (x, mu), pr in dist.items():
            lb += pr * psi[x] * abs(mu)
            sg += pr * f[x] * mu
        if n == N:
            mass = sum(dist.values())
            break
        nd: dict = {}
        for (x, mu), pr in dist.items():
            for z in fam.Z:
                y = fam.nxt(x, z)
                if y is None:
                    continue
                key = (y, mu + S[z])
                nd[key] = nd.get(key, F(0)) + pr * P[z]
        dist = nd
    return {"lower": lb, "signed_trunc": sg, "surviving_mass_at_N": mass, "states": len(dist)}


def r5() -> list:
    rows = []
    for L in (4, 5, 6):
        fam = LRFamily(L)
        for e in (F(1, 8), F(1, 4)):
            Q.guard_drift(e)
            Kc = fam.kernel(e)
            K1 = fam.kernel_deriv(e, 1)
            KS = fam.kernel(e, lambda z: fam.score(z, e))
            ident_KS_K1 = KS == K1
            # structural NC (d): a planted wrong score S(z) := z (the base-measure score, not d/de log p_e) must break
            # the kernel identity K^S = K_1 at e > 0
            nc_score = fam.kernel(e, lambda z: F(z)) != K1
            R = X.mat_inv(D.I_minus(Kc))
            for pname, psi in (("ramp", [F(1, 100) + F(x, L) for x in range(L)]),
                               ("top_state", [F(1) if x == L - 1 else F(0) for x in range(L)])):
                rng = random.Random(31 * L + int(e * 8))
                f = [p * rng.choice((-1, 1)) for p in psi]
                exact_signed = D.mv(R, D.mv(K1, D.mv(R, f)))[0]
                paths = lr_paths(fam, e, psi, f, 60)
                cert = lr_certificate(fam, e, psi)
                K1a = [[abs(x) for x in r] for r in K1]
                pm = D.mv(R, D.mv(K1a, D.mv(R, psi)))[0]
                Kabs_path = fam.kernel(e, lambda z: abs(fam.score(z, e)))
                pm_path = D.mv(R, D.mv(Kabs_path, D.mv(R, psi)))[0]
                k1 = X.op_norm(K1)
                Cn = X.op_norm(R)
                normb = k1 * Cn * Cn * D.vnorm(psi)
                nc_c = not (paths["lower"] * F(9, 10) >= paths["lower"])
                rows.append({
                    "L": L, "e": str(e), "psi": pname, "kernel_identity_KS_eq_K1": ident_KS_K1,
                    "signed_exact": float(exact_signed), "signed_trunc_N60": float(paths["signed_trunc"]),
                    "signed_trunc_gap": float(abs(exact_signed - paths["signed_trunc"])),
                    "surviving_mass_N60": float(paths["surviving_mass_at_N"]),
                    "LR_lower_N60": float(paths["lower"]), "LR_cert": float(cert["alpha_a"]),
                    "cert_ge_lower": cert["alpha_a"] >= paths["lower"],
                    "lower_ge_signed": paths["lower"] >= abs(paths["signed_trunc"]),
                    "cert_nonneg": cert["alpha_min"] >= 0 and cert["beta_min"] >= 0,
                    "PM_entrywise": float(pm), "PM_pathwise": float(pm_path), "norm_bound_k1C2": float(normb),
                    "LR_cert_over_PM_entrywise": float(cert["alpha_a"] / pm),
                    "LR_lower_over_PM_pathwise": float(paths["lower"] / pm_path),
                    "LR_cert_over_norm": float(cert["alpha_a"] / normb),
                    "cert_c": str(cert["c"]), "cert_delta": str(cert["delta"]),
                    "nc_c_detected": nc_c, "nc_d_wrong_score_detected": nc_score})
    return rows


def main() -> None:
    t0 = time.time()
    out = {"schema": "OV_D309_RSO_FSM/1", "declared_rule": DECLARED_RULE}
    out["R123"] = [row for s in range(1, 13) for row in r123(s)]
    out["R4"] = [row for s in range(1, 13) for row in r4(s)]
    out["R5"] = r5()
    r123_rows, r4_rows, r5_rows = out["R123"], out["R4"], out["R5"]

    def rng_of(rows, key, filt=lambda r: True):
        v = [r[key] for r in rows if filt(r)]
        return [min(v), max(v)] if v else None
    out["summary"] = {
        "R123_cases": len(r123_rows),
        "R1_certs_verified_twice_all": all(r["certs_verified_twice"] for r in r123_rows),
        "R2_sound_all": all(all(r["sound"].values()) for r in r123_rows),
        "NC_a_detected": sum(r["nc_a_detected"] for r in r123_rows),
        "NC_b_detected": sum(r["nc_b_detected"] for r in r123_rows),
        "R3_shape_factor": {c: rng_of(r123_rows, "shape_factor_mu_a_over_sup", lambda r, c=c: r["class"] == c)
                            for c in ("generic_phiH", "favourable", "adversarial_atom", "adversarial_const")},
        "R3_N0_over_Lambda_norm": {c: rng_of(r123_rows, "N0_over_Lambda_norm", lambda r, c=c: r["class"] == c)
                                   for c in ("generic_phiH", "favourable", "adversarial_atom", "adversarial_const")},
        "R3_N0_over_A0norm": {c: rng_of(r123_rows, "N0_over_A0norm", lambda r, c=c: r["class"] == c)
                              for c in ("generic_phiH", "favourable", "adversarial_atom", "adversarial_const")},
        "R3_N1_over_A1norm": rng_of(r123_rows, "N1_over_A1norm"),
        "R3_N2_over_A2norm": rng_of(r123_rows, "N2_over_A2norm"),
        "R3_cert_overhead_N0_over_truth": rng_of(r123_rows, "cert_overhead_N0_over_truth"),
        "R4_cases": len(r4_rows),
        "R4_violations_total": sum(c["violations"] for r in r4_rows for c in r["checks"].values()),
        "R4_points_checked": sum(33 * len(r["checks"]) for r in r4_rows),
        "R4_rso_shape_gain_box1_over_boxn": [
            min(r["checks"]["RSO_P_box1"]["rad_rho_over_base"] / r["checks"]["RSO_P_boxn"]["rad_rho_over_base"]
                for r in r4_rows),
            max(r["checks"]["RSO_P_box1"]["rad_rho_over_base"] / r["checks"]["RSO_P_boxn"]["rad_rho_over_base"]
                for r in r4_rows)],
        "R3_signed1_over_N1": rng_of(r123_rows, "signed1_over_N1"),
        "R4_rad_ratio": {kname: [min(r["checks"][kname]["rad_rho_over_base"] for r in r4_rows),
                                 max(r["checks"][kname]["rad_rho_over_base"] for r in r4_rows)]
                         for kname in r4_rows[0]["checks"]},
        "R5_cases": len(r5_rows),
        "R5_kernel_identity_all": all(r["kernel_identity_KS_eq_K1"] for r in r5_rows),
        "R5_cert_ge_lower_all": all(r["cert_ge_lower"] for r in r5_rows),
        "R5_lower_ge_signed_all": all(r["lower_ge_signed"] for r in r5_rows),
        "R5_signed_trunc_gap_max": max(r["signed_trunc_gap"] for r in r5_rows),
        "R5_LR_cert_over_PM_entrywise": rng_of(r5_rows, "LR_cert_over_PM_entrywise"),
        "R5_LR_lower_over_PM_pathwise": rng_of(r5_rows, "LR_lower_over_PM_pathwise"),
        "R5_LR_cert_over_norm": rng_of(r5_rows, "LR_cert_over_norm"),
        "NC_c_detected": sum(r["nc_c_detected"] for r in r5_rows),
        "NC_d_wrong_score_detected": sum(r["nc_d_wrong_score_detected"] for r in r5_rows),
        "wall_s": round(time.time() - t0, 1),
    }
    p = D.NS / "validation" / "D309_RSO_FSM.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True, default=lambda o: float(o) if isinstance(o, F) else str(o)))
    Q.log_execution("streams/D_309/code/d309_rso.py",
                    "RSO-0 / RSO-PM / RSO-LR certificates, soundness vs exact truth, TC assembly, NCs on synthetic FSM",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
