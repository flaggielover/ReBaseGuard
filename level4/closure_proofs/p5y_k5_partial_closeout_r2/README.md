# P5Y / K5 — K5 PARTIAL closeout, successor R2 (CUSUM, m = 5 tail cells 306–309)

Second successor closeout. The rejected predecessors stay unedited:
* `level4/closure_proofs/p5y_k5_partial_closeout/` — freeze 08e9acd1, review 591b4394, CLOSEOUT_FREEZE_REJECTED;
* `level4/closure_proofs/p5y_k5_partial_closeout_r1/` — freeze dfcd8f79, review 0d275038, CLOSEOUT_FREEZE_REJECTED.

Under neither of them did an adjudication, a publication closeout or any scientific computation occur. This chain is
document-only: Γ evaluations for cells 306, 307, 308 and 309 are 0; no cell is adopted; no r6 is created; r5 stays the
current authoritative coverage map.

| step | artifact | state |
|---|---|---|
| protocol, frozen | `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R2.md` | FROZEN |
| checker and drift self-test, frozen | `code/closeout_checks_r2.py`, `code/drift_selftest_r2.py` | FROZEN (stdlib + read-only git; no campaign import) |
| rule tables, frozen | `config/REF_RULES_R2.json`, `config/WORDING_RULES_R2.json`, `config/WORDING_FIXTURES_R2.json`, `config/PUBLICATION_ALLOWLIST_R2.json` | FROZEN |
| repository-wide ref snapshot, frozen | `evidence/REF_SNAPSHOT_R2.json` | FROZEN |
| pre-freeze checks and drift self-test, frozen | `evidence/PREFREEZE_CHECKS_R2.json`, `evidence/DRIFT_SELFTEST_R2.json` | FROZEN |
| freeze review | `review/CLOSEOUT_FREEZE_REVIEW_R2.md` | pending |
| pre-adjudication gate and adjudication | `evidence/PREADJUDICATION_CHECKS_R2.json`, `evidence/PREADJUDICATION_REF_DIFF_R2.json`, `adjudication/K5_CUSUM_FINAL_ADJUDICATION_R2.md` | pending (only if the freeze review is accepted) |
| adjudication review | `review/K5_ADJUDICATION_REVIEW_R2.md` | pending |
| pre-publication gate, publication, conformance | `evidence/PREPUBLICATION_REF_DIFF_R2.json`, `publication/K5_CUSUM_CLOSEOUT_STATUS.md`, `review/PUBLICATION_CONFORMANCE_R2.md`, `evidence/PUBLICATION_CHECKS_R2.json` | pending (only if the adjudication review is accepted) |

Reproduce from the repository root:

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout_r2/code/closeout_checks_r2.py --phase freeze --out /tmp/checks_r2.json
```

```bash
python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout_r2/code/closeout_checks_r2.py --diff level4/closure_proofs/p5y_k5_partial_closeout_r2/evidence/REF_SNAPSHOT_R2.json --out /tmp/diff_r2.json
```
