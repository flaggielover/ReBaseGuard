# Digest: Cover refinement for the K5-B direct clause (CR-1..3, B2/B2c, DRP-0/DRP-1)

Firewalled digest. Sources (NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`):
`streams/D_309/COVER_REFINEMENT_309.md`, `streams/D_309/code/d309_cover.py` (review items from
`reviews/REVIEW_STREAM_D_R1.md` §2 are included where they bear on this route).
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
All numbers kept are synthetic FSM (parent e0 = 1/4, ρ0 = 1/8) or generic.

---

## 0. Status (header), near-verbatim

* Research, target-free; nothing evaluated on CUSUM m = 5 cells 305–309 or any drift in [1.2, 2.6].
* Algebra validated on synthetic FSM only (`code/d309_cover.py` → `validation/D309_COVER_FSM.json`).
* Rule S8: committed tail history only in §9, no route factor attached.

Route state: decomposition and gain theorem **VALIDATED_NON_TARGET**; DRP-1 **IMPLEMENTED** on FSM, **outcome-adaptive**
(frozen pass predicate), not result-free; DRP-0 result-free (repair r1, N12); real use **BLOCKED**: NEW_REAL (new K1
midpoint records).

## 1. Objects (§1), verbatim-close

Cell `C = [x_lo, x_hi] = [e0 − ρ, e0 + ρ]`, `x_lo > 0`, `g = R − eR'`, `g' = −eR''`. A **record** at midpoint e_c with
Taylor half-width h supplies: midpoint enclosures `R ∈ R_iv`, `R' ∈ D_iv`, hence `g_hi := hi(R_iv − e_c D_iv)`; the
TC / TC-T premises on its cell; the TC profile `L(s) = c_lo − rad(s)`, `U(s) = c_hi + rad(s)`, with `c_lo, c_hi` = the
candidate centre `Σ(1/m)Ĥ_r(a)` plus the whole-cell W enclosure, and `rad(s) = Σ_r (1/m) rad_r(s) = Σ_j r_j s^j`
(Lemma TC-P).

With Ĝ = 0 and constants A = (A0, A1, A2):

    r0 = Σ(1/m)(A0 f_H + 2A1 f_D + A2 f_F)             (midpoint residuals)
    r1 = Σ(1/m)(A0 f_G + 2A1 f_H + A2 f_D)             (order-3 surrogate channel)
    r2 = Σ(1/m)(A0 Env4/2 + A1 f_G + A2 f_H/2)         (order-4 envelope channel)
    r3 = Σ(1/m)(A1 Env4/3 + A2 f_G/6),   r4 = Σ(1/m) A2 Env4/24

(from TC §3: p2 = f_H + s f_G + s²Env4/2, p1, p0).

Three clauses on one record:
* **frozen:** `Γ_F = g_hi + ρ x_hi M`, `M = max(|L(ρ)|, |U(ρ)|)`;
* **C5-T:** `g_hi + max((−L(ρ))⁺ ρ(e0 + ρ/2), (U(ρ))⁺ ρ(e0 − ρ/2))`;
* **TPT (Corollary TPT-M):** `g_hi + max(0, I_R(ρ), I_L(ρ))`, `I_R(h) = ∫_0^h (e0+s)(−L(s)) ds`,
  `I_L(h) = ∫_0^h (e0−s) U(s) ds`.

## 2. Error decomposition vs ρ (§2)

**Proposition CR-1 (frozen clause as a polynomial in ρ, premises fixed).** If the lower end binds (|c_lo| := −c_lo):

    Γ_F(ρ) − g_hi = ρ(e0 + ρ)(|c_lo| + r0 + r1 ρ + r2 ρ² + r3 ρ³ + r4 ρ⁴).

| power of ρ in Γ_F − g_hi | coefficient | channel |
|---|---|---|
| ρ¹ | e0(|c_lo| + r0) | true transport (|R''|) plus centre error, W half-width, midpoint residual radius |
| ρ² | (|c_lo| + r0) + e0 r1 | order-3 surrogate f_G (via r1), plus the x_hi factor |
| ρ³ | r1 + e0 r2 | order-4 envelope Env4 (via r2) |
| ρ⁴, ρ⁵, ρ⁶ | r2 + e0 r3, r3 + e0 r4, r4 | higher Taylor terms |

ρ⁰ term `g_hi − g(e0)` = midpoint enclosure width `w_g`, independent of ρ.

**TPT form ("the identity with TPT").** `I_R(ρ) = |c_lo|(e0ρ + ρ²/2) + Σ_j r_j (e0 ρ^{j+1}/(j+1) + ρ^{j+2}/(j+2))`.
This is Proposition TPT-G: constant component charged 1, linear component 1/2, quadratic 1/3 (relative to the
whole-cell charge, to leading order in ρ/e0).

**Slack relative to truth** (right side binding, R'' < 0):

    S_TPT(ρ) := Γ_TPT − max_C g = w_g + ∫_0^ρ (e0+s)[R''(e0+s) − L(s)] ds,   0 ≤ R'' − L ≤ 2(W + rad(s)) + (centre error).

Orders: order-1 slack `e0(W + r0 + centre error)ρ`; order-2 `≈ e0 r1 ρ²/2`; order-3 `≈ e0 r2 ρ³/3`; …

## 3. What each mechanism does to each order (§3)

| mechanism | ρ⁰ (w_g) | order-1 slack | order-2 (f_G) | order-3 (Env4) | new certified inputs |
|---|---|---|---|---|---|
| frozen clause | 1 | ≥ 1 (charged at x_hi) | 1 | 1 | — |
| C5-T | 1 | 1 (exact weights) | 1 | 1 | none |
| **TPT** | 1 | 1 | **1/2** | **1/3** | none (third input = TC profile) |
| C5 "ρ halved" oracle | 1 | 1 | 1/2 of the Taylor part only | 1/4 | none: scales `meas["rho"]` only (`p5y_k5_tail_c5_exhaustion/code/c5_common.py:85-86`), keeps ρ·x_hi and g_hi, so models **neither** the new midpoint value **nor** the shorter transport |
| **real refinement, N subcells** | ≈ 1 (new record's own w_g) | **1/N** | **1/(2N²)** | **1/(3N³)** | N new records (or 1, §6) |

## 4. Relation to C5 route B2 (§4)

**Proposition CR-2 (within the fixed-input family, B2 is dominated by TPT).** Split C into subcells, create **no** new
record, and use **only the fixed triple** `(g_hi, L, U)` of the parent record. Then every resulting bound on `max_C g`
is at least the TPT bound.
*Proof.* Such a split returns a bound valid for every function consistent with `(g_hi, L, U)`. By Proposition TPT-O as
corrected, `g_hi + P*` is the **supremum** over C² functions consistent with those inputs; any valid bound from these
inputs is therefore ≥ `g_hi + P*`. (Repair r1, N10: r0 said "attained".) ∎

**Scope (repair r1, review B2).** C5 killed B2 as **NEW_REAL**, not MATH: "R and D are certified at e0 only;
transporting them to a sub-midpoint costs exactly what the split saves" (`C5_ROUTE_SEARCH.md:50`). CR-2 is a MATH
statement about a narrower object. **B2 is REFUTED only within the fixed-(g_hi, L, U) family.** The r0 sentence "a
record-free split can never gain anything" is withdrawn.

**Separate lever B2c (recorded, unevaluated).** A record-free split can still change the third input: re-certify the
operator constants (k_i, the A-supply, the k-terms of Env4) on shorter drift segments → s-dependent profile pointwise
≤ the cell-uniform one (Lemma TC-P needs the constants only on [e0, t]). Not dominated by fixed-profile TPT; creates no
new K1 record (not NEW_REAL); **not refuted**. State THEORY_ONLY; closure-only under floor r2.

**Transcription-consistency identity (not evidence; review B3).** `d309_cover.py` implements the record-free split as
the parent's own TPT integrals over sub-lengths from the same e0; its maximum equals the parent TPT **by construction**
(`B2_transcription_identity_diff` = 0 in all 30 splits). Checks the transcription only; CR-2 rests on TPT-O alone.

## 5. What a REAL refinement buys beyond TPT (§5) — the 1 − 1/N^j result

**Theorem CR-3 (leading-order gain).** Refine C into N equal subcells, each with a **new** record. Let J be the binding
subcell (rightmost when the right integral binds; J = 1 by symmetry otherwise). Then, exactly,

    Γ_TPT(parent) − Γ_TPT,N  =  T_par(ρ) − T_J(ρ/N) + [w_g(e0) − w_g(e_J)] + (max_C g − max_{C_J} g)

where `T_X(h) := P*_X(h) − (true increase of g over the transported length)` is the **transport** slack of record X over
length h, **excluding** the midpoint width w_g (repair r1, N9: r0 wrote S_X, which double-counted w_g).

**Leading-order model.** If the subcell premises equal the parent's (differences — new candidates, constants over the
smaller cell, W enclosure — are second order) and the max of g lies in C_J:

    gain(ρ, N) ≈ T(ρ) − T(ρ/N) = Σ_j s_j ρ^j (1 − (e_J/e0) N^{−j}),
    s_1 = e0 (W + r0 + centre error),   s_2 ≈ e0 r1/2 + s_1/(2e0),   s_3 ≈ e0 r2/3 + r1/3, …

The factor `e_J/e0 = 1 + O(ρ/e0)` makes the fractions exact only to leading order in ρ/e0. The "centre error" (deviation
of the candidate centre from the true R''(e0)) is **not** an input; its certified bound is W + r0 half-widths, so
`s_1^cert := e0 (2W + 2r0)` is used wherever a rule needs s_1 (repair r1, N11).

So beyond TPT, a real refinement removes: the fraction `1 − 1/N` of the **order-1** slack (which TPT cannot touch; TPT-G
charges the constant component at 1); `1 − 1/N²` of the order-2 slack TPT leaves; `1 − 1/N³` of the order-3 slack TPT
leaves. It cannot remove w_g (every new record brings its own). Not captured by the scaling model: (1) constants
re-certified over a smaller cell; (2) the **cell itself changes**, so any statement quantified over the frozen closed
cell does not transfer to a subcell (C4 Condition 5 records that 309's exclusion depends on that quantifier; no number
computed).

**Generic conclusion.** Wide-cell regime (`ρ r1 ≫ r0 + W`, a regime property): order-2 channel dominates the slack;
real refinement gains ≈ 1 − 1/N², TPT alone 1/2. Narrow-cell regime: order-1 slack dominates; TPT gains ≈ 0,
refinement 1 − 1/N.

Review R1 confirmation: order-j slack of a TPT record over half-width h ≈ e_c r_{j−1} h^j / j; with h = ρ/N and
e_J = e0 + O(ρ), retained fraction N^{−j}(1 + O(ρ/e0)); frozen-relative charges 1/N, 1/(2N²), 1/(3N³). Correct as a
leading-order statement with premises held fixed.

**FSM validation** (10 fixtures, parent e0 = 1/4, ρ0 = 1/8): real gain as fraction of parent TPT slack — N = 2:
0.710–0.892; N = 3: 0.855–0.958; N = 4: 0.893–0.978; every refined bound sound vs exact g (30/30). Pure-scaling
prediction relative error — N = 2: −12 % … +28 %; N = 3: −8 % … +34 %; N = 4: −6 % … +37 % (1–2 % on fixture 1; error
from changed premises of new records; leading-order statement, not a forecast).

**Scaling exponents** (nested ρ_k = ρ0/2^k, new records each level): per-order TPT components have log2 halving ratios
→ j + 1 (fixture 1: r0 1.36, 1.18, 1.09, 1.05; r1 2.32 → 2.04; r2 3.50 → 3.07; r3 4.69 → 4.10; r4 5.86 → 5.12); w_g ratio
≈ 0; total TPT slack slope 2.55 → 1.32 as ρ decreases (order-2 → order-1 crossover).

## 6. Cover designs (§6)
* Frozen cover: left-to-right walk with `ρ ≤ 1/(4 a C_upper)`, a geometry rule for K1's order-2 B_cover, "NOT a proof
  that B_cover will pass" (`p5y_k1_cover_ledger_successor/CHECKPOINT.md:71-110, 128-132`); ρ scales like 1/C_upper, not
  with the K5-B slack orders.
* **Uniform refinement:** N_k = ⌈ρ_k/ρ*⌉ for one global ρ*; result-free; cost Σ_k N_k scales with the whole cover.
* **DRP-0 (adaptive a priori):** `N_k = ⌈ρ_k / ρ_k*⌉`, `ρ_k* := s_1^cert / s_2^cert` (crossover where order-2 slack =
  order-1 slack), `s_1^cert = e0(2W + 2r0)`, `s_2^cert = e0 r1/2 + s_1^cert/(2e0)`. Result-free and deterministic;
  depends only on certified premise sizes (f_*, Env4, A, W); no centre error or Γ enters (N11). Below the crossover
  splitting buys at most 1 − 1/N of an order-1 term.
* **Hierarchical (dyadic):** subcells nest in frozen cells (boundaries of `cells.json` preserved); K5-B chain
  recurrences (ℓ_k, γ_k) apply to any contiguous tiling with exact shared endpoints (`K5_GLOBAL_BRIDGE.md:7, 20-33`).
* **Anisotropic in e (one extra record on the binding side):** keep parent record for `[x_lo, x_hi − 2ρ/N]`
  (different left/right transport lengths from e0; TPT holds for any record point inside a segment where its premises
  are certified); add one new record on `[x_hi − 2ρ/N, x_hi]`; binding side read from the parent's certified pieces
  `I_R ≥ I_L`, not from any target outcome. FSM (N = 4, one record): gain fraction 0.12–0.97 vs 0.89–0.98 for four
  records; sound 10/10.
* Anisotropic in state space concerns certificates (boxes aligned with occupation), not the e-cover (see RSO).
* Local Lipschitz: rad(s) is already a certified local modulus (TPT uses it). Option: if a record certifies U(s) < 0
  on the whole cell (g increasing), max_C g = g(x_hi) and a record **at** x_hi gives Γ = g_hi(x_hi) with zero
  transport (strong premise; design option only, not assessed on any real cell).

## 7. DRP-1 and cost model (§7)

**DRP-1 (dyadic certified branch-and-bound)**, fixed without reference to any cell's difficulty, for every cell with
x_lo > 0: (1) evaluate the frozen consumer clause (TPT) once on the existing record; (2) if it fails (Γ ≥ 0), bisect;
each child gets a **new** midpoint record (the child containing e0 does not reuse the parent); (3) recurse on failing
children; (4) stop at the first of: all leaves pass; depth D (frozen, e.g. D = 4); record budget B per cell (frozen);
(5) report PASS or FAIL_AT_DEPTH_CAP; (6) no re-runs, no parameter tuned after any evaluation; (7) cost
`records ≤ 2^{D+1} − 2` per cell.

**DRP-1 is OUTCOME-ADAPTIVE, not result-free** (repair r1, N12): splits on Γ ≥ 0 via a frozen pass predicate; rigour
unaffected (every leaf certified, adaptivity cannot create a false PASS); under S1 a branch-and-bound toward Γ < 0 on a
target cell is admissible only as a frozen, budget-capped stage authorized in advance; applying it to a target cell is
itself a target evaluation. Superseding wording: **"DRP-0 result-free; DRP-1 outcome-adaptive, frozen-predicate."**
(commit subject of 6d0f0615 cannot be edited).

**Cost model.** cost = Σ new records × c_rec (c_rec = one new certified K1 midpoint record: regenerated candidates,
midpoint residual certification, order-2 refinement, Aux3-type order-3 source evidence, W enclosures). Depth needed to
remove slack δ: smallest d with `Σ_j s_j ρ^j (1 − 2^{−jd}) ≥ δ`. Committed per-record reference costs in §9 (history).

**FSM exercise.** Synthetic, fixture-internal threshold `θ = gmax + κ(Γ_TPT(parent) − gmax)`, κ ∈ {1/2, 1/4, 1/16}; all
30 runs PASS within the depth cap; new records per fixture: κ = 1/2 → 2; 1/4 → 2–4; 1/16 → 4–6 (grows as threshold
approaches truth, as the order-1 floor predicts).

## 8. Validation summary (§8; 10 fixtures; declared rule `d309_cover.py:47-56`)

| check | result |
|---|---|
| C1 frozen clause equals its polynomial form, exactly | holds |
| C1 TPT closed form inside an independent 256-panel Riemann bracket | holds |
| midpoint enclosures contain exact R, R′ | holds |
| C2 soundness: every clause ≥ grid max of exact g | holds |
| C2 order TPT ≤ C5-T ≤ frozen | 10/10 |
| C3/C4/C5 refinements | sound everywhere |
| B2 transcription identity (NOT evidence, review B3) | 0 in 30 splits, by construction |

Controls (repair r1, review B1/N13), planted-invalid inputs through `Record.tpt_parts` and the profile on all 140 records
(10 parents, 40 nested, 90 subcells):
| check (truth-relative) | genuine | no_rad | flat_rad0 | rad_half | no_W | no_midpoint_width |
|---|---|---|---|---|---|---|
| transport level: clause value < exact grid max of g | 0/140 | 32/140 | 32/140 | 0/140 | 2/140 | 1/140 |
| profile level: exact R''_m outside [L(s), U(s)] (17 pts) | 0/140 | 136/140 | 130/140 | 0/140 | 140/140 | — |
| midpoint level: ĝ without widths < exact g(e_c) | — | — | — | — | — | 63/140 |
Transport-level check weak (masked by other slack); **profile-level check load-bearing** for the third TPT input;
rad_half undetected at both levels (TC radius overestimates true deviation by > 2× on these fixtures, so the halved
profile still encloses truth — not invalid there). Withdrawn: r0 "planted transport P := (gmax − g_hi)/2" (arithmetic).
Harness check only: shifted-interval control of `midpoint_check`.

## 9. History (§9, quoted, no route factor)
* Committed replay cost of existing K1 addresses for the tail cells: [TAIL-NUMBER REDACTED] (MEASUREMENT_NOTE.md:17-29,
  cited at ROUTE_AUDIT_R1.md:51). A **new** address additionally needs its own certification and provenance chain. B1
  costed "multi-hour – CPU-day, unmeasured" (ROUTE_AUDIT_R1.md:589).
* Classification: B1 is NEW_REAL, "a governed new K1 address, not the R-stage" (C5_ADJUDICATION.md:620-621;
  C5_ROUTE_SEARCH.md:49).
* The "ρ halved" diagnostic is committed as a cover-refinement oracle (C5_ADJUDICATION.md:606-613); §3 records why it is
  not one; graph_A_consumer.md item 9 found the same.

## 10. Governance (§10) and kill gates (§11)
* Adoption: real refinement **CLOSURE-ONLY** under floor r2 (changes consumer inputs: records, geometry) → user-decided
  floor extension frozen before evaluation (U3).
* New records are NEW_REAL: need host provisioning (U1), a new provenance chain (tail records are P3; C6 Condition 10),
  explicit authorization. Guard DENY unchanged; no new real address created tonight.
* Gates: G1 PASS (structural order decomposition); G2 PASS (CR-1 exact algebra; CR-2 corollary of TPT-O; CR-3 exact
  identity + leading-order model, labelled); G3 PASS (x_lo > 0, TC-T premises per record, TPT-M monotone profiles);
  G4 PASS; G5 PASS on FSM; G6 PASS for mathematics (review re-derived CR-1, CR-3, scoped CR-2; B2 check is an
  implementation identity); G7, G8 PASS; G9 PASS (DRP-0/1 fully specified, freezable); G10 PASS (real refinement has
  certified inputs outside F2; within the fixed-(g_hi, L, U) family a record-free split is cosmetic (CR-2); B2c outside
  that family and unevaluated).
* **Verdict:** algebra and policy VALIDATED_NON_TARGET; real use BLOCKED (NEW_REAL + U1/U3); FREEZE_READY **no**
  (requires unauthorized new real addresses).

## 11. Review R1 items on this route (from REVIEW_STREAM_D_R1 §2) and their disposition
* CR-1 re-derived, correct. "1 − 1/N^j" correct as leading-order with premises fixed; show e_J/e0 (done).
* N9 (CR-3 double-count of w_g) → T_X defined without w_g (done). N10 ("attained" → "supremum", done).
* **B2** (B2 REFUTED label overreach) → "REFUTED within the fixed-(g_hi, L, U) family"; B2c recorded THEORY_ONLY (done).
* **B3** ("B2 − TPT = 0, 30/30" by construction) → relabelled transcription-consistency identity (done).
* N11 (s_1 contains non-input centre error) → DRP-0 uses s_1^cert (done). N12 (DRP-1 wording) → outcome-adaptive
  (done). Cost bound 2^{D+1} − 2 confirmed.
* N13 (`NC_half_transport` arithmetic; `NC_g_hi_planted` harness) → withdrawn / relabelled; code-path mutants added
  (done). C5 "ρ halved" oracle diagnosis confirmed.

---

## 12. `d309_cover.py` — functions, formulas, data needed

Target-free; synthetic only; imports `d309_core`.

DECLARED_RULE: seeds 1..10, n = 4 + seed%3, kernel degree 4 (random_family, kill 1/5, e-range (0, 3/8)), two sources of
degree 5, W = K_e S_0 with coefficient 1/2, pert = (1e-6, 1e-4, 1e-3)[seed%3] (seeded by seed, source index, midpoint),
Ĝ := 0, Lemma-G constants on each (sub)cell; parent e0 = 1/4, ρ0 = 1/8; C3 ρ_k = ρ0/2^k, k = 0..4; C4 N ∈ {2, 3, 4};
C5 new record on binding quarter; C6 DRP-1 depth cap 4, θ = gmax + κ(Γ_TPT(parent) − gmax), κ ∈ {1/2, 1/4, 1/16};
truth grid 65 points per (sub)cell; Riemann 256 panels.

* `Fix(seed)`: family, sources, W(e)(a) = (1/2)Σ_y K_ay(e) S0_y(e) as exact polynomial; `g(e)` exact
  (R = (1/2)ΣF_r(a) + W, R' likewise; g = R − eR'); `gmax(lo, hi, pts=65)`.
* `Record(fx, ec, h)`: k_i, C over [ec − h, ec + h]; A = Lemma G; per source: perturbed candidates, f_F, f_D, f_H
  (exact residual norms), f_G = 3k1 sH + 3k2 sD + k3 sF + ‖S'''(ec)‖ (surrogate), Env4 = σ4 + 6k2 sH + 4k3(sD + h sH) +
  k4(sF + h sD + h² sH/2); rad = Σ (1/2)·tc_rad_poly; R̂ = W(ec) + Σ F̂(a)/2, D̂ likewise; dR = Σ A0 f_F/2,
  dD = Σ (A0 f_D + A1 f_F)/2; centre cen = Σ Ĥ(a)/2; W'' whole-cell range [w_lo, w_hi]; R_iv = R̂ ± dR, D_iv = D̂ ± dD;
  g_hi = R_iv.hi − ec·D_iv.lo. Properties c_lo = cen + w_lo, c_hi = cen + w_hi.
  * `H_whole(h)` = (c_lo − rad(h), c_hi + rad(h)); `frozen(h, rad_h)` = g_hi + h(ec + h)·mag;
    `c5t()` = g_hi + max(max(−H_lo,0)·h(ec + h/2), max(H_hi,0)·h(ec − h/2));
    `tpt_parts(hr, hl, rad, clo, chi)`: −L(s) = −clo + rad(s), U(s) = chi + rad(s), IR = ∫_0^{hr} (ec + s)(−L), IL =
    ∫_0^{hl} (ec − s)U, P = max(0, IR, IL) (overrides only for planted controls); `tpt()` = g_hi + P;
    `riemann_bracket(256)`; `components()` = per-order right-side slack pieces r_j(ec h^{j+1}/(j+1) + h^{j+2}/(j+2)),
    centre_W = (−c_lo)(ec h + h²/2), midpoint_width = g_hi − g(ec).
* `c1_identities`, `midpoint_check`, `transport_mutants(rec, gm)` (no_rad, flat_rad0, rad_half, no_W,
  no_midpoint_width; profile-level truth check on 17 points; midpoint-level check), `clause_values`.
* `run_fixture(seed)`: C1; midpoint validity + harness check; C2 soundness/order; flat-profile value; C3 nested scaling
  with log2 ratios; C4 refinement N ∈ {2,3,4}: real_gain = TPT(parent) − max TPT(subcells), pure-scaling prediction
  from parent premises (`slack_model`), B2 transcription identity; C4 oracle (Taylor ρ halved inside rad only) vs real
  bisection; C5 one extra record on binding quarter; C6 DRP-1 stack recursion with depth cap 4.
* Data needed: synthetic only.
