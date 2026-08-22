# Frozen-definition and code-correspondence audit

**Audit date:** 2026-08-22  
**Repository boundary:** commit `6341020`  
**Authoritative threshold:** `A = 520.886133602749` in natural SR units

This audit reconstructs the theorem's sign, stopped statistic, detector, and
reuse map from the active Stage D source.  It does not import the CUSUM
derivative formula by analogy.

## 1. Concept correspondence

| Mathematical object | Frozen meaning | Active source correspondence |
|---|---|---|
| Physical observation | `X_t = mu + epsilon_t`, `epsilon_t ~ N(0,1)` | Stage D draws `raw ~ N(0,1)` in `stopped.py:205-207`; its in-control coordinate sets `mu=0` |
| Reference error | `e = R_j - mu` | the parameter named `e` in `simulate_stopped` |
| Residual | `Z_t = X_t - R_j = epsilon_t - e`, hence `Z_t ~ N(-e,1)` | `z = raw - e`, `stopped.py:207` |
| SR state | `R_0^+=R_0^-=0` | stored as `Y=log(1+R)` and initialized at zero, `stopped.py:186-187` |
| SR update | `R_t^+=(1+R_{t-1}^+) exp(Z_t-1/2)` and `R_t^-=(1+R_{t-1}^-) exp(-Z_t-1/2)` | `log_r_plus = Y^+ + z - .5`, `log_r_minus = Y^- - z - .5`, then `Y=logaddexp(0,log_r)`, `stopped.py:152-165` |
| Alarm time | first `t>=1` after the update with either raw `R_t^+>=A` or `R_t^->=A`; boundary inclusive | crossing flags use `>= log_thr`, `stopped.py:165`, and are tested after the update, `stopped.py:201-230` |
| Natural threshold | `A=520.886133602749` | caller supplies `A`; source rejects `A<=1` and takes `log` exactly once, `stopped.py:178-185` |
| Stopped sum | `T_tau=sum_{s=1}^tau Z_s`, terminal innovation included | total is incremented before crossing is finalized, `stopped.py:216,226-234` |
| One-point reused residual | `Z_tau` | terminal innovation is written before alarm handling, `stopped.py:217,226-234`; for `m=1` it is the retained lag |
| Reused physical estimate | `R_j+Z_tau` | Stage D recurrence uses `e + zbar`; for `m=1`, `zbar=Z_tau`, `chain.py:120-128` |
| Mixed reference error | `e_next=rho(e+Z_tau)+(1-rho)U`, `E[U]=0`, `U` independent | generic Stage D reuse rule is documented and implemented at `chain.py:3-6,127-128` |
| Conditional mean map | `F_rho(e)=E[e_next | e]=rho(e+E_e[Z_tau])` | exact expectation of the frozen mixed recurrence; the fresh term has mean zero |
| Score statistic | `-T_tau` at `e=0` | derived below from the stopped Gaussian likelihood, not taken from CUSUM |
| SR gain | `Gamma_SR=E_0[Z_tau T_tau]` | theorem-specific definition; both factors include the terminal innovation |

The active `chain.py` cycle simulator happens to call the CUSUM update because
it was written for the historical Stage D chain experiment.  It is used here
only to audit the repository's mixed-reference convention.  Track 2 will
implement both SR routes independently and will not replace the SR detector
with this CUSUM call.

## 2. Raw/log recursion equivalence

Let `Y=log(1+R)`.  The plus chart's active update computes

```text
log_r_plus = Y_{t-1}^+ + Z_t - 1/2
Y_t^+      = logaddexp(0, log_r_plus).
```

Exponentiating the represented raw state gives

```text
R_t^+
  = exp(Y_t^+) - 1
  = exp(logaddexp(0, log_r_plus)) - 1
  = exp(log_r_plus)
  = (1 + R_{t-1}^+) exp(Z_t - 1/2).
```

The minus chart is identical after replacing `Z_t` by `-Z_t`.  Because
`log_r_plus = log(R_t^+)`, the code's `log_r_plus >= log(A)` is exactly the raw
condition `R_t^+ >= A`, and likewise for the minus chart.  The stored
post-update `Y_t=log(1+R_t)` is not itself compared with `log(A)`.

## 3. The parameter changes the law, not the detector functional

After choosing the residual path as the sample coordinate, define the fixed
measurable detector functional

```text
D_A(z_1,z_2,...) = (tau, terminal chart, z_tau, sum_{s<=tau} z_s).
```

The SR update receives only the current state, `z`, and `log(A)`.  The source
contains no `e` argument in `_sr_update`; its sole occurrence before the update
is `z = raw - e`.  Therefore, for fixed `A`, `D_A` is independent of `e` and
the residual law changes from `Q_0` to `Q_e` with iid marginals `N(-e,1)`.

This is the load-bearing stopped-score architecture:

```text
path functional fixed, law varies.
```

There is no hidden explicit state-derivative term.  If a future source change
passes `e` into the recursion or stopping rule, this audit and theorem become
invalid until re-derived.

## 4. Sign and stopped likelihood

For a deterministic prefix `z_1,...,z_n`, the density ratio of iid
`N(-e,1)` variables relative to iid `N(0,1)` variables is

```text
prod_{t=1}^n phi(z_t+e)/phi(z_t)
  = exp(-e sum_{t=1}^n z_t - n e^2/2).
```

On the event `tau=n`, the stopped likelihood is therefore

```text
L_e = exp(-e T_tau - e^2 tau/2),
```

whose derivative at zero is `-T_tau`.  Once the tail and domination
obligations are discharged, this yields

```text
d/de E_e[Z_tau] at e=0 = -E_0[Z_tau T_tau].
```

The exact mixed-reference reduction then gives

```text
F_rho(e)  = rho(e + E_e[Z_tau]),
F'_rho(0) = rho(1 - E_0[Z_tau T_tau])
          = rho(1 - Gamma_SR).
```

The minus sign is fixed by `Z=epsilon-e`; reversing the residual convention
would reverse the score and requires a different theorem statement.

## 5. Forcing bound derived from the frozen raw recursion

Every live raw state satisfies `R_{t-1}^+>=0` and `R_{t-1}^->=0`.  Put

```text
b_A = log(A) + 1/2.
```

If `Z_t >= b_A`, then line by line

```text
Z_t - 1/2 >= log(A),
exp(Z_t - 1/2) >= A,
1 + R_{t-1}^+ >= 1,
R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2) >= A.
```

The plus chart therefore crosses its inclusive natural-unit boundary.  If
`Z_t <= -b_A`, then

```text
-Z_t - 1/2 >= log(A),
exp(-Z_t - 1/2) >= A,
1 + R_{t-1}^- >= 1,
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2) >= A,
```

so the minus chart crosses.  Hence, from every live state,

```text
|Z_t| >= log(A) + 1/2
```

forces at least one chart to alarm.  This constant is derived from the frozen
`-1/2` log-likelihood increment and inclusive raw threshold; it is not
inherited from CUSUM or a historical certificate.

For `e` in any bounded neighborhood of zero, the Gaussian probability of this
forcing event has a strictly positive uniform lower bound.  Thus `tau` has a
uniform geometric tail there.  The human proof will use that fact to establish
the required small exponential moments and domination.

## 6. Reflection and tie semantics

Under path reflection `z_t -> -z_t`, the raw recursions swap chart-for-chart.
Consequently `tau` is preserved, `Z_tau` and `T_tau` change sign, and their
product is preserved.  Since reflection sends `Q_e` to `Q_{-e}`,
`F_1(-e)=-F_1(e)`.

In the continuous Gaussian model, exact equality of the two terminal chart
values has probability zero.  A finite-precision implementation must still
distinguish:

- a single crossing;
- simultaneous unequal crossings, resolved in favor of the larger raw/log
  chart; and
- exact equality, recorded explicitly as `TIE`.

Every numerical tie will be counted.  Any nonzero confirmatory exact-tie count
blocks the numerical gate for diagnosis rather than being silently assigned a
direction.

## 7. Threshold representation

The authoritative scientific label is the exact decimal

```text
A_decimal = 520886133602749 / 10^12.
```

The active binary64 runtime value is

```text
A_binary64 = 4581762885148045 / 8796093022208
hex(A_binary64) = 0x1.04716cd36dd8dp+9.
```

Their difference is about `5.52e-14`.  The derivative theorem is stated for
arbitrary admissible `A`.  Confirmatory code uses the active binary64 value;
any post-Lean Arb correspondence certificate must use its exact rational
value while reporting the authoritative decimal label.  The historical
`520.3125` threshold is not authoritative for this track.

## 8. Frozen source hashes

| Source | SHA-256 at audit |
|---|---|
| `level4/stage_d/src/stopped.py` | `7224bfec8bf0473c7ddee711d4773a2881889e22977b7e925fee8617f4a58c41` |
| `level4/stage_d/src/chain.py` | `84d354a67d23c33e631f611ed5537b37cbb032023435f051f05e8ccc10439205` |
| `level4/src/rebaseguard_level4/frozen.py` | `777681ea32842ff48224b4c51ff7a2a26525d5a44d815d521949a6242baa6c54` |

The Track-2 implementation must remain source-separated from the active Stage
D implementation; these hashes preserve the correspondence target rather
than authorizing code reuse between the independent numerical routes.

