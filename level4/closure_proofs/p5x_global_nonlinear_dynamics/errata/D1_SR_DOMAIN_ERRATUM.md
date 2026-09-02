# Erratum D1 — the frozen SR pre-alarm state square

```text
ERRATUM_ID        = D1
SUBJECT           = FROZEN_THEOREM.md section 2, the constant b_SR
FROZEN_VALUE      = b_SR = log A
TRUE_VALUE        = b_SR = log(1 + A)
CLASSIFICATION    = CERTIFIER_DOMAIN_ERRATUM
GOVERNANCE_ROUTE  = A (non-scientific erratum to a certified-domain declaration)
SUPERSEDES_FOR    = future SR certified work only
FROZEN_BYTES      = UNCHANGED (nothing in FROZEN_THEOREM.md is edited)
STATUS            = adjudicated here; SR certified work may resume under section 8
```

This erratum is **additive**. The defective sentence remains in
`FROZEN_THEOREM.md` and in the Checkpoint-A commit `db0781e`, and gate `G1`
still passes because no frozen byte moved. Nothing in this file changes a P5X
theorem statement, a P5 result, or any historical verdict.

---

## 1. The original frozen statement

`FROZEN_THEOREM.md` §2, `P5X-T1`, opening sentence:

> Let `x = (x^+, x^-)` denote the pre-alarm detector state, living in the
> compact square `E_D = [0, b_D)^2` with `b_CUSUM = h = 5`, `b_SR = log A` …

The CUSUM half of that sentence is correct. The SR half is false, and this
erratum states exactly why, from the recurrence rather than from the witness.

## 2. The exact frozen recurrence

`level4/closure_proofs/p7_statistical_consequences/src/rebaseguard_p7/detectors.py`,
restated verbatim from Stage D's `_sr_update`:

```python
def sr_update(yp, ym, z, log_thr):
    log_r_plus  = yp + z - 0.5
    log_r_minus = ym - z - 0.5
    return (np.logaddexp(0.0, log_r_plus), np.logaddexp(0.0, log_r_minus),
            log_r_plus >= log_thr, log_r_minus >= log_thr)
```

with `log_thr = log A`, `A = 520.886133602749`, symmetric two-chart, no head
start, `y^+_0 = y^-_0 = 0`.

## 3. The exact state update

Writing `v^{+}_t = y^+_{t-1} + z_t - 1/2` and `v^{-}_t = y^-_{t-1} - z_t - 1/2`
for the **pre-update log-likelihood-ratio statistics**, the *stored* state is

```text
y^{+}_t = log(1 + exp(v^{+}_t)) ,        y^{-}_t = log(1 + exp(v^{-}_t)) .
```

`softplus(v) = log(1 + e^v)` is strictly increasing, maps `R` onto `(0, ∞)`,
and satisfies `softplus(v) > 0` for every finite `v`.

## 4. The exact alarm condition

```text
alarm at step t   <=>   max(v^{+}_t, v^{-}_t) >= log A .
```

The test is on the **pre-update quantity `v`**, not on the stored state `y`.
This is the entire content of the defect: the threshold governs `v`, while the
domain declaration was written about `y`.

## 5. Derivation of the true reachable bound

**Upper bound.** Let `t >= 1` and suppose the path is alive at `t`, i.e. no
alarm occurred at steps `1..t`. Then in particular `v^{+}_t < log A`, and since
`softplus` is strictly increasing,

```text
y^{+}_t = softplus(v^{+}_t) < softplus(log A) = log(1 + A) .
```

The same holds for `y^{-}_t`, and `y^{+}_0 = y^{-}_0 = 0`. Hence every live
state satisfies `0 <= y^{±} < log(1 + A)`.

**The bound is attained in the limit, and is therefore tight.** Take `t = 1`
from the reset state `y^+_0 = 0`: then `v^{+}_1 = z_1 - 1/2`, so for any
`epsilon in (0, 1)` the innovation `z_1 = log A + 1/2 - epsilon` is alive
(`v^+_1 = log A - epsilon < log A`) and gives

```text
y^{+}_1 = log(1 + A e^{-epsilon})  -->  log(1 + A)   as epsilon -> 0+ .
```

Every such `z_1` has strictly positive Gaussian density, so this is a
positive-probability family, not a null set. Therefore

```text
sup { y : y is a live SR chart state } = log(1 + A) ,   not attained,
```

and the correct compact square is `E_SR = [0, log(1+A)]^2`, with the live states
in `[0, log(1+A))^2`.

**The region omitted by the frozen bound is reachable with positive
probability.** A live state has `y^{+} >= log A` exactly when
`v^{+} >= log(A - 1)`, i.e. when `v^{+} in [log(A-1), log A)`. In exact terms

```text
log(A - 1) = 6.25360981375633376570…
log A      = 6.25553146432147308692…
log(1 + A) = 6.25744942922713551796…
log(1+A) - log A = log(1 + 1/A) = 0.00191796490566243103…
```

so the frozen square omits a band of width `1.918e-3` in each coordinate that
the chain enters whenever `v` lands in an interval of length
`log A - log(A-1) = 1.921e-3` — an event of probability `~1e-3` per step near
the boundary region, and observed at a rate of `1535` live states in `400 000`
simulated paths.

**Consistency of the continuation interval.** The alarm test rewritten in `z`
gives, from a general state `x`,

```text
alarm  <=>  z >= c_SR - x^{+}   or   z <= x^{-} - c_SR ,     c_SR = log A + 1/2 ,
```

which is exactly the frozen `(l(x), u(x)) = (x^- - c_SR, c_SR - x^+)`. That
formula was derived for a general `x` and never used `x < log A`, so it is
**unchanged** by this erratum. With the corrected square it still defines a
nonempty open interval containing `0`:

```text
u(x) = c_SR - x^+ >= c_SR - log(1+A) = 0.49808203509433756896… > 0 ,
l(x) = x^- - c_SR <= -0.49808203509433756896… < 0 ,
```

so the continuation interval always has length `>= 0.99616…`, and
`l(x) < 0 < u(x)` for every reachable `x`. Every structural fact `P5X-T1`
needs about `(l, u)` survives verbatim.

## 6. Explicit counterexample to the old bound

*Deterministic witness (exact).* Take `z_1 = log A + 1/2 - 1/1000` from the
reset state. Then `v^+_1 = log A - 1/1000 < log A`, so no alarm, and

```text
y^+_1 = log(1 + A e^{-1/1000}) = 6.2574484…  >  log A = 6.2555314… .
```

*Simulated witness.* `feasibility/sr_domain_check.py`, fresh seed `20260902`,
`400 000` paths (`feasibility/results/sr_domain_check.json`): maximum live
stored state `6.25744933301356`, which exceeds `log A` and lies below
`log(1+A) = 6.25744942922713`; `1535` live states at or above `log A`.

The derivation in §5 is the proof; the witness only exhibits it.

## 7. Blast radius

| touched? | item | reason |
|---|---|---|
| **NO** | original P5 (`p5_nonlinear_dynamics/`) | P5 never declares a detector state square. `P5-T4` bounds `E[tau]` by a forcing argument from *any* state; `P5-T7`'s minorisation uses the reset state and the `{tau = 1}` event; `P5-T5` is a pathwise Jensen bound. None mentions `b_SR` |
| **NO** | `P5-T1` (raw-mean identity) | pure algebra on the window; no state space |
| **NO** | `P5-T7` (invariant law, ergodicity) | see above; the two-step Doeblin argument is state-space agnostic |
| **NO** | `P5-T11` (ACF identity) | consumes `pi` only |
| **NO** | P5 final-disposition audit | quotes none of this |
| **NO** | `P5X` human proofs `L2`, `L3`, `L5`, `L6` | `L2` and `L5` use only "compact set, scalar innovation, interval continuation"; `L3` uses `c_D` (the alarm margin from the reset state), not `b_D`; `L6` is measure-theoretic |
| **AMENDED, ALREADY** | `P5X` human proof `L1` | `PROOF.md` §L1.3 already derives the correct SR square and flags the defect in place. `L1`'s conclusions `(a)`, `(b)`, `(c)` are proved on the corrected square and are unchanged |
| **NO** | CUSUM path, including the first stop-gate and its FAIL result | `b_CUSUM = h = 5` is exactly right: before an alarm `max(S^+, S^-) < h` and each coordinate is a `max(0, ·)` |
| **YES** | SR **certified** path | a certifier restricted to `[0, log A]^2` would evaluate the candidate outside its domain on a positive-probability region and would produce an **invalid** certificate. This is the whole operative content of `D1` |
| **NO** | `P9` / `P9R` downstream synthesis | they use the SR recurrence directly (P9R even repairs a separate `log 2` first-step defect); neither declares a P5X state square |
| **NO** | `P3`, the `Gamma_SR` certificate, `P6`, `P7`, `P8`, `P8R` | none references `b_SR` |

`DOWNSTREAM_CORE_THREAT = NONE`. The defect is confined to a domain declaration
consumed by a future SR certifier.

## 8. Exact repair semantics

For **future SR certified work only**, read `FROZEN_THEOREM.md` §2 with

```text
b_SR := log(1 + A)        (exact; A = 520.886133602749)
```

everything else in `P5X-T1` unchanged: `c_SR = log A + 1/2`,
`(l(x), u(x)) = (x^- - c_SR, c_SR - x^+)`, `q_SR(x,z) = (softplus(x^+ + z - 1/2),
softplus(x^- - z - 1/2))`, `x_0 = (0,0)`, and the alarm test on the pre-update
`v`. Any SR certificate must state which value of `b_SR` it used and must cite
this erratum.

The historical text is preserved and is cited as **superseded for future SR
certified work**; it is not corrected in place, not deleted, and not
reinterpreted for any past result. No past P5X or P5 verdict changes.

## 9. Classification, argued

| candidate class | verdict |
|---|---|
| `DOCUMENTATION_ERRATUM` | **too weak.** A certifier built to `b_SR = log A` would be *wrong*, not merely mis-documented: it would omit a positive-probability region of the state space and its enclosure would be invalid |
| `SCOPE_ERRATUM` | **no.** The scope of the campaign (detectors, windows, `rho`, `e`, convention A) is unchanged |
| **`CERTIFIER_DOMAIN_ERRATUM`** | **yes.** The defect is in the declared domain on which the certified numerical realisation must operate. It changes one constant in the setup of `P5X-T1` and nothing else |
| `THEOREM_DEFECT` | **no.** No hypothesis, conclusion or proof step of `P5X-T1(a)(b)(c)`, `P5X-T2` or `P5X-T3` uses `b_SR`; `PROOF.md` `L1` is proved on the corrected square with no other change |
| `SCIENTIFIC_CORE_DEFECT` | **no.** Neither P5's core nor P5X's theorem core is affected; see §7 |

Governance route **A**: a non-scientific erratum to a certified-domain
declaration. Route B (theorem-changing scientific correction) is **not**
triggered, so the campaign continues without escalation.
