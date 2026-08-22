# Track-3 numerical correspondence report

## Verdict

```text
LOCATION-FAMILY-NUMERICAL-FAILED
NUMERICAL GATE FAILED — LEAN NOT AUTHORIZED
```

The frozen campaign ran once with master seed `2026082307`, six mandatory
regular families, Route A at 48 batches of 10,000 paths, and two independent
Route-B replications at 48 batches of 5,000 paired path streams.  No sample,
step, threshold, family, estimand, or gate changed after outcomes.

Five families passed every primary criterion.  The mandatory t3 cell failed
one and only one frozen predicate: its two direct finite-difference
replications differed by `4.605%`, exceeding the frozen 3% relative band.
Their covariance-aware difference was only `|z|=1.318`, but both conditions
were required.  The favorable z-value cannot rescue the relative failure.

## Primary correspondence

All SEs are computed from batch estimates.  Route B uses paired `+h/-h` batch
derivatives at the frozen primary step `h=0.0125`.

| family | `Gamma_f` Route A | predicted derivative | direct Route B | `|z|` | relative | replication `|z|` | replication relative | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Gaussian | 15.9375 ± 0.0574 | -14.9375 ± 0.0574 | -14.7927 ± 0.0661 | 1.653 | 0.974% | 0.045 | 0.041% | PASS |
| t10 | 15.5459 ± 0.0702 | -14.5459 ± 0.0702 | -14.3312 ± 0.0844 | 1.956 | 1.487% | 0.547 | 0.646% | PASS |
| t5 | 13.3638 ± 0.1588 | -12.3638 ± 0.1588 | -12.1779 ± 0.1106 | 0.961 | 1.515% | 0.677 | 1.234% | PASS |
| **t3** | **8.7101 ± 0.4632** | **-7.7101 ± 0.4632** | **-7.6338 ± 0.1339** | **0.158** | **0.995%** | **1.318** | **4.605%** | **FAIL** |
| contam 5% | 15.3817 ± 0.1431 | -14.3817 ± 0.1431 | -14.7231 ± 0.1116 | 1.882 | 2.346% | 0.561 | 0.854% | PASS |
| contam 10% | 18.3196 ± 0.1172 | -17.3196 ± 0.1172 | -17.1737 ± 0.1362 | 0.812 | 0.846% | 0.099 | 0.157% | PASS |

Every Route-A operating-point ARL reproduced its historical Stage-D value
within 0.23%, far inside the frozen 2% control.  Every structural reflection,
score, rho-scaling, source-separation, seed, protocol, and historical-integrity
check passed.  Exact ties and simultaneous crossings were zero in both routes
for all six families.

## Gaussian control

The new Gaussian `Gamma_f=15.9375 ± 0.0574` agrees with Stage D's independent
batch estimate `15.8671 ± 0.0495`: combined `|z|=0.928`, relative discrepancy
`0.442%`.  Source algebra gives `psi(z)=z`, so

```text
Gamma_f=E[Z_tau T_tau]
```

exactly.  The Gaussian sign and specialization controls pass.

## t3 and the historical estimands

The new raw-observation quantity is

```text
Gamma_f = E[Z_tau sum psi(Z_t)] = 8.7101 ± 0.4632.
```

Stage D measured

```text
Gamma_psi                         = 2.5980,
Gamma_psi / E[psi']               = 1.2990.
```

The new number is not a selection between those two.  The definition audit
proved before outcomes that both concern the score-transformed terminal
functional `psi(Z_tau)`, whereas actual ReBaseGuard reuse has terminal
functional `Z_tau`.  Hence neither historical quantity is the raw-reuse gain.
Stage D's historical t3 verdict remains `AMBIGUOUS` exactly as frozen.

## Geometric ladder diagnostics

The t3 Route-B replications were:

| `h` | replication 1 | replication 2 |
|---:|---:|---:|
| 0.05 | -7.6336 ± 0.0911 | -7.8095 ± 0.0942 |
| 0.025 | -7.5647 ± 0.1442 | -7.7644 ± 0.1198 |
| 0.0125 primary | -7.4580 ± 0.1892 | -7.8095 ± 0.1880 |

The coarser steps happen to have relative replication discrepancies below 3%.
They are not primary and cannot replace the frozen finest step.  Observed order
was noisy/undefined and Richardson was secondary, so neither controls the
verdict.

## Irregular edge case

For translated centered uniform noise with deterministic `tau=1`, the interior
a.e. density score is zero but support motion gives

```text
d/de E_e[Z_1]|_0=-1.
```

The naive interior-score calculation gives zero.  This exact mismatch
demonstrates why common support/local absolute continuity is load-bearing.  It
is an irregular negative control, not a theorem confirmation.

## Consequence

The numerical evidence strongly supports the derived score identity, including
pooled t3 correspondence, but the complete frozen primary gate did not pass.
Accordingly Lean is not authorized.  No general location-family closure is
claimed from the five passing families or from the favorable pooled t3 result.

