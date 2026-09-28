# K5 cell-308 research campaign (prospective, closure-only)

**Charter written 2026-09-28 ~12:30Z, before any science of this campaign.**

| item | value |
|---|---|
| worktree / branch | `/Users/suzhe/ReBaseGuard-c308`, branch `p5y-k5-cell308-research`, **local only, not pushed, not merged** |
| base | `b73b9449` (final report of the cell-307 RLR campaign; contains the overnight research at `7f45e048`) |
| namespace | `level4/closure_proofs/p5y_k5_cell308_research/` (research). A formal campaign, if any route becomes FREEZE_READY, gets its own namespace. |
| target | CUSUM m = 5 cell 308, **quarantined** (`config/TARGET_QUARANTINE_308.json`) |
| objective | a legitimate prospective scientific closure `CELL308_CLOSED_UNDER_<ROUTE>`, **or** a rigorous exhaustion report (brief §33) |
| interpretation | **closure-only**: no floor r2 change, no r6, no adoption, no K5/P5Y closure, no main-branch integration, no push |

## Start state (verified by this campaign, 2026-09-28)

* Cell-307 campaign `p5y-k5-cell307-rlr-r1` at `b73b9449`: CELL307_CLOSED_UNDER_RLR (scientific closure only),
  ADJUDICATION_ACCEPTED at `f3f8d207`; consumed marker `refs/p5y-k5-cell307-rlr-r1/target-consumed` → grant
  `5390b06d`; sealed result blob `04161112` (= `refs/p5y-k5-cell307-rlr-r1/pending-result`). **Not touched here.**
* r5 coverage map unchanged (sha256 `e2197051…`, blob `f978eeb6…`): m = 5 open [306, 309]. **No r6 on any ref.**
* K1 closed (tag `p5y-k1-successor-closed` → `7d5cf02b`), K2/K3 closed (`p5y-k2-k3-closed` → `df703837`), K4 closed
  by successor (`p5y-k4-successor-closed` → `e88a2885`). K5 PARTIAL. P5Y NOT_YET_CLOSED.
* Tail state: 306 OPEN / NOT ADOPTED; 307 CLOSED_UNDER_RLR (scientific only, not adopted); **308 OPEN**; 309 OPEN.
* Floor r2 (`a15d083b`, review `3fadb422`) unchanged.
* Toolchain: stdlib Python 3.14.5 (and 3.11.15), no numpy/flint/mpmath; 6 cores, 8 GB. No remote host is contacted.

## Governance (binding)

1. **Quarantine** (`config/TARGET_QUARANTINE_308.json`): no new target-sensitive quantity for 306–309 before a grant;
   no new-route quantity on 305; no new operator quantity at drifts in [6/5, 13/5] or the mirror; Theorem-M transfer
   rules T1–T4; target proxies (incl. route factor × committed share) forbidden.
2. **History** lives only in `history/`; committed tail figures appear only in `history/` and `ledger/`
   (`code/c308_quarantine.py --scan`, two planted multi-shape controls).
3. **Ledger** `ledger/TARGET_INTEGRITY_LEDGER.jsonl`: HISTORICAL_READ / HISTORICAL_RECONSTRUCTION /
   PRUNING_FROM_COMMITTED / validation classes; Γ306/307/308/309 new evaluations must stay 0/0/0/0 before a grant.
4. **Exposure disclosure** `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`: the coordinator is not target-blind.
5. **Route selection by logical dominance only.** A formal route is the combination of every reviewed, sound
   component acting on distinct inequalities, each taken as a minimum with the committed supply; no component is
   chosen or dropped by estimated effect on 308.
6. **Negative controls** travel through the code path under test; a control that cannot fail is not a control.
7. **Agents**: briefs are pasted inline (never placeholders); no tail figure is ever put into a brief; agent output
   files are not read, committed or acted on before the agent's completion notification; explicit `git add` paths only.
8. Historical records (r5, 306 verdicts, the 307 campaign, the overnight namespace, rejected campaigns) are immutable.

## Route statuses

IDEA · THEORY_ONLY · IMPLEMENTED · VALIDATED_SYNTHETIC · VALIDATED_NON_TARGET · REVIEW_PENDING · REVIEW_ACCEPTED ·
FREEZE_READY · BLOCKED · REFUTED · DEFERRED · INVALID_RESULT_CHASING. The live registry is `registry/ROUTE_REGISTRY.md`.

## Layout

`config/` quarantine · `ledger/` integrity ledger, disclosures, incidents · `history/` committed 308 facts ·
`code/` governance tools · `recon/` start-state and historical reconstructions · `theory/` theorems ·
`streams/` research streams · `validation/` non-target evidence · `reviews/` independent reviews (verbatim) ·
`registry/` route registry · `checkpoints/` milestone handovers.
