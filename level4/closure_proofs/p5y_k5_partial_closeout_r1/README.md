# P5Y / K5 — K5 PARTIAL closeout, successor R1 (CUSUM, m = 5 tail cells 306–309)

Successor of the rejected closeout freeze `08e9acd1` (review `591b4394`, CLOSEOUT_FREEZE_REJECTED), which stays
unedited in `level4/closure_proofs/p5y_k5_partial_closeout/`. Under that predecessor no adjudication, no publication
and no scientific computation occurred. This is a document-only governance chain: Γ evaluations for cells 306, 307,
308 and 309 are 0; no cell is adopted; no r6 is created; r5 stays the current authoritative coverage map.

| step | artifact | state |
|---|---|---|
| protocol, frozen | `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R1.md` | FROZEN (freeze commit = the commit that adds it) |
| administrative checker, frozen | `code/closeout_checks_r1.py` | FROZEN (stdlib + read-only git; no campaign import) |
| pre-freeze checks and cross-ref snapshot | `evidence/PREFREEZE_CHECKS_R1.json`, `evidence/XREF_SNAPSHOT_R1.json` | committed with the freeze |
| freeze review | `review/CLOSEOUT_FREEZE_REVIEW_R1.md` | pending |
| pre-adjudication re-read, final adjudication | `evidence/PREADJUDICATION_XREF_R1.json`, `adjudication/K5_CUSUM_FINAL_ADJUDICATION_R1.md` | pending (only if the freeze review is accepted) |
| adjudication review | `review/K5_ADJUDICATION_REVIEW_R1.md` | pending |
| pre-publication re-read, publication, conformance | `evidence/PREPUBLICATION_XREF_R1.json`, `publication/K5_CUSUM_CLOSEOUT_STATUS.md`, `review/PUBLICATION_CONFORMANCE_R1.md`, `evidence/PUBLICATION_CHECKS_R1.json` | pending (only if the adjudication review is accepted) |

Reproduce the administrative checks from the repository root:

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout_r1/code/closeout_checks_r1.py --phase freeze --out /tmp/checks_r1.json
```

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout_r1/code/closeout_checks_r1.py --xref --out /tmp/xref_r1.json
```
