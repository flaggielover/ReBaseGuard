"""Stream A0: C2b pointwise rungs at a declared validation drift.

(U) supersolution (upper bound on Lambda(e) = E_a[tau]): the PINNED C2b pipeline ``c2b_certify.run(N, e, e, 'whole',
    'P1')`` executed verbatim.  Two recording wrappers are installed around ``c2b_certify._dyadic`` and
    ``c2b_exact.certify`` for the duration of the call; they call the originals unchanged and only keep the proposal
    g (dyadic integers) and the final exact nodal vector W, so that the certificate can be persisted and re-verified
    without the float proposal (review REVIEW_C2B_STRATEGY_R1 condition C1).

(L) P1 SUBSOLUTION (lower bound; NEW in this stream, not part of the reviewed C2b code).  Statement: for a nodal
    vector W >= 0 with P1 interpolant w on the same mesh, if for every cell T
          min_{vertices v of T} [ 1 + (K_e w)(v)_lower - w(v) ]  >=  err(T)
    with err(T) the reviewed C2b interpolation bound (c2b_exact.hessian_bounds, STRATEGY s5.3; it bounds
    |Psi - I Psi| on the cell, for ANY sign of the residual), then w <= 1 + K_e w on R.  Proof: on each simplex
    1 + Psi - w >= (1 + I Psi - w) - |Psi - I Psi|, the first term is affine and its minimum is at a vertex, where it
    is >= 1 + (K_e w)_lower(v) - w(v).  Subsolution lemma: u = G1 - w with G1 = E_.[tau] bounded (it is: a certified
    supersolution at the same drift bounds it) satisfies u >= K_e u, so u >= K_e^n u -> 0 uniformly (|K_e^n u| <=
    ||u|| P(tau > n) <= ||u|| sup G1 / n).  Hence Lambda(e) = G1(a) >= w(a).
    Family: w = c g, g = the pinned proposal V_h (>= 0), c = a / 2^CBITS chosen EXACTLY (integer arithmetic, no
    float selection) as the largest value allowed by the linear constraints; the choice is then re-checked by
    ``sub_certify`` on the final integer vector (the verification function; the selection's linearity is not trusted).

(E) NON-CERTIFIED estimate: the pinned proposal's Nystrom Lambda_h at mesh N (O(h^2) biased); Richardson is formed
    across rungs by the report.
"""
from __future__ import annotations

import time
from fractions import Fraction as F

import a0_common as A

CBITS = 40
SUB_DECREMENT_MAX = 64


def _mods():
    return A.load_c2b()


def c2b_super(e, N: int) -> dict:
    """Pinned C2b pipeline (verbatim) with W capture.  Returns record + persisted certificate object."""
    e = A.declared_drift(e)
    M = _mods()
    CE, EX = M["c2b_certify"], M["c2b_exact"]
    cap = {"g_int": None, "calls": 0, "last": None}
    orig_dyadic, orig_certify = CE._dyadic, EX.certify

    def rec_dyadic(Wf, q=CE.Q):
        out = orig_dyadic(Wf, q)
        cap["g_int"] = out
        return out

    def rec_certify(S, Wint, Q, full, want_detail=False):
        res = orig_certify(S, Wint, Q, full, want_detail)
        cap["calls"] += 1
        cap["last"] = (Wint, Q, full, res)
        return res

    CE._dyadic, EX.certify = rec_dyadic, rec_certify
    t0 = time.process_time()
    try:
        r = CE.run(N, e, None, "whole", "P1")
    finally:
        CE._dyadic, EX.certify = orig_dyadic, orig_certify
    cpu = time.process_time() - t0
    cert = r["certificate"]
    rec = {"certifier": "C2B_P1_SUPER", "drift": A.fs(e), "N": N, "kind": "whole", "family": "P1",
           "alpha_bits": CE.ALPHA_BITS, "Q": CE.Q,
           "status": "CERTIFIED" if (cert and cert.get("certified")) else "NOT_CERTIFIED",
           "alpha": r["alpha"], "beta": r["beta"], "bumps": r["bumps"], "ladder_index": r["ladder_index"],
           "cpu_seconds_pipeline": r["cpu_seconds"], "cpu_seconds": round(cpu, 2),
           "nystrom_Lambda_h_NONCERTIFIED": r["nystrom_same_mesh"]["Lambda"][0],
           "nystrom_tau_a_h_NONCERTIFIED": r["nystrom_same_mesh"]["tau_a"][0],
           "nystrom_C_T_h_NONCERTIFIED": r["nystrom_same_mesh"]["C_T"][0],
           "certify_calls": cap["calls"]}
    certobj = None
    if rec["status"] == "CERTIFIED":
        Wint, Qb, full, res = cap["last"]
        assert res is cert and full is True
        rec.update({"U": cert["w_atom"], "U_float": float(F(cert["w_atom"])), "cells_checked": cert["cells_checked"],
                    "failing_cells": cert["failing_cells"], "min_slack": cert["min_slack"],
                    "max_err_float": cert["max_err_float"], "w_max": cert["w_max"]})
        certobj = make_cert("C2B_P1_SUPER", e, N, Qb, Wint, F(cert["w_atom"]))
    return {"record": rec, "cert": certobj, "g_int": cap["g_int"]}


# ------------------------------------------------------------------------------------------------ subsolution
def sub_certify(S, Wint, Qb: int, full: bool = True) -> dict:
    """Exact P1 SUBSOLUTION check (see module docstring).  w = Wint * 2^-Qb.  Pointwise (S.J == 0) only."""
    M = _mods()
    EX = M["c2b_exact"]
    P = EX.P
    if S.J != 0:
        raise ValueError("sub_certify: pointwise drift only in this stream")
    if any(Wint[i][j] < 0 for (i, j) in S.mesh.nodes):
        return {"certified": False, "reason": "negative nodal value"}
    one = 1 << (P + Qb)
    Kw = EX.kernel_nodes(S, Wint, 0, full, upper=False)                    # rigorous LOWER bounds of K_e w
    defect = {x: one + Kw[x] - (Wint[x[0]][x[1]] << P) for x in Kw}        # lower bounds of 1 + K w - w
    Hb = EX.hessian_bounds(S, Wint, full)
    fails, worst, cells = 0, None, 0
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        cells += 1
        vmin = min(defect[v] for v in cell[8])
        slack = vmin - err
        if slack < 0:
            fails += 1
        if worst is None or slack < worst:
            worst = slack
    scale = F(1, 1 << (P + Qb))
    return {"certified": fails == 0, "failing_cells": fails, "cells_checked": cells,
            "min_slack": A.fs(worst * scale), "min_slack_float": float(worst * scale),
            "w_atom": A.fs(F(Wint[0][0], 1 << Qb)), "w_atom_float": Wint[0][0] / 2 ** Qb}


def c2b_sub(e, N: int, g_int, Qg: int) -> dict:
    """Exact selection of c = a / 2^CBITS for w = c g, then sub_certify on the final vector (decrement a if needed)."""
    e = A.declared_drift(e)
    M = _mods()
    EX = M["c2b_exact"]
    P = EX.P
    t0 = time.process_time()
    S = EX.Setup(N, e)
    Kg = EX.kernel_nodes(S, g_int, 0, True, upper=False)
    d = {x: Kg[x] - (g_int[x[0]][x[1]] << P) for x in Kg}                  # scale 2^-(P+Qg)
    Hb = EX.hessian_bounds(S, g_int, True)
    one_big = 1 << (P + Qg + CBITS)
    eight_n2 = 8 * N * N
    # per cell: one_big + a * min_v d_v >= ceil(a * E_c / 8N^2), E_c = err numerator of g; E_c/8N^2 - min d > 0
    a_best = None
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        ry = (cell[5] - cell[4]) + je
        E = Hss + 2 * ry * Hsy + ry * ry * Hyy
        dmin = min(d[v] for v in cell[8])
        denom = E - eight_n2 * dmin                   # = 8N^2 (E/8N^2 - dmin) > 0
        if denom <= 0:
            continue                                  # this cell never binds (cannot happen for g ~ 1 + K g)
        a_c = ((one_big - 1) * eight_n2) // denom
        a_best = a_c if a_best is None else min(a_best, a_c)
    a = min(a_best, 1 << CBITS) if a_best is not None else (1 << CBITS)
    t_sel = time.process_time() - t0
    res, dec = None, 0
    while a > 0 and dec <= SUB_DECREMENT_MAX:
        W = [[a * x for x in col] for col in g_int]
        res = sub_certify(S, W, Qg + CBITS, True)
        if res["certified"]:
            break
        a -= 1 + (a >> 30)
        dec += 1
    cpu = time.process_time() - t0
    rec = {"certifier": "C2B_P1_SUB", "drift": A.fs(e), "N": N, "kind": "whole", "cbits": CBITS,
           "status": "CERTIFIED" if (res and res["certified"]) else "NOT_CERTIFIED",
           "c": A.fs(F(a, 1 << CBITS)), "one_minus_c_float": float(1 - F(a, 1 << CBITS)), "decrements": dec,
           "cpu_seconds": round(cpu, 2), "cpu_seconds_selection": round(t_sel, 2)}
    certobj = None
    if rec["status"] == "CERTIFIED":
        rec.update({"L": res["w_atom"], "L_float": float(F(res["w_atom"])), "cells_checked": res["cells_checked"],
                    "failing_cells": res["failing_cells"], "min_slack": res["min_slack"]})
        certobj = make_cert("C2B_P1_SUB", e, N, Qg + CBITS, W, F(res["w_atom"]))
    return {"record": rec, "cert": certobj}


# ------------------------------------------------------------------------------------------------ persistence
def w_sha256(W) -> str:
    return A.sha256_bytes(A.canon([[str(x) for x in col] for col in W]))


def make_cert(kind: str, e, N: int, Qb: int, W, claim: F) -> dict:
    return {"schema": "A0_CERT/1", "certifier": kind, "drift": A.fs(e), "N": N, "kind": "whole", "Qbits": Qb,
            "W": [[str(x) for x in col] for col in W], "W_sha256": w_sha256(W), "claim_w_atom": A.fs(claim),
            "statement": ("E_a[tau](e) <= claim_w_atom (P1 supersolution, C2b)" if kind == "C2B_P1_SUPER" else
                          "E_a[tau](e) >= claim_w_atom (P1 subsolution, stream A0)"),
            "latent_proxy": "validation-drift certificate; keep inside streams/A0 (T1/T2)"}
