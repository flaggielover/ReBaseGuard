# P5X Compute Optimization R2 — frozen specification

Frozen **before** any R2 implementation or benchmark, and committed at
Checkpoint D. R1 (`9e19c70`) is the baseline and is not modified. The certified
target, the scope `e in [0,12]`, the `0.2` gate threshold and every P5X theorem
statement are unchanged.

---

## 1. Selected candidates (two, per the cap)

Both attack the measured `~85-89%` bottleneck. Both are justified by
measurement in `R2_PROFILE_AND_AUDIT.md`, not by expectation.

### C1 — Bernstein subdivision depth reduction
`CLASS = CERTIFIED_BOUND_REFACTOR`

A shallower Bernstein subdivision yields a **looser but still rigorous** bound
(the convex-hull property holds at every depth). Frozen rule:

```text
depth := min{ d in (0, 1, 2, 3) : C * delta(d) <= 0.05 }        (0.05 = 0.19/3.8, a
                                                                  frozen budget fraction)
if no d qualifies -> ABORT the benchmark (do not fall back, do not widen)
```

The ladder is bounded, deterministic and evaluated at run time, exactly as R1's
`n_sub` ladder was. Escalation can only tighten.

### C2 — dense Taylor-shift replacement for `_affine_to_unit_square`
`CLASS = CERTIFIED_BOUND_REFACTOR`

Replace the `O(deg^4)` dictionary product loop by the standard
**scale-then-synthetic-division** algorithm on a dense coefficient array:

```text
given P(r,t) = sum_{i,j} c_{ij} r^i t^j , substitute r = a + b*rho , t = c + d*sigma
  step 1 (scale)  : c_{ij} <- c_{ij} * b^i * d^j                      O(deg^2)
  step 2 (shift r): for each column j, Horner synthetic division by a  O(deg^2) per column
  step 3 (shift t): for each row i,    Horner synthetic division by c  O(deg^2) per row
```

In exact arithmetic this produces the **same polynomial**; in ball arithmetic
both are outward-rounded enclosures of the same coefficients. Complexity drops
from `O(deg^4)` to `O(deg^3)` with scalar (not dict) operations.

**Neutrality.** Same detector, `m`, drift, Fredholm equation, kernel, reward,
state space, stopping convention, `R(e)`/`S(e)` definitions, candidate degree,
Taylor order, precision, enclosure meaning, theorem-consumer interface and gate
semantics. Only the range-bound arithmetic changes. Neither candidate is
`SCIENTIFIC_METHOD_CHANGE` or `SCIENTIFIC_SCOPE_CHANGE`.

### Explicitly rejected, on measurement
Taylor-order reduction (`<= 1.3x`, spends the truncation margin); candidate-degree
reduction (`14%` of degree, degrades the candidate); kernel-path caching
(`< 1.02x`); `r_powers`/`t_powers` memoisation (addresses `O(deg^2)`, not the
`O(deg^4)` loop); the SR softplus minorant (optimizes a part that already costs
`0.1 s`). **Deferred to R3:** the state-patch x `z`-panel re-architecture, the
only identified lever that could be `~30x` and the only one that would make SR
tractable at all.

## 2. Frozen parameters

Unchanged from R1: Taylor order `N = 120`; candidate degree `12`; quadrature
`400`; `scale_bits = 50`; precision `256` bits; resolvent = R1's drift-explicit
monotone minorant; sub-cell rule `h = 1/(4 a C)`; exact rational drifts with
denominator `10^7`; workers `5`. Only `subdivision_depth` becomes rule-driven
(C1) and `_affine_to_unit_square` is replaced (C2).

## 3. Frozen benchmark suite

| id | content | runnable? |
|---|---|---|
| **B1** | full gate, CUSUM `m = 1`, first moment, `e in [0.24, 0.26]`, 8 sub-cells — direct CPU comparison to R1's stored `1.1727245380555558` CPU-hours at the same 5 workers | **yes** |
| **B2** | primitive-level: one `_max_abs_on_reachable` at `N = 120` on the same residual pair, reference vs optimized — isolates C1 and C2 attribution | **yes** |
| **B3** | SR, `m = 1`, near origin | **NOT RUNNABLE — no SR certifier exists in P5X** |
| **B4** | CUSUM, `m = 5` | **NOT RUNNABLE — no `m > 1` certifier exists in P5X** |

`B3` and `B4` are recorded as unrunnable rather than substituted with easier
cells. Their costs remain **estimates composed from measured primitives**, as
`R2_PROFILE_AND_AUDIT.md` §2 requires. The second-moment case is covered inside
`B1`, which already certifies the derivative equation and therefore exercises the
dominant path twice per sub-cell.

## 4. Baselines

Stored R1 authoritative values, not re-run: `1.1727245380555558` CPU-hours,
`1262.9 s` wall, 5 workers, 8 sub-cells, 24 certified solves, 16 Bernstein
bounds, half-width `0.008045668639929672`, enclosure
`[-1.5843524238144047, -1.5682610865345454]`. Same-session normalisation is
provided by `B2`, whose reference arm re-runs the unmodified routine in this
session.

## 5. Mandatory self-test, before any benchmark

| id | check |
|---|---|
| `S1` | C2 output agrees with the reference `_affine_to_unit_square`: every coefficient ball of the two overlaps, on the real production polynomials |
| `S2` | the resulting Bernstein bound from C2 is within a factor `2` of the reference bound at the same depth |
| `S3` | same certified target: the optimized path calls the unmodified `ra_certifier` equation assembly |
| `S4` | `e = 0` consistency: enclosure still contains `R(0) = 0`'s witness `ghat(0,0)` to `1e-12` |
| `S5` | exact-rational drift preserved: `e_0` denominators are `10^7`, sub-cells tile exactly |
| `S6` | no empirical monotonicity used anywhere |
| `S7` | the depth ladder is deterministic and bounded |
| `S8` | first/second-moment interfaces unchanged (the derivative equation is certified identically) |

Any failure `->` STOP; no benchmark.

## 6. Acceptance and speedup categories (frozen)

Certification: same target; half-width `<= 0.2`; the R2 enclosure must **overlap**
R1's `[-1.5843524238144047, -1.5682610865345454]`.

```text
SPEEDUP = R1_cpu_hours / R2_cpu_hours          (CPU authoritative)
< 2x        -> R2_WEAK
2x  - <4x   -> R2_MODERATE
4x  - <8x   -> R2_STRONG
>= 8x       -> R2_BREAKTHROUGH
```

Campaign class, from the re-projected total:

```text
> 10,000 CPUh        -> R2_USEFUL_BUT_MORE_OPT_REQUIRED
5,000 - 10,000       -> borderline; explicit resource adjudication
2,000 - 5,000        -> R2_READY_FOR_FULL_COVER
<= 2,000             -> R2_BREAKTHROUGH_READY_FOR_FULL_COVER
```

Not changed after the run.

## 7. Abort rule

Abort and record `FAIL` if: any self-test fails; the depth ladder finds no
qualifying `d`; the R2 enclosure does not overlap R1's; the half-width exceeds
`0.2`; or any Arb positivity/containment/tiling check raises. No parameter
change after a result, no fallback candidate.

## 8. Pre-registered prediction

Recorded so the outcome can falsify it:

```text
predicted B1 CPU-hours = 0.13   (band 0.08 - 0.30)
predicted speedup      = 9.0    (band 4 - 15)  -> R2_STRONG or R2_BREAKTHROUGH
predicted total P5X    = ~3.4e3 CPU-hours       -> likely R2_READY_FOR_FULL_COVER
```

## 9. What R2 will not do

No full cover, no SR campaign, no scope reduction, no threshold change, no
modification of R1 or any historical artifact, and no implementation of the
deferred R3 re-architecture.
