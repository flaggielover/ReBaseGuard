# Phase 1: target-independent theory for cell 309 (answers to the ten priority questions)

This document is research only. It contains **no new quantity for cells 305–309 and no drift in the band**. Committed
facts are cited qualitatively, and their sources are in `dossier/sources/`. Every theorem below is general: it holds
for every cell and every m. Notation follows `THEOREM_SRK.md`.

## Q1. Why does 309 survive the existing consumer?

Binding-regime closed form (graph A §0.2, committed facts: 𝓗 ⊆ R2_interval, the lower end binds, C_lo < 0):

    Γ(S) = g_hi + ρ·x_hi·( |C_lo| + A0·P̄2 + 2A1·P̄1 + A2·P̄0 ),   P̄j = (1/5)Σ_r p_j(r).

**Proposition Q1 (supply exhaustion, restating C3/C4/C7/C8 symbolically).**
* Lemma SM(d) makes the order-0 channel sharp at f ≡ 1. So every valid order-0 constant satisfies A0 ≥ Λ_309 =
  sup_{C309} E_a[τ].
* Since A1, A2 ≥ 0, every atom-constant supply S satisfies Γ(S) ≥ g_hi + ρx_hi(|C_lo| + Λ_309·P̄2).
* The committed record (C4 at C4's floor; C7 STRENGTHENED; C8; under the direct clause and under C5-T) shows that this
  lower bound is ≥ 0 at 309.

So **no supply-only route closes 309 under the frozen TC-T inputs and a whole-cell transport**. Any route must change
at least one of:
* P̄2, i.e. the order-0 channel's charge on the Taylor surrogates;
* |C_lo|, g_hi, or the transport.

C4's refuted family explicitly `does_not_cover` residual-specific (non-norm-only) order-0 bounds, changes to TC-T,
the clause or the inputs, and order-3 candidates.

## Q2. Which terms dominate the gap (symbolically)?

The committed decompositions (C2 D1, C5, HISTORICAL_DOMINANCE; reader A §G) show the following. They are quoted
qualitatively; no number is reproduced.
* A0·P̄2 dominates S̄.
* Within p2 = f_H + ρf_G + ρ²Env4/2:
  * the order-3 surrogate ρ·f_G is first;
  * the order-4 envelope ρ²Env4/2 is second;
  * the midpoint residual f_H is negligible.
* |C_lo|, A1 and A2 are small.

Structurally, both dominant terms are **norm-only** majorants of objects with known pointwise structure. Each is
charged through the order-0 channel at its **sup norm**:
* f_G majorizes S‴ + 3K₁Ĥ + 3K₂D̂ + K₃F̂;
* Env4 majorizes the (P3) expansion.

## Q3. Can a genuine order-3 remainder strictly dominate the surrogate?

**Proposition O3-N (no uniform dominance).** Take a real candidate Ĝ ≠ 0 and the same F̂, D̂, Ĥ. Theorem TC gives:
* a centre motion of half-width ρ|Ĝ(a)|, which is **unsigned** in the committed records;
* p2 = f_H + ρf_G^real + ρ²Env4(s_G)/2, with Env4(s_G) = Env4(0) + 4k₁s_G + 6k₂ρs_G + 4k₃ρ²s_G/2 + k₄ρ³s_G/6.

The real route is better for cell r iff

    ρ|Ĝ_r(a)| + A0[ρ(f_G^real − f_G^sur) + ρ²(Env4(s_G) − Env4(0))/2] < 0.

Neither sign is implied by the premises: s_G > 0 raises Env4 strictly, and |Ĝ(a)| > 0 adds width. So the real
order-3 route **does not uniformly dominate** the surrogate. This is consistent with Campaign B's committed "T2 hinges
on the centre motion".

**Theorem O3-X (intersection dominance).** Let 𝓗^0 and 𝓗^Ĝ be the TC enclosures of R''_m(e) on the cell from the
zero candidate and from the real candidate, with the same F̂, D̂, Ĥ. Both are valid (theorem TC with two different
fixed Ĝ). Then 𝓗^0 ∩ 𝓗^Ĝ is valid and dominates both.

More generally, for any finite set Λ_G ⊂ ℝ fixed before evaluation, ∩_{λ∈Λ_G} 𝓗^{λĜ} is valid. Each λĜ is a legal
fixed candidate. Its (P2) residual is bounded by the triangle inequality:
‖φ'''_λ(e0)‖ ≤ λ·(δ_G + ε3) + (1 − λ)·f_G^sur for λ ∈ [0, 1], since φ'''_λ = λφ'''_1 + (1 − λ)φ'''_0. This interpolates the two premises.

*Proof.* Theorem TC holds for any fixed candidate quadruple, and the intersection of valid enclosures of the same set
is valid. ∎

**Status.** Theorem-level PROMISING (no loss from adding the real candidate). **BLOCKED** for 309: it needs a real Ĝ at
309, which is new real computation under guard DENY with N1/N5/N7 open. SRK (below) also composes with a real Ĝ: the
s_G terms of Env4 then get state-resolved weights 4κ̄₁ + ….

## Q4. Can the composite-sup theorem be strengthened prospectively?

**Theorem L (ladder).** With exact certificates, for every cell and every r:

    rad^TC-T  ≥  rad^SRK  ≥  rad^{RSO-P∘SC}  ≥  |exact order-0 image| + 2A1p1 + A2p0 .

*Proof.*
1. **TC-T ≥ SRK:** the min construction (THEOREM_SRK §3 step 7).
2. **SRK ≥ RSO-P∘SC:** RSO-P∘SC applies the order-0 channel to the actual pointwise moduli a3(x) = |φ'''(e0)(x)| and
   a4(x) = sup_s|φ⁗(s)(x)|, weighted by occupation. SRK applies it to the pointwise majorants Ψ3 ≥ a3 and Ψ4 ≥ a4
   (THEOREM_SRK §3 steps 4–5). Positivity of R_e then gives (R_e a_j)(a) ≤ (R_eΨ_j)(a).
3. **Last step:** RSO-0 (overnight) is the exact image when the certificate is exact. ∎

SC (overnight SC-3/SC-4w) strengthens the **norm** of the composite, and RSO-P∘SC strengthens its **occupation
weighting**. Both need the candidate payloads, which are not serialized (U1/U2). **SRK is the payload-free
strengthening:** it keeps the pointwise *structure* of the surrogate (which kernel term, with which state-resolved
window) and drops only the candidates' pointwise values, replacing them by their certified sups s_X.

**Theorem SC-SRK (strict gain criterion).** At exact certificate level, SRK is strictly below TC-T for cell r iff at
least one of these holds:
* (3s_H κ̄₁ + 3s_D κ̄₂ + s_F κ̄₃) is non-constant μ_{a,e}-a.e., with values below its sup on a set of positive
  occupation, for the maximizing e;
* the analogous statement holds for the order-4 weight.

*Proof.* This is the equality case of Lemma SV. ∎

## Q5. Does TPT give a strict theorem-level improvement after the incident liabilities?

**Mathematics.** Yes, and unchanged by the liabilities. TPT is sound and dominates C5-T. It is strict whenever the
profile has s-dependent terms: the TPT-G factor for s^k is (x0+ρ/2)/(x0/(k+1)+ρ/(k+2)) > 1 for k ≥ 1. TPT-O makes it
sharp within its three-input family.

**Composition (Theorem SRK-P).** The SRK radius is also a profile:

    rad^SRK(s) = A0f_H + s·B3 + (s²/2)·B4 + 2A1p1(s) + A2p0(s)   for s = |t − e0| ≤ ρ.

This is Lemma TC-P with THEOREM_SRK step 3 at distance s. Γ̄_i is uniform on the cell, so the proof is unchanged. So
TPT∘SRK is valid and dominates both.

**Liability.** Any 309 use of TPT carries:
* overnight incident 01 (motivation by committed tail shares);
* incident 309R1-01 (the coordinator re-exposed to those shares).

**Rating: BLOCKED for this campaign; HIGH motivation risk.** It needs an explicit user decision with both incidents
disclosed. It is not reused here as clean evidence.

## Q6. What can cover refinement guarantee symbolically?

Overnight CR-1/CR-3 are restated and verified in form (digest `COVER.md`).
* The clause is a polynomial in ρ.
* Real refinement into N sub-cells, each with new K1 records at its own midpoint, removes the fraction 1 − 1/N^j of
  the order-j (in ρ) slack of the radius charge.
* Refinement **without** new records gains exactly 0 over TPT (an identity).

Consequence: refinement's guarantee lives only in the NEW_REAL class. That is new K1 records at sub-cell midpoints of
309, which is **BLOCKED** (new real computation; cover-index governance; U1).

## Q7. Does an operator-specific sup-norm bound remove worst-case slack?

Yes: **SRK** (THEOREM_SRK, new in this campaign).
* It replaces the uniform kernel-derivative norms k_i inside the order-0 channel by the state-resolved window
  integrals k_i(x; e). These integrals are ≤ κ_i and strictly smaller wherever the survival window truncates the
  Gaussian mass.
* It weights them by the chain's occupation from the atom.
* It needs **no candidate payloads, no replay host (U1), and no new record-derived quantity**. Its new inputs are
  operator-only supersolution certificates, in the same class as RLR307's Stage 1.

## Q8. Residual-specific structure instead of uniform bounds

SRK is the residual-specific route (C4 §7.1's "escapes the floor") in the only form that is currently data-feasible.
Structurally:
* The route audit had narrowed RSO to "A0·f_H only", because f_G and Env4 are norm-only.
* SRK removes that premise: the surrogates' **pointwise majorants** are explicit (Lemma SK).
* So the residual-specific mechanism reaches the dominant order-3 and order-4 terms.

The full RSO-P∘SC (overnight) stays payload-blocked.

## Q9. Can assembly inequalities be sharpened without target tuning?

| item | status |
|---|---|
| **Corollary T for g_hi** (theorem AD §6, adopted; applied on cells 0–148 only) | Valid on any cell whose record eps fields and a valid supply are available. It replaces generic midpoint eps C·f by A0 f and A0 f_D + A1 f_F. Effect: small by structure (midpoint residuals). Governance: it tightens a recorded interval with a new quantity derived from the record, so it needs the U2 ruling (P3 record). Stated here as an optional dominance component, not selected |
| **TPT/C5-T** | See Q5 |
| **Chain clause** (K5-B, part of k5b_literal) | Already evaluated by the frozen K5-B. No new lever without new L_k (R''' lower bounds, i.e. real order-3) |
| **W-term hull / independent summation over r** | Would need joint objects that do not exist (C6: "NEVER EXISTED"). Not a route |

## Q10. Can SC or RSO be constructed from prospective candidate data without tuning on historical 309 outcomes?

**Mathematically, yes.** The certificate definitions (SC-3, SC-4w, RSO-0/P) are fixed and target-free.

**Practically, BLOCKED.**
* The candidate payloads for 309 were never serialized.
* Regenerating them is a replay of the frozen K1 producer at 309's midpoint. That needs:
  * a numpy/flint host (U1);
  * an admissibility ruling on objects derived from the P3 record (U2);
  * a governed real execution.

This session has network access to PyPI, so a flint host *could* be provisioned here. But choosing a certifying host
is a user decision (U1, C6 Condition 7), not a campaign decision. SRK is the payload-free core of RSO, and it is not
blocked by U1/U2.

## Summary of new theorems in this campaign

| id | statement | proof | tests |
|---|---|---|---|
| SRK (with Lemmas SK, SV, SV′, SV-T) | state-resolved order-0 channel, dominance by min | THEOREM_SRK §§1–3, 9, 10 | FSM exact truth, two-sided assembly, envelopes, port identity, decoys, independent verifier (in progress) |
| SRK-P | profile form (composes with TPT) | above, Q5 | covered by the assembly battery for s = ρ; profile form not implemented (TPT blocked) |
| L (ladder) | TC-T ≥ SRK ≥ RSO-P∘SC ≥ exact | above, Q4 | FSM truth (TC-T ≥ SRK ≥ exact) |
| O3-N, O3-X | real order-3 does not dominate uniformly; intersection does | above, Q3 | theory only (BLOCKED data) |
| Q1 | supply exhaustion (restated symbolically) | above | committed record |
