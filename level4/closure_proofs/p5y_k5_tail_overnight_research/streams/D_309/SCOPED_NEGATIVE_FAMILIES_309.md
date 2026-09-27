# Scoped negative families for CUSUM m = 5 cell 309

Status: RESEARCH, target-free. Nothing below was computed; every tail number is quoted from a committed file with
file:line (paths relative to `level4/closure_proofs/`). Rule S8: this document contains **no** new-route gain factor.
Section 1 is committed history only; section 2 argues the difference of the new routes from those families in purely
structural terms.

## 1. History (quoted, no route factor)

### F1 — uniform-A0 atom-constant family (REFUTED WITHIN SCOPE)

* **Family** (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:196-199`): every triple
  `(A0, A1, A2)` whose `A0` is a valid uniform order-0 bound on the closed cell, consumed through the frozen TC-T and the
  frozen K5-B direct clause, at the frozen measurement inputs, at cell 309, `m = 5`.
* **Excluded from the family by the gate's own `does_not_cover`** (`:201-203`):
  * residual-specific (non-norm-only) order-0 bounds;
  * any change to TC-T, to the K5-B clause or to the frozen measurement inputs;
  * order-3 candidates of F.
* **Binding restatement.** C4 Condition 1 (`:522-526`) is superseded by the C5-T restatement
  (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md:357-363`):
  * against the frozen measurement inputs and the C5-T transport, no uniform-A0 supply closes 309 for any `A1, A2 ≥ 0`;
  * "It is not a statement that cell 309 is unclosable".
* **Floor versus ceiling.**
  * C5-T critical A0: 3.266416 (`p5y_k5_tail_c7_e2_lambda309/README.md:20`).
  * C7 floor: `Λ₃₀₉ ≥ 3.586306094` (`README.md:15`).
  * Lemma SM(d) makes `A0 ≥ Λ` necessary (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:51`).
* **C3 knockout.** `A1 = A2 = 0` still leaves 309 open
  (`p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md:351`;
  `p5y_k5_tail_c3_closure/OPEN_NOTES_DISPOSITION_C3.md:22`).
* **C8 wording.** The refutation holds "within the atom-constant family, at the committed sup norms"
  (`p5y_k5_tail_c8_operator_feasibility/README.md:63-71`).
* **C4 Condition 5.** The margin exists only by virtue of the sup-over-closed-cell quantifier and the left-endpoint
  evaluation (`C4_ADJUDICATION.md:543-547`).

### F2 — two-input transport family (EXHAUSTED; C5)

* **Family** (`C5_ADJUDICATION.md:165-167`): every bound on `max_cell g` derivable from exactly (i) `g_hi` and (ii) a
  whole-cell `[H_lo, H_hi]`, on a cell in `e > 0`.
* **Scope** (`:175-181`). The result exhausts "the transport, not the cell". It "says nothing" about:
  * improving `g_hi`;
  * improving the `R''` enclosure;
  * "a transport consuming a third certified input".
* **Scope limits** (`:185-189`; Condition 8, `:597-599`):
  * the witness is an arbitrary absolutely continuous function, not a resolvent-type R;
  * `x_lo > 0` is required.
* **Outside F2 by that sentence:** `streams/E_assembly/THEOREM_TPT.md`. It consumes a third certified input, the TC
  profile. Its Proposition TPT-O makes TPT optimal within the three-input family.

### F3 — C7 E2 family (Wald/overshoot lower bounds on Λ₃₀₉)

* **Ceiling.** The family ceiling is 4.679910340, below the certified A0 4.867216117
  (`p5y_k5_tail_c7_e2_lambda309/README.md:107-113`).
* **What going further needs** (`:115-117`): a bound on `E[τ] − E[τ′]`, or on the gap between the sup over the cell and
  the value at `e_lo`.
* **Direction.** The family yields **lower** bounds on Λ, so it can only strengthen the exclusion. Its scope is 309 only.

### F4 — C1 atom deflation at the tail (MARGINAL)

* The need falls 2.252903 → 2.101597, a 6.716 % fall against a 10 % threshold, so the class is MARGINAL
  (`p5y_k5_tail_operator_registry/README.md:26-30`).
* Deflation buys 1.10–1.13× on A0 and makes A2 worse (`:24-25`).
* Ā is inert (`:31`).

### F5 — Campaign B route T2: a real order-3 candidate at the tail

The USEFUL class is refuted (`p5y_k5_m5_tail_closure/README.md:22-29`; `phase_c/EXECUTION_DECISION.md:57-100`):

| input scenario | NOMINAL | CONSERVATIVE |
|---|---|---|
| the audit's own inputs | 3/5 | 0/5 |
| the Campaign-A order-3 scale | 0/5 (INFEASIBLE) | 0/5 |

* **The single hinge** (`EXECUTION_DECISION.md:81-86`): the centre motion, with `|Ĝ(a)| = 0.681·s_G`.

### F6 — C8 routes R1 (clipping gap) and R2 (cell uniformization): zero closure leverage

* Both routes raise Λ, and raising a floor cannot lower Γ.
* Perfect information in either changes Γ by exactly 0 (`p5y_k5_tail_c8_operator_feasibility/README.md:36-41, 74-77`).

### F7 — C5 route-search verdicts relevant to this stream

All from `p5y_k5_tail_c5_exhaustion/phase_3/C5_ROUTE_SEARCH.md`.

**Killed:**

| route | line | verdict |
|---|---|---|
| **B2**, split the clause without new records | `:50` | "R and D are certified at e0 only; transporting them to a sub-midpoint costs exactly what the split saves" |
| **D2**, sign-awareness alone | `:52` | an identity |
| **A4**, reuse the cell-0 order-3 probe | `:46` | no certified transport across the range |

**Not refuted:**

| route | line | status |
|---|---|---|
| **A1**, tighten `sup{F,D,H}` | `:43` | DATA |
| **A3**, cancellation in the order-3 identity | `:45` | DATA |
| **B1**, cover refinement | `:49` | NEW_REAL |

### Levers C5/C8 list as outside F1 (quoted; no route attached)

* **Six source-supply levers**, cheapest `all_four_together` at 0.6076 %
  (`p5y_k5_tail_c5_exhaustion/evidence/forecast/C5_FORECAST.json:24-32`;
  `p5y_k5_tail_c8_operator_feasibility/ERRATUM_C8_GATE.md:39-44`).
* **Three oracles** ("ρ halved", `sup{F,D,H} → 0`, `f_G → 0`): C5 Condition 10 (`C5_ADJUDICATION.md:606-613`).
* **Caveat on the "ρ halved" oracle** (`p5y_k5_tail_c5_exhaustion/code/c5_common.py:85-86`):
  * it scales only the TC-T Taylor ρ (`meas["rho"]`);
  * the transport factor ρ·x_hi and `g_hi` are left unchanged;
  * it is therefore **not** a model of a cover refinement (see `COVER_REFINEMENT_309.md` §3).

## 2. Why each new route of this stream lies outside these families (structural; no numbers)

A route is **cosmetic** relative to a family if its certified output equals, for every input, a bound the family
already produces, possibly after a change of notation or reparameterization. Each claim below is a mathematical
statement about the certified objects, with its proof location.

### SC — composite-sup premise supply (`SUPNORM_THEOREM.md`)

SC replaces the premise `f_G ≥ ‖φ'''(e0)‖`, and optionally `Env4 ≥ sup_C ‖φ⁗‖`, by a certified sup of the actual
function. The Leibniz triangle/submultiplicativity product is no longer used.

* **vs F1.** SC leaves `A0`, `A1`, `A2` untouched and changes a TC-T premise supply. That is exactly C4's excluded item
  "any change to TC-T … or to the frozen measurement inputs" (`C4_ADJUDICATION.md:202-203`).
  * **Not a reparameterization of A0.** Such a rescaling would be `A0' = A0·(f_G^SC / f_G)` on the `ρ f_G` term only.
    That is not a uniform order-0 bound: it can violate Lemma SM(d), because it is below Λ whenever the ratio is small.
    So SC's effect is not representable inside F1.
* **vs F5 (T2).** SC keeps `Ĝ := 0`, so `s_G = |Ĝ(a)| = 0` (TC-T (P2′)). It proposes no order-3 candidate and no
  order-3 producer run, and T2's hinge (the centre motion `ρ|Ĝ(a)|`) is absent. SC measures the **zero-candidate**
  residual exactly instead of by the triangle inequality.
* **vs A1 (sup-norm tightening, C6).** SC does not change any `s_X`, so every identity-gated field stays byte-identical.
  C6's "a faithful replay … delivers exactly zero of A1's gain, by construction" concerns `s_X` and does not apply. SC
  adds a **new** quantity computed from the same payloads.
* **Relation to A3.** SC is C5's route A3 ("exploit cancellation in the order-3 identity", DATA-blocked) made precise:
  * a theorem (SUPNORM §2);
  * a strictness proposition (§4);
  * a computable certificate (§5).
* **Why the gain is not the (removed) source term.** Proposition SC-T (SUPNORM §3) shows the composite equals
  `‖(I − K)F_r'''(e0)‖` up to candidate-error terms, and the surrogate is its Leibniz triangle bound. The gain is the
  Leibniz slack, a structural quantity.

### CR — real cover refinement (`COVER_REFINEMENT_309.md`)

A real refinement uses **new certified midpoint records**: new `g_hi`, new TC premises and a new cell for the uniform
quantifiers.

* **vs F2.** Each record adds certified inputs beyond `(g_hi, [H_lo, H_hi])`, so the route is outside F2 by C5's own
  scope sentence (`C5_ADJUDICATION.md:179-180`).
* **vs B2.** B2 splits without new records. COVER §4 proves (Proposition CR-2, a corollary of TPT-O) that such a
  split is dominated by TPT **within the fixed-(g_hi, L, U) family**. (Repair r1, review B2/B3: the r0 claim that the
  kill was "validated with exact zero difference" is withdrawn; that difference is 0 by construction of the
  implementation. The r0 wording "B2's kill is confirmed and sharpened" overreached: C5 killed B2 as NEW_REAL.)
  * A record-free split that **re-certifies the operator constants on sub-segments** (lever B2c) is outside that
    family and is unevaluated.
  * A real refinement is the complement of B2.
* **vs F1.** Refinement changes the cell, hence:
  * the domain of the "uniform on the closed cell" quantifier;
  * the constants over it.

  F1 is stated for the frozen cell. C4 Condition 5 (`:543-547`) records that the exclusion depends on that quantifier
  and on the left-endpoint evaluation.
* **Rejected cosmetic variant.** Scaling only the TC-T Taylor ρ while keeping `g_hi` and the transport ρ·x_hi (the C5
  oracle's knob, `c5_common.py:85-86`) is **not** a refinement. It models neither the new midpoint value nor the
  shorter transport. COVER §3 treats it only as a mis-model.

### RSO — residual-specific order-0 bounds and their derivative extensions (`RESIDUAL_SPECIFIC_309.md`)

The route bounds `|(R_e φ)(a)|` by `(R_e ψ)(a)` for a pointwise majorant `ψ ≥ |φ|`, certified by a supersolution
`v ≥ ψ + K_e v`.

* **vs F1.**
  * **Collapse lemma** (RSO §2.3): for constant `ψ ≡ c` the certificate is `c` times an ARL certificate `Ā`, i.e. a
    member of F1.
  * **Characterization** (RSO §2.2): the route leaves F1 **iff** ψ is non-constant on the support of the atom's
    occupation measure. The gain over the best member of F1 is exactly `‖ψ‖/μ_a(ψ) ≥ 1`, where `μ_a` is the normalized
    expected occupation measure up to τ.
  * F1's bounds are norm-only by definition (`C4_ADJUDICATION.md:201-203` names non-norm-only bounds as excluded).
* **vs F3 / F6.** RSO produces **upper** bounds on atom functionals of specific residuals. It never raises a floor, so
  the zero-leverage argument of R1/R2 does not apply.
* **vs F4 (C1).** C1's deflation is a norm-only atom-constant supply, a member of F1.
* **The RSO-PM and RSO-LR derivative extensions** bound `|(∂R f)(a)|` and `|(∂²R f)(a)|` for `|f| ≤ ψ`, pointwise in ψ.
  With constant ψ they reduce to atom constants of norm type, i.e. members of F1. With non-constant ψ they are outside
  F1 for the same reason as RSO-0.

### Assembly (E stream)

`streams/E_assembly/THEOREM_TPT.md` is outside F2 by C5's own scope sentence, as quoted in §1 F2. This stream uses TPT
as its transport and does not restate it.
