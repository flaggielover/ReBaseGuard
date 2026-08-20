# 03 — Lean Verification and Model Correspondence Audit

**Working directory:** `/Users/suzhe/ReBaseGuard/rebaseguard-lean`
**Date of record:** 2026-08-20
**Machine:** macOS 26.5.2, arm64, Apple A18 Pro

---

## 1. Environment

| Component | Value | Source |
|---|---|---|
| Lean toolchain | `leanprover/lean4:v4.34.0-rc1` | `lean-toolchain` |
| Lake | `Lake version 5.0.0-src+3447a66 (Lean version 4.34.0-rc1)` | `lake --version` |
| Mathlib | `v4.34.0-rc1`, rev `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11` | `lake-manifest.json`, confirmed against the checkout's `git rev-parse HEAD` |
| batteries | `01bc479e7432594821ba3fb0ca465211941de86d` | `lake-manifest.json` |
| aesop | `c1c4362a130f12e632d252180a6c2a31d8fd4726` | `lake-manifest.json` |
| Qq | `3b55e9d00c6b0018e5d984eb011b6f93c09bd163` | `lake-manifest.json` |
| proofwidgets | `99e8adeea3c3cd86b6b79ba01a1383bf2d31d055` | `lake-manifest.json` |
| importGraph | `978b7ec9fbbf9a535114f1de8fe5b3778b358870` | `lake-manifest.json` |
| plausible | `38e9c3ce15cbb63c92e90bb9a92e4eb82131f669` | `lake-manifest.json` |
| LeanSearchClient | `2bc7cf064315b26bc38dac2e9612fb581be9b75f` | `lake-manifest.json` |
| Cli | `af8bc067a4cc6c6df472a68909a3f40b1c76c43e` | `lake-manifest.json` |
| Lean options | `pp.unicode.fun = true`, `relaxedAutoImplicit = false`, `weak.linter.mathlibStandardSet = true`, `maxSynthPendingDepth = 3` | `lakefile.toml` |

Note `relaxedAutoImplicit = false`: auto-bound implicits are restricted, which
removes a class of silent-typo failure modes.

## 2. `lake build`

```text
$ lake build
…
Build completed successfully (8717 jobs).
exit code: 0
```

Warnings only, all cosmetic (see §5).

## 3. Direct per-module compilation

Every module was elaborated **from source** with `lake env lean`, bypassing the
`lake build` replay cache. Exact exit codes and wall times:

| # | Module | Command | Exit | Wall time |
|---|---|---|---|---|
| 1 | `RebaseguardLean/Basic.lean` | `lake env lean …` | **0** | 5 s |
| 2 | `RebaseguardLean/StoppedLikelihood.lean` | `lake env lean …` | **0** | 261 s |
| 3 | `RebaseguardLean/IntegralBridge.lean` | `lake env lean …` | **0** | 246 s |
| 4 | `RebaseguardLean/Domination.lean` | `lake env lean …` | **0** | 222 s |
| 5 | `RebaseguardLean/CUSUMBridge.lean` | `lake env lean …` | **0** | 259 s |
| 6 | `RebaseguardLean/StoppedQuantities.lean` | `lake env lean …` | **0** | 213 s |
| 7 | `RebaseguardLean/StoppedWalkMoment.lean` | `lake env lean …` | **0** | 217 s |
| 8 | `RebaseguardLean/SmallMoment.lean` | `lake env lean …` | **0** | 211 s |
| 9 | `RebaseguardLean/ReBaseGuardIdentity.lean` | `lake env lean …` | **0** | 222 s |
| 10 | `RebaseguardLean.lean` (root aggregator) | `lake env lean …` | **0** | 238 s |

**All ten exit 0. No module log contains the string `error`** (case-insensitive
scan over all ten logs). Times are dominated by loading Mathlib `.olean` files —
the processes run at ~10% CPU and are I/O-bound.

## 4. Bypass scan

Case-insensitive scan for proof-bypassing constructs across
`RebaseguardLean/` and `RebaseguardLean.lean`:

| Pattern | Matches |
|---|---|
| `sorry` | **0** |
| `admit` | **0** |
| `axiom` | **0** |
| `unsafe` | **0** |
| `native_decide` | **0** |

Zero matches for all five, including inside comments and docstrings — so no
semantic inspection of false positives was necessary (there were none to inspect).

## 5. Warnings

All warnings are cosmetic lint. Distinct categories across the ten module logs:

| Count | Warning |
|---|---|
| 9 | `Set.mem_setOf_eq` deprecated → `Set.mem_ofPred_eq` |
| 5 | `push_neg` deprecated → `push Not` |
| 2 | unused binder hint |
| 1 | `Variable name 's' is not explicitly referenced` |
| 1 | `Variable name 'hX' is not explicitly referenced` |
| 1 | `haveI` where `have` suffices (proof irrelevance) |
| — | `show` used where `change` is meant (style linter), short copyright headers |

None affects soundness. They are recorded, not fixed, so that accepted proofs
are not touched during a closure audit.

## 6. Axiom audit

```text
$ lake env lean AxFull.lean          # imports RebaseguardLean
exit code: 0
```

| Theorem | Axioms |
|---|---|
| `stoppedIntegrand_hasDerivAt` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.isStoppingTime_cusumTau` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.integrable_exp_forcingNat` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.ae_stopped_quantities_eq` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.integrable_exp_abs_walkAt_of_moment_tail` | `[propext, Classical.choice, Quot.sound]` |
| `RebaseguardLean.exists_pos_integrable_exp_abs_walkAt_rebaseguard` | `[propext, Classical.choice, Quot.sound]` |
| **`RebaseguardLean.hasDerivAt_rebaseguard_cusum`** | **`[propext, Classical.choice, Quot.sound]`** |

**Verdict: exactly the acceptable baseline.** No `sorryAx`. No custom axiom. No
proof-bypassing declaration anywhere in the chain.

> Naming note for future auditors: the closure brief listed
> `hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment` and
> `integrable_exp_abs_walkAt_of_moment_tail`; the actual repository names are as
> printed above (the brief's
> `exists_pos_integrable_exp_abs_walkAt_rebaseguard` exists verbatim in
> `SmallMoment.lean:256`). No requested theorem was missing.

## 7. The final theorem, exactly as elaborated

```text
$ #check @RebaseguardLean.hasDerivAt_rebaseguard_cusum

@hasDerivAt_rebaseguard_cusum : ∀ {Ω : Type u_1} [mΩ : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} (X : ℕ → Ω → ℝ),
  (∀ (n : ℕ), Measurable (X n)) →
    ProbabilityTheory.iIndepFun X μ →
      (∀ (j : ℕ), MeasureTheory.Measure.map (X j) μ = ProbabilityTheory.gaussianReal 0 1) →
        HasDerivAt
          (fun e =>
            ∫ (ω : Ω),
              scoreAt X (cusumTau (1 / 2) 5 X) ω *
                Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
          (-∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0
```

Read in ordinary notation: for any measurable, mutually independent family `X`
with standard-Gaussian marginals,

```text
d/de  E[ Z_τ · exp( −e·T_τ − (e²/2)·τ ) ] |_{e=0}  =  − E[ Z_τ · T_τ ]
```

at the alarm time of the two-sided CUSUM with `k = 1/2`, `h = 5`.

---

# Model Correspondence Audit

Compilation does not by itself establish that the Lean statement means what the
science means. Each item below was checked against the **source text**, not
against the module docstrings.

### [x] The detector is genuinely two-sided

`cusumPair : ℝ → (ℕ → Ω → ℝ) → ℕ → Ω → ℝ × ℝ` carries **both** arms as a pair and
`cusumMax k X n ω = max (cusumPair k X n ω).1 (cusumPair k X n ω).2`. The alarm is
tested on `cusumMax`, not on either arm alone.
*(`CUSUMBridge.lean`, `cusumPair` / `cusumMax`.)*

### [x] The positive-arm recurrence is correct

```lean
(max 0 ((cusumPair k X n ω).1 + X n ω - k), …)
```
i.e. `S⁺_{n+1} = max(0, S⁺_n + X_n − k)` — matching `S_t⁺ = max(0, S_{t-1}⁺ + Z_t − k)`
under the derived convention `X n = Z_{n+1}`.

### [x] The negative-arm recurrence is correct

```lean
(…, max 0 ((cusumPair k X n ω).2 - X n ω - k))
```
i.e. `S⁻_{n+1} = max(0, S⁻_n − X_n − k)`. The **same** `X n` drives both arms, with
the sign flipped only in the second component. Correct.

### [x] `k = 1/2` in the final theorem

`hasDerivAt_rebaseguard_cusum` calls `cusumTau (1 / 2) 5 X` — the literal `1/2`
appears in the elaborated statement of §7, not merely in a docstring.

### [x] `h = 5` in the final theorem

Likewise the literal `5`. Both constants are visible in the `#check` output.

### [x] The alarm condition is `≥ h`, not `> h`

`cusumTau k h X = hittingAfter (cusumMax k X) (Set.Ici h) 1`, and
`Set.Ici h = {x | h ≤ x}`. Verified against mathlib's definition
(`Mathlib/Probability/Process/HittingTime.lean:65`):

```lean
hittingAfter u s n = fun x ↦ if ∃ j, n ≤ j ∧ u j x ∈ s
  then (sInf {i | n ≤ i ∧ u i x ∈ s} : ι) else ⊤
```

so `cusumTau` is literally `inf {n ≥ 1 : max(S⁺_n, S⁻_n) ≥ h}`. The earlier
one-sided Gate-4 helper `cusumAlarm` used a strict `> h`; it is **not** used by
the final theorem, and `CUSUMBridge.lean` documents the replacement explicitly.

### [x] The hitting time starts at `t = 1`

The third argument of `hittingAfter` is `1`, and this is turned into a usable
fact by `one_le_cusumTau : (1 : ℕ) ≤ cusumTau k h X ω` (`StoppedQuantities.lean`).
It is used substantively: `lintegral_slice_expAbs_scoreAt_le` proves the `m = 0`
slice is **empty** precisely from `1 ≤ τ`.

### [x] Lean `X n` corresponds consistently to mathematical `Z_{n+1}`

The convention is *derived* from the recursion shape, not assumed, and then
pinned by four lemmas: `innov_succ : innov X (n+1) = X n`,
`walk_succ : walk X (n+1) ω = walk X n ω + X n ω`,
`walk_succ_innov : walk X (n+1) ω = walk X n ω + innov X (n+1) ω`, and
`walk_eq_sum_innov : walk X n ω = ∑ s ∈ Finset.range n, innov X (s+1) ω`.
The source additionally flags the off-by-one alternative
(`T n = ∑ s ∈ Finset.Icc 1 n, X s`) as wrong under this convention and states
that it is deliberately not used.

### [x] `scoreAt` represents `Z_τ`

`scoreAt X τ = stoppedValue (innov X) τ`, and
`scoreAt_of_eq_coe : τ ω = m+1 → scoreAt X τ ω = X m ω` — i.e. on `{τ = m+1}` the
stopped score is `X m = Z_{m+1} = Z_τ`. This lemma is used, not just stated: it
is what rewrites the integrand inside `lintegral_slice_expAbs_scoreAt_le`.

### [x] `walkAt` represents `T_τ`

`walkAt X τ = stoppedValue (walk X) τ`, and
`walkAt_of_eq_coe : τ ω = m → walkAt X τ ω = ∑ j ∈ Finset.range m, X j ω`.
Combined with `ae_stopped_quantities_eq`, on `{τ = m+1}` this is
`∑_{j<m+1} X_j = Z_1 + … + Z_{m+1}` — the terminal increment **is** included.

### [x] `cusumTauReal` represents a finite `τ` a.e.

`cusumTauReal k h X ω = ((cusumTau k h X ω).untopA : ℝ)`. Finiteness a.e. comes
from `ae_cusumTau_ne_top`, which is derived from
`measure_never_forced_eq_zero` under `q < 1` — itself derived from the Gaussian
law, not assumed.

### [x] The `WithTop` fallback is confined to a null event

`cusumTau` is `WithTop ℕ`-valued and is **never silently coerced**. On `{τ = ⊤}`,
`stoppedValue` evaluates at `WithTop.untopA = WithTop.untopD (Classical.arbitrary _)`,
an unspecified element. The source states plainly that this is *not* provably `0`
and does not pretend otherwise. It is confined to a null set by
`ae_cusumTau_ne_top` / `ae_exists_succ_cusumTau` / `ae_stopped_quantities_eq`.
The `ℕ`-valued object used for the exponential moment is the *forcing* time
`forcingNat`, whose `sInf` junk value `0` is made harmless by the same null-set
argument.

### [x] Independence is `iIndepFun X μ`

Mutual independence of the whole family, as it appears in the `#check` output:
`ProbabilityTheory.iIndepFun X μ`. Not pairwise, not a product-space
construction (the source notes "no explicit infinite product probability space is
constructed"). It also supplies the probability-measure instance —
`haveI := hindep.isProbabilityMeasure` (`SmallMoment.lean:135`) — so `μ` is a
probability measure as a consequence of the stated hypotheses, not an
unstated extra.

### [x] The Gaussian marginal law is `μ.map (X j) = gaussianReal 0 1`

Exactly as in the `#check` output:
`MeasureTheory.Measure.map (X j) μ = ProbabilityTheory.gaussianReal 0 1`. Both the
one-step exponential moment (`lintegral_expAbsScore_eq_gaussExpMoment`) and the
forcing probability `q = gaussianReal 0 1 (Set.Iic (h+k)) < 1`
(`measure_le_eq_gaussianReal`, `gaussianReal_Iic_lt_one`) are **derived** from this
pushforward identity, not assumed as separate moment hypotheses.

### [x] The stopped score is NOT assumed `N(0,1)`

Nowhere is `scoreAt` given a law. `ReBaseGuardIdentity.lean` says so explicitly:
*"the stopped score `Zτ = X_{τ-1}` is not asserted to be `N(0,1)`. Only the
one-step law is used, through the Cauchy–Schwarz slice bound."* The `L²` control
is obtained from `x² ≤ (4/a²)e^{a|x|}` applied to the slice-summed exponential
moment — a route that never needs the stopped law.

### [x] No `τ`/`Tτ` independence is assumed

Confirmed by reading the proofs, not only the comments. The stopped-walk moment
is obtained by decomposing over `{τ = m}` and applying Cauchy–Schwarz to
`∫_{τ=m} e^{a|T_m|} ≤ (∫ e^{2a|T_m|})^{1/2}·μ{τ=m}^{1/2}` — an inequality valid
for *dependent* factors. The only independence used is among the **one-step**
variables `X j` (`iIndepFun_expAbsScore`, `lintegral_expAbs_walk_le_prod`), which
is a hypothesis of the model, not a claim about `τ`.

### [x] No invalid factorization over `{τ = m}` occurs

The slice bounds never write `∫_{τ=m} f = μ{τ=m}·∫ f`. They use
`setLIntegral_le_of_sq_le`, i.e. Cauchy–Schwarz with exponents `p = q = 2`. The
final assembly (`integrable_absZ_mul_exp_of_separate`) likewise uses only the
elementary AM–GM bound `2xy ≤ x² + y²` — no product measure, no conditional
independence.

### [x] The final theorem literally represents the target identity

`#check` output (§7) reads, term by term:

| Target | Lean |
|---|---|
| `Z_τ` | `scoreAt X (cusumTau (1 / 2) 5 X) ω` |
| `T_τ` | `walkAt X (cusumTau (1 / 2) 5 X) ω` |
| `τ` | `cusumTauReal (1 / 2) 5 X ω` |
| `exp(−e·T_τ − (e²/2)·τ)` | `Real.exp (-e * walkAt … - e ^ 2 / 2 * cusumTauReal …)` |
| `E[·]` | `∫ (ω : Ω), … ∂μ` |
| `d/de …\|₀` | `HasDerivAt (fun e => …) (…) 0` |
| `−E[Z_τT_τ]` | `-∫ (ω : Ω), scoreAt … * walkAt … ∂μ` |

**Match: exact.**

---

## Scope observations (not failures)

Recorded so a later reader is not surprised. Neither affects the theorem.

1. **The filtration is the natural filtration of the detector statistic**, not
   the innovation filtration: `cusumFiltration = Filtration.natural (cusumMax k X) …`.
   `isStoppingTime_cusumTau` is a genuine stopping-time statement with respect to
   *that* filtration. This is sufficient here because the final chain uses only
   the measurability of `{τ = m}` and the forcing bound — **no optional stopping
   theorem is invoked anywhere**, so the coarser filtration costs nothing. The
   source states the choice openly.
2. **Gate 4's `cusumStat` / `cusumAlarm` / `forcingTime`** are one-sided,
   pathwise, strict-`>` helpers retained from an earlier gate. Of these only
   `forcingTime` feeds the final theorem (through `forcingNat`), and it is a
   *forcing* time, not the alarm time — the strictness there is harmless because
   `h + k < X n ω` forces `> h`, which implies the `≥ h` alarm.

---

## Verdict

```text
Lean build:              PASS  (lake build exit 0, 8717 jobs)
Direct compilation:      PASS  (10/10 modules, exit 0, no errors)
Bypass scan:             PASS  (0 matches for all five patterns)
Axiom audit:             PASS  (9/9 theorems, baseline axioms only)
Final theorem #check:    PASS  (statement matches the frozen model exactly)
Model correspondence:    PASS  (17/17 checklist items)
```

**No substantive item failed. The Lean phase does not block closure.**
