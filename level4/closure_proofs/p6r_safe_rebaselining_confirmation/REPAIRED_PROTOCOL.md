# P6R repaired protocol — the precommit package

```text
STATUS AT WRITING = PRECOMMIT.  No P6R confirmation EVAL has been executed.
EVIDENCE PRESENT  = the frozen P6 calibration (TUNE, Delta = 0), audited;
                    the P6R TUNE-only baseline selection (TUNE, Delta = 1).
EVIDENCE ABSENT   = every P6R EVAL and REPLAY number.
ANCHOR            = this package is committed and pushed BEFORE confirmation EVAL runs.
                    The commit SHA is recorded in results/precommit_anchor.json.
```

This document is the whole precommitment. Everything a later reader needs in
order to say "the campaign did what it said it would" is here, and nothing in it
may be changed once the Checkpoint A commit exists. Where it departs from the
original P6 protocol it does so **only** to repair an adjudicated defect, and
each departure names the defect.

---

## 1. Theorem scope

`THEOREM_SCOPE.md`, in full. In summary: **T6-B** `EXACT_VALID`, unchanged, with
its memoryless policy class stated field-by-field; **T6-C** exact **for fixed
`k`**, with the explicit statement that the scalar Jensen formula is *not*
claimed for adaptive `k` and that no adaptive-`k` theorem is asserted. Every
headline cell below fixes `k`.

## 2. The fixed-`rho` grid and the TUNE-only selection rule *(repairs B1)*

```text
RHO_FINE = { 0.05, 0.06, 0.07, ..., 0.34, 0.35 }        31 points, 0.01 spacing
```

```text
S1  for each cell (detector, m, k):
      family    TUNE, and TUNE only
      arm       Delta = 1, shift injected at cycle 15, one delay per replicate
      n_rep     150,000 replicates per grid point
      curve     d(rho)  = TUNE estimate of Dtail(100)
      smoothing s(rho)  = centred 5-point moving average of d, edge-truncated
      choice    rho*_TUNE = argmin_rho s(rho)
      ties      smaller smoothed Dq95, then smaller rho
```

The moving average is **part of the rule**, declared here and implemented in
`select.py::select_rho`: on a `0.01`-spaced grid the fixed-`rho` objective is
nearly flat across `[0.15, 0.30]`, and a raw argmin over 31 correlated noisy
points is dominated by selection noise. Smoothing gives the baseline its best
shot, which is what an honest bar requires. The unsmoothed argmin, the `Arl0`
argmax and the `Rms` argmin are recorded as TUNE diagnostics.

**Second control, declared now.** `rho = 0.25` — the value the independent
adjudication identified as the TUNE optimum for the primary CUSUM `m=3, k=3`
cell — is carried into confirmation as `FIXED_ADJ` whether or not S1 selects it.
**The headline claim must survive against whichever of `FIXED_TUNE` and
`FIXED_ADJ` is less favourable to SAW-M.** This is strictly harder than S1
alone.

**No EVAL-dependent baseline selection is permitted anywhere.** For every
robustness cell the selection is run prospectively by the same rule, on TUNE,
and written to the frozen artifact before that cell is evaluated. The REPLAY
reproduction uses the **same** `rho*_TUNE`; it is never re-selected.

## 3. Confirmation plan — frozen cells, frozen order

Executed in this order. **No cell is added after any result is inspected.**

| id | cell | arms | purpose |
|---|---|---|---|
| **P** | CUSUM, `m=3`, `k=3`, `Delta=1` | `B3` full reuse; `B0` fresh-only; `FIXED_TUNE`; `FIXED_ADJ`; **`SAW_M`** | the primary comparison |
| RC1 | SR, `m=3`, `k=3`, `Delta=1` | same, with SR's own `rho*_TUNE` | separately calibrated replication across detectors |
| RC2 | CUSUM and SR, `m in {1,2,5}`, `k=m`, `Delta=1` | same, each with its own `rho*_TUNE` | window replication |
| RC3 | primary cell at `Delta in {0.5, 2}` | `B3`, `B0`, `FIXED_TUNE`, `SAW_M` | the declared `Delta` scope of section 7 |
| RC4 | primary cell, `e_0 ~ N(0, 1/m_0)`, `m_0 in {20,50,100}` | `B3`, `B0`, `FIXED_TUNE`, `SAW_M` | post-burn-in robustness to alternative initialization |
| RC5 | primary cell, **REPLAY** family | as **P** | independent-seed reproduction, run only after the EVAL analysis is frozen |

Sample sizes, frozen, and deliberately identical to the original campaign so
that the repaired numbers are comparable with the historical record:

```text
in-control cells : n_rep = 8,000    n_cycles = 100   burn_in = 15
delay cells      : n_rep = 60,000   shift injected at cycle 15, one delay per replicate
seeds            : SeedSequence([family_root, sha256(detector)[:8], m,
                                 sha256(policy_id)[:8], sha256(cell_tag)[:8], block])
                   families TUNE / EVAL / REPLAY, asserted disjoint
pairing          : all arms in a cell share one replicate stream (pair_tag),
                   so per-replicate differences are paired; the realised pair
                   correlation is measured and reported, never assumed
```

## 4. Metrics

**Primary objective (the closure gate):** `Dtail(100)` at cell **P**, SAW-M
against `FIXED_TUNE`, subject to the event floor of section 6.

**Declared co-primary claims**, each reported individually and all inside BH
family F1: `Arl0`, reference `Rms`, `Dmean`, `Dq95`, and the one-step risk gain
`G` of section 9.

**Secondary / reported:** `Fap(100)`, `Mad`, `Q95e`, `Tail(0.2/0.5/1.0)`,
`OutCal(beta)` for `beta in {0.75, 0.5, 0.25, 0.1}`, `Dmed`, `Dtail(50)`,
`Rdelta = Dmean / Arl0`, `Coll = E[tau_2]/E[tau_1]`, and the three cost
accountings of section 5.

**`Coll` carries no threshold.** The original `G-E` gate had an ordering defect
(**B4**); P6R does not re-litigate it and does not replace it. `Coll` is a
reported diagnostic, declared thresholdless here, in advance.

**Materiality:** `10%` relative, as in the original preregistration. Verdict
labels are P7's, verbatim: `INCONCLUSIVE`, `STATISTICALLY_RESOLVED`,
`PRACTICALLY_MATERIAL`, plus `INSUFFICIENT_TAIL_EVENTS`.

## 5. Cost definitions *(repairs Q2)*

```text
PRIMARY      fresh-sample acquisition cost   C_acq(j)  = k_j * 1{rho_j < 1}
SENSITIVITY  proportional fresh contribution C_prop(j) = (1 - rho_j) * k_j
SENSITIVITY  quadratic / effective           C_quad(j) = (1 - rho_j)^2 * k_j
```

The primary metric is unchanged in definition and only renamed. The **only**
permitted primary cost claim is:

> SAW-M and the comparison fixed-`rho` baseline require the same number of newly
> acquired fresh samples per update, under the frozen acquisition-cost
> definition.

The claims "SAW reuses more", "SAW is cheaper", "SAW has a lower effective fresh
contribution cost" are **forbidden** unless the repaired selected baseline and
the corresponding measured sensitivity actually support them in the cell being
reported. `costs.py::report_costs` returns the signed direction so the answer is
read off the data. Against a TUNE-selected baseline near `rho = 0.25` these
claims may well be **false**, and that outcome is to be reported, not avoided.

## 6. Statistical procedure *(repairs B2)*

```text
unit                 the independent replicate
resamples            N_BOOT = 10,000, EXACTLY          (asserted by test)
intervals            BCa (bias-corrected + accelerated), with a real jackknife
                     acceleration: closed form for ratios of means, exact
                     leave-one-out for ratios of quantiles
                     AND a normal-approximation interval emitted beside every one
ratios               bootstrapped AS RATIOS: one replicate index vector draws
                     numerator and denominator together; never a post-hoc
                     division of independently bootstrapped means
p-values             two-sided percentile bootstrap against theta = 1,
                     floored at 1/B
Rdelta               = Dmean / Arl0 mixes two INDEPENDENT simulation blocks (the
                     delay run and the in-control run), so no single replicate
                     index pairs them.  Its resample draws one index vector per
                     block and applies each to BOTH policies: paired across
                     policies, independent across blocks, ratio re-formed inside
                     every resample
multiplicity         Benjamini-Hochberg, q = 0.10, over the declared families below
tail-event floor     200 events per arm, in BOTH arms
clustered statistics the one-step risk resamples REPLICATE CLUSTERS, never cycles
```

**Declared BH families.**

| family | contents | correction |
|---|---|---|
| **F0** | the single primary test: `Dtail(100)` at cell **P**, SAW-M vs `FIXED_TUNE` | none — one test; reported raw, and repeated against `FIXED_ADJ` |
| **F1** | the primary cell's co-primary and secondary metrics vs `FIXED_TUNE`: `Arl0`, `Fap100`, `Rms`, `Mad`, `Q95e`, `Tail1.0`, `OutCal0.25`, `Dmean`, `Dmed`, `Dq95`, `Dtail50`, `Rdelta`, `Coll`, one-step `G` | BH `q = 0.10` |
| **F2** | the replication family: `Dtail(100)`, SAW-M vs each cell's own `rho*_TUNE`, over the 8 `(detector, m)` cells of **P**+RC1+RC2 | BH `q = 0.10` |
| **F3** | the `Delta`-scope family: the primary metric at `Delta in {0.5, 2}` | BH `q = 0.10`; sub-floor cells are **excluded** from the family and labelled |
| **F4** | the finite-reference family: the primary metric at `m_0 in {20,50,100}` | BH `q = 0.10` |

**Tail-event floor.** A `Dtail` estimate is reportable as an effect only if
**both** arms carry at least `200` exceedances. Below that the cell is labelled
`INSUFFICIENT_TAIL_EVENTS` — never `INCONCLUSIVE` — it carries **no resolved
claim**, and it is excluded from its BH family rather than consuming
false-discovery budget.

**No sample-size increase after inspection.** If a cell falls below the floor,
the declared fallback is `Dq95`. Raising `n_rep` in response to an inspected
result would require a separately preregistered power-extension campaign and is
out of scope here.

## 7. `Delta`-specific claim scope *(repairs Q4, Q5)*

| `Delta` | precommitted scope |
|---|---|
| **1** | the primary moderate-shift regime. Primary and co-primary claims live here: `Arl0`, reference `Rms`, `Dmean`, `Dq95`, `Dtail(100)` **if the event floor is met**, and the one-step risk |
| **0.5** | **predeclared as a limitation.** The original campaign established **no coherent aggregate adaptive advantage** at `Delta = 0.5`. P6R reports the cell and treats it as a limitation, not as a failed result to optimise away. **SAW-M is not altered to target `Delta = 0.5`** — its four constants are the frozen P6 constants, fitted at `Delta = 0`, and nothing about the method changes in P6R |
| **2** | `Dtail(100)` is **inferentially unresolved** unless the 200-event floor is met in both arms; `Dq95` is the declared fallback metric. No post-inspection sample-size increase |

## 8. Calibration diagnostics *(repairs Q3)*

The method's constants are **not re-derived**: they are the adjudicated object,
fitted on TUNE at `Delta = 0`, and re-deriving them would change what is being
confirmed. They are **audited**. `audit.py` reports per cell:

* the convergence flag actually recorded, and the iterations reached;
* the number of observations behind `s1`;
* whether the `1e-2` variance floor is active;
* whether the `rho_max = 0.95` cap can bind;
* whether the final large-pass refit was followed by another fixed-point update.

**Declared in advance:** "all cells converged" is **not** claimed and is false.
Cells whose `s1` rests on fewer than `50` observations receive the predeclared
sensitivity check of `experiments/precommit_freeze.py`: `s1` is perturbed to
`{0.5x, 2x}` its fitted value and to `s0`, and the resulting change in the
policy's realised decisions is measured on TUNE. **Primary-cell stability may
not be used to excuse an unstable secondary cell**; each cell's sensitivity is
reported for that cell.

## 9. The one-step risk statistic *(repairs Q8)* — formula precommitted

Fixed `k`, hence fixed `nu = 1/k`. On the post-burn-in cycles of one chain,
with `U_{r,j} = e_{r,j} + zbar_{r,j}` the realized raw window mean (exact by T1)
and `rho_hat_{r,j}` the weight the policy actually chose:

```text
M2      = mean_{r,j} [ U^2 ]
R_star  = min over CONSTANT rho_0 of  ( rho_0^2 M2 + (1-rho_0)^2 nu )
        = nu M2 / (M2 + nu)                       at rho_0* = nu/(M2 + nu)
R_adapt = mean_{r,j} [ rho_hat^2 U^2 + (1-rho_hat)^2 nu ]
G       = 1 - R_adapt / R_star
```

Both risks are evaluated on the **same cycles**, i.e. under a common entering
law — exactly the setting in which fixed-`k` T6-C is exact — and `R_star` is the
best constant weight **on that very sample**, not a grid member. Uncertainty:
replicate-cluster bootstrap, BCa, 10,000 resamples.

Reported **twice**, both declared now: `G` computed on the SAW-M chain's cycles
(primary) and on the `FIXED_TUNE` chain's cycles (secondary), because the two
chains induce different entering laws and neither is privileged.

The `sigma(V_hat)`-restricted diagnostic from the original campaign is retained
and **labelled restricted** wherever it appears. Because `R_adapt` uses the
plug-in weights, `G` is a **lower bound** on the achievable gap, and **the
plug-in is not the oracle `F`-measurable optimizer**.

## 10. Language constraints, binding on every P6R document

| forbidden | required instead |
|---|---|
| "detector transfer" | **separately calibrated replication across CUSUM and SR** (no no-recalibration transfer experiment is run) |
| "full initialization robustness" | **post-burn-in robustness to alternative initialization**; cycle-1 behaviour reported separately as descriptive evidence |
| "SAW reuses more" / "is cheaper" / "lower effective fresh cost" | only what the measured sensitivity supports, in the cell being reported |
| any novelty upgrade | the wording of `NOVELTY_SCOPE.md`, unchanged |
| any claim resting on sub-floor tail counts | `INSUFFICIENT_TAIL_EVENTS` |

## 11. Closure rule *(frozen)*

> **P6R may conclude `P6 = CLOSED`** only if **all twelve** hold:
>
> 1. T6-B remains valid;
> 2. fixed-`k` T6-C remains valid;
> 3. SAW-M remains observable and memoryless;
> 4. the fixed baseline is selected exclusively on TUNE;
> 5. repaired EVAL preserves the primary scientific effect;
> 6. the preregistered statistical analysis is actually executed;
> 7. no claim relies on sub-floor tail counts;
> 8. `Delta = 0.5` remains honestly scoped as a limitation;
> 9. calibration defects are correctly reported;
> 10. the new precommit commit predates confirmation EVAL;
> 11. no protected historical artifact is rewritten;
> 12. all documented claims agree with generated artifacts.
>
> **If any scientific result materially fails, report `P6 = PARTIAL`.**
> No threshold is moved and no success criterion is redefined.

The first-party verdict is **not** an independent closure. The next independent
reviewer owns final closure.

## 12. Execution order *(repairs B3)*

```text
1. freeze this package + THEOREM_SCOPE.md + ADJUDICATION_RECORD.md + NOVELTY_SCOPE.md
2. run the TUNE-only selection and the calibration audit   (TUNE only; no EVAL)
3. run the focused tests
4. verify protected-tree integrity
5. COMMIT and PUSH Checkpoint A          <- the temporal anchor
6. record the commit SHA in results/precommit_anchor.json
7. only then run confirmation EVAL
8. freeze the EVAL analysis, then run REPLAY
9. COMMIT and PUSH Checkpoint B
```

Step 7 may not begin before step 6 exists.
