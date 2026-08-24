# D4 definition and historical correspondence audit

**Audit completed before D4 numerical generation.**

## Historical status firewall

This campaign creates a later, isolated result. It does not modify or
reinterpret any historical decision:

- Stage B: `STAGE-B-CLOSED-RIGOROUS-PERIOD2`
- Stage C: `STAGE-C-PARTIAL`
- Stage C.1: `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`
- Stage D: `STAGE-D-PARTIAL`
- Stage E: `STAGE-E-PARTIAL`
- Stage F: `LEVEL-4-PARTIAL`
- post-closure global re-audit: `LEVEL-4-PARTIAL`
- Stage-D D2.3: `FAILED`
- Stage-D D2.5: `MATHEMATICAL, NOT OPERATIONAL`
- historical D4: `NOT RUN`
- Track 1A: `MGT1-TRACK1A-FAILED`
- Track 1B: `MGT1-TRACK1B-CLOSED`

The authoritative pre-campaign branch was synchronized at
`be160e199229e65d3ea630a59d35434a1433b568`. The claimed 947-check baseline is
verified by the repository verifier before new campaign data are generated.

## Frozen detector and stopping semantics

For both Stage A and Stage D the detector is the reset, symmetric, two-sided
Gaussian CUSUM with allowance `k=1/2`, inclusive alarm threshold `h=5`, and the
terminal observation included.

The agreement stops there for `m>1`.

### Stage A

Stage A suppresses alarms before `m`:

`tau_m = inf{t >= m : alarm at t}`.

Its reuse window always contains exactly `m` observations and has denominator
`m`. Thus its stopped path itself depends on `m`.

### Stage D convention A

Stage D retains the ordinary alarm time

`tau = inf{t >= 1 : alarm at t}`

with no minimum dwell. It then truncates the reuse window:

`w_m = min(m,tau)`,

`S_m = sum_{r=0}^{w_m-1} Z_{tau-r}`,

`A_m = S_m / w_m`.

When `tau<m`, the window is the entire stopped path, `S_m=T_tau`, and the
denominator is `tau`, not `m`. Stage A and Stage D therefore define different
maps for `m>1`; they coincide at `m=1` only. No Stage-A minimum-dwell simulator
or scalar is admissible as D4 primary evidence.

## Exact Track-1B scalar

Let

`T_tau = sum_{t=1}^tau Z_t`.

The theorem scalar is

`GammaTilde_m = E_0[A_m T_tau]`.

The tilde is load-bearing: this is the random-denominator Stage-D convention-A
gain. D4 uses `GammaTilde_m` throughout; shortened prose may say `Gamma_m` only
after explicitly declaring it an alias for this exact object.

Define the fixed-denominator stopped suffix

`B_m = (1/m) sum_{r=0}^{m-1} 1{tau>r} Z_{tau-r}`

and lag terms

`gamma_r = E_0[1{tau>r} Z_{tau-r} T_tau]`.

The historical fixed-denominator lag average is

`E_0[B_m T_tau] = (1/m) sum_{r=0}^{m-1} gamma_r`.

It is not equal to `GammaTilde_m` under convention A when short cycles occur.

## Exact short-cycle correction

Track 1B proves the pathwise decomposition

`A_m T_tau = B_m T_tau + Q_m`,

where

`Q_m = 1{tau<m}(1/tau - 1/m)T_tau^2 >= 0`.

Consequently,

`GammaTilde_m = (1/m) sum_{r=0}^{m-1} gamma_r + C_m`,

`C_m = E_0[Q_m] >= 0`.

D4 reports `C_m` and `P_0(tau<m)` at every frozen `m`. Omitting `C_m`, using a
fixed denominator on short cycles, or enforcing a minimum dwell is a semantic
failure.

## Exact reuse scaling and derivative

The Stage-D affine update is

`E^+ = rho(e+A_m) + (1-rho) Ybar_m`,

where the fresh statistic is centered and independent of the stopped path.
Therefore

`F_{rho,m}(e) = rho(e+E_e[A_m])`

and rho scaling is exact:

`F_{rho,m}(e) = rho F_{1,m}(e)`.

The closed Track-1B theorem gives

`F'_{rho,m}(0) = rho(1-GammaTilde_m)`.

This is a human-proved frozen-CUSUM application plus a compiled Lean algebraic
and conditional analytic spine. Track 1B does not claim an end-to-end Lean
instantiation of every concrete stopped-path measurability and domination
obligation.

## Why historical D2.3 remains failed

Stage D tested a precommitted central difference at step `0.05`; all eight
cells failed its three-combined-SE rule. Later diagnostics showed the expected
one-signed `O(epsilon^2)` truncation pattern, and later closure tracks supplied
the corrected theorem and successful independently frozen correspondence.
Those later facts do not change the historical Stage-D verdict. D4 imports the
closed Track-1B theorem; it does not relabel D2.3.

## Audited sources

- `level4/reports/STAGE_D_REPORT.md`
- `level4/stage_d/STAGE_D_PROTOCOL.md`
- `level4/closure_proofs/m_gt_1/THEOREM.md`
- `level4/closure_proofs/m_gt_1/FINAL_REPORT.md`
- `level4/reports/MGT1_TRACK1A_REPORT.md`
- `level4/reports/MGT1_TRACK1B_REPORT.md`
- `level4/closure_proofs/m_gt_1_track1b/THEOREM.md`
- `level4/closure_proofs/m_gt_1_track1b/LEAN_CORRESPONDENCE.md`
- `level4/closure_proofs/m_gt_1_track1b/results/decision.json`
- `level4/re_audit_post_closure/requirements.json`
