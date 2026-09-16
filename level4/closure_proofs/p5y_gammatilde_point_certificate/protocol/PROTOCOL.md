# GammaTilde point certificate — frozen protocol (pre-result)

This successor has one scientific purpose: certify the sign of `R_m'(0)` for CUSUM `m = 3, 5`. Its evaluator is
qualified before any target value is computed. By P1-T1, `R_m'(0) = 1 − GammaTilde_m`, so a negative sign is the
premise `GammaTilde_m > 1`. It is separate from the K5 order-3 work. It has no signed-R''' object, no cells
148/305/309, no order-3 campaign, and it makes no writes to K1 or the CUSUM composite.

The machine-readable, binding text is `POINT_PROTOCOL.json`. Its sha256 is `POINT_PROTOCOL_HASH`. This file only
summarizes it.

## Definition audit (Phase 1)

The frozen K1 CUSUM kernel produces `D_interval` on the midpoint path only
(`aux_propagate.cell_obligations`: `cell_dag(cert, "delta_mid")` → `propagate.enclosures` →
`assembly.assemble(m, D, W[1])`). Every midpoint residual is certified at the exact cell midpoint `e0`
(`cusum_layer2.CellCertifier.certify`: `delta_mid`). Whole-cell objects (`delta_cell`, refine2, the aux order-3
evidence, M_R2) never enter `R_interval` or `D_interval`. The certifier chain is Aux3 → Order2 → Sharp →
Repaired → CellCertifier. Its overrides change only the operator-norm table (which can only tighten), the single
S0 charge (Repair1, applied at the midpoint) and `delta_cell`.

A point certificate is therefore direct. The degenerate cell `{0}` (`left = right = e0 = 0`, `rho = 0`) makes
every midpoint residual certified at `e = 0` exactly. The drift-aware norms are taken over that single point, and
`C` is frozen cell 0's resolvent bound. Cell 0 is `[0, 2e0]` and its `C_evaluation` is exactly `0`. No narrow
fallback cell is needed.

The frozen code fixes every convention:

| Item | Where it is fixed |
|---|---|
| k = 1/2, h = 5, state bound 11/2 | `cusum_layer1.K_FROZEN`, `H_FROZEN` |
| Reset and convention A | frozen raw-variable DAG |
| Terminal increment included, random denominator | frozen raw-variable DAG |
| Exact coefficients `c_(m,t) = 1/t − 1/m` | `assembly.coefficients` |
| m restricted to the frozen scope `(1,2,3,5)` | `assembly.coefficients` refuses other m |
| No leading `+e` | `assembly.assemble` refuses one |
| Sign convention | `R'(0) = 1 − GammaTilde` (PB3 BOUND, reuse audit `323e2b8f`) |

## Gates, ladder, controls

- **Gates** (`point_core.adjudicate`):
  - `hi < 0` → CERTIFIED.
  - `lo ≥ 0` → REFUTED.
  - Anything else → INCONCLUSIVE.
  - Premise: all targets CERTIFIED → SATISFIED; any target REFUTED → REFUTED; otherwise OPEN.
- **Precision ladder:** 256 → 384 → 512 bits. Escalate only while a target is INCONCLUSIVE. The first decisive
  rung decides.
- **Controls** (they can only void a run):
  - m = 2 must intersect its reuse-certified interval.
  - m = 1 must intersect CORE-C1 and the reuse interval.
  - Every `R_m(0)` enclosure must contain 0.
- **CPU ceilings:** qualification 2 CPU-h, science 3 CPU-h.

## Qualification (before science)

1. Q1: the unit tests pass.
2. Q2: `replay-cell0` reproduces the committed K1 cell-0 `R_interval` and `D_interval` exactly, for every m.
3. Q3: the degenerate cell `{e0}` gives enclosures contained in the record's, for every m.
4. Q4: both runs are bound to this protocol, identity equals the frozen K1 identity, and the SciPy guard is clean.
5. Q5: qualification CPU is within its ceiling.

A pre-freeze dry gate check ran on `rebaseguard-vultr-02`. It covered imports, manifest-v3 verify, identity,
runtime contract and module coverage, with no kernel arithmetic, and passed.
