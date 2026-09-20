# C1 — the certified operator-only registry extension over the CUSUM m = 5 tail

**C1 proves no new theorem.** It supplies theorem AD's Lemma Dv′ atom constants over a domain where none existed, and
feeds them to the adopted theorem TC-T in place of Lemma G's generic ones. Every mathematical step is adopted:

| step | owner | status |
|---|---|---|
| the six operator constants Ā, τ, C_T, D_lo, D1, D2 per e-block | theorem AD §8 | adopted |
| their certification (polynomial supersolutions, Bernstein ranges, Arb at 256 bits) | `taboo_certify.py` | adopted, executed from its pinned bytes |
| A0, A1, A2 from them | theorem AD Lemma Dv′ / `deflated_consume.atom_constants_r2` | adopted |
| the whole-cell enclosure of R″_m from A0, A1, A2 | theorem TC-T | adopted (Campaign B, two reviews) |
| the pass/open predicate | theorem K5-B `k5b_literal` | frozen |

What is **new** is only: the domain (e ∈ [1.6209, 2.0923] instead of [0, 0.1147]), the block geometry (one block per
tail cell, equal to that cell's own interval, so `block_for` resolves each cell to exactly one block with exact
coverage), and the deterministic alpha ladders. **NEW_REAL_ADDRESSES = 0**; the guard stays DENY.

**The block geometry is conservative, and that direction should be stated.** Lemma T is quantified over the drift
set, so certifying `w ≥ 1 + K̂_e w` uniformly on one block of width 2ρ ≈ 0.081–0.108 is a *stronger* obligation than
on the adopted r1's 1/100-wide blocks, and the resulting C_T and τ are whole-cell sup bounds by construction. The
constants are therefore valid — but the conservatism costs accuracy: under the adopted rule a cell takes the worst
over the sub-blocks meeting it, and nine 1/100-wide sub-blocks would each admit a tighter supersolution than one
block nine times as wide. Since A0 = τ/D_lo is where C1's entire gain lives, this is the cheapest tightening C1
leaves on the table, and it is the first item of the C2 plan.

## 1. What was certified

`evidence/registry_c1/REGISTRY_C1.json` (sha256 `87bb1cfa…`), 1232.2 CPU-s, all five cells certified, every cell at
the **first** alpha of its ladder:

| cell | e-interval | C_T | τ | Ā | D_lo | D1 | D2 | τ/D_lo | Ā_eff |
|---|---|---|---|---|---|---|---|---|---|
| 305 | [1.620881, 1.701923] | 6.028953 | 5.291155 | 8.290719 | 0.768609 | 1.618684 | 28.506538 | 6.884064 | **6.884064** |
| 306 | [1.701923, 1.788592] | 5.670984 | 5.070746 | 7.912417 | 0.790892 | 1.519245 | 25.787949 | 6.411423 | **6.411423** |
| 307 | [1.788592, 1.882413] | 5.331527 | 4.851873 | 7.555613 | 0.810385 | 1.448025 | 23.555402 | 5.987123 | **5.987123** |
| 308 | [1.882413, 1.983910] | 5.008961 | 4.633777 | 7.217875 | 0.828872 | 1.377221 | 21.469367 | 5.590460 | **5.590460** |
| 309 | [1.983910, 2.092283] | 4.705512 | 4.418493 | 6.900983 | 0.848046 | 1.284353 | 19.336006 | 5.210202 | **5.210202** |

Every cell certified at the **first** rung of both ladders (taboo α = 6/5, ARL α = 5/4).

**Ā is inert.** Lemma Dv′ uses Ā_eff = min(Ā, τ/D_lo), and on all five tail cells τ/D_lo is the smaller, so the
whole-kernel ARL supersolution — roughly half the 1232 CPU-s of the build — feeds nothing, and a wrong Ā would not
show up in any published number. It is certified and recorded for completeness and as a consistency check
(Ā ≥ Ā_eff holds on all five), not because anything depends on it. A successor that wants A0 lower should attack
τ and D_lo, not Ā.

## 2. The result, and the honest shape of it

Lemma Dv′ against Lemma G on the tail:

| cell | A0 generic → C1 | A1 generic → C1 | A2 generic → C1 |
|---|---|---|---|
| 305 | 7.73 → 6.88 (**1.123×** better) | 47.69 → 47.61 (1.002×) | 646.19 → 814.63 (**0.793×**, i.e. worse) |
| 306 | 7.23 → 6.41 (1.128×) | 41.70 → 41.33 (1.009×) | 531.47 → 665.54 (0.799×) |
| 307 | 6.68 → 5.99 (1.116×) | 35.58 → 36.17 (0.984×) | 422.13 → 550.86 (0.766×) |
| 308 | 6.17 → 5.59 (1.104×) | 30.39 → 31.63 (0.961×) | 336.05 → 455.61 (0.738×) |
| 309 | 5.78 → 5.21 (1.110×) | 26.65 → 27.45 (0.971×) | 277.93 → 372.56 (0.746×) |

**Deflation buys much less at the tail than at e = 0, and it makes A2 worse.** Theorem AD §3 said so in advance —
"the large gains below are in the order-1 and order-2 cross terms, where the generic stack multiplies independent
copies of C" — and at the tail C_upper is already only 5.78–7.73, so there are no large copies of C to collapse.
Meanwhile Lemma Dv′ pays absolute costs the generic stack does not: d₂ = D2/D_lo is 22.8–37.1, which lands directly
in A2. The e = 0 precedent (2.46× on A0) does not transfer: the tail gets **1.10–1.13×**.

The net effect on the enclosure is nevertheless favourable, because the radius is dominated by the A0·p2 term:

| cell | mag TC-T (Lemma G) | mag TC-T (C1) | M needed | Γ (C1) | margin | K5-B |
|---|---|---|---|---|---|---|
| 305 | 4.257155 | **3.947590** | 4.891579 | −0.065100 | **1.239×** | **PASS** (direct) |
| 306 | 4.151682 | **3.831264** | 3.905056 | −0.005719 | **1.019×** | **PASS** (direct) |
| 307 | 4.040057 | 3.774673 | 3.076148 | +0.061683 | 0.815× | open |
| 308 | 4.005124 | 3.785137 | 2.432398 | +0.136195 | 0.643× | open |
| 309 | 3.964274 | 3.723417 | 1.969828 | +0.198810 | 0.529× | open |

No previously passing cell regresses; m = 1, 2, 3 remain complete on 0–309; no intersection is empty.

**Cell 306 closes by a thin margin and should be read as such.** Γ(306) = −0.005719468 against a curvature penalty
ρ·x_hi·M_after = 0.296955 and a drift term −0.302674; |Γ| is **1.93 %** of the penalty it has to overcome, and the
K5-B margin M_needed/M_after is 1.0192605. The frozen DEGRADED scenario (every certified atom constant × 5/4) loses
it. (An earlier draft of this paragraph quoted the penalty as ≈ 0.43, which is ρ·x_hi·M_R2 — the penalty *before*
C1's tightening — and understated the margin as 1.3 %.)

## 3. Why a componentwise minimum was not taken

Lemma G's constants and Lemma Dv′'s are both valid, so their componentwise minimum is also valid and would be
slightly better where Dv′ is worse. C1 does **not** do this: its frozen gate specifies the Lemma Dv′ constants "used
exactly as theorem AD Lemma Dv′ prescribes", and choosing a different composition after seeing that Dv′ degrades A2
is precisely the post-hoc optimisation the gate's `no_redefinition` clause forbids.

The diagnostic was computed anyway and is recorded at `evidence/forecast_r1/C1_DIAGNOSTIC_MIN.json`, because
withholding a decision-relevant number would be worse than reporting one the gate excludes. It changes nothing:
magnitudes 3.9265 / 3.8117 / 3.7411 / 3.7331 / 3.6809, margins 1.246 / 1.025 / 0.822 / 0.652 / 0.535, and the same
two cells close. The gate-specified computation costs C1 nothing.

## 4. Premises, and where the repaired (P3′) logic is preserved

C1 changes no premise of theorem TC-T. In particular Campaign B's review-r1 repair is carried through untouched: σ₃
is a **midpoint** premise ((P2), at e₀) and takes the midpoint tower; σ₄ is a **whole-cell** premise ((P3), every e in
the cell) and takes the cell tower with the mean-value correction. C1 substitutes only the A-constants, which enter at
theorem TC §4 step 3 and nowhere else. Mutant `M01_midpoint_tower_used_for_sigma4` in
`evidence/prefreeze/C1_MUTATIONS.json` exists to keep that repair honest, and is detected.

The operator constants themselves are **whole-cell by construction**: each is certified uniformly on the cell's own
e-interval (Lemma T with E = the block), never at a midpoint. There is no midpoint quantity anywhere in C1's own
contribution.

## 5. Independent second paths

The C1 gate requires a second calculation path that does not share the load-bearing helpers whose shared use hid
Campaign B's round-1 defect. There are two, at the two places C1 adds something:

- **atom constants**: `c1_forecast._atom_constants_independent` re-derives Lemma Dv′ from `THEOREM_AD.md` §4 and shares
  no function with `deflated_consume.atom_constants_r2`. They must agree exactly, as rationals, on all five cells.
- **the enclosure**: `tct_rule.tail_enclosure_crosscheck` re-derives both towers, both σ's, the Taylor sums, the (P3)
  envelope and the assembly table in-line and shares no function with `tail_enclosure`. They must agree exactly on
  every cell and every m (20 pairs).

Both hold. Separately, `c1_tail_registry verify` recomputes every stored operator artifact from its own exact payload
and compares every certified field.
