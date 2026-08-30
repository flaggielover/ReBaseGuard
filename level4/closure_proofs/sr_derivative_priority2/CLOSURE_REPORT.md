# Level-4 Priority 2 closure report

## Overall verdict

```text
Level-4 Priority 2 -- CLOSED
```

Meaning:

> Level-4 Priority 2 -- the Shiryaev--Roberts derivative theorem and its
> declared validation package are closed.

This does not mean all SR theory, the global stability map, Priority 3, or
Level 4 as a whole is closed. Frozen infinite-horizon Gaussian SR `m>1` values
are not interval-certified.

## 1. SR definition and history audit — PASS

The authoritative detector is reset symmetric two-chart SR:

```text
R_t^+=(1+R_{t-1}^+)exp(Z_t-1/2),
R_t^-=(1+R_{t-1}^-)exp(-Z_t-1/2),
tau=inf{t>=1:max(R_t^+,R_t^-)>=A}.
```

The threshold is natural-unit `A=520.886133602749`; both charts update before
the inclusive comparison; the terminal increment is included; there is no
head-start. The ordinary Stage-D window is `w_m=min(m,tau)` and is not the
Stage-A minimum-dwell process.

Separate manifests reproduce the 52-file terminal-Level-4 tree and the
92-file additive SR-certificate tree. All original 52 blobs are identical in
the later tree, and Priority 2 changes neither protected tree.

## 2. Analytical SR theorem closure — PASS

Under `Q_e`, residuals are iid `N(-e,1)`. On the stopped sigma-field,

```text
L_e=exp(-eT_tau-e^2tau/2),
dL_e/de|_0=-T_tau.
```

The SR-specific forcing inequality `|Z|>=log(A)+1/2` gives a uniform geometric
tail near zero. It supplies the stopped exponential moment used to prove
integrability of `A_m`, `A_mT_tau`, and an integrable local derivative
dominator. Reflection exchanges charts, preserves `tau`, negates `A_m,T_tau`,
and centers the map.

All eight pre-registered analytical obligations are `PROVED`; none is
discharged numerically. Therefore

```text
GammaTilde_m^SR=E_0[A_mT_tau],
F'_{rho,m}(0)=rho(1-GammaTilde_m^SR).
```

The proof retains the random denominator and proves the exact nonnegative
short-cycle correction. Attraction holds below unit multiplier magnitude,
repulsion above it, and equality is inconclusive from linearization alone.

## 3. Lean proof-spine closure — PASS

`SRPriority2.lean` compiles under the pinned toolchain. It formalizes SR
reflection, inclusive finite first alarms, the short/full window partition,
denominator decomposition, correction nonnegativity, expectation
decomposition, `m=1` reduction, dominated derivative consequence, `rho`
scaling, and stability predicates.

Seven audited declarations depend only on `propext`, `Classical.choice`, and
`Quot.sound`. There is no `sorryAx` or project-specific axiom. Concrete
infinite-Gaussian tail, moment, and domination obligations are human-proved,
not claimed as Lean-checked.

## 4. Frozen Gaussian SR numerical correspondence — PASS

Independent raw-score and log-direct implementations passed all twelve
pre-registered cells:

| `m` | `GammaTilde_m^SR` | batch SE |
|---:|---:|---:|
| 1 | 17.453571 | 0.065881 |
| 2 | 14.500510 | 0.056725 |
| 3 | 12.972655 | 0.049011 |
| 5 | 11.048526 | 0.041047 |

All smallest-step, Richardson, convergence, fixed escalation, finiteness, and
tie gates passed for `rho=0.05,0.10,0.25`. Final short-cycle counts were
`0,0,1,37` for `m=1,2,3,5`. These results are empirical only.

## 5. Rigorous finite-support interval certification — PASS

At 128-bit Arb precision, the exact `A=2` SR witness certifies stopping times
`1,1,6,6`, normalization, score `-T_tau`, the derivative identity, denominator
decomposition, nonnegative correction, finite-difference convergence, and
selected attraction/repulsion inequalities. Exact gains are `3`, `8/3`, and
`12/5` for `m=2,3,5`.

This certificate applies only to the finite-support SR-compatible witness. It
does not interval-certify frozen Gaussian SR values.

## 6. Cross-representation correspondence — PASS

The human theorem/proof, authoritative recurrence, two independent Python
routes, Lean spine, Arb witness, historical SR package, and generic Priority-1
architecture agree on initialization, likelihood sign, natural threshold,
inclusive post-update timing, stopping index, terminal inclusion, stopped sum,
window, denominator, reference-error sign, and `rho` scaling.

## 7. Frozen-history and inheritance integrity — PASS

Frozen new-input hashes, both historical per-path manifests, their tags and
Git trees, the protected working tree, historical SR 94/94, Priority 1 13/13,
and required clean downstream regressions all pass. Full Level 1–3 verification
passed with zero skips, including direct Lean elaboration and full Arb replay.

## HISTORICAL_DIAGNOSTICS

- The aggregate Level-4 verifier passes the frozen stages through D4 phase-map
  and then rejects `92 != 52` in the old novelty protected-tree guard.
- External validation v2, final global re-audit, and terminal Level-4 suites
  reproduce the same protected-tree scope mismatch.
- The post-Level-4 archive verifier separately rejects the repository-root
  `README.md` hash changed by later documentation commits.

Both conditions predate Priority 2. Snapshot reconstruction proves their
provenance, and Priority 2 did not mutate the responsible history. They are
reported, not counted as Priority-2 passes, and not treated as Priority-2
failures.

## Verification summary

- Priority-2 focused tests: 18/18 PASS before final one-command replay.
- Level 1–3 verifier: PASS, zero skips; numerical sub-suite 90/90.
- Historical SR: 94/94 PASS.
- Priority 1: 13/13 PASS.
- External validation v3: 75/75 PASS.
- L4R-06 policy: 28/28 PASS.
- L4R-12 operational crossing: 26/26 PASS.
- Historical mismatch suites: v2 43 pass/2 expected failures; final global 33
  pass/3 expected failures; terminal closure 32 pass/4 expected failures.

The mechanical decision in `results/closure_decision.json` marks all seven
Priority-2 categories true while explicitly setting frozen Gaussian SR
`m>1` interval certification to false.

## Future strengthening

Full multidimensional infinite-horizon Arb certification of the frozen
Gaussian SR values remains optional future work. It is not a Priority-2 gate.
