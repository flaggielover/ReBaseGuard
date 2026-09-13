# CUSUM K1 cover: successor governance prefreeze (no launch)

## Route comparison

| criterion | Route A: restore historical Aux4 runtime | Route B: governed successor on a named current host |
|---|---|---|
| provenance | keeps the adjudicated Aux4 identity (`f85bd92c…`, contract `d49f0437…`) and its 2 cells | new producer identity (manifest v3). Aux4 records stay immutable history and are never composed. |
| scientific equivalence | bit-continuation of Aux4 | the 58 science files stay byte-identical; only the runtime identity changes. A different OpenBLAS kernel changes dyadic candidates (Aux4 measured 62/240 differ between SkylakeX and Haswell), giving **different but equally rigorous** certificates. The cover must be homogeneous under one identity. |
| operational fragility | **High.** Needs CPython `3.12.3 (main, Jul 15 2026, 23:46:41) [GCC 13.3.0]`, glibc 2.39 and the SkylakeX kernel. Only AWS selects SkylakeX, and AWS's apt-managed system Python was already rebuilt by unattended upgrades (Aug 31 build). Restoring means downgrading and holding the system interpreter on the host whose `level4/.venv` serves the **live PS1 campaign**, which is forbidden while PS1 runs and a provenance hazard afterwards. Vultr cannot select SkylakeX at all (no AVX-512). | **Moderate on Vultr-02.** uv-managed standalone CPython 3.12.3 (Clang 17.0.6), not apt-managed; Haswell kernel; glibc 2.41 is apt-managed and `apt-daily-upgrade.timer` is enabled, so it must be bound and a host guard must fail closed on drift. Fully isolated from the live PS1 host. |
| cost | saves 2 cells ≈ 1.27 CPU-h; only possible on AWS after PS1 (~15 days) and its deployment gate | +2 cells ≈ 1.27 CPU-h, plus qualification ≈ 2.5 CPU-h; runs on idle Vultr (4 physical cores ≈ 52 h wall) |
| known successor defect to repair | — | Aux4 `runtime_identity.backend_libraries()` globs relative to the repository root, so a venv outside the tree binds `{}`. The successor must bind backend libraries by **absolute resolved path and sha256**. |

```text
CUSUM_RECOMMENDED_ROUTE = NEW_SUCCESSOR   (named host rebaseguard-vultr-02; runtime contract bound at prefreeze)
CUSUM_SUCCESSOR_REQUIRES_REPRODUCING_EXISTING_2_CELLS = YES
   (the Aux4 ledger admits only its own identity and adjudication requires REQUIRES_FULL_326_RERUN; cells 318 and 323
    are re-produced as fresh-process determinism controls in qualification and again as production cells)
```

## Cost projection and cap

- Measured basis: Aux4 `cost_model.json`, cells 318 and 323, 4 workers on 4 physical cores. Mean 2,270.1 CPU-s/cell, worst 2,278.1.
- Projection: `326 × 2270.1 s = 205.6 CPU-h` (mean), `326 × 2278.1 s = 206.3 CPU-h` (worst).

The cap formula is the frozen PS1 method (`p5y_k1_ps1_production/code/make_constants.py`), re-used term for term rather than invented:

```text
c_max  = worst measured CPU-h per cell            N = 326 cells      W = workers (physical cores) on the bound host
P      = 1.10 · N · c_max                          (10% measurement margin)
R      = ceil_0.5(1.25 · c_max)                    (per-cell reservation)
INFL   = W · R                                     (full pool in flight at the last admission)
RETRY  = 0.03 · N · R                              (≈3% of cells torn once and re-run)
OVH    = 0.02 · P                                  (supervisor/launcher/probe overhead)
CAP    = ceil_50( 1.15 · (P + INFL + RETRY + OVH) )   (1.15 = frozen lifecycle invariant factor)
```

With the current basis (`c_max = 2278.1 s = 0.63281 CPU-h`, `W = 4`):
- `P = 226.93`, `R = 1.0`, `INFL = 4.0`, `RETRY = 9.78`, `OVH = 4.54`
- `1.15 × 245.25 = 282.03`, so **CAP = 300 CPU-h**
- effective reserve `300 / 206.3 = 1.45`

Why these reserve terms are defensible:

| term | evidence |
|---|---|
| RETRY 3% | Retry and tear history: PS1 generation 1 lost 92.32 CPU-h to infrastructure tears against a 5,694 CPU-h basis (1.6%), and the frozen per-cell tear limit is 3. The 3% allowance covers the observed rate with margin. |
| no production-shape factor | PS1's ×1.2265 came from changing production shape (patch-outer → cells-outer). Aux4 was measured in its production shape (one worker per physical core), so the factor does not apply. |
| 10% measurement margin | Covers a 2-cell sample. Those cells (318, 323) are the largest-ρ "difficult block", so the sample leans conservative. |
| 1.15 invariant | Frozen PS1 lifecycle invariant factor. |
| cross-check | The effective 1.45 is close to the historical `CHECKPOINT_S` β = 1.5. |

**Requalification rule (frozen formula, not frozen number).** On the successor host, qualify cells 318 and 323 twice each in fresh processes. Set `c_max` to the maximum measured CPU-s per cell over those four runs, and `W` to the host's physical cores. Recompute `CAP` with the same formula **before** production. `CAP` is never raised after production starts.

```text
CUSUM_PROJECTED_CPU_HOURS = 205.6 (mean) / 206.3 (worst), Aux4-host basis, to be requalified on the successor host
CUSUM_PROPOSED_CPU_CAP    = 300 CPU-h (current basis)
CUSUM_CAP_DERIVATION      = ceil_50(1.15·(1.10·N·c_max + W·ceil_0.5(1.25·c_max) + 0.03·N·ceil_0.5(1.25·c_max) + 0.022·N·c_max))
CUSUM_READY_FOR_PREFREEZE = YES
```

## Prefreeze content, fixed before any successor result

1. **Namespace and identity.** New successor namespace. Producer manifest v3: the Aux4 science file list byte-identical, identity layer repaired (absolute backend-library binding plus host name), and the K1 record schema unchanged, including the per-m `R_interval`/`D_interval`/`M_R2` fields the frozen K4 checkpoint reads.
2. **Runtime contract** bound on `rebaseguard-vultr-02`:
   - CPython 3.12.3 (Clang 17.0.6, uv standalone), glibc 2.41, numpy 2.5.2, python-flint 0.9.0;
   - OpenBLAS 0.3.34 runtime corename **Haswell**;
   - 256 bits, thread contract = 1;
   - library sha256 by absolute path.
3. **Qualification (non-production).**
   - Cells 318 and 323 in two fresh processes each; pass iff the scientific hashes are identical within the successor host.
   - A cross-kernel comparison against the Aux4 SkylakeX records is **informational only**, never a pass criterion.
   - Cost is measured for the cap rule.
4. **Host guard.** Pre-run and per-cell runtime-contract comparison that fails closed on drift, including glibc and apt timers.
5. **Production.** All 326 frozen cells under one identity. Accounting and the cap invariant follow the PS1 lifecycle pattern.
6. **K4 attestation output.** `rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1` with `cells_verified`, `all_scientific_hashes_verified`, `producer_identity_hash` and `producer_checkpoint_sha256`.
7. **K5.** Not coupled to this K1 campaign (see K5_TARGET_AND_THIRD_ORDER.md §4).

Not done here: building the successor code, running qualification or production, or the actual freeze commit.
