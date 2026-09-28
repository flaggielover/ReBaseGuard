"""R2 supplementary block control B4' (declaration D17): a DISCRIMINANT-ONLY (i') plant with A > 0 and C >= 0
established GLOBALLY on R x block, pushed through the pinned block checker c1b_certpw.quad_check (e_r > 0).

B4 in c1b_blockctl.py is discriminant-only at its witness but its uniform shift of `a` also makes C negative
elsewhere, so it does not isolate the discriminant clause.  Here the certificate (a, b1, b2) is kept and only the
forcing constants are raised: g2' = g2 + dA, g0' = g0 + dC, so A' = A - dA and C' = C - dC UNIFORMLY while B is unchanged.
  * dA < A_lo (rigorous enclosure of A over R x block)  =>  A' > 0 everywhere;
  * dC <= max(C_lo, 0) (rigorous enclosure of C)        =>  C' >= 0 everywhere;
  * exact witness (x*, e*) in R x block with B^2 > 4 A' C'  =>  the plant is invalid (the quadratic is negative
    at mu = -B/(2A')), and ONLY the discriminant conjunct can reject it.
If no base-cover centre admits such a witness, the plant is reported NOT_CONSTRUCTIBLE (not forced).
This file is outside the pinned c1b_* set; its own sha256 is recorded in its output.
Usage: nice python3 -u -B r2_blockctl_disc.py --tight-ct --block-light   Output NS/validation/C1B_R2_BLOCKCTL_DISC.json
"""
from __future__ import annotations

import hashlib
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


def main():
    assert CP.BLOCK_LIGHT and CP.TIGHT_CT
    Q.guard_drift(LO, HI)
    t0 = time.time()
    log = lambda *a: print(*a, flush=True)
    rec = CP.certify_degree(EC, 4, BW, log=log, e_r=ER)
    assert rec["status"] == "CERTIFIED"
    cx = CP.Ctx(EC, BW, log=log, e_r=ER)
    q = min((x for x in rec["_quad"] if x["check"]["passed"]), key=lambda x: x["L1_bound"])
    a, b1, b2, g2 = q["_a"], q["_b1"], q["_b2"], q["_g2"]
    g0 = rec["c_global"] / 2
    K, P, add, S = cx.K, cx.P, PW.tadd, cx.S
    A = add(add(P(b2), P(CP.wconst(g2, S)), -1), K(b2), -1)
    B = add(add(P(b1), K(b1), -1), K(b2, 1), -2)
    Cf = add(add(add(add(P(a), P(CP.wconst(g0, S)), -1), K(a), -1), K(b1, 1), -1), K(b2, 2), -1)
    encA, encC = cx.enc(A, "A"), cx.enc(Cf, "C")
    dA = CP.dyadic_up(encA["lo"] * (1 - F(1, 1024)), 60) if encA["lo"] > 0 else F(0)
    dA = min(dA, encA["lo"] * (1 - F(1, 2048)))
    dA = F(int(dA * (1 << 60)), 1 << 60)                      # dyadic, strictly below A_lo
    dC = F(int(max(encC["lo"], F(0)) * (1 << 60)), 1 << 60)  # dyadic, <= max(C_lo, 0)
    assert dA < encA["lo"] and dC <= max(encC["lo"], F(0))
    best = None
    for bx in KX.base_cover():
        x = (bx[0], bx[1])
        if not PW.in_R(*x):
            continue
        av, bv, cv = (PW.teval(T, *x, EC) for T in (A, B, Cf))
        if bv[0] <= 0 <= bv[1]:
            continue
        bmin2 = min(bv[0] ** 2, bv[1] ** 2)
        slack = bmin2 - 4 * (av[1] - dA) * (cv[1] - dC)     # > 0  <=>  exact discriminant violation
        if best is None or slack > best[0]:
            best = (slack, x, av, bv, cv)
    out = {"schema": "C1B_R2_BLOCKCTL_DISC/1", "declaration": "PROGRESS.md D17", "block": [str(LO), str(HI)],
           "witness_drift": str(EC), "A_lo_global": float(encA["lo"]), "C_lo_global": float(encC["lo"]),
           "dA": float(dA), "dC": float(dC)}
    slack, xs, av, bv, cv = best
    if slack <= 0:
        out["status_D17"] = "NOT_CONSTRUCTIBLE"
        out["best_slack"] = float(slack)
    else:
        wit = (av[0] - dA > 0) and (cv[0] - dC >= 0) and slack > 0
        assert wit
        chk = CP.quad_check(cx, a, b1, b2, g0 + dC, g2 + dA)
        out.update({"status": "PLANTED", "x_star": [float(t) for t in xs], "witness_valid": wit,
                    "global_A_positive": True, "global_C_nonnegative": True,
                    "rejected": not chk["passed"], "n_failures": chk["n_failures"],
                    "failure_samples": chk["failures"][:3]})
        pos = CP.quad_check(cx, a, b1, b2, g0, g2)
        out["positive_control_unshifted_passed"] = pos["passed"]
    # ---------------- D17b: inflate B via b1 -> (1+lam) b1 (A unchanged; C' = C - lam K^(1) b1)
    out["D17b"] = {"ladder": ["1/8", "1/4", "1/2", "1", "2", "4"], "tried": []}
    Dq = add(P(b1), K(b1), -1)                                    # b1 - K^b1
    K1b1 = K(b1, 1)
    for lam in (F(1, 8), F(1, 4), F(1, 2), F(1), F(2), F(4)):
        Bp = add(B, Dq, lam)
        Cp = add(Cf, K1b1, -lam)
        best = None
        for bx in KX.base_cover():
            x = (bx[0], bx[1])
            if not PW.in_R(*x):
                continue
            av, bv, cv = (PW.teval(T, *x, EC) for T in (A, Bp, Cp))
            if bv[0] <= 0 <= bv[1] or av[0] <= 0 or cv[0] < 0:
                continue
            slack = min(bv[0] ** 2, bv[1] ** 2) - 4 * av[1] * cv[1]
            if best is None or slack > best[0]:
                best = (slack, x)
        ent = {"lam": str(lam), "witness_slack": float(best[0]) if best else None}
        if best and best[0] > 0:
            encCp = cx.enc(Cp, f"Cp{lam}")
            ent["C_prime_lo_global"] = float(encCp["lo"])
            ent["A_lo_global"] = float(encA["lo"])
            if encCp["lo"] >= 0 and encA["lo"] > 0:
                b1p = CP.wscale(b1, 1 + lam)
                chk = CP.quad_check(cx, a, b1p, b2, g0, g2)
                ent.update({"status": "PLANTED", "x_star": [float(t) for t in best[1]], "witness_valid": True,
                            "global_A_positive": True, "global_C_nonnegative": True,
                            "rejected": not chk["passed"], "n_failures": chk["n_failures"],
                            "failure_samples": chk["failures"][:3]})
                out["D17b"]["tried"].append(ent)
                out["D17b"]["result"] = ent
                break
        out["D17b"]["tried"].append(ent)
    out["D17b"].setdefault("result", {"status": "NOT_CONSTRUCTIBLE"})
    # ---------------- D17c: B inflation with C-margin compensation a -> a + mu w_T
    wT = rec["_wT"]
    encK1 = cx.enc(K1b1, "K1b1")
    S_up = max(abs(encK1["lo"]), abs(encK1["hi"]))
    Vf = add(P(wT), K(wT), -1)                                   # V = w_T - K^w_T >= 1 on R x block (S1)
    out["D17c"] = {"ladder": ["1", "2", "4", "8", "16", "32"], "S_up": float(S_up), "tried": []}
    for lam in (F(1), F(2), F(4), F(8), F(16), F(32)):
        mu = CP.dyadic_up(lam * S_up, 40)
        Bp = add(B, Dq, lam)
        Cp = add(add(Cf, K1b1, -lam), Vf, mu)
        best = None
        for bx in KX.base_cover():
            x = (bx[0], bx[1])
            if not PW.in_R(*x):
                continue
            av, bv, cv = (PW.teval(T, *x, EC) for T in (A, Bp, Cp))
            if bv[0] <= 0 <= bv[1] or av[0] <= 0 or cv[0] < 0:
                continue
            slack = min(bv[0] ** 2, bv[1] ** 2) - 4 * av[1] * cv[1]
            if best is None or slack > best[0]:
                best = (slack, x)
        ent = {"lam": str(lam), "mu": float(mu), "witness_slack": float(best[0]) if best else None}
        if best and best[0] > 0:
            encCp = cx.enc(Cp, f"Cc{lam}")
            ent["C_prime_lo_global"] = float(encCp["lo"])
            if encCp["lo"] >= 0 and encA["lo"] > 0:
                a_p = [KX.padd(x, y, mu) for x, y in zip(a, wT)]
                b1p = CP.wscale(b1, 1 + lam)
                chk = CP.quad_check(cx, a_p, b1p, b2, g0, g2)
                ent.update({"status": "PLANTED", "x_star": [float(t) for t in best[1]], "witness_valid": True,
                            "global_A_positive": True, "global_C_nonnegative": True,
                            "rejected": not chk["passed"], "n_failures": chk["n_failures"],
                            "disc_flag_in_samples": [f.get("discriminant_violation") for f in chk["failures"][:5]],
                            "failure_samples": chk["failures"][:3]})
                out["D17c"]["tried"].append(ent)
                out["D17c"]["result"] = ent
                break
        out["D17c"]["tried"].append(ent)
    out["D17c"].setdefault("result", {"status": "NOT_CONSTRUCTIBLE"})
    pos = CP.quad_check(cx, a, b1, b2, g0, g2)
    out["positive_control_unmodified_passed"] = pos["passed"]
    out["seconds"] = round(time.time() - t0, 1)
    out["own_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out["provenance"] = PV.provenance({"TIGHT_CT": CP.TIGHT_CT, "BLOCK_LIGHT": CP.BLOCK_LIGHT})
    (NS / "validation" / "C1B_R2_BLOCKCTL_DISC.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                           default=str) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/r2_blockctl_disc.py", "C1b block discriminant-only control B4' (C3)",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="block [1/2,17/32] only")
    print(json.dumps({k: v for k, v in out.items() if k != "provenance"}, indent=1, default=str))


if __name__ == "__main__":
    main()
