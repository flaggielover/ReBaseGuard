# Level-4 Priority 9 — independent adjudication

```text
FINAL_P9_VERDICT              = PARTIAL
P9_TEMPORAL_CLASS             = RETROSPECTIVE_SYNTHESIS / TEMPORAL_INTEGRITY_PARTIAL
SCIENTIFIC_CORE               = SURVIVES_WITH_NARROWING
P8_QUARANTINE                 = PASS
P9_T2                         = CONDITIONAL_ONLY_AS_SUBMITTED
CLAIM_INFLATION               = PRESENT
PROTECTED_TREE                = PASS
NOVELTY_STATUS                = NOT_ESTABLISHED
```

P9 is a useful retrospective synthesis, but it is not closed. The exact
`rho=0` kernel and invariant law, the stationary mixture identity, the P8
quarantine, and the main reproduced P7 phenomena survive. The submitted
`P9-T2` proof nevertheless imports global monotonicity of the run-length
response as though authoritative `P7-A` proved it. It did not: P7's independent
adjudication explicitly says global monotonicity was not proved. The ledger
then repeats that promotion and its rank validator cannot detect it because it
checks self-assigned classes rather than source truth.

There are two further implementation defects. The P9 SR replay is not the
frozen no-headstart recurrence on its first update, and the theorem-relevant
A5/A6 result files have no generating program in the submitted namespace.
These defects prevent `CLOSED`, but they do not erase the surviving synthesis
or justify `FAIL` under a retrospective-audit mandate.

## 1. Repository and git state

The independent review started after refreshing `origin` at:

```text
main        5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8
origin/main 5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8
p9-research 5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8
```

The P9 worktree had no P9 commit and one untracked namespace,
`level4/closure_proofs/p9_final_synthesis/`, containing 38 non-ignored files.
There were no tracked changes. The refreshed remote was identical to local
main. The base commit is the authoritative P8 integration, whose subject is
`adjudicate Level-4 Priority 8 model-class robustness as failed`.

## 2. P9 definition and temporal status

History before `5411e2c` contains no occurrence of `Priority 9`, `PRIORITY 9`,
`priority_9`, or `priority9`. Historical whole-word `P9` occurrences are the
P5/P6 premise label for measured `m`-monotonicity, not a ninth priority.

Commit `5411e2c` first introduces an “Exact P9 handoff boundary” in P8's
independent adjudication. That section does not freeze a P9 scientific question,
protocol, gate, or deliverable. It only licenses downstream use of:

1. P8-L0/P8-L1 algebra, P8-T2 reset decomposition, and exact convention
   decomposition as exact results;
2. P8-T1 conditionally on its stated analytic hypotheses;
3. no P8-certified numerical result;
4. scoped P8 empirical and negative evidence with the stated caveats.

P9 itself declined all four surviving evidence tiers as premises.

The P9 filesystem chronology independently confirms that computations preceded
the protocol/gates: `reproduction_anchors.json` and `burnin_sensitivity.json`
predate `EXPERIMENT_PROTOCOL.md` and `CLOSURE_GATES.md`; the P9-T2 mixture result
predates `THEORY.md`. The protocol discloses that the gates are post hoc, but
the P9 README still calls all 14 gates “preregistered.” No commit or external
digest anchors a pre-result P9 mandate.

The correct classification is therefore:

```text
RETROSPECTIVE_SYNTHESIS
POST_HOC_PROTOCOL
TEMPORAL_INTEGRITY_PARTIAL
```

This is not the same defect as P8's result-driven production calibration and
reused inspected addresses. A retrospective evidence audit does not inherently
need a new prospective empirical protocol. Its post-hoc gates may be useful
checklists, but they cannot be counted as preregistered closure evidence.
Temporal status alone therefore does not force `FAIL`; it does prevent the
candidate's preregistration wording from supporting `CLOSED`.

## 3. Authoritative P1–P8 reconstruction

| priority | authoritative status | surviving downstream content |
|---|---|---|
| P1 | `CLOSED` | Frozen Gaussian CUSUM finite-window derivative theorem under its explicit analytic obligations; Lean proof spine; finite-support certificate; Gaussian values remain Monte Carlo. |
| P2 | `CLOSED` | Frozen reset symmetric two-chart SR derivative theorem; no headstart; Lean spine; Gaussian `m>1` values remain Monte Carlo. |
| P3 | `CLOSED` | First-order local boundary `rho_c=1/abs(1-Gamma)` for the two frozen detectors and `m in {1,2,3,5}`; no global, stationary, detector-universal, or non-Gaussian conclusion. Grid preregistration is unauthenticated but the boundary algebra is not fitted to the grid. |
| P4 | `PARTIAL` | P4-T1 survives conditionally under (A1)–(A7); narrowed P4-T2 gives Gaussian sufficiency and explicit non-Gaussian correction failures, not an iff theorem; Lean/Arb artifacts retain their narrow scopes. Three literal numerical gates remain false. |
| P5 | `PARTIAL` | P5-T1 raw-mean identity, P5-T7 fixed-policy invariant law/uniqueness/uniform geometric ergodicity/all positive moments, and P5-T11 stationary ACF identity survive exactly. Attraction, flip type, global uniqueness, optima, bimodality onset, and `m` trends remain conditional or finite-grid empirical. |
| P6 | `CLOSED` in the current root status table | Exact T6-A/B/C statements in scope and reproduced policy evidence survive. P6R/P6R2 repaired the statistical/label defects and P6R2b repaired Gate-9 primitive identity. The P6 namespace itself still stops at `READY_FOR_INDEPENDENT_GATE9_REVIEW`, so closure has a traceability gap. Calibration is 6/8 converged, sparse in several cells, not a verified fixed point, and not production validation. Novelty is not established. |
| P7 | `CLOSED` | P7-A finite-cycle mixture identity is exact. P7-B/C/D retain their conditions. Operational degradation, cycle-2 collapse, and the frozen-criterion negative boundary result are independently reproduced empirical results. Global monotonicity of `A` is not proved. |
| P8 | `FAIL` | Only the exact/conditional/empirical/negative tiers in P8 adjudication section 16 survive, with all caveats. The window law and sub-gates fail, literal G7 fails, detector transfer is measured absent, and G14 temporal integrity fails. No P8 certified numerical result exists. |

A `PARTIAL` or `FAIL` priority is neither wholly valid nor wholly unusable.
Downstream use is legal only at the surviving claim's adjudicated tier and
scope. P9 generally follows this rule, except for the monotonicity promotion
described below.

## 4. P8 to P9 quarantine

`P8_TO_P9_RECONCILIATION.md` correctly records `P8 = FAIL`. The machine graph
contains six P8 nodes and no edge whose source or parent is a P8 node. P9-T1,
P9-T2, P9-N1, all reproductions, and the local/operational synthesis have no P8
premise. Non-Gaussian scope cells remain unknown. Search found no hidden use of
P8-T1 as unconditional, the Gamma matrix as certified, detector or boundary
transfer, the rejected window law, a literal-G7 reinterpretation, or novelty.

P8 negative results appear only as status/history/constraints. That is allowed
by section 16 and does not create logical dependence. `P8_QUARANTINE = PASS`.

## 5. P9-T2 independent reconstruction

### Exact components

For fixed frozen detector `D`, fixed `m>=1`, and convention A, P5-T1 gives

```text
e_(j+1) = rho U_(e_j) + (1-rho) F,   F ~ N(0,1/m) independent.
```

At `rho=0` the kernel ignores its input and is exactly `N(0,1/m)`. That law is
invariant and unique directly; P5-T7 supplies the same existence/uniqueness
conclusion. P5's uniform stopping bound makes `A(e)` integrable under this law.
P7-A then gives the exact stationary identity

```text
ARL_0 = E_{e ~ N(0,1/m)}[A(e)].
```

The local multiplier is `rho(1-Gamma)`, so it is exactly zero at `rho=0`, the
minimum possible absolute multiplier on `rho in [0,1]`. “Maximally locally
stable” is defensible only in that first-order multiplier sense.

### The failed exact step

P9 next asserts `A(e)<=A(0)` from “P7-A.” Authoritative P7 says instead:

> Global strict monotonicity of `A` is not proved.

P7's theory bridge calls decrease in `abs(e)` observed on the response grid.
P9's 0/320 three-SE violations are empirical corroboration, not a proof. The
facts `A(0)>1` and `A(e)->1` do show nonconstancy, but without an exact global
upper bound they do not imply `E[A(e)]<A(0)`.

Thus the submitted exact theorem must be narrowed to:

> For the two frozen Gaussian detectors, convention A and fixed `m>=1`, the
> `rho=0` invariant law and mixture identity above are exact. Conditional on
> `A(e)<=A(0)` almost everywhere with strict inequality on a set of positive
> `N(0,1/m)` measure, the stationary ARL is strictly below `A(0)`.

The stronger operational conclusion must also be narrowed. Even if strictness
is discharged, the counterexample refutes the particular rule
`rho<rho_c => no ARL degradation relative to the known-reference A(0)` for
these frozen detectors. It does not prove that every conceivable threshold in
`rho`, every tolerance-based safety definition, every metric, detector, or
model class lacks an operational boundary.

```text
P9_T2 = CONDITIONAL_THEOREM_AS_SUBMITTED
```

## 6. Claim-ledger and dependency-graph audit

The files contain 65 claims and 64 edges (58 `premise`, five `verifies`, one
`diagnoses`), not the 66 edges stated in `THEORY.md`. The graph is acyclic and
its mechanical rank check passes, but the check trusts the ledger's own status
labels. It therefore misses semantic inflation.

Adversarial samples by class found:

| class | sample verdict |
|---|---|
| `EXACT_THEOREM` | P5-T7 is correctly scoped; P7-A is inflated by appending unproved monotonicity; P7-D0 and P9-T2 mix an exact law with an empirical/conditional strict deficit. |
| `CONDITIONAL_THEOREM` | P4-T1 and narrowed P4-T2 preserve their assumptions and partial-priority scope. |
| `FORMALLY_VERIFIED` | P4-L1 correctly describes a Lean proof spine, not the full scientific model. P3-X1 is misclassified under P9's own vocabulary: its evidence is exact Fraction arithmetic plus Arb, not a Lean-kernel result. |
| `CERTIFIED_NUMERICAL` | The SR interval is correctly restricted to the frozen m=1 symmetric two-chart SR certificate. It certifies a number, not the whole derivative bridge or campaign. |
| `EMPIRICAL_REPRODUCED` | P7-E1 is supported by production and an independent P7 seed; P9's CUSUM fresh-ARL and cycle-2 values are MC-consistent. P9's SR replay has the recurrence defect below. |
| `EMPIRICAL_ONLY` | P5 optima, bimodality, attraction, and `m` trends are properly finite-grid in their dedicated rows. |
| `NEGATIVE_RESULT` | P7's operational-crossing result and P8's failed transfer/window gates remain negative and scoped. |
| `NOT_ESTABLISHED` | P4/P5/P6/P8/P9 novelty boundaries are conservative. |
| `PARTIAL_PRIORITY_RESULT` | The project-level partial row is sound; P6-F1 uses this class for a current `CLOSED` status statement, which is internally confusing even though its limitations are explicit. |

Typed edges are necessary: formal verification, empirical reproduction,
diagnosis, provenance, and logical premise are not interchangeable. Collapsing
them would be scientifically ambiguous and could license invalid propagation.
But typing is not sufficient. The graph omits the unproved monotonicity premise
from P9-T2 and misstates it inside P7-A, so the published typed graph remains
unsound despite zero rank violations.

```text
CLAIM_INFLATION = PRESENT
PARTIAL_PREMISE_PROPAGATION = FAIL_FOR_P7_MONOTONICITY; OTHERWISE_SCOPED
```

## 7. Discrepancy rulings

### D-09

`CURRENT LEVEL-4 CAMPAIGN: CLOSED` conflicts with current mandatory ledger rows
including L4R-11 `FAIL`, L4R-06/L4R-12 `PARTIAL`, L4R-15 `FAIL`, and L4R-16
`OPEN`. This is a genuine unresolved global-governance contradiction. It is
closure-threatening for Level-4 global closure, but not theorem-threatening
and not a P9-only closure prerequisite. P9 correctly leaves it open.

### D-13

P5-T11's ACF identity is exact. The 0.0174 PCHIP prediction gap is not evidence
against that identity: a direct realized-window replay reduces the paired gap
to `-0.00045 +/- 0.00034`. The 16-chain-SE discrepancy instead demonstrates
that the gridded-map/PCHIP plug-in lacks a valid uncertainty budget. D-13 is a
scope-limiting numerical plug-in defect, not a theorem defect; it remains open
and cannot be summarized merely as “within 3.5% agreement.”

### D-15

P3's 49 files arrived in one uncommitted intake, so preregistration is
unauthenticated. This is a real provenance limitation. It does not threaten the
analytic continuous boundary formula because the grid is descriptive rather
than used to fit the boundary. It remains open as process history.

## 8. Local stability, stationarity, and operational safety

These are distinct layers:

1. Local stability is the exact first-order deterministic multiplier result.
2. Stationarity is an exact fixed-policy Markov-chain result from P5-T7, with
   exact `N(0,1/m)` at `rho=0`.
3. Operational performance is a functional of the entering-state law and is
   primarily empirical here.

The non-equivalence between layers 1 and 2 is conceptual plus theorem-backed:
local attraction does not itself prove a stochastic invariant law, while P5-T7
proves one separately. The operational non-equivalence is strongly
counterexample-supported empirically by P7. The measured ARL optimum at about
`1.25x`–`4.1x rho_c` is finite-grid empirical evidence only, not a universal
law. The strongest defensible operational statement is P7's: under its frozen
criterion and two Gaussian detector/window families, `rho_c` is not an
operational safety boundary and `rho<rho_c` is not validated as a safety rule.

## 9. P6 safe-rebaselining language

The proposed language is acceptable with strict separation:

- current campaign status: `CLOSED`, per the latest root table;
- exact theory: only T6-A/B/C at their stated policy/kernel/one-step scopes;
- empirical effectiveness: confirmed and replicated in tested simulation and
  semi-real regimes;
- calibration: limited (6/8 convergence, sparse/fallback `s1`, final refit not
  a verified fixed point);
- novelty: `NOT_ESTABLISHED`;
- production validation and general transferability: not established.

`CLOSED` does not imply calibration quality, novelty, production readiness, or
transfer to detector-state-reading/adaptive kernels. The missing independent
Gate-9 review inside the P6 namespace is a traceability gap that should remain
visible.

## 10. Formal, certified, empirical, and novelty firewall

The main Lean project rebuilt successfully: 8,717 jobs, warnings only. Source
search found no `sorry`, `admit`, unsafe scientific shortcut, or project
scientific axiom in the sampled P1/P4/P5 files. The strongest formal statement
carried by P9 is the P4/P1 proof spine: kernel-checked declarations under the
standard `propext`, `Classical.choice`, and `Quot.sound` axioms, while concrete
stopped-model hypotheses remain human obligations.

The strongest certified numerical result is the frozen m=1 symmetric
two-chart SR interval

```text
Gamma_SR in [5.800391799508442, 28.781285803081492].
```

Twenty-eight focused independent certificate/auditor tests passed. The
certificate does not certify P9-T2, arbitrary windows, other detectors, or the
campaign. The broader post-Level-4 archive wrapper fails on the known changed
root `README.md` hash, so it is not a clean current-tree archive check.

The strongest reproduced empirical result remains P7's operational finding:
fresh ARL about `79.91–162.03`, full-reuse ARL about `48.36–80.05`, and cycle-2
collapse about `5.6–9.4`. P9's independent CUSUM values are consistent with
this; SR-specific P9 values must be discounted because of the recurrence
mismatch.

P9 ran no new literature search. A prior finite search found no `DIRECT` match,
which is not proof of novelty. `NOVELTY_STATUS = NOT_ESTABLISHED`.

## 11. Reproduction implementation audit

CUSUM stopping, window inclusion, raw-mean update, per-path cycle averaging,
and `MAX_STEPS` handling match the frozen convention for the exercised cells.
At `rho=0` burn-in is irrelevant because each entering reference is iid after
the first update; at `rho=1` finite-horizon means are burn-in-sensitive and P9
correctly reports this qualitatively. A4 computes uncertainty across paths,
not pooled dependent cycles.

The SR implementation is not algebraically identical to the frozen recurrence.
The frozen state stores `Y=log(1+R)`, starts at `Y_0=0`, computes
`ell=Y+z-1/2`, tests `ell>=log(A)`, then stores `logaddexp(0,ell)`. P9 instead
starts at zero and computes `logaddexp(0,state)+z-1/2`, so the first step is
shifted upward by `log(2)`. At `z=6.5`, for example, P9 alarms on step one while
the frozen recurrence does not. This recurs after every cycle reset.

Moreover, `burnin_sensitivity.json` and `p9t2_mixture_check.json` are not emitted
by either supplied experiment program and are not checked by the focused suite.
The A6 quadrature error is also unquantified. Consequently P9's A5/A6 cannot be
treated as independently reproducible artifacts.

## 12. Tests and independent reviewer checks

Candidate focused suite, rerun with worktree write access:

```text
37 passed
```

These tests validate schemas, candidate classifications, generator byte
consistency, A1–A3 algebra, quarantine, and protected scope. They do not validate
the scientific truth of the assigned evidence classes and do not test A4–A6.

Independent checks added in `tests/test_independent_adjudication.py` cover:

1. the source-level P7 monotonicity contradiction;
2. P9-T2's resulting exact-class inflation;
3. the frozen-vs-P9 SR first-step mismatch;
4. absence of A5/A6 generators;
5. literal P8 edge quarantine;
6. the 64-vs-66 edge-count discrepancy;
7. the authoritative `PARTIAL` verdict record.

## 13. Protected tree and regression

The pre-P9 manifest contains 2,217 files anchored at `ffe23a6`. Independent
focused checks confirm that the only protected-file deviation before P9
integration is the root README change made by authoritative commit `5411e2c`.
P9 itself altered no P1–P8 artifact. Integration adds the P9 namespace, this
adjudication, reviewer checks, and the root P9 status row only.

The final repository-wide regression result is recorded in the integration
handoff. Historical protected-manifest/archive failures must be compared with
the authoritative baseline and not misattributed to P9.

## 14. Limitations after P9 and future P8R

After P9, the following remain open: a proof (or honest conditional status) for
global `A(e)` monotonicity; corrected no-headstart SR reproductions; generators
and quantified numerical error for A5/A6; D-09, D-13, and D-15; P4/P5 literal
failed gates; P6 calibration/traceability limitations; P8 repair; novelty;
non-Gaussian/detector/window transfer; and global Level-4 closure.

A future P8R cannot change the correctness of P9's P1–P7-only exact kernel and
mixture identities. It can change the later model-class/global synthesis by
adding independently valid robustness evidence. P8R is not required for P9's
retrospective synthesis, but it also cannot repair P9-T2's missing monotonicity
premise or the P9 SR implementation.

## 15. Final verdict and next action

`PARTIAL` is required. The scientific core survives, but closure requires a
separate P9R namespace that is temporally anchored before new results and that:

1. either proves global monotonicity/strict ARL loss for the frozen detectors or
   labels P9-T2 conditional and narrows the operational corollary;
2. repairs and independently tests the SR recurrence;
3. supplies deterministic generators for A5/A6 with numerical-error accounting;
4. rebuilds the ledger from authoritative source statements rather than
   self-assigned ranks.

Global Level-4 closure must remain a later, separate audit after P9R and any
chosen P8R; P9 `PARTIAL` does not repair P4, P5, P8, or the global requirement
ledger.

```text
FINAL_P9_VERDICT = PARTIAL
P9_TEMPORAL_CLASS = RETROSPECTIVE_SYNTHESIS / TEMPORAL_INTEGRITY_PARTIAL
P9_T2 = CONDITIONAL_THEOREM_AS_SUBMITTED
P8_QUARANTINE = PASS
P8R_REQUIRED_FOR_P9 = NO
CLAIM_INFLATION = PRESENT
PARTIAL_PREMISE_PROPAGATION = FAIL_FOR_P7_MONOTONICITY; OTHERWISE_SCOPED
PROTECTED_TREE = PASS
NOVELTY_STATUS = NOT_ESTABLISHED
SCIENTIFIC_CORE = SURVIVES_WITH_NARROWING
LEVEL4_GLOBAL_CLOSURE = NO
AUTHORITATIVE_STATUS_RECOMMENDATION = P9_PARTIAL
```
