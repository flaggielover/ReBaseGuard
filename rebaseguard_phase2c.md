# ReBaseGuard — Phase-2C Proof Closure Report

**Discipline enforced throughout:** PROVED · PROPOSITION UNDER STATED ASSUMPTIONS · CERTIFIED NUMERICAL PROOF · ASYMPTOTIC · NUMERICAL EVIDENCE · CONJECTURE · FALSE / WITHDRAWN. None of the last four is written as PROVED anywhere below.

---

## 1. Executive Verdict

**PROOF CLOSURE: CONDITIONAL.**

The exact score identity `F₁'(0) = 1 − Γ(m,k,h)` is now rigorously established (§4), with its regularity conditions stated explicitly rather than asserted. The mixed-reuse theorem `F_ρ'(0) = ρF₁'(0)` and the conditional threshold statement `ρ_c = 1/|F₁'(0)| ∈ (0,1) whenever |F₁'(0)|>1` are fully PROVED (§10–11) — as **conditional** theorems, valid regardless of whether the antecedent `Γ>2` is itself established.

**The antecedent `Γ(m,k,h) > 2` is NOT rigorously established this round.** I traced the obstruction to a precise root (§8): closing it in elementary closed form requires the exact conditional law of the CUSUM pre-crossing state (equivalently, the ladder-height/overshoot distribution of a negative-drift Gaussian random walk), which is a classical Wiener–Hopf boundary-value problem with **no known elementary closed form** — the sequential-analysis literature itself resorts to numerical Markov-chain discretization (Brook–Evans-type methods) or asymptotic (Siegmund corrected-diffusion) approximations, never exact formulas, for the *much simpler* quantity of plain CUSUM ARL. `Γ>2` is a strictly harder joint-moment functional of the same crossing structure. A genuinely certified (interval-arithmetic / validated-quadrature) numerical proof was not attempted this round because building one honestly requires machinery (a rigorous discretization-error bound for a 2D reflected-walk kernel) beyond what the stated budget permits; attempting a shortcut would risk a false CERTIFIED label, which I will not do.

An **Escalation Package** (§17) is therefore issued, per the mandatory stop rule.

---

## 2. Corrected Mathematical Model

Fix the reference-error view: monitor observes `Z_t = X_t − e`, `X_t ~iid N(0,1)`, so `Z_t ~iid N(−e,1)` under the law `Q_e` (write `Q_0 = P_0` for the null, `Z_t~N(0,1)`). Symmetric two-sided CUSUM:
```
S_t^+ = max(0, S_{t-1}^+ + Z_t − k),   S_t^- = max(0, S_{t-1}^- − Z_t − k),   S_0^± = 0.
```
**Terminal-window formulation (§3 resolves this): minimum dwell**, `τ = τ_m = inf{t ≥ m : max(S_t^+,S_t^-) ≥ h}`, terminal block `W_{τ,m} = Σ_{r=0}^{m-1} Z_{τ-r}` (last `m` observations, alarm included), `T_τ = Σ_{t=1}^τ Z_t`. Full replacement `e_{j+1} = e + W_{τ,m}/m`, full CUSUM reset each cycle.

## 3. Regularity Conditions / Terminal-Window Resolution

**Choice: minimum-dwell (A) for `m≥2`; for the CORE proof target, use `m=1`, which sidesteps the issue entirely** (`τ ≥ 1` always holds, no dwell constraint is active). This is the cleanest possible formulation for attacking `Γ>2` and is why §5–§9 below work with `m=1`.

**Is the instability an artifact of forcing `τ≥m`?** No — this was already checked (Phase-2B): `P(τ=m)≈0.001` at `(m,k,h)=(5,0.5,5)`, so the dwell constraint binds negligibly. At `m=1` the question is moot by construction. **Verdict: NOT an artifact (confirmed, not merely asserted).**

Standing regularity assumptions used throughout (stated explicitly, not swept into "by change of measure"):
- **(R1)** `k>0`, `h<∞` ⇒ `τ<∞` a.s. under `Q_e` for `e` in a neighborhood of 0 (standard: the reflected chain has a uniformly-positive-probability escape to `h` from any state within a bounded number of steps, giving a geometric tail).
- **(R2)** `τ` has finite exponential moments: `E_0[e^{cτ}]<∞` for some `c>0`. This follows from (R1) by a standard regeneration argument (the chain restarts at every visit to a bounded neighborhood of 0, and each regeneration cycle has uniformly bounded length tail).
- **(R3)** Consequently all polynomial moments of `τ`, and (via `|T_t|≤`sum of sub-Gaussian increments) of `T_τ`, `W_{τ,m}`, are finite.

## 4. Exact Score Identity — audited proof

**Proposition 1 (PROPOSITION UNDER STATED ASSUMPTIONS R1–R3).**
```
F₁'(0) = 1 − Γ(m,k,h),     Γ(m,k,h) = (1/m) Σ_{r=0}^{m-1} Cov_0(Z_{τ-r}, T_τ).
```

*Proof.* The likelihood ratio of `Q_e` w.r.t. `P_0` on `F_t` is `M_t(e) := dQ_e/dP_0|_{F_t} = Π_{s≤t} φ(Z_s+e)/φ(Z_s) = exp(−e T_t − t e²/2)` (elementary Gaussian density ratio). `M_t(e)` is a `P_0`-martingale. **Optional stopping at `τ`:** `E_{Q_e}[g(Z_{1:τ})] = E_0[g(Z_{1:τ}) M_τ(e)]` for any `F_τ`-measurable `g` with `E_0[|g|M_τ(e)]<∞`, valid because `M_{t∧τ}(e)` is uniformly integrable — this is where (R2) is load-bearing: `E_0[M_τ(e)]=1` (no loss of mass) follows from `τ<∞` a.s. (R1) plus a uniform bound `M_{t∧τ}(e) ≤ e^{|e|·|T_{t∧τ}|}` dominated in `L¹` using the exponential-moment control of `τ` (R2) for `|e|` small enough that `e²/2 < c`. Apply with `g = W_{τ,m}`:
```
F₁(e) = e + (1/m) E_{Q_e}[W_{τ,m}] = e + (1/m) E_0[ W_{τ,m} · exp(−eT_τ − τe²/2) ].
```
**Differentiation under the expectation:** `∂_e[W_{τ,m} e^{-eT_τ-τe²/2}]|_{e=0} = −W_{τ,m}T_τ`. Dominated convergence for the derivative (interchanging `d/de` and `E_0`) requires a uniform-in-`e∈[-δ,δ]` integrable envelope for `|W_{τ,m}(T_τ+eτ)|e^{-eT_τ-τe²/2}`; this is furnished by (R2)+(R3) via a Cauchy–Schwarz split (`W_{τ,m}T_τ` has finite 4th moment by R3, and the exponential factor is dominated by `e^{δ|T_τ|+δ²τ/2}`, itself integrable against any polynomial by R2's exponential-moment bound for `δ` small). Hence
```
F₁'(0) = 1 − (1/m) E_0[W_{τ,m} T_τ].
```
`E_0[W_{τ,m}]=0` and `E_0[T_τ]=0` **both by the reflection symmetry `X↦−X`** (Phase-2B Prop. 1; NOT by Wald — see §9 for why Wald does not directly apply to `W_{τ,m}`), so `(1/m)E_0[W_{τ,m}T_τ] = (1/m)Cov_0(W_{τ,m},T_τ) = Γ` by bilinearity of covariance and `Cov(Σ_r Z_{τ-r}, T_τ)=Σ_r Cov(Z_{τ-r},T_τ)`. ∎

**This is a strictly more careful derivation than Phase-2B's**, with the regularity conditions (R1–R3) named explicitly rather than invoked as "by change of measure." No correction to the identity itself was needed — it survives the audit intact.

## 5. Simplest-Case Analysis (`m=1`)

At `m=1`: `Γ(1,k,h) = Cov_0(Z_τ,T_τ) = E_0[Z_τT_τ]` (means vanish, §4). By the arm-symmetry decomposition (reflection swaps arms and negates `Z,T`, leaves `Z_τT_τ` invariant):
```
Γ(1,k,h) = 2·E_0[Z_τT_τ ; A=+]     (PROVED reduction).
```
**Elementary partial bound (PROVED).** On `A=+`, the crossing condition `S_{τ-1}^+ + Z_τ − k ≥ h` with `S_{τ-1}^+ < h` gives `Z_τ > k` a.s. on `A=+`. Hence `E_0[Z_τ² | A=+] ≥ k²`, so (by symmetry) `E_0[Z_τ²] ≥ k²` unconditionally. Writing `Z_τT_τ = Z_τ² + Z_τT_{τ-1}`:
```
Γ(1) ≥ k² + E_0[Z_τT_{τ-1}]     (PROVED, but the second term's sign is NOT established — see §7).
```
For `k=0.5` this gives only `Γ(1)≥0.25` — far short of 2. **The elementary bound alone cannot close the gap;** the bulk of `Γ` must come from the cross-term / conditional structure, which requires the pre-crossing-state distribution (§8).

**Diagnostic only (NUMERICAL EVIDENCE, single configuration, moderate sample, not a sweep):** at `(k,h)=(0.5,5)`, `m=1`: `E_0[T_τ]=−0.009`, `E_0[Z_τ]=−0.002` (both ≈0, consistent with the proved symmetry), `E_0[T_τ²]=465.3` vs `E_0[τ]=465.4` (Wald's second identity confirmed to <0.1%, validating R1–R3 empirically), and `Γ(1) ≈ 15.8` — well above 2, consistent with Phase-2B's `m=5` value (`Γ(5)≈10.2`). This is **evidence, not proof**, of the antecedent.

## 6. Terminal-Excursion Argument

Let `ν = max{t<τ : S_t^+=0}` (last reset before the successful excursion). On the excursion `(ν,τ]`: `S_t^+ = U_t−U_ν` where `U_t=T_t−kt`, giving at `τ`: `Σ_{s=ν+1}^τ Z_s = h+O+k(τ−ν)`, `O≥0` the overshoot. This gives `T_τ = T_ν + h + O + k(τ−ν) ≥ T_ν + h` (PROVED, elementary).

**A tempting shortcut, tried and found FALSE — reported explicitly per the brief's discipline.** I initially attempted the claim "`T_ν = kν` exactly" (i.e., that `S^+` resets exactly at 0 imply the *pre-history sum* also resets to a clean multiple of `k`). This is **wrong**: `S_t^+=0` means `U_t` is a *new running minimum*, not that `U_t=0`. Since `U_t` has drift `−k<0`, `U_t→−∞` a.s., so `U_ν` (hence `T_ν=U_ν+kν`) drifts to `−∞` in absolute terms even though `T_ν` itself is a driftless martingale (E[T_ν]=0 is not violated, since ν is random and grows). **The correct structural fact is weaker:** the sequence of reset times `ν` are exactly the *strict descending ladder epochs* of the walk `U_t`, and by classical fluctuation theory the ladder heights `(U_{ν_i}−U_{ν_{i-1}})_i` are i.i.d. — but their common law has no elementary closed form for Gaussian increments (§8). **FALSE / WITHDRAWN:** "`T_ν=kν`"; **PROVED (standard fluctuation theory):** the regenerative/ladder structure exists, but is not elementarily solvable.

## 7. Covariance/Energy Decomposition

`Γ(m) = (1/m)E_0[W_{τ,m}²] + (1/m)E_0[W_{τ,m}R_{τ,m}]`, `T_τ=W_{τ,m}+R_{τ,m}`. **`E_0[W_{τ,m}R_{τ,m}]≥0` is NOT proved and I do not assume it.** No sign argument for this cross-term was found this round: `R_{τ,m}=T_{τ-m}` is the pre-window path sum, which (as §6 shows) is governed by the same ladder-height law as `T_ν`, with no elementary handle on its correlation with the terminal block beyond what's already captured in `Cov(Z_{τ-r},T_τ)` directly. **This sub-question is left OPEN**, not asserted either way — flagged as part of the escalation lemma.

## 8. Proof Attempts for `Γ>2` — where each fails

| Route | Attempt | Where it stops |
|---|---|---|
| **1. Direct analytic inequality** | Elementary truncation bound `Z_τ>k` on `A=+` (§5) | Gives only `Γ≥k²≈0.25`; the rest requires the conditional law of `S_{τ-1}^+` (the pre-jump state), which needs the crossing/overshoot distribution — not elementary. |
| **1b. Ladder-height decomposition** | Express `T_ν` via i.i.d. descending ladder heights of `U_t=T_t−kt` (§6) | Ladder-height law for Gaussian-minus-drift increments has no elementary closed form; requires Wiener–Hopf factorization of the characteristic function, invertible only numerically (Fourier inversion) or asymptotically. |
| **2. Renewal/integral-equation** | Formulate `Γ` as a functional of the stationary/quasi-stationary pre-crossing density on `[0,h)`, satisfying a Lindley-type (Fredholm) integral equation with Gaussian kernel | Existence/uniqueness of the functional solution is standard (compact positive operator, Krein–Rutman), but the equation has **no closed-form solution**; solving it requires numerical discretization — exactly the "Brook–Evans" Markov-chain method used throughout the SPC literature for plain CUSUM ARL, itself never closed-form. |
| **3. Certified numerical proof** | Considered: discretize the 2D `(S^+,S^-)` state on a fine grid, solve the linear system, bound discretization error via a Lipschitz/monotonicity argument on the Gaussian transition kernel | **Not attempted this round.** A genuine error certification (bounding the discretization bias on a joint 2D reflected-walk kernel with absorbing boundary) is a substantial undertaking — comparable in effort to a small numerical-analysis paper — and is explicitly outside this round's budget. Doing it hastily would risk a false "CERTIFIED" label, which the brief explicitly forbids. |

**Conclusion: the obstruction is real and specific, not a failure of effort.** `Γ(m,k,h)>2` reduces to a joint-moment functional of the CUSUM overshoot/ladder structure that is a recognized hard problem in its own right — the same family of problems (Wiener–Hopf boundary crossing for Gaussian walks) that the sequential-analysis literature has never closed in elementary form even for the *simpler* quantity of plain ARL.

## 9. Rigorous Instability Result

**What IS proved:** `F₁'(0) = 1−Γ` (§4, exact identity, stated regularity). `Γ(m,k,h) ≥ k²` for `m=1` (§5, elementary). `Γ(m,k,h)>0` for all `m,k,h` (Phase-2B, from `Cov_0(Z_{τ-r},T_τ)>0`, itself a consequence of the same monotone-selection intuition but numerically verified, not analytically proved either — flagged here for completeness: **this too is NUMERICAL EVIDENCE**, not proved, on reflection, since a rigorous sign proof of `Cov_0(Z_{τ-r},T_τ)>0` for every `r` was not carried out in Phase-2B beyond simulation).

**What is NOT proved:** `Γ>1` (sign reversal `F₁'(0)<0`) and `Γ>2` (instability `F₁'(0)<-1`) both remain **NUMERICAL EVIDENCE ONLY**, consistently across `m=1` (`Γ≈15.8`) and `m=5` (`Γ≈10.2`, Phase-2B) at `(k,h)=(0.5,5)`.

## 10. Mixed-Reuse Theorem

**Proposition 2 (PROVED, unconditionally, independent of §8's open question).** `e_{j+1}=ρ·μ̂_{reuse}+(1−ρ)·μ̂_{fresh}`, fresh block independent of the stopping event with `E[μ̂_{fresh}]=0`. Then for every `e`: `F_ρ(e) = E[ρμ̂_{reuse}+(1−ρ)μ̂_{fresh} | e] = ρF₁(e) + (1−ρ)·0 = ρF₁(e)` by linearity of conditional expectation and independence. Differentiating: `F_ρ'(0)=ρF₁'(0)`. *No regularity beyond finiteness of `F₁'(0)` is needed — this holds regardless of whether `Γ>2`.*

## 11. Critical Reuse Threshold `ρ_c`

**Proposition 3 (PROVED, conditional).** *If* `F₁'(0)<−1` (equivalently `Γ>2`, §9), *then* `ρ_c := 1/|F₁'(0)| ∈ (0,1)` and:
```
ρ<ρ_c  ⇒  |F_ρ'(0)|<1   (local stability of e=0),
ρ>ρ_c  ⇒  |F_ρ'(0)|>1   (local instability of e=0).
```
*Proof.* `|F_ρ'(0)|=ρ|F₁'(0)|` (Prop. 2) is strictly increasing and continuous in `ρ∈[0,1]`, `=0` at `ρ=0`, `=|F₁'(0)|>1` at `ρ=1`; by the intermediate value theorem it crosses 1 exactly once, at `ρ_c=1/|F₁'(0)|`, and since `|F₁'(0)|>1` this lies strictly inside `(0,1)`. Monotonicity gives the two implications directly. ∎

**Call this what it is: "local sign-reversing instability," not "period-doubling bifurcation."** No global dynamical-systems hypothesis (normal-form validity, fold-back structure) is invoked or needed for this linear-stability statement, and none is claimed.

**This theorem is unconditionally correct as an implication; its practical force depends entirely on the unresolved antecedent from §8.**

## 12. ARL Claim Audit

The Phase-2B claim `ARL_reuse < ARL_fresh ⟺ Var_π(e) > 1/m` is **FALSE / WITHDRAWN as a general biconditional.** Variance ordering of `π` vs `N(0,1/m)` does **not** imply expectation ordering of `L(e)` for an arbitrary even function `L`. A sufficient condition would require `π` to dominate `N(0,1/m)` in the **convex order** (a strictly stronger condition than matching-mean variance comparison) *and* `L` to be **concave over the full support** of both distributions. The second condition is almost certainly false in general: `L(e)` is bounded below and flattens for large `|e|` (a floor near the minimum achievable run length), which forces `L` to be convex, not concave, in its tails — directly contradicting global concavity. **Corrected, weaker statement:** `ARL_reuse < ARL_fresh` for a *specific* configuration is a NUMERICAL EVIDENCE finding (verified: 82 vs 162 at `(m,k,h)=(5,0.5,5)`, Phase-2B), not a consequence of the variance comparison alone. Establishing it in general would require either the convex-order relationship or a direct comparison of `E_π[L]` vs `E_{fresh}[L]`, neither attempted here (out of scope per the budget instruction).

## 13. Statements Corrected or Withdrawn from Phase-2B

- **WITHDRAWN implicitly-assumed step:** `T_ν=kν` at CUSUM reset times — false; corrected to the ladder-height structure (§6).
- **WITHDRAWN (general form):** `ARL_reuse<ARL_fresh ⟺ Var_π>1/m` — false as a biconditional; downgraded to configuration-specific numerical evidence (§12).
- **DOWNGRADED:** `Cov_0(Z_{τ-r},T_τ)>0` for all `r` — Phase-2B treated this as established; on this audit it is NUMERICAL EVIDENCE, not proved (§9).
- **REAFFIRMED, more carefully:** the score identity itself, now with explicit regularity conditions (§4) rather than "by change of measure."
- **REAFFIRMED, unconditionally:** the mixed-reuse linearity and conditional `ρ_c` theorem (§10–11) — these were already sound in Phase-2B and survive the audit intact.

## 14. Strongest Defensible Theorem

> **Theorem.** Under the model of §2, `F_ρ'(0)=ρ·F₁'(0)` for all `ρ∈[0,1]` (PROVED, unconditional), where `F₁'(0)=1−Γ(m,k,h)` and `Γ(m,k,h)=(1/m)Σ_r Cov_0(Z_{τ-r},T_τ)` (PROVED identity, under stated exponential-moment regularity). Consequently, **if** `Γ(m,k,h)>2` for some `(m,k,h)` — for which `Γ(1,0.5,5)≈15.8` and `Γ(5,0.5,5)≈10.2` are strong, consistent, reproducible numerical evidence at two different window sizes — **then** `ρ_c=1/|F₁'(0)|` is a well-defined, strictly interior (`∈(0,1)`) critical reuse fraction below which the reference fixed point is linearly stable and above which it is not.

This is the maximal claim defensible today: a clean, unconditionally proved *reduction* (Γ controls everything) plus strong, reproducible, but not yet certified numerical support for the one open antecedent.

## 15. Remaining Unproved Lemmas

1. **[CENTRAL]** `Γ(m,k,h) > 2` for some fixed natural `(m,k,h)` — reduces to the pre-crossing/overshoot law of a negative-drift Gaussian random walk (Wiener–Hopf boundary problem); no elementary closed form found; certified numerics not attempted (budget).
2. `Cov_0(Z_{τ-r},T_τ)>0` for each `r` (used implicitly to argue `Γ` is "obviously" positive) — currently numerical only.
3. Sign of `E_0[W_{τ,m}R_{τ,m}]` (§7) — open in either direction.
4. Convex-order (or equivalent) relationship between `π` and `N(0,1/m)` needed to make the ARL comparison rigorous (§12) — not investigated.

## 16. Level-3 Theory Status

Unchanged in substance from Phase-2B's assessment but now on firmer footing for the parts that are actually proved: the reduction chain `Γ→F₁'(0)→ρ_c` is a genuine, non-trivial, provable theoretical spine (§10–11, §14), sufficient to anchor a Level-3 contribution **once the single lemma in §17 is closed** — by a stronger analytic effort, a validated numerical proof, or (if it fails) a demonstration that `Γ≤2` always, which would itself be a valuable negative result forcing the paper to reposition around the still-true conditional theorem and the (still real, still reproducible) numerical phenomenon.

## 17. Escalation Package

**1. Strongest exact identity already proved:**
```
F₁'(0) = 1 − Γ(m,k,h),   Γ = (1/m)Σ_{r=0}^{m-1} Cov_0(Z_{τ-r}, T_τ),   T_τ=Σ_{t≤τ}Z_t,
```
under regularity (R1–R3): `k>0`, finite exponential moments of `τ` (§4), for two-sided CUSUM on `Z_t~iid N(0,1)`, minimum-dwell stopping `τ=inf{t≥m: max(S_t^+,S_t^-)≥h}`.

**2. Precise unresolved lemma:**
```
Prove or disprove:  Γ(1, 0.5, 5) = E_0[Z_τ T_τ] > 2
for τ = inf{t≥1 : max(S_t^+,S_t^-) ≥ 5}, S_t^± as in §2 with k=0.5.
```
(`m=1` chosen to eliminate all terminal-window ambiguity; `(k,h)=(0.5,5)` chosen as the configuration used throughout Phase-2B/2C with `ARL_0≈465`.)

**3. All assumptions:** `Z_t~iid N(0,1)` under `P_0`; `S_0^±=0`; ties (`S_t^+=S_t^-≥h` simultaneously) have probability 0 (a.s. true, continuous distribution).

**4. Most promising proof route:** Wiener–Hopf factorization of the characteristic function of the driftless-then-tilted walk `U_t=T_t−kt` to obtain the Laplace transform of the ladder-height distribution at the first ascending ladder epoch exceeding `h`; alternatively, a validated (interval-arithmetic) numerical solution of the Fredholm integral equation for the pre-crossing density on `[0,h)`, with a rigorously bounded discretization error (e.g., via a Lipschitz-modulus argument on the Gaussian transition kernel and Banach fixed-point contraction bound).

**5. Failed attempts and why:**
- Elementary truncation (`Z_τ>k` a.s. on `A=+`) gives only `Γ≥k²=0.25` — far short.
- Assuming `T_ν=kν` at CUSUM resets — **false** (conflates `S=0` with `U=0`; `U` drifts to `−∞`).
- Assuming `E[W_{τ,m}R_{τ,m}]≥0` — unproved either way, not usable.

**6. Numerical evidence relevant to the lemma:** `Γ(1,0.5,5)≈15.8` (diagnostic MC, `n=3×10^5`, `E[T_τ²]=465.3` vs `E[τ]=465.4` confirming Wald's identity to <0.1% and validating the simulator/regularity assumptions).

**7. Minimal question for a stronger reasoning model:** *Derive, via Wiener–Hopf factorization or an equivalent exact method, the joint moment `E_0[Z_τ T_τ]` for the two-sided CUSUM first-passage time `τ=inf{t≥1: max(S_t^+,S_t^-)≥h}` with reference `k` and threshold `h`, `Z_t~iid N(0,1)`, `S_0^±=0`; evaluate (or rigorously bound) it at `k=0.5, h=5`, and determine whether it exceeds `2`.*

**8. Self-contained prompt for escalation:**

> Let `Z_1,Z_2,... ~ iid N(0,1)`. Define `S_0^+=S_0^-=0`, `S_t^+=max(0,S_{t-1}^++Z_t-k)`, `S_t^-=max(0,S_{t-1}^--Z_t-k)`, and `τ=inf{t≥1: max(S_t^+,S_t^-)≥h}` for fixed `k=0.5, h=5`. Let `T_t=Σ_{s=1}^t Z_s`. Prove or disprove, with a rigorous derivation (closed-form, transform-based, or a certified numerical bound with explicit error control — not a Monte Carlo estimate): `E[Z_τ T_τ] > 2`. Background: `τ` is the first-passage time of a two-sided CUSUM chart; by symmetry `E[Z_τ]=E[T_τ]=0`, and Wald's identity gives `E[T_τ²]=E[τ]`. The quantity is known numerically (Monte Carlo, ~15.8) but no rigorous proof of the inequality is available. A full proof of the biconditional stability threshold for a related recursive reference-updating dynamical system depends on this single inequality.

---

## Gate Decision

**PROOF CLOSURE: CONDITIONAL.**

The score identity and mixed-reuse/`ρ_c` theorem are rigorous. The instability antecedent `Γ>2` relies on ordinary (diagnostic) numerical evidence, consistently reproduced across two window sizes, but not yet proved or certified. Per the budget-aware stop rule, work stops here with the Escalation Package above rather than continuing into secondary topics.
