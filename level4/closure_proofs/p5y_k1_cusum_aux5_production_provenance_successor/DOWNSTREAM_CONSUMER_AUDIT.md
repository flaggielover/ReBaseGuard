# Downstream consumer audit: who can treat a CUSUM Aux5 record as production

**Method.** I searched the repository for every reader of CUSUM cell records, CUSUM ledgers or CUSUM attestations (`aux[345]_CUSUM_`, `cusum_full_cover`, `check_cusum_attestation`, `cusum-production.integrity`, `p5y_k1_cusum_aux5`). Each consumer is classified by whether it can admit a CUSUM Aux5 record as production **without** a verified (record, envelope) pair.

## Consumers

| Consumer | Path to production status | Pair required? | Disposition |
|---|---|---|---|
| **K4 assembly**, `p5y_k2k5_postk1_audit/code/k4_assembly.py` (FROZEN; not edited) | GENUINE mode takes `--cusum-records DIR` plus `--cusum-attestation ATT`. `check_cusum_attestation` checks the attestation schema, `cells_verified == 326`, `all_scientific_hashes_verified`, a non-empty `producer_checkpoint_sha256`, and every record's `producer_identity_hash`. It does **not** read envelopes. | Via the attestation | **Gated by attestation.** The only sanctioned attestation is `prov_integrity.build_k4_attestation`, which refuses unless the integrity audit verified all 326 pairs of a COMPLETE, settled ledger. It records every (record sha, envelope sha) pair, the authorization block and the audit sha. The K4 checkpoint's integrity clause requires `producer_checkpoint_sha256` to be the FROZEN CUSUM successor checkpoint, so the adjudicator must match the **successor** checkpoint sha and re-run `prov_integrity.verify_k4_attestation`, which requires exact recomputation. A predecessor-style attestation, with no `production_provenance` section, fails that recomputation (acceptance t17). **Residual:** frozen K4 code alone would accept a hand-written attestation. The PS1 SR path has the same structure (the Lane C audit JSON is also a file), so this is a stated adjudication duty, not a code path this successor can close without editing a frozen checkpoint. |
| **K4 records directory** | K4 globs `*.json` in the records directory | Yes | `prov_integrity.export_pairs` writes `k4_records/` only for pairs that verified. The predecessor `prod_entry.py export`, which wrote raw records, is non-authoritative: its only target is the fenced predecessor root, which has no ledger (P03). |
| **K1 adjudication / closure report**, `p5y_k1_ps1_postk1_adjudication_tooling/CLOSURE_REPORT_SKELETON.md` | A template with placeholders; §3 still names the "CUSUM Aux4 rerun" and `{{aux4_producer_identity}}` | Must be | **Stale template, no code path.** The adjudicator fills §3 from the successor integrity audit (`INTEGRITY_READY_FOR_ADJUDICATION`, verified pairs 326/326, successor checkpoint and authorization). Required change for the adjudicator, recorded here: read "Aux4" as the Aux5 provenance successor, and count a cell only as a verified pair. |
| **PS1 Lane C audit**, `ps1_adjudication_audit.py` | SR only (`NS_REL = p5y_k1_ps1_production`, 369 cells) | n/a | Cannot read CUSUM records. |
| **Aux4 aggregate ledger / audit / report**, `p5y_k1_cusum_aux4_fullcover/code/{aggregate_ledger,audit4,report4}.py` | Globs `diagnostics/cells/aux4_CUSUM_*.json` in the Aux4 namespace, and requires `implementation_hash_kind == identity4.IDENTITY_KIND` (Aux4) and the Aux4 producer identity | n/a | Refuses every Aux5 record ("identity kind is not Aux4's"), and never reads the production runtime root. Immutable history. |
| **Aux3 audit / report** | Aux3 identity and namespace only | n/a | Superseded history; refuses Aux5 records by identity. |
| **Predecessor ledger tools**, `p5y_k1_cusum_aux5_production_checkpoint/code/{prod_entry,prod_ledger,k4_input_attestation}.py` | `export_bundle` and `build_integrity_attestation` consult the ledger seal only | No | **Non-authoritative (BLOCKED predecessor).** Their CLI targets only the predecessor runtime root, which is fenced on the host (DRAIN plus a BLOCKED marker; predecessor preflight NOT_READY via C13; no ledger exists). Called as a library on a successor ledger, they produce an attestation without `production_provenance`, which `verify_k4_attestation` refuses. The successor supervisor refuses any ledger not born under the authorization (`check_genesis`). |
| **Successor integrity verifier**, `prov_integrity.audit` / `export_pairs` / `build_k4_attestation` | `verify_pair` on every sealed attempt | **Yes** | The sanctioned admission path. |

## Required properties

| Property | Enforcement | Evidence |
|---|---|---|
| A raw Aux5 record never becomes production by its path alone | `verify_pair` requires the envelope, a ledger binding and an authorization-born genesis. The audit, export and attestation count only verified pairs. | t02 (record only), t15 (sealed but unbindable record never counted), t17 (legacy attestation refused) |
| A qualification record cannot acquire production status | QUALIFICATION_RECORD_REUSE before any envelope check; no ledger seal for it | t03 |
| An envelope cannot be attached to a different record | Record sha == envelope sha == ledger seal sha; the envelope is recomputed from the record | t04, t05 |
| An envelope cannot be replayed for another cell, run or checkpoint | The cell, checkpoint, authorization (run id, ledger id, countersignature) and ledger entries (genesis, reservation, running, seal) are all recomputed | t04, t07, t08, t11 |
| No retroactive authorization | Genesis state and journal entry 0 must both name the authorization; inserting the block later is refused; a ledger without it is never adopted | t09 |
| Neither object alone is disposition-bearing | Export and attestation refuse a half pair | t02 |

```text
DOWNSTREAM_CONSUMERS_REQUIRE_PAIR = YES for every code path that can admit CUSUM Aux5 production
RESIDUAL (stated, PS1-equivalent)  = frozen K4 code trusts an attestation file; the adjudicator must recompute it
                                     with prov_integrity.verify_k4_attestation against the successor checkpoint
STALE TEMPLATE                     = CLOSURE_REPORT_SKELETON.md §3 names Aux4; the adjudicator reads it as the
                                     Aux5 provenance successor (no code path)
```
