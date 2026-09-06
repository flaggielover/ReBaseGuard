# P5Y K1 SR qualification -- status

```text
SR_IMPLEMENTATION = PARTIAL
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

## Blocker 2 — refinement: designed, and shown to be mandatory

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

## Blocker 3 — full-scope structure: prepared

`sr_universe.py` derives the exact 8,849-obligation SR universe from the frozen
`universe.work_ids()`, verifies uniqueness, per-cell shape and the single
far-field unit, and shards it by the frozen floor rule with exact partition at
every worker count tested (1, 2, 4, 7, 64, 317, 8849). Resume identity binds work
ID + scientific hash + TCB + frozen checkpoint hash, and admission rejects the
superseded 12,255-object universe, superseded checkpoint hashes and stale
producers.

## Order-3 assessment

`(I-K) F_r''' = 3K'F_r'' + 3K''F_r' + K'''F_r + S_r''' + 3h_1'' + e h_1'''`, with
`K''' f = -int (w^3-3w) f phi dz` — still inside the frozen panel machinery, so no
new object or operator class. Assessment: **LIKELY NEEDED but `NOT_ESTABLISHED`
for SR** — order-2 midpoint refinement leaves a residual `rho·sup|F'''| ~ 0.3133 C^3`,
the same order it was meant to remove, unless the midpoint third derivative is
much smaller than its tower (as Aux3 measured for CUSUM). That is an empirical
question requiring the deferred midpoint solves; it is not inherited from CUSUM.

## Exact remaining SR blockers

1. **Midpoint refinement solves** for `F/D/H` at `e0` — the deferred heavy
   numerics, and the only way to remove the norm-tower artefact.
2. **Order-3 auxiliary evidence**, if the midpoint third derivative does not turn
   out to be small; architecture derived, not built.
3. **Patch-resolved candidate layer**: the sup-norm envelope is implemented; the
   Task1R bivariate Taylor-model panel certification must be generalised from
   `F_0` at one patch/drift to all objects, 3,994 live patches and 316 cells.
4. **Production-resolution corroboration** of `C_upper`: the interval-DP
   certifier converges (ratio to frozen 1.98 -> 1.57 as P goes 16 -> 32) but has
   not yet been run fine enough to return `CORROBORATED`.
5. **Measured cost**: no SR cell has been certified, so no statement is made in
   either direction about the 1126 CPU-hour cap.

## Deliberately NOT claimed

SR CLOSED, K1 CLOSED, COST_CAP PASS, production ready, P5Y closed. None of these
are supported by anything in this namespace.
