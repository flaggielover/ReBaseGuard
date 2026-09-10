# P5Y K1 SR O9 — T2 per-patch certification: T2_PER_PATCH_CERTIFICATION_CLOSED

Scope: **patch-level certified residual execution only.** This record claims **no** whole-cell
`delta_cell` closure, **no** midpoint refinement closure, **no** `B_cover` closure, **no** 28-obligation cell
closure and **no** production readiness. T3/T4/T5 were not started. Production was not touched.

Authoritative record: `config/T2_CLOSURE_RECORD.json`. All 13 closure-gate items are true.

## The final certifier
`code/t2_final_certifier.py` only composes committed pieces. It certifies the full frozen SR DAG: 63 nodes,
of which 45 are residual nodes and 18 are operator images, over 102 contracts. It uses:
- the task1r-span-p1-v1 core with O9 contraction (29ee382);
- contracted endpoint strips and the repeated-multiplication raw-shift path (b48973d6);
- the authorized P1 Lagrange factor (014879b / 0f52b77).

No new scientific method is introduced.

## Evidence
- **Phase 1 — predecessors** (`evidence/phase1_predecessors.json`):
  - `verify_pre_t2`, `verify_a5` and the B_int governance verifier all pass.
  - The endpoint-strip manifest, strip validation and the micropilot hash reproduce.
  - The B_int pilot kill-case hash reproduces.
  - Predecessor commits and tags are unchanged, and the predecessor directories are clean.
- **Phase 2 — equations and contracts** (`evidence/equation_audit.json`):
  - The equation map equals the committed map (sha ebcd9b13…).
  - There are 46 candidates, and 102 contracts with shift counts 43/35/20/4. The contract IDs are bijective,
    and 163 operator applications map exactly onto the node contracts.
  - The identity h1^(k) = δ_k0 − K^(k)1 holds through the const:1 contracts, both symbolically and
    numerically (108 containment checks; max gap 4e-75).
  - There is no Phi shortcut.
- **Phase 3 — representative full DAG** (`evidence/dag/`): 36 cases, 6 cells × 6 patches. All 63 nodes
  and all 102 contracts are present in every case, all bounds are finite and non-negative, and dependency
  hashes are complete. The endpoint gate, B_int and all F local gates pass 36/36. The worst endpoint ratio is
  6.2e-11 and the worst int/allowance is 1.4e-4.
- **Phase 4 — determinism** (`evidence/determinism.json`): 5 replays in fresh processes. 0 scientific
  leaves moved. Only incidental runtime leaves moved, under the frozen aux4 classification.
- **Phase 5 — cache equivalence** (`evidence/cache_equivalence_compare.json`, `evidence/cache_measurements.json`):
  18 tile-major/shared-cache records are scientifically byte-identical to fresh recomputation. The production
  block size is NOT frozen.
- **Phase 6 — universe** (`evidence/universe_conformance.json`): all 3,994 live patches conform.
  - Counts: 76,475 contracted panels and 7,988 strips, which is 84,463 in the historical n_z + 2
    convention. The 83,452 census is not used.
  - Checks: exact rational P1 passes on panels and strips, span closure is exact, and the v2/v3
    identities are canonical and unique.
  - Raw-shift drift: 0 non-finite values over 458,850 panel–cell evaluations. The cell 315 splice is exact.

## Disclosures
- **Panel-ID label repair.** The frozen T2 engine emits panel IDs with the rule name inside
  (`task1r-span-p1-v1`). The successor emits the governance-canonical form `SRpanel:v2:task1r-span-p1:...`.
  These are labels only, and predecessor evidence is not rewritten.
- **Frozen aux4 classifier quirk.** Its pattern `run.**` matches only one segment below `run`. A first
  comparison with nested run counters was therefore superseded (`evidence/superseded_nested_counters/`). The
  counters were flattened and every run repeated; the classifier itself is unchanged.
- **Historical negative results are preserved.** `T2_NOT_CLOSING_RECORD.json` (endpoint gate not closing,
  29ee382b) is byte-identical to its commit, and fa92afb (BINT_REPRESENTATION_NUMERICALLY_NOT_CLOSING) stands.
