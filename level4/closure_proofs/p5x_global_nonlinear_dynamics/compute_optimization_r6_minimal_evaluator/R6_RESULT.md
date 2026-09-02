# P5X R6 — result: GATE PASS, the conditioning blocker is closed

```text
FROZEN GATE        PASS      G1..G10 all pass
AMPLIFICATION      1.0027e2  threshold 1e12    R6_BREAKTHROUGH
   vs R4           2.1356e17 -> 1.0027e2       improvement 2.130e15x
   vs R5 (frozen)  2.2381e20 -> 1.0027e2
RUNTIME            0.3757 ms/patch             EXCELLENT (budget 2.0 ms)
   vs R4           0.3990 ms                   R6 is CHEAPER than R4
PROJECTED SR       9.07 CPU-hours              R6_BREAKTHROUGH
PROJECTED TOTAL    155.07 CPU-hours
```

Anchor: Checkpoint H `7800911d4ca5b93f1f4317494669f228501ef42a`, pushed before
this evaluator was implemented.

## G10 — a representation repair, not a precision patch

| bits | amplification |
|---|---|
| 192 | `1.0027e2` |
| 256 | `1.0028e2` |
| 320 | `1.0028e2` |
| 384 | `1.0028e2` |
| 512 | `1.0028e2` |

Flat. The condition number is `~2^6.6`, against R4's `~2^58` and R5-frozen's
`~2^67`. Accuracy now scales with the working precision, which is exactly what
"the metric itself is reduced" means.

## What made the difference

One change: split the `Phi` **difference** by regime so it is formed from `erfc`
values, never from `1 + erf` (which cancels 26 digits in the deep left tail) and
never from `(1-x) - (1-y)` (which re-cancels in the deep right tail). No
`erfcx`, no `hypgeom_u`, no exponent folding — the architecture R5's `Q4`
forced, and which `D13` showed was never needed.

Regimes used at this configuration: `C` for `k = -16..-6`, `D` for `k = -5..5`,
`B` for `k = 6..16`. Exhaustive over all 33 values of `k`.

## Reporting diagnostics (D13: reported, never gated)

`huge_tiny_products = 4`, `max_abs_log10 = 46.8`, `min_tail_factor = 3.7e-2`.
Four `huge x tiny` products are formed and they are **harmless**: relative error
is preserved under multiplication, and both factors carry full relative
accuracy. That is the whole content of `D13`, now confirmed by a passing gate.

## Historical results preserved

R4 `GATE = FAIL` and R5 `R5_LOCAL_GATE = FAIL` are unchanged and not
reinterpreted. R6 is a successor with its own pre-result anchor; it inherits
`L-R5.1` .. `L-R5.9` unchanged, since the R6 evaluator is regimes B/C/D with the
exponent carried outside rather than folded in — algebraically the same `I_k`,
and `G1` confirms that at every `k`.

## Consequence

The `P3`/`Q3`/`G3` conditioning blocker, open since R4, is **closed**. The SR
lane now projects to `9.07` CPU-hours with zero `z`-panels and zero softplus
approximations. Phase 2 (the SR `m=1`, `e in [0.24,0.26]` full-cell prototype)
is authorized by the R5 brief section 20 condition, which R6 now satisfies.
