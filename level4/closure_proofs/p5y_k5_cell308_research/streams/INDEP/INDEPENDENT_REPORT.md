# Stream F2: independent reconstruction of the Theorem MB composition layers (obligation O4)

**Status:** VALIDATED_SYNTHETIC. V1 passes 59 of 59 checks. V2: every layer agrees with its reference, and the
primary TPT-B value lies in the F2 bracket on all 18 decoys and on 177 synthetic profiles. V3: every non-equivalent
planted mutant is detected, in both directions.

**Shared code surface:** none that does any work. See section 6.

**Quarantine:** 0 target evaluations. No tail-cell number was read or written. No drift in the band or its mirror was
evaluated; the band appears only in two refusal controls. The quarantine scan PASSes with 0 findings.

Nothing here is staged or committed.

## 1. Independence protocol and timeline

All times are UTC on 2026-09-28. The ledger agent is `streamF2`.

| time | event |
|---|---|
| 14:47 | Stream start (ledger `INFRASTRUCTURE`). Sources read from theorem text only:<br>• THEOREM_MB r1 (full)<br>• THEOREM_RLR307 §0–§1 (D14, Lemma Lad)<br>• THEOREM_AD §4 (Lemma Dv, Dv′ r2, whole-kernel supersolution)<br>• THEOREM_TPT §0–§2b<br>• THEOREM_TCT §0–§4 (Lemma G, (P2′), (P3′), §4 profile). §5 was **not** read. |
| 14:47–15:07 | Wrote `mb_independent.py` and `v1_synthetic.py`. V1 passed 59/59. |
| 15:07:38 | **Freeze before any primary read.** `mb_independent.py` sha256 `32aa83a8…a16ca4c0` recorded in the ledger (`SYNTHETIC_VALIDATION`). A copy was kept in the scratchpad. |
| 15:08–15:31 | Primary and reference **code** read, for the harness only:<br>• ASSEMBLY `decoy_gen.py`, `tptb_tail.py`, `frozen_path_loader.py`<br>• `deflated_consume.atom_constants_r2` / `atom_constants` and its κ constants<br>• `c2_d5_forecast.combine` / `_atom_independent` / `direct`<br>• `tct_rule.atom_constants_generic`<br>• OV `tpt.py`: `SourceTerm`, `CellProfile`, `rad_poly`, `lo_hi_polys`, `_check`, `_crossing`, `check_nonempty`, `penalty_c5t`, `penalty_frozen`, `Block`, `_check_blocks`, `penalty_blocked`<br>• A0 `a0_ladder.py` (header and `compose`), `a0_common.py` header<br>• `rlr307_independent.py` (whole)<br>• function list of `rlr307_stage1.py`<br>No data file of any cell was opened. |
| 15:33–15:58 | Harness development and runs (`compare_primary.py`, one ledger line per run). The first run used a loose tolerance and failed V3 (see §5). |
| 15:58 | `shared_surface.py` run. `mb_independent.py` is **byte-identical to the pre-read freeze**: no edit was made after any primary file was read. |

## 2. What was implemented (`mb_independent.py`, stdlib only: `fractions`, `re`)

Every function is pure and works on exact `Fraction`s. The module refuses:
* floats, bools and decimal strings;
* inputs that break a premise.

"No bound" (+∞) is `None` or the singleton `INF`. The input schema is documented in the module docstring.

| layer | function | statement implemented |
|---|---|---|
| L1 | `dv_prime` | Lemma Dv′ r2, with Ā_eff = min(Ā, τ/D_lo) |
| L2 | `dv_prime_M` | Lemma Dv′-M: Ā′ = min(Ā_B, U_Λ). Optional Lemma DM refresh (requires τ_a,lo). |
| L3 | `d14_M` | Declaration D14 with Ā′ = min(Ā, Ū). C3 A0 slot = min(Ā′_eff, C_R). With `dlo_refresh`, D_lo′ = max(D_lo, τ_a,lo/Ā′) is used everywhere: δ_j, τ/D_lo and L_j/D_lo. |
| L4 | `lemma_g` | (C_R, κ₁C_R², κ₂C_R² + 2κ₁²C_R³) |
| L5 | `envelope` | Running minimum over strictly increasing block drifts b ≥ 0. `None` means no certificate. |
| L6 | `block_supply` | Componentwise minimum. S_I1 is mandatory. Provenance is given per component, plus the list of all members attaining the minimum. |
| L7 | `ladder` | Lemma Lad: min over CERTIFIED rungs for the upper keys, max for the lower keys. Returns `None` if no rung is certified. Unknown keys are refused. |
| L8 | `tptb` | Theorem TPT-B / MB §7. Exact bracket `[P_lo, P_hi]`, width < 2^-150 (see below). |
| L9 | `gamma_mb` | Γ bracket = g_hi + [P_lo, P_hi]:<br>• CLOSED iff g_hi + P_hi < 0<br>• NOT_CLOSED iff g_hi + P_lo ≥ 0<br>• UNDECIDED otherwise |

Helpers:
* `dyadic_hull`, which computes 2^-20 outward hulls;
* `check_kappas`, an exact sufficient check using rational lower bounds on π and e. It accepts both the frozen
  κ = (7978846/10⁷, 9678830/10⁷) and the RLR κ₁ = 7978845609/10¹⁰. It rejects values below √(2/π) and 4φ(1).

### How L8 works

**Profile.** The profile is built straight from Lemma TC-P:
* rad_r = A0·p2 + 2A1·p1 + A2·p0, and half_r = rad_r + s|Ĝ_r(a)|.
* lo_i and hi_i use weight 1/m on each r, plus the W interval (given pre-summed or as c·[lo, hi] terms).
* The cap H_final is applied.

**Pieces.** The cell is cut at every end of every E_i and at e0.
* Right side: integrand (e0 + s)·min(−H.lo, −lo_i(s)).
* Left side: integrand (e0 − s)·min(H.hi, hi_i(s)).
* P*_B = max(0, all running integrals at piece ends).

**Why the cap crossing is handled rigorously.** On each piece, g (that is −lo_i, or hi_i) has non-negative
s¹…s⁴ coefficients. This is checked, so g is non-decreasing. The cap crossing is therefore unique, and exact
bisection isolates it to 2^-200 (refined further if needed). On the isolating interval [α, β], w·g(α) ≤ integrand
≤ w·c because w > 0, and this gives an exact bracket.

**Premise checks (refusals).**
* C5: E = [e0 − ρ, e0 + ρ] must hold exactly, and x_lo > 0.
* C6: the capped band must be non-empty at the inner end of **every** piece.
* The E_i must tile E exactly.
* All constants must be non-negative.
* m must match the number of source terms.
* Intervals must be ordered.
* M_consumed must equal mag(H_final) when it is given.
* The research band guard is on by default. A formal namespace would have to pass `research_band_guard=False`
  explicitly.

**Test-only hooks.** The private `_mutant` hooks (`endpoint_only`, `flip_t`, `drop_piece_end`) exist only for
controls. They default to off.

## 3. V1: synthetic exact cases (`v1_synthetic.py` → `results/V1_RESULTS.json`, 59/59)

**Hand-computed values:**
* **L1–L4:** Dv′ examples where Ā binds and where τ/D_lo binds, with Ā = ∞. Dv′-M, with and without DM.
  D14 with Lemma-G caps binding, and the C3 A0 slot. D14-M together with DM (D_lo′ = 3/4 binds). Lemma G.
* **L5–L7:** envelope with `None` entries; ladder with a non-certified rung ignored.
* **L9:** decision boundaries, including Γ_hi = 0, which is **not** CLOSED.

**TPT-B hand cases:**

| case | expected | result |
|---|---|---|
| (a) Single block. This is the TPT closed form (Corollary TPT-M). | 41/6 | exact, including when split into 4 identical blocks |
| (b) Constant profile. This equals the C5-T closed form. It is reached both through rad = 0 and through caps binding everywhere. | 27/2 | exact |
| (c) Decreasing block constants | 17/2 at an interior piece end | exact. The endpoint-only rule gives 49/8 < 17/2 and is invalid (C4 reproduced). |
| (d) Irrational crossing at √2 | 23 − 20√2/3 | the bracket contains it (checked exactly, integers only), width < 2^-150 |
| (d′) Irrational crossing below the band | 19/4096 − √2/768 | the bracket contains it |
| (e) Rational crossing, hit exactly | 83/48 | width 0 |

**Refusals.** All of these were refused:
* E ≠ [e0 − ρ, e0 + ρ] by 10⁻³⁰;
* x_lo = 0, and a negative-side cell;
* floats;
* an empty band at s = 0;
* **an empty band only at an outer piece's inner end** (the s = 0 check passes there);
* a tiling gap;
* a negative block constant;
* an m mismatch;
* an unordered Ĥ;
* M_consumed ≠ mag;
* a band cell (refused by the guard).

**Fuzz, 160 random exact cases.** Settings: 1–4 sources, 1–6 blocks, decreasing-constant modes, tight and shifted
caps.
* 154 cases were accepted and 6 were refused under C6.
* Every refusal was confirmed by an independent pointwise evaluation.
* No accepted case has an empty inner end.

On the accepted cases:
* The width is always < 2^-150; the worst is about 2^-389.
* The bracket is consistent with an independent Darboux bracket that uses the pointwise TC-P formulas.
* P_hi ≤ the C5-T closed form.
* Running integrals at 2010 interior points and piece ends never exceed P_hi. This is a direct check of the
  piece-end theorem.
* P_B ≤ P_TPT using the componentwise-max single block.
* Raising any block constant never lowers P.

**Self-controls.** The fuzz checks catch each planted module mutant: endpoint-only 1, flip_t 55, drop_piece_end 28
detections.

## 4. V2: comparison with the primary (`compare_primary.py` → `results/V2V3_RESULTS.json`)

| layer | reference (committed-format, loaded only in the harness) | cases | agree |
|---|---|---|---|
| L1 | frozen `deflated_consume.atom_constants_r2` (through the primary's pinned loader) | 409 (decoy Dv′ sources + synthetic grid) | 409 |
| L1 | `c2_d5_forecast._atom_independent` | 409 | 409 |
| L1 | `rlr307_independent.dv_prime_r2` | 409 | 409 |
| L2 | substitution identity: Dv′-M(Ū) = frozen Dv′ r2 at Ā′ = min(Ā, Ū) | 409 | 409 |
| L4 | frozen `tct_rule.atom_constants_generic`; `rlr307_independent.lemma_g` | 209 / 209 | 209 / 209 |
| L6 | frozen `c2_d5_forecast.combine` (values, and the primary's provenance is among the F2 attaining members) | 309 | 309 |
| L3 | `rlr307_independent.block_supply` for plain D14 with the A0 slot | 400 | 400 |
| L3 | D14-M = D14 at Ā′ | 400 | 400 |
| L3 | D14-M + DM = D14 at (Ā′, D_lo′), with D_lo′ checked. DM binds in 126 of these cases. | 400 | 400 |
| L7 | `rlr307_independent.ladder` (key names mapped) | 200 | 200 |
| L7 | committed `a0_ladder.compose` output fields of the 4 A0 LADDER files (validation drifts 3 and 7/2) | 4 | 4 |
| L5 | literal definition, written separately in the harness. No primary implementation exists (§7). | 300 | 300 |
| L8 | `tptb_tail.evaluate_bundle` on all 18 in-memory decoys: P_B and P_TPT inside the F2 bracket; C5-T equal; Γ decision consistent; the primary's `tpt.penalty_blocked` reproduces its own record | 18 | 18 |
| L8 | the primary's `tpt.penalty_blocked` on 177 synthetic profiles (the V1 generator + 40 rise-then-fall cases), label DECOY 9100+i | 177 | 177 |
| C6 | the refusal decision against the primary consumer's per-piece G-R4 rule (`tptb_tail._pieces` + `band_at` at s_a) | 191 | 191 (14 refused by both) |

**L8 on the decoys:**
* **11 of 18: exact equality.** P_lo = P_hi = P_primary.
* **7 of 18: the cap crosses inside a piece.** The primary exceeds P_hi by 2^-126 to 2^-146, and P_primary ≥ P_lo
  always. The primary is sound and never below the bracket.
* **Tolerance used.** Each case gets an F2-side tight bound on the primary's split excess, between 2^-121 and 2^-143.
  - The primary's `_crossing` returns the left end a of a 60-bit bisection over [0, ρ], so s* − ρ/2^60 ≤ a ≤ s*.
  - The excess on one piece is then at most (ρ/2^60)·x_hi·(c − g(max(s_a, α − ρ/2^60))).
  - This is second order, because c − g is itself O(ρ/2^60) near the crossing. That is why the observed excess sits
    near 2^-126.

## 5. V3: planted mutants (same comparison functions as V2)

All counts are from the final run. Terms used in the table:
* **eq** means the mutant's output is exactly equal to the original. Such a mutant is counted as equivalent, never
  as a detection.
* **det L/S** gives detections split into too-large and too-small mutants.

| class | n | non-eq | detected | det L / S | eq |
|---|---|---|---|---|---|
| L1 component ×(1 ± 2^-40) | 2454 | 2454 | 2454 | both | 0 |
| L2 component ×(1 ± 2^-40) | 2454 | 2454 | 2454 | both | 0 |
| L3 component ×(1 ± 2^-40) | 2400 | 2400 | 2400 | both | 0 |
| L3 D_lo′ ×(1 ± 2^-40) (DM mutant: too large = unsound, too small = loose) | 800 | 778 | 778 | both | 22 |
| L4 component ×(1 ± 2^-40) | 1254 | 1254 | 1254 | both | 0 |
| L5 right-hand-U envelope min_{i≤j+1} | 300 | 184 | 184 | S | 116 |
| L5 component ×(1 ± 2^-40) | 586 | 586 | 586 | both | 0 |
| L6 component ×(1 ± 2^-40) | 1854 | 1854 | 1854 | both | 0 |
| L7 composed key ×(1 ± 2^-40) | 336 | 336 | 336 | both | 0 |
| L7 upper key composed by max | 168 | 83 | 83 | L | 85 |
| L8 decoys: P_B ×(1 ± 2^-40) | 36 | 36 | 36 | 18 / 18 | 0 |
| L8 decoys: block supply component ×(1 ± 2^-40) (primary `penalty_blocked` on mutated triples) | 324 | 180 | 180 | 90 / 90 | 144 |
| L8 decoys: swapped block triple | 36 | 27 | 27 | 14 / 13 | 9 |
| L8 decoys: missing piece end (a block boundary dropped) | 36 | 17 | 17 | 4 / 13 | 19 |
| L8 decoys: consumed H_final end ×(1 ± 2^-40) | 72 | 18 | 18 | 9 / 9 | 54 |
| L8 decoys: sign flip of t (value from the F2 hook, placed in the primary record) | 18 | 18 | 18 | 0 / 18 | 0 |
| L8 decoys: endpoint-only rule (from the primary's own `I_right_full`, `I_left_full`) | 18 | 0 | 0 | none | 18 |
| L8 synthetic: P_B ×(1 ± 2^-40) | 354 | 354 | 354 | 177 / 177 | 0 |
| L8 synthetic: block supply component | 1292 | 576 | 576 | 286 / 290 | 716 |
| L8 synthetic: swapped block triple | 469 | 335 | 335 | 168 / 167 | 134 |
| L8 synthetic: missing piece end | 469 | 256 | 256 | 123 / 133 | 213 |
| L8 synthetic: sign flip of t | 177 | 177 | 177 | 26 / 151 | 0 |
| L8 synthetic: endpoint-only rule | 177 | 41 | 41 | 0 / 41 | 136 |

Across all L8 mutant classes, 915 too-large and 1120 too-small mutants were detected.

**Direction limits.** Some classes can only fail in one direction, and the table shows that:
* The endpoint-only rule and the right-hand-U envelope can only be too small.
* Composing an upper key by max can only be too large.

**The first harness run failed V3.** That run used a loose, first-order tolerance, equivalent to the primary's own
`tptb_tail.split_tolerance`: about 2^-57 to 2^-65. Under it, 12 of 180 too-large block-component mutants on the
decoys went undetected. Their effect was 2^-58 to 2^-67. With the tight second-order bound of §4, all 180 are
detected. The ledger line of that run records `ok=False`.

## 6. Shared code surface (`shared_surface.py` → `results/SHARED_SURFACE.json`)

* **Static imports** of `mb_independent.py`: `__future__`, `fractions`, `re`. There are no non-stdlib imports.
* **Runtime:** `import mb_independent` in a fresh `-I -B` interpreter loads no non-stdlib module.
* **Textual overlap.** This compares normalised code lines (docstrings and comments removed, at least 24
  characters) against 39 primary and reference files. The references are ASSEMBLY, A0, VERIFY, OV `tpt.py`, OV
  `c1b_*`/`c2b_*`, `rlr307_independent`/`stage1`, `deflated_consume`, `c2_d5_forecast`, `tct_rule` and `tc_rule`.
  - 7 distinct identical lines in total, all boilerplate: `from __future__ import annotations`,
    `from fractions import Fraction`, and three generic loop or list idioms in polynomial helpers
    (`for i, x in enumerate(a):` and similar).
  - The maximum identifier 6-gram Jaccard similarity is 0.016, against `tpt.py`.
* **Provenance:** the sha256 now equals the pre-read freeze `32aa83a8…`.

The formulas coincide with the primary's because both transcribe the same lemmas; for example, the p0/p1/p2
coefficient lists match `tpt.rad_poly` term for term. They were written before reading, as the freeze proves.

## 7. Open issues and observations

1. **No primary implementation exists yet for the MB-new composition parts.**
   * **Affected parts:** D14-M with Ū, Lemma DM (D_lo′), the envelope over block drifts, and the per-block
     min over {S_I1, Dv′-M, D14-M, G}. Nothing in ASSEMBLY, A0 or VERIFY implements them.
   * **How they were checked instead:** by the substitution identity against D14 and Dv′ references
     (`rlr307_independent`, which is itself a reconstruction and not the pinned `c1b_certpw.assemble` path), and
     by a literal definition for L5.
   * **What to do:** once a primary block-composition layer exists, rerun `compare_primary.py` against it.
2. **The TC-T tuple derivation was not reconstructed.** This is the step that derives f_G and Env4 from (P2′) and
   (P3′). F2 consumed the tuple the primary extracted from the frozen path. Because `tptb_tail.rederive_tuple` has
   now been read, an independent reconstruction of that layer needs a different agent.
3. **Tolerance for a formal gate.** The primary's own loose split tolerance, about 2^-57, can hide 2^-40-relative
   block-constant mutants. A formal comparison gate should use the second-order sliver bound (`f2_tol_tight`) or
   exact equality.
4. **The decoy set does not test the endpoint-only rule.** All 18 decoys have monotone running integrals. The
   endpoint-only mutant was covered only through the 40 synthetic rise-then-fall profiles. ASSEMBLY should add a
   decreasing-constant decoy regime.
5. **C6 must stay with the consumer.** `tpt.penalty_blocked` alone checks the band only at s = 0 with the cell
   constants. In 14 synthetic profiles it would return a value where C6 refuses. `tptb_tail` G-R4 does refuse, and
   agreed with F2 on all 191 profiles.
6. **Module-surface choices a formal pin must accept or strip:** the research band guard (default on, explicit
   opt-out), and the private `_mutant` hooks (default off).
7. **Scope of the sign-flip control.** The sign-flip-of-t mutant value is produced by the F2 hook, not by the
   primary's code. The mutant proves the comparison detects that defect class. It does not show the primary is free
   of it: that rests on V2 equality.

## 8. Files (all under `streams/INDEP/`)

| file | content |
|---|---|
| `mb_independent.py` | the independent module (sha256 `32aa83a8…a16ca4c0`, unchanged since the freeze) |
| `v1_synthetic.py` | V1 (stdlib + module only) |
| `compare_primary.py` | V2/V3 harness. It imports the primary and reference code through the primary's pinned loader and by path. |
| `shared_surface.py` | the shared-surface measurement |
| `results/V1_RESULTS.json`, `results/V2V3_RESULTS.json`, `results/SHARED_SURFACE.json`, `results/F2_SUMMARY.json` | results (sizes as log2 only; no tail figure) |

Ledger: 9 `streamF2` lines, classes INFRASTRUCTURE and SYNTHETIC_VALIDATION, with no LEAK_FLAG:
* 1 start line;
* 1 V1 freeze line;
* 5 harness runs (the first `ok=False`, then 4 `ok=True`);
* 1 shared-surface line;
* 1 final V1 re-run plus scan line.
