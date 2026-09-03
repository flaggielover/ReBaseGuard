# CUSUM Global Production Cover — Result

Binding pre-result anchor: Checkpoint K, commit
`3704988533f2d9038ddf0b35e58dea0eed4b6a2d` (pushed before the run started).
Machine-readable ledger: `../results/cusum_m1_production.json`.

**Headline: the run completed, and it did not pass. 46 of 47 cells satisfy the
strict criterion; cell 46 fails it. `CUSUM_M1_G3 = FAIL`.**

This document does not restate the failure as a success, and does not move
`e_far` after the fact to make it disappear. See §5.

## 1. What was run

| item | value |
| --- | --- |
| detector | two-sided CUSUM, `k = 1/2`, `h = 5` |
| moment | first (`R_{CUSUM,m}(e)`) |
| `m` actually run | **`m = 1` only** — see §6 |
| certifier | `certified_method_repair_ra/ra_certifier.py` + `compute_optimization_r2/r2_certifier.py`, unmodified |
| precision | 256 bits, Taylor order 120, degree 12 |
| `e` domain | `[0, 12]`, frozen `e_far = 12` (`FROZEN_SCOPE.md` §3) |
| cover | 47 outer cells, 372 sub-cells, exact rational endpoints |
| gaps / overlaps | **0** — consecutive endpoints are equal as exact rationals |
| criterion | `ABS_MAX < 2` strictly (theorem consumer `P5X-T4`); historical `F3 = 0.2` **not** applied |
| cost | 3.903 CPU-hours, 1.027 wall-hours, 80.4 MiB peak RSS |
| resource STOP (500 CPU-h) | not triggered |

## 2. Result

```
cells passing : 46 / 47
failing cells : [46]
min margin    : -0.336766   (cell 46)
2nd-min margin: +0.033003   (cell 45)
median margin : +0.748300
max margin    : +1.931326
```

The failing cell:

```
cell 46   e in [10.5441104, 12.0]   width 1.4559   n_sub 4   C = 1.0000002
          R in [-2.336765897, +2.336765896]
          centre    ~ 4.3e-10        half-width 2.3367659
          ABS_MAX   = 2.336765897    margin = -0.336765897   FAIL
```

## 3. Diagnosis: certificate width, not a G3 violation

The enclosure is centred on `4.3e-10`. The certificate does **not** claim `R`
is large there; it fails to claim anything useful, because it is 2.34 wide.
Independently, the frozen exact theorem `P5X-T3` gives a majorant `B_D`
decreasing in `|e|` with `|R_CUSUM(±10)| <= 3.2e-5`. So the true `|R|` on
`[10.544, 12]` is below `3.2e-5`, and this is a **C-F2 failure (certificate too
wide)**, not a **C-F1 failure (true `sup |R| >= 2`)**.

Width attribution, sub-cell 0 of cell 46 (diagnostic, `diagnose_cell46.py`):

| term | contribution | share |
| --- | --- | --- |
| `e`-range | ±0.181986 | 8.1% |
| `C·delta` | ±0.000000 | 0.0% |
| `h·dg` | ±0.269065 | 11.9% |
| `(h²/2)·S2` | **±1.809203** | **80.0%** |

with `G0 = 10.726`, `G1 = 1.0000`, `S2 = 49.981`.

**Root cause — a design flaw in the cover rule I froze in Checkpoint K.** The
rule sized the model radius `h` from the *contraction* condition
`C·(2a·h + b2·h²) <= 1/2`; on cell 46 that gives `0.499438 <= 0.5`, satisfied.
But the *enclosure width* is dominated by `(h²/2)·S2` with
`S2 ≈ 2C(b2·G0 + …)` and `G0 ≈ sup|ĝ| ≈ e`. So the width grows like
`h²·C·e`, which the frozen rule never bounded. Where `C` is large (small and
mid `e`) the contraction rule forces `h` tiny and the enclosure is tight; where
`C → 1` (large `e`) it permits `h ≈ 0.27` and the enclosure blows up. The two
largest-`e` cells are exactly the two smallest margins (+0.033, −0.337).

The rule was frozen before the run and is preserved as frozen. The flaw is
recorded, not repaired in place.

## 4. Correspondence

Production cell 28, `e ∈ [0.2286224, 0.2491648]`, encloses
`R ∈ [-1.585641304, -1.564220910]`. The independently recorded R2 benchmark at
`e = 24/100` gives `R ∈ [-1.584973380, -1.567644375]`. The production cell
**contains** the benchmark enclosure, as it must (it spans a wider `e`-range).
The drift resolvent reproduces `C = 220.7075187096823143058125152854812294891688046029854141728 ± 7.14e-5`
at `(24, 100)`, matching the recorded R1/R2 value.

Excluding the two width-dominated large-`e` cells, the largest certified
`|R|` is `1.5857` near `e ≈ 0.24`, consistent with the known `|R|` profile.

## 5. What this result is NOT allowed to become

`P5X-T3` is valid for every `|e|` at which its majorant is evaluated, and
`B_CUSUM(10) <= 3.2e-5` is already recorded in `FROZEN_THEOREM.md`. It is
therefore *mathematically* true that the union

```
certified finite cover on [0, 10.5441104]   +   P5X-T3 on [10, infinity)
```

has no gap and that every cell in that reduced cover passes.

**That is not this run's result, and it is not being adopted here.**
`e_far = 12` is frozen in `FROZEN_SCOPE.md` §3 and was restated in Checkpoint
K §6 before the run. Re-cutting `e_far` to 10 *after* seeing cell 46 fail is
precisely the post-result optimization the brief forbids (§13). The reduced-cover
observation is recorded as a **pre-registerable successor option**, to be frozen
before a future run, never as a reclassification of this one.

The same applies to the cover rule: adding an enclosure-width cap
`h² · C · b2 · G0 <= epsilon` alongside the contraction cap would very likely
fix cell 46 at negligible cost (`C ≈ 1` there, so cells are cheap). That is a
successor design, not an amendment.

## 6. `m > 1` was not run, and could not be

`ra_certifier.py` line 1 reads "R-A' certified enclosure of
`R_{CUSUM,m=1}(e)` over a cell." A search over every `.py` file in the
namespace finds the `m`-dependent objects `h_j` / `S_j` **only** in
`feasibility/fredholm_probe.py`, a Phase-1 probe, and never in a certifier.
There is no `m > 1` CUSUM certifier in the tree. Brief §3 forbids inventing
one. Therefore:

```
CUSUM_M2_G3 = CUSUM_M3_G3 = CUSUM_M5_G3 = INCOMPLETE   (no certifier exists)
P5X_CUSUM_GLOBAL_G3          = INCOMPLETE
SECOND_MOMENT_PRODUCTION     = NOT_RUN
```

This was disclosed in Checkpoint K §0 **before** the run, not discovered after.

## 7. Governance

This run changes no historical verdict. It is new evidence appended to a
closed record, and it is negative evidence for the cover rule, not for the
theorem.

```
P5_SCIENTIFIC_LINE_STATUS = PARTIALLY_REPAIRED_BY_SUCCESSOR   (unchanged)
P5X_FINAL_VERDICT         = PARTIAL                           (unchanged)
P5X_SR_GLOBAL_G3          = OUT_OF_BUDGET                     (unchanged)
LEVEL4_GLOBAL_CLOSURE     = NO                                (unchanged)
NOVELTY_STATUS            = NOT_ESTABLISHED                   (unchanged)
```

The original P5 record remains immutable and historically `PARTIAL`.
