# P8R production plan

**Frozen at the temporal anchor, before any production result existed.** Every
budget is quoted from `src/rebaseguard_p8r/config.py`. The exact commands are in
`COMMAND_MANIFEST.json`, also committed at the anchor; gate `I8` checks that each
one names a script that exists, and every result artifact records its own `argv`
so the two can be compared.

## 1. Ordering

Production may not begin before the anchor commit exists. Within production the
order is forced by data dependencies:

```
0.  make_manifests.py --stage anchor        (pre-campaign, at the anchor)
1.  run_regularity.py                        no randomness at all
2.  run_calibration.py <family> x 6          CAL_SEARCH / CAL_VERIFY_*
3.  run_calibration.py --merge               freezes the accepted thresholds
4.  run_gamma_matrix.py <det> <fam> --tag E1  x 12
5.  aggregate_gamma.py E1
6.  run_gamma_matrix.py <det> <fam> --tag E5  x 12
7.  aggregate_gamma.py E5
8.  run_arl0_check.py
9.  run_independent_repro.py                 needs the E1 matrix to compare
10. run_chain_ladder.py <det> <fam>   x 12    needs E1's rho_c
11. run_drift.py <det> <fam>          x 12
12. derive_resolution.py
13. rng_identity.py ; audit_integrity.py ; derive_verdict.py
14. make_manifests.py --stage final
```

Step 3 is a hard barrier: `experiments/thresholds.py` refuses to resolve an SR
threshold until `results/sr_calibration.json` exists, so no SR production cell
can be generated on a threshold that has not been through the frozen acceptance
ladder.

## 2. Experiments and budgets

| id | experiment | address tag | budget (from `config`) | statistical unit |
|---|---|---|---|---|
| `E1` | stopped-cycle `Gamma` matrix | `p8r/production/gamma_e1` | `E1_BATCHES` × `E1_ROW_BLOCKS` × 4096 cycles per `(D,f)` cell, batches from `E1_BATCH0` | the batch; SE is the batch-means SE over the batches |
| `E5` | independent seed family | `p8r/production/gamma_e5` | identical budget, batches from `E5_BATCH0`, **different tag** | as `E1` |
| `E2` | SR calibration | `p8r/cal_*` | `CALIBRATION_PLAN.md` | the cycle |
| `E3` | in-control reuse ladder | `p8r/production/chain_e3` | `E3_REPLICATES` replicates × `E3_CYCLES` cycles, burn-in `E3_BURN_IN`, for `m in M_CHAIN` | the replicate |
| `E4` | drift / delay | `p8r/production/drift_e4` | `E4_REPLICATES` × `E4_CYCLES`, change at `E4_SHIFT_CYCLE` | the replicate |
| `E6` | independent reimplementation | none (outside the address system) | `E6_REPRO_BATCHES` × `E6_REPRO_PATHS` per checked cell | the batch |
| — | in-control `ARL` re-measurement | `p8r/production/arl0_check` | `ARL0_CHECK_ROW_BLOCKS` × 4096 per `(D,f)` cell | the row block |

`E1` and `E5` are separated by tag, so their primitive fields are disjoint and
their comparison in `S13` is a genuine independent reproduction, not a
re-analysis of one field.

## 3. Cells

`E1`, `E5` and the `ARL` re-measurement cover the full cross:
`config.DETECTORS` × `config.FAMILIES` = 12 cells, each at every `m` in
`config.M_GRID` and both conventions — 72 `(D,f,m)` cells per seed family.

`E3` and `E4` cover the same 12 `(D,f)` cells but only `m in config.M_CHAIN =
(1, 5)`. **That is a declared restriction, not a full cross**, and high-level
prose must not imply that the `Gamma` grid and the drift grid were fully crossed.
`S10`'s frozen rule states the restriction in the rule text itself.

`E4` covers `rho in {0, 1}` × `{in-control, step 0.5/1.0/2.0, ramp 0.02/0.05}` ×
`m in {1,5}` per cell.

## 4. Exclusions

A family whose SR calibration ends `CALIBRATION_FAILED` has no SR threshold. Its
SR cells in `E1`, `E5`, `E3` and `E4` are written with
`status = "EXCLUDED_CALIBRATION_FAILED"` and a reason, so the exclusion is a
visible artifact rather than a missing file. No substitute threshold is ever used.

## 5. Reproducibility

Every production artifact carries the frozen provenance envelope
(`experiments/_common.py`):

```
schema, campaign, generator, argv, git_commit, generated_utc,
environment{python, numpy, scipy, platform, machine},
address_tags, payload_sha256, payload
```

Gate `I10` walks `results/**` and fails on any artifact that lacks the envelope,
names a generator that does not exist, names a generator other than the one
declared in `audit_integrity.GENERATOR_MAP`, or whose stored payload digest does
not match a recomputation. There are no orphan results.

`tests/test_generators_and_inheritance.py` regenerates nothing expensive but
checks the mapping, the digests, the environment records, and that the thresholds
actually used in production are the frozen Stage-D values (CUSUM) or an accepted
P8R calibration (SR).

## 6. The independent reimplementation, `E6`

Frozen cells, declared here before results:

```
(cusum, gaussian)  (sr, gaussian)     the two Gaussian anchors
(cusum, t3)        (sr, t3)           the contested heavy-tail pair
(cusum, contam0.05) (sr, t5)          mid-tail / contaminated controls
```

at windows `m in {1, 5, 20}`, giving 18 comparisons.

The simulator shares nothing with production: `PCG64DXSM` rather than Philox, an
entropy source outside the P8R address system, inline family draws and location
scores rather than `families.py`, its own CUSUM and SR recurrences rather than
`detectors.py`, and a shift-register window rather than the production ring
buffer. It reads production only to compare.

`(sr, t3)` and `(cusum, t3)` at `m = 20` are included **specifically** so that
`S15` has a third, independent interval; that is why `S15`'s frozen rule can
require one.

## 7. If a bug is found after production begins

The frozen procedure, declared here so it cannot be improvised:

1. **Stop.**
2. Characterise whether the bug invalidates the affected results, and say so.
3. **Preserve** the invalid artifacts; do not overwrite them.
4. Write a documented amendment stating what changed and why.
5. If — and only if — the amendment is result-independent and scientifically
   legitimate, create a **new temporal anchor** before rerunning anything.
6. Never silently overwrite a prior result.
7. If the bug was found *because* a result was inspected, disclose that
   explicitly, in those words.

A `--force` flag exists on the cell drivers so that a rerun is deliberate;
without it an existing artifact is left alone and the driver says `SKIP`.
