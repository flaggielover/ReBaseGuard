# Theorem-TC successor — specification (pre-registration; written before any certified or real TC computation)

## 1. Question and answer shape

Can the CUSUM K5 lower front (m1 11–35, m2 11–41, m3 11–42, m5 11–44; 122 open (m, cell) pairs after coverage map r3)
be closed by certified whole-cell R'' enclosures with H.lo ≥ 0 (theorem TC), fed to the frozen K5-B on top of the adopted
Perron-deflated state? The answer is the frozen K5-B pass/open set of the sealed, adjudicated consumption. Nothing else
(no tolerance, no cell selection) decides it.

## 2. Why new real addresses are needed (section-5 demonstration)

Phase B (`phase_b/ROUTE_COMPARISON.md`, forecast under the gates frozen at `e89b33f2`): every zero-new-real route closes
0 pairs with the certified inputs it would actually use (G: midpoint R'' + T-EXT M3; D with the certified T-EXT M5),
and the idealised D (a deflated M5 tower with no hull growth at all) is MARGINAL. The order-2 information in the adopted
K1 records cannot be made whole-cell sharp without a candidate for F''' at the cell midpoint (the whole-cell radius
is set by the e-constant candidate, Phase A). The TC route needs exactly one new object per (cell, r): the order-3
midpoint candidate G_r and its certified residual.

## 3. Addresses (pre-registered, exhaustive)

CUSUM K1 cells 11, 12, …, 44 (34 cells; union of the open lower front over m), at the frozen cell midpoint e0 only,
objects r = 0..4, all m ∈ {1, 2, 3, 5} from the same objects. No other cell, drift, order or detector. The K1 part
(F_r, dF_r, H_r, sources, W) is a deterministic REPRODUCTION of the adopted candidates, checked field by field against the
sealed records (identity gate); the new values are G_r (order-3 candidate, used internally), δ_mid(G_r), the candidate suprema and the
origins at x0.

## 4. Producer, runtime, dependencies

- `code/tc_producer.py real` on rebaseguard-vultr-02, venv `/root/work/rbg-cusum-aux5-venv` (Python 3.12.3, numpy 2.5.2,
  scipy 1.18.1, python-flint 0.9.0), 256 bits, 1 BLAS/flint thread per process, 4 worker processes.
- Frozen chain imported in place: order-3 real producer (`cusum_order3.Order3Certifier`, `rung3_residual.g_residual`;
  its producer manifest must have no problem), Aux5 / Aux3 K1 science (`all_residuals`, `aux_residuals`,
  `aux_propagate.cell_dag`, `RefinedCellValues`, `midpoint_order3_eps`, `AuxiliaryRefinement`, `order2`), frozen assembly.
  The whole-cell refinement `refine2` is not run (it is not needed by theorem TC).
- Every repository file loaded by the producer is pinned in `config/TC_PROTOCOL.json` (collected from `sys.modules`).

## 5. Fields and outputs

Per cell `TC_CELL_<k>.json` (exact rational strings): rho, e0, the drift-aware norms k_0..k_4 and j_0..j_4, the
closed-form source suprema sup_C|S_0⁽ⁿ⁾| (n = 0..4), for r = 0..4: δ_mid of F_r, dF_r, H_r, G_r, the midpoint source
errors of orders 0..3, the candidate suprema of F̂, D̂, Ĥ, Ĝ, the origin interval Ĥ_r(a) and the upper bound |Ĝ_r(a)|
(no uncertified order-3 candidate value is recorded); the frozen order-2 W enclosures; the identity-gate report; the
runtime checks; the governance binding. Plus `TC_INDEX.json`, `RUN_LEDGER.jsonl`, and after the seal
`TC_CONSUMPTION.json`.

## 6. Acceptance (all required; otherwise the run is VOID and not consumed)

1. Every address yields exactly one gated real record (identity gate: identical).
2. The pre-registered reproduction (cells 11 and 44) is byte-identical to the first run.
3. `tc_rule` and the independent `tc_crosscheck` agree exactly on every cell and m.
4. The consumer replay gate passes; A-constants equal the adopted audit; no TC intersection is empty.

## 7. Budget and stopping rule

- Forecast of new real CPU: 16.3 CPU-hours (`evidence/forecast_r1/COST_NOTE.md`: measured dev replays of cells 11 and
  44, recorded before the freeze). Protocol cap: 24 CPU-hours, 4 workers (campaign hard cap 40 across Campaigns A and
  B). `tc_run` launches no new cell once the recorded CPU would exceed the cap; that makes the run VOID.
- Each address runs exactly once, plus the 2-cell reproduction. No re-run, no extra address, no adaptive choice.

## 7a. Governance of the real run (pre-freeze review r1, B1/B2 and N1/N2 addressed)

- Mode real refuses unless: the protocol is committed and pin-exact and the namespace is clean; a QUALIFIED result at
  the freeze commit is committed; an AUTHORIZATION bound to that qualification's sha and to exactly the 34 addresses is
  committed AFTER it; a GUARD = ALLOW bound to that authorization's sha is committed (same or later commit); the runtime
  equals the protocol's; the order-3 producer manifest and the Aux5 manifest verify; the K1 record sha is the
  pre-registered one; no repository module outside the frozen list is loaded.
- The frozen Order3Certifier is called directly; its own real-cell registry stays empty. This protocol's authorization
  is the governing gate for this parallel channel, and the authorization review must accept it explicitly.
- The consumer is bound to the frozen protocol (review r2 B-R2-1): the protocol must be committed and equal to its bytes
  at the freeze commit, the namespace unchanged since the freeze outside `evidence/tc_r1/` (no uncommitted or untracked
  file either) and every pin matching; tc_rule and tc_crosscheck are loaded from the protocol's pins. It refuses unless
  the index lists exactly the 34 addresses under this protocol, the 2-cell reproduction is byte-identical, every sealed
  file (cells, repro, index, ledger) was committed once and never modified, the ledger records exactly one START and one
  ok OUTPUT per address (index sha), a RUN_END with identical reproduction and no RUN_VOID/CAP_STOP, GUARD is DENY
  again, the QUALIFICATION -> AUTHORIZATION chain is bound to this protocol, every record's binding (protocol sha,
  freeze commit, authorization sha, a run head that descends from the authorization commit and carries the bound ALLOW
  guard, K1 record sha) matches, and tc_crosscheck equals tc_rule on every cell and m.

## 8. Lifecycle

pre-freeze refusal exercised → freeze commit (protocol + code + this spec + all review documents) → qualification S00–S09 at the freeze commit
in a fresh clone on vultr-02 → fresh-context authorization review → AUTHORIZATION.json + GUARD.json (ALLOW, exactly
the 34 addresses; AUTHORIZATION after QUALIFICATION, GUARD bound to AUTHORIZATION) committed → `tc_run` → GUARD back to DENY
→ seal (cells, repro, index, ledger committed once; no inspection
of pass/open before) → consumption (`tc_consume`, twice, byte-identical) → independent adjudication → coverage map r4.
After the freeze only `evidence/tc_r1/` may change.
