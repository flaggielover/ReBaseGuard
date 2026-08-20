# 02 — Theorem / Claim Map

Every important Level 1–3 claim, with its formal name, evidence label, source
file and dependencies. Evidence labels follow the strict definitions in
`06_CLAIM_LEDGER.md`.

**Namespace.** All Lean names below live in `RebaseguardLean` unless shown
otherwise. Paths are relative to `/Users/suzhe/ReBaseGuard`.

**The single most important separation in this document:**

> The **Lean analytic identity** (§A, `T-14`) and the **numerical
> certification of `Γ_CUSUM`** (§C, `N-03`) are disjoint bodies of evidence.
> Lean says nothing about the value of `Γ`. The Arb certificate says nothing
> about differentiation under the expectation. They meet only in the human
> theorem `C-F1`, which consumes both.

---

## A. The Lean machine-checked chain

| Claim ID | Scientific statement | Formal name | Evidence | Source file | Assumptions | Depends on | Status |
|---|---|---|---|---|---|---|---|
| `T-01` | The exponent `x ↦ −xT − (x²/2)τ` is differentiable with derivative `−T − eτ` | `stoppedExponent_hasDerivAt` | MACHINE-CHECKED | `rebaseguard-lean/RebaseguardLean/StoppedLikelihood.lean:19` | none (real analysis) | — | PASS |
| `T-02` | **Stopped-likelihood pointwise derivative.** `d/de [Z·e^{−eT−(e²/2)τ}] = Z(−(T+eτ))e^{…}` | `stoppedIntegrand_hasDerivAt` | MACHINE-CHECKED | `StoppedLikelihood.lean:44` | none | `T-01` | PASS |
| `T-03` | **Differentiation under the integral at `e=0`**, given an integrable dominating function on `[−δ,δ]` | `hasDerivAt_integral_stoppedIntegrand_zero` | MACHINE-CHECKED | `IntegralBridge.lean:95` | `Zτ ∈ L¹`; `g` integrable dominating; `δ>0` | `T-02`, mathlib `hasDerivAt_integral_of_dominated_loc_of_deriv_le` | PASS |
| `T-04` | **Domination inequality** (deterministic): `‖Z(−(T+et))e^{−eT−e²t/2}‖ ≤ \|Z\|(\|T\|+δ\|t\|)e^{δ\|T\|+δ²\|t\|/2}` for `\|e\|≤δ` | `abs_stoppedIntegrandDeriv_le` | MACHINE-CHECKED | `Domination.lean:90` | `0 ≤ δ`, `\|e\| ≤ δ` | — | PASS |
| `T-05` | **The dominating function** satisfies Gate 3's `hdom` unconditionally (pointwise, not merely a.e.) | `explicitDominatingFunction`, `hdom_explicitDominatingFunction` | MACHINE-CHECKED | `Domination.lean:113,137` | `0 ≤ δ` | `T-04` | PASS |
| `T-06` | **Exponential-moment bridge**: the dominating function is integrable given a joint moment `\|Zτ\|e^{a\|Tτ\|+b\|τ\|}` | `integrable_explicitDominatingFunction_of_expMoment` | MACHINE-CHECKED | `Domination.lean:237` | `δ+c ≤ a`, `δ²/2+cδ ≤ b` | `T-05` | PASS |
| `T-07` | **Split-moment form**: `Zτ ∈ L²` + separate exponential moments of `Tτ` and `τ` suffice | `hasDerivAt_integral_stoppedIntegrand_zero_of_separate_moments` | MACHINE-CHECKED | `Domination.lean:508` | `4a ≤ p`, `4b ≤ q` | `T-03`, `T-06` | PASS |
| `T-08` | **Two-sided CUSUM definition** and its measurability | `cusumPair`, `cusumMax`, `measurable_cusumPair`, `measurable_cusumMax` | MACHINE-CHECKED | `CUSUMBridge.lean` | `∀n, Measurable (X n)` | — | PASS |
| `T-09` | **Stopping-time result**: the alarm time is a genuine stopping time for the natural filtration | `isStoppingTime_cusumTau` | MACHINE-CHECKED | `CUSUMBridge.lean` | measurability of `X` | `T-08` | PASS |
| `T-10` | **Forcing result** (pathwise): one score above `h+k` forces an alarm by the next step | `cusumTau_le_of_lt`, `lt_cusumPair_fst_succ` | MACHINE-CHECKED | `CUSUMBridge.lean` | none (pathwise) | `T-08` | PASS |
| `T-11` | **Independence ⇒ geometric tail**: `μ(no forcing in k trials) ≤ q^k`; forcing is a.s. | `measure_noForcing_le_pow`, `measure_le_forcingNat_le_pow`, `measure_never_forced_eq_zero` | MACHINE-CHECKED | `CUSUMBridge.lean` | `iIndepFun X μ`, `μ{X_j ≤ H} ≤ q`, `q < 1` | — | PASS |
| `T-12` | **Forcing-time exponential moment** at any rate `b` with `e^b·r < 1` | `integrable_exp_forcingNat` | MACHINE-CHECKED | `CUSUMBridge.lean` | as `T-11` plus `exp b · r < 1` | `T-11`, `integrable_exp_of_geometric_tail` | PASS |
| `T-13` | **Stopped quantities** `Zτ, Tτ, τR` constructed from `X` and the real alarm time, with a.e. finite-index identification | `scoreAt`, `walkAt`, `cusumTauReal`, `ae_stopped_quantities_eq` | MACHINE-CHECKED | `StoppedQuantities.lean` | as `T-11` | `T-09`, `T-11` | PASS |
| `T-14a` | **Stopped-walk exponential moment** (conditional on scalar data `c·d<1`) | `integrable_exp_abs_walkAt_of_moment_tail` | MACHINE-CHECKED | `StoppedWalkMoment.lean:320` | one-step moment ≤ `c²`, `μ{X_j≤h+k} ≤ d²`, `c·d<1` | `T-13` | PASS |
| `T-14b` | **Gaussian small-rate existence**: `∃a>0` with `E e^{a\|Tτ\|} < ∞` | `exists_pos_integrable_exp_abs_walkAt_gaussian` / `…_rebaseguard` | MACHINE-CHECKED | `SmallMoment.lean:243,256` | `iIndepFun`, `μ.map (X j) = gaussianReal 0 1` | `T-14a` | PASS |
| `T-15` | **`scoreAt` moment result**: `Zτ ∈ L²`, via the same slice decomposition + `x² ≤ (4/a²)e^{a\|x\|}` | `integrable_sq_scoreAt_gaussian` | MACHINE-CHECKED | `ReBaseGuardIdentity.lean:279` | as `T-14b` | `T-13` | PASS |
| `T-16` | **`cusumTauReal` exponential moment** at some rate `>0` | `exists_pos_integrable_exp_abs_cusumTauReal_gaussian` | MACHINE-CHECKED | `ReBaseGuardIdentity.lean:308` | as `T-14b` | `T-12`, `T-13` | PASS |
| `T-17` | **Three Gate-4 moment inputs produced (not assumed)** at the actual detector | `rebaseguard_separate_moments` | MACHINE-CHECKED | `ReBaseGuardIdentity.lean:332` | as `T-14b` | `T-14b`, `T-15`, `T-16` | PASS |
| `T-18` | **Final actual-detector derivative identity, general `(k,h)`** | `hasDerivAt_integral_rebaseguard_gaussian` | MACHINE-CHECKED | `ReBaseGuardIdentity.lean:360` | as `T-14b` | `T-07`, `T-17` | PASS |
| **`T-19`** | **THE FINAL THEOREM.** For the frozen detector `k=1/2`, `h=5` driven by iid `N(0,1)` scores: `d/de E[Zτ·e^{−eTτ−(e²/2)τ}]\|₀ = −E[Zτ·Tτ]` | **`hasDerivAt_rebaseguard_cusum`** | **MACHINE-CHECKED** | `ReBaseGuardIdentity.lean:392` | `∀n, Measurable (X n)`; `iIndepFun X μ`; `μ.map (X j) = gaussianReal 0 1` | `T-18` | **PASS** |

## B. Human mathematics (not represented in the Lean chain)

| Claim ID | Scientific statement | Evidence | Source | Assumptions | Status |
|---|---|---|---|---|---|
| `C-REG` | Regularity: `k>0 ⇒ τ<∞` a.s. with finite exponential moments; all moments of `τ, T_τ, Z_τ` finite | PROVED (and its Lean-relevant half is `T-12`/`T-16`) | `rebaseguard_lemma_handoff.md` §1; Step-2 audit | `k>0` | PASS |
| `C-DEC` | Exact decomposition `E[Z_τT_τ] = E[Z_τ²] + E[Z_τT_{τ-1}]`; `E[Z_τ]=E[T_τ]=0` by reflection symmetry | PROVED | `rebaseguard_lemma_handoff.md` §2 | reflection symmetry of the two-arm detector | PASS |
| `C-M1` | `Z_tT_t − 1` is a martingale-difference sequence; `E[Σ_{t≤τ}Z_tT_t] = E[τ]` | PROVED | handoff §3 (M1) | optional stopping under `C-REG` | PASS |
| `C-M2` | **Wald's second identity** `E[T_τ²] = E[τ]` | PROVED | handoff §3 (M2) | `C-REG` | PASS |
| `C-M3` | Pathwise summation by parts `Σ_{t≤τ}Z_tT_t = ½T_τ² + ½Σ_{t≤τ}Z_t²` | PROVED | handoff §3 (M3) | none (pathwise) | PASS |
| `C-NEG` | **Rigorous negative result**: mean/variance martingale identities *cannot* isolate `E[Z_τT_τ]`, because `τ−1` is not a stopping time | PROVED | handoff §4 | — | PASS — motivates the certificate route |
| `C-LB` | Elementary rigorous lower bound `E[Z_τ²] ≥ k² = 0.25` | PROVED | handoff §5 | — | PASS (too weak for the target) |
| `C-BELL` | **Bellman/Fredholm state reduction**: `E[Z_τT_τ\|s,x] = a(s)x + b(s)`; `Γ = b(0,0)`; `a = Ka+r_a`, `b = Kb+K_z a+r_b`; `r_a = φ(u)−φ(ℓ)`, `r_b = uφ(u)+1−Φ(u)+Φ(ℓ)−ℓφ(ℓ)` | PROVED | `rebaseguard-proof/proofs/derivation.md`; Step-2 audit §"Bellman/Fredholm"; independently re-derived in `Mathematical_proof/blind_rederivation_report.md` | Markov property + `C-REG` | PASS (three independent derivations agree) |
| `C-SYM` | Reflection identities `a(p,m) = −a(m,p)`, `b(p,m) = b(m,p)`, hence `a(0,0)=0` | PROVED | `derivation.md`; Step-2 audit | reflection involution | PASS |
| `C-EXU` | Existence/uniqueness of bounded `(a,b)` from the convergent Neumann series (`‖K^250‖ ≤ 0.81 < 1`) | PROVED + CERTIFIED (the constant is Arb-certified) | Proof Report §8 | sub-Markov `K` | PASS |
| **`C-F1`** | **`F₁'(0) = 1 − Γ`** — the stopped-score identity linking the analytic derivative to the mean-transition map | **PROVED** (human); its analytically delicate differentiation step is `T-19` | `rebaseguard_phase2c.md` §4; Step-2 audit "Canonical Level-3 theorem" | `C-REG`; reflection symmetry giving `F(0)=0`; `m=1` | PASS |
| `C-RHO` | `F_ρ'(0) = ρF₁'(0)`, unconditional | PROVED | `rebaseguard_phase2c.md` Prop. 2 | affine mixed reuse with mean-zero `e`-independent fresh component | PASS |
| `C-RHOC` | *If* `F₁'(0) < −1` then `ρ_c = 1/\|F₁'(0)\| = 1/(Γ−1) ∈ (0,1)`, with local stability below and instability above | PROVED (conditional) | `rebaseguard_phase2c.md` Prop. 3 | `C-RHO` | PASS — antecedent supplied by `N-03` |

## C. The Arb rigorous numerical certificate

| Claim ID | Scientific statement | Evidence | Source | Assumptions | Status |
|---|---|---|---|---|---|
| `N-01` | Monotone one-sided block contraction: `H_250(0) ≥ 0.196685089387733776… > q_safe = 0.19`, hence `‖K^250‖_∞ ≤ β = 0.81 < 1` | CERTIFIED | `proofs/contraction_monotone.json`; Proof Report §8 | pathwise-coupling monotonicity (proved); outward-rounded Arb | PASS — replayed |
| `N-02` | Continuum residual bounds `δ_a ≤ 8.4634602268726276e-6`, `δ_b ≤ 2.0616516000703808e-4`, with complete Bernstein coverage of the reachable set | CERTIFIED | `proofs/residual.json`; Proof Report §9 | exact dyadic candidate; degree-100 `φ` with Lagrange remainder | PASS — replayed |
| **`N-03`** | **`Γ_CUSUM ∈ [3.9243482005828971282…, 27.8493821275467032805…]`, hence `Γ_CUSUM > 2`** | **CERTIFIED** | `proofs/certificate.json`; `proofs/audit_report.md` | `N-01`, `N-02`; resolvent `C = 1315.789…`; `μ = ‖K_z‖ ≤ √(2/π)` | **PASS — reproduced 2026-08-20, exit 0** |
| `N-04` | `F₁'(0) ∈ [−26.8493821…, −2.9243482…]`, in particular `F₁'(0) < −1` | CERTIFIED (given `C-F1` PROVED) | Proof Report §17 | `C-F1` + `N-03` | PASS |
| `N-05` | `ρ_c = 1/(Γ−1) ∈ [0.0372448049…, 0.3419565426…] ⊂ (0,1)` | CERTIFIED (given `C-RHOC` PROVED) | Proof Report §18 | `C-RHOC` + `N-03` | PASS |

## D. Numerical validation claims (non-rigorous)

| Claim ID | Scientific statement | Evidence | Source | Status |
|---|---|---|---|---|
| `V-01` | Monte Carlo point estimates `Γ ≈ 15.96` (seed 1729) and `Γ ≈ 15.90` (seed 20260818), `n = 200 000` each | NUMERICAL EVIDENCE | `diagnostics/reference.json` | Reproduced exactly |
| `V-02` | `E[Z_τ²] ≈ 4.05`, cross term `E[Z_τT_{τ-1}] ≈ 11.85–11.91` | NUMERICAL EVIDENCE | `diagnostics/reference.json` | Reproduced exactly |
| `V-03` | Wald check `E[T_τ²] ≈ E[τ]`: `463.86 vs 465.61` and `463.25 vs 462.54` | NUMERICAL EVIDENCE (consistency check on `C-M2`) | `diagnostics/reference.json` | Reproduced exactly |
| `V-04` | Reflection balance: `up_fraction ≈ 0.4985 / 0.5011`; `E[Z_τ] ≈ 0`, `E[T_τ] ≈ 0` | NUMERICAL EVIDENCE (consistency check on `C-DEC`) | `diagnostics/reference.json` | Reproduced exactly |
| `V-05` | Independent finite cellwise Arb Bellman solve gives `18.7401484450…`, inside the certified interval | NUMERICAL EVIDENCE | `proofs/bellman_crosscheck.json` | Consistency-enforced by the auditor |
| `V-06` | The `18.74` vs `15.87` gap is finite-discretization bias of the 12-cell chain (whose ARL is `2099.53` instead of `≈465`); refined solver extrapolates to `Γ ≈ 15.8868236` | NUMERICAL EVIDENCE | `proofs/ReBaseGuard_Phase4_Feasibility_PreGate_Report.md` | Explained, not a defect |
| `V-07` | `Γ` across thresholds `h ∈ [0.5, 5.0]` with derived `F₁'(0)`, `ρ_c`, `ARL₀`; at `h=5`: `Γ=15.8851`, `ARL₀=465.4` | NUMERICAL EVIDENCE | `Mathematical_proof/gamma_table.csv` | Consistent with `V-01` |
| `V-08` | 90-test regression suite passes (symmetry invariants, Arb backend, mass balance, oracle conventions) | NUMERICAL EVIDENCE | `rebaseguard-proof/tests/` | PASS, exit 0 |
| `V-09` | Level 1 phenomenon: stopping-selected recursive reuse destabilizes the reference | NUMERICAL EVIDENCE | `rebaseguard_phase15.md`, `rebaseguard_phase2b.md` | Historical |

## E. Explicitly OPEN or NOT CLAIMED

| Claim ID | Statement | Label | Note |
|---|---|---|---|
| `O-01` | `Γ > 2` provable in Lean | NOT CLAIMED | Deliberately out of scope; `Γ>2` is CERTIFIED, never MACHINE-CHECKED |
| `O-02` | `Cov₀(Z_{τ−r}, T_τ) > 0` for every `r` (needed for general `m > 1`) | OPEN | `rebaseguard_phase2c.md` §4 explicitly downgrades this to NUMERICAL EVIDENCE; irrelevant to `m=1` |
| `O-03` | Period-2 behaviour, bimodality, invariant-law shape, multi-cycle oscillation theorem, ARL-degradation mechanism | NOT CLAIMED at Level 1–3 | Step-2 audit "Empirical only unless separately proved" |
| `O-04` | Robustness across arbitrary `m`, `(k,h)`, or noise families | NOT CLAIMED | Proof Report §19 |
| `O-05` | Level-4 multi-cycle recursive reference-state dynamics; second (Shiryaev–Roberts) detector; `Γ_SR > 2` | OPEN | `rebaseguard_phase4d_audit.md`: "Architecture SOUND; not yet executed. Nothing here is a proof of `Γ_SR>2`" |
| `O-06` | Global nonlinear bifurcation theorem | NOT CLAIMED | Step-3 audit §19 |

---

## F. Dependency summary in one line each

```text
T-02 → T-03 → (T-04→T-05→T-06) → T-07 ─┐
T-08 → T-09,T-10 → T-11 → T-12         ├→ T-18 → T-19   (Lean: derivative identity)
T-13 → T-14a → T-14b, T-15, T-16 → T-17┘

C-BELL + C-SYM + C-EXU → N-01, N-02 → N-03            (Arb: Γ > 2)

T-19 (regularity/differentiation) + C-DEC + reflection → C-F1 : F₁'(0) = 1 − Γ
C-F1 + N-03 → N-04 : F₁'(0) < −1
N-04 + C-RHO + C-RHOC → N-05 : ρ_c ∈ (0,1)
```
