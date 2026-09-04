# T2 DESIGN-VALIDATION RECORD

Non-result-bearing. Records that the checkpoint validates itself; contains no
production result. Deliberately **not** in `manifests/source_manifest.json`, so
it cannot alter `CHECKPOINT_HASH`.

```text
anchor commit    310c3aa34a5d980ef48331d2d2bea36b7c37360d
CHECKPOINT_HASH  ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d
files hashed     18        protected inputs absent at anchor: none
suite            tests/test_k1_checkpoint_design.py    50 tests    OK
negative control tests/negative_control.py             12 / 12 violations CAUGHT
```

## What the 50 tests check

```text
scope        2 detectors verified against FROZEN_SCOPE.md; m = {1,2,3,5}; 8 cells;
             K2..K5 and novelty declared out of scope
budget       ledger fractions + reserve sum to 1 EXACTLY (Fraction arithmetic);
             allocated 0.190 <= w_target 0.200; B_resolvent = 0; no redistribution;
             m=1 tightening is exactly half Gate-2E; delta_max not looser than 2E;
             C evaluated at e_lo (verified: delta_max at e=0 is smaller)
assembly     every per-m coefficient table RECOMPUTED from the general formula
             (1/t - 1/m) and compared as exact Fractions, for m = 1,2,3,5
DAG          19 functions, 10 resolvent solves, union over m == the m=5 set,
             0 m-specific solves, geometry not multiplied by m, dependency order
             acyclic and resolvable, 12255 work units, shard partition exact for
             S in {1,7,16,64,128,997}
CPU          programme central reproduces the carried 3091.856205551252 exactly;
             scope factor == (19/49)/1.17; bands strictly ordered; cap ==
             ceil(1.5 x conservative); cap > worst; cap > 1.5 x central;
             cap != the programme worst 4597; no cap extension
governance   C is UPPER for both detectors and <= the certified 25000/19 cap;
             the two detector bounds are distinct objects; P1 rule != check with
             workprec 512; no precision escalation or degree adaptation;
             complexity ceiling 60000 admits both measured classes, rejects
             bidegree (20,20) and the Gate-2C defect class, and is not the
             pilot-era 100000
cover        counts and patch accounting reconciled against the Gate-2B artifact
             (322 / 3994 live / 83452 panels, and NOT live x 28)
no-run       results/, certificates/, logs/ empty; no FINAL_K1_VERDICT.json;
             AST scan proves no checkpoint module imports flint/mpmath/sympy/numpy
verdict      K1_CLOSED requires independent adjudication and cannot be
             self-awarded; K1_CLOSED does not close P5; missing artifact is a
             failure, not silence
integrity    every hashed blob re-read from the anchor commit; CHECKPOINT_HASH
             recomputed; protected trees compared repo-root-relative
inheritance  Gate-2C/2D/2E verdicts unchanged; P5 and P5X still PARTIAL
```

## Negative control — all 12 caught

```text
narrow the frozen m set                          CAUGHT
producer self-awards K1_CLOSED                   CAUGHT
K1_CLOSED auto-closes P5                         CAUGHT
adopt programme worst 4597 as the cap            CAUGHT
revert the m=1 budget tightening                 CAUGHT
corrupt an m=5 assembly coefficient              CAUGHT
allow budget redistribution                      CAUGHT
a production result exists at T2                 CAUGHT
allow precision escalation                       CAUGHT
forge the checkpoint hash                        CAUGHT
reinterpret Gate-2E as PASS                      CAUGHT
revert to the pilot-era ceiling 100000           CAUGHT
```

## Corrections made at T1, before the suite was accepted

```text
C1  protected-input list named p5y_gate2f_sr_metric_b/results/gate2f_adjudication.json;
    the authoritative artifact is results/sr_metric_b.json. Corrected, and
    freeze_manifest.py now REFUSES to freeze when any protected input is absent
    at the anchor -- a manifest naming a non-existent blob can never be satisfied.
C2  `git ls-tree HEAD <path>` is CURRENT-DIRECTORY relative. It passed only
    because ROOT coincided with the repo root; the protected-tree assertion was
    silently cwd-dependent. Both freezer and test now use --full-tree.
```
Neither correction changed a scientific rule, budget, threshold, cover, DAG or
verdict. Both re-anchored the hash and are recorded here rather than amended
away.

```text
P5Y_PRODUCTION_RUN = NO
```
