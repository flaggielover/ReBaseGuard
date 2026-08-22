# Track-3B Lean correspondence and analytic boundary

## Status

```text
Lean source: COMPILED
Axiom audit: CLEAN
Classification: conditional formal proof spine
```

Compilation used the repository-pinned Lean `v4.34.0-rc1` and Mathlib
`v4.34.0-rc1` environment.  The proof source is
`lean/LocationFamilyTrack3AB.lean`; the standalone inventory is
`lean/AxiomAudit.lean`.

## Exact declarations

| Declaration | Scientific role |
|---|---|
| `parameterScoreSum_eq_neg_conventional` | fixes `s=-psi` and the stopped-sum sign |
| `stoppedScore_derivative_bridge` | exposes the conditional expectation derivative under analytic hypotheses |
| `rho_scaling` | derives exact affine reuse scaling |
| `locationFamily_derivative_spine` | gives derivative `rho(1-Gamma_f)` from the stopped-score bridge |
| `reflectPath_involutive` | finite-path sign reflection is an involution |
| `conventionalScoreSum_reflection` | odd score sums negate under reflection |
| `reflected_stopped_gain` | product of odd terminal and score sum is reflection invariant |
| `reuseMean_odd` | odd terminal mean implies odd conditional reuse map |
| `gaussian_score_specialization` | standard-Gaussian conventional score is `z` |
| `gaussian_score_sum_specialization` | Gaussian stopped score sum is the residual total |
| `gaussian_gain_specialization` | general gain becomes `Z_tau T_tau` |
| `gamma_threshold_derivative_lt_neg_one` | `rho>0`, `Gamma>1+1/rho` implies derivative `<-1` |
| `gamma_gt_two_full_reuse_derivative_lt_neg_one` | full-reuse `Gamma>2` specialization |
| `raw_gain_ne_terminal_score_gain` | raw and terminal-score gains differ off terminal equality |
| `gaussian_terminal_gain_eq_raw` | Gaussian score equality removes that distinction |

The standalone axiom audit prints the 14 load-bearing declarations; the
simple definitional `gaussian_score_specialization` is compiled and covered by
the two audited Gaussian consequence theorems.

## Correspondence to the human theorem

Lean represents

```text
Gamma_f = integral (terminal * conventional stopped-score sum),
terminalMean'(0) = -Gamma_f,
reuseMean rho terminalMean e = rho * (e + terminalMean e).
```

`locationFamily_derivative_spine` then machine-checks

```text
F'_rho(0)=rho(1-Gamma_f).
```

The correctly signed parameter-score sum is separately checked to be the
negative of the conventional location-score sum.  The Gaussian declarations
reduce `psi(z)` to `z`, so the general gain reduces to the existing
`E[Z_tau T_tau]` quantity.

## Explicit analytic boundary

The theorem is conditional.  Lean takes the stopped-score expectation
derivative as an explicit `HasDerivAt` bridge and makes terminal/score
measurability plus gain integrability visible in its interface.  It does not
construct or instantiate the concrete infinite t3 CUSUM process.

The following remain human-proved for the concrete t3 process:

- residual-path stopping and terminal measurability;
- parameter independence of the detector functional;
- almost-sure finiteness and the geometric stopping-tail argument;
- finite-prefix likelihood differentiation and stopped change of measure;
- integrability and absolute event-slice summability; and
- domination of stopped likelihood difference quotients.

Accordingly the result is not described as an end-to-end formalization of the
concrete infinite process.  It is a reusable algebraic/stopped-score proof
spine under explicit analytic hypotheses.

## Axiom inventory

Every audited declaration depends only on:

```text
propext
Classical.choice
Quot.sound
```

There is no `sorry`, `admit`, `sorryAx`, project-specific axiom, or scientific
postulate in the Lean source.
