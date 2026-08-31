# P7 theory bridge: from the P3 multiplier to monitoring performance

Each statement carries an explicit status. Nothing below is a theorem unless it
says `THEOREM` or `PROPOSITION`, and every empirical input is named.

Notation is P1/P2/P3's throughout. `e_j` is the reference error entering cycle
`j`, `tau_j` the cycle's run length, `zbar_m` the convention-A truncated window
mean, `rho` the reuse fraction, `GammaTilde_{D,m} = E_0[zbar_m T_tau]`,
`lambda = rho(1 - GammaTilde)`, `rho_c = 1/|1 - GammaTilde|`.

---

## 1. The reference error is a sufficient statistic for the cycle

**THEOREM P7-A (exact decomposition).** In the frozen repeated-cycle model both
detector arms, the lag buffer and the cycle clock are reset at every alarm, and
the innovations are iid. Hence, conditionally on `e_j`, the cycle `j` run length
is independent of everything that happened before cycle `j`, and

```text
E[tau_j]              = E[ A(e_j) ],
E[tau_j | shift Delta] = E[ A(e_j - Delta) ],
```

where `A(x) := E[tau | reset state, z_t ~ N(-x,1)]` is one detector-specific
function. Detector symmetry makes `A` even. Its decrease with `|x|` is observed
on the response grid; strict global monotonicity is not proved here.

*Proof.* The cycle's law depends on the past only through the reset detector
state (constant) and the innovation law `N(-e_j, 1)`. A process-mean shift
`+Delta` is the reference-error offset `-Delta` (`DEFINITION_AUDIT.md` §1), so
the shifted cycle is the unshifted one at argument `e_j - Delta`. ∎

The identities hold for the actual finite-cycle law of `e_j`; stationarity is
not required. Writing `E_pi` is a conditional stationary-law corollary and is
valid only if such a law exists and the required expectation is finite.

**Consequence.** Every first-moment consequence for the measured shifted cycle
is carried by the entering law of `e_j`. The measured delay is the first cycle
after the shift: its entering reference was built from pre-change observations.
Changed observations affect only the reference built after that cycle's alarm.

`A` is measured once per detector in `results/response_curves.json`; the delay
half of P7-A is validated against direct shifted-chain simulation in
`results/delay_validation.json` (eight cells, largest `|z| = 2.36`, largest
relative gap 2.9%).

## 2. The multiplier is the slope of the stopping-selection bias

Write `z_t = eps_t - e` with `eps_t` iid `N(0,1)`. Then
`zbar_m = (1/w) sum_{r<w} eps_{tau-r} - e`, so

```text
g_m(x) := E_x[zbar_m] = -x + h_m(x),
h_m(x) := E_x[ (1/w) sum_{r<w} eps_{tau-r} ]
```

**`h_m` is the stopping-selection bias**: the mean of the last `w` *raw*
innovations of the stopped path. It is odd, vanishes at `0`, and — unlike
`g_m` — is bounded (measured `sup|h| = 1.57, 1.26, 1.10, 0.91` for
`m = 1,2,3,5`; both detectors agree to about 1%).

Because `F_{rho,m}(e) = rho(e + g_m(e)) = rho·h_m(e)`, the closed theorems read

```text
GammaTilde_{D,m} = 1 - h_m'(0),
lambda           = rho(1 - GammaTilde) = rho·h_m'(0),
rho_c            = 1/|h_m'(0)|.
```

*Status:* exact algebra plus the P1/P2 theorems. `h_m` is not new mathematics;
it is the same object in coordinates that make the mechanism visible. The
conditional-mean reference map is **exactly** `rho` times the selection bias.

## 3. The chain's effective multiplier, and its exact link to `lambda`

**PROPOSITION P7-B (effective-multiplier identity).** Let the chain admit a
stationary law `pi` with `E_pi[e] = 0` and `0 < E_pi[e^2] < infinity`. Since
`E[e_{j+1} | e_j] = F_{rho,m}(e_j) = rho·h_m(e_j)` and the fresh term is
independent and centred,

```text
ACF1(e) = Cov(e_{j+1}, e_j)/Var(e_j)
        = rho · E_pi[e h_m(e)] / E_pi[e^2]
        = rho (1 - Gamma_eff),      Gamma_eff := 1 - E_pi[e h_m(e)]/E_pi[e^2].
```

`Gamma_eff -> GammaTilde_{D,m}` for a family of laws that concentrates at `0`
with enough second-moment uniform integrability to pass the local limit through
the expectation, because `h_m(e)/e -> h_m'(0)`. Under that additional limiting
condition, the P3 multiplier is the zero-dispersion limit of lag-1 reference
autocorrelation.

*Status:* the displayed identity is exact conditional on stationarity, symmetry
of `pi`, and a finite nonzero second moment. The zero-dispersion limit needs the
additional concentration condition above. The identity is supported empirically
on all 104 cells; the reported ACF is pooled and has no replicate-level interval.

## 4. Conditional mass-escape inequality

The response-grid Monte Carlo supports `e·h_m(e) <= 0` on `|e| <= 12`. P7 does
not prove this sign property globally. Define `b(e) := -e·h_m(e)`.

**CONDITIONAL PROPOSITION P7-C (mass escape).** Assume a stationary symmetric
law with finite nonzero second moment and assume `b(e) >= 0` on its support.
Then `|ACF1| <= 1` by Cauchy-Schwarz, hence

```text
E_pi[b(e)] <= E_pi[e^2] / rho.
```

Let `beta_r := inf_{0<|e|<=r} (-h_m(e)/e)`, so `b(e) >= beta_r e^2` on
`|e| <= r` and `beta_r -> GammaTilde - 1 = 1/rho_c` as `r -> 0`. Dropping the
non-negative tail,

```text
E_pi[e^2]/rho >= beta_r ( E_pi[e^2] - E_pi[e^2; |e|>r] ),
```

so whenever `rho·beta_r > 1`,

```text
E_pi[e^2 ; |e| > r] / E_pi[e^2]  >=  1 - 1/(rho beta_r).            (MASS)
```

The hypothesis `rho·beta_r > 1` is exactly P3's repulsion condition
`rho > rho_c` in the limit `r -> 0`.

**Interpretation.** Conditional on those hypotheses, local repulsion is
incompatible with keeping all second-moment mass inside the local region. The
observed smooth, high-dispersion chains are consistent with escape into a
nonlinear regime. This inequality neither proves existence or stability of a
stationary law nor proves that dispersion causes the absence of an operational
feature at `rho_c`.

## 5. A conditional Monte Carlo plug-in ARL bound

**CONDITIONAL PROPOSITION P7-D.** Under P7-C's hypotheses, a finite fourth
moment, and non-increase of `A` in `|e|`, `(MASS)` and Cauchy-Schwarz give
`E[e^2;|e|>r] <= sqrt(E[e^4] P(|e|>r))`, hence

```text
P(|e| > r)  >=  [ E[e^2] (1 - 1/(rho beta_r)) ]^2 / E[e^4],
```

and since `A` is even and non-increasing in `|e|`, `THEOREM P7-A` gives

```text
ARL_0(chain) = E_pi[A(e)]  <=  A(0) - (A(0) - A(r)) · P(|e| > r).
```

Free companion bound, from the independence of the fresh term:
`E_pi[e^2] >= (1-rho)^2/m`.

*Status:* the algebraic implication is exact under the named hypotheses, but
`beta_r`, the moments, `A(0)`, `A(r)`, the sign condition, and monotonicity are
supported only by Monte Carlo point estimates. No simultaneous confidence or
interval enclosure propagates their uncertainty. The displayed values are
therefore plug-in diagnostics, not certified bounds, and are not load-bearing
for closure.

## 6. Rejected first-order transfer shortcut

The original candidate asserted that, from
`d/d(eps) E[e_1 | e_0 = eps]|_0 = lambda`, differentiability of `M` alone would
imply

```text
d/d(eps) E[ M(e_1) | e_0 = eps ] |_0 = M'(0) · lambda.
```

That implication is false without substantially stronger control of the full
law of `e_1`: `e_1` remains random at `eps = 0`, so the derivative of its mean
does not determine the derivative of `E[M(e_1)]`. A valid result would require a
distributional derivative or score identity. P7 supplies neither. P7-E is
rejected and no closure conclusion depends on it.

## 7. The linear-response formula, and why it is not used

Inside `r_lin` the linearised recursion `e_{j+1} ~ lambda e_j + eta_j` gives

```text
Var(e) = Var(eta) / (1 - lambda^2)
       = [ rho^2 s^2 + (1-rho)^2/m ] / (1 - (rho/rho_c)^2),
```

a pole exactly at `rho_c`. It is recorded here **only to be rejected**: it
predicts divergence at `rho_c`, and the measured reference MSE varies smoothly
and is *non-monotone* through `rho_c` (`STATISTICAL_CONSEQUENCES.md` §3). The
formula fails because empirical post-burn-in RMS divided by the grid-defined
`r_lin` is about 8.1 to 27.4 over all cells and 8.2 to 18.9 at the eight exact
`rho=rho_c` cells. The chain is not concentrated in the neighbourhood the
formula describes. Reporting the pole as a
prediction would have been the main way to manufacture a boundary effect in this
campaign; it is stated and discarded on the evidence.

## 8. The bridge, assembled

```text
selection bias h_m         (response-grid evidence; odd by symmetry)
    -> lambda = rho h_m'(0)                       P1/P2/P3   [CLOSED]
    -> ACF1 = rho(1 - Gamma_eff)                     P7-B [conditional exact]
    -> local repulsion implies mass outside r        P7-C [conditional]
    -> reference dispersion  E_pi[e^2]
    -> ARL_0 = E_pi[A(e)], delay = E_pi[A(e-Delta)] P7-A [conditional on pi]
    -> ARL deficit plug-in diagnostic                         P7-D [conditional + MC]
```

P7-A is the exact structural bridge for any actual entering-error law. P7-B is
exact under its stationary-law conditions. P7-C/D additionally depend on an
empirical sign condition and Monte Carlo inputs. The chain therefore does not
prove a causal or sharp prediction of the deficit from `lambda` alone.

## 9. Explicitly not claimed

* No statement about period-2 orbits, attractors, basins, hysteresis or
  bifurcation. `ACF1 < 0` in every cell and `|ACF1|` grows with `rho`; that is
  an alternation *statistic*, not a period-2 claim. **P5 handoff.**
* No existence or uniqueness proof for `pi`. P7-B/C/D are conditional on a
  stationary law with the stated moments; the simulations exhibit rapid
  convergence but do not prove it.
* No mitigation. **P6 handoff.**
* Nothing outside the two frozen Gaussian specialisations and `m in {1,2,3,5}`.
  **P8 handoff.**
