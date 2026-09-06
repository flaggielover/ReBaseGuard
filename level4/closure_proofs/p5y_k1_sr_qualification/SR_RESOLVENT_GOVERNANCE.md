# Global vs local SR resolvent constants — decided from frozen artifacts

Phase 5. The answer was read out of the frozen cover geometry, not chosen for
convenience, and it corrects the working assumption of the previous checkpoint.

## 1. The frozen artifacts already answer this

`config/cells.json` carries, **per cell**:

```text
    C_upper         exact rational upper bound on the resolvent constant
    C_evaluation    the exact rational left endpoint it was evaluated at
    rho             the cell half-width
    e0, left, right the drift interval
```

and the validated CUSUM implementation consumes it directly:

```python
# p5y_k1_cover_ledger_implementation/code/cusum_layer2.py:130
self.C = F(cell["C_upper"])
```

`C_upper` is also part of the frozen **cell identity** hashed into every record
(`identity4.py:40,147`; `aggregate_ledger.py:81`), alongside `e0, rho, left, right`.

> **Decision: the SR resolvent constant is PER CELL, and it is FROZEN INPUT.**
> `C_upper` is cover geometry. The producer reads it; it does not recompute it,
> and it must not alter it. SR consumes it exactly as CUSUM does, via
> `sr_nstep.ResolventCertificate.from_frozen_cell`.

This also means no budget line is owed for it: `ERROR_ALGEBRA.md` records
`| B_resolvent | 0 | none; C is only multiplicative | additive resolvent charge |`.

## 2. Measured range across the 316 SR cells

```text
    C_upper  min = 2.0000   (cell 313, e0 = 6.240)
             max = 1205.94  (cell 0,   e0 = 2.598e-4)
```

A single global constant would have to be 1205.94 everywhere, discarding a factor
of ~600 at large drift. The frozen geometry does not make that mistake.

## 3. The geometry balances rho against C_upper

The frozen step rule is `s = 1/(4 * a_upper * C_upper)`
(`build_spec.py:97`), and the consequence is directly measurable:

| cell | e0 | C_upper | rho | **rho x C_upper** |
|---|---|---|---|---|
| 0 | 2.598e-4 | 1205.94 | 2.598e-4 | **0.3133** |
| 200 | 0.2284 | 216.17 | 1.449e-3 | **0.3133** |
| 275 | 1.005 | 17.923 | 1.748e-2 | **0.3133** |
| 313 | 6.240 | 2.0005 | 1.566e-1 | **0.3133** |

`rho * C_upper` is invariant by construction. This is why a whole-cell width that
scales like `rho * C^2` is *linear in C* rather than quadratic, and why no cell
is "easy": the geometry has already equalised the difficulty.

**Correction to the previous checkpoint.** An earlier probe used an artificial
`rho = 1e-3` for every cell and concluded that large-drift cells fit inside
`B_cover`. With the real per-cell `rho` they do not: at cell 313 the true `rho` is
157x larger and the utilisation is `6.18e7`, not `0.80`. The frozen `rho` must
always be used.

## 4. What the n-step machinery is for

Since `C_upper` is frozen input, `sr_nstep.certify` is **not** the primary source
of `C`. Its role is independent corroboration — nested auxiliary evidence that
the frozen constant really does dominate the SR resolvent:

```text
   exploratory sup_y E_y[tau]   vs   frozen C_upper
     e ~ 0.00    471   (n=256, not converged)      1205.94   frozen dominates
     e ~ 0.25    127.1                              189.49   frozen dominates
     e ~ 0.50     35.67                              59.86   frozen dominates
     e ~ 1.00     11.00                              17.92   frozen dominates
     e ~ 2.00      4.616                              6.59   frozen dominates
```

The frozen constants sit above the independent survival-theory estimates at every
drift with a consistent 1.4x-2.6x margin. That is mutual corroboration of two
independently derived objects.

`corroborate()` is deliberately one-sided: both quantities are UPPER bounds, so a
loose enclosure exceeding `C_upper` is INCONCLUSIVE, never evidence against it.
Falsifying `C_upper` would require a certified LOWER bound on the resolvent norm,
which this lane does not claim to produce.

## 5. Governance conclusions

* per-cell constants: **already frozen**, no change proposed;
* per-patch constants: **not** part of the frozen geometry — not introduced;
* `ResolventCertificate` is nested supporting evidence consumed inside the
  existing `F` / `dF` / curvature obligations. It creates **no new work ID**; the
  SR universe stays at 8,849 and the global universe at 17,978;
* a certificate binds its own exact-rational drift interval, so a constant
  certified for one cell can never be silently reused on another
  (`CellMismatch`);
* nothing here alters the theorem, the estimand, the detector scope, `m`, the
  precision, the budgets, the reserve, the cover geometry or the splice points.

---

## 6. Production-resolution corroboration plan (Phase 10)

Corroboration currently returns `INCONCLUSIVE`: the interval-DP enclosure is
looser than the frozen constant. Measured convergence at cell 292 (`e in [2, 41/20]`):

| partition P | z-panels | n | independent `C_n` | ratio to frozen `C_upper = 6.592` | CPU |
|---|---|---|---|---|---|
| 10 | 10 | 6 | 32.71 | 4.96 | 0.29 s |
| 16 | 16 | 6 | 13.02 | 1.98 | 1.20 s |
| 24 | 24 | 6 | 10.50 | 1.59 | 4.09 s |
| 32 | 32 | 6 | 10.32 | 1.57 | 9.59 s |

**Refining `P` alone will not reach `CORROBORATED`.** Fitting `ratio = c + a/P`
to the last two rows gives an asymptote `c ~ 1.16 > 1`. The residual is not
spatial resolution: it is `n`. At `n = 6` the survival is still `q_6 ~ 0.44`, so
the `1/(1 - q_n)` factor alone inflates `C_n` by `~1.8x` above `sup_y E_y[tau]`.
Both `P` and `n` must increase together.

### Target configuration

```text
    n          32        (q_32 ~ 3.6e-3 at e = 2, from the exploratory ladder)
    partition  64
    z_panels   64
    bits       256
```

Cost scales as `P^2 * Nz * n`, so from the measured 9.59 s at `(32, 32, 6)`:

```text
    (64/32)^2 * (64/32) * (32/6) = 42.7      ->  ~410 CPU-s (~6.8 min) per cell
    selected-cell (8 pilots)                 ->  ~55 CPU-minutes
    all 315 compact cells                    ->  ~36 CPU-hours
```

Small-drift cells need larger `n` (the exploratory ladder shows `e -> 0` has not
converged even at `n = 256`), so their cost is proportionally higher; those cells
are exactly where `C_upper` is largest and corroboration matters most.

### Scope decision

> **Selected-cell corroboration, not global.** `C_upper` is frozen cover
> geometry that the certificate consumes; corroboration is nested auxiliary
> evidence that it is sound. Governance does not require it per cell, and
> spending ~36 CPU-hours of a 1126-hour cap to re-derive a frozen input would be
> a poor trade. The pilot suite corroborates the cells that bound the range —
> largest `C_upper`, smallest, central and the splice neighbour.

### Prepared command (NOT run — CUSUM owns the host)

```bash
python code/sr_pilot.py --pilot hardest --m all --bits 256 --corroborate 32
python code/sr_pilot.py --all --m all --bits 256 --corroborate 32
```

A run that still returns `INCONCLUSIVE` is not a failure of the frozen constant:
it means the enclosure is not yet tight enough, and `can_falsify_frozen` remains
`False` by construction (section 4).
