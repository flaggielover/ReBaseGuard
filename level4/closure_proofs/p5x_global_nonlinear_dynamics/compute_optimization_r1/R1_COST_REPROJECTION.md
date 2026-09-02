# P5X cost re-projection after Compute Optimization R1

Computed only after the benchmark. The scientific scope is unchanged: both
detectors, `m in {1,2,3,5}`, first and second moments, `e in [0, 12]`.

## 1. Measured basis

`527.73` CPU-s per sub-cell (`4221.81 / 8`), `218.1 MiB` per worker, three
certified solves and two Bernstein bounds per sub-cell, refinement rate `0`.

## 2. Cover size, optimized vs baseline

`h(e) = 1/(4 a C(e))`, so cells per unit `e` is `2 a C(e)`:

| `e` | `C` block forcing | `C` monotone minorant | gain | cells/unit `e` (optimized) |
|---|---|---|---|---|
| `0` | `5323.42` | `1232.84` | `4.32x` | `1967` |
| `0.1` | `3744.89` | `567.16` | `6.60x` | `905` |
| `0.25` | `1124.65` | `207.75` | `5.41x` | `332` |
| `0.5` | `150.88` | `61.36` | `2.46x` | `98` |
| `1` | `19.56` | `16.94` | `1.15x` | `27` |
| `2` | `5.76` | `5.73` | `1.00x` | `9.1` |
| `5.5` | `2.00` | `2.00` | `1.00x` | `3.2` |
| `12` | `1.00` | `1.00` | `1.00x` | `1.6` |

| cover | cells (block) | cells (optimized) | ratio |
|---|---|---|---|
| `[0, 12]` (frozen `e_far`) | `1565` | `334` | `4.69x` |
| `[0, 5.5]` (`= [0, e_star]`, `C1` only) | `1553` | `323` | `4.82x` |

## 3. Projection, CUSUM

| scope | sub-cells | CPU-hours |
|---|---|---|
| `m = 1`, first moment, `[0, 12]` | `334` | **`49.0`** |
| `m = 1`, first moment, `[0, e_star]` | `323` | `47.3` |
| `m in {1,2,3,5}`, first moments (`sum m = 11`) | `~3674` | `~539` |
| `m in {1,2,3,5}`, second moments (`sum m(m+1)/2 = 25`) | `~8350` | `~1225` |
| **CUSUM total (`P5X-T4` + `P5X-T6`)** | `~12000` | **`~1764`** |

## 4. Projection, SR, with the corrected domain `b_SR = log(1+A)`

`D1`'s correction enlarges the state square side by
`log(1+1/A) = 1.918e-3`, i.e. `+0.031%` per side and `+0.061%` in area — a
**negligible** cost effect. The real SR cost drivers are different:

| driver | effect |
|---|---|
| higher barrier: `c_SR = 6.7555` vs `c_CUSUM = 5.5` | the aligned chart must climb further, so the resolvent is worse: by the softplus domination `softplus(v) >= max(0,v)` the SR chart dominates the CUSUM one-sided chart with `h -> log A`, giving `C_SR / C_CUSUM = 3.86x` at `e = 0`, `2.17x` at `0.25`, `1.53x` at `0.5`, `1.27x` at `1`, `1.21x` at `2` — a cover roughly `2.5x` larger |
| reachable-set structure | SR has no CUSUM-style triangle collapse; the existing `Gamma_SR` certificate needed `1210` cells and `96k` innovation intervals against CUSUM's `4` Bernstein patches, i.e. `5`–`8x` the per-cell certificate cost |
| corrected domain (`D1`) | `+0.06%`; immaterial |

```text
SR total  ~  1764 x 2.5 x (5 to 8)  =  22,000 - 35,300 CPU-hours   (midpoint ~28,700)
```

**The R1 minorant as implemented is CUSUM-only.** The softplus domination above
shows the same machinery extends to SR with `h -> log A`, but that extension is
**not implemented and not claimed here**; it needs its own pre-result
specification.

## 5. Total, and what it means

| | with R1 | without R1 |
|---|---|---|
| CUSUM (all `m`, both moments) | `~1.8e3` | `~9.3e3` |
| SR (all `m`, both moments) | `~2.9e4` | `~1.5e5` |
| **total P5X `T4` + `T6`** | **`~3.0e4` CPU-hours** | `~1.6e5` CPU-hours |

| effective cores | wall-clock, optimized total |
|---|---|
| 8 | `~3800 h` (158 d) |
| 16 | `~1900 h` (79 d) |
| 32 | `~950 h` (40 d) |
| 64 | `~475 h` (20 d) |
| 128 | `~240 h` (10 d) |

**RAM** `~218 MiB` per worker (`~28 GiB` at 128 cores). **Storage** `~1.5 KiB`
per sub-cell record, `~63 MiB` total — negligible. **Refinement rate** `0` by
construction.

**Bottleneck** after R1: the per-cell symbolic residual (three
`_kernel_polynomials` assemblies at degree `~145` in `z` and two Bernstein
bounds at degree `~290`). The resolvent, at `0.1 s`, is no longer a cost driver.

R1 is a genuine `5.3x`, and it does **not** bring the campaign inside the
`300`–`800` CPU-hour planning budget of `CERTIFICATE_PLAN.md`. That budget
remains wrong by roughly `40x` even after the optimization.

## 6. Theorem-based cover compression

`results/r1_cover_compression.json`, derived from `P5X-T3` and **not** chosen
for cost:

```text
sup_{|e| in [c_D, c_D+1]} B_D(e)  =  1.2649965374940489448718...  <  2   (continuum interval cover, 4000 panels)
B_D(c_D + 1) = 0.5477150290551...,  and B_D is proved strictly decreasing beyond c_D + 1   (PROOF.md L3.4)
=>  CERTIFIED_E_STAR:  CUSUM  e_star = c_D = 5.5
                        SR     e_star = c_D = 6.755531464321473...
```

(The two suprema coincide because `B_D` depends on `e` only through
`a = c_D - |e|`.)

**Verdict: `THEOREM_BASED_COVER_COMPRESSION = YES`, but only for the `C1`
first-moment cover, and the saving is immaterial.** For `|e| >= e_star` the
proved far-field majorant already gives `|R| < 2`, so those cells need no
Fredholm solve for `P5X-T4`. That removes `334 - 323 = 11` sub-cells out of
`334`, i.e. `3.3%` of the CUSUM `m = 1` cover — because the optimized cover cost
is concentrated near the origin, not in the far field.

It does **not** apply to the `C2` second-moment cover: no far-field lemma for
`E[Rbar^2 | e]` has been proved. Such a lemma is a short, identified extension of
`L3`, but it is not proved here and is not smuggled in.

`[0, 12]` is therefore **retained** as the frozen range. The compression is
recorded as mathematically available and economically irrelevant.
