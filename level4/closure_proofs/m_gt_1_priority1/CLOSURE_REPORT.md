# Level-4 Priority 1 closure report

## Overall verdict: CLOSED

This verdict means exactly:

> Level-4 Priority 1 -- the general Stage-D `m > 1` derivative theorem and its
> specified two-tier validation package are closed.

It does **not** mean that frozen infinite-horizon Gaussian CUSUM values for
`m>1` are interval-certified. They are not.

## 1. Analytical theorem closure -- PASS

`DEFINITION_AUDIT.md` establishes the authoritative ordinary stopping time,
inclusive post-update alarm, terminal inclusion, `w_m=min(m,tau)`, and random
denominator. It proves that Stage A's minimum-dwell process is distinct for
`m>1` and coincides only at `m=1`.

`THEOREM.md` and `PROOF.md` independently prove, under explicit stopped-
likelihood, measurability, integrability, and local-domination assumptions,

```text
F'_{rho,m}(0)=rho(1-GammaTilde_m),
GammaTilde_m=E_0[A_m T_tau].
```

The proof retains the random denominator, partitions `{tau<m}` and
`{tau>=m}`, and derives the exact nonnegative short-cycle correction. It states
attraction, repulsion, and the inconclusive equality case correctly.

## 2. Lean proof-spine closure -- PASS

`lean/MGtOneClosure.lean` compiled with the pinned Lean 4.34.0-rc1 toolchain.
The new namespace contains the window partition, correction identity and
nonnegativity, expectation decomposition, `m=1` reduction, rho scaling,
dominated Gaussian-likelihood derivative spine, and multiplier criteria.

The axiom audit contains only `propext`, `Classical.choice`, and `Quot.sound`.
There is no `sorry`, `admit`, scientific axiom, or Track 1B import.

Lean consumes abstract measurability, integrability, and domination
hypotheses. It does not prove the concrete frozen-CUSUM stopped exponential
moment or domination conditions; those remain explicit human analytic
obligations.

## 3. Frozen Gaussian CUSUM numerical correspondence -- PASS

The preregistered independent implementation evaluated `m={1,2,3,5}` and
`rho={0.05,0.1,0.25}` with three finite-difference steps, pilot/final sample
escalation, disjoint seed families, and fixed tolerances. All 12 cells passed
smallest-step agreement, Richardson agreement, convergence, precision, and
finite-value gates.

The score-route estimates were:

```text
m             1          2          3          5
GammaTilde  15.91654   13.26482   11.95708   10.22636
```

These are Monte Carlo estimates. Short, equal, and long paths are reported,
and deterministic fixtures cover every denominator branch.

## 4. Finite-support Arb certification -- PASS

The exact witness and rational inputs were hash-frozen before evaluation. The
normalized exponential tilt is analytically a valid probability family: its
finite positive normalizer is strictly positive, normalized masses sum to one,
and sign symmetry gives `E_0[T_tau]=0`, so the score at zero is exactly
`-T_tau`.

At 128-bit Arb precision, every `m` in `{2,3,5}` certified

```text
GammaTilde_m=15/2,
F'_{1/10,m}(0)=-13/20  (attracting),
F'_{1/4,m}(0)=-13/8    (repelling).
```

Normalization, score, decomposition, correction sign, derivative identity,
dyadic finite-difference convergence, attraction, and repulsion all passed.
This rigorous certificate applies only to the finite-support witness.

## 5. Frozen-history and inheritance integrity -- PASS

Track 1B, historical D2.3, the Stage-D decision, Track 1A's failed decision,
and the historical `m_gt_1/` partial campaign are unchanged. Hash gates pass.
The new campaign is isolated in the sibling `m_gt_1_priority1/` namespace
because the historical tree is hash-protected in its entirety.

The inheritance ledger distinguishes frozen definitions, read-only prior
evidence, generic Lean infrastructure, and newly produced evidence. Track 1B
is a regression anchor only.

## Verification

- Focused campaign suite: 13 passed.
- Full Level 1–3 verifier: all checks passed, zero skipped.
- Level-4 suites passed through Stages A--F, post-closure re-audit, and D4;
  external-validation V3, L4R-06, and L4R-12 also passed independently.
- The repository-wide Level-4 verifier remains nonzero because its novelty,
  external-validation V2, final-global, and terminal audits expect a historical
  `sr_derivative` tree of 52 files while the current repository tracks 92
  files from later committed SR work. This mismatch predates and is outside
  this campaign; it is preserved in `results/verification.json` and was not
  repaired or reinterpreted.
- Immutable Track 1B regression suite: 32 passed. The older partial `m_gt_1`
  suite has 44 passes and two bookkeeping failures: its stored Lean-tree hash
  predates later committed Lean work, and its worktree-scope test rejects any
  sibling campaign. Its scientific files remain git-clean.

The unrelated SR hash mismatch is not a Priority-1 gate and does not affect
the five passing categories above.

## Remaining boundaries and future strengthening

- Concrete Gaussian-CUSUM analytic domination is human-level, not instantiated
  end-to-end in Lean.
- Frozen Gaussian `m>1` values have statistical uncertainty and no rigorous
  interval enclosure.
- A multidimensional infinite-horizon Arb certificate for those Gaussian
  values is future strengthening only.
- No SR theorem, global `(m,rho)` map, or location-family theorem was started.
