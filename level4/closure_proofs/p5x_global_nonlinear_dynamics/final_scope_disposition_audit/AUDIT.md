# P5X — Final Scientific Scope and Disposition Audit

`FINAL_GOVERNANCE_AND_SCIENTIFIC_SCOPE_AUDIT`. Not R9, not a binding campaign,
no new science. **Nothing historical changed.**

```text
P5X_FINAL_VERDICT        = PARTIAL          (CASE D)
P5_SCIENTIFIC_LINE       = PARTIALLY_REPAIRED_BY_SUCCESSOR
P5_ORIGINAL_VERDICT      = PARTIAL          (unchanged, immutable)
```

---

## 1. What the original P5 actually left open

From `p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md`, quoted:

> `CLOSED` is unavailable for two independent reasons. First, frozen closure
> gate G20 is literally false in the adjudication worktree... Second, G3, G7,
> and G9 use universal language (`sup_e`, `wherever`, and `anywhere`) while
> their evidence is finite-grid Monte Carlo/interpolation; they do not pass as
> literal universal criteria.

The literal gate audit gives `15 PASS, 5 FAIL`:

| P5 gate | literal criterion | result | why |
|---|---|---|---|
| `G3` | `sup_e |R| < 2` in 8/8 | **FAIL** | only a finite grid measured; unproved `H3b` |
| `G4` | `|R| < 0.01` for `|e| >= 10`, 8/8 | **FAIL as universal** | finite-grid extrapolation |
| `G7` | multiplier `<1` wherever it exists | **FAIL** | finite branch grid; global attraction unproved |
| `G9` | SNR anywhere `< 2.5` | **FAIL as universal** | interpolation/finite-grid |
| `G20` | 294 files byte-identical; worktree scope = P5 only | **FAIL** | root README + P6 pre-design; **external to the science** |

**`8/8` = 2 detectors x `m in {1,2,3,5}`.** P5's `G3` is stated over both
detectors and all `m`; it is not detector-separable as written.

So the original scientific gap is exactly: **universal-in-`e` statements whose
evidence was a finite grid rather than a certified enclosure.** That is the gap
P5X exists to close, and `G20` is a repository-hygiene failure that no
successor campaign can address.

## 2. What P5X intended to close, frozen at Checkpoint A

`FROZEN_GATES.md`, verdict semantics, quoted verbatim:

```text
P5X = CLOSED_CANDIDATE     iff G1,G2,G6,G7,G8,G10,G11,G12,G13 pass
                            and G3 = PROVED_ALL_CELLS
                            and G4 = TWO_SIDED
                            and G5 = CERTIFIED for at least one detector,
                                     and not FAILED for the other
                            and G9 = AGREE
P5X = PARTIAL_CANDIDATE    iff the integrity gates pass but a scientific gate
                            lands on an admissible weaker outcome
```

and: *"`G3 = PROVED_ALL_CELLS` with `G4 = TWO_SIDED` is the minimum that can be
called a global mechanism."*

## 3. Obligation ledger

| obligation | status | evidence |
|---|---|---|
| `P5X-T1` exact 2-D reduction, every `m`, every `e` | **CLOSED_EXACT** | `PROOF.md` `L1`,`L2`; Checkpoint B |
| `P5X-T2` exact second-moment reduction | **CLOSED_EXACT** | `FROZEN_THEOREM.md` §3 |
| `P5X-T3` far-field forgetting, explicit constants | **CLOSED_EXACT** (theorem); certified scalar **NOT_RUN** | `|R_SR(±10)| <= 4.2e-3` from audit arithmetic, not a P5X production certificate |
| `L1,L2,L3,L5,L6` human proofs | **CLOSED_EXACT** | Checkpoint B |
| `D1` erratum (`b_SR = log(1+A)`) | **CLOSED_EXACT** | frozen bytes preserved, erratum recorded |
| SR panel-free exact kernel (R4/R6) | **CLOSED_CERTIFIED** (method) | R6 gate PASS, amplification `1.0027e2`, flat 192-512 bits |
| `C_SR` rigorous resolvent (B1) | **CLOSED_CERTIFIED** at `e = 1/4` and `e = 0` | `203.067`, `1505.821` |
| R8 local certification gate | **CLOSED_CERTIFIED** | `B1_GATE and B2_GATE` PASS |
| SR `m=1` sign of `R` on one cell | **CLOSED_CERTIFIED** | R8 enclosure `[-2.6875, -0.4932]`, strictly negative |
| **`G3` = `sup_e |R| < 2`, all cells** | **OUT_OF_BUDGET** | no cover run for either detector |
| **`G4` = `TWO_SIDED` (needs `s_min>0`, `M_2<inf`)** | **NOT_RUN** | second moments never implemented |
| `G5` accepted cover tiles `[0,12]`, per detector | **NOT_RUN** | no production cover, either detector |
| `G9` empirical correspondence `E1`-`E3` | **NOT_RUN** | |
| `G7` Lean `X1`-`X3` sorry-free | **NOT_RUN** in P5X | Lean tree unchanged since Checkpoint A |
| `G13` single adjudication results document | **NOT_RUN** | |
| `P5X-T7`, `T8` (Level C/D) | **NOT_RUN** | pre-registered as optional |
| `F3 = 0.2` | **NON_LOAD_BEARING_ENGINEERING_GATE** | F3 provenance audit, `CASE B`/`G2` |

## 4. `P5_CORE_REQUIRED` and what is closed

The minimum needed to say "the gap P5 left has been closed" is, from P5's own
failed gates: `{G3 universal, G4 universal, G7 universal, G9 universal}` —
the four universal-in-`e` statements. (`G20` is repository hygiene, outside any
successor's reach.)

```text
closed : G4  -- at THEOREM level only (P5X-T3 is exact and decreasing;
               the certified production scalar was never produced)
open   : G3, G7, G9
```

**One of four, and that one only at theorem level.**

## 5. Is SR global `G3` load-bearing? — YES, on two independent edges

**Edge 1 (P5X's own semantics).** `CLOSED_CANDIDATE` requires
`G3 = PROVED_ALL_CELLS`. SR is not certified on any cell under the frozen
criterion, so `G3` lands on an admissible weaker outcome, which by the frozen
rule yields `PARTIAL_CANDIDATE`.

**Edge 2 (P5's gate).** P5's `G3` is `sup_e |R| < 2` in `8/8` — *both*
detectors, all `m`. SR global `G3` is therefore directly one of the four
original failures, not an SR-specific extra.

Failure to certify it prevents `A` (the SR global quantitative bound) and, via
`P5X-T5`, the explicit trapping interval; it does **not** invalidate the
invariant-law theorem `P5-T7` (which P5 already established and P5X never
re-opened), nor the exact structural results `P5X-T1`/`T2`/`T3`.

## 6. Detector separability — `PARTIAL`, and it does not rescue closure

Pre-existing evidence for separability: P5X `G5` says *"for each detector
separately... asymmetric outcomes are admissible"*, and `CLOSED_CANDIDATE`
accepts `G5 = CERTIFIED for at least one detector`. So detector asymmetry was
pre-registered — but **only for `G5`, the cover-construction gate**.

`G3` carries no such allowance: it requires `PROVED_ALL_CELLS`. And P5's own
`G3` is `8/8`. So `DETECTOR_SCOPE_SEPARABILITY = PARTIAL`: real for `G5`, absent
for `G3`. A detector-limited closure would require weakening `G3`, which §11
prohibits.

## 7. Second moment — independently load-bearing

`G4 = TWO_SIDED` is a conjunct of `CLOSED_CANDIDATE`, and the frozen text names
`G3` **with** `G4` as "the minimum that can be called a global mechanism".
Second-moment certification was never run — the campaign stopped at SR first
moment. **This alone blocks `CLOSED`, independently of anything about SR.**

## 8. Post-hoc-narrowing test

> Would calling P5X `CLOSED` now require removing or weakening a requirement
> that was clearly load-bearing before the relevant result?

**YES.** It would require weakening `G3` from `PROVED_ALL_CELLS` and dropping
`G4 = TWO_SIDED`, both frozen at Checkpoint A before any result. **`CLOSED` and
`CLOSED_IN_PREEXISTING_SCOPE` are prohibited.**

## 9. SR global `G3` limitation classification

```text
MATHEMATICAL_FAILURE            NO   -- P5X-T1/T4 are stated and the route exists
CERTIFIER_FAILURE               NO   -- R6/R8 machinery works; local gate PASSES
CERTIFICATION_COST_LIMITATION   YES  -- worst required grid 4708 at e~3
RESOURCE_ENVELOPE_LIMITATION    YES  -- infeasible under the frozen envelope
UNRESOLVED_SCIENTIFIC_CLAIM     YES  -- no certified sup_e |R| < 2 exists
```

Known mathematically: the reduction, the far-field decay, the sign on one cell,
and the resolvent constant. Lacking a rigorous certificate: the global magnitude
bound on either detector.

## 10. Claim table — strongest legitimate status today

| claim | status |
|---|---|
| exact invariant law (`P5-T2`, raw-mean identity) | **EXACT** (P5, unchanged) |
| geometric ergodicity, unique invariant law (`P5-T7`) | **EXACT** (P5, unchanged) |
| symmetry / oddness `R` odd, `S` even, `R(0)=0` (`P5-T3`) | **EXACT** |
| finite moments of every positive order | **EXACT** (P5-T7) |
| local derivative `R'(0)` / `Gamma` | **CERTIFIED** (pre-existing Arb intervals) |
| local instability mechanism, `rho_c` | **CERTIFIED** (P3, pre-existing) |
| exact 2-D reduction for all `m` (`P5X-T1`) | **EXACT** (new) |
| far-field forgetting with explicit constants (`P5X-T3`) | **EXACT** (new); production scalar **NOT_ESTABLISHED** |
| CUSUM global `sup_e |R| < 2` | **NOT_ESTABLISHED** (single-cell certified only) |
| SR sign of `R_{SR,1}` on `e in [0.24,0.26]` | **CERTIFIED** |
| SR global magnitude `sup_e |R| < 2` | **NOT_ESTABLISHED** (out of budget) |
| second moment / stationary RMS beyond linearization | **NOT_ESTABLISHED** |
| stationary nonlinear mechanism (global) | **NOT_ESTABLISHED** |
| detector-general conclusions | **NOT_ESTABLISHED** |

## 11. Verdict

**`CASE D` — `P5X = PARTIAL`.** Smallest sufficient reason: *the production
phase never ran.* No certified cover exists for either detector, the
second-moment obligation `G4` was never started, and `G5`/`G7`/`G9`/`G13` are
unrun. `CASE C (PARTIAL_STRONG)` requires "one load-bearing obligation
remaining"; four remain. Calling it `PARTIAL_STRONG` would optimise for
appearance, which §15 forbids.

**`P5_SCIENTIFIC_LINE = PARTIALLY_REPAIRED_BY_SUCCESSOR`.** P5X supplies exact
structure P5 did not have — the 2-D reduction that makes certified global-in-`e`
enclosures possible at all, and an exact far-field theorem addressing P5's `G4`
at theorem level — plus a validated certification stack and a corrected frozen
statement (`D1`). It closes none of P5's four universal gates with production
evidence.

## 12. Is more work justified?

**`LARGE_COMPUTE_ONLY`** for stronger SR closure, with an important
qualification: **the CUSUM lane was never run and is not large.** The R3
accounting projected CUSUM at `~146` CPU-hours. The campaign spent R3-R8 and six
audits on SR certification method and never returned to run the affordable
CUSUM production cover, nor scoped the second moment.

No further certifier R&D is recommended; this audit discovered no new
load-bearing mathematical fact.

## 13. Level-4 implication

P5 remains one of the unresolved Level-4 scientific lines. P4X and residual P5
**coexist**: P4X is not the only remaining repair campaign. No global Level-4
closure is claimed.

## 14. Recommended wording

**README status line:**

> P5 remains historically **PARTIAL** and immutable. The successor campaign P5X
> establishes new exact structural results — a two-dimensional reduction of the
> selection map for every window `m`, an exact second-moment reduction, and an
> exact far-field forgetting theorem — and builds a validated panel-free
> certification stack for the Shiryaev-Roberts detector. It does **not** close
> P5's universal-in-`e` gates: no certified cover was produced for either
> detector, and second-moment certification was never run. P5X is **PARTIAL**.

**Closure-report wording:**

> `P5X = PARTIAL`. Exact obligations `P5X-T1`, `T2`, `T3` and lemmas `L1`-`L6`
> are closed. The SR certification stack (`R6` kernel, `B1` resolvent, `R8`
> local gate) is validated and certifies the **sign** of `R_{SR,1}` on the
> probe cell, consistent with Monte Carlo. The load-bearing consumer
> `sup_e |R| < 2` (`G3`) is **out of budget** under the frozen resource
> envelope: certification-feasible in principle, with a worst required state
> grid of `~4708` near `e = 3`. `G4` (second moments) was never run. Historical
> `R8 = FAIL` and `F3 = 0.2` stand. Novelty `NOT_ESTABLISHED`;
> `LEVEL4_GLOBAL_CLOSURE = NO`.
