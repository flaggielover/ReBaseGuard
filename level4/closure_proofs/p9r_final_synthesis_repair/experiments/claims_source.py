"""Source-derived node table for the P9R evidence graph.

Every row is transcribed from an authoritative artifact and carries the exact
path and the section/table it came from.  ``build_ledger.py`` re-reads those
paths at build time and fails if one is missing, so the ledger cannot drift
away from the repository.

This table is **not** a copy of P9's ``CLAIM_LEDGER.json``.  It was rebuilt
from the adjudications themselves.  Several P9 rows conflated an exact identity
with an empirical or conditional conclusion and had to be split (``P7-A`` ->
``P7-A-ID`` / ``P7-A-MONO`` / ``P7-A-OP``; ``P7-D0`` -> ``P7-D0-ID`` /
``P7-D0-DEF``), one was reclassified (``P3-X1``), and the hypothesis that P9
left implicit is now an explicit node (``ASM-DOM``).

Node kinds
----------
``DEFINITION``  a frozen modelling convention; carries no claim class.
``ASSUMPTION``  a hypothesis some claim needs; carries a claim class so that
                its epistemic strength is visible in the graph.
``CLAIM``       a scientific assertion; carries a frozen claim class.
``STATUS``      an adjudicated priority status; carries no claim class and may
                never be a logical premise of anything.

``hypotheses`` values
---------------------
``NONE_BEYOND_MODEL``            nothing assumed beyond the frozen definitions.
``DISCHARGED_FOR_FROZEN_MODEL``  hypotheses stated and proved for this model.
``STATED_NOT_DISCHARGED``        at least one hypothesis is assumed, not proved.
``NOT_APPLICABLE``               empirical, provenance or status rows.
"""
from __future__ import annotations

P1 = "level4/closure_proofs/m_gt_1_priority1"
P2 = "level4/closure_proofs/sr_derivative_priority2"
P2B = "level4/closure_proofs/sr_derivative"
P3 = "level4/closure_proofs/m_rho_stability_priority3"
P4 = "level4/closure_proofs/p4_theory_generalization"
P5 = "level4/closure_proofs/p5_nonlinear_dynamics"
P6 = "level4/closure_proofs/p6_safe_rebaselining"
P7 = "level4/closure_proofs/p7_statistical_consequences"
P8 = "level4/closure_proofs/p8_model_class_robustness"
P8R = "level4/closure_proofs/p8r_temporal_integrity_repair"
P9 = "level4/closure_proofs/p9_final_synthesis"
P9RNS = "level4/closure_proofs/p9r_final_synthesis_repair"
FROZEN = "level4/src/rebaseguard_level4/frozen.py"
STAGED = "level4/stage_d/src/stopped.py"

NODES = [
# ------------------------------------------------------------------ definitions
dict(id="DEF-CUSUM", kind="DEFINITION", priority="FROZEN",
     statement="Frozen two-sided CUSUM: k=1/2, h=5, S+_t=max(0,S+_{t-1}+Z_t-k), "
               "S-_t=max(0,S-_{t-1}-Z_t-k), inclusive alarm tested after the update.",
     source=FROZEN, section="module docstring; K_FROZEN/H_FROZEN; step_scalar",
     scope="frozen Gaussian CUSUM", edges=[]),
dict(id="DEF-SR", kind="DEFINITION", priority="FROZEN",
     statement="Frozen symmetric two-chart SR with A=520.886133602749 and NO "
               "headstart: R+_0=R-_0=0, R+_t=(1+R+_{t-1})exp(Z_t-1/2), "
               "R-_t=(1+R-_{t-1})exp(-Z_t-1/2), inclusive alarm on the "
               "post-update raw state. Log form stores y=log(1+R), y_0=0, and "
               "tests ell=y+Z-1/2=log R.",
     source=STAGED, section="_sr_update; restated verbatim in "
                            f"{P7}/src/rebaseguard_p7/detectors.py::sr_update "
                            f"and {P2B}/src/rebaseguard_sr_derivative/log_sr.py",
     scope="frozen Gaussian SR", edges=[]),
dict(id="DEF-CONV-A", kind="DEFINITION", priority="FROZEN",
     statement="Convention A: no minimum dwell, tau=inf{t>=1: alarm}; reuse "
               "window w=min(m,tau) with denominator w; "
               "e_{j+1}=rho(e_j+zbar_w)+(1-rho)F with F~N(0,1/m) drawn "
               "independently of the stopping event; detector state reset at "
               "every cycle boundary.",
     source=f"{P9}/DEFINITION_CROSSWALK.md", section="X-03",
     scope="the repeated-cycle chain used by P5, P7, P9 and P9R", edges=[]),
dict(id="DEF-A", kind="DEFINITION", priority="FROZEN",
     statement="A(e) := E_e[tau] for a single cycle started from the reset "
               "detector state with constant entering reference error e. A "
               "depends on the detector only, not on m or rho.",
     source=f"{P7}/THEORY_BRIDGE.md", section="response function",
     scope="both frozen detectors",
     edges=[dict(parent="DEF-CUSUM", type="SCOPE_RESTRICTION"),
            dict(parent="DEF-SR", type="SCOPE_RESTRICTION")]),

# ------------------------------------------------------------------ assumptions
dict(id="ASM-DOM", kind="ASSUMPTION", priority="P9R", claim_class="NOT_ESTABLISHED",
     statement="A(e) <= A(0) for N(0,1/m)-almost every e.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md",
     section="§5 'The failed exact step'",
     scope="both frozen detectors, all m>=1",
     hypotheses="NOT_APPLICABLE",
     limitation="This is the ONLY premise separating P9R-T2b from an exact "
                "theorem. It is weaker than global monotonicity: only global "
                "maximality of A at e=0 is needed. It is not proved.",
     edges=[dict(parent="DEF-A", type="SCOPE_RESTRICTION")]),
dict(id="ASM-MONO", kind="ASSUMPTION", priority="P7", claim_class="NOT_ESTABLISHED",
     statement="A is even and globally non-increasing in |e|.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md",
     section="§ theory-status table, P7-A row: 'Global strict monotonicity of "
             "A is not proved.'",
     scope="both frozen detectors",
     hypotheses="NOT_APPLICABLE",
     limitation="Strictly stronger than ASM-DOM, and not needed by P9R-T2b. "
                "P9 promoted this to an exact premise inside P7-A; P9R does not.",
     edges=[dict(parent="DEF-A", type="SCOPE_RESTRICTION")]),
dict(id="ASM-P1-EXPMOM", kind="ASSUMPTION", priority="P1",
     claim_class="NOT_ESTABLISHED",
     statement="Stopped exponential-moment bound for the frozen Gaussian CUSUM, "
               "from which integrability and local domination are derived.",
     source=f"{P1}/DEFINITION_AUDIT.md", section="§4",
     scope="frozen Gaussian CUSUM", hypotheses="NOT_APPLICABLE",
     limitation="Stated as an assumed hypothesis; P1's Lean spine explicitly "
                "does not establish it.",
     edges=[dict(parent="DEF-CUSUM", type="SCOPE_RESTRICTION")]),
dict(id="ASM-P4-A1A7", kind="ASSUMPTION", priority="P4",
     claim_class="NOT_ESTABLISHED",
     statement="P4's location-family regularity hypotheses (A1)-(A7).",
     source=f"{P4}/", section="theorem statement; P9 adjudication §3 P4 row",
     scope="general location families", hypotheses="NOT_APPLICABLE",
     edges=[]),

# ------------------------------------------------------------------ P1 / P2 / P3
dict(id="P1-T1", kind="CLAIM", priority="P1", claim_class="CONDITIONAL_THEOREM",
     statement="Frozen truncated-window derivative theorem for the m>1 Gaussian "
               "CUSUM: F'_rho(0)=rho(1-Gamma) with Gamma the stopped-selection gain.",
     source=f"{P1}/THEOREM.md", section="§1-§3; PROOF.md §; DEFINITION_AUDIT.md §4",
     scope="frozen Gaussian CUSUM, Track-1B convention, m>=1",
     hypotheses="STATED_NOT_DISCHARGED",
     limitation="P9R classifies this CONDITIONAL rather than EXACT because "
                "DEFINITION_AUDIT.md §4 says the integrability and domination "
                "obligations are discharged FROM AN ASSUMED stopped "
                "exponential-moment bound. This is a downgrade relative to P9's "
                "ledger and does not change P1's authoritative CLOSED status.",
     edges=[dict(parent="DEF-CUSUM", type="SCOPE_RESTRICTION"),
            dict(parent="ASM-P1-EXPMOM", type="ASSUMPTION")]),
dict(id="P1-L1", kind="CLAIM", priority="P1", claim_class="FORMALLY_VERIFIED",
     statement="Lean proof spine for the abstract dominated-differentiation and "
               "moment machinery behind P1-T1; kernel-checked, no sorry, "
               "standard Mathlib axioms only.",
     source=f"{P1}/LEAN_CORRESPONDENCE.md", section="axiom audit",
     scope="the abstract spine ONLY", hypotheses="NOT_APPLICABLE",
     formal_evidence="Lean 4 kernel; axioms propext, Classical.choice, Quot.sound; "
                     "no sorry/admit/scientific axiom",
     limitation="Does not construct the concrete CUSUM probability space, its "
                "stopping time, its stopped moments or the concrete domination "
                "inequality.",
     edges=[dict(parent="P1-T1", type="FORMAL_SUPPORT")]),
dict(id="P2-T1", kind="CLAIM", priority="P2", claim_class="EXACT_THEOREM",
     statement="Frozen symmetric two-chart SR derivative/stability theorem, "
               "no headstart.",
     source=f"{P2}/THEOREM.md", section="THEOREM.md; PROOF.md §1-§6",
     scope="frozen Gaussian SR", hypotheses="DISCHARGED_FOR_FROZEN_MODEL",
     limitation="Gaussian m>1 numerical values remain Monte Carlo.",
     edges=[dict(parent="DEF-SR", type="SCOPE_RESTRICTION"),
            dict(parent="P2-D1", type="LOGICAL_PREMISE")]),
dict(id="P2-D1", kind="CLAIM", priority="P2", claim_class="EXACT_THEOREM",
     statement="All eight concrete Gaussian SR analytic obligations SR-A1..SR-A8 "
               "(a.s. finiteness and geometric tail, stopped measurability, "
               "integrability, exponential stopped moments, stopped likelihood "
               "identity, local domination, reflection symmetry) are PROVED for "
               "the frozen model.",
     source=f"{P2}/ASSUMPTION_DISCHARGE.md", section="discharge table (8 rows, all PROVED)",
     scope="frozen Gaussian SR", hypotheses="DISCHARGED_FOR_FROZEN_MODEL",
     limitation="Numerical evidence discharges none of these rows; the "
                "discharge is analytic.",
     edges=[dict(parent="DEF-SR", type="SCOPE_RESTRICTION")]),
dict(id="P2-L1", kind="CLAIM", priority="P2", claim_class="FORMALLY_VERIFIED",
     statement="Lean proof spine for the SR derivative theorem, including the "
               "finite-path reflection spine.",
     source=f"{P2}/LEAN_CORRESPONDENCE.md", section="axiom audit",
     scope="the spine ONLY", hypotheses="NOT_APPLICABLE",
     formal_evidence="Lean 4 kernel; standard Mathlib axioms propext, "
                     "Classical.choice, Quot.sound; no sorry",
     edges=[dict(parent="P2-T1", type="FORMAL_SUPPORT")]),
dict(id="P2-C1", kind="CLAIM", priority="P2", claim_class="CERTIFIED_NUMERICAL",
     statement="Certified enclosure of the frozen m=1 symmetric two-chart SR "
               "gain: Gamma_SR in [5.800391799508442, 28.781285803081492].",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§10",
     scope="frozen m=1 SR ONLY", hypotheses="NOT_APPLICABLE",
     certified_evidence="Arb interval arithmetic; 28 focused certificate/auditor "
                        "tests pass",
     limitation="Certifies a number. It does not certify the derivative bridge, "
                "other windows, other detectors, P9R-T2a/b, or the campaign.",
     edges=[dict(parent="P2-T1", type="CERTIFIED_SUPPORT")]),
dict(id="P3-T1", kind="CLAIM", priority="P3", claim_class="EXACT_THEOREM",
     statement="First-order local reuse boundary rho_c = 1/|1-Gamma| for the "
               "conditional-mean map, with attraction below and repulsion above.",
     source=f"{P3}/THEOREM.md", section="Lemmas 1-3, Theorem 4",
     scope="the two frozen Gaussian detectors, m in {1,2,3,5}; LOCAL and "
           "DETERMINISTIC",
     hypotheses="NONE_BEYOND_MODEL",
     limitation="No global, stationary, detector-universal or non-Gaussian "
                "conclusion follows.",
     edges=[dict(parent="DEF-CUSUM", type="SCOPE_RESTRICTION"),
            dict(parent="DEF-SR", type="SCOPE_RESTRICTION")]),
dict(id="P3-X1", kind="CLAIM", priority="P3", claim_class="CERTIFIED_NUMERICAL",
     statement="Exact rational witnesses: CUSUM-compatible gain 15/2 gives "
               "rho_c=2/13 for every m; SR-compatible gains 4, 3, 8/3, 12/5 give "
               "rho_c=1/3, 1/2, 3/5, 5/7; every rational boundary satisfies "
               "|rho_c(1-Gamma)|=1 exactly.",
     source=f"{P3}/CLOSURE_REPORT.md", section="§5 'Exact witnesses and Arb audit'",
     scope="witness rows only", hypotheses="NOT_APPLICABLE",
     certified_evidence="exact Python Fraction arithmetic plus a python-flint/Arb "
                        "128-bit replay used as a consistency enclosure",
     limitation="REPAIRED CLASSIFICATION. P9 recorded this as FORMALLY_VERIFIED. "
                f"{P3}/LEAN_CORRESPONDENCE.md states the Priority-3 Lean file "
                "'makes no numerical claim', so there is no formal-kernel "
                "evidence for these witnesses. The certificate contains no "
                "Gaussian gain and records gaussian_layers_certified=false.",
     edges=[dict(parent="P3-T1", type="CERTIFIED_SUPPORT")]),
dict(id="P3-N1", kind="CLAIM", priority="P3", claim_class="EMPIRICAL_ONLY",
     statement="Gaussian boundary values rho_c(D,m) obtained by applying the "
               "exact P3-T1 formula to the Monte Carlo P1/P2 gain estimates.",
     source=f"{P3}/results/boundary_table.json", section="GAUSSIAN layers",
     scope="two detectors, m in {1,2,3,5}", hypotheses="NOT_APPLICABLE",
     limitation="The formula is exact; the numbers inherit Monte Carlo error "
                "from the gain estimates and are not certified.",
     edges=[dict(parent="P3-T1", type="LOGICAL_PREMISE")]),
dict(id="P3-L1", kind="CLAIM", priority="P3", claim_class="FORMALLY_VERIFIED",
     statement="Lean formalisation of the generic stability-map logic, including "
               "definitional agreement with the Priority-1 and Priority-2 "
               "attraction/repulsion predicates.",
     source=f"{P3}/LEAN_CORRESPONDENCE.md", section="correspondence table; axiom audit",
     scope="generic stability-map logic ONLY", hypotheses="NOT_APPLICABLE",
     formal_evidence="Lean 4 kernel; 14 declarations; axioms propext, "
                     "Classical.choice, Quot.sound; no sorry",
     limitation="Makes NO numerical claim; the campaign's numerical work is "
                "checked by tests and Arb, not by Lean.",
     edges=[dict(parent="P3-T1", type="FORMAL_SUPPORT")]),
dict(id="P3-PROV", kind="CLAIM", priority="P3", claim_class="PROVENANCE_LIMITATION",
     statement="D-15: P3's 49 files arrived in a single uncommitted intake, so "
               "the grid preregistration cannot be authenticated.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§7 D-15",
     scope="P3 process history", hypotheses="NOT_APPLICABLE",
     limitation="Does not threaten the analytic boundary formula, which is not "
                "fitted to the grid. Remains open.",
     edges=[dict(parent="P3-T1", type="PROVENANCE")]),
]

NODES += [
# ------------------------------------------------------------------ P4 / P5 / P6
dict(id="P4-T1", kind="CLAIM", priority="P4", claim_class="CONDITIONAL_THEOREM",
     statement="General location-family derivative theorem under hypotheses "
               "(A1)-(A7).",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3, P4 row",
     scope="location families satisfying (A1)-(A7)",
     hypotheses="STATED_NOT_DISCHARGED",
     limitation="Survives only conditionally and only at P4's PARTIAL strength.",
     edges=[dict(parent="ASM-P4-A1A7", type="ASSUMPTION"),
            dict(parent="P4-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P4-T2N", kind="CLAIM", priority="P4", claim_class="CONDITIONAL_THEOREM",
     statement="Narrowed P4-T2: Gaussian sufficiency together with explicit "
               "non-Gaussian correction failures. NOT an iff characterisation.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3, P4 row",
     scope="tested location families", hypotheses="STATED_NOT_DISCHARGED",
     limitation="The converse was explicitly narrowed; it may not be written as "
                "an equivalence.",
     edges=[dict(parent="P4-T1", type="LOGICAL_PREMISE")]),
dict(id="P4-L1", kind="CLAIM", priority="P4", claim_class="FORMALLY_VERIFIED",
     statement="Lean proof spine for P4: 19 kernel-checked declarations.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§6 class table; §10",
     scope="the spine ONLY", hypotheses="NOT_APPLICABLE",
     formal_evidence="Lean 4 kernel; propext, Classical.choice, Quot.sound; no sorry",
     limitation="Does not construct the stopped probability model and does not "
                "discharge L1-L5. A verifies-style edge, never a premise edge.",
     edges=[dict(parent="P4-T1", type="FORMAL_SUPPORT")]),
dict(id="P4-F1", kind="CLAIM", priority="P4", claim_class="NEGATIVE_RESULT",
     statement="Three frozen preregistered numerical closure gates remain "
               "literally false; none was weakened or rewritten.",
     source="README.md", section="root status table, P4 row",
     scope="P4's frozen gates", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P4-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P4-RESULT", kind="CLAIM", priority="P4",
     claim_class="PARTIAL_PRIORITY_RESULT",
     statement="P4's surviving content is usable downstream only at conditional "
               "strength and inside its stated scope.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3",
     scope="downstream use of P4", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P4-T1", type="LOGICAL_PREMISE"),
            dict(parent="P4-F1", type="NEGATIVE_RESULT_CONSTRAINT"),
            dict(parent="P4-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P5-T1", kind="CLAIM", priority="P5", claim_class="EXACT_THEOREM",
     statement="Raw-mean identity: the frozen convention-A update collapses "
               "identically to e_{j+1} = rho * (mean of the last min(m,tau) RAW "
               "N(0,1) observations) + (1-rho) * N(0,1/m). The entering error "
               "cancels from e_j + zbar_w.",
     source=f"{P5}/THEOREM.md", section="P5-T1; PROOF.md; INDEPENDENT_ADJUDICATION.md",
     scope="frozen Gaussian constant-policy convention-A chain, both detectors",
     hypotheses="NONE_BEYOND_MODEL",
     limitation="An identity about the update rule. It is not by itself a "
                "dynamical or operational conclusion.",
     edges=[dict(parent="DEF-CONV-A", type="SCOPE_RESTRICTION")]),
dict(id="P5-T7", kind="CLAIM", priority="P5", claim_class="EXACT_THEOREM",
     statement="For each frozen detector, each fixed m>=1 and each fixed rho in "
               "[0,1], the reference-error chain admits a two-step whole-space "
               "minorisation, a unique invariant law, uniform geometric "
               "convergence in total variation, and finite invariant moments of "
               "every positive order.",
     source=f"{P5}/STATIONARY_DYNAMICS.md",
     section="P5-T7; INDEPENDENT_ADJUDICATION.md",
     scope="PER FIXED (detector, m, rho); fixed constant policy only",
     hypotheses="DISCHARGED_FOR_FROZEN_MODEL",
     limitation="Constants are qualitative and confirmed loose, so convergence "
                "RATES are empirical. Not adaptive kernels.",
     edges=[dict(parent="P5-T1", type="LOGICAL_PREMISE")]),
dict(id="P5-T11", kind="CLAIM", priority="P5", claim_class="EXACT_THEOREM",
     statement="Stationary autocorrelation identity for the reference-error chain.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3 P5 row; §7 D-13",
     scope="fixed-policy frozen chain", hypotheses="DISCHARGED_FOR_FROZEN_MODEL",
     limitation="Exact as an identity. Its gridded-map/PCHIP plug-in evaluation "
                "is a separate, defective numerical object (P5-D13).",
     edges=[dict(parent="P5-T7", type="LOGICAL_PREMISE")]),
dict(id="P5-D13", kind="CLAIM", priority="P5", claim_class="NOT_ESTABLISHED",
     statement="D-13: the gridded-map / PCHIP plug-in used to evaluate P5-T11 "
               "lacks a valid uncertainty budget; the residual reaches about 16 "
               "chain standard errors, while a direct realized-window replay "
               "reduces the paired gap to -0.00045 +/- 0.00034.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§7 D-13",
     scope="the plug-in evaluation, not the identity",
     hypotheses="NOT_APPLICABLE",
     limitation="Scope-limiting numerical/model-reconstruction defect. It must "
                "not be summarised as 'within 3.5% agreement'. Remains open.",
     edges=[dict(parent="P5-T11", type="CONSISTENCY_CHECK")]),
dict(id="P5-E1", kind="CLAIM", priority="P5", claim_class="EMPIRICAL_ONLY",
     statement="P5's optima, bimodality onset, attraction behaviour and m trends "
               "are finite-grid measurements.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3 P5 row; §6 class table",
     scope="the tested finite grid", hypotheses="NOT_APPLICABLE",
     limitation="May not be written as theorems about m or about attraction.",
     edges=[dict(parent="P5-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P5-RESULT", kind="CLAIM", priority="P5",
     claim_class="PARTIAL_PRIORITY_RESULT",
     statement="P5's exact identities survive in full; its dynamical and "
               "operational conclusions survive only as conditional or "
               "finite-grid empirical statements.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3",
     scope="downstream use of P5", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P5-T1", type="LOGICAL_PREMISE"),
            dict(parent="P5-T7", type="LOGICAL_PREMISE"),
            dict(parent="P5-E1", type="EMPIRICAL_SUPPORT"),
            dict(parent="P5-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P6-T6ABC", kind="CLAIM", priority="P6", claim_class="EXACT_THEOREM",
     statement="P6 theorems T6-A/B/C at their stated policy, kernel and one-step "
               "scopes.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§3 P6 row; §9",
     scope="the stated policy/kernel/one-step scopes ONLY",
     hypotheses="DISCHARGED_FOR_FROZEN_MODEL",
     limitation="The P6 chain is a DIFFERENT kernel from the fixed-policy chain "
                "P5-T7 covers; P5-T7 does not supply P6's stationarity.",
     edges=[]),
dict(id="P6-E1", kind="CLAIM", priority="P6", claim_class="EMPIRICAL_REPRODUCED",
     statement="P6's safe-rebaselining policy effectiveness is confirmed and "
               "replicated in the tested simulation and semi-real regimes.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§9",
     scope="tested regimes only", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P6-T6ABC", type="EMPIRICAL_SUPPORT")]),
dict(id="P6-LIM", kind="CLAIM", priority="P6", claim_class="NOT_ESTABLISHED",
     statement="P6 calibration quality (6/8 converged, sparse cells, final refit "
               "not a verified fixed point), production validation, transfer to "
               "detector-state-reading or adaptive kernels, and novelty are not "
               "established; the missing independent Gate-9 review inside the P6 "
               "namespace is a traceability gap.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§9",
     scope="P6", hypotheses="NOT_APPLICABLE",
     limitation="P6's CLOSED campaign status does not imply any of these.",
     edges=[dict(parent="P6-STATUS", type="STATUS_PROPAGATION")]),
]

NODES += [
# ------------------------------------------------------------------ P7 (split)
dict(id="P7-A-ID", kind="CLAIM", priority="P7", claim_class="EXACT_THEOREM",
     statement="Exact finite-cycle conditional identity: given the entering "
               "error e_j, the reset state and iid innovations, E[tau_j | e_j] = "
               "A(e_j); and for ANY entering-error law pi with A pi-integrable, "
               "ARL_0 = E_pi[A(e)] and the first shifted-cycle mean is "
               "E_pi[A(e-Delta)].",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md",
     section="theory-status table, P7-A row",
     scope="frozen Gaussian repeated-cycle model, both detectors",
     hypotheses="NONE_BEYOND_MODEL",
     limitation="SPLIT NODE. This is the exact part of P9's P7-A only. It "
                "carries no monotonicity content and no numerical conclusion. "
                "E_pi notation is conditional on existence/integrability of pi.",
     edges=[dict(parent="DEF-A", type="LOGICAL_PREMISE"),
            dict(parent="DEF-CONV-A", type="SCOPE_RESTRICTION")]),
dict(id="P7-A-MONO", kind="CLAIM", priority="P7", claim_class="NOT_ESTABLISHED",
     statement="Global monotonicity of A in |e| is NOT proved by P7.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md",
     section="P7-A row: 'Global strict monotonicity of A is not proved.'; "
             "THEORY_BRIDGE.md line 27: 'strict global monotonicity is not "
             "proved here.'",
     scope="both frozen detectors", hypotheses="NOT_APPLICABLE",
     limitation="SPLIT NODE. P9 folded this into its P7-A EXACT_THEOREM row; "
                "that promotion is the defect P9R repairs.",
     edges=[dict(parent="ASM-MONO", type="ASSUMPTION")]),
dict(id="P7-A-OP", kind="CLAIM", priority="P7", claim_class="EMPIRICAL_ONLY",
     statement="On P7's response grid, A is observed to decrease in |e|.",
     source=f"{P7}/THEORY_BRIDGE.md", section="line 27 and the response-curve section",
     scope="P7's finite response grid", hypotheses="NOT_APPLICABLE",
     limitation="Grid evidence. It may support ASM-DOM but may never discharge it.",
     edges=[dict(parent="ASM-MONO", type="EMPIRICAL_SUPPORT"),
            dict(parent="ASM-DOM", type="EMPIRICAL_SUPPORT")]),
dict(id="P7-D0-ID", kind="CLAIM", priority="P7", claim_class="EXACT_THEOREM",
     statement="At rho=0 every entering reference is an independent estimate "
               "with error N(0,1/m), so the in-control cycle length is the "
               "mixture E[A(e)] and not the calibrated A(0). This is a "
               "matched-information / reset-reference effect; it is neither "
               "reuse nor burn-in.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md", section="§3",
     scope="both frozen detectors, all m>=1, rho=0",
     hypotheses="NONE_BEYOND_MODEL",
     limitation="SPLIT NODE: identity content only. That the mixture is SMALLER "
                "than A(0) is P7-D0-DEF and is conditional.",
     edges=[dict(parent="P7-A-ID", type="LOGICAL_PREMISE"),
            dict(parent="P5-T1", type="LOGICAL_PREMISE")]),
dict(id="P7-D0-DEF", kind="CLAIM", priority="P7", claim_class="CONDITIONAL_THEOREM",
     statement="Fresh-reference estimation alone REDUCES the in-control ARL "
               "relative to A(0).",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md", section="§3",
     scope="both frozen detectors, rho=0", hypotheses="STATED_NOT_DISCHARGED",
     limitation="SPLIT NODE: requires ASM-DOM. P9 carried this inside an "
                "EXACT_THEOREM row.",
     edges=[dict(parent="P7-D0-ID", type="LOGICAL_PREMISE"),
            dict(parent="ASM-DOM", type="ASSUMPTION")]),
dict(id="P7-BCD", kind="CLAIM", priority="P7", claim_class="CONDITIONAL_THEOREM",
     statement="P7-B (conditional-exact stationary identity), P7-C (conditional "
               "proposition with an empirically supported but unproved global "
               "sign condition) and P7-D (Monte Carlo plug-in diagnostic, not "
               "certified) retain their conditions.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md", section="theory-status table",
     scope="frozen model", hypotheses="STATED_NOT_DISCHARGED",
     limitation="P7-D additionally needs a finite fourth moment and monotonicity "
                "of A; the former 'certified deficit' wording was removed.",
     edges=[dict(parent="P7-A-ID", type="LOGICAL_PREMISE"),
            dict(parent="ASM-MONO", type="ASSUMPTION")]),
dict(id="P7-E1", kind="CLAIM", priority="P7", claim_class="EMPIRICAL_REPRODUCED",
     statement="Operational degradation under recursive re-baselining: fresh "
               "(rho=0) ARL 79.91-162.03 and full-reuse (rho=1) ARL 48.36-80.05 "
               "across the eight frozen (detector, m) families, at n_rep=5000, "
               "n_cycles=50, burn_in=12.",
     source=f"{P7}/results/consequences.json",
     section="cells with rho in {0,1}; ranges restated in INDEPENDENT_ADJUDICATION.md",
     scope="two Gaussian detectors, m in {1,2,3,5}", hypotheses="NOT_APPLICABLE",
     limitation="Monte Carlo. Estimator is the per-replicate mean cycle length "
                "after burn-in.",
     edges=[dict(parent="P7-A-ID", type="EMPIRICAL_SUPPORT")]),
dict(id="P7-E2", kind="CLAIM", priority="P7", claim_class="EMPIRICAL_REPRODUCED",
     statement="Cycle-2 collapse under full reuse: mean second-cycle length "
               "5.60-9.35 against a first cycle of about 447-492.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md", section="cycle-2 discussion",
     scope="two Gaussian detectors, m in {1,2,3,5}, rho=1",
     hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P7-E1", type="EMPIRICAL_SUPPORT")]),
dict(id="P7-R1", kind="CLAIM", priority="P7", claim_class="NEGATIVE_RESULT",
     statement="Under P7's frozen operational criterion and its two Gaussian "
               "detector/window families, rho_c is REJECTED as an operational "
               "safety boundary: rho < rho_c is not validated as a safety rule.",
     source=f"{P7}/INDEPENDENT_ADJUDICATION.md",
     section="RHO_C_STATUS = LOCAL_MATHEMATICAL_BOUNDARY_ONLY",
     scope="P7's frozen criterion, two Gaussian detectors, m in {1,2,3,5}",
     hypotheses="NOT_APPLICABLE",
     limitation="A negative result about ONE criterion in ONE tested family. It "
                "does not prove that no rho-based operational boundary can exist.",
     edges=[dict(parent="P7-E1", type="EMPIRICAL_SUPPORT"),
            dict(parent="P3-T1", type="SCOPE_RESTRICTION")]),

# ------------------------------------------------------------------ P8 / P8R
dict(id="P8-L0L1", kind="CLAIM", priority="P8", claim_class="EXACT_THEOREM",
     statement="P8-L0/P8-L1 algebra, the P8-T2 reset decomposition and the exact "
               "convention decomposition survive P8's FAIL verdict as exact "
               "results.",
     source=f"{P8}/INDEPENDENT_ADJUDICATION.md", section="§16 surviving-evidence tiers",
     scope="as stated in P8 §16", hypotheses="NONE_BEYOND_MODEL",
     limitation="Surviving evidence inside a FAILED priority. Usable only at its "
                "adjudicated tier and scope, and cited as P8, never as CLOSED.",
     edges=[dict(parent="P8-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8-T1", kind="CLAIM", priority="P8", claim_class="CONDITIONAL_THEOREM",
     statement="P8-T1 survives conditionally on its stated analytic hypotheses.",
     source=f"{P8}/INDEPENDENT_ADJUDICATION.md", section="§16",
     scope="as stated", hypotheses="STATED_NOT_DISCHARGED",
     limitation="Must never be used as unconditional.",
     edges=[dict(parent="P8-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8-F1", kind="CLAIM", priority="P8", claim_class="NEGATIVE_RESULT",
     statement="The cross-family window law and its sub-gates are rejected, "
               "literal G7 fails, detector transfer is measured absent, and the "
               "G14 temporal-integrity gate fails. No P8 certified numerical "
               "result exists.",
     source=f"{P8}/INDEPENDENT_ADJUDICATION.md", section="§16",
     scope="P8's tested families", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P8-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8R-T1", kind="CLAIM", priority="P8R", claim_class="CONDITIONAL_THEOREM",
     statement="P8R-T1 survives as a conditional theorem.",
     source=f"{P8R}/INDEPENDENT_ADJUDICATION.md", section="verdict block p8r_t1",
     scope="as stated", hypotheses="STATED_NOT_DISCHARGED",
     edges=[dict(parent="P8R-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8R-S15", kind="CLAIM", priority="P8R", claim_class="EMPIRICAL_ONLY",
     statement="The S15 frozen gate is SUPPORTED but statistically fragile; its "
               "adjudicated claim class is empirical-suggestive only "
               "(independent upper 95% bound 1.9425).",
     source=f"{P8R}/results/independent_adjudication.json", section="s15",
     scope="P8R's tested model classes", hypotheses="NOT_APPLICABLE",
     limitation="Fragile. Must not be read as a magnitude law.",
     edges=[dict(parent="P8R-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8R-F1", kind="CLAIM", priority="P8R", claim_class="NEGATIVE_RESULT",
     statement="P8R re-confirms rejection of the window law (S7/S7D/S7F "
               "REJECTED, S12 REJECTED) and measures detector transfer as "
               "absent; novelty is not established.",
     source=f"{P8R}/results/independent_adjudication.json",
     section="scientific_questions; novelty_status",
     scope="P8R's tested model classes", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P8R-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P8R-RECON", kind="CLAIM", priority="P9R",
     claim_class="PARTIAL_PRIORITY_RESULT",
     statement="P8R = CLOSED repairs P8's temporal integrity and closes the "
               "Priority-8 REPAIR lineage. It does NOT convert P8 = FAIL into "
               "CLOSED, does not imply universal model-class transfer, and is "
               "not required by the P9R core theorems, which are P1-P7 derived.",
     source=f"{P8R}/INDEPENDENT_ADJUDICATION.md",
     section="verdict block; p8_original_verdict=FAIL, verdict=CLOSED",
     scope="status reconciliation only", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P8-STATUS", type="STATUS_PROPAGATION"),
            dict(parent="P8R-STATUS", type="STATUS_PROPAGATION"),
            dict(parent="P8R-F1", type="NEGATIVE_RESULT_CONSTRAINT")]),
]

NODES += [
# ------------------------------------------------------------------ P9 original
dict(id="P9-ORIG-RESULT", kind="CLAIM", priority="P9",
     claim_class="PARTIAL_PRIORITY_RESULT",
     statement="P9's retrospective synthesis, its P8 quarantine (PASS), the "
               "exact rho=0 kernel and invariant law, the stationary mixture "
               "identity and the reproduced P7 CUSUM phenomena survive at "
               "PARTIAL strength.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="verdict block; §15",
     scope="P9 as submitted", hypotheses="NOT_APPLICABLE",
     limitation="P9 is temporally RETROSPECTIVE_SYNTHESIS / POST_HOC_PROTOCOL / "
                "TEMPORAL_INTEGRITY_PARTIAL; its 14 gates are not preregistered "
                "closure evidence.",
     edges=[dict(parent="P9-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P9-T2-SUBMITTED", kind="CLAIM", priority="P9",
     claim_class="NOT_ESTABLISHED",
     statement="P9-T2's strict stationary ARL deficit E[A(e)] < A(0), as "
               "submitted at EXACT_THEOREM class, is NOT established: it "
               "imported global monotonicity of A as if authoritative P7 had "
               "proved it.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md",
     section="§5 'The failed exact step'; P9_T2 = CONDITIONAL_ONLY_AS_SUBMITTED",
     scope="P9's submitted theorem", hypotheses="NOT_APPLICABLE",
     limitation="Repaired by the P9R-T2a / P9R-T2b split. The identity content "
                "was never in doubt; only the strict inequality's class was.",
     edges=[dict(parent="P7-A-MONO", type="LOGICAL_PREMISE"),
            dict(parent="P9-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P9-SR-DEFECT", kind="CLAIM", priority="P9", claim_class="NEGATIVE_RESULT",
     statement="P9's SR replay is not the frozen no-headstart recurrence: it "
               "evaluates logaddexp(0, state) BEFORE adding the increment, so "
               "the first update of every cycle is shifted upward by exactly "
               "log 2, and the shift recurs after every reset.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§11",
     scope="P9's SR-specific reproduction values", hypotheses="NOT_APPLICABLE",
     limitation="P9's SR reproduction numbers must be discounted. P9's CUSUM "
                "values are unaffected.",
     edges=[dict(parent="DEF-SR", type="SCOPE_RESTRICTION"),
            dict(parent="P9-STATUS", type="STATUS_PROPAGATION")]),
dict(id="P9-A5A6-PROV", kind="CLAIM", priority="P9",
     claim_class="PROVENANCE_LIMITATION",
     statement="P9's results/burnin_sensitivity.json and "
               "results/p9t2_mixture_check.json are emitted by neither supplied "
               "experiment program and are not covered by P9's focused suite; "
               "the A6 quadrature error is unquantified.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§11",
     scope="P9's A5/A6 artifacts", hypotheses="NOT_APPLICABLE",
     edges=[dict(parent="P9-STATUS", type="STATUS_PROPAGATION")]),

# ------------------------------------------------------------------ P9R
dict(id="P9R-L1", kind="CLAIM", priority="P9R", claim_class="EXACT_THEOREM",
     statement="Evenness: A(e) = A(-e) exactly, for both frozen detectors.",
     source=f"{P9RNS}/THEORY.md", section="Lemma L1",
     scope="both frozen detectors", hypotheses="NONE_BEYOND_MODEL",
     limitation="Symmetry of the two-chart detector under (S+,S-,Z) -> "
                "(S-,S+,-Z) together with X ~ -X. Says nothing about "
                "monotonicity.",
     edges=[dict(parent="DEF-CUSUM", type="LOGICAL_PREMISE"),
            dict(parent="DEF-SR", type="LOGICAL_PREMISE"),
            dict(parent="DEF-A", type="LOGICAL_PREMISE")]),
dict(id="P9R-L2", kind="CLAIM", priority="P9R", claim_class="EXACT_THEOREM",
     statement="Uniform boundedness: sup_{e in R} A(e) <= C_D < infinity, with "
               "C_CUSUM = 10 / Phi(-1)^10 and C_SR = 1 / Phi(-(log A + 1/2)). "
               "Hence A is integrable under every probability law on e, and the "
               "quadrature truncation error is bounded by C_D * P(|e| > L).",
     source=f"{P9RNS}/THEORY.md", section="Lemma L2",
     scope="both frozen detectors, all e", hypotheses="NONE_BEYOND_MODEL",
     limitation="The constant is loose; it is a finiteness and truncation-bound "
                "tool, not an operational bound.",
     edges=[dict(parent="DEF-CUSUM", type="LOGICAL_PREMISE"),
            dict(parent="DEF-SR", type="LOGICAL_PREMISE"),
            dict(parent="P5-T7", type="CONSISTENCY_CHECK")]),
dict(id="P9R-L3", kind="CLAIM", priority="P9R", claim_class="EXACT_THEOREM",
     statement="A(0) > 1 for both frozen detectors: an alarm at t=1 from a "
               "perfect reference requires |Z_1| >= h+k = 5.5 (CUSUM) or "
               "|Z_1| >= log A + 1/2 (SR), each of probability strictly less "
               "than 1.",
     source=f"{P9RNS}/THEORY.md", section="Lemma L3",
     scope="both frozen detectors", hypotheses="NONE_BEYOND_MODEL",
     edges=[dict(parent="DEF-CUSUM", type="LOGICAL_PREMISE"),
            dict(parent="DEF-SR", type="LOGICAL_PREMISE")]),
dict(id="P9R-L4", kind="CLAIM", priority="P9R", claim_class="EXACT_THEOREM",
     statement="A(e) -> 1 as e -> +infinity (and, by L1, as e -> -infinity). "
               "Consequently there exists e* with A(e) < A(0) for all e >= e*, "
               "a set of strictly positive N(0,1/m) measure, for every m >= 1.",
     source=f"{P9RNS}/THEORY.md", section="Lemma L4",
     scope="both frozen detectors", hypotheses="NONE_BEYOND_MODEL",
     limitation="This is what makes STRICTNESS free in P9R-T2b. It is NOT "
                "monotonicity and does not imply ASM-DOM.",
     edges=[dict(parent="DEF-CUSUM", type="LOGICAL_PREMISE"),
            dict(parent="DEF-SR", type="LOGICAL_PREMISE"),
            dict(parent="P9R-L1", type="LOGICAL_PREMISE"),
            dict(parent="P9R-L3", type="LOGICAL_PREMISE")]),
dict(id="P9R-T2a", kind="CLAIM", priority="P9R", claim_class="EXACT_THEOREM",
     statement="For either frozen Gaussian detector, convention A, fixed m >= 1 "
               "and rho = 0: (i) e_{j+1} ~ N(0,1/m) independently of the current "
               "state, so N(0,1/m) is the unique invariant law; (ii) the "
               "stationary in-control ARL is exactly E_{e~N(0,1/m)}[A(e)], which "
               "is finite by L2; (iii) the first-order local multiplier "
               "rho(1-Gamma) is exactly zero.",
     source=f"{P9RNS}/THEORY.md", section="Theorem P9R-T2a",
     scope="both frozen detectors, all m>=1, rho=0 exactly",
     hypotheses="NONE_BEYOND_MODEL",
     limitation="Contains NO inequality and NO operational conclusion. "
                "'Maximally locally stable' is defensible only in the "
                "first-order multiplier sense.",
     edges=[dict(parent="P5-T1", type="LOGICAL_PREMISE"),
            dict(parent="P5-T7", type="LOGICAL_PREMISE"),
            dict(parent="P7-A-ID", type="LOGICAL_PREMISE"),
            dict(parent="P9R-L2", type="LOGICAL_PREMISE"),
            dict(parent="P3-T1", type="LOGICAL_PREMISE"),
            dict(parent="DEF-CONV-A", type="SCOPE_RESTRICTION")]),
dict(id="P9R-T2b", kind="CLAIM", priority="P9R", claim_class="CONDITIONAL_THEOREM",
     statement="Conditional strict deficit: IF A(e) <= A(0) for N(0,1/m)-almost "
               "every e (ASM-DOM), THEN E_{e~N(0,1/m)}[A(e)] < A(0) strictly. "
               "The strict-inequality half needs no further assumption: L3 and "
               "L4 already give A(e) < A(0) on a set of positive measure.",
     source=f"{P9RNS}/THEORY.md", section="Theorem P9R-T2b",
     scope="both frozen detectors, all m>=1, rho=0", 
     hypotheses="STATED_NOT_DISCHARGED",
     limitation="ASM-DOM is NOT established. P9R does not claim this "
                "inequality as exact. Global monotonicity would suffice for "
                "ASM-DOM but is strictly stronger than needed.",
     edges=[dict(parent="P9R-T2a", type="LOGICAL_PREMISE"),
            dict(parent="P9R-L3", type="LOGICAL_PREMISE"),
            dict(parent="P9R-L4", type="LOGICAL_PREMISE"),
            dict(parent="ASM-DOM", type="ASSUMPTION")]),
dict(id="P9R-T3", kind="CLAIM", priority="P9R", claim_class="NEGATIVE_RESULT",
     statement="rho < rho_c does not, in the frozen tested models, guarantee "
               "preservation of the nominal in-control ARL: at rho = 0, which "
               "lies strictly below rho_c for every supported (detector, m) and "
               "at which the local multiplier is exactly zero, the entering "
               "reference is still an estimate and the stationary ARL is the "
               "mixture E[A(e)], measured far below A(0) in every tested cell.",
     source=f"{P9RNS}/THEORY.md", section="§4 operational corollary",
     scope="the two frozen Gaussian detectors, m in {1,2,3,5}, P7's frozen "
           "criterion", hypotheses="NOT_APPLICABLE",
     limitation="It does NOT say that no conceivable rho-based operational "
                "boundary can ever exist, and says nothing about other "
                "detectors, tolerances, metrics or model classes.",
     edges=[dict(parent="P9R-T2a", type="LOGICAL_PREMISE"),
            dict(parent="P7-R1", type="NEGATIVE_RESULT_CONSTRAINT"),
            dict(parent="P9R-E1", type="EMPIRICAL_SUPPORT"),
            dict(parent="P3-T1", type="SCOPE_RESTRICTION")]),
dict(id="P9R-E1", kind="CLAIM", priority="P9R", claim_class="EMPIRICAL_REPRODUCED",
     statement="Corrected independent reproduction of the sixteen authoritative "
               "P7 rho in {0,1} cells under P7's own estimator convention, with "
               "the repaired no-headstart SR recurrence; CUSUM and SR reported "
               "separately and judged by the combined-SE z statistic.",
     source=f"{P9RNS}/results/reproduction.json",
     section="rows; per_detector_summary",
     scope="two detectors, m in {1,2,3,5}, rho in {0,1}",
     hypotheses="NOT_APPLICABLE",
     limitation="Monte Carlo consistency, never exact agreement.",
     edges=[dict(parent="P7-E1", type="REPRODUCTION"),
            dict(parent="P7-E2", type="REPRODUCTION"),
            dict(parent="P9-SR-DEFECT", type="NEGATIVE_RESULT_CONSTRAINT"),
            dict(parent="DEF-SR", type="SCOPE_RESTRICTION")]),
dict(id="P9R-E2", kind="CLAIM", priority="P9R", claim_class="EMPIRICAL_REPRODUCED",
     statement="Burn-in sensitivity under full reuse: the approach to the "
               "stationary regime is slow and non-monotone, so finite-horizon "
               "operational ARL estimates depend materially on the burn-in "
               "convention. Regenerated with a supplied deterministic generator.",
     source=f"{P9RNS}/results/burnin_sensitivity.json", section="rows; conventions",
     scope="two detectors, m in {1,5}, rho=1", hypotheses="NOT_APPLICABLE",
     limitation="Measured, not proved. P5-T7 proves uniform geometric "
                "ergodicity but its constants are loose, so the RATE is empirical.",
     edges=[dict(parent="P5-T7", type="EMPIRICAL_SUPPORT"),
            dict(parent="P9-A5A6-PROV", type="PROVENANCE")]),
dict(id="P9R-E3", kind="CLAIM", priority="P9R", claim_class="EMPIRICAL_ONLY",
     statement="Response-grid evidence: A measured on a uniform grid with a "
               "three-part error budget; the mixture E[A(e)] agrees with the "
               "independently simulated rho=0 chain ARL; no increase of A in "
               "|e| is detected at three combined standard errors, at the "
               "reported grid resolution and power.",
     source=f"{P9RNS}/results/response_grid.json",
     section="detectors.*.mixtures; detectors.*.monotonicity",
     scope="the tested grid and node counts", hypotheses="NOT_APPLICABLE",
     limitation="Grid corroboration of ASM-DOM. It cannot discharge ASM-DOM and "
                "is not a proof. The audit's power is finite and is reported.",
     edges=[dict(parent="ASM-DOM", type="EMPIRICAL_SUPPORT"),
            dict(parent="ASM-MONO", type="EMPIRICAL_SUPPORT"),
            dict(parent="P9R-T2a", type="CONSISTENCY_CHECK"),
            dict(parent="P9-A5A6-PROV", type="PROVENANCE")]),
dict(id="P9R-N1", kind="CLAIM", priority="P9R", claim_class="NOT_ESTABLISHED",
     statement="Novelty of any P9R or upstream result is NOT established. The "
               "earlier finite search of 2445 works with zero DIRECT hits is "
               "prior-art evidence, not proof of novelty. P9R ran no new "
               "literature search.",
     source=f"{P9}/NOVELTY_AUDIT.md",
     section="search summary; P9 adjudication §10",
     scope="the whole campaign", hypotheses="NOT_APPLICABLE",
     edges=[]),
dict(id="GLOBAL-CLOSURE", kind="CLAIM", priority="P9R",
     claim_class="NOT_ESTABLISHED",
     statement="Level-4 global closure is NOT established. D-09 records an "
               "unresolved governance contradiction: the root 'CURRENT LEVEL-4 "
               "CAMPAIGN: CLOSED' line conflicts with mandatory ledger rows "
               "L4R-11 FAIL, L4R-06/L4R-12 PARTIAL, L4R-15 FAIL and L4R-16 OPEN.",
     source=f"{P9}/INDEPENDENT_ADJUDICATION.md", section="§7 D-09",
     scope="the Level-4 campaign", hypotheses="NOT_APPLICABLE",
     limitation="Closure-threatening for global closure; not theorem-threatening "
                "and not a P9R closure prerequisite.",
     edges=[dict(parent="P4-STATUS", type="STATUS_PROPAGATION"),
            dict(parent="P5-STATUS", type="STATUS_PROPAGATION"),
            dict(parent="P8-STATUS", type="STATUS_PROPAGATION"),
            dict(parent="P9-STATUS", type="STATUS_PROPAGATION")]),

# ------------------------------------------------------------------ statuses
dict(id="P1-STATUS", kind="STATUS", priority="P1", priority_status="CLOSED",
     statement="P1 = CLOSED.", source="README.md", section="root status table", edges=[]),
dict(id="P2-STATUS", kind="STATUS", priority="P2", priority_status="CLOSED",
     statement="P2 = CLOSED.", source="README.md", section="root status table", edges=[]),
dict(id="P3-STATUS", kind="STATUS", priority="P3", priority_status="CLOSED",
     statement="P3 = CLOSED.", source="README.md", section="root status table", edges=[]),
dict(id="P4-STATUS", kind="STATUS", priority="P4", priority_status="PARTIAL",
     statement="P4 = PARTIAL.", source="README.md", section="root status table", edges=[]),
dict(id="P5-STATUS", kind="STATUS", priority="P5", priority_status="PARTIAL",
     statement="P5 = PARTIAL.", source="README.md", section="root status table", edges=[]),
dict(id="P6-STATUS", kind="STATUS", priority="P6", priority_status="CLOSED",
     statement="P6 = CLOSED at the repository's authoritative status, with the "
               "P6-namespace traceability gap recorded.",
     source="README.md", section="root status table", edges=[]),
dict(id="P7-STATUS", kind="STATUS", priority="P7", priority_status="CLOSED",
     statement="P7 = CLOSED.", source="README.md", section="root status table", edges=[]),
dict(id="P8-STATUS", kind="STATUS", priority="P8", priority_status="FAIL",
     statement="P8 = FAIL. This is unchanged by P8R.",
     source="README.md", section="root status table", edges=[]),
dict(id="P8R-STATUS", kind="STATUS", priority="P8R", priority_status="CLOSED",
     statement="P8R = CLOSED (Priority-8 REPAIR lineage), adjudicated at "
               "dc8516732c2c5672987a6a5a22c1ce023c77f68f.",
     source=f"{P8R}/results/independent_adjudication.json",
     section="verdict; priority8_repair_lineage_closed", edges=[]),
dict(id="P9-STATUS", kind="STATUS", priority="P9", priority_status="PARTIAL",
     statement="P9 = PARTIAL, adjudicated at "
               "a3e3cabc30c4508b866736aeede54db17e5e1fcc.",
     source=f"{P9}/results/independent_adjudication.json",
     section="final_p9_verdict", edges=[]),
]
