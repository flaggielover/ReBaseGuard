# K5_PERRON_DEFLATED_SUCCESSOR_SPEC (draft r1 — not frozen)

An additive, deterministic successor of the adopted T-EXT consumption. It re-derives tighter enclosures of R_m, R_m'
(at every K1 midpoint) and R_m'' (uniformly on every K1 cell) for the CUSUM cells 0–148 from the published K1 records,
using theorem AD (`theorem/THEOREM_AD.md`, rule r2) and a certified operator-only registry, and feeds them to the frozen
K5-B exactly as T-EXT did. **New real scientific addresses: 0.** No model solve, no candidate recomputation, no R''' or
R⁽⁵⁾, no new real campaign namespace.

## 1. Frozen mathematics

- Theorem AD with Lemma K, Lemma T (taboo and whole-kernel supersolutions, e-uniform by the affine expansion), Lemma SM,
  Lemma Dv', Theorem AD, Corollary T, Corollary C, as committed at the freeze.
- Premises taken from the frozen stack only: ERROR_ALGEBRA §1 and §3 (exact error identities; delta_mid and the
  whole-cell delta_cell, a uniform bound of the fixed candidate's residual on the cell), as produced by the Aux5 chain
  (`aux_propagate.cell_obligations`, `refine2`, `order2`) and assembled by `propagate.enclosures`, `assembly.assemble`, `enclose`.

## 2. Certified operator quantities (registry r1, `evidence/registry_r1/REGISTRY.json`)

| quantity | domain | certificate |
|---|---|---|
| C_T ≥ ‖Ĝ_e‖, τ ≥ E_a[τ ∧ T_a] | 12 taboo e-blocks of width 1/100 on [0, 12/100] | degree-20 polynomial supersolution, Pair kernel minus the origin piece, both ends of the block |
| Ā ≥ E_a[τ] | each K1 cell 0–148, uniformly on the cell | degree-12 whole-kernel polynomial supersolution W = αA + 2 |
| D_lo, D1 ≥ \|D'\|, D2 ≥ \|D''\| | each K1 cell 0–148, uniformly on the cell | taboo objects d = Ĝh₁, d', d'' (degree 20) with tame taboo error propagation |

Every artifact carries its exact payload; `code/build_registry.py verify` recomputes every certified field.

## 3. Domain and block partition

K1 cells 0–148 (e ∈ [0, 0.1146944]); the registry has one entry per cell (its own [x_lo, x_hi]); the consumer's r2
matching uses the open-interval intersection, so each cell uses exactly its own entry. Cells 149–309 are untouched.

## 4. Consumer semantics (`code/deflated_consume.py consume`)

1. Refuse unless the successor protocol (`config/SUCCESSOR_PROTOCOL.json`) is committed, the namespace is clean and
   every pin matches (`frozen_guard`). Append an evaluation-ledger line for every run.
2. Load the adopted inputs through the pinned E6 adapter and the pinned T-EXT channel derivation.
3. For every covered cell: radii of Theorem AD with the r2 constants; Corollary-T tightening of R and R' (midpoint) and
   R'' (whole cell); M' = min(M_R2, mag(R'')). Refusals: recorded interval narrower than its radii; empty interval.
4. Apply the adopted T-EXT C2 channel unchanged (L_k on 1–40; H ∩ [−M2, M2], M = min(M, M2) on 0–40).
5. Frozen `k5b_literal` per m on 0–309. Output: pass/open ranges, rows sha256, per-cell enclosures used, audit.

## 5. Acceptance gates (qualification, before the evaluation)

| gate | requirement |
|---|---|
| S00 | clean checkout at the freeze head; every protocol pin matches |
| S01 | registry verify: every artifact recomputed byte-identically from its payload; REGISTRY.json re-assembled byte-identically from the artifacts; all certified |
| S02 | registry float cross-check X-A (`xcheck_registry.py xcheck`): every certified bound dominates the float operator value |
| S03 | certifier probe: a wide block is refused; the point-certificate-as-block mutant is accepted (term load-bearing) |
| S04 | manufactured qualification `qualify_ad.py`: Q_PASS and MUTATION_PASS (17/17 unsound mutants detected; refusal and property checks all true) |
| S05 | replay: the empty registry reproduces the adopted T-EXT C2 consumption exactly (pass ranges and rows sha256, every m) |
| S06 | gate evaluation (`gate_eval.py`) at level USEFUL or better under the frozen FEASIBILITY_GATES |
| S07 | determinism: two evaluations byte-identical; ledger shows both at the freeze head |
| S08 | refusal-before-freeze exercised (a pre-freeze consume attempt is refused) |
| S09 | record assembly semantics: every recorded half-width ≥ Σ(1/m)·recorded radii (R, R', R''); for m = 1 equal to within 1e-6 relative |
| S10 | X-B: independent Fraction recomputation of every registry field from the artifacts' intermediates (envelopes, tame propagation, D composition, worst-block rule) |
| S11 | Arb proof of the rational bounds κ₁ < 0.7978846, κ₂ < 0.9678830 used by the consumer |

## 6. Seal and interpretation

The consumption result is committed (sha256) before any interpretation. Then an independent, fresh-context adjudication
reproduces the registry verification (or a declared sample), the replay, the consumption (byte-identical) and audits the
theorem use; only then is an updated K5 coverage map built.

## 7. Relation to T-EXT and to slot-1

Additive only. T-EXT's sealed TEXT_RESULT and its consumption are inputs, never modified; its C2 channel is applied
unchanged. Slot-1 enters only through T-EXT (L1 and Λ(k)). Cells that pass under T-EXT C2 cannot fail under the successor
(K5-B is monotone in tighter valid enclosures; S05 checks the base case).

## 8. Expected scientific addresses

None. The successor reads published records and certified operator constants only.
