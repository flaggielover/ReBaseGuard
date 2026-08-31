# P5 limitations

What P5 does **not** establish, stated as precisely as what it does.

## 1. Scope

* Frozen Gaussian core only: two-sided CUSUM `k=1/2, h=5` and symmetric two-chart
  SR `A=520.886133602749`, iid `N(0,1)` observations, `Delta = 0`,
  `rho in [0,1]`, `m in {1,2,3,5}`. Non-Gaussian innovations, contaminated data,
  other detectors and other reuse conventions are **P8**, not P5.
* Only the *in-control* reference chain is studied. The shifted-process
  behaviour enters solely through P7's response function; P5 does not re-measure
  detection delay.
* The Stage-D **convention A** window (`w = min(m, tau)`, denominator `w`,
  terminal increment included) is essential. The raw-mean identity T1 — and
  hence essentially every P5 theorem — **fails** for a fixed-`m` denominator on
  a truncated window. P5 says nothing about that convention.

## 2. What is proved vs what is measured

| statement | tier |
|---|---|
| T1 raw-mean identity, T2 `rho`-factorisation, T3 symmetry | EXACT THEOREM |
| T4 uniform `E[tau]` bound, T5 uniform moment bound, T6 Feller | EXACT THEOREM |
| T7 unique invariant law, uniform ergodicity, all moments finite | EXACT THEOREM |
| T11 `ACF1 = rho(1 - Gamma_eff)`, `Gamma_eff = 1 + sbar` | EXACT THEOREM (uses T7's `pi`) |
| T8 unique fixed point, T9 symmetric 2-cycle branch, T10 zero branch SNR at `rho_c` | CONDITIONAL THEOREM on measured (H1)–(H3); attraction/full flip classification is numerical |
| the Lean spine (12 declarations, sorry-free, three standard axioms) | RIGOROUS CERTIFICATE of the T8–T10 *algebra only* |
| the shape of `R`, `S`, `A`; the dispersion law; the bimodality onset; mixing | NUMERICAL EVIDENCE |
| runaway behaviour, multiple attractors, cascades, saddle-node/pitchfork | REJECTED HYPOTHESIS |

**(H2) and (H3) are not proved.** They are measured on a finite grid with batch
standard errors and replicated on an independent seed family. A proof of
`R(e) < 0` for `e > 0`, or of the monotonicity of `s` on `(0,2]`, from the
detector recursions is **open**. It would upgrade T8–T10 from conditional to
exact and is the single most valuable remaining theoretical target in P5's
territory.

## 3. The theorem constants are vacuous as rates

`C_CUSUM <= 9.8959e8` and `C_SR <= 1.4054e11` against measured values of `465.2`
and `464.4`. The Doeblin constant `delta'` inherits this and is astronomically
small, so T7's total-variation rate `2(1-delta')^{floor(n/2)}` is useless
numerically. T7's *content* — existence, uniqueness, ergodicity, finite moments
of every order, no runaway — does not depend on the constants. Measured mixing
(integrated autocorrelation time `<= 1` cycle) is reported separately and is not
used inside any proof.

A sharpening exists and is **not claimed**: assuming the measured
`sup_e A(e) = 465.2 / 464.4` as a hypothesis turns T5 and T7 into CONDITIONAL
THEOREMS with realistic constants. Proving `sup_e E[tau|e] = E[tau|0]` (i.e.
that the in-control ARL is the maximum over `e`) would make that unconditional;
P5 did not attempt it.

## 4. `rho = 1` and the minorisation

The two-step Doeblin argument covers `rho = 1` because it uses the `{tau = 1}`
event rather than the fresh-noise term. That was not obvious at the outset and
is the reason the minorisation is placed on the compact return set rather than
globally. The global one-step Doeblin condition holds only for `rho < 1`; P5
states the two-step version, which is uniform in `rho`.

## 5. Delay tails are *not* explained by a heavy-tailed reference law

The stationary reference law is **platykurtic** at every `rho` measured (excess
kurtosis from `-0.01` at `rho=0` down to `-1.02` at `rho=0.8`, never positive).
P7's heavy detection-delay tail therefore cannot be attributed to heavy tails in
`e`. P5's positive statement is only that `pi` has `O(1)` dispersion far outside
the linearisation radius; the mapping from that dispersion to the delay tail
runs through P7's response function `A(e - Delta)` and its convexity, which P5
did **not** re-derive. Anyone using `E_pi[A(e - Delta)]` must do so under P7-A's
exact conditions.

## 6. Numerical gaps left open

* **T11 cross-check.** Independent adjudication recorded the realised terminal
  raw mean in the worst cell and matched the identity within paired Monte Carlo
  error. The former `0.0174` residual is a gridded-map/PCHIP plug-in discrepancy;
  the prediction's full interpolation error budget remains unquantified.
* **Oddness residual.** Up to `1.6 x` a `t_7` batch interval, absolute size
  `<= 0.011` (`<0.7%` of `sup|R|`). Consistent with an 8-batch interval
  calibration effect; not fully resolved.
* **Slope bias.** P5's `R'(0)` is one-signed below P3's `1 - GammaTilde` by
  `0.14%–1.6%` in 8/8 cells, reproduced across seed families. A
  finite-difference artifact, not chased to ground.
* **`s` monotonicity beyond `e = 2`.** `s` is *not* globally monotone: a
  secondary lobe of `|R|` near `|e| ~ 5.5-7` makes `s` rise slightly between
  `e = 4` and `e = 5`. This is irrelevant to `rho in (0,1]` (which only probes
  `s >= 1`) and is handled by the `sup|R| < 2` tail bound, but it means (H3)
  must never be quoted globally.

## 7. No interval certification

No Arb / interval-arithmetic certificate was produced. The natural target would
be a rigorous enclosure of `R` on a grid, which would turn (H2)/(H3) into
verified-on-a-grid statements; that requires rigorous bounds on a stopped
expectation of a two-sided detector and was judged out of proportion to its
value here. The Lean spine certifies the *algebra* that consumes (H1)–(H3), not
the hypotheses themselves.

## 8. Not formalised

T1, T3–T7 and T11 — the entire probabilistic content — are human-proved only.
Formalising a Markov-chain Doeblin argument, Wald's identity for a stopped sum
and a Feller property was judged a poor use of P5's budget; the Lean spine
covers the deterministic skeleton logic where formalisation is cheap and the
risk of a subtle error (an "obvious" monotonicity, a mis-stated bifurcation
condition) is highest.
