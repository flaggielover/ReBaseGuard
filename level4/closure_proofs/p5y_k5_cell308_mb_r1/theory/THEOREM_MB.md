# Theorem MB — Theorem-M block atom constants and their block-resolved transport (r1)

**Status.** r1 applies the independent proof review `reviews/REVIEW_THEOREM_MB_R1.md`
(THEORY_ACCEPTED_WITH_CORRECTIONS on r0 = blob of commit `b6ab352e`): corrections C1–C6 and notes N2–N6, N8.
Obligation O1 is discharged subject to these corrections (review summary). No blocker was found.
It states what the certificates prove and **nothing about the value of any consumer output** at any cell.
No number of any CUSUM m = 5 tail cell appears in this file.

| rev | change |
|---|---|
| r0 (`b6ab352e`) | first draft |
| r1 | C1 domains (E ∩ B_i); C2 dominance premise M = mag(H_final); C3 A0 slot of the D14 member; C4 TPT-B justification and "upper bound" wording, endpoint-only rule invalid; C5 cell identity gate; C6 per-piece emptiness refusal as a consumer obligation; N2 any certified bound on Λ(b) transfers; N3 declared D_lo refresh (Lemma DM); N4 tiling by the exact sub-intervals E_i and min over members; N5 notation U_Λ; N6 sign map; N8 certificates only at pre-declared block drifts |

Sources (unchanged from r0):

| source | what is used | status there |
|---|---|---|
| THEOREM_AD (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`) | Lemma K, T, SM (a)–(d), Dv, Dv′ r2, whole-kernel supersolution | adopted |
| THEOREM_TC / THEOREM_TCT | premises (P1), (P2′), (P3′), (P4); (P4) used only at TC §4 step 3, pointwise in t (THEOREM_TC.md:80) | adopted; confirmed by REVIEW_THEOREM_MB_R1 T3(1) |
| Theorem M (`p5y_k5_tail_overnight_research/streams/C_308/A0X/EXCLUSION_308.md` §c) | P_e(τ > n) even and nonincreasing in \|e\| from the atom | REVIEW_THEOREM_M_R1 ACCEPTED_WITH_CORRECTIONS (applied); re-derived independently in REVIEW_THEOREM_MB_R1 T1 |
| THEOREM_RLR307 (`p5y_k5_cell307_rlr_r1/theory/THEOREM_RLR307.md`) | declaration D14, Lemma S, H, Lad | accepted through the cell-307 campaign |
| THEOREM_TPT (`p5y_k5_tail_overnight_research/streams/E_assembly/THEOREM_TPT.md`) | Theorem TPT, Lemma TC-P, Theorem TPT-B, Proposition TPT-D | REVIEW_TPT_R1: sound |

## 0. Objects

As THEOREM_RLR307 §0. State x = (p, m) ∈ R = {0 ≤ p, m ≤ 5 : p = 0 or m = 0 or p + m ≤ 4}; K = 1/2, H = 5,
C = H + K = 11/2; increment Z with Z + e ~ N(0, 1); T(x, z) = ((p + z − K)⁺, (m − z − K)⁺); alarm-free window
A(x) = [m − C, C − p] (survival at equality); (K_e f)(x) = ∫_{A(x)} f(T(x, z)) φ(z + e) dz; atom a = (0, 0);
R_e = (I − K_e)⁻¹; Λ(e) := E_a[τ](e) = (R_e 1)(a) = τ_a(e)/D_e (Lemma SM(d)).

A triple (A0, A1, A2) is **admissible on a drift set E** if |[∂_e^j R_e f](a)| ≤ A_j‖f‖ for every e ∈ E, every
f ∈ B(R) and j ∈ {0, 1, 2} (P4). A componentwise minimum of triples admissible on D_1, …, D_k is admissible on
D_1 ∩ … ∩ D_k ((P4) is three separate inequalities).

**Sign map (N6).** Every constant used here is even in e (THEOREM_RLR307 Lemma S) and so is Λ (Theorem M); every
statement "B ⊆ [b, ∞)" is read in |e|. A protocol must still fix the map between the kernel's e and the cover's e
explicitly.

## 1. Theorem M (restated)

For the chain started at the atom, every n ≥ 0 and 0 ≤ e ≤ e′: P_e(τ > n) = P_{−e}(τ > n) ≥ P_{e′}(τ > n). Hence Λ
is even and nonincreasing on [0, ∞).

*Proof outline* (EXCLUSION_308 §c.2–c.6; independently re-derived in REVIEW_THEOREM_MB_R1 T1). From the atom,
{τ > n} = {|S_t − S_s| ≤ H + K(t − s), 0 ≤ s < t ≤ n} (Lindley recursion unrolled; alarm on the unclipped update,
which is exactly z ∉ A(x)); the set is closed, convex and centrally symmetric; S = R_n − e(1, …, n) with R_n Gaussian,
even and with convex superlevel sets; Anderson's inequality (or Prékopa) gives the monotonicity; the tail-sum formula
gives Λ. Assumptions used: i.i.d. Gaussian increments with the drift as a shift; equal H and K on both arms; a start
with p0 = m0. **Scope:** atom (and diagonal) starts only; nothing about off-diagonal starts, sup_x E_x[τ], C_R,
C_upper, τ_a, D, C_T, derivatives, or the size of Λ′.

## 2. Lemma M-U (one drift controls a block)

Let b ≥ 0 and let **U_Λ** be any certified upper bound U_Λ ≥ Λ(b). Then for every set B ⊆ [b, ∞):

    sup_{e ∈ B} Λ(e) ≤ U_Λ.

By evenness the same holds for B ⊆ (−∞, −b]. *Proof.* Theorem M. ∎

**What may serve as U_Λ (N2).** Any certified upper bound on Λ at the exact drift b: the whole-kernel supersolution
value W(a) (W ≥ 1 + K_b W, W ≥ 0; THEOREM_AD §4), a certified τ(b)/D_lo(b) at that single drift, or their minimum.
**Nothing else computed at the single drift b transfers to B**: not τ, C_T, D_lo, D1, D2, L1, L2, C_R (Theorem M does
not cover taboo quantities, sup_x quantities or derivatives). A float or Monte-Carlo value never qualifies.

**Monotone envelope.** If b₀ < b₁ < … < b_k are the pre-declared block drifts (all ≥ 0) with certified
U_i ≥ Λ(b_i), then Ū_j := min_{i ≤ j} U_i ≥ sup_{e ≥ b_j} Λ(e). The rule is result-free.

**Governance note (N8).** Lemma M-U would accept a U_Λ certified at any drift b below a block, including drifts below
the quarantine band. In this research namespace any such transfer into the band is forbidden (quarantine T1/T3). In a
formal protocol, U_Λ is certified at the pre-declared block drifts b_i **inside the granted execution**, and the
envelope ranges only over those pre-declared drifts, so that no choice depends on a result.

## 3. Lemma A0-M (order-0 channel)

With B, U_Λ as in Lemma M-U: A0 := U_Λ satisfies |[R_e f](a)| ≤ A0‖f‖ for all e ∈ B, f ∈ B(R).
*Proof.* Lemma SM(c)–(d): |[R_e f](a)| ≤ Λ(e)‖f‖ ≤ U_Λ‖f‖. ∎

## 4. Lemma Dv′-M (Lemma Dv′ with a Theorem-M Ā)

Lemma Dv′ r2 (THEOREM_AD §4) uses Ā only through the pointwise inequality Λ(e) ≤ Ā on the drift set
(THEOREM_AD.md:83-89; REVIEW_THEOREM_MB_R1 T2, N1). Hence on a block B with certified, B-uniform τ, C_T, D_lo, D1, D2
and U_Λ as in Lemma M-U,

    Ā′ := min(Ā_B, U_Λ),   Ā′_eff := min(Ā′, τ/D_lo),
    A0 = Ā′_eff,   A1 = Ā′_eff (κ₁C_T + δ₁),   A2 = Ā′_eff (2κ₁²C_T² + κ₂C_T + 2κ₁C_Tδ₁ + 2δ₁² + δ₂)

is admissible on B (δ_j = D_j/D_lo; Ā_B a B-uniform whole-kernel certificate, or +∞ if none). ∎

## 5. Lemma D14-M (the RLR block supply with a Theorem-M Ā) and Lemma DM (declared D_lo refresh)

**D14-M.** In THEOREM_RLR307 §1 (declaration D14) and its proof §2, Ā enters only through Step 3 ("Λ(e) ≤ Ā for
e ∈ B") and through Ā_eff = min(Ā, τ/D_lo). Replacing Ā by Ā′ = min(Ā, U_Λ) keeps Step 3 true, so the D14 block
supply computed with Ā′ is admissible on B. **A0 slot (C3):** declaration D14 defines only A1^B, A2^B; the D14
member of §6 contributes **A0 := min(Ā′_eff, C_R)**, admissible by Lemma A0-M and Lemma G at order 0 (C_R = sup_R W of
a **B-uniform** whole-kernel certificate; C_R is never taken from a single-drift certificate). Every other D14 input —
τ, C_T, C_R, τ_a,lo, D_lo, D1, D2, L1_up, L2_up — comes from a **B-uniform** certificate on B, exactly as in
THEOREM_RLR307.

**Lemma DM (declared change to a certifier output; review N3).** For e ∈ B, D_e = τ_a(e)/Λ(e) (SM(d)). With τ_a,lo ≤
inf_B τ_a (B-uniform) and Ā′ ≥ sup_B Λ, D_e ≥ τ_a,lo/Ā′. Hence

    D_lo′ := max(D_lo, τ_a,lo / Ā′)

is a valid B-uniform lower bound on D, and may replace D_lo in Lemma Dv′-M and in D14-M (in δ_j, τ/D_lo and
L_j,up/D_lo). The pinned certifier already computes D_lo = max(D_lo_tame, τ_a,lo/Ā_B); D_lo′ re-evaluates only its
second argument with Ā′. This is declared as a composition-layer change, with its own control (a D_lo′ below the
certifier's D_lo is impossible; a D_lo′ computed with a non-certified Ā′ must be refused).

## 6. Block supply (C1, N4)

Let the cover cell E = [x_lo, x_hi] (x_lo > 0) be tiled by a rule fixed in advance into consecutive exact
sub-intervals E_i (the pieces used by the consumer), with outward dyadic hulls B_i ⊇ E_i (b_i = ⌊2^20·lo(E_i)⌋/2^20 ≥ 0,
computed exactly; THEOREM_RLR307 Lemma H). For each i let S_i be the componentwise minimum of the available members:

1. the committed cell-level supply S_I1 (admissible on E);
2. Lemma Dv′-M on B_i (with D_lo′), when B_i-uniform τ, C_T, D_lo, D1, D2 are certified;
3. Lemma D14-M on B_i (with D_lo′ and the A0 slot of §5), when the RLR block certificate exists;
4. Lemma G on B_i (A0 = C_R, A1 = κ₁C_R², A2 = κ₂C_R² + 2κ₁²C_R³, C_R B_i-uniform).

Then **S_i is admissible on E ∩ B_i ⊇ E_i** (C1). The consumer uses S_i only for t ∈ E_i.

## 7. Theorem MB (composition with the block-resolved transport)

**Premises.** (i) The frozen TC-T premises (P1), (P2′), (P3′) for the K1 cell with midpoint e0 and half-width ρ;
(ii) **E = [e0 − ρ, e0 + ρ] as an exact rational identity (C5; gated by the consumer)**; (iii) x_lo > 0; (iv) the
block triples S_i admissible on E ∩ B_i, with E tiled by the E_i; (v) H_final a valid whole-cell enclosure of R″_m
on E.

1. (Lemma TC-P, pointwise in t.) For t ∈ E_i, s = |t − e0|:
   |F_r″(t)(a) − Ĥ_r(a)| ≤ rad_r^{(i)}(s) := A0^{(i)} p2(s) + 2A1^{(i)} p1(s) + A2^{(i)} p0(s), with the profile
   polynomials p_j(s) of THEOREM_TPT §2 (Ĝ ≡ 0 on the TC-T path, (P2′)). TC uses (P4) only at §4 step 3, pointwise in t,
   so the triple of the piece containing t may be used.
2. (Profile enclosure.) L(t) := max(H_final.lo, lo_i(s)) ≤ R″_m(t) ≤ min(H_final.hi, hi_i(s)) =: U(t).
3. (Theorem TPT-B.) For every e ∈ E, g_m(e) ≤ g_hi + P*_B, where P*_B is the maximum of 0 and of the running
   transport integrals at the piece ends; pieces are [x_lo, e0] and [e0, x_hi] cut at every end of an E_i.
4. Hence **Γ_MB := g_hi + P*_B is a certified upper bound on sup_{e ∈ E} g_m(e)**, the quantity the K5-B direct clause
   bounds by g_hi + ρ x_hi M. If Γ_MB < 0 (exact rationals), then g_m < 0 on E, which is all the K5-B conclusion needs
   from the cell.

*Proof.* (1) Lemma TC-P with (P4) applied at each t with the triple of the piece containing t. (2) intersects two valid
enclosures of the same number. (3) On one piece the triple is fixed and every profile coefficient and A^{(i)} is ≥ 0,
so −L(e0 + s) and U(e0 − s) are nondecreasing in s on that piece. **The integrand t·(−L(t)) is not itself monotone
(C4)**, but because t ≥ x_lo > 0 its sign changes at most once on a piece, from − to +. So the running integral
restricted to a piece is quasi-convex and attains its maximum over the piece at a piece end; jumps of −L between
pieces, in either direction, are irrelevant. Hence the sup over each side equals the maximum over all piece ends
(e0 contributes 0). (4) follows from (3) and g′ = −eR″ (K5_GLOBAL_BRIDGE step 2). ∎

**Implementation statements (C4, C6).**
* The endpoint-only rule of Corollary TPT-M, max(0, I(ρ)), is **invalid** when block constants are not monotone
  across pieces (review control K2 fires). Only the piece-end rule may be used.
* With a K1 cap, the per-piece split at a crossing point on the non-binding side makes the **computed** P*_B a valid
  upper bound on the exact P*_B, not the exact maximum. The computed value is still nondecreasing in every block
  constant (review T3(3e)).
* **Consumer obligation (C6):** the consumer must refuse (STOP, no value) when on any piece
  max(H_final.lo, lo_i(s_a)) > min(H_final.hi, hi_i(s_a)), where s_a is the piece's inner end and i its triple. The
  overnight `tpt.penalty_blocked` checks this only with the cell's own constants at s = 0 (tpt.py:391); the formal
  consumer must add the per-piece check.
* Members of the min over blocks meeting a piece may be combined by componentwise **min** (sound and never larger than
  the max, N4); tiling by the exact E_i removes hull overlaps from the pieces altogether.

**Dominance (C2).** P*_B is nondecreasing in every block constant. If S_i ≤ S_I1 for all i (true by §6 item 1) and
H_final is the **consumed** enclosure with M = mag(H_final), then
Γ_MB ≤ Γ_TPT(S_I1) ≤ Γ_C5T(S_I1) ≤ Γ_frozen(S_I1). Soundness of Γ_MB does not depend on this chain.

## 8. What changes, and the governance class

| item | change |
|---|---|
| K1 records, TC-T inputs (f_*, Env4, W terms, Ĥ_r(a), g_hi, H_final, cover) | **unchanged** |
| atom constants | block-resolved, each a minimum including the committed S_I1 |
| certifier outputs | one declared composition change: D_lo′ (Lemma DM) |
| consumer | the direct clause is replaced by the TPT-B transport, a different certified bound on the same quantity sup g_m; the chain clause is untouched (N7) |
| closure criterion | **unchanged**: a certified upper bound on sup_cell g_m that is < 0 (strict) |
| floor r2 | **closure-only** (consumer and certifiers differ from C2's). No adoption, no r6. |

## 9. Obligations before FREEZE_READY

* O1 — **discharged** by REVIEW_THEOREM_MB_R1 subject to C1–C6 (applied in r1; C6 is carried to O3).
* O2 — a pointwise Λ certifier that is deterministic, persisted and independently re-verifiable (streams A0, VERIFY).
* O3 — the TC-T input extraction and the TPT-B consumer on the frozen path with reproduction gates (stream ASSEMBLY,
  done on decoys), **plus the C6 per-piece refusal and the C5 cell-identity gate**.
* O4 — an independent reconstruction of the composition layers (block supply with Ā′ and D_lo′, envelope, ladder,
  TPT-B integral).
* O5 — incident-independence review (incident 01 applies to any profile transport; COORDINATOR_EXPOSURE_DISCLOSURE).
