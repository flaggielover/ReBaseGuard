# P5Y K1 — CUSUM completion successor

**NOT production. Not result-bearing. No cell of the frozen cover is claimed
closed by this namespace beyond what its own certificates state.**

This namespace answers a narrow two-part task set after the independent
adjudication of `f8e6f758`:

1. repair the final-successor **producer / provenance binding** (adjudicated
   `PROVENANCE = FAIL`);
2. **tighten and certify CUSUM cells 318–324** (adjudicated
   `CUSUM_318_324_CLASSIFICATION = CERTIFICATE_TOO_LOOSE`).

It does **not** implement SR, does not change far-field logic, and does not run
production.

---

## Inherited findings, taken as given

Recorded in `code/ancestry.py` and never re-litigated here:

| finding | state | this namespace |
| --- | --- | --- |
| `DRIFT_AWARE_NORM` | SOUND | inherited and used unchanged |
| `CELL_325` | CERTIFIED_PASS | kept as the regression control |
| `CUSUM_FAR_FIELD` | PASS | inherited, not re-derived |
| `SR_FAR_FIELD` | PASS | inherited, not re-derived |
| uncovered interval between `c_D` and `e_far` | **none exists** | the predecessor's contrary reading is recorded as superseded in `code/far_field_inherited.py` |
| `COST_CAP` | NOT_ESTABLISHED | still NOT_ESTABLISHED; the predecessor's 435.8 CPU-hour figure is **not** carried forward |

---

## Part 1 — the provenance repair

### The defect

Every final-completion record stamped **Repair2's** producer hash, with a note
saying so:

```json
"producer": {
  "implementation_hash": "f703921b045f39092d9bdf67d02927f70961dd344dc3be50d17aab0b23df16bd",
  "implementation_hash_kind": "repair2_producer_manifest_v1",
  "note": "this record is produced by the final-completion certifier, whose
           modules are NOT in the Repair2 producer manifest; the stamped hash is
           Repair2's and is recorded for lineage only, not as this record's
           producer identity"
}
```

`base.py`, `sharp_norms.py` and `sharp_certifier.py` — the code that computed
every certified bound in those records — were outside the manifest the records
were stamped with. Editing any of them would have left the stamped identity
unchanged, so the certificates did not bind their own producer. A record is only
as good as the identity that fixes what produced it.

### The repair

`code/successor_producer.py` builds a **47-file manifest** hashed into a single
producer identity of its own kind, `cusum_successor_producer_manifest_v1`:

* every certifying module of this namespace (`ancestry`, `order2`, `refine2`,
  `successor_producer`, `successor_certhash`, `successor_universe`,
  `successor_qualify`);
* every inherited module that actually executes — final-completion (3), Repair2
  (5), Repair1 (5), reviewed implementation (13);
* the frozen successor's own inputs (checkpoint, cells, cover witnesses, record
  schema, `ERROR_ALGEBRA.md`, `algebra.py`);
* the certified backend contract (8 files), hashed separately as
  `backend_hash`;
* the generation parameters, including pinned `python-flint`, `numpy` and
  `scipy` versions and the threading contract `blas_threads = 1`,
  `flint_threads = 1`.

Reporting, decomposition, self-audit and diagnostics are deliberately **outside**
the manifest: they cannot change a certified value. `verify_loaded_modules_
covered()` runs inside every cell run and fails the run if any module that is
neither third-party nor explicitly non-certifying was imported without being
covered.

Rejected as this successor's identity, each by an explicit negative control:
Repair2's hash, the reviewed parent's hash, any final-completion lineage hash,
and every git commit id.

### Determinism

The float candidate solve goes through `numpy.linalg.solve`; multi-threaded BLAS
changes its reduction order, hence the dyadic candidate, hence every certified
residual. `successor_qualify` therefore pins the thread environment and re-execs
itself **before numpy is imported**, records the contract in the certificate, and
binds it into the producer identity — so a record made under different threading
is a *different producer*, not a silently different certificate.

`code/successor_certhash.py` separates scientific content from runtime noise:
CPU seconds, wall seconds, RSS, call counts, host and threading are excluded from
the scientific hash; every certified interval, bound and status is included.

Verified, not asserted: fresh repeat runs of cells 318 and 323, in separate
processes and a separate output directory, reproduce the recorded scientific
hash exactly while their CPU seconds differ by a factor of two
(`diagnostics/determinism.json`). That is the adjudicated predecessor defect —
repeats under one producer identity producing different hashes — checked
directly.

**Importing `successor_qualify` re-execs the process** unless the pinned
environment is already set, because the thread environment must be in place
before numpy loads. A process whose `sys.argv[0]` is not a file (`python -c`,
`python -m unittest`) cannot be re-executed faithfully and dies. Any harness that
imports it must adopt the contract first, as `tests/test_successor.py` does at
the top of the file. Making the guard degrade gracefully instead would change
the producer identity, so it is left for a task that is re-running the cells
anyway.

---

## Part 2 — the tightening

Three levers, each an upper-bound improvement only, none touching the frozen
error algebra, ledger, budgets, charges, geometry, precision or Taylor degree.

### 1. Drift-aware operator norms (inherited, SOUND)

Kept exactly as adjudicated. `sharp_norms` replaces whole-line Cramér suprema by
Hermite-weighted integrals over the cell's reachable window.

### 2. Order-2 Taylor-in-`e` on the residuals (`code/order2.py`)

Every order-2 residual's whole-cell bound was ≥ 99.8% mean-value term:
`delta_cell = delta_mid + rho * Env`, with `Env` a product of operator norms and
candidate suprema — loose twice over, since an operator applied to a *specific*
candidate is far from its worst case and the terms in the sum cancel. Replaced
by

```
sup_cell |r|  <=  sup_x |r(e0)| + rho * sup_x |d_e r(e0)| + (rho^2/2) * sup |d_e^2 r|
```

where the middle term is the certified Bernstein range of the actual
differentiated residual. Measured 3.3×–9.8× on the targeted objects.

Closed-form leaves (`h_1^(k)`, `S_0^(k)`) additionally use drift-aware pointwise
suprema over the cell's argument windows instead of the whole-line bound
(3.8× at cell 321).

### 3. Second-order Taylor-in-`e` on the whole-cell `D` and `F` bounds (`code/refine2.py`)

After lever 2 the binding quantity is `epsH`, and the predecessor produced
`epsD` by a mean-value step whose midpoint part is negligible — so essentially
all of `epsD` was `rho * epsH`, closing an `epsH -> epsD -> epsH` loop with gain
`rho*C*2k1 = 0.408` (amplification 1.69× at cell 321). `F` was already expanded
to second order; `D` was not, only because no third-derivative bound existed.
`refine2` supplies one by differentiating the frozen equation `(I - K_e)F = S`
one order further than the frozen algebra does:

```
supF3  <=  C ( 3 k1 supH + 3 k2 supD + k3 supF + supS3 )
```

whose binomial coefficients continue the frozen second-order line. This adds no
certified error level, no object and no charge — it is a norm-only majorant used
inside the refinement, exactly as `supH = sup|Hhat| + epsH` already is. All the
maps are monotone non-decreasing in `(epsF, epsD, epsH)`, the iteration is seeded
with the predecessor's own refinement and every step takes `min` with it, so the
sequence is a decreasing sequence of valid bounds; a guard refuses any `r` that
is not `<=` the predecessor's.

`propagate` is reviewed and unedited — its refinement dependency is substituted
explicitly by `refine2.install()`, recorded in every record under
`whole_cell_refinement_module`, covered by the producer manifest and asserted by
the test suite.

The break-even analysis that motivated it, including the correct like-for-like
comparison, is in `diagnostics/third_order_analysis.py`.

---

## Results

See `RESULTS.md` for the full per-`(cell, m)` table, the comparison against the
predecessor, and the exact classification of every remaining failure.

---

## Governance

Unchanged and asserted by tests: cover endpoints, cell splits, precision
(256 bits), Taylor degree, budgets (Σ = 19/100), reserve (not drawable, not
redistributed), the 1126 CPU-hour cap, `m` scope, detector scope, Taylor
semantics, the 17,978-obligation universe and the frozen spec hashes.
`PRODUCTION_ENABLED` is false; no production ran; no historical verdict was
edited. The frozen successor, the reviewed implementation (`c0a1f40`), Repair1
(`4164121`), Repair2 (`7a7df9b`) and the previous final-completion namespace
(`f8e6f75`) are byte-identical to their commits, which the test suite checks with
`git diff` against each commit.

---

## Layout

```
code/         ancestry, order2, refine2, producer/identity/hash, runner,
              determinism, far-field inheritance, audit, reporting
tests/        test_successor.py, test_pre_repair_provenance.py
diagnostics/  cells/succ_CUSUM_<n>_256.json, third_order_analysis.*
```

## Reproducing

```
code/run_successor.sh OUTDIR 318 319 320 321 322 323 324 325   # ~45 min, 8 workers
cp OUTDIR/succ_CUSUM_*.json diagnostics/cells/

code/run_successor.sh REPEATDIR 318 323                        # determinism repeats
python code/determinism.py --repeats REPEATDIR --out diagnostics/determinism.json

python code/successor_audit.py --tests-ok yes --out diagnostics/audit.json
python code/successor_report.py --write
python diagnostics/third_order_analysis.py
python -m unittest discover -s tests -p 'test_*.py'
```

Eight workers on eight cores roughly doubles the CPU seconds each cell reports,
through memory-bandwidth contention; the audit records both figures.
