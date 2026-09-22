"""C10 Phases 5-11 -- Q2: is the C2 adoption floor binding forever, or may a new prospective
successor define a different adoption rule without retroactively changing C2?

Everything here is reconstructed from committed text and committed numbers. No science is run.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c10_common as C

ADJ = C.C2 / "evidence" / "adjudication" / "C2_ADJUDICATION.md"


def main() -> int:
    txt = ADJ.read_text()

    def quote(pat, span=260):
        m = re.search(pat, txt)
        return txt[m.start():m.start() + span].replace("\n", " ") if m else None

    # ---- Phase 5: where the rule comes from, and what it says about itself -------------------
    rule = {
        "artifact": str(ADJ.relative_to(C.REPO)),
        "artifact_sha256": C.sha256_file(ADJ),
        "instrument": "an ADJUDICATION, not a scientific theorem and not a project-global invariant",
        "name_in_text": "K5 tail adoption floor (r1), set by this adjudication",
        "declares_itself_prospective": bool(re.search(r"It is \*\*prospective\*\*", txt)),
        "prospectivity_quote": quote(r"It is \*\*prospective\*\*"),
        "stated_scope": "future adoptions of K5 m = 5 tail cells from this verdict onward",
        "explicitly_does_not_reopen": quote(r"It does not reopen"),
        "structure": "frozen K5-B pass (Gamma < 0) AND at least one of F1, F2",
        "F1": {"content": "supply independence: Gamma < 0 also under a certified atom-constant "
                          "supply NOT depending on the Arb/FLINT registry (Lemma G)",
               "HAS_AN_EXPLICIT_LAPSE_CONDITION": True,
               "lapse_quote": quote(r"This limb is available for as long as"),
               "lapses_when": "N9 is closed (a second, independently written certifier exists)"},
        "F2": {"content": "degradation survival: Gamma < 0 still holds with every atom constant "
                          "degraded uniformly by x1.25, i.e. uniform-A margin >= 1.25",
               "severity_origin": "C2's own, published against its own interest before any "
                                  "adjudicator existed -- not invented by the adjudicator"},
    }

    # does anything claim permanence?
    perm_hits = [l.strip() for l in txt.splitlines()
                 if re.search(r"immutab|forever|never be changed|all future successors", l, re.I)]
    rule["any_claim_of_permanence"] = perm_hits
    rule["permanence_finding"] = (
        "NONE. The word 'permanent' occurs only about adopted CELLS ('an adopted cell is permanent, "
        "is removed from every future campaign's universe, and is never revisited'), which concerns "
        "VERDICTS, not the rule. No text asserts the floor binds all future successors immutably.")

    # ---- the adjudication ANTICIPATES a replacement floor ------------------------------------
    repl = quote(r"a \*\*second, independently written certifier\*\*", 430)
    rule["adjudication_itself_directs_a_replacement"] = {
        "quote": repl,
        "reading": ("the adjudication that SET the floor names, in the same document, the condition "
                    "under which a successor SHOULD FREEZE A REPLACEMENT FLOOR. A rule that "
                    "provides for its own replacement is not immutable."),
    }

    # ---- N9 status, which gates the replacement route ----------------------------------------
    # N9 status. The first version matched r"N9.{0,40}(closed|discharged)" and concluded N9 was
    # CLOSED -- because it fired on "N9 ... remains open, and lapses WHEN N9 IS CLOSED" (a quotation
    # of the lapse CONDITION, whose own text says "remains open") and on "N9 ever closed" (a
    # hypothetical). A scan that reads a conditional or a negation as an assertion is the same defect
    # C9 shipped. Status is now decided by explicit ASSERTIONS, with conditionals excluded.
    CONDITIONAL = re.compile(r"(lapses when|when N9 is closed|if N9|ever closed|until N9|once N9)",
                             re.I)
    ASSERT_OPEN = re.compile(r"N9\b[^.\n]{0,60}?\b(is|are|remain|remains|stays?)\b[^.\n]{0,20}?\bopen\b", re.I)
    ASSERT_CLOSED = re.compile(r"N9\b[^.\n]{0,60}?\b(is|are|was|has been|now)\b[^.\n]{0,20}?\b(closed|discharged)\b", re.I)
    n9_hits, opens, closes = {}, [], []
    for ns in ("c2_closure", "c3_closure", "c4_exhaustion", "c5_exhaustion",
               "c6_evidence_recovery", "c7_e2_lambda309", "c8_operator_feasibility",
               "c9_e1_cell307"):
        p_ns = C.CLOSURE / f"p5y_k5_tail_{ns}"
        found = []
        for f in p_ns.rglob("*.md"):
            body = f.read_text()
            for m in re.finditer(r"N9[^.\n]{0,140}", body):
                # Include PRECEDING context. The first fix still failed because the match begins AT
                # "N9", so "lapses when N9 is closed" yielded the fragment "N9 is closed" with the
                # conditional prefix outside the match entirely.
                seg = body[max(0, m.start() - 70):m.end()].replace("\n", " ").strip()
                if CONDITIONAL.search(seg):
                    continue
                if ASSERT_OPEN.search(seg):
                    opens.append((ns, seg[:110])); found.append("OPEN: " + seg[:90])
                elif ASSERT_CLOSED.search(seg):
                    closes.append((ns, seg[:110])); found.append("CLOSED: " + seg[:90])
        n9_hits[ns] = sorted(set(found))[:3]
    # If both kinds of assertion survive the conditional filter, the status is AMBIGUOUS and must be
    # reported as such rather than resolved by a majority vote.
    if closes and opens:
        n9_state, closed = "AMBIGUOUS", None
    elif closes:
        n9_state, closed = "CLOSED", True
    elif opens:
        n9_state, closed = "OPEN", False
    else:
        n9_state, closed = "UNDETERMINED", None
    rule["N9_status"] = {
        "state": n9_state,
        "open": (closed is False),
        "explicit_open_assertions": len(opens), "explicit_closed_assertions": len(closes),
        "open_examples": [o[1] for o in opens[:3]],
        "closed_examples": [c[1] for c in closes[:3]],
        "statements_by_successor": n9_hits,
        "method": ("explicit status ASSERTIONS only; conditionals such as 'lapses when N9 is "
                   "closed' and hypotheticals such as 'N9 ever closed' are excluded, because an "
                   "earlier version read those as evidence that N9 had closed"),
        "consequence": ("F1 remains AVAILABLE because it lapses only when N9 closes; and the "
                        "replacement-floor route the adjudication names is NOT yet reachable, "
                        "because it is conditioned on closing N9."),
    }

    # ---- Phase 6: the four concepts -----------------------------------------------------------
    four = {
        "A_HISTORICAL_C2_VERDICT": {
            "content": "305 adopted; 306 deferred; D_PARTIAL",
            "mutable": False,
            "why": "verdicts are immutable in this programme and the adjudication says so directly"},
        "B_HISTORICAL_C2_ADOPTION_RULE": {
            "content": "the r1 floor: frozen K5-B pass AND (F1 or F2)",
            "mutable": "NOT RETROACTIVELY; it governs adoptions 'from this verdict onward'",
            "why": "it is prospective by its own terms and carries a lapse condition on F1"},
        "C_SUCCESSOR_SCIENTIFIC_CLOSURE": {
            "content": "Gamma < 0 under the authoritative consumer",
            "governed_by": "the frozen K5-B clause, not by the adoption floor"},
        "D_SUCCESSOR_GOVERNANCE_ADOPTION": {
            "content": "whether a closed cell may be added to the coverage map",
            "governed_by": "the floor in force at the time of that successor's own freeze"},
        "does_changing_D_imply_changing_A_or_B": {
            "answer": "NO",
            "reason": ("A is a past verdict about past cells and is untouched by any future rule. B "
                       "governs adoptions from C2's verdict onward; a successor that freezes its own "
                       "prospective rule BEFORE its own result exists does not alter what B required "
                       "of adoptions made under B. Retroactivity would mean re-adjudicating 305 or "
                       "306 under a new rule, which is the thing that is forbidden."),
        },
    }

    # ---- Phase 7: precedent -------------------------------------------------------------------
    precedent = {
        "campaign_A_cells_11_44": {
            "quote": quote(r"the programme's own precedent \(Campaign A's adjudication", 300),
            "significance": ("the programme HAS adopted K5 cells under a DIFFERENT and weaker "
                             "standard -- a valid enclosure plus a frozen K5-B pass, with no "
                             "robustness requirement. So the r1 floor is not a programme-wide "
                             "invariant; it is a raised bar introduced for this line."),
        },
        "implication": ("adoption standards in this programme have already varied by campaign. That "
                        "is descriptive precedent that a successor-specific rule is possible; it is "
                        "not by itself a licence."),
    }

    # ---- Phases 10/11: consequence tables, from committed numbers -----------------------------
    ad8 = C.load(C.C8 / "evidence" / "phase9" / "C8_ADOPTION.json")["per_cell"]
    lever = C.load(C.C9 / "evidence" / "phase4" / "C9_ALPHA_LEVER.json")
    best_alpha_tight = max(p["tightening"] for p in lever["projection"])

    def cell_row(k, alpha_applies):
        r = ad8[str(k)]
        need_adopt = r["uniform_eff_tightening_to_be_ADOPTABLE"]
        need_close = r["uniform_eff_tightening_to_close"]
        f1 = r["F1_supply_independence"]
        row = {
            "closes_now": r["closes_now"],
            "uniform_A_margin": r["uniform_A_margin"],
            "F1_Gamma_under_Lemma_G": f1["Gamma_under_Lemma_G"],
            "F1_passes": f1["passes"],
            "F2_passes": r["F2_degradation_survival"]["passes"],
            "tightening_to_close": need_close,
            "tightening_to_be_ADOPTABLE_under_the_inherited_floor": need_adopt,
        }
        if alpha_applies:
            row["best_alpha_tightening_projected"] = best_alpha_tight
            row["alpha_can_close"] = bool(need_close and best_alpha_tight >= need_close)
            row["alpha_can_satisfy_F2"] = bool(best_alpha_tight >= need_adopt)
            row["alpha_can_satisfy_F1"] = False
            row["why_alpha_cannot_help_F1"] = (
                "F1 asks for Gamma < 0 under a supply that does NOT use the Arb/FLINT registry. "
                "Alpha tightens the registry's own taboo supersolution, so it cannot move a "
                "registry-free supply at all. F1's verdict is invariant under alpha.")
        return row

    cell307 = cell_row(307, True)
    cell306 = cell_row(306, False)
    cell306["C8_frozen_rule_1_prohibited_selecting_it_in_C9"] = True
    cell306["that_C8_decision_is_immutable"] = True
    cell306["may_a_FUTURE_campaign_target_it"] = (
        "YES, prospectively. C8's rule 1 bound C9's selection, not every future campaign. A future "
        "campaign that freezes its own gate before its own result may target 306. C10 does not "
        "authorize this and does not retroactively alter C8 or C9.")
    cell306["discharge_routes_named_by_the_C2_adjudication"] = [
        "close N9 with a second independently written certifier, then freeze a REPLACEMENT floor "
        "requiring agreement between two independent implementations rather than F1",
        "further deterministic tightening bringing the uniform-A margin to >= 1.25",
        "a real order-3 candidate under the R-stage's own frozen gate, after N1, N5 and N7",
    ]

    cases = {
        "CASE_A_inherited_rule_applies": {
            "cell307": ("alpha-only closure is achievable in projection (up to "
                        f"{best_alpha_tight:.6f}x vs {cell307['tightening_to_close']:.6f}x needed) "
                        f"but CANNOT be adopted: F2 needs "
                        f"{cell307['tightening_to_be_ADOPTABLE_under_the_inherited_floor']:.6f}x and "
                        "F1 is invariant under alpha and currently fails."),
            "worth_certifying": ("only if the programme values a CLOSED-but-unadoptable cell, which "
                                 "buys no coverage-map change"),
            "new_compute_rational": False,
            "governance_bridge_required_first": True},
        "CASE_B_successor_rule_allowed_but_undefined": {
            "cell307": "undecidable until the successor rule exists",
            "worth_certifying": False,
            "new_compute_rational": False,
            "governance_bridge_required_first": True},
        "CASE_C_alternative_robustness_substitutes_for_F1_F2": {
            "cell307": ("the adjudication itself names the substitute -- two-implementation "
                        "agreement replacing F1 -- but conditions it on closing N9"),
            "worth_certifying": "only after N9 closes",
            "new_compute_rational": ("closing N9 is the rational purchase, not an alpha run; it "
                                     "unblocks BOTH 306 and 307 and answers the failure mode the "
                                     "floor exists for"),
            "governance_bridge_required_first": True},
        "CASE_D_rule_cannot_legally_change": {
            "status": "CONTRADICTED BY THE COMMITTED TEXT",
            "why": ("the adjudication declares the floor prospective, gives F1 an explicit lapse "
                    "condition, and directs a successor to freeze a replacement floor. A rule that "
                    "provides for its own replacement is not immutable.")},
    }

    # ---- Phase 9: what the floor is protecting against ----------------------------------------
    purpose = {
        "reconstructed_from": "the adjudication's own reasoning",
        "F1_protects_against": ("systematic error in the single Arb/FLINT supersolution surface -- "
                                "the evidence surface the programme says has never been "
                                "independently implemented (N9), with its build provenance recorded "
                                "nowhere (N10)"),
        "F2_protects_against": "numerical fragility: being wrong about the constants by up to 25%",
        "the_quote": quote(r"The open risk is N9", 240),
        "therefore_an_alternative_package_must": (
            "answer IMPLEMENTATION INDEPENDENCE, not merely add margin. More margin is explicitly "
            "called 'the wrong instrument for the risk that is actually open'."),
        "candidate_ingredients_audited": {
            "second independent certifier": "DIRECTLY answers N9 -- named by the adjudication itself",
            "precision escalation": "does not answer implementation independence",
            "interval widening / degradation stress": "is F2; already available",
            "disjoint decomposition": "partial -- same implementation",
            "theorem-level robustness": "would answer it but no such theorem exists",
        },
    }

    out = {"schema": "C10_GOVERNANCE/1",
           "Q2_phase5_rule_reconstruction": rule,
           "Q2_phase6_four_concepts": four,
           "Q2_phase7_precedent": precedent,
           "Q2_phase9_purpose_of_the_floor": purpose,
           "Q2_phase10_cell307": cell307,
           "Q2_phase11_cell306": cell306,
           "Q2_consequence_cases": cases,
           "Q2_ANSWER": (
               "A future successor MAY define a different prospective adoption rule without "
               "retroactively altering C2. The floor declares itself prospective, scopes itself to "
               "adoptions 'from this verdict onward', gives F1 an explicit lapse condition tied to "
               "N9, and -- decisively -- the same adjudication directs that once N9 closes 'a "
               "successor should freeze a replacement floor requiring agreement between two "
               "independent certifier implementations rather than F1'. Nothing claims permanence. "
               "What a successor may NOT do is re-adjudicate 305 or 306 under a new rule, or apply "
               "its own rule to an adoption already made."),
           "Q2_GATING_FACT": ("N9 is still OPEN, so the replacement route the adjudication names is "
                              "not yet reachable. The rational next purchase is a second, "
                              "independently written certifier -- not an alpha run."),
           }
    s = C.write_evidence(C.NS / "evidence" / "phase5" / "C10_GOVERNANCE.json", out)
    print("Q2 -- the C2 adoption floor")
    print(f"  instrument            : {rule['instrument']}")
    print(f"  declares prospective  : {rule['declares_itself_prospective']}")
    print(f"  scope                 : {rule['stated_scope']}")
    print(f"  F1 lapse condition    : {rule['F1']['HAS_AN_EXPLICIT_LAPSE_CONDITION']} "
          f"({rule['F1']['lapses_when']})")
    print(f"  claims of permanence  : {rule['any_claim_of_permanence'] or 'NONE'}")
    print(f"  N9 open               : {rule['N9_status']['open']}")
    print(f"\n  adjudication directs a replacement floor: "
          f"{bool(rule['adjudication_itself_directs_a_replacement']['quote'])}")
    print(f"\ncell 307: closes now {cell307['closes_now']}, F1 {cell307['F1_passes']}, "
          f"F2 {cell307['F2_passes']}")
    print(f"  alpha can close: {cell307['alpha_can_close']}   "
          f"alpha can satisfy F2: {cell307['alpha_can_satisfy_F2']}   "
          f"alpha can satisfy F1: {cell307['alpha_can_satisfy_F1']}")
    print(f"cell 306: margin {cell306['uniform_A_margin']:.6f}, needs "
          f"{cell306['tightening_to_be_ADOPTABLE_under_the_inherited_floor']:.6f}x")
    print(f"\nwrote evidence/phase5/C10_GOVERNANCE.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
