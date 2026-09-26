"""K5 tail adoption floor r2 -- writes the machine-readable rule and the cell-306 adoption gate.

Governance only. It computes nothing: no Gamma, no atom constant, no margin, no operator constant. Every
field below is text, a commit id, a blob id, a file path, a field name or one of the two frozen parameters
inherited verbatim (the factor 2 of the N9 comparison rule and the x1.25 of limb F2).

    python3 -I -S -B floor_r2_build.py
"""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
L = "level4/closure_proofs"
C2 = f"{L}/p5y_k5_tail_c2_closure"
C10 = f"{L}/p5y_k5_tail_c10_governance_provenance"
C11R = f"{L}/p5y_k5_tail_c11r_n9_statement_alignment"
C11RD = f"{L}/p5y_k5_tail_c11rd_d1d2_extension"
AD = f"{L}/p5y_k5_perron_deflated_resolvent"


def sealed(body: dict) -> dict:
    body = dict(body)
    body["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return body


STATE_AT_FREEZE = {
    "N9": "CLOSED (adjudication 7d67989d3da6595180ca3c01d34f2bdf4543ae73; ADJUDICATION_ACCEPTED review fb237288a7cf481c14cd2f85c18bb363d2ebe44a)",
    "K5": "PARTIAL",
    "coverage_map": f"r5 authoritative ({C2}/evidence/coverage/K5_COVERAGE_MAP_R5.json, blob f978eeb6; m = 5 open cells 306-309)",
    "r6": "none",
    "cell_306": "not adopted",
    "cells_307_309": "untouched",
    "historical_verdicts": "C2 PARTIALLY_ADOPTED [305] with floor r1; C10 ACCEPTED_WITH_CONDITIONS; C11 EXECUTION_INVALID; "
                           "C11R AGREEMENT_INSUFFICIENT / N9_REMAINS_OPEN; C11RD execution, comparison and N9 adjudication accepted -- all immutable",
    "no_post_N9_adoption_magnitude_inspected_before_freeze": True,
    "what_the_designer_had_seen": [
        "historical, pre-N9 published figures in the C2 adjudication, C2's CELL_306_ADOPTION.md and C10 (Gamma, margins, F1/F2 values of cells 305-309 under r1 supplies)",
        "the N9 comparison classes and ratios of the six operator constants (C11R's four; C11RD's D1, D2)",
        "no Gamma, atom constant, uniform-A margin or F2 value was computed, estimated or inspected for any supply containing a C11R or C11RD constant; "
        "REGISTRY_C2.json and C2_D5_FORECAST.json were bound by blob id only and not opened",
    ],
}

RULE = {
    "schema": "rebaseguard.p5y.k5.tail-adoption-floor.r2",
    "name": "K5 tail adoption floor r2 -- replacement of limb F1 by two-implementation agreement (F1'); base clause and limb F2 carried over",
    "status_on_commit": "PROPOSED. In force only once a fresh read-only review returns REPLACEMENT_FLOOR_ACCEPTED and that review is "
                        "preserved in its own commit; from then on FROZEN and prospective.",
    "authority": {
        "primary": f"C2 verdict Condition 1 ({C2}/evidence/adjudication/C2_ADJUDICATION.md): the floor is the standard for K5 m = 5 tail "
                   "adoptions, prospectively; a successor that replaces it must freeze the replacement BEFORE recomputing any magnitude",
        "route": "C2 section K, first discharge route for cell 306: close N9 with a second independently written certifier of the six operator "
                 "constants, then freeze a replacement floor requiring agreement between two independent certifier implementations rather than F1",
        "permission": f"C10 Q2 ({C10}/README.md, evidence/phase5/C10_GOVERNANCE.json): a successor MAY freeze a different prospective adoption rule "
                      "without retroactively altering C2; it may NOT re-adjudicate 305 or 306 under a new rule or apply its rule to an adoption already made",
        "purpose_to_preserve": "C10 Q2_phase9: F1 protected against a systematic error in the single Arb/FLINT supersolution surface (N9); an "
                               "alternative must answer IMPLEMENTATION INDEPENDENCE, not merely add margin; F2 protects against numerical fragility",
        "not_a_re_adjudication": "C10 Q2_phase6: retroactivity 'would mean re-adjudicating 305 or 306 under a new rule, which is the thing that is "
                                 "forbidden'; C10 Q2_phase11 answers whether a future campaign may target 306: 'YES, prospectively' for a campaign that "
                                 "freezes its own gate before its own result; C2 section K: a deferred cell 'is recomputed next cycle ... under a floor "
                                 "frozen in advance'. r2 leaves C2's historical deferral of 306 and its adoption of 305 untouched; a future 306 decision "
                                 "under r2 is a new prospective decision by a separately instructed campaign, not a re-adjudication of C2",
    },
    "state_at_freeze": STATE_AT_FREEZE,
    "old_F1_status": {
        "status": "LAPSED",
        "basis": "r1's own frozen text: F1 is 'available for as long as N9 ... remains open, and lapses when N9 is closed'; N9 is CLOSED by the "
                 "accepted adjudication 7d67989d / fb237288",
        "effect": "F1 may not be used for any adoption decided under a campaign frozen after the N9 adjudication was accepted",
        "whole_limb": "N9 as worded concerns cell 306 only (N9 adjudication), but F1's availability is conditioned on N9's status, not on a cell, "
                      "so the limb lapses as a whole; a lapse only removes a route to adoption (fail-safe); the N9 adjudication itself applied the "
                      "lapse to no cell and no adoption is decided here",
        "not_retroactive": "adoptions already made under r1 (cell 305, by C2) are untouched; no historical verdict is re-adjudicated",
    },
    "rule": {
        "base": "A pair (m = 5, k) may be adopted only if the frozen K5-B certifies it (Gamma < 0 under the campaign's own frozen closure rule), "
                "evaluated on the campaign's CHOSEN SUPPLY, and at least one of the limbs F1' or F2 holds. (r1's base clause, verbatim in substance.)",
        "chosen_supply_restriction": "The chosen supply (used by the base clause and by F2) must be a SINGLE-IMPLEMENTATION supply: the componentwise "
                                     "minimum (C2's D4 rule) over registry-free Lemma G and Lemma Dv' r2 applied to constant sets produced by ONE "
                                     "operator-constant implementation. It must never combine constants or atom constants of two different "
                                     "operator-constant implementations: such a mixture is valid only if BOTH implementations are sound, which is "
                                     "exactly the assumption the floor exists not to make. It is frozen before any evaluation.",
        "limbs": {
            "F1_prime": {
                "name": "two-implementation agreement",
                "text": "For cell k: (a) two operator-constant certifier implementations I1 and I2, independent as defined in 'independence', have "
                        "each certified the six operator constants C_T, tau, Abar, D_lo, D1, D2 of cell k on the cell's whole drift block; (b) the two "
                        "sets were compared under the frozen N9 comparison rule with every constant AGREES or STRONGER and every statement EQUIVALENT "
                        "or STRONGER, in a comparison accepted by an independent review; (c) each implementation carries the soundness evidence in "
                        "'soundness_evidence'; and (d) Gamma(5, k; S_I) < 0 holds for EACH of I = I1 and I = I2 SEPARATELY.",
                "why_it_answers_N9": "If either implementation carries a systematic error, the other implementation's supply alone -- valid if that "
                                     "one is sound -- still certifies closure. Adoption under F1' is therefore correct whenever at least one of the two "
                                     "implementations is sound (single-implementation fault tolerance). It does not require, and does not infer, that "
                                     "either one is sound.",
            },
            "F2": {
                "name": "degradation survival (r1, verbatim)",
                "text": "Gamma < 0 still holds when every atom constant of the chosen supply is degraded uniformly in the unfavourable direction by "
                        "the factor x1.25, i.e. the cell's uniform-A margin is >= 1.25.",
                "factor": "1.25",
                "note": "unchanged from r1; the chosen supply is subject to 'chosen_supply_restriction'",
            },
        },
    },
    "quantity_compared": {
        "adoption_quantity": "Gamma(5, k; S): the exact rational K5-B value for pair (m = 5, k) computed by the frozen consumer path that produced "
                             f"C2's committed Gamma_exact ({C2}/code/c2_d5_forecast.py blob 18403dbe with its pinned dependencies "
                             f"{AD}/code/deflated_consume.py blob a0a836fa, {L}/p5y_k5_m5_tail_closure/code/tct_rule.py blob 98f6eee4 and the "
                             "k5b_literal direct clause), with the atom constants S substituted and every other input unchanged",
        "criterion": "strict sign: Gamma < 0 (exact rational arithmetic; Gamma = 0 or an incomplete evaluation fails)",
        "supplies": {
            "S_I": "componentwise minimum of A0, A1, A2 (C2's D4 rule) over {Lemma G (THEOREM_TCT section 1)} union {Lemma Dv' r2 (THEOREM_AD "
                   "section 4, deflated_consume.atom_constants_r2) applied to each six-constant set of cell k certified by implementation I}; "
                   "each set is used as certified -- no operator-level recombination of sets (the D' mixed-operator supply of C2 Condition 3 / "
                   "N7) is part of S_I. For I1 at cell 306 this is exactly C2's adopted supply {G, C1, C2} (c2_d5_forecast.combine)",
            "kappa": "k1, k2 are the consumer's own frozen constants deflated_consume.K1_BOUND and K2_BOUND, identical for every supply; they are "
                     "not outputs of either operator-constant implementation",
            "consumer_validation": "the consumer's own precondition (tau >= 1, C >= tau, D_lo > 0, Abar >= 1) must hold for every constant set; "
                                   "otherwise that set is invalid and the evaluation fails closed",
            "everything_else": "the K1 adopted stack, Lemma G inputs, the TC-T premises (zero order-3 candidate, sigma3/sigma4), cells.json and "
                               "all other consumer inputs are identical in every evaluation; only the operator-constant sets differ",
        },
        "per_constant_precondition": f"the frozen N9 comparison rule (C11R statement table {C11R}/evidence/table/C11R_N9_STATEMENTS.json blob 58b4066f, comparison_semantics_frozen_before_results; "
                                     "unchanged in the C11RD freeze L_agreement_criterion): factor 2; UPPER_BOUND STRONGER if independent <= original, "
                                     "AGREES if original < independent <= 2 x original, else INSUFFICIENT; LOWER_BOUND mirrored; exact equality INVALID; "
                                     "SAME STATEMENT BEFORE SAME NUMBER",
    },
    "statement_domain_compatibility": [
        "each constant of each implementation is a certified statement uniform in e on a drift domain that contains the cell's whole block "
        "(EQUAL or SUPERSET); a scalar drift or a strict sub-interval never qualifies",
        "the six statements of each implementation are EQUIVALENT or STRONGER to the frozen original statements of the cell (C11R statement "
        "table semantics): same constant, quantity, kernel (Khat_e atom_removed for C_T, tau, D_lo, D1, D2; K_e full for Abar), direction, state "
        "set and proposition; premises SAME or FEWER",
        "each constant set is consumed as C2's chain consumes a registry block: one six-constant set per source per cell, valid uniformly on "
        "the whole cell (C1's block is the cell; C2's sub-blocks are composed onto the cell inside its registry; I2's statements are whole-block)",
    ],
    "numerical_agreement_threshold": {
        "per_constant": "factor 2 (the frozen N9 rule); every one of the six AGREES or STRONGER",
        "adoption": "no ratio threshold: the sign of Gamma must be negative under EACH implementation's own supply",
    },
    "STRONGER_policy": {
        "accepted_as_agreement": "yes, per the frozen N9 rule, for the per-constant precondition",
        "never_substitutes": "a STRONGER constant is used ONLY inside its own implementation's supply S_I; F1' never replaces one implementation's "
                             "value by the other's, never takes a componentwise best across implementations, and always requires the OTHER "
                             "implementation to close on its own",
        "soundness": "STRONGER is not evidence of soundness (an unsound certifier would also appear STRONGER for an upper bound). Soundness of each "
                     "implementation rests on its own evidence ('soundness_evidence'), and F1' is correct if either implementation is sound",
    },
    "asymmetric_bounds": {
        "directions": "C_T, tau, Abar, D1, D2 are UPPER bounds; D_lo is the only LOWER bound (C11R statement table: 'why_the_asymmetry_matters')",
        "treatment": "each implementation's own D_lo lower bound enters its own supply (Lemma Dv' uses D_lo in denominators); the per-constant "
                     "comparison applies the lower-bound rule to D_lo; no constant is ever mixed across implementations",
        "contradiction_check": "if both implementations ever certify two-sided information on the same quantity and one's upper bound lies below "
                               "the other's lower bound, that is SCIENTIFIC_DISAGREEMENT (see 'disagreement')",
    },
    "soundness_evidence": {
        "principle": "F1' does not assume either implementation sound; it tolerates one faulty implementation. Each implementation must nevertheless "
                     "carry its own soundness evidence, so that the single-fault premise is itself reasonable. The comparison classes are not "
                     "soundness evidence.",
        "I1": {
            "implementation": f"the original operator-constant certifier: {AD}/code/taboo_certify.py (certify_cell) with Arb/FLINT supersolutions, "
                              f"as recorded in {C2}/evidence/registry_c2/REGISTRY_C2.json (blob 1a3adfd3) and {L}/p5y_k5_tail_operator_registry/"
                              "evidence/registry_c1/REGISTRY_C1.json",
            "evidence": [
                "C2's two-pass re-certification of cell 306's eighteen artifacts on a recorded host: bit-identical at 256 bits; safe-side domination at 384 bits (phase_d/CELL_306_ADOPTION.md)",
                "the C2 adjudicator's independent re-certification of five registry artifacts with an independent python-flint venv, and its independent exact re-derivation of Gamma from committed inputs",
                "independent agreement of all six cell-306 constants with I2 (N9 CLOSED)",
            ],
            "residuals": ["N10 remains OPEN: REGISTRY_C2.json records no build host, toolchain or precision",
                          "never independently re-implemented before C11R/C11RD"],
        },
        "I2": {
            "implementation": f"the independent line: C11R's certifier (C_T, tau, Abar, D_lo; sealed runs {C11R}/evidence/runs/C11R_RUNS.json blob "
                              f"a5351603, seal 5ff4cc5b) and C11RD's certifier (D1, D2; freeze ce5b8595, sealed runs {C11RD}/evidence/runs/"
                              "C11RD_RUNS.json at seal 4547bcd4, sha256 c28a8cea); C11RD consumes C11R's accepted F_H certificate as a DEPENDENCY",
            "evidence": [
                "C11R: pre-freeze reviews R1-R8, QUALIFICATION_ACCEPTED, AUTHORIZATION_ACCEPTED, EXECUTION_ACCEPTED (22537709), COMPARISON_ACCEPTED (7375b9cd); exact-rational whole-block supersolution certificates",
                "C11RD: theory theory/D1_D2_DERIVATION.md (Proposition 1, Lemmas 0-4, 6, Theorem 5) reviewed READY_TO_QUALIFY (3c1eff11); frozen validation 29/29 including V04, V13, V15, V22, V24, V25; non-target rehearsal; QUALIFICATION_ACCEPTED (e27c2ffd); EXECUTION_ACCEPTED (db1c6118); COMPARISON_ACCEPTED (90265349) with an independent exact recomputation of every sub-block propagation; ADJUDICATION_ACCEPTED (fb237288)",
            ],
            "residuals": ["the comparison cannot detect unsoundness in the STRONGER direction (adjudication review N2)",
                          "independence is implementation/code independence, not independent authorship (N3)",
                          "the propagation used C_T = the exact supremum of C11R's F_H weight (3429/500), below C11R's outward-rounded C_T record by about 3.7e-97 (N1); sound and frozen before the run"],
        },
    },
    "I2_constant_sources_for_cell_306": {
        "C_T, tau, Abar, D_lo": f"{C11R}/evidence/comparison/C11R_COMPARISON.json (blob 5269c2aa) result.per_target[k].independent_value -- the values "
                                "the accepted C11R comparison classified (C_T is the outward-rounded record, the conservative choice)",
        "D1, D2": f"{C11RD}/evidence/comparison/C11RD_COMPARISON.json (commit 8e2defab) per_target[k].independent_value = the sealed runs' targets[k].value",
        "note": "sources are bound by path, blob and field; no value is restated here",
    },
    "independence": {
        "definition": "implementation/code independence in the frozen C11R sense: disjoint load-bearing import graphs (no module of the other's "
                      "certifier chain and none of numpy, flint, intervals, fast_range, ra_certifier, resolvent_certificate, opnorms, "
                      "rebaseguard_certify, rung3_engine, spec, taboo_certify on the independent path); no consumption of the other implementation's "
                      "outputs as premises (C11R DEPENDENCY_FINDING); dependencies inside one implementation are allowed (C11RD on C11R)",
        "re_execution_is_not_independence": "re-running the same certifier on other inputs or another host is not an independent check "
                                            "(C2 CELL_306_ADOPTION.md, Condition 2)",
        "authorship": "not required and not claimed; disclosed: I2 shares an author lineage and its author had seen the original D1/D2 values before "
                      "C11RD's freeze (docs/C11RD_INDEPENDENCE_AUDIT.md); certified bounds do not depend on authorship",
        "common_mode_residual": "both implementations certify statements of the same frozen model, kernel definition and derivative theory; an error "
                                "in those shared definitions, in Lemma G or in the consumer is common-mode and outside what F1' (or N9) protects against",
    },
    "disagreement": {
        "per_constant": "any constant INSUFFICIENT, INVALID or DISAGREES, any statement not EQUIVALENT/STRONGER, or any independence violation: F1' "
                        "is UNAVAILABLE for that cell",
        "closure": "Gamma(5, k; S_I1) < 0 but Gamma(5, k; S_I2) >= 0, or the reverse: F1' FAILS for that cell and the disagreement is recorded; "
                   "no adoption under F1'; F2 may still be evaluated on its own frozen single-implementation supply",
        "contradiction": "incompatible two-sided certificates (SCIENTIFIC_DISAGREEMENT): no adoption of that cell under any limb until a separate "
                         "adjudication resolves it",
        "never": "no re-evaluation, parameter change or supply change after a disagreement in the same campaign",
    },
    "fail_closed": [
        "any input not bound by commit/blob, not byte-identical, or not covered by an accepted review: F1' unavailable",
        "the consumer's validation fails for a constant set, or Gamma cannot be evaluated to an exact rational for either supply: F1' fails",
        "the adopting campaign's control does not reproduce C2's committed Gamma_exact for S_I1 exactly: stop, nothing is decided",
        "the chosen supply violates 'chosen_supply_restriction': the base clause and F2 are not satisfied",
        "neither F1' nor F2 established: DO NOT ADOPT; the cell stays OPEN in the coverage map",
    ],
    "scope": {
        "standing_floor": "r2 replaces r1 prospectively as the standing floor (C2 Condition 1) for K5 m = 5 tail adoptions decided by campaigns "
                          "frozen after r2 is in force; it changes no past adoption",
        "F1_prime_availability": "only for a cell with its own two-implementation evidence (F1' (a)-(c)); at freeze only cell 306 has it",
        "operative_scope_of_this_campaign": "cell 306 only: the gate and the future adoption criterion concern cell 306 and nothing else",
        "cell_306": "eligible to be evaluated under F1' by a separately instructed, prospectively frozen adoption campaign (see the gate); not "
                    "evaluated, not recomputed and not adopted here",
        "cells_307_309": "OUT OF SCOPE: no independent certification of their constants exists; this rule authorizes no work on them, computes "
                         "nothing for them, sets no gate or criterion for them, does not extend F1' to them and makes no statement about their "
                         "closure or adoptability; r5 lists them open. Any future campaign concerning them needs its own instruction and, under C2 "
                         "Condition 1, freezes any further replacement before recomputing",
    },
    "adoption_vs_closure": {
        "scientific_closure": "Gamma(5, k; chosen supply) < 0 under the frozen K5-B clause -- a fact about the cell",
        "adoption": "a governance decision adding (5, k) to the coverage map: scientific closure AND (F1' or F2) AND a complete prospective "
                    "governance chain (freeze before evaluation, qualification, one sealed evaluation, independent reviews, an adjudication "
                    "applying this rule, then the coverage map generated from that adjudication)",
        "N9": "N9_CLOSED is a trust condition on the constants; it is neither closure nor adoption of any cell and does not close K5",
    },
    "cell_306_future_adoption_criterion": {
        "chosen_supply": "S_I1 = C2's adopted supply for cell 306 (componentwise minimum over Lemma G and Lemma Dv' r2 of the I1 registries), "
                         "fixed here so that no supply is chosen after seeing any value",
        "criterion": "adopt (m = 5, k = 306) iff, in a separately instructed campaign frozen before any evaluation: (1) Gamma(5, 306; S_I1) < 0 is "
                     f"reproduced exactly as C2's committed Gamma_exact ({C2}/evidence/phase_d5/C2_D5_FORECAST.json blob a191557f, cells['306'].Gamma_exact) (control); "
                     "(2) Gamma(5, 306; S_I2) < 0, evaluated once and sealed (F1'), "
                     "or F2 holds on S_I1; (3) every item of config/CELL306_ADOPTION_GATE_R2.json passes; (4) an independent adjudication "
                     "applies this rule. Otherwise cell 306 is NOT adopted and stays OPEN.",
        "known_historically": "C2 published that F2 fails for cell 306 on S_I1; this rule does not revisit that and draws no conclusion about F1'",
    },
    "prohibitions_this_round": ["no Gamma, atom constant or margin computed for any supply", "no cell-306 recomputation or adoption",
                                "no execution of cells 307-309", "no comparator re-run", "no r6", "r5 unchanged", "no historical verdict altered",
                                "K5 remains PARTIAL"],
}

GATE = {
    "schema": "rebaseguard.p5y.k5.cell306-adoption-gate.r2",
    "applies_to": "a future, separately instructed cell-306 adoption campaign under floor r2; every item must pass, in order; any failure stops the "
                  "campaign without a decision (fail closed)",
    "items": [
        {"id": "G00", "check": "floor r2 in force: its rule commit and its preserved REPLACEMENT_FLOOR_ACCEPTED review commit are ancestors of the campaign entry; config/K5_TAIL_ADOPTION_FLOOR_R2.json byte-identical and its sha256 field verifies"},
        {"id": "G01", "check": "N9 CLOSED: adjudication 7d67989d holds exactly one N9_CLOSED line and review fb237288 exactly one ADJUDICATION_ACCEPTED line; both byte-identical"},
        {"id": "G02", "check": "governance entry state: K5 PARTIAL; r5 authoritative and byte-identical (blob f978eeb6); no r6; cell 306 open at m = 5; cells 307-309 untouched"},
        {"id": "G03", "check": "PROSPECTIVE FREEZE before any evaluation: the campaign freezes the exact I1 and I2 input bindings (paths, blobs, fields), the consumer path and its hashes, the chosen supply S_I1, the S_I2 construction, the evaluation order and this decision table; nothing about Gamma for any supply containing an I2 constant is computed, estimated or inspected before that freeze"},
        {"id": "G04", "check": "I1 inputs: the cell-306 blocks of REGISTRY_C1.json (blob f6d84bdb) and REGISTRY_C2.json (blob 1a3adfd3), exactly as c2_d5_forecast.py consumed them; C2's consumer path (c2_d5_forecast.py 18403dbe, deflated_consume.py a0a836fa, tct_rule.py 98f6eee4) unchanged"},
        {"id": "G05", "check": "I2 inputs: C11R_COMPARISON.json blob 5269c2aa per_target[C_T, tau, Abar, D_lo].independent_value and C11RD_COMPARISON.json at 8e2defab per_target[D1, D2].independent_value (= C11RD_RUNS.json targets at seal 4547bcd4); all byte-identical; all six statements EQUIVALENT/STRONGER on the whole block [680769/400000, 17885921/10000000]"},
        {"id": "G06", "check": "per-constant agreement: all six AGREES or STRONGER under the frozen factor-2 rule with no independence violation, in accepted comparisons (C11R 2c24a989/7375b9cd; C11RD 8e2defab/90265349)"},
        {"id": "G07", "check": "soundness evidence present and unchanged for I1 and I2 exactly as listed in the rule's 'soundness_evidence'; residuals (N10 open; STRONGER-direction blindness; implementation-only independence; C_T exact-vs-rounded; original-value exposure) restated in the campaign's disclosure"},
        {"id": "G08", "check": "no cross-implementation mixing anywhere: S_I1 contains no I2 constant; S_I2 contains no I1 constant; the chosen supply is S_I1"},
        {"id": "G09", "check": "consumer validation (tau >= 1, C >= tau, D_lo > 0, Abar >= 1) passes for every constant set; kappa = deflated_consume.K1_BOUND, K2_BOUND for both supplies"},
        {"id": "G10", "check": "CONTROL: the frozen path reproduces C2's committed Gamma_exact for cell 306 on S_I1 (evidence/phase_d5/C2_D5_FORECAST.json blob a191557f, cells['306'].Gamma_exact) string-for-string as an exact rational, BEFORE S_I2 is evaluated; mismatch stops the campaign"},
        {"id": "G11", "check": "ONE evaluation of Gamma(5, 306; S_I2), exact rational, sealed (committed) before any interpretation; exactly once"},
        {"id": "G12", "check": "decision by the rule's table only: base holds iff the G10 Gamma < 0; F1' holds iff G05-G07 pass and the Gamma values of G10 and G11 are both < 0; F2 is evaluated on S_I1 only, and C2 published that it fails there -- a campaign that re-evaluates it must bind C2's F2 procedure in its freeze and stops if its result differs from C2's published classification; adopt iff base AND (F1' or F2); otherwise do not adopt"},
        {"id": "G13", "check": "independent execution review and an independent adoption adjudication applying floor r2; only that adjudication's chain may generate a coverage map r6"},
        {"id": "G14", "check": "scope: cells 307-309 not evaluated, not executed, not adopted; no r5 mutation; historical verdicts untouched"},
    ],
}


def main() -> int:
    (NS / "config").mkdir(parents=True, exist_ok=True)
    for name, body in (("K5_TAIL_ADOPTION_FLOOR_R2.json", RULE), ("CELL306_ADOPTION_GATE_R2.json", GATE)):
        (NS / "config" / name).write_text(json.dumps(sealed(body), indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        print("written", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
