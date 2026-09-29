# Independent route review R2 of SRK (cell-309 research campaign r1)
ROUTE_REVIEW: PENDING_EVIDENCE

**Status.** Phase A in progress (items 1, 2, 4, 5, 6, 7). Items 3 and 8 and the verdict follow in Phase B.

## 0. Reviewer execution declaration (written before any of these runs)

Written 2026-09-29 ~16:20Z at HEAD `a748ac49`, while the coordinator's rerun (`srk_decoy_suite.py 2 whole`,
`2 cell`) is running. I do not start, stop or touch those processes, and I do not run `srk_decoy_suite.py`.

Every run below uses `PYTHONDONTWRITEBYTECODE=1`, calls only `run()` (never a `__main__` that writes evidence), and
redirects `q309_guard.EXEC_LEDGER` to `scratchpad/r2/reviewer_exec_ledger.jsonl`. Nothing is written in the repository
except this file.

| id | what | kernel / geometry / drift | certifier? |
|---|---|---|---|
| RD2-0 | static quarantine scan (`q309_guard.scan()`, read-only) | none | no |
| RD2-1 | `cell_blocks` arithmetic probe on non-dyadic, dyadic, negative and degenerate cell endpoints, against my own re-implementation (no kernel evaluated; no endpoint in [6/5, 13/5] or its mirror) | none | no |
| RD2-2 | `srk_gate.gate` / `combine` / adapter-binding probes on constructed certificate objects (no kernel), with refusal reasons printed | none | no |
| RD2-T | NS tests via `run()`: test_q309_guard, test_srk_gate, test_srk_adapter, test_srk_assembly_twosided, test_srk_envelope (real geometry envelope only, E = [1/4, 9/32]), test_srk_fsm_truth (synthetic FSM), test_srk_wrec_refusal and test_srk_cert_mutants (both: synthetic h = 3, k = 1/2, E = [1/4, 9/32], degree 8, whole and taboo kernel; the latter also runs the independent verifier) | h = 3 synthetic; real geometry only inside the envelope test at e ≤ 9/32 | yes (h = 3 only) |
| RD2-3 | T1 power probe. Synthetic h = 3, k = 1/2, E = [1/4, 9/32], degree 8, index 1, whole kernel: (a) genuine and `quarter_weight` weight certificates from the same W, reporting r_min and λ of both; (b) a *consistent* quarter-weight mutant (float proposal RHS also κ̄₁/4, exact check against κ̄₁/4, certificate claims κ̄₁), judged by `verify/srk_verify_indep.verify_cert` with the test's settings (N = 8, max_depth = 24). Expected: (b) REJECT with an explicit refutation | h = 3 synthetic only | yes (h = 3 only) |

No run touches the real kernel at a drift above 9/32, any cell 305–309, or any drift in [6/5, 13/5] or its mirror.

(Findings follow below as they are established.)
