# Authorization review — brief (theorem-TC successor: new real scientific addresses)

You are a fresh-context reviewer deciding whether the frozen, qualified theorem-TC producer may evaluate its
pre-registered real addresses. You did not write it. Verdicts: AUTHORIZED or NOT_AUTHORIZED (with reasons). This is the
section-5 step E of the campaign rules: before ANY new real scientific address is evaluated, (A) deterministic reuse
must be shown insufficient, (B) addresses/producer/runtime/dependencies/fields/outputs/acceptance/budget/stopping rule
pre-registered, (C) producer/protocol frozen, (D) independently qualified, (E) fresh-context authorization, (F) guard
switched from DENY only for those exact addresses.

Namespace: `level4/closure_proofs/p5y_k5_lower_front_order3/` on branch `p5y-postk1-frontier` (read it in the worktree
/Users/suzhe/ReBaseGuard-k5lf; the relevant commits are named in `evidence/tc_r1/`).

Check:
1. (A) `phase_b/ROUTE_COMPARISON.md`, `evidence/forecast_r1/ROUTE_FORECAST.json`, gates `config/FEASIBILITY_GATES_A.json`
   (frozen at e89b33f2 before any forecast): is the case that zero-new-real routes are insufficient sound?
2. (B)(C) `config/TC_PROTOCOL.json` (committed in the freeze commit): exact addresses (cells 11–44, midpoint only),
   producer, runtime, pins, fields, expected outputs, acceptance, budget (forecast 16.3 CPU-h, cap 24, campaign hard cap
   40), stopping rule, seal rule. Does the freeze commit contain exactly the protocol, code and the pre-freeze refusal?
3. (D) `evidence/tc_r1/QUALIFICATION_RESULT.json` (and the qualification evidence files): QUALIFIED true, S00 head equal
   to the freeze commit, every gate passed as the frozen gate definitions in `code/tc_qualify.py` require.
4. Reviews: `review/REVIEW_R1.md` (NOT_READY), `review/REVIEW_R1_DISPOSITION.md`, `review/REVIEW_R2.md` (+ disposition if
   any). Was every load-bearing finding resolved before the freeze?
5. The parallel channel: the TC producer calls the frozen order-3 producer's `Order3Certifier` directly, while that
   producer's own real-cell registry stays empty. Decide explicitly whether this protocol's authorization is an
   acceptable governing gate for these 34 addresses (the order-3 producer is frozen and its manifest is verified at run
   time; the published order-3 information is limited to the certified δ_mid(G_r), the certified candidate supremum
   sup.G and the certified upper bound |Ĝ_r(a)|; no uncertified order-3 candidate value is recorded).
6. Temporal integrity: no real TC value exists before your decision (the dev replays computed only adopted K1 values and
   a synthetic-G code path; check `evidence/dev/` and the commit history for anything else).

If AUTHORIZED, write `evidence/tc_r1/AUTHORIZATION_REVIEW.md` (your reasoning and verdict line
`AUTHORIZATION_VERDICT = AUTHORIZED`), and nothing else. If not, write the same file with NOT_AUTHORIZED and the reasons.
Do not modify any other file, do not commit, do not run anything remote, do not run any CUSUM computation.
