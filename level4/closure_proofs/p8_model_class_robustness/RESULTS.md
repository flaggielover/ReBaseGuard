# P8 results

Every number below is printed by `experiments/make_tables.py` from
`results/*.json`. Nothing is typed by hand. Gate verdicts come from
`results/closure_decision.json`, computed by `experiments/derive_closure.py`,
which runs no simulation.

**Headline, in one paragraph.** The recursive re-baselining phenomenon
**survives** outside the frozen Gaussian specialisation: in all 40 eligible
`(detector, family, m in {1,2,3,5})` cells — and in the 8 moment-marginal `t3`
cells reported beside them — the stopped-selection gain `Gamma_A` has a lower
95% bound above `2`, so `rho_c < 1` and full reuse is locally repelling. Its
**magnitude does not**: `rho_c(D,f,1)` ranges over a factor of `2.54` across the
twelve cells at a matched `ARL_0`. The preregistered window-separability law
`H1` is **rejected** across innovation families (spread `22.7%` to `49.3%`
against a `10%` margin) and is **narrowed** to a cross-detector regularity whose
residual is `<= 3.63%` — about `13x` smaller than the cross-distribution spread,
but still one comparison outside the pre-declared `3%` sub-gate. Three post-hoc
explanations of the failure were frozen while seven cells did not yet exist and
**all three were rejected** by those cells.

---

## 1. What was measured

`4,096,000` independent monitoring cycles per `(detector, family)` cell, 20
addressable batches each, at the frozen operating point `ARL_0 = 465.50394`:
2 detector families x 6 innovation families x 6 windows x 2 window conventions,
plus the lag-selection profile at every lag `r < 20`. Then the repeated-cycle
chain on P7's reuse ladder, and step and ramp drift.

Thresholds: the six CUSUM thresholds are Stage-D D3's, **byte-identical**, never
recalibrated (gate `G14`). The five non-Gaussian SR thresholds are P8's own and
are the campaign's only new constants (`NEW_P8_CALIBRATION`, gate `G2`).

## 2. Reproduction of the priorities P8 depends on

`G1a` — P3 (`CLOSED`), Gaussian `GammaTilde`, both detectors, `m in {1,2,3,5}`:
8 of 8 cells within `|z| <= 3`.
`G1b` — P4 (`PARTIAL`), `m = 1` CUSUM `Gamma_f`, all six families: 6 of 6 within
`|z| <= 3`, the largest being `|z| = 1.55`.
`G1c` — the achieved `ARL_0` at the frozen CUSUM thresholds is within `0.1%` of
the frozen target in every family.
`G1d` — `E[eps psi(eps)] = 1` to `7.9e-6`, `E[psi(eps)] = 0` exactly, and the
Fisher information reproduces Stage-D's independently computed `E[psi']` to
`1.5e-8`, in all six families.
`G1e` — P8's independently written `psi` agrees with P4's frozen
`location_score` to `8.9e-16` and its `logpdf` with P4's `log_density` exactly.

**One systematic offset, independently confirmed.** P8's Gaussian SR gain sits
below P3's at *every* window, all four `z` values between `-1.75` and `-2.07`,
all four relative differences between `-0.70%` and `-0.80%`. That is the same
sign and magnitude P7 recorded and sharpened at P3's own sample size
(`p7/results/sr_gain_check.json`), and P8 — a third implementation on an
independent primitive field — **agrees with P7**, not with P3:

| `m` | P3 | P7 | P8 | `z(P8, P3)` | `z(P8, P7)` |
|---:|---:|---:|---:|---:|---:|
| 1 | 17.4536 | 17.2990 | 17.3266 | `-1.88` | `+0.67` |
| 2 | 14.5005 | 14.3752 | 14.3991 | `-1.75` | `+0.72` |
| 3 | 12.9727 | 12.8481 | 12.8683 | `-2.07` | `+0.66` |
| 5 | 11.0485 | 10.9423 | 10.9634 | `-2.03` | `+0.86` |

`G1a` passes because every `|z|` is under `3`, but the consistency of the sign
across four windows and two independent campaigns is not noise. **P8 does not
own the P3 numbers and does not resolve this**, exactly as P7 did not. It is
recorded in `results/cross_priority_consistency.json` for whoever does. Nothing
in P8 depends on it: `rho_c` shifts by under `0.9%` and every P8 effect is
`22%` or larger.

## 3. A cross-priority disagreement that turns out to be definitional

P4 reports `Gamma_f = 8.71` for `t3` at `m = 1`, CUSUM, threshold
`6.337011391962933`. Stage-D D3 reports `Gamma_psi = 2.598` for the same family,
window and threshold — a factor of `3.35`. Similar gaps appear at `t5` (`1.86x`)
and both contaminated families (`2.7x`, `3.6x`).

P8 measures **three** estimands on its own field in one pass
(`results/cross_priority_consistency.json`):

| family | P8 `Gamma_A` | P4 `Gamma_f` | z | P8 `Gamma_psipsi` | Stage-D `Gamma_psi` | z | wrong-score inflation |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gaussian` | 15.8853 | 15.9375 | -0.89 | 15.8853 | 15.8671 | +0.43 | 1.00x |
| `t10` | 15.4284 | 15.5459 | -1.52 | 11.9807 | 11.9938 | -0.33 | 1.29x |
| `t5` | 13.2351 | 13.3638 | -0.77 | 7.2608 | 7.1890 | +2.07 | 2.56x |
| `t3` | 8.5124 | 8.7101 | -0.41 | 2.6117 | 2.5980 | +0.47 | 11.66x |
| `contam0.05` | 15.6036 | 15.3817 | +1.43 | 5.7666 | 5.7572 | +0.34 | 3.01x |
| `contam0.1` | 18.1261 | 18.3196 | -1.55 | 5.0706 | 5.0474 | +1.03 | 3.27x |

All twelve comparisons agree within `|z| <= 2.1`. **The published gap is
entirely definitional**: P4 weights the *raw* convention-A window by the family
score sum; Stage-D weights the *score-transformed* window by the same sum. They
are the multipliers of two different reuse rules.

**Which one is the frozen reference map's derivative?** `Gamma_A`. The frozen
update is `e_{j+1} = rho (e_j + zbar^A_m) + (1-rho) mu_fresh` with `zbar^A_m` a
**raw** mean (`P8-L0`; P5's `T1` for the Gaussian case), so the multiplier is
`rho(1 - Gamma_A)`. `Gamma_psi` is the multiplier of a score-transformed reuse
rule that no ReBaseGuard artifact implements.

**P8 adjudicates neither artifact and edits neither.** Stage D remains
`STAGE-D-PARTIAL`; P4 remains `LOCATION-FAMILY-THEOREM-PARTIAL`.

The last column is a result in its own right: **using the Gaussian score on
non-Gaussian data overstates the gain by up to `11.7x`**. A misspecification
study of this phenomenon that keeps `T_tau = sum z_t` as the score is not
approximately right; it is wrong by an order of magnitude at `t3` and by a
factor of three under `10%` contamination.

## 4. The phenomenon survives — gate `G3` PASS

In every one of the 40 eligible `(D, f, m in {1,2,3,5})` cells the lower 95%
bound of `Gamma_A` exceeds `2`, so by P3's boundary theorem `rho_c < 1`, the
boundary is interior to the admissible domain, and **full reuse is locally
repelling**. The 8 `t3` cells, reported but never counted, also all exceed `2`.

Regime classification (P3's audit table, applied without assuming a regime):
`GAMMA_GT_2` in all 48 cells at `m in {1,2,3,5}`.

**One exception appears at the extrapolated windows.** At `m = 20`, CUSUM with
`t3` innovations gives `Gamma_A = 1.949 +- 0.007`, i.e. regime
`GAMMA_BETWEEN_1_AND_2`, `rho_c = 1.054 > 1`: the boundary leaves the admissible
domain and **every admissible reuse fraction becomes locally attracting**. This
is the only cell in the matrix where that happens. It is at a window P3 does not
support, is labelled `EXTRAPOLATION_BEYOND_P3`, and is **not** gated — but it is
the first cell anywhere in ReBaseGuard where the local instability disappears,
and it is where a follow-up should look.

## 5. The magnitude does not transfer

At `m = 1` and a matched `ARL_0`, `rho_c` ranges from `0.0524` (SR,
`contam0.1`) to `0.1331` (CUSUM, `t3`) — **a factor of 2.54**, with every
interval far narrower than the spread. A `rho_c` computed under Gaussianity is
therefore wrong by up to a factor of about `2.5` under the misspecifications
tested, **and the sign of the error is not uniform**. Against the Gaussian value
at `m = 1`:

| family | CUSUM `rho_c` (Gaussian `0.0672`) | SR `rho_c` (Gaussian `0.0612`) |
|---|---|---|
| `t10` | `0.0693` higher | `0.0608` marginally lower |
| `t5` | `0.0817` higher | `0.0663` higher |
| `t3` | `0.1331` much higher | `0.0930` much higher |
| `contam0.05` | `0.0685` marginally higher | `0.0588` lower |
| `contam0.1` | `0.0584` **lower** | `0.0524` **lower** |

Heavy tails raise the boundary substantially in both detectors, so a
Gaussian-derived limit is conservative there. Ten percent contamination
**lowers** it in both detectors, so a Gaussian-derived limit is optimistic
there — the direction that matters. The remaining cells move by a few percent in
either direction and their sign is not stable across the two detectors.

`Gamma_A` is **not** monotone in tail weight: the `t` families fall below the
Gaussian (`8.51` at `t3` vs `15.89`) while the contaminated families rise above
it (`18.13` at `contam0.1`). Whatever governs the gain, it is not a single
tail-weight index.

## 6. The window-separability law `H1` — gate `G4` FAIL

`K(D,f,m) := rho_c(D,f,m)/rho_c(D,f,1) = (Gamma_A(1)-1)/(Gamma_A(m)-1)`.

| m | mean `K` | min | max | spread (`max/min - 1`) | margin | verdict |
|---:|---:|---:|---:|---:|---:|---|
| 2 | 1.3735 | 1.2146 | 1.4900 | **22.67%** | <= 10% | **FAIL** |
| 3 | 1.6450 | 1.3632 | 1.8542 | **36.02%** | <= 10% | **FAIL** |
| 5 | 2.0805 | 1.6193 | 2.4175 | **49.29%** | <= 10% | **FAIL** |
| 10 | 3.1203 | — | — | 50.25% | not gated | `EXTRAPOLATION_BEYOND_P3` |
| 20 | 5.5405 | — | — | 42.94% | not gated | `EXTRAPOLATION_BEYOND_P3` |

**`H1` is REJECTED across innovation families.** This is the preregistered
`NARROWED`/`REJECTED` wording of `EXPERIMENT_PROTOCOL.md` §10, not a softening.

Decomposed onto the two axes:

* **`G4-F` (distribution invariance, within a detector) — FAIL.** The spread is
  `22.3% / 34.9% / 47.3%` at `m = 2/3/5` under CUSUM and `22.3% / 34.8% / 47.5%`
  under SR. The two detectors fail *identically*, which is itself informative.
* **`G4-D` (detector invariance, within a family) — FAIL by one comparison of
  fifteen.** The largest cross-detector residual is `3.63%`, at `(t5, m = 5)`,
  against a pre-declared `3%` margin. The other fourteen are inside it, and the
  whole residual is at most `3.63%`.

**The narrowed statement P8 can support**, stated with its residual rather than
as a law: *the window scaling of the critical reuse fraction is nearly the same
for the two frozen detectors (residual `<= 3.63%`) and strongly
distribution-dependent (spread `22%` to `49%`)* — a separation of about `13x`
between the two axes. `LIMITATIONS.md` `L3` and `ADVERSARIAL_REVIEW.md` `A14`
record why "the two frozen detectors" is not "detectors".

## 7. Mechanism: the lag-selection profile

`P8-L1(b)` gives the exact decomposition
`Gamma_A(m) = mean_{r<m} gamma_r + R_m` with
`gamma_r = E[Z_{tau-r} 1{r<tau} sum psi(Z_t)]`. Gate `G5` confirms it
numerically in every cell, and gate `G6` confirms that `Gamma_A - Gamma_B` is
exactly the truncation remainder `R_m`. So `K` is fully determined by the
normalised profile `w_r = (gamma_r - 1)/(gamma_0 - 1)`, which P8 measures at
every `r < 20` **independently of any `m` grid**.

`w_1`, the share of the selection effect carried by the observation immediately
before the alarm-causing one:

| family | CUSUM `w_1` | SR `w_1` |
|---|---:|---:|
| `gaussian` | 0.6466 | 0.6414 |
| `t10` | 0.5535 | 0.5447 |
| `t5` | 0.4354 | 0.4111 |
| `contam0.05` | 0.3712 | 0.3553 |
| `contam0.1` | 0.3466 | 0.3423 |
| `t3` | 0.2860 | 0.2421 |

**Every non-Gaussian family concentrates the selection effect on the
alarm-causing observation more than the Gaussian does**, in both detectors, and
`gaussian > t10 > t5 > contam0.05 > contam0.1 > t3` is the same ordering under
both. That is the mechanism behind `G4`'s failure: `K(m) = m / sum_{r<m} w_r`
up to `R_m`, so a family whose profile is more concentrated has a larger `K`.

The reading this supports is that **an alarm driven by a single outlying
observation carries less information about the reference error in the
observations around it** — the selection is concentrated because the alarm is.
P8 states that as an interpretation of a measured profile, not as a mechanism it
has established.

## 8. Three post-hoc explanations, all rejected

`results/posthoc_preregistration_H2.json` was frozen while 7 of the 12 cells did
not exist, naming the visible cells with their SHA-256 digests. It recorded that
the Fisher-information reading and the tail-heaviness reading make **opposite**
predictions for the contaminated families, so at most one could survive.
`results/posthoc_H2_evaluation.json` reports:

| hypothesis | verdict | evidence |
|---|---|---|
| `H2a` the lag profile is detector-invariant to `5%` for `r <= 5` | **REJECTED** | 19 of 30 comparisons pass; largest residual `19.66%`, concentrated on the heavy-tailed families |
| `H2b` `w_1` is monotone decreasing in the Fisher information | **REJECTED** | predicted `contam0.1 > contam0.05 > gaussian > t10 > t5 > t3`; measured `gaussian > t10 > t5 > contam0.05 > contam0.1 > t3` in **both** detectors. The contaminated families have lower Fisher information than the Gaussian and were predicted to have the largest `w_1`; they measure among the smallest |
| `H2c` `K` is a function of `(m, w_1)` alone | **REJECTED** | only one pair qualified and it failed; **zero** cross-family pairs qualified, so the test is weak as well as negative |

None of `H2a`–`H2c` is a closure gate and none enters
`results/closure_decision.json`. **P8 produced no replacement law.** The
falsification of `H2b` does discriminate between the two available readings of
§7: the Fisher-information reading is dead, the tail-heaviness reading is not.

Note the tension `H2a` creates with `G4-D`: the profile is *not* detector
invariant (up to `19.7%` at individual lags) while `K`, which is a
window-average of that profile, *is* invariant to `<= 3.63%`. Averaging over the
window cancels most of the detector difference. P8 records this and does not
explain it.

## 9. Operational degradation survives everywhere — gate `G8` PASS

Repeated-cycle chains at P7's reuse ladder, 2,000 replicates x 70 cycles,
burn-in 20, metrics on the following 50. **Finite-horizon averages, never
stationary quantities** (`LIMITATIONS.md` `L7`).

At full reuse, all 24 `(D, f, m in {1,5})` cells:

| quantity | range across all 24 cells | P7's Gaussian value |
|---|---|---|
| `ARL_0` at `rho = 1`, as a fraction of the same-cell nominal `A_f(0)` | `10.5%` to `29.8%` | `465 -> 48..80`, i.e. `10%`–`17%` |
| reuse-attributable loss vs the **same-`m` fresh control** (`rho = 0`) | `-37.9%` to `-50.7%` | `-39.5%` to `-50.6%` |

The reuse-attributable loss is `-37.9%` to `-43.0%` at `m = 1` and `-44.9%` to
`-50.7%` at `m = 5` in every family — reproducing P7's `-40%` at `m=1` rising to
`-51%` at `m=5`, **in all six innovation families**, to within a few percentage
points.

**This is the campaign's sharpest single contrast.** The local multiplier varies
enormously across families — `Gamma_A(1)` from `8.51` to `20.10`, `rho_c` by a
factor of `2.54` — while the reuse-attributable operational damage is nearly
invariant at `-38%` to `-51%`. `X6` and the rejected candidate `P7-E` say the
derivative of `E[e_1]` does not determine the derivative of `E[M(e_1)]`; P8
supplies an unusually clean empirical illustration of exactly that, across a
model class rather than within one model.

## 10. `rho_c`'s operational status — gate `G7` FAIL (4 of 6), and what that means

P7's pre-committed boundary criterion, applied verbatim per innovation family
(`p7/experiments/make_report.py::boundary_verdict`), with the declared
adaptation for cells whose `4 rho_c` leaves `[0,1]`:

| family | sub-families peaking at the boundary, per metric | verdict | reproduces P7 |
|---|---|---|---|
| `gaussian` | arl 0, ref_mse 0, fap100 0, e_acf1 0 | `LOCAL-MATHEMATICAL, NOT OPERATIONAL` | yes |
| `t10` | arl 1, ref_mse 0, fap100 0, e_acf1 0 | `LOCAL-MATHEMATICAL, NOT OPERATIONAL` | yes |
| `t5` | arl 0, ref_mse 0, fap100 0, e_acf1 0 | `LOCAL-MATHEMATICAL, NOT OPERATIONAL` | yes |
| `t3` | arl 2, ref_mse 0, **fap100 4**, e_acf1 1 | `OPERATIONAL_BOUNDARY` | **no** |
| `contam0.05` | arl 2, ref_mse 0, fap100 0, e_acf1 0 | `OPERATIONAL_BOUNDARY` | **no** |
| `contam0.1` | arl 0, ref_mse 0, fap100 0, e_acf1 0 | `LOCAL-MATHEMATICAL, NOT OPERATIONAL` | yes |

`G7` required the verdict to reproduce in `>= 5` of 6 families. It reproduces in
4. **The gate fails and is reported failed.**

The gate is not, however, the end of the analysis. P7's criterion is a bare
`max` over brackets with **no uncertainty margin**, and P8 applies it at 4
sub-families per family where P7 had 8, so it is far more easily flipped by
Monte Carlo noise. A preregistered-style companion (`EXPERIMENT_PROTOCOL.md` §8:
BH at `q = 0.10` within a secondary metric family) tests one-sided whether the
boundary rate really exceeds the best rate elsewhere, over **all 96**
`(family, sub-family, metric)` comparisons that carry a replicate-level standard
error. Result, reported as `DESCRIPTIVE_ONLY` and changing no gate:

* **Exactly one** of 96 survives BH: `t3`, CUSUM, `m = 5`, `fap100`, at
  `+3.11` standard errors, `p = 9.4e-4`.
* The next-largest is the same sub-family's `arl` at `+2.56` SE, which does
  **not** survive BH.
* `contam0.05`'s two "peaks" — the ones that flipped its verdict — are both
  **well under 1 SE**. Its `OPERATIONAL_BOUNDARY` verdict is a noise artifact of
  a criterion with no error bars.
* The same cell's SR counterpart (`t3`, `sr_m5`, `fap100`) is at `+0.92` SE, so
  the one surviving signal **does not corroborate across detectors**.

The honest reading: **in 23 of 24 sub-cells, and in five of six families, P7's
`LOCAL-MATHEMATICAL, NOT OPERATIONAL` verdict reproduces outside the Gaussian
core.** In one sub-cell — heavy-tailed `t3` innovations, CUSUM, `m = 5` — the
false-alarm probability shows a rate maximum at the `rho_c` bracket that
survives multiplicity correction, does not replicate under SR, and is small in
absolute terms (`0.318` against `0.261` in the next bracket). It is a lead, not
a result, and `G7` fails literally either way.

## 11. Drift patterns — gate `G11` PASS

All 288 declared drift rows are present. 27 are labelled
`INSUFFICIENT_TAIL_EVENTS`, every one of them at `Delta = 2` — the same regime
P6's `S8` records as under-powered in its own campaign, at a comparable budget.

**Step shift, `Delta = 1`, `m = 1`, full reuse.** The failure mode is a tail,
not a slowdown, in every family. CUSUM/`gaussian`: mean `48.9`, **median `7`**
— below the nominal single-cycle delay — `q95 = 250`, `P(delay > 100) = 11.0%`.
P7 reports mean `52.6`, median `7`, `q95 = 275`, `P(>100) = 11.4%` for the same
cell. The pattern holds across all twelve `(D, f)` cells: median `7`–`10`,
`q95` `250`–`357`, `P(>100)` `10.2%`–`13.4%`.

**Loss of discrimination is total, in every family.** With
`R_Delta := E[first post-change cycle] / E[in-control cycle at the same rho]`,
measured against the `E3` post-burn-in in-control ARL (not the drift run's own
pre-change mean, which includes the `e_0 = 0` transient):

| family | `R_Delta`, step `Delta=1`, `m=1`, `rho=0` | same, `rho=1` |
|---|---:|---:|
| `gaussian` | 0.653 / 0.661 | 0.976 / 1.055 |
| `t10` | 0.614 / 0.579 | 1.010 / 0.927 |
| `t5` | 0.486 / 0.532 | 0.762 / 0.814 |
| `t3` | 0.347 / 0.337 | 0.551 / 0.516 |
| `contam0.05` | 0.653 / 0.644 | 1.034 / 0.988 |
| `contam0.1` | 0.693 / 0.650 | 0.891 / 0.982 |

(CUSUM / SR.) The nominal value is `10.35/465 = 0.022`. At full reuse the
shifted cycle is **as long as, or longer than, an in-control cycle** in eight of
the twelve cells — P7 reported `1.06` for the Gaussian `m=1` cell and P8
measures `0.976` (CUSUM) and `1.055` (SR). `t3` retains the most discrimination
(`0.52`–`0.55`), consistent with its weaker feedback.

**A slow ramp is invisible in the first post-change cycle, with or without
reuse.** At `slope = 0.05` per cycle, `m = 1`, `R_Delta` is `0.92`–`1.05` at
**both** `rho = 0` and `rho = 1`, in every family and both detectors.

At `rho = 0` this is structural rather than merely measured: by `P8-L0` the
reference-error recursion under a ramp is
`e_{j+1} = rho(e_j + zbar_j) + (1-rho) mu_fresh - slope`, so at `rho = 0` it
collapses to `e_{j+1} = mu_fresh - slope` — the reference error is **pinned near
`-slope` forever** and the ramp is permanently absorbed, however long it runs.
Pure-fresh re-baselining does not merely delay a slow ramp; it hides it
indefinitely. **That is a property of re-baselining itself, not of reuse**, and
it is the one place where P8's two drift patterns disagree qualitatively about
what `rho` does.

**Scope of the ramp result, stated.** At `rho = 1` the same recursion is a
random walk with drift `-slope`, so the offset *does* accumulate — and P8's
metric, the first post-change cycle, cannot see that. `E4` runs only 4
post-change cycles (`n_cycles = 24`, change at cycle 20), which is enough for a
step and **not** enough to measure ramp accumulation. P8's ramp claim is
therefore confined to the first post-change cycle and to the exact `rho = 0`
argument above; a time-to-detection study over many post-change cycles is not
run and is the obvious follow-up.

## 12. Why P4's `t3` replication gate failed

P4's frozen numerical gate failed for one reason: its two independent Route-B
replications of the `t3` cell differed by `4.605%` against a precommitted `3%`
limit (`location_family/FINAL_REPORT.md` §A). Lean was correctly not authorised
and the priority stands `PARTIAL`.

`E6` runs **12** independent replications of the same `m = 1` CUSUM estimand per
family, `409,600` cycles each, on P8's own field:

| family | mean | obs. sd (12 reps) | mean nominal SE | ratio | rel. sd | median pair | max of 66 pairs | P(one pair > 3%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gaussian` | 15.8722 | 0.0574 | 0.0630 | 0.91x | 0.36% | 0.32% | 1.47% | 0.0% |
| `t10` | 15.4396 | 0.1155 | 0.0912 | 1.27x | 0.75% | 0.84% | 2.26% | 0.0% |
| `t5` | 13.1886 | 0.1514 | 0.1756 | 0.86x | 1.15% | 1.18% | 3.92% | 7.6% |
| **`t3`** | 8.6718 | 0.5661 | 0.4534 | 1.25x | **6.53%** | **7.60%** | 24.32% | **80.3%** |
| `contam0.05` | 15.5359 | 0.1580 | 0.1626 | 0.97x | 1.02% | 1.18% | 3.22% | 4.5% |
| `contam0.1` | 18.0951 | 0.1280 | 0.1541 | 0.83x | 0.71% | 0.54% | 2.91% | 0.0% |

P4 compared exactly **two** replications, so the P4-comparable statistic is the
last column: the empirical probability that **one random pair** differs by more
than `3%`.

* At `t3` that probability is **`80.3%`**. The **median** pairwise difference is
  `7.60%` — larger than the `4.605%` P4 observed. A `3%` two-replication
  agreement criterion at that sample size was **more likely to fail than to
  pass**, whatever the theorem's status.
* At every other family it is `7.6%` or less, and at `gaussian`, `t10` and
  `contam0.1` it is zero in 66 pairs.
* The variance-inflation ratios are all near `1` (`0.83x`–`1.27x`), so the
  nominal standard errors are roughly the right *size*; what distinguishes `t3`
  is that its relative sampling spread is `6.53%`, **18x** the Gaussian's
  `0.36%`, with the nominal SE understating it by about `25%`. Both effects push
  the same way.
* P8's own `t3` mean over the 12 replications, `8.672`, agrees with P4's `8.710`
  and with P8's own `E1` estimate `8.512` within their intervals.

**P8 does not adjudicate P4, does not re-open it, and edits nothing in it.**
What P8 can say is narrow and factual: an estimator with this sampling behaviour
fails a `3%` two-replication criterion at this sample size most of the time, so
that particular gate outcome carries little information about the estimand. P4
remains `LOCATION-FAMILY-THEOREM-PARTIAL` and only P4's owners can change that.

The comparability caveat is stored in the artifact: P4's Route B used `240,000`
paths per replication against P8's `409,600`, so P4's per-replication standard
error is about `1.3x` larger than P8's and its single-pair spread correspondingly
wider — which makes the `80.3%` an **under**-estimate of what P4 faced.

## 13. Seed sensitivity — gate `G10` PASS, at its threshold

`E5` repeats the entire `E1` matrix at a different experiment tag *and* a
disjoint batch range, so the two primitive fields are independent rather than
offset. Agreement at `|z| <= 3`: **69 of 72** cells overall (`95.8%`, required
`>= 90%`) and **57 of 60** non-`t3` cells (`95.0%`, required `>= 95%` — exactly
at the threshold).

All three failures are the **same cell**, SR / `gaussian`, which shows a
consistent `+0.30%` to `+0.51%` offset between the two seed families at *every*
window. Since all six windows are measured on the same `4,096,000` cycles, that
is **one** discrepancy at `z ~ 3`–`4`, not six. Across the whole matrix the `z`
values have mean `0.08` and sd `1.26`, i.e. mildly over-dispersed relative to
the nominal `1`, which suggests the batch-means standard error slightly
understates true cell-to-cell variability at the highest-precision cells.

This changes no conclusion — the effects P8 reports are `22%`–`49%`, two orders
of magnitude larger than a `0.4%` offset — but it is a real anomaly, it is not
explained, and it is on the list of things Codex should attack.

## 14. Detector transfer — gate `G9` PASS (reported, not asserted)

`G9` has no threshold by design: it requires the comparison to be reported and
no transfer claim to be made beyond it. The result is unambiguous: **`Gamma_A`
does not transfer between the two frozen detectors.** Zero of 36
`(family, m)` ratios `Gamma_A(cusum)/Gamma_A(sr)` are consistent with `1`; the
largest deviation is `27.6%`. SR exceeds CUSUM in every family, by `9.1%`
(`gaussian`) to `38.1%` (`t3`).

What *is* nearly detector-invariant is the derived quantity `K` (§6), and the
chain metrics: the reuse-attributable ARL loss agrees between detectors to a few
percentage points in every family (§9). A quantity computed for one detector
must not be reused for the other; a *ratio* of that quantity across windows
approximately may be, with the `3.63%` residual attached.

## 15. Gate table and verdict

| gate | what it tests | result |
|---|---|---|
| `G1a` | reproduces P3's `CLOSED` Gaussian `GammaTilde` | **PASS** (8/8) |
| `G1b` | reproduces P4's `m=1` `Gamma_f`, six families | **PASS** (6/6) |
| `G1c` | `ARL_0` at the frozen CUSUM thresholds | **PASS** (6/6, `<= 0.1%`) |
| `G1d` | exact regularity identities | **PASS** |
| `G1e` | family implementation vs P4's frozen module | **PASS** (`<= 8.9e-16`) |
| `G2` | P8's SR calibration hits the frozen target | **PASS** (max `0.44%` vs `0.5%`) |
| `G3` | regime survival, `Gamma_A` lower bound `> 2` | **PASS** (40/40 eligible; 8/8 `t3` too) |
| `G4` | **window-separability law `H1`** | **FAIL** (spread 22.7/36.0/49.3% vs 10%) |
| `G4-D` | detector invariance of `K` | **FAIL** (3.63% vs 3%, 14/15 inside) |
| `G4-F` | distribution invariance of `K` | **FAIL** (22–47% vs 10%) |
| `G5` | the `P8-L1(b)` decomposition identity | **PASS** (max residual `7.2e-16`) |
| `G6` | convention A/B semantics | **PASS** (max identity error `3.8e-15`) |
| `G7` | **P7's boundary verdict transfers** | **FAIL** (4/6 vs required 5/6) |
| `G8` | operational degradation survives | **PASS** (24/24) |
| `G9` | detector transfer reported, not asserted | **PASS** |
| `G10` | independent seed family | **PASS** (69/72; 57/60 non-`t3`) |
| `G11` | drift-pattern coverage and tail labelling | **PASS** (288/288) |
| `G12` | protected-tree integrity | **PASS** (24 trees, 0 differences) |
| `G13` | CRN primitive identity | **PASS** (18 tests) |
| `G14` | no hidden recalibration | **PASS** (12 + 24 artifacts byte-checked) |
| `G15` | focused test suite | **PASS** (126 tests) |

**17 of 21 gates pass.** The four failures — `G4`, `G4-D`, `G4-F`, `G7` — are
exactly the preregistered scientific hypotheses, and every one of them is
reported as failed rather than re-thresholded. The whole correctness,
reproduction and integrity spine passes.

```text
P8 = PARTIAL_CANDIDATE
```

**Candidate only.** This verdict was produced by the agent that designed the
experiments, wrote the gates and ran the code. It is not authoritative and must
not be promoted to `CLOSED` without independent adjudication.
