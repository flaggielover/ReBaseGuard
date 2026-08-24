# L4R-06 policy campaign design audit

## 1. Considered policy forms

### Selected — uncertainty-aware continuous clipping

`rho_P3(m)=min(1, 0.8*rho_c,L95(m))`

This is the primary design. It uses the lower 95% D4 confidence bound and a
frozen 20% margin. It is mechanically `m`-dependent, continuous up to the unit
cap, and does not optimize observed monitoring performance.

### Rejected — binary reject/reuse

Setting `rho` to zero or one according to a stability test is simple but
unnecessarily discontinuous and discards admissible partial reuse.

### Rejected — nominal-cap adaptation

`min(rho_nominal,0.8*rho_c,L95(m))` introduces an extra arbitrary nominal cap
that could be confused with performance tuning. No such degree of freedom is
needed.

The D4 point-estimate version is omitted entirely. If ever computed for
description, it is exploratory and cannot affect closure.

## 2. Architecture

The campaign has five isolated units:

1. `policy`: imports the frozen D4 lower confidence limits and deterministically
   reconstructs P3.
2. `simulator`: implements the frozen Gaussian CUSUM multi-cycle semantics for
   `m>1` with shifts at cycle boundaries. At `Delta=0` it must reproduce the
   existing multi-cycle oracle exactly.
3. `campaign`: runs resumable policy/regime/shift cells and stores aggregate
   per-replicate checkpoints without raw paths.
4. `analysis`: performs joint paired cluster-bootstrap inference and derives
   H6-1 through H6-5 without qualitative override.
5. `finalization`: generates figures, decision JSON, reports, adversarial
   records, and reproduction checks from final JSON only.

No historical module is edited. No Lean work is needed because the algebraic
bridge is already closed and the new result is a policy/consequence campaign.

## 3. Frozen policies and regimes

| Policy | Definition | Role |
|---|---|---|
| P0 | `rho=0` | fresh comparison |
| P1 | `rho=1` | full-reuse comparison |
| P2 | `rho=0.0297958439` | historical fixed-policy comparison |
| P3 | `min(1,0.8*rho_c,L95(m))` | sole closure policy |

| m | D4 lower 95% rho_c | Exact P3 | Display P3 | Role |
|---:|---:|---:|---:|---|
| 1 | 0.06705273502486477 | 0.05364218801989182 | 0.053642 | historical Stage-C / strongly unstable full reuse |
| 20 | 0.3067722549504311 | 0.24541780396034488 | 0.245418 | clearly unstable full reuse |
| 70 | 0.9774919431834009 | 0.7819935545467208 | 0.781994 | near D4 full-reuse boundary |
| 100 | 1.2827906445813966 | 1.0 | 1.000000 | clearly stable saturated control |

At `m=100`, P3 equals P1 because the general clipping formula saturates. This
is not a special case. It remains in every table and detection gate, but is not
misrepresented as an improvement comparison against itself.

## 4. Frozen numerical design

- Gaussian symmetric two-sided CUSUM, `k=0.5`, `h=5`, inclusive terminal
  observation, minimum dwell `tau>=m`, Convention A window
  `w=min(m,tau)` (equal to `m` under minimum dwell).
- 200 independent replicate clusters per cell.
- 200 change events per replicate.
- 300 in-control burn-in cycles.
- 15 in-control spacing cycles between change events.
- shifts `{0,0.25,0.5,1.0,1.5}`.
- identical design for every policy and regime; no cell-specific increases.
- common random numbers pair policies, regimes, and shifts by replicate index.
- 10,000 joint nonparametric bootstrap resamples of replicate indices.
- all primary intervals are familywise simultaneous within their frozen family.

The sample size is fixed from the historical Stage C.1 sizing ladder: 200 x
200 achieved estimated standard error below 0.02 at `m=1`, one fifth of the
new primary non-inferiority margin. No new outcome-blind or outcome-aware
sizing run is performed.

## 5. Frozen endpoints and decision flow

- Reference endpoint: in-control `E[e_prev^2]` per replicate.
- Operational endpoint: in-control cycle ARL; higher ARL means lower false-alert
  burden and is interpreted only together with detection-response gates.
- Detection endpoint: `R_Delta(rho)=E[tau_Delta]/E[tau_0]` within policy.
- Absolute safety endpoint: `Q_Delta=E[tau_Delta|P3]/E[tau_Delta|P0]`.
- Secondary diagnostics: reference bias/SD/ACF1, direction ACF1, raw delays,
  P2 contrasts, and the `epsilon=0.05` sensitivity table.

H6-2 and H6-3 apply to the clipping-active regimes `{1,20,70}`. H6-4 and the
absolute safety guard apply to all 16 positive-shift `(m,Delta)` conditions,
including the saturated `m=100` control.

## 6. Error handling and negative outcomes

Missing cells, duplicate seeds, non-finite values, protocol/hash mismatch,
simulator disagreement at `Delta=0`, historical mutation, or figure source
coupling are engineering/integrity failures. Scientific gate failures yield
`L4R06-POLICY-PARTIAL`, not threshold changes or reruns. P2 dominance, P3
near-fresh behavior, detection degradation, or failure of an active regime is
reported without rescue.

## 7. Testing strategy

Focused tests cover source hashes, exact policy arithmetic, saturation,
stability margins, frozen policies/regimes/seeds, simulator equivalence,
shift semantics, paired simultaneous inference, joint decision logic,
historical immutability, same-requirement mapping, figures, and reproducer.
The adversarial suite contains exactly A1–A23 from `PROTOCOL.md`.
