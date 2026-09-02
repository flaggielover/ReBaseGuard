# Level-4 Priority 8 Repair — independent adjudication

**Authoritative verdict: `P8R = CLOSED`.** The original Priority-8 verdict
remains **`P8 = FAIL`**. P8R repairs P8's temporal-integrity failure; it does
not rewrite, reopen, or replace P8.

This adjudication does not adopt the candidate report unchanged. It corrects a
material but closure-neutral error in the anchored deterministic resolver:
`S10` reversed the meaning of reproducing P7's verdict. The raw P8R chain data
match P7's actual `LOCAL-MATHEMATICAL, NOT OPERATIONAL` verdict in five of six
families, so authoritative `S10 = SUPPORTED`, not the candidate's `REJECTED`.
Both outcomes are admissible under the frozen closure rule; the correction
changes the scientific interpretation, not the temporal repair or closure
mechanics.

## 1. Repository state and exact history

The adjudication began from a clean worktree with local `main`, refreshed
`origin/main`, and `HEAD` all at:

```text
84dcfe953ae6f1e95b144d3d4b1435e457884f17
P8R Checkpoint B: completed repair campaign, CLOSED_CANDIDATE awaiting adjudication
```

The exact single-parent ancestry is:

| role | commit | parent | committed |
|---|---|---|---|
| authoritative P8 adjudication | `5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8` | `ffe23a6...` | 2026-09-02 01:58:55 +09:00 |
| P9 adjudication integration | `a3e3cabc30c4508b866736aeede54db17e5e1fcc` | `5411e2c...` | between P8 and P8R A |
| P8R Checkpoint A | `ee61e240998e468eff66a076226eadc70109f9f5` | `a3e3cab...` | 2026-09-02 10:56:22 +09:00 |
| P8R Checkpoint B | `84dcfe953ae6f1e95b144d3d4b1435e457884f17` | `ee61e24...` | 2026-09-02 14:00:03 +09:00 |

`git rev-list --parents --ancestry-path` shows exactly those three edges and
exactly one commit from A to B. Both P8R commits are unsquashed ancestors of
refreshed `origin/main`. The local remote-ref reflog records A being pushed at
2026-09-02 10:56:45 +09:00 and B at 14:00:15 +09:00. The first production
artifact records 10:57:06 +09:00, after A was pushed. This does not prove every
wall-clock fact by itself, but together with the literal trees and artifact
commits it rules out the alleged anchor being a post-result backfill in the
available repository history.

There is no post-B P8R commit before this adjudication and no evidence of an
amend, rebase, squash, or history rewrite of A or B.

## 2. Temporal anchor authenticity

`TEMPORAL_ANCHOR = VALID`.

The literal tree at Checkpoint A contains:

- `FROZEN_PROTOCOL.md`, `FROZEN_GATES.md`, the scientific question,
  calibration plan, RNG/address plan, production plan, and statistical plan;
- the complete `src/`, `experiments/`, and `scripts/` executable surface;
- the complete ten-file focused test suite;
- the 65-command command manifest;
- the 36-file source manifest and ten-file protocol digest;
- the pre-campaign protected-tree manifest.

The literal A tree contains exactly one path under `results/`:

```text
results/integrity/protected_tree_manifest_pre.json
```

It contains no calibrated P8R thresholds, search/holdout traces, Gamma batch,
Gamma matrix, ARL0 result, chain result, drift result, independent reproduction,
scientific resolution, gate outcome, or verdict. Sixty-two scientific result
artifacts record A as their generator commit. The pre-manifest necessarily
records A's parent because it was generated before A; it is not scientific
evidence.

The only A-to-B modification of an anchored document is the promised
`ANCHOR_COMMIT = ee61e24...` backfill in `TEMPORAL_ANCHOR.md`. That file is
explicitly outside the frozen ten-file protocol digest. No frozen scientific
content changed.

## 3. Digest locks, post-anchor mutation, and protected history

Independent byte hashing, using the manifest's documented
`path + NUL + digest + NUL` aggregate rule, gives:

| lock | files | recomputed at A | recomputed at B | verdict |
|---|---:|---|---|---|
| source | 36 | `2f6c7b1eab3fc3c5d01ead7aa57ed535ee19ade87a6747c36bf11c168c17de99` | same | LOCKED |
| protocol | 10 | `fc2302c3bbbf253d1c04ecaac4974867d2955640637b2359121ae41b8981eaf6` | same | LOCKED |

Every constituent file also matches its recorded digest. The A-to-B diffs for
`src/`, `experiments/`, `scripts/`, `tests/`, `config.py`, frozen protocol,
frozen gates, plans, command manifest, thresholds, budgets, seed namespaces,
and decision rules are empty.

Therefore:

```text
POST_ANCHOR_SOURCE_MUTATION = NONE
RESULT_DRIVEN_AMENDMENT = NONE
```

The protected-tree recomputation covers exactly 3,306 tracked files outside the
P8R namespace. Pre, post, and live aggregates are all:

```text
3f2a6b33ee42f3443c15af6acc01f6e37fc0ba35ef2e4c423694f383aeba9da4
```

There are zero file mismatches. The original P8 tree has 129 files and aggregate
`1ba97b70dc342875e32b1265fb6a207427471d1d408dcf5ffc40c2ed8a66b68a`
both before and after P8R. A direct diff from `5411e2c` to Checkpoint B over the
P8 namespace is empty, and exactly one commit in all refs touches that namespace:
the authoritative P8 adjudication commit. The root README did not change.

## 4. Original G14 root-cause repair

| original cause | independent P8R ruling | evidence |
|---|---|---|
| no pre-result anchor | **REPAIRED** | A is a pushed commit with complete frozen surface and no scientific result |
| declared/executed SR budget mismatch | **REPAIRED** | raw trace is exactly six 262,144-cycle S1 evaluations, three 819,200-cycle S2 evaluations, and one 1,228,800-cycle holdout per non-Gaussian family |
| result-driven A2 amendment | **REPAIRED** | fixed-length search and predeclared retry existed at A; no A-to-B source/rule mutation |
| same verification address reused | **REPAIRED** | all families accepted once at `CAL_VERIFY_1`; `CAL_VERIFY_2` was untouched |
| inadequate protocol/source hashing | **REPAIRED** | independently reproduced source and protocol digests are in A and unchanged at B |

All five causes of P8's G14 failure are repaired. The original P8 scientific
failures are not reclassified as integrity failures and P8 stays FAIL.

## 5. RNG address-class audit

The class name is inside the actual hashed experiment string:
`sha256("p8r/<class>/<name>")[:8]`. The eight anchored tags have pairwise
distinct 64-bit prefixes. At identical remaining coordinates the search,
verify-1, verify-2, and production draws differ. Bare, legacy P8, and malformed
tags raise; asking `_verify` to use the search tag raises `PermissionError`.

Stopped addresses omit detector, window, convention, and lag depth as declared.
Chain addresses omit reuse fraction, shift, drift pattern, and live-set state as
declared. Independent checks across request order, cache clears, live-set masks,
row-band boundaries, and a primitive at index 1,000,000 reproduce exactly.
The independent simulator uses PCG64DXSM with its own SHA-derived entropy,
family code, detector recurrences, and shift-register window; it does not use
the P8R Philox address system.

```text
CAL_SEARCH_VERIFY_DISJOINT = PASS
CAL_PRODUCTION_DISJOINT = PASS
CRN_PRIMITIVE_IDENTITY = PASS
EXECUTION_ORDER_DEPENDENCE = NO
LIVE_SET_DEPENDENCE = NO
```

One anchored identity test contains a tautological shared-prefix comparison,
but the underlying property follows from the address construction and was
checked independently; this is a test-quality defect, not an RNG defect.

## 6. Calibration protocol

Family scope is the six frozen families. CUSUM is never calibrated. Gaussian SR
keeps its frozen threshold and is holdout-checked only. Each of the five
non-Gaussian SR families executes exactly:

```text
S1 search:  batches 1000..1005, CAL_SEARCH, 6 x 262,144 cycles
S2 search:  batches 2000..2002, CAL_SEARCH, 3 x 819,200 cycles
holdout:    batch 7, CAL_VERIFY_1, 1 x 1,228,800 cycles
retry:      none
CAL_VERIFY_2 batch 11: untouched
```

The search is a fixed-length log-log secant with anchored beta bounds, damping,
and multiplier clipping. It has no early stop or best-observed selection. The
returned threshold is the final S2 update. All trace entries use the declared
classes and batches; there is no verification-to-search leakage.

| family | accepted threshold | holdout relative error |
|---|---:|---:|
| Gaussian SR (frozen) | 520.886133602749 | 0.0288% |
| t10 | 633.7817692131832 | 0.1243% |
| t5 | 929.0425928760179 | 0.1214% |
| t3 | 1690.8415125187357 | 0.0676% |
| contamination 0.05 | 6408.0645837792035 | 0.0681% |
| contamination 0.1 | 34317.39159354839 | 0.0518% |

All five non-Gaussian families accepted at their first holdout, below the frozen
0.5% tolerance. No retry address was read.

`CALIBRATION_PROTOCOL = PASS` and `CALIBRATION_LEAKAGE = NONE`.

### Latent `CALIBRATION_FAILED` defect

The disclosed defect is real and slightly broader than the handoff summary. A
reviewer probe replacing an SR cell by the exact
`EXCLUDED_CALIBRATION_FAILED` shape raises `KeyError: 'per_m'` in S6, S7, S7D,
S7F, S8, S9, and S13; for t3 it also raises in S15. The frozen protocol allowed
`CALIBRATION_FAILED`, declared that affected questions would exclude those
cells, and allowed S5 to resolve REJECTED. The implementation would instead be
unable to produce the complete resolution artifact.

The ruling is **`SCOPE_LIMITING`**. The branch was part of the declared
protocol and is not executable as promised, but it carried no observed data,
could not change any accepted threshold or production value, and counterfactual
failure-path executability is not an I1-I13 gate. It does not invalidate this
realised campaign. The frozen source is not patched here.

## 7. Independent scientific reconstruction

### E1 raw batch reproduction

Means and SEs below were recomputed directly from each cell's twenty stored
batch records, not from `aggregate_gamma.py`:

| detector | Gaussian | t10 | t5 | t3 | contam 0.05 | contam 0.1 |
|---|---:|---:|---:|---:|---:|---:|
| CUSUM | 15.8646 ± 0.0196 | 15.4506 ± 0.0207 | 13.3351 ± 0.0630 | 8.5761 ± 0.1056 | 15.5947 ± 0.0485 | 18.1713 ± 0.0700 |
| SR | 17.2570 ± 0.0158 | 17.5117 ± 0.0115 | 16.1575 ± 0.0649 | 11.8682 ± 0.1177 | 18.0386 ± 0.0376 | 20.1216 ± 0.0593 |

Every value and SE equals the committed matrix value. Code inspection confirms
the inclusive post-update alarm, terminal observation, newest-first window,
random denominator `min(m,tau)`, location score sign, detector recurrence,
per-cycle estimator, and batch-means SE. Independent raw-batch recomputation of
the decomposition and convention identities gives the same worst residual,
`4.846600551444702e-15`.

`E1_REPRODUCTION = PASS`.

### E5 and ARL0

All 72 E1/E5 cells agree within three combined SE; all 60 non-t3 cells do too.
The largest absolute z is 2.5388 at CUSUM/t3/m=1, consistent with the disclosed
heavy-tail wobble. This is interval agreement, not equality of seeds.

All twelve production ARL0 cells are within the frozen 1% bound. The worst is
SR/t5 at 0.3452%. CUSUM thresholds match Stage-D D3; Gaussian SR matches its
frozen D1 threshold; the five other SR thresholds match the P8R holdout
calibration. ARL0 production uses the disjoint `PRODUCTION` class.

`E5_REPRODUCTION = PASS`; authoritative `S3 = SUPPORTED`.

## 8. S15: CUSUM/t3/m=20

The raw batch vectors contain 20 E1 batches and 20 E5 batches. The independently
coded simulator was rerun to recover its eight deterministic batch values,
which the committed summary had not retained.

| run | mean | frozen SE | frozen normal upper 95% | t upper 95% | batch-bootstrap upper 95% |
|---|---:|---:|---:|---:|---:|
| E1 | 1.945735 | 0.006562 | 1.958595 | 1.959468 | 1.959002 |
| E5 | 1.965108 | 0.007631 | 1.980063 | 1.981079 | 1.979620 |
| independent | 1.884721 | 0.029468 | 1.942478 | 1.954402 | 1.937460 |

The first two runs remain below two under normal, t, batch bootstrap,
leave-one-batch-out, 10% trimming/winsorisation, and two-/four-batch grouping.
The eight-batch independent run is more fragile: grouping into four two-batch
means gives a t upper bound of 2.0163, and grouping into two four-batch means is
uninformative. E1 and E5 each also contain an individual batch mean above two.

Therefore the frozen rule mechanically resolves `SUPPORTED`, but scientific
trust is **FRAGILE**. t3 is moment-marginal, higher-moment convergence is slow,
the independent run has only eight batches, and aggregation granularity matters.
The strongest defensible claim is **suggestive empirical evidence in the tested
CUSUM/t3/m=20 cell under the frozen normal batch rule**. It is not a theorem,
not a certified numerical result, not established for SR, and not generalised
beyond m=20. SR/t3/m=20 is above two in E1, E5, and the independent run.

```text
S15_FROZEN_GATE = SUPPORTED
S15_STATISTICAL_TRUST = FRAGILE
S15_CLAIM_CLASS = EMPIRICAL_SUGGESTIVE_ONLY
```

## 9. Window law, boundary transfer, and detector transfer

Independent raw-batch reconstruction gives:

- S7 spreads: 22.6661%, 35.9857%, and 49.4018% at m=2,3,5 versus 10%;
- S7D: t5/m=5 is 3.0548% versus the exact 3% bound;
- S7F: all six detector/m spreads range from 22.2858% to 47.9241%, above 10%.

All remain literally REJECTED. The close 3.0548% cell is not rounded into a
pass.

### Authoritative S10 correction

P7's actual source defines `criterion_met = false` as
`LOCAL-MATHEMATICAL, NOT OPERATIONAL`. P8's original resolver correctly used
`reproduces_P7_verdict = not criterion_met`. P8R's anchored resolver instead
sets reproduction equal to `criterion_met`, reversing the meaning.

Applying P7's original meaning to P8R's raw chain ladders gives:

| family | boundary criterion met | reproduces P7's negative verdict |
|---|---:|---:|
| Gaussian | no | yes |
| t10 | no | yes |
| t5 | no | yes |
| t3 | yes | no |
| contamination 0.05 | no | yes |
| contamination 0.1 | no | yes |

Thus authoritative S10 is **SUPPORTED, 5/6**, not `REJECTED, 1/6`. The reported
P8-to-P8R shift from 4/6 to 1/6 was a semantic inversion, not calibration or
seed instability. The bare-max criterion is still scientifically noisy and the
scope is the frozen four-sub-family subset, so this must not be promoted to a
universal boundary-transfer law.

### Detector transfer

The ratio is the ratio of paired batch means. Its SE is recomputed from
`a_i - r b_i`, preserving the covariance induced by the shared stopped field.
All 36 paired 95% CIs exclude one; maximum absolute deviation is 27.7393%.
The independently recomputed median naive-unpaired/paired SE ratio is 1.7649,
not the prose claim of 1.83. That documentation discrepancy does not change any
CI or the authoritative `S12 = REJECTED` result.

The correct claim is **detector transfer measured absent in these 36 tested
cells**, not universal non-equivalence.

## 10. P3/P7 discrepancy, operations, and independent implementation

Gaussian SR at m=1 is 17.2570 ± 0.0158. P7 is 17.2990 ± 0.0382
(`z=-1.017`); P3 is 17.4536 ± 0.0659 (`z=-2.901`). Across m=1,2,3,5 P8R is
within three combined SE of P7 and systematically below P3. Detector,
recurrence, head-start, stopping, score, and window conventions match.

`P3_DISCREPANCY = KNOWN_PREEXISTING_DISCREPANCY`.

All 24 full-reuse chain cells are below half their same-cell nominal ARL0; the
maximum fraction is 0.3011. All 288 drift rows are present and complete; 26 are
explicitly `INSUFFICIENT_TAIL_EVENTS`, which is not a positive tail conclusion.
A deterministic reviewer replay of Gaussian CUSUM/m=1/rho=1 reproduces ARL,
SE, MSE, false-alarm probability, and pooled ACF exactly. A Gaussian
CUSUM/m=1/rho=1/step-1 replay reproduces mean delay 54.4905, SE 1.9972, median
7, q95 293.1, and 747 tail events exactly. Cycle 20 is the first changed cycle;
detectors and windows reset each cycle.

The independent implementation is genuinely separate in RNG, entropy,
families, recurrences, and window data structure. All 18 comparisons lie within
three combined SE; the largest absolute z is 2.3899. It reads production only
to form comparisons.

`S11 = SUPPORTED`; `S14 = SUPPORTED`; `S17 = SUPPORTED`.

## 11. Theory and novelty firewalls

The algebraic decomposition and convention identities are exact under the
stated iid/reset model and reproduce to `4.85e-15`. They do not prove the
differentiation-under-expectation, score-integrability, or stopping-time
integrability hypotheses needed for the derivative theorem. Those hypotheses
are not discharged family-by-family, especially for t3.

`P8R_T1 = CONDITIONAL`.

No P8R artifact claims a universal theorem, certified numerical result, new
algorithm, priority, or novelty. The explicit status remains:

`NOVELTY_STATUS = NOT_ESTABLISHED`.

## 12. Authoritative gate table

### Integrity gates

| gate | authoritative status | independent basis |
|---|---|---|
| I1 | PASS | valid A tree, complete frozen surface, no scientific result |
| I2 | PASS | ten-file protocol digest reproduced |
| I3 | PASS | 36-file source digest reproduced |
| I4 | PASS | trace and address classes show no search/verification overlap |
| I5 | PASS | calibration and production tag spaces disjoint |
| I6 | PASS | frozen prose unchanged from A |
| I7 | PASS | `config.py` byte-identical to A |
| I8 | PASS | 65 anchored commands and scripts present |
| I9 | PASS | structural and independent primitive-identity checks pass |
| I10 | PASS, caveat | all 62 scientific artifacts have valid generator, argv, A commit, environment, and payload digest |
| I11 | PASS | 3,306/3,306 protected tracked files identical |
| I12 | PASS | anchored suite 72/72 |
| I13 | PASS | budgets independently reconstructed from raw trace |

I10's checker does not actually enforce every field named in its gate statement
and exempts all integrity artifacts. Two manifested integrity commands (the
integrity audit and final protected manifest) do not use the common envelope.
This is a self-audit enforcement gap. It is nonblocking here because every
scientific artifact was independently checked and the integrity artifacts are
verified directly by Git, hashes, or rerun outcomes. Future repair work should
make the gate statement and executable scope agree.

### Scientific questions

| question | authoritative status | note |
|---|---|---|
| S1 | SUPPORTED | 8/8 P3 Gaussian comparisons within 3 combined SE |
| S2 | SUPPORTED | 6/6 P4 cells; score implementation agrees |
| S3 | SUPPORTED | 12/12 ARL0 errors below 1% |
| S4 | SUPPORTED | all regularity identities within frozen bounds |
| S5 | SUPPORTED | five non-Gaussian thresholds accepted at verify-1 |
| S6 | SUPPORTED | 40/40 eligible lower bounds above two; t3 excluded both ways |
| S7 | REJECTED | spreads 22.67/35.99/49.40% exceed 10% |
| S7D | REJECTED | t5/m=5 is 3.055% versus 3% |
| S7F | REJECTED | all six spreads exceed 10% |
| S7X | OUT_OF_SCOPE | m=10,20 reported, not gated |
| S8 | SUPPORTED | worst exact residual 4.85e-15 |
| S9 | SUPPORTED | worst exact residual 4.85e-15; all probabilities present |
| S10 | **SUPPORTED** | authoritative correction: 5/6 reproduce P7's negative verdict |
| S11 | SUPPORTED | 24/24 full-reuse ARLs below half nominal |
| S12 | REJECTED | 36/36 paired CIs exclude one |
| S13 | SUPPORTED | 72/72 all cells and 60/60 non-t3 within 3 combined SE |
| S14 | SUPPORTED | 288/288 rows; 26 insufficient-tail labels |
| S15 | SUPPORTED | frozen mechanical rule; statistical trust fragile |
| S16 | SUPPORTED | known pre-existing P3/P7 discrepancy |
| S17 | SUPPORTED | 18/18 independent comparisons within 3 combined SE |

Authoritative scientific count: 15 SUPPORTED, 4 REJECTED, 0 INCONCLUSIVE,
1 OUT_OF_SCOPE. Every mandatory question has an admissible resolution.

## 13. Tests and repository regression

The anchored P8R focused suite passes `72/72` with two NumPy warnings. No frozen
test was weakened. No reviewer test was added to the frozen `tests/` directory;
doing so would itself change the anchored source digest. Independent reviewer
probes covered anchor inventory, digest recomputation, result envelopes,
address separation, deep-address identity, calibration budgets, the failed
calibration branch, raw S15 vectors, corrected S10 semantics, protected history,
and deterministic operational replays.

The single final repository sweep produced:

| suite | result |
|---|---:|
| frozen Level 1-3 | 90 passed |
| Level-4 Stage A | 290 passed |
| Stage B | 46 passed |
| Stage C | 48 passed |
| Stage C.1 | 36 passed |
| Stage D | 72 passed |
| Stage E | 59 passed |
| Stage F | 54 passed |
| post-closure | 18 passed |
| D4 | 18 passed |
| novelty | 17 passed, 1 historical failure |
| external V2 | 43 passed, 2 historical failures |
| external V3 | 75 passed |
| final global re-audit | 33 passed, 3 historical failures |
| L4R-06 | 28 passed |
| L4R-12 | 26 passed |
| terminal closure | 32 passed, 4 historical failures |

The four failing suite trees, their generators, and the implicated historical
`sr_derivative` tree are byte-identical to both `5411e2c` and pre-P8R
`a3e3cab`. The failure counts and assertions match the authoritative P8
adjudication baseline. P8R introduced no repository-wide regression.

## 14. Limitations and final synthesis

The strongest defensible result is:

- temporal integrity and all five G14 repair obligations are repaired;
- local repulsion survives empirically across the 40 eligible tested cells;
- magnitude is non-universal and the window-separability law is rejected;
- P7's negative operational-boundary verdict transfers on the frozen subset in
  five of six families, after correcting the candidate's semantic inversion;
- detector transfer is measured absent in the 36 tested comparisons;
- P7-like operational degradation reproduces in all declared chain cells;
- CUSUM/t3/m=20 attraction is frozen-gate-supported but statistically fragile;
- P8R-T1 remains conditional and novelty is not established.

The latent failed-calibration branch, S10 candidate inversion, I10 enforcement
gap, tautological RNG assertion, detector-transfer prose rounding, lack of
per-path production archives, t3 higher-moment behaviour, and historical P3/P7
discrepancy are all explicit. None changes a frozen threshold, leaks a holdout,
alters raw production evidence, or leaves a mandatory realised question
unresolved.

Therefore the Priority-8 lineage is represented as:

```text
P8  = FAIL
P8R = CLOSED
```

P8R may be treated as closure of the Priority-8 **repair lineage**, not as a
retroactive closure of P8. `LEVEL4_GLOBAL_CLOSURE` remains `NO`.

The next recommended Level-4 action is a separately anchored P9 repair/synthesis
checkpoint that consumes this authoritative P8R adjudication, uses corrected
S10 semantics, preserves P8=FAIL, and does not promote S15, P8R-T1, detector
transfer, or novelty. Any future executable reuse should first repair the
`CALIBRATION_FAILED` resolver path and align I10's code with its prose in a new
anchor; neither frozen P8R checkpoint should be amended.

```text
P8_ORIGINAL_VERDICT = FAIL
FINAL_P8R_VERDICT = CLOSED
TEMPORAL_REPAIR_ANCHOR = VALID
PRE_RESULT_PROTOCOL_FREEZE = PASS
SOURCE_DIGEST_LOCKED = PASS
PROTOCOL_DIGEST_LOCKED = PASS
POST_ANCHOR_SOURCE_MUTATION = NONE
RESULT_DRIVEN_AMENDMENT = NONE
CAL_SEARCH_VERIFY_DISJOINT = PASS
CAL_PRODUCTION_DISJOINT = PASS
CRN_PRIMITIVE_IDENTITY = PASS
CALIBRATION_PROTOCOL = PASS
LATENT_FAILURE_PATH_DEFECT = SCOPE_LIMITING
S15_FROZEN_GATE = SUPPORTED
S15_STATISTICAL_TRUST = FRAGILE
WINDOW_LAW = REJECTED
DETECTOR_TRANSFER = MEASURED_ABSENT_IN_TESTED_CELLS
P8R_T1 = CONDITIONAL
P3_DISCREPANCY = KNOWN_PREEXISTING_DISCREPANCY
PROTECTED_TREE = PASS_3306_OF_3306_IDENTICAL
NOVELTY_STATUS = NOT_ESTABLISHED
SCIENTIFIC_CORE = SUPPORTED_WITH_EXPLICIT_LIMITATIONS
LEVEL4_GLOBAL_CLOSURE = NO
AUTHORITATIVE_STATUS_RECOMMENDATION = P8R_CLOSED_ADVANCE_TO_SEPARATELY_ANCHORED_P9_REPAIR_SYNTHESIS
```
