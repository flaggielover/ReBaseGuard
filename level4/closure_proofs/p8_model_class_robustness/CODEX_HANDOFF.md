# P8 -> Codex handoff

**Do not trust Claude's candidate verdict.** It was produced by the same agent
that designed the experiments, wrote the gates and ran the code. The gates are
`P8_ORIGINAL` — no historical P8 gate existed to constrain them — so the
preregistration is only as good as the timestamps and digests in
`results/pilot_notes.json`, `results/posthoc_preregistration_H2.json` and
`results/protocol_amendments.json`. **Check those first.** Everything below is
a claim to be attacked, not a finding to be accepted.

---

## 1. The exact P8 question

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c` (P3), and the operational monitoring degradation
> (P7) — survive outside that specialisation, across innovation-distribution
> families, detector families, reuse windows `m`, reuse conventions and drift
> patterns?

Traced to four frozen statements (`p7/EXPERIMENT_DESIGN.md:21`,
`p7/CLOSURE_REPORT.md:102`, `p7/README.md:56`,
`p6_safe_rebaselining_predesign/DEPENDENCY_LEDGER.md:155`) in
`P8_DEFINITION_AUDIT.md` §2. **First thing to check: is that the right P8?**
Note the naming collision documented as `U1`: `P8` is *also* P5's premise label
for RMS/ARL co-optimality, and this campaign deliberately does **not** address
that.

## 2. Candidate verdict

```text
P8 = PARTIAL_CANDIDATE
```

17 of 21 gates pass. The four failures are `G4`, `G4-D`, `G4-F` (the
preregistered window-separability law) and `G7` (transfer of P7's boundary
verdict). None was re-thresholded. The whole correctness / reproduction /
integrity spine passes, which is what makes the verdict `PARTIAL` rather than
`FAIL` under the frozen rule in `CLOSURE_GATES.md`.

## 3. Strongest surviving result

**The recursive re-baselining phenomenon survives outside the frozen Gaussian
specialisation, but only qualitatively.**

* Survives: `Gamma_A` has a lower 95% bound above `2` — so `rho_c < 1` and full
  reuse is locally repelling — in **all 40** eligible `(detector, family,
  m in {1,2,3,5})` cells and in the 8 moment-marginal `t3` cells reported beside
  them. Operationally, `ARL_0` at full reuse is `10.5%`–`29.8%` of the same-cell
  nominal, and the reuse-attributable loss against the same-`m` fresh control is
  `-37.9%` to `-50.7%`, in **every** family (gates `G3`, `G8`).
* Does not survive: the magnitude. `rho_c(D,f,1)` spans a factor of `2.54`, and
  the sign of the error against the Gaussian value is not uniform — heavy tails
  raise the boundary, `10%` contamination lowers it.

**The sharpest single contrast in the campaign**: the local multiplier varies by
a factor of `2.4` across the matrix while the reuse-attributable operational
damage stays inside `-38%` to `-51%`. That is an unusually clean empirical
illustration of `X6` / the rejected candidate `P7-E` — the derivative of
`E[e_1]` does not determine the derivative of `E[M(e_1)]` — demonstrated across
a model class rather than within one model.

## 4. Strongest theorem and its assumptions

`P8-T1` (`THEORY.md`): for a general regular location family and every
convention-A window `m`,

```text
Gamma_A(D,f,m) = E_0[ zbar^A_m * sum_{t<=tau} psi(Z_t) ],
F'_{rho,m}(0)  = rho ( 1 - Gamma_A ),   rho_c = 1/|1 - Gamma_A|.
```

**Status: `THEOREM_CONDITIONAL_ON_PARTIAL_PREMISE`.** It is P4's abstract
stopped-score theorem — which lives in `P4 = PARTIAL` — applied to a new stopped
functional. P8 *proves* the part that is not automatic (hypotheses 1–3, the
measurability of the truncated window with its state-dependent denominator) and
*assumes*, per family, P4's analytic hypotheses 7–9: a.s. finiteness of `tau`
locally in `e`, absolute summability of the event-sliced change of measure, and
integrable domination of the stopped likelihood difference quotient. **Those are
not verified for the two-sided CUSUM or SR recursion under any heavy tail.** If
they fail, `rho_c` is not the derivative of anything.

`P8-L1(a)` (`E[eps psi(eps)] = 1` for every regular location family) and
`P8-L1(b)` (the exact lag decomposition, with `Gamma_A - Gamma_B = R_m`) are
unconditional and are used as exact estimator anchors, verified to `7e-16` and
`4e-15` in all 72 cells (gates `G5`, `G6`). `P8-T2` (the reset decomposition for
a general innovation family) is exact and, on its own, operationally empty.

**No enclosure, no Lean, no certified numerics anywhere in P8, and none is
claimed.**

## 5. Main numerical result

The `Gamma_A` / `rho_c` matrix, `4,096,000` cycles per `(detector, family)`
cell, at a matched `ARL_0 = 465.50394`:

| | `gaussian` | `t10` | `t5` | `t3` | `contam0.05` | `contam0.1` |
|---|---:|---:|---:|---:|---:|---:|
| `Gamma_A(1)` CUSUM | 15.885 | 15.428 | 13.235 | 8.512 | 15.604 | 18.126 |
| `Gamma_A(1)` SR | 17.327 | 17.439 | 16.086 | 11.753 | 18.003 | 20.097 |
| `rho_c(1)` CUSUM | 0.0672 | 0.0693 | 0.0817 | 0.1331 | 0.0685 | 0.0584 |
| `rho_c(1)` SR | 0.0612 | 0.0608 | 0.0663 | 0.0930 | 0.0588 | 0.0524 |
| `w_1` CUSUM | 0.6466 | 0.5535 | 0.4354 | 0.2860 | 0.3712 | 0.3466 |
| `w_1` SR | 0.6414 | 0.5447 | 0.4111 | 0.2421 | 0.3553 | 0.3423 |

Full tables, with standard errors, intervals, regimes, `Gamma_B`, `R_m`,
`P(tau<m)`, the lag profiles at every `r < 20`, the 310 chain rows and the 288
drift rows: `results/result_tables.json`.

## 6. Baseline / reproduction table

| target | source | P8 result |
|---|---|---|
| P3 Gaussian `GammaTilde`, both detectors, `m in {1,2,3,5}` | `CLOSED` | 8/8 within `\|z\| <= 3`; but see the SR offset below |
| P3 vs P7 vs P8 on the Gaussian **SR** gain | `CLOSED` / `CLOSED` / P8 | P8 agrees with **P7** (`z = +0.66..+0.86`) and both sit `0.70%`–`0.80%` **below** P3 at every `m` (`z = -1.75..-2.07`). Same sign and magnitude P7 recorded. P8 does not own or resolve it |
| P4 `Gamma_f`, `m=1` CUSUM, six families | `PARTIAL` | 6/6 within `\|z\| <= 3`, largest `\|z\| = 1.55` |
| Stage-D D3 `Gamma_psi`, six families | `STAGE-D-PARTIAL` | 6/6 within `\|z\| <= 2.1` |
| Stage-D `gamma_T_naive_DIAGNOSTIC_ONLY` | Stage D | reproduced |
| `ARL_0` at the frozen CUSUM thresholds | Stage D | within `0.1%`, six families |
| Fisher information vs Stage-D `E[psi']` | Stage D | within `1.5e-8`, six families |
| `psi` vs P4's frozen `location_score` | P4 | within `8.9e-16` |
| P7 `ARL_0` collapse at `rho=1`, `m=1`, Gaussian CUSUM | `CLOSED` | P7 `48`–`80`; P8 `50.1` |
| P7 reuse-attributable ARL loss, `m=1 -> m=5` | `CLOSED` | P7 `-40% -> -51%`; P8 `-40.0% -> -50.7%` |
| P7 delay tail, `m=1, rho=1, Delta=1`, Gaussian CUSUM | `CLOSED` | P7 mean `52.6`, med `7`, `q95 275`, `P(>100) 11.4%`; P8 `48.9`, `7`, `250`, `11.0%` |
| P7 discrimination `R_Delta` at `m=1, rho=1` | `CLOSED` | P7 `1.06`; P8 `0.976` (CUSUM), `1.055` (SR) |

**A published disagreement resolved.** P4 and Stage-D D3 report numbers for the
same family, threshold and window that differ by up to a factor of `3.35`. P8
measures both estimands in one pass and reproduces each against its own source:
the gap is **entirely definitional** (raw window x score sum, versus
score-transformed window x score sum). P8 adjudicates neither and edits neither.

## 7. Uncertainty

Batch means over 20 addressable batches are the unit for `E1`/`E5`; the
replicate is the unit for the chain and drift runs. Relative SE of `Gamma_A(1)`:
`0.08%` (`gaussian`) to `1.59%` (`t3`, `16.5x` inflation, the predicted
signature of its divergent third absolute moment). `K`'s SE is computed from
batch ratios, not by an independence-assuming delta method. `rho_c` intervals
are the exact monotone image, not a linearisation. Every invariance gate is a
practical-equivalence gate with a pre-declared margin; Cochran's `Q` is reported
and labelled `DESCRIPTIVE_ONLY`. Full detail in `STATISTICAL_AUDIT.md`.

## 8. Robustness

Six innovation families x two detectors x six windows x two window conventions x
{in control, three step sizes, two ramp slopes}, plus an independent seed family
over the whole `Gamma` matrix. Detail in `ROBUSTNESS.md`. The one cell where the
phenomenon disappears is CUSUM / `t3` / `m = 20`: `Gamma_A = 1.949 +- 0.007`,
regime `GAMMA_BETWEEN_1_AND_2`, `rho_c = 1.054 > 1`, so every admissible reuse
fraction is locally attracting. It sits inside the `EXTRAPOLATION_BEYOND_P3`
region and is not gated.

## 9. Novelty status

`NOVELTY = NOT_INDEPENDENTLY_ADJUDICATED`, and **weaker after the results than
before them**: the campaign's best novelty candidate, the window-separability
law, was measured and **rejected**, so it is not a candidate. P8 claims no novel
phenomenon, no novel theorem, no novel algorithm. The only
`PLAUSIBLE_BUT_NOT_ADJUDICATED` labels are on experimental syntheses whose axes
are individually standard. `NOVELTY_AUDIT.md` states the search's three
weaknesses.

## 10. Gate-by-gate table

See `RESULTS.md` §15 and `results/closure_decision.json`. Summary: `G1a`–`G1e`,
`G2`, `G3`, `G5`, `G6`, `G8`–`G15` **PASS**; `G4`, `G4-D`, `G4-F`, `G7`
**FAIL**.

## 11. Claims rejected or narrowed during the campaign

| claim | outcome |
|---|---|
| `H1`: `rho_c(m)/rho_c(1)` is invariant across detector **and** distribution | **REJECTED** on the distribution axis (`22.7%`–`49.3%` vs a `10%` margin) |
| `H1` narrowed to the detector axis alone | **NARROWED, and still failing its own `3%` sub-gate** in 1 of 15 comparisons (`3.63%`) |
| `H2a`: the lag profile is detector-invariant to `5%` | **REJECTED** (19/30, largest residual `19.66%`) |
| `H2b`: `w_1` is monotone in Fisher information | **REJECTED** out of sample by the held-out contaminated families, in both detectors |
| `H2c`: `K` is a function of `(m, w_1)` alone | **REJECTED**, and the test was weak (zero cross-family pairs qualified) |
| P7's boundary verdict transfers to every family | **REJECTED literally** (4/6); the uncertainty companion shows 5/6 with one narrow, uncorroborated exception |
| the ramp result at `rho > 0` | **NARROWED** to the first post-change cycle; `E4`'s 4 post-change cycles cannot measure ramp accumulation |
| `R_Delta` against the drift run's own pre-change mean | **REJECTED as a defect and fixed**; the corrected control is the `E3` post-burn-in ARL |
| any detector-transfer claim | **not made**; `Gamma_A` transfers in 0 of 36 comparisons, max deviation `27.6%` |

## 12. Protected-tree status

`G12` **PASS**: 24 protected trees, **zero** differences against
`results/protected_tree_manifest_pre.json`, recorded at anchor commit
`ffe23a63181e2ff11380768d3c73980de80f94fb` before any substantive work.
`git status --porcelain` reports nothing outside
`level4/closure_proofs/p8_model_class_robustness/`.
`tests/test_protected_scope.py` re-checks every tree independently, asserts no
P8 write call targets a protected-tree path constant, and asserts no P8 module
loads a P5 or P6 result artifact. **P4, P5, P6, P7 and Stage D are byte-identical
to their pre-campaign state.**

## 13. Focused tests

**126 tests**, all passing, in six files:

| file | tests | covers |
|---|---:|---|
| `test_families.py` | 38 | score vs P4's frozen module, score vs finite differences, the exact unit-diagonal lemma, Fisher information vs Stage-D, and a re-derivation of the `MOMENT_MARGINAL` set from the tail index rather than the literal |
| `test_crn_identity.py` | 18 | addressability, order-independence, live-set independence, cache-clear invariance, block boundaries including index `> 4 * BLOCK_LEN`, primitive-type collision, field digest |
| `test_semantics.py` | 14 | frozen CUSUM recurrence and inclusive post-update alarm, SR vs Stage-D's helper, `tau >= 1` and terminal increment, convention A vs B, newest-first truncated window, the frozen update line, `rho=0` reference variance, step and ramp drift semantics |
| `test_metrics.py` | 23 | `rho_c` in all seven P3 regimes, P3's exact finite-support witnesses, P7's boundary-rate arithmetic restated verbatim, the pathwise lag-decomposition identity, chain metric definitions, and two **exact** estimator anchors from a degenerate detector |
| `test_replay.py` | 5 | bit-identical replay, batch/row-block composition, single-replicate recoverability, `rho` not entering the primitive field |
| `test_protected_scope.py` | 28 | 24 protected trees, worktree scope, write-target scope, byte-identical thresholds, no P5/P6 result import |

## 14. Exact commands for independent replay

Full replay from scratch (dominated by `E1`/`E5`; expect several hours):

```bash
bash level4/closure_proofs/p8_model_class_robustness/reproduce.sh
```

Individual pieces, from the repository root, using the Level-4 virtual
environment (`level4/.venv/bin/python`, NumPy 2.5.2 / SciPy 1.18.0):

```bash
cd level4/closure_proofs/p8_model_class_robustness && ../../../level4/.venv/bin/python -m pytest tests -q
```

```bash
level4/.venv/bin/python level4/closure_proofs/p8_model_class_robustness/experiments/run_regularity.py
```

```bash
level4/.venv/bin/python level4/closure_proofs/p8_model_class_robustness/experiments/run_gamma_matrix.py cusum t5 --tag E1 --batch0 0 --force
```

```bash
level4/.venv/bin/python level4/closure_proofs/p8_model_class_robustness/experiments/run_cross_priority.py
```

```bash
level4/.venv/bin/python level4/closure_proofs/p8_model_class_robustness/experiments/derive_closure.py
```

Every gate verdict is recomputed by `derive_closure.py` from `results/*.json`
alone; it runs no simulation, so it is cheap to re-run after editing a
threshold in `CLOSURE_GATES.md` to see what the gate was actually protecting.

**Single-cell replay.** Any `(detector, family)` cell reproduces bit-for-bit
from its address alone — `experiment` tag, `batch`, `row_block` — with no
dependence on what else ran. `tests/test_replay.py` asserts this.

## 15. Files Codex should attack, in order

| # | file | why it is the weak point |
|---|---|---|
| 1 | `results/posthoc_preregistration_H2.json` | the only place P8 formulated a hypothesis after seeing data. Check the digests against the cell files, check the timestamps, and check the `contam0.05` caveat |
| 2 | `results/protocol_amendments.json` | two amendments (`A1` sample sizes, `A2` calibration procedure). Verify neither touched a gate threshold and that `A2` really preceded every SR non-Gaussian production cell |
| 3 | `src/rebaseguard_p8/stopped.py` | the whole `Gamma` matrix is one function. The window extraction (`order`, `valid`, newest-first ring buffer) is the place a subtle off-by-one would silently change every number |
| 4 | `src/rebaseguard_p8/primitives.py` | the CRN claim. Attack the row-banding in `chain_monitor_column`: it is an efficiency device, and the argument that it cannot change a delivered value is the thing to break |
| 5 | `src/rebaseguard_p8/families.py` | if `psi` is wrong for one family, that family's whole column is wrong. It is checked against P4's frozen module to `1e-12` and against finite differences, but both checks share P8's own density |
| 6 | `THEORY.md` `P8-T1` | hypotheses 7–9 are **assumed**, not verified, per family. If they fail for the two-sided CUSUM or SR recursion under a heavy tail, `rho_c` is not the derivative of anything |
| 7 | `experiments/derive_closure.py` | the gate arithmetic. In particular `gate_G7`'s **declared adaptation** to a clipped ladder, and `gate_G4`'s cell-count requirements |
| 8 | `src/rebaseguard_p8/calibrate.py` + `experiments/polish_sr_calibration.py` | P8's only new constants. A systematic bias here shifts every SR non-Gaussian number |
| 9 | `results/sr_calibration.json` | the residual `ARL_0` errors, and whether they are small enough for the `3%` detector sub-gate `G4-D` to mean anything |
| 10 | `src/rebaseguard_p8/chain.py` | the drift semantics: a permanent mean shift enters as a **one-time** reference-error offset, because the reference re-centres. If that reading of P7's convention is wrong, every delay number is wrong |

## 16. Known weak points, stated by Claude

1. **`P8-T1` rests on a `PARTIAL` premise** (P4's abstract theorem) whose
   analytic hypotheses P8 assumes rather than verifies. Every `rho_c` in P8 is
   `THEOREM_CONDITIONAL_ON_PARTIAL_PREMISE`.
2. **Two detector families that are close relatives.** Any detector-invariance
   statement means *these two*; `ADVERSARIAL_REVIEW.md` `A14` concedes this.
3. **No stationarity outside the Gaussian core.** Every non-Gaussian chain
   number is a 50-cycle post-burn-in average, never a stationary quantity.
4. **`t3` is on the third-moment boundary** and its standard errors are not
   trustworthy. Its exclusion from `G4` is pre-declared and conservative
   (including it enlarges the spread), but it is an exclusion.
5. **The contaminated families do not have unit variance** (1.4 and 1.8), by
   Stage-D's frozen construction, so `k = 1/2` is not the same design point
   there. The ARL match removes the first-order consequence, not the confound.
6. **The `H2` family is exploratory**, formulated after four cells were seen.
7. **An unresolved upstream discrepancy is inherited.** P8's Gaussian SR gain
   is `0.70%`–`0.80%` below P3's at every window, agreeing with P7's independent
   re-measurement instead. Every P8 SR number is anchored on a value that two
   downstream campaigns now measure differently from the priority that owns it.
   P8 does not resolve it and does not own it.
8. **An unexplained seed anomaly.** `G10` passes at exactly its `95%`
   non-`t3` threshold, and all three failures are the same cell (SR /
   `gaussian`) offset by `+0.4%` across every window. The matrix-wide `z`
   distribution has sd `1.26`, so the batch-means SE understates cell-to-cell
   variability at the tightest cells. Cheap to attack: re-run that one cell at a
   third experiment tag.
9. **`G7`'s two failing families are noise.** The uncertainty companion puts
   `contam0.05`'s verdict-flipping "peaks" under 1 SE. The gate still fails and
   is reported failed, but a reader who takes `G7`'s literal count as the
   science will misread it in both directions.
10. **No enclosure, no formal proof, no novelty adjudication.**
11. **The gates were written by the agent that ran the experiments.**

## 17. What would falsify P8's headline claims

| claim | what would break it |
|---|---|
| the phenomenon survives outside the Gaussian core (`G3`) | a single `(D, f, m in {1,2,3,5})` cell with `Gamma_A` lower 95% bound `<= 2` on an independent replay, or a demonstration that `P8-T1`'s hypotheses fail so `Gamma_A` is not a derivative at all |
| the window law fails across distributions (`G4`) | showing the cross-family spread is an artifact of the ARL match, the non-unit contaminated variance, or the frozen Gaussian detector design — e.g. by repeating the matrix with family-optimal detectors and finding the spread collapses |
| the lag-profile diagnosis | an off-by-one in the ring-buffer window extraction in `stopped.py`, which would rotate the profile |
| the cross-priority reconciliation | showing that `Gamma_psipsi` as P8 computes it is not Stage-D's `Gamma_psi`, or that `Gamma_A` is not P4's `Gamma_f` |
| the operational results | showing the one-time-offset drift semantics misreads P7's convention |
| the `E6` diagnosis of P4's failed gate | showing that P8's `409,600`-cycle replication is not comparable to P4's Route B, so the `80.3%` pair-failure rate at `t3` does not describe what P4 faced |
| every SR number | resolving the P3 / P7-P8 SR-gain offset in P3's favour, which would shift every P8 SR `rho_c` by about `0.8%` |
