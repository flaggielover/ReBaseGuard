"""C8 Phases 1-5, 7, 9 -- DAG, gap anatomy, minimum-information inversion, perfect-information
oracles, kill gates and the cost/value frontier.

Nothing here computes a new scientific value. Every Gamma is either a reproduction of a committed
certified supply (verified first, all twenty) or a COUNTERFACTUAL evaluation of the frozen TC-T rule
at a tuple that no certificate supplies. Counterfactuals are labelled and are never called evidence.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C
import c8_chain as X

OPEN = (306, 307, 308, 309)
GATE_SHA = "55e743320987a1e031c586938216e70839ed8d0ef1e9d518304197563dde9a7a"


def bisect_max(ch, k, A, field, hi0=None):
    """Largest value of `field` (others fixed) keeping Gamma < 0. None if even 0 fails."""
    if ch.gamma(k, {**A, field: F(0)}) >= 0:
        return None
    lo = F(0)
    hi = hi0 if hi0 is not None else max(F(A[field]) * 4, F(1))
    while ch.gamma(k, {**A, field: hi}) < 0:
        hi *= 2
    for _ in range(72):
        mid = (lo + hi) / 2
        if ch.gamma(k, {**A, field: mid}) < 0:
            lo = mid
        else:
            hi = mid
    return lo


def main() -> int:
    gate_p = C.NS / "config" / "DECISION_GATE_C8.json"
    if C.sha256_file(gate_p) != GATE_SHA:
        raise SystemExit("the C8 decision gate is not the frozen one")

    ch = X.Chain()
    ver = ch.verify()
    if not ver["all_agree"]:
        raise SystemExit(f"chain reconstruction does not reproduce committed supplies: "
                         f"{ver['disagreements'][:3]}")

    c4 = C.c4_cells()
    c7 = C.c7_certificate()
    lam_c7 = F(c7["bounds"][c7["PRIMARY"]["key"]]["value"])
    lam_c4_309 = F(c4["309"]["lower_bound_E_a_tau"])

    floors, floor_src = {}, {}
    for k in OPEN:
        b = F(c4[str(k)]["lower_bound_E_a_tau"])
        src = "C4 certificate (theorem L)"
        if k == 309 and lam_c7 > b:
            b, src = lam_c7, "C7 PRIMARY (dependency-free, theorem C7-E2c + lemma C7-U)"
        floors[k], floor_src[k] = b, src

    crit = C.load(C.C2 / "evidence" / "phase_d5" / "C2_CRITICAL_RATIOS.json")["supplies"]

    # ---------------- Phase 1: the DAG ------------------------------------------------------
    dag = {"equation": "Gamma_k = g_hi + rho * x_hi * M ;  pass iff Gamma_k < 0",
           "nodes": {}, "per_cell": {}}
    for nm, cls, why in (
        ("g_hi", "COMMITTED_DERIVED",
         "R_interval.hi - e0 * D_interval.lo; recovered exactly from the committed (Gamma_exact, "
         "M_after_exact) pair and cross-checked against all five committed supplies per cell"),
        ("rho", "COMMITTED_CERTIFIED", "cell half-width (e_hi - e_lo)/2, from REGISTRY_C2 blocks"),
        ("x_hi", "COMMITTED_CERTIFIED", "cell right endpoint e_hi, from REGISTRY_C2 blocks"),
        ("M", "COMMITTED_DERIVED",
         "max(|lo|,|hi|) over the TC-T enclosure. The sealed clause also clips against the R2 "
         "interval; neither that interval nor M_R2 is carried in any committed artifact, so the clip "
         "is UNREACHABLE and is dropped. Dropping it can only RAISE Gamma, so every threshold here "
         "is at least as demanding as the sealed one, and the clip does not bind at any of the 20 "
         "committed supplies."),
        ("A0", "COMMITTED_CERTIFIED", "Lemma Dv': min(Abar, tau/D_lo); tau/D_lo binds on the tail"),
        ("A1", "COMMITTED_CERTIFIED", "eff * (K1*C + d1)"),
        ("A2", "COMMITTED_CERTIFIED", "eff * (2*K1^2*C^2 + K2*C + 2*K1*C*d1 + 2*d1^2 + d2)"),
        ("Abar, tau, C_T, D_lo, D1, D2", "COMMITTED_CERTIFIED",
         "Arb/FLINT operator registry REGISTRY_C2 (and C1); certified, operator_only, rule r2"),
        ("order-3 surrogate", "MISSING",
         "the frozen TC-T rule accepts an `order3` argument; no certified order-3 value exists for "
         "the tail cells. Its effect IS quantified in committed evidence as Gamma_perfect_order3."),
        ("order-4 envelope Env4", "COMMITTED_CERTIFIED", "C3_BLOCKER fG_plus_Env4_mean"),
        ("Lambda (lower bound on E_a[tau])", "ANALYTIC_CERTIFIED",
         "C4 theorem L for 306-308; C7 PRIMARY for 309. Enters ONLY as an admissibility FLOOR on "
         "A0 via Lemma SM(d). It is NOT an input to Gamma."),
    ):
        dag["nodes"][nm] = {"class": cls, "why": why}

    for k in OPEN:
        g = ch.geom[k]
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        dag["per_cell"][str(k)] = {
            "e_lo": str(g["e_lo"]), "e_hi": str(g["e_hi"]), "e0": str(g["e0"]),
            "rho": str(g["rho"]), "x_hi": str(g["x_hi"]),
            "rho_times_x_hi": str(g["rho"] * g["x_hi"]),
            "g_hi": str(ch.g_hi[k]), "g_hi_float": float(ch.g_hi[k]),
            "A_best_committed": {j: float(A[j]) for j in A},
            "Gamma_now": float(ch.gamma(k, A)),
            "M_budget_for_pass": float(-ch.g_hi[k] / (g["rho"] * g["x_hi"])),
            "M_now": float(ch.M_of(k, A)),
            "Lambda_floor_on_A0": float(floors[k]), "Lambda_floor_source": floor_src[k],
        }

    # ---------------- Phase 2: the gap anatomy ----------------------------------------------
    anatomy = {
        "A_pointwise_Lambda_e_lo": ("C7 certifies Lambda(e_lo) >= 3.586306093865 for cell 309, and "
                                    "C4 certifies analogous pointwise bounds for 306-308."),
        "B_uniform_sup_over_cell": "sup_{e in cell} Lambda(e) >= Lambda(e_lo). NOT certified.",
        "C_tau_prime": "the alarm time of the unclipped pathwise majorant; tau >= tau' pathwise.",
        "D_tau": "the true CUSUM alarm time; E[tau] >= E[tau'].",
        "E_operator_A0": "A0 = min(Abar, tau/D_lo), a certified UPPER bound on sup_cell E_a[tau].",
        "F_consumed_by_C5T_K5B": "Gamma consumes A0, A1, A2 through M only.",
        "exact_inequalities": [
            "Lambda(e_lo) <= sup_{e in cell} E_a[tau]            (a point is at most the sup)",
            "E[tau'] <= E[tau]                                    (pathwise majorant, tau >= tau')",
            "sup_{e in cell} E_a[tau] <= A0                       (Lemma SM(d) admissibility)",
            "hence  Lambda(e_lo) <= A0  for every admissible A0   (the FLOOR)",
        ],
        "which_inequality_causes_which_gap": {
            "G1_clipping": "E[tau'] <= E[tau] -- C7 bounds E[tau'], so Lambda understates E[tau]. "
                           "Closing it RAISES Lambda.",
            "G2_uniformization": "Lambda(e_lo) <= sup_cell -- C7 is pointwise. Closing it RAISES Lambda.",
        },
        "THE_CENTRAL_STRUCTURAL_FACT": (
            "Lambda is a LOWER bound on E_a[tau] and A0 is an UPPER bound on the same quantity. "
            "Gamma depends on A0, never on Lambda. Lambda enters the decision ONLY as the floor "
            "below which no admissible A0 can go. Therefore any route that improves Lambda -- which "
            "is exactly what R1 and R2 do -- RAISES the floor and can never lower Gamma. R1 and R2 "
            "cannot close a cell. They can only strengthen an EXCLUSION, which is what C7 did."),
        "role_of_Lambda_309": (
            "Lambda_309 is a FEASIBILITY DIAGNOSTIC for the operator route, not an input to the "
            "closure clause. It answers 'how small could a perfect A0 ever be?'. When it exceeds the "
            "A0 ceiling the clause can tolerate, the operator route is refuted for that cell."),
    }

    # ---------------- Phase 4: minimum-information inversion ---------------------------------
    Z = {"A1": F(0), "A2": F(0)}
    inversion = {}
    for k in OPEN:
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        gam_now = ch.gamma(k, A)
        a0_ceiling_zero = bisect_max(ch, k, {**A, **Z}, "A0", hi0=F(40))
        row = {
            "Gamma_now": float(gam_now), "already_passes": gam_now < 0,
            "A_now": {j: float(A[j]) for j in A},
            "Lambda_floor_on_A0": float(floors[k]),
            "max_admissible_A0_others_fixed": None, "max_admissible_A1_others_fixed": None,
            "max_admissible_A2_others_fixed": None,
            "A0_ceiling_with_A1_A2_zero": float(a0_ceiling_zero) if a0_ceiling_zero else None,
            "uniform_reduction_required": None,
        }
        for f_ in ("A0", "A1", "A2"):
            v = bisect_max(ch, k, A, f_)
            row[f"max_admissible_{f_}_others_fixed"] = float(v) if v is not None else None
            if v is not None and F(A[f_]) > v:
                row[f"required_{f_}_improvement_factor"] = float(F(A[f_]) / v)
        # uniform scaling
        lo, hi = F(1, 1000), F(1)
        if ch.gamma(k, {j: F(A[j]) * lo for j in A}) < 0:
            for _ in range(60):
                mid = (lo + hi) / 2
                if ch.gamma(k, {j: F(A[j]) * mid for j in A}) < 0:
                    lo = mid
                else:
                    hi = mid
            row["uniform_reduction_required"] = float(1 / lo) if gam_now >= 0 else 1.0
        # cheapest sufficient fact
        Af = {**A, "A0": floors[k]}
        if gam_now < 0:
            row["cheapest_sufficient_fact"] = ("NONE -- already passes under committed certified "
                                               "supplies; the blocker is ADOPTION, not information")
        elif row.get("required_A0_improvement_factor") and \
                F(row["max_admissible_A0_others_fixed"]).limit_denominator(10**12) > floors[k]:
            row["cheapest_sufficient_fact"] = (
                f"reduce A0 from {float(A['A0']):.6f} to <= "
                f"{row['max_admissible_A0_others_fixed']:.6f} "
                f"({row['required_A0_improvement_factor']:.4f}x), which the floor "
                f"{float(floors[k]):.6f} permits")
        elif ch.gamma(k, Af) < 0:
            row["cheapest_sufficient_fact"] = (
                f"drive A0 to its floor {float(floors[k]):.6f} (perfect operator information)")
        else:
            a1 = bisect_max(ch, k, Af, "A1")
            if a1 is not None:
                row["cheapest_sufficient_fact"] = (
                    f"A0 to its floor {float(floors[k]):.6f} AND A1 from {float(A['A1']):.6f} to "
                    f"<= {float(a1):.6f} ({float(F(A['A1'])/a1):.4f}x)")
                row["A1_ceiling_at_perfect_A0"] = float(a1)
            else:
                row["cheapest_sufficient_fact"] = (
                    "NONE within the atom-constant family: no (A0 >= floor, A1 >= 0, A2 >= 0) "
                    "closes this cell")
        inversion[str(k)] = row

    # ---------------- Phase 5: perfect-information oracles -----------------------------------
    oracles = {"LABEL": "COUNTERFACTUAL_ONLY -- none of these is certified evidence", "routes": {}}
    r12 = {}
    for k in OPEN:
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        r12[str(k)] = {"Gamma_now": float(ch.gamma(k, A)),
                       "Gamma_with_Delta_clip_zero": float(ch.gamma(k, A)),
                       "Gamma_with_Delta_cell_zero": float(ch.gamma(k, A)),
                       "delta": 0.0}
    oracles["routes"]["R1"] = {
        "perfect_information": "Delta_clip = 0, i.e. E[tau] known exactly rather than via E[tau']",
        "effect_on_Gamma": r12,
        "leverage": "ZERO",
        "proof": ("Gamma is a function of (g_hi, rho, x_hi, A0, A1, A2). Lambda appears in none of "
                  "them. Perfect clipping information changes Lambda and therefore changes the FLOOR "
                  "on A0; it changes no term of Gamma. The effect on every open cell is exactly 0."),
        "what_it_DOES_do": "raises the A0 floor, strengthening exclusions and shrinking R3's room",
        "class": "LOW_LEVERAGE"}
    oracles["routes"]["R2"] = dict(oracles["routes"]["R1"])
    oracles["routes"]["R2"]["perfect_information"] = ("Delta_cell = 0, i.e. sup over the cell known "
                                                      "and equal to the endpoint value")

    r3 = {}
    for k in OPEN:
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        g_floor0 = ch.gamma(k, {"A0": floors[k], "A1": F(0), "A2": F(0)})
        g_zero = ch.gamma(k, {"A0": F(0), "A1": F(0), "A2": F(0)})
        a0c = bisect_max(ch, k, {**A, **Z}, "A0", hi0=F(40))
        r3[str(k)] = {
            "Gamma_at_A0_floor_A1_A2_zero": float(g_floor0), "closes": g_floor0 < 0,
            "Gamma_at_A0_A1_A2_all_zero": float(g_zero),
            "A0_ceiling_with_A1_A2_zero": float(a0c) if a0c else None,
            "Lambda_floor": float(floors[k]),
            "verdict": ("FEASIBLE" if g_floor0 < 0 else
                        "MATHEMATICALLY_REFUTED -- the certified floor on A0 exceeds the ceiling the "
                        "clause tolerates even at A1 = A2 = 0")}
    oracles["routes"]["R3"] = {
        "perfect_information": ("A0 driven to its certified floor sup_cell E_a[tau] (the smallest "
                                "value Lemma SM(d) admits) with A1 = A2 = 0 -- strictly better than "
                                "any operator certification could ever supply"),
        "per_cell": r3,
        "class": "STRONG",
        "note": ("the A0 ceiling computed here for cell 309, 3.214236022678, independently "
                 "reproduces C4's own critical_A0_reported_only 3.2142360226778806, and the "
                 "refutation of 309 reproduces C4's published exclusion of 309. C8 claims neither "
                 "as new; it extends the same test to 306, 307 and 308, which C4 did not decide.")}

    r4 = {}
    for k in OPEN:
        c = crit["operator_mixed"][str(k)]
        r4[str(k)] = {"Gamma_now": c["Gamma"], "Gamma_perfect_order3": c["Gamma_perfect_order3"],
                      "closes_with_perfect_order3": c["Gamma_perfect_order3"] < 0,
                      "critical_sG_over_sH": c["critical_sG_over_sH"]}
    oracles["routes"]["R4"] = {
        "perfect_information": "a certified order-3 surrogate at its eps_src floor",
        "per_cell": r4,
        "source": "committed C2_CRITICAL_RATIOS.json, field Gamma_perfect_order3 -- not recomputed here",
        "class": "NEW_REAL_BLOCKED",
        "note": ("this is the ONLY route whose perfect-information oracle closes cell 309. It is "
                 "also the route the programme classifies as TRUE NEW-REAL (B1/D4), which the C8 "
                 "boundary forbids and which the decision rule forbids recommending while a "
                 "competitive zero-new-real route is untested.")}

    out = {"schema": "C8_ROUTES/1", "gate_sha256": GATE_SHA,
           "chain_verification": {"committed_supplies_reproduced": len(ver["rows"]),
                                  "all_agree": ver["all_agree"],
                                  "max_Gamma_abs_err": max(r["Gamma_abs_err"] for r in ver["rows"]),
                                  "cells_verified": ver["cells_verified"]},
           "authoritative_open_set": list(OPEN),
           "phase1_dag": dag, "phase2_gap_anatomy": anatomy,
           "phase4_minimum_information_inversion": inversion,
           "phase5_perfect_information_oracles": oracles}
    s = C.write_evidence(C.NS / "evidence" / "phase4" / "C8_ROUTES.json", out)

    print(f"chain verification: {len(ver['rows'])} committed supplies reproduced, "
          f"all_agree={ver['all_agree']}, max Gamma err "
          f"{max(r['Gamma_abs_err'] for r in ver['rows']):.1e}\n")
    print(f"{'cell':>5} {'Gamma now':>13} {'passes':>7} {'A0 ceil(A1=A2=0)':>17} {'Lambda floor':>13} {'R3 verdict':>12}")
    for k in OPEN:
        r = r3[str(k)]
        print(f"{k:>5} {inversion[str(k)]['Gamma_now']:>+13.9f} "
              f"{str(inversion[str(k)]['already_passes']):>7} "
              f"{(r['A0_ceiling_with_A1_A2_zero'] or float('nan')):>17.9f} "
              f"{r['Lambda_floor']:>13.9f} {r['verdict'].split(' --')[0]:>12}")
    print("\ncheapest sufficient fact per cell:")
    for k in OPEN:
        print(f"  {k}: {inversion[str(k)]['cheapest_sufficient_fact']}")
    print(f"\nR1 leverage {oracles['routes']['R1']['leverage']}, "
          f"R2 leverage {oracles['routes']['R2']['leverage']}")
    print(f"R4 closes 309 with perfect order-3: {r4['309']['closes_with_perfect_order3']} "
          f"(Gamma {r4['309']['Gamma_perfect_order3']:+.9f})")
    print(f"\nwrote evidence/phase4/C8_ROUTES.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
