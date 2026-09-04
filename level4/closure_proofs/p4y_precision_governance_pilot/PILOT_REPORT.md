# P4Y pre-freeze pilot — report

```text
STATUS = PILOT COMPLETE, NON-BINDING
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT     = PARTIAL   (immutable, untouched)
P4X_SUCCESSOR_VERDICT   = FAIL      (immutable, untouched)
P4X_SCIENTIFIC_FAILURES = NONE      (immutable, untouched)
```

P4X is failed immutable history and is **not present on this branch**;
`level4/closure_proofs/p4x_generalization_boundary/` does not exist here, so
nothing in this pilot could alter, repair, relabel or overwrite it.  The
branch `p4y-prefreeze-pilot` is not merged to `main`.

---

## 1. Reconstructed P4X governance defects

### 1.1 The precision machinery as P4X froze it

| quantity | value | where it comes from |
|---|---|---|
| accuracy criterion | `0.03` | inherited unchanged from Track 3 |
| consistency criterion | `\|z\| <= 4` | inherited unchanged |
| `r*` | `0.010823` | **forced**, not chosen: `1.96 * sqrt(2) * r* = 0.03` |
| per-path tail index, `t1p5` | `alpha = 1.5` exactly; measured floor `1.47` | Student-`t`, `nu = 1.5` |
| `kappa` | `0.5` for `alpha >= 2`; `1 - 1/alpha = 0.3197…` for `alpha < 2` | frozen P4X precision policy |
| sample-size law | `N_req = N_ref * (relSE_ref / r*) ** (1/kappa)` | " |
| block size | `250 000` paths for `alpha < 2`, else `20 000` | " |
| stage structure | stage 1 from the historical reference, then **at most one** top-up | Checkpoint A §8.1 |
| top-up trigger | the route's own achieved relative SE exceeding `r*` | " |
| caps | `TOTAL_CPU_CAP = 60 h`, `PER_CONFIGURATION_CPU_CAP = 40 h` | Checkpoint A §13 |
| `PRECISION_LIMITED` | declared from projected cost alone, before the gate | " |

`r*` is derived **from** the unchanged 3 % criterion rather than replacing it:
if two independent routes each carry relative standard error `r`, their
relative discrepancy has standard deviation `sqrt(2) * r`, so the frozen gate
`<= 0.03` is met with 95 % probability exactly when `1.96 * sqrt(2) * r <=
0.03`.  Nothing about `r*` is negotiable, and this pilot does not touch it.

### 1.2 G1 — why the law targets a nominal point and not an attainment

`N_req = N_ref (relSE_ref / r*)^(1/kappa)` is the inverse of the *deterministic*
relation `relSE(N) = C N^{-kappa}`.  Two of its three ingredients are random
and the third is a model:

1. **`relSE_ref` is an estimate**, not `C`.  It is a sample standard error
   computed from finitely many block means, so `N_req` inherits its error.
2. **The realised relative SE at `N_req` is itself random.**  Even given
   perfect knowledge of `C`, the quantity the gate reads is
   `s_B / (sqrt(B) |xbar_B|)`, a statistic, not a constant.
3. `relSE ∝ N^{-kappa}` is an asymptotic rate, applied at finite `N`.

Solving for the point where the *expected* behaviour equals `r*` therefore
lands the *realised* value on a distribution centred near `r*`.  If the `B`
block means were exactly normal,

```text
s_B^2 / sigma^2  ~  chi2_{B-1} / (B-1)
P(realised relSE <= true relSE) = F_{chi2_{B-1}}(B-1)
                                = 0.557 at B = 12
                                = 0.539 at B = 24
                                = 0.502 at B = 8801
```

so a rule that lands exactly on the target attains it with probability near
one half — **not near one**.  A single deterministic top-up gives roughly one
further look, which lifts that to perhaps three quarters.  It cannot reach
0.95, and no amount of care in *sizing* the top-up changes this, because the
shortfall is in *what is being targeted*: an expectation instead of a
quantile.

This is derived from the structure of the estimator alone.  It uses no P4X
outcome, and it predicts the failure before looking at one.

### 1.3 G1 under a heavy tail — why one top-up is especially fragile

For `alpha < 2` the per-path summand has infinite variance.  Three things
follow, and all of them make a single deterministic correction worse:

* **The reference is median-low and mean-high.**  A sample standard deviation
  of heavy-tailed summands is right-skewed: it is usually *below* the scale it
  estimates, and occasionally far above.  A top-up sized from it is therefore
  usually undersized, and the pilot measures exactly this (§8, unbiased check:
  the realised relative SE fell below its true value on 75 % of fresh draws
  pooled, rising to 100 % on the heaviest-tailed cell, against 55.7 % under
  normality).
* **The correction gets one chance.**  With a fat-tailed statistic, one look
  is not enough; the whole point of a fat tail is that the informative events
  are rare.
* **The law conflates two different rates.**  Writing everything in terms of
  `N` hides that `N` can grow two ways.  Growing the *block size* for
  `alpha < 2` improves the block mean at rate `n^{1/alpha - 1}`; growing the
  *block count* at a fixed block size improves the pooled mean at rate
  `B^{-1/2}` as soon as the block means themselves have finite variance.  P4X's
  `MINIMUM_BLOCK_SIZE = 250 000` rule exists precisely to buy the second
  regime, and this pilot confirms it works: the Hill index of the **block
  means** is 4.1–93 across the pilot cells, everywhere well above 2 (§8).
  Applying `kappa = 0.3197` to *block-count* growth therefore over-buys rather
  than under-buys — and P4X still missed, which localises the failure
  unambiguously in the targeting, not the exponent.

### 1.4 The four configuration-route strata that missed

Recorded as structure only.  No realised relative SE, discrepancy or `z` from
any of them enters any pilot parameter.

| stratum | cells affected |
|---|---|
| `frozen/cusum@5/t1p5` Route A | 2 |
| `frozen/cusum@5/t3` Route A | 1 |
| `frozen/sr@520.886/t1p5` Route A | 3 |
| `reduced/sr@20/t1p5` Route B | 2 |
| **total** | **8 of 96** |

Each had a route that took its one permitted top-up, still missed `r*`, and
did not reach any cap — so it satisfied *neither* branch of the Checkpoint-A
X6 precondition and its gate was not adjudicable.  `C2` became `INCOMPLETE`.
Zero cells failed the scientific gate; 88 of 96 passed it.

### 1.5 G2 — the sharding arithmetic, exactly

`run_c2_stage2_adjudicate.py` split an approved top-up with

```python
per_shard = math.ceil(blocks_total / n_shards)
...
"blocks": per_shard,          # for every one of the n_shards shards
```

so the executed total is `K * ceil(B/K) = B + ((-B) mod K)`, which equals `B`
only when `K` divides `B`.  For the campaign's dominant top-up:

```text
additional_N          = 2 200 168 764.43 paths
frozen blocks_total   = ceil(additional_N / 250 000) = 8 801
frozen paths          = 8 801 * 250 000 = 2 200 250 000
K                     = min(5, ceil(21.187 / 2.0)) = 5
per_shard             = ceil(8801 / 5) = 1 761
executed              = 5 * 1 761       = 8 805     (+4 blocks)
executed paths        = 8 805 * 250 000 = 2 201 250 000   (+1 000 000 paths)
```

which is the recorded `c2_stage2.json` figure exactly.

There is a second half to the defect, and it is the more serious one.  Each
shard was seeded on **the worker**:

```python
"seed": C2.seed_for(layer, kind, family, f"{route}_s2_shard{k}")
```

and then each shard looped `for batch in range(blocks)` internally.  The
scientific random stream was therefore a function of the worker index and the
scheduling, not of the block.  Blocks are i.i.d., so this does not bias the
estimate — but it means "the frozen allocation" had no addressable identity,
changing `K` changed the entire set of blocks the campaign requested, and
nothing in the code could notice that four extra blocks had run.

---

## 2. Inherited immutable scientific scope

Unchanged, not revisited, and mechanically checked where checkable:

the P4 theorem and A1–A7; the detector recursions (`cusum`, `sr`, boundary
inclusive, tested after the update); the six theorem-supported families and
the two outside-assumption families; the `m` grid `{1,2,3,5}`; the Route-A
score estimator; the Route-B Richardson CRN central difference at
`h = (0.05, 0.025)` with `(4 D(h/2) - D(h))/3` formed **per block**; the
Route-Q role as an independent deterministic reference that is *not* a control
variate; the Gaussian consistency statistic; the Lean spine (19 declarations,
axioms `propext`, `Classical.choice`, `Quot.sound`); the 3 Arb objects at 160
bits; the correspondence gate `relative <= 0.03 AND |z| <= 4`; and
`r* = 0.010823`.

Mechanical checks, all passing in this environment:

* `tests/test_estimator_nondrift.py` — pooling the pilot's per-block values
  over `range(B)` reproduces the frozen `route_a` and `route_b` **bit for
  bit**, on Route A, Route B, CUSUM and SR, and on every prefix.
* `tests/test_frozen_anchor_reproduction.py` — all 72 frozen Route-Q
  quadrature anchors reproduce; the frozen protocol file still hashes to the
  `protocol_sha256` recorded in `correspondence.json`; `r*` is re-derived from
  the 0.03 gate rather than read.

`NEW LEAN = NO`, `NEW ARB = NO`, `NEW SCIENTIFIC THEOREM = NO`.  The pilot
found no scientific issue that would contradict that default.

---

## 3. Pilot preregistration

`PILOT_PREREGISTRATION.md`, frozen in commit `12142d1` **before any design or
validation replicate existed**, plus `AMENDMENT 1` recorded in commit
`2d06514` after design and before validation.  In outline:

```text
delta (attainment target)    0.95
beta  (one-sided confidence) 0.05        -> R >= log(beta)/log(delta) = 59
R_design                     20 per cell
R_validation                 59 per cell   (354 pooled over 6 cells)
B1 nominal                   24 blocks
reference                    12 blocks, its own namespace
pilot cap                    6 * B1 = 144 blocks
min blocks                   8
CPU cap                      2.0 CPU-hours, hard, cheapest-first, STOP on reach
seeds                        injective positional code, base 4 310 000 000
```

The amendment is documented in full in the preregistration; §5 of this report
states what it changed and §12 states what it costs the verdict.

## 4. Pilot configurations

| cell | configuration | route | block size | `kappa` | `r*_pilot` | role |
|---|---|---|---|---|---|---|
| `C1` | `reduced/cusum@2/t1p5` | A | 50 000 | 0.3197 | 0.02522 | heavy tail, CUSUM, Route A |
| `C2` | `reduced/cusum@2/t1p5` | B | 20 000 | 0.3197 | 0.08986 | heavy tail, CUSUM, Route B |
| `C3` | `reduced/sr@20/t1p5` | A | 50 000 | 0.3197 | 0.02631 | heavy tail, SR, Route A |
| `C4` | `reduced/sr@20/t1p5` | B | 20 000 | 0.3197 | 0.1471 | heavy tail, SR, Route B |
| `C5` | `reduced/cusum@2/gaussian` | B | 20 000 | 0.5 | 0.005528 | finite-variance control |
| `C6` | `reduced/cusum@2/t1p5` | A | **250 000** | 0.3197 | 0.01858 | `C1` at the production block size |

Six cells, not 96.  The pilot deliberately does not rerun the campaign; it
stresses the phenomenon on a 2 × 2 of `{CUSUM, SR} × {Route A, Route B}` under
`t1p5`, a light-tail control, and one repeat at the frozen production block
size.

`r*_pilot(cell) = relSE_true(cell, 24 blocks)`, measured over 400 blocks in a
`calibration` namespace that no rule and no replicate ever touches again, and
frozen to four significant figures.  This puts the *nominal* rule exactly on
its target — the production situation — at an affordable block count.
`r* = 0.010823` itself is untouched and is what P4Y production would use.

## 5. Candidate allocation rules

Nine, fixed before any replicate.  Every rule is a pure function of
route-local precision: `rules.run` takes `(rule, measure, reference_blocks,
reference_relative_se, r_star, kappa, cap_blocks, min_blocks)` and nothing
else, and `tests/test_rules.py` asserts that signature, so discrepancy, sign,
`z`, pass/fail, family correspondence and cell history have no channel into a
continuation decision.

```text
RULE A   one-shot from the reference, AT MOST ONE top-up, target r*
         -- the P4X rule verbatim, present only as the baseline
RULE B   the same shape, target r*/S for S in {1.15, 1.30, 1.50}
RULE C   staged, terminated ONLY by the cap, target r*/S for S in {1.00, 1.15, 1.30}
RULE D   staged, terminated ONLY by the cap, target r*/sqrt(q_delta(B))
         with q_delta(B) = chi2_delta(B-1)/(B-1), for delta in {0.95, 0.99}
```

Sizing everywhere is the inherited law
`blocks_next = blocks * (achieved / target) ** (1/kappa)` at the inherited
`kappa`.

RULE D is the analytically motivated candidate: it targets the `delta`
**quantile** of the realised statistic instead of its expectation, which is
exactly what §1.2 says P4X failed to do.  Its surcharge is block-count
adaptive and vanishes where production actually lives:

| `B` | `sqrt(q_0.95(B))` | cost surcharge at `kappa = 0.3197` |
|---|---|---|
| 24 | 1.237 | 1.93× |
| 96 | 1.118 | 1.41× |
| 374 | 1.059 | 1.20× |
| 1 258 | 1.033 | 1.11× |
| 8 801 | 1.012 | 1.04× |

## 6. Statistical attainment framework

```text
p_attain = P( realised relative SE <= r* )   under fresh repetitions
bound    = exact one-sided Clopper-Pearson lower bound at confidence 1 - beta
```

At zero failures Clopper–Pearson coincides with the brief's rule of thumb
(`lower = beta**(1/R)`, `= 0.9505` at `R = 59`), and unlike it remains defined
when a candidate fails once, which is what lets nine candidates be *ranked*
rather than merely accepted or rejected.

The brief writes the replicate rule as `(1 - delta)**R <= beta`, which reads
`delta` as the tolerated failure rate.  Throughout this pilot `delta` is the
**attainment** probability, so the base is `delta` and
`R >= log(beta)/log(delta) = 58.4 -> 59`.  Substituting the brief's form
literally would ask for `R = 1`, which certifies nothing; the substitution is
deliberate and was recorded before any result.

**Conditioning.**  `AMENDMENT 1` makes the primary endpoint

```text
p_attain = P( realised relSE <= r*  |  the cap funded the allocation the
              rule required )
```

because `PRECISION_LIMITED` is branch B of the requirement this pilot exists
to satisfy — a predeclared, acceptable disposition — not a miss.  Counting it
as a miss ranks a *more* careful rule *below* a less careful one, which is how
the ambiguity announced itself.  The unconditional fraction is reported for
every rule and is not used to select.  §12 states the price the verdict pays
for that amendment having been made mid-pilot.

## 7. Fresh-seed policy

```text
seed(cell, namespace, replicate)
    = 4 310 000 000
    + cell_index      * 1 000 000
    + namespace_index *   100 000
    + replicate
```

* **Fresh.**  The frozen P4 campaign uses `401xxxx`, the P4X R0 pilot
  `411xxxx`, P4X production `421xxxx` — all below `5e6`.  The pilot base is
  above `4.3e9`.  No pilot block can coincide with any earlier block, and no
  P4X sample is reused as pilot evidence.
* **Injective, and proved so.**  Not `SEED_BASE + sha256(...) % 9973`, the
  pattern inherited from the earlier campaigns.  Over the few thousand
  addresses a replicated pilot needs, a birthday collision in a 9 973-wide
  space is near-certain, and two colliding addresses do not merely share a
  number — they replay the *same blocks*, so replicates counted as independent
  silently stop being independent.  The pilot found this with its own test
  before it found anything else, and replaced the scheme.  **This is a defect
  P4Y should fix in production too.**
* **Worker-free.**  `derive_seed` has no worker, shard, `K` or pid argument,
  and a test asserts the signature.
* **Split.**  `calibration`, `reference`, `design`, `validation` and
  `costtail` are disjoint namespaces; design replicates are numbered from 0,
  validation from 1 000, cost tail from 5 000, so their reference streams are
  disjoint too.
* **Address table frozen.**  A cell with no declared index cannot draw a
  block at all; re-registering a key at a different index, or reusing an
  index, raises rather than overwriting.  First-touch ordering is rejected
  precisely because it would make a seed depend on which script ran first.

## 8. Exact shard partition algorithm

```python
def partition(total_blocks: int, workers: int) -> list[int]:
    q, r = divmod(total_blocks, workers)
    sizes = [q + 1 if i < r else q for i in range(workers)]
    verify(sizes, total_blocks)      # raises unless sum == B and spread <= 1
    return sizes

def block_ids(total_blocks, workers, shard) -> range:
    sizes  = partition(total_blocks, workers)
    start  = exclusive_prefix_sum(sizes)[shard]
    return range(start, start + sizes[shard])
```

`sum(sizes) = q*K + r = B` by the division algorithm, and the multiset of
sizes is `{q+1}` `r` times and `{q}` `K-r` times, so `max - min <= 1`.  These
two properties together determine the multiset uniquely, which a test asserts.
Empty shards are kept rather than dropped: dropping one would silently change
`K`, and the addressing makes them free.

Coverage is checked **structurally**, never by enumeration — a frozen total
can be billions of blocks and nothing is allowed to materialise them.  The
shard ranges are contiguous, start at 0, and abut, so they tile `range(B)`
iff each start equals the previous end and the last end is `B`.

Crucially, `block_ids` returns *logical* indices into one global index space,
and the Philox stream is keyed on `(seed(cell, namespace, replicate),
logical_block_id)`.  A shard therefore evaluates a **subset of the same
blocks** under the **same seed**.  `K` is a scheduling parameter and nothing
else.

## 9. Shard-sum tests

`tests/test_shard_invariants.py`, 75 tests, all passing.

| requirement | test | result |
|---|---|---|
| `B` divisible by `K` | `(100, 5)` | exact |
| `B` **not** divisible by `K` | `(8801, 5)` | exact |
| `B < K` | `(3, 5)` | exact, two empty shards |
| `B = 1` | `(1, 1)` and `(1, 5)` | exact |
| `B = 0` | `(0, 4)` | exact |
| very large `B` | `2 200 168 765`, `10**12 + 1`, `8801 * 250 000` | exact, audited without enumeration |
| historical case | `B = 8801`, `K = 5` | **8 801, not 8 805** |
| exact path total | `8801 * 250 000` | `2 200 250 000`, `delta_paths = 0` |
| over/under by one block | every `K` in `{1,2,3,5,7,8,13,64}` × every `B` | `delta_blocks == 0` |

```text
partition(8801, 5) = [1761, 1760, 1760, 1760, 1760]      sum = 8801
p4x_defective_partition(8801, 5) = [1761]*5              sum = 8805
                                                         over = 4 blocks
                                                         over = 1 000 000 paths
```

The defective partition is reproduced verbatim in `shard.py` as
`p4x_defective_partition` and pinned by a test, so a regression to it cannot
pass silently.  A further test proves the general form of the defect:
`sum(p4x_partition(B,K)) - B == (-B) % K`, zero **iff** `K` divides `B`.

`verify()` raises on an over-execution (`+4 blocks`), on an under-execution
(`-1 blocks`), and on an unbalanced partition; it does not warn.  The one test
the brief asks for — fail if aggregate execution differs from the frozen
allocation by even one block — is `test_no_over_or_under_execution_for_any_k`.

```text
P4Y_EXACT_SHARD_SUM_INVARIANT = PASS
```

## 10. RNG / block identity tests

`tests/test_rng_block_identity.py`, 29 tests, all passing.

| requirement | result |
|---|---|
| logical block set invariant under `K ∈ {1,2,5,7,12,64}` | union of shard ranges `== range(B)`, no block on two workers |
| block values bit-identical across `K` | Route A **and** Route B, every block, `K ∈ {1,2,5,7,12,64}` |
| pooled summary equals the unsharded pooling formula | pooled mean and SE equal **exactly**, not approximately |
| path total invariant under `K` | `sum(sizes) * block_size` constant |
| seed takes no worker argument | signature asserted to be `(cell_key, namespace, replicate)` |
| seed derivation injective | proved over the whole declared address space |
| stream `(seed, block id)` never reused | proved |
| namespace disjoint from every earlier campaign | `4.31e9` vs `< 5e6` |
| P4X-style per-shard seeding | reproduced, and shown to share **no block** with the unsharded allocation |

Floating-point reduction *order* is deliberately not pinned: the frozen
specification does not demand it, and block-count and block membership are
what the specification actually fixes.  Both of those are identical across
every `K` tested.

```text
P4Y_RNG_BLOCK_IDENTITY = PASS
```

## 17. Exact `PRECISION_LIMITED` semantics

Stated mechanically, as the code implements it and as a P4Y checkpoint should
freeze it.

```text
A route is PRECISION_LIMITED if and only if, at the moment the frozen rule
computes its next stage,

        blocks_next  >  cap_blocks

where
    blocks_next = the allocation the FROZEN rule requires next, computed from
                  the route's own achieved relative SE by the frozen scaling
                  law and nothing else;
    cap_blocks  = the frozen cost cap for that configuration, fixed in the
                  checkpoint before production begins.
```

Consequences, each of which is a test:

* **It is a statement about the *next* stage.**  It is therefore always made
  *before* that stage's data exists, and can never be made after seeing a
  result.
* **Nothing beyond the cap ever executes.**  `test_a_route_never_executes_
  beyond_the_cap` asserts `blocks <= cap` for every cap tried.
* **It is not "precision missed after some number of attempts".**  A route may
  take many stages and still not be precision-limited
  (`test_precision_limited_is_not_produced_by_repeated_attempts_alone`).
* **It is not "compute felt expensive"**, not "the route looked
  scientifically good", not "this cell was historically difficult".  None of
  those quantities is an argument of `rules.run`, and a test asserts the exact
  parameter set.
* **It is exhaustive with `ATTAINED`.**  For a cap-terminated rule the loop
  can only exit by `achieved <= r*` or by `blocks_next > cap`.
  `test_staged_rules_cannot_reach_the_third_state` drives every staged
  candidate with a converging route, a stuck route and a hopeless route and
  asserts the terminal state is always one of the two.

The third state is representable in the code — as `UNRESOLVED` — for exactly
one reason: so that the bounded-stage baselines can be *shown* to produce it.
`test_the_p4x_shaped_rules_can_reach_the_third_state` drives a two-stage rule
to `UNRESOLVED` with the cap set to `10**9`, i.e. with cost demonstrably not
the binding constraint.  A frozen P4Y rule must satisfy
`can_end_unresolved(rule) is False`, which is a one-line check on the frozen
object.

---

## 11. Pilot results

```text
calibration   400 blocks x 6 cells                       0.0716 CPU-hours
design         20 replicates x 6 cells x 9 rules         0.2375 CPU-hours
validation     59 replicates x 6 cells x 9 rules         0.5903 CPU-hours
cost tail      24 replicates x 6 cells x 3 rules (AMD 1) see sec. 14
                                                  cap =  2.0 CPU-hours, not reached
STOPPED = NO   (no STOP rule fired in any phase)
```

### 11.1 The headline

On 354 fresh validation replicates the P4X-shaped rule left **9 routes in the
third state** — neither at `r*` nor capped — and the same rule with the single
change "continue until attained or the cap refuses" left **0**, attained the 9
routes the baseline abandoned, and cost **1.2 % more compute**.

| | `A_oneshot_one_topup` (P4X shape) | `C_staged_safety_1.00` (selected) |
|---|---|---|
| third state possible by construction | **YES** | no |
| `UNRESOLVED` observed / 354 | **9** | **0** |
| attained / funded | 273 / 282 | **282 / 282** |
| `p_attain` given the cap funded it | 0.9681 | **1.0000** |
| 95 % Clopper–Pearson lower bound | 0.9450 — **below** `delta` | **0.9894** — above |
| mean block multiplier | 1.1277 | 1.1412 |
| compute cost relative to the baseline | 1.000 | **1.012** |

The nine `UNRESOLVED` replicates are the P4X failure mode reproduced under
fresh seeds, in a namespace three orders of magnitude away from any P4X
block, with no P4X outcome used anywhere in the design.  They fell on four of
the six cells: `C1` ×2, `C3` ×1, `C2` ×1, and `C5` ×5.

**`C5` is the cleanest evidence in the pilot.**  It is the finite-variance
Gaussian control, and on it the cap never once bound — `PRECISION_LIMITED = 0`
across all 59 replicates of every rule.  Cost was therefore never the
constraint, and the P4X-shaped rule *still* left 5 of 59 routes (8.5 %) in the
third state, while the staged rule attained 59 of 59.  That isolates G1 as a
defect of the *stage structure* alone, with heavy tails and compute limits
both removed from the picture.

### 11.2 Design phase, and what the frozen criterion literally said

Read literally, the original §7 criterion — under which a `PRECISION_LIMITED`
replicate counts against the rule — selected **nothing**: pooled design
attainment ran 0.725 to 0.875 for all nine candidates, against `delta = 0.95`.
Every shortfall was a `PRECISION_LIMITED` replicate against the pilot's
deliberately tight `6 × B1` cap.  Under that reading the *more* careful rules
score *worse*, because they cost more and so meet the cap more often:
`B_oneshot_safety_1.50` scores 0.725, the worst of the nine, while being the
most conservative.  That inversion is what exposed the ambiguity.  §12 records
what the amendment costs the verdict.

## 12. Attainment probability estimates

Validation, 59 replicates × 6 cells = 354 per rule.  "funded" excludes
replicates the cap refused to pay for, which are branch B of the requirement
and not trials of the precision rule (`AMENDMENT 1`).

| rule | third state possible | `UNRESOLVED` / 354 | attained / funded | `p_attain` (funded) | `p_attain` (uncond.) | mean × | max × |
|---|---|---|---|---|---|---|---|
| `A_oneshot_one_topup` | **YES** | **9** | 273 / 282 | 0.9681 | 0.771 | 1.13 | 5.67 |
| `B_oneshot_safety_1.15` | **YES** | **2** | 262 / 264 | 0.9924 | 0.740 | 1.40 | 5.96 |
| `B_oneshot_safety_1.30` | **YES** | **1** | 247 / 248 | 0.9960 | 0.698 | 1.58 | 6.00 |
| `B_oneshot_safety_1.50` | **YES** | 0 | 231 / 231 | 1.0000 | 0.653 | 1.68 | 5.96 |
| `C_staged_safety_1.00` | no | **0** | **282 / 282** | **1.0000** | 0.797 | **1.14** | 5.67 |
| `C_staged_safety_1.15` | no | 0 | 264 / 264 | 1.0000 | 0.746 | 1.41 | 5.96 |
| `C_staged_safety_1.30` | no | 0 | 248 / 248 | 1.0000 | 0.701 | 1.59 | 6.00 |
| `D_staged_quantile_0.95` | no | 0 | 261 / 261 | 1.0000 | 0.737 | 1.68 | 5.96 |
| `D_staged_quantile_0.99` | no | 0 | 248 / 248 | 1.0000 | 0.701 | 1.83 | 5.96 |

Three things are visible at once.

1. **Only the bounded-stage rules ever reach the third state**, and they reach
   it in proportion to how little they overspend: the cheapest, `RULE A`, hits
   it 9 times.  Buying the third state away with a safety factor *works* —
   `B_safety_1.50` never hit it in 354 — but costs 49 % more compute and still
   cannot *guarantee* the disjunction, because nothing in its structure
   forbids the state.
2. **Every cap-terminated rule attains on every funded replicate**, whatever
   its safety factor.  The staged structure subsumes the safety factor: once
   the rule is allowed to look again, inflating the target buys nothing except
   compute.
3. **The unconditional column is dominated by the pilot's cap**, not by
   precision.  It falls monotonically as the rules get more expensive, which
   is a statement about a `6 × B1` cap and not about any rule's ability to
   reach `r*`.

### 12.1 Unbiased confirmation of the G1 mechanism

Every replicate draws exactly 12 reference blocks unconditionally, so the
fraction of replicates whose realised relative SE falls below its *true* value
is an unbiased estimate of "does a rule that targets the truth attain it?"

| cell | Hill alpha of block means | realised ≤ true at `B = 12` |
|---|---|---|
| `C5` `cusum@2/gaussian` B | 68–93 | 0.500 |
| `C1` `cusum@2/t1p5` A | 15.1 | 0.600 |
| `C3` `sr@20/t1p5` A | 13.2 | 0.700 |
| `C2` `cusum@2/t1p5` B | 4.1 | 0.800 |
| `C6` `cusum@2/t1p5` A, 250 k blocks | 22.7 | 0.900 |
| `C4` `sr@20/t1p5` B | 4.3 | 1.000 |
| **pooled (design, 120 draws)** | | **0.750** |

The Gaussian control lands at 0.500 against the chi-square prediction of
0.557 — the expectation-targeting rule attains its own target barely half the
time, exactly as §1.2 derives.  The heavy-tailed cells sit *above* 0.5 and
rise monotonically as the block-mean tail gets heavier, which is the
right-skew of a heavy-tailed sample standard deviation: it is usually below
the scale it estimates, and occasionally far above.  That is the shape §1.3
predicts, and it is why the failures, when they come, are large.

Note also that the Hill index of the **block means** is 4.1–93 everywhere —
comfortably above 2 — so the frozen `MINIMUM_BLOCK_SIZE` rule does buy the
finite-variance regime it was designed to buy.  The heavy tail lives inside a
block, not across blocks.

## 13. Confidence bounds

```text
PRIMARY   (AMENDMENT 1, conditional)
  rule                       C_staged_safety_1.00
  attained / funded          282 / 282
  PRECISION_LIMITED          72 of 354
  UNRESOLVED                 0 of 354
  p_attain                   1.0000
  95% Clopper-Pearson lower  0.9894    >= delta = 0.95     MET

SECONDARY (per cell, R = 59, threshold 0.90)
  C1  40 / 40 funded   lower 0.9278
  C3  42 / 42 funded   lower 0.9312
  C2  40 / 40 funded   lower 0.9278
  C4  53 / 53 funded   lower 0.9450
  C6  48 / 48 funded   lower 0.9395
  C5  59 / 59 funded   lower 0.9505
  minimum                    0.9278   >= 0.90              MET

TERTIARY  (unconditional, reported, not decisive)
  p_attain                   0.797     at a 6 x B1 cap
```

For contrast, the same bound on the P4X-shaped baseline is **0.9450**, which
is *below* `delta = 0.95`.  The bounded-stage rule fails the target it was
meant to meet; the staged rule clears it.

## 14. CPU multipliers

### 14.1 What the repair costs, measured against the baseline directly

The staged rule and the P4X-shaped rule read the *same* block stream in each
replicate, so their spends can be compared replicate by replicate rather than
in aggregate.  Over 317 validation replicates where the baseline ran at least
one block:

```text
spend( C_staged_safety_1.00 ) / spend( A_oneshot_one_topup )

    median   1.000        q90  1.000        q95  1.000
    mean     1.0105       q99  1.386        max  2.022
    identical in 97.2 % of replicates
```

The staged rule spends **exactly what the P4X rule spends in 97 % of routes**.
It costs more only on the routes where the P4X rule would have given up, and
there it costs 1.37× on average (median 1.33, worst 2.02) — and attains.

That is the whole economics of the repair: it is free where nothing was wrong,
and where something was wrong it buys the answer for about a third more.

### 14.2 The uncensored cost tail (AMENDMENT 1, 16× cap, 144 replicates)

| cell | route | oracle q50 / q90 / q95 / max | `C_staged_1.00` attained | mean × | q90 × | q95 × | max × |
|---|---|---|---|---|---|---|---|
| `C1` | A | 0.79 / 1.54 / 1.83 / 2.83 | 19 / 24 | 3.11 | 7.75 | 9.25 | 13.04 |
| `C3` | A | 0.38 / 1.25 / 1.75 / 3.46 | 19 / 24 | 2.09 | 5.08 | 6.42 | 13.42 |
| `C2` | B | 0.58 / 0.92 / 1.42 / 3.21 | 22 / 24 | 2.05 | 5.04 | 6.17 | 6.46 |
| `C4` | B | 0.33 / 1.21 / 1.46 / 1.67 | 22 / 24 | 2.48 | 6.79 | 11.08 | 15.62 |
| `C6` | A | 0.33 / 0.88 / 1.21 / 1.46 | 21 / 24 | 2.19 | 8.33 | 9.17 | 10.38 |
| `C5` | B | 0.92 / 1.42 / 1.42 / 1.83 | **24 / 24** | 1.40 | 1.88 | 2.04 | 2.67 |
| **pooled** | | 0.50 / 1.42 / **1.67** / 3.46 | **127 / 144 = 0.882** | 2.22 | 5.42 | **8.33** | 15.62 |

The "oracle" is the smallest block count at which the realised relative SE
first reaches `r*` — the cost a rule with hindsight would pay.  Its 95th
percentile is **1.67 × B1**.  The rule's 95th percentile is **8.33 × B1**.

**The pilot's cost tail is not precision difficulty; it is sizing noise
amplified by the exponent.**  The rule sizes from a measured relative SE and
raises the ratio to `1/kappa = 3.128`.  A one-standard-deviation fluctuation
in that measurement therefore inflates the allocation by:

| blocks the measurement rests on | rel. sd of the measured SE | inflation at `kappa = 0.3197` | at `kappa = 0.5` |
|---|---|---|---|
| 12 (the pilot's reference) | 21.3 % | **+83 %** | +47 % |
| 24 (the pilot's `B1`) | 14.7 % | +54 % | +32 % |
| 96 | 7.3 % | +24 % | +15 % |
| 204 | 5.0 % | +16 % | +10 % |
| 374 | 3.7 % | +12 % | +7 % |
| 1 258 | 2.0 % | +6 % | +4 % |
| 8 801 | 0.8 % | **+2 %** | +2 % |

Production block counts in the frozen scope run from 48 to 9 021, so the
production cost tail is one to two orders of magnitude tighter than the
pilot's.  The pilot's tail is a **strong upper bound**, not a forecast.

This also identifies the single largest cost lever available to a future P4Y,
and §16.2 records it as a question for the next pilot rather than acting on it
here.

## 15. Candidate comparison

Against every criterion the brief lists, on the validation data.

| criterion | `A` (P4X shape) | `B` safety 1.15/1.30/1.50 | `C` staged 1.00 | `C` staged 1.15/1.30 | `D` quantile 0.95/0.99 |
|---|---|---|---|---|---|
| estimated attainment (funded) | 0.9681 | 0.992 / 0.996 / 1.000 | **1.0000** | 1.000 / 1.000 | 1.000 / 1.000 |
| one-sided 95 % lower bound | 0.9450 ✗ | 0.976 / 0.981 / 0.987 | **0.9894** ✓ | 0.989 / 0.988 | 0.989 / 0.988 |
| third state reachable | **YES** | **YES** | no | no | no |
| `UNRESOLVED` observed / 354 | **9** | 2 / 1 / 0 | **0** | 0 / 0 | 0 / 0 |
| expected CPU multiplier | 1.13 | 1.40 / 1.58 / 1.68 | **1.14** | 1.41 / 1.59 | 1.68 / 1.83 |
| worst observed CPU multiplier | 5.67 | 5.96 / 6.00 / 5.96 | 5.67 | 5.96 / 6.00 | 5.96 / 5.96 |
| Route A vs Route B | A: 2 UNRES; B: 1 | mixed | **identical, 0 both** | 0 both | 0 both |
| CUSUM vs SR | CUSUM 3; SR 1 | mixed | **identical, 0 both** | 0 both | 0 both |
| under `t1p5` | 4 UNRES over 4 heavy cells | 2 / 1 / 0 | **0** | 0 | 0 |
| light-tail control `C5` | **5 UNRES of 59, cap never bound** | 1 / 0 / 0 | **0 of 59, 59/59 attained** | 0 | 0 |
| ease of freezing | 2 numbers | 3 numbers | **2 numbers** | 3 numbers | 3 numbers + a chi-square table |
| governance simplicity | admits a state with no disposition | same | **exhaustive by construction** | exhaustive | exhaustive, but `q_delta` must be frozen too |

Robustness is uniform: every cap-terminated rule attained on every funded
replicate on Route A and Route B, on CUSUM and on SR, on `t1p5` and on the
Gaussian control, and at both the pilot block size and the production block
size (`C1` vs `C6`).  Nothing separates the staged rules on attainment.  They
separate only on cost, and there the cheapest is the plainest.

**The safety factor and the quantile inflation buy nothing.**  Once the rule
is allowed to look again, `C_1.15`, `C_1.30`, `D_0.95` and `D_0.99` attain
exactly as often as `C_1.00` and cost 24 %, 39 %, 47 % and 60 % more.  RULE D
was the analytically motivated candidate and the pilot's own result is that it
is unnecessary: its job — protecting against the realised statistic landing
above its expectation — is done for free by the next stage.  That is a
negative result about a rule this pilot proposed, and it is reported as such.

## 16. Recommended future allocation rule

```text
P4Y_RECOMMENDED_ALLOCATION_RULE = C_staged_safety_1.00

  stage 1     blocks = max(MIN_BLOCKS,
                           ceil(B_ref * (relSE_ref / r*) ** (1/kappa)))

  loop        measure the route's own achieved relative SE at the worst m
              over the frozen m grid, pooling every block drawn so far

              if achieved <= r*                      -> ATTAINED, stop
              blocks_next = ceil(blocks * (achieved / r*) ** (1/kappa))
              if blocks_next > cap_blocks            -> PRECISION_LIMITED, stop
              draw blocks_next - blocks FRESH logical blocks and repeat

  r*          0.010823        unchanged
  kappa       0.5 if alpha >= 2, else 1 - 1/alpha    unchanged
  block size  250 000 for alpha < 2, else 20 000     unchanged
```

This is the **smallest** change to the P4X rule that meets the target: delete
"at most one top-up", and let the cap be the only terminator.  It adds no
safety factor, no reserve, no new tunable, and no new statistical object.  It
is the same two frozen numbers P4X already had.

Its predeclared probability-of-attainment interpretation is explicit:

> For any route whose required allocation the frozen cap will fund, the rule
> attains `r*` with probability at least `delta = 0.95`; validated at 282 of
> 282 funded replicates, one-sided 95 % Clopper–Pearson lower bound 0.9894.

And the disjunction the brief asks for is a **theorem about the rule**, not an
empirical claim: the loop has exactly two exits, so `ATTAINED or
PRECISION_LIMITED` is exhaustive for every route, every cell and every
realisation, including ones the pilot never drew.

### 16.2 Two questions this pilot deliberately did not answer

Recorded so that a future pilot predeclares them instead of discovering them.

1. **Which exponent governs block-count growth.**  The frozen law writes
   `relSE ∝ N^{-kappa}` and applies `kappa = 0.3197` for `alpha < 2`.  But
   P4X and P4Y both grow `N` by adding blocks at a *fixed* block size, and the
   pilot measures the Hill index of the **block means** at 4.1–93 — finite
   variance — for which the exact block-count rate is `B^{-1/2}`, i.e.
   `kappa = 0.5`.  Using 0.3197 there is not conservative in a useful way: it
   raises the noise-amplifying exponent from 2 to 3.128, which §14.2 shows is
   what produces the entire cost tail.  A next pilot should carry
   `kappa_blockcount ∈ {0.3197, 0.5}` as a **predeclared candidate pair**.
   This pilot did not predeclare it and therefore does not act on it.
2. **What `cap_blocks` should be.**  See §20.

`D_staged_quantile_0.95` remains the recommended fallback if a future pilot
finds a regime where the staged structure alone does not suffice; its
machinery is implemented and tested here and its surcharge vanishes at
production block counts (1.04× at `B = 8801`).

## 18. Future P4Y full-production design — designed, NOT created

Nothing below is created by this pilot.  There is no `checkpoint_a/`
directory, no `checkpoint_a.json`, no anchor commit and no binding text.

### 18.1 Inherited unchanged from P4/P4X

The theorem; the scientific scope; all 96 theorem-supported cells and the 32
outside-assumption rows; the six families; the `m` grid `{1,2,3,5}`; both
detectors at both layers; the Route-A and Route-B estimators with their frozen
finite-difference steps and per-block Richardson combination; the Route-Q and
Route-N roles; `r* = 0.010823`; and the meanings of `C1`, `C3`, `C4`, `C5`,
`C6` and `C7`.

`NEW LEAN = NO`.  `NEW ARB = NO`.  `NEW SCIENTIFIC THEOREM = NO`.  The
obligation is re-verification of the 19 inherited Lean declarations and the 3
Arb objects at 160 bits, exactly as P4X held it.

### 18.2 What changes — the precision-allocation and execution machinery only

| # | change | why |
|---|---|---|
| 1 | `X6` precondition becomes the two-exit staged loop of §16 | G1: makes `ATTAINED or PRECISION_LIMITED` exhaustive by construction |
| 2 | `C2` semantics: no route may end in a third state, and a checkpoint test asserts `can_end_unresolved(frozen_rule) is False` | G1: the property is checked, not promised |
| 3 | `PRECISION_LIMITED` frozen to the mechanical definition of §17 | G1: removes every non-mechanical reading |
| 4 | all sharding through `shard.partition`, with an execution ledger asserting `delta_blocks == 0` before the run is accepted | G2: the frozen total becomes unfalsifiable |
| 5 | Philox streams keyed on `(seed(cell, namespace, replicate), logical_block_id)`, with no worker argument in the seed | G2: block identity survives any `K` |
| 6 | seeds by an injective positional code, not `hash % 9973` | latent defect found by this pilot; see §7 |
| 7 | a per-configuration `cap_blocks`, frozen in the checkpoint, expressed in **blocks** rather than projected CPU-hours | so the cap that decides `PRECISION_LIMITED` is exact and knowable before the run |

Change 7 is worth stating plainly.  P4X's caps were CPU-hour caps against
*projected* cost, so whether a route was `PRECISION_LIMITED` depended on a
cost model.  A block cap is a count, it is exact, and it makes §17's
`blocks_next > cap_blocks` a comparison of two integers.

### 18.3 Scope of P4Y production

**Fresh full-scope production.**  All 96 theorem-supported cells and both
routes, re-run from scratch under the new machinery, in a fresh seed
namespace.

Running only the eight historical `PRECONDITION_NOT_MET` cells is **not**
recommended and would not be accepted: it would make the successor's evidence
conditional on which cells a failed campaign happened to leave open, which is
the selection effect the anti-overfitting rules exist to prevent.  No P4X
sample may be reused as P4Y result-bearing evidence.

### 18.4 What a P4Y Checkpoint A must additionally contain

* `cap_blocks` per configuration, as a frozen integer, justified by a cost
  study that resolves §20's open point.
* The `delta`/`beta` pair and the exact conditioning of `p_attain`, frozen in
  prose that does not admit the reading §11.2 exposed.
* A test asserting the frozen rule cannot reach the third state.
* A test asserting `sum(shard sizes) == frozen total` for the actual `K` the
  run will use.
* The pre-registered cost risk, as P4X honourably did.

## 19. Projected P4Y CPU cost

Basis: P4X's own measured execution of the identical scientific scope —
24.749 CPU-hours total, 18.599 CPU-hours on its largest configuration
(`frozen/cusum@5/t1p5`) — scaled by the spend ratio this pilot measured
replicate-by-replicate against that same baseline rule.

```text
                                         central     conservative
  ratio applied            median 1.000   q99 1.386
  P4Y_PROJECTED_TOTAL_CPU        25.0 h        34.3 h     cap 60 h
  P4Y_PROJECTED_MAX_CONFIG_CPU   18.8 h        25.8 h     cap 40 h
```

The central figure is the honest one: the staged rule spends *identically* to
the P4X rule on 97 % of routes, so P4Y's cost is P4X's cost plus the
continuation of the routes P4X abandoned, and those were among its cheaper
ones (final block counts 93, 204, 374 and 1 258, against 9 021 on the
configuration that dominated the bill).  The conservative figure applies the
pilot's 99th-percentile ratio to the *entire* campaign, which is deliberately
pessimistic twice over: it assumes every route lands in the worst percentile,
and it uses a ratio measured at `B_ref = 12`, `B1 = 24`, where §14.2 shows the
sizing noise is one to two orders of magnitude larger than in production.

Both figures sit inside the inherited `60 h` total and `40 h` per-configuration
caps, so **the caps do not need to be raised** and the pilot does not propose
raising them.

## 20. Kill-criteria outcome

| kill criterion | outcome |
|---|---|
| no practical predeclared rule attains the target probability | **not met** — `C_staged_safety_1.00` attains 282/282 funded, lower bound 0.9894 ≥ 0.95 |
| attaining `r*` reliably requires implausible compute | **not met** — +1.2 % over the failed campaign's own spend; identical on 97 % of routes |
| precision behaviour too unstable for a finite staged rule | **not met** — 0 of 354 unresolved; the rule is finite by construction, terminated by the cap |
| the pilot uncovers estimator drift | **not met** — per-block evaluation is bit-identical to the frozen `route_a`/`route_b`; all 72 frozen Route-Q anchors reproduce; the frozen protocol still hashes to its recorded digest |
| exact shard identity cannot be guaranteed | **not met** — 75 shard tests and 29 identity tests pass, including `B = 8801, K = 5 -> 8801` |
| the successor would have to change scientific meaning | **not met** — `r*`, the gate, the estimators, the families, the `m` grid and the theorem are untouched; `NEW LEAN = NO`, `NEW ARB = NO` |

**No kill criterion fired.  `DO_NOT_OPEN_P4Y` is not recommended.**

### 20.1 The one thing that is genuinely not established

A frozen `cap_blocks` cannot yet be written down honestly.

At the pilot's scale a **16× cap still leaves 12 % of routes
`PRECISION_LIMITED`** (127 of 144 attained), so the cost distribution is not
covered even there, and the pilot cannot name the multiple at which
`PRECISION_LIMITED` becomes rare rather than routine.  §14.2 gives strong
reason to expect the production tail to be one to two orders of magnitude
tighter — the entire tail is sizing noise raised to the power `1/kappa`, and
production rests on 48–9 021 blocks rather than 12 — but *expecting* is not
*measuring*, and a cap is exactly the number that decides whether a route gets
a disposition or a result.

Writing a cap on an extrapolation is the shape of the mistake that ended P4X.
This pilot declines to do it.

## 21. Should a P4Y campaign be opened?

**Not yet — one more pre-freeze pilot first.**  The governance machinery is
sound, cheap and provable, and no kill criterion fired.  Two things stand
between here and a binding checkpoint, and neither is a scientific problem:

1. **The deciding criterion moved mid-pilot.**  `AMENDMENT 1` re-defined the
   primary endpoint after design data existed.  The amendment is right — §11.2
   shows the original reading ranks careful rules below careless ones — but a
   successor to a campaign that failed on governance cannot be opened on an
   endpoint that was re-defined once results were in view.  The
   preregistration said so before validation ran, and this report holds to it.
2. **The cap is not measured.**  §20.1.

The next pilot is small and its content is already determined: re-run *this
identical design* with (a) the amended endpoint frozen from the start,
(b) `B_ref` and `B1` at production-representative block counts so the cost
tail is measured where production lives rather than extrapolated to it, and
(c) `kappa_blockcount ∈ {0.3197, 0.5}` as a predeclared candidate pair.  It
needs no new estimator, no new theorem, and no new formal work.

```text
P4Y_GOVERNANCE_FEASIBILITY = STRONG
P4Y_PILOT_VERDICT          = NEEDS_ONE_MORE_PRE-FREEZE_PILOT
```

---

## Repository safety

```text
branch                      p4y-prefreeze-pilot, off main, NOT merged
worktree                    /Users/suzhe/ReBaseGuard-p4y
writes outside this dir     none
P4X namespace on this branch absent -- it cannot be read, altered or relabelled
main                        untouched
binding checkpoint          none created
production run              none executed
tests                       207 passed, 1 skipped
                            (75 shard, 29 identity, 8 non-drift,
                             20 rule semantics, 76 frozen anchors)
pilot CPU                   1.1983 of the 2.0 CPU-hour cap; no STOP rule fired
```

`P4_ORIGINAL_VERDICT = PARTIAL` and `P4X_SUCCESSOR_VERDICT = FAIL` are
recorded here as immutable history and are not modified, re-adjudicated or
re-interpreted by this pilot.  `P4X_SCIENTIFIC_FAILURES = NONE`: the eight
`PRECONDITION_NOT_MET` cells were a governance gap, and this pilot repairs the
gap without touching a single scientific meaning.
