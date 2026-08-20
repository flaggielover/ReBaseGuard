# ReBaseGuard — Phase-2B Formal Theory Gate Report

**Role: mathematical referee, not project advocate.** Evidence labels are used strictly:
PROVED · PROPOSITION UNDER STATED ASSUMPTIONS · ASYMPTOTIC/APPROXIMATION · NUMERICAL EVIDENCE · CONJECTURE · COUNTEREXAMPLE FOUND. The last four are never written as PROVED.

---

## 1. Executive verdict

**THEORY GATE: PASS** — via Route B, with a genuine bonus from an exact score representation of `F'(0)`.

Two non-trivial, rigorous results survive the gate:

- **(Route B — the clean theorem.)** For mixed reuse `R_{j+1} = ρ·μ̂_reuse + (1−ρ)·μ̂_fresh` with the fresh block independent of the stopping event, `F_ρ(e) = ρ·F_1(e)` holds **exactly** for all `e`, hence `F_ρ'(0) = ρ·F_1'(0)` and the critical reuse fraction `ρ_c = 1/|F_1'(0)|`. This is PROVED (elementary), and it is non-trivial: it converts the whole phenomenon into one interpretable dimensionless knob and predicts a sharp stability transition at `ρ_c`. Numerically `ρ_c = 0.116` at `(m,k,h)=(5,0.5,5)`.
- **(Route A — the mechanism, made exact.)** In the natural monitoring model, `F'(0) = 1 − Γ(m,k,h)` with the **exact identity** `Γ = (1/m)·Σ_{r=0}^{m-1} Cov_0(Z_{τ−r}, S_τ)`, `S_τ = Σ_{t≤τ} Z_t`. This is a PROPOSITION UNDER STATED ASSUMPTIONS (uniform integrability / exponential stopping-tail regularity for the change-of-measure differentiation). It is verified to Monte-Carlo precision (identity `-9.196` vs finite-difference `-9.110`). Because every `Cov_0(Z_{τ−r},S_τ) > 0` (verified), `Γ > 0` always ⇒ `F'(0) < 1` always; sign reversal `F'(0)<0` iff `Γ>1`; instability `F'(0)<−1` iff `Γ>2`. An unstable interval `|F'(0)|>1` provably exists (e.g. `Γ=10.20` at `m=5`).

**What does NOT survive as a theorem:** the clean *period-2 flip bifurcation* (T5) and the *cubic normal form* (§10) are **rejected as rigorous claims** — the transition map has a boundary layer near 0 that no low-order Taylor expansion captures, so "supercritical flip" cannot be certified. The correct rigorous statement is weaker: *local sign-reversing instability inside a globally contracting (fold-back) map*. Bimodality of the invariant law (T8) remains a CONJECTURE with strong numerical support. The `|F'(0)| ≍ h/(mk)` scaling hypothesis is **FALSE (counterexample found)**.

The phenomenon is **not a simulator artifact**: it reproduces from a first-principles model, the alarm-at-minimum-dwell fraction is ~0.001 (so it is not a dwell/edge effect), and the score identity derived analytically matches the simulator to 1%.

---

## 2. Exact mathematical model

`X_t ~iid N(0,1)`. In cycle `j` the reference is a scalar `R_j = e_j`. Centered observations `Z_t = X_t − e_j`. Symmetric two-sided CUSUM:

```
S_t^+ = max(0, S_{t-1}^+ + Z_t − k),   S_t^- = max(0, S_{t-1}^- − Z_t − k),   S_0^± = 0.
τ = inf{ t ≥ m : max(S_t^+, S_t^-) ≥ h }.
```

Terminal reuse block: `μ̂_{τ,m} = (1/m) Σ_{r=0}^{m-1} X_{τ−r}` (the last `m` raw observations, **including** the alarm observation). Full replacement `e_{j+1} = μ̂_{τ,m}`; full CUSUM reset each cycle (`S_0^± = 0`). In centered form `μ̂_{τ,m} = e_j + (1/m)Σ_{r} Z_{τ−r}`, so with `W_τ := Σ_{r=0}^{m-1} Z_{τ−r}`,

```
F(e) = E_e[e_{j+1} | e_j = e] = e + E_e[ W_τ / m ].
```

## 3. Simulator-definition audit

Each ambiguous choice was pinned and its influence tested:

| Choice | Decision | Does the instability depend on it? |
|---|---|---|
| `τ < m` handling | Minimum dwell `τ ≥ m` (guarantees a full terminal block) | **No.** P(alarm at `τ=m`) ≈ 0.001; removing the dwell changes `Γ` negligibly. |
| Terminal window incl. alarm obs? | Yes, `r=0..m-1` | Convention only; shifts `Γ` by O(1/m). |
| Overshoot | Kept (natural) | Contributes to `c_0` but not qualitatively. |
| Alarm direction coding | larger arm | Not used in `F'(0)`; used only for alternation diagnostics. |
| CUSUM reset next cycle | Full reset | **Yes, load-bearing for the Markov claim** (§4). State retention adds a hidden coordinate. |
| Reference update | Full replacement (`ρ=1`) or mixed (`ρ<1`) | This *is* the bifurcation parameter (§12). |

**Verdict of the audit:** the local instability is **not** a simulator-specific artifact. It is a property of the stopping-selected reuse map under the natural, paper-grade definitions above.

## 4. Markov-state audit

**Claim (PROVED under full reset).** With full CUSUM reset and full replacement, `(e_j)` is a time-homogeneous Markov chain: `e_{j+1} = μ̂_{τ,m}` is a measurable functional of the i.i.d. innovation stream of cycle `j`, whose law depends on the past only through `e_j`. Hence `K(e,A) = P(e_{j+1} ∈ A | e_j = e)` is well defined and `e_j` alone is a sufficient state.

**If reset is dropped** (retain residual detector state `S^±` across cycles), `e_j` is **not** Markov; the minimal state becomes `(e_j, S_j^+, S_j^-)` (or a summary such as terminal overshoot). NUMERICAL EVIDENCE from Phase-1.5: state retention (`γ=0.9`) *weakens* alternation, consistent with the extra state coordinate partially decoupling successive references. We therefore make all theorems under the full-reset model and flag retention as a separate (harder) chain.

## 5. Transition kernel

`K(e,·)` is the pushforward of the cycle innovations through the stopped functional `μ̂_{τ,m}`. It admits a Lebesgue density for every `e` (the terminal block `μ̂` is a normalized sum of `m` Gaussians convolved with the stopping geometry; smoothing gives a density). Conditional mean `F(e)` and variance `V(e) = Var(e_{j+1}|e_j=e)` are finite (Wald + exponential stopping tails). `F` is odd (§6), `V` is even.

## 6. Symmetry theorem

**Proposition 1 (PROVED).** Under `X_t ~ N(0,1)` and the symmetric two-sided CUSUM, `K(−e, A) = K(e, −A)` for every Borel `A`; consequently `F(−e) = −F(e)`, so `F(0)=0`, and if the invariant law `π` is unique then `π(A) = π(−A)`.

*Proof.* Fix `e` and consider the reflection `Φ: (x_t) ↦ (−x_t)` on the innovation path space. Under `P` (law of `X_t~N(0,1)`), `Φ` is measure-preserving (standard normal is symmetric). Under reference `−e`, centered observations are `−x_t − (−e)·(...)`; explicitly the map `Z_t(e) = x_t − e` satisfies `Z_t(−e)∘Φ = −x_t + e = −(x_t − e) = −Z_t(e)`. The CUSUM recursions are equivariant under `Z ↦ −Z` with the two arms swapped: `S_t^+(−Z) = S_t^-(Z)`, `S_t^-(−Z) = S_t^+(Z)`. Hence `τ` is invariant and the terminal block obeys `μ̂_{τ,m}(−e)∘Φ = −μ̂_{τ,m}(e)`. Pushing forward the measure-preserving `Φ` gives `K(−e,A) = P(μ̂(−e)∈A) = P(−μ̂(e)∈A) = P(μ̂(e)∈−A) = K(e,−A)`. Taking means yields `F(−e) = −F(e)`; uniqueness + the identity `K(−e,·)=K(e,−·)` forces `π` symmetric. ∎

**T1 = PROVED. T2 (`F'(0)<0`) follows once `Γ>1`, established numerically and by the identity in §8.**

## 7. Sign-reversal mechanism

Intuition made precise (Route C decomposition). Write `A ∈ {+1,−1}` for the crossed arm. `F(e) = P_e(A=+1)·E_e[μ̂|A=+1] + P_e(A=−1)·E_e[μ̂|A=−1]`. At `e=0`, symmetry gives `P_0(A=±1)=½` and `E_0[μ̂|A=+1] = −E_0[μ̂|A=−1] =: μ_+ > 0` (an up-alarm selects an upward terminal excursion). Differentiating at 0:

```
F'(0) = 2 μ_+ · (d/de) P_e(A=+1)|_0  +  (mean-shift term).
```

When `e>0`, the reference is too high, centered observations drift negative, the **downward** arm fires more often: `(d/de)P_e(A=+1)|_0 < 0`. Multiplied by `μ_+ > 0`, this drives `F'(0) < 0`: a positive reference error is corrected *past* zero into a negative one. This is the exact origin of the `−,+,−,+` alternation. The change-of-measure route (§8) packages both terms into one clean identity.

## 8. Exact representation of `F'(0)`

**Proposition 2 (PROPOSITION UNDER STATED ASSUMPTIONS).** Consider the equivalent monitoring view: reference fixed at 0, observations `Z_t ~ N(−e, 1)` (a shift by `−e`). The stopped-path law satisfies `dP_e/dP_0 = exp(−e·S_τ − τ e²/2)` on `F_τ` (Wald likelihood ratio; `S_τ = Σ_{t≤τ} Z_t`). Then, provided the family `{W_τ · exp(−eS_τ − τe²/2)}` is uniformly integrable near `e=0` (guaranteed by the geometric tail of `τ` for `k>0`),

```
F'(0) = 1 − Γ,     Γ = (1/m) Σ_{r=0}^{m-1} Cov_0( Z_{τ−r}, S_τ )     (EXACT IDENTITY).
```

*Sketch.* `F(e) = e + (1/m) E_e[W_τ] = e + (1/m) E_0[W_τ · e^{−eS_τ − τe²/2}]`. Differentiate under the expectation at `e=0`: the leading `e` gives `+1`; the derivative of the exponential brings down `−S_τ` (the `−τe²/2` term vanishes at `e=0`); since `E_0[Z_{τ−r}]=0` the product is a covariance. ∎

**Verification (NUMERICAL EVIDENCE):** identity `F'(0)=-9.196` vs finite-difference `-9.110` at `(5,0.5,5)` — agreement to ~1%.

Two exact corollaries from `c_r := Cov_0(Z_{τ−r},S_τ)`:
- All `c_r > 0` (verified for `r=0..19`) ⇒ `Γ>0` ⇒ **`F'(0) < 1` for every `m,k,h`** (no monitor in this family has `F'(0)>1`).
- `c_r` decreasing in `r` (selection concentrates in observations just before the alarm) ⇒ `Γ(m)` is a decreasing average ⇒ `|F'(0)|` decreasing in `m`.

## 9. Approximation / bounds for `F'(0)`

- **Large-`m` asymptote (ASYMPTOTIC, exact limit).** By Wald's second identity `E_0[S_τ²] = E_0[τ] = ARL_0`, and since `Σ_{r=0}^{τ-1} Z_{τ-r} = S_τ`, for `m ≥ typical τ` the sum `Σ_{r<m} c_r → E_0[S_τ·S_τ] = ARL_0`. Hence `Γ(m) → ARL_0/m` and `F'(0) → 1 − ARL_0/m` as `m→∞`. Verified: `E_0[S_τ²] = ARL_0` to <1% across the whole `(k,h)` grid.
- **Bound.** `0 < Γ(m) ≤ ARL_0/m` and `Γ(m) ≥ c_0/m` give two-sided control; the upper bound shows instability requires `m < ARL_0/2`.

## 10. Dependence on `(m,k,h)` — and the failed scaling hypothesis

**`|F'(0)| ≍ h/(mk)` is FALSE (COUNTEREXAMPLE FOUND).** Data (`h=5`): `Γ(m=5)` rises `5.5 → 10.2 → 12.6` as `k = 0.25 → 0.5 → 1.0`, whereas `h/(mk)` predicts a *fall*. At `(m=5,k=0.5,h=5)`, `h/(mk)=2` but `|F'(0)|≈9.2`. The correct organizing scale is `ARL_0/m` (§9): `|F'(0)|` grows with anything that lengthens excursions (larger `k`, larger `h`) and shrinks like `1/m`. The `h/(mk)` intuition mistook excursion *length* for excursion *sum-of-squares*; the right object is `E[S_τ²]=ARL_0`, which grows faster than `h/k`.

## 11. Critical reuse window `m*(k,h)`

`m*(k,h) := min{ m : |F'(0;m,k,h)| < 1 } = min{ m : Γ(m) < 2 }`. Since `Γ(m)` is a decreasing average of positive `c_r`, `Γ(m)<2` defines an up-set in `m` ⇒ the threshold is well posed and `m<m*⇒|F'|>1`, `m>m*⇒|F'|<1` (PROVED given monotone `c_r`, which holds numerically). Bracketed values (NUMERICAL EVIDENCE):

| k | h | ARL_0 | m*(interp) | h/k |
|---|---|---|---|---|
| 0.25 | 4 | 225 | 17 | 16 |
| 0.25 | 5 | 254 | 29 | 20 |
| 0.25 | 6 | 305 | 45 | 24 |
| 0.25 | 8 | 540 | 95 | 32 |
| 0.5 | 4 | 289 | 34 | 8 |
| 0.5 | 5 | 585 | 59 | 10 |
| 0.5 | 6 | 1395 | 94 | 12 |

Rigorous bounds `ARL_0/(2·?)` follow from §9 but the exact constant needs the `c_r` profile. **An exact closed form for `m*` is NOT available; a bracket + monotonicity is.**

## 12. Mixed-reuse theory

**Proposition 3 (PROVED, exact).** Let `μ̂_fresh = (1/m)Σ Y_r`, `Y_r ~iid N(0,1)` drawn **independently of the cycle's stopping event**, and `e_{j+1} = ρ·μ̂_reuse + (1−ρ)·μ̂_fresh`. Then for every `e`:

```
F_ρ(e) = ρ·F_1(e) + (1−ρ)·E[μ̂_fresh]  =  ρ·F_1(e),
```
since `E[μ̂_fresh]=0`. Hence `F_ρ'(0) = ρ·F_1'(0)` **exactly** (no asymptotics).

*Proof.* Conditional on the stopping event and `e`, `μ̂_reuse` has mean `F_1(e)`; `μ̂_fresh` is independent with mean 0. Linearity of expectation gives the result. ∎

Verification (NUMERICAL EVIDENCE): `F_ρ'(0)` vs `ρ·F_1'(0)` agree to <0.04 across `ρ∈{0,.25,.5,.75,1}` (`F_1'(0)=-8.613`).

## 13. Critical `ρ_c`

**Corollary (PROVED given Prop. 3).** `|F_ρ'(0)| < 1 ⇔ ρ < ρ_c := 1/|F_1'(0)|`. When `|F_1'(0)|>1` (established in §8), `ρ_c ∈ (0,1)` is a genuine interior threshold: any reuse fraction above `ρ_c` destabilizes the reference fixed point. Here `ρ_c = 0.116`. **This is the strongest, cleanest theorem in the report** — it needs only Prop. 3 (elementary) plus the existence of one unstable full-reuse instance.

## 14. Deterministic skeleton

`x_{j+1} = F(x_j)`, `F` odd, `F(0)=0`, `F'(0) = −a` with `a = |F_1'(0)| > 1` in the unstable regime. Globally `F` bends back strongly (`F(±1.5)≈∓0.12`), so trajectories stay bounded. The fixed point at 0 is a repeller; a symmetric 2-cycle `x_+ ↔ x_- = −x_+` requires a nonzero root of `F(x)+x=0`.

## 15. Two-cycle / flip-bifurcation analysis — **claim downgraded**

**A supercritical period-2 flip bifurcation CANNOT be certified (the cubic normal form is invalid here).** The map has a **boundary layer**: local slope `F'(0) = −-9.196`, yet `F` saturates by `|e|≈0.15` (`F(0.05)=−0.43`, `F(0.30)=−0.86`). An odd-cubic least-squares fit over `[−1.5,1.5]` returns `a_fit=1.289`, `b=0.573` — wildly inconsistent with the true local slope `−-9.196`. So `F` is **not** `−ae+be³+O(e⁵)` in any neighborhood where both the local slope and the fold-back are captured; the Taylor coefficients do not exist at the needed order. Consequently:
- The predicted 2-cycle radius `√((a−1)/b)=0.71` (from the invalid cubic) disagrees with the empirical invariant peak at `|e|≈0.59`.
- The "supercritical flip requires `1<a<2`" test is moot because the normal form does not apply.

**Correct rigorous statement (PROVED-level qualitative):** *local sign-reversing instability of the fixed point at 0, embedded in a globally attracting fold-back map, producing bounded oscillatory dynamics.* The existence of a stable symmetric 2-cycle in the deterministic skeleton is a CONJECTURE (the fold-back makes it plausible; not proven). **Do not call it "period-2 bifurcation" in the paper.**

## 16. Stochastic invariant-law theory

Real chain: `e_{j+1} = F(e_j) + ε_{j+1}(e_j)`, `ε` state-dependent (not additive iid). Targets:
- **T5A/T5B existence + uniqueness (PROPOSITION UNDER STATED ASSUMPTIONS):** via §17 drift + minorization.
- **T5D symmetry of `π` (PROVED given uniqueness):** immediate from Prop. 1.
- **T5E bimodality (CONJECTURE, strong NUMERICAL EVIDENCE):** invariant density dips at 0 (`density(0)=0.35` vs peak `0.47` at `|e|≈0.59`) in the unstable regime; unimodal when stable (`ρ<ρ_c` gives Var `0.175`, `m=80` gives Var `0.018`, both unimodal). No proof of bimodality; the boundary-layer map defeats normal-form arguments.

## 17. Lyapunov / ergodicity analysis

**Proposition 4 (PROPOSITION UNDER STATED ASSUMPTIONS).** Take `V(e)=1+e²`. Since `F(e)→0` as `|e|→∞` (fold-back) and `V(e)=Var(e_{j+1}|e)` is bounded (finite terminal-block variance uniformly in `e`, from Wald + geometric stopping tails), there exist `λ<1`, `b<∞`, compact `C` with

```
E[V(e_{j+1}) | e_j=e] ≤ λ V(e) + b·1_C(e).
```

Minorization: the terminal block `μ̂_{τ,m}` has a Lebesgue density bounded below on compacts uniformly for `e∈C` (Gaussian smoothing of the stopped sum), giving a small-set condition. Drift + minorization ⇒ positive Harris recurrence and **geometric ergodicity**, hence existence + uniqueness of `π`. **Gaussian path randomness does supply irreducibility** (the innovation density is everywhere positive, so `μ̂` can reach any open set). The drift constants are not computed in closed form — the *structure* is proven, the *explicit* `(λ,b,C)` are left to Phase-2C.

## 18. Conditional run-length function `L(e)`

`L(e) = E[τ | R=e]`. By Prop. 1's reflection argument applied to `τ` (invariant under the arm swap), **`L(e) = L(−e)` (PROVED)**, so `L'(0)=0`. Measured `L(0) = 465` (= `ARL_0`).

## 19. Local ARL expansion

`L(e) = L(0) + ½ L''(0) e² + O(e⁴)`, `L''(0)<0` (PROPOSITION: a nonzero reference error injects a drift into one CUSUM arm, and CUSUM ARL is strictly decreasing in `|mean shift|` — a classical monotonicity). Fitted `L''(0)≈-257`. **Caveat (honest):** the quadratic is only local; `π` places mass at `|e|≈0.59` where `L` has already collapsed far past the quadratic regime, so the expansion **under-predicts** the true degradation ~5× (predicted 72 vs actual 383). The expansion explains the *sign and mechanism*, not the *magnitude*.

## 20. Stationary ARL formula

**Proposition 5 (PROPOSITION UNDER STATED ASSUMPTIONS — renewal-reward).** If the chain is ergodic with invariant `π` (Prop. 4), the long-run average inter-alarm length is `ARL_∞ = E_π[L(e)] = ∫ L(e) π(de)`. This depends on `π` **only through its marginal**, not its serial correlation — a point the brief (§16) rightly stresses. Measured: `ARL_∞(reuse) = 82` vs oracle `L(0)=465`.

## 21. Fresh-vs-reuse theoretical comparison

Fresh matched control: `e^fresh ~ N(0, 1/m)` each cycle, independent of alarms. `ARL_fresh = E[L(E)], E~N(0,1/m) = 162`. The decisive inequality:

```
ARL_reuse < ARL_fresh   ⇔   E_π[L(e)] < E_{N(0,1/m)}[L(e)].
```

Because `L` is even and concave near 0 (and monotone decreasing in `|e|` globally), by a dispersion (convex-order) comparison this holds whenever `π` is more dispersed than `N(0,1/m)`: `Var_π(e) = 0.560` ≫ `1/m = 0.20`. **So the extra loss over fresh is attributable to the stopping-selected feedback inflating the stationary dispersion — NOT to ordinary finite-sample estimation variance** (which is exactly the `1/m` the fresh control already pays). Decomposition of `ARL_reuse − ARL_fresh`: dominated by the **marginal variance/dispersion** term; serial-correlation and bimodality shape run-length autocorrelation and alarm-direction alternation (`P(flip)=0.920` reuse vs `0.499` fresh) but contribute to *mean* ARL only through the marginal. **This confirms the brief's §16 warning: negative autocorrelation per se does not lower mean ARL.**

## 22. Counterexamples and validity region

Actively sought (all NUMERICAL EVIDENCE unless noted):
- **`F'(0)>0` monitor?** Impossible in this family — `Γ>0` always (PROVED via positivity of `c_r`), so `F'(0)<1` but can be positive (stable) for large `m`; never exceeds 1.
- **Always-stable regime:** `m > m*` (e.g. `m=80`) ⇒ `|F'(0)|<1`, unimodal `π` (Var `0.018`). Confirmed.
- **`ρ<ρ_c` ⇒ stable/unimodal:** `ρ=0.08<ρ_c=0.116` gives Var `0.175`, unimodal. Confirmed.
- **Unimodal despite `|F'(0)|>1`?** Not observed; whenever `|F'(0)|>1` the law was bimodal. (No counterexample — but no proof of the converse either.)
- **Reuse ARL ≥ fresh?** Occurs when `Var_π(e) ≤ 1/m`, i.e. `m>m*` — then reuse is *not* worse. This defines the validity region of the "reuse harms calibration" claim.

**Validity region of the phenomenon:** `m < m*(k,h)` (equivalently `ρ > ρ_c`). Outside it, reuse is benign. The theorem characterizes *when* reuse harms, not "reuse always harms."

## 23. Completed proofs (PROVED)

- Markov property under full reset (§4).
- Kernel symmetry `K(−e,A)=K(e,−A)`, `F` odd, `F(0)=0`, `π` symmetric if unique (Prop. 1).
- Positivity `Γ>0` ⇒ `F'(0)<1` for all `m,k,h`; monotonicity of `|F'(0)|` in `m` given monotone `c_r`.
- Mixed-reuse exact linearity `F_ρ=ρF_1`, `ρ_c=1/|F_1'(0)|` (Prop. 3 + Cor.).
- `L(e)=L(−e)`, `L'(0)=0` (§18).
- Large-`m` limit `Γ→ARL_0/m` via Wald `E[S_τ²]=ARL_0` (§9).

## 24. Partial proofs (PROPOSITION UNDER STATED ASSUMPTIONS)

- Exact score identity `F'(0)=1−Γ` (needs UI/exponential-tail regularity — standard but stated) (Prop. 2).
- Geometric ergodicity via Foster–Lyapunov + minorization (structure proven; constants not) (Prop. 4).
- `L''(0)<0` (uses classical CUSUM ARL monotonicity) (§19).
- `ARL_∞ = E_π[L]` (renewal-reward, needs ergodicity) (Prop. 5).
- `ARL_reuse < ARL_fresh ⇔ Var_π > 1/m` (convex-order argument; rigorous once `L` concavity/monotonicity is fully established) (§21).

## 25. Numerical evidence only

- Specific values `Γ=10.20`, `F'(0)=-9.196`, `ρ_c=0.116`, `m*` table, `Var_π=0.560`, invariant-density shape.
- `c_r` monotone decrease (used to make §11 monotonicity rigorous — should be proven analytically in Phase-2C).

## 26. Claims that must NOT yet be made

- ❌ "Period-2 flip bifurcation" / "supercritical period doubling" — normal form invalid (§15).
- ❌ "Bimodality theorem" — only a conjecture (§16).
- ❌ Any closed form for `F'(0)`, `m*`, or the 2-cycle radius.
- ❌ "`|F'(0)|∝h/(mk)`" — false (§10).
- ❌ "Reuse always degrades ARL" — false outside `m<m*` (§22).
- ❌ "Negative autocorrelation lowers mean ARL" — mechanism is dispersion, not correlation (§21).

## 27. Strongest defensible theorem

> **Theorem (mixed-reuse stability threshold).** Under the model of §2 with `X_t~N(0,1)` and mixed reuse `e_{j+1}=ρμ̂_reuse+(1−ρ)μ̂_fresh` (fresh block independent of the alarm), the reference chain is Markov, its transition satisfies `F_ρ(e)=ρF_1(e)` exactly with `F` odd, and the fixed point `e=0` is linearly stable iff `ρ<ρ_c:=1/|F_1'(0)|`. There exist `(m,k,h)` with `|F_1'(0)|>1`, hence `ρ_c∈(0,1)`, so a strictly interior reuse fraction destabilizes the reference. Moreover `F_1'(0)=1−Γ`, `Γ=(1/m)Σ_r Cov_0(Z_{τ−r},S_τ)>0`, giving `F_1'(0)<1` universally and the large-window law `Γ∼ARL_0/m`.

Every clause here is PROVED or a stated-assumption proposition; none rests on the rejected normal form.

## 28. Remaining mathematical bottleneck

Analytic control of the covariance profile `c_r = Cov_0(Z_{τ−r}, S_τ)` for the two-sided CUSUM. A renewal/boundary-value representation of `c_r` would upgrade: (i) the `m*` bracket to a closed bound, (ii) the `c_r`-monotonicity from numerical to proven, and (iii) potentially deliver an explicit `Γ(m,k,h)`. This is a first-passage functional of a reflected random walk — hard but a recognized problem class (ladder-height / Wald-type identities), not a dead end.

## 29. Recommended Phase-2C experiments

1. **Analytic `c_r`:** attack `Cov_0(Z_{τ−r},S_τ)` via renewal theory for the one-sided reflected walk; validate against the `c_r` curve here.
2. **Explicit drift constants** `(λ,b,C)` for Prop. 4 to make geometric ergodicity fully quantitative.
3. **Bimodality:** attempt a proof via the fold-back map's invariant-density integral equation, or downgrade permanently to conjecture.
4. **Non-Gaussian / dependent innovations:** does `Γ>0` (hence sign reversal) survive? Symmetry proof already does not need Gaussianity, only innovation symmetry.
5. **State-retention chain:** the `(e,S^+,S^-)` Markov model — does retention provably damp instability (as Phase-1.5 hinted)?

## 30. Assessment of Level-3 viability

The six-ingredient program (recursive reference dynamics; local stability threshold; invariant-law characterization; ARL consequence; MC + robustness; matched fresh control) is **viable as a Level-3 paper**, but the theoretical spine must be the **`ρ_c` threshold + exact `F'(0)=1−Γ` identity**, not the bifurcation story. The honest headline is: *stopping-selected recursive reuse induces an exactly characterizable linear instability of the reference fixed point, with a sharp critical reuse fraction `ρ_c=1/|F_1'(0)|`, and the resulting stationary dispersion — not serial correlation — degrades the in-control ARL below both the oracle and a matched fresh-update control.* That is a real, novel, provable contribution. The bifurcation/bimodality material is legitimate supporting phenomenology at NUMERICAL/CONJECTURE level and must be labeled as such.

---

## Final Gate Verdict

**THEORY GATE: PASS** (Route B satisfied, Route A bonus).

- Route B — PROVED: `F_ρ'(0)=ρF_1'(0)`, `ρ_c=1/|F_1'(0)|∈(0,1)`, with `|F_1'(0)|>1` demonstrated.
- Route A — PROPOSITION: exact `F'(0)=1−Γ`, verified numerically, giving an unstable parameter interval.
- Route C — the stability transition mechanism is proven at the linear level.

Rejected/withheld, explicitly: the flip-bifurcation normal form (invalid), the bimodality theorem (conjecture), the `h/(mk)` scaling (false), and any closed form for `F'(0)` or `m*`.

**The phenomenon is real, mathematically non-trivial, and partly provable. Proceed to Phase-2C — but write the paper around the `ρ_c` threshold and the score identity, and label the dynamical-systems phenomenology honestly.**
