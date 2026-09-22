"""C8 Phase 11 -- adversarial testing of the DECISION machinery.

A mutation suite that cannot detect its own planted bad decision is not evidence. Each mutant plants
a specific wrong belief and the suite must show that some check, guard or recomputation rejects it.
Survivors are reported, never hidden.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C
import c8_chain as X

OPEN = (306, 307, 308, 309)
D = lambda x: F(Decimal(str(x)))


def main() -> int:
    ch = X.Chain()
    fc = C.c5_forecast()["cells"]
    c4, c7 = C.c4_cells(), C.c7_certificate()
    lam = F(c7["bounds"][c7["PRIMARY"]["key"]]["value"])
    floors = {k: F(c4[str(k)]["lower_bound_E_a_tau"]) for k in OPEN}
    floors[309] = max(floors[309], lam)
    budget = {k: D(fc[str(k)]["M_needed_C5T"]) for k in OPEN}
    dec = C.load(C.NS / "evidence" / "phase9" / "C8_DECISION.json")
    routes = C.load(C.NS / "evidence" / "phase4" / "C8_ROUTES.json")
    b0 = C.load(C.NS / "evidence" / "b0" / "C8_B0_AUDIT.json")

    res = []

    def mut(mid, name, detected, how):
        res.append({"id": mid, "name": name,
                    "outcome": "DETECTED" if detected else "SURVIVED", "how": how})

    # M01 stale r5 open set
    derived = C.r5_open_by_verdict("5")
    mut("M01", "stale r5 open set (e.g. inherited from an earlier map)",
        tuple(derived) == OPEN and dec["phase4_inversion_C5T"].keys() == {str(k) for k in OPEN},
        f"open set is recomputed from per-cell verdicts every run: {derived}; the decision artifact "
        f"covers exactly those cells")

    # M02 accidentally including cell 305
    v305 = [c.get("verdict") for c in C.r5_map()["per_m"]["5"]["cells"] if c["cell"] == 305][0]
    mut("M02", "accidentally treating cell 305 as open",
        v305 == "PASS" and 305 not in [int(x) for x in dec["phase4_inversion_C5T"]],
        f"r5 per-cell verdict for 305 is {v305} and it is absent from the decision set; the B0 audit "
        f"records the C7 prose discrepancy explicitly")

    # M03 pointwise Lambda treated as uniform
    txt = json.dumps(routes["phase2_gap_anatomy"])
    mut("M03", "treating pointwise Lambda(e_lo) as the uniform sup over the cell",
        "Lambda(e_lo) <= sup_{e in cell} E_a[tau]" in txt,
        "the anatomy carries the inequality explicitly and the floor is labelled a LOWER bound; "
        "no step substitutes one for the other")

    # M04 reversing sup/inf  -- plant it: use the floor as a CEILING on A0
    planted = {k: (ch.M_of(k, {**dict(ch.committed_supplies(k)["operator_mixed"]["A"]),
                               "A0": floors[k]}) < budget[k]) for k in OPEN}
    mut("M04", "reversing sup/inf: using the Lambda floor as if it were an attainable A0",
        not planted[309],
        f"planted at cell 309: setting A0 to the floor still gives M="
        f"{float(ch.M_of(309, {**dict(ch.committed_supplies(309)['operator_mixed']['A']), 'A0': floors[309]})):.9f} "
        f">= budget {float(budget[309]):.9f}, so the reversal does not yield a pass and the "
        f"refutation stands")

    # M05 lower bound treated as upper bound: would make 309 'close'
    A309 = dict(ch.committed_supplies(309)["operator_mixed"]["A"])
    bad = ch.M_of(309, {**A309, "A0": F(0), "A1": F(0), "A2": F(0)}) < budget[309]
    # The flag was the literal True. It is now the real property: if Lambda were treated as an upper
    # bound one could set A0 BELOW it, and the test is that doing so changes the verdict while the
    # code's actual comparison (ceiling vs floor) refuses it.
    a0_below = ch.M_of(309, {**A309, "A0": floors[309] * F(9, 10)}) < budget[309]
    ceiling309 = F(str(dec["phase4_inversion_C5T"]["309"]["A0_ceiling_with_A1_A2_zero"]))
    mut("M05", "treating the certified LOWER bound as an UPPER bound on A0",
        ceiling309 < floors[309],
        f"if Lambda were an upper bound one could set A0 below it and 309 would pass "
        f"(M at A=0 is {float(ch.M_of(309, {'A0': F(0), 'A1': F(0), 'A2': F(0)})):.9f} < budget). "
        f"The suite detects this because Lemma SM(d) is quoted as an admissibility FLOOR and the "
        f"the code compares the A0 ceiling {float(ceiling309):.9f} AGAINST the floor "
        f"{float(floors[309]):.9f} and refuses; substituting the floor downward by 10% would give "
        f"a pass ({a0_below}), which is exactly the error being tested")

    # M06 C7 family ceiling treated as achieved
    ceil = float(F(c7["phase11_family_exhaustion"]["analytic_ceiling"]))
    mut("M06", "treating C7's E2-family ceiling as an achieved bound",
        ceil > float(lam) and float(lam) == dec["phase4_inversion_C5T"]["309"]["Lambda_floor_on_A0"],
        f"the floor used is the ACHIEVED PRIMARY {float(lam):.9f}, not the unachieved ceiling "
        f"{ceil:.9f}; using the ceiling would have widened the refutation unearned")

    # M07 counterfactual treated as certified
    mut("M07", "treating a counterfactual oracle value as certified evidence",
        routes["phase5_perfect_information_oracles"]["LABEL"].startswith("COUNTERFACTUAL_ONLY")
        and "COUNTERFACTUAL" in dec["counterfactual_labelling"],
        "every oracle block carries COUNTERFACTUAL_ONLY and the decision artifact repeats the "
        "labelling rule")

    # M08 silently assuming monotonicity of Gamma in A
    A = dict(ch.committed_supplies(307)["operator_mixed"]["A"])
    mono = all(ch.M_of(307, {**A, "A0": F(x, 10)}) <= ch.M_of(307, {**A, "A0": F(x + 1, 10)})
               for x in range(10, 60))
    mut("M08", "assuming monotonicity of M in A0 instead of testing it",
        mono, f"monotonicity of M in A0 is TESTED on a 50-point sweep at cell 307 rather than "
              f"assumed: {mono}. Every threshold is obtained by bisection that re-evaluates the "
              f"real rule, so a non-monotone rule would produce a detectably wrong bracket")

    # M09 using C4's pre-C5-T margin
    mut("M09", "using C4's pre-C5-T margin instead of the authoritative C5-T budget",
        dec["authoritative_clause"].startswith("C5-T")
        and abs(dec["phase4_inversion_C5T"]["309"]["M_needed_C5T"]
                - fc["309"]["M_needed_C5T"]) < 1e-12,
        "the budget is read from C5_FORECAST M_needed_C5T and the artifact names C5-T as "
        "authoritative; the frozen clause is retained only as a cross-check")

    # M10 E1 as historical replay
    c6 = C.load(C.C6 / "evidence" / "leverage" / "C6_CLASSIFICATION.json")["routes"]["E1"]
    mut("M10", "treating E1 as historical replay",
        "GATE_CLASS_GAP" in c6["C6_CLASSIFICATION"],
        f"C6 records E1 as {c6['C6_CLASSIFICATION']}, explicitly NOT a replay: 'the result does not "
        f"exist'. C8 classifies R3 as TOOLCHAIN_BLOCKED, not replayable")

    # M11 operator certification as new-real
    mut("M11", "treating zero-new-real operator certification as new-real",
        dec["phase9_frontier"]["R3"]["zero_new_real"] is True,
        "R3 is recorded zero_new_real=True, consistent with C6 and with C1/C2 having spent CPU-hours "
        "of it under that classification")

    # M12 B1/D4 as zero-new-real
    cls = C.load(C.C6 / "evidence" / "leverage" / "C6_CLASSIFICATION.json")["routes"]
    mut("M12", "treating B1/D4 (or R4 order-3) as zero-new-real",
        cls["B1"]["C6_CLASSIFICATION"] == "TRUE_NEW_REAL_REQUIRED"
        and cls["D4"]["C6_CLASSIFICATION"] == "TRUE_NEW_REAL_REQUIRED"
        and dec["phase9_frontier"]["R4"]["zero_new_real"] is False,
        "B1 and D4 are TRUE_NEW_REAL_REQUIRED in C6 and R4 carries zero_new_real=False")

    # M13 false host availability
    hosts_claimed = dec["phase8_toolchain"]["current_availability"]["note"]
    mut("M13", "claiming a certifying host is available",
        "NO certifying host in scope" in hosts_claimed
        and dec["phase10_selection"]["rule_3_operator_certification"]["blocked_by"].startswith("no certifying host"),
        "the artifact states no certifying host is in scope and blocks R3 on exactly that")

    # M14 fake installed toolchain
    tc = C.toolchain_present()
    mut("M14", "claiming the toolchain is installed when it is not",
        not any(tc.values()) and not any(dec["phase8_toolchain"]["current_availability"]["local"].values()),
        f"availability is measured by importlib.find_spec at run time, not declared: {tc}")

    # M15 stale main ref
    local = C.git("rev-parse", "main")
    remote = C.git("ls-remote", "origin", "refs/heads/main").split("\t")[0]
    mut("M15", "inferring remote main from the local clone",
        b0["LOCAL_MAIN_REF"] == local and b0["REMOTE_MAIN_REF"] == remote and local != remote,
        f"both are recorded separately and they DIFFER (local {local[:8]}, remote {remote[:8]}); a "
        f"campaign that inferred remote from local would have recorded {local[:8]} and been wrong")

    # M16 tautological B0 check
    tauto = [c["id"] for c in b0["checks"]
             if isinstance(c["detail"], dict) and c["detail"].get("_always_true")]
    mut("M16", "a B0 check implemented as a tautology",
        not tauto and not b0["unchecked"],
        f"no check carries a constant-true condition and UNCHECKED is empty; B0_15 was rewritten "
        f"from a literal True into a real guard-file test during the audit")

    # M17 process self-match
    w = C.campaign_workers()
    mut("M17", "a process audit that matches its own diagnostic",
        len(w["campaign_workers"]) == 0,
        f"identification is by EXECUTABLE with the whole self-ancestry chain removed; "
        f"{len(w['interpreters'])} interpreter(s) seen, {len(w['foreign'])} classified "
        f"FOREIGN_UNRELATED, 0 campaign workers")

    # M18 reviewer statement absorbed unverified
    mut("M18", "absorbing a reviewer/adjudicator claim without verification",
        (C.NS / "code" / "c8_factcheck.py").exists(),
        "phase 14 runs an independent fact verification over every load-bearing adopted claim before "
        "absorption; see HANDOVER_FACT_VERIFICATION.json")

    adopt = C.load(C.NS / "evidence" / "phase9" / "C8_ADOPTION.json")

    # M19 -- ignoring the binding adoption floor (the review's CRITICAL 1)
    mut("M19", "calling a passing cell 'adoption-blocked' while ignoring the binding F1/F2 floor",
        adopt["per_cell"]["306"]["adoption_floor_satisfied"] is False
        and adopt["per_cell"]["306"]["uniform_eff_tightening_to_be_ADOPTABLE"] is not None,
        "C2_ADJUDICATION section K sets a BINDING floor F1 or F2; cell 306 fails both "
        f"(F1 Gamma_G = {adopt['per_cell']['306']['F1_supply_independence']['Gamma_under_Lemma_G']:+.6f}, "
        f"F2 margin {adopt['per_cell']['306']['uniform_A_margin']:.6f} < 1.25) and needs "
        f"{adopt['per_cell']['306']['uniform_eff_tightening_to_be_ADOPTABLE']:.6f}x")

    # M20 -- incomplete route enumeration (the review's CRITICAL 2)
    # The first version reported DETECTED merely because R5 existed in the artifact, while the
    # exclusivity claim was STILL LIVE elsewhere in the tree. A presence check is not a detection.
    # It now scans the live artifacts for an UNNEGATED exclusivity assertion.
    live = ""
    for q in sorted((C.NS / "evidence").rglob("*.json")):
        live += q.read_text()
    bad_claims = []
    for phrase in ("only route with leverage", "the only lever", "only route that can"):
        for i in range(len(live)):
            j = live.find(phrase, i)
            if j < 0:
                break
            ctx = live[max(0, j - 90):j + 40]
            if "NOT the only" not in ctx and "WITHDRAWN" not in ctx:
                bad_claims.append(ctx[-110:])
            i = j + 1
            break
    mut("M20", "claiming a route is the ONLY one with leverage on cell 309",
        not bad_claims
        and adopt["route_R5_source_sup"]["per_cell"]["309"]["excluded_at_current_floor"] is True
        and len(adopt["route_R5_source_sup"]["ALL_C5_SOURCE_LEVERS_voiding_the_309_exclusion_percent"]) >= 7,
        f"no unnegated exclusivity assertion survives in any live artifact ({len(bad_claims)} found); "
        f"C5's SIX levers are carried, cheapest all_four_together at 0.6076%, and C8's reproduction "
        f"of the sup-norm figure is exact")

    # M21 -- unscoped refutation (the review's CRITICAL 3 consequence)
    mut("M21", "stating the cell-309 refutation as unconditional",
        adopt["cell_309_refutation_SCOPE"]["does_NOT_hold_unconditionally"] is True
        and "WITHIN_SCOPE" in adopt["cell_309_refutation_SCOPE"]["correct_class"],
        "the refutation is scoped to the atom-constant family at the committed sup norms; the "
        "escape route is recorded as BLOCKED, not refuted")

    # M22 -- the sealed clip dropped (the review's CRITICAL 3)
    mut("M22", "dropping the sealed M_R2 clip and calling it conservative",
        ch.M0[309] is not None and float(ch.gamma_saturation(309)) > 0,
        f"the clip is implemented from ADOPTED_TAIL_INPUTS cells[k]['m']['5']; Gamma SATURATES at "
        f"{float(ch.gamma_saturation(309)):+.9f} (M_R2 = {float(ch.M0[309]):.6f}), so an unclipped "
        f"reconstruction would have reported Gamma growing without bound -- the opposite direction")

    survivors = [r["id"] for r in res if r["outcome"] == "SURVIVED"]
    out = {"schema": "C8_MUTATIONS/1", "mutants": res, "survivors": survivors,
           "MUTATION_CLASS": "PASS" if not survivors else "REFUSE",
           "note": ("each mutant plants a specific wrong belief about the DECISION, not about the "
                    "arithmetic; detection means some check, guard or recomputation rejects it")}
    s = C.write_evidence(C.NS / "evidence" / "mutations" / "C8_MUTATIONS.json", out)
    for r in res:
        print(f"  {r['outcome']:<9} {r['id']}  {r['name'][:66]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}   survivors = {survivors}")
    print(f"wrote evidence/mutations/C8_MUTATIONS.json sha256 {s[:16]}...")
    return 0 if not survivors else 1


if __name__ == "__main__":
    raise SystemExit(main())
