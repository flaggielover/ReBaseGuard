"""Exact theorem-TC / TC-T pipeline on one synthetic fixture cell, with the exact truth next to every bound.

For one cell [e0 - rho, e0 + rho] of a fixture kernel family and m sources S_0..S_{m-1}:
  * certified cell bounds (k_i, C, sigma_n) and Lemma-G constants;
  * K1-type candidates F^, D^, H^ (exact + seeded noise), a real order-3 candidate G^ (exact F''' + noise) and the
    zero candidate G^ = 0 (TC-T premise P2');
  * the exact midpoint residual norms f_F, f_D, f_H, f_G, the TC-T surrogate f_G, Env4, p0/p1/p2, rad, half;
  * on the declared rational time grid: the exact E''(e)(a), its exact five-way split
        E''(e)(a) = P_H + P_G + P_4 + P_1 + P_0
            P_H = [R_e phi''(e0)](a),  P_G = t [R_e phi'''(e0)](a),  P_4 = [R_e (phi''(e) - phi''(e0) - t phi'''(e0))](a),
            P_1 = 2 [dR_e phi'(e)](a),  P_0 = [d2R_e phi(e)](a)
    each against its own bound term (A0 fH, A0 rho fG, A0 rho^2 Env4/2, 2 A1 p1, A2 p0);
  * the premise checks ||phi^(j)(e)|| <= p_j(|t|) and ||phi''''(e)|| <= Env4.
All arithmetic is exact (Fraction); floats appear only in the returned summaries.
"""
from __future__ import annotations

import random
from fractions import Fraction as F
from math import comb

import b307_lib as L
from b307_lib import X, Q

# declared candidate noise sizes (VALIDATION_DECLARATION_B307.json)
ETA_K1 = F(1, 10 ** 6)
ETA_G = (F(1, 10 ** 3), F(1, 10 ** 2))
GRID = 8


def _noise(rng, n):
    return [F(rng.randint(-100, 100), 100) for _ in range(n)]


def f_derivs_at(P, spoly, e, upto, s_upto=None):
    """[S^(0..s_upto)(e)], [F^(0..upto)(e)] exactly from (I - K)F = S (Leibniz), using P's resolvent."""
    s_upto = upto if s_upto is None else max(s_upto, upto)
    S = [[X.poly_eval(X.poly_deriv(list(p), i), e) for p in spoly] for i in range(s_upto + 1)]
    out = []
    for nn in range(upto + 1):
        rhs = list(S[nn])
        for i in range(1, nn + 1):
            rhs = L.vadd(rhs, L.vscale(X.mat_vec(P.K[i], out[nn - i]), F(comb(nn, i))))
        out.append(X.mat_vec(P.R, rhs))
    return S, out


def phis_at(P, S, Ft, t, upto):
    """phi^(j)(e) for j = 0..upto, phi = S - (I - K) Ftilde, Ftilde^(j) from the Taylor candidate.
    Ft = (Fh, Dh, Hh, Gh).  Uses phi^(j) = S^(j) + sum_{i>=1} C(j,i) K_i Ftilde^(j-i) - (I - K) Ftilde^(j)."""
    Fh, Dh, Hh, Gh = Ft
    n = len(Fh)
    z = [F(0)] * n
    Ftil = [
        L.vadd(Fh, L.vscale(Dh, t), L.vscale(Hh, t * t / 2), L.vscale(Gh, t ** 3 / 6)),
        L.vadd(Dh, L.vscale(Hh, t), L.vscale(Gh, t * t / 2)),
        L.vadd(Hh, L.vscale(Gh, t)),
        list(Gh),
        z,
    ]
    out = []
    for j in range(upto + 1):
        v = list(S[j])
        for i in range(1, j + 1):
            v = L.vadd(v, L.vscale(X.mat_vec(P.K[i], Ftil[j - i]), F(comb(j, i))))
        v = L.vsub(v, L.vsub(Ftil[j], X.mat_vec(P.K[0], Ftil[j])))
        out.append(v)
    return out


def run_cell(kp, sources, e0: F, rho: F, seed: int, m: int | None = None, want_d3: bool = True,
             negative_controls: bool = True, adlr: bool = True):
    Q.guard_drift(e0 - rho, e0 + rho)
    m = len(sources) if m is None else m
    n = len(kp)
    cb = L.cell_bounds(kp, sources, e0, rho)
    k, C = cb["k"], cb["C"]
    A0, A1, A2 = C, k[1] * C * C, k[2] * C * C + 2 * k[1] ** 2 * C ** 3
    P0 = L.Point(kp, e0, need_d3=want_d3)
    lad = P0.ladders() if want_d3 else None
    rng = random.Random(99991 * seed + 7)
    objs = []
    for r in range(m):
        S0, Fd = f_derivs_at(P0, sources[r], e0, 4)
        Fh = L.vadd(Fd[0], L.vscale(_noise(rng, n), ETA_K1))
        Dh = L.vadd(Fd[1], L.vscale(_noise(rng, n), ETA_K1))
        Hh = L.vadd(Fd[2], L.vscale(_noise(rng, n), ETA_K1))
        g3max = X.sup_norm(Fd[3]) or F(1)
        Greal = {eta: L.vadd(Fd[3], L.vscale(_noise(rng, n), eta * g3max)) for eta in ETA_G}
        Gzero = [F(0)] * n
        ph0 = phis_at(P0, S0, (Fh, Dh, Hh, Gzero), F(0), 3)
        fF, fD, fH = (X.sup_norm(ph0[j]) for j in range(3))
        phi3_zero = ph0[3]
        sF, sD, sH = X.sup_norm(Fh), X.sup_norm(Dh), X.sup_norm(Hh)
        sig3_mid = X.sup_norm(S0[3])
        sig4_cell = cb["sigma"][r][4]
        fG_surr = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + sig3_mid
        routes = {}
        # surrogate (TC-T P2'): f_G = split surrogate, s_G = 0, G(a) = 0
        e4_0 = L.env4(sF, sD, sH, F(0), k, sig4_cell, rho)
        routes["surrogate"] = {"G": Gzero, "fG": fG_surr, "sG": F(0), "Gat": F(0), "env4": e4_0}
        # surrogate with the EXACT zero-candidate residual norm (isolates the split/collapse slack)
        routes["zero_exactfG"] = {"G": Gzero, "fG": X.sup_norm(phi3_zero), "sG": F(0), "Gat": F(0), "env4": e4_0}
        for eta, G in Greal.items():
            ph3 = phis_at(P0, S0, (Fh, Dh, Hh, G), F(0), 3)[3]
            sG = X.sup_norm(G)
            routes[f"real_eta{eta}"] = {"G": G, "fG": X.sup_norm(ph3), "sG": sG, "Gat": G[L.ATOM],
                                          "env4": L.env4(sF, sD, sH, sG, k, sig4_cell, rho)}
        for name, rt in routes.items():
            p = L.taylor_p(fF, fD, fH, rt["fG"], rt["env4"], rho)
            rt["p"] = p
            rt["rad"] = L.radius(A0, A1, A2, p)
            rt["half"] = rho * abs(rt["Gat"]) + rt["rad"]
            rt["terms"] = L.radius_terms(A0, A1, A2, fF, fD, fH, rt["fG"], rt["env4"], rho)
            rt["ph_e0"] = phis_at(P0, S0, (Fh, Dh, Hh, rt["G"]), F(0), 3)
            rt["max"] = {"E2": F(0), "P_H": F(0), "P_G": F(0), "P_4": F(0), "P_1": F(0), "P_0": F(0),
                         "phi4": F(0), "prem_ratio_max": F(0), "env4_fail": 0, "idfail": 0, "sound_fail": 0,
                         "nc_flip_fail": 0, "nc_e10_fail": 0}
        objs.append({"r": r, "Fd": Fd, "S0": S0, "cand": (Fh, Dh, Hh), "fF": fF, "fD": fD, "fH": fH,
                     "sF": sF, "sD": sD, "sH": sH, "sig3_mid": sig3_mid, "sig4_cell": sig4_cell,
                     "fG_surr": fG_surr, "phi3_zero": phi3_zero, "routes": routes})
    # joint assembly (surrogate route) : one source (1/m) sum_r S_r, candidates (1/m) sum
    jsrc = []
    for x in range(n):
        acc = [F(0)]
        for r in range(m):
            acc = L.poly_add(acc, L.poly_scale(sources[r][x], F(1, m)))
        jsrc.append(acc)
    cbj = L.cell_bounds(kp, [jsrc], e0, rho)
    Sj, _ = f_derivs_at(P0, jsrc, e0, 4)
    avg = lambda vs: [sum(c, F(0)) / m for c in zip(*vs)]  # noqa: E731
    Fj, Dj, Hj = (avg([o["cand"][i] for o in objs]) for i in range(3))
    phj = phis_at(P0, Sj, (Fj, Dj, Hj, [F(0)] * n), F(0), 3)
    fFj, fDj, fHj = (X.sup_norm(phj[j]) for j in range(3))
    sFj, sDj, sHj = X.sup_norm(Fj), X.sup_norm(Dj), X.sup_norm(Hj)
    fGj = 3 * k[1] * sHj + 3 * k[2] * sDj + k[3] * sFj + X.sup_norm(Sj[3])
    e4j = L.env4(sFj, sDj, sHj, F(0), k, cbj["sigma"][0][4], rho)
    rad_joint = L.radius(A0, A1, A2, L.taylor_p(fFj, fDj, fHj, fGj, e4j, rho))
    rad_perr_sum = sum((o["routes"]["surrogate"]["rad"] for o in objs), F(0)) / m
    joint_truth = F(0)
    adlr_grid = {"Amax": [F(0)] * 5, "F4max": [F(0)] * m, "E2_surrogate": [[] for _ in range(m)]}
    # ------------------------------------------------------------------ time grid (exact truth)
    for kk in range(-GRID, GRID + 1):
        t = rho * kk / GRID
        e = e0 + t
        Pt = L.Point(kp, e, need_d3=False)
        tot_E2 = F(0)
        if adlr:
            rows = Pt.atom_rows(4)
            for jj in range(5):
                adlr_grid["Amax"][jj] = max(adlr_grid["Amax"][jj], L.row_l1([rows[jj]], 0))
        for o in objs:
            S, Fe = f_derivs_at(Pt, sources[o["r"]], e, 4 if adlr else 2, s_upto=4)
            if adlr:
                adlr_grid["F4max"][o["r"]] = max(adlr_grid["F4max"][o["r"]], abs(Fe[4][L.ATOM]))
            Fh, Dh, Hh = o["cand"]
            for name, rt in o["routes"].items():
                G = rt["G"]
                ph = phis_at(Pt, S, (Fh, Dh, Hh, G), t, 4)
                E2 = Fe[2][L.ATOM] - Hh[L.ATOM] - t * G[L.ATOM]
                comp = (X.mat_vec(Pt.R, ph[2])[L.ATOM] + 2 * X.mat_vec(Pt.dR, ph[1])[L.ATOM]
                        + X.mat_vec(Pt.d2R, ph[0])[L.ATOM])
                mx = rt["max"]
                if comp != E2:
                    mx["idfail"] += 1
                # five-way split
                ph0_e0 = rt["ph_e0"]
                PH = X.mat_vec(Pt.R, ph0_e0[2])[L.ATOM]
                PG = t * X.mat_vec(Pt.R, ph0_e0[3])[L.ATOM]
                P4 = X.mat_vec(Pt.R, L.vsub(L.vsub(ph[2], ph0_e0[2]), L.vscale(ph0_e0[3], t)))[L.ATOM]
                P1 = 2 * X.mat_vec(Pt.dR, ph[1])[L.ATOM]
                P0v = X.mat_vec(Pt.d2R, ph[0])[L.ATOM]
                if PH + PG + P4 + P1 + P0v != E2:
                    mx["idfail"] += 1
                for key, v in (("E2", E2), ("P_H", PH), ("P_G", PG), ("P_4", P4), ("P_1", P1), ("P_0", P0v)):
                    mx[key] = max(mx[key], abs(v))
                # premise checks at |t|
                s = abs(t)
                pp = L.taylor_p(o["fF"], o["fD"], o["fH"], rt["fG"], rt["env4"], s)
                for j, pj in ((0, pp[0]), (1, pp[1]), (2, pp[2])):
                    nrm = X.sup_norm(ph[j])
                    if pj > 0:
                        mx["prem_ratio_max"] = max(mx["prem_ratio_max"], nrm / pj)
                mx["phi4"] = max(mx["phi4"], X.sup_norm(ph[4]))
                if X.sup_norm(ph[4]) > rt["env4"]:
                    mx["env4_fail"] += 1
                if abs(E2) > rt["rad"]:
                    mx["sound_fail"] += 1
                if negative_controls:
                    if name.startswith("real") and abs(Fe[2][L.ATOM] - Hh[L.ATOM] + t * G[L.ATOM]) > rt["rad"]:
                        mx["nc_flip_fail"] += 1
                    if name == "surrogate":
                        rad_e10 = L.radius(A0, A1, A2, L.taylor_p(o["fF"], o["fD"], o["fH"], F(0), rt["env4"], rho))
                        if abs(E2) > rad_e10:
                            mx["nc_e10_fail"] += 1
                if name == "surrogate":
                    tot_E2 += E2
                    adlr_grid["E2_surrogate"][o["r"]].append((t, E2))
        joint_truth = max(joint_truth, abs(tot_E2) / m)
    return {"e0": e0, "rho": rho, "cb": cb, "A": (A0, A1, A2), "P0": P0, "ladders": lad, "objs": objs,
            "adlr_grid": adlr_grid,
            "joint": {"rad_joint": rad_joint, "rad_perr_sum": rad_perr_sum, "truth": joint_truth}}
