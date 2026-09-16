# Synthetic qualification r1: result

The protocol `config/QUALIFICATION_PROTOCOL.json` and the bound code were frozen in commit `10911e51`, on base
`d7d3c08b`. The trials ran after that commit, and the bound code is unchanged since.

```text
QN1_SOUNDNESS              = PASS   15/15 trials, 0 containment violations (objects, assembly, signed export; e0 + 17 exact grid points)
QN2_MUTATION_SENSITIVITY   = PASS   8/8 required mutations detected; each designated trial clean when unmutated
QN3_EXACT_ARITHMETIC       = PASS
QN4_SCIENTIFIC_FENCE       = PASS
QN5_FROZEN_ASSEMBLY_TABLE  = PASS   (checkpoint.json 1c2a6825; reference rule == frozen table, m in {1,2,3,5})
QN6_DETERMINISM            = PASS   fresh-process replay byte-identical (evidence/qualification_r1/REPLAY.txt)
evidence sha256            = 75e159237500433b0ce05a67dcf712e47df59a01475ae9b86337217e3aed9452
```

| Mutation | Trial | First detection |
|---|---|---|
| M1 order-3 Leibniz coefficients (3 → 2) | T_H | midpoint `F:r:3` |
| M2 drop `k_3 ε_F` | T_F | midpoint `F:r:3` |
| M3 drop `3k_1 ε_H` | T_H | midpoint `F:r:3` |
| M4 midpoint used as the cell bound | T_X | cell grid point 0 |
| M6 Taylor bound without the tower | T_X | cell grid point 0 |
| M7 assembly drops W | T_X | assembly midpoint, m = 2 |
| M8 coefficient `1/t` instead of `1/t − 1/m` | T_X | assembly midpoint, m = 2 |
| M9 lower-bound sign | T_X | export at `e0` |

**Disclosure.** Before `d7d3c08b` was visible, the same session ran this identical protocol, with byte-identical
protocol and code, on an unpublished branch based on `e8680998`. That run produced the same evidence hash. That
line was not published: its review packet stated that no K5-B countersignature existed, which `d7d3c08b` made
false. This namespace is the re-issue.

**Scope.** This qualifies the signed order-3 error **algebra** on synthetic systems with exact derivatives. It says
nothing about the CUSUM operators, Arb soundness or feasibility, any `(D,m)`, or any `R'''` value, including the
sign at CUSUM cell 0 (DESIGN §7). The grid checks are necessary-condition samples; the proofs are in DESIGN §3.

```text
K5_B_COUNTERSIGNATURE                  = PASS_WITH_SCOPE_LIMITATION   (d7d3c08b; separate Claude session, not human, not a different model family)
B3                                     = CLOSED

ORDER3_PRODUCER_DESIGN                 = PASS
REFERENCE_KERNEL                       = PASS
SYNTHETIC_QUALIFICATION                = PASS

CERTIFIED_REAL_CUSUM_ORDER3_PRODUCER   = NOT_BUILT
REAL_INTERVAL_QUALIFICATION            = NOT_DONE
B1_NO_CERTIFIED_ORDER3_PRODUCER        = OPEN

SCIENTIFIC_K5_PROBES_AUTHORIZED        = NO
FULL_K5_PRODUCTION_AUTHORIZED          = NO
```
