# Adversarial audit

The first run is preserved at **23/25 FAIL**.
Its expected A24/A25 failures precede creation of the full-verifier and
byte-reproduction records. Final result: **25/25 PASS**.

| ID | Check | First | Final | Evidence |
|---|---|---|---|---|
| A1 | Stage E unchanged | PASS | PASS | historical Stage E remains PARTIAL with 0/3 H-E5 |
| A2 | V2 unchanged | PASS | PASS | protected V2 decision remains PARTIAL with one supporting task |
| A3 | V2 partial result preserved | PASS | PASS | V2 Household remains its sole H2-4 success |
| A4 | no V2 statistics pooled into V3 inference | PASS | PASS | V3 confirmatory records contain only task-level streams; aggregation counts decisions |
| A5 | selection outcome-blind | PASS | PASS | selection/protocol 97565574 precedes outcomes ['5a43ee99', '5a43ee99'] |
| A6 | power floor frozen | PASS | PASS | 40-effective-block floor is in the hashed protocol |
| A7 | no failed task replacement | PASS | PASS | both frozen primaries retained; no backup exists |
| A8 | rho outcome-blind | PASS | PASS | rho fixed at execution checkpoint 07e2fb71 |
| A9 | interventions frozen | PASS | PASS | five confirmatory conditions exactly match the frozen family |
| A10 | H3 definitions unchanged | PASS | PASS | effect, multiplicity, and safety thresholds match the freeze |
| A11 | matched streams | PASS | PASS | each task uses one residual stream and one event grid across policies |
| A12 | no future leakage | PASS | PASS | chronological splits and train/calibration ownership guards pass |
| A13 | dependence-aware block inference | PASS | PASS | paired task-level moving blocks are used; no iid endpoint inference |
| A14 | simultaneous non-inferiority | PASS | PASS | all five conditions pass the frozen simultaneous one-sided 99% bound |
| A15 | effective-block floor enforced | PASS | PASS | every calibration, natural, and event endpoint meets floor 40 |
| A16 | no direction-only support | PASS | PASS | H3-1 and H3-2 Route A meet magnitude and lower-bound rules |
| A17 | contradictions not hidden | PASS | PASS | no strong P2 contradiction exists; all condition bounds remain visible |
| A18 | P3 exploratory only | PASS | PASS | P3 is absent from every confirmatory policy set |
| A19 | no production-validation wording | PASS | PASS | strong claims appear only in an explicit does-not-establish boundary |
| A20 | aggregation frozen before outcomes | PASS | PASS | counting rule frozen at 97565574 before confirmatory outcomes |
| A21 | figures use summary only | PASS | PASS | five figures are generated exclusively from results/summary.json |
| A22 | protocol, execution, dataset, and history hashes pass | PASS | PASS | all frozen digests and protected historical trees verify |
| A23 | focused tests pass | PASS | PASS | focused tests=75/75 returncode=0 |
| A24 | full repository verifier passes | FAIL | PASS | status=PASS checks=1103 |
| A25 | generated science bytes reproduce | FAIL | PASS | status=PASS byte_stable=True |

No scientific threshold, route, task, result, or aggregation rule is weakened
between the two runs.
