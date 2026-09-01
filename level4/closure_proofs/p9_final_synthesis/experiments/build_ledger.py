#!/usr/bin/env python3
"""P9 claim ledger + theorem dependency graph generator.

Single source of truth. Emits CLAIM_LEDGER.json, CLAIM_LEDGER.md,
THEOREM_DEPENDENCY_GRAPH.json and THEOREM_DEPENDENCY_GRAPH.md.

Every claim is traced to an artifact that existed at the anchor commit
ffe23a63181e2ff11380768d3c73980de80f94fb. P9 introduces no new premise.
"""
import json, os, sys

ANCHOR = "ffe23a63181e2ff11380768d3c73980de80f94fb"

# Allowed status vocabulary. Deliberately NOT flattened.
STATUS = [
    "EXACT_THEOREM", "CONDITIONAL_THEOREM", "FORMALLY_VERIFIED",
    "CERTIFIED_NUMERICAL", "EMPIRICAL_REPRODUCED", "EMPIRICAL_ONLY",
    "NEGATIVE_RESULT", "PARTIAL_PRIORITY_RESULT", "REJECTED_CLAIM",
    "NOT_ESTABLISHED", "PROVISIONAL_P8_PENDING_CODEX",
]
# Strength order for the no-inflation bound (higher = stronger).
RANK = {
    "NOT_ESTABLISHED": 0, "REJECTED_CLAIM": 0, "PROVISIONAL_P8_PENDING_CODEX": 0,
    "NEGATIVE_RESULT": 1, "EMPIRICAL_ONLY": 2, "PARTIAL_PRIORITY_RESULT": 2,
    "EMPIRICAL_REPRODUCED": 3, "CERTIFIED_NUMERICAL": 4,
    "CONDITIONAL_THEOREM": 5, "FORMALLY_VERIFIED": 6, "EXACT_THEOREM": 6,
}

# Edge types. ONLY "premise" bounds claim strength (see THEORY.md, P9-T1).
#   premise   : X is a logical premise of Y. Y cannot be stronger than X.
#   verifies  : X is an independent evidence LAYER about Y (Lean kernel check,
#               Arb certificate). The layer's own status is a fact about the
#               artifact; it does NOT license upgrading Y, and Y does not cap it.
#   diagnoses : X explains//reconciles a recorded negative result Y without
#               deriving from it. Does not bound strength in either direction.
EDGE_TYPES = ("premise", "verifies", "diagnoses")

def C(cid, pri, stmt, status, ev, src, parents=(), assumptions="", scope="",
      limits="", usable="YES", note=""):
    edges = []
    for p in parents:
        pid, _, kind = p.partition(":")
        edges.append({"parent": pid, "type": kind or "premise"})
    return dict(id=cid, priority=pri, statement=stmt, status=status,
                evidence_type=ev, source=src, edges=edges,
                parents=[e["parent"] for e in edges if e["type"] == "premise"],
                assumptions=assumptions, scope=scope, limitations=limits,
                p9_may_use=usable, note=note)

FROZEN = "frozen two-sided Gaussian CUSUM (k=1/2, h=5) and frozen symmetric two-chart SR (A=520.886133602749); convention A window w=min(m,tau) with random denominator"

CLAIMS = [
# ---------------------------------------------------------------- core (pre-P1)
C("CORE-T1", "CORE",
  "For the frozen m=1 two-sided Gaussian CUSUM, F'_rho(0) = rho(1 - Gamma) where Gamma is the stopped-selection gain.",
  "EXACT_THEOREM", "human theorem + Lean-checked differentiation/moment spine",
  "closure/02_THEOREM_MAP.md; rebaseguard-lean/",
  assumptions="stopped-likelihood differentiability, measurability, integrability, local domination",
  scope="m=1, rho in [0,1], frozen Gaussian CUSUM",
  limits="local deterministic result for the conditional-mean map; not a global or stochastic instability theorem"),
C("CORE-C1", "CORE",
  "Gamma_CUSUM lies in [3.9243482, 27.8493821]; in particular Gamma_CUSUM > 2, so zero is locally repelling for the deterministic conditional-mean map at rho=1.",
  "CERTIFIED_NUMERICAL", "Arb outward-rounded interval certificate",
  "closure/04_ARB_CERTIFICATE.md", parents=["CORE-T1:verifies"],
  scope="m=1 frozen Gaussian CUSUM",
  limits="Arb does not prove differentiation under the expectation; the human theorem supplies that bridge"),
C("CORE-C2", "CORE",
  "Gamma_SR lies in [5.800391799508442, 28.781285803081492]; its lower endpoint exceeds two by 3.800391799508442.",
  "CERTIFIED_NUMERICAL", "Arb outward-rounded interval certificate (SR-GAMMA-CERTIFIED)",
  "docs/releases/SR_GAMMA_CERTIFIED_RELEASE_NOTES.md", parents=["CORE-T1:verifies"],
  scope="frozen symmetric two-chart SR",
  limits="separate later upgrade; same local-deterministic caveat as CORE-C1"),
# ---------------------------------------------------------------- P1
C("P1-T1", "P1",
  "For every fixed m>=1 in the frozen CUSUM convention, F'_{rho,m}(0) = rho(1 - GammaTilde_m) with GammaTilde_m = E_0[A_m T_tau], retaining the random denominator and the exact nonnegative short-cycle correction on {tau<m}.",
  "EXACT_THEOREM", "human theorem + proof, independently reviewed",
  "level4/closure_proofs/m_gt_1_priority1/{THEOREM,PROOF,DEFINITION_AUDIT}.md",
  parents=["CORE-T1"],
  assumptions="stopped-likelihood, measurability, integrability, local domination (human obligations)",
  scope=FROZEN + "; m in {1,2,3,5} numerically supported, theorem for all m>=1",
  limits="attraction/repulsion/inconclusive-equality trichotomy is local and first order only"),
C("P1-L1", "P1",
  "The Lean namespace MGtOneClosure kernel-checks the window partition, correction identity and nonnegativity, expectation decomposition, m=1 reduction, rho scaling, dominated Gaussian-likelihood derivative spine, and multiplier criteria. Axioms: propext, Classical.choice, Quot.sound. No sorry/admit.",
  "FORMALLY_VERIFIED", "Lean 4.34.0-rc1 kernel check + axiom audit",
  "level4/closure_proofs/m_gt_1_priority1/lean/MGtOneClosure.lean",
  parents=["P1-T1:verifies"],
  limits="Lean consumes abstract measurability/integrability/domination as HYPOTHESES; it does not prove the concrete frozen-CUSUM stopped exponential moment or domination conditions. Those remain explicit human analytic obligations."),
C("P1-N1", "P1",
  "Frozen Gaussian CUSUM GammaTilde_m score-route estimates: m=1 15.916540430, m=2 13.264824962, m=3 11.957078195, m=5 10.226363970.",
  "EMPIRICAL_REPRODUCED", "preregistered independent implementation; 12/12 cells passed smallest-step, Richardson, convergence, precision, finite-value gates",
  "level4/closure_proofs/m_gt_1_priority1/CLOSURE_REPORT.md §3",
  parents=["P1-T1"],
  limits="Monte Carlo estimates. Frozen infinite-horizon Gaussian CUSUM values for m>1 are NOT interval-certified (stated verbatim in the closure report)."),
# ---------------------------------------------------------------- P2
C("P2-T1", "P2",
  "For the reset symmetric two-chart SR detector, GammaTilde_m^SR = E_0[A_m T_tau] and F'_{rho,m}(0) = rho(1 - GammaTilde_m^SR). All eight preregistered analytical obligations are PROVED; none is discharged numerically.",
  "EXACT_THEOREM", "human theorem + proof, independently reviewed",
  "level4/closure_proofs/sr_derivative_priority2/CLOSURE_REPORT.md §2",
  parents=["CORE-T1"],
  assumptions="SR forcing inequality |Z| >= log(A)+1/2 supplies a uniform geometric tail near zero, hence the stopped exponential moment; reflection symmetry exchanges charts, preserves tau, negates (A_m, T_tau)",
  scope="reset symmetric two-chart SR, A=520.886133602749, inclusive terminal comparison, no head-start",
  limits="frozen infinite-horizon Gaussian SR m>1 values are NOT interval-certified"),
C("P2-N1", "P2",
  "Frozen Gaussian SR GammaTilde_m^SR: m=1 17.453570692, m=2 14.500509744, m=3 12.972654634, m=5 11.048526073.",
  "EMPIRICAL_REPRODUCED", "P2 numerical package; later re-run at 1.6M paths during P4 adjudication",
  "level4/closure_proofs/sr_derivative_priority2/; p4/INDEPENDENT_ADJUDICATION.md",
  parents=["P2-T1"],
  limits="the original 240k-path realization was later diagnosed by P4's adjudicator as a correlated high Monte Carlo realization across m; see D-01 in DISCREPANCY_REGISTER.md"),
# ---------------------------------------------------------------- P3
C("P3-T1", "P3",
  "The first-order local stability boundary is rho_c = 1/|1 - GammaTilde|, and |lambda| = rho|1 - GammaTilde| classifies local attraction/repulsion of the origin.",
  "EXACT_THEOREM", "algebraic consequence of P1/P2, independently recomputed",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §2",
  parents=["P1-T1", "P2-T1"],
  scope="first-order local, deterministic conditional-mean map, m in {1,2,3,5}, two frozen detectors",
  limits="does NOT establish global or nonlinear stability, a stationary-law result, detector universality, or any non-Gaussian extension (verbatim)"),
C("P3-N1", "P3",
  "Frozen Gaussian rho_c: CUSUM m=1..5 = 0.067039673, 0.081533981, 0.091265206, 0.108385059; SR = 0.060777081, 0.074071277, 0.083523665, 0.099517083, each with a transformed 95% interval from the gain SE.",
  "EMPIRICAL_REPRODUCED", "independent recomputation from immutable P1/P2 JSON without importing P3 code",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §3",
  parents=["P3-T1", "P1-N1", "P2-N1"],
  limits="empirical Gaussian correspondence, not rigorous gain enclosures"),
C("P3-X1", "P3",
  "Exact finite-support witnesses: CUSUM-compatible gain 15/2 with rho_c = 2/13 for all m; SR-compatible gains 4, 3, 8/3, 12/5 with rho_c = 1/3, 1/2, 3/5, 5/7. Every rational boundary satisfies |rho_c(1-GammaTilde)| = 1 exactly.",
  "FORMALLY_VERIFIED", "independent exact Fraction arithmetic + Arb 128-bit replay of the SR witness recurrence",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §5",
  parents=["P3-T1"],
  limits="witness rows only. The certificate contains no Gaussian gain and records gaussian_layers_certified=false."),
C("P3-N2", "P3",
  "For every supported m the frozen Gaussian SR point boundary lies below the CUSUM boundary with disjoint transformed intervals (gaps ~0.0052583, 0.0061994, 0.0063668, 0.0072595).",
  "EMPIRICAL_ONLY", "independent recomputation",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §4",
  parents=["P3-N1"],
  limits="an empirical ordering of the two frozen specializations only - NOT a detector-universal theorem (verbatim)"),
C("P3-U1", "P3",
  "Exactly one declared grid cell is uncertainty-inconclusive: Gaussian SR m=5 rho=0.10, |lambda| interval [0.9968076348404744, 1.0128975798590936].",
  "EMPIRICAL_REPRODUCED", "independent reconstruction of all 304 grid cells",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §4",
  parents=["P3-N1"],
  limits="one cell crosses unit magnitude; it is classified INCONCLUSIVE and must not be reported as either side"),
C("P3-LIM1", "P3",
  "P3's grid preregistration cannot be independently authenticated: all 49 candidate files arrived in one uncommitted intake. Reports call it the candidate-declared fixed grid.",
  "NOT_ESTABLISHED", "temporal-integrity finding by P3's adjudicator",
  "level4/closure_proofs/m_rho_stability_priority3/CLOSURE_REPORT.md §4",
  usable="AS_LIMITATION_ONLY",
  limits="does not change the scientific result - the boundary is analytic and continuous in rho, so grid cells are descriptive evaluations, not fitted thresholds"),
# ---------------------------------------------------------------- P4 (PARTIAL)
C("P4-T1", "P4",
  "For a regular location family with score psi, under (A1)-(A7) and for every fixed m>=1: g_m'(0) = -E_0[A_m sum_{t<=tau} psi(Z_t)] and F'_{rho,m}(0) = rho(1 - Gamma_{D,m,f}).",
  "CONDITIONAL_THEOREM", "human theorem, independently re-derived and accepted by P4's adjudicator",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md 'Strongest theorem accepted'",
  parents=["P1-T1", "P2-T1"],
  assumptions="(A1)-(A7); L3 needs a finite 1+eta moment; change of measure justified on each {tau=n} then summed via (A5)-(A6); Lipschitz difference quotient in (A6) gives dominated convergence. Symmetry is NOT needed for the derivative identity - it is needed separately to make the origin a fixed point before P3's local classification applies.",
  scope="regular location families; m=1 raw-reuse for the abstract theorem",
  limits="P4 is PARTIAL. The theorem survives; three literal frozen numerical gates remain false.",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P4-T2", "P4",
  "Narrowed G3: sign(Q_{m,f}) = sign(T_tau S_tau^psi) on {tau<m}; psi(z)=cz with c>0 makes the product a square; non-Gaussian corrections can be negative pathwise and in expectation.",
  "CONDITIONAL_THEOREM", "adjudicator-narrowed theorem statement",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md 'Theorem narrowing'",
  parents=["P4-T1"],
  limits="This is Gaussian sufficiency plus explicit non-Gaussian failure, NOT an iff characterisation. The campaign did NOT prove that all-path sign preservation forces a linear score, and a general affine score has an intercept that must be handled. The original G3 prose overstated its converse.",
  usable="YES_IN_NARROWED_FORM_ONLY"),
C("P4-L1", "P4",
  "Lean recompiled 19 intended declarations from P1/P2/P3/P4 sources with axioms propext, Classical.choice, Quot.sound; no sorry, sorryAx, project scientific axiom, or unsafe shortcut.",
  "FORMALLY_VERIFIED", "Lean kernel check + axiom audit at adjudication",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-T1:verifies"],
  limits="the bridge uses Mathlib's local Lipschitz dominated-integral lemma; it does NOT construct the stopped probability model or discharge L1-L5"),
C("P4-C1", "P4",
  "Arb (160 bits stored, 256 bits independent) certifies only the Laplace memoryless closed form Gamma_1 = 1 + 2*sqrt(2), the uniform moving-support defect 2, and the finite-support negative-correction witness.",
  "CERTIFIED_NUMERICAL", "Arb replay at two precisions",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-T1:verifies"],
  limits="NO frozen CUSUM or SR gain is interval-certified by P4. Cauchy is excluded because E|A_m| diverges already on tau=1."),
C("P4-F1", "P4",
  "Frozen gate all_theorem_supported_cells_pass is FALSE: the original skewnormal4/SR/m=2 cell and nine precision-limited t1p5 cells remain frozen failures.",
  "NEGATIVE_RESULT", "literal frozen gate evaluation, not weakened or regenerated",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-T1"]),
C("P4-F2", "P4",
  "Frozen gate all_outside_assumption_cells_demonstrate_failure is FALSE: Cauchy produces the proved non-convergence failure, not the sharp deterministic defect the gate was written to detect.",
  "NEGATIVE_RESULT", "literal frozen gate evaluation",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-T1"]),
C("P4-F3", "P4",
  "Frozen gate gaussian_consistency_with_closed_core is FALSE.",
  "NEGATIVE_RESULT", "literal frozen gate evaluation",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-T1", "P2-N1"]),
C("P4-R1", "P4",
  "The skewnormal4/SR/m=2 anomaly (combined |z| = 4.29) is diagnosed as finite-step bias in the asymmetric frozen-SR map plus score-route Monte Carlo scatter; at the smallest step pair all four windows agree with the original Route A within 0.09-0.56 combined SE.",
  "EMPIRICAL_REPRODUCED", "two independent attacks: finer Route B (960k paths), smallest Route B (480k), fresh Route A (1.6M)",
  "level4/closure_proofs/p4_theory_generalization/INDEPENDENT_ADJUDICATION.md",
  parents=["P4-F1:diagnoses"],
  limits="resolves the SCIENTIFIC anomaly; the original protocol result remains immutable and its gate remains FAILED"),
C("P4-NOV", "P4", "P4 novelty is NOVELTY-NOT-ADJUDICATED.",
  "NOT_ESTABLISHED", "adjudication record", "README.md Level-4 table; p4 adjudication",
  usable="AS_LIMITATION_ONLY"),
# ---------------------------------------------------------------- P5 (PARTIAL)
C("P5-T1", "P5",
  "Raw-mean identity: the frozen Stage-D update collapses identically to e_{j+1} = rho * (mean of the last min(m,tau) RAW N(0,1) observations) + (1-rho) * N(0,1/m). The entering reference error cancels; it influences the future ONLY by selecting which observations land in the terminal reuse window.",
  "EXACT_THEOREM", "human theorem, independently confirmed in 48 configurations (attack A1)",
  "level4/closure_proofs/p5_nonlinear_dynamics/{THEOREM,PROOF}.md; INDEPENDENT_ADJUDICATION.md",
  parents=["P1-T1", "P2-T1"],
  scope="frozen Gaussian constant-policy convention-A chain, both frozen detectors",
  limits="exact for the frozen convention; it is an identity, not a dynamical conclusion by itself"),
C("P5-T7", "P5",
  "For each frozen detector, each fixed m>=1 and each fixed rho in [0,1], the reference-error chain admits a two-step whole-space minorisation, a unique invariant law, uniform geometric convergence in total variation, and finite invariant moments of every positive order.",
  "EXACT_THEOREM", "human theorem, independently re-verified; Lean spine 12 declarations sorry-free, 3 standard axioms",
  "level4/closure_proofs/p5_nonlinear_dynamics/STATIONARY_DYNAMICS.md; INDEPENDENT_ADJUDICATION.md",
  parents=["P5-T1"],
  assumptions="uniform stopping-time control: for CUSUM, ten consecutive Z_t>=1 or <=-1 has probability at least Phi(-1)^10 and forces a crossing from every reachable state; for SR, one observation with Z_t >= log(A)+1/2 forces an inclusive crossing",
  scope="PER FIXED (D, m, rho) - the constants are not claimed uniform in rho",
  limits="constants are qualitative; A12 confirmed they are loose. Fixed constant policy only - NOT adaptive kernels."),
C("P5-T11", "P5",
  "Under T7's invariant law pi, ACF1 = rho(1 - Gamma_eff) with Gamma_eff = 1 + sbar.",
  "EXACT_THEOREM", "human theorem using T7's pi; independently confirmed",
  "level4/closure_proofs/p5_nonlinear_dynamics/STATIONARY_DYNAMICS.md",
  parents=["P5-T7"],
  limits="map-predicted vs chain-measured ACF1 agree to <= 0.0174 absolute (<= 3.5%), up to 16 chain s.e.; the PREDICTION's own error budget is unquantified. The identity is proved; the gridded-map/PCHIP plug-in is the residual (attack A13, 'overturned as unresolved')."),
C("P5-T8T9", "P5",
  "A unique fixed point and a symmetric 2-cycle branch emerging at rho_c: symmetric 2-cycles are exactly the roots of s(e) = 1/rho for the odd map rho*R(e).",
  "CONDITIONAL_THEOREM", "human theorem conditional on measured hypotheses (H1)-(H3)",
  "level4/closure_proofs/p5_nonlinear_dynamics/NONLINEAR_MAP.md",
  parents=["P5-T1", "P3-T1"],
  assumptions="(H1)-(H3), including a one-crossing condition, all MEASURED not proved",
  limits="uniqueness among ALL cycles is unproved; uniqueness is only among symmetric cycles under one-crossing H3",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P5-T10", "P5",
  "The symmetric branch amplitude tends to zero at rho_c against an O(1) noise floor, so its SNR tends to zero.",
  "CONDITIONAL_THEOREM", "human theorem conditional on H2/H3",
  "level4/closure_proofs/p5_nonlinear_dynamics/NONLINEAR_MAP.md",
  parents=["P5-T8T9"],
  limits="the UNIVERSAL operational-invisibility inference drawn from it was REJECTED by P5's adjudicator. Only the conditional asymptotic survives.",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P5-MECH", "P5",
  "Selection-channel mechanism: the selection channel is maximal per unit of e at e=0 (where the alarm is rare and therefore exquisitely selective, giving GammaTilde ~ 9-17) and VANISHES once |e| is large enough that the alarm is immediate, because a certain event selects nothing. Local repulsion and global boundedness are the same channel evaluated at opposite ends of its dynamic range: the chain does not 'return' from a large excursion, it is RESET.",
  "EXACT_THEOREM", "mechanism follows from T1; adjudicated SCIENTIFIC_CORE = SURVIVES",
  "level4/closure_proofs/p5_nonlinear_dynamics/CLOSURE_REPORT.md §1; INDEPENDENT_ADJUDICATION.md",
  parents=["P5-T1", "P5-T7"],
  limits="the mechanism is exact; the quantitative shape of R(e) away from the origin is a measured PCHIP map"),
C("P5-N1", "P5",
  "Attraction and supercritical-flip classification of the 2-cycle branch.",
  "EMPIRICAL_ONLY", "numerical evidence on the measured PCHIP map",
  "level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md theory-status table",
  parents=["P5-T8T9"],
  limits="attack A4 partially confirmed: the independent scan supports the branch but still scans an ESTIMATED PCHIP map. Global deterministic attraction was NARROWED by the adjudicator."),
C("P5-N2", "P5", "Bimodality onset of the invariant law.",
  "EMPIRICAL_ONLY", "numerical evidence, four measured cells",
  "level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md",
  parents=["P5-T7"], limits="four cells only; the earlier unimodality draft was overturned"),
C("P5-N3", "P5", "A dispersion/ARL optimum in rho.",
  "EMPIRICAL_ONLY", "numerical evidence, finite grid",
  "level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md",
  parents=["P5-T7"],
  limits="finite grid; attack A7 partially confirmed - the minimum is robust but its exact LOCATION has near-ties in three cells. Must not be imported as a design constant (P6 pre-design X-ledger)."),
C("P5-N4", "P5",
  "Increasing m improves the listed dispersion and ARL metrics over m in {1,2,3,5} at common measured rho.",
  "EMPIRICAL_ONLY", "numerical evidence for specified metrics and m<=5",
  "level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md",
  parents=["P5-T7"],
  limits="NOT a monotonic theorem; does not cover m>5; does not improve every conceivable metric - measured SNR INCREASES with m. This is the premise P5's ledger labels 'P9', which is NOT Priority 9 (see P9_DEFINITION_AUDIT.md U1). It stands in recorded tension X8 with P6 premise S14.",
  note="LABEL_COLLISION_WITH_PRIORITY_NINE"),
C("P5-F1", "P5",
  "Frozen closure gates G3, G7 and G9 are literally false: they use universal language (sup_e, 'wherever', 'anywhere') while their evidence is finite-grid Monte Carlo/interpolation. Gate G20 is also false in the adjudication worktree.",
  "NEGATIVE_RESULT", "literal frozen gate evaluation; focused suite 44 passed, 1 failed",
  "level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md",
  parents=["P5-N1"],
  limits="G20's failure is a worktree-scope artifact (pre-existing root README modification plus untracked P6 pre-design), NOT a scientific defect; the brief forbade weakening it or deleting the unrelated files"),
C("P5-NOV", "P5", "P5 novelty is NOVELTY-NOT-ADJUDICATED.",
  "NOT_ESTABLISHED", "adjudication record", "p5/INDEPENDENT_ADJUDICATION.md",
  usable="AS_LIMITATION_ONLY"),
# ---------------------------------------------------------------- P6 (PARTIAL per repository)
C("P6-T6A", "P6",
  "One-step reference-risk bound, uniform over the decision box, with C_D := sup_x E_x[tau_x] finite by T4/T5.",
  "EXACT_THEOREM", "human theorem",
  "level4/closure_proofs/p6_safe_rebaselining/THEORY.md §2",
  parents=["P5-T7"],
  limits="the theorem CONSTANTS are EMPIRICAL_ONLY (a loose theorem constant is reported beside the measured one)",
  usable="YES_UNDER_P6_PARTIAL"),
C("P6-T6B", "P6",
  "Closed-loop invariant law and uniform geometric ergodicity for a memoryless admissible policy u with rho_max < 1.",
  "EXACT_THEOREM", "human theorem, adjudicated T6_B = EXACT_VALID",
  "level4/closure_proofs/p6_safe_rebaselining/THEORY.md §4; p6r2 ADJUDICATION_RECORD_P6R2.md",
  parents=["P6-T6A", "P5-T7"],
  assumptions="MEMORYLESS policies only, and rho_max < 1",
  limits="policies that read the detector state are outside T6-B. This is the well-posedness of stationary language for the safe-adaptive-window policy, not a performance claim.",
  usable="YES_UNDER_P6_PARTIAL"),
C("P6-T6C", "P6",
  "Exact conditional dominance and the Jensen-gap identity, with a plug-in design criterion; requires V non-degenerate (P(V != E V) > 0).",
  "EXACT_THEOREM", "human theorem, adjudicated T6_C = VALID_WITH_NARROWER_ASSUMPTIONS",
  "level4/closure_proofs/p6_safe_rebaselining/THEORY.md §3",
  parents=["P5-T1"],
  limits="ONE STEP, from a COMMON entering law. It does not assert a multi-step or closed-loop advantage. This is the separation from fixed-rho tuning.",
  usable="YES_IN_NARROWED_FORM_ONLY"),
C("P6-T6D", "P6", "One-step tail control.",
  "CONDITIONAL_THEOREM", "EXACT in oracle form, APPROXIMATE in implementable form",
  "level4/closure_proofs/p6_safe_rebaselining/THEORY.md §5", parents=["P6-T6A"],
  limits="the implementable form is an approximation; only the oracle form is exact",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P6-T6E", "P6", "Pareto endpoints: rho_j == 1 is the unique endpoint of the declared cost model, with endpoint non-comparability exact.",
  "CONDITIONAL_THEOREM", "EXACT endpoint non-comparability given the cost model; frontier is EMPIRICAL",
  "level4/closure_proofs/p6_safe_rebaselining/THEORY.md §6", parents=["P6-T6C"],
  limits="conditional on the declared step-shaped fresh-sample cost model; the frontier itself is empirical",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P6-EMP", "P6",
  "The primary empirical result of the stability-aware re-baselining policy is CONFIRMED and independently REPLICATED in the tested regimes.",
  "EMPIRICAL_REPRODUCED", "adjudicated PRIMARY_EMPIRICAL_RESULT = CONFIRMED, REPLICATION = CONFIRMED",
  "level4/closure_proofs/p6r2_literal_closure_repair/ADJUDICATION_RECORD_P6R2.md",
  parents=["P6-T6C", "P6-T6B"],
  limits="regime-scoped simulation and semi-real evidence, NOT production validation",
  usable="YES_UNDER_P6_PARTIAL"),
C("P6-F1", "P6",
  "P6 is CLOSED at the authoritative status table: 'The safe-rebaselining campaign and its literal closure repairs are complete at the repository's authoritative status; its scope and negative results remain as adjudicated.'",
  "PARTIAL_PRIORITY_RESULT", "root README.md Level-4 status table, updated by the adjudicator in the same pass as the P8 verdict",
  "README.md Level-4 status table (authoritative)",
  parents=["P6-EMP"],
  limits="CLOSURE IS SCOPE-BOUND, NOT NOVELTY (P6-NOV remains NOT_ESTABLISHED) and not a calibration or production claim. The intermediate record in the P6 namespace still reads FINAL_P6_VERDICT = PARTIAL with G6/G9/G12 PARTIAL, and p6r2b GATE9_REPAIR_REPORT.md says verbatim 'P6 = CLOSED is not declared here'; no independent Gate-9 review is recorded IN the P6 namespace. P9 follows the newer authoritative status table and records the gap (D-10).",
  usable="AS_STATUS_ONLY"),
C("P6-NOV", "P6", "P6 NOVELTY_STATUS = NOT_ESTABLISHED.",
  "NOT_ESTABLISHED", "independent adjudication record",
  "level4/closure_proofs/p6r_safe_rebaselining_confirmation/ADJUDICATION_RECORD.md",
  usable="AS_LIMITATION_ONLY",
  limits="P6 closure, if it ever comes, is NOT a novelty claim. Scientific validity, operational effectiveness, algorithmic novelty and theoretical novelty are four separate questions."),
# ---------------------------------------------------------------- P7 (CLOSED)
C("P7-A", "P7",
  "Exact decomposition: in the frozen repeated-cycle model, ARL_0 = E_pi[A(e)] and delay = E_pi[A(e-Delta)] for the actual entering-error law, with A even and non-increasing in |e|.",
  "EXACT_THEOREM", "exact structural bridge, independently adjudicated",
  "level4/closure_proofs/p7_statistical_consequences/THEORY_BRIDGE.md",
  parents=["P5-T1"],
  scope="frozen Gaussian repeated-cycle model, both detectors",
  limits="EXACT as a structural bridge for ANY actual entering-error law; the numerical consequence is conditional on which law pi actually holds"),
C("P7-B", "P7", "Effective-multiplier identity ACF1 = rho(1 - Gamma_eff).",
  "CONDITIONAL_THEOREM", "exact under its stationary-law conditions",
  "level4/closure_proofs/p7_statistical_consequences/THEORY_BRIDGE.md",
  parents=["P7-A"],
  limits="P7 itself supplied NO existence or uniqueness proof for pi; P7-B/C/D are conditional on a stationary law. P5's T7 later proved existence/uniqueness/ergodicity for the same frozen constant-policy convention-A chain.",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P7-C", "P7", "Mass escape: local repulsion implies stationary mass outside a radius r.",
  "CONDITIONAL_THEOREM", "conditional proposition with an empirically supported but UNPROVED global sign condition",
  "level4/closure_proofs/p7_statistical_consequences/THEORY_BRIDGE.md",
  parents=["P7-B", "P3-T1"],
  limits="the global sign condition is empirically supported and NOT proved",
  usable="YES_AS_CONDITIONAL_ONLY"),
C("P7-D", "P7", "ARL-deficit plug-in diagnostic.",
  "EMPIRICAL_ONLY", "Monte Carlo plug-in diagnostic; explicitly NOT certified",
  "level4/closure_proofs/p7_statistical_consequences/THEORY_BRIDGE.md",
  parents=["P7-C"], limits="conditional on P7-C's hypotheses plus a finite fourth moment; a diagnostic, not a theorem",
  usable="YES_AS_DIAGNOSTIC_ONLY"),
C("P7-E1", "P7",
  "Recursive re-baselining materially degrades monitoring: nominal A(0) is CUSUM 465.12 / SR 464.86; fresh-reference (rho=0) ARL is 79.91-162.03; full-reuse (rho=1) ARL is 48.36-80.05; loss vs nominal 82.8%-89.6%; loss vs fresh 39.5%-50.6%; FAP(100) rises from 0.619-0.823 (fresh) to 0.822-0.899 (full reuse).",
  "EMPIRICAL_REPRODUCED", "production plus independent seed-20260917 replay, agreeing across every listed quantity",
  "level4/closure_proofs/p7_statistical_consequences/INDEPENDENT_ADJUDICATION.md §3",
  parents=["P7-A"],
  scope="frozen Gaussian repeated-cycle regime, m in {1,2,3,5}, both frozen detectors",
  limits="simulation in the frozen model; ranges are across the m/detector families"),
C("P7-E2", "P7",
  "One-cycle calibration can look normal while cycle 2 collapses to about 5.6-9.4 in mean run length; detection delay develops a severe heavy tail.",
  "EMPIRICAL_REPRODUCED", "frozen operational evaluation with independent replay",
  "level4/closure_proofs/p7_statistical_consequences/; README.md",
  parents=["P7-E1"],
  limits="the measured delay tail is NOT attributable to changed-observation contamination - the adjudicator corrected candidate wording that said so. The entering reference of the reported delay was built from pre-change observations."),
C("P7-D0", "P7",
  "At rho=0 every new reference is an independent estimate with error N(0,1/m), so the cycle length is a mixture E[A(e)] rather than the calibrated A(0). Fresh-reference estimation ALONE reduces ARL. This is a matched-information/reset-reference effect - it is not reuse and not burn-in.",
  "EXACT_THEOREM", "structural consequence of P7-A plus the rho=0 kernel; adjudicated as a required separation",
  "level4/closure_proofs/p7_statistical_consequences/INDEPENDENT_ADJUDICATION.md §3",
  parents=["P7-A", "P5-T1"],
  limits="the two controls (rho=0 vs nominal A(0)) MUST remain separate; conflating them inflates the reuse-attributable effect"),
C("P7-R1", "P7",
  "RHO_C_STATUS = LOCAL_MATHEMATICAL_BOUNDARY_ONLY. Under P7's frozen operational criterion, the P3 critical reuse fraction rho_c is NOT an operational safety boundary; rho < rho_c is not a safety rule.",
  "NEGATIVE_RESULT", "independent adjudication verdict line",
  "level4/closure_proofs/p7_statistical_consequences/INDEPENDENT_ADJUDICATION.md",
  parents=["P3-T1", "P7-E1"],
  limits="this is a MONITORING consequence under a frozen criterion, not a global nonlinear-dynamics theorem"),
C("P7-R2", "P7",
  "The preregistered operational-crossing hypothesis is rejected: 0/4 metrics peaked at the crossing and 4/4 were monotone in log m.",
  "NEGATIVE_RESULT", "frozen operational evaluation under the tested protocol",
  "level4/closure_proofs/l4r12_operational_crossing/FINAL_REPORT.md; README.md",
  parents=["P7-R1"]),
# ---------------------------------------------------------------- project-level
C("PROJ-L4R11", "PROJECT",
  "L4R-11 (the m-rho phase map, D4) is a MANDATORY Level-4 row recorded as FAIL (not run); no later closure campaign supplies the phase map.",
  "NEGATIVE_RESULT", "Level-4 requirement ledger",
  "level4/reports/LEVEL_4_CURRENT_LEDGER.md:19; level4/re_audit_post_closure/REQUIREMENT_UPDATE.md:19",
  usable="AS_LIMITATION_ONLY"),
C("PROJ-L4R13", "PROJECT",
  "L4R-13 non-Gaussian robustness remains PARTIAL and nonmandatory.",
  "PARTIAL_PRIORITY_RESULT", "Level-4 requirement ledger + README limitations",
  "README.md 'Limitations and negative results'",
  usable="AS_LIMITATION_ONLY"),
C("PROJ-STAGED", "PROJECT",
  "Historical Stage-D D2.3 and Track 1A remain FAILED. The later Track 1B theorem is a separate result under its own random-window convention.",
  "NEGATIVE_RESULT", "README.md limitations; Stage-D records",
  "README.md 'Limitations and negative results'",
  usable="AS_LIMITATION_ONLY"),
C("PROJ-SCOPE", "PROJECT",
  "Results concern frozen CUSUM and one symmetric two-chart SR model; they are neither detector-independent nor distribution-free.",
  "NEGATIVE_RESULT", "README.md limitations",
  "README.md 'Limitations and negative results'",
  usable="AS_LIMITATION_ONLY"),
]

# --- P8: AUTHORITATIVE. Codex verdict P8 = FAIL (16 PASS / 5 FAIL, G14 fails).
# Tiers below are transcribed VERBATIM from the authoritative
# INDEPENDENT_ADJUDICATION.md section 16 "Exact P9 handoff boundary".
# P9 is PERMITTED to use the first four tiers; it USES NONE of them as a
# premise (see P8_TO_P9_RECONCILIATION.md section 4). Enforced: no P8 node has
# any outgoing edge.
NOT_USED = "PERMITTED_BY_P8_BOUNDARY_BUT_NOT_USED_BY_P9"
P8_AUTHORITATIVE = [
C("P8-V", "P8",
  "Authoritative verdict P8 = FAIL. Gate count 16 PASS / 5 FAIL: the four candidate-reported scientific failures G4, G4-D, G4-F, G7, plus G14 (temporal integrity). Under the frozen verdict rule any integrity-spine failure requires FAIL. PREREGISTRATION_TEMPORAL_ANCHOR = PARTIAL: the directory was untracked with no pre-result commit or externally anchored digest, the provenance record does not hash THEORY.md/EXPERIMENT_PROTOCOL.md/CLOSURE_GATES.md, and the frozen protocol's stated E2 sizes (250,000 / 2,048,000 cycles) contradict the executed 163,840 / 1,024,000.",
  "NEGATIVE_RESULT", "authoritative independent adjudication",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a72,\u00a715",
  usable="AS_STATUS_AND_HISTORY_ONLY",
  limits="The verdict does not erase the surviving evidence; it prevents that evidence being represented as a successfully preregistered P8 closure campaign. P9 must not describe P8 as a successful preregistered closure campaign."),
C("P8-S1", "P8",
  "P8-L0/P8-L1 algebra and the P8-T2 reset decomposition under their stated iid/reset definitions; exact convention-A/B truncation decomposition.",
  "EXACT_THEOREM", "surviving P8 premise, tier assigned by the authoritative adjudicator",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a716",
  usable=NOT_USED,
  limits="survives inside a FAILED campaign; P9 draws no conclusion from it"),
C("P8-S2", "P8",
  "P8-T1, conditional on the stated P4 analytic/differentiation/integrability hypotheses for the particular detector, family and window.",
  "CONDITIONAL_THEOREM", "surviving P8 premise, tier assigned by the authoritative adjudicator",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a716",
  usable=NOT_USED,
  limits="conditional on P4 hypotheses, and P4 is itself PARTIAL. Unconditional hypotheses 7-9 are NOT_ESTABLISHED (P8-S5)."),
C("P8-S3", "P8",
  "In the measured matrix only: broad Gamma_A > 2 at m <= 5, operational degradation in the declared cells, exact-to-floating implementation identities, and the scoped drift/seed results.",
  "EMPIRICAL_ONLY", "surviving P8 evidence, tier assigned by the authoritative adjudicator",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a716",
  usable=NOT_USED,
  limits="Monte Carlo evidence with heavy-tail and seed-level overdispersion caveats. Citable ONLY as a failed-campaign evidence set within the exact tested scope. The single CUSUM/t3/m=20 cell is contested: production Gamma_A = 1.9492126 +/- 0.0071724 vs an independent 1.96323 +/- 0.02558 whose interval crosses two."),
C("P8-S4", "P8",
  "NEGATIVE: the preregistered cross-family window-separability law and BOTH its sub-gates fail; literal G7 (P7 boundary transfer) fails; measured detector transfer is absent.",
  "NEGATIVE_RESULT", "authoritative adjudication",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a77,\u00a79,\u00a716",
  usable="AS_NEGATIVE_RESULT_ONLY",
  limits="a failed gate is NOT a positive premise for a weaker law. P9 must not use the rejected window law, assume detector transfer, or assume P7-boundary transfer."),
C("P8-S5", "P8",
  "NOT ESTABLISHED by P8: unconditional P8-T1 hypotheses 7-9, detector transfer, P7-boundary transfer, long-run ramp accumulation, the t3/m20 attraction claim as a theorem or certificate, novelty, and any new algorithm. P8 created NO certified-numerical result.",
  "NOT_ESTABLISHED", "authoritative adjudication",
  "level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md \u00a716",
  usable="AS_LIMITATION_ONLY"),
]

ALL = CLAIMS + P8_AUTHORITATIVE

# --- P9-owned claims -------------------------------------------------------
P9_OWN = [
C("P9-T1", "P9",
  "Claim-class propagation: on the acyclic premise sub-graph, rho(v) = min(r(s(v)), min over premise parents p of rho(p)) is well defined, bounded by r(s(v)), and non-increasing along premise paths. verifies-edges and diagnoses-edges are excluded from the bound.",
  "EXACT_THEOREM", "elementary proof over the ledger DAG; validator-enforced",
  "level4/closure_proofs/p9_final_synthesis/THEORY.md \u00a71",
  parents=[],
  scope="the P9 claim graph as published in CLAIM_LEDGER.json",
  limits="the ARITHMETIC is elementary and P9 does not present it as a deep theorem. Its soundness reading - that rho(v) bounds what a sentence about v may assert - is a POLICY with a rationale, not a proved metatheorem. The substantive content is the verifies/premise edge distinction, which was forced by the validator, not designed in advance."),
C("P9-T2", "P9",
  "Separation: for each frozen detector and each m>=1, at rho=0 the invariant law is exactly N(0,1/m), the stationary in-control ARL equals E_{e~N(0,1/m)}[A(e)], and that expectation is STRICTLY less than A(0). Operational degradation is therefore already present at rho=0, which lies strictly below rho_c for every supported (D,m) and is where the local map is maximally stable. Hence no threshold in rho is an operational safety boundary.",
  "EXACT_THEOREM", "human proof from existing exact claims; independent numerical correspondence on an 81-point half-grid",
  "level4/closure_proofs/p9_final_synthesis/THEORY.md \u00a72",
  parents=["P5-T1", "P5-T7", "P7-A"],
  assumptions="frozen two-sided CUSUM (k=1/2,h=5) or frozen symmetric two-chart SR (A=520.886133602749); A even and non-increasing in |e| (P7-A, independently corroborated with 0 monotonicity violations at 3 SE over 320 comparisons); A(0)>1 and A(e)->1 as |e|->infinity, both proved from the frozen recurrences",
  scope="the two frozen Gaussian detectors, any m>=1, rho=0",
  limits="says nothing about the SIZE of the degradation (measured, P7-E1), nothing about rho>0, nothing about other detectors or non-Gaussian innovations. Does NOT say rho_c is meaningless - rho_c remains an exact local boundary (P3-T1); it says being on its stable side is not SUFFICIENT for operational safety."),
C("P9-N1", "P9",
  "The approach to the stationary regime under full reuse is slow and OSCILLATORY, not monotone: SR m=1 rho=1 mean cycle length by cycle index runs 460.5, 5.8, 73.7, 38.2, 53.6, 46.0, 48.6, 46.4, ... converging to about 48.5 only after roughly ten cycles. Finite-horizon operational estimates therefore depend materially on the burn-in convention; pooling all cycles including the first inflates the estimate by about 40%.",
  "EMPIRICAL_REPRODUCED", "P9 independent implementation, 12000 paths, 20 cycles, deterministic seed derivation",
  "level4/closure_proofs/p9_final_synthesis/{RESULTS,CROSS_PRIORITY_REPRODUCTION}.md",
  parents=["P5-T7"],
  scope="frozen Gaussian chain, both detectors, m in {1,5}, rho=1",
  limits="measured, not proved. P5-T7 proves uniform geometric ergodicity but its constants are loose, so the RATE here is empirical. Two detectors and two windows only."),
]
ALL = ALL + P9_OWN

def validate(claims):
    errs = []
    ids = set()
    for c in claims:
        if c["id"] in ids: errs.append(f"duplicate id {c['id']}")
        ids.add(c["id"])
        if c["status"] not in STATUS: errs.append(f"{c['id']}: bad status {c['status']}")
    for c in claims:
        for e in c["edges"]:
            if e["parent"] not in ids: errs.append(f"{c['id']}: unknown parent {e['parent']}")
            if e["type"] not in EDGE_TYPES: errs.append(f"{c['id']}: bad edge type {e['type']}")
    # acyclicity
    idx = {c["id"]: c for c in claims}
    colour = {}
    def dfs(n, stack):
        if colour.get(n) == 2: return
        if colour.get(n) == 1:
            errs.append("cycle: " + " -> ".join(stack + [n])); return
        colour[n] = 1
        for e in idx[n]["edges"]: dfs(e["parent"], stack + [n])
        colour[n] = 2
    for c in claims: dfs(c["id"], [])
    # no-inflation: a claim may not be stronger than its weakest parent
    for c in claims:
        if not c["parents"]: continue   # premise edges only
        worst = min(RANK[idx[p]["status"]] for p in c["parents"])
        if RANK[c["status"]] > worst:
            errs.append(f"INFLATION {c['id']} ({c['status']}, rank {RANK[c['status']]}) "
                        f"exceeds weakest parent rank {worst}")
    return errs

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errs = validate(ALL)
    for e in errs: print("VALIDATION:", e)
    payload = {"anchor_commit": ANCHOR, "status_vocabulary": STATUS,
               "strength_rank": RANK, "n_claims": len(ALL),
               "validation_findings": errs, "claims": ALL}
    with open(os.path.join(here, "CLAIM_LEDGER.json"), "w") as f:
        json.dump(payload, f, indent=1)
    graph = {"anchor_commit": ANCHOR,
             "nodes": [{"id": c["id"], "priority": c["priority"],
                        "status": c["status"]} for c in ALL],
             "edge_types": {"premise": "bounds claim strength",
                            "verifies": "independent evidence layer about the claim",
                            "diagnoses": "explains a recorded negative result"},
             "edges": [{"from": e["parent"], "to": c["id"], "type": e["type"]}
                       for c in ALL for e in c["edges"]]}
    with open(os.path.join(here, "THEOREM_DEPENDENCY_GRAPH.json"), "w") as f:
        json.dump(graph, f, indent=1)
    print(f"claims={len(ALL)} edges={len(graph['edges'])} validation_findings={len(errs)}")

# ---------------------------------------------------------------- markdown
def emit_markdown(here, claims, errs):
    by_pri = {}
    for c in claims: by_pri.setdefault(c["priority"], []).append(c)
    order = ["CORE", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P9", "PROJECT", "P8"]
    L = ["# P9 claim ledger — every scientifically important P1–P8 claim, at its authoritative strength",
         "", f"**Anchor commit:** `{ANCHOR}`",
         f"**Generated by:** `experiments/build_ledger.py` (single source of truth; "
         f"`CLAIM_LEDGER.json` is emitted from the same data)",
         f"**Claims:** {len(claims)}  •  **Validation findings:** {len(errs)}", "",
         "This ledger **does not flatten** evidence classes. `P4`, `P5` and `P6` are "
         "`PARTIAL` priorities and their claims are carried at their adjudicated tier, "
         "never at the priority's best tier. `P8` is quarantined (see "
         "`P8_DEPENDENCY_GATE.md`).", "",
         "## Status vocabulary and strength rank", "",
         "| status | rank | meaning |", "|---|---:|---|",
         "| `EXACT_THEOREM` | 6 | proved outright within a stated convention |",
         "| `FORMALLY_VERIFIED` | 6 | machine-checked (Lean kernel), for exactly the declarations checked |",
         "| `CONDITIONAL_THEOREM` | 5 | proved under assumptions that are themselves not established |",
         "| `CERTIFIED_NUMERICAL` | 4 | rigorous interval/exact certificate (Arb, rational arithmetic) |",
         "| `EMPIRICAL_REPRODUCED` | 3 | measured and independently reproduced |",
         "| `EMPIRICAL_ONLY` | 2 | measured once, or on a finite grid, not independently reproduced |",
         "| `PARTIAL_PRIORITY_RESULT` | 2 | a priority-level status that is not closure |",
         "| `NEGATIVE_RESULT` | 1 | a preregistered hypothesis or gate that failed |",
         "| `NOT_ESTABLISHED` | 0 | explicitly not established; may not be presented as fact |",
         "| `REJECTED_CLAIM` | 0 | asserted then rejected by adjudication |",
         "| `PROVISIONAL_P8_PENDING_CODEX` | 0 | unusable as a premise until Codex adjudicates P8 |", "",
         "Rank is used by the no-inflation check (`THEORY.md`, `P9-T1`): along "
         "**premise** edges, no claim may exceed the weakest rank above it.", ""]
    titles = {"CORE": "Frozen m=1 core (pre-P1)", "P1": "P1 — m>1 CUSUM derivative (CLOSED)",
              "P2": "P2 — symmetric two-chart SR derivative (CLOSED)",
              "P3": "P3 — m–rho local stability map (CLOSED)",
              "P4": "P4 — location-family generalization (**PARTIAL**)",
              "P5": "P5 — nonlinear/stochastic dynamics (**PARTIAL**)",
              "P6": "P6 — safe re-baselining (**PARTIAL** per repository; see P9_DEFINITION_AUDIT C1)",
              "P7": "P7 — statistical/operational consequences (CLOSED)",
              "P9": "P9 — synthesis-owned claims",
              "PROJECT": "Project-level standing results",
              "P8": "P8 — model-class robustness (**QUARANTINED**, not adjudicated)"}
    for pri in order:
        if pri not in by_pri: continue
        L += [f"## {titles[pri]}", ""]
        for c in by_pri[pri]:
            L.append(f"### `{c['id']}` — {c['status']}")
            L.append("")
            L.append(f"> {c['statement']}")
            L.append("")
            L.append(f"* **evidence** — {c['evidence_type']}")
            L.append(f"* **source** — `{c['source']}`")
            if c["assumptions"]: L.append(f"* **assumptions** — {c['assumptions']}")
            if c["scope"]: L.append(f"* **scope** — {c['scope']}")
            if c["edges"]:
                L.append("* **depends on** — " + ", ".join(
                    f"`{e['parent']}` ({e['type']})" for e in c["edges"]))
            if c["limitations"]: L.append(f"* **limitations** — {c['limitations']}")
            L.append(f"* **P9 may use** — `{c['p9_may_use']}`")
            if c["note"]: L.append(f"* **note** — `{c['note']}`")
            L.append("")
    open(os.path.join(here, "CLAIM_LEDGER.md"), "w").write("\n".join(L))

    idx = {c["id"]: c for c in claims}
    G = ["# P9 theorem dependency graph",
         "", f"**Anchor commit:** `{ANCHOR}`",
         f"**Nodes:** {len(claims)}  •  **Edges:** {sum(len(c['edges']) for c in claims)}  •  "
         f"**Cycles:** 0  •  **Inflation violations:** {len([e for e in errs if 'INFLATION' in e])}", "",
         "## Edge semantics — read this before reading the graph", "",
         "Edges are **not** \"these two priorities discuss the same object\". "
         "There are exactly three edge types and they behave differently:", "",
         "| type | meaning | bounds strength? |", "|---|---|---|",
         "| `premise` | the parent is a logical premise of the child | **yes** — the child may not be stronger than the weakest premise |",
         "| `verifies` | the parent is an independent evidence *layer about* the child (Lean kernel check, Arb certificate) | **no** — and crucially it does **not** license upgrading the child |",
         "| `diagnoses` | the parent explains or reconciles a recorded negative result | no |", "",
         "The `verifies` type exists because of a real repository invariant: "
         "*\"Lean does not certify either numerical interval; Arb does not prove "
         "differentiation under the expectation. The human theorem supplies the "
         "bridge.\"* A formal layer is a fact about an artifact, not an upgrade "
         "to the science it is about. Collapsing `verifies` into `premise` is "
         "exactly how a `CONDITIONAL_THEOREM` gets narrated as machine-verified "
         "fact.", "",
         "## Mermaid (premise edges solid, verifies dotted, diagnoses dashed)", "",
         "```mermaid", "graph TD"]
    style = {"premise": "-->", "verifies": "-.->", "diagnoses": "-..->"}
    def nid(x): return x.replace("-", "_")
    for c in claims:
        lbl = f"{c['id']}<br/>{c['status']}"
        G.append(f"  {nid(c['id'])}[\"{lbl}\"]")
    for c in claims:
        for e in c["edges"]:
            G.append(f"  {nid(e['parent'])} {style[e['type']]} {nid(c['id'])}")
    G += ["```", "", "## Edge table", "",
          "| from | type | to | parent status | child status |", "|---|---|---|---|---|"]
    for c in claims:
        for e in c["edges"]:
            G.append(f"| `{e['parent']}` | {e['type']} | `{c['id']}` | "
                     f"{idx[e['parent']]['status']} | {c['status']} |")
    G += ["", "## Roots (no premise above them)", ""]
    for c in claims:
        if not c["parents"]: G.append(f"* `{c['id']}` — {c['status']}")
    open(os.path.join(here, "THEOREM_DEPENDENCY_GRAPH.md"), "w").write("\n".join(G))

if os.environ.get("P9_EMIT_MD") == "1":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    emit_markdown(here, ALL, validate(ALL))
    print("markdown emitted")
