"""Stream A0: C1b pointwise rungs at a declared validation drift (pinned C1b code, loaded by a0_common.load_c1b).

W-ONLY rung (``c1b_w_rung``): the whole-kernel part of the pinned ``c1b_certpw.certify_degree`` -- the untrusted float
candidate W (strip-piecewise degree d, LS collocation, whole kernel), its exact dyadic rounding, the rigorous residual
enclosure, the D1 scaling eta_W, the pinned supersolution check (S2, ``check_supersolution(..., whole=True)``), and the
pinned Lambda_lo formula -- composed from the pinned functions with the same arguments and the same order.  It skips
the taboo, derivative, one-sided and assembly parts, which do not enter A_bar or Lambda_lo.  ``c1b_full_rung`` runs the
pinned ``certify_degree`` itself; the cross-check job asserts EXACT equality of A_bar, Lambda_lo and eta_W between the
two paths (so the W-only composition is validated against the reviewed path, not assumed).

Flags: TIGHT_CT = True, BLOCK_LIGHT = False (the flags of the overnight R2 point rungs C1B_R2_PW_POINT_*; TIGHT_CT does
not enter the whole-kernel W path; BLOCK_LIGHT = False keeps the default enclosure depth, extra_levels = 4).
"""
from __future__ import annotations

import time
from fractions import Fraction as F

import a0_common as A


def _mods():
    return A.load_c1b(tight_ct=True, block_light=False)


def c1b_w_rung(e, d: int) -> dict:
    e = A.declared_drift(e)
    M = _mods()
    cp, PW, FL = M["c1b_certpw"], M["c1b_pw"], M["c1b_float"]
    BW = PW.BW_PW
    lines: list = []
    t0 = time.process_time()
    cx = cp.Ctx(e, BW, lines.append)                         # Ctx calls the (shimmed) guard_drift itself
    D = PW.DiscPW(float(e), d, BW)
    qw = FL.QR(D.matrix(True))
    Wf = D.split(qw.solve([1.0] * len(D.pts)))                # == solve_chain_pw(e, d, BW)["W"] (same operations)
    cW = PW.to_exact_pw(Wf, D.idx)
    t_float = time.process_time() - t0
    res = PW.tadd(PW.tadd(cx.P(cW), cx.P(cp.wconst(1, cx.S)), -1), cx.K(cW, 0, True), -1)
    encW = cx.enc(res, "W")
    rWlo, rWhi = encW["lo"], encW["hi"]
    rec = {"certifier": "C1B_PW_W_SUPER", "drift": A.fs(e), "degree": d, "BW": list(BW), "flags": dict(M["_flags"]),
           "residual_lo": float(rWlo), "residual_hi": float(rWhi), "residual_boxes": encW["boxes"]}
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
                "eta_W": A.fs(etaW), "eta_W_float": float(etaW),
                "check_residual_lo": float(sW["residual_lo"]), "check_w_min_lo": float(sW["w_min_lo"]),
                "check_boxes": sW["boxes"], "cpu_seconds": round(cpu, 2), "cpu_seconds_float": round(t_float, 2),
                "W_atom_candidate_float_NONCERTIFIED": float(Wa)})
    certobj = None
    if sW["certified"]:
        rec.update({"U": A.fs(Abar), "U_float": float(Abar), "L": A.fs(Lam_lo), "L_float": float(Lam_lo),
                    "C_R_sup_W": A.fs(sW["w_max_hi"])})
        certobj = make_cert(e, d, BW, W, Abar)
    return {"record": rec, "cert": certobj}


def c1b_full_rung(e, d: int) -> dict:
    """The pinned certify_degree (reviewed path), for the exact-equality cross-check of the W-only composition."""
    e = A.declared_drift(e)
    M = _mods()
    cp, PW = M["c1b_certpw"], M["c1b_pw"]
    lines: list = []
    t0 = time.process_time()
    r = cp.certify_degree(e, d, PW.BW_PW, log=lines.append)
    cpu = time.process_time() - t0
    out = {"drift": A.fs(e), "degree": d, "status": r["status"], "cpu_seconds": round(cpu, 2)}
    if r["status"] == "CERTIFIED":
        out.update({"A_bar": A.fs(r["A_bar"]), "Lambda_lo": A.fs(r["Lambda_lo"]), "eta_W": A.fs(r["eta_W"]),
                    "C_R": A.fs(r["C_R"])})
    return out


# ------------------------------------------------------------------------------------------------ persistence
def poly_ser(P: dict) -> list:
    return [[i, j, k, A.fs(v)] for (i, j, k), v in sorted(P.items())]


def poly_de(L: list) -> dict:
    return {(int(i), int(j), int(k)): F(v) for i, j, k, v in L}


def w_sha256(Wser) -> str:
    return A.sha256_bytes(A.canon(Wser))


def make_cert(e, d: int, BW, W, claim: F) -> dict:
    Wser = [poly_ser(P) for P in W]
    return {"schema": "A0_CERT/1", "certifier": "C1B_PW_W_SUPER", "drift": A.fs(e), "degree": d, "BW": list(BW),
            "W": Wser, "W_sha256": w_sha256(Wser), "claim_w_atom": A.fs(claim),
            "statement": "E_a[tau](e) <= claim_w_atom (strip-piecewise polynomial whole-kernel supersolution, C1b S2)",
            "latent_proxy": "validation-drift certificate; keep inside streams/A0 (T1/T2)"}
