"""Driver: every exact-fixture computation of stream B_307 (HIGHER_ORDER_AUDIT_307 + REAL_ORDER3_THEORY).

Validation set = the rules of VALIDATION_DECLARATION_B307.json (written before this script existed).
Writes  NS/validation/B307_AUDIT_FIXTURES.json  and  NS/validation/B307_ORDER3_FIXTURES.json.
No CUSUM cell is touched; every drift passes ov_quarantine.guard_drift.

Parts
  P1  exact identity checks (+ negative controls): resolvent-derivative formulas, Lemma SM(d), D = nu(h1),
      the E'' identity, the (P2') phi''' identity by exact polynomial differentiation.
  P2  atom-constant ladders at points (A0..A3: true / positive majorant / collapse / Lemma G / Lemma Dv' r2),
      soundness of each rung, and the FX_B scaling in Lambda at e = 0.
  P3  fixture cells: the TC/TC-T pipeline with the exact five-way split of E''(e)(a), per-term looseness,
      premise checks, soundness, assembly per-r vs joint, and the order-3 comparisons (b307_order3).
"""
from __future__ import annotations

import json
import math
import sys
import time
import zlib
from fractions import Fraction as F
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b307_lib as L  # noqa: E402
from b307_lib import X, Q, NS  # noqa: E402
import b307_cellpipe as CP  # noqa: E402
import b307_order3 as O3  # noqa: E402

Q.install_import_guard()


def fl(x):
    if x is None:
        return None
    return float(x)


def stats(vals):
    v = sorted(float(x) for x in vals if x is not None)
    if not v:
        return None
    return {"n": len(v), "min": v[0], "median": v[len(v) // 2], "max": v[-1]}


# ------------------------------------------------------------------------------------------------ declared sets

def fx_a_specs():
    for n in (5, 7):
        for seed in (1, 2, 3, 4, 5, 6):
            for kill in (F(1, 5), F(1, 40)):
                yield {"class": "FX_A", "n": n, "seed": seed, "kill": kill}


def fx_b_points():
    for N in (4, 6, 8, 12, 16, 24):
        for e in (F(0), F(1, 4), F(1, 2)):
            yield {"class": "FX_B", "N": N, "e": e}


def fx_b_cells():
    for N in (4, 6, 8, 12):
        for e0 in (F(0), F(1, 4)):
            yield {"class": "FX_B", "N": N, "e0": e0}


# ------------------------------------------------------------------------------------------------ P1 identities

def part1():
    out = {"checks": [], "negative_controls": []}
    # (a) resolvent derivative formulas F^(n) = sum C(n,i) d^iR S^(n-i)
    cases = []
    kpA = L.generic_family(5, 1, F(1, 5))
    srcA = L.generic_sources(5, 1, 2)
    cases.append(("FX_A n=5 seed=1", kpA, srcA, F(1, 8)))
    kpB, srcB, _ = L.score_walk(6)
    cases.append(("FX_B N=6", kpB, srcB[:2], F(1, 4)))
    for label, kp, srcs, e in cases:
        Q.guard_drift(e)
        P = L.Point(kp, e)
        RK1R = P.dR
        bad_d3R = X.mat_add(P.d3R, X.mat_scale(L.mm(P.R, P.K[2], RK1R), F(3)), F(-1))
        for r, sp in enumerate(srcs):
            fam = X.DriftFamily(kp, sp, (e, e))
            Fd = fam.F_derivs(e, 3)
            S = [fam.S(e, i) for i in range(4)]
            f1 = L.vadd(X.mat_vec(P.R, S[1]), X.mat_vec(P.dR, S[0]))
            f2 = L.vadd(X.mat_vec(P.R, S[2]), L.vscale(X.mat_vec(P.dR, S[1]), F(2)), X.mat_vec(P.d2R, S[0]))
            f3 = L.vadd(X.mat_vec(P.R, S[3]), L.vscale(X.mat_vec(P.dR, S[2]), F(3)),
                        L.vscale(X.mat_vec(P.d2R, S[1]), F(3)), X.mat_vec(P.d3R, S[0]))
            f3bad = L.vadd(X.mat_vec(P.R, S[3]), L.vscale(X.mat_vec(P.dR, S[2]), F(3)),
                           L.vscale(X.mat_vec(P.d2R, S[1]), F(3)), X.mat_vec(bad_d3R, S[0]))
            out["checks"].append({"what": f"d^nR formulas n=1,2,3 ({label}, r={r})",
                                  "pass": f1 == Fd[1] and f2 == Fd[2] and f3 == Fd[3]})
            out["negative_controls"].append({"what": f"d3R without 3 R K2 R K1 R ({label}, r={r})",
                                             "detected": f3bad != Fd[3]})
    # (b) E'' identity with the factor 2 dropped, one cell (the full identity is checked on every grid point in P3)
    kp, srcs, e0 = kpA, srcA, F(1, 8)
    rho = F(1, 64)
    P0 = L.Point(kp, e0, need_d3=False)
    S0, Fd0 = CP.f_derivs_at(P0, srcs[0], e0, 3)
    cand = (L.vadd(Fd0[0], [F(1, 10 ** 6)] * 5), L.vadd(Fd0[1], [F(-1, 10 ** 6)] * 5), Fd0[2], [F(0)] * 5)
    t = rho / 2
    Pt = L.Point(kp, e0 + t, need_d3=False)
    St, Fdt = CP.f_derivs_at(Pt, srcs[0], e0 + t, 2)
    ph = CP.phis_at(Pt, St, cand, t, 2)
    E2 = Fdt[2][0] - cand[2][0]
    good = X.mat_vec(Pt.R, ph[2])[0] + 2 * X.mat_vec(Pt.dR, ph[1])[0] + X.mat_vec(Pt.d2R, ph[0])[0]
    bad = X.mat_vec(Pt.R, ph[2])[0] + X.mat_vec(Pt.dR, ph[1])[0] + X.mat_vec(Pt.d2R, ph[0])[0]
    out["checks"].append({"what": "E'' = R phi'' + 2 dR phi' + d2R phi at a (FX_A, one grid point)", "pass": good == E2})
    out["negative_controls"].append({"what": "E'' identity without the factor 2", "detected": bad != E2})
    # (c) (P2') phi''' identity by EXACT polynomial differentiation of phi(e) = S(e) - (I - K_e) Ftilde(e)
    Fh, Dh, Hh = cand[0], cand[1], cand[2]
    for Gh, gl in (([F(0)] * 5, "G=0"), (Fd0[3], "G=F'''")):
        # Ftilde as polynomial in e: t = e - e0
        tp = [-e0, F(1)]
        def pw(k):
            p = [F(1)]
            for _ in range(k):
                p = L.poly_mul(p, tp)
            return p
        Ftp = [L.poly_add(L.poly_add([Fh[x]], L.poly_scale(pw(1), Dh[x])),
                          L.poly_add(L.poly_scale(pw(2), Hh[x] / 2), L.poly_scale(pw(3), Gh[x] / 6))) for x in range(5)]
        KF = L.polymat_vec(kp, Ftp)
        phip = [L.poly_add(L.poly_add(srcs[0][x], L.poly_scale(Ftp[x], F(-1))), KF[x]) for x in range(5)]
        phi3_poly = [X.poly_eval(X.poly_deriv(p, 3), e0) for p in phip]
        phi3_formula = CP.phis_at(P0, S0, (Fh, Dh, Hh, Gh), F(0), 3)[3]
        K = P0.K
        tc_formula = L.vsub(L.vadd(S0[3], L.vscale(X.mat_vec(K[1], Hh), F(3)), L.vscale(X.mat_vec(K[2], Dh), F(3)),
                                   X.mat_vec(K[3], Fh)), L.vsub(Gh, X.mat_vec(K[0], Gh)))
        bad_formula = L.vsub(L.vadd(S0[3], L.vscale(X.mat_vec(K[1], Hh), F(2)), L.vscale(X.mat_vec(K[2], Dh), F(3)),
                                    X.mat_vec(K[3], Fh)), L.vsub(Gh, X.mat_vec(K[0], Gh)))
        out["checks"].append({"what": f"phi'''(e0) = S''' + 3K1H + 3K2D + K3F - (I-K)G by polynomial differentiation ({gl})",
                              "pass": phi3_poly == phi3_formula == tc_formula})
        out["negative_controls"].append({"what": f"phi''' identity with 2K1H instead of 3K1H ({gl})",
                                         "detected": bad_formula != phi3_poly})
    return out


# ------------------------------------------------------------------------------------------------ P2 ladders

LEVELS = ("true", "PM", "collapse", "G", "Dv2")


def ladder_record(lad):
    rec = {"Lambda": fl(lad["Lambda"]), "C": fl(lad["C"]), "C_T": fl(lad["C_T"]), "tau_a": fl(lad["tau_a"]),
           "D": fl(lad["D"]), "delta1": fl(lad["delta1"]), "delta2": fl(lad["delta2"])}
    for A in ("A0", "A1", "A2", "A3"):
        if A in lad:
            rec[A] = {k: fl(v) for k, v in lad[A].items()}
    return rec


def ladder_checks(lad):
    """soundness of every rung (each must be >= the true functional norm), and the chain order."""
    fails = []
    for A in ("A0", "A1", "A2", "A3"):
        if A not in lad:
            continue
        tr = lad[A]["true"]
        for lv, v in lad[A].items():
            if v < tr:
                fails.append(f"{A}.{lv} < true")
    for A in ("A1", "A2", "A3"):
        if A in lad and not (lad[A]["true"] <= lad[A]["PM"] <= lad[A]["collapse"] <= lad[A]["G"]):
            fails.append(f"{A} chain order")
    return fails


def ladder_plants(lad):
    """Class-(a) controls THROUGH ladder_checks (review F6/C-7): (i) the Lemma-G A1 rung replaced by
    true * (1 - 2^-20) must be reported unsound (fires iff true > 0); (ii) the PM and collapse rungs of A2 swapped must
    break the chain-order check (fires iff PM != collapse)."""
    import copy
    out = {}
    l1 = copy.deepcopy(lad)
    tr = l1["A1"]["true"]
    l1["A1"]["G"] = tr * (1 - F(1, 2 ** 20))
    out["rung_plant_eligible"] = tr > 0
    out["rung_plant_fired"] = any(x.startswith("A1.G") for x in ladder_checks(l1)) if tr > 0 else None
    l2 = copy.deepcopy(lad)
    pm, co = l2["A2"]["PM"], l2["A2"]["collapse"]
    l2["A2"]["PM"], l2["A2"]["collapse"] = co, pm
    out["order_plant_eligible"] = pm != co
    out["order_plant_fired"] = ("A2 chain order" in ladder_checks(l2)) if pm != co else None
    return out


def part2():
    pts, fails, nc = [], [], []
    plants = []
    sm_ok = True
    for sp in fx_a_specs():
        kp = L.generic_family(sp["n"], sp["seed"], sp["kill"])
        P = L.Point(kp, F(1, 8))
        lad = P.ladders()
        tb = P.taboo()
        sm_ok &= (tb["tau_a"] / tb["D"] == P.Lam) and (tb["D"] == tb["D_via_h1"])
        nc.append(tb["tau_a"] < P.Lam)
        f = ladder_checks(lad)
        fails += f
        plants.append(ladder_plants(lad))
        pts.append({"spec": {k: str(v) for k, v in sp.items()}, "e": "1/8", **ladder_record(lad), "fails": f})
    for sp in fx_b_points():
        Q.guard_drift(sp["e"])
        kp, _, _ = L.score_walk(sp["N"])
        P = L.Point(kp, sp["e"])
        lad = P.ladders()
        tb = P.taboo()
        sm_ok &= (tb["tau_a"] / tb["D"] == P.Lam) and (tb["D"] == tb["D_via_h1"])
        nc.append(tb["tau_a"] < P.Lam)
        f = ladder_checks(lad)
        fails += f
        plants.append(ladder_plants(lad))
        pts.append({"spec": {k: str(v) for k, v in sp.items()}, **ladder_record(lad), "fails": f})
    # ratios to the truth, per class
    summ = {}
    for cls in ("FX_A", "FX_B"):
        sel = [p for p in pts if p["spec"]["class"] == cls]
        summ[cls] = {}
        for A in ("A0", "A1", "A2", "A3"):
            summ[cls][A] = {lv: stats([p[A][lv] / p[A]["true"] for p in sel if p[A]["true"] > 0])
                            for lv in sel[0][A] if lv != "true"}
    # scaling in Lambda on FX_B at e = 0 (least-squares slopes of log(level) vs log(Lambda))
    scal = {}
    sel = [p for p in pts if p["spec"]["class"] == "FX_B" and p["spec"]["e"] == "0"]
    xs = [math.log(p["Lambda"]) for p in sel]
    def slope(ys):
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    for A in ("A1", "A2", "A3"):
        scal[A] = {lv: slope([math.log(p[A][lv]) for p in sel]) for lv in sel[0][A]}
    scal["C_over_Lambda"] = slope([math.log(p["C"]) for p in sel])
    scal["C_T_over_Lambda"] = slope([math.log(p["C_T"]) for p in sel])
    scal["N_values"] = [p["spec"]["N"] for p in sel]
    scal["Lambda_values"] = [p["Lambda"] for p in sel]
    return {"points": pts, "rung_failures": fails, "SM_identities_all_exact": sm_ok,
            "NON_EVIDENCE_class_d_A0_eq_tau_a": {"detected_on": sum(nc), "of": len(nc),
                                                 "note": "class (d): guaranteed by Lemma SM(d) since D < 1; not evidence (review C-7)"},
            "class_a_plants_through_ladder_checks": {
                "rung_plant": {"fired": sum(1 for x in plants if x["rung_plant_fired"]),
                               "eligible": sum(1 for x in plants if x["rung_plant_eligible"])},
                "order_plant": {"fired": sum(1 for x in plants if x["order_plant_fired"]),
                                "eligible": sum(1 for x in plants if x["order_plant_eligible"])}},
            "ratio_to_true": summ, "FX_B_e0_loglog_slopes_vs_Lambda": scal}


# ------------------------------------------------------------------------------------------------ P3 cells

def cell_specs():
    for sp in fx_a_specs():
        kp = L.generic_family(sp["n"], sp["seed"], sp["kill"])
        srcs = L.generic_sources(sp["n"], sp["seed"], 5)
        e0 = F(1, 8)
        rho = L.cover_rule_rho(kp, srcs, e0, F(1, 16))
        for reg, rr in (("cover", rho), ("cover/16", rho / 16)):
            yield dict(sp, e0=e0, rho=rr, regime=reg), kp, srcs
    for sp in fx_b_cells():
        kp, srcs, _ = L.score_walk(sp["N"])
        e0 = sp["e0"]
        rho = L.cover_rule_rho(kp, srcs, e0, F(1, 8))
        assert L.score_walk_admissible(e0 - rho, e0 + rho)
        for reg, rr in (("cover", rho), ("cover/16", rho / 16)):
            yield dict(sp, rho=rr, regime=reg), kp, srcs


TERM_MAP = (("P_H", "A0*fH"), ("P_G", "A0*rho*fG"), ("P_4", "A0*rho^2*Env4/2"))


def summarize_cell(spec, cell):
    recs, o3 = [], []
    A0, A1, A2 = cell["A"]
    rho = cell["rho"]
    for o in cell["objs"]:
        per = {"r": o["r"]}
        for name, rt in o["routes"].items():
            mx = rt["max"]
            tm = rt["terms"]
            p0, p1, p2 = rt["p"]
            bnd = {"P_H": tm["A0*fH"], "P_G": tm["A0*rho*fG"], "P_4": tm["A0*rho^2*Env4/2"],
                   "P_1": 2 * A1 * p1, "P_0": A2 * p0}
            per[name] = {
                "rad": fl(rt["rad"]), "half": fl(rt["half"]), "max_abs_E2": fl(mx["E2"]),
                "looseness_rad_over_maxE2": fl(rt["rad"] / mx["E2"]) if mx["E2"] else None,
                "per_term_bound_over_truth": {k: (fl(bnd[k] / mx[k]) if mx[k] else None) for k in bnd},
                "per_term_bound_share_of_rad": {k: fl(bnd[k] / rt["rad"]) for k in bnd},
                "per_term_truth": {k: fl(mx[k]) for k in bnd},
                "per_term_sound": all(mx[k] <= bnd[k] for k in bnd),
                "identity_failures": mx["idfail"], "soundness_failures": mx["sound_fail"],
                "premise_max_ratio": fl(mx["prem_ratio_max"]), "env4_failures": mx["env4_fail"],
                "env4_over_max_phi4": fl(rt["env4"] / mx["phi4"]) if mx["phi4"] else None,
                "fG": fl(rt["fG"]), "sG": fl(rt["sG"]), "Gat": fl(rt["Gat"]),
                "nc_flip_detections": mx["nc_flip_fail"], "nc_e10_detections": mx["nc_e10_fail"],
                "split_bookkeeping_mismatch": mx["split_bookkeeping_mismatch"],
                "plant_d2R_noK2_eligible": mx["plant_d2R_noK2_eligible"], "plant_d2R_noK2_fired": mx["plant_d2R_noK2_fired"],
            }
        per["fG_split_over_exact_zero_residual"] = fl(o["fG_surr"] / X.sup_norm(o["phi3_zero"]))
        per["normonly_A0_over_pointwise_at_e0"] = (
            fl(A0 * X.sup_norm(o["phi3_zero"]) / abs(X.mat_vec(cell["P0"].R, o["phi3_zero"])[L.ATOM]))
            if X.mat_vec(cell["P0"].R, o["phi3_zero"])[L.ATOM] else None)
        per["Lambda_normonly_over_pointwise_at_e0"] = (
            fl(cell["P0"].Lam * X.sup_norm(o["phi3_zero"]) / abs(X.mat_vec(cell["P0"].R, o["phi3_zero"])[L.ATOM]))
            if X.mat_vec(cell["P0"].R, o["phi3_zero"])[L.ATOM] else None)
        recs.append(per)
        dh = O3.direct_hierarchy(cell, o)
        rg = O3.route_groups(cell, o, dh)
        ad = O3.adlr(cell, o)
        pl = O3.route_group_plants(cell, o, dh)
        adf = {}
        for kk, vv in ad.items():
            if isinstance(vv, dict):
                adf[kk] = {a: (fl(b) if isinstance(b, F) else b) for a, b in vv.items()}
            else:
                adf[kk] = vv
        o3.append({"r": o["r"], "identity_F3_at_atom": dh["identity_ok"],
                   "levels": {k: fl(v) for k, v in dh["levels"].items()},
                   "levels_over_truth": {k: (fl(v / dh["levels"]["T3_true"]) if dh["levels"]["T3_true"] else None)
                                         for k, v in dh["levels"].items()},
                   "levels_sound": all(v >= dh["levels"]["T3_true"] for v in dh["levels"].values()),
                   "groups": {k: ({kk: (fl(vv) if not isinstance(vv, bool) else vv) for kk, vv in v.items()}
                                  if isinstance(v, dict) else (fl(v) if not isinstance(v, bool) else v))
                              for k, v in rg.items()},
                   "adlr": adf, "ro3_plants": pl})
    j = cell["joint"]
    return {
        "spec": {k: str(v) for k, v in spec.items()},
        "rho": fl(rho), "C_cell": fl(cell["cb"]["C"]), "Lambda_e0": fl(cell["P0"].Lam),
        "k_cell": [fl(x) for x in cell["cb"]["k"]], "A_G": [fl(x) for x in cell["A"]],
        "rhoC": fl(rho * cell["cb"]["C"]),
        "per_r": recs,
        "assembly": {"sum_r_rad_over_m": fl(j["rad_perr_sum"]), "rad_joint": fl(j["rad_joint"]),
                     "perr_over_joint": fl(j["rad_perr_sum"] / j["rad_joint"]), "truth": fl(j["truth"]),
                     "joint_sound": j["truth"] <= j["rad_joint"]},
    }, o3


def main():
    t0 = time.time()
    p1 = part1()
    p2 = part2()
    cells_audit, cells_o3 = [], []
    for spec, kp, srcs in cell_specs():
        cell = CP.run_cell(kp, srcs, spec["e0"], spec["rho"], seed=zlib.crc32(str(sorted(spec.items())).encode()) % 100000)
        a, o3 = summarize_cell(spec, cell)
        cells_audit.append(a)
        cells_o3.append({"spec": a["spec"], "rho": a["rho"], "C_cell": a["C_cell"], "Lambda_e0": a["Lambda_e0"],
                         "rhoC": a["rhoC"], "per_r": o3})
    wall = time.time() - t0
    # ---------------------------------------------------------------- global verdicts
    def allrec():
        for c in cells_audit:
            for per in c["per_r"]:
                for name, v in per.items():
                    if isinstance(v, dict) and "rad" in v:
                        yield c, per, name, v
    id_fail = sum(v["identity_failures"] for _, _, _, v in allrec())
    sound_fail = sum(v["soundness_failures"] for _, _, _, v in allrec())
    env4_fail = sum(v["env4_failures"] for _, _, _, v in allrec())
    prem_ok = all(v["premise_max_ratio"] <= 1 for _, _, _, v in allrec())
    term_ok = all(v["per_term_sound"] for _, _, _, v in allrec())
    nc_flip = sum(1 for _, _, n, v in allrec() if n.startswith("real") and v["nc_flip_detections"] > 0)
    nc_flip_of = sum(1 for _, _, n, v in allrec() if n.startswith("real"))
    nc_e10 = sum(1 for _, _, n, v in allrec() if n == "surrogate" and v["nc_e10_detections"] > 0)
    nc_e10_of = sum(1 for _, _, n, v in allrec() if n == "surrogate")
    joint_ok = all(c["assembly"]["joint_sound"] for c in cells_audit)
    split_mis = sum(v["split_bookkeeping_mismatch"] for _, _, _, v in allrec())
    pid_el = sum(v["plant_d2R_noK2_eligible"] for _, _, n, v in allrec() if n == "surrogate")
    pid_fi = sum(v["plant_d2R_noK2_fired"] for _, _, n, v in allrec() if n == "surrogate")

    def route_stat(route, key, cls=None, regime=None):
        vals = []
        for c, per, name, v in allrec():
            if name != route:
                continue
            if cls and c["spec"]["class"] != cls:
                continue
            if regime and c["spec"]["regime"] != regime:
                continue
            x = v
            for kk in key:
                x = x[kk]
            vals.append(x)
        return stats(vals)

    summary = {}
    for cls in ("FX_A", "FX_B"):
        for reg in ("cover", "cover/16"):
            d = {}
            for route in ("surrogate", "zero_exactfG", f"real_eta{CP.ETA_G[0]}", f"real_eta{CP.ETA_G[1]}"):
                d[route] = {
                    "rad_over_maxE2": route_stat(route, ["looseness_rad_over_maxE2"], cls, reg),
                    "share_of_rad": {k: route_stat(route, ["per_term_bound_share_of_rad", k], cls, reg)
                                     for k in ("P_H", "P_G", "P_4", "P_1", "P_0")},
                    "bound_over_truth": {k: route_stat(route, ["per_term_bound_over_truth", k], cls, reg)
                                         for k in ("P_H", "P_G", "P_4", "P_1", "P_0")},
                    "env4_over_max_phi4": route_stat(route, ["env4_over_max_phi4"], cls, reg),
                }
            sel = [per for c in cells_audit if c["spec"]["class"] == cls and c["spec"]["regime"] == reg
                   for per in c["per_r"]]
            d["fG_split_over_exact_zero_residual"] = stats([p["fG_split_over_exact_zero_residual"] for p in sel])
            d["A0_normonly_over_pointwise_phi3"] = stats([p["normonly_A0_over_pointwise_at_e0"] for p in sel])
            d["Lambda_normonly_over_pointwise_phi3"] = stats([p["Lambda_normonly_over_pointwise_at_e0"] for p in sel])
            d["assembly_perr_over_joint"] = stats([c["assembly"]["perr_over_joint"] for c in cells_audit
                                                   if c["spec"]["class"] == cls and c["spec"]["regime"] == reg])
            d["rhoC"] = stats([c["rhoC"] for c in cells_audit if c["spec"]["class"] == cls and c["spec"]["regime"] == reg])
            summary[f"{cls}|{reg}"] = d
    audit = {
        "schema": "P5Y_K5_TAIL_OVERNIGHT_B307_AUDIT_FIXTURES/1",
        "producer": "streams/B_307/code/b307_run_fixtures.py",
        "declaration": "streams/B_307/VALIDATION_DECLARATION_B307.json",
        "class": "SYNTHETIC_VALIDATION",
        "cells_touched_CUSUM": [],
        "wall_seconds": wall,
        "P1_identities": p1,
        "P1_all_pass": all(c["pass"] for c in p1["checks"]),
        "P1_all_negative_controls_detected": all(c["detected"] for c in p1["negative_controls"]),
        "P2_ladders": p2,
        "P3_coverage": {"cells": len(cells_audit), "objects": sum(len(c["per_r"]) for c in cells_audit),
                        "grid_points_per_cell": 2 * CP.GRID + 1,
                        "routes": ["surrogate", "zero_exactfG"] + [f"real_eta{e}" for e in CP.ETA_G]},
        "P3_verdicts": {"E2_identity_and_split_failures": id_fail, "soundness_failures_|E2|>rad": sound_fail,
                        "premise_checks_all_hold": prem_ok, "env4_failures": env4_fail,
                        "every_term_individually_sound": term_ok, "assembly_joint_sound": joint_ok,
                        "class_b_NC_sign_flipped_centre_motion_detected_on": {"objects": nc_flip, "of": nc_flip_of},
                        "class_b_NC_E10_fG_zero_as_certificate_detected_on": {"objects": nc_e10, "of": nc_e10_of},
                        "class_a_plant_d2R_without_RK2R_through_identity_check": {"fired": pid_fi, "eligible_grid_points": pid_el},
                        "NON_EVIDENCE_class_c_five_way_split_bookkeeping_mismatches": split_mis},
        "P3_summary": summary,
        "P3_cells": cells_audit,
    }
    # ---------------------------------------------------------------- order-3 file
    def o3vals(key, cls=None, reg=None, route=None):
        vals = []
        for c in cells_o3:
            if cls and c["spec"]["class"] != cls:
                continue
            if reg and c["spec"]["regime"] != reg:
                continue
            for per in c["per_r"]:
                x = per
                try:
                    for kk in key:
                        x = x[kk]
                except KeyError:
                    continue
                vals.append(x)
        return vals
    o3sum = {}
    for cls in ("FX_A", "FX_B"):
        for reg in ("cover", "cover/16"):
            lv = cells_o3[0]["per_r"][0]["levels_over_truth"].keys()
            d = {"levels_over_truth": {k: stats(o3vals(["levels_over_truth", k], cls, reg)) for k in lv}}
            d["alpha"] = stats(o3vals(["groups", "alpha"], cls, reg))
            d["cover_factor_2k1rhoC"] = stats(o3vals(["groups", "cover_factor_2k1rhoC"], cls, reg))
            d["perron_index_normF3_over_C_normIKF3"] = stats(o3vals(["groups", "perron_index"], cls, reg))
            for eta in CP.ETA_G:
                nm = f"real_eta{eta}"
                d[nm] = {kk: stats(o3vals(["groups", nm, kk], cls, reg)) for kk in
                         ("Q_ratio_real_over_surrogate", "beta", "beta_envelope", "half_ratio_real_over_surrogate")}
            d["adlr"] = {}
            for v in ("G", "PM", "true", "oracle"):
                d["adlr"][v] = {kk: stats(o3vals(["adlr", v, kk], cls, reg)) for kk in
                                ("half_over_surrogate_half", f"half_over_real_eta{CP.ETA_G[0]}_half", "rad0", "rho_B3",
                                 "rho2_B4_over2")}
                d["adlr"][v]["pointwise_failures_total"] = sum(o3vals(["adlr", v, "pointwise_failures"], cls, reg))
                d["adlr"][v]["s_coefficient_B3_over_A0fGsurr"] = stats(o3vals(["adlr", "s_coefficient_B3_over_A0fGsurr", v], cls, reg))
            d["adlr"]["nc_B3_dropped_detected_objects"] = sum(1 for x in o3vals(["adlr", "nc_B3_dropped_detections"], cls, reg) if x > 0)
            d["adlr"]["objects"] = len(o3vals(["adlr", "nc_B3_dropped_detections"], cls, reg))
            o3sum[f"{cls}|{reg}"] = d
    all_levels_sound = all(per["levels_sound"] for c in cells_o3 for per in c["per_r"])
    all_ident = all(per["identity_F3_at_atom"] for c in cells_o3 for per in c["per_r"])
    env_ok = all(per["groups"][f"real_eta{eta}"]["envelope_ok"] for c in cells_o3 for per in c["per_r"] for eta in CP.ETA_G)
    floor_ok = all(per["groups"]["floor_ok_surrogate"] and all(per["groups"][f"real_eta{eta}"]["floor_ok"] for eta in CP.ETA_G)
                   for c in cells_o3 for per in c["per_r"])
    order3 = {
        "schema": "P5Y_K5_TAIL_OVERNIGHT_B307_ORDER3_FIXTURES/1",
        "producer": "streams/B_307/code/b307_run_fixtures.py (functions in b307_order3.py)",
        "class": "SYNTHETIC_VALIDATION",
        "cells_touched_CUSUM": [],
        "verdicts": {"F3_atom_identity_all_exact": all_ident, "every_direct_level_sound": all_levels_sound,
                     "proposition_RO3_E_envelope_holds": env_ok, "proposition_RO3_F_floor_holds": floor_ok,
                     "real_route_pointwise_soundness_failures": sound_fail,
                     "ADLR_G_certified_pointwise_failures": sum(per["adlr"]["G"]["pointwise_failures"] for c in cells_o3 for per in c["per_r"]),
                     "ADLR_true_proxy_pointwise_failures": sum(per["adlr"]["true"]["pointwise_failures"] for c in cells_o3 for per in c["per_r"]),
                     "ADLR_NC_B3_dropped_detected_objects": sum(1 for c in cells_o3 for per in c["per_r"] if per["adlr"]["nc_B3_dropped_detections"] > 0),
                     "ADLR_objects": sum(len(c["per_r"]) for c in cells_o3),
                     "class_a_RO3F_floor_plant": {"fired": sum(1 for c in cells_o3 for per in c["per_r"] if per["ro3_plants"]["floor_plant_fired"]),
                                                  "eligible": sum(1 for c in cells_o3 for per in c["per_r"] if per["ro3_plants"]["floor_plant_eligible"])},
                     "class_a_RO3E_envelope_plant": {"fired": sum(1 for c in cells_o3 for per in c["per_r"] if per["ro3_plants"]["envelope_plant_fired"]),
                                                     "of": sum(len(c["per_r"]) for c in cells_o3)}},
        "summary": o3sum,
        "cells": cells_o3,
    }
    (NS / "validation").mkdir(exist_ok=True)
    with open(NS / "validation" / "B307_AUDIT_FIXTURES.json", "w") as fh:
        json.dump(audit, fh, indent=1, default=str)
    with open(NS / "validation" / "B307_ORDER3_FIXTURES.json", "w") as fh:
        json.dump(order3, fh, indent=1, default=str)
    Q.log_execution("streams/B_307/code/b307_run_fixtures.py",
                    "B307 exact-fixture audit (identities, atom-constant ladders, TC per-term looseness, order-3 comparisons)",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION",
                    notes=f"cells={len(cells_audit)} wall={wall:.0f}s P1={audit['P1_all_pass']} "
                          f"NC={audit['P1_all_negative_controls_detected']} sound_fail={sound_fail}")
    print(json.dumps({"P1": audit["P1_all_pass"], "P1_NC": audit["P1_all_negative_controls_detected"],
                      "P2_fails": len(p2["rung_failures"]), "P2_plants": p2["class_a_plants_through_ladder_checks"], "P3": audit["P3_verdicts"],
                      "O3": order3["verdicts"], "wall": wall}, indent=1, default=str))


if __name__ == "__main__":
    main()
