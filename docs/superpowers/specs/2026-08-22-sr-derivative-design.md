# Proof Track 2 design: symmetric two-chart SR derivative theorem

**Date:** 2026-08-22

**Track namespace:** `level4/closure_proofs/sr_derivative/`

**Primary route:** stopped-score differentiation

**Arb status in the closure rule:** non-blocking rigor upgrade

## 1. Objective and closure boundary

The sole scientific objective is to derive, validate, and, if the frozen gates
survive, formally close the derivative theorem for the authoritative symmetric
two-chart Shiryaev–Roberts detector under the matched `m=1` reference-reuse
protocol.

The allowed track verdicts are:

- `SR-DERIVATIVE-CLOSED`;
- `SR-DERIVATIVE-PARTIAL`;
- `SR-DERIVATIVE-FAILED`.

`SR-DERIVATIVE-CLOSED` requires definition/code correspondence, a human proof,
independent numerical correspondence, exact symmetry and rho scaling, a
compiled Lean proof spine with a transparent axiom audit, authoritative
repository verification, and unchanged historical artifacts.

An Arb certificate for `Gamma_SR>2` is explicitly not part of that closure
definition. Without Arb, the permitted final classification is:

```yaml
derivative theorem: CLOSED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR instability certificate: OPEN
```

If a sound certificate later succeeds at the authoritative threshold, it adds
`SR-GAMMA-CERTIFIED` without redefining `SR-DERIVATIVE-CLOSED`.

This track does not start an `m`–`rho` map, an SR period-2 certificate, a
general location-family theorem, new external validation, or a global Level-4
re-audit.

## 2. Immutable history

The following states remain unchanged:

- Level 1–3: `CLOSED`;
- Stage B: rigorous deterministic CUSUM period-2 result;
- Stage D: `STAGE-D-PARTIAL`;
- D2.3: `FAILED`;
- Track 1: `MGT1-THEOREM-PARTIAL`;
- Track 1A: `MGT1-TRACK1A-FAILED`;
- Track 1B: `MGT1-TRACK1B-CLOSED`;
- the scoped `m>1` derivative-theorem requirement: `CLOSED`;
- Stage F: `LEVEL-4-PARTIAL`.

Stage D SR artifacts remain read-only. A pre-track manifest records and tests
the hashes of every tracked Stage D and Track 1–1B artifact.

## 3. Authoritative SR detector

The authoritative detector uses the Stage D operating point:

```text
delta = 1
A = 520.886133602749  (natural units)
R_0^+ = R_0^- = 0

R_t^+ = (1 + R_{t-1}^+) exp(Z_t - 1/2)
R_t^- = (1 + R_{t-1}^-) exp(-Z_t - 1/2)

tau = inf {t >= 1 : max(R_t^+, R_t^-) >= A}.
```

Both charts update from the same residual. The alarm is tested inclusively
after both updates. If both charts cross and their post-update values differ,
the larger chart supplies the direction. Exact equality is recorded as a
distinct `TIE` status. Detector statistics reset to `(0,0)` each cycle; the
reference error does not reset except through the matched reuse update.

The implementation may store `Y=log(1+R)`. Its exact equivalent recursion is

```text
log R_t^+ = Y_{t-1}^+ + Z_t - 1/2
log R_t^- = Y_{t-1}^- - Z_t - 1/2
Y_t^+ = softplus(log R_t^+)
Y_t^- = softplus(log R_t^-).
```

The comparison is `log R_t^± >= log A`; `A` is logged exactly once inside the
log implementation. The authoritative displayed decimal is the exact rational

```text
A_decimal = 520886133602749 / 10^12.
```

Parsing it into the Stage D NumPy runtime gives the nearest binary64 value

```text
A_binary64 = 4581762885148045 / 8796093022208
           = 0x1.04716cd36dd8dp+9,
A_binary64 - A_decimal
           = 118479773 / 2147483648000000000000
           ≈ 5.52e-14.
```

Numerical code and any certificate claiming correspondence with that code use
the exact binary64 rational. Reports retain the authoritative decimal label
`A=520.886133602749` and disclose the faithful-rounding distinction. The
derivative theorem itself is proved for any admissible positive threshold.

The older Phase 4B–4D feasibility value `A=520.3125` is not authoritative and
none of its numerical certificate conclusions may be transferred.

## 4. Forcing bound derived from the frozen recursion

The exponential-tail argument uses a bound derived directly from the raw
authoritative recursion.

Every live chart state is nonnegative because it starts at zero and each
update is a positive factor times `1+R`.

For the plus chart, if

```text
Z_t >= log(A) + 1/2,
```

then, line by line,

```text
Z_t - 1/2 >= log(A),
exp(Z_t - 1/2) >= A,
1 + R_{t-1}^+ >= 1,
R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2) >= A.
```

For the minus chart, if

```text
Z_t <= -log(A) - 1/2,
```

then

```text
-Z_t - 1/2 >= log(A),
exp(-Z_t - 1/2) >= A,
1 + R_{t-1}^- >= 1,
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2) >= A.
```

Because the alarm boundary is inclusive, equality also forces a crossing.
Consequently

```text
|Z_t| >= log(A) + 1/2
```

forces at least one chart to alarm from every live state. In log coordinates,
the same proof uses `Y_{t-1}^±=log(1+R_{t-1}^±)>=0`, so the implemented
`log R_t^±` also reaches `log A`. The bound is therefore exactly the correct
one for the frozen raw and log implementations; it is not inherited from the
CUSUM theorem.

For `e` in a compact neighborhood of zero, `Z_t~N(-e,1)`. The forcing event
has a uniformly positive probability, so `tau` is uniformly geometrically
dominated. This supplies a.s. finiteness, exponential stopping moments for a
small positive exponent, and the moment bounds used in the human
differentiation argument.

## 5. Reference-error parameterization

The sign convention is reconstructed from the Stage D code:

```text
X_t = mu + epsilon_t,       epsilon_t ~ N(0,1)
e   = R_j - mu
Z_t = X_t - R_j = epsilon_t - e ~ N(-e,1)
T_tau = sum_{t<=tau} Z_t.
```

At `m=1`, the reused physical observation is

```text
X_tau = R_j + Z_tau,
```

so its error relative to `mu` is `e+Z_tau`. Let `U~N(0,1)` be an independent
fresh-reference error. The matched update is

```text
E_next = rho(e+Z_tau) + (1-rho)U.
```

The conditional-mean map is therefore exactly

```text
F_rho(e) = E_e[E_next] = rho(e + E_e[Z_tau]).
```

This proves exact rho scaling:

```text
F_rho(e)=rho F_1(e),  F_0=0.
```

## 6. Why no explicit SR-state derivative remains

In residual coordinates, the map from a coordinate sequence
`(z_1,z_2,...)` to the chart states, stopping time, terminal residual, and
stopped sum uses only the fixed constants `A,delta` and the coordinate values.
It has no explicit `e` argument. The parameter changes the coordinate law
from `Q_0` to `Q_e`; it does not change that functional.

Thus this track is in the regime

```text
path functional fixed, law varies,
```

not

```text
detector functional itself varies with e.
```

The definition audit must verify this line by line in both implementations.
If an explicit `e` survives after residual parameterization, the theorem
candidate is invalid and the protocol must not freeze until the formula is
revised. A pathwise derivative of the discontinuous hitting time is not used.

## 7. Human theorem route

Let `Q_e` be the law of iid residuals `N(-e,1)`. On the stopped sigma-field,
the Gaussian likelihood ratio relative to `Q_0` is

```text
L_e = exp(-e T_tau - e^2 tau/2).
```

The proof chain is:

```text
F_rho(e)
  -> exact mixed-reference reduction
  -> exact rho scaling
  -> derivative of E_e[Z_tau]
  -> stopped likelihood/score identity
  -> Gaussian score -T_tau at e=0
  -> Gamma_SR = E_0[Z_tau T_tau]
  -> F'_rho(0) = rho(1-Gamma_SR).
```

The forcing bound supplies the SR-specific tail control. Gaussian moments and
the geometric tail provide integrability and a uniform integrable dominator
near zero, justifying differentiation under the stopped expectation.

Reflection sends every residual path to its negative. It swaps the plus and
minus charts at every step, preserves the first alarm time, negates `Z_tau`
and `T_tau`, and preserves their product. Hence `E_0[Z_tau]=0`, zero is a fixed
point, and `F_1` is odd. The theorem is specifically for the symmetric
two-chart construction; a one-sided SR chart does not have this symmetry.

The human theorem target is

```text
Gamma_SR = E_0[Z_tau T_tau],
F'_rho(0) = rho(1-Gamma_SR).
```

If `Gamma_SR>2`, then at full reuse `F'_1(0)<-1`, so the zero fixed point of
the deterministic conditional-mean skeleton is locally linearly unstable.
Without Arb, that inequality remains confirmatory numerical evidence.

## 8. Required execution order

The implementation campaign follows this exact order:

1. repository and hash audit;
2. definition/code audit;
3. freeze and hash `PROTOCOL.md`;
4. write the complete human theorem;
5. classify proof obligations;
6. execute independent numerical correspondence;
7. explicitly declare `NUMERICAL GATE CLOSED — LEAN AUTHORIZED` only if every
   primary gate passes;
8. compile the Lean spine and audit axioms;
9. attempt the non-blocking Arb upgrade at the authoritative threshold;
10. run full verification and decide the track.

Lean cannot begin after a failed numerical gate. Arb cannot begin before Lean.

## 9. Frozen numerical design

### 9.1 Seeds and batches

Fresh master seed `2026082227` is absent from the repository before Track 2.
Seed families are disjoint by route and from all historical science streams.
The statistical unit is the independent batch.

Frozen route identifiers are: calibration/CUSUM target `[master,1,0]`,
calibration search `[master,1,1,iteration]`, calibration final measurement
`[master,1,2]`, fixed-threshold SR/CUSUM checks `[master,1,3-or-4,batch]`, raw
Route A `[master,2,batch]`, paired log Route B
`[master,3,replicate,batch]`, and structural controls with identifiers at least
90. The same path/time stream is intentionally shared across signs and the
entire `h` ladder inside one Route B replicate/batch; no stream crosses a
route, replicate, or batch boundary.

### 9.2 Calibration audit

The threshold used everywhere remains `A=520.886133602749`.

The fresh bisection audit uses natural-unit bracket `[100,3000]`, 200,000
cycles per search evaluation, at most 30 iterations, log-width tolerance
`1e-3`, and a fresh 800,000-cycle final measurement. Its candidate must be
within 2% of the authoritative threshold. This is a blocking
calibration-reproduction sanity check but cannot replace the frozen threshold.

The operating-point check independently measures CUSUM and SR ARL at their
fixed thresholds with 64 batches of 10,000 cycles. The fixed-threshold ratio
must satisfy `|ARL_SR/ARL_CUSUM-1|<=1%`. This is a separate blocking check.

Natural/log-unit tests, the decimal value, and the binary64 value are pinned.

### 9.3 Route A: score/Gamma prediction

An independently written raw-state implementation runs 64 batches of 25,000
cycles, 1.6 million total, with keys `[2026082227,2,batch]`.

It accumulates `tau`, `Z_tau`, `T_tau`, `Z_tau T_tau`, alarm direction, exact
ties, simultaneous crossings, and ARL. It estimates
`Gamma_SR=E_0[Z_tau T_tau]` and predicted derivative `1-Gamma_SR`.

The estimate must agree with historical `17.3198 +/- 0.0280` within four
combined standard errors. Its batch-based 99% lower confidence bound must
exceed two. The latter remains confirmatory numerical evidence.

### 9.4 Route B: direct conditional-map derivative

A separately written log-state implementation imports no Route A theorem or
recursion helper. The frozen ladder is

```text
h in {0.1, 0.05, 0.025, 0.0125}.
```

There are two independent replications. Each uses 64 batches of 12,500 paired
paths per sign and step with keys
`[2026082227,3,replicate,batch]`. Path/time-addressable common random numbers
pair `+h` and `-h` inside a batch.

For every batch and `h`, Route B first forms the paired batch derivative

```text
D_b(h) = (mean_b F(+h) - mean_b F(-h))/(2h)
```

from matched paths. The SE is estimated from the empirical distribution of
the `D_b(h)` values. Separate `+h` and `-h` SEs are never combined as if
independent.

The primary estimator is the central difference at `h=0.0125`. Richardson
extrapolation from `0.025` and `0.0125`, and the observed convergence order,
are secondary diagnostics only. They can neither fail a passing primary
result nor rescue a failing one.

Primary acceptance requires:

1. pooled finest-step derivative versus Route A prediction has `|z|<=3`;
2. each Route B replication has `|z|<=4`;
3. the two Route B replications agree within three combined SE;
4. pooled relative discrepancy is at most 2%;
5. batch identities, path counts, CRN pairing, and seed keys align;
6. Route A and Route B seeds are disjoint; and
7. source-level guards verify implementation separation.

### 9.5 Structural controls and ties

Before the numerical verdict:

- raw and log implementations agree on frozen deterministic paths;
- reflected paths swap charts, preserve `tau`, and negate `Z_tau,T_tau`;
- exact map oddness and rho scaling hold structurally;
- `rho=0`, `rho=1`, and a frozen interior rho satisfy the affine rule;
- simultaneous unequal crossings select the larger post-update chart;
- an injected exact tie returns the separate `TIE` status; and
- confirmatory routes observe zero exact ties.

The continuous Gaussian mathematical model assigns exact ties probability
zero. Every numerical tie is recorded. Any observed confirmatory tie blocks
the gate pending diagnosis; it cannot be silently folded into a direction.

No sample size, threshold, step, criterion, or route may change after outcomes.
Any primary calibration, structural, correspondence, source-separation, or
historical-integrity failure stops before Lean.

## 10. Lean design and analytic boundary

The Lean source will formalize only the high-value spine:

1. a raw two-chart SR state and step;
2. step reflection under state swap and `z -> -z`;
3. symmetry of the inclusive alarm predicate;
4. finite-list first-alarm and terminal-record reflection;
5. terminal signed-statistic negation and product invariance;
6. odd-map and exact rho-scaling algebra;
7. the derivative identity as a consequence of the existing abstract stopped
   differentiation interface under explicit hypotheses;
8. `Gamma_SR>2 -> |F'_1(0)|>1`; and
9. correspondence with the authoritative threshold and convention.

The Lean result is a conditional formal proof spine over explicit analytic
hypotheses. The Lean theorem formalizes the algebraic/stopped-score consequence
under explicit analytic hypotheses; the concrete SR tail, measurability,
a.s. finiteness, integrability, exponential-tail, and domination obligations
remain human-proved. It must not be described as an end-to-end formalization
of the concrete infinite SR process unless those obligations are actually
instantiated in Lean.

The axiom audit compiles with the pinned project, inventories each headline
theorem, scans for `sorry`, `admit`, and project-specific axioms, and records
the exact standard dependencies.

## 11. Non-blocking Arb upgrade

Arb starts only after the Lean gate closes and uses only the exact runtime
rational corresponding to the authoritative displayed threshold
`A=520.886133602749`.

The old Phase 4C/4D work supplies a mathematical architecture, not an
authoritative numerical certificate. Every operator constant, reachable
enclosure, candidate, residual, and resolvent bound must be recomputed at the
Stage D threshold.

`SR-GAMMA-CERTIFIED` requires all of the following:

- outward-rounded Arb arithmetic;
- exact threshold serialization;
- a proved reachable enclosure;
- exact-rational patch coverage including the isolated reset point;
- certified residual and truncation bounds;
- a certified resolvent/error budget;
- a strict interval lower endpoint above two; and
- an independently implemented auditor that reconstructs rather than invokes
  producer logic.

Missing coverage, shared critical producer/auditor code, an uncertified
remainder, incomplete truncation accounting, or a non-strict lower bound leaves
the certificate `OPEN / NOT CLOSED`. No midpoint collocation or historical
`A=520.3125` result may be presented as a certificate.

## 12. Artifacts and component boundaries

The campaign creates only:

```text
level4/closure_proofs/sr_derivative/
  README.md
  PROTOCOL.md
  DEFINITION_AUDIT.md
  THEOREM.md
  PROOF_OBLIGATIONS.md
  CORRESPONDENCE_REPORT.md
  LEAN_CORRESPONDENCE.md
  FAILURE_DIAGNOSES.md
  FINAL_REPORT.md
  reproduce.sh
  src/
  tests/
  numerics/
  lean/
  certificate/
  results/

level4/reports/SR_DERIVATIVE_THEOREM_REPORT.md
```

The raw-state route, log-state route, statistical analysis, calibration audit,
and Arb attempt remain separate modules with narrow data interfaces. Saved
scientific checkpoints contain batch summaries and deterministic metadata, not
raw Monte Carlo paths.

## 13. Testing and reproduction

Tests cover:

- historical hashes and decisions;
- natural/log threshold units and binary64 correspondence;
- calibration reproduction versus operating-point matching;
- raw/log deterministic path correspondence;
- chart reflection, alarm-time symmetry, and terminal signs;
- simultaneous crossings and injected exact ties;
- `rho=0`, `rho=1`, and interior rho;
- stopped-score accumulation and Gamma calculation;
- paired batch derivative SE;
- frozen finest-step decision and diagnostic-only Richardson behavior;
- independent implementations and seed disjointness;
- Lean declarations, compilation, and axiom audit hooks;
- Arb claim guards;
- the reproducer; and
- final language boundaries.

The authoritative repository verifier is run before work and after the final
package. The Track 2 reproducer rechecks expected historical decisions,
protocol and manifest hashes, scoped tests, retained numerical checkpoints,
Lean compilation, axiom output, and the final Arb status.

## 14. Failure-first and Git policy

Every meaningful failure is preserved: definition mismatch, threshold-unit
error, candidate sign error, calibration failure, score/direct disagreement,
symmetry or tie defect, numerical-gate failure, Lean obstruction, or unsound
Arb route. A failed primary gate cannot be rescued by Richardson, additional
paths, a different step, threshold recalibration, or relaxed criteria.

Meaningful green checkpoints are:

1. definition audit and frozen protocol;
2. human theorem and numerical closure;
3. Lean closure;
4. Arb certificate or explicit open-status record; and
5. final verified report.

No force-push, history rewrite, cache, raw path dump, secret, generated
toolchain, or huge binary is committed.
