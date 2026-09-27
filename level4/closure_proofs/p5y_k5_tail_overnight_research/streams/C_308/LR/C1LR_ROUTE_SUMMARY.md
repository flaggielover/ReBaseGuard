# C1LR route summary — likelihood-ratio / score representation of the atom constants (stream C1a)

Scope: theory plus exact synthetic validation only.
* No CUSUM quantity was computed and no cell was evaluated.
* No drift in [1.2, 2.6] or its mirror was used.
* The next stream does the CUSUM certification.
* **Nothing here is FREEZE_READY.**

Files:
* `THEOREM_LR.md` holds the theory: §0–§6, §cert and §7.
* `lr_fsm.py` is the producer.
* `NS/validation/C1LR_FSM_VALIDATION.json`, `C1LR_EXAMPLES.json` and `C1LR_BLOCK.json` hold the results.
* `PROGRESS.md` is the log. It holds the declared rules, each written before its run.

## 1. Route items and states

The certificate items are labelled CT0–CT4. These are this stream's own labels and have no relation to any historical
campaign name.


| id | item | state | where |
|---|---|---|---|
| LR-1 | Score identity: ∂(Rf)(a) = E_a[Σ_{n<τ} f(X_n)M_n], and ∂²(Rf)(a) = E_a[Σ f(X_n)(M_n²+N_n)] for general driven killed chains | proved; VALIDATED_NON_TARGET (exact on 24 seeds) | THEOREM_LR §1; `identity_checks` |
| TL | Geometric tail lemma from a supersolution: moments of τ and M, and vanishing of polynomial-growth terms | proved | §2 |
| LR-2 | A0 = Λ exactly; A1 ≤ A1^LR; A2 ≤ A2^LR | proved; validated | §4 |
| LR-4 | Chain true ≤ LR ≤ PM ≤ Lemma G, with a caveat on the score level | proved; VALIDATED_NON_TARGET (24/24 for A1 and for A2) | §5.1 |
| E1/E2 | Plain whole-kernel LR is **not** dominated by Dv′. Its order is Λ^{3/2}; Dv′'s is O(Λ) | proved in order (E1); rigorous lower bounds on toy chains (E2, E1d′) | §5.2; `C1LR_EXAMPLES.json` |
| LR-3 | **Regenerative LR (RLR)**: LR is applied inside the taboo excursion, and Dv′'s Sherman–Morrison quotient is kept. A1 = Ā_eff(ρ1+δ1) and A2 = Ā_eff(ρ2+2ρ1δ1+2δ1²+δ2). The exact ratios satisfy ρ1 ≤ κ1C_T and ρ2 ≤ 2κ1²C_T²+κ2C_T, so RLR dominates Dv′ when both use the same inputs | proved; VALIDATED_NON_TARGET | §5.3; `rlr_and_dv` |
| CT0/CT1 | Comparison lemma, and the δ-certificate. The δ-certificate reduces to two linear supersolution inequalities, (C1-b) and (C1-a) | proved; implemented; checker has negative controls | §cert (i) |
| CT1′ | Full quadratic certificate with a linear term, using a global or a per-state c. Its exact value is √(ΛS2) for global c and Σ_y√(U0U2) for per-state c. At equal c it dominates the δ-form | proved; validated | §cert (i′) |
| CT2 | A2: the triangle bound S2 + T_N, and a per-state quartic Cauchy–Schwarz bound | proved; exact values validated. The quartic checker (for blocks) is **not implemented** | §cert (ii) |
| CT3 | Finite horizon: a per-(n,y) Cauchy–Schwarz head plus a certified tail | proved; validated | §cert (iii) |
| CT4 | Hölder lower bound on A1^LR, used as a validation handle | proved; used | §cert (iv) |
| U1 | Block uniformity via an e-free certificate, checked against interval enclosures | proved; demonstrated on fixtures (§3) | §6; `run_block*` |

**Overall route states**

| route | state | note |
|---|---|---|
| RLR (Theorem LR-3) | **VALIDATED_NON_TARGET** | The theory is complete. |
| plain LR | VALIDATED_NON_TARGET | Use it only as one more supply inside the componentwise minimum, never on its own. |

**Governance under floor r2.** Both routes are **CLOSURE-ONLY**, because they supply constants other than Lemma G and
Lemma Dv′ r2. RLR reuses Dv′'s inputs but adds the new ρ1 and ρ2. Adoption needs a floor extension that the user
decides and freezes before any evaluation.

## 2. Key results (all synthetic; every number is a field of the named JSON)

**Validation sets V1 and V2** (24 seeds, Λ ∈ [2.7, 8.4]):
* the identities are exact;
* the independent checks (finite differences and path enumeration) agree;
* the sign-flip negative controls are detected;
* every certificate passes the exact checker;
* all four planted non-supersolutions are rejected for each seed;
* the chain true ≤ LR_cert ≤ PM ≤ G holds 24/24 for A1 and for A2.

**A1 on V1** (`V1.summary.A1_ratios`):

| ratio | median | range |
|---|---|---|
| LR_lower / true | 1.99 | |
| LR_cert / true | 3.21 | |
| PM / true | 7.79 | |
| Dv′ (exact inputs) / true | 6.52 | |
| RLR / true | 2.26 | |
| Dv′ / RLR | 2.39 | 1.83–2.99 |

For A2 on V1, Dv′/RLR ranges over 1.44–3.09.

**Negative results (preserved).**
1. **The exact LR is still about 2× above the true functional norm** (median). The rigorous lower bound shows this.
   * About half of the gap between the true value and PM is cancellation *between paths* that end in the same state.
     No bound built on |M_n| can recover it.
   * LR captures only the *within-path* cancellation: PM/LR_cert ≈ 1.5–2.4.
2. **Plain LR loses to Dv′ at large Λ.**
   * In E2 the LR lower bound is ≈ 0.40Λ^{3/2}, while Dv′ ≈ 1.07Λ. The ratio grows to 4.69 at Λ = 160.
   * In E1d′ the ratio reaches 5.10.
   * RLR removes this, because M resets at each return to the atom.
3. **The δ-certificate (b1 = 0) is 1.7–3.3× worse than the full or per-state quadratic** on the fixtures.
4. **Two design errors of mine, both preserved and explained:**
   * E1d as declared could not separate, because its δ1 grows like Λ. E1d′ was declared before it was run.
   * The block "slack = 0" negative control was not guaranteed invalid. It passed legitimately in 2 of 64 variants. It
     was replaced by a guaranteed-invalid control (scaled below the LR lower bound), which was rejected 8/8.
5. **Block overhead.** The baseline envelope certificate is 1.55–3.43× the pointwise one (§3).

## 3. Block uniformity (C1LR_BLOCK.json)

The block is [0, 1/4] on V1 seeds 1..8. Each certificate is a single e-free w, checked on m sub-intervals with exact
interval-Horner enclosures (`check_block_cert`).

* **Baseline (η = 1/100, m = 8).**
  * All 8 pass.
  * The overhead over the largest pointwise certificate on the grid e = k/32 is 1.55–3.43×.
  * For seed 1, block LR exceeded block PM.
* **Declared variants (η ∈ {1/100, 1/10, 1/2, 2} × m ∈ {8, 32}).**
  * All 64 pass the checker.
  * The best variant is m = 32 with η = 1/10 on 7 of 8 seeds.
  * Its overhead is 1.44–1.94×, and the chain block LR ≤ block PM ≤ block G holds 8/8.
  * The Λ envelope inflation (K_up versus the largest Λ on the grid) is 1.05–1.10×.
* **Checks.** LB(e) ≤ block bound holds on every grid point, and the guaranteed-invalid scaled certificate is rejected
  8/8.
* **Lesson for CUSUM.** Most of the block overhead comes from the discriminant slack. The δ-certificate's A-margin
  trades against B's variation across the block, so the CUSUM stream should tune η with a declared grid and use fine
  sub-blocks.

## 4. Gates

| gate | result |
|---|---|
| G1 prospective motivation | **PASS.** The motivation comes from the synthetic probe (sign cancellation) and from the kernel structure (e-free window, Gaussian score). Nothing depends on the sign of a target. |
| G2 mathematical validity | **PASS**, self-checked. The proofs are in THEOREM_LR. The exact fixture identities support LR-1 and LR-3; the regenerative quotient identities are exact. There has been no independent review yet. |
| G3 scope explicit | **PASS.** The scope is (H1)–(H3), the e-free survival set, the score level, and the block form. The caveat about noise-level versus state-level scores is stated. |
| G4 reproducible implementation | **PASS for the finite-state case.** `lr_fsm.py` regenerates every JSON (flags `--sets`, `--examples`, `--example-e1dp`, `--block`, `--block-variants`, `--block-negctl`). **There is no CUSUM implementation.** |
| G5 non-target validation | **PASS, synthetic only**: 24 seeds, 3 toy ladders and 8 block seeds. |
| G6 independent check | **PARTIAL.** There are internal independent code paths: finite differences, path enumeration, matrix-product identities, and closed-form versus solved certificates. There is no independent reviewer and no second implementation. |
| G7 temporal integrity | **PASS.** Every rule was declared in PROGRESS.md before its run. No target was evaluated. |
| G8 no target leakage | **PASS.** No CUSUM computation was done. The only drifts used are {0, k/32 ≤ 1/4} on synthetic fixtures. The quarantine scan shows no finding in this stream; the one finding it reports is in another stream's file. There are 6 ledger entries (one per flag run), none flagged. |
| G9 could be frozen prospectively | **YES, in principle.** The constant formulas (LR-3) and the certificate checker are fixed objects. Freezing needs the CUSUM certifier and a floor extension. |
| G10 real improvement | **RLR: YES, structurally.** It replaces the worst-case κ1·C_T by an excursion-average LR constant from the atom, and it provably never loses to Dv′. **Plain LR:** it improves only on Lemma G. |

## 5. What the CUSUM certification stream must implement

1. **Taboo moment kernels.**
   * Compute K̂_e^{(j)} b for j = 0, 1, 2 on grid functions b(p, m), with weights 1, S and S².
   * Here S = −(z+e) ~ N(0,1), integrated over the window that neither alarms nor hits the atom.
   * These are Gaussian moments of order ≤ 2, over the same cells as the existing kernel_apply.
   * T is injective off the atom window, so the noise-level and state-level excursion scores coincide. No
     Rao–Blackwell issue arises inside RLR.
2. **Excursion certificate for L1** (per-state full quadratic, §cert (i′)). Solve, in order:
   * b2 ≥ 1/(2c(x)) + K̂b2;
   * b1 = Ĝ(2K̂^{(1)}b2);
   * a ≥ c/2 + K̂a + K̂^{(1)}b1 + K̂^{(2)}b2.

   Then check A ≥ 0, C ≥ 0 and B² ≤ 4AC in every state, with outward rounding. This gives L1 ≤ a(atom).
3. **Excursion certificate for L2.** Use the triangle bound Ŝ2 + E_a[σ(σ−1)/2] (N_n = −n). The quartic bound is
   optional.
4. **Block (§6).**
   * Use interval-drift enclosures: upper bounds for the nonnegative terms, two-sided bounds for the signed terms.
   * Tune η over a declared grid, with fine sub-blocks.
   * Set ρ_j = sup L_j / inf τ_a (τ_a ≥ 1), or use the non-ratio form.
   * Combine with Dv′'s own certified (Ā, τ, D_lo, δ1, δ2).
   * Take the componentwise minimum with Dv′ and G.
5. **Non-target validation.**
   * Use only the drifts {0, 1/4, 1/2, 1, ≥ 3}.
   * Compare against exact finite truncations.
   * Include negative controls: a flipped score, and a planted certificate scaled below a rigorous lower bound.

## 6. Cost expectation (not measured on CUSUM)

* **Per point.** About 3 Lemma-T-type solves on the 2-D state, plus about 3 moment-kernel applications. That is O(1)×
  the existing taboo supersolution. L2 by the triangle bound adds about 2 solves.
* **Per block.** The same work with interval-drift kernels, as I1/I2 already do for K_e. Expect a 1.4–2× block
  overhead, on the synthetic evidence, unless η and the sub-blocks are tuned.
* **Fixtures.** About 1–10 s per seed in exact rationals (n ≤ 9).

## 7. Rule S8 compliance (checked after the coordinator's notice)

I grepped every C1a file: this summary, THEOREM_LR.md, PROGRESS.md and lr_fsm.py. None of them contains:
* a committed tail-cell constant, share, factor or margin;
* a C3 knockout value, a C8 x-eff factor or an E10 diagnostic;
* any product of a route gain with such a quantity.

Every ratio in this stream is synthetic or taken from a toy chain, and is stated only against other synthetic
quantities. The asymptotic orders in THEOREM_LR §5.2 are stated without tail numbers.

One change was made for S8: the certificate items were renamed from C0–C4 to CT0–CT4, so they cannot be read as the
historical "C3". No other correction was needed.
