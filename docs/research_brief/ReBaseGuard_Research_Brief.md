# ReBaseGuard

**Jingzhe Su**
School of Information and Software Engineering
University of Electronic Science and Technology of China
suzhea0226@gmail.com

*Academic research brief - repository presentation artifact, not a peer-reviewed publication or accepted manuscript.*

## 1. Problem

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
does not imply a detector-independent or distribution-free theorem.

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

## 6. Negative result

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

## 7. Evidence and rigor summary

- **Human theorem:** analytic statements with explicit assumptions.
- **Lean-checked:** compiled formal proof spine for the encoded statements.
- **Arb-certified:** rigorous outward-rounded numerical enclosures for CUSUM
  and the authoritative SR detector.
- **Deterministic certificate:** interval result for the conditional-mean
  skeleton, not the noisy stochastic chain.
- **Empirical evidence:** frozen simulation and semi-real task evaluations.
- **Negative result:** a scoped pre-specified hypothesis not supported under
  its frozen design.

## 8. Limitations

The stronger non-Gaussian extension remains partial. The work is not
detector-independent or distribution-free. Local deterministic results do not
establish stochastic invariant behavior or an operational phase transition.
Semi-real streams do not establish production readiness. The literature audit
supports only a scoped N2 position, not absolute novelty or priority.

## 9. Reproducibility and repository

The repository is internally closed under a pre-specified project checklist;
that designation is not an external standard, publication decision, or
peer-review result. Reproduce the frozen terminal snapshot with
`bash level4/final_level4_closure/reproduce.sh` at tag
`rebaseguard-level4-closed`. Reproduce the later SR certificate with
`bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh`
at tag `rebaseguard-sr-gamma-certified`.

Repository: https://github.com/flaggielover/ReBaseGuard
Research synthesis: `docs/research_synthesis/README.md`
Citation metadata: `CITATION.cff`
License: not yet specified; see `docs/releases/LICENSING_READINESS.md`.
