# Theorem TPT — Taylor-profile transport for the K5-B direct clause

**Status:** research theorem, written 2026-09-27/28 (overnight campaign) before any evaluation on any cell.
* It has **never been evaluated on CUSUM m = 5 cells 305–309**, and is not evaluated on them in this campaign.
* It is general: it applies to every K1 cell with `x_lo > 0`, for every detector and every m.

## 0. Motivation (prospective, target-independent)

The K5-B direct clause and its C5-T sharpening transport the midpoint value `g(e0)` across the cell with
`g(e) − g(e0) = −∫_{e0}^{e} t R''(t) dt`. Both then bound `R''(t)` by **one whole-cell interval** `[H_lo, H_hi]`.

Theorem TC's own proof (`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` §4 step 1) produces something finer. It
proves Taylor remainder bounds at distance `|t − e0|` and only then replaces `|t − e0|` by its maximum `ρ`. The
resulting radius `rad_r(ρ)` is charged at every point of the cell, including the midpoint, where the true TC radius
is `rad_r(0) = A0·f_H + 2A1·f_D + A2·f_F`. That is the midpoint residual only, typically orders of magnitude smaller.

The C5 adjudication (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md` §8) scopes C5-T's
exhaustion to bounds built from **exactly two inputs** (`g_hi` and a whole-cell `[H_lo, H_hi]`). It states that the
exhaustion "says nothing about … a transport consuming a third certified input". The C5 route search
(`phase_3/C5_ROUTE_SEARCH.md`) killed:
* **B2**, splitting the cell, because R and D are certified at e0 only;
* **D3**, second-order transport, because it needs R'''.

TPT is neither of these:
* it keeps one midpoint and first-order transport;
* it needs no R''';
* it consumes, as its third input, the pointwise profile that theorem TC already certifies.

This motivation is a property of the inequality chain. It does not depend on any cell's Γ.

## 1. Transport theorem

**Setting.** A cell `C = [x_lo, x_hi] = [e0 − ρ, e0 + ρ]` with **`x_lo > 0`**. `R` is C² on C, and
`g(e) := R(e) − e R'(e)`, so `g'(e) = −e R''(e)`.

**Inputs.**
* (i) `g(e0) ≤ g_hi`.
* (ii) Measurable functions `L, U` on C with `L(t) ≤ R''(t) ≤ U(t)` for every `t ∈ C`, with `t·L` and `t·U`
  integrable.

**Theorem TPT.** For every `e ∈ C`, `g(e) ≤ g_hi + P*`, where

    P* := max( 0,  sup_{e∈[e0,x_hi]} ∫_{e0}^{e} t·(−L(t)) dt,  sup_{e∈[x_lo,e0]} ∫_{e}^{e0} t·U(t) dt ).

**Proof.**
* `g` is absolutely continuous on C.
* For `e ≥ e0`: `g(e) − g(e0) = −∫_{e0}^{e} t R''(t) dt ≤ ∫_{e0}^{e} t (−L(t)) dt`, because `t > 0` and
  `−R'' ≤ −L`.
* For `e ≤ e0`: `g(e) − g(e0) = ∫_{e}^{e0} t R''(t) dt ≤ ∫_{e}^{e0} t U(t) dt`.
* The case `e = e0` gives the 0 term.
* Take the supremum over e. ∎

**Corollary TPT-M (monotone profiles).** Assume
* `−L(e0 + s)` is non-decreasing in `s ∈ [0, ρ]`, and
* `U(e0 − s)` is non-decreasing in `s ∈ [0, ρ]`.

Then

    P* = max( 0,  ∫_{e0}^{x_hi} t·(−L(t)) dt,  ∫_{x_lo}^{e0} t·U(t) dt ).

*Proof.* Write `I(s) := ∫_{e0}^{e0+s} t(−L(t)) dt`.
* `I'(s) = (e0+s)(−L(e0+s))`. Since `e0 + s > 0`, its sign is the sign of `−L(e0+s)`.
* That sign is non-decreasing in s, so it changes at most once, from − to +.
* Hence I is quasi-convex and attains its maximum over `[0, ρ]` at an endpoint.
* The left side is the same argument with `J(s) := ∫_{e0−s}^{e0} tU(t) dt`. ∎

**Corollary TPT-P (sound relaxation, no monotonicity needed).**

    P* ≤ P₊ := max( ∫_{e0}^{x_hi} t·(−L(t))⁺ dt,  ∫_{x_lo}^{e0} t·(U(t))⁺ dt ).

**Proposition TPT-D (dominance over C5-T and the frozen clause).**
* With `L ≥ H_lo` and `U ≤ H_hi` pointwise, `P* ≤ P₊ ≤ P_C5T` (C5-T's
  `max((−H_lo)⁺ w_R, (H_hi)⁺ w_L)`), and `P_C5T < ρ·x_hi·M`.
* C5-T is exactly TPT with the constant profile `L ≡ H_lo`, `U ≡ H_hi`.
* *Proof:* `(−L)⁺ ≤ (−H_lo)⁺` pointwise, and `∫_{e0}^{x_hi} t dt = w_R`. ∎

**Proposition TPT-O (optimality within the three-input family).** For given `(g_hi, L, U)` with `L ≤ U`, the bound
`g_hi + P*` is attained by an admissible witness:
* `g(e0) = g_hi`;
* `R'' = L` on `(e0, x_hi]` and `R'' = U` on `[x_lo, e0)`.

So no bound using only these three inputs is smaller.

**Scope** (carried over from C5 adjudication §8, verbatim in substance):
* The witness is an arbitrary absolutely continuous function consistent with the inputs, not a resolvent-type R.
* The result does not apply to a cell with `x_lo = 0`.

## 2. The TC profile lemma (the third input)

**Lemma TC-P.** Assume the premises (P1)–(P4) of theorem TC, or (P1), (P2′), (P3′) and Lemma G of TC-T, on C. For
`t ∈ C` put `s := |t − e0| ≤ ρ` and

    p0(s) := f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ Env4/24
    p1(s) := f_D + s f_H + s² f_G/2 + s³ Env4/6
    p2(s) := f_H + s f_G + s² Env4/2
    rad_r(s) := A0·p2(s) + 2·A1·p1(s) + A2·p0(s).

Then `|F_r''(t)(a) − Ĥ_r(a) − (t − e0)·Ĝ_r(a)| ≤ rad_r(s)` for every `t ∈ C`.

*Proof.* This is theorem TC §4 with the substitution of `ρ` for `|t − e0|` omitted.
* Step 1 is Taylor's theorem with integral remainder in `B(X)`. For example
  `φ''(t) = φ''(e0) + (t−e0)φ'''(e0) + ∫_{e0}^{t}(t−u)φ⁗(u)du`, with `‖φ⁗(u)‖ ≤ Env4` for every `u` on the segment
  `[e0, t] ⊂ C`. So `‖φ''(t)‖ ≤ p2(s)`, and likewise `p1(s)` and `p0(s)`.
* Steps 2–3 are unchanged. The A-constants are uniform over C, so they hold at t.
* No inequality of TC uses `s = ρ` except the final substitution. ∎

**Consequence (profile enclosure of R''_m).**

    R''_m(t) ∈ 𝓗_m(t) := Σ_{r<m} (1/m)·[Ĥ_r(a) + (t−e0)Ĝ_r(a) − rad_r(s), Ĥ_r(a) + (t−e0)Ĝ_r(a) + rad_r(s)]
                          + Σ c·𝒲_(r,j),

where the whole-cell W enclosures are used unchanged (constant in t).

Intersecting with any whole-cell enclosure `H_K1 ⊇ R''_m(C)` (the K1 record's `R2_interval`) keeps validity
pointwise:

    L(t) := max(H_K1.lo, lo 𝓗_m(t)),    U(t) := min(H_K1.hi, hi 𝓗_m(t)).

* If `Ĝ ≡ 0` (TC-T, premise (P2′)), `lo 𝓗_m(e0 + s)` is non-increasing and `hi 𝓗_m(e0 − s)` is non-decreasing in s,
  because every coefficient of `p0`, `p1` and `p2` is ≥ 0. So Corollary TPT-M applies, and `P*` is two polynomial
  integrals.
* With `Ĝ ≠ 0` (theorem TC), use `P₊` (Corollary TPT-P), which is always sound.

## 3. What TPT changes and what it does not

| item | status |
|---|---|
| `g_hi`, `R2_interval`, W enclosures, A-constants, `f_*`, `Env4`, ρ, cover | **unchanged**; all are the committed certified inputs |
| TC / TC-T radius | used pointwise in t instead of at its maximum |
| consumer | **changed**: the direct clause `g_hi + ρ x_hi M` (or C5-T) is replaced by `g_hi + P*` |
| floor r2 | TPT is **closure-only** under floor r2 (`adoption_quantity` binds C2's consumer path, `fail_closed[3]`); any adoption use needs a floor extension frozen before any evaluation (C2 Condition 1; route audit U3) |
| chain recurrences of K5-B (`ℓ_k`, `γ_k`) | not changed here. The same profile idea applies to `μ_k` and is left as a remark. |

## 4. Validation obligations (non-target only)

* **V1.** Exact-truth synthetic fixtures (finite-state drift families, `code/ov_fixtures.py`):
  * build a full TC pipeline (candidates, certified residual bounds, Env4, Lemma-G constants);
  * check `max_{e∈C} g(e) ≤ g_hi + P* ≤ g_hi + P_C5T ≤ g_hi + ρ x_hi M` on every fixture cell;
  * check Lemma TC-P pointwise against the exact `F''(t)(a)` on a dense rational grid.
* **V2.** Adversarial:
  * profiles that are non-monotone (P₊ path);
  * `H_K1` binding on part of the cell;
  * a planted invalid profile (L above the true R'' somewhere) must make the check fail.
* **V3.** Real non-tail cells: the 34 lower-front TC cell records (CUSUM cells 11–44,
  `p5y_k5_lower_front_order3/evidence/tc_r1/cells/`), if their committed inputs suffice. Soundness relations and
  improvement factor; e ≈ 0.01, a regime far from the tail.
* **V4.** Independent second implementation of the P* integral (different algorithm: dense rational Riemann upper
  sums vs closed-form polynomial integration). They must agree, the upper sums from above.
