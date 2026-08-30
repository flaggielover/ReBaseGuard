# Level-4 Priority 1: General Stage-D `m > 1` Derivative Closure Design

**Date:** 2026-08-30

**Status:** Implemented; Priority-1 gates closed

**Scope:** Level-4 Priority 1 only

**Target namespace:** `level4/closure_proofs/m_gt_1_priority1/`

## 1. Objective and closure meaning

This campaign independently proves and certifies the general derivative theorem
for the exact Stage-D truncated reuse window. It creates a new, self-contained
evidence package under `level4/closure_proofs/m_gt_1_priority1/`. The sibling
namespace preserves the hash-protected historical partial campaign already
present at `level4/closure_proofs/m_gt_1/`, including its entire tree boundary.

The existing `level4/closure_proofs/m_gt_1_track1b/` package is immutable,
read-only prior evidence and a regression anchor. It is not a substitute for
any deliverable or gate in this campaign. Existing Stage A--F artifacts,
historical failures including D2.3 and Track 1A, and the closed Level 1--3 core
must remain unchanged.

If every gate passes, `CLOSED` means only:

> Level-4 Priority 1 -- the general Stage-D `m > 1` derivative theorem and its
> specified two-tier validation package are closed.

It does not mean that the frozen infinite-horizon Gaussian CUSUM values of
`GammaTilde_m` for `m > 1` have rigorous interval certificates.

## 2. Authoritative stochastic object

The campaign uses the ordinary Stage-D stopping process

```text
tau = inf {t >= 1 : an alarm is present after the update at time t},
w_m = min(m, tau),
A_m = (1 / w_m) sum_{r=0}^{w_m-1} Z_{tau-r},
T_tau = sum_{t=1}^{tau} Z_t.
```

The terminal alarm-causing increment is included in both `A_m` and `T_tau`.
The threshold comparison is inclusive and is performed after the detector
update.

Stage A instead uses the minimum-dwell stopping process

```text
tau_m = inf {t >= m : an alarm is present}.
```

For `m > 1`, `tau` and `tau_m` are distinct stopping times with different
laws, and they induce different maps. They must not be identified. At `m = 1`
the minimum-dwell restriction is vacuous, so the two definitions coincide;
this is a regression anchor, not evidence of equivalence for larger `m`.

## 3. Definition audit

`DEFINITION_AUDIT.md` will locate and cite every relevant mathematical and
implemented definition of:

- the stopping time and alarm timing;
- nominal reuse length `m` and realized length `w_m`;
- terminal increment and stopped sum;
- post-alarm reused statistic and reference update;
- the random denominator;
- Stage A's minimum-dwell map;
- Stage D's ordinary-stop truncated-window map.

For every entry, the audit will give its source file and symbol or section,
restate the mathematical object, compare code with mathematics, and record any
ambiguity. It will explicitly analyze `tau < m`, `tau = m`, and `tau > m`.

The audit will explain that `1 / w_m` is bounded by one because `tau >= 1` and
`m >= 1`. Thus the random denominator does not create a singularity. It does,
however, correlate with the stopped numerator, so it cannot be replaced by
`1 / m` before expectation. Measurability and domination are handled through
the stopped-window and stopped-moment assumptions stated in the theorem.

No inconsistency will be repaired in frozen history. Any inconsistency found
will be documented, and the new theorem will use the authoritative definitions
above.

## 4. Human theorem

`THEOREM.md` will state a general score-at-zero theorem and its frozen Gaussian
CUSUM specialization.

Let `P_e` be locally dominated by `P_0` on the stopped sigma-field, with
likelihood ratio `L_e`. Assume:

1. `tau` is positive and finite almost surely;
2. `A_m`, `T_tau`, and the required stopped objects are measurable;
3. `A_m` and `A_m T_tau` are integrable under `P_0`;
4. `L_0 = 1` and the derivative of `L_e` at zero is `-T_tau` almost surely;
5. the derivative integrand has an integrable uniform dominator on a
   neighborhood of zero;
6. the centered fresh-reference term has zero mean and does not contribute to
   the derivative.

Here `e = R - mu` is the reference error at the start of one monitoring cycle:
the active reference `R` minus the in-control process location `mu`. Under
`P_e`, the reference-centered Gaussian innovations have law `N(-e, 1)` and
drive the detector from its reset state until `tau`. Expectations `E_e` are
with respect to this stopped-path law. The likelihood ratio is defined on the
stopped sigma-field

```text
F_tau = {B : B intersect {tau <= t} belongs to F_t for every t >= 1},
```

where `F_t = sigma(Z_1, ..., Z_t)`. The map `F_{rho,m}` is the conditional
mean state-to-state map: given entering error `e`, form the alarm-cycle reuse
statistic `A_m`, combine it with the old reference using fraction `rho`, add
the centered fresh-reference component using fraction `1-rho`, and take the
mean next-cycle reference error.

Define

```text
F_{rho,m}(e) = rho (e + E_e[A_m]),
GammaTilde_m = E_0[A_m T_tau].
```

Then

```text
F'_{rho,m}(0) = rho (1 - GammaTilde_m).
```

For the frozen Gaussian location model, the stopped likelihood is

```text
L_e = exp(-e T_tau - e^2 tau / 2),
```

whose derivative at zero is `-T_tau`. The concrete CUSUM specialization will
state all stopping, measurability, moment, and domination assumptions rather
than hiding them in code.

The theorem will also state the local linearization consequence:

- attraction when `abs(rho (1 - GammaTilde_m)) < 1`;
- repulsion when `abs(rho (1 - GammaTilde_m)) > 1`;
- no conclusion from linearization alone at equality.

## 5. Human proof and random-denominator decomposition

`PROOF.md` will first prove the exact pathwise decomposition. Define

```text
B_m = (1/m) sum_{r=0}^{min(m,tau)-1} Z_{tau-r},
Q_m = 1{tau < m} (1/tau - 1/m) T_tau^2.
```

On `{tau >= m}`, `w_m = m`, so `A_m = B_m` and `Q_m = 0`. On
`{tau < m}`, the retained suffix is the whole stopped path, hence its sum is
`T_tau`, and

```text
(A_m - B_m) T_tau = (1/tau - 1/m) T_tau^2 = Q_m.
```

Therefore

```text
A_m T_tau = B_m T_tau + Q_m,
GammaTilde_m = E_0[B_m T_tau] + E_0[Q_m],
E_0[Q_m] >= 0.
```

The proof will then use the local likelihood derivative and its integrable
dominator to justify differentiation under the stopped expectation. Symmetry
at zero will justify the centered map and fresh-reference contribution where
used. Affinity gives exact scaling in `rho`. At `m = 1`, the short-cycle event
is empty and the theorem reduces to the previously closed terminal-observation
case.

## 6. Inheritance and immutability ledger

`INHERITANCE_LEDGER.md` and a machine-readable manifest will distinguish:

- frozen artifacts cited only as historical definitions or decisions;
- Track 1B results used only as prior evidence or regression anchors;
- generic Level 1--3 Lean infrastructure imported without modification;
- implementation primitives reused only where scientific independence is not
  compromised;
- definitions, proofs, computations, tests, and certificates newly produced
  by this campaign.

The ledger will record SHA-256 hashes for the immutable Track 1B tree and the
historical D2.3 decision inputs. The verifier will fail if those hashes change
during the campaign.

## 7. Two-tier validation architecture

### 7.1 Frozen Gaussian CUSUM numerical correspondence

A new numerical package will independently implement the two-sided CUSUM
recurrence, stopping logic, terminal inclusion, and truncated-window
accumulation. It will not call Stage D or Track 1B scientific evaluators.
Any reused constants or primitive semantics will be listed in the inheritance
ledger and checked by focused regression tests.

The numerical study will cover `m = 1, 2, 3, 5` and several `rho` values. It
will compare:

- direct finite differences of the induced map near zero;
- the independent score prediction `rho (1 - GammaTilde_m)`;
- multiple finite-difference step sizes;
- increasing sample sizes or batch precision;
- raw and Richardson-extrapolated convergence diagnostics where justified.

Independent seed families will separate the direct-map and score routes.
Machine-readable results will contain estimates, standard errors, tolerances,
seed provenance, sample sizes, and pass/fail gates.

Before final estimates are observed, the numerical protocol will freeze:

- `m = {1, 2, 3, 5}` and `rho = {1/20, 1/10, 1/4}`;
- central-difference steps `h = {1/10, 1/20, 1/40}`;
- a pilot escalation level of 8 batches of 2,500 paths per evaluation and a
  final level of 48 batches of 10,000 paths per evaluation;
- disjoint seed families for score, pilot finite-difference, and final
  finite-difference routes;
- exact structural tolerances of `1e-12` for deterministic fixtures;
- agreement at the smallest step within `max(0.20, 4 combined batch SE)` after
  `rho` scaling;
- Richardson agreement within `max(0.12, 4 combined batch SE)` after `rho`
  scaling;
- a convergence gate requiring the Richardson discrepancy not to exceed the
  `h=1/10` discrepancy by more than two combined standard errors; and
- a precision gate requiring the final batch SE not to exceed the pilot batch
  SE after like-for-like `rho` scaling.

These rules, along with maximum-step and finite-value guards, will be stored in
a hash-pinned protocol file before the final experiment is run. A failed gate
will remain failed; tolerances and sample sizes will not be retuned after
seeing final estimates.

Because very short frozen-CUSUM cycles can be rare, deterministic stopped-path
fixtures will separately exercise `tau < m`, `tau = m`, and `tau > m`, while
the stochastic output will report the observed short-cycle counts honestly.
This tier is empirical numerical correspondence only.

### 7.2 Exact finite-support stopped-process Arb witness

The rigorous witness will use a finite sample space of symmetric stopped paths
that contains both a short branch (`tau = 1`) and a full-window branch
(`tau = 6`). It therefore exercises both `{tau < m}` and `{tau >= m}` for
`m = 2, 3, 5` and has a nonzero short-cycle correction.

Let the baseline probabilities be positive rationals `p(omega)` summing to
one, choose a symmetric stopped sum `T_tau` with `E_0[T_tau] = 0`, and define

```text
M(e) = sum_omega p(omega) exp(-e T_tau(omega)),
P_e(omega) = p(omega) exp(-e T_tau(omega)) / M(e).
```

This is analytically a valid probability family on every real neighborhood of
zero: each weight is positive, the finite sum `M(e)` is finite and strictly
positive, and normalized weights sum exactly to one. Differentiating the
finite sum gives

```text
d/de log P_e(omega) at e=0
  = -T_tau(omega) - M'(0)/M(0)
  = -T_tau(omega) + E_0[T_tau]
  = -T_tau(omega).
```

This proof will appear in both the theorem package and certificate report; it
will not rely on numerical normalization.

Before certificate evaluation, a manifest will freeze the complete witness:
path labels, every stopped increment, stopping times, baseline rational
probabilities, the `m` grid, dyadic finite-difference steps, Arb precision, and
the selected `rho` values. The construction principle is fixed in advance:
use sign-symmetric short and long path pairs so `E_0[T_tau] = 0`, make the
short-cycle correction nonzero for every target `m`, and select one rational
`rho` on each side of the analytically computed unit-multiplier boundary.
Those attraction and repulsion witnesses are design consequences, not
parameters selected after interval output is inspected.

Arb via `python-flint` will evaluate the exact rational inputs and rigorous
transcendental enclosures. The certificate will establish:

- normalization enclosures and positivity of `M(e)`;
- the exact score-at-zero identity;
- the random-denominator decomposition and nonnegative correction;
- agreement between the analytic derivative and interval finite differences;
- convergence as the dyadic step size shrinks;
- at least one certified attraction inequality and one certified repulsion
  inequality for selected `rho` values.

The certificate output will be machine-readable and independently audited.
It rigorously validates this finite-support theorem instantiation only. It is
not an interval evaluation of the frozen Gaussian CUSUM's `GammaTilde_m`.

## 8. Lean proof spine

New Lean source in `level4/closure_proofs/m_gt_1_priority1/lean/` will independently
formalize:

1. `windowLength m tau = min m tau`;
2. the short/long partition;
3. whole-path suffix behavior on `tau < m`;
4. pointwise and expectation-level denominator decomposition;
5. correction nonnegativity;
6. the `m = 1` reduction;
7. dominated differentiation of the stopped expectation through the existing
   generic Level 1--3 integral bridge;
8. affine scaling in `rho`;
9. the algebraic attraction and repulsion criteria.

The new file may import generic `RebaseguardLean` infrastructure but will not
import the Track 1B theorem source. `LEAN_CORRESPONDENCE.md` will list theorem
names, assumptions, human-proof sections, and remaining concrete-CUSUM
analytic obligations. It will separate (a) abstract measurability,
integrability, domination, and derivative assumptions explicitly consumed by
Lean from (b) concrete Gaussian-CUSUM stopped-moment, measurability, and local
domination obligations discharged only in the human analysis. It will not
describe those concrete obligations as machine-checked unless the
formalization actually proves them. An axiom audit will be recorded.
Compilation must use the repository's pinned Lean toolchain.

## 9. Correspondence and evidence boundaries

`CORRESPONDENCE_TABLE.md` will compare mathematical prose, the independent
Python implementation, Lean, Arb, frozen Stage D, frozen Stage A, and immutable
Track 1B for:

- indexing and start time;
- stopping and inclusive threshold conventions;
- terminal increment inclusion;
- reuse window and denominator;
- `tau < m`, `tau = m`, and `tau > m` behavior;
- parameter notation;
- reference-error and derivative sign conventions;
- the role of `rho`.

Every report and README will repeat the evidence boundary: frozen Gaussian
CUSUM results are empirical, whereas rigorous interval certification applies
only to the exact finite-support witness.

## 10. Tests and verification

Focused tests will cover:

- `m = 1` reduction and Stage A/Stage D coincidence there;
- `m = 2` and `m = 3` required cases, plus `m = 5` numerics;
- forced `tau < m`, `tau = m`, and `tau > m` paths;
- random-denominator correctness;
- direct versus decomposed statistics;
- independence of numerical implementations and seed families;
- finite-difference convergence and theorem agreement;
- Arb output parsing and all certified inequalities;
- Lean compilation and axiom-audit expectations;
- Track 1B and historical D2.3 immutability;
- presence and consistency of every required report.

A one-command campaign verifier will run the focused Python tests, regenerate
or audit numerical and certificate outputs, compile Lean, verify immutable
hashes, and derive the closure decision. The existing Level 1--3 verifier and
all feasible relevant repository suites will also run before closure.

## 11. Required artifacts

The campaign will create at least:

```text
level4/closure_proofs/m_gt_1_priority1/
  README.md
  DEFINITION_AUDIT.md
  INHERITANCE_LEDGER.md
  THEOREM.md
  PROOF.md
  NUMERICAL_CORRESPONDENCE.md
  LEAN_CORRESPONDENCE.md
  CORRESPONDENCE_TABLE.md
  CLOSURE_REPORT.md
  reproduce.sh
  manifest.json
  numerics/
  certificates/
  lean/
  src/
  tests/
  results/
```

Machine-readable results and certificates will contain configuration,
provenance, precision, backend, pass/fail fields, and evidence classification.

## 12. Closure decision

`CLOSURE_REPORT.md` will report these categories separately:

1. analytical theorem closure;
2. Lean proof-spine closure;
3. frozen Gaussian CUSUM numerical correspondence;
4. finite-support Arb certification;
5. frozen-history and inheritance integrity.

The overall verdict is exactly one of `CLOSED`, `PARTIALLY_CLOSED`, or
`NOT_CLOSED`. It may be `CLOSED` only when every Priority-1 requirement and all
five categories pass. A failure in any category remains visible even if other
categories pass. The report must not allow overall closure to be read as an
interval certificate for frozen Gaussian `m > 1` values.

## 13. Scope exclusions and future strengthening

This campaign will not:

- start the SR theorem;
- reopen the global `(m, rho)` stability map;
- attempt a general location-family theorem;
- modify licensing;
- rewrite frozen history or old closure decisions;
- build the multidimensional infinite-horizon Arb certificate for frozen
  Gaussian CUSUM at `m > 1`.

The last item may be recorded as future strengthening, but it is not a gate for
this Priority-1 campaign and must not expand the current implementation scope.

## 14. Git checkpoint

After implementation, all gates will be run, the complete diff will be
reviewed, and the campaign will be committed as one coherent Level-4 Priority
1 checkpoint. A push will be attempted only after the local commit and only if
the configured remote accepts existing authenticated access. The final report
will record the commit hash and exact push status.
