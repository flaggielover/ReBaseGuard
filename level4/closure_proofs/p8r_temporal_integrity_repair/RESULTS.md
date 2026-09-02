# P8R results

**Candidate verdict: `P8R = CLOSED_CANDIDATE`.** 13/13 integrity gates pass;
all 20 mandatory scientific questions are resolved — 14 `SUPPORTED`, 5
`REJECTED`, 1 `OUT_OF_SCOPE`.

**This is a candidate. It is not authoritative and must not be promoted to
`CLOSED` without independent adjudication.**
`AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION`.

**`P8 = FAIL` is unchanged, authoritative, and not under review here.** Every
byte of the P8 namespace is identical to its pre-campaign manifest.

---

## 1. The temporal anchor

```
ANCHOR_COMMIT     ee61e240998e468eff66a076226eadc70109f9f5
ANCHOR_TIMESTAMP  2026-09-02T10:56:22+09:00
pushed to         origin/main before any production result existed
SOURCE_DIGEST     2f6c7b1eab3fc3c5d01ead7aa57ed535ee19ade87a6747c36bf11c168c17de99  (36 files)
PROTOCOL_DIGEST   fc2302c3bbbf253d1c04ecaac4974867d2955640637b2359121ae41b8981eaf6  (10 files)
PROTECTED_TREE    3f2a6b33ee42f3443c15af6acc01f6e37fc0ba35ef2e4c423694f383aeba9da4  (3306 files)
```

`git ls-tree -r ee61e24` shows exactly one path under `results/`: the
pre-campaign protected-tree manifest. Every production artifact records a
`git_commit` that descends from the anchor. This is the thing P8 did not have.

## 2. Integrity gates — 13/13 PASS

| gate | result |
|---|---|
| `I1` anchor carries protocol + source + tests, no production result | PASS |
| `I2` frozen prose byte-identical to the anchored digest | PASS |
| `I3` executable surface byte-identical to the anchored digest | PASS |
| `I4` no search evaluation read a verification address | PASS |
| `I5` no production address coincides with a calibration address | PASS |
| `I6` no frozen prose changed after the anchor | PASS |
| `I7` `config.py` byte-identical to its anchor blob | PASS |
| `I8` every production command recorded verbatim (65) | PASS |
| `I9` every primitive a pure function of its address (6 checks) | PASS |
| `I10` every result has a working generator and a matching payload digest | PASS |
| `I11` every protected tree byte-identical | PASS |
| `I12` focused suite 72 passed, 0 failed, 0 skipped | PASS |
| `I13` executed calibration budget == declared budget | PASS |

## 3. Calibration — the repaired procedure

Every non-Gaussian SR threshold was accepted on `CAL_VERIFY_1`, **at the first
attempt**. `CAL_VERIFY_2` was never read. No family ended `CALIBRATION_FAILED`.

| family | `A_f` | holdout `ARL_0` | rel. error | outcome | P8's `A_f` |
|---|---:|---:|---:|---|---:|
| gaussian | 520.886134 | 465.638 ± 0.436 | 0.029% | `FROZEN_NOT_RECALIBRATED` | 520.886134 |
| t10 | 633.781769 | 464.925 ± 0.420 | 0.124% | `ACCEPTED_VERIFY_1` | 633.1015 |
| t5 | 929.042593 | 464.939 ± 0.422 | 0.121% | `ACCEPTED_VERIFY_1` | 929.2356 |
| t3 | 1690.841513 | 465.819 ± 0.426 | 0.068% | `ACCEPTED_VERIFY_1` | 1676.9657 |
| contam0.05 | 6408.064584 | 465.821 ± 0.413 | 0.068% | `ACCEPTED_VERIFY_1` | 6384.8204 |
| contam0.1 | 34317.391594 | 465.745 ± 0.430 | 0.052% | `ACCEPTED_VERIFY_1` | 34119.1682 |

Executed budget, re-derived from the stored trace: 6 S1 evaluations of 262,144
cycles and 3 S2 evaluations of 819,200 cycles per family, one holdout of
1,228,800 cycles. Identical to the declared budget — which is the specific
comparison P8 never made.

Search addresses were `("cal_search", 1000..1005)` and `("cal_search",
2000..2002)`; the holdout was `("cal_verify_1", 7)`. The two sets are disjoint,
and the class strings sit inside the hashed address, not beside it.

## 4. The scientific matrix

`Gamma_A(m=1)`, 4,096,000 cycles per cell, batch-means SE over 20 batches:

| | gaussian | t10 | t5 | t3 | contam0.05 | contam0.1 |
|---|---|---|---|---|---|---|
| CUSUM | 15.865 ± 0.020 | 15.451 ± 0.021 | 13.335 ± 0.063 | 8.576 ± 0.106 | 15.595 ± 0.049 | 18.171 ± 0.070 |
| SR | 17.257 ± 0.016 | 17.512 ± 0.012 | 16.158 ± 0.065 | 11.868 ± 0.118 | 18.039 ± 0.038 | 20.122 ± 0.059 |

### `S6` — regime survival: SUPPORTED

All 40 eligible cells have a lower 95% bound above 2; the smallest is **6.697**.
The 8 `t3` cells are reported in full and counted in neither direction; every one
of them also exceeds 2 at `m <= 5` (lower bounds 3.753 to 11.637).

**Local repulsion of full reuse survives broadly across the tested matrix.**
This is the one substantive positive finding, and it is empirical, scope-bound,
and consistent with what P8 measured.

## 5. What was rejected — the negative results

### `S7` — the window-separability law `H1`: REJECTED

Relative spread of `K(D,f,m) = rho_c(m)/rho_c(1)` across the 10 eligible `(D,f)`
cells, against a frozen 10% bound:

| m | spread | min K | max K |
|---:|---:|---:|---:|
| 2 | **22.67%** | 1.2151 | 1.4905 |
| 3 | **35.99%** | 1.3632 | 1.8538 |
| 5 | **49.40%** | 1.6214 | 2.4225 |

P8 measured 22.67%, 36.02%, 49.29% on an independent seed namespace. The
agreement to three significant figures is itself notable: the rejection is not a
noise artifact of either campaign.

`K` is **not** a function of `m` alone. The window factor is family- and
detector-dependent, and increasingly so as `m` grows.

### `S7D` — detector invariance of `K`: REJECTED

The single failing cell is **`t5`, `m=5`**, at a 3.055% residual against a 3.0%
bound. Every other one of the 15 comparisons is inside. P8's single failing cell
was also `t5`, `m=5`, at 3.634%.

This is a narrow, reproducible miss, and it should be read as such: the residual
is 3.055% against 3.000%, and the next-worst cell (`contam0.05`, `m=5`, 2.993%)
is inside by less than a hundredth of a percent. The frozen rule is literal and
the result is `REJECTED`; a reader who wants to know *how badly* invariance
fails should look at `S7F`, not here.

### `S7F` — family invariance of `K`: REJECTED

Per-detector spreads across the five eligible families:

| m | CUSUM | SR |
|---:|---:|---:|
| 2 | 22.29% | 22.46% |
| 3 | 35.08% | 34.92% |
| 5 | 47.52% | 47.92% |

All six exceed the 10% bound, and the two detectors agree closely on *how much*
they exceed it — the family dependence is the dominant effect and it is nearly
detector-independent. That is a sharper statement than `S7D` supports on its own.

### `S10` — P7 boundary transfer: REJECTED, more strongly than in P8

P7's criterion reproduces in **1 of 6** families (`t3` only); the frozen rule
requires 5.

| family | reproduces | hits by metric (`arl`/`ref_mse`/`fap100`/`e_acf1`) |
|---|---|---|
| gaussian | no | 0 / 0 / 0 / 0 |
| t10 | no | 1 / 0 / 1 / 0 |
| t5 | no | 0 / 0 / 0 / 0 |
| t3 | **yes** | 2 / 0 / 3 / 1 |
| contam0.05 | no | 0 / 0 / 0 / 0 |
| contam0.1 | no | 0 / 0 / 0 / 0 |

P8 reported 4 of 6. P8R reports 1 of 6 on an independent field. Both fail the
gate, but the disagreement between them is itself informative: P7's criterion is
a bare `max` over brackets with **no uncertainty margin**, applied here at half
P7's resolving power (4 sub-families per family, not 8), and it evidently flips
easily between seed realisations. The right reading is that the criterion is
**unstable at this resolution**, not that P8R has measured a smaller transfer
than P8 did.

The descriptive BH companion (72 comparisons at `q = 0.10`, `DESCRIPTIVE_ONLY`,
never part of the gate) rejects the null in 40 of them, which says the bracket
rates do differ — not that the boundary is where P7 placed it.

### `S12` — detector transfer: REJECTED

All 36 `(family, m)` ratios `Gamma_A(cusum)/Gamma_A(sr)` exclude 1 at 95%, using
the CRN-paired linearised SE. Maximum deviation **27.74%**.

| cell | ratio | paired SE | naive SE | batch corr. |
|---|---:|---:|---:|---:|
| gaussian, m=1 | 0.9193 | 0.00087 | 0.00141 | 0.643 |
| t3, m=1 | 0.7226 | 0.00506 | 0.01142 | 0.823 |
| t3, m=5 | 0.8042 | 0.00303 | 0.00713 | 0.825 |

The pairing matters: the median naive/paired SE ratio is **1.83**, so an
independent-SE interval would be roughly twice too wide. That would not have
rescued transfer — the deviations are far larger than either interval — but
using the wrong formula here is precisely the correction the P8 adjudication had
to apply by hand, and P8R does it in the frozen plan instead.

**Detector transfer is measured absent in the tested cells.** That is not a
proof of permanent or universal non-equivalence, and nothing here says otherwise.

### `S7X` — `m in {10, 20}`: OUT_OF_SCOPE

Reported, never gated. Spread 50.73% at `m=10`. Outside P3's supported window
grid by construction, and excluded from `S7`/`S7D`/`S7F`'s evidence — a test
asserts that no `m in {10,20}` cell appears there.

## 6. Reproduction and correctness

| question | result |
|---|---|
| `S1` P3 Gaussian, 8 cells | **8/8** within 3 combined SE. CUSUM `z` in `[-1.58, -0.60]`; SR `z` in `[-2.90, -2.47]` |
| `S2` P4 families, `m=1` CUSUM | **6/6** within 3 SE (`z` in `[-1.30, +1.41]`); independent score implementation matches P4 to `8.88e-16` |
| `S3` in-control ARL at the frozen thresholds | **12/12** within 1%; worst 0.345% (SR/t5) |
| `S4` regularity identities | `E[eps psi] - 1` max `7.86e-06`; `E[psi]` exactly 0; Fisher vs Stage-D max `1.51e-08` |
| `S8` decomposition identity | max absolute residual `4.85e-15` against a `1e-9` bound, 72 cells |
| `S9` convention identity | max absolute residual `4.85e-15` against `1e-12`, all `P(tau<m)` present |
| `S13` seed sensitivity `E1` vs `E5` | **72/72** cells within 3 combined SE — 100%, against required 90% / 95% |
| `S17` independent reimplementation | **18/18** within 3 combined SE, max `|z| = 2.39`, zero outliers |

`S11` operational degradation: all 24 chain cells have `ARL` at `rho = 1` below
half the same-cell nominal; the worst is 30.1% (CUSUM/`t3`/`m=5`), the best 22.2%.

`S14` drift reporting: all **288** declared rows present and complete, 0 cells
excluded, **26** rows labelled `INSUFFICIENT_TAIL_EVENTS` (P8 had 27 of the same
288). Labelled, not dropped.

## 7. The `t3` / `m=20` cell — `S15 = SUPPORTED`, and what that does and does not mean

This is the one place P8R's frozen rule yields a **stronger** statement than P8
was willing to make, so it is stated carefully.

| | `E1` | `E5` | independent |
|---|---|---|---|
| CUSUM `Gamma_A` | 1.9457, CI [1.9329, 1.9586] | 1.9651, CI [1.9502, 1.9801] | 1.8847, CI [1.8270, 1.9425] |
| upper bound < 2 | yes | yes | yes |
| SR `Gamma_A` | 2.2605, CI [2.2463, 2.2748] | 2.2770, CI [2.2617, 2.2922] | 2.2436, CI [2.1816, 2.3056] |
| upper bound < 2 | no | no | no |

The frozen `S15` rule — upper 95% bound below 2 in `E1` **and** `E5` **and** the
independent reimplementation — is met, **for CUSUM only**. P8's independent
estimate for this cell was `1.963 ± 0.0256`, whose interval crossed 2, so P8
correctly declined to certify it. P8R's three intervals all exclude 2.

**What this is:** three independently-seeded measurements, one of them from an
independently written simulator, agreeing that `Gamma_A < 2` for the frozen
CUSUM chart on `t3` innovations at a 20-observation reuse window.

**What this is not, and must not be reported as:**

* It is **not** a theorem. `P8R-T1`'s differentiation and integrability
  hypotheses are not established for `t3` — this is the family where they are
  least defensible.
* It is **not** a certified numerical result. P8R creates none.
* It is **not** a statement about SR, which shows `Gamma_A ≈ 2.26 > 2` in the
  same cell, i.e. the opposite regime under the other detector. Given `S12`, that
  is what one should expect.
* It is **not** inside the campaign's own gated scope. `m = 20` is
  `EXTRAPOLATION_BEYOND_P3`; `S7X` is `OUT_OF_SCOPE` for exactly this reason.
* The three intervals are **not** three independent kinds of evidence about the
  tail. All three are normal-approximation batch-means intervals on a
  `MOMENT_MARGINAL` family whose sample variance has infinite variance. They can
  be too narrow *together*, and a common bias would not show up as disagreement
  between them. This is a real weakness of the rule, and it was frozen before the
  answer was known.

`CODEX_HANDOFF.md` attack 11 directs an adjudicator to re-derive this cell from
the raw per-batch vectors. That is the right response to it.

## 8. `S16` — the P3 / P7 discrepancy: `KNOWN_PREEXISTING_DISCREPANCY`

P8R's Gaussian SR gain against both prior measurements:

| m | P8R | vs P3 | vs P7 | relative to P3 |
|---:|---:|---:|---:|---:|
| 1 | 17.2570 ± 0.0158 | `z = -2.90` | `z = -1.02` | −1.13% |
| 2 | 14.3566 ± 0.0130 | `z = -2.47` | `z = -0.55` | −0.99% |
| 3 | 12.8321 ± 0.0112 | `z = -2.80` | `z = -0.52` | −1.08% |
| 5 | 10.9271 ± 0.0092 | `z = -2.89` | `z = -0.62` | −1.10% |

P8R agrees with P7 at every `m` and sits systematically about 1% below P3 —
the same sign and shape P7 and P8 both reported, slightly larger in magnitude
(P8 measured −0.70% to −0.80%). The frozen decision table therefore returns
`KNOWN_PREEXISTING_DISCREPANCY`, **not** `NEW_DEFECT_CANDIDATE`.

Three campaigns on three independent fields now measure this quantity below the
priority that owns it. P8R does not own the P3 numbers, does not adjudicate
them, and does not resolve the discrepancy. It records a third independent
measurement for whoever does. Every P8R SR quantity inherits it.

## 9. Theory status

`P8R-T1 = CONDITIONAL_THEOREM`, unchanged and unchangeable by this campaign.
The reference-map derivative `rho (1 - Gamma_A)` follows from P4's abstract
stopped-score theorem **conditional on** its differentiation-under-expectation,
score-integrability and stopping-time-integrability hypotheses, which are assumed
per family, not verified. Simulation agreement is not a discharge.

The exact algebraic identities are separate and are established: `S8` and `S9`
both hold to `4.85e-15`, i.e. to floating point. They are exact algebra under the
stated iid/reset model and must not be cited as evidence for the conditional
theorem's analytic hypotheses.

## 10. Novelty

`NOVELTY_STATUS = NOT_ESTABLISHED`. No independent novelty review was run, and a
repair campaign does not generate novelty. Zero direct hits, the absence of a
known transfer law, a new negative result and a new empirical matrix are
explicitly not evidence of it.

## 11. Protected tree

```
pre  aggregate 3f2a6b33ee42f3443c15af6acc01f6e37fc0ba35ef2e4c423694f383aeba9da4
post aggregate 3f2a6b33ee42f3443c15af6acc01f6e37fc0ba35ef2e4c423694f383aeba9da4
```

**Identical.** 3,306 tracked files outside the P8R namespace, 22 declared
protected trees, **zero differences** — including the root status files. P8R
made no change anywhere outside its own directory, not even the one root README
change its own gate would have permitted. Updating the repository dashboard is
left to the adjudicator, after adjudication.

## 12. One implementation defect, disclosed not patched

`LIMITATIONS.md` §5 `I1`: `aggregate_gamma.py` writes calibration-excluded cells
without a `per_m` block, and `derive_resolution.py` indexes `per_m`
unconditionally for `S6`, `S7`, `S7D`, `S7F`, `S13` and `S15`. Had any family
ended `CALIBRATION_FAILED`, those questions would have raised `KeyError` rather
than resolving.

No family did, so the path carried no production data and no result depends on
it. It is **disclosed rather than patched**, because patching anchored source
after production is exactly what `I3` and `I7` exist to prevent, and because a
silent fix would be indistinguishable from the amendment that failed P8.

One other note for the record: `tests/test_claim_firewall.py` — anchored source
— rejected an early draft of `LIMITATIONS.md` §6 because two disclaimers
contained an affirmative collocation inside a sentence that denied it. The
disclaimers were rephrased; no claim changed. The firewall is a blunt substring
check by design, and its passing means "no forbidden collocation appears", not
"no overclaim was made".

## 13. Reproducing this

```bash
cd level4/closure_proofs/p8r_temporal_integrity_repair
P8R_JOBS=4 ./experiments/pipeline.sh          # 65 commands, ~2.5 h on 6 cores
python scripts/rng_identity.py
python -m pytest tests -q                     # recorded in results/integrity/focused_tests.json
python scripts/audit_integrity.py
python experiments/derive_verdict.py
python scripts/make_manifests.py --stage final
```

Every artifact under `results/` carries its generator, its verbatim `argv`, its
git commit, its environment and a payload digest that recomputes.

---

```
P8_ORIGINAL_VERDICT        = FAIL   (unchanged, authoritative)
P8R_VERDICT                = CLOSED_CANDIDATE
AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION
```
