# Stage C — protocol deviations

**No protocol quantity was changed after seeing results.** No endpoint, grid,
sample size, tolerance or success criterion in
`STAGE_C_PROTOCOL.md` (sha256
`36bd6ba03a20b7f87dc0eb91c42e5c023c03d7a23cba0c515390d1130b2cedd7`) was
rewritten, re-scoped or softened.

Two things are nonetheless recorded here, because both look superficially like
the thing this file exists to prevent.

## 1. Criterion C6 failed and was left failed

C6 failed at `Delta = 0.25` and `Delta = 0.5`. It was **not** amended, and the
Stage C decision reflects the failure. The criterion turned out to be badly
formulated — it compares raw delays between policies whose in-control ARLs
differ by 1.7x — and that is analysed in
[`CRITERION_C6_DIAGNOSIS.md`](CRITERION_C6_DIAGNOSIS.md). The analysis is a
diagnosis, not an amendment; the baseline-free ratio it introduces is reported
only as a labelled secondary diagnostic and never as a gate.

## 2. The C7 check was corrected TOWARD the protocol, not away from it

The protocol, section 8, specifies

```text
sigma_combined^2 = SE_direct^2 + SE_decomp^2 + bias_interp^2
```

with `bias_interp` "estimated by halving the e-grid". The first implementation
of the adversarial check **omitted the `bias_interp` term entirely** and reported
`max |z| = 3.70`, i.e. a failure. That was an implementation bug: the check did
not compute the formula the protocol had already fixed.

Implementing the specified formula gives `max |z| = 2.12`, i.e. a pass. Because
this is the one place where a correction turned a failure into a pass, all three
variants are reported side by side in the check output and in the report:

| variant | max \|z\| | verdict |
|---|---|---|
| without the pre-specified `bias_interp` term (the bug) | 3.70 | fail |
| **protocol formula, `bias_interp` = fine − coarse** | **2.12** | **pass** |
| sharper Richardson residual bias, `(fine − coarse)/3` | 3.34 | 2 of 23 points exceed 3 |

Supporting facts, all reported:

* every one of the 23 gaps is **positive**, and refining the `e`-grid **raises**
  the decomposition with a ratio of about 3.8 per halving — consistent with
  `O(h^2)` error from log-linear interpolation of a convex function, which
  biases the decomposition low. The sign, the magnitude and the grid-scaling all
  agree with that single explanation;
* the raw agreement between the two ARL routes is better than **0.6%** at every
  `rho`;
* **the C7 verdict does not change the Stage C decision**, because C6 already
  fails and the decision rule returns `STAGE-C-PARTIAL` either way. There is
  therefore no outcome riding on this correction.

C7 is flagged in the report as the weakest of the criteria.

## 3. Permitted additions (recorded, never substituted)

* two `rho` points added to the mandated grid **before** the campaign (the two
  policy values; protocol section 5);
* four further `rho` points near `rho_c` added by the adversarial refinement
  check (`rho in {0.055, 0.062, 0.068, 0.072}`).

No grid point was deleted.
