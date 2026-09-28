# C1b ROUTE SUMMARY (R2 revision) — regenerative LR (RLR) certificate for the atom constants A1, A2 on the real CUSUM kernel

> **LATENT-PROXY NOTICE (QUARANTINE_AMENDMENT_2 R2.3).**
> * Appendix V, `NS/validation/C1B_*.json` and `logs/*` carry certified validation-drift values (Λ, τ, C_T, …).
> * They are reported by content class only. Their values must not be quoted in cross-route or handover text.
> * They must never be put next to any tail-cell number (S8, R2.1).
> * No Theorem-M transfer into [6/5, 13/5] is derived or stated (R2.2).
> * The body of this summary contains no validation-drift values. All numbers are in Appendix V.

Stream C1b. Non-target drifts only.

**Governance: CLOSURE-ONLY under floor r2.** RLR supplies constants other than Lemma G / Lemma Dv′ r2, so adoption
needs a user-decided floor extension, frozen before any evaluation.

**Quarantine.**
* Every entry point calls `Q.guard_drift`.
* Drifts used: e ∈ {0, 1/4, 1/2, 1, 3} and the block [1/2, 17/32], with its endpoints.
* No cell id appears in any code or output.
* No committed tail value is read.

**Route state: VALIDATED_NON_TARGET.** It is not FREEZE_READY (§8).

This revision answers conditions C1–C4 of REVIEW_RLR_R2 (ACCEPTED_WITH_CONDITIONS), as the coordinator instructed.
The status of each condition is in §0.

## 0. REVIEW_RLR_R2 conditions — status

| cond. | requirement | status | where |
|---|---|---|---|
| C1 | Correct the (i′)-ladder claim (old :91) and the continuity / null-set reasoning (old :269). Make no "never worse than Dv′" claim for certified ρ | DONE for this stream's files (§1, §3, §4, §8). THEOREM_LR.md:223 and C1LR_ROUTE_SUMMARY.md:28 belong to C1a and are not mine to edit (Q7); they are **left to their owner** | §1 "Guarantee", §3, §4, §8 |
| C2 | Put the combined supply in load-bearing code, with a test that can fail | DONE. `c1b_certpw.assemble` returns SUPPLY (D14). `c1b_test_combined.py` tests it, with two mutants | §1, §5.3 |
| C3 | Push class-(a) plants through the block (e_r > 0) checkers, including a discriminant-only plant and an interior-drift-only plant, with a positive control. Declare the block family. Assert the N1′/N4 preconditions | DONE: `c1b_blockctl.py`, D12, D15, and asserts in `c1b_negctl.py` | §3, §5.1, §5.2 |
| C4 | Re-pin, record code hashes and CLI flags in every output, and regenerate once with the pinned code | see §6 | §6 |
| C5 | Latent-proxy listing | Not assigned to me. I added the banner above and moved all values to Appendix V; the config list itself is outside my directory | — |

## 1. What is certified (statements)

Model (re-derived as in C11):
* Parameters: K = 1/2, H = 5, C = 11/2. State (p, m), and z + e ~ N(0,1).
* Update: T(x,z) = ((p+z−K)^+, (m−z−K)^+).
* Alarm-free window [m−C, C−p]. The atom is a = (0,0), with atom window [m−K, K−p].
* K̂_e is the taboo kernel: the window minus the atom window. The score is S = −(z+e).
* Reachable set: R = {0 ≤ p, m ≤ 5 : p = 0 or m = 0 or p+m ≤ 4}.

The following holds at each declared drift e (pointwise), and for every e in the declared block (block-uniform, §3):

| id | statement | producer |
|---|---|---|
| S1 | w_T ≥ 1 + K̂_e w_T and w_T ≥ 0 on R ⇒ τ := w_T(a) ≥ τ_a and C_T := sup_R w_T ≥ ‖Ĝ_e‖ (Lemma T) | `c1b_certpw.check_supersolution` |
| S2 | W ≥ 1 + K_e W and W ≥ 0 on R ⇒ Ā := W(a) ≥ Λ(e) and C_R := sup_R W ≥ ‖R_e‖ | same, with `whole=True` |
| S3 | Two-sided tame-error enclosures of τ_a, Ŝ2, E_a Σ n, D, D′ and D″, plus subsolution lower bounds for τ_a and Λ | `certify_degree` (S3) |
| S4 | One-sided (i′) quadratic certificates for Ŝ2 (forcing μ²) and L1 (forcing c/2 + g₂μ², with 2c·g₂ ≥ 1). The checker requires A_lo > 0, C_lo ≥ 0 and B² ≤ 4A_loC_lo on every box and x-region. Also a one-sided T_N certificate | `quad_check`, `lin_check` |

**Assembly (`c1b_certpw.assemble`).** There are three supplies, all built from the SAME certified inputs, plus their
combination:
* **Raw RLR** (THEOREM_LR LR-3), taking the termwise min of the ratio and non-ratio forms:
  * A1 = q1 + Ā_eff δ1 and A2 = q2 + 2q1δ1 + Ā_eff(2δ1² + δ2);
  * q_j = min(Ā_eff ρ_j, L_j/D_lo), ρ_j = L_j/τ_a,lo, and L2 ≤ Ŝ2 + T_N.
* **Dv′ r2** (THEOREM_AD §4), with κ1 = √(2/π) and κ2 = 4φ(1) (Lemma K).
* **Lemma G** in the THEOREM_LR LR-4 form, with C_R: G1 = κ1C_R² and G2 = κ2C_R² + 2κ1²C_R³.
* **SUPPLY (declaration D14):**
  * Take the term-level minimum c_j = min(q_j, Ā_eff·(Dv′ factor)_j).
  * Then A1 = c1 + Ā_eff δ1 and A2 = c2 + 2c1δ1 + Ā_eff(2δ1² + δ2).
  * Finally take the componentwise minimum with G. For A0 this is min(Ā_eff, C_R).

**Guarantee (corrected wording, REVIEW_RLR_R2 §1.3).**
1. With EXACT excursion ratios, LR-3 gives A_j^RLR ≤ A_j^Dv′. This is a theorem.
2. With CERTIFIED ratios (Cauchy–Schwarz for L1, the triangle bound for L2), raw RLR carries **no** such guarantee.
   The review exhibits exact fixtures where the certified CS ρ1 exceeds κ1C_T.
3. Only SUPPLY is guaranteed to be ≤ Dv′ r2 and ≤ Lemma G componentwise. This holds by construction and is tested in
   §5.3.

Any observation that raw RLR lies below Dv′ at the declared drifts is **empirical at those drifts only**
(Appendix V). It is not a consequence of LR-3.

## 2. Implementation (this directory)

| file | role | trust |
|---|---|---|
| `c1b_gauss.py` | Rigorous φ and Φ at rationals (integer fixed point at 2^-160, proved remainders). sup\|φ^(n)\| ≤ E\|Y\|^n/√(2π) | load-bearing |
| `c1b_kernel.py` | Exact closed forms ("G-forms") of K̂^(j)w. Taylor-model box enclosures in exact dyadic integers. The cover of R | load-bearing |
| `c1b_pw.py` | Strip-piecewise family (D8). Per-x-region closed forms. The D13 region rule. `in_R` | load-bearing |
| `c1b_certpw.py` | S1–S4, the checkers, the assembly including SUPPLY (D14), and JSON output with provenance | load-bearing |
| `c1b_certify.py` | Plain-polynomial baseline certifier | load-bearing (baseline) |
| `c1b_float.py` | Quadrature, LS collocation and QR (candidates only) | UNTRUSTED |
| `c1b_prov.py` | Records code hashes, pins, CLI flags and argv in every output | provenance |
| `c1b_negctl.py`, `c1b_blockctl.py`, `c1b_test_combined.py` | Point controls N1–N4, block controls B0–B4, and the combined-supply test with mutants | validation |
| `c1b_mc.py`, `c1b_report.py` | NON-CERTIFIED Monte Carlo; aggregation plus the MC consistency checks | context / report |

Internal independent checks (unchanged from R1):
* The exact closed form agrees with split Gauss–Legendre quadrature at the 1e-15 level.
* The mass balance K̂1 + k_a + h1 = 1 holds exactly.
* The φ/Φ intervals intersect those of c7_gaussian.
* The integer and Fraction Taylor models agree.
* The float solves reproduce the Sherman–Morrison identity Λ = τ_a/D.
* MC consistency (§5.4).

## 3. Families, scaling and checker coverage (declared before running; PROGRESS.md D3, D6–D16)

**Point family.** PW_d on the strips t = p+m ∈ [0,1], (1,2], (2,3], (3,5] (D8), with d ∈ {4, 6, 8}. The baseline is
P_d with d ∈ {6, 8, 10, 12}.

**Block family (D12, decided).**
* e-FREE PW_d, one candidate per block, solved in float at the block midpoint.
* Uses the D11 light enclosure settings: 2 extra levels and the single s-rung 2^-4.
* e-affine candidates are not part of this route version.

**Other rules.** Scaling rules, candidate generation and arithmetic follow D3/D6/D7/D16 and are unchanged in R2.

**Coverage and ownership (corrects old :269).**
* The x-region J = ⌈p+m⌉ (with J = 1 for p+m ≤ 1) owns each state, and strips are right-closed.
* Piece B maps a state with p+m = t > 1 onto the whole line p′+m′ = t − 1. Its images carry **positive mass on a
  line**, and they fall ON a strip line whenever t − 1 is an integer. So they are **not** a null set.
* Consequently K̂w is in general **discontinuous** in x across those lines when w is discontinuous.
* Correctness instead rests on the following:
  * For piece B, each region-J closed form uses the strip that owns p′+m′ ∈ (J−2, J−1], under the same right-closed
    convention.
  * So the owning region's form is the exact residual at every state of its closed region, including the boundary
    line.
  * Every box is checked with every region form it meets, which is a superset of what is needed.
  * The axis images of pieces A and C, and their strip crossings, genuinely are null sets.
* R1 and R2 confirmed that the code implements this.

**D13 (R2, soundness-preserving).**
* States of R with p+m > 4 lie only on the axis segments, and the 1-D boxes cover those. So the J = 5 form is checked
  on 1-D boxes only.
* A "pointwise violation" is reported only at a box centre that is a point of R, tested in its owning region.
* Before D13 the J = 5 form was also checked on 2-D boxes; the part of such a box with p+m > 4 lies outside R.

## 4. What the regenerated evidence certifies (flags and counts only; values in Appendix V)

**Evidence.** The evidence comes from pinned code only (§6):
* 15 point rungs, one per pair of e ∈ {0, 1/4, 1/2, 1, 3} and d ∈ {4, 6, 8}, in `NS/validation/C1B_R2_PW_POINT_e*_d*.json`;
* one block rung (`C1B_R2_PW_BLOCK_1_2__17_32_d4.json`);
* 8 plain-baseline rungs (`C1B_R2_PLAIN_POINT_e*_d*.json`).

The aggregate is `C1B_R2_SUMMARY.json` (`rung_flags`, `source_provenance`).

**Status of every rung.**
* All 16 PW and block rungs are **CERTIFIED**.
* Every S1/S2 supersolution passes.
* **Every** (i′) check passes in every rung: TTT/TTT on the point rungs, and the single declared rung (T/T) on the block.
* Every one-sided T_N check passes.

**Correction of the old claim (old :91, R2 finding F1).** The pre-pin summary said "every (i′) checker passes". That
was false:
* In the pre-pin rung e = 3, d = 6, the S2 checks failed at all three s-rungs and the L1 checks failed at two of three.
* Those failures were sound. The ladder minima fell back to the tame bound and to passing rungs.
* All eight failures were flagged at box centres with p+m > 4, which lie *outside* R. The J = 5 form had been checked
  on 2-D boxes. So the old "pointwise violation" label wrongly claimed a reachable witness.
* With D13 the same rung passes all six checks. The pre-pin files are preserved in `logs/prepin/`.

**What is guaranteed.** At every declared drift and on the block, SUPPLY (D14) is a valid combined supply and is ≤ Dv′ r2
and ≤ Lemma G componentwise.

**Observed, not guaranteed.**
* At all five drifts and on the block, SUPPLY equals raw RLR: neither the min with the Dv′ factors nor Lemma G binds
  (`A*_SUPPLY == A*_RLR`, exact).
* That raw RLR lies below Dv′ there is an **empirical fact at these drifts only** (Appendix V). It is not a theorem
  for certified ρ (§1).

**MC consistency** (NON-CERTIFIED; `mc_checks`, each a check that can fail) passes at all 5 drifts and at both block
endpoints.


## 5. Controls

### 5.1 Point controls (`C1B_R2_NEGCTL.json`; e = 1/2 and e = 1/2 ± 2^-12)

All are detected (`all_controls_detected = true`, pinned code):
* N1′ (w_T/2) is rejected, with a pointwise witness. Its precondition V(atom) < 2 is now **asserted in code**.
* N1″ (tight) has an exact witness at x* and is rejected.
* N2: the score-sign finite-difference test passes for the true sign; the flipped first- and second-order scores are
  detected at every declared point.
* N3: the atom-window and alarm-window mutations are detected.
* N4 (a − κ) is rejected. Its precondition C(atom) > 0 is now **asserted in code**.
* N4b is rejected.
* N1 (the declared (1 − 2^-6) scaling) remains a preserved design error. It is not guaranteed invalid, and its
  acceptance is correct behaviour.

### 5.2 Block controls (`C1B_R2_BLOCKCTL.json`, `c1b_blockctl.py`; block [1/2, 17/32], witness drift e* = 33/64)

Every plant goes through the **block (e_r > 0) checkers** of the pinned code. Every invalidity is an exact interval
witness, asserted in code.

| control | construction | witness | result |
|---|---|---|---|
| B0 positive | the certified block w_T and L1 (i′) certificate | — | accepted |
| B1 supersolution | (1 − ε)w_T | residual < 0 at (atom, e*) | rejected; the checker also finds the pointwise witness |
| B2 interior drift only | w_T − cψ(e), with ψ = 0 at both block ends | residual < 0 at (atom, e_c) | **rejected by the block checker**, and **accepted** by the point checkers at both ends. This isolates the e-direction |
| B3 (i′) C-conjunct | a − κ | C′ < 0 at (atom, e*) | rejected |
| B4 (i′) discriminant at witness | a − κ″ | A > 0, C″ ≥ 0, B² > 4AC″ at (x*, e*) | rejected. **Limitation:** the uniform shift also makes C negative elsewhere, so B4 does not isolate the discriminant clause |

`all_block_controls = true`.

**Isolating the discriminant clause** (`r2_blockctl_disc.py`, outside the pinned set; its own sha256 is recorded;
declarations D17, D17b, D17c). Each attempt needs A > 0 and C ≥ 0 **globally** on R × block, established by rigorous
enclosures, together with an exact discriminant witness.

| attempt | construction | outcome |
|---|---|---|
| D17 | uniform forcing shifts | NOT_CONSTRUCTIBLE: the global C margin is too large (preserved) |
| D17b | B inflation alone | NOT_CONSTRUCTIBLE: C goes negative globally on every declared rung (preserved) |
| D17c | B inflation with C-margin compensation a + μw_T | **PLANTED and REJECTED** at the first ladder rung (λ = 1). A > 0 globally; C′ ≥ 0 globally, by a rigorous block enclosure; exact witness B′² > 4AC′ at (x* = (0, 4.625), e*). The pinned block `quad_check` rejects, and every sampled failure is a centre discriminant violation with A > 0 and C > 0. The unmodified certificate passes (positive control). This **isolates the discriminant clause** on the block path. `C1B_R2_BLOCKCTL_DISC.json` is the final file version (own sha256 recorded); the D17 and D17b outputs are in `logs/`. |

### 5.3 Combined supply (`C1B_R2_TEST_COMBINED.json`, `c1b_test_combined.py`)

**What is tested.** The test recomputes raw RLR, Dv′ and G with its own formulas. It checks SUPPLY ≤ min(RLR, Dv′, G)
on each of the following:
* the 16 regenerated rungs;
* three plants: raw RLR worse than Dv′ (plant validity asserted, and SUPPLY < raw RLR required), G smallest, and mixed;
* 2000 seeded random input sets.

**Result.** assemble **passes**. Both mutants are **caught**:
* mutant without the min: the planted cases fail, and 379/2000 random sets fail;
* mutant without Lemma G: the G plant fails, and 153/2000 random sets fail.

### 5.4 Other checks

* **Quarantine static scan:** 0 findings in this stream's files.
* **Ledger:** all entries are NONTARGET_DRIFT_VALIDATION or SYNTHETIC_VALIDATION, with cells_touched = [].
* **MC consistency:** as in §4.


## 6. Provenance (C4)

**Pins.** `NS/validation/C1B_R2_CODE_PINS.json` holds the sha256 of every `c1b_*.py`.
* It was written after all R2 edits and before the regeneration.
* Revision 2 changed only `c1b_report.py`, a crash fix in the aggregator. The load-bearing set is unchanged:
  gauss 3189208d…, kernel dfdc871b…, pw f10c2cf1…, certpw 48080dd4…, certify 47bdc8e2….

**Self-identification.** Every output JSON records `provenance`:
* `code_sha256` of every `c1b_*.py`;
* the pinned set and `matches_pins`;
* `flags` (TIGHT_CT, BLOCK_LIGHT);
* `argv`.

All 16 PW/block sources, NEGCTL, BLOCKCTL, MC, TEST_COMBINED and SUMMARY record `matches_pins = true`.

**Regenerated once with pinned code (27 capped jobs, all rc = 0).**
* PW point rungs: 15.
* Block rung: 1.
* Block controls: 1.
* Plain baseline: 8 rungs, e ∈ {1/4, 1/2}, d ∈ {6, 8, 10, 12}.
* Also: NEGCTL, MC, TEST_COMBINED, SUMMARY.
* Each job was capped at 1200 s with a perl alarm; macOS has no `timeout`. The supplementary B4′ runs were separately
  capped.

**NOT REGENERATED: none.**

**Reproduction versus pre-pin** (`C1B_R2_PREPIN_COMPARISON.json`, counts only).
* PW: 16 rungs, 208 field comparisons.
  * 76 are identical, 128 are tighter and 4 are looser.
  * The looser ones are τ_a,lo at d = 4 for three drifts, by at most 0.45%, and one Λ_lo, by 1e-4 relative.
  * The cause is that D13 changes the adaptive covers. Both old and new bounds are rigorous.
* Plain baseline: 0 identical, 53 tighter and 51 looser. Its untrusted candidates changed, because the float
  quadrature was split at strip crossings after the old plain runs.

The pre-pin evidence is kept in `logs/prepin/` and is superseded.


## 7. Runtimes

Setup: one core, `nice`, and two lanes.
* **Point rungs:** d = 4 takes 31–62 s, d = 6 takes 86–168 s, and d = 8 takes 216–594 s.
* **Block rung:** 185 s. The block controls took 374 s.
* **Plain baseline:** 38–287 s per rung.
* **Sleep caveat:** a system sleep (pmset log, about 08:30–08:46) inflated the wall time of two jobs (pl12d10 and
  e0d6). Both finished under the cap.
* **Effect of D13:** it roughly halves the pre-pin d = 8 times, because it stops checking the J = 5 form on 2-D boxes.


## 8. Freeze binding, gates, readiness

**What a future FROZEN certification would bind** (the route is CLOSURE-ONLY; no block is proposed or evaluated here):
1. The code pins in `C1B_R2_CODE_PINS.json`, load-bearing set as listed in §6.
2. The family: PW_d for points, and the declared e-free PW_d for blocks (D12), with the degree ladder.
3. The scaling rules D3, D6 and D7; D11 for blocks; D13 coverage.
4. Exact arithmetic: 2^-480 G-form grid, 2^-160 φ/Φ, Taylor order 10.
5. A pre-registered block list with dyadic endpoints.
6. **The acceptance rule:**
   * every checker passes;
   * constants are ladder minima;
   * **the consumed output is SUPPLY (D14)**, never raw RLR;
   * no retuning after any evaluation.
7. Every output self-identifies through `provenance`.

**Gates.**

| gate | result |
|---|---|
| G1 | PASS (unchanged) |
| G2 | **PASS, self-checked, independently reviewed (R1, R2).** The corrections are: <br>• LR-3 dominance holds for exact ρ only (§1); <br>• the ownership reasoning replaces the wrong continuity / null-set argument (§3). |
| G3 | PASS |
| G4 | **PASS.** One pinned regeneration, and every output self-identifies (§6). |
| G5 | **PASS.** 5 point drifts plus 1 block, all CERTIFIED with all checks passing. MC is consistent. The point and block negative controls are all detected. |
| G6 | PASS_WITH_NOTES (per R2). There are now block-path negative controls and a combined-supply test with mutants. There is still no second implementation. |
| G7 | **PASS.** D12–D17c were declared before their runs. The failures and NOT_CONSTRUCTIBLE outcomes are preserved. |
| G8 | **PASS.** All values are confined to Appendix V and the latent-proxy artefacts. There is no juxtaposition and no Theorem-M transfer. |
| G9 | Bindable list above. |
| G10 | **Empirical at the declared drifts only:** raw RLR is below Dv′ there (Appendix V). The guaranteed object is SUPPLY. |

**Readiness.** The route stays at **VALIDATED_NON_TARGET**, CLOSURE-ONLY. Conditions C2–C4 are met, and C1 is met for
this stream's files. It is not declared FREEZE_READY by this stream, for three reasons:
1. C1 edits in THEOREM_LR.md:223 and C1LR_ROUTE_SUMMARY.md:28 belong to the C1a owner.
2. C5 (the latent-proxy config listing) is outside my directory.
3. The block family is decided (e-free), but its cost at larger blocks and e-affine candidates remain open work. There is no second implementation of the checker.

Changing the route state is for the coordinator and reviewer to decide.


## Appendix V — LATENT-PROXY VALUES (R2.3; not for handover, never next to any tail number)

Source: `NS/validation/C1B_R2_SUMMARY.json` (producer `c1b_report.py R2_PW`), tables printed by `r2_tables.py`.
Ladder minima (maxima for lower bounds) over the certified pinned rungs d in {4, 6, 8}; exact rationals in the JSON.

**V.1 Certified inputs (pointwise).**

| e | tau | tau_a,lo | C_T | C_R | A-bar | Lambda_lo | D_lo | D1 | D2 | S2^ | T_N | L1 | L2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0/1 | 6.826 | 6.758 | 16.14 | 467.5 | 467.5 | 463.3 | 0.01434 | 0.003671 | 1.127 | 97.52 | 63.79 | 25.81 | 161.4 |
| 1/4 | 7.754 | 7.628 | 17.36 | 140.4 | 139.9 | 139.1 | 0.05442 | 0.4158 | 3.357 | 97.37 | 84.75 | 27.48 | 182.1 |
| 1/2 | 9.032 | 8.809 | 17.57 | 38.11 | 38.03 | 37.97 | 0.2318 | 1.09 | 4.232 | 60.51 | 105 | 23.38 | 165.5 |
| 1/1 | 6.739 | 6.639 | 9.853 | 10.4 | 10.38 | 10.37 | 0.64 | 0.614 | 2.055 | 42.2 | 34.69 | 16.87 | 76.88 |
| 3/1 | 2.558 | 2.557 | 2.59 | 2.583 | 2.574 | 2.573 | 0.994 | 0.01698 | 0.04235 | 2.836 | 2.211 | 2.693 | 5.047 |

**V.2 Supplies (same certified inputs).** SUPPLY = D14 combined supply (only it is guaranteed <= Dv' and <= G).

| e | rho1 | kappa1 C_T | rho2 | Dv' rho2-factor | A1 RLR | A1 Dv' | A1 G | A1 SUPPLY | A2 RLR | A2 Dv' | A2 G | A2 SUPPLY | Dv'/RLR A1 | Dv'/RLR A2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0/1 | 3.82 | 12.88 | 23.89 | 347.3 | 1906 | 6140 | 1.744e+05 | 1906 | 4.888e+04 | 2.023e+05 | 1.303e+08 | 4.888e+04 | 3.222 | 4.138 |
| 1/4 | 3.602 | 13.85 | 23.88 | 400.6 | 1573 | 3007 | 1.573e+04 | 1573 | 3.6e+04 | 1.106e+05 | 3.544e+06 | 3.6e+04 | 1.912 | 3.073 |
| 1/2 | 2.654 | 14.02 | 18.79 | 409.9 | 279.6 | 711.7 | 1159 | 279.6 | 4036 | 2.297e+04 | 7.19e+04 | 4036 | 2.546 | 5.692 |
| 1/1 | 2.541 | 7.862 | 11.58 | 133.1 | 36.31 | 91.54 | 86.33 | 36.31 | 223.1 | 1591 | 1538 | 223.1 | 2.521 | 7.13 |
| 3/1 | 1.053 | 2.066 | 1.974 | 11.05 | 2.754 | 5.363 | 5.324 | 2.754 | 5.281 | 28.73 | 28.4 | 5.281 | 1.947 | 5.439 |

**V.3 Block-uniform (C1B_R2_PW_BLOCK_1_2__17_32_d4.json).** BLOCK-UNIFORM for every e in [1/2, 17/32] (declared non-target)

| tau | C_T | A-bar | D_lo | D1 | D2 | L1 | L2 | A1 RLR | A1 Dv' | A1 SUPPLY | A2 RLR | A2 Dv' | A2 SUPPLY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9.618 | 18.42 | 41.74 | 0.222 | 1.492 | 16.34 | 27.86 | 201.1 | 406.1 | 894.1 | 406.1 | 9436 | 3.388e+04 | 9436 |

**V.4 NON-CERTIFIED context (MC, N = 200000, seed 12345; float fairness Dv' with float C_T).**

| e | MC tau_a | MC D | MC Lambda | MC L1 | MC L2 | Dv'/RLR A1 with float C_T |
|---|---|---|---|---|---|---|
| 0/1 | 6.782 | 0.01455 | 466.3 | 17.12 | 76.8 | 3.167 |
| 1/4 | 7.669 | 0.05579 | 137.4 | 18.74 | 77.74 | 1.881 |
| 1/2 | 8.888 | 0.234 | 37.98 | 16.09 | 84.12 | 2.488 |
| 1/1 | 6.678 | 0.6427 | 10.39 | 10.16 | 35.4 | 2.487 |
| 3/1 | 2.556 | 0.9937 | 2.572 | 1.57 | 2.541 | 1.935 |

