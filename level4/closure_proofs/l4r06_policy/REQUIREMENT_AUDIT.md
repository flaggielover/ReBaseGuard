# Original L4R-06 requirement audit

## 1. Exact original requirement

The authoritative original 18-row ledger records:

> **L4R-06 — Stability-aware reuse policy with monitoring consequences**

Classification: **MANDATORY**. Historical Stage F, the protected post-closure
audit, and the final global re-audit all retain this row as `PARTIAL`.

It is mandatory because Level 4 requires the stability theory to control an
actual reuse decision and requires the resulting policy to retain useful
monitoring behavior. A theorem, phase map, safe scalar, or reference-error
improvement alone does not satisfy the wording.

## 2. Historical Stage C question and policy

Stage C asked whether reuse could be controlled by the local stability
boundary while retaining alarm-triggering data, avoiding recursive reference
instability, and preserving monitoring performance. It froze

`rho_safe(delta) = clip((1-delta)/(Gamma-1), 0, 1)`

with `delta=0.2` and the certified upper endpoint of the `m=1` Gamma enclosure,
giving the fixed policy `rho=0.02979584394902044`.

Stage C passed its policy-definition, theorem-bridge, reference-stability,
reuse, decomposition, reproducibility, regression, and negative-retention
criteria. It failed only C6 and therefore remains `STAGE-C-PARTIAL`.

## 3. Exact immutable C6 rule

C6 required, for every `Delta` in `{0.25,0.5,1.0,1.5}`, that the paired 95%
confidence interval for

`delay(RBG) - delay(full reuse)`

lie below `0.25 * delay(full reuse)`. The two unfavorable conditions were:

| Delta | RBG delay | Full delay | Difference | Threshold | Historical result |
|---:|---:|---:|---:|---:|---|
| 0.25 | 77.68 | 51.91 | +25.77 | +12.98 | **FAIL** |
| 0.50 | 74.10 | 50.28 | +23.82 | +12.57 | **FAIL** |
| 1.00 | 52.00 | 53.19 | -1.19 | +13.30 | PASS |
| 1.50 | 33.73 | 44.37 | -10.64 | +11.09 | PASS |

C6 compared raw delays at very different in-control alarm rates: full reuse
had cycle ARL about 50 while RBG had about 85. This made short full-reuse delay
compatible with frequent instability-driven alarms. That diagnosis is
scientifically relevant, but it does not rewrite the frozen C6 verdict.

## 4. Stage C.1 later evidence

Stage C.1 froze a new baseline-normalized response

`R_Delta(rho)=E[tau_Delta|rho]/E[tau_0|rho]`

and independently confirmed that the historical fixed RBG policy was
non-inferior to fresh at all four shifts with `epsilon=0.05`. Stage C.1 remains
`STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`, while explicitly preserving Stage C
and C6 as partial/failed.

This supports the metric choice for a later same-requirement campaign. It does
not itself close L4R-06 because it evaluates the historical fixed `m=1` policy
rather than a new `m`-dependent policy with jointly frozen reference and
operational consequences.

## 5. Relevant later results

- Track 1B closes the `m>1` derivative theorem and supports
  `F'_{rho,m}(0)=rho(1-GammaTilde_m)` under its explicit assumptions.
- D4 closes the deterministic local phase map and supplies the frozen
  uncertainty-aware `rho_c(m)` rows.
- The D4 operational overlay shows consequences of reuse at selected cells but
  deliberately has no policy-closure threshold.

## 6. Evidence that is insufficient by itself

- Track 1B theorem closure: no policy outcome.
- D4 phase-map closure: local deterministic stability, not a monitoring-policy
  result and not an operational transition.
- A safe `rho` or positive local margin: no demonstrated monitoring consequence.
- Lower reference MSE: insufficient without an operational endpoint.
- Stage C.1 normalized sensitivity: fixed historical policy and separate scope.
- External validation V3: closes L4R-15, not this requirement.

## 7. Legitimate same-requirement closure evidence

Later evidence can map to L4R-06 only if a pre-outcome-frozen policy:

1. mechanically uses the D4 stability quantity to choose reuse;
2. respects its uncertainty-aware stability margin by construction;
3. improves reference distortion relative to full reuse where clipping acts;
4. improves a pre-specified operational monitoring endpoint relative to full
   reuse where clipping acts;
5. remains non-inferior to fresh in baseline-normalized detection response;
6. triggers no frozen absolute-delay safety contradiction;
7. retains every regime and unfavorable outcome; and
8. passes history, adversarial, reproduction, and repository verification.

Only that joint evidence can support `same_requirement_mapping=true` and
current original L4R-06 `PASS`.
