# SR cancellation-preserving residual blocker

## Status

```text
OPEN — NO GLOBAL SR RESIDUAL SUPREMUM CERTIFIED
```

This optional rigor-upgrade attempt preserves the frozen SR detector,
authoritative runtime threshold, degree-16 exact-dyadic candidate, and the
already certified monotone block resolvent. It does not alter any historical
Level-4 artifact or verdict.

## Strongest new residual component

The validated centered-Taylor integrator evaluates the Bellman integrals with
algebraic cancellation intact. At reset, 192-bit Arb, Taylor order 10, and 32
innovation subintervals give rigorous local enclosures

```text
residual_a(0,0) in approximately [-1.302e-6, 1.302e-6]
residual_b(0,0) in approximately [-1.6330e-5, 1.6330e-5].
```

These are point enclosures only. They have no global proof weight.

For the complete first continuum rectangle

```text
0 <= y_plus  <= log(1+A)/64,
0 <= y_minus <= log(1+A)/64,
```

the multivariate Taylor model preserves the residual polynomial cancellation:

```text
polynomial residual-a upper = 2.8993182689e-7.
```

The result is a continuum patch bound, not a sampled-grid calculation.

## Exact blocker

The outward-rounded total-degree remainder for that patch is

```text
0.0120020684097529382869...
```

and the resulting rigorous patch residual upper bound is

```text
0.0120023583415798300276...
```

With the certified resolvent `25000/19` and
`||K_z|| <= E|Z| = sqrt(2/pi)`, even granting `epsilon_b=0`, the largest
global `epsilon_a` compatible with a propagated lower endpoint above two is

```text
1.1069256037165139360e-5.
```

The current patch bound is therefore about 1,084 times too large. This does
not show that the true residual is large: the cancellation-preserving
polynomial part is small. It shows that interval evaluation of high-order
derivative remainders is too pessimistic and too costly for a global cover.

An order-8/32-subinterval diagnostic reduced the same bound to about
`0.00265878` but required about 352 seconds for one patch, so blindly raising
the order cannot support the required thousands-patch independent replay.

## Most plausible mathematical fix

Retain the validated point integrator and replace interval high-derivative
remainders with locally composed polynomial models whose ranges and remainders
are converted to Bernstein form. Adaptively subdivide the innovation
coordinate where the pure innovation remainder dominates, and reuse exact
patch polynomials across the producer and a source-independent auditor.

Until that global cover yields certified `epsilon_a` and `epsilon_b`, coupled
propagation and a strict outward-rounded `Gamma_SR` lower endpoint cannot be
formed. The correct status remains:

```yaml
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

Reproduce the exact machine-readable probe with:

```bash
bash level4/closure_proofs/sr_derivative/certificate/reproduce_open_upgrade.sh
```
