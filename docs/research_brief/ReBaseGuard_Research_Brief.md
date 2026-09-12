# ReBaseGuard

**Jingzhe Su**
School of Information and Software Engineering
University of Electronic Science and Technology of China
suzhea0226@gmail.com

*Academic research brief - repository presentation artifact, not a peer-reviewed publication or accepted manuscript.*

## 1. Problem and motivation

Sequential drift monitors are commonly described one alarm at a time, but real
systems may repeat the cycle: monitor, alarm, update the reference, and monitor
again. A subtle problem appears when the update reuses observations that
participated in the alarm. Those observations were selected through a
data-dependent stopping event, so they need not behave like fresh reference
data. Their reuse changes the next reference, which changes the next monitoring
cycle, creating recursive selection feedback.

ReBaseGuard isolates this **stopping-selected recursive re-baselining**
mechanism. The project asks how the feedback changes local reference dynamics,
when it becomes unstable in a deterministic conditional-mean description, and
whether a stability-aware reuse rule improves monitored behavior in scoped
experiments.

![Figure 1. Alarm-participating observations update the next reference and recursively affect later cycles.](../../figures/final/figure01_recursive_rebaselining.png)

## 2. Core mechanism

Let `e` denote the current reference error and let `F(e)` be the deterministic
conditional mean of the next reference error. For a reuse fraction `rho`, the
one-observation stopped-selection derivative has the form

```text
F'_rho(0) = rho (1 - Gamma),    Gamma = E_0[Z_tau T_tau].
```

The gain `Gamma` measures how the terminal reused residual covaries with the
stopped path score. If `Gamma > 2`, full reuse makes the zero fixed point
locally repelling in the deterministic mean map. This is a local mathematical
statement, not a claim that the noisy monitoring process is globally or
operationally unstable.

<!-- PAGEBREAK -->

## 3. Main theoretical results

| Result | Evidence | Scoped conclusion |
|---|---|---|
| Gaussian CUSUM derivative | Human theorem + Lean-checked spine | Stopped-selection derivative identity for the frozen detector |
| `Gamma_CUSUM > 2` | Outward-rounded Arb certificate | Local repulsion at full reuse for the deterministic mean map |
| Symmetric two-chart SR derivative | Human theorem + conditional Lean spine | Same stopped-score structure for the authoritative SR model |
| `Gamma_SR > 2` | Post-closure Arb certificate | `Gamma_SR` lies in `[5.800391799508442, 28.781285803081492]` |
| Period-two skeleton | Rigorous deterministic certificate | Locally attracting period-two orbit of the conditional-mean skeleton |
| Finite-window extension | Human theorem + deterministic analysis | Protocol-specific `m`-`rho` local-stability boundary |

![Figure 2. The derivative theorem, human model bridge, and Arb enclosure play distinct roles in the CUSUM instability result.](../../figures/final/figure02_derivative_instability.png)

The Lean formalization checks the encoded differentiation spine and its
algebraic consequences. Human proofs carry stopped change-of-measure,
measurability, tail, integrability, and domination obligations not wholly
discharged in Lean. Arb interval arithmetic independently certifies numerical
enclosures; it does not prove differentiation under the expectation. The SR
certificate is specific to the authoritative symmetric two-chart detector and
does not imply a detector-general or distribution-general theorem.

For a reuse window of size `m`, the authoritative random-window convention
includes an exact short-cycle correction. Its derivative yields a critical
reuse boundary `rho_c(m)`. The full-reuse crossing is bracketed at `m` in
`[70,72]`, but this boundary belongs to a local deterministic map rather than
an operational phase-transition theorem.

<!-- PAGEBREAK -->

## 4. Stability-aware reuse policy

The frozen P3 policy converts the local-stability analysis into a conservative
reuse allowance:

```text
rho_P3(m) = min(1, 0.8 * rho_c,L95(m)).
```

It uses 80% of the simultaneous lower-95% boundary and clips the result at one.
At `m = 1, 20, 70, 100`, its reuse fractions are `0.053642`, `0.245418`,
`0.781994`, and `1.0`.

![Figure 3. P3 follows an uncertainty-aware stability allowance across the four frozen regimes.](../../figures/final/figure05_p3_policy.png)

Under the frozen Gaussian CUSUM policy protocol, P3 improved reference-state
mean-squared error and false-alert burden against full reuse in active regimes,
while passing the primary non-inferiority family. The result is deliberately
scoped: P3 equals full reuse at the saturated `m=100` regime, P2 retains
descriptive advantages at `m=70` and `m=100`, and two secondary stricter
conditions fail. These findings do not establish universal safety or
optimality.

## 5. Semi-real validation

Public sequential streams were evaluated task by task without pooling samples.
The retained campaign record is Stage E `0/3`, V2 `1/3`, and V3 `2/2`, giving
three supporting tasks against two required by the internal protocol.
Unsuccessful tasks remain visible. This is scoped semi-real evidence, not
production deployment validation, and policy behavior remains regime-dependent.

<!-- PAGEBREAK -->

## 6. Negative result on the operational crossing

A pre-specified study asked whether the deterministic full-reuse crossing near
`m=71` produced a corresponding operational transition. It did not: `0/4`
preselected metrics peaked at the crossing and `4/4` were monotone in `log m`
under the frozen Gaussian CUSUM protocol.

![Figure 4. The four monitored operational metrics pass smoothly through the mathematical crossing.](../../figures/final/figure08_negative_crossing.png)

The correct conclusion is narrow: no crossing-localized operational transition
was detected for the frozen grid, shifts, and metrics. It is not a universal
no-effect claim. Keeping this negative result visible prevents the mathematical
boundary from being presented as stronger operational evidence than the study
supports.

## 7. Historical campaign status

The Level-4 programme ran nine numbered campaigns. Their adjudicated verdicts
are immutable and are not rewritten by any successor.

| Campaign | Verdict | Scope of the recorded outcome |
|---|---|---|
| P1, P2, P3 | `CLOSED` | Frozen derivative theorems, the SR derivative result, and the reuse-fraction stability map |
| P4 | `PARTIAL` | Location-family theorem survives review; three preregistered numerical gates remain literally false |
| P5 | `PARTIAL` | Raw-mean identity and fixed-policy ergodicity survive; attraction and universality claims narrowed |
| P6, P7 | `CLOSED` | Safe-rebaselining scope and the operational-degradation consequence |
| P8 | `FAIL` | Cross-family window law rejected; G7 and the temporal-integrity gate fail |
| P9 | `PARTIAL` | Retrospective synthesis survives; several sub-claims conditional or unsupplied |
| P8R, P9R | `CLOSED` | Separate repair lineages behind pre-result anchors; P8 and P9 keep their own verdicts |

<!-- PAGEBREAK -->

## 8. Successor philosophy and the P4 line

A successor is a new campaign declared behind a pre-result temporal anchor that
continues a research line. Supersession means later research continues the line;
it never deletes an earlier campaign and never converts a `PARTIAL` or `FAIL`
into a pass.

![Figure 5. Level-4 chronology and the successor lines that continue it.](../../figures/final/figure09_campaign_lineage.png)

The P4 line, published as historical research branches, illustrates why failed
successors are retained. **P4X** reached 88/96 binding PASS with zero scientific
failures, yet its verdict was overridden to `FAIL` on governance and sampling
integrity: stage-2 top-up sharding executed four unauthorised blocks and
1,000,000 unauthorised paths, and precision attainment held only in expectation.
**P4Y** ran four measurement-architecture pilots and concluded
`P4Y_MEASUREMENT_FEASIBILITY = NOT_FEASIBLE` with `DO_NOT_FREEZE_P4Y`; no P4Y
checkpoint was frozen and no P4Y production ran. The later **P4Z/P4ZA/P4ZB**
line ran in three stages against the unchanged frozen gate, each recording its
own self-verdict: P4Z `P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE` (44/96
adjudicated), P4ZA `P4ZA_INCONCLUSIVE` (92/96, four cells left open rather than
widening the frozen K7 limit), and P4ZB `P4ZB_CLOSED` (96/96 `COVERED_PASS`).
`P4ZB_CLOSED` is the campaign's own self-verdict, not an independently accepted
closure: independent assessment currently reads the line as
`SCIENTIFICALLY_COMPLETE_GOVERNANCE_INCOMPLETE`, with the P4 scientific line
`CLOSABLE_WITH_REMAINING_OBLIGATIONS`. None of these closes P4, which remains
`PARTIAL`.

## 9. O9 certification architecture and governed negative results

The P5X/P5Y line carried the global-dynamics successor into the O9 SR
certification executor, progressing through T1 candidate construction, T2
per-patch certification, T3 whole-cell aggregation, T4 curvature, and T5
one-cell and regional closure. The old cell-313 region of the frozen 316-cell SR
cover exposed a genuine whole-cell curvature obstruction, and four separate
routes to remove it were declared, executed, and falsified.

| Route | Recorded classification | Consequence for the design space |
|---|---|---|
| Curvature successor | `CURVATURE_SUCCESSOR_NUMERICALLY_NOT_CLOSING` | Predeclared kill condition failed at cell 313 for `m = 2, 3, 5` |
| Operator-norm tightening | `OPERATOR_NORM_TIGHTENING_INSUFFICIENT` | Tighter certified norms of the same operator did not close the cell |
| Aux3 third derivative | `AUX3_SR_FEASIBILITY_FAIL` | The augmentation was not feasible under its own governance |
| Endpoint route | endpoint `NOT_CLOSING`, then strip micropilot | Endpoint gate later passed, but the frozen `B_int` line stayed open |

These are governed scientific outcomes, not incidental engineering faults. Each
removed a candidate mechanism from consideration, and together they are the
reason the next successor changed the partition rather than the bound.

<!-- PAGEBREAK -->

## 10. The PS1 partition successor

PS1 is a new additive K1 SR successor campaign. It keeps the theorem target,
drift domain, `m` scope, per-cell `B_cover` budget, precision, and degree
unchanged, and declares one canonical 369-cell partition of the whole domain by
a geometry-only rule (`RHO_CAP`, `r_max = 1/25`) frozen before any successor
result existed. It refines 25 parent cells and replaces the old-313 region with
four deterministic successor cells. The union of successor cells is the original
domain exactly.

![Figure 6. The failed old-313 cover ratios against the certified PS1 successor and control cells.](../../figures/final/figure11_ps1_partition_geometry.png)

The four successor cells each recorded `T5_28_OF_28_PASS`, as did three
certified control cells at parents 150, 275, and 315. Recorded `B_cover` ratios
for the successor cells lie between `0.099` and `0.198` against a frozen limit
of one, where the old cell 313 recorded ratios from `33.4` to `2174.5`. The old
316-cell campaign and its cell-313 failure remain immutable historical evidence
and are not claimed by PS1.

## 11. Cost qualification and production authorization

Requalification on the production unit measured a per-cell mean of 11.94 CPU-h
across 13 real cells, giving a 369-cell projection of 4,413 CPU-h on mean groups
and 4,642 CPU-h on the worst group, against a frozen global cap of 6,600 CPU-h.
The executor reproduced 343/343 cell-patch records bit-identically to the
committed certified records. Topology is `A_AWS_ONLY`; the Vultr host is
`NOT_QUALIFIED_FOR_PS1`. One pre-existing lifecycle-suite assertion fails
because a historical torn-attempt ledger from 2026-09-10 remains in the
namespace; it is byte-unchanged, records zero genuine cells, and is disposed as
`known_pre_existing_only`.

## 12. Exact current closure boundary

![Figure 7. What PS1 has authorized, and what has not been run or closed.](../../figures/final/figure13_ps1_current_boundary.png)

The authoritative classification is `PS1_PRODUCTION_AUTHORIZATION_CLOSED`, with
`AWS_GENUINE_PS1_SR_PRODUCTION_AUTHORIZED_TO_START = YES`. In this published
snapshot the boundary is exact and narrow:

- genuine PS1 production cells = **0**; production has **not started**;
- the full 369-cell genuine production campaign is **NOT RUN**;
- the SR side of K1 is **NOT CLOSED**; K1 is **NOT CLOSED**; P5Y is **NOT CLOSED**;
- `LEVEL4_GLOBAL_CLOSURE = NO`.

Authorization to start is a governance state, not a scientific result. The PS1
production namespace carries an empty result ledger at freeze and the recorded
start command is intentionally not run.

## 13. Evidence and rigor summary

- **Human theorem:** analytic statements with explicit assumptions.
- **Lean-checked:** compiled formal proof spine for the encoded statements.
- **Arb-certified:** rigorous outward-rounded numerical enclosures for CUSUM
  and the authoritative SR detector.
- **Deterministic certificate:** interval result for the conditional-mean
  skeleton, not the noisy stochastic chain.
- **Empirical evidence:** frozen simulation and semi-real task evaluations.
- **Negative result:** a scoped pre-specified hypothesis not supported under
  its frozen design.
- **Governance and temporal integrity:** pre-result anchors, immutability
  checks, and audit records. This is process evidence, never a theorem.

## 14. Limitations

The stronger non-Gaussian extension remains partial. The work is not
detector-general or distribution-general. Local deterministic results do not
establish stochastic invariant behavior or an operational phase transition.
Semi-real streams do not establish production readiness. The literature audit
supports only a scoped N2 position, not absolute novelty or priority. PS1
evidence covers seven certified cells and says nothing about the remaining 362
cells of its declared universe, and its cost figures are projections rather than
measured campaign cost. The Level-4 internal closure designation is a project
checklist outcome, not an external academic standard.

## 15. Next scientific steps

Run the declared 369-cell PS1 campaign under its frozen cap, submit the result
to independent adjudication, and only then consider the SR side of K1. K1
closure, the remaining K2-K5 work, and P5Y closure follow in that order. The P4
line needs independent governance adjudication of the P4Z/P4ZA/P4ZB result: the
K7 instrument lineage, the status of P4X's C4/C5 obligations under P4X's
governance `FAIL`, and a disclosed calibration/production RNG address overlap
inside P4Z. None of these steps is anticipated by the present snapshot.

## 16. Reproducibility and repository

The repository is internally closed under a pre-specified project checklist;
that designation is not an external standard, publication decision, or
peer-review result. Reproduce the frozen terminal snapshot with
`bash level4/final_level4_closure/reproduce.sh` at tag
`rebaseguard-level4-closed`. Reproduce the later SR certificate with
`bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh`
at tag `rebaseguard-sr-gamma-certified`. Check the current presentation with
`python3 scripts/verify_academic_presentation.py --no-diff-check` and
`python3 docs/research_synthesis/verify_synthesis.py --no-diff-check`.

Repository: https://github.com/flaggielover/ReBaseGuard
Research synthesis: `docs/research_synthesis/README.md`
Current successor status: `docs/research_synthesis/PS1_CURRENT_STATUS.md`
Citation metadata: `CITATION.cff`
License: original ReBaseGuard material is Apache-2.0 to the extent owned by the
licensor; third-party material is excluded. See `LICENSE` and
`THIRD_PARTY_NOTICES.md`.
