# Theorem CV — separating certificate search from verification, with a two-sided operator sandwich

**Status:** THEORY + stdlib IMPLEMENTATION + NON-TARGET VALIDATION of the mechanics (Stream A, overnight
campaign; R1-repaired). Route states after the repair: R-CV and R-SAND are **IMPLEMENTED (qualification needed)**;
see `../A_306_ROUTE_SUMMARY.md`. It is not applied
to any tail drift or cell. No drift in [6/5, 13/5] (or its mirror) was evaluated. No committed tail-cell number
appears in this file (PREAMBLE S8).

## 0. Prospective motivation (independent of any target sign)

Three facts about the programme motivate the route. Each one holds without reference to the sign of any Γ.

1. **Floor r2 reads two implementations as two independent value producers.** F1′ requires Γ < 0 under each
   implementation's own supply, and forbids mixing (`p5y_k5_tail_floor_r2/FLOOR_R2_SPECIFICATION.md`:62-83). The
   protection F1′ buys is soundness redundancy: adoption is correct "whenever at least one of the two
   implementations is sound" (:74-77). F1′ pays for that with a **value** requirement. Two sound implementations
   can therefore disagree on a closure verdict for no reason other than the quality of their candidate
   searches.
2. **"STRONGER" cannot be tested.** An unsound certifier looks STRONGER on an upper bound
   (`p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md`:260-265; FLOOR_R2_SPECIFICATION.md:126). The
   programme has no certified object that could refute a too-small upper bound.
3. **Search dominates value.** The Stream A mechanism study (`mechanism/MECHANISM_STUDY.md`, non-target) shows three
   things for the family of operator constants:
   * certificate families carry large, avoidable, drift-dependent slack;
   * a whole class of families (the p-flat ones) provably cannot separate τ from the whole-kernel ARL (Proposition PF);
   * richer families of the *same* statements remove most of the slack.

Theorem CV answers all three:
* It moves the independence requirement from the **values** to the **verification**.
* It supplies a certified **lower** side for each upper-bound constant, and an upper side for D_lo, so every
  constant is sandwiched.
* It turns "STRONGER" into a refutable claim.

## 1. Setting and assumptions

* E ⊂ ℝ is a drift block; the other-side sets E′ ⊂ E are points or sub-blocks.
* R is the state set, and a is the atom.
* K_e is the transition kernel, and K̂_e = K_e − k_{a,e} ⊗ δ_a is the atom-removed kernel.
* h_{1,e} = 1 − K_e1 is the one-step killing (alarm) probability.

| # | assumption | CUSUM (this programme) |
|---|---|---|
| A1 | K_e ≥ 0 on B(R); atom split with K̂_e ≥ 0, k_{a,e} ≥ 0, k_a + h₁ + K̂1 = 1 | Lemma K (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`:17-30) |
| A2 | R is invariant: from any x ∈ R the next state lies in R | shown in `mechanism/mech_core.py` docstring; also the reachable-set spec of `c11_certifier.py`:189-197 |
| A3 | uniform killing on the sets used for SUB kinds: inf_{R×E′} h₁ ≥ h_min > 0 | certified per certificate (both verifiers) |
| A4 | for the D1/D2 lower bounds: e ↦ D_e is C² on E | Lemma K analyticity (THEOREM_AD.md:23-30) |
| A5 | a verifier V is *sound for kind κ* iff V(Z) = ACCEPT implies P_κ(Z) | an assumption about code, which is why two verifiers are used |

No assumption refers to a cell, to an m, or to CUSUM specifically beyond A1–A4. The theorem applies to every K1 cell
and every drift block of any detector whose kernel has an atom split. The sandwich and refutation parts also apply
to finite-state fixtures (validated in §7.3).

## 2. Statement

**Definition (certificate predicates).** A certificate Z = (κ, E, f) has a kind κ, a block E and a bounded function f
on R. Its predicate P_κ(Z) is:

| κ | predicate (for every e in the certificate's set, on R) | value(s) |
|---|---|---|
| ARL_SUPER | f ≥ 0 and f ≥ 1 + K_e f | Ā := f(a) |
| TABOO_SUPER | f ≥ 0 and f ≥ 1 + K̂_e f | τ := f(a), C_T := sup_R f |
| D_SUPER | f ≥ 0 and f ≥ h₁ + K̂_e f | D^up := f(a) |
| ARL_SUB | f ≥ 0, f ≤ 1 + K_e f, and h_min > 0 | Ā^lo := f(a) |
| TABOO_SUB | f ≥ 0, f ≤ 1 + K̂_e f, and h_min > 0 | τ^lo := f(a), C^lo := sup over listed points of R of f |
| D_SUB | f ≥ 0, f ≤ h₁ + K̂_e f, and h_min > 0 | D_lo := f(a) |

**Theorem CV.** Assume A1–A3.

1. **(Values.** If P_κ(Z) holds, then for every e in Z's set:
   * ARL_SUPER: E_a[τ](e) ≤ Ā.
   * TABOO_SUPER: τ_a(e) := (Ĝ_e 1)(a) ≤ τ and ‖Ĝ_e‖ ≤ C_T.
   * D_SUPER: D_e ≤ D^up.
   * ARL_SUB: E_a[τ](e) ≥ Ā^lo.
   * TABOO_SUB: τ_a(e) ≥ τ^lo and ‖Ĝ_e‖ ≥ C^lo.
   * D_SUB: D_e ≥ D_lo.
2. **(Sandwich.** Take true block constants Ā* = sup_E E_a[τ], τ* = sup_E τ_a, C* = sup_E ‖Ĝ_e‖ and D* = inf_E D_e.
   Take a SUPER certificate on E and a SUB certificate on some E′ ⊂ E, both valid. Then:
   * (a) Ā^lo ≤ Ā* ≤ Ā, τ^lo ≤ τ* ≤ τ, C^lo ≤ C* ≤ C_T, and D_lo ≤ D* ≤ min(D^up, 1).
   * (b) Assume A4, and valid D_SUB and D_SUPER certificates at points e₀ < e₁ < e₂ of E, spaced h, with
     D(e_i) ∈ [ℓ_i, υ_i]. Then
     sup_E |D′| ≥ max_{i<j} max(0, ℓ_j − υ_i, ℓ_i − υ_j)/(e_j − e_i), and
     sup_E |D″| ≥ dist(0, [ℓ₀ − 2υ₁ + ℓ₂, υ₀ − 2ℓ₁ + υ₂]) / h².
3. **(Refutation.** Consider any claim of the same statement from any source.
   * An upper-bound constant X (for Ā*, τ*, C*, sup|D′| or sup|D″|) with X < L, the certified lower side, is
     **false**.
   * A lower-bound constant X (for D*) with X > U, the certified upper side, is **false**.
4. **(Separation.** Let V₁ and V₂ be verifiers and S a certificate set that both ACCEPT.
   * If V₁ **or** V₂ is sound, every predicate in S holds, and so every value in (1)–(3) is certified.
   * The value of a certificate is an exact deterministic function of f. The "V₁ path" and the "V₂ path" therefore
     certify **identical** statements with **identical** values.
5. **(Consumption.** Lemma Dv′ r2 (THEOREM_AD.md:81-89) is non-decreasing in (Ā, τ, C, D1, D2) and non-increasing
   in D_lo. Any supply built by Lemma Dv′ r2 from values certified under (4) is therefore valid under the same
   hypothesis, "V₁ or V₂ is sound". So is the componentwise minimum over several doubly-accepted certificate sets for
   the same statements.

## 3. Proofs

*(1).*
* ARL_SUPER and TABOO_SUPER: Lemma T (THEOREM_AD.md:32-40) and its whole-kernel version (:91-93). Induction gives
  Σ_{j<n} K^j 1 ≤ f; let n → ∞. ‖Ĝ‖ = ‖Ĝ1‖_∞ by positivity.
* D_SUPER: induction Σ_{j<n} K̂^j h₁ ≤ f. The base case is 0 ≤ f. The step is h₁ + K̂ Σ_{j<n} ≤ h₁ + K̂f ≤ f. Then
  d_e = Ĝ_e h₁ ≤ f and D_e = d_e(a).
* SUB kinds:
  * Iterating the inequality gives f ≤ Σ_{j<n} P^j s + P^n f, with (P, s) = (K, 1), (K̂, 1) or (K̂, h₁).
  * Because P1 ≤ K1 = 1 − h₁ ≤ 1 − h_min, ‖P^n f‖ ≤ (1 − h_min)^n ‖f‖ → 0.
  * Hence f ≤ (I − P)⁻¹ s, which is E_·[τ], Ĝ1 or d.
  * For C^lo: every listed point lies in R, so f(x) ≤ Ĝ1(x) ≤ ‖Ĝ‖.

*(2)(a).* Apply (1) at e′ ∈ E′ ⊂ E and on E: L ≤ q(e′) ≤ sup_E q ≤ U, and inf_E D ≤ D(e′) ≤ D^up. D ≤ 1 because D_e is
a probability (THEOREM_AD.md:48).

*(2)(b).*
* First difference: by the mean value theorem, D(e_j) − D(e_i) = (e_j − e_i)D′(ξ) for some ξ ∈ (e_i, e_j), and
  |D(e_j) − D(e_i)| ≥ max(0, ℓ_j − υ_i, ℓ_i − υ_j).
* Second difference: for C² functions, D(e₀) − 2D(e₁) + D(e₂) = h² D″(ξ) for some ξ ∈ (e₀, e₂). This is the
  second-order mean value theorem for divided differences. The left side lies in the stated interval.

*(3).* An upper-bound claim "X ≥ q(e) for all e ∈ E" with X < L ≤ q(e′) fails at e′. The lower-bound case is the
mirror image.

*(4).* If V₁ is sound, then V₁(Z) = ACCEPT ⇒ P(Z). Otherwise V₂ is sound, and V₂(Z) = ACCEPT ⇒ P(Z). The values are
computed from f, not taken from either verifier. ∎

*(5).* Monotonicity can be read off Lemma Dv′ r2. The componentwise minimum of valid supplies is valid, as in C2's D4
rule; it is valid **whenever each input is valid**, and under (4) each input is. ∎

## 4. The sufficient condition both verifiers check (Lemma BP, box/panel)

Let 𝓑 be the depth-d dyadic cover of R. A box B = [a,b]×[c,d] is kept iff a + c ≤ 4, or a = 0, or c = 0.
Put T(x, z) = (max(0, p + z − K), max(0, m − z − K)), C = K + H, and u = z + e.

**Upper bound of (K_e f)(x) on B × E, for f ≥ 0 on R.**
* Take the u-range U = [c − C + e_lo, C − a + e_hi]. It is the union of the alarm-free windows over B × E, shifted.
  Split it into P equal panels. Panel k has z-range Z_k = [u_k − e_hi, u_{k+1} − e_lo].
* Image box: I_k = [max(0, a + z_lo − K), max(0, b + z_hi − K)] × [max(0, c − z_hi − K), max(0, d − z_lo − K)].
  T is monotone in (p, m, z), so T(x, z) ∈ I_k.
* Then (K_e f)(x) ≤ Σ_k max(0, sup_{I_k} f) · ∫_{panel k} φ. For z in x's own window, 0 ≤ f(T) ≤ sup f. For z outside
  it, the true integrand is 0.
* For K̂_e: a panel with Z_k ⊂ [d − K, K − b] may be skipped. That interval is the intersection of the atom windows
  [m − K, K − p] over B, so the panel lies inside every x's atom window and carries no K̂ mass.

**Lower bound of (K_e f)(x) on B × E.**
* Take the u-range U′ = [d − C + e_hi, C − b + e_lo]. It is contained in every x's window for every e. The dropped
  mass has integrand f(T)φ ≥ 0.
* Each kept panel contributes at least inf_{I_k} f · mass_lo, or inf_{I_k} f · mass_hi when inf_{I_k} f < 0.
* For K̂_e: drop every panel meeting [c − K, K − a], the union of the atom windows over B.

**Source.** h₁(p, m, e) = 1 − Φ(C − p + e) + Φ(m − C + e) increases in p and m. Each Φ-term is monotone in e. So
h₁ ∈ [1 − Φ(C − a + e_hi) + Φ(c − C + e_lo), 1 − Φ(C − b + e_lo) + Φ(d − C + e_hi)] on B × E.

**Checks.** Every box B ∈ 𝓑 must satisfy:
* SUPER: inf_B f − sup src − (upper bound) ≥ 0;
* SUB: inf src + (lower bound) − sup_B f ≥ 0;
* inf_B f ≥ 0;
* for SUB kinds, h_min = min_B inf h₁ > 0.

These imply P_κ(Z), because every x ∈ R lies in some box of 𝓑.

This is the C11R box/panel scheme (`p5y_k5_tail_c11r_n9_statement_alignment/code/c11r_idrift.py`:275-316,
`c11r_boxdata.py`:157-234), extended to all six kinds and to arbitrary polynomial weights. It is written down here as
a specification, and both verifiers implement it from this text.

## 5. Certificate format (schema `A306_CV_CERT/1`, JSON; example files in `certs/`)

```
{ "schema": "A306_CV_CERT/1",
  "kind": "ARL_SUPER | TABOO_SUPER | D_SUPER | ARL_SUB | TABOO_SUB | D_SUB",
  "drift_block": ["e_lo", "e_hi"],                 exact rationals; a point block has e_lo = e_hi
  "weight": {"i,j": "rational", ...},              f(p, m) = sum c_ij p^i m^j
  "claims": {"value_at_atom": "rational",          must equal f(0,0) exactly
             "C_T_upper": "rational",              TABOO_SUPER: must be >= each verifier's sup bound of f on R
             "C_T_lower": "rational"},             TABOO_SUB: must be <= each verifier's exact point maximum on R
  "hints": {"depth": int, "panels": int},          discretisation defaults; soundness does not depend on them
  "model": {"K": "1/2", "H": "5", "R": "...", "atom": [0, 0]} }
```

Acceptance of a certificate set requires:
* both verifiers ACCEPT every certificate;
* the value strings are identical;
* every supply constant is on the correct side of the certified other side (the sandwich-consistency gate).

Any disagreement excludes the certificate (fail closed) and is recorded.

## 6. Implementation (stdlib only)

| file | role |
|---|---|
| `cv_verify_a.py` | V_A: exact `fractions` plus C7's rigorous rational Φ/φ (2^-320 outward). Monotone-monomial polynomial bounds. Recursive cover. |
| `cv_verify_b.py` | V_B: `decimal` at 90 digits with ROUND_FLOOR/ROUND_CEILING on every operation. Own Φ series (all-positive terms with geometric tail) and own π (Machin in decimal). Interval Horner. Grid cover. Shares **no code** with V_A. |
| `cv_search.py` | UNTRUSTED search: an LP over the float box condition for monotone polynomial families in m, then safe dyadic rounding. |
| `cv_validate.py` | the declared non-target validation (§7). |

**Independence and common mode.**
* V_A and V_B share the model constants, the R specification and Lemma BP (the mathematical sufficient condition).
  An error in Lemma BP itself would be common-mode.
* They share no arithmetic, no Gaussian primitive, no polynomial bound and no code.
* The same author wrote both in one session, so this is implementation independence, not authorship independence.
  The same qualification applies to I2 (FLOOR_R2_SPECIFICATION.md:158-163).

## 7. Non-target validation (`cv_validate.py` → `validation/A306_CV_VALIDATION.json`)

**Latent-proxy notice (quarantine amendment 2, R2.3).** The certified values below are validation-drift
E_a[τ]/τ/C_T bounds at e = 3. They are latent proxies by content class. They must not be quoted in cross-route or
handover text, and no transfer into the band is derived from them (R2.2).

**R1 repair (REVIEW_GLOBAL_INTEGRITY_R1 C-2, C-3, F5, F11).** The validation was repaired and re-run in full with
instrumented verifiers:
* the class (c)/(d) items are withdrawn from the verdict;
* taboo-specific certificates were added;
* planted items P8 and P9 were added;
* the DD control was re-planted.

The declaration of the repair is in the docstring of `cv_validate.py`. The pre-repair runs are preserved as
`runs/V_*_pre_R1.*`. Verdict after the repair: **PASS** (`cv_validate.assemble`, `out["verdict"]`). The gates are:
* valid certificates accepted by both verifiers with identical values;
* planted certificates rejected by both;
* the sandwich contains the float truth;
* both taboo branches fire in both verifiers;
* the taboo certificate is distinct from the ARL one;
* √(2π) memoisation is bit-identical;
* the DD re-plant passes.

**7.1 Two verifiers, one certificate set.**
* Seven valid certificates were found by the untrusted search:
  * six at the non-target block E = [3, 49/16] and at E′ = {3}: ARL_SUPER, TABOO_SUPER, D_SUB, ARL_SUB, TABOO_SUB,
    D_SUPER;
  * one taboo-specific certificate **TABOO_SUPER_T** at the point {3}, searched with the K̂ box condition.
* Each certificate has 363 boxes and 32 u-panels.
* Both V_A and V_B **ACCEPT** all seven with **identical** value strings.
* Distinct certificates:
  * TABOO_SUPER (block) has a weight byte-identical to ARL_SUPER (review F11). It is **not** evidence for the taboo
    path.
  * TABOO_SUPER_T has its own weight, distinct from ARL_SUPER (gated).
  * The K̂ sub-solution search at {3} reproduced the ARL_SUB weight byte-for-byte: the atom-union drop does not bind
    there. So TABOO_SUB is **not distinct** from ARL_SUB, and no distinct valid taboo lower certificate is claimed.
* **Taboo branches exercised, identically in both verifiers** (instrumented counters, gated):
  * the upper K̂ skip fires on 2 panels for TABOO_SUPER_T (the origin box);
  * the lower atom-union drop fires on 68 panels for TABOO_SUB;
  * both counters are 0 for TABOO_SUPER (block), where the skip cannot align.
* **Discrimination (reported, not gated):** TABOO_SUPER_T re-submitted with kind ARL_SUPER is REJECTED by both
  verifiers, with margins about −9.7e-4, whereas its K̂ margin is about +9.9e-5.
  * So the skip branch is load-bearing: this certificate is valid for K̂ and not certifiable for K at this
    discretisation.
  * This is not a proof that the weight is not a K-supersolution.
* **D_SUPER is vacuous:** its value exceeds 1, and D ≤ 1 always.

**7.2 Planted-invalid certificates. All nine are REJECTED by both verifiers.** Every item is class (a): through the
verifier code, and guaranteed to fire for a sound verifier.

| id | planted defect | why invalid | V_A / V_B reason |
|---|---|---|---|
| P1 | ARL_SUPER value below the certified ARL_SUB lower side | provably (Theorem CV (2a)) | box inequality |
| P2 | D_SUB with u(a) = 101/100 | D ≤ 1 | box inequality |
| P3 | TABOO_SUPER value claim − 1/1000 | claim ≠ f(a) | claim check |
| P4 | TABOO_SUPER C_T claim below sup f | claim check | C_T_upper branch |
| P5 | ARL_SUPER with f(5) = −1/10 | f ≥ 0 fails | box + nonnegativity |
| P6 | TABOO_SUB above the certified TABOO_SUPER upper side | provably | box inequality |
| P7 | D_SUPER below the certified D_SUB lower side | provably | box inequality |
| **P8** | **TABOO_SUPER_T** (taboo path, skip active) scaled below the TABOO_SUB lower side at {3} | provably (τ_a(3) ≥ L) | box inequality |
| **P9** | TABOO_SUB with C_T_lower claim = f(a) + 1/100 | above the point maximum | **C_T_lower branch** |

**7.3 Sandwich against the float truth** (the truth is a non-certified reference):
* All five intervals contain the Nyström truth: Ā*, τ*, C* and D* on E, plus τ_a(3) at the point, which uses the
  taboo-specific upper side.
* The upper side of D* is the trivial bound D ≤ 1, because D_SUPER is vacuous.
* **Refutation (Theorem CV part 3)** is a one-line logical corollary. The former "refutation pattern" list tested
  only comparisons (class (c)/(d)). It is kept in the JSON as `refutation_illustration_not_a_control` and is **not**
  in the verdict.
* The operational content of refutation — a certificate asserting a value on the wrong side of a certified bound is
  rejected — is carried by the class-(a) plants P1, P6, P7 and P8.

**Divided-difference lower bounds, part (2b)**, on five exact finite-state drift families (`ov_fixtures`, seeds 1–5):
* The honest enclosures d ± δ are checked exactly as sub/super-solutions.
* LB1 ≤ exact sup|D′| and LB2 ≤ exact sup|D″| in all 10 records.
* LB2 is non-vacuous in the 5 records with δ = 1e-9, and vacuous (0) in the 5 with δ = 1e-3.
* **Re-planted control (class (a)):** an invalid enclosure u = d + 1/20, claimed as a sub-solution, is rejected by
  the exact sub-solution check in 10/10 records. This is guaranteed, since u − K̂u − h₁ = (1/20)(1 − K̂1) > 0.
* The former "planted D2 claim 0.9·LB2 refuted 5/5" reduced to LB2 > 0 (class (c)). It is WITHDRAWN.

**7.4 What the validation shows and does not show.**
* **It shows:**
  * two arithmetically independent verifiers agree on accept/reject for every certificate, including nine
    class-(a) plants and a taboo-specific certificate whose skip branch is load-bearing;
  * values are shared exactly;
  * the sandwich is sound against the float truth.
* **It does not show:**
  * **Tight sandwiches.** At depth 5 / 32 panels, with degree-3 monotone polynomials in m, the widths are
    dominated by box/panel loss, not by the theorem.
  * **A non-vacuous D upper side.**
  * **A taboo lower certificate distinct from the ARL one.**
  * **Any D1/D2 certificate kind.** Theorem CV covers four of the six supply constants: C_T, τ, Ā and D_lo.
* **Correction.** The first version of this section said the depth-5 re-run followed a vacuous depth-4 D_SUPER, and
  implied the vacuity was cured. It was **not** cured: D_SUPER's value is still above 1 at depth 5 / 32 panels.
  The depth-4 → depth-5 change happened before any verifier ran and is disclosed as a search trial only.
* **Coverage:**
  * 17 certificates × 2 verifiers: 7 valid, 9 planted, 1 discrimination;
  * 363 boxes × 32 panels each;
  * 10 synthetic records.

## 8. Relation to governance (cell 306 and beyond)

See `../A_306_ROUTE_SUMMARY.md` §3. In short:
* Applying Theorem CV to cell 306 would create a new 306 supply after the sealed disagreement. That is the situation
  ROUTE_AUDIT_R1 §5 classifies as 306-c/306-d (RESULT_CHASING_RISK) and 306-g (GOVERNANCE_BARRED).
* It also contradicts the fixed fact "no new 306 supply" (ROUTE_AUDIT_R1.md:92).
* Under current governance there is **no legitimate 306 use**.
* As a prospective method (a candidate floor-r3 limb for cells not yet evaluated), it would have to bind the items
  listed there **before** any tail-drift search or verification. Under floor r2 as written it is CLOSURE-ONLY:
  * it redefines "each implementation certified the constants" as "both verifiers accepted one certificate set";
  * part (5) legitimises a componentwise minimum across certificate sets, which r2 forbids.

## 9. Limitations

* **Theorem CV improves trust semantics, not values.** Achievable values depend on the search family and on the
  sufficient condition's discretisation. At the validation block the certified sandwich is wide because of box/panel
  loss (§7.4), not because of the theorem. Tighter sandwiches need finer or adaptive covers, or better panel bounds.
  This is future work and is not claimed here.
* **Verifiers are incomplete.** A sound verifier may reject a true certificate. Soundness is what matters; a
  rejection is informative only as "not certified at this discretisation".
* **The D1/D2 lower side (2b) needs tight two-sided D enclosures.** Its bound is vacuous when the enclosure width
  exceeds h²·|D″| (seen in §7.3 at δ = 1e-3).
* **Float truth is a reference only.** The sandwich-contains-truth check uses the non-certified Nyström truth, with
  its Richardson uncertainty as tolerance.
* **The theorem covers four of the six supply constants.** There is no certificate kind for D1 or D2 (upper bounds
  on |D′| and |D″|); only their certified lower sides (2b) exist. A supply built by Theorem CV (5) therefore still
  needs D1/D2 from a derivative certificate of the C11RD type. That certificate lies outside Theorem CV's separation
  structure.
* **The D upper side is vacuous at the validation configuration** (D_SUPER value > 1). The D sandwich's upper side
  is the trivial D ≤ 1.
* **The taboo lower branch is not validated as distinct.** The K̂ sub-solution optimum coincided with the ARL one at
  the validation point.
