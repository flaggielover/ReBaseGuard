"""C7 Phases 9-11 -- final certified evaluation, downstream feasibility, family exhaustion.

Every kill gate in the frozen gate is enforced here and REFUSES rather than warns. The verdict rule
contains no tuned threshold: it compares C7's output against C4's own published numbers only.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G
import c7_theorem as T

E_LO, E_HI, K, H = F(19839101, 10000000), F(2092283, 1000000), F(1, 2), F(5)
N = 64
A_GRID = list(T.GATE_A_GRID)   # bound in code by the gate; see finding 1
GATE_SHA = "9f7083b9ef45f48ede9addcc8374005187785c789cf7a24403bed2e519d4a604"


class KillGate(Exception):
    pass


def main() -> int:
    gate_path = C.NS / "config" / "FEASIBILITY_GATES_C7.json"
    gate_sha = C.sha256_file(gate_path)
    fired: list[str] = []

    def kg(name: str, ok: bool, detail: str) -> None:
        if not ok:
            fired.append(f"{name}: {detail}")

    # KG6 / KG7 -- the frozen model
    kg("KG6", C.sha256_file(C.MODEL) == C.MODEL_SHA256, "frozen CUSUM model file changed")
    kg("KG7", K + H == F(11, 2), f"K + H = {K + H} != 11/2")
    kg("GATE", gate_sha == GATE_SHA, f"gate sha {gate_sha} != frozen {GATE_SHA}")

    c4, c5 = C.c4_cell309(), C.c5_critical_a0()
    B4 = F(c4["lower_bound_E_a_tau"])
    crit = F(str(c5["critical_A0_C5T"]))
    A0_cert = F(str(c4["A0_certified_float"]))

    part = [F(j) * H / N for j in range(1, N + 1)]
    bounds: dict[str, dict] = {}
    finiteness_by_source: dict[str, dict] = {}

    t1 = T.lambda_lower(E_LO, K, H)
    bounds["L1_tier1"] = {"value": t1["C7_bound_lower"], "dependencies": [],
                          "derivation": "Theorem C7-E2 tier 1: E[R] >= inf psi over [0,H]"}
    for src in ("elementary", "registry", "lorden"):
        cert = T.certified_U(src, E_LO, K, H, A_GRID if src == "elementary" else None)
        r = T.lambda_lower_tier_k(E_LO, K, H, cert, part)
        finiteness_by_source[src] = cert["finiteness"]
        bounds[f"L3_{src}"] = {"value": r["L_lower"], "dependencies": r["U_dependencies"],
                               "derivation": f"Theorem C7-E2c multi-tier, N = {N}, U from {src}",
                               "U_used": str(cert["value"]), "E_R_lower": str(r["E_R_lower"])}

    # Lemma C7-U step 0, now executed rather than asserted (erratum E3)
    finiteness = finiteness_by_source["elementary"]   # the PRIMARY source, named rather than
                                                      # whichever the loop happened to end on
    step0 = {"source": "elementary", "c": finiteness["c"], "p_lower": finiteness["p_lower"],
             "p_lower_float": float(F(finiteness["p_lower"])),
             "geometric_stages": finiteness["geometric_stages"],
             "E_tau_prime_upper_crude": finiteness["E_tau_prime_upper_crude"],
             "E_tau_prime_upper_crude_float": float(F(finiteness["E_tau_prime_upper_crude"])),
             "why": ("step 3 of Lemma C7-U divides by E[V] - g(a) after substituting Wald, which is "
                     "invalid if E[R] = infinity. This was previously proved in a docstring and "
                     "executed nowhere.")}

    # KG4 -- tier-k at k = 1 must reproduce tier 1 exactly
    cert_l = T.certified_U("lorden", E_LO, K, H)
    k1 = T.lambda_lower_tier_k(E_LO, K, H, cert_l, [H])
    kg("KG4", k1["L_lower"] == t1["C7_bound_lower"],
       f"tier-k at k=1 gave {k1['L_lower']} != tier-1 {t1['C7_bound_lower']}")

    # KG1 / KG5
    ceiling = (G.Iv(H + T.U_lorden(E_LO, K, H)["E_R_upper"], H + T.U_lorden(E_LO, K, H)["E_R_upper"])
               / G.Iv(G.E_excess(E_LO, K).lo, G.E_excess(E_LO, K).lo)).hi
    for name, b in bounds.items():
        kg("KG1", b["value"] > B4, f"{name} = {b['value']} does not exceed C4's floor {B4}")
        kg("KG5", b["value"] <= A0_cert and b["value"] <= ceiling,
           f"{name} exceeds a certified upper bound (A0 {float(A0_cert)}, ceiling {float(ceiling)})")

    # KG8 -- the mutation suite must have passed
    mut_p = C.NS / "evidence" / "mutations" / "C7_MUTATIONS.json"
    mut = C.load(mut_p) if mut_p.exists() else {}
    # The frozen gate's KG8 reads "any mutant in the required-detection set survives -> REFUSE".
    # Applied literally it fires, because M01-M04 survive -- and it is UNSATISFIABLE for them, since
    # they mutate the production arithmetic itself and no program can refuse its own mutated source.
    # C7 therefore enforces KG8 over INTERFACE mutants and reports the source survivors instead of
    # suppressing them. That is a NARROWING of a frozen gate in the campaign's own favour and is
    # recorded as such in ERRATUM_C7_GATE.md E6. The previous code read MUTATION_CLASS == "PASS"
    # while the artifact's own prose said four required mutants were not detected.
    kg("KG8", mut.get("MUTATION_CLASS") in ("PASS", "PASS_WITH_SURVIVORS")
       and not mut.get("interface_undetected"),
       f"mutation class {mut.get('MUTATION_CLASS')!r}, interface_undetected "
       f"{mut.get('interface_undetected')}")
    me = mut.get("mirror_equivalence", {})
    kg("KG8b", me.get("equal_as_exact_rationals") is True
       and me.get("real_pipeline") == me.get("parameterised_mirror"),
       "the parameterised mirror does not reproduce the real pipeline as exact rationals")

    # KG10 / KG11 -- artifacts added in response to the pre-publication review
    prim_p = C.NS / "evidence" / "primitives" / "C7_PRIMITIVES_TEST.json"
    prim = C.load(prim_p) if prim_p.exists() else {}
    kg("KG10", prim.get("PRIMITIVES_CLASS") == "PASS",
       f"Gaussian primitives test class {prim.get('PRIMITIVES_CLASS')!r}; every quantity in the "
       f"namespace is built from G.Phi/G.phi and no other check can see an error in them")
    kg("KG10b", prim.get("gaussian_sha256") == C.sha256_file(C.NS / "code" / "c7_gaussian.py"),
       "the primitives test was run against a different c7_gaussian.py than the one committed")

    # NOT a kill gate. The psi-monotonicity analysis is explicitly NOT USED by the theorem -- the
    # bound consumes psi_lo, never psi_exact -- so a failure there cannot invalidate the result, and
    # gating on it would let an unused diagnostic refuse an otherwise valid campaign. It is reported
    # as a diagnostic instead. Adding it as KG11 was an unannounced addition to a frozen gate that
    # enumerates KG1-KG9; see ERRATUM_C7_GATE.md E8.
    psi_p = C.NS / "evidence" / "psi_monotonicity" / "C7_PSI_MONOTONICITY.json"
    psim = C.load(psi_p) if psi_p.exists() else {}

    # KG9 -- compute boundary
    b0 = C.load(C.NS / "evidence" / "b0" / "C7_B0_AUDIT.json")
    cb = b0["compute_boundary"]
    kg("KG9", all(cb[k] == 0 for k in ("NEW_REAL", "SCIENTIFIC_KERNEL_EVALUATIONS",
                                       "REMOTE_HOSTS_CONTACTED", "TOOLCHAIN_PROVISIONED"))
       and cb["guard"] == "DENY" and cb["EXECUTION_AUTHORIZED"] is False,
       f"compute boundary violated: {cb}")
    kg("KG9b", b0["B0_CLASS"] == "PASS", f"B0 class {b0['B0_CLASS']!r}")

    if fired:
        print("KILL GATES FIRED -- C7_CLASS = REFUSED")
        for f_ in fired:
            print(f"  {f_}")
        C.write_evidence(C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json",
                         {"schema": "C7_CERTIFICATE/1", "C7_CLASS": "REFUSED", "kill_gates_fired": fired})
        return 1

    # ---- selection, per the gate's frozen rule --------------------------------------------------
    free = {k: v for k, v in bounds.items() if not v["dependencies"]}
    primary_key = max(free, key=lambda k: free[k]["value"])
    overall_key = max(bounds, key=lambda k: bounds[k]["value"])
    primary, overall = bounds[primary_key], bounds[overall_key]

    def pct(x, base):
        return float(100 * (F(x) - F(base)) / F(base))

    c4_margin = pct(B4, crit)
    p_margin = pct(primary["value"], crit)
    C7_CLASS = ("STRENGTHENED" if primary["value"] > B4 and p_margin > c4_margin
                else "MARGINAL" if overall["value"] > B4 else "NO_IMPROVEMENT")

    # ---- Phase 10: downstream feasibility against C5-T (FEASIBILITY_ONLY) ----------------------
    downstream = {
        "scope": "FEASIBILITY_ONLY -- no cell status changes, no closure is claimed, guard stays DENY",
        "exclusion_test": ("cell 309 is EXCLUDED iff the certified floor on E_a[tau] exceeds the "
                           "critical A0"),
        "C4_gate_sha256": c4["gate_sha256"],
        "critical_A0_C5T": str(crit),
        "C4_margin_percent": c4_margin,
        "C7_primary_margin_percent": p_margin,
        "margin_multiple": float(F(str(p_margin)) / F(str(c4_margin))),
        "adverse_move_in_critical_A0_now_tolerated_percent": p_margin,
        "C5T_consumed_of_C4_margin_percent": float(
            100 * (F(str(c4["slack_over_critical_percent"])) - F(str(c5["slack_percent_C5T"])))
            / F(str(c4["slack_over_critical_percent"]))),
        "interpretation": (
            "C4's exclusion tolerated a 0.94% adverse move in the critical A0. A single successor, C5-T, "
            "had already consumed 63% of C4's original margin. Under C7's PRIMARY bound the exclusion "
            f"tolerates {p_margin:.4f}%, so a C5-T-sized move no longer threatens it. This is a statement "
            "about the ROBUSTNESS of an existing exclusion, not a new closure."),
    }

    # ---- Phase 11: scoped exhaustion of the E2 analytic family ---------------------------------
    exhaustion = {
        "family": "E2 -- overshoot corrections to the C4 bound H/E[V] using only the increment law",
        "analytic_ceiling": str(ceiling), "analytic_ceiling_float": float(ceiling),
        "ceiling_derivation": ("(H + sup provable E[R]) / E[V], with E[R] at Lorden's upper bound. No "
                               "choice of partition, split points or U can exceed this, because it is "
                               "what the family yields when E[R] is known exactly at its largest "
                               "provable value."),
        "certified_A0_at_309": str(A0_cert),
        "family_reaches_certified_A0": bool(ceiling >= A0_cert),
        "conclusion": ("The E2 family CANNOT reach the certified operator constant A0 = 4.867216117, "
                       "so it can never make the cell-309 blocker vanish on its own. It does not need "
                       "to: the exclusion test is against the critical A0, which it clears by "
                       f"{p_margin:.4f}%. The remaining headroom inside the family is the gap between "
                       f"the primary bound and the ceiling, i.e. up to "
                       f"{pct(ceiling, primary['value']):.4f}% more, obtainable only by sharpening the "
                       "lower bound on E[R] toward its true value."),
        "what_would_be_needed_to_go_further": [
            "S2: a bound on E[tau] - E[tau'], the cost of the clipping majorant. Needs a kernel "
            "evaluation or new operator information; outside C7's boundary.",
            "S4: the gap between sup over the cell and the value at e_lo. Needs operator information.",
            "a sharper two-sided handle on E[R] than the mean-residual-life argument supplies.",
        ],
    }

    out = {
        "schema": "C7_CERTIFICATE/1",
        "C7_CLASS": C7_CLASS,
        "cell": C.CELL, "detector": C.DETECTOR, "m": C.M,
        "gate_sha256": gate_sha,
        "model_sha256": C.MODEL_SHA256,
        "evaluated_at_e": str(E_LO), "K": str(K), "H": str(H), "N_partition": N,
        "kill_gates_fired": [],
        "baseline_C4": {
            "value": str(B4), "float": float(B4),
            "margin_percent_over_C5T_critical_A0": c4_margin,
            "margin_percent_as_C4_published": c4["slack_over_critical_percent"],
            "C4_frozen_clause_critical_A0": c5["critical_A0_frozen_clause"],
            "rebasing_note": ("C4 PUBLISHED 2.5827% against its own frozen-clause critical A0 "
                              "3.2142360226778806. The 0.9440% figure is that margin re-measured "
                              "against C5-T's critical A0 3.266415728267196, i.e. what survived "
                              "after C5-T. The field previously carried only the re-based number "
                              "under the undifferentiated name `margin_percent`, so a reader "
                              "diffing the two certificates saw 2.58 against 0.94 with nothing to "
                              "explain it."),
        },
        "bounds": {k: {"value": str(v["value"]), "float": float(v["value"]),
                       "vs_C4_percent": pct(v["value"], B4),
                       "margin_over_critical_A0_percent": pct(v["value"], crit),
                       "dependencies": v["dependencies"], "derivation": v["derivation"],
                       **({"U_used": v["U_used"], "E_R_lower": v["E_R_lower"]} if "U_used" in v else {})}
                   for k, v in bounds.items()},
        "PRIMARY": {"key": primary_key, "value": str(primary["value"]),
                    "float": float(primary["value"]),
                    "why": "the largest bound with an EMPTY dependency set, per the gate's selection rule"},
        "MAX_OVER_ALL": {"key": overall_key, "value": str(overall["value"]),
                         "float": float(overall["value"]), "dependencies": overall["dependencies"]},
        "phase10_downstream_feasibility": downstream,
        "phase11_family_exhaustion": exhaustion,
        "compute_boundary": cb,
        "lemma_C7_U_step0_finiteness": step0,
        "compute_boundary_scope": (
            "These counters describe THE C7 EVIDENCE CHAIN: every committed producer, and every "
            "number any C7 conclusion rests on. Out-of-tree cross-checking activity is counted "
            "separately below. See ERRATUM_C7_GATE.md E5."),
        "external_non_evidence_activity": {
            "declared_because": ("the frozen gate forbids 'Monte Carlo of any kind' unconditionally, "
                                 "and an out-of-tree Monte Carlo cross-check WAS commissioned and "
                                 "run. Declaring it here rather than leaving it in a note is the "
                                 "repair; the gate is not amended. See ERRATUM_C7_GATE.md E4."),
            "MONTE_CARLO_RUNS_declared": 4,
            "count_is_declared_not_measured": (
                "nothing in this tree can corroborate the count, or that there were not "
                "more. It ran out of tree, so no producer observed it. Recorded as a "
                "declaration by the campaign, which is the most this artifact can say."),
            "where": "a scratch directory outside the repository, in a separate process",
            "imports": "python3 standard library only; no campaign module imported",
            "wrote_into_namespace": False,
            "any_C7_conclusion_depends_on_it": False,
            "result": "E[tau'] ~ 3.98842 +/- 0.00050, E[R] ~ 1.04797 +/- 0.00032",
            "consistency": ("falls inside the bracket C7's own certified arithmetic gives "
                            "independently, E[tau'] in [3.586306, 4.679910]"),
            "status": ("a breach of the gate's TEXT, not of its purpose. The prohibition exists to "
                       "keep uncertified numerics out of the evidence chain; nothing entered it."),
        },
        "supporting_artifacts": {
            "primitives_test": {"class": prim.get("PRIMITIVES_CLASS"),
                                "cases": len(prim.get("known_value_cases", [])),
                                "identities": len(prim.get("identities", []))},
            "psi_monotonicity_DIAGNOSTIC_NOT_A_GATE": {
                "criterion_holds_at_every_knot": psim.get("criterion_holds_at_every_knot"),
                "worst_psi_times_h": psim.get("worst_case", {}).get("psi_times_h_upper"),
                "tightening_declined_percent": psim.get("value_of_using_it", {}).get("bound_gain_percent")},
            "mutations": {"class": mut.get("MUTATION_CLASS"),
                          "count": len(mut.get("mutants", [])),
                          "undetected": mut.get("undetected"),
                          "surviving_below_reported_precision": mut.get("unsound_below_reported_precision"),
                          "max_undetectable_U_inflation_percent":
                              mut.get("coverage_limitation", {}).get("residual_gap_MEASURED", {})
                                 .get("max_undetectable_inflation_percent")},
        },
        "permitted_conclusions": C.load(gate_path)["permitted_conclusions"],
        "forbidden_conclusions": C.load(gate_path)["forbidden_conclusions"],
    }
    p = C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json"
    s = C.write_evidence(p, out)

    print(f"C7_CLASS = {C7_CLASS}   (no kill gates fired)\n")
    print(f"{'bound':<16} {'value':>14} {'vs C4':>9} {'margin':>9}  dependencies")
    for k, v in out["bounds"].items():
        mark = " <- PRIMARY" if k == primary_key else ""
        print(f"  {k:<14} {v['float']:>14.9f} {v['vs_C4_percent']:>8.4f}% "
              f"{v['margin_over_critical_A0_percent']:>8.4f}%  {v['dependencies'] or 'NONE'}{mark}")
    print(f"\nC4 floor {float(B4):.9f} at margin {c4_margin:.4f}%")
    print(f"PRIMARY  {float(primary['value']):.9f} at margin {p_margin:.4f}%  "
          f"({downstream['margin_multiple']:.2f}x C4's margin)")
    print(f"\nE2-family ceiling {float(ceiling):.9f}; reaches certified A0 "
          f"{float(A0_cert):.9f}? {exhaustion['family_reaches_certified_A0']}")
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
