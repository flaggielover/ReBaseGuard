"""C1b: certified RLR (THEOREM_LR, Theorem LR-3) and same-input Dv' r2 atom constants on the REAL CUSUM kernel,
at DECLARED NON-TARGET point drifts only (declarations D0-D6 in PROGRESS.md).

Usage:  nice python3 -B c1b_certify.py point E_NUM/E_DEN DEG [DEG ...]
Output: NS/validation/C1B_POINT_e<E>.json (one record per degree + ladder minimum).

Statement proved per drift e (pointwise): with R the reachable set,
  (S1) w_T >= 1 + K^_e w_T on R, w_T >= 0          (Lemma T)      -> tau := w_T(a) >= tau_a, C_T := sup_R w_T >= ||G^||
  (S2) W >= 1 + K_e W on R, W >= 0                  (whole kernel) -> A-bar := W(a) >= Lambda(e)
  (S3) tame-error enclosures of the linear functionals tau_a, S2^ = E_a sum M_n^2, E_a sum n, D, D', D''
  (S4) explicit (i') excursion quadratic certificate for L1 (checker: A>0, C>=0, B^2 <= 4AC per box)
and the assembled RLR / Dv' constants follow by THEOREM_LR LR-3 and THEOREM_AD Lemma Dv'.
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
import c1b_float as FL  # noqa: E402

KAPPA1 = G.KAPPA1                  # >= sqrt(2/pi) >= ||K^(1)||, ||K^'||
KAPPA2 = G.kappa2_upper()          # >= 4 phi(1) >= ||K^''||
M2 = F(1)                          # >= ||K^(2)|| (E S^2 = 1)
ATOM = (F(0), F(0))


def fstr(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def sqrt_up(x: F, k: int = 80) -> F:
    n = x.numerator * (1 << (2 * k)) // x.denominator + 1
    return F(KX.G._isqrt(n) + 1, 1 << k)


def dyadic_up(x: F, bits: int = 20) -> F:
    return F(math.ceil(x * (1 << bits)), 1 << bits)


def dyadic_near(x: float, bits: int = 10) -> F:
    return F(round(x * (1 << bits)), 1 << bits)


class Ctx:
    def __init__(self, e: F, log=print):
        Q.guard_drift(e)
        self.e = F(e)
        self.log = log
        self._kc = {}

    def K(self, P: dict, j: int = 0, whole: bool = False) -> tuple:
        key = (id(P), j, whole)
        if key not in self._kc:
            self._kc[key] = (P, KX.pair_subs_e(KX.kernel_gf(P, j, whole), self.e))
        return self._kc[key][1]

    def enc(self, pair: tuple, name: str, **kw) -> dict:
        t = time.time()
        r = KX.enclose_pair(pair, self.e, F(0), **kw)
        r["seconds"] = round(time.time() - t, 2)
        r["sup_abs"] = max(abs(r["lo"]), abs(r["hi"]))
        self.log(f"  enclose {name:6s} lo={float(r['lo']):+.3e} hi={float(r['hi']):+.3e} "
                 f"boxes={r['boxes']} lev={r['max_level']} {r['seconds']}s")
        return r


P = KX.poly_pair
ONE = {(0, 0, 0): F(1)}


def residual_forms(cx: Ctx, c: dict) -> dict:
    K = cx.K
    add = KX.pair_add
    out = {}
    out["b0"] = add(add(P(c["b0"]), P(ONE), -1), K(c["b0"]), -1)
    out["b1"] = add(add(P(c["b1"]), K(c["b0"], 1), -1), K(c["b1"]), -1)
    out["b2"] = add(add(add(P(c["b2"]), K(c["b0"], 2), -1), K(c["b1"], 1), -2), K(c["b2"]), -1)
    out["xT"] = add(add(P(c["xT"]), P(c["b0"]), -1), K(c["xT"]), -1)
    h1, h1p, h1pp = (KX.pair_subs_e(x, cx.e) for x in (KX.H1, KX.H1P, KX.H1PP))
    out["d0"] = add(add(P(c["d0"]), h1, -1), K(c["d0"]), -1)
    out["d1"] = add(add(add(P(c["d1"]), K(c["d0"], 1), -1), h1p, -1), K(c["d1"]), -1)
    k2pp = add(K(c["d0"], 2), K(c["d0"]), -1)
    out["d2"] = add(add(add(add(P(c["d2"]), k2pp, -1), K(c["d1"], 1), -2), h1pp, -1), K(c["d2"]), -1)
    out["W"] = add(add(P(c["W"]), P(ONE), -1), K(c["W"], 0, True), -1)
    return out


def at_atom(Pl: dict) -> F:
    return KX.peval(Pl, F(0), F(0), F(0))


def check_supersolution(cx: Ctx, w: dict, whole: bool, name: str) -> dict:
    """(S1)/(S2) checker: rigorous lower bound of w - 1 - K w on R and of w on R; pointwise refutation search."""
    res = KX.pair_add(KX.pair_add(P(w), P(ONE), -1), cx.K(w, 0, whole), -1)
    r = cx.enc(res, name + "_res")
    wmin, wmax, _ = KX.poly_range_R(w)
    ok = r["lo"] >= 0 and wmin >= 0
    return {"residual_lo": r["lo"], "residual_centre_min": r["centre_min"], "w_min_lo": wmin, "w_max_hi": wmax,
            "certified": ok, "pointwise_refuted": r["centre_min"] < 0, "boxes": r["boxes"]}


def quad_check(cx: Ctx, a: dict, b1: dict, b2: dict, g0: F, g2: F, extra_levels: int = 4) -> dict:
    """THEOREM_LR §cert (i') checker for w = a + b1 mu + b2 mu^2 >= g0 + g2 mu^2 + P w on R (taboo chain):
    A = b2 - g2 - K^b2, B = b1 - K^b1 - 2K^(1)b2, C = a - g0 - K^a - K^(1)b1 - K^(2)b2;
    per box A_lo > 0, C_lo >= 0, max(B^2) <= 4 A_lo C_lo."""
    K = cx.K
    add = KX.pair_add
    A = add(add(P(b2), P({(0, 0, 0): g2}), -1), K(b2), -1)
    B = add(add(P(b1), K(b1), -1), K(b2, 1), -2)
    Cf = add(add(add(add(P(a), P({(0, 0, 0): g0}), -1), K(a), -1), K(b1, 1), -1), K(b2, 2), -1)
    Ai, Bi, Ci = KX.pair_to_int(A), KX.pair_to_int(B), KX.pair_to_int(Cf)
    work = [(b, 0) for b in KX.base_cover()]
    n_ok, fails, n_boxes = 0, [], 0
    while work:
        nxt = []
        for bx, lev in work:
            n_boxes += 1
            ok = True
            for reg in KX.regions_of_box(bx):
                cen, rad = (bx[0], bx[1], cx.e), (bx[2], bx[3], F(0))
                alo, _, _ = KX.gf_box_int(Ai[reg], cen, rad)
                blo, bhi, _ = KX.gf_box_int(Bi[reg], cen, rad)
                clo, _, _ = KX.gf_box_int(Ci[reg], cen, rad)
                bm = max(blo * blo, bhi * bhi)
                if not (alo > 0 and clo >= 0 and bm <= 4 * alo * clo):
                    ok = False
                    if KX.region_of(bx[0], bx[1]) == reg:
                        cv = KX.gf_eval(Cf[reg], bx[0], bx[1], cx.e)
                        av = KX.gf_eval(A[reg], bx[0], bx[1], cx.e)
                        if cv[1] < 0 or av[1] < 0:
                            fails.append({"box": [str(t) for t in bx], "region": reg, "C_centre_hi": float(cv[1]),
                                          "A_centre_hi": float(av[1]), "pointwise_violation": True})
            if ok:
                n_ok += 1
            elif lev < extra_levels:
                nxt.extend((cb, lev + 1) for cb in KX.split_box(bx) if KX.box_in_R_nonempty(cb))
            else:
                fails.append({"box": [str(t) for t in bx], "level": lev})
        work = nxt
    return {"passed": not fails, "boxes_checked": n_boxes, "boxes_ok": n_ok, "failures": fails[:5],
            "n_failures": len(fails), "pointwise_violations": sum(1 for f in fails if f.get("pointwise_violation"))}


def lin_check(cx: Ctx, u: dict, f: dict) -> dict:
    """checker for u >= f + K^ u on R (f a state polynomial): rigorous lower bound of u - f - K^u."""
    res = KX.pair_add(KX.pair_add(P(u), P(f), -1), cx.K(u), -1)
    r = cx.enc(res, "u_res")
    return {"residual_lo": r["lo"], "certified": r["lo"] >= 0, "boxes": r["boxes"], "centre_min": r["centre_min"]}


def certify_degree(e: F, d: int, log=print) -> dict:
    cx = Ctx(e, log)
    t0 = time.time()
    fl = FL.solve_chain(float(e), d, log)
    idx = fl["_idx"]
    keys = ["b0", "b1", "b2", "xT", "d0", "d1", "d2", "W"]
    c = {k: KX.dyadic_round_poly(FL.to_exact_poly(fl[k], idx)) for k in keys}
    t_float = time.time() - t0
    log(f" e={float(e)} d={d}: float candidates {t_float:.1f}s")
    t1 = time.time()
    rf = residual_forms(cx, c)
    enc = {k: cx.enc(v, k) for k, v in rf.items()}
    rn = {k: v["sup_abs"] for k, v in enc.items()}
    # ---- (S1) taboo supersolution by the declared multiplicative scaling rule
    rlo = enc["b0"]["lo"]
    if rlo <= -1:
        return {"drift": fstr(e), "degree": d, "status": "SCALING_RULE_INAPPLICABLE", "r_lo": float(rlo)}
    eta = F(0) if rlo >= 0 else dyadic_up(-rlo / (1 + rlo))
    wT = KX.pscale(c["b0"], 1 + eta)
    sT = check_supersolution(cx, wT, False, "wT")
    tau = at_atom(wT)
    C_T = sT["w_max_hi"]
    # ---- (S2) whole-kernel supersolution
    rWlo = enc["W"]["lo"]
    etaW = F(0) if rWlo >= 0 else dyadic_up(-rWlo / (1 + rWlo))
    W = KX.pscale(c["W"], 1 + etaW)
    sW = check_supersolution(cx, W, True, "W")
    Abar = at_atom(W)
    if not (sT["certified"] and sW["certified"]):
        return {"drift": fstr(e), "degree": d, "status": "SUPERSOLUTION_NOT_CERTIFIED",
                "wT": {k: str(v) for k, v in sT.items()}, "W": {k: str(v) for k, v in sW.items()}}
    # ---- (S3) tame-error chains (two-sided) + subsolution lower bounds (D7(c))
    V_lo = 1 + sT["residual_lo"]            # w_T - K^ w_T >= V_lo on R
    E0n = C_T * rn["b0"]
    b0a = at_atom(c["b0"])
    rhi = enc["b0"]["hi"]
    zeta = F(0) if rhi <= 0 else dyadic_up(rhi / (1 + rhi))
    tau_a_lo = max(b0a - tau * max(rhi, F(0)), (1 - zeta) * b0a)
    tau_a_up = min(tau, b0a - tau * min(enc["b0"]["lo"], F(0)))
    E1n = C_T * (KAPPA1 * E0n + rn["b1"])
    E2a = tau * (M2 * E0n + 2 * KAPPA1 * E1n + rn["b2"])
    S2_tame = at_atom(c["b2"]) + E2a
    ETa = tau * (E0n + rn["xT"])
    TN_tame = at_atom(c["xT"]) + ETa - tau_a_lo
    Ed0n = C_T * rn["d0"]
    D_lo_tame = at_atom(c["d0"]) - tau * max(enc["d0"]["hi"], F(0))
    Wa = at_atom(c["W"])
    rWhi = enc["W"]["hi"]
    zW = F(0) if rWhi <= 0 else dyadic_up(rWhi / (1 + rWhi))
    Lam_lo = max(Wa - Abar * max(rWhi, F(0)), (1 - zW) * Wa)
    D_lo_sm = tau_a_lo / Abar
    D_lo = max(D_lo_tame, D_lo_sm)
    Ed1a = tau * (KAPPA1 * Ed0n + rn["d1"])
    Ed1n = C_T * (KAPPA1 * Ed0n + rn["d1"])
    D1 = abs(at_atom(c["d1"])) + Ed1a
    Ed2a = tau * (KAPPA2 * Ed0n + 2 * KAPPA1 * Ed1n + rn["d2"])
    D2 = abs(at_atom(c["d2"])) + Ed2a
    t_s3 = time.time() - t1
    # ---- one-sided T_N (D7(b)): u = (1+eta) x~T + lam w_T >= w_T + K^u
    t2 = time.time()
    lamT = dyadic_up(max(F(0), -(1 + eta) * enc["xT"]["lo"]) / V_lo * F(17, 16)) + F(1, 1 << 20)
    uT = KX.padd(KX.pscale(c["xT"], 1 + eta), wT, lamT)
    chkT = lin_check(cx, uT, wT)
    TN_one = at_atom(uT) - tau_a_lo if chkT["certified"] else None
    TN_up = min(x for x in (TN_tame, TN_one) if x is not None)
    # ---- one-sided S2^ (D7(a)) and explicit L1 certificate (D6), declared s-ladders
    b2a = at_atom(c["b2"])
    cc = dyadic_near(math.sqrt(max(float(b2a), 1e-9) / float(b0a)))
    g = 1 + eta
    quadS2, quad = [], []
    for s in (F(1, 64), F(1, 16), F(1, 4)):
        # S2: forcing mu^2 (g0 = 0, g2 = 1); A = (1+s)V - 1, B = 2(1+s)g r_b1, C0 = (1+s) g r_b2
        A_lo = (1 + s) * V_lo - 1
        Bn = 2 * (1 + s) * g * rn["b1"]
        C0_lo = (1 + s) * g * enc["b2"]["lo"]
        lam = dyadic_up(max(F(0), Bn * Bn / (4 * A_lo) - C0_lo) / V_lo * F(17, 16)) + F(1, 1 << 20)
        b2q = KX.pscale(wT, 1 + s)
        b1q = KX.pscale(c["b1"], 2 * (1 + s) * g)
        aq = KX.padd(KX.pscale(c["b2"], (1 + s) * g), wT, lam)
        chk = quad_check(cx, aq, b1q, b2q, F(0), F(1))
        val = at_atom(aq)
        log(f"  S2 quad s={s} lam={float(lam):.4g} S2<= {float(val):.6g} passed={chk['passed']} "
            f"boxes={chk['boxes_checked']}")
        quadS2.append({"s": fstr(s), "lam": fstr(lam), "S2_bound": val, "check": chk})
        # L1: forcing c/2 + mu^2/(2c)
        g2c = dyadic_up(1 / (2 * cc), 40)          # forcing c/2 + g2c mu^2 >= |mu| needs 2 c g2c >= 1
        assert 2 * cc * g2c >= 1
        beta = dyadic_up((1 + s) * g2c, 40)
        A_lo = beta * V_lo - g2c
        gb = beta * g
        Bn = 2 * gb * rn["b1"]
        C0_lo = (cc / 2) * enc["b0"]["lo"] + gb * enc["b2"]["lo"]
        lam = dyadic_up(max(F(0), Bn * Bn / (4 * A_lo) - C0_lo) / V_lo * F(17, 16)) + F(1, 1 << 20)
        b2q = KX.pscale(wT, beta)
        b1q = KX.pscale(c["b1"], 2 * gb)
        aq = KX.padd(KX.padd(KX.pscale(c["b0"], cc / 2), c["b2"], gb), wT, lam)
        chk = quad_check(cx, aq, b1q, b2q, cc / 2, g2c)
        val = at_atom(aq)
        log(f"  L1 quad s={s} lam={float(lam):.4g} L1<= {float(val):.6g} passed={chk['passed']} "
            f"boxes={chk['boxes_checked']}")
        quad.append({"s": fstr(s), "beta": fstr(beta), "lam": fstr(lam), "L1_bound": val, "check": chk,
                     "_a": aq, "_b1": b1q, "_b2": b2q})
    t_s4 = time.time() - t2
    S2_one = min((q["S2_bound"] for q in quadS2 if q["check"]["passed"]), default=None)
    S2_up = min(x for x in (S2_tame, S2_one) if x is not None)
    L1_cs = sqrt_up(tau_a_up * S2_up)
    L1_quad = min((q["L1_bound"] for q in quad if q["check"]["passed"]), default=None)
    L1 = min(x for x in (L1_cs, L1_quad) if x is not None)
    L2_tri = S2_up + TN_up
    rec = {"drift": fstr(e), "degree": d, "status": "CERTIFIED",
           "eta_T": eta, "eta_W": etaW, "tau": tau, "C_T": C_T, "A_bar": Abar, "Lambda_lo": Lam_lo,
           "tau_a_lo": tau_a_lo, "tau_a_up": tau_a_up, "S2_up": S2_up, "TN_up": TN_up,
           "S2_tame": S2_tame, "S2_onesided": S2_one, "TN_tame": TN_tame, "TN_onesided": TN_one,
           "TN_check": chkT, "S2_ladder": quadS2, "zeta": zeta, "V_lo": V_lo,
           "D_lo": D_lo, "D_lo_tame": D_lo_tame, "D_lo_SM": D_lo_sm, "D1": D1, "D2": D2,
           "L1_cs": L1_cs, "L1_quad": L1_quad, "L1_up": L1, "L2_up": L2_tri, "c_global": cc,
           "residual_sup": rn, "residual_enclosures": {k: {"lo": v["lo"], "hi": v["hi"], "boxes": v["boxes"],
                                                           "seconds": v["seconds"]} for k, v in enc.items()},
           "supersolution_wT": sT, "supersolution_W": sW,
           "quad_ladder": [{k: v for k, v in q.items() if not k.startswith("_")} for q in quad],
           "float_values": {k: FL.eval_at_atom(fl[k], fl["_B00"]) for k in keys},
           "seconds": {"float": round(t_float, 1), "S1_S3": round(t_s3, 1), "S4": round(t_s4, 1),
                       "total": round(time.time() - t0, 1)},
           "_wT": wT, "_quad": quad}
    rec.update(assemble(rec))
    return rec


def assemble(r: dict) -> dict:
    """THEOREM_LR LR-3 (ratio and non-ratio forms, termwise min) and Lemma Dv' r2, SAME certified inputs."""
    Abar, tau, D_lo, C_T = r["A_bar"], r["tau"], r["D_lo"], r["C_T"]
    A_eff = min(Abar, tau / D_lo)
    d1, d2 = r["D1"] / D_lo, r["D2"] / D_lo
    rho1 = r["L1_up"] / r["tau_a_lo"]
    rho2 = r["L2_up"] / r["tau_a_lo"]
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


def jsonable(o):
    if isinstance(o, F):
        return {"exact": fstr(o), "float": float(o)}
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


def run_point(e: F, degrees: list) -> dict:
    Q.guard_drift(e)
    t0 = time.time()
    recs = []
    for d in degrees:
        rec = certify_degree(e, d)
        recs.append(rec)
        print(f"== d={d} status={rec['status']}", flush=True)
        if rec["status"] == "CERTIFIED":
            for k in ("tau", "C_T", "A_bar", "tau_a_lo", "S2_up", "TN_up", "D_lo", "D1", "D2", "L1_up", "L2_up",
                      "A1_RLR", "A2_RLR", "A1_Dv", "A2_Dv"):
                print(f"   {k:9s} {float(rec[k]):.6g}", flush=True)
    cert = [r for r in recs if r["status"] == "CERTIFIED"]
    best = {}
    if cert:
        # ladder minimum of each certified input (each rung independently valid), then re-assemble
        best = {k: (min if k not in ("tau_a_lo", "D_lo", "Lambda_lo") else max)(r[k] for r in cert)
                for k in ("tau", "C_T", "A_bar", "tau_a_lo", "tau_a_up", "S2_up", "TN_up", "D_lo", "D1", "D2",
                          "L1_up", "L2_up", "Lambda_lo")}
        best.update(assemble(best))
    out = {"schema": "C1B_POINT/1", "drift": fstr(e), "statement": "POINTWISE at drift e (declared non-target)",
           "declarations": "PROGRESS.md D0-D6", "degrees": degrees, "records": recs, "ladder_min": best,
           "kappa1": KAPPA1, "kappa2": KAPPA2, "wall_seconds": round(time.time() - t0, 1)}
    import c1b_prov as PV
    out["provenance"] = PV.provenance({})
    out["latent_proxy"] = "QUARANTINE_AMENDMENT_2 R2.3: values not for handover"
    path = NS / "validation" / f"C1B_R2_PLAIN_POINT_e{str(e).replace('/', '_')}_d{'-'.join(str(d) for d in degrees)}.json"
    path.write_text(json.dumps(jsonable(out), indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_certify.py", f"C1b RLR/Dv' point certification e={e} d={degrees}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes=f"drift {e} declared non-target (guard_drift passed); no cell id used")
    print("wrote", path, flush=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "point":
        run_point(F(sys.argv[2]), [int(x) for x in sys.argv[3:]])
    else:
        print(__doc__)
