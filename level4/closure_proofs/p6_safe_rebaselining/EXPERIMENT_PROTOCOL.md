# P6 experiment protocol (preregistration)

```text
FROZEN_AT              = before any policy-comparison number existed in this campaign
EVIDENCE_AT_FREEZE     = Stage 1 only: X1/X2/X3 correspondence, c_beta, SAW calibration constants
NOT_SEEN_AT_FREEZE     = every baseline-vs-method comparison, every delay metric, every ablation
```

This document, together with `CLOSURE_GATES.md`, discharges entry-gate items
4, 5, 7, 8, 11, 13 of `FULL_CAMPAIGN_ENTRY_GATE.md`. Everything numeric in it
is fixed **before** the comparison stages run. The one deliberate exception is
gate `G-E`, whose deferral to post-pilot was itself preregistered in
`PREREGISTRATION_OPTIONS.md` section 2; section 8 below records how that
deferral is executed so it cannot be resolved informally.

---

## 1. Primary objective and primary cell

| item | choice | why (fixed in advance) |
|---|---|---|
| primary objective | **`O1`**: minimise `Dtail(100)` at the primary shift, subject to the Tier-1 constraints | `S9` is the strongest *closed* statement P7 makes about where the damage lives, and it is a tail statement: at CUSUM `m=1, rho=1, Delta=1` the median delay (`7`) beats nominal while `q95 = 275` and `P(delay>100) = 11.4%` |
| primary cell | **CUSUM, `m = 3`, `Delta = 1.0`** | `m = 3` is inside the range P3/P7 support and is *not* the cell most favourable to the method: the one-step Jensen gap of `THEORY.md` T6-C is largest at `m = 1` (`~10%`) and smallest at `m = 5`, so choosing `m = 3` deliberately avoids the best case. `m = 1` is additionally declared "unusable at any `rho`" by `S14`, so it is unsuitable as a primary. `Delta = 1.0` is P7's headline shift |
| reported scientific output | **`O5`**: the Pareto frontier over (`Dtail`, `Arl0`, `Fresh`) with baselines and oracles on the same axes | removes the obligation to name a winner (`F7`) |
| declared surrogate | **`O2`**: `OutCal(beta)` | may be optimised, never gated on (`S18`, `X6`, `F2`) |
| composite `Risk` (formulation D) | **screening only**, weights frozen here as `w_D = w_A = w_F = 1/3` on values normalised at `rho = 1` | no closure claim rests on it |

## 2. The candidate method and its information set

`METHOD.md` defines SAW in full. For preregistration purposes:

* **Information set:** `tau_j` (F01) and the terminal window (F05/F06) through
  `zbar_j(m)` and `w_j = min(m, tau_j)`. Nothing else. **Memoryless.**
* **Latent quantities used:** none. `CycleObservation` has no field carrying
  `e`, `raw`, `Rbar` or `shift` (asserted by test).
* **Future information used:** none.
* **Shift direction used:** none. SAW is calibrated **entirely at `Delta = 0`**,
  so no out-of-control information of any kind enters its constants -- the
  strongest available form of the `F8` anti-leakage guarantee.
* **Free hyperparameters:** none. The four constants `(g0, g1, s0, s1)` are
  ordinary least-squares / group-mean estimates from a fixed-point calibration
  on `TUNE` seeds; `rho_max = 0.95` and the variance floor `1e-2` are structural
  constants required by `THEORY.md` T6-B; `(m, k)` are design choices swept as
  axes, not fitted.
* **`c_beta` for SAW-T:** `beta = 0.25`, i.e. the reference error at which the
  conditional in-control ARL has fallen to a quarter of nominal. **Frozen here,
  before any SAW-T number exists.** Derived from P7's closed response curve in
  `results/c_beta.json`: `c = 0.2816` (CUSUM), `0.2656` (SR), interpolation
  bracket `0.05`.

## 3. Baselines (frozen; not extended after results are seen)

| id | policy | parameters |
|---|---|---|
| `B0`/`B1` | fresh-only | `rho = 0`, `k = m` |
| `B2` | **fixed-`rho` grid** | `rho in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75}`, `k = m` |
| `B3` | full reuse | `rho = 1` |
| `B4` | `m` sweep | via the `m` axis |
| `B5` | adaptive `m` from `tau` | `m_short = 1, m_long = m, tau_split = 20` |
| `B6` | two-level `rho` from `|zbar|` | `rho_hi = 0.5, rho_lo = 0.05`, `q` = median `|zbar|` from calibration |
| `B7` | overshoot rule | `rho_hi = 0.5`, `a = 1` |
| `B8` | window-dispersion rule | `rho_hi = 0.5`, `a = 1` |
| `B9` | fresh injection | `rho` at the `B2` optimum, `k in {2m, 4m}` |
| `B10` | capped consecutive reuse | `rho = 0.5`, `n_max = 3` |
| `B11` | confidence gate | `rho_hi = 0.5`, `q` = median `|zbar|` |

**`B2*` -- the bar.** `B2*` is the member of the `B2` grid with the best primary
objective **at matched `Fresh`**, selected on `TUNE` and then re-estimated on
`EVAL`. Beating `B3` is a sanity check, never a result
(`METHOD_NOVELTY_SEPARATION.md` section 3).

`Z5` (the stationary-law oracle: the single best fixed `rho`) is estimated by
the `B2` grid minimum on the **evaluation** family, with the grid-selection bias
handled by re-estimating it on `REPLAY`.

## 4. Metrics (frozen)

In-control (`Delta = 0`): `Arl0`, `Fap50`, `Fap100`, `Rate`; reference `Rms`,
`Mad`, `Q95e`, `Tail(0.2/0.5/1.0)`, `OutCal(beta)` for
`beta in {0.75, 0.5, 0.25, 0.1}`; cost `Reuse`, `Fresh`, `FracReuse`, `Wbar`,
`Down`, `Eff`, and the proportional-cost sensitivity `FreshProp`.

Out-of-control: **`Dmean`, `Dmed`, `Dq95`, `Dtail(50)`, `Dtail(100)` are all
mandatory in every table** (`S9`, `F4`); plus `Rdelta` and, as a latent
diagnostic only, the blind-spot mass `P(|e - Delta| < 0.2)`.

Finite-cycle: `Coll = E[tau_2]/E[tau_1]`, and per-cycle curves to cycle 50.

Cost model (entry-gate item 13, decided here):

* **(C-a) blind** fresh-collection window: the `k_j` post-alarm observations are
  unmonitored, so `Down = Fresh` is a risk term as well as a cost term.
* **(C-b) step-shaped** primary cost `C_fresh = k_j 1{rho_j < 1}`, i.e. cost
  proportional to the number of newly collected observations -- the campaign
  brief's `C_fresh = k_fresh`. The proportional variant `(1-rho_j) k_j` is run
  as a declared sensitivity (`FreshProp`) and never as the primary.

**A structural consequence of (C-b), recorded now because it determines gate
`G-C`:** every policy that ever draws a fresh baseline pays exactly `k` per
alarm, so `Fresh` separates policies only through `k`, not through `rho`. The
sample-cost axis is therefore explored by sweeping `k`, and `k` is the knob that
traces the frontier.

## 5. Regimes (mandatory, `EVALUATION_PROTOCOL.md` section 5)

| regime | definition | applies to |
|---|---|---|
| `R1` | cycle 1 from `e_0 = 0` | all |
| `R2` | cycle 2 -- the cycle after the first re-baselining; `Coll` | all |
| `R3` | cycles 1..50 from `e_0 = 0`, no burn-in, per-cycle curves | all |
| `R4` | post-burn-in, long run | all |

**No claim rests on R1 or R4 alone.** Burn-in is re-established per policy class
from the R3 curves (entry-gate item 15) rather than inherited from P7's 12.

**Finite-reference robustness (secondary).** In addition to the canonical
`e_0 = 0`, an `e_0 ~ N(0, 1/m_0)` regime with `m_0 in {20, 50, 100}` is run as
secondary robustness evidence. It does not replace the canonical experiment.

## 6. Seeds, tuning/evaluation separation, and pairing

* Three disjoint families: `TUNE` (calibration and every design choice), `EVAL`
  (all reported numbers), `REPLAY` (independent reproduction, untouched until
  the confirmation stage is complete). Disjointness asserted by test.
* SAW's constants are fitted on `TUNE` **at `Delta = 0` only** and are frozen
  before any `EVAL` run. The freeze point is `results/calibration.json`.
* Comparisons are **paired by seed**: policies in a comparison share the
  replicate stream (`pair_tag`). Pairing is valid regardless of coupling
  strength; the **measured** pair correlation is reported per comparison and
  power is sized on the *unpaired* variance (`F5`).

## 7. Compute staging and early stops

| stage | purpose | seeds | scale |
|---|---|---|---|
| **S1 foundation** | X1-X5, `c_beta`, calibration | TUNE/EVAL | done |
| **S2 pilot + screen** | baseline `Coll`, `cv` measurement, screen all baselines and SAW variants on in-control + reference metrics | TUNE | `n_rep = 4000`, `n_cycles = 60` |
| **S3 ablation** | mechanism: sensor removal, tau-feature removal, naive proxy, oracle rungs | TUNE | as S2 |
| **S4 confirm** | the frozen shortlist, full metric set, `Delta in {0, 1}` at tail precision | EVAL | `n_rep = 40000` delay cells |
| **S5 robustness / replay** | both detectors, `m in {1,2,3,5}`, `Delta in {0,0.5,1,2}`, `e_0` regimes, `k` sweep, `REPLAY` reproduction | EVAL + REPLAY | as S4 |

Early stops `ES1`-`ES5` apply at S2/S3 on `TUNE` only, and **every drop is
recorded with its reason and its numbers** (`DROPPED_POLICIES` table in
`RESULTS.md`). Screening may eliminate, never select (`COMPUTE_PLAN.md`
section 2): a policy is dropped only if it is worse than the matched-cost
fixed-`rho` baseline with the paired interval excluding zero.

## 8. How gate `G-E` is set

`PREREGISTRATION_OPTIONS.md` section 2 defers `G-E`'s threshold to post-pilot
"by prior agreement". Execution, in this order and recorded in
`results/gate_e.json` with the ordering explicit:

1. S2 measures `Coll` for `B0`, `B2` grid and `B3` **only**.
2. The `G-E` threshold is written down from those numbers alone.
3. Only then is `Coll` computed for SAW.

## 9. Statistical analysis (frozen)

* **Unit:** the independent replicate. Never the cycle.
* **Intervals:** BCa bootstrap over replicates, `B = 10000`, plus a normal
  interval; both reported. Ratios (`Coll`, `Rdelta`, relative losses)
  bootstrapped as ratios. Quantiles bootstrapped as per-replicate quantiles.
* **Paired differences:** bootstrap over replicate pairs, `B = 10000`.
* **Verdict labels:** P7's, verbatim -- `INCONCLUSIVE`,
  `STATISTICALLY_RESOLVED`, `PRACTICALLY_MATERIAL`.
* **Tail sizing:** a tail estimate is reported only if the expected tail-event
  count per arm exceeds `200`; otherwise `INSUFFICIENT_TAIL_EVENTS`, never
  `INCONCLUSIVE`.
* **Multiplicity:** one primary objective at one primary cell. Secondary
  comparisons carry Benjamini-Hochberg FDR at `q = 0.10` within each metric
  family, reported beside the raw intervals. The real protection is
  reproduction: both detectors, `>= 3` values of `m`, and an independent seed
  family.
* **Grid-selected optima:** `B2*` and `Z5` are grid minima and therefore biased
  optimistically on the family that selected them; they are re-estimated on
  `REPLAY` and the shift is reported.
