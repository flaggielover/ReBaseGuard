# P5Y K4: execution of the frozen assembly checkpoint (r1)

**K4_SCIENTIFIC_RESULT = NOT_CLOSED.** The frozen disposition is **K4_INCONCLUSIVE_K1_RECORDS**. The independent adjudication is **ACCEPTED**. No closure tag was created.

This namespace is additive. It executes the K4 assembly checkpoint frozen at `e5cc5a90` (`p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json`, sha256 `95b1fd16…`) exactly once, over the now-complete K1 production records, and records the result. The checkpoint, its bound sources and all historical evidence are unchanged.

## Obligation, as frozen

For `D ∈ {CUSUM, SR}` and `m ∈ {1,2,3,5}`, `R_{D,m}(e) < 0` must hold for every `e ∈ (0,2]`. This is P5X-T7(1).
- The domain is every frozen cover cell with `left < 2` and `right > 0`.
- The chain step certifies a maximal prefix from `e = 0` with `Rprime_cell.hi < 0`.
- The direct step requires `R_cell.hi < 0` on every other cell.
- A cell with `R.lo > 0` is a counterexample. Any other cell is too loose.
- There is no refinement.

The checkpoint does not assert H2 for `e > 2`. That region is covered by the consumer licence (P5X-T7(1) plus K1 `sup|R| < 2`).

## Inputs (readiness gate: PASS)

| Input | Status |
|---|---|
| **SR** | 369 sealed PS1 production records, with T4 evidence re-hashed. **PASS.** |
| **SR Lane C audit** | Run here for the first time, read-only and blinded, with frozen tool `7e65c8bc`: `INTEGRITY_READY_FOR_ADJUDICATION = true`, 369/369 complete, no issues, accounting reconciles. Output: `evidence/lane_c/`. **PASS.** |
| **CUSUM** | Aux5 composite export, 326 records (closure `ce7fb933`). `verify_closure.py --export-tree` passes. Attestation `039e2e1c`, producer identity `3692d0fe`. **PASS.** |
| **Geometry** | `code/k4_readiness.py` (executor-written, not frozen) checks every record's `e0`/`rho` against the hash-bound frozen tables. Domain: CUSUM cells 0–309 and SR cells 0–294, both contiguous from 0 past 2. **PASS.** |
| **K1 successor (`7d5cf02b`)** | Its bridges lie at `e > 5.5`, so the K4 compact domain rests only on the historical records above. |

## Result of the frozen assembly

Report: `evidence/K4_ASSEMBLY_REPORT.json`, sha `83cabce2…`. It is exact rational and took 1.19 CPU-s.

| (D,m) | Outcome |
|---|---|
| CUSUM m=1 | CELLWISE_ALL_CERTIFIED (chain up to 0.1748) |
| CUSUM m=2 | **CERTIFICATE_TOO_LOOSE** (cells 0, 1) |
| CUSUM m=3 | **CERTIFICATE_TOO_LOOSE** (cells 0, 1, 2) |
| CUSUM m=5 | **CERTIFICATE_TOO_LOOSE** (cells 0, 1, 2) |
| SR m=1, 2, 3, 5 | CELLWISE_ALL_CERTIFIED |

There is no counterexample: no domain cell has `R.lo > 0` in any (D,m).

## Residual blocker: CERTIFICATE_TOO_LOOSE (CUSUM, m ≥ 2, `e ∈ [0, 957/625000]`)

In the failing cells, `R'(e0)` is certified negative: `D.hi` is −3.73, −2.53 and −0.94 at cell 0 for m = 2, 3, 5. The frozen mean-value widening `ρ·M_R2` is about 7.6–7.9, because `M_R2 ≈ 3·10^4`. That widening exceeds `|D.hi|`, so `Rprime_cell` crosses 0 and the chain is empty. Cell 0 contains `R(0) = 0`, so the direct rule cannot certify it either. `evidence/K4_LOOSE_CELL_DIAGNOSTIC.txt` gives the per-cell numbers (float-formatted, for diagnosis only).

Under the frozen mapping, any tightening needs a **new predeclared successor**. Candidate tightenings include finer near-zero cells, signed use of `R2_interval` (judged admissible in K4_FREEZE_AUDIT), and a certified `R'` enclosure on `[0, e_0]`. None was attempted here.

## Independent review (`review/`)

A fresh-context reviewer re-ran everything from pristine archives: Lane C, the CUSUM tree obtained directly from vultr-02, and the frozen tool in GENUINE mode. The reproduced report is **byte-identical** (`83cabce2`). The frozen tests pass 16/16. An independent exact recomputation agrees with every cell.

Verdict: **K4_ADJUDICATION = ACCEPTED**, disposition K4_INCONCLUSIVE_K1_RECORDS.

The reviewer recorded these notes:
- **Temporal (PASS_WITH_NOTE).** 16 genuine SR T4 records, all in the K4 domain, were written about 25 minutes before the freeze. The checkpoint's blinding disclosure does not list them, and there is no evidence they were observed. All failing cells are post-freeze CUSUM cells.
- **Frozen-tool weaknesses (non-blocking).** The tool only checks that `producer_checkpoint_sha256` is present. It trusts the Lane C flags of whatever file it is passed. It does not compare record geometry with the frozen tables; the readiness gate does. Its CUSUM `*.json` glob matches dotfiles, which fails closed.

## State

```text
HISTORICAL_K4_PRE_RESULT_STATE = PRESERVED
K4_SCIENTIFIC_RESULT           = NOT_CLOSED
K4_FINAL_VERDICT               = NOT_CLOSED (K4_INCONCLUSIVE_K1_RECORDS)
K4_RESIDUAL_BLOCKERS           = CERTIFICATE_TOO_LOOSE (CUSUM m=2,3,5; cells 0-2)
K1 = CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN   K2 = CLOSED   K3 = CLOSED   K4 = OPEN   K5 = OPEN   P5Y = NOT_YET_CLOSED
```

The machine-readable record is `config/K4_EXECUTION_RESULT.json`.
