# CUSUM measurement lane — replacing the extrapolated multipliers

Lightweight deliverable of R3 §22. The goal is to stop using `x11` and `x25/11`
as unmeasured assumptions. Building full `m>1` certifiers would **not** be
lightweight, so the multipliers are replaced by **operator counts derived from
`P5X-T1` / `PROOF.md L2`, composed with R2-measured primitive costs** — a
measured-structure figure rather than a guess.

## 1. Operator counts per `e`-sub-cell

From `P5X-T1(c)`, a window `m` first moment needs `g_r` for `r = 0..m-1`, each
with its `e`-derivative for the Taylor-in-`e` model, plus the backward functions
`h_1..h_{m-1}` and sources `S_1..S_{m-1}`:

```text
first-moment certified functions(m)  = m (values) + m (derivatives) + 2(m-1) (h_j, S_j)
                                     = 4m - 2
```

From `PROOF.md L2`, the second moment needs the pair functions `G_{r,r'}` for
`0 <= r' <= r <= m-1`, i.e. `m(m+1)/2` of them, each with its `e`-derivative:

```text
second-moment certified functions(m) = m(m+1)
```

| `m` | first moment | second moment |
|---|---|---|
| 1 | 2 | 2 |
| 2 | 6 | 6 |
| 3 | 10 | 12 |
| 5 | 18 | 30 |
| **sum** | **36** | **50** |

Unit = the `m = 1` first-moment cost = **2** certified functions (one value, one
derivative), which is exactly what R1/R2 measure.

```text
MEASURED-STRUCTURE MULTIPLIER = 86 / 2 = 43x
   first-moment part  = 18x   (previously ASSUMED 11x)
   second-moment part = 25x   (previously assumed 25x, and it was right)
```

## 2. What was wrong with `x11`

The `x11` figure was `sum_m m = 1+2+3+5`. It counted only the `g_r` value solves
and silently omitted (i) the `e`-derivative equation that the R-A′ Taylor-in-`e`
model requires for every certified function and (ii) the `2(m-1)` backward
functions `h_j` and sources `S_j` that `P5X-T1(c)` needs. The corrected
first-moment multiplier is `18x`, `64%` higher.

The second-moment `25x` was `sum_m m(m+1)/2`, which happens to coincide with the
correct count once the derivative equations are included, because
`m(m+1) / 2 = m(m+1)/2`. It survives unchanged.

## 3. Consequence

Every projection in R1, R2 and the pre-R3 state used `36x`. The corrected value
is `43x`, so **all prior CUSUM and SR totals were understated by `19%`**:

| quantity | with `36x` | with `43x` |
|---|---|---|
| CUSUM all `m`, both moments (post-R2) | `122` CPU-h | **`146` CPU-h** |
| SR all `m`, both moments (pre-R3 architecture) | `~28,665` | **`~34,239`** |
| total P5X (pre-R3) | `~28,787` | **`~34,385`** |

This is a correction to the campaign's own bookkeeping, made before the R3 gate
was run and applied to the frozen R3 PASS formula.

## 4. What this lane does NOT claim

It does not measure an `m>1` certification, because no `m>1` certifier exists.
It replaces an arithmetic assumption with an arithmetic derivation from the
frozen reduction, and composes it with R2-measured per-function primitive costs.
Building and timing a real `m = 2` path remains open work, and until it is done
the per-function cost is assumed equal to the measured `m = 1` per-function cost
— an assumption this document states rather than hides.
