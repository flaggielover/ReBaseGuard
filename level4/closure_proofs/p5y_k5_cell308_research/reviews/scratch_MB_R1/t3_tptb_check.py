"""REVIEW_THEOREM_MB_R1 scratch (reviewMB): synthetic, non-target check of tpt.penalty_blocked (Theorem TPT-B).

Synthetic cell [29/10, 31/10] (e0 = 3, rho = 1/10), label SYNTH, no real input of any kind. Checks:
  K1  penalty_blocked >= an independent dense float evaluation of sup of the running transport integral, with
      block constants that DECREASE across block boundaries and a binding K1 cap (upper-bound property);
  K2  the endpoint-only rule of Corollary TPT-M (max(0, I(rho)) per side), applied with the same non-monotone
      block constants, UNDER-estimates the sup (so the piece-end rule is necessary; a control that must fire);
  K3  dominance: penalty_blocked <= penalty_closed with the componentwise-max (cell) constants;
  K4  fail-closed gap: a block profile that is disjoint from H_K1 at a piece's inner end is NOT refused when the
      cell constants in cp are large (check_nonempty only uses cp.A*).
stdlib only; floats appear only in the independent dense evaluation (non-rigorous by design).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
LP = NS.parent
sys.path.insert(0, str(NS / "code"))
import c308_quarantine as Q  # noqa: E402

Q.install_import_guard()
sys.path.insert(0, str(LP / "p5y_k5_tail_overnight_research" / "streams" / "E_assembly"))
import tpt  # noqa: E402  (pinned r2, sha256 05cebc9c...)

E0, RHO = F(3), F(1, 10)
Q.guard_drift(E0 - RHO, E0 + RHO)


def term(Hc, fF, fD, fH, fG, Env4):
    return tpt.SourceTerm(H_at_a=(Hc - F(1, 1000), Hc + F(1, 1000)), abs_G_at_a=F(0), fF=fF, fD=fD, fH=fH, fG=fG,
                          Env4=Env4)


def profile(A, cap):
    terms = [term(F(3, 10), F(1, 100), F(2, 100), F(5, 100), F(3, 10), F(4)),
             term(F(1, 5), F(1, 200), F(1, 50), F(3, 100), F(1, 5), F(3))]
    return tpt.CellProfile(detector="SYNTH", m=2, cell=0, e0=E0, rho=RHO, g_hi=F(0), A0=A[0], A1=A[1], A2=A[2],
                           terms=terms, W=(F(-1, 100), F(1, 100)), H_K1=cap)


def blocks_nonmono():
    # right side: large constants next to e0, then a sharp DECREASE; left side symmetric-ish
    return [tpt.Block(F(29, 10), F(3), F(1, 2), F(1, 2), F(1, 2)),
            tpt.Block(F(3), F(302, 100), F(40), F(50), F(80)),
            tpt.Block(F(302, 100), F(31, 10), F(1, 2), F(1, 2), F(1, 2))]


def dense_sup(cp, blocks, N=200000):
    """independent float evaluation of sup_e of the running integrals (true integrand, exact cap via max/min)."""
    e0, rho = float(cp.e0), float(cp.rho)
    polys = {}

    def A_at(t):
        cand = [b for b in blocks if float(b.e_lo) < t < float(b.e_hi)] or \
            [b for b in blocks if float(b.e_lo) <= t <= float(b.e_hi)]
        return (max(float(b.A0) for b in cand), max(float(b.A1) for b in cand), max(float(b.A2) for b in cand))

    def lohi(t):
        s = abs(t - e0)
        A = A_at(t)
        lo = float(cp.W[0])
        hi = float(cp.W[1])
        for tm in cp.terms:
            p0 = float(tm.fF) + s * float(tm.fD) + s * s * float(tm.fH) / 2 + s ** 3 * float(tm.fG) / 6 + s ** 4 * float(tm.Env4) / 24
            p1 = float(tm.fD) + s * float(tm.fH) + s * s * float(tm.fG) / 2 + s ** 3 * float(tm.Env4) / 6
            p2 = float(tm.fH) + s * float(tm.fG) + s * s * float(tm.Env4) / 2
            rad = A[0] * p2 + 2 * A[1] * p1 + A[2] * p0
            lo += (float(tm.H_at_a[0]) - rad) / cp.m
            hi += (float(tm.H_at_a[1]) + rad) / cp.m
        if cp.H_K1 is not None:
            lo, hi = max(lo, float(cp.H_K1[0])), min(hi, float(cp.H_K1[1]))
        return lo, hi

    best = 0.0
    run = 0.0
    h = rho / N
    for i in range(N):
        t = e0 + (i + 0.5) * h
        run += h * t * (-lohi(t)[0])
        best = max(best, run)
    run = 0.0
    for i in range(N):
        t = e0 - (i + 0.5) * h
        run += h * t * lohi(t)[1]
        best = max(best, run)
    return best


def endpoint_only_rule(cp, blocks):
    """MUTANT: Corollary TPT-M's endpoint rule applied to block constants: max(0, I_right(rho), I_left(rho))."""
    r = tpt.penalty_blocked(cp, blocks)
    return max(F(0), r["I_right_full"], r["I_left_full"])


def main():
    out = {}
    bl = blocks_nonmono()
    cellA = (max(b.A0 for b in bl), max(b.A1 for b in bl), max(b.A2 for b in bl))
    for tag, cap in (("cap_none", None), ("cap_binding", (F(-41, 10), F(41, 10)))):
        cp = profile(cellA, cap)
        pb = tpt.penalty_blocked(cp, bl)
        dense = dense_sup(cp, bl)
        endpoint = endpoint_only_rule(cp, bl)
        pc = tpt.penalty_closed(cp)["P_star"]
        out[tag] = {"P_star_B": float(pb["P_star_B"]), "dense_float_sup": dense,
                    "K1_upper_bound_ok": float(pb["P_star_B"]) >= dense - 1e-9,
                    "K1_rel_gap": (float(pb["P_star_B"]) - dense) / max(dense, 1e-300),
                    "K2_endpoint_rule": float(endpoint), "K2_endpoint_rule_underestimates": float(endpoint) < dense - 1e-9,
                    "K3_P_closed_cellmax": float(pc), "K3_dominance_ok": pb["P_star_B"] <= pc}
    # K4: planted inconsistent cap (valid only for the large constants): block constants tiny on the outer right
    bl4 = [tpt.Block(F(29, 10), F(3), F(9), F(12), F(20)),
           tpt.Block(F(3), F(61, 20), F(9), F(12), F(20)),
           tpt.Block(F(61, 20), F(31, 10), F(0), F(0), F(0))]
    cp4 = profile((F(9), F(12), F(20)), None)
    lo, hi = tpt._lo_hi_with(cp4, (F(0), F(0), F(0)))
    s_in = F(5, 100)
    lo_s, hi_s = tpt.peval(lo, s_in), tpt.peval(hi, s_in)
    cap4 = (hi_s + F(1, 100), hi_s + F(2))          # disjoint from the tiny-constant profile at s = 5/100
    cp4.H_K1 = cap4
    try:
        r4 = tpt.penalty_blocked(cp4, bl4)
        out["K4"] = {"refused": False, "P_star_B": float(r4["P_star_B"]),
                     "block_profile_at_s_in": [float(lo_s), float(hi_s)], "cap": [float(c) for c in cap4]}
    except ValueError as exc:
        out["K4"] = {"refused": True, "reason": str(exc)}
    print(json.dumps(out, indent=1))
    (HERE / "out_t3_tptb.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_event("reviews/scratch_MB_R1/t3_tptb_check.py",
                "REVIEW_THEOREM_MB_R1 T3: synthetic TPT-B checks of pinned tpt.py r2 (penalty_blocked) on a SYNTH cell "
                "[29/10, 31/10]; upper bound vs dense float, endpoint-rule mutant, dominance, empty-intersection gap",
                klass="REVIEW", agent="reviewMB",
                notes="synthetic inputs only; drift range guarded; no cell id, no tail file, no operator quantity")


if __name__ == "__main__":
    main()
