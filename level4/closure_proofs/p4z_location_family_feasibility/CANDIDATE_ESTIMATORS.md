# P4Z Phases 5–8 — candidate estimators, and the validity audit

Two candidates.  No third: see §5.

Both are exact reformulations of the frozen estimand, obtained by taking a
conditional expectation over the alarm-causing increment.  Neither changes the
theorem, the conventions, the detectors, the window semantics, the stopping
rule, the finite-difference convention or any threshold.

## 1. The construction both share

By the bounded-survival lemma (`GENERAL_LOCATION_THEOREM_AUDIT.md` §5), the
event `{tau = n}` is, on the `F_{n-1}`-measurable event `{tau >= n}`, exactly
`{Z_n ∉ I(u_{n-1}, d_{n-1})}` with `I = (L, U)` an explicit bounded interval.
Write the alarm set `E = (-inf, L] ∪ [U, inf)` and

```text
J0 = int_E f       J1 = int_E z f       J2 = int_E z psi(z) f      J3 = int_E psi f
```

Because `psi f = -f'` by definition of the score, three of the four are
**family free**:

```text
J3 = f(U) - f(L)
J2 = F(L) - L f(L) + U f(U) + 1 - F(U)
J0 = F(L) + 1 - F(U)
```

and only `J1 = Mlow(L) - Mlow(U)` is family specific, where
`Mlow(x) = int_{-inf}^x z f`.  A family's entire analytic contract is
`(f, F, Mlow)`.  All four are verified against quadrature to `<= 1e-7` for
gaussian, laplace, logistic, t3, t1p5 and skewnormal4 by
`tests/test_analytic_contract.py`.

`J1` is also where the theorem's proved failure mode F2 reappears
*structurally*: for a law without a first moment, `Mlow` does not exist and the
estimator cannot be written down at all.  Cauchy is refused, not approximated.
Uniform is absent entirely: its support moves, (A3) fails, and the identity is
false — there is nothing to estimate.

## 2. Candidate A — `RB-SCORE`

**Minimal scientific change**: same route, same identity, same score, one
conditional expectation taken.

### 2.1 Derivation

With `P_{n-1} = sum_{t<n} psi(Z_t)`, `B_{n,m} = sum_{r=1}^{w-1} Z_{n-r}` and
`w = min(m, n)` — all `F_{n-1}`-measurable —

```text
E[ 1{tau = n} A_m S_tau^psi | F_{n-1} ]
    = (1{tau >= n} / w) * ( P_{n-1}(J1 + B_{n,m} J0) + (J2 + B_{n,m} J3) )
    =: 1{tau >= n} * h_n
```

Summing over `n`,

```text
Gamma = sum_{n >= 1} E[ 1{tau >= n} h_n ]
```

so the per-path estimator is: run the ordinary frozen path, accumulate `h_n`
computed from the *pre-step* charts at every step `n = 1 .. tau`, and stop.
The realised value of `Z_tau` is drawn — it is what stops the path — but never
enters the estimator's value.

### 2.2 Expectation and bias

Exact: `E[RB-SCORE] = Gamma_{D,m,f}`.  This is the tower property applied
termwise, with no interchange beyond the one G1a already licenses.  **Bias =
0**, not asymptotically but identically.

### 2.3 Variance and moments

`|J0| <= 1`, `|J1| <= E|eps|`, `|J2| <= 1 + 2 c_D sup f`, `|J3| <= 2 sup f`,
`|B_{n,m}| <= (m-1) c_D`, `|P_{n-1}| <= M(n-1)`.  Hence `|h_n| <= C n` and the
per-path value is bounded by `C tau^2`.  Discharge lemma L1 gives `tau` a
geometric tail uniformly on the `e`-neighbourhood, so **every moment of the
RB-SCORE summand is finite** — against an infinite *second* moment for the
historical summand.

This is not a variance reduction in the usual sense.  It is a change of moment
class.  The estimator's own standard error becomes a statistic that estimates
something that exists, which is the precondition P4Y Pilot-4 proved the
historical architecture could not meet.

Measured variance reduction factor against the historical summand on identical
cells (`micropilots/diagnostics/micropilot.json`):

| cell | historical rel. sd | RB-SCORE rel. sd | VRF | Hill: hist → RB | top-1: hist → RB |
|---|---|---|---|---|---|
| `gaussian/cusum@2` | 1.00 | 0.973 | **1.1** | 6.4 → 3.8 | 0.003 → 0.005 |
| `t3/cusum@5` | 19.9 | 2.30 | **75** | 3.1 → 3.3 | 0.010 → 0.012 |
| `t1p5/sr@20` | 12.1 | 0.94 | **165** | 1.6 → 4.0 | 0.436 → 0.005 |
| `t1p5/cusum@5` | 29.7 | 1.22 | **596** | 1.6 → 3.5 | 0.297 → 0.012 |
| `t1p5/sr@520.886` | 128.3 | 1.24 | **10 668** | 1.5 → 4.1 | 0.975 → 0.006 |

The Gaussian control is the honest check: RB-SCORE is *neutral* there (VRF 1.1,
a marginal increase), because on a light-tailed family the alarm increment was
never the dominant term.  The construction targets exactly the failure mode
diagnosed and nothing else.  A method that improved every cell uniformly would
be evidence that something else was going on.

### 2.4 Compatibility with the stopping rule and the neutrality control

The detector recursion, threshold, inclusivity, tie rule, window `w = min(m,
tau)`, random denominator and inclusion of the alarm-causing increment are all
untouched — `alarm_bounds` is checked path-by-path against the frozen
`Detector.step` in `tests/test_estimator_identity.py`.

Under a deterministic `tau ≡ n0` the alarm set is empty for `n < n0` and all of
`R` at `n0`, giving the exact constants `J0 = 1`, `J1 = E[eps] = 0`,
`J2 = E[eps psi] = 1`, `J3 = E[psi] = 0` — the two integration-by-parts
identities of Corollary G2(b).  Then `h_{n0} = (P_{n0-1} B + 1)/w`, and since
`E[psi(Z_t) Z_s] = 1{t=s}` the window contributes `w - 1`, so

```text
Gamma = ((w - 1) + 1) / w = 1     exactly, every m, every family.
```

The neutrality control survives as an **algebraic identity** rather than a
measurement.  `whole_line_integrals()` returns those four constants and
`alarm_integrals()` refuses an empty survival interval rather than silently
double-counting the two tails.

### 2.5 Cost and provenance

Per path, RB-SCORE evaluates `f`, `F` and `Mlow` at two points per step,
against the historical route's one `psi` evaluation.  Measured cost ratio:
2.3 CPU-s per million paths for `gaussian/cusum@2`, 5.7 for `t1p5`, 69 for
`t3/cusum@5` (whose long ARL dominates).  Roughly 2–4x the historical per-path
cost, against 75–10 668x the variance reduction.

Provenance requirement: the family's `(f, F, Mlow)` triple joins the scientific
hash.  It is new load-bearing analytic input, and it must be bound as such.

## 3. Candidate B — `RB-MAP`

**Structurally different failure mode**: it never evaluates `psi`, never forms
a likelihood ratio, and never changes measure.  It runs the frozen detector at
shifted parameter values and differences the result — the role the historical
Route B played, which is why a two-route correspondence is evidence about the
score identity at all.

### 3.1 Derivation

Identically, but with the score prefix absent:

```text
g_m(e) = sum_{n>=1} E_e[ 1{tau_e >= n} (J1^{(e)} + B_{n,m} J0^{(e)}) / w ]
```

where `J0^{(e)}, J1^{(e)}` are the same functionals with endpoints shifted by
`e` (residual alarm set `{z<=L} ∪ {z>=U}` is innovation set
`{eps<=L+e} ∪ {eps>=U+e}`, and `J1` picks up `- e J0`).  Common random numbers
couple `+h` and `-h` through the frozen Philox stream keyed on
`(seed, batch, step)` with the inherited `2^64` stride, and the frozen
per-batch Richardson combination `(4 D(h/2) - D(h))/3` is applied unchanged.

### 3.2 Expectation and bias

`g_m(e)` is estimated **without bias** at each `e`.  The finite-difference
truncation error is therefore *identical in expectation* to the historical
route's, because it is the same function `g_m` being differenced at the same
steps.  P4Z introduces no new bias term.

Verified by the FD ladder (`micropilots/diagnostics/fd_ladder.json`): on
`t1p5/sr@520.886`, `m=1`, the central-difference offset against RB-SCORE runs
`-0.0918` at `h=0.2` and `-0.0211` at `h=0.1` — ratio **4.36**, the `O(h^2)`
signature — and reaches `+0.0025` at the frozen `h=0.05`, below the Monte Carlo
noise.  The Richardson pair `(0.2, 0.1)` recovers RB-SCORE to within `0.06 %`.

### 3.3 Variance and moments

`|J1^{(e)}| <= E|eps| + |e|` and `|J0^{(e)}| <= 1`, so the accumulated map
value is bounded by `C tau` and the differenced value by `C tau / h`.  With
L1's geometric `tau`, **every moment is finite, uniformly in `h`**.  The
historical Route-B summand has none beyond the first, because its rare
disagreement paths carry `O(Z_tau/h)`.

Measured per-path relative sd on identical cells:

| cell | historical Route B | RB-MAP | VRF |
|---|---|---|---|
| `gaussian/cusum@2` | 3.92 | 1.11 | **12** |
| `t1p5/cusum@5` (60k-path estimate) | 38.8 | 1.92 | **407** |
| `t1p5/cusum@5` (scale implied by P4X's 2.255e9-path result) | ~293 | 1.92 | **~23 000** |

The two `t1p5` rows differ by a factor of 7.5 because the historical sd cannot
be measured from 60 000 paths — that gap *is* finding F-03, observed directly.
The conservative row is used in the cost model.

### 3.4 Honest limitation

RB-MAP uses `f` and `F` analytically where the historical Route B used only the
detector.  It is therefore **less independent** than Route B was, and P4Z says
so rather than claiming parity.  What it still does not use is the score
identity G1a, the score function `psi`, or any change of measure — and G1a is
the object under test.  RB-MAP remains admissible independent evidence for the
identity, at a disclosed reduction in independence.

This reduction is the reason Phase 17 keeps a *third*, fully score-free and
fully analytic cross-check (`CORRESPONDENCE_AND_FORMAL_PLAN.md`).

## 4. Phase 8 — validity audit

Applied to both candidates.  A "no" anywhere is a rejection.

| check | RB-SCORE | RB-MAP |
|---|---|---|
| estimates exactly the frozen `Gamma_{D,m,f}` | yes, by the tower property applied to G1a | yes, `-g_m'(0)` by the same construction |
| hidden change of estimand | none: the conditional expectation is over `Z_tau` only | none |
| change of stopping convention | none: `alarm_bounds` reproduces the frozen `crossed` flag exactly, tested path by path | none, same test |
| change of window semantics | none: `w = min(m, tau)`, random denominator, alarm increment included | none |
| change of threshold | none | none |
| change of finite-difference convention | n/a | none: `(0.05, 0.025)` and per-batch Richardson, unchanged |
| post-result tuning | none: both were derived before any cell value was compared | none |
| unauthorised conditioning | no: conditioning is on `F_{n-1}` only, an honest filtration | no |
| reuse of future information | no: every quantity in `h_n` is pre-step | no |
| bias from adaptive stopping of the estimator | no: the estimator has no stopping rule of its own; the path stops when the frozen detector alarms | no |
| unbiasedness (required by the contract) | exact | exact at each `e`; FD truncation identical to the historical route's |
| refuses inadmissible families structurally | yes: no `Mlow` ⇒ `ValueError` (cauchy); uniform absent | yes, same contract |

**Both candidates are admissible.**

Two disclosed items, neither a rejection:

1. RB-MAP's reduced independence (§3.4).
2. Both candidates add the analytic triple `(f, F, Mlow)` to the trusted
   computing base.  It is new load-bearing input and must be hashed, bound to
   the producer, and validated against quadrature in-run — not merely at
   development time.  `CAMPAIGN_GOVERNANCE.md` §5 makes that a fail-closed gate.

## 5. Phase 7 — why there is no Candidate C

A third candidate is only warranted by a concrete unresolved tradeoff.  The
two candidates leave three residual weaknesses, and none of them is answered by
a third *estimator*:

* **Reduced independence of RB-MAP** — answered by a diagnostic cross-check
  that is neither route (Phase 17), not by a third gate-bearing estimator.
  Adding a third estimator to the official gate would also change the
  multiple-comparison structure of a frozen gate, which is not permitted.
* **A shared analytic TCB** — answered by an in-run quadrature validation gate,
  not by another estimator that would share the same TCB.
* **The `|z| <= 4` gate becoming binding at high precision** — this is a
  property of the *frozen gate*, not of any estimator, and a third estimator
  cannot help.  It is handled in `CAMPAIGN_GOVERNANCE.md` §4 by making Route
  B's uncertainty honest about its truncation residual, and by an explicit
  `INCONCLUSIVE` verdict.

`REJECTED_ESTIMATORS` therefore consists of the four P4X R0 candidates, which
were measured and rejected on evidence, plus the historical Routes A and B,
which are excluded by finding F-01/F-02.
