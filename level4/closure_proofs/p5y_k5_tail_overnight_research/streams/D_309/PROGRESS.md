# Stream D (cell 309: leave the exhausted constant family) — progress log

Validation prefix `D309_`. Every script: stdlib only, `Q.install_import_guard()`, `guard_drift` at drift entry points,
`Q.log_execution` per substantive run. **New target evaluations: 0. Target-equivalent proxies: 0.**

## Done (code + validation, all target-free)

| step | artifact | result (from the JSON named) |
|---|---|---|
| core | `code/d309_core.py` | exact TC pipeline on FSM families; two independent phi^(j) paths (Leibniz / polynomial) |
| SC on FSM | `code/d309_supnorm_fsm.py` → `validation/D309_SUPNORM_FSM.json` | 60 cases; identities exact; ladder holds; 0/9900 enclosure violations; NC1 60/60, NC2 60/60; adversarial equality case reached |
| Hermite (real kernel, non-target drifts) | `code/d309_hermite.py` → `validation/D309_HERMITE_NONTARGET.json` | 1200/1200 closed-form checks vs independent C11 K_e; sign NC 592/592; kink NC 936/960; naive box certificate sound but vacuous for a degree-9 test function |
| certificate stability | `code/d309_hermite_tf.py` → `validation/D309_HERMITE_TF_NONTARGET.json` | Taylor-form certificate sound 6/6, 1.19–1.44x the grid lower bound |
| RSO | `code/d309_rso.py` → `validation/D309_RSO_FSM.json` | certificates verified twice; soundness vs exact truth; NC a/b/c/d detected; 0/2376 enclosure violations; LR cert >= exact lower bound 12/12 |
| cover | `code/d309_cover.py` → `validation/D309_COVER_FSM.json` | identities exact; all clauses sound; B2 − TPT = 0 exactly (30/30); scaling exponents → j+1 |
| SC-T | `code/d309_sct.py` → `validation/D309_SCT_FSM.json` | identity 48/48, bound 48/48, NC 48/48 |
| scan | `code/ov_quarantine.py --scan` (re-run at end) | 0 findings in the seven D_309 files (1 finding elsewhere: `streams/A_306/a306_reproduce_A.py`, not touched) |

## Rule S8 (received mid-task)

Received after all code/validation had run and **before any document was written**. No file in this directory places a
route factor next to a committed tail-cell share, factor or margin. The documents below keep committed tail history in
separate "History (quoted, no route factor)" sections; route sections contain only structural statements and
synthetic / non-target ratios.

## Documents (filled section by section)

- [x] SCOPED_NEGATIVE_FAMILIES_309.md (history §1 quoted with file:line; §2 structural differences, no numbers)
- [x] SUPNORM_THEOREM.md (SC-3, SC-4w, TC+, SC-T, SC-S1; certificate; stability; data check)
- [x] COVER_REFINEMENT_309.md (CR-1..CR-3, B2 dominated by TPT, DRP-0/1, cost model)
- [x] RESIDUAL_SPECIFIC_309.md (RSO-0 + occupation characterization + collapse lemma; RSO-PM; RSO-LR order 1; RSO-P)
- [x] D_309_ROUTE_SUMMARY.md (route rows + gates; 309 deliverable; structural ranking; FREEZE_READY no)

## Final state

All five deliverables written. Tail-number grep over the four route documents: no committed tail share/factor/margin present (S8).
