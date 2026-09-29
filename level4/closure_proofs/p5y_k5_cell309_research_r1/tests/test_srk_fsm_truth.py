"""THEOREM_SRK end to end against EXACT truth on synthetic finite-state drift families (no CUSUM, no band drift).

For each declared seed (rule fixed before the first run, below):
  * exact F, F', F'' at e0; candidates = exact + perturbation; G := 0 (P2');
  * TC-T premises (s_X, f_*, sigma3, sigma4, k_i, f_G, Env4, Lemma-G A from the certified cell bound C);
  * FSM analogue of the state-resolved norm: kbar_i(x) = sum_y sup_{e in C} |K_i(e)_{xy}|  (>= sup_e k_i(x; e));
  * Gamma_i = certified supersolution value (overnight d309_rso.certify: two independent rigorous checks);
  * rad_srk (impl/srk_assemble.py) vs exact |F''(e)(a) - H(a)| on 33 points of the cell;
  * pointwise premises: |phi'''(e0)(x)| <= Psi3(x) and sup_s |phi''''(s)(x)| <= Psi4(x) exactly/rigorously;
  * dominance rad_srk <= rad_tct;
  * mutants: (M1) Gamma halved, (M2) SRK min dropped (raw SRK coefficients used even when larger),
    (M3) coefficient 3 -> 1 on the s_H term of B3, (M4) Psi3 without the sigma3 term.  A mutant is 'caught' when
    it violates exact truth, a pointwise premise, or dominance.

DECLARED RULE: seeds 1..12; n = 4 + seed % 4; kernel degree 4; e0 = 1/8; rho = (1/64, 1/32, 1/16)[seed % 3];
pert = (1e-6, 1e-4, 1e-2)[(seed // 3) % 3]; one source of degree (2, 5)[seed % 2].
"""
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
OV = NS.parent / "p5y_k5_tail_overnight_research"
for p in (NS / "impl", NS / "code", OV / "code", OV / "streams" / "D_309" / "code"):
    sys.path.insert(0, str(p))
import q309_guard as Q  # noqa: E402

Q.install_import_guard()
import d309_core as D  # noqa: E402
import d309_rso as RSO  # noqa: E402
import srk_assemble as SA  # noqa: E402

PERTS = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 100))
RHOS = (F(1, 64), F(1, 32), F(1, 16))


def case(seed: int) -> dict:
    n = 4 + seed % 4
    rho = RHOS[seed % 3]
    pert = PERTS[(seed // 3) % 3]
    e0 = F(1, 8)
    lo, hi = e0 - rho, e0 + rho
    fam = D.make_family(n, seed, F(1, 4), deg=4)
    sp = D.make_sources(n, 1, seed, deg=(2, 5)[seed % 2])[0]
    famr = D.X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
    Fd = famr.F_derivs(e0, 3)
    rng = random.Random(1000 + seed)
    cand = {"F": D.perturbed(Fd[0], pert, rng), "D": D.perturbed(Fd[1], pert, rng), "H": D.perturbed(Fd[2], pert, rng)}
    fx = D.TCFixture(fam, sp, e0, rho, cand)
    sF, sD, sH = D.vnorm(cand["F"]), D.vnorm(cand["D"]), D.vnorm(cand["H"])
    phi = [fx.phi_leibniz(j) for j in range(4)]
    fF, fD, fH = D.vnorm(phi[0]), D.vnorm(phi[1]), D.vnorm(phi[2])
    k = [None] + [D.k_cell(fam, i, lo, hi) for i in range(1, 5)]
    sigma3 = D.sigma_cell(sp, 3, e0, e0)
    sigma4 = D.sigma_cell(sp, 4, lo, hi)
    fG = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + sigma3
    Env4 = sigma4 + 6 * k[2] * sH + 4 * k[3] * (sD + rho * sH) + k[4] * (sF + rho * sD + rho ** 2 * sH / 2)
    C = D.C_cell(fam, e0, rho)
    A0, A1, A2 = D.lemma_g(k, C)
    fields = {"sF": sF, "sD": sD, "sH": sH, "fF": fF, "fD": fD, "fH": fH, "fG": fG, "Env4": Env4,
              "sigma3": sigma3, "eps3": F(0), "sigma4": sigma4, "rho": rho, "A0": A0, "A1": A1, "A2": A2}
    # FSM state-resolved norms and certified weighted resolvent bounds
    kbar = {}
    for i in (1, 2, 3, 4):
        M = RSO.abs_sup_matrix(fam, i, lo, hi)
        kbar[i] = [sum(row) for row in M]
    gam = {i: RSO.certify(fam, e0, rho, kbar[i])["va"] for i in (1, 2, 3, 4)}
    out = SA.rad_srk(fields, gam)
    # ---- pointwise premises (exact at e0; rigorous whole-cell sup for order 4)
    psi3 = [sigma3 + 3 * sH * kbar[1][x] + 3 * sD * kbar[2][x] + sF * kbar[3][x] for x in range(n)]
    psi4 = [sigma4 + 6 * sH * kbar[2][x] + 4 * (sD + rho * sH) * kbar[3][x]
            + (sF + rho * sD + rho ** 2 * sH / 2) * kbar[4][x] for x in range(n)]
    p3_ok = all(abs(phi[3][x]) <= psi3[x] for x in range(n))
    polys = fx.phi_poly()
    p4_ok = all(D.sup_abs_on(D.p_deriv(polys[x], 4), -rho, rho)[0] <= psi4[x] for x in range(n))
    # ---- exact truth over the cell
    ts = [lo + (hi - lo) * F(j, 32) for j in range(33)]
    dev = max(abs(famr.F_derivs(t, 2)[2][0] - cand["H"][0]) for t in ts)
    ok_truth = dev <= out["rad_srk"]
    ok_dom = out["rad_srk"] <= out["rad_tct"]
    # ---- premise-level exact truth (load-bearing; review lesson: radius-level truth checks are weak)
    egrid = [lo + (hi - lo) * F(j, 16) for j in range(17)]
    Rs = {e: fam.R(e) for e in egrid}
    g_truth = {i: max(D.mv(Rs[e], kbar[i])[0] for e in egrid) for i in (1, 2, 3, 4)}
    ok_gamma = all(gam[i] >= g_truth[i] for i in (1, 2, 3, 4))
    a3 = [abs(v) for v in phi[3]]
    b3_truth = max(D.mv(Rs[e], a3)[0] for e in egrid)
    sgrid = [-rho + 2 * rho * F(j, 16) for j in range(17)]
    q4 = [max(abs(D.p_eval(D.p_deriv(polys[x], 4), s_)) for s_ in sgrid) for x in range(n)]
    b4_truth = max(D.mv(Rs[e], q4)[0] for e in egrid)
    ok_b = out["B3"] >= b3_truth and out["B4"] >= b4_truth
    # ---- mutants
    mut = {}
    half = {i: gam[i] / 2 for i in gam}
    m1 = SA.rad_srk(fields, half)
    mut["M1_gamma_half"] = {"rad": m1["rad_srk"], "caught_truth": dev > m1["rad_srk"],
                            "caught_premise": any(half[i] < g_truth[i] for i in half)
                            or m1["B3"] < b3_truth or m1["B4"] < b4_truth}
    raw3, raw4 = out["B3_srk_raw"], out["B4_srk_raw"]
    p0, p1, p2 = SA.p_terms({kk: F(v) for kk, v in fields.items()})
    m2 = A0 * fH + rho * raw3 + rho ** 2 / 2 * raw4 + 2 * A1 * p1 + A2 * p0
    mut["M2_min_dropped"] = {"rad": m2, "applicable": (raw3 > A0 * fG) or (raw4 > A0 * Env4),
                             "caught_dominance": m2 > out["rad_tct"], "caught_truth": dev > m2}
    b3 = min(A0 * fG, A0 * sigma3 + 1 * sH * gam[1] + 3 * sD * gam[2] + sF * gam[3])
    m3 = A0 * fH + rho * b3 + rho ** 2 / 2 * out["B4"] + 2 * A1 * p1 + A2 * p0
    mut["M3_coef3to1"] = {"rad": m3, "caught_truth": dev > m3, "caught_premise": b3 < b3_truth}
    psi3_bad = [3 * sH * kbar[1][x] + 3 * sD * kbar[2][x] + sF * kbar[3][x] for x in range(n)]
    mut["M4_sigma3_dropped"] = {"caught_pointwise": not all(abs(phi[3][x]) <= psi3_bad[x] for x in range(n))}
    return {"seed": seed, "n": n, "rho": str(rho), "pert": str(pert),
            "rad_srk": float(out["rad_srk"]), "rad_tct": float(out["rad_tct"]), "dev": float(dev),
            "ratio_srk_tct": float(out["rad_srk"] / out["rad_tct"]), "branch3": out["branch3"],
            "branch4": out["branch4"], "ok_truth": ok_truth, "ok_dominance": ok_dom,
            "ok_pointwise3": p3_ok, "ok_pointwise4": p4_ok, "ok_gamma_premise": ok_gamma, "ok_B_premise": ok_b,
            "gamma_over_truth": {i: float(gam[i] / g_truth[i]) for i in gam},
            "gain_gamma_vs_A0kappa": {i: float(gam[i] / (A0 * k[i])) for i in gam},
            "mutants": {kk: {a: (float(b) if isinstance(b, F) else b) for a, b in v.items()} for kk, v in mut.items()}}


def run():
    Q.log_execution("tests/test_srk_fsm_truth.py", "SRK exact-truth FSM validation", klass="SYNTHETIC_VALIDATION",
                    notes="synthetic finite-state families, drifts in [0, 1/4]")
    rows = [case(s) for s in range(1, 13)]
    ok = all(r["ok_truth"] and r["ok_dominance"] and r["ok_pointwise3"] and r["ok_pointwise4"]
             and r["ok_gamma_premise"] and r["ok_B_premise"] for r in rows)
    caught = {m: sum(1 for r in rows if any(v for kk, v in r["mutants"][m].items() if kk.startswith("caught")))
              for m in rows[0]["mutants"]}
    caught["M2_min_dropped_applicable_cases"] = sum(1 for r in rows if r["mutants"]["M2_min_dropped"]["applicable"])
    return ok, rows, caught


if __name__ == "__main__":
    ok, rows, caught = run()
    out = {"all_genuine_ok": ok, "mutants_caught_of_12": caught,
           "ratio_srk_tct": [round(r["ratio_srk_tct"], 4) for r in rows],
           "branches": [(r["branch3"], r["branch4"]) for r in rows], "rows": rows}
    (NS / "evidence").mkdir(exist_ok=True)
    (NS / "evidence" / "SRK_FSM_TRUTH.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print({k: out[k] for k in ("all_genuine_ok", "mutants_caught_of_12", "ratio_srk_tct", "branches")})
    sys.exit(0 if ok else 1)
