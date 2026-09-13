# PS1 / K1 status correction (additive record, 2026-09-13)

This record supersedes stale statements. It does not rewrite them: `docs/research_synthesis/PS1_CURRENT_STATUS.md`
and the root `README.md` are left byte-unchanged on this branch.

## Superseded statements

| source | stale statement | corrected status |
|---|---|---|
| `docs/research_synthesis/PS1_CURRENT_STATUS.md` | "genuine production has not started: cells = 0"; "Full 369-cell production is NOT RUN" | Genuine PS1 SR production **started**. Generation 1 (run `20260912T041203Z-962132d3`) halted on RETRY_LIMIT with 0 finalized cells and 92.32 CPU-h, after a host/systemd maintenance event. Generation 2 has run since 2026-09-12T15:46:58Z (unit `rbg-p5y-k1-ps1-recov-aws-20260912T154658Z-2011fded`), under an operator compatibility DRAIN since 16:04:18Z. Read-only observation at 2026-09-13T04:26Z: 0 finalized, 64 open cell reservations. The campaign is not complete. |
| root `README.md` §status | "genuine PS1 production remains NOT STARTED (0 cells)" | as above |
| the post-K1 brief | "K1 has CUSUM machinery but SR remains unfinished / unqualified" | **The live 369-cell PS1 campaign is the SR side of K1 and is already qualified and authorized on AWS** (`PS1_PRODUCTION_AUTHORIZATION_CLOSED`, authorization `29b3bffb`). SR is unfinished only in the sense that production is still in progress. **The unfinished CUSUM side requires its current-producer full rerun**: Aux4 has 2/326 cells certified and `CUSUM_COVER_INHERITANCE = REQUIRES_FULL_326_RERUN`. |

## Unchanged

`K1 = NOT CLOSED`; `P5Y = NOT CLOSED`; `LEVEL4_GLOBAL_CLOSURE = NO`; `NOVELTY_STATUS = NOT_ESTABLISHED`.
No K1 closure is claimed.
