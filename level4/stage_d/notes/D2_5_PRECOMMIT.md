# D2.5 — monitoring-bridge design pre-commitment

**Written 2026-08-22, BEFORE any D2.5 data was generated.** `STAGE_D_PROTOCOL.md`
(`925adecf…`) fixes the D2.5 *question* — does the `Gamma_m` crossing predict an
operational change — and the *metrics*, but not the `m` values, replicate count
or shift sizes. Those are committed here first. This note constrains; it loosens
nothing and changes no criterion.

## Reuse fraction

`rho = 1` (full reuse). This is forced, not chosen: `rho_c = 1/(Gamma_m − 1)`
equals 1 exactly when `Gamma_m = 2`, so the `Gamma_m = 2` crossing *is* the
point where full reuse changes local stability. Any other `rho` would test a
different boundary.

## Grid

`m ∈ {10, 20, 50, 65, 75, 90, 100}` — four below the D2.2 bracket
(`m* ∈ [50, 75]`, interpolated 72.19), three above. `65` and `90` are additions
recorded as such. All seven are reported; none may be dropped.

## Design

* `n_replicates = 20,000`; `n_cycles = 80`; `burn_in = 30` cycles discarded.
* Replicates advance in continuous lockstep — each rebaselines on its own alarm —
  so the cost is `O(cycles x ARL)` steps, not `O(cycles)` full simulations.
* Stage D convention throughout: frozen stopping rule with **no minimum dwell**,
  truncated window `w = min(m, tau)`, `e_{j+1} = rho*(e_j + zbar_m) + (1-rho)*fresh`.
  Stage C's chain implements Stage A's dwell and is therefore **not** reused.
* Statistical unit: the **replicate** (protocol §6 for multi-cycle quantities).

## Metrics (all five reported at every m)

1. in-control cycle ARL, `E[tau]` over post-burn-in cycles;
2. stationary reference MSE, `E[e^2]`;
3. lag-1 autocorrelation of `e_j`;
4. alarm alternation: lag-1 autocorrelation of the alarm direction `±1`;
5. baseline-normalised discrimination `R_Delta = E[tau_Delta] / E[tau_0]`,
   shift applied at cycle 30, `Delta ∈ {0.5, 1.0}`.

## How the verdict is read

A crossing with operational content should show a **transition in these metrics
localised near `m* ≈ 72`** — not merely monotone drift across the whole grid.

**Committed in advance:** smooth monotone variation with no feature near `m*`
will be reported as *the boundary is mathematical, not operational*, exactly as
the protocol's D2.5 row requires. A phase-transition narrative will not be
constructed from monotone curves, and no metric will be selected after the fact
for showing the sharpest change.
