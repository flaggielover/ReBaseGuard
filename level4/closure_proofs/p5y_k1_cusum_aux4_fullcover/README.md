# P5Y K1 — CUSUM Aux4 full cover

**NOT production. Not result-bearing.**

A new governed successor to `4191beb`, created because independent adjudication
returned five identity failures against Aux3 — `PRODUCER_MANIFEST`,
`STRICT_PRODUCER_ENFORCEMENT`, `RUNTIME_BINDING`, `CERTIFICATE_DETERMINISM`,
`AUXILIARY_GOVERNANCE` — and required the complete 326-cell CUSUM cover to be
**rerun** under a new producer (`CUSUM_COVER_INHERITANCE = REQUIRES_FULL_326_RERUN`).

Inherited and not re-opened: `AUXILIARY_DERIVATIVE_SOUND = YES`,
`AUX3_BLOCK_REPLAY = 32/32`, `REPOSITORY_PROVENANCE = PASS`,
`EXPLICIT_REFINEMENT_WIRING = PASS`, `FAR_FIELD = PASS`,
`COST_CAP = NOT_ESTABLISHED`. The Aux3 *science* is imported and executed
unchanged; only the identity layer is replaced.

---

## The five defects, reproduced before being repaired

`tests/test_aux3_defects.py` (20 controls) demonstrates each defect against the
committed Aux3 bytes, without mutating them.

### 1. A basename whitelist exempted an execution-relevant module

Aux3 decided coverage by file *name*:

```python
NON_CERTIFYING_BASENAMES = {..., "successor_producer.py", ...}
```

`successor_producer.py` is on the execution path — Aux3's own
`rejected_producer_identities()` imports it and puts its hash in the record,
inside the scientific hash — yet it was exempt from coverage and absent from the
manifest. A basename is not an identity.

**Repaired**: `code/tcb.py` decides membership by exact repository-relative path.
There is no basename mechanism at all, and a negative control drops a file with
the formerly-exempt name into the namespace and asserts certification aborts.

### 2. The last gate ran too early

Aux3's final `manifest.require()` sat *before* the auxiliary assembly, the
certificate construction, a lazy import and the scientific hash. Everything after
it was unguarded.

**Repaired**: `manifest_v2.final_gate()` runs **after** the scientific hash and
immediately before the atomic write. Negative controls prove a late import and a
late source mutation both abort it.

### 3. The numerical backend was not identified — and it matters

This is the one that changes numbers. The wheel's OpenBLAS is built
`DYNAMIC_ARCH`, so it picks a microkernel at *runtime*. Forcing that choice on
this host, with everything Aux3 binds held fixed:

| | |
| --- | --- |
| `OPENBLAS_CORETYPE=SkylakeX` vs `Haswell` | **62 of 240 certified dyadic candidates differ** |
| cells sampled | 0, 150, 318, 325 |
| identical across both | numpy version, python-flint version, CPython major.minor, thread pinning, precision |

`evidence/blas_kernel_sensitivity.json` records the measurement. Two hosts
carrying Aux3's exact declared identity therefore produce different
certificates — which is also the mechanism behind `CERTIFICATE_DETERMINISM = FAIL`.
Note too that `numpy.show_config()` reports the *build* target ("Haswell") while
the runtime selection here is "SkylakeX"; binding the build string would have
recorded the wrong fact.

**Repaired**: `code/runtime_identity.py` binds the runtime-selected kernel, the
OpenBLAS config string, and the **sha256 of every backend library actually
mapped** — libflint, libgmp, libmpfr and libscipy_openblas64 — plus the exact
CPython build, numpy and python-flint versions, the thread contract and the
frozen precision. The CPU model is deliberately *not* bound: it is what OpenBLAS
reads, but it is the selected kernel that changes arithmetic.

### 4. A swallowed lazy import decided a hashed field

Aux3's `rejected_producer_identities()` did `import successor_producer` inside
`try/except Exception`. On the real run that import **failed** — two namespaces
both ship a module called `ancestry`, so the wrong one won — and the failure was
swallowed. The committed records are missing the key it would have added, and
adding it changes the scientific hash. Same declared identity, different
certificate.

**Repaired**: no lazy imports on the certifying path. Rejected identities are
static: commit ids plus the Aux3 manifest hash read from a committed artifact
that is itself byte-bound. The bootstrap module is named `ancestry4`, so the name
collision cannot recur.

### 5. Three scientific fields fell outside the hash

Aux3 hashed a hand-picked include list, so `candidate_suprema`, the auxiliary
`order` and the `hermite_weight` could all be mutated with the hash unchanged.

**Repaired**: `code/schema.py` + `code/hash_v2.py` invert the rule. Every leaf
path of the record is classified; only an explicit `INCIDENTAL_PATHS` whitelist
(timings, RSS, call counters, float views of exact rationals) may be dropped, and
anything unrecognised defaults to **SCIENTIFIC**, so a new field is bound
automatically and a mistake fails closed. Measured on a real record: 2912 leaf
paths, 2554 hashed, 357 dropped, **0 unaccounted**.

---

## SciPy: enforced, not trusted

Aux3 justified excluding SciPy with a probe artifact that was never byte-bound.
The conclusion was right; the justification was not. Here:

* the probe artifact **is** byte-bound in the TCB;
* the conclusion is **re-verified independently** (`code/scipy_guard.py`);
* and it is **enforced on every cell** with `sys.monitoring` (PEP 669): the CALL
  event fires for C functions too, so `scipy.special.ndtr` cannot slip past, and
  every non-SciPy call site returns `DISABLE` so the cost decays to nothing —
  1018 call sites observed on a whole cell.

If any SciPy code ever runs, `require_clean()` aborts the certification. A
negative control calls `ndtr` inside the guard and asserts it fires.

---

## Auxiliary governance, unchanged

The `h'''` / `S'''` evidence stays nested support for the cell's existing
curvature obligations: no top-level work id, no frozen DAG node or edge, universe
unchanged at **17,978**, CUSUM cells **326**. It is now fully inside the
scientific hash and bound into every unit identity as `auxiliary_evidence_hash`.

## Layout

```
code/     ancestry4, tcb, runtime_identity, scipy_guard, manifest_v2, schema,
          hash_v2, identity4, qualify4            (certifying — in the manifest)
          aggregate_ledger, audit4, report4       (not certifying, never imported
                                                   by the certifying process)
          qualify_batch.sh                        launcher only: it starts
                                                  processes, it certifies nothing,
                                                  and every certificate is
                                                  self-verifying regardless of
                                                  how it was launched
manifests/producer_manifest_v2.json               committed immutable artifact
evidence/ blas_kernel_sensitivity.json            the measurement behind Phase 4
tests/    test_aux3_defects.py, test_aux4.py
diagnostics/ cells/, determinism.json, cost_model.json, aggregate_ledger.json
```

## Reproducing

```
python code/manifest_v2.py --write                 # rebuild the artifact
code/qualify_batch.sh DIR_A 2 318 323              # determinism repeats
code/qualify_batch.sh DIR_B 2 318 323
python code/report4.py --determinism DIR_A DIR_B
python code/report4.py --cost-model DIR_A
code/qualify_batch.sh diagnostics/cells 4 $(seq 0 325)     # the full cover
python code/aggregate_ledger.py --out diagnostics/aggregate_ledger.json --brief
python code/audit4.py --tests-ok yes --out diagnostics/audit.json
python -m unittest discover -s tests -p 'test_*.py'
```

The host has 8 logical CPUs on **4 physical cores**. Eight workers inflate
per-cell CPU by 2.04× for the same wall throughput, so the full run uses **four**
workers: identical wall time at half the CPU-hours, and CPU-hours are what the
1126-hour cap governs.
