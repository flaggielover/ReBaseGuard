# P5Y K1 final-completion campaign — checkpoint

Successor namespace to the independently validated Repair2
(`7a7df9b173e5de535c15037089fabebc687c5e6f`). Everything validated so far is
IMPORTED, never copied or edited.

```text
START_HEAD                 7a7df9b173e5de535c15037089fabebc687c5e6f
branch                     p5y-gate1-micropilots
frozen successor           byte-identical to its freeze manifest
reviewed  c0a1f40          byte-identical
repair1   4164121          byte-identical
repair2   7a7df9b          byte-identical
PRODUCTION_ENABLED         false
HARD_CPU_CAP               1126 CPU-hours (unchanged)
PRODUCTION_BITS            256 (unchanged)
Taylor degree              unchanged        cover geometry: unchanged
budgets / thresholds       unchanged        detector/m scope: unchanged
```

## Host (measured at runtime, not assumed)

```text
CPU count            8          (NOT the 64 of the historical projections)
RAM                  30.8 GiB   available 29.6 GiB
free disk            92 GiB
python               3.12.3     python-flint 0.9.0     numpy 2.5.2
safe worker count    8          measured peak RSS 202 MiB/worker
```

## What this campaign changes

Exactly one scientific object: the certified operator-norm family.

`sharp_norms.py` replaces the whole-line absolute Gaussian moments with
drift-aware ones over the actual shifted window
`W = [left - 11/2, right + 11/2]`. Both operator families collapse to the same
quantity there,

```text
||d_e^i K_e|| <= A_i(W)        ||J_i|| <= A_(i+1)(W)
A_n(W) = int_W |He_n(y)| phi(y) dy
```

evaluated in closed form (`int He_n phi = -He_(n-1) phi`, split at the known
roots of `He_n`), never quadratured. Each entry is
`min(drift-aware, reviewed whole-line, Cauchy-Schwarz)`, so it can only tighten;
an audit asserts that over all 326 CUSUM cells.

ERROR_ALGEBRA section 2 calls the whole-line moments "admissible", not
mandatory. A sharper certified bound on the same operator is not a relaxation of
anything: no threshold, budget, precision, degree, cell endpoint or Taylor
semantic is touched.

## Obligation universe (unchanged)

```text
17,978 obligations       12,198 base objects
CUSUM 326 cells          SR 316 cells
shard conservation       exact at 1 / 8 / 16 / 32 / 64 workers
cells_sha256             341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f
```

## Erratum recorded against Repair2 (not edited)

`p5y_k1_cover_ledger_repair2/REPAIR2_STATUS.md` line 6 quotes
`BACKEND_CONTRACT_HASH = 495058e3…`. That value was transcribed from an
intermediate probe taken before `rebaseguard_certify/__init__.py` was added to
the backend contract. Every machine-generated artifact — the committed
regression records, the certificate identities and `producer_manifest.json` —
consistently carries the correct `8abad284d1eb642e0e682de3eb118f1f901993ae16c939b29ab95c339b2ebf25`,
and Repair2's own test `test_stamped_producer_hash_is_the_current_one` passes.
The defect is confined to one human-typed line in a status document. Repair2 is
protected, so it is recorded here rather than corrected there.

## Phase 0 result

No new scientific result is claimed in Phase 0. State, freeze and resources are
as recorded above, and production remains disabled.
