# DRAFT P4X binding specification — NOT EXECUTED, NOT FROZEN

```text
STATUS        = DRAFT_ONLY
BINDING       = NO
CHECKPOINT    = NOT CREATED
FROZEN        = NOTHING
```

This is a proposal for what a P4X campaign would commit to *if* it were opened.
Nothing here is frozen, no checkpoint exists, and no number in it has been
produced.  A real P4X Checkpoint A would have to freeze this text (or a revision
of it) **before** any production result, and would additionally have to record
the §6 disposition-artifact loss.

## 1. Exact successor scientific question

> P4 proved, and independent adjudication accepted, that the closed Gaussian
> reuse-derivative mechanism generalizes to regular one-dimensional location
> families at both frozen detectors for every window `m >= 1`.  Its three
> failed gates were measurement and gate-specification objects, not theorem
> objects.
>
> **Does a correctly specified numerical correspondence, run at a precision the
> gate can actually demand, confirm that theorem across the same 96-cell design
> — and does P4's independent reimplementation agree with the closed Gaussian
> gains under a correctly specified two-sample statistic?**

P4X does **not** re-ask P4's theorem question, does not re-run P4's gates, does
not weaken them, and does not reinterpret any P4 negative result.

## 2. Exact required theorem

**Inherited, not reproved.**  `G1a`, `G1b`, `G1'`, `G2`, `G3a` (in its narrowed
form) and `G4`, verbatim from
`level4/closure_proofs/p4_theory_generalization/THEOREM.md`, cited by path and
by git object `eede90383da44c250871b1bb97d12045c897c8d9`.

P4X proves **no new theorem**.  Any proposal to prove one — the `G3` iff, a
Level-C headline, symmetry-free `G4`, the asymmetric fixed point `e*` — is
new science for a new priority and is out of scope by construction.

## 3. Assumptions

`(A1)-(A7)` exactly as frozen in `THEOREM.md` §2, discharged for the frozen
two-sided CUSUM (`k=1/2, h=5`) and the frozen symmetric two-chart SR
(`A=520.886133602749`, no headstart) by `L1`-`L5` of `PROOF.md` §8.  No
assumption is added, removed, weakened or strengthened.

## 4. Correspondence points / cells

Identical design to P4, so that the comparison is meaningful:

```text
layers    : reduced (cusum@2, sr@20) and frozen (cusum@5, sr@520.886133602749)
families  : THEOREM-SUPPORTED  gaussian, laplace, logistic, skewnormal4, t1p5, t3
            OUTSIDE-ASSUMPTIONS uniform (moving support), cauchy (no first moment)
windows   : m in {1,2,3,5}
cells     : 96 theorem-supported + 32 outside-assumption
routes    : A (score), B (Richardson finite difference), Q (deterministic
            quadrature, memoryless detector), N (deterministic-stopping
            neutrality control) -- kept apart exactly as in P4
```

Path budgets are **not** inherited.  They are set by a published pilot (§8 R0)
so that Route-B relative standard error is `<= 1 %` on every theorem-supported
cell where that is affordable.

## 5. Lean spine

```text
NONE_NEW.
```

Obligation: recompile the inherited `GeneralLocationFamilyP4.lean` (19
declarations) from its protected source and re-assert the axiom audit — axioms
exactly `{propext, Classical.choice, Quot.sound}`; no `sorry`, no `sorryAx`, no
project-specific axiom, no `axiom` declaration in the source.

Rationale: every open edge is numerical.  Lean evaluates no gain, so no
declaration can move the cut set.

## 6. Interval / certificate requirement

```text
NO NEW CERTIFICATION.
```

Obligation: re-verify the three inherited Arb objects at 160 bits and again at
`>= 256` bits — the unbounded-horizon Laplace closed form, the uniform exact
rational defect, and the finite-support bounded-score tilt witness.

P4X must state explicitly, as P1/P2/P3/P4 all did, that **no frozen CUSUM or SR
gain is interval-certified**, and must not move that boundary in either
direction.

## 7. Pass / fail gates  (to be frozen before any production run)

| id | gate | criterion |
|---|---|---|
| `X1` | protocol and witness hashes match the manifest | byte equality |
| `X2` | inherited theorem cited unchanged | `p4_theory_generalization` tree object equals `eede9038…` |
| `X3` | Route Q analytic identity holds | worst relative discrepancy `<= 1e-6` over 24 cells |
| `X4` | Route Q uniform identity fails as predicted | score side exactly `0`, exact map slope `-2.366025`, defect `2` |
| `X5` | Route N neutrality holds | all 72 deterministic-stopping cells return gain `1`, `\|z\| <= 4` |
| `X6` | **theorem-supported correspondence** | for every one of the 96 cells: `\|z\| <= 4` **and** `relative <= 0.03`.  A cell may instead be declared `ARBITRATED` iff its Route-B relative SE exceeds `0.01` **and** Route Q reproduces the identity for that family and `m` to `<= 1e-6`.  The precision rule is frozen at Checkpoint A from the R0 pilot and is a function of estimator precision only, never of observed discrepancy |
| `X7a` | **outside-assumption, A3 half** | all 16 `uniform` cells: `relative >= 0.5` and `z >= 10` |
| `X7b` | **outside-assumption, first-moment half** | all 16 `cauchy` cells demonstrate **non-existence**: the estimated relative standard error of `E_0[A_m]` does not decrease at the `n^{-1/2}` rate over a preregistered ladder of path budgets, and the truncated first moment `E[\|A_m\| 1{\|A_m\|<=K}]` grows without bound in `K` at a preregistered ladder of thresholds |
| `X8` | both frozen detectors covered | `{cusum@5, sr@520.886}` present |
| `X9` | at least five theorem-supported families | `>= 5` |
| `X10` | asymmetric family origin not a fixed point | `skewnormal4` classified `FIXED-POINT-NOT-AT-ORIGIN`, never `CLASSIFIED` at `0` |
| `X11` | **Gaussian cross-implementation consistency** | two-sample statistic `\|P4X - closed\| / hypot(se_{P4X}, se_{closed}) <= 4` on all 8 Gaussian frozen cells, using the closed campaigns' own published `gamma_tilde_se`.  The historical single-error statistic is **reported alongside** and gates nothing |
| `X12` | inherited certificates re-verify | all checks pass at 160 and `>= 256` bits |
| `X13` | inherited Lean re-verifies | 19 declarations, clean axiom set |
| `X14` | protected-tree integrity | every path outside the P4X namespace byte-identical to `HEAD`, recorded pre and post, untracked namespaces enumerated by digest |
| `X15` | no historical mutation | `p4_theory_generalization` tree object unchanged; `P4 = PARTIAL` unchanged in the root status table |

Verdict semantics, frozen before any result:

```text
P4X = CLOSED   iff X1-X15 all pass
P4X = PARTIAL  iff the integrity gates X1, X2, X14, X15 pass but a scientific
                   gate lands on an admissible weaker outcome
P4X = FAIL     iff an integrity gate fails, or a theorem-supported cell shows a
                   TRUE_THEOREM_CONTRADICTION
```

## 8. Resource stop rule

```text
R0  pilot, <= 4 CPU-hours.  Measure Route-B variance and finite-difference bias
    on the four cost-driving configurations (frozen/sr/t1p5, frozen/cusum/t1p5,
    reduced/sr/t1p5, frozen/sr/skewnormal4) on a fresh seed namespace.
    PUBLISH the pilot.  Freeze the X6 precision rule and the production path
    budgets from it.  Nothing else is frozen before R0 completes.

R1  production grid.  Envelope: 120 CPU-hours.
    STOP if the projected cost to reach Route-B relative SE <= 1 % on the
    frozen/sr/t1p5 configuration exceeds 60 CPU-hours by itself; in that case
    that configuration is carried as ARBITRATED under X6 and the campaign
    continues rather than expanding the envelope.

HARD STOP  total campaign envelope 200 CPU-hours.  If X6 cannot be met inside
    it, the honest outcome is P4X = PARTIAL with the cost limitation recorded.
    The envelope is NEVER raised after a result is seen.

PROHIBITED  any threshold change after a result is seen; any new theorem work;
    any new Lean declaration; any new certificate object; any Route-C or
    Route-D activity.
```

## 9. Historical preservation rules

* `P4_ORIGINAL_VERDICT = PARTIAL` is immutable and is restated in every P4X
  document.
* `level4/closure_proofs/p4_theory_generalization/` is byte-frozen.  Its ten
  failed cells, its sixteen `COUNTEREXAMPLE-NOT-DEMONSTRATED` cells, its three
  failed gates and its `closure_decision.json` are never edited, regenerated or
  reinterpreted.
* P4X gates are **new preregistered objects**.  P4X never describes itself as
  repairing, correcting or superseding a P4 gate.
* No `P1`-`P9`, `P8R`, `P9R`, `P5X` namespace is modified.
* `P5_RESIDUAL_STATUS = DOCUMENTED_LIMITATION` and
  `LEVEL4_GLOBAL_CLOSURE = NO` are restated; a P4X closure implies neither.
* `NOVELTY_STATUS = NOT_ESTABLISHED` throughout.
* Checkpoint A must record the destroyed `p4_final_disposition_audit`
  (sha256 `bda05c9c5ee5df2a7bfbe11ca1fb07432907378299fd36ea0b75cada68ffba34`),
  must derive its own disposition finding rather than claim to inherit one, and
  must state that a recovered copy of that artifact would take precedence.
