# P5Y post-K1: K2–K5 audit and CUSUM readiness (NO-COMPUTE, NON-RESULT-BEARING)

```
K2                                  = INCOMPLETE
K3                                  = INCOMPLETE     (finite half exactly discharged; frozen "useful" half open, no frozen criterion)
K4_NEW_COMPUTE_REQUIRED             = NO             (assembly-only over K1 production records; widths are result-dependent)
K5_NEW_COMPUTE_REQUIRED             = YES            (near-zero third-order certificate missing from every K1 record)
K4_K5_ASSEMBLY_READY                = NO             (K4 tooling built and synthetic-tested, locked; K5 not assembly-only)
CUSUM_HOST_BINDING_READY            = NO
CUSUM_COST_CAP_READY                = NO
NEW_RESULT_BEARING_COMPUTE          = NONE
LIVE_AWS_RUN_TOUCHED                = NO
VERDICTS_ISSUED                     = NONE           (K1, K2, K3, K4, K5 all remain OPEN / NOT CLOSED)
```

| document | content |
|---|---|
| `K2_K3_AUDIT.md` | Frozen obligations, the full evidence map (exact theorems, certified evidence, Lean, frozen fallbacks), missing items, and the scientific vs governance split. The binding TA reading governs: P5X-T6 consumes both quantities. |
| `K4_K5_ADMISSIBILITY.md` | Exact K4/K5 definitions, record schema semantics, domain, precision, disposition/predeclaration/producer status, and the adverse finding that the frozen near-zero K5 route ("second-order remainder") cannot fix the sign of `s'`, because `R''(0) = 0` by oddness. |
| `config/K4_ASSEMBLY_PREDECLARATION.json` | Proposed pre-result K4 decision procedure, declared blind to all genuine production values, **unfrozen**. |
| `code/k4_assembly.py`, `tests/test_k4_assembly.py` | Exact-rational K4 assembly. Genuine mode is locked until `config/K4_ASSEMBLY_CHECKPOINT_HASH` exists. **13 passed** on Vultr (synthetic fixtures plus frozen geometry only). |
| `CUSUM_READINESS.md` | Host binding: Vultr 7 mismatches (Haswell, no AVX-512); AWS 2 mismatches (CPython build stamp), kernel and libraries match. Cost cap: none established for CUSUM. |

## Adverse findings

1. `FORWARD_AUDIT.md`'s "K2/K3 not hypotheses" was already overturned by the binding TA. The post-K1 DAG rows are corrected accordingly.
2. The TA and `FROZEN_THEOREM.md` §8 near-zero K5 route is insufficient as written: a second-order remainder gives continuity and the limit, not the sign. TA's 105.4 CPU-h K5 estimate does not cover the missing third-order object.
3. The frozen K5 targets are inconsistent: P5 H3a (strict decrease) versus P5X-T7(2) (level attainment). Read literally, P5X-T7(2) is false for levels above `sup s`. These are governance rulings, not repaired here.
4. No quantitative "useful M₂" criterion is frozen anywhere.
5. The Aux4 CUSUM identity is not reproducible on either current host as frozen. On AWS the CPython build stamp changed after the Aux4 commit.
