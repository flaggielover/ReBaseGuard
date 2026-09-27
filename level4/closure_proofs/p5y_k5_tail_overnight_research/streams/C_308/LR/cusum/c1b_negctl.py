"""C1b negative controls (declaration D4, D6) and finite-difference score checks. Non-target drift e = 1/2 only.

N1  planted non-supersolution (w_T scaled by 1 - 2^-6) must be rejected, with an exact pointwise violation.
N2  score sign: central differences of the plain kernel in e vs the score-weighted kernels K^(1), K^(2) - K^;
    the correct sign must agree within the proved Taylor bound, the flipped sign must violate it.
N3  window mis-specification: (a) atom window not removed, (b) alarm window shifted by 1/8 -> mass balance
    K^1 + k_a + h1 = 1 and the independent quadrature cross-check must both fail; the correct kernel passes both.
N4  the explicit (i') L1 certificate with a' = a - kappa (C'(atom) = -C(atom) < 0 exactly) must be rejected;
    N4b the one-sided T_N certificate u scaled by 1/2 must be rejected by lin_check.
Output: NS/validation/C1B_NEGCTL.json
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
import c1b_certpw as CP  # noqa: E402
import c1b_float as FL  # noqa: E402
import c1b_kernel as KX  # noqa: E402
import c1b_pw as PW  # noqa: E402

BW = PW.BW_PW
E0 = F(1, 2)
PTS = [(F(0), F(0)), (F(1, 2), F(1, 4)), (F(2), F(1)), (F(4), F(0)), (F(0), F(3)), (F(1, 8), F(3, 8))]


def iv_mid(iv):
    return (iv[0] + iv[1]) / 2


def n2_score(w: dict, wsup: F) -> dict:
    h = F(1, 1 << 12)
    for x in (E0 - h, E0, E0 + h):
        Q.guard_drift(x)
    g = PW.kernel_gf_pw(w, BW, 0)
    gm, g0, gp = (PW.tsubs_e(g, x) for x in (E0 - h, E0, E0 + h))
    k1 = PW.tsubs_e(PW.kernel_gf_pw(w, BW, 1), E0)
    k2 = PW.tsubs_e(PW.kernel_gf_pw(w, BW, 2), E0)
    # sign-flipped first score: weight +(z+e) = -S  -> -K^(1);  flipped t: K^(2) + K^ instead of K^(2) - K^
    b1 = h * h / 6 * F(2450, 1000) * wsup          # (h^2/6) E|He_3| ||w||, E|He_3| <= sqrt(6) < 2.450
    b2 = h * h / 12 * F(4900, 1000) * wsup         # (h^2/12) E|He_4| ||w||, E|He_4| <= sqrt(24) < 4.900
    rows = []
    ok_true = ok_flip = True
    for (p, m) in PTS:
        vm, v0, vp = (iv_mid(PW.teval(G_, p, m, x)) for G_, x in ((gm, E0 - h), (g0, E0), (gp, E0 + h)))
        fd1 = (vp - vm) / (2 * h)
        fd2 = (vp - 2 * v0 + vm) / (h * h)
        s1 = iv_mid(PW.teval(k1, p, m, E0))
        s2 = iv_mid(PW.teval(k2, p, m, E0)) - v0
        s2f = iv_mid(PW.teval(k2, p, m, E0)) + v0
        tol_iv = F(1, 10 ** 20)            # interval-midpoint slack (phi widths ~1e-40, divided by h^2 ~ 1.7e7)
        t1 = abs(fd1 - s1) <= b1 + tol_iv
        f1 = abs(fd1 + s1) <= b1 + tol_iv
        t2 = abs(fd2 - s2) <= b2 + tol_iv
        f2 = abs(fd2 - s2f) <= b2 + tol_iv
        ok_true &= t1 and t2
        ok_flip &= not (f1 and f2)
        rows.append({"p": str(p), "m": str(m), "fd1": float(fd1), "K1w": float(s1), "err1": float(abs(fd1 - s1)),
                     "bound1": float(b1), "flip1_err": float(abs(fd1 + s1)), "fd2": float(fd2), "Kppw": float(s2),
                     "err2": float(abs(fd2 - s2)), "bound2": float(b2), "flip2_err": float(abs(fd2 - s2f)),
                     "true_pass": t1 and t2, "flip_detected": not (f1 and f2),
                     "flip1_detected": not f1, "flip2_detected": not f2})
    return {"h": str(h), "rows": rows, "true_sign_passes_all": ok_true,
            "flipped_detected_all_points": all(r["flip_detected"] for r in rows),
            "flip1_detected_points": sum(r["flip1_detected"] for r in rows),
            "flip2_detected_points": sum(r["flip2_detected"] for r in rows), "points": len(rows)}


def n3_window(ws: list, coefs, idx) -> dict:
    e = E0
    one = [{(0, 0, 0): F(1)}] * (len(BW) - 1)
    ka = PW.tsubs_e(PW.KA_T, e)
    h1 = PW.tsubs_e(PW.H1_T, e)
    D = PW.DiscPW.__new__(PW.DiscPW)
    D.d, D.idx, D.BW = max(i + j for i, j in idx), idx, BW
    quad_ref = []
    for (p, m) in PTS:
        nl, _ = FL.nodes(float(p), float(m), float(e))
        quad_ref.append(sum(ww * D.feval(coefs, pp, mm) for (ww, S, pp, mm) in nl))

    def devs(Kone_vals, Kw_vals):
        kah1 = [iv_mid(PW.teval(PW.tadd(ka, h1), p, m, e)) for (p, m) in PTS]
        md = max(abs(a + b - 1) for a, b in zip(Kone_vals, kah1))
        qd = max(abs(float(v) - q) for v, q in zip(Kw_vals, quad_ref))
        return {"mass_dev": float(md), "quad_dev": qd}

    def vals(whole=False):
        Ko = PW.tsubs_e(PW.kernel_gf_pw(one, BW, 0, whole), e)
        Kw = PW.tsubs_e(PW.kernel_gf_pw(ws, BW, 0, whole), e)
        return ([iv_mid(PW.teval(Ko, p, m, e)) for (p, m) in PTS], [iv_mid(PW.teval(Kw, p, m, e)) for (p, m) in PTS])

    out = {"correct": devs(*vals(False)), "atom_not_removed": devs(*vals(True))}
    saved = dict(KX.ELL)
    try:
        KX.ELL[1] = (KX.C + F(1, 8), -1, 0, 1)
        KX.ELL[4] = (-KX.C - F(1, 8), 0, 1, 1)
        KX._POWC.clear()
        shifted = vals(False)
    finally:
        KX.ELL.clear()
        KX.ELL.update(saved)
        KX._POWC.clear()
    out["window_shift_1_8"] = devs(*shifted)
    thr_m, thr_q = 1e-20, 1e-9
    out["thresholds"] = {"mass": thr_m, "quad": thr_q}
    out["correct_passes"] = out["correct"]["mass_dev"] < thr_m and out["correct"]["quad_dev"] < thr_q
    out["atom_not_removed_detected"] = (out["atom_not_removed"]["mass_dev"] > thr_m
                                        and out["atom_not_removed"]["quad_dev"] > thr_q)
    out["window_shift_detected"] = (out["window_shift_1_8"]["mass_dev"] > thr_m
                                    and out["window_shift_1_8"]["quad_dev"] > thr_q)
    return out


def main():
    Q.guard_drift(E0)
    t0 = time.time()
    res = {"schema": "C1B_NEGCTL/1", "drift": "1/2"}
    # a certified record (PW family, d = 4) provides w_T, the candidates and the explicit certificates
    rec = CP.certify_degree(E0, 4, BW, log=lambda *a: None)
    cx = CP.Ctx(E0, BW, log=lambda *a: None)
    wT = rec["_wT"]
    # N1
    s_bad = CP.check_supersolution(cx, CP.wscale(wT, 1 - F(1, 64)), False, "wbad")
    s_good = CP.check_supersolution(cx, wT, False, "wT")
    res["N1"] = {"good_certified": s_good["certified"], "planted_rejected": not s_bad["certified"],
                 "planted_pointwise_violation": s_bad["pointwise_refuted"],
                 "planted_residual_lo": float(s_bad["residual_lo"]),
                 "planted_centre_min": float(s_bad["residual_centre_min"])}
    # N1' / N1'' (declaration D10, guaranteed invalid)
    resT = PW.tadd(PW.tadd(cx.P(wT), cx.P(CP.wconst(1, cx.S)), -1), cx.K(wT), -1)
    Vt = PW.tadd(cx.P(wT), cx.K(wT), -1)
    Va = PW.teval(Vt, F(0), F(0), E0)
    s_half = CP.check_supersolution(cx, CP.wscale(wT, F(1, 2)), False, "whalf")
    cen = [(b[0], b[1]) for b in KX.base_cover()]
    rv = [(PW.teval(resT, p, m, E0)[0], (p, m)) for (p, m) in cen if p + m <= 4 or p == 0 or m == 0]
    rho, xs = min(rv)
    f2 = F(int((1 / (1 + rho)) * (1 << 20)), 1 << 20) - F(1, 1 << 20)
    w2 = CP.wscale(wT, f2)
    res2 = PW.tadd(PW.tadd(cx.P(w2), cx.P(CP.wconst(1, cx.S)), -1), cx.K(w2), -1)
    r2x = PW.teval(res2, xs[0], xs[1], E0)
    s_tight = CP.check_supersolution(cx, w2, False, "wtight")
    res["N1prime"] = {"V_atom": float(Va[0]), "f": 0.5, "rejected": not s_half["certified"],
                      "checker_pointwise_violation": s_half["pointwise_refuted"],
                      "residual_lo": float(s_half["residual_lo"])}
    res["N1dprime"] = {"x_star": [float(xs[0]), float(xs[1])], "rho_star": float(rho), "f": float(f2),
                       "exact_residual_at_x_star_hi": float(r2x[1]), "exact_violation_at_x_star": r2x[1] < 0,
                       "rejected": not s_tight["certified"], "checker_pointwise_violation": s_tight["pointwise_refuted"],
                       "residual_lo": float(s_tight["residual_lo"])}
    # N2
    rng = cx.enc(cx.P(wT), "wTrng")
    wsup = max(abs(rng["lo"]), abs(rng["hi"]))
    res["N2"] = n2_score(wT, wsup)
    # N3
    fl = PW.solve_chain_pw(float(E0), 4, BW)
    res["N3"] = n3_window(PW.to_exact_pw(fl["b0"], fl["_idx"]), fl["b0"], fl["_idx"])
    # N4: planted explicit L1 certificate
    q = min((x for x in rec["_quad"] if x["check"]["passed"]), key=lambda x: x["L1_bound"])
    a, b1, b2, g2c = q["_a"], q["_b1"], q["_b2"], q["_g2"]
    cc = rec["c_global"]
    K, add = cx.K, PW.tadd
    Cf = add(add(add(add(cx.P(a), cx.P(CP.wconst(cc / 2, cx.S)), -1), K(a), -1), K(b1, 1), -1), K(b2, 2), -1)
    Ca = PW.teval(Cf, F(0), F(0), E0)
    kah1 = PW.teval(PW.tadd(PW.tsubs_e(PW.KA_T, E0), PW.tsubs_e(PW.H1_T, E0)), F(0), F(0), E0)
    kappa = CP.dyadic_up(2 * Ca[1] / kah1[0], 40)
    abad = [KX.padd(a[0], {(0, 0, 0): -kappa})] + [KX.padd(x, {(0, 0, 0): -kappa}) for x in a[1:]]
    good = CP.quad_check(cx, a, b1, b2, cc / 2, g2c)
    bad = CP.quad_check(cx, abad, b1, b2, cc / 2, g2c)
    res["N4"] = {"good_passed": good["passed"], "planted_rejected": not bad["passed"],
                 "planted_pointwise_violations": bad["pointwise_violations"], "C_atom": float(Ca[0]),
                 "kappa": float(kappa)}
    # N4b: one-sided T_N certificate replaced by x~T / 2
    lb = CP.lin_check(cx, CP.wscale(rec["_c"]["xT"], F(1, 2)), wT)
    res["N4b"] = {"planted_rejected": not lb["certified"], "residual_lo": float(lb["residual_lo"])}
    res["N1_note"] = ("N1 (w_T*(1-2^-6)) is NOT guaranteed invalid (w_T carries certified residual slack); "
                      "its acceptance is correct behaviour; replaced by N1', N1'' (D10)")
    res["all_controls_detected"] = bool(res["N1prime"]["rejected"] and res["N1prime"]["checker_pointwise_violation"]
                                        and res["N1dprime"]["rejected"] and res["N1dprime"]["exact_violation_at_x_star"]
                                        and res["N2"]["true_sign_passes_all"]
                                        and res["N2"]["flipped_detected_all_points"]
                                        and res["N3"]["correct_passes"] and res["N3"]["atom_not_removed_detected"]
                                        and res["N3"]["window_shift_detected"] and res["N4"]["good_passed"]
                                        and res["N4"]["planted_rejected"] and res["N4b"]["planted_rejected"])
    res["seconds"] = round(time.time() - t0, 1)
    path = NS / "validation" / "C1B_NEGCTL.json"
    path.write_text(json.dumps(CP.jsonable(res), indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_negctl.py", "C1b negative controls N1-N4 at e=1/2",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="drift 1/2 and 1/2 +- 2^-12")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "rows"})
                      for k, v in CP.jsonable(res).items()}, indent=1)[:3000])


if __name__ == "__main__":
    main()
