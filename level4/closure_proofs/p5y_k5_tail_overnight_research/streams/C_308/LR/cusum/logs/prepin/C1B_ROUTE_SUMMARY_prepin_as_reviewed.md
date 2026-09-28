# C1b ROUTE SUMMARY — regenerative LR (RLR) certificate for the atom constants A1, A2 on the real CUSUM kernel

Stream C1b. Non-target drifts only. Governance: **CLOSURE-ONLY under floor r2**, because RLR supplies constants
other than Lemma G / Lemma Dv′ r2. Adoption would need a user-decided floor extension, frozen before any evaluation.

Quarantine:
* Every entry point calls `Q.guard_drift`.
* The only drifts used are the declared point drifts and the declared block (see §4).
* Nothing was evaluated in [1.2, 2.6] or its mirror.
* No cell id appears in any code or output.
* No committed tail value is read or quoted in this stream (rule S8).

Status: complete for this session. Route state: **VALIDATED_NON_TARGET** (not FREEZE_READY; see §8).

## 1. What is certified (statements)

Model (re-derived as in C11):
* Parameters: K = 1/2, H = 5, C = 11/2.
* State and update: state (p, m), z + e ~ N(0,1), T(x,z) = ((p+z−K)^+, (m−z−K)^+).
* Alarm-free window: [m−C, C−p]. The atom is a = (0,0), and its window is [m−K, K−p].
* Kernels: K̂_e is the taboo kernel (window minus the atom window). The score is S = −(z+e).
* Reachable set: R = {0 ≤ p, m ≤ 5 : p = 0 or m = 0 or p + m ≤ 4}.

At each declared drift e (pointwise; the block statement is in §4):

| id | statement | producer line |
|---|---|---|
| S1 | w_T ≥ 1 + K̂_e w_T and w_T ≥ 0 on R. Hence τ := w_T(a) ≥ τ_a = E_a σ and C_T := sup_R w_T ≥ ‖Ĝ_e‖ (Lemma T) | `c1b_certpw.certify_degree` → `check_supersolution` |
| S2 | W ≥ 1 + K_e W and W ≥ 0 on R. Hence Ā := W(a) ≥ Λ(e) = E_a τ | same, `whole=True` |
| S3 | Tame-error enclosures of τ_a, Ŝ2 = E_a Σ_{n<σ} M_n², E_a Σ_{n<σ} n, D, D′, D″ (two-sided), plus subsolution lower bounds for τ_a and Λ | `certify_degree`, block "(S3)" |
| S4 | One-sided quadratic certificates on the augmented chain (THEOREM_LR §cert (i′)). The checker requires A_lo > 0, C_lo ≥ 0 and B² ≤ 4 A_lo C_lo on every box and x-region. They give Ŝ2 ≤ a(a) (forcing μ²) and L1 ≤ a(a) (forcing c/2 + g₂μ², with 2c·g₂ ≥ 1). A one-sided certificate gives T_N | `quad_check`, `lin_check` |

Assembly:
* **LR-3** (THEOREM_LR §5.3): ρ_j = L_j,up / τ_a,lo, with L2 ≤ Ŝ2 + T_N (triangle bound, §cert (ii-a)).
  * A1 = min(Ā_eff ρ1, L1/D_lo) + Ā_eff δ1.
  * A2 = min(Ā_eff ρ2, L2/D_lo) + 2 q1 δ1 + Ā_eff(2δ1² + δ2).
  * Here Ā_eff = min(Ā, τ/D_lo) and δ_j = D_j/D_lo.
* **Dv′ r2** (THEOREM_AD §4) uses the **same** Ā, τ, C_T, D_lo, D1, D2, with κ1 = √(2/π) and κ2 = 4φ(1) from Lemma K.
* The code is `c1b_certpw.assemble`.

## 2. Implementation (files in this directory)

| file | role | trust |
|---|---|---|
| `c1b_gauss.py` | Rigorous φ and Φ at rationals, using an integer fixed point at 2^-160 and proved series remainders. sup\|φ^(n)\| ≤ E\|Y\|^n/√(2π) (Fourier). κ1 and κ2 bounds | load-bearing |
| `c1b_kernel.py` | Exact closed form ("G-form") of K̂^(j) w for polynomial w. <br>• Every piece is poly(u)·φ(u), and M_n(A,B) = G_n(A)φ(A) − G_n(B)φ(B) + (n−1)!!(Φ(B) − Φ(A)). <br>• Taylor-model box enclosure of order 10, in exact dyadic integers (`gf_box_int`). <br>• Cover of R | load-bearing |
| `c1b_pw.py` | Strip-piecewise family (D8). Per x-region closed forms, with six extra boundaries l3 − b and l2 + b | load-bearing |
| `c1b_certpw.py` | Certification pipeline S1–S4, the checkers, the assembly and the JSON output | load-bearing |
| `c1b_certify.py` | First-generation plain-polynomial pipeline. It produced the P_d baseline JSONs | load-bearing (baseline) |
| `c1b_float.py` | Quadrature, least-squares collocation and Householder QR | UNTRUSTED (candidates only) |
| `c1b_negctl.py` | Negative controls N1–N4 and the finite-difference score check | validation |
| `c1b_mc.py` | Monte Carlo context | NON-CERTIFIED |

Internal independent checks:
* The exact closed form agrees with independent Gauss–Legendre quadrature to ≤ 1.3e-15 (plain) and ≤ 4.4e-16 (piecewise).
  The quadrature was split at the strip crossings.
* The mass balance K̂1 + k_a + h1 = 1 holds exactly.
* φ and Φ intervals intersect those of `c7_gaussian` (an independent rational implementation) at 5 declared points.
* The integer and Fraction Taylor models agree to 2e-44 on 5 declared boxes.
* The float solves reproduce the Sherman–Morrison identity Λ = τ_a/D: at e = 1/2 they give 37.9985 against 37.9984.

## 3. Candidate family ladder and scaling rules (declared before running; PROGRESS.md D3, D6–D8)

**Families.**
* Baseline P_d: global Chebyshev polynomials of total degree d, with d ∈ {6, 8, 10, 12}.
* Main PW_d: strip-piecewise polynomials on t = p + m ∈ [0,1], (1,2], (2,3], (3,5], with d ∈ {4, 6, 8}.
  Candidates may be discontinuous across strip lines.
* How the PW family came about: after the P_d ladder was observed to stagnate, D8 was declared from a structural
  diagnosis. The gradient of the atom-window boundary term jumps on p+m = 1, and piece B propagates that jump to
  p+m = 2, 3, 4. The diagnosis used no target information.

**Candidates (untrusted).**
* LS collocation of (I − K̂)X − F on the declared sample set, then rounding to the 2^-200 grid.
* The systems solved are b0 = Ĝ1, b1 = ĜK̂^(1)b0, b2 = Ĝ(K̂^(2)b0 + 2K̂^(1)b1), xT = Ĝb0, d0 = Ĝh1,
  d1 = Ĝ(K̂^(1)d0 + h1′), d2 = Ĝ((K̂^(2) − K̂)d0 + 2K̂^(1)d1 + h1″), and W = R1 for the whole kernel.

**Scaling rules.**
* Supersolutions: w = (1+η)w̃ with η = −r_lo/(1+r_lo), rounded up to 2^-20.
* Explicit certificates: λ is the smallest dyadic at 2^-20 after the factor 17/16, with ladder s ∈ {2^-6, 2^-4, 2^-2}.
* Reported value: the minimum over rungs of each certified input. The lower bounds (τ_a,lo, D_lo, Λ_lo) take the maximum.
  Every rung is an independently valid certificate at the same non-target drift.

**Arithmetic.** Exact rationals and dyadic integers throughout. Only φ and Φ enter as rigorous intervals.

## 4. Results at the declared non-target drifts (certified, pointwise)

**Source.** `NS/validation/C1B_SUMMARY_PW_PW9.json` (producer `c1b_report.py`, function `best_of` then
`c1b_certpw.assemble`).
* The inputs are ladder minima (maxima for the lower bounds) over all certified PW/PW9 rungs d ∈ {4, 6, 8} at that drift.
* Each rung lives in `NS/validation/C1B_PW*_POINT_e*.json`.
* All rungs at all drifts are CERTIFIED: the S1 and S2 supersolutions pass, every (i′) checker passes, and every
  one-sided T_N check passes.
* Values are rounded here; the exact rationals are in the JSON.

Certified inputs:

| e | τ ≥ τ_a | τ_a,lo | C_T ≥ ‖Ĝ‖ | Ā ≥ Λ | Λ_lo | D_lo | D1 ≥ \|D′\| | D2 ≥ \|D″\| | Ŝ2 ≤ | T_N ≤ | L1 ≤ | L2 ≤ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1/4 | 7.787 | 7.531 | 17.50 | 139.90 | 139.14 | 0.05383 | 0.4174 | 3.472 | 97.96 | 85.67 | 27.62 | 183.6 |
| 1/2 | 9.032 | 8.705 | 17.67 | 38.026 | 37.967 | 0.22900 | 1.0896 | 4.240 | 61.13 | 105.03 | 23.50 | 166.2 |
| 1 | 6.739 | 6.616 | 9.853 | 10.378 | 10.375 | 0.63775 | 0.6140 | 2.055 | 42.20 | 34.69 | 16.87 | 76.91 |
| 3 | 2.5582 | 2.5574 | 2.590 | 2.5737 | 2.5729 | 0.99396 | 0.0170 | 0.0424 | 2.836 | 2.211 | 2.693 | 5.047 |
| 0 | 6.833 | 6.693 | 16.16 | 467.49 | 463.31 | 0.014329 | 0.0042 | 1.148 | 97.53 | 64.00 | 25.81 | 161.5 |

Constants, with the Dv′ r2 column computed from the **same** certified inputs:

| e | ρ1 (RLR) | κ1C_T (Dv′) | ρ2 (RLR) | 2κ1²C_T²+κ2C_T (Dv′) | δ1 | δ2 | A1 RLR | A1 Dv′ | A2 RLR | A2 Dv′ | A1 Dv′/RLR | A2 Dv′/RLR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1/4 | 3.667 | 13.96 | 24.38 | 406.8 | 7.755 | 64.51 | 1598 | 3038 | 37221 | 113064 | **1.90** | **3.04** |
| 1/2 | 2.699 | 14.10 | 19.09 | 414.5 | 4.758 | 18.52 | 283.5 | 717.0 | 4128 | 23288 | **2.53** | **5.64** |
| 1 | 2.550 | 7.862 | 11.62 | 133.1 | 0.963 | 3.223 | 36.44 | 91.58 | 224.2 | 1591.6 | **2.51** | **7.10** |
| 3 | 1.053 | 2.066 | 1.974 | 11.05 | 0.017 | 0.043 | 2.754 | 5.363 | 5.281 | 28.73 | **1.95** | **5.44** |
| 0 | 3.857 | 12.90 | 24.13 | 348.3 | 0.293 | 80.14 | 1939 | 6166 | 49875 | 203889 | **3.18** | **4.09** |

**Reading.**
* At every declared drift the excursion LR ratio ρ1 is 2.0–5.2× below Dv′'s κ1C_T, and ρ2 is 5.6–21.7× below.
* At e = 0 the true D′ is 0 by symmetry (the float value is 1e-7); the certified D1 is 0.0042.
* The A-level ratios are smaller because the δ terms are shared by both sides. At e = 1/4, δ1 = 7.76 carries most
  of A1 on both sides. That value is itself close to the float |D′|/D ≈ 7.04, so the dilution is intrinsic and not
  certification slack.
* Fairness check: Dv′ is also recomputed with the most favourable NON-CERTIFIED float C_T (the sup of the float
  b̃0 over the samples), keeping the certified inputs everywhere else. The A1/A2 ratios move only slightly: 2.46 and
  5.34 at e = 1/2, 2.48 and 6.91 at e = 1, 1.93 and 5.38 at e = 3 (field `Dv_with_float_C_T_NONCERTIFIED`). So the
  gain is not an artefact of C_T enclosure slack.
* **These ratios are reported only at these drifts and are not to be combined with any tail quantity (S8).** No
  statement about any other drift is made or implied. In particular, no monotonicity transfer (e.g. via Theorem M)
  into the quarantined band is made.

## 4b. Block-uniform result on [1/2, 17/32]

**Statement.** The file is `NS/validation/C1B_PW9_BLOCK_1_2__17_32.json`. The run was
`c1b_certpw.py block 1/2 17/32 4 --tight-ct --block-light`, with declarations D8 and D11. For EVERY e ∈ [1/2, 17/32]:
* S1 and S2 hold with one e-free w_T and one e-free W.
* The residual enclosures are taken over R × [1/2, 17/32], using 3-variable Taylor models in (p, m, e).
* The (i′) certificates and the T_N certificate hold for every e in the block.

Hence the constants below are admissible uniformly on the block (THEOREM_LR §6; THEOREM_AD §8 block form).

**Certified inputs.** τ 9.808, τ_a,lo 7.956, C_T 18.79, Ā 41.74, D_lo 0.2204, D1 1.528, D2 17.86, Ŝ2 ≤ 87.13,
T_N ≤ 127.7, L1 ≤ 29.23, L2 ≤ 214.8.

**Constants.** ρ1 = 3.674 against κ1C_T = 14.99, and ρ2 = 27.00 against 467.7.

| | RLR | Dv′ (same inputs) | Dv′/RLR |
|---|---|---|---|
| A1 | 422.1 | 915.1 | **2.17** |
| A2 | 10210 | 35593 | **3.49** |

**Checks.** The MC consistency checks pass at both block endpoints, e = 1/2 and e = 17/32 (MC was run at 17/32 as well).

**Block overhead.** Relative to the best pointwise certificate at e = 1/2 (§4), A1_RLR is 1.49× larger and A2_RLR
2.47× larger. Most of this comes from D1 and D2: D2 = 17.9 against 4.24 pointwise. An e-free candidate pays the
first-order variation ‖∂_e K̂ w‖·e_r in every residual. This matches C1a's fixture lesson.

**Negative result, preserved.** The first block attempt used the declared D2 adaptive rule (tolerance 5/4, 4 extra
levels) and was stopped by me after 24 min, beyond the preamble's ~20 min cap. The 3-D refinement exploded: the d̃0
enclosure alone took 631 s over 28509 boxes. The partial log is `logs/pw9_block_killed_at_24min.log`. The light rule
D11 (2 levels, single s-rung) finished in 246 s.

**Freeze-grade blocks** would need either e-affine candidates X̃ + (e − e_c)X̃′ or finer blocks. The derivative
candidates already exist in the chain (b1 = ∂_e b0, d1 = ∂_e d0, and so on), but this was not implemented tonight.

## 5. Where the remaining slack is (certified versus NON-CERTIFIED context)

Context values come from two NON-CERTIFIED sources:
* `C1B_MC.json`: Monte Carlo, N = 200000 excursions, seed 12345, producer `c1b_mc.py`.
* The float candidates at the atom (`float_context_NONCERTIFIED` in the summary JSON).

| e | τ_a (MC) | τ (cert) | D (MC) | D_lo (cert) | Λ (MC renewal) | Ā (cert) | L1 (MC) | √(τ_a Ŝ2) (float) | L1 (cert) | L2 (MC) | Ŝ2+T_N (float) | L2 (cert) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1/4 | 7.669±.024 | 7.787 | .0558±.0005 | .05383 | 137.4 | 139.90 | 18.74±.11 | 26.56 | 27.62 | 77.7±.6 | 174.2 | 183.6 |
| 1/2 | 8.888±.026 | 9.032 | .2340±.0009 | .22900 | 37.98 | 38.026 | 16.09±.08 | 22.55 | 23.50 | 84.1±.6 | 157.4 | 166.2 |
| 1 | 6.678±.012 | 6.739 | .6427±.0011 | .63775 | 10.39 | 10.378 | 10.16±.05 | 16.23 | 16.87 | 35.4±.3 | 73.0 | 76.9 |
| 3 | 2.556±.002 | 2.558 | .9937±.0002 | .99396 | 2.572 | 2.574 | 1.570±.004 | 2.683 | 2.693 | 2.54±.01 | 5.03 | 5.05 |
| 0 | 6.782±.021 | 6.833 | .0145±.0003 | .014329 | 466.3 | 467.49 | 17.12±.10 | 25.20 | 25.81 | 76.8±.8 | 156.2 | 161.5 |

**Checks.** `mc_checks` in `c1b_report.py` passes at all five drifts. It verifies τ_a,lo ≤ MC + 4se ≤ …,
τ_a,up ≥ MC − 4se, Ŝ2, T_N, L1, L2 ≥ MC − 4se, D_lo ≤ MC + 4se, and Ā ≥ the MC Λ lower bound. Each of these is a
check that can fail.

**Diagnosis.**
* The certification itself is tight. τ, Ā, D_lo, Ŝ2 and T_N are all within 0.1–7% of the float or MC truth.
* The two remaining factors are *theorem-level* losses in the functional, not certification losses:
  1. **Cauchy–Schwarz for L1:** √(τ_a Ŝ2) / E Σ|M_n| ≈ 1.4–1.7×. The per-state c(x) certificate of THEOREM_LR (i′)
     would recover part of this. It is not implemented here.
  2. **The triangle bound for L2:** (Ŝ2+T_N) / E Σ|M_n² − n| ≈ 1.9–2.2×. The quartic certificate (ii-b) would
     recover part of this. It is not implemented here.
* D1 and D2 (the two-sided tame chains) are the loosest certified inputs. D2/|D″| is ≈ 4.1 at e = 1/2 and ≈ 2.4 at
  e = 1. Both sides of the comparison share them.

## 6. Negative controls (C1B_NEGCTL.json, producer `c1b_negctl.py`; e = 1/2 and e = 1/2 ± 2^-12)

| control | expectation | result |
|---|---|---|
| N1 (declared): w_T·(1−2^-6) | rejected | **NOT rejected. This was a design error and is preserved** (`logs/C1B_NEGCTL_run1_N1_design_error.json`). w_T carries certified residual slack of about 0.03, so the scaled function is a genuine supersolution (lower bound +0.0079). Accepting it is correct. |
| N1′ (D10): f = 1/2 | rejected, with a pointwise violation | rejected (lower bound −0.632); pointwise violation found |
| N1″ (D10, tight): f just below 1/(1+ρ*) at the exact argmin centre | rejected | exact residual at x* is −1.17e-6 < 0; the checker rejects (−0.0103) and finds the violation |
| N2: score sign | true sign within the proved Taylor bound (h²/6)E\|He3\|‖w‖; flipped sign outside it | the true sign passes 6/6. The flipped first-order score (weight +(z+e)) and the flipped second-order t (K^(2)+K̂) are each detected at 6/6 points |
| N3a: atom window not removed | mass balance and quadrature both fail | detected (mass deviation 0.341, quadrature deviation 3.02); the correct kernel gives 0 and 3.6e-15 |
| N3b: alarm window shifted by 1/8 | both fail | detected (0.0060, 0.088) |
| N4: explicit L1 certificate with a′ = a − κ | rejected | rejected, with 832 pointwise violations; the unmodified certificate passes |
| N4b: T_N certificate replaced by x̃T/2 | rejected | rejected (lower bound −11.98) |

`all_controls_detected = true`. This counts the N1′/N1″ replacements. N1 is reported separately as the design error.

**Coverage.**
* Every certified rung checks the base cover of R: 144 boxes, plus adaptive refinement to up to about 4700 boxes.
* Each inequality is checked in every x-region (p+m-strip) that a box meets.
* The (i′) checkers ran 3 s-rungs × 2 functionals per degree.
* The quarantine static scan (final run) finds 0 findings in this stream's 9 files, with overall verdict PASS; the scan's own negative control is detected.

## 7. Runtimes

Setup: one core, `nice`, with at most 2 concurrent processes. Wall time is about equal to CPU time; the Python
processes ran at ≈ 96% CPU. The figures below are the `seconds.total` fields per rung.

Point drift, PW family, full chain:
* The chain is S1–S3, 8 residual enclosures, the one-sided T_N check, and 6 (i′) checks.
* d = 4: 37–128 s. d = 6: 115–424 s. d = 8: 363–1064 s.
* The whole ladder takes about 8.5–30 min per drift, and every single rung stays under about 18 min: 515 s at e = 3, 1282 s at e = 1, 1486–1562 s at e = 1/4 and 1/2, and 1775 s at e = 0 (rungs of 207, 602 and 966 s).
* Block [1/2, 17/32], PW_4, D11 light settings: 246 s. The declared-rule attempt was stopped at 24 min.
* The plain P_d baseline (c1b_certify.py) took 53 s at d = 6 and 388–407 s at d = 12.

Cost structure:
* About 40–55% of the time goes to the six (i′) quadratic checks. They refine to about 2000–3000 boxes at d = 8,
  because λ is chosen with only 1/16 safety.
* Candidate generation (untrusted float LS) takes 4–18 s.

## 8. Freeze binding, readiness and gates

**What a future FROZEN certification on a pre-registered block would have to bind.** Any such block would be decided
and frozen by the user under a floor extension. This stream proposes none and evaluated none.
1. **Code.** SHA-256 of `c1b_gauss.py`, `c1b_kernel.py`, `c1b_pw.py` and `c1b_certpw.py` (the load-bearing set).
   `c1b_float.py` is pinned for reproducibility of the candidates only. The current prefixes are 3189208d…, dfdc871b…,
   db51847c…, 0e1465d5… and 2a14067c…; they must be re-pinned at freeze.
   * Provenance note: the PW runs at e = 1/4 and 1/2 were produced by an earlier revision of `c1b_certpw.py`, before
     the D9 flag, the `C_T_float` field and block support were added. The mathematics is identical, and the PW9 runs
     at e = 1/2 reproduce the d = 4 and d = 6 values.
2. **Family.** PW_d on the strips t = p+m ∈ [0,1], (1,2], (2,3], (3,5], in the D3 Chebyshev basis, with a declared
   degree ladder. For blocks, it must also say whether candidates are e-free (the U1 form used here) or e-affine
   (not implemented; see §4b).
3. **Candidate generation.** The declared sample set, LS collocation, and 2^-200 dyadic rounding. The candidate is
   not trusted.
4. **Scaling rules.**
   * Supersolutions: η = −r_lo/(1+r_lo), rounded up to 2^-20.
   * Explicit certificates: λ = the dyadic 2^-20 ceiling of (17/16)·max(0, B²/(4A_lo) − C0_lo)/V_lo, plus 2^-20.
   * s ∈ {2^-6, 2^-4, 2^-2}.
   * c is the 2^-10 rounding of √(b̃2(a)/b̃0(a)).
   * g₂ is the 2^-40 ceiling of 1/(2c).
5. **Arithmetic.**
   * Exact rationals, with G-form coefficients as integers at 2^-480 (exactness asserted).
   * φ and Φ on the 2^-160 grid.
   * Taylor order 10.
   * Cover: h = 1/4, adaptive tolerance 5/4, 4 extra levels.
6. **Block list.** Pre-registered blocks (e_lo, e_hi), dyadic endpoints, and the statement type (block-uniform).
7. **Acceptance rule.**
   * Every checker passes on its full cover in every x-region.
   * Constants are ladder minima over the certified rungs.
   * RLR is assembled by LR-3 in the termwise-min form, then combined componentwise with Dv′ r2 and Lemma G.
   * A block that fails is reported as NOT_CERTIFIED. There is no retuning after any evaluation.
8. **Consumer.** None tonight. Under floor r2 the route is **CLOSURE-ONLY**, so it can be consumed only after a
   user-decided floor extension is frozen before any evaluation.

**Kill gates.**

| gate | result |
|---|---|
| G1 prospective motivation | **PASS.** The route is C1a's theorem LR-3. The Monte Carlo results give independent evidence of its mechanism: the score resets at each return to the atom, so ρ is an excursion-average and not a worst case. Nothing was chosen by reference to a target sign. The PW family (D8) was chosen from a structural kink diagnosis. |
| G2 mathematical validity | **PASS, self-checked.** <br>• S1 and S2: Lemma T and its whole-kernel analogue, with w ≥ 0 checked. <br>• Tame chains: Ĝ ≥ 0, with ‖Ĝ‖ ≤ C_T and (Ĝg)(a) ≤ τ‖g‖. <br>• Subsolutions: K̂^n → 0 by Lemma T. <br>• (i′) certificates: Lemma C0(ii). The w are quadratic in μ with bounded polynomial coefficients, so Lemma TL(d) applies. <br>• L1 forcing: c/2 + g₂μ² ≥ \|μ\| holds because 2c·g₂ ≥ 1 is asserted. <br>• Discontinuous PW candidates are allowed. K̂w is continuous in x, both adjacent region forms are checked on boundary lines, and images on strip lines are null sets. <br>• Not independently reviewed. |
| G3 scope explicit | **PASS.** Pointwise at e ∈ {0, 1/4, 1/2, 1, 3}, plus one block [1/2, 17/32] (§4b). The reachable set R is the C11 specification. The κ are the Lemma K constants. |
| G4 reproducible | **PASS.** Every JSON is regenerated by its CLI (`c1b_certpw.py point E DEG… --tight-ct`, `block LO HI DEG…`, `c1b_negctl.py`, `c1b_mc.py`, `c1b_report.py PW PW9`). The logs are in `logs/`. |
| G5 non-target validation | **PASS.** Everything is CERTIFIED at 5 point drifts and consistent with MC at every drift where MC ran. All replacement negative controls are detected. |
| G6 independent check | **PARTIAL.** The internal independent paths are: <br>• exact closed form versus split Gauss–Legendre quadrature (4e-16); <br>• own φ/Φ versus c7_gaussian; <br>• integer versus Fraction Taylor models; <br>• Sherman–Morrison Λ = τ_a/D, from float and from MC renewal; <br>• the MC bracket checks; <br>• the block-path spot check. <br>There is no independent reviewer and no second implementation (same author). |
| G7 temporal integrity | **PASS.** D0–D10 were each declared in PROGRESS.md before their runs. The amendments D7–D10 are recorded with their reasons: the one-sided certificates after the d = 6 test, the PW family after the P_d stagnation, the C_T fairness rule, and the replacement of the N1 design error. The failures are preserved. |
| G8 no target leakage | **PASS.** Every drift passes `guard_drift` and none is in or near [1.2, 2.6]. No cell id is used. There are 0 scan findings in this stream. The ledger entries are all NONTARGET_DRIFT_VALIDATION with cells_touched = []. No tail number is read or juxtaposed. No Theorem-M transfer is made. |
| G9 could be frozen prospectively | **YES in principle** (binding list above). It is not yet frozen-grade; see the readiness verdict. |
| G10 real improvement | **YES, structurally, at the declared drifts.** ρ1 is 2.0–5.2× and ρ2 5.6–21.7× below Dv′'s κ-terms, from the same certified inputs. At the constant level this is A1 1.9–3.2× and A2 3.0–7.1× at the 5 point drifts, and A1 2.17× and A2 3.49× block-uniformly on [1/2, 17/32]. |

**Readiness verdict.** The route is **VALIDATED_NON_TARGET**. It is **not FREEZE_READY**, for four reasons:
1. G6 is only partial. There is no independent review or second implementation of the CUSUM certifier, and C1a's
   theory is also self-checked only.
2. The block candidate family is undecided. The e-free block works at a cost of about 1.5–2.5×, and e-affine
   candidates are not implemented. The block cost per unit width is also not yet characterised; there is one block only.
3. The D1 and D2 two-sided chains are the loosest inputs. They affect RLR and Dv′ alike.
4. The per-state c(x) and quartic (ii-b) refinements of THEOREM_LR are not implemented. The CS and triangle losses of
   §5 are the largest remaining RLR slack.

None of these needs target information. All could be resolved on non-target drifts before any freeze. Governance:
**CLOSURE-ONLY under floor r2**.

## 9. Files

* **Code:** `c1b_gauss.py`, `c1b_kernel.py`, `c1b_pw.py`, `c1b_certpw.py`, `c1b_certify.py`, `c1b_float.py`,
  `c1b_negctl.py`, `c1b_mc.py`, `c1b_report.py`.
* **Log:** `PROGRESS.md`, with the declarations D0–D11, including the reason for every amendment.
* **Run logs:** `logs/`.
* **Results:** `NS/validation/` holds
  * `C1B_POINT_e1_2.json` and `C1B_POINT_e1_4.json`: the plain P_d baseline;
  * `C1B_PW_POINT_e1_2.json` and `C1B_PW_POINT_e1_4.json`;
  * `C1B_PW9_POINT_e{0,1_2,1,3}.json`;
  * `C1B_PW9_BLOCK_1_2__17_32.json`;
  * `C1B_NEGCTL.json`;
  * `C1B_MC.json` (NON-CERTIFIED);
  * `C1B_SUMMARY_PW_PW9.json` (the aggregate, including the MC consistency checks and the float-C_T fairness check).
* **Ledger:** 22 entries in `ledger/ZERO_TARGET_LEDGER.jsonl`. All are NONTARGET_DRIFT_VALIDATION, with
  cells_touched = [] and no LEAK_FLAG. One of them is a retroactive entry for the scratchpad test scripts.
