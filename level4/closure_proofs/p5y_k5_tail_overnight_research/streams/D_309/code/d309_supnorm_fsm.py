"""Theorem SC (composite-sup premise supply for theorem TC / TC-T) -- exact-truth validation on synthetic FSM families.

Target-free: no CUSUM cell, no committed tail value, no drift in the quarantined band is touched.

For each declared fixture (rule DECLARED_RULE, fixed before the first run) and each source r:
  1. identity: phi^(j)(e0), j = 0..5, by the Leibniz path == by the independent polynomial path (exact);
  2. the order-3 ladder  TRUE <= S3 <= S2 <= S1 <= S0  (and TRUE <= S4), where
        S0 = 3 k1 sH + 3 k2 sD + k3 sF + sigma3            (TC-T surrogate, cell-uniform k_i)
        S1 = same with the exact MIDPOINT operator norms ||K_i(e0)||
        S2 = 3||K1 H^|| + 3||K2 D^|| + ||K3 F^|| + sigma3  (per-term composite: removes submultiplicativity)
        S3 = ||3 K1 H^ + 3 K2 D^ + K3 F^|| + sigma3        (candidate composite: also removes the cross-term triangle)
        S4 = ||S3^ + 3 K1 H^ + 3 K2 D^ + K3 F^|| + eps3    (full composite with a source candidate S3^, ||S''' - S3^|| <= eps3)
        TRUE = ||phi'''(e0)||;
  3. the order-4 ladder  sup_C ||phi''''|| <= E3 <= ... and E3 vs the (P3) envelope E0 (rigorous whole-cell composite);
  4. theorem TC enclosures for five premise supplies (base TC-T, SC3, SC3+E3, SC4+E3, TC+ order-raised) checked
     POINTWISE against the exact F_r''(t)(a) on a 33-point rational grid, and their rad(rho) ratios;
  5. controls (repair r1, review B1 and 'test power'): a COMPARATOR control (a wrong hand-written formula must differ
     from the polynomial path; it tests the comparator only); PREMISE-LEVEL truth checks (premise_truth: the atom
     constants vs exact ||R_e||, ||dR_e||, ||d2R_e|| on a drift grid, every f_* and Env4/f4/Env5 vs the exact quantity,
     the Taylor profiles p_j(s) vs the exact ||phi^(2-j)(t)||); planted-INVALID premise supplies (mutants) fed through
     premise_truth AND through tc_rad_poly + enclosure_check, with each check's detection power reported. The old NC2
     (rad := max_dev/2) was arithmetic and is withdrawn.
     Review N4: E3, Env5_comp and f4_comp are sups of phi_poly, which contains the EXACT source S(e); they are
     exact-source idealizations that real use cannot certify.
  6. adversarial fixtures (sign-aligned candidates) where the composite gain over S1 is expected to vanish.
Writes validation/D309_SUPNORM_FSM.json.
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_core as D  # noqa: E402

Q, X = D.Q, D.X

DECLARED_RULE = (
    "[repair r1, declared before the re-run: mutants fG_zero, Env4_zero, fG_Env4_half_truth, A0_half, A0_x0.99, "
    "Env4_midpoint_only, Env4_x0.9, fG_sigma3_dropped (sigma3 > 0 only) on the SC4_E3 supply; A-truth on a 9-point "
    "drift grid] Generic fixtures: seeds 1..24; n = 4 + seed % 4 states; kernel degree 4 in e (random_family, kill 1/5); "
    "e0 = 1/8; rho = (1/64, 1/32, 1/16)[seed % 3]; candidate perturbation pert = (1e-6, 1e-4, 1e-2)[(seed // 3) % 3] "
    "(uniform integer/100 multiples); source degree (2, 5)[seed % 2] (degree 2 => sigma3 = sigma4 = 0); two sources "
    "per fixture; G^ := 0 (premise P2'). Adversarial fixtures: seeds 101..106, n = 5, source degree 2, candidates set "
    "to the sign pattern of the maximising row of K_1(e0) (H^), K_2(e0) (D^), K_3(e0) (F^). Grid: 33 equispaced "
    "rational points on the closed cell. Fixed before the first run; no fixture is selected by outcome.")


def sgn(v: F) -> F:
    return F(1) if v >= 0 else F(-1)


def ladder(fx: D.TCFixture, k: list, rng: random.Random, pert: F) -> dict:
    K = fx.K
    sH, sD, sF = D.vnorm(fx.Hh), D.vnorm(fx.Dh), D.vnorm(fx.Fh)
    sig3 = D.vnorm(fx.S[3])
    t1, t2, t3 = D.mv(K[1], fx.Hh), D.mv(K[2], fx.Dh), D.mv(K[3], fx.Fh)
    comp = D.vadd((F(3), t1), (F(3), t2), (F(1), t3))
    S0 = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + sig3
    S1 = 3 * X.op_norm(K[1]) * sH + 3 * X.op_norm(K[2]) * sD + X.op_norm(K[3]) * sF + sig3
    S2 = 3 * D.vnorm(t1) + 3 * D.vnorm(t2) + D.vnorm(t3) + sig3
    S3 = D.vnorm(comp) + sig3
    noiseS = [pert * F(rng.randint(-100, 100), 100) for _ in range(fx.n)]
    S3hat = D.vadd((F(1), fx.S[3]), (F(1), noiseS))
    eps3 = D.vnorm(noiseS)
    S4 = D.vnorm(D.vadd((F(1), S3hat), (F(1), comp))) + eps3
    phi3_L = fx.phi_leibniz(3)
    phi3_P = fx.phi_poly_deriv_at0(3)
    TRUE = D.vnorm(phi3_L)
    # COMPARATOR control (relabelled, repair r1 / review B1): a wrong hand-written formula must differ from the
    # polynomial path. It tests the identity comparator only, not a premise supply.
    planted = D.vadd((F(1), fx.S[3]), (F(3), t1), (F(2), t2), (F(1), t3))
    nc1_detected = planted != phi3_P
    return {"S0": S0, "S1": S1, "S2": S2, "S3": S3, "S4": S4, "TRUE": TRUE, "sigma3": sig3,
            "identity_phi3": phi3_L == phi3_P, "comparator_control_differs": nc1_detected,
            "ladder_ok": TRUE <= S3 <= S2 <= S1 <= S0 and TRUE <= S4,
            "strict_submult": S2 < S1, "strict_crossterm": S3 < S2}


def env_levels(fx: D.TCFixture, k: list) -> dict:
    rho = fx.rho
    lo, hi = fx.lo, fx.hi
    sH, sD, sF = D.vnorm(fx.Hh), D.vnorm(fx.Dh), D.vnorm(fx.Fh)
    sig4 = D.sigma_cell(fx.sp, 4, lo, hi)
    sig5 = D.sigma_cell(fx.sp, 5, lo, hi)
    E0 = sig4 + 6 * k[2] * sH + 4 * k[3] * (sD + rho * sH) + k[4] * (sF + rho * sD + rho ** 2 * sH / 2)
    E3_up, E3_lo = fx.phi_poly_deriv_sup(4)
    sig4mid = D.vnorm(fx.S[4])
    f4_sur = sig4mid + 6 * k[2] * sH + 4 * k[3] * sD + k[4] * sF
    f4_comp = D.vnorm(fx.phi_leibniz(4))
    Env5_norm = sig5 + 10 * k[3] * sH + 5 * k[4] * (sD + rho * sH) + k[5] * (sF + rho * sD + rho ** 2 * sH / 2)
    E5_up, E5_lo = fx.phi_poly_deriv_sup(5)
    return {"E0": E0, "E3": E3_up, "E3_lower": E3_lo, "E3_lower_exact": E3_lo, "E5_lower_exact": E5_lo,
            "f4_sur": f4_sur, "f4_comp": f4_comp,
            "Env5_norm": Env5_norm, "Env5_comp": E5_up, "Env5_comp_lower": E5_lo,
            "env4_ok": E3_lo <= E3_up and E3_lo <= E0, "f4_ok": f4_comp <= f4_sur,
            "env5_ok": E5_lo <= E5_up and E5_lo <= Env5_norm}


def a_truth(fam, e0: F, rho: F, pts: int = 9) -> dict:
    """exact max over a drift grid of ||R_e||, ||dR_e|| = ||R K1 R||, ||d2R_e|| (lower bounds of the true sups)."""
    best = {"A0": F(0), "A1": F(0), "A2": F(0)}
    for j in range(pts):
        e = e0 - rho + 2 * rho * F(j, pts - 1)
        D.guard_interval(e, e)
        R, K1, K2 = fam.R(e), fam.K(e, 1), fam.K(e, 2)
        dR = X.mat_mul(X.mat_mul(R, K1), R)
        d2R = X.mat_add(X.mat_scale(X.mat_mul(X.mat_mul(dR, K1), R), F(2)), X.mat_mul(X.mat_mul(R, K2), R))
        best["A0"] = max(best["A0"], X.op_norm(R))
        best["A1"] = max(best["A1"], X.op_norm(dR))
        best["A2"] = max(best["A2"], X.op_norm(d2R))
    return best


def premise_truth(fx: D.TCFixture, A: tuple, prem: dict, at: dict, env: dict, variant: str = "TC",
                  grid: int = 32) -> list:
    """TRUTH-RELATIVE premise checks (repair r1, review 'test power'): every premise of theorem TC must dominate the
    exact quantity it bounds. Returns the violated premises (empty = pass). It can fail: see the mutants."""
    viol = []
    for name, val in zip(("A0", "A1", "A2"), A):
        if val < at[name]:
            viol.append(name)
    exact = {j: D.vnorm(fx.phi_poly_deriv_at0(j)) for j in range(5)}
    for key, j in (("F", 0), ("D", 1), ("H", 2), ("G", 3)):
        if prem[key] < exact[j]:
            viol.append("f_" + key)
    if variant == "TC":
        if prem["Env4"] < env["E3_lower_exact"]:
            viol.append("Env4")
    else:
        if prem["f4"] < exact[4]:
            viol.append("f4")
        if prem["Env5"] < env["E5_lower_exact"]:
            viol.append("Env5")
    p0, p1, p2 = D.tc_profile_polys(prem, variant)
    polys = fx.phi_poly()
    done = False
    for i in range(grid + 1):
        t = -fx.rho + 2 * fx.rho * F(i, grid)
        for pj, der in ((p2, 2), (p1, 1), (p0, 0)):
            tv = max(abs(D.p_eval(D.p_deriv(c, der), t)) for c in polys)
            if D.p_eval(pj, abs(t)) < tv:
                viol.append("profile_p%d" % der)
                done = True
                break
        if done:
            break
    return viol


def enclosure_check(fx: D.TCFixture, rad: list, grid: int = 32, plant: bool = False) -> dict:
    e0, rho = fx.e0, fx.rho
    Ha = fx.Hh[0]
    devs, rads = [], []
    for i in range(grid + 1):
        t = e0 - rho + 2 * rho * F(i, grid)
        s = abs(t - e0)
        devs.append(abs(fx.Fpp_at_atom(t) - Ha))
        rads.append(D.p_eval(rad, s))
    if plant:
        rads = [max(devs) / 2] * len(devs)
    viol = sum(1 for d, r in zip(devs, rads) if d > r)
    worst = max((d / r for d, r in zip(devs, rads) if r > 0), default=F(0))
    return {"violations": viol, "worst_dev_over_rad": float(worst), "max_dev": float(max(devs))}


def build(seed: int, n: int, rho: F, pert: F, sdeg: int, nsrc: int = 2, adversarial: bool = False):
    e0 = F(1, 8)
    fam = D.make_family(n, seed, e0 + rho, deg=4)
    sps = D.make_sources(n, nsrc, seed, deg=sdeg)
    rng = random.Random(90001 + seed)
    out = []
    for r, sp in enumerate(sps):
        famr = X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
        if adversarial:
            K1, K2, K3 = fam.K(e0, 1), fam.K(e0, 2), fam.K(e0, 3)
            xs = max(range(n), key=lambda x: sum(abs(a) for a in K1[x]))
            cand = {"H": [sgn(a) for a in K1[xs]], "D": [sgn(a) for a in K2[xs]], "F": [sgn(a) for a in K3[xs]]}
        else:
            Fd = famr.F_derivs(e0, 2)
            cand = {"F": D.perturbed(Fd[0], pert, rng), "D": D.perturbed(Fd[1], pert, rng),
                    "H": D.perturbed(Fd[2], pert, rng)}
        out.append((r, D.TCFixture(fam, sp, e0, rho, cand)))
    return fam, out


def run_fixture(seed: int, n: int, rho: F, pert: F, sdeg: int, adversarial: bool = False) -> list:
    fam, fxs = build(seed, n, rho, pert, sdeg, adversarial=adversarial)
    e0 = F(1, 8)
    lo, hi = e0 - rho, e0 + rho
    k = [D.k_cell(fam, i, lo, hi) for i in range(6)]
    C = D.C_cell(fam, e0, rho)
    A = D.lemma_g(k, C)
    rows = []
    at = a_truth(fam, e0, rho)
    for r, fx in fxs:
        rng = random.Random(4242 + 31 * seed + r)
        idents = {j: fx.phi_leibniz(j) == fx.phi_poly_deriv_at0(j) for j in range(6)}
        lad = ladder(fx, k, rng, pert)
        env = env_levels(fx, k)
        fF, fD, fH = (D.vnorm(fx.phi_leibniz(j)) for j in range(3))
        base = {"F": fF, "D": fD, "H": fH}
        fG_sc = min(lad["S0"], lad["S3"])
        fG_sc4 = min(lad["S0"], lad["S3"], lad["S4"])
        E4 = min(env["E0"], env["E3"])
        variants = {
            "TCT_base": D.tc_rad_poly(A, dict(base, G=lad["S0"], Env4=env["E0"])),
            "SC3": D.tc_rad_poly(A, dict(base, G=fG_sc, Env4=env["E0"])),
            "SC3_E3": D.tc_rad_poly(A, dict(base, G=fG_sc, Env4=E4)),
            "SC4_E3": D.tc_rad_poly(A, dict(base, G=fG_sc4, Env4=E4)),
            "SC4_TCplus": D.tc_rad_poly(A, dict(base, G=fG_sc4, f4=min(env["f4_sur"], env["f4_comp"]),
                                                Env5=min(env["Env5_norm"], env["Env5_comp"])), variant="TCp"),
        }
        rad_rho = {kname: D.p_eval(p, fx.rho) for kname, p in variants.items()}
        checks = {kname: enclosure_check(fx, p) for kname, p in variants.items()}
        supplies = {
            "TCT_base": (dict(base, G=lad["S0"], Env4=env["E0"]), "TC"),
            "SC3": (dict(base, G=fG_sc, Env4=env["E0"]), "TC"),
            "SC3_E3": (dict(base, G=fG_sc, Env4=E4), "TC"),
            "SC4_E3": (dict(base, G=fG_sc4, Env4=E4), "TC"),
            "SC4_TCplus": (dict(base, G=fG_sc4, f4=min(env["f4_sur"], env["f4_comp"]),
                                Env5=min(env["Env5_norm"], env["Env5_comp"])), "TCp")}
        genuine_viol = {kname: premise_truth(fx, A, pr, at, env, var) for kname, (pr, var) in supplies.items()}
        g4 = dict(base, G=fG_sc4, Env4=E4)
        mut = {
            "fG_zero": (dict(g4, G=F(0)), A),
            "Env4_zero": (dict(g4, Env4=F(0)), A),
            "fG_Env4_half_truth": (dict(g4, G=lad["TRUE"] / 2, Env4=env["E3_lower"] / 2), A),
            "A0_half": (g4, (A[0] / 2, A[1], A[2])),
            "A0_x0.99": (g4, (A[0] * F(99, 100), A[1], A[2])),
            "Env4_midpoint_only": (dict(g4, Env4=env["f4_comp"]), A),
            "Env4_x0.9": (dict(g4, Env4=E4 * F(9, 10)), A),
        }
        if lad["sigma3"] > 0:
            mut["fG_sigma3_dropped"] = (dict(g4, G=lad["S3"] - lad["sigma3"]), A)
        mutants = {}
        for mname, (pr, AA) in mut.items():
            mutants[mname] = {"premise_check_flags": premise_truth(fx, AA, pr, at, env, "TC"),
                              "enclosure_violations": enclosure_check(fx, D.tc_rad_poly(AA, pr))["violations"]}
        rows.append({
            "seed": seed, "r": r, "n": n, "rho": str(rho), "pert": str(pert), "source_degree": sdeg,
            "adversarial": adversarial,
            "identity_all_orders": all(idents.values()),
            "ladder": {kk: (float(v) if isinstance(v, F) else v) for kk, v in lad.items()},
            "env": {kk: (float(v) if isinstance(v, F) else v) for kk, v in env.items()},
            "ratios": {
                "S3_over_S0": float(lad["S3"] / lad["S0"]), "S3_over_S1": float(lad["S3"] / lad["S1"]),
                "S2_over_S1": float(lad["S2"] / lad["S1"]), "S1_over_S0": float(lad["S1"] / lad["S0"]),
                "TRUE_over_S0": float(lad["TRUE"] / lad["S0"]),
                "S4_over_S0": float(lad["S4"] / lad["S0"]),
                "E3_over_E0": float(env["E3"] / env["E0"]),
                "rad_rho_over_base": {kk: float(v / rad_rho["TCT_base"]) for kk, v in rad_rho.items()},
            },
            "enclosure_checks": checks,
            "premise_truth_genuine_violations": genuine_viol,
            "mutants": mutants,
        })
    return rows


def main() -> None:
    t0 = time.time()
    out = {"schema": "OV_D309_SUPNORM_FSM/1", "declared_rule": DECLARED_RULE, "rows": []}
    for seed in range(1, 25):
        n = 4 + seed % 4
        rho = (F(1, 64), F(1, 32), F(1, 16))[seed % 3]
        pert = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 2))[(seed // 3) % 3]
        sdeg = (2, 5)[seed % 2]
        out["rows"].extend(run_fixture(seed, n, rho, pert, sdeg))
    for seed in range(101, 107):
        out["rows"].extend(run_fixture(seed, 5, F(1, 32), F(0), 2, adversarial=True))
    rows = out["rows"]
    gen = [r for r in rows if not r["adversarial"]]
    adv = [r for r in rows if r["adversarial"]]

    def rng_of(key, sub=None, rs=gen):
        vals = [(r["ratios"][key] if sub is None else r["ratios"][key][sub]) for r in rs]
        return [min(vals), max(vals)]
    out["summary"] = {
        "cases_generic": len(gen), "cases_adversarial": len(adv),
        "identity_all_orders_all": all(r["identity_all_orders"] for r in rows),
        "ladder_ok_all": all(r["ladder"]["ladder_ok"] for r in rows),
        "env_ok_all": all(r["env"]["env4_ok"] and r["env"]["f4_ok"] and r["env"]["env5_ok"] for r in rows),
        "comparator_control_differs": sum(1 for r in rows if r["ladder"]["comparator_control_differs"]),
        "premise_truth_genuine_violations_total": sum(len(v) for r in rows
                                                      for v in r["premise_truth_genuine_violations"].values()),
        "premise_truth_supplies_checked": sum(len(r["premise_truth_genuine_violations"]) for r in rows),
        "mutant_power": {m: {"applicable": sum(1 for r in rows if m in r["mutants"]),
                             "premise_check_detects": sum(1 for r in rows if m in r["mutants"]
                                                          and r["mutants"][m]["premise_check_flags"]),
                             "enclosure_check_detects": sum(1 for r in rows if m in r["mutants"]
                                                            and r["mutants"][m]["enclosure_violations"] > 0)}
                         for m in ("fG_zero", "Env4_zero", "fG_Env4_half_truth", "A0_half", "A0_x0.99",
                                   "Env4_midpoint_only", "Env4_x0.9", "fG_sigma3_dropped")},
        "enclosure_worst_dev_over_rad_genuine": max(c["worst_dev_over_rad"] for r in rows
                                                    for c in r["enclosure_checks"].values()),
        "enclosure_violations_total": sum(c["violations"] for r in rows for c in r["enclosure_checks"].values()),
        "enclosure_points_checked": sum(33 * len(r["enclosure_checks"]) for r in rows),
        "strict_submult_generic": sum(1 for r in gen if r["ladder"]["strict_submult"]),
        "strict_crossterm_generic": sum(1 for r in gen if r["ladder"]["strict_crossterm"]),
        "S3_over_S0_generic": rng_of("S3_over_S0"),
        "S3_over_S1_generic": rng_of("S3_over_S1"),
        "S2_over_S1_generic": rng_of("S2_over_S1"),
        "S1_over_S0_generic": rng_of("S1_over_S0"),
        "TRUE_over_S0_generic": rng_of("TRUE_over_S0"),
        "E3_over_E0_generic": rng_of("E3_over_E0"),
        "rad_rho_over_base_generic": {v: rng_of("rad_rho_over_base", v) for v in
                                      ("SC3", "SC3_E3", "SC4_E3", "SC4_TCplus")},
        "S3_over_S1_adversarial": rng_of("S3_over_S1", rs=adv),
        "S2_over_S1_adversarial": rng_of("S2_over_S1", rs=adv),
        "by_source_degree": {
            str(d): {"S3_over_S0": rng_of("S3_over_S0", rs=[r for r in gen if r["source_degree"] == d]),
                     "rad_SC4_E3_over_base": rng_of("rad_rho_over_base", "SC4_E3",
                                                    rs=[r for r in gen if r["source_degree"] == d])}
            for d in (2, 5)},
        "by_pert": {
            p: {"S3_over_S0": rng_of("S3_over_S0", rs=[r for r in gen if r["pert"] == p]),
                "TRUE_over_S0": rng_of("TRUE_over_S0", rs=[r for r in gen if r["pert"] == p])}
            for p in sorted({r["pert"] for r in gen})},
        "wall_s": round(time.time() - t0, 2),
    }
    p = D.NS / "validation" / "D309_SUPNORM_FSM.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_execution("streams/D_309/code/d309_supnorm_fsm.py",
                    "theorem SC composite-sup: identity, ladder, TC enclosure soundness, NCs on synthetic FSM",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
