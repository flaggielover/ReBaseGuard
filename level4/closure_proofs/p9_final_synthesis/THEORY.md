# P9 theory — what a synthesis priority can honestly prove

P9 owns two statements. Neither is a new claim about the monitoring model's
unexplored behaviour; both are statements assembled from claims that already
existed at the anchor commit. That is deliberate: `P9_DEFINITION_AUDIT.md` §7.1
declared before any analysis that P9 would **not** invent a model theorem, and
§2 records why — P9 has no frozen mandate, so its only defensible output is one
a reader can check against existing artifacts.

| # | statement | status |
|---|---|---|
| `P9-T1` | claim-class propagation / no-inflation bound on the evidence graph | **PROPOSITION** (elementary; the content is in the definitions) |
| `P9-T2` | operational degradation is present strictly inside the local stability region | **EXACT THEOREM** for the frozen model |

---

## 1. `P9-T1` — the no-inflation bound

### 1.1 Honest framing first

The mathematics here is elementary — a minimum over a DAG. **P9 does not
present it as a deep theorem.** Its value is entirely in two places: the
`verifies`/`premise` edge distinction (§1.4), which is a real and violable
invariant of this repository; and the audit it licenses (§1.5), which found
actual wording to fix. A reader who wants the mathematical content of P9 should
read `P9-T2` instead.

### 1.2 Setup

Let `G = (V, E)` be the claim graph of `CLAIM_LEDGER.json`: `V` the claims,
each with a status `s(v)` in the vocabulary of `CLAIM_LEDGER.md`, and a rank
`r(s) in {0,...,6}` given by that file's table. Edges are typed
`premise`, `verifies`, `diagnoses`. Write `Pa(v)` for the **premise** parents
of `v`.

Define the **licensed strength**

```text
    rho(v) = min( r(s(v)),  min_{p in Pa(v)} rho(p) )
```

with `rho(v) = r(s(v))` when `Pa(v)` is empty.

### 1.3 Proposition

> **P9-T1.** On the acyclic premise sub-graph:
> (a) `rho` is well defined;
> (b) `rho(v) <= r(s(v))` for every `v`;
> (c) for every directed premise path `v_0 -> v_1 -> ... -> v_k`,
>     `rho(v_k) <= min_i r(s(v_i))`.

*Proof.* (a) The premise sub-graph is a DAG (verified: 0 cycles over all 66
edges), so the recursion terminates. (b) is immediate from the outer `min`.
(c) By induction on `k`: `rho(v_0) <= r(s(v_0))` by (b); and
`rho(v_{i+1}) <= rho(v_i)` because `v_i in Pa(v_{i+1})`, so `rho` is
non-increasing along premise edges. Combining with (b) at each node gives the
bound. ∎

**Soundness reading** — the part that is not arithmetic. `rho(v)` is claimed to
bound what a synthesis sentence about `v` may assert. The justification is
class-by-class and definitional, not formal: a consequence of a
`CONDITIONAL_THEOREM` is at best conditional on the same assumptions; a
consequence of a finite-grid measurement is at best a finite-grid measurement;
a consequence of a claim in a `PARTIAL` priority inherits that priority's
status. P9 asserts this as a *policy* with a rationale (see
`CLAIM_LANGUAGE_POLICY.md`), not as a proved metatheorem.

### 1.4 Why `verifies` is not a premise edge — the substantive part

The `verifies` edge type was **not** designed in advance. It was forced by the
validator: the first run of `experiments/build_ledger.py` reported

```text
INFLATION P4-L1 (FORMALLY_VERIFIED, rank 6) exceeds weakest parent rank 5
INFLATION P4-R1 (EMPIRICAL_REPRODUCED, rank 3) exceeds weakest parent rank 1
```

Both were real modelling errors in the graph, and both point the same way.

`P4-L1` is a Lean kernel check of 19 declarations. As a fact about an artifact
it is `FORMALLY_VERIFIED` — the kernel really did check them. But the theorem it
supports, `P4-T1`, is a `CONDITIONAL_THEOREM`, and Lean "does not construct the
stopped probability model or discharge L1–L5". So the formal layer is neither
*bounded by* the science (the kernel check is not made less true by the
theorem's assumptions) nor *licensing* it (the check does not discharge those
assumptions). Modelling that edge as `premise` is wrong in **both** directions.

This is precisely the invariant the repository already states in prose:

> Lean does not certify either numerical interval; Arb does not prove
> differentiation under the expectation. The human theorem supplies the bridge.

So `verifies` edges are excluded from the `min` in `rho`, and a `verifies`
parent never licenses an upgrade of its child. `P1-L1`, `CORE-C1`, `CORE-C2`
and `P4-C1` were retyped for the same reason; `P1-L1` had escaped only because
`P1-T1` happens to be `EXACT_THEOREM`, which is luck, not correctness.

`P4-R1` was the second kind of error: it *diagnoses* the failed gate `P4-F1`
rather than deriving from it. A resolved anomaly is not a passed gate, and a
diagnosis is not a consequence. Hence `diagnoses`.

**Consequence for the graph as published:** a dependency graph of this project
drawn with untyped edges is unsound. `THEOREM_DEPENDENCY_GRAPH.md` therefore
renders the three types distinguishably (solid / dotted / dashed).

### 1.5 What the bound catches

With typed edges the ledger validates at **0 inflation violations**. The bound
is nevertheless not vacuous — it is what forces these, each of which is a live
temptation in this project:

* `P4-T2` may not be written as an *iff* characterisation (its parent `P4-T1`
  is conditional, and the converse was explicitly narrowed).
* `P7-B/C/D` may not be written as unconditional stationary results, even though
  `P5-T7` later supplied the missing existence proof for the *fixed-policy*
  chain — because the chain P6 uses is a different kernel (`X-07`).
* No P6 claim may be written at `CLOSED` strength (`P6-F1`, `PARTIAL`).
* No P8 claim may be a premise for anything (rank 0; separately test-enforced).
* `P5-N1`…`P5-N4` may not be written as theorems about `m` or about attraction.

---

## 2. `P9-T2` — local stability does not imply operational safety

This is the sharp form of the project's central operational lesson. P7
established it as a **negative empirical result** under a frozen criterion
(`P7-R1`: `RHO_C_STATUS = LOCAL_MATHEMATICAL_BOUNDARY_ONLY`). P9 observes that
for the frozen model it can be strengthened to an **exact** statement, using
only claims already at `EXACT_THEOREM`.

### 2.1 Statement

> **Theorem P9-T2 (separation).** Fix a frozen detector `D` in {two-sided CUSUM
> `k=1/2, h=5`; symmetric two-chart SR `A = 520.886133602749`} and a window
> `m >= 1`. Let `A(e)` be the expected cycle length from a reset detector with
> entering reference error `e`. Then at `rho = 0`:
>
> 1. the invariant law of the reference-error chain is exactly `N(0, 1/m)`;
> 2. the stationary in-control ARL equals `E_{e ~ N(0,1/m)}[A(e)]`;
> 3. **`E_{e ~ N(0,1/m)}[A(e)] < A(0)` strictly.**
>
> Consequently the monitoring scheme is *already* operationally degraded at
> `rho = 0`, which lies strictly below `rho_c` for every supported `(D, m)`
> — indeed at the value of `rho` at which the local map is *maximally* stable
> (multiplier `0`). Therefore **no threshold in `rho` is an operational safety
> boundary**, and in particular `rho < rho_c` is not a safety rule.

### 2.2 Proof

**(1)** `P5-T1` gives `e_{j+1} = rho * U_x + (1-rho) * F` with `F ~ N(0,1/m)`
independent. At `rho = 0` the kernel is the state-independent law `N(0,1/m)`,
so that law is invariant, and it is the unique invariant law (`P5-T7`, or
directly: the kernel ignores its argument).

**(2)** `P7-A` is the exact structural decomposition `ARL_0 = E_pi[A(e)]` for
*any* entering-error law `pi`. Apply it with `pi = N(0,1/m)` from (1).

**(3)** `P7-A` also gives that `A` is even and non-increasing in `|e|`, so
`A(e) <= A(0)` pointwise and `E[A(e)] <= A(0)`. For **strictness** it suffices
that `A(e) < A(0)` on a set of positive `N(0,1/m)`-measure. Both frozen
detectors satisfy this:

* `A(0) > 1`, since at `e = 0` an alarm at `t = 1` requires `|Z_1| >= h + k = 5.5`
  (CUSUM) or `|Z_1| >= log A + 1/2` (SR), each of probability `< 1`; hence
  `A(0) >= 1 + P(tau > 1) > 1`.
* `A(e) -> 1` as `e -> infinity`. For CUSUM, `C^-_1 = max(0, e - X_1 - k)`, so
  the event `{X_1 <= e - h - k}` forces an alarm at `t = 1` and has probability
  `Phi(e - 5.5) -> 1`. The SR argument is the same with `log A + 1/2`.

So `A` is non-constant; by monotonicity there is `e*` with `A(e) < A(0)` for all
`|e| >= e*`, a set of positive Gaussian measure. Hence `E[A(e)] < A(0)`. ∎

### 2.3 Status and dependencies

`EXACT_THEOREM` for the frozen model. Premises: `P5-T1` (`EXACT_THEOREM`),
`P5-T7` (`EXACT_THEOREM`), `P7-A` (`EXACT_THEOREM`), plus the frozen detector
definitions. Every premise is rank 6, so `rho(P9-T2) = 6` and the theorem does
not violate `P9-T1`. **It introduces no new premise.**

### 2.4 What it does and does not say

**Does:** it converts P7's frozen-criterion negative result into a statement
that holds by construction rather than by measurement, for these two detectors.
The degradation at `rho = 0` is not an artifact of P7's grid, its criterion, or
its Monte Carlo — it is forced by the fact that a reference *estimated* from `m`
observations is not the reference the threshold was calibrated for. This is
exactly `P7-D0`'s matched-information effect, proved.

**Does not:** it says nothing about the *size* of the degradation (that is
measured, `P7-E1`), nothing about `rho > 0`, nothing about other detectors or
non-Gaussian innovations (that is P8's territory and unadjudicated), and it does
**not** say `rho_c` is meaningless — `rho_c` remains an exact local boundary
(`P3-T1`) and a correct statement about the deterministic map. It says only that
being on the stable side of it is not sufficient for operational safety.

### 2.5 Independent numerical correspondence

`A(e)` was measured on an 81-point half-grid (even reflection, 2500 paths per
node) by an implementation that shares no code with P1–P8, and the mixture in
(2) formed by quadrature. Compared against the entirely separate recursive
`rho = 0` chain simulation:

| cell | `A(0)` | `A(1 sigma)` | `E[A(e)]` (quadrature) | `rho=0` ARL (recursive run) |
|---|---:|---:|---:|---:|
| CUSUM `m=1` | 468.0 | 10.35 | 83.72 | 82.08 ± 0.52 |
| CUSUM `m=5` | 469.7 | 48.51 | 162.41 | 162.11 ± 0.71 |
| SR `m=1` | 480.7 | 10.49 | 79.93 | 78.84 ± 0.51 |
| SR `m=5` | 471.2 | 42.12 | 154.88 | 155.67 ± 0.70 |

Two independent estimators of the same quantity agree to `0.3–1.6` (the
quadrature carries its own truncation and grid error, so this is agreement, not
an identity check). The `A(1 sigma)` column is the mechanism in one number: at
one standard deviation of the *fresh* reference error, CUSUM `m=1` ARL has
already fallen from `468` to `10.35`.

The same grid tests `P7-A`'s structural premise directly: across all four cells
and 320 adjacent-node comparisons there are **0 violations of monotonicity in
`|e|` at 3 standard errors**. P9 therefore reports `P7-A`'s evenness/monotonicity
premise as independently corroborated, not merely assumed.

---

## 3. Theorem targets P9 considered and declined

Prompt §12 lists candidate shapes. Recording the declines matters as much as
the adoptions:

| candidate | decision |
|---|---|
| exact chain from local stopped-selection gain to local recursive instability | **already exists** — that is `P1-T1`/`P2-T1` + `P3-T1`. Restating it as a P9 theorem would be concatenation. |
| separation theorem, `rho_c` local but not operational | **adopted** as `P9-T2` |
| conditional chain from reference-state distribution to exact finite-cycle P7 consequences | **declined** — `P7-A` already is this, exactly, and P9 cannot strengthen it without a new premise |
| theorem identifying which conclusions survive model-class generalization | **declined, blocked** — this is P8's question and P8 is unadjudicated. Attempting it now would be the exact partial-premise propagation P9 exists to prevent. |
