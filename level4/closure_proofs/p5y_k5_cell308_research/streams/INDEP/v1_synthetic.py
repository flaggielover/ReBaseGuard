"""V1 -- synthetic exact validation of mb_independent (stream F2). Imports only the stdlib and mb_independent.

Every case is synthetic; every drift set lies outside the research quarantine band and its mirror (checked by the
module's own band guard, which stays ON). Hand-computed values are written in the comments next to each case.
Writes results/V1_RESULTS.json. Exit code 0 iff every check passes.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mb_independent as mb  # noqa: E402

CHECKS: list[dict] = []
QUIET = False          # set during the self-controls, whose planted mutants are EXPECTED to fail checks


def check(name, ok, **info):
    CHECKS.append({"name": name, "pass": bool(ok), **{k: str(v) for k, v in info.items()}})
    if not ok and not QUIET:
        print("FAIL", name, info)


def refuses(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except mb.Refusal as exc:
        return True, str(exc)[:120]
    return False, "no refusal"


# ------------------------------------------------------------------ exact a + b*sqrt(2) comparisons

def le_sqrt2(x, a, b):
    """x <= a + b*sqrt(2) exactly (b may be negative)."""
    d = a - x                       # need d + b sqrt2 >= 0
    if b >= 0:
        return d >= 0 or (d < 0 and 2 * b * b >= d * d)
    return d >= 0 and d * d >= 2 * b * b


def ge_sqrt2(x, a, b):
    """x >= a + b*sqrt(2) exactly."""
    return le_sqrt2(-x, -a, -b)


# ------------------------------------------------------------------ L1-L7, L9 hand cases

def hand_layers():
    # L1: Abar=10, tau=6, C_T=2, D_lo=1/2, D1=1, D2=3, k1=1, k2=2: tau/D_lo=12, A_eff=10, d1=2, d2=6
    #     A1 = 10(2+2) = 40; A2 = 10(8+4+8+8+6) = 340.  Abar=None: A_eff=12 -> (12, 48, 408)
    check("L1 dv_prime hand", mb.dv_prime(10, 6, 2, F(1, 2), 1, 3, 1, 2) == (10, 40, 340))
    check("L1 dv_prime no Abar", mb.dv_prime(None, 6, 2, F(1, 2), 1, 3, 1, 2) == (12, 48, 408))
    check("L1 dv_prime INF Abar", mb.dv_prime(mb.INF, 6, 2, F(1, 2), 1, 3, 1, 2) == (12, 48, 408))
    ok, why = refuses(mb.dv_prime, 10.0, 6, 2, F(1, 2), 1, 3, 1, 2)
    check("L1 refuses float", ok, why=why)
    ok, why = refuses(mb.dv_prime, 10, 6, 2, 0, 1, 3, 1, 2)
    check("L1 refuses D_lo=0", ok, why=why)
    # L2: registry as L1, Ubar=8 -> A_eff=8: (8, 32, 272); with DM refresh tau_a_lo=6: D_lo'=max(1/2, 6/9)=2/3,
    #     tau/D_lo'=9, A_eff=9, d1=3/2, d2=9/2: A1 = 9*7/2 = 63/2, A2 = 9*(8+4+6+9/2+9/2) = 243
    reg = {"A_bar": 10, "tau": 6, "C_T": 2, "D_lo": F(1, 2), "D1": 1, "D2": 3}
    check("L2 dv_prime_M Ubar", mb.dv_prime_M(reg, 8, 1, 2) == (8, 32, 272))
    check("L2 dv_prime_M Ubar=INF equals L1", mb.dv_prime_M(reg, None, 1, 2) == mb.dv_prime(10, 6, 2, F(1, 2), 1, 3, 1, 2))
    reg2 = dict(reg, tau_a_lo=6)
    check("L2 dv_prime_M + DM", mb.dv_prime_M(reg2, 9, 1, 2, dlo_refresh=True) == (9, F(63, 2), 243))
    ok, why = refuses(mb.dv_prime_M, reg, 9, 1, 2, dlo_refresh=True)
    check("L2 DM needs tau_a_lo", ok, why=why)
    ok, why = refuses(mb.dv_prime_M, reg, 9.0, 1, 2)
    check("L2 refuses float Ubar (non-certified)", ok, why=why)
    # L3: A_bar=10,tau=6,C_T=2,C_R=20,tau_a_lo=4,D_lo=1/2,D1=1,D2=3,L1=8,L2=20; k=(1,2); Ubar=INF, no refresh:
    #     A_eff=10, d=(2,6), rho=(2,5), rhoDv=(2,12), c1=min(20,16,20)=16, c2=min(50,40,120)=40,
    #     A1=min(36,400)=36, A2=min(40+64+140=244, 16800)=244, A0=min(10,20)=10
    blk = {"A_bar": 10, "tau": 6, "C_T": 2, "C_R": 20, "tau_a_lo": 4, "D_lo": F(1, 2), "D1": 1, "D2": 3,
           "L1_up": 8, "L2_up": 20}
    check("L3 d14_M hand", mb.d14_M(blk, None, 1, 2, False) == (10, 36, 244))
    #     Ubar=8, tau_a_lo=6, refresh: D_lo'=max(1/2, 6/8)=3/4, A_eff=min(8, 8)=8, d=(4/3,4), rho=(4/3,10/3),
    #     c1=min(32/3,32/3,16)=32/3, c2=min(80/3,80/3,96)=80/3, A1=64/3, A2=80/3+256/9+544/9=1040/9, A0=8
    blk2 = dict(blk, tau_a_lo=6)
    d = mb.d14_M_detail(blk2, 8, 1, 2, True)
    check("L3 d14_M + DM hand", (d["A0"], d["A1"], d["A2"]) == (8, F(64, 3), F(1040, 9)) and d["D_lo_used"] == F(3, 4))
    d_no = mb.d14_M_detail(blk2, 8, 1, 2, False)
    check("L3 DM never lowers D_lo", d["D_lo_used"] >= d_no["D_lo_used"])
    #     Lemma-G caps bind when C_R is small (C_R=3: G1=9, G2=72, A0 slot min(A_eff, C_R)=3)
    check("L3 d14_M G caps + C3 A0 slot", mb.d14_M(dict(blk, C_R=3), None, 1, 2, False) == (3, 9, 72))
    ok, why = refuses(mb.d14_M, {k: v for k, v in blk.items() if k != "L2_up"}, None, 1, 2, False)
    check("L3 refuses missing input", ok, why=why)
    # L4
    check("L4 lemma_g hand", mb.lemma_g(3, 1, 2) == (3, 9, 72))
    # L5
    check("L5 envelope", mb.envelope([5, None, 7, 4, None, 6], [0, F(1, 4), F(1, 2), 1, 3, 4]) == [5, 5, 5, 4, 4, 4])
    check("L5 envelope leading None", mb.envelope([None, 3]) == [None, 3])
    ok, why = refuses(mb.envelope, [5, 4], [1, 1])
    check("L5 refuses non-increasing drifts", ok, why=why)
    ok, why = refuses(mb.envelope, [5, 4], [1, 2])
    check("L5 band guard fires on a block drift in the band", ok, why=why)
    # L6
    bs = mb.block_supply({"S_I1": (10, 50, 400), "DvM": (8, 60, 300), "D14M": None, "G": (12, 40, 500)})
    check("L6 block_supply", (bs["A0"], bs["A1"], bs["A2"]) == (8, 40, 300)
          and bs["provenance"] == {"A0": "DvM", "A1": "G", "A2": "DvM"})
    ok, why = refuses(mb.block_supply, {"DvM": (1, 2, 3)})
    check("L6 refuses missing S_I1", ok, why=why)
    # L7
    rungs = [{"degree": 4, "status": "CERTIFIED", "tau": 7, "D_lo": F(1, 2), "C_R": 30},
             {"degree": 6, "status": "CERTIFIED", "tau": 6, "D_lo": F(2, 5), "C_R": 31},
             {"degree": 8, "status": "FAILED", "tau": 1, "D_lo": 100, "C_R": 1}]
    lad = mb.ladder(rungs)
    check("L7 ladder", (lad["tau"], lad["D_lo"], lad["C_R"]) == (6, F(1, 2), 30)
          and lad["from"] == {"tau": 6, "D_lo": 4, "C_R": 4})
    check("L7 ladder no certified rung -> None", mb.ladder([rungs[2]]) is None)
    # L9
    check("L9 CLOSED", mb.gamma_mb(-5, (F(1), F(2)))["decision"] == "CLOSED")
    check("L9 NOT_CLOSED", mb.gamma_mb(-1, (F(1), F(2)))["decision"] == "NOT_CLOSED")
    check("L9 UNDECIDED", mb.gamma_mb(F(-3, 2), (F(1), F(2)))["decision"] == "UNDECIDED")
    check("L9 boundary Gamma_hi = 0 is not CLOSED", mb.gamma_mb(-2, (F(1), F(2)))["decision"] == "UNDECIDED")
    # kappas
    k = mb.check_kappas(F(7978845609, 10 ** 10), 4 * F(24197072451914337, 10 ** 17))
    check("kappa check accepts kappa1=7978845609/1e10, kappa2=4*0.24197072451914337",
          k["kappa1_ge_sqrt_2_over_pi"] and k["kappa2_ge_4_phi_1"])
    k = mb.check_kappas(F(7978845608, 10 ** 10), 4 * F(2419707245191433, 10 ** 16))
    check("kappa check rejects values below sqrt(2/pi) / 4 phi(1)",
          not k["kappa1_ge_sqrt_2_over_pi"] and not k["kappa2_ge_4_phi_1"])
    # dyadic hull
    lo, hi = mb.dyadic_hull(F(1, 3), F(2, 3))
    check("dyadic hull outward", lo <= F(1, 3) and hi >= F(2, 3) and (F(1, 3) - lo) < F(1, 2 ** 20)
          and lo * 2 ** 20 == int(lo * 2 ** 20))


# ------------------------------------------------------------------ L8 hand cases

def src(**kw):
    base = {"f_F": 0, "f_D": 0, "f_H": 0, "f_G": 0, "Env4": 0, "Hhat": [0, 0], "G_abs": 0}
    base.update(kw)
    return base


def prof(e0, rho, sources, H, W=(0, 0)):
    return {"e0": e0, "rho": rho, "x_lo": e0 - rho, "x_hi": e0 + rho, "m": len(sources), "sources": sources,
            "W": list(W), "H_final": list(H)}


def hand_tptb():
    # (a) single block, no cap: f_F=f_D=1, A=(0,0,1): rad = 1+s; e0=4, rho=1.
    #     right = int_0^1 (4+s)(1+s) = 41/6, left = int_0^1 (4-s)(1+s) = 31/6 -> P* = 41/6 (TPT closed form)
    pa = prof(4, 1, [src(f_F=1, f_D=1)], (-100, 100))
    r = mb.tptb(pa, [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8(a) single block = TPT closed form 41/6", r["P_lo"] == r["P_hi"] == F(41, 6), got=r["P_hi"])
    # same with the block split in 4 identical triples: piece ends change nothing
    r4 = mb.tptb(pa, [{"lo": a, "hi": b, "A0": 0, "A1": 0, "A2": 1}
                      for a, b in ((3, F(7, 2)), (F(7, 2), F(17, 4)), (F(17, 4), F(9, 2)), (F(9, 2), 5))])
    check("L8(a') identical triples on 4 blocks = 41/6", r4["P_lo"] == r4["P_hi"] == F(41, 6))
    # (b) constant profile = C5-T: rad = 0, Hhat=[-3,2], H_final=[-3,2]: max(0, 3(25-16)/2, 2(16-9)/2) = 27/2
    pb = prof(4, 1, [src(Hhat=[-3, 2])], (-3, 2))
    r = mb.tptb(pb, [{"lo": 3, "hi": 5, "A0": 1, "A1": 1, "A2": 1}])
    check("L8(b) constant profile = C5-T 27/2", r["P_lo"] == r["P_hi"] == F(27, 2) == mb.p5_c5t_closed_form(pb))
    pb2 = prof(4, 1, [src(f_F=1000)], (-3, 2))          # huge radius: both caps bind everywhere
    r = mb.tptb(pb2, [{"lo": 3, "hi": 5, "A0": 1, "A1": 1, "A2": 1}])
    check("L8(b') cap-bound profile = C5-T 27/2", r["P_lo"] == r["P_hi"] == F(27, 2))
    # (c) decreasing block constants: f_F=1, Hhat=[1,1], rad=A2; blocks [3,4]:0, [4,9/2]:5, [9/2,5]:0
    #     right running: 4*(81/4-16)/2 = 17/2, then -(25-81/4)/2 = -19/8 -> 49/8; left: (16-9)/2 = 7/2
    #     P*_B = 17/2 at the interior piece end; endpoint-only rule gives 49/8 < 17/2 (INVALID, C4)
    pc = prof(4, 1, [src(f_F=1, Hhat=[1, 1])], (-100, 100))
    bc = [{"lo": 3, "hi": 4, "A0": 0, "A1": 0, "A2": 0}, {"lo": 4, "hi": F(9, 2), "A0": 0, "A1": 0, "A2": 5},
          {"lo": F(9, 2), "hi": 5, "A0": 0, "A1": 0, "A2": 0}]
    r = mb.tptb(pc, bc)
    re_ = mb.tpt_endpoint_only(pc, bc)
    check("L8(c) decreasing block constants: piece-end rule 17/2", r["P_lo"] == r["P_hi"] == F(17, 2),
          argmax=r["argmax"])
    check("L8(c) endpoint-only rule fails (49/8 < 17/2)", re_["P_hi"] == F(49, 8) and re_["P_hi"] < r["P_lo"])
    # (d) irrational crossing: f_H=1, A=(0,0,2): rad = s^2; H=[-2,2]; e0=5, rho=2; crossing sqrt(2)
    #     right = 23 - 20 sqrt2/3, left = 17 - 20 sqrt2/3 -> P* = 23 - 20 sqrt2/3
    pd = prof(5, 2, [src(f_H=1)], (-2, 2))
    r = mb.tptb(pd, [{"lo": 3, "hi": 7, "A0": 0, "A1": 0, "A2": 2}])
    check("L8(d) irrational crossing bracket contains 23 - 20 sqrt2/3",
          ge_sqrt2(r["P_hi"], F(23), F(-20, 3)) and le_sqrt2(r["P_lo"], F(23), F(-20, 3))
          and r["width"] < F(1, 2 ** 150), width_log2=r["width"].denominator.bit_length() - r["width"].numerator.bit_length())
    # (d') below the band: e0=1/2, rho=1/4, H=[-1/32,1/32]: P* = 19/4096 - sqrt2/768
    pd2 = prof(F(1, 2), F(1, 4), [src(f_H=1)], (F(-1, 32), F(1, 32)))
    r = mb.tptb(pd2, [{"lo": F(1, 4), "hi": F(3, 4), "A0": 0, "A1": 0, "A2": 2}])
    check("L8(d') irrational crossing below band contains 19/4096 - sqrt2/768",
          ge_sqrt2(r["P_hi"], F(19, 4096), F(-1, 768)) and le_sqrt2(r["P_lo"], F(19, 4096), F(-1, 768))
          and r["width"] < F(1, 2 ** 150))
    # (e) rational crossing hit exactly: f_D=1, A=(0,0,1): rad = s; H=[-1/2,1/2]; e0=4, rho=1 -> 83/48
    pe = prof(4, 1, [src(f_D=1)], (F(-1, 2), F(1, 2)))
    r = mb.tptb(pe, [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8(e) rational crossing exact", r["P_lo"] == r["P_hi"] == F(83, 48))  # c308-quarantine: literal-ok (an integral value, not a drift)
    # (f) refusals
    bad = dict(pa, x_hi=pa["x_hi"] + F(1, 10 ** 30))
    ok, why = refuses(mb.tptb, bad, [{"lo": 3, "hi": pa["x_hi"] + F(1, 10 ** 30), "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses E != [e0-rho, e0+rho] (C5)", ok and "CELL_IDENTITY" in why, why=why)
    ok, why = refuses(mb.tptb, prof(F(1, 4), F(1, 4), [src(f_F=1)], (-1, 1)),
                      [{"lo": 0, "hi": F(1, 2), "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses x_lo = 0", ok, why=why)
    ok, why = refuses(mb.tptb, prof(4, 1, [src(f_F=1.0)], (-1, 1)), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses float", ok, why=why)
    ok, why = refuses(mb.tptb, prof(4, 1, [src(f_F=1, f_D=1)], (2, 3)), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 C6 refuses empty band at s=0", ok and "C6" in why, why=why)
    pc6 = prof(4, 1, [src(f_F=1, Hhat=[1, 1])], (F(3, 2), 10))  # c308-quarantine: literal-ok (an H_final end, not a drift)
    bc6 = [{"lo": 3, "hi": 4, "A0": 0, "A1": 0, "A2": 5}, {"lo": 4, "hi": F(9, 2), "A0": 0, "A1": 0, "A2": 5},
           {"lo": F(9, 2), "hi": 5, "A0": 0, "A1": 0, "A2": 0}]
    ok, why = refuses(mb.tptb, pc6, bc6)
    check("L8 C6 refuses empty band at an OUTER piece inner end (s=0 check passes)", ok and "C6" in why, why=why)
    ok, why = refuses(mb.tptb, pa, [{"lo": 3, "hi": 4, "A0": 0, "A1": 0, "A2": 1},
                                    {"lo": F(41, 10), "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses tiling gap", ok, why=why)
    ok, why = refuses(mb.tptb, pa, [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": -1}])
    check("L8 refuses negative block constant", ok, why=why)
    ok, why = refuses(mb.tptb, dict(pa, m=2), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses m label mismatch", ok, why=why)
    ok, why = refuses(mb.tptb, prof(4, 1, [src(f_F=1, Hhat=[1, 0])], (-1, 1)), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses unordered Hhat", ok, why=why)
    ok, why = refuses(mb.tptb, dict(pa, M_consumed=99), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses M_consumed != mag(H_final)", ok, why=why)
    check("L8 accepts M_consumed == mag(H_final)",
          mb.tptb(dict(pa, M_consumed=100), [{"lo": 3, "hi": 5, "A0": 0, "A1": 0, "A2": 1}])["P_hi"] == F(41, 6))
    # guard control: a synthetic cell INSIDE the band must be refused by the module's guard before any evaluation
    ok, why = refuses(mb.tptb, prof(2, F(1, 2), [src(f_F=1)], (-1, 1)), [{"lo": F(3, 2), "hi": F(5, 2), "A0": 0, "A1": 0, "A2": 1}])  # c308-quarantine: literal-ok (refusal control, never evaluated)
    check("L8 research band guard refuses a band cell", ok and "BAND" in why, why=why)
    ok, why = refuses(mb.tptb, prof(-4, 1, [src(f_F=1)], (-1, 1)), [{"lo": -5, "hi": -3, "A0": 0, "A1": 0, "A2": 1}])
    check("L8 refuses a negative-side cell (x_lo <= 0)", ok, why=why)


# ------------------------------------------------------------------ L8 randomized soundness (independent pointwise path)

def point_band(P, A, s):
    """lo(s), hi(s) evaluated DIRECTLY from the TC-P formulas at one point (no polynomial composition)."""
    m = len(P["sources"])
    lo = F(P["W"][0])
    hi = F(P["W"][1])
    A0, A1, A2 = A
    for r in P["sources"]:
        fF, fD, fH, fG, E4 = (F(r[k]) for k in ("f_F", "f_D", "f_H", "f_G", "Env4"))
        p0 = fF + s * fD + s ** 2 * fH / 2 + s ** 3 * fG / 6 + s ** 4 * E4 / 24
        p1 = fD + s * fH + s ** 2 * fG / 2 + s ** 3 * E4 / 6
        p2 = fH + s * fG + s ** 2 * E4 / 2
        half = A0 * p2 + 2 * A1 * p1 + A2 * p0 + s * F(r.get("G_abs", 0))
        lo += (F(r["Hhat"][0]) - half) / m
        hi += (F(r["Hhat"][1]) + half) / m
    return lo, hi


def darboux(P, blocks, N=48):
    """Coarse independent bracket of P*_B: Darboux sums of w*min(g,c) on N sub-intervals per piece, using the
    monotonicity of min(g, c) and positivity of w (interval product), max over sub-interval ends."""
    e0, rho = F(P["e0"]), F(P["rho"])
    Hlo, Hhi = F(P["H_final"][0]), F(P["H_final"][1])
    best_lo = best_hi = F(0)
    for side in ("R", "L"):
        cuts = sorted({(F(b[k]) - e0) if side == "R" else (e0 - F(b[k])) for b in blocks for k in ("lo", "hi")})
        pts = [F(0)] + [c for c in cuts if 0 < c < rho] + [rho]
        run_lo = run_hi = F(0)
        for sa, sb in zip(pts, pts[1:]):
            tm = e0 + (sa + sb) / 2 if side == "R" else e0 - (sa + sb) / 2
            A = next((b["A0"], b["A1"], b["A2"]) for b in blocks if F(b["lo"]) <= tm <= F(b["hi"]))
            A = tuple(F(x) for x in A)
            for k in range(N):
                u = sa + (sb - sa) * k / N
                v = sa + (sb - sa) * (k + 1) / N

                def mval(s):
                    lo, hi = point_band(P, A, s)
                    return min(-Hlo, -lo) if side == "R" else min(Hhi, hi)
                mu, mv = mval(u), mval(v)
                wu = e0 + u if side == "R" else e0 - u
                wv = e0 + v if side == "R" else e0 - v
                prods = [x * y for x in (mu, mv) for y in (wu, wv)]
                run_lo += min(prods) * (v - u)
                run_hi += max(prods) * (v - u)
                best_lo = max(best_lo, run_lo)
                best_hi = max(best_hi, run_hi)
    return best_lo, best_hi


def rnd_q(rng, lo, hi, den=64):
    return F(rng.randint(int(lo * den), int(hi * den)), den)


def random_case(rng):
    e0 = rng.choice([F(1, 2), F(3, 4), F(1), F(3), F(7, 2), F(4)])
    rho = rng.choice([F(1, 8), F(1, 5), F(1, 4)]) if e0 < 2 else rng.choice([F(1, 4), F(1, 3), F(1, 2)])
    if e0 < 2 and e0 + rho >= F(6, 5):  # c308-quarantine: literal-ok (validation drifts stay below the band)
        rho = F(1, 8)
    if e0 > 2 and e0 - rho <= F(13, 5):  # c308-quarantine: literal-ok (validation drifts stay above the band)
        rho = F(1, 4)
    m = rng.randint(1, 4)
    sources = []
    for _ in range(m):
        c = rng.randint(-3, 3)
        sources.append({"f_F": rnd_q(rng, 0, 1, 16), "f_D": rnd_q(rng, 0, 2, 16), "f_H": rnd_q(rng, 0, 4, 16),
                        "f_G": rnd_q(rng, 0, 8, 16), "Env4": rnd_q(rng, 0, 40, 4),
                        "Hhat": [F(c, 4), F(c, 4) + rnd_q(rng, 0, F(1, 4), 64)], "G_abs": rng.choice([0, 0, F(1, 8)])})
    W = (F(rng.randint(-8, 0), 16), F(rng.randint(0, 8), 16))
    nb = rng.randint(1, 6)
    x_lo, x_hi = e0 - rho, e0 + rho
    inner = sorted({x_lo + (x_hi - x_lo) * F(rng.randint(1, 63), 64) for _ in range(nb - 1)})
    ends = [x_lo] + inner + [x_hi]
    blocks = [{"lo": a, "hi": b, "A0": rnd_q(rng, 0, 8, 8), "A1": rnd_q(rng, 0, 40, 4), "A2": rnd_q(rng, 0, 300, 2)}
              for a, b in zip(ends, ends[1:])]
    if rng.random() < 0.4:
        # decreasing block constants away from e0 and positive centres: running integrals that rise then fall
        for b in blocks:
            dist = min(abs(F(b["lo"]) - e0), abs(F(b["hi"]) - e0)) / rho
            fac = F(1, 1 + int(64 * dist) ** 2)
            for k in ("A0", "A1", "A2"):
                b[k] = F(b[k]) * fac
        for r in sources:
            shift = rnd_q(rng, 0, 40, 4)
            r["Hhat"] = [r["Hhat"][0] + shift, r["Hhat"][1] + shift]
    # cap: sometimes wide (no crossing), sometimes tight (crossings)
    P0 = {"e0": e0, "rho": rho, "x_lo": x_lo, "x_hi": x_hi, "m": m, "sources": sources, "W": list(W),
          "H_final": [-10 ** 6, 10 ** 6]}
    los, his = [], []
    for b in blocks:
        A = (b["A0"], b["A1"], b["A2"])
        for s in (F(0), rho):
            lo, hi = point_band(P0, A, s)
            los.append(lo)
            his.append(hi)
    mode = rng.choice(["wide", "tight", "tight", "one", "shift"])
    if mode == "wide":
        H = [min(los) - 1, max(his) + 1]
    else:
        lo0 = max(point_band(P0, (b["A0"], b["A1"], b["A2"]), F(0))[0] for b in blocks)
        hi0 = min(point_band(P0, (b["A0"], b["A1"], b["A2"]), F(0))[1] for b in blocks)
        span_lo = lo0 - min(los)
        span_hi = max(his) - hi0
        f1, f2 = F(rng.randint(1, 15), 16), F(rng.randint(1, 15), 16)
        H = [lo0 - f1 * span_lo, hi0 + f2 * span_hi]
        if mode == "one":
            H[1] = max(his) + 1
        if mode == "shift":        # an H_final that may miss some piece's band (C6 path) or pinch it
            lo_all = sorted(los + his)
            a, b = sorted(rng.sample(lo_all, 2))
            H = [a, b]
    P0["H_final"] = H
    return P0, blocks


def fuzz(n=160, seed=20260928):
    rng = random.Random(seed)
    stats = {"cases": 0, "refused_C6": 0, "split_pieces": 0, "cap_pieces": 0, "profile_pieces": 0,
             "max_width_log2": None, "interior_points": 0}
    worst = None
    for _ in range(n):
        P, blocks = random_case(rng)
        try:
            r = mb.tptb(P, blocks)
        except mb.Refusal as exc:
            if "C6" in str(exc):
                stats["refused_C6"] += 1
                # the refusal must be justified: some piece's inner end is empty (independent pointwise check)
                if not c6_justified(P, blocks):
                    check("fuzz C6 refusal justified", False, P=P, blocks=blocks)
                continue
            raise
        stats["cases"] += 1
        if c6_justified(P, blocks):
            check("fuzz accepted case has no empty inner end", False, P=P, blocks=blocks)
        for side in r["pieces"].values():
            for pc in side:
                stats[{"split": "split_pieces", "split_exact": "split_pieces", "cap": "cap_pieces",
                       "profile": "profile_pieces"}[pc["regime"]]] += 1
        w = r["width"]
        wl = (w.denominator.bit_length() - w.numerator.bit_length()) if w else 10 ** 6
        worst = wl if worst is None else min(worst, wl)
        check_ok = r["width"] < F(1, 2 ** 150)
        dlo, dhi = darboux(P, blocks, N=24)
        c5t = mb.p5_c5t_closed_form(P)
        ok = check_ok and dlo <= r["P_hi"] and r["P_lo"] <= dhi and r["P_hi"] <= c5t
        # piece-end theorem check: running integral at random interior points never exceeds P_hi
        for side_name, side in r["pieces"].items():
            for pc in side:
                for _k in range(3):
                    frac = F(rng.randint(1, 31), 32) if _k < 2 else F(1)   # two interior points and the piece end
                    s_mid = pc["s_a"] + (pc["s_b"] - pc["s_a"]) * frac
                    part = interior_running(P, blocks, side_name, s_mid)
                    stats["interior_points"] += 1
                    if part > r["P_hi"]:
                        ok = False
        # single-block TPT with the componentwise max triple dominates TPT-B (P*_B <= P*_TPT)
        Amax = tuple(max(F(b[k]) for b in blocks) for k in ("A0", "A1", "A2"))
        try:
            rt = mb.tptb(P, [{"lo": P["x_lo"], "hi": P["x_hi"], "A0": Amax[0], "A1": Amax[1], "A2": Amax[2]}])
            ok = ok and r["P_lo"] <= rt["P_hi"]
        except mb.Refusal:
            pass
        # monotone in block constants: raising one block constant never lowers P*_B
        j = rng.randrange(len(blocks))
        key = rng.choice(["A0", "A1", "A2"])
        bl2 = [dict(b) for b in blocks]
        bl2[j][key] = F(bl2[j][key]) + F(1, 3)
        try:
            r2 = mb.tptb(P, bl2)
            ok = ok and r2["P_hi"] >= r["P_lo"]
        except mb.Refusal:
            pass
        if not ok:
            check("fuzz case", False, P=P, blocks=blocks, r=(r["P_lo"], r["P_hi"]), darboux=(dlo, dhi), c5t=c5t)
    stats["max_width_log2"] = -worst if worst is not None else None
    check("L8 fuzz: no accepted case has an empty inner end (C6 two-sided)",
          all(c["pass"] for c in CHECKS if c["name"] == "fuzz accepted case has no empty inner end"))
    check("L8 fuzz: every C6 refusal independently justified",
          all(c["pass"] for c in CHECKS if c["name"] == "fuzz C6 refusal justified"), n=stats["refused_C6"])
    check("L8 fuzz: every accepted case sound (width < 2^-150, Darboux-consistent, <= C5-T, interior <= P_hi, "
          "TPT dominance, monotone)", all(c["pass"] for c in CHECKS if c["name"] == "fuzz case"), **stats)
    return stats


def c6_justified(P, blocks):
    e0, rho = F(P["e0"]), F(P["rho"])
    Hlo, Hhi = F(P["H_final"][0]), F(P["H_final"][1])
    for side in ("R", "L"):
        cuts = sorted({(F(b[k]) - e0) if side == "R" else (e0 - F(b[k])) for b in blocks for k in ("lo", "hi")})
        pts = [F(0)] + [c for c in cuts if 0 < c < rho] + [rho]
        for sa, sb in zip(pts, pts[1:]):
            tm = e0 + (sa + sb) / 2 if side == "R" else e0 - (sa + sb) / 2
            A = next((F(b["A0"]), F(b["A1"]), F(b["A2"])) for b in blocks if F(b["lo"]) <= tm <= F(b["hi"]))
            lo, hi = point_band(P, A, sa)
            if max(Hlo, lo) > min(Hhi, hi):
                return True
    return False


def interior_running(P, blocks, side, s_end):
    """Upper bound of the running integral from e0 to the interior point s_end on one side (via the module's own
    piece routine on truncated pieces). Used for the piece-end theorem check."""
    Pp = mb._parse_profile(P, True)
    blk = mb._parse_blocks(blocks, Pp["x_lo"], Pp["x_hi"])
    pieces = mb._side_pieces(Pp, blk, side)
    e0 = Pp["e0"]
    Hlo, Hhi = Pp["H"]
    run = F(0)
    for sa, sb, i in pieces:
        if sa >= s_end:
            break
        sb = min(sb, s_end)
        lo_p, hi_p = mb.profile_polys(Pp, blk[i][2])
        if side == "R":
            w, g, c = [e0, F(1)], [-x for x in lo_p], -Hlo
        else:
            w, g, c = [e0, F(-1)], list(hi_p), Hhi
        plo, phi, _ = mb._piece_bracket(w, g, c, sa, sb, 200)
        run += plo
    return run


def self_controls():
    """The V1 fuzz checks must be able to fail: rerun them with the module's planted L8 mutants and require
    that each mutant is caught at least once (and that the hand cases catch the endpoint-only rule)."""
    global CHECKS, QUIET
    orig = mb.tptb
    QUIET = True
    res = {}
    for mut in ("endpoint_only", "flip_t", "drop_piece_end"):
        saved = CHECKS
        CHECKS = []

        def patched(profile, blocks, _m=mut, **kw):
            kw.pop("_mutant", None)
            return orig(profile, blocks, _mutant=_m, **kw)
        mb.tptb = patched
        try:
            fuzz(n=60, seed=777)
        except Exception as exc:  # a mutant may also crash the harness: that also counts as detection
            CHECKS.append({"name": "fuzz case", "pass": False, "exc": repr(exc)[:80]})
        finally:
            mb.tptb = orig
        n_fail = sum(1 for c in CHECKS if c["name"] == "fuzz case" and not c["pass"])
        CHECKS = saved
        res[mut] = n_fail
        QUIET = False
        check(f"V1 self-control: fuzz detects planted L8 mutant {mut}", n_fail > 0, detections=n_fail)
        QUIET = True
    QUIET = False
    return res


def main():
    hand_layers()
    hand_tptb()
    stats = fuzz()
    stats["self_controls"] = self_controls()
    n_pass = sum(c["pass"] for c in CHECKS)
    out = {"schema": "F2_V1_RESULTS/1", "module_revision": mb.MODULE_REVISION, "n_checks": len(CHECKS),
           "n_pass": n_pass, "all_pass": n_pass == len(CHECKS), "fuzz_stats": stats, "checks": CHECKS}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "V1_RESULTS.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"V1: {n_pass}/{len(CHECKS)} checks pass; fuzz {stats}")
    return 0 if n_pass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
