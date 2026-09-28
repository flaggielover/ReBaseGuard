"""Stream A0: C1b W-only rung on the DYADIC HULL of a non-dyadic declared drift.

Finding that motivated it (batch 1): the pinned C1b integer Taylor models require dyadic drift data
(c1b_kernel._dy_exp / to_int_gf raise "G-form coefficient not on the 2^-SC grid" when a non-dyadic drift such as
11/10 or 27/10 is substituted pointwise).  The pointwise C1b rung therefore FAILS CLOSED (exception, no value) at every
non-dyadic drift.  The cell-307 campaign handled the same limitation with an outward 2^-20 hull (its rule P2).

Here: [lo, hi] = [floor(e 2^B) / 2^B, ceil(e 2^B) / 2^B] with B = HULL_BITS (so lo < e < hi, width 2^-B, dyadic centre
and radius), and the pinned block path of the same functions (Ctx(e_c, BW, e_r) with e_r = 2^-(B+1); cx.K keeps e
symbolic; enclosures are over R x [lo, hi]).  The statement is block-uniform on the hull, hence valid at e:
    for every e' in [lo, hi]:  E_a[tau](e') <= A_bar,   and  Lambda_lo <= E_a[tau](e').
Guards: the hull is checked to contain the declared drift, to have width exactly 2^-B, and it passes BOTH quarantine
guards as an interval (and again inside Ctx through the shim).  Flags as in a0_c1b (TIGHT_CT True, BLOCK_LIGHT False).
"""
from __future__ import annotations

import math
import time
from fractions import Fraction as F

import a0_common as A
import a0_c1b as C1

HULL_BITS = 20


def hull_of(e: F, bits: int = HULL_BITS):
    s = 1 << bits
    lo, hi = F(math.floor(e * s), s), F(math.ceil(e * s), s)
    if lo == hi:
        raise ValueError("drift is dyadic at this resolution: use the pointwise rung")
    return lo, hi


def c1b_hull_rung(e, d: int) -> dict:
    e = A.declared_drift(e)
    lo, hi = hull_of(e)
    assert lo < e < hi and hi - lo == F(1, 1 << HULL_BITS)
    A.C.guard_drift(lo, hi)
    A._OVQ.guard_drift(lo, hi)
    M = A.load_c1b(tight_ct=True, block_light=False)
    cp, PW, FL = M["c1b_certpw"], M["c1b_pw"], M["c1b_float"]
    BW = PW.BW_PW
    e_c, e_r = (lo + hi) / 2, (hi - lo) / 2
    lines: list = []
    t0 = time.process_time()
    cx = cp.Ctx(e_c, BW, lines.append, e_r)
    D = PW.DiscPW(float(e_c), d, BW)                    # e-free candidate solved at the hull midpoint (D12 rule)
    qw = FL.QR(D.matrix(True))
    Wf = D.split(qw.solve([1.0] * len(D.pts)))
    cW = PW.to_exact_pw(Wf, D.idx)
    t_float = time.process_time() - t0
    res = PW.tadd(PW.tadd(cx.P(cW), cx.P(cp.wconst(1, cx.S)), -1), cx.K(cW, 0, True), -1)
    encW = cx.enc(res, "W")
    rWlo, rWhi = encW["lo"], encW["hi"]
    rec = {"certifier": "C1B_PW_W_SUPER_HULL", "drift": A.fs(e), "hull": [A.fs(lo), A.fs(hi)], "degree": d,
           "BW": list(BW), "flags": dict(M["_flags"]), "residual_lo": float(rWlo), "residual_hi": float(rWhi),
           "residual_boxes": encW["boxes"]}
    if rWlo <= -1:
        rec.update({"status": "SCALING_RULE_INAPPLICABLE", "cpu_seconds": round(time.process_time() - t0, 2)})
        return {"record": rec, "cert": None}
    etaW = F(0) if rWlo >= 0 else cp.dyadic_up(-rWlo / (1 + rWlo))
    W = cp.wscale(cW, 1 + etaW)
    sW = cp.check_supersolution(cx, W, True, "W")
    cpu = time.process_time() - t0
    Abar, Wa = cp.at_atom(W), cp.at_atom(cW)
    zW = F(0) if rWhi <= 0 else cp.dyadic_up(rWhi / (1 + rWhi))
    Lam_lo = max(Wa - Abar * max(rWhi, F(0)), (1 - zW) * Wa)
    rec.update({"status": "CERTIFIED" if sW["certified"] else "SUPERSOLUTION_NOT_CERTIFIED",
                "eta_W": A.fs(etaW), "eta_W_float": float(etaW), "check_boxes": sW["boxes"],
                "cpu_seconds": round(cpu, 2), "cpu_seconds_float": round(t_float, 2)})
    cert = None
    if sW["certified"]:
        rec.update({"U": A.fs(Abar), "U_float": float(Abar), "L": A.fs(Lam_lo), "L_float": float(Lam_lo)})
        cert = C1.make_cert(e, d, BW, W, Abar)
        cert["certifier"] = "C1B_PW_W_SUPER_HULL"
        cert["hull"] = [A.fs(lo), A.fs(hi)]
        cert["statement"] = ("for every e' in hull: E_a[tau](e') <= claim_w_atom (block-uniform C1b S2 on the dyadic "
                             "hull of the declared drift)")
    return {"record": rec, "cert": cert}
