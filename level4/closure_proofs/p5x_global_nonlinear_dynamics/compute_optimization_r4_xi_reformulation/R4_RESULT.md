# P5X R4 — result: the xi reformulation ELIMINATES the z-panel bottleneck

```text
PRIMARY QUESTION   answered YES
GATE (as frozen)   FAIL     failed criteria: P2, P3
DECISIVE CRITERION P4  PASS by 830x
t_patch            0.3990 ms          budget 331.45 ms
z-panels           0                  R3 had 128
softplus approx.   0                  R3 had 256 per patch
Phi evaluations    66                 exactly 2(2n+1), n = 16
PROJECTED_SR       9.63 CPU-hours     R3: 12,083.77  ->  speedup 1254.8x
PROJECTED_TOTAL    155.63 CPU-hours   ->  R4_BREAKTHROUGH / STRONGLY_VIABLE
```

Anchor: Checkpoint F `209a6fd9a5ca2824688062ac855a7abcefae9697`, committed and
pushed before this gate was implemented.

---

## 1. The answer

**Yes.** The exact frozen SR certification problem can be reformulated in
`xi = exp(y)` — in production, `zeta = (xi-1)/A` — so that the Gaussian
innovation integral is *fully closed form*. The `z`-panel dimension is not
reduced; it is **removed**, exactly. The scientific target, recurrence
semantics, alarm event, stopping convention, theorem interface and certified
enclosure meaning are all preserved, proved in `L-R4.1` .. `L-R4.10`.

The mechanism, in one line: under `zeta' = (1/A + zeta)E^{+/-}`, a bidegree-`(n,n)`
polynomial candidate composes into a finite sum of *pure exponentials*
`e^{kz}`, `k = i-j in [-n, n]`, and each such integral against `phi(z+e)` over
the live region is `e^{k^2/2-ke}[Phi(u+e-k) - Phi(l+e-k)]`. R3 needed `128`
panels per state patch because `softplus` had to be Taylor-approximated in `z`;
in `zeta` there is no `softplus` left to approximate.

## 2. The gate FAILS as frozen, and I am not re-budgeting it

| criterion | verdict | what it means |
|---|---|---|
| `P1` recurrence exactness | **PASS** | `1 + xi e^{z-1/2}` and `exp(softplus(v))` agree as balls at all three frozen points |
| `P2` closed-form correctness | **FAIL** | the criterion is ill-typed (`D11`); see §3 |
| `P3` conditioning at `n = 16` | **FAIL** | amplification `2.14e17` vs the frozen `1e12`; real, see §4 |
| `P4` panel elimination | **PASS** | `0.3990 ms` vs `331.45 ms`, `830x` under budget |
| `P5` zero-panel structure | **PASS** | instrumented counters: `0` panels, `0` softplus expansions, exactly `66` `Phi` |
| `P6` exact rational drift | **PASS** | `e = 1/4`, ball radius exactly `0` |
| `P7` atom neutrality | **PASS** | `zeta' > 0` strictly; alarm agrees with `y`-space on both sides of the boundary |
| `P8` no empirical monotonicity | **PASS** | only `exp`/`log` monotonicity is used |

`GATE = FAIL`. Two of eight criteria failed and the frozen conjunction is the
binding verdict. The frozen thresholds, the `P4` budget and the classes are
exactly as committed at Checkpoint F.

## 3. Why `P2` failed, and why it does not mean the method is wrong

`P2` as frozen required the closed-form **ball to CONTAIN** a composite-Simpson
reference. That is unsatisfiable by any correct implementation: the closed
form's relative radius is `~3.5e-57`, while Simpson at `40000` points carries a
truncation error of `~2.6e-21` that its ball arithmetic does not account for.
A correct method is *guaranteed* to fail. Registered as **`D11`**, frozen bytes
unedited.

The gate's own diagnostic then compounded it: `rel_gap` and the Richardson
widening were computed through `float()`, which truncates at `~1e-16` and
destroyed both quantities — they printed as `0.0`. That is why even
`pass_corrected` failed in `results/r4_gate.json`.

Redone entirely in Arb (`results/r4_diagnostics.json`, **disclosed as post-hoc**):

| point | `|cf - ref| / |ref|` | reference's own Richardson truncation | ratio |
|---|---|---|---|
| patch centre | `2.59574e-21` | `2.59573e-21` | `1.0000` |
| corner `(lo,lo)` | `2.13193e-21` | `2.13193e-21` | `1.0000` |
| corner `(lo,hi)` | `2.51113e-21` | `2.51113e-21` | `1.0000` |
| corner `(hi,lo)` | `2.78330e-21` | `2.78330e-21` | `1.0000` |
| corner `(hi,hi)` | `3.12146e-21` | `3.12146e-21` | `1.0000` |

Worst ratio `1.0000005`. **The entire disagreement is the reference's own error.**
Independently, the closed form was checked against a brute-force simulation of
the frozen `y`-space recurrence (not the `zeta` algebra) on five random
candidates: agreement to the printed precision on every one.

## 4. Why `P3` failed — a real finding, not an artifact

Amplification `2.14e17` against the frozen `1e12`. This is risk (ii) from the
Checkpoint-F prediction, named in advance: `e^{k^2/2}` reaches `~4e55` at
`k = 16` and multiplies a `Phi`-difference of order `e^{-k^2/2}`.

The precision sweep settles what kind of failure it is:

| bits | amplification | passes `1e12`? | `t_patch` | projected SR |
|---|---|---|---|---|
| 192 | `2.14e17` | no | `0.54 ms` | `13.0` CPU-h |
| 256 | `2.62e17` | no | `0.65 ms` | `15.6` CPU-h |
| 320 | `2.13e17` | no | `0.79 ms` | `19.0` CPU-h |
| 384 | `5.14e17` | no | `0.91 ms` | `22.1` CPU-h |
| 448 | `4.65e17` | no | `1.05 ms` | `25.4` CPU-h |
| 512 | `5.14e17` | no | `1.17 ms` | `28.2` CPU-h |

**Flat.** The amplification is a *fixed condition number* of about `2^58`, not a
precision defect that worsens. So the method loses a constant ~58 bits and
recovers accuracy linearly in the working precision, at about `+20%` time per
`64` bits — and even at `512` bits the projection is `28` CPU-hours, still three
orders below R3.

That is a real and useful negative finding: **R4's kernel is correct and fast but
badly conditioned at high candidate degree**, and a production certifier must
budget ~58 bits of headroom, or restructure the `e^{k^2/2} x Phi`-difference
product (for instance through a scaled complementary error function) to avoid
forming a huge prefactor against a tiny difference. That restructuring is *not*
attempted here; it is an R5 question.

A first-pass caveat: this sweep was run at one state patch and one drift. It
establishes the *shape* of the dependence, not a uniform bound.

## 5. Cost model, before and after

```text
R3:  SR = 835 * 1210 * 128 * 0.003911 * 2 * 43 / 3600 = 12,083.77 CPU-hours
R4:  SR = 835 * 1210 *       0.000399 * 2 * 43 / 3600 =      9.63 CPU-hours
                             ^ t_patch, no panel factor at all

CUSUM (R2, unchanged)                                 =    146.00 CPU-hours
TOTAL                                                 =    155.63 CPU-hours
```

Speedup vs R3 on the SR lane: **`1254.8x`**. The campaign bottleneck moves from
SR (`98.8%` of cost under R3) to **CUSUM** (`93.8%` of cost under R4).

## 6. Scientific classification

`CERTIFIED_COORDINATE_CHANGE` + `CERTIFIED_KERNEL_REFACTOR`, with
`XI_SECOND_MOMENT_EXTENSION = DIRECT_WITH_SPECIAL_FUNCTIONS`
(the `z`- and `z^2`-weighted kernels follow by differentiating the same closed
form in `k`, staying closed form).

Not a `SCIENTIFIC_METHOD_CHANGE` and not a `SCIENTIFIC_SCOPE_CHANGE`: the frozen
`A`, the `D1`-corrected domain, convention A, the stopping rule, `m in {1,2,3,5}`,
the `[0,12]` drift range and the `0.2` stop-gate threshold are all untouched, and
no theorem consumer interface changes.

## 7. Defects found in R4

* **`D10`** — the §7/§14 shorthand wrote the minus chart as `1/E`. The frozen
  recurrence gives `E^- = e^{-z-1/2}`, and `E^+ E^- = e^{-1}`, so the charts are
  **not** reciprocal. Every minus-chart term of degree `j` was inflated by `e^j`
  (measured error `5.3e-3` .. `2.9e-1`). Correction: `(E^+)^i (E^-)^j =
  e^{(i-j)z} e^{-(i+j)/2}`; the `z`-exponent and therefore the whole zero-panel
  structure are unchanged. Explicitly **not** a `D8`/`D9` repeat — the
  anchor-phase standing rule was followed in R4.
* **`D11`** — the frozen `P2` criterion is unsatisfiable by a correct method
  (§3), compounded by a `float()` truncation in the gate's own diagnostic.

Both were found by the pre-gate independent equivalence check — the same
discipline that caught the R2 `C2` substitution-order bug — not by reading the
algebra. Frozen bytes were not edited for either; errata carry the corrections.

## 8. Prediction scorecard (recorded at Checkpoint F, before running)

| quantity | predicted | measured | verdict |
|---|---|---|---|
| `P1` | PASS | PASS | **hit** |
| `P2` | PASS, rel half-width `1e-16`..`1e-14` | FAIL (frozen); half-width `3.7e-57` | **miss**, both parts |
| `P3` | PASS with margin | FAIL, `2.1e17` vs `1e12` | **miss** |
| `t_patch` | `1.0`..`4.0 ms` | `0.399 ms` | **miss** (better) |
| `P4` | PASS by ~2 orders | PASS by `2.9` orders | **hit** |
| projected SR | `25`..`100` CPU-h | `9.63` | **miss** (better) |
| campaign total | `170`..`250` CPU-h | `155.6` | **miss** (better) |
| gate | PASS | **FAIL** | **miss** |

**2 of 8.** Of the three risks I named in advance, (i) `Phi`-difference
cancellation and (ii) `e^{k^2/2}` overflow both bit — they are the same risk and
they are what failed `P3`. Risk (iii), slow `erf`, did not: `66` `Phi`
evaluations cost `0.4 ms`. I was systematically pessimistic about speed and
systematically optimistic about conditioning and about my own criteria.

## 9. What R4 does and does not establish

**Established.** The `zeta` reformulation is exact (`L-R4.1`..`L-R4.10`); it
introduces and destroys no atom; the kernel is closed form with `2(2n+1)` `Phi`
evaluations and zero panels; measured `t_patch` is `0.399 ms`, `830x` inside the
frozen budget; the SR lane projects to `9.63` CPU-hours.

**Not established.** The frozen gate did not pass. `P3` conditioning fails at
`n = 16` and is unresolved. The measurement is one patch, one drift, first
moment only — no full-cell prototype was run, because §22 of the brief is
conditional on the gate passing and it did not. The second-moment kernels are
proved closed form but not implemented or timed. Nothing here licenses a
production launch, and no full cover was attempted.

**Recommended next step (R5, not started).** Restructure the
`e^{k^2/2-ke} x [Phi(u+e-k) - Phi(l+e-k)]` product to avoid forming a `4e55`
prefactor against a `1e-55` difference — the standard remedy is a scaled
complementary error function, which would attack the `2^58` condition number
directly. If that lands, `P3` passes at production degree and the SR lane is
closed at single-digit CPU-hours.
