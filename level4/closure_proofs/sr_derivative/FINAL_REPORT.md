# Final report — symmetric two-chart SR derivative theorem

## Decision

```text
SR-DERIVATIVE-CLOSED
```

The frozen symmetric two-chart Shiryaev--Roberts derivative theorem is closed
for the authoritative detector/reuse correspondence:

```text
Gamma_SR = E_0[Z_tau T_tau],
F'_rho(0) = rho(1-Gamma_SR).
```

The closure is based on a frozen definition audit, a concrete human
stopped-score proof, two independent numerical implementations, structural
reflection and rho scaling, a compiled conditional Lean proof spine with a
transparent axiom audit, and clean repository verification.

Arb was attempted afterward and remains non-blocking and open.  The final
three-part status is exactly:

```yaml
derivative theorem: CLOSED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

`SR-GAMMA-CERTIFIED` is not awarded.  No SR instability claim is described as
certified or rigorous.

## 1. Frozen correspondence

The theorem uses the active Stage D convention:

```text
e = R_j-mu,
Z_t = X_t-R_j = epsilon_t-e ~ N(-e,1),
R_t^+ = (1+R_{t-1}^+)exp(Z_t-1/2),
R_t^- = (1+R_{t-1}^-)exp(-Z_t-1/2),
tau = inf{t>=1:max(R_t^+,R_t^-)>=A},
A = 520.886133602749.
```

Both charts update before the inclusive alarm test, reset to zero for a new
cycle, and include the terminal innovation.  At `m=1`, the reused error is
exactly `e+Z_tau`; the independent fresh term has mean zero.

The active log code stores `Y=log(1+R)` and receives only the residual `z` and
`log(A)`.  Thus residual parameterization gives

```text
path functional fixed, law varies.
```

There is no explicit detector-state derivative term.  The residual sign and
score were derived from the source rather than imported from CUSUM.

The forcing inequality was also re-derived from the raw recursion:

```text
|Z_t| >= log(A)+1/2
```

forces at least one chart to cross from every live state.  This yields the
uniform geometric-tail control used in the human proof.

## 2. Human theorem

On `{tau=n}`, the iid `N(-e,1)` prefix density relative to `N(0,1)` is

```text
exp(-eT_n-e^2n/2).
```

Summing finite-prefix change-of-measure identities gives

```text
E_e[Z_tau]
  = E_0[Z_tau exp(-eT_tau-e^2 tau/2)].
```

The SR forcing event gives a uniform geometric tail.  Gaussian exponential
moments and Cauchy--Schwarz then establish stopped-variable integrability and
an integrable uniform derivative dominator.  Differentiation at zero yields

```text
d/de E_e[Z_tau]|_0 = -E_0[Z_tau T_tau] = -Gamma_SR.
```

The exact mixed-reference reduction

```text
F_rho(e)=rho(e+E_e[Z_tau])
```

therefore proves the theorem.

Path reflection swaps the two charts step by step, preserves `tau`, negates
`Z_tau` and `T_tau`, and preserves their product.  It proves `F_1` odd and
zero a fixed point.  Rho scaling is exact for every `rho in [0,1]`.

## 3. Independent numerical correspondence

The protocol was frozen before outcomes at SHA-256
`e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762`.
No threshold, step, sample size, seed, route, or primary criterion changed
after outcomes.

### Calibration

The fresh bisection candidate was `522.6191239`, only `0.333%` from the
authoritative threshold; it was never substituted into the theorem.  At the
fixed thresholds, the SR/CUSUM ARL ratio was `0.998383`, within the blocking
1% band.

### Route A — raw stopped score

An independently written raw-state simulator ran 64 batches of 25,000 paths:

```text
Gamma_SR = 17.2913209 +/- 0.0275686,
1-Gamma_SR = -16.2913209 +/- 0.0275686.
```

The historical comparison gave combined `z=-0.726`.  The batch-Student 99%
lower bound was `17.2181>2`, classified only as confirmatory numerical
evidence.

### Route B — independent log conditional map

The separately written log-state implementation used two disjoint
replications, each with 64 batches of 12,500 paired paths per sign and step.
Uncertainty was computed from the distribution of paired batch derivatives.
At the frozen primary step `h=0.0125`:

```text
direct conditional-map derivative = -16.1950096 +/- 0.0390592,
pooled z versus Route A = 2.01453,
relative discrepancy = 0.591%,
replication-agreement |z| = 0.741.
```

Every primary correspondence criterion passed.  Both routes recorded zero
exact ties and zero simultaneous crossings.  Richardson and observed order
remained secondary diagnostics and did not control the verdict.

The numerical gate closed with the exact declaration:

```text
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

## 4. Conditional Lean proof spine

The pinned Lean project compiles the following high-value spine:

- raw two-chart state/update and sign/state-swap reflection;
- inclusive alarm symmetry;
- finite-list first-alarm and stopped-record reflection;
- terminal sign negation and product invariance;
- oddness and exact rho scaling;
- the derivative consequence using the existing stopped-integral interface;
- `Gamma>2 -> |F'_1(0)|>1`; and
- exact authoritative/runtime threshold distinctions.

The nine-declaration axiom audit contains only:

```text
propext
Classical.choice
Quot.sound
```

There is no `sorry`, `admit`, or project-specific scientific axiom.

The formal boundary remains explicit:

> The Lean theorem formalizes the algebraic/stopped-score consequence under
> explicit analytic hypotheses; the concrete SR tail, measurability,
> integrability, and domination obligations remain human-proved.

This is not an end-to-end Lean formalization of the concrete infinite SR
process.

## 5. Non-blocking Arb attempt

The post-Lean Arb attempt used the exact runtime rational

```text
4581762885148045/8796093022208
```

for the authoritative threshold.  It recomputed outward-rounded geometry and
a fresh exact-dyadic degree-16 candidate at the current threshold.  The
candidate reset value was about `17.29084`, but it is not a true-Gamma
enclosure.

Representative raw interval residual cells reproduced severe dependency
loss: residual-`b` widths ranged from about `0.54` to `2.91`.  The attempt did
not complete an exact global patch cover, certified global residual suprema,
a useful certified resolvent/error propagation, or a strict final Gamma lower
endpoint.  Its independent auditor passed only the honesty and consistency of
the OPEN attempt.

Therefore:

```text
rigorous SR local-instability certificate: OPEN
```

The historical `A=520.3125` feasibility values were not used as authority.

## 6. Verification and historical integrity

The pre-decision evidence replay at commit
`2ca2740d816d6703460b894403c344fbe38508a0` passed every then-retained suite,
the Lean replay, the byte-stable Arb OPEN audit, and the authoritative
repository verifier.  Final clean package reproduction passed:

- Track 1: 46/46;
- Track 1A: 32/32;
- Track 1B: 32/32;
- Track 2: 58/58;
- frozen Level 1--3 and authoritative Level-4 stages: 695/695; and
- combined retained/repository checks: 863/863.

The authoritative verifier reported a clean worktree and `LEVEL 4
VERIFICATION OK`.  The 139-file historical manifest remained unchanged.

Historical scientific outcomes are preserved:

- D2.3 remains `FAILED`;
- Stage D remains `STAGE-D-PARTIAL`;
- Stage F remains `LEVEL-4-PARTIAL`; and
- no global Level-4 or Stage-F re-audit was performed.

The old Stage-F ledger still reflects its historical audit boundary.  This
track closes only the scoped SR derivative-theorem requirement.

## 7. Meaning of closure

`SR-DERIVATIVE-CLOSED` means that the derivative identity and its frozen SR
correspondence have survived the human, independent numerical, structural,
Lean, axiom, integrity, and repository gates defined before outcomes.

It does not mean that `Gamma_SR>2` has an Arb certificate, that the stochastic
reference process has a rigorously certified instability, that an SR period-2
orbit exists, or that global Level 4 is closed.  A later successful full Arb
certificate may add `SR-GAMMA-CERTIFIED` without changing this definition.
