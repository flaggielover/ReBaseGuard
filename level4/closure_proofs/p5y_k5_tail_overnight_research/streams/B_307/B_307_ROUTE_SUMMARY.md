# B_307_ROUTE_SUMMARY — cell 307 higher-order bottleneck and real order-3 research

Stream B_307 (validation prefix `B307_`). Research only: **no route and no cell is CLOSED**, nothing is adopted, and
nothing is frozen.

**Quarantine.** 0 target evaluations, 0 target-equivalent proxies, 0 target-informed optimisations. Every run is in
`NS/ledger/ZERO_TARGET_LEDGER.jsonl` with class SYNTHETIC_VALIDATION, NONTARGET_DRIFT_VALIDATION or
NONTARGET_REAL_VALIDATION. The static scan (`code/ov_quarantine.py --scan`) found 0 findings in the 8 B_307 files,
and its planted control was detected.

## Deliverables

| file | content |
|---|---|
| `HIGHER_ORDER_AUDIT_307.md` | HO-1 … HO-16 inequality reconstruction, Λ/C/ρ/j orders, exact fixture demonstrations T1–T5, ranked looseness inventory |
| `REAL_ORDER3_THEORY.md` | true order-3 objects; TC vs K5-B chain needs; resolvent and Hermite/LR representations; finiteness; Propositions RO3-S/F/E; ADLR evaluation; inputs and availability; fixtures and lower-front evidence; the structural-information verdict |
| `VALIDATION_DECLARATION_B307.json` | validation sets, declared before any run |
| `code/b307_lib.py`, `b307_cellpipe.py`, `b307_order3.py`, `b307_run_fixtures.py`, `b307_scaling.py`, `b307_tower_fixture.py`, `b307_lower_front.py`, `b307_hermite_check.py` | stdlib-only producers |
| `NS/validation/B307_AUDIT_FIXTURES.json`, `B307_ORDER3_FIXTURES.json`, `B307_SCALING.json`, `B307_TOWER_FIXTURE.json`, `B307_LOWER_FRONT_ORDER3.json`, `B307_HERMITE_IDENTITY.json` | results. Controls are classified (a)–(d) as in `NS/reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` §1; see the Controls table below. Class (c)/(d) items are not counted as evidence |

## Registry rows

| id | route | mechanism | cells in principle | state | r2 status | owner |
|---|---|---|---|---|---|---|
| **B307-R1** | real order-3 candidate Ĝ ≈ F_r'''(e0) in theorem TC (R4, restated) | replaces the norm-only surrogate A0ρf_G by ρ\|Ĝ(a)\| + A0ρδ_G, at the cost s_G in Env4 | any; the tail untested | **BLOCKED**: candidates never serialized (C6); no host; producer registry empty and guard DENY; N1/N3/N5/N7 open | closure-only | B_307 (theory); governed campaign (execution) |
| **B307-R2** | ADLR: atom-direct LR Taylor enclosure (coordinator suggestion) | Ĥ(a) ± [rad0 + sB3 + s²B4/2] with B3, B4 built from atom functionals A_j and source sups σ_i | any | **BLOCKED**: needs sharp cell-uniform A_3, A_4, which no stream certifies. Validated on fixtures only | closure-only | B_307 (theory, fixtures) |
| **B307-R3** | Hermite h/S tower: ‖h_j^(n)‖ ≤ κ_n j^{n/2}, ‖S_r^(n)‖ ≤ √(n!(r+1)^n) + nκ_{n−1}(r+1)^{(n−1)/2} | alternative σ3/σ4 supply, min with the frozen tower | any | **THEORY_ONLY** (identity validated at the declared drifts; tower slack on fixtures) | closure-only | B_307 |
| **B307-R4** | joint (unsplit) order-3/4 residual across the four kernel terms and across r | removes the split factor (≈ 2.2×) and the per-r triangle (≈ 2.4×) | any | **BLOCKED**: needs the candidate payloads (C6) | closure-only | B_307 (theory) |
| B307-ref | (A1, A2) via LR / score constants | removes the sign-cancellation slack (rank 1) | any | referenced, **DEFERRED to C_308** (not implemented here) | closure-only | C_308 |

## Kill-gate table

Legend: P = pass, F = fail, — = not applicable or not reached.

| gate | B307-R1 real Ĝ | B307-R2 ADLR | B307-R3 Hermite tower | B307-R4 joint residual |
|---|---|---|---|---|
| G1 prospective motivation (independent of target sign) | **P**: norm-only structure (RO3-S); lower-front evidence | **P**: removes the A1/A2 cross terms structurally | **P**: j^{n/2} vs j^n growth | **P**: split and assembly slack on fixtures |
| G2 mathematical validity | **P**: TC holds for any Ĝ; RO3-F and RO3-E proved and checked (320 / 640 objects) | **P**: validity conditions (i)–(iii) of §4d; 0 failures in all variants | **P**: Gaussian-location lemma; identity checked to 4.4e-13 | **P** (standard triangle) |
| G3 scope explicit | **P** | **P** | **P** | **P** |
| G4 reproducible implementation | P on fixtures; **F** on real cells (no producer or host) | P on fixtures | **—** (float identity only; no σ supply built) | **F** (no payloads) |
| G5 non-target validation | **P**: fixtures, plus 34 real lower-front cells (136/136 exact reproduction; real/surrogate enclosure 0.11–0.22) | P on fixtures; **—** on real cells (no certified Λ_j) | — (no test of the Hermite tower as a σ supply; the identity check at declared drifts and the FX_B tower slack are not a validation of R3) | P on fixtures |
| G6 independent check | partial: independent re-implementation of the TC arithmetic reproduces the committed audit exactly. No second agent has checked RO3-E/F | **F** (single implementation) | **F** | **F** |
| G7 temporal integrity | **P**: declaration before runs; no target evaluation | **P** | **P** | **P** |
| G8 no target leakage | **P** | **P** | **P** | **P** |
| G9 could be frozen prospectively | **F**: data, host and governance (N1/N3/N5/N7) | **F**: A_3, A_4 uncertified | F (no supply built) | **F** (payloads) |
| G10 real, not cosmetic | P on non-target: lower-front m-enclosures are 4.42–9.35× narrower (`B307_LOWER_FRONT_ORDER3.json` `enclosure_narrowing_factor_surrogate_over_real_all_m`). **Baseline caveat:** the surrogate baseline uses the pure-tower σ3, which is looser than a (P3′) surrogate, so the factor favours R1. Capped by 1/(α+β); leaves ranks 1 and 3 | **F** with certified constants (18×–2·10⁴× looser); best case incomparable (FX_A 0.46×, FX_B 2.9×) | undetermined (bounded gain, j ≤ 5) | undetermined (≈ 2× on fixtures) |
| **state** | **BLOCKED** | **BLOCKED** | **THEORY_ONLY** | **BLOCKED** |

## Controls register (review F6: classes as in `NS/reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` §1)

Class key:
* (a): through the code under test, planted invalid input, guaranteed to fire;
* (b): through the code, not guaranteed; the fire rate is given;
* (c): tautological or arithmetic;
* (d): tests only a comparison operator.

(c) and (d) are **not evidence**. No control gates a script's exit code; each is reported as a JSON count.

| check | control | class | result | source |
|---|---|---|---|---|
| resolvent-derivative formulas (P1) | ∂³R without 3RK₂RK₁R | (a) | 4/4 | `B307_AUDIT_FIXTURES.json` P1 |
| E'' identity at a point (P1) | factor 2 dropped | (a) | fired | P1 |
| E'' identity on every grid point (P3) | ∂²R without RK₂R, through the identity check | (a) | 5439/5439 eligible | P3_verdicts |
| (P2)/(P2′) φ''' identity (P1) | 2K₁Ĥ in place of 3K₁Ĥ | (a) | 2/2 | P1 |
| ladder soundness `ladder_checks` (P2) | A1 Lemma-G rung := true·(1 − 2⁻²⁰); PM ↔ collapse swap | (a) | 42/42; 42/42 | P2 `class_a_plants_through_ladder_checks` |
| Lemma SM(d) "A0 := τ_a ≥ Λ" | — | **(d) non-evidence** (C-7) | 42/42, not counted | P2 `NON_EVIDENCE_class_d_A0_eq_tau_a` |
| Λ-exponent claim (drift 0) | mutant with \|K_i\| through `b307_lib.Point` | (a) | fired (2.008 / 3.006 / 4.004 vs claim 1.5 / 2 / 2.5) | `B307_SCALING.json` `exponent_claim_check` |
| linear slope plant "true × Λ^{1/2}" | — | **(c) non-evidence** (C-8) | — | `B307_SCALING.json` |
| five-way split of E'' | — | **(c) non-evidence** (C-9), true by construction | — | P3 |
| pointwise soundness \|E''\| ≤ rad | sign-flipped centre motion; f_G := 0 (E10) | (b) | 328/640; 146/320 | P3_verdicts |
| RO3-F floor check | G = 0, f_G = 0, s_G = 0 through `route_groups` | (a) | 320/320 eligible | `B307_ORDER3_FIXTURES.json` verdicts |
| RO3-E envelope check | inflated s_G through `route_groups` | (a) | 320/320 | same |
| ADLR pointwise soundness | oracle with B3 := 0 | (b) | 247/320 | same |
| lower-front exact reproduction | 2⁻⁶⁰ perturbation of one δ_G through `per_object` | (a) | fired | `B307_LOWER_FRONT_ORDER3.json` |
| Hermite identity (one-step / j-step) | sign dropped; variance rescaling dropped | (b) | 112/120; 225/300 (the misses are identically-zero or order-1 cases) | `B307_HERMITE_IDENTITY.json` |
| J/h tower soundness (FX_B) | binomial weights dropped | (b), weak | 6/54 | `B307_TOWER_FIXTURE.json` |
| quarantine static scan | planted file | (a) | detected | `ov_quarantine.py --scan` |

## Per-cell deliverable — cell 307

**Correction note (incident 01).** A pre-correction version of this section listed committed tail shares of S next to
lower-front route factors. That adjacency is a target-equivalent proxy. It was corrected on coordinator instruction
(incident 01): committed history now sits in its own subsection (0), and no route factor appears there or next to it.

**0. History (committed, quoted; no route factor attached).**
* C5 decomposition of 307's radius sum S (`p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:43-50`):
  * A0·ρ·f_G 61.59 %;
  * A0·ρ²·Env4/2 19.86 %;
  * 2A1·p1 16.77 %;
  * A2·p0 1.67 %;
  * A0·f_H 0.11 %.
* Under the C3/C4 knockout, 307 closes at A1 = A2 = 0 with the certified A0, so (A1, A2) is 307's blocker under that
  clause (`p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:72-76, 103-105`).
* The accepted route audit rates R4 at HIGH scientific risk for 307 (`p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md:105-124`).
* The tail's own s_G/s_H has never been measured (`p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md:68-69`).

**1. Higher-order decomposition (structural; no numbers).**
* The (A1, A2) monomials are A1ρ²f_G + A1ρ³Env4/3 + A2ρ³f_G/6 + … plus measured-residual terms. So the committed
  blocker is structurally the **product** of two slack classes:
  * the atom-functional slack (audit rank 1: sign cancellation, a Λ^{j/2} asymptotic gap);
  * the order-3/4 surrogates (ranks 2–3: norm-only bounds on point values).
* The frozen cover rule gives k₁ρC ≤ 1/4 at every cell, so the A1/A2 monomials are never asymptotically small
  relative to the A0 monomials at any cell.

**2. Order-3 findings (general theorems, and non-target evidence only).**
* (a) RO3-S: the surrogate's dominant monomial is exactly a norm-only resolvent bound of ρ|F'''(e0)(a)|.
* (b) RO3-F: no choice of Ĝ goes below the true centre motion in a whole-cell interval.
* (c) RO3-E: a real Ĝ moves a norm-only cost to order 4. Under the cover rule that cost is at most ≈ 1/2 of the
  surrogate monomial, so the gain is ≈ 1/(α + β).
* (d) ADLR is valid and has an excellent shape, but it is incomparable with TC-T and blocked on certified A_3, A_4.
* Non-target measurements (fixtures, and the 34 lower-front cells) are in REAL_ORDER3_THEORY §6. They are **not**
  transferred to 307, and no number from them is placed here.

**3. Strongest surviving route (by theoretical avoidable slack, not by closure chance).**
* The largest **proven asymptotic** slack is audit rank 1: sign cancellation in the atom functionals of ∂R and ∂²R,
  owned by C_308 (LR). This stream shows that the whole Λ^{j/2} gap is sign cancellation; the positive-majorant rung
  already has the certified exponent.
* Inside this stream's remit, the strongest surviving route is **B307-R1** (real Ĝ). It is the only one with a
  demonstrated real non-target gain, it is **BLOCKED** and **closure-only**, and it leaves ranks 1 and 3 untouched.

**4. Remaining theorem gap.**
* (i) No certified sharp atom functionals capturing the score cancellation: A1, A2 (C_308), and A3, A4 (unowned).
* (ii) No pointwise order-4 object. Rank 3 dominates after any order-3 fix (fixtures).
* (iii) No sign-aware consumer of the order-3 point value compatible with floor r2. TPT and the chain are
  closure-only or need contiguity.
* (iv) R4's data, host and governance prerequisites (N1/N3/N5/N7).

**5. FREEZE_READY: NO.**
No route of this stream meets G9. Every route is closure-only under floor r2 and would need a user-decided floor
extension frozen before any evaluation (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:42`).
