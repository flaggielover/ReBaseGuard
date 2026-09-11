# P5Y K1 SR O9 T3/T4/T5: T5_ONE_REAL_SR_CELL_28_OF_28_PASS

**Scope: scientific qualification only.** This result is NOT K1 closure and NOT a production authorization or
readiness claim. The 316-cell campaign was not started.

The authoritative record is `config/T345_RECORD.json` (sha256 `509cf1dd8fe1ec467cf7c5ea26a15b1beefa5436731a66191cdffb6f7ee0fa0b`). The parent is T2 `1bd7a3f` (tag
`p5y-k1-sr-o9-t2-per-patch-closed`), which is unchanged, as are all predecessor namespaces.

**One real SR cell, cell 150, achieves 28/28 frozen obligations PASS.** The bounded representative set of cells
0, 150, 250, 275, 313 and 315 was completed over all 3,994 patches before T5 was finalized. It exposes a
high-drift regime in which the frozen B_cover does not close under the frozen refinement architecture (see below).

## Determinism (frozen aux4 classifier; only INCIDENTAL_RUNTIME leaves may move)

| comparison | mode | scientific leaves moved | incidental leaves moved |
|---|---|---|---|
| `replay_patches_c0_matched.json` | patches | 0 | 4 |
| `replay_patches_c150.json` | patches | 0 | 20 |
| `replay_patches_c250_matched.json` | patches | 0 | 4 |
| `replay_patches_c275_matched.json` | patches | 0 | 4 |
| `replay_patches_c313.json` | patches | 0 | 20 |
| `replay_pipeline_c0.json` | pipeline | 0 | 0 |
| `replay_pipeline_c150.json` | pipeline | 0 | 0 |
| `replay_pipeline_c313.json` | pipeline | 0 | 0 |

## Method: frozen machinery only

- **T3 producer** (`code/t3_patch.py`). It runs the T2-closed certifier path (full 63-node DAG, O9 core, contracted
  endpoint strips, repeated-multiplication raw shift, P1 Lagrange factor) at the two drift modes the frozen algebra
  requires:
  - **mid:** `e = e0`, which gives R_interval, D_interval and the midpoint error chain.
  - **cell:** `e = [left, right]` as one Arb ball. By inclusion isotonicity this bounds every e in the cell. It feeds
    the H and W'' chains and the crude seeds.

  On the reset patch (0,0), every operator image is also evaluated at x0 = (0,0), the patch's exact corner. Each
  exported bound is the 256-bit certified upper endpoint rounded up to binary64. The midpoint mode reproduces the T2
  closure records on every compared node.
- **T3 aggregation** (`code/t3_aggregate.py`):
  - takes the sup over all 3,994 frozen live patches, which is legitimate for a sup norm; nothing is averaged or sampled;
  - records per-channel maxima of the F certificates, all per-patch local gates, the x0 image values, and
    geometry/identity conformance against the T2 universe table;
  - treats a missing or non-finite patch as a failure.
- **T4** (`code/t4_cell.py`) uses, unchanged:
  - `depgraph.ErrorDAG`, traversed twice (mid and cell) over the frozen SR equation map with every operator
    application resolved;
  - `sr_operators.one_step_norms`, the frozen per-cell `C_upper`, and `sr_refine.refine_cell` (SR midpoint/whole-cell
    refinement);
  - `assembly.assemble` and `assembly.curvature_bound`, and `ledger.cell_ledger` (STYLE_1).

  Two conventions follow the frozen rules:
  - The `const:1` terms (h_1 and e·h_1) and the r = 0 closed forms are INCLUDED in the certified residual
    (ERROR_ALGEBRA §1), so they carry no separate input error.
  - Terminal cell 315 (ρ = p + s·c_SR) uses the same formulas and gates, with ρ carried as its Arb enclosure.
- **T5** (`code/t5_obligations.py`):
  - the 28 frozen units, order and dependencies come from repair2 provenance and repair_universe, and match the frozen
    `universe.work_ids` exactly;
  - certificates are built bottom-up with the hashes of their dependencies, and the chain is re-verified;
  - every obligation has explicit governing gates, and no status comes from a certificate merely existing.

## Cell 150 (target): 28/28

**T3.** All 3,994 live patches present in both drift modes. Every bound is finite, geometry and identities conform to
the T2 universe, every F local gate passes on every patch, and all 18 image values are present at x0.

**T4.** All four m pass. Every top-level and nested gate passes, and the target interval lies strictly inside (−2, 2).

| m | B_cover / (1/20) | nominal ρ·\|D\| | curvature ρ²·M_R2/2 | M_R2 | certified R_m(e0) |
|---|---|---|---|---|---|
| 1 | 7.58% | 3.3e-3 | 3.75e-4 | 1,423 | [−1.41681, −1.41587] |
| 2 | 6.01% | 2.56e-3 | 3.45e-4 | 1,309 | [−1.15194, −1.15112] |
| 3 | 5.20% | 2.17e-3 | 3.31e-4 | 1,256 | [−1.01330, −1.01250] |
| 5 | 4.26% | 1.71e-3 | 3.20e-4 | 1,212 | [−0.84216, −0.84141] |

The frozen SR refinement is essential. It contracts at κ ≈ 0.50 in about 31 iterations, taking eps_H from about 2e6
to about 1.1e3. Without it the cover would be 8.8–12× over budget.

**T5.** 28/28 PASS. The obligation IDs equal the frozen universe (`universe.work_ids`), the provenance chain is
re-verified by recomputation, and every obligation passes its own governing gates.

## Determinism
- **Patch records:** 10 cell-150 patches re-executed in a fresh process. 0 scientific leaves moved; the 20 moved
  leaves are all CPU seconds or RSS (frozen aux4 classifier).
- **Pipeline:** T3 aggregation, T4 and T5 for cell 150, and T3 and T4 for cell 0, re-run from the same inputs.
  0 leaves moved.
- **Disclosed defect, fixed:** the first aggregator hashed whole shared chunk files that were still growing, so a
  cell-0 replay moved 30 provenance leaves while the content was identical. The aggregator now hashes the records it
  consumes. The superseded replay is kept in `evidence/replay/superseded_whole_file_provenance/`.

## Cost (measured on this host)
Cell 150 needed 55.4 CPU-h for T3 (both drift modes, run on its own), about 50 CPU-s per patch at 30-way load on
32 vCPU, with a peak RSS of 102 MiB per worker. T4 and T5 take minutes. Scaled by 316 cells, the estimate is about
17,500 CPU-h, roughly 15× the 1,126 CPU-h cap. This is an estimate only, not a campaign measurement.

Tile mode, where one process runs several cells per patch and reuses the e-independent PanelShared tensors through
the committed cache, gave:

| cell | CPU-h | mean CPU-s per patch | peak RSS |
|---|---|---|---|
| 0 | 55.30 | 49.8 | 108 MiB |
| 250 | 48.96 | 44.1 | 108 MiB |
| 275 | 48.86 | 44.0 | 108 MiB |

That is about 51 CPU-h per cell, only 8–12% below the fresh single-cell run. Cross-cell sharing therefore does not
change the conclusion: the full 316-cell campaign would need roughly 16,000–17,500 CPU-h under the current
architecture, well above the 1,126 CPU-h cap. The production block size is NOT frozen.

## Representative set: all six cells complete over 3,994 patches

T3 passes for every cell: the aggregation is complete, finite, conforming and deterministic.

| cell | e0 | ρ | C_upper | B_cover / (1/20), m = 1 / 2 / 3 / 5 | T4 |
|---|---|---|---|---|---|
| 0 | 2.6e-4 | 2.6e-4 | 1,206 | 9.10% / 7.68% / 6.87% / 5.85% | PASS ×4 |
| 150 | 0.127 | 7.3e-4 | 431 | 7.58% / 6.01% / 5.20% / 4.26% | PASS ×4 |
| 250 | 0.506 | 5.4e-3 | 57.6 | 21.3% / 31.1% / 40.7% / 64.9% | PASS ×4 |
| 275 | 1.005 | 0.0175 | 17.9 | 95.1% / 2.06× / 3.17× / 5.90× | PASS m = 1; FAIL m = 2, 3, 5 |
| 313 | 6.24 | 0.157 | 2.00 | 33.4× / 1,084× / 1,595× / 2,174× | FAIL ×4; target gate also fails |
| 315 (terminal) | 6.73 | 0.0227 | 2.00 | 30.1% / 9.53× / 13.25× / 16.43× | PASS m = 1; FAIL m = 2, 3, 5 |

## Regime finding: B_cover does not close at high drift under the frozen refinement

Every failure is in the curvature child ρ²·M_R2/2. The nominal ρ·|D| and the derivative uncertainty stay small in
every cell. The dominant input is the cell-uniform H residual δH_cell (the residual of the constant-in-e candidate
Ĥ_r over the whole drift interval), which grows with the cell width 2ρ:
- 0.5–1.1 at cell 150;
- 27–1,330 at cell 315;
- 57–2,630 at cell 313.

So `C·δH_cell` sets eps_H_cell. At cell 313 the refinement stops after one iteration, because that constant term,
not the C-tower, is the binding one.

This is the same class of failure the CUSUM lane recorded for its large-ρ cells 318–324: the certificate is too
loose. It is not a scientific counterexample. The true R'' need not be large: at cell 313, for example, the m = 2
enclosure R2 ≈ [−4,419, +4,419] is almost symmetric about 0.

Closing it would need a governed change to the curvature construction, for example an e-dependent or
higher-order-in-e candidate for H, or order-3 auxiliary evidence. That is outside this round, and no frozen
setting was changed.

The boundary lies between ρ ≈ 5.4e-3 (cell 250 passes at 65% for m = 5) and ρ ≈ 0.0175 (cell 275 fails m ≥ 2).
Cell 275 at m = 1 passes at 95.1%.

Because every certificate quantity is monotone in the per-patch sups, the partial-coverage previews could only
understate the final values. The final values match them to about 1%.


## Disclosures
1. **Aggregator provenance.** The first T3 aggregator recorded whole-file hashes of the shared chunk files. Those
   files were still growing, so a cell-0 pipeline replay moved 30 provenance leaves while the content was identical.
   The aggregator now hashes the records it consumes for the cell. The superseded replay is kept in
   `evidence/replay/superseded_whole_file_provenance/`.
2. **Replay configuration.** For patches (0,0) and (0,18), the original cell-313 records came from a five-cell tile
   run in which the PanelShared cache was warm. A standalone replay moved only the nested cache counters, which the
   frozen classifier defaults to SCIENTIFIC; every node value was identical. The definitive replay uses the matching
   configuration (`evidence/replay/matched_tile_config/`), and the standalone comparison is kept in
   `evidence/replay/superseded_config_mismatch/`.
3. **Firewall check.** The record's production-process check originally used a substring search, which matched this
   tool's own shells. It now matches only python processes running a production entry point.
4. **Terminal cell 315.** Its ρ = p + s·c_SR (SR_terminal_exception) is carried as a 256-bit Arb enclosure, with
   formulas and gates identical to `ledger.cell_ledger`.
5. **Inherited canonical IDs.** Panel IDs use the governance-canonical v2 form inherited from the T2 closure.


## Production firewall
- prodctl was not run. The production ledger was not touched, no retries were consumed, and no AWS or Vultr
  production workers were started.
- The production worktrees are clean and unchanged: `ReBaseGuard-sr-parallel` at bd7cf26 and
  `ReBaseGuard-sr-lifecycle` at bcec064.
- Active `rbg-` units: 0. Production processes: 0.
- The historical 2026-09-10 unit is unchanged: ActiveState=failed StateChangeTimestamp=Thu 2026-09-10 11:03:19 UTC.
- **Firewall PASS: True.**

## Not claimed
K1 closure, production readiness or authorization, the 316-cell campaign, any cell other than the six listed, and the
far field (inherited, not recomputed).
