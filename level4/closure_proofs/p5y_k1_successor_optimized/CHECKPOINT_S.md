# P5Y — K1 SUCCESSOR BINDING CHECKPOINT
# Optimized certified backend / full K1 campaign

**DESIGN ONLY. `P5Y_K1_SUCCESSOR_PRODUCTION_RUN = NO`.** This task stops at T1S.

```text
lineage        parent checkpoint anchor 310c3aa, hash ababbef4…
               HISTORICAL K1 verdict  K1_INCOMPLETE_BUDGET   [immutable]
               HISTORICAL K1 cap      1848 CPU-h             [immutable evidence]
               Task 1  FAIL / IMPLEMENTATION_DEFECT          [immutable]
               Task 1R PASS                                   [immutable]
               backend audit COMPLETE / BACKEND_HARD_TARGET_PASS
               P5_ORIGINAL_VERDICT = PARTIAL, P5X_FINAL_VERDICT = PARTIAL
```
The historical campaign is **not** resumed or repaired in place. This is a new
namespace with a new verdict lineage.

## 1. Target — identical
`R_max(D,m) = sup_e |R_{D,m}(e)| < 2` for both frozen detectors and all frozen
`m ∈ {1,2,3,5}`. No detector removed, no `m` removed, no cover narrowed, no
splice moved. **`K1_CLOSED` does not close P5** — K2–K5 remain.

## 2. Backend frozen
The optimized cancellation-preserving backend that passed the cost audit
(`p5y_k1_sr_backend_cost_audit/code/opt_backend.py`, routes O1+O2+O3), at the
Task1R-frozen `D = 11`, `Z = 20`. Its elements: patch/panel-local Chebyshev
composition tensors; certified Gaussian moments; bivariate Taylor models in
`(α,ζ)` and `(β,ζ)`; the shared panel operator `M = P·Hankel(N)·Qᵀ` factorised
through `R = P·Hankel(N)`; `arb_mat` carriage; patch-outer / drift-inner /
function-innermost ordering; value and derivative sharing every intermediate;
m-sharing. **The optimization is reuse, scheduling and exact algebraic
refactoring — no new mathematics.**

## 3. Correctness equivalence — frozen criterion
Same quantity · enclosure overlap/containment against Task1R · no weaker
interval semantics · same ledger outcome line by line · same P1 · same sliver
treatment · same candidate representation · same precision · same resolvent
theorem · no float-only load-bearing path.

**Bit-identical interval endpoints are NOT required** and must not be demanded:
they are unattainable across a reordered interval summation. Frozen tolerance
`1e-8` relative. Measured: 144/144 enclosures overlap, equation defect agrees to
`1.49e-10`, endpoint slivers bit-identical, `delta_F0` ratio `0.99992`, all
per-line gates pass.

The optimized certificate is **not uniformly conservative**: the truncation
channels are 2–3% larger, the interval channel 0.26% smaller because matrix
products round fewer times than long scalar chains. Both are rigorous
enclosures of the same quantity.

## 4. Audit adjudicator amendments — recorded, not hidden
1. **CUSUM control.** A loaded-machine sample (299.2 s) showed an apparent 27.8%
   regression; a quiet re-measurement gave 238.8 s against a 234.1 s reference
   (2.0%). The check was amended to use the quiet sample.
2. **Equation-defect comparison.** An adjudicator check initially demanded bit
   equality; the frozen criterion is enclosure agreement, not bit equality.

**Conclusion: neither amendment changes a scientific or performance decision.**
Machine load inflates the SR timings too, so the decisive figure was
conservative under either sample; and the backend qualified on the criterion the
science actually requires. The decisive quantity — worst-cell amortized
`t_panel = 2.731 ms` against a `10.442 ms` HARD target frozen *before* timing —
is untouched by both.

## 5. Performance model — worst cell, caches not free
```text
worst benchmark cell        C_sliver_heavy, patch (63,63)
t_panel                     2.731 ms  = shared 102.6 ms / 6118
                                       + drift 0.1 ms / 19
                                       + per-function 2.711 ms
SR raw                      387.3 CPU-h        candidate construction 0.18
CUSUM                       126 CPU-h          x1.15 overhead, x1.05 aggregation

central                     620.1 CPU-h
conservative                750.2 CPU-h   x1.2781 — the MEASURED machine-load
                                          inflation from the audit's own control
worst plausible             899.6 CPU-h   a further x1.25 for patch-class variation
```
Cache build is inside `t_panel` by amortisation; it is not assumed free.

**Degraded-reuse contingency** (shared cache not held across drifts):
`8.116 ms/panel → 1542 CPU-h`. This is **not** a budget band — the frozen memory
plan prevents it, so its occurrence is STOP `S04`, not an overrun to absorb.

## 6. CPU governance
```text
SUCCESSOR_K1_HARD_CAP = ceil(1.5 x 750.2) = 1126 CPU-hours
HISTORICAL_K1_CAP     = 1848 CPU-hours          [distinct, immutable, not copied]

1126 / 899.6 (worst plausible) = 1.252   does not bind below the campaign's own
                                         worst projection
1126 / 620.1 (central)         = 1.816   materially constraining
1126 / 1848  (historical)      = 0.609   the successor is genuinely cheaper
```
`β = 1.5` is governance-inherited from Gate-2C-bis and the parent checkpoint.
**No in-campaign extension.**

## 7. Memory and parallelism
Per-patch shared cache ~22 MiB · candidate set ~108 MiB · audit peak RSS 269 MiB
· per-worker budget 300 MiB with a ×2 safety margin. `MAX_WORKERS = 64`
(~38 GiB). Each worker **owns** the cache for its assigned patches: no
cross-worker sharing, no mutable global state. Scheduling is deterministic —
assignment is a pure function of `(shard index, shard count)`. No
oversubscription. Parallelism changes wall time, never CPU accounting:
1 → 620 h, 8 → 78, 16 → 39, 32 → 19, 64 → 9.7.

## 8. Cover, DAG, ledger, P1, precision
Inherited verbatim from the parent checkpoint: CUSUM 323 sub-cells, SR 322
sub-cells / 3994 live patches / 83,452 panels, the 19-function DAG with 10
resolvent solves, the absolute non-redistributable ledger, `eps_P1 = 1e-3` with
construction target `(1−eps_P1)·1e-9`, acceptance `1e-9`, `HEADROOM_REL ≥ 1e-6`
at `P1_RULE_WORKPREC = 512`, production precision 256 bits, complexity ceiling
60,000. No result-dependent splitting, no adaptive cover change after T2S.

## 9. Endpoint-sliver gate
The tightest channel: 88.078% of `B_end` at the reference cell. **`B_end` is
checked independently for every required (sub-cell, patch).** No cross-cell
borrowing, no redistribution, and `B_end` is **not** pre-emptively enlarged. Any
patch exceeding its own `B_end` fails under the frozen taxonomy (`S09`).

## 10. Cache dependency — load-bearing
Every cached quantity carries a key naming the dimensions it depends on, and may
be reused **only** across dimensions absent from that key. Verified by
measurement in both directions:
```text
POSITIVE  Chebyshev tensor bit-identical across drift        -> licenses 6118x reuse
NEGATIVE  Chebyshev tensor differs across patch              -> key cannot narrow
NEGATIVE  Gaussian moments differ across drift               -> correctly keyed on e
POSITIVE  panel grid identical across drift                  -> P1 rule is e-free
```

## 11. Work conservation
Unit identity `(detector, subcell_index, function_id)`; 12,255 units
(CUSUM 6,137 + SR 6,118). Shard `k` receives `[floor(k·N/S), floor((k+1)·N/S))`
— **floor boundaries, never ceil-per-shard**, which is the P4X shard-rounding
defect. Sum over shards equals `N` exactly; no overlap, no omission;
deterministic order-independent aggregation; every unit individually
recomputable.

## 12. Execution order
A integrity + backend-artifact checks (Task1R **verified, never re-executed**) ·
B CUSUM production (~126 CPU-h) · C SR production in frozen patch order
(~387 CPU-h) · D exact all-m assembly · E far-field splice · F independent
adjudication. CUSUM first: ~20% of cost, identical assembly/DAG/ledger, so a
failure surfaces cheaply.

## 13. STOP rules — 16, no "continue and see"
Hash mismatch · protected-tree mutation · backend equivalence failure · cache
scope violation · precision change · degree change · budget redistribution · P1
failure · `B_end` failure · complexity breach · cover gap · work
duplication/omission · splice gap · CPU-cap breach · true counterexample ·
invalidating implementation defect.

## 14. Verdicts
`K1_CLOSED` · `K1_FAIL_MATHEMATICAL` · `K1_FAIL_CERTIFICATE` ·
`K1_FAIL_GOVERNANCE` · `K1_INCOMPLETE_BUDGET` · `K1_INCOMPLETE_EXTERNAL`. Every
STOP maps deterministically. **No producer self-award.**

---
```text
P5Y_K1_SUCCESSOR_CHECKPOINT_STATUS = FROZEN
P5Y_K1_OPTIMIZED_BACKEND           = QUALIFIED
P5Y_K1_SUCCESSOR_PRODUCTION_RUN    = NO
P5Y_K1_SUCCESSOR_VERDICT           = NOT_RUN
```
