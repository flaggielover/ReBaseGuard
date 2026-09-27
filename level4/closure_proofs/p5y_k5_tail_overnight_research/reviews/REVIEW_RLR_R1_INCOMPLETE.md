# REVIEW_RLR_R1 — independent adversarial review of the RLR atom-constant route

> **INCOMPLETE — NOT A VERDICT.** The reviewer agent stalled twice (600 s watchdog) before writing sections 2–7 and
> the verdict. Preserved as written by the coordinator (renamed from REVIEW_RLR_R1.md). The completing review is
> `REVIEW_RLR_R2.md`.


Status: IN PROGRESS (skeleton). Verdict line will be added at the end.

## 0. Scope and quarantine statement

Reviewer: independent adversarial reviewer (wrote none of the reviewed material), 2026-09-28.

Files reviewed, with SHA-256 prefixes at review time:

| file | sha256 prefix |
|---|---|
| `streams/C_308/LR/THEOREM_LR.md` | 59cd350ca201 |
| `streams/C_308/LR/lr_fsm.py` | 4965bd775ab9 |
| `streams/C_308/LR/cusum/c1b_gauss.py` | 3189208d6c4c |
| `streams/C_308/LR/cusum/c1b_kernel.py` | dfdc871b18ff |
| `streams/C_308/LR/cusum/c1b_pw.py` | db51847c5b56 |
| `streams/C_308/LR/cusum/c1b_certpw.py` | c506907858a3 |
| `streams/C_308/LR/cusum/c1b_float.py` | 2a14067cd0c6 |
| `streams/C_308/LR/cusum/c1b_negctl.py` | aae8d3b4c7eb |
| `streams/C_308/LR/cusum/c1b_report.py` | 4d3142974b00 |
| `streams/C_308/LR/cusum/C1B_ROUTE_SUMMARY.md` | 6ed252f98eb1 |

Also reviewed: `validation/C1LR_*.json` and `validation/C1B_*.json`. The background theorems used are THEOREM_AD
(Lemmas K, T, SM, Dv, Dv′) and the TC-T consumer (THEOREM_TCT.md:41 and :125).

Quarantine compliance of this review:
* **Drifts.** Every computation of mine is at a declared drift: e ∈ {0, 1/4, 1/2, 1, 3}, plus the author's declared
  block [1/2, 17/32]. `Q.guard_drift` is called at every entry point.
* **No tail quantities.** No cell id is used. No 305–309 quantity is computed, read into code, or quoted. No value or
  ratio here is placed next to a tail number (S8, R2.1).
* **Latent proxies (R2.3).** The C1B artefacts carry validation-drift Λ, τ and C_T values. This review therefore
  reports **pass/fail flags and dimensionless certificate-to-truth slack ratios only**, never those values.
* **Imports.** No historical module was imported. The only campaign modules imported are this route's own `c1b_*`
  code under test and `NS/code/ov_quarantine.py`.
* **Writes.** No git writes, no remote hosts. `Q.LEDGER` is redirected to `SCR/review_RLR/REVIEW_LEDGER.jsonl`.
* **Where the scripts are.** All reviewer scripts, outputs and a PROGRESS log are in `SCR/review_RLR/`. The
  declarations RD1–RD5 were written in `SCR/review_RLR/PROGRESS.md` before the corresponding runs.

## 1. Mathematics

### 1.1 LR-1 identity (THEOREM_LR.md:53–91): **VALID**

* **Window independent of e.** The noise-level standing form needs e-free survival sets. For CUSUM the alive window
  [m−C, C−p] and the atom window [m−K, K−p] are sets of the increment z. The e-dependence sits only in the density
  φ(z+e) (Lemma K), so K′ has weight S = −(z+e) on an e-free set, with no boundary terms. The taboo survival set
  Â(x) = A(x) \ {T(x,z) = a} is likewise e-free, so LR-1 applies to K̂ verbatim.
* **Stopping-time measurability.** {n < τ} = ∩_{k≤n}{Z_k ∈ A(X_{k−1})} ∈ σ(Z_1..Z_n), and the same holds for σ in the
  taboo chain.
* **Differentiation under the expectation.** It is correctly avoided:
  * ∂R = RK′R is the operator-norm resolvent derivative (Lemma K gives C² in operator norm);
  * the Neumann expansion is then read path-wise term by term (:66–76);
  * absolute convergence comes from the majorant identities and Lemma TL(a)–(c).
* **Algebra.** I re-derived Lemma TL (:94–114): KW ≤ θW needs W ≤ C_W, and the per-step bound
  P(τ>k−1)·m_p·sup_y P_y(τ>n−k) is right. Lemma C0(ii) (:287) is legitimately fed by TL(d), because the certificates
  are quadratic in μ with coefficients bounded on the compact reachable set.
* **Independent exact confirmation.** The FSM identities are exact rational vector equalities (`identity_counts`
  24/24 in C1LR_FSM_VALIDATION.json).

### 1.2 Regenerative decomposition and exactly what RLR bounds: **VALID**

Lemma SM(c) gives (R_e f)(a) = ν_e(f)/D_e for every e. The consumer needs |(∂^j R_e f)(a)| ≤ A_j‖f‖ uniformly on
the drift block; this is the atom functional norm, used exactly once in TC-T (THEOREM_TCT.md:41). RLR bounds exactly
this, through the quotient rule:
(ν/D)′ = ν′/D − νD′/D² and (ν/D)″ = ν″/D − 2ν′D′/D² + ν(2D′²/D³ − D″/D²).

**All five terms are present** (THEOREM_LR.md:244–248; code `c1b_certpw.assemble`). Each is bounded in absolute
value, so the signs are immaterial. With Λ = τ_a/D ≤ Ā_eff:

| term | bound |
|---|---|
| \|ν′/D\| | ≤ L1/D ≤ min(Ā_eff ρ1, L1_up/D_lo) = q1 |
| \|ν″/D\| | ≤ q2 |
| \|2ν′D′/D²\| | ≤ 2 q1 δ1 |
| \|ν\|(2D′²/D³ + \|D″\|/D²) | ≤ Ā_eff(2δ1² + δ2) |

I verified line by line that this is `assemble` (c1b_certpw.py: A1 = q1 + A_eff·d1, A2 = q2 + 2q1d1 +
A_eff(2d1² + d2)).

**The k_{a,e}′ cancellation.** D is certified as D = (Ĝh1)(a), not as 1 − (Ĝk_a)(a). These are equal by
Ĝ(I−K̂)1 = 1 and K̂1 + k_a + h1 = 1. So D′ = (ĜK̂′Ĝh1)(a) + (Ĝh1′)(a), and k_a′ never appears explicitly. It is
absorbed in h1′ = −k_a′ − K̂′1. I checked that the two forms agree algebraically. The d-chain is:

    d1 = Ĝ(K̂^(1)d0 + h1′),   d2 = Ĝ((K̂^(2) − K̂)d0 + 2K̂^(1)d1 + h1″)

This matches ∂ and ∂² of Ĝh1 (c1b_certpw.residual_forms). h1′ = −φ(l1) + φ(l4) and h1″ = l1φ(l1) − l4φ(l4)
(c1b_kernel.py H1P, H1PP) are correct. The FSM regenerative identities for ∂R and ∂²R are exact equalities in
`rlr_and_dv` (lr_fsm.py:447–506), which is an exact check of the quotient-rule expansion.

**Uniform on a block.** Yes, provided each input is a uniform bound, which the implementation provides:
* τ ≥ sup τ_a and C_T ≥ sup ‖Ĝ‖, from one e-free w_T;
* Ā ≥ sup Λ, from one e-free W;
* τ_a,lo ≤ inf τ_a (subsolution);
* D_lo = max(tame, τ_a,lo/Ā);
* D1 and D2 from residuals enclosed over R × E;
* L1 and L2 from e-free (i′)/tame certificates;
* ρ_j = sup L_j / inf τ_a, which is ≥ sup(L_j/τ_a).

I re-derived every tame-chain bound in `certify_degree`:
* the E0n, E1n, E2 error propagation with ‖K̂^(1)‖ ≤ κ1, ‖K̂^(2)‖ ≤ 1 and ‖K̂″‖ ≤ κ2;
* τ_a,lo and τ_a,up;
* Λ_lo;
* the one-sided T_N certificate (no positivity needed, since K̂^N → 0).

All are valid.

### 1.3 LR-3 dominance over Dv′ on equal inputs: **PROVED for exact ρ; trivially for the min form; NOT a theorem for certified ρ**

For exact excursion ratios the chain is L1 = E_a Σ_{n<σ}|M_n| ≤ (Ĝ|K̂′|Ĝ1)(a) ≤ C_T‖|K̂′|‖τ_a.
* Ĝ1 ≤ C_T pointwise.
* ‖|K̂′|‖ = sup_x ∫_Â |S|φ ≤ E|S| = κ1.
* T(x,·) is injective on Â(x), so the noise and state norms coincide (THEOREM_LR.md:252 is right).

Likewise L2 ≤ τ_a(κ2C_T + 2κ1²C_T²). Hence ρ1 ≤ κ1C_T and ρ2 ≤ 2κ1²C_T² + κ2C_T. The A2 cross term 2ρ1δ1 ≤ 2κ1C_Tδ1
is dominated as well, so A^RLR ≤ A^Dv′ componentwise for the same (Ā_eff, δ1, δ2). This is the Dv′ r2 form of
THEOREM_AD.md:85, checked against the code.

**The certified implementation does not use exact ρ.** It uses the Cauchy–Schwarz / (i′) bound for L1 and the
triangle bound Ŝ2 + T_N for L2. Neither is guaranteed below κ1C_T or the Dv′ ρ2 in general. The theorem text covers
this correctly with "ρ_j := min(certified ρ_j, Dv′ factor)" (:241), but `assemble` does not take that min: it reports
raw RLR. The acceptance rule of the route summary (§8.7) does combine componentwise with Dv′ r2 and Lemma G. The
observed RLR < Dv′ at all 5 drifts and on the block is therefore an **empirical fact at those drifts**, not a
consequence of LR-3 (see N3).

### 1.4 Plain LR vs Dv′ (§5.2): **VALID as stated**

* **Example E1.** I re-derived it:
  * Dv′ and state-level LR are exact (Λ²φ(h));
  * noise-level LR ≥ (σ_h/2)Σπ^n√n − μ_hπ/(1−π)²;
  * μ_hπ/(1−π)² equals A1_true exactly, so the text's "A1_true/Φ(h)" is a valid weakening;
  * the Hölder step EY⁴ ≤ 3n²σ⁴ + nE(ξ−μ)⁴ is right.

  This is a correct proof that plain noise-level LR can be unboundedly worse than Dv′. It is also why only the
  regenerative form RLR is certified on CUSUM.
* **Other material.** The E2 and heuristic-order statements are explicitly labelled HEURISTIC or numerical, and no
  bound uses them.
* **Rao–Blackwell remark (:86).** Correct. Given the whole X-path, Z_k depends only on (X_{k−1}, X_k).

### 1.5 Quadratic certificates (i′) and box-wise checking: **SOUND**

* **Expansion.** ∫w(T, μ+s)q = Ka + μKb1 + K^(1)b1 + μ²Kb2 + 2μK^(1)b2 + K^(2)b2 (:313–318). With forcing
  g0 + g2μ², the quadratic's coefficients A, B, C are exactly the `quad_check` forms.
* **L1 forcing.** c/2 + g2μ² ≥ |μ| needs 2c·g2 ≥ 1, which is asserted in code.
* **Box-wise logic is sound.**
  * On a box, A ≥ alo > 0, C ≥ clo ≥ 0 and B² ≤ max(blo², bhi²) ≤ 4·alo·clo ≤ 4AC. So the quadratic is ≥ 0 for all
    μ at every (x, e) in the box.
  * Every point x lies in exactly one x-region J = ⌈p+m⌉ (`region_of_point`), and `regions_of_box` includes every J
    whose closed interval meets the box.
  * Each J-form is a globally defined analytic expression, so evaluating it on the whole box is a sound superset.
  * The strip-piecewise w(x) uses the strip containing [J−1, J], consistent with right-closed strips.
* **Discontinuous candidates across strip lines are handled correctly in code, but the stated reason is wrong (N1).**
  * The middle ("B") piece maps x with p+m = t > 1 onto the **whole segment p′+m′ = t−1**, which is a set of positive
    kernel mass, not a null set.
  * So K̂w is *discontinuous* in x across t ∈ {2, 3, 4} whenever w jumps across t′ ∈ {1, 2, 3}. This contradicts
    C1B_ROUTE_SUMMARY.md:269 ("K̂w is continuous in x … images on strip lines are null sets").
  * The code is nevertheless right. `kernel_gf_pw` (c1b_pw.py:47–72) splits the x-regions exactly at t = J−1, and it
    assigns the B-image to the strip σ ⊇ [J−2, J−1] with the same right-closed ownership. At x on t = 2 it therefore
    uses P_1 on the image line t′ = 1, which is the true value.
  * My independent quadrature (RD1, §3.1) confirms this on the exact lines, and my wrong-convention control
    detects the alternative ownership (deviation 0.40).

### 1.6 §6 block uniformity: **VALID**

The U1 argument holds: one e-free w satisfying the kernel-affine inequality for each e in E yields V_e ≤ w for
each e. The two-sided enclosure of B over (x, e) is what `quad_check` does. The (i′) form with b1 ≠ 0 over a block
is therefore sound as implemented, even though THEOREM_LR.md:268–271 recommends the δ-form.

## 2. Implementation vs theory

I read all load-bearing code line by line. What I checked, with the result:

* **Geometry of the pieces (c1b_kernel.py:1–30, 171–209).** Let u = z+e, α_p = p−K−e, α_m = m−K+e and
  l1..l4 = C−p+e, K−p+e, m−K+e, m−C+e.
  * Region II (t ≥ 1): A is [l4, l2] → (0, α_m−u); B is [l2, l3] → (α_p+u, α_m−u); C is [l3, l1] → (α_p+u, 0).
  * Region I (t ≤ 1): A is [l4, l3]; C is [l2, l1]; the atom window [l3, l2] appears only in the whole kernel, with
    P_1(0,0).
  * These are the correct CUSUM pieces.
* **Score-weighted Gaussian moments with S = −(z+e) = −u.** `_ucoef` expands w(T) in powers of u with the binomial
  signs (−1)^t for m′ = α_m − u, then multiplies by (−u)^j (`nn = n + j`, factor (−1)^j).
  * The antiderivative is ∫u^nφ = G_n(A)φ(A) − G_n(B)φ(B) + (n−1)!!(Φ(B)−Φ(A)), with G_n = t^{n−1} + (n−1)G_{n−2}.
    Correct.
  * The author's N2 control (finite differences in e of the exact kernel against K^(1) and K^(2) − K̂, with the proved
    Taylor bound) independently fixes the sign through the code under test.
* **Kinks at p+m ∈ {1,…,4} and strip splits (c1b_pw.py:47–72).**
  * The J=1 A/C pieces are split at l3 − b and l2 + b (images m′ = b, p′ = b).
  * For J ≥ 2 the pieces start in strip σ ⊇ [J−2, J−1], then run over the full upper strips.
  * The x-regions J = ⌈t⌉ absorb the kink of the B-image line. The t = 4 kink is not split because strip 4 is (3, 5];
    this is a matter of efficiency only.
  * Verified independently in RD1 (§3.1).
* **Exact arithmetic and outward rounding (c1b_gauss.py, c1b_kernel.py:500–690).**
  * **exp.** Partial sums use floor and ceil directed integer rounding, with the tail bound t_N·q/(1−q), q = y/(N+1).
  * **φ.** φ = exp(−t²/2)·[1/√(2π)], with π from Machin bounds.
  * **Φ.** Φ(t) = 1/2 + φ(t)Σt^{2n+1}/(2n+1)!! (positive terms), with Φ(−t) = 1 − Φ(t).
  * **Derivative bound.** sup|φ^(n)| ≤ E|Y|^n/√(2π), by Fourier inversion. Correct.
  * **Taylor models.** The integer Taylor model scales Ps, T and coefs consistently: Ps at 2^{SC+kd·dmax}, T at
    fKT·2^{kd·KT}, φ/Φ intervals at 2^GP, and Z = fKT·2^{SC+kd·dmax+kd·KT+GP}.
  * **Remainders.** The Lagrange remainders use Pb·sup|φ^{(KT+1)}|ρ^{KT+1}/(KT+1)! for φ, and sup|φ^{(KT)}| for Φ.
    The range of the polynomial part is |c0| ± Σ|c_α|r^α with interval coefficients.
  * **Conclusion.** No rounding-direction error found.
* **Certificates and checkers (c1b_certpw.py).**
  * `check_supersolution` re-encloses the residual of the *scaled* function directly; η only chooses the candidate.
  * `quad_check` re-encloses A, B and C directly; λ, s and c only choose the candidate.
  * The soundness of every certified number therefore rests on the enclosures and the forms, not on the scaling
    heuristics.
* **Dv′ recomputation "from the same certified inputs".** `assemble` uses the same A_eff, C_T, δ1 and δ2, and it
  matches THEOREM_AD Lemma Dv′ r2 (AD.md:85) term by term, with κ1 = 0.7978845609 ≥ √(2/π) and κ2 = 4·φ(1)_hi.
  * I recomputed every point and block constant from the exact rationals in the JSONs with my own formula code
    (RD5, `SCR/review_RLR/rv_assemble.py`).
  * I also recomputed the ladder minima from the per-rung records. All outputs match **exactly** at all 5 drifts and
    on the block.
  * Mixing rungs in the ladder minima is sound, because each field is an independent valid bound on the same true
    quantity.
* **Float side (c1b_float.py, c1b_pw.solve_chain_pw).** It only proposes candidates. The exact side never trusts it.

## 3. Attacks (planted invalid certificates, dense sampling, independent float check)
(pending)

## 4. Controls and coverage
(pending)

## 5. Claims vs evidence; route state; freeze binding
(pending)

## 6. Blockers and notes
(pending)

## 7. Verdict
(pending)
