# Level-4 Priority 8 — independent adjudication

**Authoritative verdict: `P8 = FAIL`.** The P8 campaign contains a substantive,
independently reproducible negative scientific result, but it does not satisfy
its frozen integrity spine. The authoritative gate count is **16 PASS / 5
FAIL**. In addition to the four candidate-reported scientific failures (`G4`,
`G4-D`, `G4-F`, and `G7`), **`G14` fails**. Under the frozen verdict rule, any
integrity-spine failure requires `FAIL`.

This verdict does not erase the surviving evidence. It prevents that evidence
from being represented as a successfully preregistered P8 closure campaign.

## 1. Repository state and authority

The adjudication began at:

```text
HEAD        ffe23a63181e2ff11380768d3c73980de80f94fb
origin/main ffe23a63181e2ff11380768d3c73980de80f94fb
ancestry    identical
```

The only worktree change was the untracked
`level4/closure_proofs/p8_model_class_robustness/` directory. It contained 227
raw files (about 3.6 MB), including 13 Markdown files, 74 result files, and six
focused test files collecting 126 tests. There were no unrelated tracked
changes. Logs and caches are ignored; no file exceeds 10 MB.

The P8 question is genuinely inherited from the P7 F1–F3 handoff and the P6
pre-design X5 exclusion: whether the stopped-selection gain, local boundary,
and operational degradation survive changes in innovation family, detector,
window/convention, and drift pattern. `P8_DEFINITION_AUDIT.md` distinguishes
that priority from historical uses of “P8” as a premise label. I found no
scientific-question redefinition after results.

## 2. Temporal anchor and preregistration

`PREREGISTRATION_TEMPORAL_ANCHOR = PARTIAL`.

Filesystem birth times put `THEORY.md` at 2026-09-01 21:18:16 JST,
`EXPERIMENT_PROTOCOL.md` at 21:19:15, and `CLOSURE_GATES.md` at 21:19:55. The
first located E1 production result was born at 21:32:56. This is supporting
evidence that the theory, protocol, and gates preceded production, but it is
not an independent temporal anchor: the entire directory was untracked, there
was no pre-result commit or externally anchored digest, and the provenance
record was generated only after production.

The provenance record does not hash `THEORY.md`, `EXPERIMENT_PROTOCOL.md`, or
`CLOSURE_GATES.md`. It also records the executable source only after source
changes: `config.py`, for example, was modified at 2026-09-02 01:16:53, after
the production artifacts, while `provenance.json` was last generated at
01:19:44. Consequently the record cannot prove that the current protocol,
constants, grids, or implementation bytes are the bytes used for every result.

There is also a direct frozen-protocol mismatch. `EXPERIMENT_PROTOCOL.md` says
E2 used 250,000 cycles per search evaluation and 2,048,000 cycles for final
verification. The executable and result artifacts use 163,840 and 1,024,000,
respectively; the A2 amendment itself describes the latter verification size.
The current protocol therefore is not an accurate frozen description of the
executed campaign.

These facts do not show that `G4` was fabricated or retuned. They do make the
literal `G14` assertion—no production threshold, constant, or grid changed
after a result existed—unverifiable as frozen and contradicted by the protocol
bytes. The candidate gate code checks current threshold equality, not the
temporal claim in the controlling prose. **The prose controls, so `G14 =
FAIL`.**

## 3. Protocol amendments

| amendment | ordering and change | classification |
|---|---|---|
| A1 | Recorded after a smoke run but before E3/E4 production. E3 changed from 4,000×80 to 2,000×70 and E4 from 8,000×40 to 6,000×24. Estimands, metrics, cells, gates, ladders, and thresholds did not change. | `NONBLOCKING_PRE_RESULT` |
| A2 | Recorded after first-pass SR verification showed misses, including contamination 0.1. It added a 614,400-cycle threshold-refinement phase. The 0.5% G2 threshold and scientific estimands did not change, but the same addressed verification experiment/batch inspected on the first pass was reused after tuning. | `RESULT_DRIVEN` |

A2 is disclosed rather than hidden, but disclosure does not restore holdout
independence. Its stated 1,024,000-cycle verification size also contradicts the
current protocol's 2,048,000. I retain the literal numerical `G2 = PASS`—the
stored final values meet its 0.5% inequality—but treat the procedure defect as
part of `G14`, not as permission to rewrite G2.

## 4. Implementation audit

### Window extraction

`WINDOW_EXTRACTION = EXACT`.

For a ring position immediately after storing observation `tau`, the intended
newest-first addresses are
`(pos - 1 - arange(L)) mod L`, masked by `arange(L) < tau`. This is exactly the
last `min(m,tau)` observations. Independent naive-reference tests cover
`tau<m`, `tau=m`, `tau=m+1`, `m=1`, first and deep alarms, and request/ring
boundaries at 255/256/257 and 4095/4096/4097. Across 1,024 stopped paths, every
window size, and a chain primitive comparison, the maximum numerical
discrepancy was `8.881784197001252e-16`.

### Addressable primitives and row bands

`P8_CRN_IDENTITY = PASS` within the intended paired-comparison scope. Stopped
addresses include family, batch, row block, primitive block and primitive
type; detector/window/convention are deliberately excluded for paired stopped
comparisons. Chain addresses include family, detector, window, cycle,
primitive type and block; reuse fraction, shift, live history, and execution
order are deliberately excluded. Family is not paired. Reviewer tests changed
request size and crossed row/band/block boundaries; existing live-set, cache,
order, and deep-index tests also pass. Endogenous trajectories are not required
to remain equal after their states diverge.

## 5. Theory and exact estimator anchors

`P8-T1 = CONDITIONAL_THEOREM`. The sign convention, location score,
differentiation identity, random truncated denominator, terminal observation,
and factor of `rho` are internally consistent. P8 establishes the pathwise
hypotheses corresponding to P4 1–3, but it inherits P4's partial analytic
bridge and does not discharge the required differentiation/integrability
hypotheses 7–9 for every detector/family/window. The issue is most acute for
heavy-tailed `t3`; batch stability is evidence, not a proof of the theorem's
hypotheses. `P8-L0`, `P8-L1`, and the reset decomposition `P8-T2` are exact
algebra under their stated iid/reset model.

The two estimator anchors are correct:

1. With the degenerate threshold-zero detector, `tau=1`, hence
   `Gamma_A = E[epsilon psi(epsilon)] = 1` for a regular standardized location
   family.
2. For the anchor construction, the sample identity is
   `R_m = (1 - 1/m) * mean(epsilon psi(epsilon))`; its population value is
   exactly `1 - 1/m`, rather than a finite-sample assertion that the sample
   mean itself equals one.

The implementation and independent derivation agree, constraining the score
sign, denominator, window orientation, and normalization.

## 6. Independent numerical reproduction

The reviewer implementation in `experiments/run_independent_adjudication.py`
uses PCG64DXSM, independently coded family draws and scores, independent CUSUM
and SR recurrences, and a separate shift-register window. It does not import
P8 simulator code. All 18 representative Gamma values—six detector/family
cells at `m in {1,5,20}`—are within three combined standard errors of the
production matrix. The full stored matrix mechanically contains all 72
detector/family/window cells.

All 40 preregistered eligible cells and all eight reported `t3` cells at
`m<=5` have lower 95% bounds above two. Thus the measured local-repulsion
phenomenon survives broadly in the tested matrix. The moment-marginal set is
correctly derived from the `t3` tail/moment boundary and is reported rather
than smuggled into G3.

For CUSUM/`t3`/`m=20`, production gives
`Gamma_A=1.9492126 ± 0.0071724` and `rho_c=1.053505`. The independent estimate
is `1.96323 ± 0.02558`, whose interval crosses two. This is the only one of the
72 stored matrix cells whose production point estimate has `Gamma_A<2`, but it
is an extrapolation cell, its theorem hypotheses are not proved, and the
independent interval does not certify attraction. The proper label is
`EMPIRICAL`, not theorem or certified numerical result.

## 7. Window law and detector transfer

The exact preregistered `K(m)=rho_c(m)/rho_c(1)` family spreads are:

| m | all eligible detector/family cells |
|---:|---:|
| 2 | 22.6742% |
| 3 | 36.0208% |
| 5 | 49.2901% |

All exceed the 10% G4 margin. Per-detector distribution spreads are about
22.28%, 34.8–34.9%, and 47.35–47.53%, also above 10%, so G4-F fails. The sole
G4-D miss is `t5,m=5`, at 3.63405% against a 3% bound. These are literal
failures; covariance, multiplicity, or post-hoc narrowing cannot rescue them.

The detector ratios require paired covariance because CUSUM and SR share the
stopped primitive field. After recomputing covariance from paired batch
values, every one of 36 tested Gamma ratios still excludes one, with maximum
deviation 27.5737%. This establishes measured absence of transfer in the
tested cells, not permanent or universal detector non-equivalence. G9 remains
a reporting/no-overclaim PASS.

## 8. P3 and P7 correspondence

P8 reproduces all eight frozen P3 comparison cells under the literal
combined-SE criterion. Its Gaussian SR estimates are systematically 0.70–0.80%
below P3 (`z=-1.75` to `-2.07`) but agree with P7's independent remeasurement
(`z=0.66` to `0.86`). The detector threshold, head start, inclusive stopping,
score, and window conventions align. This is
`KNOWN_PREEXISTING_DISCREPANCY`, plausibly numerical/seed bias but unresolved;
it is not evidence of a new P8 convention defect.

The targeted P7 replay for Gaussian CUSUM, `m=1`, `rho=1`, `Delta=1`, using
6,000 paths × 24 cycles gave mean delay 47.49, median 7, q95 253, and
`P(delay>100)=10.6%`. These are Monte Carlo-consistent with P8
(48.92/7/250/11.0%) and P7 (52.6/7/275/11.4%). The fresh control replay had
mean 50.26.

`R_DELTA_REPAIR = NONBLOCKING_CORRECTION`. The original P8 denominator included
the deterministic `e0=0` transient, producing 0.703. The corrected artifact
uses the post-burn-in E3 in-control denominator and gives 0.976, matching the
frozen P7 estimand. No closure gate depended on the old ratio. This is a
calculation repair, not an estimand change.

## 9. G7: literal result and uncertainty

`G7_LITERAL = FAIL`: four of six families reproduce the declared boundary
verdict, below the required five. The implementation adapts only `m={1,5}` and
four metrics, omitting half of P7's `m` coverage and P7's `R_delta` metric, so
its claim that the P7 test was applied “verbatim” is too strong. The narrowed
adaptation was declared, but cannot be expanded after results to rescue G7.

The post-hoc uncertainty companion performs 96 comparisons. Only one survives
BH at q=0.10: the `t3` CUSUM `m=5` false-alarm comparison at 3.107 standard
errors; the contamination-0.05 flips are below one standard error. Thus the
uncertainty analysis broadly supports the qualitative P7 boundary conclusion
in five families, with one narrow `t3` lead. It does not override the literal
gate.

## 10. Robustness and statistics

The Gamma matrix has no missing cells: six families × two detectors × six
windows. Both conventions are evaluated for those 72 cells, and
`(Gamma_A-Gamma_B)-R_m` is at most `3.833955722343241e-15`. The chain and drift
experiments deliberately use only `m={1,5}`; their 288 drift rows cross two
detectors, six families, two windows, two reuse fractions, and six shift
specifications. High-level prose must not imply that the complete Gamma and
drift factors were fully crossed.

All 27 insufficient-tail labels occur for step `Delta=2`. Step `R_delta`
ranges from about 0.024 to 0.918 at `rho=0` and 0.082 to 1.107 at `rho=1`, so a
single narrower headline range is not universal. Ramp `R_delta` ranges from
0.924 to 1.059 at `rho=0` and 0.926 to 1.038 at `rho=1`. Under the implemented
ramp, `rho=0` pins the entering reference near minus the slope; this is a
first-post-change-cycle interpretation. Four post-change cycles do not
establish long-run ramp accumulation.

The 20 addressable batch means are independent by construction. Normal batch
intervals are useful for the large non-heavy-tail margins, but `t3` has finite
variance with unstable higher moments and slow convergence; its intervals are
fragile. `rho_c` and ratio uncertainty must retain pairing/covariance. Cochran's
Q is `DESCRIPTIVE_ONLY`; it is not a closure test. Practical-equivalence gates
remain literal and multiple comparisons are descriptive except for the
explicit post-hoc BH companion.

## 11. Third seed and E6

A production-sized third SR/Gaussian seed family (`E7_CODEX`, 20 batches × 50
row blocks) gives `Gamma_A(m=1)=17.2981508 ± 0.0217317`. E1 is
17.3266020 ± 0.0147355 and E5 is 17.2391270 ± 0.016053. The third result lies
between them: E1–E7 is 1.084 SE, E5–E7 is -2.185 SE, while E1–E5 is 4.014 SE.
The three-seed inverse-variance mean is 17.288907, with descriptive Cochran
`Q=16.340958` on 2 degrees of freedom. The directional +0.4% anomaly does not
replicate, but seed-level overdispersion persists and the nominal SEs appear
underestimated. I found no evidence that hidden dependence or calibration
coupling is the cause.

The E6 80.3% figure is an E6 design diagnostic for `t3`, not a quantitative
reproduction of P4 Route B. E6 uses 12 × 409,600 cycles; Route B used two ×
240,000, with different replication structure. The larger E6 sample would
naively reduce SE by about 1.3×, but heavy-tail convergence prevents treating
that scaling as validation. The figure must not be used as a P4-comparability
claim.

## 12. Novelty and adversarial review

`NOVELTY = NOT_INDEPENDENTLY_ADJUDICATED`. No new algorithm, novelty, or
priority claim is established. The rejected primary window law weakens, rather
than strengthens, the candidate novelty position.

The candidate's 17-attack self-review is useful disclosure, not independent
evidence. Its R-delta and ramp corrections are valid, and its G7 uncertainty
companion is appropriately separated from the gate. A5 remains conceded rather
than resolved because calibration validation was reused. A14 remains a scoped
empirical detector comparison, not a general detector theorem.

## 13. Literal gate adjudication

| gate | literal evidence | authoritative | candidate matched? |
|---|---|---:|---:|
| G1a | 8/8 P3 Gaussian cells within 3 combined SE | PASS | yes |
| G1b | 6/6 P4 family cells within 3 combined SE | PASS | yes |
| G1c | all six frozen CUSUM ARLs within 1% | PASS | yes |
| G1d | six-family regularity identities meet tolerances | PASS | yes |
| G1e | independent family code agrees with P4 fixed checks | PASS | yes |
| G2 | five stored non-Gaussian SR ARLs satisfy 0.5% inequality | PASS | yes |
| G3 | all 40 eligible lower bounds exceed 2; eight t3 reported | PASS | yes |
| G4 | K spreads 22.67%, 36.02%, 49.29% > 10% | FAIL | yes |
| G4-D | t5/m5 detector residual 3.634% > 3% | FAIL | yes |
| G4-F | every per-detector family spread > 10% | FAIL | yes |
| G5 | maximum batch decomposition error `5.18e-15` | PASS | yes |
| G6 | exact convention remainder error `3.84e-15`; all probabilities present | PASS | yes |
| G7 | 4/6 families, required 5/6 | FAIL | yes |
| G8 | all 24 full-reuse ARLs below 50% of nominal | PASS | yes |
| G9 | comparisons reported and appropriately scoped | PASS | yes |
| G10 | stored independent-seed matrix satisfies literal rates | PASS | yes |
| G11 | all declared drift cells and tail labels present | PASS | yes |
| G12 | pre-status protected-tree manifest has zero differences | PASS | yes |
| G13 | scoped primitive identity and boundary tests pass | PASS | yes |
| G14 | no pre-result source/protocol anchor; E2 protocol contradicts execution; reused calibration validation | **FAIL** | **no** |
| G15 | 131/131 focused tests pass after five reviewer tests | PASS | yes |

Authoritative count: **16 PASS / 5 FAIL**. `G4-X` is a report-only item and is
not one of the 21 PASS/FAIL gates.

## 14. Focused and repository verification

The original focused suite passed 126/126. Five independent window/address
tests were added, and the final focused result is 131/131.

An independent pre-status manifest recomputation found 24/24 declared
protected trees exact, covering 2,011 tracked files. The only intended tracked
file outside P8 is the root status README; after that authorized change, 23
historical trees remain byte-identical and the README difference is disclosed.

Exactly one main repository-wide pass was invoked through
`scripts/verify_level_4.sh`; because it is fail-fast, the not-yet-run downstream
suites were then invoked once each as continuation. Level 1–3 passed 90 tests.
The major Level-4 suites passed with no observed skips: base 290, Stage B 46,
Stage C 48, Stage C1 36, Stage D 72, Stage E 59, Stage F 54, post-closure 18,
D4 18, external V3 75, L4R06 28, and L4R12 26. Four historical suites fail:
novelty 1/18, external V2 2/45, final global re-audit 3/36, and final terminal
closure 4/36.

The same exact failure counts and assertions reproduce from a clean local
clone of the authoritative pre-P8 commit `ffe23a6`. They arise from stale
historical protected-manifest/generated-artifact expectations, especially the
pre-existing `sr_derivative` hash mismatch. P8 caused no repository-wide
regression.

## 15. Limitations and final verdict

The surviving evidence is Monte Carlo evidence with heavy-tail and seed-level
overdispersion caveats. It does not prove hypotheses 7–9 of P8-T1, universal
local attraction/repulsion, detector transfer, P7 boundary transfer, long-run
ramp behavior, formal equivalence, or novelty. The protocol and gate files lack
an independently anchored pre-result digest, and the SR calibration procedure
reused an inspected verification address.

The frozen verdict rule says `PARTIAL_CANDIDATE` is available only when every
correctness/reproduction/integrity-spine gate, including G14, passes. G14 does
not pass. Therefore:

> **`P8 = FAIL`**

## 16. Exact P9 handoff boundary

P9 may use only the following, with the stated evidence tier:

| tier | surviving P8 premise |
|---|---|
| `EXACT_THEOREM` | P8-L0/P8-L1 algebra and P8-T2 reset decomposition under their stated iid/reset definitions; exact convention-A/B truncation decomposition. |
| `CONDITIONAL_THEOREM` | P8-T1, only conditional on the stated P4 analytic/differentiation/integrability hypotheses for the particular detector, family, and window. |
| `CERTIFIED_NUMERICAL` | None created by P8. |
| `EMPIRICAL` | In the measured matrix, broad `Gamma_A>2` at `m<=5`, operational degradation in the declared cells, exact-to-floating implementation identities, and the scoped drift/seed results, all with the caveats above. |
| `NEGATIVE_RESULT` | The preregistered cross-family window-separability law and both sub-gates fail; literal G7 transfer fails; measured detector transfer is absent. |
| `NOT_ESTABLISHED` | Unconditional P8-T1 hypotheses 7–9, detector transfer, P7-boundary transfer, long-run ramp accumulation, the t3/m20 attraction claim as a theorem/certificate, novelty, and any new algorithm. |

P9 must not use the rejected window law, assume detector transfer, or assume
P7-boundary transfer. It must not describe P8 as a successful preregistered
closure campaign. It may cite surviving empirical observations only as a
failed-campaign evidence set within the exact tested scope.
