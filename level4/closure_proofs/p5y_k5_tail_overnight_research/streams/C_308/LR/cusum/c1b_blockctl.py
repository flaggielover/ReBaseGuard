"""C1b block-path negative controls (REVIEW_RLR_R2 condition C3, declaration D15).  Block [1/2, 17/32], PW_4 (D12),
D11 light settings.  Every plant is pushed through the BLOCK (e_r > 0) checkers of c1b_certpw; every invalidity is
witnessed EXACTLY (rigorous interval of the planted residual / quadratic at a point of R and the interior drift
e* = 33/64) and the witness is asserted in code.

  B0  positive: the certified block w_T (supersolution) and explicit L1 (i') certificate are ACCEPTED.
  B1  supersolution: w' = (1 - eps) w_T                         -> exact residual'(atom, e*) < 0
  B2  interior-drift-only: w'' = w_T - c psi(e), psi = 1 - ((e - e_c)/e_r)^2 (0 at both block ends)
      residual'' = residual - c psi (k_a + h1)                   -> exact residual''(atom, e_c) < 0; at both block ends
      residual'' equals the certified residual (point checkers at the two ends must ACCEPT it)
  B3  (i') C-conjunct: a' = a - kappa                            -> exact C'(atom, e*) < 0
  B4  (i') discriminant only: a'' = a - kappa'' at a witness x* in R -> exact A > 0, C'' >= 0, B^2 > 4 A C''
Usage: nice python3 -u -B c1b_blockctl.py --tight-ct --block-light      Output NS/validation/C1B_R2_BLOCKCTL.json
"""
from __future__ import annotations

import json
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
import c1b_kernel as KX  # noqa: E402
import c1b_prov as PV  # noqa: E402
import c1b_pw as PW  # noqa: E402

LO, HI = F(1, 2), F(17, 32)
EC, ER = (LO + HI) / 2, (HI - LO) / 2
BW = PW.BW_PW
ATOM = (F(0), F(0))


def tmul_poly(T: tuple, P: dict) -> tuple:
    """multiply every term of a per-region G-form tuple by the polynomial P(p, m, e)."""
    return tuple({k: KX.pmul(v, P) for k, v in g.items()} for g in T)


def main():
    assert CP.BLOCK_LIGHT and CP.TIGHT_CT, "run with --tight-ct --block-light (declared D11/D12 settings)"
    Q.guard_drift(LO, HI)
    t0 = time.time()
    log = lambda *a: print(*a, flush=True)
    res = {"schema": "C1B_R2_BLOCKCTL/1", "block": [str(LO), str(HI)], "witness_drift": str(EC),
           "declarations": "PROGRESS.md D11, D12, D15"}
    rec = CP.certify_degree(EC, 4, BW, log=log, e_r=ER)
    assert rec["status"] == "CERTIFIED", rec["status"]
    cx = CP.Ctx(EC, BW, log=log, e_r=ER)
    S = cx.S
    wT = rec["_wT"]
    one = CP.wconst(1, S)
    resT = PW.tadd(PW.tadd(cx.P(wT), cx.P(one), -1), cx.K(wT), -1)
    mform = PW.tadd(cx.P(one), cx.K(one), -1)                     # k_a + h1 = 1 - K^1 (block form, e symbolic)
    # ---------------- B0 positive controls
    s0 = CP.check_supersolution(cx, wT, False, "B0_wT")
    q = min((x for x in rec["_quad"] if x["check"]["passed"]), key=lambda x: x["L1_bound"])
    a, b1, b2, g2 = q["_a"], q["_b1"], q["_b2"], q["_g2"]
    g0 = rec["c_global"] / 2
    q0 = CP.quad_check(cx, a, b1, b2, g0, g2)
    res["B0_positive"] = {"wT_certified": s0["certified"], "L1_quad_passed": q0["passed"]}
    # ---------------- B1 supersolution violation
    V = PW.teval(PW.tadd(cx.P(wT), cx.K(wT), -1), *ATOM, EC)     # V = w_T - K^w_T at (atom, e*)
    eps = CP.dyadic_up(1 - 1 / V[1], 40) + F(1, 1 << 20)
    w1 = CP.wscale(wT, 1 - eps)
    r1 = PW.teval(PW.tadd(PW.tadd(cx.P(w1), cx.P(one), -1), cx.K(w1), -1), *ATOM, EC)
    assert r1[1] < 0, "B1 plant not guaranteed invalid"
    s1 = CP.check_supersolution(cx, w1, False, "B1")
    res["B1_supersolution"] = {"eps": float(eps), "witness_residual_hi": float(r1[1]), "witness_valid": r1[1] < 0,
                               "rejected": not s1["certified"], "checker_pointwise": s1["pointwise_refuted"]}
    # ---------------- B2 interior-drift-only violation (e-dependent plant, residual form pushed through enclose_t)
    psi = {(0, 0, 0): 1 - EC * EC / (ER * ER), (0, 0, 1): 2 * EC / (ER * ER), (0, 0, 2): -1 / (ER * ER)}
    assert KX.peval(psi, 0, 0, LO) == 0 and KX.peval(psi, 0, 0, HI) == 0 and KX.peval(psi, 0, 0, EC) == 1
    rT_c = PW.teval(resT, *ATOM, EC)
    m_c = PW.teval(mform, *ATOM, EC)
    assert m_c[0] > 0
    cc2 = CP.dyadic_up(2 * max(rT_c[1], F(0)) / m_c[0], 40) + F(1, 1 << 20)
    res2 = PW.tadd(resT, tmul_poly(mform, psi), -cc2)
    w2 = PW.teval(res2, *ATOM, EC)
    assert w2[1] < 0, "B2 plant not guaranteed invalid at the interior drift"
    enc2 = cx.enc(res2, "B2")
    end_ok = []
    for ep in (LO, HI):                                          # at the block ends residual'' = certified residual
        cxp = CP.Ctx(ep, BW, log=log)
        encp = cxp.enc(PW.tsubs_e(res2, ep), f"B2@{ep}")
        end_ok.append(encp["lo"] >= 0)
    res["B2_interior_drift_only"] = {"c": float(cc2), "witness_residual_hi_at_e_c": float(w2[1]),
                                     "witness_valid": w2[1] < 0, "rejected_by_block_checker": enc2["lo"] < 0,
                                     "block_lower_bound": float(enc2["lo"]),
                                     "accepted_by_point_checker_at_both_ends": all(end_ok),
                                     "checker_pointwise_R": enc2["centre_min_R"] is not None and enc2["centre_min_R"] < 0}
    # ---------------- B3 (i') C-conjunct violation
    K, P, add = cx.K, cx.P, PW.tadd

    def forms(aa, bb1, bb2):
        A = add(add(P(bb2), P(CP.wconst(g2, S)), -1), K(bb2), -1)
        B = add(add(P(bb1), K(bb1), -1), K(bb2, 1), -2)
        Cf = add(add(add(add(P(aa), P(CP.wconst(g0, S)), -1), K(aa), -1), K(bb1, 1), -1), K(bb2, 2), -1)
        return A, B, Cf

    A, B, Cf = forms(a, b1, b2)
    Ca = PW.teval(Cf, *ATOM, EC)
    ma = PW.teval(mform, *ATOM, EC)
    assert Ca[0] > 0, "B3 precondition C(atom, e*) > 0"
    kap = CP.dyadic_up(2 * Ca[1] / ma[0], 40)
    a3 = [KX.padd(x, {(0, 0, 0): -kap}) for x in a]
    C3 = PW.teval(forms(a3, b1, b2)[2], *ATOM, EC)
    assert C3[1] < 0
    q3 = CP.quad_check(cx, a3, b1, b2, g0, g2)
    res["B3_C_conjunct"] = {"kappa": float(kap), "witness_C_hi": float(C3[1]), "witness_valid": C3[1] < 0,
                            "rejected": not q3["passed"], "checker_pointwise": q3["pointwise_violations"]}
    # ---------------- B4 discriminant-only violation
    best = None
    for bx in KX.base_cover():
        x = (bx[0], bx[1])
        if not PW.in_R(*x):
            continue
        av, bv, cv = (PW.teval(T, *x, EC) for T in (A, B, Cf))
        if bv[0] <= 0 <= bv[1] or av[0] <= 0:
            continue
        bmin2 = min(bv[0] ** 2, bv[1] ** 2)
        score = bmin2 / (4 * av[1])
        if best is None or score > best[0]:
            best = (score, x, av, bv, cv)
    score, xs, av, bv, cv = best
    mx = PW.teval(mform, *xs, EC)
    kap4 = CP.dyadic_up((cv[1] - score / 2) / mx[0], 60)          # C''(x*) ~ score/2 in (0, B^2/(4A))
    a4 = [KX.padd(x, {(0, 0, 0): -kap4}) for x in a]
    A4, B4, C4 = (PW.teval(T, *xs, EC) for T in forms(a4, b1, b2))
    b4min2 = min(B4[0] ** 2, B4[1] ** 2) if not (B4[0] <= 0 <= B4[1]) else F(0)
    wit4 = A4[0] > 0 and C4[0] >= 0 and b4min2 > 4 * A4[1] * C4[1]
    assert wit4, "B4 plant is not a guaranteed discriminant-only violation"
    q4 = CP.quad_check(cx, a4, b1, b2, g0, g2)
    res["B4_discriminant_only"] = {"x_star": [float(t) for t in xs], "A_lo": float(A4[0]), "C_lo": float(C4[0]),
                                   "C_hi": float(C4[1]), "B_min_sq": float(b4min2), "witness_valid": wit4,
                                   "rejected": not q4["passed"], "checker_pointwise": q4["pointwise_violations"]}
    res["all_block_controls"] = bool(
        res["B0_positive"]["wT_certified"] and res["B0_positive"]["L1_quad_passed"]
        and res["B1_supersolution"]["witness_valid"] and res["B1_supersolution"]["rejected"]
        and res["B2_interior_drift_only"]["witness_valid"] and res["B2_interior_drift_only"]["rejected_by_block_checker"]
        and res["B2_interior_drift_only"]["accepted_by_point_checker_at_both_ends"]
        and res["B3_C_conjunct"]["witness_valid"] and res["B3_C_conjunct"]["rejected"]
        and res["B4_discriminant_only"]["witness_valid"] and res["B4_discriminant_only"]["rejected"])
    res["seconds"] = round(time.time() - t0, 1)
    res["provenance"] = PV.provenance({"TIGHT_CT": CP.TIGHT_CT, "BLOCK_LIGHT": CP.BLOCK_LIGHT})
    path = NS / "validation" / "C1B_R2_BLOCKCTL.json"
    path.write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_blockctl.py", "C1b block-path negative controls B0-B4 (C3)",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes="block [1/2,17/32] and its endpoints only; guard_drift passed")
    print(json.dumps({k: v for k, v in res.items() if k != "provenance"}, indent=1, default=str))


if __name__ == "__main__":
    main()
