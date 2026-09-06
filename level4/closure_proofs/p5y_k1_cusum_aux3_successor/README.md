# P5Y K1 — CUSUM aux3 successor

**NOT production. Not result-bearing. No cell of the frozen cover is claimed
closed beyond what its own certificate states.**

A new governed successor to `70a2943`, created because independent adjudication
returned **`CUSUM_SUCCESSOR_UNSOUND`** against that namespace's *validation and
provenance architecture* — not against its mathematics. The predecessor is left
byte-identical and its records stand as its own evidence.

Inherited and not re-opened: `REFINE2_SOUND = YES`,
`CERTIFICATE_DETERMINISM = PASS`, `CELL_325 = CERTIFIED_PASS`,
`CUSUM_FAR_FIELD = PASS`, `SR_FAR_FIELD = PASS`,
`REMAINING_WIDTH_DIAGNOSIS = CONFIRMED`, `COST_CAP = NOT_ESTABLISHED`.

---

## Part 1 — the architecture defects, reproduced then repaired

`tests/test_pre_repair_controls.py` reproduces each defect against the committed
predecessor bytes *before* anything is fixed, so the repair has something to be
measured against.

### 1. Runtime monkey-patching

The predecessor redirected a reviewed module's behaviour by assigning into it:

```python
propagate.refine = sys.modules[__name__]        # refine2.py:229
```

A reader of `propagate.py` sees `refine.refine(...)` and gets something else. The
call graph depended on import order, and no test could see it.

**Repaired by wiring, not patching.** `aux_propagate.cell_obligations` takes its
refinements as arguments:

```python
record = aux_propagate.cell_obligations(
    cert,
    whole_cell_refinement=refine2.refine,          # inherited, adjudicated SOUND
    node_refinement_factory=make_backend)          # the auxiliary node bound
```

`code/no_monkeypatch.py` is a static AST detector for four patterns — module
attribute assignment, `setattr` on a module, `sys.modules[...] =`, and
`globals()[...] =`. It reports this namespace **clean** and independently
rediscovers the predecessor's patch at `refine2.py:229`, which is what shows the
detector actually fires.

### 2. Non-fatal loaded-module coverage

The predecessor's certifying path called
`verify_loaded_modules_covered(strict=False)`: an uncovered certifying module
produced a note, not an abort.

**Repaired fail-closed.** `manifest.require()` runs *before* any certificate is
built and again after the science completes, and raises on an uncovered module, a
moved byte, a moved runtime version, a missing artifact, or an unpinned thread
environment. A negative control introduces a real uncovered certifying module and
asserts the run aborts.

### 3 & 4. A producer identity nothing could resolve

The predecessor computed its producer hash on the fly from the working tree, so a
record carried a 64-hex number that a verifier could not check without re-running
the predecessor's own code and trusting the answer — and every committed record
went stale, silently, the moment a bound library version moved.

**Repaired by a committed artifact.** `manifests/producer_manifest_v1.json`
holds canonical `path -> sha256` for all 51 certifying inputs plus the runtime
contract, and

```
producer_manifest_hash = sha256(canonical(manifest))
```

is carried by every certificate identity alongside the manifest's schema id and
repo-relative path. A verifier with the repository alone can read the artifact,
recompute every file hash from disk, recompute the manifest hash, and compare.

### 5. A green suite that hid all of it

The predecessor's suite passed throughout. The controls in
`tests/test_pre_repair_controls.py` run it in an isolated process and demonstrate
that it never mentions any of defects 1–4.

---

## Part 2 — runtime binding, resolved honestly

SciPy was the open question. Measured, not assumed
(`evidence/scipy_execution_probe.json`):

* **imported** on the certifying path — `rebaseguard_certify/spectral_candidate.py`
  does `from scipy.special import ndtr` at module level;
* **never called** — a `sys.setprofile` run over a representative certification
  (Layer-1 collocation and candidate solve, Arb kernel application, Bernstein
  range, order-3 auxiliary candidates) records **zero** scipy python or C calls.
  Statically, the only scipy call sites in the certifying input set are inside
  `solve_spectral_candidates`, which the CUSUM path never reaches: candidates come
  from `cusum_layer1.dyadic_candidate`.

So its *availability* is bound (the import must succeed) and its *version*
deliberately is not: `scipy_status = "AVAILABILITY_ONLY_IMPORTED_NOT_CALLED"`.
Binding a version that cannot change a certified number would manufacture a
reproducibility constraint. `python-flint`, `numpy`, the CPython major.minor, the
BLAS/OpenMP thread contract and the frozen precision are all bound and fail
closed, because all of them do change certified numbers.

---

## Part 3 — auxiliary third-derivative evidence

### The problem it solves

Every whole-cell node value in the frozen DAG is a cascade: each node's cell value
is its local residual plus operator norms times its dependencies' cell values. At
cell 321 that is where the remaining width lives:

```
S_4^(2) = 2.4577 = j0·h_4^(2) (1.093) + 2j1·h_4^(1) (1.040) + j2·h_4^(0) (0.325)
h_4^(2) = 1.679  = k0·h_3^(2) (0.769) + 2k1·h_3^(1) (0.698) + k2·h_3^(0) (0.190)
```

seeded by `rho·sup|phi''| = 0.0586` and multiplying by ≈2.98 per level. None of it
is equation defect: it is how far the true object travels across the cell while
the candidate stays fixed in `e`.

### The bound

Candidates are state-only polynomials, constant in `e`, so for
`E(e) = Xhat^(k) − X^(k)(e)` we have `E' = −X^(k+1)`, `E'' = −X^(k+2)`, and Taylor
at `e0` gives, for every node:

```
eps_cell(X^(k)) <= eps_mid(X^(k)) + rho·||X^(k+1)(e0)|| + (rho²/2)·T[X,k+2]
```

At `k = 2` the middle term needs the third derivative at the midpoint — which is
what the auxiliary certificates provide. The cascade and this bound are both
computed for every node and the **smaller is kept**: a uniform method, no per-cell
tuning, and a node where the cascade already wins keeps it.

### Why it wins

The norm-only tower massively overstates the true derivatives, because it
multiplies operator norms by candidate suprema with no cancellation. Measured at
cell 321:

| | certified candidate sup | norm-only tower | ratio |
| --- | ---: | ---: | ---: |
| `h_4'''` | 0.0394 | 19.81 | 500× |
| `S_4'''` | 0.00067 | 35.58 | 53,000× |

### The derivation

The frozen recursions differentiated three times with Leibniz — every coefficient
derived, none pattern-matched (`code/aux_certifier.py`):

```
h_1^(3) = -S_0^(2)                                       (closed form)
h_j^(3) = K_0 h_(j-1)^(3) + 3K_1 h_(j-1)^(2) + 3K_2 h_(j-1)^(1) + K_3 h_(j-1)^(0)
S_0^(3) = -He_3(u+e)phi(u+e) + He_3(l+e)phi(l+e)         (phi''' = -He_3 phi)
S_r^(3) = sum_i C(3,i) J_i h_r^(3-i),   J_i = Kz_i + e K_i + i K_(i-1)
W_(r,j)^(3) = sum_i C(3,i) K_i W_(r,j-1)^(3-i)
```

The order-3 collocation operator continues the frozen Hermite weight sequence
`phi^(i)/phi = (-1)^i He_i` at `i = 3`, on the same grid, degree, quadrature and
basis (`code/aux_collocation.py`).

### Governance

The auxiliary evidence is **nested internal support** for the cell's existing
curvature obligations: no new top-level work id, no new frozen DAG node, universe
unchanged at **17,978**. It is hashed into the parent certificate's scientific
content and bound into every unit identity as `auxiliary_evidence_hash`, so a
parent m=5 certificate is checkable down to its auxiliary derivative evidence, and
tampering with one auxiliary bound changes the parent hash.

---

## Results

See `RESULTS.md` for the per-`(cell, m)` table, the comparison against the
predecessor, and the auxiliary-evidence accounting. Counts are stated exactly:
cells 318–324 are **28** obligations, cells 318–325 are **32**.

## Governance

Unchanged and asserted by tests: the 17,978-obligation universe, cover geometry,
cell boundaries, `rho`, detector scope, `m` scope, precision (256 bits), Taylor
degree, budgets (Σ = 19/100), reserve, the 1126 CPU-hour cap, the theorem and
estimand. `PRODUCTION_ENABLED` is false, no production ran, SR is untouched, no
far-field gap claim is reintroduced, and every predecessor namespace is
byte-identical to its commit.

## Layout

```
code/         ancestry, aux_collocation, aux_certifier, aux_refine, aux_propagate,
              manifest, aux_universe, aux_certhash, aux_qualify (certifying);
              aux_audit, aux_report, no_monkeypatch, far_field_inherited (not)
manifests/    producer_manifest_v1.json          committed immutable artifact
evidence/     scipy_execution_probe.json         measured runtime binding evidence
tests/        test_pre_repair_controls.py, test_aux3.py
diagnostics/  cells/aux3_CUSUM_<n>_256.json, determinism.json, audit.json
```

## Reproducing

```
python code/manifest.py --write                       # rebuild the artifact
code/run_aux3.sh OUTDIR 318 319 320 321 322 323 324 325
cp OUTDIR/aux3_CUSUM_*.json diagnostics/cells/
code/run_aux3.sh REPEATDIR 318 323                    # determinism repeats
python code/aux_report.py --determinism REPEATDIR
python code/aux_audit.py --tests-ok yes --out diagnostics/audit.json
python code/aux_report.py --write
python -m unittest discover -s tests -p 'test_*.py'
```

Eight workers on eight cores roughly doubles the CPU seconds each cell reports,
through memory-bandwidth contention; the audit records both the contended and the
clean figures.
