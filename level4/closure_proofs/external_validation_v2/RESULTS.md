# External validation V2 results

All results below are generated from `results/summary.json`. Null, unfavorable,
and contradictory directions are retained.

| Task | E2 P1/P2 ratio [95% CI] | E3 P1/P2 ratio [95% CI] | H2-1 | H2-2 | H2-3 | H2-4 |
|---|---:|---:|---|---|---|---|
| A — Household power | 1.233 [1.104, 1.395] | 1.280 [1.029, 1.673] | YES | YES | YES | YES |
| B — Metro traffic | 1.272 [1.147, 1.398] | 0.752 [0.683, 0.828] | YES | NO | NO | NO |
| C — Beijing PM2.5 | 1.233 [1.127, 1.344] | 1.204 [1.112, 1.314] | YES | YES | NO | NO |

## Task decisions

- **A — Household power:** H2-1=True; H2-2=True (burden route=True, medium-step route=False); H2-3=True; failed safety conditions=none; H2-4=True.
- **B — Metro traffic:** H2-1=True; H2-2=False (burden route=False, medium-step route=False); H2-3=False; failed safety conditions=STEP_0.5, STEP_2.0; H2-4=False.
- **C — Beijing PM2.5:** H2-1=True; H2-2=True (burden route=True, medium-step route=False); H2-3=False; failed safety conditions=STEP_1.0, STEP_2.0; H2-4=False.

## Campaign result

Only household power supports H2-4. Metro shows reference distortion but its
full-reuse alert burden is lower, the medium-step response route is unsupported,
and simultaneous P2 non-inferiority is not demonstrated. Beijing shows
reference distortion and higher P1 alert burden, but simultaneous P2
non-inferiority is not demonstrated. No task shows a strong P2 safety
contradiction.

The frozen >=2/3 closure rule is therefore not met: the scoped result is
`EXTERNAL-VALIDATION-V2-PARTIAL`.
