# K2: analytic route for `s_min = inf_e S_{D,m}(e) > 0` (pre-compute, no new result)

## 1. Exact frozen definitions

- `S_{D,m}(e) = Var(Rbar | e)` and `Rbar = (1/w) Σ_{r<w} raw_{τ−r}`, with `w = min(m, τ)` and `raw_t ~ iid N(0,1)` (P5X FROZEN_THEOREM §1; P5-T1/T2).
- `s_min = inf_{e∈ℝ} S_{D,m}(e)` per frozen `(D,m)`.
- P5X-T6 lower arm: `ρ²s_min + (1−ρ)²/m ≤ E_π[e²]`. Gate G4 requires "`s_min > 0` … certified".
- K1 checkpoint §1: "`K2` (`s_min > 0`)".
- Alarm structure (P5X-T1, EXACT):
  - pre-alarm state `x = (x⁺, x⁻)` with `x^± ≥ 0`;
  - continuation interval `(l(x), u(x)) = (x⁻ − c_D, c_D − x⁺)`, and the alarm is exactly `{z ≤ l} ∪ {z ≥ u}`;
  - `c_CUSUM = 11/2`;
  - `c_SR = log A + 1/2`, or `log(1+A) + 1/2` under erratum D1. The bound below is taken over both readings.

## 2. Route A: exact theorem, tried in the requested order

| attempt | outcome |
|---|---|
| nondegeneracy / pointwise positivity | yes: `S(e) > 0` for each `e`, but alone this does not bound the infimum |
| continuity + compact domain + far-field limit | viable (P5X `L5` gives real-analytic `S`; P5X-T3 with P5-T5 gives `S(e) → 1` as `|e| → ∞`), but it yields only a **non-constructive** `s_min > 0` |
| **direct uniform conditional-variance bound** | **works, with an explicit constant, and needs neither continuity nor the far field** (Lemma K2-A) |
| existing Arb or exact lower bounds | none in the repository (the Gate-1 scan `0.0403` is explicitly not a certificate) |

### Lemma K2-A (proposed EXACT theorem)

For every `D ∈ {CUSUM, SR}`, every `m ≥ 1` and every `e ∈ ℝ`:

```text
S_{D,m}(e)  ≥  κ_D / m² ,     κ_D := min{ (1 − 2/π)/2 , u(G_D) } > 0 ,
u(t) := Var(N | N ≥ t) = 1 + t·λ(t) − λ(t)² ,   λ(t) = φ(t)/(1 − Φ(t)) ,
G_CUSUM := 2c_CUSUM = 11 ,      G_SR := 2 log(1+A) + 1  (≥ 2c_SR under either reading).
```

Hence `s_min(D,m) ≥ κ_D/m² > 0`.

**Proof.**

1. **Alarm set in raw coordinates.** Since `z = raw − e`, given pre-alarm state `x_{t−1}` the alarm at step `t` is `raw_t ∈ T_t := (−∞, a_t] ∪ [a_t + g_t, ∞)`, where `a_t = l(x_{t−1}) + e` and `g_t = u − l = 2c_D − x⁺ − x⁻ ≤ 2c_D ≤ G_D` (because `x^± ≥ 0`). If `g_t ≤ 0` then `T_t = ℝ`.
2. **Finiteness.** `τ < ∞` a.s. (P5-T4) and `E_e[Rbar²] < ∞` (P5-T5).
3. **Conditional law of the terminal draw.** Let `𝒢 = σ(τ, raw_1, …, raw_{τ−1})`. On `{τ = t}`, `raw_t` is independent of `F_{t−1}`, and `x_{t−1}` is `F_{t−1}`-measurable. So the conditional law of `raw_τ` given `𝒢` is `N(0,1)` conditioned on `T_τ`.
4. **Window.** `w = min(m, τ)` and `Σ_{r=1}^{w−1} raw_{τ−r}` are `𝒢`-measurable. Therefore `Var(Rbar | 𝒢) = Var(raw_τ | 𝒢)/w² ≥ Var(raw_τ | 𝒢)/m²`.
5. **Total variance.** `S(e) = Var(Rbar) ≥ E[Var(Rbar | 𝒢)] ≥ m^{−2} · inf_{a∈ℝ, g≤G_D} V(a,g)`, where `V(a,g) = Var(N | (−∞,a] ∪ [a+g,∞))`, and `V = 1` when `g ≤ 0`.
6. **Gaussian lemma: `V(a,g) ≥ κ_D` for `0 < g ≤ G_D`.** It uses three standard facts:
   - (i) a two-component mixture has variance at least the weighted within-component variance;
   - (ii) `u(t)` is non-increasing in `t`, by log-concavity of `φ`, and `Var(N | N ≤ a) = u(−a)`;
   - (iii) `u(0) = 1 − 2/π`.

   The cases:
   - `a ≥ 0`: the left part has weight `Φ(a)/(Φ(a) + Q(a+g)) ≥ 1/2`, since `Q(a+g) ≤ 1/2 ≤ Φ(a)`, and variance `u(−a) ≥ u(0)`. So `V ≥ (1−2/π)/2`.
   - `a + g ≤ 0`: symmetric.
   - `a < 0 < a+g`: then `−a < G_D` and `a+g < G_D`, so both component variances are `≥ u(G_D)`, and `V ≥ u(G_D)`.
7. **Positivity.** `u(G_D) > 0`, because it is the variance of a nondegenerate law. So `κ_D > 0`. `∎`

**Sanity check (float, NOT a certificate).**
- `u(11) ≈ 7.88e-3` and `u(13.515) ≈ 5.30e-3`.
- Resulting bounds: `s_min(CUSUM, m) ≳ 7.9e-3/m²` and `s_min(SR, m) ≳ 5.3e-3/m²`.
- A brute-force grid over `(a,g)` gives `inf V ≈ 0.040 / 0.026`, consistent with and above `κ_D`.
- A Sampford-type Mills-ratio inequality `(4 + t² − t√(t²+8))/8` was also tested as an analytic lower bound for `u` and is **numerically false** at these `t`. It is **rejected** and must not be used.

## 3. Status and minimal compute

- **Positivity (the frozen K2 obligation):** Lemma K2-A proves it exactly. No numerics are needed for `s_min > 0`.
- **Explicit value:** requires one rigorous interval evaluation of the elementary closed form `u(G_D)` at two points (Arb, milliseconds). This is not a cover, not a campaign and not route B.
- **Route B (C2 cover of `E_e[Rbar²]`):** **not needed** for K2 as frozen. It is not run.

```text
K2_ANALYTIC_ROUTE     = PASS_POSSIBLE   (complete proof above; needs independent adjudication + a formal write-up
                                         citing the log-concave truncated-variance monotonicity lemma)
K2_MINIMAL_NEW_COMPUTE = NONE           (optional: two-point rigorous evaluation of u(G_D) to state κ_D numerically)
```

## 4. Governance findings (not repaired here)

1. **Tier.** P5X-T6 asks for a "certified" `s_min`. Lemma K2-A gives an **EXACT_THEOREM** constant, which is logically stronger than a cover certificate. The adjudicator must record that an exact explicit constant satisfies G4's "certified" clause.
2. **Frozen quantitative corollary defect.** The P5X-T6 corollary and P5X-T9 item 5 read: "the stationary law lives more than an order of magnitude outside the linearisation radius (`r_lin = 0.05`) for every ρ". By the exact identity, `E_π[e²] = 1/m` at `ρ = 0`, so `RMS = 0.447 < 10·r_lin` for `m = 5`, whatever `s_min` is. More generally `min_ρ (ρ²s + (1−ρ)²/m) = s/(1+ms)`, so the "×10" reading needs `s_min > 1/3, 1/2, 1` for `m = 1, 2, 3` and is **unattainable for `m = 5`**. The corollary is not part of the K2 obligation. It is a frozen P5X text defect for adjudication. Lemma K2-A does not deliver it, and neither would any value of `s_min` for `m = 5`.
3. **T10 side note.** The separate T10 hypothesis "`S` continuous at 0" is discharged by P5X `L5` (real-analyticity), once `L5` is adjudicated. That is not a K2 item.
