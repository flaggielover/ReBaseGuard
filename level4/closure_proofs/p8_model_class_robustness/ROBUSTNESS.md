# P8 robustness

The axes P8 was handed, one section each, with what was varied and what the
variation showed. Tables are printed by `experiments/make_tables.py` from
`results/*.json`; nothing is typed by hand.

Two axes are *not* here because P8 declined them, with reasons:

* **A third detector family** (`P8_DEFINITION_AUDIT.md` §6 `O1`). No closed
  derivative theorem exists for any detector outside `{CUSUM, SR}`, so a third
  family could only be reported as `EMPIRICAL_ONLY` with nothing behind it.
  The cost of that decision is attack `A14` in `ADVERSARIAL_REVIEW.md`, which
  P8 concedes rather than answers.
* **A family-optimal (score-based) chart.** P8 keeps the detector statistic
  frozen at its Gaussian design in every family and recalibrates only the
  threshold — Stage-D's convention and the operationally realistic one. A
  score-based chart for a heavy-tailed family is a *different detector*
  (`LIMITATIONS.md` `L4`).

---

## 1. Distribution family

Six frozen Stage-D families at one matched `ARL_0 = 465.50394`. Every family is
symmetric and unimodal; the `t` families are rescaled to unit variance, the
contaminated families are **not** (variance `1.4` and `1.8`, Stage-D's frozen
construction, `LIMITATIONS.md` `L5`).

**What survives.** `Gamma_A > 2` with a lower 95% bound above `2` in all 40
eligible `(D, f, m in {1,2,3,5})` cells, and in the 8 `t3` cells reported beside
them. The local instability is not a Gaussian artifact.

**What does not.** The *magnitude*. `rho_c(D,f,1)` spans a factor of `2.54`
across the twelve cells, and the direction of the error is not uniform: heavy
tails raise `rho_c` well above the Gaussian value in both detectors (a
Gaussian-derived limit is conservative there), while `10%` contamination
**lowers** it in both (a Gaussian-derived limit is optimistic there -- the
direction that matters). The intermediate cells move by a few percent in either
direction and their sign is not stable across the two detectors. `Gamma_A` is
not monotone in tail weight — the `t` families
fall below the Gaussian, the contaminated families rise above it.

**Where it breaks entirely.** At the extrapolated window `m = 20`, CUSUM with
`t3` innovations gives `Gamma_A = 1.949 +- 0.007`: regime
`GAMMA_BETWEEN_1_AND_2`, `rho_c = 1.054 > 1`, and every admissible reuse
fraction becomes locally attracting. One cell in 72, at a window P3 does not
support, not gated — and the only place in the whole matrix where the phenomenon
disappears.

## 2. Detector family

The two frozen detectors, ARL-matched per innovation family. `Gamma_A` itself
does **not** transfer: SR exceeds CUSUM in every family, by `9.1%`
(`gaussian`) to `38.1%` (`t3`). Gate `G9` therefore has no threshold — it
requires the ratios to be reported and requires no transfer claim beyond them.

What *is* nearly detector-invariant is the **window scaling** `K`: the largest
cross-detector residual over the 15 `(family, m in {2,3,5})` comparisons is
`3.63%`, against a cross-distribution spread of `22%`–`49%` — a separation of
about `13x`. It still misses the pre-declared `3%` sub-gate `G4-D` in one
comparison, and it means *these two closely related two-chart likelihood-ratio
schemes*, not "detectors" (`ADVERSARIAL_REVIEW.md` `A14`).

The lag profile itself is **less** detector-invariant than `K` is: post-hoc
`H2a` required `5%` at every lag `r <= 5` and was rejected at `19.66%`, the
failures concentrated on the heavy-tailed families. Averaging over the window
cancels most of the detector difference; P8 records this without explaining it.

## 3. Window `m` and the window convention

`m in {1,2,3,5}` are P3-supported; `m in {10,20}` are reported and labelled
`EXTRAPOLATION_BEYOND_P3` in every row of every artifact, and are never gated.

Convention A (`denominator min(m,tau)`) versus convention B (`denominator m`):
gate `G6` confirms that `Gamma_A - Gamma_B` equals the exact truncation
remainder `R_m` of `P8-L1(b)` to machine precision in all 72 cells, so the
convention difference is fully explained rather than merely measured. `P(tau<m)`
is reported per cell.

**Convention B is reported and never merged with A.** `p5/LIMITATIONS.md` §1
records that P5's `T1` — and with it essentially every P5 theorem — *fails* for
a fixed-`m` denominator, so no P5 theorem is attached to any convention-B
number anywhere in P8.

## 4. Reuse fraction `rho`

P7's ladder verbatim: `{0.25,0.5,0.8,1.0,1.25,1.5,2,4} x rho_c` plus the
absolute anchors `{0,0.25,0.5,0.75,1}`, clipped to `[0,1]`. In cells whose
`rho_c` is large enough that `4 rho_c` leaves the admissible domain, gate `G7`
applies P7's criterion to the rungs that exist, with both boundary brackets
required and at least five rungs — a **declared adaptation**, recorded in
`results/closure_decision.json` with the rungs used per sub-family.

## 5. Canonical initialisation

Every chain starts at `e_0 = 0`, the canonical convention, with a burn-in of 20
cycles and metrics on the following 50. The finite-reference regime
`e_0 ~ (0, 1/m_0)` was **not** run: it is P6 territory (`p6/LIMITATIONS.md`
`L4`), the `init` primitive stream exists and is addressable but is unused, and
`LIMITATIONS.md` `L1` records the gap.

## 6. Seed sensitivity

`E5` repeats the whole `E1` matrix at a different experiment tag
(`p8_gamma_E5`) **and** a disjoint batch range (100–119), so both address
components differ and the two primitive fields are independent rather than
offset. Gate `G10` requires `|z| <= 3` in `>= 90%` of the 72 cells and `>= 95%`
of the 60 non-`t3` cells: measured `95.8%` and exactly `95.0%`. **PASS, at the
threshold.**

All three failures are the same cell — SR / `gaussian` — offset by `+0.30%` to
`+0.51%` at every window, i.e. one discrepancy at `z ~ 3`–`4`. The matrix-wide
`z` distribution has sd `1.26`, so the batch-means SE mildly understates
cell-to-cell variability at the highest-precision cells. Unexplained, recorded,
and immaterial to conclusions two orders of magnitude larger
(`STATISTICAL_AUDIT.md` §7.7).

## 7. Grid-resolution sensitivity

The `m` grid enters only through `K`, and `K`'s normaliser `m = 1` is a
definition rather than a selection. The mechanism behind `K` — the lag profile
`gamma_r` — is measured at every `r < 20` **without reference to any `m` grid**,
so the `G4` result is a consequence of a grid-free measurement. The spread
*grows* with `m`, so a coarser grid would understate the rejection, not
manufacture it.

## 8. Null monitoring, changed regimes and drift patterns

In control (`Delta = 0`), step shifts `Delta in {0.5, 1, 2}` and linear ramps at
`0.02` and `0.05` per cycle, each applied at a re-baselining instant, at
`rho in {0, 1}` and `m in {1, 5}`, both detectors, all six families: 288 rows,
all present. Delay is reported as mean, `q50`, `q95` and `P(delay > 100)`, with
an explicit `INSUFFICIENT_TAIL_EVENTS` label below 200 tail events (gate `G11`
PASS). 27 rows carry that label and **every one of them is at `Delta = 2`** —
the same under-powered regime `p6/LIMITATIONS.md` `S8` records for P6's own
campaign at a comparable budget.

**Step and ramp disagree about what reuse does.** For a step, reuse destroys
discrimination: `R_Delta` rises from `0.34`–`0.69` at `rho = 0` to `0.52`–`1.06`
at `rho = 1`, against a nominal `0.022`. For a ramp, `R_Delta` is `0.92`–`1.05`
at **both** reuse fractions — the ramp is already invisible without any reuse,
because at `rho = 0` the reference-error recursion pins `e` near `-slope`
forever. The ramp result is confined to the first post-change cycle
(`LIMITATIONS.md` `S5b`): `E4` runs only 4 post-change cycles, which cannot
measure ramp accumulation at `rho > 0`.
