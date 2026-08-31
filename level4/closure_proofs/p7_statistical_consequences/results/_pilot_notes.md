# P7 runtime / variance pilot (informal, kept for provenance)

Run before `EXPERIMENT_DESIGN.md` was written. Not production evidence; the
production numbers supersede every figure here.

## What the pilot measured

1. `A(e)` and `g_m(e)` on `e in {0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0}`,
   `n = 60,000` per point, both detectors.
2. The chain at `n_rep = 2000`, `n_cycles = 24`, `burn_in = 10`, for
   `m in {1,5}`, both detectors, ten reuse fractions.

## What it established (and therefore what the design had to accommodate)

* **Runtime.** A chain cell costs 1--4 s at pilot size; the chain is *cheaper*
  than the nominal ARL suggests because the degraded reference shortens every
  cycle. Production size (`n_rep = 5000`, `n_cycles = 50`) is ~2--6 s per cell,
  so the full 104-cell matrix is affordable and no adaptive pruning was needed.
  The response curves are the expensive half (`n = 4x10^5` near `x = 0`).
* **Variance.** Across-replicate `SE(ARL)` at pilot size was ~1.4% of the mean;
  production size gives ~0.4%. Effects of interest at `rho = 1` are tens of
  percent, so precision is not the binding constraint. The binding constraint is
  resolving a *knee* near `rho_c`, which is why the ladder is dense there.
* **`g_m` slope at the origin** matched `-GammaTilde` from P3 to within Monte
  Carlo error, confirming the P7 simulator measures the P1/P2 object.
* **`g_m` saturates.** `|g_m|` departs from its tangent by 10% already near
  `e ~ 0.05` and flattens by `e ~ 0.25`. This is what motivated measuring the
  linearisation radius `r_lin` as a first-class quantity.
* **The fresh control is not a clean reference.** `rho = 0` still injects
  `N(0, 1/m)` reference noise, so the `rho = 0` chain ARL is far below the
  nominal `A(0)`. This is why P7 reports **two** controls and never quotes an
  absolute ARL loss as a reuse effect.
* **No visible feature at `rho_c` in the pilot**, and a mildly *non-monotone*
  ARL in `rho`. Both were promoted to pre-committed claims (C2, and the
  exploratory non-monotonicity note) rather than discovered afterwards.

## Defects the pilot and first production pass exposed, and their fixes

| defect | effect | fix |
|---|---|---|
| `int(round(x*1e6))` negative for the symmetry-check points | `SeedSequence` rejected negative entropy; the run aborted | sign is passed as a separate non-negative entropy word |
| `hash(detector) % 97` in the seed | Python salts `hash` of a `str` per process, so **no run was reproducible** | fixed `DETECTOR_CODE = {"cusum": 11, "sr": 13}`; every production result was regenerated after the fix, and `tests/test_reproducibility.py` forbids `hash(` in the campaign source |
| response-curve grid stopped at `|x| = 3` | up to 7% of the delay integrand `A(e-Delta)` was clamped at `m=1, rho=1`, biasing the delay identity by up to 6% (`z = -4.05`) | grid extended to `|x| = 12`; all eight validation cells then agree within `1.1` SE |
| `ResponseCurves.g` was both an attribute and a method | the interpolant was shadowed by the raw array | raw grid renamed `g_grid` |
