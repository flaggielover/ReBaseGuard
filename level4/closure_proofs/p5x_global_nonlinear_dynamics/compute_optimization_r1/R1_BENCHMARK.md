# P5X Compute Optimization R1 — benchmark result

```text
R1_STOP_GATE          = PASS
ACHIEVED_HALF_WIDTH   = 0.008045668639929672      (24.9x inside the threshold)
FROZEN_THRESHOLD      = 0.2                        (unchanged)
CELL                  = CUSUM, m = 1, e in [0.24, 0.26]   (unchanged from R-A')
MEASURED_SPEEDUP      = 5.286834033745004  (CPU)   ->  STRONG_PASS
CERTIFIED_CORRESPONDENCE = PASS (overlaps, and is strictly inside, the R-A' enclosure)
FULL_COVER_LAUNCHED   = NO
```

R-A′ remains the reference implementation; its `PASS` at `0.014176477298268092`
is untouched, and so is the first certified method's `FAIL`.

---

## 1. Certified result

```text
R_{CUSUM, m=1}(e)  in  [ -1.5843524238144047 , -1.5682610865345454 ]   for every e in [0.24, 0.26]
```

half-width `0.008045668639929672`. The authoritative R-A′ enclosure on the same
cell is `[-1.5902505376455707, -1.5618975830490345]`. The R1 interval is
**strictly contained** in it — the expected relation, since both are valid
enclosures of the same number and R1 propagates a smaller `C`. `|R| <= 1.58435 < 2`
on the binding cell, margin `0.41565` to `H3b`.

## 2. What was run

| item | value |
|---|---|
| resolvent, optimized | `220.70751870968231` (monotone minorant, `t* = 52`, `H_52(0) >= 0.23560592907757061`) |
| resolvent, baseline | `1224.3968088688466` (block forcing at the same drift) |
| reduction factor | `5.547598994483793` |
| sub-cells | `8` (against R-A′'s `40`), `h_sub = 0.00125 <= h_max = 0.0014196550084052` |
| bootstrap closure | `0.4405815838177189 <= 1/2`, verified in interval arithmetic |
| ladder steps used | `0` — resolved at the first candidate |
| tiling | exact |
| certified solves | `24` (against R-A′'s `120`) |
| Bernstein continuum bounds | `16` (against `80`) |
| refinements | `0` |
| precision / order / degree / depth | `256` bits / `N = 120` / `12` / `3` — all unchanged |

## 3. Error budget, worst over the eight sub-cells

| component | R1 | R-A′ |
|---|---|---|
| `C * delta` | `~2.3e-3` | `1.27e-2` |
| second-order Taylor term `(h^2/2) S_2` | `~3.1e-3` | `6.99e-4` |
| sub-cell `e`-range `h` | `1.25e-3` | `2.5e-4` |
| **achieved half-width** | **`8.05e-3`** | `1.42e-2` |

The trade is visible and expected: a smaller `C` shrinks `C delta` by `5.5x`
but widens `h` by the same factor, which grows the second-order term. The first
effect dominates, so the optimized enclosure is *tighter* as well as cheaper.

## 4. Speed

| quantity | value |
|---|---|
| baseline CPU (stored, not re-run) | `6.20` CPU-hours, 5 workers |
| optimized CPU | `1.1727245380555558` CPU-hours, 5 workers |
| **measured CPU speedup** | **`5.286834033745004`** |
| speedup class | **`STRONG_PASS`** (`>= 4.0`) |
| baseline wall | `5173.3 s` |
| optimized wall | `1262.9 s` (wall speedup `4.10x`) |
| peak RSS, parent / worst worker | `64.1 MiB` / `218.1 MiB` |

CPU is the authoritative metric and the worker count was held at 5 to remove the
parallelism confound.

## 5. The pre-registered prediction

`R1_FROZEN_SPEC.md` §11 predicted, before the run: half-width `0.00886`
(band `0.006`–`0.014`), `1.24` CPU-hours, speedup `5.0`. Measured: `0.008046`,
`1.173` CPU-hours, speedup `5.287`. **The prediction held**, inside its band on
all three quantities — in contrast to the R-A′ prediction, which was falsified
on the optimistic side.

## 6. Self-test, before the benchmark

All eight checks of `R1_FROZEN_SPEC.md` §9 passed (`results/r1_selftest.json`),
including: the optimized path calls the unmodified R-A′ certifier; the minorant
is tighter than block forcing at every drift tested (`5.55x`, `4.32x`, `2.46x`,
`1.15x`, `1.005x` at `e = 0.24, 0, 0.5, 1, 2`); `C_opt(0) = 1232.836 <= 1315.79`,
consistent with the independently certified `N-01`; the bound exceeds a Monte
Carlo `E[tau]` spot-check; interval containment holds at a shared drift; the
`e = 0` configuration degenerates to `N-01`'s; the sub-cells tile exactly; and
`empirical_monotonicity_used` is `false` everywhere.

## 7. Where the cost now sits

The resolvent minorant itself costs `~0.1 s`. Per sub-cell the `527.7` CPU-s is
spent almost entirely on three `_kernel_polynomials` assemblies (symbolic
`TriPoly` times the degree-120 coefficient list, then symbolic `z`-integration)
and two Bernstein continuum bounds on degree-`~290` polynomials. **After R1 the
resolvent is no longer a cost driver.** Any further optimization must attack the
symbolic residual — the Taylor order `N` or the candidate degree — and that
would be a different campaign with its own pre-result anchor.
