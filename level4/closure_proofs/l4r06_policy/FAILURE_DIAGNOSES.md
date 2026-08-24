# Failure diagnoses and unfavorable findings

## HISTORICAL C6 — immutable failure

Historical Stage C remains `STAGE-C-PARTIAL`. C6 failed at `Delta=0.25` and
`Delta=0.5` because the paired upper 95% bounds for raw
`delay(ReBaseGuard)-delay(full reuse)` exceeded 25% of full-reuse delay. The
raw-delay comparison was confounded by materially different in-control alarm
rates, but that diagnosis does not rewrite or reinterpret C6.

## NEW L4R-06 campaign — separate later evidence

Primary unfavorable conditions retained: **0**.
Secondary epsilon=0.05 failures retained: **2**.

- `m=1, Delta=0.25`: simultaneous upper 95% `0.057971` exceeds 0.05 but remains below the controlling 0.10 margin.
- `m=100, Delta=0.25`: simultaneous upper 95% `0.063187` exceeds 0.05 but remains below the controlling 0.10 margin.

### Descriptive P2 advantages (non-controlling)

- `m=70`: P2 has lower reference MSE (`0.013507` vs `0.014364`), higher ARL0 (`415.463` vs `405.744`), and lower normalized response at 4/4 shifts.
- `m=100`: P2 has lower reference MSE (`0.009454` vs `0.013414`), higher ARL0 (`466.944` vs `442.209`), and lower normalized response at 4/4 shifts.

At `m=100`, P3 is exactly identical to P1 in every retained per-replicate
summary. This is the pre-specified natural saturation of the common clipping
rule; it supplies no P3-versus-P1 improvement and was excluded from H6-2/H6-3.

P2 outcomes and all 80 policy/regime/shift cell summaries remain in the final
scientific JSON whether favorable or unfavorable. No policy, regime, shift,
sample size, threshold, or margin was changed after outcomes.
