# P5X — G3 Consumer-Binding-Region Feasibility Audit

`PRE_FREEZE_THEOREM_CONSUMER_COVER_AUDIT`. **No binding checkpoint created, no
historical artifact changed, `|R| < 2` not weakened, no production run.**
`R8 SR full-cell prototype = FAIL` and `R8 F3 = 0.2` stand exactly as recorded.

```text
FINDING   Consumer-adaptive certification of  sup_e |R| < 2  over the whole
          frozen cover projects to ~55 CPU-hours -- COST_STRONG.
          That is 22.1x cheaper than the uniform grid-1024 projection (1216 h)
          and 354x cheaper than uniform grid-4096 (19457 h).
B1..B5    all PASS         READY_TO_FREEZE = YES (spec drafted, NOT created)
```

---

## 1. Authoritative cover and exact structure

`FROZEN_SCOPE.md` §3: the certified cover is **`[0, e_far]` with `e_far = 12`**,
oddness `P5-T3` supplies `e < 0`, and `P5X-T3` closes `[12, infinity)`.
Granularity is frozen as a *rule* (adaptive bisection, recorded in full), not a
number; the campaign cost formula uses `835` cells, adopted here as the model.

`P5-T3` (frozen, existing): **`R` odd, `S` even, `R(0) = 0`** — exact.
`Gamma_SR in [5.8003917995084423356, 28.781285803081492059]` (existing Arb
certificate), so `R'(0) = 1 - Gamma` and `|R'(0)| <= 27.781286`.

`FROZEN_THEOREM.md` already uses this pattern elsewhere: *"certified on
`[e_0, E]` by direct enclosure and on `(0, e_0]` by a certified `R' < 0`
together with the **exact** `R(0) = 0` of `P5-T3`."*

`P5X-T3` far field: `|R_SR(±10)| <= 4.2e-3`, decreasing.

## 2. Consumer metric

For a cell `E` with certified enclosure `[L_E, U_E]`:
`ABS_MAX(E) = max(|L_E|,|U_E|)`, `G3_MARGIN(E) = 2 - ABS_MAX(E)`, PASS iff
`G3_MARGIN > 0` strictly. Half-width is reported, not gated.

## 3. Numerical scan (DIAGNOSTIC ONLY)

`R_hat(e) = e + ghat(x_0)`, existing candidate solve; `C_SR(e)` from the R8
one-sided resolvent (the rigorous algorithm, run at each drift).

| `e` | `|R_hat|` | `2-|R|` | `C_SR` |
|---|---|---|---|---|
| 0 | `0.000000` | `2.000000` | `1505.821` |
| 0.025 | `0.396733` | `1.603267` | `1195.999` |
| 0.05 | `0.752569` | `1.247431` | `955.680` |
| 0.10 | `1.255480` | `0.744520` | `621.654` |
| 0.15 | `1.497210` | `0.502790` | `415.514` |
| 0.20 | `1.581192` | `0.418808` | `285.825` |
| **0.24** | **`1.591982`** | **`0.408018`** | — |
| 0.25 | `1.590342` | `0.409658` | `203.067` |
| 0.35 | `1.532418` | `0.467582` | `112.598` |
| 0.50 | `1.410617` | `0.589383` | `57.915` |
| 1 | `1.056488` | `0.943512` | `18.726` |
| 2 | `0.616008` | `1.383992` | `7.854` |
| 4 / 6 / 8 | `0.262` / `0.301` / `0.184` | — | — |
| 12 | `0.000000` | `2.000000` | — |

The secondary lobe at `e ~ 6` is visible, consistent with `FROZEN_SCOPE`.

## 4. The four binding locations do **not** coincide

| quantity | location | value |
|---|---|---|
| `|R|` maximum | `e = 0.24` | `1.591982` (margin `0.408018`) |
| `C_SR` maximum | `e = 0` | `1505.821` |
| half-width maximum | `e = 0` | `2.4072` at `delta = 1.5986e-3` |
| `G3` margin minimum (uniform certifier) | `e = 0` | `-0.4144` |
| **peak grid requirement** | **`e = 0.10`** | **`G = 1380`** |

The peak *grid* requirement sits at `e = 0.10`, at neither the `|R|` argmax nor
the `C_SR` maximum: it is where the product of a large `C_SR` and a small
remaining margin is worst. That is the load-bearing distinction this audit was
asked to find.

With a **uniform** grid-1024 certifier the crossover is near `e ~ 0.22`:
everything below fails, everything above passes.

## 5. Consumer-adaptive requirement

`delta_needed(e) = (2 - |R_hat(e)| - e_contrib)/C_SR(e)`, `G ~ 1024 x
1.5986e-3 / delta_needed`, `e_contrib = 6/835 = 0.00719`.

| `e` | allowed half-width | `delta` needed | grid | CPU-h/cell |
|---|---|---|---|---|
| 0 | `1.9928` | `1.3234e-03` | `1237` | `2.1250` |
| 0.025 | `1.5961` | `1.3345e-03` | `1227` | `2.0898` |
| 0.05 | `1.2402` | `1.2978e-03` | `1261` | `2.2098` |
| **0.10** | `0.7373` | `1.1861e-03` | **`1380`** | `2.6455` |
| 0.15 | `0.4956` | `1.1928e-03` | `1372` | `2.6161` |
| 0.20 | `0.4116` | `1.4401e-03` | `1137` | `1.7945` |
| 0.25 | `0.4025` | `1.9820e-03` | `826` | `0.9474` |
| 0.35 | `0.4604` | `4.0889e-03` | `400` | `0.2226` |
| 0.50 | `0.5822` | `1.0053e-02` | `163` | `0.0368` |
| 1 | `0.9363` | `5.0002e-02` | `33` | `0.0015` |
| 2 | `1.3768` | `1.7531e-01` | `9` | `0.0001` |

**The grid requirement collapses for `e >= 0.35`** — most of the cover is
essentially free, because `C_SR` falls fast while the margin grows.

## 6. Cost

| `e` range | cells | max grid | CPU-h | method |
|---|---|---|---|---|
| `[0, 0.0720]` | 5.0 | — | `0.00` | near-zero theorem (`R(0)=0` exact + certified `sup|R'|`) |
| `[0.0720, 0.35]` | 19.3 | `1380` | `51.18` | direct-residual certifier |
| `[0.35, 0.50]` | 10.4 | `400` | `2.32` | direct-residual certifier |
| `[0.50, 1.00]` | 34.8 | `163` | `1.28` | direct-residual certifier |
| `[1.00, 2.00]` | 69.6 | `33` | `0.10` | direct-residual certifier |
| `[2.00, 10.0]` | 556.7 | `9` | `0.07` | direct-residual certifier |
| `[10.0, 12.0]` | 139.2 | — | `0.00` | `P5X-T3` far-field majorant |
| **TOTAL** | | | **`54.95`** | **`COST_STRONG`** |

## 7. The near-zero theorem is an optimisation, not a dependency

`R(0) = 0` is exact, and `|R(e)| <= e sup|R'| < 2` covers `[0, 0.071991]` using
only the existing certified `Gamma_SR` upper bound (`|R'(0)| <= 27.781286`); a
certified `sup|R'|` on the interval would extend that to `~0.126`
(numerically `|R'(0)| ~ 15.87`).

**But it is not required.** Because `|R(0)| = 0`, the *allowed half-width at
`e = 0` is `1.9928`* — the direct certifier already succeeds there at grid
`1237`. Certifying the five near-zero cells directly costs `11.05` CPU-h, for a
total of **`66.0` CPU-h, still `COST_STRONG`**.

So the apparent `e = 0` failure in the previous audit was **entirely an artifact
of demanding a uniform half-width** rather than the consumer margin: multiplying
`C_SR(0) = 1505.821` by a `delta` sized for the `|R| = 1.59` region, when
`e = 0` tolerates a half-width of nearly `2`.

## 8. Pre-freeze conditions

| | condition | verdict |
|---|---|---|
| `B1` | load-bearing criterion is `|R| < 2` | **PASS** — `FROZEN_GATES.md` `G3`, re-read from `db0781e` |
| `B2` | every region has a rigorous route | **PASS, unconditional** — direct certifier suffices everywhere; near-zero theorem and `P5X-T3` are optimisations |
| `B3` | projected total `<= 500` CPU-h | **PASS** — `54.95` (or `66.0` without the near-zero theorem) |
| `B4` | no historical artifact changed | **PASS** |
| `B5` | no new candidate/approximation | **PASS** — existing candidate, existing certifiers, existing `C_SR` |

`READY_TO_FREEZE = YES`. Per §20 the successor specification is **drafted, not
created**.

## 9. Drafted successor specification — NOT created

```text
Cover        [0,12], adaptive bisection, oddness for e<0, P5X-T3 for [12,inf)
Criterion    for every accepted cell: certified R(E) subset (-2,2) STRICTLY
Safety       ABS_MAX <= 1.95  (diagnostic value from this audit; the frozen
             margin must be chosen BEFORE the run and justified there)
Regions      [0, 0.072]   near-zero: exact R(0)=0 (P5-T3) + certified sup|R'|
                          on the interval; fallback = direct certifier @1261
             [0.072, 0.35] direct-residual certifier, grid <= 1380
             [0.35, 1.0]   direct-residual certifier, grid <= 400
             [1.0, 10]     direct-residual certifier, grid <= 33
             [10, 12]      P5X-T3 far-field majorant
Certifier    R8/B2 Bernstein machinery with the direct-residual variant;
             R6 kernel unchanged; w^- boundary term as corrected in R8
Resolvent    R8 one-sided C_SR, computed per drift (3-25 s each)
Precision    192-bit baseline, 256-bit for the conversion, as in R8
Cost budget  <= 150 CPU-hours, <= 30 h wall on 6 cores
Correspondence  MC diagnostic per region; certified interval must contain it
Protected tree  P5, R4-R8 and all audits byte-identical by git object
```

**Why this is not post-result gate weakening.** The criterion `|R| < 2` is
`G3`'s own pass condition, written at Checkpoint A before any result existed and
re-read here from the commit. It retains teeth: R8's actual enclosure fails it
(`|R|max = 2.688`), and a uniform grid-1024 certifier fails it on all of
`e < 0.22`. Historical `R8` was adjudicated against `F3 = 0.2`, correctly
applied pre-result, and remains `FAIL`.

## 10. Caveats

* The `835`-cell uniform model is an approximation: the frozen cover is
  *adaptive*, so the true cell distribution will concentrate where `|R|` varies
  fastest — i.e. in the expensive `e < 0.35` band. The cost could rise if the
  adaptive cover puts many more than `~19` cells there. This is the single
  largest uncertainty in the `55` CPU-h figure.
* `delta` was taken as the direct-residual audit's measured `1.5986e-3` at grid
  `1024` for `e = 1/4`, and assumed to scale as `1/G` and to be `e`-independent.
  Neither was verified across `e`.
* `C_SR(e)` values are from the R8 one-sided algorithm; the cell-valid bound
  needs `B1-L6` (proved) or a per-cell computation.
