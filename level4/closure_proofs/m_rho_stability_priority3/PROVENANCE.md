# Priority-3 provenance

Every number in this campaign is either (a) read mechanically out of a
hash-verified Priority-1/Priority-2 JSON artifact, or (b) recomputed in exact
rational or interval arithmetic from a hash-verified frozen witness file. No
value is transcribed from a report, a table or a figure.

## Frozen new input

| file | sha256 |
|---|---|
| `configs/MAP_PROTOCOL.json` | `8a40a23905724fa55bdcc0c01e1d8e38035c1ea64497250f635703faa2d440b3` |

The candidate labels this protocol as frozen before any map output. Because all
49 candidate files arrived together as one uncommitted intake, the independent
review cannot authenticate that temporal claim from Git history. What can be
and is proved is byte-level immutability from reviewer intake onward:
`manifest.json` pins the protocol hash and `derive_closure.py` refuses to close
if the protocol, provenance artifact, map, and certificate disagree on it.

The reviewer separately froze the complete 49-file candidate intake at
aggregate SHA-256
`41f82b34481bc2427d16a9534affb9fdd0c6efa328db4467d96f0f8f193bc319`.
No scientific conclusion depends on the temporal status of the display grid:
the continuous boundary is derived analytically, and the grid cells are
descriptive evaluations of that boundary rather than a fitted threshold.

## Consumed upstream artifacts

All ten are pinned by sha256 in `manifest.json` and re-checked by
`provenance.verify_upstream_hashes`, by `tests/test_integrity.py` and by
`derive_closure.py`.

| artifact | role |
|---|---|
| `m_gt_1_priority1/results/numerical_correspondence.json` | Gaussian CUSUM gains and batch SEs |
| `m_gt_1_priority1/certificates/WITNESS.json` | exact finite-support witness paths |
| `m_gt_1_priority1/certificates/certificate.json` | recorded exact gains for replay |
| `m_gt_1_priority1/results/closure_decision.json` | confirms Priority 1 is CLOSED |
| `m_gt_1_priority1/manifest.json` | Priority-1 frozen-input record |
| `sr_derivative_priority2/results/numerical_correspondence.json` | Gaussian SR gains and batch SEs |
| `sr_derivative_priority2/certificates/WITNESS.json` | exact SR-compatible witness paths |
| `sr_derivative_priority2/certificates/certificate.json` | recorded exact gains for replay |
| `sr_derivative_priority2/results/closure_decision.json` | confirms Priority 2 is CLOSED |
| `sr_derivative_priority2/manifest.json` | Priority-2 frozen-input record |

## Pointer discipline

| layer | value | pointer |
|---|---|---|
| `GAUSSIAN_CUSUM_FROZEN` | `GammaTilde_m` | `score.gamma_mean` |
| `GAUSSIAN_CUSUM_FROZEN` | `SE` | `score.slope_se` (the score slope is `-GammaTilde`, so the two standard errors coincide) |
| `GAUSSIAN_SR_FROZEN` | `GammaTilde_m^SR` | `final.gamma` |
| `GAUSSIAN_SR_FROZEN` | `SE` | `final.gamma_se` |

The window grid is not taken from this campaign's protocol alone: the loader
asserts that the upstream `protocol.m_grid` equals `[1,2,3,5]` and raises if it
does not, so no `m` value can be synthesised.

## Witness recomputation and replay

`provenance.exact_witness_gamma` evaluates

```text
GammaTilde_m = sum_omega p(omega) * A_m(omega) * T_tau(omega),
A_m = (1/min(m,tau)) * sum over the last min(m,tau) increments,
```

in `Fraction` arithmetic, keeping the random denominator and the terminal
increment. For `m in {2,3,5}` — the grid the two closed packages certified —
the result must equal the recorded exact string or the loader raises. It does:

| layer | m=1 | m=2 | m=3 | m=5 |
|---|---|---|---|---|
| CUSUM witness | `15/2` (new) | `15/2` | `15/2` | `15/2` |
| SR witness | `4` (new) | `3` | `8/3` | `12/5` |

`m=1` is new Priority-3 evidence: the same frozen witness, the same window
convention, a window length the earlier packages simply did not evaluate. It is
labelled `P3_NEW_EXACT_FROM_FROZEN_WITNESS` in every artifact and is never
merged into the replayed rows.

## Protected trees

`manifest.json::protected_trees_read_only` lists the eight trees Priority 3
reads and never writes, including both source campaigns, the historical SR
package, the D4 phase map, the earlier `m_gt_1` tracks and Stage D.
`tests/test_integrity.py` asserts `git diff --quiet HEAD` on each of them and
additionally asserts that the entire working-tree change set lies inside
`level4/closure_proofs/m_rho_stability_priority3/`.

## Inherited conventions

| convention | value | inherited from |
|---|---|---|
| boundary tolerance | `1e-12` | `d4_phase_map/src/rebaseguard_d4/config.py` |
| `z95` | `1.959963984540054` | `d4_phase_map/src/rebaseguard_d4/config.py` |
| admissible domain | `rho in [0,1]` | Stage C / Stage D / D4 |
| window | `w_m = min(m,tau)`, denominator `w_m`, terminal increment included | P1 and P2 protocols |
| alarm / stopping | inclusive post-update; ordinary `tau` from `t=1` | P1 and P2 protocols |
| class vocabulary | `LOCALLY-STABLE` / `BOUNDARY` / `LOCALLY-UNSTABLE` | D4 phase map |

`tests/test_integrity.py` reads the D4 config source and both upstream
protocols and asserts these values still agree, so a silent redefinition
anywhere would fail the focused suite.

## Relationship to the D4 phase map

`d4_phase_map` is the earlier single-detector CUSUM stability map built on
Track 1B, over a much wider `m` grid and its own Gamma campaign. Priority 3
does not modify it, does not consume its numbers, and does not supersede it. It
reuses D4's classification vocabulary and numerical conventions so that the two
maps can be read side by side, and adds what D4 does not have: a second
detector family, an exact/certified layer, and a mechanical evidence hierarchy.
