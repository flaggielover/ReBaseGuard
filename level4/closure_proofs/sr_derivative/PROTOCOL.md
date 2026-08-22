# Frozen protocol — symmetric two-chart SR derivative theorem

**Campaign:** Level-4 Proof Track 2  
**Freeze date:** 2026-08-22  
**Primary proof route:** change of measure and stopped-score differentiation  
**Confirmatory outcomes generated before this text:** none  
**Arb:** non-blocking, post-Lean rigor upgrade only

This protocol is immutable once its SHA-256 record is written.  It replaces no
historical gate, does not reinterpret a historical result, and authorizes no
scientific work outside the derivative theorem described here.

## 1. Closure target and allowed decisions

The sole target is the local derivative theorem for the authoritative
symmetric two-chart Shiryaev--Roberts detector under matched one-observation
reuse.  Allowed track verdicts are:

- `SR-DERIVATIVE-CLOSED`;
- `SR-DERIVATIVE-PARTIAL`; and
- `SR-DERIVATIVE-FAILED`.

`SR-DERIVATIVE-CLOSED` requires all of the following:

1. frozen definition/code correspondence;
2. a complete human derivative proof;
3. explicit discharge and classification of the concrete analytic obligations;
4. structural reflection and rho-scaling closure;
5. both independent numerical routes and all blocking checks passing;
6. a compiled conditional Lean proof spine with transparent axiom audit;
7. clean reproduction and authoritative full-repository verification; and
8. unchanged historical artifacts.

Arb is not a condition of this verdict.  Without a successful Arb certificate,
the only allowed scalar classification is:

```yaml
derivative theorem: CLOSED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR instability certificate: OPEN
```

A later successful certificate may add `SR-GAMMA-CERTIFIED`; it must not
retroactively redefine `SR-DERIVATIVE-CLOSED`.

This track does not start an `m`--`rho` map, an SR period-2 certificate, a
general location-family theorem, external validation, or a global Level-4
re-audit.

## 2. Immutable history and authority boundary

The manifest at `results/historical_manifest.json` freezes all Git-tracked
files under Stage D and Tracks 1, 1A, and 1B.  It preserves:

- Level 1--3 `CLOSED`;
- Stage D `STAGE-D-PARTIAL` and D2.3 `FAILED`;
- Track 1 `MGT1-THEOREM-PARTIAL`;
- Track 1A `MGT1-TRACK1A-FAILED`;
- Track 1B `MGT1-TRACK1B-CLOSED`;
- the scoped `m>1` derivative-theorem requirement `CLOSED`; and
- Stage F `LEVEL-4-PARTIAL`.

Historical artifacts are read-only.  Historical numerical values may be used
only as predeclared comparators.  They are never pooled into new estimates.

## 3. Frozen detector and threshold

The scientific detector is

```text
delta = 1
A = 520.886133602749       (natural SR units)
R_0^+ = R_0^- = 0

R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2)
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2)

tau = inf {t>=1 : max(R_t^+,R_t^-) >= A}.
```

Both charts use the same residual.  Both updates occur before the inclusive
alarm test.  The terminal residual is included in every terminal statistic.
Each new cycle resets both chart states to zero.

If exactly one chart crosses, it supplies the direction.  If both cross with
unequal post-update raw values, the larger chart supplies the direction.  If
both cross with exactly equal post-update values, the outcome is `TIE`; it is
never silently assigned to either chart.

The log representation stores `Y=log(1+R)` and computes

```text
ell_t^+ = Y_{t-1}^+ + Z_t - 1/2
ell_t^- = Y_{t-1}^- - Z_t - 1/2
Y_t^+ = logaddexp(0,ell_t^+)
Y_t^- = logaddexp(0,ell_t^-).
```

Crossing compares `ell_t^± >= log(A)`.  The implementation accepts `A` in
natural units and takes its logarithm exactly once.

The authoritative label is the exact decimal rational

```text
A_decimal = 520886133602749 / 10^12.
```

The numerical implementation uses its nearest binary64 value

```text
A_binary64 = 4581762885148045 / 8796093022208
           = 0x1.04716cd36dd8dp+9.
```

The displayed label remains `A=520.886133602749`.  The derivative theorem is
for arbitrary admissible `A`.  Any code-corresponding Arb computation must use
the exact binary64 rational.  The historical value `A=520.3125` is forbidden
as an authority, substitute, or transferred certificate.

## 4. Frozen sign, reuse, and map definitions

Let

```text
X_t = mu + epsilon_t,       epsilon_t iid N(0,1),
e   = R_j - mu,
Z_t = X_t - R_j = epsilon_t-e ~ N(-e,1),
T_tau = sum_{t=1}^tau Z_t.
```

For matched `m=1` reuse, the reused physical observation is
`R_j+Z_tau`; its error relative to `mu` is `e+Z_tau`.  Let `U~N(0,1)`
be independent of the stopped SR path and have mean zero.  The next reference
error and conditional-mean map are

```text
E_next = rho(e+Z_tau) + (1-rho)U,
F_rho(e) = E_e[E_next] = rho(e+E_e[Z_tau]),
rho in [0,1].
```

Thus `F_rho=rho F_1` and `F_0=0` exactly.  No independent fresh draw is needed
to estimate the conditional mean numerically because its expectation is zero;
structural tests still exercise the full affine update.

## 5. Fixed path functional and forcing bound

In residual coordinates, the SR recursion, stopping rule, terminal residual,
and stopped sum depend on the residual path and fixed detector constants only.
The parameter `e` changes the path law; it is not an explicit detector input:

```text
path functional fixed, law varies.
```

Any discovered explicit `e` dependence in the detector functional invalidates
the theorem candidate and stops the campaign before numerical outcomes.

The analytic tail bound is derived from the raw recursion.  Since every live
state is nonnegative, if `Z_t>=log(A)+1/2`, then

```text
R_t^+ = (1+R_{t-1}^+)exp(Z_t-1/2) >= 1*A = A.
```

If `Z_t<=-log(A)-1/2`, the identical argument gives `R_t^- >= A`.
Therefore

```text
|Z_t| >= log(A)+1/2
```

forces an inclusive crossing from every live state.  This exact constant is
not inherited from CUSUM.  The uniform positive forcing probability on a
bounded neighborhood of `e=0` is the basis for the concrete geometric-tail
and domination proof.

## 6. Human theorem and proof gate

Define `Q_e` as the law of iid residuals `N(-e,1)`.  On the stopped
sigma-field the likelihood ratio relative to `Q_0` is

```text
L_e = exp(-e T_tau-e^2 tau/2).
```

The required human proof follows this chain explicitly:

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

The proof must establish for the concrete infinite SR functional, rather than
merely assume, all of the following needed facts:

- path-space and stopped-variable measurability;
- almost-sure finiteness of `tau` near zero;
- a uniform geometric tail and a small exponential stopping moment;
- integrability of `Z_tau`, `T_tau`, and `Z_tau T_tau`;
- uniform integrability/dominating bounds for the stopped likelihood
  difference quotient; and
- validity of exchanging derivative, stopped sum, and expectation.

Reflection `z->-z` must be proved to swap the charts at every finite step,
preserve `tau`, negate `Z_tau` and `T_tau`, and preserve their product.  It
then proves `F_1` odd and zero a fixed point; numerical symmetry alone is not
accepted.

The theorem document and proof-obligation ledger must be complete before the
confirmatory numerical verdict.  A contradiction in sign, map definition, or
fixed-functional status is a theorem failure and stops the track.

## 7. Frozen randomness and non-adaptation rule

The fresh master seed is `2026082227`.  All streams use NumPy `SeedSequence`
with PCG64 and the following keys:

| Purpose | Seed key |
|---|---|
| CUSUM target ARL for calibration reproduction | `[2026082227,1,0]` |
| SR bisection iteration `i` | `[2026082227,1,1,i]` |
| fresh measurement at the bisection candidate | `[2026082227,1,2]` |
| fixed-threshold SR ARL batch `b` | `[2026082227,1,3,b]` |
| fixed-threshold CUSUM ARL batch `b` | `[2026082227,1,4,b]` |
| raw Route A batch `b` | `[2026082227,2,b]` |
| log Route B replication `r`, batch `b` | `[2026082227,3,r,b]` |
| structural control | route identifier at least `90` |

Families are pairwise disjoint.  The independent batch mean is the
statistical unit.  No threshold, seed, sample size, step, primary criterion,
or route may be changed after outcomes.  There is no pilot-selected resizing.
A failure cannot be rescued with more paths, a replacement step, Richardson,
threshold retuning, or relaxed acceptance criteria.

## 8. Blocking calibration checks

The authoritative CUSUM comparator uses the frozen two-sided CUSUM with
`k=1/2`, inclusive `h=5`, after-update alarm, reset state, and terminal
observation included.

### 8.1 Calibration-reproduction sanity check

Estimate the target CUSUM ARL with 800,000 cycles using key
`[2026082227,1,0]`.  Starting with the natural-unit SR bracket `[100,3000]`,
bisect in log threshold.  Iteration `i` uses 200,000 reset SR cycles and its
own key `[2026082227,1,1,i]`.  If the estimated SR ARL is below the target,
replace the lower endpoint; otherwise replace the upper endpoint.  Stop when
the log-width is at most `1e-3` or after 30 evaluations, whichever occurs
first.  The candidate is the geometric midpoint of the final bracket.  Measure
it afresh with 800,000 cycles and key `[2026082227,1,2]`.

The blocking criterion is

```text
|A_candidate/A_authoritative - 1| <= 0.02.
```

The final fresh ARL and its ratio to the target are reported as diagnostics.
The candidate never replaces the authoritative threshold in the theorem or
either confirmatory route.

### 8.2 Fixed-operating-point matching check

At fixed `A=520.886133602749` and fixed CUSUM `h=5`, run each detector in 64
independent batches of 10,000 reset cycles.  Estimate each ARL and SE from its
64 batch means.  The blocking criterion is

```text
|mean_ARL_SR/mean_ARL_CUSUM - 1| <= 0.01.
```

This check establishes operating-point matching and cannot be replaced by the
bisection result.  A threshold-unit test must also establish that `A`, not
`log(A)`, enters each public simulator.

## 9. Route A — raw-state stopped-score estimate

Route A is an independently written raw-state SR simulator.  It must not
import the Stage D SR update or any Route B recursion, stopping, map, or
theorem helper.  It uses 64 independent batches of 25,000 reset cycles, for
1,600,000 paths, with keys `[2026082227,2,b]`.

For every path it accumulates and internally validates:

```text
tau, Z_tau, T_tau, Z_tau*T_tau,
terminal raw chart values, direction,
simultaneous-crossing flag, exact-tie flag.
```

Saved artifacts retain batch summaries and counts, not raw paths.  From the 64
batch means compute the sample mean and sample SE
`s_batch/sqrt(64)` for

```text
Gamma_hat = mean(Z_tau*T_tau),
d_A = 1-Gamma_hat.
```

The historical comparator is frozen as

```text
Gamma_hist = 17.319830589555345,
SE_hist    = 0.02800150922045604.
```

The blocking historical-correspondence statistic is

```text
z_hist = (Gamma_hat-Gamma_hist)/sqrt(SE_hat^2+SE_hist^2),
|z_hist| <= 4.
```

Using the Student `t` critical value `t_{0.995,63}`, the one-sided numerical
lower bound

```text
Gamma_hat - t_{0.995,63} SE_hat
```

must be strictly greater than two.  This bound is confirmatory numerical
evidence only and is never called a rigorous certificate.

## 10. Route B — independent log-state conditional-map derivative

Route B is written independently in log state.  It must not import Route A,
the Stage D SR update, or a shared recursion, stopping, score, Gamma, or
theorem-encoding helper.  Source/AST guards enforce this separation.

The precommitted central-difference ladder is

```text
h in {0.1,0.05,0.025,0.0125}.
```

There are two independent replications `r in {0,1}`.  Each replication uses
64 batches of 12,500 path indices, with seed key `[2026082227,3,r,b]`.
Within a replication/batch, one PCG64 stream emits a full 12,500-vector
`epsilon[path,t]` at each time `t`, including entries for already stopped path
conditions.  Every sign and every `h` condition uses that same
path/time-addressed innovation and sets `Z=epsilon-e`.  Ignoring an innovation
after a condition stops never shifts another condition's stream.  Thus CRN is
shared across signs and the entire ladder but never across batches or
replications.

For `rho=1`, each path's conditional-map output is

```text
M_e = e + Z_tau(e).
```

For each batch and `h`, first form the paired batch derivative directly:

```text
D_b(h) = (mean_b M_{+h} - mean_b M_{-h})/(2h).
```

The Route B mean and SE are the mean and `s_batch/sqrt(B)` of these paired
batch derivatives.  Separate `+h` and `-h` SEs are never combined as if the
signs were independent.

The primary step is exactly `h=0.0125`.  Pooling the two replications means
taking the mean and ordinary sample SE of all 128 independent primary batch
derivatives.  With `d_A=1-Gamma_hat` and independent Route A/Route B families,
define

```text
z(A,B) = (d_B-d_A)/sqrt(SE_B^2+SE_A^2),
relative discrepancy = |d_B-d_A|/|d_A|.
```

Route B passes only if:

1. the pooled primary estimate has `|z(A,B)|<=3`;
2. each replication's primary estimate has `|z(A,B_r)|<=4`;
3. the replication difference divided by
   `sqrt(SE_B0^2+SE_B1^2)` is at most three in absolute value;
4. the pooled relative discrepancy is at most `0.02`;
5. all batch IDs, path counts, seed keys, and path/time CRN align exactly;
6. Route A and Route B seed families are disjoint; and
7. source-level implementation-separation guards pass.

The secondary Richardson value is

```text
D_R = (4 D(0.0125)-D(0.025))/3.
```

Observed order from successive ladder differences and all Richardson
comparisons are diagnostics only.  They cannot fail an otherwise passing
primary result or rescue a failing primary result.

## 11. Mandatory structural controls and tie guard

Before any numerical verdict, both implementations must pass a fixed suite of
deterministic innovations containing reset paths, noncrossing paths, plus and
minus crossings, boundary crossings, simultaneous unequal crossings, and an
injected exact tie.  Required pathwise conclusions are:

1. raw and log chart states correspond within declared floating-point
   tolerances and alarm at the same first index;
2. reflection swaps charts step by step and preserves `tau`;
3. reflection negates `Z_tau` and `T_tau` and preserves their product;
4. simultaneous unequal crossings select the larger terminal chart;
5. the injected equality returns `TIE` in both implementations;
6. `F_1(-e)=-F_1(e)` on exactly paired reflected finite paths;
7. `F_0=0`, `F_1=M_e`, and the frozen interior value `rho=0.37` equals
   `rho*M_e+(1-rho)U` pathwise; and
8. the empirical conditional mean obeys exact rho scaling up to roundoff.

Both confirmatory routes record every simultaneous crossing and exact tie.
The mathematical exact-tie probability is zero under the continuous Gaussian
law.  The blocking confirmatory criterion is exactly zero observed ties in
every route, batch, sign, and step.  Any positive count stops the gate for
implementation/numerical diagnosis.

## 12. Numerical decision gate

The numerical gate closes only if:

- both calibration checks pass in their distinct roles;
- all definition, threshold, history, seed, batch, and source guards pass;
- all structural reflection, rho, crossing, and tie controls pass;
- Route A passes its historical correspondence and numerical lower-bound
  checks;
- Route B passes every primary finest-step and replication check; and
- no historical artifact changed.

If any primary item fails, preserve the outcome and stop before Lean.  Use
`SR-DERIVATIVE-FAILED` for a definition, sign, symmetry, theorem, or structural
contradiction.  Use `SR-DERIVATIVE-PARTIAL` for an unresolved numerical,
calibration, precision, implementation-separation, or evidentiary obstruction.

Only an all-pass result authorizes the exact declaration:

```text
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

## 13. Lean gate and analytic boundary

Lean starts only after that declaration.  Against the pinned project, formalize
the high-value proof spine:

1. raw two-chart SR state and step;
2. state-swap/sign-reflection equivariance of a step;
3. symmetry of the inclusive alarm predicate;
4. finite-list first-alarm and terminal-record reflection;
5. terminal signed-statistic negation and product invariance;
6. odd-map and exact rho-scaling algebra;
7. the stopped-score derivative consequence through the existing abstract
   stopped-integral differentiation interface and explicit hypotheses;
8. `Gamma_SR>2 -> |F'_1(0)|>1`; and
9. correspondence with the authoritative threshold, reset, update, boundary,
   and terminal-inclusion conventions.

The Lean theorem is a conditional formal proof spine over explicit analytic
hypotheses.  The required description is:

> The Lean theorem formalizes the algebraic/stopped-score consequence under
> explicit analytic hypotheses; the concrete SR tail, measurability,
> integrability, and domination obligations remain human-proved.

It must not be described as an end-to-end formalization of the concrete
infinite SR process unless measurability, a.s. finiteness, integrability,
exponential tails, and domination are actually instantiated in Lean.

The axiom audit must compile every headline declaration, run `#print axioms`,
scan the Track-2 Lean source for `sorry`, `admit`, and project-specific axioms,
and list each remaining standard dependency.  A hidden assumption or
uncompiled declaration leaves the track partial.

## 14. Non-blocking Arb upgrade

Arb begins only after the Lean gate closes.  It uses the exact rational
`4581762885148045/8796093022208`, corresponding to the authoritative Stage D
runtime threshold, and recomputes every enclosure and constant.  Historical
`A=520.3125` feasibility work supplies architecture only.

`SR-GAMMA-CERTIFIED` requires:

- outward-rounded Arb arithmetic and exact threshold serialization;
- a proved reachable enclosure;
- exact-rational patch coverage, including the isolated reset point;
- certified truncation and tail remainders;
- a certified fixed-point residual and resolvent/error budget;
- a final interval for `Gamma_SR` with strict lower endpoint greater than two;
  and
- an independently implemented auditor that reconstructs certificate claims
  without invoking the producer's critical logic.

Any missing cover, shared critical producer/auditor code, uncertified
remainder, incomplete truncation accounting, unresolved build error, or
non-strict lower endpoint records:

```text
rigorous SR instability certificate: OPEN
```

This does not block `SR-DERIVATIVE-CLOSED`.  No midpoint computation or
confirmatory confidence interval may be called rigorous or certified.

## 15. Reproduction and final verification

The reproducer must verify, in order:

1. the historical manifest and preserved failure/partial decisions;
2. the immutable protocol hash;
3. definition, threshold, seed, source, structural, and tie tests;
4. retained calibration and independent numerical checkpoints;
5. the numerical decision and Lean authorization;
6. Lean compilation and the retained axiom audit;
7. the Arb certificate or explicit open-status record; and
8. final report language and decision consistency.

Run the complete authoritative `scripts/verify_level_4.sh` after the Track-2
package and all scoped tests are green.  Generated caches, raw Monte Carlo
paths, toolchains, and large binaries are not committed.

Final closure requires clean reproduction from retained artifacts, all scoped
tests, the authoritative full suite, and a clean historical manifest.  The
final report must distinguish the derivative theorem, confirmatory
`Gamma_SR>2` evidence, and the rigorous certificate status exactly as required
in Section 1.

