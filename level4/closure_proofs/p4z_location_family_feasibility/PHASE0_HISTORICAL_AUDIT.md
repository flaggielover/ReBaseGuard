# P4Z Phase 0 — historical and frozen audit of the P4 line

Read-only reconstruction from repository artifacts.  Where a machine-readable
config exists it is the source; prose is used only where no config exists.

```text
P4_ORIGINAL_VERDICT      = PARTIAL          immutable, unchanged by P4Z
P4X_SUCCESSOR_VERDICT    = PARTIAL          as recorded on p4x-feasibility-audit
P4Y_OUTCOME              = DO_NOT_FREEZE_P4Y (four pilots, no binding checkpoint)
LEVEL4_GLOBAL_CLOSURE    = NO
P4Z_TOUCHES_NONE_OF_THESE
```

## 1. Where the lineage lives

| campaign | branch | worktree | namespace | tip |
|---|---|---|---|---|
| P4 | `p5y-gate1-micropilots` (and `main`) | `/Users/suzhe/ReBaseGuard` | `level4/closure_proofs/p4_theory_generalization` | tree `eede9038` |
| P4X | `p4x-feasibility-audit` | `/Users/suzhe/ReBaseGuard-p4x` | `level4/closure_proofs/p4x_generalization_boundary` | `19b0064` |
| P4Y pilot 1 | `p4y-prefreeze-pilot` | `-p4y` | `p4y_precision_governance_pilot` | `cefc03d` |
| P4Y pilot 2 | `p4y-pilot2-final` | `-p4y2` | `p4y_pilot2_final_prefreeze` | `7797368` |
| P4Y pilot 3 | `p4y-pilot3-heavy-stage1` | `-p4y3` | `p4y_pilot3_heavy_stage1` | `9656b69` |
| P4Y pilot 4 | `p4y-pilot4-measurement` | `-p4y4` | `p4y_pilot4_measurement` | `de9c9da` |

**A discrepancy in the historical record, recorded and not resolved by P4Z.**
`p4x-feasibility-audit` records `P4X_SUCCESSOR_VERDICT = PARTIAL`
(`production/PRODUCTION_RESULT.md` §10).  Every P4Y branch records
`P4X_SUCCESSOR_VERDICT = FAIL`, qualified as "governance and sampling
integrity, not a scientific contradiction", together with
`P4X_SCIENTIFIC_FAILURES = NONE`.  Both readings agree on the substance —
88/96 binding PASS, 0 scientific FAIL, 8 cells not adjudicable — and differ
only on the label.  P4Z adopts neither label, cites both, and depends on
neither: its scope is fixed by the *8 unadjudicated cells*, which both readings
record identically.

## 2. The frozen theorem target

| item | value | source |
|---|---|---|
| theorem | G1a `Gamma_{D,m,f} = E_0[A_m S_tau^psi]`; G1b `F'_{rho,m}(0) = rho(1 - Gamma)` | `THEOREM.md` §3 |
| estimand | `Gamma_{D,m,f}`, one scalar per `(layer, detector, family, m)` | `THEOREM.md` §3 |
| detectors | frozen two-sided CUSUM `k=1/2`, frozen two-chart SR; no others | `detectors.py`, `THEOREM.md` §10 |
| parameter domain | `e = 0` for G1; `e0 ∈ (-d0, d0)` for G1' | `THEOREM.md` §§3–4 |
| window | `w = min(m, tau)`, random denominator, alarm-causing increment included | `P4_PROTOCOL.json` |
| residual convention | `Z_t = eps_t - e`, `f_e(z) = f(z+e)`, `psi = -f'/f`, `s = -psi` | `P4_PROTOCOL.json` |
| `m` grid | `1, 2, 3, 5` | `P4_PROTOCOL.json` |
| layers | reduced (`cusum@2`, `sr@20`, `max_steps` 60 000); frozen (`cusum@5`, `sr@520.886133602749`, `max_steps` 200 000) | `P4_PROTOCOL.json` |
| families | THEOREM-SUPPORTED gaussian, laplace, logistic, t3, t1p5, skewnormal4; OUTSIDE-ASSUMPTIONS uniform, cauchy | `P4_PROTOCOL.json` |
| correspondence gate | relative discrepancy `<= 0.03` **and** `\|z\| <= 4` | `P4_PROTOCOL.json` `gates` |
| Route-Q tolerance | `1e-6` relative, 24 rows, cross-check only | `P4_PROTOCOL.json` |
| neutrality tolerance | `\|z\| <= 4` on 72 deterministic-stopping rows | `P4_PROTOCOL.json` |
| FD convention | central difference at `h ∈ {0.05, 0.025}`, per-batch Richardson `(4 D(h/2) - D(h))/3` | `P4_PROTOCOL.json` |
| variance rule | *batch* standard error: one mean per batch, SE = spread of batch means | `estimators.py` docstring |
| frozen precision | Monte Carlo throughout; Arb at 160 bits for the three certificate objects only | `certificates/certificate.json` |
| master seeds | 4010001–4010006 | `P4_PROTOCOL.json` |
| stopping rule | fixed batch and path counts per layer; no adaptive rule in P4 itself | `P4_PROTOCOL.json` `layers` |

## 3. Which P4 claims are theorem level and which are certified correspondences

**Theorem level** (proved, not measured): G1, G1', G2, G3's identity (G3a), G4,
the discharge lemmas L1–L5, and the two failure modes F1 (moving support:
identity false, exact defect 2) and F2 (no first moment: the estimand does not
exist).  `EVIDENCE_BOUNDARY.md` and the Lean bridge cover these.

**Interval certified** (Arb, 160 bits, re-verified at 256 by P4X): exactly
three objects — the closed-form unbounded-horizon Laplace instance, the exactly
rational moving-support counterexample, and the finite-support general-score
witness.

**Monte Carlo only**: *every* frozen CUSUM and SR gain, Gaussian or not.  P4's
own `evidence_boundary` says so in as many words.  This is the load-bearing
fact for P4Z: the unresolved gates are all Monte Carlo gates.

**Binding vs exploratory.**  Binding: `configs/P4_PROTOCOL.json`,
`manifest.json`, `certificates/`, `results/closure_decision.json`, and P4X's
`checkpoint_a/results/checkpoint_a.json` plus
`production/results/production_results.json`.  Exploratory and explicitly
non-binding: every P4Y pilot artifact (all four pilots record
`P4Y_BINDING_CHECKPOINT_CREATED = NO`), and P4X's
`r0_variance_reduction_pilot`.

## 4. P4's own gate ledger — what failed

From `results/closure_decision.json`, `all_required_gates_pass = false`:

| gate | result | reason |
|---|---|---|
| `all_theorem_supported_cells_pass` | **false** | 9 t1p5 cells over the 3 % relative limit with `\|z\| <= 1.5` (precision limited); 1 skewnormal4 cell at `z = 4.2946` |
| `all_outside_assumption_cells_demonstrate_failure` | **false** | 16 Cauchy cells show non-convergence, not the deterministic defect the gate was written to detect |
| `gaussian_consistency_with_closed_core` | **false** | worst `z = 12.91` under a statistic that divides by P4's SE alone and treats the closed Monte Carlo value as exact |
| all other 11 gates | true | |

Worst theorem-supported relative discrepancy `0.2564` (frozen `sr@520.886`,
`t1p5`, `m=1`), against a Route-B relative SE of `0.2333` on the same cell —
i.e. the cell was noise, not disagreement.

## 5. P4X — what it closed and what it did not

`production/results/production_results.json`:

| obligation | status |
|---|---|
| C1 inherit the theorem unchanged | PASS |
| C2 attainable-precision correspondence | **INCOMPLETE** |
| C3 Route Q as cross-check only | PASS |
| C4 failure-mode evidence matched to the proved mode | PASS |
| C5 Gaussian consistency by a two-sample statistic | PASS |
| C6 re-verify inherited Lean and Arb | PASS |
| C7 protected-tree integrity | PASS |

P4X therefore resolved two of P4's three failed gates outright:

* the Cauchy gate, by replacing a Monte Carlo disagreement signature with the
  analytic non-existence argument (`X7b`, new compute NONE);
* the Gaussian-consistency gate, by introducing the correct two-sample
  statistic `z_combined = |e1-e2| / sqrt(SE1^2 + SE2^2)`, worst value `2.977`
  against a limit of `4.0`.  This is a *new preregistered object*; P4's own
  gate stays failed and untouched.

C2 is what remains.  88/96 cells PASS the unchanged `0.03` / `|z| <= 4` gate,
**0 cells FAIL**, and 8 are `PRECONDITION_NOT_MET`.

## 6. The 8 unadjudicated cells — the exact residue P4Z targets

Checkpoint A §8 forced a precision precondition `r* = 0.010823`, derived from
the unchanged 3 % criterion by `1.96 * sqrt(2) * r* = 0.03`.  A cell is only
adjudicable once **each** route reaches `r*`, or is declared
`PRECISION_LIMITED` from projected cost alone.  These 8 cells took their one
permitted top-up, still missed `r*` on one route, and hit no cap — so neither
branch applied.

| # | layer | detector | family | m | route A relSE | A paths | route B relSE | B paths | which route missed | rel | `z` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | reduced | sr@20 | t1p5 | 1 | 0.00748 | 16 250 000 | **0.01721** | 314 500 000 | B | 0.0210 | 1.14 |
| 2 | reduced | sr@20 | t1p5 | 2 | 0.00522 | 16 250 000 | **0.01190** | 314 500 000 | B | 0.0146 | 1.14 |
| 3 | frozen | cusum@5 | t3 | 1 | **0.01101** | 4 080 000 | 0.00864 | 960 000 | A | 0.0007 | 0.05 |
| 4 | frozen | cusum@5 | t1p5 | 1 | **0.01658** | 93 500 000 | 0.00618 | 2 255 250 000 | A | 0.0004 | 0.02 |
| 5 | frozen | cusum@5 | t1p5 | 2 | **0.01153** | 93 500 000 | 0.00429 | 2 255 250 000 | A | 0.0003 | 0.03 |
| 6 | frozen | sr@520.886 | t1p5 | 1 | **0.01502** | 23 250 000 | 0.01078 | 446 000 000 | A | 0.0237 | 1.29 |
| 7 | frozen | sr@520.886 | t1p5 | 2 | **0.01086** | 23 250 000 | 0.00774 | 446 000 000 | A | 0.0173 | 1.31 |
| 8 | frozen | sr@520.886 | t1p5 | 5 | **0.01108** | 23 250 000 | 0.00460 | 446 000 000 | A | 0.0168 | 1.40 |

Four configurations are involved: `frozen/cusum@5/t1p5`, `frozen/cusum@5/t3`,
`frozen/sr@520.886/t1p5`, `reduced/sr@20/t1p5`.  Every one of the 8 satisfies
the 3 % criterion *informationally*; none may be counted as a pass, and P4Z
does not count them.

## 7. Was any historical path count or stopping rule beyond authorization?

No.  Checked against Checkpoint A §13 (`TOTAL_CPU_CAP = 60 h`,
`PER_CONFIGURATION_CPU_CAP = 40 h`): P4X spent **24.7493 CPU-h** total and
**18.5994 CPU-h** on its worst configuration.  The largest single allocation,
`frozen/cusum@5/t1p5` Route B at 2 255 250 000 paths across 5 shards, is
sized by the frozen `N_req` rule and stays inside both caps.  The sharding was
recorded as a scheduling choice with the total N, block size, estimator,
precision rule and gate unchanged, and P4Y's shard-sum regression
(`partition(8801, 5) = [1761, 1760, 1760, 1760, 1760]`, 8 801 blocks,
2 200 250 000 paths) confirms the arithmetic and pins the earlier defective
8 805-block implementation.

One authorization *defect* — distinct from an overrun — is real and is
recorded in Phase 1: the "at most one top-up" rule combined with an
achieved-relSE precondition admits a state in which no branch of the gate
applies.  That is a stopping-rule defect, not a budget breach.

## 8. P4Y — four pilots, no checkpoint

| pilot | verdict | what it established |
|---|---|---|
| 1 | `NEEDS_ONE_MORE_PRE-FREEZE_PILOT` | `N_req` targets an **expectation**, so the realised relSE lands on a distribution centred near `r*` and attains it with probability ≈ 0.55, not ≈ 0.95.  One top-up lifts that to roughly 0.75 and can never reach 0.95. |
| 2 | `NEEDS_ONE_MORE_PRE_FREEZE_PILOT` | governance endpoint holds; heavy-tail stage-1 sizing does not |
| 3 | **STOPPED** | the pilot's own benchmark was not a truth: one block in 8 000 carried 29.3 % of the total squared deviation; its `1/sqrt(2(n-1))` normal-theory uncertainty was meaningless |
| 4 | `DO_NOT_FREEZE_P4Y` | executed in full to a negative result: **no block size in the frozen grid yields an admissible benchmark** for the heavy strata.  Best heavy lower bound on reference accuracy `0.2293` against a target `0.90`; the finite-variance control reached `0.9019` at the same block size. |

Pilot-4's decisive observation is that *agreement* diagnostics (two-pool split,
growing prefix) declared the heavy strata stable to within 2–4 % while a single
block carried 21–25 % of the squared deviation.  Cost never bound: every grid
point was affordable, from 0.21 to 6.83 CPU-h against a 10 h allowance.  The
measurement bound.

## 9. What this audit fixes for P4Z

1. The unresolved scientific residue is **8 cells in 4 configurations**, all
   `t1p5` except one `t3`, all on the *frozen-precision precondition* rather
   than on a scientific disagreement.  0 cells ever failed the 3 % gate.
2. The binding obstacle is not cost.  P4X spent 25 of 60 authorised CPU-hours;
   P4Y-4 found every measurement grid point affordable.
3. The binding obstacle is that the *standard error itself* is not a
   trustworthy statistic for the historical estimator on a family with
   `E[eps^2] = infinity`.
4. Therefore a successor must change the **estimator**, not the allocation
   rule.  P4X and P4Y between them exhausted the allocation-rule design space.
