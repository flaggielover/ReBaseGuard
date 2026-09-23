"""C11R Phase 7 -- manufactured validation. Revision 2.

Identities the implementation cannot satisfy by accident, and soundness checks on the machinery
revision 2 adds. The decisive old check is V6, SCALAR COLLAPSE: with a degenerate drift interval
the block-uniform layer must reproduce C11's scalar certifier BIT FOR BIT, not merely enclose it.

EVERY CHECK RUNS ON THE NON-TARGET BLOCK NT = [5/2, 5/2 + 108337/1250000], or at the non-target
scalar e = 5/2. NT lies above cell 309's upper end, so it belongs to no m=5 cell; it has exactly
cell 306's width. Revision 1 ran V6 at e = 18355/10000, C11's development drift, which lies inside
OPEN cell 307's block. Nothing in these checks depends on the drift value -- they test interval
arithmetic, identities of the kernel, and the soundness of bounds -- so moving them off every open
cell loses nothing and removes all contact with target-block quantities.

V1-V10  revision 1's checks, unchanged in substance, moved to NT.
V11     the selector's factored box margin equals the REVIEWED kernel_box_upper_iv.
V12     the selector is minimal: its choice certifies under the reviewed certifier, and one grid
        step less fails a box constraint.
V13     the new box LOWER bound for Khat_e u lies below the pointwise value.
V14     the D_lo sub-solution route is SOUND: its certified lower bound does not exceed an
        independent float solution of d = h_1 + Khat_e d, and an inflated u fails certification.
V15     the Phi cache changes no bit.
V16     the pointwise coefficient form is conservative (an upper bound on L) for the screen.
"""
from __future__ import annotations

import math
import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_common as C
import c11r_idrift as I

X, G = I.X, I.G
W = F(108337, 1250000)
NT = I.Blk(F(5, 2), F(5, 2) + W)
E_SCALAR = F(5, 2)
STATES = [(F(0), F(0)), (F(3), F(1)), (F(0), F(5)), (F(5), F(0)), (F(2), F(2)),
          (F(23, 5), F(0)), (F(1, 4), F(1, 4))]
WS = {"const9": {(0, 0): F(9)},
      "m_only": {(0, 0): F(99, 10), (0, 1): F(-3, 2)},
      "mixed": {(0, 0): F(4), (1, 0): F(1, 5), (0, 1): F(-1, 2)},
      "deg2": {(0, 0): F(7), (1, 1): F(-1, 3), (0, 2): F(1, 7)}}
results = []


def rec(cid, name, ok, detail):
    results.append({"id": cid, "name": name, "pass": bool(ok), "detail": detail})


def _same(a, b) -> bool:
    return (a.lo, a.hi) == (b.lo, b.hi)


# ---------------------------------------------------------------------------------------------
# an independent FLOAT solver for d = h_1 + Khat_e d at a scalar drift -- NOT load-bearing; used
# only as the reference a rigorous LOWER bound must not exceed (V14)
# ---------------------------------------------------------------------------------------------
def float_d_at_atom(e: float, n: int = 41, tol: float = 1e-11) -> float:
    Kf, Cf = 0.5, 5.5
    step = 5.0 / (n - 1)

    def phi(y):
        return math.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)

    def Phi(y):
        return 0.5 * (1.0 + math.erf(y / math.sqrt(2)))

    def simpson(f, a, b, k=96):
        if b <= a:
            return 0.0
        h = (b - a) / k
        s = f(a) + f(b)
        for i in range(1, k):
            s += (4.0 if i % 2 else 2.0) * f(a + i * h)
        return s * h / 3.0

    V = [[0.0] * n for _ in range(n)]

    def interp(p, m):
        p = min(max(p, 0.0), 5.0)
        m = min(max(m, 0.0), 5.0)
        i, j = min(int(p / step), n - 2), min(int(m / step), n - 2)
        u, v = (p - i * step) / step, (m - j * step) / step
        return ((1 - u) * (1 - v) * V[i][j] + u * (1 - v) * V[i + 1][j]
                + (1 - u) * v * V[i][j + 1] + u * v * V[i + 1][j + 1])

    def khat(p, m):
        lo, hi = m - Cf, Cf - p
        cuts = sorted({lo, hi} | {c for c in (Kf - p, m - Kf) if lo < c < hi})
        tot = 0.0
        for a, b in zip(cuts[:-1], cuts[1:]):
            if m - Kf < Kf - p and a >= m - Kf - 1e-12 and b <= Kf - p + 1e-12:
                continue                                   # the atom piece: removed
            tot += simpson(lambda z: interp(max(0.0, p + z - Kf), max(0.0, m - z - Kf))
                           * phi(z + e), a, b)
        return tot

    h1 = [[1.0 - (Phi(Cf - i * step + e) - Phi(j * step - Cf + e)) for j in range(n)]
          for i in range(n)]
    for _ in range(400):
        W2 = [[h1[i][j] + khat(i * step, j * step) for j in range(n)] for i in range(n)]
        d = max(abs(W2[i][j] - V[i][j]) for i in range(n) for j in range(n))
        V = W2
        if d < tol:
            break
    return V[0][0]


def main() -> int:
    t0 = time.time()
    PT = I.Blk(E_SCALAR, E_SCALAR)
    one = {(0, 0): F(1)}

    # V1 -- standard-normal moments
    Ms = I.moments_iv(I.Blk(-12), I.Blk(12), 4)
    tgt = [1, 0, 1, 0, 3]
    rec("V1", "standard-normal moments are exactly 1, 0, 1, 0, 3",
        all(v.lo <= t <= v.hi for v, t in zip(Ms, tgt)),
        {"enclosures": [[float(v.lo), float(v.hi)] for v in Ms], "target": tgt})

    # V2 -- the alarm probability is a probability, over the whole block
    ok, rows = True, []
    for p, m in STATES:
        h = I.alarm_prob_iv(p, m, NT)
        good = h.lo >= 0 and h.hi <= 1
        ok = ok and good
        rows.append({"state": [str(p), str(m)], "h1": [float(h.lo), float(h.hi)], "in01": good})
    rec("V2", "the alarm probability lies in [0, 1] uniformly over the block", ok, {"rows": rows})

    # V3 -- (K_e 1) = 1 - h_1
    ok, rows = True, []
    for p, m in STATES:
        k1 = I.kernel_apply_iv(one, p, m, NT)
        rhs = G.Iv(1, 1) - I.alarm_prob_iv(p, m, NT)
        sep = max(k1.lo - rhs.hi, rhs.lo - k1.hi)
        ok = ok and sep <= 0
        rows.append({"state": [str(p), str(m)], "separation": float(sep)})
    rec("V3", "kernel/alarm identity holds uniformly over the block", ok, {"rows": rows})

    # V4 -- K_e = Khat_e + atom, for four weights including a degree-2 one
    ok, rows = True, []
    for nm, w in WS.items():
        for p, m in STATES:
            full = I.kernel_apply_iv(w, p, m, NT)
            hat = I.kernel_apply_iv(w, p, m, NT, atom_removed=True)
            at = I.atom_contribution_iv(w, p, m, NT)
            sep = max(full.lo - (hat + at).hi, (hat + at).lo - full.hi)
            ok = ok and sep <= 0
            rows.append({"w": nm, "state": [str(p), str(m)], "separation": float(sep)})
    rec("V4", "atom decomposition K_e = Khat_e + atom (4 weights x 7 states)", ok,
        {"rows": rows})

    # V5 -- the atom window is non-empty exactly when p + m < 2K
    ok, rows = True, []
    for p, m in [(F(0), F(0)), (F(1, 4), F(1, 4)), (F(1, 2), F(1, 2)), (F(3, 4), F(1, 2)),
                 (F(1), F(0)), (F(2), F(2)), (F(0), F(9, 10))]:
        has = I._pieces(p, m)[3] is not None
        pred = bool(p + m < 2 * I.K)
        ok = ok and has == pred
        rows.append({"state": [str(p), str(m)], "atom_window": has, "predicted": pred})
    rec("V5", "the atom window is non-empty exactly when p + m < 2K = 1", ok, {"rows": rows})

    # V6 -- SCALAR COLLAPSE, bit for bit, at the non-target scalar
    fails = []
    for nm, w in WS.items():
        for p, m in STATES:
            if not _same(X.kernel_apply(w, p, m, E_SCALAR), I.kernel_apply_iv(w, p, m, PT)):
                fails.append(f"kernel:{nm}:{p},{m}")
        for bx in ((F(0), F(1), F(0), F(1)), (F(1), F(2), F(0), F(1)),
                   (F(4), F(5), F(0), F(1)), (F(0), F(5, 4), F(3), F(4))):
            if not _same(X.kernel_box_upper(w, *bx, E_SCALAR, 12),
                         I.kernel_box_upper_iv(w, *bx, PT, 12)):
                fails.append(f"box:{nm}:{bx}")
    for p, m in STATES:
        if not _same(X.alarm_prob(p, m, E_SCALAR), I.alarm_prob_iv(p, m, PT)):
            fails.append(f"alarm:{p},{m}")
    rec("V6", "scalar collapse: a degenerate block reproduces C11 BIT FOR BIT",
        not fails, {"scalar": str(E_SCALAR), "mismatch_count": len(fails),
                    "mismatches": fails[:12],
                    "comparisons": len(WS) * len(STATES) + len(WS) * 4 + len(STATES)})

    # V7 -- the block enclosure contains every point enclosure inside it
    ok, rows = True, []
    w = WS["m_only"]
    for p, m in [(F(0), F(0)), (F(23, 5), F(0)), (F(2), F(2))]:
        blk = I.kernel_apply_iv(w, p, m, NT)
        for e in (NT.lo, (NT.lo + NT.hi) / 2, NT.hi, NT.lo + W / 3):
            pt = X.kernel_apply(w, p, m, e)
            good = blk.lo <= pt.lo and pt.hi <= blk.hi
            ok = ok and good
            rows.append({"state": [str(p), str(m)], "e": str(e), "contained": good})
    rec("V7", "the block enclosure contains the scalar result at every probed drift", ok,
        {"probes": len(rows), "failures": [r for r in rows if not r["contained"]]})

    # V8 -- the facts the interval extension rests on
    xs = [F(-3), F(-1), F(0), F(1), F(3)]
    mono = all(G.Phi(xs[i]).hi <= G.Phi(xs[i + 1]).lo for i in range(len(xs) - 1))
    peak = all(G.phi(F(0)).lo >= G.phi(x).hi for x in xs if x != 0)
    even = _same(G.phi(F(-7, 4)), G.phi(F(7, 4)))
    straddle = I._monomial_pair(F(-1), F(2), 2) == (F(0), F(4))
    rec("V8", "Phi increasing, phi even and peaked at 0, monomial extrema",
        mono and peak and even and straddle,
        {"Phi_increasing": mono, "phi_peak": peak, "phi_even": even, "straddle": straddle})

    # V9 -- a wider block gives a wider enclosure
    narrow = I.Blk(NT.lo, (NT.lo + NT.hi) / 2)
    n = I.kernel_apply_iv(WS["m_only"], F(0), F(0), narrow)
    v = I.kernel_apply_iv(WS["m_only"], F(0), F(0), NT)
    rec("V9", "a wider drift block gives a wider enclosure", v.lo <= n.lo and n.hi <= v.hi,
        {"narrow": [float(n.lo), float(n.hi)], "wide": [float(v.lo), float(v.hi)]})

    # V10 -- the box bound tightens with panels
    w = {(0, 0): F(12), (0, 1): F(-3, 2)}
    bx = (F(0), F(1), F(0), F(1))
    with BD.PhiCache():
        vals = {pn: I.kernel_box_upper_iv(w, *bx, NT, pn).hi for pn in (8, 16, 32)}
    rec("V10", "precision escalation: the box bound tightens monotonically with panels",
        vals[32] <= vals[16] <= vals[8], {str(k): float(v) for k, v in vals.items()})

    # V11 -- the selector's factored margin equals the reviewed box bound
    worst, n11 = F(0), 0
    boxes = [(F(0), F(5, 16), F(0), F(5, 16)), (F(0), F(5, 16), F(15, 16), F(5, 4)),
             (F(5, 2), F(45, 16), F(0), F(5, 16)), (F(0), F(5, 4), F(3), F(4))]
    with BD.PhiCache():
        for bx in boxes:
            row = BD.box_upper_coeffs(*bx, NT, 16)
            for A, B in ((F(12), F(3, 2)), (F(9), F(1)), (F(30), F(4)), (F(7), F(0))):
                for key, ar in (("K", False), ("H", True)):
                    wv = {(0, 0): A, (0, 1): -B}
                    rev = (X.poly_eval_iv(wv, G.Iv(bx[0], bx[1]), G.Iv(bx[2], bx[3])).lo - 1
                           - I.kernel_box_upper_iv(wv, *bx, NT, 16, atom_removed=ar).hi)
                    diff = abs(rev - BD.factored_upper_margin(row, key, A, B))
                    worst = diff if diff > worst else worst
                    n11 += 1
    rec("V11", "the factored box margin equals the REVIEWED kernel_box_upper_iv",
        worst < F(1, 10 ** 80), {"comparisons": n11, "max_abs_difference": float(worst)})

    # V12 -- the selector is minimal, and its choice certifies under the reviewed certifier
    D12, P12 = 3, 16
    with BD.PhiCache():
        rows = [BD.box_upper_coeffs(*b, NT, P12) for b in X.cover(D12)]
        s = BD.select_upper(rows, "K", grid=1000, b_max=F(4), mu=F(1, 2 ** 60))
        cert = I.supersolution_margin_iv({(0, 0): s["A"], (0, 1): -s["B"]}, NT,
                                         depth=D12, panels=P12)
        below = min(BD.factored_upper_margin(r, "K", s["A"] - F(1, 1000), s["B"]) for r in rows)
    rec("V12", "the selector's choice certifies, and one grid step less violates a box",
        s["feasible"] and cert["certified"] and below < 0,
        {"config": [D12, P12], "block": "NON-TARGET", "A": str(s["A"]), "B": str(s["B"]),
         "reviewed_margin": float(cert["margin_lower_bound"]),
         "margin_one_step_below": float(below)})

    # V13 -- the box LOWER bound lies below the pointwise Khat_e u
    u = {(0, 0): F(1, 2), (0, 1): F(1, 10)}
    ok, slack_min, n13 = True, None, 0
    with BD.PhiCache():
        for bx in boxes[:3]:
            lo = BD.kernel_box_lower_iv(u, *bx, NT, 16)
            for p, m in ((bx[0], bx[2]), ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2),
                         (bx[1], bx[3])):
                for e in (NT.lo, (NT.lo + NT.hi) / 2, NT.hi):
                    pt = I.kernel_apply_iv(u, p, m, I.Blk(e, e), atom_removed=True)
                    ok = ok and lo <= pt.lo
                    sl = pt.lo - lo
                    slack_min = sl if slack_min is None or sl < slack_min else slack_min
                    n13 += 1
    rec("V13", "the Khat_e box LOWER bound never exceeds the pointwise value", ok,
        {"checks": n13, "smallest_slack": float(slack_min)})

    # V14 -- the sub-solution route is SOUND on the non-target block
    D14, P14 = 3, 16
    with BD.PhiCache():
        lrows = [BD.box_lower_coeffs(*b, NT, P14) for b in X.cover(D14)]
        sl = BD.select_lower(lrows, grid=1000, beta_max=F(1), mu=F(1, 2 ** 60))
        u14 = {(0, 0): sl["alpha"], (0, 1): sl["beta"]}
        c14 = BD.subsolution_margin_iv(u14, NT, D14, P14)
        inflated = {(0, 0): sl["alpha"] + F(1, 10), (0, 1): sl["beta"]}
        c14_bad = BD.subsolution_margin_iv(inflated, NT, D14, P14)
    refs = {str(e): float_d_at_atom(float(e)) for e in (NT.lo, (NT.lo + NT.hi) / 2, NT.hi)}
    sound = all(float(sl["alpha"]) < r for r in refs.values())
    rec("V14", "the D_lo sub-solution bound is certified, lies below an independent float d(atom)"
               " at every probed drift, and an inflated u fails",
        sl["feasible"] and c14["certified"] and sound and not c14_bad["certified"],
        {"config": [D14, P14], "block": "NON-TARGET", "alpha": str(sl["alpha"]),
         "beta": str(sl["beta"]), "certified": c14["certified"],
         "h_min": float(c14["h_min_lower_bound"]),
         "float_d_at_atom_reference": refs,
         "gaps_reference_minus_alpha": {k: v - float(sl["alpha"]) for k, v in refs.items()},
         "inflated_by_one_tenth_certified": c14_bad["certified"],
         "note": "the float reference is not rigorous (grid 41x41); it is a soundness check"})

    # V15 -- the Phi cache is bit-transparent
    w = {(0, 0): F(12), (0, 1): F(-3, 2)}
    a = I.kernel_box_upper_iv(w, *boxes[1], NT, 16)
    with BD.PhiCache():
        b = I.kernel_box_upper_iv(w, *boxes[1], NT, 16)
        c = I.kernel_box_upper_iv(w, *boxes[1], NT, 16)
    rec("V15", "the Phi cache changes no bit", _same(a, b) and _same(b, c), {})

    # V16 -- the pointwise coefficient form is an UPPER bound on L (conservative screen)
    ok, rows = True, []
    for p, m in ((F(0), F(0)), (F(5, 14), F(15, 14)), (F(5, 2), F(0))):
        cf = BD.pointwise_coeffs(p, m, NT)
        for A, B in ((F(12), F(3, 2)), (F(9), F(1))):
            for key, ar in (("K", False), ("H", True)):
                wv = {(0, 0): A, (0, 1): -B}
                direct = (X.poly_eval_iv(wv, G.Iv(p, p), G.Iv(m, m)).hi - 1
                          - I.kernel_apply_iv(wv, p, m, NT, atom_removed=ar).lo)
                coef = BD.pointwise_upper_hi(cf, key, A, B)
                ok = ok and coef >= direct - F(1, 10 ** 80)
                rows.append({"state": [str(p), str(m)], "A": str(A), "B": str(B), "kernel": key,
                             "coefficient_form": float(coef), "direct": float(direct)})
    rec("V16", "the pointwise coefficient form upper-bounds L, so the screen is conservative",
        ok, {"rows": rows})

    failed = [r["id"] for r in results if not r["pass"]]
    out = {"schema": "C11R_VALIDATION/2",
           "block": "NON-TARGET [5/2, 5/2 + 108337/1250000]; scalar e = 5/2",
           "why_non_target": ("every check is drift-independent mathematics; running them off "
                              "every open cell removes all contact with target-block quantities"),
           "checks": results, "failed": failed,
           "VALIDATION_CLASS": "PASS" if not failed else "REFUSE",
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json", out,
                         producer=__file__)
    for r in results:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['id']:4s} {r['name'][:84]}")
    print(f"\nVALIDATION_CLASS = {out['VALIDATION_CLASS']}  failed={failed}  ({out['seconds']}s)")
    print(f"wrote evidence/validation/C11R_VALIDATION.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
