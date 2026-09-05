# Repair 1 regression: reviewed (c0a1f40) vs repaired

NON-RESULT-BEARING. A re-certification of already-reviewed CUSUM
obligations through the repaired path, to confirm the independently
accepted components survive the repair. Not production, not a new
scientific campaign. Cell 325 is deliberately absent: its state remains
CURRENT_CERTIFICATE_FAILURE_ONLY and it is out of scope here.

The duplicate removed by the repair is `reward_allow[k]`, of order
1e-53 to 1e-51 -- roughly 48 orders of magnitude below the certificate
values it sat inside. The certified quantities are therefore EXPECTED
to be unchanged, and they are. Correctness is established by the
accounting invariant in `repair_check.py`, not by a numerical change.

| cell | scope | bits | m | quantity | reviewed | repaired | delta |
|---:|---|---:|---:|---|---|---|---|
| 221 | full | 256 | 1 | mag D | 0.490988804903 | 0.490988804903 | +0.000e+00 |
| 221 | full | 256 | 1 | M_R2 | 354.110668235 | 354.110668235 | +0.000e+00 |
| 221 | full | 256 | 1 | B_cover | 0.00114094579842 | 0.00114094579842 | +0.000e+00 |
| 221 | full | 256 | 1 | status | PASS | PASS | same |
| 221 | full | 256 | 2 | mag D | 0.698790284535 | 0.698790284535 | +0.000e+00 |
| 221 | full | 256 | 2 | M_R2 | 313.087852903 | 313.087852903 | +0.000e+00 |
| 221 | full | 256 | 2 | B_cover | 0.00140736691464 | 0.00140736691464 | +0.000e+00 |
| 221 | full | 256 | 2 | status | PASS | PASS | same |
| 221 | full | 256 | 3 | mag D | 0.82006118512 | 0.82006118512 | +0.000e+00 |
| 221 | full | 256 | 3 | M_R2 | 304.553894833 | 304.553894833 | +0.000e+00 |
| 221 | full | 256 | 3 | B_cover | 0.00158031780792 | 0.00158031780792 | +0.000e+00 |
| 221 | full | 256 | 3 | status | PASS | PASS | same |
| 221 | full | 256 | 5 | mag D | 0.912895995005 | 0.912895995005 | +0.000e+00 |
| 221 | full | 256 | 5 | M_R2 | 300.932314274 | 300.932314274 | +0.000e+00 |
| 221 | full | 256 | 5 | B_cover | 0.00171601572502 | 0.00171601572502 | +0.000e+00 |
| 221 | full | 256 | 5 | status | PASS | PASS | same |
| 221 | m1_only | 256 | 1 | mag D | 0.490988804903 | 0.490988804903 | +0.000e+00 |
| 221 | m1_only | 256 | 1 | M_R2 | 354.110668235 | 354.110668235 | +0.000e+00 |
| 221 | m1_only | 256 | 1 | B_cover | 0.00114094579842 | 0.00114094579842 | +0.000e+00 |
| 221 | m1_only | 256 | 1 | status | PASS | PASS | same |
| 221 | m1_only | 384 | 1 | mag D | 0.490988804903 | 0.490988804903 | +0.000e+00 |
| 221 | m1_only | 384 | 1 | M_R2 | 354.110668235 | 354.110668235 | +0.000e+00 |
| 221 | m1_only | 384 | 1 | B_cover | 0.00114094579842 | 0.00114094579842 | +0.000e+00 |
| 221 | m1_only | 384 | 1 | status | PASS | PASS | same |
| 221 | m1_only | 512 | 1 | mag D | 0.490988804903 | 0.490988804903 | +0.000e+00 |
| 221 | m1_only | 512 | 1 | M_R2 | 354.110668235 | 354.110668235 | +0.000e+00 |
| 221 | m1_only | 512 | 1 | B_cover | 0.00114094579842 | 0.00114094579842 | +0.000e+00 |
| 221 | m1_only | 512 | 1 | status | PASS | PASS | same |
| 293 | full | 256 | 1 | mag D | 0.607628746993 | 0.607628746993 | +0.000e+00 |
| 293 | full | 256 | 1 | M_R2 | 7.00476229642 | 7.00476229642 | +0.000e+00 |
| 293 | full | 256 | 1 | B_cover | 0.0120857739309 | 0.0120857739309 | +0.000e+00 |
| 293 | full | 256 | 1 | status | PASS | PASS | same |
| 293 | full | 256 | 2 | mag D | 0.588118518499 | 0.588118518499 | +0.000e+00 |
| 293 | full | 256 | 2 | M_R2 | 15.6403904629 | 15.6403904629 | +0.000e+00 |
| 293 | full | 256 | 2 | B_cover | 0.0131360981975 | 0.0131360981975 | +0.000e+00 |
| 293 | full | 256 | 2 | status | PASS | PASS | same |
| 293 | full | 256 | 3 | mag D | 0.547004226308 | 0.547004226308 | +0.000e+00 |
| 293 | full | 256 | 3 | M_R2 | 24.3274631734 | 24.3274631734 | +0.000e+00 |
| 293 | full | 256 | 3 | B_cover | 0.0138054976967 | 0.0138054976967 | +0.000e+00 |
| 293 | full | 256 | 3 | status | PASS | PASS | same |
| 293 | full | 256 | 5 | mag D | 0.458390906202 | 0.458390906202 | +0.000e+00 |
| 293 | full | 256 | 5 | M_R2 | 46.8596930102 | 46.8596930102 | +0.000e+00 |
| 293 | full | 256 | 5 | B_cover | 0.0158665945181 | 0.0158665945181 | +0.000e+00 |
| 293 | full | 256 | 5 | status | PASS | PASS | same |

## S0 charge audit (repaired)

| cell | object | charge count | local | dependency | reward_allow |
|---:|---|---:|---|---|---|
| 221 | F_0 | 1 | 0.000e+00 | 4.309445e-53 | 4.309445e-53 |
| 221 | dF_0 | 1 | 0.000e+00 | 2.479124e-52 | 2.479124e-52 |
| 221 | H_0 | 1 | 0.000e+00 | 1.469277e-51 | 1.469277e-51 |
| 221 | F_0 | 1 | 0.000e+00 | 4.309445e-53 | 4.309445e-53 |
| 221 | dF_0 | 1 | 0.000e+00 | 2.479124e-52 | 2.479124e-52 |
| 221 | H_0 | 1 | 0.000e+00 | 1.469277e-51 | 1.469277e-51 |
| 221 | F_0 | 1 | 0.000e+00 | 4.309445e-53 | 4.309445e-53 |
| 221 | dF_0 | 1 | 0.000e+00 | 2.479124e-52 | 2.479124e-52 |
| 221 | H_0 | 1 | 0.000e+00 | 1.469277e-51 | 1.469277e-51 |
| 221 | F_0 | 1 | 0.000e+00 | 4.309445e-53 | 4.309445e-53 |
| 221 | dF_0 | 1 | 0.000e+00 | 2.479124e-52 | 2.479124e-52 |
| 221 | H_0 | 1 | 0.000e+00 | 1.469277e-51 | 1.469277e-51 |
| 293 | F_0 | 1 | 0.000e+00 | 4.309445e-53 | 4.309445e-53 |
| 293 | dF_0 | 1 | 0.000e+00 | 2.810344e-52 | 2.810344e-52 |
| 293 | H_0 | 1 | 0.000e+00 | 1.875821e-51 | 1.875821e-51 |

Representation across all records: ['A: residual against fixed candidate + separate epsS']

`charge count = 1` everywhere, with the charge in the dependency
graph and zero in the local residual: representation A, exactly
once, as the frozen ERROR_ALGEBRA requires.

## Frozen-kernel correspondence (unchanged by the repair)

| object | reviewed reference | repaired |
|---|---|---|
| h_2:0 (cell 221) | ~1.83e-06 | 1.831353e-06 |
| S_1:0 (cell 221) | ~2.76e-06 | 2.764060e-06 |
| h_2:0 (cell 293) | ~1.83e-06 | 6.621631e-06 |
| S_1:0 (cell 293) | ~2.76e-06 | 1.136417e-05 |
