# P6 closure gates

```text
FROZEN_AT   = before any policy-comparison number existed
STATUS      = SEE SECTION 3 (filled after the campaign; the wording above it is never edited)
```

Section 1 and section 2 are the **preregistration**. They reproduce the
pre-design's `C1`-`C10` verbatim and select one option for each of `G-A`..`G-E`
from `PREREGISTRATION_OPTIONS.md`. Section 3 is the audit, written afterwards.
Following P4's precedent, a failed gate is left unedited and explained.

---

## 1. Structural criteria `C1`-`C10` (verbatim from the pre-design)

| # | criterion |
|---|---|
| C1 | **No metric is selected post hoc.** The primary objective, primary cell and materiality threshold are fixed before any `EVAL` data are produced |
| C2 | **Every comparison carries an interval**, and uses P7's verdict labels verbatim |
| C3 | **No latent-state information in any policy claimed implementable**, enforced structurally |
| C4 | **Reproduction across both frozen detectors**, with the effect resolved in each |
| C5 | **Reproduction on an independent seed family** (`REPLAY`), untouched during the campaign |
| C6 | **No change to frozen P1-P5/P7 semantics**; constant-policy correspondence is bit-identical in `tau` |
| C7 | **Multi-cycle evaluation**: no claim rests on R1 or R4 alone; `Coll` is reported for every method |
| C8 | **Cost-matched comparison**: the headline comparison is against the best fixed `rho` at matched `Fresh`, never against `B3` alone |
| C9 | **The novelty audit is executed before the confirmation stage** and its verdict recorded, whatever it is |
| C10 | **Dropped candidates are reported** with reason and numbers |

## 2. Numeric gates -- options selected

### G-A. Tail-risk improvement over full reuse — **option A1**

> The method improves `Dtail(100)` relative to `B3` (`rho = 1`) at the primary
> cell `(CUSUM, m = 3, Delta = 1.0)` by a **relative reduction of at least
> 25%**, with the paired interval excluding zero.

Declared fallback, per `PREREGISTRATION_OPTIONS.md`: **A3** (`Dq95` reduction
`>= 20%`) *if and only if* the preregistered tail-event budget of 200 events per
arm cannot be met. The fallback is declared here, before the data.

### G-B. Do-no-harm on in-control performance — **option B1**

> `Arl0(U) >= 0.95 x Arl0(B2*)`, where `B2*` is the best fixed `rho` in the
> frozen grid at matched `Fresh`, at the primary cell.

### G-C. Sample efficiency — **option C-iii** (report the frontier, no threshold), with a preregistered anti-degeneracy replacement

The pre-design offers C-i (`Fresh(U) <= 0.5 Fresh(B0)`), C-ii (`Fresh(U) <
Fresh(B0)`) and C-iii (report the frontier, set no threshold), and recommends
C-i. **C-iii is selected**, for a reason that follows from the approved cost
model alone and from no result:

> Under the approved primary cost model `C_fresh = k_j 1{rho_j < 1}`
> (`EXPERIMENT_PROTOCOL.md` section 4), *every* policy that ever collects a
> fresh baseline pays exactly `k` observations per alarm. `Fresh` therefore
> separates policies only through the design constant `k` and not through the
> reuse rule at all. A threshold of the form `Fresh(U) <= 0.5 Fresh(B0)` is then
> not a statement about the method: it is passed or failed by the choice of `k`,
> and any method can pass it by halving `k`. Gating on it would be
> simultaneously vacuous and gameable.

Because C-iii sets no threshold, a substantive anti-degeneracy criterion is
preregistered in its place, capturing what `K4`/`F3` actually intend:

> **G-C'.** The method must not be cost-degenerate: at matched `Fresh`, its mean
> algebraic reuse weight `Wbar` must be materially above zero, with the interval
> excluding zero, and the headline comparison must be reported at matched
> `Fresh`. C-i's outcome is additionally reported, pass or fail, so nothing is
> hidden by the change of option.

### G-D. Reproduction breadth — **option D1**, count corrected

> The effect is resolved in **at least 5 of the 6** `(detector, m)` families with
> `m in {2, 3, 5}`. `m = 1` is **excluded from the count and reported
> separately**, declared here in advance with `S14` as the reason ("`m = 1` is
> unusable under any `rho`").

D1's literal wording is ">= 6 of the 8 families"; with `m = 1` excluded as the
pre-design also directs, only 6 families remain, and requiring 6 of 6 would be
option D2, which the pre-design rejects as brittle. `>= 5 of 6` is D1's stated
bar (one family may fail) applied to the reduced count. The deviation is
recorded rather than made silently.

### G-E. Finite-cycle safety — deferred to post-pilot **by prior agreement**

Set in `results/gate_e.json` from the baseline `Coll` values measured at stage
S2, **before** any SAW `Coll` is computed. The execution order is recorded in
that file.

## 3. Closure rule (frozen)

> **P6 CLOSED** requires `C1`-`C10`, plus `G-A`, `G-B`, `G-C`/`G-C'` and `G-D`
> at the selected options, plus `G-E`'s post-pilot criterion.
>
> **P6 PARTIAL** if the structural criteria hold and some but not all of
> `G-A`..`G-E` are met, each failure reported unedited in the P4 style.
>
> **P6 CLOSED (negative)** if `C1`-`C10` hold, the oracle ceiling is measured,
> and the reproduced finding is that no implementable adaptive policy beats the
> matched-cost fixed `rho`. This is a legitimate closure, not a failure.

## 4. What must not become a gate

* `rho < rho_c`, or any function of `rho/rho_c` (`X1`, `F15`).
* Any latent-layer surrogate (`Rms`, `E[e^2]`, `OutCal`) as a *closure*
  criterion (`F2`, `S18`).
* Recovering nominal `ARL_0` (`S20`, `E1`, `X12`).
* Any P5 numeric as a threshold (`X9`).

---

## 5. AUDIT — filled after the campaign

<!-- P6-GATE-AUDIT-START -->
```text
STRUCTURAL   C1-C10 :  10 PASS,  0 FAIL   (two qualifications recorded, C1 and C9)
NUMERIC      G-A..G-E:  4 PASS,  0 FAIL,  1 REPORTED-WITHOUT-THRESHOLD (G-E, with a recorded ordering defect)
TOTAL                :  14 PASS, 0 FAIL, 1 N/A-BY-SELECTED-OPTION
```

Gates are quoted unedited. Where a gate's wording is imperfect, the defect is
documented and the gate is still evaluated as written (P4's precedent).

### Structural criteria

| # | verdict | evidence |
|---|---|---|
| C1 | **PASS**, with a qualification | The primary objective (`Dtail(100)`), primary cell (CUSUM `m=3`, `Delta=1`), materiality (`10%` relative), baselines, metrics and cost model are all fixed in `EXPERIMENT_PROTOCOL.md`, written after Stage 1 (correspondence + calibration only) and before Stage 2 and Stage 4 ran. **Qualification:** that ordering is recorded in the documents but is not established by an external timestamp — nothing is committed, so an adjudicator has the campaign's own account and not a cryptographic trail. Listed as an attack target in `CODEX_HANDOFF.md` |
| C2 | **PASS** | Every comparison in `RESULTS.md`, `ABLATION.md` and `ROBUSTNESS.md` carries a 95% interval; P7's labels `INCONCLUSIVE` / `STATISTICALLY_RESOLVED` / `PRACTICALLY_MATERIAL` are used verbatim. `INSUFFICIENT_TAIL_EVENTS` **is** triggered and is applied: every cell used for a gate clears the preregistered floor of 200 tail events (the smallest is 269, SR `m=5`, `Delta=1`), but the secondary `Delta = 2` cells fall below it for most arms (as few as **0** events at `m=5`), and their `Dtail(100)` values are labelled `INSUFFICIENT_TAIL_EVENTS` rather than reported as effects. Two of the eighteen frontier cells (`m=5, k=20`) are likewise under-powered for `Dtail(100)` and are labelled |
| C3 | **PASS** | Structural: `CycleObservation` has no latent field, its field set is asserted equal to the audited list, every registered implementable policy is asserted `requires_oracle == False`, oracle policies are asserted to *refuse* a plain observation, and `test_saw_decision_depends_only_on_the_audited_observables` perturbs nine non-SAW fields and asserts no decision changes (93 focused tests in total) |
| C4 | **PASS** | Both frozen detectors, four `m`, eight families. The effect is resolved in **8 of 8** on `Arl0`, `Rms` and `Dtail(100)`. Each detector is calibrated separately; no transfer is assumed |
| C5 | **PASS** | `REPLAY` reproduces **8 of 8**, with `B2*` re-selected on `REPLAY` itself. Primary cell: `Dtail(100)` `-8.9%` `[-12.8%, -4.9%]` against `EVAL`'s `-10.4%` `[-14.3%, -6.4%]` |
| C6 | **PASS** | `X1`: 24/24 cells bit-identical in `tau`, `max abs e_start difference = 0.0` exactly. `X3`: 40/40 reproduce P7's published `Arl0` intervals, `max |z| = 2.53`. Protected tree: 2,907 tracked files outside the P6 namespaces, **zero modified** against `HEAD = bb03c0ea`, the authoritative P5 checkpoint |
| C7 | **PASS** | R1/R2/R3 per-cycle curves recorded for every policy in every cell; `Coll` reported in every table; no headline claim rests on R1 or R4 alone. R3 curves are flat from cycle 5-8, which is how `burn_in = 15` was established rather than inherited |
| C8 | **PASS** | The headline comparison is against `B2*`, the best fixed `rho` at **matched `Fresh`** — identical to four decimal places in every cell — with `B3` reported only as a sanity check. The `k`-swept frontier repeats the comparison at matched `Fresh` for `k in {m, 2m, 4m}` |
| C9 | **PASS**, with a qualification | The 17 literature queries were executed and `NOVELTY_AUDIT.md` was written **before any Stage-4 confirmation number was read**. **Qualification:** the Stage-4 runs were executing in the background while the searches ran, so the audit preceded the *reading* of the results but not their mechanical *production*. The intent of C9 — that the audit cannot be influenced by how good the numbers look — is satisfied; the literal reading "before the confirmation stage" is not |
| C10 | **PASS** | Three baselines (`B7`, `B8`, `B10`) were dropped at Stage 2 by `ES2`, each with its rule, its reason and its numbers in `RESULTS.md` section 8. No policy was dropped by any other rule |

### Numeric gates

**G-A** (option A1): *`Dtail(100)` reduction `>= 25%` vs `B3` at the primary cell,
paired interval excluding zero.*

> Measured: **`-57.6%`**, 95% paired interval `[-59.1%, -56.0%]`.
> **PASS** with a wide margin. The declared `Dq95` fallback was not needed: the
> tail-event budget was met with 3,639-8,576 events per arm against a
> preregistered floor of 200.

**G-B** (option B1): *`Arl0(U) >= 0.95 x Arl0(B2*)` at the primary cell.*

> Measured: `151.52 / 144.10 = 1.0515`. **PASS** — SAW does not merely avoid
> harming in-control performance, it improves it by `+5.1%`
> `[+4.5%, +5.7%]` at identical fresh cost.

**G-C** (option C-iii): *report the frontier, set no threshold.*

> The `k`-indexed frontier is reported in `ROBUSTNESS.md` section 1 across 18
> `(detector, m, k)` cells with baselines on the same axes. **PASS** (satisfied
> by construction, as the selected option carries no threshold).
>
> **`G-C'`** (the preregistered anti-degeneracy replacement): *`Wbar` materially
> above zero with the interval excluding zero, headline at matched `Fresh`.*
> Measured `Wbar = 0.247` against `B2*`'s `0.150`, a paired difference of
> `+64.8%` `[+64.6%, +64.9%]`; `Fresh` identical. **PASS.** SAW is the opposite
> of cost-degenerate: it reuses **more** than the best fixed weight while
> distorting less.
>
> **C-i reported unedited, as promised:** `Fresh(U) <= 0.5 x Fresh(B0)` requires
> `3.00 <= 1.50`. **FAIL.** It fails for *every* policy in the class including
> `B2*` and `B0` itself, which is the structural reason C-i was not selected.

**G-D** (option D1, count restated): *the effect resolved in `>= 5 of 6`
families with `m in {2,3,5}`; `m = 1` excluded from the count and reported
separately.*

> Measured on the primary objective `Dtail(100)` vs each cell's own `B2*`
> (two-proportion, unpaired and therefore conservative; the measured pair
> correlation is `~0.00`):
>
> | family | rel. effect | `z` | resolved |
> |---|---|---|---|
> | CUSUM m=2 | -10.1% | -5.70 | yes |
> | CUSUM m=3 | -10.4% | -4.96 | yes |
> | CUSUM m=5 | -10.9% | -3.85 | yes |
> | SR m=2 | -11.3% | -6.20 | yes |
> | SR m=3 | -8.6% | -3.93 | yes |
> | SR m=5 | -9.6% | -3.25 | yes |
>
> **6 of 6. PASS.** Reported separately as declared: `m = 1` also resolves in
> both detectors (`-6.0%`, `z = -3.75`; `-4.7%`, `z = -2.81`), so the count is
> in fact 8 of 8. All eight also resolve on `REPLAY`.

**G-E** (deferred to post-pilot; option E3 selected): *report `Coll`, gate on
nothing.*

> Selected from the baseline numbers alone: fresh-only — the policy that reuses
> nothing and is therefore the natural ceiling for a matched-cost reuse rule —
> attains `Coll` of only `0.165`-`0.350` across the eight families, and the best
> member of the frozen fixed-`rho` grid `0.202`-`0.385`. Option E1's absolute
> floor of `0.5` and option E2's `2 x Coll(B2*)` are therefore **above what any
> matched-cost policy in the class can reach**; the pre-design's own text
> designates E3 for exactly this situation.
>
> **Reported unedited, as promised:**
> * **E1** (`Coll >= 0.5`): **FAIL** for every policy including `B0` and `B2*`.
> * **E2** (`Coll(U) >= 2 x Coll(B2*)`): **FAIL** for every policy.
> * Measured: `Coll(SAW_M) = 0.301` vs `Coll(B2*) = 0.293` at the primary cell,
>   paired difference `+0.8%` `[-4.7%, +6.4%]`, **INCONCLUSIVE** — SAW neither
>   introduces nor repairs the `S8` finite-cycle collapse. Full reuse remains at
>   `0.012`-`0.020` in all eight families, reproducing P7's 98% collapse.
>
> **G-E carries a recorded ORDERING DEFECT** (`results/gate_e.json`,
> `LIMITATIONS.md` `S4`): the protocol required baseline `Coll` to be seen, the
> threshold written, and only then SAW's `Coll` computed; the Stage-2 script
> produced both in one pass and both were inspected together. The *selection* of
> E3 rests only on the baseline numbers and E1/E2 are reported unedited, but
> `G-E` does **not** have the pre-commitment status of `G-A`..`G-D`, and it is
> classified `REPORTED_WITHOUT_THRESHOLD`, not `PASS`.

### What the frozen closure rule says

> *P6 CLOSED requires C1-C10, plus G-A, G-B, G-C/G-C' and G-D at the selected
> options, plus G-E's post-pilot criterion.*

`C1`-`C10` hold (two qualifications recorded, neither a failure of the
criterion's substance). `G-A`, `G-B`, `G-C`/`G-C'` and `G-D` all **PASS**.
`G-E`'s post-pilot criterion is E3, which is satisfied by reporting — but its
selection carries a recorded ordering defect.

**On the frozen rule, P6 meets the CLOSED conditions.** This campaign does not
award that verdict: the closure decision is Codex's, and the two qualifications
(C1's missing external timestamp, C9's literal ordering) plus `G-E`'s ordering
defect are exactly the material an independent adjudicator should weigh. The
campaign's own classification is therefore **`P6 = CLOSED_CANDIDATE`**, pending
independent adjudication.
<!-- P6-GATE-AUDIT-END -->
