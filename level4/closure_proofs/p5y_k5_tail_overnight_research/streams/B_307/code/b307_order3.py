"""Real order-3 objects on exact fixtures (REAL_ORDER3_THEORY.md sections 2, 4, 7).

Functions here take the output of ``b307_cellpipe.run_cell`` (a synthetic fixture cell) and compute, exactly:

  direct_hierarchy : the ladder of bounds on the TRUE point value |F_r'''(e0)(a)|
      L_res_norm   = Lambda * ||(I-K) F'''||                            (resolvent identity, norm-only)
      L_split_true = Lambda * (sigma3 + 3 k1 ||F''|| + 3 k2 ||F'|| + k3 ||F||)   (triangle split, true sups)
      L_surrogate  = A0 * f_G^surr   (theorem TC-T P2': cell k_i, candidate sups, Lemma-G A0)
      L_atom_true  = Lambda sigma3 + 3 A1 sigma2 + 3 A2 sigma1 + A3 sigma0   (atom functionals of d^iR, TRUE norms)
      L_atom_PM    = same with positive-majorant functionals
      L_atom_G     = same with Lemma-G-type constants (C, k1 C^2, ..., 6 k1^3 C^4 + 6 k1 k2 C^3 + k3 C^2)
      L_real(eta)  = |G^(a)| + Lambda (f_G(G^) + eps3)                       (real-candidate bound)
    plus the exact identity F'''(a) = [R S'''](a) + 3[dR S''](a) + 3[d2R S'](a) + [d3R S](a).

  route_groups : the order-3/4 group of the theorem-TC half-width at the A0 level,
      Q(G^) = rho |G^(a)| + A0 rho f_G(G^) + A0 rho^2/2 * s_G (4 k1 + 6 k2 rho + 2 k3 rho^2 + k4 rho^3/6)
    the structural ratios alpha = |F'''(a)| / (A0 f_G^surr), beta = rho * env4_sG(s_G) / (2 f_G^surr),
    the floor Q(G^) >= rho |[R_e0 phi'''_0(e0)](a)| (Proposition RO3-F) and the envelope (Proposition RO3-E)
      beta <= rho (4 k1 + 6 k2 rho + 2 k3 rho^2 + k4 rho^3/6) (C (f_G^surr + eps3) + ||G^ - F'''||) / (2 f_G^surr).
"""
from __future__ import annotations

from fractions import Fraction as F

import b307_lib as L
from b307_lib import X


def direct_hierarchy(cell, o):
    P0 = cell["P0"]
    lad = cell["ladders"]
    k_cell = cell["cb"]["k"]
    A0 = cell["A"][0]
    a = L.ATOM
    Fd, S = o["Fd"], o["S0"]
    kp_ = P0.k
    T3 = abs(Fd[3][a])
    ident = (X.mat_vec(P0.R, S[3])[a] + 3 * X.mat_vec(P0.dR, S[2])[a] + 3 * X.mat_vec(P0.d2R, S[1])[a]
             + X.mat_vec(P0.d3R, S[0])[a])
    ikf3 = L.vsub(Fd[3], X.mat_vec(P0.K[0], Fd[3]))
    sig = [X.sup_norm(S[j]) for j in range(4)]
    Lam = P0.Lam
    Fh, Dh, Hh = o["cand"]
    eps3 = 3 * kp_[1] * X.sup_norm(L.vsub(Fd[2], Hh)) + 3 * kp_[2] * X.sup_norm(L.vsub(Fd[1], Dh)) \
        + kp_[3] * X.sup_norm(L.vsub(Fd[0], Fh))
    lev = {
        "T3_true": T3,
        "L_res_norm": Lam * X.sup_norm(ikf3),
        "L_split_true": Lam * (sig[3] + 3 * kp_[1] * X.sup_norm(Fd[2]) + 3 * kp_[2] * X.sup_norm(Fd[1])
                               + kp_[3] * X.sup_norm(Fd[0])),
        "L_surrogate_TCT": A0 * o["fG_surr"],
        "L_atom_true": Lam * sig[3] + 3 * lad["A1"]["true"] * sig[2] + 3 * lad["A2"]["true"] * sig[1]
        + lad["A3"]["true"] * sig[0],
        "L_atom_PM": Lam * sig[3] + 3 * lad["A1"]["PM"] * sig[2] + 3 * lad["A2"]["PM"] * sig[1]
        + lad["A3"]["PM"] * sig[0],
        "L_atom_G": P0.C * sig[3] + 3 * lad["A1"]["G"] * sig[2] + 3 * lad["A2"]["G"] * sig[1]
        + lad["A3"]["G"] * sig[0],
    }
    for name, rt in o["routes"].items():
        if name.startswith("real"):
            lev[f"L_{name}"] = abs(rt["Gat"]) + Lam * (rt["fG"] + eps3)
    return {"levels": lev, "identity_ok": ident == Fd[3][a], "eps3": eps3,
            "normF3": X.sup_norm(Fd[3]), "normIKF3": X.sup_norm(ikf3), "sig": sig}


def route_groups(cell, o, dh):
    rho = cell["e0"] * 0 + cell["rho"]
    A0 = cell["A"][0]
    C = cell["cb"]["C"]
    k = cell["cb"]["k"]
    P0 = cell["P0"]
    a = L.ATOM
    f = o["fG_surr"]
    T3 = dh["levels"]["T3_true"]
    floor_val = rho * abs(X.mat_vec(P0.R, o["phi3_zero"])[a])
    out = {"Q_surrogate": A0 * rho * f, "alpha": T3 / (A0 * f), "floor": floor_val,
           "cover_factor_2k1rhoC": 2 * k[1] * rho * C, "perron_index": dh["normF3"] / (C * dh["normIKF3"])
           if dh["normIKF3"] else None}
    out["floor_ok_surrogate"] = out["Q_surrogate"] >= floor_val
    for name, rt in o["routes"].items():
        if not name.startswith("real"):
            continue
        sGpart = L.env4_sG_part(rt["sG"], k, rho)
        Qr = rho * abs(rt["Gat"]) + A0 * rho * rt["fG"] + A0 * rho ** 2 / 2 * sGpart
        beta = rho * sGpart / (2 * f)
        G = rt["G"]
        gerr = X.sup_norm(L.vsub(G, o["Fd"][3]))
        coef = rho * (4 * k[1] + 6 * k[2] * rho + 2 * k[3] * rho ** 2 + k[4] * rho ** 3 / 6)
        beta_env = coef * (C * (f + dh["eps3"]) + gerr) / (2 * f)
        out[name] = {"Q": Qr, "Q_ratio_real_over_surrogate": Qr / out["Q_surrogate"], "beta": beta,
                     "beta_envelope": beta_env, "envelope_ok": beta <= beta_env,
                     "floor_ok": Qr >= floor_val,
                     "half_ratio_real_over_surrogate": rt["half"] / o["routes"]["surrogate"]["half"],
                     "centre_motion": rho * abs(rt["Gat"]), "A0rho_fG": A0 * rho * rt["fG"],
                     "sG_penalty_A0": A0 * rho ** 2 / 2 * sGpart}
    return out


def adlr(cell, o):
    """Atom-direct likelihood-ratio Taylor (ADLR) enclosure (coordinator suggestion; REAL_ORDER3_THEORY section 4b):

        F_r''(e)(a) in H^(a) +- [ rad0 + s B3 + (s^2/2) B4 ],   s = |e - e0|
        rad0 = A0 f_H + 2 A1 f_D + A2 f_F                         (theorem-AD midpoint form, constants at e0)
        B3  >= |F_r'''(e0)(a)|  via  sum_j C(3,j) A_j sigma_{3-j}(e0)
        B4  >= sup_cell |F_r''''(u)(a)|  via  sum_j C(4,j) sup_u A_j(u) sigma_{4-j}^cell
    with A_j >= ||delta_a d^j R|| (the LR constants Lambda_j of the Gaussian case are such A_j).
    Variants:  G      -- Lemma-G-type cell-uniform A_j (certified: generic_dnR_bound with cell k, C);
               true   -- the TRUE atom functional norms (best case for ANY A_j supply, incl. LR): exact at e0 for
                         rad0 and B3; B4 uses the grid maximum of ||delta_a d^j R_u|| (a PROXY, not a certificate);
               oracle -- B3 = |F'''(e0)(a)|, B4 = grid max |F''''(u)(a)| (the floor of this enclosure SHAPE; proxy).
    Returns half-widths at s = rho and pointwise soundness counts on the grid."""
    rho = cell["rho"]
    k, C = cell["cb"]["k"], cell["cb"]["C"]
    P0, lad = cell["P0"], cell["ladders"]
    r = o["r"]
    S = o["S0"]
    sig_mid = [X.sup_norm(S[j]) for j in range(4)]
    sig_cell = cell["cb"]["sigma"][r]
    AG = [L.generic_dnR_bound(j, k, C) for j in range(5)]
    At = [P0.Lam, lad["A1"]["true"], lad["A2"]["true"], lad["A3"]["true"]]
    APM = [P0.Lam, lad["A1"]["PM"], lad["A2"]["PM"], lad["A3"]["PM"]]
    Amax = cell["adlr_grid"]["Amax"]
    fF, fD, fH = o["fF"], o["fD"], o["fH"]
    from math import comb
    B3 = {"G": sum(comb(3, j) * AG[j] * sig_mid[3 - j] for j in range(4)),
          "true": sum(comb(3, j) * At[j] * sig_mid[3 - j] for j in range(4)),
          "PM": sum(comb(3, j) * APM[j] * sig_mid[3 - j] for j in range(4)),
          "oracle": abs(o["Fd"][3][L.ATOM])}
    B4 = {"G": sum(comb(4, j) * AG[j] * sig_cell[4 - j] for j in range(5)),
          "true": sum(comb(4, j) * Amax[j] * sig_cell[4 - j] for j in range(5)),
          "oracle": cell["adlr_grid"]["F4max"][r]}
    B4["PM"] = B4["true"]
    rad0 = {"G": AG[0] * fH + 2 * AG[1] * fD + AG[2] * fF,
            "true": At[0] * fH + 2 * At[1] * fD + At[2] * fF}
    rad0["PM"] = APM[0] * fH + 2 * APM[1] * fD + APM[2] * fF
    rad0["oracle"] = rad0["true"]
    out = {}
    surr_half = o["routes"]["surrogate"]["half"]
    for v in ("G", "PM", "true", "oracle"):
        half = rad0[v] + rho * B3[v] + rho ** 2 * B4[v] / 2
        fails = 0
        for t, E2 in cell["adlr_grid"]["E2_surrogate"][r]:
            s = abs(t)
            if abs(E2) > rad0[v] + s * B3[v] + s * s * B4[v] / 2:
                fails += 1
        rec = {"rad0": rad0[v], "rho_B3": rho * B3[v], "rho2_B4_over2": rho ** 2 * B4[v] / 2, "half": half,
               "half_over_surrogate_half": half / surr_half, "pointwise_failures": fails,
               "certified": v == "G"}
        for name, rt in o["routes"].items():
            if name.startswith("real"):
                rec[f"half_over_{name}_half"] = half / rt["half"]
        out[v] = rec
    out["s_coefficient_B3_over_A0fGsurr"] = {v: B3[v] / (cell["A"][0] * o["fG_surr"]) for v in B3}
    # negative control (planted-invalid): the oracle enclosure with the linear term dropped (B3 := 0)
    nc = 0
    for t, E2 in cell["adlr_grid"]["E2_surrogate"][r]:
        s = abs(t)
        if abs(E2) > rad0["oracle"] + s * s * B4["oracle"] / 2:
            nc += 1
    out["nc_B3_dropped_detections"] = nc
    return out


def route_group_plants(cell, o, dh):
    """Class-(a) controls for the RO3-F floor check and the RO3-E envelope check (review F6): planted-invalid routes
    are passed THROUGH route_groups (the code under test) and its own floor_ok / envelope_ok must flip.
      floor plant    : G = 0, f_G = 0, s_G = 0 (violates the premise f_G >= ||phi'''_G(e0)||); Q = 0, so the floor check
                       fires whenever the floor is > 0 (eligibility recorded);
      envelope plant : the eta = 1e-3 real route with s_G := 2 (C (f + eps3) + ||G - F'''||) + 1 (violates the premise
                       s_G <= ||F'''|| + ||G - F'''||); beta is then > 2 * beta_envelope > beta_envelope, guaranteed."""
    n = len(o["Fd"][0])
    C = cell["cb"]["C"]
    f = o["fG_surr"]
    real = next(rt for nm, rt in o["routes"].items() if nm.startswith("real"))
    gerr = X.sup_norm(L.vsub(real["G"], o["Fd"][3]))
    sG_bad = 2 * (C * (f + dh["eps3"]) + gerr) + 1
    o2 = dict(o)
    o2["routes"] = {
        "surrogate": o["routes"]["surrogate"],
        "real_PLANT_floor": {"G": [F(0)] * n, "fG": F(0), "sG": F(0), "Gat": F(0), "half": o["routes"]["surrogate"]["half"]},
        "real_PLANT_env": dict(real, sG=sG_bad),
    }
    out = route_groups(cell, o2, dh)
    eligible_floor = out["floor"] > 0
    return {"floor_plant_eligible": eligible_floor,
            "floor_plant_fired": (not out["real_PLANT_floor"]["floor_ok"]) if eligible_floor else None,
            "envelope_plant_fired": not out["real_PLANT_env"]["envelope_ok"]}
