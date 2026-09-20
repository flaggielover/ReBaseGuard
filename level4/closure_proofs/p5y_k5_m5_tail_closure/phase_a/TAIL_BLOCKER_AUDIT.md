# Campaign B, Phase A — m = 5 tail (K1 cells 305–309) blocker audit

Inputs: the adopted K1 records (export manifest `29ad1f9b…`, each record sha-checked), the frozen cover `cells.json`
(`341eb5e9…`) and the frozen Theorem K5-B. Machine-readable: `TAIL_BLOCKER_MAP.json` (sha256 `06a3d6ca…`, 40 rows,
cells 300–309 × m). No model quantity is computed here.

## What is open and why

After the theorem-TC lower-front successor, m = 1, 2, 3 pass every cell 0–309. For m = 5 exactly cells 305–309 remain
open. Every one of them fails the frozen **direct** test on the curvature penalty, not on the point enclosures:

| cell | e-cell | g(e0) enclosure | ρ·x_hi·M_R2 | Γ_k | M_R2 | M needed for Γ_k < 0 | reduction factor needed | C_upper |
|---|---|---|---|---|---|---|---|---|
| 305 | [1.6209, 1.7019] | [−0.345, −0.337] | 0.379 | +0.042 | 5.498 | 4.892 | **1.12×** | 7.73 |
| 306 | [1.7019, 1.7886] | [−0.311, −0.303] | 0.421 | +0.118 | 5.427 | 3.905 | **1.39×** | 7.23 |
| 307 | [1.7886, 1.8824] | [−0.280, −0.272] | 0.471 | +0.199 | 5.335 | 3.076 | **1.73×** | 6.68 |
| 308 | [1.8824, 1.9839] | [−0.253, −0.245] | 0.533 | +0.288 | 5.296 | 2.432 | **2.18×** | 6.17 |
| 309 | [1.9839, 2.0923] | [−0.231, −0.223] | 0.597 | +0.374 | 5.270 | 1.970 | **2.67×** | 5.78 |

The point enclosures are not the blocker: R half-widths are 2–3e-4 and D half-widths 1.7–2.3e-3, so g(e0) is resolved
to ±0.004 against |g| ≈ 0.22–0.35.

The **chain** route also fails: γ_304 ≤ Γ_304 = −0.0385, while μ_305 = H_305.lo ≈ −5.5 and (x²_305 − x²_304)/2 = 0.135,
so U_305 = γ_304 − μ_305·0.135 ≈ +0.70 > 0. The chain needs μ_k ≥ 2γ_{k−1}/(x_k² − x_{k−1}²) ≈ −0.29 at cell 305.

## Where M_R2 comes from, and how far it is from the truth

M_R2 = mag(R2_interval) with R2_interval = Σ_{r<5}(1/5)[Ĥ_r(a) ± eps_cell_refined(H:r)] + W terms; the refined per-object
eps at cell 305 are 1.80, 3.32, 5.00, 6.59, 8.45 (r = 0..4), so the mean ≈ 5.0 sets M.

NON-CERTIFIED diagnostic (adopted record midpoints only; central differences of the recorded R' centres, which agree
with the recorded R'' centres to 3 decimals): the true R'' on the tail is **−0.27 (cell 305) … −0.09 (cell 309)**, i.e.
the certified M is ≈ 20–55× the truth. The obstacle is the width of the whole-cell curvature enclosure, not the value.

Allowed radius for a closure by the direct test (M_needed − |R''|_est): **4.62, 3.69, 2.91, 2.31, 1.87** for cells
305…309. Any route that certifies the whole-cell R'' to within ≈ 1.9 at cell 309 (and looser at 305–308) closes the tail.

## Residual data that a tightening route would use (per cell, from the records)

ρ = 0.041…0.054 (much larger than on the lower front, 2.7e-4), C_upper = 5.8…7.7 (much smaller than the front's 1011–1177),
δ_mid(F_r) ≈ 1e-7…4e-5, δ_mid(dF_r) ≈ 4e-7…1.5e-4, δ_mid(H_r) ≈ 5e-6…4e-4, whole-cell δ_cell 8e-3…7e-2 and candidate
envelopes 0.15…3.4. The whole-cell residuals are ρ-dominated exactly as on the lower front, which is why the adopted
whole-cell refinement leaves M ≈ 5.3.
