# K4: assembly-rule audit and freeze (pre-result; no production value read)

## Validity audit of the proposed procedure

| check | finding |
|---|---|
| mathematics | On a chain of contiguous cells from `e = 0` with `R'_cell < 0`, `R` is strictly decreasing, and `R(0) = 0` exactly (P5-T3), so `R < 0` on `(0, chain end]`. On any other cell, `R_cell.hi < 0` gives `R < 0` there. Both are sound given the premises. |
| premises | (i) `R_interval` and `D_interval` are the K1-certified enclosures of `R(e0)` and `R'(e0)`. (ii) `M_R2 ≥ sup_cell |R''|` (frozen `assembly.curvature_bound`). K1's own `target_gate` rests on exactly these objects (`ledger.taylor_enclosure`), so K4 inherits K1's soundness and adds no new analytic premise. |
| signed use | `taylor_enclosure` uses `D` only through `|D|` (Δ is symmetric). The chain uses `D.hi`. This is admissible because `|D|` bounds `|R'(e0)|` only by virtue of `D_interval` being an enclosure. The same reasoning makes **signed** use of `R2_interval` admissible. This corrects the "magnitude only" wording of `p5y_k2k5_postk1_audit/K4_K5_ADMISSIBILITY.md` §2; the adjudicator should confirm. |
| domain | **Amended to be strict.** Cells with `left < 2`. A cell starting exactly at 2 meets `(0,2]` only at a point already covered, and including it could manufacture a spurious failure. Frozen geometry has none: SR 295 cells (0–294) and CUSUM 310 cells (0–309), both contiguous from 0 to past 2. |
| scope | 8 `(D,m)` with `m ∈ {1,2,3,5}`; a missing detector or `m` → `K4_SCOPE_INCOMPLETE` |
| precision | exact rationals over outward endpoints; floats refused; strict inequalities |
| integrity | SR is reached only through sealed production records and re-hashed. The integrity function reproduced `t4_record_sha256` on one committed non-production control record (hash only). CUSUM requires an attestation bound to the frozen successor producer identity. |
| failure / inconclusive | fixed mapping; a too-loose cell is `INCONCLUSIVE`, never a mathematical failure; no in-checkpoint refinement |
| governance | Freezing before any genuine PS1 or CUSUM production value is observed by the declarer is pre-result. Earlier non-production records are disclosed. |
| literal H2 for `e > 2` | **not asserted**. The consumer licence is P5X-T7(1) plus K1. |

## Freeze

- `p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json` (+ `K4_ASSEMBLY_CHECKPOINT_HASH`) binds:
  - the decision procedure;
  - the input schema;
  - the exact domain (both frozen tables by sha256);
  - failure and disposition behaviour;
  - the sha256 of `code/k4_assembly.py`, `tests/test_k4_assembly.py` and the unchanged proposal.
- Genuine mode unlocks only with that binding **and** the integrity inputs. It has not been executed.

```text
K4_CHECKPOINT_READY                    = YES (frozen)
K4_NEW_COMPUTE_REQUIRED                = NO
K4_WAITING_ONLY_FOR_COMPLETE_K1_INPUTS = YES  (PS1 369 sealed + attested; CUSUM 326 under the frozen successor + attested;
                                               then independent adjudication applies the frozen mapping)
```
