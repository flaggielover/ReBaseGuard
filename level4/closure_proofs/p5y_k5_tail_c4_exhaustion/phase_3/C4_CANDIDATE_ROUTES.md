# Phase 3 — candidate routes, in the order the campaign was told to prefer them

Producers: `code/c4_lower_bound.py` (route L), `code/c4_routes.py` (all routes, and the diagnostics).
Evidence: `evidence/phase3/C4_ROUTES.json`.

## Summary table

| # | route | class | new scientific value? | kernel calls | bound at 308 | bound at 309 | status |
|---|---|---|---|---|---|---|---|
| 1 | **L — ladder/Wald minorant** | exact analytic inequality | **no** | **0** | 3.512734 | **3.297250** | **SELECTED** |
| 2 | R4 — `1/D` from `D_mid` | recombination of existing artifacts | no | 0 | 1.051130 | 1.041023 | evaluated, insufficient |
| 3 | R1 — taboo defect inversion | transform of an existing certified bound | yes | re-run of `certify_block` | — | — | rejected |
| 4 | R2 — whole-kernel defect inversion | transform of an existing certified bound | yes | re-run | — | — | rejected |
| 5 | R3 — truncated Neumann series | certified operator inequality | yes | n per cell | — | — | rejected |
| 6 | R5 — two-sided `tau_a` certificate | certified operator inequality | yes | new fit + certification | — | — | rejected here, recommended to a successor |

Thresholds to beat: **4.375228833136** at 308, **3.214236022678** at 309. Cells 306 and 307 have no threshold —
`A0` is not their blocker (Phase 1 §5).

## Route L, the one that is used

    E_a[tau]  >=  H / E[(|z| - K)^+],    z ~ N(e, 1) in law for |z|,  H = 5,  K = 1/2.

Proof in the module docstring of `code/c4_lower_bound.py`. In one line: the reflected CUSUM increases by at most
`(|z| - K)^+` per step, the alarm needs `H`, and Wald turns that pathwise inequality into an expectation.

* **Assumptions:** the frozen geometry; `K > 0`; the start is the atom; `E[tau] < infinity`, which Lemma T already
  gives (`E_x[tau] <= C_T`).
* **Domain:** one drift, any point of the closed cell. Evaluated at `e_lo`, which is optimal for this route because
  `E[(|z| - K)^+]` is increasing in `e`.
* **Inputs:** `H` and `K` read from the pinned frozen producer; `e_lo` from the cover ledger, cross-checked against
  the C1 registry's own `e_lo`. Nothing else.
* **Arithmetic:** `fractions.Fraction` with outward rounding onto a `2^-320` grid; `phi`, `Phi`, `pi` and
  `sqrt(2 pi)` built from series with proved and run-time-checked remainder bounds. No float reaches a certified
  value, and no special-function library is called.
* **Independence:** it uses no registry constant, no candidate polynomial and no Arb certificate.

**Result** (`evidence/phase3/C4_ROUTES.json`), with the load-bearing test `Gamma(B, 0, 0) >= 0`:

| cell | certified `E_a[tau] >=` | `Gamma` at that A0, A1 = A2 = 0 | excluded? |
|---|---|---|---|
| 306 | 3.959880291 | −0.143881163 | no — and cannot be: `A0` is not its blocker |
| 307 | 3.734070431 | −0.092985288 | no — and cannot be: `A0` is not its blocker |
| 308 | 3.512733596 | −0.040467543 | **no** |
| 309 | 3.297250282 | **+0.004661130** | **yes** |

## Why the rejected routes are rejected, and why rejecting them costs nothing

**R1 and R5 are the sharp ones.** R1 inverts Lemma T on the committed taboo candidate:
`w = Ghat 1 + Ghat g` exactly, with `g := w - 1 - Khat w >= 0`, and `(Ghat g)(a) <= tau_a sup_X g`, so
`tau_a >= w(a) / (1 + sup_X g)`. The committed taboo proposals are unshifted (`beta = 0`, `alpha = 6/5`), so
`sup g` should sit near 0.2 and the bound near `tau / 1.2 / D_mid_hi` — materially better than route L. R5 is
better still. **Both require a new operator certification**: the frozen certifier records `inf_X` of the defect and
discards `sup_X`, and `python-flint` is not installed on this host in any case.

They are rejected rather than pursued because **neither can change the verdict on a single cell**:

* at 309, route L already excludes, so a sharper bound adds nothing to the result;
* at 308, no bound can exclude, because the threshold is above the truth (Phase 1 §5);
* at 306 and 307, `A0` is not the blocker at all.

The set of cells this campaign can discharge is therefore `{309}` under route L and `{309}` under any route. Route
L is not a compromise forced by the compute constraint; it is sufficient.

**R2** is strictly weaker than R1: the committed whole-kernel proposal is shifted by `beta = 2`, so its defect
carries `2 h_1` and the inversion loses more than the route gains. **R3** needs `n` kernel applications per cell
with no advantage over R1. **R4** is the only route that needs literally nothing new, and it is reported with its
numbers (≈1.04–1.08) rather than waved away.

## Diagnostics recorded at this point, and disclosed in the gate

Two independent committed float estimates of the true `E_a[tau]` at each cell midpoint — one from the unshifted
taboo candidate (`tau / alpha / d0`), one from the whole-kernel proposal's `float_sup_taboo_grid` — agree to
between 1.4e-7 and 1.1e-6:

| cell | from taboo candidate | from whole-kernel grid |
|---|---|---|
| 306 | 4.729933563 | 4.729933369 |
| 307 | 4.444490710 | 4.444490571 |
| 308 | 4.174300305 | 4.174300818 |
| 309 | 3.920786171 | 3.920787285 |

**Measured, not asserted.** They are candidate values, not certified bounds. Nothing in the gate, the certificate
or the verdict depends on them. They are recorded because they are what tells the campaign that cell 308 is out of
reach for *every* route, and because a successor should not spend a certification run rediscovering it.
