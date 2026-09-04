"""P5Y K1 TASK 1R -- budget-derived certification harness.

Successor to the failed Production Task 1. Repairs ONE thing: the certification
harness. No scientific rule, scope, threshold, ledger line, precision, degree
ceiling or verdict semantic changes.

THE PREDECESSOR DEFECT
----------------------
Task 1 composed to full degree first -- 16 x 9 = 144 per side, so total composed
degree n = r+s ran to 288 -- in the mixed variable u = alpha + zeta, and only
then truncated the patch-local variables at DEG_X = 6.  Re-expanding u^n spreads
alpha-mass BINOMIALLY with p = H/rho = 0.2041, so a degree-n term has expected
patch-local degree 0.204 n, exceeding 6 once n > 29.  Most of the retained series
was therefore surrendered to the discard bound: 98.23% of the certified delta_0.

THE REPAIR
----------
Truncate the patch-local variable at EVERY product, not once at the end.  The
objects are bivariate Taylor models in (alpha, zeta) and (beta, zeta) carrying a
rigorous remainder; alpha-degree never exceeds D, so the discarded coefficients
decay geometrically in H/R with R the alpha-analyticity radius (softplus is
analytic to distance pi) instead of following a binomial tail in H/rho with
rho = 0.24.  That is a factor pi/rho ~ 13 per order, and it is structural: no
configuration can silently dump mass into the discard bound, because there is no
late re-expansion in which to dump it.

Two further repairs required by the successor brief:
  * the crude |N_k| <= h^k N_0 becomes the Gaussian-structure bound
    |N_k| <= 2 phi_max h^(k+1) / (k+1), sharper by a factor (k+1);
  * a joint (D, Z) consistency guard rejects late-truncation configurations
    quantitatively, before any result-bearing work.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
K1 = ROOT / "level4/closure_proofs/p5y_k1_binding_campaign"
R3 = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"
G2B = ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover"
for _p in (str(R3), str(G2B), str(K1 / "task1"), str(ROOT / "rebaseguard-proof" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb                                                # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec       # noqa: E402
import sr_local as L                                                 # noqa: E402

# ===================== INHERITED, UNCHANGED (read from the binding checkpoint)
DETECTOR, OBJECT = "SR", "F_0"
PATCH, GRID = (17, 11), 64
E_NUM, E_DEN = 1, 4
SOFTPLUS_DEGREE = 8
CAND_DEGREE = 16
SCALE_BITS = 50
PROD_BITS = 256
P1_RULE_WORKPREC = 512
EPS_P1 = 1e-3
P1_CHECK_THRESHOLD = 1e-9
P1_HEADROOM_GUARD = 1e-6
COMPLEXITY_CEILING = 60_000
B_CANDIDATE = 0.040
LOCAL_GATE_BUDGET = 0.100
K1_ANCHOR = "310c3aa34a5d980ef48331d2d2bea36b7c37360d"
K1_HASH = "ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d"

# ============================ BUDGET PARTITION OF B_candidate (frozen at T1R)
# Twentieths of the EXISTING B_candidate. No new budget is created; the sum is
# exactly B_candidate. Shape mirrors the parent ledger: the quantity under test
# takes the plurality, the two tunable harness parameters are treated
# symmetrically, precision-limited lines take the parent's smallest share, and
# the reserve is non-redistributable.
PARTITION_20THS = {
    "B_eq":      9,   # 45%  the equation defect itself -- the object under test
    "B_trunc":   3,   # 15%  patch-local (alpha,beta) truncation
    "B_tail":    3,   # 15%  zeta truncation + Gaussian moment tail
    "B_end":     2,   # 10%  endpoint slivers (structural, not tunable)
    "B_int":     1,   #  5%  Arb interval radius   (parent ledger's smallest line)
    "B_round":   1,   #  5%  exact-dyadic rounding (parent ledger's smallest line)
    "B_reserve": 1,   #  5%  NON-REDISTRIBUTABLE   (mirrors the parent reserve)
}
RESERVE_KEY = "B_reserve"

# ======================= parameter-selection search grids (frozen, ordered)
Z_GRID = (12, 16, 20, 24, 28, 32, 40, 48)
D_GRID = tuple(range(SOFTPLUS_DEGREE + 1, 25))     # D >= SOFTPLUS_DEGREE + 1
BINOM_SIGMA = 5.0          # tail quantile used by the joint-consistency relation


def budget() -> dict:
    tot = sum(PARTITION_20THS.values())
    assert tot == 20, tot
    ab = {k: B_CANDIDATE * v / 20 for k, v in PARTITION_20THS.items()}
    return {"B_candidate_total": B_CANDIDATE,
            "partition_twentieths": dict(PARTITION_20THS),
            "absolute": ab,
            "sum_absolute": sum(ab.values()),
            "sums_to_B_candidate": abs(sum(ab.values()) - B_CANDIDATE) < 1e-15,
            "reserve_key": RESERVE_KEY,
            "reserve_redistributable": False,
            "new_budget_created": False}


# ============================================ Gaussian moment tail certificate
def gaussian_moment_bound(mu: arb, h: arb, kmax: int) -> list[arb]:
    """Certified |N_k| <= 2 phi_max h^(k+1) / (k+1),  N_k = int_-h^h z^k phi(mu+z)dz.

    |z^k| <= |z|^k and phi >= 0 give |N_k| <= phi_max * int_-h^h |z|^k dz
    = phi_max * 2 h^(k+1)/(k+1).  phi is unimodal, so on [mu-h, mu+h]
    phi_max = phi(0) when |mu| <= h and phi(|mu|-h) otherwise.  Monotone
    decreasing in k for h < 1, hence mechanically checkable.

    Sharper than the predecessor's |N_k| <= h^k N_0 by a factor (k+1), because
    N_0 <= 2 h phi_max already carries one power of h.
    """
    two_pi = arb(2) * arb.pi()
    am = mu.abs_lower()
    arg = arb(0) if am <= h.abs_upper() else (mu.abs_lower() - h.abs_upper())
    phi_max = ((-(arg * arg) / arb(2)).exp() / two_pi.sqrt()).abs_upper()
    return [arb(2) * phi_max * (h ** (k + 1)) / arb(k + 1) for k in range(kmax + 1)]


# =========================================== joint (D, Z) consistency relation
def required_local_degree(mode: str, D: int, Z: int, H: float, h: float) -> dict:
    """required DEG_X >= f(truncation architecture, patch geometry, composition).

    'truncate_each_product' (the repair): the patch-local variable is truncated
    at every multiplication, so alpha-degree is bounded at the SOURCE by the
    softplus expansion and D >= SOFTPLUS_DEGREE + 1 makes the source expansion
    exact in alpha.  Nothing can spread.

    'compose_then_truncate' (the predecessor): composition first, to total
    degree n_max = 2 * CAND_DEGREE * (SOFTPLUS_DEGREE + 1), then one truncation.
    alpha-mass is then binomial with p = H/(H+h), so representing it needs
        D >= n_max p + BINOM_SIGMA sqrt(n_max p (1-p)).
    """
    rho = H + h
    p = H / rho
    n_max = 2 * CAND_DEGREE * (SOFTPLUS_DEGREE + 1)
    if mode == "truncate_each_product":
        req = SOFTPLUS_DEGREE + 1
    elif mode == "compose_then_truncate":
        req = int(math.ceil(n_max * p + BINOM_SIGMA * math.sqrt(n_max * p * (1 - p))))
    else:
        raise ValueError(f"unknown truncation architecture: {mode}")
    local_score = (D + 1) ** 2 * (Z + 1)
    cand_score = (CAND_DEGREE + 1) ** 2 * (Z + 1)
    d_max = int(math.floor(math.sqrt(COMPLEXITY_CEILING / (Z + 1)))) - 1
    return {"mode": mode, "p_alpha_share": p, "n_max_composed_degree": n_max,
            "required_D": req, "selected_D": D, "D_max_from_complexity": d_max,
            "local_score": local_score, "candidate_score": cand_score,
            "complexity_ceiling": COMPLEXITY_CEILING,
            "D_satisfies_requirement": D >= req,
            "D_within_complexity": D <= d_max,
            "scores_within_ceiling": (local_score <= COMPLEXITY_CEILING
                                      and cand_score <= COMPLEXITY_CEILING),
            "PASS": bool(D >= req and D <= d_max
                         and local_score <= COMPLEXITY_CEILING
                         and cand_score <= COMPLEXITY_CEILING)}


# =============================================== bivariate Taylor model (x, z)
class TM2:
    """f(x,z) in  sum_{a<=D,k<=Z} c[a][k] x^a z^k  + [-ex-ez, ex+ez]
    for all |x| <= H, |z| <= h.

    `x` is the PATCH-LOCAL variable (alpha or beta), truncated at D at EVERY
    product -- this is the repair.  `ex` and `ez` are tracked separately so each
    can be charged to its own frozen budget line.
    """
    __slots__ = ("c", "ex", "ez", "H", "h", "D", "Z", "_hp", "_Hp")

    def __init__(self, c, ex, ez, H, h, D, Z, Hp, hp):
        self.c, self.ex, self.ez = c, ex, ez
        self.H, self.h, self.D, self.Z = H, h, D, Z
        self._Hp, self._hp = Hp, hp

    @classmethod
    def zero(cls, ctxt):
        H, h, D, Z, Hp, hp = ctxt
        return cls([[arb(0)] * (Z + 1) for _ in range(D + 1)], arb(0), arb(0),
                   H, h, D, Z, Hp, hp)

    def ctxt(self):
        return (self.H, self.h, self.D, self.Z, self._Hp, self._hp)

    def copy_with(self, c, ex, ez):
        return TM2(c, ex, ez, self.H, self.h, self.D, self.Z, self._Hp, self._hp)

    def mag(self) -> arb:
        acc = arb(0)
        for a, row in enumerate(self.c):
            Ha = self._Hp[a]
            for k, ck in enumerate(row):
                if not ck.is_zero():
                    acc += ck.abs_upper() * Ha * self._hp[k]
        return acc + self.ex + self.ez

    def scaled(self, s: arb, shift: arb = None):
        c = [[ck * s for ck in row] for row in self.c]
        if shift is not None:
            c[0][0] = c[0][0] + shift
        return self.copy_with(c, self.ex * s.abs_upper(), self.ez * s.abs_upper())

    def __add__(self, o):
        c = [[self.c[a][k] + o.c[a][k] for k in range(self.Z + 1)]
             for a in range(self.D + 1)]
        return self.copy_with(c, self.ex + o.ex, self.ez + o.ez)

    def __sub__(self, o):
        return self + o.scaled(arb(-1))

    def __mul__(self, o):
        D, Z = self.D, self.Z
        conv = [[arb(0)] * (2 * Z + 1) for _ in range(2 * D + 1)]
        for a, row in enumerate(self.c):
            for k, ck in enumerate(row):
                if ck.is_zero():
                    continue
                for b, row2 in enumerate(o.c):
                    ab = a + b
                    tgt = conv[ab]
                    for l, cl in enumerate(row2):
                        if not cl.is_zero():
                            tgt[k + l] += ck * cl
        keep = [[conv[a][k] for k in range(Z + 1)] for a in range(D + 1)]
        ex_tail = arb(0)
        for a in range(D + 1, 2 * D + 1):
            Ha = self.H ** a
            for k in range(2 * Z + 1):
                if not conv[a][k].is_zero():
                    ex_tail += conv[a][k].abs_upper() * Ha * (self.h ** k)
        ez_tail = arb(0)
        for a in range(D + 1):
            Ha = self._Hp[a]
            for k in range(Z + 1, 2 * Z + 1):
                if not conv[a][k].is_zero():
                    ez_tail += conv[a][k].abs_upper() * Ha * (self.h ** k)
        ma, mo = self.mag(), o.mag()
        ex = ex_tail + ma * o.ex + mo * self.ex + self.ex * o.ex
        ez = ez_tail + ma * o.ez + mo * self.ez + self.ez * o.ez \
            + self.ex * o.ez + self.ez * o.ex
        return self.copy_with(keep, ex, ez)


def softplus_tm2(centre: arb, ctxt, sign_z: int) -> TM2:
    """sp(centre + x + sign_z*z) as an exact-in-x bivariate Taylor model.

    softplus_local_enclosure gives the Lagrange form with an interval coefficient
    on the degree-(d+1) term, valid over the whole box, so expanding
    (x + sign_z z)^r binomially is exact for D, Z >= SOFTPLUS_DEGREE + 1:
    NOTHING is discarded at the source.  That is what makes the patch-local
    truncation harmless downstream.
    """
    H, h, D, Z, Hp, hp = ctxt
    rho = H + h
    a, _E, a_next = L.softplus_local_enclosure(centre, rho, SOFTPLUS_DEGREE)
    coeffs = list(a) + [a_next]
    out = TM2.zero(ctxt)
    ex = ez = arb(0)
    for r, ar in enumerate(coeffs):
        if ar.is_zero():
            continue
        for j in range(r + 1):
            xa, zk = j, r - j
            term = ar * arb(math.comb(r, j)) * (arb(sign_z) ** zk)
            if xa <= D and zk <= Z:
                out.c[xa][zk] += term
            elif xa > D:
                ex += term.abs_upper() * (H ** xa) * (h ** zk)
            else:
                ez += term.abs_upper() * (H ** xa) * (h ** zk)
    out.ex, out.ez = ex, ez
    return out


def cheb_tm2(x: TM2, n: int) -> list[TM2]:
    ctxt = x.ctxt()
    one = TM2.zero(ctxt)
    one.c[0][0] = arb(1)
    out = [one, x]
    two_x = x.scaled(arb(2))
    for _ in range(2, n + 1):
        out.append(two_x * out[-1] - out[-2])
    return out[: n + 1]


# ==================================================================== geometry
def geometry():
    A, b, c = L.sr_constants()
    e = rational(E_NUM, E_DEN)
    geo = L.patch_geometry(*PATCH, grid=GRID)
    p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
    m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
    H = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    U_c, L_c = c - p_c, m_c - c
    return dict(A=A, b=b, c=c, e=e, geo=geo, p_c=p_c, m_c=m_c, H=H,
                U_c=U_c, L_c=L_c, span=U_c - L_c)


def p1_rule(H: arb, span: arb) -> dict:
    """Frozen asymmetric P1 rule, construction target inside explicit workprec."""
    with workprec(P1_RULE_WORKPREC):
        eps = arb(1) / arb(1000)
        rule_target = (arb(1) - eps) * arb("1e-9")
        M = L.softplus_derivative_bound_tight(SOFTPLUS_DEGREE + 1)
        fact = arb(math.factorial(SOFTPLUS_DEGREE + 1))
        H_max = ((rule_target * fact / M).log() / arb(SOFTPLUS_DEGREE + 1)).exp()
        rt = rule_target.str(30)
        H_max_f = float(H_max.lower())
    h_z = arb(H_max_f) - H
    n_z = int(math.ceil(float((span / (arb(2) * h_z)).upper())))
    h = span / (arb(2) * arb(n_z))
    with workprec(PROD_BITS):
        M = L.softplus_derivative_bound_tight(SOFTPLUS_DEGREE + 1)
        E_d = M * ((h + H) ** (SOFTPLUS_DEGREE + 1)) / arb(math.factorial(SOFTPLUS_DEGREE + 1))
        E_d_up = float(E_d.abs_upper())
    hr = (P1_CHECK_THRESHOLD - E_d_up) / P1_CHECK_THRESHOLD
    return {"eps_P1": EPS_P1, "P1_RULE_TARGET": rt,
            "P1_CHECK_THRESHOLD": P1_CHECK_THRESHOLD,
            "rule_and_check_distinct": (1 - EPS_P1) * 1e-9 < P1_CHECK_THRESHOLD,
            "P1_RULE_WORKPREC_BITS": P1_RULE_WORKPREC,
            "rule_target_evaluated_inside_workprec": True,
            "H_max": H_max_f, "n_panels": n_z, "h_panel": float(h),
            "patch_half": float(H), "H_used": float(h + H), "E_d": E_d_up,
            "E_d_le_construction_target": E_d_up <= (1 - EPS_P1) * 1e-9,
            "HEADROOM_REL": hr, "headroom_guard": P1_HEADROOM_GUARD,
            "PASS": bool(E_d_up <= P1_CHECK_THRESHOLD and hr >= P1_HEADROOM_GUARD)}


def panel_moments(z_lo, z_hi, z_c, e, kmax, h):
    """Exact moments, CLAMPED by the certified Gaussian-structure bound (rigorous
    under either, and sharper than either alone)."""
    Nm = L.centred_gaussian_moments(z_lo, z_hi, z_c, e, kmax)
    Mb = gaussian_moment_bound(z_c + e, h, kmax)
    out = []
    for k in range(kmax + 1):
        v = Nm[k] if k < len(Nm) else arb(0, Mb[k].upper())
        if v.abs_upper() > Mb[k]:
            v = arb(0, Mb[k].upper())
        out.append(v)
    return out


# ============================================ the harness (shared by selection
#                                               and by the genuine certificate)
def run_panels(cand, D, Z, g, p1, *, majorant=False, only_panel=None):
    """Accumulate the (alpha,beta) Taylor model of K_e Fhat over all panels."""
    b, c, e = g["b"], g["c"], g["e"]
    p_c, m_c, H, L_c = g["p_c"], g["m_c"], g["H"], g["L_c"]
    n_z = p1["n_panels"]
    h = (g["span"]) / (arb(2) * arb(n_z))
    Hp = [H ** a for a in range(2 * D + 2)]
    hp = [h ** k for k in range(2 * Z + 2)]
    ctxt = (H, h, D, Z, Hp, hp)
    half = arb(1) / arb(2)
    coef = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_tot = ez_tot = arb(0)
    for kp in (range(n_z) if only_panel is None else (only_panel,)):
        z_lo = L_c + arb(2) * h * arb(kp)
        z_hi = z_lo + arb(2) * h
        z_c = (z_lo + z_hi) / arb(2)
        V = softplus_tm2(p_c + z_c - half, ctxt, +1)
        W = softplus_tm2(m_c - z_c - half, ctxt, -1)
        TV = cheb_tm2(V.scaled(arb(2) / b, shift=arb(-1)), CAND_DEGREE)
        TW = cheb_tm2(W.scaled(arb(2) / b, shift=arb(-1)), CAND_DEGREE)
        N = panel_moments(z_lo, z_hi, z_c, e, 2 * Z + 1, h)
        N0 = N[0].abs_upper()
        for i in range(CAND_DEGREE + 1):
            inner = TM2.zero(ctxt)
            for j in range(CAND_DEGREE + 1):
                cij = arb(1) if majorant else cand[i][j]
                if cij.is_zero():
                    continue
                inner = inner + TW[j].scaled(cij)
            P, Q = TV[i], inner
            mp, mq = P.mag(), Q.mag()
            ex_tot += (mq * P.ex + mp * Q.ex) * N0
            ez_tot += (mq * P.ez + mp * Q.ez) * N0
            for a in range(D + 1):
                prow = P.c[a]
                if all(x.is_zero() for x in prow):
                    continue
                for bq in range(D + 1):
                    qrow = Q.c[bq]
                    acc = arb(0)
                    for k1, pk in enumerate(prow):
                        if pk.is_zero():
                            continue
                        for k2, qk in enumerate(qrow):
                            if not qk.is_zero():
                                acc += pk * qk * N[k1 + k2]
                    coef[a][bq] += acc
    return coef, ex_tot, ez_tot, h, ctxt


def gauss_tm2(centre: arb, ctxt, sign: int, degree: int = 12) -> TM2:
    """phi(centre + sign*x) as a bivariate TM with z-degree 0 (Lagrange form)."""
    from flint import arb_series
    H, h, D, Z, Hp, hp = ctxt
    two_pi = arb(2) * arb.pi()

    def _pad(s, n):
        o = list(s)
        return o + [arb(0)] * (n - len(o)) if len(o) < n else o[:n]
    xs = arb_series([centre, arb(1)], degree + 2)
    fp = (-(xs * xs) / arb(2)).exp() / two_pi.sqrt()
    a = _pad(fp, degree + 2)[: degree + 1]
    xi = arb_series([centre + arb(0, H.upper()), arb(1)], degree + 2)
    fi = (-(xi * xi) / arb(2)).exp() / two_pi.sqrt()
    a = a + [_pad(fi, degree + 2)[degree + 1]]
    out = TM2.zero(ctxt)
    ex = arb(0)
    for k, ak in enumerate(a):
        term = ak * (arb(sign) ** k)
        if k <= D:
            out.c[k][0] += term
        else:
            ex += term.abs_upper() * (H ** k)
    out.ex = ex
    return out


def candidate_sup(cand, t_lo: arb, t_hi: arb) -> arb:
    mid, rad = (t_lo + t_hi) / arb(2), (t_hi - t_lo) / arb(2)
    t = mid + arb(0, rad.upper())
    T = [arb(1), t]
    for _ in range(2, CAND_DEGREE + 1):
        T.append(arb(2) * t * T[-1] - T[-2])
    iv = arb(0)
    for i in range(CAND_DEGREE + 1):
        for j in range(CAND_DEGREE + 1):
            iv += cand[i][j] * T[i] * T[j]
    return iv.abs_upper()


# ==================================== deterministic budget-derived selection
def select_parameters(g, p1, C_SR: float) -> dict:
    """Frozen, deterministic, RESULT-INDEPENDENT parameter selection.

    1. a-priori certified scale:  ||F_0||_inf <= C_SR(e) * ||S_0||_inf
                                             <= C_SR(e) * 2 phi(0)
       and a 2-D Chebyshev coefficient obeys |chat_ij| <= 4 ||F||_inf, so
       Cmax = 4 * C_SR * 2 phi(0) bounds any admissible candidate coefficient.
       NOTHING here involves a candidate or any predecessor residual.
    2. allowable tail fractions come from the FROZEN budget partition, converted
       to defect units by dividing by C_SR(e).
    3. minimal Z, then minimal D, on the frozen ascending grids, are the first
       values whose majorant probe meets the corresponding allowance.

    The probe evaluates the unit-coefficient majorant on the worst panel (the
    one with the largest Gaussian mass) scaled by the panel count.  The rule
    need not itself be conservative: the certificate recomputes every component
    exactly and FAILS if any exceeds its frozen line.
    """
    bud = budget()["absolute"]
    two_pi = arb(2) * arb.pi()
    phi0 = float(arb(1) / two_pi.sqrt())
    scale = C_SR * 2 * phi0
    Cmax = 4 * scale
    d_trunc = bud["B_trunc"] / C_SR
    d_tail = bud["B_tail"] / C_SR
    n_z = p1["n_panels"]
    h = g["span"] / (arb(2) * arb(n_z))
    worst, best = 0, None
    for kp in range(n_z):
        zc = g["L_c"] + arb(2) * h * arb(kp) + h
        v = float((zc + g["e"]).abs_lower())
        if best is None or v < best:
            best, worst = v, kp
    trail = {"a_priori_scale_F0": scale, "Cmax_coefficient_bound": Cmax,
             "delta_trunc_max": d_trunc, "delta_tail_max": d_tail,
             "worst_panel": worst, "n_panels": n_z,
             "stage1_Z": [], "stage2_D": []}
    Z_sel = None
    for Z in Z_GRID:
        _, ex, ez, _, _ = run_panels(None, SOFTPLUS_DEGREE + 1, Z, g, p1,
                                     majorant=True, only_panel=worst)
        tot = float(ez.abs_upper()) * n_z * Cmax
        trail["stage1_Z"].append({"Z": Z, "bound": tot, "allow": d_tail,
                                  "ok": tot <= d_tail})
        if tot <= d_tail:
            Z_sel = Z
            break
    if Z_sel is None:
        trail["FAIL"] = "HARNESS_TAIL_BOUND_FAILURE"
        return trail
    D_sel = None
    for D in D_GRID:
        _, ex, ez, _, _ = run_panels(None, D, Z_sel, g, p1,
                                     majorant=True, only_panel=worst)
        tot = float(ex.abs_upper()) * n_z * Cmax
        jc = required_local_degree("truncate_each_product", D, Z_sel,
                                   float(g["H"]), float(h))
        trail["stage2_D"].append({"D": D, "bound": tot, "allow": d_trunc,
                                  "ok": tot <= d_trunc, "joint": jc["PASS"]})
        if tot <= d_trunc and jc["PASS"]:
            D_sel = D
            break
    if D_sel is None:
        trail["FAIL"] = "HARNESS_ORDER_REQUIREMENT_EXCEEDS_COMPLEXITY"
        return trail
    trail["Z_selected"] = Z_sel
    trail["D_selected"] = D_sel
    trail["joint_consistency"] = required_local_degree(
        "truncate_each_product", D_sel, Z_sel, float(g["H"]), float(h))
    trail["FAIL"] = None
    return trail


# ============================================== the genuine F_0 certificate
def certify(cand, D, Z, g, p1, C_SR: float, cinfo: dict) -> dict:
    b, c, e = g["b"], g["c"], g["e"]
    p_c, m_c, H, U_c, L_c = g["p_c"], g["m_c"], g["H"], g["U_c"], g["L_c"]
    half = arb(1) / arb(2)
    kcoef, ex_k, ez_k, h, ctxt = run_panels(cand, D, Z, g, p1)

    # ---- Fhat on the patch (exact polynomial; z-degree 0)
    tp = TM2.zero(ctxt); tp.c[0][0] = arb(2) * p_c / b - arb(1); tp.c[1][0] = arb(2) / b
    tmn = TM2.zero(ctxt); tmn.c[0][0] = arb(2) * m_c / b - arb(1); tmn.c[1][0] = arb(2) / b
    TVx, TWx = cheb_tm2(tp, CAND_DEGREE), cheb_tm2(tmn, CAND_DEGREE)
    fh = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_f = arb(0)
    for i in range(CAND_DEGREE + 1):
        inner = TM2.zero(ctxt)
        for j in range(CAND_DEGREE + 1):
            if not cand[i][j].is_zero():
                inner = inner + TWx[j].scaled(cand[i][j])
        P, Q = TVx[i], inner
        ex_f += P.mag() * Q.ex + Q.mag() * P.ex
        for a in range(D + 1):
            if P.c[a][0].is_zero():
                continue
            for bq in range(D + 1):
                fh[a][bq] += P.c[a][0] * Q.c[bq][0]

    # ---- S_0 = phi(U_c - alpha + e) - phi(L_c + beta + e)
    up, lo = gauss_tm2(U_c + e, ctxt, -1), gauss_tm2(L_c + e, ctxt, +1)
    s0 = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    for a in range(D + 1):
        s0[a][0] += up.c[a][0]
        s0[0][a] -= lo.c[a][0]
    ex_s = up.ex + lo.ex

    # ---- endpoint slivers (the two x-dependent integration limits)
    def sliver(z_mid):
        ziv = z_mid + arb(0, H.upper())
        ap = L.softplus(p_c + arb(0, H.upper()) + ziv - half)
        am = L.softplus(m_c + arb(0, H.upper()) - ziv - half)
        t_lo = min((arb(2) * ap / b - arb(1)).lower(), (arb(2) * am / b - arb(1)).lower())
        t_hi = max((arb(2) * ap / b - arb(1)).upper(), (arb(2) * am / b - arb(1)).upper())
        w = ziv + e
        two_pi = arb(2) * arb.pi()
        pm = ((-(w * w) / arb(2)).exp() / two_pi.sqrt()).abs_upper()
        return H.abs_upper() * candidate_sup(cand, arb(t_lo), arb(t_hi)) * pm
    sl = sliver(U_c) + sliver(L_c)

    # ---- defect, split into midpoint (the object) and radius (interval channel)
    Hp = [H ** k for k in range(2 * D + 2)]
    eq = itv = arb(0)
    dmid = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    for a in range(D + 1):
        for bq in range(D + 1):
            d = fh[a][bq] - kcoef[a][bq] - s0[a][bq]
            dmid[a][bq] = d
            eq += arb(d.mid()).abs_upper() * Hp[a + bq]
            itv += arb(d.rad()) * Hp[a + bq]

    comp = {
        "equation_defect_polynomial": float(eq.abs_upper()),
        "truncation_patch_local": float((ex_k + ex_f + ex_s).abs_upper()),
        "tail_zeta_and_moments": float(ez_k.abs_upper()),
        "endpoint_slivers": float(sl),
        "interval_arithmetic": float(itv.abs_upper()),
        "rounding_exact_dyadic": 0.0,
    }
    delta = sum(comp.values())
    bud = budget()["absolute"]
    lines = {"equation_defect_polynomial": "B_eq",
             "truncation_patch_local": "B_trunc",
             "tail_zeta_and_moments": "B_tail",
             "endpoint_slivers": "B_end",
             "interval_arithmetic": "B_int",
             "rounding_exact_dyadic": "B_round"}
    charge = {}
    for k, v in comp.items():
        allow = bud[lines[k]] / C_SR
        charge[k] = {"value": v, "budget_line": lines[k],
                     "allowance_delta_units": allow,
                     "fraction_of_line": v / allow if allow > 0 else float("inf"),
                     "PASS": v <= allow}
    return {
        "delta_F0": delta,
        "components": comp,
        "per_line": charge,
        "all_lines_pass": all(x["PASS"] for x in charge.values()),
        "defect_constant_term": float(dmid[0][0].mid()),
        "defect_constant_radius": float(dmid[0][0].rad()),
        "D": D, "Z": Z, "n_panels": p1["n_panels"],
        "panel_half_width": float(h), "patch_half_width": float(H),
        "rho": float(h + H),
        "rounding_note": ("exact-dyadic coefficients are exactly representable, so "
                          "no rounding error enters the defect; all arithmetic error "
                          "is captured in the Arb radii (interval channel)"),
        "dyadic_rounding_abs_sum_construction": cinfo.get("dyadic_rounding_abs_sum"),
    }
