"""C11RD -- manufactured validation. NON-TARGET ONLY: drifts 0, 1 and 5/2 (+ C11R's NT block), and
synthetic polynomial test functions. No cell-306 drift, no D1/D2 value, no original certificate.

Each test returns {"pass": bool, ...}. `python -B c11rd_validate.py [--out PATH]` runs them all.
"""
from __future__ import annotations

import ast
import json
import math
import pathlib
import random
import sys
import time
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c11rd_float as FL  # noqa: E402
import c11rd_kernel as KR  # noqa: E402
import c11rd_model as MD  # noqa: E402
import c11rd_tm as T  # noqa: E402
import c11rd_certify as CE  # noqa: E402

_C11 = HERE.parents[1] / "p5y_k5_tail_c11_n9_independent_certifier" / "code"
E_NT = F(5, 2)
E_LOW = F(1)
NTB = (F(5, 2), F(5, 2) + F(108337, 1250000))       # C11R's frozen NON-TARGET block
TINY = F(1, 2 ** 40)


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def tm_at(tm, u) -> tuple:
    acc = F(0)
    for k, v in tm.c.items():
        t = F(v, T.ONE)
        for ui, d in zip(u, k):
            t *= F(ui) ** d
        acc += t
    r = F(tm.r, T.ONE)
    return acc - r, acc + r


def contains(iv, lo, hi=None) -> bool:
    hi = lo if hi is None else hi
    return iv[0] <= lo and hi <= iv[1]


def overlap(a, b) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def global_cand(g: dict) -> dict:
    """The same bivariate polynomial g(p, m) on every band, and its axis restrictions for band 4."""
    return {0: dict(g), 1: dict(g), 2: dict(g), 3: dict(g),
            ("A", "p"): {i: c for (i, j), c in g.items() if j == 0},
            ("A", "m"): {j: c for (i, j), c in g.items() if i == 0}}


def point_box(p: F, m: F, e: F, order: int = 4):
    """A tiny box in the band that owns (p, m) with the EXACT state at one of its corners, and the
    corner's u-vector: the TM evaluated at that corner encloses the value at exactly (p, m, e).
    The drift interval is degenerate [e, e]."""
    s = p + m
    k = 0 if s < 1 else min(4, int(math.floor(s)))
    if k == 4 or (s >= 4 and (p == 0 or m == 0)):
        ax = "p" if m == 0 else "m"
        if s < 5:
            return KR.Box(4, (s, s + TINY), (e, e), axis=ax, order=order), (-1, 0, 0)
        return KR.Box(4, (s - TINY, s), (e, e), axis=ax, order=order), (1, 0, 0)
    th = (p - m) / s if s > 0 else F(0)
    if s < k + 1:
        sb, us = (s, s + TINY), -1
    else:
        sb, us = (s - TINY, s), 1
    if th < 1:
        tb, ut = (th, th + TINY), -1
    else:
        tb, ut = (th - TINY, th), 1
    return KR.Box(k, sb, (e, e), theta=tb, order=order), (us, ut, 0)


def kernel_at(cand: dict, p: F, m: F, e: F, orders=(0, 1, 2), order: int = 4) -> tuple:
    bx, u = point_box(p, m, e, order)
    KD = KR.kernel_box(bx, [cand], orders=orders)
    return {i: tm_at(KD[(i, 0)], u) for i in orders}, (bx, u)


def c7_phi(x):
    return T.phi_point(F(x))


def c7_Phi(x):
    return T.Phi_point(F(x))


def iv_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def iv_sub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def iv_scale(a, c):
    c = F(c)
    return (a[0] * c, a[1] * c) if c >= 0 else (a[1] * c, a[0] * c)


def iv_mul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (min(ps), max(ps))


SAMPLE_STATES = [(F(1, 8), F(1, 4)), (F(0), F(0)), (F(3, 5), F(1, 5)), (F(1, 2), F(3, 4)),
                 (F(1), F(1)), (F(7, 4), F(1, 2)), (F(3), F(1, 2)), (F(0), F(9, 2)),
                 (F(19, 4), F(0)), (F(2), F(0))]


# ---------------------------------------------------------------------------------------------
# V01 Gaussian moment identities (exact closed forms; finite and whole-line)
# ---------------------------------------------------------------------------------------------
def v01_gaussian_moments():
    cases, ok = [], True
    for yc, a, b in ((F(7, 4), F(-1, 2), F(1, 2)), (F(-3), F(-3, 8), F(5, 8)), (F(13, 2), F(-1, 2), F(1, 2)),
                     (F(0), F(-1), F(1)), (F(-8), F(-1, 4), F(3, 4))):
        A = T.TM.const(3, 4, a)
        B = T.TM.const(3, 4, b)
        I = T.centred_moments(yc, A, B, 3, 36)
        al, be = yc + a, yc + b
        pa, pb, Pa, Pb = c7_phi(al), c7_phi(be), c7_Phi(al), c7_Phi(be)
        M0 = iv_sub(Pb, Pa)
        M1 = iv_sub(pa, pb)
        M2 = iv_add(M0, iv_sub(iv_scale(pa, al), iv_scale(pb, be)))
        M3 = iv_add(iv_scale(M1, 2), iv_sub(iv_scale(pa, al ** 2), iv_scale(pb, be ** 2)))
        M = [M0, M1, M2, M3]
        for k in range(4):   # centred I_k = sum_i C(k,i) (-yc)^(k-i) M_i
            ref = (F(0), F(0))
            for i in range(k + 1):
                ref = iv_add(ref, iv_scale(M[i], math.comb(k, i) * (-yc) ** (k - i)))
            got = tm_at(I[k], (0, 0, 0))
            good = overlap(got, ref)
            ok &= good
            cases.append({"yc": str(yc), "k": k, "overlap": good,
                          "width": float(got[1] - got[0])})
    # whole-line even moments int y^(2k) phi = (2k-1)!!, over [-12, 12] in unit pieces
    for k in range(0, 5):
        tot = (F(0), F(0))
        for c in range(-12, 12):
            yc = F(2 * c + 1, 2)
            A, B = T.TM.const(3, 4, F(-1, 2)), T.TM.const(3, 4, F(1, 2))
            I = T.centred_moments(yc, A, B, 2 * k, 36)
            # int (yc + v)^(2k) phi = sum C(2k, r) yc^(2k-r) I_r
            for r in range(2 * k + 1):
                tot = iv_add(tot, iv_scale(tm_at(I[r], (0, 0, 0)), math.comb(2 * k, r) * yc ** (2 * k - r)))
        dfact = math.prod(range(1, 2 * k, 2)) if k else 1
        tail = F(1, 10 ** 25)
        good = tot[0] - tail <= dfact <= tot[1] + tail
        ok &= good
        cases.append({"whole_line_moment": 2 * k, "exact": dfact, "enclosure": [float(tot[0]), float(tot[1])],
                      "pass": good})
    return {"pass": ok, "cases": cases}


# ---------------------------------------------------------------------------------------------
# V02 known kernel images of f = 1 (closed forms), all three derivative orders
# ---------------------------------------------------------------------------------------------
def closed_khat1(p, m, e):
    """Khat^(i) 1 = [Phi^(i)-antiderivative over the window] minus the atom window if s < 1:
    i = 0: Phi(u+e) - Phi(l+e); i = 1: phi(u+e) - phi(l+e); i = 2: phi'(u+e) - phi'(l+e)."""
    K, C = F(1, 2), F(11, 2)
    u, l = C - p + e, m - C + e
    out = {0: iv_sub(c7_Phi(u), c7_Phi(l)), 1: iv_sub(c7_phi(u), c7_phi(l)),
           2: iv_sub(iv_scale(c7_phi(u), -u), iv_scale(c7_phi(l), -l))}
    if p + m < 1:
        au, al = K - p + e, m - K + e
        out[0] = iv_sub(out[0], iv_sub(c7_Phi(au), c7_Phi(al)))
        out[1] = iv_sub(out[1], iv_sub(c7_phi(au), c7_phi(al)))
        out[2] = iv_sub(out[2], iv_sub(iv_scale(c7_phi(au), -au), iv_scale(c7_phi(al), -al)))
    return out


def v02_kernel_of_one():
    one = global_cand({(0, 0): F(1)})
    cases, ok = [], True
    for e in (E_NT, E_LOW):
        for (p, m) in SAMPLE_STATES:
            got, _ = kernel_at(one, p, m, e)
            ref = closed_khat1(p, m, e)
            for i in (0, 1, 2):
                good = overlap(got[i], ref[i])
                ok &= good
                cases.append({"e": str(e), "x": [str(p), str(m)], "order": i, "pass": good,
                              "width": float(got[i][1] - got[i][0])})
    return {"pass": ok, "cases": cases}


# ---------------------------------------------------------------------------------------------
# V03 cross-check against C11's INDEPENDENT exact full kernel (K_e = Khat_e + atom term)
# ---------------------------------------------------------------------------------------------
def v03_vs_c11_kernel():
    sys.path.insert(0, str(_C11))
    import c11_certifier as C11
    K = F(1, 2)
    polys = [{(1, 0): F(1)}, {(0, 1): F(1)}, {(1, 1): F(1)}, {(2, 0): F(1), (0, 1): F(-1, 3)},
             {(0, 0): F(1), (1, 0): F(1, 5), (0, 2): F(-1, 7)}]
    cases, ok = [], True
    for g in polys:
        cand = global_cand(g)
        fa = g.get((0, 0), F(0))
        for e in (E_NT, E_LOW):
            for (p, m) in SAMPLE_STATES[:7]:
                got, _ = kernel_at(cand, p, m, e, orders=(0,))
                khat = got[0]
                if p + m < 1:                    # K = Khat + f(a) * atom mass
                    mass = iv_sub(c7_Phi(K - p + e), c7_Phi(m - K + e))
                    khat = iv_add(khat, iv_scale(mass, fa))
                ref = C11.kernel_apply(g, p, m, e)
                good = overlap(khat, (ref.lo, ref.hi))
                ok &= good
                cases.append({"f": {f"{i},{j}": str(c) for (i, j), c in g.items()}, "e": str(e),
                              "x": [str(p), str(m)], "atom_term_added": p + m < 1 and fa != 0,
                              "pass": good})
    return {"pass": ok, "cases": cases, "reference": "c11_certifier.kernel_apply (exact, full kernel)"}


# ---------------------------------------------------------------------------------------------
# V04 finite differences in the drift (non-target), rigorous tolerance
# ---------------------------------------------------------------------------------------------
def v04_finite_difference():
    g = {(0, 0): F(1), (1, 0): F(1, 5), (0, 2): F(-1, 20), (1, 1): F(1, 30)}
    cand = global_cand(g)
    fsup = F(1) + F(5, 5) + F(25, 20) + F(25, 30)          # crude sup |f| on [0,5]^2
    eps = F(1, 1000)
    # int |phi'''| = 2 (phi(0) + 4 phi(sqrt 3)) = 1.5118..;  int |phi''''| = 2.80.. (zeros of He_4)
    kappa3 = F(16, 10)
    kappa4 = F(3)
    cases, ok = [], True
    for (p, m) in SAMPLE_STATES[:6]:
        for e in (E_NT, E_LOW):
            kp, _ = kernel_at(cand, p, m, e + eps, orders=(0,))
            km, _ = kernel_at(cand, p, m, e - eps, orders=(0,))
            k0, _ = kernel_at(cand, p, m, e, orders=(0, 1, 2))
            fd1 = iv_scale(iv_sub(kp[0], km[0]), 1 / (2 * eps))
            tol1 = fsup * kappa3 * eps ** 2 / 6
            good1 = overlap((fd1[0] - tol1, fd1[1] + tol1), k0[1])
            fd2 = iv_scale(iv_sub(iv_add(kp[0], km[0]), iv_scale(k0[0], 2)), 1 / eps ** 2)
            tol2 = fsup * kappa4 * eps ** 2 / 12
            good2 = overlap((fd2[0] - tol2, fd2[1] + tol2), k0[2])
            ok &= good1 and good2
            cases.append({"x": [str(p), str(m)], "e": str(e), "first": good1, "second": good2})
    return {"pass": ok, "cases": cases, "eps": str(eps)}


# ---------------------------------------------------------------------------------------------
# V05 / V06 scalar-drift collapse and block-uniform enclosure (NT candidates)
# ---------------------------------------------------------------------------------------------
_NT_CANDS = {}


def nt_candidates(n: int = 6):
    if n not in _NT_CANDS:
        ec = (NTB[0] + NTB[1]) / 2
        prop = FL.propose(float(ec), n=n, n4=n, ns=9, nt=9)
        _NT_CANDS[n] = (prop, [FL.exact_candidate(prop["basis"], c) for c in prop["coeffs"]])
    return _NT_CANDS[n]


def v05_scalar_collapse():
    prop, cands = nt_candidates()
    ec = (NTB[0] + NTB[1]) / 2
    cases, ok = [], True
    for band, s, th in ((1, (F(5, 4), F(3, 2)), (F(0), F(1, 4))), (0, (F(1, 4), F(1, 2)), (F(-1, 2), F(0)))):
        blk = KR.residuals_box(KR.Box(band, s, NTB, theta=th, order=4), cands)
        pt = KR.residuals_box(KR.Box(band, s, (ec, ec), theta=th, order=4), cands)
        for key in ("r0", "r1", "r2"):
            # the point-drift enclosure at the box centre must meet the block enclosure at u_e = 0
            a = tm_at(blk[key], (0, 0, 0))
            b = tm_at(pt[key], (0, 0, 0))
            good = overlap(a, b)
            ok &= good
            cases.append({"band": band, "residual": key, "pass": good,
                          "block_width": float(a[1] - a[0]), "point_width": float(b[1] - b[0])})
    return {"pass": ok, "cases": cases}


def float_residuals(prop, p, m, band, e, ec):
    Bz, cf = prop["basis"], prop["coeffs"]
    kr = FL.kernel_rows(Bz, p, m, band, e, orders=(0, 1, 2), q=30)
    bp = Bz.eval_band(band, p, m)
    Dv = [sum(c[i] * v for i, v in bp.items()) for c in cf]
    Kv = {(i, j): sum(kr[i][t] * cf[j][t] for t in range(Bz.size)) for i in (0, 1, 2) for j in range(4)}
    h = e - ec
    fact = [1, 1, 2, 6]
    et = lambda vals, k: sum(h ** (j - k) / fact[j - k] * vals[j] for j in range(k, 4))
    kt = lambda i, k: et([Kv[(i, j)] for j in range(4)], k)
    src = FL.h1_derivs(p, m, e, 2)
    return [et(Dv, 0) - kt(0, 0) - src[0], et(Dv, 1) - kt(0, 1) - kt(1, 0) - src[1],
            et(Dv, 2) - kt(0, 2) - 2 * kt(1, 1) - kt(2, 0) - src[2]]


def v06_block_uniform():
    rnd = random.Random(11)
    prop, cands = nt_candidates()
    ec = float((NTB[0] + NTB[1]) / 2)
    boxes = [KR.Box(0, (F(1, 2), F(3, 4)), NTB, theta=(F(1, 2), F(1)), order=4),
             KR.Box(2, (F(9, 4), F(5, 2)), NTB, theta=(F(-1, 4), F(0)), order=4),
             KR.Box(4, (F(17, 4), F(9, 2)), NTB, axis="p", order=4)]
    cases, ok = [], True
    for bx in boxes:
        R = KR.residuals_box(bx, cands)
        for _ in range(4):
            u = [rnd.uniform(-1, 1) for _ in range(3)]
            s = float((F(bx.s[0]) + F(bx.s[1])) / 2) + float((F(bx.s[1]) - F(bx.s[0])) / 2) * u[0]
            e = float(bx.ec) + float(bx.de) * u[2]
            if bx.band == 4:
                p, m = (s, 0.0) if bx.axis == "p" else (0.0, s)
            else:
                tc = float((F(bx.theta[0]) + F(bx.theta[1])) / 2)
                tw = float((F(bx.theta[1]) - F(bx.theta[0])) / 2)
                th = tc + tw * u[1]
                p, m = s * (1 + th) / 2, s * (1 - th) / 2
            fr = float_residuals(prop, p, m, bx.band, e, ec)
            uu = [F(x) for x in u]
            for kk, key in enumerate(("r0", "r1", "r2")):
                lo, hi = tm_at(R[key], uu)
                good = float(lo) - 1e-9 <= fr[kk] <= float(hi) + 1e-9
                ok &= good
                cases.append({"band": bx.band, "residual": key, "pass": good})
    return {"pass": ok, "cases": len(cases), "failures": [c for c in cases if not c["pass"]]}


# ---------------------------------------------------------------------------------------------
# V07 / V08 atom vs atom-removed; K_e vs Khat_e negative control
# ---------------------------------------------------------------------------------------------
def v07_atom_distinction():
    K = F(1, 2)
    one = global_cand({(0, 0): F(1)})
    cases, ok = [], True
    for (p, m) in ((F(1, 8), F(1, 4)), (F(0), F(0)), (F(3, 5), F(1, 5))):
        got, _ = kernel_at(one, p, m, E_NT, orders=(0,))
        mass = iv_sub(c7_Phi(K - p + E_NT), c7_Phi(m - K + E_NT))
        full = closed_khat1(p, m, E_NT)[0]
        full = iv_add(full, mass)                          # K 1 = Khat 1 + atom mass
        differ = mass[0] > (got[0][1] - got[0][0]) * 2     # the atom mass exceeds the enclosure width
        ok &= differ
        cases.append({"x": [str(p), str(m)], "atom_mass_lower": float(mass[0]),
                      "khat_width": float(got[0][1] - got[0][0]), "distinguished": differ})
    return {"pass": ok, "cases": cases}


def v08_full_kernel_negative_control():
    """The Khat-candidate residual recomputed with the FULL kernel (adding D0(a) * atom mass) must be
    large in band 0: the check tells the two kernels apart."""
    prop, cands = nt_candidates()
    K = F(1, 2)
    bx = KR.Box(0, (F(1, 4), F(1, 4) + TINY), (NTB[0], NTB[0]), theta=(F(0), TINY), order=4)
    R = KR.residuals_box(bx, cands)
    r0 = tm_at(R["r0"], (-1, -1, 0))
    p = m = F(1, 8)
    mass = iv_sub(c7_Phi(K - p + NTB[0]), c7_Phi(m - K + NTB[0]))
    Da = cands[0][0].get((0, 0), F(0))
    r0_full = iv_sub(r0, iv_scale(mass, Da))
    # the K_e reading of the same candidate is EXCLUDED by the Khat_e enclosure, and is larger
    good = not overlap(r0, r0_full) and min(abs(r0_full[0]), abs(r0_full[1])) > max(abs(r0[0]), abs(r0[1]))
    return {"pass": good, "r0_khat": [float(r0[0]), float(r0[1])],
            "r0_full_kernel": [float(r0_full[0]), float(r0_full[1])]}


# ---------------------------------------------------------------------------------------------
# V09 premise (C11R F_H) and its tamper controls
# ---------------------------------------------------------------------------------------------
def v09_premise():
    cases = {}
    pr = MD.c11r_fh_premise()
    cases["honest"] = pr["C_T"] == F(3429, 500) and pr["tau"] == F(3429, 500) and pr["B"] == F(1113, 1000)
    import copy
    real = MD._load_bound

    def run_with(mut):
        def fake(rel, blob):
            d = copy.deepcopy(real(rel, blob))
            if rel == MD.C11R_RUNS_REL:
                mut(d["certificates"]["F_H"])
            return d
        MD._load_bound = fake
        try:
            MD.c11r_fh_premise()
            return False                      # must refuse
        except MD.ModelError:
            return True
        finally:
            MD._load_bound = real
    cases["refuses_K_e_kernel"] = run_with(lambda c: c["certifier_result"].__setitem__("kernel", "K_e"))
    cases["refuses_atom_not_removed"] = run_with(lambda c: c["inputs"].__setitem__("atom_removed_argument", False))
    cases["refuses_cell_307_block"] = run_with(lambda c: c["inputs"].__setitem__(
        "drift_block", ["17885921/10000000", "1882413/1000000"]))
    cases["refuses_increasing_weight"] = run_with(lambda c: c["weight"].__setitem__("0,1", "1113/1000"))
    cases["refuses_uncertified"] = run_with(lambda c: c["certifier_result"].__setitem__("certified", False))
    cases["refuses_premises"] = run_with(lambda c: c.__setitem__("premises", ["C_T"]))
    try:
        MD._load_bound(MD.C11R_RUNS_REL, "0" * 40)
        cases["refuses_wrong_blob"] = False
    except MD.ModelError:
        cases["refuses_wrong_blob"] = True
    # propagation is increasing in C_T and tau
    kap = MD.kernel_norms()
    a = CE.propagate([F(1, 10 ** 4)] * 3, F(3429, 500), F(3429, 500), kap)
    b = CE.propagate([F(1, 10 ** 4)] * 3, F(4), F(4), kap)
    cases["propagation_monotone_in_premise"] = a["err_D1"] > b["err_D1"] and a["err_D2"] > b["err_D2"]
    return {"pass": all(cases.values()), "cases": cases}


# ---------------------------------------------------------------------------------------------
# V10 / V11 / V12 zero, symmetric and known-sign cases
# ---------------------------------------------------------------------------------------------
def v10_zero_cases():
    zero = global_cand({})
    got, _ = kernel_at(zero, F(1, 2), F(1, 2), E_NT)
    all_zero = all(got[i] == (F(0), F(0)) for i in (0, 1, 2))
    # h_1' at a symmetric state with e = 0 is 0
    bx, u = point_box(F(3, 2), F(3, 2), F(0))
    src = KR.sources(bx)
    h1p = tm_at(src[1], u)
    one = global_cand({(0, 0): F(1)})
    k1, _ = kernel_at(one, F(1, 2), F(1, 2), F(0), orders=(1,))
    return {"pass": all_zero and contains(h1p, F(0)) and contains(k1[1], F(0)),
            "kernel_of_zero_is_zero": all_zero, "h1_prime_symmetric_contains_0": contains(h1p, F(0)),
            "khat_prime_1_symmetric_contains_0": contains(k1[1], F(0))}


def v11_symmetry():
    g = {(0, 0): F(1), (1, 0): F(1, 7), (0, 1): F(1, 7), (1, 1): F(1, 13)}     # f(p, m) = f(m, p)
    cand = global_cand(g)
    cases, ok = [], True
    for (p, m) in ((F(1, 8), F(1, 4)), (F(1, 2), F(3, 4)), (F(3, 2), F(1, 3)), (F(0), F(9, 2))):
        a, _ = kernel_at(cand, p, m, F(0), orders=(0, 2))
        b, _ = kernel_at(cand, m, p, F(0), orders=(0, 2))
        good = overlap(a[0], b[0]) and overlap(a[2], b[2])
        ok &= good
        cases.append({"x": [str(p), str(m)], "mirror_agrees": good})
    for q in (F(1, 4), F(3, 4), F(3, 2)):
        k1, _ = kernel_at(cand, q, q, F(0), orders=(1,))
        good = contains(k1[1], F(0))
        ok &= good
        cases.append({"x": [str(q), str(q)], "odd_derivative_contains_0": good})
    return {"pass": ok, "cases": cases}


def v12_known_signs():
    one = global_cand({(0, 0): F(1)})
    cases, ok = [], True
    for (p, m) in SAMPLE_STATES:
        got, (bx, u) = kernel_at(one, p, m, E_NT, orders=(0,))
        h = tm_at(KR.sources(bx)[0], u)
        good = 0 < got[0][0] and got[0][1] < 1 and 0 < h[0] and h[1] < 1
        ok &= good
        cases.append({"x": [str(p), str(m)], "khat1_in_(0,1)_and_h1_in_(0,1)": good})
    return {"pass": ok, "cases": cases}


# ---------------------------------------------------------------------------------------------
# V13 kink-crossing boxes refused; continuity across band lines for a continuous function
# ---------------------------------------------------------------------------------------------
def v13_kinks():
    refused = {}
    for label, args in (("s_across_1", (0, (F(9, 10), F(11, 10)), NTB, (F(0), F(1, 2)), None)),
                        ("s_across_2", (1, (F(3, 2), F(5, 2)), NTB, (F(0), F(1, 2)), None)),
                        ("theta_out_of_range", (1, (F(1), F(3, 2)), NTB, (F(1, 2), F(3, 2)), None)),
                        ("band4_without_axis", (4, (F(4), F(9, 2)), NTB, None, None))):
        band, s, e, th, ax = args
        try:
            KR.Box(band, s, e, theta=th, axis=ax)
            refused[label] = False
        except ValueError:
            refused[label] = True
    g = {(0, 0): F(1), (1, 0): F(1, 5), (0, 2): F(-1, 20)}
    cand = global_cand(g)
    cont, ok = [], True
    for k in (1, 2, 3):
        for th in (F(-1, 2), F(0), F(1, 3)):
            lo_box = KR.Box(k - 1, (F(k) - TINY, F(k)), (E_NT, E_NT), theta=(th, th + TINY), order=4)
            hi_box = KR.Box(k, (F(k), F(k) + TINY), (E_NT, E_NT), theta=(th, th + TINY), order=4)
            a = KR.kernel_box(lo_box, [cand], orders=(0, 1))
            b = KR.kernel_box(hi_box, [cand], orders=(0, 1))
            # both boxes contain the exact state (s = k, theta = th): corner u_s = +1 / -1, u_t = -1
            good = all(overlap(tm_at(a[(i, 0)], (1, -1, 0)), tm_at(b[(i, 0)], (-1, -1, 0))) for i in (0, 1))
            ok &= good
            cont.append({"line": k, "theta": str(th), "both_regimes_agree": good})
    return {"pass": ok and all(refused.values()), "refused": refused, "continuity": cont}


# ---------------------------------------------------------------------------------------------
# V14 very small drift intervals
# ---------------------------------------------------------------------------------------------
def v14_tiny_drift():
    one = global_cand({(0, 0): F(1)})
    got, _ = kernel_at(one, F(1, 3), F(1, 5), E_NT)
    widths = [got[i][1] - got[i][0] for i in (0, 1, 2)]
    ref = closed_khat1(F(1, 3), F(1, 5), E_NT)
    good = all(w < F(1, 10 ** 9) for w in widths) and all(overlap(got[i], ref[i]) for i in (0, 1, 2))
    return {"pass": good, "widths": [float(w) for w in widths]}


# ---------------------------------------------------------------------------------------------
# V15 deliberately invalid derivative bounds must be rejected
# ---------------------------------------------------------------------------------------------
def _one_box_bound(bx, cands, kappa, which: int):
    """The D_which bound the propagation would give if bx were the whole cover (a manufactured
    quantity used only to exercise the refusal logic; not a certificate)."""
    R = KR.residuals_box(bx, cands)
    lam = [R[k].abs_upper() for k in ("r0", "r1", "r2")]
    av = CE.atom_values(cands, bx.de)
    pr = CE.propagate(lam, F(3429, 500), F(3429, 500), kappa)
    return (av[1] + pr["err_D1"]) if which == 1 else (av[2] + pr["err_D2"]), lam, av


def v15_invalid_bounds():
    """Deliberately invalid derivative bounds must be REFUSED. Every refusal below is by strict
    comparison with the bound recomputed from the claimed ingredients; no tolerance factor."""
    prop, cands = nt_candidates()
    kap = MD.kernel_norms()
    CT = F(3429, 500)
    bx = KR.Box(4, (F(17, 4), F(9, 2)), NTB, axis="m", order=4)       # h_1' is large here
    out = {}
    B_h, lam_h, av_h = _one_box_bound(bx, cands, kap, 1)
    # (a) a claim computed with the honest candidate, presented for a sign-flipped D1 candidate, on
    #     a band-1 box where D1 is not small
    bx1 = KR.Box(1, (F(1), F(5, 4)), NTB, theta=(F(-1, 4), F(0)), order=4)
    B1h, lam1h, av1h = _one_box_bound(bx1, cands, kap, 1)
    flipped = [cands[0], {k: {kk: -v for kk, v in pol.items()} for k, pol in cands[1].items()},
               cands[2], cands[3]]
    B_f, lam_f, _ = _one_box_bound(bx1, flipped, kap, 1)
    out["flipped_D1_candidate_refused"] = lam_f[1] > lam1h[1] and \
        not verify_claim(B1h, av1h[1], lam_f, CT, CT, kap)
    # (b) the sign of h_1' flipped in the source: the honest candidate's r1 moves by 2 h_1'
    real_sources = KR.sources
    try:
        def flipped_sources(b):
            s = real_sources(b)
            return [s[0], -s[1], s[2]]
        KR.sources = flipped_sources
        R_bad = KR.residuals_box(bx, cands)
    finally:
        KR.sources = real_sources
    lam_bad = [R_bad[k].abs_upper() for k in ("r0", "r1", "r2")]
    out["flipped_h1prime_sign_refused"] = lam_bad[1] > lam_h[1] and \
        not verify_claim(B_h, av_h[1], lam_bad, CT, CT, kap)
    # (c) a claim computed with a WRONG kappa (zero) is refused under the true kappa
    wrong = CE.propagate(lam_h, CT, CT, {1: F(0), 2: F(0)})
    out["zero_kappa_claim_refused"] = not verify_claim(av_h[1] + wrong["err_D1"], av_h[1], lam_h, CT, CT, kap)
    # (d) a claimed D1 one unit in the 12th place below the recomputed bound is refused; the exact
    #     recomputed bound is accepted
    out["under_claimed_D1_refused"] = verify_claim(B_h, av_h[1], lam_h, CT, CT, kap) and \
        not verify_claim(B_h - F(1, 10 ** 12), av_h[1], lam_h, CT, CT, kap)
    out["under_claimed_D2_refused"] = verify_claim(B2 := _one_box_bound(bx, cands, kap, 2)[0], None,
                                                   lam_h, CT, CT, kap, which=2, cands=cands, de=bx.de) and \
        not verify_claim(B2 - F(1, 10 ** 12), None, lam_h, CT, CT, kap, which=2, cands=cands, de=bx.de)
    # (e) kernel norms are rigorous upper enclosures of the closed forms 2 phi(0), 4 phi(1)
    p0, p1 = T.phi_point(F(0)), T.phi_point(F(1))
    out["kernel_norms_rigorous"] = kap[1] >= 2 * p0[1] and kap[2] >= 4 * p1[1] and \
        kap[1] - 2 * p0[0] < F(1, 10 ** 20) and kap[2] - 4 * p1[0] < F(1, 10 ** 20)
    return {"pass": all(out.values()), "checks": out, "honest_lam_band4": [float(x) for x in lam_h],
            "honest_lam_band1": [float(x) for x in lam1h], "flipped_D1_lam_band1": [float(x) for x in lam_f],
            "flipped_h1prime_lam_band4": [float(x) for x in lam_bad]}


def verify_claim(claimed: F, atom_bound, lam: list, C_T: F, tau: F, kappa: dict, *, which: int = 1,
                 cands=None, de=None) -> bool:
    """A claimed D_which is accepted only if it is >= the bound RECOMPUTED from its ingredients
    (the atom bound is recomputed from the candidates when they are given)."""
    if cands is not None:
        atom_bound = CE.atom_values(cands, de)[which]
    rec = CE.propagate(lam, C_T, tau, kappa)
    return claimed >= atom_bound + rec["err_D1" if which == 1 else "err_D2"]


# ---------------------------------------------------------------------------------------------
# V16 independence scan (imports and data paths)
# ---------------------------------------------------------------------------------------------
FORBIDDEN_IMPORTS = {"taboo_certify", "resolvent_certificate", "opnorms", "ra_certifier", "fast_range",
                     "intervals", "rebaseguard_certify", "rung3_engine", "spec", "cusum_layer1",
                     "cusum_layer2", "ancestry5", "numpy", "flint", "mpmath", "scipy", "sympy", "gmpy2"}
CERTIFIER_MODULES = ("c11rd_tm.py", "c11rd_model.py", "c11rd_float.py", "c11rd_kernel.py",
                     "c11rd_certify.py", "c11rd_runs.py")
FORBIDDEN_DATA = ("REGISTRY_C2", "C11R_ORIGINAL_MAGNITUDES", "C11R_COMPARISON", "quarantine",
                  "taboo_cell", "denominator_artifact", "ADJUDICATION_", "REVIEW_")


def _import_roots(path: pathlib.Path) -> set:
    roots = set()
    for n in ast.walk(ast.parse(path.read_text())):
        if isinstance(n, ast.Import):
            roots |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            roots.add(n.module.split(".")[0])
    return roots


def v16_independence():
    """(a) static: no C11RD module and no module they load from outside the namespace (C7's
    c7_gaussian) imports a forbidden root; (b) RUNTIME: a fresh isolated interpreter that imports
    every certifier module has no forbidden module in sys.modules; (c) no certifier module names a
    forbidden data source."""
    import subprocess
    hits, data_hits, scanned = {}, {}, []
    c7 = HERE.parents[1] / "p5y_k5_tail_c7_e2_lambda309" / "code" / "c7_gaussian.py"
    for f in sorted(HERE.glob("c11rd_*.py")) + [c7]:
        bad = sorted(_import_roots(f) & FORBIDDEN_IMPORTS)
        if bad:
            hits[f.name] = bad
        scanned.append(f.name)
        if f.name in CERTIFIER_MODULES:
            found = [s for s in FORBIDDEN_DATA if s in f.read_text()]
            if found:
                data_hits[f.name] = found
    mods = [m[:-3] for m in CERTIFIER_MODULES if (HERE / m).exists()]
    code = ("import sys; sys.path.insert(0, %r)\n" % str(HERE)
            + "".join(f"import {m}\n" for m in mods)
            + "print('\\n'.join(sorted(sys.modules)))")
    out = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code], capture_output=True, text=True,
                         timeout=600)
    loaded = set(out.stdout.split())
    runtime_bad = sorted({m.split(".")[0] for m in loaded} & FORBIDDEN_IMPORTS)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        planted = pathlib.Path(td) / "planted.py"
        planted.write_text("import taboo_certify\nfrom opnorms import x\nimport numpy.linalg\n")
        control = sorted(_import_roots(planted) & FORBIDDEN_IMPORTS) == ["numpy", "opnorms", "taboo_certify"]
    ok = not hits and not data_hits and out.returncode == 0 and not runtime_bad and len(loaded) > 10 and control
    return {"pass": ok, "scanned": scanned, "forbidden_imports": hits,
            "forbidden_data_references_in_certifier": data_hits, "runtime_modules_checked": len(loaded),
            "runtime_imported_modules": mods, "runtime_forbidden": runtime_bad,
            "runtime_returncode": out.returncode, "negative_control_flagged": control}


NUMERIC_ALLOWLIST = {0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 20, 30, 34, 40, 50, 52, 100, 160, 200000, 306,
                     0.25, 0.5, 1.0, 2.0, 4.5, 5.0, 5.5, 1e-16}
RATIONAL_STRING_ALLOWLIST = {"680769/400000", "17885921/10000000"}     # cell 306's block (checked vs table)


def v17_no_embedded_magnitudes():
    """Every numeric literal in the certifier modules is a structural constant from an explicit
    allowlist, and no string literal carries a decimal with >= 3 fractional digits or a rational with
    a >= 4-digit numerator other than the cell block: no D1/D2 magnitude (original or otherwise) can be
    embedded in the execution logic. (The post-hoc check against the ORIGINAL strings is a comparator
    obligation, performed only after the sealed result exists.)"""
    import tempfile
    files = [HERE / n for n in CERTIFIER_MODULES if (HERE / n).exists()]
    bad = _literal_scan(files)
    # negative control: planted magnitudes MUST be flagged (the scanner can fail)
    with tempfile.TemporaryDirectory() as td:
        planted = pathlib.Path(td) / "planted.py"
        planted.write_text('X = 0.1234\nY = "D1 <= 0.98765"\nZ = "12345/100000"\n')
        caught = _literal_scan([planted]).get("planted.py", [])
    control = len(caught) == 3
    return {"pass": not bad and control, "violations": bad, "negative_control_flagged": caught,
            "files_scanned": [f.name for f in files], "allowlist": sorted(map(str, NUMERIC_ALLOWLIST))}


def _literal_scan(files: list) -> dict:
    import re
    dec = re.compile(r"\d+\.\d{3,}")
    rat = re.compile(r"\d{4,}/\d+")
    bad = {}
    for f in files:
        name = f.name
        tree = ast.parse(f.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant):
                v = n.value
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v not in NUMERIC_ALLOWLIST:
                    bad.setdefault(name, []).append(repr(v))
                elif isinstance(v, str):
                    for hit in dec.findall(v) + [r for r in rat.findall(v) if r not in RATIONAL_STRING_ALLOWLIST]:
                        bad.setdefault(name, []).append(hit)
    return bad


# sha256 of every rendering (truncation or rounding, >= 4 significant digits) of the two ORIGINAL
# values disclosed in the campaign instruction, as c11rd_compare.value_patterns generates them. The
# values themselves appear nowhere in the namespace; a reviewer recomputes these hashes from the
# instruction's two numbers with value_patterns.
ORIGINAL_PATTERN_SHA256 = frozenset({
    "12503916defdb3c955a4739509604b2c26ce425e8eb15e84c2b12f84a93b1a75",
    "1737392ce9298211a79d8f62db77061589442cd622f8c1e66a34ddde782411af",
    "1e8126c7e367e3ab525fb3b4c1873b9109f069f5c1131334d3c1e0a9ef008e32",
    "2dd46127f8f6c22ac5ff106e55c4db56295df66f5c6514be52eb444e6e0d9339",
    "3d9bab0177b9f6b1c1d6b7ab7b804147e2243462eada37f5f5d1a735d8d9a460",
    "456dd9a7fb5ffc21cad93b3e7ee964720bfc0be9835585db8e94abca8e3a7498",
    "4a4e735424c6c4ef8a88f682a7cc2b00dbd2d0b8254fdcf57c67af716106c681",
    "57ae262040ae7ac7f48d48f0385fd6caa2331157831c518dd12fdb808a4b7eb8",
    "88de08d2139af9ed56ccf556908001cb05a21c6e11ba442b6169a4d617455fa8",
    "91fe67d6d28a19b3e7c9b6938af5f3158913e1234efffa7271b853bb49232f9f",
    "9d27d2c5810081a52969d6a6c5e4d34b27c4e7bd7ecdb06e169724a740edb79a",
    "a178e45cc97bd2238430d5f871b503db4c0de27902f92388e1126fd91a8ecbb6",
    "c5b5543b41d74540bdc1464bc17b78197b956cd221bbee165709fa2fa5c23385",
    "ca38bcb6a89245e99f1bdc1d1673b7f80062aa6e221c645b31db8ab6ba442e32",
    "d6e347faea66ecd6da8907afe9a89524ee5535c6065705593f3469548b10b1ec",
    "e7f14443df7d83993cb9e0e749c2762b5c0fb737b2d4a1e542ed0ae46a4a5eaa",
    "ec81b983b2b5f7fd873bb4e3895d7f890d9b47cb9b058c9b8831dac205c6ace1"})


def _hashed_leak_scan(files: list, hashes: frozenset) -> dict:
    import hashlib
    import c11rd_compare as CM
    hits = {}
    for f in files:
        try:
            txt = f.read_text()
        except UnicodeDecodeError:
            continue
        for tok in CM.NUMERIC_TOKEN.findall(txt):
            if any(hashlib.sha256(x.encode()).hexdigest() in hashes for x in CM.token_prefixes(tok)):
                hits.setdefault(str(f.relative_to(f.parents[len(f.relative_to(HERE.parent).parts) - 1])), []).append(tok)
    return hits


def v18_no_original_values_anywhere():
    """PRE-VERIFIES the comparator's post-hoc leak check U7: no file of the namespace (code, docs,
    theory, protocol, evidence, review) has a numeric token starting with any rendering of the two
    original values. The detector is shown able to fail on a planted decoy."""
    import hashlib
    import tempfile
    files = sorted(f for f in HERE.parent.rglob("*") if f.is_file() and "__pycache__" not in f.parts)
    hits = _hashed_leak_scan(files, ORIGINAL_PATTERN_SHA256)
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "ns"
        d.mkdir()
        planted = d / "planted.md"
        planted.write_text("a bound of 0.123456789 here, 7.25 there\n")
        import c11rd_compare as CM
        decoy = frozenset(hashlib.sha256(x.encode()).hexdigest() for x in CM.value_patterns("0.123456789"))
        caught = _hashed_leak_scan_plain([planted], decoy)
        missed = _hashed_leak_scan_plain([planted], frozenset(hashlib.sha256(x.encode()).hexdigest()
                                                              for x in CM.value_patterns("0.987654321")))
    return {"pass": not hits and caught == ["0.123456789"] and not missed and len(ORIGINAL_PATTERN_SHA256) == 17,
            "files_scanned": len(files), "hits": hits, "negative_control_caught": caught,
            "negative_control_non_match": missed}


def _hashed_leak_scan_plain(files: list, hashes: frozenset) -> list:
    import hashlib
    import c11rd_compare as CM
    out = []
    for f in files:
        for tok in CM.NUMERIC_TOKEN.findall(f.read_text()):
            if any(hashlib.sha256(x.encode()).hexdigest() in hashes for x in CM.token_prefixes(tok)):
                out.append(tok)
    return out


def _c11r_schema():
    import importlib.util
    rel = MD.C11R_SCHEMA_REL
    if MD.git_blob(MD.REPO / rel) != "0526426cf15647bcc44bc5ab901df0ba408ddef6":
        raise MD.ModelError("c11r_schema.py is not the frozen blob")
    spec = importlib.util.spec_from_file_location("c11r_schema_frozen", MD.REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def v19_statement_semantics_equal_c11r_schema():
    """C11RD's statement strings and the comparator's rule constants are EQUAL to C11R's frozen schema
    (blob-bound c11r_schema.py, which imports only fractions)."""
    import c11rd_compare as CM
    S = _c11r_schema()
    r = MD.ROUTE
    checks = {
        "state_set": MD.STATE_SET_R == S.STATE_SET_R,
        "quantity": all(MD.QUANTITY[k] == S.QUANTITY[k] for k in ("D1", "D2")),
        "proposition": all(MD.PROPOSITION[k] == S.PROPOSITION[k] for k in ("D1", "D2")),
        "direction": all(S.DIRECTION[k] == "UPPER_BOUND" for k in ("D1", "D2")),
        "route_reserved": r in S.INDEPENDENT_ROUTES and {"D1", "D2"} <= S.ROUTE_CAN_PRODUCE[r],
        "dependencies": set(MD.DEPENDENCIES) == S.ROUTE_REQUIRED_DEPENDENCIES[r],
        "exact_fields": CM.EXACT_FIELDS == S.EXACT_FIELDS and CM.STATEMENT_FIELDS == S.STATEMENT_FIELDS,
        "convention": CM.CONVENTION == S.CONVENTION,
        "valid_aggregation": CM.VALID_AGGREGATION == S.VALID_AGGREGATION,
        "independent_routes": CM.INDEPENDENT_ROUTES == S.INDEPENDENT_ROUTES,
        "forbidden_producers": CM.FORBIDDEN_PRODUCERS == S.FORBIDDEN_PRODUCERS,
        "route_rules": CM.ROUTE_CAN_PRODUCE[r] == S.ROUTE_CAN_PRODUCE[r] and
        CM.ROUTE_REQUIRED_DEPENDENCIES[r] == S.ROUTE_REQUIRED_DEPENDENCIES[r],
        "six": CM.SIX == S.SIX_CONSTANTS,
    }
    return {"pass": all(checks.values()), "checks": checks}


def _statement_battery():
    import copy
    import c11rd_runs as RN
    lo, hi = MD.cell_block()
    premise = {"C_T": F(3429, 500), "tau": F(3429, 500), "source": {"file": "x"}}
    honest = RN.statements(lo, hi, premise, {"sub_blocks": 4})
    mid = str((lo + hi) / 2)
    cases = []
    for k in ("D1", "D2"):
        h = honest[k]

        def mut(label, fn, expect):
            s = copy.deepcopy(h)
            fn(s)
            cases.append((label, k, s, expect))
        mut("honest", lambda s: None, "EQUIVALENT")
        mut("scalar_drift", lambda s: s.__setitem__("drift_domain", [mid, mid]), "WEAKER")
        mut("narrower_block", lambda s: s.__setitem__("drift_domain", [mid, str(hi)]), "WEAKER")
        mut("wider_block", lambda s: s.__setitem__("drift_domain", [str(lo - 1), str(hi)]), "STRONGER")
        mut("shifted_block", lambda s: s.__setitem__("drift_domain", [str(lo + F(1, 100)), str(hi + F(1, 100))]),
            "NOT_COMPARABLE")
        mut("full_kernel", lambda s: s.update(kernel="K_e", convention="full"), "NOT_EQUIVALENT")
        mut("kernel_convention_mismatch", lambda s: s.update(kernel="K_e"), "INVALID")
        mut("lower_direction", lambda s: s.update(direction="LOWER_BOUND"), "INVALID")
        mut("min_aggregation", lambda s: s["aggregation"].update(method="min_over_sub_blocks"), "INVALID")
        mut("original_premises", lambda s: s.__setitem__("dependencies", ["C_T", "tau"]), "INVALID")
        mut("missing_tau", lambda s: s.__setitem__("dependencies", ["C_T_independent"]), "INVALID")
        mut("forbidden_producer", lambda s: s["producer"].update(module="taboo_certify.py"), "INVALID")
        mut("no_file_hash", lambda s: s["producer"].update(file_sha256=""), "INVALID")
        mut("other_state_set", lambda s: s.update(state_set="R minus the atom"), "NOT_EQUIVALENT")
        mut("other_quantity", lambda s: s.update(quantity="|d(atom)|"), "NOT_EQUIVALENT")
        mut("original_route", lambda s: s["producer"].update(route="original_certify_cell"), "INVALID")
    return cases


def v20_comparator_fidelity():
    """(a) C11RD's compare_statement returns, on a battery of honest and mutated statements, EXACTLY
    what C11R's own frozen c11r_equiv.compare returns (run in an isolated subprocess, since importing
    it installs C11R's open-guard), and the expected class; (b) classify_numeric agrees with the rule
    C11R froze in its statement table, evaluated literally from the table's strings, on a grid that
    includes every boundary."""
    import subprocess
    import c11rd_compare as CM
    table = MD._load_bound(MD.STATEMENT_TABLE_REL, MD.STATEMENT_TABLE_BLOB)
    cases = _statement_battery()
    ours = []
    for label, k, s, expect in cases:
        r = CM.compare_statement(table["original_statements"][k], s)
        ours.append({"label": label, "k": k, "status": r["STATUS"], "expect": expect,
                     "violation": bool(r.get("independence_violation"))})
    payload = json.dumps([[k, s] for _, k, s, _ in cases])
    code = ("import sys, json; sys.path.insert(0, %r)\n" % str(MD.REPO / MD.C11R_NS / "code")
            + "import c11r_equiv as EQ\n"
            + "tab = json.load(open(%r))\n" % str(MD.REPO / MD.STATEMENT_TABLE_REL)
            + "cases = json.loads(sys.stdin.read())\n"
            + "print(json.dumps([[EQ.compare(EQ.original_statement(tab, k), s)['STATUS'], "
              "bool(EQ.compare(EQ.original_statement(tab, k), s).get('independence_violation'))] for k, s in cases]))\n")
    out = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code], input=payload, capture_output=True,
                         text=True, timeout=300)
    theirs = json.loads(out.stdout) if out.returncode == 0 else None
    agree = theirs is not None and all(o["status"] == th[0] and o["violation"] == th[1]
                                       for o, th in zip(ours, theirs))
    expected = all(o["status"] == o["expect"] for o in ours)
    # (b) the numeric rule, literally from the frozen table
    rule = MD.comparison_rule(table)

    def literal(direction, indep, orig):
        env = {"independent": indep, "original": orig}
        hits = [cls for cls, cond in rule[direction].items() if eval(cond, {"__builtins__": {}}, env)]
        return hits
    grid_ok, grid = True, 0
    for orig in (F(1, 3), F(5, 2), F(7)):
        for mult in (F(0), F(1, 4), F(1, 2), F(1, 2) + F(1, 10 ** 9), F(99, 100), F(1), F(1) + F(1, 10 ** 9),
                     F(3, 2), F(2) - F(1, 10 ** 9), F(2), F(2) + F(1, 10 ** 9), F(3)):
            for d in ("UPPER_BOUND", "LOWER_BOUND"):
                lit = literal(d, orig * mult, orig)
                grid += 1
                if lit != [CM.classify_numeric(d, orig * mult, orig)]:
                    grid_ok = False
    # (c) the N9 precedence
    prec = {"all_agree": CM.n9_verdict({k: "AGREES" for k in CM.SIX}, []) == "N9_CLOSED",
            "one_insufficient": CM.n9_verdict(dict({k: "STRONGER" for k in CM.SIX}, D2="INSUFFICIENT"), [])
            == "AGREEMENT_INSUFFICIENT",
            "invalid_beats_insufficient": CM.n9_verdict(dict({k: "AGREES" for k in CM.SIX}, D1="INVALID",
                                                             D2="INSUFFICIENT"), []) == "EXECUTION_INVALID",
            "disagree_beats_invalid": CM.n9_verdict(dict({k: "AGREES" for k in CM.SIX}, D1="DISAGREES",
                                                         D2="INVALID"), []) == "SCIENTIFIC_DISAGREEMENT",
            "violation_first": CM.n9_verdict({k: "AGREES" for k in CM.SIX}, ["D1"]) == "INDEPENDENCE_VIOLATION"}
    return {"pass": agree and expected and grid_ok and all(prec.values()) and len(ours) == 32,
            "battery": ours, "c11r_equiv_returncode": out.returncode, "c11r_equiv_agrees": agree,
            "expected_classes": expected, "numeric_grid_points": grid, "numeric_rule_literal": grid_ok,
            "precedence": prec, "stderr": out.stderr[-500:]}


def v21_lifecycle_refusals():
    """The runner's and comparator's guards refuse (no science is run): bad grants, a second lock, a
    rehearsal output inside the namespace, a tampered runs artifact in the exact recomputation, a
    non-tiling sub-block set, and the leak detector on a planted original-shaped token."""
    import copy
    import tempfile
    import c11rd_runs as RN
    import c11rd_compare as CM
    lo, hi = MD.cell_block()
    fz = {"code_sha256": {"code/c11rd_runs.py": "0" * 64}, "target": {"cell": 306, "drift_block": [str(lo), str(hi)]}}
    good = {"decision": "ALLOW", "campaign": "C11RD", "code_sha256": fz["code_sha256"],
            "target": {"cell": 306, "e_lo": str(lo), "e_hi": str(hi)}, "max_executions": 1,
            "host": {"platform": sys.platform, "python": sys.version.split()[0]},
            "freeze_commit": MD.C11R_FINAL_HEAD}
    out = {}
    with tempfile.TemporaryDirectory() as td:
        def grant_refused(g):
            gp = pathlib.Path(td) / "g.json"
            gp.write_text(json.dumps(g))
            try:
                RN.verify_grant(fz, gp)
                return False
            except SystemExit as exc:
                return "REFUSE R2" in str(exc)
        out["grant_deny"] = grant_refused(dict(good, decision="DENY"))
        out["grant_two_executions"] = grant_refused(dict(good, max_executions=2))
        out["grant_other_cell"] = grant_refused(dict(good, target={"cell": 307, "e_lo": str(lo), "e_hi": str(hi)}))
        out["grant_other_code"] = grant_refused(dict(good, code_sha256={"code/c11rd_runs.py": "1" * 64}))
        out["grant_bogus_freeze_commit"] = grant_refused(dict(good, freeze_commit="f" * 40))
        out["grant_other_host"] = grant_refused(dict(good, host={"platform": "linux", "python": "3.12.0"}))
        out["grant_without_freeze_file"] = grant_refused(good)      # C11R's final HEAD has no C11RD freeze
        # the lock is exclusive and permanent
        real_ns = RN.NS
        try:
            RN.NS = pathlib.Path(td) / "ns"
            RN.NS.mkdir()
            RN.take_lock({"t": 1})                     # creates evidence/runs itself
            out["lock_creates_its_directory"] = (RN.NS / RN.LOCK_REL).exists()
            try:
                RN.take_lock({"t": 2})
                out["second_lock_refused"] = False
            except SystemExit as exc:
                out["second_lock_refused"] = "REFUSE R4" in str(exc)
            (RN.NS / RN.LOCK_REL).chmod(0o644)
            (RN.NS / RN.LOCK_REL).unlink()
            (RN.NS / RN.RUNS_REL).write_text("{}")
            try:
                RN.take_lock({"t": 3})
                out["runs_artifact_blocks_lock"] = False
            except SystemExit as exc:
                out["runs_artifact_blocks_lock"] = "REFUSE R4" in str(exc)
        finally:
            RN.NS = real_ns
    # R1: a changed C11RD file or a changed C7 primitive is refused
    fzp = HERE.parent / "protocol" / "C11RD_FREEZE.json"
    if fzp.exists():
        real = json.loads(fzp.read_text())
        try:
            RN.verify_code(real)
            out["r1_passes_on_frozen_tree"] = True
        except SystemExit:
            out["r1_passes_on_frozen_tree"] = False
        for label, mut in (("r1_code_hash_refused", lambda f: f["code_sha256"].__setitem__("code/c11rd_tm.py", "0" * 64)),
                           ("r1_c7_hash_refused", lambda f: f["input_bindings"]["c7_gaussian"].__setitem__("sha256", "0" * 64))):
            f = copy.deepcopy(real)
            mut(f)
            try:
                RN.verify_code(f)
                out[label] = False
            except SystemExit as exc:
                out[label] = "REFUSE R1" in str(exc)
        try:
            CM.verify_own_code(real)
            out["comparator_self_check_passes"] = True
        except CM.Refusal:
            out["comparator_self_check_passes"] = False
        f = copy.deepcopy(real)
        f["code_sha256"]["code/c11rd_compare.py"] = "0" * 64
        try:
            CM.verify_own_code(f)
            out["comparator_self_check_refuses_changed_comparator"] = False
        except CM.Refusal as exc:
            out["comparator_self_check_refuses_changed_comparator"] = "c11rd_compare" in str(exc)
    else:
        out["r1_freeze_present"] = False
    # a runs artifact or lock EVER committed (then deleted) refuses a new lock
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        g = lambda *a: subprocess.run(["git", "-C", td, *a], capture_output=True, text=True)
        g("init", "-q")
        g("config", "user.email", "t@example.invalid")
        g("config", "user.name", "t")
        (pathlib.Path(td) / "README").write_text("x\n")
        g("add", "README")
        g("commit", "-qm", "base")
        out["history_clean_repo_empty"] = RN.ever_committed([f"{MD.NS_REL}/{RN.RUNS_REL}"], repo=td) == []
        f = pathlib.Path(td) / MD.NS_REL / RN.RUNS_REL
        f.parent.mkdir(parents=True)
        f.write_text("{}\n")
        g("add", "-A")
        g("commit", "-qm", "a run")
        g("rm", "-q", str(f))
        g("commit", "-qm", "delete it")
        out["history_deleted_run_found"] = len(RN.ever_committed([f"{MD.NS_REL}/{RN.RUNS_REL}"], repo=td)) == 2
    out["history_real_repo_has_no_run"] = RN.ever_committed([f"{MD.NS_REL}/{RN.RUNS_REL}",
                                                             f"{MD.NS_REL}/{RN.LOCK_REL}"]) == []
    # a rehearsal may not write inside the namespace (refused before any science: the freeze is absent)
    try:
        RN.main(["--mode", "nontarget", "--out", str(HERE / "x.json")])
        out["rehearsal_inside_ns_refused"] = False
    except SystemExit as exc:
        out["rehearsal_inside_ns_refused"] = "REFUSE" in str(exc)
    # exact recomputation: a synthetic two-sub-block runs record (synthetic numbers only)
    kap = MD.kernel_norms()
    prem = {"C_T": F(3429, 500), "tau": F(3429, 500)}
    mid = (lo + hi) / 2
    subs = []
    for (a, b), at, lam in (((lo, mid), ["1/2", "1/10", "-1/5", "3/10"], ["1/10000", "1/5000", "1/1000"]),
                            ((mid, hi), ["1/2", "1/9", "-1/4", "1/3"], ["1/20000", "1/4000", "1/900"])):
        de = (b - a) / 2
        A = [F(x) for x in at]
        pr = CE.propagate([F(x) for x in lam], prem["C_T"], prem["tau"], kap)
        subs.append({"e_lo": str(a), "e_hi": str(b), "atom_candidate_values": at, "lam": lam,
                     "D1": str(abs(A[1]) + abs(A[2]) * de + abs(A[3]) / 2 * de ** 2 + pr["err_D1"]),
                     "D2": str(abs(A[2]) + abs(A[3]) * de + pr["err_D2"]),
                     "candidates": {f"D{j}": {"0": {"0,0": at[j]}} for j in range(4)}})
    runs = {"execution": {"sub_blocks": subs},
            "targets": {k: {"value": str(max(F(s[k]) for s in subs))} for k in ("D1", "D2")}}
    out["recompute_honest_clean"] = CM.recompute(runs, prem, kap, (lo, hi)) == []
    t1 = copy.deepcopy(runs)
    t1["execution"]["sub_blocks"][1]["lam"][2] = "1/100000"
    out["recompute_tampered_lam_caught"] = bool(CM.recompute(t1, prem, kap, (lo, hi)))
    t2 = copy.deepcopy(runs)
    t2["targets"]["D2"]["value"] = subs[0]["D2"] if F(subs[0]["D2"]) < F(subs[1]["D2"]) else subs[1]["D2"]
    out["recompute_min_instead_of_max_caught"] = bool(CM.recompute(t2, prem, kap, (lo, hi)))
    t3 = copy.deepcopy(runs)
    t3["execution"]["sub_blocks"][1]["e_hi"] = str(hi - F(1, 10 ** 6))
    out["recompute_gap_caught"] = bool(CM.recompute(t3, prem, kap, (lo, hi)))
    t4 = copy.deepcopy(runs)
    t4["execution"]["sub_blocks"][0]["candidates"]["D1"]["0"]["0,0"] = "0"
    out["recompute_atom_not_candidate_caught"] = bool(CM.recompute(t4, prem, kap, (lo, hi)))
    out["leak_detector_catches_planted"] = CM.leak_hits({"f.md": "value 0.12345 x"}, {"D1": "0.123456789"}) == {"f.md": ["D1"]}
    out["leak_detector_token_boundary"] = CM.leak_hits({"f.md": "value 10.12345 x"}, {"D1": "0.123456789"}) == {}
    return {"pass": all(out.values()), "checks": out}


def v22_cover_invariants():
    """Soundness invariants of the cover: (a) the initial boxes tile R exactly (area of bands 0-3 in
    (s, theta) and total length of band 4); (b) every box -- and every descendant under split -- keeps
    the sub-block's full drift interval, so all residuals are of ONE candidate function with ONE
    Taylor centre; (c) a split partitions its parent."""
    splits = {"s": 4, "theta": [4, 8, 12, 16], "s4": 4}
    boxes = CE.initial_boxes(NTB[0], NTB[1], splits, 4)
    area = sum((F(b.s[1]) - F(b.s[0])) * (F(b.theta[1]) - F(b.theta[0])) for b in boxes if b.band < 4)
    length = sum(F(b.s[1]) - F(b.s[0]) for b in boxes if b.band == 4)
    per_band = {k: sum((F(b.s[1]) - F(b.s[0])) * (F(b.theta[1]) - F(b.theta[0])) for b in boxes if b.band == k)
                for k in range(4)}
    tiled = area == 8 and length == 2 and all(v == 2 for v in per_band.values())
    same_e = all(b.e == NTB for b in boxes)
    kids_ok, part_ok = True, True
    for b in boxes[:: 17]:
        kids = b.split()
        kids_ok &= all(k.e == b.e and k.ec == b.ec and k.de == b.de for k in kids)
        if b.band < 4:
            part_ok &= sum((F(k.s[1]) - F(k.s[0])) * (F(k.theta[1]) - F(k.theta[0])) for k in kids) == \
                (F(b.s[1]) - F(b.s[0])) * (F(b.theta[1]) - F(b.theta[0]))
        else:
            part_ok &= sum(F(k.s[1]) - F(k.s[0]) for k in kids) == F(b.s[1]) - F(b.s[0])
    return {"pass": tiled and same_e and kids_ok and part_ok, "initial_boxes": len(boxes),
            "tiles_R": tiled, "one_drift_interval": same_e, "split_keeps_e": kids_ok, "split_partitions": part_ok}


def v23_preimport_barrier():
    """The runner's and comparator's pre-import barrier: on a byte-copy of the code directory (and a
    C7 directory holding only c7_gaussian.py) the runner passes the barrier; planting a
    standard-library-named file or a __pycache__ in the code directory, a .pyc or a stdlib-named
    file in C7's directory, or starting without -I/-S/-B, is refused BEFORE any other import."""
    import shutil
    import subprocess
    import tempfile
    c7 = HERE.parents[1] / "p5y_k5_tail_c7_e2_lambda309" / "code" / "c7_gaussian.py"
    out = {}

    def run(setup, flags=("-I", "-S", "-B"), script="c11rd_runs.py", args=("--mode", "nontarget", "--out", "INSIDE")):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td) / "closure_proofs"
            code = root / "p5y_k5_tail_c11rd_d1d2_extension" / "code"
            c7d = root / "p5y_k5_tail_c7_e2_lambda309" / "code"
            code.mkdir(parents=True)
            c7d.mkdir(parents=True)
            for f in HERE.glob("c11rd_*.py"):
                shutil.copyfile(f, code / f.name)
            shutil.copyfile(c7, c7d / "c7_gaussian.py")
            setup(code, c7d)
            a = [str(code / "x.json") if x == "INSIDE" else x for x in args]
            r = subprocess.run([sys.executable, *flags, str(code / script), *a], capture_output=True, text=True,
                               timeout=300, cwd=td)
            return r.returncode, r.stderr + r.stdout
    rc, msg = run(lambda c, s: None)
    out["honest_copy_passes_barrier"] = "REFUSE R0" not in msg and "never writes inside" in msg
    rc, msg = run(lambda c, s: (c / "fractions.py").write_text("raise SystemExit('SHADOW RAN')\n"))
    out["stdlib_shadow_in_code_refused"] = "REFUSE R0" in msg and "SHADOW RAN" not in msg
    rc, msg = run(lambda c, s: (c / "__pycache__").mkdir())
    out["pycache_in_code_refused"] = "REFUSE R0" in msg
    rc, msg = run(lambda c, s: (s / "c7_gaussian.cpython-314.pyc").write_bytes(b"\0"))
    out["pyc_in_c7_refused"] = "REFUSE R0" in msg
    rc, msg = run(lambda c, s: (s / "json.py").write_text("raise SystemExit('SHADOW RAN')\n"))
    out["stdlib_shadow_in_c7_refused"] = "REFUSE R0" in msg and "SHADOW RAN" not in msg
    rc, msg = run(lambda c, s: None, flags=("-B",))
    out["non_isolated_interpreter_refused"] = "REFUSE R0" in msg
    rc, msg = run(lambda c, s: (c / "notes.txt").write_text("x"), script="c11rd_compare.py",
                  args=("--seal-commit", "0" * 40, "--execution-review-commit", "0" * 40))
    out["comparator_barrier_refuses_extra_file"] = "REFUSE R0" in msg
    frozen = set(json.loads((HERE.parent / "protocol" / "C11RD_FREEZE.json").read_text())["code_sha256"]) \
        if (HERE.parent / "protocol" / "C11RD_FREEZE.json").exists() else None
    import c11rd_runs as RN
    import types
    import importlib.machinery as IM
    try:                                   # the honest process: every loaded module passes
        RN.verify_loaded_modules()
        out["loaded_module_check_passes_honest_process"] = True
    except SystemExit:
        out["loaded_module_check_passes_honest_process"] = False
    for label, origin, cached in (("unfrozen_module_in_code_dir", str(HERE / "evil.py"), None),
                                  ("cached_bytecode_of_frozen_module", str(HERE / "c11rd_tm.py"), str(HERE))):
        fake = types.ModuleType("c11rd_fake")
        fake.__spec__ = IM.ModuleSpec("c11rd_fake", None, origin=origin)
        fake.__spec__.cached = cached      # an existing path stands for a bytecode cache on disk
        sys.modules["c11rd_fake"] = fake
        try:
            RN.verify_loaded_modules()
            out[label + "_refused"] = False
        except SystemExit as exc:
            out[label + "_refused"] = "REFUSE R0" in str(exc)
        finally:
            del sys.modules["c11rd_fake"]
    out["barrier_file_set_equals_code_dir"] = set(RN.CODE_FILES) == {f.name for f in HERE.glob("c11rd_*.py")} and \
        (frozen is None or {f"code/{n}" for n in RN.CODE_FILES} == frozen)
    return {"pass": all(out.values()), "checks": out}


TESTS = [v01_gaussian_moments, v02_kernel_of_one, v03_vs_c11_kernel, v04_finite_difference,
         v05_scalar_collapse, v06_block_uniform, v07_atom_distinction, v08_full_kernel_negative_control,
         v09_premise, v10_zero_cases, v11_symmetry, v12_known_signs, v13_kinks, v14_tiny_drift,
         v15_invalid_bounds, v16_independence, v17_no_embedded_magnitudes,
         v18_no_original_values_anywhere, v19_statement_semantics_equal_c11r_schema,
         v20_comparator_fidelity, v21_lifecycle_refusals, v22_cover_invariants,
         v23_preimport_barrier]


def run_all() -> dict:
    out = {}
    for t in TESTS:
        t0 = time.time()
        try:
            r = t()
        except Exception as exc:                          # a crash is a failure, recorded
            r = {"pass": False, "error": f"{type(exc).__name__}: {exc}"}
        r["seconds"] = round(time.time() - t0, 1)
        out[t.__name__] = r
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {t.__name__}  ({r['seconds']}s)", flush=True)
    return {"tests": out, "passed": sum(1 for v in out.values() if v["pass"]), "total": len(out),
            "VALIDATION_CLASS": "PASS" if all(v["pass"] for v in out.values()) else "FAIL",
            "drifts_used": ["0", "1", "5/2", "C11R NT block [5/2, 5/2 + 108337/1250000]"],
            "target_values_used": False}


if __name__ == "__main__":
    res = run_all()
    if len(sys.argv) == 3 and sys.argv[1] == "--out":
        pathlib.Path(sys.argv[2]).write_text(json.dumps(res, indent=1, default=str, sort_keys=True) + "\n")
    print(f"\nVALIDATION_CLASS = {res['VALIDATION_CLASS']} ({res['passed']}/{res['total']})")
