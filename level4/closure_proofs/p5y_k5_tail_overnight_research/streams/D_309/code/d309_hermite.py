"""Hermite/score closed form for the CUSUM kernel derivatives K_i, and a certified composite-sup bound.
NON-TARGET DRIFTS ONLY (e in {0, 1/4, 1/2, 1, 3}); every drift touched is passed through ov_quarantine.guard_drift.

Frozen model (graph C section 5.1, re-derived, nothing imported from a historical consumer): state (p, m), K = 1/2,
C = H + K = 11/2, increment z with z + e ~ N(0, 1), next state (max(0, p + z - K), max(0, m - z - K)), alarm-free window
z in [m - C, C - p].  Because e enters only through the density phi(z + e) and
    d^i/de^i phi(z + e) = (-1)^i He_i(z + e) phi(z + e),
the i-th drift derivative of the kernel is
    (K_i w)(p, m) = int_{m-C}^{C-p} w(n(x, z)) (-1)^i He_i(z + e) phi(z + e) dz          (score form: He_i(S), S = -(z+e)).
For a bivariate polynomial w, n(x, z) is affine in z on each piece between the kinks z = K - p and z = m - K, so K_i w is
an exact finite combination of Gaussian moments M_j(A, B) = int_A^B u^j phi(u) du (rigorous rational phi/Phi from the
allowed pure library c7_gaussian).

Checks (declared set DECLARED_RULE, fixed before the first run):
  H1  closed form (this module) vs the INDEPENDENT C11 implementation of K_e (c11_certifier.kernel_apply, allowed pure
      library): i = 0 directly; i = 1, 2, 3 by central finite differences in e with RIGOROUS truncation bounds
      h^2/6, h^2/12, 0.2834 h^2 times sqrt((i+2)!) * sup_[0,5]^2 |w|  (E|He_j(Y)| <= sqrt(j!)).
  H1-NC  planted defects that must be detected by H1: (a) the Hermite sign (-1)^i dropped; (b) the kinks ignored.
  H2  DIAGNOSTIC (grid, not certified): composite |3 K1 wH + 3 K2 wD + K3 wF| vs the ideal surrogate
      3 k1 |wH| + 3 k2 |wD| + k3 |wF| with k_i the TRUE operator norm at that drift (rigorous lower end) and |w| a grid
      lower bound -- i.e. the surrogate is taken at its smallest possible value, so the ratio is conservative.
  H3  CERTIFIED box-cover upper bound of sup_X |3 K1 wH + 3 K2 wD + K3 wF| for declared triples at declared drifts,
      checked against the grid lower bound (soundness) with a planted-too-small negative control.
Writes validation/D309_HERMITE_NONTARGET.json.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_core as D  # noqa: E402

Q = D.Q
CLOSURE = D.NS.parent
sys.path.insert(0, str(CLOSURE / "p5y_k5_tail_c7_e2_lambda309" / "code"))
sys.path.insert(0, str(CLOSURE / "p5y_k5_tail_c11_n9_independent_certifier" / "code"))
import c7_gaussian as G  # noqa: E402  allowed pure library (PREAMBLE Q3)
import c11_certifier as C11  # noqa: E402  allowed pure library (PREAMBLE Q3); used ONLY as the independent K_e

KK = F(1, 2)
CC = F(11, 2)
HE = [[F(1)], [F(0), F(1)], [F(-1), F(0), F(1)], [F(0), F(-3), F(0), F(1)],
      [F(3), F(0), F(-6), F(0), F(1)], [F(0), F(15), F(0), F(-10), F(0), F(1)]]

DECLARED_RULE = (
    "Drifts e in {0, 1/4, 1/2, 1, 3} (declared validation drifts; guard_drift on [e-2h, e+2h], h = 1/10000). States: "
    "(0,0),(0,1),(1,0),(0,5/2),(5/2,0),(1/4,1/2),(1,1),(2,1),(1,3),(0,9/2),(9/2,0),(3/2,5/2). Test polynomials: "
    "w_const = 1; w_lin = p - 2m + 1; w_quad = p^2 + p m - m^2/2 + 3; w_cub = seeded random cubic (seed 11); "
    "w_bump = y (1 - (y/(5/2))^2)^4, y = m - 5/2. H1 on every (state, w, i in {0,1,2,3}, e). H2 triples "
    "(wF, wD, wH) in {(w_quad, w_lin, w_const), (w_cub, w_quad, w_lin), (w_bump, w_bump, w_bump), (w_cub, w_cub, w_cub)} on "
    "the grid {p, m in (0, 1/2, ..., 5)} intersected with the reachable closure. H3 on triples 1 and 3 at e in {1/4, 3}, "
    "box cover depth 4, z-panels of width 1/16. Fixed before the first run.")

# Performance only, value-identical: c7_gaussian recomputes sqrt(2 pi) (Machin series + isqrt) inside every phi/Phi
# call.  It is memoised in-process here, and phi/Phi are memoised by argument; C11 (same module object) benefits too.
# _memo_selftest() re-checks bit-identity of the enclosures against a fresh, unpatched evaluation.
_REF = (G.Phi(F(3, 7)), G.phi(F(-5, 3)))
_S2P = G.sqrt_two_pi()
_Phi_raw, _phi_raw = G.Phi, G.phi
_phi_cache: dict = {}
_Phi_cache: dict = {}


def phi(t: F) -> G.Iv:
    t = F(t)
    if t not in _phi_cache:
        _phi_cache[t] = _phi_raw(t)
    return _phi_cache[t]


def Phi(t: F) -> G.Iv:
    t = F(t)
    if t not in _Phi_cache:
        _Phi_cache[t] = _Phi_raw(t)
    return _Phi_cache[t]


G.sqrt_two_pi = lambda: _S2P  # noqa: E731
G.Phi, G.phi = Phi, phi


def _memo_selftest() -> bool:
    a, b = G.Phi(F(3, 7)), G.phi(F(-5, 3))
    return (a.lo, a.hi, b.lo, b.hi) == (_REF[0].lo, _REF[0].hi, _REF[1].lo, _REF[1].hi)


def moments(A: F, B: F, jmax: int) -> list:
    pa, pb = phi(A), phi(B)
    out = [Phi(B) - Phi(A)]
    if jmax >= 1:
        out.append(pa - pb)
    for j in range(2, jmax + 1):
        out.append(G.Iv(j - 1) * out[j - 2] + G.Iv(A ** (j - 1)) * pa - G.Iv(B ** (j - 1)) * pb)
    return out


def lin_pow(c0: F, c1: F, n: int) -> list:
    return [F(math.comb(n, k)) * c0 ** (n - k) * c1 ** k for k in range(n + 1)]


def compose_piece(w: dict, p: F, m: F, p_on: bool, m_on: bool) -> list:
    """w(p', m') as a polynomial in z on one piece (p' = p - K + z or 0, m' = m - K - z or 0)."""
    out = [F(0)]
    for (i, j), c in w.items():
        if (i and not p_on) or (j and not m_on):
            continue
        a = lin_pow(p - KK, F(1), i) if i else [F(1)]
        b = lin_pow(m - KK, F(-1), j) if j else [F(1)]
        out = D.p_add(out, D.p_scale(D.p_mul(a, b), c))
    return out


def Ki_apply(w: dict, p: F, m: F, e: F, i: int, *, drop_sign: bool = False, ignore_kinks: bool = False) -> G.Iv:
    """(K_i w)(p, m) at drift e, exact up to the rigorous Gaussian enclosure."""
    Q.guard_drift(e)
    ell, up = m - CC, CC - p
    cuts = {ell, up}
    if not ignore_kinks:
        cuts |= {z for z in (KK - p, m - KK) if ell < z < up}
    cuts = sorted(cuts)
    he_z = D.p_taylor(HE[i], e)  # He_i(z + e) as a polynomial in z
    sgn = F(1) if (drop_sign or i % 2 == 0) else F(-1)
    tot = G.Iv(0)
    for lo, hi in zip(cuts, cuts[1:]):
        mid = (lo + hi) / 2
        p_on = True if ignore_kinks else (p + mid - KK) > 0
        m_on = True if ignore_kinks else (m - mid - KK) > 0
        P = D.p_mul(compose_piece(w, p, m, p_on, m_on), D.p_scale(he_z, sgn))
        Pu = D.p_taylor(P, -e)  # as a polynomial in u = z + e
        if all(c == 0 for c in Pu):
            continue
        Ms = moments(lo + e, hi + e, len(Pu) - 1)
        for k, c in enumerate(Pu):
            if c:
                tot = tot + G.Iv(c) * Ms[k]
    return tot


def w_sup_crude(w: dict) -> F:
    return sum((abs(c) * F(5) ** (i + j) for (i, j), c in w.items()), F(0))


def poly_eval(w: dict, p: F, m: F) -> F:
    return sum((c * p ** i * m ** j for (i, j), c in w.items()), F(0))


def in_reach(p: F, m: F) -> bool:
    return 0 <= p <= 5 and 0 <= m <= 5 and (p + m <= 4 or p == 0 or m == 0)


def test_polys() -> dict:
    rng = random.Random(11)
    cub = {}
    for i in range(4):
        for j in range(4 - i):
            cub[(i, j)] = F(rng.randint(-20, 20), 40) / F(5) ** (i + j)
    y = {(0, 1): F(1), (0, 0): F(-5, 2)}  # y = m - 5/2
    L2 = F(4, 25)

    def pm(a, b):
        out = {}
        for (i1, j1), c1 in a.items():
            for (i2, j2), c2 in b.items():
                out[(i1 + i2, j1 + j2)] = out.get((i1 + i2, j1 + j2), F(0)) + c1 * c2
        return out
    one_minus = {(0, 0): F(1)}
    y2 = pm(y, y)
    for k, c in y2.items():
        one_minus[k] = one_minus.get(k, F(0)) - L2 * c
    bump = dict(y)
    for _ in range(4):
        bump = pm(bump, one_minus)
    return {"w_const": {(0, 0): F(1)}, "w_lin": {(1, 0): F(1), (0, 1): F(-2), (0, 0): F(1)},
            "w_quad": {(2, 0): F(1), (1, 1): F(1), (0, 2): F(-1, 2), (0, 0): F(3)},
            "w_cub": cub, "w_bump": {k: v for k, v in bump.items() if v != 0}}


def fd_check(w: dict, p: F, m: F, e: F, i: int, h: F) -> dict:
    Q.guard_drift(e - 2 * h, e + 2 * h)
    ka = lambda ee: C11.kernel_apply(w, p, m, ee)  # noqa: E731  independent K_e (C11)
    if i == 0:
        fd, trunc = ka(e), F(0)
    elif i == 1:
        fd = (ka(e + h) - ka(e - h)) / G.Iv(2 * h)
        trunc = h * h / 6 * F(math.isqrt(math.factorial(3)) + 1) * w_sup_crude(w)
    elif i == 2:
        fd = (ka(e + h) - G.Iv(2) * ka(e) + ka(e - h)) / G.Iv(h * h)
        trunc = h * h / 12 * F(math.isqrt(math.factorial(4)) + 1) * w_sup_crude(w)
    else:
        fd = (ka(e + 2 * h) - G.Iv(2) * ka(e + h) + G.Iv(2) * ka(e - h) - ka(e - 2 * h)) / G.Iv(2 * h ** 3)
        trunc = F(2834, 10000) * h * h * F(math.isqrt(math.factorial(5)) + 1) * w_sup_crude(w)
    cf = Ki_apply(w, p, m, e, i)
    gap = max(abs(cf.hi - fd.lo), abs(fd.hi - cf.lo))
    ok = gap <= trunc + (cf.hi - cf.lo) + (fd.hi - fd.lo) + F(1, 10 ** 60)
    nc_sign = Ki_apply(w, p, m, e, i, drop_sign=True)
    nc_kink = Ki_apply(w, p, m, e, i, ignore_kinks=True)
    tol = trunc + (fd.hi - fd.lo) + F(1, 10 ** 50)

    def far(iv):
        return max(abs(iv.hi - fd.lo), abs(fd.hi - iv.lo)) > tol
    return {"ok": bool(ok), "value": float(cf.lo), "gap": float(gap), "trunc_bound": float(trunc),
            "nc_sign_detected": far(nc_sign), "nc_sign_applicable": i % 2 == 1 and abs(cf.lo) > 10 * tol,
            "nc_kink_detected": far(nc_kink)}


def op_norm_true(e: F, i: int) -> G.Iv:
    """k_i(e) = sup_x int_window |He_i(z+e)| phi(z+e) dz = int_{e-C}^{e+C} |He_i(u)| phi(u) du (widest window at the
    atom).  Rigorous: split at the roots of He_i, antiderivative of He_i phi is -He_{i-1} phi."""
    Q.guard_drift(e)
    A, B = e - CC, e + CC
    s3 = G.sqrt_iv(G.Iv(3))
    roots = {1: [G.Iv(0)], 2: [G.Iv(-1), G.Iv(1)], 3: [G.Iv(0) - s3, G.Iv(0), s3]}[i]

    def prim_rational(t: F) -> G.Iv:
        """-He_{i-1}(t) phi(t) at a rational point."""
        return G.Iv(0) - G.Iv(D.p_eval(HE[i - 1], t)) * phi(t)

    def prim_sqrt3() -> G.Iv:
        """-He_2(+-sqrt3) phi(sqrt3) = -2 exp(-3/2)/sqrt(2 pi)  (only i = 3 has the irrational roots +-sqrt3)."""
        assert i == 3
        return G.Iv(0) - G.Iv(2) * (G.exp_neg(F(3, 2)) / G.sqrt_two_pi())
    pts = [(A, prim_rational(A))]
    for r in roots:
        if r.lo == r.hi:
            pts.append((r.lo, prim_rational(r.lo)))
        else:
            pts.append(((r.lo + r.hi) / 2, prim_sqrt3()))
    pts.append((B, prim_rational(B)))
    pts = [pt for pt in pts if A <= pt[0] <= B]
    pts.sort(key=lambda t: t[0])
    tot = G.Iv(0)
    for (a, pa), (b, pb) in zip(pts, pts[1:]):
        d = pb - pa
        lo = min(abs(d.lo), abs(d.hi)) if d.lo * d.hi > 0 else F(0)
        tot = tot + G.Iv(lo, max(abs(d.lo), abs(d.hi)))
    return tot


def box_upper_composite(triple: list, box: tuple, e: F, panel: F) -> G.Iv:
    """Rigorous enclosure of {sum_i c_i (K_i w_i)(x) : x in box} (triple = [(c_i, i, w_i)])."""
    a, b, c, d = box
    zlo, zhi = c - CC, CC - a            # union window
    ilo, ihi = d - CC, CC - b            # window common to every state of the box
    cuts = {zlo, zhi, ilo, ihi}
    k = math.floor(zlo / panel)
    while k * panel < zhi:
        if zlo < k * panel < zhi:
            cuts.add(k * panel)
        k += 1
    cuts = sorted(x for x in cuts if zlo <= x <= zhi)
    tot = G.Iv(0)
    he_z = [D.p_taylor(HE[i], e) for i in range(4)]
    for z0, z1 in zip(cuts, cuts[1:]):
        P = G.Iv(max(F(0), a + z0 - KK), max(F(0), b + z1 - KK))
        M = G.Iv(max(F(0), c - z1 - KK), max(F(0), d - z0 - KK))
        Z = G.Iv(z0, z1)
        q = G.Iv(0)
        for coef, i, w in triple:
            wv = C11.poly_eval_iv(w, P, M)
            hv = G.Iv(0)
            for kk, cz in enumerate(he_z[i]):
                if cz:
                    t = G.Iv(cz)
                    for _ in range(kk):
                        t = t * Z
                    hv = hv + t
            q = q + G.Iv(coef * (-1) ** i) * wv * hv
        mass = Phi(z1 + e) - Phi(z0 + e)
        contrib = q * mass  # for every x in the box: int_P g(x,z) phi(z+e) dz in [q.lo, q.hi] * mass
        if not (ilo <= z0 and z1 <= ihi):  # the panel is inside the window for some states only
            contrib = G.Iv(min(F(0), contrib.lo), max(F(0), contrib.hi))
        tot = tot + contrib
    return tot


def certified_sup(triple: list, e: F, depth: int, panel: F) -> tuple:
    Q.guard_drift(e)
    best = F(0)
    boxes = C11.cover(depth)
    for box in boxes:
        iv = box_upper_composite(triple, box, e, panel)
        best = max(best, abs(iv.lo), abs(iv.hi))
    return best, len(boxes)


def main() -> None:
    t0 = time.time()
    W = test_polys()
    drifts = [F(0), F(1, 4), F(1, 2), F(1), F(3)]
    states = [(F(0), F(0)), (F(0), F(1)), (F(1), F(0)), (F(0), F(5, 2)), (F(5, 2), F(0)), (F(1, 4), F(1, 2)),
              (F(1), F(1)), (F(2), F(1)), (F(1), F(3)), (F(0), F(9, 2)), (F(9, 2), F(0)), (F(3, 2), F(5, 2))]
    assert all(in_reach(p, m) for p, m in states)
    h = F(1, 10000)
    out = {"schema": "OV_D309_HERMITE_NONTARGET/1", "declared_rule": DECLARED_RULE, "H1": [], "H2": [], "H3": [],
           "memoisation_value_identical": _memo_selftest()}
    assert out["memoisation_value_identical"]
    for e in drifts:
        Q.guard_drift(e - 2 * h, e + 2 * h)
        for (p, m) in states:
            for wn, w in W.items():
                for i in range(4):
                    r = fd_check(w, p, m, e, i, h)
                    r.update({"e": str(e), "state": [str(p), str(m)], "w": wn, "i": i})
                    out["H1"].append(r)
    h1 = out["H1"]
    # H2: grid diagnostic of the composite vs the ideal surrogate
    grid = [(F(a, 2), F(b, 2)) for a in range(11) for b in range(11) if in_reach(F(a, 2), F(b, 2))]
    triples = [("w_quad", "w_lin", "w_const"), ("w_cub", "w_quad", "w_lin"), ("w_bump", "w_bump", "w_bump"),
               ("w_cub", "w_cub", "w_cub")]
    for e in drifts:
        k = {i: op_norm_true(e, i) for i in (1, 2, 3)}
        for (fn, dn, hn) in triples:
            wsup = {nm: max(abs(poly_eval(W[nm], p, m)) for p, m in grid) for nm in {fn, dn, hn}}
            sur_lo = 3 * k[1].lo * wsup[hn] + 3 * k[2].lo * wsup[dn] + k[3].lo * wsup[fn]
            comp_max = F(0)
            parts = {1: F(0), 2: F(0), 3: F(0)}
            for (p, m) in grid:
                v1, v2, v3 = Ki_apply(W[hn], p, m, e, 1), Ki_apply(W[dn], p, m, e, 2), Ki_apply(W[fn], p, m, e, 3)
                v = G.Iv(3) * v1 + G.Iv(3) * v2 + v3
                comp_max = max(comp_max, min(abs(v.lo), abs(v.hi)) if v.lo * v.hi > 0 else F(0))
                for ii, vv in ((1, v1), (2, v2), (3, v3)):
                    parts[ii] = max(parts[ii], max(abs(vv.lo), abs(vv.hi)))
            out["H2"].append({
                "e": str(e), "triple": [fn, dn, hn], "k_true": {i: float(k[i].lo) for i in k},
                "grid_points": len(grid), "composite_grid_max": float(comp_max),
                "surrogate_ideal_lower": float(sur_lo),
                "ratio_composite_over_surrogate": float(comp_max / sur_lo),
                "submult_ratio_per_term": {
                    "K1wH": float(parts[1] / (k[1].lo * wsup[hn])), "K2wD": float(parts[2] / (k[2].lo * wsup[dn])),
                    "K3wF": float(parts[3] / (k[3].lo * wsup[fn]))}})
    # H3: certified box-cover sup for two triples at two drifts
    for e in (F(1, 4), F(3)):
        k = {i: op_norm_true(e, i) for i in (1, 2, 3)}
        for (fn, dn, hn) in (triples[0], triples[2]):
            trip = [(F(3), 1, W[hn]), (F(3), 2, W[dn]), (F(1), 3, W[fn])]
            ts = time.time()
            ub, nbox = certified_sup(trip, e, depth=4, panel=F(1, 16))
            glo = F(0)
            for (p, m) in grid:
                v = sum((G.Iv(cf) * Ki_apply(w, p, m, e, i) for cf, i, w in trip), G.Iv(0))
                glo = max(glo, min(abs(v.lo), abs(v.hi)) if v.lo * v.hi > 0 else F(0))
            wsup = {nm: max(abs(poly_eval(W[nm], p, m)) for p, m in grid) for nm in {fn, dn, hn}}
            sur_lo = 3 * k[1].lo * wsup[hn] + 3 * k[2].lo * wsup[dn] + k[3].lo * wsup[fn]
            planted = glo * F(99, 100)
            out["H3"].append({
                "e": str(e), "triple": [fn, dn, hn], "boxes": nbox, "panel": "1/16", "depth": 4,
                "certified_upper": float(ub), "grid_lower": float(glo), "surrogate_ideal_lower": float(sur_lo),
                "sound_upper_ge_grid_lower": bool(ub >= glo),
                "certified_upper_over_surrogate": float(ub / sur_lo),
                "certified_upper_over_grid_lower": float(ub / glo) if glo else None,
                "nc_planted_upper_detected": bool(not (planted >= glo)),
                "wall_s": round(time.time() - ts, 1)})
    out["summary"] = {
        "H1_cases": len(h1), "H1_ok": sum(1 for r in h1 if r["ok"]),
        "H1_max_gap": max(r["gap"] for r in h1),
        "H1_nc_sign_applicable": sum(1 for r in h1 if r["nc_sign_applicable"]),
        "H1_nc_sign_detected_where_applicable": sum(1 for r in h1 if r["nc_sign_applicable"] and r["nc_sign_detected"]),
        "H1_nc_kink_detected": sum(1 for r in h1 if r["nc_kink_detected"]),
        "H1_nc_kink_cases_with_i0_nonconst": sum(1 for r in h1 if r["w"] != "w_const"),
        "H2_ratio_range": [min(r["ratio_composite_over_surrogate"] for r in out["H2"]),
                           max(r["ratio_composite_over_surrogate"] for r in out["H2"])],
        "H3_sound_all": all(r["sound_upper_ge_grid_lower"] for r in out["H3"]),
        "H3_nc_detected": sum(1 for r in out["H3"] if r["nc_planted_upper_detected"]),
        "H3_certified_over_surrogate": [r["certified_upper_over_surrogate"] for r in out["H3"]],
        "wall_s": round(time.time() - t0, 1),
    }
    pth = D.NS / "validation" / "D309_HERMITE_NONTARGET.json"
    pth.write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_execution("streams/D_309/code/d309_hermite.py",
                    "Hermite/score closed form of K_i on the CUSUM kernel vs independent C11 K_e (finite differences), "
                    "grid composite diagnostic, certified box-cover composite sup; drifts {0,1/4,1/2,1,3} only",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
