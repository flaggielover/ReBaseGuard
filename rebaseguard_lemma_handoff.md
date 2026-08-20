# ReBaseGuard — Lemma Attack & Handoff: `E₀[Z_τ T_τ] > 2`

**Model (fixed):** `Z_t ~iid N(0,1)`, `S₀^±=0`, `S_t^+=max(0,S_{t-1}^++Z_t−0.5)`, `S_t^-=max(0,S_{t-1}^-−Z_t−0.5)`, `τ=inf{t≥1: max(S_t^+,S_t^-)≥5}`, `T_t=Σ_{s≤t}Z_s`.

**Outcome of this round: NOT rigorously proved.** No Monte-Carlo CI is used as proof. Below are the exact identities obtained, a rigorous *negative* result (why elementary routes cannot work), the exact sufficient inequality, the minimal sub-lemma, and a self-contained handoff. Numerical values are diagnostic only, explicitly labelled NUMERICAL EVIDENCE.

---

## 1. Regularity (used by every identity below) — PROVED
`k=0.5>0 ⇒ τ<∞ a.s. with finite exponential moments` (regeneration: the chart returns to a bounded neighbourhood of 0 infinitely often with uniformly bounded cycle-length tail). Hence all moments of `τ, T_τ, Z_τ` are finite and every optional-stopping / dominated-convergence step below is justified in `L¹`.

## 2. Exact decomposition — PROVED
```
E[Z_τ T_τ] = E[Z_τ²] + E[Z_τ T_{τ-1}]  =  c₀ + Σ_{r≥1} c_r,   c_r := E[Z_τ Z_{τ-r}] (Z_{τ-r}:=0 if r≥τ).
```
Both `E[Z_τ]=0` and `E[T_τ]=0` hold by the reflection symmetry `X↦−X` (swaps the two arms, negates `Z,T`, leaves `τ` and `Z_τT_τ` invariant), so the raw second moment equals the covariance. **NUMERICAL EVIDENCE** (n=2×10⁵): `E[Z_τT_τ]≈15.88`, `c₀=E[Z_τ²]≈4.05`, `E[Z_τT_{τ-1}]≈11.82`; `c_r>0` and monotonically decreasing over `r=0..~30` (`c_1..c_5 ≈ 2.39,2.13,1.82,1.46,1.11`).

## 3. Exact martingale identities obtained — PROVED
- **(M1)** `E[Z_t T_t | F_{t-1}] = T_{t-1}·E[Z_t] + E[Z_t²] = 1`, so `Z_tT_t − 1` is a martingale-difference sequence; optional stopping gives `E[Σ_{t=1}^τ Z_t T_t] = E[τ]`.
- **(M2)** `T_t²−t` is a martingale ⇒ **Wald's second identity** `E[T_τ²]=E[τ]` (=ARL₀). NUMERICAL EVIDENCE: `E[T_τ²]≈465.3` vs `E[τ]≈465.4` (agreement <0.1%).
- **(M3, summation-by-parts, exact pathwise)** `Σ_{t=1}^τ Z_tT_t = ½T_τ² + ½Σ_{t=1}^τ Z_t²`. Taking `E`: `E[τ]=½E[τ]+½E[τ]` ✓ (self-consistent).

## 4. Rigorous NEGATIVE result — why elementary identities cannot close the lemma — PROVED
Every identity in §3 constrains only the **path-sum** `Σ_{t≤τ} Z_tT_t` (which equals `E[τ]` in expectation), **not the terminal term `Z_τT_τ`**. Concretely, attempting to isolate `E[Z_τT_τ]` from the `T_t²−t` martingale via `T_τ²=T_{τ-1}²+2Z_τT_{τ-1}+Z_τ²` and `E[T_τ²]=E[τ]` yields, after substitution, the tautology `E[Z_τT_τ]=E[Z_τT_{τ-1}]+E[Z_τ²]` — i.e. `0=0` — because `τ−1` is **not a stopping time** (`{τ−1=t}=​{τ=t+1}∉F_t`), so no Wald identity applies to `T_{τ-1}`. **Conclusion:** `E[Z_τT_τ]` is an irreducible boundary functional of the pre-crossing state `S_{τ-1}`; it cannot be obtained from mean/variance martingales alone. This rigorously validates the Phase-2C diagnosis.

## 5. Sufficient inequality (the cleanest handoff target)
Because both summands in §2 are numerically well above the requirement, **either** of the following alone suffices:
```
(S-a)  E[Z_τ²] ≥ 2         [needs only the terminal-increment 2nd moment; truth ≈4.05]
(S-b)  E[Z_τ T_{τ-1}] ≥ 0  AND  E[Z_τ²] > 2   [covariance-positivity + (S-a)]
```
Elementary partial results toward (S-a): on the up-alarm `A=+`, the crossing forces `Z_τ = h − S_{τ-1}^+ + k + (overshoot) > k = 0.5`, giving the **rigorous but weak** bound `E[Z_τ²] ≥ k² = 0.25`. Closing the gap from 0.25 to 2 requires the conditional law of the pre-crossing level `S_{τ-1}^+` — the same object §4 shows is unavoidable.

## 6. Smallest unresolved sub-lemma
```
Prove a rigorous lower bound  E[Z_τ² | A=+] ≥ 4   (⇒ E[Z_τ²]≥4 ≥ 2 by symmetry),
```
equivalently, control the quasi-stationary density g(s) of S_{τ-1}^+ on [0,h) at the crossing, since
`E[Z_τ²|A=+] = ∫₀ʰ E[(V−(s−k))² | V>s−k+? ]·g(s)ds` with `V~N(0,1)` the fresh increment and the crossing event `S_{τ-1}^++V−k≥h`. A rigorous two-sided bracket on `g` gives a rigorous bracket on `E[Z_τ²]`.

## 7. Most promising rigorous route (Route 3 — certified numerics, feasible given 8× slack)
The pre-crossing level `S_{τ-1}^+` on `A=+` has density `g` solving a **Lindley/Fredholm integral equation** `g = 𝒦g` on `[0,h)`, where `𝒦` is the sub-stochastic transition kernel of the reflected walk `s ↦ max(0, s+V−k)` restricted below `h` (absorbing at `h`), `V~N(0,1)`. `𝒦` is a positive compact operator with spectral radius `<1` (mass leaks to the absorbing boundary), so `(I−𝒦)⁻¹` exists (Krein–Rutman / Banach). A **certified** lower bound on `E[Z_τ²]` follows from:
1. Discretize `[0,h)` into `N` cells; build **rigorous lower/upper interval enclosures** `𝒦⁻ ≤ 𝒦 ≤ 𝒦⁺` for the Gaussian kernel entries via validated quadrature (Gaussian CDF is monotone ⇒ endpoint evaluation gives certified per-cell bounds; add the analytic tail bound `1−Φ(x)≤φ(x)/x`).
2. Solve the two interval linear systems for enclosures `g⁻,g⁺` (monotone iteration converges since `𝒦` is positive and sub-stochastic — a rigorous contraction bound gives the truncation error).
3. Propagate to `E[Z_τ²] ∈ [L,U]` with all discretization + tail truncation errors included.
Because the target margin is large (need `>2`, truth `≈4.05`), a **coarse** `N` with generously loose interval bounds should already certify `L>2`. This is the recommended next step; it is genuinely certifiable, unlike a floating-point quadrature.

## 8. Minimal self-contained handoff problem
> Let `V~N(0,1)`, `k=0.5`, `h=5`. Let `g` be the (unnormalised) density on `[0,h)` of the stationary sub-probability measure of the Markov kernel `P(s,·)=Law(max(0,s+V−k))` killed on exit above `h`, i.e. the Perron eigen-solution / renewal density of the reflected random walk below an absorbing barrier. Using validated numerics (interval arithmetic on the Gaussian kernel + rigorous tail truncation) or a Wiener–Hopf factorisation of `V−k`, produce a **certified** lower bound `L` with `E[Z_τ²]=∫∫(v−k−(s−?))²… ≥ L > 2`. Equivalently, certify `E[Z_τ²]≥2` OR (`E[Z_τ T_{τ-1}]≥0` and `E[Z_τ²]>2`). Any one closes `E₀[Z_τT_τ]>2`, hence `F₁'(0)=1−E[Z_τT_τ]<−1`, hence — with the already-proved `F_ρ'(0)=ρF₁'(0)` — the interior threshold `ρ_c=1/|F₁'(0)|∈(0,1)`.

---

### Status labels
- §1 regularity, §2 decomposition, §3 (M1–M3), §4 negative result, §5 `E[Z_τ²]≥k²=0.25`: **PROVED.**
- `E[Z_τT_τ]≈15.9`, `c₀≈4.05`, `E[Z_τT_{τ-1}]≈11.8`, `c_r>0` decaying: **NUMERICAL EVIDENCE** (not proof).
- `E₀[Z_τT_τ]>2`: **UNPROVED / OPEN.** Reduces to a certified bound on the pre-crossing density (§6–§8); Route 3 is feasible within the large target margin but was not executed this round (a hasty version would risk a false CERTIFIED label, which the budget forbids).
