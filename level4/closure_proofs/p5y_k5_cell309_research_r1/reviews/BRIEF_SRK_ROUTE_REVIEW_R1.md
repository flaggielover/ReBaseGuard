# Brief: independent route review R1 of SRK (cell-309 research campaign r1)

You are an **independent reviewer**, with no stake in the outcome. Your task is to decide whether the SRK route is
sound, correctly implemented, target-independent, and ready to be frozen (route level, closure-only). The alternative
is to name the blockers.

## Firewall (strict)

* **Allowed reading:**
  * `level4/closure_proofs/p5y_k5_cell309_research_r1/` (NS), everything except `ledger/EXPOSURE_LEDGER.jsonl` and
    `ledger/INCIDENT_*`, whose content classes you may read but which you need not open;
  * `p5y_k5_perron_deflated_resolvent/theorem/{THEOREM_AD.md, OPERATOR_AUDIT.md}`;
  * `p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` and `code/tc_rule.py`;
  * `p5y_k5_m5_tail_closure/code/tct_rule.py`;
  * `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`, **lines 1–62 only**;
  * `p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/{c1b_kernel.py, c1b_gauss.py, c1b_float.py}`, for the port
    comparison;
  * `p5y_k5_tail_overnight_research/streams/D_309/code/{d309_core.py, d309_rso.py}`, used by an FSM test.
* **Forbidden:**
  * any other file that may carry numbers for CUSUM m = 5 cells 305–309, including TCT_INPUTS_*, REGISTRY_C*,
    graph/, HISTORICAL_DOMINANCE, other reviews, SCOPED_NEGATIVE_FAMILIES_309 and route-audit files;
  * running anything on the real kernel (h = 5, k = 1/2) at drifts in [6/5, 13/5] or its mirror;
  * modifying any file other than your review file;
  * git writes.
* **Allowed running:** the tests under NS/tests, and the certifier on decoys you declare **inside your review before
  running them**, restricted to:
  * the real geometry at e ≤ 33/32;
  * synthetic geometries h ∈ {3, 4}, k = 1/2.

## What to review (answer each with PASS / FAIL / NOTE and evidence)

1. **Theorem.** Re-derive `theory/THEOREM_SRK.md` §§1–3 (Lemmas SK, SV), §9 (Lemma SV′, amendment A1) and §10
   (SV-T). Check in particular:
   * pointwise Taylor in B(X);
   * the pointwise kernel bound, including the atom sub-window;
   * positivity and the invertibility argument, including the W ≥ 0 premise;
   * the e-affine family argument;
   * the coefficient-wise min;
   * the claim that SRK changes only the order-0 channel term and is dominated by TC-T.
2. **Phase-1 statements.** Check `theory/PHASE1_RESULTS.md`: Theorem L (ladder), O3-N / O3-X, SRK-P (profile form). Are
   the proofs correct? Are any claims overstated?
3. **Scope claim.** Is SRK outside the committed knockout families? Use `dossier/CELL309_DOSSIER.md` §C and the C4
   `does_not_cover` quotation there. You may not open C4 itself.
4. **Implementation.**
   * `impl/srk_kernel.py` is a port of C1b: compare it with c1b_kernel and run `tests/test_srk_port_identity.py`.
   * `impl/srk_envelope.py`: rigour of I_i, root brackets, and the box monotonicity.
   * `impl/srk_certify.py`: the e-affine residual G-form, the λ/η repairs, the refinement rule's effect on validity,
     the Γ extraction, the weight-block vs check-block logic, and the guards.
   * `impl/srk_assemble.py`, `impl/srk_adapter.py`: exactness, the min, the reproduction gate.
5. **Tests with power.** Run and assess `tests/test_q309_guard.py`, `test_srk_envelope.py`, `test_srk_fsm_truth.py`,
   `test_srk_assembly_twosided.py`, `test_srk_adapter.py` and `srk_mc_control.py`.
   * Are the controls able to fail?
   * Are any negative controls vacuous? Note that M2 was not applicable at the truth level and is covered by the
     two-sided test.
   * Are mutants caught for the right reason?
6. **Decoy evidence.** Check `config/SRK_DECOY_DECLARATION.json` (committed before the real-geometry runs; verify
   with `git log`), `evidence/srk_decoys/*`, and `verify/VERIFY_RESULTS.json` from the independent verifier, if
   present. Do the certificates verify independently? Are there failures, and why?
7. **Target independence and temporal integrity.**
   * The charter and quarantine precede all science (git order).
   * Incidents 309R1-01/02 are disclosed.
   * No band drift appears in any run or ledger line.
   * The route-selection rule (`registry/ROUTE_SELECTION_RULE.md`) is target-free and precedes any cross-route
     comparison.
   * Parameters (degree ladder, cover, μ, sub-block rule) are fixed without reference to 309.
8. **Readiness.** What exactly is missing before a formal, closure-only, exactly-once 309 campaign could freeze SRK
   (with RLR as a min-composed A1/A2 component, per the selection rule)? Distinguish:
   * blockers that are science or implementation;
   * blockers that are governance (user decisions);
   * items that belong to the formal campaign itself (driver, grant, seal).

## Verdict (line 2 of your review file)

One of:
* `ROUTE_REVIEW: ACCEPTED`
* `ROUTE_REVIEW: ACCEPTED_WITH_CONDITIONS` (list them C1…)
* `ROUTE_REVIEW: NOT_READY` (list the blockers B1…)

Write your review to `NS/reviews/REVIEW_SRK_R1.md`.
