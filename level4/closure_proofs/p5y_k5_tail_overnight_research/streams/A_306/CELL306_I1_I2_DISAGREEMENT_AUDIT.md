# Cell 306 — why do implementations I1 and I2 disagree? (Stream A audit)

**Status:** RESEARCH, read-only with respect to cell 306. No Γ, margin, enclosure, radius, x-eff factor, operator
constant or any other new quantity was computed for any CUSUM m = 5 tail cell (305–309). The one computation that
touches 306 data is a HISTORICAL_READ reproduction: each supply's **own** committed constants are pushed through
Lemma Dv′ r2 and compared for exact equality with the committed atom constants (`audit/a306_reproduce_A.py`, ledger
class HISTORICAL_READ). It emits booleans and branch labels only. No mixing, no perturbation, no Γ.

**Layout rule (PREAMBLE S8).** Part A quotes committed cell-306 history and attaches no route or non-target factor
to it. Part C reports non-target mechanism numbers and quotes no cell-306 number. Part D (classification) is
qualitative and cites Parts A–C by section; it multiplies, ranks or compares no Part-C number against any Part-A
number. Nothing written before S8 arrived violated this layout (checked; see `PROGRESS.md`).

Paths are relative to `level4/closure_proofs/` unless stated; `file:N` is line N in the worktree at the time of
reading (branch `p5y-k5-tail-overnight-306-309`).

Contents:
* Part A — committed history (quotes only)
* Part B — axis-by-axis audit and discrepancy register (each item classified, with file:line evidence)
* Part C — non-target mechanism evidence (summary of `mechanism/`)
* Part D — classification of the disagreement, defects flagged, what remains unknown

---

## Part A — Committed history (quotes only; no route factor attached)

A.1 **Sealed facts** (not recomputed): Γ(5,306; S_I1) = −0.030469257709306738
(`p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json`:47, reproduced as the C12-R2 control);
Γ(5,306; S_I2) = +0.005159101140006536 sealed once
(`p5y_k5_tail_c12r2_cell306_adoption/evidence/execution/C12R2_CELL306_RESULT.json`:129 region, `target.evaluated.Gamma`);
CELL306_NOT_ADOPTED because F1′(d) needs Γ < 0 under EACH implementation's own supply
(`p5y_k5_tail_floor_r2/FLOOR_R2_SPECIFICATION.md`:62-69; `p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md`:2-7).

A.2 **The two constant sets and the frozen N9 classes** (committed; quoted from
`p5y_k5_tail_c11r_n9_statement_alignment/adjudication/ADJUDICATION_C11R_N9.md`:27-32 and
`p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json`:23-57):

| constant | direction | statement class | I1 (C2 registry) | I2 | class (frozen rule) |
|---|---|---|---|---|---|
| C_T | upper | EQUIVALENT | 5.829887954 | 6.858 (+3.7e-97, outward-rounded record) | AGREES (ratio 1.176351939) |
| τ | upper | EQUIVALENT | 5.169819806 | 3429/500 | AGREES (1.326545268) |
| Ā | upper | EQUIVALENT | 7.912416712 | 3429/500 | STRONGER (0.866738981) |
| D_lo | lower | STRONGER (premises FEWER) | 0.844492286 | 101/200 | AGREES (0.597992437) |
| D1 | upper | EQUIVALENT | 0.455295982 | exact rational (C11RD_COMPARISON.json:27) | STRONGER (ratio_float 0.45362884480385873) |
| D2 | upper | EQUIVALENT | 5.416355434 | exact rational (C11RD_COMPARISON.json:44) | STRONGER (ratio_float 0.0557333083728129) |

A.3 **Committed read-offs used below** (string identities, no arithmetic): the committed target A0 string of S_I2 is
`"3429/500"` (C12R2_CELL306_RESULT.json:125), equal to the committed I2 Ā and τ strings
(C11R_COMPARISON.json:75, :171); S_I2 provenance I2/I2/I2 and S_I1 provenance C2/C2/C2 (C12R2 result :30-36,
:138-143; C2_D5_FORECAST.json:61-64). C2 docstring: "Abar_eff = tau/D_lo on all five cells"
(`p5y_k5_tail_c2_closure/code/c2_refined_registry.py`:16-17).

A.4 **Committed statements about why values differ** (quoted, not re-derived):
ROUTE_AUDIT_R1 lists "Which constants drive the I1/I2 disagreement" as UNKNOWN, "not attributed in committed
evidence" (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`:225); review note N6: "the independent tau … is exactly the
K_e bound … weak corroboration of tau's Khat_e-specific tightness"
(`p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_COMPARISON.md`:214); C11RD adjudication review N2:
"an unsound independent certifier would also show up as STRONGER. D2's ratio of about 0.056 is a large gap"
(`p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md`:261-262).

A.5 **Reproduction result** (`validation/A306_HISTORICAL_A_REPRO.json`, producer `audit/a306_reproduce_A.py`,
verdict PASS, 12 checks + 3 negative controls):
* Lemma Dv′ r2 (THEOREM_AD.md:86) on the I1/C2 constant set reproduces C2's committed `A_exact` **exactly**
  (`checks.I1_C2_equals_C2_forecast_A_exact`, a306_reproduce_A.py:117) and the C12-R2 control `A_exact` exactly;
  the C1 and C2 floats match `supplies`.
* Lemma Dv′ r2 on the I2 constant set — with C_T = C11R's **outward-rounded record**, τ = Ā = 3429/500, D_lo = 101/200,
  D1/D2 from C11RD — reproduces the sealed S_I2 `A_exact` **exactly** (`checks.I2_equals_C12R2_target_A_exact`,
  a306_reproduce_A.py:125).
  So the sealed target used the outward-rounded C_T record in the consumer, as floor r2 §6 binds it
  (FLOOR_R2_SPECIFICATION.md:143-145), while C11RD's D1/D2 propagation used the exact 3429/500 (Part B, item B-H2).
* Binding eff branch inside each supply: I1/C1 and I1/C2 → **τ/D_lo**; I2 → **Ā**
  (`branches`, a306_reproduce_A.py:78). The I2 branch is structural: τ_I2 = Ā_I2 (a306_reproduce_A.py:135) and
  D_lo < 1, so τ/D_lo > Ā for every admissible D_lo.
* Negative controls (a306_reproduce_A.py:143-153): a committed string altered by one unit in the last place is
  detected; a mixed-provenance constant set is refused before any arithmetic; a C1 value compared with the C2
  record is detected as a mismatch.

---

## Part B — Axis-by-axis audit

Part B contains no non-target number and no route factor. Classes: EXACTLY_EQUIVALENT / REPRESENTATION_ONLY /
PROOF_STRENGTH_DIFFERENCE / IMPLEMENTATION_SLACK / SUPPLY_DIFFERENCE / ASSUMPTION_DIFFERENCE / POSSIBLE_DEFECT /
UNKNOWN. I1 = `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py` (+ registries C1, C2); I2 = C11R
(`p5y_k5_tail_c11r_n9_statement_alignment/code/c11r_idrift.py`, `c11r_boxdata.py`, on C11's `c11_certifier.py` and C7's
`c7_gaussian.py`) + C11RD (`p5y_k5_tail_c11rd_d1d2_extension`).

### B.1 Verification of the key citations of `SCR/graph_B_operators.md` §(b)

Each row was re-read in the source at the cited lines by this stream.

| graph_B claim | source re-read | result |
|---|---|---|
| I2 F_D: u = 101/200 + (21/250) m, Khat_e, depth 5, 32 panels, whole block, premises [] | C11R_RUNS.json:3-42 | confirmed |
| I2 F_H and F_K: the same weight 3429/500 − (1113/1000) m; F_H `atom_removed_argument` true, F_K false; identical margin and w_min | C11R_RUNS.json:43-120 | confirmed |
| selector mu = 2^-60, grid 1000, b_max 4, beta_max 1 | C11R_POLICY.json:389-395; C11R_RUNS.json:200-230 | confirmed |
| I2 τ = w(a), C_T = sup over cover of w | c11r_certificate.py:85, 162-168 | confirmed |
| C_T "3429/500 + 99/2.67e101, outward rounding"; τ and Ā equal because the binding box lies outside the atom window | REVIEW_C11R_COMPARISON.md:71, 85-86, 214 | confirmed |
| six-constant table with ratios | ADJUDICATION_C11R_N9.md:27-32 | confirmed |
| I1 original values = REGISTRY_C2 cell-306 row (max/min over nine sub-rows; Ā single ARL record) | C11R_COMPARISON.json `original_value` strings found verbatim at REGISTRY_C2.json:181-185, 347 (text search by this stream); REVIEW_C11R_COMPARISON.md item 17 | confirmed |
| I1 D-statement conditional on (C_T, τ) | taboo_certify.py:348-349; C11R_N9_STATEMENTS.json:3-18 | confirmed |
| C11RD premise C_T = τ = 3429/500 (exact), κ₁ = 2φ(0), κ₂ = 4φ(1); 4 sub-blocks; e-Taylor candidates; D1_j, D2_j propagation | C11RD_FREEZE_R1.json:67-90, 124-154 | confirmed |
| Theorem 5 (C11RD error propagation), candidates do not affect soundness | D1_D2_DERIVATION.md:162-191 | confirmed |
| I1 ladders: taboo (6/5, …) β = 0; ARL (5/4, …) β = 2; first certifying rung taken | c2_refined_registry.py:53-54, 95-99, 126-128 | confirmed |
| I1 cell artifact: candidates from a float solve at e0, residual at e0, ρ·env widening, D_lo = D_mid_lo − ρ·D1 | taboo_certify.py:274-281, 300-337 | confirmed |
| floor r2 supplies, no mixing, STRONGER never substitutes | FLOOR_R2_SPECIFICATION.md:54-83, 90-100, 123-127 | confirmed |
| the combined S_I2 A0 equals the I2 Ā string | C12R2_CELL306_RESULT.json:125; C11R_COMPARISON.json:75 | confirmed, and now also reproduced exactly (A.5) |

### B.2 The axes

**(1) Definition equivalence.** Both implementations define K̂_e by removing the atom window z ∈ [m − K, K − p]
(both arms clamp) from the alarm-free window [m − C, C − p]: I1 subtracts the frozen Pair kernel's "origin" piece
(taboo_certify.py:146-156), I2 skips the atom piece in `kernel_apply_iv` (c11r_idrift.py:183-196, 234-244). The
proposition, kernel, direction and drift block agree for all six constants (C11R_COMPARISON.json:83-92, 107-116,
155-164, 179-188; C11RD_COMPARISON.json:35-39, 52-56). → EXACTLY_EQUIVALENT (definitions).

**(2) Constant provenance.** C_T and τ: I1 = max over nine sub-blocks of degree-20 taboo supersolutions at the first
certifying α (c2_refined_registry.py:95-106, 159-166); I2 = one whole-block linear weight (C11R_RUNS.json:43-81).
Ā: I1 = one degree-12 ARL supersolution α = 5/4, β = 2 (c2_refined_registry.py:126-127); I2 = the same linear weight
on K_e (C11R_RUNS.json:82-120). D_lo: I1 = min over nine conditional cell artifacts; I2 = one unconditional linear
sub-solution. D1, D2: I1 = max over nine cell artifacts; I2 = max over four C11RD sub-blocks.
→ REPRESENTATION_ONLY for the aggregation form ("for every e in the block" either way); the value difference it
produces is IMPLEMENTATION_SLACK (see (13)).

**(3) Interval enclosure.** I1: Arb balls at 256 bits (taboo_certify.py:56), Bernstein range on the frozen
reachable cover at depth 2 for block certificates (taboo_certify.py:220-224; depth `2` at c2_refined_registry.py:96)
and **depth 0** for the residuals of the cell artifacts (taboo_certify.py:284, 296-297; the C2 call at
c2_refined_registry.py:109 passes no depth). I2: exact rationals with 2^-320 outward rounding of Gaussian values
(c7_gaussian.py:27, 37-43), box/panel bounds on a 363-box cover with 32 u-panels (c11r_idrift.py:275-316;
c11r_boxdata.py:166-234). → REPRESENTATION_ONLY for soundness (both outward); IMPLEMENTATION_SLACK for value.

**(4) Normalisation.** Candidate bases differ (I1: Chebyshev payload on [0, H]², taboo_certify.py:84-90; I2: raw
monomials). Probability normalisation is the same density φ(z + e) on the same window with mass balance
k_a + h₁ + K̂1 = 1 (THEOREM_AD.md:19-21; c11r_idrift.py:263-269). → REPRESENTATION_ONLY.

**(5) Truncation.** I1: order-120 φ Taylor series with doubled truncation allowances (taboo_certify.py:136-160) and
an affine-in-(e − e_c) block expansion with a κ₂δ²/2·sup w remainder checked at both ends (taboo_certify.py:214-226;
THEOREM_AD.md:171-173). I2: the drift is carried as an interval, no e-truncation for C_T/τ/Ā/D_lo
(c11r_idrift.py:8-23); Gaussian series with run-time-checked remainders (c7_gaussian.py:10-23); C11RD Taylor models
of order 6 with enclosed remainders (C11RD_FREEZE_R1.json:156-166). → REPRESENTATION_ONLY.

**(6) Rounding / exact arithmetic.** I1 converts Arb ball ends to exact rationals (taboo_certify.py:73-79). I2 is
exact; its C_T target record is an interval evaluation of w over the cover, 3.7e-97 above the exact sup 3429/500,
which C11RD used as its premise (C11RD_ADJUDICATION_REVIEW.md:255-259). The reproduction (A.5) shows the sealed S_I2
used the record, and C11RD's D1/D2 used the exact sup. Both are valid bounds on ‖Ĝ_e‖ because sup_R(A − B m) = A
exactly for B ≥ 0. → REPRESENTATION_ONLY.

**(7) Proof strength.** D_lo: I1 is conditional on (C_T, τ) of its own sub-block (taboo_certify.py:348-349), I2 is
unconditional (c11r_boxdata.py:25-31) → PROOF_STRENGTH_DIFFERENCE in favour of I2. This difference **cannot** be what
makes I2's D_lo value smaller: the maximal bounded sub-solution of u ≤ h₁ + K̂_e u is d itself (d = Ĝ_e h₁ satisfies the
equation, and K̂_e^n → 0 because K̂_e 1 ≤ 1 − h_min), so the unconditional route can in principle reach D_e. Part C
(control NC1) confirms this mechanically on a discretised operator. All other statements are EQUIVALENT.
→ the D_lo proof-strength difference is real but value-neutral in principle.

**(8) Supply construction.** S_I1 = min{G, C1, C2}, S_I2 = min{G, I2}, componentwise (FLOOR_R2_SPECIFICATION.md:90-94).
The reproduction confirms C2 wins every field of S_I1 and I2 wins every field of S_I2 (A.5), so each supply is in
effect one constant set pushed through Lemma Dv′ r2, and G is inert in both. The eff branch differs: τ/D_lo in I1,
Ā in I2 (A.5). In I2 the branch is forced by structure: the one weight certifies both τ and Ā, so τ_I2 = Ā_I2 and
τ_I2/D_lo ≥ Ā_I2 for any D_lo ≤ 1. Consequence: in S_I2, τ is inert and D_lo enters **only** through
δ₁ = D1/D_lo and δ₂ = D2/D_lo in A1 and A2; in S_I1, Ā is inert and D_lo enters A0, A1 and A2.
→ SUPPLY_DIFFERENCE (branch), caused by the IMPLEMENTATION_SLACK of I2's τ (see (13)).

**(9) Consumer semantics.** One consumer (C2's frozen chain), common κ₁, κ₂ (deflated_consume.py:55-56), identical
non-constant inputs (K1 stack, Lemma G inputs, TC-T premises, `cells.json`): FLOOR_R2_SPECIFICATION.md:95-100 and one
`input_sha256` block for both evaluations (C12R2_CELL306_RESULT.json `input_sha256`). Both sets pass the consumer
validation τ ≥ 1, C ≥ τ, D_lo > 0, Ā ≥ 1 (a306_reproduce_A.py:75-77). → EXACTLY_EQUIVALENT.

**(10) Hidden assumptions.**
* B-H1: I1's D_lo, D1, D2 are conditional on each sub-block's own (C_T, τ), discharged by that sub-block's taboo
  certificate (c2_refined_registry.py:104-109). → ASSUMPTION_DIFFERENCE (discharged).
* B-H2: C11RD's premise is the exact 3429/500; the consumer uses the outward-rounded record. → REPRESENTATION_ONLY.
* B-H3: I2's F_D needs h_min > 0 and u ≥ 0, certified in the same pass (c11r_boxdata.py:213-234; review item 20
  quotes h_min ≈ 7.29e-5). → ASSUMPTION_DIFFERENCE (discharged).
* B-H4: both need ‖∂ⁿK̂_e‖ ≤ κ_n (Lemma K, THEOREM_AD.md:23-30), I1 via `opnorms.kernel_norm` (taboo_certify.py:291),
  I2 via C7 enclosures of 2φ(0) and 4φ(1). → EXACTLY_EQUIVALENT premise (common-mode theory).
* B-H5: the reachable-set specification is I1's frozen reachable cover versus I2's R spec (c11_certifier.py:189-197).
  The statement table classifies the domain EQUAL, but byte-level identity of the two covers' closures was not
  re-verified here. → UNKNOWN (recorded, not suspected).
* B-H6: I1's provenance residual N10 (no build host, toolchain or precision recorded) is OPEN
  (FLOOR_R2_SPECIFICATION.md:141). → UNKNOWN.

**(11) Bound decomposition (committed only).** Lemma Dv′ r2 (THEOREM_AD.md:86): A0 ← eff; A1 ← eff·(κ₁C + δ₁);
A2 ← eff·(2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂). Constant → component map:
* **I1** (branch τ/D_lo): τ → A0, A1, A2; D_lo → A0, A1, A2; C_T → A1, A2; D1 → A1, A2; D2 → A2; Ā → none.
* **I2** (branch Ā): Ā → A0, A1, A2; C_T → A1, A2; D_lo → A1, A2 (through δ₁, δ₂ only); D1 → A1, A2; D2 → A2; τ → none.

TC-T places A0 on p2, A1 on 2·p1 and A2 on p0 (THEOREM_TCT.md:124-126). The only recomputation is the exact
reproduction of A.5. No per-term value was emitted, as the brief and the quarantine require.

**(12) Does one implementation prove a genuinely stronger theorem?** No, not in any sense that bears on Γ.
* Five statements are EQUIVALENT.
* The one stronger statement (I2's unconditional D_lo) carries the weaker value, and its strength does not force that
  value (see (7)).
* D1, D2 and Ā are STRONGER in value only, not in statement.
* The two supplies bound the same quantity, sup over the block of E_a[τ], through different admissible branches of
  Lemma Dv′ r2. At exact operator values the Ā branch is never worse than the τ/D_lo branch, because
  sup τ_a / inf D ≥ sup(τ_a/D) = sup E_a[τ] (Lemma SM(d), THEOREM_AD.md:51). So branch choice is not a theorem
  difference either.

**(13) Avoidable slack.**
* **I1:**
  * (i) First-rung α ladders: τ and C_T come from w = (6/5)·g, and Ā from w = (5/4)·g + 2, where g is a float solve at
    the block centre (taboo_certify.py:190-197; c2_refined_registry.py:53-54). C9's committed counterfactual for a
    different cell documents unused margin at the first rung. It is labelled COUNTERFACTUAL_PROJECTION
    (`p5y_k5_tail_c9_e1_cell307/evidence/phase4/C9_ALPHA_LEVER.json`:2-8).
  * (ii) Degree-20 global polynomial candidates absorb the kinks at p + m ∈ {1, 2, 3, 4} in their residuals
    (D1_D2_STATEMENT_AUDIT.md:125-129).
  * (iii) Residual ranges at subdivision depth 0 (taboo_certify.py:284, 297).
  * (iv) First-order ρ·env widening (taboo_certify.py:317-318). I1's own C1 → C2 partition refinement changed its D1
    and D2 strongly (C1_OPERATOR_EXTENSION.md:34 versus ADJUDICATION_C11R_N9.md:31-32), which shows these two
    constants are dominated by partition-dependent residual widening rather than by the candidate's atom value.
  * (v) Block decoupling in τ/D_lo: max-τ and min-D_lo are taken over sub-blocks independently
    (c2_refined_registry.py:159-166).
  * All five → IMPLEMENTATION_SLACK.
* **I2:**
  * (i) The upper family w = A − B·m is p-flat, so its τ is at least its whole-kernel value and τ = C_T = A. This is
    review note N6 (REVIEW_C11R_COMPARISON.md:214), and Part C shows it is a property of every p-flat family.
  * (ii) The lower family u = α + β·m is linear.
  * (iii) The box/panel discretisation at depth 5, 32 panels. The atom skip is "nearly inert"
    (REVIEW_C11R_PREFREEZE.md:189).
  * (iv) The certificate is single and whole-block, with no drift sub-blocks.
  * (v) The grid rounding of the selector (1/1000; C11R_POLICY.json:393).
  * All five → IMPLEMENTATION_SLACK. The source itself records (ii) as a known limitation: "Richer families would give
    tighter lower bounds; that is out of scope" (c11r_boxdata.py:39-41).

**(14) A common stronger theorem?** At the level of statements, yes. The true constants of the block lie in
two-sided certified intervals, and any sound implementation's constant must lie on the correct side of them.
Certificates can also be separated from verifiers, so that one certificate set is verified by two independent
verifiers and yields one supply. This is developed as the common-theorem route in `common/THEOREM_CV.md`. It does
not by itself improve any value: it removes the two-supply structure and makes "STRONGER" refutable.

### B.3 Discrepancy register

| id | discrepancy | I1 evidence | I2 evidence | class |
|---|---|---|---|---|
| X01 | K̂_e construction (origin piece subtracted vs atom piece skipped) | taboo_certify.py:146-156 | c11r_idrift.py:183-196, 234-244 | EXACTLY_EQUIVALENT |
| X02 | drift block | REGISTRY_C2.json:195-199 | C11R_RUNS.json:25-28 | EXACTLY_EQUIVALENT |
| X03 | consumer, κ in the consumer, non-constant inputs | FLOOR_R2_SPECIFICATION.md:95-100 | same; C12R2 `input_sha256` | EXACTLY_EQUIVALENT |
| X04 | κ inside certificates (`opnorms.kernel_norm` vs C7 enclosures of 2φ(0), 4φ(1)) | taboo_certify.py:215, 291 | C11RD_FREEZE_R1.json:143-146 | REPRESENTATION_ONLY |
| X05 | reachable set: frozen reachable cover vs R spec | taboo_certify.py:222-224 | c11_certifier.py:189-197 | REPRESENTATION_ONLY (byte-level identity UNKNOWN, B-H5) |
| X06 | arithmetic: Arb 256-bit vs exact rationals and C7 2^-320 | taboo_certify.py:56, 73-79 | c7_gaussian.py:27, 37-43 | REPRESENTATION_ONLY |
| X07 | e-handling: affine expansion + κ₂δ²/2 remainder vs interval drift | taboo_certify.py:214-226 | c11r_idrift.py:8-23, 275-316 | REPRESENTATION_ONLY |
| X08 | C_T rendering: exact 3429/500 (C11RD premise) vs outward-rounded record (supply) | — | C11RD_FREEZE_R1.json:147-153; FLOOR_R2_SPECIFICATION.md:141; A.5 | REPRESENTATION_ONLY |
| X09 | aggregation: max/min over 9 sub-blocks vs single whole-block certificate (C_T, τ, D_lo) | c2_refined_registry.py:159-166 | C11R_COMPARISON.json:108-112 | REPRESENTATION_ONLY (statement) + IMPLEMENTATION_SLACK (value) |
| X10 | D_lo statement conditional vs unconditional | taboo_certify.py:348-349 | c11r_boxdata.py:25-31 | PROOF_STRENGTH_DIFFERENCE (value-neutral in principle, (7)) |
| X11 | D_lo premises: (C_T, τ) vs h_min > 0, u ≥ 0 | c2_refined_registry.py:104-109 | c11r_boxdata.py:213-234 | ASSUMPTION_DIFFERENCE (both discharged) |
| X12 | τ/C_T candidate: (6/5)·g, degree 20, per sub-block vs linear p-flat w | taboo_certify.py:190-197; c2_refined_registry.py:95-99 | C11R_RUNS.json:43-81 | IMPLEMENTATION_SLACK (both sides) |
| X13 | Ā candidate: (5/4)·g + 2, degree 12 vs the same linear w | c2_refined_registry.py:126-127 | C11R_RUNS.json:82-120 | IMPLEMENTATION_SLACK (both sides) |
| X14 | τ_I2 = Ā_I2 (the atom-removal structure is not exercised at the binding box) | — | REVIEW_C11R_COMPARISON.md:71, 214; A.5 | IMPLEMENTATION_SLACK (p-flat family; Part C) |
| X15 | eff branch τ/D_lo (I1) vs Ā (I2) | A.5 branch labels | A.5 branch labels | SUPPLY_DIFFERENCE (caused by X14) |
| X16 | D_lo candidate: e0-midpoint degree-20 d̃0 − τλ0 − ρD1 vs linear u on box/panel cover | taboo_certify.py:300-337 | c11r_boxdata.py:166-234 | IMPLEMENTATION_SLACK (both sides) |
| X17 | D1/D2 method: e-constant global candidates + ρ·env widening, 9 sub-blocks vs e-Taylor band-piecewise candidates + Taylor models, 4 sub-blocks | taboo_certify.py:300-337 | D1_D2_DERIVATION.md:162-191 | IMPLEMENTATION_SLACK (I1 dominated by widening, (13)(iv)) |
| X18 | residual range depth 0 (I1 cell artifacts) | taboo_certify.py:284, 297 | — | IMPLEMENTATION_SLACK |
| X19 | S_I1 draws on two I1 constant sets (C1, C2), S_I2 on one | FLOOR_R2_SPECIFICATION.md:90-94 | same | SUPPLY_DIFFERENCE (inert at 306: C2 dominates C1 on every field, A.5) |
| X20 | D2 STRONGER by a large ratio (N2 concern) | C1 → C2 partition sensitivity of I1's D2 | Theorem 5 + validation 29/29 + independent recomputation (C11RD_COMPARISON_REVIEW.md:100-108) | IMPLEMENTATION_SLACK on I1's side is the documented explanation. Soundness of I2's D2 is not refuted and cannot be tested at 306 under the quarantine → flagged in Part D (POSSIBLE_DEFECT: not raised; UNKNOWN: a certified lower bound on sup\|D''\| at 306 does not exist) |
| X21 | I1 provenance residual N10 | FLOOR_R2_SPECIFICATION.md:141 | — | UNKNOWN |
| X22 | selector grid rounding of A (1/1000) and α (1/1000) | — | C11R_POLICY.json:389-395; c11r_boxdata.py:146, 272 | IMPLEMENTATION_SLACK (≤ 1/1000 absolute) |

---

## Part C — Non-target mechanism evidence

All of Part C was computed at e ∈ {1/2, 1, 3} only. It is FLOAT and NON-CERTIFIED, and no cell-306 number appears in
it. Full report: `mechanism/MECHANISM_STUDY.md`. Generated tables: `mechanism/MECHANISM_TABLES.md`. Data:
`validation/A306_MECHANISM.json` and `validation/A306_PFLAT.json`.

C.1 **Proposition PF (p-flat ceiling), proved and checked.**
* *Statement.* Every p-flat K̂_e-supersolution f(m) has τ_F = C_T,F = f(0) ≥ L′_e(0). Here L′_e is the ARL of the
  m-arm read along the atom-free states (max(0, 1 − m), m).
* *Checks.* All 18 p-flat family values (6 families × 3 drifts) respect the ceiling; p-dependent families go below it
  at every drift (`mech_pflat.py`, verdict PASS, with a planted negative control).
* *Size.* L′(0) equals the whole-kernel E_a[τ] to 5–6 figures at e = 1 and e = 3. So a p-flat taboo certificate
  cannot certify τ below ≈ E_a[τ] = τ_a/D.
* *Why this matters.* It is the structural explanation of review note N6. I2's weight is p-flat, so its τ is
  inherently a whole-kernel bound.

C.2 **Family slack, point drift, same statement.**
* The I2 families (L1 for Ā, τ and C_T; linear u for D_lo) are loose at every declared drift. Examples:
  * Ā/E_a[τ] = 1.146 (e = 1) and 1.164 (e = 3); a factor of 17.6 at e = 1/2, where the m-drift e − K vanishes;
  * D_lo/D = 0.550 (e = 1).
* Richer families of the **same** statements recover most of this:
  * Ā: HATm reaches 1.006 at e = 1; M6 reaches 1.002 at e = 3.
  * τ: HATpm reaches 1.033 at e = 1.
  * D_lo: PM4 and HATm reach 0.966 at e = 1.
* Controls:
  * NC1: the full nodal family reproduces the truth exactly (Ā, τ, D). The unconditional D_lo statement is therefore
    not what limits the value.
  * NC4: all 120 LP values lie on the correct side of the truth.

C.3 **Verification-discretisation and block slack of the linear family** (I2's selector re-implemented in float at
D5/P32; checked against the exact `c11_certifier` box bound, |diff| 1.1e-16).
* At e = 3, the box value of A exceeds the pointwise optimum by about 10 %, and the box α for D_lo falls from 0.988
  (pointwise) to 0.855 (w = 0) and to 0.748 (w = 1/8).
* At e = 1 the box selector hits b_max. The box loss (at most about 0.66 in m-drift at this configuration) can
  exceed the m-drift itself.

C.4 **Sherman–Morrison consistency** (Lemma SM(d), τ_a = D·E_a[τ]) holds to 1e-12 in every discretised solve.
Planted wrong atom split: the error rises to 3.7 (NC3).

**What Part C establishes.** The candidate families of I2 carry large, avoidable, drift-dependent slack from three
sources: the ansatz (linear, p-flat), the box/panel discretisation, and block uniformity. Richer families of the
same statements remove most of it. The one I2 statement that is stronger (D_lo) is not the limiting factor. Each
outcome was open in advance.

**What Part C does not establish.** The size of any effect at cell 306's drift block. No number here may be used
as an estimate for 306 (PREAMBLE S1, S8).

---

## Part D — Classification, defects flagged, unknowns

D.1 **Classification of the 306 disagreement: IMPLEMENTATION_SLACK (primary), acting through a SUPPLY_DIFFERENCE
(the eff branch).** It is **not** a PROOF_STRENGTH_DIFFERENCE. Reasons, qualitative and each cited:
* Five of the six statements are EQUIVALENT, and the sixth (D_lo) is stronger on I2's side, yet I2's D_lo value is
  the weaker one. A stronger statement cannot explain a weaker value unless the statement forces it. The full nodal
  control (C.2, NC1) shows that it does not.
* The consumer, κ, and every non-constant input are identical (B.2 (9)).
* Both implementations bound the same quantity, sup_E E_a[τ], through admissible Lemma Dv′ r2 branches (B.2 (12)).
* Every value-relevant difference in the register (X09, X12–X18, X22) is a property of the candidate family, the
  discretisation, the partition or the ladder. Each is avoidable in principle by a richer family or a finer
  discretisation of the same statement (Part C, generically).
* I2's branch Ā is forced by the p-flat ansatz (Proposition PF): τ_I2 = Ā_I2, so τ/D_lo cannot bind. I1's branch
  τ/D_lo is forced by its loose Ā (first ARL rung α = 5/4, β = 2).
* So the two supplies are limited by **different** slack mechanisms on the **same** statements. Neither has a
  stronger theorem.

This is a structural conclusion. It does **not** say which constant "drives" the sign difference of Γ. That
attribution would require a mixed-supply or per-term evaluation, which the quarantine forbids. It stays UNKNOWN,
as ROUTE_AUDIT_R1.md:225 records.

D.2 **Defects flagged.**
* **None found** in either implementation's mathematics, on the axes audited:
  * the Lemma T, Lemma SM and Theorem 5 propagations were re-read (B.1);
  * the reproduction A.5 matched exactly.
* **POSSIBLE_DEFECT (not raised, recorded as UNKNOWN):** the soundness of I2's D2, whose ratio to I1's is ≈ 0.056.
  * The committed record offers a benign explanation: I1's D2 is dominated by partition-dependent widening (B.2 (13)
    (iv); X17). I2's D2 has a theorem, a 29/29 validation and an independent exact recomputation of the propagation
    (X20).
  * No certified **lower** bound on sup|D″| over the 306 block exists, so a too-small D2 could not currently be
    detected. Theorem CV part (2b) supplies that missing check generically. Its use at 306 is governance-barred
    (A_306_ROUTE_SUMMARY.md §3).
* **Governance/record observations (not soundness defects):**
  * N10 open for I1 (X21).
  * Byte-level identity of I1's frozen reachable cover and I2's R specification not re-verified (B-H5).
  * C_T is rendered two ways inside I2 (X08). Sound either way, and the sealed evaluation used the conservative
    record (A.5).

D.3 **Does one implementation prove a genuinely stronger theorem?** No (B.2 (12)).

**Is there avoidable slack?** Yes, in both, and of different kinds (B.2 (13)).

**Does a common stronger theorem dominate both?** At the level of statements, yes. The true block constants are
common to both implementations, and Theorem CV (`common/THEOREM_CV.md`) makes them a common certified object: one
certificate set, two verifiers, a sandwich, and refutation. It dominates both implementations' **trust** structure,
not their values; values still come from search and discretisation. Its use at 306 is addressed in
`A_306_ROUTE_SUMMARY.md` §3: none is legitimate under current governance.

D.4 **Unknowns kept open.**
* Which constant drives the Γ-sign disagreement (forbidden to attribute).
* The true block constants at 306 (not computed; quarantined).
* Whether I2's D2 is sound (no refuting object exists; see D.2).
* B-H5 and N10.
