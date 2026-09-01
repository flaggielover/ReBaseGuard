# P9 statistical audit

P9 performs **no hypothesis test**. Its computations are reproductions and
consistency checks, so this audit is mostly about what P9 declined to do.

## 1. Replicate-level uncertainty

All A4/A5 standard errors are computed **across paths** on the *per-path* cycle
mean, never across pooled cycles. Cycles within a path are dependent — that
dependence *is* the phenomenon under study (`P5-T11`: `ACF1 = rho(1-Gamma_eff)`)
— so pooling cycles as independent replicates would understate the SE. This is
the one statistical choice that materially affects the reported intervals.

Anchor A6's SEs are across paths within a grid node. The quadrature's own
truncation and grid error is **not** quantified, which is exactly why A6 is
reported as *agreement* and never as an identity check.

## 2. Seeds

Every seed is derived deterministically as
`SHA-256(label | detector | m | rho)[:8]`. No seed was chosen by hand, tried and
replaced, or selected after seeing a result. The derivation function is in
`experiments/reproduce_anchors.py` and is used by every anchor.

## 3. Effect sizes and intervals

| comparison | effect | uncertainty |
|---|---|---|
| nominal `A(0)` vs fresh `rho=0` ARL, CUSUM `m=1` | `468 -> 82` | SE `4.07` / `0.52` |
| fresh vs full reuse, CUSUM `m=1` | `82.08 -> 47.90`, `41.6%` | SE `0.52` / `0.37` |
| `A(0)` vs `A(1 sigma)`, CUSUM `m=1` | `468 -> 10.35` | across-path SE at each node |
| burn-in convention, SR `m=1` | `46.96 -> 48.49` (discard 1 → 10); pooled `67.64` | `~40%` inflation from pooling |

The second row is the reuse-attributable effect; the first is **not** (`X-05`).

## 4. Multiple comparisons

**No correction is applied, because no test is performed.** A4/A5/A6 report
point estimates with standard errors and are interpreted descriptively. Applying
a multiplicity correction would imply a testing frame that does not exist here
and would misrepresent the analysis. Where P9 quotes a `z` (`D-12`, `z = -3.09`)
it is used as a *distance in standard errors* to decide whether to investigate,
not as a test statistic, and the investigation's outcome is reported either way.

## 5. Incompatible standard errors — the trap P9 avoided

P9 does **not** compare its own SEs against P1–P7 SEs where the definitions
differ:

* P1/P2 gain SEs are **across-batch** SEs of a score-route expectation.
* P3's `rho_c` intervals are **delta-method transforms** of those.
* P7's operational SEs are across-replicate on cycle statistics.
* P9's A4 SEs are across-path on per-path cycle means.

These are not interchangeable. Where P9 compares to a published value it either
uses an exact tolerance (A1–A3) or reports the published *range* alongside its
own point estimate and SE (A4), rather than forming a combined `z` across
incompatible SE definitions.

## 6. Grid-selection caveats

* A6's `A(e)` grid is 81 half-grid nodes truncated at `5 sigma`; the mixture is
  renormalised for the truncated mass. Truncation error is not quantified.
* A5's burn-in table is a **descriptive** sweep over discard conventions, not a
  selection of the most favourable one. All five conventions are reported,
  including `pool all cycles`, which is the least favourable to P9's
  reconciliation of `D-11`.
* The monotonicity test of `P7-A`'s premise uses a `3 SE` tolerance on adjacent
  nodes. It is a **corroboration**, not a proof: it cannot detect a violation
  smaller than the node spacing or the Monte Carlo noise floor.

## 7. Approximate agreement is never called identity

Per prompt §19 and `CLAIM_LANGUAGE_POLICY.md`:

* A1 and A3 **are** identities and are called so: exact rational arithmetic, and
  a machine-precision algebraic residual of `8.882e-16`.
* A2 is exact algebra on rounded published inputs; the `4.882e-10` residual is
  attributed to the published table's 9-decimal rounding, not called exact.
* A4 and A6 are **agreement**, never identity. `D-11` is a resolved *convention*
  difference, not a reproduced identity.
* `P5-T11`'s `<= 3.5%` map-vs-chain agreement is **never** quoted without the
  accompanying "up to 16 chain standard errors" (`D-13`, `OPEN`).

## 8. The discarded first attempt

The A6 mixture was first computed with 21-node Gauss-Hermite quadrature and
returned `134.19` against a measured `82.08`. This was a **quadrature-resolution
failure**, not a result: `A(e)` falls from `468` to `10.35` within one standard
deviation, and the node at `e=0` carries enough weight to dominate the sum.

It is reported in `CROSS_PRIORITY_REPRODUCTION.md` §A6 and
`EXPERIMENT_PROTOCOL.md` §4 rather than deleted. Silently replacing a method
that disagreed with a method that agreed — without saying so — is selective
reporting, whatever the diagnosis.

## 9. What P9's numbers cannot support

* No claim about `rho` between `0` and `1` other than at the two endpoints run.
* No claim about `m` outside `{1, 2, 5}`.
* No claim about any non-Gaussian innovation family — P9 ran none.
* No claim about detectors other than the two frozen ones.
* No rate constant for `P5-T7`'s geometric ergodicity: `P9-N1` measures a
  transient in two cells, which is an observation, not a bound.
