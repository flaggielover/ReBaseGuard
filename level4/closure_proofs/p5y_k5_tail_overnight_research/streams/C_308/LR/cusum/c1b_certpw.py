"""C1b certifier, strip-piecewise family (declaration D8; same statements S1-S4, rules D1-D7 as c1b_certify.py).

Usage:  nice python3 -u -B c1b_certpw.py point E_NUM/E_DEN DEG [DEG ...]   [--plain]
Output: NS/validation/C1B_PW_POINT_e<E>.json   (or C1B_PLAIN2_POINT_e<E>.json with --plain, BW = [0,5])

(S1) w_T >= 1 + K^ w_T and w_T >= 0 on R  -> tau = w_T(a) >= tau_a, C_T = sup_R w_T >= ||G^||    (Lemma T)
(S2) W >= 1 + K W and W >= 0 on R         -> A-bar = W(a) >= Lambda                            (THEOREM_AD §4)
(S3) tame-error chains (two-sided) for tau_a, S2^, E sum n, D, D', D''; subsolution lower bounds    (D1, D7(c))
(S4) one-sided quadratic certificates: S2^ (forcing mu^2) and L1 (forcing c/2 + g2 mu^2, 2 c g2 >= 1),
     checker A_lo > 0, C_lo >= 0, B^2 <= 4 A_lo C_lo per box and x-region; one-sided T_N certificate.  (D6, D7)
Assembly: THEOREM_LR LR-3 (termwise min of ratio / non-ratio forms) and Lemma Dv' r2 with the SAME inputs.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
import c1b_gauss as G  # noqa: E402
import c1b_kernel as KX  # noqa: E402
import c1b_pw as PW  # noqa: E402

TIGHT_CT = "--tight-ct" in sys.argv
BLOCK_LIGHT = "--block-light" in sys.argv   # declaration D11: block runs within the ~20 min cap     # declaration D9: sup_R w_T enclosed with tol 1+2^-7, 6 extra levels
KAPPA1 = G.KAPPA1
KAPPA2 = G.kappa2_upper()
M2 = F(1)
ONE = {(0, 0, 0): F(1)}


def fstr(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def sqrt_up(x: F, k: int = 80) -> F:
    n = x.numerator * (1 << (2 * k)) // x.denominator + 1
    return F(G._isqrt(n) + 1, 1 << k)


def dyadic_up(x: F, bits: int = 20) -> F:
    return F(math.ceil(x * (1 << bits)), 1 << bits)


def dyadic_near(x: float, bits: int = 10) -> F:
    return F(round(x * (1 << bits)), 1 << bits)


def wscale(ws, s):
    return [KX.pscale(P, F(s)) for P in ws]


def wadd(a, b, s=1):
    return [KX.padd(x, y, s) for x, y in zip(a, b)]


def wconst(c, S):
    return [{(0, 0, 0): F(c)} if c else {} for _ in range(S)]


class Ctx:
    def __init__(self, e: F, BW, log=print, e_r: F = F(0)):
        Q.guard_drift(F(e) - F(e_r), F(e) + F(e_r))
        self.e, self.BW, self.log, self.e_r = F(e), BW, log, F(e_r)
        self.S = len(BW) - 1
        self._kc = {}

    def K(self, ws, j=0, whole=False):
        key = (id(ws), j, whole)
        if key not in self._kc:
            g = PW.kernel_gf_pw(ws, self.BW, j, whole)
            self._kc[key] = (ws, PW.tsubs_e(g, self.e) if self.e_r == 0 else g)
        return self._kc[key][1]

    def P(self, ws):
        return PW.tpoly(ws, self.BW)

    def enc(self, T, name, **kw):
        if BLOCK_LIGHT and "extra_levels" not in kw:
            kw["extra_levels"] = 2
        t = time.time()
        r = PW.enclose_t(T, self.e, self.e_r, **kw)
        r["seconds"] = round(time.time() - t, 2)
        r["sup_abs"] = max(abs(r["lo"]), abs(r["hi"]))
        self.log(f"  enclose {name:6s} lo={float(r['lo']):+.3e} hi={float(r['hi']):+.3e} boxes={r['boxes']} "
                 f"lev={r['max_level']} argmin={r['argmin_box'][:2]} {r['seconds']}s")
        return r


def residual_forms(cx: Ctx, c: dict) -> dict:
    K, P, add = cx.K, cx.P, PW.tadd
    S = cx.S
    one = wconst(1, S)
    e = cx.e
    out = {}
    out["b0"] = add(add(P(c["b0"]), P(one), -1), K(c["b0"]), -1)
    out["b1"] = add(add(P(c["b1"]), K(c["b0"], 1), -1), K(c["b1"]), -1)
    out["b2"] = add(add(add(P(c["b2"]), K(c["b0"], 2), -1), K(c["b1"], 1), -2), K(c["b2"]), -1)
    out["xT"] = add(add(P(c["xT"]), P(c["b0"]), -1), K(c["xT"]), -1)
    h1, h1p, h1pp = ((PW.tsubs_e(x, e) if cx.e_r == 0 else x) for x in (PW.H1_T, PW.H1P_T, PW.H1PP_T))
    out["d0"] = add(add(P(c["d0"]), h1, -1), K(c["d0"]), -1)
    out["d1"] = add(add(add(P(c["d1"]), K(c["d0"], 1), -1), h1p, -1), K(c["d1"]), -1)
    k2pp = add(K(c["d0"], 2), K(c["d0"]), -1)
    out["d2"] = add(add(add(add(P(c["d2"]), k2pp, -1), K(c["d1"], 1), -2), h1pp, -1), K(c["d2"]), -1)
    out["W"] = add(add(P(c["W"]), P(one), -1), K(c["W"], 0, True), -1)
    return out


def at_atom(ws) -> F:
    return KX.peval(ws[0], F(0), F(0), F(0))


def range_R(cx: Ctx, ws, name, tight: bool = False):
    kw = {"tol": 1 + F(1, 128), "extra_levels": 6} if tight else {}
    r = cx.enc(cx.P(ws), name, **kw)
    return r["lo"], r["hi"]


def check_supersolution(cx: Ctx, w, whole: bool, name: str) -> dict:
    res = PW.tadd(PW.tadd(cx.P(w), cx.P(wconst(1, cx.S)), -1), cx.K(w, 0, whole), -1)
    r = cx.enc(res, name + "R")
    wmin, wmax = range_R(cx, w, name + "rng", tight=TIGHT_CT and not whole)
    return {"residual_lo": r["lo"], "residual_centre_min": r["centre_min"], "w_min_lo": wmin, "w_max_hi": wmax,
            "certified": r["lo"] >= 0 and wmin >= 0, "pointwise_refuted": r["centre_min"] < 0, "boxes": r["boxes"]}


def lin_check(cx: Ctx, u, f) -> dict:
    res = PW.tadd(PW.tadd(cx.P(u), cx.P(f), -1), cx.K(u), -1)
    r = cx.enc(res, "uR")
    return {"residual_lo": r["lo"], "certified": r["lo"] >= 0, "boxes": r["boxes"], "centre_min": r["centre_min"]}


def quad_check(cx: Ctx, a, b1, b2, g0: F, g2: F, extra_levels: int = 4) -> dict:
    K, P, add, S = cx.K, cx.P, PW.tadd, cx.S
    A = add(add(P(b2), P(wconst(g2, S)), -1), K(b2), -1)
    B = add(add(P(b1), K(b1), -1), K(b2, 1), -2)
    Cf = add(add(add(add(P(a), P(wconst(g0, S)), -1), K(a), -1), K(b1, 1), -1), K(b2, 2), -1)
    Ai, Bi, Ci = (tuple(KX.to_int_gf(x) for x in T) for T in (A, B, Cf))
    work = [(b, 0) for b in KX.base_cover()]
    n_ok, fails, n_boxes = 0, [], 0
    while work:
        nxt = []
        for bx, lev in work:
            n_boxes += 1
            ok = True
            for J in PW.regions_of_box(bx):
                cen, rad = (bx[0], bx[1], cx.e), (bx[2], bx[3], cx.e_r)
                alo, _, _ = KX.gf_box_int(Ai[J - 1], cen, rad)
                blo, bhi, _ = KX.gf_box_int(Bi[J - 1], cen, rad)
                clo, _, _ = KX.gf_box_int(Ci[J - 1], cen, rad)
                if not (alo > 0 and clo >= 0 and max(blo * blo, bhi * bhi) <= 4 * alo * clo):
                    ok = False
                    if PW.region_of_point(bx[0], bx[1]) == J:
                        cv = KX.gf_eval(Cf[J - 1], bx[0], bx[1], cx.e)
                        av = KX.gf_eval(A[J - 1], bx[0], bx[1], cx.e)
                        if cv[1] < 0 or av[1] < 0:
                            fails.append({"box": [float(t) for t in bx], "region": J, "C_centre_hi": float(cv[1]),
                                          "A_centre_hi": float(av[1]), "pointwise_violation": True})
            if ok:
                n_ok += 1
            elif lev < extra_levels:
                nxt.extend((cb, lev + 1) for cb in KX.split_box(bx) if KX.box_in_R_nonempty(cb))
            else:
                fails.append({"box": [float(t) for t in bx], "level": lev})
        work = nxt
    return {"passed": not fails, "boxes_checked": n_boxes, "boxes_ok": n_ok, "failures": fails[:5],
            "n_failures": len(fails), "pointwise_violations": sum(1 for f in fails if f.get("pointwise_violation"))}


def certify_degree(e: F, d: int, BW, log=print, e_r: F = F(0)) -> dict:
    cx = Ctx(e, BW, log, e_r)
    S = cx.S
    t0 = time.time()
    fl = PW.solve_chain_pw(float(e), d, BW)
    keys = ["b0", "b1", "b2", "xT", "d0", "d1", "d2", "W"]
    c = {k: PW.to_exact_pw(fl[k], fl["_idx"]) for k in keys}
    t_float = time.time() - t0
    log(f" e={float(e)} d={d} strips={S}: float candidates {t_float:.1f}s")
    t1 = time.time()
    enc = {k: cx.enc(v, k) for k, v in residual_forms(cx, c).items()}
    rn = {k: v["sup_abs"] for k, v in enc.items()}
    rlo = enc["b0"]["lo"]
    if rlo <= -1:
        return {"drift": fstr(e), "degree": d, "status": "SCALING_RULE_INAPPLICABLE"}
    eta = F(0) if rlo >= 0 else dyadic_up(-rlo / (1 + rlo))
    wT = wscale(c["b0"], 1 + eta)
    sT = check_supersolution(cx, wT, False, "wT")
    rWlo = enc["W"]["lo"]
    etaW = F(0) if rWlo >= 0 else dyadic_up(-rWlo / (1 + rWlo))
    W = wscale(c["W"], 1 + etaW)
    sW = check_supersolution(cx, W, True, "W")
    if not (sT["certified"] and sW["certified"]):
        return {"drift": fstr(e), "degree": d, "status": "SUPERSOLUTION_NOT_CERTIFIED", "sT": str(sT), "sW": str(sW)}
    tau, C_T, Abar = at_atom(wT), sT["w_max_hi"], at_atom(W)
    V_lo = 1 + sT["residual_lo"]
    # ---- (S3)
    E0n = C_T * rn["b0"]
    b0a = at_atom(c["b0"])
    rhi = enc["b0"]["hi"]
    zeta = F(0) if rhi <= 0 else dyadic_up(rhi / (1 + rhi))
    tau_a_lo = max(b0a - tau * max(rhi, F(0)), (1 - zeta) * b0a)
    tau_a_up = min(tau, b0a - tau * min(enc["b0"]["lo"], F(0)))
    E1n = C_T * (KAPPA1 * E0n + rn["b1"])
    S2_tame = at_atom(c["b2"]) + tau * (M2 * E0n + 2 * KAPPA1 * E1n + rn["b2"])
    TN_tame = at_atom(c["xT"]) + tau * (E0n + rn["xT"]) - tau_a_lo
    Ed0n = C_T * rn["d0"]
    D_lo_tame = at_atom(c["d0"]) - tau * max(enc["d0"]["hi"], F(0))
    Wa, rWhi = at_atom(c["W"]), enc["W"]["hi"]
    zW = F(0) if rWhi <= 0 else dyadic_up(rWhi / (1 + rWhi))
    Lam_lo = max(Wa - Abar * max(rWhi, F(0)), (1 - zW) * Wa)
    D_lo_sm = tau_a_lo / Abar
    D_lo = max(D_lo_tame, D_lo_sm)
    Ed1n = C_T * (KAPPA1 * Ed0n + rn["d1"])
    D1 = abs(at_atom(c["d1"])) + tau * (KAPPA1 * Ed0n + rn["d1"])
    D2 = abs(at_atom(c["d2"])) + tau * (KAPPA2 * Ed0n + 2 * KAPPA1 * Ed1n + rn["d2"])
    t_s3 = time.time() - t1
    # ---- one-sided T_N
    t2 = time.time()
    lamT = dyadic_up(max(F(0), -(1 + eta) * enc["xT"]["lo"]) / V_lo * F(17, 16)) + F(1, 1 << 20)
    uT = wadd(wscale(c["xT"], 1 + eta), wT, lamT)
    chkT = lin_check(cx, uT, wT)
    TN_one = at_atom(uT) - tau_a_lo if chkT["certified"] else None
    TN_up = min(x for x in (TN_tame, TN_one) if x is not None)
    # ---- (S4) one-sided S2^ and L1
    b2a = at_atom(c["b2"])
    cc = dyadic_near(math.sqrt(max(float(b2a), 1e-9) / float(b0a)))
    g = 1 + eta
    quadS2, quad = [], []
    for s in ((F(1, 16),) if BLOCK_LIGHT else (F(1, 64), F(1, 16), F(1, 4))):
        A_lo = (1 + s) * V_lo - 1
        Bn = 2 * (1 + s) * g * rn["b1"]
        C0_lo = (1 + s) * g * enc["b2"]["lo"]
        lam = dyadic_up(max(F(0), Bn * Bn / (4 * A_lo) - C0_lo) / V_lo * F(17, 16)) + F(1, 1 << 20)
        aq = wadd(wscale(c["b2"], (1 + s) * g), wT, lam)
        chk = quad_check(cx, aq, wscale(c["b1"], 2 * (1 + s) * g), wscale(wT, 1 + s), F(0), F(1))
        val = at_atom(aq)
        log(f"  S2 quad s={s} lam={float(lam):.4g} S2<= {float(val):.6g} passed={chk['passed']} boxes={chk['boxes_checked']}")
        quadS2.append({"s": fstr(s), "lam": float(lam), "S2_bound": val, "check": chk})
        g2c = dyadic_up(1 / (2 * cc), 40)
        assert 2 * cc * g2c >= 1
        beta = dyadic_up((1 + s) * g2c, 40)
        A_lo = beta * V_lo - g2c
        gb = beta * g
        Bn = 2 * gb * rn["b1"]
        C0_lo = (cc / 2) * enc["b0"]["lo"] + gb * enc["b2"]["lo"]
        lam = dyadic_up(max(F(0), Bn * Bn / (4 * A_lo) - C0_lo) / V_lo * F(17, 16)) + F(1, 1 << 20)
        aq = wadd(wadd(wscale(c["b0"], cc / 2), c["b2"], gb), wT, lam)
        b1q, b2q = wscale(c["b1"], 2 * gb), wscale(wT, beta)
        chk = quad_check(cx, aq, b1q, b2q, cc / 2, g2c)
        val = at_atom(aq)
        log(f"  L1 quad s={s} lam={float(lam):.4g} L1<= {float(val):.6g} passed={chk['passed']} boxes={chk['boxes_checked']}")
        quad.append({"s": fstr(s), "lam": float(lam), "L1_bound": val, "check": chk, "_a": aq, "_b1": b1q,
                     "_b2": b2q, "_g2": g2c})
    t_s4 = time.time() - t2
    S2_one = min((q["S2_bound"] for q in quadS2 if q["check"]["passed"]), default=None)
    S2_up = min(x for x in (S2_tame, S2_one) if x is not None)
    L1_cs = sqrt_up(tau_a_up * S2_up)
    L1_quad = min((q["L1_bound"] for q in quad if q["check"]["passed"]), default=None)
    L1 = min(x for x in (L1_cs, L1_quad) if x is not None)
    rec = {"drift": fstr(e), "drift_radius": fstr(F(e_r)), "degree": d, "strips": S, "status": "CERTIFIED",
           "eta_T": eta, "eta_W": etaW, "tau": tau, "C_T": C_T, "A_bar": Abar, "Lambda_lo": Lam_lo,
           "tau_a_lo": tau_a_lo, "tau_a_up": tau_a_up, "S2_up": S2_up, "TN_up": TN_up,
           "S2_tame": S2_tame, "S2_onesided": S2_one, "TN_tame": TN_tame, "TN_onesided": TN_one,
           "D_lo": D_lo, "D_lo_tame": D_lo_tame, "D_lo_SM": D_lo_sm, "D1": D1, "D2": D2,
           "L1_cs": L1_cs, "L1_quad": L1_quad, "L1_up": L1, "L2_up": S2_up + TN_up, "c_global": cc,
           "V_lo": V_lo, "zeta": zeta,
           "residual_enclosures": {k: {"lo": float(v["lo"]), "hi": float(v["hi"]), "boxes": v["boxes"],
                                       "argmin_box": v["argmin_box"], "argmax_box": v["argmax_box"],
                                       "seconds": v["seconds"]} for k, v in enc.items()},
           "supersolution_wT": {k: (float(v) if isinstance(v, F) else v) for k, v in sT.items()},
           "supersolution_W": {k: (float(v) if isinstance(v, F) else v) for k, v in sW.items()},
           "TN_check": {k: (float(v) if isinstance(v, F) else v) for k, v in chkT.items()},
           "S2_ladder": [{k: (float(v) if isinstance(v, F) else v) for k, v in q.items()} for q in quadS2],
           "L1_ladder": [{k: (float(v) if isinstance(v, F) else v) for k, v in q.items() if not k.startswith("_")}
                         for q in quad],
           "float_values_at_atom": {k: fl["_disc"].feval(fl[k], 0.0, 0.0) for k in keys},
           "C_T_float_NONCERTIFIED": max(fl["_disc"].feval(fl["b0"], p, m) for (p, m) in fl["_disc"].pts),
           "seconds": {"float": round(t_float, 1), "S1_S3": round(t_s3, 1), "S4_TN": round(t_s4, 1),
                       "total": round(time.time() - t0, 1)},
           "_wT": wT, "_quad": quad, "_c": c}
    rec.update(assemble(rec))
    return rec


def assemble(r: dict) -> dict:
    Abar, tau, D_lo, C_T = r["A_bar"], r["tau"], r["D_lo"], r["C_T"]
    A_eff = min(Abar, tau / D_lo)
    d1, d2 = r["D1"] / D_lo, r["D2"] / D_lo
    rho1, rho2 = r["L1_up"] / r["tau_a_lo"], r["L2_up"] / r["tau_a_lo"]
    q1 = min(A_eff * rho1, r["L1_up"] / D_lo)
    q2 = min(A_eff * rho2, r["L2_up"] / D_lo)
    A1_rlr = q1 + A_eff * d1
    A2_rlr = q2 + 2 * q1 * d1 + A_eff * (2 * d1 * d1 + d2)
    rho1_dv = KAPPA1 * C_T
    rho2_dv = 2 * KAPPA1 ** 2 * C_T ** 2 + KAPPA2 * C_T
    A1_dv = A_eff * (rho1_dv + d1)
    A2_dv = A_eff * (rho2_dv + 2 * KAPPA1 * C_T * d1 + 2 * d1 * d1 + d2)
    return {"A0": A_eff, "delta1": d1, "delta2": d2, "rho1": rho1, "rho2": rho2, "rho1_Dv": rho1_dv,
            "rho2_Dv": rho2_dv, "A1_RLR": A1_rlr, "A2_RLR": A2_rlr, "A1_Dv": A1_dv, "A2_Dv": A2_dv,
            "ratio_A1_Dv_over_RLR": A1_dv / A1_rlr, "ratio_A2_Dv_over_RLR": A2_dv / A2_rlr,
            "ratio_rho1_Dv_over_RLR": rho1_dv / rho1, "ratio_rho2_Dv_over_RLR": rho2_dv / rho2}


EXACT_KEYS = {"tau", "C_T", "A_bar", "Lambda_lo", "tau_a_lo", "tau_a_up", "S2_up", "TN_up", "D_lo", "D1", "D2",
              "L1_up", "L2_up", "A0", "A1_RLR", "A2_RLR", "A1_Dv", "A2_Dv", "eta_T", "eta_W", "c_global"}


def jsonable(o, key=None):
    if isinstance(o, F):
        return {"exact": fstr(o), "float": float(o)} if key in EXACT_KEYS else float(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v, str(k)) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


LADDER_KEYS_MIN = ("tau", "C_T", "A_bar", "tau_a_up", "S2_up", "TN_up", "D1", "D2", "L1_up", "L2_up")
LADDER_KEYS_MAX = ("tau_a_lo", "D_lo", "Lambda_lo")


def run_point(e: F, degrees: list, BW, tag: str, e_r: F = F(0)) -> dict:
    Q.guard_drift(e - e_r, e + e_r)
    t0 = time.time()
    recs = []
    for d in degrees:
        rec = certify_degree(e, d, BW, e_r=e_r)
        recs.append(rec)
        print(f"== d={d} status={rec['status']}", flush=True)
        if rec["status"] == "CERTIFIED":
            for k in ("tau", "C_T", "A_bar", "tau_a_lo", "S2_up", "TN_up", "D_lo", "D1", "D2", "L1_up", "L2_up",
                      "A1_RLR", "A2_RLR", "A1_Dv", "A2_Dv"):
                print(f"   {k:9s} {float(rec[k]):.6g}", flush=True)
            print(f"   seconds {rec['seconds']}", flush=True)
    cert = [r for r in recs if r["status"] == "CERTIFIED"]
    best = {}
    if cert:
        best = {k: min(r[k] for r in cert) for k in LADDER_KEYS_MIN}
        best.update({k: max(r[k] for r in cert) for k in LADDER_KEYS_MAX})
        best.update(assemble(best))
    out = {"schema": "C1B_POINT/2", "family": tag, "BW": list(BW), "drift": fstr(e), "drift_radius": fstr(e_r),
           "statement": ("POINTWISE at drift e (declared non-target)" if e_r == 0 else
                         f"BLOCK-UNIFORM for every e in [{fstr(e - e_r)}, {fstr(e + e_r)}] (declared non-target)"), "declarations": "PROGRESS.md D0-D8",
           "degrees": degrees, "records": recs, "ladder_min": best, "kappa1": KAPPA1, "kappa2": KAPPA2,
           "wall_seconds": round(time.time() - t0, 1)}
    stem = f"POINT_e{str(e).replace('/', '_')}" if e_r == 0 else f"BLOCK_{fstr(e - e_r).replace('/', '_')}__{fstr(e + e_r).replace('/', '_')}"
    path = NS / "validation" / f"C1B_{tag}_{stem}.json"
    path.write_text(json.dumps(jsonable(out), indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_certpw.py", f"C1b RLR/Dv' point certification ({tag}) e={e} d={degrees}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes=f"drift {e} declared non-target (guard_drift passed); no cell id used")
    print("wrote", path, flush=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "block":
        lo, hi = F(sys.argv[2]), F(sys.argv[3])
        degs = [int(x) for x in sys.argv[4:] if not x.startswith("--")]
        run_point((lo + hi) / 2, degs, PW.BW_PW, "PW9" if TIGHT_CT else "PW", e_r=(hi - lo) / 2)
    elif len(sys.argv) >= 4 and sys.argv[1] == "point":
        plain = "--plain" in sys.argv
        degs = [int(x) for x in sys.argv[3:] if not x.startswith("--")]
        tag = ("PLAIN2" if plain else "PW") + ("9" if TIGHT_CT else "")
        run_point(F(sys.argv[2]), degs, PW.BW_PLAIN if plain else PW.BW_PW, tag)
    else:
        print(__doc__)
