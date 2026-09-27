# K5 remaining-cells prospective route audit, revision r1: CUSUM m = 5, cells 306–309

**Status: READ-ONLY AUDIT, revision r1.**

| item | value |
|---|---|
| new Γ evaluations | **0** |
| target-equivalent proxies evaluated | **0** |
| cells adopted | none |
| r5 | authoritative, unchanged |
| r6 | none created |
| K5 | **PARTIAL** |

## What r1 is

r1 **supersedes `ROUTE_AUDIT.md` (r0, d52cec02)**. The fresh independent review of r0 returned
**ROUTE_AUDIT_REJECTED** (`review/ROUTE_AUDIT_REVIEW.md`, preserved verbatim at 27e259f4) with three blockers:

* **B1.** RSO's adoption rule was mislabelled as "floor r2 verbatim".
* **B2.** The case for C over D rested on false or overstated premises.
* **B3.** C6 Condition 10 / P3 admissibility and the replay trust surface were omitted.

Before absorbing each blocker and note, I re-checked it at its cited source (§R below).

r0 and its RSO draft (`protocol/PROPOSED_RSO_PROTOCOL_DRAFT.md`, 1667ea88) stay in the tree unedited, as history.
Neither is recommended by r1.

**The recommendation changes.** Once the three blockers are corrected, the case for a staged RSO campaign no longer
holds on the instructed criteria (§7). r1 recommends **architecture D**: a final K5 PARTIAL adjudication and
publication closeout for the m = 5 tail. The proposed closeout protocol is
`protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md`, marked **DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION**.

The author context is the same session that wrote r0 and ran C12 → C12-R2. A fresh independent review of r1
follows, in `review/`.

---

## R. Disposition of the r0 review

| finding | verified at | disposition in r1 |
|---|---|---|
| **B1** RSO cannot adopt under r2 | `K5_TAIL_ADOPTION_FLOOR_R2.json`: `chosen_supply_restriction` (Lemma G / Lemma Dv′ r2 atom-constant supplies only); `adoption_quantity` (C2's frozen consumer path `c2_d5_forecast.py` blob 18403dbe, "with the atom constants S substituted and every other input unchanged"); `fail_closed[3]` | **Accepted.** Every route that changes the consumer or its non-constant inputs is **closure-only under r2**: RSO, R-asm, R4, R5, B1. Any adoption path for them is a **floor extension**, to be labelled as such, and needs the user's instruction (C2 Condition 1; r2 §9 :202–203). R-α is held to the same standard (§6). |
| **B2a** exclusivity claim | C4 §6 table (:229–235) and Condition 1 (:522–524); C5 adj Condition 10 (:607–609); `ERRATUM_C8_GATE.md` E3 (:39–44) | **Accepted; claim withdrawn.** RSO is not the only named route outside 309's refutation scope. Six C5 source-supply levers (cheapest `all_four_together`, 0.6076 %), sup-norm tightening, cover refinement and real order-3 all lie outside it. |
| **B2b** "three independent adjudications" | C4 :256–259 (ranks it first); C5 adj Condition 11 (:615–622: order E2, A1, E1, B1; RSO "costed alongside (b)"); C8 adj :174–176, :385 | **Accepted; corrected.** Only C4 ranks RSO first. C5 and C8 cite C4 and are not independent of it. |
| **B2c** "no host" | r0 §8 S4/KG5 vs §10 | **Accepted.** r0's Stage 0 needed a host that r0 deferred to Stage 1. C6 Condition 7 (OND C6 :17; adj :292) makes host provisioning a **separately governed user decision**. |
| **B3a** P3 admissibility | C6 adj §2 (:168–185): all four tail records P3, `admissible_for_NEW_scientific_reuse: false`, standing only via `already_adopted_exception`; OND C6 row 10 (binding); C6-N4 (manifest anomaly); C6-N5 | **Accepted.** Added to E17 and to every dossier. Any route deriving a **new** quantity from the tail K1 records or their regenerated candidates faces Condition 10. |
| **B3b** replay trust surface | `MEASUREMENT_NOTE.md` :33–37: `norms.k/j`, `sup_S0`, `sup.{F,D,H}` gated by "neither gate directly"; 262-field identity gate | **Accepted.** A pointwise φ_H is outside every committed gate. |
| N1 306-f label | C2 adj §K :501–506 (third discharge route: real order-3 "under the R-stage's own separately frozen gate, and only after N1, N5 and N7 are discharged") | **Accepted.** 306-f is now GOVERNANCE_BARRED, and the 306 NOT APPLICABLE entry is removed. |
| N2 308 wording | C4 verdict (:508–512): "operator-level route not excluded", not "cannot be excluded"; Condition 2 (:527–533); Condition 3 (:534–537) | **Accepted.** The 308 dossier is corrected, and X308 is re-rated. |
| N3 outcome classes | — | **Accepted.** 309's uniform-eff entry moves to FAILED (within scope). 307's F1′ becomes UNAVAILABLE (never attempted). |
| N4 committed replay cost | `MEASUREMENT_NOTE.md` :17–29: 1350.2–1359.6 CPU-s per cell (306–309), ≈ 1.87 CPU-h for 305–309; C9 887 CPU-s | **Accepted.** Cited in §6. |
| N5 pin and host record | `MEASUREMENT_NOTE.md` :3–4 (vultr-02 frozen Aux5 venv incl. scipy 1.18.1, 2026-09-20) vs C6-N1 (vultr-02 lacks numpy/scipy/flint by `find_spec`) | **Accepted.** Recorded as an **unreconciled** host-record inconsistency bearing on any host decision. |
| N6 notation and replaced term | `THEOREM_TCT.md` :122–125: `rad_r = A0 p2 + 2 A1 p1 + A2 p0`, `p2 = f_H + ρ f_G + ρ² Env4/2`; Ĝ in TC-T is the order-3 candidate of F | **Accepted.** The C4 §7.1 mechanism replaces (at most) the residual part `A0·f_H` of `A0·p2`. `f_G` and `Env4` are norm-only. The taboo resolvent is written **Ĝ_e** from here on. |
| N7 "32 pin classes" | C12-R2 had 32 pinned inputs | Accepted. It affects only the superseded RSO draft. |
| N8 Stage 0a | — | Considered in §7 (option C0a). |
| N9 307 and RSO | C4 §8 (:288–290): 307's blocker is (A1, A2), not A0 | **Accepted.** Carried in §6. |
| N10 R-asm/RSO asymmetry | ERRATUM C8 E3 | **Accepted.** R-asm's theory stage is rated like RSO's, and `all_four_together` 0.6076 % is cited. |
| N11 omissions | C11RD `C11RD_R1_QUALIFICATION_REVIEW.md` (89330534, first qualification REJECTED); C6 Condition 1 ("the INPUTS only. Never the gain") | **Accepted.** Added to §3. |
| N12 theorem premises | C5 adj :39–42 (C5-T premise `x_lo > 0` fails at cell 0) | **Accepted.** Carried in §6 RSO. |
| N13 minor | — | **Accepted.** The E15 line cite is :256–259. The E10 explorer caveat is lifted, because the reviewer verified the four values. KG2 is a soundness obligation, not a kill gate. |

---

## 0. Starting state

The starting state was verified before any reading of the science. It is unchanged since r0, apart from r0's own three
commits (d52cec02, 1667ea88, 27e259f4).

| check | value |
|---|---|
| HEAD at audit start | `c5324a78441c23aa985e59e7c878625e31a3fa4c` |
| HEAD before r1 | 27e259f4 |
| branch | `p5y-k5-tail-c11rd-d1d2-extension` (local only; never pushed; no remote copy) |
| tree | clean, including ignored files |
| C12-R2 chain | `11f91daf → 107a8b36 → e19f4edd → dec92e09 → 276f4d41 → 1173670f → 33b5f183 → 9c2cbf21 → c5324a78` |
| verdicts | EXECUTION_ACCEPTED (1173670f), CELL306_NOT_ADOPTED (9c2cbf21), ADJUDICATION_ACCEPTED (c5324a78) |
| r5 | `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`, blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`, m = 5 open `[[306, 309]]` |
| r6 | none exists |
| K5 | PARTIAL |
| exactly-once refs | `refs/c12r2/cell306-target-consumed → dec92e09`; `refs/c12r2/cell306-pending-result → 0ac46b3d` |
| forensic objects | blob `b83cc6f5`, commit `def4e453`, both present and retained |
| main refs | LOCAL_MAIN_REF `c123b9bb…` and REMOTE_MAIN_REF `1cb45382…` are unsynchronized, and are not touched |

## 1. Facts treated as fixed

These facts are **not recomputed, reinterpreted or revisited** anywhere in this audit.

* Γ(5, 306; S_I1) < 0 (sealed control value −0.030469257709306738).
* Γ(5, 306; S_I2) = **+0.005159101140006536** > 0, sealed once (276f4d41).
* **CELL306_NOT_ADOPTED**, with ADJUDICATION_ACCEPTED. F1′ fails at (d); F2 fails, as C2 §K published: Γ_deg(306) =
  +0.029163293, uniform-A margin 1.1277.
* **Not done here:** no reinterpretation of floor r2, no new 306 supply, no r6, no change to r5.
* **Closeness of +0.005159 to zero is not used as a reason for anything.**

## 2. Method and information discipline

The method is unchanged from r0.

* **Sources:** committed text and JSON only.
* **Numbers:** every number is quoted from a committed artifact. No number was computed by this audit.
* **Scaled sweeps:** C8's per-cell factors are historical target-proxy evaluations, labelled COUNTERFACTUAL_ONLY by
  their producer. They are cited and never re-derived.
* **Rule:** *if uncertain whether a check leaks target information, it is forbidden.*
* **Things not run or read:**
  * no campaign code;
  * no TCT input, registry constant or certificate value read into any computation;
  * C11R's quarantine not opened;
  * no D1/D2 value;
  * no session transcript.
* **r1's only additional reads:**
  * the string fields of the floor-r2 config JSON (rule text);
  * the committed text lines listed in §R.

**Evidence types:**

| code | meaning |
|---|---|
| TH | theorem, proved and reviewed |
| CI | certified interval or bound |
| EX | exact computation on certified inputs |
| NE | numerical experiment, diagnostic or counterfactual |
| HE | heuristic |
| GD | governance decision |
| FA | failed attempt |
| UH | untested hypothesis |

**Outcome classes:**

| class | meaning |
|---|---|
| FAILED | an attempt that did not succeed, or a proved impossibility within a stated scope |
| UNKNOWN | never attempted, or indeterminate |
| UNAVAILABLE | a limb whose prerequisite evidence does not exist |
| NOT APPLICABLE | the question does not arise |

## 3. Evidence map

**Column key:**
* **P/PR:** P means frozen or produced before the result it bears on; PR means produced in knowledge of that result.
* **Order:** commit date, 2026-09.
* **"imm."** means immutable, i.e. sealed or adjudicated.

Every row is immutable.

| # | artifact (under `level4/closure_proofs/`) | commit | order | cells | scientific claim | governance status | P/PR | reuse | superseded |
|---|---|---|---|---|---|---|---|---|---|
| E01 | `p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` | e5cc5a90 | 09-13 | all | decision rule: unresolved cells ⇒ `K5_INCONCLUSIVE` (:91) | specification | P | yes | no |
| E02 | `p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md` | 6f1d351b | 09-13 | all | K5-B direct clause, sufficient-only | frozen | P | yes | no |
| E03 | `p5y_k5_order3_readiness_audit/README.md` | e8680998 | 09-16 | 305–309 | tail is a chain problem; options include `K5_INCONCLUSIVE` for m = 5 on ≈(1.62, 2] (:111–112) | audit | P | yes | no |
| E04 | `p5y_k5_remaining_cell_closure/K5_STATUS.md`, `K5_COVERAGE_MAP.json` | a3547b9b / 5a8c194d | 09-19 | CUSUM; SR | CUSUM K5 PARTIAL; **SR K5 NOT STARTED** (:52); P5Y final assembly waits on SR K1, SR K5 and CUSUM K5 (:55) | status | PR | yes | map by r3–r5 |
| E05 | `p5y_k5_perron_deflated_resolvent/…/K5_COVERAGE_MAP_R3.json` | 7cb01e38 | 09-20 | lower front | map r3 | ADOPTED | PR | yes | by r4 |
| E06 | `p5y_k5_lower_front_order3/…/K5_COVERAGE_MAP_R4.json` | f2ac1eb3 | 09-20 | m = 5 open 305–309 | map r4 | ADOPTED | PR | yes | by r5 |
| E07 | `p5y_k5_m5_tail_closure/` (Campaign B; `theorem/THEOREM_TCT.md`) | b920c757 / 76c37de1 | 09-20 | 305–309 | **TH TC-T** (`rad_r = A0 p2 + 2A1 p1 + A2 p0`, :122–125); 305 closes with Ĝ := 0; 306–309 need 1.071×/1.362×/1.771×/2.253× uniform (Campaign-B clause) | STOPPED by its own frozen stop rule; TC-T used downstream | P | TC-T yes | factors by C2/C3/C8 |
| E07a | `p5y_k5_m5_tail_closure/evidence/measurement_r1/MEASUREMENT_NOTE.md` | b920c757 | 09-20 | 305–309 | replay of TC-T inputs on vultr-02, frozen Aux5 venv (python 3.12.3, numpy 2.5.2, scipy 1.18.1, python-flint 0.9.0); 262-field identity gate; 1350.2–1359.6 CPU-s per cell, ≈1.87 CPU-h for 305–309; `norms.k/j`, `sup_S0`, `sup.{F,D,H}` gated by "neither gate directly" | measurement ("not a new real scientific evaluation") | P | yes | no |
| E08 | `p5y_k5_tail_operator_registry/` (C1) | 36d8e39b … 5289b6ce | 09-20 | 305–309 | need falls 2.252903 → 2.101597 (6.716 % vs 10 %) | **MARGINAL**, stopped before freeze | P | REGISTRY_C1 yes | no |
| E09 | `p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md` | 8aee1fc5 | 09-20 | 307–309 | R-a (307, 1 new real address, ≈0.44 CPU-h); R-b (307–309, 3 addresses, ≈1.3 CPU-h); caps 3/6 CPU-h; blocked by N1, N3, N5; anchors transfer an *estimate*, not a certificate | design, not run | P | yes | no |
| E10 | `p5y_k5_tail_c2_closure/evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json` | 5a94568a | 09-20 | 306–309 | diagnostic perfect-order-3 Γ −0.2175 / −0.1718 / −0.1267 / −0.0873 | diagnostic (NE) | PR | diagnostic only | no |
| E11 | `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` | ae4cbc2c | 09-21 | 305–309 | **PARTIALLY_ADOPTED [305]**; 306 Γ −0.030469258, margin 1.1277, F2 fails (+0.029163); D′ gives 306 Γ −0.036198, margin 1.1555 (:497); §K lists **three** 306 discharge routes: second certifier, margin ≥ 1.25, real order-3 under its own gate after N1/N5/N7 (:501–506) | adjudicated | PR | yes | floor by r2 |
| E12 | `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md` | a03b3f2e | 09-21 | 305–309 | N1 (order-3 producer may evaluate no real CUSUM cell), N3, N5, N7 (not exhausted; blocks any R stage), N8, N9, N10 (registry build host unrecorded) | open notes | PR | yes | N9 closed by E24 |
| E13 | `p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json` | ae4cbc2c | 09-21 | m = 5 open [306, 309] | **map r5, authoritative** | ADOPTED | — | yes | no |
| E14 | `p5y_k5_tail_c3_closure/…/C3_ADJUDICATION.md`, `OPEN_NOTES_DISPOSITION_C3.md` | 019ecce0 | 09-22 | 306–309 | knockout A1 = A2 = 0: 308 +0.039568, 309 +0.092812; 307 1.112× uniform or 2.203× on (A1, A2); 306 needs a further 7.56 %; C3-N1..N5 | **REJECTED** (notes carried) | PR | notes yes | factors by C8 |
| E15 | `p5y_k5_tail_c4_exhaustion/…/C4_ADJUDICATION.md` | e12a09e8 | 09-22 | 306–309 | 309 excluded in the order-0 atom-constant channel only (Condition 1: "against the frozen measurement inputs and the frozen TC-T / K5-B consumer"); §6: sup norms and ρ dominate 309's critical A0; §7: seven unexcluded mechanisms, #1 residual-specific order-0 ranked "cost first" (:256–259); §8: R-stage premise **not available**; 308 "operator-level route not excluded", MC ~65 SE says no lower-bound route will exclude it (:508–512); Condition 3: at MC Λ₃₀₈ = 4.311, closing 308 needs 18.2× on (A1, A2) | **ACCEPTED_WITH_SCOPE_LIMITATION**, EXCLUDED [309] | PR | yes | 309 margin by E16/E18 |
| E16 | `p5y_k5_tail_c5_exhaustion/` | 69bff424 | 09-22 | 305–309 | **TH C5-T**: 1.211–1.295 % of the penalty, "closes nothing" (adj :72, :135–136); not a blanket replacement (premise `x_lo > 0` fails at cell 0, adj :39–42); Condition 10: three non-R-stage oracles each close every open cell; Condition 11: successor order E2, A1, E1, B1, with RSO "costed alongside (b)"; gate written post hoc, disclosed (adj :68–75) | **ACCEPTED_WITH_SCOPE_LIMITATION** | PR (post-hoc gate) | theorem yes | no |
| E17 | `p5y_k5_tail_c6_evidence_recovery/` | f494416f | 09-22 | 306–309 | candidates never serialized; replayable (**inputs only, "Never the gain"**, Condition 1); all four tail records **P3, `admissible_for_NEW_scientific_reuse: false`**, standing only via `already_adopted_exception` (adj §2); **Condition 10 binding: no P3 object may be adopted as new scientific evidence**; C6-N4 manifest anomaly (third audit hash); C6-N5 (`production_run` / `result_bearing` semantics unknown); C6-N1 no certifying host (local and vultr-02 lack numpy/scipy/flint); Condition 7 host provisioning is a separately governed user decision | **ACCEPTED_WITH_SCOPE_LIMITATION** (14 conditions) | PR | yes | no |
| E18 | `p5y_k5_tail_c7_e2_lambda309/` | df4ec179 | 09-22 | 309 | **CI** Λ₃₀₉ ≥ 3.586306094; 9.7933 % over critical A0 | **ACCEPTED_WITH_CONDITIONS** | PR | yes | no |
| E19 | `p5y_k5_tail_c8_operator_feasibility/` (README, `ERRATUM_C8_GATE.md` E1–E4, `C8_ADOPTION.json`, adjudication) | 63a3f825 | 09-22 | 306–309 | per-cell ×eff to close / to adopt (COUNTERFACTUAL_ONLY); R1/R2 zero leverage; R3 closes 306/307/308, not 309; R4 closes all; R5 voids 309 refutation; **E1**: rule 1 false premise; **E3**: exclusivity claim withdrawn, six C5 levers void 309 exclusion (cheapest 0.6076 %); RSO and others unevaluated | **ACCEPTED_WITH_CONDITIONS** | PR | diagnostic | no |
| E20 | `p5y_k5_tail_c9_e1_cell307/` | ee10db72 / fd3cb2d4 | 09-22 | 307 | α lever 1.098807×–1.137406× (COUNTERFACTUAL, from 307's own recorded margins); closes, cannot adopt (1.370009×); pin python 3.12.3 / numpy 2.5.2 / python-flint 0.9.0 / FLINT 3.6.0 absent; no host authorization; 887 CPU-s vs "~31 CPU-min" unresolved | **EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION**; review STOP_PREMATURE (absorbed) | PR | projection only | no |
| E21 | `p5y_k5_tail_c10_governance_provenance/` | ec969db1 | 09-22 | 306, registry | REGISTRY_C2 pin not broken; floor replaceable prospectively (Condition 1); next purchase = second certifier, not α (:95) | adjudicated | PR | yes | no |
| E22 | `p5y_k5_tail_c11_n9_independent_certifier/` | 440bcd91 | 09-23 | 307 (one constant) | one constant for 307 at a single e, within 31 % | **EXECUTION_INVALID** | PR | code yes | by E23/E24 |
| E23 | `p5y_k5_tail_c11r_n9_statement_alignment/` | 7375b9cd | 09-25 | 306 | 4/6 agree; D1/D2 not implemented | COMPARISON_ACCEPTED: **AGREEMENT_INSUFFICIENT** | P | yes | by E24 |
| E24 | `p5y_k5_tail_c11rd_d1d2_extension/` | 89330534 … fb237288 | 09-26 | 306 | **first qualification QUALIFICATION_REJECTED (89330534)**; repaired successor accepted; N9 **CLOSED** (7d67989d, fb237288) | ADJUDICATION_ACCEPTED | P | yes | no |
| E25 | `p5y_k5_tail_floor_r2/` (spec + `config/K5_TAIL_ADOPTION_FLOOR_R2.json`) | a15d083b / 3fadb422 | 09-27 | 306 operative; **standing floor for m = 5 tail** | F1 lapsed; r2 = base + (F1′ or F2); chosen supply = Lemma G / Lemma Dv′ r2 over **one** implementation's constant set; **adoption quantity bound to C2's consumer path, atom constants substituted, "every other input unchanged"**; `fail_closed[3]`: restriction violated ⇒ base and F2 not satisfied; 307–309 out of its operative scope (§9) | REPLACEMENT_FLOOR_ACCEPTED | P | yes | no |
| E26 | `p5y_k5_tail_c12_cell306_adoption/` | b9ffc87f … eba56027 | 09-27 | 306 | — (no evaluation) | **QUALIFICATION_REJECTED** | P | lessons | by E28 |
| E27 | `p5y_k5_tail_c12r1_cell306_adoption/` | 5cfe336a … 13e06db0 | 09-27 | 306 | — (no evaluation) | **QUALIFICATION_REJECTED** | P | lessons | by E28 |
| E28 | `p5y_k5_tail_c12r2_cell306_adoption/` | 11f91daf … c5324a78 | 09-27 | 306 | **EX** Γ(5,306;S_I2) = +0.005159101140006536, sealed once; control reproduces C2; floor-r2 NOT_MET | EXECUTION_ACCEPTED; **CELL306_NOT_ADOPTED**; ADJUDICATION_ACCEPTED | P | yes | no |
| E29 | forensic: blob `b83cc6f5`, commit `def4e453`, `refs/c12r2/*` | — | 09-27 | 306 | invocation-past-grant record, marker and pending ref | retained | — | forensic | no |
| E30 | this audit, r0 + RSO draft + review (`p5y_k5_tail_route_audit/`) | d52cec02, 1667ea88, 27e259f4 | 09-27 | 306–309 | r0 recommended staged RSO | **ROUTE_AUDIT_REJECTED** | PR | review yes | by r1 |

**Negative evidence retained, none discarded:**
* C1 MARGINAL; Campaign-B routes MARGINAL or INFEASIBLE;
* C3 REJECTED;
* C4's scope limits, including its §6 finding that the order-0 channel is not dominant at 309;
* C5's post-hoc gate;
* C6: no host, "A1 harder than believed", P3 inadmissibility, Condition 10, the manifest anomaly;
* C8 errata E1 and E3;
* C9 blocked;
* C11 EXECUTION_INVALID;
* C11R AGREEMENT_INSUFFICIENT;
* C11RD's first QUALIFICATION_REJECTED;
* C12 and C12-R1 QUALIFICATION_REJECTED;
* the C12-R2 closure disagreement at 306;
* r0's own ROUTE_AUDIT_REJECTED.

## 4. Cell dossiers

**Cross-cutting fact for all four cells.**
* Their K1 records are P3 with `admissible_for_NEW_scientific_reuse: false`.
* The TCT inputs derived from them stand only through the `already_adopted_exception`, which covers the adopted bytes
  (E17).
* C6 Condition 10 therefore binds any route that derives a **new** scientific quantity from those records or from
  candidates regenerated against them.

### Cell 306

**PROVED**

| claim | type | source |
|---|---|---|
| Γ(5,306;S_I1) = −0.030469257709306738 < 0 (C2 clause): closed under I1's supply | EX on CI constants | E11 :47; E28 control |
| Γ(5,306;S_I2) = +0.005159101140006536: not certified under I2 (non-certification, not disproof) | EX, sealed once | E28 |
| F2 on S_I1 fails: +0.029163293 at ×1.25; margin 1.1277 | EX | E11 :65, :474–478 |
| D′ mixed supply: −0.036198, margin 1.1555 < 1.25 | EX | E11 :497; E14 |
| N9 CLOSED (trust condition only) | GD | E24 |
| CELL306_NOT_ADOPTED (base TRUE; F1′(a–c) TRUE, (d) FALSE; F2 FALSE) | GD | E28 |

**FAILED**
* F1′(d): closure disagreement.
* F2 on S_I1.
* D′ as a route to F2.
* The C12 and C12-R1 qualifications (process failures, no evaluation).

**UNKNOWN**
* Whether any sound single-implementation supply reaches margin ≥ 1.25. C8's counterfactual figure is 1.067071×;
  it was never attempted.
* Which constants drive the I1/I2 disagreement. It is not attributed in committed evidence.
* Whether a real order-3 candidate would close 306 under its own gate. It was never run.

**NOT APPLICABLE**
* Λ exclusion, since 306 closes under a certified supply.

### Cell 307

**PROVED**

| claim | type | source |
|---|---|---|
| does not close under any committed certified supply | EX | E11, E14, E19 |
| with A1 = A2 = 0 it closes at the certified A0: **(A1, A2), not A0, is its blocker** | EX | E14 C3-N4; E15 §6, §8 :288–290 |
| needs 1.111966× uniform or 2.203053× on (A1, A2) (C3 clause) | EX | E15 §6 |
| needs 1.096007× uniform eff to close, 1.370009× to be adoptable under F2 (C5-T clause) | NE (COUNTERFACTUAL_ONLY) | E19 |
| Λ exclusion impossible within the atom-constant family (floor 3.734070 < ceiling 6.262333; certified A0 closes at A1 = A2 = 0) | EX on committed values | E19 adjudication |
| perfect order-3 Γ −0.1718 | NE | E10 |

**FAILED**
* C1 (MARGINAL).
* Campaign B (MARGINAL / INFEASIBLE).
* C11's single-e constant: a failed corroboration, not a certification.

**UNKNOWN**
* Whether a certified operator improvement reaches 1.096007×. The α projection of 1.098807×–1.137406× is
  uncertified.
* Whether any lever reaches 1.370009× (none is costed).
* The real order-3 ratio.
* Two-implementation constants.
* RSO and R-asm effects, both uncosted.

**UNAVAILABLE**
* F1′, because no I2 certification exists for 307. r2 would admit it with such evidence (spec :193).

C9's "BLOCKED" is not a scientific FAILED.

### Cell 308

**PROVED**

| claim | type | source |
|---|---|---|
| does not close under committed supplies | EX | E11, E19 |
| knockout A1 = A2 = 0 leaves Γ = +0.039568: no improvement of (A1, A2) alone suffices | EX | E14 :350; C3-N4 |
| critical A0 4.3752 vs certified 5.2185 (C3 clause); C5-T ceiling 4.442851 vs certified Λ floor 3.512734 | EX | E14; E19 adjudication :382 |
| needs 1.438423× uniform eff to close, 1.798029× to be adoptable | NE | E19 |
| perfect order-3 Γ −0.1267 | NE | E10 |

**FAILED**
* C1 and Campaign-B routes (MARGINAL).

**UNKNOWN**
* **Status per C4's verdict: "operator-level route not excluded".**
* Uncertified Monte-Carlo evidence (2,000,000 paths, ~65 SE) says no lower-bound route will exclude 308.
* At the MC value Λ₃₀₈ = 4.311, closing still needs 18.2× on (A1, A2) (C4 Condition 3). No certified upper bound on
  Λ₃₀₈ exists.
* RSO, sup-norm, cover refinement, assembly and real order-3 effects are uncosted or unrun.

C4 Condition 2 forbids quoting "none can" / "cannot be excluded" as establishing anything.

**UNAVAILABLE**
* F1′.

### Cell 309

**PROVED**

| claim | type | source |
|---|---|---|
| does not close under committed supplies | EX | E11, E19 |
| knockout A1 = A2 = 0: Γ = +0.092812 | EX | E14 :351 |
| **REFUTED WITHIN SCOPE**: "for the uniform-A0 atom-constant family, at cell 309, at m = 5, against the frozen measurement inputs and the frozen TC-T / K5-B consumer" (C4 Condition 1), with Λ₃₀₉ ≥ 3.586306094 exceeding the C5-T ceiling 3.266416 by 9.79 % | CI + EX | E15; E18; E19 |
| outside that scope several levers void the refutation: sup-norm cut 19.612136 % (vs C7's floor); six C5 source-supply levers, cheapest `all_four_together` 0.6076 % (vs C4's floor); smaller ρ; real order-3 | NE | E15 §6; E16 Condition 10; E19 README and E3 |

**FAILED (within scope)**
* R3/E1 and any uniform-eff tightening cannot close 309: the Λ floor exceeds the ceiling.
* C1 and Campaign-B routes (MARGINAL).

**UNKNOWN**
* Every route outside the scope: R4, R5, B1, RSO, R-asm.
* C4 :503: the exclusion is **not** a statement that 309 is unclosable.

**UNAVAILABLE**
* F1′.

## 5. Cell 306 route audit (very high bar)

| id | route | classification | reason |
|---|---|---|---|
| 306-a | reinterpret floor r2 | **GOVERNANCE_BARRED** | post-result floor change; expressly prohibited |
| 306-b | re-evaluate Γ(S_I1), Γ(S_I2) or F2 | **ALREADY_EXHAUSTED** / GOVERNANCE_BARRED | C12-R2 consumed its target; r2 spec :224 "does not revisit" C2's F2 |
| 306-c | tighten or repair I2 until Γ(S_I2) < 0 | **RESULT_CHASING_RISK** | aimed at a known gap (+0.005159); consumed marker |
| 306-d | a third implementation paired with I1 | **RESULT_CHASING_RISK** (also GOVERNANCE_BARRED) | supply-shopping after I2 failed to certify; needs a new limb |
| 306-e | deterministic I1 tightening to margin ≥ 1.25 (1.067071× under C5-T; a further 7.56 % from D′) | **GOVERNANCE_BARRED** (secondary: RESULT_CHASING_RISK) | historically prospective (C2 §K, C3, C8), but it is a new 306 supply, C8 rule 1 still bars it (E1), it is toolchain-blocked, and it would now be designed knowing the adverse I1/I2 result at 306 |
| 306-f | real order-3 candidate under its own frozen gate (C2 §K third route) | **GOVERNANCE_BARRED** | guard DENY; N1, N5 and N7 open (E12, E15 §8); a new 306 supply; closure-only under r2 as written (E25) |
| 306-g | RSO or any new mechanism applied to 306 | **GOVERNANCE_BARRED** (as mathematics: REQUIRES_NEW_THEORY) | a new 306 supply; closure-only under r2 |

**Conclusion for 306: NO_SUPPORTED_ROUTE under current governance.** 306 remains **OPEN / NOT ADOPTED**. +Γ under
I2 is non-certification, not disproof.

## 6. Cells 307–309: route feasibility

**r2 adoptability** (E25):
* **r2-conformant** means the route substitutes a new single-implementation atom-constant set into C2's consumer path.
* **Closure-only** means the route changes the consumer or its other inputs, so r2 fails closed on adoption. Any
  adoption would need a labelled floor extension on user instruction.
* **Exclusion-only** means the route can only exclude.

**R-α.** α ladder below 6/5 (C9).
* **Cells:** 307.
* **Mechanism:** `w = dyadic(α·g)`. All ten sub-blocks certified at 6/5 with margin ≈0.16 (E20).
* **Evidence required:** a certified run at a frozen α; the pin; host provisioning (user decision, C6 Condition 7).
* **Compute:** minutes (887 CPU-s recorded for one 307 taboo certification vs "~31 CPU-min", unresolved).
* **Governance:** HIGH.
* **Scientific risk:** MEDIUM (1.098807× vs 1.096007× is thin).
* **Result-chasing risk:** **HIGH**. The lever was sized on 307's own recorded margins, and its outcome is projected in
  advance.
* **r2 adoptability:** r2-conformant, but projected (counterfactual) at most 1.137406× < 1.370009×. It is therefore
  closure-only in expectation.
* **P3 / Condition 10:** it consumes the adopted TCT inputs plus new operator constants, so it is covered by the
  exception as far as committed text shows.

**R-E1g.** A general better operator tuple (C8 R3).
* **Cells:** 307, 308.
* **Mechanism:** a tighter certified upper bound on the constants. Perfect information closes 307 and 308, not 309.
* **Evidence required:** a cell-independent certifier strategy (none identified beyond α); host.
* **Compute:** unknown.
* **Governance:** HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** MEDIUM–HIGH. A search against known required factors is constant optimization.
* **r2 adoptability:** r2-conformant.
* **P3:** as R-α.

**R-F1′.** I2 extended to 307, plus an I1 that closes.
* **Cells:** 307.
* **Mechanism:** r2 F1′.
* **Evidence required:** I2 six-constant, block-uniform certification for 307 (engineering: C11 → C11R → C11RD for
  306), and I1 closing (needs R-α or R-E1g).
* **Compute:** hours.
* **Governance:** VERY HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** HIGH, through its α component.
* **r2 adoptability:** r2-conformant.
* **P3:** as R-α.

**R-I2-alone.** 307 under S_I2.
* **Cells:** 307.
* **Mechanism:** another single-implementation supply.
* **Evidence required:** I2 on 307.
* **Compute:** hours.
* **Governance:** HIGH.
* **Scientific risk:** HIGH.
* **Result-chasing risk:** **HIGH**. It is supply-shopping after I1 failed, and there is no evidence S_I2 is tighter.
* **r2 adoptability:** r2-conformant.
* **P3:** as R-α.

**R4.** Real order-3: R-a on 307, R-b on 307–309 (E09).
* **Cells:** 307–309.
* **Mechanism:** replace the `resG` surrogate by a real order-3 enclosure. Perfect order-3 closes all four
  (diagnostic).
* **Evidence required:** N1, N3, N5 and N7 (C4 §8: "another deterministic successor remains necessary"); new real
  addresses; host.
* **Compute:** hours (≈0.44 / ≈1.3 CPU-h forecast).
* **Governance:** VERY HIGH (guard DENY).
* **Scientific risk:** MEDIUM.
* **Result-chasing risk:** LOW (preregistered in C2).
* **r2 adoptability:** closure-only.
* **P3:** new K1-derived quantities, so Condition 10 applies.

**R5.** Sup-norm tightening via candidate replay (C6 A1).
* **Cells:** 307–309.
* **Mechanism:** tighten `sup{F,D,H}`. C5 calls it the dominant channel at 309, closing 307 and 308 (diagnostic).
* **Evidence required:** replay (inputs only; the gain must be derived for the first time), a sup routine permitting
  a non-identical sup, and host.
* **Compute:** replay ≈1350 CPU-s per cell (E07a) plus the unmeasured tightening.
* **Governance:** HIGH.
* **Scientific risk:** HIGH (slack not quantifiable).
* **Result-chasing risk:** MEDIUM.
* **r2 adoptability:** closure-only (changes inputs).
* **P3:** new candidate-derived quantity, so **Condition 10 applies**; the replay trust surface is ungated (E07a :37).

**B1.** Cover refinement, smaller ρ.
* **Cells:** 309 (and others).
* **Mechanism:** a smaller enclosure radius. The largest lever (C4 §6, C5).
* **Evidence required:** new K1 addresses, producer and host.
* **Compute:** multi-hour to CPU-day, unmeasured.
* **Governance:** VERY HIGH.
* **Scientific risk:** MEDIUM.
* **Result-chasing risk:** LOW–MEDIUM.
* **r2 adoptability:** closure-only.
* **P3:** new records (a new provenance chain needed).

**RSO.** Residual-specific order-0 majorant (C4 §7.1).
* **Cells:** 307–309.
* **Mechanism:** replace, at most, the residual part `A0·f_H` of TC-T's `A0·p2` (`p2 = f_H + ρ f_G + ρ² Env4/2`,
  TC-T :125) by a pointwise majorant `(Ĝ_e|φ_H|)(a)/D_e`. The norm-only `f_G` and `Env4` parts are untouched. C4 §6
  attributes 309's critical A0 mainly to the sup-norm and ρ channels, and C4 §8 says 307's blocker is (A1, A2). The
  mechanism's reach is therefore narrower than r0 stated.
* **Evidence required:**
  * a new theorem, whose premises must be checkable from geometry fields only or else belong to a load-bearing stage
    (cf. C5-T `x_lo > 0`);
  * pointwise φ_H, from an **ungated** replay surface;
  * host.
* **Compute:** theory negligible; replay ≈1350 CPU-s per cell; the majorant's own cost unmeasured.
* **Governance:** VERY HIGH for any K5 consequence: floor extension, admissibility decision, host, theorem review and
  the full chain.
* **Scientific risk:** HIGH (unproved; partial reach).
* **Result-chasing risk:** LOW for theory; MEDIUM for evaluation.
* **r2 adoptability:** **closure-only**.
* **P3:** new candidate-derived quantity, so **Condition 10 applies**.

**R-asm.** Assembly / clause tightening: σ₃, σ₄, env4, f_G surrogate (C4 §7.4).
* **Cells:** 307–309.
* **Mechanism:** a demonstrated-effective lever class (C5-T: 1.211–1.295 % of the penalty); `all_four_together`
  0.6076 % voids the 309 exclusion (vs C4's floor).
* **Evidence required:** new theorem(s), computed from adopted inputs.
* **Compute:** negligible to minutes.
* **Governance:** MEDIUM, plus a floor extension for any adoption.
* **Scientific risk:** HIGH (past gains ≈1 %).
* **Result-chasing risk:** LOW–MEDIUM for theory (same basis as RSO); MEDIUM for evaluation (C5-T's gate was post
  hoc).
* **r2 adoptability:** **closure-only**.
* **P3:** adopted inputs only, as far as committed text shows.

**X308.** Certified Λ₃₀₈ floor above the ceiling.
* **Cells:** 308.
* **Mechanism:** exclusion only (zero closure leverage).
* **Evidence required:** a certified floor above 4.442851, when the current floor is 3.512734 and the MC truth is 4.311.
* **Compute:** minutes to hours.
* **Governance:** MEDIUM.
* **Scientific risk:** **VERY_HIGH**. On uncertified MC at ~65 SE the target bound is false (E15 :508–512).
* **Result-chasing risk:** LOW.
* **r2 adoptability:** exclusion-only.
* **P3:** —.

**Floor-307.** Any new or lowered floor for 307–309.
* **Cells:** 307–309.
* **Mechanism:** none.
* **Governance:** barred.
* **Result-chasing risk:** **HIGH** (fitted to the known α projection).

**D.** Stop at K5 PARTIAL.
* **Cells:** all.
* **Mechanism:** none.
* **Evidence required:** a final adjudication.
* **Compute:** none.
* **Governance:** LOW.
* **Scientific risk:** none.
* **Result-chasing risk:** none.

**User-level prerequisites that no route may presume** (all from committed text):
* **U1: host provisioning.** C6 Condition 7 makes it a separately governed user decision. No certifying host is in
  scope (C6-N1), and the vultr-02 record is inconsistent: E07a's Aux5 venv (2026-09-20) vs C6-N1's `find_spec`
  absence (2026-09-22). This is unreconciled.
* **U2: admissibility of new quantities derived from P3 tail records.** C6 Condition 10 is binding, and raising the
  records above P3 needs C6-N5's schema semantics and C6-N4's manifest anomaly resolved.
* **U3: a floor extension** for any closure-only route to adopt (r2 `fail_closed[3]`; C2 Condition 1: freeze before
  recomputing).

**Structural finding.** Every route that is r2-adoptable today (R-α, R-E1g, R-F1′, R-I2-alone) carries HIGH or
MEDIUM–HIGH result-chasing risk, because it optimizes or shops operator constants against known per-cell factors. It
also needs U1.

Every route with LOW result-chasing risk (R4, RSO theory, R-asm theory, B1, X308) is one of:
* **barred:** R4, guard DENY;
* **closure-only under r2:** R4, RSO, R-asm, B1;
* **refuted in expectation by uncertified evidence:** X308.

## 7. Architecture comparison

Architectures are compared on the instructed criteria, **not** on chance of CLOSED. Following the review's request,
C is argued **on information gain alone**, with r0's withdrawn premises removed.

**C0a.** Staged, Stage 0a = RSO theory plus fixtures only; no host, no data.
* **What it can deliver without U1–U3:** a yes/no on a lemma whose reach is at most the `A0·f_H` part of one term.
* **K5 consequence:** none, by itself.
* **To matter for K5 it needs U1, U2 and U3,** plus a Stage-1 chain.
* **U3 liability:** it would be a floor extension decided knowing C8's per-cell factors. That is permitted if frozen
  first (C2 Condition 1), but it is a temporal-integrity liability of the kind C5 (post-hoc gate) and C8 (rule 1)
  recorded.
* **Information gain:** real but narrow and conditional.
* **Result-chasing risk:** LOW.
* **Compute:** negligible.
* **Governance:** a freeze plus ≥ 2 reviews now, and 3 user decisions plus a full chain later.

**C (general).** Any staged campaign aimed at K5 coverage for 307–309 must pick either:
* an r2-adoptable route (all HIGH or MEDIUM–HIGH result-chasing, §6); or
* a closure-only route (needs U3, and for replay-based routes U1 and U2).

No choice satisfies temporal integrity, low result-chasing risk and r2 adoptability together.

**A — joint.** Inherits C's route problem for all three cells at once; poor early stop.

**B — separate.** Inherits it per cell, and adds unbounded cross-campaign multiplicity (HIGH result-chasing).

**D — final K5 PARTIAL adjudication and publication closeout.**
* **Information:** the closeout records the complete blocker map (§4), the structural finding (§6) and U1–U3. It also
  ranks the open research items:
  * RSO lemma;
  * R-asm;
  * R4 after N1, N5 and N7;
  * B1 with a new provenance chain.

  None of this is lost. PARTIAL is **not** a claim that any cell is unclosable, and K5's specification pre-specifies
  `K5_INCONCLUSIVE` for unresolved cells (E01 :91; E03 :111–112).
* **Temporal integrity:** perfect.
* **Result-chasing risk:** none.
* **Compute:** zero.
* **Governance:** one adjudication plus one review.
* **Reproducibility:** a document-only chain.
* **Defensibility:** high.

**Comparison on information gain alone.** C0a buys one narrow, conditional mathematical answer. Converting it into
anything K5-relevant still needs three user-level decisions and a full chain, one of which (U3) carries a
temporal-integrity liability. D records everything the programme knows and forecloses nothing: a later theorem or
governance decision can reopen 307–309 under fresh authorization, frozen before any recomputation. The information
C0a adds does not require K5 to stay open; the lemma can be pursued as research whether or not K5 is closed out.

On the remaining criteria, D dominates C0a. Governance simplicity and defensibility decide the comparison, not chance
of CLOSED.

**Chosen: D.**

## 8. Information boundary and kill gates, for any future campaign

This section is not recommended now. It is kept so that a future authorization starts from corrected gates.

**Safe preflight (target-free):**
* theorem statements and proofs with no cell data;
* manufactured-fixture qualification;
* code- and schema-only applicability checks;
* 305 replay identity (PASS/FAIL only; candidates deleted unread; the reviewer confirmed this is safe);
* cost of the replay.

**Load-bearing:**
* any evaluation of a new bound, Γ, sign, margin, factor or closure indicator for 306–309;
* any ratio from which such a Γ could be inferred;
* **calibration on any real cell**, because per-cell ratios transfer as estimates (E09);
* anything computed on replayed tail candidates beyond identity.

**Gates that r0 lacked:**
* **KG-U1 host:** a separate user decision (C6 Condition 7), never bundled into a science stage.
* **KG-U2 admissibility:** a governance ruling that the new quantity may be derived from P3 records (or records raised
  above P3) **before** the Stage-1 freeze. Otherwise closure-only-and-inadmissible, so STOP.
* **KG-T trust surface:** any pointwise quantity (φ_H, residuals) must be **re-certified a posteriori** from the
  replayed candidate with outward exact or interval arithmetic, not taken from replay output. Scalar identity does not
  certify function values.
* **KG-U3 floor:** closure-only routes are labelled closure-only, unless a floor extension is instructed by the user,
  frozen and reviewed before Stage 1.
* **Cost:** replay **plus** the new evaluation's own cost against the cap.
* **KG2 (domination)** is a soundness obligation, not a kill gate.

## 9. Route table

| route | cell(s) | scientific basis | required work | compute | governance | success uncertainty | result-chasing risk | r2 | recommendation |
|---|---|---|---|---|---|---|---|---|---|
| 306-a…g | 306 | §5 | — | — | barred / exhausted | — | HIGH where applicable | — | **REJECT** (306 stays OPEN) |
| R-α | 307 | C9 projection | host, pin, chain | minutes | HIGH | medium | **HIGH** | conformant; ≤ 1.137406× projected < 1.370009× | **REJECT** |
| R-I2-alone | 307 | none beyond r2 form | I2 on 307 | hours | HIGH | high | **HIGH** | conformant | **REJECT** |
| R-F1′ | 307 | floor r2 | I2 on 307 + I1 closing | hours | VERY HIGH | high | HIGH (via α) | conformant | **DEFER** |
| R-E1g | 307, 308 | C8 R3 | new cell-independent certifier strategy + host | unknown | HIGH | high | MEDIUM–HIGH | conformant | **INSUFFICIENT_EVIDENCE** |
| R4 | 307–309 | E09, C2 §K | N1, N3, N5, N7 + host + new real | hours | VERY HIGH | medium | LOW | closure-only | **DEFER** (guard DENY) |
| R5 | 307–309 | C6 A1, C5 | replay + new sup routine + host + U2 | hours | HIGH | high | MEDIUM | closure-only | **DEFER** |
| B1 | 309 | C4 §7.3, C5 | new K1 addresses | multi-hour–CPU-day | VERY HIGH | medium | LOW–MEDIUM | closure-only | **DEFER** |
| RSO | 307–309 | C4 §7.1 (ranked first by C4 only) | theorem + U1 + U2 + U3 + chain | theory negligible; replay ≈1350 CPU-s/cell | VERY HIGH for K5 effect | high | LOW (theory) / MEDIUM | closure-only | **DEFER** (research item) |
| R-asm | 307–309 | C5-T precedent, C8 E3 | theorem + U3 | negligible–minutes | MEDIUM + U3 | high | LOW–MEDIUM (theory) | closure-only | **DEFER** (research item) |
| X308 | 308 | C3-N4 | certified Λ₃₀₈ > 4.442851 | minutes–hours | MEDIUM | very high (MC says false) | LOW | exclusion-only | **REJECT** |
| Floor-307 | 307–309 | none | — | — | barred | — | HIGH | — | **REJECT** |
| D | all | E01 :91, E03 | final adjudication + closeout | none | LOW | none | none | — | **PROCEED** (on authorization) |

No success percentages are given, because none is supported.

## 10. Recommendation: exactly one next action

> **Authorize the final K5 PARTIAL adjudication and publication closeout for the CUSUM m = 5 tail (cells 306–309),
> per `protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md`.**
>
> * No cell is evaluated.
> * No coverage changes: r5 stays final, and there is no r6.
> * The closeout records 306 NOT ADOPTED / OPEN, 307 and 308 OPEN, and 309 OPEN and REFUTED WITHIN SCOPE.
> * It also records the blocker map, the structural finding, U1–U3 and the ranked research items.

**Why, on the instructed criteria:**
* **Defensibility:** nothing is claimed beyond committed evidence.
* **Information gain:** everything known is recorded, and nothing is foreclosed.
* **Temporal integrity:** perfect.
* **Reproducibility:** document-only.
* **Compute:** zero.
* **Governance simplicity:** one adjudication plus one review.

It is **not** chosen because 307–309 are unlikely to close. That likelihood is unknown and is not estimated. It is
chosen because no route for 307–309 is simultaneously:
* r2-adoptable;
* low in result-chasing risk;
* evidence-supported;
* free of user-level governance changes that this audit may not presume.

**What stays possible.** The user may instead take the decisions U1–U3 and authorize a research-stage RSO or R-asm
theorem. This audit does not recommend it now (§7), but it forecloses nothing.

## 11. Protocol draft

`protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md` — **DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION**.

The r0 RSO draft remains as history and is not recommended.

## 12. Computation declaration

| quantity | count |
|---|---|
| new Γ evaluations, cell 306 | **0** |
| new Γ evaluations, cell 307 | **0** |
| new Γ evaluations, cell 308 | **0** |
| new Γ evaluations, cell 309 | **0** |
| target-equivalent proxies evaluated | **0** |
| scientific code executed | **0** |
| new real addresses, AWS or Vultr contacts | **0** |

## 13. Coverage preservation

* r5 (`f978eeb6…`) is authoritative and unchanged.
* No r6 exists.
* Maps r3 and r4 are unchanged.
* The m = 5 open set is 306–309.
* K5 is **PARTIAL**. SR K5 is NOT STARTED (E04) and outside this audit.

## 14. Forensics and unrelated refs

* **Retained:**
  * `b83cc6f5`;
  * `def4e453`;
  * `refs/c12r2/cell306-target-consumed` (dec92e09);
  * `refs/c12r2/cell306-pending-result` (`0ac46b3d`);
  * seal 276f4d41;
  * all C12-line reviews;
  * r0, its draft and its rejecting review.
* **Unrelated:** the `p5y-k4*` ref movement (`p5y-k4-frozen-execution-r1 bc4ba08e`, `p5y-k4r1-nearzero-successor
  5d33363c`) concerns K4. It is recorded and not touched.

## 15. Limitations

* The architecture ratings are argued judgements.
* The P3 coverage of R-α / R-E1g / R-F1′ / R-I2-alone by the `already_adopted_exception` is inferred from committed
  text: they use adopted TCT inputs plus new operator constants. It would need an explicit ruling if any of them were
  ever pursued.
* The vultr-02 host-record inconsistency is reported, not resolved.
