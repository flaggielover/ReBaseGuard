# Independent review of P5X L5 (regularity premise of Theorem K5-B)

**Verdict: `P5X_L5_INDEPENDENT_REVIEW = PASS_WITH_SCOPE_LIMITATION`.** P5X L5 correctly proves that
`e ↦ R_{D,m}(e)` is holomorphic on a horizontal strip `|Im e| ≤ θ₀` with `θ₀ > 0` independent of `Re e`,
`m`, and the detector state. So `R_{D,m}` is real-analytic, and in particular C^∞, on all of ℝ. That covers
every regularity premise K5-B uses. The scope limitation is in §6.

This review was run only because K5-B now depends on L5. It is a theory review: it adds files and changes
nothing else. It does not modify L5, K5-B, the K5-B countersignature or any K1/CUSUM evidence. It runs no
scientific compute, builds no producer, does not touch AWS/PS1 or origin/main, and does not declare K5 or P5Y
closed.

```text
P5X_L5_INDEPENDENT_REVIEW     = PASS_WITH_SCOPE_LIMITATION
HOLOMORPHY                    = PASS
REAL_C3_ON_K5_DOMAIN          = PASS
K5B_REGULARITY_PREMISE        = SATISFIED
HIDDEN_C4_REQUIREMENT_IN_K5B  = NO
TEMPORAL_INTEGRITY            = PASS
```

## 0. Independence and lineage

| Item | Value |
|---|---|
| Theorem and proof | `p5x_global_nonlinear_dynamics/PROOF.md` §L5 (L5.1–L5.6, lines 412–482). File sha256 `da4a2d51…42cd88be`, blob `a46e8c3d`. L5 section sha256 `cad5bc6c…c7466449` |
| Frozen obligation | `PROOF_OBLIGATIONS.md` row `L5` (Checkpoint A `db0781ed`, sha256 `f8d7bf3a…`) |
| Introduced | `528908ba` (P5X Checkpoint B, 2026-09-02 19:11 +09). `PROOF.md` has **one** touching commit, so it has never been modified |
| Author lineage | Commit author `suzhe`, co-authored by Claude Opus 5, in the P5X Checkpoint-B session. The only internal classification is `DEPENDENCY_AUDIT.md`: "qualitative; nothing certified depends on it". The only prior note is `DEFECT_REGISTER.md` D4, an over-attribution in the "hence" clause that is not a defect |
| Prior review | None. Premise-binding audit `10769e07` recorded `PB2 = BOUND_WITH_NOTE` because L5 had no independent review |
| Consumed definitions | `FROZEN_THEOREM.md` §1–§2 (`K_e`, `K_{z,e}`, `ρ_{1,e}`, `(l,u)`, `q_D`, P5X-T1(c)); `FROZEN_SCOPE.md` §1 (detectors, inclusive alarm, `z = raw − e`, convention A); P5 `THEOREM.md`/`PROOF.md` (P5-T2 `R = E[Rbar\|e]`, the common probability space, P5-T4); P5X L1 (reduction) and L2 (for `S`) |
| This review | A separate Claude Code session (Claude Opus 5), 2026-09-16, based on `origin/p5y-postk1-frontier = 10769e07`. The review re-derived `R` from the P5 definitions and did not rely on K5 summaries. It supplies a **second proof of holomorphy that does not use L1, L2 or P5-T4** (§2.3) |

**Limit on independence.** The review is independent by session and by method, since §2.3 is a different
proof. It is not independent by agent family (author and reviewer are both Claude), and it is not a human review.

All hashes are in `config/L5_HASH_INVENTORY.json`, and `code/l5_review_check.py verify-hashes` checks them.

## 1. The function, reconstructed from the definitions

- **Probability space.** `raw_1, raw_2, …` are iid `N(0,1)` on a space `(Ω,F,P)` that does not depend on `e`
  (P5 `PROOF.md`).
- **Innovation and detectors.** The detector sees `z_t = raw_t − e`. Both detectors start at the reset state
  `x₀ = (0,0)`:
  - CUSUM(k=½, h=5): `x ↦ (max(0, x⁺+z−½), max(0, x⁻−z−½))`;
  - SR(A): `x ↦ (log(1+e^{x⁺+z−½}), log(1+e^{x⁻−z−½}))`.
- **Stopping time.** `τ` is the first `t` at which the inclusive post-update test fires. From state `x`, an alarm
  occurs iff `z ∉ (l(x), u(x)) = (x⁻ − c_D, c_D − x⁺)`, where `c_CUSUM = 11/2` and `c_SR = log A + ½`. Arm
  priority on ties affects only which arm fires, not `τ`.
- **Window (convention A).** `w = min(m, τ)` and `Rbar = (1/w) Σ_{r<w} raw_{τ−r}`, so the terminal alarm
  observation is included. Each cycle starts from the reset state.
- **Function.** `R_{D,m}(e) = E[Rbar | e]` (P5-T2), where `m` is a fixed integer `≥ 1`.
- **How `R` depends on `e`.** In `raw` coordinates, `τ(e,ω)` depends on `e` in a non-smooth way. In `z`
  coordinates it does not:
  - `{τ = t} = {(z_1,…,z_t) ∈ A_t}`, where `A_t ⊂ ℝ^t` is a fixed Borel set built only from `q_D` and `(l,u)`.
  - The `z_i` are iid with density `φ(z+e)`.
  - `Rbar = e + ā_t(z)` on `{τ = t}`, where `ā_t` is the mean of the last `min(m,t)` coordinates of `z`.

  So `e` enters **only** through the entire density `φ(z+e)` and the additive `e`. This is exactly what L5.6
  claims: the continuation set is a bounded interval, and neither it nor `q` depends on `e`.

## 2. Holomorphy — PASS

### 2.1 Audit of L5's proof, step by step

| Step | L5 claim | Check | Result |
|---|---|---|---|
| Domain | strip `Σ = {\|Im e\| ≤ θ₀}` | `θ₀` must be independent of `σ = Re e`. It is: the only input is `exp(θ²/2)` and a `β` that is uniform in `σ` | ✓ |
| Kernel | `\|φ(z+σ+iθ)\| = φ(z+σ)·e^{θ²/2}` | `Re((a+iθ)²) = a² − θ²`; spot-checked to relative residual `1.5e-16` | ✓ exact |
| Domination | `\|K_e f\| ≤ e^{θ²/2} K_σ\|f\|` | the integration limits `(l(x),u(x))` and `q` do not depend on `e`; `K_σ` is positive | ✓ |
| Powers | `‖K_e^n‖ ≤ e^{nθ²/2}‖K_σ^n‖ ≤ e^{nθ²/2}β^{⌊n/n₀⌋}` | induction using positivity of `K_σ`; `‖K_σ^n‖ = sup_x P_{x,σ}(τ > n)` | ✓ |
| P5-T4 uniformity | `n₀`, `β < 1` uniform in `σ` and `x` | re-proved from P5 `PROOF.md`. CUSUM: ten steps with `z ≥ 1` (for `e ≤ 0`) or `z ≤ −1` (for `e ≥ 0`) alarm from any state, because `S^± ≥ 0`, so `n₀ = 10` and `p₀ = Φ(−1)^{10}`. SR: one step with `\|z\| ≥ c_SR` alarms, because `y^± ≥ 0`, so `n₀ = 1` and `p₀ = Φ(−c_SR)`. The D1 erratum (`b_SR = log(1+A)`) keeps `y ≥ 0` and has no effect | ✓ |
| Choice of `θ₀` | `e^{n₀θ₀²/2}β < 1` | symbolic: `θ₀² = p₀/n₀` gives `e^{p₀/2}(1−p₀) ≤ e^{−p₀/2} < 1` | ✓ exists, positive |
| Single operator | `e ↦ (K_e f)(x)` holomorphic | bounded interval, entire integrand, locally uniform bound; Morera + Fubini | ✓ |
| Iterates | `K_e^{i−1} S_r (x₀)` holomorphic | **Exposition gap, filled here.** The inner function `(K_e f)(y)` depends on `e`. It is Borel in `y` and continuous in `e`, so it is jointly measurable (Carathéodory), and it is bounded by `e^{θ²/2}‖f‖`. Morera + Fubini then applies again. Induction on depth | ✓ (gap closed) |
| Unbounded sources | `S₀ = ρ_{1,e}` holomorphic | **Exposition gap, filled here.** `ρ_{1,e}` integrates over half-lines, which L5.4's "bounded interval" argument does not cover. Its closed form (`φ`, `Φ` entire) is entire in `e`, and `\|ρ_{1,e}(x)\| ≤ e^{θ²/2}(√(2/π) + \|σ\|)` uniformly in `x` | ✓ (gap closed) |
| Local bounds | `‖S_r‖` locally bounded | `‖S_r‖ ≤ ‖K_{z,e}‖·‖K_e‖^{r−1}·‖h₁‖`, with `‖K_{z,e}‖ ≤ e^{θ²/2}(√(2/π)+\|σ\|)` and `‖h₁‖ ≤ 1 + e^{θ²/2}` | ✓ |
| Neumann tail | `Σ_n K_e^n S_r (x₀)` converges uniformly on compacts | geometric in `e^{n₀θ²/2}β < 1`, with `‖S_r‖` bounded on `\|σ\| ≤ M` | ✓ |
| Limit | `g_r(x₀)` holomorphic | Weierstrass | ✓ |
| Assembly | `R = e + ` finite combination (P5X-T1(c)) | at most `m−1` operator applications plus `m` resolvent terms. Holomorphic for every `m`, and `θ₀` does not depend on `m` | ✓ |
| Real identity | the extension equals `R` on ℝ | by L1 (the identity is used only at real `e`) | ✓ given L1; §2.3 removes this dependence |

### 2.2 Falsification attempts on the strip

- **Radius collapse as `|σ| → ∞`.** None. The bound `e^{θ²/2}` does not depend on `σ`, and P5-T4's `β` is
  uniform in `e`, so the strip is a full horizontal strip. Unbounded continuation sets would break this; here
  they are bounded.
- **`m`-dependent collapse.** None. `m` enters only through a finite combination that is assembled after the
  strip is fixed.
- **State-dependent collapse.** None. All bounds are sup-norms over `E_D`.
- **Detector-dependent singularity.** None. The non-smooth `max(0,·)` in CUSUM and `log(1+exp)` in SR act on
  `z`, not on `e`. Their only effect is on the fixed sets `A_t`.
- **How wide the strip is.** Double precision, not authoritative (`evidence/STRIP_ARITHMETIC.json`):

  | Detector | L5 route `θ₀` | Direct route `θ₁` |
  |---|---|---|
  | CUSUM | `3.2e-5` | `1.4e-4` |
  | SR | `2.7e-6` | `2.7e-6` |

  These strips are tiny but positive. Only positivity matters, because K5-B never uses Cauchy estimates.

### 2.3 Independent second proof (does not use L1, L2 or P5-T4)

1. **One-step floor.** From every live state, `x⁺, x⁻ ≥ 0`, so the alarm set contains `{|z| ≥ c_D}`. Then
   `P_x(no alarm) ≤ Φ(σ+c_D) − Φ(σ−c_D) ≤ 1 − 2Φ(−c_D) =: β₁ < 1`. The middle quantity is maximised at
   `σ = 0`, because its derivative `φ(σ+c)−φ(σ−c)` has the sign of `−σ`. So `P_σ(τ ≥ t) ≤ β₁^{t−1}` uniformly.
2. **Series.** `R(e) = Σ_{t≥1} F_t(e)`, where
   `F_t(e) = ∫_{A_t} (e + ā_t(z)) Π_{i≤t} φ(z_i+e) dz`.
   The series converges absolutely at real `e` because `τ < ∞` a.s. and `E|Rbar| < ∞`.
3. **Termwise holomorphy.** The integrand is entire in `e`. On `|σ| ≤ M` it is dominated by
   `e^{tθ²/2}(|e| + Σ|z_i|) Π sup_{|σ|≤M} φ(z_i+σ)`, which is integrable. Morera + Fubini then make `F_t`
   entire.
4. **Uniform bound.** Apply Cauchy–Schwarz to each `E_σ[|Z_i| 1{τ=t}]`:
   `|F_t(e)| ≤ e^{tθ²/2}(|e| + t√(1+σ²)) β₁^{(t−1)/2}`.
5. **Strip.** Put `p₁ = 2Φ(−c_D)` and `θ₁² = p₁/2`. The ratio is then `e^{θ²/2}β₁^{1/2} ≤ e^{−p₁/4} < 1`, so the
   series converges uniformly on compact subsets of `|Im e| ≤ θ₁`. By Weierstrass, `R` is holomorphic there. ∎

The two proofs agree. L5's conclusion for `R` therefore does not depend on the correctness of L1's reduction.

## 3. Real C³ on the K5-B domain — PASS

A function holomorphic on an open neighbourhood of ℝ is real-analytic on ℝ, and so has continuous derivatives of
every order there. (A closed strip of width `θ₀` contains the open strip.) No real point is special:

- `e = 0` is an interior point of ℝ. All derivatives are two-sided, and no one-sided or endpoint argument is
  needed. Oddness gives `R''` odd and continuous, so `R''(0) = 0`.
- Every closed cell meeting `(0,2]` is covered: CUSUM cells 0–309 and SR PS1 cells 0–294.
- The whole of CUSUM cell 309, `[1.98391, 2.092283]`, is covered, including the part beyond `e = 2`.
- Any interval inside `[0, 11/2]`, `[0, e_far = 12]` or ℝ is covered.
- This holds for both detectors and every `m ≥ 1`, which includes the frozen `m ∈ {1,2,3,5}`.

## 4. Load-bearing K5-B uses — all satisfied, maximum order C³

From `K5_GLOBAL_BRIDGE.md` (sha256 `c1c62346…`), read line by line. See also `evidence/REGULARITY_USES.json`.

| # | Where K5-B uses regularity | Minimum | L5 supplies |
|---|---|---|---|
| U1 | `R''(0) = 0` from oddness (Setting; proof step 1) | C² at 0 | ✓ |
| U2 | MVT for `R''` on `C_k`: `R''(t) ≥ R''(x_{k−1}) + L_k(t−x_{k−1})` (steps 1, `μ_k`, `ℓ_k`) | C³ (`R''` differentiable, `R''' ≥ L_k`) | ✓ |
| U3 | Cell 1: `R''(t) ≥ L₁t`, `g ≤ −L₁e³/3` | C³ on `[0,x₁]` | ✓ |
| U4 | `g(e) = g(x_{k−1}) − ∫ tR''` (FTC; `U_k`, `γ_k`) | C² | ✓ |
| U5 | `g' = −eR''` | C² | ✓ |
| U6 | MVT for `g` about `e0_k` (`Γ_k`) | C² | ✓ |
| U7 | K1 inputs `H_k ⊇ R''(C_k)`, `M_k ≥ sup|R''|` on the **whole closed** cell | C² on the closed cell | ✓ |
| U8 | `L_k ≤ inf_{C_k} R'''` must make sense on the closed cell | C³ (`R'''` defined) | ✓ |
| U9 | `D_k ∋ R'(e0)`; `s' = g/e²`; strictly decreasing by MVT | C¹ | ✓ |
| U10 | `s(0+) = −R'(0) = Γ̃ − 1` | C¹ at 0 | ✓ |
| U11 | continuity of `s`; `s(2) < 1 ⇔ R(2) > −2` | C⁰ | ✓ |

**Hidden C⁴ requirement in K5-B: NO.** The whole-cell signed-`R'''` reasoning (U2, U3, U8) treats `L_k` as a
certified **input**. K5-B needs only that `R'''` exists on the closed cell and bounds it from below. It never
takes a derivative of `R'''`, never uses a remainder of order 4, and never needs `R'''` to be continuous. The
fourth-order objects in the repository belong to **producers** that would certify `L_k` or `H_k`:

- `ρ·T[R,4]` whole-cell remainders (readiness audit §4; `K5_TARGET_AND_THIRD_ORDER.md`);
- SR Aux3 fourth-order towers;
- the norm-only order-4 towers in `aux_refine`.

These are not K5-B premises. If a producer needs C⁴ or higher, L5 already gives C^∞, but that producer's own
remainder bounds are its own obligation and are not reviewed here.

## 5. Adversarial review (`evidence/ADVERSARIAL_REVIEW.json`)

| Failure mode | Finding |
|---|---|
| Pointwise but non-uniform domination | Ruled out. Every bound is a sup-norm over `E_D` with the explicit factor `e^{nθ²/2}`, and it is uniform on `\|σ\| ≤ M`, `\|θ\| ≤ θ₀` |
| Stopping-time tail | Ruled out. The tail is geometric in `e^{n₀θ²/2}β` (L5 route) or `e^{θ²/2}β₁^{1/2}` (direct route), with ratio `< 1` uniformly on the strip |
| Failure to interchange derivative and integral | Avoided by design. The proof uses Morera + Fubini + Weierstrass with no termwise differentiation. Joint measurability of iterated integrands is checked (§2.1) |
| Boundary at `e = 0` | None. 0 is interior to the strip and to ℝ |
| Strip radius collapse (in `σ`, `x`, `m`) | None; see §2.2. It would occur only if the continuation interval were unbounded or `β` were non-uniform in `e`, and neither is the case |
| `m`-dependent domination | None. `θ₀` and `θ₁` do not depend on `m` |
| Detector-dependent singularity | None. The non-smooth recursions act on `z`, not `e`, and SR's D1 erratum does not affect `x ≥ 0` |
| `R` odd yet not C³ (K5-B adversarial A6/A7) | Excluded by L5 for the true `R`. A6/A7 remain valid only as demonstrations that the premise is load-bearing |

## 6. Verdict and scope limitation

`PASS_WITH_SCOPE_LIMITATION`. The limitations are:

1. **Only `R` is certified.** L5 also claims that `S_{D,m}` is real-analytic, through L2. That route was not
   reviewed: L2 was not audited, and K5-B does not use `S`.
2. **Only qualitative regularity.** `θ₀` is positive but tiny. L5 gives no derivative bound, no radius of
   practical size, and no approximation rate (L5.6 says so itself). No certified enclosure may cite L5 for a
   **numerical** bound on `R''`, `R'''` or higher derivatives.
3. **Two exposition gaps.** The holomorphy of iterates whose integrands depend on `e`, and of the half-line
   sources `ρ_{1,e}`, is not argued in L5's text. Both gaps are closed in §2.1 without changing the conclusion.
   L5 is **not** edited.
4. **L1 is used for the identity in L5's own route but not reviewed in full.** The direct proof (§2.3) makes
   the holomorphy conclusion for `R` independent of L1.
5. **The frozen "hence interval-valued `e` is admissible" clause is not certified.** It is D4 and irrelevant to
   K5-B.
6. **Independence limit** as stated in §0.

## 7. Temporal integrity — PASS

- L5 (`528908ba`, 2026-09-02) is an ancestor of K5-B (`6f1d351b`, 2026-09-13), of the K5-B countersignature
  (`d7d3c08b`), and of the premise-binding audit (`10769e07`).
- `PROOF.md` has exactly one touching commit, and `PROOF_OBLIGATIONS.md`, `FROZEN_THEOREM.md` and
  `FROZEN_SCOPE.md` are Checkpoint-A bytes.
- L5 names no cell, no `m`-specific outcome, and no tunable constant.
- This namespace only adds files.

## 8. What this countersignature certifies

> For `D ∈ {CUSUM(k=½,h=5), SR(A=520.886133602749)}` and every integer `m ≥ 1`, `R_{D,m}(e) = E[Rbar | e]`
> (convention A, reset start, inclusive alarm) extends holomorphically to a strip `|Im e| ≤ θ > 0` whose width
> does not depend on `Re e` or `m`. Hence `R_{D,m} ∈ C^∞(ℝ)`, and so it supplies every regularity premise of
> Theorem K5-B (U1–U11: C⁰–C³, including `R''(0) = 0` with oddness) on every closed cover cell. That includes
> `e = 0` and the full cell containing `e = 2`.

It certifies **nothing** about:

- `S_{D,m}`;
- derivative magnitudes;
- K1 or order-3 enclosures;
- whether any cell passes;
- H3a, K5, P5Y or P5Z.

## Commands

```bash
python -B tests/test_l5_review.py
python -B code/l5_review_check.py verify-hashes
python -B code/l5_review_check.py strip --out evidence/STRIP_ARITHMETIC.json
```
