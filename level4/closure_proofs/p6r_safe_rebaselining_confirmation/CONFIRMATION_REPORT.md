# P6R confirmation report

```text
PRECOMMIT ANCHOR   = fcc1355715426531c431e9390c9f12d1bad9b97c   (committed AND pushed
                     to origin/main before any confirmation EVAL ran)
SEED FAMILIES      = TUNE (selection + calibration only) / EVAL (reported) / REPLAY
FIRST-PARTY VERDICT= P6 = CLOSED, on the literal twelve conditions of
                     REPAIRED_PROTOCOL.md section 11
INDEPENDENT STATUS = NOT ADJUDICATED.  The next independent reviewer owns closure.
```

Every interval below is a **10,000-resample BCa** interval with a
**normal-approximation** interval beside it; every ratio is bootstrapped **as a
ratio over replicate pairs**; every declared family carries **BH-adjusted**
p-values at `q = 0.10`; every tail estimate is gated on the **200-event floor**.

---

## 1. The repaired baseline — what changed, and why it matters

Rule **S1**, TUNE only, on the frozen `0.01`-spaced grid, was run before the
anchor and written to `precommit/baseline_selection.json`:

| cell | `rho*_TUNE` (S1) | unsmoothed argmin | `Arl0` argmax | `Rms` argmin | original P6 `B2*` (EVAL-selected) |
|---|---|---|---|---|---|
| **CUSUM m=3** | **0.20** | 0.22 | 0.20 | 0.20 | 0.15 |
| CUSUM m=1 | 0.24 | 0.20 | 0.27 | 0.29 | 0.15 |
| CUSUM m=2 | 0.19 | 0.17 | 0.21 | 0.23 | 0.25 |
| CUSUM m=5 | 0.17 | 0.18 | 0.17 | 0.18 | 0.15 |
| SR m=1 | 0.22 | 0.13 | 0.26 | 0.30 | 0.20 |
| SR m=2 | 0.21 | 0.20 | 0.22 | 0.23 | 0.20 |
| SR m=3 | 0.23 | 0.23 | 0.18 | 0.21 | 0.20 |
| SR m=5 | 0.19 | 0.19 | 0.16 | 0.17 | 0.25 |

**Defect B1 was material.** Rule S1 selects a different `rho` from the original
EVAL-selected `B2*` in **all eight** cells. That is the defect made visible: the
original value was chosen as the grid member minimising the objective *on the
evaluation sample*, so of course it looks best on that sample — that is the
selection bias, not evidence about the population. The repaired control is
chosen without ever seeing the evaluation data.

Two honest calibrations of what the repair does to the headline, neither of
which is "the new bar is harder on the old sample":

* the measured SAW-M advantage at the primary cell against the repaired control
  is `-12.92%` on `Dtail(100)`, against `-10.37%` in the original campaign
  versus its EVAL-selected `rho = 0.15`. The repair neither manufactures the
  effect nor destroys it;
* the two P6R controls bracket it: `-12.92%` against `rho = 0.20` and `-16.20%`
  against `rho = 0.25`. The **smaller** of the two is quoted throughout.

The original and repaired numbers come from different replicate streams (the
pairing tag differs), so they are comparable in magnitude, not element by
element.

**The adjudication's value is carried too.** The independent adjudication
identified `rho = 0.25` for the primary cell; rule S1 independently selects
`0.20`. The two differ by half a grid step in a region where the objective is
flat, and the adjudication's own selection rule was not supplied to this
session, so the difference cannot be attributed. **Both are carried as declared
controls**, and every headline below is quoted against `FIXED_TUNE` (`0.20`),
which is the control **less favourable to SAW-M** on the primary objective.

## 2. Primary cell — CUSUM, `m = 3`, `k = 3`, `Delta = 1`, EVAL

Absolute values (`C_acq` = fresh-sample acquisition cost, observations/update):

| arm | `Arl0` | `Rms` | `C_acq` | `C_prop` | `C_quad` | `Wbar` | `Coll` | `Dmean` | `Dmed` | `Dq95` | `Dtail50` | `Dtail100` | events>100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `B3` full reuse | 69.38 | 0.9246 | **0.00** | 0.000 | 0.000 | 1.000 | 0.016 | 65.13 | 9 | 337 | 0.2115 | 0.1429 | 8,573 |
| `B0` fresh-only | 131.81 | 0.5755 | 3.00 | 3.000 | 3.000 | 0.000 | 0.276 | 41.68 | 9 | 186 | 0.1334 | 0.0832 | 4,990 |
| `FIXED_TUNE` `rho=0.20` | 145.11 | 0.5133 | 3.00 | 2.400 | 1.920 | 0.200 | 0.287 | 36.22 | 9 | 147 | 0.1187 | 0.0689 | 4,134 |
| `FIXED_ADJ` `rho=0.25` | 143.03 | 0.5158 | 3.00 | 2.250 | 1.688 | 0.250 | 0.277 | 36.85 | 9 | 154 | 0.1199 | 0.0716 | 4,296 |
| **`SAW_M`** | **151.54** | **0.4908** | 3.00 | 2.259 | 1.737 | 0.247 | 0.298 | **33.20** | 9 | **125** | **0.1058** | **0.0600** | 3,600 |

Paired effects, SAW-M against **`FIXED_TUNE` (`rho = 0.20`)**:

| metric | relative | BCa 95% | normal 95% | p (BH-adj) | verdict |
|---|---|---|---|---|---|
| **`Dtail(100)`** (primary) | **-12.92%** | `[-16.55%, -9.08%]` | `[-16.65%, -9.18%]` | 0.00013 | **PRACTICALLY_MATERIAL** |
| `Dq95` | -14.97% | `[-20.00%, -10.34%]` | `[-19.82%, -10.12%]` | 0.00012 | PRACTICALLY_MATERIAL |
| `Dtail(50)` | -10.91% | `[-13.68%, -8.11%]` | `[-13.70%, -8.12%]` | 0.00012 | PRACTICALLY_MATERIAL |
| `Dmean` | -8.32% | `[-11.53%, -4.93%]` | `[-11.64%, -5.00%]` | 0.00012 | STATISTICALLY_RESOLVED |
| `Dmed` | 0.00% (both `9`) | `[0, 0]` | `[0, 0]` | 1.00000 | INCONCLUSIVE |
| `Arl0` | +4.43% | `[+3.85%, +5.03%]` | `[+3.84%, +5.02%]` | 0.00012 | STATISTICALLY_RESOLVED |
| `Fap(100)` | -2.45% | `[-2.69%, -2.22%]` | `[-2.69%, -2.22%]` | 0.00012 | STATISTICALLY_RESOLVED |
| `Rms` | -4.39% | `[-4.60%, -4.17%]` | `[-4.61%, -4.18%]` | 0.00012 | STATISTICALLY_RESOLVED |
| `Mad` | -4.86% | `[-5.08%, -4.63%]` | — | 0.00012 | STATISTICALLY_RESOLVED |
| `Q95e` | -4.07% | `[-4.36%, -3.77%]` | — | 0.00012 | STATISTICALLY_RESOLVED |
| `Tail(1.0)` | -16.68% | `[-17.91%, -15.43%]` | — | 0.00012 | PRACTICALLY_MATERIAL |
| `OutCal(0.25)` | -3.76% | `[-4.02%, -3.49%]` | — | 0.00012 | STATISTICALLY_RESOLVED |
| `Rdelta` | -12.21% | `[-15.29%, -9.00%]` | `[-15.37%, -9.06%]` | 0.00012 | PRACTICALLY_MATERIAL |
| **one-step `G`** | **+9.09%** | `[+9.06%, +9.12%]` | `[+9.06%, +9.12%]` | 0.00012 | STATISTICALLY_RESOLVED |
| `Coll` | +3.76% | `[-2.41%, +10.52%]` | `[-2.72%, +10.23%]` | 0.26568 | INCONCLUSIVE |
| **`C_acq`** | **0.00%** | `[0, 0]` | `[0, 0]` | 1.00000 | **identical, exactly** |

Against **`FIXED_ADJ` (`rho = 0.25`)** the effects are larger, not smaller:
`Dtail(100)` `-16.20%` `[-19.78%, -12.61%]`, `Dq95` `-18.83%`, `Arl0` `+5.95%`,
`Rms` `-4.85%`. The headline is quoted against the weaker of the two effects.

**BH family F1**: 14 tests at `q = 0.10`, **12 reject**. The two that do not are
`Dmed` (identically `9` in both arms) and `Coll` (`p_adj = 0.266`). No test was
excluded for insufficient tail events at this cell.

## 3. Cost — what the data actually support *(repairs Q2)*

The **primary** metric is the fresh-sample **acquisition** cost
`C_acq = k_j 1{rho_j < 1}`: newly acquired observations per update.

> **Permitted claim, and the only one made:** SAW-M and both fixed-`rho`
> controls require the **same number of newly acquired fresh samples per
> update** — `3.00` versus `3.00` versus `3.00`, a paired relative difference of
> exactly `0.0000` with a degenerate interval, in **every one of the eight
> replication cells**.

The two declared sensitivities do **not** point the same way against the two
controls, and this is reported rather than resolved in SAW-M's favour:

| sensitivity | vs `FIXED_TUNE` (`0.20`) | vs `FIXED_ADJ` (`0.25`) |
|---|---|---|
| `C_prop = (1-rho)k` | **-5.88%** `[-5.91%, -5.85%]` (SAW lower) | **+0.40%** `[+0.36%, +0.43%]` (SAW **higher**) |
| `C_quad = (1-rho)^2 k` | **-9.56%** `[-9.61%, -9.50%]` (SAW lower) | **+2.90%** `[+2.84%, +2.97%]` (SAW **higher**) |
| `Wbar` (algebraic reuse) | **+23.52%** (SAW reuses more) | **-1.19%** (SAW reuses **less**) |

> **Therefore the claims "SAW reuses more", "SAW is cheaper" and "SAW has a
> lower effective fresh contribution cost" are NOT made.** They hold against the
> `rho = 0.20` control and fail against the `rho = 0.25` control. The original
> campaign's "+64.8% Wbar / -11.4% cheaper" headline was an artifact of the
> EVAL-selected `rho = 0.15` baseline and does not survive the repair.

Across the eight replication cells, measured against each cell's own
`rho*_TUNE`: `C_acq` identical in all eight; `Wbar` higher in all eight
(`+10.4%` to `+62.8%`); `C_prop` lower in all eight (`-2.7%` to `-17.7%`). That
is a statement about the `rho*_TUNE` controls specifically, not a general one.

## 4. The one-step risk — direct evidence for fixed-`k` T6-C *(repairs Q8)*

Formula precommitted in `REPAIRED_PROTOCOL.md` section 9 and
`onestep.py` before the anchor. No binning, no plug-in reference, no
`sigma(V_hat)` restriction: the realized `U^2` only.

At the primary cell, `nu = 1/3`, 8,000 replicate clusters, 680,000 cycles:

| chain the cycles come from | `M2` realized | best constant `rho_0*` | `R_star` | `R_adapt` | **`G`** | BCa 95% |
|---|---|---|---|---|---|---|
| SAW-M's own | 1.3264 | 0.2008 | 0.26639 | 0.24218 | **+9.089%** | `[+9.058%, +9.121%]` |
| `FIXED_TUNE`'s (SAW-M's rule applied) | 1.2891 | 0.2054 | 0.26485 | 0.24014 | **+9.330%** | `[+9.297%, +9.362%]` |
| `FIXED_ADJ`'s (SAW-M's rule applied) | — | — | — | — | **+9.353%** | `[+9.321%, +9.385%]` |

**Null calibration.** The same statistic applied to each *constant* policy's own
weights returns `-0.018%` for `rho = 0.20` and `-1.189%` for `rho = 0.25` —
non-positive by construction, and exactly the loss from using a fixed weight
rather than the sample-optimal constant `0.2054`. The statistic isolates
adaptivity and returns zero when there is none.

**Two limits, stated:** `R_adapt` uses the **plug-in** weights, so `G` is a
**lower bound** on the achievable gap and **the plug-in is not the oracle
`F`-measurable optimizer**. And `G` is a one-step, latent-layer quantity: no
monitoring consequence is inferred from it — the monitoring metrics are measured
separately, above.

**Recorded deviation.** The protocol declared the secondary reading as SAW-M's
rule evaluated on the baseline chain's cycles. The Checkpoint-A code computed
something weaker — the control's *own* gain, which is zero by construction. The
declared quantity was computed afterwards, in `onestep_cross.py`, with the
formula unchanged; the module records that it is post-anchor. An adjudicator
should note that the corrected value (`+9.33%`) is *more* favourable than the
uninterpretable one it replaced and was computed after the primary results were
seen. The primary reading (`+9.089%`, on SAW-M's own chain) is unaffected and
was computed by the Checkpoint-A code.

The original `sigma(V_hat)`-restricted diagnostic is retained in the historical
namespace and is **labelled restricted**: it estimated `E[U^2 | V_hat]`, i.e.
the plug-in's calibration, not the achievable gap.

### 4a. A recorded artifact defect: undefined ratios against degenerate controls

Two reference arms have structurally **zero denominators** for some metrics:
`B3` (full reuse) acquires nothing, so `C_acq = C_prop = C_quad = 0`; `B0`
(fresh-only) reuses nothing, so `Wbar = 0`. A relative effect against a zero
denominator is **undefined**, and the Checkpoint-A analysis code labels it from
its non-finite bootstrap like any other effect, producing a meaningless
`PRACTICALLY_MATERIAL` verdict in the raw JSON.

Rather than edit anchored code after seeing results, every such entry is
enumerated in `results/p6r_undefined_ratios.json` — **52 in EVAL, 4 in
REPLAY**, all against `B3` or `B0`, all on the four cost/reuse metrics. A test
asserts the enumeration is complete, that none of them enters any BH family,
and that every cost comparison this report actually claims uses a
non-degenerate control. **They must be read as `UNDEFINED_ZERO_DENOMINATOR`.**

## 5. Replication — separately calibrated across detectors and windows

**Not "detector transfer".** Each detector is calibrated separately and each
cell's baseline is selected separately on TUNE; no no-recalibration transfer
experiment was run.

BH family **F2**, `Dtail(100)` against each cell's own `rho*_TUNE`, `q = 0.10`:

| cell | `rho*_TUNE` | `Dtail(100)` rel | BCa 95% | `p_adj` | reject | `Arl0` rel | `Rms` rel |
|---|---|---|---|---|---|---|---|
| **P** CUSUM m=3 | 0.20 | -12.92% | `[-16.55%, -9.08%]` | 0.00013 | yes | +4.43% | -4.39% |
| RC1 SR m=3 | 0.23 | -9.53% | `[-13.40%, -5.35%]` | 0.00013 | yes | +5.59% | -4.46% |
| RC2 CUSUM m=1 | 0.24 | -5.19% | `[-8.11%, -1.92%]` | 0.00240 | yes | +10.57% | -7.90% |
| RC2 CUSUM m=2 | 0.19 | -10.13% | `[-13.40%, -6.69%]` | 0.00013 | yes | +6.82% | -6.07% |
| RC2 CUSUM m=5 | 0.17 | -7.62% | `[-12.78%, -2.16%]` | 0.00850 | yes | +2.70% | -2.79% |
| RC2 SR m=1 | 0.22 | -8.15% | `[-11.16%, -5.02%]` | 0.00013 | yes | +11.50% | -8.55% |
| RC2 SR m=2 | 0.21 | -9.94% | `[-13.30%, -6.45%]` | 0.00013 | yes | +6.81% | -5.86% |
| RC2 SR m=5 | 0.19 | -14.56% | `[-19.68%, -8.83%]` | 0.00013 | yes | +2.76% | -2.85% |

**8 of 8 reject** after BH correction. `Arl0` and `Rms` are resolved in all
eight. Acquisition cost is identical in all eight.

## 6. Independent seed family (REPLAY)

The primary cell was re-run on `REPLAY` using the **same** `rho*_TUNE = 0.20`;
the baseline was **not** re-selected.

| metric | EVAL | REPLAY |
|---|---|---|
| `Dtail(100)` | -12.92% `[-16.55%, -9.08%]` | **-10.47%** `[-14.21%, -6.65%]` |
| `Dq95` | -14.97% `[-20.00%, -10.34%]` | -12.16% `[-17.45%, -7.62%]` |
| `Dtail(50)` | -10.91% | -6.65% `[-9.66%, -3.66%]` |
| `Dmean` | -8.32% | -5.66% `[-8.84%, -2.35%]` |
| `Arl0` | +4.43% | +4.61% `[+4.04%, +5.20%]` |
| `Rms` | -4.39% | -4.43% `[-4.65%, -4.22%]` |
| `Fap(100)` | -2.45% | -2.55% |
| `Rdelta` | -12.21% | -9.81% |
| one-step `G` | +9.089% | +9.099% |
| `C_acq` | 0.00% | 0.00% |
| `Coll` | +3.76% INCONCLUSIVE | +2.28% INCONCLUSIVE |

Family F1 on REPLAY: 14 tests, **12 reject**, the same two failing to reject
(`Dmed`, `Coll`).

## 7. `Delta` scope *(repairs Q4, Q5)*

| `Delta` | metric | result | status |
|---|---|---|---|
| **0.5** | `Dtail(100)` | -0.23% `[-2.25%, +1.91%]` | **INCONCLUSIVE** |
| | `Dq95` | -1.04% `[-3.89%, +2.12%]` | INCONCLUSIVE |
| | `Dmean` | -0.53% `[-2.86%, +1.82%]` | INCONCLUSIVE |
| | `Rdelta` | -4.75% | STATISTICALLY_RESOLVED |
| **2** | `Dtail(100)` | 24 and 35 events, floor is 200 | **INSUFFICIENT_TAIL_EVENTS** — excluded from F3, carries no claim |
| | `Dq95` (declared fallback) | 0.00% `[-10.00%, 0.00%]` | INCONCLUSIVE |
| | `Dmean` | -2.05% `[-3.81%, -0.26%]` | STATISTICALLY_RESOLVED |

BH family **F3**: 3 tests after excluding the sub-floor cell; **none rejects**.

> **`Delta = 0.5` is reported as the predeclared limitation, not as a failure to
> optimise away.** SAW-M was not altered to target it; its four constants are the
> frozen P6 constants, fitted at `Delta = 0`. The confirmation reproduces what
> the original campaign found: **no coherent aggregate adaptive advantage at
> `Delta = 0.5`**. The discrimination ratio does move (`-4.75%`), which is
> consistent with the in-control gain rather than with a delay-tail gain.
>
> **No sample size was increased after inspecting any result.** Resolving
> `Delta = 2` at the tail would need a separately preregistered power-extension
> campaign, which was not run.

## 8. Post-burn-in robustness to alternative initialization *(repairs Q7)*

**Not "full initialization robustness".** `e_0 ~ N(0, 1/m_0)`, primary cell,
post-burn-in comparison; BH family **F4**, `q = 0.10`:

| `m_0` | `Dtail(100)` rel | `p_adj` | reject | `Arl0` rel | `Rms` rel | `Dq95` rel |
|---|---|---|---|---|---|---|
| 20 | -8.80% | 0.00010 | yes | +5.20% | -4.53% | -10.67% |
| 50 | -11.41% | 0.00010 | yes | +5.23% | -4.53% | -12.72% |
| 100 | -10.39% | 0.00010 | yes | +5.06% | -4.50% | -10.88% |

**3 of 3 reject.** Cycle-1 behaviour, reported separately as descriptive
evidence and not as part of any claim: mean `tau_1` is `259.2 / 336.1 / 376.1`
for SAW-M against `259.9 / 321.6 / 374.3` for the baseline at
`m_0 = 20 / 50 / 100`. `Coll` shifts across regimes because its *denominator*
changes with `e_0`; the two regimes' `Coll` values are not comparable.

## 9. Calibration diagnostics *(repairs Q3)* — reported, not softened

The constants are **not re-derived**; they are the adjudicated object, audited.

| cell | converged | iterations | obs behind `s1` | `s1` is `s0` fallback | floor `1e-2` active | max relative move under the `s1` sensitivity (`rho_mean` / `Rms` / `Arl0`) |
|---|---|---|---|---|---|---|
| CUSUM m=1 | yes | 3 | **0** | yes | no | 0.19% / 0.32% / 0.75% |
| CUSUM m=2 | **NO** | 6 | **3** | no | no | 0.32% / 0.64% / 0.88% |
| **CUSUM m=3** | yes | 2 | 262 | no | no | 0.55% / 0.34% / 1.96% |
| CUSUM m=5 | yes | 6 | 3,653 | no | no | 0.66% / 0.44% / 1.06% |
| SR m=1 | yes | 3 | **0** | yes | no | 0.13% / 0.37% / 1.56% |
| SR m=2 | yes | 3 | **0** | yes | no | 0.60% / 0.96% / **3.73%** |
| SR m=3 | **NO** | 6 | **20** | no | no | 0.09% / 0.14% / 0.52% |
| SR m=5 | yes | 2 | 1,061 | no | no | 0.33% / 0.61% / 0.27% |

* **"All cells converged" is false and is not claimed.** `cusum_m2` and `sr_m3`
  did not converge within the iteration budget.
* The `1e-2` variance floor is **inactive everywhere**; the `rho_max = 0.95` cap
  **cannot bind** in any cell.
* **The final large-pass refit was NOT followed by another fixed-point update.**
  The shipped constants are a refit under the policy built from the fixed-point
  iterate, not a verified fixed point of themselves. The recorded drift measures
  that one-step-off gap: `|dg0| <= 0.0028`, `|dg1| <= 0.019`, `|ds0| <= 0.0007`,
  and `|ds1|` up to `22.7` at `cusum_m2`.
* The predeclared sensitivity was run for **every** cell, not only the sparse
  ones, so primary-cell stability cannot be used to excuse a secondary cell.
  Perturbing `s1` to `0.5x`, `2x` and `s0` moves mean `rho` by at most `0.66%`,
  `Rms` by `0.96%` and `Arl0` by `3.73%` (`sr_m2`, whose `s1` is a pure `s0`
  fallback and therefore has no truncated-window content at all).

## 10. Novelty *(repairs Q9)*

```text
Algorithmic novelty  = NOT ESTABLISHED
Theoretical novelty  = NOT ESTABLISHED
Formulation novelty  = PLAUSIBLE
Integration novelty  = PLAUSIBLE
```

Unchanged from `NOVELTY_SCOPE.md`. No line is upgraded; P6R ran no new
literature audit. The only positive statement made is that **no direct prior
formulation has yet been identified** for the exact repeated post-alarm
terminal-window reuse + fresh-sample acquisition + recursive reference-state
setting — a statement about what one sitting of search did not find, and weak
evidence of absence. The inverse-variance rule, the Jensen argument and the
Doeblin technique are **not** claimed novel.

## 11. Closure rule — the twelve conditions, audited

| # | condition | verdict | evidence |
|---|---|---|---|
| 1 | T6-B remains valid | **HOLDS** | `EXACT_VALID`, unchanged. Its policy class is now pinned field-by-field, and `test_p6r_method_identity.py` asserts SAW-M satisfies it: no decision moves when any of the eight excluded fields is perturbed, in all 8 cells |
| 2 | fixed-`k` T6-C remains valid | **HOLDS** | stated for fixed `k` only; `test_fixed_k_throughout_so_T6C_applies` asserts every cell uses a single `k`. No adaptive-`k` theorem is asserted |
| 3 | SAW-M observable and memoryless | **HOLDS** | asserted structurally; `rho < rho_max` strictly and `rho > 0` in all 8 cells |
| 4 | baseline selected exclusively on TUNE | **HOLDS** | rule S1 in `precommit/baseline_selection.json`, frozen at the anchor; `test_baseline_selection_used_tune_only` asserts `family == "tune"` for every cell |
| 5 | repaired EVAL preserves the primary effect | **HOLDS** | `Dtail(100)` `-12.92%` `[-16.55%, -9.08%]` against the harder TUNE-selected control; 8/8 replication cells reject after BH; REPLAY reproduces at `-10.47%` |
| 6 | preregistered statistical analysis actually executed | **HOLDS** | exactly 10,000 resamples, BCa with a real jackknife, normal intervals beside every BCa, ratios bootstrapped as ratios, BH over four declared families, 200-event floor — each asserted by test to *run*. One declared secondary statistic was implemented incorrectly at the anchor and corrected afterwards; see section 4 |
| 7 | no claim relies on sub-floor tail counts | **HOLDS** | `Dtail(100)` at `Delta = 2` (24 and 35 events) is labelled `INSUFFICIENT_TAIL_EVENTS`, excluded from family F3, and carries no claim |
| 8 | `Delta = 0.5` honestly scoped as a limitation | **HOLDS** | measured INCONCLUSIVE on `Dtail(100)`, `Dq95` and `Dmean`; reported as the predeclared limitation; SAW-M unaltered |
| 9 | calibration defects correctly reported | **HOLDS** | section 9; "all converged" is not claimed; 2 non-converged cells named; `s1` counts, floor status and the unverified-fixed-point status all reported |
| 10 | precommit commit predates confirmation EVAL | **HOLDS** | `fcc1355`, committed and **pushed**, with `remote_matches_local = true` recorded in `results/precommit_anchor.json` before the first EVAL run; `confirm_eval.py` refuses to run without it |
| 11 | no protected historical artifact rewritten | **HOLDS** | 121-file hash manifest + two tests; `git diff --name-only HEAD` empty outside the P6 namespaces |
| 12 | documented claims agree with generated artifacts | **HOLDS** | `tests/test_p6r_claims.py` re-derives every number in this report from `results/*.json` |

> **First-party verdict: `P6 = CLOSED`** on the literal twelve conditions.
>
> This is **not** an independent closure. P6R does not adjudicate itself. The
> items an independent reviewer should weigh before accepting it are in
> section 12.

## 12. What an independent reviewer should attack

1. **The post-anchor correction of section 4.** A declared secondary statistic
   was implemented incorrectly in the anchored code and recomputed afterwards,
   with a result more favourable than the one it replaced, after the primary
   results were visible. The primary one-step reading is unaffected, but this is
   the clearest process blemish in P6R.
2. **Rule S1 versus the adjudication's `0.25`.** S1 selects `0.20` at the
   primary cell. The adjudication's selection rule was not supplied, so the
   difference is unexplained. Both controls are reported and the weaker effect
   is quoted, but a reviewer holding the original rule should re-run it.
3. **The smoothing inside S1.** The 5-point moving average is declared and
   defensible on a flat objective, but it is a choice; the unsmoothed argmins
   are recorded and differ by up to `0.09` in `sr_m1`.
4. **The two non-converged calibration cells** (`cusum_m2`, `sr_m3`) and the
   three cells whose `s1` is a pure fallback. The sensitivity says it does not
   matter; the sensitivity is itself a simulation.
5. **The cost story.** `C_acq` equality is exact and is the only claim made, but
   an operator whose cost is proportional or quadratic would read the primary
   cell differently depending on which control is taken as the incumbent.
6. **`Delta = 0.5`.** SAW-M buys nothing there. If small shifts are the
   operationally relevant regime, the result is much narrower than it reads.
7. **The scope of the whole thing.** One frozen Gaussian convention-A model, two
   detectors, one reuse convention. Nothing here is evidence about a real
   process.
