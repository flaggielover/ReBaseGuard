# P5Y / K5 — final K5 PARTIAL adjudication and publication closeout (CUSUM, m = 5 tail 306–309)

This is a document-only governance chain. It performs no scientific computation: Γ evaluations for cells 306, 307,
308 and 309 are 0. It adopts no cell, creates no r6, and leaves r5 as the current authoritative coverage map.

| step | artifact | state |
|---|---|---|
| protocol, frozen | `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL.md` | FROZEN (freeze commit = the commit that adds it) |
| administrative checker, frozen | `code/closeout_checks.py` | FROZEN (stdlib and git only; no campaign import) |
| pre-freeze checks | `evidence/PREFREEZE_CHECKS.json`, `evidence/SR_K5_REFS.json` | committed with the freeze |
| freeze review | `review/CLOSEOUT_FREEZE_REVIEW.md` | pending |
| final adjudication | `adjudication/K5_CUSUM_FINAL_ADJUDICATION.md` | pending (only if the freeze review is accepted) |
| adjudication review | `review/K5_ADJUDICATION_REVIEW.md` | pending |
| publication | `publication/K5_CUSUM_CLOSEOUT_STATUS.md` + additive sections (protocol §13) | pending (only if the adjudication review is accepted) |

**Foundation.**
* Route audit r1: `level4/closure_proofs/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`, commit 802be11e.
* Its review: ROUTE_AUDIT_ACCEPTED, commit 2f36352e.
* The superseded draft `level4/closure_proofs/p5y_k5_tail_route_audit/protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md`
  (4a4b1392) stays unedited.

**Reproduce the administrative checks** from the repository root:

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout/code/closeout_checks.py --phase freeze --out /tmp/checks.json
```

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout/code/closeout_checks.py --sr-refs --out /tmp/sr.json
```
