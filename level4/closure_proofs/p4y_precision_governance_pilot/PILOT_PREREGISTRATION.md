# P4Y pre-freeze pilot — preregistration

```text
STATUS                        = PRE-RESULT, FROZEN
BINDING                       = NO
THIS IS NOT A P4Y CHECKPOINT A
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT   = PARTIAL   (immutable)
P4X_SUCCESSOR_VERDICT = FAIL      (immutable; governance failure)
P4X_SCIENTIFIC_FAILURES = NONE    (immutable)
```

Fixed before any `design` or `validation` replicate is drawn.  The only
numbers already observed when this document was written are the `calibration`
namespace outputs of `run_calibration.py`, which fix the pilot's *scale* and
are recorded in §4; no allocation rule has been evaluated.

---

## 1. What this pilot is allowed to change

Precision-allocation and execution governance.  Nothing else.

Inherited unchanged and out of scope: the P4 theorem, A1–A7, the detector
definitions, the six theorem-supported families, the outside-assumption logic,
the `m` grid `{1,2,3,5}`, the Route-A score estimator, the Route-B Richardson
CRN central difference, the finite-difference steps `(0.05, 0.025)`, the
Richardson rule, the Route-Q role, the Gaussian consistency statistic, the
Lean spine, the Arb certificates, the `0.03` / `|z| <= 4` correspondence
gate, and `r* = 0.010823`.

`tests/test_estimator_nondrift.py` asserts bit equality between the pilot's
per-block evaluation and the frozen `route_a` / `route_b`, so "inherited
unchanged" is checked mechanically rather than asserted.

## 2. The two defects being repaired

**G1 — attainment in expectation only.**  P4X sized stage 1 from a historical
reference and permitted *at most one* top-up, sized deterministically to hit
`r*` on the nose.  A route could therefore finish in a third state: not at
`r*`, and not capped either.  Eight cells did.  The repair must make the
disjunction `ATTAINED or PRECISION_LIMITED` **exhaustive by construction**,
and must attach an explicit probability statement to the first branch.

**G2 — sharding broke the frozen block total.**  P4X used
`per_shard = ceil(B / K)` for every shard, executing `B + ((-B) mod K)`
blocks, and gave each shard its own Philox seed keyed on the worker.  At
`B = 8801`, `K = 5` that is 8805 blocks — four unauthorised blocks and
1 000 000 unauthorised paths.  The repair is an exact balanced partition plus
worker-free logical block addressing.

## 3. Candidate allocation rules — the whole slate, fixed now

All rules read **route-local precision only**.  Discrepancy, its sign, `z`,
pass/fail, the family correspondence result and any cell's history are not
arguments of `rules.run` and cannot be.

| id | shape | stages | target per stage |
|---|---|---|---|
| `A_oneshot_one_topup` | the P4X rule verbatim | 2 | `r*` |
| `B_oneshot_safety_1.15` | one-shot + constant factor | 2 | `r* / 1.15` |
| `B_oneshot_safety_1.30` | " | 2 | `r* / 1.30` |
| `B_oneshot_safety_1.50` | " | 2 | `r* / 1.50` |
| `C_staged_safety_1.00` | staged, cap-terminated | ∞ | `r*` |
| `C_staged_safety_1.15` | " | ∞ | `r* / 1.15` |
| `C_staged_safety_1.30` | " | ∞ | `r* / 1.30` |
| `D_staged_quantile_0.95` | staged, cap-terminated | ∞ | `r* / sqrt(q_0.95(B))` |
| `D_staged_quantile_0.99` | " | ∞ | `r* / sqrt(q_0.99(B))` |

Sizing is the inherited law with the inherited exponents:

```text
blocks_next = blocks * ( achieved_relSE / target ) ** (1 / kappa)

kappa = 0.5                     alpha >= 2   (light tail)
kappa = 1 - 1/alpha = 0.3197…   alpha  < 2   (t1p5, alpha_floor = 1.47)
```

`q_delta(B) = chi2_delta(B-1) / (B-1)`.  If the `B` block means were exactly
normal, the realised relative SE exceeds its true value by more than
`sqrt(q_delta(B))` with probability exactly `1 - delta`.  RULE D therefore
targets the `delta`-quantile of the realised statistic rather than its
expectation — which is precisely what G1 says P4X failed to do.  Because
`q_delta(B) -> 1`, RULE D's surcharge vanishes at production block counts:
`sqrt(q_0.95)` is 1.237 at `B = 24`, 1.082 at `B = 200` and 1.012 at
`B = 8801`.

RULE D uses the quantile on the **target** side only, not additionally on the
estimate of the current relative SE.  The staged structure already absorbs an
under-estimate — it simply buys another stage — and inflating both sides would
double-charge.  This is a design choice, recorded before results.

## 4. Pilot cells and scale — frozen

Fresh independent seeds throughout.  Seed namespace base `4 310 000 000`; the
frozen P4 campaign (`401xxxx`), the P4X R0 pilot (`411xxxx`) and P4X
production (`421xxxx`) all live below `5e6`, so no pilot block can coincide
with any earlier block.  Seeds are an **injective positional code** in
`(cell, namespace, replicate)`; the worker index is not an argument.

| cell | configuration | route | block size | kappa | rationale |
|---|---|---|---|---|---|
| `C1` | `reduced/cusum@2/t1p5` | A | 50 000 | 0.3197 | heavy tail, CUSUM, Route A |
| `C2` | `reduced/cusum@2/t1p5` | B | 20 000 | 0.3197 | heavy tail, CUSUM, Route B |
| `C3` | `reduced/sr@20/t1p5` | A | 50 000 | 0.3197 | heavy tail, SR, Route A |
| `C4` | `reduced/sr@20/t1p5` | B | 20 000 | 0.3197 | heavy tail, SR, Route B |
| `C5` | `reduced/cusum@2/gaussian` | B | 20 000 | 0.5 | finite-variance control |
| `C6` | `reduced/cusum@2/t1p5` | A | **250 000** | 0.3197 | C1 at the production block size |

The pilot is defined at a **stage-1 nominal of `B1 = 24` blocks**, and the
pilot target is

```text
r*_pilot(cell) = relSE_true(cell, 24 blocks) = block_sd / (sqrt(24) * |mu|)
```

at the worst `m`, measured in the `calibration` namespace over 400 blocks and
frozen to four significant figures.  This reproduces the production situation
— a nominal rule that lands exactly on the target — at an affordable block
count.  `r* = 0.010823` itself is untouched and is what P4Y production uses.

**Frozen calibration output (the only results seen before this freeze):**

| cell | worst m | `r*_pilot` | block sd | mean | Hill alpha of block means |
|---|---|---|---|---|---|
| `C1` | 1 | 0.02522 | 0.3061 | 2.47702 | 15.96 |
| `C2` | 1 | 0.08986 | 1.029 | 2.33672 | 5.57 |
| `C3` | 1 | 0.02631 | 0.3611 | 2.80198 | 13.39 |
| `C4` | 1 | 0.1471 | 1.953 | 2.71046 | 4.13 |
| `C5` | 1 | 0.005528 | 0.1677 | 6.19118 | 93.32 |
| `C6` | 1 | 0.01858 | 0.2249 | 2.47184 | 25.24 |

**Direction of the pilot's bias, stated now.**  `B1 = 24` is far below
production block counts (P4X's largest allocation was 8801 blocks).  Realised
precision is *more* variable at fewer blocks, so a rule that attains the
target here is conservative for production, and RULE D's surcharge measured
here is an upper bound on its production surcharge.  `C6` exists to bound the
other deviation — the pilot's smaller blocks — by repeating `C1` at the frozen
250 000-path heavy-tail block size.

## 5. Replication, namespaces and the design/validation split

```text
reference   12 blocks, its own namespace, one draw per replicate
design      R_DESIGN    = 20 replicates per cell   -> tunes the slate
validation  R_VALIDATION = 59 replicates per cell  -> the ONLY source of p_attain
```

Design and validation replicates are addressed in disjoint global ranges
(`0..` and `1000..`), so their reference streams are disjoint too.  No design
replicate is reused as validation evidence.

Within a replicate every rule reads a **prefix of the same block stream**.
That is a common-random-number comparison across rules — it makes the
comparison sharp and costs no more than the greediest rule — while each
rule's own attainment estimate remains an average over `R` independent
replicates.

## 6. Statistical framework — fixed before validation

```text
P4Y_ATTAINMENT_TARGET     delta = 0.95
P4Y_VALIDATION_CONFIDENCE beta  = 0.05   (one-sided, 95% confidence)

p_attain = P( realised relative SE <= r* )   under fresh repetitions

R >= log(beta) / log(delta) = 58.4  ->  R_VALIDATION = 59
```

The bound is the **exact one-sided Clopper–Pearson lower bound**.  At zero
failures it coincides with the brief's `delta**R <= beta` rule
(`lower = beta**(1/R) = 0.9505` at `R = 59`); unlike that rule it remains
defined when a candidate fails once, which is what lets the slate be ranked
rather than merely accepted or rejected.

The brief writes the rule as `(1 - delta)**R <= beta`, which reads `delta` as
the tolerated failure rate.  Here `delta` is the attainment probability
throughout, so the base is `delta`.  The substitution is deliberate.

```text
PRIMARY endpoint    pooled over the 6 cells, R = 354 validation replicates of
                    the SELECTED rule; require Clopper-Pearson lower bound
                    on p_attain >= 0.95
SECONDARY endpoint  per cell, R = 59; require no cell's lower bound < 0.90
```

## 7. Selection criterion — fixed before design results

Among rules that

1. cannot terminate in the third state (`max_stages` infinite), and
2. reach a design attainment fraction `>= 0.95` pooled over the six cells,

select the one with the **smallest mean block multiplier**
`E[blocks used] / B1`.  Ties break on smaller worst-case multiplier, then on
governance simplicity (fewer free parameters).  Cost is never traded against
the attainment target: a cheaper rule that misses `delta` is not selectable.

Only the selected rule's validation bound decides the pilot verdict.  Every
other rule's validation numbers are reported for completeness and for the
comparison table, and are not used to re-select.

## 8. `PRECISION_LIMITED` — the exact mechanical semantics

A route is `PRECISION_LIMITED` **iff**, at the moment the frozen rule computes
the next stage,

```text
blocks_next  >  cap_blocks
```

where `blocks_next` is the allocation the frozen rule requires and
`cap_blocks` is the frozen cost cap for that configuration.  Nothing else
produces the label.  In particular it is NOT produced by: precision missed
after some number of attempts; compute feeling expensive; the route looking
scientifically good or bad; a cell having been historically difficult; or any
quantity that is not route-local precision or frozen cost.

The declaration is a statement about the *next* stage, so it is always made
before that stage's data exists.

Pilot cap: `cap_blocks = CAP_MULTIPLIER * B1 = 6 * 24 = 144`.

## 9. Cost model and CPU budget

```text
PILOT_CPU_CAP_HOURS = 2.0        hard, checked live, never silently extended
calibration already spent        0.0716 CPU-hours
```

Cells are executed cheapest-first so that if the cap binds, the surviving
evidence is maximal.  CPU multipliers are reported in blocks, which are
equal-cost within a cell.

## 10. STOP rules

Execution stops immediately on any of:

1. **CPU cap** — cumulative pilot CPU reaching 2.0 hours;
2. **pool overrun** — any replicate requesting more than
   `12 + 144 = 156` blocks;
3. **estimator drift** — `tests/test_estimator_nondrift.py` failing;
4. **shard-sum breach** — any partition whose executed block count differs
   from the frozen total by even one block;
5. **address-table breach** — a cell or namespace drawing blocks without a
   frozen address, or a seed collision.

A STOP is reported as a STOP.  Partial evidence is reported as partial, and
the pilot verdict then becomes `NEEDS_ONE_MORE_PRE-FREEZE_PILOT`.

## 11. Anti-overfitting commitments

* No P4X result — no realised relative SE, no discrepancy, no `z`, no
  pass/fail, no identity of the eight `PRECONDITION_NOT_MET` cells — enters
  any pilot parameter.  The P4X namespace is not even present on this branch.
* The safety factors, `delta`, `beta`, the stage count, the reserve factors
  and the cap multiplier are all fixed in this document.
* `r*` is not weakened.  No historical cell is relabelled.  No P4X sample is
  reused.
* The pilot's evidence is new: fresh seeds in a namespace three orders of
  magnitude away from every earlier campaign.

## 12. Kill criteria

`DO_NOT_OPEN_P4Y` is recommended if any of: no predeclared rule attains the
target probability; attaining `r*` reliably needs implausible compute;
precision behaviour is too unstable for a finite staged rule; the pilot
uncovers estimator drift; exact shard identity cannot be guaranteed; or the
successor would have to change scientific meaning.

---

# AMENDMENT 1 — recorded after the design phase, before any validation replicate

```text
TIMING   design.json exists; validation.json does NOT.
SCOPE    the DESIGN phase and one ADDED phase only.
          The validation phase runs exactly as frozen above: same cells, same
          R = 59, same seeds, same cap of 144 blocks, same nine rules.
          Nothing already frozen is edited.
```

The design phase is the phase whose purpose is to inform the design, and the
design/validation split exists so that it can.  This amendment is recorded
because it changes the criterion the pilot is finally judged by, and a change
of that kind must be visible and dated rather than silently absorbed.

## A1.1 The defect in §6 / §7 that design exposed

§6 defines `p_attain = P(realised relative SE <= r*)` without saying what to
do with a replicate the cap refused to fund.  §7 then thresholds "the design
attainment fraction" against `delta`.  Read literally — every non-`ATTAINED`
replicate counts against the rule — the pooled design fractions are:

| rule | attained / 120 | fraction |
|---|---|---|
| `A_oneshot_one_topup` | 105 | 0.875 |
| `C_staged_safety_1.00` | 105 | 0.875 |
| `C_staged_safety_1.15` | 97 | 0.808 |
| `D_staged_quantile_0.95` | 95 | 0.792 |
| `D_staged_quantile_0.99` | 91 | 0.758 |

so **no rule is eligible and the frozen criterion selects nothing.**

That result is an artefact of the criterion, not a fact about the rules.
Every one of those shortfalls is a `PRECISION_LIMITED` replicate, and
`PRECISION_LIMITED` is branch B of the requirement this pilot exists to
satisfy — an acceptable, predeclared disposition, not a miss.  Counting it as
a miss makes a *more* careful rule score *worse*, which is why the safety
factors rank below the plain rule above: they cost more, so they meet the
pilot's deliberately tight cap more often.

Conditioning on the cap having permitted the purchase, the same design data
reads:

| rule | attained / funded | 95% CP lower |
|---|---|---|
| `A_oneshot_one_topup` | 105 / 105 | 0.972 |
| `C_staged_safety_1.00` | 105 / 105 | 0.972 |
| `C_staged_safety_1.15` | 97 / 97 | 0.970 |
| `D_staged_quantile_0.95` | 95 / 95 | 0.969 |
| `D_staged_quantile_0.99` | 91 / 91 | 0.968 |

The intent was already recorded pre-result: `run_pilot.summarise_rule`, frozen
in the preregistration commit, computes both readings and its comment states
that "a `PRECISION_LIMITED` route is a declared, legal outcome, not a failure
of the precision rule".  The ambiguity is in the prose, not the code.

## A1.2 What is amended

```text
PRIMARY endpoint (amended)
    p_attain = P( realised relSE <= r*  |  the frozen cap funded the
                  allocation the rule required )
    pooled over cells, Clopper-Pearson lower bound >= delta = 0.95

SECONDARY endpoint (amended)
    per cell, lower bound >= 0.90, same conditioning

TERTIARY endpoint (unchanged, now explicitly secondary)
    the unconditional fraction, reported for every rule, NOT used to select
```

`delta`, `beta`, `R`, the cells, the seeds, the split, the cap, the rules and
the selection rule ("smallest mean block multiplier among eligible") are
**unchanged**.  Only the treatment of a `PRECISION_LIMITED` replicate changes,
from *counts as a failure* to *is not a trial of the precision rule*.

## A1.3 Added phase — cost tail

The pilot cap of `6 * B1 = 144` blocks censors the cost distribution: the
observed maximum multipliers sit at 5.4–6.0, i.e. against the cap.  A frozen
production cap cannot be projected from censored costs, and without it the
unconditional `p_attain` at a production-like cap is unmeasurable.

```text
PHASE       costtail
NAMESPACE   "costtail"          fresh, disjoint from calibration/reference/
                                design/validation
REPLICATES  R = 24 per cell
CAP         16 * B1 = 384 blocks   (pool hard limit 396)
RULES       A_oneshot_one_topup, C_staged_safety_1.00, D_staged_quantile_0.95
RECORDS     blocks each rule spends, and the ORACLE first-crossing block count
            at which the realised relative SE first reaches r*
USED FOR    projecting a production cap, and for an uncensored unconditional
            p_attain at that cap
NOT USED FOR  selecting the rule, setting delta or beta, or the primary
              endpoint
BUDGET      whatever remains under the unchanged 2.0 CPU-hour pilot cap,
            cheapest-first, STOP on exhaustion
```

## A1.4 Consequence for the pilot verdict

The criterion that finally decides the recommendation was amended in the
middle of the pilot.  That is exactly the class of move that turned P4X's
disclosed limitation into an invalidating one, so the amendment is not
allowed to buy a clean bill of health for itself: whatever the validation
numbers say, this pilot cannot return `READY_FOR_BINDING_CHECKPOINT` on an
endpoint it re-defined after seeing design data.  The strongest outcome
available to it is `NEEDS_ONE_MORE_PRE-FREEZE_PILOT`, whose content is
"re-run this identical design with the amended endpoint frozen from the
start".
