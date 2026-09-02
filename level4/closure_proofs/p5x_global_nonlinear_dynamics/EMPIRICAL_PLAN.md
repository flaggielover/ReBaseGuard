# P5X empirical support plan

Simulation is **support, never proof**. Its only admissible roles here are
correspondence, non-vacuousness, quantification and finite-sample illustration.

## 1. Firewall

| role | admissible | inadmissible |
|---|---|---|
| correspondence | check that an independent Monte Carlo estimate lies inside a certified enclosure | use Monte Carlo to *establish* an enclosure |
| non-vacuousness | show the certified interval is narrow enough to be informative and that the theorem's scope is non-empty | widen a target after seeing that the certificate missed it |
| quantification | report measured `R`, `S`, `E_pi[e^2]`, `RMS_pi` with intervals | quote them as theorem constants |
| finite-sample | show how many cycles are needed for the stationary bound to be visible | infer a bound from that number |

Gate `G8` fails the campaign if any proof-path artifact cites a Monte Carlo
number; gate `G9` requires the correspondence to *agree*, and treats
disagreement as a defect to investigate, not as a scientific finding.

## 2. Planned checks

| id | check | design |
|---|---|---|
| `E1` | `R_{D,m}(e)` correspondence | fresh seed family, independent of P5's `20260501` / `20261119`; both detectors, `m in {1,2,3,5}`; `e` at the midpoint of a sample of accepted certified cells; batch standard errors; require the MC interval to intersect the certified enclosure in every cell |
| `E2` | `S_{D,m}(e)` correspondence | same design, second moments |
| `E3` | stationary dispersion | simulate the frozen chain at a grid of `rho` for each `(D,m)`; require the measured `E_pi[e^2]` to lie inside `[rho^2 s_min + (1-rho)^2/m , rho^2 M_2 + (1-rho)^2/m]` in every cell |
| `E4` | non-vacuousness | report, per cell, the ratio (upper bound)/(lower bound) and the ratio (lower bound)/`r_lin^2`; the campaign claims "high dispersion" only where the second ratio is `> 100` |
| `E5` | independent re-derivation | a second, structurally different estimator of `R` (P5's own kernel, re-run) versus the certified enclosure, as a cross-method check of `P5X-T1` |
| `E6` | finite-sample | burn-in and replicate counts needed for `E3` to resolve; reported, not used |

## 3. Relationship to P5's data

P5's measured maps and chain statistics are used **only** as an external
consistency reference and are never re-adjudicated, re-interpreted or
re-labelled. A disagreement between a P5X certified enclosure and a P5 measured
value is, by gate `G10`, first treated as a P5X defect.
