# P5Y K1 SR qualification -- status

```text
SR_IMPLEMENTATION = PARTIAL          (was: ABSENT)
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
| SR top-level obligations | **8,849** | `universe.work_ids()` |
| . object / dep / curv / assembly / far-field | 6004 / 316 / 1264 / 1264 / 1 | derived |
| total universe | **17,978** | `spec.TOTAL_UNITS` |
| precision | 256 bits | `spec.PRODUCTION_BITS` |
| cap | 1126 CPU-hours | `spec.HARD_CAP_CPU_H` |
| SR splice | `log(4581762885148045/8796093022208)+1/2` | `spec.SPLICE_EXACT["SR"]` |

`sr_status.py`'s prose says "8,850"; its own `coverage()` computes
`28*316+1 = 8849`, which matches `universe.work_ids()`. **8,849 is the machine
count**; the prose is off by one.

## What was built

Complete raw-variable SR object DAG (99 nodes, 351 edges), audited acyclic,
derivative-ordered, and covering exactly the 28 frozen per-cell obligation
classes. Closed-form sources with validated first and second e-derivatives.
Exact operator-norm layer. Full F/D/H resolvent propagation in the frozen error
algebra, exact all-m assembly, and `M_R2`. Execution-derived certifying
provenance with a fail-closed final gate. 54 structural tests, 0.51 s total.

## Three findings that change the SR plan

**1. `M_R2` is not what the task brief assumed.** The K1 obligation is
`M_R2 = mag(R2_interval) >= sup_{e in cell} |R''_{D,m}(e)|` (`assembly.py`,
consumed by `ledger.cover_charge`). It is NOT `sup_e E_e[Rbar^2]` -- that is the
P5X theorem-consumer scalar `M_2`, which is not a K1 cover obligation.
Implementing `M_2` would leave every K1 cover obligation undischarged while
appearing to succeed. Recorded as `GOVERNANCE_PROHIBITED`.

**2. The SR one-step operator is not contractive, by eleven orders of magnitude.**

```text
k0 = ||K_e|| = Phi(c_SR) - Phi(-c_SR) = 1 - 1.42e-11      (e = 0)
naive Neumann bound 1/(1-k0)          = 7.03e10           -- useless
```

`K_e` is substochastic with mass essentially 1 at the reset state; the
contraction is an n-STEP effect (`||K^n|| = sup_y P_y(tau > n)`, decaying at the
alarm rate), not a one-step one. `sr_operators.resolvent_bound` therefore takes
certified power norms and **rejects `k0^n` as a stand-in**. Obtaining a certified
`||K^n|| < 1` requires iterating the operator -- the first real SR numerical
task, and the top blocker.

**3. The unrefined chain is far too loose, exactly as CUSUM found.** `M_R2`
scales like `C^3` through the H_r equation, so with a placeholder `C = 600` the
whole-cell `B_cover` utilisation is ~10^4x budget. This mirrors the documented
CUSUM experience (`refine.py`: "unrefined chain gives `M_R2 = 6.2e4` and
`B_cover = 143%` -- a FAIL"), which the frozen refinement wiring repairs. Per
governance this is certificate looseness, **not** a scientific failure.

## Exact remaining SR blockers

1. **Certified n-step resolvent bound** `||K^n|| < 1` for the SR kernel. Blocks
   every F/D/H bound. Requires operator iteration -- heavy numerics.
2. **Refinement wiring** into the whole-cell chain, without which `M_R2` will not
   fit `B_cover` (frozen `refine.py`, already validated on CUSUM).
3. **Patch-resolved candidate layer**: the sup-norm envelope is implemented; the
   Task1R bivariate Taylor-model panel certification must be generalised from
   `F_0` at one patch/drift to all objects, 3,994 live patches and 316 cells.
4. **Measured cost**: no SR cell has been certified, so no statement is made in
   either direction about the 1126 CPU-hour cap.

## Deliberately NOT claimed

SR CLOSED, K1 CLOSED, COST_CAP PASS, production ready, P5Y closed. None of these
are supported by anything in this namespace.
