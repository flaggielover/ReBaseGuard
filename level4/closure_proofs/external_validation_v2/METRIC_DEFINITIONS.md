# Frozen metrics and hypotheses

## Policies and detector

Every task uses the same two-sided inclusive CUSUM (`k = 0.5`, `m = 20`). Its
task threshold is calibrated on the calibration block under P0 and then shared
by all policies.

- P0 fresh: `rho = 0`.
- P1 full alarm-selected reuse: `rho = 1`.
- P2 ReBaseGuard: authoritative outcome-blind `rho = 0.029796`.

All policies consume the same post-alarm fresh block; only reference weighting
differs. P3 is absent. If ever added, it is exploratory and excluded from all
closure logic.

## Metrics

- **E1 normalized response:** mean capped post-intervention waiting time divided
  by the same policy's mean capped in-control wait at identical grid points.
  This is the matched-wait denominator, never a full-cycle denominator.
- **E2 reference distortion:** at each evaluation observation, absolute error
  between the active policy reference and an offline centered 24-hour residual
  mean, divided by train residual SD. The centered mean is measurement only and
  is never exposed to a model, detector, threshold, or policy.
- **E3 alert burden:** alarms per 1,000 observations on the natural evaluation
  stream, summarized in physical seven-day blocks. It is not a false-alarm
  rate.
- **E4 absolute delay:** capped observations and elapsed hours from intervention
  to first alarm. Administrative cap is four target ARLs; censored events are
  retained at the cap.
- **E5 diagnostics:** reference ACF1 and alarm-direction ACF1; never used for
  closure.

## Dependence-aware inference

Natural E2/E3 comparisons are paired by non-overlapping physical-week blocks,
then bootstrapped in moving blocks of two weeks. Controlled E1/E4 comparisons
are paired by the 120 chronological event locations and use moving blocks of
six events. There are 10,000 deterministic bootstrap draws. Effective blocks
must be at least 20 for every relevant policy/endpoint.

## Hypotheses

- **H2-1 reference distortion:** both P1/P2 and P1/P0 E2 point ratios are at
  least 1.10, and both one-sided 97.5% lower bounds exceed 1.0.
- **H2-2 operational consequence:** at least one of two predeclared
  co-primary effects passes: P1/P2 natural alert-burden ratio, or P1/P2
  medium-step E1 ratio. It must have point ratio at least 1.10 and a one-sided
  97.5% lower bound above 1.0. Absolute delay is reported but cannot create a
  third route to support.
- **H2-3 ReBaseGuard safety:** for every five primary interventions, the
  Bonferroni-simultaneous one-sided 99% upper bound on `E1(P2)/E1(P0)-1` is at
  most primary epsilon 0.10. Secondary epsilon 0.05 is also reported.
- **Strong safety contradiction:** any simultaneous one-sided 99% lower bound
  on `E1(P2)/E1(P0)-1` exceeding 0.10.
- **H2-4 mechanism package:** H2-1 AND H2-2 AND H2-3 in the same usable task.

Campaign closure requires at least two of three primaries to support H2-4, no
strong safety contradiction, green adversarial/reproduction gates, and intact
history. One supportive task yields `PARTIAL`; zero support, any strong safety
contradiction, or an integrity failure yields `FAILED`.
