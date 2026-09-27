# Cover refinement for the K5-B direct clause — error decomposition in ρ, the gain beyond TPT, and a generic policy

**Status.**
* Research, target-free. Nothing here was evaluated on CUSUM m = 5 cells 305–309, or on any drift in [1.2, 2.6].
* The algebra is validated on synthetic FSM families only (`code/d309_cover.py` → `validation/D309_COVER_FSM.json`).
* Rule S8: committed tail history appears only in §9, with no route factor attached.

**Route state.**
* The decomposition and the gain theorem are **VALIDATED_NON_TARGET**.
* Policy DRP-1 is **IMPLEMENTED** on FSM. It is **outcome-adaptive** (frozen pass predicate), not result-free.
  DRP-0 is result-free (repair r1, review N12).
* Real use is **BLOCKED**: NEW_REAL, i.e. new K1 midpoint records.

## 1. Objects

The cell is `C = [x_lo, x_hi] = [e0 − ρ, e0 + ρ]` with `x_lo > 0`, and `g = R − eR'`, so `g' = −e R''`. A **record** at a
midpoint `e_c` with Taylor half-width `h` supplies:
* the midpoint enclosures `R ∈ R_iv` and `R' ∈ D_iv`, hence `g_hi := hi(R_iv − e_c D_iv)`;
* the TC / TC-T premises on its cell;
* the TC profile
  * `L(s) = c_lo − rad(s)` and `U(s) = c_hi + rad(s)`;
  * `c_lo, c_hi` = the candidate centre `Σ(1/m)Ĥ_r(a)` plus the whole-cell W enclosure;
  * `rad(s) = Σ_r (1/m) rad_r(s) = Σ_j r_j s^j` (Lemma TC-P, `streams/E_assembly/THEOREM_TPT.md` §2).

With Ĝ = 0 and Lemma-G / Lemma-Dv′ constants A = (A0, A1, A2), the coefficients of `rad` are

    r0 = Σ(1/m)(A0 f_H + 2A1 f_D + A2 f_F)             (midpoint residuals)
    r1 = Σ(1/m)(A0 f_G + 2A1 f_H + A2 f_D)             (order-3 surrogate channel)
    r2 = Σ(1/m)(A0 Env4/2 + A1 f_G + A2 f_H/2)         (order-4 envelope channel)
    r3 = Σ(1/m)(A1 Env4/3 + A2 f_G/6),   r4 = Σ(1/m) A2 Env4/24

(from TC §3: `p2 = f_H + s f_G + s²Env4/2`, `p1`, `p0`).

The three clauses on one record:
* **frozen:** `Γ_F = g_hi + ρ x_hi M`, with `M = max(|L(ρ)|, |U(ρ)|)`;
* **C5-T:** `g_hi + max((−L(ρ))⁺ ρ(e0 + ρ/2), (U(ρ))⁺ ρ(e0 − ρ/2))`;
* **TPT (Corollary TPT-M):** `g_hi + max(0, I_R(ρ), I_L(ρ))`, where

      I_R(h) = ∫_0^h (e0+s)(−L(s)) ds,   I_L(h) = ∫_0^h (e0−s) U(s) ds.

## 2. Error decomposition of the clause versus ρ

**Proposition CR-1 (frozen clause as a polynomial in ρ, premises fixed).** Suppose the lower end binds, and write
`|c_lo|` for `−c_lo`. Then

    Γ_F(ρ) − g_hi = ρ(e0 + ρ)(|c_lo| + r0 + r1 ρ + r2 ρ² + r3 ρ³ + r4 ρ⁴).

The coefficient of each power of ρ:

| power of ρ in Γ_F − g_hi | coefficient | channel |
|---|---|---|
| ρ¹ | e0(|c_lo| + r0) | true transport (\|R''\|) plus centre error, W half-width and the midpoint residual radius |
| ρ² | (|c_lo| + r0) + e0 r1 | order-3 surrogate `f_G` (through r1), plus the x_hi factor |
| ρ³ | r1 + e0 r2 | order-4 envelope `Env4` (through r2) |
| ρ⁴, ρ⁵, ρ⁶ | r2 + e0 r3, r3 + e0 r4, r4 | higher Taylor terms |

The ρ⁰ term, `g_hi − g(e0)`, is the midpoint enclosure width `w_g`. It is independent of ρ.

**TPT form.** `I_R(ρ) = |c_lo|(e0ρ + ρ²/2) + Σ_j r_j (e0 ρ^{j+1}/(j+1) + ρ^{j+2}/(j+2))`. This is Proposition TPT-G:
* the constant component is charged 1;
* the linear component 1/2;
* the quadratic component 1/3.

**Slack relative to the truth.** Take the right side as binding, which is the case when R'' < 0. Then

    S_TPT(ρ) := Γ_TPT − max_C g = w_g + ∫_0^ρ (e0+s)[R''(e0+s) − L(s)] ds,   0 ≤ R'' − L ≤ 2(W + rad(s)) + (centre error).

The integrand splits into orders:
* the **order-1 slack** `e0(W + r0 + centre error)ρ`;
* the **order-2 slack** `≈ e0 r1 ρ²/2`;
* the **order-3 slack** `≈ e0 r2 ρ³/3`;
* and so on.

## 3. What each existing mechanism does to each order

| mechanism | ρ⁰ (w_g) | order-1 slack | order-2 (f_G) | order-3 (Env4) | new certified inputs |
|---|---|---|---|---|---|
| frozen clause | 1 | ≥ 1 (charged at x_hi) | 1 | 1 | — |
| C5-T | 1 | 1 (exact weights) | 1 | 1 | none |
| **TPT** | 1 | 1 | **1/2** | **1/3** | none (third input = TC profile) |
| C5 "ρ halved" oracle | 1 | 1 | 1/2 of the Taylor part only | 1/4 | none: it scales `meas["rho"]` only (`p5y_k5_tail_c5_exhaustion/code/c5_common.py:85-86`), keeps ρ·x_hi and g_hi, so it models **neither** the new midpoint value **nor** the shorter transport |
| **real refinement, N subcells** | ≈ 1 (the new record's own w_g) | **1/N** | **1/(2N²)** | **1/(3N³)** | N new records (or 1, §6) |

TPT factors are relative to the whole-cell charge, to leading order in ρ/e0.

## 4. Relation to C5 route B2

**Proposition CR-2 (within the fixed-input family, B2 is dominated by TPT).** Split C into subcells, create **no** new
record, and use **only the fixed triple** `(g_hi, L, U)` of the parent record. Then every resulting bound on `max_C g`
is at least the TPT bound.

*Proof.* Such a split returns a bound valid for every function consistent with `(g_hi, L, U)`. By Proposition TPT-O as
corrected (`streams/E_assembly/THEOREM_TPT.md:75-80`), `g_hi + P*` is the **supremum** over C² functions consistent
with those inputs. Any valid bound from these inputs is therefore at least `g_hi + P*`. (Repair r1, review N10: the r0
text said "attained", which the corrected TPT-O withdraws; the conclusion is unchanged.) ∎

**Scope (repair r1, review B2).** C5 killed B2 as **NEW_REAL**, not MATH, with: "R and D are certified at e0 only;
transporting them to a sub-midpoint costs exactly what the split saves" (`p5y_k5_tail_c5_exhaustion/phase_3/
C5_ROUTE_SEARCH.md:50`). CR-2 is a MATH statement about a narrower object. **B2 is REFUTED only within the
fixed-(g_hi, L, U) family.** The r0 sentence "a record-free split can never gain anything" is withdrawn.

**Separate lever B2c (recorded, unevaluated).** A record-free split can still change the third input:
* re-certify the operator constants (`k_i`, the A-supply, the k-terms of Env4) on shorter drift segments;
* this gives an s-dependent profile pointwise ≤ the cell-uniform one;
* Lemma TC-P needs the constants only on `[e0, t]`.

B2c is not dominated by fixed-profile TPT. It creates no new K1 record, so it is not NEW_REAL, and it is **not refuted
by anything here**. State: THEORY_ONLY; closure-only under floor r2.

**Transcription-consistency identity (not evidence; review B3).** `d309_cover.py` implements the record-free split as
the parent's own TPT integrals over sub-lengths from the same e0. Its maximum equals the parent TPT **by construction**
(`B2_transcription_identity_diff` = 0 in all 30 splits). This checks the transcription only. CR-2 rests on TPT-O
alone.

## 5. What a REAL refinement buys beyond TPT (as a function of ρ)

**Theorem CR-3 (leading-order gain).** Refine C into N equal subcells, each with a **new** record. Let J be the binding
subcell: the rightmost when the right integral binds, and J = 1 by symmetry otherwise. Then, exactly,

    Γ_TPT(parent) − Γ_TPT,N  =  T_par(ρ) − T_J(ρ/N) + [w_g(e0) − w_g(e_J)] + (max_C g − max_{C_J} g)

where `T_X(h) := P*_X(h) − (true increase of g over the transported length)` is the **transport** slack of record X
over length h. It **excludes** the midpoint width `w_g`, which appears separately. (Repair r1, review N9: r0 wrote
`S_X`, which the r0 §2 definition of `S_TPT` made include `w_g`, and so double-counted it.)

**Leading-order model.** Suppose the subcell premises equal the parent's. They differ only by the new candidates, the
constants over the smaller cell and the W enclosure, which are all second order. Suppose also the max of g lies in
`C_J`. Then

    gain(ρ, N) ≈ T(ρ) − T(ρ/N) = Σ_j s_j ρ^j (1 − (e_J/e0) N^{−j}),
    s_1 = e0 (W + r0 + centre error),   s_2 ≈ e0 r1/2 + s_1/(2e0),   s_3 ≈ e0 r2/3 + r1/3, …

The factor `e_J/e0 = 1 + O(ρ/e0)` makes the fractions below exact only to leading order in ρ/e0 (review note). The
"centre error" is the deviation of the candidate centre from the true `R''(e0)`. It is **not** an input. Its
certified bound is `W + r0` half-widths, so a certified `s_1^cert := e0 (2W + 2r0)` is used wherever a rule needs
`s_1` (repair r1, review N11).

So beyond TPT, a real refinement removes:
* the fraction `1 − 1/N` of the **order-1** slack, which TPT cannot touch (TPT-G charges the constant component at 1);
* `1 − 1/N²` of the order-2 slack that TPT leaves;
* `1 − 1/N³` of the order-3 slack that TPT leaves.

It cannot remove `w_g`: every new record brings its own.

Two further effects are not captured by the scaling model:
1. the constants are re-certified over a smaller cell;
2. the **cell itself changes**, so any statement quantified over the frozen closed cell does not transfer to a subcell.
   C4 Condition 5 records that 309's exclusion depends on that quantifier; no number is computed here.

**Generic conclusion.**
* In the **wide-cell regime** (`ρ r1 ≫ r0 + W`, a regime property) the order-2 channel dominates the slack. There real
  refinement gains `≈ 1 − 1/N²`, and TPT alone `1/2`.
* In the **narrow-cell regime** the order-1 slack dominates. There TPT gains ≈ 0 and refinement gains `1 − 1/N`.

**Validation on FSM** (10 fixtures, parent `e0 = 1/4`, `ρ0 = 1/8`; `d309_cover.py:308-342`).

Real gain as a fraction of the parent TPT slack (`:315`):

| N | fraction of parent slack removed |
|---|---|
| 2 | 0.710–0.892 |
| 3 | 0.855–0.958 |
| 4 | 0.893–0.978 |

Every refined bound is sound against the exact g (30/30).

Pure-scaling prediction from the parent's premises (`:321-329`), relative error:

| N | relative error |
|---|---|
| 2 | −12 % … +28 % |
| 3 | −8 % … +34 % |
| 4 | −6 % … +37 % |

The prediction is 1–2 % on fixture 1. The error comes from the changed premises of the new records. The model is a
**leading-order** statement, not a forecast.

**Scaling exponents** (`:280-300`). Nested cells `ρ_k = ρ0/2^k` with new records at every level:
* **Components.** The per-order TPT components have log2 halving ratios converging to j + 1. Fixture 1 (the other nine
  alike, in the JSON):

  | component | log2 halving ratios, largest ρ → smallest |
  |---|---|
  | r0 | 1.36, 1.18, 1.09, 1.05 |
  | r1 | 2.32 → 2.04 |
  | r2 | 3.50 → 3.07 |
  | r3 | 4.69 → 4.10 |
  | r4 | 5.86 → 5.12 |

* **Midpoint width** `w_g`: ratio ≈ 0, independent of ρ.
* **Total TPT slack**: slope 2.55 → 1.32 as ρ decreases. This is the order-2 → order-1 crossover.

## 6. Cover designs

The frozen cover is adaptive but not built for K5-B.
* It is a left-to-right walk with `ρ ≤ 1/(4 a C_upper)`: a geometry rule for K1's order-2 B_cover, "NOT a proof that
  B_cover will pass" (`p5y_k1_cover_ledger_successor/CHECKPOINT.md:71-110, 128-132`, as reconstructed in
  `graph_C_inputs.md` §1.3).
* Its ρ scales like 1/C_upper, not with the K5-B slack orders of §2.

**Uniform refinement.** Every cell k gets `N_k = ⌈ρ_k/ρ*⌉` equal subcells for one global ρ*. This is result-free, but
the cost `Σ_k N_k` scales with the whole cover.

**Adaptive a priori (DRP-0).** `N_k` is chosen from the cell's own certified **inputs**, never from Γ.
* **Rule:** `N_k = ⌈ρ_k / ρ_k*⌉`, where `ρ_k* := s_1^cert / s_2^cert` is the crossover at which the order-2 slack
  equals the order-1 slack (§5). It uses the **certified** coefficients `s_1^cert = e0(2W + 2r0)` and
  `s_2^cert = e0 r1/2 + s_1^cert/(2e0)`. Below the crossover further splitting buys at most `1 − 1/N` of an order-1
  term.
* **Properties:** result-free and deterministic. It depends only on certified premise sizes (`f_*`, `Env4`, A, W),
  which are inputs; no centre error or Γ enters (repair r1, review N11).

**Hierarchical (dyadic) refinement.**
* Subcells nest inside the frozen cells, so the committed boundaries of `cells.json` are preserved.
* The K5-B chain recurrences (`ℓ_k`, `γ_k`) apply to any contiguous tiling with exact shared endpoints
  (`K5_GLOBAL_BRIDGE.md:7, 20-33`). A refined cell simply passes its chain state through its subcells.

**Anisotropic, in the drift e (1-D): one extra record on the binding side.**
* Keep the parent record for `[x_lo, x_hi − 2ρ/N]`, transporting from e0 with different left and right lengths. TPT
  holds for any record point inside a segment on which its premises are certified.
* Add **one** new record covering the binding end `[x_hi − 2ρ/N, x_hi]`.
* The binding side is read from the parent's own certified pieces `I_R ≥ I_L`, not from any target outcome.
* **FSM result (N = 4, one record)** (`d309_cover.py:350-362`): gain fraction 0.12–0.97, against 0.89–0.98 for four
  records. It is sound in 10/10 cases.
* It is efficient when the order-2/3 slack concentrates at the binding end. It is inefficient when the parent's
  transport over `[e0, x_hi − ρ/2]` still dominates.

**Anisotropic, in the state space.** Anisotropy in (p, m) concerns the certificates (reachable-cover boxes aligned
with the chain's occupation), not the e-cover. See `RESIDUAL_SPECIFIC_309.md` for the occupation-weighted analogue.

**Local Lipschitz information.**
* The TC profile `rad(s)` is already a certified local modulus of R'' around each record. TPT uses it.
* A stronger structural option: if a record certifies `U(s) < 0` on the whole cell, i.e. `R'' < 0` and so g is
  increasing, then `max_C g = g(x_hi)`. A record placed **at** x_hi then gives `Γ = g_hi(x_hi)` with **zero** transport.
* The premise (the whole enclosure strictly negative) is strong. It is stated as a design option, not assessed on any
  real cell.

**Certified branch-and-bound (DRP-1)** is defined in §7.

## 7. Generic deterministic refinement policy and cost model

**DRP-1 (dyadic certified branch-and-bound)** is fixed without reference to any cell's difficulty and applies to every
cell with `x_lo > 0`.
1. **Evaluate once.** Evaluate the frozen consumer clause (TPT) once on the cell's existing record.
2. **Split on failure.** If the clause fails (Γ ≥ 0), bisect. Each child gets a **new** midpoint record, and the child
   containing e0 does **not** reuse the parent record.
3. **Recurse** on failing children.
4. **Stop** at the first of:
   * all leaves pass;
   * depth D (frozen, e.g. D = 4);
   * record budget B per cell (frozen).
5. **Report** PASS or FAIL_AT_DEPTH_CAP per cell.
6. **No re-runs.** No parameter is tuned after any evaluation.
7. **Cost:** `records ≤ 2^{D+1} − 2` per cell.

**DRP-1 is OUTCOME-ADAPTIVE, not result-free** (repair r1, review N12).
* It splits on `Γ ≥ 0`, i.e. on the outcome, through a frozen pass predicate.
* Rigour is unaffected: every leaf bound is certified, so adaptivity cannot create a false PASS.
* Under S1, a branch-and-bound toward `Γ < 0` on a target cell is admissible only as a frozen, budget-capped stage
  authorized in advance.
* Applying it to a target cell is itself a target evaluation.

Any r0 phrase calling the DRP-0/1 pair "result-free" (including the commit subject of 6d0f0615, which cannot be edited)
is superseded by: **DRP-0 result-free; DRP-1 outcome-adaptive, frozen-predicate.**

**Cost model.**
* `cost = Σ_new records × c_rec`.
* `c_rec` is the cost of one new certified K1 midpoint record: regenerated candidates, midpoint residual certification,
  the order-2 refinement, Aux3-type order-3 source evidence and the W enclosures.
* By the leading-order model of §5, the depth needed to remove a slack amount δ from a cell with slack coefficients `s_j`
  is the smallest d with `Σ_j s_j ρ^j (1 − 2^{−jd}) ≥ δ`.
* Committed per-record reference costs are in §9 (history).

**FSM exercise** (`d309_cover.py:363-387`).
* **Threshold** (fixture-internal and declared): `θ = gmax + κ(Γ_TPT(parent) − gmax)`, with κ ∈ {1/2, 1/4, 1/16}.
* **Outcome:** all 30 runs PASS within the depth cap.

| κ | new records per fixture |
|---|---|
| 1/2 | 2 |
| 1/4 | 2–4 |
| 1/16 | 4–6 |

The record count grows as the threshold approaches the truth, as the order-1 floor of §5 predicts.

## 8. Validation summary (target-free)

Source: `validation/D309_COVER_FSM.json`, 10 fixtures; declared rule at `d309_cover.py:47-56`.

**Identities, soundness and B2**

| check | code | result |
|---|---|---|
| C1 frozen clause equals its polynomial form, exactly | `:198-209` | holds |
| C1 TPT closed form lies inside an independent 256-panel Riemann bracket | same | holds |
| midpoint enclosures contain the exact R and R′ | `:212-214` | holds |
| C2 soundness: every clause ≥ the grid max of the exact g | — | holds |
| C2 order: TPT ≤ C5-T ≤ frozen | — | holds in 10/10 |
| C3 / C4 / C5 refinements | — | sound everywhere |
| B2 transcription identity (NOT evidence, review B3) | `:330-340` | 0 in 30 splits, by construction |

**Controls (repair r1, review B1/N13).** Planted-invalid inputs go **through** `Record.tpt_parts` and the profile, on
all 140 records built (10 parents, 40 nested, 90 subcells). Code: `transport_mutants` in `d309_cover.py`.

| check (truth-relative) | genuine | no_rad | flat_rad0 | rad_half | no_W | no_midpoint_width |
|---|---|---|---|---|---|---|
| transport level: clause value < exact grid max of g | 0/140 | 32/140 | 32/140 | 0/140 | 2/140 | 1/140 |
| profile level: exact `R''_m` outside `[L(s), U(s)]` (17 pts) | 0/140 | 136/140 | 130/140 | 0/140 | 140/140 | — |
| midpoint level: `ĝ` without the widths < exact `g(e_c)` | — | — | — | — | — | 63/140 |

* **The transport-level check is weak.** It is a necessary condition, masked by the other slack terms.
* **The profile-level check is the load-bearing evidence** for the third TPT input.
* **`rad_half` is not detected at either level.** On these fixtures the TC radius overestimates the true deviation by
  more than 2×: the genuine worst deviation/radius in the SC run is 0.54. So the halved profile still encloses the
  truth, and it is not invalid on these fixtures.
* **Withdrawn:** the r0 "planted transport P := (gmax − g_hi)/2" was arithmetic.
* **Harness check only:** the shifted-interval control of `midpoint_check`.

## 9. History (quoted, no route factor attached)

**Committed replay cost of existing K1 addresses.**
* 1350.2–1359.6 CPU-s per cell for 306–309, about 1.87 CPU-h for 305–309 (`MEASUREMENT_NOTE.md:17-29`, cited at
  `ROUTE_AUDIT_R1.md:51`).
* A **new** address additionally needs its own certification and provenance chain.
* B1 is costed "multi-hour – CPU-day, unmeasured" (`ROUTE_AUDIT_R1.md:589`).

**Classification.** B1 is NEW_REAL, "a governed new K1 address, not the R-stage"
(`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md:620-621`; route ledger
`phase_3/C5_ROUTE_SEARCH.md:49`).

**The "ρ halved" diagnostic.** It is committed as a cover-refinement oracle (`C5_ADJUDICATION.md:606-613`). §3 records
why it is not one; `graph_A_consumer.md` item 9 found the same.

## 10. Governance

* **Adoption.** Real refinement is **CLOSURE-ONLY** under floor r2: it changes the consumer's inputs (records,
  geometry). Any adoption needs a user-decided floor extension frozen before evaluation (U3).
* **New records.** The records are NEW_REAL. They need:
  * host provisioning (U1);
  * a new provenance chain, since the tail records are P3 (C6 Condition 10);
  * explicit authorization.
* **Tonight.** Guard DENY is unchanged. No new real address was created tonight.

## 11. Kill gates

| gate | result |
|---|---|
| G1 | PASS. Motivation: the structural order decomposition, independent of target sign. |
| G2 | PASS. CR-1 is exact algebra; CR-2 is a corollary of TPT-O; CR-3 is an exact identity plus a leading-order model, labelled as such. |
| G3 | PASS. Premises: `x_lo > 0`, TC-T premises on each record, TPT-M monotone profiles. |
| G4 | PASS. |
| G5 | PASS on FSM. |
| G6 | PASS for the mathematics (independent review R1 re-derived CR-1, CR-3 and CR-2 in its scoped form). The B2 check is an implementation identity, not evidence. |
| G7 | PASS. |
| G8 | PASS. |
| G9 | PASS. DRP-0 and DRP-1 are fully specified and freezable. |
| G10 | PASS. A real refinement has certified inputs outside F2. Within the fixed-(g_hi, L, U) family a record-free split is cosmetic (CR-2). B2c (constant re-certification on sub-segments) is outside that family and unevaluated. |

**Verdict.**
* The algebra and policy are **VALIDATED_NON_TARGET**.
* Real use is **BLOCKED** (NEW_REAL + U1/U3).
* FREEZE_READY: **no**. It requires new real addresses that are not authorized.
