# L4R-12 historical-evidence audit

No new scientific experiment was run.

## Frozen crossing evidence

- Stage-D Gamma grid: `m={1,2,5,10,20,50,75,100}`, 2,000,000 independent
  cycles, 20 batches, convention A.
- Primary crossing bracket: `[50,75]`; endpoint separation from two is
  `+108.55 SE` and `-14.54 SE`.
- Frozen log-m interpolation: `72.189259`; the bracket, not the interpolation,
  is primary.
- Stage-D adversarial interpolation check compared log-linear, linear-m, and
  local-quadratic values and passed its frozen tolerance.
- Later D4 independently refined the bracket to `[70,72]`, with Gamma estimates
  `2.016702` and `1.993263`; its log-linear crossing is `71.419386`.

## Frozen D2.5 design

- `rho=1`; `m={10,20,50,65,75,90,100}`; all points retained.
- 20,000 replicates, 80 cycles, 30-cycle burn-in; replicate is the statistical
  unit.
- Shifts `Delta={0.5,1.0}` for the reported `R_Delta` response.
- Preselected metrics: cycle ARL, reference MSE, reference-state ACF1,
  alarm-direction ACF1, and reported `R_Delta` at both shifts.
- The metric family, negative reading, and prohibition on post-outcome metric
  selection were committed before outcomes.

## Result and uncertainty

Four points lie below and three above the historical interpolated crossing.
None of the four primary localization metrics has its steepest log-m change
across the crossing; all four raw mean sequences are monotone. Across the nearest
pair (`m=65` versus `m=75`), each smooth change is resolved by more than 12
combined standard errors. Thus the negative conclusion is not merely failure to
reach significance. Alarm-direction alternation also persists at `m=100`.

Limitations are retained: this is numerical evidence for the frozen Gaussian
CUSUM, full reuse, Stage-D window convention, grid, shifts, and monitored
metrics. It is not a universal no-effect result.

