# Frozen V3 metrics and hypotheses

## Metrics

- **E1 reference-state distortion:** absolute active-reference error relative
  to an offline centered 24-hour residual mean, divided by train residual SD.
  The centered mean is measurement only and is never exposed to the monitor.
- **E2 alert burden:** alarms per 1,000 observations on the natural evaluation
  stream. This is not called a false-alarm rate.
- **E3 normalized detection response:** mean capped post-intervention wait
  divided by the same policy's mean capped in-control wait at matched event
  locations.
- **E4 absolute detection delay:** capped observations and elapsed hours from
  intervention to first alarm; censored events remain at the four-ARL cap.
- **E5 reference ACF1** and **E6 alarm-direction ACF1:** descriptive only.

## Hypotheses

- **H3-1:** P1/P2 and P1/P0 natural E1 ratios are each at least 1.10 and each
  paired one-sided 97.5% lower bound exceeds 1.0.
- **H3-2 Route A:** P1/P2 and P1/P0 natural E2 ratios are each at least 1.10
  and each paired one-sided 97.5% lower bound exceeds 1.0.
- **H3-2 Route B:** at fixed `STEP_1.0`, P1/P2 and P1/P0 E3 ratios are each at
  least 1.10 and each paired one-sided 97.5% lower bound exceeds 1.0.
- **H3-2:** Route A OR Route B. E4 cannot create a third route.
- **H3-3:** for every five primary interventions, the
  Bonferroni-simultaneous one-sided 99% upper bound on
  `E3(P2)/E3(P0)-1` is at most primary epsilon 0.10. Epsilon 0.05 is secondary.
- **Strong contradiction:** any simultaneous one-sided 99% lower bound on
  `E3(P2)/E3(P0)-1` exceeds 0.10.
- **H3-4:** H3-1 AND H3-2 AND H3-3 in the same gated, reliable task.

Direction alone never passes. Every relevant comparison must retain at least
40 effective blocks.
