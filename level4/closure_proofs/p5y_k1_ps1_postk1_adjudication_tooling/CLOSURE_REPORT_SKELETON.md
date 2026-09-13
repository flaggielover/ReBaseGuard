# P5Y K1 closure report — SKELETON (not a report; nothing below is a finding)

> Status: TEMPLATE. Produced before any genuine PS1 cell was finalized and before the
> CUSUM Aux4 rerun. The producer may not self-award `K1_CLOSED` (binding campaign
> CHECKPOINT §18). Every `{{…}}` is filled mechanically from a named artefact. Sections
> marked **ADJUDICATOR** are written by the independent adjudicator only. The frozen verdict
> taxonomy (§25) is the only admissible vocabulary.

## 0. Identity and ancestry  (mechanical)
- checkpoint anchor / hash: `{{checkpoint_sha256}}`; PS1 partition anchor `9bfe3a71…`
- production authorization sha256: `{{production_authorization_sha256}}`; producer commit `{{producer_commit}}`
- operational contract (generation, sha256): `{{generation}}`, `{{contract_sha256}}`
- gen2 lineage reachable from the canonical remote: `{{YES|NO}}`  (DAG node OP.5)

## 1. SR cover integrity: PS1, 369 cells  (mechanical; `ADJUDICATION_AUDIT.json`)
| item | value | source key |
|---|---|---|
| sealed ∧ ledger-completed cells | `{{A_completeness.sealed_and_ledger}}` / 369 | A |
| sealed file ≡ ledger record | `{{B_reconciliation.sealed_equal_ledger}}` | B |
| evidence files re-hash | `{{C_scientific_hash.evidence_ok_cells}}` | C |
| scientific_content_hash recomputed | `{{C_scientific_hash.scientific_hash_consistent_cells}}` | C |
| open reservations / unsettled runs | `{{D_state.open_reservations}}` / `{{D_state.unsettled_runs}}` | D |
| torn-attempt lineage (gen1 preserved, gen2) | `{{D_state.torn_attempts}}` | D |
| halt field (verbatim) | `{{D_state.halt_field_verbatim}}` | D |
| integrity issues | `{{issues}}` | all |
| INTEGRITY_READY_FOR_ADJUDICATION | `{{INTEGRITY_READY_FOR_ADJUDICATION}}` | — |

## 2. CPU-hour accounting  (mechanical; `E_accounting`)
| item | value |
|---|---|
| imported generation-1 history | 92.32 CPU-h |
| science CPU (sealed records) | `{{science_record_cpu_h}}` |
| settlement charges (torn, overhead) | `{{settlement_charges_cpu_h}}` |
| committed (AWS) / reconciles | `{{committed_cpu_h_by_role}}` / `{{reconciles}}` |
| governed charged vs cap 6,600 | `{{governed_charged_cpu_h_if_settled}}` |

## 3. CUSUM cover: Aux4, 326 cells  (mechanical, once produced)
`{{cusum_cells_certified_under_aux4_producer}}` / 326; producer identity `{{aux4_producer_identity}}`;
runtime binding and host `{{…}}`; cost cap `{{K1.f decision reference}}`.

## 4. Far-field splice  (inherited)
`SR:-1:far_field:all_m` INHERITED PASS; CUSUM far field INHERITED PASS. Re-verification: **ADJUDICATOR**.

## 5. Required artefact set (§26)  (mechanical presence check)
| artefact | present |
|---|---|
| certificates/cusum_compact_certificate.json | `{{}}` |
| certificates/SR_compact_certificate.json | `{{}}` |
| certificates/far_field_splice.json | `{{}}` |
| certificates/assembly_all_m.json | `{{}}` |
| results/cells_cusum.jsonl, results/cells_sr.jsonl | `{{}}` |
| results/cpu_ledger.json, results/budget_ledger_usage.json | `{{}}` |
| logs/run_log.jsonl, logs/shard_map.json, logs/work_conservation.json | `{{}}` |
| adjudication/ADJUDICATION_REPORT.md, adjudication/ADJUDICATION_VERDICT.json | **ADJUDICATOR** |
| FINAL_K1_VERDICT.json | **ADJUDICATOR** |

## 6. Scientific status  — **ADJUDICATOR ONLY** (unblinded audit: `--unblind`)
Left empty by construction.

## 7. Verdict  — **ADJUDICATOR ONLY**
One of: `K1_CLOSED` · `K1_FAIL_MATHEMATICAL` · `K1_FAIL_CERTIFICATE` · `K1_FAIL_GOVERNANCE` ·
`K1_CAMPAIGN_FAIL_ARCHITECTURE` · `K1_INCOMPLETE_BUDGET` · `K1_INCOMPLETE_EXTERNAL`.

## 8. Binding consequences (§17), whatever the verdict
P5 = PARTIAL and P5X = PARTIAL are not recoloured; K2–K5 remain OPEN;
`NOVELTY_STATUS = NOT_ESTABLISHED`; `LEVEL4_GLOBAL_CLOSURE = NO`.
