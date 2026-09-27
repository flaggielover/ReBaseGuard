# K5 remaining-cells prospective route audit: CUSUM m = 5, cells 306–309

**Status: READ-ONLY AUDIT.**

| item | value |
|---|---|
| new Γ evaluations | **0** |
| target-equivalent proxies evaluated | **0** |
| cells adopted | none |
| r5 | authoritative, unchanged |
| r6 | none created |
| K5 | **PARTIAL** |

This document audits the K5 m = 5 tail as it stands after the C12-R2 chain. It inventories the evidence for cells
306–309 and says, per cell, what is proved, what failed and what is unknown. It classifies every route the
repository supports and compares four campaign architectures. It ends with exactly one recommended next action.

The proposed protocol for that action is in `protocol/PROPOSED_RSO_PROTOCOL_DRAFT.md`. It is **DRAFT ONLY — NOT
FROZEN — NOT AUTHORIZED FOR EXECUTION**.

Author context: the session that ran C12 → C12-R2 and the floor-r2 application. An independent fresh-context
review follows, in `review/`.

---

## 0. Starting state (verified before any reading of the science)

The starting state was checked before any scientific evidence was read.

| check | value |
|---|---|
| HEAD | `c5324a78441c23aa985e59e7c878625e31a3fa4c` |
| branch | `p5y-k5-tail-c11rd-d1d2-extension` (local only; never pushed; no remote copy) |
| tree | clean, including ignored files (`git status --porcelain --ignored` empty) |
| C12-R2 chain | `11f91daf → 107a8b36 → e19f4edd → dec92e09 → 276f4d41 → 1173670f → 33b5f183 → 9c2cbf21 → c5324a78` |
| verdicts | EXECUTION_ACCEPTED (1173670f), CELL306_NOT_ADOPTED (9c2cbf21), ADJUDICATION_ACCEPTED (c5324a78) |
| r5 | `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`, blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`, m = 5 open `[[306, 309]]` |
| r6 | none exists, anywhere in the tree |
| K5 | PARTIAL |
| exactly-once refs | `refs/c12r2/cell306-target-consumed → dec92e09` (commit); `refs/c12r2/cell306-pending-result → 0ac46b3d` (blob) |
| forensic objects | probe blob `b83cc6f5` present; trial commit `def4e453` present (both retained, §14) |
| main refs | LOCAL_MAIN_REF `c123b9bb…` and REMOTE_MAIN_REF `1cb45382…` are unsynchronized, and this audit does not touch them |

## 1. Facts treated as fixed

These facts are **not recomputed, reinterpreted or revisited** anywhere in this audit.

* Γ(5, 306; S_I1) < 0 (sealed control value −0.030469257709306738; C2 and the C12-R2 control).
* Γ(5, 306; S_I2) = **+0.005159101140006536** > 0, sealed once (276f4d41, blob `0ac46b3d`).
* **CELL306_NOT_ADOPTED** under floor r2, with ADJUDICATION_ACCEPTED.
  * F1′ fails at (d), a closure disagreement.
  * F2 fails, as C2 §K published: Γ_deg(306) = +0.029163293 at ×1.25, uniform-A margin 1.1277.
* The following do not happen here:
  * floor r2 is not reinterpreted;
  * no new 306 supply is sought;
  * no r6 is created and r5 is not modified.

**Closeness of +0.005159 to zero is not used as a reason for anything in this document.**

## 2. Method and information discipline

* **Sources.** Committed text and JSON only:
  * README, adjudication, review, open-note and erratum files of every K5 tail campaign;
  * the K5 specification;
  * the coverage maps.
* **Inventory.**
  * Three read-only explorers produced the first inventory.
  * Every load-bearing claim used below was then spot-checked in the file and at the line cited (§3 lists the files).
  * Claims that could not be spot-checked are marked *(explorer, not re-verified)*.
* **No new numbers.** No number in this document was computed by this audit. Every number is quoted from a committed
  artifact, with its source.
* **Scaled sweeps are historical target proxies.** The per-cell "×eff to close / to be adoptable" factors (C8) are
  historical target-proxy evaluations, labelled `COUNTERFACTUAL_ONLY` by their producer. They are cited, never
  re-derived.
* **Rule applied throughout:** *if uncertain whether a check leaks target information, treat it as forbidden.*
  * No code of any campaign was run.
  * No TCT input, registry constant or certificate value was read into any computation.
* **Things not touched:**
  * C11R's quarantine was not opened;
  * no original or independent D1/D2 value is written here;
  * no session transcript was read.

**Evidence-type legend** (used in §4):

| code | meaning |
|---|---|
| **TH** | theorem, proved and independently reviewed |
| **CI** | certified interval or bound (Arb/FLINT or exact-rational certificate) |
| **EX** | exact computation on certified inputs, sealed or reproduced |
| **NE** | numerical experiment, diagnostic or counterfactual sweep (not certified) |
| **HE** | heuristic or estimate |
| **GD** | governance decision |
| **FA** | failed attempt |
| **UH** | untested hypothesis |

**Outcome classes** (§4) are kept distinct:

| class | meaning |
|---|---|
| **FAILED** | the repository records an attempt that did not succeed, or a proved impossibility within a stated scope |
| **UNKNOWN** | never attempted, or attempted without a determinate result |
| **NOT APPLICABLE** | the question does not arise for that cell |

## 3. Evidence map

**Column key:**
* **P/PR** — P means frozen or produced before the result it bears on. PR means produced in knowledge of that
  result.
* **Reuse** — whether a successor may rely on the artifact.
* **Sup.** — superseded.
* **Imm.** — immutable, i.e. sealed or adjudicated and not to be edited.
* **Order** — commit date (all 2026-09), then git order.

| # | artifact (path under `level4/closure_proofs/`) | commit | order | cells | scientific claim | governance status | P/PR | reuse | sup. | imm. |
|---|---|---|---|---|---|---|---|---|---|---|
| E01 | `p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` | e5cc5a90 | 09-13 | all | K5 object, and decision rule: unresolved cells ⇒ `K5_INCONCLUSIVE` (:91) | specification | P | yes | no | yes |
| E02 | `p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md` | 6f1d351b | 09-13 | all | K5-B direct clause, sufficient-only | frozen | P | yes | no | yes |
| E03 | `p5y_k5_order3_readiness_audit/README.md` | e8680998 | 09-16 | 305–309 | tail is a chain problem; options include accepting `K5_INCONCLUSIVE` for m = 5 on ≈(1.62, 2] (:112) | audit | P | yes | no | yes |
| E04 | `p5y_k5_remaining_cell_closure/K5_STATUS.md` + `K5_COVERAGE_MAP.json` | a3547b9b / 5a8c194d | 09-19 | m = 5 305–309 | K5 PARTIAL; m = 5 tail design only | status | PR | yes | map superseded by r3–r5 | yes |
| E05 | `p5y_k5_perron_deflated_resolvent/evidence/successor_r1/K5_COVERAGE_MAP_R3.json` | 7cb01e38 | 09-20 | lower front | map r3 | ADOPTED | PR | yes | by r4 | yes |
| E06 | `p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json` | f2ac1eb3 | 09-20 | m = 5 open 305–309 | map r4 (lower front closed) | ADOPTED | PR | yes | by r5 | yes |
| E07 | `p5y_k5_m5_tail_closure/` (Campaign B; `theorem/THEOREM_TCT.md`) | b920c757 / 76c37de1 | 09-20 | 305–309 | **TH TC-T**; 305 closes with Ĝ := 0; 306–309 need 1.071×/1.362×/1.771×/2.253× uniform (Campaign-B clause) | STOPPED by its own frozen stop rule; TC-T adopted downstream | P (stop rule) | TC-T yes; factors historical | factors by C2/C3/C8 | yes |
| E08 | `p5y_k5_tail_operator_registry/` (C1) | 36d8e39b … 5289b6ce | 09-20 | 305–309 | deflation registry: reduction need falls 2.252903 → 2.101597 (6.716 % vs 10 % threshold) | **MARGINAL**, stopped before freeze | P | registry REGISTRY_C1 yes | no | yes |
| E09 | `p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md` | 8aee1fc5 | 09-20 | 307–309 | R-a (307, 1 new real address, ≈0.44 CPU-h); R-b (307–309, 3 addresses, ≈1.3 CPU-h); caps 3/6 CPU-h; blocked by N1, N3, N5 (§4 table) | design, not run | P | yes | no | yes |
| E10 | `p5y_k5_tail_c2_closure/evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json` | 5a94568a | 09-20 | 306–309 | diagnostic perfect-order-3 Γ: −0.2175 / −0.1718 / −0.1267 / −0.0873 *(explorer, not re-verified)* | diagnostic (NE) | PR | as diagnostic only | no | yes |
| E11 | `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` | ae4cbc2c | 09-21 | 305–309 | **PARTIALLY_ADOPTED [305]**; 306 closes (Γ −0.030469258) but margin 1.1277, F2 fails (+0.029163); binding floor r1 (§K); D′ mixed supply gives 306 Γ −0.036198, margin 1.1555 (:497) | adjudicated | PR | yes | floor by r2 | yes |
| E12 | `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md` | a03b3f2e | 09-21 | 305–309 | N1 (order-3 registry forbids real CUSUM), N3, N5, N7 (deterministic direction not exhausted; blocks any R stage), N8, N9, N10 | open notes | PR | yes | N9 closed by E24 | yes |
| E13 | `p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json` | ae4cbc2c | 09-21 | m = 5 open [306, 309] | **map r5, authoritative** | ADOPTED | — | yes | no | yes |
| E14 | `p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md` + `OPEN_NOTES_DISPOSITION_C3.md` | 019ecce0 | 09-22 | 306–309 | knockout A1 = A2 = 0: 308 +0.039568, 309 +0.092812 (still open); 307 closes on 1.112× uniform or 2.203× on (A1, A2); 306 needs a further 7.56 % (from margin 1.1555) | **REJECTED**; nothing enters the record; notes carried | PR | notes yes | factors by C8 | yes |
| E15 | `p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md` | e12a09e8 | 09-22 | 306–309 | 309 excluded within the order-0 atom-constant channel; §7 names **seven unexcluded mechanisms** (incl. #1 residual-specific order-0 bounds, "cost first"); §8 R-stage premise **not available**; 308 path unattempted; 307 "live, cheap, quantified" | **ACCEPTED_WITH_SCOPE_LIMITATION**, EXCLUDED [309] | PR | yes | 309 margin by E17/E18 | yes |
| E16 | `p5y_k5_tail_c5_exhaustion/` (adjudication + `OPEN_NOTES_DISPOSITION_C5.md`) | 69bff424 | 09-22 | 305–309 | **TH C5-T** (transport tightening 1.211–1.295 % of the penalty at 306–309, "closes nothing", adj :72, :135–136; not a blanket replacement at every cell, adj :41); narrows the 309 exclusion margin (C4's scope sentence restated, OND C5 item 1); fragility levers (sup norms 2.056 %, all_four_together 0.608 %, …, per C8 adj :174–178); C5-N3 successor order; gate written post hoc, disclosed (adj :68–75) | **ACCEPTED_WITH_SCOPE_LIMITATION** | PR (gate post hoc) | theorem yes | no | yes |
| E17 | `p5y_k5_tail_c6_evidence_recovery/` | f494416f | 09-22 | 306–309 | K1 candidate polynomials **never serialized**; deterministic function of committed code, replayable (`REPLAYABLE_EXISTING_ADDRESS`); sealed records recovered at **P3**; **no certifying host in scope** | **ACCEPTED_WITH_SCOPE_LIMITATION** (14 conditions) | PR | yes | no | yes |
| E18 | `p5y_k5_tail_c7_e2_lambda309/` | df4ec179 | 09-22 | 309 | **CI** Λ₃₀₉ ≥ 3.586306094 (L3 elementary); clears critical A0 by 9.7933 % | **ACCEPTED_WITH_CONDITIONS** | PR | yes | no | yes |
| E19 | `p5y_k5_tail_c8_operator_feasibility/` (README, `ERRATUM_C8_GATE.md`, `evidence/phase9/C8_ADOPTION.json`, `review/ADJUDICATION_C8.md`) | 63a3f825 | 09-22 | 306–309 | per-cell ×eff to close / to adopt (COUNTERFACTUAL_ONLY); R1/R2 zero leverage; R3 closes 306/307/308, not 309; R4 closes all; R5 voids 309 refutation; rule-1 erratum E1; §7.1 and others unevaluated | **ACCEPTED_WITH_CONDITIONS** (conditions 5–7 not landed, *explorer, not re-verified*) | PR | as diagnostic | no | yes |
| E20 | `p5y_k5_tail_c9_e1_cell307/` (README, `STOP_RECORD_C9.md`, `review/REVIEW_C9_STOP.md`) | ee10db72 / fd3cb2d4 | 09-22 | 307 | α lever: 1.098807×–1.137406× (COUNTERFACTUAL projection from 307's own recorded margins) — closes, **cannot adopt** (1.370009×); toolchain pin python 3.12.3 / numpy 2.5.2 / python-flint 0.9.0 / FLINT 3.6.0 absent; no host authorization | **EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION**; review STOP_PREMATURE (absorbed) | PR | projection only | no | yes |
| E21 | `p5y_k5_tail_c10_governance_provenance/` | ec969db1 | 09-22 | 306 (+ registry) | REGISTRY_C2 pin not broken (governance drift); C2 floor replaceable prospectively via Condition 1 (freeze before recomputing); next purchase = second certifier, not α | adjudicated | PR | yes | no | yes |
| E22 | `p5y_k5_tail_c11_n9_independent_certifier/` | 440bcd91 | 09-23 | 307 (one constant) | second certifier built (exact rational, independent backend); **one** constant for **307** at a single e (scalar drift), within 31 % of the original | **EXECUTION_INVALID**; N9 open | PR | code yes, number no | by E23/E24 | yes |
| E23 | `p5y_k5_tail_c11r_n9_statement_alignment/` | 7375b9cd | 09-25 | 306 | block-uniform I2 on 306; 4/6 agree, D1/D2 not implemented | COMPARISON_ACCEPTED: **AGREEMENT_INSUFFICIENT** | P (frozen chain) | yes | by E24 | yes |
| E24 | `p5y_k5_tail_c11rd_d1d2_extension/` (adjudication `ADJUDICATION_C11RD_N9.md`) | 7d67989d / fb237288 | 09-26 | 306 | I2 six constants for 306; N9 **CLOSED** (trust condition only) | ADJUDICATION_ACCEPTED | P | yes | no | yes |
| E25 | `p5y_k5_tail_floor_r2/` | a15d083b / 3fadb422 | 09-27 | 306 operative; standing floor for m = 5 tail | F1 lapsed with N9; r2 = base + (F1′ or F2); single-implementation chosen supply; 307–309 out of scope | REPLACEMENT_FLOOR_ACCEPTED | P (frozen before any S_I2 evaluation) | yes | no | yes |
| E26 | `p5y_k5_tail_c12_cell306_adoption/` | b9ffc87f … eba56027 | 09-27 | 306 | none (no evaluation) | **QUALIFICATION_REJECTED** (verifier sandbox could evaluate at later states) | P | lessons only | by E28 | yes |
| E27 | `p5y_k5_tail_c12r1_cell306_adoption/` | 5cfe336a … 13e06db0 | 09-27 | 306 | none (no evaluation) | **QUALIFICATION_REJECTED** (unchecked ignored result path) | P | lessons only | by E28 | yes |
| E28 | `p5y_k5_tail_c12r2_cell306_adoption/` | 11f91daf … c5324a78 | 09-27 | 306 | **EX** Γ(5,306;S_I2) = +0.005159101140006536 (sealed once); control Γ(S_I1) reproduces C2 exactly; floor-r2 table NOT_MET | EXECUTION_ACCEPTED; **CELL306_NOT_ADOPTED**; ADJUDICATION_ACCEPTED | P (frozen, one evaluation) | yes | no | yes |
| E29 | forensic objects: blob `b83cc6f5`, commit `def4e453`, refs `refs/c12r2/*` | — | 09-27 | 306 | record of one invocation past the grant check; marker and pending ref | retained | — | forensic | no | yes |

**Negative evidence retained, none discarded:**
* C1 MARGINAL; Campaign-B routes MARGINAL or INFEASIBLE;
* C3 REJECTED;
* C4's statement that its exclusion is one channel at one cell;
* C5's post-hoc gate;
* C6's "no certifying host" finding and "A1 harder than believed";
* C8's rule-1 false premise and its incomplete route enumeration;
* C9's blocked execution;
* C11 EXECUTION_INVALID;
* C11R AGREEMENT_INSUFFICIENT;
* C12 and C12-R1 QUALIFICATION_REJECTED;
* the C12-R2 closure disagreement at 306.

## 4. Cell dossiers

### Cell 306

**PROVED**

| claim | type | source |
|---|---|---|
| Γ(5,306;S_I1) = −0.030469257709306738 < 0 under the C2 clause (scientifically closed under I1's supply) | EX on CI constants | E11 :47; reproduced exactly by the E28 control |
| Γ(5,306;S_I2) = +0.005159101140006536: I2's own supply does **not** certify closure. This is non-certification, not proof of non-closure (E28 adjudication). | EX, sealed once | E28 |
| F2 fails on S_I1: Γ at every constant ×1.25 = +0.029163293; uniform-A margin 1.1277 | EX | E11 :65, :474–478 |
| Under the D′ mixed supply: Γ = −0.036198, margin 1.1555, still < 1.25 | EX (C3 reproduced) | E11 :497; E14 :269, :283 |
| I1 and I2 six constants compared under the frozen N9 rule; N9 CLOSED | GD on EX comparisons | E24 |
| CELL306_NOT_ADOPTED: base TRUE, F1′(a–c) TRUE, (d) FALSE, F2 FALSE | GD | E28 adjudication 9c2cbf21, review c5324a78 |

**FAILED**
* F1′(d): closure disagreement between I1 and I2.
* F2 on S_I1.
* D′ as a route to F2 (C3, REJECTED; C2 adjudicator: "a D′ campaign alone will not discharge this floor").
* The C12 and C12-R1 qualifications. These are process failures, with no evaluation.

**UNKNOWN**
* Whether any sound single-implementation supply reaches uniform-A margin ≥ 1.25.
  * C8's counterfactual figure is 1.067071× under the C5-T clause.
  * It was never attempted: C8 rule 1 barred it, E1 is toolchain-blocked, and C9 targeted 307.
* Which constants drive the I1/I2 closure disagreement. The adjudication records it and does not attribute it.
* Whether 306 is closable under any second-implementation supply at all.

**NOT APPLICABLE**
* A 309-style Λ exclusion. 306 closes under a certified supply, so no exclusion can hold.
* The order-3 R stage for adoption. C2's R-stage design lists 305/306 as needing nothing (E09 §3), and C4 §8 says 306's
  blocker is "the adoption floor, which no order-3 computation addresses".

### Cell 307

**PROVED**

| claim | type | source |
|---|---|---|
| does **not** close under any committed certified supply (C2 D4, D′) | EX | E11 (sealed D_PARTIAL: open {307, 308, 309}); E14; E19 table "closes now: no" |
| with A1 = A2 = 0 it closes at the certified A0: A0 is not its sole blocker | EX (knockout) | E14 OND C3-N4; E15 §6 |
| needs 1.111966× uniform or 2.203053× on (A1, A2), C3 clause | EX (bisection) | E15 §6 (C4 reproduced C3) |
| needs 1.096007× uniform eff to close, 1.370009× to be adoptable under F2 (C5-T clause) | NE, COUNTERFACTUAL_ONLY | E19 `C8_ADOPTION.json` |
| a Λ-based exclusion is impossible within the atom-constant family: certified Λ floor 3.734070 < ceiling 6.262333, and the certified A0 already closes at A1 = A2 = 0 | EX on committed values | E19 adjudication route table |
| perfect order-3 (diagnostic) Γ −0.1718 | NE | E10 *(explorer, not re-verified)* |

**FAILED**
* C1 deflation registry: MARGINAL.
* Campaign-B routes: MARGINAL / INFEASIBLE.
* C11: EXECUTION_INVALID. Its single 307 constant was certified at a single e, not on the block, so it is a failed
  corroboration, not a certification.

**UNKNOWN**
* Whether any certified operator improvement reaches 1.096007×.
  * The α lever is a counterfactual projection at 1.098807×–1.137406×, uncertified (E20).
  * Dyadic rounding and every sub-block must still certify.
* Whether any known lever reaches 1.370009× (F2). No costed lever does.
* The real order-3 ratio s_G/s_H at 307. R-a was never run.
* Two-implementation constants for 307's block. They were never certified.
* The effect of residual-specific order-0 bounds (C4 §7.1) and of assembly tightening (C4 §7.4). Both are
  uncosted.

**NOT APPLICABLE**
* F1′ at present, because no I2 certification exists for 307.

**Note on C9's "BLOCKED".** It is not a scientific FAILED: no certification was executed.

### Cell 308

**PROVED**

| claim | type | source |
|---|---|---|
| does not close under committed supplies | EX | E11, E19 |
| knockout A1 = A2 = 0 still leaves Γ = +0.039568: **infeasible by any improvement of A1, A2 alone** | EX | E14 :350; OND C3-N4 |
| critical A0 4.3752 vs certified 5.2185 (C3 clause); C5-T-clause ceiling 4.442851 vs certified Λ floor 3.512734 | EX | E14 :350; E19 adjudication table |
| needs 1.438423× uniform eff to close, 1.798029× to be adoptable | NE, COUNTERFACTUAL_ONLY | E19 |
| perfect order-3 (diagnostic) Γ −0.1267 | NE | E10 *(explorer, not re-verified)* |

**FAILED**
* C1 and Campaign-B routes (MARGINAL).
* C4's order-0 exclusion route cannot exclude 308 (C4 §8: "cannot be excluded by this route").

**UNKNOWN**
* Where E_a[τ] at 308 lies between the Λ floor 3.512734 and the certified A0.
  * A certified lower bound above the ceiling would refute 308 within the atom-constant family (C3-N4).
  * A certified upper bound below 4.375229, together with ≥ 18.2× on (A1, A2), would close it (C4 §7 item 5).
* Residual-specific order-0 bounds, sup-norm tightening, cover refinement, assembly tightening and the real
  order-3 value: all uncosted or unrun.

**NOT APPLICABLE**
* F1′, because no second implementation exists for 308.

### Cell 309

**PROVED**

| claim | type | source |
|---|---|---|
| does not close under committed supplies | EX | E11, E19 |
| knockout A1 = A2 = 0: Γ = +0.092812 | EX | E14 :351 |
| **MATHEMATICALLY_REFUTED_WITHIN_SCOPE**: within the order-0 atom-constant family at the committed sup norms, Λ₃₀₉ ≥ 3.586306094 exceeds the clause ceiling 3.266416 by 9.79 %; no admissible A0 closes it | CI + EX | E18; E19; E15 EXCLUDED [309] |
| the scope is real: a 19.612136 % cut of the candidate sup norms voids the refutation (vs C7's floor) | NE, COUNTERFACTUAL | E19 README |
| perfect order-3 closes (diagnostic) | NE | E10, E19 |

**FAILED**
* R3/E1 operator certification cannot close 309 at all, within scope: floor above ceiling.
* C1 and Campaign-B routes (MARGINAL).

**UNKNOWN.** Every route outside the refutation's scope:
* real order-3 (R4);
* sup-norm tightening (R5, needs work "derived for the first time", E17);
* cover refinement / smaller ρ (B1, a new K1 address);
* residual-specific order-0 bounds (§7.1, "escapes the floor entirely", E15);
* assembly tightening (§7.4 / C5 fragility levers).

C4 :503 is explicit that the exclusion is **not** a statement that 309 is unclosable.

**NOT APPLICABLE**
* F1′ (no second implementation).
* Any uniform-eff tightening (it is inadmissible below the Λ floor).

## 5. Cell 306 route audit (very high bar)

Labels: LEGITIMATE_PROSPECTIVE_ROUTE, REQUIRES_NEW_THEORY, RESULT_CHASING_RISK, ALREADY_EXHAUSTED, GOVERNANCE_BARRED,
NO_SUPPORTED_ROUTE.

| id | route | classification | reason |
|---|---|---|---|
| 306-a | reinterpret floor r2; e.g. read F1′ as "either implementation" or treat S_I1 closure as sufficient | **GOVERNANCE_BARRED** | Post-result floor change, expressly prohibited. r2 §3 fixes "for EACH of I1 and I2 separately". |
| 306-b | re-evaluate Γ(S_I1), Γ(S_I2) or F2 on the existing supplies | **ALREADY_EXHAUSTED** / GOVERNANCE_BARRED | C12-R2 consumed its target exactly once. C2 published F2, and floor r2 `FLOOR_R2_SPECIFICATION.md` :224 says the rule "does not revisit that". |
| 306-c | tighten or repair I2 so that Γ(S_I2) < 0 | **RESULT_CHASING_RISK** | The gap is known exactly (+0.005159). Any I2 change now is aimed at a known number, and the target marker is consumed. |
| 306-d | a third implementation I3, to pair with I1 under an F1′-like limb | **RESULT_CHASING_RISK** (also GOVERNANCE_BARRED) | It would be supply-shopping after I2 failed to certify, and would need a new limb (r2 defines F1′ over I1 and I2). |
| 306-e | deterministic I1 tightening to margin ≥ 1.25 (F2), i.e. 1.067071× under C5-T (C8) or a further 7.56 % from D′ (C3) | **GOVERNANCE_BARRED** (secondary: RESULT_CHASING_RISK) | See the note below the table. |
| 306-f | order-3 R stage | **NO_SUPPORTED_ROUTE** | The repository assigns 306 no R-stage role (E09 §3), and C4 §8 says order-3 does not address the floor. |
| 306-g | residual-specific order-0 bound (C4 §7.1) applied to 306 | **GOVERNANCE_BARRED** for 306 (it is REQUIRES_NEW_THEORY as mathematics) | Applying any new mechanism to 306 now is a new 306 supply. If the theorem is ever established, a 306 application needs its own authorization and a floor decision frozen before recomputation (C10: C2 Condition 1). |

**Note on 306-e.** The route is historically prospective: C2 :497–498, C3 :294–295 and C8 all name it before C12.
It is nonetheless barred now, for four reasons:
* it is exactly the "new 306 supply" this audit may not seek;
* C8 rule 1 still bars it unless re-frozen (erratum E1);
* E1 is toolchain-blocked (E20);
* after C12-R2 it would be designed in knowledge of an adverse cross-implementation result at 306. An I1-only F2
  adoption would adopt a cell whose second, independent implementation does not certify closure.

**Conclusion for 306: NO_SUPPORTED_ROUTE under current governance.**
* 306 remains **OPEN / NOT ADOPTED**.
* The C12-R2 execution stays scientifically valid.
* +Γ under I2 is non-certification, not disproof.

## 6. Cells 307–309: route feasibility

Compute scale: negligible / minutes / hours / multi-hour / CPU-day / heavy. Scientific risk: LOW / MEDIUM / HIGH /
VERY_HIGH. Result-chasing risk: LOW / MEDIUM / HIGH.

**R-α.** E1 via an α ladder below 6/5 (C9).
* **Cells:** 307 only. For 308 the projected maximum of 1.137406× is below 1.438423×.
* **Mechanism:** the certifier's candidate is `w = dyadic(α·g)`. All ten 307 sub-blocks certified at the first rung,
  6/5, with recorded margin ≈0.16, so a smaller α scales τ (E20).
* **Required evidence:**
  * a certified taboo_certify run at a frozen α on 307's ten sub-blocks;
  * the pinned toolchain;
  * a host authorization.
* **Compute:** minutes. The recorded cost for 307 is 887 CPU-s against a quoted "~31 CPU-min", unresolved.
* **Governance:** HIGH (host authorization plus the full chain).
* **Scientific risk:** MEDIUM. The projected 1.098807× at α = 1.07 against a need of 1.096007× is thin.
* **Result-chasing risk:** **HIGH**.
  * The lever was sized from 307's own recorded margins.
  * The outcome is projected in advance.
  * Under r2 it can at best give SCIENTIFICALLY_CLOSED_NOT_ADOPTABLE (1.137406× < 1.370009×), and F1′ is
    unavailable.
  * C10 already judged the next purchase to be "a second certifier, not alpha".

**R-E1g.** E1 as a general search for a better operator tuple (C8 R3).
* **Cells:** 307, 308.
* **Mechanism:** a tighter certified upper bound on the operator constants. Perfect information closes 307 and 308,
  not 309.
* **Required evidence:** a new certifier search strategy, the toolchain and a host.
* **Compute:** unknown.
* **Governance:** HIGH.
* **Scientific risk:** HIGH. No costed lever beyond α exists.
* **Result-chasing risk:** MEDIUM. The required factors are known.

**R-F1′.** A two-implementation route: I2 extended to 307's block, plus an I1 that closes.
* **Cells:** 307 (then 308).
* **Mechanism:** floor r2 F1′ for a new cell.
* **Required evidence:**
  * I2 six-constant, block-uniform certification for 307. This is engineering, and took C11 → C11R → C11RD for 306.
  * I1 must also close, which it does not today, so R-α or R-E1g is needed as well.
* **Compute:** hours.
* **Governance:** VERY HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** MEDIUM. The I2-alone variant (below) is HIGH.

**R-I2-alone.** Evaluate 307 under S_I2 as the chosen supply (r2 base + F2).
* **Cells:** 307.
* **Mechanism:** another single-implementation supply.
* **Required evidence:** as R-F1′, for I2 only.
* **Compute:** hours.
* **Governance:** HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** **HIGH**. It is supply-shopping on a cell that failed under I1, and there is no evidence
  S_I2 is systematically tighter. At 306 it was the weaker of the two.

**R4.** The real order-3 R stage: R-a on 307, or R-b on 307–309 (E09).
* **Cells:** 307 (R-a); 307–309 (R-b).
* **Mechanism:** replace the `resG` surrogate by a real order-3 enclosure. Perfect order-3 closes all four
  (diagnostic).
* **Required evidence:**
  * N1 bridge, N3 fixtures, N5 identity gates;
  * discharge of N7, which C4 §8 says needs "another deterministic successor";
  * an adoption criterion for an order-3 supply, which is undefined;
  * new real addresses on a certifying host.
* **Compute:** hours (≈0.44 / ≈1.3 CPU-h forecast; caps 3/6 CPU-h).
* **Governance:** VERY HIGH. Guard DENY; N1 open.
* **Scientific risk:** MEDIUM.
* **Result-chasing risk:** LOW. It was preregistered in C2, before C3–C12.

**R5.** Sup-norm tightening via candidate replay (C6 route A1).
* **Cells:** 307–309.
* **Mechanism:** tighten sup{F, D, H}. A 19.612 % cut voids 309's refutation (NE).
* **Required evidence:**
  * identity-gated candidate replay on a toolchain host;
  * a tighter sup routine whose gain must be "derived for the first time"; the delivery-side slack is not quantifiable
    (E17, E19 adj :168–171).
* **Compute:** hours, unmeasured.
* **Governance:** HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** MEDIUM. The required percentages are known.

**B1.** Cover refinement, a smaller ρ (C4 §7 item 3; C5-N3(d)).
* **Cells:** 309 (and others).
* **Mechanism:** a smaller enclosure radius. Halving ρ lifts 309's critical A0 to 7.53 (C4 §6 probe, NE).
* **Required evidence:** new K1 measurement at finer cells, i.e. a new real K1 address, a producer and a host.
* **Compute:** multi-hour to CPU-day, unmeasured.
* **Governance:** VERY HIGH.
* **Scientific risk:** MEDIUM.
* **Result-chasing risk:** LOW to MEDIUM.

**RSO.** Residual-specific order-0 bound (C4 §7.1).
* **Cells:** 307–309.
* **Mechanism:** replace `A0‖φ_H‖` by a pointwise majorant `(Ĝ|φ_H|)(a)/D_e`. It "sits legitimately below
  E_a[τ]·‖φ‖ and escapes the floor entirely" (E15 :255–258).
* **Required evidence:**
  * a **new theorem** (a TC-T variant), independently reviewed;
  * φ_H as a function, which needs identity-gated candidate replay (E17: only suprema are committed).
* **Compute:**
  * theory and fixtures: minutes;
  * replay on a host: unmeasured;
  * evaluation: minutes to hours per cell, unmeasured.
* **Governance:** MEDIUM–HIGH.
* **Scientific risk:** HIGH. It is an unproved mechanism.
* **Result-chasing risk:**
  * **LOW** for the theory stage. It was named by the C4 gate and adjudicator (09-22), and repeated by C5-N3 and the
    C8 adjudication as "uncosted by anyone", all before C12.
  * **MEDIUM** for evaluation. The distances to closure are known, which tempts tuning free parameters; this must be
    frozen cell-independently.

**R-asm.** Assembly / K5-B clause tightening: σ₃, σ₄, env4, the f_G surrogate (C4 §7.4; C5 fragility).
* **Cells:** 307–309.
* **Mechanism:** a demonstrated-effective lever class (C5-T: 1.211–1.295 % of the penalty).
* **Required evidence:** new theorem(s).
* **Compute:** negligible to minutes.
* **Governance:** MEDIUM.
* **Scientific risk:** HIGH. Past gains were ≈1 %.
* **Result-chasing risk:** MEDIUM. C5-T's own gate was post hoc (E16 adj :68–75), and the fragility levers are
  measured at 309.

**X308.** Refute 308 within scope via a certified lower bound on E_a[τ] above the ceiling (C3-N4; C4-N1's R1/R5
lower-bound routes).
* **Cells:** 308.
* **Mechanism:** exclusion only. It has zero closure leverage (C8: raising Λ cannot lower Γ).
* **Required evidence:** a certified Λ₃₀₈ floor above 4.442851 (the current floor is 3.512734).
* **Compute:** minutes to hours.
* **Governance:** MEDIUM.
* **Scientific risk:** HIGH. The current floor is far below the ceiling.
* **Result-chasing risk:** LOW. An exclusion adopts nothing.

**Floor-307.** Any new or lowered floor for 307–309, e.g. F2 at a smaller factor.
* **Cells:** 307–309.
* **Mechanism:** none; this is governance.
* **Required evidence:** —.
* **Compute:** none.
* **Governance:** barred.
* **Scientific risk:** —.
* **Result-chasing risk:** **HIGH**. The α projection (≤ 1.137406× < 1.370009×) is known, so any lowering is fitted
  to it.

**D.** Stop at K5 PARTIAL.
* **Cells:** all.
* **Mechanism:** none.
* **Required evidence:** a final adjudication.
* **Compute:** none.
* **Governance:** LOW.
* **Scientific risk:** none.
* **Result-chasing risk:** none.

**Cross-cutting blocker:**
* Every deterministic route that touches real tail data (R-α, R-E1g, R-F1′, R5, RSO evaluation) needs a
  **certifying host with the pinned toolchain**.
* The repository records that none is in scope (E17, E20).
* The local machine lacks the pin, and a shared Homebrew install was judged a shared-system change (E20).
* AWS SR/PS1 is forbidden, and Vultr is unauthorized.
* This is a governance prerequisite, not a scientific one. No route may assume it.

## 7. Architecture comparison

Criteria as instructed. Architectures are compared as designs, **not** by their chance of producing CLOSED.

**A — Joint:** one campaign, one freeze, all of 307–309.
* **Scientific cleanliness:** medium. The routes differ per cell (309 is out of reach of R3; 307 is not A0-blocked),
  so one route fits badly.
* **Temporal integrity:** OK if frozen before any target.
* **Result-chasing risk:** MEDIUM.
* **Compute:** lowest total.
* **Governance complexity:** one chain.
* **Early stop:** poor. It carries the weakest cell's blockers.
* **Reproducibility:** OK.
* **Publication defensibility:** medium.

**B — Separate:** one campaign per cell.
* **Scientific cleanliness:** high per cell.
* **Temporal integrity:** OK.
* **Result-chasing risk:** **HIGH across campaigns**. Each cell is exposed to route after route, and the multiplicity
  is unbounded.
* **Compute:** medium.
* **Governance complexity:** 3 × chain.
* **Early stop:** per cell only.
* **Reproducibility:** OK.
* **Publication defensibility:** medium. There is a multiplicity objection.

**C — Staged:** a target-free feasibility stage, then pre-target kill gates, then one sealed evaluation per surviving
cell.
* **Scientific cleanliness:** high. The theory and soundness are settled before any tail number exists.
* **Temporal integrity:** **best**. The stage boundary coincides with the load-bearing boundary (§8).
* **Result-chasing risk:** LOW in Stage 0; MEDIUM in Stage 1, mitigated by cell-independent freezing.
* **Compute:** Stage 0 negligible to minutes; Stage 1 hours, unmeasured.
* **Governance complexity:** medium–high, but fallible early.
* **Early stop:** **best**. Every kill gate precedes the target, and the fallback is D.
* **Reproducibility:** high. It uses exact rational arithmetic and fixtures.
* **Publication defensibility:** high. A negative Stage 0 is itself publishable: "the last uncosted mechanism was
  costed".

**D — Stop at K5 PARTIAL.**
* **Scientific cleanliness:** high (no new claims).
* **Temporal integrity:** perfect.
* **Result-chasing risk:** none.
* **Compute:** zero.
* **Governance complexity:** lowest.
* **Early stop:** n/a.
* **Reproducibility:** n/a.
* **Publication defensibility:** high. The K5 spec (E01 :91) pre-specifies `K5_INCONCLUSIVE` for unresolved cells,
  and E03 lists it as an option for this tail.

**D is fairly considered.** Its cost is information, not integrity.
* It would leave uncosted the one mechanism that three independent adjudications (C4, C5, C8) named, before C12, as
  the next thing to cost.
* That mechanism is also the only named one that "escapes the floor entirely", i.e. that can reach 309's refutation
  scope and 308's order-0 problem.
* Its first stage needs no target, no host and no new real address.

C with a D fallback dominates D on information gain at negligible compute and LOW result-chasing risk. It ties D on
temporal integrity, because Stage 0 is target-free.

C dominates A and B on early stopping and multiplicity.

**Chosen: C (staged), with automatic fallback to D on any Stage-0 kill.**

## 8. Information classification and kill gates

### Safe preflight information

This information may be obtained before any target evaluation. It is target-free.

* **S1.** The statement and proof of the RSO lemma, a TC-T variant.
  * It is pure mathematics.
  * It reads no cell data.
* **S2.** Qualification of an exact-rational implementation of the bound.
  * The test cases are **manufactured fixtures** with analytic answers.
  * A second independent implementation must agree exactly on those fixtures.
  * Mutation tests are required.
* **S3.** Structural applicability.
  * It checks that the committed code paths and schemas can deliver φ_H as a function through identity-gated replay.
  * It inspects code and schemas only: file presence, hashes and signatures. It reads no numeric values of the tail
    cells.
* **S4.** Toolchain and host.
  * The pinned runtime is built on an **authorized** host.
  * Replay identity is checked on cell **305**. It is already adopted, and the identity gate outputs only
    bit-identity pass/fail against committed scalars.
* **S5.** Cost is measured on the S4 replay: wall time and CPU time only.
* **S6.** Governance items are decided and reviewed: G-1, the F2 reading for the new term, and G-2, the clause
  choice (protocol draft §6).

### Load-bearing target information

This information is available only in Stage 1, exactly once per cell, after the grant.

* **L1.** Any evaluation of the RSO bound on a cell in 306–309. For 306 it is forbidden outright.
* **L2.** Any Γ, Γ sign, margin, uniform factor, or closure/non-closure indicator for 307–309, under any supply.
* **L3.** Any quantity from which a 307–309 Γ under the new supply could be inferred. For example:
  * the ratio of the new order-0 term to `A0‖φ_H‖`;
  * any pointwise residual quantity on a tail candidate.
* **L4.** **Calibration on any real cell**, including 305 and the lower front.
  * C2's R-stage design records that such per-cell ratios transfer as estimates between cells (E09 §3).
  * So calibration is a target proxy. Under the "uncertain → forbidden" rule it is forbidden in Stage 0.
* **L5.** Anything computed on replayed 307–309 candidates beyond identity-gating.

### Kill gates

All kill gates are evaluated **before** any L-information exists. **None uses a prediction of success on 307–309.**

| gate | condition to pass | on failure |
|---|---|---|
| KG0 state | HEAD/branch/refs as frozen; r5 blob `f978eeb6…`; no r6; C12-R2 refs unchanged | STOP |
| KG1 theory | the RSO lemma is proved and a fresh independent review returns THEOREM_ACCEPTED | STOP → D |
| KG2 domination | the lemma proves the new term ≤ `A0‖φ_H‖` pointwise, so it cannot loosen any cell (a proof obligation, no numbers) | STOP → D |
| KG3 soundness | fixtures 100 %; the two implementations agree exactly; every non-equivalent mutant killed | STOP (repairable once, then D) |
| KG4 applicability | S3 passes; otherwise DATA_BLOCKED | STOP → D |
| KG5 host | an authorized certifying host with the pinned toolchain exists and 305 replay identity PASSES | STOP (TOOLCHAIN_BLOCKED) → D |
| KG6 cost | 3 × measured per-cell cost ≤ a frozen hard cap (proposed 6 CPU-h, matching C2's hard cap) | STOP → D |
| KG7 governance | G-1 and G-2 frozen and independently reviewed; adoption criterion frozen | STOP |

## 9. Route table

| route | cell(s) | scientific basis | required work | compute | governance | success uncertainty | result-chasing risk | recommendation |
|---|---|---|---|---|---|---|---|---|
| 306-a…g | 306 | §5 | — | — | barred / exhausted | — | HIGH where applicable | **REJECT** (306 stays OPEN) |
| RSO Stage 0 | 307–309 | C4 §7.1 (pre-C12, repeated by C5 and the C8 adjudication) | theorem + fixtures + host qualification | negligible–minutes (+ host build) | MEDIUM | high (unproved) | LOW | **PROCEED** (on authorization to freeze) |
| RSO Stage 1 | 307, 308, 309 | the Stage-0 theorem | one sealed evaluation per cell | hours (unmeasured) | HIGH | high | MEDIUM (mitigated) | **PROCEED_IF_GATE_PASSES** |
| R-asm | 307–309 | C5-T precedent; C4 §7.4 | new theorem(s) | negligible–minutes | MEDIUM | high | MEDIUM | **DEFER** (candidate for a later Stage 0) |
| X308 | 308 | C3-N4, C4-N1 | certified Λ₃₀₈ floor | minutes–hours | MEDIUM | high | LOW | **DEFER** (exclusion only) |
| R4 R-a / R-b | 307 / 307–309 | E09 | N1, N3, N5, N7 + host + order-3 adoption rule | hours | VERY HIGH | medium | LOW | **DEFER** (governance-barred: guard DENY, N7) |
| R-E1g | 307, 308 | C8 R3 | new certifier search + host | unknown | HIGH | high | MEDIUM | **INSUFFICIENT_EVIDENCE** |
| R5 | 307–309 | C6 A1, C8 R5 | replay + tighter sup routine + host | hours | HIGH | high (slack unquantifiable) | MEDIUM | **INSUFFICIENT_EVIDENCE** |
| B1 | 309 | C4 §7.3 | new K1 addresses | multi-hour–CPU-day | VERY HIGH | medium | LOW–MEDIUM | **DEFER** |
| R-F1′ | 307 | floor r2 | I2 on 307 + I1 closing | hours | VERY HIGH | high | MEDIUM | **DEFER** |
| R-α | 307 | C9 projection | host + toolchain + chain | minutes | HIGH | medium | HIGH | **REJECT** as the next action (cannot adopt; lever sized on target margins) |
| R-I2-alone | 307 | none beyond r2 form | I2 on 307 | hours | HIGH | high | HIGH | **REJECT** |
| Floor-307 | 307–309 | none | — | — | barred | — | HIGH | **REJECT** |
| D stop | all | E01 :91 | final adjudication | none | LOW | none | none | **DEFER** (automatic on any Stage-0 kill) |

No percentages of success are given, because none is supported by committed evidence.

## 10. Recommendation: exactly one next action

> **Authorize the freeze of Stage 0 of the proposed staged campaign "RSO" for cells 307–309.**
>
> * Stage 0 contains only the target-free theory, fixture qualification, applicability, host and cost gates: KG0–KG7.
> * Stage 0 evaluates nothing on any tail cell.
> * Stage 1 (one sealed evaluation per cell, in the frozen order 307 → 308 → 309) needs a **separate**
>   authorization after all of KG0–KG7 pass.
>   * That authorization includes an explicit host authorization.
>   * The draft does not presume it.
> * Any kill leads to the final K5 PARTIAL adjudication.

**Why this, measured on the instructed criteria:**
* **Defensibility.** The mechanism was motivated before C12 by three adjudications, and was never costed.
* **Information gain.** It resolves the programme's longest-carried UNKNOWN, in either direction.
* **Temporal integrity.** Stage 0 has no target.
* **Reproducibility.** Exact arithmetic and fixtures.
* **Compute.** Negligible until the host gate.
* **Governance simplicity.** One freeze with early exits.

**What this does not do:**
* It is not chosen for its chance of CLOSED, which is unknown and not estimated.
* It does not touch 306.
* It does not create r6.
* It does not presume any floor change.

## 11. Protocol draft

`protocol/PROPOSED_RSO_PROTOCOL_DRAFT.md` — **DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION**. No campaign
number is assigned, no namespace for it is created and no code exists.

## 12. Computation declaration

| quantity | count |
|---|---|
| new Γ evaluations, cell 306 | **0** |
| new Γ evaluations, cell 307 | **0** |
| new Γ evaluations, cell 308 | **0** |
| new Γ evaluations, cell 309 | **0** |
| target-equivalent proxies evaluated (margins, factors, bisections, Λ bounds, knockouts, replays, calibrations) | **0** |
| scientific code executed | **0** (no campaign code, producer, certifier or verifier was run) |
| new real addresses, AWS or Vultr contacts | **0** |

Every number in this document is quoted from a committed artifact.

## 13. Coverage preservation

* r5 (`f978eeb6…`) is authoritative and unchanged.
* No r6 exists.
* Maps r3 and r4 are unchanged.
* The m = 5 open set is 306–309.
* K5 is **PARTIAL**.
* Cell 306 is NOT ADOPTED and OPEN.
* Cells 307–309 are OPEN, and 309 is also refuted within scope.

## 14. Forensics and unrelated refs

**Retained, unmodified:**
* the probe blob `b83cc6f5`;
* the trial commit `def4e453`;
* `refs/c12r2/cell306-target-consumed` (dec92e09);
* `refs/c12r2/cell306-pending-result` (`0ac46b3d`);
* the C12-R2 seal 276f4d41;
* all C12/C12-R1/C12-R2 reviews.

**Unrelated ref movement.** The earlier movement of `p5y-k4*` refs is **unrelated** to K5 and to this audit:
`p5y-k4-frozen-execution-r1 bc4ba08e` and `p5y-k4r1-nearzero-successor 5d33363c` at audit time. It is recorded, not
touched.

## 15. Limitations of this audit

* Rows marked *(explorer, not re-verified)* rest on a read-only explorer's report:
  * the E10 diagnostic order-3 values;
  * the landing state of the C8 conditions 5–7.
* All other load-bearing lines were opened at the cited location.
* The RSO mechanism is a named, unproved hypothesis. This audit does not claim it is true, only that it is the
  best-motivated uncosted route and that its first stage is target-free.
* Architecture ratings are qualitative judgements. They are argued from the cited evidence, not measured.
