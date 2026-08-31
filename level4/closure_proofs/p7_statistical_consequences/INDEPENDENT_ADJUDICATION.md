# P7 independent adjudication

```text
FINAL_VERDICT                  = CLOSED
RHO_C_STATUS                   = LOCAL_MATHEMATICAL_BOUNDARY_ONLY
P4_DEPENDENCY                  = NONE
P7_REGRESSION                  = NONE
```

This verdict closes the scoped P7 statistical-consequences campaign. It does
not prove a stationary law, global nonlinear stability, an operational optimum,
or a safe reuse policy.

## 1. Baseline, scope, and integrity

Adjudication began with local `HEAD` and `origin/main` both at
`38875fd1fa8a1274b0a6f5ef014619deaf04676f`. The only untracked campaign was
`level4/closure_proofs/p7_statistical_consequences/`; there were no staged or
tracked changes. All adjudication edits remain inside that namespace.

P1--P3 are the authoritative scientific basis. P4 remains `PARTIAL` and is used
only for the supplementary SR Monte Carlo diagnosis in section 9. No P7 result
requires P4 to be closed.

## 2. Monitoring semantics

The implementation matches the closed Stage-D/P1--P3 object:

| item | adjudicated meaning | result |
|---|---|---|
| entering error | `e_j = R_j - mu` before cycle `j`; in control `z_t ~ N(-e_j,1)` | PASS |
| stopping/alarm | first post-update inclusive crossing, `tau >= 1`; terminal observation included | PASS |
| reuse window | last `w=min(m,tau)` innovations, denominator `w`, including `tau<m` | PASS |
| update | `e_(j+1)=rho(e_j+zbar_m)+(1-rho)fresh`, `fresh~N(0,1/m)` independent | PASS |
| reset | both detector arms, lag buffer, and cycle clock reset; only reference carries forward | PASS |
| CUSUM/SR | frozen recurrences, thresholds, no SR headstart, plus-arm priority on ties | PASS |
| initialization/indexing | `e_0=0`; stored array column 0 is cycle 1 | PASS |
| shift | `+Delta` is `e -> e-Delta` at the start of the measured shifted cycle | PASS |
| censoring | `max_steps` raises; it never truncates an observation | PASS |

The CUSUM chain is bit-identical to frozen Stage D, and convention-A stopped
statistics are bit-identical for both detectors. No silent semantic mismatch was
found.

The delay experiment measures the first post-shift cycle. Its entering reference
was built from pre-change observations. Changed observations are included in the
post-alarm reference for the *next* cycle, but do not contaminate the entering
reference of the reported delay. Candidate wording that attributed the measured
tail to changed-observation contamination was corrected.

## 3. Central statistical conclusion

Recursive re-baselining causes large monitoring degradation in the frozen
Gaussian repeated-cycle regime, but the P3 local critical fraction does not mark
an operational cliff under the precommitted grid criterion.

The two controls must remain separate. At `rho=0`, every new reference is an
independent estimate with error `N(0,1/m)`. Therefore its cycle length is a
mixture `E[A(e)]`, not the calibrated `A(0)`. Since the measured response falls
steeply away from zero, fresh-reference estimation alone reduces ARL. This is a
real matched-information/reset-reference effect, not reuse and not burn-in.
At `rho=1`, stopping-selected terminal-window reuse adds further dispersion and
dependence.

Production results and the independent seed `20260917` replay agree:

| quantity | production | independent replay |
|---|---:|---:|
| nominal `A(0)` | CUSUM 465.12; SR 464.86 | first-cycle 447–492 at `n=2500` per family |
| fresh `rho=0` ARL | 79.91–162.03 | 78.92–164.12 |
| full reuse `rho=1` ARL | 48.36–80.05 | 47.73–80.40 |
| full reuse loss vs nominal | 82.8%–89.6% | reproduced |
| full reuse loss vs fresh | 39.5%–50.6% | reproduced |
| fresh `FAP(100)` | 0.619–0.823 | 0.615–0.823 |
| full reuse `FAP(100)` | 0.822–0.899 | 0.821–0.900 |
| full reuse alarms/1000 | 12.49–20.68 | consistent |

The nominal `FAP(100) ~ 0.19` is a separate single-cycle baseline; the campaign
does not estimate it from the chain. Reuse-attributable statements use the
same-`m` fresh control, not nominal calibration.

## 4. Detection-delay tail

The identity-route full-reuse mean for `Delta=1` is 50.54–66.06 across all
eight families (the candidate's 52.8 lower endpoint omitted SR `m=1`). Nominal
means are 10.35 (CUSUM) and 11.01 (SR). Direct production validation covered
eight detector/window/reuse/shift cells without censoring; maximum absolute
z-score was 2.36 and maximum relative gap 2.9%. No `A(e-Delta)` sample fell
outside the corrected `|x|<=12` grid, whose extreme response is already near
the minimum possible run length.

The independent replay confirms a heavy right tail rather than uniform
slowdown:

| cell | mean ± SE | median | q95 | `P(delay>100)` |
|---|---:|---:|---:|---:|
| CUSUM `m=1,rho=1` | 54.12 ± 0.90 | 7 | 292 | 0.1180 ± 0.0019 |
| SR `m=5,rho=1` | 61.37 ± 0.96 | 10 | 311 | 0.1327 ± 0.0020 |

For CUSUM, 10.0% of entering references were within 0.2 of the post-change
mean. Their mean delay was 347 and 75.2% exceeded 100, versus mean 21.6 and 4.8%
outside that region. The analogous SR figures were 11.7%, mean 337, 73.1%,
versus mean 24.7 and 5.3%. Thus the tail mechanism survives an independent seed
family, with the corrected causal description: pre-shift reference dispersion
occasionally masks the shift.

## 5. Finite-cycle result

The production cycle-1 ARL is 456.70–473.54 under full reuse, near nominal.
Cycle 2 is 5.60–9.35, a roughly 98% collapse. Independent replay gives 447–492
for cycle 1 and 5.7–9.5 for cycle 2 across all eight families.

There is no off-by-one error. Cycle 1 enters at fixed `e_0=0`; its alarm then
constructs cycle 2's reference. At `rho=1`, that reference is made entirely from
the stopping-selected terminal window, producing an extreme entering error and
near-immediate next alarm. Later alternation and nonlinear saturation partially
recover to the post-burn-in 48–80 range. This is a transient observation, not a
global nonlinear theorem. Comparing cycles 12–49 with 30–49 changes ARL by at
most 1.41% over 104 cells.

## 6. Critical boundary and local radius

`EXPERIMENT_DESIGN.md` fixes the eight-rung ladder, five metrics, and 4-of-8
threshold. Its filesystem timestamp precedes the production chain result by 17
minutes and the final derived boundary result by more than an hour. Because the
campaign was uncommitted, this is provenance evidence rather than a
cryptographic preregistration, but no contrary version or selective family
omission was found.

The implementation uses all eight detector/window families and both adjacent
brackets `0.8–1.0` and `1.0–1.25`; it performs no interpolation. Counts are:

| metric | families peaking at boundary | required |
|---|---:|---:|
| ARL | 2/8 | 4/8 |
| reference MSE | 3/8 | 4/8 |
| `FAP(100)` | 1/8 | 4/8 |
| reference ACF1 | 0/8 | 4/8 |
| `R_Delta` at `Delta=1` | 3/8 | 4/8 |

The literal negative-result criterion therefore fails to support an operational
boundary. The exact conclusion is: **`rho_c` is a local mathematical boundary
only in this observed regime under this fixed point-estimate/grid criterion.**
This is not proof that no other operational metric, design, or finer experiment
could show a feature.

`r_lin=0.05` is not a proved mathematical radius. It is a grid-defined empirical
diagnostic: the largest tested radius where the response slope stays within 10%
of the P3 tangent. Comparing it with empirical RMS is dimensionally valid because
both are reference-error scales. The corrected ratios are 8.1–27.4 over all
cells and 8.2–18.9 at the eight exact `rho=rho_c` cells, not the candidate's
11–21 claim. The conclusion that the observed chains are far outside the local
neighbourhood survives strongly.

## 7. Theory adjudication

| statement | final status |
|---|---|
| P7-A | **Exact finite-cycle conditional theorem.** Given entering `e_j`, reset state, and iid innovations, `E[tau_j]=E[A(e_j)]` and the first shifted-cycle mean is `E[A(e_j-Delta)]`. `E_pi` notation is conditional on existence/integrability of `pi`; stationarity is not needed for the finite-cycle identity. Global strict monotonicity of `A` is not proved. |
| P7-B | **Conditional exact proposition.** The ACF identity holds for a stationary symmetric law with finite nonzero second moment and centered independent fresh noise. The zero-dispersion limit needs an additional second-moment concentration/uniform-integrability condition. Empirical maximum gap is 0.00714; pooled ACF has no replicate-level interval. |
| P7-C | **Conditional proposition, not a global stability theorem.** The mass-escape inequality additionally assumes `e h(e)<=0` on the stationary support. That sign is supported on the response grid but not proved globally. It does not prove existence, uniqueness, ergodicity, saturation, or causal absence of a boundary feature. |
| P7-D | **Conditional algebra plus Monte Carlo plug-in diagnostic.** It also needs a finite fourth moment and monotonicity of `A`. Inputs and assumptions lack simultaneous interval propagation, so the former “certified deficit” wording was removed. The point plug-in reaches 21.5% and is not numerically violated, but is not certified or load-bearing. |
| candidate P7-E | **Rejected.** `d E[e_1]/d epsilon` does not determine `d E[M(e_1)]/d epsilon` when `e_1` remains random. A distributional derivative or score identity would be required. |

Stationary-law existence, uniqueness, ergodicity, finite second/fourth moments,
and burn-in convergence are evidenced only by finite simulation. Main finite
cycle results and P7-A do not require stationarity. Quasi-stationary summaries,
P7-B/C/D, and `E_pi` language do.

## 8. Reproducibility and statistical audit

No scientific seed calls Python's randomized `hash(str)`. Fixed integer detector
codes feed `SeedSequence`; production (`20260831`), campaign adversarial
(`20260901`), and independent adjudication (`20260917`) families are distinct.
Two independent-adjudication reruns produced byte-identical JSON.

The replicate is correctly used for ARL, MSE, FAP, bootstrap, and normal
intervals. Normal/bootstrap ARL interval widths differ by at most 2.91%.
Path-level pseudo-replication was not found for those claims. Limitations:

* pooled ACF1 is not accompanied by replicate-level uncertainty;
* boundary peak counts use point estimates, as the frozen criterion specifies;
* ratio bootstrap approximates the independent denominator by its normal
  sampling law instead of resampling its saved replicates;
* the statement that no multiplicity correction is “needed” is too broad, but
  the large C1 effect, descriptive C3 identity check, and negative C2 criterion
  are not materially changed by this wording;
* finite fourth moments cannot be inferred merely because sample fourth moments
  are finite.

CRN is used only within response-curve grid points and when a measured entering
law is evaluated for shifts. Chain cells at different `rho` use independent
streams. No z-score treats the four correlated `m` estimates as independent.

## 9. SR discrepancy and P4 supplementary evidence

P7's 2-million-path SR gains are 0.9%–1.1% below frozen P2/P3, with combined
z-scores -1.94 to -2.26 across four correlated windows, and agree with Stage-D
`d1_gamma`. P4's independent 1.6-million-path replay of the frozen P2
implementation agrees with P4 at 1.26–1.49 combined SE and found no recurrence,
threshold, or window mismatch. The historical P2 vector is therefore consistent
with a correlated high Monte Carlo realization. Its frozen values remain
unchanged. A roughly 1% `rho_c` shift cannot alter a boundary result whose fixed
criterion peaks at only 0–3 of 8 families. This discrepancy is not material to
P7 and does not require P4 closure.

## 10. Closure gates

The campaign script's eleven gates are the literal closure matrix. The script is
not sufficient by itself: gates 1 and 7 conflate weak mechanical checks with
scientific validity, while gates 9–11 check file presence. Independent review
supplies the substantive evidence below.

| # | gate | status | independent evidence |
|---:|---|---|---|
| 1 | definition correspondence with P1–P3 | PASS | source audit, bit identity, shift/window/reset tests |
| 2 | CUSUM and SR evidence | PASS | 104 production cells plus independent replay |
| 3 | attraction/boundary/repulsion comparisons | PASS | all eight ladder rungs in all eight families |
| 4 | uncertainty-aware ARL evidence | PASS | replicate intervals; bootstrap/normal width gap <=2.91% |
| 5 | false-alarm and delay evidence | PASS | production plus independent tail replay; no censoring |
| 6 | finite-cycle evidence | PASS | 50 production cycles; independent cycle-1/2 replay |
| 7 | honest bridge or declared boundary | PASS | bridge narrowed as in section 7; unsupported P7-E rejected |
| 8 | focused tests | PASS | 31 passed |
| 9 | adversarial review | PASS | original attacks checked; independent seed/causal/theory attacks added |
| 10 | P5/P6/P8 scope boundaries | PASS | explicit handoffs; no downstream work started |
| 11 | no unsupported causal/novelty claim | PASS | contamination, certification, stability, and causality wording corrected |

All gates are applicable; none is `NOT_APPLICABLE`. The failed operational
boundary hypothesis is a precommitted negative result permitted by the protocol,
not a positive-result closure requirement.

## 11. Repository verification and protected trees

Focused P7: **31 passed**.

`bash scripts/verify_level_1_3.sh`: **PASS**, zero skipped. The Level-4 verifier
passes the frozen 90, Stage A 290, B 46, C 48, C.1 36, D 72, E 59, F 54,
post-closure 18, D4 18, external V3 75, L4R-06 28, and L4R-12 26 tests.

One pre-existing/environment-dependent freeze-manifest defect prevents a wholly
green Level-4 command: old historical manifests freeze directory contents before
later closed additions to `level4/closure_proofs/sr_derivative` and also count
ignored/generated files. It produces 1 novelty, 2 external-V2, 3 global-reaudit,
and 4 terminal-closure failures through one root cause. Current HEAD tracks 92
files where the novelty manifest expects 52. A detached clean worktree at
authoritative HEAD, with no P7 directory, independently fails the same protected-
history test (an earlier environment-dependent `stage_e` count fails first).
The frozen checks were not weakened or rewritten. Exact results are in
`results/repository_verification.json`.

There are zero tracked changes to P1–P4 or any other protected tree. Therefore
repository verification finds no P7 regression.

## 12. Claims narrowed and handoffs

Corrections made during adjudication:

1. delay-tail causality changed from changed-observation contamination to
   pre-shift reference dispersion;
2. full-reuse mean-delay range corrected to 50.54–66.06 across all families;
3. exact-boundary dispersion ratio corrected to 8.2–18.9;
4. `r_lin` labelled empirical/grid-defined rather than mathematical;
5. P7-B limiting conditions made explicit;
6. P7-C/D made conditional and non-causal;
7. “certified” removed from the P7-D Monte Carlo plug-in diagnostic;
8. candidate P7-E rejected;
9. boundary verdict limited to the fixed observed criterion;
10. P6 language changed from proved control principle to motivated hypothesis.

P5 should test the hypothesis
`local repulsion -> escape from the local region -> nonlinear high-dispersion
regime -> quasi-stationary law`, without presuming a bifurcation, period-2 orbit,
multiple attractors, or global instability.

P6 should investigate control of the entering-reference distribution and delay
tails (`q95`, `P(delay>L)`) rather than treating `rho<rho_c` as a safety rule.
The exploratory ARL maximum near `rho=0.14–0.25` remains exploratory and is not
a recommended operating point or universal optimum.

## 13. Remaining limitations

Results cover only frozen Gaussian two-sided CUSUM and two-chart SR,
`m in {1,2,3,5}`, `rho in [0,1]`, and a shift applied at a re-baselining instant.
There is no stationary-law theorem, rigorous interval layer, Lean spine,
detector/distribution robustness matrix, persistent post-change chain analysis,
or safe-policy result. The precommitment provenance is filesystem-based because
P7 was not committed before production. These limitations do not defeat the
literal P7 closure gates or the central empirical conclusion.
