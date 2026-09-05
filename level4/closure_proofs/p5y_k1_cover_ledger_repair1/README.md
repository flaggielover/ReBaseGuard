# P5Y K1 cover-ledger repair 1

A narrowly scoped repair of the two correctness defects the independent
adjudication found in the reviewed implementation at
`c0a1f40cff6974899cd44ab424591bb6a819c949`:

```text
DERIVATIVE_DEPENDENCY_SOUND = NO     ->  repaired here (single S0 charge)
WORK_UNIVERSE               = FAIL   ->  repaired here (exact resume identity)
```

Nothing else is touched. In particular this repair does **not** attempt cell
325, does **not** implement SR, does **not** implement the far-field
certificates, and does **not** revisit the cost cap.

```text
PRODUCTION_ENABLED     = false        HARD_CPU_CAP     = 1126 (unchanged)
PRODUCTION_PRECISION   = 256 bits (unchanged)
FROZEN SUCCESSOR       = untouched, byte-identical
REVIEWED IMPLEMENTATION= untouched, byte-identical to c0a1f40
CELL 325               = CURRENT_CERTIFICATE_FAILURE_ONLY (unchanged)
```

## Structure: override, do not rewrite

The reviewed implementation is **imported, not copied**. `code/prior.py` puts
`p5y_k1_cover_ledger_implementation/code` on the import path; every module here
subclasses or wraps the reviewed one and overrides only the defective part. A
self-audit check asserts that `git diff c0a1f40 -- <reviewed namespace>` is
empty.

| module | what it overrides |
|---|---|
| `repair_layer2.py` | `CellCertifier.all_residuals` -- removes the duplicate S0 remainder from the three r=0 local residuals |
| `repair_scoped.py` | the m=1 path, same correction, via the shared helper |
| `repair_universe.py` | `admit_resume_record` -- exact per-obligation identity |
| `repair_check.py` | the "charged exactly once" accounting invariant |
| `repair_compare.py` | before/after comparison of the affected quantities |
| `repair_components.py` | provenance of the Arb radii in the truncation term |
| `repair_qualify.py` | regression runner (refuses cell 325 by construction) |
| `repair_audit.py` | repair-specific self-audit |

The expensive certified work -- the Bernstein range bound on each residual
polynomial -- is reused from the reviewed pass. Only the scalar allowance is
recomputed.

## Defect 1: the closed-form S0 remainder was charged twice

`reward_allow[k]` bounds `||Sclosed_k - S_0^(k)_true||`. The reviewed code put
it inside the local F_0/D_0/H_0 residual *and* propagated it again as the
`Sclosed:k` epsS node, so `epsF = C*(deltaF + epsS)` counted it twice. The
frozen ERROR_ALGEBRA section 1 allows representation A (residual against the
fixed candidate + a separate epsS) or B (complete residual against the true
source, epsS forced to zero) -- never a mixture.

Representation **A** is adopted, because it is what every other object in the
DAG already uses: `S_r` for `r >= 1`, `h_1^(k)` and the `S_0:k` candidate all
carry their error in their own node. Only the three r = 0 residuals deviated.

`epsF = C*(deltaF + epsS)` and `epsD = C*(deltaD + k1*epsF + epsS')` keep their
exact frozen shape; STYLE_1, the complete `D_interval` and the single Taylor
derivative charge are untouched.

### Numerical effect: none, and that is the honest result

The duplicate is `reward_allow[k] ~ 4.3e-53 .. 1.5e-51`, roughly 48 orders of
magnitude below the certificate values it sits inside. The repaired certified
quantities on CUSUM cell 221 are **identical** to the reviewed ones at 256, 384
and 512 bits. Correctness here is established by the accounting invariant in
`repair_check.py`, not by a numerical improvement.

### A note on Arb radius granularity

Exact bit-equality between "reviewed allowance minus `reward_allow`" and the
recomputed allowance is **not** an available invariant. `eps_z` (the frozen
`taylor_remainder`) carries a relative radius of 2.04e-16, and Arb stores ball
radii with 30-bit precision, so two valid outward bounds of the same quantity
can differ by `~2^-30 * rad ~ 4.8e-35` -- about 1e18 times `reward_allow`.
`repair_components.py` records this. The over-removal guard is therefore stated
at a granularity the arithmetic supports (`2^-40` of the allowance), which is
still twelve orders below any real term.

## Defect 2: resume admission did not bind per-obligation identity

The reviewed `admit_resume_record` validated only global context and took no
expected unit, so a record for one obligation was admissible as any other.
`repair_universe.admit_resume_record(record, expected_unit, ...)` rebuilds the
canonical identity and requires a field-for-field match on

```text
checkpoint_hash, cells_sha256, error_algebra_sha256, backend_hash,
implementation_hash, obligation_universe_total, detector, cell_index,
unit_kind, function_or_m, left, right, e0, rho, C_upper, precision_bits,
source_certificate_hashes, unit_hash
```

`unit_hash` is **recomputed**, so a forged or stale hash cannot survive.
`source_certificate_hashes` -- required by the frozen `work.resume_identity`
list and absent from the reviewed identity -- is derived from the frozen
dependency graph, so an obligation cannot be replayed unless the exact set of
dependencies it is defined to consume is named with their own canonical hashes.

Exact quantities (`e0`, `rho`, `left`, `right`, `C_upper`) are compared in the
repository's canonical exact encoding: the frozen affine `[p, s]` rational-string
pair and reduced rational strings. A float in any exact field is a hard reject,
never a tolerance comparison.

## Running it

```bash
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python -m pytest \
    level4/closure_proofs/p5y_k1_cover_ledger_repair1/tests -q

# demonstrate the defects against the reviewed code
PRE_REPAIR_EXPECT_FAILURE=1 level4/.venv/bin/python -m pytest \
    level4/closure_proofs/p5y_k1_cover_ledger_repair1/tests/test_pre_repair_defects.py -q

level4/.venv/bin/python \
    level4/closure_proofs/p5y_k1_cover_ledger_repair1/code/repair_audit.py \
    --records level4/closure_proofs/p5y_k1_cover_ledger_repair1/diagnostics/regression
```
