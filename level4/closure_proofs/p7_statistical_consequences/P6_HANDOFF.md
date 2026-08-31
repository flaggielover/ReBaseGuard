# P6 handoff: what a safe re-baselining algorithm has to control

P7 does not design a mitigation. This note says only what the evidence shows a
mitigation must fix, and — as importantly — what it must **not** aim at.

All numbers are from `results/consequences.json`; nominal `A(0) ~ 465`.

---

## 1. The quantity to control is reference-state dispersion, not the multiplier

`THEOREM P7-A` is exact: conditionally on the entering reference error `e_j`,
the cycle is a fresh cycle at innovation mean `-e_j`. Therefore

```text
ARL_0 = E_pi[A(e)],     E[delay | Delta] = E_pi[A(e - Delta)].
```

Every first-moment monitoring consequence measured here is a functional of the
law of `e` alone. The data motivate controlling that law—especially dispersion
and mass near post-change blind spots—rather than controlling `rho` alone.
Reducing `E_pi[e^2]` by itself is not proved to improve every metric.

`A` is extremely steep: `A(0) = 465`, `A(0.1) = 348`, `A(0.2) = 191`,
`A(0.5) = 38`. A reference RMS of `0.2` already costs 59% of the in-control ARL.
The tolerable reference RMS is of order `0.05`, i.e. `E_pi[e^2] <~ 0.0025`.
**Every configuration P7 measured is 30x to 400x above that in second moment.**

## 2. Do not target `rho < rho_c`

This is the strongest negative instruction P7 can give P6.

* The pre-committed boundary test returns
  `LOCAL-MATHEMATICAL, NOT OPERATIONAL` (`results/boundary_verdict.json`): at
  most 3 of 8 detector/window families show a rate peak at `rho/rho_c = 1` in
  any pre-specified metric, against a threshold of 4.
* The measured in-control ARL is **maximised at `rho ~ 0.14 to 0.25`, which is
  `1.25x to 4.1x rho_c`** — inside the region P3 classifies as locally
  repelling — and the improvement over `rho = 0` is `+7.2%` to `+14.8%`,
  resolved at `z >= 13.5` in all eight families (`results/adversarial.json`,
  `non_monotonicity`; EXPLORATORY, not a recommendation).
* Conditional P7-C is consistent with local repulsion escaping into dispersion,
  but does not prove global stability or causality. Holding `rho` below `rho_c`
  buys a local linear classification; the experiment does not show that it buys
  an operational monitoring guarantee.

A P6 design justified by "keep `rho` under the P3 critical fraction" would be
optimising the wrong quantity.

## 3. Where the damage actually is, ranked

| rank | consequence | size | attribution |
|---:|---|---|---|
| 1 | **detection delay for `Delta = 1`** | `10.4` nominal -> `52.8 to 66.1` under full reuse (**+360% to +540%**) | roughly half is re-baselining per se, half is reuse (`28.7 -> 63.9` at `m=5`) |
| 2 | **loss of discrimination** | `R_Delta = E[tau_Delta]/E[tau_0]` rises from `0.022` nominal to `1.06` at `m=1, rho=1`: the shifted cycle is **longer** than the in-control cycle | reuse |
| 3 | **in-control ARL** | `465 -> 48 to 80` at full reuse (`-83%` to `-90%`); `-39.5%` to `-50.6%` of that is reuse-attributable against the same-`m` fresh control, `PRACTICALLY_MATERIAL` in all 8 families | split |
| 4 | **immediate post-alarm false alarm** | the cycle *right after* the first re-baselining has mean length `5.6 to 9.4` under full reuse, against `463 to 474` for the first cycle — a **98%** collapse | reuse |
| 5 | **false-alarm probability** | `FAP(100)` rises from `~0.19` nominal to `0.82 to 0.90` | split |

## 4. The failure mode is a tail, not a slowdown

Direct simulation (`results/delay_validation.json`) shows strong right-tail
inflation. At CUSUM `m=1, rho=1, Delta=1`: mean `52.6`, but **median `7`** —
below the nominal `10.35` — with `q95 = 275` and `P(delay > 100) = 11.4%`.

Most cycles still detect quickly; roughly one cycle in nine has a pre-shift
dispersed reference that happens to lie near the post-change mean and is
effectively **blind** to the shift. The changed observations in the measured
cycle do not construct its entering reference.
`P(|e - Delta| < 0.2)` is tabulated per cell in `STATISTICAL_CONSEQUENCES.md` §4.

A mitigation evaluated only on mean delay will look far better than it is. P6
should adopt a tail criterion — `P(delay > c)` or the blind-spot probability —
alongside the mean.

## 5. The most vulnerable configurations

* **Reuse-attributable ARL loss grows with `m`**: `-40%` at `m=1` rising to
  `-51%` at `m=5`, both detectors. Larger windows do *not* protect against
  reuse; they only raise the fresh-control baseline.
* **Absolute damage is worst at small `m`**, because the fresh reference is
  itself noisy (`Var = 1/m`). `m = 1` is unusable under any `rho`.
* **`rho >= 0.5` is where the collapse starts.** Between `rho = 0.25` and
  `rho = 1` the in-control ARL falls by roughly half in every family, and the
  reference MSE roughly triples.
* **CUSUM and SR behave the same.** Every consequence agrees between the two
  ARL-matched detectors to within a few percent (§6 below). A mitigation may be
  designed detector-agnostically at this level of evidence.

## 6. Operationally unsafe regions, as measured

| region | status |
|---|---|
| `rho >= 0.5`, any `m in {1,2,3,5}` | unsafe: `>= 25%` reuse-attributable ARL loss, `R_Delta >= 0.5` |
| `rho = 1`, any `m` | severely unsafe: `-40%` to `-51%` ARL, delay `+360%` to `+540%`, near-immediate false alarm after the first re-baselining |
| `m = 1`, any `rho` | unsafe irrespective of reuse: reference RMS `~1.0`, `ARL_0 <= 96` |
| `rho <= rho_c`, any `m` | **not** safe, and not distinguishable from its neighbourhood; the P3 boundary is not an operational one |
| anywhere in the measured grid | no cell reaches within a factor of 4 of the nominal `ARL_0` |

## 7. What P7 explicitly does not hand over

* No algorithm, no correction term, no bias-adjustment proposal.
* No claim that any measured `rho` is safe. The best cell in the whole matrix
  still loses 62% of the nominal in-control ARL.
* No robustness beyond frozen Gaussian CUSUM/SR and `m in {1,2,3,5}` — that is
  P8's.
