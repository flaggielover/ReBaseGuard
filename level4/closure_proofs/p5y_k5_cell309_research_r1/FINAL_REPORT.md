# K5 cell-309 research campaign r1: final report (research only; prospective; target-quarantined)

**Endpoint: READY_TO_FREEZE_PENDING_OWNER_AUTHORIZATION.** Route P309 package 1 is FREEZE_READY by independent review
R2. The formal-campaign package is prepared but not frozen, not authorized and never executed.

Namespace `level4/closure_proofs/p5y_k5_cell309_research_r1/`. Branch `claude/rebaseguard-k5-cell-309-w0jv8m`. It was
checkpoint-pushed under the user's standing preservation permission; every push is ledgered.

## 1. Authoritative reconstructed 309 state (`dossier/CELL309_DOSSIER.md`)

* **Status.** 309 is **OPEN**: listed OPEN in r5 (blob f978eeb6, INTERVAL_WIDTH / TAIL), with no r6. K5 is PARTIAL
  and P5Y NOT_YET_CLOSED. The accepted scoped wording is "OPEN; refuted within scope only".
* **Consumer.** The K5-B direct clause Γ = g_hi + ρ·x_hi·M, with M from the TC-T enclosure (Lemma G, Ĝ := 0) through
  C2's frozen consumer path.
* **Supply.** The best committed supply is S_I1 = min{Lemma G, C1, C2}.
* **Historical closure attempts, all open or excluded within scope:**
  * Campaign B (T2 order-3 refuted);
  * C1 (MARGINAL);
  * C2 (D_PARTIAL);
  * C3 (knockout: A1 = A2 = 0 still leaves Γ > 0);
  * C4 (EXCLUDED within the uniform-A0 scope, via A0 ≥ Λ = E_a[τ]);
  * C5 (C5-T MARGINAL);
  * C7 (strengthened);
  * C8 (MATHEMATICALLY_REFUTED_WITHIN_SCOPE; escape BLOCKED, not refuted).
* **Scope of the negatives.** Every committed negative holds TC-T's order-0 channel as a *norm-only* bound. C4's
  `does_not_cover` explicitly excludes "residual-specific (non-norm-only) order-0 bounds".
* **Provenance.** The dossier carries no 305–309 numbers. It was reconstructed by firewalled readers, and every read
  is ledgered.

## 2. Complete route matrix (`dossier/ROUTE_MATRIX.md`, 19 routes)

| class | routes |
|---|---|
| REJECTED | R1 constant tightening (F1); R2 A0 tightening (Λ floor); R3 A1/A2 alone (C3 knockout); R14 operator tuples (C3/F1) |
| BLOCKED (data / host) | R5 real order-3 at 309; R6/R12 composite-sup SC (payloads never serialized; U1/U2); R8 cover refinement (new K1 records); R9 sup-norm (payloads); R11/R13 RSO-P (payloads); R19 O3-X (real Ĝ) |
| BLOCKED (liability) | R7 TPT (incident 01 + 309R1-01, HIGH); R18 TPT∘SRK |
| INSUFFICIENT_EVIDENCE | R15 second implementation (trust only; it does not change Γ) |
| RESEARCHABLE | R4 RLR (as a min-composed A1/A2 component); R10 Corollary T (needs U2); R17 SRK-T (no D_lo certifier; OUT of package 1; declared taboo family withdrawn before results, E-15) |
| **FREEZE_READY** | R16 SRK (state-resolved order-0 channel), as P309 package 1 with R4 min-composed |

## 3. New theorems (`theory/`)

* **Theorem SRK** (THEOREM_SRK §§1–3), with:
  * Lemma SK (state-resolved kernel norms k_i(x; e) ≤ κ_i);
  * Lemma SV (a supersolution V ≥ Ψ + K_eV with W ≥ 1 + K_eW gives R_eΨ ≤ V);
  * the B3/B4 coefficient-wise min construction rad^SRK ≤ rad^TCT, which replaces only the order-0 channel term.
* **Amendments:**
  * A1: e-affine families, Lemma SV′;
  * A2: taboo form, Lemma SV-T;
  * A3: drift-block rule (2⁻¹⁰ outward hull, 4 check sub-blocks, weight block = hull; Lemma SV″) and the mandatory
    certificate gate;
  * A4: pinned constants, the SRK-T D_lo rule, §8 test amendments.
* **Phase-1 results** (`theory/PHASE1_RESULTS.md`, Q1–Q10), with corrections marked:
  * Theorem L (ladder, order-0 channel);
  * O3-N (no uniform dominance of a real order-3 remainder);
  * O3-X (the intersection dominates both);
  * SRK-P (profile form);
  * SC-SRK (a sufficient condition for a strict gain).
* **Reviews.** R1 re-derived the SRK-0 mathematics and found it sound (`reviews/REVIEW_SRK_R1.md`). R2 re-derived A3
  and the D_lo argument (PASS).

## 4. Implementations and independent verifiers

* **Producer** (`impl/`, identified by fingerprint 377057be…):
  * `srk_kernel.py`, a geometry-parametrized port of the reviewed C1b kernel (84/84 identical);
  * `srk_float.py`;
  * `srk_envelope.py` (rigorous ∫|He_i|φ with root brackets);
  * `srk_certify.py` (e-affine W and V certificates, exact rational checks over a box cover, λ/η repairs,
    `cell_blocks`/`run_cell`).
* **Consumer side:**
  * `srk_assemble.py`: exact B3/B4 min, with refusals;
  * `srk_gate.py`: the only path from certificates to Γ̄. It is immutable and bound to cell, geometry, kernel,
    admitted shas and verifier identity;
  * `srk_adapter.py`: reproduction gate against the frozen TC-T output, dominance check, binding checks.
* **Independent verifier** (`verify/srk_verify_indep.py`). Written by a separate agent from the spec only, with its own
  kernel closed form, Taylor models, a cover of X × E, rigorous Gaussians and explicit disproofs.
* **Runner** (`impl/srk_decoy_suite.py`). Single-code-state lock: producer files committed and clean, with the
  fingerprint checked per job.

## 5. Controls and mutants (all can fail; results)

| test | result |
|---|---|
| port identity | 84/84 |
| envelope sandwich / point-sampled containment | 240/240; 4/4 wrong-corner mutants caught |
| exact-truth FSM (12 seeds) | genuine 12/12; M1 12/12, M4 6/6 applicable, M5 (centre drift only) 12/12 |
| two-sided assembly | 10/10 textual mutants; dominance refusal live (also under -O) |
| adapter binding | 17 checks × 20 cases (reproduction, tamper, Ĝ ≠ 0, coefficients, raw dict, other cell, geometry, verifier, taboo/min sources, hand-built, float cell, rho mismatch, partial gate) |
| gate | 33 checks (G1–G6, taboo D_lo, combine, immutability, binding) |
| W-record refusal | 7 refusals + positive control |
| certificate battery | T1 consistent quarter-weight REFUTED at an explicit point; T2 taboo-as-whole REFUTED, genuine taboo ACCEPT; T8 MC identity and Γ₀ bounds; T10 byte-identical, JSON round trip, ACCEPT |
| independent verifier on decoys (single code state 2a03e838 / producer 377057be) | 87/87 rerun certificates ACCEPT (107/107 including the preliminary ones). Harness v2 batteries give 1868/1868 reason-specific expectations. 7q is refused for the band on all 41 real-kernel certificates. The verifier self-tests pass 21/21 |
| MC positive control | 55/55 whole-kernel rows (5-se criterion; worst MC excess 2.23 se) plus 8/8 cell-level rows |
| A2 cell family end to end | PASS on both declared cells: in-process verdicts equal the batch verdicts; the gate is bound to cell and verifier; all 5 real-certificate negatives are refused for their own reasons |
| evidence manifest / self-audit | 19/19 declared jobs, complete. Self-audit A1–A10 PASS (max ledgered drift 37/32, including the verifier probes) |

## 6. Incident and exposure ledger (`ledger/`)

* **Incidents.**
  * **309R1-03 (new overnight), liability NONE.** An unsanctioned in-band verifier probe (harness v1, 7h) was refused
    at parse time; nothing was evaluated.
  * **309R1-04 (new overnight), liability LOW.** Phase-4 drafting began in the uncommitted scratchpad at 2026-09-29
    14:11Z, before any FREEZE_READY. It contains no target information. The drafts are preserved verbatim
    (`ledger/INCIDENT_309R1_04_ADDENDUM_DRAFTS.md`).
  * **309R1-01 (TPT shares), liability HIGH.** An over-broad grep exposed tail shares.
  * **309R1-02 (in-band mental estimate), liability MEDIUM-HIGH.** Both are disclosed in the theorem header, dossier,
    route matrix and Phase 3.
  * The overnight incidents 01–03 are inherited and disclosed.
* **Exposures.** 55 exposure rows (firewalled readers A/B/C, the coordinator, reviewer R1). All are historical
  reads. None is a new evaluation.
* **Executions.** Every execution is ledgered (ZERO_TARGET_LEDGER), with every target counter 0. The real kernel was
  used only at out-of-band decoy drifts ≤ 33/32.
* **Integrity.**
  * Checkpoint pushes: all nine checks plus the static quarantine scan, ledgered.
  * Errata E-1..E-18 record every correction; commits are immutable.
  * A container restart interrupted the harness-v2 rerun. The interruption record is 27b50777; the rerun was
    completed from scratch, and no result was inferred from the killed run.

## 7. Rejected and blocked routes, with exact reasons

See item 2. In brief:
* R1/R2/R14 are inside F1 (A0 ≥ Λ_309 floors every norm-only order-0 bound; C4/C7/C8).
* R3 falls to C3 (A1 = A2 = 0 still leaves Γ > 0).
* R5/R6/R8/R9/R11/R12/R13/R19 need candidate payloads, new K1 or order-3 records, or a replay host (U1/U2). None
  exists in this session.
* R7/R18 are liability-blocked (incident 01 + 309R1-01; they need an explicit user decision).
* R10 needs U2.
* R17 is not qualifiable without a D_lo certifier.

## 8. Surviving route(s)

**P309 (rule S, fixed before any cross-route comparison):**
* the frozen K5-B direct clause;
* the TC-T order-0 channel term replaced by the SRK-0 whole-kernel B3/B4 min construction;
* supply S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)), the 307 S_RLR construction.

It is closure-only under floor r2, with exactly one sealed evaluation in a separately authorized formal campaign.
SRK-T is OUT of package 1 (C5).

## 9. Is any route FREEZE_READY?

**Yes: P309 package 1, by independent review R2 (phases A–D).**
* **Phase A:** no science blocker; findings P-1 (gate/consumer binding) and P-2 (T1 power), both repaired.
* **Phase B:** FREEZE_READY_WITH_CONDITIONS, with:
  * C1: the adapter's geometry override;
  * C2: withdrawal of the taboo family;
  * C3: verifier-battery mutants passing for the wrong reason.
* **Phase C:** C1–C3 closed; a new C4 (verifier executions not ledgered).
* **Phase D:** C4 closed; no blocker of any class; **ROUTE_REVIEW: FREEZE_READY**.

The reviewer states that this classifies readiness only. An actual freeze needs owner authorization.

**Independent package review R3** (a fresh reviewer): **PACKAGE_REVIEW: COMPLETE** (`reviews/REVIEW_P309_PACKAGE_R3.md`).
It was reached after three follow-ups, which settled notes N1–N19, F2.1–F2.8, D1–D2 and P1–P5 in candidate rev. 2b.
R3 also states that its verdict authorizes nothing.

## 10. Exact remaining blockers

* **Science, implementation, evidence: none** (R2).
* **Owner decisions** (`protocol_prep/P309_OWNER_DECISIONS.md`):
  * **P0-1 / G2:** authorize the closure-only exactly-once campaign, including in-band Stage-1 over Ew and a grant;
  * **G1:** accept the MEDIUM-HIGH liability;
  * **G3:** confirm RLR as the A1/A2 component;
  * **U2:** rule on it, or confirm it is not triggered;
  * **U3:** CLOSURE_ONLY by default;
  * confirm the cell set {309};
  * acknowledge the incidents (01–03, 309R1-01/02/03/04), E-3, E-17(a) and E-18;
  * decide the Stage-1a failure mapping (exceptions → EXECUTION_INDETERMINATE; the 48 CPU-h start threshold);
  * decide the Stage-1b fallback to S_I1 under G3, rather than RLR307's NOT_CLOSED;
  * accept that efficacy at 309 is unknown by design;
  * optionally, SRK-T;
  * later, inside the campaign: a separate grant decision after QUALIFICATION_ACCEPTED, and any push or merge.
* **Formal-campaign items (FC1–FC6),** inside an authorized campaign:
  * **FC1:** the final pin set;
  * **FC2:** a grant-scoped guard and verifier variant, re-qualified and ledgered; genuine-only in-band verification;
    a band guard on probe construction independent of any lifted list;
  * **FC3:** Stage-1 failure gives Γ̄ = +∞, with no retry;
  * **FC4:** the Stage-2 driver, with in-process verdicts and a static check;
  * **FC5:** the RLR Stage-1 blocks for 309;
  * **FC6:** the exactly-once machinery and its reviews.

## 11. Recommended next formal campaign

If the owner authorizes it: **p5y_k5_cell309_p309_r1**, closure only, one sealed evaluation, run exactly as in
`protocol_prep/` (candidate rev. 2b), in this order:
1. owner decisions;
2. incident-independence review;
3. FC2 grant-scoped variants, with their re-qualification;
4. freeze, committing the protocol, the parameters and the outcome table unchanged;
5. qualification QC01–QC17 (gates Q01–Q17);
6. independent qualification review;
7. the grant, naming Ew and the verifier id;
8. the historical control, then arming the marker, Stage 1a/1b, Stage 2, and recording the result from memory;
9. post-execution checks;
10. execution review;
11. adjudication by the frozen table;
12. adjudication review.

Pass criterion: Γ < 0, exact and strict. Label: CELL309_CLOSED_UNDER_P309, a scientific closure only (no adoption,
no r6, no K5/P5Y status change).

## 12. Statement

NEW Γ309 TARGET EVALUATIONS = 0
NEW Γ308 TARGET EVALUATIONS = 0
r5 unchanged
no r6 created
no adoption performed
no K5/P5Y status changed
