"""Stream A0: C2b rung with EXACT-SCALE selection for BOTH directions (written after the first batch-1 result showed
that, at mesh N = 80, the pinned C2b alpha grid 2^-12 (c2b_certify.ALPHA_BITS) is the binding resolution while the
certified interpolation term is an order of magnitude smaller; the same effect was recorded by the C2b author at
N = 40 (C2B_ROUTE_SUMMARY s2.1, "the alpha-ladder step 2^-12 is the binding resolution").  Evidence: validation drifts
only.)

  proposal    g = the pinned C2b proposal (c2b_certify.proposal + c2b_certify._dyadic, verbatim): V_h at mesh N.
  upper       w = a g / 2^CBITS with the SMALLEST integer a allowed by the exact per-cell constraints
                  a * min_v (g - (K g)_upper)_v - 2^(P+Q+CBITS) >= ceil(a * E_c / 8N^2)
              (linearity of the pinned vertex evaluator and interpolation bound in W >= 0), then CERTIFIED BY THE
              PINNED CHECKER c2b_exact.certify on the final integer vector (bump a upward, <= BUMP_MAX times).
              The selection is only a proposal: soundness rests on c2b_exact.certify (reviewed, REVIEW_C2B_STRATEGY_R1).
  lower       w = a g / 2^CBITS with the LARGEST a (a0_c2b.c2b_sub rule), checked by a0_c2b.sub_certify.
The certificate objects have the same statement and format as a0_c2b's (certifier C2B_P1_SUPER / C2B_P1_SUB) and are
re-verified by a0_verify.verify_certificate like every other certificate.
"""
from __future__ import annotations

import time
from fractions import Fraction as F

import a0_common as A
import a0_c2b as C2

CBITS = 40
BUMP_MAX = 64


def c2bx_rung(e, N: int) -> dict:
    e = A.declared_drift(e)
    M = A.load_c2b()
    CE, EX = M["c2b_certify"], M["c2b_exact"]
    P, Q = EX.P, CE.Q
    t0 = time.process_time()
    g, sols = CE.proposal(N, e, e, "whole")                 # pinned (guard inside FloatKernel callers: Setup below)
    g_int = CE._dyadic(g)
    t_prop = time.process_time() - t0
    S = EX.Setup(N, e)                                      # pinned; calls the (shimmed) guard
    t_setup = time.process_time() - t0 - t_prop
    Hb = EX.hessian_bounds(S, g_int, True)
    Kup = EX.kernel_nodes(S, g_int, 0, True, upper=True)
    Klo = EX.kernel_nodes(S, g_int, 0, True, upper=False)
    eight_n2 = 8 * N * N
    one_big = 1 << (P + Q + CBITS)
    a_up, a_lo = 1 << CBITS, 1 << CBITS
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        ry = (cell[5] - cell[4]) + je
        E = Hss + 2 * ry * Hsy + ry * ry * Hyy
        verts = cell[8]
        Dmin = min((g_int[v[0]][v[1]] << P) - Kup[v] for v in verts)          # g - K_up g   (scale 2^-(P+Q))
        den = eight_n2 * Dmin - E
        if den <= 0:
            a_up = None
            break
        a_c = -((-(eight_n2 * (one_big + 1))) // den)
        a_up = max(a_up, a_c)
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        ry = (cell[5] - cell[4]) + je
        E = Hss + 2 * ry * Hsy + ry * ry * Hyy
        dmin = min(Klo[v] - (g_int[v[0]][v[1]] << P) for v in cell[8])
        den = E - eight_n2 * dmin
        if den > 0:
            a_lo = min(a_lo, ((one_big - 1) * eight_n2) // den)
    t_sel = time.process_time() - t0 - t_prop - t_setup
    # ---- upper: pinned checker
    res_u, bumps = None, 0
    if a_up is not None:
        while bumps <= BUMP_MAX:
            Wu = [[a_up * x for x in col] for col in g_int]
            res_u = EX.certify(S, Wu, Q + CBITS, True)
            if res_u["certified"]:
                break
            a_up += 1 + (a_up >> 30)
            bumps += 1
    t_u = time.process_time() - t0 - t_prop - t_setup - t_sel
    # ---- lower: A0 subsolution checker
    res_l, dec = None, 0
    while a_lo > 0 and dec <= BUMP_MAX:
        Wl = [[a_lo * x for x in col] for col in g_int]
        res_l = C2.sub_certify(S, Wl, Q + CBITS, True)
        if res_l["certified"]:
            break
        a_lo -= 1 + (a_lo >> 30)
        dec += 1
    cpu = time.process_time() - t0
    up_ok = bool(res_u and res_u["certified"])
    lo_ok = bool(res_l and res_l["certified"])
    rec = {"certifier": "C2B_P1_EXACT_SCALE", "drift": A.fs(e), "N": N, "cbits": CBITS,
           "status_U": "CERTIFIED" if up_ok else "NOT_CERTIFIED", "status_L": "CERTIFIED" if lo_ok else "NOT_CERTIFIED",
           "alpha_up": A.fs(F(a_up, 1 << CBITS)) if a_up else None,
           "alpha_up_minus_1": float(F(a_up, 1 << CBITS) - 1) if a_up else None, "bumps_up": bumps,
           "c_lo": A.fs(F(a_lo, 1 << CBITS)), "one_minus_c_lo": float(1 - F(a_lo, 1 << CBITS)), "decrements_lo": dec,
           "nystrom_Lambda_h_NONCERTIFIED": sols[0]["Lambda"], "nystrom_iterations": sols[0]["iterations"],
           "cpu_seconds": {"proposal": round(t_prop, 2), "setup_gauss": round(t_setup, 2),
                           "selection_hessian_kernels": round(t_sel, 2), "certify_upper": round(t_u, 2),
                           "certify_lower": round(cpu - t_prop - t_setup - t_sel - t_u, 2), "total": round(cpu, 2)}}
    certs = {}
    if up_ok:
        rec.update({"U": res_u["w_atom"], "U_float": float(F(res_u["w_atom"])), "min_slack_U": res_u["min_slack"],
                    "cells_checked": res_u["cells_checked"]})
        cu = C2.make_cert("C2B_P1_SUPER", e, N, Q + CBITS, Wu, F(res_u["w_atom"]))
        cu["selection"] = "A0_EXACT_SCALE"
        certs["super"] = cu
    if lo_ok:
        rec.update({"L": res_l["w_atom"], "L_float": float(F(res_l["w_atom"])), "min_slack_L": res_l["min_slack"]})
        cl = C2.make_cert("C2B_P1_SUB", e, N, Q + CBITS, Wl, F(res_l["w_atom"]))
        cl["selection"] = "A0_EXACT_SCALE"
        certs["sub"] = cl
    return {"record": rec, "certs": certs}
