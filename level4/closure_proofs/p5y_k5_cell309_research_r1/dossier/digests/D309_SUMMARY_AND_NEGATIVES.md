# Digest: Stream D (cell 309) route summary, scoped negative families, progress log

Firewalled digest. Sources (NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`):
`streams/D_309/D_309_ROUTE_SUMMARY.md`, `streams/D_309/SCOPED_NEGATIVE_FAMILIES_309.md`, `streams/D_309/PROGRESS.md`.
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
SCOPED §1 quotes committed tail numbers; every one is redacted below. Families are stated symbolically with their exact
scope (what is held fixed, which consumer).

---

## A. Scoped negative families (SCOPED_NEGATIVE_FAMILIES_309.md §1 "History (quoted, no route factor)")

Document status: RESEARCH, target-free; nothing computed; every tail number quoted from a committed file with
file:line; no new-route gain factor; §1 history only, §2 structural differences only.

### F1 — uniform-A0 atom-constant family — REFUTED WITHIN SCOPE
* **Family** (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:196-199`): every triple
  `(A0, A1, A2)` whose A0 is a valid **uniform order-0 bound on the closed cell**, consumed through the **frozen TC-T**
  and the **frozen K5-B direct clause**, at the **frozen measurement inputs**, at **cell 309, m = 5**.
* **Held fixed:** TC-T (premise supplies (P2′), (P3′), Ĝ := 0), the K5-B direct clause, the frozen measurement inputs
  (K1 records, sup norms, residuals, W, cover cell). **Varied:** the atom-constant triple, with A0 uniform on the cell.
* **Excluded by the gate's own `does_not_cover`** (`:201-203`): residual-specific (non-norm-only) order-0 bounds; any
  change to TC-T, to the K5-B clause or to the frozen measurement inputs; order-3 candidates of F.
* **Binding restatement** (C4 Condition 1, `:522-526`, superseded by the C5-T restatement,
  `p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md:357-363`): **consumer = C5-T transport** (not the
  frozen clause) against the frozen measurement inputs: no uniform-A0 supply closes 309 for any `A1, A2 ≥ 0`. "It is
  not a statement that cell 309 is unclosable".
* **Floor vs ceiling (symbolic):** C5-T critical A0, `A0*_{C5-T}` = [TAIL-NUMBER REDACTED]
  (`p5y_k5_tail_c7_e2_lambda309/README.md:20`); C7 floor `Λ₃₀₉ ≥` [TAIL-NUMBER REDACTED] (`README.md:15`); Lemma SM(d)
  makes `A0 ≥ Λ` necessary (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:51`). The refutation is the
  ordering `A0*_{C5-T} < Λ₃₀₉-floor ≤ A0` for every valid uniform A0.
* **C3 knockout:** `A1 = A2 = 0` still leaves 309 open (`p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md:351`;
  `OPEN_NOTES_DISPOSITION_C3.md:22`).
* **C8 wording:** refutation holds "within the atom-constant family, at the committed sup norms"
  (`p5y_k5_tail_c8_operator_feasibility/README.md:63-71`).
* **C4 Condition 5:** the margin exists only by virtue of the sup-over-closed-cell quantifier and the left-endpoint
  evaluation (`C4_ADJUDICATION.md:543-547`).

### F2 — two-input transport family — EXHAUSTED (C5)
* **Family** (`C5_ADJUDICATION.md:165-167`): every bound on `max_cell g` derivable from exactly (i) `g_hi` and (ii) a
  whole-cell `[H_lo, H_hi]`, on a cell in `e > 0`.
* **Held fixed:** the two inputs. **Varied:** the transport (consumer) only.
* **Scope** (`:175-181`): exhausts "the transport, not the cell"; "says nothing" about improving g_hi, improving the R''
  enclosure, or "a transport consuming a third certified input".
* **Scope limits** (`:185-189`; Condition 8 `:597-599`): witness is an arbitrary absolutely continuous function, not a
  resolvent-type R; `x_lo > 0` required.
* **Outside F2:** `streams/E_assembly/THEOREM_TPT.md` (consumes a third certified input, the TC profile; TPT-O makes
  TPT optimal within the three-input family).

### F3 — C7 E2 family (Wald/overshoot lower bounds on Λ₃₀₉)
* **Ceiling:** family ceiling [TAIL-NUMBER REDACTED] lies below the certified A0 [TAIL-NUMBER REDACTED]
  (`p5y_k5_tail_c7_e2_lambda309/README.md:107-113`), i.e. symbolically `sup_{E2} Λ-lower-bound < A0_certified`.
* **Going further needs** (`:115-117`): a bound on `E[τ] − E[τ′]`, or on the gap between the sup over the cell and the
  value at `e_lo`.
* **Direction:** yields **lower** bounds on Λ, so can only strengthen the exclusion. **Scope: 309 only.**

### F4 — C1 atom deflation at the tail — MARGINAL
* The need falls [TAIL-NUMBER REDACTED] → [TAIL-NUMBER REDACTED], a relative fall of [TAIL-NUMBER REDACTED] against the
  MARGINAL-classification threshold [TAIL-NUMBER REDACTED] → class MARGINAL (`p5y_k5_tail_operator_registry/README.md:26-30`).
* Deflation buys a factor [TAIL-NUMBER REDACTED] on A0 and makes A2 worse (`:24-25`). Ā is inert (`:31`).
* Scope: C1's deflation is a norm-only atom-constant supply (a member of F1).

### F5 — Campaign B route T2: a real order-3 candidate at the tail — USEFUL class REFUTED
* Source: `p5y_k5_m5_tail_closure/README.md:22-29`; `phase_c/EXECUTION_DECISION.md:57-100`.
* Scenario table (cells USEFUL out of the five tail cells): audit's own inputs — NOMINAL [TAIL-NUMBER REDACTED],
  CONSERVATIVE [TAIL-NUMBER REDACTED]; Campaign-A order-3 scale — NOMINAL [TAIL-NUMBER REDACTED] (INFEASIBLE),
  CONSERVATIVE [TAIL-NUMBER REDACTED].
* **Single hinge** (`EXECUTION_DECISION.md:81-86`): the centre motion, under the evidence model `|Ĝ(a)| = c·s_G` with
  c = [TAIL-NUMBER REDACTED].
* Scope: a forecast built on the TC-T consumer with a real Ĝ supplied at the tail, using lower-front ratios as the
  evidence model.

### F6 — C8 routes R1 (clipping gap) and R2 (cell uniformization): zero closure leverage
* Both raise Λ; raising a floor cannot lower Γ. Perfect information in either changes Γ by exactly 0
  (`p5y_k5_tail_c8_operator_feasibility/README.md:36-41, 74-77`).

### F7 — C5 route-search verdicts (`p5y_k5_tail_c5_exhaustion/phase_3/C5_ROUTE_SEARCH.md`)
Killed:
| route | line | verdict |
|---|---|---|
| B2, split the clause without new records | `:50` | "R and D are certified at e0 only; transporting them to a sub-midpoint costs exactly what the split saves" |
| D2, sign-awareness alone | `:52` | an identity |
| A4, reuse the cell-0 order-3 probe | `:46` | no certified transport across the range |
Not refuted:
| route | line | status |
|---|---|---|
| A1, tighten sup{F,D,H} | `:43` | DATA |
| A3, cancellation in the order-3 identity | `:45` | DATA |
| B1, cover refinement | `:49` | NEW_REAL |

### Levers C5/C8 list as outside F1 (quoted; no route attached)
* Six source-supply levers, cheapest `all_four_together` at [TAIL-NUMBER REDACTED]
  (`C5_FORECAST.json:24-32`; `ERRATUM_C8_GATE.md:39-44`).
* Three oracles ("ρ halved", `sup{F,D,H} → 0`, `f_G → 0`): C5 Condition 10 (`C5_ADJUDICATION.md:606-613`).
* Caveat on "ρ halved" (`c5_common.py:85-86`): scales only the TC-T Taylor ρ (`meas["rho"]`); transport factor ρ·x_hi
  and g_hi unchanged; therefore **not** a model of a cover refinement.

## B. Why each new route lies outside these families (SCOPED §2; structural, no numbers)

"Cosmetic" relative to a family = certified output equals, for every input, a bound the family already produces
(possibly after renaming/reparameterization).

**SC (composite-sup premise supply).** Replaces `f_G ≥ ‖φ'''(e0)‖` (optionally `Env4 ≥ sup_C ‖φ⁗‖`) by a certified sup
of the actual function; Leibniz triangle/submultiplicativity product not used.
* vs F1: leaves A0, A1, A2 untouched and changes a TC-T premise supply = C4's excluded item "any change to TC-T … or to
  the frozen measurement inputs" (`C4_ADJUDICATION.md:202-203`). Not a reparameterization of A0: such a rescaling
  would be `A0' = A0·(f_G^SC / f_G)` on the ρ f_G term only, not a uniform order-0 bound (can violate SM(d), below Λ
  when the ratio is small) → not representable in F1.
* vs F5 (T2): keeps Ĝ := 0 (s_G = |Ĝ(a)| = 0, TC-T (P2′)); no order-3 candidate, no producer run; T2's hinge (centre
  motion ρ|Ĝ(a)|) absent; measures the zero-candidate residual exactly instead of by the triangle inequality.
* vs A1 (sup-norm tightening, C6): changes no s_X, identity-gated fields byte-identical; C6's "faithful replay …
  delivers exactly zero of A1's gain, by construction" does not apply; SC adds a **new** quantity from the same payloads.
* Relation to A3: SC is C5's route A3 made precise (theorem, strictness proposition, computable certificate).
* Gain is the Leibniz slack (SC-T), a structural quantity, not the removed source term.

**CR (real cover refinement).** Uses **new certified midpoint records** (new g_hi, new TC premises, new cell for the
uniform quantifiers).
* vs F2: each record adds certified inputs beyond (g_hi, [H_lo, H_hi]) → outside F2 by C5's scope sentence
  (`C5_ADJUDICATION.md:179-180`).
* vs B2: CR-2 (corollary of TPT-O) — record-free split dominated by TPT **within the fixed-(g_hi, L, U) family**
  (repair r1: r0 "validated with exact zero difference" withdrawn — 0 by construction; r0 "B2's kill is confirmed and
  sharpened" overreached — C5 killed B2 as NEW_REAL). Record-free split re-certifying constants on sub-segments (B2c)
  is outside that family, unevaluated. Real refinement is the complement of B2.
* vs F1: refinement changes the cell → the domain of the "uniform on the closed cell" quantifier and the constants over
  it. F1 is stated for the frozen cell; C4 Condition 5 records dependence on that quantifier and left-endpoint
  evaluation.
* Rejected cosmetic variant: scaling only the TC-T Taylor ρ while keeping g_hi and ρ·x_hi (C5 oracle knob) is not a
  refinement.

**RSO (residual-specific order-0 and derivative extensions).** Bounds |(R_eφ)(a)| by (R_eψ)(a), ψ ≥ |φ|, certified by
v ≥ ψ + K_e v.
* vs F1: collapse lemma (constant ψ → c·Ā, a member of F1); characterization: leaves F1 iff ψ ≠ ‖ψ‖ μ-a.e. (r1 wording;
  SCOPED §2 text still says "non-constant on the support of the atom's occupation measure"); gain over best F1 member
  exactly ‖ψ‖/μ_a(ψ) ≥ 1; F1 is norm-only by definition (non-norm-only bounds named excluded at `:201-203`).
* vs F3/F6: produces **upper** bounds on atom functionals of specific residuals; never raises a floor.
* vs F4 (C1): C1's deflation is norm-only (member of F1).
* RSO-PM / RSO-LR: pointwise in ψ; constant ψ → norm-type atom constants (F1); non-constant ψ outside F1.

**Assembly (TPT, E stream).** Outside F2 by C5's own scope sentence; used as transport, not restated.

## C. Route summary (D_309_ROUTE_SUMMARY.md)

Quarantine tally: new target evaluations 0; target-equivalent proxies 0; target-informed optimisation 0; drifts
touched: synthetic FSM ≤ 3/8 and CUSUM kernel at {0, 1/4, 1/2, 1, 3} ± 2·10⁻⁴; static scan 0 findings in seven
`code/*.py`. Ledger SYNTHETIC_VALIDATION / NONTARGET_DRIFT_VALIDATION only. Rule S8: committed history only in SCOPED
§1, COVER §9, RESIDUAL §1.

### C.1 Route rows (P = PASS, p = PARTIAL)
| route | document | state | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | floor r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SC composite-sup (SC-3, SC-4w, TC⁺; SC-T; SC-S1) | SUPNORM_THEOREM.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | P¹ | P | P | P | P for exact sups³ | CLOSURE-ONLY |
| CR real cover refinement (CR-1..3, DRP-0/1) | COVER_REFINEMENT_309.md | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED (outcome-adaptive); real use BLOCKED (NEW_REAL) | P | P | P | P | P | P¹ | P | P | P | P | CLOSURE-ONLY |
| B2 split without new records, fixed (g_hi, L, U) | COVER §4 | REFUTED **within the fixed-(g_hi, L, U) family** (CR-2 via TPT-O) | — | P | P | P | identity only² | P¹ | P | P | — | fails within that family: cosmetic | — |
| B2c record-free split, constants re-certified on sub-segments | COVER §4 | THEORY_ONLY (unevaluated) | P | — | P | — | — | — | P | P | — | not assessed | CLOSURE-ONLY |
| RSO-C4 (original, A0 f_H only) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; structurally narrow | P | P | P | P | P | p | P | P | P | P for non-constant ψ | CLOSURE-ONLY |
| RSO-P (+ RSO-PM, needs SC for order 3) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | P¹ | P | P | P | P iff ψ ≠ ‖ψ‖ μ-a.e. | CLOSURE-ONLY |
| RSO-LR order 1 | RESIDUAL §3.2 | VALIDATED_NON_TARGET (single drift) | P | P | P | P | P | p | P | P | P | P | CLOSURE-ONLY |
| RSO-LR order 2 | RESIDUAL §3.2 | THEORY_ONLY | P | sketch | P | — | — | — | P | P | — | — | CLOSURE-ONLY |
| Assembly (TPT) | E stream | referenced, not restated | | | | | | | | | | | CLOSURE-ONLY |
Footnotes: ¹ G6 PASS for the mathematics only (review re-derivation, own quadrature). ² "B2 − TPT = 0" is a
transcription identity, not evidence (B3). ³ SC-S1 is strictness of the exact sup; certified gain not guaranteed (N3).

### C.2 Common blockers for every real-use row
* **Payloads:** K1 candidate payloads never serialized; no real cell, target or not, has them (SUPNORM §8).
* **U1 (host):** numpy and python-flint needed; absent locally and on the permitted worker (C6-N1).
* **U2 (admissibility):** new quantities derived from P3 records fall under C6 Condition 10.
* **U3 (floor):** a floor extension, frozen before any evaluation.
* **CR additionally:** new real K1 addresses (NEW_REAL, guard DENY).

### C.3 Per-cell deliverable for 309
* Scoped negative families F1–F7, each new route shown outside them on structural grounds.
* Sup-norm result: Theorem SC general; SC-T shows the composite measures ‖(I−K)F_r'''(e0)‖ up to candidate errors
  while the surrogate is its Leibniz triangle bound; SC-S1 strict submultiplicativity slack for continuous candidates on
  the Gaussian kernel; validated exactly on FSM; Hermite machinery and stdlib Taylor-form certificate validated on the
  real kernel at non-target drifts. **Not killed.**
* Cover result: CR-1 exact ρ-decomposition; CR-2 (within fixed family, record-free split dominated by TPT via TPT-O);
  B2c outside and unevaluated; real refinement removes 1−1/N of order-1, 1−1/N² of remaining order-2, 1−1/N³ of order-3
  (CR-3 leading order); C5 "ρ halved" oracle is not a refinement model; DRP-0 (result-free) / DRP-1 (outcome-adaptive,
  frozen predicate) with cost model.
* Residual-specific result: RSO-0 with occupation characterization (shape factor ‖ψ‖/μ(ψ)) and collapse lemma (constant
  ψ → F1); RSO-PM, RSO-LR; RSO-P assembly; RSO-C4 narrow, RSO-P with SC covers every order.
* Assembly: relies on TPT for transport and on TPT-O for CR-2.
* **FREEZE_READY: no.**

### C.4 Strongest surviving route (structural ranking only; no committed per-cell number, no synthetic ratio)
1. **SC + TPT** — strongest route creating no new real K1 object: acts on the order-2 (f_G) and order-3 (Env4) channels,
   which dominate the slack of any **wide** cell (ρ r1 ≫ r0 + W); gain strict for **exact** sups with continuous
   candidates on the Gaussian kernel (SC-S1), certified gain not guaranteed (certificate overhead 1.2–1.44× on test
   functions); exactly the Leibniz gap (SC-T); composes with every atom-constant supply and with TPT; blocker is data
   (payloads + U1/U2), not mathematics or NEW_REAL.
2. **Real cover refinement** — structurally most powerful: acts on every ρ-order with factors N^{−j} incl. the order-1
   slack SC and TPT cannot remove; re-certifies constants over smaller cells; changes the cell of F1's quantifiers.
   Blocker: NEW_REAL + U1/U3.
3. **RSO-P (∘ SC)** — multiplicative refinement of SC (occupation shape factor on every term); RSO-C4 alone narrow
   (order-0 term only); blockers of SC plus a supersolution certificate per term.

### C.5 FREEZE_READY: no — reasons
1. No payloads (regeneration needs U1; derived quantity faces U2). 2. Every route closure-only under floor r2 (U3).
3. Cover refinement needs new real addresses under guard DENY. 4. Independent review (ACCEPTED_WITH_CONDITIONS)
agrees no route could honestly be FREEZE_READY; conditions repaired (§7).
Freezable now (prospectively, G9): theorem statements; certificate formats; declared calibration rule for the SC
certificate configuration (Taylor-form ranges, cover depth ≥ 5, panel 1/16, calibrated on synthetic degree-matched
functions); DRP-0/DRP-1 with fixed depth and budget.

### C.6 Negative results and limits recorded (§5)
* B2 within the fixed-(g_hi, L, U) family is cosmetic (CR-2 via TPT-O); r0 "30/30" withdrawn as evidence.
* RSO-C4 barely moves the radius on FSM (rad ratio 0.957–1.000); RSO without SC (normonly34) 0.80–1.00.
* Constant ψ gives no gain (N0/(Λ‖ψ‖) ≥ 1 with small overhead; synthetic ratio).
* SC equality case: sign-aligned discontinuous candidates on a general FSM kernel reach S3 = S1.
* Naive interval certificates vacuous for a degree-9 function (≈ 10⁴× grid lower bound).
* Pure-scaling refinement prediction errs by up to 37 % (FSM).
* Coverage limits: H1 kink control misses 24 of 960 (all w_bump at one state, below tolerance); H1b misses 5 of 960.
  Transport-level soundness checks are weak necessary conditions (FSM enclosure check: Env4 := 0 detected 0/60, halved
  A0 1/60; cover transport check rad_half 0/140); load-bearing checks are premise-level and profile-level truth checks.

### C.7 Quarantine observations (§6)
* `ov_quarantine --scan` reports one finding in **another stream's** file, `streams/A_306/a306_reproduce_A.py`
  (`TARGET_INPUT_PATH`); not touched; flagged for the coordinator.
* `d309_hermite.py` memoises `c7_gaussian.sqrt_two_pi`, `phi`, `Phi` in-process (value-identical, `_memo_selftest`);
  library files unmodified.
* Rule S8 arrived after all computation and before any document was written; no correction needed.

### C.8 Repair r1 (conditions of REVIEW_STREAM_D_R1, ACCEPTED_WITH_CONDITIONS) — dispositions
No theorem changed; all six D309_*.json regenerated; no target cell, band drift or committed tail number touched; S8 and
quarantine amendment 2 respected ("no validation-drift Λ or supersolution value appears anywhere in this stream").

B1 controls replaced (planted invalid input → checker; power):
| r0 control | replaced by | power |
|---|---|---|
| d309_hermite H3 "planted-too-small" | defects inside `box_upper_composite` → per-box containment | drop_sign 2/4 runs, collapse 4/4, shrink_half 0/4, drop_hull 2/4; genuine 0/2996 |
| d309_hermite_tf "planted" | defects inside `box_upper_tf` → containment | zero_remainder 6/6, half_remainder 4/6, drop_sign 6/6, drop_hull 2/6; genuine 0/9028 |
| supnorm NC1 | relabelled comparator control | differs 60/60 |
| supnorm NC2 (rad := max dev/2) | planted-invalid premise supplies → `premise_truth` and `enclosure_check` | premise: Env4 := 0 60/60, A0 halved 60/60, A0 × 0.99 20/60; enclosure 0/60, 1/60, 0/60 |
| rso NC (a) | invalid ψ through `cert_chain` → truth | a1 N0 44/48; a2 N0 48/48 |
| rso NC (c) | invalid LR certificates through `lr_certificate` | drop_cross 4/12, drop_KS2 12/12, drop_psi 12/12 |
| cover "half transport" | transport/profile/midpoint mutants on 140 records | profile: no_rad 136/140, flat 130/140, no_W 140/140, rad_half 0/140; transport: no_rad 32/140, rad_half 0/140 |
Genuine controls NC (b) (`check_cert_taylor`) and NC (d) (score via kernel builder) kept; `midpoint_check` shifted
interval relabelled a harness check.

Test power: premise-level (`premise_truth`) and profile-level (`transport_mutants`) truth checks added; FSM
enclosure/transport checks downgraded to weak necessary conditions (TC radius overestimates true deviation by > 2× on
these fixtures, so a halved radius is still valid there). Premise-level checks carry SC evidence: genuine 0/300.

B2: route B2 "REFUTED within the fixed-(g_hi, L, U) family" (COVER §4; SCOPED §2; row above); CR-2 uses TPT-O's
supremum (N10). B2c recorded THEORY_ONLY. B3: "B2 − TPT = 0, 30/30" relabelled a transcription-consistency identity.

Guards (N8): `Q.guard_drift` added in `box_upper_composite`, `box_upper_tf`, `abs_sup_matrix`, `check_cert_taylor`,
`check_cert_grid`, `LRFamily.kernel`, `LRFamily.kernel_deriv`.

Wording notes: N1 (TC⁺ variable s = |e − e0|); N2 (SC-S1 root condition |e| < C − 1, i = 1..5); N3 (strict only for
exact sups); N4 (exact-source idealization labelled); N5 (per-box containment replaces grid-lower check); N6 (stated);
N7 (independent float quadrature H1b 1200/1200, max gap 2e-13); N9 (CR-3 transport slack T without w_g; e_J/e0 shown);
N10 ("attained" → "supremum"); N11 (DRP-0 uses certified s_1^cert); N12 (DRP-0 result-free; DRP-1 outcome-adaptive,
frozen predicate); N13 (harness labels); N14 (RSO non-cosmetic iff ψ ≠ ‖ψ‖ μ-a.e.); N15 (sup_e μ_{a,e}(ψ)); N17
(re-run log in PROGRESS); N18 (pointer to committed per-cell share removed from RESIDUAL §1). Commit subject of
6d0f0615 ("strictly positive", "result-free policies DRP-0/1") cannot be edited; superseded by the corrected wording.

Route states after repair: unchanged except B2 narrowed to true scope, B2c added THEORY_ONLY, G6 PASS for mathematics.
**FREEZE_READY: no, for every route.**

## D. Route dispositions and blockers — consolidated list

| route | disposition | blockers |
|---|---|---|
| SC | VALIDATED_NON_TARGET; not killed | payloads never serialized (0/326); U1 host (numpy, python-flint absent locally and on permitted worker, C6-N1); U2 P3 admissibility (C6 Condition 10: SC is a new scientific quantity derived from P3 records); U3 floor extension (closure-only under floor r2); SC-4w interval-drift enclosure not implemented; certificate configuration calibration only synthetic; certified gain not guaranteed |
| CR | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED (outcome-adaptive) | NEW_REAL (new K1 midpoint records; guard DENY; explicit authorization); U1; new provenance chain (tail records are P3; C6 Condition 10 / U2); U3 |
| B2 | REFUTED within fixed-(g_hi, L, U) family | — (C5 killed B2 as NEW_REAL; CR-2 is MATH within the fixed family) |
| B2c | THEORY_ONLY, unevaluated | closure-only under floor r2 (U3) |
| RSO-C4 | VALIDATED_NON_TARGET; structurally narrow | as RSO-P |
| RSO-P / RSO-PM | VALIDATED_NON_TARGET; real use BLOCKED | payloads; per-box residual ranges discarded by frozen certifier; SC composite (for RSO-P); U1; U2; supersolution certificate needs kernel evaluation at the cell's drift block (quarantined); U3 |
| RSO-LR order 1 | VALIDATED_NON_TARGET (single drift) | block-uniform version absent; U1–U3 as above |
| RSO-LR order 2 | THEORY_ONLY | not implemented |
| TPT (E stream) | referenced | see TPT digest (BLOCKED at tail, incident 01) |
All: CLOSURE-ONLY under floor r2; FREEZE_READY no.

## E. PROGRESS.md (log), condensed
* Every script stdlib only, `Q.install_import_guard()`, `guard_drift` at drift entry points, `Q.log_execution` per
  substantive run. New target evaluations 0; target-equivalent proxies 0.
* Done: core (`d309_core.py`: exact TC pipeline, dual φ^(j) paths); SC on FSM (60 cases, identities exact, ladder
  holds, r1 premise checks 0/300); Hermite (1200/1200 vs C11, r1 H1b 1200/1200, H3 per-box containment 0 violations);
  certificate stability (Taylor-form 1.19–1.44× grid lower bound; r1 containment 0 genuine, 4 planted defects inside
  `box_upper_tf`); RSO (certificates verified twice; r1 controls a1/a2, c1–c3, e; b, d genuine); cover (identities
  exact; clauses sound; scaling exponents → j+1; r1 mutants on 140 records; B2 − TPT = 0 an implementation identity);
  SC-T (identity 48/48, bound 48/48, comparator 48/48); scan (0 findings in the seven D_309 files; 1 elsewhere,
  `streams/A_306/a306_reproduce_A.py`, not touched).
* Rule S8 received after code/validation, before documents; no file places a route factor next to a committed tail
  share/factor/margin; committed tail history kept in separate "History (quoted, no route factor)" sections.
* Repair r1 re-run log (N17): `d309_hermite.py` (B1/N5/N7/N8), `d309_hermite_tf.py` (same for box_upper_tf),
  `d309_supnorm_fsm.py` (B1/test power/N4), `d309_rso.py` (B1/N8), `d309_cover.py` (B1/B3/N12/N13), `d309_sct.py`
  (B1 comparator relabel). Earlier r0 re-runs of `d309_rso.py` (3×) and `d309_cover.py` (2×) for dual verification,
  LR structural control and NC fixes; none changed a declared validation set.
