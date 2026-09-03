# P5X R8 — source manifest and protocol digest

## R8 frozen documents (sha256 at freeze time)
```text
02defc57885171f87c0603824268fa86b3a3cd3cb03a91bd74134cfd695c84af  R8_BINDING_SPEC.md
f90c118a160a7cbef890356293927fa1dd5030f35fc784d09135b8385309dfe3  r8_certify.py
```

## Protected tree by git object
```text
original P5 (immutable, PARTIAL)               ec1d3b1da066a4ddda34f24bd5e062c6b8a93484
  same at bb03c0e                              ec1d3b1da066a4ddda34f24bd5e062c6b8a93484
certified_method_repair_ra                     bef5da6a0f723e824c6d6271caa11a77ac42f97e
compute_optimization_r1                        b96fe1d3c810c97eb002bb9499f8c8f66def5b3a
compute_optimization_r2                        0d3ce0b7fac213f67a0e74495d2089ed113dfa11
compute_optimization_r3_sr_symbolic            1662dc0448767926c5109d76db9028b499935bfe
compute_optimization_r4_xi_reformulation       ba94ad9ab854a4ef84df4c1a449f3eba0720d204
compute_optimization_r5_scaled_tail            20a54eba43bb75c42f83cc11747456bc98c9c69b
compute_optimization_r6_minimal_evaluator      bc04ef2ba596dee1f1c8b2417f4ad5d844553014
compute_optimization_r7_sr_certification       007e67bfa24d9f071f1bebcfe7c4f76256b98e80
sr_full_cell_prototype                         5a21395412d0132da600636f07fb29e90ee26f19
b2_basis_feasibility_audit                     a7da5b1c87de11cbe24d4c364b7d6ff6ec0e22e4
rebaseguard-lean                               3fa5d722bc5e1d6c244f2448953eaeb0b258bec3
rebaseguard-proof                              727edc8013f3f89afb4dd45085994318e57234be
```

## Protocol digest
```text
B2 grid            : 1024 x 1024   (DEVIATION from brief section 8, disclosed)
B2 threshold       : <= 1e-2       UNCHANGED
B2 Bernstein degree: 16, elevated to 32 for derivative hulls only
B1 grid            : G1 = 1024, Z1 = 1024, n_max = 4000, q_target = 1/2
gate semantics     : conjunctive B1-Q1..Q8 AND B2-Q1..Q14
prototype criteria : F1..F10, frozen; F3 PREDICTED TO FAIL (disclosed)
K_e[B_i x B_j]     : FORBIDDEN (audit measured 1.9324e6)
retry ladder       : NONE
```
