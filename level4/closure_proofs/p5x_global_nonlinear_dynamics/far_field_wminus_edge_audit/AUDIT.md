# P5X — Far-Field Minus-Chart Edge-Localization Audit

`PRE_FREEZE_FAR_FIELD_EDGE_LOCALIZATION_AUDIT`. Not R9, not a binding
checkpoint, no production. **Nothing historical changed.**

```text
RESULT   FAR_FIELD_EDGE_ROUTE = FAIL
         Edge localization gains only 1.09x - 5.80x, against the ~30-100x
         needed.  Worst required grid falls from 8463 to 4708 -- still 3.06x
         over the 1536 cap.
FAILURE  FF-D (tail mass x global range still dominates), mechanism FF-A
         (weight not concentrated near l at the worst drift, e = 3).
```

---

## 1. Exact edge geometry — clean, and confirmed

`q_-(z) = w^- e^{-z-1/2}` with `l = log(w^-) - 1/2`, so

```text
q_-(l) = w^- / w^- = 1        EXACTLY
q_-(l+s) = w^- e^{-(l+s)-1/2} = e^{-s} q_-(l) = e^{-s}
```

**The image leaves the edge as `e^{-s}`, independent of the cell.** Verified at
`zeta^- = 0.001, 0.1, 0.5, 0.99` and `s = 0, 0.05, 0.2`: all match `e^{-s}` to
12 digits. Symmetrically `q_+(z) = e^{z-u}`, so near `z = l` the image sits in
the corner `(zeta^+ ~ e^{-D}, zeta^- ~ 1)` with `D = u - l`.

## 2. Weight concentration — the premise only half holds

`W_e(z) = E^-(z) phi(z+e) ~ exp(-z - (z+e)^2/2)`, which **peaks at `z = -e-1`**,
not at `l`. Over the state square `l in [-6.756, -0.498]`, so:

| `e` | peak `z` | peak interior to `(l,u)`? |
|---|---|---|
| 2 | `-3.00` | yes for `l < -3.00` |
| 3 | `-4.00` | yes for `l < -4.00` |
| 4 | `-5.00` | yes for `l < -5.00` |
| 5 | `-6.00` | yes for `l < -6.00` |
| 6 | `-7.00` | **no — always at the edge** |
| 6.9 | `-7.90` | **no — always at the edge** |

Fraction of `int E^- phi` inside `[l, l+s0]`:

| `e` | `zeta^-` | total mass | `s0=0.2` | `s0=0.5` | `s0=1.0` | `s0=2.0` |
|---|---|---|---|---|---|---|
| 2 | 0.01 | `7.19e+00` | `0.0154` | `0.0510` | `0.1536` | `0.5151` |
| 4 | 0.01 | `2.58e+01` | `0.1664` | `0.3978` | `0.6987` | `0.9593` |
| 6 | 0.01 | `7.75e+00` | `0.3965` | `0.7356` | `0.9444` | `0.9988` |
| 4 | 0.90 | `3.00e-04` | `0.6095` | `0.9113` | `0.9938` | `1.0000` |

**The cells carrying the largest weight are exactly the cells with the worst
concentration.** At `e = 4`, `zeta^- = 0.01` carries mass `25.8` with only `40%`
inside `s0 = 0.5`, while `zeta^- = 0.9` concentrates beautifully but carries mass
`3e-4`.

## 3. The split, and why it cannot deliver

`Ky <= R_local(s0) x mass_near(s0) + R_global x mass_tail(s0)`, tail mass
computed by the same Arb Gaussian machinery, no `z`-panels.

At `e = 4`, `zeta^- = 0.01` (`R_global = 77.14`, total mass `25.77`, old
`Ky = 1987.5`):

| `s0` | `mass_near` | `mass_tail` | `R_local` | new `Ky` | gain |
|---|---|---|---|---|---|
| 0.05 | `1.084` | `24.68` | `0.011` | `1903.9` | `1.044x` |
| 0.20 | `4.287` | `21.48` | `0.121` | `1657.4` | `1.199x` |
| 0.50 | `10.25` | `15.52` | `2.005` | `1217.4` | `1.633x` |
| **0.75** | `14.52` | `11.25` | `11.41` | **`1033.1`** | **`1.924x`** |
| 1.00 | `18.00` | `7.764` | `44.74` | `1404.3` | `1.415x` |
| 2.00 | `24.72` | `1.049` | `1271.5` | `31508` | `0.063x` |

The optimum is shallow and modest. Concentration and locality are in direct
conflict: small `s0` gives a tiny `R_local` but leaves `>95%` of the mass in the
tail; large `s0` captures the mass but `R_local` explodes (`0.011 -> 1271` from
`s0 = 0.05` to `2.0`). The best achievable gain is bounded by roughly
`1/mass_tail_fraction`, and that fraction never drops below `~0.4` where the
weight is largest.

## 4. Applied across the blocker region (fixed rule `s0 = 0.75`, not re-tuned)

| `e` | `R_global` | old `Ky` | new `Ky` | gain | old `G` | **new `G`** | class |
|---|---|---|---|---|---|---|---|
| 2.0 | `11.86` | `85.3` | `78.3` | `1.090x` | `655` | `601` | USEFUL |
| **3.0** | `54.99` | `909.7` | `657.2` | `1.384x` | `6518` | **`4708`** | **FAIL** |
| 4.0 | `77.14` | `1987.5` | `1033.1` | `1.924x` | `8463` | `4399` | FAIL |
| 5.0 | `319.08` | `6734.4` | `2215.1` | `3.040x` | `6899` | `2269` | FAIL |
| 6.0 | `75.16` | `582.3` | `144.5` | `4.029x` | `5441` | `1351` | BARELY_FEASIBLE |
| 6.9 | `224.87` | `331.8` | `57.3` | `5.795x` | `3983` | `687` | USEFUL |

**Worst new required grid `4708` at `e = 3.0` — `3.06x` over the `1536` cap.**
The `§14` early-stop condition was met at `e = 4` and `e = 5` (both still
`>1536` by a comfortable factor) and no further drift was optimised.

The gain is weakest exactly where it is needed most: at `e = 3` the weight peaks
at `z = -4`, interior to the live region for the heavy small-`zeta^-` cells, so
almost nothing is gained by localizing at `l`.

## 5. Cost impact

```text
before this audit   INFEASIBLE (worst G = 8432)
after  this audit   still INFEASIBLE (worst G = 4708)
per e-cell at e = 3, G = 4708:  4708^2 x 6 ms = 36.9 CPU-hours
```

A few dozen cells in `[2, 6.9]` run to hundreds-to-thousands of CPU-hours, and
`[0.072, 0.35]` remains an independent blocker (`G` up to `2362`) that this
audit does not touch at all. The conservative full-cover projection stays far
above the `500` CPU-h target.

## 6. Failure classification

**`FF-D` — tail mass times global range still dominates.** At the optimal `s0`
the tail still carries `43%` of the mass at `e = 4`, multiplied by an
`R_global` that itself grows with drift (`0.667` at `e = 0.25`, `77.1` at
`e = 4`, `319.1` at `e = 5`).

Mechanism **`FF-A`** at the worst drift: the weight peak sits at `z = -e-1`,
interior to the live region for the heavy cells whenever `e < 5.76`, so the
premise "mass concentrates at the edge" simply does not hold on `[2, 5.76]`.

Not `FF-B`: the edge image really is tiny (`q_- in [e^{-s0}, 1]`).
Not `FF-E`: the boundary term was never dominant.

## 7. Recommendation

Per `§17`: **stop opening further SR first-moment certification-technique
audits.** Six architectures have now been measured — R7 centred, direct
residual, displacement-correlated, two-sided supersolution, consumer-adaptive
grids, and edge localization. The consumer-adaptive reframing was real and
retired a factor `~22` in the mid-range; none of the interval-bounding variants
has moved the far field by more than `~6x` against a `~30-100x` requirement.

Record the SR `m = 1` `G3` line as **certification-feasible in principle but
out-of-budget under the frozen resource envelope**: every region has a rigorous
route, the mathematics is settled, and the obstruction is purely the cost of
rigorous range bounds on `[0.072, 0.35]` and `[2, 6.9]`.
