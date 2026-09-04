# P5Y K1 — TASK 1R SUCCESSOR CHECKPOINT (binding, frozen at T1R)

Successor to the failed Production Task 1. **Repairs only the certification
harness.** No scientific rule, scope, threshold, ledger line, precision, degree
ceiling, representation family or verdict semantic changes.

```text
predecessor   P5Y_K1_TASK1 = FAIL   governing class IMPLEMENTATION_DEFECT
              delta_0 = 1.106607e-03, of which 98.23% was the harness truncation
              IMMUTABLE. Not edited, deleted, reinterpreted or overwritten.
parent        P5Y_K1_CHECKPOINT_STATUS = FROZEN, anchor 310c3aa,
              hash ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d
```

## 1. Unchanged scientific object
`SR` / `F_0` / `e = 1/4` / patch `(17,11)` / grid 64 / bidegree (16,16) /
exact-dyadic 2^-50 / Chebyshev basis / 256 bits / `P1_RULE_WORKPREC = 512` /
`B_candidate = 0.040` / `LOCAL_GATE_BUDGET = 0.100` / ceiling 60,000. All read
from the parent checkpoint and asserted field by field.

## 2. The defect being repaired
Task 1 composed to full degree first (`16 x 9 = 144` per side, total `n` to 288)
in the mixed variable `u = alpha + zeta`, then truncated the patch-local
variables once, at `DEG_X = 6`. Re-expanding `u^n` spreads alpha-mass binomially
with `p = H/rho = 0.2041`, so expected patch-local degree is `0.204 n`, exceeding
6 once `n > 29`. Most of the retained series was surrendered to the discard bound.

## 3. The repair — three parts, all frozen here
```text
R1  truncate the patch-local variable at EVERY product (bivariate Taylor models
    in (alpha,zeta) and (beta,zeta)), never once after composition. The source
    softplus expansion is EXACT in alpha for D >= SOFTPLUS_DEGREE+1, so nothing
    is discarded at the source and nothing can be dumped later.
R2  |N_k| <= 2 phi_max h^(k+1)/(k+1)  replaces  |N_k| <= h^k N_0,
    sharper by a factor (k+1); moments are additionally clamped by it.
R3  a joint (D,Z) consistency relation that REJECTS late-truncation
    architectures quantitatively, before any result-bearing work.
```

## 4. Budget partition of `B_candidate` — no new budget
Twentieths of the existing `B_candidate = 0.040`; the sum is exactly
`B_candidate`. Shape mirrors the parent ledger.

| line | 20ths | absolute | covers |
|---|---|---|---|
| `B_eq` | 9 | 0.018 | the equation defect itself (the object under test) |
| `B_trunc` | 3 | 0.006 | patch-local `(alpha,beta)` truncation |
| `B_tail` | 3 | 0.006 | `zeta` truncation + Gaussian moment tail |
| `B_end` | 2 | 0.004 | endpoint slivers (structural, not tunable) |
| `B_int` | 1 | 0.002 | Arb interval radius |
| `B_round` | 1 | 0.002 | exact-dyadic rounding |
| `B_reserve` | 1 | 0.002 | **non-redistributable** |

Justification: the quantity under test takes the plurality (45%) so the harness
can never account for more than the object; the two tunable harness parameters
are treated symmetrically at 15% each, which is exactly what the predecessor
lacked; endpoints get 10%; the two precision-limited lines take the parent
ledger's own smallest share (5%); the reserve mirrors the parent's reserve.

## 5. Parameter-selection algorithm — deterministic, result-independent
```text
a-priori scale   ||F_0||_inf <= C_SR(e) * ||S_0||_inf <= C_SR(e) * 2 phi(0)
                             = 149.8006          (resolvent theorem only)
coefficient cap  Cmax = 4 * that = 599.2024      (2-D Chebyshev coefficient bound)
allowances       delta_trunc_max = B_trunc / C_SR ,  delta_tail_max = B_tail / C_SR
stage 1          minimal Z in the frozen ascending grid Z_GRID meeting B_tail
stage 2          minimal D in the frozen ascending grid D_GRID meeting B_trunc
                 AND the joint-consistency relation
probe            unit-coefficient majorant on the worst panel (largest Gaussian
                 mass), scaled by the panel count
```
No candidate and no predecessor residual is read. The rule need not itself be
conservative: the certificate recomputes every component exactly and FAILS if
any exceeds its frozen line.

## 6. Selected parameters (frozen before T2R)
```text
Z = 20    D = 11    n_panels = 28
stage 1   Z=12 -> 1.366e+00 | Z=16 -> 3.258e-03 | Z=20 -> 1.050e-05  <= 3.196e-05
stage 2   D= 9 -> 1.293e-03 | D=10 -> 6.906e-05 | D=11 -> 3.607e-06  <= 3.196e-05
joint     required_D = 9, selected 11, D_max from complexity 52
scores    local (D+1)^2(Z+1) = 3,024 ; candidate (17)^2(Z+1) = 6,069 ; ceiling 60,000
```

## 7. STOP rules
`CHECKPOINT_INTEGRITY_FAILURE`, `HARNESS_TAIL_BOUND_FAILURE`,
`HARNESS_ORDER_REQUIREMENT_EXCEEDS_COMPLEXITY`, `REPRESENTATION_COMPLEXITY_FAILURE`,
`P1_HEADROOM_FAILURE`, `PRECISION_FAILURE`, `CANDIDATE_RESIDUAL_TOO_LARGE`,
`INTERVAL_WIDTH_TOO_LARGE`, `IMPLEMENTATION_DEFECT`. Any fires ⇒ stop, no retry.

If the repaired harness passes all internal design checks and the genuine `F_0`
still exceeds `B_candidate`, the class is **`CANDIDATE_RESIDUAL_TOO_LARGE`** —
materially stronger evidence against the candidate architecture. It may not be
called `IMPLEMENTATION_DEFECT` without a newly demonstrated defect.

## 8. Execution policy
Exactly one genuine execution. No refit loop, parameter retry, degree retry,
precision retry or budget redistribution. Candidate construction is the
predecessor's, imported verbatim from `task1/task1_f0.py`.

```text
CPU cap for this task   0.10 CPU-hours   (the parent campaign cap is 1,848 and
                                          is not touched by a single-cell task)
T0R design | T1R freeze | T2R one result | T3R completion | T4R adjudication
```
