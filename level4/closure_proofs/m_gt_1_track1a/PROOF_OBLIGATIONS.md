# Proof and evidence obligations

| ID | Obligation | Status | Evidence |
|---|---|---|---|
| T1A-1 | prior theorem artifacts reproduce | PASS | `AUDIT.md`; prior 46/46 tests and expected partial decision |
| T1A-2 | historical hashes remain frozen | PASS | `AUDIT.md`; integrity tests |
| T1A-3 | protocol frozen before new data | PASS | SHA-256 `76a5d40b…`; commit `13e4975…` |
| T1A-4 | Stage-A min-dwell and Stage-D truncation semantics | NUMERICALLY-CHECKED | simulator tests and retained path controls |
| T1A-5 | independent Stage-A/Stage-D distinction | PASS | preselected `m=20,50` rule in `REPLICATION_REPORT.md` |
| T1A-6 | correction nonnegative | HUMAN-PROVED / NUMERICALLY-CHECKED | `THEOREM.md`; every path nonnegative |
| T1A-7 | direct decomposition algebra | HUMAN-PROVED / NUMERICALLY-CHECKED | exact pathwise identity |
| T1A-8 | independent decomposition correspondence | FAILED | pooled `m=20` abs z `3.130 > 3` |
| T1A-9 | `m=1` reduction | PASS | exact shared-stream equality; independent agreement |
| T1A-10 | exact rho scaling | PASS | human algebra; zero sample-transformation error |
| T1A-11 | Lean proof spine | NOT STARTED | mandatory stop after T1A-8 |
| T1A-12 | axiom audit | NOT RUN | no Track 1A Lean declaration or axiom exists |
| T1A-13 | Arb certificate | NOT REQUIRED | no new rigorous scalar inequality claimed |
| T1A-14 | final repository verification | PASS | Track 1A 32/32; prior track 46/46; authoritative 695/695 |

The failed independent decomposition gate controls the campaign even though
the human and pathwise algebra passed. It cannot be replaced post hoc by the
same-sample identity.
