# p5y_k5_cell307_rlr_r1: cell-307 RLR formal prospective closure campaign (r1)

**Scientific closure only.** This campaign does not adopt, change floor r2, create r6, close K5 or close P5Y.

It answers one question, once: does the prospectively frozen RLR certificate close CUSUM K5 cell 307 under the
existing frozen consumer?

| read first | what |
|---|---|
| `protocol/RLR307_PROTOCOL.md` | the frozen protocol: scope, the decisions this campaign adds, Stage 1/2, the outcome table, qualification, order, STOP rules |
| `theory/THEOREM_RLR307.md` | Theorem RLR-307 and its proof |
| `audit/INCIDENT_AUDIT_RLR307.md` + `audit/INCIDENT_AUDIT_ADDENDUM_R1.md` | overnight incidents and their relevance to RLR/307 (the addendum prevails) |
| `review/INCIDENT_INDEPENDENCE_REVIEW.md` | the independent gate before the freeze: INCIDENT_AUDIT_ACCEPTED with conditions C1–C6 |
| `evidence/provenance/RLR_PROVENANCE_TIMELINE.md` | RLR timeline (commit order) |
| `evidence/start/START_STATE.json` | starting-state verification (20/20) |
| `code/` | driver (exactly-once), pinned-certifier loader, guard, Stage 1, independent reconstruction, qualification verifier, manifest writer |
| `tests/` | two-sided composition tests, independent Monte Carlo, exactly-once sandbox flows |
| `config/` | qualification cases (frozen before running) and the stricter-only latent-proxy amendment |
| `ledger/ZERO_TARGET_LEDGER_307.jsonl` | every computation of the campaign |

**Branch.** `p5y-k5-cell307-rlr-r1`, worktree `/Users/suzhe/ReBaseGuard-c307`. It is local and not pushed.
