# ReBaseGuard Level 4 — Gate 4.1 Report

## Multi-Cycle Experimental Oracle

**Decision: `PASS-4.1`**

> **Proof role.** Everything in this report is Monte Carlo simulation.
> Nothing here is a proof, and nothing here modifies, reinterprets or
> supersedes any frozen Level 1–3 artifact. The frozen model is treated
> as immutable ground truth and is only ever *checked against*.

---

## 1. Exact experiment design

### 1.1 The simulated object

One **cycle** is: monitor with reference error `E_j` → stop at the frozen
alarm rule → form a re-baselining statistic from the stopping-selected
data → obtain `E_{j+1}`. The detector state is fully reset at every cycle
boundary. The detector recursion itself is literally the frozen one:

```text
X_t   ~ iid N(0,1)                      physical observation
Z_t    = X_t - E_j                      residual against the reference
S+_t   = max(0, S+_{t-1} + Z_t - k)     k = 1/2   (frozen)
S-_t   = max(0, S-_{t-1} - Z_t - k)     shared innovation Z_t
tau_j  = inf{ t >= max(1,m) : max(S+_t, S-_t) >= h }      h = 5 (frozen)
mu_reuse = (1/m) sum_{r=0}^{m-1} X_{tau-r}   (alarm observation included)
mu_fresh = (1/m) sum_{r=1}^{m} Y_r,  Y iid N(0,1), independent of the cycle
E_{j+1}  = rho * mu_reuse + (1-rho) * mu_fresh
```

`rho = 0` is the **fresh** policy (the matched-information control),
`rho = 1` is **full reuse**, and intermediate `rho` is **fixed partial
reuse**. All three are the same expression, so no separate code path can
drift between them.

### 1.2 Grid and sample size

| Campaign | stage | `m` | `rho` | replicates | retained cycles/replicate | burn-in |
|---|---|---|---|---|---|---|
| `gate4.1-full-0ef53096975d` | full | 1 | 0, 0.02, 0.05, 0.1, 0.25, 0.5, 1 | 100 | 10,000 | 1,000 |
| `gate4.1-full-mgrid-0b107713d71e` | full-mgrid | 5, 10, 20, 50 | 0, 0.05, 0.1, 0.25, 0.5, 1 | 100 | 2,000 | 500 |

Total simulated cycles across the campaigns in this report: **13,700,000**.

The full Cartesian product was **not** run at maximum sample size. The
`m = 1` sweep is run at full resolution because it is the only
configuration for which Level 1–3 supplies a certified counterpart; the
`m > 1` sweep is exploratory and is run at one fifth the cycle count.
Sizing came from the pilot stage, whose measured cost per lockstep
iteration is recorded in every cell manifest
(`seconds_per_lockstep_iteration`).

### 1.3 Statistical unit

**The replicate is the statistical unit.** Cycles within a replicate are
a serially dependent Markov chain — and the hypothesis under test is
precisely that they are *strongly* dependent — so treating cycles as
independent observations would deflate every standard error in the
direction that flatters the hypothesis. Each metric is therefore reduced
to one number per replicate first; the point estimate is the mean over
replicates; and every interval is a 95% nonparametric percentile
bootstrap **resampling replicates**, never cycles. Replicate-to-replicate
standard deviation is reported next to every interval.

---

## 2. Reproducibility

| Field | Value |
|---|---|
| git commit | `9077c9b66e837f9f687d6dc117306da3f4417efb` |
| working tree | **dirty** |
| branch | `main` |
| Python | 3.14.5 |
| NumPy / SciPy | 2.5.2 / 1.18.0 |
| pyarrow / matplotlib | 25.0.1 / 3.11.1 |
| platform | macOS-26.5.2-arm64-arm-64bit-Mach-O |
| package code digest | `a4eb397772147ad4…` |
| master seed | `20260820` |

Every cell writes its own manifest carrying the experiment id, UTC
timestamp, git state, dependency versions, per-file source hashes, the
full configuration, and the seed rule for every random stream.

**Seed rule.** Replicate `r` draws its physical observations from
`SeedSequence([master_seed, 0, r])` and its fresh statistics from
`SeedSequence([master_seed, 1, r])`, each feeding its own `PCG64`. The
chains are advanced with vectorised NumPy, but each replicate consumes
only its own stream, so **replicate `r` can be re-simulated in isolation
and reproduces bit-for-bit** — independently of how many replicates were
run beside it. `test_vectorised_matches_scalar_replay` asserts this
against a naive scalar re-implementation that never touches the
vectorised code path.

No aggregate in this report rests on seeds that cannot be recovered.

---

## 3. Frozen-model correspondence

Before any Level 4 science, the new implementation was pinned to the
frozen one. `level4/tests/test_frozen_correspondence.py` asserts, among
others, that: the step function agrees with `rebaseguard_certify.model.step`
on a grid of states and innovations; the `>= h` boundary fires on exact
equality; the alarm is tested after the update; `tau` starts at 1; `T_tau`
includes the terminal increment; both arms are driven by the same `Z_t`;
and — the strongest single check — **with `e0 = 0` and `m = 1`, cycle 0 of
the multi-cycle oracle is bit-identical to `frozen_model.run_path` on the
same innovations**, in `tau`, `Z_tau`, `T_tau`, alarm direction and both
terminal arm values.

Two invariants are checked on live data in every cell rather than assumed:

* `full`: simultaneous two-arm crossings observed = **0** (unreachable for the frozen CUSUM; recorded, not assumed).
* `full-mgrid`: simultaneous two-arm crossings observed = **0** (unreachable for the frozen CUSUM; recorded, not assumed).

---

## 4. Fresh / full / partial reuse comparison

All intervals are 95% percentile bootstrap over replicates.

### `m = 1`  (full campaign, 100 replicates × 10,000 cycles)

| `rho` | policy | cycle ARL | ARL / fresh | alternation | sd(`E_j`) | RMSE(`E_j`) | ACF lag 1 | ACF lag 2 | ACF lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | fresh | 82.93 [82.57, 83.28] | 1.000 | 0.4999 [0.4988, 0.5010] | 1.0000 | 1.0000 | -0.0009 | -0.0014 | 0.0000 |
| 0.02 | partial reuse | 84.16 [83.80, 84.52] | 1.015 | 0.5098 [0.5089, 0.5109] | 0.9804 | 0.9804 | -0.0170 | -0.0011 | 0.0001 |
| 0.05 | partial reuse | 86.48 [86.09, 86.87] | 1.043 | 0.5268 [0.5258, 0.5278] | 0.9530 | 0.9530 | -0.0429 | 0.0004 | -0.0000 |
| 0.1 | partial reuse | 89.44 [89.06, 89.83] | 1.079 | 0.5570 [0.5559, 0.5580] | 0.9130 | 0.9130 | -0.0905 | 0.0069 | -0.0004 |
| 0.25 | partial reuse | 95.49 [95.05, 95.96] | 1.152 | 0.6651 [0.6642, 0.6660] | 0.8448 | 0.8448 | -0.2529 | 0.0683 | -0.0191 |
| 0.5 | partial reuse | 81.63 [81.31, 81.95] | 0.984 | 0.8388 [0.8381, 0.8395] | 0.9071 | 0.9071 | -0.4691 | 0.2998 | -0.1883 |
| 1 | full reuse | 50.06 [49.79, 50.33] | 0.604 | 0.8951 [0.8945, 0.8956] | 1.3711 | 1.3710 | -0.4965 | 0.3956 | -0.3002 |

### `m = 5`  (full-mgrid campaign, 100 replicates × 2,000 cycles)

| `rho` | policy | cycle ARL | ARL / fresh | alternation | sd(`E_j`) | RMSE(`E_j`) | ACF lag 1 | ACF lag 2 | ACF lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | fresh | 162.13 [161.02, 163.25] | 1.000 | 0.4999 [0.4979, 0.5020] | 0.4469 | 0.4469 | 0.0010 | 0.0011 | -0.0019 |
| 0.05 | partial reuse | 168.50 [167.39, 169.61] | 1.039 | 0.5395 [0.5374, 0.5416] | 0.4271 | 0.4271 | -0.0586 | 0.0045 | -0.0016 |
| 0.1 | partial reuse | 171.85 [170.76, 172.91] | 1.060 | 0.5839 [0.5819, 0.5860] | 0.4134 | 0.4133 | -0.1239 | 0.0174 | -0.0028 |
| 0.25 | partial reuse | 169.47 [168.23, 170.73] | 1.045 | 0.7274 [0.7253, 0.7295] | 0.4118 | 0.4118 | -0.3169 | 0.1237 | -0.0462 |
| 0.5 | partial reuse | 124.08 [123.10, 125.06] | 0.765 | 0.8958 [0.8947, 0.8969] | 0.4913 | 0.4912 | -0.5264 | 0.4370 | -0.3339 |
| 1 | full reuse | 81.26 [80.49, 82.04] | 0.501 | 0.9205 [0.9192, 0.9218] | 0.7481 | 0.7480 | -0.4839 | 0.5093 | -0.3987 |

### `m = 10`  (full-mgrid campaign, 100 replicates × 2,000 cycles)

| `rho` | policy | cycle ARL | ARL / fresh | alternation | sd(`E_j`) | RMSE(`E_j`) | ACF lag 1 | ACF lag 2 | ACF lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | fresh | 210.72 [209.44, 211.98] | 1.000 | 0.4999 [0.4976, 0.5023] | 0.3160 | 0.3160 | 0.0010 | 0.0011 | -0.0019 |
| 0.05 | partial reuse | 217.86 [216.65, 219.08] | 1.034 | 0.5375 [0.5353, 0.5398] | 0.3019 | 0.3019 | -0.0582 | 0.0049 | -0.0017 |
| 0.1 | partial reuse | 222.88 [221.62, 224.15] | 1.058 | 0.5801 [0.5781, 0.5821] | 0.2920 | 0.2920 | -0.1225 | 0.0162 | -0.0026 |
| 0.25 | partial reuse | 219.82 [218.55, 221.06] | 1.043 | 0.7218 [0.7200, 0.7236] | 0.2892 | 0.2892 | -0.3182 | 0.1203 | -0.0458 |
| 0.5 | partial reuse | 164.00 [162.96, 165.08] | 0.778 | 0.8996 [0.8983, 0.9008] | 0.3432 | 0.3431 | -0.5592 | 0.4691 | -0.3634 |
| 1 | full reuse | 103.65 [102.85, 104.43] | 0.492 | 0.9421 [0.9408, 0.9434] | 0.5103 | 0.5102 | -0.5620 | 0.6275 | -0.5054 |

### `m = 20`  (full-mgrid campaign, 100 replicates × 2,000 cycles)

| `rho` | policy | cycle ARL | ARL / fresh | alternation | sd(`E_j`) | RMSE(`E_j`) | ACF lag 1 | ACF lag 2 | ACF lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | fresh | 269.37 [268.04, 270.70] | 1.000 | 0.4980 [0.4958, 0.5004] | 0.2235 | 0.2234 | 0.0010 | 0.0011 | -0.0019 |
| 0.05 | partial reuse | 277.10 [275.63, 278.57] | 1.029 | 0.5301 [0.5278, 0.5324] | 0.2132 | 0.2132 | -0.0458 | 0.0035 | -0.0016 |
| 0.1 | partial reuse | 283.21 [281.93, 284.50] | 1.051 | 0.5611 [0.5589, 0.5634] | 0.2050 | 0.2049 | -0.0973 | 0.0109 | -0.0022 |
| 0.25 | partial reuse | 289.16 [287.57, 290.72] | 1.073 | 0.6723 [0.6704, 0.6743] | 0.1952 | 0.1952 | -0.2635 | 0.0779 | -0.0235 |
| 0.5 | partial reuse | 251.68 [250.43, 252.92] | 0.934 | 0.8341 [0.8324, 0.8357] | 0.2215 | 0.2214 | -0.4943 | 0.3237 | -0.2054 |
| 1 | full reuse | 167.77 [166.67, 168.83] | 0.623 | 0.9138 [0.9125, 0.9150] | 0.3326 | 0.3326 | -0.5667 | 0.5303 | -0.4175 |

### `m = 50`  (full-mgrid campaign, 100 replicates × 2,000 cycles)

| `rho` | policy | cycle ARL | ARL / fresh | alternation | sd(`E_j`) | RMSE(`E_j`) | ACF lag 1 | ACF lag 2 | ACF lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | fresh | 368.35 [366.88, 369.83] | 1.000 | 0.4997 [0.4975, 0.5019] | 0.1413 | 0.1413 | 0.0010 | 0.0011 | -0.0019 |
| 0.05 | partial reuse | 375.12 [373.45, 376.80] | 1.018 | 0.5159 [0.5138, 0.5181] | 0.1346 | 0.1346 | -0.0256 | 0.0018 | -0.0016 |
| 0.1 | partial reuse | 381.88 [380.12, 383.65] | 1.037 | 0.5373 [0.5351, 0.5397] | 0.1287 | 0.1287 | -0.0552 | 0.0038 | -0.0022 |
| 0.25 | partial reuse | 395.46 [393.75, 397.22] | 1.074 | 0.5984 [0.5959, 0.6009] | 0.1166 | 0.1166 | -0.1545 | 0.0240 | -0.0077 |
| 0.5 | partial reuse | 387.40 [385.77, 389.13] | 1.052 | 0.7065 [0.7048, 0.7083] | 0.1201 | 0.1200 | -0.3096 | 0.1119 | -0.0432 |
| 1 | full reuse | 316.14 [314.59, 317.67] | 0.858 | 0.7980 [0.7961, 0.7999] | 0.1822 | 0.1822 | -0.4119 | 0.2311 | -0.1270 |

### What the comparison shows

* The **fresh control is structureless**: at `m = 1, rho = 0` the
  alternation rate is 0.4999 against the
  independent-alarm value 0.5, the lag-1 ACF is
  -0.0009, and `sd(E_j) =
  1.0000` against the exact value
  `1/sqrt(m) = 1.0000` that the policy forces. The control behaves
  exactly as its own definition requires, which is what licenses
  reading any departure from it as a reuse effect.
* **Full reuse is strongly structured**: alternation
  0.8951 [0.8945, 0.8956],
  lag-1 ACF -0.4965, lag-2
  0.3956, lag-3 -0.3002 —
  the alternating-sign, slowly-decaying envelope.
* **Cycle ARL is not monotone in `rho`.** At `m = 1` it rises from
  82.9 at `rho = 0` to a maximum of
  95.5 at `rho = 0.25`, and only then falls to
  50.1 at full reuse. Partial reuse below
  the turning point is *better* than the matched fresh control, not
  worse. This matters for interpretation: the local stability
  threshold and the ARL turning point are **different points**, so
  "reuse degrades calibration" is true only of the large-`rho`
  regime and must not be stated unconditionally.

---

## 5. Historical Phase-1.5 reproduction status

**Status of the historical material.** `rebaseguard_phase15.md` reports
Monte Carlo signatures from a session whose code, seeds and sample sizes
are not in this repository: `git log --all --diff-filter=A` finds only
the memo and its figure, never a simulator. Those numbers are therefore
**historical-only** by the standard this project applies to itself, and
what follows is a *new reproducible baseline* placed beside them, not an
attempt to force agreement.

| Signature | Phase-1.5 (historical-only) | This work | Status |
|---|---|---|---|
| fresh alarm alternation | 0.500 | 0.500 | **REPRODUCED** (tol ±0.020) |
| alternation, full reuse, `m=5` | 0.920 | 0.921 | **REPRODUCED** (tol ±0.030) |
| alternation, full reuse, `m=10` | 0.940 | 0.942 | **REPRODUCED** (tol ±0.030) |
| alternation, full reuse, `m=50` | 0.800 | 0.798 | **REPRODUCED** (tol ±0.030) |
| ACF lag 1, full reuse, `m=10` | -0.560 | -0.562 | **REPRODUCED** (tol ±0.060) |
| ACF lag 2, full reuse, `m=10` | 0.570 | 0.628 | **REPRODUCED** (tol ±0.100) |
| ACF lag 3, full reuse, `m=10` | -0.470 | -0.505 | **REPRODUCED** (tol ±0.100) |
| ARL(reuse)/ARL(fresh), `m=10` | 0.480 | 0.492 | **REPRODUCED** (tol ±0.050) |
| ARL(reuse)/ARL(fresh), `m=50` | 0.790 | 0.858 | **FAILED-TO-REPRODUCE** (tol ±0.050) |
| absolute ARL, reuse, `m=10` | 101.0 | 103.7 | **REPRODUCED** (tol ±15.0) |
| absolute ARL, fresh, `m=10` | 209.0 | 210.7 | **REPRODUCED** (tol ±25.0) |

**10 of 11** direct
observables fall inside the stated tolerance.

#### Direct observables that did not reproduce

* **ARL(reuse)/ARL(fresh), `m=50`** — historical 0.790, measured 0.858, tolerance ±0.050. Reported as
  **FAILED-TO-REPRODUCE**; no attempt was made to widen the
  tolerance to absorb it.

The `m = 50` ARL ratio deserves one remark, because it is the only
direct observable in the table that misses. Phase-1.5 did not report
that ratio directly: it reports `fresh ARL / ARL_oracle = 0.71` and
`naive = 0.56`, and 0.79 is the quotient of those two rounded
two-digit numbers, so its own uncertainty is at least a few percent
before any Monte Carlo error is counted. That does not make the
miss disappear — the entry stays FAILED-TO-REPRODUCE — but it does
mean the discrepancy is not of the same kind as the `F'(0)` one
below, which contradicts a certified enclosure rather than a
rounded quotient. The `m = 50` campaign here is also the
exploratory one, run at one fifth the cycle count of `m = 1`.

### The one historical claim that contradicts the frozen result

Phase-1.5 also reports local slopes `F'(0) = -4.51 (m=5)`, `-2.98
(m=10)`, `-0.71 (m=50)`. These are **FAILED-TO-REPRODUCE**, and they
cannot be rescued by sample size, because they contradict the frozen
Level 1–3 result directly rather than merely differing from it:

* Level 2C proves the exact identity `F_1'(0) = 1 - Gamma(m,k,h)`, and
  the Level 3 certificate encloses `Gamma(1,0.5,5)` in
  `[3.9243, 27.8494]`. So `F_1'(0)` at `m = 1`
  is certified to lie in `[-26.849, -2.924]`.
* Phase-2B/2C independently report `Gamma(5) ≈ 10.2` and `rho_c = 0.116`
  at `m = 5`, i.e. `F_1'(0) ≈ -9.2` there — roughly twice the magnitude
  Phase-1.5 reports at the same `m`.
* Gate 4.2 of this work measures `F_1'(0)` at `m = 1` by two independent
  routes that agree with each other and with the certificate.

Phase-1.5's own memo says the Phase-1 conclusion was overturned by a
mismeasured slope; the natural reading is that its replacement slope was
also measured over too wide a window — the same failure mode one step
smaller. **This work does not attempt to recover those numbers.** What is
striking is that every *direct observable* in Phase-1.5 — alternation,
ACF shape, ARL ratio, the `rho` sweep — reproduces closely, while only
the derived slope does not.

---

## 6. Uncertainty, burn-in and anomalies

### 6.1 Burn-in adequacy, from data

Burn-in is justified by block-wise means over the whole run rather than
asserted. Each cell manifest carries a ten-block diagnostic; the table
below contrasts the first post-burn-in block with the last block for the
most structured configuration available.

| campaign | `m` | `rho` | burn-in | first retained block | last block | drift |
|---|---|---|---|---|---|---|
| full | 1 | 1 | 1,000 | sd=1.3740, ARL=50.2 | sd=1.3717, ARL=50.6 | -0.0022 |
| full-mgrid | 5 | 1 | 500 | sd=0.7462, ARL=82.5 | sd=0.7492, ARL=80.9 | 0.0030 |
| full-mgrid | 10 | 1 | 500 | sd=0.5116, ARL=102.8 | sd=0.5092, ARL=101.8 | -0.0024 |
| full-mgrid | 20 | 1 | 500 | sd=0.3331, ARL=168.4 | sd=0.3337, ARL=167.1 | 0.0006 |
| full-mgrid | 50 | 1 | 500 | sd=0.1827, ARL=317.2 | sd=0.1820, ARL=316.2 | -0.0008 |

### 6.2 Anomalies and failures

All **87** acceptance checks passed. Nothing was
discarded: every configuration in every campaign appears in the
tables above, including the ones where the reuse effect is absent by
construction (`rho = 0`) or weak (`rho ≤ 0.05`).

Known limits of this campaign, stated rather than buried:

* Only `k = 1/2`, `h = 5`, Gaussian innovations were simulated. Nothing
  here speaks to other detector constants or other noise models.
* The `m > 1` campaign is run at one fifth the cycle count of the `m = 1`
  campaign and is exploratory; `m > 1` has no certified Level 1–3
  counterpart, and its minimum-dwell convention (`tau >= m`) is a
  documented choice inherited from Phase-2C, not a derived necessity.
* `mu_fresh` is drawn as a single `N(0, 1/m)` variate rather than as the
  mean of `m` standard normals. These are distributionally identical and
  `mu_fresh` is independent of the stopping event by construction, so no
  pathwise coupling is lost; it is recorded here because it *is* a
  deviation from the literal formula.
* Bootstrap intervals are percentile intervals over 100 replicates. They
  are not corrected for bias or acceleration, and for the extreme
  quantile metrics 100 replicates is not many.

### 6.3 Are the multi-cycle effects robust?

Yes, on the evidence collected, with one important qualification.

* The alternation and ACF signatures are present at every `m` tested
  (1, 5, 10, 20, 50) and at every `rho` above roughly
  0.1, and they are absent at `rho = 0` to within Monte Carlo error.
* They turn on **continuously** in `rho`, not abruptly, and the
  turn-on is monotone in every campaign.
* Replicate-to-replicate dispersion is small relative to the effect: the
  bootstrap intervals for alternation at `rho = 1` exclude 0.5 by many
  interval widths.
* **The qualification:** the *run-length* consequence is not robust in
  the same way. Cycle ARL is non-monotone in `rho` and partial reuse can
  improve on the matched fresh control. Any statement that reuse degrades
  calibration must be scoped to the regime in which it was measured.

---

## 7. Decision

### `PASS-4.1`

The criteria were fixed before the runs and are evaluated mechanically in
`level4/experiments/make_reports.py::gate41_decision`:

| # | criterion | result |
|---|---|---|
| 1 | no simultaneous two-arm crossings | PASS (31/31) |
| 2 | minimum dwell respected | PASS (31/31) |
| 3 | fresh control alternation ~ 0.5 | PASS (5/5) |
| 4 | fresh control sd(E) ~ 1/sqrt(m) | PASS (5/5) |
| 5 | fresh control lag-1 ACF ~ 0 | PASS (5/5) |
| 6 | full reuse alternation exceeds 0.5 by more than its CI | PASS (5/5) |
| 7 | full reuse lag-1 ACF negative beyond its CI | PASS (5/5) |

**87 of 87**
checks passed.

The Multi-Cycle Oracle reproduces the frozen single-cycle semantics
exactly, produces a matched fresh control that behaves as its own
definition requires, records complete provenance for every aggregate,
and exhibits the reuse-induced multi-cycle structure robustly across
`m` and `rho`. **`PASS-4.1`.**

What this decision does **not** assert: that the invariant law is
bimodal; that a period-2 orbit exists; that reuse always degrades ARL;
anything about `(k, h)` other than `(1/2, 5)`; or anything at all with the
force of a proof.
