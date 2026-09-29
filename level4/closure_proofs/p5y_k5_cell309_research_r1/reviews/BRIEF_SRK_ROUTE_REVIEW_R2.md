# Brief: independent route review R2 of SRK (cell-309 research campaign r1)

You are an **independent reviewer** with no stake in the outcome, and you are not the R1 reviewer. Review R1
(`reviews/REVIEW_SRK_R1.md`) found SRK-0 sound and returned **NOT_READY** with blockers B1–B6 and governance items
G1–G6. Your task has two parts:
* decide whether every R1 blocker is resolved and whether the new evidence qualifies the route;
* classify the route for a formal, closure-only, exactly-once cell-309 campaign.

## Firewall (strict; tightened after R1 G6)

**Allowed reading:**
* `level4/closure_proofs/p5y_k5_cell309_research_r1/` (NS), everything except `ledger/EXPOSURE_LEDGER.jsonl` and
  `ledger/INCIDENT_*`. You need not open those; their content classes are described in the dossier. This includes
  `reviews/REVIEW_SRK_R1.md`.
* `p5y_k5_perron_deflated_resolvent/theorem/{THEOREM_AD.md, OPERATOR_AUDIT.md}`.
* `p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` and `code/tc_rule.py`.
* `p5y_k5_m5_tail_closure/code/tct_rule.py`.
* `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`, **lines 1–11, 13–38 and 40–62 only**. Lines 12 and 39 are excluded:
  line 12 gives the tail drift domain, and line 39 gives atom-constant ranges on cells 305–309.
* `p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/{c1b_kernel.py, c1b_gauss.py, c1b_float.py}`.
* `p5y_k5_tail_overnight_research/streams/D_309/code/{d309_core.py, d309_rso.py}`.

**Forbidden:**
* any other file that may carry numbers for CUSUM m = 5 cells 305–309, including TCT_INPUTS_*, REGISTRY_C*,
  graph/, HISTORICAL_DOMINANCE, SCOPED_NEGATIVE_FAMILIES_309, route audits and other reviews;
* running anything on the real kernel (h = 5, k = 1/2) at drifts in [6/5, 13/5] or its mirror;
* evaluating anything for cells 305–309;
* extrapolating any decoy number toward the band;
* modifying any file other than your review file;
* any git write.

**Allowed running:**
* everything under NS/tests and NS/verify;
* the certifier on decoys that you declare **inside your review file before running them**, restricted to the real
  geometry at e ≤ 33/32 and synthetic h ∈ {3, 4}, k = 1/2.

Redirect the q309 execution ledger to your scratchpad (set `q309_guard.EXEC_LEDGER`), or list your executions in
the review so the coordinator can transcribe them.

## What changed since R1 (the coordinator's claims; verify them, do not trust them)

| R1 item | claimed repair | where |
|---|---|---|
| B1 cell-to-block rule | outward 2⁻¹⁰ dyadic hull Ew, 4 equal check sub-blocks, weight block = Ew for each, Lemma SV″ | THEOREM_SRK §11 (A3); `srk_certify.cell_blocks`, `run_cell` (5f41d8a9) |
| B2 Γ-binding gate | `srk_gate.gate`: rules G1–G6, a mandatory verifier ACCEPT per sha, max over sub-blocks of min over rungs, None → TC-T fallback. The adapter accepts only a GateResult. A taboo gate requires D_lo and divides (E-11) | `impl/srk_gate.py`, `impl/srk_adapter.py`, `tests/test_srk_gate.py` (23 checks), `tests/e2e_cell_family.py` |
| B3 qualification evidence | every declared block (whole kernel) and the A2 cell family re-run from ONE committed code state, under a runner lock. Each file carries `producer.combined` and `git_head_at_start` | `impl/srk_decoy_suite.py`, `evidence/srk_decoys/`, `evidence/srk_decoys_cell/`, config `SRK_DECOY_DECLARATION_A2.json` |
| B4 controls with power | box-envelope sampling control (4 corner mutants); FSM exit rule (M1 12/12, M4 on all applicable, new M5); §8 tests 1/2/8/10 (T1, T2, T8, T10); `certify_W`/`certify_weight` per-call ledgering; `rad_srk` refusal instead of assert; W-record consistency refusal | `tests/test_srk_envelope.py`, `test_srk_fsm_truth.py`, `test_srk_cert_mutants.py`, `test_srk_assembly_twosided.py`, `test_srk_wrec_refusal.py`; THEOREM_SRK §12 (A4) |
| B5 taboo | kernel and producer hash inside the hashed body; D_lo rule (THEOREM_SRK §12). SRK-T is **OUT of package 1** by rule S C5: there is no certified D_lo path on decoys. The taboo decoy family is preparatory evidence only | `impl/srk_certify.certificate_json`, `registry/PHASE3_ROUTE_COMPARISON.md` |
| B6 text | N1–N3, Theorem L, SC-SRK, O3-N, PHASE3 wording | ERRATA E-5, E-8, E-9; marked in place |
| G5, G6 | push authorizations recorded; reviewer executions and exposures transcribed | README.md; ledgers (fae64157) |
| new | pinned implementation constants (A4); verifier final report (all genuine certificates ACCEPT; a "slack" finding: certificates are conservative) | THEOREM_SRK §12; `verify/README_VERIFY.md`, `verify/VERIFY_RESULTS.json` |

## What to review (answer each with PASS / FAIL / NOTE and evidence)

1. **B1 / Lemma SV″ and the §12 D_lo argument.** Re-derive them.
   * Is the hull rule target-free and fixed before any 309-related number?
   * Does `cell_blocks` implement it exactly? Test non-dyadic endpoints yourself.
2. **B2 gate.**
   * Can any path deliver a Γ̄ to the adapter without a verifier ACCEPT for that exact sha256, with a weight block
     narrower than Ew, with a missing sub-block, or with the wrong kernel?
   * Are the gate negatives in `e2e_cell_family.py` run on **real** certificates, and do they fail for the right
     reason?
3. **B3 evidence integrity.**
   * Every declared block of `SRK_DECOY_DECLARATION.json` and every A2 cell sub-block must be present, with nothing
     dropped or added.
   * Every file must have the same `producer.combined`. Check that the producer files at `git_head_at_start` are
     byte-identical to the files that hash to it (git show / sha256).
   * Every certificate must be independently verified (VERIFY_RESULTS.json, matched by sha256).
   * The MC controls (`evidence/SRK_MC_CONTROL.json`, `SRK_CELL_FAMILY_E2E.json`) must pass.
   * Report any failure and its classification.
4. **B4 controls.** Can each control fail? Is each negative caught for the right reason? Are the rules that were
   written after R1 disclosed where they were written with knowledge of counts (E-10)?
5. **B5 / SRK-T.** Is excluding SRK-T under C5 correct and safe?
6. **Soundness spot-checks of changed code only** (R1 established the unchanged parts):
   * `certify_weight`'s W-record checks;
   * `cell_blocks`;
   * `srk_gate` including taboo and `combine`;
   * the adapter source check;
   * the runner lock.
7. **Target independence and temporal integrity since R1.**
   * No band drift in any ledger line after fae64157.
   * Decisions (A3, A4, the SRK-T exclusion, the FSM rule) must be fixed without reference to 309.
   * The quarantine static scan must pass.
   * Is the route-selection application still target-free?
8. **Classification.** Is P309 (rule S: frozen direct clause, SRK-0 whole-kernel order-0 channel min construction,
   and supply S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR))) scientifically ready to be frozen into a formal
   closure-only exactly-once campaign? Separate:
   * remaining science or implementation blockers (these prevent FREEZE_READY);
   * governance decisions the user must take before any formal campaign (G1–G4). State whether these block the
     *route class* or only *authorization*;
   * formal-campaign items: freeze package, Stage-1 driver, grant, seal, qualification. These are expected to be
     outstanding and are not blockers of the route class.

## Verdict (line 2 of your review file)

One of:
* `ROUTE_REVIEW: FREEZE_READY`: no science or implementation blocker remains. Governance and formal-campaign items
  may remain and must be listed.
* `ROUTE_REVIEW: FREEZE_READY_WITH_CONDITIONS`: list C1…. Each condition must be target-free and satisfiable inside
  the freeze package without new science.
* `ROUTE_REVIEW: NOT_READY`: list the blockers B1….

Write your review to `NS/reviews/REVIEW_SRK_R2.md`. Keep numbers for cells 305–309 out of it. If you are exposed to
one anyway, disclose the exposure's class, not its value.
