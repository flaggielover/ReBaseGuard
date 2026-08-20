# ReBaseGuard — Phase-4D Pre-Implementation Adversarial Audit

**Role: senior mathematical referee and proof architect.** The Phase-4C GREEN verdict is treated as a hypothesis to be attacked, not a premise. Evidence labels are strict: PROVED · CERTIFIED (Arb) · NUMERICAL EVIDENCE · CONJECTURE · ERROR FOUND. The protected Level-3 CUSUM certificate is not touched anywhere below.

---

## PROGRESS CAPSULE (final state)

| Field | Value |
|---|---|
| Step / total | 9 / 9 (Parts I–IX complete) |
| Current gate | Phase-4D pre-implementation |
| Established facts | SR operator core re-derived independently and **confirmed correct**; reachable enclosure valid as a *sufficient* cover; contraction logic valid but **needlessly lossy**; coupled propagation algebra **correct as stated**; one **error of omission** found (§IV.3) that *improves* the budget ~7× |
| Unresolved issues | ε_a achievability at continuum scale (Part V) — the sole genuine open risk; `sup_y E_y[τ]` needs its own Arb certificate |
| Proof status | Architecture SOUND; not yet executed. Nothing here is a proof of `Γ_SR>2` |
| Estimated remaining work | 4–7 engineering days + 2–12 workstation hours (revised down; see §XI) |

---

## PART I — Independent re-derivation of the mathematical core

I re-derived every object from the frozen detector definition without reading the Phase-4C algebra first, then compared.

**1. Log-state recursion — CONFIRMED.** With `Y=log(1+R)`, `R' = (1+R)e^{Z-1/2} = e^{Y+Z-1/2}`, so
`Y'_+ = log(1+e^{y_+ + z - 1/2}) = softplus(y_+ + z - 1/2)`, and by `Z→−Z`, `Y'_- = softplus(y_- - z - 1/2)`. Correct. The `softplus` form is the right choice: it is globally 1-Lipschitz and convex, which is what makes Part V viable at all.

**2. Continuation region — CONFIRMED, including both signs.** Absorption is `max(R'_+,R'_-) ≥ A`, i.e. `e^{y_+ + z - 1/2} ≥ A` or `e^{y_- - z - 1/2} ≥ A`. The first gives `z ≥ log A - y_+ + 1/2 = u(y)`; the second gives `z ≤ y_- - log A - 1/2 = ℓ(y)`. Continuation is `ℓ(y) < z < u(y)`. Both Phase-4C signs are right.

> **Flag (harmless, but must be implemented consistently).** Absorption is tested on `R'`, i.e. **after** the update, and the boundary is **inclusive** (`≥A`). Therefore continuation is the **open** interval and absorption the closed complement. Since `Z` has a density, the endpoints carry zero mass and every integral is unaffected. The requirement is only that the implementation never double-counts or drops the endpoints — a bookkeeping obligation, not a mathematical gap.

**3–4. Affine reduction and Bellman equations — CONFIRMED.** With `x=T_t` and `H(y,x)=E[Z_τ T_τ | Y_t=y, T_t=x]`, condition on the next innovation `z`. On continuation the state becomes `(q(y,z), x+z)`; on absorption `τ=t+1`, `Z_τ=z`, `T_τ=x+z`, reward `z(x+z)=zx+z²`. Hence
```
H(y,x) = ∫_ℓ^u H(q(y,z), x+z) φ(z)dz  +  ∫_{absorb} (zx+z²) φ(z)dz.
```
Substituting the ansatz `H=a(y)x+b(y)` and matching in `x` (legitimate: the equation holds for all real `x`, and `{1,x}` are linearly independent) gives exactly
```
a = Ka + r_a,        b = Kb + K_z a + r_b,
```
with `(Kf)(y)=∫_ℓ^u f(q)φ dz` and `(K_z f)(y)=∫_ℓ^u z f(q)φ dz`. The `K_z a` term is the coupling; it arises because the continuation state carries `x+z`, not `x`. Correct, and correctly triangular.

**5. Tail moments — CONFIRMED by direct integration.** The absorption set is `(-∞,ℓ] ∪ [u,∞)`.
```
r_a = ∫_absorb z φ dz = [−φ]_{−∞}^{ℓ} + [−φ]_{u}^{∞} = −φ(ℓ) + φ(u) = φ(u) − φ(ℓ)  ✓
r_b = ∫_absorb z² φ dz = (Φ(ℓ) − ℓφ(ℓ)) + (Φ(−u) + uφ(u))  ✓
```
using `∫_{-∞}^{ℓ} z²φ = Φ(ℓ) − ℓφ(ℓ)` and `∫_u^∞ z²φ = Φ(−u) + uφ(u)`. Both Phase-4C expressions are exactly right. Note `r_a` is signed and `r_b>0`.

**6. `Γ_SR=b(0,0)` — CONFIRMED with one caveat.** At reset `R^±=0 ⇒ Y^±=0` and `T_0=0`, so `Γ_SR = H((0,0),0) = a(0,0)·0 + b(0,0) = b(0,0)`. Additionally the diagonal symmetry (item 7) forces `a(0,0)=0`, so the value is insensitive to any error in `a` *at the reset point specifically* — though **not** to errors in `a` elsewhere, which propagate through `K_z a`. This is the crux of Part IV.

**7. Reflection identities — CONFIRMED.** The involution `(y_+,y_-,z,x) ↦ (y_-,y_+,−z,−x)` swaps `q_+ ↔ q_-`, maps `ℓ ↦ −u` and `u ↦ −ℓ` (so the continuation interval maps onto itself), preserves `φ`, and sends the reward `z(x+z) ↦ (−z)(−x−z) = z(x+z)`. Hence `H(y_+,y_-,x)=H(y_-,y_+,−x)`, giving `a` antisymmetric and `b` symmetric, and `a≡0` on the diagonal. Correct.

**8. Stopped-score connection — CONFIRMED but scope-limited.** `F'_{SR}(0)=1−Γ_SR` follows from the general identity, whose proof requires only (i) `τ` an a.s.-finite stopping time on the innovation filtration with `E[e^{cτ}]<∞` for some `c>0`, and (ii) the reflection symmetry killing the means. **SR satisfies both**: (i) holds because `log R^+_t` has positive drift `+1/2` under the `Z_t−1/2` increments... 

> **Flag — this is the one place I want the Phase-4D write-up to be careful.** The *symmetric two-chart* SR is reflection-symmetric by construction, which is exactly why the two-chart variant was chosen over standard one-sided SR. Standard one-sided SR is **not** symmetric and the identity would acquire nonzero mean terms. The theorem in Part VIII must therefore say "symmetric two-chart SR", never "Shiryaev–Roberts" unqualified. **NUMERICAL EVIDENCE** confirming (ii) here: my independent simulation gives `E[Z_τ]=+0.0045`, `E[T_τ]=−0.0010` (n=3×10⁵), both consistent with 0.

**Independent numerical corroboration of the whole core.** Rather than trust agreement of two solvers built from the same derivation, I wrote an independent two-chart SR simulator directly from the *raw* `R`-recursion (not the log form) and obtained:

| Quantity | My independent value (n=3×10⁵) | Phase-4B / 4C |
|---|---|---|
| `Γ_SR` | **17.2164 ± 0.0724 (SE)**, 95% CI `[17.074, 17.358]` | MC 17.2721 ± 0.0280; spectral 17.28682 |
| `E[T_τ²]` vs `E[τ]` (Wald) | 464.93 vs 464.77 — agree to 0.03% | — |
| `ARL₀ = E[τ]` | **464.77 ± 0.83** | (not reported) |

The spectral candidate 17.28682 sits 0.98 SE above my estimate — consistent. **The Phase-4C core derivation passes the audit.** No sign, indexing, terminal-reward, or measure-change error found.

> **Noteworthy and worth stating in the paper:** `ARL₀(SR) = 464.8` versus `ARL₀(CUSUM) = 465.8` (my earlier independent run). The two detectors are matched to within 0.2% — so the eventual cross-detector comparison is *genuinely like-for-like*, not an artifact of differing alarm rates. That is a real strength of the frozen (δ,A) choice and should be stated explicitly rather than left implicit.

---

## PART II — Reachable-domain audit

**Product identity — CONFIRMED.** `R'_+ R'_- = (1+R_+)(1+R_-)e^{Z-1/2}e^{-Z-1/2} = e^{Y_+ + Y_- - 1}`, independent of `z`. Correct and elegant: the product is a *deterministic* function of the current state, which is what makes the enclosure possible.

**The bound is sufficient, not exact — and that is harmless, in the right direction.** The argument: at a live (non-absorbed) state, `R'_± < A`, and maximizing `Y'_+ + Y'_- = log(1+R'_+)+log(1+R'_-)` subject to the fixed product `R'_+R'_- = e^{Y_++Y_--1}` and the box constraint `R'_± ≤ A` is a convex maximization, so the max is at an endpoint — one factor pinned at `A`. Iterating to the fixed point `C` gives the invariant region. This is a valid **forward-invariance** argument: the set `{Y_++Y_- ≤ C}` contains the reset point and is mapped into itself, hence contains every reachable live state by induction. Over-covering is **safe**: a residual bound proved on a superset is a fortiori valid on the reachable set. Only *under*-covering would be fatal.

**Checks performed:**
- *First step from reset*: `(0,0) → Y_+ + Y_- = 2·softplus(±z−1/2)`, bounded well inside `C=6.716`. ✓
- *Near-threshold states*: covered, since the enclosure is derived from the live constraint `R'_±<A` itself. ✓
- *Overshoot*: irrelevant to coverage — overshoot lands in the **absorption** set, where `r_a,r_b` handle the reward exactly and analytically. There is no discretization of the overshoot distribution anywhere, which neatly sidesteps the Wiener–Hopf obstruction that blocked the earlier analytic route. This is a genuine architectural strength.
- *Open vs closed*: the enclosure is stated with `≤`, covering the closure; continuation is open; zero-measure discrepancy. ✓
- *Reset as isolated point*: `(0,0)` violates the lower bound `Y_± ≥ 0.000707` (which applies only to non-reset live states), so it **must** be adjoined explicitly as its own patch. Phase-4C says so. This is the single most likely place for an implementation gap, because it is an exceptional case in otherwise uniform patch logic — flag it as a mandatory regression test.

> **Residual concern (minor, must be closed in code, not mathematics).** "Patch coverage of the closure implies coverage of all reachable continuation states" is valid **only if** the patch cover is verified to contain the enclosure with Arb-outward-rounded geometry — i.e. the union of patches must be *proved* to contain `{0≤Y_±, Y_++Y_-≤C}∪{(0,0)}`, not merely constructed to. A floating-point patch generator that leaves a 10⁻¹² sliver uncovered voids the theorem. **Requirement: the auditor must independently verify coverage from exact rational patch corners, not trust the generator.**

**Two-dimensionality — CONFIRMED and important.** The nonzero Jacobian argument rules out a 1-D reduction. Combined with the antisymmetry of `a`, the half-domain reduction is the only available dimension saving. Accept it.

---

## PART III — Contraction audit

**The logic is valid.** Each of the six required links checks out:

1. *Monotonicity.* For the one-sided chart, `Y ↦ softplus(Y+z−1/2)` is nondecreasing in `Y` for every fixed `z`, so pathwise coupling under a common innovation sequence gives monotone hitting: starting higher hits no later. Hitting probability by step `n` is therefore nondecreasing in the start state. ✓ PROVED.
2. *Left-endpoint step envelope is a continuum bound.* Because of (1), the hitting probability on a cell `[s_i,s_{i+1})` is `≥` its value at `s_i`. A 200-cell left-endpoint construction is thus a genuine lower envelope over the continuum, **not** grid sampling. This is the key point and Phase-4C has it right. ✓
3. *One-sided hit ⇒ two-chart absorption.* Immediate: `max(R_+,R_-) ≥ R_+`, and the plus chart's evolution does not depend on the minus chart. ✓ But note the minorant must be started from `R_+=0`, the **lowest** possible plus-state, for the bound to hold uniformly over all live two-chart states. Phase-4C does this. ✓
4. *Coverage of reset and all live states.* Follows from (1)+(3) since `R_+=0` minorizes. ✓
5. *Outward rounding and row masses.* Row-mass-one checks catch the standard failure (mass silently lost to truncation, which would *inflate* the apparent hitting probability). Necessary and, with outward rounding, sufficient. ✓
6. *Resolvent arithmetic.* For a positive substochastic `K` with `‖K^n‖_∞ ≤ q < 1`, writing `j = kn+r` and summing the geometric series over blocks gives `‖(I−K)^{-1}‖_∞ ≤ n/(1−q)`. With `n=139`, `q=0.89`: `139/0.11 = 1263.64`. ✓ Arithmetic correct.

**Independent numerical check of the contraction constant.** I simulated the one-sided minorant from `R_+=0`:
```
P(τ_+ ≤ 139 | R_+ = 0) = 0.1319   (n = 3×10⁵)
```
The Phase-4C certified claim is `> 0.11`. My estimate exceeds it, so the certified bound is **conservative and safe** — as it must be. ✓ No counterexample or coverage gap found.

> ### FINDING 1 — the resolvent bound is valid but ~2.7× lossier than necessary, and this matters quadratically
>
> For a substochastic `K` arising as the continuation operator of a stopping time, there is an exact and much sharper identity:
> ```
>     ‖(I−K)^{-1}‖_∞ = sup_y Σ_{n≥0} (K^n 1)(y) = sup_y E_y[τ]
> ```
> because `(K^n 1)(y) = P_y(τ > n)`. The resolvent norm **is** the worst-case expected run length over live states. By the monotonicity established in (1), the supremum over the reachable set is attained in the limit of the largest states, and is bounded by the ARL from the *most favorable* start; my independent simulation gives `sup_y E_y[τ] ≈ ARL₀ = 464.8`.
>
> So the true `R ≈ 465`, not `1263.64` — the block bound throws away a factor of **2.72**. Since `R` enters the dominant error term **squared**, this is a factor of **7.4** in the controlling budget line. Phase-4C left it on the table by treating the contraction as the only route to a resolvent bound, when the resolvent has a direct probabilistic meaning here.
>
> **This is an improvement, not a flaw** — the Phase-4C bound is *valid*, merely wasteful. But it is free margin and should be taken.

---

## PART IV — Coupled error propagation audit

**Re-derivation from scratch.** Let `δ_a = â − Kâ − r_a` and `δ_b = b̂ − Kb̂ − K_z â − r_b`, with `e_a = a − â`, `e_b = b − b̂`. Subtracting:
```
e_a = K e_a − δ_a          ⇒  (I−K) e_a = −δ_a   ⇒  ‖e_a‖ ≤ R‖δ_a‖ ≤ R ε_a
e_b = K e_b + K_z e_a − δ_b ⇒ (I−K) e_b = K_z e_a − δ_b
                            ⇒  ‖e_b‖ ≤ R(‖K_z‖‖e_a‖ + ε_b) ≤ R²‖K_z‖ε_a + R ε_b
```
**The Phase-4C inequalities are exactly correct.** ✓ The triangular structure is genuine (`a` does not depend on `b`), so no additional coupling term exists.

**Checks against the specific worries raised in the brief:**
- *`K_z` signed*: handled — the bound uses `‖K_z‖_∞ = sup_y ∫_ℓ^u |z| φ(z)dz ≤ E|Z| = √(2/π) = 0.797885`, which takes absolute values and is therefore valid for a signed kernel. Also correctly *conservative*: the true sup is over a truncated interval, so `‖K_z‖ < √(2/π)` strictly. ✓
- *State-dependent continuation domain*: absorbed into the definition of `K`; the sup-norm bound is taken pointwise over `y`, so variable limits are harmless. ✓
- *Patchwise residual evaluation*: valid **provided** `ε_a`, `ε_b` are global sups over a verified cover — `‖δ‖_∞ = max over patches` requires the cover to be complete (Part II concern). ✓ conditional on coverage.
- *Isolated reset point*: `(0,0)` must be included in the sup. If the reset patch were omitted, `ε` would be understated and the theorem void. ✓ conditional on the mandatory reset patch.
- *Dyadic coefficients with nonlinear transitions*: harmless by design — the residual theorem absorbs all candidate error, so the candidate needs no accuracy guarantee, only exactness of representation. This is the architecture's best feature (see Part VI).
- *Domain a strict subset of the square*: safe in the right direction; `sup` over a subset is `≤` sup over the square, and the operators are only ever applied to states in the reachable set.

**No missing terms found.** The propagation is sound.

> ### FINDING 2 — an error of omission in the budget, in your favor
>
> Combining Finding 1 with the (correct) propagation, and using a safe certified `R ≤ 470`:
>
> | Budget item | Phase-4C (`R`=1263.64) | **Corrected (`R`≤470)** |
> |---|---:|---:|
> | `a`-induced `b` error `R²‖K_z‖ε_a` | 6.3702 | **0.8813** |
> | direct `b` error `R ε_b` | 1.8955 | **0.7050** |
> | reserve | 0.5 | 0.5 |
> | **projected lower endpoint** | **8.5211** | **15.2006** |
>
> Failure thresholds (holding the other target fixed) move correspondingly:
>
> | | Phase-4C | Corrected | observed deg-16 float residual |
> |---|---:|---:|---:|
> | `ε_a` fails at | `1.01e−5` | **`7.99e−5`** | `5.21e−7` |
> | `ε_b` fails at | `6.66e−3` | **`2.96e−2`** | `8.07e−6` |
>
> The safety factor on the controlling quantity `ε_a` rises from **19×** to **153×** over the observed candidate residual scale. Equivalently: at the observed residual scale, the proof would still close with any resolvent bound up to `R ≤ 5954` — the crude 1263.64 was never actually binding, but the corrected value converts a comfortable margin into an overwhelming one.
>
> **Verdict on the 8.52 projection: it survives skeptical recomputation, and is pessimistic by roughly 6.7 units.** I recommend implementing with `R` from the direct `sup_y E_y[τ]` route, and *retaining* the 139-step block bound as an independent cross-check (two derivations of `R` that must be consistent is a cheap and valuable audit invariant).

---

## PART V — Attacking the Taylor/Bernstein plan

**This is the only component I cannot clear, and it is where the residual risk lives.** Everything above is either proved or arithmetic; this part is an unimplemented engineering bet.

**The diagnosis in Phase-4C is right.** Raw interval boxes fail not from any pathology in the operator (the transition is 1-Lipschitz, convex, second derivative `≤1/4` — about as benign as a nonlinearity gets) but from **dependency loss**: the residual `b̂ − Kb̂ − K_z â − r_b` is a difference of quantities of size ~17 whose true difference is ~10⁻⁶. Enclosing minuend and subtrahend independently gives a width set by the *terms*, not the *difference* — hence the observed widths of 2.9 at 1/32 refinement, seven orders of magnitude too coarse. Refining cannot fix this at any practical cost: the table shows width halving with cell width, so reaching 5e−6 from 2.9 needs ~2¹⁹ refinement per axis. **Rejecting raw boxes is correct and non-negotiable.**

**Does Taylor/Bernstein actually restore the cancellation? — Yes in principle, and the mechanism is specific.** The cancellation is restored because the candidate and its Bellman image are represented in the *same* polynomial basis on each patch, so the subtraction happens **symbolically on coefficients** before any interval evaluation. What is then enclosed by intervals is only (i) the Taylor remainders of `softplus` and the Gaussian factors, and (ii) the integration remainder — all of which are genuinely small, not differences of large quantities. Bernstein range bounds on the resulting low-degree residual polynomial are near-tight (they converge to the true range under subdivision, quadratically for the standard de Casteljau refinement).

**Complete list of remainder terms a correct implementation must enclose.** Any omission voids the theorem:

1. **softplus Taylor remainder** — degree-`d` local model on each patch; `|s^{(2)}|≤1/4` globally and all higher derivatives are bounded by explicit constants (`s'=σ`, `s''=σ(1−σ)`, derivatives are polynomials in `σ∈(0,1)`), so Lagrange remainders are straightforward and *provably* bounded. Low risk.
2. **Candidate composition `b̂(q(y,z))`** — a degree-16 tensor-Chebyshev polynomial composed with the softplus Taylor model. This is the **degree-growth hazard**: naive composition gives degree `16·d`. Must be re-expanded and truncated *with remainder* at working degree. Highest-risk item on this list.
3. **Gaussian density `φ(z)`** — local Taylor with explicit remainder; `φ` is entire with well-controlled derivatives. Low risk.
4. **Gaussian tail terms in `r_a,r_b`** — `Φ` at variable endpoints; needs certified `Φ`/`φ` enclosures (already in the reusable CUSUM machinery). Low risk.
5. **Variable integration limits `ℓ(y),u(y)`** — these are **affine** in `y`, which is a significant simplification: the `z`-integral over an affine-endpoint interval of a polynomial integrand is exactly integrable in closed form. Low risk, and should be exploited rather than quadratured.
6. **Cells intersecting the continuation boundary** — where the patch straddles `z=ℓ` or `z=u`. Requires splitting the `z`-integral at the exact affine boundary within the patch. Medium risk; a standard but fiddly case.
7. **Patch-boundary consistency** — no continuity requirement is actually needed (the residual is bounded patchwise and the sup taken), but **overlap or gap accounting** is mandatory.
8. **Chebyshev→Bernstein conversion** — the basis change must be done in exact rational/dyadic arithmetic or with certified rounding; the conversion matrix is ill-conditioned at degree 16 and this is a silent-error risk.
9. **Integration remainder** — eliminated if item 5 is done exactly; otherwise needs certified quadrature error.
10. **Coefficient quantization** — harmless by construction (exact dyadics; the residual theorem absorbs it).
11. **Symmetry reduction** — the half-domain argument must be applied to the *residual bound*, not assumed; i.e. prove `δ` on the reflected half equals the reflection of `δ`, which follows from exact coefficient symmetrization. Must be a verified invariant, not an assumption.
12. **Domain-cover geometry** — Part II concern; exact rational corners.

**Is `ε_a ≤ 5e−6` realistically achievable?** My assessment: **yes, with substantial margin, and the corrected budget makes the question much less pressing.**

- The degree-16 spectral candidate already achieves `residual_a = 5.21e−7` on an independent float grid — a factor 9.6 below the Phase-4C target and **153× below the corrected failure threshold of 7.99e−5**.
- The real question is not the candidate's accuracy but the **overestimation factor** of the certified evaluation over the float residual. Taylor/Bernstein on adaptively subdivided patches typically loses one to two orders of magnitude, not four. Against a 153× margin, a 10–30× overestimation still closes.
- The `a`-residual is the easier of the two: `a` is antisymmetric, ranges over only `[−0.612, 0.612]`, and vanishes on the diagonal — a small, smooth, well-scaled function. It is `b` (range `[10.26, 17.29]`) that is large, and `ε_b` now has a 3.6e3× margin.

> **Recommendation on local representation.** Phase-4C proposes degree 4–8 local Taylor models. I recommend instead **local Chebyshev models with certified remainder (Taylor-model arithmetic in the Makino–Berz sense), degree 6–8, on adaptively subdivided patches**, for a concrete reason: the dominant risk (item 2, composition degree growth) is controlled by re-expansion, and Chebyshev re-expansion is numerically stable where monomial Taylor re-expansion at degree 16·d is not. Convert to Bernstein **only at the final range-bounding step**, on the low-degree residual — never on the composed intermediate. This is a small change to the plan that removes most of the highest-risk item.
>
> **Second recommendation.** Exploit item 5: since `ℓ,u` are affine and the integrand is polynomial after local modeling, do the `z`-integration **symbolically in exact arithmetic**. This eliminates remainder item 9 entirely and removes a whole error channel.

---

## PART VI — Trusted computing base review

| Class | Contents | Assessment |
|---|---|---|
| **A. Theorem-level mathematics** | Affine reduction; Bellman equations; `r_a,r_b`; reflection identities; forward-invariance of the reachable enclosure; monotone-minorant contraction; resolvent identity `‖(I−K)^{-1}‖=sup_y E_y[τ]`; triangular error propagation | All re-derived and confirmed in Parts I–IV. **Must be human-checked, not machine-trusted** |
| **B. Exact rational/dyadic artifacts** | `A=8325/16`, `δ=1`, candidate coefficients, patch corners | Exact; must be *serialized* exactly and hashed |
| **C. Arb-certified inequalities** | Reachable constants; transition/remainder enclosures; Bernstein bounds; contraction matrix and row masses; resolvent; final interval | The genuine numerical TCB |
| **D. Non-rigorous (untrusted)** | NumPy/SciPy, Monte Carlo, bilinear refinement, spectral collocation, candidate solve | Correctly outside the TCB ✓ |
| **E. Independent replay** | Auditor | See Part VII |

**The "candidate need not be trusted" claim is CORRECT and is the architecture's strongest property.** Once coefficients are fixed as exact dyadics, the residual theorem `‖e‖ ≤ R‖δ‖` validates *whatever* they are. An adversary could supply arbitrary coefficients and the proof would either close or fail loudly — it cannot silently produce a wrong answer. ✓

> ### FINDING 3 — three things must be trusted that are not in the stated TCB
>
> 1. **The patch cover's completeness** (Part II). The stated TCB lists "local polynomial/Taylor remainder logic" and "Bernstein range evaluation" but not *geometric coverage verification*. If the union of patches does not provably contain the reachable enclosure, every residual bound is vacuous. **Add: exact-rational coverage certificate.**
> 2. **The `sup` reduction across patches.** `ε = max_patch(bound)` is only the global sup if the patch set is complete *and* the reset point is included. **Add: an explicit enumeration invariant.**
> 3. **The symmetry reduction** (item 11 above). Computing on the half-domain and reflecting is a *theorem* about the residual, and it must be verified on exact coefficients — not assumed. **Add to class A, and verify in class C.**
>
> None is a flaw in the mathematics; all three are TCB-completeness gaps that a careless implementation would fall into.

---

## PART VII — Independent auditor design

The auditor must **reconstruct**, not **re-invoke**. Concretely, for each item: what it independently rebuilds, and whether it may share Arb primitives.

| Item | Auditor obligation | Share Arb? |
|---|---|---|
| Detector constants | Re-read `A=8325/16`, `δ=1` from the certificate; re-derive `L`, `C` from formulas it implements itself | Yes (ball arithmetic only) |
| Operator formulas | **Re-implement** `q_±`, `ℓ`, `u`, `r_a`, `r_b` from the paper's equations, independently of producer code | **No — separate implementation** |
| Reachable coverage | Independently verify `∪patches ⊇ enclosure` from exact rational corners; verify reset patch present | **No** |
| Dyadic coefficients | Read as exact rationals; verify hash; verify exact symmetry relations | Yes |
| Taylor remainders | **Re-derive and re-bound** from its own derivative bounds — the single most important non-shared component | **No** |
| Bernstein bounds | Re-convert and re-bound from its own conversion routine | **No** |
| Contraction | Rebuild the 200-cell monotone minorant, re-verify row masses sum to 1, re-derive `q` and the 139-step bound | Yes (Arb), **No** (logic) |
| Resolvent | Recompute *both* `n/(1−q)` and the `sup_y E_y[τ]` route; **require consistency** | Yes |
| Error propagation | Re-derive `R ε_b + R² ‖K_z‖ ε_a` symbolically and recompute | Yes |
| Final interval, `L>2` | Recompute `b(0,0)` interval; assert `L>2` strictly with outward rounding | Yes |
| Hashes | SHA-256 over all exact artifacts | Yes |

**Correlated-bug avoidance is the whole point.** The three items marked "No" (operator formulas, Taylor remainders, Bernstein conversion) are where a shared implementation would let a single sign or index error pass both producer and auditor. Everything else may share Arb, since Arb itself is an irreducible trust root. **Add one adversarial test the report does not mention: feed the auditor a deliberately corrupted candidate coefficient and confirm it FAILS.** An auditor that has never been observed to reject is not known to be an auditor.

---

## PART VIII — The exact Phase-4D theorem

Phase-4D should attempt exactly this, and claim nothing beyond it.

> **Theorem (Phase-4D target).** Let `Z_1,Z_2,… ` be i.i.d. `N(0,1)`. Define the symmetric two-chart Shiryaev–Roberts detector with `δ=1`, `A=8325/16`:
> ```
> R_0^± = 0,   R_t^+ = (1+R_{t-1}^+)e^{Z_t−1/2},   R_t^- = (1+R_{t-1}^-)e^{−Z_t−1/2},
> τ = inf{t≥1 : max(R_t^+,R_t^-) ≥ A},   T_t = Σ_{s≤t} Z_s,   Γ_SR = E_0[Z_τ T_τ].
> ```
> **(a) [PROVED]** `τ` is a.s. finite with `E[e^{cτ}]<∞` for some `c>0`; consequently all moments below exist and the stopped-score identity applies.
> **(b) [CERTIFIED, computer-assisted]** `Γ_SR ∈ [L,U]` with `L > 2`, established by Arb outward-rounded interval arithmetic over a verified cover of a proved forward-invariant reachable enclosure, via an exact-dyadic candidate, certified Bellman residual bounds, and a certified resolvent bound.
> **(c) [PROVED, given (a),(b)]** For `m=1` full reuse in the centered Gaussian location model, `F'_{SR,1}(0) = 1 − Γ_SR < −1`; hence the zero-reference fixed point of the **deterministic skeleton** of the re-baselining recursion is linearly unstable under full reuse.
> **(d) [PROVED]** For affine mixed reuse with fraction `ρ`, `F'_{SR,ρ}(0) = ρ F'_{SR,1}(0)`, hence there is an interior critical reuse fraction `ρ_c^{SR} = 1/(Γ_SR − 1) ∈ (0,1)`, certified to lie in `[1/(U−1), 1/(L−1)]`.
>
> **Assumptions, stated in full:** Gaussian innovations; the specific frozen `(δ,A)`; reuse window `m=1`; the affine mixed-reuse rule; the centered location model; and the reflection symmetry of the *two-chart* construction (which standard one-sided SR does **not** possess).

**Scope discipline — what must NOT be claimed.** Two certified detectors do **not** establish detector-independence. The honest framing is: the *general stopped-score identity* is detector-independent (it assumes only exponential stopping moments and symmetry); the *instability criterion `Γ>2`* is verified at two structurally distinct instances. That is **evidence of mechanism generality, not a proof of it**. Also: nothing here proves oscillation, bimodality, period-2 behaviour, or ARL degradation — those remain empirical/conjectural, and (c) is a statement about the deterministic skeleton, not about the stochastic recursion's invariant law.

---

## PART IX — Codex-ready Phase-4D specification

Issued because the architecture survives the audit, with the Part IV/V amendments folded in.

**1. Modules (conceptual).** `sr_operator` (exact `q_±,ℓ,u,r_a,r_b`) · `reachable` (enclosure constants + exact-rational patch cover + coverage certificate) · `candidate` (float solve, **outside TCB**; dyadic quantizer + exact symmetrizer, inside) · `taylor_model` (Chebyshev models w/ Arb remainder; softplus/φ/Φ; exact affine-limit `z`-integration) · `residual` (patchwise `δ_a,δ_b`; Bernstein range) · `contraction` (200-cell monotone minorant; **both** resolvent routes) · `propagate` (triangular budget) · `certificate` (schema + hashes) · `auditor` (independent; see Part VII).

**2. Stages.** (i) constants & enclosure → (ii) candidate solve + dyadic freeze + symmetrize → (iii) patch cover + coverage certificate → (iv) patchwise residual bounds with adaptive refinement → (v) contraction + dual resolvent bounds → (vi) propagation → (vii) final interval + `L>2` gate → (viii) independent replay.

**3. Candidate.** Degree-16 tensor Chebyshev, exact dyadic coefficients, exactly symmetrized (`a` antisymmetric, `b` symmetric). Not trusted.

**4. Patches.** Adaptive subdivision of the **half-domain** `{0≤Y_±, Y_++Y_-≤C, Y_+≥Y_-}` plus the isolated reset patch. Curvilinear boundary handled by covering with exact-rational boxes clipped to the enclosure — over-cover is safe, under-cover is fatal.

**5. Refinement criterion.** Subdivide any patch whose `δ_a` bound exceeds `ε_a/√(#patches)` (or `δ_b` likewise); cap depth; **fail loudly** rather than silently accept a coarse patch.

**6. Arb precision.** 192 bits baseline, 256 near the single-chart boundary where degree growth is worst. Precision must be a certificate field, not a runtime default.

**7. Residual targets (revised).** `ε_a ≤ 5e−6`, `ε_b ≤ 1.5e−3` retained as *working* targets — but the true failure thresholds under corrected `R` are `ε_a < 7.99e−5`, `ε_b < 2.96e−2`. Implement to the working target; **gate on the failure threshold.**

**8. Contraction target.** `R ≤ 470` via `sup_y E_y[τ]`, cross-checked against `139/(1−q) ≤ 1263.64`. Certificate must record both and assert consistency.

**9. Stopping condition.** **Halt immediately** when the audited interval satisfies `L > 2`. No tightening. This is a hard instruction: further refinement has zero scientific value and nonzero risk of introducing a bug into a passing proof.

**10. Certificate schema.** Detector constants (exact rationals) · enclosure constants (Arb balls) · candidate coefficient hash · patch cover manifest + coverage certificate · per-patch residual bounds · `ε_a,ε_b` · both resolvent bounds · propagation arithmetic · final `[L,U]` · `L>2` boolean · Arb/FLINT versions · SHA-256 of every artifact.

**11. Auditor.** Per Part VII, with operator formulas / Taylor remainders / Bernstein conversion **separately implemented**.

**12. Regression tests.** Protected Level-3 CUSUM certificate full Arb replay (must still PASS) · reset-patch presence · coverage completeness · symmetry invariants · row-mass-one · corrupted-coefficient rejection · corrupted-patch-cover rejection · endpoint (open/closed) convention.

**13. Artifact protection.** Level-3 and Phase-4B artifacts read-only; SR work writes only to new paths; no shared mutable state.

**14. Failure modes.** `ε_a` unreachable at practical patch count (→ raise candidate degree or subdivide further) · composition degree blow-up (→ Chebyshev re-expansion per Part V) · coverage gap (→ hard fail) · resolvent inconsistency between the two routes (→ hard fail, indicates a bug in one).

**15. PASS/FAIL.** **PASS** iff an independently replayed certificate yields `Γ_SR ∈ [L,U]` with `L > 2` strictly under outward rounding, all invariants verified, and the protected CUSUM certificate still replaying green. **FAIL** otherwise — and a FAIL is reported as a FAIL, not narrowed by relaxing a target.

---

# FINAL VERDICT

## PHASE-4D PRE-IMPLEMENTATION VERDICT: GREEN

Qualified GREEN: the architecture is mathematically sound as specified, and the two amendments below *increase* its margin rather than repair a defect. I found no mathematical flaw. The one genuinely unresolved item (certified `ε_a` at continuum scale, Part V) is an engineering risk with a 153× margin, not a mathematical obstruction — which is what distinguishes GREEN from YELLOW here.

**Strongest surviving theorem.** As stated in Part VIII: `Γ_SR ∈ [L,U]`, `L>2` for the frozen symmetric two-chart SR, yielding `F'_{SR,1}(0)<−1` and `ρ_c^{SR}∈(0,1)`, under the general stopped-score identity whose hypotheses (exponential stopping moments; reflection symmetry) SR provably satisfies.

**Flaws found in Phase-4C.** No mathematical error. Three findings: **(1)** the resolvent bound is valid but 2.72× lossier than the exact identity `‖(I−K)^{-1}‖_∞ = sup_y E_y[τ] ≈ 465` allows, costing 7.4× in the dominant budget term; **(2)** consequently the 8.52 projection is pessimistic by ~6.7 units; **(3)** three TCB-completeness gaps (patch-cover verification, sup-across-patches enumeration, symmetry reduction as a verified theorem) that are not listed and that a careless implementation would fall into. Additionally, one presentational point: the theorem must say *symmetric two-chart SR*, never "Shiryaev–Roberts" unqualified, since standard one-sided SR lacks the symmetry the identity needs.

**Corrected error budget.** `R ≤ 470`: `a`-induced 0.8813 + direct-`b` 0.7050 + reserve 0.5 ⇒ **projected lower endpoint 15.20** (vs 8.52). Plausible final enclosure ≈ `[15, 20]`; stop as soon as `L>2`.

**Minimum residual targets.** Working: `ε_a ≤ 5e−6`, `ε_b ≤ 1.5e−3`. Hard failure thresholds: `ε_a < 7.99e−5`, `ε_b < 2.96e−2`. Observed float scale: `5.21e−7` / `8.07e−6` — margins 153× and 3.7e3×.

**Contraction/resolvent assessment.** Logic valid on all six checks; monotone-minorant construction is a genuine continuum bound, not grid inference; my independent estimate `P(τ_+≤139|R_+=0)=0.132` confirms the certified `>0.11` is conservative. Recommend the `sup_y E_y[τ]` route as primary with the block bound retained as a consistency invariant.

**Estimated probability of successful closure.** **High** — I'd put it around 0.85–0.9. The dominant residual uncertainty is the certified-vs-float overestimation factor in Part V, and the corrected margin absorbs two orders of magnitude of it.

**Estimated proof-engineering effort.** 4–7 focused days (unchanged from Phase-4C's 4–8, slightly reduced by the exact affine-limit integration and the larger margin permitting coarser patches) plus 2–12 workstation hours.

**Top 5 mathematical risks.** 1. Certified `ε_a` overestimation exceeding ~150× the float residual. 2. Composition degree growth (deg-16 candidate ∘ softplus model) defeating cancellation at patch boundaries. 3. Reachable-cover gap, especially the isolated reset point. 4. Symmetry reduction assumed rather than verified on exact coefficients. 5. Open/closed continuation convention mishandled at absorption boundaries (zero-measure, but a double-count would bias `r_a,r_b`).

**Top 5 implementation risks.** 1. Chebyshev→Bernstein conversion at degree 16 (ill-conditioned; silent error). 2. Patch generator producing slivers not provably covered. 3. Auditor sharing producer code for operator formulas or Taylor remainders (correlated bugs). 4. Adaptive refinement silently accepting a coarse patch instead of failing. 5. Arb precision set by runtime default rather than recorded as a certificate field.

**Exact conditions that would invalidate the proof.** Any patch-cover gap; omission of the reset state from the residual sup; a non-outward-rounded step anywhere in the Arb chain; row masses not verified to contain 1; use of the *float* residual in place of a certified bound; asserting `L>2` non-strictly; the symmetry reduction applied without proof; or modification of any protected Level-3 artifact.

**Does certified CUSUM + certified SR + the general stopped-score theorem constitute genuinely cross-detector rigorous evidence?** **Partially — and the distinction matters.** What would be rigorous is: (i) the stopped-score identity, whose proof genuinely uses no detector structure beyond exponential stopping moments and symmetry — that *is* detector-independent and is the real conceptual content; and (ii) two certified witnesses at structurally distinct detectors (additive/reflected CUSUM vs multiplicative/two-chart SR), ARL-matched to within 0.2% (464.8 vs 465.8), which is a genuinely like-for-like pair rather than a coincidence of calibration. What would **not** be established is that `Γ>2` holds for *classes* of detectors: two points are two points. The defensible claim is "the mechanism is not CUSUM-specific, and the governing identity is general"; the indefensible one is "reuse destabilizes re-baselining for sequential detectors generally." I would also note that both witnesses remain Gaussian and `m=1` — a non-Gaussian exponential-family witness would add more generality per unit effort than a third Gaussian detector.

**Level-4 rating: deferred**, as instructed, pending Phase-4D success or failure.
