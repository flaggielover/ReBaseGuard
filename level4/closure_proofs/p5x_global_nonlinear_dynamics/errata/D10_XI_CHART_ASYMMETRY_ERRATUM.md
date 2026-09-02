# Erratum `D10` — the two SR charts are not reciprocal in `E`

**Class:** `DERIVATION_SHORTHAND_ERRATUM`.
**Applies to:** `XI_DERIVATION_AND_INVARIANCE.md` §7 and §14 as frozen at
Checkpoint F `209a6fd9a5ca2824688062ac855a7abcefae9697`. Those bytes are **not**
edited; this file carries the correction, as `D1` did.

## What is wrong

Both sections abbreviate the plus-chart factor as `E = e^{z-1/2}` and then write
the minus-chart factor as `E^{-1}`. From the frozen recurrence

```text
v^+ = y^+ + z - 1/2 ,     v^- = y^- - z - 1/2 ,
```

the two multiplicative factors are

```text
E^+ = e^{ z - 1/2} ,      E^- = e^{-z - 1/2} ,
```

and these are **not** reciprocal:

```text
E^+ * E^- = e^{-1}  ,     so   E^- = e^{-1} / E^+   and   1/E^+ = e^{+1} E^- .
```

Writing `E^-` as `1/E^+` inflates every minus-chart term of degree `j` by `e^{j}`.

## The correction

```text
(E^+)^i (E^-)^j = e^{(i-j) z} * e^{-(i+j)/2} .
```

The `z`-exponent is still `k = i - j`. Therefore **every structural conclusion of
§7 and §14 survives**: the same `2n+1` values of `k`, the same closed-form
Gaussian integral, the same `2(2n+1)` `Phi` evaluations, the same zero `z`-panels.
Only the constant prefactor changes, and it moves inside the grouping:

```text
G_k(zeta) = sum_{i-j=k} c_ij (1/A + zeta^+)^i (1/A + zeta^-)^j e^{-(i+j)/2} ,

(K_e f)(zeta) = sum_{k=-n}^{n} G_k(zeta) e^{k^2/2 - k e}
                [ Phi(u+e-k) - Phi(l+e-k) ] .
```

## What is unaffected

* §1 `xi^- ' = 1 + xi^- exp(-z-1/2)` — correct as frozen.
* §4/§14 live-region limits `l = log(1/A+zeta^-) - 1/2`, `u = 1/2 - log(1/A+zeta^+)`
  — re-derived and re-verified; correct as frozen.
* §7's integral identity `int_l^u e^{kz} phi(z+e) dz = e^{k^2/2-ke}[Phi(u+e-k)-Phi(l+e-k)]`
  — correct as frozen.
* `L-R4.1` .. `L-R4.10` — pathwise statements about `exp`/`log`; the shorthand
  plays no role in any of them.
* Every gate criterion, threshold, class and the recorded prediction.

## Evidence

Before correction, the closed form disagreed with an independent brute-force
simulation of the frozen `y`-space recurrence by relative `5.3e-3` .. `2.9e-1` on
random candidates. After correction, agreement is exact to the printed precision
on all five random cases (`rel_gap = 0.0` at double resolution), including cases
the pre-correction code got wrong.

The defect was found by that pre-gate equivalence check, **not** by reading the
algebra — the same way the R2 `C2` substitution-order bug was found, and the
reason such a check is run before every gate in this campaign.
