# P4X — successor feasibility and closure-boundary audit

```text
CLASSIFICATION        = PRE_SUCCESSOR_FEASIBILITY_AND_SCOPE_AUDIT
BINDING               = NO
P4_ORIGINAL_VERDICT   = PARTIAL   (immutable)
P4X_CAMPAIGN_STATUS   = NOT_OPENED
NOVELTY_STATUS        = NOT_ESTABLISHED
LEVEL4_GLOBAL_CLOSURE = NO
```

## 0. Isolation

| item | state |
|---|---|
| worktree | `/Users/suzhe/ReBaseGuard-p4x`, branch `p4x-feasibility-audit`, created from `main` |
| starting HEAD | `c123b9bb8f15d17650545b3fce4aca8a6b61093b` |
| tree at entry | clean (`git status --porcelain` empty) |
| concurrent writers | three other worktrees exist — `/Users/suzhe/ReBaseGuard` (main), `/Users/suzhe/ReBaseGuard-p5x-opt` (`p5x-compute-opt-r1`), `/Users/suzhe/ReBaseGuard-p9` (`p9-research`).  This audit writes to none of them and to no path outside its own namespace |
| P5X worktree | **not used** |
| protected historical P4 tree | intact, `HEAD:level4/closure_proofs/p4_theory_generalization = eede90383da44c250871b1bb97d12045c897c8d9` |
| P5/P5X archival trees | intact — see §22 |
| remote | `origin/main = c123b9b…` (identical to local `main`); `origin/p5x-compute-opt-r1 = c4fc5e7…`; `origin/sr-arb-certificate = 949415b…` |

Isolation is established.

## 1. Audit namespace

```text
level4/closure_proofs/p4x_generalization_boundary/feasibility_and_scope_audit/
```

No binding P4X checkpoint is created.  No P4X protocol is frozen.  No
production numerics are run.

## 2-3. The three failed gates, classified

The full obligation reconstruction is in `HISTORICAL_OBLIGATION_TABLE.md`.  This
section classifies only what failed, from the exact repository wording.

### Gate 6 — `all_theorem_supported_cells_pass`  (FAIL)

Literal criterion, `numerics/run_correspondence.py`:

```text
PASS iff relative_discrepancy <= 0.03  AND  z <= 4.0
```

Result: **86 / 96** theorem-supported cells pass.  The ten non-passing cells are
nine `t1p5` cells and one `skewnormal4` cell.  There is **no other family and no
other detector/window combination among the failures.**

| sub-population | cells | `\|z\|` | Route-B relative SE | classification |
|---|---|---|---|---|
| `t1p5`, `sr@20` and `sr@520.886` and `cusum@5` `m=1` | 9 | **0.35 – 1.49** (all statistically consistent) | **1.5 % – 23.3 %** | `GATE_OVER_SPECIFICATION` |
| `skewnormal4`, `sr@520.886`, `m=2` | 1 | **4.29** | 0.4 % | `NUMERICAL_ERROR` (finite-difference bias) |
| `TRUE_THEOREM_CONTRADICTION` | **0** | — | — | — |

**The nine `t1p5` cells.**  The gate asks for 3 % agreement from an estimator
whose own relative standard error reaches 23.3 %.  Every one of the nine is
*statistically consistent* (`\|z\| <= 1.49` against a limit of 4).  Route Q —
deterministic quadrature, no sampling error — reproduces the identity for
`t1p5` at every window length to nine significant figures.  The two routes
agree as well as their errors permit.  This is a defect in the accuracy gate's
specification relative to the estimator's precision, not evidence about the
identity.

**The `skewnormal4` cell.**  Genuinely inconsistent as generated
(`6.3875 ± 0.0284` vs `6.5561 ± 0.0270`, combined `\|z\| = 4.29`).  Independent
adjudication *tested* rather than assumed the explanation and found finite-step
bias in the Richardson correction on an asymmetric (non-odd) map:

| replay | `m=2` estimate | distance from original Route A |
|---|---|---|
| Route B, steps `.025/.0125`, 960k paths | `6.5170 ± 0.0391` | moves toward Route A |
| Route B, steps `.0125/.00625`, 480k paths | `6.4342 ± 0.0785` | `0.56` combined SE |
| fresh Route A, 1.6M paths | `6.4549 ± 0.0452` | `0.23` combined SE from the above |

At the smallest step pair all four windows agree with the original Route A
within `0.09 – 0.56` combined standard errors.  The anomaly is resolved; the
frozen cell and its literal gate were correctly left failed.

Charter classification: **`NUMERICAL_CORRESPONDENCE_GAP`**, with the dominant
component **`GATE_OVER_SPECIFICATION`**.  Not `SCIENTIFIC_THEOREM_GAP`.

### Gate 7 — `all_outside_assumption_cells_demonstrate_failure`  (FAIL)

Literal criterion:

```text
COUNTEREXAMPLE-CONFIRMED iff relative_discrepancy >= 0.5  AND  z >= 10.0
```

Result: **16 / 32**.

| family | cells | verdict | what actually happened |
|---|---|---|---|
| `uniform` (moving support, breaks A3) | 16 / 16 | `COUNTEREXAMPLE-CONFIRMED` | 100 % relative at 468–517 standard errors, at both frozen detectors and every `m`; and the exact rational defect `2` is Arb-certified |
| `cauchy` (no first moment, breaks A5/A7) | 0 / 16 | `COUNTEREXAMPLE-NOT-DEMONSTRATED` | nothing converges.  `E_0[A_1] = 10.0 ± 14.6`.  Standard errors are comparable to or larger than the estimates on every cell |

The gate was written to detect a **deterministic defect**: a large *and
statistically sharp* two-route disagreement.  That is exactly the signature of
the moving-support failure `F1`, and `F1` produces it.  It is structurally
**not** the signature of the first-moment failure `F2`.  `PROOF.md` §10 proves
that for Cauchy under the frozen CUSUM `E\|A_1\| = infinity`, i.e. the estimand
*does not exist*; a two-sample `z` statistic formed from two divergent Monte
Carlo estimators cannot reach `z >= 10` however many paths are spent.  The gate
asks the wrong question of half its own population.

Charter classification: **`NEGATIVE_TEST_DESIGN_GAP`** + **`GATE_OVER_SPECIFICATION`**.
Not `SCIENTIFIC_THEOREM_GAP`, and not `ASSUMPTION_BOUNDARY_GAP` — see §8 and §11.

### Gate 11 — `gaussian_consistency_with_closed_core`  (FAIL)

Literal criterion, `derive_closure.py`: `z = |P4 - closed| / se_{P4} <= 4.0`.
The denominator is **P4's own standard error alone**, which treats the closed
Priority-1/2 Monte Carlo point as exact.  That is not the right test for
comparing two Monte Carlo estimates, and `derive_closure.py` says so in a
comment.  It was deliberately left unchanged after the data were seen so that no
gate outcome could be improved by editing it — a correct integrity decision that
also guaranteed the gate would fail.

| detector | `m` | closed P1/P2 | P4 independent | signed rel. diff | gate `z` (single error) | correct `z` (combined error) |
|---|---|---|---|---|---|---|
| cusum@5 | 1 | `15.916540 ± 0.059905` | `15.877342 ± 0.016821` | `-0.246 %` | 2.33 | **0.63** |
| cusum@5 | 2 | `13.264825 ± 0.050152` | `13.247492 ± 0.015087` | `-0.131 %` | 1.15 | **0.33** |
| cusum@5 | 3 | `11.957078 ± 0.043161` | `11.914735 ± 0.013733` | `-0.354 %` | 3.08 | **0.93** |
| cusum@5 | 5 | `10.226364 ± 0.035237` | `10.184212 ± 0.012062` | `-0.412 %` | 3.49 | **1.13** |
| sr@520.886 | 1 | `17.453571 ± 0.065881` | `17.258937 ± 0.020260` | `-1.115 %` | 9.61 | **2.82** |
| sr@520.886 | 2 | `14.500510 ± 0.056725` | `14.358610 ± 0.016104` | `-0.979 %` | 8.81 | **2.41** |
| sr@520.886 | 3 | `12.972655 ± 0.049011` | `12.831340 ± 0.013049` | `-1.089 %` | 10.83 | **2.79** |
| sr@520.886 | 5 | `11.048526 ± 0.041047` | `10.922955 ± 0.009725` | `-1.137 %` | 12.91 | **2.98** |

Worst gate statistic **12.91**; worst correctly-specified statistic **2.98**,
against the same limit of 4.  The residual discrepancy is confined to SR, is
one-signed, and is **1.0 – 1.1 % low**.

Independent adjudication then reran the **frozen Priority-2 score
implementation itself** on 1.6M fresh paths:

| `m` | fresh P2 implementation | P4 Route A | combined `\|z\|` |
|---|---|---|---|
| 1 | `17.3132 ± 0.0363` | `17.2589 ± 0.0203` | 1.31 |
| 2 | `14.4055 ± 0.0309` | `14.3586 ± 0.0161` | 1.35 |
| 3 | `12.8688 ± 0.0268` | `12.8313 ± 0.0130` | 1.26 |
| 5 | `10.9575 ± 0.0210` | `10.9230 ± 0.0097` | 1.49 |

This rules out a recurrence, alarm, window or convention mismatch at the
reported scale.  The older 240k-path P2 vector was a **correlated high Monte
Carlo realization across `m`**, and P4 used 3.2M paths against it.

Charter classification: **`CERTIFICATION_GAP`** (a mis-specified comparison
statistic between two uncertified Monte Carlo estimates), with a residual
**`NUMERICAL_CORRESPONDENCE_GAP`** component.  **Not** mathematical, **not**
convention-related, **not** interpolation-related.  Repairable without changing
scientific meaning.

### Summary

```text
SCIENTIFIC_THEOREM_GAP        : 0 gates
NUMERICAL_CORRESPONDENCE_GAP  : gate 6 (primary), gate 11 (residual)
CERTIFICATION_GAP             : gate 11 (primary)
ASSUMPTION_BOUNDARY_GAP       : 0 gates
NEGATIVE_TEST_DESIGN_GAP      : gate 7 (primary)
GATE_OVER_SPECIFICATION       : gates 6, 7, 11 (all three carry it)
GOVERNANCE_ONLY               : 0 gates
```

**All three failed gates are measurement-and-specification objects.  None is a
theorem object.**

## 4. The true scientific core

The strongest theorem P4 established, accepted verbatim by independent
adjudication:

```text
Under (A1)-(A7), for every fixed m >= 1,

    g_m'(0)        = -E_0[ A_m sum_{t<=tau} psi(Z_t) ]
    F'_{rho,m}(0)  = rho (1 - Gamma_{D,m,f})
```

The exact scope of that identity — the object §4 of the charter asks about —
audits as follows.

| level | what is reached | status |
|---|---|---|
| **A** symmetric differentiable location family | everything below **plus** the fixed point at the origin (`G4`), hence the P3 stability map applies unchanged | **proved** |
| **B** general differentiable location family, score formulation | `G1`, `G1'`, `G2`, `G3a` with **no symmetry assumption**.  This is the campaign's headline | **proved** |
| **C** general dominated parametric family | the interchange argument uses no location structure; reached, and it is what the Lean bridge formalizes.  Deliberately **not** promoted to the headline: at Level C the score has no `-f'/f` interpretation, so `G2` disappears, and `L1`-`L5` become uncheckable | **reached, not claimed** |

Charter classification of the derivative identity:

* **A — theorem already proved:** `G1a`, `G1b`, `G1'`, `G2`, `G3a`, `G4`, for
  every `m >= 1`, both frozen detectors, under (A1)-(A7) discharged by `L1`-`L5`
  for those two detectors.  Independently re-derived.  Lean-verified at the
  bridge (`hasDerivAt_stoppedMean`), which *proves* the step Track 3A/3B
  assumed.  Arb-certified in three exact instances.
* **B — theorem needing stronger assumptions:** none, for the frozen claim.
  (A6) is deliberately *weaker* than P1/P2's hypothesis, not stronger.
* **C — numerical correspondence only:** the *values* `Gamma_{D,m,f}` at the
  frozen operating points, every family including the Gaussian control.  This
  was already the evidence boundary at P1, P2 and P3, and P4 did not move it.
* **D — symmetry/reflection needed for the zero fixed point and P3 reuse:**
  `G4` requires `f` even and the detector reflection-equivariant.  P4 refuses to
  classify asymmetric cells at the origin, and gate 10 asserts that refusal.

**The gap is not in the theorem.**

## 5. Original P4 gap vs stronger stretch

```text
REQUIRED_TO_REPAIR_P4
  R1  a two-route theorem-supported correspondence whose accuracy criterion is
      attainable by the estimator that has to meet it, arbitrated by Route Q
  R2  an outside-assumption demonstration whose failure signature matches the
      failure mode the theorem actually proves, separately for A3 (defect) and
      for the first moment (non-existence)
  R3  a cross-implementation consistency test against the closed Gaussian gains
      that is a correctly specified two-sample statistic

OPTIONAL_GENERALIZATION_STRETCH   (explicitly out of scope for repair)
  S1  the G3 iff characterisation the adversarial review declined
  S2  promoting Level C to the headline statement
  S3  ARL-matched cross-family comparison (CLOSURE_REPORT.md limitation 1)
  S4  locating the asymmetric fixed point e* and classifying there via G1'
  S5  infinite-horizon interval certification of any frozen CUSUM or SR gain
  S6  a novelty adjudication
```

Two symmetric prohibitions follow.

* Do **not** turn "general location-family theorem" into a universal theorem.
  P4 never claimed distribution-freeness or detector-universality, and three
  frozen negative claims assert that it did not.  `S1`, `S2` and `S4` are new
  science belonging to a new priority, not P4 repair.
* Do **not** narrow the frozen universal claim post hoc.  `G1` is stated for
  **every** `m >= 1` and for a **general** regular location family; a successor
  may not restrict it to `m ∈ {1,2,3,5}` or to the six measured families
  because those are the cells that happen to be measurable.  The numerical grid
  is evidence for the theorem, never its scope.

## 6. Prior P4 disposition — and a material integrity finding

**The historical P4 final-disposition audit no longer exists.**

`level4/closure_proofs/p4_final_disposition_audit/` was present as an
**untracked** working-tree namespace at P5X Checkpoint A (`eea2bfb`) and at
Checkpoint B, with content digest

```text
sha256  bda05c9c5ee5df2a7bfbe11ca1fb07432907378299fd36ea0b75cada68ffba34
```

recorded in
`p5x_global_nonlinear_dynamics/results/integrity/protected_tree_manifest_pre.json`
under `untracked_namespaces_outside_p5x`.  It was never committed.  It was
removed from the working tree — together with `p5_final_disposition_audit/` and
P5X's own `results/ra_selftest.json` — by an external `git clean` or equivalent
run alongside commit `31132e8`, an event P5X records in
`INCIDENT_EXTERNAL_TREE_CHANGE.md` §1(b).  Git holds no copy and `git fsck`
shows no recoverable tree.

Consequences, stated exactly:

* the **wording** of any P4 disposition ruling, and of any prohibition on
  `P4R` / `P4.1`, **cannot be read**.  This audit does not guess it;
* its **identity is still provable** if a copy exists outside this repository —
  the digest above is a complete verification key;
* **nothing in P4's own surviving tree contains such a prohibition.**  A full
  text search of the repository for `P4R`, `P4.1`, `p4r`, `p4_1` returns
  **zero** matches outside the manifest reference above.

What *can* be established about the governance semantics the repository
actually operated under:

1. The parallel P5 disposition audit is quoted verbatim in a surviving P5X
   document (`FEASIBILITY_AUDIT.md`, "authoritative disposition" row):
   `P5_PARTIAL_SHOULD_BE_FINAL`, `P5R_LAUNCHED = NO`,
   `NEW_SCIENCE_REQUIRED = YES for literal G3/G7/G9`.  It ruled the missing
   work **new science belonging to a new priority** — not forbidden work.
2. P5X was then opened as a successor campaign *under that ruling*, was
   committed, ran through eleven checkpoints and was archivally completed.  No
   objection is recorded anywhere.
3. P5X's own final disposition audit (`c6a82cc`,
   `final_scope_disposition_audit/AUDIT.md` §13) states, unprompted:

   > P5 remains one of the unresolved Level-4 scientific lines.  **P4X** and
   > residual P5 coexist: P4X is not the only remaining repair campaign.

   A P4X successor is therefore *anticipated by name* in the surviving
   governance record.
4. P4's own `CLOSURE_REPORT.md` §10 limitation 1 names "a follow-up campaign
   with per-family threshold calibration" as the fix for one of its
   limitations.  P4 itself contemplates successor campaigns.

**Reading of the prohibition: A.**  The disposition semantics in force are *no
retroactive repair or amendment of the historical priority* — not *no successor
scientific campaign at all*.  Evidence: items 1-4 above, plus the complete
absence of any surviving prohibitive text.

**Conditionality, stated honestly.**  This reading is a structural inference
from the surviving record, not a quotation of the P4 ruling, because that
ruling is destroyed.  If a copy of the artifact hashing to `bda05c9c…` is
recovered and it forbids a successor campaign outright, that ruling takes
precedence over this inference and `P4X_GOVERNANCE_VALID` must be re-evaluated.
A P4X Checkpoint A must record this loss explicitly and derive its own
disposition finding rather than claim to inherit one.

## 7. Successor closure semantics

For the target status

```text
P4_ORIGINAL_VERDICT   = PARTIAL                       (unchanged)
P4X_SUCCESSOR_VERDICT = CLOSED
P4_SCIENTIFIC_LINE    = CLOSED_BY_SUCCESSOR_CAMPAIGN
```

the minimum load-bearing set, drawn **only** from historical P4 dependencies:

```text
P4X_CORE_REQUIRED = {
  C1  INHERIT, do not reprove: G1a, G1b, G1', G2, G3a (narrowed), G4 under
      (A1)-(A7), with L1-L5 discharged for the frozen CUSUM and the frozen SR.
      Cited from p4_theory_generalization, byte-unchanged.

  C2  A theorem-supported two-route numerical correspondence over the same
      96-cell design (2 layers x 2 detectors x 6 families x m in {1,2,3,5}),
      passing a pass rule that is attainable by the estimator that must meet it
      and is frozen before P4X's production run.

  C3  Route Q as the deterministic arbiter for every cell where Routes A and B
      disagree, with its explicit non-frozen-detector disclaimer preserved.

  C4  An outside-assumption demonstration split by proved failure mode:
        (a) A3 / moving support  -> exact defect, already CONFIRMED 16/16 and
            Arb-certified as the exact rational 2;
        (b) first moment / Cauchy -> a divergence demonstration (non-existence),
            not a sharp two-route defect.

  C5  A cross-implementation consistency test against the closed Gaussian gains
      using the two-sample combined-error statistic and the closed campaigns'
      own published standard errors, with a preregistered statement that a
      failure of this test is evidence about Monte Carlo realizations and never
      a licence to alter a frozen value.

  C6  Re-verification, not extension, of the inherited formal and certified
      layers: 19 Lean declarations compile with axioms exactly
      {propext, Classical.choice, Quot.sound}; the three Arb objects pass.

  C7  Protected-tree integrity: every P1-P9, P8R, P9R, P5X and
      p4_theory_generalization path byte-identical to HEAD throughout.
}
```

Not in the set, and deliberately: any new theorem; any new Lean declaration;
any new interval certificate; any change to the evidence boundary.

## 8. Theorem-boundary audit, A1-A7

The charter's crucial question: is a *failure demonstration outside* each
assumption actually required for closure, or was the historical negative-cell
gate a robustness gate?

| id | necessary or sufficient? | is failure-outside required by a frozen claim? | load-bearing? |
|---|---|---|---|
| A1 parameter-free path functional | **sufficient**.  Needed so the change of measure restricts to `F_tau`.  No necessity claimed | **no** | engineering |
| A2 a.s. finiteness | **sufficient**, discharged by `L1`.  No necessity claimed | **no** | engineering |
| A3 local common support / absolute continuity | **sufficient** for the theorem — and P4 **separately claims sharpness**: `F1` proves the identity is *false* without it, with exact defect `2` | **YES** | **scientifically load-bearing** — and already satisfied: 16/16 uniform cells CONFIRMED, plus an exact rational Arb certificate |
| A4 differentiability of `L_tau` at zero | **sufficient**, discharged by `L5`.  Strictly *weaker* than P1/P2's neighbourhood hypothesis, which is false for Laplace.  No necessity claimed | **no** | engineering |
| A5 integrability of `A_m`, `A_m S` | **sufficient**, discharged by `L2`+`L3` or `L2`+`L4`.  P4 **separately claims** a first-moment boundary via `F2`: without it the *map* is undefined | **partly** — the claim is *non-existence of the estimand*, and it is already proved analytically in `PROOF.md` §10 | **the analytic proof is load-bearing; the Monte Carlo cells are not** |
| A6 Lipschitz stopped likelihood | **sufficient**, discharged by `L3`/`L4`.  Deliberately weaker than P1/P2.  No necessity claimed | **no** | engineering |
| A7 fresh reference unbiased | **sufficient** for the affine map form; forces `E[eps] = 0` and `E\|eps\| < infinity` before any derivative | **no** (its first-moment content is `F2`, above) | engineering |

Conclusion for §8:

> The historical gate `all_outside_assumption_cells_demonstrate_failure` is
> **load-bearing on its A3 half and already passes there**, and is a
> **robustness/engineering gate on its A5 half**, where the load-bearing
> evidence is an analytic proof that the campaign already has.

No frozen P4 claim requires demonstrating failure everywhere outside the
assumptions.  Five of the seven assumptions carry no sharpness claim at all.

## 9. Gaussian consistency audit

Traced in full in §3, gate 11.  In the charter's terms:

| question | answer |
|---|---|
| what quantity was compared | `Gamma_{D,m,gaussian}` at the two frozen operating points, `m ∈ {1,2,3,5}`, P4's independent reimplementation against the closed value |
| against which closed result | `m_rho_stability_priority3/results/stability_map.json`, which carries the P1 (CUSUM) and P2 (SR) Gaussian gains and their `gamma_tilde_se` |
| mathematical mismatch? | **no** — the estimands are identical; `psi(z) = z` makes `S_tau^psi = T_tau` exactly |
| convention mismatch? | **no** — a fresh 1.6M-path run through the **frozen P2 implementation itself** agrees with P4 within `1.26 – 1.49` combined SE, ruling out recurrence, alarm and window differences at the reported scale |
| interpolation-related? | **no** — no interpolation is involved on either side |
| numerical? | **yes, in part** — the older 240k-path P2 vector is a correlated high realization; P4 used 3.2M paths |
| gate-design-related? | **yes, primarily** — the gate divides by P4's SE alone, treating an uncertified Monte Carlo point as exact |
| repairable without changing scientific meaning? | **yes** |

Exact remaining discrepancy, from existing artifacts only, no new computation:

```text
CUSUM :  signed relative -0.131 % .. -0.412 %,  combined |z| 0.33 .. 1.13
SR    :  signed relative -0.979 % .. -1.137 %,  combined |z| 2.41 .. 2.98
vs the fresh 1.6M-path frozen-P2 replay:        combined |z| 1.26 .. 1.49
gate limit 4.0 on both statistics
```

The SR column remains one-signed at ~1 %.  Against the old P2 vector it sits at
2.4-3.0 combined SE; against a fresh replay of P2's own code it sits at
1.3-1.5.  Nothing here is outside Monte Carlo scatter, and nothing here licenses
touching a frozen value.

## 10. Theorem-supported cell failures

Every one of the ten, classified.

| layer | detector | family | `m` | rel | `\|z\|` | Route-B rel SE | classification |
|---|---|---|---|---|---|---|---|
| reduced | sr@20 | t1p5 | 1 | 5.276 % | 1.29 | 3.72 % | `GATE_OVER_SPECIFICATION` |
| reduced | sr@20 | t1p5 | 2 | 3.874 % | 1.35 | 2.63 % | `GATE_OVER_SPECIFICATION` |
| reduced | sr@20 | t1p5 | 3 | 3.645 % | 1.47 | 2.09 % | `GATE_OVER_SPECIFICATION` |
| reduced | sr@20 | t1p5 | 5 | 3.132 % | 1.44 | 1.53 % | `GATE_OVER_SPECIFICATION` |
| frozen | cusum@5 | t1p5 | 1 | 3.155 % | 0.35 | 8.10 % | `GATE_OVER_SPECIFICATION` |
| frozen | sr@520.886 | t1p5 | 1 | 25.637 % | 1.47 | 23.33 % | `GATE_OVER_SPECIFICATION` |
| frozen | sr@520.886 | t1p5 | 2 | 18.717 % | 1.49 | 15.36 % | `GATE_OVER_SPECIFICATION` |
| frozen | sr@520.886 | t1p5 | 3 | 14.706 % | 1.44 | 11.84 % | `GATE_OVER_SPECIFICATION` |
| frozen | sr@520.886 | t1p5 | 5 | 11.044 % | 1.45 | 8.46 % | `GATE_OVER_SPECIFICATION` |
| frozen | sr@520.886 | skewnormal4 | 2 | 2.571 % | **4.29** | 0.41 % | `NUMERICAL_ERROR` (finite-step bias, resolved) |

```text
TRUE_THEOREM_CONTRADICTION     : 0
NUMERICAL_ERROR                : 1
CERTIFICATE_WIDTH              : 0
FINITE_PRECISION               : 0   (subsumed under GATE_OVER_SPECIFICATION)
CONVENTION_MISMATCH            : 0
ASSUMPTION_NOT_ACTUALLY_SATISFIED : 0
GATE_OVER_SPECIFICATION        : 9
UNKNOWN                        : 0
```

Two independent controls make `ASSUMPTION_NOT_ACTUALLY_SATISFIED = 0` for
`t1p5` specifically: `L3` requires only a `1+eta` innovation moment, and
Student-`t` with `nu = 1.5` has a finite mean; and Route Q reproduces the
identity for `t1p5` at every `m` with no sampling error.

**P4X is therefore scientifically cheap, not dangerous.**  There is no cell at
which the identity is under threat.

## 11. Outside-assumption cells

The theorem's logical form is `assumptions => identity`.  Success outside
sufficient assumptions is not a problem, and failure outside them is not
mathematically required — **unless the campaign separately claims necessity or
sharpness.**  P4's exact position:

* it claims **no** necessity for A1, A2, A4, A6, A7;
* it claims sharpness for **A3** (`F1`: identity provably false under moving
  support, exact defect `2`);
* it claims a first-moment boundary for **A5/A7** (`F2`: `E|A_1| = infinity`,
  the map is undefined).  This is a *non-existence* claim, not a
  *false-identity* claim.

The gate applied one failure signature — large **and statistically sharp**
two-route disagreement — uniformly to both.  That signature is correct for
`F1` and is structurally unreachable for `F2`: when neither route converges,
the standard errors grow with the estimates and `z` does not.

```text
Did the historical gate accidentally test necessity of sufficient assumptions?
  Partly: it applied a necessity-shaped test to A5, whose proved boundary claim
  is non-existence rather than falsity.

Classification: OVER-SPECIFIED GATE on its Cauchy half.
                Correctly specified and PASSING on its uniform half.
```

## 12. Claim dependency graph

```text
                (A1)-(A7)  [stated; discharged for the two frozen detectors
                            by L1-L5, which are human proofs]
                     |
                     v
   THEOREM LAYER  G1a --> G1b --> G1'          [PROVED, independently re-derived]
                     |      |
                     |      +--> G4 (symmetry) --> P3 reuse: rho_c = 1/|1-Gamma|
                     |                             [PROVED; needs even f and a
                     |                              reflection-equivariant detector]
                     +--> G2 (neutrality, family-free)   [PROVED]
                     +--> G3a (decomposition identity)   [PROVED; sign narrowed]
                     |
                     v
   EVIDENCE LAYER
        Route Q  arbiter, memoryless detector, 24 cells, worst 4.3e-09  [CLOSED]
        Route N  neutrality control, 72 cells, worst |z| 2.64 < 4       [CLOSED]
        Lean     19 declarations, clean axioms                          [CLOSED]
        Arb      3 objects at 160 bits, re-verified at 256              [CLOSED]

        Routes A vs B, 96 theorem-supported cells                  ==> OPEN EDGE 1
        outside-assumption failure demonstration, 32 cells         ==> OPEN EDGE 2
                (uniform half CLOSED; cauchy half OPEN)
        cross-implementation consistency vs closed Gaussian gains  ==> OPEN EDGE 3
                     |
                     v
   CLAIM LAYER   "the closed Gaussian mechanism generalizes to regular
                  one-dimensional location families at both frozen detectors,
                  for every m >= 1"                         [P4 = PARTIAL]
                     |
                     v
   REPOSITORY    P4-STATUS = PARTIAL --> GLOBAL-CLOSURE (status propagation only)
```

Every open edge is on the **evidence** layer.  The theorem layer has no open
edge.  P4 is a scientific leaf: nothing outside its own sub-graph takes it as a
premise, so closing it changes no downstream claim — only the global-closure
status node.

## 13. Smallest open cut set

```text
P4X_SMALLEST_OPEN_CUT_SET = {
  CUT-1  the pass rule of the theorem-supported two-route correspondence gate
         must be attainable by the estimator that has to meet it
         (concretely: Route-B relative SE reaches 23.3 % where the gate demands
          3 % accuracy)

  CUT-2  the outside-assumption gate must test the failure signature the
         theorem proves, separately for A3 (defect) and for the first moment
         (non-existence)

  CUT-3  the cross-implementation consistency gate must use the two-sample
         combined-error statistic rather than treating a closed Monte Carlo
         point as exact
}
```

Three elements.  All three are **gate-specification objects**.  `CUT-2` and
`CUT-3` cost essentially nothing.  `CUT-1` is the only element with a compute
price, and that price is concentrated in a single configuration
(`frozen / sr@520.886 / t1p5`, Route B).

## 14. Feasibility options

Cost anchor for all four rows: the **entire** historical P4 numerical campaign —
Routes A, B, Q, N, both layers, both detectors, all eight families, all four
windows — took `6604 s ≈ 1.83 h` (`results/correspondence.json`,
`elapsed_seconds`).

### ROUTE A — theorem-boundary cleanup only

| axis | assessment |
|---|---|
| mathematical risk | none; nothing new is proved |
| implementation | ~none |
| certification | none |
| CPU | ~0 |
| wall time | hours |
| new Lean | none |
| new Arb | none |
| P(true contradiction) | ~0 |
| **closes the cut set?** | **NO — 0 of 3.** All three cuts are on the evidence layer and Route A touches none of them |

Useful as documentation.  **Does not close the scientific line.**

### ROUTE B — theorem + corrected numerical correspondence  *(recommended)*

Inherit the theorem unchanged; re-measure with correctly specified gates:
precision-attainable correspondence rule with Route-Q arbitration; split
outside-assumption gate; two-sample Gaussian consistency statistic.

| axis | assessment |
|---|---|
| mathematical risk | **low**.  Route Q already reproduces the identity for all six families including `t1p5` to `4.3e-09`; the one inconsistent cell was already traced to finite-step bias and resolved to `0.56` combined SE |
| implementation | **moderate**.  The simulator, all four route drivers, the closure deriver and 137 passing tests already exist and are byte-frozen.  New code is a variance-reduction / path-budget upgrade on Route B and three gate re-specifications |
| certification | **none new** |
| CPU | dominated by one configuration.  Reaching `<= 1 %` Route-B relative SE at `frozen/sr@520.886/t1p5` needs `~ (23.33)^2 ≈ 544x` its historical 960k paths by brute force; `frozen/cusum@5/t1p5` needs `~ 66x`; `reduced/sr@20/t1p5` needs `~ 14x`.  Against a 1.83 h whole-grid baseline this lands in **tens of CPU-hours**, and could reach `~10^2` CPU-hours if brute force is the only lever.  **Bounded and benchmarkable** |
| wall time | days, not months; the batch structure already parallelizes |
| new Lean | **none** |
| new Arb / interval | **none** |
| P(true contradiction) | **low** |
| **closes the cut set?** | **YES — 3 of 3** |

### ROUTE C — theorem + correspondence + counterexamples / sharpness

Route B plus a rigorous treatment of the Cauchy non-existence (a truncated-moment
divergence certificate, or an exact Arb witness for a memoryless-detector Cauchy
instance), and possibly a sharpness statement for A3 beyond the uniform example.

| axis | assessment |
|---|---|
| mathematical risk | **moderate**.  Proving *necessity* is materially harder than the *sufficiency* the theorem needs |
| implementation | Route B plus a new certificate object |
| certification | one new Arb object |
| CPU | Route B plus a small increment |
| new Lean | optional |
| P(true contradiction) | low; the real risk is **scope creep** — this is the P5X failure mode |
| **required for closure?** | **NO.**  `F1` and `F2` are already proved analytically, and `F1` is already Arb-certified.  §8 shows no frozen claim requires more |

### ROUTE D — stronger general location-family theorem

Promote Level C to the headline; prove the `G3` iff; drop symmetry from `G4`;
locate the asymmetric fixed point `e*`; ARL-matched cross-family comparison.

| axis | assessment |
|---|---|
| mathematical risk | **high**.  The `G3` converse is an all-path functional characterisation the adversarial review explicitly declined.  Locating `e*` for the skew-normal under a frozen detector is a genuinely open nonlinear problem, adjacent to what P5X could not certify |
| implementation / certification / CPU | unbounded |
| new Lean | substantial (the measure-theoretic construction Lean deliberately omits) |
| P(true contradiction) | low, but P(campaign fails on cost) is **high** |
| **admissible as P4 repair?** | **NO.**  It changes the original scientific question.  §5 classifies `S1`, `S2`, `S4` as new science for a new priority |

## 15. Lean requirement

Already formalized: 19 declarations; axioms exactly `propext`,
`Classical.choice`, `Quot.sound`; no `sorry`, no `sorryAx`, no project axiom;
and the load-bearing `hasDerivAt_stoppedMean`, which **proves** from Mathlib's
`hasDerivAt_integral_of_dominated_loc_of_lip` the bridge that Track 3A/3B
assumed and that P1/P2 proved only through the stronger pointwise-derivative
variant Laplace does not satisfy.

Deliberately not formalized: the probability space, filtration, stopping time
and stopped sigma-field; that `prod f(Z_t+e)/f(Z_t)` is the Radon-Nikodym
derivative on `F_tau`; the `L1`-`L5` discharges; any `Gamma` value; the
integration-by-parts identities behind `G2`; the `F1`/`F2` failure modes.

```text
P4X_LEAN_REQUIREMENT = NONE_NEW
```

Reason: every open edge is a numerical or gate-specification object.  Lean
evaluates no gain and certifies no Monte Carlo number, so **no Lean declaration
can move any element of the cut set.**  Formalizing the measure-theoretic
construction is a Route-D stretch, not a repair.  P4X's obligation is
re-verification: recompile the inherited 19 declarations and re-assert the axiom
audit as an inherited gate.

## 16. Certification requirement

Existing: three Arb objects at 160 bits, all checks passing, independently
re-verified at 256 bits — the unbounded-horizon Laplace closed form
`Gamma_1 = 1 + 2sqrt(2)`; the uniform moving-support exact rational defect `2`;
the finite-support bounded-score tilt witness with `E[Q_5] = -1/10 < 0`.

Not certified, explicitly and since P1: every frozen CUSUM and SR gain.

```text
P4X_CERTIFICATE_REQUIREMENT = NO_NEW_CERTIFICATION_BEYOND_RE-VERIFICATION
```

Two reasons, both binding.  First, requiring interval certification of frozen
`Gamma` values would **raise** an evidence boundary that P1, P2 and P3 never
moved — a post-hoc change to the original scientific meaning in the *stricter*
direction, which §5 prohibits as firmly as weakening.  Second, it is precisely
the P5X over-engineering pattern: P5X spent rounds R3-R8 plus six audits on
certification method R&D and never ran its affordable production lane.

A finite set of correspondence points, arbitrated by Route Q, is what P4X needs
— not an interval certification over parameter families, and not an analytic
exact reduction.

## 17. Novelty

```text
NOVELTY_STATUS = NOT_ESTABLISHED
```

P4's own `NOVELTY_AUDIT.md` returns `NOVELTY-NOT-ADJUDICATED`: no internet
access, no literature search, therefore no verdict.  P4X is a closure campaign,
not a novelty audit, and must not claim otherwise.

## 18. Successor-governance test

Applying the post-hoc-narrowing test that P5X's own disposition audit used
(`final_scope_disposition_audit/AUDIT.md` §8):

| question | answer |
|---|---|
| would a P4X `CLOSED` verdict require changing the historical P4 verdict? | **No.**  P4 stays `PARTIAL`, immutable, exactly as P5X kept `P5 = PARTIAL` |
| would it require changing historical failed artifacts? | **No.**  `closure_decision.json`, `correspondence.json`, the ten failed cells and the sixteen Cauchy cells all stay byte-identical |
| would it require changing frozen theorem meaning? | **No.**  P4X inherits `G1`-`G4` verbatim and reproves nothing |
| would it require weakening a requirement that was load-bearing before the result? | **Not for P4's gates** — they are untouched and stay failed.  **This is the live risk for P4X's own gates**, see below |
| does P4X add new successor evidence under a fresh preregistered scope while preserving `P4 = PARTIAL`? | **Yes** |

```text
P4X_GOVERNANCE_VALID = YES
```

subject to the §6 conditionality (the destroyed P4 disposition ruling), and to
one binding design constraint:

> **The threshold risk is real and must be engineered out, not argued away.**
> A precision-aware pass rule chosen *after* seeing that `t1p5`'s Route-B
> standard error is 23 % would be exactly the prohibited post-hoc move.

Two mitigations, and P4X should adopt **both**:

1. **Buy the precision rather than move the threshold.**  Where affordable, run
   enough paths and enough variance reduction that Route-B relative SE falls
   below 1 % and the *unchanged* 3 % criterion becomes reachable.  This requires
   no threshold change at all and is the honest route.
2. **Where it is not affordable, preregister a rule derived from estimator
   precision, never from observed discrepancy**, on a fresh independently
   seeded pilot published before the production run — and state plainly that a
   3 % accuracy demand on a 23 %-precision estimator is a design error
   independent of its outcome.

The same principle governs `CUT-3`: P4X should report *both* statistics — the
historical single-error one for continuity and the correctly specified
two-sample one as its gate — and must never present this as repairing P4's
gate.  P4X's gates are **new preregistered objects**, never edits of P4's.

## 19. Cost / risk classification

```text
P4X_FEASIBILITY    = STRONG
P4X_EXPECTED_SCALE = LIGHT
```

`STRONG` because: the theorem is proved and independently adjudicated; zero
cells contradict it; all four evidence routes, the simulator, the Lean file, the
Arb certificate and 137 passing tests already exist; and the entire open surface
is three gate specifications, two of which are free.

`LIGHT` because: no new theorem, no new Lean, no new certificate, and a compute
requirement anchored to a measured 1.83 h whole-grid baseline.  **Honest
caveat:** the single `frozen / sr@520.886 / t1p5` Route-B configuration is the
cost driver and needs `~544x` its historical path budget by brute force.  If
brute force is the only lever, the campaign edges toward `MEDIUM`
(`~10^2` CPU-hours).  A cheap variance-reduction pilot must be the first step
and must precede any frozen resource envelope — this is the direct lesson from
P5X, which committed to a certification architecture before benchmarking it.

This is **not** `P5X_LIKE`.  P5X needed a new global mechanism theorem and an
interval-certification architecture whose worst required state grid was `~4708`
and out of budget.  P4X needs neither a theorem nor a certificate.

## 20. Decision

```text
P4X_DECISION = OPEN_P4X_NARROW_SUCCESSOR      (CASE B)
```

**Smallest sufficient reason:** P4's scientific core is already proved and
independently adjudicated, and all three failed gates are gate-specification and
estimator-precision defects with **zero** theorem-contradiction cells — so the
entire repair is a bounded numerical re-measurement plus two correctly specified
gates, requiring no new theorem, no new Lean spine and no new certificate.

Why not the alternatives:

* **CASE A (full successor)** — a full-scope successor invites Route-D creep
  (`G3` iff, the asymmetric fixed point, ARL matching).  Those are new science
  for a new priority, and pulling them into a repair campaign is how P5X ended
  `PARTIAL`.
* **CASE C (one more cheap audit)** — this audit already answers every question
  a further cheap audit would ask: the cells, the gates, the assumption map, the
  dependency graph, the cut set and the costs are all quantified from existing
  artifacts.  One thing a further audit *cannot* recover is the destroyed
  disposition ruling; waiting does not help, and §6 handles it by conditionality.
* **CASE D (do not open)** — the gap is genuinely closable, cheaply, without
  touching anything frozen.  Declining would leave a repairable line open for no
  reason.

## 21. Level-4 implication

```text
P5_RESIDUAL_STATUS        = DOCUMENTED_LIMITATION
NEXT_ACTIVE_REPAIR_CAMPAIGN = P4X   (recommended; not yet opened)
LEVEL4_GLOBAL_CLOSURE     = NO
```

The P5 residual remains a documented limitation: P5X supplied new exact
structure and a validated certification stack but closed none of P5's four
universal-in-`e` gates with production evidence.  P4X, if opened, is the only
**active** repair campaign — but it is **not** the only residual limitation.
P5X's own disposition audit says so directly: *"P4X and residual P5 coexist:
P4X is not the only remaining repair campaign."*  Other residuals persist
independently, among them P8 = `FAIL`, P9 = `PARTIAL`, the P6-namespace
traceability gap, and `NOVELTY_STATUS = NOT_ESTABLISHED` throughout.

**No Level-4 global closure is claimed, and none follows from a P4X closure.**
