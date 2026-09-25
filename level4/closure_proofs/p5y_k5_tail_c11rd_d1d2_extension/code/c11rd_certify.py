"""C11RD -- the D1/D2 certifier: cover, adaptive refinement, error propagation, bounds.

THEOREM USED (theory/D1_D2_DERIVATION.md, Theorem 4). Let E_j be a drift interval on which, for every
e, Ghat_e 1 <= w on R with sup_R w <= C_T and w(a) <= tau (the ACCEPTED C11R F_H premise), and let
D0(e), D1(e), D2(e) be the e-Taylor candidates with residuals |r_k(x, e)| <= lam_k on R x E_j. Then
for every e in E_j, with kappa_1 = 2 phi(0), kappa_2 = 4 phi(1),

    n0 = C_T lam0,   n1 = C_T (lam1 + kappa_1 n0)
    |d'_e(a)|  <= |D1(e)(a)| + tau (lam1 + kappa_1 n0)                                  =: D1 bound
    |d''_e(a)| <= |D2(e)(a)| + tau (lam2 + 2 kappa_1 n1 + kappa_2 n0)                   =: D2 bound

and the cell statement is the MAXIMUM over the sub-blocks E_j, which tile the cell block exactly.
The lam_k come from Taylor-model enclosures on a box cover of R (bands 0-3: strips in (s, theta);
band 4: the two axis segments), refined by bisection until each box meets the frozen tolerance or
the frozen maximum depth; the maximum over the LEAF boxes is used whether or not every tolerance was
met (the refinement rule only affects tightness, never soundness).
"""
from __future__ import annotations

import time
from fractions import Fraction as F

import c11rd_float as FL
import c11rd_kernel as KR
import c11rd_model as MD
import c11rd_tm as T


def initial_boxes(e_lo: F, e_hi: F, splits: dict, order: int) -> list:
    """Band-aligned cover of R: band k in 0-3 as the (s, theta) strip split splits['s'] x
    splits['theta'][k] (the theta split grows with the band so that boxes have comparable PHYSICAL
    size: a theta-width dt at s spans s dt / 2 in p and m); band 4 as the two axis segments split
    splits['s4']."""
    out = []
    ns, n4 = splits["s"], splits["s4"]
    for k in range(4):
        nt = splits["theta"][k]
        for a in range(ns):
            s0, s1 = F(k) + F(a, ns), F(k) + F(a + 1, ns)
            for b in range(nt):
                t0, t1 = F(-1) + F(2 * b, nt), F(-1) + F(2 * (b + 1), nt)
                out.append(KR.Box(k, (s0, s1), (e_lo, e_hi), theta=(t0, t1), order=order))
    for ax in ("p", "m"):
        for a in range(n4):
            s0, s1 = F(4) + F(a, n4), F(4) + F(a + 1, n4)
            out.append(KR.Box(4, (s0, s1), (e_lo, e_hi), axis=ax, order=order))
    return out


def refine_box(bx: KR.Box, cands: list, params: dict) -> dict:
    """One initial box and its refinement subtree: bisect while some residual bound exceeds its
    frozen tolerance and the depth is below the frozen maximum; lam_k = max over the LEAVES (every
    leaf counts, whether or not it met its tolerance -- the rule affects tightness, not soundness)."""
    tol = [F(x) for x in params["tolerances"]]
    queue = [(bx, 0)]
    lam, leaves, evaluated, unmet, worst = [F(0)] * 3, 0, 0, 0, [None] * 3
    while queue:
        b, depth = queue.pop()
        R = KR.residuals_box(b, cands, J=params["moment_terms"])
        evaluated += 1
        v = [R["r0"].abs_upper(), R["r1"].abs_upper(), R["r2"].abs_upper()]
        over = any(v[i] > tol[i] for i in range(3))
        if over and depth < params["max_depth"]:
            queue.extend((c, depth + 1) for c in b.split())
            continue
        leaves += 1
        unmet += over
        for i in range(3):
            if v[i] > lam[i]:
                lam[i], worst[i] = v[i], b.label()
    return {"lam": lam, "leaves": leaves, "evaluated": evaluated, "unmet": unmet, "worst": worst}


def merge(acc: dict | None, r: dict) -> dict:
    """Order-free combination of refine_box results (max of lam, sums of counts)."""
    if acc is None:
        acc = {"lam": [F(0)] * 3, "leaves": 0, "evaluated": 0, "unmet": 0, "worst": [None] * 3}
    for k in ("leaves", "evaluated", "unmet"):
        acc[k] += r[k]
    for i in range(3):
        if r["lam"][i] > acc["lam"][i]:
            acc["lam"][i], acc["worst"][i] = r["lam"][i], r["worst"][i]
    return acc


def residual_cover(e_lo: F, e_hi: F, cands: list, params: dict, log=None) -> dict:
    """Serial cover (validation and calibration); the runner parallelises the same refine_box."""
    t0 = time.time()
    acc = None
    boxes = initial_boxes(e_lo, e_hi, params["splits"], params["tm_order"])
    for n, bx in enumerate(boxes, 1):
        acc = merge(acc, refine_box(bx, cands, params))
        if log is not None and n % 20 == 0:
            log(f"    initial boxes {n}/{len(boxes)}, boxes evaluated {acc['evaluated']}, {time.time() - t0:.0f}s")
    return {"lam": acc["lam"], "leaves": acc["leaves"], "boxes_evaluated": acc["evaluated"],
            "leaves_over_tolerance": acc["unmet"], "worst_box": acc["worst"], "initial_boxes": len(boxes),
            "seconds": time.time() - t0}


def atom_values(cands: list, de: F) -> list:
    """Exact bounds of |D1(e)(a)| and |D2(e)(a)| over h in [-de, de]:
    D1(e)(a) = D1(a) + h D2(a) + h^2/2 D3(a),  D2(e)(a) = D2(a) + h D3(a)  (D_j(a) = band-0 constant)."""
    a = [c[0].get((0, 0), F(0)) for c in cands]
    # |poly(h)| <= |c0| + |c1| de + |c2| de^2 (rigorous; exact rationals)
    d1 = abs(a[1]) + abs(a[2]) * de + abs(a[3]) / 2 * de ** 2
    d2 = abs(a[2]) + abs(a[3]) * de
    return [a, d1, d2]


def propagate(lam: list, C_T: F, tau: F, kappa: dict) -> dict:
    k1, k2 = kappa[1], kappa[2]
    n0 = C_T * lam[0]
    n1 = C_T * (lam[1] + k1 * n0)
    e_d1 = tau * (lam[1] + k1 * n0)
    e_d2 = tau * (lam[2] + 2 * k1 * n1 + k2 * n0)
    return {"n0": n0, "n1": n1, "err_D1": e_d1, "err_D2": e_d2}


def certify_subblock(e_lo: F, e_hi: F, params: dict, premise: dict, kappa: dict, log=None) -> dict:
    ec = (e_lo + e_hi) / 2
    de = (e_hi - e_lo) / 2
    t0 = time.time()
    fp = params["float"]
    prop = FL.propose(float(ec), n=fp["n"], n4=fp["n4"], ns=fp["ns"], nt=fp["nt"], q=fp["q"])
    cands = [FL.exact_candidate(prop["basis"], c, bits=fp["bits"]) for c in prop["coeffs"]]
    t_prop = time.time() - t0
    rc = residual_cover(e_lo, e_hi, cands, params, log=log)
    av = atom_values(cands, de)
    pr = propagate(rc["lam"], premise["C_T"], premise["tau"], kappa)
    D1 = av[1] + pr["err_D1"]
    D2 = av[2] + pr["err_D2"]
    return {"e_lo": str(e_lo), "e_hi": str(e_hi), "D1": D1, "D2": D2,
            "atom_candidate_values": [str(x) for x in av[0]],
            "abs_D1e_atom_bound": av[1], "abs_D2e_atom_bound": av[2],
            "lam": rc["lam"], "propagation": pr, "cover": {k: rc[k] for k in (
                "leaves", "boxes_evaluated", "leaves_over_tolerance", "worst_box")},
            "float_proposal": {"discrete_residual": prop["discrete_residual"],
                               "nodes": prop["nodes"], "unknowns": prop["unknowns"],
                               "seconds": t_prop},
            "seconds": time.time() - t0}


def sub_blocks(e_lo: F, e_hi: F, n: int) -> list:
    w = (e_hi - e_lo) / n
    return [(e_lo + w * i, e_lo + w * (i + 1)) for i in range(n)]
