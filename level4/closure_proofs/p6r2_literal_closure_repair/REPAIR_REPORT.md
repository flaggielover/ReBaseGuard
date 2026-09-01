# P6R2 repair report

```text
NATURE            = POST-ADJUDICATION deterministic/statistical repair over FROZEN
                    P6R raw evidence.  Not preregistered before the original P6R
                    EVAL, and not presented as such.
SOURCE P6R HEAD   = 73ecad84620e71b68db60612a7001707a2cbd741  (independently reviewed)
SCOPE             = adjudicated blockers in gates 6, 9 and 12.  Nothing else.
FIRST-PARTY       = GATE_6 PASS / GATE_9 PASS / GATE_12 PASS  -> READY_FOR_INDEPENDENT_REVIEW
                    P6 = CLOSED is NOT declared here; the next reviewer owns it.
```

No simulation of the scientific campaign was rerun. No baseline was reselected,
no sample size increased, no algorithm retuned, no estimand changed. The nine
passing gates are not reopened.

---

## A. What exactly was wrong?

| # | defect | evidence |
|---|---|---|
| **6A** | The **F3 family was not executed literally**. The declaration is "the primary metric at `Delta in {0.5, 2}`", with `Dq95` as the **fallback used only when `Dtail(100)` is sub-floor**. The implementation entered **both** the primary and the fallback at `Delta = 0.5`, where the primary was eligible — an **undeclared extra test** | P6R F3 = `{Dtail100@0.5, Dq95@0.5, Dq95@2.0}`, 3 tests |
| **6B** | The **`Rdelta` BCa acceleration jackknifed only the shorter block**. `Rdelta` is a functional of two independent blocks, so that is not the jackknife of the complete two-sample functional | P6R `accel = +1.6e-05`; the complete two-block value is `+4.2e-04`, **26x larger** |
| **6C / 12** | Ratios with an **exactly-zero denominator** were labelled with finite effect verdicts. **56** such invalid favourable labels (52 EVAL + 4 REPLAY) sat in the authoritative JSON; a downstream enumeration artifact was added, which does not repair a false primary JSON | full reuse has `C_acq = C_prop = C_quad = 0`; fresh-only has `Wbar = 0` |
| **9** | The official `s1` calibration-sensitivity artifact was **confounded**: variants used different `policy_id` values and therefore different RNG streams, so the reported movement mixed the perturbation with Monte Carlo path noise | it reported up to `3.730%` movement in a cell where `s1` **cannot fire at all** |

## B. What was changed?

Four things, all in statistical post-processing and artifacts:

1. **`families.py`** builds F3 by the literal declared rule: the primary metric
   per `Delta`, with the declared fallback substituted **only** when the primary
   is sub-floor. Nothing else may enter.
2. **`twoblock.py`** implements the complete two-sample BCa acceleration for
   `Rdelta`. The **bootstrap estimand is unchanged**; only the acceleration is
   repaired.
3. **`undefined.py` + `effects.py`** guard zero denominators **at the source of
   the pipeline** — no bootstrap is ever started — and emit
   `status = "UNDEFINED_ZERO_DENOMINATOR"`, `verdict = "NO_CLAIM"` with JSON
   `null` for every numeric field.
4. **`fixedpath.py` + `crn_sensitivity.py`** replace the confounded sensitivity
   with a **fixed-path / common-random-number** experiment in which every
   variant sees identical innovations.

## C. What was NOT changed?

SAW-M; its calibration constants; the frozen TUNE-selected `rho` values
(`cusum` 0.24/0.19/**0.20**/0.17, `sr` 0.22/0.21/0.23/0.19); the S1 rule; the
primary estimand; the resample count, BCa method, normal intervals, ratio
resampling, tail floor and BH `q`; the closure thresholds; the twelve gates;
T6-B; T6-C; the novelty wording; historical P6; historical P6R; Stage A-F;
P1-P5. `POST_ANCHOR_CORRECTION` remains a disclosed non-blocking deviation and
is not re-litigated.

**Mechanical proof that nothing else moved:** every defined effect other than
`Rdelta` was recomputed from the frozen arrays and compared with P6R.
**958 of 958 reproduce bit-for-bit; 0 differ** (873 EVAL + 85 REPLAY).

## D. Which frozen artifacts were reused?

`precommit/frozen_inputs.json` hashes **37** files, consumed read-only: the 13
P6R per-replicate `.npz` arrays, 12 scalar JSONs, both P6R analysis JSONs, both
confirmation manifests, the precommit anchor, the P6R undefined enumeration, the
four P6R precommit artifacts (`baseline_selection`, `calibration_audit`,
`s1_sensitivity`, `PRECOMMIT_MANIFEST`), `REPAIRED_PROTOCOL.md`,
`CONFIRMATION_REPORT.md`, and the frozen P6 `calibration.json`. A test verifies
all 37 are byte-identical, and P6R's own 121-file historical manifest still
verifies.

## E. Did primary scientific conclusions change?

**No.** The independently confirmed primary numbers are reproduced exactly:

| metric | P6R | P6R2 |
|---|---|---|
| `Dtail(100)` | -12.9173% | **-12.9173%** |
| `Dq95` | -14.9660% | **-14.9660%** |
| `Dmean` | -8.3210% | **-8.3210%** |
| `Arl0` | +4.4323% | **+4.4323%** |
| `Rms` | -4.3920% | **-4.3920%** |

Replication: **8/8** cells still reject after BH. REPLAY: unchanged.

## F. Did F3 decisions change?

**The membership changed; the decisions did not.**

| | P6R | P6R2 (literal) |
|---|---|---|
| members | `Dtail100@0.5`, **`Dq95@0.5`**, `Dq95@2.0` | `Dtail100@0.5`, `Dq95@2.0` |
| `n_tests` | 3 | **2** |
| excluded | `Dtail100@2.0` (`INSUFFICIENT_TAIL_EVENTS`) | `Dtail100@2.0` (`INSUFFICIENT_TAIL_EVENTS`, 24/35 events vs floor 200) |
| BH-adjusted p | all `1.000` | all `1.000` |
| rejections | **none** | **none** |

Derivation from the raw arrays: at `Delta = 0.5` the primary metric clears the
floor (**13,724 / 13,755** exceedances), so the fallback may not also enter; at
`Delta = 2` it does not (**24 / 35**), so it is excluded and labelled and the
declared fallback takes its place. **The repair removes a test and rejects
nothing new — it cannot and does not make SAW-M look better.**

## G. Did corrected `Rdelta` intervals change interpretation?

**No.** Primary cell, SAW-M vs `FIXED_TUNE`:

| | acceleration | BCa 95% interval | verdict |
|---|---|---|---|
| P6R (one-block shortcut) | `+1.62e-05` | `[-15.2888%, -8.9968%]` | PRACTICALLY_MATERIAL |
| **P6R2 (two-block)** | **`+4.16e-04`** | `[-15.2886%, -8.9963%]` | PRACTICALLY_MATERIAL |

The acceleration is **26x larger** once both blocks contribute, which is the
defect made visible; but because `|a|` is small in absolute terms and the delay
block (`n = 60,000`) dominates the in-control block (`n = 8,000`), the endpoints
move only in the sixth decimal. Across **46** `Rdelta` records in both families,
**zero verdicts flip**. The point estimate is untouched by construction.

Correctness evidence: the closed-form leave-one-out families match literal
brute-force deletion to `<1e-12`; the acceleration matches a from-scratch
recomputation of the multi-sample formula to `<1e-12`; and it **reduces exactly**
to the single-block formula when the other block carries no influence.

## H. Did the common-random-number calibration sensitivity change interpretation?

**The numbers changed materially; the qualitative conclusion survives and is
strengthened.** Under identical stochastic paths the movement attributable to
`s1` is far smaller than the confounded artifact reported, and **exactly zero**
in the four cells where `s1` can never fire.

| cell | converged | obs behind `s1` | `s1` = `s0` fallback | baseline `rho` | `Rms` | `Arl0` | CONFOUNDED max abs rel. `rho`/`Rms`/`Arl0` (%) | **CORRECTED CRN** (%) |
|---|---|---|---|---|---|---|---|---|
| cusum_m1 | true | 0 | true | 0.3561 | 0.7812 | 105.37 | 0.187 / 0.324 / 0.748 | **0.000 / 0.000 / 0.000** |
| cusum_m2 | **false** | 3 | false | 0.2877 | 0.5842 | 132.58 | 0.320 / 0.642 / 0.877 | **0.000 / 0.000 / 0.000** |
| cusum_m3 | true | 262 | false | 0.2478 | 0.4920 | 152.53 | 0.549 / 0.343 / 1.964 | **0.064 / 0.085 / 0.027** |
| cusum_m5 | true | 3653 | false | 0.2027 | 0.3945 | 178.98 | 0.661 / 0.441 / 1.062 | **0.334 / 0.090 / 0.027** |
| sr_m1 | true | 0 | true | 0.3580 | 0.7831 | 100.71 | 0.131 / 0.366 / 1.557 | **0.000 / 0.000 / 0.000** |
| sr_m2 | true | 0 | true | 0.2913 | 0.5833 | 127.97 | 0.602 / 0.958 / 3.730 | **0.000 / 0.000 / 0.000** |
| sr_m3 | **false** | 20 | false | 0.2533 | 0.4914 | 145.53 | 0.087 / 0.140 / 0.519 | **0.012 / 0.026 / 0.016** |
| sr_m5 | true | 1061 | false | 0.2115 | 0.3908 | 171.60 | 0.331 / 0.606 / 0.273 | **0.158 / 0.063 / 0.085** |

`sr_m2` is the clearest demonstration: the confounded artifact attributed
`3.730%` of `Arl0` movement to an `s1` perturbation in a cell where **`s1` is a
pure `s0` fallback and no truncated window exists**, so the true movement is
identically zero. That number was Monte Carlo path noise, not sensitivity.

`cusum_m2` shows `0.000%` despite `s1` having 3 observations behind it in the
original calibration: in this experiment's 90,000 cycles no truncated window
occurred at all, so `s1` never fired.

**Carried forward unchanged and not reinterpreted:** 6/8 cells converged;
**`cusum_m2` and `sr_m3` did not**; the final large-pass refit was **not**
followed by another fixed-point update and is **not a verified fixed point**;
`s1` rests on 0-3,653 observations by cell; the `1e-2` variance floor is
inactive everywhere and `rho_max` cannot bind. **This artifact does not claim to
prove calibration convergence.**

## I. Are all zero-denominator entries now first-class undefined?

**Yes, at the source.** All **56** (52 EVAL + 4 REPLAY) appear in the
regenerated artifacts as

```json
{"status": "UNDEFINED_ZERO_DENOMINATOR", "relative_effect": null,
 "bca_interval": null, "normal_interval": null, "p_value": null,
 "p_adjusted": null, "verdict": "NO_CLAIM"}
```

with JSON `null`, never `NaN` or `Infinity`. No bootstrap is started for them,
none enters any BH family, none receives an adjusted p-value, and none supports
a claim. The artifacts contain no `NaN`/`Infinity` token and parse under strict
JSON with a `parse_constant` trap. They are enumerated in
`results/p6r2_claim_ledger.json` for auditability. The controls involved are
`B3_full_reuse` (zero acquisition cost) and `B0_fresh_only` (zero reuse weight);
the metrics are the three cost accountings and `Wbar`.

## J. Are gates 6, 9 and 12 now literally satisfied?

```text
GATE_6_P6R2  = PASS
GATE_9_P6R2  = PASS
GATE_12_P6R2 = PASS
```

* **G6A** F3 is the literal declared family: 2 tests, the undeclared
  `Dq95@0.5` removed, membership derived from raw event counts, decisions
  unchanged.
* **G6B** `Rdelta` uses the complete two-sample acceleration, verified against
  brute force, with the old shortcut retained side by side so the difference is
  auditable.
* **G6C / G12** zero denominators are first-class undefined at source; all 56
  repaired; strict JSON.
* **G9** the confounded artifact is replaced by a fixed-path CRN analysis with
  path identity asserted per cell.

## Claim ledger

| category | count |
|---|---|
| `SURVIVED_UNCHANGED` | **958** defined effects reproduce P6R bit-for-bit |
| `NUMERICALLY_CORRECTED_BUT_SAME_INTERPRETATION` | **46** `Rdelta` records (0 verdict flips) + the F3 family |
| `DOWNGRADED` | **0** |
| `INVALIDATED` | **58** — the 56 zero-denominator labels, the undeclared F3 member `Dq95@0.5`, and the confounded `s1_sensitivity.json` |
| `UNDEFINED_NO_CLAIM` | **56** |

Full enumeration: `results/p6r2_claim_ledger.json`.

## Limitations, retained

* `Delta = 0.5` is **INCONCLUSIVE** on `Dtail(100)`, `Dq95` and `Dmean`; it
  remains the predeclared limitation and SAW-M was not altered to target it.
* `Delta = 2` is **underpowered at the tail** (24/35 exceedances against a floor
  of 200); `Dtail(100)` carries no claim there and `Dq95` is the fallback. No
  sample size was increased.
* Calibration: **6/8 cells converged**; `cusum_m2` and `sr_m3` did not.
* **Sparse `s1` cells**: 0, 3, 20 observations at `cusum_m1`/`sr_m1`/`sr_m2`,
  `cusum_m2`, `sr_m3` respectively; three are pure `s0` fallbacks.
* The final calibration refit is **not a verified fixed point**.
* **No no-recalibration detector transfer experiment** was run; the evidence is
  separately calibrated replication across CUSUM and SR.
* Finite-reference evidence is **post-burn-in only**.
* **No generic "cheaper" or "reuses more" claim**: the direction flips between
  the `rho = 0.20` and `rho = 0.25` controls. Only exact equality of
  fresh-sample acquisition cost is claimed.
* **Algorithmic novelty NOT ESTABLISHED; theoretical novelty NOT ESTABLISHED**;
  formulation and integration novelty remain `PLAUSIBLE`. Nothing is upgraded.
* One frozen Gaussian convention-A model, two detectors, one reuse convention.
  Nothing here is evidence about a real process.

## First-party verdict

```text
GATE_6_P6R2 = PASS
GATE_9_P6R2 = PASS
GATE_12_P6R2 = PASS

FIRST_PARTY_P6R2_VERDICT = READY_FOR_INDEPENDENT_REVIEW
```

`P6 = CLOSED` is **not** declared here. P6R2 repaired three literal defects over
frozen evidence; whether that clears the campaign is the next independent
reviewer's decision.
