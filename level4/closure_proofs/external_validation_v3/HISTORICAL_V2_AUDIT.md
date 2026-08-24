# Historical V2 forensic audit

External validation V2 is permanently `EXTERNAL-VALIDATION-V2-PARTIAL`.
Household supported H2-4; Metro and Beijing did not. This audit reads the
persisted V2 result JSON only and changes no V2 artifact.

| Descriptor | Household | Metro | Beijing |
|---|---:|---:|---:|
| Calibration residual ACF1 | 0.006 | 0.724 | 0.339 |
| Calibration excess kurtosis | 4.57 | 6.81 | 12.87 |
| Train residual scale | 0.203 | 0.557 | 0.201 |
| Threshold | 5.255 | 5.240 | 4.909 |
| Achieved cycle ARL | 239.21 | 60.18 | 59.51 |
| Evaluation observations / achieved ARL | 279.05 | 337.12 | 289.71 |
| P1/P2 reference-distortion ratio | 1.233 | 1.272 | 1.233 |
| P1/P2 alert-burden ratio | 1.280 | 0.752 | 1.204 |
| H2-1 / H2-2 / H2-3 / H2-4 | Y / Y / Y / Y | Y / N / N / N | Y / Y / N / N |

## POST-HOC HYPOTHESES

These interpretations are scientific coverage hypotheses, not a fitted
success classifier and not selection criteria based on reuse-policy outcomes.

1. Near-white predictive residuals may make a small certificate-aware reuse
   weight less disruptive across heterogeneous interventions. Household is
   consistent with this; Metro and Beijing retain much more dependence.
2. Tail heaviness and residual persistence may widen simultaneous safety
   intervals, particularly at strong interventions. Beijing's strongest
   failures and extreme kurtosis are consistent with that possibility.
3. Full reuse can reduce rather than increase natural alert burden in some
   regimes, as Metro demonstrates. Reference distortion alone therefore does
   not imply the frozen operational penalty.
4. Threshold and evaluation-length/ARL ratio do not explain the V2 split: the
   thresholds were similar and all tasks had roughly 279--337 achieved ARLs in
   evaluation.
5. The uniform 20-block floor may have left strong-intervention safety
   inference too variable. V3 therefore raises every closure-relevant floor to
   40 without changing the practical non-inferiority margin.

V3 covers both a moderately persistent industrial residual regime and a
near-white retail-demand residual regime. Their selection used only raw-stream
and train/calibration diagnostics.
