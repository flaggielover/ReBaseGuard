# B_int P1-bound successor — BINT_P1_BOUND_GOVERNANCE_AND_PILOT_PASS

Authorization: `P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR` (commit 014879b, `GOVERNANCE.md`).
Implementation: `code/sr_o9_bint_p1.py`. The only change is the source of the L-R3.1 Lagrange factor
`A_9`, which becomes `[-M/9!, M/9!]`. It is scoped to the certify call; candidates are built outside it.
Evidence: `config/BINT_P1_PILOT_MANIFEST.json`. **T2 is not closed.** Nothing was run on the 3,994-patch
universe, and there was no production run and no T3/T4/T5 work.

## Kill test (all four pass)
| case | b48973d6 int/allowance | new worst int/allowance | endpoint worst C·δ_end/(1/250) | all local gates | CPU s |
|---|---|---|---|---|---|
| cell 0 (51,63) | 4.96 (FAIL) | 6.38e-5 | 5.4e-11 | PASS | 2.07 |
| cell 0 (63,54) | 1.25 (FAIL) | 2.53e-5 | 6.2e-11 | PASS | 2.07 |
| cell 150 (51,63) | 1.81 (FAIL) | 2.34e-5 | 1.9e-11 | PASS | 2.07 |
| cell 150 (17,11) control | 0.13 | 2.77e-5 | 2.0e-16 | PASS | 5.66 |

All gate comparisons are exact rationals on the Arb upper bound. Node results are identical to the fa92afb
diagnostic: the node hashes match in all 4 cases. Invariants against b48973d6 hold in every case: n_z,
strip IDs, strip P1, C_upper, candidate identity hashes and contracts are all equal.

## 36-case bounded pilot (same cases as b48973d6)
- **B_int:** 36/36 PASS. **Endpoint:** 36/36 PASS. **All local gates:** 36/36 PASS. b48973d6 had 33/36,
  with all three failures on the int line.
- **Worst ratios:** int/allowance 1.42e-4; endpoint 6.2e-11.
- **Resources:** 171 CPU-s in total (max 7.5 s, mean 4.8 s); peak RSS 60 MiB.
- **Channel changes against b48973d6** (200 node-channel checks):
  - int, trunc, tail and end decreased everywhere; round is unchanged (0).
  - eq moved by at most 8e-7 relative (at most 3.4e-9 of its allowance), because the new ball's midpoint
    is exactly 0. eq+int is never larger than before.
- **Disclosure:** in 444 of 1,644 Lagrange-factor evaluations, the old interval-series ball was narrower
  than M/9!. These are panels where sp^(9) is tiny; the new ball is still rigorous there, and B_int still
  passes with at least ×7,000 margin.
