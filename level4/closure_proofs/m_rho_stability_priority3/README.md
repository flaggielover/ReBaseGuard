# Level-4 Priority 3 — theorem-supported m–rho stability map

Priority 3 is a **synthesis layer**. It adds no detector theory. It takes the
two already closed derivative theorems

```text
Priority 1 (Gaussian two-sided CUSUM):  F'_{rho,m}(0) = rho(1 - GammaTilde_m)
Priority 2 (reset symmetric two-chart SR): F'_{rho,m}(0) = rho(1 - GammaTilde_m^SR)
```

and mechanically derives, per detector family and per window length, the local
first-order stability of the reference fixed point over the admissible reuse
domain `rho in [0,1]`, with an explicit evidence hierarchy that keeps
interval-certified statements separate from empirical Gaussian correspondence.

The original 49-file candidate was subsequently subjected to an independent
frozen-intake adversarial adjudication. Its self-reported verdict was not
inherited: theorem consequences, all numerical boundaries, uncertainty cells,
exact witnesses, Lean/Arb claims, provenance, figures, and repository gates
were recomputed or replayed independently. The reviewer restored literal
passing of the three locale/PATH-sensitive suites; controlled failures remain
diagnostics only and are not substitutes for passing gates.

## Headline result

| detector | evidence | `rho_c` at `m = 1, 2, 3, 5` |
|---|---|---|
| Gaussian two-sided CUSUM | theorem + Monte Carlo gain | `0.067040, 0.081534, 0.091265, 0.108385` |
| Gaussian SR | theorem + Monte Carlo gain | `0.060777, 0.074071, 0.083524, 0.099517` |
| Priority-1 finite-support witness | exact + interval-certified | `2/13` at every `m` |
| Priority-2 SR-compatible witness | exact + interval-certified | `1/3, 1/2, 3/5, 5/7` |

`rho < rho_c` is locally attracting, `rho > rho_c` is locally repelling, and
`rho = rho_c` is a first-order boundary on which linearization is silent. Every
boundary above is strictly interior to `[0,1]`, because every measured gain
exceeds `2`.

Both Gaussian rows are empirical. The two witness rows are rigorous, and they
are *not* estimates of the Gaussian rows — see `EVIDENCE_BOUNDARY.md`.

## Documents

| file | contents |
|---|---|
| `THEOREM.md` | the imported identities, the classification, the critical reuse fraction, and an audit of every gain regime |
| `PROOF.md` | proofs of all eleven statements, including the degenerate cases and the uncertainty-envelope results |
| `EVIDENCE_BOUNDARY.md` | the six-level hierarchy and exactly what is and is not certified |
| `PROVENANCE.md` | where every number comes from and which trees are read-only |
| `LEAN_CORRESPONDENCE.md` | prose-to-Lean table, declared reuse of the closed spines, axiom audit |
| `STABILITY_MAP_REPORT.md` | generated tables; do not edit by hand |
| `CLOSURE_REPORT.md` | the verdict and the gate-by-gate result |

## Artifacts

| file | contents |
|---|---|
| `configs/MAP_PROTOCOL.json` | frozen protocol: layers, grids, hierarchy, gates, tolerances |
| `results/provenance.json` | hash-verified gains, standard errors and boundaries per layer |
| `results/stability_map.json` | 304 grid cells plus 16 exact-boundary cells, with checks |
| `results/stability_map.csv` | the same cells as a flat table |
| `results/boundary_table.json` | per detector and window: regime, `rho_c`, delta SE, interval, admissibility |
| `arb/certificate.json` | 128-bit Arb certification of the two finite-support layers |
| `results/lean_compile.json`, `results/axiom_audit.txt` | Lean spine and axiom audit |
| `results/verification.json` | repository regression suites and historical diagnostics |
| `results/closure_decision.json` | the mechanical verdict |
| `figures/*.png`, `figures/figure_index.json` | publication figures and their input/output hashes |

## Figures

- `p3_cross_detector_stability_map.png` — the map itself. `m` is a discrete
  categorical axis because `GammaTilde` is known only at four window lengths;
  `rho` is the only continuous axis. The lower row zooms each detector onto its
  own boundary.
- `p3_critical_reuse_by_detector.png` — `rho_c` against `m` for all four
  layers, with transformed 95% intervals on the empirical rows only.
- `p3_evidence_grid.png` — one square per machine-readable cell, with the
  uncertainty-sensitive cells marked.

## Reproduce

```bash
bash level4/closure_proofs/m_rho_stability_priority3/reproduce.sh
```

The script rebuilds the provenance, map, figures and report from the closed
Priority-1/Priority-2 artifacts, replays the Arb certificate, runs the focused
tests, compiles the Lean spine and its axiom audit, runs the repository
regression suites, and finally derives the closure decision. Regeneration is
byte-identical; `tests/test_map_artifacts.py` asserts it.

## Scope

First-order local stability of the deterministic conditional-mean reference map
at `e = 0`, per detector family and per window length. Not global stability,
not nonlinear convergence, not stationary uniqueness, not detector-universal,
not non-Gaussian. Stage-D D2.5 remains the controlling operational result.
