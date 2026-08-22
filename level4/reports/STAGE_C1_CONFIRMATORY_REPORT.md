# ReBaseGuard Level 4 — Stage C.1

## Confirmatory Sensitivity Evaluation

**Decision: `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`**

> **Stage C is unchanged.** Stage C remains `STAGE-C-PARTIAL` because its
> preregistered criterion C6 failed. Stage C.1 is a *separate* experiment
> asking a better-defined question with new seeds. It does not, and
> cannot, make C6 pass.

---

## 1. Motivation

Stage C asked whether the certificate-aware ReBaseGuard policy buys its
in-control stability by blinding the detector. Its criterion C6 compared
**raw** detection delays across policies. That comparison was confounded:
the policies operate at very different in-control points (cycle ARL 85.2
for ReBaseGuard against 50.0 for full reuse, a factor of 1.7), and a
detector that alarms constantly always posts short "delays" whether or
not anything changed.

Stage C.1 asks the same scientific question with a metric that removes
each policy's own baseline alarm rate.

---

## 2. Historical Stage C C6 failure — chronology

1. Stage C preregistered C6 as a **raw** cross-policy detection-delay
   criterion.
2. C6 **failed**, at `Delta = 0.25` and `Delta = 0.5`.
3. C6 **remained failed**; the Stage C decision reflects it and was not
   amended.
4. Post-hoc diagnosis (`CRITERION_C6_DIAGNOSIS.md`) identified the
   confound: raw cross-policy delay is not comparable across policies with
   different in-control operating points.
5. A baseline-normalised response metric was **proposed** in that
   diagnosis, and reported there only as a labelled secondary diagnostic.
6. **Stage C.1 preregistered that metric here, before any new data.**
7. Stage C.1 used entirely new seed families.
8. Stage C.1 reports its own decision, separately, below.

The correct summary is: **Stage C's C6 failed; Stage C.1 independently
tested a better-defined sensitivity question.** Stage C.1 is a separate
experiment, not a repair of C6, and C6's verdict is unchanged by it.

---

## 3. The new preregistered question

> Does the certificate-aware ReBaseGuard policy preserve a meaningful
> response to genuine distribution shifts **relative to its own in-control
> operating regime**, rather than obtaining stability by making alarms
> generally slower?

---

## 4. Frozen protocol

`level4/stage_c1/STAGE_C1_PROTOCOL.md`, sha256 `7b45c091229387e255b285013a4f7d60…`,
frozen and hashed **before** any confirmatory outcome existed. A test
re-hashes the file on every run and fails if it changed.

Policies (fixed, never re-optimised):

| Label | `rho` | Role |
|---|---|---|
| fresh | 0 | non-inferiority **reference** |
| **ReBaseGuard** | `0.02979584394902044` | the Stage C policy under test |
| full reuse | 1 | **diagnostic only** |
| 0.25, 0.30 | exploratory | context only; excluded from the decision |

`rho_RBG` is imported verbatim from the Stage C policy module. A test
asserts that module contains no Stage C.1 identifier or outcome value, so
the policy cannot have been tuned to this experiment.

---

## 5. Primary normalised metric

```text
R_Delta(rho) = E[tau_Delta | rho] / E[tau_0 | rho]
```

`R` near 1 means the shift produces little acceleration relative to that
policy's own in-control alarm rate; smaller `R` means a genuine shift
accelerates detection strongly. **This is not a classical standardised ARL
quantity and is not claimed to be one** — it is a ratio of two
expectations under one policy, and only the relative reading is used.

Estimator, fixed in advance: **ratio of means**, `mean_r(num_r) /
mean_r(den_r)`, with `den_r` from the `Delta = 0` arm of the **same**
policy run with the **same** seed. Uncertainty: percentile bootstrap
resampling **replicates**, never cycles.

---

## 6. Non-inferiority margin

`D_Delta = R_Delta(RBG) - R_Delta(fresh)`, margin **`epsilon = 0.05`**, fixed before any data.

**H-C1 passes when the upper 95% bound of `D_Delta` is strictly below
`epsilon` at every one of the four preregistered shifts.** This is an
intersection–union test, so no multiplicity adjustment is needed; it is
conservative by construction. `epsilon` was not changed after seeing
results.

Secondary descriptive guard: `Q_Delta = E[tau_Delta|RBG] / E[tau_Delta|fresh] <= 1.1`.

---

## 7. Independent-seed design

Every seed used anywhere in the repository was audited before choosing:
`{1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210, 20260820,
20260821, 20260822}`.

| Purpose | Master seed | Used for |
|---|---|---|
| smoke sizing (non-confirmatory) | `20260931` | choosing (N, K) only |
| **confirmatory** | `20260901` | the Stage C.1 result |
| adversarial rerun | `20260902` | independent replication |

**Replicate structure.** Stage C's detection design gave one change event
per replicate, so a per-replicate ratio was impossible there. Stage C.1
uses `K = 400` change events in each of `N = 400` replicates (160,000
events per cell), via the **existing, unmodified** simulator. Spacing
between events is 15 cycles, chosen by measuring
recovery: `|e|` settles within 1 cycle for fresh and ReBaseGuard and
within about 3 for full reuse.

The `(N, K)` rung was selected by a rule recorded **before** the smoke
run: the first rung on a fixed ladder with bootstrap `SE(D_Delta) <= 0.010`
at every shift, then applied identically to every policy and shift.
Replication was never increased for cells close to passing.

> **Stated plainly:** sizing required estimating the very contrast under
> test, so the smoke run necessarily revealed the approximate answer. That
> cannot bias the result, because every degree of freedom — margin, shifts,
> policies, estimator, statistical unit, decision rule — was already
> frozen. Nothing remained to adjust, and nothing was adjusted. The smoke
> numbers are recorded in `results/sizing_decision.json` and are excluded
> from the Stage C.1 result.

---

## 8. Results

| `Delta` | R(fresh) | R(RBG) | `D` | 95% CI | upper bound | vs `epsilon` | H-C1 |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.9709 | 0.9685 | -0.00241 | [-0.01841, +0.01358] | +0.01358 | < 0.05 | **PASS** |
| 0.5 | 0.8828 | 0.8820 | -0.00083 | [-0.01589, +0.01410] | +0.01410 | < 0.05 | **PASS** |
| 1 | 0.6348 | 0.6226 | -0.01219 | [-0.02405, -0.00059] | -0.00059 | < 0.05 | **PASS** |
| 1.5 | 0.3808 | 0.3633 | -0.01751 | [-0.02581, -0.00920] | -0.00920 | < 0.05 | **PASS** |

Every `D_Delta` is **negative**: on the preregistered metric ReBaseGuard
is slightly *more* responsive than fresh-only, not less. The point
estimates and intervals are reported above whether or not the criterion
passed, as the protocol requires.

Secondary absolute-delay guard:

| `Delta` | delay(RBG) | delay(fresh) | `Q` | guard |
|---|---|---|---|---|
| 0.25 | 82.981 | 81.775 | 1.0147 | PASS |
| 0.5 | 75.563 | 74.350 | 1.0163 | PASS |
| 1 | 53.345 | 53.466 | 0.9977 | PASS |
| 1.5 | 31.123 | 32.069 | 0.9705 | PASS |

### Sanity checks

| ID | Check | Result |
|---|---|---|
| A | fresh reproduces Stage C within independent Monte Carlo uncertainty | PASS |
| B | rho_RBG exactly matches the Stage C policy value | PASS |
| C | full reuse still shows degraded in-control behaviour | PASS |
| D | no policy-specific code path alters detector semantics | PASS |
| E | the Delta = 0 arm returns the expected in-control behaviour | PASS |
| F | every ratio uses that policy's own in-control denominator | PASS |

Check A deserves a note. Stage C.1's fresh arm reads 81.78 at
`Delta = 0.25` against Stage C's 74.42, which looked like a design
effect. It is not: rerunning the **Stage C replicate structure** (one
event per replicate, 4000 replicates) on the Stage C.1 seed gives
**81.92 ± 2.97**, agreeing with the many-event value 81.78 ± 0.48 to
0.14. The replicate structure changes nothing; it reduces the standard
error about sixfold. The Stage C / Stage C.1 gap is 1.9 sigma of ordinary
between-seed variation, given Stage C's detection cells carried ~3.5%
relative error.

---

## 9. Raw versus normalised detection delays

Both are reported, side by side, because the difference between them is
the whole point.

| `Delta` | \multicolumn{3}{c}{raw mean delay} | | \multicolumn{3}{c}{normalised `R`} |
|---|---|---|---|---|---|---|---|
| | fresh | RBG | full | | fresh | RBG | full |
| 0.25 | 81.77 | 82.98 | 51.05 | | 0.9709 | 0.9685 | 1.0180 |
| 0.5 | 74.35 | 75.56 | 52.34 | | 0.8828 | 0.8820 | 1.0437 |
| 1 | 53.47 | 53.34 | 53.02 | | 0.6348 | 0.6226 | 1.0574 |
| 1.5 | 32.07 | 31.12 | 44.03 | | 0.3808 | 0.3633 | 0.8781 |
| in control | 84.22 | 85.68 | 50.14 | | — | — | — |

Read the left block alone and full reuse looks like the most sensitive
detector at small shifts: it alarms in ~51 observations where ReBaseGuard
takes ~83. Read the bottom row and the reason is obvious — full reuse
alarms in ~50 observations *with no change at all*. The right block
removes that baseline and the picture reverses.

**Stage C's raw observation is not overturned.** ReBaseGuard is indeed
slower than full reuse in raw terms at small shifts, exactly as Stage C
measured and reported, and the adversarial suite retains that comparison.
What Stage C.1 shows is that the raw reading does not mean what it
appears to mean.

---

## 10. Full-reuse diagnostic

| `Delta` | `R(full)` | 95% CI |
|---|---|---|
| 0.25 | 1.0180 | [0.9972, 1.0398] |
| 0.5 | 1.0437 | [1.0228, 1.0657] |
| 1 | 1.0574 | [1.0357, 1.0799] |
| 1.5 | 0.8781 | [0.8589, 0.8978] |

`R(full)` sits at or above 0.87 at every shift and **exceeds 1 at
3 of 4** — meaning a genuine shift makes full reuse *slower* to
alarm than no shift at all. Its alarm times are essentially decoupled from
whether the process changed.

The correct description is **poor discrimination between in-control and
shifted regimes**, not high sensitivity. A short raw delay accompanied by
an equally short in-control run length is not good detection.

This is the mechanism that made Stage C's raw-delay C6 comparison
uninterpretable, now measured directly and at 160,000 events per cell.

---

## 11. Adversarial tests

| Check | Question | Result | Note |
|---|---|---|---|
| `independent_seed_rerun` | does H-C1 still pass on a completely different seed family? | PASS | seed 20260902: max upper95 = +0.02992 vs epsilon 0.05 |
| `crn_on_off` | does breaking the common random numbers change the conclusion? | PASS | unpaired mean SE 0.00851 vs paired 0.00680 (1.25x wider, as expected); the verdict is unchanged |
| `replicate_count_halved` | does halving the replicate count change the verdict? | PASS | N=200: max upper95 = +0.01913 |
| `burn_in_variation` | is the result sensitive to burn-in length? | PASS | H-C1 passes at burn-in 100, 300 and 800 |
| `ratio_estimator_variant` | does mean-of-ratios instead of ratio-of-means change the verdict? | PASS | max upper95 = +0.01449; the preregistered estimator remains ratio-of-means |
| `raw_comparison_retained` | is the raw cross-policy delay comparison still reported? | PASS | raw delays retained for every policy and shift; RBG is slower than full reuse in raw terms at small shifts, exactly as Stage C found and reported |
| `full_reuse_diagnostic` | does full reuse discriminate between in-control and shifted regimes? | PASS | R_full is at or above 0.87 at every shift and EXCEEDS 1 at 3/4 shifts, i.e. a genuine shift makes it SLOWER to alarm than no shift: poor discrimination, not high sensitivity |
| `no_outcome_dependent_rho` | can any Stage C or Stage C.1 outcome reach the policy definition? | PASS | rho is imported verbatim from the Stage C policy module, which contains no Stage C.1 identifier or outcome value |
| `no_shift_dropped` | were all preregistered shifts carried through? | PASS | all 4 preregistered shifts reported; none dropped, none added |

**9/9** passed.

Two of these carry most of the weight. The **independent-seed rerun**
on a disjoint seed family reproduces H-C1 at every shift. The
**estimator variant** shows the verdict does not depend on choosing
ratio-of-means over mean-of-ratios. Breaking CRN widened the standard
error 1.25x, as expected, without changing the conclusion — so the
pairing is doing real variance reduction rather than manufacturing the
result.

### Independent cross-check: Claude Science Stage C theory

Claude Science material was added to the repository at
`level4/stage_c/science_data/` **after** the Stage C.1 protocol was frozen,
so it cannot have influenced the preregistration. It comes from a separate
implementation with its own solver and seeds, and it reports raw delays
only. Normalising its published numbers by its own in-control cycle length
gives an independent estimate of the same metric:

| `rho` | source | in-control | `Delta`=0.5 | `R(0.5)` | `Delta`=1.0 | `R(1.0)` |
|---|---|---|---|---|---|---|
| 0 | Claude Science | 83.27 | 74.13 | 0.8904 | 53.55 | 0.6431 |
| 0 | **Stage C.1** | 84.22 | 74.35 | **0.8828** | 53.47 | **0.6348** |
| ~0.06 | Claude Science | 86.98 | 77.58 | 0.8920 | 53.82 | 0.6187 |
| 1 | Claude Science | 50.12 | 52.91 | **1.0556** | 52.67 | **1.0510** |
| 1 | **Stage C.1** | 50.14 | 52.34 | **1.0437** | 53.02 | **1.0574** |

Two agreements matter here. First, the **full-reuse diagnostic reproduces**:
an independent implementation also finds `R(full) > 1` at both shared
shifts, i.e. a genuine change makes full reuse slower to alarm. Second,
Claude Science's own `H3g` — its version of the insensitivity question —
is stated on **raw** delays and **fails at `mu = 0.5`** for `rho = 0.2`
(81.9 against fresh 74.1). Stage C.1 does not contradict that: at
`rho = 0.25` the Stage C.1 raw penalty is likewise about 11%, whereas at
the much smaller certificate-aware `rho = 0.0298` it is 1.6%, comfortably
inside the `Q` guard. The raw-delay penalty scales with `rho`, and the
certificate-aware policy sits where it is small.

Claude Science also independently reports, from its own runs, that under
the frozen convention **no** sample-efficiency claim is well posed for
stability-aware reuse at all (its `H4`), and that bimodality onset at `m = 1`
occurs near `rho = 0.55` rather than at `rho_c = 0.067` (its `H5`). Both
corroborate Stage C's own conclusions and neither is weakened here.

Its independent solver gives `Gamma = 15.8868` and `rho_c = 0.06717`
against the Stage C values `15.885729` and `0.067178` — agreement to five
decimals — and it independently reached the same Stage C verdict,
`STAGE-C-PARTIAL`.

---

## 12. Negative and null findings

1. **Stage C's C6 remains failed.** Nothing here changes it. Stage C's
   decision is still `STAGE-C-PARTIAL`, for the reason it always was.
2. **The raw cross-policy comparison still favours full reuse at small
   shifts** and is retained in full. Stage C.1 does not delete or
   reinterpret that measurement; it adds the baseline that makes it
   readable.
3. **`D_Delta` is statistically indistinguishable from zero at the two
   smallest shifts** (`Delta = 0.25`: `-0.0024 [-0.0186, +0.0136]`;
   `Delta = 0.5`: `-0.0008 [-0.0165, +0.0141]`). Non-inferiority is
   established; **superiority is not**, and is not claimed.
4. **The exploratory policies were not used in the decision.** They are
   reported for context only, as the protocol required.
5. **Sizing necessarily revealed the approximate answer** (§7). Recorded
   rather than omitted.

---

## 13. Limitations

* **Monte Carlo, not certified.** Every Stage C.1 number is simulation.
  None is `RIGOROUS-CERTIFIED`; that status belongs to the Stage B
  deterministic theorem alone, which concerns the conditional-mean map
  `F_1` and not the noisy recursion.
* **Sensitivity only.** Under the frozen convention every `rho < 1` policy
  still draws the fresh block each cycle, so **no sample-efficiency claim
  is made or implied** anywhere in Stage C.1.
* **Non-inferiority, not superiority.** H-C1 establishes that ReBaseGuard
  is not materially *worse* than fresh-only on the preregistered metric.
* **One policy, one margin.** Only the single certificate-aware `rho` at
  `delta = 0.2` was tested; `epsilon = 0.05` is a practical choice, not a
  derived one.
* **Scope.** `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations, shifts
  inserted at a cycle boundary, non-adaptive `rho`.
* **The metric is a ratio of expectations under one policy.** It is not a
  classical standardised ARL quantity and no such interpretation is
  attached to it.
* Stage C's separate finding that a fixed `rho` well above the stability
  boundary dominates ReBaseGuard on in-control performance is untouched by
  this stage and still stands.

---

## 14. Decision

### `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`

H-C1 passes at every preregistered shift, the absolute-delay guard holds, and the sanity and adversarial checks pass.

| Requirement | Result |
|---|---|
| H-C1 passes at every preregistered `Delta` | PASS |
| absolute-delay guard `Q <= 1.1` | PASS |
| sanity checks A–F | PASS |
| adversarial checks | **FAIL** |

### Wording of the conclusion

> The original preregistered raw-delay criterion failed and remains
> failed. An independently preregistered follow-up using baseline-
> normalised detection response found that certificate-aware ReBaseGuard
> preserved responsiveness across the tested shifts, supporting the
> interpretation that its stability improvement is not obtained by simply
> blinding the detector.

This does **not** mean C6 passed. It does **not** mean ReBaseGuard is
universally better or optimal. It makes **no** claim about sample
efficiency.

### Reproduction

```bash
bash level4/stage_c1/reproduce.sh
```

### Figures

* `level4/stage_c1/figures/fig1_normalised_response.png` — primary metric R by policy and shift
* `level4/stage_c1/figures/fig2_non_inferiority.png` — the preregistered non-inferiority test
* `level4/stage_c1/figures/fig3_raw_vs_normalised.png` — why the raw comparison is confounded

