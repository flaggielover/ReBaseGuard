# Lean correspondence and analytic-assumption audit

**Compile:** `PASS`

**Axiom audit:** `PASS`
**Classification:** B — algebraic consequence of the existing general
dominated-differentiation lemma, not a fully instantiated CUSUM theorem

## 1. Target map

| Target | Lean declaration | Checked content |
|---|---|---|
| L1 | `windowLength`; `windowLength_eq_tau_of_lt`; `windowLength_eq_m_of_le` | `w=min m tau` and its two branches |
| L2 | `directTerm_eq_fixed_add_shortCorrection` | partition on `tau<m` versus `m<=tau` |
| L3 | `directTerm_short` | under the whole-path premise `S=T`, the short statistic is `T/tau` |
| L4 | `directTerm_eq_fixed_add_shortCorrection`; `integral_direct_eq_fixed_add_correction` | pointwise and expectation-level decompositions |
| L5 | `shortCorrection_nonneg` | correction nonnegativity for positive `m,tau` |
| L6 | `windowLength_one`; `directTerm_one`; `shortCorrection_one` | exact `m=1` reduction |
| L7 | `reuseMap_apply`; `reuseMap_zero`; `reuseMap_one` | exact affine rho scaling |
| L8 | `rho_derivative_of_expectation_derivative`; `derivative_spine_of_dominated` | derivative-map algebra and reuse of the generic stopped-integral bridge |

The source is `lean/MGtOneTrack1B.lean`. It contains no `sorry`, `admit`, or
new `axiom` declaration.

## 2. What Lean proves

`derivative_spine_of_dominated` calls the already proved theorem
`RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero`. Given functions
`A`, `T`, and real-valued `tauR`, it proves

`d/de [rho(e + integral A exp(-eT-e^2 tauR/2))]|_0`

`=rho(1-integral A T)`

provided the listed analytic hypotheses hold. The rho algebra, signs,
short/long partition, decomposition, and integral addition are checked by
Lean.

## 3. What remains outside the Track 1B Lean theorem

The concrete frozen CUSUM probability space and stopped-path constructor are
not instantiated. In particular, Track 1B does not machine-check:

- that its abstract `A` is exactly the random-window statistic `A_m`;
- a.e. strong measurability of that concrete `A_m`, `T_tau`, and `tau`;
- integrability of the concrete `A_m`; or
- existence of the uniform integrable derivative dominator for that concrete
  `A_m`.

The short-cycle theorem also takes the mathematical stopped-path fact
`tau<m -> S=T` as an explicit premise; the generic real-valued algebra does
not construct `S` from a path.

These are load-bearing analytic assumptions for the concrete application.
They are supported by the human theorem and prior stopped-moment work, but the
complete concrete derivative theorem must not be called machine-checked.

## 4. Axiom output

`lean/AxiomAudit.lean` prints:

```text
directTerm_eq_fixed_add_shortCorrection: [propext, Classical.choice, Quot.sound]
shortCorrection_nonneg: [propext, Classical.choice, Quot.sound]
integral_direct_eq_fixed_add_correction: [propext, Classical.choice, Quot.sound]
derivative_spine_of_dominated: [propext, Classical.choice, Quot.sound]
```

These are Mathlib/Lean standard logical axioms. There are no scientific or
Track-1B-specific axioms.

## 5. Reproduction hook

`reproduce.sh` compiles the main source with the pinned Lake environment,
builds a temporary local `.olean`, runs the standalone `#print axioms` audit,
checks that only the three allowed standard axioms appear, and removes the
temporary object on exit.
