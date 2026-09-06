# P5Y K1 SR qualification -- status

```text
SR_IMPLEMENTATION = PARTIAL
SR_REFINEMENT     = ARCHITECTURE_PARTIAL   (derived, implemented, contraction proved)
SR_ORDER3         = NOT_ESTABLISHED        (downgraded from LIKELY_NEEDED)
SR_NSTEP          = ARCHITECTURE_PARTIAL   (derived, implemented, corroborating)
SR_M_R2           = IMPLEMENTED_NOT_YET_QUANTITATIVELY_CLOSING
SR_ALL_M          = IMPLEMENTED  (m = 1,2,3,5, exact frozen coefficients)
SR_FAR_FIELD      = PASS         (inherited, not recomputed)
COST_CAP          = NOT_ESTABLISHED
PRODUCTION        = OFF
heavy numerics    = DEFERRED by the Phase-10 CPU gate (CUSUM owns the cores)
```

## Frozen scope, confirmed from authoritative files

| quantity | value | source |
|---|---|---|
| SR compact cells | **316** (indices 0..315) | `spec.COUNTS["SR"]` |
| m | **{1,2,3,5}** | `spec.M_VALUES` |
| SR top-level obligations | **8,849** | `sr_universe.audit()` |
| . object / dep / curv / assembly / far-field | 6004 / 316 / 1264 / 1264 / 1 | derived |
| total universe | **17,978** | `spec.TOTAL_UNITS` |
| precision | 256 bits | `spec.PRODUCTION_BITS` |
| cap | 1126 CPU-hours | `spec.HARD_CAP_CPU_H` |
| SR splice | `log(4581762885148045/8796093022208)+1/2` | `spec.SPLICE_EXACT["SR"]` |

## Blocker 1 — n-step resolvent: RESOLVED, and reframed

`SR_NSTEP_RESOLVENT.md` derives, with proofs:

* **Lemma 1 (positivity)** `||T||_inf = ||T 1||_inf` for positive `T`, turning an
  operator norm into one function evaluation;
* **Lemma 2 (survival)** `(K_e^n 1)(y) = P_y(tau > n)`, so `||K^n||` is exactly the
  worst-case n-step survival mass;
* **Theorem** `(I-K)^{-1} = P_n (I-K^n)^{-1}`, hence
  `C_n = ||E_.[tau ^ n]||_inf / (1 - q_n)`, decreasing to the exact
  `sup_y E_y[tau]`.

Exploratory survival DP (float, 4.24 CPU-s, **not** a certificate) gives
`C -> 471 / 127 / 35.7 / 11.0 / 4.62` at `e = 0 / 0.25 / 0.5 / 1 / 2`, versus the
useless one-step `7.03e10`.

**Governance correction found mid-task.** `config/cells.json` already carries a
per-cell `C_upper`, and the validated CUSUM code reads it directly
(`cusum_layer2.py:130`). **`C` is frozen cover geometry, not a producer output.**
SR now consumes it the same way. The n-step machinery is therefore independent
*corroboration*, and it corroborates: frozen `C_upper` dominates the survival
estimate at every drift with a 1.4x-2.6x margin. See `SR_RESOLVENT_GOVERNANCE.md`.

## Blocker 2 — refinement: DERIVED, IMPLEMENTED, contraction PROVED

`SR_MIDPOINT_REFINEMENT.md`. Three results.

**The cover is frozen at order 2 in `e`.** `assembly.py` fixes `R_interval` and
`D_interval` at `e0` and `R2_interval` uniformly on the cell; `ledger.py` consumes
them through a second-order Taylor cover, so raising the Taylor order is not
available. This exposes a conservatism in the previous checkpoint: `sr_propagate`
evaluates all three as whole-cell envelopes where the frozen semantics ask for
midpoints on the first two.

**Refinement acts on the ERROR, not the value** (as `refine.py` does), consuming
midpoint errors and CANDIDATE sups. The patch-resolved candidate layer is
therefore a PREREQUISITE for refinement, not a parallel task. This reorders the
remaining blockers.

**The iteration provably contracts on every compact SR cell:**

```text
    kappa  = rho * C_upper * 2 k1           max 0.500000  over all 315 cells
    kappa' = C rho (2 k1 + k2 rho / 2)      max 0.513371  over all 315 cells
    fixed-point amplification 1/(1-kappa')  <= 2.0550
```

`kappa` is capped at exactly 1/2 by construction: the frozen step rule
`s = 1/(4 a_upper C_upper)` with `a_upper = k1 = sqrt(2/pi)` gives
`kappa = 2k1/(4 a_upper) = 1/2`, the same identity behind `rho*C_upper = 0.3133`.
The `C^3` tower is removed by the iteration itself, with no order-3 evidence.

## Blocker 2b — the measured gap refinement must close

Second correction: an earlier probe used an artificial `rho = 1e-3` and concluded
that large-drift cells fit inside `B_cover`. The frozen geometry holds
`rho * C_upper = 0.3133` **invariant**, so large-drift cells have proportionally
larger `rho`. Re-measured with each cell's own frozen `rho`, m = 2:

| cell | e0 | C_upper | rho | rho·\|D\| | rho²·M_R2/2 | utilisation |
|---|---|---|---|---|---|---|
| 0 | 2.60e-4 | 1205.94 | 2.60e-4 | 1.91e2 | 4.78e1 | **4.78e3** |
| 200 | 0.2284 | 216.17 | 1.45e-3 | 5.99e1 | 1.50e1 | **1.50e3** |
| 275 | 1.005 | 17.92 | 1.75e-2 | 1.57e1 | 4.10e0 | **3.97e2** |
| 313 | 6.240 | 2.00 | 1.57e-1 | 1.75e6 | 1.34e6 | **6.18e7** |

No sampled cell fits; the best is 397x over budget, and the dominant term is the
**linear** `rho|D|`, ~4x the curvature term. Measured tower exponent
`d log M_R2 / d log C = 2.97`.

Phase-7 diagnosis: **`NSTEP_HELPS_BUT_REFINEMENT_REQUIRED`**.

Exact additive attribution of `W_cover` at cell 150 (sums to 100.000000%):

| origin | C-power | share |
|---|---|---|
| `S_r` source uncertainty | C^2 | 67.65% |
| `S_r` source uncertainty | C^3 | 16.90% |
| `e*h_1` raw-variable drift | C^2 | 11.51% |
| `e*h_1` raw-variable drift | C^3 | 2.88% |
| everything else | C^0..C^2 | 1.06% |

Amplification spectrum: **C^2 = 79.4%**, C^3 = 19.8%, C^1 = 0.85%. The dominant
depth is `C^2`, i.e. `D`, not the curvature.

Correction to the previous checkpoint: the claim that `rho|D|` dominates
curvature by ~4x holds only for small-`rho` cells (3.99 / 3.95 / 4.00 at cells
150 / 250 / 0) and REVERSES at large `rho` (1.30 at cell 313). Cell 315 is the
unique terminal/far-field cell whose `rho` is a compactified coordinate, so the
Taylor cover arithmetic does not apply to it; it is excluded from the
compact-cell analysis and SR far-field is already PASS.

### The falsifiable target refinement must hit

With `D_int ~ a_m sup|Dhat|` and `M_R2 ~ 2 a_m sup|Hhat|`, `B_cover` closes iff

```text
    rho * sup|Dhat| + rho^2 * sup|Hhat|  <=  B_cover / a_m
```

| cell | rho | max sup&#124;Dhat&#124; | max sup&#124;Hhat&#124; | proxy for &#124;R'&#124; | gap |
|---|---|---|---|---|---|
| 50 | 3.35e-4 | 99.4 | 2.97e5 | 5322 | 53.5x |
| 150 | 7.26e-4 | 45.9 | 6.32e4 | 2139 | 46.6x |
| 250 | 5.44e-3 | 6.13 | 1127 | 136.6 | 22.3x |
| 300 | 7.92e-2 | 0.421 | 5.31 | 1.343 | 3.19x |

The projected gap is now **3x-54x**, not 400x-6.2e7x. The proxy uses derivatives
of the frozen `C_upper(e)` profile and cannot see the renewal cancellation that
the cancellation-preserving backend exists to exploit, so it is an upper
indicator, not evidence. Measuring `sup|Dhat|` at cell 150 against **45.9** is
the single decisive pilot measurement.

## SR work universe — exact and shard-conserving

`sr_universe.py` derives the exact 8,849-obligation SR universe from the frozen
`universe.work_ids()`, verifies uniqueness, per-cell shape and the single
far-field unit, and shards it by the frozen floor rule with exact partition at
every worker count tested (1, 2, 4, 7, 64, 317, 8849). Resume identity binds work
ID + scientific hash + TCB + frozen checkpoint hash, and admission rejects the
superseded 12,255-object universe, superseded checkpoint hashes and stale
producers.

## Order-3 assessment — DOWNGRADED to NOT_ESTABLISHED

`(I-K) F_r''' = 3K'F_r'' + 3K''F_r' + K'''F_r + S_r''' + 3h_1'' + e h_1'''`, with
`K''' f = -int (w^3-3w) f phi dz` — still inside the frozen panel machinery, so no
new object or operator class. Verdict: **`NOT_ESTABLISHED`**, downgraded from the previous `LIKELY_NEEDED`.

The earlier reading rested on order-2 refinement leaving a residual of the same
order it was meant to remove. That reasoning is superseded: the monotone
iteration contracts at <= 0.5134 and removes the `C^3` tower without any order-3
evidence. It is equally not `ORDER2_LIKELY_SUFFICIENT`, because the refined fixed
point is driven by midpoint errors and candidate sups that do not yet exist. The
adjudication is blocked on the candidate layer, not on more derivation.

## Blocker 3 — patch-resolved architecture: identity and contracts built

`sr_patch.py` reproduces the frozen Gate-2B live-patch census exactly — **4096
nominal, 3994 live, 57 dead_low, 45 dead_high, 83452 panels, reset patch (0,0)** —
by importing the frozen classifier rather than re-deriving it. Deterministic patch
identity, the cell x patch x object work mapping, the candidate determinism
contract (producer + runtime + patch/cell/config -> identity) and the Gate-2C
degree ceiling are implemented and tested. Candidate SOLVES raise
`CandidateSolveDeferred` rather than returning a stub that could be certified.

Patch evidence is NESTED: 23,979,976 order-0 patch items sit beneath the **8,849**
SR obligations and create no work ID.

## Exact remaining SR blockers, in dependency order

1. **Patch-resolved candidate solves** — now the FIRST blocker, not the third:
   refinement consumes `sup|Dhat|`, `sup|Hhat|` and midpoint errors, none of which
   exist without candidates.
2. **Midpoint propagation at `e0`** (`epsF_mid`, `epsD_mid`), the second
   propagation the refinement requires.
3. **Order-3 auxiliary evidence** — `NOT_ESTABLISHED`; decidable only once 1 and 2
   supply real numbers.
4. **Production-resolution corroboration** of `C_upper` — needs `n` raised as well
   as `P`; plan and cost in `SR_RESOLVENT_GOVERNANCE.md` section 6.
5. **Measured cost**: no SR cell has been certified, so no statement is made in
   either direction about the 1126 CPU-hour cap.

## Deliberately NOT claimed

SR CLOSED, K1 CLOSED, COST_CAP PASS, production ready, P5Y closed. None of these
are supported by anything in this namespace.
