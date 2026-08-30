# Level-4 Priority 2: Shiryaev--Roberts Derivative Closure Design

**Date:** 2026-08-30

**Status:** Approved binding design; implementation pending

**Approach:** Layered independent instantiation

**Scope:** Level-4 Priority 2 only

**Target namespace:** `level4/closure_proofs/sr_derivative_priority2/`

## 1. Objective and closure meaning

This campaign independently closes the derivative theorem for the authoritative
reset, symmetric two-chart Shiryaev--Roberts detector and the ordinary Stage-D
truncated reuse window. It combines newly discharged SR-specific analytic
obligations with detector-independent stopped-score and window infrastructure.

Existing SR, Priority-1, Stage A--F, D2.3, Track 1A/1B, and Level 1--3 artifacts
remain immutable. They are prior evidence or generic infrastructure, not
substitutes for Priority-2 deliverables.

If every Priority-2 gate passes, `CLOSED` means exactly:

> Level-4 Priority 2 -- the Shiryaev--Roberts derivative theorem and its
> declared validation package are closed.

It does not close all SR theory, the global stability map, Priority 3, or Level
4 as a whole. It does not interval-certify frozen infinite-horizon Gaussian SR
values for `m>1`.

## 2. Immutable SR history and two-snapshot policy

`SR_HISTORY_AUDIT.md` and machine-readable manifests will preserve two distinct
historical boundaries rather than collapsing them into one canonical tree.
For each snapshot, paths are sorted bytewise; each manifest line is
`<content-SHA-256><two spaces><path>\n`; the aggregate is the SHA-256 of the
UTF-8 concatenation of those lines. Git tree IDs are recorded separately and
are not mislabeled as SHA-256 values.

### 2.1 Terminal-Level-4 snapshot

- Tag: `rebaseguard-level4-closed`
- Commit: `5e43336264f257c7224b622f8063eb10aad481d6`
- Commit date: `2026-08-26T13:14:50+09:00`
- Scope: 52 tracked files below `level4/closure_proofs/sr_derivative/`
- Git tree: `abd869b91fe8ba3e69af9db0e7356a73c36c724f`
- Per-file SHA-256 manifest aggregate under the campaign's declared rule:
  `4d084982669c128967720d38a21d882fd92e3249835162e02ba452ad607594aa`

### 2.2 Additive post-Level-4 snapshot

- Tag: `rebaseguard-sr-gamma-certified`
- Commit: `b04578810126d3fbc4d938a721481b1e6186b8ce`
- Commit date: `2026-08-27T22:12:01+08:00`
- Scope: the original 52 files plus 40 additive files, for 92 tracked files
  below `level4/closure_proofs/sr_derivative/`
- Git tree: `a4fbe9890b0ba59d588766dccfa17e9ef9d45f1b`
- Per-file SHA-256 manifest aggregate under the campaign's declared rule:
  `3212a35f6f7ebc5d2e05bb791f0a099673f5d60d930ebede96d90fa8ea66a063`
- The 92-file tree at design time is identical to the tagged tree.

The campaign will store complete per-path SHA-256 manifests for both snapshots,
their Git identities, counts, scope, and hash rule. It will verify that every
original 52-file blob remains identical and that the additive snapshot remains
identifiable and unchanged. Priority 2 must not modify either tree.

### 2.3 Historical diagnostics

The audit will report, separately from Priority-2 gates:

1. the terminal verifier's expected rejection when its frozen 52-file rule is
   applied to the later 92-file additive tree; and
2. `scripts/verify_post_level4_archive.py` currently rejecting a later
   `README.md` hash after commits `acf8e16`, `e1f87d6`, and `e3dee7c` changed
   repository documentation following the SR archive tag.

These are `HISTORICAL_DIAGNOSTICS`, not Priority-2 failures, only if the audit
reproduces their pre-campaign provenance, both snapshots remain reproducibly
identifiable, Priority 2 changes none of the responsible protected paths, and
the new campaign has a clean independent integrity boundary. Otherwise the
affected condition becomes a Priority-2 integrity failure.

## 3. Authoritative SR stochastic object

Fix an admissible natural-unit threshold `A>1`. Under `Q_e`, the canonical
residual coordinates are iid

```text
Z_t ~ N(-e,1),                 e = current reference - true mean.
```

Starting from a reset state,

```text
R_0^+ = R_0^- = 0,
R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2),
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2),
tau = inf {t>=1 : max(R_t^+,R_t^-) >= A}.
```

Both charts update before the inclusive alarm comparison. The terminal
alarm-causing increment is included. The authoritative Gaussian correspondence
uses the exact decimal label

```text
A = 520.886133602749
```

and the implementation's nearest binary64 value. A cycle uses no head-start.
The stable log implementation stores `Y=log(1+R)` but compares the raw-state
logarithms to `log(A)`; it is algebraically equivalent to the recurrence above.

For positive integer `m`, define the ordinary Stage-D truncated window

```text
w_m = min(m,tau),
A_m = (1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r},
T_tau = sum_{t=1}^tau Z_t.
```

This is not Stage A's minimum-dwell stopping time. Priority 2 will audit any SR
appearance in Stage A separately and will not identify the two objects for
`m>1`.

## 4. Likelihood convention and sign audit

The parameter `e` changes the residual law while the SR path functional is
fixed. For a prefix `z_1,...,z_n`,

```text
dQ_e/dQ_0
  = product_t phi(z_t+e)/phi(z_t)
  = exp(-e sum_t z_t - n e^2/2).
```

On the stopped sigma-field

```text
F_tau = {B : B intersect {tau<=n} belongs to F_n for every n},
```

the stopped likelihood is

```text
L_e = exp(-e T_tau-e^2 tau/2),
dL_e/de at e=0 = -T_tau.
```

The sign follows from `Z_t=epsilon_t-e`; it is not inherited by analogy from
CUSUM or Priority 1. A focused regression test will compare the symbolic
one-step normal density derivative, an independently evaluated numerical
density-ratio derivative, and the stopped score. Reversing any of the `e`,
`Z_t`, `T_tau`, or map-derivative conventions must make that test fail.

## 5. Pre-registered concrete Gaussian assumption discharge

Before final numerical experiments, the campaign will freeze an assumption
ledger with exactly these rows and permitted terminal statuses:

| Obligation | Required discharge | Permitted status |
|---|---|---|
| Almost-sure finiteness and geometric tail | Derive an SR-specific uniform forcing probability near zero | `PROVED` or `FAILED/OPEN` |
| Stopped measurability | Construct finite-prefix states, alarm events, `tau`, suffix statistic, and stopped sum measurably | `PROVED` or `INHERITED_GENERIC` with explicit instantiation |
| `A_m` integrability | Bound the random-denominator suffix statistic by stopped absolute sums | `PROVED` or `FAILED/OPEN` |
| `A_m T_tau` integrability | Combine stopped-sum bounds and stopped exponential moments | `PROVED` or `FAILED/OPEN` |
| Required exponential stopped moments | Prove a sufficiently small exponential moment using the SR forcing bound and Gaussian moments | `PROVED` or `FAILED/OPEN` |
| Stopped likelihood identity | Derive the `Q_e/Q_0` Radon--Nikodym derivative on `F_tau` | `PROVED` or `FAILED/OPEN` |
| Local derivative domination | Exhibit an integrable uniform dominator for the differentiated stopped integrand | `PROVED` or `FAILED/OPEN` |
| Reflection symmetry and centering | Prove chart exchange, stopping invariance, sign reversal, and `E_0[A_m]=0` | `PROVED` or `FAILED/OPEN` |

Every row will cite its human-proof section, any generic lemma consumed, Lean
correspondence where applicable, and the immutable source definition. Numerical
evidence cannot discharge an analytical obligation. Any `FAILED/OPEN` row
blocks analytical closure and overall `CLOSED`.

The SR-specific forcing constant is

```text
b_A = log(A)+1/2.
```

From every live state, `|Z_t|>=b_A` forces a chart to cross. A uniform positive
probability of this event for `e` in a bounded neighborhood of zero gives a
geometric tail. On nonterminal steps, `|Z_t|<b_A`; hence stopped absolute sums
are bounded by `b_A(tau-1)+|Z_tau|`. The proof will turn these facts into the
required stopped exponential moments and domination rather than assuming them.

## 6. Human theorem and proof

`THEOREM.md` will define the probability space, `e`, `Q_e`, `F_tau`, SR
recurrence, stopping convention, stopped variables, reuse map, and all analytic
assumptions. Define

```text
F_{rho,m}(e) = rho(e + E_e[A_m]),
GammaTilde_m^SR = E_0[A_m T_tau].
```

The state-to-state interpretation is the conditional mean of the next
reference error after mixing a fraction `rho` of the reused post-alarm estimate
with an independent centered fresh-reference contribution. The theorem is

```text
F'_{rho,m}(0) = rho(1-GammaTilde_m^SR).
```

It states attraction when the multiplier magnitude is below one, repulsion
when it is above one, and no conclusion from first-order linearization at
equality.

`PROOF.md` will be standalone. It will:

1. establish the concrete SR tail, measurability, moment, likelihood, and
   domination results;
2. differentiate the stopped expectation using the score `-T_tau`;
3. retain `w_m` and partition `tau<m`, `tau=m`, and `tau>m`;
4. prove the detector-independent pathwise decomposition

   ```text
   B_m = (1/m) sum_{r=0}^{min(m,tau)-1} Z_{tau-r},
   Q_m = 1{tau<m}(1/tau-1/m)T_tau^2,
   A_m T_tau = B_m T_tau + Q_m,
   Q_m >= 0;
   ```

5. prove that residual reflection exchanges charts, preserves `tau`, negates
   `A_m` and `T_tau`, and centers the map at zero; and
6. derive exact `rho` scaling and the stability consequences.

At `m=1`, the result reduces to the immutable historical SR theorem, but that
coincidence is a regression anchor rather than a replacement proof.

## 7. Finite-support SR-compatible witness

The witness uses `A=2`, baseline probabilities `1/4`, and four symmetric paths:

```text
short_plus  = [2],                 tau=1
short_minus = [-2],                tau=1
long_plus   = [0,0,0,0,0,2],      tau=6
long_minus  = [0,0,0,0,0,-2],     tau=6.
```

### 7.1 Analytic stopping verification before freeze

Put `q=exp(-1/2)`. Along a zero prefix the two charts agree and

```text
R_n = q(1+R_{n-1}) = sum_{k=1}^n q^k.
```

The elementary bound `exp(1/2)>1+1/2=3/2` gives `q<2/3`. Therefore for every
`n<=5`,

```text
R_n < q/(1-q) < 2,
```

so neither chart crosses the inclusive boundary during the first five long
steps. At the sixth step of `long_plus`,

```text
R_6^+ = (1+R_5)exp(3/2) > exp(3/2) > 1+3/2 = 5/2 > 2.
```

Thus it first crosses at `t=6`. For `short_plus`,

```text
R_1^+ = exp(3/2)>2,
```

so it stops at `t=1`. Sign reflection exchanges the plus and minus charts
stepwise, proving the identical claims for both reflected paths.

These strict analytic inequalities validate the proposed path/threshold pair.
The manifest may therefore freeze the witness without changing the
authoritative SR convention. Arb will independently enclose the same states
and inequalities as a certificate regression.

### 7.2 Exact gain and preselected stability points

Both short paths have `A_m T_tau=4`. Each long path has
`A_m T_tau=4/m` for `m in {2,3,5}`. Equal weighting gives

```text
GammaTilde_m^SR = 2+2/m.
```

The preselected values are `rho=1/4` for attraction and `rho=1` for repulsion.
For every certified `m`, the corresponding multiplier magnitudes are strictly
below and above one, respectively. These values and the construction principle
will be frozen before certificate execution.

Define the finite probability family

```text
M(e) = sum_omega p(omega) exp(-e T_tau(omega)),
P_e(omega) = p(omega) exp(-e T_tau(omega))/M(e).
```

Positivity and finite support make `M(e)` finite and strictly positive for
every real `e`; the normalized weights therefore form a probability family.
Symmetry gives `E_0[T_tau]=0`, so

```text
d/de log P_e(omega) at zero = -T_tau(omega).
```

The certificate will rigorously validate normalization, score, SR stopping,
the derivative identity, denominator decomposition, correction
nonnegativity, dyadic finite-difference convergence, and the selected stability
inequalities. Its evidence boundary is this exact finite witness only.

## 8. Pre-registered Gaussian numerical correspondence

Priority 2 will create fresh, source-separated implementations:

- a raw-state baseline score route for `GammaTilde_m^SR`; and
- a log-state perturbed-law direct-map route using paired common random numbers
  within each `+h/-h` comparison.

Neither route will import Stage D or historical SR scientific evaluators. They
will use disjoint seed families and share only frozen scalar configuration and
result schemas. Deterministic fixtures will exercise recurrence, threshold
timing, terminal inclusion, and every window branch.

The numerical protocol will be written and hashed before pilot or final output:

```text
m grid:                 [1,2,3,5]
rho grid:               [0.05,0.10,0.25]
central-difference h:   [0.05,0.025,0.0125]
pilot:                  8 batches x 2,000 paths per condition
final:                  48 batches x 5,000 paths per condition
score seed family:      2026083021
pilot direct family:    2026083022
final direct family:    2026083023
structural fixtures:    2026083024
maximum path length:    4,000,000
```

The fixed two-stage schedule is the sample-size escalation rule. Pilot results
cannot alter the final schedule, thresholds, steps, or tolerances. There is no
post-failure rescue run.

For every `(m,rho)` cell, the smallest-step direct derivative must agree with
the independent score prediction within the maximum of `0.12` absolute units
after `rho` scaling and four combined batch standard errors. A secondary
Richardson diagnostic must agree within the maximum of `0.08` and four combined
standard errors. The step ladder must not exhibit a statistically significant
increase in absolute discrepancy beyond two combined standard errors. Final
batch SE must not exceed the corresponding pilot batch SE after scaling. All
cells, finiteness checks, source-separation checks, and seed-disjointness checks
must pass. Exact ties are reported and any nonzero count blocks the numerical
gate for diagnosis. Short-cycle counts are reported honestly; zero stochastic
short cycles do not fail the gate because deterministic fixtures independently
cover `tau<m`, `tau=m`, and `tau>m`.

Machine-readable results will record estimates, batch SEs, counts, seeds,
toolchain, source hashes, gate margins, and evidence classification. Frozen
Gaussian SR output is empirical correspondence only.

## 9. Lean proof spine

New Lean files under the Priority-2 namespace will not import the historical
protected SR theorem. They may import generic `RebaseguardLean` integral
infrastructure. They will independently formalize:

1. reset two-chart SR state and recurrence;
2. post-update inclusive alarm and reflection;
3. finite stopped-record reflection and stopping-time preservation;
4. stopped-window length and short/full partition;
5. whole-path suffix behavior on short cycles;
6. pointwise and expectation denominator decomposition;
7. correction nonnegativity and `m=1` reduction;
8. the abstract dominated derivative bridge and score substitution;
9. exact `rho` scaling and attraction/repulsion algebra.

`LEAN_CORRESPONDENCE.md` will separate abstract assumptions formalized and
consumed by Lean from concrete Gaussian SR obligations proved outside Lean.
Lean will not be described as proving the concrete infinite-process tail,
moment, or domination results unless it actually does. The axiom audit may
contain only standard Mathlib axioms and no `sorryAx` or project-specific
scientific axiom.

## 10. Audits, correspondence, and inheritance

The campaign will create:

- `SR_HISTORY_AUDIT.md` for the two snapshots and historical diagnostics;
- `DEFINITION_AUDIT.md` classifying authoritative, historical, obsolete,
  exploratory, and new SR objects;
- `ASSUMPTION_DISCHARGE.md` and a machine-readable status table;
- `INHERITANCE_LEDGER.md` and separate immutable manifests;
- `CORRESPONDENCE_TABLE.md` across prose, authoritative recurrence, independent
  Python routes, Lean, Arb, historical SR, and Priority 1; and
- focused reports for the theorem, proof, numerics, certificate, Lean, and
  closure decision.

All reuse will state whether it is immutable prior evidence, generic
infrastructure, a regression anchor, or a newly discharged Priority-2 fact.
Old exploratory SR artifacts cannot silently become authoritative.

## 11. Tests and verification

Focused tests will cover:

- raw and log recurrence against hand-computed paths;
- reset initialization and zero head-start;
- natural threshold units, inclusive comparison, and post-update timing;
- stopping index, chart reflection, terminal inclusion, and sign convention;
- the symbolic/numerical stopped-likelihood sign regression;
- `m=1,2,3,5` and `tau<m`, `tau=m`, `tau>m`;
- the random denominator and decomposed-statistic equality;
- direct versus score correspondence and disjoint seeds;
- exact witness stopping, normalization, Arb parsing, and all inequalities;
- Lean compilation, theorem correspondence, and axiom audit;
- complete preservation of both SR snapshots; and
- presence and consistency of every closure artifact.

The one-command `reproduce.sh` will regenerate or audit numerical and interval
outputs, run focused tests, compile Lean, audit axioms, verify correspondence,
run the Level 1--3 verifier, run feasible relevant Level-4 suites, capture both
historical diagnostics explicitly, and mechanically derive the Priority-2
verdict. Historical diagnostics will not be silently treated as passes, nor
will their expected pre-campaign state fail Priority 2 unless provenance or
immutability checks fail.

## 12. Closure categories

`CLOSURE_REPORT.md` will report separately:

1. SR definition and history audit;
2. analytical SR theorem closure;
3. Lean proof-spine closure;
4. frozen Gaussian SR numerical correspondence;
5. rigorous finite-support interval certification;
6. cross-representation correspondence;
7. frozen-history and inheritance integrity; and
8. `HISTORICAL_DIAGNOSTICS` for the old tree guard and README drift.

The overall verdict is exactly `CLOSED`, `PARTIALLY_CLOSED`, or `NOT_CLOSED`.
`CLOSED` requires every Priority-2 gate and all seven closure categories to
pass. Historical diagnostics remain visible but do not block when their
grandfathering conditions are proved.

## 13. Required artifacts

The campaign will create at least:

```text
level4/closure_proofs/sr_derivative_priority2/
  README.md
  SR_HISTORY_AUDIT.md
  DEFINITION_AUDIT.md
  ASSUMPTION_DISCHARGE.md
  INHERITANCE_LEDGER.md
  THEOREM.md
  PROOF.md
  NUMERICAL_CORRESPONDENCE.md
  CERTIFICATE_REPORT.md
  LEAN_CORRESPONDENCE.md
  CORRESPONDENCE_TABLE.md
  CLOSURE_REPORT.md
  reproduce.sh
  manifest.json
  history/
  numerics/
  certificates/
  lean/
  src/
  tests/
  results/
```

## 14. Failure and scope policy

If the recurrence conflicts with frozen evidence, the witness stopping claims
fail, a concrete analytic obligation remains open, numerics contradict the
theorem, the theorem appears false, or a protected artifact would require
modification, implementation stops and records the exact issue. Conventions or
gates will not be changed to manufacture closure.

The campaign will not start Priority 3, reopen the global `(m,rho)` stability
map, attempt a general location-family theorem, perform full frozen
infinite-horizon SR Arb certification, refactor unrelated code, change
licensing, or rewrite historical failed gates.

## 15. Git checkpoint

After implementation, all gates will run, the complete diff and protected
hashes will be reviewed, and one coherent Priority-2 checkpoint will be
committed. A push will be attempted only after the local commit and only using
existing authenticated remote access. History will not be rewritten and no
force-push will be used.
