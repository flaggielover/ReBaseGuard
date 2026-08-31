# P5 theorems — nonlinear reference-state dynamics

Every statement carries an explicit tier from the P5 theory hierarchy:

```
EXACT THEOREM | CONDITIONAL THEOREM | RIGOROUS CERTIFICATE
NUMERICAL EVIDENCE | EXPLORATORY OBSERVATION | REJECTED HYPOTHESIS
```

Proofs are in `PROOF.md`; the numerical hypotheses of the conditional theorems
are audited in `NUMERICAL_CORRESPONDENCE.md` and attacked in
`ADVERSARIAL_REVIEW.md`.

Throughout, `D in {CUSUM(k=1/2,h=5), SR(A=520.886133602749)}`, `m >= 1`,
`rho in [0,1]`, `Delta = 0`, and all conventions are those audited in
`DEFINITION_AUDIT.md`. `(e_j)` is the entering-reference-error chain.

---

## T1. Raw-mean representation  — EXACT THEOREM

For every `D`, `m >= 1`, `rho in [0,1]` and every `e_j`,

```
e_{j+1} = rho * Rbar_j + (1 - rho) * fresh_j ,
Rbar_j  = (1/w_j) * sum_{r=0}^{w_j-1} raw_{tau_j - r} ,   w_j = min(m, tau_j),
```

where `raw_1, raw_2, ...` are the iid `N(0,1)` observations of cycle `j` and
`fresh_j ~ N(0,1/m)` is independent of the cycle.

**Consequence (the P5 mechanism in one line).** The next reference error is an
average of **at most `m` standard normal observations**, plus independent
`N(0,1/m)` noise. The entering error `e_j` acts on the future *only* by
selecting which observations enter the terminal window — never additively.

## T2. rho-factorisation of the conditional-mean map  — EXACT THEOREM

With `R_{D,m}(e) = E[Rbar | e]`, `S_{D,m}(e) = Var(Rbar | e)`:

```
M_{D,m,rho}(e) = E[e_{j+1} | e_j = e]   = rho * R_{D,m}(e) ,
V_{D,m,rho}(e) = Var(e_{j+1} | e_j = e) = rho^2 S_{D,m}(e) + (1-rho)^2 / m .
```

The reuse fraction rescales the deterministic map and nothing else; the
skeleton family `f_rho = rho R` is a genuine one-parameter scaling family, and
`R'(0) = 1 - GammaTilde_{D,m}` recovers P1/P2/P3 exactly.

## T3. Symmetry  — EXACT THEOREM

`R(-e) = -R(e)`, `S(-e) = S(e)`, `A(-e) = A(e)` where `A(e) = E[tau|e]`.

## T4. Uniform geometric stopping bound  — EXACT THEOREM (explicit constants)

```
C_CUSUM := sup_{e in R} E[tau | e]  <=  10 / Phi(-1)^10   =  9.8959e8 ,
C_SR    := sup_{e in R} E[tau | e]  <=  1  / Phi(-(log A + 1/2))  =  1.4054e11 .
```

The constants are crude by construction (they are worst-case block bounds, not
the measured `sup_e A(e) ~ 465`). What matters is that they are **finite and
independent of `e`**, which is all T5–T7 use. `NUMERICAL_CORRESPONDENCE.md` §5
reports the measured `sup_e A(e)`; substituting it turns every bound below into
a realistic CONDITIONAL THEOREM.

## T5. Uniform moment bound  — EXACT THEOREM

For every integer `p >= 1`, every `D`, `m`, `rho`, and every `e`,

```
E[ Rbar^{2p} | e ]  <=  (2p-1)!! * C_D ,
E[ e_{j+1}^{2p} | e ] <= 2^{2p-1} ( rho^{2p} (2p-1)!! C_D
                                  + (1-rho)^{2p} (2p-1)!! / m^p ) .
```

In particular `sup_e E[e_{j+1}^2 | e] <= rho^2 C_D + (1-rho)^2/m =: B_{D,m,rho}`
— a **state-independent** one-step second-moment bound. There is no Lyapunov
function to construct and no outer-drift inequality to verify: the bound is
uniform over the whole state space because of T1.

## T6. Feller property by a.s. local constancy  — EXACT THEOREM

For each fixed `e`, almost surely there is a random `eps > 0` such that
`e' -> e_{j+1}(e', omega)` is **constant** on `(e-eps, e+eps)`. Consequently the
transition kernel is Feller.

## T7. Uniform ergodicity and all stationary moments  — EXACT THEOREM

For every `D in {CUSUM, SR}`, every `m >= 1` and **every `rho in [0,1]`,
including `rho = 1`**:

1. **(minorisation)** there exist `delta > 0` and a probability measure `nu`
   with
   ```
   P^2(e, .) >= delta * nu(.)      for every e in R ;
   ```
2. **(uniqueness + geometric convergence)** the chain has a unique invariant
   probability measure `pi = pi_{D,m,rho}` and is *uniformly ergodic*:
   ```
   sup_{e in R} || P^n(e, .) - pi ||_TV  <=  2 (1 - delta)^{floor(n/2)} ;
   ```
3. **(moments)** `pi` has finite moments of every order, with
   ```
   E_pi[ e^{2p} ] <= 2^{2p-1} (2p-1)!! ( rho^{2p} C_D + (1-rho)^{2p} m^{-p} ) ,
   ```
   in particular a finite second **and fourth** moment, bounded uniformly in
   `rho`;
4. **(no runaway in distribution)** consequently
   `P_pi(|e| > r) <= E_pi[e^2]/r^2`; from every initial state the marginals are
   uniformly tight after one step and the chain cannot converge to infinity.
   This does not claim bounded sample paths; the invariant law has unbounded
   support.

> **This closes, for the frozen Gaussian core, the five stationary-law gaps that
> P7 explicitly left open** (existence, second moment, uniqueness/ergodicity,
> fourth moment, geometric convergence). P7's conditional results that assumed
> "existence of a stationary law with finite fourth moment (evidenced, not
> proved)" are hereby unconditional in this model.

The explicit `delta` is astronomically small (it inherits `C_D`); the theorem is
qualitative. Quantitative mixing is reported as NUMERICAL EVIDENCE
(`STATIONARY_DYNAMICS.md` §4: measured integrated autocorrelation time of 1–3
cycles).

---

## The nonlinear map and the skeleton

The following use measured properties of the fixed function `R_{D,m}` as
hypotheses. They are stated as CONDITIONAL THEOREMS with the hypotheses
isolated, and the hypotheses are separately certified on the measured grid.

**Measured hypotheses (see `NONLINEAR_MAP.md`).**

```
(H1)  R is continuous and odd                          [T3 exact; verified]
(H2)  R(e) < 0 for all e > 0
(H3a) s(e) := -R(e)/e is continuous and strictly decreasing on (0,2],
      with s(0+) = GammaTilde - 1 = 1/rho_c and s(2) < 1
(H3b) sup_e |R(e)| < 2
```

## T8. Global fixed-point uniqueness  — CONDITIONAL THEOREM  (H1,H2)

For every `rho in (0,1]` the deterministic skeleton `f_rho(e) = rho R(e)` has
**`e = 0` as its unique fixed point**, for every `D` and `m`. There is no
saddle-node, transcritical or pitchfork bifurcation anywhere in `rho in (0,1]`,
and there are no stable non-zero equilibria.

## T9. Symmetric period-2 branch — CONDITIONAL THEOREM (H1–H3)

Symmetric 2-cycles `{e*, -e*}` of `f_rho` are **exactly** the solutions of

```
s(e*) = 1 / rho .
```

Hence, with `rho_c = 1/s(0+) = 1/|1 - GammaTilde|` the frozen P3 critical
fraction:

* `rho <= rho_c` : no symmetric 2-cycle; `0` is locally attracting;
* `rho >  rho_c` : **exactly one** symmetric 2-cycle `+/- e*(rho)`, with
  `e*` strictly increasing in `rho` and `e*(rho) -> 0` as `rho -> rho_c+`;
* the branch multiplier is `mu(rho) = rho^2 R'(e*)^2` (`R'` is even because `R`
  is odd), and the 2-cycle is attracting iff `rho |R'(e*(rho))| < 1`.

Thus H1--H3 give a continuous symmetric period-2 branch on the supercritical
side of the local multiplier crossing. Calling it an **attracting
supercritical flip** additionally requires attraction/nondegeneracy conditions
not proved here. Attraction and the absence of asymmetric cycles are numerical
evidence from the measured PCHIP map.

## T10. Noise-floor invisibility of the flip bifurcation  — CONDITIONAL THEOREM (H1–H3, plus `S` continuous at 0)

Define the skeleton signal-to-noise ratio on the bifurcating branch

```
SNR(rho) := e*(rho) / sqrt( V_{D,m,rho}(e*(rho)) ) ,
V_{D,m,rho}(e) = rho^2 S(e) + (1-rho)^2/m .
```

Then

```
lim_{rho -> rho_c+}  SNR(rho) = 0 ,
```

because the emerging orbit amplitude `e*(rho) -> 0` while the noise floor tends
to `sqrt( rho_c^2 S(0) + (1-rho_c)^2/m ) > 0`, which is bounded away from zero.

> This conditional asymptotic shows that the emerging deterministic branch is
> small relative to the one-step stochastic noise floor. It is consistent with
> P7's negative operational-boundary result, but it does not prove that every
> statistic of the stochastic chain is featureless at `rho_c`.

## T11. Exact identity for P7's effective gain  — EXACT THEOREM (given `pi`, which T7 supplies)

Let `pi` be the invariant law of T7 and suppose `E_pi[e^2] > 0`. Then the
stationary lag-1 autocorrelation of the reference-error chain is **exactly**

```
ACF1  =  Cov_pi(e_{j+1}, e_j) / Var_pi(e)
      =  rho * ( 1 - Gamma_eff ) ,        Gamma_eff := 1 + sbar ,
sbar  :=  E_pi[ e^2 s(e) ] / E_pi[ e^2 ]      (if E_pi[e] = 0).
```

That is: P7's empirical relation `ACF1 = rho(1 - Gamma_eff)` is an identity, and
P5 **identifies** `Gamma_eff`: it is `1 +` the `e^2`-weighted stationary average
of the secant gain `s`. Because `s` is strictly decreasing (H3) with
`s(0+) = GammaTilde - 1` and the stationary dispersion is `O(1)` — far outside
the linearisation radius — Jensen-type comparison gives

```
sbar  <<  s(0+) = GammaTilde - 1     whenever pi charges the saturated region,
```

which is exactly P7's measured 5x–25x overshoot of `lambda` over `ACF1`.
The overshoot is therefore **not** a modelling error: it is the difference
between the tangent gain at `0` and the stationary secant gain.

## T12. Rejected hypotheses  — REJECTED HYPOTHESIS

| hypothesis | status |
|---|---|
| `rho > rho_c` implies unbounded/runaway reference error | **rejected** by T5/T7: the state has uniformly bounded moments of every order at every `rho <= 1` |
| local repulsion at `0` is globally destabilising | **rejected**: `M(e) -> 0` as `|e| -> infinity` (H2/H3 + T1); the map saturates |
| the observed high dispersion is a Foster–Lyapunov outer-drift phenomenon needing a drift function | **rejected as unnecessary**: T1 gives a *state-independent* one-step moment bound, strictly stronger than any outer-drift condition |
| the P3 boundary should show an operational signature under P7's frozen criterion | **rejected empirically by P7 and the P5 grid**; T10 is consistent with this result but does not prove it |
| multiple invariant measures | **rejected** by T7(2): the invariant law is unique for every `(D,m,rho)` in the frozen core |
| multiple deterministic attractors | none found on the measured PCHIP scan; not rejected by T7 |
| a pitchfork / saddle-node / transcritical bifurcation in `rho` | **rejected** by T8 |
| period-doubling cascade to chaos on `rho in (0,1]` | see `NONLINEAR_MAP.md` §6 — the 2-cycle multiplier stays `< 1` on the measured grid; no further doubling on `[0,1]` |
