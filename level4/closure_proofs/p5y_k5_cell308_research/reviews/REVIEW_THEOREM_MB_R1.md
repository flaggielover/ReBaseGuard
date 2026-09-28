# REVIEW_THEOREM_MB_R1 — independent adversarial review of theory/THEOREM_MB.md (draft r0)

THEORY_ACCEPTED_WITH_CORRECTIONS

Reviewer: reviewMB (independent; did not author any reviewed material). Date 2026-09-28.
Scope: NS/theory/THEOREM_MB.md r0 and its cited sources. No CUSUM m=5 tail-cell number is computed or written
here; reviewer exposure to committed tail figures while reading the assigned sources is disclosed in §X.

## Summary

The mathematics of THEOREM_MB r0 is sound. Theorem M is correct; I re-derived it (T1). Lemmas M-U, A0-M, Dv′-M and
D14-M are correct. Dv′-M and D14-M are instances of Lemma Dv′ r2 and declaration D14 with a smaller but still valid
Ā, because both proofs use Ā only through the scalar inequality Λ(e) ≤ Ā pointwise in e (T2). Theorem MB is correct:
(P4) is used only pointwise in t, TPT-B stays valid when block constants decrease across boundaries, and the
piece-end rule is both exact and necessary (T3). No hidden premise breaks soundness (T4). Six corrections are
required. Five are statement-level (C1-C5): a wrong domain claim, a missing premise for the dominance chain, an
unspecified A0 slot, a wrong "monotone integrand" justification, and an ungated E = [e0 − ρ, e0 + ρ]. One is
implementation-level for obligation O3 (C6). None changes the conclusion of Theorem MB. This review discharges
obligation O1 (THEOREM_MB.md:134-135) subject to C1-C5.

## Blockers

None.

## Corrections

* **C1 (domain of the block supply).** THEOREM_MB.md:89 says S_I1 is "admissible on all of E, hence on B_i". That
  is false whenever the outward hull B_i sticks out of E (always possible at the cell ends). S_I1 is admissible on
  E ∩ B_i ⊇ E_i. Restate §6 (:86-94): "S_i is admissible on E ∩ B_i", and "a componentwise minimum of triples
  admissible on D_1, …, D_k is admissible on ∩ D_k". Theorem MB is unaffected, because item 1 (:102) already uses
  t ∈ E ∩ B_i.
* **C2 (dominance chain premise).** :118-120 assert Γ_C5T(S_I1) ≤ Γ_frozen(S_I1). That requires M_k = mag(H_final),
  with H_final the consumed enclosure, i.e. everything the consumer intersects (REVIEW_TPT_R1 N7; tpt.py:319-328).
  :99 allows "any valid whole-cell enclosure", which is enough for soundness but not for the chain. State the
  premise.
* **C3 (A0 slot of the D14 member).** §6 item 3 (:91) and Lemma D14-M (:74-81) never say which A0 the D14 member
  contributes. Declaration D14 has no A0 (THEOREM_RLR307.md:93, :217). The pinned assembly outputs
  A0_SUPPLY = min(Ā_eff, C_R) (c1b_certpw.py:337). Either state A0 := min(Ā′_eff, C_R), which is admissible by Lemma
  A0-M and Lemma G at order 0, or state that item 3 contributes (+∞, A1, A2).
* **C4 (TPT-B justification and computed value).** :114 (like THEOREM_TPT.md:141-142) says "within one piece the
  integrand is monotone in s". It is not: t·(−L(t)) need not be monotone. The correct reason is that −L(e0+s)
  (resp. U(e0−s)) is nondecreasing on a piece and t ≥ x_lo > 0, so the integrand changes sign at most once, from −
  to +, and the running integral is quasi-convex on the piece. Also state that (i) the endpoint-only rule of
  Corollary TPT-M is invalid under non-monotone block constants (T3(3), control K2), and (ii) with a K1 cap the
  computed P*_B is an upper bound (non-binding-side split), not "the maximum" of :107-108.
* **C5 (cell identity).** TC-P and the K5-B direct clause live on the K1 cell [e0 − ρ, e0 + ρ]; the block partition
  and "sup over E" live on the cover cell E. Add E = [e0 − ρ, e0 + ρ] as an exact-rational premise of §7 (:98),
  enforced by a gate in the consumer.
* **C6 (implementation, obligation O3).** `tpt.penalty_blocked` enforces the pointwise-empty-intersection refusal
  only with the CellProfile's own constants at s = 0 (tpt.py:391, :208-215). A frozen TPT-B consumer must refuse
  when max(H_final.lo, lo_i(s_a)) > min(H_final.hi, hi_i(s_a)) on any piece, where s_a is the piece's inner end and
  i its triple. Planted control K4 shows the current code accepts such an input.

## Notes

* **N1.** Lemmas Dv′-M and D14-M add no new mathematics: they are Dv′ r2 and D14 with Ā := min(Ā_B, U), which
  satisfies the only hypothesis used (Λ(e) ≤ Ā on the block).
* **N2.** :53-55, "Only the whole-kernel value U = W(a) … transfers", is narrower than Lemma M-U. Any certified
  upper bound on Λ(b) transfers: τ(b)/D_lo(b), Ā_eff(b), A0_SUPPLY(b). Nothing else transfers, as MB says.
* **N3.** At certifier level the pinned code also uses Ā in D_lo_SM = τ_a,lo/Ā and in Λ_lo (c1b_certpw.py:228-230).
  Both use Ā only as an upper bound on Λ, so a smaller valid Ā′ gives a larger but still valid D_lo and Λ_lo. MB r0
  keeps the block-certified D_lo, which is sound. If an implementation re-derives D_lo from Ā′, it must declare that
  as a change to a certifier output. "Ā enters only through Step 3 and Ā_eff" (:76-77) is true of the proof, not of
  the certifier.
* **N4.** penalty_blocked takes the componentwise **max** over blocks containing a piece (tpt.py:423, :433). The
  **min** is also sound and never larger. Cutting at E_i ends rather than hull ends removes the overlap pieces.
* **N5.** The symbol U is used for the Λ bound (§2-§5) and for the upper profile U(t) (:106). Rename one of them.
* **N6.** Every constant and Λ are even (Lemma S; Theorem M), so kernel-e versus K5-B-e sign conventions are
  harmless. A protocol must still fix the map explicitly and read "B ⊆ [b, ∞)" in |e|.
* **N7.** Γ_MB also bounds g(x_k), so it could cap the chain clause γ_k. MB r0 keeps to the direct clause, the
  adoption quantity (REVIEW_TPT_R1 N11). Keep it that way unless a consumer states otherwise.
* **N8 (governance, not mathematics).** M-U accepts U certified at any b ≤ b_i, including drifts below the
  quarantine band. In this research namespace any such transfer into the band is forbidden (T1/T3). In a formal
  protocol, U should be certified at b_i inside the granted execution, and the envelope rule should be restricted to
  pre-declared blocks, so that no choice depends on a result.
* **N9.** The T5 numerics are float and non-rigorous. They support Theorem M (0 violations from the atom and the
  diagonal, 7/7 MC pairs resolved) and show that the detectors fire off the diagonal.

## T1. Theorem M reconstruction

**Reviewed objects (sha256 prefixes).** THEOREM_MB.md `d8e88f9d` (commit b6ab352e); THEOREM_AD.md `e1895b32`;
THEOREM_RLR307.md `f0c51d6b`; THEOREM_TPT.md `48862378`; tpt.py `05cebc9c` (= the r2 pin of THEOREM_TPT.md:177).

**Statement (as it must be read).** Kernel of THEOREM_MB.md:19-22 (= THEOREM_RLR307.md:19-28): K = 1/2, H = 5,
C = H + K = 11/2, z_t = r_t − e with r_t i.i.d. N(0,1) (so Z + e ~ N(0,1)), update T(x,z) = ((p+z−K)⁺, (m−z−K)⁺),
survival window A(x) = [m − C, C − p]. For the chain started at a = (0,0), every n ≥ 0 and 0 ≤ e ≤ e′:
P_e(τ > n) = P_{−e}(τ > n) ≥ P_{e′}(τ > n); hence Λ(e) = Σ_{n≥0} P_e(τ > n) = (R_e 1)(a) is even and nonincreasing
on [0, ∞). Assumptions actually used: i.i.d. Gaussian increments with the drift entering only as a shift; equal
arm thresholds H and reference K on both arms; start with p0 = m0 (atom, or diagonal per review C2). Nothing else
(finiteness of Λ is not needed for the termwise inequality; Lemma T gives it anyway).

**Re-derivation (mine, independent of EXCLUSION_308).**
1. *Window = unclipped-update alarm.* p + z − K ≤ H ⇔ z ≤ C − p and m − z − K ≤ H ⇔ z ≥ m − C, so "no alarm at
   this step" is exactly z ∈ A(x), with survival at equality on both sides: the same closed window as K_e
   (THEOREM_MB.md:21 and :38-39 are CORRECT). Because H > 0, max(0, u) > H ⇔ u > H, so alarm on the clipped or on
   the unclipped value is the same event.
2. *Lemma V.* With S_0 = 0, S_t = z_1 + … + z_t and the unkilled Lindley recursion from p_0 = m_0 = 0, induction gives
   p_t = max_{0≤s≤t} [(S_t − S_s) − K(t−s)] (the s = t term is the clip at 0), and the same for m with −S. On
   {τ ≥ t} the killed chain equals the unkilled recursion, and its unclipped step-t updates are
   max_{s<t}[±(S_t − S_s) − K(t−s)]. Intersecting the no-alarm events for t = 1..n gives
   {τ > n} = {|S_t − S_s| ≤ H + K(t−s), 0 ≤ s < t ≤ n}. At lag 1 the half-width is H + K = C, matching step 1.
   From (p0, m0) only the s = 0 slabs change, to −(H − m0 + Kt) ≤ S_t ≤ H − p0 + Kt: symmetric iff p0 = m0.
3. *Lemma S.* A_n is a finite intersection of closed slabs {|ℓ(x)| ≤ c}, c > 0: closed, convex, A_n = −A_n,
   bounded (s = 0 slabs), 0 interior.
4. *Law.* S = R − e·v, v = (1,…,n), R = L r ~ N(0, Σ_n), Σ_n[s,t] = min(s,t), det L = 1; density f_n even with
   ellipsoidal superlevel sets. P_e(τ > n) = P(R ∈ A_n + e v) = ∫_{A_n} f_n(y + e v) dy.
5. *Anderson (1955, Thm 1)* with E = A_n, y = e′v, k = e/e′ ∈ [0,1] gives P_e ≥ P_{e′}. Prékopa gives the same
   (x ↦ 1_{A_n}(x − ev) f_n(x) is jointly log-concave in (x, e); its marginal g_n(e) is even, positive and
   log-concave, hence nonincreasing on [0, ∞)). Evenness: A_n = −A_n and R =d −R (or directly the model symmetry
   (z, e, p, m) ↦ (−z, −e, m, p), which fixes a).
6. *Tail sum.* (K_e^n 1)(a) = P_a(τ > n), so Λ(e) = Σ_n (K_e^n 1)(a), and termwise inequalities between nonnegative
   terms pass to the sum.

**Convention checks asked for.** (i) *Increment convention.* Z + e ~ N(0,1) makes S = R − e v; Z − e ~ N(0,1) makes
S = R + e v. Either way P_e(τ > n) = ∫_{A_n} f_n(y ± e v) dy, and evenness makes the two conventions the same
function of |e|. The symmetry argument uses only A_n = −A_n and f_n(x) = f_n(−x), so the convention cannot break it.
(ii) *Ties.* The kernel survives at equality (closed window) and so does (V). Under the open convention (V) holds
with < and A_n is replaced by its interior, still convex and symmetric. In any case a slab boundary has Lebesgue-null
preimage (R has a density), so ties change no probability. (iii) *Equal K and H on both arms* (C = 11/2 on both
sides of A(x)). An asymmetric kernel (H₊ ≠ H₋ or K₊ ≠ K₋) would break A_n = −A_n even from the atom; not the case.

**Review history.** EXCLUSION_308 §c was reviewed by `OV/reviews/REVIEW_THEOREM_M_R1.md` (ACCEPTED_WITH_CORRECTIONS,
no blockers; its §1.1–1.5 check Lemma V, Lemma S, the law, Anderson/Prékopa and the tail sum; §2 non-target
numerics; §2.3 off-atom negative controls). Corrections and their application (checked by me; I grepped §b with
digits masked, because §b carries committed tail figures): **C1** (e_lo is optimal only for the truth, not for every
lower-bound route) applied at EXCLUSION_308.md:132-133 and :197; **C2** (Theorem M also holds from every diagonal
start p0 = m0 = c, 0 < c ≤ 2) applied at EXCLUSION_308.md:313-316 and in the §c header :213-218; **N3** (cross-cell
juxtaposition in the §b.1 row "C7 E2 / E2c") re-worded at :141, so that no committed ceiling of another cell is set
against a 308 quantity. N4 (withdrawn cross-cell "entailment") is recorded as
`OV/ledger/INCIDENT_02_C2A_CROSS_CELL_FLOOR.md`; N5 became QUARANTINE_AMENDMENT_2 (inherited here as T1–T4).
**Unresolved conditions:** none for the mathematics. The scope limits remain binding and are correctly restated at
THEOREM_MB.md:35-36: atom or diagonal start only; nothing about sup_x E_x[τ] (hence nothing about C_R, C_upper or
Lemma G's A0), τ_a, D, C_T, derivatives, or the size of Λ′.

**T1 verdict: Theorem M is correct as restated in THEOREM_MB.md §1.** The restatement at :29-30 matches
EXCLUSION_308 §c.6, and the kernel-consistency paragraph at :38-39 is right.

## T2. Lemmas M-U, A0-M, Dv'-M, D14-M

**Lemma M-U (THEOREM_MB.md:41-47): CORRECT.** For e ∈ B ⊆ [b, ∞), b ≥ 0: Λ(e) ≤ Λ(b) ≤ U (Theorem M, e ≥ b ≥ 0).
Mirror by evenness. The only property of U used is U ≥ Λ(b) for the exact drift b; a certificate computed on a small
drift ball around b (the certifier's `e_r > 0` mode, `c1b_certpw.py:72-73`) also gives it.

**Monotone envelope (:49-51): CORRECT.** For i ≤ j, b_i ≤ b_j, so for e ≥ b_j: Λ(e) ≤ Λ(b_i) ≤ U_i; take the
minimum over i ≤ j. Strict ordering of the b_i is not needed. Result-free, as claimed.

**"Only Λ transfers" (:53-55): CORRECT in substance, too narrow in wording (N2).** Theorem M covers only
P_a(τ > n) and hence Λ; τ_a = E_a[τ ∧ T_a] (taboo event not convex: EXCLUSION_308 §c.8), D = τ_a/Λ, C_T and C_R
(suprema over all starts, where monotonicity fails: §c.8 and REVIEW_THEOREM_M_R1 §2.3), D1, D2 (derivatives) and
L1, L2 (taboo score functionals) are not covered, so none of them, computed at the single drift b, is a block-uniform
input (T2(c): **confirmed**). But the text's "Only the whole-kernel value U = W(a) … transfers" is narrower than
Lemma M-U itself: *any* certified upper bound on Λ(b) transfers, e.g. τ(b)/D_lo(b), Ā_eff(b), or the certifier's
A0_SUPPLY(b) = min(Ā_eff, C_R)(b) (`c1b_certpw.py:337`), because each is ≥ Λ(b). Harmless (conservative), but a
freeze should state the rule as "any certified upper bound on Λ at b".

**Lemma A0-M (:57-61): CORRECT.** |[R_e f](a)| = |ν_e(f)|/D_e ≤ (τ_a/D)(e)‖f‖ = Λ(e)‖f‖ (THEOREM_AD.md:50-51,
Lemma SM(c)-(d)); or directly R_e = Σ K_e^j ≥ 0 gives |R_e f(a)| ≤ (R_e 1)(a)‖f‖. Then Λ(e) ≤ U on B.

**Lemma Dv′-M (:63-72): CORRECT; it is an instance of Lemma Dv′ r2, not a new lemma.** T2(a): Lemma Dv′ r2
(THEOREM_AD.md:83-89) bounds each of the five quotient-rule terms by (τ_a/D)(e) × (tame factor):
|ν′/D| ≤ (τ_a/D)κ₁C, |νD′/D²| ≤ (τ_a/D)(|D′|/D), |ν″/D| ≤ (τ_a/D)(2κ₁²C² + κ₂C), |2ν′D′/D²| ≤ 2(τ_a/D)κ₁C(|D′|/D),
|ν(2D′²/D³ − D″/D²)| ≤ (τ_a/D)(2(D′/D)² + |D″|/D). The tame factors use ‖Ĝ_e‖ ≤ C_T, |D′|/D ≤ D1/D_lo,
|D″|/D ≤ D2/D_lo (block-uniform) and κ_n (e-free). The Ā hypothesis enters only as the scalar inequality
(τ_a/D)(e) = Λ(e) ≤ Ā at each e ∈ E. **No pointwise-in-x property of the supersolution W is used** (W enters only
through W(a) ≥ Λ(e), THEOREM_AD.md:91-92). With Ā := min(Ā_B, U), Ā ≥ Λ(e) on B by M-U, so Dv′ r2 applies
verbatim. The A0/A1/A2 formulas at :70-71 match THEOREM_AD.md:86 term by term. Ā_B = +∞ when absent is fine (then
Ā′ = U).

**Lemma D14-M (:74-81): CORRECT at the theorem level; one certifier-level fact is missing (N3), and the A0 slot of
the D14 triple is unspecified (C3).** T2(b), theorem level: in THEOREM_RLR307 §2, Ā appears only in Step 3
(THEOREM_RLR307.md:128-139, "Λ(e) ≤ Ā") and through Ā_eff in Steps 3-4 (:136-148, e.g. |νD′/D²| ≤ Ā_eff δ₁ uses
|ν|/D ≤ τ_a/D = Λ ≤ Ā_eff). Step 5 (Lemma G) uses C_R = sup_R W (:155), which is a sup over all states and is **not**
covered by Theorem M; MB correctly keeps C_R block-uniform (:80-81, and §6 item 4 at :92). Step 6 (Lemma Lad) takes a
minimum of upper bounds, so min(Ā, U) is the same operation. The implemented assembly also uses Ā only through
A_eff (`c1b_certpw.py:308-309`; pinned sha256 48080dd4…, matching `rlr307_pinned.py:31`).
T2(b), certifier level: the pinned certifier uses Ā at two further places, **inside the production of D14 inputs**:
`D_lo_SM = τ_a,lo / Ā` and `D_lo = max(D_lo_tame, D_lo_SM)` (`c1b_certpw.py:229-230`), and
`Λ_lo = max(W̃(a) − Ā·max(r̄_W, 0), (1 − z_W)W̃(a))` (:228). In both, Ā is used only as an upper bound on Λ(e) at the
same drifts where τ_a,lo (resp. the residual bound) holds: D(e) = τ_a(e)/Λ(e) ≥ τ_a,lo/Ā, and
Λ = W̃(a) − (R r)(a) ≥ W̃(a) − Λ·r̄_W⁺ ≥ W̃(a) − Ā·r̄_W⁺. A **smaller** Ā gives a **larger** D_lo and Λ_lo, and this
direction is **sound** for every Ā′ ≥ sup_B Λ, which min(Ā_B, U) is. So (i) MB r0 as written (D_lo taken from the
block certificate computed with Ā_B) is sound, and (ii) recomputing D_lo_SM with Ā′ would also be sound; but (ii) is
a change of a certifier output, and the text "Ā enters only through Step 3 and Ā_eff" is true of the proof, not of
the pinned certifier. No place uses Ā as a lower bound; no place uses sup_x W except C_R.
T2(c): see "Only Λ transfers" above — confirmed; none of τ, C_T, D_lo, D1, D2, L1, L2, C_R at a single drift
transfers to a block.

## T3. Theorem MB

**(1) (P4) is used only pointwise in t: CONFIRMED.** In THEOREM_TC §4 the atom constants appear only in step 3
(THEOREM_TC.md:80: |E″(e)(a)| ≤ A0‖φ″(e)‖ + 2A1‖φ′(e)‖ + A2‖φ(e)‖, i.e. (P4) at the single drift e with the fixed
functions f = φ″(e), φ′(e), φ(e)). Step 1 (:73-75) uses (P1)-(P3) and |t| ≤ ρ only; step 2 (:76-79) uses the error
identities and existence/analyticity of R_e (true at every e: Λ(e) < ∞ and Lemma SM(b)), not the constants; step 4
(:82-84) is interval assembly. THEOREM_TCT.md:41-42 says the same for TC-T; (P2′) and (P3′) (:44-117) involve k_i,
j_i, σ3, σ4, not A. Lemma TC-P (THEOREM_TPT.md:84-102) keeps s = |t − e0| and uses the constants only in that step-3
inequality at t. So a triple admissible at t (any block whose certified domain contains t, or the componentwise
minimum of several) is enough, and MB item 1 (THEOREM_MB.md:102-105) is correct. Ĝ ≡ 0 on the TC-T path is (P2′)
(THEOREM_TCT.md:46-57), so the centre-motion term vanishes. REVIEW_TPT_R1 N16 reached the same conclusion.
*Hidden premise (C5):* TC-P lives on the K1 cell [e0 − ρ, e0 + ρ] and the block partition on the cover cell E.
MB §7 (:98) asserts "midpoint e0, half-width ρ" of E but never states E = [e0 − ρ, e0 + ρ] as an exact identity to
be gated. (cells.json stores e0, ρ, left, right as exact rationals; on the non-target CUSUM cells 1 and 2, which I
inspected, left = e0 − ρ and right = e0 + ρ exactly.)

**(2) Intersection with H_final: CORRECT.** lo_i(s) ≤ R″_m(t) ≤ hi_i(s) (TC-P with block i's triple, assembled with
the frozen nonnegative coefficients and the whole-cell W enclosures, THEOREM_TPT.md:104-110) and H_final ∋ R″_m(t);
the intersection of two valid enclosures of the same number is valid. Under valid inputs it is non-empty at every t.
*Implementation gap (C6):* `tpt.penalty_blocked` refuses an empty intersection only with the constants stored in the
CellProfile, at s = 0 (tpt.py:391 → :208-215), not with each piece's constants at the piece's inner end, where a
small-constant block profile is narrowest. My planted control K4 (a cap disjoint from a zero-constant block profile
at s = 5/100) was **accepted** and returned a value. This is the REVIEW_TPT_R1 N5 fail-closed rule, lost for blocks.
Notation: MB reuses "U" for the Λ bound (§2-§5) and for the upper profile U(t) (:106) — rename (N5).

**(3) TPT-B with block constants that decrease across boundaries: VALID; the piece-end rule is exact for the true
integrand and necessary.** On one piece the triple is fixed, all profile coefficients and A^(i) are ≥ 0, so lo_i(s)
is nonincreasing and hi_i(s) nondecreasing in s, and −L(e0+s) = min(−H_final.lo, −lo_i(s)) and
U(e0−s) = min(H_final.hi, hi_i(s)) are nondecreasing in s. The integrand t·(−L(t)) itself is **not** monotone (t
grows; with −L < 0 the product decreases), so MB :114 and THEOREM_TPT.md:141-142 ("the integrand is monotone") are
literally wrong (C4). What holds is that its sign changes at most once, from − to +, because t ≥ x_lo > 0. Hence the
running integral restricted to a piece is decreasing then increasing (quasi-convex), its maximum over the piece is at
a piece end, and sup over a side = max over all piece ends (e0 contributes 0). Jumps of −L between pieces, in either
direction, are irrelevant. So "max over piece ends" is exact for the true integrand. The endpoint-only rule of
Corollary TPT-M (max(0, I(ρ))) is **not** valid under non-monotone blocks. My control K2 fires: on a synthetic cell
with a high-constant block next to e0 and low constants beyond, the endpoint rule gives 0.2044 (0.2009 with a binding
cap) against a true sup of 0.2485 (0.2450).
*`penalty_blocked` (tpt.py:382-436) implements the piece-end rule correctly.* (a) It cuts at every block end strictly
inside (e0, x_hi) and (x_lo, e0), plus e0 and the cell ends (:417-418, :427-428). (b) Each piece gets the
componentwise max over blocks containing its midpoint (:422-423); every such block contains the whole piece, because
no block end lies inside a piece. The max is sound; the min would also be sound and tighter (N4). (c) The running sum
is updated and the best value kept at every piece end (:419-425, :429-435). (d) K1 cap per piece (:397-413): the
crossing of that piece's own polynomial with the cap is found on [0, ρ] by a 60-step bisection that returns a point
on the non-binding side (:183-205). The piece uses the profile before that point and the cap after it. On
[crossing′, true crossing] the cap over-estimates −L (resp. U), and t > 0, so each piece integral is ≥ the true one.
The computed P*_B is therefore a **valid upper bound**, not the exact maximum (C4: say so at :107-108). (e) The
bisection returns the last grid point before the crossing, a monotone function of the polynomial. So the computed
integrand is pointwise nondecreasing in the block constants, and computed monotonicity and dominance hold too, not
only the true ones. Control K1: against an independent dense float evaluation (own profile code, own block
selection, midpoint rule with N = 200000), penalty_blocked agrees to within float noise (relative gap +4.5e-13
without a cap and −5.3e-12 with a binding cap; check tolerance 1e-9 absolute). K3: P*_B ≤ penalty_closed
with the cell-max constants (both cases). (`scratch_MB_R1/t3_tptb_check.py`, `out_t3_tptb.json`; ledgered.)

**(4) Γ_MB bounds sup_E g_m, the K5-B direct-clause quantity: CORRECT.** K5_GLOBAL_BRIDGE.md defines
g(e) = R(e) − eR′(e), g′ = −eR″, and the direct test Γ_k = hi(R_k − e0_k·D_k) + ρ_k x_k M_k < 0, whose proof (step 2)
shows g ≤ Γ_k on C_k. With g(e0) ≤ g_hi = hi(R_k − e0 D_k): for e ≥ e0, g(e) − g(e0) = −∫_{e0}^{e} tR″ ≤ ∫ t(−L);
for e ≤ e0, g(e) − g(e0) = ∫_{e}^{e0} tR″ ≤ ∫ tU (t > 0). Hence g_m ≤ g_hi + P*_B on E. Γ_MB is the same kind of
upper bound on the same function over the same cell, and Γ_MB < 0 gives g_m < 0 on the cell, which is all that
K5-B's conclusion (step 3) needs from the cell. MB leaves the chain clause γ_k alone (N7).

**(5) Dominance chain: CORRECT given one missing premise (C2).** Monotonicity: rad^(i)(s) is linear in A^(i) with
coefficients p_j(s) ≥ 0, so −L and U are pointwise nondecreasing in the constants, the running integrals are
pointwise nondecreasing (t > 0), and so is their sup (and, by (3e), so is the computed value). S_i ≤ S_I1 by
construction, because S_I1 is one of the members of the min. So P*_B ≤ P*_TPT(S_I1), where TPT-M is exact for the
constant triple. P*_TPT ≤ P_C5T is TPT-D (THEOREM_TPT.md:70-73), valid because L ≥ H_final.lo and U ≤ H_final.hi by
construction. The last link, P_C5T ≤ ρ x_hi M_k, holds only if M_k = mag(H_final), i.e. H_final is everything the
consumer intersects (REVIEW_TPT_R1 N7; `tpt.penalty_frozen` enforces it when M_consumed is supplied, tpt.py:319-328).
MB :118-120 says only "the same enclosure inputs" and must state this. Soundness of Γ_MB does not depend on the
chain.

## T4. Missing premises

| premise | status in MB r0 | finding |
|---|---|---|
| x_lo > 0 | stated (:85, :98); enforced by `tpt._check` (tpt.py:171-172) | OK. It is needed twice: for the sign of t in TPT/TPT-B, and for b_i ≥ 0 in M-U. |
| b_i ≥ 0 for dyadic hulls | stated (:86) | OK. The outward 2^-20 hull of E_i ⊆ [x_lo, x_hi] with x_lo > 0 has b_i = ⌊2^20·lo_i⌋/2^20 ≥ 0. It must be computed in exact rationals and must be outward (b_i ≤ lo_i), or E_i ⊄ B_i (THEOREM_RLR307 Lemma H). |
| U certified at b_i itself | implicit | M-U needs U ≥ Λ(b) for some b ≤ min(domain of use). A certificate at a drift b > b_i covers only [b, ∞) ∩ B_i. That is still fine if b ≤ lo(E_i) and the triple is used only on E_i. State the domain. |
| E = [e0 − ρ, e0 + ρ] exactly | missing | **C5.** TC-P and the direct clause live on the K1 cell, and the blocks on the cover cell. Gate the identity. |
| domain of S_i | :89 wrong | **C1.** S_I1 is admissible on E, not on B_i ⊄ E. S_i is admissible on E ∩ B_i ⊇ E_i. Harmless for §7, which uses t ∈ E ∩ B_i only. |
| componentwise min of admissible triples | stated (:94) | TRUE on the **intersection** of the members' domains: (P4) is three separate inequalities, and the consumer (TC-P radius) is nondecreasing in each A_j with coefficient p_{2−j}(s) ≥ 0. Composition with the committed supply is therefore sound. |
| A0 slot of the D14 member | missing | **C3.** Declaration D14 has no A0 (THEOREM_RLR307.md:93, :217); the pinned assembly has A0_SUPPLY = min(Ā_eff, C_R) (c1b_certpw.py:337). |
| H_final, M_k | "any valid whole-cell enclosure" (:99) | Enough for soundness. The dominance chain needs H_final = the consumed enclosure and M_k = mag(H_final) (**C2**). |
| exact arithmetic | "exact rationals" (:110) | OK: profile polynomials and integrals are exact (`pint`), the cap split is a rational point, κ₁ and κ₂ are rational upper bounds (THEOREM_RLR307.md:71-72), U comes from an exact-rational certificate, and the test Γ_MB < 0 is exact. The computed P*_B is an upper bound, not the maximum (C4). Floats or Monte Carlo never qualify as U (REVIEW_THEOREM_M_R1 §1.6(5)). |
| sign conventions (Lemma S) | not addressed | OK mathematically: every constant is even (THEOREM_RLR307.md:105-111), and so is Λ (Theorem M), so kernel e and K5-B e may differ by a sign. A protocol must still fix the map and read "B ⊆ [b, ∞)" in \|e\| (N6). |
| existence of R_e on E | implicit | OK: Λ(e) < ∞ and the taboo resolvent exist for every e (Lemma T, SM(b)). TC step 2 needs only this. |

No hidden premise found that breaks soundness. The misstatements (C1, C3, C4) are local and do not affect Theorem
MB's conclusion, because §7 uses each triple only on E ∩ B_i and only through the separate (P4) inequalities.

## T5. Numerical sanity (non-rigorous, non-target drifts only)

Script `scratch_MB_R1/t5_theorem_m_numerics.py`, output `out_t5_theorem_m.json` (float, stdlib). The drifts are only
{0, 1/4, 1/2, 1, 11/10, 27/10, 3, 7/2}; `guard_drift` is called on each before any evaluation; the run is ledgered
(class REVIEW, agent reviewMB). **No atom-start value of Λ, E_a[τ] or P_a(τ > n) is written here**; for the atom I
report only violation counts, signs and z-scores. Nothing below is compared with any tail-cell figure.

| check | atom | diagonal (1,1), (2,2) | off-diagonal (1,0), (5/2,0), (5,0), (2,1) |
|---|---|---|---|
| N1: exact n = 1, survival nonincreasing along the 8 drifts | 0 violations | 0 / 0 | **2 / 4 / 5 / 2 violations**, starting at the pair (0, 1/4) |
| N2: n = 2 by Gauss-Legendre (split at the clip kinks) | 0 violations | 0 / 0 | **1 / 2 / 4 / 1 violations**, starting at (0, 1/4) |
| N3: d/de P(τ > 1) at e = 0 (closed form φ(C − p0) − φ(C − m0)) | 0 | 0 / 0 | **+1.6e-5 / +4.43e-3 / +0.352 / +8.6e-4** |
| N3: d/de P(τ > 2) at e = 0 (differentiated integrand; the window is e-free) | 0 (float) | 0 / 0 | **+1.03e-3 / +2.84e-2 / +0.463 / +9.7e-3** |
| N4: MC E[τ], 3000 paths, common random numbers; paired z of E(e_j) − E(e_{j+1}) for the 7 consecutive pairs | all 7 positive, z = 31 to 80 (monotone decrease resolved) | — | — |
| N5: MC evenness at e = 1/4 via the reflection (p, m, e) ↦ (m, p, −e) | same-start null baseline z = −0.07 (cannot fail by construction; not evidence) | (2,2): null baseline z = −0.07 | (5,0) vs (0,5): **98.4 vs 49.7, z = 18.9** (not even) |

Reading. The monotonicity from the atom and from diagonal starts holds on every exact n ≤ 2 comparison and on every
MC pair. From off-diagonal starts (p0, 0), p0 > 0, the survival probability **increases** in e near 0. The derivative
at 0 is strictly positive and matches the closed form φ(C − p0) − φ(C) of EXCLUSION_308 §c.8 (and REVIEW_THEOREM_M_R1
§2.3: +1.6e-5, +0.00443, +0.352). Evenness fails there. So the numerics detect the predicted counterexample, and the
detectors can fire. As REVIEW_THEOREM_M_R1 N2 found, the E-level failure off the diagonal is local near e = 0 and is
not expected to show at this drift spacing. I tested it only at the P level and through evenness.

## X. Reviewer exposure, runs and limits

**Exposure (disclosed, not used).** While reading the assigned sources I saw committed tail-cell figures in:
EXCLUSION_308.md §a.1 (lines 52-69, read before I masked digits; it carries the committed cover interval and a
committed float of a cell-308 critical constant); THEOREM_TCT.md (per-cell numeric ranges for cells 305-309 in §1,
§2, §3, §5 and §6); REVIEW_TPT_R1 N12 (one committed cell-306 figure); `code/c308_quarantine.py` (the TAIL_FIGURES
definitions) and `config/TARGET_QUARANTINE_308.json` (the cover interval). After that I read §b of EXCLUSION_308 only
through a digit-masked grep. None of these figures entered any computation, script, brief or sentence of this
review. No tail-cell number is written here. My verdict does not depend on any value: it concerns only the validity
of the inequalities.

**Runs (all ledgered: class REVIEW, agent reviewMB).**
* `scratch_MB_R1/t3_tptb_check.py`, three runs. Run 1 had no interior peak, so its K2 control could not fire; I
  redesigned it. Run 3 repeats run 2 after one change: the synthetic block end 305/100 was rewritten as 61/20 (the
  same value), because the scanner flagged the integer 305 as a cell literal. Runs 2 and 3 give identical results,
  and those are the ones reported.
* `scratch_MB_R1/t5_theorem_m_numerics.py`, once.
* Two restricted scans of `reviews/` with `c308_quarantine._scan_tree` (planted controls on). The final scan gives
  PASS: 2 .py and 5 text files scanned, 0 findings, and both negative controls detected. It reports 9 report-only
  "attention drift literal" items: the start states 2.0 and 2.5 in t5, which are states, not drifts.

Stdlib Python 3 with `-I -B`; no network, no remote host, no git add or commit. Inputs are synthetic, or the declared drifts
{0, 1/4, 1/2, 1, 11/10, 27/10, 3, 7/2}. I also read the fields e0, rho, left and right of the committed non-target
CUSUM cells 1 and 2 in `p5y_k1_cover_ledger_successor/config/cells.json` (for C5). I opened none of the files
TCT_INPUTS_30*, C2_D5_FORECAST*, REGISTRY_C1*/C2* or RLR307 result/evidence.

**What I could not check.** The pinned certifier's S1-S4 implementation (outside O1's scope; reviewed in
REVIEW_RLR_R2 and REVIEW_RLR_R3_VERIFY). Anderson (1955) is taken as cited; the Prékopa route is independent. The
E-level monotonicity failure off the diagonal is local near e = 0 and is not resolvable at the declared drift
spacing (REVIEW_THEOREM_M_R1 N2).
