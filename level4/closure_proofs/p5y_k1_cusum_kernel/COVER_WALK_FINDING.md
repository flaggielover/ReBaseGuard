# CUSUM frozen cover walk — reconstruction and a spec inconsistency

## What was implemented

The frozen walk, exactly as specified, with no redesign and no endpoint
perturbation:

```text
start        e = 0                                   (frozen)
end          e_star = 11/2 = 5.5                     (frozen c_CUSUM)
step rule    h(e) = 1 / (4 a C(e)),  a = 2 phi(0)    (cover_cusum.json)
width        2h   -- h is the HALF-width             (R1_COST_REPROJECTION)
C(e)         R1 drift-monotone resolvent at the cell's LEFT endpoint,
             the smallest |e| of the cell and so the worst case by M2
rationals    every endpoint exact with denominator 10^7   (R1_FROZEN_SPEC T7)
rounding     the step is FLOORED onto that grid, which can only shorten a
             cell and is therefore conservative
tiling       the final cell is truncated at e_star
```

The half-width reading is verified, not assumed: `R1_COST_REPROJECTION` lists
"cells/unit e (optimized)", and `2 a C(e)` reproduces that column at **all seven
tabulated points** — 1967.3/1967, 905.1/905, 331.5/332, 97.9/98, 27.0/27,
9.1/9.1, 3.2/3.2. The underlying `C(e)` likewise reproduces the doc's column:
1232.836/1232.84, 207.754/207.75, 5.732/5.73.

## Structural invariants — all PASS

```text
start 0            end 55000000/10^7 = 5.5      splice match      yes
no gaps            no overlaps                  monotone          yes
total measure 5.5000000000 exactly              deterministic     byte-identical
canonical table sha256 3519f2ecfc8314ba423d2b8354642c1d...
```

## The inconsistency

```text
frozen manifest subcell_count        323
greedy walk under the frozen rule    326
```

This is **not** a rounding artifact and **not** tunable. The 323 is the
continuum cost estimate:

```text
int_0^5.5 2 a C(e) de  =  322.49   ->  ceil  =  323
```

The greedy walk necessarily exceeds that integral, because it holds `C` fixed at
each cell's left endpoint while `C` decreases across the cell, so every step is
shorter than the continuum density would allow. The 1.1% excess (326/322.49 =
1.011) is exactly that discretisation gap.

So the frozen manifest records a **cost-model estimate** in a field named
`subcell_count`, while the rule it also records produces 326.

## Why this blocks wiring, rather than being a harmless rounding difference

The two cannot simply be reconciled by taking 323:

* the driver enumerates the CUSUM work universe as `323 x 19`, and the frozen
  `work_conservation.total_units = 12255 = (323 + 322) x 19`. A 326-cell cover
  makes it 12,312, contradicting a frozen invariant that the driver, its tests
  and its independent review all enforce;
* forcing 323 cells requires widening cells beyond `2h`, and the step rule
  exists precisely to keep the cover's Taylor-model error inside `B_cover`.
  Widening past the rule would breach a frozen budget line.

Taking 326 is scientifically safe (a finer cover is more conservative) but
violates the frozen work universe. Taking 323 is governance-consistent but
breaches `B_cover`. Neither is available without a checkpoint decision, and this
task may not modify the checkpoint.

## Classification

`FROZEN_SPEC_INCONSISTENCY` — the frozen cover manifest's `subcell_count` (323,
a continuum estimate) disagrees with the frozen step rule it records (326).
Not an implementation defect: the walk reproduces every published `C` and
density value exactly.
