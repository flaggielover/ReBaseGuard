# Priority-3 evidence boundary

This file exists so that no reader can confuse a theorem-supported
classification computed from a Monte Carlo gain with an interval-certified one.

## Hierarchy

| rank | class | meaning | where it occurs in this campaign |
|---:|---|---|---|
| 1 | `EXACT_SYMBOLIC` | closed-form rational value | gains of both finite-support witnesses; their `rho_c`; the boundary identity `|lambda(rho_c)|=1` |
| 2 | `INTERVAL_CERTIFIED` | rigorous Arb enclosure at 128 bits | every witness-layer grid cell's magnitude; the SR witness stopping times |
| 3 | `THEOREM_PLUS_CERTIFIED_INPUT` | closed derivative theorem applied to an exact/certified gain | every `CUSUM-witness` and `SR-witness` cell |
| 4 | `THEOREM_PLUS_EMPIRICAL_ESTIMATE` | closed derivative theorem applied to a Monte Carlo gain | every `CUSUM` and `SR` cell whose 95% interval does not straddle unit magnitude |
| 5 | `EMPIRICAL_ONLY` | Monte Carlo estimate with no theorem attached | the imported gains themselves, before the theorem is applied |
| 6 | `INCONCLUSIVE` | linearization or evidence does not determine the class | any cell whose magnitude interval contains 1, including every cell placed at an estimated `rho_c` |

Ranks 1–3 are rigorous. Rank 4 is rigorous *given* the gain, and the gain is
not rigorous. The separation is enforced mechanically:
`results/stability_map.json` carries `gamma_evidence_class` and
`evidence_class` on every cell, and `derive_closure.py` fails the campaign if
any `EMPIRICAL_ONLY` gain ever produces a `THEOREM_PLUS_CERTIFIED_INPUT` cell.

## What is certified

- The generic map algebra of `THEOREM.md` and `PROOF.md`, machine-checked in
  Lean with only `propext`, `Classical.choice` and `Quot.sound`.
- For the Priority-1 finite-support witness: gain `15/2` at every supported
  `m`, `rho_c = 2/13`, and the class of every grid reuse fraction, at 128-bit
  Arb precision with the exact rational values as the primary evidence.
- For the Priority-2 SR-compatible witness: stopping times `1,1,6,6`
  re-derived in interval arithmetic from the frozen increments, gain `2+2/m`,
  `rho_c = m/(m+2)`, and the class of every grid reuse fraction, including the
  exact boundary cell at `m=3`, `rho=3/5`.
- That the `m in {2,3,5}` witness gains recomputed here are identical to the
  values already recorded by the Priority-1 and Priority-2 certificates.

## What is not certified

- **The frozen infinite-horizon Gaussian gains.** `GammaTilde_m` for the
  Gaussian two-sided CUSUM and `GammaTilde_m^SR` for the Gaussian SR detector
  are Monte Carlo estimates carried over unchanged from the two closed
  campaigns. They have batch standard errors and no rigorous enclosure. Every
  boundary, interval and class derived from them is empirical in that exact
  sense.
- **Anything about detectors outside the two frozen specializations**, about
  non-Gaussian innovations, or about window lengths outside `m in {1,2,3,5}`.
- **Anything nonlinear or global.** The map classifies the linearization of the
  conditional-mean reference map at `e=0`. It says nothing about convergence
  from arbitrary initial conditions, about basins of attraction, about the
  stochastic repeated-monitoring chain, or about existence or uniqueness of a
  stationary law.
- **Any operational claim.** Stage-D D2.5 remains the controlling operational
  negative result; nothing here supersedes it.

## The finite-support witnesses are not the Gaussian detectors

Both witnesses are exact finite-support probability models that instantiate the
same abstract derivative theorem. The Priority-1 witness is not an instance of
the Gaussian likelihood formula, and the Priority-2 witness runs at threshold
`A=2` rather than the frozen `A=520.886133602749`. Their certified boundaries
(`2/13`, and `m/(m+2)`) are therefore *not* estimates of the Gaussian
boundaries (`~0.067`–`0.108` and `~0.061`–`0.100`), and the map keeps them in
separate layers for exactly that reason. The certified layers demonstrate that
the map machinery is rigorous; they do not transfer rigour to the Gaussian
rows.

## Uncertainty handling

The 95% intervals use `z95 = 1.959963984540054` and the across-batch standard
errors recorded verbatim in the two closed packages. The estimand is the frozen
infinite-horizon gain `E_0[A_m T_tau]`; the assumptions are independent equally
sized batches and a central-limit normal approximation for the batch mean. No
re-estimation, resampling or confidence level is invented here.

A classification is reported as robust only when the induced magnitude interval
does not contain `1`. On the candidate-declared fixed grid exactly one cell
fails that test — Gaussian SR at `m=5`, `rho=0.10`, magnitude interval
`[0.99681, 1.01290]` — and it is recorded as `INCONCLUSIVE` rather than as a
repelling cell. All sixteen cells placed exactly at an estimated or exact
`rho_c` are boundary cells; the eight empirical ones are additionally
`INCONCLUSIVE`, while the eight witness ones are exact.
