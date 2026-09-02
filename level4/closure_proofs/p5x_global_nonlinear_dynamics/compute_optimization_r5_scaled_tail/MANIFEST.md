# P5X R5 — source manifest and protocol digest

Generated at Checkpoint G, before any R5 implementation exists.

## R5 frozen documents (sha256 of working-tree bytes at freeze time)
```text
ca3119bf64c1d8479a3a58d5e20a94fd7ce5381c4bb0a32626a2ef38b197c947  SCALED_TAIL_DERIVATION.md
dd99f06ab43969d6f17beb9aec74bd1524a3357afca71bd4dab17c436d9dd0c6  R5_FROZEN_SPEC.md
```

## Protected tree — verified by git object, not worktree state
```text
original P5 tree (immutable, PARTIAL)          ec1d3b1da066a4ddda34f24bd5e062c6b8a93484
  same tree at bb03c0e (baseline)              ec1d3b1da066a4ddda34f24bd5e062c6b8a93484
certified_method_repair_ra                                         bef5da6a0f723e824c6d6271caa11a77ac42f97e
compute_optimization_r1                        b96fe1d3c810c97eb002bb9499f8c8f66def5b3a
compute_optimization_r2                        0d3ce0b7fac213f67a0e74495d2089ed113dfa11
compute_optimization_r3_sr_symbolic            1662dc0448767926c5109d76db9028b499935bfe
compute_optimization_r4_xi_reformulation       ba94ad9ab854a4ef84df4c1a449f3eba0720d204
FROZEN_THEOREM.md blob                         85c8762f67b76122c74273bb1572a7cfeb4f4b6f
rebaseguard-lean tree                          3fa5d722bc5e1d6c244f2448953eaeb0b258bec3
rebaseguard-proof tree                         727edc8013f3f89afb4dd45085994318e57234be
results/r4_gate.json blob                      bbe51c83f9d8a47048d4c4fddd642edf8e917766
results/r3_gate.json blob                      28112181cdca846cd977fc8044f3ebaee21856fc
```

## Checkpoint chain (no squash)
```text
daaabf9e028098b88bc1e7a8f5ebddb1e6c21825  R4 result: the xi reformulation ELIMINATES the z-panel bottleneck (1255x), but the gate FAILS on conditioning
209a6fd9a5ca2824688062ac855a7abcefae9697  Checkpoint F - P5X R4 xi-reformulation pre-result anchor
```

## Protocol digest
```text
amplification metric : rad(sum_k G_k I_k) * 2^bits   (identical to R4 P3)
R4 reference         : 2.1356e17
frozen threshold     : 1e12          NOT weakened
gate semantics       : conjunctive Q1..Q10
rigorous references  : R4 direct evaluator only
diagnostic-only refs  : Simpson quadrature, y-space brute force
retry ladder         : NONE
```
