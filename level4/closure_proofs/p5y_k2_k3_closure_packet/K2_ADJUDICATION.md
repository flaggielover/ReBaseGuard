# K2 adjudication: `s_min = inf_e S_{D,m}(e) > 0` (additive closure packet, 2026-09-13)

**Independence disclosure.** This adjudication was carried out as a separate pass that re-derived every step from the **frozen sources**:
- `level4/stage_d/src/stopped.py::_sr_update`
- `level4/src/rebaseguard_level4/frozen.py::cusum_update`
- `p5_nonlinear_dynamics/{DEFINITION_AUDIT,THEOREM,PROOF}.md`
- `p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md`

It did not start from the candidate proof in `p5y_postk1_precompute_resolution/K2_ANALYTIC_ROUTE.md`. The same agent authored that candidate, so a second human or agent countersignature is recommended before any public claim. Nothing historical is rewritten.

## 1. Frozen definitions checked

| item | frozen source | checked |
|---|---|---|
| `S_{D,m}(e) = Var(Rbar ∣ e)`, `Rbar = (1/w) Σ_{r<w} raw_{τ−r}`, `w = min(m,τ)`, `raw_t ~ iid N(0,1)` independent of `e` | DEFINITION_AUDIT §2–4 (AUDIT-1); FROZEN_THEOREM §1 | yes |
| `s_min = inf_{e∈ℝ} S_{D,m}(e)`, per frozen `(D,m)`, `m ∈ {1,2,3,5}` | FROZEN_THEOREM §7; K1 checkpoint §1–2 | yes |
| detector reset each cycle, no head start, no minimum dwell; `z_t = raw_t − e`; inclusive post-update test | DEFINITION_AUDIT §2 | yes |
| CUSUM: `S⁺ ← max(0, S⁺ + z − 1/2)`, alarm iff `S⁺ ≥ 5` | `frozen.py::cusum_update` (`new_plus >= h`) | alarm ⇔ `S⁺_{t−1} + z − 1/2 ≥ 5` (since `h > 0`) ⇔ `z ≥ 11/2 − S⁺_{t−1}`; symmetric minus arm |
| SR: `Y ← logaddexp(0, Y + z − 1/2)`, alarm iff `Y + z − 1/2 ≥ log A`, stored `Y = log(1+R) ≥ 0` | `stopped.py::_sr_update` (`log_r_plus >= log_thr`, `log_thr = log A`) | alarm ⇔ `z ≥ log A + 1/2 − Y⁺_{t−1}`; symmetric minus arm |

**Alarm geometry (both detectors, confirmed).**
- For pre-alarm state `x = (x⁺, x⁻)` with `x^± ≥ 0`, the next-step alarm set is `{z ≤ x⁻ − c_D} ∪ {z ≥ c_D − x⁺}`, where `c_CUSUM = 11/2` and `c_SR = log A + 1/2`. This matches P5X-T1.
- In raw coordinates, the alarm set is `T = (−∞, a] ∪ [a + g, ∞)` with `a = x⁻ − c_D + e` and `g = 2c_D − x⁺ − x⁻ ≤ 2c_D`.
- **Correction to the candidate:** the SR threshold in the frozen code is `log A`, not `log(1+A)` (erratum D1 concerns the state bound). The candidate's `G_SR = 2 log(1+A) + 1` is still a valid upper bound, so nothing breaks. Below, `G_SR = 2 log A + 1`.

## 2. Step audit of the candidate proof

| step | verdict |
|---|---|
| 1 alarm set in raw coordinates, gap `≤ 2c_D` | **valid** (confirmed from frozen code) |
| 2 `τ < ∞` a.s. and `E_e[Rbar²] < ∞` | **valid**: P5-T4 and P5-T5 are exact, re-verified here, and listed as authoritative premises by the P5 independent adjudication (P6 handoff item 3) |
| 3 conditional law of `raw_τ` given `𝒢 = σ(τ, raw_1..raw_{τ−1})` is `N(0,1)` restricted to `T_τ` | **valid**: on `{τ = t}`, `raw_t ⟂ F_{t−1}` and `x_{t−1} ∈ F_{t−1}` |
| 4 `Var(Rbar ∣ 𝒢) = Var(raw_τ ∣ 𝒢)/w² ≥ Var(raw_τ ∣ 𝒢)/m²` | **valid**: `w` and the other window terms are `𝒢`-measurable; `1 ≤ w ≤ m` |
| 5 law of total variance | **valid** (`Rbar ∈ L²`) |
| 6 Gaussian lemma via monotonicity of `u(t) = Var(N ∣ N ≥ t)` | **valid but not self-contained**: it depends on the convexity of the inverse Mills ratio, which the candidate cites but does not prove. The formula `u(t) = 1 + tλ − λ²` is correct. **Replaced** below by an elementary lemma with explicit rational constants. |
| 7 positivity | **valid** |
| Mills-ratio shortcut | not used (already rejected as numerically false) |

## 3. Adjudicated theorem (self-contained)

**Theorem K2.** For `D ∈ {CUSUM, SR}`, every `m ≥ 1` (in particular `m ∈ {1,2,3,5}`) and every `e ∈ ℝ`:

```text
S_{D,m}(e) ≥ κ*_D / m²,     κ*_CUSUM = 121/46875 (≈ 2.581e-3),     κ*_SR = 49/30000 (≈ 1.633e-3).
Hence s_min(D,m) ≥ κ*_D/m² > 0.
```

**Lemma G1 (bathtub).** If a real random variable has a density `f ≤ M` a.e., then `Var ≥ 1/(12M²)`.
*Proof.* Let `μ` be the mean. Among measurable `0 ≤ f ≤ M` with `∫f = 1`, the integral `∫(x−μ)²f` is minimised by `f = M·1{|x−μ| ≤ 1/(2M)}` (bathtub principle), and its value is `1/(12M²)`. `∎`

**Lemma G2 (Gordon).** For `t > 0`: `t·φ(t)/(1+t²) < Q(t) < φ(t)/t`, where `Q = 1 − Φ`.
*Proof.*
- The upper bound: `∫_t^∞ φ(x)dx < ∫_t^∞ (x/t)φ(x)dx`.
- The lower bound: let `h(t) = Q(t) − tφ(t)/(1+t²)`. Then `h'(t) = −2φ(t)/(1+t²)² < 0` and `h(∞) = 0`, so `h > 0`. `∎`

**Corollary G3.** `λ(t) := φ(t)/Q(t)` is increasing on ℝ, and `λ(t) < t + 1/t` for `t > 0`.
*Proof.*
- `λ' = λ(λ − t)`. This is `> 0`: for `t ≤ 0`, `λ > 0 ≥ t`; for `t > 0`, `λ > t` by G2.
- The bound `λ(t) < t + 1/t` is G2's lower bound rearranged. `∎`

**Lemma G4.** Let `N ~ N(0,1)` and `T = (−∞,a] ∪ [a+g,∞)` with `0 < g ≤ G` and `G ≥ 2`. Then `Var(N ∣ N ∈ T) ≥ 1/(12 (G/2 + 2/G)²)`. If `g ≤ 0`, then `T = ℝ` and the variance is 1.

*Proof.* The conditional density is `φ·1_T/P(T)`. Write `b = a + g`.
- **`a ≥ 0`.** `P(T) ≥ Φ(0) = 1/2` and `sup φ ≤ φ(0)`, so `M ≤ √(2/π) < 1`. G1 gives variance `≥ 1/12`.
- **`b ≤ 0`.** Symmetric: variance `≥ 1/12`.
- **`a < 0 < b`.** Put `t₀ = min(−a, b) ≤ g/2 ≤ G/2`. Then `sup_T φ = φ(t₀)`, and `P(T) ≥ Q(t₀)` (the half-line whose endpoint is at distance `t₀`). So `M ≤ λ(t₀) ≤ λ(G/2) < G/2 + 2/G` by G3, and G1 gives the bound.

Finally `1/(12(G/2 + 2/G)²) ≤ 1/12` for `G ≥ 2`. `∎`

**Proof of Theorem K2.** Candidate steps 1–5, which are all valid, give `S_{D,m}(e) ≥ m^{−2} · inf_{a, g ≤ G_D} Var(N ∣ T)`. Apply G4:
- **CUSUM.** `G = 11`, so `G/2 + 2/G = 125/22` and `κ* = 1/(12·(125/22)²) = 121/46875`.
- **SR.** `G = 2 log A + 1 < 14`. Indeed `log A < 13/2` because `A = 520.886133602749 < e^{13/2}`, which follows from the rational bounds `e ≥ Σ_{k≤6} 1/k! = 1957/720` and `e^{1/2} ≥ Σ_{k≤4} 2^{−k}/k! = 633/384`, whose product gives `e^{13/2} > 663`. So `G/2 < 7`, and G3 (monotone `λ`) gives `M < λ(7) < 50/7`, hence `κ* ≥ 1/(12·(50/7)²) = 49/30000`.

The bound holds for every `e`, since the gap does not depend on `e` and `a` ranges over all of ℝ, and for every `m ≥ 1`, since `w ≤ m`. `∎`

Rational arithmetic is replayed exactly, with no floats in any decision, by `code/verify_k2_constants.py` (`tests/test_k2_constants.py`).

## 4. Does an exact theorem with an explicit constant satisfy "certified `s_min`"?

- **The frozen text.**
  - P5X tier vocabulary: `EXACT_THEOREM | CERTIFIED_THEOREM | CONDITIONAL_THEOREM | NUMERICAL_EVIDENCE …`.
  - `CERTIFIED_THEOREM` = "an exact theorem whose hypotheses are discharged by an outward-rounded interval certificate … never a grid evaluation".
  - G4 requires `s_min > 0` … "certified".
  - G8 forbids justification by point evaluation, Monte Carlo or floating-point numbers, and requires independent re-checkability.
- **Ruling.**
  - "Certified" in the frozen corpus distinguishes rigorously established scalars from measured or grid values. It does not require one particular proof technique.
  - An exact theorem with exact rational constants is at least as strong as an interval certificate, has no rounding, is re-checkable by exact arithmetic, and meets G8.
  - **Binding precedent:** `THEOREM_ADJUDICATION.json` (binding, 2026-09-05) already treats the *exact* theorem P5-T5 as closing the certified-finiteness requirement on `M_2` in the same gate G4.
  - `CERTIFICATE_PLAN.md` lists `C2` as "mandatory". That is the P5X campaign's execution **route** to these scalars, not a definition of the K2 obligation, which the P5Y K1 checkpoint states as `s_min > 0`.
  - P5X-T6's lower arm with `s_min := κ*_D/m²` therefore holds as an **EXACT_THEOREM**. P5X itself is not recoloured (its adjudicated status is unchanged).

```text
K2_ANALYTIC_PROOF_VALID              = YES  (candidate steps 1-5 valid; step 6 replaced by self-contained G1-G4;
                                             constants 121/46875 (CUSUM), 49/30000 (SR); SR threshold corrected to log A)
K2_CERTIFICATION_SEMANTICS_SATISFIED = YES  (exact explicit constant ⊇ "certified"; binding precedent: TA on P5-T5 / G4)
K2_FINAL                             = CLOSED  (s_min(D,m) ≥ κ*_D/m² > 0 for all 8 frozen (D,m); countersignature recommended)
```

## 5. Explicitly not claimed

- The P5X-T6 corollary and P5X-T9(5), "more than an order of magnitude outside `r_lin` for every ρ", are **not** delivered by `κ*`. For `m = 5` they are unattainable for any `s_min`, since at ρ = 0 the stationary variance is exactly `1/m`. This stays a recorded P5X text defect.
- The T10 hypothesis "`S` continuous at 0" is a separate item and is not ruled here.
