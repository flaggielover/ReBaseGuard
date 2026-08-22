# Frozen protocol — `m>1` derivative closure proof

**Campaign:** ReBaseGuard Level-4 Closure Proof Campaign, Proof Track 1  
**Freeze date:** 2026-08-22  
**Status:** frozen before new confirmatory numerics  
**Historical Stage D D2.3:** `FAILED`, immutable

## 1. Scientific scope

This campaign addresses only the derivative theorem for the Stage-D Gaussian
CUSUM with an ordinary stopping time and a truncated reuse window. It does not
start the SR theorem, an `m-rho` phase map, a general location-family theorem,
semi-real experiments, external validation, or an overall Level-4 closure
audit.

No file in historical Stage A–F, Level 1–3 closure, `rebaseguard-proof`, or the
pre-existing Lean source may be modified. New artifacts live only below
`level4/closure_proofs/m_gt_1/`, except for a future minimal navigation link if
needed.

## 2. Frozen mathematical object

Under `P_e`, `Z_t` are iid `N(-e,1)`. The detector is the frozen two-sided
CUSUM (`k=1/2`, `h=5`) and

\[
 \tau=\inf\{t\ge1:\max(S_t^+,S_t^-)\ge5\}.
\]

For a fixed positive integer `m`,

\[
 w_m=\min(m,\tau),\quad
 A_m=\frac1{w_m}\sum_{r=0}^{w_m-1}Z_{\tau-r},\quad
 T_\tau=\sum_{t=1}^\tau Z_t.
\]

The update and conditional-mean map are

\[
 E^+=\rho(e+A_m)+(1-\rho)\bar Y_m,
 \quad \bar Y_m\perp\mathcal F_\tau,
 \quad E\bar Y_m=0,
\]

\[
 F_{\rho,m}(e)=E_e[E^+\mid E=e].
\]

Stage A's minimum-dwell map is explicitly out of scope except for the frozen
distinction control.

## 3. Frozen theorem candidate

Define

\[
 \widetilde\Gamma_m=E_0[A_mT_\tau],\quad
 \gamma_r=E_0[\mathbf1_{\{\tau>r\}}Z_{\tau-r}T_\tau],
\]

\[
 C_m=E_0\left[\mathbf1_{\{\tau<m\}}
       (\tau^{-1}-m^{-1})T_\tau^2\right].
\]

The candidate frozen before confirmatory numerics is

\[
 \boxed{F'_{\rho,m}(0)=\rho(1-\widetilde\Gamma_m)},
\]

with the exact decomposition

\[
 \boxed{\widetilde\Gamma_m
       =m^{-1}\sum_{r=0}^{m-1}\gamma_r+C_m}.
\]

Thus the historical scalar identity is predicted to be correct only for the
direct convention-A gain. The historical fixed-lag formula is predicted to be
incomplete by the short-cycle correction `C_m`.

## 4. Allowed assumptions and human proof gate

The theorem may use only:

1. iid standard-Gaussian coordinates under `P_0`;
2. the frozen CUSUM stopping rule and its stopping-time measurability;
3. almost-sure finiteness of `tau`;
4. the stopped Gaussian likelihood-ratio identity;
5. exponential integrability of `tau` and `T_tau` already proved for the
   frozen CUSUM;
6. the finite-lag stopped-coordinate exponential/L2 bounds derived by the same
   geometric-slice argument as the existing terminal-coordinate proof;
7. standard dominated differentiation and finite-sum algebra.

The human proof must explicitly discharge measurability, integrability, the
exchange of derivative and expectation, the `tau<m` case, and the m=1 and rho
endpoint reductions. If it cannot, the theorem becomes `THEOREM-OPEN` and no
confirmatory numerics or Lean work begins.

## 5. Confirmatory numerical design

All simulations use only the frozen detector update from
`level4/src/rebaseguard_level4/frozen.py`; Stage-A conditional-map and
multi-cycle modules are forbidden imports.

### 5.1 Grid and seed separation

- `m = {1,2,5,10,20,50,75,100}`.
- `rho = {0,0.25,0.5,1}` for scaling checks; derivative correspondence is
  primary at `rho=1` and transported by the independently proved exact scaling.
- master seed family `2026082204`.
- Route A entropy: `[2026082204,1,replicate,batch]`.
- Route B entropy: `[2026082204,2,replicate,step_index,sign,batch]`.
- Stage-A/Stage-D distinction entropy: `[2026082204,3,replicate,batch]`.
- fresh/rho check entropy: `[2026082204,4,replicate,batch]`.
- Two independent replicates (`replicate=0,1`) are mandatory.
- Route A and Route B share no seed key. CRN is not used for the primary
  derivative. Paired fresh draws may be used only for the exact rho-scaling
  control and must be labelled as such.

### 5.2 Route A: theorem prediction

For each replicate, simulate `1,000,000` iid ordinary stopped cycles at `e=0`.
Estimate `widetilde Gamma_m` by the sample mean of `A_m T_tau`, its iid standard
error, `Gamma_m^B`, `C_m`, `P(tau<m)`, and the lag contributions. Verify the
sample-level identity `widetilde Gamma_m=Gamma_m^B+C_m` up to floating-point
roundoff. The predicted derivative is `1-widetilde Gamma_m`.

### 5.3 Route B: actual induced map

Use independent stopped-cycle simulations at `+h` and `-h`, each with
`500,000` paths per replicate and step. Pre-specified ladder:

\[
 h\in\{0.1,0.05,0.025,0.0125\}.
\]

For every `h`, report `F(+h)`, `F(-h)`, pointwise standard errors, the central
difference, propagated standard error, discrepancy from Route A, and combined
standard error. The **primary step is `h=0.0125`**. Richardson extrapolation
from `0.025` and `0.0125` is secondary diagnostic evidence only.

### 5.4 Frozen criteria

Primary correspondence passes only if, for every `m`:

1. the inverse-variance pooled primary-step discrepancy is at most three
   combined standard errors;
2. each independent replicate's primary-step discrepancy is at most four
   combined standard errors;
3. the two replicate derivative estimates agree within four combined standard
   errors;
4. all raw step estimates are reported, with none dropped.

Finite-difference behavior passes if the absolute discrepancy shrinks from
`h=0.1` to `0.05` for at least 7/8 `m` values and from `0.05` to `0.025` for at
least 6/8, and the median observed coarse-grid order lies in `[1.25,2.75]`.
Failure of the primary criterion stops the campaign before Lean.

Additional mandatory checks:

- `m=1` exact reduction and numerical identity control;
- exact sample-level rho scaling with paired fresh draws;
- explicit short-cycle probability and correction;
- Stage-A minimum-dwell and Stage-D truncated maps differ at `e=0.1` for
  `m=20,100` by more than five combined standard errors in a `200,000`-path
  audit-only comparison;
- source/import guard against Stage-A map code;
- independent seed-family and raw-result manifest checks.

No threshold, step, seed, grid, or primary route may be changed after exposure.

## 6. Theorem revision rule

Before confirmatory numerics, a mathematical error found during the human proof
may revise the theorem only by replacing this protocol, recording the old hash
and reason, and freezing a new hash before data. After any Route A/B output is
observed, a theorem revision is `POST-NUMERIC`; it cannot be called
pre-registered confirmation and forces at most `MGT1-THEOREM-PARTIAL` unless a
new independently frozen campaign is run. A numerical failure is never rescued
by redefining `Gamma_m`.

## 7. Lean scope and closure rule

Lean begins only after the human theorem is proved and numerical
correspondence passes. The mandatory proof spine is:

1. truncated-window weight/statistic definition and positivity;
2. exact `m=1` reduction;
3. exact rho scaling and endpoint reductions;
4. short-cycle/fixed-denominator algebraic correction;
5. stopped-integral derivative identity under explicit measurable,
   integrable, domination hypotheses, reusing the existing generic bridge;
6. a conditional scalar-gain implication for local slope.

The frozen-CUSUM finite-lag domination proof may remain a human-proved input to
the Lean bridge if it is stated explicitly; no `sorry`, `admit`, new `axiom`,
`unsafe`, or `native_decide` is allowed. `MGT1-THEOREM-CLOSED` requires this
spine to elaborate and pass an axiom audit with only the Mathlib baseline
axioms (`propext`, `Classical.choice`, `Quot.sound`).

## 8. Interval certificate scope

This campaign claims a structural derivative identity, not a new rigorous
numerical inequality for any `m>1`. Therefore a new Arb certificate is not
required for closure. The existing m=1 certificate is regression-checked but
is not relabelled as m>1 evidence. If any new stability/instability inequality
is claimed later, it requires a separately specified outward-rounded
certificate with truncation and discretization error; midpoint collocation is
not sufficient.

## 9. Decision states

The final decision is exactly one of `MGT1-THEOREM-CLOSED`,
`MGT1-THEOREM-PARTIAL`, or `MGT1-THEOREM-FAILED`, using the criteria in the
campaign brief. Overall Level-4 closure is never decided here. Historical D2.3
remains `FAILED` under every outcome.

