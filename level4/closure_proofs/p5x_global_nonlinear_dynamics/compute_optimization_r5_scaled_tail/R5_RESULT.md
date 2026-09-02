# P5X R5 — result: the repair works, the frozen gate does not

```text
PRIMARY QUESTION      answered YES (mathematically) / NO (as frozen)
FROZEN GATE           FAIL      failed: Q2, Q3, Q7
R5 CLASSIFICATION     R5_P3_FAIL
RESIDUAL ISSUE        ARB_SPECIAL_FUNCTION_LIMITATION
SELF-TEST             PASS      all 9 binding items + all-k overlap with R4
------------------------------------------------------------------------------
Q3 amplification (frozen)   2.2381e20     threshold 1e12    R4 was 2.1356e17
Q7 runtime      (frozen)    2.2617 ms     budget 2.0 ms     COST_FAIL
Q4 huge x tiny  (frozen)    NO (0)        -- the one criterion it was built for
------------------------------------------------------------------------------
POST-HOC "minimal" variant  amplification 1.0027e2   0.3885 ms   9.38 CPU-h
   vs R4                    2.1356e17 -> 1.0027e2    = 2.1e15x better
   flat across 192..512 bits: 1.0027e2, 1.0028e2, 1.0028e2, 1.0028e2, 1.0028e2
FULL-CELL PROTOTYPE         NOT RUN -- section 20 authorizes it only if all
                            Q1-Q10 pass, and they do not
```

Anchor: Checkpoint G `f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63`, committed and
pushed before any implementation existed.

---

## 1. What the pre-design diagnostic found

The R4 brief attributed the `2^58` to forming `exp(k^2/2-ke) x [Phi(b)-Phi(a)]`
as `~1e55 x ~1e-55`. Measured on the exact R4 `P3` configuration, that is **not**
the mechanism:

| quantity | value |
|---|---|
| cross-`k` cancellation `max_k |G_k I_k| / |sum|` | **`0.9933` = `2^-0.0`** — none |
| rel. radius of `I_k` at `k = 0` | `1.59e-58` |
| rel. radius of `I_k` at `k = +-16` | `1.68e-32`, `6.63e-33` |
| predicted `rad(sum)` from those two terms | `3.4e-41` |
| **measured** `rad(sum)` | **`3.4022e-41`** |

The whole radius comes from the `Phi` *branch*, `(1 + erf(x/sqrt2))/2`, which at
`x = -10.707` cancels 26 digits in `1 + erf`. Directly: `(1+erf)/2` gives
relative radius `1.690e-32`; `erfc(-x/sqrt2)/2` gives `4.575e-56`.

## 2. The algebra is correct — `Q1` proves it

The exponent identity `k^2/2 - ke - (x+e-k)^2/2 = kx - (x+e)^2/2` cancels `k^2`
**exactly** (verified as balls, including at `e = 12`). The regime split is

| regime | condition | `k` range used | formula |
|---|---|---|---|
| B | `k >= u+e` | `6 .. 16` | `I_k = [T(u) - T(l)]/2` |
| D | `l+e < k < u+e` | `-5 .. 5` | direct, each `Phi` on its accurate `erfc` branch |
| C | `k <= l+e` | `-16 .. -6` | `I_k = [T(l) - T(u)]/2` |

with `T(x) = exp(kx - (x+e)^2/2) erfcx(|x+e-k|/sqrt2)`. **`Q1` passes: the scaled
interval overlaps R4's rigorous interval at every one of the 33 values of `k`.**
`L-R5.1` .. `L-R5.9` all stand. The scaled form is *not* invalid — hence
`R5_P3_FAIL`, not `R5_SCALED_FORM_INVALID`.

Non-cancellation is proved, not hoped for: `W = u - l >= 2(c_SR - b_SR) =
0.99616407018867513833`, whence `Phi(b)/Phi(a) >= 3.13312` in B/C and
`Phi(b) - Phi(a) >= 0.19078688886760390794` in D. **Regime F (near-equal tail
probabilities) is impossible.**

## 3. Why the frozen gate fails — `D12`

`Q3 = 2.2381e20`, a factor `1048` **worse** than R4, and `Q7 = 2.2617 ms`,
`COST_FAIL`. Cause: the frozen `erfcx` branch `t > 2 -> hypgeom_u(1/2,1/2,t^2)`.
The identity is right; the evaluator is not. Arb's `U` is excellent on **point**
arguments (`~5e-60`) and loses up to 26 digits on **ball** arguments:

| `t` | ball `U` | monotone-endpoint `U` | `exp(t^2)erfc(t)` | true sensitivity |
|---|---|---|---|---|
| `7.5708` | `1.772e-29` | `4.307e-30` | `1.590e-55` | `7.3e-58` |
| `15.1179` | `2.253e-57` | `3.507e-57` | `7.251e-55` | — |
| `4.7423` | `4.543e-45` | `1.024e-45` | `8.687e-56` | — |

The degradation is erratic in `t`, characteristic of an internal algorithm
switch. I froze the branch on point-argument evidence. Registered `D12`;
residual classification **`ARB_SPECIAL_FUNCTION_LIMITATION`**.

`Q2` fails as a consequence: R5's interval is *wider* than R4's, so
`R5 subset R4` cannot hold. It does overlap R4 (`overlaps_R4 = True`), i.e. both
enclosures are valid — which is exactly what `Q1` already established.

## 4. Why `Q4` was the wrong criterion — `D13`

`Q4` (`huge x tiny = NO`) **passed** — `0` such products — and it is the only
criterion that forced the exponent-folding architecture, hence the `erfcx`
choice, hence `D12`. But `Q4` encodes the brief's hypothesis, which §1 of my own
Checkpoint-G derivation had already measured to be false. A `huge x tiny`
product is harmless when both factors carry full relative accuracy, because
relative error is preserved under multiplication.

This is the third mis-specified criterion in the campaign (`D11`, then `Q4`
twice over). Twice a criterion was frozen from an inherited hypothesis rather
than from the measurement already in hand.

## 5. The post-hoc variants — disclosed as post-hoc

Neither contributes to the gate verdict.

| variant | amplification | class | huge x tiny | `t_patch` | projected SR | total |
|---|---|---|---|---|---|---|
| R4 (reference) | `2.1356e17` | — | yes | `0.3990 ms` | `9.63` CPU-h | `155.63` |
| **frozen R5** | `2.2381e20` | `R5_P3_FAIL` | `0` | `2.2617 ms` | `54.59` | `200.59` |
| post-hoc `expbranch` | `1.0027e2` | `R5_P3_BREAKTHROUGH` | `26` | `0.4777 ms` | `11.53` | `157.53` |
| post-hoc `minimal` | **`1.0027e2`** | `R5_P3_BREAKTHROUGH` | `4` | **`0.3885 ms`** | **`9.38`** | **`155.38`** |

`minimal` is the repair the §1 diagnostic actually implies: keep R4's structure
exactly, and split the `Phi` *difference* by regime so it is formed from `erfc`
values rather than from `(1-x)-(1-y)` or `1+erf`. No exponent folding, no
`erfcx`, no `hypgeom_u`. It costs **less** than R4 (`0.3885` vs `0.3990 ms`).

**Precision sweep — the metric itself is reduced, not hidden:**

| bits | frozen (`hypgeom_u`) | post-hoc `minimal` |
|---|---|---|
| 192 | `2.2381e20` | `1.0027e2` |
| 256 | `3.0293e20` | `1.0028e2` |
| 320 | `2.8926e20` | `1.0028e2` |
| 384 | `3.0348e20` | `1.0028e2` |
| 512 | `3.0383e20` | `1.0028e2` |

Both are flat, i.e. both are fixed condition numbers. R4's was `~2^58`; the
`minimal` repair's is `~2^6.6`. That is a reduction of `2.1e15`, and it is a
property of the *representation*, exactly as R5 set out to achieve.

## 6. Correspondence criterion — `D11` not repeated in either direction

Binding criteria `Q1`/`Q2` are **rigorous vs rigorous**: the R5 Arb interval
against the R4 Arb interval, both enclosures of the same exact `I_k`. Simpson
quadrature and the `y`-space brute force are recorded as **DIAGNOSTIC ONLY** in
`results/r5_gate.json` and can neither pass nor fail the gate. No interval was
widened to contain a non-rigorous reference.

## 7. Prediction scorecard (frozen at Checkpoint G)

| quantity | predicted | measured | verdict |
|---|---|---|---|
| `Q1`, `Q2` | PASS | `Q1` PASS, `Q2` **FAIL** | half |
| `Q3` | `1e0`..`1e4`, `R5_P3_BREAKTHROUGH` | `2.2381e20`, `R5_P3_FAIL` | **miss** |
| `Q4` | NO | NO | **hit** |
| `Q5`, `Q6` | `0`, `0` | `0`, `0` | **hit** |
| `Q7` | `0.5`..`1.5 ms` | `2.2617 ms`, `COST_FAIL` | **miss** |
| `Q8`,`Q9`,`Q10` | PASS | PASS | **hit** |
| gate | PASS | **FAIL** | **miss** |
| projected SR | `12`..`36` CPU-h | `54.59` frozen / `9.38` post-hoc | **miss** |

**4 of 9.** Named risk (i) — "`hypgeom_u` may be markedly slower than `erf`,
threatening `Q7`" — materialised exactly. Risk (ii), `hypgeom_u` near `z -> 0`,
did not; the `t <= 2` branch handled it. Risk (iii), some other `k` dominating,
did not: the post-hoc amplification of `1.0027e2` shows `k = +-16` was indeed the
whole story. I correctly predicted the *achievable* amplification band for the
repair and then froze an evaluator that could not reach it.

## 8. Second-moment stability (analytic only, as required)

Differentiating the exact identity in `k`, and using the same exponent identity:

```text
int_l^u z   e^{kz} phi(z+e) dz = (k-e) I_k - [e^{E(u)} - e^{E(l)}]/sqrt(2pi)
int_l^u z^2 e^{kz} phi(z+e) dz = I_k + (k-e) d/dk I_k
                                 - [u e^{E(u)} - l e^{E(l)}]/sqrt(2pi)
```

The new terms are bare exponentials — no `erfcx`, no tail difference, so no
cancellation site at all. **`R5_SECOND_MOMENT_STABILITY = DIRECT_WITH_DERIVATIVE_SCALING`.**
Not implemented, as required.

## 9. R3 retry fallback — recorded, not executed

R3's local architecture is sound but projects to `12,084` CPU-hours (`128`
`z`-panels per patch at `3.911 ms`). A retry would at best shave the panel
constant; it cannot approach the panel-free architecture. **R5 is preferred over
the R3 retry on cost by three orders of magnitude**, and that conclusion is
unchanged by the frozen gate's failure, because the failure is in an `erfcx`
evaluator choice, not in the panel-free architecture. Not executed.

## 10. What R5 establishes and does not

**Established.** The `2^58` is caused by the `1 + erf` branch, measured
term-by-term, not by `huge x tiny`. The exponent-cancellation identity is exact.
The regime decomposition is total, deterministic and rigorous, and
non-cancellation is *proved* from `W >= 0.99616...`. `Q1` confirms algebraic
correspondence with R4 at all 33 values of `k`. A representation exists that
reduces the amplification metric from `2.1356e17` to `1.0027e2` — flat across
192-512 bits — at `0.3885 ms` per patch, cheaper than R4.

**Not established.** The frozen gate did **not** pass. `Q3` and `Q7` fail on the
frozen `erfcx` evaluator, and `Q2` fails in consequence. The `1.0027e2` figure
comes from a **post-hoc** variant and has the evidential status of a diagnostic,
not of a gated result. No full-cell prototype was run — §20 authorizes it only
on a full `Q1`-`Q10` pass. No second-moment implementation. No production cover.

**Recommended R6 (not started).** Re-freeze with the `erfcx`/`hypgeom_u`
requirement removed and `Q4` dropped or restated as a *reporting* field rather
than a gate criterion, then re-run this identical configuration. On the measured
evidence that gate should pass at `R5_P3_BREAKTHROUGH` and authorize the
full-cell prototype. The scientific content of the repair is already proved and
measured; what remains is a correctly specified gate.
