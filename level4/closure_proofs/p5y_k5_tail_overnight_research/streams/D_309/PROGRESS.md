# Stream D (cell 309: leave the exhausted constant family) — progress log

Validation prefix `D309_`. Every script: stdlib only, `Q.install_import_guard()`, `guard_drift` at drift entry points,
`Q.log_execution` per substantive run. **New target evaluations: 0. Target-equivalent proxies: 0.**

## Done (code + validation, all target-free)

| step | artifact | result (from the JSON named) |
|---|---|---|
| core | `code/d309_core.py` | exact TC pipeline on FSM families; two independent phi^(j) paths (Leibniz / polynomial) |
| SC on FSM | `code/d309_supnorm_fsm.py` → `validation/D309_SUPNORM_FSM.json` | 60 cases; identities exact; ladder holds; **r1:** premise-level truth checks 0/300 genuine violations, mutation power reported; enclosure check demoted (weak); r0 NC1 relabelled comparator control, r0 NC2 withdrawn (arithmetic) |
| Hermite (real kernel, non-target drifts) | `code/d309_hermite.py` → `validation/D309_HERMITE_NONTARGET.json` | 1200/1200 vs C11 (FD); **r1:** H1b independent float quadrature 1200/1200; H3 per-box containment 0 violations, planted defects inside the certificate; r0 planted-too-small control withdrawn (arithmetic) |
| certificate stability | `code/d309_hermite_tf.py` → `validation/D309_HERMITE_TF_NONTARGET.json` | Taylor-form certificate 1.19–1.44x the grid lower bound; **r1:** per-box containment 0 genuine violations, 4 planted defects inside `box_upper_tf`; r0 arithmetic control withdrawn |
| RSO | `code/d309_rso.py` → `validation/D309_RSO_FSM.json` | certificates verified twice; soundness vs exact truth; **r1:** controls a1/a2 through cert_chain, c1-c3 through lr_certificate, e (profile halved); r0 NC a/c withdrawn (arithmetic); b, d genuine |
| cover | `code/d309_cover.py` → `validation/D309_COVER_FSM.json` | identities exact; all clauses sound; scaling exponents → j+1; **r1:** B2 − TPT = 0 is an implementation identity (not evidence); transport/profile/midpoint mutants on 140 records |
| SC-T | `code/d309_sct.py` → `validation/D309_SCT_FSM.json` | identity 48/48, bound 48/48; comparator control differs 48/48 (relabelled, r1) |
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

## Repair r1 (after `reviews/REVIEW_STREAM_D_R1.md`, ACCEPTED_WITH_CONDITIONS)

Re-run log (review N17). Each re-run below regenerated its JSON after a code change declared in the script's
DECLARED_RULE / docstring before the run:

| script | re-run reason |
|---|---|
| `d309_hermite.py` | review B1/N5/N7/N8: H3 per-box containment with planted defects inside `box_upper_composite`; H1b independent quadrature; `guard_drift` in the certificate entry point |
| `d309_hermite_tf.py` | the same for `box_upper_tf` |
| `d309_supnorm_fsm.py` | review B1 / test power / N4: premise-level truth checks, mutants, comparator relabel, exact-source note |
| `d309_rso.py` | review B1/N8: controls through `cert_chain`, `lr_certificate` and `rso_poly`; guards in `abs_sup_matrix`, `check_cert_*` and the LR kernel builders |
| `d309_cover.py` | review B1/B3/N12/N13: transport, profile and midpoint mutants; B2 identity relabel; DRP-1 wording |
| `d309_sct.py` | review B1: comparator relabel |

Earlier r0 re-runs of `d309_rso.py` (3×) and `d309_cover.py` (2×) were for the dual-verification requirement, the added
LR structural control and the NC fixes; none changed a declared validation set.
